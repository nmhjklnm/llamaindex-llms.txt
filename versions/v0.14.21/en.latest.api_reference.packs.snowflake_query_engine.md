# Snowflake query engine
##  SnowflakeQueryEnginePack #
Bases: `BaseLlamaPack`
Snowflake query engine pack. It uses snowflake-sqlalchemy to connect to Snowflake, then calls NLSQLTableQueryEngine to query data.
Source code in `llama-index-packs/llama-index-packs-snowflake-query-engine/llama_index/packs/snowflake_query_engine/base.py`

| ```
class SnowflakeQueryEnginePack(BaseLlamaPack):
    """
    Snowflake query engine pack.
    It uses snowflake-sqlalchemy to connect to Snowflake, then calls
    NLSQLTableQueryEngine to query data.
    """

    def __init__(
        self,
        user: str,
        password: str,
        account: str,
        database: str,
        schema: str,
        warehouse: str,
        role: str,
        tables: List[str],
        **kwargs: Any,
    ) -> None:
        """Init params."""
        # workaround for https://github.com/snowflakedb/snowflake-sqlalchemy/issues/380.
        try:
            snowflake_sqlalchemy_20_monkey_patches()
        except Exception:
            raise ImportError("Please run `pip install snowflake-sqlalchemy`")

        if not os.environ.get("OPENAI_API_KEY", None):
            raise ValueError("OpenAI API Token is missing or blank.")

        snowflake_uri = f"snowflake://{user}:{password}@{account}/{database}/{schema}?warehouse={warehouse}&role={role}"

        engine = create_engine(snowflake_uri)

        self._sql_database = SQLDatabase(engine)
        self.tables = tables

        self.query_engine = NLSQLTableQueryEngine(
            sql_database=self._sql_database, tables=self.tables
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "sql_database": self._sql_database,
            "query_engine": self.query_engine,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.query_engine.query(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-snowflake-query-engine/llama_index/packs/snowflake_query_engine/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "sql_database": self._sql_database,
        "query_engine": self.query_engine,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-snowflake-query-engine/llama_index/packs/snowflake_query_engine/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---
