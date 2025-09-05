# Opensearch
##  OpensearchVectorStore #
Bases: `BasePydanticVectorStore`
Elasticsearch/Opensearch vector store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`client` |  `OpensearchVectorClient` |  Vector index client to use for data insertion/querying. |  _required_  
Examples:
`pip install llama-index-vector-stores-opensearch`
```
from llama_index.vector_stores.opensearch import (
    OpensearchVectorStore,
    OpensearchVectorClient,
)

# http endpoint for your cluster (opensearch required for vector index usage)
endpoint = "http://localhost:9200"
# index to demonstrate the VectorStore impl
idx = "gpt-index-demo"

# OpensearchVectorClient stores text in this field by default
text_field = "content"
# OpensearchVectorClient stores embeddings in this field by default
embedding_field = "embedding"

# OpensearchVectorClient encapsulates logic for a
# single opensearch index with vector search enabled
client = OpensearchVectorClient(
    endpoint, idx, 1536, embedding_field=embedding_field, text_field=text_field
)

# initialize vector store
vector_store = OpensearchVectorStore(client)

```

Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
class OpensearchVectorStore(BasePydanticVectorStore):
    """
    Elasticsearch/Opensearch vector store.

    Args:
        client (OpensearchVectorClient): Vector index client to use
            for data insertion/querying.

    Examples:
        `pip install llama-index-vector-stores-opensearch`

    ```python
        from llama_index.vector_stores.opensearch import (
            OpensearchVectorStore,
            OpensearchVectorClient,
        )

        # http endpoint for your cluster (opensearch required for vector index usage)
        endpoint = "http://localhost:9200"
        # index to demonstrate the VectorStore impl
        idx = "gpt-index-demo"

        # OpensearchVectorClient stores text in this field by default
        text_field = "content"
        # OpensearchVectorClient stores embeddings in this field by default
        embedding_field = "embedding"

        # OpensearchVectorClient encapsulates logic for a
        # single opensearch index with vector search enabled
        client = OpensearchVectorClient(
            endpoint, idx, 1536, embedding_field=embedding_field, text_field=text_field
        )

        # initialize vector store
        vector_store = OpensearchVectorStore(client)
    ```

    """

    stores_text: bool = True
    _client: OpensearchVectorClient = PrivateAttr(default=None)

    def __init__(
        self,
        client: OpensearchVectorClient,
    ) -> None:
        """Initialize params."""
        super().__init__()
        self._client = client

    @property
    def client(self) -> Any:
        """Get client."""
        return self._client

    def add(
        self,
        nodes: List[BaseNode],
        **add_kwargs: Any,
    ) -> List[str]:
        """
        Add nodes to index.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings.

        """
        self._client.index_results(nodes)
        return [result.node_id for result in nodes]

    async def async_add(
        self,
        nodes: List[BaseNode],
        **add_kwargs: Any,
    ) -> List[str]:
        """
        Async add nodes to index.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings.

        """
        await self._client.aindex_results(nodes)
        return [result.node_id for result in nodes]

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.

        Args:
            ref_doc_id (str): The doc_id of the document to delete.

        """
        self._client.delete_by_doc_id(ref_doc_id)

    async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Async delete nodes using with ref_doc_id.

        Args:
            ref_doc_id (str): The doc_id of the document to delete.

        """
        await self._client.adelete_by_doc_id(ref_doc_id)

    def delete_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
        **delete_kwargs: Any,
    ) -> None:
        """
        Deletes nodes async.

        Args:
            node_ids (Optional[List[str]], optional): IDs of nodes to delete. Defaults to None.
            filters (Optional[MetadataFilters], optional): Metadata filters. Defaults to None.

        """
        self._client.delete_nodes(node_ids, filters, **delete_kwargs)

    async def adelete_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
        **delete_kwargs: Any,
    ) -> None:
        """
        Async deletes nodes async.

        Args:
            node_ids (Optional[List[str]], optional): IDs of nodes to delete. Defaults to None.
            filters (Optional[MetadataFilters], optional): Metadata filters. Defaults to None.

        """
        await self._client.adelete_nodes(node_ids, filters, **delete_kwargs)

    def clear(self) -> None:
        """Clears index."""
        self._client.clear()

    async def aclear(self) -> None:
        """Async clears index."""
        await self._client.aclear()

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """
        Query index for top k most similar nodes.

        Args:
            query (VectorStoreQuery): Store query object.

        """
        query_embedding = cast(List[float], query.query_embedding)

        return self._client.query(
            query.mode,
            query.query_str,
            query_embedding,
            query.similarity_top_k,
            filters=query.filters,
        )

    async def aquery(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        """
        Async query index for top k most similar nodes.

        Args:
            query (VectorStoreQuery): Store query object.

        """
        query_embedding = cast(List[float], query.query_embedding)

        return await self._client.aquery(
            query.mode,
            query.query_str,
            query_embedding,
            query.similarity_top_k,
            filters=query.filters,
        )

```
  
---|---  
###  client `property` #
```
client: Any

```

Get client.
###  add #
```
add(nodes: List[BaseNode], **add_kwargs: Any) -> List[str]

```

Add nodes to index.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[BaseNode]` |  List[BaseNode]: list of nodes with embeddings. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
def add(
    self,
    nodes: List[BaseNode],
    **add_kwargs: Any,
) -> List[str]:
    """
    Add nodes to index.

    Args:
        nodes: List[BaseNode]: list of nodes with embeddings.

    """
    self._client.index_results(nodes)
    return [result.node_id for result in nodes]

```
  
---|---  
###  async_add `async` #
```
async_add(nodes: List[BaseNode], **add_kwargs: Any) -> List[str]

```

Async add nodes to index.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[BaseNode]` |  List[BaseNode]: list of nodes with embeddings. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
async def async_add(
    self,
    nodes: List[BaseNode],
    **add_kwargs: Any,
) -> List[str]:
    """
    Async add nodes to index.

    Args:
        nodes: List[BaseNode]: list of nodes with embeddings.

    """
    await self._client.aindex_results(nodes)
    return [result.node_id for result in nodes]

```
  
---|---  
###  delete #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using with ref_doc_id.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ref_doc_id` |  `str` |  The doc_id of the document to delete. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete nodes using with ref_doc_id.

    Args:
        ref_doc_id (str): The doc_id of the document to delete.

    """
    self._client.delete_by_doc_id(ref_doc_id)

```
  
---|---  
###  adelete `async` #
```
adelete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Async delete nodes using with ref_doc_id.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ref_doc_id` |  `str` |  The doc_id of the document to delete. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Async delete nodes using with ref_doc_id.

    Args:
        ref_doc_id (str): The doc_id of the document to delete.

    """
    await self._client.adelete_by_doc_id(ref_doc_id)

```
  
---|---  
###  delete_nodes #
```
delete_nodes(node_ids: Optional[List[str]] = None, filters: Optional[MetadataFilters] = None, **delete_kwargs: Any) -> None

```

Deletes nodes async.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_ids` |  `Optional[List[str]]` |  IDs of nodes to delete. Defaults to None. |  `None`  
`filters` |  `Optional[MetadataFilters]` |  Metadata filters. Defaults to None. |  `None`  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
def delete_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    filters: Optional[MetadataFilters] = None,
    **delete_kwargs: Any,
) -> None:
    """
    Deletes nodes async.

    Args:
        node_ids (Optional[List[str]], optional): IDs of nodes to delete. Defaults to None.
        filters (Optional[MetadataFilters], optional): Metadata filters. Defaults to None.

    """
    self._client.delete_nodes(node_ids, filters, **delete_kwargs)

```
  
---|---  
###  adelete_nodes `async` #
```
adelete_nodes(node_ids: Optional[List[str]] = None, filters: Optional[MetadataFilters] = None, **delete_kwargs: Any) -> None

```

Async deletes nodes async.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_ids` |  `Optional[List[str]]` |  IDs of nodes to delete. Defaults to None. |  `None`  
`filters` |  `Optional[MetadataFilters]` |  Metadata filters. Defaults to None. |  `None`  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
async def adelete_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    filters: Optional[MetadataFilters] = None,
    **delete_kwargs: Any,
) -> None:
    """
    Async deletes nodes async.

    Args:
        node_ids (Optional[List[str]], optional): IDs of nodes to delete. Defaults to None.
        filters (Optional[MetadataFilters], optional): Metadata filters. Defaults to None.

    """
    await self._client.adelete_nodes(node_ids, filters, **delete_kwargs)

```
  
---|---  
###  clear #
```
clear() -> None

```

Clears index.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
def clear(self) -> None:
    """Clears index."""
    self._client.clear()

```
  
---|---  
###  aclear `async` #
```
aclear() -> None

```

Async clears index.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
async def aclear(self) -> None:
    """Async clears index."""
    await self._client.aclear()

```
  
---|---  
###  query #
```
query(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Query index for top k most similar nodes.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `VectorStoreQuery` |  Store query object. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
    """
    Query index for top k most similar nodes.

    Args:
        query (VectorStoreQuery): Store query object.

    """
    query_embedding = cast(List[float], query.query_embedding)

    return self._client.query(
        query.mode,
        query.query_str,
        query_embedding,
        query.similarity_top_k,
        filters=query.filters,
    )

```
  
---|---  
###  aquery `async` #
```
aquery(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Async query index for top k most similar nodes.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `VectorStoreQuery` |  Store query object. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-opensearch/llama_index/vector_stores/opensearch/base.py`

| ```
async def aquery(
    self, query: VectorStoreQuery, **kwargs: Any
) -> VectorStoreQueryResult:
    """
    Async query index for top k most similar nodes.

    Args:
        query (VectorStoreQuery): Store query object.

    """
    query_embedding = cast(List[float], query.query_embedding)

    return await self._client.aquery(
        query.mode,
        query.query_str,
        query_embedding,
        query.similarity_top_k,
        filters=query.filters,
    )

```
  
---|---
