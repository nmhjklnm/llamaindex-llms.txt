# Similarity
Node PostProcessor module.
##  SimilarityPostprocessor #
Bases: `BaseNodePostprocessor`
Similarity-based Node processor.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`similarity_cutoff` |  `float` |  |  `0.0`  
Source code in `llama-index-core/llama_index/core/postprocessor/node.py`

| ```
class SimilarityPostprocessor(BaseNodePostprocessor):
    """Similarity-based Node processor."""

    similarity_cutoff: float = Field(default=0.0)

    @classmethod
    def class_name(cls) -> str:
        return "SimilarityPostprocessor"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        sim_cutoff_exists = self.similarity_cutoff is not None

        new_nodes = []
        for node in nodes:
            should_use_node = True
            if sim_cutoff_exists:
                similarity = node.score
                if similarity is None:
                    should_use_node = False
                elif cast(float, similarity) < cast(float, self.similarity_cutoff):
                    should_use_node = False

            if should_use_node:
                new_nodes.append(node)

        return new_nodes

```
  
---|---
