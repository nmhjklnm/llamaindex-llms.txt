# Wolfram alpha
##  WolframAlphaToolSpec #
Bases: `BaseToolSpec`
Wolfram Alpha tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-wolfram-alpha/llama_index/tools/wolfram_alpha/base.py`

| ```
class WolframAlphaToolSpec(BaseToolSpec):
    """Wolfram Alpha tool spec."""

    spec_functions = ["wolfram_alpha_query"]

    def __init__(self, app_id: Optional[str] = None) -> None:
        """Initialize with parameters."""
        self.token = app_id

    def wolfram_alpha_query(self, query: str):
        """
        Make a query to wolfram alpha about a mathematical or scientific problem.

        Example inputs:
            "(7 * 12 ^ 10) / 321"
            "How many calories are there in a pound of strawberries"

        Args:
            query (str): The query to be passed to wolfram alpha.

        """
        response = requests.get(
            QUERY_URL_TMPL.format(
                app_id=self.token, query=urllib.parse.quote_plus(query)
            )
        )
        return response.text

```
  
---|---  
###  wolfram_alpha_query #
```
wolfram_alpha_query(query: str)

```

Make a query to wolfram alpha about a mathematical or scientific problem.
Example inputs
"(7 * 12 ^ 10) / 321" "How many calories are there in a pound of strawberries"
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The query to be passed to wolfram alpha. |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-wolfram-alpha/llama_index/tools/wolfram_alpha/base.py`

| ```
def wolfram_alpha_query(self, query: str):
    """
    Make a query to wolfram alpha about a mathematical or scientific problem.

    Example inputs:
        "(7 * 12 ^ 10) / 321"
        "How many calories are there in a pound of strawberries"

    Args:
        query (str): The query to be passed to wolfram alpha.

    """
    response = requests.get(
        QUERY_URL_TMPL.format(
            app_id=self.token, query=urllib.parse.quote_plus(query)
        )
    )
    return response.text

```
  
---|---
