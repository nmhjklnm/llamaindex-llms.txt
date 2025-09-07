# Prompt
Bases: `QueryComponent`
Prompt component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `BasePromptTemplate` |  Prompt |  _required_  
`llm` |  `Annotated[BaseLLM, SerializeAsAny] | None` |  LLM to use for formatting prompt. |  `None`  
`format_messages` |  `bool` |  Whether to format the prompt into a list of chat messages. |  `False`  
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
class PromptComponent(QueryComponent):
    """Prompt component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    prompt: SerializeAsAny[BasePromptTemplate] = Field(..., description="Prompt")
    llm: Optional[SerializeAsAny[BaseLLM]] = Field(
        default=None, description="LLM to use for formatting prompt."
    )
    format_messages: bool = Field(
        default=False,
        description="Whether to format the prompt into a list of chat messages.",
    )

    def set_callback_manager(self, callback_manager: Any) -> None:
        """Set callback manager."""

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        keys = list(input.keys())
        for k in keys:
            input[k] = validate_and_convert_stringable(input[k])
        return input

    def _run_component(self, **kwargs: Any) -> Any:
        """Run component."""
        if self.format_messages:
            output: Union[str, List[ChatMessage]] = self.prompt.format_messages(
                llm=self.llm, **kwargs
            )
        else:
            output = self.prompt.format(llm=self.llm, **kwargs)
        return {"prompt": output}

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component."""
        # NOTE: no native async for prompt
        return self._run_component(**kwargs)

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        return InputKeys.from_keys(
            set(self.prompt.template_vars) - set(self.prompt.kwargs)
        )

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        return OutputKeys.from_keys({"prompt"})

```
  
---|---  
##  input_keys `property` #
```
input_keys: InputKeys

```

Input keys.
##  output_keys `property` #
```
output_keys: OutputKeys

```

Output keys.
##  set_callback_manager #
```
set_callback_manager(callback_manager: Any) -> None

```

Set callback manager.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def set_callback_manager(self, callback_manager: Any) -> None:
    """Set callback manager."""

```
  
---|---
