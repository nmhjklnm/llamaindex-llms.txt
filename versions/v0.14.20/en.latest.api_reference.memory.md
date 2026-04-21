# Index
##  BaseMemory #
Bases: `BaseComponent`
Base class for all memory types.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
class BaseMemory(BaseComponent):
    """Base class for all memory types."""

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "BaseMemory"

    @classmethod
    @abstractmethod
    def from_defaults(
        cls,
        **kwargs: Any,
    ) -> "BaseMemory":
        """Create a chat memory from defaults."""

    @abstractmethod
    def get(self, input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]:
        """Get chat history."""

    async def aget(
        self, input: Optional[str] = None, **kwargs: Any
    ) -> List[ChatMessage]:
        """Get chat history."""
        return await asyncio.to_thread(self.get, input=input, **kwargs)

    @abstractmethod
    def get_all(self) -> List[ChatMessage]:
        """Get all chat history."""

    async def aget_all(self) -> List[ChatMessage]:
        """Get all chat history."""
        return await asyncio.to_thread(self.get_all)

    @abstractmethod
    def put(self, message: ChatMessage) -> None:
        """Put chat history."""

    async def aput(self, message: ChatMessage) -> None:
        """Put chat history."""
        await asyncio.to_thread(self.put, message)

    def put_messages(self, messages: List[ChatMessage]) -> None:
        """Put chat history."""
        for message in messages:
            self.put(message)

    async def aput_messages(self, messages: List[ChatMessage]) -> None:
        """Put chat history."""
        await asyncio.to_thread(self.put_messages, messages)

    @abstractmethod
    def set(self, messages: List[ChatMessage]) -> None:
        """Set chat history."""

    async def aset(self, messages: List[ChatMessage]) -> None:
        """Set chat history."""
        await asyncio.to_thread(self.set, messages)

    @abstractmethod
    def reset(self) -> None:
        """Reset chat history."""

    async def areset(self) -> None:
        """Reset chat history."""
        await asyncio.to_thread(self.reset)

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "BaseMemory"

```
  
---|---  
###  from_defaults `abstractmethod` `classmethod` #
```
from_defaults(**kwargs: Any) -> BaseMemory

```

Create a chat memory from defaults.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@classmethod
@abstractmethod
def from_defaults(
    cls,
    **kwargs: Any,
) -> "BaseMemory":
    """Create a chat memory from defaults."""

```
  
---|---  
###  get `abstractmethod` #
```
get(input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]

```

Get chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@abstractmethod
def get(self, input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]:
    """Get chat history."""

```
  
---|---  
###  aget `async` #
```
aget(input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]

```

Get chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aget(
    self, input: Optional[str] = None, **kwargs: Any
) -> List[ChatMessage]:
    """Get chat history."""
    return await asyncio.to_thread(self.get, input=input, **kwargs)

```
  
---|---  
###  get_all `abstractmethod` #
```
get_all() -> List[ChatMessage]

```

Get all chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@abstractmethod
def get_all(self) -> List[ChatMessage]:
    """Get all chat history."""

```
  
---|---  
###  aget_all `async` #
```
aget_all() -> List[ChatMessage]

```

Get all chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aget_all(self) -> List[ChatMessage]:
    """Get all chat history."""
    return await asyncio.to_thread(self.get_all)

```
  
---|---  
###  put `abstractmethod` #
```
put(message: ChatMessage) -> None

```

Put chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@abstractmethod
def put(self, message: ChatMessage) -> None:
    """Put chat history."""

```
  
---|---  
###  aput `async` #
```
aput(message: ChatMessage) -> None

```

Put chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aput(self, message: ChatMessage) -> None:
    """Put chat history."""
    await asyncio.to_thread(self.put, message)

```
  
---|---  
###  put_messages #
```
put_messages(messages: List[ChatMessage]) -> None

```

Put chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
def put_messages(self, messages: List[ChatMessage]) -> None:
    """Put chat history."""
    for message in messages:
        self.put(message)

```
  
---|---  
###  aput_messages `async` #
```
aput_messages(messages: List[ChatMessage]) -> None

```

Put chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aput_messages(self, messages: List[ChatMessage]) -> None:
    """Put chat history."""
    await asyncio.to_thread(self.put_messages, messages)

```
  
---|---  
###  set `abstractmethod` #
```
set(messages: List[ChatMessage]) -> None

```

Set chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@abstractmethod
def set(self, messages: List[ChatMessage]) -> None:
    """Set chat history."""

```
  
---|---  
###  aset `async` #
```
aset(messages: List[ChatMessage]) -> None

```

Set chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aset(self, messages: List[ChatMessage]) -> None:
    """Set chat history."""
    await asyncio.to_thread(self.set, messages)

```
  
---|---  
###  reset `abstractmethod` #
```
reset() -> None

```

Reset chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@abstractmethod
def reset(self) -> None:
    """Reset chat history."""

```
  
---|---  
###  areset `async` #
```
areset() -> None

```

Reset chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def areset(self) -> None:
    """Reset chat history."""
    await asyncio.to_thread(self.reset)

```
  
---|---  
##  BaseChatStoreMemory #
Bases: `BaseMemory`
Base class for storing multi-tenant chat history.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`chat_store` |  `BaseChatStore` |  Simple chat store. Async methods provide same functionality as sync methods in this class. |  `<dynamic>`  
`chat_store_key` |  `str` |  |  `'chat_history'`  
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
class BaseChatStoreMemory(BaseMemory):
    """Base class for storing multi-tenant chat history."""

    chat_store: SerializeAsAny[BaseChatStore] = Field(default_factory=SimpleChatStore)
    chat_store_key: str = Field(default=DEFAULT_CHAT_STORE_KEY)

    @field_serializer("chat_store")
    def serialize_courses_in_order(self, chat_store: BaseChatStore) -> dict:
        res = chat_store.model_dump()
        res.update({"class_name": chat_store.class_name()})
        return res

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "BaseChatStoreMemory"

    @classmethod
    @abstractmethod
    def from_defaults(
        cls,
        chat_history: Optional[List[ChatMessage]] = None,
        llm: Optional[LLM] = None,
        **kwargs: Any,
    ) -> "BaseChatStoreMemory":
        """Create a chat memory from defaults."""

    def get_all(self) -> List[ChatMessage]:
        """Get all chat history."""
        return self.chat_store.get_messages(self.chat_store_key)

    async def aget_all(self) -> List[ChatMessage]:
        """Get all chat history."""
        return await self.chat_store.aget_messages(self.chat_store_key)

    def get(self, input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]:
        """Get chat history."""
        return self.chat_store.get_messages(self.chat_store_key, **kwargs)

    async def aget(
        self, input: Optional[str] = None, **kwargs: Any
    ) -> List[ChatMessage]:
        """Get chat history."""
        return await self.chat_store.aget_messages(self.chat_store_key, **kwargs)

    def put(self, message: ChatMessage) -> None:
        """Put chat history."""
        # ensure everything is serialized
        self.chat_store.add_message(self.chat_store_key, message)

    async def aput(self, message: ChatMessage) -> None:
        """Put chat history."""
        # ensure everything is serialized
        await self.chat_store.async_add_message(self.chat_store_key, message)

    def set(self, messages: List[ChatMessage]) -> None:
        """Set chat history."""
        self.chat_store.set_messages(self.chat_store_key, messages)

    async def aset(self, messages: List[ChatMessage]) -> None:
        """Set chat history."""
        # ensure everything is serialized
        await self.chat_store.aset_messages(self.chat_store_key, messages)

    def reset(self) -> None:
        """Reset chat history."""
        self.chat_store.delete_messages(self.chat_store_key)

    async def areset(self) -> None:
        """Reset chat history."""
        await self.chat_store.adelete_messages(self.chat_store_key)

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "BaseChatStoreMemory"

```
  
---|---  
###  from_defaults `abstractmethod` `classmethod` #
```
from_defaults(chat_history: Optional[List[ChatMessage]] = None, llm: Optional[LLM] = None, **kwargs: Any) -> BaseChatStoreMemory

```

Create a chat memory from defaults.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
@classmethod
@abstractmethod
def from_defaults(
    cls,
    chat_history: Optional[List[ChatMessage]] = None,
    llm: Optional[LLM] = None,
    **kwargs: Any,
) -> "BaseChatStoreMemory":
    """Create a chat memory from defaults."""

```
  
---|---  
###  get_all #
```
get_all() -> List[ChatMessage]

```

Get all chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
def get_all(self) -> List[ChatMessage]:
    """Get all chat history."""
    return self.chat_store.get_messages(self.chat_store_key)

```
  
---|---  
###  aget_all `async` #
```
aget_all() -> List[ChatMessage]

```

Get all chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aget_all(self) -> List[ChatMessage]:
    """Get all chat history."""
    return await self.chat_store.aget_messages(self.chat_store_key)

```
  
---|---  
###  get #
```
get(input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]

```

Get chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
def get(self, input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]:
    """Get chat history."""
    return self.chat_store.get_messages(self.chat_store_key, **kwargs)

```
  
---|---  
###  aget `async` #
```
aget(input: Optional[str] = None, **kwargs: Any) -> List[ChatMessage]

```

Get chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aget(
    self, input: Optional[str] = None, **kwargs: Any
) -> List[ChatMessage]:
    """Get chat history."""
    return await self.chat_store.aget_messages(self.chat_store_key, **kwargs)

```
  
---|---  
###  put #
```
put(message: ChatMessage) -> None

```

Put chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
def put(self, message: ChatMessage) -> None:
    """Put chat history."""
    # ensure everything is serialized
    self.chat_store.add_message(self.chat_store_key, message)

```
  
---|---  
###  aput `async` #
```
aput(message: ChatMessage) -> None

```

Put chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aput(self, message: ChatMessage) -> None:
    """Put chat history."""
    # ensure everything is serialized
    await self.chat_store.async_add_message(self.chat_store_key, message)

```
  
---|---  
###  set #
```
set(messages: List[ChatMessage]) -> None

```

Set chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
def set(self, messages: List[ChatMessage]) -> None:
    """Set chat history."""
    self.chat_store.set_messages(self.chat_store_key, messages)

```
  
---|---  
###  aset `async` #
```
aset(messages: List[ChatMessage]) -> None

```

Set chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def aset(self, messages: List[ChatMessage]) -> None:
    """Set chat history."""
    # ensure everything is serialized
    await self.chat_store.aset_messages(self.chat_store_key, messages)

```
  
---|---  
###  reset #
```
reset() -> None

```

Reset chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
def reset(self) -> None:
    """Reset chat history."""
    self.chat_store.delete_messages(self.chat_store_key)

```
  
---|---  
###  areset `async` #
```
areset() -> None

```

Reset chat history.
Source code in `llama-index-core/llama_index/core/memory/types.py`

| ```
async def areset(self) -> None:
    """Reset chat history."""
    await self.chat_store.adelete_messages(self.chat_store_key)

```
  
---|---
