# Router
##  RouterQueryEngine #
Bases: `BaseQueryEngine`
Router query engine.
Selects one out of several candidate query engines to execute a query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `BaseSelector` |  A selector that chooses one out of many options based on each candidate's metadata and query. |  _required_  
`query_engine_tools` |  `Sequence[QueryEngineTool]` |  A sequence of candidate query engines. They must be wrapped as tools to expose metadata to the selector. |  _required_  
`summarizer` |  `Optional[TreeSummarize]` |  Tree summarizer to summarize sub-results. |  `None`  
Source code in `llama-index-core/llama_index/core/query_engine/router_query_engine.py`

| ```
class RouterQueryEngine(BaseQueryEngine):
    """
    Router query engine.

    Selects one out of several candidate query engines to execute a query.

    Args:
        selector (BaseSelector): A selector that chooses one out of many options based
            on each candidate's metadata and query.
        query_engine_tools (Sequence[QueryEngineTool]): A sequence of candidate
            query engines. They must be wrapped as tools to expose metadata to
            the selector.
        summarizer (Optional[TreeSummarize]): Tree summarizer to summarize sub-results.

    """

    def __init__(
        self,
        selector: BaseSelector,
        query_engine_tools: Sequence[QueryEngineTool],
        llm: Optional[LLM] = None,
        summarizer: Optional[TreeSummarize] = None,
        verbose: bool = False,
    ) -> None:
        self._llm = llm or Settings.llm
        self._selector = selector
        self._query_engines = [x.query_engine for x in query_engine_tools]
        self._metadatas = [x.metadata for x in query_engine_tools]
        self._summarizer = summarizer or TreeSummarize(
            llm=self._llm,
            summary_template=DEFAULT_TREE_SUMMARIZE_PROMPT_SEL,
        )
        self._verbose = verbose

        super().__init__(callback_manager=Settings.callback_manager)

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        # NOTE: don't include tools for now
        return {"summarizer": self._summarizer, "selector": self._selector}

    @classmethod
    def from_defaults(
        cls,
        query_engine_tools: Sequence[QueryEngineTool],
        llm: Optional[LLM] = None,
        selector: Optional[BaseSelector] = None,
        summarizer: Optional[TreeSummarize] = None,
        select_multi: bool = False,
        **kwargs: Any,
    ) -> "RouterQueryEngine":
        llm = llm or Settings.llm

        selector = selector or get_selector_from_llm(llm, is_multi=select_multi)

        assert selector is not None

        return cls(
            selector,
            query_engine_tools,
            llm=llm,
            summarizer=summarizer,
            **kwargs,
        )

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            result = self._selector.select(self._metadatas, query_bundle)

            if len(result.inds) > 1:
                responses = []
                for i, engine_ind in enumerate(result.inds):
                    log_str = (
                        f"Selecting query engine {engine_ind}: {result.reasons[i]}."
                    )
                    logger.info(log_str)
                    if self._verbose:
                        print_text(log_str + "\n", color="pink")

                    selected_query_engine = self._query_engines[engine_ind]
                    responses.append(selected_query_engine.query(query_bundle))

                if len(responses) > 1:
                    final_response = combine_responses(
                        self._summarizer, responses, query_bundle
                    )
                else:
                    final_response = responses[0]
            else:
                try:
                    selected_query_engine = self._query_engines[result.ind]
                    log_str = f"Selecting query engine {result.ind}: {result.reason}."
                    logger.info(log_str)
                    if self._verbose:
                        print_text(log_str + "\n", color="pink")
                except ValueError as e:
                    raise ValueError("Failed to select query engine") from e

                final_response = selected_query_engine.query(query_bundle)

            # add selected result
            final_response.metadata = final_response.metadata or {}
            final_response.metadata["selector_result"] = result

            query_event.on_end(payload={EventPayload.RESPONSE: final_response})

        return final_response

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            result = await self._selector.aselect(self._metadatas, query_bundle)

            if len(result.inds) > 1:
                tasks = []
                for i, engine_ind in enumerate(result.inds):
                    log_str = (
                        f"Selecting query engine {engine_ind}: {result.reasons[i]}."
                    )
                    logger.info(log_str)
                    if self._verbose:
                        print_text(log_str + "\n", color="pink")
                    selected_query_engine = self._query_engines[engine_ind]
                    tasks.append(selected_query_engine.aquery(query_bundle))

                responses = run_async_tasks(tasks)
                if len(responses) > 1:
                    final_response = await acombine_responses(
                        self._summarizer, responses, query_bundle
                    )
                else:
                    final_response = responses[0]
            else:
                try:
                    selected_query_engine = self._query_engines[result.ind]
                    log_str = f"Selecting query engine {result.ind}: {result.reason}."
                    logger.info(log_str)
                    if self._verbose:
                        print_text(log_str + "\n", color="pink")
                except ValueError as e:
                    raise ValueError("Failed to select query engine") from e

                final_response = await selected_query_engine.aquery(query_bundle)

            # add selected result
            final_response.metadata = final_response.metadata or {}
            final_response.metadata["selector_result"] = result

            query_event.on_end(payload={EventPayload.RESPONSE: final_response})

        return final_response

```
  
---|---
