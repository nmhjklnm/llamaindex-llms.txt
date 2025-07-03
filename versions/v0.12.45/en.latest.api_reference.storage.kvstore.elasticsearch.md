# Elasticsearch
##  ElasticsearchKVStore #
Bases: `BaseKVStore`
Elasticsearch Key-Value store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`index_name` |  `str` |  Name of the Elasticsearch index. |  _required_  
`es_client` |  `Optional[Any]` |  Optional. Pre-existing AsyncElasticsearch client. |  _required_  
`es_url` |  `Optional[str]` |  Optional. Elasticsearch URL. |  `None`  
`es_cloud_id` |  `Optional[str]` |  Optional. Elasticsearch cloud ID. |  `None`  
`es_api_key` |  `Optional[str]` |  Optional. Elasticsearch API key. |  `None`  
`es_user` |  `Optional[str]` |  Optional. Elasticsearch username. |  `None`  
`es_password` |  `Optional[str]` |  Optional. Elasticsearch password. |  `None`  
Raises:
Type | Description  
---|---  
`ConnectionError` |  If AsyncElasticsearch client cannot connect to Elasticsearch.  
`ValueError` |  If neither es_client nor es_url nor es_cloud_id is provided.  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
class ElasticsearchKVStore(BaseKVStore):
    """
    Elasticsearch Key-Value store.

    Args:
        index_name: Name of the Elasticsearch index.
        es_client: Optional. Pre-existing AsyncElasticsearch client.
        es_url: Optional. Elasticsearch URL.
        es_cloud_id: Optional. Elasticsearch cloud ID.
        es_api_key: Optional. Elasticsearch API key.
        es_user: Optional. Elasticsearch username.
        es_password: Optional. Elasticsearch password.


    Raises:
        ConnectionError: If AsyncElasticsearch client cannot connect to Elasticsearch.
        ValueError: If neither es_client nor es_url nor es_cloud_id is provided.

    """

    es_client: Optional[Any]
    es_url: Optional[str]
    es_cloud_id: Optional[str]
    es_api_key: Optional[str]
    es_user: Optional[str]
    es_password: Optional[str]

    def __init__(
        self,
        index_name: str,
        es_client: Optional[Any],
        es_url: Optional[str] = None,
        es_cloud_id: Optional[str] = None,
        es_api_key: Optional[str] = None,
        es_user: Optional[str] = None,
        es_password: Optional[str] = None,
    ) -> None:
        nest_asyncio.apply()

        """Init a ElasticsearchKVStore."""
        try:
            from elasticsearch import AsyncElasticsearch
        except ImportError:
            raise ImportError(IMPORT_ERROR_MSG)

        if es_client is not None:
            self._client = es_client.options(
                headers={"user-agent": self.get_user_agent()}
            )
        elif es_url is not None or es_cloud_id is not None:
            self._client: AsyncElasticsearch = _get_elasticsearch_client(
                es_url=es_url,
                username=es_user,
                password=es_password,
                cloud_id=es_cloud_id,
                api_key=es_api_key,
            )
        else:
            raise ValueError(
                """Either provide a pre-existing AsyncElasticsearch or valid \
                credentials for creating a new connection."""
            )

    @property
    def client(self) -> Any:
        """Get async elasticsearch client."""
        return self._client

    @staticmethod
    def get_user_agent() -> str:
        """Get user agent for elasticsearch client."""
        return "llama_index-py-vs"

    async def _create_index_if_not_exists(self, index_name: str) -> None:
        """
        Create the AsyncElasticsearch index if it doesn't already exist.

        Args:
            index_name: Name of the AsyncElasticsearch index to create.

        """
        if await self.client.indices.exists(index=index_name):
            logger.debug(f"Index {index_name} already exists. Skipping creation.")

        else:
            index_settings = {"mappings": {"_source": {"enabled": True}}}

            logger.debug(
                f"Creating index {index_name} with mappings {index_settings['mappings']}"
            )
            await self.client.indices.create(index=index_name, **index_settings)

    def put(
        self,
        key: str,
        val: dict,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        self.put_all([(key, val)], collection=collection)

    async def aput(
        self,
        key: str,
        val: dict,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        await self.aput_all([(key, val)], collection=collection)

    def put_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        return asyncio.get_event_loop().run_until_complete(
            self.aput_all(kv_pairs, collection, batch_size)
        )

    async def aput_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        await self._create_index_if_not_exists(collection)

        # Prepare documents with '_id' set to the key for batch insertion
        docs = [{"_id": key, **value} for key, value in kv_pairs]

        # Insert documents in batches
        for batch in (
            docs[i : i + batch_size] for i in range(0, len(docs), batch_size)
        ):
            requests = []
            for doc in batch:
                doc_id = doc["_id"]
                doc.pop("_id")
                logger.debug(doc)
                request = {
                    "_op_type": "index",
                    "_index": collection,
                    **doc,
                    "_id": doc_id,
                }
                requests.append(request)
            await async_bulk(self.client, requests, chunk_size=batch_size, refresh=True)

    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        return asyncio.get_event_loop().run_until_complete(self.aget(key, collection))

    async def aget(
        self, key: str, collection: str = DEFAULT_COLLECTION
    ) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        await self._create_index_if_not_exists(collection)

        try:
            response = await self._client.get(index=collection, id=key, source=True)
            return response.body["_source"]
        except elasticsearch.NotFoundError:
            return None

    def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the store.

        Args:
            collection (str): collection name

        """
        return asyncio.get_event_loop().run_until_complete(self.aget_all(collection))

    async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the store.

        Args:
            collection (str): collection name

        """
        await self._create_index_if_not_exists(collection)

        result = {}
        q = {"query": {"match_all": {}}}
        async for doc in async_scan(client=self._client, index=collection, query=q):
            doc_id = doc["_id"]
            content = doc["_source"]
            result[doc_id] = content
        return result

    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        return asyncio.get_event_loop().run_until_complete(
            self.adelete(key, collection)
        )

    async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        await self._create_index_if_not_exists(collection)

        try:
            response = await self._client.delete(index=collection, id=key)
            return response.body["result"] == "deleted"
        except elasticsearch.NotFoundError:
            return False

```
  
---|---  
###  client `property` #
```
client: Any

```

Get async elasticsearch client.
###  get_user_agent `staticmethod` #
```
get_user_agent() -> str

```

Get user agent for elasticsearch client.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
@staticmethod
def get_user_agent() -> str:
    """Get user agent for elasticsearch client."""
    return "llama_index-py-vs"

```
  
---|---  
###  put #
```
put(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
def put(
    self,
    key: str,
    val: dict,
    collection: str = DEFAULT_COLLECTION,
) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    self.put_all([(key, val)], collection=collection)

```
  
---|---  
###  aput `async` #
```
aput(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
async def aput(
    self,
    key: str,
    val: dict,
    collection: str = DEFAULT_COLLECTION,
) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    await self.aput_all([(key, val)], collection=collection)

```
  
---|---  
###  get #
```
get(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    return asyncio.get_event_loop().run_until_complete(self.aget(key, collection))

```
  
---|---  
###  aget `async` #
```
aget(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
async def aget(
    self, key: str, collection: str = DEFAULT_COLLECTION
) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    await self._create_index_if_not_exists(collection)

    try:
        response = await self._client.get(index=collection, id=key, source=True)
        return response.body["_source"]
    except elasticsearch.NotFoundError:
        return None

```
  
---|---  
###  get_all #
```
get_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the store.

    Args:
        collection (str): collection name

    """
    return asyncio.get_event_loop().run_until_complete(self.aget_all(collection))

```
  
---|---  
###  aget_all `async` #
```
aget_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the store.

    Args:
        collection (str): collection name

    """
    await self._create_index_if_not_exists(collection)

    result = {}
    q = {"query": {"match_all": {}}}
    async for doc in async_scan(client=self._client, index=collection, query=q):
        doc_id = doc["_id"]
        content = doc["_source"]
        result[doc_id] = content
    return result

```
  
---|---  
###  delete #
```
delete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    return asyncio.get_event_loop().run_until_complete(
        self.adelete(key, collection)
    )

```
  
---|---  
###  adelete `async` #
```
adelete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-elasticsearch/llama_index/storage/kvstore/elasticsearch/base.py`

| ```
async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    await self._create_index_if_not_exists(collection)

    try:
        response = await self._client.delete(index=collection, id=key)
        return response.body["result"] == "deleted"
    except elasticsearch.NotFoundError:
        return False

```
  
---|---
