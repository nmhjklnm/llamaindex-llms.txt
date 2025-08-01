# Simple
##  SimpleChatStore #
Bases: `BaseChatStore`
Simple chat store. Async methods provide same functionality as sync methods in this class.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
class SimpleChatStore(BaseChatStore):
    """Simple chat store. Async methods provide same functionality as sync methods in this class."""

    store: Dict[str, List[AnnotatedChatMessage]] = Field(default_factory=dict)

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "SimpleChatStore"

    def set_messages(self, key: str, messages: List[ChatMessage]) -> None:
        """Set messages for a key."""
        self.store[key] = messages

    def get_messages(self, key: str) -> List[ChatMessage]:
        """Get messages for a key."""
        return self.store.get(key, [])

    def add_message(
        self, key: str, message: ChatMessage, idx: Optional[int] = None
    ) -> None:
        """Add a message for a key."""
        if idx is None:
            self.store.setdefault(key, []).append(message)
        else:
            self.store.setdefault(key, []).insert(idx, message)

    def delete_messages(self, key: str) -> Optional[List[ChatMessage]]:
        """Delete messages for a key."""
        if key not in self.store:
            return None
        return self.store.pop(key)

    def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """Delete specific message for a key."""
        if key not in self.store:
            return None
        if idx >= len(self.store[key]):
            return None
        return self.store[key].pop(idx)

    def delete_last_message(self, key: str) -> Optional[ChatMessage]:
        """Delete last message for a key."""
        if key not in self.store:
            return None
        return self.store[key].pop()

    def get_keys(self) -> List[str]:
        """Get all keys."""
        return list(self.store.keys())

    def persist(
        self,
        persist_path: str = "chat_store.json",
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> None:
        """Persist the docstore to a file."""
        fs = fs or fsspec.filesystem("file")
        dirpath = os.path.dirname(persist_path)
        if not fs.exists(dirpath):
            fs.makedirs(dirpath)

        with fs.open(persist_path, "w") as f:
            f.write(self.json())

    @classmethod
    def from_persist_path(
        cls,
        persist_path: str = "chat_store.json",
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> "SimpleChatStore":
        """Create a SimpleChatStore from a persist path."""
        fs = fs or fsspec.filesystem("file")
        if not fs.exists(persist_path):
            return cls()
        with fs.open(persist_path, "r") as f:
            data = json.load(f)

        if isinstance(data, str):
            return cls.model_validate_json(data)
        else:
            return cls.model_validate(data)

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "SimpleChatStore"

```
  
---|---  
###  set_messages #
```
set_messages(key: str, messages: List[ChatMessage]) -> None

```

Set messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
def set_messages(self, key: str, messages: List[ChatMessage]) -> None:
    """Set messages for a key."""
    self.store[key] = messages

```
  
---|---  
###  get_messages #
```
get_messages(key: str) -> List[ChatMessage]

```

Get messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
def get_messages(self, key: str) -> List[ChatMessage]:
    """Get messages for a key."""
    return self.store.get(key, [])

```
  
---|---  
###  add_message #
```
add_message(key: str, message: ChatMessage, idx: Optional[int] = None) -> None

```

Add a message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
def add_message(
    self, key: str, message: ChatMessage, idx: Optional[int] = None
) -> None:
    """Add a message for a key."""
    if idx is None:
        self.store.setdefault(key, []).append(message)
    else:
        self.store.setdefault(key, []).insert(idx, message)

```
  
---|---  
###  delete_messages #
```
delete_messages(key: str) -> Optional[List[ChatMessage]]

```

Delete messages for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
def delete_messages(self, key: str) -> Optional[List[ChatMessage]]:
    """Delete messages for a key."""
    if key not in self.store:
        return None
    return self.store.pop(key)

```
  
---|---  
###  delete_message #
```
delete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Delete specific message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """Delete specific message for a key."""
    if key not in self.store:
        return None
    if idx >= len(self.store[key]):
        return None
    return self.store[key].pop(idx)

```
  
---|---  
###  delete_last_message #
```
delete_last_message(key: str) -> Optional[ChatMessage]

```

Delete last message for a key.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
def delete_last_message(self, key: str) -> Optional[ChatMessage]:
    """Delete last message for a key."""
    if key not in self.store:
        return None
    return self.store[key].pop()

```
  
---|---  
###  get_keys #
```
get_keys() -> List[str]

```

Get all keys.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
def get_keys(self) -> List[str]:
    """Get all keys."""
    return list(self.store.keys())

```
  
---|---  
###  persist #
```
persist(persist_path: str = 'chat_store.json', fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the docstore to a file.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
def persist(
    self,
    persist_path: str = "chat_store.json",
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> None:
    """Persist the docstore to a file."""
    fs = fs or fsspec.filesystem("file")
    dirpath = os.path.dirname(persist_path)
    if not fs.exists(dirpath):
        fs.makedirs(dirpath)

    with fs.open(persist_path, "w") as f:
        f.write(self.json())

```
  
---|---  
###  from_persist_path `classmethod` #
```
from_persist_path(persist_path: str = 'chat_store.json', fs: Optional[AbstractFileSystem] = None) -> SimpleChatStore

```

Create a SimpleChatStore from a persist path.
Source code in `llama-index-core/llama_index/core/storage/chat_store/simple_chat_store.py`

| ```
@classmethod
def from_persist_path(
    cls,
    persist_path: str = "chat_store.json",
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> "SimpleChatStore":
    """Create a SimpleChatStore from a persist path."""
    fs = fs or fsspec.filesystem("file")
    if not fs.exists(persist_path):
        return cls()
    with fs.open(persist_path, "r") as f:
        data = json.load(f)

    if isinstance(data, str):
        return cls.model_validate_json(data)
    else:
        return cls.model_validate(data)

```
  
---|---
