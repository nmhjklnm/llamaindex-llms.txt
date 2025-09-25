# Agents llm compiler
##  LLMCompilerAgentPack #
Bases: `BaseLlamaPack`
LLMCompilerAgent pack.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`tools` |  `List[BaseTool]` |  List of tools to use. |  _required_  
`llm` |  `Optional[LLM]` |  LLM to use. |  `None`  
Source code in `llama-index-packs/llama-index-packs-agents-llm-compiler/llama_index/packs/agents_llm_compiler/base.py`

| ```
class LLMCompilerAgentPack(BaseLlamaPack):
    """
    LLMCompilerAgent pack.

    Args:
        tools (List[BaseTool]): List of tools to use.
        llm (Optional[LLM]): LLM to use.

    """

    def __init__(
        self,
        tools: List[BaseTool],
        llm: Optional[LLM] = None,
        callback_manager: Optional[CallbackManager] = None,
        agent_worker_kwargs: Optional[Dict[str, Any]] = None,
        agent_runner_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Init params."""
        self.llm = llm or OpenAI(model="gpt-4")
        self.callback_manager = callback_manager or self.llm.callback_manager
        self.agent_worker = LLMCompilerAgentWorker.from_tools(
            tools,
            llm=llm,
            verbose=True,
            callback_manager=self.callback_manager,
            **(agent_worker_kwargs or {}),
        )
        self.agent = AgentRunner(
            self.agent_worker,
            callback_manager=self.callback_manager,
            **(agent_runner_kwargs or {}),
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "llm": self.llm,
            "callback_manager": self.callback_manager,
            "agent_worker": self.agent_worker,
            "agent": self.agent,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.agent.chat(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-agents-llm-compiler/llama_index/packs/agents_llm_compiler/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "llm": self.llm,
        "callback_manager": self.callback_manager,
        "agent_worker": self.agent_worker,
        "agent": self.agent,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-agents-llm-compiler/llama_index/packs/agents_llm_compiler/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.agent.chat(*args, **kwargs)

```
  
---|---
