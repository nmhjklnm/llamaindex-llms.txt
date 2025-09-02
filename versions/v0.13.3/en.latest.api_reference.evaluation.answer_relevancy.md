# Answer relevancy
Evaluation modules.
##  AnswerRelevancyEvaluator #
Bases: `BaseEvaluator`
Answer relevancy evaluator.
Evaluates the relevancy of response to a query. This evaluator considers the query string and response string.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`raise_error(Optional[bool])` |  |  Whether to raise an error if the response is invalid. Defaults to False. |  _required_  
`eval_template(Optional[Union[str,` |  `BasePromptTemplate]]` |  The template to use for evaluation. |  _required_  
`refine_template(Optional[Union[str,` |  `BasePromptTemplate]]` |  The template to use for refinement. |  _required_  
Source code in `llama-index-core/llama_index/core/evaluation/answer_relevancy.py`

| ```
class AnswerRelevancyEvaluator(BaseEvaluator):
    """
    Answer relevancy evaluator.

    Evaluates the relevancy of response to a query.
    This evaluator considers the query string and response string.

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
        score_threshold: float = _DEFAULT_SCORE_THRESHOLD,
        parser_function: Callable[
            [str], Tuple[Optional[float], Optional[str]]
        ] = _default_parser_function,
    ) -> None:
        """Init params."""
        self._llm = llm or Settings.llm
        self._raise_error = raise_error

        self._eval_template: BasePromptTemplate
        if isinstance(eval_template, str):
            self._eval_template = PromptTemplate(eval_template)
        else:
            self._eval_template = eval_template or DEFAULT_EVAL_TEMPLATE

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
        """Evaluate whether the response is relevant to the query."""
        del kwargs  # Unused
        del contexts  # Unused

        if query is None or response is None:
            raise ValueError("query and response must be provided")

        await asyncio.sleep(sleep_time_in_seconds)

        eval_response = await self._llm.apredict(
            prompt=self._eval_template,
            query=query,
            response=response,
        )

        score, reasoning = self.parser_function(eval_response)

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
            response=response,
            score=score,
            feedback=eval_response,
            invalid_result=invalid_result,
            invalid_reason=invalid_reason,
        )

```
  
---|---  
###  aevaluate `async` #
```
aevaluate(query: str | None = None, response: str | None = None, contexts: Sequence[str] | None = None, sleep_time_in_seconds: int = 0, **kwargs: Any) -> EvaluationResult

```

Evaluate whether the response is relevant to the query.
Source code in `llama-index-core/llama_index/core/evaluation/answer_relevancy.py`

| ```
async def aevaluate(
    self,
    query: str | None = None,
    response: str | None = None,
    contexts: Sequence[str] | None = None,
    sleep_time_in_seconds: int = 0,
    **kwargs: Any,
) -> EvaluationResult:
    """Evaluate whether the response is relevant to the query."""
    del kwargs  # Unused
    del contexts  # Unused

    if query is None or response is None:
        raise ValueError("query and response must be provided")

    await asyncio.sleep(sleep_time_in_seconds)

    eval_response = await self._llm.apredict(
        prompt=self._eval_template,
        query=query,
        response=response,
    )

    score, reasoning = self.parser_function(eval_response)

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
        response=response,
        score=score,
        feedback=eval_response,
        invalid_result=invalid_result,
        invalid_reason=invalid_reason,
    )

```
  
---|---
