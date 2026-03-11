# Index
Base reader class.
##  BaseReader #
Bases: `ABC`
Utilities for loading data from a directory.
Source code in `llama-index-core/llama_index/core/readers/base.py`

| ```
class BaseReader(ABC):  # pragma: no cover
    """Utilities for loading data from a directory."""

    def lazy_load_data(self, *args: Any, **load_kwargs: Any) -> Iterable[Document]:
        """Load data from the input directory lazily."""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not provide lazy_load_data method currently"
        )

    async def alazy_load_data(
        self, *args: Any, **load_kwargs: Any
    ) -> Iterable[Document]:
        """Load data from the input directory lazily."""
        # Threaded async - just calls the sync method with to_thread. Override in subclasses for real async implementations.
        return await asyncio.to_thread(self.lazy_load_data, *args, **load_kwargs)

    def load_data(self, *args: Any, **load_kwargs: Any) -> List[Document]:
        """Load data from the input directory."""
        return list(self.lazy_load_data(*args, **load_kwargs))

    async def aload_data(self, *args: Any, **load_kwargs: Any) -> List[Document]:
        """Load data from the input directory."""
        return await asyncio.to_thread(self.load_data, *args, **load_kwargs)

    def load_langchain_documents(self, **load_kwargs: Any) -> List["LCDocument"]:
        """Load data in LangChain document format."""
        docs = self.load_data(**load_kwargs)
        return [d.to_langchain_format() for d in docs]

```
  
---|---  
###  lazy_load_data #
```
lazy_load_data(*args: Any, **load_kwargs: Any) -> Iterable[Document]

```

Load data from the input directory lazily.
Source code in `llama-index-core/llama_index/core/readers/base.py`

| ```
def lazy_load_data(self, *args: Any, **load_kwargs: Any) -> Iterable[Document]:
    """Load data from the input directory lazily."""
    raise NotImplementedError(
        f"{self.__class__.__name__} does not provide lazy_load_data method currently"
    )

```
  
---|---  
###  alazy_load_data `async` #
```
alazy_load_data(*args: Any, **load_kwargs: Any) -> Iterable[Document]

```

Load data from the input directory lazily.
Source code in `llama-index-core/llama_index/core/readers/base.py`

| ```
async def alazy_load_data(
    self, *args: Any, **load_kwargs: Any
) -> Iterable[Document]:
    """Load data from the input directory lazily."""
    # Threaded async - just calls the sync method with to_thread. Override in subclasses for real async implementations.
    return await asyncio.to_thread(self.lazy_load_data, *args, **load_kwargs)

```
  
---|---  
###  load_data #
```
load_data(*args: Any, **load_kwargs: Any) -> List[Document]

```

Load data from the input directory.
Source code in `llama-index-core/llama_index/core/readers/base.py`

| ```
def load_data(self, *args: Any, **load_kwargs: Any) -> List[Document]:
    """Load data from the input directory."""
    return list(self.lazy_load_data(*args, **load_kwargs))

```
  
---|---  
###  aload_data `async` #
```
aload_data(*args: Any, **load_kwargs: Any) -> List[Document]

```

Load data from the input directory.
Source code in `llama-index-core/llama_index/core/readers/base.py`

| ```
async def aload_data(self, *args: Any, **load_kwargs: Any) -> List[Document]:
    """Load data from the input directory."""
    return await asyncio.to_thread(self.load_data, *args, **load_kwargs)

```
  
---|---  
###  load_langchain_documents #
```
load_langchain_documents(**load_kwargs: Any) -> List[Document]

```

Load data in LangChain document format.
Source code in `llama-index-core/llama_index/core/readers/base.py`

| ```
def load_langchain_documents(self, **load_kwargs: Any) -> List["LCDocument"]:
    """Load data in LangChain document format."""
    docs = self.load_data(**load_kwargs)
    return [d.to_langchain_format() for d in docs]

```
  
---|---  
##  BasePydanticReader #
Bases: `BaseReader`, `BaseComponent`
Serialiable Data Loader with Pydantic.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`is_remote` |  `bool` |  Whether the data is loaded from a remote API or a local file. |  `False`  
Source code in `llama-index-core/llama_index/core/readers/base.py`

| ```
class BasePydanticReader(BaseReader, BaseComponent):
    """Serialiable Data Loader with Pydantic."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    is_remote: bool = Field(
        default=False,
        description="Whether the data is loaded from a remote API or a local file.",
    )

```
  
---|---
