# You
##  You #
Bases: `CustomLLM`
Wrapper around You.com's conversational Smart and Research APIs.
Each API endpoint is designed to generate conversational responses to a variety of query types, including inline citations and web results when relevant.
Smart Mode: - Quick, reliable answers for a variety of questions - Cites the entire web page URL
Research Mode: - In-depth answers with extensive citations for a variety of questions - Cites the specific web page snippet relevant to the claim
To connect to the You.com api requires an API key which you can get at https://api.you.com.
For more information, check out the documentations at https://documentation.you.com/api-reference/.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`mode` |  |  You.com conversational endpoints. Choose from "smart" or "research" |  _required_  
`ydc_api_key` |  |  You.com API key, if `YDC_API_KEY` is not set in the environment |  _required_  
Source code in `llama-index-integrations/llms/llama-index-llms-you/llama_index/llms/you/base.py`

| ```
class You(CustomLLM):
    """
    Wrapper around You.com's conversational Smart and Research APIs.

    Each API endpoint is designed to generate conversational
    responses to a variety of query types, including inline citations
    and web results when relevant.

    Smart Mode:
    - Quick, reliable answers for a variety of questions
    - Cites the entire web page URL

    Research Mode:
    - In-depth answers with extensive citations for a variety of questions
    - Cites the specific web page snippet relevant to the claim

    To connect to the You.com api requires an API key which
    you can get at https://api.you.com.

    For more information, check out the documentations at
    https://documentation.you.com/api-reference/.

    Args:
        mode: You.com conversational endpoints. Choose from "smart" or "research"
        ydc_api_key: You.com API key, if `YDC_API_KEY` is not set in the environment

    """

    mode: Literal["smart", "research"] = Field(
        "smart",
        description='You.com conversational endpoints. Choose from "smart" or "research"',
    )
    ydc_api_key: Optional[str] = Field(
        None,
        description="You.com API key, if `YDC_API_KEY` is not set in the envrioment",
    )

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            model_name=f"you.com-{self.mode}",
            is_chat_model=True,
            is_function_calling_model=False,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        response = _request(
            self.endpoint,
            api_key=self._api_key,
            query=prompt,
        )
        return CompletionResponse(text=response["answer"], raw=response)

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        response = _request_stream(
            self.endpoint,
            api_key=self._api_key,
            query=prompt,
        )

        completion = ""
        for token in response:
            completion += token
            yield CompletionResponse(text=completion, delta=token)

    @property
    def endpoint(self) -> str:
        if self.mode == "smart":
            return SMART_ENDPOINT
        return RESEARCH_ENDPOINT

    @property
    def _api_key(self) -> str:
        return self.ydc_api_key or os.environ["YDC_API_KEY"]

```
  
---|---
