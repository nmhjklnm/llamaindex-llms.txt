# Index
Base interface class for storing chat history per user.
##  BaseChatStore #
Bases: `BaseComponent`
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
class BaseChatStore(BaseComponent):
    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "BaseChatStore"

    @abstractmethod
    def set_messages(self, key: str, messages: List[ChatMessage]) -> None:
        """Set messages for a key."""
        ...

    @abstractmethod
    def get_messages(self, key: str) -> List[ChatMessage]:
        """Get messages for a key."""
        ...

    @abstractmethod
    def add_message(self, key: str, message: ChatMessage) -> None:
        """Add a message for a key."""
        ...

    @abstractmethod
    def delete_messages(self, key: str) -> Optional[List[ChatMessage]]:
        """Delete messages for a key."""
        ...

    @abstractmethod
    def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """Delete specific message for a key."""
        ...

    @abstractmethod
    def delete_last_message(self, key: str) -> Optional[ChatMessage]:
        """Delete last message for a key."""
        ...

    @abstractmethod
    def get_keys(self) -> List[str]:
        """Get all keys."""
        ...

    async def aset_messages(self, key: str, messages: List[ChatMessage]) -> None:
        """Async version of Get messages for a key."""
        await asyncio.to_thread(self.set_messages, key, messages)

    async def aget_messages(self, key: str) -> List[ChatMessage]:
        """Async version of Get messages for a key."""
        return await asyncio.to_thread(self.get_messages, key)

    async def async_add_message(self, key: str, message: ChatMessage) -> None:
        """Async version of Add a message for a key."""
        await asyncio.to_thread(self.add_message, key, message)

    async def adelete_messages(self, key: str) -> Optional[List[ChatMessage]]:
        """Async version of Delete messages for a key."""
        return await asyncio.to_thread(self.delete_messages, key)

    async def adelete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """Async version of Delete specific message for a key."""
        return await asyncio.to_thread(self.delete_message, key, idx)

    async def adelete_last_message(self, key: str) -> Optional[ChatMessage]:
        """Async version of Delete last message for a key."""
        return await asyncio.to_thread(self.delete_last_message, key)

    async def aget_keys(self) -> List[str]:
        """Async version of Get all keys."""
        return await asyncio.to_thread(self.get_keys)

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "BaseChatStore"

```
  
---|---  
###  set_messages `abstractmethod` #
```
set_messages(key: str, messages: List[ChatMessage]) -> None

```

Set messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
@abstractmethod
def set_messages(self, key: str, messages: List[ChatMessage]) -> None:
    """Set messages for a key."""
    ...

```
  
---|---  
###  get_messages `abstractmethod` #
```
get_messages(key: str) -> List[ChatMessage]

```

Get messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
@abstractmethod
def get_messages(self, key: str) -> List[ChatMessage]:
    """Get messages for a key."""
    ...

```
  
---|---  
###  add_message `abstractmethod` #
```
add_message(key: str, message: ChatMessage) -> None

```

Add a message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
@abstractmethod
def add_message(self, key: str, message: ChatMessage) -> None:
    """Add a message for a key."""
    ...

```
  
---|---  
###  delete_messages `abstractmethod` #
```
delete_messages(key: str) -> Optional[List[ChatMessage]]

```

Delete messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
@abstractmethod
def delete_messages(self, key: str) -> Optional[List[ChatMessage]]:
    """Delete messages for a key."""
    ...

```
  
---|---  
###  delete_message `abstractmethod` #
```
delete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Delete specific message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
@abstractmethod
def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """Delete specific message for a key."""
    ...

```
  
---|---  
###  delete_last_message `abstractmethod` #
```
delete_last_message(key: str) -> Optional[ChatMessage]

```

Delete last message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
@abstractmethod
def delete_last_message(self, key: str) -> Optional[ChatMessage]:
    """Delete last message for a key."""
    ...

```
  
---|---  
###  get_keys `abstractmethod` #
```
get_keys() -> List[str]

```

Get all keys.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
@abstractmethod
def get_keys(self) -> List[str]:
    """Get all keys."""
    ...

```
  
---|---  
###  aset_messages `async` #
```
aset_messages(key: str, messages: List[ChatMessage]) -> None

```

Async version of Get messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
async def aset_messages(self, key: str, messages: List[ChatMessage]) -> None:
    """Async version of Get messages for a key."""
    await asyncio.to_thread(self.set_messages, key, messages)

```
  
---|---  
###  aget_messages `async` #
```
aget_messages(key: str) -> List[ChatMessage]

```

Async version of Get messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
async def aget_messages(self, key: str) -> List[ChatMessage]:
    """Async version of Get messages for a key."""
    return await asyncio.to_thread(self.get_messages, key)

```
  
---|---  
###  async_add_message `async` #
```
async_add_message(key: str, message: ChatMessage) -> None

```

Async version of Add a message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
async def async_add_message(self, key: str, message: ChatMessage) -> None:
    """Async version of Add a message for a key."""
    await asyncio.to_thread(self.add_message, key, message)

```
  
---|---  
###  adelete_messages `async` #
```
adelete_messages(key: str) -> Optional[List[ChatMessage]]

```

Async version of Delete messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
async def adelete_messages(self, key: str) -> Optional[List[ChatMessage]]:
    """Async version of Delete messages for a key."""
    return await asyncio.to_thread(self.delete_messages, key)

```
  
---|---  
###  adelete_message `async` #
```
adelete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Async version of Delete specific message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
async def adelete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """Async version of Delete specific message for a key."""
    return await asyncio.to_thread(self.delete_message, key, idx)

```
  
---|---  
###  adelete_last_message `async` #
```
adelete_last_message(key: str) -> Optional[ChatMessage]

```

Async version of Delete last message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
async def adelete_last_message(self, key: str) -> Optional[ChatMessage]:
    """Async version of Delete last message for a key."""
    return await asyncio.to_thread(self.delete_last_message, key)

```
  
---|---  
###  aget_keys `async` #
```
aget_keys() -> List[str]

```

Async version of Get all keys.
Source code in `llama-index-core/llama_index/core/storage/chat_store/base.py`

| ```
async def aget_keys(self) -> List[str]:
    """Async version of Get all keys."""
    return await asyncio.to_thread(self.get_keys)

```
  
---|---
