# Awsdocdb
##  AWSDocDbVectorStore #
Bases: `BasePydanticVectorStore`
AWS DocumentDB Vector Store.
To use, you should have both: - the `pymongo` python package installed - a connection string associated with a DocumentDB Instance
Please refer to the official Vector Search documentation for more details: https://docs.aws.amazon.com/documentdb/latest/developerguide/vector-search.html
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-awsdocdb/llama_index/vector_stores/awsdocdb/base.py`

| ```
class AWSDocDbVectorStore(BasePydanticVectorStore):
    """
    AWS DocumentDB Vector Store.

    To use, you should have both:
    - the ``pymongo`` python package installed
    - a connection string associated with a DocumentDB Instance

    Please refer to the official Vector Search documentation for more details:
    https://docs.aws.amazon.com/documentdb/latest/developerguide/vector-search.html

    """

    stores_text: bool = True
    flat_metadata: bool = True

    _docdb_client: MongoClient = PrivateAttr()
    _similarity_score: AWSDocDbVectorStoreSimilarityType = PrivateAttr()
    _collection: Any = PrivateAttr()
    _embedding_key: str = PrivateAttr()
    _id_key: str = PrivateAttr()
    _text_key: str = PrivateAttr()
    _metadata_key: str = PrivateAttr()
    _insert_kwargs: Dict = PrivateAttr()
    _index_crud: DocDbIndex = PrivateAttr()

    def __init__(
        self,
        docdb_client: Optional[Any] = None,
        db_name: str = "default_db",
        index_name: str = "default_index",
        collection_name: str = "default_collection",
        id_key: str = "id",
        embedding_key: str = "embedding",
        text_key: str = "text",
        metadata_key: str = "metadata",
        insert_kwargs: Optional[Dict] = None,
        similarity_score="cosine",
        **kwargs: Any,
    ) -> None:
        """
        Initialize the vector store.

        Args:
            docdb_client: A DocumentDB client.
            db_name: A DocumentDB database name.
            collection_name: A DocumentDB collection name.
            id_key: The data field to use as the id.
            embedding_key: A DocumentDB field that will contain
            the embedding for each document.
            text_key: A DocumentDB field that will contain the text for each document.
            metadata_key: A DocumentDB field that will contain
            the metadata for each document.
            insert_kwargs: The kwargs used during `insert`.

        """
        super().__init__()

        if docdb_client is not None:
            self._docdb_client = cast(MongoClient, docdb_client)
        else:
            raise ValueError("Must specify connection string to DocumentDB instance ")
        self._similarity_score = similarity_score
        self._collection = self._docdb_client[db_name][collection_name]
        self._embedding_key = embedding_key
        self._id_key = id_key
        self._text_key = text_key
        self._metadata_key = metadata_key
        self._insert_kwargs = insert_kwargs or {}
        self._index_crud = DocDbIndex(index_name, self._embedding_key, self._collection)

    @classmethod
    def class_name(cls) -> str:
        return "AWSDocDbVectorStore"

    def add(
        self,
        nodes: List[BaseNode],
        **add_kwargs: Any,
    ) -> List[str]:
        """
        Add nodes to index.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings

        Returns:
            A List of ids for successfully added nodes.

        """
        ids = []
        data_to_insert = []
        for node in nodes:
            metadata = node_to_metadata_dict(
                node, remove_text=True, flat_metadata=self.flat_metadata
            )

            entry = {
                self._id_key: node.node_id,
                self._embedding_key: node.get_embedding(),
                self._text_key: node.get_content(metadata_mode=MetadataMode.NONE) or "",
                self._metadata_key: metadata,
            }
            data_to_insert.append(entry)
            ids.append(node.node_id)
        logger.debug("Inserting data into DocumentDB: %s", data_to_insert)
        insert_result = self._collection.insert_many(
            data_to_insert, **self._insert_kwargs
        )
        logger.debug("Result of insert: %s", insert_result)
        return ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using by id.

        Args:
            ref_doc_id (str): The doc_id of the document to delete.

        """
        if ref_doc_id is None:
            raise ValueError("No document id provided to delete.")
        self._collection.delete_one({self._metadata_key + ".ref_doc_id": ref_doc_id})

    @property
    def client(self) -> Any:
        """Return DocDB client."""
        return self._docdb_client

    def _query(
        self, query: VectorStoreQuery, projection: Optional[Dict[str, int]] = None
    ) -> VectorStoreQueryResult:
        params: Dict[str, Any] = {
            "vector": query.query_embedding,
            "path": self._embedding_key,
            "similarity": self._similarity_score,
            "k": query.similarity_top_k,
        }
        if query.filters:
            params["filter"] = _to_mongodb_filter(query.filters)

        if projection is None:
            pipeline = [{"$search": {"vectorSearch": params}}]
        else:
            pipeline = [{"$search": {"vectorSearch": params}}, {"$project": projection}]
        logger.debug("Running query pipeline: %s", pipeline)
        cursor = self._collection.aggregate(pipeline)  # type: ignore
        top_k_nodes = []
        top_k_ids = []
        top_k_scores = []
        for res in cursor:
            text = res.pop(self._text_key)
            vector = res.pop(self._embedding_key)
            id = res.pop(self._id_key)
            metadata_dict = res.pop(self._metadata_key)
            score = similarity(query.query_embedding, vector, self._similarity_score)

            try:
                node = metadata_dict_to_node(metadata_dict)
                node.set_content(text)
            except Exception:
                # NOTE: deprecated legacy logic for backward compatibility
                metadata, node_info, relationships = legacy_metadata_dict_to_node(
                    metadata_dict
                )

                node = TextNode(
                    text=text,
                    id_=id,
                    metadata=metadata,
                    start_char_idx=node_info.get("start", None),
                    end_char_idx=node_info.get("end", None),
                    relationships=relationships,
                )

            top_k_ids.append(id)
            top_k_nodes.append(node)
            top_k_scores.append(score)
        result = VectorStoreQueryResult(
            nodes=top_k_nodes, similarities=top_k_scores, ids=top_k_ids
        )
        logger.debug("Result of query: %s", result)
        return result

    def query(
        self,
        query: VectorStoreQuery,
        projection: Optional[Dict[str, int]] = None,
        **kwargs: Any,
    ) -> VectorStoreQueryResult:
        """
        Query index for top k most similar nodes.

        Args:
            query: a VectorStoreQuery object.
            projection: a dictionary specifying which fields to return after the search

        Returns:
            A VectorStoreQueryResult containing the results of the query.

        """
        return self._query(query, projection=projection)

    def create_index(self, dimensions, similarity_score=None):
        score = self._similarity_score
        if similarity_score is not None:
            score = similarity
        return self._index_crud.create_index(dimensions, score)

    def delete_index(self):
        return self._index_crud.delete_index()

    def __del__(self) -> None:
        self._docdb_client.close()

```
  
---|---  
###  client `property` #
```
client: Any

```

Return DocDB client.
###  add #
```
add(nodes: List[BaseNode], **add_kwargs: Any) -> List[str]

```

Add nodes to index.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[BaseNode]` |  List[BaseNode]: list of nodes with embeddings |  _required_  
Returns:
Type | Description  
---|---  
`List[str]` |  A List of ids for successfully added nodes.  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-awsdocdb/llama_index/vector_stores/awsdocdb/base.py`

| ```
def add(
    self,
    nodes: List[BaseNode],
    **add_kwargs: Any,
) -> List[str]:
    """
    Add nodes to index.

    Args:
        nodes: List[BaseNode]: list of nodes with embeddings

    Returns:
        A List of ids for successfully added nodes.

    """
    ids = []
    data_to_insert = []
    for node in nodes:
        metadata = node_to_metadata_dict(
            node, remove_text=True, flat_metadata=self.flat_metadata
        )

        entry = {
            self._id_key: node.node_id,
            self._embedding_key: node.get_embedding(),
            self._text_key: node.get_content(metadata_mode=MetadataMode.NONE) or "",
            self._metadata_key: metadata,
        }
        data_to_insert.append(entry)
        ids.append(node.node_id)
    logger.debug("Inserting data into DocumentDB: %s", data_to_insert)
    insert_result = self._collection.insert_many(
        data_to_insert, **self._insert_kwargs
    )
    logger.debug("Result of insert: %s", insert_result)
    return ids

```
  
---|---  
###  delete #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using by id.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ref_doc_id` |  `str` |  The doc_id of the document to delete. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-awsdocdb/llama_index/vector_stores/awsdocdb/base.py`

| ```
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete nodes using by id.

    Args:
        ref_doc_id (str): The doc_id of the document to delete.

    """
    if ref_doc_id is None:
        raise ValueError("No document id provided to delete.")
    self._collection.delete_one({self._metadata_key + ".ref_doc_id": ref_doc_id})

```
  
---|---  
###  query #
```
query(query: VectorStoreQuery, projection: Optional[Dict[str, int]] = None, **kwargs: Any) -> VectorStoreQueryResult

```

Query index for top k most similar nodes.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `VectorStoreQuery` |  a VectorStoreQuery object. |  _required_  
`projection` |  `Optional[Dict[str, int]]` |  a dictionary specifying which fields to return after the search |  `None`  
Returns:
Type | Description  
---|---  
`VectorStoreQueryResult` |  A VectorStoreQueryResult containing the results of the query.  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-awsdocdb/llama_index/vector_stores/awsdocdb/base.py`

| ```
def query(
    self,
    query: VectorStoreQuery,
    projection: Optional[Dict[str, int]] = None,
    **kwargs: Any,
) -> VectorStoreQueryResult:
    """
    Query index for top k most similar nodes.

    Args:
        query: a VectorStoreQuery object.
        projection: a dictionary specifying which fields to return after the search

    Returns:
        A VectorStoreQueryResult containing the results of the query.

    """
    return self._query(query, projection=projection)

```
  
---|---
