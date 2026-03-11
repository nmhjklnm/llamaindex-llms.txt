# Simple summarize
Init file.
##  SimpleSummarize #
Bases: `BaseSynthesizer`
Source code in `llama-index-core/llama_index/core/response_synthesizers/simple_summarize.py`

| ```
class SimpleSummarize(BaseSynthesizer):
    def __init__(
        self,
        llm: Optional[LLM] = None,
        callback_manager: Optional[CallbackManager] = None,
        prompt_helper: Optional[PromptHelper] = None,
        text_qa_template: Optional[BasePromptTemplate] = None,
        streaming: bool = False,
    ) -> None:
        super().__init__(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            streaming=streaming,
        )
        self._text_qa_template = text_qa_template or DEFAULT_TEXT_QA_PROMPT_SEL

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {"text_qa_template": self._text_qa_template}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "text_qa_template" in prompts:
            self._text_qa_template = prompts["text_qa_template"]

    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        text_qa_template = self._text_qa_template.partial_format(query_str=query_str)
        single_text_chunk = "\n".join(text_chunks)
        truncated_chunks = self._prompt_helper.truncate(
            prompt=text_qa_template,
            text_chunks=[single_text_chunk],
            llm=self._llm,
        )

        response: RESPONSE_TEXT_TYPE
        if not self._streaming:
            response = await self._llm.apredict(
                text_qa_template,
                context_str=truncated_chunks,
                **response_kwargs,
            )
        else:
            response = await self._llm.astream(
                text_qa_template,
                context_str=truncated_chunks,
                **response_kwargs,
            )

        if isinstance(response, str):
            response = response or "Empty Response"
        else:
            response = cast(Generator, response)

        return response

    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        text_qa_template = self._text_qa_template.partial_format(query_str=query_str)
        single_text_chunk = "\n".join(text_chunks)
        truncated_chunks = self._prompt_helper.truncate(
            prompt=text_qa_template,
            text_chunks=[single_text_chunk],
            llm=self._llm,
        )

        response: RESPONSE_TEXT_TYPE
        if not self._streaming:
            response = self._llm.predict(
                text_qa_template,
                context_str=truncated_chunks,
                **kwargs,
            )
        else:
            response = self._llm.stream(
                text_qa_template,
                context_str=truncated_chunks,
                **kwargs,
            )

        if isinstance(response, str):
            response = response or "Empty Response"
        else:
            response = cast(Generator, response)

        return response

```
  
---|---
