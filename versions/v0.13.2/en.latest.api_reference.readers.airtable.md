# Airtable
##  AirtableReader #
Bases: `BaseReader`
Airtable reader. Reads data from a table in a base.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`api_key` |  `str` |  Airtable API key. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-airtable/llama_index/readers/airtable/base.py`

| ```
class AirtableReader(BaseReader):
    """
    Airtable reader. Reads data from a table in a base.

    Args:
        api_key (str): Airtable API key.

    """

    def __init__(self, api_key: str) -> None:
        """Initialize Airtable reader."""
        self.api_key = api_key

    def load_data(self, base_id: str, table_id: str) -> List[Document]:
        """
        Load data from a table in a base.

        Args:
            table_id (str): Table ID.
            base_id (str): Base ID.


        Returns:
            List[Document]: List of documents.

        """
        table = Table(self.api_key, base_id, table_id)
        all_records = table.all()
        return [Document(text=f"{all_records}", extra_info={})]

```
  
---|---  
###  load_data #
```
load_data(base_id: str, table_id: str) -> List[Document]

```

Load data from a table in a base.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`table_id` |  `str` |  Table ID. |  _required_  
`base_id` |  `str` |  Base ID. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-airtable/llama_index/readers/airtable/base.py`

| ```
def load_data(self, base_id: str, table_id: str) -> List[Document]:
    """
    Load data from a table in a base.

    Args:
        table_id (str): Table ID.
        base_id (str): Base ID.


    Returns:
        List[Document]: List of documents.

    """
    table = Table(self.api_key, base_id, table_id)
    all_records = table.all()
    return [Document(text=f"{all_records}", extra_info={})]

```
  
---|---
