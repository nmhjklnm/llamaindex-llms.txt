# Make com
##  MakeWrapper #
Bases: `BaseReader`
Make reader.
Source code in `llama-index-integrations/readers/llama-index-readers-make-com/llama_index/readers/make_com/base.py`

| ```
class MakeWrapper(BaseReader):
    """Make reader."""

    def load_data(self, *args: Any, **load_kwargs: Any) -> List[Document]:
        """
        Load data from the input directory.

        NOTE: This is not implemented.

        """
        raise NotImplementedError("Cannot load documents from Make.com API.")

    def pass_response_to_webhook(
        self, webhook_url: str, response: Response, query: Optional[str] = None
    ) -> None:
        """
        Pass response object to webhook.

        Args:
            webhook_url (str): Webhook URL.
            response (Response): Response object.
            query (Optional[str]): Query. Defaults to None.

        """
        response_text = response.response
        source_nodes = [n.dict() for n in response.source_nodes]
        json_dict = {
            "response": response_text,
            "source_nodes": source_nodes,
            "query": query,
        }
        r = requests.post(webhook_url, json=json_dict)
        r.raise_for_status()

```
  
---|---  
###  load_data #
```
load_data(*args: Any, **load_kwargs: Any) -> List[Document]

```

Load data from the input directory.
NOTE: This is not implemented.
Source code in `llama-index-integrations/readers/llama-index-readers-make-com/llama_index/readers/make_com/base.py`

| ```
def load_data(self, *args: Any, **load_kwargs: Any) -> List[Document]:
    """
    Load data from the input directory.

    NOTE: This is not implemented.

    """
    raise NotImplementedError("Cannot load documents from Make.com API.")

```
  
---|---  
###  pass_response_to_webhook #
```
pass_response_to_webhook(webhook_url: str, response: Response, query: Optional[str] = None) -> None

```

Pass response object to webhook.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`webhook_url` |  `str` |  Webhook URL. |  _required_  
`response` |  `Response` |  Response object. |  _required_  
`query` |  `Optional[str]` |  Query. Defaults to None. |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-make-com/llama_index/readers/make_com/base.py`

| ```
def pass_response_to_webhook(
    self, webhook_url: str, response: Response, query: Optional[str] = None
) -> None:
    """
    Pass response object to webhook.

    Args:
        webhook_url (str): Webhook URL.
        response (Response): Response object.
        query (Optional[str]): Query. Defaults to None.

    """
    response_text = response.response
    source_nodes = [n.dict() for n in response.source_nodes]
    json_dict = {
        "response": response_text,
        "source_nodes": source_nodes,
        "query": query,
    }
    r = requests.post(webhook_url, json=json_dict)
    r.raise_for_status()

```
  
---|---
