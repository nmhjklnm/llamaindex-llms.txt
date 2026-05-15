# Jinaai
##  JinaEmbedding #
Bases: `MultiModalEmbedding`
JinaAI class for embeddings.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model` |  `str` |  Model for embedding. Defaults to `jina-embeddings-v3` |  `'jina-embeddings-v3'`  
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-jinaai/llama_index/embeddings/jinaai/base.py`

| ```
class JinaEmbedding(MultiModalEmbedding):
    """
    JinaAI class for embeddings.

    Args:
        model (str): Model for embedding.
            Defaults to `jina-embeddings-v3`

    """

    api_key: Optional[str] = Field(default=None, description="The JinaAI API key.")
    model: str = Field(
        default="jina-embeddings-v3",
        description="The model to use when calling Jina AI API",
    )

    _encoding_queries: str = PrivateAttr()
    _encoding_documents: str = PrivateAttr()
    _task: str = PrivateAttr()
    _api: Any = PrivateAttr()

    def __init__(
        self,
        model: str = "jina-embeddings-v3",
        embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
        api_key: Optional[str] = None,
        callback_manager: Optional[CallbackManager] = None,
        encoding_queries: Optional[str] = None,
        encoding_documents: Optional[str] = None,
        task: Optional[str] = None,
        dimensions: Optional[int] = None,
        late_chunking: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            embed_batch_size=embed_batch_size,
            callback_manager=callback_manager,
            model=model,
            api_key=api_key,
            **kwargs,
        )
        self._encoding_queries = encoding_queries or "float"
        self._encoding_documents = encoding_documents or "float"
        self._task = task
        self._dimensions = dimensions
        self._late_chunking = late_chunking

        assert self._encoding_documents in VALID_ENCODING, (
            f"Encoding Documents parameter {self._encoding_documents} not supported. Please choose one of {VALID_ENCODING}"
        )
        assert self._encoding_queries in VALID_ENCODING, (
            f"Encoding Queries parameter {self._encoding_documents} not supported. Please choose one of {VALID_ENCODING}"
        )

        self._api = _JinaAPICaller(model=model, api_key=api_key)

    @classmethod
    def class_name(cls) -> str:
        return "JinaAIEmbedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        return self._api.get_embeddings(
            input=[query],
            encoding_type=self._encoding_queries,
            task=self._task,
            dimensions=self._dimensions,
            late_chunking=self._late_chunking,
        )[0]

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """The asynchronous version of _get_query_embedding."""
        result = await self._api.aget_embeddings(
            input=[query],
            encoding_type=self._encoding_queries,
            task=self._task,
            dimensions=self._dimensions,
            late_chunking=self._late_chunking,
        )
        return result[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        return self._get_text_embeddings([text])[0]

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Asynchronously get text embedding."""
        result = await self._aget_text_embeddings([text])
        return result[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._api.get_embeddings(
            input=texts,
            encoding_type=self._encoding_documents,
            task=self._task,
            dimensions=self._dimensions,
            late_chunking=self._late_chunking,
        )

    async def _aget_text_embeddings(
        self,
        texts: List[str],
    ) -> List[List[float]]:
        return await self._api.aget_embeddings(
            input=texts,
            encoding_type=self._encoding_documents,
            task=self._task,
            dimensions=self._dimensions,
            late_chunking=self._late_chunking,
        )

    def _get_image_embedding(self, img_file_path: ImageType) -> List[float]:
        if is_local(img_file_path):
            input = [{"bytes": get_bytes_str(img_file_path)}]
        else:
            input = [{"url": img_file_path}]
        return self._api.get_embeddings(input=input)[0]

    async def _aget_image_embedding(self, img_file_path: ImageType) -> List[float]:
        if is_local(img_file_path):
            input = [{"bytes": get_bytes_str(img_file_path)}]
        else:
            input = [{"url": img_file_path}]
        return await self._api.aget_embeddings(input=input)[0]

    def _get_image_embeddings(
        self, img_file_paths: List[ImageType]
    ) -> List[List[float]]:
        input = []
        for img_file_path in img_file_paths:
            if is_local(img_file_path):
                input.append({"bytes": get_bytes_str(img_file_path)})
            else:
                input.append({"url": img_file_path})
        return self._api.get_embeddings(input=input)

    async def _aget_image_embeddings(
        self, img_file_paths: List[ImageType]
    ) -> List[List[float]]:
        input = []
        for img_file_path in img_file_paths:
            if is_local(img_file_path):
                input.append({"bytes": get_bytes_str(img_file_path)})
            else:
                input.append({"url": img_file_path})
        return await self._api.aget_embeddings(input=input)

```
  
---|---
