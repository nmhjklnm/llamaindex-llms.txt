# Nebius
##  NebiusEmbedding #
Bases: `OpenAIEmbedding`
Nebius class for embeddings.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model` |  `str` |  Model for embedding. Defaults to "BAAI/bge-en-icl" |  _required_  
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-nebius/llama_index/embeddings/nebius/base.py`

| ```
class NebiusEmbedding(OpenAIEmbedding):
    """
    Nebius class for embeddings.

    Args:
        model (str): Model for embedding. Defaults to "BAAI/bge-en-icl"

    """

    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Additional kwargs for the OpenAI API."
    )

    api_key: str = Field(description="The Nebius AI Studio API key.")
    api_base: str = Field(description="The base URL for Nebius AI Studio API.")
    api_version: str = Field(description="The version for OpenAI API.")

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        dimensions: Optional[int] = None,
        embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
        additional_kwargs: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        api_base: Optional[str] = DEFAULT_API_BASE,
        api_version: Optional[str] = None,
        max_retries: int = 10,
        timeout: float = 60.0,
        reuse_client: bool = True,
        callback_manager: Optional[CallbackManager] = None,
        default_headers: Optional[Dict[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
        **kwargs: Any,
    ) -> None:
        api_key, api_base, api_version = resolve_nebius_credentials(
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
        )

        super().__init__(
            model_name=model_name,
            dimensions=dimensions,
            embed_batch_size=embed_batch_size,
            additional_kwargs=additional_kwargs,
            api_key=api_key,
            api_base=api_base,
            api_version=api_version,
            max_retries=max_retries,
            timeout=timeout,
            reuse_client=reuse_client,
            callback_manager=callback_manager,
            default_headers=default_headers,
            http_client=http_client,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        return "NebiusEmbedding"

```
  
---|---
