# Firestore
##  FirestoreIndexStore #
Bases: `KVIndexStore`
Firestore Index store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`firestore_kvstore` |  `FirestoreKVStore` |  Firestore key-value store |  _required_  
`namespace` |  `str` |  namespace for the index store |  `None`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-firestore/llama_index/storage/index_store/firestore/base.py`

| ```
class FirestoreIndexStore(KVIndexStore):
    """
    Firestore Index store.

    Args:
        firestore_kvstore (FirestoreKVStore): Firestore key-value store
        namespace (str): namespace for the index store

    """

    def __init__(
        self,
        firestore_kvstore: FirestoreKVStore,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> None:
        """Init a FirestoreIndexStore."""
        super().__init__(
            firestore_kvstore, namespace=namespace, collection_suffix=collection_suffix
        )

    @classmethod
    def from_database(
        cls,
        project: str,
        database: str,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "FirestoreIndexStore":
        """
        Load a FirestoreIndexStore from a Firestore database.

        Args:
            project (str): The project which the client acts on behalf of.
            database (str): The database name that the client targets.
            namespace (str): namespace for the docstore.
            collection_suffix (str): suffix for the collection name

        """
        firestore_kvstore = FirestoreKVStore(project=project, database=database)
        return cls(firestore_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_database `classmethod` #
```
from_database(project: str, database: str, namespace: Optional[str] = None, collection_suffix: Optional[str] = None) -> FirestoreIndexStore

```

Load a FirestoreIndexStore from a Firestore database.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`project` |  `str` |  The project which the client acts on behalf of. |  _required_  
`database` |  `str` |  The database name that the client targets. |  _required_  
`namespace` |  `str` |  namespace for the docstore. |  `None`  
`collection_suffix` |  `str` |  suffix for the collection name |  `None`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-firestore/llama_index/storage/index_store/firestore/base.py`

| ```
@classmethod
def from_database(
    cls,
    project: str,
    database: str,
    namespace: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "FirestoreIndexStore":
    """
    Load a FirestoreIndexStore from a Firestore database.

    Args:
        project (str): The project which the client acts on behalf of.
        database (str): The database name that the client targets.
        namespace (str): namespace for the docstore.
        collection_suffix (str): suffix for the collection name

    """
    firestore_kvstore = FirestoreKVStore(project=project, database=database)
    return cls(firestore_kvstore, namespace, collection_suffix)

```
  
---|---
