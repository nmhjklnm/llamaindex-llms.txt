# Index
##  AsyncBaseTool #
Bases: `BaseTool`
Base-level tool class that is backwards compatible with the old tool spec but also supports async.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
class AsyncBaseTool(BaseTool):
    """
    Base-level tool class that is backwards compatible with the old tool spec but also
    supports async.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> ToolOutput:
        return self.call(*args, **kwargs)

    @abstractmethod
    def call(self, input: Any) -> ToolOutput:
        """
        This is the method that should be implemented by the tool developer.
        """

    @abstractmethod
    async def acall(self, input: Any) -> ToolOutput:
        """
        This is the async version of the call method.
        Should also be implemented by the tool developer as an
        async-compatible implementation.
        """

```
  
---|---  
###  call `abstractmethod` #
```
call(input: Any) -> ToolOutput

```

This is the method that should be implemented by the tool developer.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
@abstractmethod
def call(self, input: Any) -> ToolOutput:
    """
    This is the method that should be implemented by the tool developer.
    """

```
  
---|---  
###  acall `abstractmethod` `async` #
```
acall(input: Any) -> ToolOutput

```

This is the async version of the call method. Should also be implemented by the tool developer as an async-compatible implementation.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
@abstractmethod
async def acall(self, input: Any) -> ToolOutput:
    """
    This is the async version of the call method.
    Should also be implemented by the tool developer as an
    async-compatible implementation.
    """

```
  
---|---  
##  BaseToolAsyncAdapter #
Bases: `AsyncBaseTool`
Adapter class that allows a synchronous tool to be used as an async tool.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
class BaseToolAsyncAdapter(AsyncBaseTool):
    """
    Adapter class that allows a synchronous tool to be used as an async tool.
    """

    def __init__(self, tool: BaseTool):
        self.base_tool = tool

    @property
    def metadata(self) -> ToolMetadata:
        return self.base_tool.metadata

    def call(self, input: Any) -> ToolOutput:
        return self.base_tool(input)

    async def acall(self, input: Any) -> ToolOutput:
        return await asyncio.to_thread(self.call, input)

```
  
---|---  
##  BaseTool #
Bases: `DispatcherSpanMixin`
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
class BaseTool(DispatcherSpanMixin):
    @property
    @abstractmethod
    def metadata(self) -> ToolMetadata:
        pass

    @abstractmethod
    def __call__(self, input: Any) -> ToolOutput:
        pass

    def _process_langchain_tool_kwargs(
        self,
        langchain_tool_kwargs: Any,
    ) -> Dict[str, Any]:
        """Process langchain tool kwargs."""
        if "name" not in langchain_tool_kwargs:
            langchain_tool_kwargs["name"] = self.metadata.name or ""
        if "description" not in langchain_tool_kwargs:
            langchain_tool_kwargs["description"] = self.metadata.description
        if "fn_schema" not in langchain_tool_kwargs:
            langchain_tool_kwargs["args_schema"] = self.metadata.fn_schema

        # Callback dont exist on langchain
        if "_callback" in langchain_tool_kwargs:
            del langchain_tool_kwargs["_callback"]
        if "_async_callback" in langchain_tool_kwargs:
            del langchain_tool_kwargs["_async_callback"]

        return langchain_tool_kwargs

    def to_langchain_tool(
        self,
        **langchain_tool_kwargs: Any,
    ) -> "Tool":
        """To langchain tool."""
        from llama_index.core.bridge.langchain import Tool

        langchain_tool_kwargs = self._process_langchain_tool_kwargs(
            langchain_tool_kwargs
        )
        return Tool.from_function(
            func=self.__call__,
            **langchain_tool_kwargs,
        )

    def to_langchain_structured_tool(
        self,
        **langchain_tool_kwargs: Any,
    ) -> "StructuredTool":
        """To langchain structured tool."""
        from llama_index.core.bridge.langchain import StructuredTool

        langchain_tool_kwargs = self._process_langchain_tool_kwargs(
            langchain_tool_kwargs
        )
        return StructuredTool.from_function(
            func=self.__call__,
            **langchain_tool_kwargs,
        )

```
  
---|---  
###  to_langchain_tool #
```
to_langchain_tool(**langchain_tool_kwargs: Any) -> Tool

```

To langchain tool.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
def to_langchain_tool(
    self,
    **langchain_tool_kwargs: Any,
) -> "Tool":
    """To langchain tool."""
    from llama_index.core.bridge.langchain import Tool

    langchain_tool_kwargs = self._process_langchain_tool_kwargs(
        langchain_tool_kwargs
    )
    return Tool.from_function(
        func=self.__call__,
        **langchain_tool_kwargs,
    )

```
  
---|---  
###  to_langchain_structured_tool #
```
to_langchain_structured_tool(**langchain_tool_kwargs: Any) -> StructuredTool

```

To langchain structured tool.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
def to_langchain_structured_tool(
    self,
    **langchain_tool_kwargs: Any,
) -> "StructuredTool":
    """To langchain structured tool."""
    from llama_index.core.bridge.langchain import StructuredTool

    langchain_tool_kwargs = self._process_langchain_tool_kwargs(
        langchain_tool_kwargs
    )
    return StructuredTool.from_function(
        func=self.__call__,
        **langchain_tool_kwargs,
    )

```
  
---|---  
##  ToolMetadata `dataclass` #
ToolMetadata(description: str, name: Optional[str] = None, fn_schema: Optional[Type[pydantic.main.BaseModel]] = , return_direct: bool = False)
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`description` |  `str` |  |  _required_  
`name` |  `str | None` |  |  `None`  
`fn_schema` |  `Type[BaseModel] | None` |  |  `<class 'llama_index.core.tools.types.DefaultToolFnSchema'>`  
`return_direct` |  `bool` |  |  `False`  
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
@dataclass
class ToolMetadata:
    description: str
    name: Optional[str] = None
    fn_schema: Optional[Type[BaseModel]] = DefaultToolFnSchema
    return_direct: bool = False

    def get_parameters_dict(self) -> dict:
        if self.fn_schema is None:
            parameters = {
                "type": "object",
                "properties": {
                    "input": {"title": "input query string", "type": "string"},
                },
                "required": ["input"],
            }
        else:
            parameters = self.fn_schema.model_json_schema()
            parameters = {
                k: v
                for k, v in parameters.items()
                if k in ["type", "properties", "required", "definitions", "$defs"]
            }
        return parameters

    @property
    def fn_schema_str(self) -> str:
        """Get fn schema as string."""
        if self.fn_schema is None:
            raise ValueError("fn_schema is None.")
        parameters = self.get_parameters_dict()
        return json.dumps(parameters, ensure_ascii=False)

    def get_name(self) -> str:
        """Get name."""
        if self.name is None:
            raise ValueError("name is None.")
        return self.name

    @deprecated(
        "Deprecated in favor of `to_openai_tool`, which should be used instead."
    )
    def to_openai_function(self) -> Dict[str, Any]:
        """
        Deprecated and replaced by `to_openai_tool`.
        The name and arguments of a function that should be called, as generated by the
        model.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters_dict(),
        }

    def to_openai_tool(self, skip_length_check: bool = False) -> Dict[str, Any]:
        """To OpenAI tool."""
        if not skip_length_check and len(self.description) > 1024:
            raise ValueError(
                "Tool description exceeds maximum length of 1024 characters. "
                "Please shorten your description or move it to the prompt."
            )
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.get_parameters_dict(),
            },
        }

```
  
---|---  
###  fn_schema_str `property` #
```
fn_schema_str: str

```

Get fn schema as string.
###  get_name #
```
get_name() -> str

```

Get name.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
def get_name(self) -> str:
    """Get name."""
    if self.name is None:
        raise ValueError("name is None.")
    return self.name

```
  
---|---  
###  to_openai_function #
```
to_openai_function() -> Dict[str, Any]

```

Deprecated and replaced by `to_openai_tool`. The name and arguments of a function that should be called, as generated by the model.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
@deprecated(
    "Deprecated in favor of `to_openai_tool`, which should be used instead."
)
def to_openai_function(self) -> Dict[str, Any]:
    """
    Deprecated and replaced by `to_openai_tool`.
    The name and arguments of a function that should be called, as generated by the
    model.
    """
    return {
        "name": self.name,
        "description": self.description,
        "parameters": self.get_parameters_dict(),
    }

```
  
---|---  
###  to_openai_tool #
```
to_openai_tool(skip_length_check: bool = False) -> Dict[str, Any]

```

To OpenAI tool.
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
def to_openai_tool(self, skip_length_check: bool = False) -> Dict[str, Any]:
    """To OpenAI tool."""
    if not skip_length_check and len(self.description) > 1024:
        raise ValueError(
            "Tool description exceeds maximum length of 1024 characters. "
            "Please shorten your description or move it to the prompt."
        )
    return {
        "type": "function",
        "function": {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters_dict(),
        },
    }

```
  
---|---  
##  ToolOutput #
Bases: `BaseModel`
Tool output.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`content` |  `str` |  |  _required_  
`tool_name` |  `str` |  |  _required_  
`raw_input` |  `Dict[str, Any]` |  |  _required_  
`raw_output` |  `Any` |  |  _required_  
`is_error` |  `bool` |  |  `False`  
Source code in `llama-index-core/llama_index/core/tools/types.py`

| ```
class ToolOutput(BaseModel):
    """Tool output."""

    content: str
    tool_name: str
    raw_input: Dict[str, Any]
    raw_output: Any
    is_error: bool = False

    def __str__(self) -> str:
        """String."""
        return str(self.content)

```
  
---|---
