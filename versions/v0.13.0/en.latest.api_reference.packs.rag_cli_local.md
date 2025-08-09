# Rag cli local
##  LocalRAGCLIPack #
Bases: `BaseLlamaPack`
Local RAG CLI Pack.
Source code in `llama-index-packs/llama-index-packs-rag-cli-local/llama_index/packs/rag_cli_local/base.py`

| ```
class LocalRAGCLIPack(BaseLlamaPack):
    """Local RAG CLI Pack."""

    def __init__(
        self,
        verbose: bool = False,
        persist_dir: Optional[str] = None,
        llm_model_name: str = "mistral",
        embed_model_name: str = "BAAI/bge-m3",
    ) -> None:
        """Init params."""
        self.verbose = verbose
        self.persist_dir = persist_dir or default_ragcli_persist_dir()
        self.llm_model_name = llm_model_name
        self.embed_model_name = embed_model_name
        self.rag_cli = init_local_rag_cli(
            persist_dir=self.persist_dir,
            verbose=self.verbose,
            llm_model_name=self.llm_model_name,
            embed_model_name=self.embed_model_name,
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {"rag_cli": self.rag_cli}

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.rag_cli.cli(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-rag-cli-local/llama_index/packs/rag_cli_local/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {"rag_cli": self.rag_cli}

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-rag-cli-local/llama_index/packs/rag_cli_local/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.rag_cli.cli(*args, **kwargs)

```
  
---|---
