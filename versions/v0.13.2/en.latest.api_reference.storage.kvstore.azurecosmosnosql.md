# Azurecosmosnosql
##  AzureCosmosNoSqlKVStore #
Bases: `BaseKVStore`, `ABC`
Creates an Azure Cosmos DB NoSql Chat Store.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
class AzureCosmosNoSqlKVStore(BaseKVStore, ABC):
    """Creates an Azure Cosmos DB NoSql Chat Store."""

    _cosmos_client: CosmosClient = PrivateAttr()
    _database: DatabaseProxy = PrivateAttr()
    _container: ContainerProxy = PrivateAttr()

    def __init__(
        self,
        cosmos_client: CosmosClient,
        chat_db_name: str = DEFAULT_CHAT_DATABASE,
        chat_container_name: str = DEFAULT_CHAT_CONTAINER,
        cosmos_container_properties: Dict[str, Any] = None,
        cosmos_database_properties: Dict[str, Any] = None,
        **kwargs,
    ):
        self._cosmos_client = cosmos_client

        # Create the database if it already doesn't exist
        self._database = self._cosmos_client.create_database_if_not_exists(
            id=chat_db_name,
            offer_throughput=cosmos_database_properties.get("offer_throughput"),
            session_token=cosmos_database_properties.get("session_token"),
            initial_headers=cosmos_database_properties.get("initial_headers"),
            etag=cosmos_database_properties.get("etag"),
            match_condition=cosmos_database_properties.get("match_condition"),
        )

        # Create the collection if it already doesn't exist
        self._container = self._database.create_container_if_not_exists(
            id=chat_container_name,
            partition_key=cosmos_container_properties["partition_key"],
            indexing_policy=cosmos_container_properties.get("indexing_policy"),
            default_ttl=cosmos_container_properties.get("default_ttl"),
            offer_throughput=cosmos_container_properties.get("offer_throughput"),
            unique_key_policy=cosmos_container_properties.get("unique_key_policy"),
            conflict_resolution_policy=cosmos_container_properties.get(
                "conflict_resolution_policy"
            ),
            analytical_storage_ttl=cosmos_container_properties.get(
                "analytical_storage_ttl"
            ),
            computed_properties=cosmos_container_properties.get("computed_properties"),
            etag=cosmos_container_properties.get("etag"),
            match_condition=cosmos_container_properties.get("match_condition"),
            session_token=cosmos_container_properties.get("session_token"),
            initial_headers=cosmos_container_properties.get("initial_headers"),
        )

    @classmethod
    def from_connection_string(
        cls,
        connection_string: str,
        chat_db_name: str = DEFAULT_CHAT_DATABASE,
        chat_container_name: str = DEFAULT_CHAT_CONTAINER,
        cosmos_container_properties: Dict[str, Any] = None,
        cosmos_database_properties: Dict[str, Any] = None,
    ) -> "AzureCosmosNoSqlKVStore":
        """Creates an instance of Azure Cosmos DB NoSql KV Store using a connection string."""
        cosmos_client = CosmosClient.from_connection_string(connection_string)

        return cls(
            cosmos_client,
            chat_db_name,
            chat_container_name,
            cosmos_container_properties,
            cosmos_database_properties,
        )

    @classmethod
    def from_account_and_key(
        cls,
        endpoint: str,
        key: str,
        chat_db_name: str = DEFAULT_CHAT_DATABASE,
        chat_container_name: str = DEFAULT_CHAT_CONTAINER,
        cosmos_container_properties: Dict[str, Any] = None,
        cosmos_database_properties: Dict[str, Any] = None,
    ) -> "AzureCosmosNoSqlKVStore":
        """Initializes AzureCosmosNoSqlKVStore from an endpoint url and key."""
        cosmos_client = CosmosClient(endpoint, key)
        return cls(
            cosmos_client,
            chat_db_name,
            chat_container_name,
            cosmos_container_properties,
            cosmos_database_properties,
        )

    @classmethod
    def from_aad_token(
        cls,
        endpoint: str,
        chat_db_name: str = DEFAULT_CHAT_DATABASE,
        chat_container_name: str = DEFAULT_CHAT_CONTAINER,
        cosmos_container_properties: Dict[str, Any] = None,
        cosmos_database_properties: Dict[str, Any] = None,
    ) -> "AzureCosmosNoSqlKVStore":
        """Creates an AzureCosmosNoSqlKVStore using an Azure Active Directory token."""
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        return cls._from_clients(
            endpoint,
            credential,
            chat_db_name,
            chat_container_name,
            cosmos_container_properties,
            cosmos_database_properties,
        )

    def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        self._container.create_item(
            body={
                "id": key,
                "messages": val,
            }
        )

    async def aput(
        self, key: str, val: dict, collection: str = DEFAULT_COLLECTION
    ) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        raise NotImplementedError

    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        response = self._container.read_item(key)
        if response is not None:
            messages = response.get("messages")
        else:
            messages = {}
        return messages

    async def aget(
        self, key: str, collection: str = DEFAULT_COLLECTION
    ) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        raise NotImplementedError

    def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the store.

        Args:
            collection (str): collection name

        """
        items = self._container.read_all_items()
        output = {}
        for item in items:
            key = item.get("id")
            output[key] = item
        return output

    async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the store.

        Args:
            collection (str): collection name

        """
        raise NotImplementedError

    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        try:
            self._container.delete_item(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting item {e} with key {key}")
            return False

    async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        raise NotImplementedError

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "AzureCosmosNoSqlKVStore"

    @classmethod
    def _from_clients(
        cls,
        endpoint: str,
        credential: Any,
        chat_db_name: str = DEFAULT_CHAT_DATABASE,
        chat_container_name: str = DEFAULT_CHAT_CONTAINER,
        cosmos_container_properties: Dict[str, Any] = None,
        cosmos_database_properties: Dict[str, Any] = None,
    ) -> "AzureCosmosNoSqlKVStore":
        """Create cosmos db service clients."""
        cosmos_client = CosmosClient(url=endpoint, credential=credential)
        return cls(
            cosmos_client,
            chat_db_name,
            chat_container_name,
            cosmos_container_properties,
            cosmos_database_properties,
        )

```
  
---|---  
###  from_connection_string `classmethod` #
```
from_connection_string(connection_string: str, chat_db_name: str = DEFAULT_CHAT_DATABASE, chat_container_name: str = DEFAULT_CHAT_CONTAINER, cosmos_container_properties: Dict[str, Any] = None, cosmos_database_properties: Dict[str, Any] = None) -> AzureCosmosNoSqlKVStore

```

Creates an instance of Azure Cosmos DB NoSql KV Store using a connection string.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
@classmethod
def from_connection_string(
    cls,
    connection_string: str,
    chat_db_name: str = DEFAULT_CHAT_DATABASE,
    chat_container_name: str = DEFAULT_CHAT_CONTAINER,
    cosmos_container_properties: Dict[str, Any] = None,
    cosmos_database_properties: Dict[str, Any] = None,
) -> "AzureCosmosNoSqlKVStore":
    """Creates an instance of Azure Cosmos DB NoSql KV Store using a connection string."""
    cosmos_client = CosmosClient.from_connection_string(connection_string)

    return cls(
        cosmos_client,
        chat_db_name,
        chat_container_name,
        cosmos_container_properties,
        cosmos_database_properties,
    )

```
  
---|---  
###  from_account_and_key `classmethod` #
```
from_account_and_key(endpoint: str, key: str, chat_db_name: str = DEFAULT_CHAT_DATABASE, chat_container_name: str = DEFAULT_CHAT_CONTAINER, cosmos_container_properties: Dict[str, Any] = None, cosmos_database_properties: Dict[str, Any] = None) -> AzureCosmosNoSqlKVStore

```

Initializes AzureCosmosNoSqlKVStore from an endpoint url and key.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
@classmethod
def from_account_and_key(
    cls,
    endpoint: str,
    key: str,
    chat_db_name: str = DEFAULT_CHAT_DATABASE,
    chat_container_name: str = DEFAULT_CHAT_CONTAINER,
    cosmos_container_properties: Dict[str, Any] = None,
    cosmos_database_properties: Dict[str, Any] = None,
) -> "AzureCosmosNoSqlKVStore":
    """Initializes AzureCosmosNoSqlKVStore from an endpoint url and key."""
    cosmos_client = CosmosClient(endpoint, key)
    return cls(
        cosmos_client,
        chat_db_name,
        chat_container_name,
        cosmos_container_properties,
        cosmos_database_properties,
    )

```
  
---|---  
###  from_aad_token `classmethod` #
```
from_aad_token(endpoint: str, chat_db_name: str = DEFAULT_CHAT_DATABASE, chat_container_name: str = DEFAULT_CHAT_CONTAINER, cosmos_container_properties: Dict[str, Any] = None, cosmos_database_properties: Dict[str, Any] = None) -> AzureCosmosNoSqlKVStore

```

Creates an AzureCosmosNoSqlKVStore using an Azure Active Directory token.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
@classmethod
def from_aad_token(
    cls,
    endpoint: str,
    chat_db_name: str = DEFAULT_CHAT_DATABASE,
    chat_container_name: str = DEFAULT_CHAT_CONTAINER,
    cosmos_container_properties: Dict[str, Any] = None,
    cosmos_database_properties: Dict[str, Any] = None,
) -> "AzureCosmosNoSqlKVStore":
    """Creates an AzureCosmosNoSqlKVStore using an Azure Active Directory token."""
    from azure.identity import DefaultAzureCredential

    credential = DefaultAzureCredential()
    return cls._from_clients(
        endpoint,
        credential,
        chat_db_name,
        chat_container_name,
        cosmos_container_properties,
        cosmos_database_properties,
    )

```
  
---|---  
###  put #
```
put(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    self._container.create_item(
        body={
            "id": key,
            "messages": val,
        }
    )

```
  
---|---  
###  aput `async` #
```
aput(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
async def aput(
    self, key: str, val: dict, collection: str = DEFAULT_COLLECTION
) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    raise NotImplementedError

```
  
---|---  
###  get #
```
get(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    response = self._container.read_item(key)
    if response is not None:
        messages = response.get("messages")
    else:
        messages = {}
    return messages

```
  
---|---  
###  aget `async` #
```
aget(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
async def aget(
    self, key: str, collection: str = DEFAULT_COLLECTION
) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    raise NotImplementedError

```
  
---|---  
###  get_all #
```
get_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the store.

    Args:
        collection (str): collection name

    """
    items = self._container.read_all_items()
    output = {}
    for item in items:
        key = item.get("id")
        output[key] = item
    return output

```
  
---|---  
###  aget_all `async` #
```
aget_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the store.

    Args:
        collection (str): collection name

    """
    raise NotImplementedError

```
  
---|---  
###  adelete `async` #
```
adelete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    raise NotImplementedError

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-azurecosmosnosql/llama_index/storage/kvstore/azurecosmosnosql/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "AzureCosmosNoSqlKVStore"

```
  
---|---
