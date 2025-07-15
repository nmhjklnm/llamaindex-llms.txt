# Simple
Simple graph store index.
##  SimpleGraphStore #
Bases: `GraphStore`
Simple Graph Store.
In this graph store, triplets are stored within a simple, in-memory dictionary.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`simple_graph_store_data_dict` |  `Optional[dict]` |  data dict containing the triplets. See SimpleGraphStoreData for more details. |  _required_  
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
class SimpleGraphStore(GraphStore):
    """
    Simple Graph Store.

    In this graph store, triplets are stored within a simple, in-memory dictionary.

    Args:
        simple_graph_store_data_dict (Optional[dict]): data dict
            containing the triplets. See SimpleGraphStoreData
            for more details.

    """

    def __init__(
        self,
        data: Optional[SimpleGraphStoreData] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        self._data = data or SimpleGraphStoreData()
        self._fs = fs or fsspec.filesystem("file")

    @classmethod
    def from_persist_dir(
        cls,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> "SimpleGraphStore":
        """Load from persist dir."""
        persist_path = os.path.join(persist_dir, DEFAULT_PERSIST_FNAME)
        return cls.from_persist_path(persist_path, fs=fs)

    @property
    def client(self) -> None:
        """
        Get client.
        Not applicable for this store.
        """
        return

    def get(self, subj: str) -> List[List[str]]:
        """Get triplets."""
        return self._data.graph_dict.get(subj, [])

    def get_rel_map(
        self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
    ) -> Dict[str, List[List[str]]]:
        """Get depth-aware rel map."""
        return self._data.get_rel_map(subjs=subjs, depth=depth, limit=limit)

    def upsert_triplet(self, subj: str, rel: str, obj: str) -> None:
        """Add triplet."""
        if subj not in self._data.graph_dict:
            self._data.graph_dict[subj] = []
        existing = self._data.graph_dict[subj]
        if (rel, obj) not in map(tuple, existing):
            existing.append([rel, obj])

    def delete(self, subj: str, rel: str, obj: str) -> None:
        """Delete triplet."""
        if subj in self._data.graph_dict:
            if (rel, obj) in self._data.graph_dict[subj]:
                self._data.graph_dict[subj].remove([rel, obj])
                if len(self._data.graph_dict[subj]) == 0:
                    del self._data.graph_dict[subj]

    def persist(
        self,
        persist_path: str = os.path.join(DEFAULT_PERSIST_DIR, DEFAULT_PERSIST_FNAME),
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> None:
        """Persist the SimpleGraphStore to a directory."""
        fs = fs or self._fs
        dirpath = os.path.dirname(persist_path)
        if not fs.exists(dirpath):
            fs.makedirs(dirpath)

        with fs.open(persist_path, "w") as f:
            json.dump(self._data.to_dict(), f)

    def get_schema(self, refresh: bool = False) -> str:
        """Get the schema of the Simple Graph store."""
        raise NotImplementedError("SimpleGraphStore does not support get_schema")

    def query(self, query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any:
        """Query the Simple Graph store."""
        raise NotImplementedError("SimpleGraphStore does not support query")

    @classmethod
    def from_persist_path(
        cls, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> "SimpleGraphStore":
        """Create a SimpleGraphStore from a persist directory."""
        fs = fs or fsspec.filesystem("file")
        if not fs.exists(persist_path):
            logger.warning(
                f"No existing {__name__} found at {persist_path}. "
                "Initializing a new graph_store from scratch. "
            )
            return cls()

        logger.debug(f"Loading {__name__} from {persist_path}.")
        with fs.open(persist_path, "rb") as f:
            data_dict = json.load(f)
            data = SimpleGraphStoreData.from_dict(data_dict)
        return cls(data)

    @classmethod
    def from_dict(cls, save_dict: dict) -> "SimpleGraphStore":
        data = SimpleGraphStoreData.from_dict(save_dict)
        return cls(data)

    def to_dict(self) -> dict:
        return self._data.to_dict()

```
  
---|---  
###  client `property` #
```
client: None

```

Get client. Not applicable for this store.
###  from_persist_dir `classmethod` #
```
from_persist_dir(persist_dir: str = DEFAULT_PERSIST_DIR, fs: Optional[AbstractFileSystem] = None) -> SimpleGraphStore

```

Load from persist dir.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
@classmethod
def from_persist_dir(
    cls,
    persist_dir: str = DEFAULT_PERSIST_DIR,
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> "SimpleGraphStore":
    """Load from persist dir."""
    persist_path = os.path.join(persist_dir, DEFAULT_PERSIST_FNAME)
    return cls.from_persist_path(persist_path, fs=fs)

```
  
---|---  
###  get #
```
get(subj: str) -> List[List[str]]

```

Get triplets.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
def get(self, subj: str) -> List[List[str]]:
    """Get triplets."""
    return self._data.graph_dict.get(subj, [])

```
  
---|---  
###  get_rel_map #
```
get_rel_map(subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30) -> Dict[str, List[List[str]]]

```

Get depth-aware rel map.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
def get_rel_map(
    self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
) -> Dict[str, List[List[str]]]:
    """Get depth-aware rel map."""
    return self._data.get_rel_map(subjs=subjs, depth=depth, limit=limit)

```
  
---|---  
###  upsert_triplet #
```
upsert_triplet(subj: str, rel: str, obj: str) -> None

```

Add triplet.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
def upsert_triplet(self, subj: str, rel: str, obj: str) -> None:
    """Add triplet."""
    if subj not in self._data.graph_dict:
        self._data.graph_dict[subj] = []
    existing = self._data.graph_dict[subj]
    if (rel, obj) not in map(tuple, existing):
        existing.append([rel, obj])

```
  
---|---  
###  delete #
```
delete(subj: str, rel: str, obj: str) -> None

```

Delete triplet.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
def delete(self, subj: str, rel: str, obj: str) -> None:
    """Delete triplet."""
    if subj in self._data.graph_dict:
        if (rel, obj) in self._data.graph_dict[subj]:
            self._data.graph_dict[subj].remove([rel, obj])
            if len(self._data.graph_dict[subj]) == 0:
                del self._data.graph_dict[subj]

```
  
---|---  
###  persist #
```
persist(persist_path: str = join(DEFAULT_PERSIST_DIR, DEFAULT_PERSIST_FNAME), fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the SimpleGraphStore to a directory.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
def persist(
    self,
    persist_path: str = os.path.join(DEFAULT_PERSIST_DIR, DEFAULT_PERSIST_FNAME),
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> None:
    """Persist the SimpleGraphStore to a directory."""
    fs = fs or self._fs
    dirpath = os.path.dirname(persist_path)
    if not fs.exists(dirpath):
        fs.makedirs(dirpath)

    with fs.open(persist_path, "w") as f:
        json.dump(self._data.to_dict(), f)

```
  
---|---  
###  get_schema #
```
get_schema(refresh: bool = False) -> str

```

Get the schema of the Simple Graph store.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
def get_schema(self, refresh: bool = False) -> str:
    """Get the schema of the Simple Graph store."""
    raise NotImplementedError("SimpleGraphStore does not support get_schema")

```
  
---|---  
###  query #
```
query(query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any

```

Query the Simple Graph store.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
def query(self, query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any:
    """Query the Simple Graph store."""
    raise NotImplementedError("SimpleGraphStore does not support query")

```
  
---|---  
###  from_persist_path `classmethod` #
```
from_persist_path(persist_path: str, fs: Optional[AbstractFileSystem] = None) -> SimpleGraphStore

```

Create a SimpleGraphStore from a persist directory.
Source code in `llama-index-core/llama_index/core/graph_stores/simple.py`

| ```
@classmethod
def from_persist_path(
    cls, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
) -> "SimpleGraphStore":
    """Create a SimpleGraphStore from a persist directory."""
    fs = fs or fsspec.filesystem("file")
    if not fs.exists(persist_path):
        logger.warning(
            f"No existing {__name__} found at {persist_path}. "
            "Initializing a new graph_store from scratch. "
        )
        return cls()

    logger.debug(f"Loading {__name__} from {persist_path}.")
    with fs.open(persist_path, "rb") as f:
        data_dict = json.load(f)
        data = SimpleGraphStoreData.from_dict(data_dict)
    return cls(data)

```
  
---|---
