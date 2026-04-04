# Self rag
##  SelfRAGPack #
Bases: `BaseLlamaPack`
Simple short form Self-RAG pack.
Source code in `llama-index-packs/llama-index-packs-self-rag/llama_index/packs/self_rag/base.py`

| ```
class SelfRAGPack(BaseLlamaPack):
    """Simple short form Self-RAG pack."""

    def __init__(
        self,
        model_path: str,
        retriever: BaseRetriever,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        self.query_engine = SelfRAGQueryEngine(model_path, retriever, verbose)

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "query_engine": self.query_engine,
            "llm": self.query_engine.llm,
            "retriever": self.query_engine.retriever,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.query_engine.query(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-self-rag/llama_index/packs/self_rag/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "query_engine": self.query_engine,
        "llm": self.query_engine.llm,
        "retriever": self.query_engine.retriever,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-self-rag/llama_index/packs/self_rag/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
