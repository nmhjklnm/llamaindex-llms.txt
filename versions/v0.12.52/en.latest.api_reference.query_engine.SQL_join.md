# SQL join
##  SQLJoinQueryEngine #
Bases: `BaseQueryEngine`
SQL Join Query Engine.
This query engine can "Join" a SQL database results with another query engine. It can decide it needs to query the SQL database or the other query engine. If it decides to query the SQL database, it will first query the SQL database, whether to augment information with retrieved results from the other query engine.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`sql_query_tool` |  `QueryEngineTool` |  Query engine tool for SQL database. other_query_tool (QueryEngineTool): Other query engine tool. |  _required_  
`selector` |  `Optional[Union[LLMSingleSelector, PydanticSingleSelector]]` |  Selector to use. |  `None`  
`sql_join_synthesis_prompt` |  `Optional[BasePromptTemplate]` |  PromptTemplate to use for SQL join synthesis. |  `None`  
`sql_augment_query_transform` |  `Optional[SQLAugmentQueryTransform]` |  Query transform to use for SQL augmentation. |  `None`  
`use_sql_join_synthesis` |  `bool` |  Whether to use SQL join synthesis. |  `True`  
`callback_manager` |  `Optional[CallbackManager]` |  Callback manager to use. |  `None`  
`verbose` |  `bool` |  Whether to print intermediate results. |  `True`  
Source code in `llama-index-core/llama_index/core/query_engine/sql_join_query_engine.py`

| ```
class SQLJoinQueryEngine(BaseQueryEngine):
    """
    SQL Join Query Engine.

    This query engine can "Join" a SQL database results
    with another query engine.
    It can decide it needs to query the SQL database or the other query engine.
    If it decides to query the SQL database, it will first query the SQL database,
    whether to augment information with retrieved results from the other query engine.

    Args:
        sql_query_tool (QueryEngineTool): Query engine tool for SQL database.
            other_query_tool (QueryEngineTool): Other query engine tool.
        selector (Optional[Union[LLMSingleSelector, PydanticSingleSelector]]):
            Selector to use.
        sql_join_synthesis_prompt (Optional[BasePromptTemplate]):
            PromptTemplate to use for SQL join synthesis.
        sql_augment_query_transform (Optional[SQLAugmentQueryTransform]): Query
            transform to use for SQL augmentation.
        use_sql_join_synthesis (bool): Whether to use SQL join synthesis.
        callback_manager (Optional[CallbackManager]): Callback manager to use.
        verbose (bool): Whether to print intermediate results.

    """

    def __init__(
        self,
        sql_query_tool: QueryEngineTool,
        other_query_tool: QueryEngineTool,
        selector: Optional[Union[LLMSingleSelector, PydanticSingleSelector]] = None,
        llm: Optional[LLM] = None,
        sql_join_synthesis_prompt: Optional[BasePromptTemplate] = None,
        sql_augment_query_transform: Optional[SQLAugmentQueryTransform] = None,
        use_sql_join_synthesis: bool = True,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = True,
        streaming: bool = False,
    ) -> None:
        """Initialize params."""
        super().__init__(callback_manager=callback_manager)
        # validate that the query engines are of the right type
        if not isinstance(
            sql_query_tool.query_engine,
            (BaseSQLTableQueryEngine, NLSQLTableQueryEngine),
        ):
            raise ValueError(
                "sql_query_tool.query_engine must be an instance of "
                "BaseSQLTableQueryEngine or NLSQLTableQueryEngine"
            )
        self._sql_query_tool = sql_query_tool
        self._other_query_tool = other_query_tool

        self._llm = llm or Settings.llm

        self._selector = selector or get_selector_from_llm(self._llm, is_multi=False)  # type: ignore
        assert isinstance(self._selector, (LLMSingleSelector, PydanticSingleSelector))

        self._sql_join_synthesis_prompt = (
            sql_join_synthesis_prompt or DEFAULT_SQL_JOIN_SYNTHESIS_PROMPT
        )
        self._sql_augment_query_transform = (
            sql_augment_query_transform or SQLAugmentQueryTransform(llm=self._llm)
        )
        self._use_sql_join_synthesis = use_sql_join_synthesis
        self._verbose = verbose
        self._streaming = streaming

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {
            "selector": self._selector,
            "sql_augment_query_transform": self._sql_augment_query_transform,
        }

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {"sql_join_synthesis_prompt": self._sql_join_synthesis_prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "sql_join_synthesis_prompt" in prompts:
            self._sql_join_synthesis_prompt = prompts["sql_join_synthesis_prompt"]

    def _query_sql_other(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Query SQL database + other query engine in sequence."""
        # first query SQL database
        sql_response = self._sql_query_tool.query_engine.query(query_bundle)
        if not self._use_sql_join_synthesis:
            return sql_response

        sql_query = (
            sql_response.metadata["sql_query"] if sql_response.metadata else None
        )
        if self._verbose:
            print_text(f"SQL query: {sql_query}\n", color="yellow")
            print_text(f"SQL response: {sql_response}\n", color="yellow")

        # given SQL db, transform query into new query
        new_query = self._sql_augment_query_transform(
            query_bundle.query_str,
            metadata={
                "sql_query": _format_sql_query(sql_query),
                "sql_query_response": str(sql_response),
            },
        )

        if self._verbose:
            print_text(
                f"Transformed query given SQL response: {new_query.query_str}\n",
                color="blue",
            )
        logger.info(f"> Transformed query given SQL response: {new_query.query_str}")
        if self._sql_augment_query_transform.check_stop(new_query):
            return sql_response

        other_response = self._other_query_tool.query_engine.query(new_query)
        if self._verbose:
            print_text(f"query engine response: {other_response}\n", color="pink")
        logger.info(f"> query engine response: {other_response}")

        if self._streaming:
            response_gen = self._llm.stream(
                self._sql_join_synthesis_prompt,
                query_str=query_bundle.query_str,
                sql_query_str=sql_query,
                sql_response_str=str(sql_response),
                query_engine_query_str=new_query.query_str,
                query_engine_response_str=str(other_response),
            )

            response_metadata = {
                **(sql_response.metadata or {}),
                **(other_response.metadata or {}),
            }
            source_nodes = other_response.source_nodes
            return StreamingResponse(
                response_gen,
                metadata=response_metadata,
                source_nodes=source_nodes,
            )
        else:
            response_str = self._llm.predict(
                self._sql_join_synthesis_prompt,
                query_str=query_bundle.query_str,
                sql_query_str=sql_query,
                sql_response_str=str(sql_response),
                query_engine_query_str=new_query.query_str,
                query_engine_response_str=str(other_response),
            )

            response_metadata = {
                **(sql_response.metadata or {}),
                **(other_response.metadata or {}),
            }
            source_nodes = other_response.source_nodes
            return Response(
                response_str,
                metadata=response_metadata,
                source_nodes=source_nodes,
            )

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Query and get response."""
        # TODO: see if this can be consolidated with logic in RouterQueryEngine
        metadatas = [self._sql_query_tool.metadata, self._other_query_tool.metadata]
        result = self._selector.select(metadatas, query_bundle)
        # pick sql query
        if result.ind == 0:
            if self._verbose:
                print_text(f"Querying SQL database: {result.reason}\n", color="blue")
            logger.info(f"> Querying SQL database: {result.reason}")
            return self._query_sql_other(query_bundle)
        elif result.ind == 1:
            if self._verbose:
                print_text(
                    f"Querying other query engine: {result.reason}\n", color="blue"
                )
            logger.info(f"> Querying other query engine: {result.reason}")
            return self._other_query_tool.query_engine.query(query_bundle)
        else:
            raise ValueError(f"Invalid result.ind: {result.ind}")

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        # TODO: make async
        return self._query(query_bundle)

```
  
---|---  
##  SQLAutoVectorQueryEngine #
Bases: `SQLJoinQueryEngine`
SQL + Vector Index Auto Retriever Query Engine.
This query engine can query both a SQL database as well as a vector database. It will first decide whether it needs to query the SQL database or vector store. If it decides to query the SQL database, it will also decide whether to augment information with retrieved results from the vector store. We use the VectorIndexAutoRetriever to retrieve results.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`sql_query_tool` |  `QueryEngineTool` |  Query engine tool for SQL database. |  _required_  
`vector_query_tool` |  `QueryEngineTool` |  Query engine tool for vector database. |  _required_  
`selector` |  `Optional[Union[LLMSingleSelector, PydanticSingleSelector]]` |  Selector to use. |  `None`  
`sql_vector_synthesis_prompt` |  `Optional[BasePromptTemplate]` |  Prompt to use for SQL vector synthesis. |  `None`  
`sql_augment_query_transform` |  `Optional[SQLAugmentQueryTransform]` |  Query transform to use for SQL augmentation. |  `None`  
`use_sql_vector_synthesis` |  `bool` |  Whether to use SQL vector synthesis. |  `True`  
`callback_manager` |  `Optional[CallbackManager]` |  Callback manager to use. |  `None`  
`verbose` |  `bool` |  Whether to print intermediate results. |  `True`  
Source code in `llama-index-core/llama_index/core/query_engine/sql_vector_query_engine.py`

| ```
class SQLAutoVectorQueryEngine(SQLJoinQueryEngine):
    """
    SQL + Vector Index Auto Retriever Query Engine.

    This query engine can query both a SQL database
    as well as a vector database. It will first decide
    whether it needs to query the SQL database or vector store.
    If it decides to query the SQL database, it will also decide
    whether to augment information with retrieved results from the vector store.
    We use the VectorIndexAutoRetriever to retrieve results.

    Args:
        sql_query_tool (QueryEngineTool): Query engine tool for SQL database.
        vector_query_tool (QueryEngineTool): Query engine tool for vector database.
        selector (Optional[Union[LLMSingleSelector, PydanticSingleSelector]]):
            Selector to use.
        sql_vector_synthesis_prompt (Optional[BasePromptTemplate]):
            Prompt to use for SQL vector synthesis.
        sql_augment_query_transform (Optional[SQLAugmentQueryTransform]): Query
            transform to use for SQL augmentation.
        use_sql_vector_synthesis (bool): Whether to use SQL vector synthesis.
        callback_manager (Optional[CallbackManager]): Callback manager to use.
        verbose (bool): Whether to print intermediate results.

    """

    def __init__(
        self,
        sql_query_tool: QueryEngineTool,
        vector_query_tool: QueryEngineTool,
        selector: Optional[Union[LLMSingleSelector, PydanticSingleSelector]] = None,
        llm: Optional[LLM] = None,
        sql_vector_synthesis_prompt: Optional[BasePromptTemplate] = None,
        sql_augment_query_transform: Optional[SQLAugmentQueryTransform] = None,
        use_sql_vector_synthesis: bool = True,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = True,
    ) -> None:
        """Initialize params."""
        # validate that the query engines are of the right type
        if not isinstance(
            sql_query_tool.query_engine,
            (BaseSQLTableQueryEngine, NLSQLTableQueryEngine),
        ):
            raise ValueError(
                "sql_query_tool.query_engine must be an instance of "
                "BaseSQLTableQueryEngine or NLSQLTableQueryEngine"
            )
        if not isinstance(vector_query_tool.query_engine, RetrieverQueryEngine):
            raise ValueError(
                "vector_query_tool.query_engine must be an instance of "
                "RetrieverQueryEngine"
            )
        if not isinstance(
            vector_query_tool.query_engine.retriever, VectorIndexAutoRetriever
        ):
            raise ValueError(
                "vector_query_tool.query_engine.retriever must be an instance "
                "of VectorIndexAutoRetriever"
            )

        sql_vector_synthesis_prompt = (
            sql_vector_synthesis_prompt or DEFAULT_SQL_VECTOR_SYNTHESIS_PROMPT
        )
        super().__init__(
            sql_query_tool,
            vector_query_tool,
            selector=selector,
            llm=llm,
            sql_join_synthesis_prompt=sql_vector_synthesis_prompt,
            sql_augment_query_transform=sql_augment_query_transform,
            use_sql_join_synthesis=use_sql_vector_synthesis,
            callback_manager=callback_manager,
            verbose=verbose,
        )

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {
            "selector": self._selector,
            "sql_augment_query_transform": self._sql_augment_query_transform,
        }

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {"sql_join_synthesis_prompt": self._sql_join_synthesis_prompt}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "sql_join_synthesis_prompt" in prompts:
            self._sql_join_synthesis_prompt = prompts["sql_join_synthesis_prompt"]

    @classmethod
    def from_sql_and_vector_query_engines(
        cls,
        sql_query_engine: Union[BaseSQLTableQueryEngine, NLSQLTableQueryEngine],
        sql_tool_name: str,
        sql_tool_description: str,
        vector_auto_retriever: RetrieverQueryEngine,
        vector_tool_name: str,
        vector_tool_description: str,
        selector: Optional[Union[LLMSingleSelector, PydanticSingleSelector]] = None,
        **kwargs: Any,
    ) -> "SQLAutoVectorQueryEngine":
        """
        From SQL and vector query engines.

        Args:
            sql_query_engine (BaseSQLTableQueryEngine): SQL query engine.
            vector_query_engine (VectorIndexAutoRetriever): Vector retriever.
            selector (Optional[Union[LLMSingleSelector, PydanticSingleSelector]]):
                Selector to use.

        """
        sql_query_tool = QueryEngineTool.from_defaults(
            sql_query_engine, name=sql_tool_name, description=sql_tool_description
        )
        vector_query_tool = QueryEngineTool.from_defaults(
            vector_auto_retriever,
            name=vector_tool_name,
            description=vector_tool_description,
        )
        return cls(sql_query_tool, vector_query_tool, selector, **kwargs)

```
  
---|---  
###  from_sql_and_vector_query_engines `classmethod` #
```
from_sql_and_vector_query_engines(sql_query_engine: Union[BaseSQLTableQueryEngine, NLSQLTableQueryEngine], sql_tool_name: str, sql_tool_description: str, vector_auto_retriever: RetrieverQueryEngine, vector_tool_name: str, vector_tool_description: str, selector: Optional[Union[LLMSingleSelector, PydanticSingleSelector]] = None, **kwargs: Any) -> SQLAutoVectorQueryEngine

```

From SQL and vector query engines.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`sql_query_engine` |  `BaseSQLTableQueryEngine` |  SQL query engine. |  _required_  
`vector_query_engine` |  `VectorIndexAutoRetriever` |  Vector retriever. |  _required_  
`selector` |  `Optional[Union[LLMSingleSelector, PydanticSingleSelector]]` |  Selector to use. |  `None`  
Source code in `llama-index-core/llama_index/core/query_engine/sql_vector_query_engine.py`

| ```
@classmethod
def from_sql_and_vector_query_engines(
    cls,
    sql_query_engine: Union[BaseSQLTableQueryEngine, NLSQLTableQueryEngine],
    sql_tool_name: str,
    sql_tool_description: str,
    vector_auto_retriever: RetrieverQueryEngine,
    vector_tool_name: str,
    vector_tool_description: str,
    selector: Optional[Union[LLMSingleSelector, PydanticSingleSelector]] = None,
    **kwargs: Any,
) -> "SQLAutoVectorQueryEngine":
    """
    From SQL and vector query engines.

    Args:
        sql_query_engine (BaseSQLTableQueryEngine): SQL query engine.
        vector_query_engine (VectorIndexAutoRetriever): Vector retriever.
        selector (Optional[Union[LLMSingleSelector, PydanticSingleSelector]]):
            Selector to use.

    """
    sql_query_tool = QueryEngineTool.from_defaults(
        sql_query_engine, name=sql_tool_name, description=sql_tool_description
    )
    vector_query_tool = QueryEngineTool.from_defaults(
        vector_auto_retriever,
        name=vector_tool_name,
        description=vector_tool_description,
    )
    return cls(sql_query_tool, vector_query_tool, selector, **kwargs)

```
  
---|---
