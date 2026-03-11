# Tablestore
##  TablestoreIndexStore #
Bases: `KVIndexStore`
Tablestore Index store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`tablestore_kvstore` |  `TablestoreKVStore` |  Tablestore key-value store |  _required_  
`namespace` |  `str` |  namespace for the index store |  `'llama_index_index_store_'`  
`collection_suffix` |  `str` |  suffix for the table name |  `'data'`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-tablestore/llama_index/storage/index_store/tablestore/base.py`

| ```
class TablestoreIndexStore(KVIndexStore):
    """
    Tablestore Index store.

    Args:
        tablestore_kvstore (TablestoreKVStore): Tablestore key-value store
        namespace (str): namespace for the index store
        collection_suffix (str): suffix for the table name

    """

    def __init__(
        self,
        tablestore_kvstore: TablestoreKVStore,
        namespace: str = "llama_index_index_store_",
        collection_suffix: str = "data",
    ) -> None:
        """Init a TablestoreIndexStore."""
        super().__init__(
            kvstore=tablestore_kvstore,
            namespace=namespace,
            collection_suffix=collection_suffix,
        )
        self._tablestore_kvstore = tablestore_kvstore

    @classmethod
    def from_config(
        cls,
        endpoint: Optional[str] = None,
        instance_name: Optional[str] = None,
        access_key_id: Optional[str] = None,
        access_key_secret: Optional[str] = None,
        **kwargs: Any,
    ) -> "TablestoreIndexStore":
        """Load a TablestoreIndexStore from config."""
        kv_store = TablestoreKVStore(
            endpoint=endpoint,
            instance_name=instance_name,
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            kwargs=kwargs,
        )
        return cls(tablestore_kvstore=kv_store)

    def delete_all_index(self):
        """Delete all index."""
        self._tablestore_kvstore.delete_all(self._collection)

```
  
---|---  
###  from_config `classmethod` #
```
from_config(endpoint: Optional[str] = None, instance_name: Optional[str] = None, access_key_id: Optional[str] = None, access_key_secret: Optional[str] = None, **kwargs: Any) -> TablestoreIndexStore

```

Load a TablestoreIndexStore from config.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-tablestore/llama_index/storage/index_store/tablestore/base.py`

| ```
@classmethod
def from_config(
    cls,
    endpoint: Optional[str] = None,
    instance_name: Optional[str] = None,
    access_key_id: Optional[str] = None,
    access_key_secret: Optional[str] = None,
    **kwargs: Any,
) -> "TablestoreIndexStore":
    """Load a TablestoreIndexStore from config."""
    kv_store = TablestoreKVStore(
        endpoint=endpoint,
        instance_name=instance_name,
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        kwargs=kwargs,
    )
    return cls(tablestore_kvstore=kv_store)

```
  
---|---  
###  delete_all_index #
```
delete_all_index()

```

Delete all index.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-tablestore/llama_index/storage/index_store/tablestore/base.py`

| ```
def delete_all_index(self):
    """Delete all index."""
    self._tablestore_kvstore.delete_all(self._collection)

```
  
---|---
