# Knowledge graph
##  KnowledgeGraphQueryEngine #
Bases: `BaseQueryEngine`
Knowledge graph query engine.
Query engine to call a knowledge graph.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`storage_context` |  `Optional[StorageContext]` |  A storage context to use. |  `None`  
`refresh_schema` |  `bool` |  Whether to refresh the schema. |  `False`  
`verbose` |  `bool` |  Whether to print intermediate results. |  `False`  
`response_synthesizer` |  `Optional[BaseSynthesizer]` |  A BaseSynthesizer object. |  `None`  
`**kwargs` |  `Any` |  Additional keyword arguments. |  `{}`  
Source code in `llama-index-core/llama_index/core/query_engine/knowledge_graph_query_engine.py`

| ```
@deprecated.deprecated(
    version="0.10.53",
    reason=(
        "KnowledgeGraphQueryEngine is deprecated. It is recommended to use "
        "the PropertyGraphIndex and associated retrievers instead."
    ),
)
class KnowledgeGraphQueryEngine(BaseQueryEngine):
    """
    Knowledge graph query engine.

    Query engine to call a knowledge graph.

    Args:
        storage_context (Optional[StorageContext]): A storage context to use.
        refresh_schema (bool): Whether to refresh the schema.
        verbose (bool): Whether to print intermediate results.
        response_synthesizer (Optional[BaseSynthesizer]):
            A BaseSynthesizer object.
        **kwargs: Additional keyword arguments.

    """

    def __init__(
        self,
        llm: Optional[LLM] = None,
        storage_context: Optional[StorageContext] = None,
        graph_query_synthesis_prompt: Optional[BasePromptTemplate] = None,
        graph_response_answer_prompt: Optional[BasePromptTemplate] = None,
        refresh_schema: bool = False,
        verbose: bool = False,
        response_synthesizer: Optional[BaseSynthesizer] = None,
        **kwargs: Any,
    ):
        # Ensure that we have a graph store
        assert storage_context is not None, "Must provide a storage context."
        assert storage_context.graph_store is not None, (
            "Must provide a graph store in the storage context."
        )
        self._storage_context = storage_context
        self.graph_store = storage_context.graph_store

        self._llm = llm or Settings.llm

        # Get Graph schema
        self._graph_schema = self.graph_store.get_schema(refresh=refresh_schema)

        # Get graph store query synthesis prompt
        self._graph_query_synthesis_prompt = graph_query_synthesis_prompt

        self._graph_response_answer_prompt = (
            graph_response_answer_prompt or DEFAULT_KG_RESPONSE_ANSWER_PROMPT
        )
        self._verbose = verbose
        callback_manager = Settings.callback_manager
        self._response_synthesizer = response_synthesizer or get_response_synthesizer(
            llm=self._llm, callback_manager=callback_manager
        )

        super().__init__(callback_manager=callback_manager)

    def _get_prompts(self) -> Dict[str, Any]:
        """Get prompts."""
        return {
            "graph_query_synthesis_prompt": self._graph_query_synthesis_prompt,
            "graph_response_answer_prompt": self._graph_response_answer_prompt,
        }

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "graph_query_synthesis_prompt" in prompts:
            self._graph_query_synthesis_prompt = prompts["graph_query_synthesis_prompt"]
        if "graph_response_answer_prompt" in prompts:
            self._graph_response_answer_prompt = prompts["graph_response_answer_prompt"]

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {"response_synthesizer": self._response_synthesizer}

    def generate_query(self, query_str: str) -> str:
        """Generate a Graph Store Query from a query bundle."""
        # Get the query engine query string

        graph_store_query: str = self._llm.predict(
            self._graph_query_synthesis_prompt,
            query_str=query_str,
            schema=self._graph_schema,
        )

        return graph_store_query

    async def agenerate_query(self, query_str: str) -> str:
        """Generate a Graph Store Query from a query bundle."""
        # Get the query engine query string

        graph_store_query: str = await self._llm.apredict(
            self._graph_query_synthesis_prompt,
            query_str=query_str,
            schema=self._graph_schema,
        )

        return graph_store_query

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Get nodes for response."""
        graph_store_query = self.generate_query(query_bundle.query_str)
        if self._verbose:
            print_text(f"Graph Store Query:\n{graph_store_query}\n", color="yellow")
        logger.debug(f"Graph Store Query:\n{graph_store_query}")

        with self.callback_manager.event(
            CBEventType.RETRIEVE,
            payload={EventPayload.QUERY_STR: graph_store_query},
        ) as retrieve_event:
            # Get the graph store response
            graph_store_response = self.graph_store.query(query=graph_store_query)
            if self._verbose:
                print_text(
                    f"Graph Store Response:\n{graph_store_response}\n",
                    color="yellow",
                )
            logger.debug(f"Graph Store Response:\n{graph_store_response}")

            retrieve_event.on_end(payload={EventPayload.RESPONSE: graph_store_response})

        retrieved_graph_context: Sequence = self._graph_response_answer_prompt.format(
            query_str=query_bundle.query_str,
            kg_query_str=graph_store_query,
            kg_response_str=graph_store_response,
        )

        node = NodeWithScore(
            node=TextNode(
                text=retrieved_graph_context,
                metadata={
                    "query_str": query_bundle.query_str,
                    "graph_store_query": graph_store_query,
                    "graph_store_response": graph_store_response,
                    "graph_schema": self._graph_schema,
                },
            ),
            score=1.0,
        )
        return [node]

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Query the graph store."""
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            nodes: List[NodeWithScore] = self._retrieve(query_bundle)

            response = self._response_synthesizer.synthesize(
                query=query_bundle,
                nodes=nodes,
            )

            if self._verbose:
                print_text(f"Final Response: {response}\n", color="green")

            query_event.on_end(payload={EventPayload.RESPONSE: response})

        return response

    async def _aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        graph_store_query = await self.agenerate_query(query_bundle.query_str)
        if self._verbose:
            print_text(f"Graph Store Query:\n{graph_store_query}\n", color="yellow")
        logger.debug(f"Graph Store Query:\n{graph_store_query}")

        with self.callback_manager.event(
            CBEventType.RETRIEVE,
            payload={EventPayload.QUERY_STR: graph_store_query},
        ) as retrieve_event:
            # Get the graph store response
            # TBD: This is a blocking call. We need to make it async.
            graph_store_response = self.graph_store.query(query=graph_store_query)
            if self._verbose:
                print_text(
                    f"Graph Store Response:\n{graph_store_response}\n",
                    color="yellow",
                )
            logger.debug(f"Graph Store Response:\n{graph_store_response}")

            retrieve_event.on_end(payload={EventPayload.RESPONSE: graph_store_response})

        retrieved_graph_context: Sequence = self._graph_response_answer_prompt.format(
            query_str=query_bundle.query_str,
            kg_query_str=graph_store_query,
            kg_response_str=graph_store_response,
        )

        node = NodeWithScore(
            node=TextNode(
                text=retrieved_graph_context,
                metadata={
                    "query_str": query_bundle.query_str,
                    "graph_store_query": graph_store_query,
                    "graph_store_response": graph_store_response,
                    "graph_schema": self._graph_schema,
                },
            ),
            score=1.0,
        )
        return [node]

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Query the graph store."""
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            nodes = await self._aretrieve(query_bundle)
            response = await self._response_synthesizer.asynthesize(
                query=query_bundle,
                nodes=nodes,
            )

            if self._verbose:
                print_text(f"Final Response: {response}\n", color="green")

            query_event.on_end(payload={EventPayload.RESPONSE: response})

        return response

```
  
---|---  
###  generate_query #
```
generate_query(query_str: str) -> str

```

Generate a Graph Store Query from a query bundle.
Source code in `llama-index-core/llama_index/core/query_engine/knowledge_graph_query_engine.py`

| ```
def generate_query(self, query_str: str) -> str:
    """Generate a Graph Store Query from a query bundle."""
    # Get the query engine query string

    graph_store_query: str = self._llm.predict(
        self._graph_query_synthesis_prompt,
        query_str=query_str,
        schema=self._graph_schema,
    )

    return graph_store_query

```
  
---|---  
###  agenerate_query `async` #
```
agenerate_query(query_str: str) -> str

```

Generate a Graph Store Query from a query bundle.
Source code in `llama-index-core/llama_index/core/query_engine/knowledge_graph_query_engine.py`

| ```
async def agenerate_query(self, query_str: str) -> str:
    """Generate a Graph Store Query from a query bundle."""
    # Get the query engine query string

    graph_store_query: str = await self._llm.apredict(
        self._graph_query_synthesis_prompt,
        query_str=query_str,
        schema=self._graph_schema,
    )

    return graph_store_query

```
  
---|---
