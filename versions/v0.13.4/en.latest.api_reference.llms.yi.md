# Yi
##  Yi #
Bases: `OpenAI`
Yi LLM.
Examples:
`pip install llama-index-llms-yi`
```
from llama_index.llms.yi import Yi

# get api key from: https://platform.01.ai/
llm = Yi(model="yi-large", api_key="YOUR_API_KEY")

response = llm.complete("Hi, who are you?")
print(response)

```

Source code in `llama-index-integrations/llms/llama-index-llms-yi/llama_index/llms/yi/base.py`

| ```
class Yi(OpenAI):
    """
    Yi LLM.

    Examples:
        `pip install llama-index-llms-yi`

    ```python
        from llama_index.llms.yi import Yi

        # get api key from: https://platform.01.ai/
        llm = Yi(model="yi-large", api_key="YOUR_API_KEY")

        response = llm.complete("Hi, who are you?")
        print(response)
    ```

    """

    model: str = Field(default=DEFAULT_YI_MODEL, description="The Yi model to use.")
    context_window: int = Field(
        default=yi_modelname_to_context_size(DEFAULT_YI_MODEL),
        description=LLMMetadata.model_fields["context_window"].description,
    )
    is_chat_model: bool = Field(
        default=True,
        description=LLMMetadata.model_fields["is_chat_model"].description,
    )
    is_function_calling_model: bool = Field(
        default=False,
        description=LLMMetadata.model_fields["is_function_calling_model"].description,
    )
    tokenizer: Union[Tokenizer, str, None] = Field(
        default=None,
        description=(
            "An instance of a tokenizer object that has an encode method, or the name"
            " of a tokenizer model from Hugging Face. If left as None, then this"
            " disables inference of max_tokens."
        ),
    )

    def __init__(
        self,
        model: str = DEFAULT_YI_MODEL,
        api_key: Optional[str] = None,
        api_base: Optional[str] = DEFAULT_YI_ENDPOINT,
        **kwargs: Any,
    ) -> None:
        api_key = api_key or os.environ.get("YI_API_KEY", None)
        super().__init__(
            model=model,
            api_key=api_key,
            api_base=api_base,
            **kwargs,
        )

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.max_tokens or -1,
            is_chat_model=self.is_chat_model,
            is_function_calling_model=self.is_function_calling_model,
            model_name=self.model,
        )

    @property
    def _tokenizer(self) -> Optional[Tokenizer]:
        if isinstance(self.tokenizer, str):
            return AutoTokenizer.from_pretrained(self.tokenizer)
        return self.tokenizer

    @classmethod
    def class_name(cls) -> str:
        return "Yi_LLM"

    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        """Complete the prompt."""
        if not formatted:
            prompt = self.completion_to_prompt(prompt)

        return super().complete(prompt, **kwargs)

    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        """Stream complete the prompt."""
        if not formatted:
            prompt = self.completion_to_prompt(prompt)

        return super().stream_complete(prompt, **kwargs)

    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        """Chat with the model."""
        if not self.metadata.is_chat_model:
            prompt = self.messages_to_prompt(messages)
            completion_response = self.complete(prompt, formatted=True, **kwargs)
            return completion_response_to_chat_response(completion_response)

        return super().chat(messages, **kwargs)

    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        if not self.metadata.is_chat_model:
            prompt = self.messages_to_prompt(messages)
            completion_response = self.stream_complete(prompt, formatted=True, **kwargs)
            return stream_completion_response_to_chat_response(completion_response)

        return super().stream_chat(messages, **kwargs)

    # -- Async methods --

    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        """Complete the prompt."""
        if not formatted:
            prompt = self.completion_to_prompt(prompt)

        return await super().acomplete(prompt, **kwargs)

    async def astream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        """Stream complete the prompt."""
        if not formatted:
            prompt = self.completion_to_prompt(prompt)

        return await super().astream_complete(prompt, **kwargs)

    async def achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        """Chat with the model."""
        if not self.metadata.is_chat_model:
            prompt = self.messages_to_prompt(messages)
            completion_response = await self.acomplete(prompt, formatted=True, **kwargs)
            return completion_response_to_chat_response(completion_response)

        return await super().achat(messages, **kwargs)

    async def astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        if not self.metadata.is_chat_model:
            prompt = self.messages_to_prompt(messages)
            completion_response = await self.astream_complete(
                prompt, formatted=True, **kwargs
            )
            return async_stream_completion_response_to_chat_response(
                completion_response
            )

        return await super().astream_chat(messages, **kwargs)

```
  
---|---  
###  complete #
```
complete(prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse

```

Complete the prompt.
Source code in `llama-index-integrations/llms/llama-index-llms-yi/llama_index/llms/yi/base.py`

| ```
def complete(
    self, prompt: str, formatted: bool = False, **kwargs: Any
) -> CompletionResponse:
    """Complete the prompt."""
    if not formatted:
        prompt = self.completion_to_prompt(prompt)

    return super().complete(prompt, **kwargs)

```
  
---|---  
###  stream_complete #
```
stream_complete(prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseGen

```

Stream complete the prompt.
Source code in `llama-index-integrations/llms/llama-index-llms-yi/llama_index/llms/yi/base.py`

| ```
def stream_complete(
    self, prompt: str, formatted: bool = False, **kwargs: Any
) -> CompletionResponseGen:
    """Stream complete the prompt."""
    if not formatted:
        prompt = self.completion_to_prompt(prompt)

    return super().stream_complete(prompt, **kwargs)

```
  
---|---  
###  chat #
```
chat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse

```

Chat with the model.
Source code in `llama-index-integrations/llms/llama-index-llms-yi/llama_index/llms/yi/base.py`

| ```
def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
    """Chat with the model."""
    if not self.metadata.is_chat_model:
        prompt = self.messages_to_prompt(messages)
        completion_response = self.complete(prompt, formatted=True, **kwargs)
        return completion_response_to_chat_response(completion_response)

    return super().chat(messages, **kwargs)

```
  
---|---  
###  acomplete `async` #
```
acomplete(prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse

```

Complete the prompt.
Source code in `llama-index-integrations/llms/llama-index-llms-yi/llama_index/llms/yi/base.py`

| ```
async def acomplete(
    self, prompt: str, formatted: bool = False, **kwargs: Any
) -> CompletionResponse:
    """Complete the prompt."""
    if not formatted:
        prompt = self.completion_to_prompt(prompt)

    return await super().acomplete(prompt, **kwargs)

```
  
---|---  
###  astream_complete `async` #
```
astream_complete(prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseAsyncGen

```

Stream complete the prompt.
Source code in `llama-index-integrations/llms/llama-index-llms-yi/llama_index/llms/yi/base.py`

| ```
async def astream_complete(
    self, prompt: str, formatted: bool = False, **kwargs: Any
) -> CompletionResponseAsyncGen:
    """Stream complete the prompt."""
    if not formatted:
        prompt = self.completion_to_prompt(prompt)

    return await super().astream_complete(prompt, **kwargs)

```
  
---|---  
###  achat `async` #
```
achat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse

```

Chat with the model.
Source code in `llama-index-integrations/llms/llama-index-llms-yi/llama_index/llms/yi/base.py`

| ```
async def achat(
    self, messages: Sequence[ChatMessage], **kwargs: Any
) -> ChatResponse:
    """Chat with the model."""
    if not self.metadata.is_chat_model:
        prompt = self.messages_to_prompt(messages)
        completion_response = await self.acomplete(prompt, formatted=True, **kwargs)
        return completion_response_to_chat_response(completion_response)

    return await super().achat(messages, **kwargs)

```
  
---|---
