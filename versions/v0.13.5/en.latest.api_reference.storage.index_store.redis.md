# Redis
##  RedisIndexStore #
Bases: `KVIndexStore`
Redis Index store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`redis_kvstore` |  `RedisKVStore` |  Redis key-value store |  _required_  
`namespace` |  `str` |  namespace for the index store |  `None`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-redis/llama_index/storage/index_store/redis/base.py`

| ```
class RedisIndexStore(KVIndexStore):
    """
    Redis Index store.

    Args:
        redis_kvstore (RedisKVStore): Redis key-value store
        namespace (str): namespace for the index store

    """

    def __init__(
        self,
        redis_kvstore: RedisKVStore,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> None:
        """Init a RedisIndexStore."""
        super().__init__(
            redis_kvstore, namespace=namespace, collection_suffix=collection_suffix
        )
        # avoid conflicts with redis docstore
        if self._collection.endswith(DEFAULT_COLLECTION_SUFFIX):
            self._collection = f"{self._namespace}/index"

    @classmethod
    def from_redis_client(
        cls,
        redis_client: Any,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "RedisIndexStore":
        """Load a RedisIndexStore from a Redis Client."""
        redis_kvstore = RedisKVStore.from_redis_client(redis_client=redis_client)
        return cls(redis_kvstore, namespace, collection_suffix)

    @classmethod
    def from_host_and_port(
        cls,
        host: str,
        port: int,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "RedisIndexStore":
        """Load a RedisIndexStore from a Redis host and port."""
        redis_kvstore = RedisKVStore.from_host_and_port(host, port)
        return cls(redis_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_redis_client `classmethod` #
```
from_redis_client(redis_client: Any, namespace: Optional[str] = None, collection_suffix: Optional[str] = None) -> RedisIndexStore

```

Load a RedisIndexStore from a Redis Client.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-redis/llama_index/storage/index_store/redis/base.py`

| ```
@classmethod
def from_redis_client(
    cls,
    redis_client: Any,
    namespace: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "RedisIndexStore":
    """Load a RedisIndexStore from a Redis Client."""
    redis_kvstore = RedisKVStore.from_redis_client(redis_client=redis_client)
    return cls(redis_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_host_and_port `classmethod` #
```
from_host_and_port(host: str, port: int, namespace: Optional[str] = None, collection_suffix: Optional[str] = None) -> RedisIndexStore

```

Load a RedisIndexStore from a Redis host and port.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-redis/llama_index/storage/index_store/redis/base.py`

| ```
@classmethod
def from_host_and_port(
    cls,
    host: str,
    port: int,
    namespace: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "RedisIndexStore":
    """Load a RedisIndexStore from a Redis host and port."""
    redis_kvstore = RedisKVStore.from_host_and_port(host, port)
    return cls(redis_kvstore, namespace, collection_suffix)

```
  
---|---
