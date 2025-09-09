# Azure
##  AzureChatStore #
Bases: `BaseChatStore`
Azure chat store leveraging Azure Table Storage or Cosmos DB.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
class AzureChatStore(BaseChatStore):
    """Azure chat store leveraging Azure Table Storage or Cosmos DB."""

    _table_service_client: TableServiceClient = PrivateAttr()
    _atable_service_client: AsyncTableServiceClient = PrivateAttr()

    chat_table_name: str = Field(default=DEFAULT_CHAT_TABLE)
    metadata_table_name: str = Field(default=DEFAULT_METADATA_TABLE)
    metadata_partition_key: str = Field(default=None)
    service_mode: ServiceMode = Field(default=ServiceMode.STORAGE)

    def __init__(
        self,
        table_service_client: TableServiceClient,
        atable_service_client: Optional[AsyncTableServiceClient] = None,
        chat_table_name: str = DEFAULT_CHAT_TABLE,
        metadata_table_name: str = DEFAULT_METADATA_TABLE,
        metadata_partition_key: str = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
    ):
        sanitized_chat_table_name = sanitize_table_name(chat_table_name)

        super().__init__(
            chat_table_name=sanitized_chat_table_name,
            metadata_table_name=sanitize_table_name(metadata_table_name),
            metadata_partition_key=(
                sanitized_chat_table_name
                if metadata_partition_key is None
                else metadata_partition_key
            ),
            service_mode=service_mode,
        )

        self._table_service_client = table_service_client
        self._atable_service_client = atable_service_client

    @classmethod
    def from_connection_string(
        cls,
        connection_string: str,
        chat_table_name: str = DEFAULT_CHAT_TABLE,
        metadata_table_name: str = DEFAULT_METADATA_TABLE,
        metadata_partition_key: str = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
    ):
        """Creates an instance of AzureChatStore using a connection string."""
        table_service_client = TableServiceClient.from_connection_string(
            connection_string
        )
        atable_service_client = AsyncTableServiceClient.from_connection_string(
            connection_string
        )

        return cls(
            table_service_client,
            atable_service_client,
            chat_table_name,
            metadata_table_name,
            metadata_partition_key,
            service_mode,
        )

    @classmethod
    def from_account_and_key(
        cls,
        account_name: str,
        account_key: str,
        endpoint: Optional[str] = None,
        chat_table_name: str = DEFAULT_CHAT_TABLE,
        metadata_table_name: str = DEFAULT_METADATA_TABLE,
        metadata_partition_key: str = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
    ) -> "AzureChatStore":
        """Initializes AzureChatStore from an account name and key."""
        if endpoint is None:
            endpoint = f"https://{account_name}.table.core.windows.net"
        credential = AzureNamedKeyCredential(account_name, account_key)
        return cls._from_clients(
            endpoint,
            credential,
            chat_table_name,
            metadata_table_name,
            metadata_partition_key,
            service_mode,
        )

    @classmethod
    def from_account_and_id(
        cls,
        account_name: str,
        endpoint: Optional[str] = None,
        chat_table_name: str = DEFAULT_CHAT_TABLE,
        metadata_table_name: str = DEFAULT_METADATA_TABLE,
        metadata_partition_key: str = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
    ) -> "AzureChatStore":
        """Initializes AzureChatStore from an account name and managed ID."""
        from azure.identity import DefaultAzureCredential

        if endpoint is None:
            endpoint = f"https://{account_name}.table.core.windows.net"
        credential = DefaultAzureCredential()
        return cls._from_clients(
            endpoint,
            credential,
            chat_table_name,
            metadata_table_name,
            metadata_partition_key,
            service_mode,
        )

    @classmethod
    def from_sas_token(
        cls,
        endpoint: str,
        sas_token: str,
        chat_table_name: str = DEFAULT_CHAT_TABLE,
        metadata_table_name: str = DEFAULT_METADATA_TABLE,
        metadata_partition_key: str = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
    ) -> "AzureChatStore":
        """Creates an AzureChatStore instance using a SAS token."""
        credential = AzureSasCredential(sas_token)
        return cls._from_clients(
            endpoint,
            credential,
            chat_table_name,
            metadata_table_name,
            metadata_partition_key,
            service_mode,
        )

    @classmethod
    def from_aad_token(
        cls,
        endpoint: str,
        chat_table_name: str = DEFAULT_CHAT_TABLE,
        metadata_table_name: str = DEFAULT_METADATA_TABLE,
        metadata_partition_key: str = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
    ) -> "AzureChatStore":
        """Creates an AzureChatStore using an Azure Active Directory token."""
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        return cls._from_clients(
            endpoint,
            credential,
            chat_table_name,
            metadata_table_name,
            metadata_partition_key,
            service_mode,
        )

    def set_messages(self, key: str, messages: List[ChatMessage]) -> None:
        """Set messages for a key."""
        asyncio_run(self.aset_messages(key, messages))

    async def aset_messages(self, key: str, messages: List[ChatMessage]) -> None:
        """Asynchronoulsy set messages for a key."""
        # Delete existing messages and insert new messages in one transaction
        chat_client = await self._atable_service_client.create_table_if_not_exists(
            self.chat_table_name
        )
        entities = chat_client.query_entities(f"PartitionKey eq '{key}'")
        all_entities = []
        async for entity in entities:
            all_entities.append(entity)

        delete_operations = (
            (TransactionOperation.DELETE, entity) for entity in all_entities
        )
        create_operations = (
            (
                TransactionOperation.CREATE,
                serialize(
                    self.service_mode,
                    {
                        "PartitionKey": key,
                        "RowKey": self._to_row_key(idx),
                        **message.dict(),
                    },
                ),
            )
            for idx, message in enumerate(messages)
        )
        await chat_client.submit_transaction(
            chain(delete_operations, create_operations)
        )

        # Update metadata
        metadata_client = await self._atable_service_client.create_table_if_not_exists(
            self.metadata_table_name
        )
        messages_len = len(messages)
        await metadata_client.upsert_entity(
            {
                "PartitionKey": self.metadata_partition_key,
                "RowKey": key,
                "LastMessageRowKey": self._to_row_key(messages_len - 1),
                "MessageCount": messages_len,
            },
            UpdateMode.REPLACE,
        )

    def get_messages(self, key: str) -> List[ChatMessage]:
        """Get messages for a key."""
        return asyncio_run(self.aget_messages(key))

    async def aget_messages(self, key: str) -> List[ChatMessage]:
        """Asynchronously get messages for a key."""
        chat_client = await self._atable_service_client.create_table_if_not_exists(
            self.chat_table_name
        )
        entities = chat_client.query_entities(f"PartitionKey eq '{key}'")
        messages = []

        async for entity in entities:
            messages.append(
                ChatMessage.model_validate(deserialize(self.service_mode, entity))
            )

        return messages

    def add_message(self, key: str, message: ChatMessage, idx: int = None):
        """Add a message for a key."""
        asyncio_run(self.async_add_message(key, message, idx))

    async def async_add_message(self, key: str, message: ChatMessage, idx: int = None):
        metadata_client = await self._atable_service_client.create_table_if_not_exists(
            self.metadata_table_name
        )
        metadata = await self._get_or_default_metadata(metadata_client, key)
        next_index = int(metadata["MessageCount"])

        if idx is not None and idx > next_index:
            raise ValueError(f"Index out of bounds: {idx}")
        elif idx is None:
            idx = next_index

        # Insert the new message
        chat_client = await self._atable_service_client.create_table_if_not_exists(
            self.chat_table_name
        )
        await chat_client.create_entity(
            serialize(
                self.service_mode,
                {
                    "PartitionKey": key,
                    "RowKey": self._to_row_key(idx),
                    **message.dict(),
                },
            )
        )

        metadata["LastMessageRowKey"] = self._to_row_key(idx)
        metadata["MessageCount"] = next_index + 1
        # Update medatada
        await metadata_client.upsert_entity(metadata, UpdateMode.MERGE)

    def delete_messages(self, key: str) -> Optional[List[ChatMessage]]:
        # Delete all messages for the key
        return asyncio_run(self.adelete_messages(key))

    async def adelete_messages(self, key: str) -> Optional[List[ChatMessage]]:
        """Asynchronously delete all messages for a key."""
        chat_client = await self._atable_service_client.create_table_if_not_exists(
            self.chat_table_name
        )
        entities = chat_client.query_entities(f"PartitionKey eq '{key}'")
        all_entities = []
        async for entity in entities:
            all_entities.append(entity)

        await chat_client.submit_transaction(
            (TransactionOperation.DELETE, entity) for entity in all_entities
        )

        metadata_client = await self._atable_service_client.create_table_if_not_exists(
            self.metadata_table_name
        )
        await metadata_client.upsert_entity(
            self._get_default_metadata(key), UpdateMode.REPLACE
        )

    def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """Delete specific message for a key."""
        return asyncio_run(self.adelete_message(key, idx))

    async def adelete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """Asynchronously delete specific message for a key."""
        # Fetch metadata to get the message count
        metadata_client = await self._atable_service_client.create_table_if_not_exists(
            self.metadata_table_name
        )
        metadata = await metadata_client.get_entity(
            partition_key=self.metadata_partition_key, row_key=key
        )

        # Index out of bounds
        message_count = int(metadata["MessageCount"])
        if idx >= message_count:
            return None

        # Delete the message
        chat_client = await self._atable_service_client.create_table_if_not_exists(
            self.chat_table_name
        )
        await chat_client.delete_entity(
            partition_key=key, row_key=self._to_row_key(idx)
        )

        # Update metadata if last message was deleted
        if idx == message_count - 1:
            metadata["LastMessageRowKey"] = self._to_row_key(idx - 1)
            metadata["MessageCount"] = message_count - 1
            await metadata_client.upsert_entity(metadata, mode=UpdateMode.MERGE)

    def delete_last_message(self, key: str) -> Optional[ChatMessage]:
        """Delete last message for a key."""
        return asyncio_run(self.adelete_last_message(key))

    async def adelete_last_message(self, key: str) -> Optional[ChatMessage]:
        """Async delete last message for a key."""
        metadata_client = await self._atable_service_client.create_table_if_not_exists(
            self.metadata_table_name
        )
        # Retrieve metadata to get the last message row key
        metadata = await metadata_client.get_entity(
            partition_key=self.metadata_partition_key, row_key=key
        )
        last_row_key = metadata["LastMessageRowKey"]

        chat_client = await self._atable_service_client.create_table_if_not_exists(
            self.chat_table_name
        )
        # Delete the last message
        await chat_client.delete_entity(partition_key=key, row_key=last_row_key)

        # Update metadata
        last_row_key_num = int(last_row_key)
        metadata["LastMessageRowKey"] = self._to_row_key(
            last_row_key_num - 1 if last_row_key_num > 0 else 0
        )
        metadata["MessageCount"] = int(metadata["MessageCount"]) - 1
        await metadata_client.upsert_entity(metadata, UpdateMode.MERGE)

    def get_keys(self) -> List[str]:
        """Get all keys."""
        return asyncio_run(self.aget_keys())

    async def aget_keys(self) -> List[str]:
        """Asynchronously get all keys."""
        metadata_client = await self._atable_service_client.create_table_if_not_exists(
            self.metadata_table_name
        )
        entities = metadata_client.query_entities(
            f"PartitionKey eq '{self.metadata_partition_key}'"
        )

        keys = []
        async for entity in entities:
            keys.append(entity["RowKey"])

        return keys

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "AzureChatStore"

    @classmethod
    def _from_clients(
        cls,
        endpoint: str,
        credential: Any,
        chat_table_name: str = DEFAULT_CHAT_TABLE,
        metadata_table_name: str = DEFAULT_METADATA_TABLE,
        metadata_partition_key: str = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
    ) -> "AzureChatStore":
        """Create table service clients."""
        table_service_client = TableServiceClient(
            endpoint=endpoint, credential=credential
        )
        atable_service_client = AsyncTableServiceClient(
            endpoint=endpoint, credential=credential
        )

        return cls(
            table_service_client,
            atable_service_client,
            chat_table_name,
            metadata_table_name,
            metadata_partition_key,
            service_mode,
        )

    def _to_row_key(self, idx: int) -> str:
        """Generate a row key from an index."""
        return f"{idx:010}"

    def _get_default_metadata(self, key: str) -> dict:
        """Generate default metadata for a key."""
        return {
            "PartitionKey": self.metadata_partition_key,
            "RowKey": key,
            "LastMessageRowKey": self._to_row_key(0),
            "MessageCount": 0,
        }

    async def _get_or_default_metadata(
        self, metadata_client: AsyncTableClient, key: str
    ) -> dict:
        """
        Retrieve metadata if it exists, otherwise return default metadata
        structure.
        """
        try:
            return await metadata_client.get_entity(
                partition_key=self.metadata_partition_key, row_key=key
            )
        except ResourceNotFoundError:
            return self._get_default_metadata(key)

```
  
---|---  
###  from_connection_string `classmethod` #
```
from_connection_string(connection_string: str, chat_table_name: str = DEFAULT_CHAT_TABLE, metadata_table_name: str = DEFAULT_METADATA_TABLE, metadata_partition_key: str = None, service_mode: ServiceMode = STORAGE)

```

Creates an instance of AzureChatStore using a connection string.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
@classmethod
def from_connection_string(
    cls,
    connection_string: str,
    chat_table_name: str = DEFAULT_CHAT_TABLE,
    metadata_table_name: str = DEFAULT_METADATA_TABLE,
    metadata_partition_key: str = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
):
    """Creates an instance of AzureChatStore using a connection string."""
    table_service_client = TableServiceClient.from_connection_string(
        connection_string
    )
    atable_service_client = AsyncTableServiceClient.from_connection_string(
        connection_string
    )

    return cls(
        table_service_client,
        atable_service_client,
        chat_table_name,
        metadata_table_name,
        metadata_partition_key,
        service_mode,
    )

```
  
---|---  
###  from_account_and_key `classmethod` #
```
from_account_and_key(account_name: str, account_key: str, endpoint: Optional[str] = None, chat_table_name: str = DEFAULT_CHAT_TABLE, metadata_table_name: str = DEFAULT_METADATA_TABLE, metadata_partition_key: str = None, service_mode: ServiceMode = STORAGE) -> AzureChatStore

```

Initializes AzureChatStore from an account name and key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
@classmethod
def from_account_and_key(
    cls,
    account_name: str,
    account_key: str,
    endpoint: Optional[str] = None,
    chat_table_name: str = DEFAULT_CHAT_TABLE,
    metadata_table_name: str = DEFAULT_METADATA_TABLE,
    metadata_partition_key: str = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
) -> "AzureChatStore":
    """Initializes AzureChatStore from an account name and key."""
    if endpoint is None:
        endpoint = f"https://{account_name}.table.core.windows.net"
    credential = AzureNamedKeyCredential(account_name, account_key)
    return cls._from_clients(
        endpoint,
        credential,
        chat_table_name,
        metadata_table_name,
        metadata_partition_key,
        service_mode,
    )

```
  
---|---  
###  from_account_and_id `classmethod` #
```
from_account_and_id(account_name: str, endpoint: Optional[str] = None, chat_table_name: str = DEFAULT_CHAT_TABLE, metadata_table_name: str = DEFAULT_METADATA_TABLE, metadata_partition_key: str = None, service_mode: ServiceMode = STORAGE) -> AzureChatStore

```

Initializes AzureChatStore from an account name and managed ID.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
@classmethod
def from_account_and_id(
    cls,
    account_name: str,
    endpoint: Optional[str] = None,
    chat_table_name: str = DEFAULT_CHAT_TABLE,
    metadata_table_name: str = DEFAULT_METADATA_TABLE,
    metadata_partition_key: str = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
) -> "AzureChatStore":
    """Initializes AzureChatStore from an account name and managed ID."""
    from azure.identity import DefaultAzureCredential

    if endpoint is None:
        endpoint = f"https://{account_name}.table.core.windows.net"
    credential = DefaultAzureCredential()
    return cls._from_clients(
        endpoint,
        credential,
        chat_table_name,
        metadata_table_name,
        metadata_partition_key,
        service_mode,
    )

```
  
---|---  
###  from_sas_token `classmethod` #
```
from_sas_token(endpoint: str, sas_token: str, chat_table_name: str = DEFAULT_CHAT_TABLE, metadata_table_name: str = DEFAULT_METADATA_TABLE, metadata_partition_key: str = None, service_mode: ServiceMode = STORAGE) -> AzureChatStore

```

Creates an AzureChatStore instance using a SAS token.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
@classmethod
def from_sas_token(
    cls,
    endpoint: str,
    sas_token: str,
    chat_table_name: str = DEFAULT_CHAT_TABLE,
    metadata_table_name: str = DEFAULT_METADATA_TABLE,
    metadata_partition_key: str = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
) -> "AzureChatStore":
    """Creates an AzureChatStore instance using a SAS token."""
    credential = AzureSasCredential(sas_token)
    return cls._from_clients(
        endpoint,
        credential,
        chat_table_name,
        metadata_table_name,
        metadata_partition_key,
        service_mode,
    )

```
  
---|---  
###  from_aad_token `classmethod` #
```
from_aad_token(endpoint: str, chat_table_name: str = DEFAULT_CHAT_TABLE, metadata_table_name: str = DEFAULT_METADATA_TABLE, metadata_partition_key: str = None, service_mode: ServiceMode = STORAGE) -> AzureChatStore

```

Creates an AzureChatStore using an Azure Active Directory token.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
@classmethod
def from_aad_token(
    cls,
    endpoint: str,
    chat_table_name: str = DEFAULT_CHAT_TABLE,
    metadata_table_name: str = DEFAULT_METADATA_TABLE,
    metadata_partition_key: str = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
) -> "AzureChatStore":
    """Creates an AzureChatStore using an Azure Active Directory token."""
    from azure.identity import DefaultAzureCredential

    credential = DefaultAzureCredential()
    return cls._from_clients(
        endpoint,
        credential,
        chat_table_name,
        metadata_table_name,
        metadata_partition_key,
        service_mode,
    )

```
  
---|---  
###  set_messages #
```
set_messages(key: str, messages: List[ChatMessage]) -> None

```

Set messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
def set_messages(self, key: str, messages: List[ChatMessage]) -> None:
    """Set messages for a key."""
    asyncio_run(self.aset_messages(key, messages))

```
  
---|---  
###  aset_messages `async` #
```
aset_messages(key: str, messages: List[ChatMessage]) -> None

```

Asynchronoulsy set messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
async def aset_messages(self, key: str, messages: List[ChatMessage]) -> None:
    """Asynchronoulsy set messages for a key."""
    # Delete existing messages and insert new messages in one transaction
    chat_client = await self._atable_service_client.create_table_if_not_exists(
        self.chat_table_name
    )
    entities = chat_client.query_entities(f"PartitionKey eq '{key}'")
    all_entities = []
    async for entity in entities:
        all_entities.append(entity)

    delete_operations = (
        (TransactionOperation.DELETE, entity) for entity in all_entities
    )
    create_operations = (
        (
            TransactionOperation.CREATE,
            serialize(
                self.service_mode,
                {
                    "PartitionKey": key,
                    "RowKey": self._to_row_key(idx),
                    **message.dict(),
                },
            ),
        )
        for idx, message in enumerate(messages)
    )
    await chat_client.submit_transaction(
        chain(delete_operations, create_operations)
    )

    # Update metadata
    metadata_client = await self._atable_service_client.create_table_if_not_exists(
        self.metadata_table_name
    )
    messages_len = len(messages)
    await metadata_client.upsert_entity(
        {
            "PartitionKey": self.metadata_partition_key,
            "RowKey": key,
            "LastMessageRowKey": self._to_row_key(messages_len - 1),
            "MessageCount": messages_len,
        },
        UpdateMode.REPLACE,
    )

```
  
---|---  
###  get_messages #
```
get_messages(key: str) -> List[ChatMessage]

```

Get messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
def get_messages(self, key: str) -> List[ChatMessage]:
    """Get messages for a key."""
    return asyncio_run(self.aget_messages(key))

```
  
---|---  
###  aget_messages `async` #
```
aget_messages(key: str) -> List[ChatMessage]

```

Asynchronously get messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
async def aget_messages(self, key: str) -> List[ChatMessage]:
    """Asynchronously get messages for a key."""
    chat_client = await self._atable_service_client.create_table_if_not_exists(
        self.chat_table_name
    )
    entities = chat_client.query_entities(f"PartitionKey eq '{key}'")
    messages = []

    async for entity in entities:
        messages.append(
            ChatMessage.model_validate(deserialize(self.service_mode, entity))
        )

    return messages

```
  
---|---  
###  add_message #
```
add_message(key: str, message: ChatMessage, idx: int = None)

```

Add a message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
def add_message(self, key: str, message: ChatMessage, idx: int = None):
    """Add a message for a key."""
    asyncio_run(self.async_add_message(key, message, idx))

```
  
---|---  
###  adelete_messages `async` #
```
adelete_messages(key: str) -> Optional[List[ChatMessage]]

```

Asynchronously delete all messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
async def adelete_messages(self, key: str) -> Optional[List[ChatMessage]]:
    """Asynchronously delete all messages for a key."""
    chat_client = await self._atable_service_client.create_table_if_not_exists(
        self.chat_table_name
    )
    entities = chat_client.query_entities(f"PartitionKey eq '{key}'")
    all_entities = []
    async for entity in entities:
        all_entities.append(entity)

    await chat_client.submit_transaction(
        (TransactionOperation.DELETE, entity) for entity in all_entities
    )

    metadata_client = await self._atable_service_client.create_table_if_not_exists(
        self.metadata_table_name
    )
    await metadata_client.upsert_entity(
        self._get_default_metadata(key), UpdateMode.REPLACE
    )

```
  
---|---  
###  delete_message #
```
delete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Delete specific message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """Delete specific message for a key."""
    return asyncio_run(self.adelete_message(key, idx))

```
  
---|---  
###  adelete_message `async` #
```
adelete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Asynchronously delete specific message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
async def adelete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """Asynchronously delete specific message for a key."""
    # Fetch metadata to get the message count
    metadata_client = await self._atable_service_client.create_table_if_not_exists(
        self.metadata_table_name
    )
    metadata = await metadata_client.get_entity(
        partition_key=self.metadata_partition_key, row_key=key
    )

    # Index out of bounds
    message_count = int(metadata["MessageCount"])
    if idx >= message_count:
        return None

    # Delete the message
    chat_client = await self._atable_service_client.create_table_if_not_exists(
        self.chat_table_name
    )
    await chat_client.delete_entity(
        partition_key=key, row_key=self._to_row_key(idx)
    )

    # Update metadata if last message was deleted
    if idx == message_count - 1:
        metadata["LastMessageRowKey"] = self._to_row_key(idx - 1)
        metadata["MessageCount"] = message_count - 1
        await metadata_client.upsert_entity(metadata, mode=UpdateMode.MERGE)

```
  
---|---  
###  delete_last_message #
```
delete_last_message(key: str) -> Optional[ChatMessage]

```

Delete last message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
def delete_last_message(self, key: str) -> Optional[ChatMessage]:
    """Delete last message for a key."""
    return asyncio_run(self.adelete_last_message(key))

```
  
---|---  
###  adelete_last_message `async` #
```
adelete_last_message(key: str) -> Optional[ChatMessage]

```

Async delete last message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
async def adelete_last_message(self, key: str) -> Optional[ChatMessage]:
    """Async delete last message for a key."""
    metadata_client = await self._atable_service_client.create_table_if_not_exists(
        self.metadata_table_name
    )
    # Retrieve metadata to get the last message row key
    metadata = await metadata_client.get_entity(
        partition_key=self.metadata_partition_key, row_key=key
    )
    last_row_key = metadata["LastMessageRowKey"]

    chat_client = await self._atable_service_client.create_table_if_not_exists(
        self.chat_table_name
    )
    # Delete the last message
    await chat_client.delete_entity(partition_key=key, row_key=last_row_key)

    # Update metadata
    last_row_key_num = int(last_row_key)
    metadata["LastMessageRowKey"] = self._to_row_key(
        last_row_key_num - 1 if last_row_key_num > 0 else 0
    )
    metadata["MessageCount"] = int(metadata["MessageCount"]) - 1
    await metadata_client.upsert_entity(metadata, UpdateMode.MERGE)

```
  
---|---  
###  get_keys #
```
get_keys() -> List[str]

```

Get all keys.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
def get_keys(self) -> List[str]:
    """Get all keys."""
    return asyncio_run(self.aget_keys())

```
  
---|---  
###  aget_keys `async` #
```
aget_keys() -> List[str]

```

Asynchronously get all keys.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
async def aget_keys(self) -> List[str]:
    """Asynchronously get all keys."""
    metadata_client = await self._atable_service_client.create_table_if_not_exists(
        self.metadata_table_name
    )
    entities = metadata_client.query_entities(
        f"PartitionKey eq '{self.metadata_partition_key}'"
    )

    keys = []
    async for entity in entities:
        keys.append(entity["RowKey"])

    return keys

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-azure/llama_index/storage/chat_store/azure/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "AzureChatStore"

```
  
---|---
