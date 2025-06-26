# Index
##  BaseIndexStore #
Bases: `ABC`
Source code in `llama-index-core/llama_index/core/storage/index_store/types.py`

| ```
class BaseIndexStore(ABC):
    @abstractmethod
    def index_structs(self) -> List[IndexStruct]:
        pass

    @abstractmethod
    async def async_index_structs(self) -> List[IndexStruct]:
        pass

    @abstractmethod
    def add_index_struct(self, index_struct: IndexStruct) -> None:
        pass

    @abstractmethod
    async def async_add_index_struct(self, index_struct: IndexStruct) -> None:
        pass

    @abstractmethod
    def delete_index_struct(self, key: str) -> None:
        pass

    @abstractmethod
    async def adelete_index_struct(self, key: str) -> None:
        pass

    @abstractmethod
    def get_index_struct(
        self, struct_id: Optional[str] = None
    ) -> Optional[IndexStruct]:
        pass

    @abstractmethod
    async def aget_index_struct(
        self, struct_id: Optional[str] = None
    ) -> Optional[IndexStruct]:
        pass

    def persist(
        self,
        persist_path: str = DEFAULT_PERSIST_PATH,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> None:
        """Persist the index store to disk."""

```
  
---|---  
###  persist #
```
persist(persist_path: str = DEFAULT_PERSIST_PATH, fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the index store to disk.
Source code in `llama-index-core/llama_index/core/storage/index_store/types.py`

| ```
def persist(
    self,
    persist_path: str = DEFAULT_PERSIST_PATH,
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> None:
    """Persist the index store to disk."""

```
  
---|---
