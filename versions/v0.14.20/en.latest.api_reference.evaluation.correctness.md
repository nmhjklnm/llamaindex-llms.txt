# Correctness
Evaluation modules.
##  CorrectnessEvaluator #
Bases: `BaseEvaluator`
Correctness evaluator.
Evaluates the correctness of a question answering system. This evaluator depends on `reference` answer to be provided, in addition to the query string and response string.
It outputs a score between 1 and 5, where 1 is the worst and 5 is the best, along with a reasoning for the score. Passing is defined as a score greater than or equal to the given threshold.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`eval_template` |  `Optional[Union[BasePromptTemplate, str]]` |  Template for the evaluation prompt. |  `None`  
`score_threshold` |  `float` |  Numerical threshold for passing the evaluation, defaults to 4.0. |  `4.0`  
Source code in `llama-index-core/llama_index/core/evaluation/correctness.py`

| ```
class CorrectnessEvaluator(BaseEvaluator):
    """
    Correctness evaluator.

    Evaluates the correctness of a question answering system.
    This evaluator depends on `reference` answer to be provided, in addition to the
    query string and response string.

    It outputs a score between 1 and 5, where 1 is the worst and 5 is the best,
    along with a reasoning for the score.
    Passing is defined as a score greater than or equal to the given threshold.

    Args:
        eval_template (Optional[Union[BasePromptTemplate, str]]):
            Template for the evaluation prompt.
        score_threshold (float): Numerical threshold for passing the evaluation,
            defaults to 4.0.

    """

    def __init__(
        self,
        llm: Optional[LLM] = None,
        eval_template: Optional[Union[BasePromptTemplate, str]] = None,
        score_threshold: float = 4.0,
        parser_function: Callable[
            [str], Tuple[Optional[float], Optional[str]]
        ] = default_parser,
    ) -> None:
        self._llm = llm or Settings.llm

        self._eval_template: BasePromptTemplate
        if isinstance(eval_template, str):
            self._eval_template = PromptTemplate(eval_template)
        else:
            self._eval_template = eval_template or DEFAULT_EVAL_TEMPLATE

        self._score_threshold = score_threshold
        self.parser_function = parser_function

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {
            "eval_template": self._eval_template,
        }

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "eval_template" in prompts:
            self._eval_template = prompts["eval_template"]

    async def aevaluate(
        self,
        query: Optional[str] = None,
        response: Optional[str] = None,
        contexts: Optional[Sequence[str]] = None,
        reference: Optional[str] = None,
        sleep_time_in_seconds: int = 0,
        **kwargs: Any,
    ) -> EvaluationResult:
        del kwargs  # Unused
        del contexts  # Unused

        await asyncio.sleep(sleep_time_in_seconds)

        if query is None or response is None:
            raise ValueError("query, and response must be provided")

        eval_response = await self._llm.apredict(
            prompt=self._eval_template,
            query=query,
            generated_answer=response,
            reference_answer=reference or "(NO REFERENCE ANSWER SUPPLIED)",
        )

        # Use the parser function
        score, reasoning = self.parser_function(eval_response)

        return EvaluationResult(
            query=query,
            response=response,
            passing=score >= self._score_threshold if score is not None else None,
            score=score,
            feedback=reasoning,
        )

```
  
---|---
