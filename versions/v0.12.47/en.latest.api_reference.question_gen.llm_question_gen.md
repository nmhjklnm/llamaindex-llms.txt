# Llm question gen
##  LLMQuestionGenerator #
Bases: `BaseQuestionGenerator`
Source code in `llama-index-core/llama_index/core/question_gen/llm_generators.py`

| ```
class LLMQuestionGenerator(BaseQuestionGenerator):
    def __init__(
        self,
        llm: LLM,
        prompt: BasePromptTemplate,
    ) -> None:
        self._llm = llm
        self._prompt = prompt

        if self._prompt.output_parser is None:
            raise ValueError("Prompt should have output parser.")

    @classmethod
    def from_defaults(
        cls,
        llm: Optional[LLM] = None,
        prompt_template_str: Optional[str] = None,
        output_parser: Optional[BaseOutputParser] = None,
    ) -> "LLMQuestionGenerator":
        # optionally initialize defaults
        llm = llm or Settings.llm
        prompt_template_str = prompt_template_str or DEFAULT_SUB_QUESTION_PROMPT_TMPL
        output_parser = output_parser or SubQuestionOutputParser()

        # construct prompt
        prompt = PromptTemplate(
            template=prompt_template_str,
            output_parser=output_parser,
            prompt_type=PromptType.SUB_QUESTION,
        )
        return cls(llm, prompt)

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {"question_gen_prompt": self._prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "question_gen_prompt" in prompts:
            output_parser = prompts["question_gen_prompt"].output_parser
            if output_parser is None:
                output_parser = SubQuestionOutputParser()
            self._prompt = PromptTemplate(
                prompts["question_gen_prompt"].get_template(llm=self._llm),
                output_parser=output_parser,
            )

    def generate(
        self, tools: Sequence[ToolMetadata], query: QueryBundle
    ) -> List[SubQuestion]:
        tools_str = build_tools_text(tools)
        query_str = query.query_str
        prediction = self._llm.predict(
            prompt=self._prompt,
            tools_str=tools_str,
            query_str=query_str,
        )

        assert self._prompt.output_parser is not None
        parse = self._prompt.output_parser.parse(prediction)
        parse = cast(StructuredOutput, parse)
        return parse.parsed_output

    async def agenerate(
        self, tools: Sequence[ToolMetadata], query: QueryBundle
    ) -> List[SubQuestion]:
        tools_str = build_tools_text(tools)
        query_str = query.query_str
        prediction = await self._llm.apredict(
            prompt=self._prompt,
            tools_str=tools_str,
            query_str=query_str,
        )

        assert self._prompt.output_parser is not None
        parse = self._prompt.output_parser.parse(prediction)
        parse = cast(StructuredOutput, parse)
        return parse.parsed_output

```
  
---|---  
##  SubQuestionOutputParser #
Bases: `BaseOutputParser`
Source code in `llama-index-core/llama_index/core/question_gen/output_parser.py`

| ```
class SubQuestionOutputParser(BaseOutputParser):
    def parse(self, output: str) -> Any:
        json_dict = parse_json_markdown(output)
        if not json_dict:
            raise ValueError(f"No valid JSON found in output: {output}")

        # example code includes an 'items' key, which breaks
        # the parsing from open-source LLMs such as Zephyr.
        # This gets the actual subquestions and recommended tools directly
        if "items" in json_dict:
            json_dict = json_dict["items"]

        sub_questions = [SubQuestion.model_validate(item) for item in json_dict]
        return StructuredOutput(raw_output=output, parsed_output=sub_questions)

    def format(self, prompt_template: str) -> str:
        return prompt_template

```
  
---|---
