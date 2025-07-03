# Agent search
##  AgentSearchReader #
Bases: `BaseReader`
AgentSearch reader.
Source code in `llama-index-integrations/readers/llama-index-readers-agent-search/llama_index/readers/agent_search/base.py`

| ```
class AgentSearchReader(BaseReader):
    """AgentSearch reader."""

    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize with parameters."""
        import_err_msg = (
            "`agent-search` package not found, please run `pip install agent-search`"
        )
        try:
            import agent_search  # noqa: F401
        except ImportError:
            raise ImportError(import_err_msg)

        from agent_search import SciPhi

        self._client = SciPhi(api_base=api_base, api_key=api_key)

    def load_data(
        self,
        query: str,
        search_provider: str = "bing",
        llm_model: str = "SciPhi/Sensei-7B-V1",
    ) -> List[Document]:
        """
        Load data from AgentSearch, hosted by SciPhi.

        Args:
            collection_name (str): Name of the Milvus collection.
            query_vector (List[float]): Query vector.
            limit (int): Number of results to return.

        Returns:
            List[Document]: A list of documents.

        """
        rag_response = self._client.get_search_rag_response(
            query=query, search_provider=search_provider, llm_model=llm_model
        )
        return [Document(text=rag_response.pop("response"), metadata=rag_response)]

```
  
---|---  
###  load_data #
```
load_data(query: str, search_provider: str = 'bing', llm_model: str = 'SciPhi/Sensei-7B-V1') -> List[Document]

```

Load data from AgentSearch, hosted by SciPhi.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection_name` |  `str` |  Name of the Milvus collection. |  _required_  
`query_vector` |  `List[float]` |  Query vector. |  _required_  
`limit` |  `int` |  Number of results to return. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-agent-search/llama_index/readers/agent_search/base.py`

| ```
def load_data(
    self,
    query: str,
    search_provider: str = "bing",
    llm_model: str = "SciPhi/Sensei-7B-V1",
) -> List[Document]:
    """
    Load data from AgentSearch, hosted by SciPhi.

    Args:
        collection_name (str): Name of the Milvus collection.
        query_vector (List[float]): Query vector.
        limit (int): Number of results to return.

    Returns:
        List[Document]: A list of documents.

    """
    rag_response = self._client.get_search_rag_response(
        query=query, search_provider=search_provider, llm_model=llm_model
    )
    return [Document(text=rag_response.pop("response"), metadata=rag_response)]

```
  
---|---
