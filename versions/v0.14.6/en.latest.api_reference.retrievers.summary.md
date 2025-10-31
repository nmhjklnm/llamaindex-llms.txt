# Summary
##  SummaryIndexRetriever #
Bases: `BaseRetriever`
Simple retriever for SummaryIndex that returns all nodes.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`index` |  `SummaryIndex` |  The index to retrieve from. |  _required_  
Source code in `llama-index-core/llama_index/core/indices/list/retrievers.py`

| ```
class SummaryIndexRetriever(BaseRetriever):
    """
    Simple retriever for SummaryIndex that returns all nodes.

    Args:
        index (SummaryIndex): The index to retrieve from.

    """

    def __init__(
        self,
        index: SummaryIndex,
        callback_manager: Optional[CallbackManager] = None,
        object_map: Optional[dict] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        self._index = index
        super().__init__(
            callback_manager=callback_manager, object_map=object_map, verbose=verbose
        )

    def _retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        """Retrieve nodes."""
        del query_bundle

        node_ids = self._index.index_struct.nodes
        nodes = self._index.docstore.get_nodes(node_ids)
        return [NodeWithScore(node=node) for node in nodes]

```
  
---|---
