# Neo4j query engine
##  Neo4jQueryEnginePack #
Bases: `BaseLlamaPack`
Neo4j Query Engine pack.
Source code in `llama-index-packs/llama-index-packs-neo4j-query-engine/llama_index/packs/neo4j_query_engine/base.py`

| ```
class Neo4jQueryEnginePack(BaseLlamaPack):
    """Neo4j Query Engine pack."""

    def __init__(
        self,
        username: str,
        password: str,
        url: str,
        database: str,
        docs: List[Document],
        query_engine_type: Optional[Neo4jQueryEngineType] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        neo4j_graph_store = Neo4jGraphStore(
            username=username,
            password=password,
            url=url,
            database=database,
        )

        neo4j_storage_context = StorageContext.from_defaults(
            graph_store=neo4j_graph_store
        )

        # define LLM
        self.llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
        Settings.llm = self.llm

        neo4j_index = KnowledgeGraphIndex.from_documents(
            documents=docs,
            storage_context=neo4j_storage_context,
            max_triplets_per_chunk=10,
            include_embeddings=True,
        )

        # create node parser to parse nodes from document
        node_parser = SentenceSplitter(chunk_size=512)

        # use transforms directly
        nodes = node_parser(docs)
        print(f"loaded nodes with {len(nodes)} nodes")

        # based on the nodes, create index
        vector_index = VectorStoreIndex(nodes=nodes)

        if query_engine_type == Neo4jQueryEngineType.KG_KEYWORD:
            # KG keyword-based entity retrieval
            self.query_engine = neo4j_index.as_query_engine(
                # setting to false uses the raw triplets instead of adding the text from the corresponding nodes
                include_text=False,
                retriever_mode="keyword",
                response_mode="tree_summarize",
            )

        elif query_engine_type == Neo4jQueryEngineType.KG_HYBRID:
            # KG hybrid entity retrieval
            self.query_engine = neo4j_index.as_query_engine(
                include_text=True,
                response_mode="tree_summarize",
                embedding_mode="hybrid",
                similarity_top_k=3,
                explore_global_knowledge=True,
            )

        elif query_engine_type == Neo4jQueryEngineType.RAW_VECTOR:
            # Raw vector index retrieval
            self.query_engine = vector_index.as_query_engine()

        elif query_engine_type == Neo4jQueryEngineType.RAW_VECTOR_KG_COMBO:
            from llama_index.core.query_engine import RetrieverQueryEngine

            # create neo4j custom retriever
            neo4j_vector_retriever = VectorIndexRetriever(index=vector_index)
            neo4j_kg_retriever = KGTableRetriever(
                index=neo4j_index, retriever_mode="keyword", include_text=False
            )
            neo4j_custom_retriever = CustomRetriever(
                neo4j_vector_retriever, neo4j_kg_retriever
            )

            # create neo4j response synthesizer
            neo4j_response_synthesizer = get_response_synthesizer(
                response_mode="tree_summarize"
            )

            # Custom combo query engine
            self.query_engine = RetrieverQueryEngine(
                retriever=neo4j_custom_retriever,
                response_synthesizer=neo4j_response_synthesizer,
            )

        elif query_engine_type == Neo4jQueryEngineType.KG_QE:
            # using KnowledgeGraphQueryEngine
            from llama_index.core.query_engine import KnowledgeGraphQueryEngine

            self.query_engine = KnowledgeGraphQueryEngine(
                storage_context=neo4j_storage_context,
                llm=self.llm,
                verbose=True,
            )

        elif query_engine_type == Neo4jQueryEngineType.KG_RAG_RETRIEVER:
            # using KnowledgeGraphRAGRetriever
            from llama_index.core.query_engine import RetrieverQueryEngine
            from llama_index.core.retrievers import KnowledgeGraphRAGRetriever

            neo4j_graph_rag_retriever = KnowledgeGraphRAGRetriever(
                storage_context=neo4j_storage_context,
                llm=self.llm,
                verbose=True,
            )

            self.query_engine = RetrieverQueryEngine.from_args(
                neo4j_graph_rag_retriever
            )

        else:
            # KG vector-based entity retrieval
            self.query_engine = neo4j_index.as_query_engine()

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {"llm": self.llm, "query_engine": self.query_engine}

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
Source code in `llama-index-packs/llama-index-packs-neo4j-query-engine/llama_index/packs/neo4j_query_engine/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {"llm": self.llm, "query_engine": self.query_engine}

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-neo4j-query-engine/llama_index/packs/neo4j_query_engine/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
