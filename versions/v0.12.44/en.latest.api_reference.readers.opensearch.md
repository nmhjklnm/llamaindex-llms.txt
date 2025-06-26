# Opensearch
##  OpensearchReader #
Bases: `BaseReader`
Read documents from an Opensearch index.
These documents can then be used in a downstream Llama Index data structure.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`endpoint` |  `str` |  URL (http/https) of cluster without port |  _required_  
`index` |  `str` |  Name of the index (required) |  _required_  
`basic_auth` |  `set` |  basic authentication username password |  `None`  
Source code in `llama-index-integrations/readers/llama-index-readers-opensearch/llama_index/readers/opensearch/base.py`

| ```
class OpensearchReader(BaseReader):
    """
    Read documents from an Opensearch index.

    These documents can then be used in a downstream Llama Index data structure.

    Args:
        endpoint (str): URL (http/https) of cluster without port
        index (str): Name of the index (required)
        basic_auth (set): basic authentication username password

    """

    def __init__(
        self, host: str, port: int, index: str, basic_auth: Optional[set] = None
    ):
        """Initialize with parameters."""
        from opensearchpy import OpenSearch

        self._opster_client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            http_compress=True,  # enables gzip compression for request bodies
            http_auth=basic_auth,
            use_ssl=True,
            verify_certs=False,
            ssl_assert_hostname=False,
            ssl_show_warn=False,
        )
        self._index = index

    def load_data(
        self,
        field: str,
        query: Optional[dict] = None,
        embedding_field: Optional[str] = None,
    ) -> List[Document]:
        """
        Read data from the Opensearch index.

        Args:
            field (str): Field in the document to retrieve text from
            query (Optional[dict]): Opensearch JSON query DSL object.
                For example:
                { "query" : {"match": {"message": {"query": "this is a test"}}}}
            embedding_field (Optional[str]): If there are embeddings stored in
                this index, this field can be used
                to set the embedding field on the returned Document list.


        Returns:
            List[Document]: A list of documents.

        """
        res = self._opster_client.search(body=query, index=self._index)
        documents = []
        for hit in res["hits"]["hits"]:
            value = hit["_source"][field]
            _ = hit["_source"].pop(field)
            embedding = hit["_source"].get(embedding_field or "", None)
            documents.append(
                Document(text=value, extra_info=hit["_source"], embedding=embedding)
            )
        return documents

```
  
---|---  
###  load_data #
```
load_data(field: str, query: Optional[dict] = None, embedding_field: Optional[str] = None) -> List[Document]

```

Read data from the Opensearch index.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`field` |  `str` |  Field in the document to retrieve text from |  _required_  
`query` |  `Optional[dict]` |  Opensearch JSON query DSL object. For example: { "query" : {"match": {"message": {"query": "this is a test"}}}} |  `None`  
`embedding_field` |  `Optional[str]` |  If there are embeddings stored in this index, this field can be used to set the embedding field on the returned Document list. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-opensearch/llama_index/readers/opensearch/base.py`

| ```
def load_data(
    self,
    field: str,
    query: Optional[dict] = None,
    embedding_field: Optional[str] = None,
) -> List[Document]:
    """
    Read data from the Opensearch index.

    Args:
        field (str): Field in the document to retrieve text from
        query (Optional[dict]): Opensearch JSON query DSL object.
            For example:
            { "query" : {"match": {"message": {"query": "this is a test"}}}}
        embedding_field (Optional[str]): If there are embeddings stored in
            this index, this field can be used
            to set the embedding field on the returned Document list.


    Returns:
        List[Document]: A list of documents.

    """
    res = self._opster_client.search(body=query, index=self._index)
    documents = []
    for hit in res["hits"]["hits"]:
        value = hit["_source"][field]
        _ = hit["_source"].pop(field)
        embedding = hit["_source"].get(embedding_field or "", None)
        documents.append(
            Document(text=value, extra_info=hit["_source"], embedding=embedding)
        )
    return documents

```
  
---|---
