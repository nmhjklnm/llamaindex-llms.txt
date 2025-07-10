# Query response
Evaluation modules.
##  QueryResponseEvaluator `module-attribute` #
```
QueryResponseEvaluator = RelevancyEvaluator

```

##  RelevancyEvaluator #
Bases: `BaseEvaluator`
Relenvancy evaluator.
Evaluates the relevancy of retrieved contexts and response to a query. This evaluator considers the query string, retrieved contexts, and response string.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`raise_error(Optional[bool])` |  |  Whether to raise an error if the response is invalid. Defaults to False. |  _required_  
`eval_template(Optional[Union[str,` |  `BasePromptTemplate]]` |  The template to use for evaluation. |  _required_  
`refine_template(Optional[Union[str,` |  `BasePromptTemplate]]` |  The template to use for refinement. |  _required_  
Source code in `llama-index-core/llama_index/core/evaluation/relevancy.py`

| ```
class RelevancyEvaluator(BaseEvaluator):
    """
    Relenvancy evaluator.

    Evaluates the relevancy of retrieved contexts and response to a query.
    This evaluator considers the query string, retrieved contexts, and response string.

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
        eval_template: Optional[Union[str, BasePromptTemplate]] = None,
        refine_template: Optional[Union[str, BasePromptTemplate]] = None,
    ) -> None:
        """Init params."""
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
        """Evaluate whether the contexts and response are relevant to the query."""
        del kwargs  # Unused

        if query is None or contexts is None or response is None:
            raise ValueError("query, contexts, and response must be provided")

        docs = [Document(text=context) for context in contexts]
        index = SummaryIndex.from_documents(docs)

        query_response = f"Question: {query}\nResponse: {response}"

        await asyncio.sleep(sleep_time_in_seconds)

        query_engine = index.as_query_engine(
            llm=self._llm,
            text_qa_template=self._eval_template,
            refine_template=self._refine_template,
        )
        response_obj = await query_engine.aquery(query_response)

        raw_response_txt = str(response_obj)

        if "yes" in raw_response_txt.lower():
            passing = True
        else:
            if self._raise_error:
                raise ValueError("The response is invalid")
            passing = False

        return EvaluationResult(
            query=query,
            response=response,
            passing=passing,
            score=1.0 if passing else 0.0,
            feedback=raw_response_txt,
            contexts=contexts,
        )

```
  
---|---  
###  aevaluate `async` #
```
aevaluate(query: str | None = None, response: str | None = None, contexts: Sequence[str] | None = None, sleep_time_in_seconds: int = 0, **kwargs: Any) -> EvaluationResult

```

Evaluate whether the contexts and response are relevant to the query.
Source code in `llama-index-core/llama_index/core/evaluation/relevancy.py`

| ```
async def aevaluate(
    self,
    query: str | None = None,
    response: str | None = None,
    contexts: Sequence[str] | None = None,
    sleep_time_in_seconds: int = 0,
    **kwargs: Any,
) -> EvaluationResult:
    """Evaluate whether the contexts and response are relevant to the query."""
    del kwargs  # Unused

    if query is None or contexts is None or response is None:
        raise ValueError("query, contexts, and response must be provided")

    docs = [Document(text=context) for context in contexts]
    index = SummaryIndex.from_documents(docs)

    query_response = f"Question: {query}\nResponse: {response}"

    await asyncio.sleep(sleep_time_in_seconds)

    query_engine = index.as_query_engine(
        llm=self._llm,
        text_qa_template=self._eval_template,
        refine_template=self._refine_template,
    )
    response_obj = await query_engine.aquery(query_response)

    raw_response_txt = str(response_obj)

    if "yes" in raw_response_txt.lower():
        passing = True
    else:
        if self._raise_error:
            raise ValueError("The response is invalid")
        passing = False

    return EvaluationResult(
        query=query,
        response=response,
        passing=passing,
        score=1.0 if passing else 0.0,
        feedback=raw_response_txt,
        contexts=contexts,
    )

```
  
---|---
