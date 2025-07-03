# Guideline
Evaluation modules.
##  GuidelineEvaluator #
Bases: `BaseEvaluator`
Guideline evaluator.
Evaluates whether a query and response pair passes the given guidelines.
This evaluator only considers the query string and the response string.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`guidelines(Optional[str])` |  |  User-added guidelines to use for evaluation. Defaults to None, which uses the default guidelines. |  _required_  
`eval_template(Optional[Union[str,` |  `BasePromptTemplate]] ` |  The template to use for evaluation. |  _required_  
Source code in `llama-index-core/llama_index/core/evaluation/guideline.py`

| ```
class GuidelineEvaluator(BaseEvaluator):
    """
    Guideline evaluator.

    Evaluates whether a query and response pair passes the given guidelines.

    This evaluator only considers the query string and the response string.

    Args:
        guidelines(Optional[str]): User-added guidelines to use for evaluation.
            Defaults to None, which uses the default guidelines.
        eval_template(Optional[Union[str, BasePromptTemplate]] ):
            The template to use for evaluation.

    """

    def __init__(
        self,
        llm: Optional[LLM] = None,
        guidelines: Optional[str] = None,
        eval_template: Optional[Union[str, BasePromptTemplate]] = None,
        output_parser: Optional[PydanticOutputParser] = None,
    ) -> None:
        self._llm = llm or Settings.llm
        self._guidelines = guidelines or DEFAULT_GUIDELINES

        self._eval_template: BasePromptTemplate
        if isinstance(eval_template, str):
            self._eval_template = PromptTemplate(eval_template)
        else:
            self._eval_template = eval_template or DEFAULT_EVAL_TEMPLATE

        self._output_parser = output_parser or PydanticOutputParser(
            output_cls=EvaluationData
        )
        self._eval_template.output_parser = self._output_parser

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
        sleep_time_in_seconds: int = 0,
        **kwargs: Any,
    ) -> EvaluationResult:
        """Evaluate whether the query and response pair passes the guidelines."""
        del contexts  # Unused
        del kwargs  # Unused
        if query is None or response is None:
            raise ValueError("query and response must be provided")

        logger.debug("prompt: %s", self._eval_template)
        logger.debug("query: %s", query)
        logger.debug("response: %s", response)
        logger.debug("guidelines: %s", self._guidelines)

        await asyncio.sleep(sleep_time_in_seconds)

        eval_response = await self._llm.apredict(
            self._eval_template,
            query=query,
            response=response,
            guidelines=self._guidelines,
        )
        eval_data = self._output_parser.parse(eval_response)
        eval_data = cast(EvaluationData, eval_data)

        return EvaluationResult(
            query=query,
            response=response,
            passing=eval_data.passing,
            score=1.0 if eval_data.passing else 0.0,
            feedback=eval_data.feedback,
        )

```
  
---|---  
###  aevaluate `async` #
```
aevaluate(query: Optional[str] = None, response: Optional[str] = None, contexts: Optional[Sequence[str]] = None, sleep_time_in_seconds: int = 0, **kwargs: Any) -> EvaluationResult

```

Evaluate whether the query and response pair passes the guidelines.
Source code in `llama-index-core/llama_index/core/evaluation/guideline.py`

| ```
async def aevaluate(
    self,
    query: Optional[str] = None,
    response: Optional[str] = None,
    contexts: Optional[Sequence[str]] = None,
    sleep_time_in_seconds: int = 0,
    **kwargs: Any,
) -> EvaluationResult:
    """Evaluate whether the query and response pair passes the guidelines."""
    del contexts  # Unused
    del kwargs  # Unused
    if query is None or response is None:
        raise ValueError("query and response must be provided")

    logger.debug("prompt: %s", self._eval_template)
    logger.debug("query: %s", query)
    logger.debug("response: %s", response)
    logger.debug("guidelines: %s", self._guidelines)

    await asyncio.sleep(sleep_time_in_seconds)

    eval_response = await self._llm.apredict(
        self._eval_template,
        query=query,
        response=response,
        guidelines=self._guidelines,
    )
    eval_data = self._output_parser.parse(eval_response)
    eval_data = cast(EvaluationData, eval_data)

    return EvaluationResult(
        query=query,
        response=response,
        passing=eval_data.passing,
        score=1.0 if eval_data.passing else 0.0,
        feedback=eval_data.feedback,
    )

```
  
---|---
