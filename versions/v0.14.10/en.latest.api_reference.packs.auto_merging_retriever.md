# Auto merging retriever
##  AutoMergingRetrieverPack #
Bases: `BaseLlamaPack`
Auto-merging Retriever pack.
Build a hierarchical node graph from a set of documents, and run our auto-merging retriever.
Source code in `llama-index-packs/llama-index-packs-auto-merging-retriever/llama_index/packs/auto_merging_retriever/base.py`

| ```
class AutoMergingRetrieverPack(BaseLlamaPack):
    """
    Auto-merging Retriever pack.

    Build a hierarchical node graph from a set of documents, and
    run our auto-merging retriever.

    """

    def __init__(
        self,
        docs: List[Document] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        # create the sentence window node parser w/ default settings
        self.node_parser = HierarchicalNodeParser.from_defaults()
        nodes = self.node_parser.get_nodes_from_documents(docs)
        leaf_nodes = get_leaf_nodes(nodes)
        docstore = SimpleDocumentStore()

        # insert nodes into docstore
        docstore.add_documents(nodes)

        # define storage context (will include vector store by default too)
        storage_context = StorageContext.from_defaults(docstore=docstore)
        self.base_index = VectorStoreIndex(leaf_nodes, storage_context=storage_context)
        base_retriever = self.base_index.as_retriever(similarity_top_k=6)
        self.retriever = AutoMergingRetriever(
            base_retriever, storage_context, verbose=True
        )
        self.query_engine = RetrieverQueryEngine.from_args(self.retriever)

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "node_parser": self.node_parser,
            "retriever": self.retriever,
            "query_engine": self.query_engine,
        }

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
Source code in `llama-index-packs/llama-index-packs-auto-merging-retriever/llama_index/packs/auto_merging_retriever/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "node_parser": self.node_parser,
        "retriever": self.retriever,
        "query_engine": self.query_engine,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-auto-merging-retriever/llama_index/packs/auto_merging_retriever/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
