# Guidance
##  GuidanceQuestionGenerator #
Bases: `BaseQuestionGenerator`
Source code in `llama-index-integrations/question_gen/llama-index-question-gen-guidance/llama_index/question_gen/guidance/base.py`

| ```
class GuidanceQuestionGenerator(BaseQuestionGenerator):
    def __init__(
        self,
        program: GuidancePydanticProgram,
        verbose: bool = False,
    ) -> None:
        self._program = program
        self._verbose = verbose

    @classmethod
    def from_defaults(
        cls,
        prompt_template_str: str = DEFAULT_GUIDANCE_SUB_QUESTION_PROMPT_TMPL,
        guidance_llm: Optional["GuidanceLLM"] = None,
        verbose: bool = False,
    ) -> "GuidanceQuestionGenerator":
        program = GuidancePydanticProgram(
            output_cls=SubQuestionList,
            guidance_llm=guidance_llm,
            prompt_template_str=prompt_template_str,
            verbose=verbose,
        )

        return cls(program, verbose)

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""

    def generate(
        self, tools: Sequence[ToolMetadata], query: QueryBundle
    ) -> List[SubQuestion]:
        tools_str = build_tools_text(tools)
        query_str = query.query_str
        question_list = self._program(
            tools_str=tools_str,
            query_str=query_str,
        )
        question_list = cast(SubQuestionList, question_list)
        return question_list.items

    async def agenerate(
        self, tools: Sequence[ToolMetadata], query: QueryBundle
    ) -> List[SubQuestion]:
        # TODO: currently guidance does not support async calls
        return self.generate(tools=tools, query=query)

```
  
---|---
