# Keyword
Node PostProcessor module.
##  KeywordNodePostprocessor #
Bases: `BaseNodePostprocessor`
Keyword-based Node processor.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`required_keywords` |  `List[str]` |  Built-in mutable sequence. If no argument is given, the constructor creates a new empty list. The argument must be an iterable if specified. |  `<dynamic>`  
`exclude_keywords` |  `List[str]` |  Built-in mutable sequence. If no argument is given, the constructor creates a new empty list. The argument must be an iterable if specified. |  `<dynamic>`  
`lang` |  `str` |  |  `'en'`  
Source code in `llama-index-core/llama_index/core/postprocessor/node.py`

| ```
class KeywordNodePostprocessor(BaseNodePostprocessor):
    """Keyword-based Node processor."""

    required_keywords: List[str] = Field(default_factory=list)
    exclude_keywords: List[str] = Field(default_factory=list)
    lang: str = Field(default="en")

    @classmethod
    def class_name(cls) -> str:
        return "KeywordNodePostprocessor"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        try:
            import spacy
        except ImportError:
            raise ImportError(
                "Spacy is not installed, please install it with `pip install spacy`."
            )
        from spacy.matcher import PhraseMatcher

        nlp = spacy.blank(self.lang)
        required_matcher = PhraseMatcher(nlp.vocab)
        exclude_matcher = PhraseMatcher(nlp.vocab)
        required_matcher.add("RequiredKeywords", list(nlp.pipe(self.required_keywords)))
        exclude_matcher.add("ExcludeKeywords", list(nlp.pipe(self.exclude_keywords)))

        new_nodes = []
        for node_with_score in nodes:
            node = node_with_score.node
            doc = nlp(node.get_content())
            if self.required_keywords and not required_matcher(doc):
                continue
            if self.exclude_keywords and exclude_matcher(doc):
                continue
            new_nodes.append(node_with_score)

        return new_nodes

```
  
---|---
