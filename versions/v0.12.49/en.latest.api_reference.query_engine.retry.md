# Retry
##  RetryGuidelineQueryEngine #
Bases: `BaseQueryEngine`
Does retry with evaluator feedback if query engine fails evaluation.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_engine` |  `BaseQueryEngine` |  A query engine object |  _required_  
`guideline_evaluator` |  `GuidelineEvaluator` |  A guideline evaluator object |  _required_  
`resynthesize_query` |  `bool` |  Whether to resynthesize query |  `False`  
`max_retries` |  `int` |  Maximum number of retries |  `3`  
`callback_manager` |  `Optional[CallbackManager]` |  A callback manager object |  `None`  
Source code in `llama-index-core/llama_index/core/query_engine/retry_query_engine.py`

| ```
class RetryGuidelineQueryEngine(BaseQueryEngine):
    """
    Does retry with evaluator feedback
    if query engine fails evaluation.

    Args:
        query_engine (BaseQueryEngine): A query engine object
        guideline_evaluator (GuidelineEvaluator): A guideline evaluator object
        resynthesize_query (bool): Whether to resynthesize query
        max_retries (int): Maximum number of retries
        callback_manager (Optional[CallbackManager]): A callback manager object

    """

    def __init__(
        self,
        query_engine: BaseQueryEngine,
        guideline_evaluator: GuidelineEvaluator,
        resynthesize_query: bool = False,
        max_retries: int = 3,
        callback_manager: Optional[CallbackManager] = None,
        query_transformer: Optional[FeedbackQueryTransformation] = None,
    ) -> None:
        self._query_engine = query_engine
        self._guideline_evaluator = guideline_evaluator
        self.max_retries = max_retries
        self.resynthesize_query = resynthesize_query
        self.query_transformer = query_transformer or FeedbackQueryTransformation(
            resynthesize_query=self.resynthesize_query
        )
        super().__init__(callback_manager)

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {
            "query_engine": self._query_engine,
            "guideline_evalator": self._guideline_evaluator,
        }

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Answer a query."""
        response = self._query_engine._query(query_bundle)
        assert not isinstance(response, AsyncStreamingResponse)
        if self.max_retries <= 0:
            return response
        typed_response = (
            response if isinstance(response, Response) else response.get_response()
        )
        query_str = query_bundle.query_str
        eval = self._guideline_evaluator.evaluate_response(query_str, typed_response)
        if eval.passing:
            logger.debug("Evaluation returned True.")
            return response
        else:
            logger.debug("Evaluation returned False.")
            new_query_engine = RetryGuidelineQueryEngine(
                self._query_engine,
                self._guideline_evaluator,
                self.resynthesize_query,
                self.max_retries - 1,
                self.callback_manager,
            )
            new_query = self.query_transformer.run(query_bundle, {"evaluation": eval})
            logger.debug("New query: %s", new_query.query_str)
            return new_query_engine.query(new_query)

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Not supported."""
        return self._query(query_bundle)

```
  
---|---  
##  RetryQueryEngine #
Bases: `BaseQueryEngine`
Does retry on query engine if it fails evaluation.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_engine` |  `BaseQueryEngine` |  A query engine object |  _required_  
`evaluator` |  `BaseEvaluator` |  An evaluator object |  _required_  
`max_retries` |  `int` |  Maximum number of retries |  `3`  
`callback_manager` |  `Optional[CallbackManager]` |  A callback manager object |  `None`  
Source code in `llama-index-core/llama_index/core/query_engine/retry_query_engine.py`

| ```
class RetryQueryEngine(BaseQueryEngine):
    """
    Does retry on query engine if it fails evaluation.

    Args:
        query_engine (BaseQueryEngine): A query engine object
        evaluator (BaseEvaluator): An evaluator object
        max_retries (int): Maximum number of retries
        callback_manager (Optional[CallbackManager]): A callback manager object

    """

    def __init__(
        self,
        query_engine: BaseQueryEngine,
        evaluator: BaseEvaluator,
        max_retries: int = 3,
        callback_manager: Optional[CallbackManager] = None,
    ) -> None:
        self._query_engine = query_engine
        self._evaluator = evaluator
        self.max_retries = max_retries
        super().__init__(callback_manager)

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {"query_engine": self._query_engine, "evaluator": self._evaluator}

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Answer a query."""
        response = self._query_engine._query(query_bundle)
        assert not isinstance(response, AsyncStreamingResponse)
        if self.max_retries <= 0:
            return response
        typed_response = (
            response if isinstance(response, Response) else response.get_response()
        )
        query_str = query_bundle.query_str
        eval = self._evaluator.evaluate_response(query_str, typed_response)
        if eval.passing:
            logger.debug("Evaluation returned True.")
            return response
        else:
            logger.debug("Evaluation returned False.")
            new_query_engine = RetryQueryEngine(
                self._query_engine, self._evaluator, self.max_retries - 1
            )
            query_transformer = FeedbackQueryTransformation()
            new_query = query_transformer.run(query_bundle, {"evaluation": eval})
            return new_query_engine.query(new_query)

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Not supported."""
        return self._query(query_bundle)

```
  
---|---  
##  RetrySourceQueryEngine #
Bases: `BaseQueryEngine`
Retry with different source nodes.
Source code in `llama-index-core/llama_index/core/query_engine/retry_source_query_engine.py`

| ```
class RetrySourceQueryEngine(BaseQueryEngine):
    """Retry with different source nodes."""

    def __init__(
        self,
        query_engine: RetrieverQueryEngine,
        evaluator: BaseEvaluator,
        llm: Optional[LLM] = None,
        max_retries: int = 3,
        callback_manager: Optional[CallbackManager] = None,
    ) -> None:
        """Run a BaseQueryEngine with retries."""
        self._query_engine = query_engine
        self._evaluator = evaluator
        self._llm = llm or Settings.llm
        self.max_retries = max_retries
        super().__init__(callback_manager=callback_manager or Settings.callback_manager)

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {"query_engine": self._query_engine, "evaluator": self._evaluator}

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        response = self._query_engine._query(query_bundle)
        assert not isinstance(response, AsyncStreamingResponse)
        if self.max_retries <= 0:
            return response
        typed_response = (
            response if isinstance(response, Response) else response.get_response()
        )
        query_str = query_bundle.query_str
        eval = self._evaluator.evaluate_response(query_str, typed_response)
        if eval.passing:
            logger.debug("Evaluation returned True.")
            return response
        else:
            logger.debug("Evaluation returned False.")
            # Test source nodes
            source_evals = [
                self._evaluator.evaluate(
                    query=query_str,
                    response=typed_response.response,
                    contexts=[source_node.get_content()],
                )
                for source_node in typed_response.source_nodes
            ]
            orig_nodes = typed_response.source_nodes
            assert len(source_evals) == len(orig_nodes)
            new_docs = []
            for node, eval_result in zip(orig_nodes, source_evals):
                if eval_result:
                    new_docs.append(Document(text=node.node.get_content()))
            if len(new_docs) == 0:
                raise ValueError("No source nodes passed evaluation.")
            new_index = SummaryIndex.from_documents(
                new_docs,
            )
            new_retriever_engine = RetrieverQueryEngine(new_index.as_retriever())
            new_query_engine = RetrySourceQueryEngine(
                new_retriever_engine,
                self._evaluator,
                self._llm,
                self.max_retries - 1,
            )
            return new_query_engine.query(query_bundle)

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Not supported."""
        return self._query(query_bundle)

```
  
---|---
