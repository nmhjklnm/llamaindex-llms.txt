# Ollama query engine
##  OllamaQueryEnginePack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-ollama-query-engine/llama_index/packs/ollama_query_engine/base.py`

| ```
class OllamaQueryEnginePack(BaseLlamaPack):
    def __init__(
        self,
        model: str,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        documents: List[Document] = None,
    ) -> None:
        self._model = model
        self._base_url = base_url
        self.llm = Ollama(model=self._model, base_url=self._base_url)

        Settings.llm = self.llm
        Settings.embed_model = OllamaEmbedding(
            model_name=self._model, base_url=self._base_url
        )
        self.index = VectorStoreIndex.from_documents(documents)

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {"llm": self.llm, "index": self.index}

    def run(self, query_str: str, **kwargs: Any) -> Any:
        """Run the pipeline."""
        query_engine = self.index.as_query_engine(**kwargs)
        return query_engine.query(query_str)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-ollama-query-engine/llama_index/packs/ollama_query_engine/base.py`

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
Source code in `llama-index-packs/llama-index-packs-ollama-query-engine/llama_index/packs/ollama_query_engine/base.py`

| ```
def run(self, query_str: str, **kwargs: Any) -> Any:
    """Run the pipeline."""
    query_engine = self.index.as_query_engine(**kwargs)
    return query_engine.query(query_str)

```
  
---|---
