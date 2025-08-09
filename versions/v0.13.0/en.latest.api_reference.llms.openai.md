# Openai
##  OpenAI #
Bases: `FunctionCallingLLM`
OpenAI LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model` |  `str` |  name of the OpenAI model to use. |  `DEFAULT_OPENAI_MODEL`  
`temperature` |  `float` |  a float from 0 to 1 controlling randomness in generation; higher will lead to more creative, less deterministic responses. |  `DEFAULT_TEMPERATURE`  
`max_tokens` |  `Optional[int]` |  the maximum number of tokens to generate. |  `None`  
`additional_kwargs` |  `Optional[Dict[str, Any]]` |  Add additional parameters to OpenAI request body. |  `None`  
`max_retries` |  `int` |  How many times to retry the API call if it fails. |  `3`  
`timeout` |  `float` |  How long to wait, in seconds, for an API call before failing. |  `60.0`  
`reuse_client` |  `bool` |  Reuse the OpenAI client between requests. When doing anything with large volumes of async API calls, setting this to false can improve stability. |  `True`  
`api_key` |  `Optional[str]` |  Your OpenAI api key |  `None`  
`api_base` |  `Optional[str]` |  The base URL of the API to call |  `None`  
`api_version` |  `Optional[str]` |  the version of the API to call |  `None`  
`callback_manager` |  `Optional[CallbackManager]` |  the callback manager is used for observability. |  `None`  
`default_headers` |  `Optional[Dict[str, str]]` |  override the default headers for API requests. |  `None`  
`http_client` |  `Optional[Client]` |  pass in your own httpx.Client instance. |  `None`  
`async_http_client` |  `Optional[AsyncClient]` |  pass in your own httpx.AsyncClient instance. |  `None`  
Examples:
`pip install llama-index-llms-openai`
```
import os
import openai

os.environ["OPENAI_API_KEY"] = "sk-..."
openai.api_key = os.environ["OPENAI_API_KEY"]

from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo")

stream = llm.stream("Hi, write a short story")

for r in stream:
    print(r.delta, end="")

```

Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/base.py`

| ```
class OpenAI(FunctionCallingLLM):
    """
    OpenAI LLM.

    Args:
        model: name of the OpenAI model to use.
        temperature: a float from 0 to 1 controlling randomness in generation; higher will lead to more creative, less deterministic responses.
        max_tokens: the maximum number of tokens to generate.
        additional_kwargs: Add additional parameters to OpenAI request body.
        max_retries: How many times to retry the API call if it fails.
        timeout: How long to wait, in seconds, for an API call before failing.
        reuse_client: Reuse the OpenAI client between requests. When doing anything with large volumes of async API calls, setting this to false can improve stability.
        api_key: Your OpenAI api key
        api_base: The base URL of the API to call
        api_version: the version of the API to call
        callback_manager: the callback manager is used for observability.
        default_headers: override the default headers for API requests.
        http_client: pass in your own httpx.Client instance.
        async_http_client: pass in your own httpx.AsyncClient instance.

    Examples:
        `pip install llama-index-llms-openai`

    ```python
        import os
        import openai

        os.environ["OPENAI_API_KEY"] = "sk-..."
        openai.api_key = os.environ["OPENAI_API_KEY"]

        from llama_index.llms.openai import OpenAI

        llm = OpenAI(model="gpt-3.5-turbo")

        stream = llm.stream("Hi, write a short story")

        for r in stream:
            print(r.delta, end="")
    ```
    """

    model: str = Field(
        default=DEFAULT_OPENAI_MODEL, description="The OpenAI model to use."
    )
    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        description="The temperature to use during generation.",
        ge=0.0,
        le=2.0,
    )
    max_tokens: Optional[int] = Field(
        description="The maximum number of tokens to generate.",
        default=None,
        gt=0,
    )
    logprobs: Optional[bool] = Field(
        description="Whether to return logprobs per token.",
        default=None,
    )
    top_logprobs: int = Field(
        description="The number of top token log probs to return.",
        default=0,
        ge=0,
        le=20,
    )
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Additional kwargs for the OpenAI API."
    )
    max_retries: int = Field(
        default=3,
        description="The maximum number of API retries.",
        ge=0,
    )
    timeout: float = Field(
        default=60.0,
        description="The timeout, in seconds, for API requests.",
        ge=0,
    )
    default_headers: Optional[Dict[str, str]] = Field(
        default=None, description="The default headers for API requests."
    )
    reuse_client: bool = Field(
        default=True,
        description=(
            "Reuse the OpenAI client between requests. When doing anything with large "
            "volumes of async API calls, setting this to false can improve stability."
        ),
    )

    api_key: Optional[str] = Field(default=None, description="The OpenAI API key.")
    api_base: Optional[str] = Field(
        default=None, description="The base URL for OpenAI API."
    )
    api_version: Optional[str] = Field(
        default=None, description="The API version for OpenAI API."
    )
    strict: bool = Field(
        default=False,
        description="Whether to use strict mode for invoking tools/using schemas.",
    )
    reasoning_effort: Optional[Literal["low", "medium", "high"]] = Field(
        default=None,
        description="The effort to use for reasoning models.",
    )
    modalities: Optional[List[str]] = Field(
        default=None,
        description="The output modalities to use for the model.",
    )
    audio_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="The audio configuration to use for the model.",
    )

    _client: Optional[SyncOpenAI] = PrivateAttr()
    _aclient: Optional[AsyncOpenAI] = PrivateAttr()
    _http_client: Optional[httpx.Client] = PrivateAttr()
    _async_http_client: Optional[httpx.AsyncClient] = PrivateAttr()

    def __init__(
        self,
        model: str = DEFAULT_OPENAI_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: Optional[int] = None,
        additional_kwargs: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        reuse_client: bool = True,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        callback_manager: Optional[CallbackManager] = None,
        default_headers: Optional[Dict[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
        async_http_client: Optional[httpx.AsyncClient] = None,
        openai_client: Optional[SyncOpenAI] = None,
        async_openai_client: Optional[AsyncOpenAI] = None,
        # base class
        system_prompt: Optional[str] = None,
        messages_to_prompt: Optional[Callable[[Sequence[ChatMessage]], str]] = None,
        completion_to_prompt: Optional[Callable[[str], str]] = None,
        pydantic_program_mode: PydanticProgramMode = PydanticProgramMode.DEFAULT,
        output_parser: Optional[BaseOutputParser] = None,
        strict: bool = False,
        reasoning_effort: Optional[Literal["low", "medium", "high"]] = None,
        modalities: Optional[List[str]] = None,
        audio_config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        # TODO: Support deprecated max_new_tokens
        if "max_new_tokens" in kwargs:
            max_tokens = kwargs["max_new_tokens"]
            del kwargs["max_new_tokens"]

        additional_kwargs = additional_kwargs or {}

        api_key, api_base, api_version = resolve_openai_credentials(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
        )

        # TODO: Temp forced to 1.0 for o1
        if model in O1_MODELS:
            temperature = 1.0

        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            additional_kwargs=additional_kwargs,
            max_retries=max_retries,
            callback_manager=callback_manager,
            api_key=api_key,
            api_version=api_version,
            api_base=api_base,
            timeout=timeout,
            reuse_client=reuse_client,
            default_headers=default_headers,
            system_prompt=system_prompt,
            messages_to_prompt=messages_to_prompt,
            completion_to_prompt=completion_to_prompt,
            pydantic_program_mode=pydantic_program_mode,
            output_parser=output_parser,
            strict=strict,
            reasoning_effort=reasoning_effort,
            modalities=modalities,
            audio_config=audio_config,
            **kwargs,
        )

        self._client = openai_client
        self._aclient = async_openai_client
        self._http_client = http_client
        self._async_http_client = async_http_client

    def _get_client(self) -> SyncOpenAI:
        if not self.reuse_client:
            return SyncOpenAI(**self._get_credential_kwargs())

        if self._client is None:
            self._client = SyncOpenAI(**self._get_credential_kwargs())
        return self._client

    def _get_aclient(self) -> AsyncOpenAI:
        if not self.reuse_client:
            return AsyncOpenAI(**self._get_credential_kwargs(is_async=True))

        if self._aclient is None:
            self._aclient = AsyncOpenAI(**self._get_credential_kwargs(is_async=True))
        return self._aclient

    def _get_model_name(self) -> str:
        model_name = self.model
        if "ft-" in model_name:  # legacy fine-tuning
            model_name = model_name.split(":")[0]
        elif model_name.startswith("ft:"):
            model_name = model_name.split(":")[1]
        return model_name

    @classmethod
    def class_name(cls) -> str:
        return "openai_llm"

    @property
    def _tokenizer(self) -> Optional[Tokenizer]:
        """
        Get a tokenizer for this model, or None if a tokenizing method is unknown.

        OpenAI can do this using the tiktoken package, subclasses may not have
        this convenience.
        """
        return tiktoken.encoding_for_model(self._get_model_name())

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=openai_modelname_to_contextsize(self._get_model_name()),
            num_output=self.max_tokens or -1,
            is_chat_model=is_chat_model(model=self._get_model_name()),
            is_function_calling_model=is_function_calling_model(
                model=self._get_model_name()
            ),
            model_name=self.model,
            # TODO: Temp for O1 beta
            system_role=MessageRole.USER
            if self.model in O1_MODELS
            else MessageRole.SYSTEM,
        )

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        if self._use_chat_completions(kwargs):
            chat_fn = self._chat
        else:
            chat_fn = completion_to_chat_decorator(self._complete)
        return chat_fn(messages, **kwargs)

    @llm_chat_callback()
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        if self._use_chat_completions(kwargs):
            stream_chat_fn = self._stream_chat
        else:
            stream_chat_fn = stream_completion_to_chat_decorator(self._stream_complete)
        return stream_chat_fn(messages, **kwargs)

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        if self.modalities and "audio" in self.modalities:
            raise ValueError(
                "Audio is not supported for completion. Use chat/achat instead."
            )

        if self._use_chat_completions(kwargs):
            complete_fn = chat_to_completion_decorator(self._chat)
        else:
            complete_fn = self._complete
        return complete_fn(prompt, **kwargs)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        if self._use_chat_completions(kwargs):
            stream_complete_fn = stream_chat_to_completion_decorator(self._stream_chat)
        else:
            stream_complete_fn = self._stream_complete
        return stream_complete_fn(prompt, **kwargs)

    def _use_chat_completions(self, kwargs: Dict[str, Any]) -> bool:
        if "use_chat_completions" in kwargs:
            return kwargs["use_chat_completions"]
        return self.metadata.is_chat_model

    def _get_credential_kwargs(self, is_async: bool = False) -> Dict[str, Any]:
        return {
            "api_key": self.api_key,
            "base_url": self.api_base,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "default_headers": self.default_headers,
            "http_client": self._async_http_client if is_async else self._http_client,
        }

    def _get_model_kwargs(self, **kwargs: Any) -> Dict[str, Any]:
        base_kwargs = {"model": self.model, "temperature": self.temperature, **kwargs}
        if self.max_tokens is not None:
            # If max_tokens is None, don't include in the payload:
            # https://platform.openai.com/docs/api-reference/chat
            # https://platform.openai.com/docs/api-reference/completions
            base_kwargs["max_tokens"] = self.max_tokens
        if self.logprobs is not None and self.logprobs is True:
            if self.metadata.is_chat_model:
                base_kwargs["logprobs"] = self.logprobs
                base_kwargs["top_logprobs"] = self.top_logprobs
            else:
                base_kwargs["logprobs"] = self.top_logprobs  # int in this case

        # can't send stream_options to the API when not streaming
        all_kwargs = {**base_kwargs, **self.additional_kwargs}
        if "stream" not in all_kwargs and "stream_options" in all_kwargs:
            del all_kwargs["stream_options"]
        if self.model in O1_MODELS and base_kwargs.get("max_tokens") is not None:
            # O1 models use max_completion_tokens instead of max_tokens
            all_kwargs["max_completion_tokens"] = all_kwargs.get(
                "max_completion_tokens", all_kwargs["max_tokens"]
            )
            all_kwargs.pop("max_tokens", None)
        if self.model in O1_MODELS and self.reasoning_effort is not None:
            # O1 models support reasoning_effort of low, medium, high
            all_kwargs["reasoning_effort"] = self.reasoning_effort

        if self.modalities is not None:
            all_kwargs["modalities"] = self.modalities
        if self.audio_config is not None:
            all_kwargs["audio"] = self.audio_config

        return all_kwargs

    @llm_retry_decorator
    def _chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        client = self._get_client()
        message_dicts = to_openai_message_dicts(
            messages,
            model=self.model,
        )

        if self.reuse_client:
            response = client.chat.completions.create(
                messages=message_dicts,
                stream=False,
                **self._get_model_kwargs(**kwargs),
            )
        else:
            with client:
                response = client.chat.completions.create(
                    messages=message_dicts,
                    stream=False,
                    **self._get_model_kwargs(**kwargs),
                )

        openai_message = response.choices[0].message
        message = from_openai_message(
            openai_message, modalities=self.modalities or ["text"]
        )
        openai_token_logprobs = response.choices[0].logprobs
        logprobs = None
        if openai_token_logprobs and openai_token_logprobs.content:
            logprobs = from_openai_token_logprobs(openai_token_logprobs.content)

        return ChatResponse(
            message=message,
            raw=response,
            logprobs=logprobs,
            additional_kwargs=self._get_response_token_counts(response),
        )

    @llm_retry_decorator
    def _stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        if self.modalities and "audio" in self.modalities:
            raise ValueError("Audio is not supported for chat streaming")

        client = self._get_client()
        message_dicts = to_openai_message_dicts(
            messages,
            model=self.model,
        )

        def gen() -> ChatResponseGen:
            content = ""
            tool_calls: List[ChoiceDeltaToolCall] = []

            is_function = False
            for response in client.chat.completions.create(
                messages=message_dicts,
                **self._get_model_kwargs(stream=True, **kwargs),
            ):
                response = cast(ChatCompletionChunk, response)
                if len(response.choices) > 0:
                    delta = response.choices[0].delta
                else:
                    if isinstance(client, AzureOpenAI):
                        continue
                    else:
                        delta = ChoiceDelta()

                if delta is None:
                    continue

                # check if this chunk is the start of a function call
                if delta.tool_calls:
                    is_function = True

                # update using deltas
                role = delta.role or MessageRole.ASSISTANT
                content_delta = delta.content or ""
                content += content_delta

                additional_kwargs = {}
                if is_function:
                    tool_calls = update_tool_calls(tool_calls, delta.tool_calls)
                    if tool_calls:
                        additional_kwargs["tool_calls"] = tool_calls

                yield ChatResponse(
                    message=ChatMessage(
                        role=role,
                        content=content,
                        additional_kwargs=additional_kwargs,
                    ),
                    delta=content_delta,
                    raw=response,
                    additional_kwargs=self._get_response_token_counts(response),
                )

        return gen()

    @llm_retry_decorator
    def _complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        client = self._get_client()
        all_kwargs = self._get_model_kwargs(**kwargs)
        self._update_max_tokens(all_kwargs, prompt)

        if self.reuse_client:
            response = client.completions.create(
                prompt=prompt,
                stream=False,
                **all_kwargs,
            )
        else:
            with client:
                response = client.completions.create(
                    prompt=prompt,
                    stream=False,
                    **all_kwargs,
                )
        text = response.choices[0].text

        openai_completion_logprobs = response.choices[0].logprobs
        logprobs = None
        if openai_completion_logprobs:
            logprobs = from_openai_completion_logprobs(openai_completion_logprobs)

        return CompletionResponse(
            text=text,
            raw=response,
            logprobs=logprobs,
            additional_kwargs=self._get_response_token_counts(response),
        )

    @llm_retry_decorator
    def _stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        client = self._get_client()
        all_kwargs = self._get_model_kwargs(stream=True, **kwargs)
        self._update_max_tokens(all_kwargs, prompt)

        def gen() -> CompletionResponseGen:
            text = ""
            for response in client.completions.create(
                prompt=prompt,
                **all_kwargs,
            ):
                if len(response.choices) > 0:
                    delta = response.choices[0].text
                    if delta is None:
                        delta = ""
                else:
                    delta = ""
                text += delta
                yield CompletionResponse(
                    delta=delta,
                    text=text,
                    raw=response,
                    additional_kwargs=self._get_response_token_counts(response),
                )

        return gen()

    def _update_max_tokens(self, all_kwargs: Dict[str, Any], prompt: str) -> None:
        """Infer max_tokens for the payload, if possible."""
        if self.max_tokens is not None or self._tokenizer is None:
            return
        # NOTE: non-chat completion endpoint requires max_tokens to be set
        num_tokens = len(self._tokenizer.encode(prompt))
        max_tokens = self.metadata.context_window - num_tokens
        if max_tokens <= 0:
            raise ValueError(
                f"The prompt has {num_tokens} tokens, which is too long for"
                " the model. Please use a prompt that fits within"
                f" {self.metadata.context_window} tokens."
            )
        all_kwargs["max_tokens"] = max_tokens

    def _get_response_token_counts(self, raw_response: Any) -> dict:
        """Get the token usage reported by the response."""
        if hasattr(raw_response, "usage"):
            try:
                prompt_tokens = raw_response.usage.prompt_tokens
                completion_tokens = raw_response.usage.completion_tokens
                total_tokens = raw_response.usage.total_tokens
            except AttributeError:
                return {}
        elif isinstance(raw_response, dict):
            usage = raw_response.get("usage", {})
            # NOTE: other model providers that use the OpenAI client may not report usage
            if usage is None:
                return {}
            # Backwards compatibility with old dict type
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)
        else:
            return {}

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        }

    # ===== Async Endpoints =====
    @llm_chat_callback()
    async def achat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        achat_fn: Callable[..., Awaitable[ChatResponse]]
        if self._use_chat_completions(kwargs):
            achat_fn = self._achat
        else:
            achat_fn = acompletion_to_chat_decorator(self._acomplete)
        return await achat_fn(messages, **kwargs)

    @llm_chat_callback()
    async def astream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponseAsyncGen:
        astream_chat_fn: Callable[..., Awaitable[ChatResponseAsyncGen]]
        if self._use_chat_completions(kwargs):
            astream_chat_fn = self._astream_chat
        else:
            astream_chat_fn = astream_completion_to_chat_decorator(
                self._astream_complete
            )
        return await astream_chat_fn(messages, **kwargs)

    @llm_completion_callback()
    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        if self.modalities and "audio" in self.modalities:
            raise ValueError(
                "Audio is not supported for completion. Use chat/achat instead."
            )

        if self._use_chat_completions(kwargs):
            acomplete_fn = achat_to_completion_decorator(self._achat)
        else:
            acomplete_fn = self._acomplete
        return await acomplete_fn(prompt, **kwargs)

    @llm_completion_callback()
    async def astream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        if self._use_chat_completions(kwargs):
            astream_complete_fn = astream_chat_to_completion_decorator(
                self._astream_chat
            )
        else:
            astream_complete_fn = self._astream_complete
        return await astream_complete_fn(prompt, **kwargs)

    @llm_retry_decorator
    async def _achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        aclient = self._get_aclient()
        message_dicts = to_openai_message_dicts(
            messages,
            model=self.model,
        )

        if self.reuse_client:
            response = await aclient.chat.completions.create(
                messages=message_dicts, stream=False, **self._get_model_kwargs(**kwargs)
            )
        else:
            async with aclient:
                response = await aclient.chat.completions.create(
                    messages=message_dicts,
                    stream=False,
                    **self._get_model_kwargs(**kwargs),
                )

        openai_message = response.choices[0].message
        message = from_openai_message(
            openai_message, modalities=self.modalities or ["text"]
        )
        openai_token_logprobs = response.choices[0].logprobs
        logprobs = None
        if openai_token_logprobs and openai_token_logprobs.content:
            logprobs = from_openai_token_logprobs(openai_token_logprobs.content)

        return ChatResponse(
            message=message,
            raw=response,
            logprobs=logprobs,
            additional_kwargs=self._get_response_token_counts(response),
        )

    @llm_retry_decorator
    async def _astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        if self.modalities and "audio" in self.modalities:
            raise ValueError("Audio is not supported for chat streaming")

        aclient = self._get_aclient()
        message_dicts = to_openai_message_dicts(
            messages,
            model=self.model,
        )

        async def gen() -> ChatResponseAsyncGen:
            content = ""
            tool_calls: List[ChoiceDeltaToolCall] = []

            is_function = False
            first_chat_chunk = True
            async for response in await aclient.chat.completions.create(
                messages=message_dicts,
                **self._get_model_kwargs(stream=True, **kwargs),
            ):
                response = cast(ChatCompletionChunk, response)
                if len(response.choices) > 0:
                    # check if the first chunk has neither content nor tool_calls
                    # this happens when 1106 models end up calling multiple tools
                    if (
                        first_chat_chunk
                        and response.choices[0].delta.content is None
                        and response.choices[0].delta.tool_calls is None
                    ):
                        first_chat_chunk = False
                        continue
                    delta = response.choices[0].delta
                else:
                    if isinstance(aclient, AsyncAzureOpenAI):
                        continue
                    else:
                        delta = ChoiceDelta()
                first_chat_chunk = False

                if delta is None:
                    continue

                # check if this chunk is the start of a function call
                if delta.tool_calls:
                    is_function = True

                # update using deltas
                role = delta.role or MessageRole.ASSISTANT
                content_delta = delta.content or ""
                content += content_delta

                additional_kwargs = {}
                if is_function:
                    tool_calls = update_tool_calls(tool_calls, delta.tool_calls)
                    if tool_calls:
                        additional_kwargs["tool_calls"] = tool_calls

                yield ChatResponse(
                    message=ChatMessage(
                        role=role,
                        content=content,
                        additional_kwargs=additional_kwargs,
                    ),
                    delta=content_delta,
                    raw=response,
                    additional_kwargs=self._get_response_token_counts(response),
                )

        return gen()

    @llm_retry_decorator
    async def _acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        aclient = self._get_aclient()
        all_kwargs = self._get_model_kwargs(**kwargs)
        self._update_max_tokens(all_kwargs, prompt)

        if self.reuse_client:
            response = await aclient.completions.create(
                prompt=prompt,
                stream=False,
                **all_kwargs,
            )
        else:
            async with aclient:
                response = await aclient.completions.create(
                    prompt=prompt,
                    stream=False,
                    **all_kwargs,
                )

        text = response.choices[0].text
        openai_completion_logprobs = response.choices[0].logprobs
        logprobs = None
        if openai_completion_logprobs:
            logprobs = from_openai_completion_logprobs(openai_completion_logprobs)

        return CompletionResponse(
            text=text,
            raw=response,
            logprobs=logprobs,
            additional_kwargs=self._get_response_token_counts(response),
        )

    @llm_retry_decorator
    async def _astream_complete(
        self, prompt: str, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        aclient = self._get_aclient()
        all_kwargs = self._get_model_kwargs(stream=True, **kwargs)
        self._update_max_tokens(all_kwargs, prompt)

        async def gen() -> CompletionResponseAsyncGen:
            text = ""
            async for response in await aclient.completions.create(
                prompt=prompt,
                **all_kwargs,
            ):
                if len(response.choices) > 0:
                    delta = response.choices[0].text
                    if delta is None:
                        delta = ""
                else:
                    delta = ""
                text += delta
                yield CompletionResponse(
                    delta=delta,
                    text=text,
                    raw=response,
                    additional_kwargs=self._get_response_token_counts(response),
                )

        return gen()

    def _prepare_chat_with_tools(
        self,
        tools: Sequence["BaseTool"],
        user_msg: Optional[Union[str, ChatMessage]] = None,
        chat_history: Optional[List[ChatMessage]] = None,
        verbose: bool = False,
        allow_parallel_tool_calls: bool = False,
        tool_required: bool = False,
        tool_choice: Optional[Union[str, dict]] = None,
        strict: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Predict and call the tool."""
        tool_specs = [
            tool.metadata.to_openai_tool(skip_length_check=True) for tool in tools
        ]

        # if strict is passed in, use, else default to the class-level attribute, else default to True`
        if strict is not None:
            strict = strict
        else:
            strict = self.strict

        if self.metadata.is_function_calling_model:
            for tool_spec in tool_specs:
                if tool_spec["type"] == "function":
                    tool_spec["function"]["strict"] = strict
                    # in current openai 1.40.0 it is always false.
                    tool_spec["function"]["parameters"]["additionalProperties"] = False

        if isinstance(user_msg, str):
            user_msg = ChatMessage(role=MessageRole.USER, content=user_msg)

        messages = chat_history or []
        if user_msg:
            messages.append(user_msg)

        return {
            "messages": messages,
            "tools": tool_specs or None,
            "tool_choice": resolve_tool_choice(tool_choice, tool_required)
            if tool_specs
            else None,
            **kwargs,
        }

    def _validate_chat_with_tools_response(
        self,
        response: ChatResponse,
        tools: Sequence["BaseTool"],
        allow_parallel_tool_calls: bool = False,
        **kwargs: Any,
    ) -> ChatResponse:
        """Validate the response from chat_with_tools."""
        if not allow_parallel_tool_calls:
            force_single_tool_call(response)
        return response

    def get_tool_calls_from_response(
        self,
        response: "ChatResponse",
        error_on_no_tool_call: bool = True,
        **kwargs: Any,
    ) -> List[ToolSelection]:
        """Predict and call the tool."""
        tool_calls = response.message.additional_kwargs.get("tool_calls", [])

        if len(tool_calls) < 1:
            if error_on_no_tool_call:
                raise ValueError(
                    f"Expected at least one tool call, but got {len(tool_calls)} tool calls."
                )
            else:
                return []

        tool_selections = []
        for tool_call in tool_calls:
            if not isinstance(tool_call, get_args(OpenAIToolCall)):
                raise ValueError("Invalid tool_call object")
            if tool_call.type != "function":
                raise ValueError("Invalid tool type. Unsupported by OpenAI")

            # this should handle both complete and partial jsons
            try:
                argument_dict = parse_partial_json(tool_call.function.arguments)
            except (ValueError, TypeError, JSONDecodeError):
                argument_dict = {}

            tool_selections.append(
                ToolSelection(
                    tool_id=tool_call.id,
                    tool_name=tool_call.function.name,
                    tool_kwargs=argument_dict,
                )
            )

        return tool_selections

    def _prepare_schema(
        self, llm_kwargs: Optional[Dict[str, Any]], output_cls: Type[Model]
    ) -> Dict[str, Any]:
        from openai.resources.beta.chat.completions import _type_to_response_format

        llm_kwargs = llm_kwargs or {}
        llm_kwargs["response_format"] = _type_to_response_format(output_cls)
        if "tool_choice" in llm_kwargs:
            del llm_kwargs["tool_choice"]
        return llm_kwargs

    def _should_use_structure_outputs(self):
        return (
            self.pydantic_program_mode == PydanticProgramMode.DEFAULT
            and is_json_schema_supported(self.model)
        )

    @dispatcher.span
    def structured_predict(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> Model:
        """Structured predict."""
        llm_kwargs = llm_kwargs or {}

        if self._should_use_structure_outputs():
            messages = self._extend_messages(prompt.format_messages(**prompt_args))
            llm_kwargs = self._prepare_schema(llm_kwargs, output_cls)
            response = self.chat(messages, **llm_kwargs)
            return output_cls.model_validate_json(str(response.message.content))

        # when uses function calling to extract structured outputs
        # here we force tool_choice to be required
        llm_kwargs["tool_choice"] = (
            "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
        )
        return super().structured_predict(
            output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
        )

    @dispatcher.span
    async def astructured_predict(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> Model:
        """Structured predict."""
        llm_kwargs = llm_kwargs or {}

        if self._should_use_structure_outputs():
            messages = self._extend_messages(prompt.format_messages(**prompt_args))
            llm_kwargs = self._prepare_schema(llm_kwargs, output_cls)
            response = await self.achat(messages, **llm_kwargs)
            return output_cls.model_validate_json(str(response.message.content))

        # when uses function calling to extract structured outputs
        # here we force tool_choice to be required
        llm_kwargs["tool_choice"] = (
            "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
        )
        return await super().astructured_predict(
            output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
        )

    def _structured_stream_call(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> Generator[
        Union[Model, List[Model], "FlexibleModel", List["FlexibleModel"]], None, None
    ]:
        if self._should_use_structure_outputs():
            from llama_index.core.program.streaming_utils import (
                process_streaming_content_incremental,
            )

            messages = self._extend_messages(prompt.format_messages(**prompt_args))
            llm_kwargs = self._prepare_schema(llm_kwargs, output_cls)
            curr = None
            for response in self.stream_chat(messages, **llm_kwargs):
                curr = process_streaming_content_incremental(response, output_cls, curr)
                yield curr
        else:
            llm_kwargs["tool_choice"] = (
                "required"
                if "tool_choice" not in llm_kwargs
                else llm_kwargs["tool_choice"]
            )
            yield from super()._structured_stream_call(
                output_cls, prompt, llm_kwargs, **prompt_args
            )

    async def _structured_astream_call(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> AsyncGenerator[
        Union[Model, List[Model], "FlexibleModel", List["FlexibleModel"]], None
    ]:
        if self._should_use_structure_outputs():

            async def gen(
                llm_kwargs=llm_kwargs,
            ) -> AsyncGenerator[
                Union[Model, List[Model], FlexibleModel, List[FlexibleModel]], None
            ]:
                from llama_index.core.program.streaming_utils import (
                    process_streaming_content_incremental,
                )

                messages = self._extend_messages(prompt.format_messages(**prompt_args))
                llm_kwargs = self._prepare_schema(llm_kwargs, output_cls)
                curr = None
                async for response in await self.astream_chat(messages, **llm_kwargs):
                    curr = process_streaming_content_incremental(
                        response, output_cls, curr
                    )
                    yield curr

            return gen()
        else:
            llm_kwargs["tool_choice"] = (
                "required"
                if "tool_choice" not in llm_kwargs
                else llm_kwargs["tool_choice"]
            )
            return await super()._structured_astream_call(
                output_cls, prompt, llm_kwargs, **prompt_args
            )

    @dispatcher.span
    def stream_structured_predict(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> Generator[Union[Model, FlexibleModel], None, None]:
        """Stream structured predict."""
        llm_kwargs = llm_kwargs or {}

        return super().stream_structured_predict(
            output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
        )

    @dispatcher.span
    async def astream_structured_predict(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> AsyncGenerator[Union[Model, FlexibleModel], None]:
        """Stream structured predict."""
        llm_kwargs = llm_kwargs or {}
        return await super().astream_structured_predict(
            output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
        )

```
  
---|---  
###  get_tool_calls_from_response #
```
get_tool_calls_from_response(response: ChatResponse, error_on_no_tool_call: bool = True, **kwargs: Any) -> List[ToolSelection]

```

Predict and call the tool.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/base.py`

| ```
def get_tool_calls_from_response(
    self,
    response: "ChatResponse",
    error_on_no_tool_call: bool = True,
    **kwargs: Any,
) -> List[ToolSelection]:
    """Predict and call the tool."""
    tool_calls = response.message.additional_kwargs.get("tool_calls", [])

    if len(tool_calls) < 1:
        if error_on_no_tool_call:
            raise ValueError(
                f"Expected at least one tool call, but got {len(tool_calls)} tool calls."
            )
        else:
            return []

    tool_selections = []
    for tool_call in tool_calls:
        if not isinstance(tool_call, get_args(OpenAIToolCall)):
            raise ValueError("Invalid tool_call object")
        if tool_call.type != "function":
            raise ValueError("Invalid tool type. Unsupported by OpenAI")

        # this should handle both complete and partial jsons
        try:
            argument_dict = parse_partial_json(tool_call.function.arguments)
        except (ValueError, TypeError, JSONDecodeError):
            argument_dict = {}

        tool_selections.append(
            ToolSelection(
                tool_id=tool_call.id,
                tool_name=tool_call.function.name,
                tool_kwargs=argument_dict,
            )
        )

    return tool_selections

```
  
---|---  
###  structured_predict #
```
structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Model

```

Structured predict.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/base.py`

| ```
@dispatcher.span
def structured_predict(
    self,
    output_cls: Type[Model],
    prompt: PromptTemplate,
    llm_kwargs: Optional[Dict[str, Any]] = None,
    **prompt_args: Any,
) -> Model:
    """Structured predict."""
    llm_kwargs = llm_kwargs or {}

    if self._should_use_structure_outputs():
        messages = self._extend_messages(prompt.format_messages(**prompt_args))
        llm_kwargs = self._prepare_schema(llm_kwargs, output_cls)
        response = self.chat(messages, **llm_kwargs)
        return output_cls.model_validate_json(str(response.message.content))

    # when uses function calling to extract structured outputs
    # here we force tool_choice to be required
    llm_kwargs["tool_choice"] = (
        "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
    )
    return super().structured_predict(
        output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
    )

```
  
---|---  
###  astructured_predict `async` #
```
astructured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Model

```

Structured predict.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/base.py`

| ```
@dispatcher.span
async def astructured_predict(
    self,
    output_cls: Type[Model],
    prompt: PromptTemplate,
    llm_kwargs: Optional[Dict[str, Any]] = None,
    **prompt_args: Any,
) -> Model:
    """Structured predict."""
    llm_kwargs = llm_kwargs or {}

    if self._should_use_structure_outputs():
        messages = self._extend_messages(prompt.format_messages(**prompt_args))
        llm_kwargs = self._prepare_schema(llm_kwargs, output_cls)
        response = await self.achat(messages, **llm_kwargs)
        return output_cls.model_validate_json(str(response.message.content))

    # when uses function calling to extract structured outputs
    # here we force tool_choice to be required
    llm_kwargs["tool_choice"] = (
        "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
    )
    return await super().astructured_predict(
        output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
    )

```
  
---|---  
###  stream_structured_predict #
```
stream_structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Generator[Union[Model, FlexibleModel], None, None]

```

Stream structured predict.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/base.py`

| ```
@dispatcher.span
def stream_structured_predict(
    self,
    output_cls: Type[Model],
    prompt: PromptTemplate,
    llm_kwargs: Optional[Dict[str, Any]] = None,
    **prompt_args: Any,
) -> Generator[Union[Model, FlexibleModel], None, None]:
    """Stream structured predict."""
    llm_kwargs = llm_kwargs or {}

    return super().stream_structured_predict(
        output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
    )

```
  
---|---  
###  astream_structured_predict `async` #
```
astream_structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> AsyncGenerator[Union[Model, FlexibleModel], None]

```

Stream structured predict.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/base.py`

| ```
@dispatcher.span
async def astream_structured_predict(
    self,
    output_cls: Type[Model],
    prompt: PromptTemplate,
    llm_kwargs: Optional[Dict[str, Any]] = None,
    **prompt_args: Any,
) -> AsyncGenerator[Union[Model, FlexibleModel], None]:
    """Stream structured predict."""
    llm_kwargs = llm_kwargs or {}
    return await super().astream_structured_predict(
        output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
    )

```
  
---|---  
##  OpenAIResponses #
Bases: `FunctionCallingLLM`
OpenAI Responses LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model` |  `str` |  name of the OpenAI model to use. |  `DEFAULT_OPENAI_MODEL`  
`temperature` |  `float` |  a float from 0 to 1 controlling randomness in generation; higher will lead to more creative, less deterministic responses. |  `DEFAULT_TEMPERATURE`  
`max_output_tokens` |  `Optional[int]` |  the maximum number of tokens to generate. |  `None`  
`reasoning_options` |  `Optional[Dict[str, Any]]` |  Optional dictionary to configure reasoning for O1 models. Corresponds to the 'reasoning' parameter in the OpenAI API. Example: {"effort": "low", "summary": "concise"} |  `None`  
`include` |  `Optional[List[str]]` |  Additional output data to include in the model response. |  `None`  
`instructions` |  `Optional[str]` |  Instructions for the model to follow. |  `None`  
`track_previous_responses` |  `bool` |  Whether to track previous responses. If true, the LLM class will statefully track previous responses. |  `False`  
`store` |  `bool` |  Whether to store previous responses in OpenAI's storage. |  `False`  
`built_in_tools` |  `Optional[List[dict]]` |  The built-in tools to use for the model to augment responses. |  `None`  
`truncation` |  `str` |  Whether to auto-truncate the input if it exceeds the model's context window. |  `'disabled'`  
`user` |  `Optional[str]` |  An optional identifier to help track the user's requests for abuse. |  `None`  
`strict` |  `bool` |  Whether to enforce strict validation of the structured output. |  `False`  
`additional_kwargs` |  `Optional[Dict[str, Any]]` |  Add additional parameters to OpenAI request body. |  `None`  
`max_retries` |  `int` |  How many times to retry the API call if it fails. |  `3`  
`timeout` |  `float` |  How long to wait, in seconds, for an API call before failing. |  `60.0`  
`api_key` |  `Optional[str]` |  Your OpenAI api key |  `None`  
`api_base` |  `Optional[str]` |  The base URL of the API to call |  `None`  
`api_version` |  `Optional[str]` |  the version of the API to call |  `None`  
`default_headers` |  `Optional[Dict[str, str]]` |  override the default headers for API requests. |  `None`  
`http_client` |  `Optional[Client]` |  pass in your own httpx.Client instance. |  `None`  
`async_http_client` |  `Optional[AsyncClient]` |  pass in your own httpx.AsyncClient instance. |  `None`  
Examples:
`pip install llama-index-llms-openai`
```
from llama_index.llms.openai import OpenAIResponses

llm = OpenAIResponses(model="gpt-4o-mini", api_key="sk-...")

response = llm.complete("Hi, write a short story")
print(response.text)

```

Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/responses.py`

| ```
class OpenAIResponses(FunctionCallingLLM):
    """
    OpenAI Responses LLM.

    Args:
        model: name of the OpenAI model to use.
        temperature: a float from 0 to 1 controlling randomness in generation; higher will lead to more creative, less deterministic responses.
        max_output_tokens: the maximum number of tokens to generate.
        reasoning_options: Optional dictionary to configure reasoning for O1 models.
                    Corresponds to the 'reasoning' parameter in the OpenAI API.
                    Example: {"effort": "low", "summary": "concise"}
        include: Additional output data to include in the model response.
        instructions: Instructions for the model to follow.
        track_previous_responses: Whether to track previous responses. If true, the LLM class will statefully track previous responses.
        store: Whether to store previous responses in OpenAI's storage.
        built_in_tools: The built-in tools to use for the model to augment responses.
        truncation: Whether to auto-truncate the input if it exceeds the model's context window.
        user: An optional identifier to help track the user's requests for abuse.
        strict: Whether to enforce strict validation of the structured output.
        additional_kwargs: Add additional parameters to OpenAI request body.
        max_retries: How many times to retry the API call if it fails.
        timeout: How long to wait, in seconds, for an API call before failing.
        api_key: Your OpenAI api key
        api_base: The base URL of the API to call
        api_version: the version of the API to call
        default_headers: override the default headers for API requests.
        http_client: pass in your own httpx.Client instance.
        async_http_client: pass in your own httpx.AsyncClient instance.

    Examples:
        `pip install llama-index-llms-openai`

    ```python
        from llama_index.llms.openai import OpenAIResponses

        llm = OpenAIResponses(model="gpt-4o-mini", api_key="sk-...")

        response = llm.complete("Hi, write a short story")
        print(response.text)
    ```
    """

    model: str = Field(
        default=DEFAULT_OPENAI_MODEL, description="The OpenAI model to use."
    )
    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        description="The temperature to use during generation.",
        ge=0.0,
        le=2.0,
    )
    top_p: float = Field(
        default=1.0,
        description="The top-p value to use during generation.",
        ge=0.0,
        le=1.0,
    )
    max_output_tokens: Optional[int] = Field(
        description="The maximum number of tokens to generate.",
        gt=0,
    )
    reasoning_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional dictionary to configure reasoning for O1 models. Example: {'effort': 'low', 'summary': 'concise'}",
    )
    include: Optional[List[str]] = Field(
        default=None,
        description="Additional output data to include in the model response.",
    )
    instructions: Optional[str] = Field(
        default=None,
        description="Instructions for the model to follow.",
    )
    track_previous_responses: bool = Field(
        default=False,
        description="Whether to track previous responses. If true, the LLM class will statefully track previous responses.",
    )
    store: bool = Field(
        default=False,
        description="Whether to store previous responses in OpenAI's storage.",
    )
    built_in_tools: Optional[List[dict]] = Field(
        default=None,
        description="The built-in tools to use for the model to augment responses.",
    )
    truncation: str = Field(
        default="disabled",
        description="Whether to auto-truncate the input if it exceeds the model's context window.",
    )
    user: Optional[str] = Field(
        default=None,
        description="An optional identifier to help track the user's requests for abuse.",
    )
    call_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata to include in the API call.",
    )
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional kwargs for the OpenAI API at inference time.",
    )
    max_retries: int = Field(
        default=3,
        description="The maximum number of API retries.",
        ge=0,
    )
    timeout: float = Field(
        default=60.0,
        description="The timeout, in seconds, for API requests.",
        ge=0,
    )
    strict: bool = Field(
        default=False,
        description="Whether to enforce strict validation of the structured output.",
    )
    default_headers: Optional[Dict[str, str]] = Field(
        default=None, description="The default headers for API requests."
    )
    api_key: str = Field(default=None, description="The OpenAI API key.")
    api_base: str = Field(description="The base URL for OpenAI API.")
    api_version: str = Field(description="The API version for OpenAI API.")
    context_window: Optional[int] = Field(
        default=None,
        description="The context window override for the model.",
    )

    _client: SyncOpenAI = PrivateAttr()
    _aclient: AsyncOpenAI = PrivateAttr()
    _http_client: Optional[httpx.Client] = PrivateAttr()
    _async_http_client: Optional[httpx.AsyncClient] = PrivateAttr()
    _previous_response_id: Optional[str] = PrivateAttr()

    def __init__(
        self,
        model: str = DEFAULT_OPENAI_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_output_tokens: Optional[int] = None,
        reasoning_options: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None,
        instructions: Optional[str] = None,
        track_previous_responses: bool = False,
        store: bool = False,
        built_in_tools: Optional[List[dict]] = None,
        truncation: str = "disabled",
        user: Optional[str] = None,
        previous_response_id: Optional[str] = None,
        call_metadata: Optional[Dict[str, Any]] = None,
        strict: bool = False,
        additional_kwargs: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
        async_http_client: Optional[httpx.AsyncClient] = None,
        openai_client: Optional[SyncOpenAI] = None,
        async_openai_client: Optional[AsyncOpenAI] = None,
        context_window: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        additional_kwargs = additional_kwargs or {}

        api_key, api_base, api_version = resolve_openai_credentials(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
        )

        # TODO: Temp forced to 1.0 for o1
        if model in O1_MODELS:
            temperature = 1.0

        super().__init__(
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            reasoning_options=reasoning_options,
            include=include,
            instructions=instructions,
            track_previous_responses=track_previous_responses,
            store=store,
            built_in_tools=built_in_tools,
            truncation=truncation,
            user=user,
            additional_kwargs=additional_kwargs,
            max_retries=max_retries,
            api_key=api_key,
            api_version=api_version,
            api_base=api_base,
            timeout=timeout,
            default_headers=default_headers,
            call_metadata=call_metadata,
            strict=strict,
            context_window=context_window,
            **kwargs,
        )

        self._previous_response_id = previous_response_id

        # store is set to true if track_previous_responses is true
        if self.track_previous_responses:
            self.store = True

        self._http_client = http_client
        self._async_http_client = async_http_client
        self._client = openai_client or SyncOpenAI(**self._get_credential_kwargs())
        self._aclient = async_openai_client or AsyncOpenAI(
            **self._get_credential_kwargs(is_async=True)
        )

    @classmethod
    def class_name(cls) -> str:
        return "openai_responses_llm"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=self.context_window
            or openai_modelname_to_contextsize(self._get_model_name()),
            num_output=self.max_output_tokens or -1,
            is_chat_model=True,
            is_function_calling_model=is_function_calling_model(
                model=self._get_model_name()
            ),
            model_name=self.model,
        )

    @property
    def _tokenizer(self) -> Optional[Tokenizer]:
        """
        Get a tokenizer for this model, or None if a tokenizing method is unknown.

        OpenAI can do this using the tiktoken package, subclasses may not have
        this convenience.
        """
        return tiktoken.encoding_for_model(self._get_model_name())

    def _get_model_name(self) -> str:
        model_name = self.model
        if "ft-" in model_name:  # legacy fine-tuning
            model_name = model_name.split(":")[0]
        elif model_name.startswith("ft:"):
            model_name = model_name.split(":")[1]
        return model_name

    def _is_azure_client(self) -> bool:
        return isinstance(self._get_client(), AzureOpenAI)

    def _get_credential_kwargs(self, is_async: bool = False) -> Dict[str, Any]:
        return {
            "api_key": self.api_key,
            "base_url": self.api_base,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "default_headers": self.default_headers,
            "http_client": self._async_http_client if is_async else self._http_client,
        }

    def _get_model_kwargs(self, **kwargs: Any) -> Dict[str, Any]:
        initial_tools = self.built_in_tools or []
        model_kwargs = {
            "model": self.model,
            "include": self.include,
            "instructions": self.instructions,
            "max_output_tokens": self.max_output_tokens,
            "metadata": self.call_metadata,
            "previous_response_id": self._previous_response_id,
            "store": self.store,
            "temperature": self.temperature,
            "tools": [*initial_tools, *kwargs.pop("tools", [])],
            "top_p": self.top_p,
            "truncation": self.truncation,
            "user": self.user,
        }

        if self.model in O1_MODELS and self.reasoning_options is not None:
            model_kwargs["reasoning"] = self.reasoning_options

        # priority is class args > additional_kwargs > runtime args
        model_kwargs.update(self.additional_kwargs)

        kwargs = kwargs or {}
        model_kwargs.update(kwargs)

        return model_kwargs

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        return self._chat(messages, **kwargs)

    @llm_chat_callback()
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        return self._stream_chat(messages, **kwargs)

    @llm_completion_callback()
    def complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        complete_fn = chat_to_completion_decorator(self._chat)

        return complete_fn(prompt, **kwargs)

    @llm_completion_callback()
    def stream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseGen:
        stream_complete_fn = stream_chat_to_completion_decorator(self._stream_chat)

        return stream_complete_fn(prompt, **kwargs)

    def _parse_response_output(self, output: List[ResponseOutputItem]) -> ChatResponse:
        message = ChatMessage(role=MessageRole.ASSISTANT, blocks=[])
        additional_kwargs = {"built_in_tool_calls": []}
        tool_calls = []
        blocks: List[ContentBlock] = []
        for item in output:
            if isinstance(item, ResponseOutputMessage):
                for part in item.content:
                    if hasattr(part, "text"):
                        blocks.append(TextBlock(text=part.text))
                    if hasattr(part, "annotations"):
                        additional_kwargs["annotations"] = part.annotations
                    if hasattr(part, "refusal"):
                        additional_kwargs["refusal"] = part.refusal

                message.blocks.extend(blocks)
            elif isinstance(item, ImageGenerationCall):
                # return an ImageBlock if there is image generation
                if item.status != "failed":
                    additional_kwargs["built_in_tool_calls"].append(item)
                    if item.result is not None:
                        image_bytes = base64.b64decode(item.result)
                        blocks.append(ImageBlock(image=image_bytes))
            elif isinstance(item, ResponseCodeInterpreterToolCall):
                additional_kwargs["built_in_tool_calls"].append(item)
            elif isinstance(item, McpCall):
                additional_kwargs["built_in_tool_calls"].append(item)
            elif isinstance(item, ResponseFileSearchToolCall):
                additional_kwargs["built_in_tool_calls"].append(item)
            elif isinstance(item, ResponseFunctionToolCall):
                tool_calls.append(item)
            elif isinstance(item, ResponseFunctionWebSearch):
                additional_kwargs["built_in_tool_calls"].append(item)
            elif isinstance(item, ResponseComputerToolCall):
                additional_kwargs["built_in_tool_calls"].append(item)
            elif isinstance(item, ResponseReasoningItem):
                additional_kwargs["reasoning"] = item

        if tool_calls and message:
            message.additional_kwargs["tool_calls"] = tool_calls

        return ChatResponse(message=message, additional_kwargs=additional_kwargs)

    @llm_retry_decorator
    def _chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        kwargs_dict = self._get_model_kwargs(**kwargs)
        message_dicts = to_openai_message_dicts(
            messages,
            model=self.model,
            is_responses_api=True,
        )

        response: Response = self._client.responses.create(
            input=message_dicts,
            stream=False,
            **kwargs_dict,
        )

        if self.track_previous_responses:
            self._previous_response_id = response.id

        chat_response = self._parse_response_output(response.output)
        chat_response.raw = response
        chat_response.additional_kwargs["usage"] = response.usage

        return chat_response

    @staticmethod
    def process_response_event(
        event: ResponseStreamEvent,
        tool_calls: List[ResponseFunctionToolCall],
        built_in_tool_calls: List[Any],
        additional_kwargs: Dict[str, Any],
        current_tool_call: Optional[ResponseFunctionToolCall],
        track_previous_responses: bool,
        previous_response_id: Optional[str] = None,
    ) -> Tuple[
        List[ContentBlock],
        List[ResponseFunctionToolCall],
        List[Any],
        Dict[str, Any],
        Optional[ResponseFunctionToolCall],
        Optional[str],
        str,
    ]:
        """
        Process a ResponseStreamEvent and update the state accordingly.

        Args:
            event: The response stream event to process
            content: Current accumulated content string
            tool_calls: List of completed tool calls
            built_in_tool_calls: List of built-in tool calls
            additional_kwargs: Additional keyword arguments to include in ChatResponse
            current_tool_call: The currently in-progress tool call, if any
            track_previous_responses: Whether to track previous response IDs
            previous_response_id: Previous response ID if tracking

        Returns:
            A tuple containing the updated state:
            (content, tool_calls, built_in_tool_calls, additional_kwargs, current_tool_call, updated_previous_response_id, delta)
        """
        delta = ""
        updated_previous_response_id = previous_response_id
        # we use blocks instead of content, since now we also support images! :)
        blocks: List[ContentBlock] = []
        if isinstance(event, ResponseCreatedEvent) or isinstance(
            event, ResponseInProgressEvent
        ):
            # Initial events, track the response id
            if track_previous_responses:
                updated_previous_response_id = event.response.id
        elif isinstance(event, ResponseOutputItemAddedEvent):
            # New output item (message, tool call, etc.)
            if isinstance(event.item, ResponseFunctionToolCall):
                current_tool_call = event.item
        elif isinstance(event, ResponseTextDeltaEvent):
            # Text content is being added
            delta = event.delta
            blocks.append(TextBlock(text=delta))
        elif isinstance(event, ResponseImageGenCallPartialImageEvent):
            # Partial image
            if event.partial_image_b64:
                blocks.append(
                    ImageBlock(
                        image=base64.b64decode(event.partial_image_b64),
                        detail=f"id_{event.partial_image_index}",
                    )
                )
        elif isinstance(event, ResponseFunctionCallArgumentsDeltaEvent):
            # Function call arguments are being streamed
            if current_tool_call is not None:
                current_tool_call.arguments += event.delta
        elif isinstance(event, ResponseFunctionCallArgumentsDoneEvent):
            # Function call arguments are complete
            if current_tool_call is not None:
                current_tool_call.arguments = event.arguments
                current_tool_call.status = "completed"

                # append a copy of the tool call to the list
                tool_calls.append(
                    ResponseFunctionToolCall(**current_tool_call.model_dump())
                )

                # clear the current tool call
                current_tool_call = None
        elif isinstance(event, ResponseOutputTextAnnotationAddedEvent):
            # Annotations for the text
            annotations = additional_kwargs.get("annotations", [])
            annotations.append(event.annotation)
            additional_kwargs["annotations"] = annotations
        elif isinstance(event, ResponseFileSearchCallCompletedEvent):
            # File search tool call completed
            built_in_tool_calls.append(event)
        elif isinstance(event, ResponseWebSearchCallCompletedEvent):
            # Web search tool call completed
            built_in_tool_calls.append(event)
        elif isinstance(event, ResponseReasoningItem):
            # Reasoning information
            additional_kwargs["reasoning"] = event
        elif isinstance(event, ResponseCompletedEvent):
            # Response is complete
            if hasattr(event, "response") and hasattr(event.response, "usage"):
                additional_kwargs["usage"] = event.response.usage

        return (
            blocks,
            tool_calls,
            built_in_tool_calls,
            additional_kwargs,
            current_tool_call,
            updated_previous_response_id,
            delta,
        )

    @llm_retry_decorator
    def _stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        message_dicts = to_openai_message_dicts(
            messages,
            model=self.model,
            is_responses_api=True,
        )

        def gen() -> ChatResponseGen:
            tool_calls = []
            built_in_tool_calls = []
            additional_kwargs = {"built_in_tool_calls": []}
            current_tool_call: Optional[ResponseFunctionToolCall] = None
            local_previous_response_id = self._previous_response_id

            for event in self._client.responses.create(
                input=message_dicts,
                stream=True,
                **self._get_model_kwargs(**kwargs),
            ):
                # Process the event and update state
                (
                    blocks,
                    tool_calls,
                    built_in_tool_calls,
                    additional_kwargs,
                    current_tool_call,
                    local_previous_response_id,
                    delta,
                ) = OpenAIResponses.process_response_event(
                    event=event,
                    tool_calls=tool_calls,
                    built_in_tool_calls=built_in_tool_calls,
                    additional_kwargs=additional_kwargs,
                    current_tool_call=current_tool_call,
                    track_previous_responses=self.track_previous_responses,
                    previous_response_id=local_previous_response_id,
                )

                if (
                    self.track_previous_responses
                    and local_previous_response_id != self._previous_response_id
                ):
                    self._previous_response_id = local_previous_response_id

                if built_in_tool_calls:
                    additional_kwargs["built_in_tool_calls"] = built_in_tool_calls

                # For any event, yield a ChatResponse with the current state
                yield ChatResponse(
                    message=ChatMessage(
                        role=MessageRole.ASSISTANT,
                        blocks=blocks,
                        additional_kwargs={"tool_calls": tool_calls}
                        if tool_calls
                        else {},
                    ),
                    delta=delta,
                    raw=event,
                    additional_kwargs=additional_kwargs,
                )

        return gen()

    # ===== Async Endpoints =====
    @llm_chat_callback()
    async def achat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        return await self._achat(messages, **kwargs)

    @llm_chat_callback()
    async def astream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponseAsyncGen:
        return await self._astream_chat(messages, **kwargs)

    @llm_completion_callback()
    async def acomplete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponse:
        acomplete_fn = achat_to_completion_decorator(self._achat)

        return await acomplete_fn(prompt, **kwargs)

    @llm_completion_callback()
    async def astream_complete(
        self, prompt: str, formatted: bool = False, **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        astream_complete_fn = astream_chat_to_completion_decorator(self._astream_chat)

        return await astream_complete_fn(prompt, **kwargs)

    @llm_retry_decorator
    async def _achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        message_dicts = to_openai_message_dicts(
            messages,
            model=self.model,
            is_responses_api=True,
        )

        response: Response = await self._aclient.responses.create(
            input=message_dicts,
            stream=False,
            **self._get_model_kwargs(**kwargs),
        )

        if self.track_previous_responses:
            self._previous_response_id = response.id

        chat_response = self._parse_response_output(response.output)
        chat_response.raw = response
        chat_response.additional_kwargs["usage"] = response.usage

        return chat_response

    @llm_retry_decorator
    async def _astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        message_dicts = to_openai_message_dicts(
            messages,
            model=self.model,
            is_responses_api=True,
        )

        async def gen() -> ChatResponseAsyncGen:
            tool_calls = []
            built_in_tool_calls = []
            additional_kwargs = {"built_in_tool_calls": []}
            current_tool_call: Optional[ResponseFunctionToolCall] = None
            local_previous_response_id = self._previous_response_id

            response_stream = await self._aclient.responses.create(
                input=message_dicts,
                stream=True,
                **self._get_model_kwargs(**kwargs),
            )

            async for event in response_stream:
                # Process the event and update state
                (
                    blocks,
                    tool_calls,
                    built_in_tool_calls,
                    additional_kwargs,
                    current_tool_call,
                    local_previous_response_id,
                    delta,
                ) = OpenAIResponses.process_response_event(
                    event=event,
                    tool_calls=tool_calls,
                    built_in_tool_calls=built_in_tool_calls,
                    additional_kwargs=additional_kwargs,
                    current_tool_call=current_tool_call,
                    track_previous_responses=self.track_previous_responses,
                    previous_response_id=local_previous_response_id,
                )

                if (
                    self.track_previous_responses
                    and local_previous_response_id != self._previous_response_id
                ):
                    self._previous_response_id = local_previous_response_id

                if built_in_tool_calls:
                    additional_kwargs["built_in_tool_calls"] = built_in_tool_calls

                # For any event, yield a ChatResponse with the current state
                yield ChatResponse(
                    message=ChatMessage(
                        role=MessageRole.ASSISTANT,
                        blocks=blocks,
                        additional_kwargs={"tool_calls": tool_calls}
                        if tool_calls
                        else {},
                    ),
                    delta=delta,
                    raw=event,
                    additional_kwargs=additional_kwargs,
                )

        return gen()

    def _prepare_chat_with_tools(
        self,
        tools: Sequence["BaseTool"],
        user_msg: Optional[Union[str, ChatMessage]] = None,
        chat_history: Optional[List[ChatMessage]] = None,
        allow_parallel_tool_calls: bool = True,
        tool_required: bool = False,
        tool_choice: Optional[Union[str, dict]] = None,
        verbose: bool = False,
        strict: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Predict and call the tool."""

        # openai responses api has a slightly different tool spec format
        tool_specs = [
            {
                "type": "function",
                **tool.metadata.to_openai_tool(skip_length_check=True)["function"],
            }
            for tool in tools
        ]

        if strict is not None:
            strict = strict
        else:
            strict = self.strict

        if strict:
            for tool_spec in tool_specs:
                tool_spec["strict"] = True
                tool_spec["parameters"]["additionalProperties"] = False

        if isinstance(user_msg, str):
            user_msg = ChatMessage(role=MessageRole.USER, content=user_msg)

        messages = chat_history or []
        if user_msg:
            messages.append(user_msg)

        return {
            "messages": messages,
            "tools": tool_specs or None,
            "tool_choice": resolve_tool_choice(tool_choice, tool_required)
            if tool_specs
            else None,
            "parallel_tool_calls": allow_parallel_tool_calls,
            **kwargs,
        }

    def get_tool_calls_from_response(
        self,
        response: "ChatResponse",
        error_on_no_tool_call: bool = True,
        **kwargs: Any,
    ) -> List[ToolSelection]:
        """Predict and call the tool."""
        tool_calls: List[ResponseFunctionToolCall] = (
            response.message.additional_kwargs.get("tool_calls", [])
        )

        if len(tool_calls) < 1:
            if error_on_no_tool_call:
                raise ValueError(
                    f"Expected at least one tool call, but got {len(tool_calls)} tool calls."
                )
            else:
                return []

        tool_selections = []
        for tool_call in tool_calls:
            # this should handle both complete and partial jsons
            try:
                argument_dict = parse_partial_json(tool_call.arguments)
            except ValueError:
                argument_dict = {}

            tool_selections.append(
                ToolSelection(
                    tool_id=tool_call.call_id,
                    tool_name=tool_call.name,
                    tool_kwargs=argument_dict,
                )
            )

        return tool_selections

    @dispatcher.span
    def structured_predict(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> Model:
        """Structured predict."""
        llm_kwargs = llm_kwargs or {}

        llm_kwargs["tool_choice"] = (
            "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
        )
        # by default structured prediction uses function calling to extract structured outputs
        # here we force tool_choice to be required
        return super().structured_predict(
            output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
        )

    @dispatcher.span
    async def astructured_predict(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> Model:
        """Structured predict."""
        llm_kwargs = llm_kwargs or {}

        llm_kwargs["tool_choice"] = (
            "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
        )
        # by default structured prediction uses function calling to extract structured outputs
        # here we force tool_choice to be required
        return await super().astructured_predict(
            output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
        )

    @dispatcher.span
    def stream_structured_predict(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> Generator[Union[Model, FlexibleModel], None, None]:
        """Stream structured predict."""
        llm_kwargs = llm_kwargs or {}

        llm_kwargs["tool_choice"] = (
            "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
        )
        # by default structured prediction uses function calling to extract structured outputs
        # here we force tool_choice to be required
        return super().stream_structured_predict(
            output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
        )

    @dispatcher.span
    async def astream_structured_predict(
        self,
        output_cls: Type[Model],
        prompt: PromptTemplate,
        llm_kwargs: Optional[Dict[str, Any]] = None,
        **prompt_args: Any,
    ) -> AsyncGenerator[Union[Model, FlexibleModel], None]:
        """Stream structured predict."""
        llm_kwargs = llm_kwargs or {}

        llm_kwargs["tool_choice"] = (
            "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
        )
        # by default structured prediction uses function calling to extract structured outputs
        # here we force tool_choice to be required
        return await super().astream_structured_predict(
            output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
        )

```
  
---|---  
###  process_response_event `staticmethod` #
```
process_response_event(event: ResponseStreamEvent, tool_calls: List[ResponseFunctionToolCall], built_in_tool_calls: List[Any], additional_kwargs: Dict[str, Any], current_tool_call: Optional[ResponseFunctionToolCall], track_previous_responses: bool, previous_response_id: Optional[str] = None) -> Tuple[List[ContentBlock], List[ResponseFunctionToolCall], List[Any], Dict[str, Any], Optional[ResponseFunctionToolCall], Optional[str], str]

```

Process a ResponseStreamEvent and update the state accordingly.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`event` |  `ResponseStreamEvent` |  The response stream event to process |  _required_  
`content` |  |  Current accumulated content string |  _required_  
`tool_calls` |  `List[ResponseFunctionToolCall]` |  List of completed tool calls |  _required_  
`built_in_tool_calls` |  `List[Any]` |  List of built-in tool calls |  _required_  
`additional_kwargs` |  `Dict[str, Any]` |  Additional keyword arguments to include in ChatResponse |  _required_  
`current_tool_call` |  `Optional[ResponseFunctionToolCall]` |  The currently in-progress tool call, if any |  _required_  
`track_previous_responses` |  `bool` |  Whether to track previous response IDs |  _required_  
`previous_response_id` |  `Optional[str]` |  Previous response ID if tracking |  `None`  
Returns:
Type | Description  
---|---  
`List[ContentBlock]` |  A tuple containing the updated state:  
`List[ResponseFunctionToolCall]` |  (content, tool_calls, built_in_tool_calls, additional_kwargs, current_tool_call, updated_previous_response_id, delta)  
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/responses.py`

| ```
@staticmethod
def process_response_event(
    event: ResponseStreamEvent,
    tool_calls: List[ResponseFunctionToolCall],
    built_in_tool_calls: List[Any],
    additional_kwargs: Dict[str, Any],
    current_tool_call: Optional[ResponseFunctionToolCall],
    track_previous_responses: bool,
    previous_response_id: Optional[str] = None,
) -> Tuple[
    List[ContentBlock],
    List[ResponseFunctionToolCall],
    List[Any],
    Dict[str, Any],
    Optional[ResponseFunctionToolCall],
    Optional[str],
    str,
]:
    """
    Process a ResponseStreamEvent and update the state accordingly.

    Args:
        event: The response stream event to process
        content: Current accumulated content string
        tool_calls: List of completed tool calls
        built_in_tool_calls: List of built-in tool calls
        additional_kwargs: Additional keyword arguments to include in ChatResponse
        current_tool_call: The currently in-progress tool call, if any
        track_previous_responses: Whether to track previous response IDs
        previous_response_id: Previous response ID if tracking

    Returns:
        A tuple containing the updated state:
        (content, tool_calls, built_in_tool_calls, additional_kwargs, current_tool_call, updated_previous_response_id, delta)
    """
    delta = ""
    updated_previous_response_id = previous_response_id
    # we use blocks instead of content, since now we also support images! :)
    blocks: List[ContentBlock] = []
    if isinstance(event, ResponseCreatedEvent) or isinstance(
        event, ResponseInProgressEvent
    ):
        # Initial events, track the response id
        if track_previous_responses:
            updated_previous_response_id = event.response.id
    elif isinstance(event, ResponseOutputItemAddedEvent):
        # New output item (message, tool call, etc.)
        if isinstance(event.item, ResponseFunctionToolCall):
            current_tool_call = event.item
    elif isinstance(event, ResponseTextDeltaEvent):
        # Text content is being added
        delta = event.delta
        blocks.append(TextBlock(text=delta))
    elif isinstance(event, ResponseImageGenCallPartialImageEvent):
        # Partial image
        if event.partial_image_b64:
            blocks.append(
                ImageBlock(
                    image=base64.b64decode(event.partial_image_b64),
                    detail=f"id_{event.partial_image_index}",
                )
            )
    elif isinstance(event, ResponseFunctionCallArgumentsDeltaEvent):
        # Function call arguments are being streamed
        if current_tool_call is not None:
            current_tool_call.arguments += event.delta
    elif isinstance(event, ResponseFunctionCallArgumentsDoneEvent):
        # Function call arguments are complete
        if current_tool_call is not None:
            current_tool_call.arguments = event.arguments
            current_tool_call.status = "completed"

            # append a copy of the tool call to the list
            tool_calls.append(
                ResponseFunctionToolCall(**current_tool_call.model_dump())
            )

            # clear the current tool call
            current_tool_call = None
    elif isinstance(event, ResponseOutputTextAnnotationAddedEvent):
        # Annotations for the text
        annotations = additional_kwargs.get("annotations", [])
        annotations.append(event.annotation)
        additional_kwargs["annotations"] = annotations
    elif isinstance(event, ResponseFileSearchCallCompletedEvent):
        # File search tool call completed
        built_in_tool_calls.append(event)
    elif isinstance(event, ResponseWebSearchCallCompletedEvent):
        # Web search tool call completed
        built_in_tool_calls.append(event)
    elif isinstance(event, ResponseReasoningItem):
        # Reasoning information
        additional_kwargs["reasoning"] = event
    elif isinstance(event, ResponseCompletedEvent):
        # Response is complete
        if hasattr(event, "response") and hasattr(event.response, "usage"):
            additional_kwargs["usage"] = event.response.usage

    return (
        blocks,
        tool_calls,
        built_in_tool_calls,
        additional_kwargs,
        current_tool_call,
        updated_previous_response_id,
        delta,
    )

```
  
---|---  
###  get_tool_calls_from_response #
```
get_tool_calls_from_response(response: ChatResponse, error_on_no_tool_call: bool = True, **kwargs: Any) -> List[ToolSelection]

```

Predict and call the tool.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/responses.py`

| ```
def get_tool_calls_from_response(
    self,
    response: "ChatResponse",
    error_on_no_tool_call: bool = True,
    **kwargs: Any,
) -> List[ToolSelection]:
    """Predict and call the tool."""
    tool_calls: List[ResponseFunctionToolCall] = (
        response.message.additional_kwargs.get("tool_calls", [])
    )

    if len(tool_calls) < 1:
        if error_on_no_tool_call:
            raise ValueError(
                f"Expected at least one tool call, but got {len(tool_calls)} tool calls."
            )
        else:
            return []

    tool_selections = []
    for tool_call in tool_calls:
        # this should handle both complete and partial jsons
        try:
            argument_dict = parse_partial_json(tool_call.arguments)
        except ValueError:
            argument_dict = {}

        tool_selections.append(
            ToolSelection(
                tool_id=tool_call.call_id,
                tool_name=tool_call.name,
                tool_kwargs=argument_dict,
            )
        )

    return tool_selections

```
  
---|---  
###  structured_predict #
```
structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Model

```

Structured predict.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/responses.py`

| ```
@dispatcher.span
def structured_predict(
    self,
    output_cls: Type[Model],
    prompt: PromptTemplate,
    llm_kwargs: Optional[Dict[str, Any]] = None,
    **prompt_args: Any,
) -> Model:
    """Structured predict."""
    llm_kwargs = llm_kwargs or {}

    llm_kwargs["tool_choice"] = (
        "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
    )
    # by default structured prediction uses function calling to extract structured outputs
    # here we force tool_choice to be required
    return super().structured_predict(
        output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
    )

```
  
---|---  
###  astructured_predict `async` #
```
astructured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Model

```

Structured predict.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/responses.py`

| ```
@dispatcher.span
async def astructured_predict(
    self,
    output_cls: Type[Model],
    prompt: PromptTemplate,
    llm_kwargs: Optional[Dict[str, Any]] = None,
    **prompt_args: Any,
) -> Model:
    """Structured predict."""
    llm_kwargs = llm_kwargs or {}

    llm_kwargs["tool_choice"] = (
        "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
    )
    # by default structured prediction uses function calling to extract structured outputs
    # here we force tool_choice to be required
    return await super().astructured_predict(
        output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
    )

```
  
---|---  
###  stream_structured_predict #
```
stream_structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Generator[Union[Model, FlexibleModel], None, None]

```

Stream structured predict.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/responses.py`

| ```
@dispatcher.span
def stream_structured_predict(
    self,
    output_cls: Type[Model],
    prompt: PromptTemplate,
    llm_kwargs: Optional[Dict[str, Any]] = None,
    **prompt_args: Any,
) -> Generator[Union[Model, FlexibleModel], None, None]:
    """Stream structured predict."""
    llm_kwargs = llm_kwargs or {}

    llm_kwargs["tool_choice"] = (
        "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
    )
    # by default structured prediction uses function calling to extract structured outputs
    # here we force tool_choice to be required
    return super().stream_structured_predict(
        output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
    )

```
  
---|---  
###  astream_structured_predict `async` #
```
astream_structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> AsyncGenerator[Union[Model, FlexibleModel], None]

```

Stream structured predict.
Source code in `llama-index-integrations/llms/llama-index-llms-openai/llama_index/llms/openai/responses.py`

| ```
@dispatcher.span
async def astream_structured_predict(
    self,
    output_cls: Type[Model],
    prompt: PromptTemplate,
    llm_kwargs: Optional[Dict[str, Any]] = None,
    **prompt_args: Any,
) -> AsyncGenerator[Union[Model, FlexibleModel], None]:
    """Stream structured predict."""
    llm_kwargs = llm_kwargs or {}

    llm_kwargs["tool_choice"] = (
        "required" if "tool_choice" not in llm_kwargs else llm_kwargs["tool_choice"]
    )
    # by default structured prediction uses function calling to extract structured outputs
    # here we force tool_choice to be required
    return await super().astream_structured_predict(
        output_cls, prompt, llm_kwargs=llm_kwargs, **prompt_args
    )

```
  
---|---
