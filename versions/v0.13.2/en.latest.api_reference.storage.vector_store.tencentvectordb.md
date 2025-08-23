# Tencentvectordb
##  TencentVectorDB #
Bases: `BasePydanticVectorStore`
Tencent Vector Store.
In this vector store, embeddings and docs are stored within a Collection. If the Collection does not exist, it will be automatically created.
In order to use this you need to have a database instance. See the following documentation for details: https://cloud.tencent.com/document/product/1709/94951
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`url` |  `Optional[str]` |  url of Tencent vector database |  _required_  
`username` |  `Optional[str]` |  The username for Tencent vector database. Default value is "root" |  `DEFAULT_USERNAME`  
`key` |  `Optional[str]` |  The Api-Key for Tencent vector database |  _required_  
`collection_params` |  `Optional[CollectionParams]` |  The collection parameters for vector database |  `CollectionParams(dimension=1536)`  
Examples:
`pip install llama-index-vector-stores-tencentvectordb`
```
from llama_index.vector_stores.tencentvectordb import TencentVectorDB, CollectionParams

# Setup
url = "http://10.0.X.X"
key = "eC4bLRy2va******************************"
collection_params = CollectionParams(dimension=1536, drop_exists=True)

# Create an instance of TencentVectorDB
vector_store = TencentVectorDB(url=url, key=key, collection_params=collection_params)

```

Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-tencentvectordb/llama_index/vector_stores/tencentvectordb/base.py`

| ```
class TencentVectorDB(BasePydanticVectorStore):
    """
    Tencent Vector Store.

    In this vector store, embeddings and docs are stored within a Collection.
    If the Collection does not exist, it will be automatically created.

    In order to use this you need to have a database instance.
    See the following documentation for details:
    https://cloud.tencent.com/document/product/1709/94951

    Args:
        url (Optional[str]): url of Tencent vector database
        username (Optional[str]): The username for Tencent vector database. Default value is "root"
        key (Optional[str]): The Api-Key for Tencent vector database
        collection_params (Optional[CollectionParams]): The collection parameters for vector database

    Examples:
        `pip install llama-index-vector-stores-tencentvectordb`

    ```python
        from llama_index.vector_stores.tencentvectordb import TencentVectorDB, CollectionParams

        # Setup
        url = "http://10.0.X.X"
        key = "eC4bLRy2va******************************"
        collection_params = CollectionParams(dimension=1536, drop_exists=True)

        # Create an instance of TencentVectorDB
        vector_store = TencentVectorDB(url=url, key=key, collection_params=collection_params)
    ```

    """

    stores_text: bool = True
    filter_fields: List[FilterField] = []

    batch_size: int
    _tencent_client: Any = PrivateAttr()
    _database: Any = PrivateAttr()
    _collection: Any = PrivateAttr()
    _filter_fields: List[FilterField] = PrivateAttr()

    def __init__(
        self,
        url: str,
        key: str,
        username: str = DEFAULT_USERNAME,
        database_name: str = DEFAULT_DATABASE_NAME,
        read_consistency: str = READ_EVENTUAL_CONSISTENCY,
        collection_params: CollectionParams = CollectionParams(dimension=1536),
        batch_size: int = 512,
        **kwargs: Any,
    ):
        """Init params."""
        super().__init__(batch_size=batch_size)
        self._init_client(url, username, key, read_consistency)
        self._create_database_if_not_exists(database_name)
        self._create_collection(database_name, collection_params)
        self._init_filter_fields()

    def _init_filter_fields(self) -> None:
        fields = vars(self._collection).get("indexes", [])
        for field in fields:
            if field["fieldName"] not in [FIELD_ID, DEFAULT_DOC_ID_KEY, FIELD_VECTOR]:
                self._filter_fields.append(
                    FilterField(name=field["fieldName"], data_type=field["fieldType"])
                )

    @classmethod
    def class_name(cls) -> str:
        return "TencentVectorDB"

    @classmethod
    def from_params(
        cls,
        url: str,
        key: str,
        username: str = DEFAULT_USERNAME,
        database_name: str = DEFAULT_DATABASE_NAME,
        read_consistency: str = READ_EVENTUAL_CONSISTENCY,
        collection_params: CollectionParams = CollectionParams(dimension=1536),
        batch_size: int = 512,
        **kwargs: Any,
    ) -> "TencentVectorDB":
        _try_import()
        return cls(
            url=url,
            username=username,
            key=key,
            database_name=database_name,
            read_consistency=read_consistency,
            collection_params=collection_params,
            batch_size=batch_size,
            **kwargs,
        )

    def _init_client(
        self, url: str, username: str, key: str, read_consistency: str
    ) -> None:
        import tcvectordb
        from tcvectordb.model.enum import ReadConsistency

        if read_consistency is None:
            raise ValueError(VALUE_RANGE_ERROR.format(read_consistency))

        try:
            v_read_consistency = ReadConsistency(read_consistency)
        except ValueError:
            raise ValueError(
                VALUE_RANGE_ERROR.format(READ_CONSISTENCY, READ_CONSISTENCY_VALUES)
            )

        self._tencent_client = tcvectordb.VectorDBClient(
            url=url,
            username=username,
            key=key,
            read_consistency=v_read_consistency,
            timeout=DEFAULT_TIMEOUT,
        )

    def _create_database_if_not_exists(self, database_name: str) -> None:
        db_list = self._tencent_client.list_databases()

        if database_name in [db.database_name for db in db_list]:
            self._database = self._tencent_client.database(database_name)
        else:
            self._database = self._tencent_client.create_database(database_name)

    def _create_collection(
        self, database_name: str, collection_params: CollectionParams
    ) -> None:
        import tcvectordb

        collection_name: str = self._compute_collection_name(
            database_name, collection_params
        )
        collection_description = collection_params._collection_description

        if collection_params is None:
            raise ValueError(VALUE_NONE_ERROR.format("collection_params"))

        try:
            self._collection = self._database.describe_collection(collection_name)
            if collection_params.drop_exists:
                self._database.drop_collection(collection_name)
                self._create_collection_in_db(
                    collection_name, collection_description, collection_params
                )
        except tcvectordb.exceptions.VectorDBException:
            self._create_collection_in_db(
                collection_name, collection_description, collection_params
            )

    @staticmethod
    def _compute_collection_name(
        database_name: str, collection_params: CollectionParams
    ) -> str:
        if database_name == DEFAULT_DATABASE_NAME:
            return collection_params._collection_name
        if collection_params._collection_name != DEFAULT_COLLECTION_NAME:
            return collection_params._collection_name
        else:
            return database_name + "_" + DEFAULT_COLLECTION_NAME

    def _create_collection_in_db(
        self,
        collection_name: str,
        collection_description: str,
        collection_params: CollectionParams,
    ) -> None:
        from tcvectordb.model.enum import FieldType, IndexType
        from tcvectordb.model.index import FilterIndex, Index, VectorIndex

        index_type = self._get_index_type(collection_params.index_type)
        metric_type = self._get_metric_type(collection_params.metric_type)
        index_param = self._get_index_params(index_type, collection_params)
        index = Index(
            FilterIndex(
                name=FIELD_ID,
                field_type=FieldType.String,
                index_type=IndexType.PRIMARY_KEY,
            ),
            FilterIndex(
                name=DEFAULT_DOC_ID_KEY,
                field_type=FieldType.String,
                index_type=IndexType.FILTER,
            ),
            VectorIndex(
                name=FIELD_VECTOR,
                dimension=collection_params.dimension,
                index_type=index_type,
                metric_type=metric_type,
                params=index_param,
            ),
        )
        for field in collection_params.filter_fields:
            index.add(field.to_vdb_filter())

        self._collection = self._database.create_collection(
            name=collection_name,
            shard=collection_params.shard,
            replicas=collection_params.replicas,
            description=collection_description,
            index=index,
        )

    @staticmethod
    def _get_index_params(index_type: Any, collection_params: CollectionParams) -> None:
        from tcvectordb.model.enum import IndexType
        from tcvectordb.model.index import (
            HNSWParams,
            IVFFLATParams,
            IVFPQParams,
            IVFSQ4Params,
            IVFSQ8Params,
            IVFSQ16Params,
        )

        vector_params = (
            {}
            if collection_params.vector_params is None
            else collection_params.vector_params
        )

        if index_type == IndexType.HNSW:
            return HNSWParams(
                m=vector_params.get("M", DEFAULT_HNSW_M),
                efconstruction=vector_params.get("efConstruction", DEFAULT_HNSW_EF),
            )
        elif index_type == IndexType.IVF_FLAT:
            return IVFFLATParams(nlist=vector_params.get("nlist", DEFAULT_IVF_NLIST))
        elif index_type == IndexType.IVF_PQ:
            return IVFPQParams(
                m=vector_params.get("M", DEFAULT_IVF_PQ_M),
                nlist=vector_params.get("nlist", DEFAULT_IVF_NLIST),
            )
        elif index_type == IndexType.IVF_SQ4:
            return IVFSQ4Params(nlist=vector_params.get("nlist", DEFAULT_IVF_NLIST))
        elif index_type == IndexType.IVF_SQ8:
            return IVFSQ8Params(nlist=vector_params.get("nlist", DEFAULT_IVF_NLIST))
        elif index_type == IndexType.IVF_SQ16:
            return IVFSQ16Params(nlist=vector_params.get("nlist", DEFAULT_IVF_NLIST))
        return None

    @staticmethod
    def _get_index_type(index_type_value: str) -> Any:
        from tcvectordb.model.enum import IndexType

        index_type_value = index_type_value or IndexType.HNSW
        try:
            return IndexType(index_type_value)
        except ValueError:
            support_index_types = [d.value for d in IndexType.__members__.values()]
            raise ValueError(
                NOT_SUPPORT_INDEX_TYPE_ERROR.format(
                    index_type_value, support_index_types
                )
            )

    @staticmethod
    def _get_metric_type(metric_type_value: str) -> Any:
        from tcvectordb.model.enum import MetricType

        metric_type_value = metric_type_value or MetricType.COSINE
        try:
            return MetricType(metric_type_value.upper())
        except ValueError:
            support_metric_types = [d.value for d in MetricType.__members__.values()]
            raise ValueError(
                NOT_SUPPORT_METRIC_TYPE_ERROR.format(
                    metric_type_value, support_metric_types
                )
            )

    @property
    def client(self) -> Any:
        """Get client."""
        return self._tencent_client

    def add(
        self,
        nodes: List[BaseNode],
        **add_kwargs: Any,
    ) -> List[str]:
        """
        Add nodes to index.

        Args:
            nodes: List[BaseNode]: list of nodes with embeddings

        """
        from tcvectordb.model.document import Document

        ids = []
        entries = []
        for node in nodes:
            document = Document(id=node.node_id, vector=node.get_embedding())
            if node.ref_doc_id is not None:
                document.__dict__[DEFAULT_DOC_ID_KEY] = node.ref_doc_id
            if node.metadata is not None:
                document.__dict__[FIELD_METADATA] = json.dumps(node.metadata)
                for field in self._filter_fields:
                    v = node.metadata.get(field.name)
                    if field.match_value(v):
                        document.__dict__[field.name] = v
            if isinstance(node, TextNode) and node.text is not None:
                document.__dict__[DEFAULT_TEXT_KEY] = node.text

            entries.append(document)
            ids.append(node.node_id)

            if len(entries) >= self.batch_size:
                self._collection.upsert(
                    documents=entries, build_index=True, timeout=DEFAULT_TIMEOUT
                )
                entries = []

        if len(entries) > 0:
            self._collection.upsert(
                documents=entries, build_index=True, timeout=DEFAULT_TIMEOUT
            )

        return ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id or ids.

        Args:
            ref_doc_id (str): The doc_id of the document to delete.

        """
        if ref_doc_id is None or len(ref_doc_id) == 0:
            return

        from tcvectordb.model.document import Filter

        delete_ids = ref_doc_id if isinstance(ref_doc_id, list) else [ref_doc_id]
        self._collection.delete(
            filter=Filter(Filter.In(DEFAULT_DOC_ID_KEY, delete_ids))
        )

    def query_by_ids(self, ids: List[str]) -> List[Dict]:
        return self._collection.query(document_ids=ids, limit=len(ids))

    def truncate(self) -> None:
        self._database.truncate_collection(self._collection.collection_name)

    def describe_collection(self) -> Any:
        return self._database.describe_collection(self._collection.collection_name)

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """
        Query index for top k most similar nodes.

        Args:
            query (VectorStoreQuery): contains
                query_embedding (List[float]): query embedding
                similarity_top_k (int): top k most similar nodes
                doc_ids (Optional[List[str]]): filter by doc_id
                filters (Optional[MetadataFilters]): filter result
            kwargs.filter (Optional[str|Filter]):

            if `kwargs` in kwargs:
               using filter: `age > 20 and author in (...) and ...`
            elif query.filters:
               using filter: " and ".join([f'{f.key} = "{f.value}"' for f in query.filters.filters])
            elif query.doc_ids:
               using filter: `doc_id in (query.doc_ids)`

        """
        search_filter = self._to_vdb_filter(query, **kwargs)
        results = self._collection.search(
            vectors=[query.query_embedding],
            limit=query.similarity_top_k,
            retrieve_vector=True,
            output_fields=query.output_fields,
            filter=search_filter,
        )
        if len(results) == 0:
            return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])

        nodes = []
        similarities = []
        ids = []
        for doc in results[0]:
            ids.append(doc.get(FIELD_ID))
            similarities.append(doc.get("score"))

            meta_str = doc.get(FIELD_METADATA)
            meta = {} if meta_str is None else json.loads(meta_str)
            doc_id = doc.get(DEFAULT_DOC_ID_KEY)

            node = TextNode(
                id_=doc.get(FIELD_ID),
                text=doc.get(DEFAULT_TEXT_KEY),
                embedding=doc.get(FIELD_VECTOR),
                metadata=meta,
            )
            if doc_id is not None:
                node.relationships = {
                    NodeRelationship.SOURCE: RelatedNodeInfo(node_id=doc_id)
                }

            nodes.append(node)

        return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)

    @staticmethod
    def _to_vdb_filter(query: VectorStoreQuery, **kwargs: Any) -> Any:
        from tcvectordb.model.document import Filter

        search_filter = None
        if "filter" in kwargs:
            search_filter = kwargs.pop("filter")
            search_filter = (
                search_filter
                if type(search_filter) is Filter
                else Filter(search_filter)
            )
        elif query.filters is not None and len(query.filters.legacy_filters()) > 0:
            search_filter = " and ".join(
                [f'{f.key} = "{f.value}"' for f in query.filters.legacy_filters()]
            )
            search_filter = Filter(search_filter)
        elif query.doc_ids is not None:
            search_filter = Filter(Filter.In(DEFAULT_DOC_ID_KEY, query.doc_ids))

        return search_filter

```
  
---|---  
###  client `property` #
```
client: Any

```

Get client.
###  add #
```
add(nodes: List[BaseNode], **add_kwargs: Any) -> List[str]

```

Add nodes to index.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[BaseNode]` |  List[BaseNode]: list of nodes with embeddings |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-tencentvectordb/llama_index/vector_stores/tencentvectordb/base.py`

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

    """
    from tcvectordb.model.document import Document

    ids = []
    entries = []
    for node in nodes:
        document = Document(id=node.node_id, vector=node.get_embedding())
        if node.ref_doc_id is not None:
            document.__dict__[DEFAULT_DOC_ID_KEY] = node.ref_doc_id
        if node.metadata is not None:
            document.__dict__[FIELD_METADATA] = json.dumps(node.metadata)
            for field in self._filter_fields:
                v = node.metadata.get(field.name)
                if field.match_value(v):
                    document.__dict__[field.name] = v
        if isinstance(node, TextNode) and node.text is not None:
            document.__dict__[DEFAULT_TEXT_KEY] = node.text

        entries.append(document)
        ids.append(node.node_id)

        if len(entries) >= self.batch_size:
            self._collection.upsert(
                documents=entries, build_index=True, timeout=DEFAULT_TIMEOUT
            )
            entries = []

    if len(entries) > 0:
        self._collection.upsert(
            documents=entries, build_index=True, timeout=DEFAULT_TIMEOUT
        )

    return ids

```
  
---|---  
###  delete #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using with ref_doc_id or ids.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`ref_doc_id` |  `str` |  The doc_id of the document to delete. |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-tencentvectordb/llama_index/vector_stores/tencentvectordb/base.py`

| ```
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete nodes using with ref_doc_id or ids.

    Args:
        ref_doc_id (str): The doc_id of the document to delete.

    """
    if ref_doc_id is None or len(ref_doc_id) == 0:
        return

    from tcvectordb.model.document import Filter

    delete_ids = ref_doc_id if isinstance(ref_doc_id, list) else [ref_doc_id]
    self._collection.delete(
        filter=Filter(Filter.In(DEFAULT_DOC_ID_KEY, delete_ids))
    )

```
  
---|---  
###  query #
```
query(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Query index for top k most similar nodes.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `VectorStoreQuery` |  contains query_embedding (List[float]): query embedding similarity_top_k (int): top k most similar nodes doc_ids (Optional[List[str]]): filter by doc_id filters (Optional[MetadataFilters]): filter result |  _required_  
`kwargs.filter` |  `Optional[str | Filter]` |  |  _required_  
`if` |  ``kwargs` in kwargs` |  using filter: `age > 20 and author in (...) and ...` |  _required_  
`elif` |  `filters` |  using filter: " and ".join([f'{f.key} = "{f.value}"' for f in query.filters.filters]) |  _required_  
`elif` |  `doc_ids` |  using filter: `doc_id in (query.doc_ids)` |  _required_  
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-tencentvectordb/llama_index/vector_stores/tencentvectordb/base.py`

| ```
def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
    """
    Query index for top k most similar nodes.

    Args:
        query (VectorStoreQuery): contains
            query_embedding (List[float]): query embedding
            similarity_top_k (int): top k most similar nodes
            doc_ids (Optional[List[str]]): filter by doc_id
            filters (Optional[MetadataFilters]): filter result
        kwargs.filter (Optional[str|Filter]):

        if `kwargs` in kwargs:
           using filter: `age > 20 and author in (...) and ...`
        elif query.filters:
           using filter: " and ".join([f'{f.key} = "{f.value}"' for f in query.filters.filters])
        elif query.doc_ids:
           using filter: `doc_id in (query.doc_ids)`

    """
    search_filter = self._to_vdb_filter(query, **kwargs)
    results = self._collection.search(
        vectors=[query.query_embedding],
        limit=query.similarity_top_k,
        retrieve_vector=True,
        output_fields=query.output_fields,
        filter=search_filter,
    )
    if len(results) == 0:
        return VectorStoreQueryResult(nodes=[], similarities=[], ids=[])

    nodes = []
    similarities = []
    ids = []
    for doc in results[0]:
        ids.append(doc.get(FIELD_ID))
        similarities.append(doc.get("score"))

        meta_str = doc.get(FIELD_METADATA)
        meta = {} if meta_str is None else json.loads(meta_str)
        doc_id = doc.get(DEFAULT_DOC_ID_KEY)

        node = TextNode(
            id_=doc.get(FIELD_ID),
            text=doc.get(DEFAULT_TEXT_KEY),
            embedding=doc.get(FIELD_VECTOR),
            metadata=meta,
        )
        if doc_id is not None:
            node.relationships = {
                NodeRelationship.SOURCE: RelatedNodeInfo(node_id=doc_id)
            }

        nodes.append(node)

    return VectorStoreQueryResult(nodes=nodes, similarities=similarities, ids=ids)

```
  
---|---
