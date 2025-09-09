# Multi tenancy rag
##  MultiTenancyRAGPack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-multi-tenancy-rag/llama_index/packs/multi_tenancy_rag/base.py`

| ```
class MultiTenancyRAGPack(BaseLlamaPack):
    def __init__(self) -> None:
        llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
        self.llm = llm
        Settings.llm = self.llm
        self.index = VectorStoreIndex.from_documents(documents=[])

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {"llm": self.llm, "index": self.index}

    def add(self, documents: List[Document], user: Any) -> None:
        """Insert Documents of a user into index."""
        # Add metadata to documents
        for document in documents:
            document.metadata["user"] = user
        # Create Nodes using IngestionPipeline
        pipeline = IngestionPipeline(
            transformations=[
                SentenceSplitter(chunk_size=512, chunk_overlap=20),
            ]
        )
        nodes = pipeline.run(documents=documents, num_workers=4)
        # Insert nodes into the index
        self.index.insert_nodes(nodes)

    def run(self, query_str: str, user: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        # Define retriever to filter out nodes for user and query
        retriever = VectorIndexRetriever(
            index=self.index,
            filters=MetadataFilters(
                filters=[
                    ExactMatchFilter(
                        key="user",
                        value=user,
                    )
                ]
            ),
            **kwargs,
        )
        # Define response synthesizer
        response_synthesizer = get_response_synthesizer(response_mode="compact")
        # Define Query Engine
        query_engine = RetrieverQueryEngine(
            retriever=retriever, response_synthesizer=response_synthesizer
        )
        return query_engine.query(query_str)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-multi-tenancy-rag/llama_index/packs/multi_tenancy_rag/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {"llm": self.llm, "index": self.index}

```
  
---|---  
###  add #
```
add(documents: List[Document], user: Any) -> None

```

Insert Documents of a user into index.
Source code in `llama-index-packs/llama-index-packs-multi-tenancy-rag/llama_index/packs/multi_tenancy_rag/base.py`

| ```
def add(self, documents: List[Document], user: Any) -> None:
    """Insert Documents of a user into index."""
    # Add metadata to documents
    for document in documents:
        document.metadata["user"] = user
    # Create Nodes using IngestionPipeline
    pipeline = IngestionPipeline(
        transformations=[
            SentenceSplitter(chunk_size=512, chunk_overlap=20),
        ]
    )
    nodes = pipeline.run(documents=documents, num_workers=4)
    # Insert nodes into the index
    self.index.insert_nodes(nodes)

```
  
---|---  
###  run #
```
run(query_str: str, user: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-multi-tenancy-rag/llama_index/packs/multi_tenancy_rag/base.py`

| ```
def run(self, query_str: str, user: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    # Define retriever to filter out nodes for user and query
    retriever = VectorIndexRetriever(
        index=self.index,
        filters=MetadataFilters(
            filters=[
                ExactMatchFilter(
                    key="user",
                    value=user,
                )
            ]
        ),
        **kwargs,
    )
    # Define response synthesizer
    response_synthesizer = get_response_synthesizer(response_mode="compact")
    # Define Query Engine
    query_engine = RetrieverQueryEngine(
        retriever=retriever, response_synthesizer=response_synthesizer
    )
    return query_engine.query(query_str)

```
  
---|---
