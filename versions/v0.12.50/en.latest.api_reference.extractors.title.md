# Title
##  TitleExtractor #
Bases: `BaseExtractor`
Title extractor. Useful for long documents. Extracts `document_title` metadata field.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`llm` |  `Optional[LLM]` |  LLM |  _required_  
`nodes` |  `int` |  number of nodes from front to use for title extraction |  `5`  
`node_template` |  `str` |  template for node-level title clues extraction |  `'Context: {context_str}. Give a title that summarizes all of the unique entities, titles or themes found in the context. Title: '`  
`combine_template` |  `str` |  template for combining node-level clues into a document-level title |  `'{context_str}. Based on the above candidate titles and content, what is the comprehensive title for this document? Title: '`  
`is_text_node_only` |  `bool` |  |  `False`  
Source code in `llama-index-core/llama_index/core/extractors/metadata_extractors.py`

| ```
class TitleExtractor(BaseExtractor):
    """
    Title extractor. Useful for long documents. Extracts `document_title`
    metadata field.

    Args:
        llm (Optional[LLM]): LLM
        nodes (int): number of nodes from front to use for title extraction
        node_template (str): template for node-level title clues extraction
        combine_template (str): template for combining node-level clues into
            a document-level title

    """

    is_text_node_only: bool = False  # can work for mixture of text and non-text nodes
    llm: SerializeAsAny[LLM] = Field(description="The LLM to use for generation.")
    nodes: int = Field(
        default=5,
        description="The number of nodes to extract titles from.",
        gt=0,
    )
    node_template: str = Field(
        default=DEFAULT_TITLE_NODE_TEMPLATE,
        description="The prompt template to extract titles with.",
    )
    combine_template: str = Field(
        default=DEFAULT_TITLE_COMBINE_TEMPLATE,
        description="The prompt template to merge titles with.",
    )

    def __init__(
        self,
        llm: Optional[LLM] = None,
        # TODO: llm_predictor arg is deprecated
        llm_predictor: Optional[LLM] = None,
        nodes: int = 5,
        node_template: str = DEFAULT_TITLE_NODE_TEMPLATE,
        combine_template: str = DEFAULT_TITLE_COMBINE_TEMPLATE,
        num_workers: int = DEFAULT_NUM_WORKERS,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        if nodes < 1:
            raise ValueError("num_nodes must be >= 1")

        super().__init__(
            llm=llm or llm_predictor or Settings.llm,
            nodes=nodes,
            node_template=node_template,
            combine_template=combine_template,
            num_workers=num_workers,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        return "TitleExtractor"

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        nodes_by_doc_id = self.separate_nodes_by_ref_id(nodes)
        titles_by_doc_id = await self.extract_titles(nodes_by_doc_id)
        return [{"document_title": titles_by_doc_id[node.ref_doc_id]} for node in nodes]

    def filter_nodes(self, nodes: Sequence[BaseNode]) -> List[BaseNode]:
        filtered_nodes: List[BaseNode] = []
        for node in nodes:
            if self.is_text_node_only and not isinstance(node, TextNode):
                continue
            filtered_nodes.append(node)
        return filtered_nodes

    def separate_nodes_by_ref_id(self, nodes: Sequence[BaseNode]) -> Dict:
        separated_items: Dict[Optional[str], List[BaseNode]] = {}

        for node in nodes:
            key = node.ref_doc_id
            if key not in separated_items:
                separated_items[key] = []

            if len(separated_items[key]) < self.nodes:
                separated_items[key].append(node)

        return separated_items

    async def extract_titles(self, nodes_by_doc_id: Dict) -> Dict:
        jobs = []
        final_dict = {}

        async def get_titles_by_doc(nodes: List[BaseNode], key: str) -> Dict:
            titles_by_doc_id = {}
            title_candidates = await self.get_title_candidates(nodes)
            combined_titles = ", ".join(title_candidates)
            titles_by_doc_id[key] = await self.llm.apredict(
                PromptTemplate(template=self.combine_template),
                context_str=combined_titles,
            )
            return titles_by_doc_id

        for key, nodes in nodes_by_doc_id.items():
            jobs.append(get_titles_by_doc(nodes, key))
        list_dict_titles: List[Dict] = await run_jobs(
            jobs=jobs,
            show_progress=self.show_progress,
        )
        for d in list_dict_titles:
            for key, value in d.items():
                final_dict.update({key: value})
        return final_dict

    async def get_title_candidates(self, nodes: List[BaseNode]) -> List[str]:
        return [
            await self.llm.apredict(
                PromptTemplate(template=self.node_template),
                context_str=cast(TextNode, node).text,
            )
            for node in nodes
        ]

```
  
---|---
