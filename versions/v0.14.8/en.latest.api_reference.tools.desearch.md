# Desearch
##  DesearchToolSpec #
Bases: `BaseToolSpec`
Desearch tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-desearch/llama_index/tools/desearch/base.py`

| ```
class DesearchToolSpec(BaseToolSpec):
    """Desearch tool spec."""

    spec_functions = [
        "ai_search_tool",
        "twitter_search_tool",
        "web_search_tool",
    ]

    def __init__(self, api_key: str) -> None:
        """Initialize with parameters."""
        self.client = Desearch(api_key=api_key)

    def ai_search_tool(
        self,
        prompt: str = Field(description="The search prompt or query."),
        tool: List[
            Literal[
                "web",
                "hackernews",
                "reddit",
                "wikipedia",
                "youtube",
                "twitter",
                "arxiv",
            ]
        ] = Field(description="List of tools to use. Must include at least one tool."),
        model: str = Field(
            default="NOVA",
            description="The model to use for the search. Value should 'NOVA', 'ORBIT' or 'HORIZON'",
        ),
        date_filter: Optional[str] = Field(
            default=None, description="Date filter for the search."
        ),
    ) -> str | dict:
        """
        Perform a search using Desearch.

        Args:
            prompt (str): The search prompt or query.
            tool (List[Literal["web", "hackernews", "reddit", "wikipedia", "youtube", "twitter", "arxiv"]]): List of tools to use. Must include at least one tool.
            model (str, optional): The model to use for the search. Defaults to "NOVA".
            date_filter (Optional[str], optional): Date filter for the search. Defaults to None.

        Returns:
            str | dict: The search result or an error string.

        """
        try:
            return self.client.search(
                prompt,
                tool,
                model,
                date_filter,
            )
        except Exception as e:
            return str(e)

    def twitter_search_tool(
        self,
        query: str = Field(description="The Twitter search query."),
        sort: str = Field(default="Top", description="Sort order for the results."),
        count: int = Field(default=10, description="Number of results to return."),
    ) -> BasicTwitterSearchResponse:
        """
        Perform a basic Twitter search using the Exa API.

        Args:
            query (str, optional): The Twitter search query. Defaults to None.
            sort (str, optional): Sort order for the results. Defaults to "Top".
            count (int, optional): Number of results to return. Defaults to 10.

        Returns:
            BasicTwitterSearchResponse: The search results.

        Raises:
            Exception: If an error occurs when calling the API.

        """
        try:
            return self.client.basic_twitter_search(query, sort, count)
        except Exception as e:
            return str(e)

    def web_search_tool(
        self,
        query: str = Field(description="The search query."),
        num: int = Field(default=10, description="Number of results to return."),
        start: int = Field(
            default=1, description="The starting index for the search results."
        ),
    ) -> List[WebSearchResult]:
        """
        Perform a basic web search using the Exa API.

        Args:
            query (str, optional): The search query. Defaults to None.
            num (int, optional): Number of results to return. Defaults to 10.
            start (int, optional): The starting index for the search results. Defaults to 1.

        Returns:
            List[WebSearchResult]: The search results.

        Raises:
            Exception: If an error occurs when calling the API.

        """
        try:
            return self.client.basic_web_search(query, num, start)
        except Exception as e:
            return str(e)

```
  
---|---  
###  ai_search_tool #
```
ai_search_tool(prompt: str = Field(description='The search prompt or query.'), tool: List[Literal['web', 'hackernews', 'reddit', 'wikipedia', 'youtube', 'twitter', 'arxiv']] = Field(description='List of tools to use. Must include at least one tool.'), model: str = Field(default='NOVA', description="The model to use for the search. Value should 'NOVA', 'ORBIT' or 'HORIZON'"), date_filter: Optional[str] = Field(default=None, description='Date filter for the search.')) -> str | dict

```

Perform a search using Desearch.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  The search prompt or query. |  `Field(description='The search prompt or query.')`  
`tool` |  `List[Literal['web', 'hackernews', 'reddit', 'wikipedia', 'youtube', 'twitter', 'arxiv']]` |  List of tools to use. Must include at least one tool. |  `Field(description='List of tools to use. Must include at least one tool.')`  
`model` |  `str` |  The model to use for the search. Defaults to "NOVA". |  `Field(default='NOVA', description="The model to use for the search. Value should 'NOVA', 'ORBIT' or 'HORIZON'")`  
`date_filter` |  `Optional[str]` |  Date filter for the search. Defaults to None. |  `Field(default=None, description='Date filter for the search.')`  
Returns:
Type | Description  
---|---  
`str | dict` |  str | dict: The search result or an error string.  
Source code in `llama-index-integrations/tools/llama-index-tools-desearch/llama_index/tools/desearch/base.py`

| ```
def ai_search_tool(
    self,
    prompt: str = Field(description="The search prompt or query."),
    tool: List[
        Literal[
            "web",
            "hackernews",
            "reddit",
            "wikipedia",
            "youtube",
            "twitter",
            "arxiv",
        ]
    ] = Field(description="List of tools to use. Must include at least one tool."),
    model: str = Field(
        default="NOVA",
        description="The model to use for the search. Value should 'NOVA', 'ORBIT' or 'HORIZON'",
    ),
    date_filter: Optional[str] = Field(
        default=None, description="Date filter for the search."
    ),
) -> str | dict:
    """
    Perform a search using Desearch.

    Args:
        prompt (str): The search prompt or query.
        tool (List[Literal["web", "hackernews", "reddit", "wikipedia", "youtube", "twitter", "arxiv"]]): List of tools to use. Must include at least one tool.
        model (str, optional): The model to use for the search. Defaults to "NOVA".
        date_filter (Optional[str], optional): Date filter for the search. Defaults to None.

    Returns:
        str | dict: The search result or an error string.

    """
    try:
        return self.client.search(
            prompt,
            tool,
            model,
            date_filter,
        )
    except Exception as e:
        return str(e)

```
  
---|---  
###  twitter_search_tool #
```
twitter_search_tool(query: str = Field(description='The Twitter search query.'), sort: str = Field(default='Top', description='Sort order for the results.'), count: int = Field(default=10, description='Number of results to return.')) -> BasicTwitterSearchResponse

```

Perform a basic Twitter search using the Exa API.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The Twitter search query. Defaults to None. |  `Field(description='The Twitter search query.')`  
`sort` |  `str` |  Sort order for the results. Defaults to "Top". |  `Field(default='Top', description='Sort order for the results.')`  
`count` |  `int` |  Number of results to return. Defaults to 10. |  `Field(default=10, description='Number of results to return.')`  
Returns:
Name | Type | Description  
---|---|---  
`BasicTwitterSearchResponse` |  `BasicTwitterSearchResponse` |  The search results.  
Raises:
Type | Description  
---|---  
`Exception` |  If an error occurs when calling the API.  
Source code in `llama-index-integrations/tools/llama-index-tools-desearch/llama_index/tools/desearch/base.py`

| ```
def twitter_search_tool(
    self,
    query: str = Field(description="The Twitter search query."),
    sort: str = Field(default="Top", description="Sort order for the results."),
    count: int = Field(default=10, description="Number of results to return."),
) -> BasicTwitterSearchResponse:
    """
    Perform a basic Twitter search using the Exa API.

    Args:
        query (str, optional): The Twitter search query. Defaults to None.
        sort (str, optional): Sort order for the results. Defaults to "Top".
        count (int, optional): Number of results to return. Defaults to 10.

    Returns:
        BasicTwitterSearchResponse: The search results.

    Raises:
        Exception: If an error occurs when calling the API.

    """
    try:
        return self.client.basic_twitter_search(query, sort, count)
    except Exception as e:
        return str(e)

```
  
---|---  
###  web_search_tool #
```
web_search_tool(query: str = Field(description='The search query.'), num: int = Field(default=10, description='Number of results to return.'), start: int = Field(default=1, description='The starting index for the search results.')) -> List[WebSearchResult]

```

Perform a basic web search using the Exa API.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The search query. Defaults to None. |  `Field(description='The search query.')`  
`num` |  `int` |  Number of results to return. Defaults to 10. |  `Field(default=10, description='Number of results to return.')`  
`start` |  `int` |  The starting index for the search results. Defaults to 1. |  `Field(default=1, description='The starting index for the search results.')`  
Returns:
Type | Description  
---|---  
`List[WebSearchResult]` |  List[WebSearchResult]: The search results.  
Raises:
Type | Description  
---|---  
`Exception` |  If an error occurs when calling the API.  
Source code in `llama-index-integrations/tools/llama-index-tools-desearch/llama_index/tools/desearch/base.py`

| ```
def web_search_tool(
    self,
    query: str = Field(description="The search query."),
    num: int = Field(default=10, description="Number of results to return."),
    start: int = Field(
        default=1, description="The starting index for the search results."
    ),
) -> List[WebSearchResult]:
    """
    Perform a basic web search using the Exa API.

    Args:
        query (str, optional): The search query. Defaults to None.
        num (int, optional): Number of results to return. Defaults to 10.
        start (int, optional): The starting index for the search results. Defaults to 1.

    Returns:
        List[WebSearchResult]: The search results.

    Raises:
        Exception: If an error occurs when calling the API.

    """
    try:
        return self.client.basic_web_search(query, num, start)
    except Exception as e:
        return str(e)

```
  
---|---
