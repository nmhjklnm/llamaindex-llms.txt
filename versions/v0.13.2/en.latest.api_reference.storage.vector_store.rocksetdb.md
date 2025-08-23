# Rocksetdb
##  RocksetVectorStore #
Bases: `BasePydanticVectorStore`
Rockset Vector Store.
Examples:
`pip install llama-index-vector-stores-rocksetdb`
```
from llama_index.vector_stores.rocksetdb import RocksetVectorStore

# Set up RocksetVectorStore with necessary configurations
vector_store = RocksetVectorStore(
    collection="my_collection",
    api_key="your_rockset_api_key",
    api_server="https://api.use1a1.rockset.com",
    embedding_col="my_embedding",
    metadata_col="node",
    distance_func=RocksetVectorStore.DistanceFunc.DOT_PRODUCT
)

```

Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-rocksetdb/llama_index/vector_stores/rocksetdb/base.py`

| ```
class RocksetVectorStore(BasePydanticVectorStore):
    """
    Rockset Vector Store.

    Examples:
        `pip install llama-index-vector-stores-rocksetdb`

    ```python
        from llama_index.vector_stores.rocksetdb import RocksetVectorStore

        # Set up RocksetVectorStore with necessary configurations
        vector_store = RocksetVectorStore(
            collection="my_collection",
            api_key="your_rockset_api_key",
            api_server="https://api.use1a1.rockset.com",
            embedding_col="my_embedding",
            metadata_col="node",
            distance_func=RocksetVectorStore.DistanceFunc.DOT_PRODUCT
        )
    ```

    """

    stores_text: bool = True
    is_embedding_query: bool = True
    flat_metadata: bool = False

    class DistanceFunc(Enum):
        COSINE_SIM = "COSINE_SIM"
        EUCLIDEAN_DIST = "EUCLIDEAN_DIST"
        DOT_PRODUCT = "DOT_PRODUCT"

    rockset: ModuleType
    rs: Any
    workspace: str
    collection: str
    text_key: str
    embedding_col: str
    metadata_col: str
    distance_func: DistanceFunc
    distance_order: str

    def __init__(
        self,
        collection: str,
        client: Any | None = None,
        text_key: str = DEFAULT_TEXT_KEY,
        embedding_col: str = DEFAULT_EMBEDDING_KEY,
        metadata_col: str = "metadata",
        workspace: str = "commons",
        api_server: str | None = None,
        api_key: str | None = None,
        distance_func: DistanceFunc = DistanceFunc.COSINE_SIM,
    ) -> None:
        """
        Rockset Vector Store Data container.

        Args:
            collection (str): The name of the collection of vectors
            client (Optional[Any]): Rockset client object
            text_key (str): The key to the text of nodes
                (default: llama_index.core.vector_stores.utils.DEFAULT_TEXT_KEY)
            embedding_col (str): The DB column containing embeddings
                (default: llama_index.core.vector_stores.utils.DEFAULT_EMBEDDING_KEY))
            metadata_col (str): The DB column containing node metadata
                (default: "metadata")
            workspace (str): The workspace containing the collection of vectors
                (default: "commons")
            api_server (Optional[str]): The Rockset API server to use
            api_key (Optional[str]): The Rockset API key to use
            distance_func (RocksetVectorStore.DistanceFunc): The metric to measure
                vector relationship
                (default: RocksetVectorStore.DistanceFunc.COSINE_SIM)

        """
        super().__init__(
            rockset=_get_rockset(),
            rs=_get_client(api_key, api_server, client),
            collection=collection,
            text_key=text_key,
            embedding_col=embedding_col,
            metadata_col=metadata_col,
            workspace=workspace,
            distance_func=distance_func,
            distance_order=(
                "ASC" if distance_func is distance_func.EUCLIDEAN_DIST else "DESC"
            ),
        )

        try:
            self.rs.set_application("llama_index")
        except AttributeError:
            # set_application method does not exist.
            # rockset version < 2.1.0
            pass

    @classmethod
    def class_name(cls) -> str:
        return "RocksetVectorStore"

    @property
    def client(self) -> Any:
        return self.rs

    def add(self, nodes: List[BaseNode], **add_kwargs: Any) -> List[str]:
        """
        Stores vectors in the collection.

        Args:
            nodes (List[BaseNode]): List of nodes with embeddings

        Returns:
            Stored node IDs (List[str])

        """
        return [
            row["_id"]
            for row in self.rs.Documents.add_documents(
                collection=self.collection,
                workspace=self.workspace,
                data=[
                    {
                        self.embedding_col: node.get_embedding(),
                        "_id": node.node_id,
                        self.metadata_col: node_to_metadata_dict(
                            node, text_field=self.text_key
                        ),
                    }
                    for node in nodes
                ],
            ).data
        ]

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Deletes nodes stored in the collection by their ref_doc_id.

        Args:
            ref_doc_id (str): The ref_doc_id of the document
                whose nodes are to be deleted

        """
        self.rs.Documents.delete_documents(
            collection=self.collection,
            workspace=self.workspace,
            data=[
                self.rockset.models.DeleteDocumentsRequestData(id=row["_id"])
                for row in self.rs.sql(
                    f"""
                        SELECT
                            _id
                        FROM
                            "{self.workspace}"."{self.collection}" x
                        WHERE
                            x.{self.metadata_col}.ref_doc_id=:ref_doc_id
                    """,
                    params={"ref_doc_id": ref_doc_id},
                ).results
            ],
        )

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """
        Gets nodes relevant to a query.

        Args:
            query (llama_index.core.vector_stores.types.VectorStoreQuery): The query
            similarity_col (Optional[str]): The column to select the cosine
                similarity as (default: "_similarity")

        Returns:
            query results (llama_index.core.vector_stores.types.VectorStoreQueryResult)

        """
        similarity_col = kwargs.get("similarity_col", "_similarity")
        res = self.rs.sql(
            f"""
                SELECT
                    _id,
                    {self.metadata_col}
                    {
                f''', {self.distance_func.value}(
                            {query.query_embedding},
                            {self.embedding_col}
                        )
                            AS {similarity_col}'''
                if query.query_embedding
                else ""
            }
                FROM
                    "{self.workspace}"."{self.collection}" x
                {
                "WHERE"
                if query.node_ids
                or (query.filters and len(query.filters.legacy_filters()) > 0)
                else ""
            } {
                f'''({
                    " OR ".join([f"_id='{node_id}'" for node_id in query.node_ids])
                })'''
                if query.node_ids
                else ""
            } {
                f''' {"AND" if query.node_ids else ""} ({
                    " AND ".join(
                        [
                            f"x.{self.metadata_col}.{filter.key}=:{filter.key}"
                            for filter in query.filters.legacy_filters()
                        ]
                    )
                })'''
                if query.filters
                else ""
            }
                ORDER BY
                    {similarity_col} {self.distance_order}
                LIMIT
                    {query.similarity_top_k}
            """,
            params=(
                {filter.key: filter.value for filter in query.filters.legacy_filters()}
                if query.filters
                else {}
            ),
        )

        similarities: List[float] | None = [] if query.query_embedding else None
        nodes, ids = [], []
        for row in res.results:
            if similarities is not None:
                similarities.append(row[similarity_col])
            nodes.append(metadata_dict_to_node(row[self.metadata_col]))
            ids.append(row["_id"])

        return VectorStoreQueryResult(similarities=similarities, nodes=nodes, ids=ids)

    @classmethod
    def with_new_collection(
        cls: Type[T], dimensions: int | None = None, **rockset_vector_store_args: Any
    ) -> RocksetVectorStore:
        """
        Creates a new collection and returns its RocksetVectorStore.

        Args:
            dimensions (Optional[int]): The length of the vectors to enforce
                in the collection's ingest transformation. By default, the
                collection will do no vector enforcement.
            collection (str): The name of the collection to be created
            client (Optional[Any]): Rockset client object
            workspace (str): The workspace containing the collection to be
                created (default: "commons")
            text_key (str): The key to the text of nodes
                (default: llama_index.core.vector_stores.utils.DEFAULT_TEXT_KEY)
            embedding_col (str): The DB column containing embeddings
                (default: llama_index.core.vector_stores.utils.DEFAULT_EMBEDDING_KEY))
            metadata_col (str): The DB column containing node metadata
                (default: "metadata")
            api_server (Optional[str]): The Rockset API server to use
            api_key (Optional[str]): The Rockset API key to use
            distance_func (RocksetVectorStore.DistanceFunc): The metric to measure
                vector relationship
                (default: RocksetVectorStore.DistanceFunc.COSINE_SIM)

        """
        client = rockset_vector_store_args["client"] = _get_client(
            api_key=rockset_vector_store_args.get("api_key"),
            api_server=rockset_vector_store_args.get("api_server"),
            client=rockset_vector_store_args.get("client"),
        )
        collection_args = {
            "workspace": rockset_vector_store_args.get("workspace", "commons"),
            "name": rockset_vector_store_args.get("collection"),
        }
        embeddings_col = rockset_vector_store_args.get(
            "embeddings_col", DEFAULT_EMBEDDING_KEY
        )
        if dimensions:
            collection_args["field_mapping_query"] = (
                _get_rockset().model.field_mapping_query.FieldMappingQuery(
                    sql=f"""
                    SELECT
                        *, VECTOR_ENFORCE(
                            {embeddings_col},
                            {dimensions},
                            'float'
                        ) AS {embeddings_col}
                    FROM
                        _input
                """
                )
            )

        client.Collections.create_s3_collection(**collection_args)  # create collection
        while (
            client.Collections.get(
                collection=rockset_vector_store_args.get("collection")
            ).data.status
            != "READY"
        ):  # wait until collection is ready
            sleep(0.1)
            # TODO: add async, non-blocking method collection creation

        return cls(
            **dict(
                filter(  # filter out None args
                    lambda arg: arg[1] is not None, rockset_vector_store_args.items()
                )
            )
        )

```
  
---|---  
###  add #
```
add(nodes: List[BaseNode], **add_kwargs: Any) -> List[str]

```

Stores vectors in the collection.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[BaseNode]` |  List of nodes with embeddings |  _required_  
Returns:
Type | Description  
---|---  
`List[str]` |  Stored node IDs (List[str])  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-rocksetdb/llama_index/vector_stores/rocksetdb/base.py`

| ```
def add(self, nodes: List[BaseNode], **add_kwargs: Any) -> List[str]:
    """
    Stores vectors in the collection.

    Args:
        nodes (List[BaseNode]): List of nodes with embeddings

    Returns:
        Stored node IDs (List[str])

    """
    return [
        row["_id"]
        for row in self.rs.Documents.add_documents(
            collection=self.collection,
            workspace=self.workspace,
            data=[
                {
                    self.embedding_col: node.get_embedding(),
                    "_id": node.node_id,
                    self.metadata_col: node_to_metadata_dict(
                        node, text_field=self.text_key
                    ),
                }
                for node in nodes
            ],
        ).data
    ]

```
  
---|---  
###  delete #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Deletes nodes stored in the collection by their ref_doc_id.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ref_doc_id` |  `str` |  The ref_doc_id of the document whose nodes are to be deleted |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-rocksetdb/llama_index/vector_stores/rocksetdb/base.py`

| ```
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Deletes nodes stored in the collection by their ref_doc_id.

    Args:
        ref_doc_id (str): The ref_doc_id of the document
            whose nodes are to be deleted

    """
    self.rs.Documents.delete_documents(
        collection=self.collection,
        workspace=self.workspace,
        data=[
            self.rockset.models.DeleteDocumentsRequestData(id=row["_id"])
            for row in self.rs.sql(
                f"""
                    SELECT
                        _id
                    FROM
                        "{self.workspace}"."{self.collection}" x
                    WHERE
                        x.{self.metadata_col}.ref_doc_id=:ref_doc_id
                """,
                params={"ref_doc_id": ref_doc_id},
            ).results
        ],
    )

```
  
---|---  
###  query #
```
query(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Gets nodes relevant to a query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `VectorStoreQuery` |  The query |  _required_  
`similarity_col` |  `Optional[str]` |  The column to select the cosine similarity as (default: "_similarity") |  _required_  
Returns:
Type | Description  
---|---  
`VectorStoreQueryResult` |  query results (llama_index.core.vector_stores.types.VectorStoreQueryResult)  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-rocksetdb/llama_index/vector_stores/rocksetdb/base.py`

| ```
def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
    """
    Gets nodes relevant to a query.

    Args:
        query (llama_index.core.vector_stores.types.VectorStoreQuery): The query
        similarity_col (Optional[str]): The column to select the cosine
            similarity as (default: "_similarity")

    Returns:
        query results (llama_index.core.vector_stores.types.VectorStoreQueryResult)

    """
    similarity_col = kwargs.get("similarity_col", "_similarity")
    res = self.rs.sql(
        f"""
            SELECT
                _id,
                {self.metadata_col}
                {
            f''', {self.distance_func.value}(
                        {query.query_embedding},
                        {self.embedding_col}
                    )
                        AS {similarity_col}'''
            if query.query_embedding
            else ""
        }
            FROM
                "{self.workspace}"."{self.collection}" x
            {
            "WHERE"
            if query.node_ids
            or (query.filters and len(query.filters.legacy_filters()) > 0)
            else ""
        } {
            f'''({
                " OR ".join([f"_id='{node_id}'" for node_id in query.node_ids])
            })'''
            if query.node_ids
            else ""
        } {
            f''' {"AND" if query.node_ids else ""} ({
                " AND ".join(
                    [
                        f"x.{self.metadata_col}.{filter.key}=:{filter.key}"
                        for filter in query.filters.legacy_filters()
                    ]
                )
            })'''
            if query.filters
            else ""
        }
            ORDER BY
                {similarity_col} {self.distance_order}
            LIMIT
                {query.similarity_top_k}
        """,
        params=(
            {filter.key: filter.value for filter in query.filters.legacy_filters()}
            if query.filters
            else {}
        ),
    )

    similarities: List[float] | None = [] if query.query_embedding else None
    nodes, ids = [], []
    for row in res.results:
        if similarities is not None:
            similarities.append(row[similarity_col])
        nodes.append(metadata_dict_to_node(row[self.metadata_col]))
        ids.append(row["_id"])

    return VectorStoreQueryResult(similarities=similarities, nodes=nodes, ids=ids)

```
  
---|---  
###  with_new_collection `classmethod` #
```
with_new_collection(dimensions: int | None = None, **rockset_vector_store_args: Any) -> RocksetVectorStore

```

Creates a new collection and returns its RocksetVectorStore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`dimensions` |  `Optional[int]` |  The length of the vectors to enforce in the collection's ingest transformation. By default, the collection will do no vector enforcement. |  `None`  
`collection` |  `str` |  The name of the collection to be created |  _required_  
`client` |  `Optional[Any]` |  Rockset client object |  _required_  
`workspace` |  `str` |  The workspace containing the collection to be created (default: "commons") |  _required_  
`text_key` |  `str` |  The key to the text of nodes (default: llama_index.core.vector_stores.utils.DEFAULT_TEXT_KEY) |  _required_  
`embedding_col` |  `str` |  The DB column containing embeddings (default: llama_index.core.vector_stores.utils.DEFAULT_EMBEDDING_KEY)) |  _required_  
`metadata_col` |  `str` |  The DB column containing node metadata (default: "metadata") |  _required_  
`api_server` |  `Optional[str]` |  The Rockset API server to use |  _required_  
`api_key` |  `Optional[str]` |  The Rockset API key to use |  _required_  
`distance_func` |  `DistanceFunc` |  The metric to measure vector relationship (default: RocksetVectorStore.DistanceFunc.COSINE_SIM) |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-rocksetdb/llama_index/vector_stores/rocksetdb/base.py`

| ```
@classmethod
def with_new_collection(
    cls: Type[T], dimensions: int | None = None, **rockset_vector_store_args: Any
) -> RocksetVectorStore:
    """
    Creates a new collection and returns its RocksetVectorStore.

    Args:
        dimensions (Optional[int]): The length of the vectors to enforce
            in the collection's ingest transformation. By default, the
            collection will do no vector enforcement.
        collection (str): The name of the collection to be created
        client (Optional[Any]): Rockset client object
        workspace (str): The workspace containing the collection to be
            created (default: "commons")
        text_key (str): The key to the text of nodes
            (default: llama_index.core.vector_stores.utils.DEFAULT_TEXT_KEY)
        embedding_col (str): The DB column containing embeddings
            (default: llama_index.core.vector_stores.utils.DEFAULT_EMBEDDING_KEY))
        metadata_col (str): The DB column containing node metadata
            (default: "metadata")
        api_server (Optional[str]): The Rockset API server to use
        api_key (Optional[str]): The Rockset API key to use
        distance_func (RocksetVectorStore.DistanceFunc): The metric to measure
            vector relationship
            (default: RocksetVectorStore.DistanceFunc.COSINE_SIM)

    """
    client = rockset_vector_store_args["client"] = _get_client(
        api_key=rockset_vector_store_args.get("api_key"),
        api_server=rockset_vector_store_args.get("api_server"),
        client=rockset_vector_store_args.get("client"),
    )
    collection_args = {
        "workspace": rockset_vector_store_args.get("workspace", "commons"),
        "name": rockset_vector_store_args.get("collection"),
    }
    embeddings_col = rockset_vector_store_args.get(
        "embeddings_col", DEFAULT_EMBEDDING_KEY
    )
    if dimensions:
        collection_args["field_mapping_query"] = (
            _get_rockset().model.field_mapping_query.FieldMappingQuery(
                sql=f"""
                SELECT
                    *, VECTOR_ENFORCE(
                        {embeddings_col},
                        {dimensions},
                        'float'
                    ) AS {embeddings_col}
                FROM
                    _input
            """
            )
        )

    client.Collections.create_s3_collection(**collection_args)  # create collection
    while (
        client.Collections.get(
            collection=rockset_vector_store_args.get("collection")
        ).data.status
        != "READY"
    ):  # wait until collection is ready
        sleep(0.1)
        # TODO: add async, non-blocking method collection creation

    return cls(
        **dict(
            filter(  # filter out None args
                lambda arg: arg[1] is not None, rockset_vector_store_args.items()
            )
        )
    )

```
  
---|---
