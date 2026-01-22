# Google
##  GoogleIndex #
Bases: `BaseManagedIndex`
Google's Generative AI Semantic vector store with AQA.
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
class GoogleIndex(BaseManagedIndex):
    """Google's Generative AI Semantic vector store with AQA."""

    _store: GoogleVectorStore
    _index: VectorStoreIndex

    def __init__(
        self,
        vector_store: GoogleVectorStore,
        embed_model: Optional[BaseEmbedding] = None,
        # deprecated
        **kwargs: Any,
    ) -> None:
        """
        Creates an instance of GoogleIndex.

        Prefer to use the factories `from_corpus` or `create_corpus` instead.
        """
        embed_model = embed_model or MockEmbedding(embed_dim=3)

        self._store = vector_store
        self._index = VectorStoreIndex.from_vector_store(
            vector_store, embed_model=embed_model, **kwargs
        )

        super().__init__(
            index_struct=self._index.index_struct,
            **kwargs,
        )

    @classmethod
    def from_corpus(
        cls: Type[IndexType], *, corpus_id: str, **kwargs: Any
    ) -> IndexType:
        """
        Creates a GoogleIndex from an existing corpus.

        Args:
            corpus_id: ID of an existing corpus on Google's server.

        Returns:
            An instance of GoogleIndex pointing to the specified corpus.

        """
        _logger.debug(f"\n\nGoogleIndex.from_corpus(corpus_id={corpus_id})")
        return cls(
            vector_store=GoogleVectorStore.from_corpus(corpus_id=corpus_id), **kwargs
        )

    @classmethod
    def create_corpus(
        cls: Type[IndexType],
        *,
        corpus_id: Optional[str] = None,
        display_name: Optional[str] = None,
        **kwargs: Any,
    ) -> IndexType:
        """
        Creates a GoogleIndex from a new corpus.

        Args:
            corpus_id: ID of the new corpus to be created. If not provided,
                Google server will provide one.
            display_name: Title of the new corpus. If not provided, Google
                server will provide one.

        Returns:
            An instance of GoogleIndex pointing to the specified corpus.

        """
        _logger.debug(
            f"\n\nGoogleIndex.from_new_corpus(new_corpus_id={corpus_id}, new_display_name={display_name})"
        )
        return cls(
            vector_store=GoogleVectorStore.create_corpus(
                corpus_id=corpus_id, display_name=display_name
            ),
            **kwargs,
        )

    @classmethod
    def from_documents(
        cls: Type[IndexType],
        documents: Sequence[Document],
        storage_context: Optional[StorageContext] = None,
        show_progress: bool = False,
        callback_manager: Optional[CallbackManager] = None,
        transformations: Optional[List[TransformComponent]] = None,
        # deprecated
        embed_model: Optional[BaseEmbedding] = None,
        **kwargs: Any,
    ) -> IndexType:
        """Build an index from a sequence of documents."""
        _logger.debug("\n\nGoogleIndex.from_documents(...)")

        new_display_name = f"Corpus created on {datetime.datetime.now()}"
        instance = cls(
            vector_store=GoogleVectorStore.create_corpus(display_name=new_display_name),
            embed_model=embed_model,
            storage_context=storage_context,
            show_progress=show_progress,
            callback_manager=callback_manager,
            transformations=transformations,
            **kwargs,
        )

        index = cast(GoogleIndex, instance)
        index.insert_documents(
            documents=documents,
        )

        return instance

    @property
    def corpus_id(self) -> str:
        """Returns the corpus ID being used by this GoogleIndex."""
        return self._store.corpus_id

    def _insert(self, nodes: Sequence[BaseNode], **insert_kwargs: Any) -> None:
        """Inserts a set of nodes."""
        self._index.insert_nodes(nodes=nodes, **insert_kwargs)

    def insert_documents(self, documents: Sequence[Document], **kwargs: Any) -> None:
        """Inserts a set of documents."""
        for document in documents:
            self.insert(document=document, **kwargs)

    def delete_ref_doc(
        self, ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any
    ) -> None:
        """Deletes a document and its nodes by using ref_doc_id."""
        self._index.delete_ref_doc(ref_doc_id=ref_doc_id, **delete_kwargs)

    def update_ref_doc(self, document: Document, **update_kwargs: Any) -> None:
        """Updates a document and its corresponding nodes."""
        self._index.update(document=document, **update_kwargs)

    def as_retriever(self, **kwargs: Any) -> BaseRetriever:
        """Returns a Retriever for this managed index."""
        return self._index.as_retriever(**kwargs)

    def as_query_engine(
        self,
        llm: Optional[LLMType] = None,
        temperature: float = 0.7,
        answer_style: Any = 1,
        safety_setting: List[Any] = [],
        **kwargs: Any,
    ) -> BaseQueryEngine:
        """
        Returns the AQA engine for this index.

        Example:
          query_engine = index.as_query_engine(
              temperature=0.7,
              answer_style=AnswerStyle.ABSTRACTIVE,
              safety_setting=[
                  SafetySetting(
                      category=HARM_CATEGORY_SEXUALLY_EXPLICIT,
                      threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                  ),
              ]
          )

        Args:
            temperature: 0.0 to 1.0.
            answer_style: See `google.ai.generativelanguage.GenerateAnswerRequest.AnswerStyle`
            safety_setting: See `google.ai.generativelanguage.SafetySetting`.

        Returns:
            A query engine that uses Google's AQA model. The query engine will
            return a `Response` object.

            `Response`'s `source_nodes` will begin with a list of attributed
            passages. These passages are the ones that were used to construct
            the grounded response. These passages will always have no score,
            the only way to mark them as attributed passages. Then, the list
            will follow with the originally provided passages, which will have
            a score from the retrieval.

            `Response`'s `metadata` may also have have an entry with key
            `answerable_probability`, which is the probability that the grounded
            answer is likely correct.

        """
        # NOTE: lazy import
        from llama_index.core.query_engine.retriever_query_engine import (
            RetrieverQueryEngine,
        )

        # Don't overwrite the caller's kwargs, which may surprise them.
        local_kwargs = kwargs.copy()

        if "retriever" in kwargs:
            _logger.warning(
                "Ignoring user's retriever to GoogleIndex.as_query_engine, "
                "which uses its own retriever."
            )
            del local_kwargs["retriever"]

        if "response_synthesizer" in kwargs:
            _logger.warning(
                "Ignoring user's response synthesizer to "
                "GoogleIndex.as_query_engine, which uses its own retriever."
            )
            del local_kwargs["response_synthesizer"]

        local_kwargs["retriever"] = self.as_retriever(**local_kwargs)
        local_kwargs["response_synthesizer"] = GoogleTextSynthesizer.from_defaults(
            temperature=temperature,
            answer_style=answer_style,
            safety_setting=safety_setting,
        )

        return RetrieverQueryEngine.from_args(**local_kwargs)

    def _build_index_from_nodes(self, nodes: Sequence[BaseNode]) -> IndexDict:
        """Build the index from nodes."""
        return self._index._build_index_from_nodes(nodes)

```
  
---|---  
###  corpus_id `property` #
```
corpus_id: str

```

Returns the corpus ID being used by this GoogleIndex.
###  from_corpus `classmethod` #
```
from_corpus(*, corpus_id: str, **kwargs: Any) -> IndexType

```

Creates a GoogleIndex from an existing corpus.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`corpus_id` |  `str` |  ID of an existing corpus on Google's server. |  _required_  
Returns:
Type | Description  
---|---  
`IndexType` |  An instance of GoogleIndex pointing to the specified corpus.  
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
@classmethod
def from_corpus(
    cls: Type[IndexType], *, corpus_id: str, **kwargs: Any
) -> IndexType:
    """
    Creates a GoogleIndex from an existing corpus.

    Args:
        corpus_id: ID of an existing corpus on Google's server.

    Returns:
        An instance of GoogleIndex pointing to the specified corpus.

    """
    _logger.debug(f"\n\nGoogleIndex.from_corpus(corpus_id={corpus_id})")
    return cls(
        vector_store=GoogleVectorStore.from_corpus(corpus_id=corpus_id), **kwargs
    )

```
  
---|---  
###  create_corpus `classmethod` #
```
create_corpus(*, corpus_id: Optional[str] = None, display_name: Optional[str] = None, **kwargs: Any) -> IndexType

```

Creates a GoogleIndex from a new corpus.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`corpus_id` |  `Optional[str]` |  ID of the new corpus to be created. If not provided, Google server will provide one. |  `None`  
`display_name` |  `Optional[str]` |  Title of the new corpus. If not provided, Google server will provide one. |  `None`  
Returns:
Type | Description  
---|---  
`IndexType` |  An instance of GoogleIndex pointing to the specified corpus.  
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
@classmethod
def create_corpus(
    cls: Type[IndexType],
    *,
    corpus_id: Optional[str] = None,
    display_name: Optional[str] = None,
    **kwargs: Any,
) -> IndexType:
    """
    Creates a GoogleIndex from a new corpus.

    Args:
        corpus_id: ID of the new corpus to be created. If not provided,
            Google server will provide one.
        display_name: Title of the new corpus. If not provided, Google
            server will provide one.

    Returns:
        An instance of GoogleIndex pointing to the specified corpus.

    """
    _logger.debug(
        f"\n\nGoogleIndex.from_new_corpus(new_corpus_id={corpus_id}, new_display_name={display_name})"
    )
    return cls(
        vector_store=GoogleVectorStore.create_corpus(
            corpus_id=corpus_id, display_name=display_name
        ),
        **kwargs,
    )

```
  
---|---  
###  from_documents `classmethod` #
```
from_documents(documents: Sequence[Document], storage_context: Optional[StorageContext] = None, show_progress: bool = False, callback_manager: Optional[CallbackManager] = None, transformations: Optional[List[TransformComponent]] = None, embed_model: Optional[BaseEmbedding] = None, **kwargs: Any) -> IndexType

```

Build an index from a sequence of documents.
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
@classmethod
def from_documents(
    cls: Type[IndexType],
    documents: Sequence[Document],
    storage_context: Optional[StorageContext] = None,
    show_progress: bool = False,
    callback_manager: Optional[CallbackManager] = None,
    transformations: Optional[List[TransformComponent]] = None,
    # deprecated
    embed_model: Optional[BaseEmbedding] = None,
    **kwargs: Any,
) -> IndexType:
    """Build an index from a sequence of documents."""
    _logger.debug("\n\nGoogleIndex.from_documents(...)")

    new_display_name = f"Corpus created on {datetime.datetime.now()}"
    instance = cls(
        vector_store=GoogleVectorStore.create_corpus(display_name=new_display_name),
        embed_model=embed_model,
        storage_context=storage_context,
        show_progress=show_progress,
        callback_manager=callback_manager,
        transformations=transformations,
        **kwargs,
    )

    index = cast(GoogleIndex, instance)
    index.insert_documents(
        documents=documents,
    )

    return instance

```
  
---|---  
###  insert_documents #
```
insert_documents(documents: Sequence[Document], **kwargs: Any) -> None

```

Inserts a set of documents.
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
def insert_documents(self, documents: Sequence[Document], **kwargs: Any) -> None:
    """Inserts a set of documents."""
    for document in documents:
        self.insert(document=document, **kwargs)

```
  
---|---  
###  delete_ref_doc #
```
delete_ref_doc(ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any) -> None

```

Deletes a document and its nodes by using ref_doc_id.
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
def delete_ref_doc(
    self, ref_doc_id: str, delete_from_docstore: bool = False, **delete_kwargs: Any
) -> None:
    """Deletes a document and its nodes by using ref_doc_id."""
    self._index.delete_ref_doc(ref_doc_id=ref_doc_id, **delete_kwargs)

```
  
---|---  
###  update_ref_doc #
```
update_ref_doc(document: Document, **update_kwargs: Any) -> None

```

Updates a document and its corresponding nodes.
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
def update_ref_doc(self, document: Document, **update_kwargs: Any) -> None:
    """Updates a document and its corresponding nodes."""
    self._index.update(document=document, **update_kwargs)

```
  
---|---  
###  as_retriever #
```
as_retriever(**kwargs: Any) -> BaseRetriever

```

Returns a Retriever for this managed index.
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
def as_retriever(self, **kwargs: Any) -> BaseRetriever:
    """Returns a Retriever for this managed index."""
    return self._index.as_retriever(**kwargs)

```
  
---|---  
###  as_query_engine #
```
as_query_engine(llm: Optional[LLMType] = None, temperature: float = 0.7, answer_style: Any = 1, safety_setting: List[Any] = [], **kwargs: Any) -> BaseQueryEngine

```

Returns the AQA engine for this index.
Example
query_engine = index.as_query_engine( temperature=0.7, answer_style=AnswerStyle.ABSTRACTIVE, safety_setting=[ SafetySetting( category=HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE, ), ] )
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`temperature` |  `float` |  0.0 to 1.0. |  `0.7`  
`answer_style` |  `Any` |  See `google.ai.generativelanguage.GenerateAnswerRequest.AnswerStyle` |  `1`  
`safety_setting` |  `List[Any]` |  See `google.ai.generativelanguage.SafetySetting`. |  `[]`  
Returns:
Type | Description  
---|---  
`BaseQueryEngine` |  A query engine that uses Google's AQA model. The query engine will  
`BaseQueryEngine` |  return a `Response` object.  
`BaseQueryEngine` |  `Response`'s `source_nodes` will begin with a list of attributed  
`BaseQueryEngine` |  passages. These passages are the ones that were used to construct  
`BaseQueryEngine` |  the grounded response. These passages will always have no score,  
`BaseQueryEngine` |  the only way to mark them as attributed passages. Then, the list  
`BaseQueryEngine` |  will follow with the originally provided passages, which will have  
`BaseQueryEngine` |  a score from the retrieval.  
`BaseQueryEngine` |  `Response`'s `metadata` may also have have an entry with key  
`BaseQueryEngine` |  `answerable_probability`, which is the probability that the grounded  
`BaseQueryEngine` |  answer is likely correct.  
Source code in `llama-index-integrations/indices/llama-index-indices-managed-google/llama_index/indices/managed/google/base.py`

| ```
def as_query_engine(
    self,
    llm: Optional[LLMType] = None,
    temperature: float = 0.7,
    answer_style: Any = 1,
    safety_setting: List[Any] = [],
    **kwargs: Any,
) -> BaseQueryEngine:
    """
    Returns the AQA engine for this index.

    Example:
      query_engine = index.as_query_engine(
          temperature=0.7,
          answer_style=AnswerStyle.ABSTRACTIVE,
          safety_setting=[
              SafetySetting(
                  category=HARM_CATEGORY_SEXUALLY_EXPLICIT,
                  threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
              ),
          ]
      )

    Args:
        temperature: 0.0 to 1.0.
        answer_style: See `google.ai.generativelanguage.GenerateAnswerRequest.AnswerStyle`
        safety_setting: See `google.ai.generativelanguage.SafetySetting`.

    Returns:
        A query engine that uses Google's AQA model. The query engine will
        return a `Response` object.

        `Response`'s `source_nodes` will begin with a list of attributed
        passages. These passages are the ones that were used to construct
        the grounded response. These passages will always have no score,
        the only way to mark them as attributed passages. Then, the list
        will follow with the originally provided passages, which will have
        a score from the retrieval.

        `Response`'s `metadata` may also have have an entry with key
        `answerable_probability`, which is the probability that the grounded
        answer is likely correct.

    """
    # NOTE: lazy import
    from llama_index.core.query_engine.retriever_query_engine import (
        RetrieverQueryEngine,
    )

    # Don't overwrite the caller's kwargs, which may surprise them.
    local_kwargs = kwargs.copy()

    if "retriever" in kwargs:
        _logger.warning(
            "Ignoring user's retriever to GoogleIndex.as_query_engine, "
            "which uses its own retriever."
        )
        del local_kwargs["retriever"]

    if "response_synthesizer" in kwargs:
        _logger.warning(
            "Ignoring user's response synthesizer to "
            "GoogleIndex.as_query_engine, which uses its own retriever."
        )
        del local_kwargs["response_synthesizer"]

    local_kwargs["retriever"] = self.as_retriever(**local_kwargs)
    local_kwargs["response_synthesizer"] = GoogleTextSynthesizer.from_defaults(
        temperature=temperature,
        answer_style=answer_style,
        safety_setting=safety_setting,
    )

    return RetrieverQueryEngine.from_args(**local_kwargs)

```
  
---|---
