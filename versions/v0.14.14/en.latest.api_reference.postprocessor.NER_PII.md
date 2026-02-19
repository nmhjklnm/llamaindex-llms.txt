# NER PII
Node PostProcessor module.
##  NERPIINodePostprocessor #
Bases: `BaseNodePostprocessor`
NER PII Node processor.
Uses a HF transformers model.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`pii_node_info_key` |  `str` |  |  `'__pii_node_info__'`  
Source code in `llama-index-core/llama_index/core/postprocessor/pii.py`

| ```
class NERPIINodePostprocessor(BaseNodePostprocessor):
    """
    NER PII Node processor.

    Uses a HF transformers model.

    """

    pii_node_info_key: str = "__pii_node_info__"

    @classmethod
    def class_name(cls) -> str:
        return "NERPIINodePostprocessor"

    def mask_pii(self, ner: Callable, text: str) -> Tuple[str, Dict]:
        """Mask PII in text."""
        new_text = text
        response = ner(text)
        mapping = {}
        for entry in response:
            entity_group_tag = f"[{entry['entity_group']}_{entry['start']}]"
            new_text = new_text.replace(entry["word"], entity_group_tag).strip()
            mapping[entity_group_tag] = entry["word"]
        return new_text, mapping

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        from transformers import pipeline  # pants: no-infer-dep

        ner = pipeline("ner", grouped_entities=True)

        # swap out text from nodes, with the original node mappings
        new_nodes = []
        for node_with_score in nodes:
            node = node_with_score.node
            new_text, mapping_info = self.mask_pii(
                ner, node.get_content(metadata_mode=MetadataMode.LLM)
            )
            new_node = deepcopy(node)
            new_node.excluded_embed_metadata_keys.append(self.pii_node_info_key)
            new_node.excluded_llm_metadata_keys.append(self.pii_node_info_key)
            new_node.metadata[self.pii_node_info_key] = mapping_info
            new_node.set_content(new_text)
            new_nodes.append(NodeWithScore(node=new_node, score=node_with_score.score))

        return new_nodes

```
  
---|---  
###  mask_pii #
```
mask_pii(ner: Callable, text: str) -> Tuple[str, Dict]

```

Mask PII in text.
Source code in `llama-index-core/llama_index/core/postprocessor/pii.py`

| ```
def mask_pii(self, ner: Callable, text: str) -> Tuple[str, Dict]:
    """Mask PII in text."""
    new_text = text
    response = ner(text)
    mapping = {}
    for entry in response:
        entity_group_tag = f"[{entry['entity_group']}_{entry['start']}]"
        new_text = new_text.replace(entry["word"], entity_group_tag).strip()
        mapping[entity_group_tag] = entry["word"]
    return new_text, mapping

```
  
---|---
