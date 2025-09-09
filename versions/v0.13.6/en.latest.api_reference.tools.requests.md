# Requests
##  RequestsToolSpec #
Bases: `BaseToolSpec`
Requests Tool.
Source code in `llama-index-integrations/tools/llama-index-tools-requests/llama_index/tools/requests/base.py`

| ```
class RequestsToolSpec(BaseToolSpec):
    """Requests Tool."""

    spec_functions = [
        "get_request",
        "post_request",
        "patch_request",
        "put_request",
        "delete_request",
    ]

    def __init__(self, domain_headers: Optional[dict] = None, timeout_seconds=None):
        self.domain_headers = {} if domain_headers is None else domain_headers
        self.timeout_seconds = timeout_seconds

    # Using dict[str, str] instead of tuple[str, str] for query_params because the way Pydantic
    # converts it into a JSON schema is incompatible with OpenAPI.
    def get_request(
        self,
        url_template: str,
        path_params: dict[str, str] = None,
        query_params: dict[str, str] = None,
    ):
        """
        Use this to GET content from a website.

        Args:
            url_template ([str]): The url to make the request against, potentially includes curly
                braces {} to mark a section of a URL path as replaceable using path parameters.
            path_params (dict[str, str]): path parameters for use in the url_template
            query_params (dict[str, str]): query parameters

        """
        if query_params is None:
            query_params = {}
        if not self._valid_url(url_template):
            return INVALID_URL_PROMPT

        path_params = {} if path_params is None else path_params
        url = self._replace_path_params(url_template, path_params)
        res = requests.get(
            url,
            headers=self._get_headers_for_url(url_template),
            params=query_params,
            timeout=self.timeout_seconds,
        )
        return res.json()

    def post_request(
        self,
        url_template: str,
        path_params: dict[str, str] = None,
        query_params: dict[str, str] = None,
        body: Optional[dict] = None,
    ):
        """
        Use this to POST content to a website.

        Args:
            url_template ([str]): The url to make the request against, potentially includes curly
                braces {} to mark a section of a URL path as replaceable using path parameters.
            path_params (dict[str, str]): path parameters for use in the url_template
            query_params (dict[str, str]): query parameters
            body (Optional[dict]): the body of the request, sent as JSON

        """
        if not self._valid_url(url_template):
            return INVALID_URL_PROMPT

        url = self._replace_path_params(url_template, path_params)
        res = requests.post(
            url,
            headers=self._get_headers_for_url(url_template),
            params=query_params,
            json=body,
            timeout=self.timeout_seconds,
        )
        return res.json()

    def patch_request(
        self,
        url_template: str,
        path_params: dict[str, str] = None,
        query_params: dict[str, str] = None,
        body: Optional[dict] = None,
    ):
        """
        Use this to PATCH content to a website.

        Args:
            url_template ([str]): The url to make the request against, potentially includes curly
                braces {} to mark a section of a URL path as replaceable using path parameters.
            path_params (dict[str, str]): path parameters for use in the url_template
            query_params (dict[str, str]): query parameters
            body (Optional[dict]): the body of the request, sent as JSON

        """
        if not self._valid_url(url_template):
            return INVALID_URL_PROMPT

        url = self._replace_path_params(url_template, path_params)
        res = requests.patch(
            url,
            headers=self._get_headers_for_url(url_template),
            params=query_params,
            json=body,
            timeout=self.timeout_seconds,
        )
        return res.json()

    def put_request(
        self,
        url_template: str,
        path_params: dict[str, str] = None,
        query_params: dict[str, str] = None,
        body: Optional[dict] = None,
    ):
        """
        Use this to PUT content to a website.

        Args:
            url_template ([str]): The url to make the request against, potentially includes curly
                braces {} to mark a section of a URL path as replaceable using path parameters.
            path_params (dict[str, str]): path parameters for use in the url_template
            query_params (dict[str, str]): query parameters
            body (Optional[dict]): the body of the request, sent as JSON

        """
        if not self._valid_url(url_template):
            return INVALID_URL_PROMPT

        url = self._replace_path_params(url_template, path_params)
        res = requests.put(
            url,
            headers=self._get_headers_for_url(url_template),
            params=query_params,
            json=body,
            timeout=self.timeout_seconds,
        )
        return res.json()

    def delete_request(
        self,
        url_template: str,
        path_params: dict[str, str] = None,
        query_params: dict[str, str] = None,
        body: Optional[dict] = None,
    ):
        """
        Use this to DELETE content from a website.

        Args:
            url_template ([str]): The url to make the request against, potentially includes
                curly braces {} to mark a section of a URL path as replaceable using path
                parameters.
            path_params (dict[str, str]): path parameters for use in the url_template
            query_params (dict[str, str]): query parameters
            body (Optional[dict]): the body of the request, sent as JSON (not typically used)

        """
        if not self._valid_url(url_template):
            return INVALID_URL_PROMPT

        url = self._replace_path_params(url_template, path_params)
        res = requests.delete(
            url,
            headers=self._get_headers_for_url(url_template),
            params=query_params,
            json=body,
            timeout=self.timeout_seconds,
        )
        return res.json()

    def _valid_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme and parsed.hostname

    def _get_domain(self, url: str) -> str:
        return urlparse(url).hostname

    def _get_headers_for_url(self, url: str) -> dict:
        return self.domain_headers.get(self._get_domain(url), {})

    @staticmethod
    def _replace_path_params(url_template: str, params: dict) -> str:
        if not params:
            return url_template

        parsed = urlparse(url_template)
        path = parsed.path
        for key, value in params.items():
            path = path.replace("{" + key + "}", str(value))
        parsed = parsed._replace(path=path)
        return str(urlunparse(parsed))

```
  
---|---  
###  get_request #
```
get_request(url_template: str, path_params: dict[str, str] = None, query_params: dict[str, str] = None)

```

Use this to GET content from a website.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url_template` |  `[str]` |  The url to make the request against, potentially includes curly braces {} to mark a section of a URL path as replaceable using path parameters. |  _required_  
`path_params` |  `dict[str, str]` |  path parameters for use in the url_template |  `None`  
`query_params` |  `dict[str, str]` |  query parameters |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-requests/llama_index/tools/requests/base.py`

| ```
def get_request(
    self,
    url_template: str,
    path_params: dict[str, str] = None,
    query_params: dict[str, str] = None,
):
    """
    Use this to GET content from a website.

    Args:
        url_template ([str]): The url to make the request against, potentially includes curly
            braces {} to mark a section of a URL path as replaceable using path parameters.
        path_params (dict[str, str]): path parameters for use in the url_template
        query_params (dict[str, str]): query parameters

    """
    if query_params is None:
        query_params = {}
    if not self._valid_url(url_template):
        return INVALID_URL_PROMPT

    path_params = {} if path_params is None else path_params
    url = self._replace_path_params(url_template, path_params)
    res = requests.get(
        url,
        headers=self._get_headers_for_url(url_template),
        params=query_params,
        timeout=self.timeout_seconds,
    )
    return res.json()

```
  
---|---  
###  post_request #
```
post_request(url_template: str, path_params: dict[str, str] = None, query_params: dict[str, str] = None, body: Optional[dict] = None)

```

Use this to POST content to a website.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url_template` |  `[str]` |  The url to make the request against, potentially includes curly braces {} to mark a section of a URL path as replaceable using path parameters. |  _required_  
`path_params` |  `dict[str, str]` |  path parameters for use in the url_template |  `None`  
`query_params` |  `dict[str, str]` |  query parameters |  `None`  
`body` |  `Optional[dict]` |  the body of the request, sent as JSON |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-requests/llama_index/tools/requests/base.py`

| ```
def post_request(
    self,
    url_template: str,
    path_params: dict[str, str] = None,
    query_params: dict[str, str] = None,
    body: Optional[dict] = None,
):
    """
    Use this to POST content to a website.

    Args:
        url_template ([str]): The url to make the request against, potentially includes curly
            braces {} to mark a section of a URL path as replaceable using path parameters.
        path_params (dict[str, str]): path parameters for use in the url_template
        query_params (dict[str, str]): query parameters
        body (Optional[dict]): the body of the request, sent as JSON

    """
    if not self._valid_url(url_template):
        return INVALID_URL_PROMPT

    url = self._replace_path_params(url_template, path_params)
    res = requests.post(
        url,
        headers=self._get_headers_for_url(url_template),
        params=query_params,
        json=body,
        timeout=self.timeout_seconds,
    )
    return res.json()

```
  
---|---  
###  patch_request #
```
patch_request(url_template: str, path_params: dict[str, str] = None, query_params: dict[str, str] = None, body: Optional[dict] = None)

```

Use this to PATCH content to a website.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url_template` |  `[str]` |  The url to make the request against, potentially includes curly braces {} to mark a section of a URL path as replaceable using path parameters. |  _required_  
`path_params` |  `dict[str, str]` |  path parameters for use in the url_template |  `None`  
`query_params` |  `dict[str, str]` |  query parameters |  `None`  
`body` |  `Optional[dict]` |  the body of the request, sent as JSON |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-requests/llama_index/tools/requests/base.py`

| ```
def patch_request(
    self,
    url_template: str,
    path_params: dict[str, str] = None,
    query_params: dict[str, str] = None,
    body: Optional[dict] = None,
):
    """
    Use this to PATCH content to a website.

    Args:
        url_template ([str]): The url to make the request against, potentially includes curly
            braces {} to mark a section of a URL path as replaceable using path parameters.
        path_params (dict[str, str]): path parameters for use in the url_template
        query_params (dict[str, str]): query parameters
        body (Optional[dict]): the body of the request, sent as JSON

    """
    if not self._valid_url(url_template):
        return INVALID_URL_PROMPT

    url = self._replace_path_params(url_template, path_params)
    res = requests.patch(
        url,
        headers=self._get_headers_for_url(url_template),
        params=query_params,
        json=body,
        timeout=self.timeout_seconds,
    )
    return res.json()

```
  
---|---  
###  put_request #
```
put_request(url_template: str, path_params: dict[str, str] = None, query_params: dict[str, str] = None, body: Optional[dict] = None)

```

Use this to PUT content to a website.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url_template` |  `[str]` |  The url to make the request against, potentially includes curly braces {} to mark a section of a URL path as replaceable using path parameters. |  _required_  
`path_params` |  `dict[str, str]` |  path parameters for use in the url_template |  `None`  
`query_params` |  `dict[str, str]` |  query parameters |  `None`  
`body` |  `Optional[dict]` |  the body of the request, sent as JSON |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-requests/llama_index/tools/requests/base.py`

| ```
def put_request(
    self,
    url_template: str,
    path_params: dict[str, str] = None,
    query_params: dict[str, str] = None,
    body: Optional[dict] = None,
):
    """
    Use this to PUT content to a website.

    Args:
        url_template ([str]): The url to make the request against, potentially includes curly
            braces {} to mark a section of a URL path as replaceable using path parameters.
        path_params (dict[str, str]): path parameters for use in the url_template
        query_params (dict[str, str]): query parameters
        body (Optional[dict]): the body of the request, sent as JSON

    """
    if not self._valid_url(url_template):
        return INVALID_URL_PROMPT

    url = self._replace_path_params(url_template, path_params)
    res = requests.put(
        url,
        headers=self._get_headers_for_url(url_template),
        params=query_params,
        json=body,
        timeout=self.timeout_seconds,
    )
    return res.json()

```
  
---|---  
###  delete_request #
```
delete_request(url_template: str, path_params: dict[str, str] = None, query_params: dict[str, str] = None, body: Optional[dict] = None)

```

Use this to DELETE content from a website.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url_template` |  `[str]` |  The url to make the request against, potentially includes curly braces {} to mark a section of a URL path as replaceable using path parameters. |  _required_  
`path_params` |  `dict[str, str]` |  path parameters for use in the url_template |  `None`  
`query_params` |  `dict[str, str]` |  query parameters |  `None`  
`body` |  `Optional[dict]` |  the body of the request, sent as JSON (not typically used) |  `None`  
Source code in `llama-index-integrations/tools/llama-index-tools-requests/llama_index/tools/requests/base.py`

| ```
def delete_request(
    self,
    url_template: str,
    path_params: dict[str, str] = None,
    query_params: dict[str, str] = None,
    body: Optional[dict] = None,
):
    """
    Use this to DELETE content from a website.

    Args:
        url_template ([str]): The url to make the request against, potentially includes
            curly braces {} to mark a section of a URL path as replaceable using path
            parameters.
        path_params (dict[str, str]): path parameters for use in the url_template
        query_params (dict[str, str]): query parameters
        body (Optional[dict]): the body of the request, sent as JSON (not typically used)

    """
    if not self._valid_url(url_template):
        return INVALID_URL_PROMPT

    url = self._replace_path_params(url_template, path_params)
    res = requests.delete(
        url,
        headers=self._get_headers_for_url(url_template),
        params=query_params,
        json=body,
        timeout=self.timeout_seconds,
    )
    return res.json()

```
  
---|---
