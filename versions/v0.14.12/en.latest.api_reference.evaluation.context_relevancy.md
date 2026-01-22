# Context relevancy
Evaluation modules.
##  ContextRelevancyEvaluator #
Bases: `BaseEvaluator`
Context relevancy evaluator.
Evaluates the relevancy of retrieved contexts to a query. This evaluator considers the query string and retrieved contexts.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`raise_error(Optional[bool])` |  |  Whether to raise an error if the response is invalid. Defaults to False. |  _required_  
`eval_template(Optional[Union[str,` |  `BasePromptTemplate]]` |  The template to use for evaluation. |  _required_  
`refine_template(Optional[Union[str,` |  `BasePromptTemplate]]` |  The template to use for refinement. |  _required_  
Source code in `llama-index-core/llama_index/core/evaluation/context_relevancy.py`

| ```
class ContextRelevancyEvaluator(BaseEvaluator):
    """
    Context relevancy evaluator.

    Evaluates the relevancy of retrieved contexts to a query.
    This evaluator considers the query string and retrieved contexts.

    Args:
        raise_error(Optional[bool]):
            Whether to raise an error if the response is invalid.
            Defaults to False.
        eval_template(Optional[Union[str, BasePromptTemplate]]):
            The template to use for evaluation.
        refine_template(Optional[Union[str, BasePromptTemplate]]):
            The template to use for refinement.

    """

    def __init__(
        self,
        llm: Optional[LLM] = None,
        raise_error: bool = False,
        eval_template: str | BasePromptTemplate | None = None,
        refine_template: str | BasePromptTemplate | None = None,
        score_threshold: float = _DEFAULT_SCORE_THRESHOLD,
        parser_function: Callable[
            [str], Tuple[Optional[float], Optional[str]]
        ] = _default_parser_function,
    ) -> None:
        """Init params."""
        from llama_index.core import Settings

        self._llm = llm or Settings.llm
        self._raise_error = raise_error

        self._eval_template: BasePromptTemplate
        if isinstance(eval_template, str):
            self._eval_template = PromptTemplate(eval_template)
        else:
            self._eval_template = eval_template or DEFAULT_EVAL_TEMPLATE

        self._refine_template: BasePromptTemplate
        if isinstance(refine_template, str):
            self._refine_template = PromptTemplate(refine_template)
        else:
            self._refine_template = refine_template or DEFAULT_REFINE_TEMPLATE

        self.parser_function = parser_function
        self.score_threshold = score_threshold

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {
            "eval_template": self._eval_template,
            "refine_template": self._refine_template,
        }

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "eval_template" in prompts:
            self._eval_template = prompts["eval_template"]
        if "refine_template" in prompts:
            self._refine_template = prompts["refine_template"]

    async def aevaluate(
        self,
        query: str | None = None,
        response: str | None = None,
        contexts: Sequence[str] | None = None,
        sleep_time_in_seconds: int = 0,
        **kwargs: Any,
    ) -> EvaluationResult:
        """Evaluate whether the contexts is relevant to the query."""
        del kwargs  # Unused
        del response  # Unused

        if query is None or contexts is None:
            raise ValueError("Both query and contexts must be provided")

        docs = [Document(text=context) for context in contexts]
        index = SummaryIndex.from_documents(docs)

        await asyncio.sleep(sleep_time_in_seconds)

        query_engine = index.as_query_engine(
            llm=self._llm,
            text_qa_template=self._eval_template,
            refine_template=self._refine_template,
        )
        response_obj = await query_engine.aquery(query)
        raw_response_txt = str(response_obj)

        score, reasoning = self.parser_function(raw_response_txt)

        invalid_result, invalid_reason = False, None
        if score is None and reasoning is None:
            if self._raise_error:
                raise ValueError("The response is invalid")
            invalid_result = True
            invalid_reason = "Unable to parse the output string."

        if score:
            score /= self.score_threshold

        return EvaluationResult(
            query=query,
            contexts=contexts,
            score=score,
            feedback=raw_response_txt,
            invalid_result=invalid_result,
            invalid_reason=invalid_reason,
        )

```
  
---|---  
###  aevaluate `async` #
```
aevaluate(query: str | None = None, response: str | None = None, contexts: Sequence[str] | None = None, sleep_time_in_seconds: int = 0, **kwargs: Any) -> EvaluationResult

```

Evaluate whether the contexts is relevant to the query.
Source code in `llama-index-core/llama_index/core/evaluation/context_relevancy.py`

| ```
async def aevaluate(
    self,
    query: str | None = None,
    response: str | None = None,
    contexts: Sequence[str] | None = None,
    sleep_time_in_seconds: int = 0,
    **kwargs: Any,
) -> EvaluationResult:
    """Evaluate whether the contexts is relevant to the query."""
    del kwargs  # Unused
    del response  # Unused

    if query is None or contexts is None:
        raise ValueError("Both query and contexts must be provided")

    docs = [Document(text=context) for context in contexts]
    index = SummaryIndex.from_documents(docs)

    await asyncio.sleep(sleep_time_in_seconds)

    query_engine = index.as_query_engine(
        llm=self._llm,
        text_qa_template=self._eval_template,
        refine_template=self._refine_template,
    )
    response_obj = await query_engine.aquery(query)
    raw_response_txt = str(response_obj)

    score, reasoning = self.parser_function(raw_response_txt)

    invalid_result, invalid_reason = False, None
    if score is None and reasoning is None:
        if self._raise_error:
            raise ValueError("The response is invalid")
        invalid_result = True
        invalid_reason = "Unable to parse the output string."

    if score:
        score /= self.score_threshold

    return EvaluationResult(
        query=query,
        contexts=contexts,
        score=score,
        feedback=raw_response_txt,
        invalid_result=invalid_result,
        invalid_reason=invalid_reason,
    )

```
  
---|---
