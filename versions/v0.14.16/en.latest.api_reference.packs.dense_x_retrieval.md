# Dense x retrieval
##  DenseXRetrievalPack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-dense-x-retrieval/llama_index/packs/dense_x_retrieval/base.py`

| ```
class DenseXRetrievalPack(BaseLlamaPack):
    def __init__(
        self,
        documents: List[Document],
        proposition_llm: Optional[LLM] = None,
        query_llm: Optional[LLM] = None,
        embed_model: Optional[BaseEmbedding] = None,
        text_splitter: TextSplitter = SentenceSplitter(),
        similarity_top_k: int = 4,
        streaming: bool = False,
    ) -> None:
        """Init params."""
        self._proposition_llm = proposition_llm or OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            max_tokens=750,
        )

        Settings.embed_model = embed_model or OpenAIEmbedding(embed_batch_size=128)
        Settings.llm = query_llm or OpenAI()
        Settings.num_output = self._proposition_llm.metadata.num_output

        nodes = text_splitter.get_nodes_from_documents(documents)
        sub_nodes = self._gen_propositions(nodes)

        all_nodes = nodes + sub_nodes
        all_nodes_dict = {n.node_id: n for n in all_nodes}

        self.vector_index = VectorStoreIndex(all_nodes, show_progress=True)

        self.retriever = RecursiveRetriever(
            "vector",
            retriever_dict={
                "vector": self.vector_index.as_retriever(
                    similarity_top_k=similarity_top_k
                )
            },
            node_dict=all_nodes_dict,
        )

        self.query_engine = RetrieverQueryEngine.from_args(
            self.retriever, streaming=streaming
        )

    async def _aget_proposition(self, node: TextNode) -> List[TextNode]:
        """Get proposition."""
        inital_output = await self._proposition_llm.apredict(
            PROPOSITIONS_PROMPT, node_text=node.text
        )
        outputs = inital_output.split("\n")

        all_propositions = []

        for output in outputs:
            if not output.strip():
                continue
            if not output.strip().endswith("]"):
                if not output.strip().endswith('"') and not output.strip().endswith(
                    ","
                ):
                    output = output + '"'
                output = output + " ]"
            if not output.strip().startswith("["):
                if not output.strip().startswith('"'):
                    output = '"' + output
                output = "[ " + output

            try:
                propositions = json.loads(output)
            except Exception:
                # fallback to yaml
                try:
                    propositions = yaml.safe_load(output)
                except Exception:
                    # fallback to next output
                    continue

            if not isinstance(propositions, list):
                continue

            all_propositions.extend(propositions)

        assert isinstance(all_propositions, list)
        nodes = [TextNode(text=prop) for prop in all_propositions if prop]

        return [IndexNode.from_text_node(n, node.node_id) for n in nodes]

    def _gen_propositions(self, nodes: List[TextNode]) -> List[TextNode]:
        """Get propositions."""
        sub_nodes = asyncio.run(
            run_jobs(
                [self._aget_proposition(node) for node in nodes],
                show_progress=True,
                workers=8,
            )
        )

        # Flatten list
        return [node for sub_node in sub_nodes for node in sub_node]

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "query_engine": self.query_engine,
            "retriever": self.retriever,
        }

    def run(self, query_str: str, **kwargs: Any) -> RESPONSE_TYPE:
        """Run the pipeline."""
        return self.query_engine.query(query_str)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-dense-x-retrieval/llama_index/packs/dense_x_retrieval/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "query_engine": self.query_engine,
        "retriever": self.retriever,
    }

```
  
---|---  
###  run #
```
run(query_str: str, **kwargs: Any) -> RESPONSE_TYPE

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-dense-x-retrieval/llama_index/packs/dense_x_retrieval/base.py`

| ```
def run(self, query_str: str, **kwargs: Any) -> RESPONSE_TYPE:
    """Run the pipeline."""
    return self.query_engine.query(query_str)

```
  
---|---
