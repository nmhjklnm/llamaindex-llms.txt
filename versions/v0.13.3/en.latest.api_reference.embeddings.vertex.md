# Vertex
##  VertexMultiModalEmbedding #
Bases: `MultiModalEmbedding`
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-vertex/llama_index/embeddings/vertex/base.py`

| ```
class VertexMultiModalEmbedding(MultiModalEmbedding):
    embed_dimension: int = Field(description="The vertex output embedding dimension.")
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Additional kwargs for the Vertex."
    )

    _model: MultiModalEmbeddingModel = PrivateAttr()
    _embed_dimension: int = PrivateAttr()

    def __init__(
        self,
        model_name: str = "multimodalembedding",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[Any] = None,
        embed_dimension: int = 1408,
        embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
        callback_manager: Optional[CallbackManager] = None,
        additional_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        init_vertexai(project=project, location=location, credentials=credentials)
        callback_manager = callback_manager or CallbackManager([])
        additional_kwargs = additional_kwargs or {}

        super().__init__(
            embed_dimension=embed_dimension,
            additional_kwargs=additional_kwargs,
            model_name=model_name,
            embed_batch_size=embed_batch_size,
            callback_manager=callback_manager,
        )
        self._model = MultiModalEmbeddingModel.from_pretrained(model_name)

    @classmethod
    def class_name(cls) -> str:
        return "VertexMultiModalEmbedding"

    def _get_text_embedding(self, text: str) -> Embedding:
        return self._model.get_embeddings(
            contextual_text=text,
            dimension=self.embed_dimension,
            **self.additional_kwargs,
        ).text_embedding

    def _get_image_embedding(self, img_file_path: ImageType) -> Embedding:
        if isinstance(img_file_path, str):
            image = Image.load_from_file(img_file_path)
        else:
            image = Image(image_bytes=img_file_path.getvalue())
        embeddings = self._model.get_embeddings(
            image=image, dimension=self.embed_dimension, **self.additional_kwargs
        )
        return embeddings.image_embedding

    def _get_query_embedding(self, query: str) -> Embedding:
        return self._get_text_embedding(query)

    # Vertex AI SDK does not support async variants yet
    async def _aget_text_embedding(self, text: str) -> Embedding:
        return self._get_text_embedding(text)

    async def _aget_image_embedding(self, img_file_path: ImageType) -> Embedding:
        return self._get_image_embedding(img_file_path)

    async def _aget_query_embedding(self, query: str) -> Embedding:
        return self._get_query_embedding(query)

```
  
---|---  
##  VertexTextEmbedding #
Bases: `BaseEmbedding`
Source code in `llama-index-integrations/embeddings/llama-index-embeddings-vertex/llama_index/embeddings/vertex/base.py`

| ```
class VertexTextEmbedding(BaseEmbedding):
    embed_mode: VertexEmbeddingMode = Field(
        default=VertexEmbeddingMode.RETRIEVAL_MODE,
        description="The embedding mode to use.",
    )
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Additional kwargs for the Vertex."
    )
    client_email: Optional[str] = Field(
        default=None, description="The client email for the VertexAI credentials."
    )
    token_uri: Optional[str] = Field(
        default=None, description="The token URI for the VertexAI credentials."
    )
    private_key_id: Optional[str] = Field(
        default=None, description="The private key ID for the VertexAI credentials."
    )
    private_key: Optional[str] = Field(
        default=None, description="The private key for the VertexAI credentials."
    )

    _model: TextEmbeddingModel = PrivateAttr()

    def __init__(
        self,
        model_name: str = "textembedding-gecko@003",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        embed_mode: VertexEmbeddingMode = VertexEmbeddingMode.RETRIEVAL_MODE,
        embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
        callback_manager: Optional[CallbackManager] = None,
        additional_kwargs: Optional[Dict[str, Any]] = None,
        num_workers: Optional[int] = None,
        client_email: Optional[str] = None,
        token_uri: Optional[str] = None,
        private_key_id: Optional[str] = None,
        private_key: Optional[str] = None,
    ) -> None:
        if credentials is None:
            if client_email and token_uri and private_key_id and private_key:
                info = {
                    "client_email": client_email,
                    "token_uri": token_uri,
                    "private_key_id": private_key_id,
                    "private_key": private_key.replace("\\n", "\n"),
                }
                credentials = service_account.Credentials.from_service_account_info(
                    info
                )
            else:
                raise ValueError(
                    "Either provide credentials or all of client_email, token_uri, private_key_id, and private_key."
                )

        init_vertexai(project=project, location=location, credentials=credentials)
        callback_manager = callback_manager or CallbackManager([])
        additional_kwargs = additional_kwargs or {}

        super().__init__(
            embed_mode=embed_mode,
            project=project,
            location=location,
            credentials=credentials,
            additional_kwargs=additional_kwargs,
            model_name=model_name,
            embed_batch_size=embed_batch_size,
            callback_manager=callback_manager,
            num_workers=num_workers,
            client_email=client_email,
            token_uri=token_uri,
            private_key_id=private_key_id,
            private_key=private_key,
        )

        self._model = TextEmbeddingModel.from_pretrained(model_name)

    @classmethod
    def class_name(cls) -> str:
        return "VertexTextEmbedding"

    def _get_text_embeddings(self, texts: List[str]) -> List[Embedding]:
        texts = _get_embedding_request(
            texts=texts,
            embed_mode=self.embed_mode,
            is_query=False,
            model_name=self.model_name,
        )
        embeddings = self._model.get_embeddings(texts, **self.additional_kwargs)
        return [embedding.values for embedding in embeddings]

    def _get_text_embedding(self, text: str) -> Embedding:
        return self._get_text_embeddings([text])[0]

    async def _aget_text_embedding(self, text: str) -> Embedding:
        return (await self._aget_text_embeddings([text]))[0]

    async def _aget_text_embeddings(self, texts: List[str]) -> List[Embedding]:
        texts = _get_embedding_request(
            texts=texts,
            embed_mode=self.embed_mode,
            is_query=False,
            model_name=self.model_name,
        )
        embeddings = await self._model.get_embeddings_async(
            texts, **self.additional_kwargs
        )
        return [embedding.values for embedding in embeddings]

    def _get_query_embedding(self, query: str) -> Embedding:
        texts = _get_embedding_request(
            texts=[query],
            embed_mode=self.embed_mode,
            is_query=True,
            model_name=self.model_name,
        )
        embeddings = self._model.get_embeddings(texts, **self.additional_kwargs)
        return embeddings[0].values

    async def _aget_query_embedding(self, query: str) -> Embedding:
        texts = _get_embedding_request(
            texts=[query],
            embed_mode=self.embed_mode,
            is_query=True,
            model_name=self.model_name,
        )
        embeddings = await self._model.get_embeddings_async(
            texts, **self.additional_kwargs
        )
        return embeddings[0].values

```
  
---|---
