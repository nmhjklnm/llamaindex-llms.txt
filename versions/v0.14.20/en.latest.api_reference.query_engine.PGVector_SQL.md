# PGVector SQL
##  PGVectorSQLQueryEngine #
Bases: `BaseSQLTableQueryEngine`
PGvector SQL query engine.
A modified version of the normal text-to-SQL query engine because we can infer embedding vectors in the sql query.
NOTE: this is a beta feature
NOTE: Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
Source code in `llama-index-core/llama_index/core/indices/struct_store/sql_query.py`

| ```
class PGVectorSQLQueryEngine(BaseSQLTableQueryEngine):
    """
    PGvector SQL query engine.

    A modified version of the normal text-to-SQL query engine because
    we can infer embedding vectors in the sql query.

    NOTE: this is a beta feature

    NOTE: Any Text-to-SQL application should be aware that executing
    arbitrary SQL queries can be a security risk. It is recommended to
    take precautions as needed, such as using restricted roles, read-only
    databases, sandboxing, etc.

    """

    def __init__(
        self,
        sql_database: SQLDatabase,
        llm: Optional[LLM] = None,
        text_to_sql_prompt: Optional[BasePromptTemplate] = None,
        context_query_kwargs: Optional[dict] = None,
        synthesize_response: bool = True,
        response_synthesis_prompt: Optional[BasePromptTemplate] = None,
        refine_synthesis_prompt: Optional[BasePromptTemplate] = None,
        tables: Optional[Union[List[str], List[Table]]] = None,
        context_str_prefix: Optional[str] = None,
        sql_only: bool = False,
        callback_manager: Optional[CallbackManager] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        text_to_sql_prompt = text_to_sql_prompt or DEFAULT_TEXT_TO_SQL_PGVECTOR_PROMPT
        self._sql_retriever = NLSQLRetriever(
            sql_database,
            llm=llm,
            text_to_sql_prompt=text_to_sql_prompt,
            context_query_kwargs=context_query_kwargs,
            tables=tables,
            sql_parser_mode=SQLParserMode.PGVECTOR,
            context_str_prefix=context_str_prefix,
            sql_only=sql_only,
            callback_manager=callback_manager,
        )
        super().__init__(
            synthesize_response=synthesize_response,
            response_synthesis_prompt=response_synthesis_prompt,
            refine_synthesis_prompt=refine_synthesis_prompt,
            llm=llm,
            callback_manager=callback_manager,
            **kwargs,
        )

    @property
    def sql_retriever(self) -> NLSQLRetriever:
        """Get SQL retriever."""
        return self._sql_retriever

```
  
---|---  
###  sql_retriever `property` #
```
sql_retriever: NLSQLRetriever

```

Get SQL retriever.
