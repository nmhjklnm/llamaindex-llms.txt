# Redis
##  RedisDocumentStore #
Bases: `KVDocumentStore`
Redis Document (Node) store.
A Redis store for Document and Node objects.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`redis_kvstore` |  `RedisKVStore` |  Redis key-value store |  _required_  
`namespace` |  `str` |  namespace for the docstore |  `None`  
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-redis/llama_index/storage/docstore/redis/base.py`

| ```
class RedisDocumentStore(KVDocumentStore):
    """
    Redis Document (Node) store.

    A Redis store for Document and Node objects.

    Args:
        redis_kvstore (RedisKVStore): Redis key-value store
        namespace (str): namespace for the docstore

    """

    def __init__(
        self,
        redis_kvstore: RedisKVStore,
        namespace: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Init a RedisDocumentStore."""
        super().__init__(redis_kvstore, namespace=namespace, batch_size=batch_size)
        # avoid conflicts with redis index store
        self._node_collection = f"{self._namespace}/doc"

    @classmethod
    def from_redis_client(
        cls,
        redis_client: Any,
        namespace: Optional[str] = None,
    ) -> "RedisDocumentStore":
        """Load a RedisDocumentStore from a Redis Client."""
        redis_kvstore = RedisKVStore.from_redis_client(redis_client=redis_client)
        return cls(redis_kvstore, namespace)

    @classmethod
    def from_host_and_port(
        cls,
        host: str,
        port: int,
        namespace: Optional[str] = None,
    ) -> "RedisDocumentStore":
        """Load a RedisDocumentStore from a Redis host and port."""
        redis_kvstore = RedisKVStore.from_host_and_port(host, port)
        return cls(redis_kvstore, namespace)

```
  
---|---  
###  from_redis_client `classmethod` #
```
from_redis_client(redis_client: Any, namespace: Optional[str] = None) -> RedisDocumentStore

```

Load a RedisDocumentStore from a Redis Client.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-redis/llama_index/storage/docstore/redis/base.py`

| ```
@classmethod
def from_redis_client(
    cls,
    redis_client: Any,
    namespace: Optional[str] = None,
) -> "RedisDocumentStore":
    """Load a RedisDocumentStore from a Redis Client."""
    redis_kvstore = RedisKVStore.from_redis_client(redis_client=redis_client)
    return cls(redis_kvstore, namespace)

```
  
---|---  
###  from_host_and_port `classmethod` #
```
from_host_and_port(host: str, port: int, namespace: Optional[str] = None) -> RedisDocumentStore

```

Load a RedisDocumentStore from a Redis host and port.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-redis/llama_index/storage/docstore/redis/base.py`

| ```
@classmethod
def from_host_and_port(
    cls,
    host: str,
    port: int,
    namespace: Optional[str] = None,
) -> "RedisDocumentStore":
    """Load a RedisDocumentStore from a Redis host and port."""
    redis_kvstore = RedisKVStore.from_host_and_port(host, port)
    return cls(redis_kvstore, namespace)

```
  
---|---
