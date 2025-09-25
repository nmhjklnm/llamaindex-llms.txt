# Azure
##  AzureIndexStore #
Bases: `KVIndexStore`
Azure Table Index store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`azure_kvstore` |  `AzureKVStore` |  Azure key-value store |  _required_  
`namespace` |  `str` |  namespace for the index store |  `None`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azure/llama_index/storage/index_store/azure/base.py`

| ```
class AzureIndexStore(KVIndexStore):
    """
    Azure Table Index store.

    Args:
        azure_kvstore (AzureKVStore): Azure key-value store
        namespace (str): namespace for the index store

    """

    def __init__(
        self,
        azure_kvstore: AzureKVStore,
        namespace: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> None:
        """Init a MongoIndexStore."""
        super().__init__(azure_kvstore, namespace, collection_suffix)

    @classmethod
    def from_connection_string(
        cls,
        connection_string: str,
        namespace: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "AzureIndexStore":
        """
        Load an AzureIndexStore from an Azure connection string.

        Args:
            connection_string (str): Azure connection string
            namespace (Optional[str]): namespace for the AzureIndexStore
            service_mode (ServiceMode): CosmosDB or Azure Table service mode

        """
        azure_kvstore = AzureKVStore.from_connection_string(
            connection_string, service_mode, partition_key
        )
        return cls(azure_kvstore, namespace, collection_suffix)

    @classmethod
    def from_account_and_key(
        cls,
        account_name: str,
        account_key: str,
        namespace: Optional[str] = None,
        endpoint: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "AzureIndexStore":
        """
        Load an AzureIndexStore from an account name and key.

        Args:
            account_name (str): Azure Storage Account Name
            account_key (str): Azure Storage Account Key
            namespace (Optional[str]): namespace for the AzureIndexStore
            service_mode (ServiceMode): CosmosDB or Azure Table service mode

        """
        azure_kvstore = AzureKVStore.from_account_and_key(
            account_name, account_key, endpoint, service_mode, partition_key
        )
        return cls(azure_kvstore, namespace, collection_suffix)

    @classmethod
    def from_account_and_id(
        cls,
        account_name: str,
        namespace: Optional[str] = None,
        endpoint: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "AzureIndexStore":
        """
        Load an AzureIndexStore from an account name and managed ID.

        Args:
            account_name (str): Azure Storage Account Name
            namespace (Optional[str]): namespace for the AzureIndexStore
            service_mode (ServiceMode): CosmosDB or Azure Table service mode

        """
        azure_kvstore = AzureKVStore.from_account_and_id(
            account_name, endpoint, service_mode, partition_key
        )
        return cls(azure_kvstore, namespace, collection_suffix)

    @classmethod
    def from_sas_token(
        cls,
        endpoint: str,
        sas_token: str,
        namespace: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "AzureIndexStore":
        """
        Load an AzureIndexStore from a SAS token.

        Args:
            endpoint (str): Azure Table service endpoint
            sas_token (str): Shared Access Signature token
            namespace (Optional[str]): namespace for the AzureIndexStore
            service_mode (ServiceMode): CosmosDB or Azure Table service mode

        """
        azure_kvstore = AzureKVStore.from_sas_token(
            endpoint, sas_token, service_mode, partition_key
        )
        return cls(azure_kvstore, namespace, collection_suffix)

    @classmethod
    def from_aad_token(
        cls,
        endpoint: str,
        namespace: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        collection_suffix: Optional[str] = None,
    ) -> "AzureIndexStore":
        """
        Load an AzureIndexStore from an AAD token.

        Args:
            endpoint (str): Azure Table service endpoint
            namespace (Optional[str]): namespace for the AzureIndexStore
            service_mode (ServiceMode): CosmosDB or Azure Table service mode

        """
        azure_kvstore = AzureKVStore.from_aad_token(
            endpoint, service_mode, partition_key
        )
        return cls(azure_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_connection_string `classmethod` #
```
from_connection_string(connection_string: str, namespace: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, collection_suffix: Optional[str] = None) -> AzureIndexStore

```

Load an AzureIndexStore from an Azure connection string.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`connection_string` |  `str` |  Azure connection string |  _required_  
`namespace` |  `Optional[str]` |  namespace for the AzureIndexStore |  `None`  
`service_mode` |  `ServiceMode` |  CosmosDB or Azure Table service mode |  `STORAGE`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azure/llama_index/storage/index_store/azure/base.py`

| ```
@classmethod
def from_connection_string(
    cls,
    connection_string: str,
    namespace: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "AzureIndexStore":
    """
    Load an AzureIndexStore from an Azure connection string.

    Args:
        connection_string (str): Azure connection string
        namespace (Optional[str]): namespace for the AzureIndexStore
        service_mode (ServiceMode): CosmosDB or Azure Table service mode

    """
    azure_kvstore = AzureKVStore.from_connection_string(
        connection_string, service_mode, partition_key
    )
    return cls(azure_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_account_and_key `classmethod` #
```
from_account_and_key(account_name: str, account_key: str, namespace: Optional[str] = None, endpoint: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, collection_suffix: Optional[str] = None) -> AzureIndexStore

```

Load an AzureIndexStore from an account name and key.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`account_name` |  `str` |  Azure Storage Account Name |  _required_  
`account_key` |  `str` |  Azure Storage Account Key |  _required_  
`namespace` |  `Optional[str]` |  namespace for the AzureIndexStore |  `None`  
`service_mode` |  `ServiceMode` |  CosmosDB or Azure Table service mode |  `STORAGE`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azure/llama_index/storage/index_store/azure/base.py`

| ```
@classmethod
def from_account_and_key(
    cls,
    account_name: str,
    account_key: str,
    namespace: Optional[str] = None,
    endpoint: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "AzureIndexStore":
    """
    Load an AzureIndexStore from an account name and key.

    Args:
        account_name (str): Azure Storage Account Name
        account_key (str): Azure Storage Account Key
        namespace (Optional[str]): namespace for the AzureIndexStore
        service_mode (ServiceMode): CosmosDB or Azure Table service mode

    """
    azure_kvstore = AzureKVStore.from_account_and_key(
        account_name, account_key, endpoint, service_mode, partition_key
    )
    return cls(azure_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_account_and_id `classmethod` #
```
from_account_and_id(account_name: str, namespace: Optional[str] = None, endpoint: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, collection_suffix: Optional[str] = None) -> AzureIndexStore

```

Load an AzureIndexStore from an account name and managed ID.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`account_name` |  `str` |  Azure Storage Account Name |  _required_  
`namespace` |  `Optional[str]` |  namespace for the AzureIndexStore |  `None`  
`service_mode` |  `ServiceMode` |  CosmosDB or Azure Table service mode |  `STORAGE`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azure/llama_index/storage/index_store/azure/base.py`

| ```
@classmethod
def from_account_and_id(
    cls,
    account_name: str,
    namespace: Optional[str] = None,
    endpoint: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "AzureIndexStore":
    """
    Load an AzureIndexStore from an account name and managed ID.

    Args:
        account_name (str): Azure Storage Account Name
        namespace (Optional[str]): namespace for the AzureIndexStore
        service_mode (ServiceMode): CosmosDB or Azure Table service mode

    """
    azure_kvstore = AzureKVStore.from_account_and_id(
        account_name, endpoint, service_mode, partition_key
    )
    return cls(azure_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_sas_token `classmethod` #
```
from_sas_token(endpoint: str, sas_token: str, namespace: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, collection_suffix: Optional[str] = None) -> AzureIndexStore

```

Load an AzureIndexStore from a SAS token.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`endpoint` |  `str` |  Azure Table service endpoint |  _required_  
`sas_token` |  `str` |  Shared Access Signature token |  _required_  
`namespace` |  `Optional[str]` |  namespace for the AzureIndexStore |  `None`  
`service_mode` |  `ServiceMode` |  CosmosDB or Azure Table service mode |  `STORAGE`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azure/llama_index/storage/index_store/azure/base.py`

| ```
@classmethod
def from_sas_token(
    cls,
    endpoint: str,
    sas_token: str,
    namespace: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "AzureIndexStore":
    """
    Load an AzureIndexStore from a SAS token.

    Args:
        endpoint (str): Azure Table service endpoint
        sas_token (str): Shared Access Signature token
        namespace (Optional[str]): namespace for the AzureIndexStore
        service_mode (ServiceMode): CosmosDB or Azure Table service mode

    """
    azure_kvstore = AzureKVStore.from_sas_token(
        endpoint, sas_token, service_mode, partition_key
    )
    return cls(azure_kvstore, namespace, collection_suffix)

```
  
---|---  
###  from_aad_token `classmethod` #
```
from_aad_token(endpoint: str, namespace: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, collection_suffix: Optional[str] = None) -> AzureIndexStore

```

Load an AzureIndexStore from an AAD token.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`endpoint` |  `str` |  Azure Table service endpoint |  _required_  
`namespace` |  `Optional[str]` |  namespace for the AzureIndexStore |  `None`  
`service_mode` |  `ServiceMode` |  CosmosDB or Azure Table service mode |  `STORAGE`  
Source code in `llama-index-integrations/storage/index_store/llama-index-storage-index-store-azure/llama_index/storage/index_store/azure/base.py`

| ```
@classmethod
def from_aad_token(
    cls,
    endpoint: str,
    namespace: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    collection_suffix: Optional[str] = None,
) -> "AzureIndexStore":
    """
    Load an AzureIndexStore from an AAD token.

    Args:
        endpoint (str): Azure Table service endpoint
        namespace (Optional[str]): namespace for the AzureIndexStore
        service_mode (ServiceMode): CosmosDB or Azure Table service mode

    """
    azure_kvstore = AzureKVStore.from_aad_token(
        endpoint, service_mode, partition_key
    )
    return cls(azure_kvstore, namespace, collection_suffix)

```
  
---|---
