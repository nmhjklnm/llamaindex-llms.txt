# Multi modal
Bases: `QueryComponent`
Base LLM component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`multi_modal_llm` |  `MultiModalLLM` |  LLM |  _required_  
`streaming` |  `bool` |  Streaming mode |  `False`  
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
class BaseMultiModalComponent(QueryComponent):
    """Base LLM component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    multi_modal_llm: MultiModalLLM = Field(..., description="LLM")
    streaming: bool = Field(default=False, description="Streaming mode")

    def set_callback_manager(self, callback_manager: Any) -> None:
        """Set callback manager."""

```
  
---|---  
##  set_callback_manager #
```
set_callback_manager(callback_manager: Any) -> None

```

Set callback manager.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
def set_callback_manager(self, callback_manager: Any) -> None:
    """Set callback manager."""

```
  
---|---
