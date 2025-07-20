# Vector
##  VectorIndexRetriever #
Bases: `BaseRetriever`
Vector index retriever.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`index` |  `VectorStoreIndex` |  vector store index. |  _required_  
`similarity_top_k` |  `int` |  number of top k results to return. |  `DEFAULT_SIMILARITY_TOP_K`  
`vector_store_query_mode` |  `str` |  vector store query mode See reference for VectorStoreQueryMode for full list of supported modes. |  `DEFAULT`  
`filters` |  `Optional[MetadataFilters]` |  metadata filters, defaults to None |  `None`  
`alpha` |  `float` |  weight for sparse/dense retrieval, only used for hybrid query mode. |  `None`  
`doc_ids` |  `Optional[List[str]]` |  list of documents to constrain search. |  `None`  
`vector_store_kwargs` |  `dict` |  Additional vector store specific kwargs to pass through to the vector store at query time. |  _required_  
Source code in `llama-index-core/llama_index/core/indices/vector_store/retrievers/retriever.py`

| ```
class VectorIndexRetriever(BaseRetriever):
    """
    Vector index retriever.

    Args:
        index (VectorStoreIndex): vector store index.
        similarity_top_k (int): number of top k results to return.
        vector_store_query_mode (str): vector store query mode
            See reference for VectorStoreQueryMode for full list of supported modes.
        filters (Optional[MetadataFilters]): metadata filters, defaults to None
        alpha (float): weight for sparse/dense retrieval, only used for
            hybrid query mode.
        doc_ids (Optional[List[str]]): list of documents to constrain search.
        vector_store_kwargs (dict): Additional vector store specific kwargs to pass
            through to the vector store at query time.

    """

    def __init__(
        self,
        index: VectorStoreIndex,
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        vector_store_query_mode: VectorStoreQueryMode = VectorStoreQueryMode.DEFAULT,
        filters: Optional[MetadataFilters] = None,
        alpha: Optional[float] = None,
        node_ids: Optional[List[str]] = None,
        doc_ids: Optional[List[str]] = None,
        sparse_top_k: Optional[int] = None,
        hybrid_top_k: Optional[int] = None,
        callback_manager: Optional[CallbackManager] = None,
        object_map: Optional[dict] = None,
        embed_model: Optional[BaseEmbedding] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        self._index = index
        self._vector_store = self._index.vector_store
        self._embed_model = embed_model or self._index._embed_model
        self._docstore = self._index.docstore

        self._similarity_top_k = similarity_top_k
        self._vector_store_query_mode = VectorStoreQueryMode(vector_store_query_mode)
        self._alpha = alpha
        self._node_ids = node_ids
        self._doc_ids = doc_ids
        self._filters = filters
        self._sparse_top_k = sparse_top_k
        self._hybrid_top_k = hybrid_top_k
        self._kwargs: Dict[str, Any] = kwargs.get("vector_store_kwargs", {})

        callback_manager = callback_manager or CallbackManager()
        super().__init__(
            callback_manager=callback_manager,
            object_map=object_map,
            verbose=verbose,
        )

    @property
    def similarity_top_k(self) -> int:
        """Return similarity top k."""
        return self._similarity_top_k

    @similarity_top_k.setter
    def similarity_top_k(self, similarity_top_k: int) -> None:
        """Set similarity top k."""
        self._similarity_top_k = similarity_top_k

    @dispatcher.span
    def _retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        if self._vector_store.is_embedding_query:
            if query_bundle.embedding is None and len(query_bundle.embedding_strs) > 0:
                query_bundle.embedding = (
                    self._embed_model.get_agg_embedding_from_queries(
                        query_bundle.embedding_strs
                    )
                )
        return self._get_nodes_with_embeddings(query_bundle)

    @dispatcher.span
    async def _aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        embedding = query_bundle.embedding
        if self._vector_store.is_embedding_query:
            if query_bundle.embedding is None and len(query_bundle.embedding_strs) > 0:
                embed_model = self._embed_model
                embedding = await embed_model.aget_agg_embedding_from_queries(
                    query_bundle.embedding_strs
                )
        return await self._aget_nodes_with_embeddings(
            QueryBundle(query_str=query_bundle.query_str, embedding=embedding)
        )

    def _build_vector_store_query(
        self, query_bundle_with_embeddings: QueryBundle
    ) -> VectorStoreQuery:
        return VectorStoreQuery(
            query_embedding=query_bundle_with_embeddings.embedding,
            similarity_top_k=self._similarity_top_k,
            node_ids=self._node_ids,
            doc_ids=self._doc_ids,
            query_str=query_bundle_with_embeddings.query_str,
            mode=self._vector_store_query_mode,
            alpha=self._alpha,
            filters=self._filters,
            sparse_top_k=self._sparse_top_k,
            hybrid_top_k=self._hybrid_top_k,
        )

    def _determine_nodes_to_fetch(
        self, query_result: VectorStoreQueryResult
    ) -> list[str]:
        """
        Determine the nodes to fetch from the docstore.

        If the vector store does not store text, we need to fetch every node from the docstore.
        If the vector store stores text, we need to fetch only the nodes that are not text.
        """
        # Fetch all nodes from the docstore
        if query_result.nodes:
            # Fetch non-text nodes from the docstore
            return [
                node.node_id
                for node in query_result.nodes  # no folding
                if node.as_related_node_info().node_type != ObjectType.TEXT
            ]
        elif query_result.ids:
            return [
                self._index.index_struct.nodes_dict[idx] for idx in query_result.ids
            ]
        else:
            return []

    def _insert_fetched_nodes_into_query_result(
        self, query_result: VectorStoreQueryResult, fetched_nodes: List[BaseNode]
    ) -> Sequence[BaseNode]:
        """
        Insert the fetched nodes into the query result.

        If the vector store does not store text, all nodes are inserted into the query result.
        If the vector store stores text, we replace non-text nodes with those fetched from the docstore.
        """
        fetched_nodes_by_id: Dict[str, BaseNode] = {
            str(node.node_id): node for node in fetched_nodes
        }
        new_nodes: List[BaseNode] = []
        if query_result.nodes:
            for node in list(query_result.nodes):
                node_id_str = str(node.node_id)
                if node_id_str in fetched_nodes_by_id:
                    new_nodes.append(fetched_nodes_by_id[node_id_str])
                else:
                    new_nodes.append(node)
        elif query_result.ids:
            for node_id in query_result.ids:
                node_id_str = str(node_id)
                if node_id_str in fetched_nodes_by_id:
                    new_nodes.append(fetched_nodes_by_id[node_id_str])
                else:
                    raise KeyError(
                        f"Node ID {node_id_str} not found in fetched nodes. "
                    )
        elif query_result.ids is None and query_result.nodes is None:
            raise ValueError(
                "Vector store query result should return at least one of nodes or ids."
            )
        return new_nodes

    def _convert_nodes_to_scored_nodes(
        self, query_result: VectorStoreQueryResult
    ) -> List[NodeWithScore]:
        """Create scored nodes from the vector store query result."""
        node_with_scores: List[NodeWithScore] = []

        for ind, node in enumerate(list(query_result.nodes or [])):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[ind]

            node_with_scores.append(NodeWithScore(node=node, score=score))

        return node_with_scores

    def _get_nodes_with_embeddings(
        self, query_bundle_with_embeddings: QueryBundle
    ) -> List[NodeWithScore]:
        query = self._build_vector_store_query(query_bundle_with_embeddings)
        query_result = self._vector_store.query(query, **self._kwargs)

        # Fetch any missing nodes from the docstore and insert them into the query result
        nodes_to_fetch = self._determine_nodes_to_fetch(query_result)
        if nodes_to_fetch:
            fetched_nodes: List[BaseNode] = self._docstore.get_nodes(
                node_ids=nodes_to_fetch, raise_error=False
            )

            query_result.nodes = self._insert_fetched_nodes_into_query_result(
                query_result, fetched_nodes
            )

        log_vector_store_query_result(query_result)

        return self._convert_nodes_to_scored_nodes(query_result)

    async def _aget_nodes_with_embeddings(
        self, query_bundle_with_embeddings: QueryBundle
    ) -> List[NodeWithScore]:
        query = self._build_vector_store_query(query_bundle_with_embeddings)
        query_result = await self._vector_store.aquery(query, **self._kwargs)

        # Async fetch any missing nodes from the docstore and insert them into the query result
        fetched_nodes: List[BaseNode] = await self._docstore.aget_nodes(
            node_ids=self._determine_nodes_to_fetch(query_result), raise_error=False
        )

        query_result.nodes = self._insert_fetched_nodes_into_query_result(
            query_result, fetched_nodes
        )

        log_vector_store_query_result(query_result)

        return self._convert_nodes_to_scored_nodes(query_result)

```
  
---|---  
###  similarity_top_k `property` `writable` #
```
similarity_top_k: int

```

Return similarity top k.
##  VectorIndexAutoRetriever #
Bases: `BaseAutoRetriever`
Vector store auto retriever.
A retriever for vector store index that uses an LLM to automatically set vector store query parameters.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`index` |  `VectorStoreIndex` |  vector store index |  _required_  
`vector_store_info` |  `VectorStoreInfo` |  additional information about vector store content and supported metadata filters. The natural language description is used by an LLM to automatically set vector store query parameters. |  _required_  
`prompt_template_str` |  `Optional[str]` |  custom prompt template string for LLM. Uses default template string if None. |  `None`  
`similarity_top_k` |  `int` |  number of top k results to return. |  `DEFAULT_SIMILARITY_TOP_K`  
`empty_query_top_k` |  `Optional[int]` |  number of top k results to return if the inferred query string is blank (uses metadata filters only). Can be set to None, which would use the similarity_top_k instead. By default, set to 10. |  `10`  
`max_top_k` |  `int` |  the maximum top_k allowed. The top_k set by LLM or similarity_top_k will be clamped to this value. |  `10`  
`vector_store_query_mode` |  `str` |  vector store query mode See reference for VectorStoreQueryMode for full list of supported modes. |  `DEFAULT`  
`default_empty_query_vector` |  `Optional[List[float]]` |  default empty query vector. Defaults to None. If not None, then this vector will be used as the query vector if the query is empty. |  `None`  
`callback_manager` |  `Optional[CallbackManager]` |  callback manager |  `None`  
`verbose` |  `bool` |  verbose mode |  `False`  
Source code in `llama-index-core/llama_index/core/indices/vector_store/retrievers/auto_retriever/auto_retriever.py`

| ```
class VectorIndexAutoRetriever(BaseAutoRetriever):
    """
    Vector store auto retriever.

    A retriever for vector store index that uses an LLM to automatically set
    vector store query parameters.

    Args:
        index (VectorStoreIndex): vector store index
        vector_store_info (VectorStoreInfo): additional information about
            vector store content and supported metadata filters. The natural language
            description is used by an LLM to automatically set vector store query
            parameters.
        prompt_template_str: custom prompt template string for LLM.
            Uses default template string if None.
        similarity_top_k (int): number of top k results to return.
        empty_query_top_k (Optional[int]): number of top k results to return
            if the inferred query string is blank (uses metadata filters only).
            Can be set to None, which would use the similarity_top_k instead.
            By default, set to 10.
        max_top_k (int):
            the maximum top_k allowed. The top_k set by LLM or similarity_top_k will
            be clamped to this value.
        vector_store_query_mode (str): vector store query mode
            See reference for VectorStoreQueryMode for full list of supported modes.
        default_empty_query_vector (Optional[List[float]]): default empty query vector.
            Defaults to None. If not None, then this vector will be used as the query
            vector if the query is empty.
        callback_manager (Optional[CallbackManager]): callback manager
        verbose (bool): verbose mode

    """

    def __init__(
        self,
        index: VectorStoreIndex,
        vector_store_info: VectorStoreInfo,
        llm: Optional[LLM] = None,
        prompt_template_str: Optional[str] = None,
        max_top_k: int = 10,
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        empty_query_top_k: Optional[int] = 10,
        vector_store_query_mode: VectorStoreQueryMode = VectorStoreQueryMode.DEFAULT,
        default_empty_query_vector: Optional[List[float]] = None,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = False,
        extra_filters: Optional[MetadataFilters] = None,
        object_map: Optional[dict] = None,
        objects: Optional[List[IndexNode]] = None,
        **kwargs: Any,
    ) -> None:
        self._index = index
        self._vector_store_info = vector_store_info
        self._default_empty_query_vector = default_empty_query_vector
        self._llm = llm or Settings.llm
        callback_manager = callback_manager or Settings.callback_manager

        # prompt
        prompt_template_str = (
            prompt_template_str or DEFAULT_VECTOR_STORE_QUERY_PROMPT_TMPL
        )
        self._output_parser = VectorStoreQueryOutputParser()
        self._prompt: BasePromptTemplate = PromptTemplate(template=prompt_template_str)

        # additional config
        self._max_top_k = max_top_k
        self._similarity_top_k = similarity_top_k
        self._empty_query_top_k = empty_query_top_k
        self._vector_store_query_mode = vector_store_query_mode
        # if extra_filters is OR condition, we don't support that yet
        if extra_filters is not None and extra_filters.condition == FilterCondition.OR:
            raise ValueError("extra_filters cannot be OR condition")
        self._extra_filters = extra_filters or MetadataFilters(filters=[])
        self._kwargs = kwargs
        super().__init__(
            callback_manager=callback_manager,
            object_map=object_map or self._index._object_map,
            objects=objects,
            verbose=verbose,
        )

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {
            "prompt": self._prompt,
        }

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Get prompt modules."""
        if "prompt" in prompts:
            self._prompt = prompts["prompt"]

    def _get_query_bundle(self, query: str) -> QueryBundle:
        """Get query bundle."""
        if not query and self._default_empty_query_vector is not None:
            return QueryBundle(
                query_str="",
                embedding=self._default_empty_query_vector,
            )
        else:
            return QueryBundle(query_str=query)

    def _parse_generated_spec(
        self, output: str, query_bundle: QueryBundle
    ) -> BaseModel:
        """Parse generated spec."""
        try:
            structured_output = cast(
                StructuredOutput, self._output_parser.parse(output)
            )
            query_spec = cast(VectorStoreQuerySpec, structured_output.parsed_output)
        except OutputParserException:
            _logger.warning("Failed to parse query spec, using defaults as fallback.")
            query_spec = VectorStoreQuerySpec(
                query=query_bundle.query_str,
                filters=[],
                top_k=None,
            )

        return query_spec

    def generate_retrieval_spec(
        self, query_bundle: QueryBundle, **kwargs: Any
    ) -> BaseModel:
        # prepare input
        info_str = self._vector_store_info.model_dump_json(indent=4)
        schema_str = VectorStoreQuerySpec.model_json_schema()

        # call LLM
        output = self._llm.predict(
            self._prompt,
            schema_str=schema_str,
            info_str=info_str,
            query_str=query_bundle.query_str,
        )

        # parse output
        return self._parse_generated_spec(output, query_bundle)

    async def agenerate_retrieval_spec(
        self, query_bundle: QueryBundle, **kwargs: Any
    ) -> BaseModel:
        # prepare input
        info_str = self._vector_store_info.model_dump_json(indent=4)
        schema_str = VectorStoreQuerySpec.model_json_schema()

        # call LLM
        output = await self._llm.apredict(
            self._prompt,
            schema_str=schema_str,
            info_str=info_str,
            query_str=query_bundle.query_str,
        )

        # parse output
        return self._parse_generated_spec(output, query_bundle)

    def _build_retriever_from_spec(  # type: ignore
        self, spec: VectorStoreQuerySpec
    ) -> Tuple[BaseRetriever, QueryBundle]:
        # construct new query bundle from query_spec
        # insert 0 vector if query is empty and default_empty_query_vector is not None
        new_query_bundle = self._get_query_bundle(spec.query)

        _logger.info(f"Using query str: {spec.query}")
        filter_list = [
            (filter.key, filter.operator.value, filter.value) for filter in spec.filters
        ]
        _logger.info(f"Using filters: {filter_list}")
        if self._verbose:
            print(f"Using query str: {spec.query}")
            print(f"Using filters: {filter_list}")

        # define similarity_top_k
        # if query is specified, then use similarity_top_k
        # if query is blank, then use empty_query_top_k
        if spec.query or self._empty_query_top_k is None:
            similarity_top_k = self._similarity_top_k
        else:
            similarity_top_k = self._empty_query_top_k

        # if query_spec.top_k is specified, then use it
        # as long as below max_top_k and similarity_top_k
        if spec.top_k is not None:
            similarity_top_k = min(spec.top_k, self._max_top_k, similarity_top_k)

        _logger.info(f"Using top_k: {similarity_top_k}")

        # avoid passing empty filters to retriever
        if len(spec.filters) + len(self._extra_filters.filters) == 0:
            filters = None
        else:
            filters = MetadataFilters(
                filters=[*spec.filters, *self._extra_filters.filters]
            )

        return (
            VectorIndexRetriever(
                self._index,
                filters=filters,
                similarity_top_k=similarity_top_k,
                vector_store_query_mode=self._vector_store_query_mode,
                object_map=self.object_map,
                verbose=self._verbose,
                **self._kwargs,
            ),
            new_query_bundle,
        )

```
  
---|---
