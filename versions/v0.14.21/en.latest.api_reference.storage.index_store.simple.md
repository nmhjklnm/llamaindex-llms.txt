# Simple
##  SimpleIndexStore #
Bases: `KVIndexStore`
Simple in-memory Index store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`simple_kvstore` |  `SimpleKVStore` |  simple key-value store |  `None`  
Source code in `llama-index-core/llama_index/core/storage/index_store/simple_index_store.py`

| ```
class SimpleIndexStore(KVIndexStore):
    """
    Simple in-memory Index store.

    Args:
        simple_kvstore (SimpleKVStore): simple key-value store

    """

    def __init__(
        self,
        simple_kvstore: Optional[SimpleKVStore] = None,
    ) -> None:
        """Init a SimpleIndexStore."""
        simple_kvstore = simple_kvstore or SimpleKVStore()
        super().__init__(simple_kvstore)

    @classmethod
    def from_persist_dir(
        cls,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> "SimpleIndexStore":
        """Create a SimpleIndexStore from a persist directory."""
        if fs is not None:
            persist_path = concat_dirs(persist_dir, DEFAULT_PERSIST_FNAME)
        else:
            persist_path = os.path.join(persist_dir, DEFAULT_PERSIST_FNAME)
        return cls.from_persist_path(persist_path, fs=fs)

    @classmethod
    def from_persist_path(
        cls,
        persist_path: str,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> "SimpleIndexStore":
        """Create a SimpleIndexStore from a persist path."""
        fs = fs or fsspec.filesystem("file")
        simple_kvstore = SimpleKVStore.from_persist_path(persist_path, fs=fs)
        return cls(simple_kvstore)

    def persist(
        self,
        persist_path: str = DEFAULT_PERSIST_PATH,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> None:
        """Persist the store."""
        if isinstance(self._kvstore, (MutableMappingKVStore, BaseInMemoryKVStore)):
            self._kvstore.persist(persist_path, fs=fs)

    @classmethod
    def from_dict(cls, save_dict: dict) -> "SimpleIndexStore":
        simple_kvstore = SimpleKVStore.from_dict(save_dict)
        return cls(simple_kvstore)

    def to_dict(self) -> dict:
        assert isinstance(self._kvstore, SimpleKVStore)
        return self._kvstore.to_dict()

```
  
---|---  
###  from_persist_dir `classmethod` #
```
from_persist_dir(persist_dir: str = DEFAULT_PERSIST_DIR, fs: Optional[AbstractFileSystem] = None) -> SimpleIndexStore

```

Create a SimpleIndexStore from a persist directory.
Source code in `llama-index-core/llama_index/core/storage/index_store/simple_index_store.py`

| ```
@classmethod
def from_persist_dir(
    cls,
    persist_dir: str = DEFAULT_PERSIST_DIR,
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> "SimpleIndexStore":
    """Create a SimpleIndexStore from a persist directory."""
    if fs is not None:
        persist_path = concat_dirs(persist_dir, DEFAULT_PERSIST_FNAME)
    else:
        persist_path = os.path.join(persist_dir, DEFAULT_PERSIST_FNAME)
    return cls.from_persist_path(persist_path, fs=fs)

```
  
---|---  
###  from_persist_path `classmethod` #
```
from_persist_path(persist_path: str, fs: Optional[AbstractFileSystem] = None) -> SimpleIndexStore

```

Create a SimpleIndexStore from a persist path.
Source code in `llama-index-core/llama_index/core/storage/index_store/simple_index_store.py`

| ```
@classmethod
def from_persist_path(
    cls,
    persist_path: str,
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> "SimpleIndexStore":
    """Create a SimpleIndexStore from a persist path."""
    fs = fs or fsspec.filesystem("file")
    simple_kvstore = SimpleKVStore.from_persist_path(persist_path, fs=fs)
    return cls(simple_kvstore)

```
  
---|---  
###  persist #
```
persist(persist_path: str = DEFAULT_PERSIST_PATH, fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the store.
Source code in `llama-index-core/llama_index/core/storage/index_store/simple_index_store.py`

| ```
def persist(
    self,
    persist_path: str = DEFAULT_PERSIST_PATH,
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> None:
    """Persist the store."""
    if isinstance(self._kvstore, (MutableMappingKVStore, BaseInMemoryKVStore)):
        self._kvstore.persist(persist_path, fs=fs)

```
  
---|---
