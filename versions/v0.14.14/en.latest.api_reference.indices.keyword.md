# Keyword
LlamaIndex data structures.
##  KeywordTableIndex #
Bases: `BaseKeywordTableIndex`
Keyword Table Index.
This index uses a GPT model to extract keywords from the text.
Source code in `llama-index-core/llama_index/core/indices/keyword_table/base.py`

| ```
class KeywordTableIndex(BaseKeywordTableIndex):
    """
    Keyword Table Index.

    This index uses a GPT model to extract keywords from the text.

    """

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        response = self._llm.predict(
            self.keyword_extract_template,
            text=text,
        )
        return extract_keywords_given_response(response, start_token="KEYWORDS:")

    async def _async_extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        response = await self._llm.apredict(
            self.keyword_extract_template,
            text=text,
        )
        return extract_keywords_given_response(response, start_token="KEYWORDS:")

```
  
---|---  
##  SimpleKeywordTableIndex #
Bases: `BaseKeywordTableIndex`
Simple Keyword Table Index.
This index uses a simple regex extractor to extract keywords from the text.
Source code in `llama-index-core/llama_index/core/indices/keyword_table/simple_base.py`

| ```
class SimpleKeywordTableIndex(BaseKeywordTableIndex):
    """
    Simple Keyword Table Index.

    This index uses a simple regex extractor to extract keywords from the text.

    """

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        return simple_extract_keywords(text, self.max_keywords_per_chunk)

    def as_retriever(
        self,
        retriever_mode: Union[
            str, KeywordTableRetrieverMode
        ] = KeywordTableRetrieverMode.SIMPLE,
        **kwargs: Any,
    ) -> BaseRetriever:
        return super().as_retriever(retriever_mode=retriever_mode, **kwargs)

```
  
---|---  
##  RAKEKeywordTableIndex #
Bases: `BaseKeywordTableIndex`
RAKE Keyword Table Index.
This index uses a RAKE keyword extractor to extract keywords from the text.
Source code in `llama-index-core/llama_index/core/indices/keyword_table/rake_base.py`

| ```
class RAKEKeywordTableIndex(BaseKeywordTableIndex):
    """
    RAKE Keyword Table Index.

    This index uses a RAKE keyword extractor to extract keywords from the text.

    """

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        return rake_extract_keywords(text, max_keywords=self.max_keywords_per_chunk)

    def as_retriever(
        self,
        retriever_mode: Union[
            str, KeywordTableRetrieverMode
        ] = KeywordTableRetrieverMode.RAKE,
        **kwargs: Any,
    ) -> BaseRetriever:
        return super().as_retriever(retriever_mode=retriever_mode, **kwargs)

```
  
---|---
