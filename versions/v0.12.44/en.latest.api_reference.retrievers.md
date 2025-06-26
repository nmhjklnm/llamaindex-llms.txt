# Index
Base retriever.
##  BaseRetriever #
Bases: `ChainableMixin`, `PromptMixin`, `DispatcherSpanMixin`
Base retriever.
Source code in `llama-index-core/llama_index/core/base/base_retriever.py`

| ```
class BaseRetriever(ChainableMixin, PromptMixin, DispatcherSpanMixin):
    """Base retriever."""

    def __init__(
        self,
        callback_manager: Optional[CallbackManager] = None,
        object_map: Optional[Dict] = None,
        objects: Optional[List[IndexNode]] = None,
        verbose: bool = False,
    ) -> None:
        self.callback_manager = callback_manager or CallbackManager()

        if objects is not None:
            object_map = {obj.index_id: obj.obj for obj in objects}

        self.object_map = object_map or {}
        self._verbose = verbose

    def _check_callback_manager(self) -> None:
        """Check callback manager."""
        if not hasattr(self, "callback_manager"):
            self.callback_manager = Settings.callback_manager

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {}

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt modules."""
        return {}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""

    def _retrieve_from_object(
        self,
        obj: Any,
        query_bundle: QueryBundle,
        score: float,
    ) -> List[NodeWithScore]:
        """Retrieve nodes from object."""
        if self._verbose:
            print_text(
                f"Retrieving from object {obj.__class__.__name__} with query {query_bundle.query_str}\n",
                color="llama_pink",
            )
        if isinstance(obj, NodeWithScore):
            return [obj]
        elif isinstance(obj, BaseNode):
            return [NodeWithScore(node=obj, score=score)]
        elif isinstance(obj, BaseQueryEngine):
            response = obj.query(query_bundle)
            return [
                NodeWithScore(
                    node=TextNode(text=str(response), metadata=response.metadata or {}),
                    score=score,
                )
            ]
        elif isinstance(obj, BaseRetriever):
            return obj.retrieve(query_bundle)
        elif isinstance(obj, QueryComponent):
            component_keys = obj.input_keys.required_keys
            if len(component_keys) > 1:
                raise ValueError(
                    f"QueryComponent {obj} has more than one input key: {component_keys}"
                )
            elif len(component_keys) == 0:
                component_response = obj.run_component()
            else:
                kwargs = {next(iter(component_keys)): query_bundle.query_str}
                component_response = obj.run_component(**kwargs)

            result_output = str(next(iter(component_response.values())))
            return [NodeWithScore(node=TextNode(text=result_output), score=score)]
        else:
            raise ValueError(f"Object {obj} is not retrievable.")

    async def _aretrieve_from_object(
        self,
        obj: Any,
        query_bundle: QueryBundle,
        score: float,
    ) -> List[NodeWithScore]:
        """Retrieve nodes from object."""
        if isinstance(obj, NodeWithScore):
            return [obj]
        elif isinstance(obj, BaseNode):
            return [NodeWithScore(node=obj, score=score)]
        elif isinstance(obj, BaseQueryEngine):
            response = await obj.aquery(query_bundle)
            return [NodeWithScore(node=TextNode(text=str(response)), score=score)]
        elif isinstance(obj, BaseRetriever):
            return await obj.aretrieve(query_bundle)
        elif isinstance(obj, QueryComponent):
            component_keys = obj.input_keys.required_keys
            if len(component_keys) > 1:
                raise ValueError(
                    f"QueryComponent {obj} has more than one input key: {component_keys}"
                )
            elif len(component_keys) == 0:
                component_response = await obj.arun_component()
            else:
                kwargs = {next(iter(component_keys)): query_bundle.query_str}
                component_response = await obj.arun_component(**kwargs)

            result_output = str(next(iter(component_response.values())))
            return [NodeWithScore(node=TextNode(text=result_output), score=score)]
        else:
            raise ValueError(f"Object {obj} is not retrievable.")

    def _handle_recursive_retrieval(
        self, query_bundle: QueryBundle, nodes: List[NodeWithScore]
    ) -> List[NodeWithScore]:
        retrieved_nodes: List[NodeWithScore] = []
        for n in nodes:
            node = n.node
            score = n.score or 1.0
            if isinstance(node, IndexNode):
                obj = node.obj or self.object_map.get(node.index_id, None)
                if obj is not None:
                    if self._verbose:
                        print_text(
                            f"Retrieval entering {node.index_id}: {obj.__class__.__name__}\n",
                            color="llama_turquoise",
                        )
                    retrieved_nodes.extend(
                        self._retrieve_from_object(
                            obj, query_bundle=query_bundle, score=score
                        )
                    )
                else:
                    retrieved_nodes.append(n)
            else:
                retrieved_nodes.append(n)

        seen = set()
        return [
            n
            for n in retrieved_nodes
            if not (n.node.hash in seen or seen.add(n.node.hash))  # type: ignore[func-returns-value]
        ]

    async def _ahandle_recursive_retrieval(
        self, query_bundle: QueryBundle, nodes: List[NodeWithScore]
    ) -> List[NodeWithScore]:
        retrieved_nodes: List[NodeWithScore] = []
        for n in nodes:
            node = n.node
            score = n.score or 1.0
            if isinstance(node, IndexNode):
                obj = node.obj or self.object_map.get(node.index_id, None)
                if obj is not None:
                    if self._verbose:
                        print_text(
                            f"Retrieval entering {node.index_id}: {obj.__class__.__name__}\n",
                            color="llama_turquoise",
                        )
                    # TODO: Add concurrent execution via `run_jobs()` ?
                    retrieved_nodes.extend(
                        await self._aretrieve_from_object(
                            obj, query_bundle=query_bundle, score=score
                        )
                    )
                else:
                    retrieved_nodes.append(n)
            else:
                retrieved_nodes.append(n)

        # remove any duplicates based on hash and ref_doc_id
        seen = set()
        return [
            n
            for n in retrieved_nodes
            if not (
                (n.node.hash, n.node.ref_doc_id) in seen
                or seen.add((n.node.hash, n.node.ref_doc_id))  # type: ignore[func-returns-value]
            )
        ]

    @dispatcher.span
    def retrieve(self, str_or_query_bundle: QueryType) -> List[NodeWithScore]:
        """
        Retrieve nodes given query.

        Args:
            str_or_query_bundle (QueryType): Either a query string or
                a QueryBundle object.

        """
        self._check_callback_manager()
        dispatcher.event(
            RetrievalStartEvent(
                str_or_query_bundle=str_or_query_bundle,
            )
        )
        if isinstance(str_or_query_bundle, str):
            query_bundle = QueryBundle(str_or_query_bundle)
        else:
            query_bundle = str_or_query_bundle
        with self.callback_manager.as_trace("query"):
            with self.callback_manager.event(
                CBEventType.RETRIEVE,
                payload={EventPayload.QUERY_STR: query_bundle.query_str},
            ) as retrieve_event:
                nodes = self._retrieve(query_bundle)
                nodes = self._handle_recursive_retrieval(query_bundle, nodes)
                retrieve_event.on_end(
                    payload={EventPayload.NODES: nodes},
                )
        dispatcher.event(
            RetrievalEndEvent(
                str_or_query_bundle=str_or_query_bundle,
                nodes=nodes,
            )
        )
        return nodes

    @dispatcher.span
    async def aretrieve(self, str_or_query_bundle: QueryType) -> List[NodeWithScore]:
        self._check_callback_manager()

        dispatcher.event(
            RetrievalStartEvent(
                str_or_query_bundle=str_or_query_bundle,
            )
        )
        if isinstance(str_or_query_bundle, str):
            query_bundle = QueryBundle(str_or_query_bundle)
        else:
            query_bundle = str_or_query_bundle
        with self.callback_manager.as_trace("query"):
            with self.callback_manager.event(
                CBEventType.RETRIEVE,
                payload={EventPayload.QUERY_STR: query_bundle.query_str},
            ) as retrieve_event:
                nodes = await self._aretrieve(query_bundle=query_bundle)
                nodes = await self._ahandle_recursive_retrieval(
                    query_bundle=query_bundle, nodes=nodes
                )
                retrieve_event.on_end(
                    payload={EventPayload.NODES: nodes},
                )
        dispatcher.event(
            RetrievalEndEvent(
                str_or_query_bundle=str_or_query_bundle,
                nodes=nodes,
            )
        )
        return nodes

    @abstractmethod
    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """
        Retrieve nodes given query.

        Implemented by the user.

        """

    # TODO: make this abstract
    # @abstractmethod
    async def _aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """
        Asynchronously retrieve nodes given query.

        Implemented by the user.

        """
        return self._retrieve(query_bundle)

    def _as_query_component(self, **kwargs: Any) -> QueryComponent:
        """Return a query component."""
        return RetrieverComponent(retriever=self)

```
  
---|---  
###  retrieve #
```
retrieve(str_or_query_bundle: QueryType) -> List[NodeWithScore]

```

Retrieve nodes given query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`str_or_query_bundle` |  `QueryType` |  Either a query string or a QueryBundle object. |  _required_  
Source code in `llama-index-core/llama_index/core/base/base_retriever.py`

| ```
@dispatcher.span
def retrieve(self, str_or_query_bundle: QueryType) -> List[NodeWithScore]:
    """
    Retrieve nodes given query.

    Args:
        str_or_query_bundle (QueryType): Either a query string or
            a QueryBundle object.

    """
    self._check_callback_manager()
    dispatcher.event(
        RetrievalStartEvent(
            str_or_query_bundle=str_or_query_bundle,
        )
    )
    if isinstance(str_or_query_bundle, str):
        query_bundle = QueryBundle(str_or_query_bundle)
    else:
        query_bundle = str_or_query_bundle
    with self.callback_manager.as_trace("query"):
        with self.callback_manager.event(
            CBEventType.RETRIEVE,
            payload={EventPayload.QUERY_STR: query_bundle.query_str},
        ) as retrieve_event:
            nodes = self._retrieve(query_bundle)
            nodes = self._handle_recursive_retrieval(query_bundle, nodes)
            retrieve_event.on_end(
                payload={EventPayload.NODES: nodes},
            )
    dispatcher.event(
        RetrievalEndEvent(
            str_or_query_bundle=str_or_query_bundle,
            nodes=nodes,
        )
    )
    return nodes

```
  
---|---  
##  BaseImageRetriever #
Bases: `PromptMixin`, `DispatcherSpanMixin`
Base Image Retriever Abstraction.
Source code in `llama-index-core/llama_index/core/image_retriever.py`

| ```
class BaseImageRetriever(PromptMixin, DispatcherSpanMixin):
    """Base Image Retriever Abstraction."""

    def text_to_image_retrieve(
        self, str_or_query_bundle: QueryType
    ) -> List[NodeWithScore]:
        """
        Retrieve image nodes given query or single image input.

        Args:
            str_or_query_bundle (QueryType): a query text
            string or a QueryBundle object.

        """
        if isinstance(str_or_query_bundle, str):
            str_or_query_bundle = QueryBundle(query_str=str_or_query_bundle)
        return self._text_to_image_retrieve(str_or_query_bundle)

    @abstractmethod
    def _text_to_image_retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        """
        Retrieve image nodes or documents given query text.

        Implemented by the user.

        """

    def image_to_image_retrieve(
        self, str_or_query_bundle: QueryType
    ) -> List[NodeWithScore]:
        """
        Retrieve image nodes given single image input.

        Args:
            str_or_query_bundle (QueryType): a image path
            string or a QueryBundle object.

        """
        if isinstance(str_or_query_bundle, str):
            # leave query_str as empty since we are using image_path for image retrieval
            str_or_query_bundle = QueryBundle(
                query_str="", image_path=str_or_query_bundle
            )
        return self._image_to_image_retrieve(str_or_query_bundle)

    @abstractmethod
    def _image_to_image_retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        """
        Retrieve image nodes or documents given image.

        Implemented by the user.

        """

    # Async Methods
    async def atext_to_image_retrieve(
        self,
        str_or_query_bundle: QueryType,
    ) -> List[NodeWithScore]:
        if isinstance(str_or_query_bundle, str):
            str_or_query_bundle = QueryBundle(query_str=str_or_query_bundle)
        return await self._atext_to_image_retrieve(str_or_query_bundle)

    @abstractmethod
    async def _atext_to_image_retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        """
        Async retrieve image nodes or documents given query text.

        Implemented by the user.

        """

    async def aimage_to_image_retrieve(
        self,
        str_or_query_bundle: QueryType,
    ) -> List[NodeWithScore]:
        if isinstance(str_or_query_bundle, str):
            # leave query_str as empty since we are using image_path for image retrieval
            str_or_query_bundle = QueryBundle(
                query_str="", image_path=str_or_query_bundle
            )
        return await self._aimage_to_image_retrieve(str_or_query_bundle)

    @abstractmethod
    async def _aimage_to_image_retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        """
        Async retrieve image nodes or documents given image.

        Implemented by the user.

        """

```
  
---|---  
###  text_to_image_retrieve #
```
text_to_image_retrieve(str_or_query_bundle: QueryType) -> List[NodeWithScore]

```

Retrieve image nodes given query or single image input.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`str_or_query_bundle` |  `QueryType` |  a query text |  _required_  
Source code in `llama-index-core/llama_index/core/image_retriever.py`

| ```
def text_to_image_retrieve(
    self, str_or_query_bundle: QueryType
) -> List[NodeWithScore]:
    """
    Retrieve image nodes given query or single image input.

    Args:
        str_or_query_bundle (QueryType): a query text
        string or a QueryBundle object.

    """
    if isinstance(str_or_query_bundle, str):
        str_or_query_bundle = QueryBundle(query_str=str_or_query_bundle)
    return self._text_to_image_retrieve(str_or_query_bundle)

```
  
---|---  
###  image_to_image_retrieve #
```
image_to_image_retrieve(str_or_query_bundle: QueryType) -> List[NodeWithScore]

```

Retrieve image nodes given single image input.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`str_or_query_bundle` |  `QueryType` |  a image path |  _required_  
Source code in `llama-index-core/llama_index/core/image_retriever.py`

| ```
def image_to_image_retrieve(
    self, str_or_query_bundle: QueryType
) -> List[NodeWithScore]:
    """
    Retrieve image nodes given single image input.

    Args:
        str_or_query_bundle (QueryType): a image path
        string or a QueryBundle object.

    """
    if isinstance(str_or_query_bundle, str):
        # leave query_str as empty since we are using image_path for image retrieval
        str_or_query_bundle = QueryBundle(
            query_str="", image_path=str_or_query_bundle
        )
    return self._image_to_image_retrieve(str_or_query_bundle)

```
  
---|---
