# Tool retriever router
##  ToolRetrieverRouterQueryEngine #
Bases: `BaseQueryEngine`
Tool Retriever router query engine.
Selects a set of candidate query engines to execute a query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`retriever` |  `ObjectRetriever` |  A retriever that retrieves a set of query engine tools. |  _required_  
`summarizer` |  `Optional[TreeSummarize]` |  Tree summarizer to summarize sub-results. |  `None`  
Source code in `llama-index-core/llama_index/core/query_engine/router_query_engine.py`

| ```
class ToolRetrieverRouterQueryEngine(BaseQueryEngine):
    """
    Tool Retriever router query engine.

    Selects a set of candidate query engines to execute a query.

    Args:
        retriever (ObjectRetriever): A retriever that retrieves a set of
            query engine tools.
        summarizer (Optional[TreeSummarize]): Tree summarizer to summarize sub-results.

    """

    def __init__(
        self,
        retriever: ObjectRetriever[QueryEngineTool],
        llm: Optional[LLM] = None,
        summarizer: Optional[TreeSummarize] = None,
    ) -> None:
        llm = llm or Settings.llm
        self._summarizer = summarizer or TreeSummarize(
            llm=llm,
            summary_template=DEFAULT_TREE_SUMMARIZE_PROMPT_SEL,
        )
        self._retriever = retriever

        super().__init__(Settings.callback_manager)

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        # NOTE: don't include tools for now
        return {"summarizer": self._summarizer}

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            query_engine_tools = self._retriever.retrieve(query_bundle)
            responses = []
            for query_engine_tool in query_engine_tools:
                query_engine = query_engine_tool.query_engine
                responses.append(query_engine.query(query_bundle))

            if len(responses) > 1:
                final_response = combine_responses(
                    self._summarizer, responses, query_bundle
                )
            else:
                final_response = responses[0]

            # add selected result
            final_response.metadata = final_response.metadata or {}
            final_response.metadata["retrieved_tools"] = query_engine_tools

            query_event.on_end(payload={EventPayload.RESPONSE: final_response})

        return final_response

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            query_engine_tools = self._retriever.retrieve(query_bundle)
            tasks = []
            for query_engine_tool in query_engine_tools:
                query_engine = query_engine_tool.query_engine
                tasks.append(query_engine.aquery(query_bundle))
            responses = run_async_tasks(tasks)
            if len(responses) > 1:
                final_response = await acombine_responses(
                    self._summarizer, responses, query_bundle
                )
            else:
                final_response = responses[0]

            # add selected result
            final_response.metadata = final_response.metadata or {}
            final_response.metadata["retrieved_tools"] = query_engine_tools

            query_event.on_end(payload={EventPayload.RESPONSE: final_response})

        return final_response

```
  
---|---
