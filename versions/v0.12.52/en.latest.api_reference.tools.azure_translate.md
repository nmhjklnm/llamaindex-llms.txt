# Azure translate
##  AzureTranslateToolSpec #
Bases: `BaseToolSpec`
Azure Translate tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-azure-translate/llama_index/tools/azure_translate/base.py`

| ```
class AzureTranslateToolSpec(BaseToolSpec):
    """Azure Translate tool spec."""

    spec_functions = ["translate"]

    def __init__(self, api_key: str, region: str) -> None:
        """Initialize with parameters."""
        self.headers = {
            "Ocp-Apim-Subscription-Key": api_key,
            "Ocp-Apim-Subscription-Region": region,
            "Content-type": "application/json",
        }

    def translate(self, text: str, language: str):
        """
        Use this tool to translate text from one language to another.
        The source language will be automatically detected. You need to specify the target language
        using a two character language code.

        Args:
            language (str): Target translation language.

        """
        request = requests.post(
            ENDPOINT_BASE_URL,
            params={"api-version": "3.0", "to": language},
            headers=self.headers,
            json=[{"text": text}],
        )
        return request.json()

```
  
---|---  
###  translate #
```
translate(text: str, language: str)

```

Use this tool to translate text from one language to another. The source language will be automatically detected. You need to specify the target language using a two character language code.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`language` |  `str` |  Target translation language. |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-azure-translate/llama_index/tools/azure_translate/base.py`

| ```
def translate(self, text: str, language: str):
    """
    Use this tool to translate text from one language to another.
    The source language will be automatically detected. You need to specify the target language
    using a two character language code.

    Args:
        language (str): Target translation language.

    """
    request = requests.post(
        ENDPOINT_BASE_URL,
        params={"api-version": "3.0", "to": language},
        headers=self.headers,
        json=[{"text": text}],
    )
    return request.json()

```
  
---|---
