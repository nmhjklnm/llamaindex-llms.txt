# Compact and refine
Init file.
##  CompactAndRefine #
Bases: `Refine`
Refine responses across compact text chunks.
Source code in `llama-index-core/llama_index/core/response_synthesizers/compact_and_refine.py`

| ```
class CompactAndRefine(Refine):
    """Refine responses across compact text chunks."""

    @dispatcher.span
    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        prev_response: Optional[RESPONSE_TEXT_TYPE] = None,
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        compact_texts = self._make_compact_text_chunks(query_str, text_chunks)
        return await super().aget_response(
            query_str=query_str,
            text_chunks=compact_texts,
            prev_response=prev_response,
            **response_kwargs,
        )

    @dispatcher.span
    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        prev_response: Optional[RESPONSE_TEXT_TYPE] = None,
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        """Get compact response."""
        # use prompt helper to fix compact text_chunks under the prompt limitation
        # TODO: This is a temporary fix - reason it's temporary is that
        # the refine template does not account for size of previous answer.
        new_texts = self._make_compact_text_chunks(query_str, text_chunks)
        return super().get_response(
            query_str=query_str,
            text_chunks=new_texts,
            prev_response=prev_response,
            **response_kwargs,
        )

    def _make_compact_text_chunks(
        self, query_str: str, text_chunks: Sequence[str]
    ) -> List[str]:
        text_qa_template = self._text_qa_template.partial_format(query_str=query_str)
        refine_template = self._refine_template.partial_format(query_str=query_str)

        max_prompt = get_biggest_prompt([text_qa_template, refine_template])
        return self._prompt_helper.repack(max_prompt, text_chunks, llm=self._llm)

```
  
---|---  
###  get_response #
```
get_response(query_str: str, text_chunks: Sequence[str], prev_response: Optional[RESPONSE_TEXT_TYPE] = None, **response_kwargs: Any) -> RESPONSE_TEXT_TYPE

```

Get compact response.
Source code in `llama-index-core/llama_index/core/response_synthesizers/compact_and_refine.py`

| ```
@dispatcher.span
def get_response(
    self,
    query_str: str,
    text_chunks: Sequence[str],
    prev_response: Optional[RESPONSE_TEXT_TYPE] = None,
    **response_kwargs: Any,
) -> RESPONSE_TEXT_TYPE:
    """Get compact response."""
    # use prompt helper to fix compact text_chunks under the prompt limitation
    # TODO: This is a temporary fix - reason it's temporary is that
    # the refine template does not account for size of previous answer.
    new_texts = self._make_compact_text_chunks(query_str, text_chunks)
    return super().get_response(
        query_str=query_str,
        text_chunks=new_texts,
        prev_response=prev_response,
        **response_kwargs,
    )

```
  
---|---
