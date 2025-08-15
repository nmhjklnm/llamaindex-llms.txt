# Chroma autoretrieval
##  ChromaAutoretrievalPack #
Bases: `BaseLlamaPack`
Chroma auto-retrieval pack.
Source code in `llama-index-packs/llama-index-packs-chroma-autoretrieval/llama_index/packs/chroma_autoretrieval/base.py`

| ```
class ChromaAutoretrievalPack(BaseLlamaPack):
    """Chroma auto-retrieval pack."""

    def __init__(
        self,
        collection_name: str,
        vector_store_info: VectorStoreInfo,
        nodes: Optional[List[TextNode]] = None,
        client: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        import chromadb

        chroma_client = client or chromadb.EphemeralClient()
        chroma_collection = chroma_client.get_or_create_collection(collection_name)

        self._vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

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
Source code in `llama-index-packs/llama-index-packs-chroma-autoretrieval/llama_index/packs/chroma_autoretrieval/base.py`

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
Source code in `llama-index-packs/llama-index-packs-chroma-autoretrieval/llama_index/packs/chroma_autoretrieval/base.py`

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
Source code in `llama-index-packs/llama-index-packs-chroma-autoretrieval/llama_index/packs/chroma_autoretrieval/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
