# Web
Init file.
##  AgentQLWebReader #
Bases: `BasePydanticReader`
Scrape a URL with or without a agentql query and returns document in json format.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`api_key` |  `str` |  The AgentQL API key, get one at https://dev.agentql.com |  _required_  
`params` |  `dict` |  Additional parameters to pass to the AgentQL API. Visit https://docs.agentql.com/rest-api/api-reference for details. |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/agentql_web/base.py`

| ```
class AgentQLWebReader(BasePydanticReader):
    """
    Scrape a URL with or without a agentql query and returns document in json format.

    Args:
        api_key (str): The AgentQL API key, get one at https://dev.agentql.com
        params (dict): Additional parameters to pass to the AgentQL API. Visit https://docs.agentql.com/rest-api/api-reference for details.

    """

    api_key: str
    params: Optional[dict]

    def __init__(
        self,
        api_key: str,
        params: Optional[dict] = None,
    ) -> None:
        super().__init__(api_key=api_key, params=params)

    def load_data(
        self, url: str, query: Optional[str] = None, prompt: Optional[str] = None
    ) -> List[Document]:
        """
        Load data from the input directory.

        Args:
            url (str): URL to scrape or crawl.
            query (Optional[str]): AgentQL query used to specify the scraped data.
            prompt (Optional[str]): Natural language description of the data you want to scrape.
            Either query or prompt must be provided.
            params (Optional[dict]): Additional parameters to pass to the AgentQL API. Visit https://docs.agentql.com/rest-api/api-reference for details.

        Returns:
            List[Document]: List of documents.

        """
        payload = {"url": url, "query": query, "prompt": prompt, "params": self.params}

        headers = {
            "X-API-Key": f"{self.api_key}",
            "Content-Type": "application/json",
            "X-TF-Request-Origin": REQUEST_ORIGIN,
        }

        try:
            response = httpx.post(
                QUERY_DATA_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=API_TIMEOUT_SECONDS,
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            response = e.response
            if response.status_code in [401, 403]:
                raise ValueError(
                    "Please, provide a valid API Key. You can create one at https://dev.agentql.com."
                ) from e
            else:
                try:
                    error_json = response.json()
                    msg = (
                        error_json["error_info"]
                        if "error_info" in error_json
                        else error_json["detail"]
                    )
                except (ValueError, TypeError):
                    msg = f"HTTP {e}."
                raise ValueError(msg) from e
        else:
            json = response.json()

            return [Document(text=str(json["data"]), metadata=json["metadata"])]

```
  
---|---  
###  load_data #
```
load_data(url: str, query: Optional[str] = None, prompt: Optional[str] = None) -> List[Document]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url` |  `str` |  URL to scrape or crawl. |  _required_  
`query` |  `Optional[str]` |  AgentQL query used to specify the scraped data. |  `None`  
`prompt` |  `Optional[str]` |  Natural language description of the data you want to scrape. |  `None`  
`params` |  `Optional[dict]` |  Additional parameters to pass to the AgentQL API. Visit https://docs.agentql.com/rest-api/api-reference for details. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/agentql_web/base.py`

| ```
def load_data(
    self, url: str, query: Optional[str] = None, prompt: Optional[str] = None
) -> List[Document]:
    """
    Load data from the input directory.

    Args:
        url (str): URL to scrape or crawl.
        query (Optional[str]): AgentQL query used to specify the scraped data.
        prompt (Optional[str]): Natural language description of the data you want to scrape.
        Either query or prompt must be provided.
        params (Optional[dict]): Additional parameters to pass to the AgentQL API. Visit https://docs.agentql.com/rest-api/api-reference for details.

    Returns:
        List[Document]: List of documents.

    """
    payload = {"url": url, "query": query, "prompt": prompt, "params": self.params}

    headers = {
        "X-API-Key": f"{self.api_key}",
        "Content-Type": "application/json",
        "X-TF-Request-Origin": REQUEST_ORIGIN,
    }

    try:
        response = httpx.post(
            QUERY_DATA_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=API_TIMEOUT_SECONDS,
        )
        response.raise_for_status()

    except httpx.HTTPStatusError as e:
        response = e.response
        if response.status_code in [401, 403]:
            raise ValueError(
                "Please, provide a valid API Key. You can create one at https://dev.agentql.com."
            ) from e
        else:
            try:
                error_json = response.json()
                msg = (
                    error_json["error_info"]
                    if "error_info" in error_json
                    else error_json["detail"]
                )
            except (ValueError, TypeError):
                msg = f"HTTP {e}."
            raise ValueError(msg) from e
    else:
        json = response.json()

        return [Document(text=str(json["data"]), metadata=json["metadata"])]

```
  
---|---  
##  AsyncWebPageReader #
Bases: `BaseReader`
Asynchronous web page reader.
Reads pages from the web asynchronously.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`html_to_text` |  `bool` |  Whether to convert HTML to text. Requires `html2text` package. |  `False`  
`limit` |  `int` |  Maximum number of concurrent requests. |  `10`  
`dedupe` |  `bool` |  to deduplicate urls if there is exact-match within given list |  `True`  
`fail_on_error` |  `bool` |  if requested url does not return status code 200 the routine will raise an ValueError |  `False`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/async_web/base.py`

| ```
class AsyncWebPageReader(BaseReader):
    """
    Asynchronous web page reader.

    Reads pages from the web asynchronously.

    Args:
        html_to_text (bool): Whether to convert HTML to text.
            Requires `html2text` package.
        limit (int): Maximum number of concurrent requests.
        dedupe (bool): to deduplicate urls if there is exact-match within given list
        fail_on_error (bool): if requested url does not return status code 200 the routine will raise an ValueError

    """

    def __init__(
        self,
        html_to_text: bool = False,
        limit: int = 10,
        dedupe: bool = True,
        fail_on_error: bool = False,
        timeout: Optional[int] = 60,
    ) -> None:
        """Initialize with parameters."""
        try:
            import html2text  # noqa: F401
        except ImportError:
            raise ImportError(
                "`html2text` package not found, please run `pip install html2text`"
            )
        try:
            import aiohttp  # noqa: F401
        except ImportError:
            raise ImportError(
                "`aiohttp` package not found, please run `pip install aiohttp`"
            )
        self._limit = limit
        self._html_to_text = html_to_text
        self._dedupe = dedupe
        self._fail_on_error = fail_on_error
        self._timeout = timeout

    async def aload_data(self, urls: List[str]) -> List[Document]:
        """
        Load data from the input urls.

        Args:
            urls (List[str]): List of URLs to scrape.

        Returns:
            List[Document]: List of documents.

        """
        if self._dedupe:
            urls = list(dict.fromkeys(urls))

        import aiohttp

        def chunked_http_client(limit: int):
            semaphore = asyncio.Semaphore(limit)

            async def http_get(url: str, session: aiohttp.ClientSession):
                async with semaphore:
                    async with session.get(url) as response:
                        return response, await response.text()

            return http_get

        async def fetch_urls(urls: List[str]):
            http_client = chunked_http_client(self._limit)

            timeout = (
                aiohttp.ClientTimeout(total=self._timeout) if self._timeout else None
            )

            async with aiohttp.ClientSession(timeout=timeout) as session:
                tasks = [http_client(url, session) for url in urls]
                return await asyncio.gather(*tasks, return_exceptions=True)

        if not isinstance(urls, list):
            raise ValueError("urls must be a list of strings.")

        documents = []
        responses = await fetch_urls(urls)

        for i, response_tuple in enumerate(responses):
            if not isinstance(response_tuple, tuple):
                if self._fail_on_error:
                    raise ValueError(f"Error fetching {urls[i]}")
                continue

            response, raw_page = response_tuple

            if response.status != 200:
                logger.warning(f"Error fetching page from {urls[i]}")
                logger.info(response)

                if self._fail_on_error:
                    raise ValueError(
                        f"Error fetching page from {urls[i]}. server returned status:"
                        f" {response.status} and response {raw_page}"
                    )

                continue

            if self._html_to_text:
                import html2text

                response_text = html2text.html2text(raw_page)
            else:
                response_text = raw_page

            documents.append(
                Document(text=response_text, extra_info={"Source": str(response.url)})
            )

        return documents

    def load_data(self, urls: List[str]) -> List[Document]:
        """
        Load data from the input urls.

        Args:
            urls (List[str]): List of URLs to scrape.

        Returns:
            List[Document]: List of documents.

        """
        return asyncio.run(self.aload_data(urls))

```
  
---|---  
###  aload_data `async` #
```
aload_data(urls: List[str]) -> List[Document]

```

Load data from the input urls.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of URLs to scrape. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/async_web/base.py`

| ```
async def aload_data(self, urls: List[str]) -> List[Document]:
    """
    Load data from the input urls.

    Args:
        urls (List[str]): List of URLs to scrape.

    Returns:
        List[Document]: List of documents.

    """
    if self._dedupe:
        urls = list(dict.fromkeys(urls))

    import aiohttp

    def chunked_http_client(limit: int):
        semaphore = asyncio.Semaphore(limit)

        async def http_get(url: str, session: aiohttp.ClientSession):
            async with semaphore:
                async with session.get(url) as response:
                    return response, await response.text()

        return http_get

    async def fetch_urls(urls: List[str]):
        http_client = chunked_http_client(self._limit)

        timeout = (
            aiohttp.ClientTimeout(total=self._timeout) if self._timeout else None
        )

        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = [http_client(url, session) for url in urls]
            return await asyncio.gather(*tasks, return_exceptions=True)

    if not isinstance(urls, list):
        raise ValueError("urls must be a list of strings.")

    documents = []
    responses = await fetch_urls(urls)

    for i, response_tuple in enumerate(responses):
        if not isinstance(response_tuple, tuple):
            if self._fail_on_error:
                raise ValueError(f"Error fetching {urls[i]}")
            continue

        response, raw_page = response_tuple

        if response.status != 200:
            logger.warning(f"Error fetching page from {urls[i]}")
            logger.info(response)

            if self._fail_on_error:
                raise ValueError(
                    f"Error fetching page from {urls[i]}. server returned status:"
                    f" {response.status} and response {raw_page}"
                )

            continue

        if self._html_to_text:
            import html2text

            response_text = html2text.html2text(raw_page)
        else:
            response_text = raw_page

        documents.append(
            Document(text=response_text, extra_info={"Source": str(response.url)})
        )

    return documents

```
  
---|---  
###  load_data #
```
load_data(urls: List[str]) -> List[Document]

```

Load data from the input urls.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of URLs to scrape. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/async_web/base.py`

| ```
def load_data(self, urls: List[str]) -> List[Document]:
    """
    Load data from the input urls.

    Args:
        urls (List[str]): List of URLs to scrape.

    Returns:
        List[Document]: List of documents.

    """
    return asyncio.run(self.aload_data(urls))

```
  
---|---  
##  BeautifulSoupWebReader #
Bases: `BasePydanticReader`
BeautifulSoup web page reader.
Reads pages from the web. Requires the `bs4` and `urllib` packages.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`website_extractor` |  `Optional[Dict[str, Callable]]` |  A mapping of website hostname (e.g. google.com) to a function that specifies how to extract text from the BeautifulSoup obj. See DEFAULT_WEBSITE_EXTRACTOR. |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/beautiful_soup_web/base.py`

| ```
class BeautifulSoupWebReader(BasePydanticReader):
    """
    BeautifulSoup web page reader.

    Reads pages from the web.
    Requires the `bs4` and `urllib` packages.

    Args:
        website_extractor (Optional[Dict[str, Callable]]): A mapping of website
            hostname (e.g. google.com) to a function that specifies how to
            extract text from the BeautifulSoup obj. See DEFAULT_WEBSITE_EXTRACTOR.

    """

    is_remote: bool = True
    _website_extractor: Dict[str, Callable] = PrivateAttr()

    def __init__(self, website_extractor: Optional[Dict[str, Callable]] = None) -> None:
        super().__init__()
        self._website_extractor = website_extractor or DEFAULT_WEBSITE_EXTRACTOR

    @classmethod
    def class_name(cls) -> str:
        """Get the name identifier of the class."""
        return "BeautifulSoupWebReader"

    def load_data(
        self,
        urls: List[str],
        custom_hostname: Optional[str] = None,
        include_url_in_text: Optional[bool] = True,
    ) -> List[Document]:
        """
        Load data from the urls.

        Args:
            urls (List[str]): List of URLs to scrape.
            custom_hostname (Optional[str]): Force a certain hostname in the case
                a website is displayed under custom URLs (e.g. Substack blogs)
            include_url_in_text (Optional[bool]): Include the reference url in the text of the document

        Returns:
            List[Document]: List of documents.

        """
        from urllib.parse import urlparse

        import requests
        from bs4 import BeautifulSoup

        documents = []
        for url in urls:
            try:
                page = requests.get(url)
            except Exception:
                raise ValueError(f"One of the inputs is not a valid url: {url}")

            hostname = custom_hostname or urlparse(url).hostname or ""

            soup = BeautifulSoup(page.content, "html.parser")

            data = ""
            extra_info = {"URL": url}
            if hostname in self._website_extractor:
                data, metadata = self._website_extractor[hostname](
                    soup=soup, url=url, include_url_in_text=include_url_in_text
                )
                extra_info.update(metadata)

            else:
                data = soup.getText()

            documents.append(
                Document(text=data, id_=str(uuid.uuid4()), extra_info=extra_info)
            )

        return documents

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get the name identifier of the class.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/beautiful_soup_web/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get the name identifier of the class."""
    return "BeautifulSoupWebReader"

```
  
---|---  
###  load_data #
```
load_data(urls: List[str], custom_hostname: Optional[str] = None, include_url_in_text: Optional[bool] = True) -> List[Document]

```

Load data from the urls.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of URLs to scrape. |  _required_  
`custom_hostname` |  `Optional[str]` |  Force a certain hostname in the case a website is displayed under custom URLs (e.g. Substack blogs) |  `None`  
`include_url_in_text` |  `Optional[bool]` |  Include the reference url in the text of the document |  `True`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/beautiful_soup_web/base.py`

| ```
def load_data(
    self,
    urls: List[str],
    custom_hostname: Optional[str] = None,
    include_url_in_text: Optional[bool] = True,
) -> List[Document]:
    """
    Load data from the urls.

    Args:
        urls (List[str]): List of URLs to scrape.
        custom_hostname (Optional[str]): Force a certain hostname in the case
            a website is displayed under custom URLs (e.g. Substack blogs)
        include_url_in_text (Optional[bool]): Include the reference url in the text of the document

    Returns:
        List[Document]: List of documents.

    """
    from urllib.parse import urlparse

    import requests
    from bs4 import BeautifulSoup

    documents = []
    for url in urls:
        try:
            page = requests.get(url)
        except Exception:
            raise ValueError(f"One of the inputs is not a valid url: {url}")

        hostname = custom_hostname or urlparse(url).hostname or ""

        soup = BeautifulSoup(page.content, "html.parser")

        data = ""
        extra_info = {"URL": url}
        if hostname in self._website_extractor:
            data, metadata = self._website_extractor[hostname](
                soup=soup, url=url, include_url_in_text=include_url_in_text
            )
            extra_info.update(metadata)

        else:
            data = soup.getText()

        documents.append(
            Document(text=data, id_=str(uuid.uuid4()), extra_info=extra_info)
        )

    return documents

```
  
---|---  
##  BrowserbaseWebReader #
Bases: `BaseReader`
BrowserbaseWebReader.
Load pre-rendered web pages using a headless browser hosted on Browserbase. Depends on `browserbase` package. Get your API key from https://browserbase.com
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/browserbase_web/base.py`

| ```
class BrowserbaseWebReader(BaseReader):
    """
    BrowserbaseWebReader.

    Load pre-rendered web pages using a headless browser hosted on Browserbase.
    Depends on `browserbase` package.
    Get your API key from https://browserbase.com
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> None:
        try:
            from browserbase import Browserbase
        except ImportError:
            raise ImportError(
                "`browserbase` package not found, please run `pip install browserbase`"
            )

        self.browserbase = Browserbase(api_key, project_id)

    def lazy_load_data(
        self,
        urls: Sequence[str],
        text_content: bool = False,
        session_id: Optional[str] = None,
        proxy: Optional[bool] = None,
    ) -> Iterator[Document]:
        """Load pages from URLs."""
        pages = self.browserbase.load_urls(urls, text_content, session_id, proxy)

        for i, page in enumerate(pages):
            yield Document(
                text=page,
                metadata={
                    "url": urls[i],
                },
            )

```
  
---|---  
###  lazy_load_data #
```
lazy_load_data(urls: Sequence[str], text_content: bool = False, session_id: Optional[str] = None, proxy: Optional[bool] = None) -> Iterator[Document]

```

Load pages from URLs.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/browserbase_web/base.py`

| ```
def lazy_load_data(
    self,
    urls: Sequence[str],
    text_content: bool = False,
    session_id: Optional[str] = None,
    proxy: Optional[bool] = None,
) -> Iterator[Document]:
    """Load pages from URLs."""
    pages = self.browserbase.load_urls(urls, text_content, session_id, proxy)

    for i, page in enumerate(pages):
        yield Document(
            text=page,
            metadata={
                "url": urls[i],
            },
        )

```
  
---|---  
##  FireCrawlWebReader #
Bases: `BasePydanticReader`
turn a url to llm accessible markdown with `Firecrawl.dev`.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`api_key` |  `str` |  The Firecrawl API key. |  _required_  
`api_url` |  `Optional[str]` |  url to be passed to FirecrawlApp for local deployment |  `None`  
`mode` |  `Optional[str]` |  The mode to run the loader in. Default is "crawl". Options include "scrape" (single url), "crawl" (all accessible sub pages), "search" (search for content), and "extract" (extract structured data from URLs using a prompt). |  `'crawl'`  
`params` |  `Optional[dict]` |  The parameters to pass to the Firecrawl API. |  `None`  
Examples include crawlerOptions. For more details, visit: https://docs.firecrawl.dev/sdks/python
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/firecrawl_web/base.py`

| ```
class FireCrawlWebReader(BasePydanticReader):
    """
    turn a url to llm accessible markdown with `Firecrawl.dev`.

    Args:
        api_key (str): The Firecrawl API key.
        api_url (Optional[str]): url to be passed to FirecrawlApp for local deployment
        mode (Optional[str]):
            The mode to run the loader in. Default is "crawl".
            Options include "scrape" (single url),
            "crawl" (all accessible sub pages),
            "search" (search for content), and
            "extract" (extract structured data from URLs using a prompt).
        params (Optional[dict]): The parameters to pass to the Firecrawl API.

    Examples include crawlerOptions.
    For more details, visit: https://docs.firecrawl.dev/sdks/python

    """

    firecrawl: Any
    api_key: str
    api_url: Optional[str]
    mode: Optional[str]
    params: Optional[dict]

    _metadata_fn: Optional[Callable[[str], Dict]] = PrivateAttr()

    def __init__(
        self,
        api_key: str,
        api_url: Optional[str] = None,
        mode: Optional[str] = "crawl",
        params: Optional[dict] = None,
    ) -> None:
        """Initialize with parameters."""
        # Ensure firecrawl-py version is 2.0 or higher
        try:
            import firecrawl

            error_msg = "firecrawl-py version must be >=2.0 and <3.0"
            if firecrawl.__version__ < "2.0.0":
                raise ImportError(error_msg)
            if firecrawl.__version__ >= "3.0.0":
                raise ImportError(error_msg)
        except ImportError:
            raise ImportError(
                "firecrawl-py not found, please run `pip install firecrawl-py`"
            )

        firecrawl = firecrawl.FirecrawlApp(api_key=api_key, api_url=api_url)

        params = params or {}
        params["integration"] = "llamaindex"

        super().__init__(
            firecrawl=firecrawl,
            api_key=api_key,
            api_url=api_url,
            mode=mode,
            params=params,
        )

    @classmethod
    def class_name(cls) -> str:
        return "Firecrawl_reader"

    def load_data(
        self,
        url: Optional[str] = None,
        query: Optional[str] = None,
        urls: Optional[List[str]] = None,
    ) -> List[Document]:
        """
        Load data from the input directory.

        Args:
            url (Optional[str]): URL to scrape or crawl.
            query (Optional[str]): Query to search for.
            urls (Optional[List[str]]): List of URLs for extract mode.

        Returns:
            List[Document]: List of documents.

        Raises:
            ValueError: If invalid combination of parameters is provided.

        """
        if sum(x is not None for x in [url, query, urls]) != 1:
            raise ValueError("Exactly one of url, query, or urls must be provided.")

        documents = []

        if self.mode == "scrape":
            # [SCRAPE] params: https://docs.firecrawl.dev/api-reference/endpoint/scrape
            if url is None:
                raise ValueError("URL must be provided for scrape mode.")
            firecrawl_docs = self.firecrawl.scrape_url(url, **self.params)
            documents.append(
                Document(
                    text=firecrawl_docs.get("markdown", ""),
                    metadata=firecrawl_docs.get("metadata", {}),
                )
            )
        elif self.mode == "crawl":
            # [CRAWL] params: https://docs.firecrawl.dev/api-reference/endpoint/crawl-post
            if url is None:
                raise ValueError("URL must be provided for crawl mode.")
            firecrawl_docs = self.firecrawl.crawl_url(url, **self.params)
            firecrawl_docs = firecrawl_docs.data
            for doc in firecrawl_docs:
                documents.append(
                    Document(
                        text=doc.get("markdown", ""),
                        metadata=doc.get("metadata", {}),
                    )
                )
        elif self.mode == "search":
            # [SEARCH] params: https://docs.firecrawl.dev/api-reference/endpoint/search
            if query is None:
                raise ValueError("Query must be provided for search mode.")

            # Remove query from params if it exists to avoid duplicate
            search_params = self.params.copy() if self.params else {}
            if "query" in search_params:
                del search_params["query"]

            # Get search results
            search_response = self.firecrawl.search(query, **search_params)

            # Handle the search response format
            if isinstance(search_response, dict):
                # Check for success
                if search_response.get("success", False):
                    # Get the data array
                    search_results = search_response.get("data", [])

                    # Process each search result
                    for result in search_results:
                        # Extract text content (prefer markdown if available)
                        text = result.get("markdown", "")
                        if not text:
                            # Fall back to description if markdown is not available
                            text = result.get("description", "")

                        # Extract metadata
                        metadata = {
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "description": result.get("description", ""),
                            "source": "search",
                            "query": query,
                        }

                        # Add additional metadata if available
                        if "metadata" in result and isinstance(
                            result["metadata"], dict
                        ):
                            metadata.update(result["metadata"])

                        # Create document
                        documents.append(
                            Document(
                                text=text,
                                metadata=metadata,
                            )
                        )
                else:
                    # Handle unsuccessful response
                    warning = search_response.get("warning", "Unknown error")
                    print(f"Search was unsuccessful: {warning}")
                    documents.append(
                        Document(
                            text=f"Search for '{query}' was unsuccessful: {warning}",
                            metadata={
                                "source": "search",
                                "query": query,
                                "error": warning,
                            },
                        )
                    )
            else:
                # Handle unexpected response format
                print(f"Unexpected search response format: {type(search_response)}")
                documents.append(
                    Document(
                        text=str(search_response),
                        metadata={"source": "search", "query": query},
                    )
                )
        elif self.mode == "extract":
            # [EXTRACT] params: https://docs.firecrawl.dev/api-reference/endpoint/extract
            if urls is None:
                # For backward compatibility, convert single URL to list if provided
                if url is not None:
                    urls = [url]
                else:
                    raise ValueError("URLs must be provided for extract mode.")

            # Ensure we have a prompt in params
            extract_params = self.params.copy() if self.params else {}
            if "prompt" not in extract_params:
                raise ValueError("A 'prompt' parameter is required for extract mode.")

            # Prepare the payload according to the new API structure
            payload = {"prompt": extract_params.pop("prompt")}

            # Call the extract method with the urls and params
            extract_response = self.firecrawl.extract(urls=urls, **payload)

            # Handle the extract response format
            if isinstance(extract_response, dict):
                # Check for success
                if extract_response.get("success", False):
                    # Get the data from the response
                    extract_data = extract_response.get("data", {})

                    # Get the sources if available
                    sources = extract_response.get("sources", {})

                    # Convert the extracted data to text
                    if extract_data:
                        # Convert the data to a formatted string
                        text_parts = []
                        for key, value in extract_data.items():
                            text_parts.append(f"{key}: {value}")

                        text = "\n".join(text_parts)

                        # Create metadata
                        metadata = {
                            "urls": urls,
                            "source": "extract",
                            "status": extract_response.get("status"),
                            "expires_at": extract_response.get("expiresAt"),
                        }

                        # Add sources to metadata if available
                        if sources:
                            metadata["sources"] = sources

                        # Create document
                        documents.append(
                            Document(
                                text=text,
                                metadata=metadata,
                            )
                        )
                    else:
                        # Handle empty data in successful response
                        print("Extract response successful but no data returned")
                        documents.append(
                            Document(
                                text="Extraction was successful but no data was returned",
                                metadata={"urls": urls, "source": "extract"},
                            )
                        )
                else:
                    # Handle unsuccessful response
                    warning = extract_response.get("warning", "Unknown error")
                    print(f"Extraction was unsuccessful: {warning}")
                    documents.append(
                        Document(
                            text=f"Extraction was unsuccessful: {warning}",
                            metadata={
                                "urls": urls,
                                "source": "extract",
                                "error": warning,
                            },
                        )
                    )
            else:
                # Handle unexpected response format
                print(f"Unexpected extract response format: {type(extract_response)}")
                documents.append(
                    Document(
                        text=str(extract_response),
                        metadata={"urls": urls, "source": "extract"},
                    )
                )
        else:
            raise ValueError(
                "Invalid mode. Please choose 'scrape', 'crawl', 'search', or 'extract'."
            )

        return documents

```
  
---|---  
###  load_data #
```
load_data(url: Optional[str] = None, query: Optional[str] = None, urls: Optional[List[str]] = None) -> List[Document]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url` |  `Optional[str]` |  URL to scrape or crawl. |  `None`  
`query` |  `Optional[str]` |  Query to search for. |  `None`  
`urls` |  `Optional[List[str]]` |  List of URLs for extract mode. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Raises:
Type | Description  
---|---  
`ValueError` |  If invalid combination of parameters is provided.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/firecrawl_web/base.py`

| ```
def load_data(
    self,
    url: Optional[str] = None,
    query: Optional[str] = None,
    urls: Optional[List[str]] = None,
) -> List[Document]:
    """
    Load data from the input directory.

    Args:
        url (Optional[str]): URL to scrape or crawl.
        query (Optional[str]): Query to search for.
        urls (Optional[List[str]]): List of URLs for extract mode.

    Returns:
        List[Document]: List of documents.

    Raises:
        ValueError: If invalid combination of parameters is provided.

    """
    if sum(x is not None for x in [url, query, urls]) != 1:
        raise ValueError("Exactly one of url, query, or urls must be provided.")

    documents = []

    if self.mode == "scrape":
        # [SCRAPE] params: https://docs.firecrawl.dev/api-reference/endpoint/scrape
        if url is None:
            raise ValueError("URL must be provided for scrape mode.")
        firecrawl_docs = self.firecrawl.scrape_url(url, **self.params)
        documents.append(
            Document(
                text=firecrawl_docs.get("markdown", ""),
                metadata=firecrawl_docs.get("metadata", {}),
            )
        )
    elif self.mode == "crawl":
        # [CRAWL] params: https://docs.firecrawl.dev/api-reference/endpoint/crawl-post
        if url is None:
            raise ValueError("URL must be provided for crawl mode.")
        firecrawl_docs = self.firecrawl.crawl_url(url, **self.params)
        firecrawl_docs = firecrawl_docs.data
        for doc in firecrawl_docs:
            documents.append(
                Document(
                    text=doc.get("markdown", ""),
                    metadata=doc.get("metadata", {}),
                )
            )
    elif self.mode == "search":
        # [SEARCH] params: https://docs.firecrawl.dev/api-reference/endpoint/search
        if query is None:
            raise ValueError("Query must be provided for search mode.")

        # Remove query from params if it exists to avoid duplicate
        search_params = self.params.copy() if self.params else {}
        if "query" in search_params:
            del search_params["query"]

        # Get search results
        search_response = self.firecrawl.search(query, **search_params)

        # Handle the search response format
        if isinstance(search_response, dict):
            # Check for success
            if search_response.get("success", False):
                # Get the data array
                search_results = search_response.get("data", [])

                # Process each search result
                for result in search_results:
                    # Extract text content (prefer markdown if available)
                    text = result.get("markdown", "")
                    if not text:
                        # Fall back to description if markdown is not available
                        text = result.get("description", "")

                    # Extract metadata
                    metadata = {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "description": result.get("description", ""),
                        "source": "search",
                        "query": query,
                    }

                    # Add additional metadata if available
                    if "metadata" in result and isinstance(
                        result["metadata"], dict
                    ):
                        metadata.update(result["metadata"])

                    # Create document
                    documents.append(
                        Document(
                            text=text,
                            metadata=metadata,
                        )
                    )
            else:
                # Handle unsuccessful response
                warning = search_response.get("warning", "Unknown error")
                print(f"Search was unsuccessful: {warning}")
                documents.append(
                    Document(
                        text=f"Search for '{query}' was unsuccessful: {warning}",
                        metadata={
                            "source": "search",
                            "query": query,
                            "error": warning,
                        },
                    )
                )
        else:
            # Handle unexpected response format
            print(f"Unexpected search response format: {type(search_response)}")
            documents.append(
                Document(
                    text=str(search_response),
                    metadata={"source": "search", "query": query},
                )
            )
    elif self.mode == "extract":
        # [EXTRACT] params: https://docs.firecrawl.dev/api-reference/endpoint/extract
        if urls is None:
            # For backward compatibility, convert single URL to list if provided
            if url is not None:
                urls = [url]
            else:
                raise ValueError("URLs must be provided for extract mode.")

        # Ensure we have a prompt in params
        extract_params = self.params.copy() if self.params else {}
        if "prompt" not in extract_params:
            raise ValueError("A 'prompt' parameter is required for extract mode.")

        # Prepare the payload according to the new API structure
        payload = {"prompt": extract_params.pop("prompt")}

        # Call the extract method with the urls and params
        extract_response = self.firecrawl.extract(urls=urls, **payload)

        # Handle the extract response format
        if isinstance(extract_response, dict):
            # Check for success
            if extract_response.get("success", False):
                # Get the data from the response
                extract_data = extract_response.get("data", {})

                # Get the sources if available
                sources = extract_response.get("sources", {})

                # Convert the extracted data to text
                if extract_data:
                    # Convert the data to a formatted string
                    text_parts = []
                    for key, value in extract_data.items():
                        text_parts.append(f"{key}: {value}")

                    text = "\n".join(text_parts)

                    # Create metadata
                    metadata = {
                        "urls": urls,
                        "source": "extract",
                        "status": extract_response.get("status"),
                        "expires_at": extract_response.get("expiresAt"),
                    }

                    # Add sources to metadata if available
                    if sources:
                        metadata["sources"] = sources

                    # Create document
                    documents.append(
                        Document(
                            text=text,
                            metadata=metadata,
                        )
                    )
                else:
                    # Handle empty data in successful response
                    print("Extract response successful but no data returned")
                    documents.append(
                        Document(
                            text="Extraction was successful but no data was returned",
                            metadata={"urls": urls, "source": "extract"},
                        )
                    )
            else:
                # Handle unsuccessful response
                warning = extract_response.get("warning", "Unknown error")
                print(f"Extraction was unsuccessful: {warning}")
                documents.append(
                    Document(
                        text=f"Extraction was unsuccessful: {warning}",
                        metadata={
                            "urls": urls,
                            "source": "extract",
                            "error": warning,
                        },
                    )
                )
        else:
            # Handle unexpected response format
            print(f"Unexpected extract response format: {type(extract_response)}")
            documents.append(
                Document(
                    text=str(extract_response),
                    metadata={"urls": urls, "source": "extract"},
                )
            )
    else:
        raise ValueError(
            "Invalid mode. Please choose 'scrape', 'crawl', 'search', or 'extract'."
        )

    return documents

```
  
---|---  
##  HyperbrowserWebReader #
Bases: `BaseReader`
Hyperbrowser Web Reader.
Scrape or crawl web pages with optional parameters for configuring content extraction. Requires the `hyperbrowser` package. Get your API Key from https://app.hyperbrowser.ai/
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`api_key` |  `Optional[str]` |  The Hyperbrowser API key, can be set as an environment variable `HYPERBROWSER_API_KEY` or passed directly |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/hyperbrowser_web/base.py`

| ```
class HyperbrowserWebReader(BaseReader):
    """
    Hyperbrowser Web Reader.

    Scrape or crawl web pages with optional parameters for configuring content extraction.
    Requires the `hyperbrowser` package.
    Get your API Key from https://app.hyperbrowser.ai/

    Args:
        api_key: The Hyperbrowser API key, can be set as an environment variable `HYPERBROWSER_API_KEY` or passed directly

    """

    def __init__(self, api_key: Optional[str] = None):
        api_key = api_key or os.getenv("HYPERBROWSER_API_KEY")
        if not api_key:
            raise ValueError(
                "`api_key` is required, please set the `HYPERBROWSER_API_KEY` environment variable or pass it directly"
            )

        try:
            from hyperbrowser import Hyperbrowser, AsyncHyperbrowser
        except ImportError:
            raise ImportError(
                "`hyperbrowser` package not found, please run `pip install hyperbrowser`"
            )

        self.hyperbrowser = Hyperbrowser(api_key=api_key)
        self.async_hyperbrowser = AsyncHyperbrowser(api_key=api_key)

    def _prepare_params(self, params: Dict) -> Dict:
        """Prepare session and scrape options parameters."""
        try:
            from hyperbrowser.models.session import CreateSessionParams
            from hyperbrowser.models.scrape import ScrapeOptions
        except ImportError:
            raise ImportError(
                "`hyperbrowser` package not found, please run `pip install hyperbrowser`"
            )

        if "scrape_options" in params:
            if "formats" in params["scrape_options"]:
                formats = params["scrape_options"]["formats"]
                if not all(fmt in ["markdown", "html"] for fmt in formats):
                    raise ValueError("formats can only contain 'markdown' or 'html'")

        if "session_options" in params:
            params["session_options"] = CreateSessionParams(**params["session_options"])
        if "scrape_options" in params:
            params["scrape_options"] = ScrapeOptions(**params["scrape_options"])
        return params

    def _create_document(self, content: str, metadata: dict) -> Document:
        """Create a Document with text and metadata."""
        return Document(text=content, metadata=metadata)

    def _extract_content_metadata(self, data: Union[Any, None]):
        """Extract content and metadata from response data."""
        content = ""
        metadata = {}
        if data:
            content = data.markdown or data.html or ""
            if data.metadata:
                metadata = data.metadata
        return content, metadata

    def lazy_load_data(
        self,
        urls: List[str],
        operation: Literal["scrape", "crawl"] = "scrape",
        params: Optional[Dict] = {},
    ) -> Iterable[Document]:
        """
        Lazy load documents.

        Args:
            urls: List of URLs to scrape or crawl
            operation: Operation to perform. Can be "scrape" or "crawl"
            params: Optional params for scrape or crawl. For more information on the supported params, visit https://docs.hyperbrowser.ai/reference/sdks/python/scrape#start-scrape-job-and-wait or https://docs.hyperbrowser.ai/reference/sdks/python/crawl#start-crawl-job-and-wait

        """
        try:
            from hyperbrowser.models.scrape import StartScrapeJobParams
            from hyperbrowser.models.crawl import StartCrawlJobParams
        except ImportError:
            raise ImportError(
                "`hyperbrowser` package not found, please run `pip install hyperbrowser`"
            )

        if operation == "crawl" and len(urls) > 1:
            raise ValueError("`crawl` operation can only accept a single URL")
        params = self._prepare_params(params)

        if operation == "scrape":
            for url in urls:
                scrape_params = StartScrapeJobParams(url=url, **params)
                try:
                    scrape_resp = self.hyperbrowser.scrape.start_and_wait(scrape_params)
                    content, metadata = self._extract_content_metadata(scrape_resp.data)
                    yield self._create_document(content, metadata)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    yield self._create_document("", {})
        else:
            crawl_params = StartCrawlJobParams(url=urls[0], **params)
            try:
                crawl_resp = self.hyperbrowser.crawl.start_and_wait(crawl_params)
                for page in crawl_resp.data:
                    content = page.markdown or page.html or ""
                    yield self._create_document(content, page.metadata or {})
            except Exception as e:
                logger.error(f"Error crawling {urls[0]}: {e}")
                yield self._create_document("", {})

    async def alazy_load_data(
        self,
        urls: Sequence[str],
        operation: Literal["scrape", "crawl"] = "scrape",
        params: Optional[Dict] = {},
    ) -> AsyncIterable[Document]:
        """
        Async lazy load documents.

        Args:
            urls: List of URLs to scrape or crawl
            operation: Operation to perform. Can be "scrape" or "crawl"
            params: Optional params for scrape or crawl. For more information on the supported params, visit https://docs.hyperbrowser.ai/reference/sdks/python/scrape#start-scrape-job-and-wait or https://docs.hyperbrowser.ai/reference/sdks/python/crawl#start-crawl-job-and-wait

        """
        try:
            from hyperbrowser.models.scrape import StartScrapeJobParams
            from hyperbrowser.models.crawl import StartCrawlJobParams
        except ImportError:
            raise ImportError(
                "`hyperbrowser` package not found, please run `pip install hyperbrowser`"
            )

        if operation == "crawl" and len(urls) > 1:
            raise ValueError("`crawl` operation can only accept a single URL")
        params = self._prepare_params(params)

        if operation == "scrape":
            for url in urls:
                scrape_params = StartScrapeJobParams(url=url, **params)
                try:
                    scrape_resp = await self.async_hyperbrowser.scrape.start_and_wait(
                        scrape_params
                    )
                    content, metadata = self._extract_content_metadata(scrape_resp.data)
                    yield self._create_document(content, metadata)
                except Exception as e:
                    logger.error(f"Error scraping {url}: {e}")
                    yield self._create_document("", {})
        else:
            crawl_params = StartCrawlJobParams(url=urls[0], **params)
            try:
                crawl_resp = await self.async_hyperbrowser.crawl.start_and_wait(
                    crawl_params
                )
                for page in crawl_resp.data:
                    content = page.markdown or page.html or ""
                    yield self._create_document(content, page.metadata or {})
            except Exception as e:
                logger.error(f"Error crawling {urls[0]}: {e}")
                yield self._create_document("", {})

```
  
---|---  
###  lazy_load_data #
```
lazy_load_data(urls: List[str], operation: Literal['scrape', 'crawl'] = 'scrape', params: Optional[Dict] = {}) -> Iterable[Document]

```

Lazy load documents.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of URLs to scrape or crawl |  _required_  
`operation` |  `Literal['scrape', 'crawl']` |  Operation to perform. Can be "scrape" or "crawl" |  `'scrape'`  
`params` |  `Optional[Dict]` |  Optional params for scrape or crawl. For more information on the supported params, visit https://docs.hyperbrowser.ai/reference/sdks/python/scrape#start-scrape-job-and-wait or https://docs.hyperbrowser.ai/reference/sdks/python/crawl#start-crawl-job-and-wait |  `{}`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/hyperbrowser_web/base.py`

| ```
def lazy_load_data(
    self,
    urls: List[str],
    operation: Literal["scrape", "crawl"] = "scrape",
    params: Optional[Dict] = {},
) -> Iterable[Document]:
    """
    Lazy load documents.

    Args:
        urls: List of URLs to scrape or crawl
        operation: Operation to perform. Can be "scrape" or "crawl"
        params: Optional params for scrape or crawl. For more information on the supported params, visit https://docs.hyperbrowser.ai/reference/sdks/python/scrape#start-scrape-job-and-wait or https://docs.hyperbrowser.ai/reference/sdks/python/crawl#start-crawl-job-and-wait

    """
    try:
        from hyperbrowser.models.scrape import StartScrapeJobParams
        from hyperbrowser.models.crawl import StartCrawlJobParams
    except ImportError:
        raise ImportError(
            "`hyperbrowser` package not found, please run `pip install hyperbrowser`"
        )

    if operation == "crawl" and len(urls) > 1:
        raise ValueError("`crawl` operation can only accept a single URL")
    params = self._prepare_params(params)

    if operation == "scrape":
        for url in urls:
            scrape_params = StartScrapeJobParams(url=url, **params)
            try:
                scrape_resp = self.hyperbrowser.scrape.start_and_wait(scrape_params)
                content, metadata = self._extract_content_metadata(scrape_resp.data)
                yield self._create_document(content, metadata)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                yield self._create_document("", {})
    else:
        crawl_params = StartCrawlJobParams(url=urls[0], **params)
        try:
            crawl_resp = self.hyperbrowser.crawl.start_and_wait(crawl_params)
            for page in crawl_resp.data:
                content = page.markdown or page.html or ""
                yield self._create_document(content, page.metadata or {})
        except Exception as e:
            logger.error(f"Error crawling {urls[0]}: {e}")
            yield self._create_document("", {})

```
  
---|---  
###  alazy_load_data `async` #
```
alazy_load_data(urls: Sequence[str], operation: Literal['scrape', 'crawl'] = 'scrape', params: Optional[Dict] = {}) -> AsyncIterable[Document]

```

Async lazy load documents.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `Sequence[str]` |  List of URLs to scrape or crawl |  _required_  
`operation` |  `Literal['scrape', 'crawl']` |  Operation to perform. Can be "scrape" or "crawl" |  `'scrape'`  
`params` |  `Optional[Dict]` |  Optional params for scrape or crawl. For more information on the supported params, visit https://docs.hyperbrowser.ai/reference/sdks/python/scrape#start-scrape-job-and-wait or https://docs.hyperbrowser.ai/reference/sdks/python/crawl#start-crawl-job-and-wait |  `{}`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/hyperbrowser_web/base.py`

| ```
async def alazy_load_data(
    self,
    urls: Sequence[str],
    operation: Literal["scrape", "crawl"] = "scrape",
    params: Optional[Dict] = {},
) -> AsyncIterable[Document]:
    """
    Async lazy load documents.

    Args:
        urls: List of URLs to scrape or crawl
        operation: Operation to perform. Can be "scrape" or "crawl"
        params: Optional params for scrape or crawl. For more information on the supported params, visit https://docs.hyperbrowser.ai/reference/sdks/python/scrape#start-scrape-job-and-wait or https://docs.hyperbrowser.ai/reference/sdks/python/crawl#start-crawl-job-and-wait

    """
    try:
        from hyperbrowser.models.scrape import StartScrapeJobParams
        from hyperbrowser.models.crawl import StartCrawlJobParams
    except ImportError:
        raise ImportError(
            "`hyperbrowser` package not found, please run `pip install hyperbrowser`"
        )

    if operation == "crawl" and len(urls) > 1:
        raise ValueError("`crawl` operation can only accept a single URL")
    params = self._prepare_params(params)

    if operation == "scrape":
        for url in urls:
            scrape_params = StartScrapeJobParams(url=url, **params)
            try:
                scrape_resp = await self.async_hyperbrowser.scrape.start_and_wait(
                    scrape_params
                )
                content, metadata = self._extract_content_metadata(scrape_resp.data)
                yield self._create_document(content, metadata)
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                yield self._create_document("", {})
    else:
        crawl_params = StartCrawlJobParams(url=urls[0], **params)
        try:
            crawl_resp = await self.async_hyperbrowser.crawl.start_and_wait(
                crawl_params
            )
            for page in crawl_resp.data:
                content = page.markdown or page.html or ""
                yield self._create_document(content, page.metadata or {})
        except Exception as e:
            logger.error(f"Error crawling {urls[0]}: {e}")
            yield self._create_document("", {})

```
  
---|---  
##  KnowledgeBaseWebReader #
Bases: `BaseReader`
Knowledge base reader.
Crawls and reads articles from a knowledge base/help center with Playwright. Tested on Zendesk and Intercom CMS, may work on others. Can be run in headless mode but it may be blocked by Cloudflare. Run it headed to be safe. Times out occasionally, just increase the default time out if it does. Requires the `playwright` package.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`root_url` |  `str` |  the base url of the knowledge base, with no trailing slash e.g. 'https://support.intercom.com' |  _required_  
`link_selectors` |  `List[str]` |  list of css selectors to find links to articles while crawling e.g. ['.article-list a', '.article-list a'] |  _required_  
`article_path` |  `str` |  the url path of articles on this domain so the crawler knows when to stop e.g. '/articles' |  _required_  
`title_selector` |  `Optional[str]` |  css selector to find the title of the article e.g. '.article-title' |  `None`  
`subtitle_selector` |  `Optional[str]` |  css selector to find the subtitle/description of the article e.g. '.article-subtitle' |  `None`  
`body_selector` |  `Optional[str]` |  css selector to find the body of the article e.g. '.article-body' |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/knowledge_base/base.py`

| ```
class KnowledgeBaseWebReader(BaseReader):
    """
    Knowledge base reader.

    Crawls and reads articles from a knowledge base/help center with Playwright.
    Tested on Zendesk and Intercom CMS, may work on others.
    Can be run in headless mode but it may be blocked by Cloudflare. Run it headed to be safe.
    Times out occasionally, just increase the default time out if it does.
    Requires the `playwright` package.

    Args:
        root_url (str): the base url of the knowledge base, with no trailing slash
            e.g. 'https://support.intercom.com'
        link_selectors (List[str]): list of css selectors to find links to articles while crawling
            e.g. ['.article-list a', '.article-list a']
        article_path (str): the url path of articles on this domain so the crawler knows when to stop
            e.g. '/articles'
        title_selector (Optional[str]): css selector to find the title of the article
            e.g. '.article-title'
        subtitle_selector (Optional[str]): css selector to find the subtitle/description of the article
            e.g. '.article-subtitle'
        body_selector (Optional[str]): css selector to find the body of the article
            e.g. '.article-body'

    """

    def __init__(
        self,
        root_url: str,
        link_selectors: List[str],
        article_path: str,
        title_selector: Optional[str] = None,
        subtitle_selector: Optional[str] = None,
        body_selector: Optional[str] = None,
        max_depth: int = 100,
    ) -> None:
        """Initialize with parameters."""
        self.root_url = root_url
        self.link_selectors = link_selectors
        self.article_path = article_path
        self.title_selector = title_selector
        self.subtitle_selector = subtitle_selector
        self.body_selector = body_selector
        self.max_depth = max_depth

    def load_data(self) -> List[Document]:
        """Load data from the knowledge base."""
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)

            # Crawl
            article_urls = self.get_article_urls(
                browser, self.root_url, self.root_url, self.max_depth
            )

            # Scrape
            documents = []
            for url in article_urls:
                article = self.scrape_article(
                    browser,
                    url,
                )
                extra_info = {
                    "title": article["title"],
                    "subtitle": article["subtitle"],
                    "url": article["url"],
                }
                documents.append(Document(text=article["body"], extra_info=extra_info))

            browser.close()

            return documents

    def scrape_article(
        self,
        browser: Any,
        url: str,
    ) -> Dict[str, str]:
        """
        Scrape a single article url.

        Args:
            browser (Any): a Playwright Chromium browser.
            url (str): URL of the article to scrape.

        Returns:
            Dict[str, str]: a mapping of article attributes to their values.

        """
        page = browser.new_page(ignore_https_errors=True)
        page.set_default_timeout(60000)
        page.goto(url, wait_until="domcontentloaded")

        title = (
            (
                page.query_selector(self.title_selector).evaluate(
                    "node => node.innerText"
                )
            )
            if self.title_selector
            else ""
        )
        subtitle = (
            (
                page.query_selector(self.subtitle_selector).evaluate(
                    "node => node.innerText"
                )
            )
            if self.subtitle_selector
            else ""
        )
        body = (
            (page.query_selector(self.body_selector).evaluate("node => node.innerText"))
            if self.body_selector
            else ""
        )

        page.close()
        print("scraped:", url)
        return {"title": title, "subtitle": subtitle, "body": body, "url": url}

    def get_article_urls(
        self,
        browser: Any,
        root_url: str,
        current_url: str,
        max_depth: int = 100,
        depth: int = 0,
    ) -> List[str]:
        """
        Recursively crawl through the knowledge base to find a list of articles.

        Args:
            browser (Any): a Playwright Chromium browser.
            root_url (str): root URL of the knowledge base.
            current_url (str): current URL that is being crawled.
            max_depth (int): maximum recursion level for the crawler
            depth (int): current depth level

        Returns:
            List[str]: a list of URLs of found articles.

        """
        if depth >= max_depth:
            print(f"Reached max depth ({max_depth}): {current_url}")
            return []

        page = browser.new_page(ignore_https_errors=True)
        page.set_default_timeout(60000)
        page.goto(current_url, wait_until="domcontentloaded")

        # If this is a leaf node aka article page, return itself
        if self.article_path in current_url:
            print("Found an article: ", current_url)
            page.close()
            return [current_url]

        # Otherwise crawl this page and find all the articles linked from it
        article_urls = []
        links = []

        for link_selector in self.link_selectors:
            ahrefs = page.query_selector_all(link_selector)
            links.extend(ahrefs)

        for link in links:
            url = root_url + page.evaluate("(node) => node.getAttribute('href')", link)
            article_urls.extend(
                self.get_article_urls(browser, root_url, url, max_depth, depth + 1)
            )

        page.close()

        return article_urls

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Load data from the knowledge base.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/knowledge_base/base.py`

| ```
def load_data(self) -> List[Document]:
    """Load data from the knowledge base."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        # Crawl
        article_urls = self.get_article_urls(
            browser, self.root_url, self.root_url, self.max_depth
        )

        # Scrape
        documents = []
        for url in article_urls:
            article = self.scrape_article(
                browser,
                url,
            )
            extra_info = {
                "title": article["title"],
                "subtitle": article["subtitle"],
                "url": article["url"],
            }
            documents.append(Document(text=article["body"], extra_info=extra_info))

        browser.close()

        return documents

```
  
---|---  
###  scrape_article #
```
scrape_article(browser: Any, url: str) -> Dict[str, str]

```

Scrape a single article url.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`browser` |  `Any` |  a Playwright Chromium browser. |  _required_  
`url` |  `str` |  URL of the article to scrape. |  _required_  
Returns:
Type | Description  
---|---  
`Dict[str, str]` |  Dict[str, str]: a mapping of article attributes to their values.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/knowledge_base/base.py`

| ```
def scrape_article(
    self,
    browser: Any,
    url: str,
) -> Dict[str, str]:
    """
    Scrape a single article url.

    Args:
        browser (Any): a Playwright Chromium browser.
        url (str): URL of the article to scrape.

    Returns:
        Dict[str, str]: a mapping of article attributes to their values.

    """
    page = browser.new_page(ignore_https_errors=True)
    page.set_default_timeout(60000)
    page.goto(url, wait_until="domcontentloaded")

    title = (
        (
            page.query_selector(self.title_selector).evaluate(
                "node => node.innerText"
            )
        )
        if self.title_selector
        else ""
    )
    subtitle = (
        (
            page.query_selector(self.subtitle_selector).evaluate(
                "node => node.innerText"
            )
        )
        if self.subtitle_selector
        else ""
    )
    body = (
        (page.query_selector(self.body_selector).evaluate("node => node.innerText"))
        if self.body_selector
        else ""
    )

    page.close()
    print("scraped:", url)
    return {"title": title, "subtitle": subtitle, "body": body, "url": url}

```
  
---|---  
###  get_article_urls #
```
get_article_urls(browser: Any, root_url: str, current_url: str, max_depth: int = 100, depth: int = 0) -> List[str]

```

Recursively crawl through the knowledge base to find a list of articles.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`browser` |  `Any` |  a Playwright Chromium browser. |  _required_  
`root_url` |  `str` |  root URL of the knowledge base. |  _required_  
`current_url` |  `str` |  current URL that is being crawled. |  _required_  
`max_depth` |  `int` |  maximum recursion level for the crawler |  `100`  
`depth` |  `int` |  current depth level |  `0`  
Returns:
Type | Description  
---|---  
`List[str]` |  List[str]: a list of URLs of found articles.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/knowledge_base/base.py`

| ```
def get_article_urls(
    self,
    browser: Any,
    root_url: str,
    current_url: str,
    max_depth: int = 100,
    depth: int = 0,
) -> List[str]:
    """
    Recursively crawl through the knowledge base to find a list of articles.

    Args:
        browser (Any): a Playwright Chromium browser.
        root_url (str): root URL of the knowledge base.
        current_url (str): current URL that is being crawled.
        max_depth (int): maximum recursion level for the crawler
        depth (int): current depth level

    Returns:
        List[str]: a list of URLs of found articles.

    """
    if depth >= max_depth:
        print(f"Reached max depth ({max_depth}): {current_url}")
        return []

    page = browser.new_page(ignore_https_errors=True)
    page.set_default_timeout(60000)
    page.goto(current_url, wait_until="domcontentloaded")

    # If this is a leaf node aka article page, return itself
    if self.article_path in current_url:
        print("Found an article: ", current_url)
        page.close()
        return [current_url]

    # Otherwise crawl this page and find all the articles linked from it
    article_urls = []
    links = []

    for link_selector in self.link_selectors:
        ahrefs = page.query_selector_all(link_selector)
        links.extend(ahrefs)

    for link in links:
        url = root_url + page.evaluate("(node) => node.getAttribute('href')", link)
        article_urls.extend(
            self.get_article_urls(browser, root_url, url, max_depth, depth + 1)
        )

    page.close()

    return article_urls

```
  
---|---  
##  MainContentExtractorReader #
Bases: `BaseReader`
MainContentExtractor web page reader.
Reads pages from the web.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`text_format` |  `str` |  The format of the text. Defaults to "markdown". Requires `MainContentExtractor` package. |  `'markdown'`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/main_content_extractor/base.py`

| ```
class MainContentExtractorReader(BaseReader):
    """
    MainContentExtractor web page reader.

    Reads pages from the web.

    Args:
        text_format (str, optional): The format of the text. Defaults to "markdown".
            Requires `MainContentExtractor` package.

    """

    def __init__(self, text_format: str = "markdown") -> None:
        """Initialize with parameters."""
        self.text_format = text_format

    def load_data(self, urls: List[str]) -> List[Document]:
        """
        Load data from the input directory.

        Args:
            urls (List[str]): List of URLs to scrape.

        Returns:
            List[Document]: List of documents.

        """
        if not isinstance(urls, list):
            raise ValueError("urls must be a list of strings.")

        from main_content_extractor import MainContentExtractor

        documents = []
        for url in urls:
            response = requests.get(url).text
            response = MainContentExtractor.extract(
                response, output_format=self.text_format, include_links=False
            )

            documents.append(Document(text=response))

        return documents

```
  
---|---  
###  load_data #
```
load_data(urls: List[str]) -> List[Document]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of URLs to scrape. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/main_content_extractor/base.py`

| ```
def load_data(self, urls: List[str]) -> List[Document]:
    """
    Load data from the input directory.

    Args:
        urls (List[str]): List of URLs to scrape.

    Returns:
        List[Document]: List of documents.

    """
    if not isinstance(urls, list):
        raise ValueError("urls must be a list of strings.")

    from main_content_extractor import MainContentExtractor

    documents = []
    for url in urls:
        response = requests.get(url).text
        response = MainContentExtractor.extract(
            response, output_format=self.text_format, include_links=False
        )

        documents.append(Document(text=response))

    return documents

```
  
---|---  
##  NewsArticleReader #
Bases: `BaseReader`
Simple news article reader.
Reads news articles from the web and parses them using the `newspaper` library.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`text_mode` |  `bool` |  Whether to load a text version or HTML version of the content (default=True). |  `True`  
`use_nlp` |  `bool` |  Whether to use NLP to extract additional summary and keywords (default=True). |  `True`  
`newspaper_kwargs` |  `Any` |  Additional keyword arguments to pass to newspaper.Article. See https://newspaper.readthedocs.io/en/latest/user_guide/quickstart.html#article |  `{}`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/news/base.py`

| ```
class NewsArticleReader(BaseReader):
    """
    Simple news article reader.

    Reads news articles from the web and parses them using the `newspaper` library.

    Args:
        text_mode (bool): Whether to load a text version or HTML version of the content (default=True).
        use_nlp (bool): Whether to use NLP to extract additional summary and keywords (default=True).
        newspaper_kwargs: Additional keyword arguments to pass to newspaper.Article. See
            https://newspaper.readthedocs.io/en/latest/user_guide/quickstart.html#article

    """

    def __init__(
        self, text_mode: bool = True, use_nlp: bool = True, **newspaper_kwargs: Any
    ) -> None:
        """Initialize with parameters."""
        if find_spec("newspaper") is None:
            raise ImportError(
                "`newspaper` package not found, please run `pip install newspaper3k`"
            )
        self.load_text = text_mode
        self.use_nlp = use_nlp
        self.newspaper_kwargs = newspaper_kwargs

    def load_data(self, urls: List[str]) -> List[Document]:
        """
        Load data from the list of news article urls.

        Args:
            urls (List[str]): List of URLs to load news articles.

        Returns:
            List[Document]: List of documents.

        """
        if not isinstance(urls, list) and not isinstance(urls, Generator):
            raise ValueError("urls must be a list or generator.")
        documents = []
        for url in urls:
            from newspaper import Article

            try:
                article = Article(url, **self.newspaper_kwargs)
                article.download()
                article.parse()

                if self.use_nlp:
                    article.nlp()

            except Exception as e:
                logger.error(f"Error fetching or processing {url}, exception: {e}")
                continue

            metadata = {
                "title": getattr(article, "title", ""),
                "link": getattr(article, "url", getattr(article, "canonical_link", "")),
                "authors": getattr(article, "authors", []),
                "language": getattr(article, "meta_lang", ""),
                "description": getattr(article, "meta_description", ""),
                "publish_date": getattr(article, "publish_date", ""),
            }

            if self.load_text:
                content = article.text
            else:
                content = article.html

            if self.use_nlp:
                metadata["keywords"] = getattr(article, "keywords", [])
                metadata["summary"] = getattr(article, "summary", "")

            documents.append(Document(text=content, metadata=metadata))

        return documents

```
  
---|---  
###  load_data #
```
load_data(urls: List[str]) -> List[Document]

```

Load data from the list of news article urls.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of URLs to load news articles. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/news/base.py`

| ```
def load_data(self, urls: List[str]) -> List[Document]:
    """
    Load data from the list of news article urls.

    Args:
        urls (List[str]): List of URLs to load news articles.

    Returns:
        List[Document]: List of documents.

    """
    if not isinstance(urls, list) and not isinstance(urls, Generator):
        raise ValueError("urls must be a list or generator.")
    documents = []
    for url in urls:
        from newspaper import Article

        try:
            article = Article(url, **self.newspaper_kwargs)
            article.download()
            article.parse()

            if self.use_nlp:
                article.nlp()

        except Exception as e:
            logger.error(f"Error fetching or processing {url}, exception: {e}")
            continue

        metadata = {
            "title": getattr(article, "title", ""),
            "link": getattr(article, "url", getattr(article, "canonical_link", "")),
            "authors": getattr(article, "authors", []),
            "language": getattr(article, "meta_lang", ""),
            "description": getattr(article, "meta_description", ""),
            "publish_date": getattr(article, "publish_date", ""),
        }

        if self.load_text:
            content = article.text
        else:
            content = article.html

        if self.use_nlp:
            metadata["keywords"] = getattr(article, "keywords", [])
            metadata["summary"] = getattr(article, "summary", "")

        documents.append(Document(text=content, metadata=metadata))

    return documents

```
  
---|---  
##  OxylabsWebReader #
Bases: `BasePydanticReader`
Scrape any website with Oxylabs Scraper.
Oxylabs API documentation: https://developers.oxylabs.io/scraper-apis/web-scraper-api/other-websites
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`username` |  `str` |  Oxylabs username. |  _required_  
`password` |  `str` |  Oxylabs password. |  _required_  
Example
.. code-block:: python from llama_index.readers.web.oxylabs_web.base import OxylabsWebReader
```
reader = OxylabsWebReader(
    username=os.environ["OXYLABS_USERNAME"], password=os.environ["OXYLABS_PASSWORD"]
)

docs = reader.load_data(
    [
        "https://sandbox.oxylabs.io/products/1",
        "https://sandbox.oxylabs.io/products/2"
    ],
    {
        "parse": True,
    }
)

print(docs[0].text)

```
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/oxylabs_web/base.py`

| ```
class OxylabsWebReader(BasePydanticReader):
    """
    Scrape any website with Oxylabs Scraper.

    Oxylabs API documentation:
    https://developers.oxylabs.io/scraper-apis/web-scraper-api/other-websites

    Args:
        username: Oxylabs username.
        password: Oxylabs password.

    Example:
        .. code-block:: python
            from llama_index.readers.web.oxylabs_web.base import OxylabsWebReader

            reader = OxylabsWebReader(
                username=os.environ["OXYLABS_USERNAME"], password=os.environ["OXYLABS_PASSWORD"]
            )

            docs = reader.load_data(
                [
                    "https://sandbox.oxylabs.io/products/1",
                    "https://sandbox.oxylabs.io/products/2"
                ],
                {
                    "parse": True,
                }
            )

            print(docs[0].text)

    """

    timeout_s: int = 100
    oxylabs_scraper_url: str = "https://realtime.oxylabs.io/v1/queries"
    api: "RealtimeAPI"
    async_api: "AsyncAPI"
    default_config: dict[str, Any] = Field(default_factory=get_default_config)

    def __init__(self, username: str, password: str, **kwargs) -> None:
        from oxylabs.internal.api import AsyncAPI, APICredentials, RealtimeAPI

        credentials = APICredentials(username=username, password=password)

        bits, _ = architecture()
        sdk_type = (
            f"oxylabs-llama-index-web-sdk-python/"
            f"{version('llama-index-readers-web')} "
            f"({python_version()}; {bits})"
        )

        api = RealtimeAPI(credentials, sdk_type=sdk_type)
        async_api = AsyncAPI(credentials, sdk_type=sdk_type)

        super().__init__(api=api, async_api=async_api, **kwargs)

    @classmethod
    def class_name(cls) -> str:
        return "OxylabsWebReader"

    def _get_document_from_response(self, response: dict[str, Any]) -> Document:
        content = response["results"][0]["content"]

        if isinstance(content, (dict, list)):
            text = json_to_markdown(content)
        else:
            striped_html = strip_html(str(content))
            text = markdownify(striped_html)

        return Document(
            metadata={"oxylabs_job": response["job"]},
            text=text,
        )

    async def aload_data(
        self,
        urls: list[str],
        additional_params: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Asynchronously load data from urls.

        Args:
            urls: List of URLs to load.
            additional_params: Dictionary with the scraper parameters. Accepts the values from
                the additional parameters described here:
                https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/generic-target#additional

        """
        if additional_params is None:
            additional_params = {}

        responses = await asyncio.gather(
            *[
                self.async_api.get_response(
                    {**additional_params, "url": url},
                    self.default_config,
                )
                for url in urls
            ]
        )

        return [
            self._get_document_from_response(response)
            for response in responses
            if response
        ]

    def load_data(
        self,
        urls: list[str],
        additional_params: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Load data from urls.

        Args:
            urls: List of URLs to load.
            additional_params: Dictionary with the scraper parameters. Accepts the values from
                the additional parameters described here:
                https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/generic-target#additional

        """
        if additional_params is None:
            additional_params = {}

        responses = [
            self.api.get_response(
                {**additional_params, "url": url},
                self.default_config,
            )
            for url in urls
        ]

        return [
            self._get_document_from_response(response)
            for response in responses
            if response
        ]

```
  
---|---  
###  aload_data `async` #
```
aload_data(urls: list[str], additional_params: Optional[Dict[str, Any]] = None) -> List[Document]

```

Asynchronously load data from urls.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `list[str]` |  List of URLs to load. |  _required_  
`additional_params` |  `Optional[Dict[str, Any]]` |  Dictionary with the scraper parameters. Accepts the values from the additional parameters described here: https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/generic-target#additional |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/oxylabs_web/base.py`

| ```
async def aload_data(
    self,
    urls: list[str],
    additional_params: Optional[Dict[str, Any]] = None,
) -> List[Document]:
    """
    Asynchronously load data from urls.

    Args:
        urls: List of URLs to load.
        additional_params: Dictionary with the scraper parameters. Accepts the values from
            the additional parameters described here:
            https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/generic-target#additional

    """
    if additional_params is None:
        additional_params = {}

    responses = await asyncio.gather(
        *[
            self.async_api.get_response(
                {**additional_params, "url": url},
                self.default_config,
            )
            for url in urls
        ]
    )

    return [
        self._get_document_from_response(response)
        for response in responses
        if response
    ]

```
  
---|---  
###  load_data #
```
load_data(urls: list[str], additional_params: Optional[Dict[str, Any]] = None) -> List[Document]

```

Load data from urls.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `list[str]` |  List of URLs to load. |  _required_  
`additional_params` |  `Optional[Dict[str, Any]]` |  Dictionary with the scraper parameters. Accepts the values from the additional parameters described here: https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/generic-target#additional |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/oxylabs_web/base.py`

| ```
def load_data(
    self,
    urls: list[str],
    additional_params: Optional[Dict[str, Any]] = None,
) -> List[Document]:
    """
    Load data from urls.

    Args:
        urls: List of URLs to load.
        additional_params: Dictionary with the scraper parameters. Accepts the values from
            the additional parameters described here:
            https://developers.oxylabs.io/scraper-apis/web-scraper-api/targets/generic-target#additional

    """
    if additional_params is None:
        additional_params = {}

    responses = [
        self.api.get_response(
            {**additional_params, "url": url},
            self.default_config,
        )
        for url in urls
    ]

    return [
        self._get_document_from_response(response)
        for response in responses
        if response
    ]

```
  
---|---  
##  ReadabilityWebPageReader #
Bases: `BaseReader`
Readability Webpage Loader.
Extracting relevant information from a fully rendered web page. During the processing, it is always assumed that web pages used as data sources contain textual content.
  1. Load the page and wait for it rendered. (playwright)
  2. Inject Readability.js to extract the main content.


Parameters:
Name | Type | Description | Default  
---|---|---|---  
`proxy` |  `Optional[str]` |  Proxy server. Defaults to None. |  `None`  
`wait_until` |  `Optional[Literal['commit', 'domcontentloaded', 'load', 'networkidle']]` |  Wait until the page is loaded. Defaults to "domcontentloaded". |  `'domcontentloaded'`  
`text_splitter` |  `TextSplitter` |  Text splitter. Defaults to None. |  `None`  
`normalizer` |  `Optional[Callable[[str], str]]` |  Text normalizer. Defaults to nfkc_normalize. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/readability_web/base.py`

| ```
class ReadabilityWebPageReader(BaseReader):
    """
    Readability Webpage Loader.

    Extracting relevant information from a fully rendered web page.
    During the processing, it is always assumed that web pages used as data sources contain textual content.

    1. Load the page and wait for it rendered. (playwright)
    2. Inject Readability.js to extract the main content.

    Args:
        proxy (Optional[str], optional): Proxy server. Defaults to None.
        wait_until (Optional[Literal["commit", "domcontentloaded", "load", "networkidle"]], optional): Wait until the page is loaded. Defaults to "domcontentloaded".
        text_splitter (TextSplitter, optional): Text splitter. Defaults to None.
        normalizer (Optional[Callable[[str], str]], optional): Text normalizer. Defaults to nfkc_normalize.

    """

    def __init__(
        self,
        proxy: Optional[str] = None,
        wait_until: Optional[
            Literal["commit", "domcontentloaded", "load", "networkidle"]
        ] = "domcontentloaded",
        text_splitter: Optional[TextSplitter] = None,
        normalize: Optional[Callable[[str], str]] = nfkc_normalize,
    ) -> None:
        self._launch_options = {
            "headless": True,
        }
        self._wait_until = wait_until
        if proxy:
            self._launch_options["proxy"] = {
                "server": proxy,
            }
        self._text_splitter = text_splitter
        self._normalize = normalize
        self._readability_js = None

    async def async_load_data(self, url: str) -> List[Document]:
        """
        Render and load data content from url.

        Args:
            url (str): URL to scrape.

        Returns:
            List[Document]: List of documents.

        """
        from playwright.async_api import async_playwright

        async with async_playwright() as async_playwright:
            browser = await async_playwright.chromium.launch(**self._launch_options)

            article = await self.scrape_page(
                browser,
                url,
            )
            extra_info = {
                key: article[key]
                for key in [
                    "title",
                    "length",
                    "excerpt",
                    "byline",
                    "dir",
                    "lang",
                    "siteName",
                ]
            }

            if self._normalize is not None:
                article["textContent"] = self._normalize(article["textContent"])
            texts = []
            if self._text_splitter is not None:
                texts = self._text_splitter.split_text(article["textContent"])
            else:
                texts = [article["textContent"]]

            await browser.close()

            return [Document(text=x, extra_info=extra_info) for x in texts]

    def load_data(self, url: str) -> List[Document]:
        return async_to_sync(self.async_load_data(url))

    async def scrape_page(
        self,
        browser: Browser,
        url: str,
    ) -> Dict[str, str]:
        """
        Scrape a single article url.

        Args:
            browser (Any): a Playwright Chromium browser.
            url (str): URL of the article to scrape.

        Returns:
            Ref: https://github.com/mozilla/readability
            title: article title;
            content: HTML string of processed article content;
            textContent: text content of the article, with all the HTML tags removed;
            length: length of an article, in characters;
            excerpt: article description, or short excerpt from the content;
            byline: author metadata;
            dir: content direction;
            siteName: name of the site.
            lang: content language

        """
        if self._readability_js is None:
            with open(path) as f:
                self._readability_js = f.read()

        inject_readability = f"""
            (function(){{
            {self._readability_js}
            function executor() {{
                return new Readability({{}}, document).parse();
            }}
            return executor();
            }}())
        """

        # browser = cast(Browser, browser)
        page = await browser.new_page(ignore_https_errors=True)
        page.set_default_timeout(60000)
        await page.goto(url, wait_until=self._wait_until)

        r = await page.evaluate(inject_readability)

        await page.close()
        print("scraped:", url)

        return r

```
  
---|---  
###  async_load_data `async` #
```
async_load_data(url: str) -> List[Document]

```

Render and load data content from url.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url` |  `str` |  URL to scrape. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/readability_web/base.py`

| ```
async def async_load_data(self, url: str) -> List[Document]:
    """
    Render and load data content from url.

    Args:
        url (str): URL to scrape.

    Returns:
        List[Document]: List of documents.

    """
    from playwright.async_api import async_playwright

    async with async_playwright() as async_playwright:
        browser = await async_playwright.chromium.launch(**self._launch_options)

        article = await self.scrape_page(
            browser,
            url,
        )
        extra_info = {
            key: article[key]
            for key in [
                "title",
                "length",
                "excerpt",
                "byline",
                "dir",
                "lang",
                "siteName",
            ]
        }

        if self._normalize is not None:
            article["textContent"] = self._normalize(article["textContent"])
        texts = []
        if self._text_splitter is not None:
            texts = self._text_splitter.split_text(article["textContent"])
        else:
            texts = [article["textContent"]]

        await browser.close()

        return [Document(text=x, extra_info=extra_info) for x in texts]

```
  
---|---  
###  scrape_page `async` #
```
scrape_page(browser: Browser, url: str) -> Dict[str, str]

```

Scrape a single article url.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`browser` |  `Any` |  a Playwright Chromium browser. |  _required_  
`url` |  `str` |  URL of the article to scrape. |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`Ref` |  `Dict[str, str]` |  https://github.com/mozilla/readability  
`title` |  `Dict[str, str]` |  article title;  
`content` |  `Dict[str, str]` |  HTML string of processed article content;  
`textContent` |  `Dict[str, str]` |  text content of the article, with all the HTML tags removed;  
`length` |  `Dict[str, str]` |  length of an article, in characters;  
`excerpt` |  `Dict[str, str]` |  article description, or short excerpt from the content;  
`byline` |  `Dict[str, str]` |  author metadata;  
`dir` |  `Dict[str, str]` |  content direction;  
`siteName` |  `Dict[str, str]` |  name of the site.  
`lang` |  `Dict[str, str]` |  content language  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/readability_web/base.py`

| ```
async def scrape_page(
    self,
    browser: Browser,
    url: str,
) -> Dict[str, str]:
    """
    Scrape a single article url.

    Args:
        browser (Any): a Playwright Chromium browser.
        url (str): URL of the article to scrape.

    Returns:
        Ref: https://github.com/mozilla/readability
        title: article title;
        content: HTML string of processed article content;
        textContent: text content of the article, with all the HTML tags removed;
        length: length of an article, in characters;
        excerpt: article description, or short excerpt from the content;
        byline: author metadata;
        dir: content direction;
        siteName: name of the site.
        lang: content language

    """
    if self._readability_js is None:
        with open(path) as f:
            self._readability_js = f.read()

    inject_readability = f"""
        (function(){{
        {self._readability_js}
        function executor() {{
            return new Readability({{}}, document).parse();
        }}
        return executor();
        }}())
    """

    # browser = cast(Browser, browser)
    page = await browser.new_page(ignore_https_errors=True)
    page.set_default_timeout(60000)
    await page.goto(url, wait_until=self._wait_until)

    r = await page.evaluate(inject_readability)

    await page.close()
    print("scraped:", url)

    return r

```
  
---|---  
##  RssNewsReader #
Bases: `BaseReader`
RSS news reader.
Reads news content from RSS feeds and parses with NewsArticleReader.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/rss_news/base.py`

| ```
class RssNewsReader(BaseReader):
    """
    RSS news reader.

    Reads news content from RSS feeds and parses with NewsArticleReader.

    """

    def __init__(self, **reader_kwargs: Any) -> None:
        """
        Initialize with parameters.

        Args:
            html_to_text (bool): Whether to convert HTML to text.
                Requires `html2text` package.

        """
        try:
            import feedparser  # noqa: F401
        except ImportError:
            raise ImportError(
                "`feedparser` package not found, please run `pip install feedparser`"
            )

        try:
            import listparser  # noqa: F401
        except ImportError:
            raise ImportError(
                "`listparser` package not found, please run `pip install listparser`"
            )

        self.reader_kwargs = reader_kwargs

    def load_data(self, urls: List[str] = None, opml: str = None) -> List[Document]:
        """
        Load data from either RSS feeds or OPML.

        Args:
            urls (List[str]): List of RSS URLs to load.
            opml (str): URL to OPML file or string or byte OPML content.

        Returns:
            List[Document]: List of documents.

        """
        if (urls is None) == (
            opml is None
        ):  # This is True if both are None or neither is None
            raise ValueError(
                "Provide either the urls or the opml argument, but not both."
            )

        import feedparser

        if urls and not isinstance(urls, list):
            raise ValueError("urls must be a list of strings.")

        documents = []

        if not urls and opml:
            try:
                import listparser
            except ImportError as e:
                raise ImportError(
                    "Package listparser must be installed if the opml arg is used. "
                    "Please install with 'pip install listparser' or use the "
                    "urls arg instead."
                ) from e
            rss = listparser.parse(opml)
            urls = [feed.url for feed in rss.feeds]

        for url in urls:
            try:
                feed = feedparser.parse(url)
                for i, entry in enumerate(feed.entries):
                    article = NewsArticleReader(**self.reader_kwargs).load_data(
                        urls=[entry.link],
                    )[0]
                    article.metadata["feed"] = url

                    documents.append(
                        Document(text=article.text, metadata=article.metadata)
                    )

            except Exception as e:
                logger.error(f"Error fetching or processing {url}, exception: {e}")
                continue

        return documents

```
  
---|---  
###  load_data #
```
load_data(urls: List[str] = None, opml: str = None) -> List[Document]

```

Load data from either RSS feeds or OPML.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of RSS URLs to load. |  `None`  
`opml` |  `str` |  URL to OPML file or string or byte OPML content. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/rss_news/base.py`

| ```
def load_data(self, urls: List[str] = None, opml: str = None) -> List[Document]:
    """
    Load data from either RSS feeds or OPML.

    Args:
        urls (List[str]): List of RSS URLs to load.
        opml (str): URL to OPML file or string or byte OPML content.

    Returns:
        List[Document]: List of documents.

    """
    if (urls is None) == (
        opml is None
    ):  # This is True if both are None or neither is None
        raise ValueError(
            "Provide either the urls or the opml argument, but not both."
        )

    import feedparser

    if urls and not isinstance(urls, list):
        raise ValueError("urls must be a list of strings.")

    documents = []

    if not urls and opml:
        try:
            import listparser
        except ImportError as e:
            raise ImportError(
                "Package listparser must be installed if the opml arg is used. "
                "Please install with 'pip install listparser' or use the "
                "urls arg instead."
            ) from e
        rss = listparser.parse(opml)
        urls = [feed.url for feed in rss.feeds]

    for url in urls:
        try:
            feed = feedparser.parse(url)
            for i, entry in enumerate(feed.entries):
                article = NewsArticleReader(**self.reader_kwargs).load_data(
                    urls=[entry.link],
                )[0]
                article.metadata["feed"] = url

                documents.append(
                    Document(text=article.text, metadata=article.metadata)
                )

        except Exception as e:
            logger.error(f"Error fetching or processing {url}, exception: {e}")
            continue

    return documents

```
  
---|---  
##  RssReader #
Bases: `BasePydanticReader`
RSS reader.
Reads content from an RSS feed.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/rss/base.py`

| ```
class RssReader(BasePydanticReader):
    """
    RSS reader.

    Reads content from an RSS feed.

    """

    is_remote: bool = True
    html_to_text: bool = False
    user_agent: Union[str, None] = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # https://pythonhosted.org/feedparser/http-useragent.html
        self.user_agent = kwargs.get("user_agent")

    @classmethod
    def class_name(cls) -> str:
        return "RssReader"

    def load_data(self, urls: List[str]) -> List[Document]:
        """
        Load data from RSS feeds.

        Args:
            urls (List[str]): List of RSS URLs to load.

        Returns:
            List[Document]: List of documents.

        """
        import feedparser

        if self.user_agent:
            feedparser.USER_AGENT = self.user_agent

        if not isinstance(urls, list):
            raise ValueError("urls must be a list of strings.")

        documents = []

        for url in urls:
            parsed = feedparser.parse(url)
            for entry in parsed.entries:
                doc_id = getattr(entry, "id", None) or getattr(entry, "link", None)
                data = entry.get("content", [{}])[0].get(
                    "value", entry.get("description", entry.get("summary", ""))
                )

                if self.html_to_text:
                    import html2text

                    data = html2text.html2text(data)

                extra_info = {
                    "title": getattr(entry, "title", None),
                    "link": getattr(entry, "link", None),
                    "date": getattr(entry, "published", None),
                }

                if doc_id:
                    documents.append(
                        Document(text=data, id_=doc_id, extra_info=extra_info)
                    )
                else:
                    documents.append(Document(text=data, extra_info=extra_info))

        return documents

```
  
---|---  
###  load_data #
```
load_data(urls: List[str]) -> List[Document]

```

Load data from RSS feeds.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of RSS URLs to load. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/rss/base.py`

| ```
def load_data(self, urls: List[str]) -> List[Document]:
    """
    Load data from RSS feeds.

    Args:
        urls (List[str]): List of RSS URLs to load.

    Returns:
        List[Document]: List of documents.

    """
    import feedparser

    if self.user_agent:
        feedparser.USER_AGENT = self.user_agent

    if not isinstance(urls, list):
        raise ValueError("urls must be a list of strings.")

    documents = []

    for url in urls:
        parsed = feedparser.parse(url)
        for entry in parsed.entries:
            doc_id = getattr(entry, "id", None) or getattr(entry, "link", None)
            data = entry.get("content", [{}])[0].get(
                "value", entry.get("description", entry.get("summary", ""))
            )

            if self.html_to_text:
                import html2text

                data = html2text.html2text(data)

            extra_info = {
                "title": getattr(entry, "title", None),
                "link": getattr(entry, "link", None),
                "date": getattr(entry, "published", None),
            }

            if doc_id:
                documents.append(
                    Document(text=data, id_=doc_id, extra_info=extra_info)
                )
            else:
                documents.append(Document(text=data, extra_info=extra_info))

    return documents

```
  
---|---  
##  ScrapflyReader #
Bases: `BasePydanticReader`
Turn a url to llm accessible markdown with `Scrapfly.io`.
Args: api_key: The Scrapfly API key. scrape_config: The Scrapfly ScrapeConfig object. ignore_scrape_failures: Whether to continue on failures. urls: List of urls to scrape. scrape_format: Scrape result format (markdown or text) For further details, visit: https://scrapfly.io/docs/sdk/python
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/scrapfly_web/base.py`

| ```
class ScrapflyReader(BasePydanticReader):
    """
    Turn a url to llm accessible markdown with `Scrapfly.io`.

    Args:
    api_key: The Scrapfly API key.
    scrape_config: The Scrapfly ScrapeConfig object.
    ignore_scrape_failures: Whether to continue on failures.
    urls: List of urls to scrape.
    scrape_format: Scrape result format (markdown or text)
    For further details, visit: https://scrapfly.io/docs/sdk/python

    """

    api_key: str
    ignore_scrape_failures: bool = True
    scrapfly: Optional["ScrapflyClient"] = None  # Declare the scrapfly attribute

    def __init__(self, api_key: str, ignore_scrape_failures: bool = True) -> None:
        """Initialize client."""
        super().__init__(api_key=api_key, ignore_scrape_failures=ignore_scrape_failures)
        try:
            from scrapfly import ScrapflyClient
        except ImportError:
            raise ImportError(
                "`scrapfly` package not found, please run `pip install scrapfly-sdk`"
            )
        self.scrapfly = ScrapflyClient(key=api_key)

    @classmethod
    def class_name(cls) -> str:
        return "Scrapfly_reader"

    def load_data(
        self,
        urls: List[str],
        scrape_format: Literal["markdown", "text"] = "markdown",
        scrape_config: Optional[dict] = None,
    ) -> List[Document]:
        """
        Load data from the urls.

        Args:
            urls: List[str]): List of URLs to scrape.
            scrape_config: Optional[dict]: Dictionary of ScrapFly scrape config object.

        Returns:
            List[Document]: List of documents.

        Raises:
            ValueError: If URLs aren't provided.

        """
        from scrapfly import ScrapeApiResponse, ScrapeConfig

        if urls is None:
            raise ValueError("URLs must be provided.")
        scrape_config = scrape_config if scrape_config is not None else {}

        documents = []
        for url in urls:
            try:
                response: ScrapeApiResponse = self.scrapfly.scrape(
                    ScrapeConfig(url, format=scrape_format, **scrape_config)
                )
                documents.append(
                    Document(
                        text=response.scrape_result["content"], extra_info={"url": url}
                    )
                )
            except Exception as e:
                if self.ignore_scrape_failures:
                    logger.error(f"Error fetching data from {url}, exception: {e}")
                else:
                    raise e  # noqa: TRY201

        return documents

```
  
---|---  
###  load_data #
```
load_data(urls: List[str], scrape_format: Literal['markdown', 'text'] = 'markdown', scrape_config: Optional[dict] = None) -> List[Document]

```

Load data from the urls.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List[str]): List of URLs to scrape. |  _required_  
`scrape_config` |  `Optional[dict]` |  Optional[dict]: Dictionary of ScrapFly scrape config object. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Raises:
Type | Description  
---|---  
`ValueError` |  If URLs aren't provided.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/scrapfly_web/base.py`

| ```
def load_data(
    self,
    urls: List[str],
    scrape_format: Literal["markdown", "text"] = "markdown",
    scrape_config: Optional[dict] = None,
) -> List[Document]:
    """
    Load data from the urls.

    Args:
        urls: List[str]): List of URLs to scrape.
        scrape_config: Optional[dict]: Dictionary of ScrapFly scrape config object.

    Returns:
        List[Document]: List of documents.

    Raises:
        ValueError: If URLs aren't provided.

    """
    from scrapfly import ScrapeApiResponse, ScrapeConfig

    if urls is None:
        raise ValueError("URLs must be provided.")
    scrape_config = scrape_config if scrape_config is not None else {}

    documents = []
    for url in urls:
        try:
            response: ScrapeApiResponse = self.scrapfly.scrape(
                ScrapeConfig(url, format=scrape_format, **scrape_config)
            )
            documents.append(
                Document(
                    text=response.scrape_result["content"], extra_info={"url": url}
                )
            )
        except Exception as e:
            if self.ignore_scrape_failures:
                logger.error(f"Error fetching data from {url}, exception: {e}")
            else:
                raise e  # noqa: TRY201

    return documents

```
  
---|---  
##  SimpleWebPageReader #
Bases: `BasePydanticReader`
Simple web page reader.
Reads pages from the web.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`html_to_text` |  `bool` |  Whether to convert HTML to text. Requires `html2text` package. |  `False`  
`metadata_fn` |  `Optional[Callable[[str], Dict]]` |  A function that takes in a URL and returns a dictionary of metadata. Default is None. |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/simple_web/base.py`

| ```
class SimpleWebPageReader(BasePydanticReader):
    """
    Simple web page reader.

    Reads pages from the web.

    Args:
        html_to_text (bool): Whether to convert HTML to text.
            Requires `html2text` package.
        metadata_fn (Optional[Callable[[str], Dict]]): A function that takes in
            a URL and returns a dictionary of metadata.
            Default is None.

    """

    is_remote: bool = True
    html_to_text: bool

    _metadata_fn: Optional[Callable[[str], Dict]] = PrivateAttr()
    _timeout: Optional[int] = PrivateAttr()
    _fail_on_error: bool = PrivateAttr()

    def __init__(
        self,
        html_to_text: bool = False,
        metadata_fn: Optional[Callable[[str], Dict]] = None,
        timeout: Optional[int] = 60,
        fail_on_error: bool = False,
    ) -> None:
        """Initialize with parameters."""
        try:
            import html2text  # noqa
        except ImportError:
            raise ImportError(
                "`html2text` package not found, please run `pip install html2text`"
            )
        super().__init__(html_to_text=html_to_text)
        self._metadata_fn = metadata_fn
        self._timeout = timeout
        self._fail_on_error = fail_on_error

    @classmethod
    def class_name(cls) -> str:
        return "SimpleWebPageReader"

    def load_data(self, urls: List[str]) -> List[Document]:
        """
        Load data from the input directory.

        Args:
            urls (List[str]): List of URLs to scrape.

        Returns:
            List[Document]: List of documents.

        """
        if not isinstance(urls, list):
            raise ValueError("urls must be a list of strings.")
        documents = []
        for url in urls:
            try:
                response = requests.get(url, headers=None, timeout=self._timeout)
            except Exception:
                if self._fail_on_error:
                    raise
                continue

            response_text = response.text

            if response.status_code != 200 and self._fail_on_error:
                raise ValueError(
                    f"Error fetching page from {url}. server returned status:"
                    f" {response.status_code} and response {response_text}"
                )

            if self.html_to_text:
                import html2text

                response_text = html2text.html2text(response_text)

            metadata: Dict = {"url": url}
            if self._metadata_fn is not None:
                metadata = self._metadata_fn(url)
                if "url" not in metadata:
                    metadata["url"] = url

            documents.append(
                Document(text=response_text, id_=str(uuid.uuid4()), metadata=metadata)
            )

        return documents

```
  
---|---  
###  load_data #
```
load_data(urls: List[str]) -> List[Document]

```

Load data from the input directory.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of URLs to scrape. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/simple_web/base.py`

| ```
def load_data(self, urls: List[str]) -> List[Document]:
    """
    Load data from the input directory.

    Args:
        urls (List[str]): List of URLs to scrape.

    Returns:
        List[Document]: List of documents.

    """
    if not isinstance(urls, list):
        raise ValueError("urls must be a list of strings.")
    documents = []
    for url in urls:
        try:
            response = requests.get(url, headers=None, timeout=self._timeout)
        except Exception:
            if self._fail_on_error:
                raise
            continue

        response_text = response.text

        if response.status_code != 200 and self._fail_on_error:
            raise ValueError(
                f"Error fetching page from {url}. server returned status:"
                f" {response.status_code} and response {response_text}"
            )

        if self.html_to_text:
            import html2text

            response_text = html2text.html2text(response_text)

        metadata: Dict = {"url": url}
        if self._metadata_fn is not None:
            metadata = self._metadata_fn(url)
            if "url" not in metadata:
                metadata["url"] = url

        documents.append(
            Document(text=response_text, id_=str(uuid.uuid4()), metadata=metadata)
        )

    return documents

```
  
---|---  
##  SitemapReader #
Bases: `BaseReader`
Asynchronous sitemap reader for web.
Reads pages from the web based on their sitemap.xml.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`sitemap_url` |  `string` |  Path to the sitemap.xml. e.g. https://gpt-index.readthedocs.io/sitemap.xml |  _required_  
`html_to_text` |  `bool` |  Whether to convert HTML to text. Requires `html2text` package. |  `False`  
`limit` |  `int` |  Maximum number of concurrent requests. |  `10`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/sitemap/base.py`

| ```
class SitemapReader(BaseReader):
    """
    Asynchronous sitemap reader for web.

    Reads pages from the web based on their sitemap.xml.

    Args:
        sitemap_url (string): Path to the sitemap.xml. e.g. https://gpt-index.readthedocs.io/sitemap.xml
        html_to_text (bool): Whether to convert HTML to text.
            Requires `html2text` package.
        limit (int): Maximum number of concurrent requests.

    """

    xml_schema_sitemap = "http://www.sitemaps.org/schemas/sitemap/0.9"

    def __init__(self, html_to_text: bool = False, limit: int = 10) -> None:
        """Initialize with parameters."""
        self._async_loader = AsyncWebPageReader(html_to_text=html_to_text, limit=limit)
        self._html_to_text = html_to_text
        self._limit = limit

    def _load_sitemap(self, sitemap_url: str) -> str:
        sitemap_url_request = httpx.get(sitemap_url)

        return sitemap_url_request.content

    def _parse_sitemap(self, raw_sitemap: str, filter_locs: str = None) -> list:
        sitemap = fromstring(raw_sitemap)
        sitemap_urls = []

        for url in sitemap.findall(f"{{{self.xml_schema_sitemap}}}url"):
            location = url.find(f"{{{self.xml_schema_sitemap}}}loc").text

            if filter_locs is None or filter_locs in location:
                sitemap_urls.append(location)

        return sitemap_urls

    def load_data(self, sitemap_url: str, filter: str = None) -> List[Document]:
        sitemap = self._load_sitemap(sitemap_url=sitemap_url)
        sitemap_urls = self._parse_sitemap(sitemap, filter)

        return self._async_loader.load_data(urls=sitemap_urls)

```
  
---|---  
##  TrafilaturaWebReader #
Bases: `BasePydanticReader`
Trafilatura web page reader.
Reads pages from the web. Requires the `trafilatura` package.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/trafilatura_web/base.py`

| ```
class TrafilaturaWebReader(BasePydanticReader):
    """
    Trafilatura web page reader.

    Reads pages from the web.
    Requires the `trafilatura` package.

    """

    is_remote: bool = True

    @classmethod
    def class_name(cls) -> str:
        """Get the name identifier of the class."""
        return "TrafilaturaWebReader"

    def load_data(
        self,
        urls: List[str],
        include_comments=True,
        output_format="txt",
        include_tables=True,
        include_images=False,
        include_formatting=False,
        include_links=False,
        show_progress=False,
        no_ssl=False,
        **kwargs,
    ) -> List[Document]:
        """
        Load data from the urls.

        Args:
            urls (List[str]): List of URLs to scrape.
            include_comments (bool, optional): Include comments in the output. Defaults to True.
            output_format (str, optional): Output format. Defaults to 'txt'.
            include_tables (bool, optional): Include tables in the output. Defaults to True.
            include_images (bool, optional): Include images in the output. Defaults to False.
            include_formatting (bool, optional): Include formatting in the output. Defaults to False.
            include_links (bool, optional): Include links in the output. Defaults to False.
            show_progress (bool, optional): Show progress bar. Defaults to False
            no_ssl (bool, optional): Bypass SSL verification. Defaults to False.
            kwargs: Additional keyword arguments for the `trafilatura.extract` function.

        Returns:
            List[Document]: List of documents.

        """
        import trafilatura

        if not isinstance(urls, list):
            raise ValueError("urls must be a list of strings.")
        documents = []

        if show_progress:
            from tqdm import tqdm

            iterator = tqdm(urls, desc="Downloading pages")
        else:
            iterator = urls
        for url in iterator:
            downloaded = trafilatura.fetch_url(url, no_ssl=no_ssl)
            response = trafilatura.extract(
                downloaded,
                include_comments=include_comments,
                output_format=output_format,
                include_tables=include_tables,
                include_images=include_images,
                include_formatting=include_formatting,
                include_links=include_links,
                **kwargs,
            )
            documents.append(
                Document(text=response, id_=str(uuid.uuid4()), metadata={"url": url})
            )

        return documents

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get the name identifier of the class.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/trafilatura_web/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get the name identifier of the class."""
    return "TrafilaturaWebReader"

```
  
---|---  
###  load_data #
```
load_data(urls: List[str], include_comments=True, output_format='txt', include_tables=True, include_images=False, include_formatting=False, include_links=False, show_progress=False, no_ssl=False, **kwargs) -> List[Document]

```

Load data from the urls.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`urls` |  `List[str]` |  List of URLs to scrape. |  _required_  
`include_comments` |  `bool` |  Include comments in the output. Defaults to True. |  `True`  
`output_format` |  `str` |  Output format. Defaults to 'txt'. |  `'txt'`  
`include_tables` |  `bool` |  Include tables in the output. Defaults to True. |  `True`  
`include_images` |  `bool` |  Include images in the output. Defaults to False. |  `False`  
`include_formatting` |  `bool` |  Include formatting in the output. Defaults to False. |  `False`  
`include_links` |  `bool` |  Include links in the output. Defaults to False. |  `False`  
`show_progress` |  `bool` |  Show progress bar. Defaults to False |  `False`  
`no_ssl` |  `bool` |  Bypass SSL verification. Defaults to False. |  `False`  
`kwargs` |  |  Additional keyword arguments for the `trafilatura.extract` function. |  `{}`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/trafilatura_web/base.py`

| ```
def load_data(
    self,
    urls: List[str],
    include_comments=True,
    output_format="txt",
    include_tables=True,
    include_images=False,
    include_formatting=False,
    include_links=False,
    show_progress=False,
    no_ssl=False,
    **kwargs,
) -> List[Document]:
    """
    Load data from the urls.

    Args:
        urls (List[str]): List of URLs to scrape.
        include_comments (bool, optional): Include comments in the output. Defaults to True.
        output_format (str, optional): Output format. Defaults to 'txt'.
        include_tables (bool, optional): Include tables in the output. Defaults to True.
        include_images (bool, optional): Include images in the output. Defaults to False.
        include_formatting (bool, optional): Include formatting in the output. Defaults to False.
        include_links (bool, optional): Include links in the output. Defaults to False.
        show_progress (bool, optional): Show progress bar. Defaults to False
        no_ssl (bool, optional): Bypass SSL verification. Defaults to False.
        kwargs: Additional keyword arguments for the `trafilatura.extract` function.

    Returns:
        List[Document]: List of documents.

    """
    import trafilatura

    if not isinstance(urls, list):
        raise ValueError("urls must be a list of strings.")
    documents = []

    if show_progress:
        from tqdm import tqdm

        iterator = tqdm(urls, desc="Downloading pages")
    else:
        iterator = urls
    for url in iterator:
        downloaded = trafilatura.fetch_url(url, no_ssl=no_ssl)
        response = trafilatura.extract(
            downloaded,
            include_comments=include_comments,
            output_format=output_format,
            include_tables=include_tables,
            include_images=include_images,
            include_formatting=include_formatting,
            include_links=include_links,
            **kwargs,
        )
        documents.append(
            Document(text=response, id_=str(uuid.uuid4()), metadata={"url": url})
        )

    return documents

```
  
---|---  
##  UnstructuredURLLoader #
Bases: `BaseReader`
Loader that uses unstructured to load HTML files.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/unstructured_web/base.py`

| ```
class UnstructuredURLLoader(BaseReader):
    """Loader that uses unstructured to load HTML files."""

    def __init__(
        self, urls: List[str], continue_on_failure: bool = True, headers: dict = {}
    ):
        """Initialize with file path."""
        try:
            import unstructured  # noqa:F401
            from unstructured.__version__ import __version__ as __unstructured_version__

            self.__version = __unstructured_version__
        except ImportError:
            raise ValueError(
                "unstructured package not found, please install it with "
                "`pip install unstructured`"
            )

        if not self.__is_headers_available() and len(headers.keys()) != 0:
            logger.warning(
                "You are using old version of unstructured. "
                "The headers parameter is ignored"
            )

        self.urls = urls
        self.continue_on_failure = continue_on_failure
        self.headers = headers

    def __is_headers_available(self) -> bool:
        _unstructured_version = self.__version.split("-")[0]
        unstructured_version = tuple([int(x) for x in _unstructured_version.split(".")])

        return unstructured_version >= (0, 5, 7)

    def load_data(self) -> List[Document]:
        """Load file."""
        from unstructured.partition.html import partition_html

        docs: List[Document] = []
        for url in self.urls:
            try:
                if self.__is_headers_available():
                    elements = partition_html(url=url, headers=self.headers)
                else:
                    elements = partition_html(url=url)
                text = "\n\n".join([str(el) for el in elements])
                metadata = {"source": url}
                docs.append(Document(text=text, extra_info=metadata))
            except Exception as e:
                if self.continue_on_failure:
                    logger.error(f"Error fetching or processing {url}, exception: {e}")
                else:
                    raise e  # noqa: TRY201
        return docs

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Load file.
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/unstructured_web/base.py`

| ```
def load_data(self) -> List[Document]:
    """Load file."""
    from unstructured.partition.html import partition_html

    docs: List[Document] = []
    for url in self.urls:
        try:
            if self.__is_headers_available():
                elements = partition_html(url=url, headers=self.headers)
            else:
                elements = partition_html(url=url)
            text = "\n\n".join([str(el) for el in elements])
            metadata = {"source": url}
            docs.append(Document(text=text, extra_info=metadata))
        except Exception as e:
            if self.continue_on_failure:
                logger.error(f"Error fetching or processing {url}, exception: {e}")
            else:
                raise e  # noqa: TRY201
    return docs

```
  
---|---  
##  WholeSiteReader #
Bases: `BaseReader`
BFS Web Scraper for websites.
This class provides functionality to scrape entire websites using a breadth-first search algorithm. It navigates web pages from a given base URL, following links that match a specified prefix.
Attributes:
Name | Type | Description  
---|---|---  
`prefix` |  `str` |  URL prefix to focus the scraping.  
`max_depth` |  `int` |  Maximum depth for BFS algorithm.  
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prefix` |  `str` |  URL prefix for scraping. |  _required_  
`max_depth` |  `int` |  Maximum depth for BFS. Defaults to 10. |  `10`  
`uri_as_id` |  `bool` |  Whether to use the URI as the document ID. Defaults to False. |  `False`  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/whole_site/base.py`

| ```
class WholeSiteReader(BaseReader):
    """
    BFS Web Scraper for websites.

    This class provides functionality to scrape entire websites using a breadth-first search algorithm.
    It navigates web pages from a given base URL, following links that match a specified prefix.

    Attributes:
        prefix (str): URL prefix to focus the scraping.
        max_depth (int): Maximum depth for BFS algorithm.

    Args:
        prefix (str): URL prefix for scraping.
        max_depth (int, optional): Maximum depth for BFS. Defaults to 10.
        uri_as_id (bool, optional): Whether to use the URI as the document ID. Defaults to False.

    """

    def __init__(
        self,
        prefix: str,
        max_depth: int = 10,
        uri_as_id: bool = False,
        driver: Optional[webdriver.Chrome] = None,
    ) -> None:
        """
        Initialize the WholeSiteReader with the provided prefix and maximum depth.
        """
        self.prefix = prefix
        self.max_depth = max_depth
        self.uri_as_id = uri_as_id
        self.driver = driver if driver else self.setup_driver()

    def setup_driver(self):
        """
        Sets up the Selenium WebDriver for Chrome.

        Returns:
            WebDriver: An instance of Chrome WebDriver.

        """
        try:
            import chromedriver_autoinstaller
        except ImportError:
            raise ImportError("Please install chromedriver_autoinstaller")

        opt = webdriver.ChromeOptions()
        opt.add_argument("--start-maximized")
        chromedriver_autoinstaller.install()
        return webdriver.Chrome(options=opt)

    def clean_url(self, url):
        return url.split("#")[0]

    def restart_driver(self):
        self.driver.quit()
        self.driver = self.setup_driver()

    def extract_content(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        body_element = self.driver.find_element(By.TAG_NAME, "body")
        return body_element.text.strip()

    def extract_links(self):
        js_script = """
            var links = [];
            var elements = document.getElementsByTagName('a');
            for (var i = 0; i < elements.length; i++) {
                var href = elements[i].href;
                if (href) {
                    links.push(href);
                }
            }
            return links;
            """
        return self.driver.execute_script(js_script)

    def load_data(self, base_url: str) -> List[Document]:
        """
        Load data from the base URL using BFS algorithm.

        Args:
            base_url (str): Base URL to start scraping.


        Returns:
            List[Document]: List of scraped documents.

        """
        added_urls = set()
        urls_to_visit = [(base_url, 0)]
        documents = []

        while urls_to_visit:
            current_url, depth = urls_to_visit.pop(0)
            print(f"Visiting: {current_url}, {len(urls_to_visit)} left")

            try:
                self.driver.get(current_url)
                page_content = self.extract_content()
                added_urls.add(current_url)

                next_depth = depth + 1
                if next_depth <= self.max_depth:
                    # links = self.driver.find_elements(By.TAG_NAME, 'a')
                    links = self.extract_links()
                    # clean all urls
                    links = [self.clean_url(link) for link in links]
                    # extract new links
                    links = [link for link in links if link not in added_urls]
                    print(f"Found {len(links)} new potential links")

                    for href in links:
                        try:
                            if href.startswith(self.prefix) and href not in added_urls:
                                urls_to_visit.append((href, next_depth))
                                added_urls.add(href)
                        except Exception:
                            continue

                doc = Document(text=page_content, extra_info={"URL": current_url})
                if self.uri_as_id:
                    warnings.warn(
                        "Setting the URI as the id of the document might break the code execution downstream and should be avoided."
                    )
                    doc.id_ = current_url
                documents.append(doc)
                time.sleep(1)

            except WebDriverException:
                print("WebDriverException encountered, restarting driver...")
                self.restart_driver()
            except Exception as e:
                print(f"An unexpected exception occurred: {e}, skipping URL...")
                continue

        self.driver.quit()
        return documents

```
  
---|---  
###  setup_driver #
```
setup_driver()

```

Sets up the Selenium WebDriver for Chrome.
Returns:
Name | Type | Description  
---|---|---  
`WebDriver` |  |  An instance of Chrome WebDriver.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/whole_site/base.py`

| ```
def setup_driver(self):
    """
    Sets up the Selenium WebDriver for Chrome.

    Returns:
        WebDriver: An instance of Chrome WebDriver.

    """
    try:
        import chromedriver_autoinstaller
    except ImportError:
        raise ImportError("Please install chromedriver_autoinstaller")

    opt = webdriver.ChromeOptions()
    opt.add_argument("--start-maximized")
    chromedriver_autoinstaller.install()
    return webdriver.Chrome(options=opt)

```
  
---|---  
###  load_data #
```
load_data(base_url: str) -> List[Document]

```

Load data from the base URL using BFS algorithm.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`base_url` |  `str` |  Base URL to start scraping. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of scraped documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-web/llama_index/readers/web/whole_site/base.py`

| ```
def load_data(self, base_url: str) -> List[Document]:
    """
    Load data from the base URL using BFS algorithm.

    Args:
        base_url (str): Base URL to start scraping.


    Returns:
        List[Document]: List of scraped documents.

    """
    added_urls = set()
    urls_to_visit = [(base_url, 0)]
    documents = []

    while urls_to_visit:
        current_url, depth = urls_to_visit.pop(0)
        print(f"Visiting: {current_url}, {len(urls_to_visit)} left")

        try:
            self.driver.get(current_url)
            page_content = self.extract_content()
            added_urls.add(current_url)

            next_depth = depth + 1
            if next_depth <= self.max_depth:
                # links = self.driver.find_elements(By.TAG_NAME, 'a')
                links = self.extract_links()
                # clean all urls
                links = [self.clean_url(link) for link in links]
                # extract new links
                links = [link for link in links if link not in added_urls]
                print(f"Found {len(links)} new potential links")

                for href in links:
                    try:
                        if href.startswith(self.prefix) and href not in added_urls:
                            urls_to_visit.append((href, next_depth))
                            added_urls.add(href)
                    except Exception:
                        continue

            doc = Document(text=page_content, extra_info={"URL": current_url})
            if self.uri_as_id:
                warnings.warn(
                    "Setting the URI as the id of the document might break the code execution downstream and should be avoided."
                )
                doc.id_ = current_url
            documents.append(doc)
            time.sleep(1)

        except WebDriverException:
            print("WebDriverException encountered, restarting driver...")
            self.restart_driver()
        except Exception as e:
            print(f"An unexpected exception occurred: {e}, skipping URL...")
            continue

    self.driver.quit()
    return documents

```
  
---|---
