# Recursive retriever
##  EmbeddedTablesUnstructuredRetrieverPack #
Bases: `BaseLlamaPack`
Embedded Tables + Unstructured.io Retriever pack.
Use unstructured.io to parse out embedded tables from an HTML document, build a node graph, and then run our recursive retriever against that.
**NOTE** : must take in a single HTML file.
Source code in `llama-index-packs/llama-index-packs-recursive-retriever/llama_index/packs/recursive_retriever/embedded_tables_unstructured/base.py`

| ```
class EmbeddedTablesUnstructuredRetrieverPack(BaseLlamaPack):
    """
    Embedded Tables + Unstructured.io Retriever pack.

    Use unstructured.io to parse out embedded tables from an HTML document, build
    a node graph, and then run our recursive retriever against that.

    **NOTE**: must take in a single HTML file.

    """

    def __init__(
        self,
        html_path: str,
        nodes_save_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        self.reader = FlatReader()

        docs = self.reader.load_data(Path(html_path))

        self.node_parser = UnstructuredElementNodeParser()
        if nodes_save_path is None or not os.path.exists(nodes_save_path):
            raw_nodes = self.node_parser.get_nodes_from_documents(docs)
            pickle.dump(raw_nodes, open(nodes_save_path, "wb"))
        else:
            raw_nodes = pickle.load(open(nodes_save_path, "rb"))

        base_nodes, node_mappings = self.node_parser.get_base_nodes_and_mappings(
            raw_nodes
        )
        # construct top-level vector index + query engine
        vector_index = VectorStoreIndex(base_nodes)
        vector_retriever = vector_index.as_retriever(similarity_top_k=1)
        self.recursive_retriever = RecursiveRetriever(
            "vector",
            retriever_dict={"vector": vector_retriever},
            node_dict=node_mappings,
            verbose=True,
        )
        self.query_engine = RetrieverQueryEngine.from_args(self.recursive_retriever)

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "node_parser": self.node_parser,
            "recursive_retriever": self.recursive_retriever,
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
Source code in `llama-index-packs/llama-index-packs-recursive-retriever/llama_index/packs/recursive_retriever/embedded_tables_unstructured/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "node_parser": self.node_parser,
        "recursive_retriever": self.recursive_retriever,
        "query_engine": self.query_engine,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-recursive-retriever/llama_index/packs/recursive_retriever/embedded_tables_unstructured/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---  
##  RecursiveRetrieverSmallToBigPack #
Bases: `BaseLlamaPack`
Small-to-big retrieval (with recursive retriever).
Given input documents, and an initial set of "parent" chunks, subdivide each chunk further into "child" chunks. Link each child chunk to its parent chunk, and index the child chunks.
Source code in `llama-index-packs/llama-index-packs-recursive-retriever/llama_index/packs/recursive_retriever/small_to_big/base.py`

| ```
class RecursiveRetrieverSmallToBigPack(BaseLlamaPack):
    """
    Small-to-big retrieval (with recursive retriever).

    Given input documents, and an initial set of "parent" chunks,
    subdivide each chunk further into "child" chunks.
    Link each child chunk to its parent chunk, and index the child chunks.

    """

    def __init__(
        self,
        docs: List[Document] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        # create the sentence window node parser w/ default settings
        self.node_parser = SentenceSplitter(chunk_size=1024)
        base_nodes = self.node_parser.get_nodes_from_documents(docs)
        # set node ids to be a constant
        for idx, node in enumerate(base_nodes):
            node.id_ = f"node-{idx}"
        self.embed_model = resolve_embed_model("local:BAAI/bge-small-en")
        self.llm = OpenAI(model="gpt-3.5-turbo")
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        # build graph of smaller chunks pointing to bigger parent chunks
        # make chunk overlap 0
        sub_chunk_sizes = [128, 256, 512]
        sub_node_parsers = [
            SentenceSplitter(chunk_size=c, chunk_overlap=0) for c in sub_chunk_sizes
        ]

        all_nodes = []
        for base_node in base_nodes:
            for n in sub_node_parsers:
                sub_nodes = n.get_nodes_from_documents([base_node])
                sub_inodes = [
                    IndexNode.from_text_node(sn, base_node.node_id) for sn in sub_nodes
                ]
                all_nodes.extend(sub_inodes)

            # also add original node to node
            original_node = IndexNode.from_text_node(base_node, base_node.node_id)
            all_nodes.append(original_node)
        all_nodes_dict = {n.node_id: n for n in all_nodes}

        # define recursive retriever
        self.vector_index_chunk = VectorStoreIndex(all_nodes)
        vector_retriever_chunk = self.vector_index_chunk.as_retriever(
            similarity_top_k=2
        )
        self.recursive_retriever = RecursiveRetriever(
            "vector",
            retriever_dict={"vector": vector_retriever_chunk},
            node_dict=all_nodes_dict,
            verbose=True,
        )
        self.query_engine = RetrieverQueryEngine.from_args(self.recursive_retriever)

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "query_engine": self.query_engine,
            "recursive_retriever": self.recursive_retriever,
            "llm": self.llm,
            "embed_model": self.embed_model,
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
Source code in `llama-index-packs/llama-index-packs-recursive-retriever/llama_index/packs/recursive_retriever/small_to_big/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "query_engine": self.query_engine,
        "recursive_retriever": self.recursive_retriever,
        "llm": self.llm,
        "embed_model": self.embed_model,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-recursive-retriever/llama_index/packs/recursive_retriever/small_to_big/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
