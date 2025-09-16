# Opik
##  opik_callback_handler #
```
opik_callback_handler(**eval_params: Any) -> BaseCallbackHandler

```

Source code in `llama-index-integrations/callbacks/llama-index-callbacks-opik/llama_index/callbacks/opik/base.py`

| ```
def opik_callback_handler(**eval_params: Any) -> BaseCallbackHandler:
    try:
        from opik.integrations.llama_index import LlamaIndexCallbackHandler

        return LlamaIndexCallbackHandler(**eval_params)

    except ImportError:
        raise ImportError(
            "Please install the Opik Python SDK with `pip install -U opik`"
        )

```
  
---|---
