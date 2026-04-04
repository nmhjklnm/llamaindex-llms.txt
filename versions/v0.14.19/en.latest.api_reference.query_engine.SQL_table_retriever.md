# SQL table retriever
##  SQLTableRetrieverQueryEngine #
Bases: `BaseSQLTableQueryEngine`
SQL Table retriever query engine.
Source code in `llama-index-core/llama_index/core/indices/struct_store/sql_query.py`

| ```
class SQLTableRetrieverQueryEngine(BaseSQLTableQueryEngine):
    """SQL Table retriever query engine."""

    def __init__(
        self,
        sql_database: SQLDatabase,
        table_retriever: ObjectRetriever[SQLTableSchema],
        rows_retrievers: Optional[dict[str, BaseRetriever]] = None,
        cols_retrievers: Optional[dict[str, dict[str, BaseRetriever]]] = None,
        llm: Optional[LLM] = None,
        text_to_sql_prompt: Optional[BasePromptTemplate] = None,
        context_query_kwargs: Optional[dict] = None,
        synthesize_response: bool = True,
        response_synthesis_prompt: Optional[BasePromptTemplate] = None,
        refine_synthesis_prompt: Optional[BasePromptTemplate] = None,
        context_str_prefix: Optional[str] = None,
        sql_only: bool = False,
        callback_manager: Optional[CallbackManager] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        self._sql_retriever = NLSQLRetriever(
            sql_database,
            llm=llm,
            text_to_sql_prompt=text_to_sql_prompt,
            context_query_kwargs=context_query_kwargs,
            table_retriever=table_retriever,
            rows_retrievers=rows_retrievers,
            cols_retrievers=cols_retrievers,
            context_str_prefix=context_str_prefix,
            sql_only=sql_only,
            callback_manager=callback_manager,
            verbose=kwargs.get("verbose", False),
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
