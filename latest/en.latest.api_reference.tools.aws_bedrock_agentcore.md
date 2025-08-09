# Aws bedrock agentcore
AWS Bedrock AgentCore tools.
##  AgentCoreBrowserToolSpec #
Bases: `BaseToolSpec`
AWS Bedrock AgentCore Browser Tool Spec.
This toolkit provides a set of tools for working with a remote browser environment:
  * navigate_browser - Navigate to a URL
  * click_element - Click on an element using CSS selectors
  * extract_text - Extract all text from the current webpage
  * extract_hyperlinks - Extract all hyperlinks from the current webpage
  * get_elements - Get elements matching a CSS selector
  * navigate_back - Navigate to the previous page
  * current_webpage - Get information about the current webpage


The toolkit supports multiple threads by maintaining separate browser sessions for each thread ID.
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
class AgentCoreBrowserToolSpec(BaseToolSpec):
    """
    AWS Bedrock AgentCore Browser Tool Spec.

    This toolkit provides a set of tools for working with a remote browser environment:

    * navigate_browser - Navigate to a URL
    * click_element - Click on an element using CSS selectors
    * extract_text - Extract all text from the current webpage
    * extract_hyperlinks - Extract all hyperlinks from the current webpage
    * get_elements - Get elements matching a CSS selector
    * navigate_back - Navigate to the previous page
    * current_webpage - Get information about the current webpage

    The toolkit supports multiple threads by maintaining separate browser sessions for each thread ID.
    """

    spec_functions = [
        ("navigate_browser", "anavigate_browser"),
        ("click_element", "aclick_element"),
        ("extract_text", "aextract_text"),
        ("extract_hyperlinks", "aextract_hyperlinks"),
        ("get_elements", "aget_elements"),
        ("navigate_back", "anavigate_back"),
        ("current_webpage", "acurrent_webpage"),
    ]

    def __init__(self, region: Optional[str] = None) -> None:
        """
        Initialize the AWS Bedrock AgentCore Browser Tool Spec.

        Args:
            region (Optional[str]): AWS region to use for Bedrock AgentCore services.
                If not provided, will try to get it from environment variables.

        """
        self.region = region if region is not None else get_aws_region()
        self._browser_clients: Dict[str, BrowserClient] = {}
        self._session_manager = BrowserSessionManager(region=self.region)

    def _get_or_create_browser_client(
        self, thread_id: str = "default"
    ) -> BrowserClient:
        """
        Get or create a browser client for the specified thread.

        Args:
            thread_id: Thread ID for the browser session

        Returns:
            BrowserClient instance

        """
        if thread_id in self._browser_clients:
            return self._browser_clients[thread_id]

        # Create a new browser client for this thread
        browser_client = BrowserClient(self.region)
        self._browser_clients[thread_id] = browser_client
        return browser_client

    def navigate_browser(
        self,
        url: str,
        thread_id: str = "default",
    ) -> str:
        """
        Navigate to a URL (synchronous version).

        Args:
            url (str): URL to navigate to.
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Confirmation message.

        """
        try:
            # Validate URL scheme
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ("http", "https"):
                return f"URL scheme must be 'http' or 'https', got: {parsed_url.scheme}"

            # Get browser and navigate to URL
            browser = self._session_manager.get_sync_browser(thread_id)
            page = get_current_page(browser)
            response = page.goto(url)
            status = response.status if response else "unknown"

            # Release the browser
            self._session_manager.release_sync_browser(thread_id)

            return f"Navigated to {url} with status code {status}"
        except Exception as e:
            return f"Error navigating to URL: {e!s}"

    async def anavigate_browser(
        self,
        url: str,
        thread_id: str = "default",
    ) -> str:
        """
        Navigate to a URL (asynchronous version).

        Args:
            url (str): URL to navigate to.
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Confirmation message.

        """
        try:
            # Validate URL scheme
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ("http", "https"):
                return f"URL scheme must be 'http' or 'https', got: {parsed_url.scheme}"

            # Get browser and navigate to URL
            browser = await self._session_manager.get_async_browser(thread_id)
            page = await aget_current_page(browser)
            response = await page.goto(url)
            status = response.status if response else "unknown"

            # Release the browser
            await self._session_manager.release_async_browser(thread_id)

            return f"Navigated to {url} with status code {status}"
        except Exception as e:
            return f"Error navigating to URL: {e!s}"

    def click_element(
        self,
        selector: str,
        thread_id: str = "default",
    ) -> str:
        """
        Click on an element with the given CSS selector (synchronous version).

        Args:
            selector (str): CSS selector for the element to click on.
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Confirmation message.

        """
        try:
            # Get browser and click on element
            browser = self._session_manager.get_sync_browser(thread_id)
            page = get_current_page(browser)

            try:
                page.click(selector, timeout=5000)
                result = f"Clicked on element with selector '{selector}'"
            except Exception as click_error:
                result = f"Unable to click on element with selector '{selector}': {click_error!s}"

            # Release the browser
            self._session_manager.release_sync_browser(thread_id)

            return result
        except Exception as e:
            return f"Error clicking on element: {e!s}"

    async def aclick_element(
        self,
        selector: str,
        thread_id: str = "default",
    ) -> str:
        """
        Click on an element with the given CSS selector (asynchronous version).

        Args:
            selector (str): CSS selector for the element to click on.
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Confirmation message.

        """
        try:
            # Get browser and click on element
            browser = await self._session_manager.get_async_browser(thread_id)
            page = await aget_current_page(browser)

            try:
                await page.click(selector, timeout=5000)
                result = f"Clicked on element with selector '{selector}'"
            except Exception as click_error:
                result = f"Unable to click on element with selector '{selector}': {click_error!s}"

            # Release the browser
            await self._session_manager.release_async_browser(thread_id)

            return result
        except Exception as e:
            return f"Error clicking on element: {e!s}"

    def extract_text(
        self,
        selector: Optional[str] = None,
        thread_id: str = "default",
    ) -> str:
        """
        Extract text from the current page (synchronous version).

        Args:
            selector (Optional[str]): CSS selector for the element to extract text from. If not provided, extracts text from the entire page.
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: The extracted text.

        """
        try:
            # Get browser and extract text
            browser = self._session_manager.get_sync_browser(thread_id)
            page = get_current_page(browser)

            if selector:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.text_content()
                        result = text if text else "Element found but contains no text"
                    else:
                        result = f"No element found with selector '{selector}'"
                except Exception as selector_error:
                    result = f"Error extracting text from selector '{selector}': {selector_error!s}"
            else:
                # Extract text from the entire page
                result = page.content()

            # Release the browser
            self._session_manager.release_sync_browser(thread_id)

            return result
        except Exception as e:
            return f"Error extracting text: {e!s}"

    async def aextract_text(
        self,
        selector: Optional[str] = None,
        thread_id: str = "default",
    ) -> str:
        """
        Extract text from the current page (asynchronous version).

        Args:
            selector (Optional[str]): CSS selector for the element to extract text from. If not provided, extracts text from the entire page.
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: The extracted text.

        """
        try:
            # Get browser and extract text
            browser = await self._session_manager.get_async_browser(thread_id)
            page = await aget_current_page(browser)

            if selector:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        result = text if text else "Element found but contains no text"
                    else:
                        result = f"No element found with selector '{selector}'"
                except Exception as selector_error:
                    result = f"Error extracting text from selector '{selector}': {selector_error!s}"
            else:
                # Extract text from the entire page
                result = await page.content()

            # Release the browser
            await self._session_manager.release_async_browser(thread_id)

            return result
        except Exception as e:
            return f"Error extracting text: {e!s}"

    def extract_hyperlinks(
        self,
        thread_id: str = "default",
    ) -> str:
        """
        Extract hyperlinks from the current page (synchronous version).

        Args:
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: The extracted hyperlinks.

        """
        try:
            # Get browser and extract hyperlinks
            browser = self._session_manager.get_sync_browser(thread_id)
            page = get_current_page(browser)

            # Extract all hyperlinks from the page
            links = page.eval_on_selector_all(
                "a[href]",
                """
                (elements) => {
                    return elements.map(el => {
                        return {
                            text: el.innerText || el.textContent,
                            href: el.href
                        };
                    });
                }
            """,
            )

            # Format the links
            formatted_links = []
            for i, link in enumerate(links):
                formatted_links.append(
                    f"{i + 1}. {link.get('text', 'No text')}: {link.get('href', 'No href')}"
                )

            result = (
                "\n".join(formatted_links)
                if formatted_links
                else "No hyperlinks found on the page"
            )

            # Release the browser
            self._session_manager.release_sync_browser(thread_id)

            return result
        except Exception as e:
            return f"Error extracting hyperlinks: {e!s}"

    async def aextract_hyperlinks(
        self,
        thread_id: str = "default",
    ) -> str:
        """
        Extract hyperlinks from the current page (asynchronous version).

        Args:
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: The extracted hyperlinks.

        """
        try:
            # Get browser and extract hyperlinks
            browser = await self._session_manager.get_async_browser(thread_id)
            page = await aget_current_page(browser)

            # Extract all hyperlinks from the page
            links = await page.eval_on_selector_all(
                "a[href]",
                """
                (elements) => {
                    return elements.map(el => {
                        return {
                            text: el.innerText || el.textContent,
                            href: el.href
                        };
                    });
                }
            """,
            )

            # Format the links
            formatted_links = []
            for i, link in enumerate(links):
                formatted_links.append(
                    f"{i + 1}. {link.get('text', 'No text')}: {link.get('href', 'No href')}"
                )

            result = (
                "\n".join(formatted_links)
                if formatted_links
                else "No hyperlinks found on the page"
            )

            # Release the browser
            await self._session_manager.release_async_browser(thread_id)

            return result
        except Exception as e:
            return f"Error extracting hyperlinks: {e!s}"

    def get_elements(
        self,
        selector: str,
        thread_id: str = "default",
    ) -> str:
        """
        Get elements matching a CSS selector (synchronous version).

        Args:
            selector (str): CSS selector for the elements to get.
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Information about the matching elements.

        """
        try:
            # Get browser and find elements
            browser = self._session_manager.get_sync_browser(thread_id)
            page = get_current_page(browser)

            # Find elements matching the selector
            elements = page.query_selector_all(selector)

            if not elements:
                result = f"No elements found matching selector '{selector}'"
            else:
                # Extract information about the elements
                elements_info = []
                for i, element in enumerate(elements):
                    tag_name = element.evaluate("el => el.tagName.toLowerCase()")
                    text = element.text_content() or ""
                    attributes = element.evaluate("""
                        (el) => {
                            const attrs = {};
                            for (const attr of el.attributes) {
                                attrs[attr.name] = attr.value;
                            }
                            return attrs;
                        }
                    """)

                    # Format element info
                    attr_str = ", ".join([f'{k}="{v}"' for k, v in attributes.items()])
                    elements_info.append(
                        f"{i + 1}. <{tag_name} {attr_str}>{text}</{tag_name}>"
                    )

                result = (
                    f"Found {len(elements)} element(s) matching selector '{selector}':\n"
                    + "\n".join(elements_info)
                )

            # Release the browser
            self._session_manager.release_sync_browser(thread_id)

            return result
        except Exception as e:
            return f"Error getting elements: {e!s}"

    async def aget_elements(
        self,
        selector: str,
        thread_id: str = "default",
    ) -> str:
        """
        Get elements matching a CSS selector (asynchronous version).

        Args:
            selector (str): CSS selector for the elements to get.
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Information about the matching elements.

        """
        try:
            # Get browser and find elements
            browser = await self._session_manager.get_async_browser(thread_id)
            page = await aget_current_page(browser)

            # Find elements matching the selector
            elements = await page.query_selector_all(selector)

            if not elements:
                result = f"No elements found matching selector '{selector}'"
            else:
                # Extract information about the elements
                elements_info = []
                for i, element in enumerate(elements):
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    text = await element.text_content() or ""
                    attributes = await element.evaluate("""
                        (el) => {
                            const attrs = {};
                            for (const attr of el.attributes) {
                                attrs[attr.name] = attr.value;
                            }
                            return attrs;
                        }
                    """)

                    # Format element info
                    attr_str = ", ".join([f'{k}="{v}"' for k, v in attributes.items()])
                    elements_info.append(
                        f"{i + 1}. <{tag_name} {attr_str}>{text}</{tag_name}>"
                    )

                result = (
                    f"Found {len(elements)} element(s) matching selector '{selector}':\n"
                    + "\n".join(elements_info)
                )

            # Release the browser
            await self._session_manager.release_async_browser(thread_id)

            return result
        except Exception as e:
            return f"Error getting elements: {e!s}"

    def navigate_back(
        self,
        thread_id: str = "default",
    ) -> str:
        """
        Navigate to the previous page (synchronous version).

        Args:
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Confirmation message.

        """
        try:
            # Get browser and navigate back
            browser = self._session_manager.get_sync_browser(thread_id)
            page = get_current_page(browser)

            # Navigate back
            response = page.go_back()

            # Get the current URL after navigating back
            current_url = page.url if response else "unknown"

            # Release the browser
            self._session_manager.release_sync_browser(thread_id)

            if response:
                return f"Navigated back to {current_url}"
            else:
                return "Could not navigate back (no previous page in history)"
        except Exception as e:
            return f"Error navigating back: {e!s}"

    async def anavigate_back(
        self,
        thread_id: str = "default",
    ) -> str:
        """
        Navigate to the previous page (asynchronous version).

        Args:
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Confirmation message.

        """
        try:
            # Get browser and navigate back
            browser = await self._session_manager.get_async_browser(thread_id)
            page = await aget_current_page(browser)

            # Navigate back
            response = await page.go_back()

            # Get the current URL after navigating back
            current_url = page.url if response else "unknown"

            # Release the browser
            await self._session_manager.release_async_browser(thread_id)

            if response:
                return f"Navigated back to {current_url}"
            else:
                return "Could not navigate back (no previous page in history)"
        except Exception as e:
            return f"Error navigating back: {e!s}"

    def current_webpage(
        self,
        thread_id: str = "default",
    ) -> str:
        """
        Get information about the current webpage (synchronous version).

        Args:
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Information about the current webpage.

        """
        try:
            # Get browser and get current webpage info
            browser = self._session_manager.get_sync_browser(thread_id)
            page = get_current_page(browser)

            # Get the current URL
            url = page.url

            # Get the page title
            title = page.title()

            # Get basic page metrics
            metrics = page.evaluate("""
                () => {
                    return {
                        width: document.documentElement.clientWidth,
                        height: document.documentElement.clientHeight,
                        links: document.querySelectorAll('a').length,
                        images: document.querySelectorAll('img').length,
                        forms: document.querySelectorAll('form').length
                    }
                }
            """)

            # Format the result
            result = f"Current webpage information:\n"
            result += f"URL: {url}\n"
            result += f"Title: {title}\n"
            result += f"Viewport size: {metrics['width']}x{metrics['height']}\n"
            result += f"Links: {metrics['links']}\n"
            result += f"Images: {metrics['images']}\n"
            result += f"Forms: {metrics['forms']}"

            # Release the browser
            self._session_manager.release_sync_browser(thread_id)

            return result
        except Exception as e:
            return f"Error getting current webpage information: {e!s}"

    async def acurrent_webpage(
        self,
        thread_id: str = "default",
    ) -> str:
        """
        Get information about the current webpage (asynchronous version).

        Args:
            thread_id (str): Thread ID for the browser session.

        Returns:
            str: Information about the current webpage.

        """
        try:
            # Get browser and get current webpage info
            browser = await self._session_manager.get_async_browser(thread_id)
            page = await aget_current_page(browser)

            # Get the current URL
            url = page.url

            # Get the page title
            title = await page.title()

            # Get basic page metrics
            metrics = await page.evaluate("""
                () => {
                    return {
                        width: document.documentElement.clientWidth,
                        height: document.documentElement.clientHeight,
                        links: document.querySelectorAll('a').length,
                        images: document.querySelectorAll('img').length,
                        forms: document.querySelectorAll('form').length
                    }
                }
            """)

            # Format the result
            result = f"Current webpage information:\n"
            result += f"URL: {url}\n"
            result += f"Title: {title}\n"
            result += f"Viewport size: {metrics['width']}x{metrics['height']}\n"
            result += f"Links: {metrics['links']}\n"
            result += f"Images: {metrics['images']}\n"
            result += f"Forms: {metrics['forms']}"

            # Release the browser
            await self._session_manager.release_async_browser(thread_id)

            return result
        except Exception as e:
            return f"Error getting current webpage information: {e!s}"

    async def cleanup(self, thread_id: Optional[str] = None) -> None:
        """
        Clean up resources

        Args:
            thread_id: Optional thread ID to clean up. If None, cleans up all sessions.

        """
        if thread_id:
            # Clean up a specific thread's session
            if thread_id in self._browser_clients:
                try:
                    self._browser_clients[thread_id].stop()
                    del self._browser_clients[thread_id]
                    logger.info(f"Browser session for thread {thread_id} cleaned up")
                except Exception as e:
                    logger.warning(
                        f"Error stopping browser for thread {thread_id}: {e}"
                    )
        else:
            # Clean up all sessions
            thread_ids = list(self._browser_clients.keys())
            for tid in thread_ids:
                try:
                    self._browser_clients[tid].stop()
                except Exception as e:
                    logger.warning(f"Error stopping browser for thread {tid}: {e}")

            self._browser_clients = {}
            logger.info("All browser sessions cleaned up")

```
  
---|---  
###  navigate_browser #
```
navigate_browser(url: str, thread_id: str = 'default') -> str

```

Navigate to a URL (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url` |  `str` |  URL to navigate to. |  _required_  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Confirmation message.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
def navigate_browser(
    self,
    url: str,
    thread_id: str = "default",
) -> str:
    """
    Navigate to a URL (synchronous version).

    Args:
        url (str): URL to navigate to.
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Confirmation message.

    """
    try:
        # Validate URL scheme
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            return f"URL scheme must be 'http' or 'https', got: {parsed_url.scheme}"

        # Get browser and navigate to URL
        browser = self._session_manager.get_sync_browser(thread_id)
        page = get_current_page(browser)
        response = page.goto(url)
        status = response.status if response else "unknown"

        # Release the browser
        self._session_manager.release_sync_browser(thread_id)

        return f"Navigated to {url} with status code {status}"
    except Exception as e:
        return f"Error navigating to URL: {e!s}"

```
  
---|---  
###  anavigate_browser `async` #
```
anavigate_browser(url: str, thread_id: str = 'default') -> str

```

Navigate to a URL (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url` |  `str` |  URL to navigate to. |  _required_  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Confirmation message.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
async def anavigate_browser(
    self,
    url: str,
    thread_id: str = "default",
) -> str:
    """
    Navigate to a URL (asynchronous version).

    Args:
        url (str): URL to navigate to.
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Confirmation message.

    """
    try:
        # Validate URL scheme
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            return f"URL scheme must be 'http' or 'https', got: {parsed_url.scheme}"

        # Get browser and navigate to URL
        browser = await self._session_manager.get_async_browser(thread_id)
        page = await aget_current_page(browser)
        response = await page.goto(url)
        status = response.status if response else "unknown"

        # Release the browser
        await self._session_manager.release_async_browser(thread_id)

        return f"Navigated to {url} with status code {status}"
    except Exception as e:
        return f"Error navigating to URL: {e!s}"

```
  
---|---  
###  click_element #
```
click_element(selector: str, thread_id: str = 'default') -> str

```

Click on an element with the given CSS selector (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `str` |  CSS selector for the element to click on. |  _required_  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Confirmation message.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
def click_element(
    self,
    selector: str,
    thread_id: str = "default",
) -> str:
    """
    Click on an element with the given CSS selector (synchronous version).

    Args:
        selector (str): CSS selector for the element to click on.
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Confirmation message.

    """
    try:
        # Get browser and click on element
        browser = self._session_manager.get_sync_browser(thread_id)
        page = get_current_page(browser)

        try:
            page.click(selector, timeout=5000)
            result = f"Clicked on element with selector '{selector}'"
        except Exception as click_error:
            result = f"Unable to click on element with selector '{selector}': {click_error!s}"

        # Release the browser
        self._session_manager.release_sync_browser(thread_id)

        return result
    except Exception as e:
        return f"Error clicking on element: {e!s}"

```
  
---|---  
###  aclick_element `async` #
```
aclick_element(selector: str, thread_id: str = 'default') -> str

```

Click on an element with the given CSS selector (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `str` |  CSS selector for the element to click on. |  _required_  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Confirmation message.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
async def aclick_element(
    self,
    selector: str,
    thread_id: str = "default",
) -> str:
    """
    Click on an element with the given CSS selector (asynchronous version).

    Args:
        selector (str): CSS selector for the element to click on.
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Confirmation message.

    """
    try:
        # Get browser and click on element
        browser = await self._session_manager.get_async_browser(thread_id)
        page = await aget_current_page(browser)

        try:
            await page.click(selector, timeout=5000)
            result = f"Clicked on element with selector '{selector}'"
        except Exception as click_error:
            result = f"Unable to click on element with selector '{selector}': {click_error!s}"

        # Release the browser
        await self._session_manager.release_async_browser(thread_id)

        return result
    except Exception as e:
        return f"Error clicking on element: {e!s}"

```
  
---|---  
###  extract_text #
```
extract_text(selector: Optional[str] = None, thread_id: str = 'default') -> str

```

Extract text from the current page (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `Optional[str]` |  CSS selector for the element to extract text from. If not provided, extracts text from the entire page. |  `None`  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The extracted text.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
def extract_text(
    self,
    selector: Optional[str] = None,
    thread_id: str = "default",
) -> str:
    """
    Extract text from the current page (synchronous version).

    Args:
        selector (Optional[str]): CSS selector for the element to extract text from. If not provided, extracts text from the entire page.
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: The extracted text.

    """
    try:
        # Get browser and extract text
        browser = self._session_manager.get_sync_browser(thread_id)
        page = get_current_page(browser)

        if selector:
            try:
                element = page.query_selector(selector)
                if element:
                    text = element.text_content()
                    result = text if text else "Element found but contains no text"
                else:
                    result = f"No element found with selector '{selector}'"
            except Exception as selector_error:
                result = f"Error extracting text from selector '{selector}': {selector_error!s}"
        else:
            # Extract text from the entire page
            result = page.content()

        # Release the browser
        self._session_manager.release_sync_browser(thread_id)

        return result
    except Exception as e:
        return f"Error extracting text: {e!s}"

```
  
---|---  
###  aextract_text `async` #
```
aextract_text(selector: Optional[str] = None, thread_id: str = 'default') -> str

```

Extract text from the current page (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `Optional[str]` |  CSS selector for the element to extract text from. If not provided, extracts text from the entire page. |  `None`  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The extracted text.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
async def aextract_text(
    self,
    selector: Optional[str] = None,
    thread_id: str = "default",
) -> str:
    """
    Extract text from the current page (asynchronous version).

    Args:
        selector (Optional[str]): CSS selector for the element to extract text from. If not provided, extracts text from the entire page.
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: The extracted text.

    """
    try:
        # Get browser and extract text
        browser = await self._session_manager.get_async_browser(thread_id)
        page = await aget_current_page(browser)

        if selector:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    result = text if text else "Element found but contains no text"
                else:
                    result = f"No element found with selector '{selector}'"
            except Exception as selector_error:
                result = f"Error extracting text from selector '{selector}': {selector_error!s}"
        else:
            # Extract text from the entire page
            result = await page.content()

        # Release the browser
        await self._session_manager.release_async_browser(thread_id)

        return result
    except Exception as e:
        return f"Error extracting text: {e!s}"

```
  
---|---  
###  extract_hyperlinks #
```
extract_hyperlinks(thread_id: str = 'default') -> str

```

Extract hyperlinks from the current page (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The extracted hyperlinks.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
def extract_hyperlinks(
    self,
    thread_id: str = "default",
) -> str:
    """
    Extract hyperlinks from the current page (synchronous version).

    Args:
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: The extracted hyperlinks.

    """
    try:
        # Get browser and extract hyperlinks
        browser = self._session_manager.get_sync_browser(thread_id)
        page = get_current_page(browser)

        # Extract all hyperlinks from the page
        links = page.eval_on_selector_all(
            "a[href]",
            """
            (elements) => {
                return elements.map(el => {
                    return {
                        text: el.innerText || el.textContent,
                        href: el.href
                    };
                });
            }
        """,
        )

        # Format the links
        formatted_links = []
        for i, link in enumerate(links):
            formatted_links.append(
                f"{i + 1}. {link.get('text', 'No text')}: {link.get('href', 'No href')}"
            )

        result = (
            "\n".join(formatted_links)
            if formatted_links
            else "No hyperlinks found on the page"
        )

        # Release the browser
        self._session_manager.release_sync_browser(thread_id)

        return result
    except Exception as e:
        return f"Error extracting hyperlinks: {e!s}"

```
  
---|---  
###  aextract_hyperlinks `async` #
```
aextract_hyperlinks(thread_id: str = 'default') -> str

```

Extract hyperlinks from the current page (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The extracted hyperlinks.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
async def aextract_hyperlinks(
    self,
    thread_id: str = "default",
) -> str:
    """
    Extract hyperlinks from the current page (asynchronous version).

    Args:
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: The extracted hyperlinks.

    """
    try:
        # Get browser and extract hyperlinks
        browser = await self._session_manager.get_async_browser(thread_id)
        page = await aget_current_page(browser)

        # Extract all hyperlinks from the page
        links = await page.eval_on_selector_all(
            "a[href]",
            """
            (elements) => {
                return elements.map(el => {
                    return {
                        text: el.innerText || el.textContent,
                        href: el.href
                    };
                });
            }
        """,
        )

        # Format the links
        formatted_links = []
        for i, link in enumerate(links):
            formatted_links.append(
                f"{i + 1}. {link.get('text', 'No text')}: {link.get('href', 'No href')}"
            )

        result = (
            "\n".join(formatted_links)
            if formatted_links
            else "No hyperlinks found on the page"
        )

        # Release the browser
        await self._session_manager.release_async_browser(thread_id)

        return result
    except Exception as e:
        return f"Error extracting hyperlinks: {e!s}"

```
  
---|---  
###  get_elements #
```
get_elements(selector: str, thread_id: str = 'default') -> str

```

Get elements matching a CSS selector (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `str` |  CSS selector for the elements to get. |  _required_  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Information about the matching elements.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
def get_elements(
    self,
    selector: str,
    thread_id: str = "default",
) -> str:
    """
    Get elements matching a CSS selector (synchronous version).

    Args:
        selector (str): CSS selector for the elements to get.
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Information about the matching elements.

    """
    try:
        # Get browser and find elements
        browser = self._session_manager.get_sync_browser(thread_id)
        page = get_current_page(browser)

        # Find elements matching the selector
        elements = page.query_selector_all(selector)

        if not elements:
            result = f"No elements found matching selector '{selector}'"
        else:
            # Extract information about the elements
            elements_info = []
            for i, element in enumerate(elements):
                tag_name = element.evaluate("el => el.tagName.toLowerCase()")
                text = element.text_content() or ""
                attributes = element.evaluate("""
                    (el) => {
                        const attrs = {};
                        for (const attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        return attrs;
                    }
                """)

                # Format element info
                attr_str = ", ".join([f'{k}="{v}"' for k, v in attributes.items()])
                elements_info.append(
                    f"{i + 1}. <{tag_name} {attr_str}>{text}</{tag_name}>"
                )

            result = (
                f"Found {len(elements)} element(s) matching selector '{selector}':\n"
                + "\n".join(elements_info)
            )

        # Release the browser
        self._session_manager.release_sync_browser(thread_id)

        return result
    except Exception as e:
        return f"Error getting elements: {e!s}"

```
  
---|---  
###  aget_elements `async` #
```
aget_elements(selector: str, thread_id: str = 'default') -> str

```

Get elements matching a CSS selector (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `str` |  CSS selector for the elements to get. |  _required_  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Information about the matching elements.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
async def aget_elements(
    self,
    selector: str,
    thread_id: str = "default",
) -> str:
    """
    Get elements matching a CSS selector (asynchronous version).

    Args:
        selector (str): CSS selector for the elements to get.
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Information about the matching elements.

    """
    try:
        # Get browser and find elements
        browser = await self._session_manager.get_async_browser(thread_id)
        page = await aget_current_page(browser)

        # Find elements matching the selector
        elements = await page.query_selector_all(selector)

        if not elements:
            result = f"No elements found matching selector '{selector}'"
        else:
            # Extract information about the elements
            elements_info = []
            for i, element in enumerate(elements):
                tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                text = await element.text_content() or ""
                attributes = await element.evaluate("""
                    (el) => {
                        const attrs = {};
                        for (const attr of el.attributes) {
                            attrs[attr.name] = attr.value;
                        }
                        return attrs;
                    }
                """)

                # Format element info
                attr_str = ", ".join([f'{k}="{v}"' for k, v in attributes.items()])
                elements_info.append(
                    f"{i + 1}. <{tag_name} {attr_str}>{text}</{tag_name}>"
                )

            result = (
                f"Found {len(elements)} element(s) matching selector '{selector}':\n"
                + "\n".join(elements_info)
            )

        # Release the browser
        await self._session_manager.release_async_browser(thread_id)

        return result
    except Exception as e:
        return f"Error getting elements: {e!s}"

```
  
---|---  
###  navigate_back #
```
navigate_back(thread_id: str = 'default') -> str

```

Navigate to the previous page (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Confirmation message.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
def navigate_back(
    self,
    thread_id: str = "default",
) -> str:
    """
    Navigate to the previous page (synchronous version).

    Args:
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Confirmation message.

    """
    try:
        # Get browser and navigate back
        browser = self._session_manager.get_sync_browser(thread_id)
        page = get_current_page(browser)

        # Navigate back
        response = page.go_back()

        # Get the current URL after navigating back
        current_url = page.url if response else "unknown"

        # Release the browser
        self._session_manager.release_sync_browser(thread_id)

        if response:
            return f"Navigated back to {current_url}"
        else:
            return "Could not navigate back (no previous page in history)"
    except Exception as e:
        return f"Error navigating back: {e!s}"

```
  
---|---  
###  anavigate_back `async` #
```
anavigate_back(thread_id: str = 'default') -> str

```

Navigate to the previous page (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Confirmation message.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
async def anavigate_back(
    self,
    thread_id: str = "default",
) -> str:
    """
    Navigate to the previous page (asynchronous version).

    Args:
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Confirmation message.

    """
    try:
        # Get browser and navigate back
        browser = await self._session_manager.get_async_browser(thread_id)
        page = await aget_current_page(browser)

        # Navigate back
        response = await page.go_back()

        # Get the current URL after navigating back
        current_url = page.url if response else "unknown"

        # Release the browser
        await self._session_manager.release_async_browser(thread_id)

        if response:
            return f"Navigated back to {current_url}"
        else:
            return "Could not navigate back (no previous page in history)"
    except Exception as e:
        return f"Error navigating back: {e!s}"

```
  
---|---  
###  current_webpage #
```
current_webpage(thread_id: str = 'default') -> str

```

Get information about the current webpage (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Information about the current webpage.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
def current_webpage(
    self,
    thread_id: str = "default",
) -> str:
    """
    Get information about the current webpage (synchronous version).

    Args:
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Information about the current webpage.

    """
    try:
        # Get browser and get current webpage info
        browser = self._session_manager.get_sync_browser(thread_id)
        page = get_current_page(browser)

        # Get the current URL
        url = page.url

        # Get the page title
        title = page.title()

        # Get basic page metrics
        metrics = page.evaluate("""
            () => {
                return {
                    width: document.documentElement.clientWidth,
                    height: document.documentElement.clientHeight,
                    links: document.querySelectorAll('a').length,
                    images: document.querySelectorAll('img').length,
                    forms: document.querySelectorAll('form').length
                }
            }
        """)

        # Format the result
        result = f"Current webpage information:\n"
        result += f"URL: {url}\n"
        result += f"Title: {title}\n"
        result += f"Viewport size: {metrics['width']}x{metrics['height']}\n"
        result += f"Links: {metrics['links']}\n"
        result += f"Images: {metrics['images']}\n"
        result += f"Forms: {metrics['forms']}"

        # Release the browser
        self._session_manager.release_sync_browser(thread_id)

        return result
    except Exception as e:
        return f"Error getting current webpage information: {e!s}"

```
  
---|---  
###  acurrent_webpage `async` #
```
acurrent_webpage(thread_id: str = 'default') -> str

```

Get information about the current webpage (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`thread_id` |  `str` |  Thread ID for the browser session. |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  Information about the current webpage.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
async def acurrent_webpage(
    self,
    thread_id: str = "default",
) -> str:
    """
    Get information about the current webpage (asynchronous version).

    Args:
        thread_id (str): Thread ID for the browser session.

    Returns:
        str: Information about the current webpage.

    """
    try:
        # Get browser and get current webpage info
        browser = await self._session_manager.get_async_browser(thread_id)
        page = await aget_current_page(browser)

        # Get the current URL
        url = page.url

        # Get the page title
        title = await page.title()

        # Get basic page metrics
        metrics = await page.evaluate("""
            () => {
                return {
                    width: document.documentElement.clientWidth,
                    height: document.documentElement.clientHeight,
                    links: document.querySelectorAll('a').length,
                    images: document.querySelectorAll('img').length,
                    forms: document.querySelectorAll('form').length
                }
            }
        """)

        # Format the result
        result = f"Current webpage information:\n"
        result += f"URL: {url}\n"
        result += f"Title: {title}\n"
        result += f"Viewport size: {metrics['width']}x{metrics['height']}\n"
        result += f"Links: {metrics['links']}\n"
        result += f"Images: {metrics['images']}\n"
        result += f"Forms: {metrics['forms']}"

        # Release the browser
        await self._session_manager.release_async_browser(thread_id)

        return result
    except Exception as e:
        return f"Error getting current webpage information: {e!s}"

```
  
---|---  
###  cleanup `async` #
```
cleanup(thread_id: Optional[str] = None) -> None

```

Clean up resources
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`thread_id` |  `Optional[str]` |  Optional thread ID to clean up. If None, cleans up all sessions. |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/browser/base.py`

| ```
async def cleanup(self, thread_id: Optional[str] = None) -> None:
    """
    Clean up resources

    Args:
        thread_id: Optional thread ID to clean up. If None, cleans up all sessions.

    """
    if thread_id:
        # Clean up a specific thread's session
        if thread_id in self._browser_clients:
            try:
                self._browser_clients[thread_id].stop()
                del self._browser_clients[thread_id]
                logger.info(f"Browser session for thread {thread_id} cleaned up")
            except Exception as e:
                logger.warning(
                    f"Error stopping browser for thread {thread_id}: {e}"
                )
    else:
        # Clean up all sessions
        thread_ids = list(self._browser_clients.keys())
        for tid in thread_ids:
            try:
                self._browser_clients[tid].stop()
            except Exception as e:
                logger.warning(f"Error stopping browser for thread {tid}: {e}")

        self._browser_clients = {}
        logger.info("All browser sessions cleaned up")

```
  
---|---  
##  AgentCoreCodeInterpreterToolSpec #
Bases: `BaseToolSpec`
AWS Bedrock AgentCore Code Interpreter Tool Spec.
This toolkit provides a set of tools for working with a remote code interpreter environment:
  * execute_code - Run code in various languages (primarily Python)
  * execute_command - Run shell commands
  * read_files - Read content of files in the environment
  * list_files - List files in directories
  * delete_files - Remove files from the environment
  * write_files - Create or update files
  * start_command - Start long-running commands asynchronously
  * get_task - Check status of async tasks
  * stop_task - Stop running tasks


The toolkit lazily initializes the code interpreter session on first use. It supports multiple threads by maintaining separate code interpreter sessions for each thread ID.
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
class AgentCoreCodeInterpreterToolSpec(BaseToolSpec):
    """
    AWS Bedrock AgentCore Code Interpreter Tool Spec.

    This toolkit provides a set of tools for working with a remote code interpreter environment:

    * execute_code - Run code in various languages (primarily Python)
    * execute_command - Run shell commands
    * read_files - Read content of files in the environment
    * list_files - List files in directories
    * delete_files - Remove files from the environment
    * write_files - Create or update files
    * start_command - Start long-running commands asynchronously
    * get_task - Check status of async tasks
    * stop_task - Stop running tasks

    The toolkit lazily initializes the code interpreter session on first use.
    It supports multiple threads by maintaining separate code interpreter sessions for each thread ID.
    """

    spec_functions = [
        ("execute_code", "aexecute_code"),
        ("execute_command", "aexecute_command"),
        ("read_files", "aread_files"),
        ("list_files", "alist_files"),
        ("delete_files", "adelete_files"),
        ("write_files", "awrite_files"),
        ("start_command", "astart_command"),
        ("get_task", "aget_task"),
        ("stop_task", "astop_task"),
    ]

    def __init__(self, region: Optional[str] = None) -> None:
        """
        Initialize the AWS Bedrock AgentCore Code Interpreter Tool Spec.

        Args:
            region (Optional[str]): AWS region to use for Bedrock AgentCore services.
                If not provided, will try to get it from environment variables.

        """
        self.region = region if region is not None else get_aws_region()
        self._code_interpreters: Dict[str, CodeInterpreter] = {}

    def _get_or_create_interpreter(self, thread_id: str = "default") -> CodeInterpreter:
        """
        Get or create a code interpreter for the specified thread.

        Args:
            thread_id: Thread ID for the code interpreter session

        Returns:
            CodeInterpreter instance

        """
        if thread_id in self._code_interpreters:
            return self._code_interpreters[thread_id]

        # Create a new code interpreter for this thread
        code_interpreter = CodeInterpreter(region=self.region)
        code_interpreter.start()
        logger.info(
            f"Started code interpreter with session_id:{code_interpreter.session_id} for thread:{thread_id}"
        )

        # Store the interpreter
        self._code_interpreters[thread_id] = code_interpreter
        return code_interpreter

    def execute_code(
        self,
        code: str,
        language: str = "python",
        clear_context: bool = False,
        thread_id: str = "default",
    ) -> str:
        """
        Execute code in the code interpreter sandbox (synchronous version).

        Args:
            code (str): The code to execute.
            language (str): The programming language of the code. Default is "python".
            clear_context (bool): Whether to clear execution context. Default is False.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the code execution.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # Execute code
            response = code_interpreter.invoke(
                method="executeCode",
                params={
                    "code": code,
                    "language": language,
                    "clearContext": clear_context,
                },
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error executing code: {e!s}"

    async def aexecute_code(
        self,
        code: str,
        language: str = "python",
        clear_context: bool = False,
        thread_id: str = "default",
    ) -> str:
        """
        Execute code in the code interpreter sandbox (asynchronous version).

        Args:
            code (str): The code to execute.
            language (str): The programming language of the code. Default is "python".
            clear_context (bool): Whether to clear execution context. Default is False.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the code execution.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.execute_code(
            code=code,
            language=language,
            clear_context=clear_context,
            thread_id=thread_id,
        )

    def execute_command(
        self,
        command: str,
        thread_id: str = "default",
    ) -> str:
        """
        Execute a shell command in the code interpreter sandbox (synchronous version).

        Args:
            command (str): The command to execute.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the command execution.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # Execute command
            response = code_interpreter.invoke(
                method="executeCommand", params={"command": command}
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error executing command: {e!s}"

    async def aexecute_command(
        self,
        command: str,
        thread_id: str = "default",
    ) -> str:
        """
        Execute a shell command in the code interpreter sandbox (asynchronous version).

        Args:
            command (str): The command to execute.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the command execution.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.execute_command(command=command, thread_id=thread_id)

    def read_files(
        self,
        paths: List[str],
        thread_id: str = "default",
    ) -> str:
        """
        Read content of files in the environment (synchronous version).

        Args:
            paths (List[str]): List of file paths to read.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The content of the files.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # Read files
            response = code_interpreter.invoke(
                method="readFiles", params={"paths": paths}
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error reading files: {e!s}"

    async def aread_files(
        self,
        paths: List[str],
        thread_id: str = "default",
    ) -> str:
        """
        Read content of files in the environment (asynchronous version).

        Args:
            paths (List[str]): List of file paths to read.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The content of the files.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.read_files(paths=paths, thread_id=thread_id)

    def list_files(
        self,
        directory_path: str = "",
        thread_id: str = "default",
    ) -> str:
        """
        List files in directories in the environment (synchronous version).

        Args:
            directory_path (str): Path to the directory to list. Default is current directory.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The list of files.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # List files
            response = code_interpreter.invoke(
                method="listFiles", params={"directoryPath": directory_path}
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error listing files: {e!s}"

    async def alist_files(
        self,
        directory_path: str = "",
        thread_id: str = "default",
    ) -> str:
        """
        List files in directories in the environment (asynchronous version).

        Args:
            directory_path (str): Path to the directory to list. Default is current directory.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The list of files.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.list_files(directory_path=directory_path, thread_id=thread_id)

    def delete_files(
        self,
        paths: List[str],
        thread_id: str = "default",
    ) -> str:
        """
        Remove files from the environment (synchronous version).

        Args:
            paths (List[str]): List of file paths to delete.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the delete operation.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # Remove files
            response = code_interpreter.invoke(
                method="removeFiles", params={"paths": paths}
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error deleting files: {e!s}"

    async def adelete_files(
        self,
        paths: List[str],
        thread_id: str = "default",
    ) -> str:
        """
        Remove files from the environment (asynchronous version).

        Args:
            paths (List[str]): List of file paths to delete.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the delete operation.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.delete_files(paths=paths, thread_id=thread_id)

    def write_files(
        self,
        files: List[Dict[str, str]],
        thread_id: str = "default",
    ) -> str:
        """
        Create or update files in the environment (synchronous version).

        Args:
            files (List[Dict[str, str]]): List of dictionaries with path and text fields.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the write operation.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # Write files
            response = code_interpreter.invoke(
                method="writeFiles", params={"content": files}
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error writing files: {e!s}"

    async def awrite_files(
        self,
        files: List[Dict[str, str]],
        thread_id: str = "default",
    ) -> str:
        """
        Create or update files in the environment (asynchronous version).

        Args:
            files (List[Dict[str, str]]): List of dictionaries with path and text fields.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the write operation.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.write_files(files=files, thread_id=thread_id)

    def start_command(
        self,
        command: str,
        thread_id: str = "default",
    ) -> str:
        """
        Start a long-running command asynchronously (synchronous version).

        Args:
            command (str): The command to execute asynchronously.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The task ID and status.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # Start command execution
            response = code_interpreter.invoke(
                method="startCommandExecution", params={"command": command}
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error starting command: {e!s}"

    async def astart_command(
        self,
        command: str,
        thread_id: str = "default",
    ) -> str:
        """
        Start a long-running command asynchronously (asynchronous version).

        Args:
            command (str): The command to execute asynchronously.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The task ID and status.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.start_command(command=command, thread_id=thread_id)

    def get_task(
        self,
        task_id: str,
        thread_id: str = "default",
    ) -> str:
        """
        Check status of an async task (synchronous version).

        Args:
            task_id (str): The ID of the task to check.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The task status.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # Get task status
            response = code_interpreter.invoke(
                method="getTask", params={"taskId": task_id}
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error getting task status: {e!s}"

    async def aget_task(
        self,
        task_id: str,
        thread_id: str = "default",
    ) -> str:
        """
        Check status of an async task (asynchronous version).

        Args:
            task_id (str): The ID of the task to check.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The task status.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.get_task(task_id=task_id, thread_id=thread_id)

    def stop_task(
        self,
        task_id: str,
        thread_id: str = "default",
    ) -> str:
        """
        Stop a running task (synchronous version).

        Args:
            task_id (str): The ID of the task to stop.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the stop operation.

        """
        try:
            # Get or create code interpreter
            code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

            # Stop task
            response = code_interpreter.invoke(
                method="stopTask", params={"taskId": task_id}
            )

            return extract_output_from_stream(response)
        except Exception as e:
            return f"Error stopping task: {e!s}"

    async def astop_task(
        self,
        task_id: str,
        thread_id: str = "default",
    ) -> str:
        """
        Stop a running task (asynchronous version).

        Args:
            task_id (str): The ID of the task to stop.
            thread_id (str): Thread ID for the code interpreter session. Default is "default".

        Returns:
            str: The result of the stop operation.

        """
        # Use the synchronous version as the underlying API is thread-safe
        return self.stop_task(task_id=task_id, thread_id=thread_id)

    async def cleanup(self, thread_id: Optional[str] = None) -> None:
        """
        Clean up resources

        Args:
            thread_id: Optional thread ID to clean up. If None, cleans up all sessions.

        """
        if thread_id:
            # Clean up a specific thread's session
            if thread_id in self._code_interpreters:
                try:
                    self._code_interpreters[thread_id].stop()
                    del self._code_interpreters[thread_id]
                    logger.info(
                        f"Code interpreter session for thread {thread_id} cleaned up"
                    )
                except Exception as e:
                    logger.warning(
                        f"Error stopping code interpreter for thread {thread_id}: {e}"
                    )
        else:
            # Clean up all sessions
            thread_ids = list(self._code_interpreters.keys())
            for tid in thread_ids:
                try:
                    self._code_interpreters[tid].stop()
                except Exception as e:
                    logger.warning(
                        f"Error stopping code interpreter for thread {tid}: {e}"
                    )

            self._code_interpreters = {}
            logger.info("All code interpreter sessions cleaned up")

```
  
---|---  
###  execute_code #
```
execute_code(code: str, language: str = 'python', clear_context: bool = False, thread_id: str = 'default') -> str

```

Execute code in the code interpreter sandbox (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`code` |  `str` |  The code to execute. |  _required_  
`language` |  `str` |  The programming language of the code. Default is "python". |  `'python'`  
`clear_context` |  `bool` |  Whether to clear execution context. Default is False. |  `False`  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the code execution.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def execute_code(
    self,
    code: str,
    language: str = "python",
    clear_context: bool = False,
    thread_id: str = "default",
) -> str:
    """
    Execute code in the code interpreter sandbox (synchronous version).

    Args:
        code (str): The code to execute.
        language (str): The programming language of the code. Default is "python".
        clear_context (bool): Whether to clear execution context. Default is False.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the code execution.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # Execute code
        response = code_interpreter.invoke(
            method="executeCode",
            params={
                "code": code,
                "language": language,
                "clearContext": clear_context,
            },
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error executing code: {e!s}"

```
  
---|---  
###  aexecute_code `async` #
```
aexecute_code(code: str, language: str = 'python', clear_context: bool = False, thread_id: str = 'default') -> str

```

Execute code in the code interpreter sandbox (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`code` |  `str` |  The code to execute. |  _required_  
`language` |  `str` |  The programming language of the code. Default is "python". |  `'python'`  
`clear_context` |  `bool` |  Whether to clear execution context. Default is False. |  `False`  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the code execution.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def aexecute_code(
    self,
    code: str,
    language: str = "python",
    clear_context: bool = False,
    thread_id: str = "default",
) -> str:
    """
    Execute code in the code interpreter sandbox (asynchronous version).

    Args:
        code (str): The code to execute.
        language (str): The programming language of the code. Default is "python".
        clear_context (bool): Whether to clear execution context. Default is False.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the code execution.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.execute_code(
        code=code,
        language=language,
        clear_context=clear_context,
        thread_id=thread_id,
    )

```
  
---|---  
###  execute_command #
```
execute_command(command: str, thread_id: str = 'default') -> str

```

Execute a shell command in the code interpreter sandbox (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`command` |  `str` |  The command to execute. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the command execution.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def execute_command(
    self,
    command: str,
    thread_id: str = "default",
) -> str:
    """
    Execute a shell command in the code interpreter sandbox (synchronous version).

    Args:
        command (str): The command to execute.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the command execution.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # Execute command
        response = code_interpreter.invoke(
            method="executeCommand", params={"command": command}
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error executing command: {e!s}"

```
  
---|---  
###  aexecute_command `async` #
```
aexecute_command(command: str, thread_id: str = 'default') -> str

```

Execute a shell command in the code interpreter sandbox (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`command` |  `str` |  The command to execute. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the command execution.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def aexecute_command(
    self,
    command: str,
    thread_id: str = "default",
) -> str:
    """
    Execute a shell command in the code interpreter sandbox (asynchronous version).

    Args:
        command (str): The command to execute.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the command execution.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.execute_command(command=command, thread_id=thread_id)

```
  
---|---  
###  read_files #
```
read_files(paths: List[str], thread_id: str = 'default') -> str

```

Read content of files in the environment (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`paths` |  `List[str]` |  List of file paths to read. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The content of the files.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def read_files(
    self,
    paths: List[str],
    thread_id: str = "default",
) -> str:
    """
    Read content of files in the environment (synchronous version).

    Args:
        paths (List[str]): List of file paths to read.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The content of the files.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # Read files
        response = code_interpreter.invoke(
            method="readFiles", params={"paths": paths}
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error reading files: {e!s}"

```
  
---|---  
###  aread_files `async` #
```
aread_files(paths: List[str], thread_id: str = 'default') -> str

```

Read content of files in the environment (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`paths` |  `List[str]` |  List of file paths to read. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The content of the files.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def aread_files(
    self,
    paths: List[str],
    thread_id: str = "default",
) -> str:
    """
    Read content of files in the environment (asynchronous version).

    Args:
        paths (List[str]): List of file paths to read.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The content of the files.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.read_files(paths=paths, thread_id=thread_id)

```
  
---|---  
###  list_files #
```
list_files(directory_path: str = '', thread_id: str = 'default') -> str

```

List files in directories in the environment (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`directory_path` |  `str` |  Path to the directory to list. Default is current directory. |  `''`  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The list of files.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def list_files(
    self,
    directory_path: str = "",
    thread_id: str = "default",
) -> str:
    """
    List files in directories in the environment (synchronous version).

    Args:
        directory_path (str): Path to the directory to list. Default is current directory.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The list of files.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # List files
        response = code_interpreter.invoke(
            method="listFiles", params={"directoryPath": directory_path}
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error listing files: {e!s}"

```
  
---|---  
###  alist_files `async` #
```
alist_files(directory_path: str = '', thread_id: str = 'default') -> str

```

List files in directories in the environment (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`directory_path` |  `str` |  Path to the directory to list. Default is current directory. |  `''`  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The list of files.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def alist_files(
    self,
    directory_path: str = "",
    thread_id: str = "default",
) -> str:
    """
    List files in directories in the environment (asynchronous version).

    Args:
        directory_path (str): Path to the directory to list. Default is current directory.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The list of files.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.list_files(directory_path=directory_path, thread_id=thread_id)

```
  
---|---  
###  delete_files #
```
delete_files(paths: List[str], thread_id: str = 'default') -> str

```

Remove files from the environment (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`paths` |  `List[str]` |  List of file paths to delete. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the delete operation.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def delete_files(
    self,
    paths: List[str],
    thread_id: str = "default",
) -> str:
    """
    Remove files from the environment (synchronous version).

    Args:
        paths (List[str]): List of file paths to delete.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the delete operation.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # Remove files
        response = code_interpreter.invoke(
            method="removeFiles", params={"paths": paths}
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error deleting files: {e!s}"

```
  
---|---  
###  adelete_files `async` #
```
adelete_files(paths: List[str], thread_id: str = 'default') -> str

```

Remove files from the environment (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`paths` |  `List[str]` |  List of file paths to delete. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the delete operation.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def adelete_files(
    self,
    paths: List[str],
    thread_id: str = "default",
) -> str:
    """
    Remove files from the environment (asynchronous version).

    Args:
        paths (List[str]): List of file paths to delete.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the delete operation.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.delete_files(paths=paths, thread_id=thread_id)

```
  
---|---  
###  write_files #
```
write_files(files: List[Dict[str, str]], thread_id: str = 'default') -> str

```

Create or update files in the environment (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`files` |  `List[Dict[str, str]]` |  List of dictionaries with path and text fields. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the write operation.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def write_files(
    self,
    files: List[Dict[str, str]],
    thread_id: str = "default",
) -> str:
    """
    Create or update files in the environment (synchronous version).

    Args:
        files (List[Dict[str, str]]): List of dictionaries with path and text fields.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the write operation.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # Write files
        response = code_interpreter.invoke(
            method="writeFiles", params={"content": files}
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error writing files: {e!s}"

```
  
---|---  
###  awrite_files `async` #
```
awrite_files(files: List[Dict[str, str]], thread_id: str = 'default') -> str

```

Create or update files in the environment (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`files` |  `List[Dict[str, str]]` |  List of dictionaries with path and text fields. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the write operation.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def awrite_files(
    self,
    files: List[Dict[str, str]],
    thread_id: str = "default",
) -> str:
    """
    Create or update files in the environment (asynchronous version).

    Args:
        files (List[Dict[str, str]]): List of dictionaries with path and text fields.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the write operation.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.write_files(files=files, thread_id=thread_id)

```
  
---|---  
###  start_command #
```
start_command(command: str, thread_id: str = 'default') -> str

```

Start a long-running command asynchronously (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`command` |  `str` |  The command to execute asynchronously. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The task ID and status.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def start_command(
    self,
    command: str,
    thread_id: str = "default",
) -> str:
    """
    Start a long-running command asynchronously (synchronous version).

    Args:
        command (str): The command to execute asynchronously.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The task ID and status.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # Start command execution
        response = code_interpreter.invoke(
            method="startCommandExecution", params={"command": command}
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error starting command: {e!s}"

```
  
---|---  
###  astart_command `async` #
```
astart_command(command: str, thread_id: str = 'default') -> str

```

Start a long-running command asynchronously (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`command` |  `str` |  The command to execute asynchronously. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The task ID and status.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def astart_command(
    self,
    command: str,
    thread_id: str = "default",
) -> str:
    """
    Start a long-running command asynchronously (asynchronous version).

    Args:
        command (str): The command to execute asynchronously.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The task ID and status.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.start_command(command=command, thread_id=thread_id)

```
  
---|---  
###  get_task #
```
get_task(task_id: str, thread_id: str = 'default') -> str

```

Check status of an async task (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  The ID of the task to check. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The task status.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def get_task(
    self,
    task_id: str,
    thread_id: str = "default",
) -> str:
    """
    Check status of an async task (synchronous version).

    Args:
        task_id (str): The ID of the task to check.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The task status.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # Get task status
        response = code_interpreter.invoke(
            method="getTask", params={"taskId": task_id}
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error getting task status: {e!s}"

```
  
---|---  
###  aget_task `async` #
```
aget_task(task_id: str, thread_id: str = 'default') -> str

```

Check status of an async task (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  The ID of the task to check. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The task status.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def aget_task(
    self,
    task_id: str,
    thread_id: str = "default",
) -> str:
    """
    Check status of an async task (asynchronous version).

    Args:
        task_id (str): The ID of the task to check.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The task status.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.get_task(task_id=task_id, thread_id=thread_id)

```
  
---|---  
###  stop_task #
```
stop_task(task_id: str, thread_id: str = 'default') -> str

```

Stop a running task (synchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  The ID of the task to stop. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the stop operation.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
def stop_task(
    self,
    task_id: str,
    thread_id: str = "default",
) -> str:
    """
    Stop a running task (synchronous version).

    Args:
        task_id (str): The ID of the task to stop.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the stop operation.

    """
    try:
        # Get or create code interpreter
        code_interpreter = self._get_or_create_interpreter(thread_id=thread_id)

        # Stop task
        response = code_interpreter.invoke(
            method="stopTask", params={"taskId": task_id}
        )

        return extract_output_from_stream(response)
    except Exception as e:
        return f"Error stopping task: {e!s}"

```
  
---|---  
###  astop_task `async` #
```
astop_task(task_id: str, thread_id: str = 'default') -> str

```

Stop a running task (asynchronous version).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  The ID of the task to stop. |  _required_  
`thread_id` |  `str` |  Thread ID for the code interpreter session. Default is "default". |  `'default'`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The result of the stop operation.  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def astop_task(
    self,
    task_id: str,
    thread_id: str = "default",
) -> str:
    """
    Stop a running task (asynchronous version).

    Args:
        task_id (str): The ID of the task to stop.
        thread_id (str): Thread ID for the code interpreter session. Default is "default".

    Returns:
        str: The result of the stop operation.

    """
    # Use the synchronous version as the underlying API is thread-safe
    return self.stop_task(task_id=task_id, thread_id=thread_id)

```
  
---|---  
###  cleanup `async` #
```
cleanup(thread_id: Optional[str] = None) -> None

```

Clean up resources
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`thread_id` |  `Optional[str]` |  Optional thread ID to clean up. If None, cleans up all sessions. |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-aws-bedrock-agentcore/llama_index/tools/aws_bedrock_agentcore/code_interpreter/base.py`

| ```
async def cleanup(self, thread_id: Optional[str] = None) -> None:
    """
    Clean up resources

    Args:
        thread_id: Optional thread ID to clean up. If None, cleans up all sessions.

    """
    if thread_id:
        # Clean up a specific thread's session
        if thread_id in self._code_interpreters:
            try:
                self._code_interpreters[thread_id].stop()
                del self._code_interpreters[thread_id]
                logger.info(
                    f"Code interpreter session for thread {thread_id} cleaned up"
                )
            except Exception as e:
                logger.warning(
                    f"Error stopping code interpreter for thread {thread_id}: {e}"
                )
    else:
        # Clean up all sessions
        thread_ids = list(self._code_interpreters.keys())
        for tid in thread_ids:
            try:
                self._code_interpreters[tid].stop()
            except Exception as e:
                logger.warning(
                    f"Error stopping code interpreter for thread {tid}: {e}"
                )

        self._code_interpreters = {}
        logger.info("All code interpreter sessions cleaned up")

```
  
---|---
