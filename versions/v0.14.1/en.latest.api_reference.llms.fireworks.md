# Fireworks
##  Fireworks #
Bases: `OpenAI`
Fireworks LLM.
Examples:
`pip install llama-index-llms-fireworks`
```
from llama_index.llms.fireworks import Fireworks

# Create an instance of the Fireworks class
llm = Fireworks(
    model="accounts/fireworks/models/mixtral-8x7b-instruct",
    api_key="YOUR_API_KEY"
)

# Call the complete method with a prompt
resp = llm.complete("Hello world!")
print(resp)

```

Source code in `llama-index-integrations/llms/llama-index-llms-fireworks/llama_index/llms/fireworks/base.py`

| ```
class Fireworks(OpenAI):
    """
    Fireworks LLM.

    Examples:
        `pip install llama-index-llms-fireworks`

    ```python
        from llama_index.llms.fireworks import Fireworks

        # Create an instance of the Fireworks class
        llm = Fireworks(
            model="accounts/fireworks/models/mixtral-8x7b-instruct",
            api_key="YOUR_API_KEY"
        )

        # Call the complete method with a prompt
        resp = llm.complete("Hello world!")
        print(resp)
    ```

    """

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_NUM_OUTPUTS,
        additional_kwargs: Optional[Dict[str, Any]] = None,
        max_retries: int = 10,
        api_base: Optional[str] = DEFAULT_API_BASE,
        api_key: Optional[str] = None,
        callback_manager: Optional[CallbackManager] = None,
        default_headers: Optional[Dict[str, str]] = None,
        system_prompt: Optional[str] = None,
        messages_to_prompt: Optional[Callable[[Sequence[ChatMessage]], str]] = None,
        completion_to_prompt: Optional[Callable[[str], str]] = None,
        pydantic_program_mode: PydanticProgramMode = PydanticProgramMode.DEFAULT,
        output_parser: Optional[BaseOutputParser] = None,
    ) -> None:
        additional_kwargs = additional_kwargs or {}
        callback_manager = callback_manager or CallbackManager([])

        api_base = get_from_param_or_env("api_base", api_base, "FIREWORKS_API_BASE")
        api_key = get_from_param_or_env("api_key", api_key, "FIREWORKS_API_KEY")

        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=api_base,
            api_key=api_key,
            additional_kwargs=additional_kwargs,
            max_retries=max_retries,
            callback_manager=callback_manager,
            default_headers=default_headers,
            system_prompt=system_prompt,
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
            pydantic_program_mode=pydantic_program_mode,
            output_parser=output_parser,
        )

    @classmethod
    def class_name(cls) -> str:
        return "Fireworks_LLM"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=fireworks_modelname_to_contextsize(self.model),
            num_output=self.max_tokens,
            is_chat_model=True,
            model_name=self.model,
            is_function_calling_model=is_function_calling_model(
                model=self._get_model_name()
            ),
        )

    @property
    def _is_chat_model(self) -> bool:
        return True

```
  
---|---
