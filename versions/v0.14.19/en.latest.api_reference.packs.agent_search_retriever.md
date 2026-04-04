# Agent search retriever
##  AgentSearchRetrieverPack #
Bases: `BaseLlamaPack`
AgentSearchRetrieverPack for running an agent-search retriever.
Source code in `llama-index-packs/llama-index-packs-agent-search-retriever/llama_index/packs/agent_search_retriever/base.py`

| ```
class AgentSearchRetrieverPack(BaseLlamaPack):
    """AgentSearchRetrieverPack for running an agent-search retriever."""

    def __init__(
        self,
        similarity_top_k: int = 2,
        search_provider: str = "agent-search",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
    ) -> None:
        self.retriever = AgentSearchRetriever(
            search_provider=search_provider,
            api_key=api_key,
            api_base=api_base,
            similarity_top_k=similarity_top_k,
        )
        super().__init__()

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "retriever": self.retriever,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self._retriever.retrieve(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-agent-search-retriever/llama_index/packs/agent_search_retriever/base.py`

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
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-agent-search-retriever/llama_index/packs/agent_search_retriever/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self._retriever.retrieve(*args, **kwargs)

```
  
---|---
