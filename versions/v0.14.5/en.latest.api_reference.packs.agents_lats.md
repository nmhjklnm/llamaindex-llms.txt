# Agents lats
##  LATSPack #
Bases: `BaseLlamaPack`
Pack for running the LATS agent.
Source code in `llama-index-packs/llama-index-packs-agents-lats/llama_index/packs/agents_lats/base.py`

| ```
class LATSPack(BaseLlamaPack):
    """Pack for running the LATS agent."""

    def __init__(
        self, tools: List[BaseTool], llm: Optional[LLM] = None, **kwargs: Any
    ) -> None:
        """Init params."""
        self.agent_worker = LATSAgentWorker(tools=tools, llm=llm, **kwargs)
        self.agent = AgentRunner(self.agent_worker)

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "agent_worker": self.agent_worker,
            "agent": self.agent,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run."""
        return self.agent.chat(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-agents-lats/llama_index/packs/agents_lats/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "agent_worker": self.agent_worker,
        "agent": self.agent,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run.
Source code in `llama-index-packs/llama-index-packs-agents-lats/llama_index/packs/agents_lats/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run."""
    return self.agent.chat(*args, **kwargs)

```
  
---|---
