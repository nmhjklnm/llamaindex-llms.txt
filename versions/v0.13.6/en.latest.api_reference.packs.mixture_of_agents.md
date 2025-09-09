# Mixture of agents
##  MixtureOfAgentsPack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-mixture-of-agents/llama_index/packs/mixture_of_agents/base.py`

| ```
class MixtureOfAgentsPack(BaseLlamaPack):
    def __init__(
        self,
        llm: LLM,
        reference_llms: List[LLM],
        num_layers: int = 3,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        timeout: int = 200,
    ) -> None:
        self._wf = MixtureOfAgentWorkflow(
            llm, reference_llms, num_layers, max_tokens, temperature, timeout=timeout
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "llm": self._wf.main_llm,
            "reference_llms": self._wf.reference_llms,
            "num_layers": self._wf.num_layers,
            "temperature": self._wf.temperature,
            "max_tokens": self._wf.max_tokens,
        }

    def run(self, query_str: str, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return asyncio_run(self._wf.run(query_str=query_str))

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-mixture-of-agents/llama_index/packs/mixture_of_agents/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "llm": self._wf.main_llm,
        "reference_llms": self._wf.reference_llms,
        "num_layers": self._wf.num_layers,
        "temperature": self._wf.temperature,
        "max_tokens": self._wf.max_tokens,
    }

```
  
---|---  
###  run #
```
run(query_str: str, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-mixture-of-agents/llama_index/packs/mixture_of_agents/base.py`

| ```
def run(self, query_str: str, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return asyncio_run(self._wf.run(query_str=query_str))

```
  
---|---
