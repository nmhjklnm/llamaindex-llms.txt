# Mongodb
##  MongoDocumentStore #
Bases: `KVDocumentStore`
Mongo Document (Node) store.
A MongoDB store for Document and Node objects.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`mongo_kvstore` |  `MongoDBKVStore` |  MongoDB key-value store |  _required_  
`namespace` |  `str` |  namespace for the docstore |  `None`  
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-mongodb/llama_index/storage/docstore/mongodb/base.py`

| ```
class MongoDocumentStore(KVDocumentStore):
    """
    Mongo Document (Node) store.

    A MongoDB store for Document and Node objects.

    Args:
        mongo_kvstore (MongoDBKVStore): MongoDB key-value store
        namespace (str): namespace for the docstore

    """

    def __init__(
        self,
        mongo_kvstore: MongoDBKVStore,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Init a MongoDocumentStore."""
        super().__init__(
            mongo_kvstore,
            namespace=namespace,
            batch_size=batch_size,
            node_collection_suffix=node_collection_suffix,
            ref_doc_collection_suffix=ref_doc_collection_suffix,
            metadata_collection_suffix=metadata_collection_suffix,
        )

    @classmethod
    def from_uri(
        cls,
        uri: str,
        db_name: Optional[str] = None,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
    ) -> "MongoDocumentStore":
        """Load a MongoDocumentStore from a MongoDB URI."""
        mongo_kvstore = MongoDBKVStore.from_uri(uri, db_name)
        return cls(
            mongo_kvstore,
            namespace,
            node_collection_suffix,
            ref_doc_collection_suffix,
            metadata_collection_suffix,
        )

    @classmethod
    def from_host_and_port(
        cls,
        host: str,
        port: int,
        db_name: Optional[str] = None,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
    ) -> "MongoDocumentStore":
        """Load a MongoDocumentStore from a MongoDB host and port."""
        mongo_kvstore = MongoDBKVStore.from_host_and_port(host, port, db_name)
        return cls(
            mongo_kvstore,
            namespace,
            node_collection_suffix,
            ref_doc_collection_suffix,
            metadata_collection_suffix,
        )

```
  
---|---  
###  from_uri `classmethod` #
```
from_uri(uri: str, db_name: Optional[str] = None, namespace: Optional[str] = None, node_collection_suffix: Optional[str] = None, ref_doc_collection_suffix: Optional[str] = None, metadata_collection_suffix: Optional[str] = None) -> MongoDocumentStore

```

Load a MongoDocumentStore from a MongoDB URI.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-mongodb/llama_index/storage/docstore/mongodb/base.py`

| ```
@classmethod
def from_uri(
    cls,
    uri: str,
    db_name: Optional[str] = None,
    namespace: Optional[str] = None,
    node_collection_suffix: Optional[str] = None,
    ref_doc_collection_suffix: Optional[str] = None,
    metadata_collection_suffix: Optional[str] = None,
) -> "MongoDocumentStore":
    """Load a MongoDocumentStore from a MongoDB URI."""
    mongo_kvstore = MongoDBKVStore.from_uri(uri, db_name)
    return cls(
        mongo_kvstore,
        namespace,
        node_collection_suffix,
        ref_doc_collection_suffix,
        metadata_collection_suffix,
    )

```
  
---|---  
###  from_host_and_port `classmethod` #
```
from_host_and_port(host: str, port: int, db_name: Optional[str] = None, namespace: Optional[str] = None, node_collection_suffix: Optional[str] = None, ref_doc_collection_suffix: Optional[str] = None, metadata_collection_suffix: Optional[str] = None) -> MongoDocumentStore

```

Load a MongoDocumentStore from a MongoDB host and port.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-mongodb/llama_index/storage/docstore/mongodb/base.py`

| ```
@classmethod
def from_host_and_port(
    cls,
    host: str,
    port: int,
    db_name: Optional[str] = None,
    namespace: Optional[str] = None,
    node_collection_suffix: Optional[str] = None,
    ref_doc_collection_suffix: Optional[str] = None,
    metadata_collection_suffix: Optional[str] = None,
) -> "MongoDocumentStore":
    """Load a MongoDocumentStore from a MongoDB host and port."""
    mongo_kvstore = MongoDBKVStore.from_host_and_port(host, port, db_name)
    return cls(
        mongo_kvstore,
        namespace,
        node_collection_suffix,
        ref_doc_collection_suffix,
        metadata_collection_suffix,
    )

```
  
---|---
