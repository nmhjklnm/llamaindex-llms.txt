# Pathway
##  PathwayReader #
Bases: `BaseReader`
Pathway reader.
Retrieve documents from Pathway data indexing pipeline.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`host` |  `str` |  The URI where Pathway is currently hosted. |  `None`  
`port` |  `str | int` |  The port number on which Pathway is listening. |  `None`  
See Also
llamaindex.retriever.pathway.PathwayRetriever and, llamaindex.retriever.pathway.PathwayVectorServer
Source code in `llama-index-integrations/readers/llama-index-readers-pathway/llama_index/readers/pathway/base.py`

| ```
class PathwayReader(BaseReader):
    """
    Pathway reader.

    Retrieve documents from Pathway data indexing pipeline.

    Args:
        host (str): The URI where Pathway is currently hosted.
        port (str | int): The port number on which Pathway is listening.

    See Also:
        llamaindex.retriever.pathway.PathwayRetriever and,
        llamaindex.retriever.pathway.PathwayVectorServer

    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        url: Optional[str] = None,
    ):
        """Initializing the Pathway reader client."""
        self.client = _VectorStoreClient(host, port, url)

    def load_data(
        self,
        query_text: str,
        k: Optional[int] = 4,
        metadata_filter: Optional[str] = None,
    ) -> List[Document]:
        """
        Load data from Pathway.

        Args:
            query_text (str): The text to get the closest neighbors of.
            k (int): Number of results to return.
            metadata_filter (str): Filter to be applied.

        Returns:
            List[Document]: A list of documents.

        """
        results = self.client(query_text, k, metadata_filter)
        documents = []
        for return_elem in results:
            document = Document(
                text=return_elem["text"],
                extra_info=return_elem["metadata"],
            )

            documents.append(document)

        return documents

```
  
---|---  
###  load_data #
```
load_data(query_text: str, k: Optional[int] = 4, metadata_filter: Optional[str] = None) -> List[Document]

```

Load data from Pathway.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_text` |  `str` |  The text to get the closest neighbors of. |  _required_  
`k` |  `int` |  Number of results to return. |  `4`  
`metadata_filter` |  `str` |  Filter to be applied. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-pathway/llama_index/readers/pathway/base.py`

| ```
def load_data(
    self,
    query_text: str,
    k: Optional[int] = 4,
    metadata_filter: Optional[str] = None,
) -> List[Document]:
    """
    Load data from Pathway.

    Args:
        query_text (str): The text to get the closest neighbors of.
        k (int): Number of results to return.
        metadata_filter (str): Filter to be applied.

    Returns:
        List[Document]: A list of documents.

    """
    results = self.client(query_text, k, metadata_filter)
    documents = []
    for return_elem in results:
        document = Document(
            text=return_elem["text"],
            extra_info=return_elem["metadata"],
        )

        documents.append(document)

    return documents

```
  
---|---
