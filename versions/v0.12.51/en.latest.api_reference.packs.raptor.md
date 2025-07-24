# Raptor
##  RaptorPack #
Bases: `BaseLlamaPack`
Raptor pack.
Source code in `llama-index-packs/llama-index-packs-raptor/llama_index/packs/raptor/base.py`

| ```
class RaptorPack(BaseLlamaPack):
    """Raptor pack."""

    def __init__(
        self,
        documents: List[BaseNode],
        llm: Optional[LLM] = None,
        embed_model: Optional[BaseEmbedding] = None,
        vector_store: Optional[BasePydanticVectorStore] = None,
        similarity_top_k: int = 2,
        mode: QueryModes = "collapsed",
        verbose: bool = True,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        self.retriever = RaptorRetriever(
            documents,
            embed_model=embed_model,
            llm=llm,
            similarity_top_k=similarity_top_k,
            vector_store=vector_store,
            mode=mode,
            verbose=verbose,
            **kwargs,
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "retriever": self.retriever,
        }

    def run(
        self,
        query: str,
        mode: Optional[QueryModes] = None,
    ) -> Any:
        """Run the pipeline."""
        return self.retriever.retrieve(query, mode=mode)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-raptor/llama_index/packs/raptor/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "retriever": self.retriever,
    }

```
  
---|---  
###  run #
```
run(query: str, mode: Optional[QueryModes] = None) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-raptor/llama_index/packs/raptor/base.py`

| ```
def run(
    self,
    query: str,
    mode: Optional[QueryModes] = None,
) -> Any:
    """Run the pipeline."""
    return self.retriever.retrieve(query, mode=mode)

```
  
---|---
