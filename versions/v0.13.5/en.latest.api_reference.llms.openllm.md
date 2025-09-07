# Openllm
##  OpenLLM #
Bases: `OpenAILike`
OpenLLM LLM.
A thin wrapper around OpenAI interface to help users interact with OpenLLM's running server.
Examples:
`pip install llama-index-llms-openllm`
```
from llama_index.llms.openllm import OpenLLM

llm = OpenLLM(api_base="https://hostname.com/v1", api_key="na", model="meta-llama/Meta-Llama-3-8B-Instruct")

result = llm.complete("Hi, write a short story\n")

print(result)

```

Source code in `llama-index-integrations/llms/llama-index-llms-openllm/llama_index/llms/openllm/base.py`

| ```
class OpenLLM(OpenAILike):
    r"""
    OpenLLM LLM.

    A thin wrapper around OpenAI interface to help users interact with OpenLLM's running server.


    Examples:
        `pip install llama-index-llms-openllm`

    ```python
        from llama_index.llms.openllm import OpenLLM

        llm = OpenLLM(api_base="https://hostname.com/v1", api_key="na", model="meta-llama/Meta-Llama-3-8B-Instruct")

        result = llm.complete("Hi, write a short story\n")

        print(result)

    ```

    """

    @classmethod
    def class_name(cls) -> str:
        return "OpenLLM"

```
  
---|---
