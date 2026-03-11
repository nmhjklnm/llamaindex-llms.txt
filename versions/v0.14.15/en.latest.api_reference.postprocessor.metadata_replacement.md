# Metadata replacement
Node PostProcessor module.
##  MetadataReplacementPostProcessor #
Bases: `BaseNodePostprocessor`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`target_metadata_key` |  `str` |  Target metadata key to replace node content with. |  _required_  
Source code in `llama-index-core/llama_index/core/postprocessor/metadata_replacement.py`

| ```
class MetadataReplacementPostProcessor(BaseNodePostprocessor):
    target_metadata_key: str = Field(
        description="Target metadata key to replace node content with."
    )

    def __init__(self, target_metadata_key: str) -> None:
        super().__init__(target_metadata_key=target_metadata_key)

    @classmethod
    def class_name(cls) -> str:
        return "MetadataReplacementPostProcessor"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        for n in nodes:
            n.node.set_content(
                n.node.metadata.get(
                    self.target_metadata_key,
                    n.node.get_content(metadata_mode=MetadataMode.NONE),
                )
            )

        return nodes

```
  
---|---
