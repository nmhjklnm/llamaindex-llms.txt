# Custom
Bases: `QueryComponent`
Custom query component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`callback_manager` |  `CallbackManager` |  Callback manager |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/base/query_pipeline/query.py`

| ```
class CustomQueryComponent(QueryComponent):
    """Custom query component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    callback_manager: CallbackManager = Field(
        default_factory=CallbackManager, description="Callback manager"
    )

    def set_callback_manager(self, callback_manager: CallbackManager) -> None:
        """Set callback manager."""
        self.callback_manager = callback_manager

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        # NOTE: user can override this method to validate inputs
        # but we do this by default for convenience
        return input

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component (async)."""
        raise NotImplementedError("This component does not support async run.")

    @property
    def _input_keys(self) -> Set[str]:
        """Input keys dict."""
        raise NotImplementedError("Not implemented yet. Please override this method.")

    @property
    def _optional_input_keys(self) -> Set[str]:
        """Optional input keys dict."""
        return set()

    @property
    def _output_keys(self) -> Set[str]:
        """Output keys dict."""
        raise NotImplementedError("Not implemented yet. Please override this method.")

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        # NOTE: user can override this too, but we have them implement an
        # abstract method to make sure they do it

        return InputKeys.from_keys(
            required_keys=self._input_keys, optional_keys=self._optional_input_keys
        )

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        # NOTE: user can override this too, but we have them implement an
        # abstract method to make sure they do it
        return OutputKeys.from_keys(self._output_keys)

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
Source code in `llama-index-core/llama_index/core/base/query_pipeline/query.py`

| ```
def set_callback_manager(self, callback_manager: CallbackManager) -> None:
    """Set callback manager."""
    self.callback_manager = callback_manager

```
  
---|---
