# Dynamodb
##  DynamoDBIndexStore #
Bases: `KVIndexStore`
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-dynamodb/llama_index/storage/index_store/dynamodb/base.py`

| ```
class DynamoDBIndexStore(KVIndexStore):
    def __init__(
        self,
        dynamodb_kvstore: DynamoDBKVStore,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> None:
        """Init a DynamoDBIndexStore."""
        super().__init__(
            kvstore=dynamodb_kvstore,
            namespace=namespace,
            collection_suffix=collection_suffix,
        )

    @classmethod
    def from_table_name(
        cls,
        table_name: str,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "DynamoDBIndexStore":
        """Load DynamoDBIndexStore from a DynamoDB table name."""
        ddb_kvstore = DynamoDBKVStore.from_table_name(table_name=table_name)
        return cls(
            dynamodb_kvstore=ddb_kvstore,
            namespace=namespace,
            collection_suffix=collection_suffix,
        )

```
  
---|---  
###  from_table_name `classmethod` #
```
from_table_name(table_name: str, namespace: Optional[str] = None, collection_suffix: Optional[str] = None) -> DynamoDBIndexStore

```

Load DynamoDBIndexStore from a DynamoDB table name.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-dynamodb/llama_index/storage/index_store/dynamodb/base.py`

| ```
@classmethod
def from_table_name(
    cls,
    table_name: str,
    namespace: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "DynamoDBIndexStore":
    """Load DynamoDBIndexStore from a DynamoDB table name."""
    ddb_kvstore = DynamoDBKVStore.from_table_name(table_name=table_name)
    return cls(
        dynamodb_kvstore=ddb_kvstore,
        namespace=namespace,
        collection_suffix=collection_suffix,
    )

```
  
---|---
