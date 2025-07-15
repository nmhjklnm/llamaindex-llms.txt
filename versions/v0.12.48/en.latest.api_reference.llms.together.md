# Together
##  TogetherLLM #
Bases: `OpenAILike`
Together LLM.
Examples:
`pip install llama-index-llms-together`
```
from llama_index.llms.together import TogetherLLM

# set api key in env or in llm
# import os
# os.environ["TOGETHER_API_KEY"] = "your api key"

llm = TogetherLLM(
    model="mistralai/Mixtral-8x7B-Instruct-v0.1", api_key="your_api_key"
)

resp = llm.complete("Who is Paul Graham?")
print(resp)

```

Source code in `llama-index-integrations/llms/llama-index-llms-together/llama_index/llms/together/base.py`

| ```
class TogetherLLM(OpenAILike):
    """
    Together LLM.

    Examples:
        `pip install llama-index-llms-together`

    ```python
        from llama_index.llms.together import TogetherLLM

        # set api key in env or in llm
        # import os
        # os.environ["TOGETHER_API_KEY"] = "your api key"

        llm = TogetherLLM(
            model="mistralai/Mixtral-8x7B-Instruct-v0.1", api_key="your_api_key"
        )

        resp = llm.complete("Who is Paul Graham?")
        print(resp)
    ```

    """

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        api_base: str = "https://api.together.xyz/v1",
        is_chat_model: bool = True,
        **kwargs: Any,
    ) -> None:
        api_key = api_key or os.environ.get("TOGETHER_API_KEY", None)
        super().__init__(
            model=model,
            api_key=api_key,
            api_base=api_base,
            is_chat_model=is_chat_model,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "TogetherLLM"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-integrations/llms/llama-index-llms-together/llama_index/llms/together/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "TogetherLLM"

```
  
---|---
