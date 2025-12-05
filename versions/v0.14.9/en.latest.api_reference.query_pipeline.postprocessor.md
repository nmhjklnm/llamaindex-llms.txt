# Postprocessor
Bases: `QueryComponent`
Postprocessor component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`postprocessor` |  `BaseNodePostprocessor` |  Postprocessor |  _required_  
Source code in `llama-index-core/llama_index/core/postprocessor/types.py`

| ```
class PostprocessorComponent(QueryComponent):
    """Postprocessor component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    postprocessor: SerializeAsAny[BaseNodePostprocessor] = Field(
        ..., description="Postprocessor"
    )

    def set_callback_manager(self, callback_manager: CallbackManager) -> None:
        """Set callback manager."""
        self.postprocessor.callback_manager = callback_manager

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        # make sure `nodes` is a list of nodes
        if "nodes" not in input:
            raise ValueError("Input must have key 'nodes'")
        nodes = input["nodes"]
        if not isinstance(nodes, list):
            raise ValueError("Input nodes must be a list")
        for node in nodes:
            if not isinstance(node, NodeWithScore):
                raise ValueError("Input nodes must be a list of NodeWithScore")

        # if query_str exists, make sure `query_str` is stringable
        if "query_str" in input:
            input["query_str"] = validate_and_convert_stringable(input["query_str"])

        return input

    def _run_component(self, **kwargs: Any) -> Any:
        """Run component."""
        output = self.postprocessor.postprocess_nodes(
            kwargs["nodes"], query_str=kwargs.get("query_str")
        )
        return {"nodes": output}

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component (async)."""
        # NOTE: no native async for postprocessor
        return self._run_component(**kwargs)

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        return InputKeys.from_keys({"nodes"}, optional_keys={"query_str"})

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        return OutputKeys.from_keys({"nodes"})

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
set_callback_manager(callback_manager: CallbackManager) -> None

```

Set callback manager.
Source code in `llama-index-core/llama_index/core/postprocessor/types.py`

| ```
def set_callback_manager(self, callback_manager: CallbackManager) -> None:
    """Set callback manager."""
    self.postprocessor.callback_manager = callback_manager

```
  
---|---
