# Deeplake
##  DeepLakeReader #
Bases: `BaseReader`
DeepLake reader.
Retrieve documents from existing DeepLake datasets.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`dataset_name` |  |  Name of the deeplake dataset. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-deeplake/llama_index/readers/deeplake/base.py`

| ```
class DeepLakeReader(BaseReader):
    """
    DeepLake reader.

    Retrieve documents from existing DeepLake datasets.

    Args:
        dataset_name: Name of the deeplake dataset.

    """

    def __init__(
        self,
        token: Optional[str] = None,
    ):
        """Initializing the deepLake reader."""
        import_err_msg = (
            "`deeplake` package not found, please run `pip install deeplake`"
        )
        try:
            import deeplake  # noqa
        except ImportError:
            raise ImportError(import_err_msg)
        self.token = token

    def load_data(
        self,
        query_vector: List[float],
        dataset_path: str,
        limit: int = 4,
        distance_metric: str = "l2",
    ) -> List[Document]:
        """
        Load data from DeepLake.

        Args:
            dataset_name (str): Name of the DeepLake dataset.
            query_vector (List[float]): Query vector.
            limit (int): Number of results to return.

        Returns:
            List[Document]: A list of documents.

        """
        import deeplake
        from deeplake.util.exceptions import TensorDoesNotExistError

        dataset = deeplake.load(dataset_path, token=self.token)

        try:
            embeddings = dataset.embedding.numpy(fetch_chunks=True)
        except Exception:
            raise TensorDoesNotExistError("embedding")

        indices = vector_search(
            query_vector, embeddings, distance_metric=distance_metric, limit=limit
        )

        documents = []
        for idx in indices:
            document = Document(
                text=str(dataset[idx].text.numpy().tolist()[0]),
                id_=dataset[idx].ids.numpy().tolist()[0],
            )

            documents.append(document)

        return documents

```
  
---|---  
###  load_data #
```
load_data(query_vector: List[float], dataset_path: str, limit: int = 4, distance_metric: str = 'l2') -> List[Document]

```

Load data from DeepLake.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`dataset_name` |  `str` |  Name of the DeepLake dataset. |  _required_  
`query_vector` |  `List[float]` |  Query vector. |  _required_  
`limit` |  `int` |  Number of results to return. |  `4`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-deeplake/llama_index/readers/deeplake/base.py`

| ```
def load_data(
    self,
    query_vector: List[float],
    dataset_path: str,
    limit: int = 4,
    distance_metric: str = "l2",
) -> List[Document]:
    """
    Load data from DeepLake.

    Args:
        dataset_name (str): Name of the DeepLake dataset.
        query_vector (List[float]): Query vector.
        limit (int): Number of results to return.

    Returns:
        List[Document]: A list of documents.

    """
    import deeplake
    from deeplake.util.exceptions import TensorDoesNotExistError

    dataset = deeplake.load(dataset_path, token=self.token)

    try:
        embeddings = dataset.embedding.numpy(fetch_chunks=True)
    except Exception:
        raise TensorDoesNotExistError("embedding")

    indices = vector_search(
        query_vector, embeddings, distance_metric=distance_metric, limit=limit
    )

    documents = []
    for idx in indices:
        document = Document(
            text=str(dataset[idx].text.numpy().tolist()[0]),
            id_=dataset[idx].ids.numpy().tolist()[0],
        )

        documents.append(document)

    return documents

```
  
---|---
