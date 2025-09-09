# Input
Bases: `QueryComponent`
Input component.
Source code in `llama-index-core/llama_index/core/query_pipeline/components/input.py`

| ```
class InputComponent(QueryComponent):
    """Input component."""

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        return input

    def _validate_component_outputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        return input

    def validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs."""
        # NOTE: we override this to do nothing
        return input

    def validate_component_outputs(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component outputs."""
        # NOTE: we override this to do nothing
        return output

    def set_callback_manager(self, callback_manager: Any) -> None:
        """Set callback manager."""

    def _run_component(self, **kwargs: Any) -> Any:
        """Run component."""
        return kwargs

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component (async)."""
        return self._run_component(**kwargs)

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        # NOTE: this shouldn't be used
        return InputKeys.from_keys(set(), optional_keys=set())
        # return InputComponentKeys.from_keys(set(), optional_keys=set())

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        return OutputKeys.from_keys(set())

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
##  validate_component_inputs #
```
validate_component_inputs(input: Dict[str, Any]) -> Dict[str, Any]

```

Validate component inputs.
Source code in `llama-index-core/llama_index/core/query_pipeline/components/input.py`

| ```
def validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
    """Validate component inputs."""
    # NOTE: we override this to do nothing
    return input

```
  
---|---  
##  validate_component_outputs #
```
validate_component_outputs(output: Dict[str, Any]) -> Dict[str, Any]

```

Validate component outputs.
Source code in `llama-index-core/llama_index/core/query_pipeline/components/input.py`

| ```
def validate_component_outputs(self, output: Dict[str, Any]) -> Dict[str, Any]:
    """Validate component outputs."""
    # NOTE: we override this to do nothing
    return output

```
  
---|---  
##  set_callback_manager #
```
set_callback_manager(callback_manager: Any) -> None

```

Set callback manager.
Source code in `llama-index-core/llama_index/core/query_pipeline/components/input.py`

| ```
def set_callback_manager(self, callback_manager: Any) -> None:
    """Set callback manager."""

```
  
---|---
