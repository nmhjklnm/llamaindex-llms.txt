# Duckdb
##  DuckDBIndexStore #
Bases: `KVIndexStore`
DuckDB Index store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`duckdb_kvstore` |  `DuckDBKVStore` |  DuckDB key-value store |  _required_  
`namespace` |  `str` |  namespace for the index store |  `None`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-duckdb/llama_index/storage/index_store/duckdb/base.py`

| ```
class DuckDBIndexStore(KVIndexStore):
    """
    DuckDB Index store.

    Args:
        duckdb_kvstore (DuckDBKVStore): DuckDB key-value store
        namespace (str): namespace for the index store

    """

    def __init__(
        self,
        duckdb_kvstore: DuckDBKVStore,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> None:
        """Init a DuckDBIndexStore."""
        super().__init__(
            duckdb_kvstore, namespace=namespace, collection_suffix=collection_suffix
        )
        # avoid conflicts with duckdb docstore
        if self._collection.endswith(DEFAULT_COLLECTION_SUFFIX):
            self._collection = f"{self._namespace}/index"

```
  
---|---
