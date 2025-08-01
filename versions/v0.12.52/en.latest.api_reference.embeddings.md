# Index
##  BaseEmbedding #
Bases: `TransformComponent`, `DispatcherSpanMixin`
Base class for embeddings.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model_name` |  `str` |  The name of the embedding model. |  `'unknown'`  
`embed_batch_size` |  `int` |  The batch size for embedding calls. |  `10`  
`callback_manager` |  `CallbackManager` |  |  `<llama_index.core.callbacks.base.CallbackManager object at 0x7132fb2bca10>`  
`num_workers` |  `int | None` |  The number of workers to use for async embedding calls. |  `None`  
`embeddings_cache` |  `Any | None` |  Cache for the embeddings: if None, the embeddings are not cached |  `None`  
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
class BaseEmbedding(TransformComponent, DispatcherSpanMixin):
    """Base class for embeddings."""

    model_config = ConfigDict(
        protected_namespaces=("pydantic_model_",), arbitrary_types_allowed=True
    )
    model_name: str = Field(
        default="unknown", description="The name of the embedding model."
    )
    embed_batch_size: int = Field(
        default=DEFAULT_EMBED_BATCH_SIZE,
        description="The batch size for embedding calls.",
        gt=0,
        le=2048,
    )
    callback_manager: CallbackManager = Field(
        default_factory=lambda: CallbackManager([]), exclude=True
    )
    num_workers: Optional[int] = Field(
        default=None,
        description="The number of workers to use for async embedding calls.",
    )
    embeddings_cache: Optional[Any] = Field(
        default=None,
        description="Cache for the embeddings: if None, the embeddings are not cached",
    )

    @model_validator(mode="after")
    def check_base_embeddings_class(self) -> Self:
        from llama_index.core.storage.kvstore.types import BaseKVStore

        if self.callback_manager is None:
            self.callback_manager = CallbackManager([])
        if self.embeddings_cache is not None and not isinstance(
            self.embeddings_cache, BaseKVStore
        ):
            raise TypeError("embeddings_cache must be of type BaseKVStore")
        return self

    @abstractmethod
    def _get_query_embedding(self, query: str) -> Embedding:
        """
        Embed the input query synchronously.

        Subclasses should implement this method. Reference get_query_embedding's
        docstring for more information.
        """

    @abstractmethod
    async def _aget_query_embedding(self, query: str) -> Embedding:
        """
        Embed the input query asynchronously.

        Subclasses should implement this method. Reference get_query_embedding's
        docstring for more information.
        """

    @dispatcher.span
    def get_query_embedding(self, query: str) -> Embedding:
        """
        Embed the input query.

        When embedding a query, depending on the model, a special instruction
        can be prepended to the raw query string. For example, "Represent the
        question for retrieving supporting documents: ". If you're curious,
        other examples of predefined instructions can be found in
        embeddings/huggingface_utils.py.
        """
        model_dict = self.to_dict()
        model_dict.pop("api_key", None)
        dispatcher.event(
            EmbeddingStartEvent(
                model_dict=model_dict,
            )
        )
        with self.callback_manager.event(
            CBEventType.EMBEDDING, payload={EventPayload.SERIALIZED: self.to_dict()}
        ) as event:
            if not self.embeddings_cache:
                query_embedding = self._get_query_embedding(query)
            elif self.embeddings_cache is not None:
                cached_emb = self.embeddings_cache.get(
                    key=query, collection="embeddings"
                )
                if cached_emb is not None:
                    cached_key = next(iter(cached_emb.keys()))
                    query_embedding = cached_emb[cached_key]
                else:
                    query_embedding = self._get_query_embedding(query)
                    self.embeddings_cache.put(
                        key=query,
                        val={str(uuid.uuid4()): query_embedding},
                        collection="embeddings",
                    )
            event.on_end(
                payload={
                    EventPayload.CHUNKS: [query],
                    EventPayload.EMBEDDINGS: [query_embedding],
                },
            )
        dispatcher.event(
            EmbeddingEndEvent(
                chunks=[query],
                embeddings=[query_embedding],
            )
        )
        return query_embedding

    @dispatcher.span
    async def aget_query_embedding(self, query: str) -> Embedding:
        """Get query embedding."""
        model_dict = self.to_dict()
        model_dict.pop("api_key", None)
        dispatcher.event(
            EmbeddingStartEvent(
                model_dict=model_dict,
            )
        )
        with self.callback_manager.event(
            CBEventType.EMBEDDING, payload={EventPayload.SERIALIZED: self.to_dict()}
        ) as event:
            if not self.embeddings_cache:
                query_embedding = await self._aget_query_embedding(query)
            elif self.embeddings_cache is not None:
                cached_emb = await self.embeddings_cache.aget(
                    key=query, collection="embeddings"
                )
                if cached_emb is not None:
                    cached_key = next(iter(cached_emb.keys()))
                    query_embedding = cached_emb[cached_key]
                else:
                    query_embedding = await self._aget_query_embedding(query)
                    await self.embeddings_cache.aput(
                        key=query,
                        val={str(uuid.uuid4()): query_embedding},
                        collection="embeddings",
                    )

            event.on_end(
                payload={
                    EventPayload.CHUNKS: [query],
                    EventPayload.EMBEDDINGS: [query_embedding],
                },
            )
        dispatcher.event(
            EmbeddingEndEvent(
                chunks=[query],
                embeddings=[query_embedding],
            )
        )
        return query_embedding

    def get_agg_embedding_from_queries(
        self,
        queries: List[str],
        agg_fn: Optional[Callable[..., Embedding]] = None,
    ) -> Embedding:
        """Get aggregated embedding from multiple queries."""
        query_embeddings = [self.get_query_embedding(query) for query in queries]
        agg_fn = agg_fn or mean_agg
        return agg_fn(query_embeddings)

    async def aget_agg_embedding_from_queries(
        self,
        queries: List[str],
        agg_fn: Optional[Callable[..., Embedding]] = None,
    ) -> Embedding:
        """Async get aggregated embedding from multiple queries."""
        query_embeddings = [await self.aget_query_embedding(query) for query in queries]
        agg_fn = agg_fn or mean_agg
        return agg_fn(query_embeddings)

    @abstractmethod
    def _get_text_embedding(self, text: str) -> Embedding:
        """
        Embed the input text synchronously.

        Subclasses should implement this method. Reference get_text_embedding's
        docstring for more information.
        """

    async def _aget_text_embedding(self, text: str) -> Embedding:
        """
        Embed the input text asynchronously.

        Subclasses can implement this method if there is a true async
        implementation. Reference get_text_embedding's docstring for more
        information.
        """
        # Default implementation just falls back on _get_text_embedding
        return self._get_text_embedding(text)

    def _get_text_embeddings(self, texts: List[str]) -> List[Embedding]:
        """
        Embed the input sequence of text synchronously.

        Subclasses can implement this method if batch queries are supported.
        """
        # Default implementation just loops over _get_text_embedding
        return [self._get_text_embedding(text) for text in texts]

    async def _aget_text_embeddings(self, texts: List[str]) -> List[Embedding]:
        """
        Embed the input sequence of text asynchronously.

        Subclasses can implement this method if batch queries are supported.
        """
        return await asyncio.gather(
            *[self._aget_text_embedding(text) for text in texts]
        )

    @dispatcher.span
    def get_text_embedding(self, text: str) -> Embedding:
        """
        Embed the input text.

        When embedding text, depending on the model, a special instruction
        can be prepended to the raw text string. For example, "Represent the
        document for retrieval: ". If you're curious, other examples of
        predefined instructions can be found in embeddings/huggingface_utils.py.
        """
        model_dict = self.to_dict()
        model_dict.pop("api_key", None)
        dispatcher.event(
            EmbeddingStartEvent(
                model_dict=model_dict,
            )
        )
        with self.callback_manager.event(
            CBEventType.EMBEDDING, payload={EventPayload.SERIALIZED: self.to_dict()}
        ) as event:
            if not self.embeddings_cache:
                text_embedding = self._get_text_embedding(text)
            elif self.embeddings_cache is not None:
                cached_emb = self.embeddings_cache.get(
                    key=text, collection="embeddings"
                )
                if cached_emb is not None:
                    cached_key = next(iter(cached_emb.keys()))
                    text_embedding = cached_emb[cached_key]
                else:
                    text_embedding = self._get_text_embedding(text)
                    self.embeddings_cache.put(
                        key=text,
                        val={str(uuid.uuid4()): text_embedding},
                        collection="embeddings",
                    )

            event.on_end(
                payload={
                    EventPayload.CHUNKS: [text],
                    EventPayload.EMBEDDINGS: [text_embedding],
                }
            )
        dispatcher.event(
            EmbeddingEndEvent(
                chunks=[text],
                embeddings=[text_embedding],
            )
        )
        return text_embedding

    @dispatcher.span
    async def aget_text_embedding(self, text: str) -> Embedding:
        """Async get text embedding."""
        model_dict = self.to_dict()
        model_dict.pop("api_key", None)
        dispatcher.event(
            EmbeddingStartEvent(
                model_dict=model_dict,
            )
        )
        with self.callback_manager.event(
            CBEventType.EMBEDDING, payload={EventPayload.SERIALIZED: self.to_dict()}
        ) as event:
            if not self.embeddings_cache:
                text_embedding = await self._aget_text_embedding(text)
            elif self.embeddings_cache is not None:
                cached_emb = await self.embeddings_cache.aget(
                    key=text, collection="embeddings"
                )
                if cached_emb is not None:
                    cached_key = next(iter(cached_emb.keys()))
                    text_embedding = cached_emb[cached_key]
                else:
                    text_embedding = await self._aget_text_embedding(text)
                    await self.embeddings_cache.aput(
                        key=text,
                        val={str(uuid.uuid4()): text_embedding},
                        collection="embeddings",
                    )

            event.on_end(
                payload={
                    EventPayload.CHUNKS: [text],
                    EventPayload.EMBEDDINGS: [text_embedding],
                }
            )
        dispatcher.event(
            EmbeddingEndEvent(
                chunks=[text],
                embeddings=[text_embedding],
            )
        )
        return text_embedding

    @dispatcher.span
    def get_text_embedding_batch(
        self,
        texts: List[str],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[Embedding]:
        """Get a list of text embeddings, with batching."""
        cur_batch: List[str] = []
        result_embeddings: List[Embedding] = []

        queue_with_progress = enumerate(
            get_tqdm_iterable(texts, show_progress, "Generating embeddings")
        )

        model_dict = self.to_dict()
        model_dict.pop("api_key", None)
        for idx, text in queue_with_progress:
            cur_batch.append(text)
            if idx == len(texts) - 1 or len(cur_batch) == self.embed_batch_size:
                # flush
                dispatcher.event(
                    EmbeddingStartEvent(
                        model_dict=model_dict,
                    )
                )
                with self.callback_manager.event(
                    CBEventType.EMBEDDING,
                    payload={EventPayload.SERIALIZED: self.to_dict()},
                ) as event:
                    if not self.embeddings_cache:
                        embeddings = self._get_text_embeddings(cur_batch)
                    elif self.embeddings_cache is not None:
                        embeddings = []
                        for txt in cur_batch:
                            cached_emb = self.embeddings_cache.get(
                                key=txt, collection="embeddings"
                            )
                            if cached_emb is not None:
                                cached_key = next(iter(cached_emb.keys()))
                                embeddings.append(cached_emb[cached_key])
                            else:
                                text_embedding = self._get_text_embedding(txt)
                                embeddings.append(text_embedding)
                                self.embeddings_cache.put(
                                    key=txt,
                                    val={str(uuid.uuid4()): text_embedding},
                                    collection="embeddings",
                                )
                    result_embeddings.extend(embeddings)
                    event.on_end(
                        payload={
                            EventPayload.CHUNKS: cur_batch,
                            EventPayload.EMBEDDINGS: embeddings,
                        },
                    )
                dispatcher.event(
                    EmbeddingEndEvent(
                        chunks=cur_batch,
                        embeddings=embeddings,
                    )
                )
                cur_batch = []

        return result_embeddings

    @dispatcher.span
    async def aget_text_embedding_batch(
        self, texts: List[str], show_progress: bool = False
    ) -> List[Embedding]:
        """Asynchronously get a list of text embeddings, with batching."""
        num_workers = self.num_workers

        model_dict = self.to_dict()
        model_dict.pop("api_key", None)

        cur_batch: List[str] = []
        pre_recorded_embs: List[Embedding] = []
        non_cached_txts: List[str] = []
        callback_payloads: List[Tuple[str, List[str]]] = []
        result_embeddings: List[Embedding] = []
        embeddings_coroutines: List[Coroutine] = []
        for idx, text in enumerate(texts):
            cur_batch.append(text)
            if idx == len(texts) - 1 or len(cur_batch) == self.embed_batch_size:
                # flush
                dispatcher.event(
                    EmbeddingStartEvent(
                        model_dict=model_dict,
                    )
                )
                event_id = self.callback_manager.on_event_start(
                    CBEventType.EMBEDDING,
                    payload={EventPayload.SERIALIZED: self.to_dict()},
                )
                callback_payloads.append((event_id, cur_batch))
                if not self.embeddings_cache:
                    embeddings_coroutines.append(self._aget_text_embeddings(cur_batch))
                elif self.embeddings_cache is not None:
                    for txt in cur_batch:
                        cached_emb = self.embeddings_cache.get(
                            key=txt, collection="embeddings"
                        )
                        if cached_emb is not None:
                            cached_key = next(iter(cached_emb.keys()))
                            pre_recorded_embs.append(cached_emb[cached_key])
                        else:
                            embeddings_coroutines.append(
                                self._aget_text_embeddings([txt])
                            )
                            non_cached_txts.append(txt)

                cur_batch = []

        # flatten the results of asyncio.gather, which is a list of embeddings lists
        nested_embeddings = []

        if len(embeddings_coroutines) > 0:
            if num_workers and num_workers > 1:
                nested_embeddings = await run_jobs(
                    embeddings_coroutines,
                    show_progress=show_progress,
                    workers=self.num_workers,
                    desc="Generating embeddings",
                )
            else:
                if show_progress:
                    try:
                        from tqdm.asyncio import tqdm_asyncio

                        nested_embeddings = await tqdm_asyncio.gather(
                            *embeddings_coroutines,
                            total=len(embeddings_coroutines),
                            desc="Generating embeddings",
                        )
                    except ImportError:
                        nested_embeddings = await asyncio.gather(*embeddings_coroutines)
                else:
                    nested_embeddings = await asyncio.gather(*embeddings_coroutines)

        result_embeddings = [
            embedding for embeddings in nested_embeddings for embedding in embeddings
        ]
        if self.embeddings_cache is not None:
            if len(result_embeddings) > 0:
                for j in range(len(result_embeddings)):
                    self.embeddings_cache.put(
                        key=non_cached_txts[j],
                        val={str(uuid.uuid4()): result_embeddings[j]},
                        collection="embeddings",
                    )
                result_embeddings += pre_recorded_embs
            else:
                result_embeddings += pre_recorded_embs

        for (event_id, text_batch), embeddings in zip(
            callback_payloads, nested_embeddings
        ):
            dispatcher.event(
                EmbeddingEndEvent(
                    chunks=text_batch,
                    embeddings=embeddings,
                )
            )
            self.callback_manager.on_event_end(
                CBEventType.EMBEDDING,
                payload={
                    EventPayload.CHUNKS: text_batch,
                    EventPayload.EMBEDDINGS: embeddings,
                },
                event_id=event_id,
            )

        return result_embeddings

    def similarity(
        self,
        embedding1: Embedding,
        embedding2: Embedding,
        mode: SimilarityMode = SimilarityMode.DEFAULT,
    ) -> float:
        """Get embedding similarity."""
        return similarity(embedding1=embedding1, embedding2=embedding2, mode=mode)

    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:
        embeddings = self.get_text_embedding_batch(
            [node.get_content(metadata_mode=MetadataMode.EMBED) for node in nodes],
            **kwargs,
        )

        for node, embedding in zip(nodes, embeddings):
            node.embedding = embedding

        return nodes

    async def acall(
        self, nodes: Sequence[BaseNode], **kwargs: Any
    ) -> Sequence[BaseNode]:
        embeddings = await self.aget_text_embedding_batch(
            [node.get_content(metadata_mode=MetadataMode.EMBED) for node in nodes],
            **kwargs,
        )

        for node, embedding in zip(nodes, embeddings):
            node.embedding = embedding

        return nodes

```
  
---|---  
###  get_query_embedding #
```
get_query_embedding(query: str) -> Embedding

```

Embed the input query.
When embedding a query, depending on the model, a special instruction can be prepended to the raw query string. For example, "Represent the question for retrieving supporting documents: ". If you're curious, other examples of predefined instructions can be found in embeddings/huggingface_utils.py.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
@dispatcher.span
def get_query_embedding(self, query: str) -> Embedding:
    """
    Embed the input query.

    When embedding a query, depending on the model, a special instruction
    can be prepended to the raw query string. For example, "Represent the
    question for retrieving supporting documents: ". If you're curious,
    other examples of predefined instructions can be found in
    embeddings/huggingface_utils.py.
    """
    model_dict = self.to_dict()
    model_dict.pop("api_key", None)
    dispatcher.event(
        EmbeddingStartEvent(
            model_dict=model_dict,
        )
    )
    with self.callback_manager.event(
        CBEventType.EMBEDDING, payload={EventPayload.SERIALIZED: self.to_dict()}
    ) as event:
        if not self.embeddings_cache:
            query_embedding = self._get_query_embedding(query)
        elif self.embeddings_cache is not None:
            cached_emb = self.embeddings_cache.get(
                key=query, collection="embeddings"
            )
            if cached_emb is not None:
                cached_key = next(iter(cached_emb.keys()))
                query_embedding = cached_emb[cached_key]
            else:
                query_embedding = self._get_query_embedding(query)
                self.embeddings_cache.put(
                    key=query,
                    val={str(uuid.uuid4()): query_embedding},
                    collection="embeddings",
                )
        event.on_end(
            payload={
                EventPayload.CHUNKS: [query],
                EventPayload.EMBEDDINGS: [query_embedding],
            },
        )
    dispatcher.event(
        EmbeddingEndEvent(
            chunks=[query],
            embeddings=[query_embedding],
        )
    )
    return query_embedding

```
  
---|---  
###  aget_query_embedding `async` #
```
aget_query_embedding(query: str) -> Embedding

```

Get query embedding.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
@dispatcher.span
async def aget_query_embedding(self, query: str) -> Embedding:
    """Get query embedding."""
    model_dict = self.to_dict()
    model_dict.pop("api_key", None)
    dispatcher.event(
        EmbeddingStartEvent(
            model_dict=model_dict,
        )
    )
    with self.callback_manager.event(
        CBEventType.EMBEDDING, payload={EventPayload.SERIALIZED: self.to_dict()}
    ) as event:
        if not self.embeddings_cache:
            query_embedding = await self._aget_query_embedding(query)
        elif self.embeddings_cache is not None:
            cached_emb = await self.embeddings_cache.aget(
                key=query, collection="embeddings"
            )
            if cached_emb is not None:
                cached_key = next(iter(cached_emb.keys()))
                query_embedding = cached_emb[cached_key]
            else:
                query_embedding = await self._aget_query_embedding(query)
                await self.embeddings_cache.aput(
                    key=query,
                    val={str(uuid.uuid4()): query_embedding},
                    collection="embeddings",
                )

        event.on_end(
            payload={
                EventPayload.CHUNKS: [query],
                EventPayload.EMBEDDINGS: [query_embedding],
            },
        )
    dispatcher.event(
        EmbeddingEndEvent(
            chunks=[query],
            embeddings=[query_embedding],
        )
    )
    return query_embedding

```
  
---|---  
###  get_agg_embedding_from_queries #
```
get_agg_embedding_from_queries(queries: List[str], agg_fn: Optional[Callable[..., Embedding]] = None) -> Embedding

```

Get aggregated embedding from multiple queries.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
def get_agg_embedding_from_queries(
    self,
    queries: List[str],
    agg_fn: Optional[Callable[..., Embedding]] = None,
) -> Embedding:
    """Get aggregated embedding from multiple queries."""
    query_embeddings = [self.get_query_embedding(query) for query in queries]
    agg_fn = agg_fn or mean_agg
    return agg_fn(query_embeddings)

```
  
---|---  
###  aget_agg_embedding_from_queries `async` #
```
aget_agg_embedding_from_queries(queries: List[str], agg_fn: Optional[Callable[..., Embedding]] = None) -> Embedding

```

Async get aggregated embedding from multiple queries.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
async def aget_agg_embedding_from_queries(
    self,
    queries: List[str],
    agg_fn: Optional[Callable[..., Embedding]] = None,
) -> Embedding:
    """Async get aggregated embedding from multiple queries."""
    query_embeddings = [await self.aget_query_embedding(query) for query in queries]
    agg_fn = agg_fn or mean_agg
    return agg_fn(query_embeddings)

```
  
---|---  
###  get_text_embedding #
```
get_text_embedding(text: str) -> Embedding

```

Embed the input text.
When embedding text, depending on the model, a special instruction can be prepended to the raw text string. For example, "Represent the document for retrieval: ". If you're curious, other examples of predefined instructions can be found in embeddings/huggingface_utils.py.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
@dispatcher.span
def get_text_embedding(self, text: str) -> Embedding:
    """
    Embed the input text.

    When embedding text, depending on the model, a special instruction
    can be prepended to the raw text string. For example, "Represent the
    document for retrieval: ". If you're curious, other examples of
    predefined instructions can be found in embeddings/huggingface_utils.py.
    """
    model_dict = self.to_dict()
    model_dict.pop("api_key", None)
    dispatcher.event(
        EmbeddingStartEvent(
            model_dict=model_dict,
        )
    )
    with self.callback_manager.event(
        CBEventType.EMBEDDING, payload={EventPayload.SERIALIZED: self.to_dict()}
    ) as event:
        if not self.embeddings_cache:
            text_embedding = self._get_text_embedding(text)
        elif self.embeddings_cache is not None:
            cached_emb = self.embeddings_cache.get(
                key=text, collection="embeddings"
            )
            if cached_emb is not None:
                cached_key = next(iter(cached_emb.keys()))
                text_embedding = cached_emb[cached_key]
            else:
                text_embedding = self._get_text_embedding(text)
                self.embeddings_cache.put(
                    key=text,
                    val={str(uuid.uuid4()): text_embedding},
                    collection="embeddings",
                )

        event.on_end(
            payload={
                EventPayload.CHUNKS: [text],
                EventPayload.EMBEDDINGS: [text_embedding],
            }
        )
    dispatcher.event(
        EmbeddingEndEvent(
            chunks=[text],
            embeddings=[text_embedding],
        )
    )
    return text_embedding

```
  
---|---  
###  aget_text_embedding `async` #
```
aget_text_embedding(text: str) -> Embedding

```

Async get text embedding.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
@dispatcher.span
async def aget_text_embedding(self, text: str) -> Embedding:
    """Async get text embedding."""
    model_dict = self.to_dict()
    model_dict.pop("api_key", None)
    dispatcher.event(
        EmbeddingStartEvent(
            model_dict=model_dict,
        )
    )
    with self.callback_manager.event(
        CBEventType.EMBEDDING, payload={EventPayload.SERIALIZED: self.to_dict()}
    ) as event:
        if not self.embeddings_cache:
            text_embedding = await self._aget_text_embedding(text)
        elif self.embeddings_cache is not None:
            cached_emb = await self.embeddings_cache.aget(
                key=text, collection="embeddings"
            )
            if cached_emb is not None:
                cached_key = next(iter(cached_emb.keys()))
                text_embedding = cached_emb[cached_key]
            else:
                text_embedding = await self._aget_text_embedding(text)
                await self.embeddings_cache.aput(
                    key=text,
                    val={str(uuid.uuid4()): text_embedding},
                    collection="embeddings",
                )

        event.on_end(
            payload={
                EventPayload.CHUNKS: [text],
                EventPayload.EMBEDDINGS: [text_embedding],
            }
        )
    dispatcher.event(
        EmbeddingEndEvent(
            chunks=[text],
            embeddings=[text_embedding],
        )
    )
    return text_embedding

```
  
---|---  
###  get_text_embedding_batch #
```
get_text_embedding_batch(texts: List[str], show_progress: bool = False, **kwargs: Any) -> List[Embedding]

```

Get a list of text embeddings, with batching.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
@dispatcher.span
def get_text_embedding_batch(
    self,
    texts: List[str],
    show_progress: bool = False,
    **kwargs: Any,
) -> List[Embedding]:
    """Get a list of text embeddings, with batching."""
    cur_batch: List[str] = []
    result_embeddings: List[Embedding] = []

    queue_with_progress = enumerate(
        get_tqdm_iterable(texts, show_progress, "Generating embeddings")
    )

    model_dict = self.to_dict()
    model_dict.pop("api_key", None)
    for idx, text in queue_with_progress:
        cur_batch.append(text)
        if idx == len(texts) - 1 or len(cur_batch) == self.embed_batch_size:
            # flush
            dispatcher.event(
                EmbeddingStartEvent(
                    model_dict=model_dict,
                )
            )
            with self.callback_manager.event(
                CBEventType.EMBEDDING,
                payload={EventPayload.SERIALIZED: self.to_dict()},
            ) as event:
                if not self.embeddings_cache:
                    embeddings = self._get_text_embeddings(cur_batch)
                elif self.embeddings_cache is not None:
                    embeddings = []
                    for txt in cur_batch:
                        cached_emb = self.embeddings_cache.get(
                            key=txt, collection="embeddings"
                        )
                        if cached_emb is not None:
                            cached_key = next(iter(cached_emb.keys()))
                            embeddings.append(cached_emb[cached_key])
                        else:
                            text_embedding = self._get_text_embedding(txt)
                            embeddings.append(text_embedding)
                            self.embeddings_cache.put(
                                key=txt,
                                val={str(uuid.uuid4()): text_embedding},
                                collection="embeddings",
                            )
                result_embeddings.extend(embeddings)
                event.on_end(
                    payload={
                        EventPayload.CHUNKS: cur_batch,
                        EventPayload.EMBEDDINGS: embeddings,
                    },
                )
            dispatcher.event(
                EmbeddingEndEvent(
                    chunks=cur_batch,
                    embeddings=embeddings,
                )
            )
            cur_batch = []

    return result_embeddings

```
  
---|---  
###  aget_text_embedding_batch `async` #
```
aget_text_embedding_batch(texts: List[str], show_progress: bool = False) -> List[Embedding]

```

Asynchronously get a list of text embeddings, with batching.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
@dispatcher.span
async def aget_text_embedding_batch(
    self, texts: List[str], show_progress: bool = False
) -> List[Embedding]:
    """Asynchronously get a list of text embeddings, with batching."""
    num_workers = self.num_workers

    model_dict = self.to_dict()
    model_dict.pop("api_key", None)

    cur_batch: List[str] = []
    pre_recorded_embs: List[Embedding] = []
    non_cached_txts: List[str] = []
    callback_payloads: List[Tuple[str, List[str]]] = []
    result_embeddings: List[Embedding] = []
    embeddings_coroutines: List[Coroutine] = []
    for idx, text in enumerate(texts):
        cur_batch.append(text)
        if idx == len(texts) - 1 or len(cur_batch) == self.embed_batch_size:
            # flush
            dispatcher.event(
                EmbeddingStartEvent(
                    model_dict=model_dict,
                )
            )
            event_id = self.callback_manager.on_event_start(
                CBEventType.EMBEDDING,
                payload={EventPayload.SERIALIZED: self.to_dict()},
            )
            callback_payloads.append((event_id, cur_batch))
            if not self.embeddings_cache:
                embeddings_coroutines.append(self._aget_text_embeddings(cur_batch))
            elif self.embeddings_cache is not None:
                for txt in cur_batch:
                    cached_emb = self.embeddings_cache.get(
                        key=txt, collection="embeddings"
                    )
                    if cached_emb is not None:
                        cached_key = next(iter(cached_emb.keys()))
                        pre_recorded_embs.append(cached_emb[cached_key])
                    else:
                        embeddings_coroutines.append(
                            self._aget_text_embeddings([txt])
                        )
                        non_cached_txts.append(txt)

            cur_batch = []

    # flatten the results of asyncio.gather, which is a list of embeddings lists
    nested_embeddings = []

    if len(embeddings_coroutines) > 0:
        if num_workers and num_workers > 1:
            nested_embeddings = await run_jobs(
                embeddings_coroutines,
                show_progress=show_progress,
                workers=self.num_workers,
                desc="Generating embeddings",
            )
        else:
            if show_progress:
                try:
                    from tqdm.asyncio import tqdm_asyncio

                    nested_embeddings = await tqdm_asyncio.gather(
                        *embeddings_coroutines,
                        total=len(embeddings_coroutines),
                        desc="Generating embeddings",
                    )
                except ImportError:
                    nested_embeddings = await asyncio.gather(*embeddings_coroutines)
            else:
                nested_embeddings = await asyncio.gather(*embeddings_coroutines)

    result_embeddings = [
        embedding for embeddings in nested_embeddings for embedding in embeddings
    ]
    if self.embeddings_cache is not None:
        if len(result_embeddings) > 0:
            for j in range(len(result_embeddings)):
                self.embeddings_cache.put(
                    key=non_cached_txts[j],
                    val={str(uuid.uuid4()): result_embeddings[j]},
                    collection="embeddings",
                )
            result_embeddings += pre_recorded_embs
        else:
            result_embeddings += pre_recorded_embs

    for (event_id, text_batch), embeddings in zip(
        callback_payloads, nested_embeddings
    ):
        dispatcher.event(
            EmbeddingEndEvent(
                chunks=text_batch,
                embeddings=embeddings,
            )
        )
        self.callback_manager.on_event_end(
            CBEventType.EMBEDDING,
            payload={
                EventPayload.CHUNKS: text_batch,
                EventPayload.EMBEDDINGS: embeddings,
            },
            event_id=event_id,
        )

    return result_embeddings

```
  
---|---  
###  similarity #
```
similarity(embedding1: Embedding, embedding2: Embedding, mode: SimilarityMode = DEFAULT) -> float

```

Get embedding similarity.
Source code in `llama-index-core/llama_index/core/base/embeddings/base.py`

| ```
def similarity(
    self,
    embedding1: Embedding,
    embedding2: Embedding,
    mode: SimilarityMode = SimilarityMode.DEFAULT,
) -> float:
    """Get embedding similarity."""
    return similarity(embedding1=embedding1, embedding2=embedding2, mode=mode)

```
  
---|---  
##  resolve_embed_model #
```
resolve_embed_model(embed_model: Optional[EmbedType] = None, callback_manager: Optional[CallbackManager] = None) -> BaseEmbedding

```

Resolve embed model.
Source code in `llama-index-core/llama_index/core/embeddings/utils.py`

| ```
def resolve_embed_model(
    embed_model: Optional[EmbedType] = None,
    callback_manager: Optional[CallbackManager] = None,
) -> BaseEmbedding:
    """Resolve embed model."""
    from llama_index.core.settings import Settings

    try:
        from llama_index.core.bridge.langchain import Embeddings as LCEmbeddings
    except ImportError:
        LCEmbeddings = None  # type: ignore

    if embed_model == "default":
        if os.getenv("IS_TESTING"):
            embed_model = MockEmbedding(embed_dim=8)
            embed_model.callback_manager = callback_manager or Settings.callback_manager
            return embed_model

        try:
            from llama_index.embeddings.openai import (
                OpenAIEmbedding,
            )  # pants: no-infer-dep

            from llama_index.embeddings.openai.utils import (
                validate_openai_api_key,
            )  # pants: no-infer-dep

            embed_model = OpenAIEmbedding()
            validate_openai_api_key(embed_model.api_key)  # type: ignore
        except ImportError:
            raise ImportError(
                "`llama-index-embeddings-openai` package not found, "
                "please run `pip install llama-index-embeddings-openai`"
            )
        except ValueError as e:
            raise ValueError(
                "\n******\n"
                "Could not load OpenAI embedding model. "
                "If you intended to use OpenAI, please check your OPENAI_API_KEY.\n"
                "Original error:\n"
                f"{e!s}"
                "\nConsider using embed_model='local'.\n"
                "Visit our documentation for more embedding options: "
                "https://docs.llamaindex.ai/en/stable/module_guides/models/"
                "embeddings.html#modules"
                "\n******"
            )
    # for image multi-modal embeddings
    elif isinstance(embed_model, str) and embed_model.startswith("clip"):
        try:
            from llama_index.embeddings.clip import ClipEmbedding  # pants: no-infer-dep

            clip_model_name = (
                embed_model.split(":")[1] if ":" in embed_model else "ViT-B/32"
            )
            embed_model = ClipEmbedding(model_name=clip_model_name)
        except ImportError as e:
            raise ImportError(
                "`llama-index-embeddings-clip` package not found, "
                "please run `pip install llama-index-embeddings-clip` and `pip install git+https://github.com/openai/CLIP.git`"
            )

    if isinstance(embed_model, str):
        try:
            from llama_index.embeddings.huggingface import (
                HuggingFaceEmbedding,
            )  # pants: no-infer-dep

            splits = embed_model.split(":", 1)
            is_local = splits[0]
            model_name = splits[1] if len(splits) > 1 else None
            if is_local != "local":
                raise ValueError(
                    "embed_model must start with str 'local' or of type BaseEmbedding"
                )

            cache_folder = os.path.join(get_cache_dir(), "models")
            os.makedirs(cache_folder, exist_ok=True)

            embed_model = HuggingFaceEmbedding(
                model_name=model_name, cache_folder=cache_folder
            )
        except ImportError:
            raise ImportError(
                "`llama-index-embeddings-huggingface` package not found, "
                "please run `pip install llama-index-embeddings-huggingface`"
            )

    if LCEmbeddings is not None and isinstance(embed_model, LCEmbeddings):
        try:
            from llama_index.embeddings.langchain import (
                LangchainEmbedding,
            )  # pants: no-infer-dep

            embed_model = LangchainEmbedding(embed_model)
        except ImportError as e:
            raise ImportError(
                "`llama-index-embeddings-langchain` package not found, "
                "please run `pip install llama-index-embeddings-langchain`"
            )

    if embed_model is None:
        print("Embeddings have been explicitly disabled. Using MockEmbedding.")
        embed_model = MockEmbedding(embed_dim=1)

    assert isinstance(embed_model, BaseEmbedding)

    embed_model.callback_manager = callback_manager or Settings.callback_manager

    return embed_model

```
  
---|---
