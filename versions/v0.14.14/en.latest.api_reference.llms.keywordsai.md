# Keywordsai
##  KeywordsAI #
Bases: `OpenAI`
KeywordsAI LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model` |  `str` |  name of the KeywordsAI model to use. |  `DEFAULT_KEYWORDSAI_MODEL`  
`temperature` |  `float` |  a float from 0 to 1 controlling randomness in generation; higher will lead to more creative, less deterministic responses. |  `DEFAULT_TEMPERATURE`  
`max_tokens` |  `Optional[int]` |  the maximum number of tokens to generate. |  `None`  
`customer_identifier` |  `Optional[str]` |  the unique ID of the customer for keywords observability. |  `None`  
`thread_identifier` |  `Optional[str]` |  the unique ID of the thread for keywords observability. |  `None`  
`additional_kwargs` |  `Optional[Dict[str, Any]]` |  Add additional parameters to OpenAI SDK request body. |  `None`  
`max_retries` |  `int` |  How many times to retry the API call if it fails. |  `3`  
`timeout` |  `float` |  How long to wait, in seconds, for an API call before failing. |  `60.0`  
`reuse_client` |  `bool` |  Reuse the KeywordsAI client between requests. When doing anything with large volumes of async API calls, setting this to false can improve stability. |  `True`  
`api_key` |  `Optional[str]` |  Your KeywordsAI api key |  `None`  
`api_base` |  `Optional[str]` |  The base URL of the API to call |  `None`  
`api_version` |  `Optional[str]` |  the version of the API to call |  `None`  
`callback_manager` |  `Optional[CallbackManager]` |  the callback manager is used for observability. |  `None`  
`default_headers` |  `Optional[Dict[str, str]]` |  override the default headers for API requests. |  `None`  
`http_client` |  `Optional[Client]` |  pass in your own httpx.Client instance. |  `None`  
`async_http_client` |  `Optional[AsyncClient]` |  pass in your own httpx.AsyncClient instance. |  `None`  
Examples:
`pip install llama-index-llms-keywordsai`
```
import os
import openai

os.environ["KEYWORDSAI_API_KEY"] = "sk-..."
openai.api_key = os.environ["KEYWORDSAI_API_KEY"]

from llama_index.llms.keywordai import KeywordsAI

llm = KeywordsAI(model="gpt-3.5-turbo")

stream = llm.stream("Hi, write a short story")

for r in stream:
    print(r.delta, end="")

```

Source code in `llama-index-integrations/llms/llama-index-llms-keywordsai/llama_index/llms/keywordsai/base.py`

| ```
class KeywordsAI(OpenAI):
    """
    KeywordsAI LLM.

    Args:
        model: name of the KeywordsAI model to use.
        temperature: a float from 0 to 1 controlling randomness in generation; higher will lead to more creative, less deterministic responses.
        max_tokens: the maximum number of tokens to generate.
        customer_identifier: the unique ID of the customer for keywords observability.
        thread_identifier: the unique ID of the thread for keywords observability.
        additional_kwargs: Add additional parameters to OpenAI SDK request body.
        max_retries: How many times to retry the API call if it fails.
        timeout: How long to wait, in seconds, for an API call before failing.
        reuse_client: Reuse the KeywordsAI client between requests. When doing anything with large volumes of async API calls, setting this to false can improve stability.
        api_key: Your KeywordsAI api key
        api_base: The base URL of the API to call
        api_version: the version of the API to call
        callback_manager: the callback manager is used for observability.
        default_headers: override the default headers for API requests.
        http_client: pass in your own httpx.Client instance.
        async_http_client: pass in your own httpx.AsyncClient instance.

    Examples:
        `pip install llama-index-llms-keywordsai`

    ```python
        import os
        import openai

        os.environ["KEYWORDSAI_API_KEY"] = "sk-..."
        openai.api_key = os.environ["KEYWORDSAI_API_KEY"]

        from llama_index.llms.keywordai import KeywordsAI

        llm = KeywordsAI(model="gpt-3.5-turbo")

        stream = llm.stream("Hi, write a short story")

        for r in stream:
            print(r.delta, end="")
    ```

    """

    model: str = Field(
        default=DEFAULT_KEYWORDSAI_MODEL, description="The KeywordsAI model to use."
    )
    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        description="The temperature to use during generation.",
        ge=0.0,
        le=1.0,
    )
    max_tokens: Optional[int] = Field(
        description="The maximum number of tokens to generate.",
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
    customer_identifier: Optional[str] = Field(
        default=None,
        description="The unique ID of the customer for keywords observability.",
    )
    thread_identifier: Optional[str] = Field(
        default=None,
        description="The unique ID of the thread for kewywords observability.",
    )
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Additional kwargs for the KeywordsAI API."
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
            "Reuse the KeywordsAI client between requests. When doing anything with large "
            "volumes of async API calls, setting this to false can improve stability."
        ),
    )

    api_key: str = Field(default=None, description="The KeywordsAI API key.")
    api_base: str = Field(description="The base URL for KeywordsAI API.")
    api_version: str = Field(description="The API version for KeywordsAI API.")
    strict: bool = Field(
        default=False,
        description="Whether to use strict mode for invoking tools/using schemas.",
    )

    _client: Optional[SyncOpenAI] = PrivateAttr()
    _aclient: Optional[AsyncOpenAI] = PrivateAttr()
    _http_client: Optional[httpx.Client] = PrivateAttr()
    _async_http_client: Optional[httpx.AsyncClient] = PrivateAttr()

    def __init__(
        self,
        model: str = DEFAULT_KEYWORDSAI_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: Optional[int] = None,
        customer_identifier: Optional[str] = None,
        thread_identifier: Optional[str] = None,
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
        **kwargs: Any,
    ) -> None:
        additional_kwargs = additional_kwargs or {}
        if not additional_kwargs.get("extra_body"):
            additional_kwargs["extra_body"] = {}
        if customer_identifier:
            additional_kwargs["extra_body"]["customer_identifier"] = customer_identifier
        if thread_identifier:
            additional_kwargs["extra_body"]["thread_identifier"] = thread_identifier

        api_key, api_base, api_version = resolve_keywordsai_credentials(
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
            **kwargs,
        )

        self._client = openai_client
        self._aclient = async_openai_client
        self._http_client = http_client
        self._async_http_client = async_http_client

    @classmethod
    def class_name(cls) -> str:
        return "keywordsai_llm"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=keywordsai_modelname_to_contextsize(self._get_model_name()),
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

```
  
---|---
