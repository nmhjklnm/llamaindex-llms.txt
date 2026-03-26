# Summary
##  SummaryExtractor #
Bases: `BaseExtractor`
Summary extractor. Node-level extractor with adjacent sharing. Extracts `section_summary`, `prev_section_summary`, `next_section_summary` metadata fields.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`llm` |  `Optional[LLM]` |  LLM |  _required_  
`summaries` |  `List[str]` |  list of summaries to extract: 'self', 'prev', 'next' |  _required_  
`prompt_template` |  `str` |  template for summary extraction |  `'Here is the content of the section:\n{context_str}\n\nSummarize the key topics and entities of the section. \nSummary: '`  
Source code in `llama-index-core/llama_index/core/extractors/metadata_extractors.py`

| ```
class SummaryExtractor(BaseExtractor):
    """
    Summary extractor. Node-level extractor with adjacent sharing.
    Extracts `section_summary`, `prev_section_summary`, `next_section_summary`
    metadata fields.

    Args:
        llm (Optional[LLM]): LLM
        summaries (List[str]): list of summaries to extract: 'self', 'prev', 'next'
        prompt_template (str): template for summary extraction

    """

    llm: SerializeAsAny[LLM] = Field(description="The LLM to use for generation.")
    summaries: List[str] = Field(
        description="List of summaries to extract: 'self', 'prev', 'next'"
    )
    prompt_template: str = Field(
        default=DEFAULT_SUMMARY_EXTRACT_TEMPLATE,
        description="Template to use when generating summaries.",
    )

    _self_summary: bool = PrivateAttr()
    _prev_summary: bool = PrivateAttr()
    _next_summary: bool = PrivateAttr()

    def __init__(
        self,
        llm: Optional[LLM] = None,
        # TODO: llm_predictor arg is deprecated
        llm_predictor: Optional[LLM] = None,
        summaries: List[str] = ["self"],
        prompt_template: str = DEFAULT_SUMMARY_EXTRACT_TEMPLATE,
        num_workers: int = DEFAULT_NUM_WORKERS,
        **kwargs: Any,
    ):
        # validation
        if not all(s in ["self", "prev", "next"] for s in summaries):
            raise ValueError("summaries must be one of ['self', 'prev', 'next']")

        super().__init__(
            llm=llm or llm_predictor or Settings.llm,
            summaries=summaries,
            prompt_template=prompt_template,
            num_workers=num_workers,
            **kwargs,
        )

        self._self_summary = "self" in summaries
        self._prev_summary = "prev" in summaries
        self._next_summary = "next" in summaries

    @classmethod
    def class_name(cls) -> str:
        return "SummaryExtractor"

    async def _agenerate_node_summary(self, node: BaseNode) -> str:
        """Generate a summary for a node."""
        if self.is_text_node_only and not isinstance(node, TextNode):
            return ""

        context_str = node.get_content(metadata_mode=self.metadata_mode)
        summary = await self.llm.apredict(
            PromptTemplate(template=self.prompt_template), context_str=context_str
        )

        return summary.strip()

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        if not all(isinstance(node, TextNode) for node in nodes):
            raise ValueError("Only `TextNode` is allowed for `Summary` extractor")

        node_summaries_jobs = []
        for node in nodes:
            node_summaries_jobs.append(self._agenerate_node_summary(node))

        node_summaries = await run_jobs(
            node_summaries_jobs,
            show_progress=self.show_progress,
            workers=self.num_workers,
        )

        # Extract node-level summary metadata
        metadata_list: List[Dict] = [{} for _ in nodes]
        for i, metadata in enumerate(metadata_list):
            if i > 0 and self._prev_summary and node_summaries[i - 1]:
                metadata["prev_section_summary"] = node_summaries[i - 1]
            if i < len(nodes) - 1 and self._next_summary and node_summaries[i + 1]:
                metadata["next_section_summary"] = node_summaries[i + 1]
            if self._self_summary and node_summaries[i]:
                metadata["section_summary"] = node_summaries[i]

        return metadata_list

```
  
---|---
