# Gel
##  GelChatStore #
Bases: `BaseChatStore`
Chat store implementation using Gel database.
Stores and retrieves chat messages using Gel as the backend storage.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
class GelChatStore(BaseChatStore):
    """
    Chat store implementation using Gel database.

    Stores and retrieves chat messages using Gel as the backend storage.
    """

    record_type: str
    _sync_client: Optional[gel.Client] = PrivateAttr()
    _async_client: Optional[gel.AsyncIOClient] = PrivateAttr()

    def __init__(
        self,
        record_type: str = "Record",
    ):
        """
        Initialize GelChatStore.

        Args:
            record_type: The name of the record type in Gel schema.

        """
        super().__init__(record_type=record_type)

        self._sync_client = None
        self._async_client = None

    def get_sync_client(self):
        """Get or initialize a synchronous Gel client."""
        if self._async_client is not None:
            raise RuntimeError(
                "GelChatStore has already been used in async mode. "
                "If you were intentionally trying to use different IO modes at the same time, "
                "please create a new instance instead."
            )
        if self._sync_client is None:
            self._sync_client = gel.create_client()

            try:
                self._sync_client.ensure_connected()
            except gel.errors.ClientConnectionError as e:
                _logger.error(NO_PROJECT_MESSAGE)
                raise

            try:
                self._sync_client.query(f"select {self.record_type};")
            except gel.errors.InvalidReferenceError as e:
                _logger.error(
                    Template(MISSING_RECORD_TYPE_TEMPLATE).render(
                        record_type=self.record_type
                    )
                )
                raise

        return self._sync_client

    async def get_async_client(self):
        """Get or initialize an asynchronous Gel client."""
        if self._sync_client is not None:
            raise RuntimeError(
                "GelChatStore has already been used in sync mode. "
                "If you were intentionally trying to use different IO modes at the same time, "
                "please create a new instance instead."
            )
        if self._async_client is None:
            self._async_client = gel.create_async_client()

            try:
                await self._async_client.ensure_connected()
            except gel.errors.ClientConnectionError as e:
                _logger.error(NO_PROJECT_MESSAGE)
                raise

            try:
                await self._async_client.query(f"select {self.record_type};")
            except gel.errors.InvalidReferenceError as e:
                _logger.error(
                    Template(MISSING_RECORD_TYPE_TEMPLATE).render(
                        record_type=self.record_type
                    )
                )
                raise

        return self._async_client

    def set_messages(self, key: str, messages: list[ChatMessage]) -> None:
        """Set messages for a key."""
        client = self.get_sync_client()
        client.query(
            SET_MESSAGES_QUERY,
            key=key,
            value=[message.model_dump_json() for message in messages],
        )

    async def aset_messages(self, key: str, messages: list[ChatMessage]) -> None:
        """Async version of Get messages for a key."""
        client = await self.get_async_client()
        await client.query(
            SET_MESSAGES_QUERY,
            key=key,
            value=[message.model_dump_json() for message in messages],
        )

    def get_messages(self, key: str) -> list[ChatMessage]:
        """Get messages for a key."""
        client = self.get_sync_client()
        result = client.query_single(GET_MESSAGES_QUERY, key=key) or []
        return [ChatMessage.model_validate_json(message) for message in result]

    async def aget_messages(self, key: str) -> list[ChatMessage]:
        """Async version of Get messages for a key."""
        client = await self.get_async_client()
        result = await client.query_single(GET_MESSAGES_QUERY, key=key) or []
        return [ChatMessage.model_validate_json(message) for message in result]

    def add_message(self, key: str, message: ChatMessage) -> None:
        """Add a message for a key."""
        client = self.get_sync_client()
        client.query(ADD_MESSAGE_QUERY, key=key, value=[message.model_dump_json()])

    async def async_add_message(self, key: str, message: ChatMessage) -> None:
        """Async version of Add a message for a key."""
        client = await self.get_async_client()
        await client.query(
            ADD_MESSAGE_QUERY, key=key, value=[message.model_dump_json()]
        )

    def delete_messages(self, key: str) -> Optional[list[ChatMessage]]:
        """Delete messages for a key."""
        client = self.get_sync_client()
        client.query(DELETE_MESSAGES_QUERY, key=key)

    async def adelete_messages(self, key: str) -> Optional[list[ChatMessage]]:
        """Async version of Delete messages for a key."""
        client = await self.get_async_client()
        await client.query(DELETE_MESSAGES_QUERY, key=key)

    def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """Delete specific message for a key."""
        client = self.get_sync_client()
        result = client.query_single(DELETE_MESSAGE_QUERY, key=key, idx=idx)
        return ChatMessage.model_validate_json(result) if result else None

    async def adelete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """Async version of Delete specific message for a key."""
        client = await self.get_async_client()
        result = await client.query_single(DELETE_MESSAGE_QUERY, key=key, idx=idx)
        return ChatMessage.model_validate_json(result) if result else None

    def delete_last_message(self, key: str) -> Optional[ChatMessage]:
        """Delete last message for a key."""
        client = self.get_sync_client()
        result = client.query_single(DELETE_LAST_MESSAGE_QUERY, key=key)
        return ChatMessage.model_validate_json(result) if result else None

    async def adelete_last_message(self, key: str) -> Optional[ChatMessage]:
        """Async version of Delete last message for a key."""
        client = await self.get_async_client()
        result = await client.query_single(DELETE_LAST_MESSAGE_QUERY, key=key)
        return ChatMessage.model_validate_json(result) if result else None

    def get_keys(self) -> list[str]:
        """Get all keys."""
        client = self.get_sync_client()
        return client.query(GET_KEYS_QUERY)

    async def aget_keys(self) -> list[str]:
        """Async version of Get all keys."""
        client = await self.get_async_client()
        return await client.query(GET_KEYS_QUERY)

```
  
---|---  
###  get_sync_client #
```
get_sync_client()

```

Get or initialize a synchronous Gel client.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
def get_sync_client(self):
    """Get or initialize a synchronous Gel client."""
    if self._async_client is not None:
        raise RuntimeError(
            "GelChatStore has already been used in async mode. "
            "If you were intentionally trying to use different IO modes at the same time, "
            "please create a new instance instead."
        )
    if self._sync_client is None:
        self._sync_client = gel.create_client()

        try:
            self._sync_client.ensure_connected()
        except gel.errors.ClientConnectionError as e:
            _logger.error(NO_PROJECT_MESSAGE)
            raise

        try:
            self._sync_client.query(f"select {self.record_type};")
        except gel.errors.InvalidReferenceError as e:
            _logger.error(
                Template(MISSING_RECORD_TYPE_TEMPLATE).render(
                    record_type=self.record_type
                )
            )
            raise

    return self._sync_client

```
  
---|---  
###  get_async_client `async` #
```
get_async_client()

```

Get or initialize an asynchronous Gel client.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
async def get_async_client(self):
    """Get or initialize an asynchronous Gel client."""
    if self._sync_client is not None:
        raise RuntimeError(
            "GelChatStore has already been used in sync mode. "
            "If you were intentionally trying to use different IO modes at the same time, "
            "please create a new instance instead."
        )
    if self._async_client is None:
        self._async_client = gel.create_async_client()

        try:
            await self._async_client.ensure_connected()
        except gel.errors.ClientConnectionError as e:
            _logger.error(NO_PROJECT_MESSAGE)
            raise

        try:
            await self._async_client.query(f"select {self.record_type};")
        except gel.errors.InvalidReferenceError as e:
            _logger.error(
                Template(MISSING_RECORD_TYPE_TEMPLATE).render(
                    record_type=self.record_type
                )
            )
            raise

    return self._async_client

```
  
---|---  
###  set_messages #
```
set_messages(key: str, messages: list[ChatMessage]) -> None

```

Set messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
def set_messages(self, key: str, messages: list[ChatMessage]) -> None:
    """Set messages for a key."""
    client = self.get_sync_client()
    client.query(
        SET_MESSAGES_QUERY,
        key=key,
        value=[message.model_dump_json() for message in messages],
    )

```
  
---|---  
###  aset_messages `async` #
```
aset_messages(key: str, messages: list[ChatMessage]) -> None

```

Async version of Get messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
async def aset_messages(self, key: str, messages: list[ChatMessage]) -> None:
    """Async version of Get messages for a key."""
    client = await self.get_async_client()
    await client.query(
        SET_MESSAGES_QUERY,
        key=key,
        value=[message.model_dump_json() for message in messages],
    )

```
  
---|---  
###  get_messages #
```
get_messages(key: str) -> list[ChatMessage]

```

Get messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
def get_messages(self, key: str) -> list[ChatMessage]:
    """Get messages for a key."""
    client = self.get_sync_client()
    result = client.query_single(GET_MESSAGES_QUERY, key=key) or []
    return [ChatMessage.model_validate_json(message) for message in result]

```
  
---|---  
###  aget_messages `async` #
```
aget_messages(key: str) -> list[ChatMessage]

```

Async version of Get messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
async def aget_messages(self, key: str) -> list[ChatMessage]:
    """Async version of Get messages for a key."""
    client = await self.get_async_client()
    result = await client.query_single(GET_MESSAGES_QUERY, key=key) or []
    return [ChatMessage.model_validate_json(message) for message in result]

```
  
---|---  
###  add_message #
```
add_message(key: str, message: ChatMessage) -> None

```

Add a message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
def add_message(self, key: str, message: ChatMessage) -> None:
    """Add a message for a key."""
    client = self.get_sync_client()
    client.query(ADD_MESSAGE_QUERY, key=key, value=[message.model_dump_json()])

```
  
---|---  
###  async_add_message `async` #
```
async_add_message(key: str, message: ChatMessage) -> None

```

Async version of Add a message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
async def async_add_message(self, key: str, message: ChatMessage) -> None:
    """Async version of Add a message for a key."""
    client = await self.get_async_client()
    await client.query(
        ADD_MESSAGE_QUERY, key=key, value=[message.model_dump_json()]
    )

```
  
---|---  
###  delete_messages #
```
delete_messages(key: str) -> Optional[list[ChatMessage]]

```

Delete messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
def delete_messages(self, key: str) -> Optional[list[ChatMessage]]:
    """Delete messages for a key."""
    client = self.get_sync_client()
    client.query(DELETE_MESSAGES_QUERY, key=key)

```
  
---|---  
###  adelete_messages `async` #
```
adelete_messages(key: str) -> Optional[list[ChatMessage]]

```

Async version of Delete messages for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
async def adelete_messages(self, key: str) -> Optional[list[ChatMessage]]:
    """Async version of Delete messages for a key."""
    client = await self.get_async_client()
    await client.query(DELETE_MESSAGES_QUERY, key=key)

```
  
---|---  
###  delete_message #
```
delete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Delete specific message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """Delete specific message for a key."""
    client = self.get_sync_client()
    result = client.query_single(DELETE_MESSAGE_QUERY, key=key, idx=idx)
    return ChatMessage.model_validate_json(result) if result else None

```
  
---|---  
###  adelete_message `async` #
```
adelete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Async version of Delete specific message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
async def adelete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """Async version of Delete specific message for a key."""
    client = await self.get_async_client()
    result = await client.query_single(DELETE_MESSAGE_QUERY, key=key, idx=idx)
    return ChatMessage.model_validate_json(result) if result else None

```
  
---|---  
###  delete_last_message #
```
delete_last_message(key: str) -> Optional[ChatMessage]

```

Delete last message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
def delete_last_message(self, key: str) -> Optional[ChatMessage]:
    """Delete last message for a key."""
    client = self.get_sync_client()
    result = client.query_single(DELETE_LAST_MESSAGE_QUERY, key=key)
    return ChatMessage.model_validate_json(result) if result else None

```
  
---|---  
###  adelete_last_message `async` #
```
adelete_last_message(key: str) -> Optional[ChatMessage]

```

Async version of Delete last message for a key.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
async def adelete_last_message(self, key: str) -> Optional[ChatMessage]:
    """Async version of Delete last message for a key."""
    client = await self.get_async_client()
    result = await client.query_single(DELETE_LAST_MESSAGE_QUERY, key=key)
    return ChatMessage.model_validate_json(result) if result else None

```
  
---|---  
###  get_keys #
```
get_keys() -> list[str]

```

Get all keys.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
def get_keys(self) -> list[str]:
    """Get all keys."""
    client = self.get_sync_client()
    return client.query(GET_KEYS_QUERY)

```
  
---|---  
###  aget_keys `async` #
```
aget_keys() -> list[str]

```

Async version of Get all keys.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-gel/llama_index/storage/chat_store/gel/base.py`

| ```
async def aget_keys(self) -> list[str]:
    """Async version of Get all keys."""
    client = await self.get_async_client()
    return await client.query(GET_KEYS_QUERY)

```
  
---|---
