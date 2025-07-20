# Prev next
Node PostProcessor module.
##  PrevNextNodePostprocessor #
Bases: `BaseNodePostprocessor`
Previous/Next Node post-processor.
Allows users to fetch additional nodes from the document store, based on the relationships of the nodes.
NOTE: this is a beta feature.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`docstore` |  `BaseDocumentStore` |  The document store. |  _required_  
`num_nodes` |  `int` |  The number of nodes to return (default: 1) |  `1`  
`mode` |  `str` |  The mode of the post-processor. Can be "previous", "next", or "both. |  `'next'`  
Source code in `llama-index-core/llama_index/core/postprocessor/node.py`

| ```
class PrevNextNodePostprocessor(BaseNodePostprocessor):
    """
    Previous/Next Node post-processor.

    Allows users to fetch additional nodes from the document store,
    based on the relationships of the nodes.

    NOTE: this is a beta feature.

    Args:
        docstore (BaseDocumentStore): The document store.
        num_nodes (int): The number of nodes to return (default: 1)
        mode (str): The mode of the post-processor.
            Can be "previous", "next", or "both.

    """

    docstore: BaseDocumentStore
    num_nodes: int = Field(default=1)
    mode: str = Field(default="next")

    @field_validator("mode")
    @classmethod
    def _validate_mode(cls, v: str) -> str:
        """Validate mode."""
        if v not in ["next", "previous", "both"]:
            raise ValueError(f"Invalid mode: {v}")
        return v

    @classmethod
    def class_name(cls) -> str:
        return "PrevNextNodePostprocessor"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        all_nodes: Dict[str, NodeWithScore] = {}
        for node in nodes:
            all_nodes[node.node.node_id] = node
            if self.mode == "next":
                all_nodes.update(get_forward_nodes(node, self.num_nodes, self.docstore))
            elif self.mode == "previous":
                all_nodes.update(
                    get_backward_nodes(node, self.num_nodes, self.docstore)
                )
            elif self.mode == "both":
                all_nodes.update(get_forward_nodes(node, self.num_nodes, self.docstore))
                all_nodes.update(
                    get_backward_nodes(node, self.num_nodes, self.docstore)
                )
            else:
                raise ValueError(f"Invalid mode: {self.mode}")

        all_nodes_values: List[NodeWithScore] = list(all_nodes.values())
        sorted_nodes: List[NodeWithScore] = []
        for node in all_nodes_values:
            # variable to check if cand node is inserted
            node_inserted = False
            for i, cand in enumerate(sorted_nodes):
                node_id = node.node.node_id
                # prepend to current candidate
                prev_node_info = cand.node.prev_node
                next_node_info = cand.node.next_node
                if prev_node_info is not None and node_id == prev_node_info.node_id:
                    node_inserted = True
                    sorted_nodes.insert(i, node)
                    break
                # append to current candidate
                elif next_node_info is not None and node_id == next_node_info.node_id:
                    node_inserted = True
                    sorted_nodes.insert(i + 1, node)
                    break

            if not node_inserted:
                sorted_nodes.append(node)

        return sorted_nodes

```
  
---|---
