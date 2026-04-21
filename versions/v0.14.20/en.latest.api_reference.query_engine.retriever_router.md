# Retriever router
##  RetrieverRouterQueryEngine #
Bases: `BaseQueryEngine`
Retriever-based router query engine.
NOTE: this is deprecated, please use our new ToolRetrieverRouterQueryEngine
Use a retriever to select a set of Nodes. Each node will be converted into a ToolMetadata object, and also used to retrieve a query engine, to form a QueryEngineTool.
NOTE: this is a beta feature. We are figuring out the right interface between the retriever and query engine.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `BaseSelector` |  A selector that chooses one out of many options based on each candidate's metadata and query. |  _required_  
`query_engine_tools` |  `Sequence[QueryEngineTool]` |  A sequence of candidate query engines. They must be wrapped as tools to expose metadata to the selector. |  _required_  
`callback_manager` |  `Optional[CallbackManager]` |  A callback manager. |  `None`  
Source code in `llama-index-core/llama_index/core/query_engine/router_query_engine.py`

| ```
class RetrieverRouterQueryEngine(BaseQueryEngine):
    """
    Retriever-based router query engine.

    NOTE: this is deprecated, please use our new ToolRetrieverRouterQueryEngine

    Use a retriever to select a set of Nodes. Each node will be converted
    into a ToolMetadata object, and also used to retrieve a query engine, to form
    a QueryEngineTool.

    NOTE: this is a beta feature. We are figuring out the right interface
    between the retriever and query engine.

    Args:
        selector (BaseSelector): A selector that chooses one out of many options based
            on each candidate's metadata and query.
        query_engine_tools (Sequence[QueryEngineTool]): A sequence of candidate
            query engines. They must be wrapped as tools to expose metadata to
            the selector.
        callback_manager (Optional[CallbackManager]): A callback manager.

    """

    def __init__(
        self,
        retriever: BaseRetriever,
        node_to_query_engine_fn: Callable,
        callback_manager: Optional[CallbackManager] = None,
    ) -> None:
        self._retriever = retriever
        self._node_to_query_engine_fn = node_to_query_engine_fn
        super().__init__(callback_manager)

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        # NOTE: don't include tools for now
        return {"retriever": self._retriever}

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        nodes_with_score = self._retriever.retrieve(query_bundle)
        # TODO: for now we only support retrieving one node
        if len(nodes_with_score) > 1:
            raise ValueError("Retrieved more than one node.")

        node = nodes_with_score[0].node
        query_engine = self._node_to_query_engine_fn(node)
        return query_engine.query(query_bundle)

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        return self._query(query_bundle)

```
  
---|---
