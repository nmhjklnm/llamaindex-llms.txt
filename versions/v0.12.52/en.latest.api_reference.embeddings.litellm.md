# Litellm
##  LiteLLMEmbedding #
Bases: `BaseEmbedding`
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-litellm/llama_index/embeddings/litellm/base.py`

| ```
class LiteLLMEmbedding(BaseEmbedding):
    model_name: str = Field(description="The name of the embedding model.")
    api_key: Optional[str] = Field(
        default=None,
        description="OpenAI key. If not provided, the proxy server must be configured with the key.",
    )
    api_base: Optional[str] = Field(
        default=None, description="The base URL of the LiteLLM proxy."
    )
    dimensions: Optional[int] = Field(
        default=None,
        description=(
            "The number of dimensions the resulting output embeddings should have. "
            "Only supported in text-embedding-3 and later models."
        ),
    )
    timeout: Optional[int] = Field(
        default=60, description="Timeout for each request.", ge=0
    )

    @classmethod
    def class_name(cls) -> str:
        return "lite-llm"

    async def _aget_query_embedding(self, query: str) -> List[float]:
        return self._get_query_embedding(query)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        return self._get_text_embedding(text)

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = get_embeddings(
            api_key=self.api_key,
            api_base=self.api_base,
            model_name=self.model_name,
            dimensions=self.dimensions,
            timeout=self.timeout,
            input=[query],
        )
        return embeddings[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = get_embeddings(
            api_key=self.api_key,
            api_base=self.api_base,
            model_name=self.model_name,
            dimensions=self.dimensions,
            timeout=self.timeout,
            input=[text],
        )
        return embeddings[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return get_embeddings(
            api_key=self.api_key,
            api_base=self.api_base,
            model_name=self.model_name,
            dimensions=self.dimensions,
            timeout=self.timeout,
            input=texts,
        )

```
  
---|---
