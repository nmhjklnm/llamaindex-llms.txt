# Azurecosmosnosql
##  AzureCosmosNoSqlIndexStore #
Bases: `BaseKVStore`
Creates an Azure Cosmos DB NoSql Index Store.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azurecosmosnosql/llama_index/storage/index_store/azurecosmosnosql/base.py`

| ```
class AzureCosmosNoSqlIndexStore(BaseKVStore):
    """Creates an Azure Cosmos DB NoSql Index Store."""

    def __init__(
        self,
        azure_cosmos_nosql_kvstore: AzureCosmosNoSqlKVStore,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> None:
        """Initializes the Azure Cosmos NoSql Index Store."""
        super().__init__(azure_cosmos_nosql_kvstore, namespace, collection_suffix)

    @classmethod
    def from_connection_string(
        cls,
        connection_string: str,
        index_db_name: str = DEFAULT_INDEX_DATABASE,
        index_container_name: str = DEFAULT_INDEX_CONTAINER,
        cosmos_container_properties: Dict[str, Any] = None,
        cosmos_database_properties: Dict[str, Any] = None,
    ) -> "AzureCosmosNoSqlIndexStore":
        """Creates an instance of Azure Cosmos DB NoSql KV Store using a connection string."""
        azure_cosmos_nosql_kvstore = AzureCosmosNoSqlKVStore.from_connection_string(
            connection_string,
            index_db_name,
            index_container_name,
            cosmos_container_properties,
            cosmos_database_properties,
        )
        namespace = index_db_name + "." + index_container_name
        return cls(azure_cosmos_nosql_kvstore, namespace)

    @classmethod
    def from_account_and_key(
        cls,
        endpoint: str,
        key: str,
        index_db_name: str = DEFAULT_INDEX_DATABASE,
        index_container_name: str = DEFAULT_INDEX_CONTAINER,
        cosmos_container_properties: Dict[str, Any] = None,
        cosmos_database_properties: Dict[str, Any] = None,
    ) -> "AzureCosmosNoSqlIndexStore":
        """Creates an instance of Azure Cosmos DB NoSql KV Store using an account endpoint and key."""
        azure_cosmos_nosql_kvstore = AzureCosmosNoSqlKVStore.from_account_and_key(
            endpoint,
            key,
            index_db_name,
            index_container_name,
            cosmos_container_properties,
            cosmos_database_properties,
        )
        namespace = index_db_name + "." + index_container_name
        return cls(azure_cosmos_nosql_kvstore, namespace)

    @classmethod
    def from_aad_token(
        cls,
        endpoint: str,
        index_db_name: str = DEFAULT_INDEX_DATABASE,
        index_container_name: str = DEFAULT_INDEX_CONTAINER,
        cosmos_container_properties: Dict[str, Any] = None,
        cosmos_database_properties: Dict[str, Any] = None,
    ) -> "AzureCosmosNoSqlIndexStore":
        """Creates an instance of Azure Cosmos DB NoSql KV Store using an aad token."""
        azure_cosmos_nosql_kvstore = AzureCosmosNoSqlKVStore.from_aad_token(
            endpoint,
            index_db_name,
            index_container_name,
            cosmos_container_properties,
            cosmos_database_properties,
        )
        namespace = index_db_name + "." + index_container_name
        return cls(azure_cosmos_nosql_kvstore, namespace)

```
  
---|---  
###  from_connection_string `classmethod` #
```
from_connection_string(connection_string: str, index_db_name: str = DEFAULT_INDEX_DATABASE, index_container_name: str = DEFAULT_INDEX_CONTAINER, cosmos_container_properties: Dict[str, Any] = None, cosmos_database_properties: Dict[str, Any] = None) -> AzureCosmosNoSqlIndexStore

```

Creates an instance of Azure Cosmos DB NoSql KV Store using a connection string.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azurecosmosnosql/llama_index/storage/index_store/azurecosmosnosql/base.py`

| ```
@classmethod
def from_connection_string(
    cls,
    connection_string: str,
    index_db_name: str = DEFAULT_INDEX_DATABASE,
    index_container_name: str = DEFAULT_INDEX_CONTAINER,
    cosmos_container_properties: Dict[str, Any] = None,
    cosmos_database_properties: Dict[str, Any] = None,
) -> "AzureCosmosNoSqlIndexStore":
    """Creates an instance of Azure Cosmos DB NoSql KV Store using a connection string."""
    azure_cosmos_nosql_kvstore = AzureCosmosNoSqlKVStore.from_connection_string(
        connection_string,
        index_db_name,
        index_container_name,
        cosmos_container_properties,
        cosmos_database_properties,
    )
    namespace = index_db_name + "." + index_container_name
    return cls(azure_cosmos_nosql_kvstore, namespace)

```
  
---|---  
###  from_account_and_key `classmethod` #
```
from_account_and_key(endpoint: str, key: str, index_db_name: str = DEFAULT_INDEX_DATABASE, index_container_name: str = DEFAULT_INDEX_CONTAINER, cosmos_container_properties: Dict[str, Any] = None, cosmos_database_properties: Dict[str, Any] = None) -> AzureCosmosNoSqlIndexStore

```

Creates an instance of Azure Cosmos DB NoSql KV Store using an account endpoint and key.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azurecosmosnosql/llama_index/storage/index_store/azurecosmosnosql/base.py`

| ```
@classmethod
def from_account_and_key(
    cls,
    endpoint: str,
    key: str,
    index_db_name: str = DEFAULT_INDEX_DATABASE,
    index_container_name: str = DEFAULT_INDEX_CONTAINER,
    cosmos_container_properties: Dict[str, Any] = None,
    cosmos_database_properties: Dict[str, Any] = None,
) -> "AzureCosmosNoSqlIndexStore":
    """Creates an instance of Azure Cosmos DB NoSql KV Store using an account endpoint and key."""
    azure_cosmos_nosql_kvstore = AzureCosmosNoSqlKVStore.from_account_and_key(
        endpoint,
        key,
        index_db_name,
        index_container_name,
        cosmos_container_properties,
        cosmos_database_properties,
    )
    namespace = index_db_name + "." + index_container_name
    return cls(azure_cosmos_nosql_kvstore, namespace)

```
  
---|---  
###  from_aad_token `classmethod` #
```
from_aad_token(endpoint: str, index_db_name: str = DEFAULT_INDEX_DATABASE, index_container_name: str = DEFAULT_INDEX_CONTAINER, cosmos_container_properties: Dict[str, Any] = None, cosmos_database_properties: Dict[str, Any] = None) -> AzureCosmosNoSqlIndexStore

```

Creates an instance of Azure Cosmos DB NoSql KV Store using an aad token.
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azurecosmosnosql/llama_index/storage/index_store/azurecosmosnosql/base.py`

| ```
@classmethod
def from_aad_token(
    cls,
    endpoint: str,
    index_db_name: str = DEFAULT_INDEX_DATABASE,
    index_container_name: str = DEFAULT_INDEX_CONTAINER,
    cosmos_container_properties: Dict[str, Any] = None,
    cosmos_database_properties: Dict[str, Any] = None,
) -> "AzureCosmosNoSqlIndexStore":
    """Creates an instance of Azure Cosmos DB NoSql KV Store using an aad token."""
    azure_cosmos_nosql_kvstore = AzureCosmosNoSqlKVStore.from_aad_token(
        endpoint,
        index_db_name,
        index_container_name,
        cosmos_container_properties,
        cosmos_database_properties,
    )
    namespace = index_db_name + "." + index_container_name
    return cls(azure_cosmos_nosql_kvstore, namespace)

```
  
---|---
