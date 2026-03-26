# NL SQL table
##  NLSQLTableQueryEngine #
Bases: `BaseSQLTableQueryEngine`
Natural language SQL Table query engine.
Read NLStructStoreQueryEngine's docstring for more info on NL SQL.
NOTE: Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
Source code in `llama-index-core/llama_index/core/indices/struct_store/sql_query.py`

| ```
class NLSQLTableQueryEngine(BaseSQLTableQueryEngine):
    """
    Natural language SQL Table query engine.

    Read NLStructStoreQueryEngine's docstring for more info on NL SQL.

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
        markdown_response: bool = False,
        response_synthesis_prompt: Optional[BasePromptTemplate] = None,
        refine_synthesis_prompt: Optional[BasePromptTemplate] = None,
        tables: Optional[Union[List[str], List[Table]]] = None,
        table_retriever: Optional[ObjectRetriever[SQLTableSchema]] = None,
        rows_retrievers: Optional[dict[str, BaseRetriever]] = None,
        cols_retrievers: Optional[dict[str, dict[str, BaseRetriever]]] = None,
        context_str_prefix: Optional[str] = None,
        embed_model: Optional[BaseEmbedding] = None,
        sql_only: bool = False,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        # self._tables = tables
        self._sql_retriever = NLSQLRetriever(
            sql_database,
            llm=llm,
            text_to_sql_prompt=text_to_sql_prompt,
            context_query_kwargs=context_query_kwargs,
            tables=tables,
            table_retriever=table_retriever,
            rows_retrievers=rows_retrievers,
            cols_retrievers=cols_retrievers,
            context_str_prefix=context_str_prefix,
            embed_model=embed_model,
            sql_only=sql_only,
            callback_manager=callback_manager,
            verbose=verbose,
        )
        super().__init__(
            synthesize_response=synthesize_response,
            markdown_response=markdown_response,
            response_synthesis_prompt=response_synthesis_prompt,
            refine_synthesis_prompt=refine_synthesis_prompt,
            llm=llm,
            callback_manager=callback_manager,
            verbose=verbose,
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
