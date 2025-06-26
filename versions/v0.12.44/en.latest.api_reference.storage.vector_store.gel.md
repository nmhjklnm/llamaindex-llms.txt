# Gel
##  GelVectorStore #
Bases: `BasePydanticVectorStore`
Gel-backed vector store implementation.
Stores and retrieves vectors using Gel database with pgvector extension.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
class GelVectorStore(BasePydanticVectorStore):
    """
    Gel-backed vector store implementation.

    Stores and retrieves vectors using Gel database with pgvector extension.
    """

    stores_text: bool = True
    collection_name: str
    record_type: str

    _sync_client: gel.Client = PrivateAttr()
    _async_client: gel.AsyncIOClient = PrivateAttr()

    def __init__(
        self,
        collection_name: str = "default",
        record_type: str = "Record",
    ):
        """
        Initialize GelVectorStore.

        Args:
            collection_name: Name of the collection to store vectors in
            record_type: The record type name in Gel schema

        """
        super().__init__(
            collection_name=collection_name,
            record_type=record_type,
        )

        self._sync_client = None
        self._async_client = None

    def get_sync_client(self):
        """Get or initialize a synchronous Gel client."""
        if self._async_client is not None:
            raise RuntimeError(
                "GelVectorStore has already been used in async mode. "
                "If you were intentionally trying to use different IO modes at the same time, "
                "please create a new instance instead."
            )
        if self._sync_client is None:
            self._sync_client = gel.create_client()

            try:
                self._sync_client.ensure_connected()
            except gel.errors.ClientConnectionError as e:
                _logger.error(NO_PROJECT_MESSAGE)
                raise

            try:
                self._sync_client.query(f"select {self.record_type};")
            except gel.errors.InvalidReferenceError as e:
                _logger.error(
                    Template(MISSING_RECORD_TYPE_TEMPLATE).render(
                        record_type=self.record_type
                    )
                )
                raise

        return self._sync_client

    async def get_async_client(self):
        """Get or initialize an asynchronous Gel client."""
        if self._sync_client is not None:
            raise RuntimeError(
                "GelVectorStore has already been used in sync mode. "
                "If you were intentionally trying to use different IO modes at the same time, "
                "please create a new instance instead."
            )
        if self._async_client is None:
            self._async_client = gel.create_async_client()

            try:
                await self._async_client.ensure_connected()
            except gel.errors.ClientConnectionError as e:
                _logger.error(NO_PROJECT_MESSAGE)
                raise

            try:
                await self._async_client.query(f"select {self.record_type};")
            except gel.errors.InvalidReferenceError as e:
                _logger.error(
                    Template(MISSING_RECORD_TYPE_TEMPLATE).render(
                        record_type=self.record_type
                    )
                )
                raise

        return self._async_client

    @property
    def client(self) -> Any:
        """Get client."""
        return self.get_sync_client()

    def get_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
    ) -> List[BaseNode]:
        """Get nodes from vector store."""
        assert filters is None, "Filters are not supported in get_nodes"
        if node_ids is None:
            return []

        client = self.get_sync_client()

        results = client.query(
            SELECT_BY_DOC_ID_QUERY.render(record_type=self.record_type),
            external_ids=node_ids,
        )
        return [
            TextNode(
                id_=result.external_id,
                text=result.text,
                metadata=json.loads(result.metadata),
                embedding=result.embedding,
            )
            for result in results
        ]

    async def aget_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
    ) -> List[BaseNode]:
        """Async version of get_nodes."""
        assert filters is None, "Filters are not supported in get_nodes"
        if node_ids is None:
            return []

        client = await self.get_async_client()

        results = await client.query(
            SELECT_BY_DOC_ID_QUERY.render(record_type=self.record_type),
            external_ids=node_ids,
        )
        return [
            TextNode(
                id_=result.external_id,
                text=result.text,
                metadata=json.loads(result.metadata),
                embedding=result.embedding,
            )
            for result in results
        ]

    def add(
        self,
        nodes: Sequence[BaseNode],
        **kwargs: Any,
    ) -> List[str]:
        """Add nodes to vector store."""
        inserted_ids = []

        client = self.get_sync_client()

        for node in nodes:
            result = client.query(
                INSERT_QUERY.render(record_type=self.record_type),
                collection_name=self.collection_name,
                external_id=node.id_,
                text=node.get_content(),
                embedding=node.embedding,
                metadata=json.dumps(node.metadata),
            )
            inserted_ids.append(result[0].external_id)

        return inserted_ids

    async def async_add(self, nodes: Sequence[BaseNode], **kwargs: Any) -> List[str]:
        """Async version of add."""
        inserted_ids = []

        client = await self.get_async_client()

        for node in nodes:
            result = await client.query(
                INSERT_QUERY.render(record_type=self.record_type),
                collection_name=self.collection_name,
                external_id=node.id_,
                text=node.get_content(),
                embedding=node.embedding,
                metadata=json.dumps(node.metadata),
            )
            inserted_ids.append(result[0].external_id)

        return inserted_ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """Delete nodes using with ref_doc_id."""
        client = self.get_sync_client()

        result = client.query(
            DELETE_BY_IDS_QUERY.render(record_type=self.record_type),
            collection_name=self.collection_name,
            external_ids=[ref_doc_id],
        )

    async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """Async version of delete."""
        client = await self.get_async_client()

        result = await client.query(
            DELETE_BY_IDS_QUERY.render(record_type=self.record_type),
            collection_name=self.collection_name,
            external_ids=[ref_doc_id],
        )

    def clear(self) -> None:
        """Clear all nodes from configured vector store."""
        client = self.get_sync_client()

        result = client.query(
            DELETE_ALL_QUERY.render(record_type=self.record_type),
            collection_name=self.collection_name,
        )

    async def aclear(self) -> None:
        """Clear all nodes from configured vector store."""
        client = await self.get_async_client()

        result = await client.query(
            DELETE_ALL_QUERY.render(record_type=self.record_type),
            collection_name=self.collection_name,
        )

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """Query vector store."""
        assert query.query_embedding is not None, "query_embedding is required"

        filter_clause = (
            "filter " + get_filter_clause(query.filters) if query.filters else ""
        )

        assert query.mode == VectorStoreQueryMode.DEFAULT

        rendered_query = COSINE_SIMILARITY_QUERY.render(
            record_type=self.record_type, filter_clause=filter_clause
        )

        client = self.get_sync_client()

        results = client.query(
            rendered_query,
            query_embedding=query.query_embedding,
            collection_name=self.collection_name,
            limit=query.similarity_top_k,
        )

        return VectorStoreQueryResult(
            nodes=[
                TextNode(
                    id_=result.external_id,
                    text=result.text,
                    metadata=json.loads(result.metadata),
                    embedding=result.embedding,
                )
                for result in results
            ],
            similarities=[result.cosine_similarity for result in results],
            ids=[result.external_id for result in results],
        )

    async def aquery(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        """Async version of query."""
        assert query.query_embedding is not None, "query_embedding is required"

        filter_clause = (
            "filter " + get_filter_clause(query.filters) if query.filters else ""
        )

        assert query.mode == VectorStoreQueryMode.DEFAULT

        rendered_query = COSINE_SIMILARITY_QUERY.render(
            record_type=self.record_type, filter_clause=filter_clause
        )

        client = await self.get_async_client()

        results = await client.query(
            rendered_query,
            query_embedding=query.query_embedding,
            collection_name=self.collection_name,
            limit=query.similarity_top_k,
        )

        return VectorStoreQueryResult(
            nodes=[
                TextNode(
                    id_=result.external_id,
                    text=result.text,
                    metadata=json.loads(result.metadata),
                    embedding=result.embedding,
                )
                for result in results
            ],
            similarities=[result.cosine_similarity for result in results],
            ids=[result.external_id for result in results],
        )

    def persist(self, persist_path: str, fs) -> None:
        _logger.warning("GelVectorStore.persist() is a no-op")

```
  
---|---  
###  client `property` #
```
client: Any

```

Get client.
###  get_sync_client #
```
get_sync_client()

```

Get or initialize a synchronous Gel client.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
def get_sync_client(self):
    """Get or initialize a synchronous Gel client."""
    if self._async_client is not None:
        raise RuntimeError(
            "GelVectorStore has already been used in async mode. "
            "If you were intentionally trying to use different IO modes at the same time, "
            "please create a new instance instead."
        )
    if self._sync_client is None:
        self._sync_client = gel.create_client()

        try:
            self._sync_client.ensure_connected()
        except gel.errors.ClientConnectionError as e:
            _logger.error(NO_PROJECT_MESSAGE)
            raise

        try:
            self._sync_client.query(f"select {self.record_type};")
        except gel.errors.InvalidReferenceError as e:
            _logger.error(
                Template(MISSING_RECORD_TYPE_TEMPLATE).render(
                    record_type=self.record_type
                )
            )
            raise

    return self._sync_client

```
  
---|---  
###  get_async_client `async` #
```
get_async_client()

```

Get or initialize an asynchronous Gel client.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
async def get_async_client(self):
    """Get or initialize an asynchronous Gel client."""
    if self._sync_client is not None:
        raise RuntimeError(
            "GelVectorStore has already been used in sync mode. "
            "If you were intentionally trying to use different IO modes at the same time, "
            "please create a new instance instead."
        )
    if self._async_client is None:
        self._async_client = gel.create_async_client()

        try:
            await self._async_client.ensure_connected()
        except gel.errors.ClientConnectionError as e:
            _logger.error(NO_PROJECT_MESSAGE)
            raise

        try:
            await self._async_client.query(f"select {self.record_type};")
        except gel.errors.InvalidReferenceError as e:
            _logger.error(
                Template(MISSING_RECORD_TYPE_TEMPLATE).render(
                    record_type=self.record_type
                )
            )
            raise

    return self._async_client

```
  
---|---  
###  get_nodes #
```
get_nodes(node_ids: Optional[List[str]] = None, filters: Optional[MetadataFilters] = None) -> List[BaseNode]

```

Get nodes from vector store.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
def get_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    filters: Optional[MetadataFilters] = None,
) -> List[BaseNode]:
    """Get nodes from vector store."""
    assert filters is None, "Filters are not supported in get_nodes"
    if node_ids is None:
        return []

    client = self.get_sync_client()

    results = client.query(
        SELECT_BY_DOC_ID_QUERY.render(record_type=self.record_type),
        external_ids=node_ids,
    )
    return [
        TextNode(
            id_=result.external_id,
            text=result.text,
            metadata=json.loads(result.metadata),
            embedding=result.embedding,
        )
        for result in results
    ]

```
  
---|---  
###  aget_nodes `async` #
```
aget_nodes(node_ids: Optional[List[str]] = None, filters: Optional[MetadataFilters] = None) -> List[BaseNode]

```

Async version of get_nodes.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
async def aget_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    filters: Optional[MetadataFilters] = None,
) -> List[BaseNode]:
    """Async version of get_nodes."""
    assert filters is None, "Filters are not supported in get_nodes"
    if node_ids is None:
        return []

    client = await self.get_async_client()

    results = await client.query(
        SELECT_BY_DOC_ID_QUERY.render(record_type=self.record_type),
        external_ids=node_ids,
    )
    return [
        TextNode(
            id_=result.external_id,
            text=result.text,
            metadata=json.loads(result.metadata),
            embedding=result.embedding,
        )
        for result in results
    ]

```
  
---|---  
###  add #
```
add(nodes: Sequence[BaseNode], **kwargs: Any) -> List[str]

```

Add nodes to vector store.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
def add(
    self,
    nodes: Sequence[BaseNode],
    **kwargs: Any,
) -> List[str]:
    """Add nodes to vector store."""
    inserted_ids = []

    client = self.get_sync_client()

    for node in nodes:
        result = client.query(
            INSERT_QUERY.render(record_type=self.record_type),
            collection_name=self.collection_name,
            external_id=node.id_,
            text=node.get_content(),
            embedding=node.embedding,
            metadata=json.dumps(node.metadata),
        )
        inserted_ids.append(result[0].external_id)

    return inserted_ids

```
  
---|---  
###  async_add `async` #
```
async_add(nodes: Sequence[BaseNode], **kwargs: Any) -> List[str]

```

Async version of add.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
async def async_add(self, nodes: Sequence[BaseNode], **kwargs: Any) -> List[str]:
    """Async version of add."""
    inserted_ids = []

    client = await self.get_async_client()

    for node in nodes:
        result = await client.query(
            INSERT_QUERY.render(record_type=self.record_type),
            collection_name=self.collection_name,
            external_id=node.id_,
            text=node.get_content(),
            embedding=node.embedding,
            metadata=json.dumps(node.metadata),
        )
        inserted_ids.append(result[0].external_id)

    return inserted_ids

```
  
---|---  
###  delete #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using with ref_doc_id.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """Delete nodes using with ref_doc_id."""
    client = self.get_sync_client()

    result = client.query(
        DELETE_BY_IDS_QUERY.render(record_type=self.record_type),
        collection_name=self.collection_name,
        external_ids=[ref_doc_id],
    )

```
  
---|---  
###  adelete `async` #
```
adelete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Async version of delete.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """Async version of delete."""
    client = await self.get_async_client()

    result = await client.query(
        DELETE_BY_IDS_QUERY.render(record_type=self.record_type),
        collection_name=self.collection_name,
        external_ids=[ref_doc_id],
    )

```
  
---|---  
###  clear #
```
clear() -> None

```

Clear all nodes from configured vector store.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
def clear(self) -> None:
    """Clear all nodes from configured vector store."""
    client = self.get_sync_client()

    result = client.query(
        DELETE_ALL_QUERY.render(record_type=self.record_type),
        collection_name=self.collection_name,
    )

```
  
---|---  
###  aclear `async` #
```
aclear() -> None

```

Clear all nodes from configured vector store.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
async def aclear(self) -> None:
    """Clear all nodes from configured vector store."""
    client = await self.get_async_client()

    result = await client.query(
        DELETE_ALL_QUERY.render(record_type=self.record_type),
        collection_name=self.collection_name,
    )

```
  
---|---  
###  query #
```
query(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Query vector store.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
    """Query vector store."""
    assert query.query_embedding is not None, "query_embedding is required"

    filter_clause = (
        "filter " + get_filter_clause(query.filters) if query.filters else ""
    )

    assert query.mode == VectorStoreQueryMode.DEFAULT

    rendered_query = COSINE_SIMILARITY_QUERY.render(
        record_type=self.record_type, filter_clause=filter_clause
    )

    client = self.get_sync_client()

    results = client.query(
        rendered_query,
        query_embedding=query.query_embedding,
        collection_name=self.collection_name,
        limit=query.similarity_top_k,
    )

    return VectorStoreQueryResult(
        nodes=[
            TextNode(
                id_=result.external_id,
                text=result.text,
                metadata=json.loads(result.metadata),
                embedding=result.embedding,
            )
            for result in results
        ],
        similarities=[result.cosine_similarity for result in results],
        ids=[result.external_id for result in results],
    )

```
  
---|---  
###  aquery `async` #
```
aquery(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Async version of query.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-gel/llama_index/vector_stores/gel/base.py`

| ```
async def aquery(
    self, query: VectorStoreQuery, **kwargs: Any
) -> VectorStoreQueryResult:
    """Async version of query."""
    assert query.query_embedding is not None, "query_embedding is required"

    filter_clause = (
        "filter " + get_filter_clause(query.filters) if query.filters else ""
    )

    assert query.mode == VectorStoreQueryMode.DEFAULT

    rendered_query = COSINE_SIMILARITY_QUERY.render(
        record_type=self.record_type, filter_clause=filter_clause
    )

    client = await self.get_async_client()

    results = await client.query(
        rendered_query,
        query_embedding=query.query_embedding,
        collection_name=self.collection_name,
        limit=query.similarity_top_k,
    )

    return VectorStoreQueryResult(
        nodes=[
            TextNode(
                id_=result.external_id,
                text=result.text,
                metadata=json.loads(result.metadata),
                embedding=result.embedding,
            )
            for result in results
        ],
        similarities=[result.cosine_similarity for result in results],
        ids=[result.external_id for result in results],
    )

```
  
---|---
