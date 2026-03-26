# Nebulagraph query engine
##  NebulaGraphQueryEnginePack #
Bases: `BaseLlamaPack`
NebulaGraph Query Engine pack.
Source code in `llama-index-packs/llama-index-packs-nebulagraph-query-engine/llama_index/packs/nebulagraph_query_engine/base.py`

| ```
class NebulaGraphQueryEnginePack(BaseLlamaPack):
    """NebulaGraph Query Engine pack."""

    def __init__(
        self,
        username: str,
        password: str,
        ip_and_port: str,
        space_name: str,
        edge_types: str,
        rel_prop_names: str,
        tags: str,
        max_triplets_per_chunk: int,
        docs: List[Document],
        query_engine_type: Optional[NebulaGraphQueryEngineType] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        os.environ["GRAPHD_HOST"] = "127.0.0.1"
        os.environ["NEBULA_USER"] = username
        os.environ["NEBULA_PASSWORD"] = password
        os.environ["NEBULA_ADDRESS"] = (
            ip_and_port  # such as "127.0.0.1:9669" for local instance
        )

        nebulagraph_graph_store = NebulaGraphStore(
            space_name=space_name,
            edge_types=edge_types,
            rel_prop_names=rel_prop_names,
            tags=tags,
        )

        nebulagraph_storage_context = StorageContext.from_defaults(
            graph_store=nebulagraph_graph_store
        )

        # define LLM
        self.llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
        Settings.llm = self.llm

        nebulagraph_index = KnowledgeGraphIndex.from_documents(
            documents=docs,
            storage_context=nebulagraph_storage_context,
            max_triplets_per_chunk=max_triplets_per_chunk,
            space_name=space_name,
            edge_types=edge_types,
            rel_prop_names=rel_prop_names,
            tags=tags,
            include_embeddings=True,
        )

        # create index
        vector_index = VectorStoreIndex.from_documents(docs)

        if query_engine_type == NebulaGraphQueryEngineType.KG_KEYWORD:
            # KG keyword-based entity retrieval
            self.query_engine = nebulagraph_index.as_query_engine(
                # setting to false uses the raw triplets instead of adding the text from the corresponding nodes
                include_text=False,
                retriever_mode="keyword",
                response_mode="tree_summarize",
            )

        elif query_engine_type == NebulaGraphQueryEngineType.KG_HYBRID:
            # KG hybrid entity retrieval
            self.query_engine = nebulagraph_index.as_query_engine(
                include_text=True,
                response_mode="tree_summarize",
                embedding_mode="hybrid",
                similarity_top_k=3,
                explore_global_knowledge=True,
            )

        elif query_engine_type == NebulaGraphQueryEngineType.RAW_VECTOR:
            # Raw vector index retrieval
            self.query_engine = vector_index.as_query_engine()

        elif query_engine_type == NebulaGraphQueryEngineType.RAW_VECTOR_KG_COMBO:
            from llama_index.core.query_engine import RetrieverQueryEngine

            # create custom retriever
            nebulagraph_vector_retriever = VectorIndexRetriever(index=vector_index)
            nebulagraph_kg_retriever = KGTableRetriever(
                index=nebulagraph_index, retriever_mode="keyword", include_text=False
            )
            nebulagraph_custom_retriever = CustomRetriever(
                nebulagraph_vector_retriever, nebulagraph_kg_retriever
            )

            # create response synthesizer
            nebulagraph_response_synthesizer = get_response_synthesizer(
                response_mode="tree_summarize"
            )

            # Custom combo query engine
            self.query_engine = RetrieverQueryEngine(
                retriever=nebulagraph_custom_retriever,
                response_synthesizer=nebulagraph_response_synthesizer,
            )

        elif query_engine_type == NebulaGraphQueryEngineType.KG_QE:
            # using KnowledgeGraphQueryEngine
            from llama_index.core.query_engine import KnowledgeGraphQueryEngine

            self.query_engine = KnowledgeGraphQueryEngine(
                storage_context=nebulagraph_storage_context,
                llm=self.llm,
                verbose=True,
            )

        elif query_engine_type == NebulaGraphQueryEngineType.KG_RAG_RETRIEVER:
            # using KnowledgeGraphRAGRetriever
            from llama_index.core.query_engine import RetrieverQueryEngine
            from llama_index.core.retrievers import KnowledgeGraphRAGRetriever

            nebulagraph_graph_rag_retriever = KnowledgeGraphRAGRetriever(
                storage_context=nebulagraph_storage_context,
                llm=self.llm,
                verbose=True,
            )

            self.query_engine = RetrieverQueryEngine.from_args(
                nebulagraph_graph_rag_retriever
            )

        else:
            # KG vector-based entity retrieval
            self.query_engine = nebulagraph_index.as_query_engine()

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "llm": self.llm,
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
Source code in `llama-index-packs/llama-index-packs-nebulagraph-query-engine/llama_index/packs/nebulagraph_query_engine/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "llm": self.llm,
        "query_engine": self.query_engine,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-nebulagraph-query-engine/llama_index/packs/nebulagraph_query_engine/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
