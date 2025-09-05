# Output parser
Bases: `QueryComponent`
Output parser component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`output_parser` |  `BaseOutputParser` |  Output parser. |  _required_  
Source code in `llama-index-core/llama_index/core/output_parsers/base.py`

| ```
class OutputParserComponent(QueryComponent):
    """Output parser component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    output_parser: BaseOutputParser = Field(..., description="Output parser.")

    def _run_component(self, **kwargs: Any) -> Dict[str, Any]:
        """Run component."""
        output = self.output_parser.parse(kwargs["input"])
        return {"output": output}

    async def _arun_component(self, **kwargs: Any) -> Dict[str, Any]:
        """Run component."""
        # NOTE: no native async for output parser
        return self._run_component(**kwargs)

    def _validate_component_inputs(self, input: Any) -> Any:
        """Validate component inputs during run_component."""
        input["input"] = validate_and_convert_stringable(input["input"])
        return input

    def set_callback_manager(self, callback_manager: Any) -> None:
        """Set callback manager."""

    @property
    def input_keys(self) -> Any:
        """Input keys."""
        return InputKeys.from_keys({"input"})

    @property
    def output_keys(self) -> Any:
        """Output keys."""
        return OutputKeys.from_keys({"output"})

```
  
---|---  
##  input_keys `property` #
```
input_keys: Any

```

Input keys.
##  output_keys `property` #
```
output_keys: Any

```

Output keys.
##  set_callback_manager #
```
set_callback_manager(callback_manager: Any) -> None

```

Set callback manager.
Source code in `llama-index-core/llama_index/core/output_parsers/base.py`

| ```
def set_callback_manager(self, callback_manager: Any) -> None:
    """Set callback manager."""

```
  
---|---
