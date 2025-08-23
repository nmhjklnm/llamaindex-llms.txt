# Pipeshift
##  Pipeshift #
Bases: `OpenAILike`
Pipeshift LLM.
Examples:
`pip install llama-index-llms-pipeshift`
```
from llama_index.llms.pipeshift import Pipeshift

# set api key in env or in llm
# import os
# os.environ["PIPESHIFT_API_KEY"] = "your api key"

llm = Pipeshift(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct", api_key="your_api_key"
)

resp = llm.complete("How fast is porsche gt3 rs?")
print(resp)

```

Source code in `llama-index-integrations/llms/llama-index-llms-pipeshift/llama_index/llms/pipeshift/base.py`

| ```
class Pipeshift(OpenAILike):
    """
    Pipeshift LLM.

    Examples:
        `pip install llama-index-llms-pipeshift`

    ```python
        from llama_index.llms.pipeshift import Pipeshift

        # set api key in env or in llm
        # import os
        # os.environ["PIPESHIFT_API_KEY"] = "your api key"

        llm = Pipeshift(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct", api_key="your_api_key"
        )

        resp = llm.complete("How fast is porsche gt3 rs?")
        print(resp)
    ```

    """

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        api_base: str = DEFAULT_API_BASE,
        is_chat_model: bool = True,
        **kwargs: Any,
    ) -> None:
        api_key = api_key or os.environ.get("PIPESHIFT_API_KEY", None)
        try:
            validate_api_key_and_model(api_key, model)
            super().__init__(
                model=model,
                api_key=api_key,
                api_base=api_base,
                is_chat_model=is_chat_model,
                **kwargs,
            )
        except ValueError as e:
            raise ValueError(e)

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "Pipeshift"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-integrations/llms/llama-index-llms-pipeshift/llama_index/llms/pipeshift/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "Pipeshift"

```
  
---|---
