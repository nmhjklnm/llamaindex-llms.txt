# Retriever
Bases: `QueryComponent`
Retriever component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`retriever` |  `BaseRetriever` |  Retriever |  _required_  
Source code in `llama-index-core/llama_index/core/base/base_retriever.py`

| ```
class RetrieverComponent(QueryComponent):
    """Retriever component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    retriever: BaseRetriever = Field(..., description="Retriever")

    def set_callback_manager(self, callback_manager: CallbackManager) -> None:
        """Set callback manager."""
        self.retriever.callback_manager = callback_manager

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        # make sure input is a string
        input["input"] = validate_and_convert_stringable(input["input"])
        return input

    def _run_component(self, **kwargs: Any) -> Any:
        """Run component."""
        output = self.retriever.retrieve(kwargs["input"])
        return {"output": output}

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component."""
        output = await self.retriever.aretrieve(kwargs["input"])
        return {"output": output}

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        return InputKeys.from_keys({"input"})

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
Source code in `llama-index-core/llama_index/core/base/base_retriever.py`

| ```
def set_callback_manager(self, callback_manager: CallbackManager) -> None:
    """Set callback manager."""
    self.retriever.callback_manager = callback_manager

```
  
---|---
