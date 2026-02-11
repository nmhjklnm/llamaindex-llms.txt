# Gel
##  GelIndexStore #
Bases: `KVIndexStore`
Gel Index store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`gel_kvstore` |  `GelKVStore` |  Gel key-value store |  _required_  
`namespace` |  `str` |  namespace for the index store |  `None`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-gel/llama_index/storage/index_store/gel/base.py`

| ```
class GelIndexStore(KVIndexStore):
    """
    Gel Index store.

    Args:
        gel_kvstore (GelKVStore): Gel key-value store
        namespace (str): namespace for the index store

    """

    def __init__(
        self,
        gel_kvstore: GelKVStore,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> None:
        """Init a GelIndexStore."""
        super().__init__(
            gel_kvstore, namespace=namespace, collection_suffix=collection_suffix
        )

```
  
---|---
