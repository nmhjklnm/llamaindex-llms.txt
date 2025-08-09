# Lmstudio
##  LMStudio #
Bases: `CustomLLM`
Source code in `llama-index-integrations/llms/llama-index-llms-lmstudio/llama_index/llms/lmstudio/base.py`

| ```
class LMStudio(CustomLLM):
    base_url: str = Field(
        default="http://localhost:1234/v1",
        description="Base url the model is hosted under.",
    )

    context_window: int = Field(
        default=DEFAULT_CONTEXT_WINDOW,
        description="The maximum number of context tokens for the model.",
        gt=0,
    )

    model_name: str = Field(description="The model to use.")

    request_timeout: float = Field(
        default=DEFAULT_REQUEST_TIMEOUT,
        description="The timeout for making http request in seconds to LM Studio API server.",
    )
    num_output: int = Field(
        default=DEFAULT_NUM_OUTPUTS,
        description=LLMMetadata.model_fields["num_output"].description,
    )

    is_chat_model: bool = Field(
        default=True,
        description=(
            "LM Studio API supports chat."
            + LLMMetadata.model_fields["is_chat_model"].description
        ),
    )

    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        description=("The temperature to use for sampling."),
        ge=0.0,
        le=1.0,
    )

    timeout: float = Field(
        default=120, description=("The timeout to use in seconds."), ge=0
    )

    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description=("Additional kwargs to pass to the model.")
    )

    def _create_payload_from_messages(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> Dict[str, Any]:
        return {
            "model": self.model_name,
            "messages": [
                {
                    "role": message.role.value,
                    "content": message.content,
                    **(
                        message.additional_kwargs
                        if message.additional_kwargs is not None
                        else {}
                    ),
                }
                for message in messages
            ],
            "options": self._model_kwargs,
            "stream": False,
            **kwargs,
        }

    def _create_chat_response_from_http_response(
        self, response: httpx.Response
    ) -> ChatResponse:
        raw = response.json()
        message = raw["choices"][0]["message"]
        return ChatResponse(
            message=ChatMessage(
                content=message.get("content"),
                role=MessageRole(message.get("role")),
                additional_kwargs=get_additional_kwargs(message, ("content", "role")),
            ),
            raw=raw,
            additional_kwargs=get_additional_kwargs(raw, ("choices",)),
        )

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        payload = self._create_payload_from_messages(messages, **kwargs)
        with httpx.Client(timeout=Timeout(self.request_timeout)) as client:
            response = client.post(
                url=f"{self.base_url}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            return self._create_chat_response_from_http_response(response)

    @llm_chat_callback()
    async def achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        payload = self._create_payload_from_messages(messages, **kwargs)
        async with httpx.AsyncClient(timeout=Timeout(self.request_timeout)) as client:
            response = await client.post(
                url=f"{self.base_url}/chat/completions",
                json=payload,
            )
            response.raise_for_status()
            return self._create_chat_response_from_http_response(response)

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        complete_fn = chat_to_completion_decorator(self.chat)
        return complete_fn(prompt, **kwargs)

    @llm_completion_callback()
    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        acomplete_fn = achat_to_completion_decorator(self.achat)
        return await acomplete_fn(prompt, **kwargs)

    @llm_chat_callback()
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        payload = self._create_payload_from_messages(messages, stream=True, **kwargs)

        with httpx.Client(timeout=Timeout(self.request_timeout)) as client:
            with client.stream(
                method="POST",
                url=f"{self.base_url}/chat/completions",
                json=payload,
            ) as response:
                response.raise_for_status()
                text = ""
                for line in response.iter_lines():
                    if line:
                        line = line.strip()
                        if isinstance(line, bytes):
                            line = line.decode("utf-8")

                        if line.startswith("data: [DONE]"):
                            break

                        # Slice the line to remove the "data: " prefix
                        chunk = json.loads(line[5:])

                        delta = chunk["choices"][0].get("delta")

                        role = delta.get("role") or MessageRole.ASSISTANT
                        content_delta = delta.get("content") or ""
                        text += content_delta

                        yield ChatResponse(
                            message=ChatMessage(
                                content=text,
                                role=MessageRole(role),
                                additional_kwargs=get_additional_kwargs(
                                    chunk, ("choices",)
                                ),
                            ),
                            delta=content_delta,
                            raw=chunk,
                            additional_kwargs=get_additional_kwargs(
                                chunk, ("choices",)
                            ),
                        )

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        stream_complete_fn = stream_chat_to_completion_decorator(self.stream_chat)
        return stream_complete_fn(prompt, **kwargs)

    @llm_completion_callback()
    async def astream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        astream_complete_fn = astream_chat_to_completion_decorator(self.astream_chat)
        return await astream_complete_fn(prompt, **kwargs)

    @property
    def metadata(self) -> LLMMetadata:
        """LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.num_output,
            model_name=self.model_name,
            is_chat_model=self.is_chat_model,
        )

    @property
    def _model_kwargs(self) -> Dict[str, Any]:
        base_kwargs = {
            "temperature": self.temperature,
            "num_ctx": self.context_window,
        }
        return {
            **base_kwargs,
            **self.additional_kwargs,
        }

```
  
---|---  
###  metadata `property` #
```
metadata: LLMMetadata

```

LLM metadata.
