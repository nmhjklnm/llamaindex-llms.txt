# Compact accumulate
##  CompactAndAccumulate #
Bases: `Accumulate`
Accumulate responses across compact text chunks.
Source code in `llama-index-core/llama_index/core/response_synthesizers/compact_and_accumulate.py`

| ```
class CompactAndAccumulate(Accumulate):
    """Accumulate responses across compact text chunks."""

    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        separator: str = "\n---------------------\n",
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        """Get compact response."""
        # use prompt helper to fix compact text_chunks under the prompt limitation
        text_qa_template = self._text_qa_template.partial_format(query_str=query_str)

        with temp_set_attrs(self._prompt_helper):
            new_texts = self._prompt_helper.repack(
                text_qa_template, text_chunks, llm=self._llm
            )

            return await super().aget_response(
                query_str=query_str,
                text_chunks=new_texts,
                separator=separator,
                **response_kwargs,
            )

    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        separator: str = "\n---------------------\n",
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        """Get compact response."""
        # use prompt helper to fix compact text_chunks under the prompt limitation
        text_qa_template = self._text_qa_template.partial_format(query_str=query_str)

        with temp_set_attrs(self._prompt_helper):
            new_texts = self._prompt_helper.repack(
                text_qa_template, text_chunks, llm=self._llm
            )

            return super().get_response(
                query_str=query_str,
                text_chunks=new_texts,
                separator=separator,
                **response_kwargs,
            )

```
  
---|---  
###  aget_response `async` #
```
aget_response(query_str: str, text_chunks: Sequence[str], separator: str = '\n---------------------\n', **response_kwargs: Any) -> RESPONSE_TEXT_TYPE

```

Get compact response.
Source code in `llama-index-core/llama_index/core/response_synthesizers/compact_and_accumulate.py`

| ```
async def aget_response(
    self,
    query_str: str,
    text_chunks: Sequence[str],
    separator: str = "\n---------------------\n",
    **response_kwargs: Any,
) -> RESPONSE_TEXT_TYPE:
    """Get compact response."""
    # use prompt helper to fix compact text_chunks under the prompt limitation
    text_qa_template = self._text_qa_template.partial_format(query_str=query_str)

    with temp_set_attrs(self._prompt_helper):
        new_texts = self._prompt_helper.repack(
            text_qa_template, text_chunks, llm=self._llm
        )

        return await super().aget_response(
            query_str=query_str,
            text_chunks=new_texts,
            separator=separator,
            **response_kwargs,
        )

```
  
---|---  
###  get_response #
```
get_response(query_str: str, text_chunks: Sequence[str], separator: str = '\n---------------------\n', **response_kwargs: Any) -> RESPONSE_TEXT_TYPE

```

Get compact response.
Source code in `llama-index-core/llama_index/core/response_synthesizers/compact_and_accumulate.py`

| ```
def get_response(
    self,
    query_str: str,
    text_chunks: Sequence[str],
    separator: str = "\n---------------------\n",
    **response_kwargs: Any,
) -> RESPONSE_TEXT_TYPE:
    """Get compact response."""
    # use prompt helper to fix compact text_chunks under the prompt limitation
    text_qa_template = self._text_qa_template.partial_format(query_str=query_str)

    with temp_set_attrs(self._prompt_helper):
        new_texts = self._prompt_helper.repack(
            text_qa_template, text_chunks, llm=self._llm
        )

        return super().get_response(
            query_str=query_str,
            text_chunks=new_texts,
            separator=separator,
            **response_kwargs,
        )

```
  
---|---
