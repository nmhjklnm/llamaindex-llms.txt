# Couchbase
##  CouchbaseIndexStore #
Bases: `KVIndexStore`
Couchbase Index store.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-couchbase/llama_index/storage/index_store/couchbase/base.py`

| ```
class CouchbaseIndexStore(KVIndexStore):
    """Couchbase Index store."""

    def __init__(
        self,
        couchbase_kvstore: CouchbaseKVStore,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> None:
        """
        Initialize a CouchbaseIndexStore.

        Args:
        couchbase_kvstore (CouchbaseKVStore): Couchbase key-value store
        namespace (str): namespace for the index store
        collection_suffix (str): suffix for the collection name

        """
        super().__init__(
            couchbase_kvstore,
            namespace=namespace,
            collection_suffix=collection_suffix,
        )

    @classmethod
    def from_couchbase_client(
        cls,
        client: Any,
        bucket_name: str,
        scope_name: str,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
        async_client: Optional[Any] = None,
    ) -> "CouchbaseIndexStore":
        """Initialize a CouchbaseIndexStore from a Couchbase client."""
        couchbase_kvstore = CouchbaseKVStore.from_couchbase_client(
            client=client,
            bucket_name=bucket_name,
            scope_name=scope_name,
            async_client=async_client,
        )
        return cls(couchbase_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_couchbase_client `classmethod` #
```
from_couchbase_client(client: Any, bucket_name: str, scope_name: str, namespace: Optional[str] = None, collection_suffix: Optional[str] = None, async_client: Optional[Any] = None) -> CouchbaseIndexStore

```

Initialize a CouchbaseIndexStore from a Couchbase client.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-couchbase/llama_index/storage/index_store/couchbase/base.py`

| ```
@classmethod
def from_couchbase_client(
    cls,
    client: Any,
    bucket_name: str,
    scope_name: str,
    namespace: Optional[str] = None,
    collection_suffix: Optional[str] = None,
    async_client: Optional[Any] = None,
) -> "CouchbaseIndexStore":
    """Initialize a CouchbaseIndexStore from a Couchbase client."""
    couchbase_kvstore = CouchbaseKVStore.from_couchbase_client(
        client=client,
        bucket_name=bucket_name,
        scope_name=scope_name,
        async_client=async_client,
    )
    return cls(couchbase_kvstore, namespace, collection_suffix)

```
  
---|---
