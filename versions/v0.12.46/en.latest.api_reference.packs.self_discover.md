# Self discover
##  SelfDiscoverPack #
Bases: `BaseLlamaPack`
Self-Discover Pack.
Source code in `llama-index-packs/llama-index-packs-self-discover/llama_index/packs/self_discover/base.py`

| ```
class SelfDiscoverPack(BaseLlamaPack):
    """Self-Discover Pack."""

    def __init__(
        self,
        llm: Optional[Any] = None,
        verbose: bool = True,
    ) -> None:
        """Init params."""
        self.llm = llm or OpenAI(model="gpt-3.5-turbo")
        self.reasoning_modules = _REASONING_MODULES
        self.verbose = verbose

        self.workflow = SelfDiscoverWorkflow(verbose=verbose)

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "llm": self.llm,
            "reasoning_modules": self.reasoning_modules,
            "workflow": self.workflow,
        }

    def run(self, task):
        """Runs the configured pipeline for a specified task and reasoning modules."""
        return asyncio_run(self.workflow.run(task=task, llm=self.llm))

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-self-discover/llama_index/packs/self_discover/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "llm": self.llm,
        "reasoning_modules": self.reasoning_modules,
        "workflow": self.workflow,
    }

```
  
---|---  
###  run #
```
run(task)

```

Runs the configured pipeline for a specified task and reasoning modules.
Source code in `llama-index-packs/llama-index-packs-self-discover/llama_index/packs/self_discover/base.py`

| ```
def run(self, task):
    """Runs the configured pipeline for a specified task and reasoning modules."""
    return asyncio_run(self.workflow.run(task=task, llm=self.llm))

```
  
---|---
