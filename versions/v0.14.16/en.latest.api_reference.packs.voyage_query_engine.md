# Voyage query engine
##  VoyageQueryEnginePack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-voyage-query-engine/llama_index/packs/voyage_query_engine/base.py`

| ```
class VoyageQueryEnginePack(BaseLlamaPack):
    def __init__(self, documents: List[Document]) -> None:
        llm = OpenAI(model="gpt-4")
        embed_model = VoyageEmbedding(
            model_name="voyage-01", voyage_api_key=os.environ["VOYAGE_API_KEY"]
        )

        self.llm = llm
        Settings.llm = self.llm
        Settings.embed_model = embed_model
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
Source code in `llama-index-packs/llama-index-packs-voyage-query-engine/llama_index/packs/voyage_query_engine/base.py`

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
Source code in `llama-index-packs/llama-index-packs-voyage-query-engine/llama_index/packs/voyage_query_engine/base.py`

| ```
def run(self, query_str: str, **kwargs: Any) -> Any:
    """Run the pipeline."""
    query_engine = self.index.as_query_engine(**kwargs)
    return query_engine.query(query_str)

```
  
---|---
