# Redis
##  RedisKVStore #
Bases: `BaseKVStore`
Redis KV Store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`redis_uri` |  `str` |  Redis URI |  `'redis://127.0.0.1:6379'`  
`redis_client` |  `Any` |  Redis client |  `None`  
`async_redis_client` |  `Any` |  Async Redis client |  `None`  
Raises:
Type | Description  
---|---  
`ValueError` |  If redis-py is not installed  
Examples:
```
>>> from llama_index.storage.kvstore.redis import RedisKVStore
>>> # Create a RedisKVStore
>>> redis_kv_store = RedisKVStore(
>>>     redis_url="redis://127.0.0.1:6379")

```

Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
class RedisKVStore(BaseKVStore):
    """
    Redis KV Store.

    Args:
        redis_uri (str): Redis URI
        redis_client (Any): Redis client
        async_redis_client (Any): Async Redis client

    Raises:
            ValueError: If redis-py is not installed

    Examples:
        >>> from llama_index.storage.kvstore.redis import RedisKVStore
        >>> # Create a RedisKVStore
        >>> redis_kv_store = RedisKVStore(
        >>>     redis_url="redis://127.0.0.1:6379")

    """

    def __init__(
        self,
        redis_uri: Optional[str] = "redis://127.0.0.1:6379",
        redis_client: Optional[Redis] = None,
        async_redis_client: Optional[AsyncRedis] = None,
        **kwargs: Any,
    ) -> None:
        # user could inject customized redis client.
        # for instance, redis have specific TLS connection, etc.
        if redis_client is not None:
            self._redis_client = redis_client

            # create async client from sync client
            if async_redis_client is not None:
                self._async_redis_client = async_redis_client
            else:
                try:
                    self._async_redis_client = AsyncRedis.from_url(
                        self._redis_client.connection_pool.connection_kwargs["url"]
                    )
                except Exception:
                    print(
                        "Could not create async redis client from sync client, "
                        "pass in `async_redis_client` explicitly."
                    )
                    self._async_redis_client = None
        elif redis_uri is not None:
            # otherwise, try initializing redis client
            try:
                # connect to redis from url
                self._redis_client = Redis.from_url(redis_uri, **kwargs)
                self._async_redis_client = AsyncRedis.from_url(redis_uri, **kwargs)
            except ValueError as e:
                raise ValueError(f"Redis failed to connect: {e}")
        else:
            raise ValueError("Either 'redis_client' or redis_url must be provided.")

    def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        self._redis_client.hset(name=collection, key=key, value=json.dumps(val))

    async def aput(
        self, key: str, val: dict, collection: str = DEFAULT_COLLECTION
    ) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        await self._async_redis_client.hset(
            name=collection, key=key, value=json.dumps(val)
        )

    def put_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Put a dictionary of key-value pairs into the store.

        Args:
            kv_pairs (List[Tuple[str, dict]]): key-value pairs
            collection (str): collection name

        """
        with self._redis_client.pipeline() as pipe:
            cur_batch = 0
            for key, val in kv_pairs:
                pipe.hset(name=collection, key=key, value=json.dumps(val))
                cur_batch += 1

                if cur_batch >= batch_size:
                    cur_batch = 0
                    pipe.execute()

            if cur_batch > 0:
                pipe.execute()

    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        val_str = self._redis_client.hget(name=collection, key=key)
        if val_str is None:
            return None
        return json.loads(val_str)

    async def aget(
        self, key: str, collection: str = DEFAULT_COLLECTION
    ) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        val_str = await self._async_redis_client.hget(name=collection, key=key)
        if val_str is None:
            return None
        return json.loads(val_str)

    def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """Get all values from the store."""
        collection_kv_dict = {}
        for key, val_str in self._redis_client.hscan_iter(name=collection):
            value = dict(json.loads(val_str))
            collection_kv_dict[key.decode()] = value
        return collection_kv_dict

    async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """Get all values from the store."""
        collection_kv_dict = {}
        async for key, val_str in self._async_redis_client.hscan_iter(name=collection):
            value = dict(json.loads(val_str))
            collection_kv_dict[key.decode()] = value
        return collection_kv_dict

    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        deleted_num = self._redis_client.hdel(collection, key)
        return bool(deleted_num > 0)

    async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        deleted_num = await self._async_redis_client.hdel(collection, key)
        return bool(deleted_num > 0)

    @classmethod
    def from_host_and_port(
        cls,
        host: str,
        port: int,
    ) -> "RedisKVStore":
        """
        Load a RedisKVStore from a Redis host and port.

        Args:
            host (str): Redis host
            port (int): Redis port

        """
        url = f"redis://{host}:{port}".format(host=host, port=port)
        return cls(redis_uri=url)

    @classmethod
    def from_redis_client(cls, redis_client: Any) -> "RedisKVStore":
        """
        Load a RedisKVStore from a Redis Client.

        Args:
            redis_client (Redis): Redis client

        """
        return cls(redis_client=redis_client)

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    self._redis_client.hset(name=collection, key=key, value=json.dumps(val))

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
async def aput(
    self, key: str, val: dict, collection: str = DEFAULT_COLLECTION
) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    await self._async_redis_client.hset(
        name=collection, key=key, value=json.dumps(val)
    )

```
  
---|---  
###  put_all #
```
put_all(kv_pairs: List[Tuple[str, dict]], collection: str = DEFAULT_COLLECTION, batch_size: int = DEFAULT_BATCH_SIZE) -> None

```

Put a dictionary of key-value pairs into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`kv_pairs` |  `List[Tuple[str, dict]]` |  key-value pairs |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
def put_all(
    self,
    kv_pairs: List[Tuple[str, dict]],
    collection: str = DEFAULT_COLLECTION,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """
    Put a dictionary of key-value pairs into the store.

    Args:
        kv_pairs (List[Tuple[str, dict]]): key-value pairs
        collection (str): collection name

    """
    with self._redis_client.pipeline() as pipe:
        cur_batch = 0
        for key, val in kv_pairs:
            pipe.hset(name=collection, key=key, value=json.dumps(val))
            cur_batch += 1

            if cur_batch >= batch_size:
                cur_batch = 0
                pipe.execute()

        if cur_batch > 0:
            pipe.execute()

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    val_str = self._redis_client.hget(name=collection, key=key)
    if val_str is None:
        return None
    return json.loads(val_str)

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

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
    val_str = await self._async_redis_client.hget(name=collection, key=key)
    if val_str is None:
        return None
    return json.loads(val_str)

```
  
---|---  
###  get_all #
```
get_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the store.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """Get all values from the store."""
    collection_kv_dict = {}
    for key, val_str in self._redis_client.hscan_iter(name=collection):
        value = dict(json.loads(val_str))
        collection_kv_dict[key.decode()] = value
    return collection_kv_dict

```
  
---|---  
###  aget_all `async` #
```
aget_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the store.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """Get all values from the store."""
    collection_kv_dict = {}
    async for key, val_str in self._async_redis_client.hscan_iter(name=collection):
        value = dict(json.loads(val_str))
        collection_kv_dict[key.decode()] = value
    return collection_kv_dict

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    deleted_num = self._redis_client.hdel(collection, key)
    return bool(deleted_num > 0)

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    deleted_num = await self._async_redis_client.hdel(collection, key)
    return bool(deleted_num > 0)

```
  
---|---  
###  from_host_and_port `classmethod` #
```
from_host_and_port(host: str, port: int) -> RedisKVStore

```

Load a RedisKVStore from a Redis host and port.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`host` |  `str` |  Redis host |  _required_  
`port` |  `int` |  Redis port |  _required_  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
@classmethod
def from_host_and_port(
    cls,
    host: str,
    port: int,
) -> "RedisKVStore":
    """
    Load a RedisKVStore from a Redis host and port.

    Args:
        host (str): Redis host
        port (int): Redis port

    """
    url = f"redis://{host}:{port}".format(host=host, port=port)
    return cls(redis_uri=url)

```
  
---|---  
###  from_redis_client `classmethod` #
```
from_redis_client(redis_client: Any) -> RedisKVStore

```

Load a RedisKVStore from a Redis Client.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`redis_client` |  `Redis` |  Redis client |  _required_  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-redis/llama_index/storage/kvstore/redis/base.py`

| ```
@classmethod
def from_redis_client(cls, redis_client: Any) -> "RedisKVStore":
    """
    Load a RedisKVStore from a Redis Client.

    Args:
        redis_client (Redis): Redis client

    """
    return cls(redis_client=redis_client)

```
  
---|---
