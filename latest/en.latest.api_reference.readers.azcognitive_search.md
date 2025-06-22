# Azcognitive search
##  AzCognitiveSearchReader #
Bases: `BaseReader`
General reader for any Azure Cognitive Search index reader.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`service_name` |  `str` |  the name of azure cognitive search service. |  _required_  
`search_key` |  `str` |  provide azure search access key directly. |  _required_  
`index` |  `str` |  index name |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-azcognitive-search/llama_index/readers/azcognitive_search/base.py`

| ```
class AzCognitiveSearchReader(BaseReader):
    """
    General reader for any Azure Cognitive Search index reader.

    Args:
        service_name (str): the name of azure cognitive search service.
        search_key (str): provide azure search access key directly.
        index (str): index name

    """

    def __init__(self, service_name: str, searck_key: str, index: str) -> None:
        """Initialize Azure cognitive search service using the search key."""
        import logging

        logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
        logger.setLevel(logging.WARNING)

        azure_credential = AzureKeyCredential(searck_key)

        self.search_client = SearchClient(
            endpoint=f"https://{service_name}.search.windows.net",
            index_name=index,
            credential=azure_credential,
        )

    def load_data(
        self, query: str, content_field: str, filter: Optional[str] = None
    ) -> List[Document]:
        """
        Read data from azure cognitive search index.

        Args:
            query (str): search term in Azure Search index
            content_field (str): field name of the document content.
            filter (str): Filter expression. For example : 'sourcepage eq
                'employee_handbook-3.pdf' and sourcefile eq 'employee_handbook.pdf''

        Returns:
            List[Document]: A list of documents.

        """
        search_result = self.search_client.search(query, filter=filter)

        return [
            Document(
                text=result[content_field],
                extra_info={"id": result["id"], "score": result["@search.score"]},
            )
            for result in search_result
        ]

```
  
---|---  
###  load_data #
```
load_data(query: str, content_field: str, filter: Optional[str] = None) -> List[Document]

```

Read data from azure cognitive search index.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  search term in Azure Search index |  _required_  
`content_field` |  `str` |  field name of the document content. |  _required_  
`filter` |  `str` |  Filter expression. For example : 'sourcepage eq 'employee_handbook-3.pdf' and sourcefile eq 'employee_handbook.pdf'' |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-azcognitive-search/llama_index/readers/azcognitive_search/base.py`

| ```
def load_data(
    self, query: str, content_field: str, filter: Optional[str] = None
) -> List[Document]:
    """
    Read data from azure cognitive search index.

    Args:
        query (str): search term in Azure Search index
        content_field (str): field name of the document content.
        filter (str): Filter expression. For example : 'sourcepage eq
            'employee_handbook-3.pdf' and sourcefile eq 'employee_handbook.pdf''

    Returns:
        List[Document]: A list of documents.

    """
    search_result = self.search_client.search(query, filter=filter)

    return [
        Document(
            text=result[content_field],
            extra_info={"id": result["id"], "score": result["@search.score"]},
        )
        for result in search_result
    ]

```
  
---|---
