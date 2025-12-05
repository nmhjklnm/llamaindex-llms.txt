# Faithfullness
Evaluation modules.
##  FaithfulnessEvaluator #
Bases: `BaseEvaluator`
Faithfulness evaluator.
Evaluates whether a response is faithful to the contexts (i.e. whether the response is supported by the contexts or hallucinated.)
This evaluator only considers the response string and the list of context strings.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`raise_error(bool)` |  |  Whether to raise an error when the response is invalid. Defaults to False. |  _required_  
`eval_template(Optional[Union[str,` |  `BasePromptTemplate]]` |  The template to use for evaluation. |  _required_  
`refine_template(Optional[Union[str,` |  `BasePromptTemplate]]` |  The template to use for refining the evaluation. |  _required_  
Source code in `llama-index-core/llama_index/core/evaluation/faithfulness.py`

| ```
class FaithfulnessEvaluator(BaseEvaluator):
    """
    Faithfulness evaluator.

    Evaluates whether a response is faithful to the contexts
    (i.e. whether the response is supported by the contexts or hallucinated.)

    This evaluator only considers the response string and the list of context strings.

    Args:
        raise_error(bool): Whether to raise an error when the response is invalid.
            Defaults to False.
        eval_template(Optional[Union[str, BasePromptTemplate]]):
            The template to use for evaluation.
        refine_template(Optional[Union[str, BasePromptTemplate]]):
            The template to use for refining the evaluation.

    """

    def __init__(
        self,
        llm: Optional[LLM] = None,
        raise_error: bool = False,
        eval_template: Optional[Union[str, BasePromptTemplate]] = None,
        refine_template: Optional[Union[str, BasePromptTemplate]] = None,
    ) -> None:
        """Init params."""
        self._llm = llm or Settings.llm
        self._raise_error = raise_error

        self._eval_template: BasePromptTemplate
        if isinstance(eval_template, str):
            self._eval_template = PromptTemplate(eval_template)
        if isinstance(eval_template, BasePromptTemplate):
            self._eval_template = eval_template
        else:
            model_name = self._llm.metadata.model_name
            self._eval_template = TEMPLATES_CATALOG.get(
                model_name, DEFAULT_EVAL_TEMPLATE
            )

        self._refine_template: BasePromptTemplate
        if isinstance(refine_template, str):
            self._refine_template = PromptTemplate(refine_template)
        else:
            self._refine_template = refine_template or DEFAULT_REFINE_TEMPLATE

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
        """Evaluate whether the response is faithful to the contexts."""
        del kwargs  # Unused

        await asyncio.sleep(sleep_time_in_seconds)

        if contexts is None or response is None:
            raise ValueError("contexts and response must be provided")

        docs = [Document(text=context) for context in contexts]
        index = SummaryIndex.from_documents(docs)

        query_engine = index.as_query_engine(
            llm=self._llm,
            text_qa_template=self._eval_template,
            refine_template=self._refine_template,
        )
        response_obj = await query_engine.aquery(response)

        raw_response_txt = str(response_obj)

        if "yes" in raw_response_txt.lower():
            passing = True
        else:
            passing = False
            if self._raise_error:
                raise ValueError("The response is invalid")

        return EvaluationResult(
            query=query,
            response=response,
            contexts=contexts,
            passing=passing,
            score=1.0 if passing else 0.0,
            feedback=raw_response_txt,
        )

```
  
---|---  
###  aevaluate `async` #
```
aevaluate(query: str | None = None, response: str | None = None, contexts: Sequence[str] | None = None, sleep_time_in_seconds: int = 0, **kwargs: Any) -> EvaluationResult

```

Evaluate whether the response is faithful to the contexts.
Source code in `llama-index-core/llama_index/core/evaluation/faithfulness.py`

| ```
async def aevaluate(
    self,
    query: str | None = None,
    response: str | None = None,
    contexts: Sequence[str] | None = None,
    sleep_time_in_seconds: int = 0,
    **kwargs: Any,
) -> EvaluationResult:
    """Evaluate whether the response is faithful to the contexts."""
    del kwargs  # Unused

    await asyncio.sleep(sleep_time_in_seconds)

    if contexts is None or response is None:
        raise ValueError("contexts and response must be provided")

    docs = [Document(text=context) for context in contexts]
    index = SummaryIndex.from_documents(docs)

    query_engine = index.as_query_engine(
        llm=self._llm,
        text_qa_template=self._eval_template,
        refine_template=self._refine_template,
    )
    response_obj = await query_engine.aquery(response)

    raw_response_txt = str(response_obj)

    if "yes" in raw_response_txt.lower():
        passing = True
    else:
        passing = False
        if self._raise_error:
            raise ValueError("The response is invalid")

    return EvaluationResult(
        query=query,
        response=response,
        contexts=contexts,
        passing=passing,
        score=1.0 if passing else 0.0,
        feedback=raw_response_txt,
    )

```
  
---|---
