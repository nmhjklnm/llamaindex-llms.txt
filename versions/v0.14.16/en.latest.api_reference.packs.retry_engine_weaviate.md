# Retry engine weaviate
##  WeaviateRetryEnginePack #
Bases: `BaseLlamaPack`
Weaviate Retry query engine pack.
Source code in `llama-index-packs/llama-index-packs-retry-engine-weaviate/llama_index/packs/retry_engine_weaviate/base.py`

| ```
class WeaviateRetryEnginePack(BaseLlamaPack):
    """Weaviate Retry query engine pack."""

    def __init__(
        self,
        collection_name: str,
        vector_store_info: VectorStoreInfo,
        host: str,
        auth_client_secret: str,
        nodes: Optional[List[TextNode]] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        from weaviate import Client

        self.client: Client = Client(host, auth_client_secret=auth_client_secret)

        weaviate_client = self.client
        weaviate_collection = weaviate_client.get_or_create_collection(collection_name)

        self._vector_store = WeaviateVectorStore(
            weaviate_collection=weaviate_collection
        )

        if nodes is not None:
            self._storage_context = StorageContext.from_defaults(
                vector_store=self._vector_store
            )
            self._index = VectorStoreIndex(
                nodes, storage_context=self._storage_context, **kwargs
            )
        else:
            self._index = VectorStoreIndex.from_vector_store(
                self._vector_store, **kwargs
            )
            self._storage_context = self._index.storage_context

        self.retriever = self._index.as_retriever()

        base_query_engine = self._index.as_query_engine()
        guideline_eval = GuidelineEvaluator(guidelines=DEFAULT_GUIDELINES)
        self.query_engine = RetryGuidelineQueryEngine(
            base_query_engine, guideline_eval, resynthesize_query=True
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "vector_store": self._vector_store,
            "storage_context": self._storage_context,
            "index": self._index,
            "retriever": self.retriever,
            "query_engine": self.query_engine,
        }

    def retrieve(self, query_str: str) -> Any:
        """Retrieve."""
        return self.retriever.retrieve(query_str)

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.query_engine.query(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-retry-engine-weaviate/llama_index/packs/retry_engine_weaviate/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "vector_store": self._vector_store,
        "storage_context": self._storage_context,
        "index": self._index,
        "retriever": self.retriever,
        "query_engine": self.query_engine,
    }

```
  
---|---  
###  retrieve #
```
retrieve(query_str: str) -> Any

```

Retrieve.
Source code in `llama-index-packs/llama-index-packs-retry-engine-weaviate/llama_index/packs/retry_engine_weaviate/base.py`

| ```
def retrieve(self, query_str: str) -> Any:
    """Retrieve."""
    return self.retriever.retrieve(query_str)

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-retry-engine-weaviate/llama_index/packs/retry_engine_weaviate/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
