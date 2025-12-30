# Long context reorder
Node PostProcessor module.
##  LongContextReorder #
Bases: `BaseNodePostprocessor`
Models struggle to access significant details found in the center of extended contexts. A study (https://arxiv.org/abs/2307.03172) observed that the best performance typically arises when crucial data is positioned at the start or conclusion of the input context. Additionally, as the input context lengthens, performance drops notably, even in models designed for long contexts.".
Source code in `llama-index-core/llama_index/core/postprocessor/node.py`

| ```
class LongContextReorder(BaseNodePostprocessor):
    """
    Models struggle to access significant details found
    in the center of extended contexts. A study
    (https://arxiv.org/abs/2307.03172) observed that the best
    performance typically arises when crucial data is positioned
    at the start or conclusion of the input context. Additionally,
    as the input context lengthens, performance drops notably, even
    in models designed for long contexts.".
    """

    @classmethod
    def class_name(cls) -> str:
        return "LongContextReorder"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        reordered_nodes: List[NodeWithScore] = []
        ordered_nodes: List[NodeWithScore] = sorted(
            nodes, key=lambda x: x.score if x.score is not None else 0
        )
        for i, node in enumerate(ordered_nodes):
            if i % 2 == 0:
                reordered_nodes.insert(0, node)
            else:
                reordered_nodes.append(node)
        return reordered_nodes

```
  
---|---
