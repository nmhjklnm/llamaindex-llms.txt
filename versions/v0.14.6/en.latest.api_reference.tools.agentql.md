# Agentql
##  AgentQLBrowserToolSpec #
Bases: `BaseToolSpec`
AgentQL Browser Tool Spec.
Source code in `llama-index-integrations/tools/llama-index-tools-agentql/llama_index/tools/agentql/agentql_browser_tool/base.py`

| ```
class AgentQLBrowserToolSpec(BaseToolSpec):
    """
    AgentQL Browser Tool Spec.
    """

    spec_functions = [
        "extract_web_data_from_browser",
        "get_web_element_from_browser",
    ]

    def __init__(
        self,
        async_browser: AsyncBrowser,
        timeout_for_data: int = DEFAULT_EXTRACT_DATA_TIMEOUT_SECONDS,
        timeout_for_element: int = DEFAULT_EXTRACT_ELEMENTS_TIMEOUT_SECONDS,
        wait_for_network_idle: bool = DEFAULT_WAIT_FOR_NETWORK_IDLE,
        include_hidden_for_data: bool = DEFAULT_INCLUDE_HIDDEN_DATA,
        include_hidden_for_element: bool = DEFAULT_INCLUDE_HIDDEN_ELEMENTS,
        mode: str = DEFAULT_RESPONSE_MODE,
    ):
        """
        Initialize AgentQL Browser Tool Spec.

        Args:
            async_browser: An async playwright browser instance.
            timeout_for_data: The number of seconds to wait for a extract data request before timing out. Defaults to 900.
            timeout_for_element: The number of seconds to wait for a get element request before timing out. Defaults to 300.
            wait_for_network_idle: Whether to wait for network idle state. Defaults to `True`.
            include_hidden_for_data: Whether to take into account visually hidden elements on the page for extract data. Defaults to `True`.
            include_hidden_for_element: Whether to take into account visually hidden elements on the page for get element. Defaults to `False`.

            mode: `standard` uses deep data analysis, while `fast` trades some depth of analysis for speed and is adequate for most usecases.
            Learn more about the modes in this guide: https://docs.agentql.com/accuracy/standard-mode. Defaults to `fast`.

        """
        self.async_browser = async_browser
        self.timeout_for_data = timeout_for_data
        self.timeout_for_element = timeout_for_element
        self.wait_for_network_idle = wait_for_network_idle
        self.include_hidden_for_data = include_hidden_for_data
        self.include_hidden_for_element = include_hidden_for_element
        self.mode = mode

    async def extract_web_data_from_browser(
        self,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> dict:
        """
        Extracts structured data as JSON from a web page given a URL using either an AgentQL query or a Natural Language description of the data.

        Args:
            query: AgentQL query used to extract the data. The query must be enclosed with curly braces `{}`. Either this field or `prompt` field must be provided.
            prompt: Natural Language description of the data to extract from the page. If AgentQL query is not specified, always use the `prompt` field. Either this field or `query` field must be provided.

        Returns:
            dict: The extracted data

        """
        # Check that query and prompt cannot be both empty or both provided
        if not query and not prompt:
            raise ValueError(QUERY_PROMPT_REQUIRED_ERROR_MESSAGE)
        if query and prompt:
            raise ValueError(QUERY_PROMPT_EXCLUSIVE_ERROR_MESSAGE)

        page = await _aget_current_agentql_page(self.async_browser)
        if query:
            return await page.query_data(
                query,
                self.timeout_for_data,
                self.wait_for_network_idle,
                self.include_hidden_for_data,
                self.mode,
                request_origin=REQUEST_ORIGIN,
            )
        else:
            return await page.get_data_by_prompt_experimental(
                prompt,
                self.timeout_for_data,
                self.wait_for_network_idle,
                self.include_hidden_for_data,
                self.mode,
                request_origin=REQUEST_ORIGIN,
            )

    async def get_web_element_from_browser(
        self,
        prompt: str,
    ) -> str:
        """
        Finds a web element on the active web page in a running browser instance using element’s Natural Language description and returns its CSS selector for further interaction, like clicking, filling a form field, etc.

        Args:
            prompt: Natural Language description of the web element to find on the page.

        Returns:
            str: The CSS selector of the target element.

        """
        page = await _aget_current_agentql_page(self.async_browser)
        element = await page.get_by_prompt(
            prompt,
            self.timeout_for_element,
            self.wait_for_network_idle,
            self.include_hidden_for_element,
            self.mode,
            request_origin=REQUEST_ORIGIN,
        )
        tf_id = await element.get_attribute("tf623_id")
        return f"[tf623_id='{tf_id}']"

```
  
---|---  
###  extract_web_data_from_browser `async` #
```
extract_web_data_from_browser(query: Optional[str] = None, prompt: Optional[str] = None) -> dict

```

Extracts structured data as JSON from a web page given a URL using either an AgentQL query or a Natural Language description of the data.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `Optional[str]` |  AgentQL query used to extract the data. The query must be enclosed with curly braces `{}`. Either this field or `prompt` field must be provided. |  `None`  
`prompt` |  `Optional[str]` |  Natural Language description of the data to extract from the page. If AgentQL query is not specified, always use the `prompt` field. Either this field or `query` field must be provided. |  `None`  
Returns:
Name | Type | Description  
---|---|---  
`dict` |  `dict` |  The extracted data  
Source code in `llama-index-integrations/tools/llama-index-tools-agentql/llama_index/tools/agentql/agentql_browser_tool/base.py`

| ```
async def extract_web_data_from_browser(
    self,
    query: Optional[str] = None,
    prompt: Optional[str] = None,
) -> dict:
    """
    Extracts structured data as JSON from a web page given a URL using either an AgentQL query or a Natural Language description of the data.

    Args:
        query: AgentQL query used to extract the data. The query must be enclosed with curly braces `{}`. Either this field or `prompt` field must be provided.
        prompt: Natural Language description of the data to extract from the page. If AgentQL query is not specified, always use the `prompt` field. Either this field or `query` field must be provided.

    Returns:
        dict: The extracted data

    """
    # Check that query and prompt cannot be both empty or both provided
    if not query and not prompt:
        raise ValueError(QUERY_PROMPT_REQUIRED_ERROR_MESSAGE)
    if query and prompt:
        raise ValueError(QUERY_PROMPT_EXCLUSIVE_ERROR_MESSAGE)

    page = await _aget_current_agentql_page(self.async_browser)
    if query:
        return await page.query_data(
            query,
            self.timeout_for_data,
            self.wait_for_network_idle,
            self.include_hidden_for_data,
            self.mode,
            request_origin=REQUEST_ORIGIN,
        )
    else:
        return await page.get_data_by_prompt_experimental(
            prompt,
            self.timeout_for_data,
            self.wait_for_network_idle,
            self.include_hidden_for_data,
            self.mode,
            request_origin=REQUEST_ORIGIN,
        )

```
  
---|---  
###  get_web_element_from_browser `async` #
```
get_web_element_from_browser(prompt: str) -> str

```

Finds a web element on the active web page in a running browser instance using element’s Natural Language description and returns its CSS selector for further interaction, like clicking, filling a form field, etc.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  Natural Language description of the web element to find on the page. |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The CSS selector of the target element.  
Source code in `llama-index-integrations/tools/llama-index-tools-agentql/llama_index/tools/agentql/agentql_browser_tool/base.py`

| ```
async def get_web_element_from_browser(
    self,
    prompt: str,
) -> str:
    """
    Finds a web element on the active web page in a running browser instance using element’s Natural Language description and returns its CSS selector for further interaction, like clicking, filling a form field, etc.

    Args:
        prompt: Natural Language description of the web element to find on the page.

    Returns:
        str: The CSS selector of the target element.

    """
    page = await _aget_current_agentql_page(self.async_browser)
    element = await page.get_by_prompt(
        prompt,
        self.timeout_for_element,
        self.wait_for_network_idle,
        self.include_hidden_for_element,
        self.mode,
        request_origin=REQUEST_ORIGIN,
    )
    tf_id = await element.get_attribute("tf623_id")
    return f"[tf623_id='{tf_id}']"

```
  
---|---  
##  AgentQLRestAPIToolSpec #
Bases: `BaseToolSpec`
AgentQL Rest API Tool Spec.
Source code in `llama-index-integrations/tools/llama-index-tools-agentql/llama_index/tools/agentql/agentql_rest_api_tool/base.py`

| ```
class AgentQLRestAPIToolSpec(BaseToolSpec):
    """
    AgentQL Rest API Tool Spec.
    """

    spec_functions = [
        "extract_web_data_with_rest_api",
    ]

    def __init__(
        self,
        timeout: int = DEFAULT_API_TIMEOUT_SECONDS,
        is_stealth_mode_enabled: bool = DEFAULT_IS_STEALTH_MODE_ENABLED,
        wait_for: int = DEFAULT_WAIT_FOR_PAGE_LOAD_SECONDS,
        is_scroll_to_bottom_enabled: bool = DEFAULT_IS_SCROLL_TO_BOTTOM_ENABLED,
        mode: str = DEFAULT_RESPONSE_MODE,
        is_screenshot_enabled: bool = DEFAULT_IS_SCREENSHOT_ENABLED,
    ):
        """
        Initialize AgentQL Rest API Tool Spec.

        Args:
            timeout: The number of seconds to wait for a request before timing out. Defaults to 900.

            is_stealth_mode_enabled: Whether to enable experimental anti-bot evasion strategies. This feature may not work for all websites at all times.
            Data extraction may take longer to complete with this mode enabled. Defaults to `False`.

            wait_for: The number of seconds to wait for the page to load before extracting data. Defaults to 0.
            is_scroll_to_bottom_enabled: Whether to scroll to bottom of the page before extracting data. Defaults to `False`.

            mode: 'standard' uses deep data analysis, while 'fast' trades some depth of analysis for speed and is adequate for most usecases.
            Learn more about the modes in this guide: https://docs.agentql.com/accuracy/standard-mode) Defaults to 'fast'.

            is_screenshot_enabled: Whether to take a screenshot before extracting data. Returned in 'metadata' as a Base64 string. Defaults to `False`.

        """
        self._api_key = os.getenv("AGENTQL_API_KEY")
        if not self._api_key:
            raise ValueError(UNSET_API_KEY_ERROR_MESSAGE)
        self.timeout = timeout
        self.is_stealth_mode_enabled = is_stealth_mode_enabled
        self.wait_for = wait_for
        self.is_scroll_to_bottom_enabled = is_scroll_to_bottom_enabled
        self.mode = mode
        self.is_screenshot_enabled = is_screenshot_enabled

    async def extract_web_data_with_rest_api(
        self,
        url: str,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> dict:
        """
        Extracts structured data as a JSON from the active web page in a running browser instance using either an AgentQL query or a Natural Language description of the data.

        Args:
            url: URL of the public webpage to extract data from.
            query: AgentQL query used to extract the data. The query must be enclosed with curly braces `{}`. Either this field or `prompt` field must be provided.
            prompt: Natural Language description of the data to extract from the page. If AgentQL query is not specified, always use the `prompt` field. Either this field or `query` field must be provided.

        Returns:
            dict: Extracted data.

        """
        _params = {
            "wait_for": self.wait_for,
            "is_scroll_to_bottom_enabled": self.is_scroll_to_bottom_enabled,
            "mode": self.mode,
            "is_screenshot_enabled": self.is_screenshot_enabled,
        }
        _metadata = {
            "experimental_stealth_mode_enabled": self.is_stealth_mode_enabled,
        }

        return await _aload_data(
            url=url,
            query=query,
            prompt=prompt,
            params=_params,
            metadata=_metadata,
            api_key=self._api_key,
            timeout=self.timeout,
        )

```
  
---|---  
###  extract_web_data_with_rest_api `async` #
```
extract_web_data_with_rest_api(url: str, query: Optional[str] = None, prompt: Optional[str] = None) -> dict

```

Extracts structured data as a JSON from the active web page in a running browser instance using either an AgentQL query or a Natural Language description of the data.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url` |  `str` |  URL of the public webpage to extract data from. |  _required_  
`query` |  `Optional[str]` |  AgentQL query used to extract the data. The query must be enclosed with curly braces `{}`. Either this field or `prompt` field must be provided. |  `None`  
`prompt` |  `Optional[str]` |  Natural Language description of the data to extract from the page. If AgentQL query is not specified, always use the `prompt` field. Either this field or `query` field must be provided. |  `None`  
Returns:
Name | Type | Description  
---|---|---  
`dict` |  `dict` |  Extracted data.  
Source code in `llama-index-integrations/tools/llama-index-tools-agentql/llama_index/tools/agentql/agentql_rest_api_tool/base.py`

| ```
async def extract_web_data_with_rest_api(
    self,
    url: str,
    query: Optional[str] = None,
    prompt: Optional[str] = None,
) -> dict:
    """
    Extracts structured data as a JSON from the active web page in a running browser instance using either an AgentQL query or a Natural Language description of the data.

    Args:
        url: URL of the public webpage to extract data from.
        query: AgentQL query used to extract the data. The query must be enclosed with curly braces `{}`. Either this field or `prompt` field must be provided.
        prompt: Natural Language description of the data to extract from the page. If AgentQL query is not specified, always use the `prompt` field. Either this field or `query` field must be provided.

    Returns:
        dict: Extracted data.

    """
    _params = {
        "wait_for": self.wait_for,
        "is_scroll_to_bottom_enabled": self.is_scroll_to_bottom_enabled,
        "mode": self.mode,
        "is_screenshot_enabled": self.is_screenshot_enabled,
    }
    _metadata = {
        "experimental_stealth_mode_enabled": self.is_stealth_mode_enabled,
    }

    return await _aload_data(
        url=url,
        query=query,
        prompt=prompt,
        params=_params,
        metadata=_metadata,
        api_key=self._api_key,
        timeout=self.timeout,
    )

```
  
---|---
