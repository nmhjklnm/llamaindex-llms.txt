# Presidio
##  PresidioPIINodePostprocessor #
Bases: `BaseNodePostprocessor`
presidio PII Node processor. Uses a presidio to analyse PIIs.
Source code in `llama-index-integrations/postprocessor/llama-index-postprocessor-presidio/llama_index/postprocessor/presidio/base.py`

| ```
class PresidioPIINodePostprocessor(BaseNodePostprocessor):
    """
    presidio PII Node processor.
    Uses a presidio to analyse PIIs.
    """

    pii_node_info_key: str = "__pii_node_info__"
    entity_mapping: Dict[str, Dict] = {}
    mapping: Dict[str, str] = {}

    @classmethod
    def class_name(cls) -> str:
        return "PresidioPIINodePostprocessor"

    def mask_pii(self, text: str) -> Tuple[str, Dict]:
        analyzer = AnalyzerEngine()
        results = analyzer.analyze(text=text, language="en")
        engine = AnonymizerEngine()
        engine.add_anonymizer(EntityTypeCountAnonymizer)

        new_text = engine.anonymize(
            text=text,
            analyzer_results=results,
            operators={
                "DEFAULT": OperatorConfig(
                    "EntityTypeCountAnonymizer",
                    {
                        "entity_mapping": self.entity_mapping,
                        "deanonymize_mapping": self.mapping,
                    },
                )
            },
        )

        return new_text.text

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        # swap out text from nodes, with the original node mappings
        new_nodes = []
        for node_with_score in nodes:
            node = node_with_score.node
            new_text = self.mask_pii(node.get_content(metadata_mode=MetadataMode.LLM))
            new_node = deepcopy(node)
            new_node.excluded_embed_metadata_keys.append(self.pii_node_info_key)
            new_node.excluded_llm_metadata_keys.append(self.pii_node_info_key)
            new_node.metadata[self.pii_node_info_key] = self.mapping
            new_node.set_content(new_text)
            new_nodes.append(NodeWithScore(node=new_node, score=node_with_score.score))

        return new_nodes

```
  
---|---
