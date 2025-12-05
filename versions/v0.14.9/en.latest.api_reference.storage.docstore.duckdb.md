# Duckdb
##  DuckDBDocumentStore #
Bases: `KVDocumentStore`
DuckDB Document (Node) store.
A DuckDB store for Document and Node objects.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`duckdb_kvstore` |  `DuckDBKVStore` |  DuckDB key-value store |  _required_  
`namespace` |  `str` |  namespace for the docstore |  `None`  
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-duckdb/llama_index/storage/docstore/duckdb/base.py`

| ```
class DuckDBDocumentStore(KVDocumentStore):
    """
    DuckDB Document (Node) store.

    A DuckDB store for Document and Node objects.

    Args:
        duckdb_kvstore (DuckDBKVStore): DuckDB key-value store
        namespace (str): namespace for the docstore

    """

    def __init__(
        self,
        duckdb_kvstore: DuckDBKVStore,
        namespace: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Init a DuckDBDocumentStore."""
        super().__init__(duckdb_kvstore, namespace=namespace, batch_size=batch_size)
        # avoid conflicts with duckdb index store
        self._node_collection = f"{self._namespace}/doc"

```
  
---|---
