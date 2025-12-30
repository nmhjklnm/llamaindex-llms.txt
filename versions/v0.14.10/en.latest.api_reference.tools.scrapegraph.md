# Scrapegraph
##  ScrapegraphToolSpec #
Bases: `BaseToolSpec`
scrapegraph tool specification for web scraping operations.
Source code in `llama-index-integrations/tools/llama-index-tools-scrapegraph/llama_index/tools/scrapegraph/base.py`

| ```
class ScrapegraphToolSpec(BaseToolSpec):
    """scrapegraph tool specification for web scraping operations."""

    spec_functions = [
        "scrapegraph_smartscraper",
        "scrapegraph_markdownify",
        "scrapegraph_search",
    ]

    def scrapegraph_smartscraper(
        self,
        prompt: str,
        url: str,
        api_key: str,
        schema: Optional[List[BaseModel]] = None,
    ) -> List[Dict]:
        """
        Perform synchronous web scraping using scrapegraph.

        Args:
            prompt (str): User prompt describing the scraping task
            url (str): Target website URL to scrape
            api_key (str): scrapegraph API key
            schema (Optional[List[BaseModel]]): Pydantic models defining the output structure

        Returns:
            List[Dict]: Scraped data matching the provided schema

        """
        client = Client(api_key=api_key)

        # Basic usage
        return client.smartscraper(
            website_url=url, user_prompt=prompt, output_schema=schema
        )

    def scrapegraph_markdownify(self, url: str, api_key: str) -> str:
        """
        Convert webpage content to markdown format using scrapegraph.

        Args:
            url (str): Target website URL to convert
            api_key (str): scrapegraph API key

        Returns:
            str: Markdown representation of the webpage content

        """
        client = Client(api_key=api_key)

        return client.markdownify(website_url=url)

    def scrapegraph_search(self, query: str, api_key: str) -> str:
        """
        Perform a search query using scrapegraph.

        Args:
            query (str): Search query to execute
            api_key (str): scrapegraph API key

        Returns:
            str: Search results from scrapegraph

        """
        client = Client(api_key=api_key)
        return client.search(query=query)

```
  
---|---  
###  scrapegraph_smartscraper #
```
scrapegraph_smartscraper(prompt: str, url: str, api_key: str, schema: Optional[List[BaseModel]] = None) -> List[Dict]

```

Perform synchronous web scraping using scrapegraph.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  User prompt describing the scraping task |  _required_  
`url` |  `str` |  Target website URL to scrape |  _required_  
`api_key` |  `str` |  scrapegraph API key |  _required_  
`schema` |  `Optional[List[BaseModel]]` |  Pydantic models defining the output structure |  `None`  
Returns:
Type | Description  
---|---  
`List[Dict]` |  List[Dict]: Scraped data matching the provided schema  
Source code in `llama-index-integrations/tools/llama-index-tools-scrapegraph/llama_index/tools/scrapegraph/base.py`

| ```
def scrapegraph_smartscraper(
    self,
    prompt: str,
    url: str,
    api_key: str,
    schema: Optional[List[BaseModel]] = None,
) -> List[Dict]:
    """
    Perform synchronous web scraping using scrapegraph.

    Args:
        prompt (str): User prompt describing the scraping task
        url (str): Target website URL to scrape
        api_key (str): scrapegraph API key
        schema (Optional[List[BaseModel]]): Pydantic models defining the output structure

    Returns:
        List[Dict]: Scraped data matching the provided schema

    """
    client = Client(api_key=api_key)

    # Basic usage
    return client.smartscraper(
        website_url=url, user_prompt=prompt, output_schema=schema
    )

```
  
---|---  
###  scrapegraph_markdownify #
```
scrapegraph_markdownify(url: str, api_key: str) -> str

```

Convert webpage content to markdown format using scrapegraph.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url` |  `str` |  Target website URL to convert |  _required_  
`api_key` |  `str` |  scrapegraph API key |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Markdown representation of the webpage content  
Source code in `llama-index-integrations/tools/llama-index-tools-scrapegraph/llama_index/tools/scrapegraph/base.py`

| ```
def scrapegraph_markdownify(self, url: str, api_key: str) -> str:
    """
    Convert webpage content to markdown format using scrapegraph.

    Args:
        url (str): Target website URL to convert
        api_key (str): scrapegraph API key

    Returns:
        str: Markdown representation of the webpage content

    """
    client = Client(api_key=api_key)

    return client.markdownify(website_url=url)

```
  
---|---  
###  scrapegraph_search #
```
scrapegraph_search(query: str, api_key: str) -> str

```

Perform a search query using scrapegraph.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Search query to execute |  _required_  
`api_key` |  `str` |  scrapegraph API key |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Search results from scrapegraph  
Source code in `llama-index-integrations/tools/llama-index-tools-scrapegraph/llama_index/tools/scrapegraph/base.py`

| ```
def scrapegraph_search(self, query: str, api_key: str) -> str:
    """
    Perform a search query using scrapegraph.

    Args:
        query (str): Search query to execute
        api_key (str): scrapegraph API key

    Returns:
        str: Search results from scrapegraph

    """
    client = Client(api_key=api_key)
    return client.search(query=query)

```
  
---|---
