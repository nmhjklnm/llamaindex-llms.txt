# Opea
##  OPEA #
Bases: `OpenAILike`
Adapter for a OPEA LLM.
Examples:
`pip install llama-index-llms-opea`
```
from llama_index.llms.opea import OPEA

llm = OPEA(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct",
    api_base="http://localhost:8080/v1",
)

```

Source code in `llama-index-integrations/llms/llama-index-llms-opea/llama_index/llms/opea/base.py`

| ```
class OPEA(OpenAILike):
    """
    Adapter for a OPEA LLM.

    Examples:
        `pip install llama-index-llms-opea`

    ```python
        from llama_index.llms.opea import OPEA

        llm = OPEA(
            model="meta-llama/Meta-Llama-3.1-8B-Instruct",
            api_base="http://localhost:8080/v1",
        )
    ```

    """

    is_chat_model: bool = Field(
        default=True,
        description=LLMMetadata.model_fields["is_chat_model"].description,
    )

    @classmethod
    def class_name(cls) -> str:
        return "OPEA"

```
  
---|---
