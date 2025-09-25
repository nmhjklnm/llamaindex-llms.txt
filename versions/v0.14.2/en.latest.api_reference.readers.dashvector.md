# Dashvector
##  DashVectorReader #
Bases: `BaseReader`
DashVector reader.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`api_key` |  `str` |  DashVector API key. |  _required_  
`endpoint` |  `str` |  DashVector cluster endpoint. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-dashvector/llama_index/readers/dashvector/base.py`

| ```
class DashVectorReader(BaseReader):
    """
    DashVector reader.

    Args:
        api_key (str): DashVector API key.
        endpoint (str): DashVector cluster endpoint.

    """

    def __init__(self, api_key: str, endpoint: str):
        """Initialize with parameters."""
        try:
            import dashvector
        except ImportError:
            raise ImportError(
                "`dashvector` package not found, please run `pip install dashvector`"
            )

        self._client: dashvector.Client = dashvector.Client(
            api_key=api_key, endpoint=endpoint
        )

    def load_data(
        self,
        collection_name: str,
        vector: Optional[List[float]],
        topk: int,
        filter: Optional[str] = None,
        include_vector: bool = True,
        partition: Optional[str] = None,
        output_fields: Optional[List[str]] = None,
        sparse_vector: Optional[Dict[int, float]] = None,
    ) -> List[Document]:
        """
        Load data from DashVector.

        Args:
            collection_name (str): Name of the collection.
            vector (List[float]): Query vector.
            topk (int): Number of results to return.
            filter (Optional[str]): doc fields filter
                conditions that meet the SQL where clause specification.detail in https://help.aliyun.com/document_detail/2513006.html?spm=a2c4g.2510250.0.0.40d25637QMI4eV
            include_vector (bool): Whether to include the embedding in the response.Defaults to True.
            partition (Optional[str]): The partition name
                to query. Defaults to None.
            output_fields (Optional[List[str]]): The fields
                to return. Defaults to None, meaning all fields
            sparse_vector (Optional[Dict[int, float]]): The
                sparse vector to query.Defaults to None.

        Returns:
            List[Document]: A list of documents.

        """
        collection = self._client.get(collection_name)
        if not collection:
            raise ValueError(
                f"Failed to get collection: {collection_name},Error: {collection}"
            )

        ret = collection.query(
            vector=vector,
            topk=topk,
            filter=filter,
            include_vector=include_vector,
            partition=partition,
            output_fields=output_fields,
            sparse_vector=sparse_vector,
        )
        if not ret:
            raise Exception(f"Failed to query document,Error: {ret}")

        doc_metas = ret.output
        documents = []

        for doc_meta in doc_metas:
            node_content = json.loads(doc_meta.fields["_node_content"])
            document = Document(
                id_=doc_meta.id,
                text=node_content["text"],
                metadata=node_content["metadata"],
                embedding=doc_meta.vector,
            )
            documents.append(document)

        return documents

```
  
---|---  
###  load_data #
```
load_data(collection_name: str, vector: Optional[List[float]], topk: int, filter: Optional[str] = None, include_vector: bool = True, partition: Optional[str] = None, output_fields: Optional[List[str]] = None, sparse_vector: Optional[Dict[int, float]] = None) -> List[Document]

```

Load data from DashVector.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection_name` |  `str` |  Name of the collection. |  _required_  
`vector` |  `List[float]` |  Query vector. |  _required_  
`topk` |  `int` |  Number of results to return. |  _required_  
`filter` |  `Optional[str]` |  doc fields filter conditions that meet the SQL where clause specification.detail in https://help.aliyun.com/document_detail/2513006.html?spm=a2c4g.2510250.0.0.40d25637QMI4eV |  `None`  
`include_vector` |  `bool` |  Whether to include the embedding in the response.Defaults to True. |  `True`  
`partition` |  `Optional[str]` |  The partition name to query. Defaults to None. |  `None`  
`output_fields` |  `Optional[List[str]]` |  The fields to return. Defaults to None, meaning all fields |  `None`  
`sparse_vector` |  `Optional[Dict[int, float]]` |  The sparse vector to query.Defaults to None. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-dashvector/llama_index/readers/dashvector/base.py`

| ```
def load_data(
    self,
    collection_name: str,
    vector: Optional[List[float]],
    topk: int,
    filter: Optional[str] = None,
    include_vector: bool = True,
    partition: Optional[str] = None,
    output_fields: Optional[List[str]] = None,
    sparse_vector: Optional[Dict[int, float]] = None,
) -> List[Document]:
    """
    Load data from DashVector.

    Args:
        collection_name (str): Name of the collection.
        vector (List[float]): Query vector.
        topk (int): Number of results to return.
        filter (Optional[str]): doc fields filter
            conditions that meet the SQL where clause specification.detail in https://help.aliyun.com/document_detail/2513006.html?spm=a2c4g.2510250.0.0.40d25637QMI4eV
        include_vector (bool): Whether to include the embedding in the response.Defaults to True.
        partition (Optional[str]): The partition name
            to query. Defaults to None.
        output_fields (Optional[List[str]]): The fields
            to return. Defaults to None, meaning all fields
        sparse_vector (Optional[Dict[int, float]]): The
            sparse vector to query.Defaults to None.

    Returns:
        List[Document]: A list of documents.

    """
    collection = self._client.get(collection_name)
    if not collection:
        raise ValueError(
            f"Failed to get collection: {collection_name},Error: {collection}"
        )

    ret = collection.query(
        vector=vector,
        topk=topk,
        filter=filter,
        include_vector=include_vector,
        partition=partition,
        output_fields=output_fields,
        sparse_vector=sparse_vector,
    )
    if not ret:
        raise Exception(f"Failed to query document,Error: {ret}")

    doc_metas = ret.output
    documents = []

    for doc_meta in doc_metas:
        node_content = json.loads(doc_meta.fields["_node_content"])
        document = Document(
            id_=doc_meta.id,
            text=node_content["text"],
            metadata=node_content["metadata"],
            embedding=doc_meta.vector,
        )
        documents.append(document)

    return documents

```
  
---|---
