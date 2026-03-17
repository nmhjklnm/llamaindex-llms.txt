# Readwise
Init file.
##  ReadwiseReader #
Bases: `BaseReader`
Reader for Readwise highlights.
Source code in `llama-index-integrations/readers/llama-index-readers-readwise/llama_index/readers/readwise/base.py`

| ```
class ReadwiseReader(BaseReader):
    """
    Reader for Readwise highlights.
    """

    def __init__(self, api_key: str):
        self._api_key = api_key

    def load_data(
        self,
        updated_after: Optional[datetime.datetime] = None,
    ) -> List[Document]:
        """
        Load your Readwise.io highlights.

        Args:
            updated_after (datetime.datetime): The datetime to load highlights after. Useful for updating indexes over time.

        """
        readwise_response = _get_readwise_data(
            api_key=self._api_key, updated_after=updated_after
        )
        return [Document(text=json.dumps(d)) for d in readwise_response]

```
  
---|---  
###  load_data #
```
load_data(updated_after: Optional[datetime] = None) -> List[Document]

```

Load your Readwise.io highlights.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`updated_after` |  `datetime` |  The datetime to load highlights after. Useful for updating indexes over time. |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-readwise/llama_index/readers/readwise/base.py`

| ```
def load_data(
    self,
    updated_after: Optional[datetime.datetime] = None,
) -> List[Document]:
    """
    Load your Readwise.io highlights.

    Args:
        updated_after (datetime.datetime): The datetime to load highlights after. Useful for updating indexes over time.

    """
    readwise_response = _get_readwise_data(
        api_key=self._api_key, updated_after=updated_after
    )
    return [Document(text=json.dumps(d)) for d in readwise_response]

```
  
---|---
