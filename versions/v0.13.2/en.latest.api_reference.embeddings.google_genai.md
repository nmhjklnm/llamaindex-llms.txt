# Google genai
##  GoogleGenAIEmbedding #
Bases: `BaseEmbedding`
Google GenAI embeddings.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model_name` |  `str` |  Model for embedding. Defaults to "text-embedding-005". |  `'text-embedding-004'`  
`api_key` |  `Optional[str]` |  API key to access the model. Defaults to None. |  `None`  
`embedding_config` |  `Optional[EmbedContentConfigOrDict]` |  Embedding config to access the model. Defaults to None. |  `None`  
`vertexai_config` |  `Optional[VertexAIConfig]` |  Vertex AI config to access the model. Defaults to None. |  `None`  
`http_options` |  `Optional[HttpOptions]` |  HTTP options to access the model. Defaults to None. |  `None`  
`debug_config` |  `Optional[DebugConfig]` |  Debug config to access the model. Defaults to None. |  `None`  
`embed_batch_size` |  `int` |  Batch size for embedding. Defaults to 100. |  `DEFAULT_EMBED_BATCH_SIZE`  
`callback_manager` |  `Optional[CallbackManager]` |  Callback manager to access the model. Defaults to None. |  `None`  
`retries` |  `int` |  Maximum number of retries for API calls. Defaults to 3. |  `3`  
`timeout` |  `int` |  Timeout for API calls in seconds. Defaults to 10. |  `60`  
`retry_min_seconds` |  `float` |  Minimum wait time between retries. Defaults to 1. |  `1`  
`retry_max_seconds` |  `float` |  Maximum wait time between retries. Defaults to 10. |  `60`  
`retry_exponential_base` |  `float` |  Base for exponential backoff calculation. Defaults to 2. |  `2`  
Examples:
`pip install llama-index-embeddings-google-genai`
```
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

embed_model = GoogleGenAIEmbedding(model_name="text-embedding-005", api_key="...")

```

Source code in `llama-index-integrations/embeddings/llama-index-embeddings-google-genai/llama_index/embeddings/google_genai/base.py`

| ```
class GoogleGenAIEmbedding(BaseEmbedding):
    """
    Google GenAI embeddings.

    Args:
        model_name (str): Model for embedding.
            Defaults to "text-embedding-005".
        api_key (Optional[str]): API key to access the model. Defaults to None.
        embedding_config (Optional[types.EmbedContentConfigOrDict]): Embedding config to access the model. Defaults to None.
        vertexai_config (Optional[VertexAIConfig]): Vertex AI config to access the model. Defaults to None.
        http_options (Optional[types.HttpOptions]): HTTP options to access the model. Defaults to None.
        debug_config (Optional[google.genai.client.DebugConfig]): Debug config to access the model. Defaults to None.
        embed_batch_size (int): Batch size for embedding. Defaults to 100.
        callback_manager (Optional[CallbackManager]): Callback manager to access the model. Defaults to None.
        retries (int): Maximum number of retries for API calls. Defaults to 3.
        timeout (int): Timeout for API calls in seconds. Defaults to 10.
        retry_min_seconds (float): Minimum wait time between retries. Defaults to 1.
        retry_max_seconds (float): Maximum wait time between retries. Defaults to 10.
        retry_exponential_base (float): Base for exponential backoff calculation. Defaults to 2.

    Examples:
        `pip install llama-index-embeddings-google-genai`

    ```python
        from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

        embed_model = GoogleGenAIEmbedding(model_name="text-embedding-005", api_key="...")
    ```

    """

    _client: google.genai.Client = PrivateAttr()
    _embedding_config: types.EmbedContentConfigOrDict = PrivateAttr()

    embedding_config: Optional[types.EmbedContentConfigOrDict] = Field(
        default=None, description="""Used to override embedding config."""
    )
    retries: int = Field(default=3, description="Number of retries for embedding.")
    timeout: int = Field(default=10, description="Timeout for embedding.")
    retry_min_seconds: float = Field(
        default=1, description="Minimum wait time between retries."
    )
    retry_max_seconds: float = Field(
        default=10, description="Maximum wait time between retries."
    )
    retry_exponential_base: float = Field(
        default=2, description="Base for exponential backoff calculation."
    )

    def __init__(
        self,
        model_name: str = "text-embedding-004",
        api_key: Optional[str] = None,
        embedding_config: Optional[types.EmbedContentConfigOrDict] = None,
        vertexai_config: Optional[VertexAIConfig] = None,
        http_options: Optional[types.HttpOptions] = None,
        debug_config: Optional[google.genai.client.DebugConfig] = None,
        embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
        callback_manager: Optional[CallbackManager] = None,
        retries: int = 3,
        timeout: int = 60,
        retry_min_seconds: float = 1,
        retry_max_seconds: float = 60,
        retry_exponential_base: float = 2,
        **kwargs: Any,
    ):
        super().__init__(
            model_name=model_name,
            embedding_config=embedding_config,
            embed_batch_size=embed_batch_size,
            callback_manager=callback_manager,
            retries=retries,
            timeout=timeout,
            retry_min_seconds=retry_min_seconds,
            retry_max_seconds=retry_max_seconds,
            retry_exponential_base=retry_exponential_base,
            **kwargs,
        )

        # API keys are optional. The API can be authorised via OAuth (detected
        # environmentally) or by the GOOGLE_API_KEY environment variable.
        api_key = api_key or os.getenv("GOOGLE_API_KEY", None)
        vertexai = vertexai_config is not None or os.getenv(
            "GOOGLE_GENAI_USE_VERTEXAI", False
        )
        project = (vertexai_config or {}).get("project") or os.getenv(
            "GOOGLE_CLOUD_PROJECT", None
        )
        location = (vertexai_config or {}).get("location") or os.getenv(
            "GOOGLE_CLOUD_LOCATION", None
        )

        config_params: Dict[str, Any] = {
            "api_key": api_key,
        }

        if vertexai_config is not None:
            config_params.update(vertexai_config)
            config_params["api_key"] = None
            config_params["vertexai"] = True
        elif vertexai:
            config_params["project"] = project
            config_params["location"] = location
            config_params["api_key"] = None
            config_params["vertexai"] = True

        if http_options:
            config_params["http_options"] = http_options

        if debug_config:
            config_params["debug_config"] = debug_config

        self._client = google.genai.Client(**config_params)

    @classmethod
    def class_name(cls) -> str:
        return "GeminiEmbedding"

    def _embed_texts(
        self, texts: List[str], task_type: Optional[str] = None
    ) -> List[List[float]]:
        """Embed texts."""
        # Set the task type if it is not already set
        if task_type and not self.embedding_config:
            embedding_config = types.EmbedContentConfig(task_type=task_type)
        elif task_type and self.embedding_config:
            embedding_config = dict(self.embedding_config)
            embedding_config["task_type"] = task_type
        else:
            embedding_config = self.embedding_config

        # Create the embedding function with retry logic
        def embed_with_client() -> List[List[float]]:
            results = self._client.models.embed_content(
                model=self.model_name,
                contents=texts,
                config=embedding_config,
            )
            return [result.values for result in results.embeddings]

        # Apply the retry decorator
        retryable_embed = get_retryable_function(
            embed_with_client,
            max_retries=self.retries,
            min_seconds=self.retry_min_seconds,
            max_seconds=self.retry_max_seconds,
            exponential_base=self.retry_exponential_base,
        )

        return retryable_embed()

    async def _aembed_texts(
        self, texts: List[str], task_type: Optional[str] = None
    ) -> List[List[float]]:
        """Asynchronously embed texts."""
        # Set the task type if it is not already set
        if task_type and not self.embedding_config:
            embedding_config = types.EmbedContentConfig(task_type=task_type)
        elif task_type and self.embedding_config:
            embedding_config = dict(self.embedding_config)
            embedding_config["task_type"] = task_type
        else:
            embedding_config = self.embedding_config

        # Create the async embedding function with retry logic
        async def aembed_with_client() -> List[List[float]]:
            results = await self._client.aio.models.embed_content(
                model=self.model_name,
                contents=texts,
                config=embedding_config,
            )
            return [result.values for result in results.embeddings]

        # Apply the async retry helper
        return await get_retryable_async_function(
            aembed_with_client,
            max_retries=self.retries,
            min_seconds=self.retry_min_seconds,
            max_seconds=self.retry_max_seconds,
            exponential_base=self.retry_exponential_base,
        )

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        return self._embed_texts([query], task_type="RETRIEVAL_QUERY")[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        return self._embed_texts([text], task_type="RETRIEVAL_DOCUMENT")[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get text embeddings."""
        return self._embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """The asynchronous version of _get_query_embedding."""
        return (await self._aembed_texts([query], task_type="RETRIEVAL_QUERY"))[0]

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Asynchronously get text embedding."""
        return (await self._aembed_texts([text], task_type="RETRIEVAL_DOCUMENT"))[0]

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get text embeddings."""
        return await self._aembed_texts(texts, task_type="RETRIEVAL_DOCUMENT")

```
  
---|---
