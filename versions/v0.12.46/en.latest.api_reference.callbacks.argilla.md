# Argilla
##  argilla_callback_handler #
```
argilla_callback_handler(**kwargs: Any) -> BaseCallbackHandler

```

Source code in `llama-index-integrations/callbacks/llama-index-callbacks-argilla/llama_index/callbacks/argilla/base.py`

| ```
def argilla_callback_handler(**kwargs: Any) -> BaseCallbackHandler:
    try:
        # lazy import
        from argilla_llama_index import ArgillaCallbackHandler
    except ImportError:
        raise ImportError("Please install Argilla with `pip install argilla`")
    return ArgillaCallbackHandler(**kwargs)

```
  
---|---
