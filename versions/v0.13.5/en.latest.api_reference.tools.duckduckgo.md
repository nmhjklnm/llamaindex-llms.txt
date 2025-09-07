# Duckduckgo
##  DuckDuckGoSearchToolSpec #
Bases: `BaseToolSpec`
DuckDuckGoSearch tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-duckduckgo/llama_index/tools/duckduckgo/base.py`

| ```
class DuckDuckGoSearchToolSpec(BaseToolSpec):
    """DuckDuckGoSearch tool spec."""

    spec_functions = ["duckduckgo_instant_search", "duckduckgo_full_search"]

    def __init__(self) -> None:
        if not importlib.util.find_spec("duckduckgo_search"):
            raise ImportError(
                "DuckDuckGoSearchToolSpec requires the duckduckgo_search package to be installed."
            )
        super().__init__()

    def duckduckgo_instant_search(self, query: str) -> List[Dict]:
        """
        Make a query to DuckDuckGo api to receive an instant answer.

        Args:
            query (str): The query to be passed to DuckDuckGo.

        """
        from duckduckgo_search import DDGS

        with DDGS() as ddg:
            return list(ddg.answers(query))

    def duckduckgo_full_search(
        self,
        query: str,
        region: Optional[str] = "wt-wt",
        max_results: Optional[int] = 10,
    ) -> List[Dict]:
        """
        Make a query to DuckDuckGo search to receive a full search results.

        Args:
            query (str): The query to be passed to DuckDuckGo.
            region (Optional[str]): The region to be used for the search in [country-language] convention, ex us-en, uk-en, ru-ru, etc...
            max_results (Optional[int]): The maximum number of results to be returned.

        """
        from duckduckgo_search import DDGS

        params = {
            "keywords": query,
            "region": region,
            "max_results": max_results,
        }

        with DDGS() as ddg:
            return list(ddg.text(**params))

```
  
---|---  
###  duckduckgo_instant_search #
```
duckduckgo_instant_search(query: str) -> List[Dict]

```

Make a query to DuckDuckGo api to receive an instant answer.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The query to be passed to DuckDuckGo. |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-duckduckgo/llama_index/tools/duckduckgo/base.py`

| ```
def duckduckgo_instant_search(self, query: str) -> List[Dict]:
    """
    Make a query to DuckDuckGo api to receive an instant answer.

    Args:
        query (str): The query to be passed to DuckDuckGo.

    """
    from duckduckgo_search import DDGS

    with DDGS() as ddg:
        return list(ddg.answers(query))

```
  
---|---  
###  duckduckgo_full_search #
```
duckduckgo_full_search(query: str, region: Optional[str] = 'wt-wt', max_results: Optional[int] = 10) -> List[Dict]

```

Make a query to DuckDuckGo search to receive a full search results.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The query to be passed to DuckDuckGo. |  _required_  
`region` |  `Optional[str]` |  The region to be used for the search in [country-language] convention, ex us-en, uk-en, ru-ru, etc... |  `'wt-wt'`  
`max_results` |  `Optional[int]` |  The maximum number of results to be returned. |  `10`  
Source code in `llama-index-integrations/tools/llama-index-tools-duckduckgo/llama_index/tools/duckduckgo/base.py`

| ```
def duckduckgo_full_search(
    self,
    query: str,
    region: Optional[str] = "wt-wt",
    max_results: Optional[int] = 10,
) -> List[Dict]:
    """
    Make a query to DuckDuckGo search to receive a full search results.

    Args:
        query (str): The query to be passed to DuckDuckGo.
        region (Optional[str]): The region to be used for the search in [country-language] convention, ex us-en, uk-en, ru-ru, etc...
        max_results (Optional[int]): The maximum number of results to be returned.

    """
    from duckduckgo_search import DDGS

    params = {
        "keywords": query,
        "region": region,
        "max_results": max_results,
    }

    with DDGS() as ddg:
        return list(ddg.text(**params))

```
  
---|---
