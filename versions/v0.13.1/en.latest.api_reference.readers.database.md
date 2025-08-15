# Database
##  DatabaseReader #
Bases: `BaseReader`
Simple Database reader.
Reads data from a database via a query and returns LlamaIndex Documents. Allows specifying columns for metadata (with optional renaming) and excluding columns from text content. Can also generate custom Document IDs from row data.
The `schema` parameter is not supported when passed with `sql_database`.
If the `sql_database` object was created with a schema, it will be used.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`sql_database` |  `Optional[SQLDatabase]` |  SQL database to use, including table names to specify. See :ref:`Ref-Struct-Store` for more details. |  `None`  
`engine` |  `Optional[Engine]` |  SQLAlchemy Engine object of the database connection. |  `None`  
`uri` |  `Optional[str]` |  uri of the database connection. |  `None`  
`scheme` |  `Optional[str]` |  scheme of the database connection. |  `None`  
`host` |  `Optional[str]` |  host of the database connection. |  `None`  
`port` |  `Optional[int]` |  port of the database connection. |  `None`  
`user` |  `Optional[str]` |  user of the database connection. |  `None`  
`password` |  `Optional[str]` |  password of the database connection. |  `None`  
`dbname` |  `Optional[str]` |  dbname of the database connection. |  `None`  
Returns:
Name | Type | Description  
---|---|---  
`DatabaseReader` |  |  A DatabaseReader object.  
Note
schema (Optional[str]): Database schema **only honored when a connection object is created inside this class** (i.e. when you pass `engine`, `uri`, or individual connection parameters). If you supply an already-built `SQLDatabase`, its internal schema (if any) is used and this argument is ignored.
#### Connection patterns#
+----------------------------+-----------+---------------------------------------+ | Pattern | Supports | Notes | +============================+===========+=======================================+ | `sql_database` | ✖ | Pass a pre-configured `SQLDatabase` | | | | if you need schema handling here. | +----------------------------+-----------+---------------------------------------+ | `engine` + `schema` | ✔ | | +----------------------------+-----------+---------------------------------------+ | `uri` + `schema` | ✔ | | +----------------------------+-----------+---------------------------------------+ | `scheme/host/…` + | ✔ | | | `schema` | | | +----------------------------+-----------+---------------------------------------+
(_schema_ = database namespace; _scheme_ = driver/dialect, e.g. `postgresql+psycopg`)
Source code in `llama-index-integrations/readers/llama-index-readers-database/llama_index/readers/database/base.py`

| ```
class DatabaseReader(BaseReader):
    """
    Simple Database reader.

    Reads data from a database via a query and returns LlamaIndex Documents.
    Allows specifying columns for metadata (with optional renaming) and
    excluding columns from text content. Can also generate custom Document IDs
    from row data.

    Note: The `schema` parameter is not supported when passed with `sql_database`.
        If the `sql_database` object was created with a schema, it will be used.

    Args:
        sql_database (Optional[SQLDatabase]): SQL database to use,
            including table names to specify.
            See :ref:`Ref-Struct-Store` for more details.

        OR

        engine (Optional[Engine]): SQLAlchemy Engine object of the database connection.

        OR

        uri (Optional[str]): uri of the database connection.

        OR

        scheme (Optional[str]): scheme of the database connection.
        host (Optional[str]): host of the database connection.
        port (Optional[int]): port of the database connection.
        user (Optional[str]): user of the database connection.
        password (Optional[str]): password of the database connection.
        dbname (Optional[str]): dbname of the database connection.

    Returns:
        DatabaseReader: A DatabaseReader object.

    Note:
        schema (Optional[str]):
            Database schema **only honored when a connection object is created
            inside this class** (i.e. when you pass `engine`, `uri`, or individual
            connection parameters).
            If you supply an already-built `SQLDatabase`, its internal schema (if
            any) is used and this argument is ignored.

    Connection patterns
    -------------------
    +----------------------------+-----------+---------------------------------------+
    | Pattern                    | Supports  | Notes                                 |
    +============================+===========+=======================================+
    | ``sql_database``           | ✖         | Pass a pre-configured ``SQLDatabase`` |
    |                            |           | if you need schema handling here.     |
    +----------------------------+-----------+---------------------------------------+
    | ``engine`` + ``schema``    | ✔         |                                       |
    +----------------------------+-----------+---------------------------------------+
    | ``uri`` + ``schema``       | ✔         |                                       |
    +----------------------------+-----------+---------------------------------------+
    | ``scheme/host/…`` +        | ✔         |                                       |
    | ``schema``                 |           |                                       |
    +----------------------------+-----------+---------------------------------------+

    (*schema* = database namespace; *scheme* = driver/dialect, e.g. ``postgresql+psycopg``)

    """

    def __init__(
        self,
        sql_database: Optional[SQLDatabase] = None,
        engine: Optional[Engine] = None,
        uri: Optional[str] = None,
        scheme: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
        schema: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Initialize with parameters."""
        db_kwargs = kwargs.copy()
        if schema and not sql_database:
            db_kwargs["schema"] = schema
            self.schema = schema if schema else db_kwargs.get("schema", None)
        else:
            self.schema = None

        if sql_database:
            self.sql_database = sql_database
        elif engine:
            self.sql_database = SQLDatabase(engine, *args, **db_kwargs)
        elif uri:
            self.uri = uri
            self.sql_database = SQLDatabase.from_uri(uri, *args, **db_kwargs)
        elif scheme and host and port and user and password and dbname:
            uri = f"{scheme}://{user}:{password}@{host}:{port}/{dbname}"
            self.uri = uri
            self.sql_database = SQLDatabase.from_uri(uri, *args, **db_kwargs)
        else:
            raise ValueError(
                "You must provide either a SQLDatabase, "
                "a SQL Alchemy Engine, a valid connection URI, or a valid "
                "set of credentials."
            )

    def lazy_load_data(
        self,
        query: str,
        metadata_cols: Optional[Iterable[Union[str, Tuple[str, str]]]] = None,
        excluded_text_cols: Optional[Iterable[str]] = None,
        document_id: Optional[Callable[[Dict[str, Any]], str]] = None,
        **load_kwargs: Any,
    ) -> Generator[Document, Any, None]:
        """
        Lazily query and load data from the Database.

        Args:
            query (str): SQL query to execute.
            metadata_cols (Optional[Iterable[Union[str, Tuple[str, str]]]]):
                Iterable of column names or (db_col, meta_key) tuples to include
                in Document metadata. If str, the column name is used as key.
                If tuple, uses first element as DB column and second as metadata key.
                If two entries map to the same metadata key, the latter will silently
                overwrite the former - **avoid duplicates**.
            excluded_text_cols (Optional[Iterable[str]]): Iterable of column names to be
                excluded from Document text. Useful for metadata-only columns.
            document_id (Optional[Callable[[Dict[str, Any]], str]]): A function
                that takes a row (as a dict) and returns a string to be used as the
                Document's `id_`, this replaces the deprecated `doc_id` field.
                **MUST** return a string, falling back to auto-generated UUID.
            **load_kwargs: Additional keyword arguments (ignored).

        Yields:
            Document: A Document object for each row fetched.

        Usage Pattern for Metadata-Only Columns:
            To include `my_col` ONLY in metadata (not text), specify it in
            `metadata_cols=['my_col']` and `excluded_text_cols=['my_col']`.

        Usage Pattern for Renaming Metadata Keys:
            To include DB column `db_col_name` in metadata with the key `meta_key_name`,
            use `metadata_cols=[('db_col_name', 'meta_key_name')]`.

        """
        exclude_set: Set[str] = set(excluded_text_cols or [])
        missing_columns: Set[str] = set()
        invalid_columns: Set[str] = set()

        with self.sql_database.engine.connect() as connection:
            if not query:
                raise ValueError("A query parameter is necessary.")

            result = connection.execute(text(query))
            column_names = list(result.keys())

            for row in result:
                row_values: Dict[str, Any] = dict(zip(column_names, row))
                doc_metadata: Dict[str, Any] = {}

                # Process metadata_cols based on Union type
                if metadata_cols:
                    for item in metadata_cols:
                        db_col: str
                        meta_key: str
                        if isinstance(item, str):
                            db_col = item
                            meta_key = item
                        elif (
                            isinstance(item, tuple)
                            and len(item) == 2
                            and all(isinstance(s, str) for s in item)
                        ):
                            db_col, meta_key = item
                        elif f"{item!r}" not in invalid_columns:
                            invalid_columns.add(f"{item!r}")
                            logger.warning(
                                f"Skipping invalid item in metadata_cols: {item!r}"
                            )
                            continue
                        else:
                            continue

                        if db_col in row_values:
                            doc_metadata[meta_key] = row_values[db_col]
                        elif db_col not in row_values and db_col not in missing_columns:
                            missing_columns.add(db_col)
                            logger.warning(
                                f"Column '{db_col}' specified in metadata_cols not found in query result."
                            )

                # Prepare text content
                text_parts: List[str] = [
                    f"{col}: {val}"
                    for col, val in row_values.items()
                    if col not in exclude_set
                ]
                text_resource = MediaResource(text=", ".join(text_parts))
                params = {
                    "text_resource": text_resource,
                    "metadata": doc_metadata,
                }

                if document_id:
                    try:
                        # Ensure function receives the row data
                        id_: Optional[str] = document_id(row_values)
                        if not isinstance(id_, str):
                            logger.warning(
                                f"document_id did not return a string for row {row_values}. Got: {type(id_)}"
                            )
                        if id_ is not None:
                            params["id_"] = id_
                    except Exception as e:
                        logger.warning(
                            f"document_id failed for row {row_values}: {e}",
                            exc_info=True,
                        )

                yield Document(**params)

```
  
---|---  
###  lazy_load_data #
```
lazy_load_data(query: str, metadata_cols: Optional[Iterable[Union[str, Tuple[str, str]]]] = None, excluded_text_cols: Optional[Iterable[str]] = None, document_id: Optional[Callable[[Dict[str, Any]], str]] = None, **load_kwargs: Any) -> Generator[Document, Any, None]

```

Lazily query and load data from the Database.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  SQL query to execute. |  _required_  
`metadata_cols` |  `Optional[Iterable[Union[str, Tuple[str, str]]]]` |  Iterable of column names or (db_col, meta_key) tuples to include in Document metadata. If str, the column name is used as key. If tuple, uses first element as DB column and second as metadata key. If two entries map to the same metadata key, the latter will silently overwrite the former - **avoid duplicates**. |  `None`  
`excluded_text_cols` |  `Optional[Iterable[str]]` |  Iterable of column names to be excluded from Document text. Useful for metadata-only columns. |  `None`  
`document_id` |  `Optional[Callable[[Dict[str, Any]], str]]` |  A function that takes a row (as a dict) and returns a string to be used as the Document's `id_`, this replaces the deprecated `doc_id` field. **MUST** return a string, falling back to auto-generated UUID. |  `None`  
`**load_kwargs` |  `Any` |  Additional keyword arguments (ignored). |  `{}`  
Yields:
Name | Type | Description  
---|---|---  
`Document` |  `Document` |  A Document object for each row fetched.  
Usage Pattern for Metadata-Only Columns
To include `my_col` ONLY in metadata (not text), specify it in `metadata_cols=['my_col']` and `excluded_text_cols=['my_col']`.
Usage Pattern for Renaming Metadata Keys
To include DB column `db_col_name` in metadata with the key `meta_key_name`, use `metadata_cols=[('db_col_name', 'meta_key_name')]`.
Source code in `llama-index-integrations/readers/llama-index-readers-database/llama_index/readers/database/base.py`

| ```
def lazy_load_data(
    self,
    query: str,
    metadata_cols: Optional[Iterable[Union[str, Tuple[str, str]]]] = None,
    excluded_text_cols: Optional[Iterable[str]] = None,
    document_id: Optional[Callable[[Dict[str, Any]], str]] = None,
    **load_kwargs: Any,
) -> Generator[Document, Any, None]:
    """
    Lazily query and load data from the Database.

    Args:
        query (str): SQL query to execute.
        metadata_cols (Optional[Iterable[Union[str, Tuple[str, str]]]]):
            Iterable of column names or (db_col, meta_key) tuples to include
            in Document metadata. If str, the column name is used as key.
            If tuple, uses first element as DB column and second as metadata key.
            If two entries map to the same metadata key, the latter will silently
            overwrite the former - **avoid duplicates**.
        excluded_text_cols (Optional[Iterable[str]]): Iterable of column names to be
            excluded from Document text. Useful for metadata-only columns.
        document_id (Optional[Callable[[Dict[str, Any]], str]]): A function
            that takes a row (as a dict) and returns a string to be used as the
            Document's `id_`, this replaces the deprecated `doc_id` field.
            **MUST** return a string, falling back to auto-generated UUID.
        **load_kwargs: Additional keyword arguments (ignored).

    Yields:
        Document: A Document object for each row fetched.

    Usage Pattern for Metadata-Only Columns:
        To include `my_col` ONLY in metadata (not text), specify it in
        `metadata_cols=['my_col']` and `excluded_text_cols=['my_col']`.

    Usage Pattern for Renaming Metadata Keys:
        To include DB column `db_col_name` in metadata with the key `meta_key_name`,
        use `metadata_cols=[('db_col_name', 'meta_key_name')]`.

    """
    exclude_set: Set[str] = set(excluded_text_cols or [])
    missing_columns: Set[str] = set()
    invalid_columns: Set[str] = set()

    with self.sql_database.engine.connect() as connection:
        if not query:
            raise ValueError("A query parameter is necessary.")

        result = connection.execute(text(query))
        column_names = list(result.keys())

        for row in result:
            row_values: Dict[str, Any] = dict(zip(column_names, row))
            doc_metadata: Dict[str, Any] = {}

            # Process metadata_cols based on Union type
            if metadata_cols:
                for item in metadata_cols:
                    db_col: str
                    meta_key: str
                    if isinstance(item, str):
                        db_col = item
                        meta_key = item
                    elif (
                        isinstance(item, tuple)
                        and len(item) == 2
                        and all(isinstance(s, str) for s in item)
                    ):
                        db_col, meta_key = item
                    elif f"{item!r}" not in invalid_columns:
                        invalid_columns.add(f"{item!r}")
                        logger.warning(
                            f"Skipping invalid item in metadata_cols: {item!r}"
                        )
                        continue
                    else:
                        continue

                    if db_col in row_values:
                        doc_metadata[meta_key] = row_values[db_col]
                    elif db_col not in row_values and db_col not in missing_columns:
                        missing_columns.add(db_col)
                        logger.warning(
                            f"Column '{db_col}' specified in metadata_cols not found in query result."
                        )

            # Prepare text content
            text_parts: List[str] = [
                f"{col}: {val}"
                for col, val in row_values.items()
                if col not in exclude_set
            ]
            text_resource = MediaResource(text=", ".join(text_parts))
            params = {
                "text_resource": text_resource,
                "metadata": doc_metadata,
            }

            if document_id:
                try:
                    # Ensure function receives the row data
                    id_: Optional[str] = document_id(row_values)
                    if not isinstance(id_, str):
                        logger.warning(
                            f"document_id did not return a string for row {row_values}. Got: {type(id_)}"
                        )
                    if id_ is not None:
                        params["id_"] = id_
                except Exception as e:
                    logger.warning(
                        f"document_id failed for row {row_values}: {e}",
                        exc_info=True,
                    )

            yield Document(**params)

```
  
---|---
