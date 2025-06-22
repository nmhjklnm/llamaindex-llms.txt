# Langfuse
##  langfuse_callback_handler #
```
langfuse_callback_handler(**eval_params: Any) -> BaseCallbackHandler

```

Source code in `llama-index-integrations/callbacks/llama-index-callbacks-langfuse/llama_index/callbacks/langfuse/base.py`

| ```
def langfuse_callback_handler(**eval_params: Any) -> BaseCallbackHandler:
    return LlamaIndexCallbackHandler(
        **eval_params, sdk_integration="llama-index_set-global-handler"
    )

```
  
---|---
