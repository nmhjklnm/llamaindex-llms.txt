# Sentence window retriever
##  SentenceWindowRetrieverPack #
Bases: `BaseLlamaPack`
Sentence Window Retriever pack.
Build input nodes from a text file by inserting metadata, build a vector index over the input nodes, then after retrieval insert the text into the output nodes before synthesis.
Source code in `llama-index-packs/llama-index-packs-sentence-window-retriever/llama_index/packs/sentence_window_retriever/base.py`

| ```
class SentenceWindowRetrieverPack(BaseLlamaPack):
    """
    Sentence Window Retriever pack.

    Build input nodes from a text file by inserting metadata,
    build a vector index over the input nodes,
    then after retrieval insert the text into the output nodes
    before synthesis.

    """

    def __init__(
        self,
        docs: List[Document] = None,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        # create the sentence window node parser w/ default settings
        self.node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key="window",
            original_text_metadata_key="original_text",
        )

        self.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
        self.embed_model = HuggingFaceEmbedding(
            model_name="sentence-transformers/all-mpnet-base-v2", max_length=512
        )
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        # extract nodes
        nodes = self.node_parser.get_nodes_from_documents(docs)
        self.sentence_index = VectorStoreIndex(nodes)
        self.postprocessor = MetadataReplacementPostProcessor(
            target_metadata_key="window"
        )
        self.query_engine = self.sentence_index.as_query_engine(
            similarity_top_k=2,
            # the target key defaults to `window` to match the node_parser's default
            node_postprocessors=[self.postprocessor],
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "sentence_index": self.sentence_index,
            "node_parser": self.node_parser,
            "postprocessor": self.postprocessor,
            "llm": self.llm,
            "embed_model": self.embed_model,
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
Source code in `llama-index-packs/llama-index-packs-sentence-window-retriever/llama_index/packs/sentence_window_retriever/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "sentence_index": self.sentence_index,
        "node_parser": self.node_parser,
        "postprocessor": self.postprocessor,
        "llm": self.llm,
        "embed_model": self.embed_model,
        "query_engine": self.query_engine,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-sentence-window-retriever/llama_index/packs/sentence_window_retriever/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
