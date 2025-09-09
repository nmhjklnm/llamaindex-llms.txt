# Oracledb
##  OraLlamaVS #
Bases: `BasePydanticVectorStore`
`OraLlamaVS` vector store.
To use, you should have both: - the `oracledb` python package installed - a connection string associated with a OracleVS having deployed an Search index
Example
.. code-block:: python
```
from llama-index.core.vectorstores import OracleVS
from oracledb import oracledb

with oracledb.connect(user = user, passwd = pwd, dsn = dsn) as connection:
    print ("Database version:", connection.version)

```
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-oracledb/llama_index/vector_stores/oracledb/base.py`

| ```
class OraLlamaVS(BasePydanticVectorStore):
    """
    `OraLlamaVS` vector store.

    To use, you should have both:
    - the ``oracledb`` python package installed
    - a connection string associated with a OracleVS having deployed an
       Search index

    Example:
        .. code-block:: python

            from llama-index.core.vectorstores import OracleVS
            from oracledb import oracledb

            with oracledb.connect(user = user, passwd = pwd, dsn = dsn) as connection:
                print ("Database version:", connection.version)

    """

    AMPLIFY_RATIO_LE5: ClassVar[int] = 100
    AMPLIFY_RATIO_GT5: ClassVar[int] = 20
    AMPLIFY_RATIO_GT50: ClassVar[int] = 10
    metadata_column: str = "metadata"
    stores_text: bool = True
    _client: Connection = PrivateAttr()
    table_name: str
    distance_strategy: DistanceStrategy
    batch_size: Optional[int]
    params: Optional[dict[str, Any]]

    def __init__(
        self,
        _client: Connection,
        table_name: str,
        distance_strategy: DistanceStrategy = DistanceStrategy.EUCLIDEAN_DISTANCE,
        batch_size: Optional[int] = 32,
        params: Optional[dict[str, Any]] = None,
    ):
        try:
            import oracledb
        except ImportError as e:
            raise ImportError(
                "Unable to import oracledb, please install with "
                "`pip install -U oracledb`."
            ) from e

        try:
            """Initialize with necessary components."""
            super().__init__(
                table_name=table_name,
                distance_strategy=distance_strategy,
                batch_size=batch_size,
                params=params,
            )
            # Assign _client to PrivateAttr after the Pydantic initialization
            object.__setattr__(self, "_client", _client)
            _create_table(_client, table_name)

        except oracledb.DatabaseError as db_err:
            logger.exception(f"Database error occurred while create table: {db_err}")
            raise RuntimeError(
                "Failed to create table due to a database error."
            ) from db_err
        except ValueError as val_err:
            logger.exception(f"Validation error: {val_err}")
            raise RuntimeError(
                "Failed to create table due to a validation error."
            ) from val_err
        except Exception as ex:
            logger.exception("An unexpected error occurred while creating the index.")
            raise RuntimeError(
                "Failed to create table due to an unexpected error."
            ) from ex

    @property
    def client(self) -> Any:
        """Get client."""
        return self._client

    @classmethod
    def class_name(cls) -> str:
        return "OraLlamaVS"

    def _append_meta_filter_condition(
        self, where_str: Optional[str], exact_match_filter: list
    ) -> Tuple[str, list]:
        bind_variables = []
        filter_conditions = []

        # Validate metadata keys (only allow alphanumeric and underscores)
        for filter_item in exact_match_filter:
            # Validate the key - only allow safe characters for JSON path
            if not re.match(r"^[a-zA-Z0-9_]+$", filter_item.key):
                raise ValueError(f"Invalid metadata key format: {filter_item.key}")
            # Use JSON_VALUE with parameterized values
            filter_conditions.append(
                f"JSON_VALUE({self.metadata_column}, '$.{filter_item.key}') = :value{len(bind_variables)}"
            )
            bind_variables.append(filter_item.value)

        # Convert filter conditions to a single string
        filter_str = " AND ".join(filter_conditions)

        if where_str is None:
            where_str = filter_str
        else:
            where_str += " AND " + filter_str

        return where_str, bind_variables

    def _build_insert(self, values: List[BaseNode]) -> Tuple[str, List[tuple]]:
        _data = []
        for item in values:
            item_values = tuple(
                column["extract_func"](item) for column in column_config.values()
            )
            _data.append(item_values)

        dml = f"""
           INSERT INTO {self.table_name} ({", ".join(column_config.keys())})
           VALUES ({", ".join([":" + str(i + 1) for i in range(len(column_config))])})
        """
        return dml, _data

    def _build_query(
        self, distance_function: str, k: int, where_str: Optional[str] = None
    ) -> str:
        where_clause = f"WHERE {where_str}" if where_str else ""

        return f"""
            SELECT id,
                doc_id,
                text,
                node_info,
                metadata,
                vector_distance(embedding, :embedding, {distance_function}) AS distance
            FROM {self.table_name}
            {where_clause}
            ORDER BY distance
            FETCH APPROX FIRST {k} ROWS ONLY
        """

    def _build_hybrid_query(
        self, sub_query: str, query_str: str, similarity_top_k: int
    ) -> str:
        terms_pattern = [f"(?i){x}" for x in query_str.split(" ")]
        column_keys = column_config.keys()
        return (
            f"SELECT {','.join(filter(lambda k: k != 'embedding', column_keys))}, "
            f"distance FROM ({sub_query}) temp_table "
            f"ORDER BY length(multiMatchAllIndices(text, {terms_pattern})) "
            f"AS distance1 DESC, "
            f"log(1 + countMatches(text, '(?i)({query_str.replace(' ', '|')})')) "
            f"AS distance2 DESC limit {similarity_top_k}"
        )

    @_handle_exceptions
    def add(self, nodes: list[BaseNode], **kwargs: Any) -> list[str]:
        if not nodes:
            return []

        for result_batch in iter_batch(nodes, self.batch_size):
            dml, bind_values = self._build_insert(values=result_batch)

            with self._client.cursor() as cursor:
                # Use executemany to insert the batch
                cursor.executemany(dml, bind_values)
                self._client.commit()

        return [node.node_id for node in nodes]

    @_handle_exceptions
    def delete(self, ref_doc_id: str, **kwargs: Any) -> None:
        with self._client.cursor() as cursor:
            ddl = f"DELETE FROM {self.table_name} WHERE doc_id = :ref_doc_id"
            cursor.execute(ddl, [ref_doc_id])
            self._client.commit()

    @_handle_exceptions
    def _get_clob_value(self, result: Any) -> str:
        try:
            import oracledb
        except ImportError as e:
            raise ImportError(
                "Unable to import oracledb, please install with "
                "`pip install -U oracledb`."
            ) from e

        clob_value = ""
        if result:
            if isinstance(result, oracledb.LOB):
                raw_data = result.read()
                if isinstance(raw_data, bytes):
                    clob_value = raw_data.decode(
                        "utf-8"
                    )  # Specify the correct encoding
                else:
                    clob_value = raw_data
            elif isinstance(result, str):
                clob_value = result
            else:
                raise Exception("Unexpected type:", type(result))
        return clob_value

    @_handle_exceptions
    def drop(self) -> None:
        drop_table_purge(self._client, self.table_name)

    @_handle_exceptions
    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        distance_function = _get_distance_function(self.distance_strategy)
        where_str = None
        params = {}
        if query.doc_ids:
            placeholders = ", ".join([f":doc_id{i}" for i in range(len(query.doc_ids))])
            where_str = f"doc_id in ({placeholders})"
            for i, doc_id in enumerate(query.doc_ids):
                params[f"doc_id{i}"] = doc_id

        bind_vars = []
        if query.filters is not None:
            where_str, bind_vars = self._append_meta_filter_condition(
                where_str, query.filters.filters
            )

        # build query sql
        query_sql = self._build_query(
            distance_function, query.similarity_top_k, where_str
        )
        """
        if query.mode == VectorStoreQueryMode.HYBRID and query.query_str is not None:
            amplify_ratio = self.AMPLIFY_RATIO_LE5
            if 5 < query.similarity_top_k < 50:
                amplify_ratio = self.AMPLIFY_RATIO_GT5
            if query.similarity_top_k > 50:
                amplify_ratio = self.AMPLIFY_RATIO_GT50
            query_sql = self._build_hybrid_query(
                self._build_query(
                    query_embed=query.query_embedding,
                    k=query.similarity_top_k,
                    where_str=where_str,
                    limit=query.similarity_top_k * amplify_ratio,
                ),
                query.query_str,
                query.similarity_top_k,
            )
            logger.debug(f"hybrid query_statement={query_statement}")
        """
        embedding = array.array("f", query.query_embedding)
        params = {"embedding": embedding}
        for i, value in enumerate(bind_vars):
            params[f"value{i}"] = value
        with self._client.cursor() as cursor:
            cursor.execute(query_sql, **params)
            results = cursor.fetchall()

            similarities = []
            ids = []
            nodes = []
            for result in results:
                doc_id = result[1]
                text = self._get_clob_value(result[2])
                node_info = (
                    json.loads(result[3]) if isinstance(result[3], str) else result[3]
                )
                metadata = (
                    json.loads(result[4]) if isinstance(result[4], str) else result[4]
                )

                if query.node_ids:
                    if result[0] not in query.node_ids:
                        continue

                if isinstance(node_info, dict):
                    start_char_idx = node_info.get("start", None)
                    end_char_idx = node_info.get("end", None)
                try:
                    node = metadata_dict_to_node(metadata)
                    node.set_content(text)
                except Exception:
                    # Note: deprecated legacy logic for backward compatibility

                    node = TextNode(
                        id_=result[0],
                        text=text,
                        metadata=metadata,
                        start_char_idx=start_char_idx,
                        end_char_idx=end_char_idx,
                        relationships={
                            NodeRelationship.SOURCE: RelatedNodeInfo(node_id=doc_id)
                        },
                    )

                nodes.append(node)
                similarities.append(1.0 - math.exp(-result[5]))
                ids.append(result[0])
            return VectorStoreQueryResult(
                nodes=nodes, similarities=similarities, ids=ids
            )

    @classmethod
    @_handle_exceptions
    def from_documents(
        cls: Type[OraLlamaVS],
        docs: List[TextNode],
        table_name: str = "llama_index",
        **kwargs: Any,
    ) -> OraLlamaVS:
        """Return VectorStore initialized from texts and embeddings."""
        _client = kwargs.get("client")
        if _client is None:
            raise ValueError("client parameter is required...")
        params = kwargs.get("params")
        distance_strategy = kwargs.get("distance_strategy")
        drop_table_purge(_client, table_name)

        vss = cls(
            _client=_client,
            table_name=table_name,
            params=params,
            distance_strategy=distance_strategy,
        )
        vss.add(nodes=docs)
        return vss

```
  
---|---  
###  client `property` #
```
client: Any

```

Get client.
###  from_documents `classmethod` #
```
from_documents(docs: List[TextNode], table_name: str = 'llama_index', **kwargs: Any) -> OraLlamaVS

```

Return VectorStore initialized from texts and embeddings.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-oracledb/llama_index/vector_stores/oracledb/base.py`

| ```
@classmethod
@_handle_exceptions
def from_documents(
    cls: Type[OraLlamaVS],
    docs: List[TextNode],
    table_name: str = "llama_index",
    **kwargs: Any,
) -> OraLlamaVS:
    """Return VectorStore initialized from texts and embeddings."""
    _client = kwargs.get("client")
    if _client is None:
        raise ValueError("client parameter is required...")
    params = kwargs.get("params")
    distance_strategy = kwargs.get("distance_strategy")
    drop_table_purge(_client, table_name)

    vss = cls(
        _client=_client,
        table_name=table_name,
        params=params,
        distance_strategy=distance_strategy,
    )
    vss.add(nodes=docs)
    return vss

```
  
---|---
