# JSONalayze
##  JSONalyzeQueryEngine #
JSONalyze query engine.
DEPRECATED: Use `JSONalyzeQueryEngine` from `llama-index-experimental` instead.
Source code in `llama-index-core/llama_index/core/query_engine/jsonalyze/jsonalyze_query_engine.py`

| ```
class JSONalyzeQueryEngine:
    """
    JSONalyze query engine.

    DEPRECATED: Use `JSONalyzeQueryEngine` from `llama-index-experimental` instead.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        raise DeprecationWarning(
            "JSONalyzeQueryEngine has been moved to `llama-index-experimental`.\n"
            "`pip install llama-index-experimental`\n"
            "`from llama_index.experimental.query_engine import JSONalyzeQueryEngine`\n"
            "Note that the JSONalyzeQueryEngine allows for arbitrary file creation, \n"
            "and should be used in a secure environment."
        )

```
  
---|---
