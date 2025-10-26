# Vector db
##  VectorDBToolSpec #
Bases: `BaseToolSpec`
Vector DB tool spec.
Source code in `llama-index-integrations/tools/llama-index-tools-vector-db/llama_index/tools/vector_db/base.py`

| ```
class VectorDBToolSpec(BaseToolSpec):
    """Vector DB tool spec."""

    spec_functions = ["auto_retrieve_fn"]

    def __init__(
        self,
        index: BaseIndex,  # TODO typing
    ) -> None:
        """Initialize with parameters."""
        self._index = index

    def auto_retrieve_fn(
        self,
        query: str,
        top_k: int,
        filter_key_list: List[str],
        filter_value_list: List[str],
    ) -> str:
        """
        Auto retrieval function.

        Performs auto-retrieval from a vector database, and then applies a set of filters.

        Args:
            query (str): The query to search
            top_k (int): The number of results to retrieve
            filter_key_list (List[str]): The list of filter keys
            filter_value_list (List[str]): The list of filter values

        """
        exact_match_filters = [
            ExactMatchFilter(key=k, value=v)
            for k, v in zip(filter_key_list, filter_value_list)
        ]
        retriever = VectorIndexRetriever(
            self._index,
            filters=MetadataFilters(filters=exact_match_filters),
            top_k=top_k,
        )
        query_engine = RetrieverQueryEngine.from_args(retriever)

        response = query_engine.query(query)
        return str(response)

```
  
---|---  
###  auto_retrieve_fn #
```
auto_retrieve_fn(query: str, top_k: int, filter_key_list: List[str], filter_value_list: List[str]) -> str

```

Auto retrieval function.
Performs auto-retrieval from a vector database, and then applies a set of filters.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The query to search |  _required_  
`top_k` |  `int` |  The number of results to retrieve |  _required_  
`filter_key_list` |  `List[str]` |  The list of filter keys |  _required_  
`filter_value_list` |  `List[str]` |  The list of filter values |  _required_  
Source code in `llama-index-integrations/tools/llama-index-tools-vector-db/llama_index/tools/vector_db/base.py`

| ```
def auto_retrieve_fn(
    self,
    query: str,
    top_k: int,
    filter_key_list: List[str],
    filter_value_list: List[str],
) -> str:
    """
    Auto retrieval function.

    Performs auto-retrieval from a vector database, and then applies a set of filters.

    Args:
        query (str): The query to search
        top_k (int): The number of results to retrieve
        filter_key_list (List[str]): The list of filter keys
        filter_value_list (List[str]): The list of filter values

    """
    exact_match_filters = [
        ExactMatchFilter(key=k, value=v)
        for k, v in zip(filter_key_list, filter_value_list)
    ]
    retriever = VectorIndexRetriever(
        self._index,
        filters=MetadataFilters(filters=exact_match_filters),
        top_k=top_k,
    )
    query_engine = RetrieverQueryEngine.from_args(retriever)

    response = query_engine.query(query)
    return str(response)

```
  
---|---
