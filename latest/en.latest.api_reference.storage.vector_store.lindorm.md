# Lindorm
##  LindormVectorStore #
Bases: `BasePydanticVectorStore`
Lindorm vector store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`client` |  `LindormVectorClient` |  Vector index client to use. for data insertion/querying. |  _required_  
Examples:
`pip install llama-index` `pip install opensearch-py` `pip install llama-index-vector-stores-lindorm`
```
from llama_index.vector_stores.lindorm import (
    LindormVectorStore,
    LindormVectorClient,
)

# lindorm instance info
# how to obtain an lindorm search instance:
# https://alibabacloud.com/help/en/lindorm/latest/create-an-instance

# how to access your lindorm search instance:
# https://www.alibabacloud.com/help/en/lindorm/latest/view-endpoints

# run curl commands to connect to and use LindormSearch:
# https://www.alibabacloud.com/help/en/lindorm/latest/connect-and-use-the-search-engine-with-the-curl-command
host = "ld-bp******jm*******-proxy-search-pub.lindorm.aliyuncs.com"
port = 30070
username = 'your_username'
password = 'your_password'

# index to demonstrate the VectorStore impl
index_name = "lindorm_test_index"

# extension param of lindorm search, number of cluster units to query; between 1 and method.parameters.nlist.
nprobe = "a number(string type)"

# extension param of lindorm search, usually used to improve recall accuracy, but it increases performance overhead;
#   between 1 and 200; default: 10.
reorder_factor = "a number(string type)"

# LindormVectorClient encapsulates logic for a single index with vector search enabled
client = LindormVectorClient(
    host=host,
    port=port,
    username=username,
    password=password,
    index=index_name,
    dimension=1536, # match with your embedding model
    nprobe=nprobe,
    reorder_factor=reorder_factor,
    # filter_type="pre_filter/post_filter(default)"
)

# initialize vector store
vector_store = LindormVectorStore(client)

```

Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-lindorm/llama_index/vector_stores/lindorm/base.py`

| ```
class LindormVectorStore(BasePydanticVectorStore):
    """
    Lindorm vector store.

    Args:
        client (LindormVectorClient): Vector index client to use.
            for data insertion/querying.

    Examples:
        `pip install llama-index`
        `pip install opensearch-py`
        `pip install llama-index-vector-stores-lindorm`


    ```python
        from llama_index.vector_stores.lindorm import (
            LindormVectorStore,
            LindormVectorClient,
        )

        # lindorm instance info
        # how to obtain an lindorm search instance:
        # https://alibabacloud.com/help/en/lindorm/latest/create-an-instance

        # how to access your lindorm search instance:
        # https://www.alibabacloud.com/help/en/lindorm/latest/view-endpoints

        # run curl commands to connect to and use LindormSearch:
        # https://www.alibabacloud.com/help/en/lindorm/latest/connect-and-use-the-search-engine-with-the-curl-command
        host = "ld-bp******jm*******-proxy-search-pub.lindorm.aliyuncs.com"
        port = 30070
        username = 'your_username'
        password = 'your_password'

        # index to demonstrate the VectorStore impl
        index_name = "lindorm_test_index"

        # extension param of lindorm search, number of cluster units to query; between 1 and method.parameters.nlist.
        nprobe = "a number(string type)"

        # extension param of lindorm search, usually used to improve recall accuracy, but it increases performance overhead;
        #   between 1 and 200; default: 10.
        reorder_factor = "a number(string type)"

        # LindormVectorClient encapsulates logic for a single index with vector search enabled
        client = LindormVectorClient(
            host=host,
            port=port,
            username=username,
            password=password,
            index=index_name,
            dimension=1536, # match with your embedding model
            nprobe=nprobe,
            reorder_factor=reorder_factor,
            # filter_type="pre_filter/post_filter(default)"
        )

        # initialize vector store
        vector_store = LindormVectorStore(client)
    ```

    """

    stores_text: bool = True
    _client: LindormVectorClient = PrivateAttr(default=None)

    def __init__(
        self,
        client: LindormVectorClient,
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
        Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings.

        Returns:
            List[str]: List of node_ids

        """
        return asyncio.get_event_loop().run_until_complete(
            self.async_add(nodes, **add_kwargs)
        )

    async def async_add(
        self,
        nodes: List[BaseNode],
        **add_kwargs: Any,
    ) -> List[str]:
        """
        Async add nodes to index.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings.

        Returns:
            List[str]: List of node_ids

        """
        await self._client.index_results(nodes)
        return [result.node_id for result in nodes]

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using a ref_doc_id.
        Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.

        Args:
            ref_doc_id (str): The doc_id of the document whose nodes should be deleted.

        """
        asyncio.get_event_loop().run_until_complete(
            self.adelete(ref_doc_id, **delete_kwargs)
        )

    async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Async delete nodes using a ref_doc_id.

        Args:
            ref_doc_id (str): The doc_id of the document whose nodes should be deleted.

        """
        await self._client.delete_by_doc_id(ref_doc_id)

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """
        Query index for top k most similar nodes.
        Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.

        Args:
            query (VectorStoreQuery): Store query object.

        """
        return asyncio.get_event_loop().run_until_complete(self.aquery(query, **kwargs))

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

Add nodes to index. Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[BaseNode]` |  List[BaseNode]: list of nodes with embeddings. |  _required_  
Returns:
Type | Description  
---|---  
`List[str]` |  List[str]: List of node_ids  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-lindorm/llama_index/vector_stores/lindorm/base.py`

| ```
def add(
    self,
    nodes: List[BaseNode],
    **add_kwargs: Any,
) -> List[str]:
    """
    Add nodes to index.
    Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.

    Args:
        nodes: List[BaseNode]: list of nodes with embeddings.

    Returns:
        List[str]: List of node_ids

    """
    return asyncio.get_event_loop().run_until_complete(
        self.async_add(nodes, **add_kwargs)
    )

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
Returns:
Type | Description  
---|---  
`List[str]` |  List[str]: List of node_ids  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-lindorm/llama_index/vector_stores/lindorm/base.py`

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

    Returns:
        List[str]: List of node_ids

    """
    await self._client.index_results(nodes)
    return [result.node_id for result in nodes]

```
  
---|---  
###  delete #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using a ref_doc_id. Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ref_doc_id` |  `str` |  The doc_id of the document whose nodes should be deleted. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-lindorm/llama_index/vector_stores/lindorm/base.py`

| ```
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete nodes using a ref_doc_id.
    Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.

    Args:
        ref_doc_id (str): The doc_id of the document whose nodes should be deleted.

    """
    asyncio.get_event_loop().run_until_complete(
        self.adelete(ref_doc_id, **delete_kwargs)
    )

```
  
---|---  
###  adelete `async` #
```
adelete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Async delete nodes using a ref_doc_id.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ref_doc_id` |  `str` |  The doc_id of the document whose nodes should be deleted. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-lindorm/llama_index/vector_stores/lindorm/base.py`

| ```
async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Async delete nodes using a ref_doc_id.

    Args:
        ref_doc_id (str): The doc_id of the document whose nodes should be deleted.

    """
    await self._client.delete_by_doc_id(ref_doc_id)

```
  
---|---  
###  query #
```
query(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Query index for top k most similar nodes. Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `VectorStoreQuery` |  Store query object. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-lindorm/llama_index/vector_stores/lindorm/base.py`

| ```
def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
    """
    Query index for top k most similar nodes.
    Synchronous wrapper,using asynchronous logic of async_add function in synchronous way.

    Args:
        query (VectorStoreQuery): Store query object.

    """
    return asyncio.get_event_loop().run_until_complete(self.aquery(query, **kwargs))

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
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-lindorm/llama_index/vector_stores/lindorm/base.py`

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
