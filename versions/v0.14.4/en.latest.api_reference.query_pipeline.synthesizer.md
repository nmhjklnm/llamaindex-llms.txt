# Synthesizer
Bases: `QueryComponent`
Synthesizer component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`synthesizer` |  `BaseSynthesizer` |  Synthesizer |  _required_  
Source code in `llama-index-core/llama_index/core/response_synthesizers/base.py`

| ```
class SynthesizerComponent(QueryComponent):
    """Synthesizer component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    synthesizer: BaseSynthesizer = Field(..., description="Synthesizer")

    def set_callback_manager(self, callback_manager: CallbackManager) -> None:
        """Set callback manager."""
        self.synthesizer.callback_manager = callback_manager

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        # make sure both query_str and nodes are there
        if "query_str" not in input:
            raise ValueError("Input must have key 'query_str'")
        input["query_str"] = validate_and_convert_stringable(input["query_str"])

        if "nodes" not in input:
            raise ValueError("Input must have key 'nodes'")
        nodes = input["nodes"]
        if not isinstance(nodes, list):
            raise ValueError("Input nodes must be a list")
        for node in nodes:
            if not isinstance(node, NodeWithScore):
                raise ValueError("Input nodes must be a list of NodeWithScore")
        return input

    def _run_component(self, **kwargs: Any) -> Dict[str, Any]:
        """Run component."""
        output = self.synthesizer.synthesize(kwargs["query_str"], kwargs["nodes"])
        return {"output": output}

    async def _arun_component(self, **kwargs: Any) -> Dict[str, Any]:
        """Run component."""
        output = await self.synthesizer.asynthesize(
            kwargs["query_str"], kwargs["nodes"]
        )
        return {"output": output}

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        return InputKeys.from_keys({"query_str", "nodes"})

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        return OutputKeys.from_keys({"output"})

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
Source code in `llama-index-core/llama_index/core/response_synthesizers/base.py`

| ```
def set_callback_manager(self, callback_manager: CallbackManager) -> None:
    """Set callback manager."""
    self.synthesizer.callback_manager = callback_manager

```
  
---|---
