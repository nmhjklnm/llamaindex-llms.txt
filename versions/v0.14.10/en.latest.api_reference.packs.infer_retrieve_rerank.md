# Infer retrieve rerank
##  InferRetrieveRerankPack #
Bases: `BaseLlamaPack`
Infer Retrieve Rerank pack.
Source code in `llama-index-packs/llama-index-packs-infer-retrieve-rerank/llama_index/packs/infer_retrieve_rerank/base.py`

| ```
class InferRetrieveRerankPack(BaseLlamaPack):
    """Infer Retrieve Rerank pack."""

    def __init__(
        self,
        labels: List[str],
        llm: Optional[LLM] = None,
        pred_context: str = "",
        reranker_top_n: int = 3,
        infer_prompt: Optional[PromptTemplate] = None,
        rerank_prompt: Optional[PromptTemplate] = None,
        verbose: bool = False,
    ) -> None:
        """Init params."""
        # NOTE: we use 16k model by default to fit longer contexts
        self.llm = llm or OpenAI(model="gpt-3.5-turbo-16k")
        label_nodes = [TextNode(text=label) for label in labels]
        pipeline = IngestionPipeline(transformations=[OpenAIEmbedding()])
        label_nodes_w_embed = pipeline.run(documents=label_nodes)

        index = VectorStoreIndex(label_nodes_w_embed, show_progress=verbose)
        self.label_retriever = index.as_retriever(similarity_top_k=2)
        self.pred_context = pred_context
        self.reranker_top_n = reranker_top_n
        self.verbose = verbose

        self.infer_prompt = infer_prompt or INFER_PROMPT_TMPL
        self.rerank_prompt = rerank_prompt or RERANK_PROMPT_TMPL

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "llm": self.llm,
            "label_retriever": self.label_retriever,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        inputs = kwargs.get("inputs", [])
        pred_reactions = []
        for idx, input in enumerate(inputs):
            if self.verbose:
                print(f"\n\n> Generating predictions for input {idx}: {input[:300]}")
            cur_pred_reactions = infer_retrieve_rerank(
                input,
                self.label_retriever,
                self.llm,
                self.pred_context,
                self.infer_prompt,
                self.rerank_prompt,
                reranker_top_n=self.reranker_top_n,
            )
            if self.verbose:
                print(f"> Generated predictions: {cur_pred_reactions}")

            pred_reactions.append(cur_pred_reactions)

        return pred_reactions

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-infer-retrieve-rerank/llama_index/packs/infer_retrieve_rerank/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "llm": self.llm,
        "label_retriever": self.label_retriever,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-infer-retrieve-rerank/llama_index/packs/infer_retrieve_rerank/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    inputs = kwargs.get("inputs", [])
    pred_reactions = []
    for idx, input in enumerate(inputs):
        if self.verbose:
            print(f"\n\n> Generating predictions for input {idx}: {input[:300]}")
        cur_pred_reactions = infer_retrieve_rerank(
            input,
            self.label_retriever,
            self.llm,
            self.pred_context,
            self.infer_prompt,
            self.rerank_prompt,
            reranker_top_n=self.reranker_top_n,
        )
        if self.verbose:
            print(f"> Generated predictions: {cur_pred_reactions}")

        pred_reactions.append(cur_pred_reactions)

    return pred_reactions

```
  
---|---
