# Multi modal
Evaluation modules.
##  MultiModalRetrieverEvaluator #
Bases: `BaseRetrievalEvaluator`
Retriever evaluator.
This module will evaluate a retriever using a set of metrics.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`metrics` |  `List[BaseRetrievalMetric]` |  Sequence of metrics to evaluate |  _required_  
`retriever` |  `BaseRetriever` |  Retriever to evaluate. |  _required_  
`node_postprocessors` |  `Optional[List[BaseNodePostprocessor]]` |  Post-processor to apply after retrieval. |  `None`  
Source code in `llama-index-core/llama_index/core/evaluation/retrieval/evaluator.py`

| ```
class MultiModalRetrieverEvaluator(BaseRetrievalEvaluator):
    """
    Retriever evaluator.

    This module will evaluate a retriever using a set of metrics.

    Args:
        metrics (List[BaseRetrievalMetric]): Sequence of metrics to evaluate
        retriever: Retriever to evaluate.
        node_postprocessors (Optional[List[BaseNodePostprocessor]]): Post-processor to apply after retrieval.

    """

    retriever: BaseRetriever = Field(..., description="Retriever to evaluate")
    node_postprocessors: Optional[List[SerializeAsAny[BaseNodePostprocessor]]] = Field(
        default=None, description="Optional post-processor"
    )

    async def _aget_retrieved_ids_and_texts(
        self, query: str, mode: RetrievalEvalMode = RetrievalEvalMode.TEXT
    ) -> Tuple[List[str], List[str]]:
        """Get retrieved ids."""
        retrieved_nodes = await self.retriever.aretrieve(query)
        image_nodes: List[ImageNode] = []
        text_nodes: List[TextNode] = []

        if self.node_postprocessors:
            for node_postprocessor in self.node_postprocessors:
                retrieved_nodes = node_postprocessor.postprocess_nodes(
                    retrieved_nodes, query_str=query
                )

        for scored_node in retrieved_nodes:
            node = scored_node.node
            if isinstance(node, ImageNode):
                image_nodes.append(node)
            if isinstance(node, TextNode):
                text_nodes.append(node)

        if mode == "text":
            return (
                [node.node_id for node in text_nodes],
                [node.text for node in text_nodes],
            )
        elif mode == "image":
            return (
                [node.node_id for node in image_nodes],
                [node.text for node in image_nodes],
            )
        else:
            raise ValueError("Unsupported mode.")

```
  
---|---
