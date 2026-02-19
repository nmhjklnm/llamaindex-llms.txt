# Firestore
##  FirestoreDocumentStore #
Bases: `KVDocumentStore`
Firestore Document (Node) store.
A Firestore store for Document and Node objects.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`firestore_kvstore` |  `FirestoreKVStore` |  Firestore key-value store |  _required_  
`namespace` |  `str` |  namespace for the docstore |  `None`  
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-firestore/llama_index/storage/docstore/firestore/base.py`

| ```
class FirestoreDocumentStore(KVDocumentStore):
    """
    Firestore Document (Node) store.

    A Firestore store for Document and Node objects.

    Args:
        firestore_kvstore (FirestoreKVStore): Firestore key-value store
        namespace (str): namespace for the docstore

    """

    def __init__(
        self,
        firestore_kvstore: FirestoreKVStore,
        namespace: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Init a FirestoreDocumentStore."""
        super().__init__(firestore_kvstore, namespace=namespace, batch_size=batch_size)

    @classmethod
    def from_database(
        cls,
        project: str,
        database: str,
        namespace: Optional[str] = None,
    ) -> "FirestoreDocumentStore":
        """
        Args:
            project (str): The project which the client acts on behalf of.
            database (str): The database name that the client targets.
            namespace (str): namespace for the docstore.

        """
        firestore_kvstore = FirestoreKVStore(project=project, database=database)
        return cls(firestore_kvstore, namespace)

```
  
---|---  
###  from_database `classmethod` #
```
from_database(project: str, database: str, namespace: Optional[str] = None) -> FirestoreDocumentStore

```

Parameters:
Name | Type | Description | Default  
---|---|---|---  
`project` |  `str` |  The project which the client acts on behalf of. |  _required_  
`database` |  `str` |  The database name that the client targets. |  _required_  
`namespace` |  `str` |  namespace for the docstore. |  `None`  
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-firestore/llama_index/storage/docstore/firestore/base.py`

| ```
@classmethod
def from_database(
    cls,
    project: str,
    database: str,
    namespace: Optional[str] = None,
) -> "FirestoreDocumentStore":
    """
    Args:
        project (str): The project which the client acts on behalf of.
        database (str): The database name that the client targets.
        namespace (str): namespace for the docstore.

    """
    firestore_kvstore = FirestoreKVStore(project=project, database=database)
    return cls(firestore_kvstore, namespace)

```
  
---|---
