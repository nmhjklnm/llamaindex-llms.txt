# Fixed recency
Node PostProcessor module.
##  FixedRecencyPostprocessor #
Bases: `BaseNodePostprocessor`
Fixed Recency post-processor.
This post-processor does the following steps orders nodes by date.
Assumes the date_key corresponds to a date field in the metadata.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`top_k` |  `int` |  |  `1`  
`date_key` |  `str` |  |  `'date'`  
Source code in `llama-index-core/llama_index/core/postprocessor/node_recency.py`

| ```
class FixedRecencyPostprocessor(BaseNodePostprocessor):
    """
    Fixed Recency post-processor.

    This post-processor does the following steps orders nodes by date.

    Assumes the date_key corresponds to a date field in the metadata.
    """

    top_k: int = 1
    date_key: str = "date"

    @classmethod
    def class_name(cls) -> str:
        return "FixedRecencyPostprocessor"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this function. Please install it with `pip install pandas`."
            )

        if query_bundle is None:
            raise ValueError("Missing query bundle in extra info.")

        # sort nodes by date
        node_dates = pd.to_datetime(
            [node.node.metadata[self.date_key] for node in nodes]
        )
        sorted_node_idxs = np.flip(node_dates.argsort())
        sorted_nodes = [nodes[idx] for idx in sorted_node_idxs]

        return sorted_nodes[: self.top_k]

```
  
---|---
