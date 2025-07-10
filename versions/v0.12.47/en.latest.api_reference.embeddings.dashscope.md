# Dashscope
##  DashScopeEmbedding #
Bases: `MultiModalEmbedding`
DashScope class for text embedding.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model_name` |  `str` |  Model name for embedding. Defaults to DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2. Options are: ```
- DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V1
- DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2

```
|  `TEXT_EMBEDDING_V2`  
`text_type` |  `str` |  The input type, ['query', 'document'], For asymmetric tasks such as retrieval, in order to achieve better retrieval results, it is recommended to distinguish between query text (query) and base text (document) types, clustering Symmetric tasks such as classification and classification do not need to be specially specified, and the system default value "document" can be used. |  `'document'`  
`api_key` |  `str` |  The DashScope api key. |  `None`  
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-dashscope/llama_index/embeddings/dashscope/base.py`

| ```
class DashScopeEmbedding(MultiModalEmbedding):
    """
    DashScope class for text embedding.

    Args:
        model_name (str): Model name for embedding.
            Defaults to DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2.
                Options are:

                - DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V1
                - DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2
        text_type (str): The input type, ['query', 'document'],
            For asymmetric tasks such as retrieval, in order to achieve better
            retrieval results, it is recommended to distinguish between query
            text (query) and base text (document) types, clustering Symmetric
            tasks such as classification and classification do not need to
            be specially specified, and the system default
            value "document" can be used.
        api_key (str): The DashScope api key.

    """

    _api_key: Optional[str] = PrivateAttr()
    _text_type: Optional[str] = PrivateAttr()

    def __init__(
        self,
        model_name: str = DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V2,
        text_type: str = "document",
        api_key: Optional[str] = None,
        embed_batch_size: int = EMBED_MAX_BATCH_SIZE,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model_name=model_name,
            embed_batch_size=embed_batch_size,
            **kwargs,
        )
        self._api_key = api_key
        self._text_type = text_type

    @classmethod
    def class_name(cls) -> str:
        return "DashScopeEmbedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        emb = get_text_embedding(
            self.model_name,
            query,
            api_key=self._api_key,
            text_type="query",
        )
        if len(emb) > 0 and emb[0] is not None:
            return emb[0]
        else:
            return []

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        emb = get_text_embedding(
            self.model_name,
            text,
            api_key=self._api_key,
            text_type=self._text_type,
        )
        if len(emb) > 0 and emb[0] is not None:
            return emb[0]
        else:
            return []

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get text embeddings."""
        return get_text_embedding(
            self.model_name,
            texts,
            api_key=self._api_key,
            text_type=self._text_type,
        )

    # TODO: use proper async methods
    async def _aget_text_embedding(self, query: str) -> List[float]:
        """Get text embedding."""
        return self._get_text_embedding(query)

    # TODO: user proper async methods
    async def _aget_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        return self._get_query_embedding(query)

    def get_batch_query_embedding(self, embedding_file_url: str) -> Optional[str]:
        """
        Get batch query embeddings.

        Args:
            embedding_file_url (str): The url of the file to embedding which with lines of text to embedding.

        Returns:
            str: The url of the embedding result, format ref:
                 https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-async-api-details.

        """
        return get_batch_text_embedding(
            self.model_name,
            embedding_file_url,
            api_key=self._api_key,
            text_type=self._text_type,
        )

    def get_batch_text_embedding(self, embedding_file_url: str) -> Optional[str]:
        """
        Get batch text embeddings.

        Args:
            embedding_file_url (str): The url of the file to embedding which with lines of text to embedding.

        Returns:
            str: The url of the embedding result, format ref:
                 https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-async-api-details.

        """
        return get_batch_text_embedding(
            self.model_name,
            embedding_file_url,
            api_key=self._api_key,
            text_type=self._text_type,
        )

    def _get_image_embedding(self, img_file_path: ImageType) -> List[float]:
        """
        Embed the input image synchronously.
        """
        input = [{"image": img_file_path}]
        return get_multimodal_embedding(
            self.model_name, input=input, api_key=self._api_key
        )

    async def _aget_image_embedding(self, img_file_path: ImageType) -> List[float]:
        """
        Embed the input image asynchronously.

        """
        return self._get_image_embedding(img_file_path=img_file_path)

    def get_multimodal_embedding(
        self, input: List[Dict], auto_truncation: bool = False
    ) -> List[float]:
        """
        Call DashScope multimodal embedding.
        ref: https://help.aliyun.com/zh/dashscope/developer-reference/one-peace-multimodal-embedding-api-details.

        Args:
            input (str): The input of the multimodal embedding, eg:
                [{'factor': 1, 'text': '你好'},
                {'factor': 2, 'audio': 'https://dashscope.oss-cn-beijing.aliyuncs.com/audios/cow.flac'},
                {'factor': 3, 'image': 'https://dashscope.oss-cn-beijing.aliyuncs.com/images/256_1.png'}]

        Raises:
            ImportError: Need install dashscope package.

        Returns:
            List[float]: The embedding result

        """
        return get_multimodal_embedding(
            self.model_name,
            input=input,
            api_key=self._api_key,
            auto_truncation=auto_truncation,
        )

```
  
---|---  
###  get_batch_query_embedding #
```
get_batch_query_embedding(embedding_file_url: str) -> Optional[str]

```

Get batch query embeddings.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`embedding_file_url` |  `str` |  The url of the file to embedding which with lines of text to embedding. |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `Optional[str]` |  The url of the embedding result, format ref: https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-async-api-details.  
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-dashscope/llama_index/embeddings/dashscope/base.py`

| ```
def get_batch_query_embedding(self, embedding_file_url: str) -> Optional[str]:
    """
    Get batch query embeddings.

    Args:
        embedding_file_url (str): The url of the file to embedding which with lines of text to embedding.

    Returns:
        str: The url of the embedding result, format ref:
             https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-async-api-details.

    """
    return get_batch_text_embedding(
        self.model_name,
        embedding_file_url,
        api_key=self._api_key,
        text_type=self._text_type,
    )

```
  
---|---  
###  get_batch_text_embedding #
```
get_batch_text_embedding(embedding_file_url: str) -> Optional[str]

```

Get batch text embeddings.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`embedding_file_url` |  `str` |  The url of the file to embedding which with lines of text to embedding. |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `Optional[str]` |  The url of the embedding result, format ref: https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-async-api-details.  
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-dashscope/llama_index/embeddings/dashscope/base.py`

| ```
def get_batch_text_embedding(self, embedding_file_url: str) -> Optional[str]:
    """
    Get batch text embeddings.

    Args:
        embedding_file_url (str): The url of the file to embedding which with lines of text to embedding.

    Returns:
        str: The url of the embedding result, format ref:
             https://help.aliyun.com/zh/dashscope/developer-reference/text-embedding-async-api-details.

    """
    return get_batch_text_embedding(
        self.model_name,
        embedding_file_url,
        api_key=self._api_key,
        text_type=self._text_type,
    )

```
  
---|---  
###  get_multimodal_embedding #
```
get_multimodal_embedding(input: List[Dict], auto_truncation: bool = False) -> List[float]

```

Call DashScope multimodal embedding. ref: https://help.aliyun.com/zh/dashscope/developer-reference/one-peace-multimodal-embedding-api-details.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`input` |  `str` |  The input of the multimodal embedding, eg: [{'factor': 1, 'text': '你好'}, {'factor': 2, 'audio': 'https://dashscope.oss-cn-beijing.aliyuncs.com/audios/cow.flac'}, {'factor': 3, 'image': 'https://dashscope.oss-cn-beijing.aliyuncs.com/images/256_1.png'}] |  _required_  
Raises:
Type | Description  
---|---  
`ImportError` |  Need install dashscope package.  
Returns:
Type | Description  
---|---  
`List[float]` |  List[float]: The embedding result  
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-dashscope/llama_index/embeddings/dashscope/base.py`

| ```
def get_multimodal_embedding(
    self, input: List[Dict], auto_truncation: bool = False
) -> List[float]:
    """
    Call DashScope multimodal embedding.
    ref: https://help.aliyun.com/zh/dashscope/developer-reference/one-peace-multimodal-embedding-api-details.

    Args:
        input (str): The input of the multimodal embedding, eg:
            [{'factor': 1, 'text': '你好'},
            {'factor': 2, 'audio': 'https://dashscope.oss-cn-beijing.aliyuncs.com/audios/cow.flac'},
            {'factor': 3, 'image': 'https://dashscope.oss-cn-beijing.aliyuncs.com/images/256_1.png'}]

    Raises:
        ImportError: Need install dashscope package.

    Returns:
        List[float]: The embedding result

    """
    return get_multimodal_embedding(
        self.model_name,
        input=input,
        api_key=self._api_key,
        auto_truncation=auto_truncation,
    )

```
  
---|---
