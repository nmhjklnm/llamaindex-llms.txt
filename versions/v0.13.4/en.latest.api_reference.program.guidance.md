# Guidance
##  GuidancePydanticProgram #
Bases: `BaseLLMFunctionProgram['GuidanceLLM']`
A guidance-based function that returns a pydantic model.
Note: this interface is not yet stable.
Source code in `llama-index-integrations/program/llama-index-program-guidance/llama_index/program/guidance/base.py`

| ```
class GuidancePydanticProgram(BaseLLMFunctionProgram["GuidanceLLM"]):
    """
    A guidance-based function that returns a pydantic model.

    Note: this interface is not yet stable.
    """

    def __init__(
        self,
        output_cls: Type[BaseModel],
        prompt_template_str: str,
        guidance_llm: Optional["GuidanceLLM"] = None,
        verbose: bool = False,
    ):
        if not guidance_llm:
            llm = guidance_llm
        else:
            llm = OpenAI("gpt-3.5-turbo")

        full_str = prompt_template_str + "\n"
        self._full_str = full_str
        self._guidance_program = partial(self.program, llm=llm, silent=not verbose)
        self._output_cls = output_cls
        self._verbose = verbose

    def program(
        self,
        llm: "GuidanceLLM",
        silent: bool,
        tools_str: str,
        query_str: str,
        **kwargs: dict,
    ) -> "GuidanceLLM":
        """A wrapper to execute the program with new guidance version."""
        given_query = self._full_str.replace("{{tools_str}}", tools_str).replace(
            "{{query_str}}", query_str
        )
        with user():
            llm = llm + given_query

        with assistant():
            llm = llm + gen(stop=".")

        return llm  # noqa: RET504

    @classmethod
    def from_defaults(
        cls,
        output_cls: Type[BaseModel],
        prompt_template_str: Optional[str] = None,
        prompt: Optional[PromptTemplate] = None,
        llm: Optional["GuidanceLLM"] = None,
        **kwargs: Any,
    ) -> "BaseLLMFunctionProgram":
        """From defaults."""
        if prompt is None and prompt_template_str is None:
            raise ValueError("Must provide either prompt or prompt_template_str.")
        if prompt is not None and prompt_template_str is not None:
            raise ValueError("Must provide either prompt or prompt_template_str.")
        if prompt is not None:
            prompt_template_str = prompt.template
        prompt_template_str = cast(str, prompt_template_str)
        return cls(
            output_cls,
            prompt_template_str,
            guidance_llm=llm,
            **kwargs,
        )

    @property
    def output_cls(self) -> Type[BaseModel]:
        return self._output_cls

    def __call__(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> BaseModel:
        executed_program = self._guidance_program(**kwargs)
        response = str(executed_program)

        return parse_pydantic_from_guidance_program(
            response=response, cls=self._output_cls
        )

```
  
---|---  
###  program #
```
program(llm: Model, silent: bool, tools_str: str, query_str: str, **kwargs: dict) -> Model

```

A wrapper to execute the program with new guidance version.
Source code in `llama-index-integrations/program/llama-index-program-guidance/llama_index/program/guidance/base.py`

| ```
def program(
    self,
    llm: "GuidanceLLM",
    silent: bool,
    tools_str: str,
    query_str: str,
    **kwargs: dict,
) -> "GuidanceLLM":
    """A wrapper to execute the program with new guidance version."""
    given_query = self._full_str.replace("{{tools_str}}", tools_str).replace(
        "{{query_str}}", query_str
    )
    with user():
        llm = llm + given_query

    with assistant():
        llm = llm + gen(stop=".")

    return llm  # noqa: RET504

```
  
---|---  
###  from_defaults `classmethod` #
```
from_defaults(output_cls: Type[BaseModel], prompt_template_str: Optional[str] = None, prompt: Optional[PromptTemplate] = None, llm: Optional[Model] = None, **kwargs: Any) -> BaseLLMFunctionProgram

```

From defaults.
Source code in `llama-index-integrations/program/llama-index-program-guidance/llama_index/program/guidance/base.py`

| ```
@classmethod
def from_defaults(
    cls,
    output_cls: Type[BaseModel],
    prompt_template_str: Optional[str] = None,
    prompt: Optional[PromptTemplate] = None,
    llm: Optional["GuidanceLLM"] = None,
    **kwargs: Any,
) -> "BaseLLMFunctionProgram":
    """From defaults."""
    if prompt is None and prompt_template_str is None:
        raise ValueError("Must provide either prompt or prompt_template_str.")
    if prompt is not None and prompt_template_str is not None:
        raise ValueError("Must provide either prompt or prompt_template_str.")
    if prompt is not None:
        prompt_template_str = prompt.template
    prompt_template_str = cast(str, prompt_template_str)
    return cls(
        output_cls,
        prompt_template_str,
        guidance_llm=llm,
        **kwargs,
    )

```
  
---|---
