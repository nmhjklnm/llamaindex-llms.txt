# Duckdb retriever
##  DuckDBRetriever #
Bases: `BaseRetriever`
Source code in `llama-index-integrations/retrievers/llama-index-retrievers-duckdb-retriever/llama_index/retrievers/duckdb_retriever/base.py`

| ```
class DuckDBRetriever(BaseRetriever):
    def __init__(
        self,
        database_name: str = ":memory:",
        table_name: str = "documents",
        text_search_config: dict = {
            "stemmer": "english",
            "stopwords": "english",
            "ignore": r"(\\.|[^a-z])+",
            "strip_accents": True,
            "lower": True,
            "overwrite": True,
        },
        persist_dir: str = "./storage",
        node_id_column: str = "node_id",
        text_column: str = "text",
        # TODO: Add more options for FTS index creation
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = False,
    ) -> None:
        self._similarity_top_k = similarity_top_k
        self._callback_manager = callback_manager
        self._verbose = verbose
        self._table_name = table_name
        self._node_id_column = node_id_column
        self._text_column = text_column

        # TODO: Check if the vector store already has data

        # Create an FTS index on the 'text' column if it doesn't already exist
        if database_name == ":memory:":
            self._database_path = ":memory:"
        else:
            self._database_path = os.path.join(persist_dir, database_name)

        strip_accents = 1 if text_search_config["strip_accents"] else 0
        lower = 1 if text_search_config["lower"] else 0
        overwrite = 1 if text_search_config["overwrite"] else 0
        ignore = text_search_config["ignore"]

        sql = f"""
            PRAGMA create_fts_index({self._table_name}, {self._node_id_column}, {self._text_column},
                            stemmer = '{text_search_config["stemmer"]}',
                            stopwords = '{text_search_config["stopwords"]}', ignore = '{ignore}',
                            strip_accents = {strip_accents}, lower = {lower}, overwrite = {overwrite})
                        """
        with DuckDBLocalContext(self._database_path) as conn:
            conn.execute(sql)

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        if self._verbose:
            logger.info(f"Searching for: {query_bundle.query_str}")
        query = query_bundle.query_str
        sql = f"""
                SELECT
                    fts_main_{self._table_name}.match_bm25({self._node_id_column}, ?) AS score,
                    {self._node_id_column}, {self._text_column}
                FROM {self._table_name}
                WHERE score IS NOT NULL
                ORDER BY score DESC
                LIMIT {self._similarity_top_k};
            """
        with DuckDBLocalContext(self._database_path) as conn:
            query_result = conn.execute(sql, [query]).fetchall()
        # Convert query result to NodeWithScore objects
        retrieve_nodes = []
        for row in query_result:
            score, node_id, text = row
            node = TextNode(id=node_id, text=text)
            retrieve_nodes.append(NodeWithScore(node=node, score=float(score)))

        return retrieve_nodes

```
  
---|---
