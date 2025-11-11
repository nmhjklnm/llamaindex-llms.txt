# Openai
##  OpenAIQuestionGenerator #
Bases: `BaseQuestionGenerator`
Source code in `llama-index-integrations/question_gen/llama-index-question-gen-openai/llama_index/question_gen/openai/base.py`

| ```
class OpenAIQuestionGenerator(BaseQuestionGenerator):
    def __init__(
        self,
        program: OpenAIPydanticProgram,
        verbose: bool = False,
    ) -> None:
        self._program = program
        self._verbose = verbose

    @classmethod
    def from_defaults(
        cls,
        prompt_template_str: str = DEFAULT_OPENAI_SUB_QUESTION_PROMPT_TMPL,
        llm: Optional[LLM] = None,
        verbose: bool = False,
    ) -> "OpenAIQuestionGenerator":
        llm = llm or Settings.llm
        program = OpenAIPydanticProgram.from_defaults(
            output_cls=SubQuestionList,
            llm=llm,
            prompt_template_str=prompt_template_str,
            verbose=verbose,
        )
        return cls(program, verbose)

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {"question_gen_prompt": self._program.prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "question_gen_prompt" in prompts:
            self._program.prompt = prompts["question_gen_prompt"]

    def generate(
        self, tools: Sequence[ToolMetadata], query: QueryBundle
    ) -> List[SubQuestion]:
        tools_str = build_tools_text(tools)
        query_str = query.query_str
        question_list = cast(
            SubQuestionList, self._program(query_str=query_str, tools_str=tools_str)
        )
        return question_list.items

    async def agenerate(
        self, tools: Sequence[ToolMetadata], query: QueryBundle
    ) -> List[SubQuestion]:
        tools_str = build_tools_text(tools)
        query_str = query.query_str
        question_list = cast(
            SubQuestionList,
            await self._program.acall(query_str=query_str, tools_str=tools_str),
        )
        assert isinstance(question_list, SubQuestionList)
        return question_list.items

```
  
---|---
