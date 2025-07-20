# Corrective rag
##  CorrectiveRAGPack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-corrective-rag/llama_index/packs/corrective_rag/base.py`

| ```
class CorrectiveRAGPack(BaseLlamaPack):
    def __init__(self, documents: List[Document], tavily_ai_apikey: str) -> None:
        """Init params."""
        self._wf = CorrectiveRAGWorkflow()

        asyncio_run(
            self._wf.run(documents=documents, tavily_ai_apikey=tavily_ai_apikey)
        )

        self.llm = OpenAI(model="gpt-4")
        self.index = self._wf.get_context("ingest").data["index"]

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {"llm": self.llm, "index": self.index}

    def run(self, query_str: str, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return asyncio_run(self._wf.run(query_str=query_str, retriever_kwargs=kwargs))

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-corrective-rag/llama_index/packs/corrective_rag/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {"llm": self.llm, "index": self.index}

```
  
---|---  
###  run #
```
run(query_str: str, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-corrective-rag/llama_index/packs/corrective_rag/base.py`

| ```
def run(self, query_str: str, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return asyncio_run(self._wf.run(query_str=query_str, retriever_kwargs=kwargs))

```
  
---|---
