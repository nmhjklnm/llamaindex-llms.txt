# Timescale vector autoretrieval
##  TimescaleVectorAutoretrievalPack #
Bases: `BaseLlamaPack`
Timescale Vector auto-retrieval pack.
Source code in `llama-index-packs/llama-index-packs-timescale-vector-autoretrieval/llama_index/packs/timescale_vector_autoretrieval/base.py`

| ```
class TimescaleVectorAutoretrievalPack(BaseLlamaPack):
    """Timescale Vector auto-retrieval pack."""

    def __init__(
        self,
        service_url: str,
        table_name: str,
        time_partition_interval: timedelta,
        vector_store_info: VectorStoreInfo,
        nodes: Optional[List[TextNode]] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        self._vector_store = TimescaleVectorStore.from_params(
            service_url=service_url,
            table_name=table_name,
            time_partition_interval=time_partition_interval,
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

        self.retriever = VectorIndexAutoRetriever(
            self._index, vector_store_info=vector_store_info
        )
        self.query_engine = RetrieverQueryEngine(self.retriever)

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
Source code in `llama-index-packs/llama-index-packs-timescale-vector-autoretrieval/llama_index/packs/timescale_vector_autoretrieval/base.py`

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
Source code in `llama-index-packs/llama-index-packs-timescale-vector-autoretrieval/llama_index/packs/timescale_vector_autoretrieval/base.py`

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
Source code in `llama-index-packs/llama-index-packs-timescale-vector-autoretrieval/llama_index/packs/timescale_vector_autoretrieval/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
