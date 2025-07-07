# Query transform
Bases: `QueryComponent`
Query transform component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_transform` |  `BaseQueryTransform` |  Query transform. |  _required_  
Source code in `llama-index-core/llama_index/core/indices/query/query_transform/base.py`

| ```
class QueryTransformComponent(QueryComponent):
    """Query transform component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    query_transform: BaseQueryTransform = Field(..., description="Query transform.")

    def set_callback_manager(self, callback_manager: Any) -> None:
        """Set callback manager."""
        # TODO: not implemented yet

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        if "query_str" not in input:
            raise ValueError("Input must have key 'query_str'")
        input["query_str"] = validate_and_convert_stringable(input["query_str"])

        input["metadata"] = input.get("metadata", {})

        return input

    def _run_component(self, **kwargs: Any) -> Any:
        """Run component."""
        output = self.query_transform.run(
            kwargs["query_str"],
            metadata=kwargs["metadata"],
        )
        return {"query_str": output.query_str}

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component."""
        # TODO: true async not implemented yet
        return self._run_component(**kwargs)

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        return InputKeys.from_keys({"query_str"}, optional_keys={"metadata"})

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        return OutputKeys.from_keys({"query_str"})

```
  
---|---  
##  input_keys `property` #
```
input_keys: InputKeys

```

Input keys.
##  output_keys `property` #
```
output_keys: OutputKeys

```

Output keys.
##  set_callback_manager #
```
set_callback_manager(callback_manager: Any) -> None

```

Set callback manager.
Source code in `llama-index-core/llama_index/core/indices/query/query_transform/base.py`

| ```
def set_callback_manager(self, callback_manager: Any) -> None:
    """Set callback manager."""

```
  
---|---
