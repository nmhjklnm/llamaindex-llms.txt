# Index
Base index classes.
##  BaseIndex #
Bases: `Generic[IS]`, `ABC`
Base LlamaIndex.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[Node]` |  List of nodes to index |  `None`  
`show_progress` |  `bool` |  Whether to show tqdm progress bars. Defaults to False. |  `False`  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
class BaseIndex(Generic[IS], ABC):
    """
    Base LlamaIndex.

    Args:
        nodes (List[Node]): List of nodes to index
        show_progress (bool): Whether to show tqdm progress bars. Defaults to False.

    """

    index_struct_cls: Type[IS]

    def __init__(
        self,
        nodes: Optional[Sequence[BaseNode]] = None,
        objects: Optional[Sequence[IndexNode]] = None,
        index_struct: Optional[IS] = None,
        storage_context: Optional[StorageContext] = None,
        callback_manager: Optional[CallbackManager] = None,
        transformations: Optional[List[TransformComponent]] = None,
        show_progress: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize with parameters."""
        if index_struct is None and nodes is None and objects is None:
            raise ValueError("One of nodes, objects, or index_struct must be provided.")
        if index_struct is not None and nodes is not None and len(nodes) >= 1:
            raise ValueError("Only one of nodes or index_struct can be provided.")
        # This is to explicitly make sure that the old UX is not used
        if nodes is not None and len(nodes) >= 1 and not isinstance(nodes[0], BaseNode):
            if isinstance(nodes[0], Document):
                raise ValueError(
                    "The constructor now takes in a list of Node objects. "
                    "Since you are passing in a list of Document objects, "
                    "please use `from_documents` instead."
                )
            else:
                raise ValueError("nodes must be a list of Node objects.")

        self._storage_context = storage_context or StorageContext.from_defaults()
        self._docstore = self._storage_context.docstore
        self._show_progress = show_progress
        self._vector_store = self._storage_context.vector_store
        self._graph_store = self._storage_context.graph_store
        self._callback_manager = callback_manager or Settings.callback_manager

        objects = objects or []
        self._object_map = {obj.index_id: obj.obj for obj in objects}
        for obj in objects:
            obj.obj = None  # clear the object to avoid serialization issues

        with self._callback_manager.as_trace("index_construction"):
            if index_struct is None:
                nodes = nodes or []
                index_struct = self.build_index_from_nodes(
                    nodes + objects,  # type: ignore
                    **kwargs,  # type: ignore
                )
            self._index_struct = index_struct
            self._storage_context.index_store.add_index_struct(self._index_struct)

        self._transformations = transformations or Settings.transformations

    @classmethod
    def from_documents(
        cls: Type[IndexType],
        documents: Sequence[Document],
        storage_context: Optional[StorageContext] = None,
        show_progress: bool = False,
        callback_manager: Optional[CallbackManager] = None,
        transformations: Optional[List[TransformComponent]] = None,
        **kwargs: Any,
    ) -> IndexType:
        """
        Create index from documents.

        Args:
            documents (Sequence[Document]]): List of documents to
                build the index from.

        """
        storage_context = storage_context or StorageContext.from_defaults()
        docstore = storage_context.docstore
        callback_manager = callback_manager or Settings.callback_manager
        transformations = transformations or Settings.transformations

        with callback_manager.as_trace("index_construction"):
            for doc in documents:
                docstore.set_document_hash(doc.id_, doc.hash)

            nodes = run_transformations(
                documents,  # type: ignore
                transformations,
                show_progress=show_progress,
                **kwargs,
            )

            return cls(
                nodes=nodes,
                storage_context=storage_context,
                callback_manager=callback_manager,
                show_progress=show_progress,
                transformations=transformations,
                **kwargs,
            )

    @property
    def index_struct(self) -> IS:
        """Get the index struct."""
        return self._index_struct

    @property
    def index_id(self) -> str:
        """Get the index struct."""
        return self._index_struct.index_id

    def set_index_id(self, index_id: str) -> None:
        """
        Set the index id.

        NOTE: if you decide to set the index_id on the index_struct manually,
        you will need to explicitly call `add_index_struct` on the `index_store`
        to update the index store.

        Args:
            index_id (str): Index id to set.

        """
        # delete the old index struct
        old_id = self._index_struct.index_id
        self._storage_context.index_store.delete_index_struct(old_id)
        # add the new index struct
        self._index_struct.index_id = index_id
        self._storage_context.index_store.add_index_struct(self._index_struct)

    @property
    def docstore(self) -> BaseDocumentStore:
        """Get the docstore corresponding to the index."""
        return self._docstore

    @property
    def storage_context(self) -> StorageContext:
        return self._storage_context

    @property
    def summary(self) -> str:
        return str(self._index_struct.summary)

    @summary.setter
    def summary(self, new_summary: str) -> None:
        self._index_struct.summary = new_summary
        self._storage_context.index_store.add_index_struct(self._index_struct)

    @abstractmethod
    def _build_index_from_nodes(
        self, nodes: Sequence[BaseNode], **build_kwargs: Any
    ) -> IS:
        """Build the index from nodes."""

    def build_index_from_nodes(
        self, nodes: Sequence[BaseNode], **build_kwargs: Any
    ) -> IS:
        """Build the index from nodes."""
        self._docstore.add_documents(nodes, allow_update=True)
        return self._build_index_from_nodes(nodes, **build_kwargs)

    @abstractmethod
    def _insert(self, nodes: Sequence[BaseNode], **insert_kwargs: Any) -> None:
        """Index-specific logic for inserting nodes to the index struct."""

    def insert_nodes(self, nodes: Sequence[BaseNode], **insert_kwargs: Any) -> None:
        """Insert nodes."""
        for node in nodes:
            if isinstance(node, IndexNode):
                try:
                    node.dict()
                except ValueError:
                    self._object_map[node.index_id] = node.obj
                    node.obj = None

        with self._callback_manager.as_trace("insert_nodes"):
            self.docstore.add_documents(nodes, allow_update=True)
            self._insert(nodes, **insert_kwargs)
            self._storage_context.index_store.add_index_struct(self._index_struct)

    async def ainsert_nodes(
        self, nodes: Sequence[BaseNode], **insert_kwargs: Any
    ) -> None:
        """Asynchronously insert nodes."""
        for node in nodes:
            if isinstance(node, IndexNode):
                try:
                    node.dict()
                except ValueError:
                    self._object_map[node.index_id] = node.obj
                    node.obj = None

        with self._callback_manager.as_trace("ainsert_nodes"):
            await self.docstore.async_add_documents(nodes, allow_update=True)
            self._insert(nodes=nodes)
            await self._storage_context.index_store.async_add_index_struct(
                self._index_struct
            )

    def insert(self, document: Document, **insert_kwargs: Any) -> None:
        """Insert a document."""
        with self._callback_manager.as_trace("insert"):
            nodes = run_transformations(
                [document],
                self._transformations,
                show_progress=self._show_progress,
                **insert_kwargs,
            )

            self.insert_nodes(nodes, **insert_kwargs)
            self.docstore.set_document_hash(document.get_doc_id(), document.hash)

    async def ainsert(self, document: Document, **insert_kwargs: Any) -> None:
        """Asynchronously insert a document."""
        with self._callback_manager.as_trace("ainsert"):
            nodes = await arun_transformations(
                [document],
                self._transformations,
                show_progress=self._show_progress,
                **insert_kwargs,
            )

            await self.ainsert_nodes(nodes, **insert_kwargs)
            await self.docstore.aset_document_hash(document.get_doc_id(), document.hash)

    @abstractmethod
    def _delete_node(self, node_id: str, **delete_kwargs: Any) -> None:
        """Delete a node."""

    def delete_nodes(
        self,
        node_ids: List[str],
        delete_from_docstore: bool = False,
        **delete_kwargs: Any,
    ) -> None:
        """
        Delete a list of nodes from the index.

        Args:
            doc_ids (List[str]): A list of doc_ids from the nodes to delete

        """
        for node_id in node_ids:
            self._delete_node(node_id, **delete_kwargs)
            if delete_from_docstore:
                self.docstore.delete_document(node_id, raise_error=False)

        self._storage_context.index_store.add_index_struct(self._index_struct)

    async def adelete_nodes(
        self,
        node_ids: List[str],
        delete_from_docstore: bool = False,
        **delete_kwargs: Any,
    ) -> None:
        """
        Asynchronously delete a list of nodes from the index.

        Args:
            doc_ids (List[str]): A list of doc_ids from the nodes to delete

        """
        for node_id in node_ids:
            self._delete_node(node_id, **delete_kwargs)
            if delete_from_docstore:
                await self.docstore.adelete_document(node_id, raise_error=False)

        await self._storage_context.index_store.async_add_index_struct(
            self._index_struct
        )

    def delete(self, doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete a document from the index.
        All nodes in the index related to the index will be deleted.

        Args:
            doc_id (str): A doc_id of the ingested document

        """
        logger.warning(
            "delete() is now deprecated, please refer to delete_ref_doc() to delete "
            "ingested documents+nodes or delete_nodes to delete a list of nodes."
            "Use adelete_ref_docs() for an asynchronous implementation"
        )
        self.delete_ref_doc(doc_id)

    def delete_ref_doc(
        self, ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any
    ) -> None:
        """Delete a document and it's nodes by using ref_doc_id."""
        ref_doc_info = self.docstore.get_ref_doc_info(ref_doc_id)
        if ref_doc_info is None:
            logger.warning(f"ref_doc_id {ref_doc_id} not found, nothing deleted.")
            return

        self.delete_nodes(
            ref_doc_info.node_ids,
            delete_from_docstore=False,
            **delete_kwargs,
        )

        if delete_from_docstore:
            self.docstore.delete_ref_doc(ref_doc_id, raise_error=False)

    async def adelete_ref_doc(
        self, ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any
    ) -> None:
        """Delete a document and it's nodes by using ref_doc_id."""
        ref_doc_info = await self.docstore.aget_ref_doc_info(ref_doc_id)
        if ref_doc_info is None:
            logger.warning(f"ref_doc_id {ref_doc_id} not found, nothing deleted.")
            return

        await self.adelete_nodes(
            ref_doc_info.node_ids,
            delete_from_docstore=False,
            **delete_kwargs,
        )

        if delete_from_docstore:
            await self.docstore.adelete_ref_doc(ref_doc_id, raise_error=False)

    def update(self, document: Document, **update_kwargs: Any) -> None:
        """
        Update a document and it's corresponding nodes.

        This is equivalent to deleting the document and then inserting it again.

        Args:
            document (Union[BaseDocument, BaseIndex]): document to update
            insert_kwargs (Dict): kwargs to pass to insert
            delete_kwargs (Dict): kwargs to pass to delete

        """
        logger.warning(
            "update() is now deprecated, please refer to update_ref_doc() to update "
            "ingested documents+nodes."
            "Use aupdate_ref_docs() for an asynchronous implementation"
        )
        self.update_ref_doc(document, **update_kwargs)

    def update_ref_doc(self, document: Document, **update_kwargs: Any) -> None:
        """
        Update a document and it's corresponding nodes.

        This is equivalent to deleting the document and then inserting it again.

        Args:
            document (Union[BaseDocument, BaseIndex]): document to update
            insert_kwargs (Dict): kwargs to pass to insert
            delete_kwargs (Dict): kwargs to pass to delete

        """
        with self._callback_manager.as_trace("update_ref_doc"):
            self.delete_ref_doc(
                document.get_doc_id(),
                delete_from_docstore=True,
                **update_kwargs.pop("delete_kwargs", {}),
            )
            self.insert(document, **update_kwargs.pop("insert_kwargs", {}))

    async def aupdate_ref_doc(self, document: Document, **update_kwargs: Any) -> None:
        """
        Asynchronously update a document and it's corresponding nodes.

        This is equivalent to deleting the document and then inserting it again.

        Args:
            document (Union[BaseDocument, BaseIndex]): document to update
            insert_kwargs (Dict): kwargs to pass to insert
            delete_kwargs (Dict): kwargs to pass to delete

        """
        with self._callback_manager.as_trace("aupdate_ref_doc"):
            await self.adelete_ref_doc(
                document.get_doc_id(),
                delete_from_docstore=True,
                **update_kwargs.pop("delete_kwargs", {}),
            )
            await self.ainsert(document, **update_kwargs.pop("insert_kwargs", {}))

    def refresh(
        self, documents: Sequence[Document], **update_kwargs: Any
    ) -> List[bool]:
        """
        Refresh an index with documents that have changed.

        This allows users to save LLM and Embedding model calls, while only
        updating documents that have any changes in text or metadata. It
        will also insert any documents that previously were not stored.
        """
        logger.warning(
            "refresh() is now deprecated, please refer to refresh_ref_docs() to "
            "refresh ingested documents+nodes with an updated list of documents."
            "Use arefresh_ref_docs() for an asynchronous implementation"
        )
        return self.refresh_ref_docs(documents, **update_kwargs)

    def refresh_ref_docs(
        self, documents: Sequence[Document], **update_kwargs: Any
    ) -> List[bool]:
        """
        Refresh an index with documents that have changed.

        This allows users to save LLM and Embedding model calls, while only
        updating documents that have any changes in text or metadata. It
        will also insert any documents that previously were not stored.
        """
        with self._callback_manager.as_trace("refresh_ref_docs"):
            refreshed_documents = [False] * len(documents)
            for i, document in enumerate(documents):
                existing_doc_hash = self._docstore.get_document_hash(
                    document.get_doc_id()
                )
                if existing_doc_hash is None:
                    self.insert(document, **update_kwargs.pop("insert_kwargs", {}))
                    refreshed_documents[i] = True
                elif existing_doc_hash != document.hash:
                    self.update_ref_doc(
                        document, **update_kwargs.pop("update_kwargs", {})
                    )
                    refreshed_documents[i] = True

            return refreshed_documents

    async def arefresh_ref_docs(
        self, documents: Sequence[Document], **update_kwargs: Any
    ) -> List[bool]:
        """
        Asynchronously refresh an index with documents that have changed.

        This allows users to save LLM and Embedding model calls, while only
        updating documents that have any changes in text or metadata. It
        will also insert any documents that previously were not stored.
        """
        with self._callback_manager.as_trace("arefresh_ref_docs"):
            refreshed_documents = [False] * len(documents)
            for i, document in enumerate(documents):
                existing_doc_hash = await self._docstore.aget_document_hash(
                    document.get_doc_id()
                )
                if existing_doc_hash is None:
                    await self.ainsert(
                        document, **update_kwargs.pop("insert_kwargs", {})
                    )
                    refreshed_documents[i] = True
                elif existing_doc_hash != document.hash:
                    await self.aupdate_ref_doc(
                        document, **update_kwargs.pop("update_kwargs", {})
                    )
                    refreshed_documents[i] = True
            return refreshed_documents

    @property
    @abstractmethod
    def ref_doc_info(self) -> Dict[str, RefDocInfo]:
        """Retrieve a dict mapping of ingested documents and their nodes+metadata."""
        ...

    @abstractmethod
    def as_retriever(self, **kwargs: Any) -> BaseRetriever: ...

    def as_query_engine(
        self, llm: Optional[LLMType] = None, **kwargs: Any
    ) -> BaseQueryEngine:
        """
        Convert the index to a query engine.

        Calls `index.as_retriever(**kwargs)` to get the retriever and then wraps it in a
        `RetrieverQueryEngine.from_args(retriever, **kwrags)` call.
        """
        # NOTE: lazy import
        from llama_index.core.query_engine.retriever_query_engine import (
            RetrieverQueryEngine,
        )

        retriever = self.as_retriever(**kwargs)
        llm = (
            resolve_llm(llm, callback_manager=self._callback_manager)
            if llm
            else Settings.llm
        )

        return RetrieverQueryEngine.from_args(
            retriever,
            llm=llm,
            **kwargs,
        )

    def as_chat_engine(
        self,
        chat_mode: ChatMode = ChatMode.BEST,
        llm: Optional[LLMType] = None,
        **kwargs: Any,
    ) -> BaseChatEngine:
        """
        Convert the index to a chat engine.

        Calls `index.as_query_engine(llm=llm, **kwargs)` to get the query engine and then
        wraps it in a chat engine based on the chat mode.

        Chat modes:
            - `ChatMode.BEST` (default): Chat engine that uses an agent (react or openai) with a query engine tool
            - `ChatMode.CONTEXT`: Chat engine that uses a retriever to get context
            - `ChatMode.CONDENSE_QUESTION`: Chat engine that condenses questions
            - `ChatMode.CONDENSE_PLUS_CONTEXT`: Chat engine that condenses questions and uses a retriever to get context
            - `ChatMode.SIMPLE`: Simple chat engine that uses the LLM directly
            - `ChatMode.REACT`: Chat engine that uses a react agent with a query engine tool
            - `ChatMode.OPENAI`: Chat engine that uses an openai agent with a query engine tool
        """
        llm = (
            resolve_llm(llm, callback_manager=self._callback_manager)
            if llm
            else Settings.llm
        )

        query_engine = self.as_query_engine(llm=llm, **kwargs)

        # resolve chat mode
        if chat_mode in [ChatMode.REACT, ChatMode.OPENAI]:
            raise ValueError(
                "ChatMode.REACT and ChatMode.OPENAI are now deprecated and removed. "
                "Please use the ReActAgent or FunctionAgent classes from llama_index.core.agent.workflow "
                "to create an agent with a query engine tool."
            )

        if chat_mode == ChatMode.CONDENSE_QUESTION:
            # NOTE: lazy import
            from llama_index.core.chat_engine import CondenseQuestionChatEngine

            return CondenseQuestionChatEngine.from_defaults(
                query_engine=query_engine,
                llm=llm,
                **kwargs,
            )

        elif chat_mode == ChatMode.CONTEXT:
            from llama_index.core.chat_engine import ContextChatEngine

            return ContextChatEngine.from_defaults(
                retriever=self.as_retriever(**kwargs),
                llm=llm,
                **kwargs,
            )

        elif chat_mode in [ChatMode.CONDENSE_PLUS_CONTEXT, ChatMode.BEST]:
            from llama_index.core.chat_engine import CondensePlusContextChatEngine

            return CondensePlusContextChatEngine.from_defaults(
                retriever=self.as_retriever(**kwargs),
                llm=llm,
                **kwargs,
            )

        elif chat_mode == ChatMode.SIMPLE:
            from llama_index.core.chat_engine import SimpleChatEngine

            return SimpleChatEngine.from_defaults(
                llm=llm,
                **kwargs,
            )
        else:
            raise ValueError(f"Unknown chat mode: {chat_mode}")

```
  
---|---  
###  index_struct `property` #
```
index_struct: IS

```

Get the index struct.
###  index_id `property` #
```
index_id: str

```

Get the index struct.
###  docstore `property` #
```
docstore: BaseDocumentStore

```

Get the docstore corresponding to the index.
###  ref_doc_info `abstractmethod` `property` #
```
ref_doc_info: Dict[str, RefDocInfo]

```

Retrieve a dict mapping of ingested documents and their nodes+metadata.
###  from_documents `classmethod` #
```
from_documents(documents: Sequence[Document], storage_context: Optional[StorageContext] = None, show_progress: bool = False, callback_manager: Optional[CallbackManager] = None, transformations: Optional[List[TransformComponent]] = None, **kwargs: Any) -> IndexType

```

Create index from documents.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`documents` |  `Sequence[Document]]` |  List of documents to build the index from. |  _required_  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
@classmethod
def from_documents(
    cls: Type[IndexType],
    documents: Sequence[Document],
    storage_context: Optional[StorageContext] = None,
    show_progress: bool = False,
    callback_manager: Optional[CallbackManager] = None,
    transformations: Optional[List[TransformComponent]] = None,
    **kwargs: Any,
) -> IndexType:
    """
    Create index from documents.

    Args:
        documents (Sequence[Document]]): List of documents to
            build the index from.

    """
    storage_context = storage_context or StorageContext.from_defaults()
    docstore = storage_context.docstore
    callback_manager = callback_manager or Settings.callback_manager
    transformations = transformations or Settings.transformations

    with callback_manager.as_trace("index_construction"):
        for doc in documents:
            docstore.set_document_hash(doc.id_, doc.hash)

        nodes = run_transformations(
            documents,  # type: ignore
            transformations,
            show_progress=show_progress,
            **kwargs,
        )

        return cls(
            nodes=nodes,
            storage_context=storage_context,
            callback_manager=callback_manager,
            show_progress=show_progress,
            transformations=transformations,
            **kwargs,
        )

```
  
---|---  
###  set_index_id #
```
set_index_id(index_id: str) -> None

```

Set the index id.
NOTE: if you decide to set the index_id on the index_struct manually, you will need to explicitly call `add_index_struct` on the `index_store` to update the index store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`index_id` |  `str` |  Index id to set. |  _required_  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def set_index_id(self, index_id: str) -> None:
    """
    Set the index id.

    NOTE: if you decide to set the index_id on the index_struct manually,
    you will need to explicitly call `add_index_struct` on the `index_store`
    to update the index store.

    Args:
        index_id (str): Index id to set.

    """
    # delete the old index struct
    old_id = self._index_struct.index_id
    self._storage_context.index_store.delete_index_struct(old_id)
    # add the new index struct
    self._index_struct.index_id = index_id
    self._storage_context.index_store.add_index_struct(self._index_struct)

```
  
---|---  
###  build_index_from_nodes #
```
build_index_from_nodes(nodes: Sequence[BaseNode], **build_kwargs: Any) -> IS

```

Build the index from nodes.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def build_index_from_nodes(
    self, nodes: Sequence[BaseNode], **build_kwargs: Any
) -> IS:
    """Build the index from nodes."""
    self._docstore.add_documents(nodes, allow_update=True)
    return self._build_index_from_nodes(nodes, **build_kwargs)

```
  
---|---  
###  insert_nodes #
```
insert_nodes(nodes: Sequence[BaseNode], **insert_kwargs: Any) -> None

```

Insert nodes.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def insert_nodes(self, nodes: Sequence[BaseNode], **insert_kwargs: Any) -> None:
    """Insert nodes."""
    for node in nodes:
        if isinstance(node, IndexNode):
            try:
                node.dict()
            except ValueError:
                self._object_map[node.index_id] = node.obj
                node.obj = None

    with self._callback_manager.as_trace("insert_nodes"):
        self.docstore.add_documents(nodes, allow_update=True)
        self._insert(nodes, **insert_kwargs)
        self._storage_context.index_store.add_index_struct(self._index_struct)

```
  
---|---  
###  ainsert_nodes `async` #
```
ainsert_nodes(nodes: Sequence[BaseNode], **insert_kwargs: Any) -> None

```

Asynchronously insert nodes.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
async def ainsert_nodes(
    self, nodes: Sequence[BaseNode], **insert_kwargs: Any
) -> None:
    """Asynchronously insert nodes."""
    for node in nodes:
        if isinstance(node, IndexNode):
            try:
                node.dict()
            except ValueError:
                self._object_map[node.index_id] = node.obj
                node.obj = None

    with self._callback_manager.as_trace("ainsert_nodes"):
        await self.docstore.async_add_documents(nodes, allow_update=True)
        self._insert(nodes=nodes)
        await self._storage_context.index_store.async_add_index_struct(
            self._index_struct
        )

```
  
---|---  
###  insert #
```
insert(document: Document, **insert_kwargs: Any) -> None

```

Insert a document.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def insert(self, document: Document, **insert_kwargs: Any) -> None:
    """Insert a document."""
    with self._callback_manager.as_trace("insert"):
        nodes = run_transformations(
            [document],
            self._transformations,
            show_progress=self._show_progress,
            **insert_kwargs,
        )

        self.insert_nodes(nodes, **insert_kwargs)
        self.docstore.set_document_hash(document.get_doc_id(), document.hash)

```
  
---|---  
###  ainsert `async` #
```
ainsert(document: Document, **insert_kwargs: Any) -> None

```

Asynchronously insert a document.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
async def ainsert(self, document: Document, **insert_kwargs: Any) -> None:
    """Asynchronously insert a document."""
    with self._callback_manager.as_trace("ainsert"):
        nodes = await arun_transformations(
            [document],
            self._transformations,
            show_progress=self._show_progress,
            **insert_kwargs,
        )

        await self.ainsert_nodes(nodes, **insert_kwargs)
        await self.docstore.aset_document_hash(document.get_doc_id(), document.hash)

```
  
---|---  
###  delete_nodes #
```
delete_nodes(node_ids: List[str], delete_from_docstore: bool = False, **delete_kwargs: Any) -> None

```

Delete a list of nodes from the index.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`doc_ids` |  `List[str]` |  A list of doc_ids from the nodes to delete |  _required_  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def delete_nodes(
    self,
    node_ids: List[str],
    delete_from_docstore: bool = False,
    **delete_kwargs: Any,
) -> None:
    """
    Delete a list of nodes from the index.

    Args:
        doc_ids (List[str]): A list of doc_ids from the nodes to delete

    """
    for node_id in node_ids:
        self._delete_node(node_id, **delete_kwargs)
        if delete_from_docstore:
            self.docstore.delete_document(node_id, raise_error=False)

    self._storage_context.index_store.add_index_struct(self._index_struct)

```
  
---|---  
###  adelete_nodes `async` #
```
adelete_nodes(node_ids: List[str], delete_from_docstore: bool = False, **delete_kwargs: Any) -> None

```

Asynchronously delete a list of nodes from the index.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`doc_ids` |  `List[str]` |  A list of doc_ids from the nodes to delete |  _required_  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
async def adelete_nodes(
    self,
    node_ids: List[str],
    delete_from_docstore: bool = False,
    **delete_kwargs: Any,
) -> None:
    """
    Asynchronously delete a list of nodes from the index.

    Args:
        doc_ids (List[str]): A list of doc_ids from the nodes to delete

    """
    for node_id in node_ids:
        self._delete_node(node_id, **delete_kwargs)
        if delete_from_docstore:
            await self.docstore.adelete_document(node_id, raise_error=False)

    await self._storage_context.index_store.async_add_index_struct(
        self._index_struct
    )

```
  
---|---  
###  delete #
```
delete(doc_id: str, **delete_kwargs: Any) -> None

```

Delete a document from the index. All nodes in the index related to the index will be deleted.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`doc_id` |  `str` |  A doc_id of the ingested document |  _required_  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def delete(self, doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete a document from the index.
    All nodes in the index related to the index will be deleted.

    Args:
        doc_id (str): A doc_id of the ingested document

    """
    logger.warning(
        "delete() is now deprecated, please refer to delete_ref_doc() to delete "
        "ingested documents+nodes or delete_nodes to delete a list of nodes."
        "Use adelete_ref_docs() for an asynchronous implementation"
    )
    self.delete_ref_doc(doc_id)

```
  
---|---  
###  delete_ref_doc #
```
delete_ref_doc(ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any) -> None

```

Delete a document and it's nodes by using ref_doc_id.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def delete_ref_doc(
    self, ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any
) -> None:
    """Delete a document and it's nodes by using ref_doc_id."""
    ref_doc_info = self.docstore.get_ref_doc_info(ref_doc_id)
    if ref_doc_info is None:
        logger.warning(f"ref_doc_id {ref_doc_id} not found, nothing deleted.")
        return

    self.delete_nodes(
        ref_doc_info.node_ids,
        delete_from_docstore=False,
        **delete_kwargs,
    )

    if delete_from_docstore:
        self.docstore.delete_ref_doc(ref_doc_id, raise_error=False)

```
  
---|---  
###  adelete_ref_doc `async` #
```
adelete_ref_doc(ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any) -> None

```

Delete a document and it's nodes by using ref_doc_id.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
async def adelete_ref_doc(
    self, ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any
) -> None:
    """Delete a document and it's nodes by using ref_doc_id."""
    ref_doc_info = await self.docstore.aget_ref_doc_info(ref_doc_id)
    if ref_doc_info is None:
        logger.warning(f"ref_doc_id {ref_doc_id} not found, nothing deleted.")
        return

    await self.adelete_nodes(
        ref_doc_info.node_ids,
        delete_from_docstore=False,
        **delete_kwargs,
    )

    if delete_from_docstore:
        await self.docstore.adelete_ref_doc(ref_doc_id, raise_error=False)

```
  
---|---  
###  update #
```
update(document: Document, **update_kwargs: Any) -> None

```

Update a document and it's corresponding nodes.
This is equivalent to deleting the document and then inserting it again.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`document` |  `Union[BaseDocument, BaseIndex]` |  document to update |  _required_  
`insert_kwargs` |  `Dict` |  kwargs to pass to insert |  _required_  
`delete_kwargs` |  `Dict` |  kwargs to pass to delete |  _required_  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def update(self, document: Document, **update_kwargs: Any) -> None:
    """
    Update a document and it's corresponding nodes.

    This is equivalent to deleting the document and then inserting it again.

    Args:
        document (Union[BaseDocument, BaseIndex]): document to update
        insert_kwargs (Dict): kwargs to pass to insert
        delete_kwargs (Dict): kwargs to pass to delete

    """
    logger.warning(
        "update() is now deprecated, please refer to update_ref_doc() to update "
        "ingested documents+nodes."
        "Use aupdate_ref_docs() for an asynchronous implementation"
    )
    self.update_ref_doc(document, **update_kwargs)

```
  
---|---  
###  update_ref_doc #
```
update_ref_doc(document: Document, **update_kwargs: Any) -> None

```

Update a document and it's corresponding nodes.
This is equivalent to deleting the document and then inserting it again.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`document` |  `Union[BaseDocument, BaseIndex]` |  document to update |  _required_  
`insert_kwargs` |  `Dict` |  kwargs to pass to insert |  _required_  
`delete_kwargs` |  `Dict` |  kwargs to pass to delete |  _required_  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def update_ref_doc(self, document: Document, **update_kwargs: Any) -> None:
    """
    Update a document and it's corresponding nodes.

    This is equivalent to deleting the document and then inserting it again.

    Args:
        document (Union[BaseDocument, BaseIndex]): document to update
        insert_kwargs (Dict): kwargs to pass to insert
        delete_kwargs (Dict): kwargs to pass to delete

    """
    with self._callback_manager.as_trace("update_ref_doc"):
        self.delete_ref_doc(
            document.get_doc_id(),
            delete_from_docstore=True,
            **update_kwargs.pop("delete_kwargs", {}),
        )
        self.insert(document, **update_kwargs.pop("insert_kwargs", {}))

```
  
---|---  
###  aupdate_ref_doc `async` #
```
aupdate_ref_doc(document: Document, **update_kwargs: Any) -> None

```

Asynchronously update a document and it's corresponding nodes.
This is equivalent to deleting the document and then inserting it again.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`document` |  `Union[BaseDocument, BaseIndex]` |  document to update |  _required_  
`insert_kwargs` |  `Dict` |  kwargs to pass to insert |  _required_  
`delete_kwargs` |  `Dict` |  kwargs to pass to delete |  _required_  
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
async def aupdate_ref_doc(self, document: Document, **update_kwargs: Any) -> None:
    """
    Asynchronously update a document and it's corresponding nodes.

    This is equivalent to deleting the document and then inserting it again.

    Args:
        document (Union[BaseDocument, BaseIndex]): document to update
        insert_kwargs (Dict): kwargs to pass to insert
        delete_kwargs (Dict): kwargs to pass to delete

    """
    with self._callback_manager.as_trace("aupdate_ref_doc"):
        await self.adelete_ref_doc(
            document.get_doc_id(),
            delete_from_docstore=True,
            **update_kwargs.pop("delete_kwargs", {}),
        )
        await self.ainsert(document, **update_kwargs.pop("insert_kwargs", {}))

```
  
---|---  
###  refresh #
```
refresh(documents: Sequence[Document], **update_kwargs: Any) -> List[bool]

```

Refresh an index with documents that have changed.
This allows users to save LLM and Embedding model calls, while only updating documents that have any changes in text or metadata. It will also insert any documents that previously were not stored.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def refresh(
    self, documents: Sequence[Document], **update_kwargs: Any
) -> List[bool]:
    """
    Refresh an index with documents that have changed.

    This allows users to save LLM and Embedding model calls, while only
    updating documents that have any changes in text or metadata. It
    will also insert any documents that previously were not stored.
    """
    logger.warning(
        "refresh() is now deprecated, please refer to refresh_ref_docs() to "
        "refresh ingested documents+nodes with an updated list of documents."
        "Use arefresh_ref_docs() for an asynchronous implementation"
    )
    return self.refresh_ref_docs(documents, **update_kwargs)

```
  
---|---  
###  refresh_ref_docs #
```
refresh_ref_docs(documents: Sequence[Document], **update_kwargs: Any) -> List[bool]

```

Refresh an index with documents that have changed.
This allows users to save LLM and Embedding model calls, while only updating documents that have any changes in text or metadata. It will also insert any documents that previously were not stored.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def refresh_ref_docs(
    self, documents: Sequence[Document], **update_kwargs: Any
) -> List[bool]:
    """
    Refresh an index with documents that have changed.

    This allows users to save LLM and Embedding model calls, while only
    updating documents that have any changes in text or metadata. It
    will also insert any documents that previously were not stored.
    """
    with self._callback_manager.as_trace("refresh_ref_docs"):
        refreshed_documents = [False] * len(documents)
        for i, document in enumerate(documents):
            existing_doc_hash = self._docstore.get_document_hash(
                document.get_doc_id()
            )
            if existing_doc_hash is None:
                self.insert(document, **update_kwargs.pop("insert_kwargs", {}))
                refreshed_documents[i] = True
            elif existing_doc_hash != document.hash:
                self.update_ref_doc(
                    document, **update_kwargs.pop("update_kwargs", {})
                )
                refreshed_documents[i] = True

        return refreshed_documents

```
  
---|---  
###  arefresh_ref_docs `async` #
```
arefresh_ref_docs(documents: Sequence[Document], **update_kwargs: Any) -> List[bool]

```

Asynchronously refresh an index with documents that have changed.
This allows users to save LLM and Embedding model calls, while only updating documents that have any changes in text or metadata. It will also insert any documents that previously were not stored.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
async def arefresh_ref_docs(
    self, documents: Sequence[Document], **update_kwargs: Any
) -> List[bool]:
    """
    Asynchronously refresh an index with documents that have changed.

    This allows users to save LLM and Embedding model calls, while only
    updating documents that have any changes in text or metadata. It
    will also insert any documents that previously were not stored.
    """
    with self._callback_manager.as_trace("arefresh_ref_docs"):
        refreshed_documents = [False] * len(documents)
        for i, document in enumerate(documents):
            existing_doc_hash = await self._docstore.aget_document_hash(
                document.get_doc_id()
            )
            if existing_doc_hash is None:
                await self.ainsert(
                    document, **update_kwargs.pop("insert_kwargs", {})
                )
                refreshed_documents[i] = True
            elif existing_doc_hash != document.hash:
                await self.aupdate_ref_doc(
                    document, **update_kwargs.pop("update_kwargs", {})
                )
                refreshed_documents[i] = True
        return refreshed_documents

```
  
---|---  
###  as_query_engine #
```
as_query_engine(llm: Optional[LLMType] = None, **kwargs: Any) -> BaseQueryEngine

```

Convert the index to a query engine.
Calls `index.as_retriever(**kwargs)` to get the retriever and then wraps it in a `RetrieverQueryEngine.from_args(retriever, **kwrags)` call.
Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def as_query_engine(
    self, llm: Optional[LLMType] = None, **kwargs: Any
) -> BaseQueryEngine:
    """
    Convert the index to a query engine.

    Calls `index.as_retriever(**kwargs)` to get the retriever and then wraps it in a
    `RetrieverQueryEngine.from_args(retriever, **kwrags)` call.
    """
    # NOTE: lazy import
    from llama_index.core.query_engine.retriever_query_engine import (
        RetrieverQueryEngine,
    )

    retriever = self.as_retriever(**kwargs)
    llm = (
        resolve_llm(llm, callback_manager=self._callback_manager)
        if llm
        else Settings.llm
    )

    return RetrieverQueryEngine.from_args(
        retriever,
        llm=llm,
        **kwargs,
    )

```
  
---|---  
###  as_chat_engine #
```
as_chat_engine(chat_mode: ChatMode = BEST, llm: Optional[LLMType] = None, **kwargs: Any) -> BaseChatEngine

```

Convert the index to a chat engine.
Calls `index.as_query_engine(llm=llm, **kwargs)` to get the query engine and then wraps it in a chat engine based on the chat mode.
Chat modes
  * `ChatMode.BEST` (default): Chat engine that uses an agent (react or openai) with a query engine tool
  * `ChatMode.CONTEXT`: Chat engine that uses a retriever to get context
  * `ChatMode.CONDENSE_QUESTION`: Chat engine that condenses questions
  * `ChatMode.CONDENSE_PLUS_CONTEXT`: Chat engine that condenses questions and uses a retriever to get context
  * `ChatMode.SIMPLE`: Simple chat engine that uses the LLM directly
  * `ChatMode.REACT`: Chat engine that uses a react agent with a query engine tool
  * `ChatMode.OPENAI`: Chat engine that uses an openai agent with a query engine tool

Source code in `llama-index-core/llama_index/core/indices/base.py`

| ```
def as_chat_engine(
    self,
    chat_mode: ChatMode = ChatMode.BEST,
    llm: Optional[LLMType] = None,
    **kwargs: Any,
) -> BaseChatEngine:
    """
    Convert the index to a chat engine.

    Calls `index.as_query_engine(llm=llm, **kwargs)` to get the query engine and then
    wraps it in a chat engine based on the chat mode.

    Chat modes:
        - `ChatMode.BEST` (default): Chat engine that uses an agent (react or openai) with a query engine tool
        - `ChatMode.CONTEXT`: Chat engine that uses a retriever to get context
        - `ChatMode.CONDENSE_QUESTION`: Chat engine that condenses questions
        - `ChatMode.CONDENSE_PLUS_CONTEXT`: Chat engine that condenses questions and uses a retriever to get context
        - `ChatMode.SIMPLE`: Simple chat engine that uses the LLM directly
        - `ChatMode.REACT`: Chat engine that uses a react agent with a query engine tool
        - `ChatMode.OPENAI`: Chat engine that uses an openai agent with a query engine tool
    """
    llm = (
        resolve_llm(llm, callback_manager=self._callback_manager)
        if llm
        else Settings.llm
    )

    query_engine = self.as_query_engine(llm=llm, **kwargs)

    # resolve chat mode
    if chat_mode in [ChatMode.REACT, ChatMode.OPENAI]:
        raise ValueError(
            "ChatMode.REACT and ChatMode.OPENAI are now deprecated and removed. "
            "Please use the ReActAgent or FunctionAgent classes from llama_index.core.agent.workflow "
            "to create an agent with a query engine tool."
        )

    if chat_mode == ChatMode.CONDENSE_QUESTION:
        # NOTE: lazy import
        from llama_index.core.chat_engine import CondenseQuestionChatEngine

        return CondenseQuestionChatEngine.from_defaults(
            query_engine=query_engine,
            llm=llm,
            **kwargs,
        )

    elif chat_mode == ChatMode.CONTEXT:
        from llama_index.core.chat_engine import ContextChatEngine

        return ContextChatEngine.from_defaults(
            retriever=self.as_retriever(**kwargs),
            llm=llm,
            **kwargs,
        )

    elif chat_mode in [ChatMode.CONDENSE_PLUS_CONTEXT, ChatMode.BEST]:
        from llama_index.core.chat_engine import CondensePlusContextChatEngine

        return CondensePlusContextChatEngine.from_defaults(
            retriever=self.as_retriever(**kwargs),
            llm=llm,
            **kwargs,
        )

    elif chat_mode == ChatMode.SIMPLE:
        from llama_index.core.chat_engine import SimpleChatEngine

        return SimpleChatEngine.from_defaults(
            llm=llm,
            **kwargs,
        )
    else:
        raise ValueError(f"Unknown chat mode: {chat_mode}")

```
  
---|---
