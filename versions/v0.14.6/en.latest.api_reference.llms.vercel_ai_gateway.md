# Vercel ai gateway
##  VercelAIGateway #
Bases: `OpenAILike`
Vercel AI Gateway LLM.
To instantiate the `VercelAIGateway` class, you will need to provide authentication credentials. You can authenticate in the following ways (in order of precedence):
  1. Pass an API key or OIDC token directly to the `api_key` parameter
  2. Set the `VERCEL_AI_GATEWAY_API_KEY` environment variable
  3. Set the `VERCEL_OIDC_TOKEN` environment variable


If you haven't obtained an API key or OIDC token yet, you can visit the Vercel AI Gateway docs at (https://vercel.com/ai-gateway) for instructions. Once you have your credentials, you can use the `VercelAIGateway` class to interact with the LLM for tasks like chatting, streaming, and completing prompts.
Examples:
`pip install llama-index-llms-vercel-ai-gateway`
```
from llama_index.llms.vercel_ai_gateway import VercelAIGateway

# Using API key directly
llm = VercelAIGateway(
    api_key="<your-api-key>",
    max_tokens=64000,
    context_window=200000,
    model="anthropic/claude-4-sonnet",
)

# Using OIDC token directly
llm = VercelAIGateway(
    api_key="<your-oidc-token>",
    max_tokens=64000,
    context_window=200000,
    model="anthropic/claude-4-sonnet",
)

# Using environment variables (VERCEL_AI_GATEWAY_API_KEY or VERCEL_OIDC_TOKEN)
llm = VercelAIGateway(
    max_tokens=64000,
    context_window=200000,
    model="anthropic/claude-4-sonnet",
)

# Customizing headers (overrides default http-referer and x-title)
llm = VercelAIGateway(
    api_key="<your-api-key>",
    model="anthropic/claude-4-sonnet",
    default_headers={
        "http-referer": "https://myapp.com/",
        "x-title": "My App"
    }
)

response = llm.complete("Hello World!")
print(str(response))

```

Source code in `llama-index-integrations/llms/llama-index-llms-vercel-ai-gateway/llama_index/llms/vercel_ai_gateway/base.py`

| ```
class VercelAIGateway(OpenAILike):
    """
    Vercel AI Gateway LLM.

    To instantiate the `VercelAIGateway` class, you will need to provide authentication credentials.
    You can authenticate in the following ways (in order of precedence):

    1. Pass an API key or OIDC token directly to the `api_key` parameter
    2. Set the `VERCEL_AI_GATEWAY_API_KEY` environment variable
    3. Set the `VERCEL_OIDC_TOKEN` environment variable

    If you haven't obtained an API key or OIDC token yet, you can visit the Vercel AI Gateway docs
    at (https://vercel.com/ai-gateway) for instructions. Once you have your credentials, you can use
    the `VercelAIGateway` class to interact with the LLM for tasks like chatting, streaming, and
    completing prompts.

    Examples:
        `pip install llama-index-llms-vercel-ai-gateway`

    ```python
        from llama_index.llms.vercel_ai_gateway import VercelAIGateway

        # Using API key directly
        llm = VercelAIGateway(
            api_key="<your-api-key>",
            max_tokens=64000,
            context_window=200000,
            model="anthropic/claude-4-sonnet",
        )

        # Using OIDC token directly
        llm = VercelAIGateway(
            api_key="<your-oidc-token>",
            max_tokens=64000,
            context_window=200000,
            model="anthropic/claude-4-sonnet",
        )

        # Using environment variables (VERCEL_AI_GATEWAY_API_KEY or VERCEL_OIDC_TOKEN)
        llm = VercelAIGateway(
            max_tokens=64000,
            context_window=200000,
            model="anthropic/claude-4-sonnet",
        )

        # Customizing headers (overrides default http-referer and x-title)
        llm = VercelAIGateway(
            api_key="<your-api-key>",
            model="anthropic/claude-4-sonnet",
            default_headers={
                "http-referer": "https://myapp.com/",
                "x-title": "My App"
            }
        )

        response = llm.complete("Hello World!")
        print(str(response))
    ```

    """

    model: str = Field(
        description="The model to use through Vercel AI Gateway. From your Vercel dashboard, go to the AI Gateway tab and select the Model List tab on the left dropdown to see the available models."
    )
    context_window: int = Field(
        default=DEFAULT_CONTEXT_WINDOW,
        description="The maximum number of context tokens for the model. From your Vercel dashboard, go to the AI Gateway tab and select the Model List tab on the left dropdown to see the available models and their context window sizes.",
        gt=0,
    )
    is_chat_model: bool = Field(
        default=True,
        description=LLMMetadata.model_fields["is_chat_model"].description,
    )

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_NUM_OUTPUTS,
        additional_kwargs: Optional[Dict[str, Any]] = None,
        max_retries: int = 5,
        api_base: Optional[str] = DEFAULT_API_BASE,
        api_key: Optional[str] = None,
        default_headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> None:
        additional_kwargs = additional_kwargs or {}

        api_base = get_from_param_or_env(
            "api_base", api_base, "VERCEL_AI_GATEWAY_API_BASE"
        )

        # Check for API key from multiple sources in order of precedence:
        if api_key is None:
            try:
                api_key = get_from_param_or_env(
                    "api_key", None, "VERCEL_AI_GATEWAY_API_KEY"
                )
            except ValueError:
                try:
                    api_key = get_from_param_or_env(
                        "oidc_token", None, "VERCEL_OIDC_TOKEN"
                    )
                except ValueError:
                    pass

        # Set up required Vercel AI Gateway headers
        gateway_headers = {
            "http-referer": "https://www.llamaindex.ai/",
            "x-title": "LlamaIndex",
        }

        if default_headers:
            gateway_headers.update(default_headers)

        super().__init__(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            api_base=api_base,
            api_key=api_key,
            additional_kwargs=additional_kwargs,
            max_retries=max_retries,
            default_headers=gateway_headers,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        return "VercelAIGateway_LLM"

```
  
---|---
