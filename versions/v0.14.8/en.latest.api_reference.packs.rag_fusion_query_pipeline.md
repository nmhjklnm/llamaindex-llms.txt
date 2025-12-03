# Rag fusion query pipeline
##  RAGFusionPipelinePack #
Bases: `BaseLlamaPack`
RAG Fusion pipeline.
Create a bunch of vector indexes of different chunk sizes.
Source code in `llama-index-packs/llama-index-packs-rag-fusion-query-pipeline/llama_index/packs/rag_fusion_query_pipeline/base.py`

| ```
class RAGFusionPipelinePack(BaseLlamaPack):
    """
    RAG Fusion pipeline.

    Create a bunch of vector indexes of different chunk sizes.

    """

    def __init__(
        self,
        documents: List[Document],
        llm: Optional[LLM] = None,
        embed_model: Optional[Any] = "default",
        chunk_sizes: Optional[List[int]] = None,
    ) -> None:
        """Init params."""
        self.documents = documents
        self.chunk_sizes = chunk_sizes or DEFAULT_CHUNK_SIZES

        # construct index
        self.llm = llm or OpenAI(model="gpt-3.5-turbo")

        self.query_engines = []
        self.retrievers = {}
        for chunk_size in self.chunk_sizes:
            splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=0)
            nodes = splitter.get_nodes_from_documents(documents)

            vector_index = VectorStoreIndex(nodes, embed_model=embed_model)
            self.query_engines.append(vector_index.as_query_engine(llm=self.llm))

            self.retrievers[str(chunk_size)] = vector_index.as_retriever()

        # define rerank component
        rerank_component = FnComponent(fn=reciprocal_rank_fusion)

        # construct query pipeline
        p = QueryPipeline()
        module_dict = {
            **self.retrievers,
            "input": InputComponent(),
            "summarizer": TreeSummarize(llm=llm),
            # NOTE: Join args
            "join": ArgPackComponent(),
            "reranker": rerank_component,
        }
        p.add_modules(module_dict)
        # add links from input to retriever (id'ed by chunk_size)
        for chunk_size in self.chunk_sizes:
            p.add_link("input", str(chunk_size))
            p.add_link(str(chunk_size), "join", dest_key=str(chunk_size))
        p.add_link("join", "reranker")
        p.add_link("input", "summarizer", dest_key="query_str")
        p.add_link("reranker", "summarizer", dest_key="nodes")

        self.query_pipeline = p

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "llm": self.llm,
            "retrievers": self.retrievers,
            "query_engines": self.query_engines,
            "query_pipeline": self.query_pipeline,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.query_pipeline.run(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-rag-fusion-query-pipeline/llama_index/packs/rag_fusion_query_pipeline/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "llm": self.llm,
        "retrievers": self.retrievers,
        "query_engines": self.query_engines,
        "query_pipeline": self.query_pipeline,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-rag-fusion-query-pipeline/llama_index/packs/rag_fusion_query_pipeline/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_pipeline.run(*args, **kwargs)

```
  
---|---
