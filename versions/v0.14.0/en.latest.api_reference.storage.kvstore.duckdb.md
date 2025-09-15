# Duckdb
##  DuckDBKVStore #
Bases: `BaseKVStore`
DuckDB KV Store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`duckdb_uri` |  `str` |  DuckDB URI |  _required_  
`duckdb_client` |  `Any` |  DuckDB client |  _required_  
`async_duckdb_client` |  `Any` |  Async DuckDB client |  _required_  
Raises:
Type | Description  
---|---  
`ValueError` |  If duckdb-py is not installed  
Examples:
```
>>> from llama_index.storage.kvstore.duckdb import DuckDBKVStore
>>> # Create a DuckDBKVStore
>>> duckdb_kv_store = DuckDBKVStore(
>>>     duckdb_url="duckdb://127.0.0.1:6379")

```

Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
class DuckDBKVStore(BaseKVStore):
    """
    DuckDB KV Store.

    Args:
        duckdb_uri (str): DuckDB URI
        duckdb_client (Any): DuckDB client
        async_duckdb_client (Any): Async DuckDB client

    Raises:
            ValueError: If duckdb-py is not installed

    Examples:
        >>> from llama_index.storage.kvstore.duckdb import DuckDBKVStore
        >>> # Create a DuckDBKVStore
        >>> duckdb_kv_store = DuckDBKVStore(
        >>>     duckdb_url="duckdb://127.0.0.1:6379")

    """

    database_name: str
    table_name: str
    persist_dir: str

    _shared_conn: Optional[duckdb.DuckDBPyConnection] = None

    _is_initialized: bool = False

    def __init__(
        self,
        database_name: str = ":memory:",
        table_name: str = "keyvalue",
        # https://duckdb.org/docs/extensions/full_text_search
        persist_dir: str = "./storage",
        client: Optional[duckdb.DuckDBPyConnection] = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> None:
        """Init params."""
        if client is not None:
            self._shared_conn = client.cursor()

        self.database_name = database_name
        self.table_name = table_name
        self.persist_dir = persist_dir

        self._thread_local = threading.local()

        _ = self._initialize_table(self.client, self.table_name)

    @classmethod
    def from_vector_store(
        cls, duckdb_vector_store, table_name: str = "keyvalue"
    ) -> "DuckDBKVStore":
        """
        Load a DuckDBKVStore from a DuckDB Client.

        Args:
            client (DuckDB): DuckDB client

        """
        from llama_index.vector_stores.duckdb.base import DuckDBVectorStore

        assert isinstance(duckdb_vector_store, DuckDBVectorStore)

        return cls(
            database_name=duckdb_vector_store.database_name,
            table_name=table_name,
            persist_dir=duckdb_vector_store.persist_dir,
            client=duckdb_vector_store.client,
        )

    @property
    def client(self) -> duckdb.DuckDBPyConnection:
        """Return client."""
        if self._shared_conn is None:
            self._shared_conn = self._connect(self.database_name, self.persist_dir)

        if not hasattr(self._thread_local, "conn") or self._thread_local.conn is None:
            self._thread_local.conn = self._shared_conn.cursor()

        return self._thread_local.conn

    @classmethod
    def _connect(
        cls, database_name: str, persist_dir: str
    ) -> duckdb.DuckDBPyConnection:
        """Connect to the DuckDB database -- create the data persistence directory if it doesn't exist."""
        database_connection = database_name

        if database_name != ":memory:":
            persist_path = Path(persist_dir)

            if not persist_path.exists():
                persist_path.mkdir(parents=True, exist_ok=True)

            database_connection = str(persist_path / database_name)

        return duckdb.connect(database_connection)

    @property
    def table(self) -> duckdb.DuckDBPyRelation:
        """Return the table for the connection to the DuckDB database."""
        return self.client.table(self.table_name)

    @classmethod
    def _initialize_table(
        cls, conn: duckdb.DuckDBPyConnection, table_name: str
    ) -> duckdb.DuckDBPyRelation:
        """Initialize the DuckDB Database, extensions, and documents table."""
        home_dir = Path.home()
        conn.execute(f"SET home_directory='{home_dir}';")
        conn.install_extension("json")
        conn.load_extension("json")

        _ = (
            conn.begin()
            .execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name}  (
                key VARCHAR,
                collection VARCHAR,
                value JSON,
                PRIMARY KEY (key, collection)
            );

            CREATE INDEX IF NOT EXISTS collection_idx ON {table_name} (collection);
        """)
            .commit()
        )

        table = conn.table(table_name)

        required_columns = ["key", "value"]
        table_columns = table.describe().columns

        for column in required_columns:
            if column not in table_columns:
                raise DuckDBTableIncorrectColumnsError(
                    table_name, required_columns, table_columns
                )

        return table

    @override
    def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        self.put_all([(key, val)], collection)

    @override
    async def aput(
        self, key: str, val: dict, collection: str = DEFAULT_COLLECTION
    ) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        await asyncio.to_thread(self.put, key, val, collection)

    @override
    def put_all(
        self,
        kv_pairs: list[tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Put a dictionary of key-value pairs into the store.

        Args:
            kv_pairs (List[Tuple[str, dict]]): key-value pairs
            collection (str): collection name

        """
        if len(kv_pairs) == 0:
            return

        rows = [
            {"key": key, "collection": collection, "value": json.dumps(value)}
            for key, value in kv_pairs
        ]
        arrow_table = pyarrow.Table.from_pylist(rows)

        _ = self.client.sql(
            query=f"""
            INSERT OR REPLACE INTO {self.table.alias}
            SELECT * from arrow_table;
            """,
        )

    @override
    async def aput_all(
        self,
        kv_pairs: list[tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Put a dictionary of key-value pairs into the store.

        Args:
            kv_pairs (List[Tuple[str, dict]]): key-value pairs
            collection (str): collection name

        """
        await asyncio.to_thread(self.put_all, kv_pairs, collection, batch_size)

    @override
    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        expression: Expression = (
            ColumnExpression("collection")
            .__eq__(ConstantExpression(collection))
            .__and__(ColumnExpression("key").__eq__(ConstantExpression(key)))
        )
        row_result = self.table.filter(filter_expr=expression).fetchone()

        if row_result is None:
            return None

        return json.loads(row_result[2])

    @override
    async def aget(
        self, key: str, collection: str = DEFAULT_COLLECTION
    ) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        return await asyncio.to_thread(self.get, key, collection)

    @override
    def get_all(self, collection: str = DEFAULT_COLLECTION) -> dict[str, dict]:
        """Get all values from the store."""
        filter_expr: Expression = ColumnExpression("collection").__eq__(
            ConstantExpression(collection)
        )

        table: pyarrow.Table = self.table.filter(
            filter_expr=filter_expr
        ).fetch_arrow_table()

        as_list = table.to_pylist()

        return {row["key"]: json.loads(row["value"]) for row in as_list}

    @override
    async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> dict[str, dict]:
        """Get all values from the store."""
        return self.get_all(collection)

    @override
    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        filter_expression = (
            ColumnExpression("collection")
            .__eq__(ConstantExpression(collection))
            .__and__(ColumnExpression("key").__eq__(ConstantExpression(key)))
        )

        command = f"DELETE FROM {self.table.alias} WHERE {filter_expression}"
        _ = self.client.execute(command)
        return True

    @override
    async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        return self.delete(key, collection)

```
  
---|---  
###  client `property` #
```
client: DuckDBPyConnection

```

Return client.
###  table `property` #
```
table: DuckDBPyRelation

```

Return the table for the connection to the DuckDB database.
###  from_vector_store `classmethod` #
```
from_vector_store(duckdb_vector_store, table_name: str = 'keyvalue') -> DuckDBKVStore

```

Load a DuckDBKVStore from a DuckDB Client.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`client` |  `DuckDB` |  DuckDB client |  _required_  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@classmethod
def from_vector_store(
    cls, duckdb_vector_store, table_name: str = "keyvalue"
) -> "DuckDBKVStore":
    """
    Load a DuckDBKVStore from a DuckDB Client.

    Args:
        client (DuckDB): DuckDB client

    """
    from llama_index.vector_stores.duckdb.base import DuckDBVectorStore

    assert isinstance(duckdb_vector_store, DuckDBVectorStore)

    return cls(
        database_name=duckdb_vector_store.database_name,
        table_name=table_name,
        persist_dir=duckdb_vector_store.persist_dir,
        client=duckdb_vector_store.client,
    )

```
  
---|---  
###  put #
```
put(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    self.put_all([(key, val)], collection)

```
  
---|---  
###  aput `async` #
```
aput(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
async def aput(
    self, key: str, val: dict, collection: str = DEFAULT_COLLECTION
) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    await asyncio.to_thread(self.put, key, val, collection)

```
  
---|---  
###  put_all #
```
put_all(kv_pairs: list[tuple[str, dict]], collection: str = DEFAULT_COLLECTION, batch_size: int = DEFAULT_BATCH_SIZE) -> None

```

Put a dictionary of key-value pairs into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`kv_pairs` |  `List[Tuple[str, dict]]` |  key-value pairs |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
def put_all(
    self,
    kv_pairs: list[tuple[str, dict]],
    collection: str = DEFAULT_COLLECTION,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """
    Put a dictionary of key-value pairs into the store.

    Args:
        kv_pairs (List[Tuple[str, dict]]): key-value pairs
        collection (str): collection name

    """
    if len(kv_pairs) == 0:
        return

    rows = [
        {"key": key, "collection": collection, "value": json.dumps(value)}
        for key, value in kv_pairs
    ]
    arrow_table = pyarrow.Table.from_pylist(rows)

    _ = self.client.sql(
        query=f"""
        INSERT OR REPLACE INTO {self.table.alias}
        SELECT * from arrow_table;
        """,
    )

```
  
---|---  
###  aput_all `async` #
```
aput_all(kv_pairs: list[tuple[str, dict]], collection: str = DEFAULT_COLLECTION, batch_size: int = DEFAULT_BATCH_SIZE) -> None

```

Put a dictionary of key-value pairs into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`kv_pairs` |  `List[Tuple[str, dict]]` |  key-value pairs |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
async def aput_all(
    self,
    kv_pairs: list[tuple[str, dict]],
    collection: str = DEFAULT_COLLECTION,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """
    Put a dictionary of key-value pairs into the store.

    Args:
        kv_pairs (List[Tuple[str, dict]]): key-value pairs
        collection (str): collection name

    """
    await asyncio.to_thread(self.put_all, kv_pairs, collection, batch_size)

```
  
---|---  
###  get #
```
get(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    expression: Expression = (
        ColumnExpression("collection")
        .__eq__(ConstantExpression(collection))
        .__and__(ColumnExpression("key").__eq__(ConstantExpression(key)))
    )
    row_result = self.table.filter(filter_expr=expression).fetchone()

    if row_result is None:
        return None

    return json.loads(row_result[2])

```
  
---|---  
###  aget `async` #
```
aget(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
async def aget(
    self, key: str, collection: str = DEFAULT_COLLECTION
) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    return await asyncio.to_thread(self.get, key, collection)

```
  
---|---  
###  get_all #
```
get_all(collection: str = DEFAULT_COLLECTION) -> dict[str, dict]

```

Get all values from the store.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
def get_all(self, collection: str = DEFAULT_COLLECTION) -> dict[str, dict]:
    """Get all values from the store."""
    filter_expr: Expression = ColumnExpression("collection").__eq__(
        ConstantExpression(collection)
    )

    table: pyarrow.Table = self.table.filter(
        filter_expr=filter_expr
    ).fetch_arrow_table()

    as_list = table.to_pylist()

    return {row["key"]: json.loads(row["value"]) for row in as_list}

```
  
---|---  
###  aget_all `async` #
```
aget_all(collection: str = DEFAULT_COLLECTION) -> dict[str, dict]

```

Get all values from the store.
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> dict[str, dict]:
    """Get all values from the store."""
    return self.get_all(collection)

```
  
---|---  
###  delete #
```
delete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    filter_expression = (
        ColumnExpression("collection")
        .__eq__(ConstantExpression(collection))
        .__and__(ColumnExpression("key").__eq__(ConstantExpression(key)))
    )

    command = f"DELETE FROM {self.table.alias} WHERE {filter_expression}"
    _ = self.client.execute(command)
    return True

```
  
---|---  
###  adelete `async` #
```
adelete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-duckdb/llama_index/storage/kvstore/duckdb/base.py`

| ```
@override
async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    return self.delete(key, collection)

```
  
---|---
