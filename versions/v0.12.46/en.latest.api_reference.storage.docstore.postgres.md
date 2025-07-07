# Postgres
##  PostgresDocumentStore #
Bases: `KVDocumentStore`
Postgres Document (Node) store.
A Postgres store for Document and Node objects.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`postgres_kvstore` |  `PostgresKVStore` |  Postgres key-value store |  _required_  
`namespace` |  `str` |  namespace for the docstore |  `None`  
`batch_size` |  `int` |  batch size for bulk operations |  `DEFAULT_BATCH_SIZE`  
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-postgres/llama_index/storage/docstore/postgres/base.py`

| ```
class PostgresDocumentStore(KVDocumentStore):
    """
    Postgres Document (Node) store.

    A Postgres store for Document and Node objects.

    Args:
        postgres_kvstore (PostgresKVStore): Postgres key-value store
        namespace (str): namespace for the docstore
        batch_size (int): batch size for bulk operations

    """

    def __init__(
        self,
        postgres_kvstore: PostgresKVStore,
        namespace: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Init a PostgresDocumentStore."""
        super().__init__(postgres_kvstore, namespace=namespace, batch_size=batch_size)

    @classmethod
    def from_uri(
        cls,
        uri: str,
        namespace: Optional[str] = None,
        table_name: str = "docstore",
        schema_name: str = "public",
        perform_setup: bool = True,
        debug: bool = False,
        use_jsonb: bool = False,
    ) -> "PostgresDocumentStore":
        """Load a PostgresDocumentStore from a Postgres URI."""
        postgres_kvstore = PostgresKVStore.from_uri(
            uri=uri,
            table_name=table_name,
            schema_name=schema_name,
            perform_setup=perform_setup,
            debug=debug,
            use_jsonb=use_jsonb,
        )
        return cls(postgres_kvstore, namespace)

    @classmethod
    def from_params(
        cls,
        host: Optional[str] = None,
        port: Optional[str] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        namespace: Optional[str] = None,
        table_name: str = "docstore",
        schema_name: str = "public",
        perform_setup: bool = True,
        debug: bool = False,
        use_jsonb: bool = False,
    ) -> "PostgresDocumentStore":
        """Load a PostgresDocumentStore from a Postgres host and port."""
        postgres_kvstore = PostgresKVStore.from_params(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            table_name=table_name,
            schema_name=schema_name,
            perform_setup=perform_setup,
            debug=debug,
            use_jsonb=use_jsonb,
        )
        return cls(postgres_kvstore, namespace)

```
  
---|---  
###  from_uri `classmethod` #
```
from_uri(uri: str, namespace: Optional[str] = None, table_name: str = 'docstore', schema_name: str = 'public', perform_setup: bool = True, debug: bool = False, use_jsonb: bool = False) -> PostgresDocumentStore

```

Load a PostgresDocumentStore from a Postgres URI.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-postgres/llama_index/storage/docstore/postgres/base.py`

| ```
@classmethod
def from_uri(
    cls,
    uri: str,
    namespace: Optional[str] = None,
    table_name: str = "docstore",
    schema_name: str = "public",
    perform_setup: bool = True,
    debug: bool = False,
    use_jsonb: bool = False,
) -> "PostgresDocumentStore":
    """Load a PostgresDocumentStore from a Postgres URI."""
    postgres_kvstore = PostgresKVStore.from_uri(
        uri=uri,
        table_name=table_name,
        schema_name=schema_name,
        perform_setup=perform_setup,
        debug=debug,
        use_jsonb=use_jsonb,
    )
    return cls(postgres_kvstore, namespace)

```
  
---|---  
###  from_params `classmethod` #
```
from_params(host: Optional[str] = None, port: Optional[str] = None, database: Optional[str] = None, user: Optional[str] = None, password: Optional[str] = None, namespace: Optional[str] = None, table_name: str = 'docstore', schema_name: str = 'public', perform_setup: bool = True, debug: bool = False, use_jsonb: bool = False) -> PostgresDocumentStore

```

Load a PostgresDocumentStore from a Postgres host and port.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-postgres/llama_index/storage/docstore/postgres/base.py`

| ```
@classmethod
def from_params(
    cls,
    host: Optional[str] = None,
    port: Optional[str] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    namespace: Optional[str] = None,
    table_name: str = "docstore",
    schema_name: str = "public",
    perform_setup: bool = True,
    debug: bool = False,
    use_jsonb: bool = False,
) -> "PostgresDocumentStore":
    """Load a PostgresDocumentStore from a Postgres host and port."""
    postgres_kvstore = PostgresKVStore.from_params(
        host=host,
        port=port,
        database=database,
        user=user,
        password=password,
        table_name=table_name,
        schema_name=schema_name,
        perform_setup=perform_setup,
        debug=debug,
        use_jsonb=use_jsonb,
    )
    return cls(postgres_kvstore, namespace)

```
  
---|---
