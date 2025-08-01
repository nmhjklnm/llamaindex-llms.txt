# Gmail openai agent
##  GmailOpenAIAgentPack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-gmail-openai-agent/llama_index/packs/gmail_openai_agent/base.py`

| ```
class GmailOpenAIAgentPack(BaseLlamaPack):
    def __init__(self, gmail_tool_kwargs: Dict[str, Any]) -> None:
        """Init params."""
        try:
            from llama_index.tools.google import GmailToolSpec
        except ImportError:
            raise ImportError("llama_hub not installed.")

        self.tool_spec = GmailToolSpec(**gmail_tool_kwargs)
        self.agent = FunctionAgent(
            tools=self.tool_spec.to_tool_list(),
            llm=OpenAI(model="gpt-4.1"),
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {"gmail_tool": self.tool_spec, "agent": self.agent}

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return asyncio_run(self.arun(*args, **kwargs))

    async def arun(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline asynchronously."""
        return await self.agent.run(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-gmail-openai-agent/llama_index/packs/gmail_openai_agent/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {"gmail_tool": self.tool_spec, "agent": self.agent}

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-gmail-openai-agent/llama_index/packs/gmail_openai_agent/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return asyncio_run(self.arun(*args, **kwargs))

```
  
---|---  
###  arun `async` #
```
arun(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline asynchronously.
Source code in `llama-index-packs/llama-index-packs-gmail-openai-agent/llama_index/packs/gmail_openai_agent/base.py`

| ```
async def arun(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline asynchronously."""
    return await self.agent.run(*args, **kwargs)

```
  
---|---
