# Node parser semantic chunking
##  SemanticChunkingQueryEnginePack #
Bases: `BaseLlamaPack`
Semantic Chunking Query Engine Pack.
Takes in a list of documents, parses it with semantic embedding chunker, and runs a query engine on the resulting chunks.
Source code in `llama-index-packs/llama-index-packs-node-parser-semantic-chunking/llama_index/packs/node_parser_semantic_chunking/base.py`

| ```
class SemanticChunkingQueryEnginePack(BaseLlamaPack):
    """
    Semantic Chunking Query Engine Pack.

    Takes in a list of documents, parses it with semantic embedding chunker,
    and runs a query engine on the resulting chunks.

    """

    def __init__(
        self,
        documents: List[Document],
        buffer_size: int = 1,
        breakpoint_percentile_threshold: float = 95.0,
    ) -> None:
        """Init params."""
        self.embed_model = OpenAIEmbedding()
        self.splitter = SemanticChunker(
            buffer_size=buffer_size,
            breakpoint_percentile_threshold=breakpoint_percentile_threshold,
            embed_model=self.embed_model,
        )

        nodes = self.splitter.get_nodes_from_documents(documents)
        self.vector_index = VectorStoreIndex(nodes)
        self.query_engine = self.vector_index.as_query_engine()

    def get_modules(self) -> Dict[str, Any]:
        return {
            "vector_index": self.vector_index,
            "query_engine": self.query_engine,
            "splitter": self.splitter,
            "embed_model": self.embed_model,
        }

    def run(self, query: str) -> Any:
        """Run the pipeline."""
        return self.query_engine.query(query)

```
  
---|---  
###  run #
```
run(query: str) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-node-parser-semantic-chunking/llama_index/packs/node_parser_semantic_chunking/base.py`

| ```
def run(self, query: str) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(query)

```
  
---|---
