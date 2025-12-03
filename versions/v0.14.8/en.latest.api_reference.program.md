# Index
##  BasePydanticProgram #
Bases: `DispatcherSpanMixin`, `ABC`, `Generic[Model]`
A base class for LLM-powered function that return a pydantic model.
Note: this interface is not yet stable.
Source code in `llama-index-core/llama_index/core/types.py`

| ```
class BasePydanticProgram(DispatcherSpanMixin, ABC, Generic[Model]):
    """
    A base class for LLM-powered function that return a pydantic model.

    Note: this interface is not yet stable.
    """

    @property
    @abstractmethod
    def output_cls(self) -> Type[Model]:
        pass

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> Union[Model, List[Model]]:
        pass

    async def acall(self, *args: Any, **kwargs: Any) -> Union[Model, List[Model]]:
        return self(*args, **kwargs)

    def stream_call(
        self, *args: Any, **kwargs: Any
    ) -> Generator[
        Union[Model, List[Model], "FlexibleModel", List["FlexibleModel"]], None, None
    ]:
        raise NotImplementedError("stream_call is not supported by default.")

    async def astream_call(
        self, *args: Any, **kwargs: Any
    ) -> AsyncGenerator[
        Union[Model, List[Model], "FlexibleModel", List["FlexibleModel"]], None
    ]:
        raise NotImplementedError("astream_call is not supported by default.")

```
  
---|---
