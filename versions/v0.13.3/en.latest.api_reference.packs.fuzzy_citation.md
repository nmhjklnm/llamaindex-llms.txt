# Fuzzy citation
##  FuzzyCitationEnginePack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-fuzzy-citation/llama_index/packs/fuzzy_citation/base.py`

| ```
class FuzzyCitationEnginePack(BaseLlamaPack):
    def __init__(
        self, query_engine: BaseQueryEngine, threshold: int = DEFAULT_THRESHOLD
    ) -> None:
        """Init params."""
        try:
            from thefuzz import fuzz  # noqa: F401
        except ImportError:
            raise ImportError(
                "Please run `pip install thefuzz` to use the fuzzy citation engine."
            )

        self.query_engine = FuzzyCitationQueryEngine(
            query_engine=query_engine, threshold=threshold
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "query_engine": self.query_engine,
            "query_engine_cls": FuzzyCitationQueryEngine,
        }

    def run(self, query_str: str, **kwargs: Any) -> RESPONSE_TYPE:
        """Run the pipeline."""
        return self.query_engine.query(query_str)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-fuzzy-citation/llama_index/packs/fuzzy_citation/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "query_engine": self.query_engine,
        "query_engine_cls": FuzzyCitationQueryEngine,
    }

```
  
---|---  
###  run #
```
run(query_str: str, **kwargs: Any) -> RESPONSE_TYPE

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-fuzzy-citation/llama_index/packs/fuzzy_citation/base.py`

| ```
def run(self, query_str: str, **kwargs: Any) -> RESPONSE_TYPE:
    """Run the pipeline."""
    return self.query_engine.query(query_str)

```
  
---|---
