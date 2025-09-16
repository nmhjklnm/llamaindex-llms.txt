# Simple
##  SimpleKVStore #
Bases: `MutableMappingKVStore[dict]`
Simple in-memory Key-Value store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`data` |  `Optional[DATA_TYPE]` |  data to initialize the store with |  `None`  
Source code in `llama-index-core/llama_index/core/storage/kvstore/simple_kvstore.py`

| ```
class SimpleKVStore(MutableMappingKVStore[dict]):
    """
    Simple in-memory Key-Value store.

    Args:
        data (Optional[DATA_TYPE]): data to initialize the store with

    """

    def __init__(
        self,
        data: Optional[DATA_TYPE] = None,
    ) -> None:
        """Init a SimpleKVStore."""
        super().__init__(mapping_factory=dict)

        if data is not None:
            self._collections_mappings = data.copy()

    def persist(
        self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> None:
        """Persist the store."""
        fs = fs or fsspec.filesystem("file")
        dirpath = os.path.dirname(persist_path)
        if not fs.exists(dirpath):
            fs.makedirs(dirpath)

        with fs.open(persist_path, "w") as f:
            f.write(json.dumps(self._collections_mappings))

    @classmethod
    def from_persist_path(
        cls, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> "SimpleKVStore":
        """Load a SimpleKVStore from a persist path and filesystem."""
        fs = fs or fsspec.filesystem("file")
        logger.debug(f"Loading {__name__} from {persist_path}.")
        print(f"Loading {__name__} from {persist_path}.")
        with fs.open(persist_path, "rb") as f:
            data = json.load(f)
        return cls(data)

    def to_dict(self) -> dict:
        """Save the store as dict."""
        return self._collections_mappings.copy()

    @classmethod
    def from_dict(cls, save_dict: dict) -> "SimpleKVStore":
        """Load a SimpleKVStore from dict."""
        return cls(save_dict)

```
  
---|---  
###  persist #
```
persist(persist_path: str, fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the store.
Source code in `llama-index-core/llama_index/core/storage/kvstore/simple_kvstore.py`

| ```
def persist(
    self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
) -> None:
    """Persist the store."""
    fs = fs or fsspec.filesystem("file")
    dirpath = os.path.dirname(persist_path)
    if not fs.exists(dirpath):
        fs.makedirs(dirpath)

    with fs.open(persist_path, "w") as f:
        f.write(json.dumps(self._collections_mappings))

```
  
---|---  
###  from_persist_path `classmethod` #
```
from_persist_path(persist_path: str, fs: Optional[AbstractFileSystem] = None) -> SimpleKVStore

```

Load a SimpleKVStore from a persist path and filesystem.
Source code in `llama-index-core/llama_index/core/storage/kvstore/simple_kvstore.py`

| ```
@classmethod
def from_persist_path(
    cls, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
) -> "SimpleKVStore":
    """Load a SimpleKVStore from a persist path and filesystem."""
    fs = fs or fsspec.filesystem("file")
    logger.debug(f"Loading {__name__} from {persist_path}.")
    print(f"Loading {__name__} from {persist_path}.")
    with fs.open(persist_path, "rb") as f:
        data = json.load(f)
    return cls(data)

```
  
---|---  
###  to_dict #
```
to_dict() -> dict

```

Save the store as dict.
Source code in `llama-index-core/llama_index/core/storage/kvstore/simple_kvstore.py`

| ```
def to_dict(self) -> dict:
    """Save the store as dict."""
    return self._collections_mappings.copy()

```
  
---|---  
###  from_dict `classmethod` #
```
from_dict(save_dict: dict) -> SimpleKVStore

```

Load a SimpleKVStore from dict.
Source code in `llama-index-core/llama_index/core/storage/kvstore/simple_kvstore.py`

| ```
@classmethod
def from_dict(cls, save_dict: dict) -> "SimpleKVStore":
    """Load a SimpleKVStore from dict."""
    return cls(save_dict)

```
  
---|---
