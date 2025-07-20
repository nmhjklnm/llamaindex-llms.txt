# Question
##  QuestionsAnsweredExtractor #
Bases: `BaseExtractor`
Questions answered extractor. Node-level extractor. Extracts `questions_this_excerpt_can_answer` metadata field.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`llm` |  `Optional[LLM]` |  LLM |  _required_  
`questions` |  `int` |  number of questions to extract |  `5`  
`prompt_template` |  `str` |  template for question extraction, |  `'Here is the context:\n{context_str}\n\nGiven the contextual information, generate {num_questions} questions this context can provide specific answers to which are unlikely to be found elsewhere.\n\nHigher-level summaries of surrounding context may be provided as well. Try using these summaries to generate better questions that this context can answer.\n\n'`  
`embedding_only` |  `bool` |  whether to use embedding only |  `True`  
Source code in `llama-index-core/llama_index/core/extractors/metadata_extractors.py`

| ```
class QuestionsAnsweredExtractor(BaseExtractor):
    """
    Questions answered extractor. Node-level extractor.
    Extracts `questions_this_excerpt_can_answer` metadata field.

    Args:
        llm (Optional[LLM]): LLM
        questions (int): number of questions to extract
        prompt_template (str): template for question extraction,
        embedding_only (bool): whether to use embedding only

    """

    llm: SerializeAsAny[LLM] = Field(description="The LLM to use for generation.")
    questions: int = Field(
        default=5,
        description="The number of questions to generate.",
        gt=0,
    )
    prompt_template: str = Field(
        default=DEFAULT_QUESTION_GEN_TMPL,
        description="Prompt template to use when generating questions.",
    )
    embedding_only: bool = Field(
        default=True, description="Whether to use metadata for emebddings only."
    )

    def __init__(
        self,
        llm: Optional[LLM] = None,
        # TODO: llm_predictor arg is deprecated
        llm_predictor: Optional[LLM] = None,
        questions: int = 5,
        prompt_template: str = DEFAULT_QUESTION_GEN_TMPL,
        embedding_only: bool = True,
        num_workers: int = DEFAULT_NUM_WORKERS,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        if questions < 1:
            raise ValueError("questions must be >= 1")

        super().__init__(
            llm=llm or llm_predictor or Settings.llm,
            questions=questions,
            prompt_template=prompt_template,
            embedding_only=embedding_only,
            num_workers=num_workers,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        return "QuestionsAnsweredExtractor"

    async def _aextract_questions_from_node(self, node: BaseNode) -> Dict[str, str]:
        """Extract questions from a node and return it's metadata dict."""
        if self.is_text_node_only and not isinstance(node, TextNode):
            return {}

        context_str = node.get_content(metadata_mode=self.metadata_mode)
        prompt = PromptTemplate(template=self.prompt_template)
        questions = await self.llm.apredict(
            prompt, num_questions=self.questions, context_str=context_str
        )

        return {"questions_this_excerpt_can_answer": questions.strip()}

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        questions_jobs = []
        for node in nodes:
            questions_jobs.append(self._aextract_questions_from_node(node))

        metadata_list: List[Dict] = await run_jobs(
            questions_jobs, show_progress=self.show_progress, workers=self.num_workers
        )

        return metadata_list

```
  
---|---
