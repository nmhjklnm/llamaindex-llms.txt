# Neptune
##  NeptuneAnalyticsGraphStore #
Bases: `NeptuneBaseGraphStore`
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/analytics.py`

| ```
class NeptuneAnalyticsGraphStore(NeptuneBaseGraphStore):
    def __init__(
        self,
        graph_identifier: str,
        client: Any = None,
        credentials_profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        node_label: str = "Entity",
        **kwargs: Any,
    ) -> None:
        """Create a new Neptune Analytics graph wrapper instance."""
        self.node_label = node_label
        self._client = create_neptune_analytics_client(
            graph_identifier, client, credentials_profile_name, region_name
        )
        self.graph_identifier = graph_identifier

    def query(self, query: str, params: dict = {}) -> Dict[str, Any]:
        """Query Neptune Analytics graph."""
        try:
            logger.debug(f"query() query: {query} parameters: {json.dumps(params)}")
            resp = self.client.execute_query(
                graphIdentifier=self.graph_identifier,
                queryString=query,
                parameters=params,
                language="OPEN_CYPHER",
            )
            return json.loads(resp["payload"].read().decode("UTF-8"))["results"]
        except Exception as e:
            raise NeptuneQueryException(
                {
                    "message": "An error occurred while executing the query.",
                    "details": str(e),
                    "query": query,
                    "parameters": str(params),
                }
            )

    def _get_summary(self) -> Dict:
        try:
            response = self.client.get_graph_summary(
                graphIdentifier=self.graph_identifier, mode="detailed"
            )
        except Exception as e:
            raise NeptuneQueryException(
                {
                    "message": ("Summary API error occurred on Neptune Analytics"),
                    "details": str(e),
                }
            )

        try:
            summary = response["graphSummary"]
        except Exception:
            raise NeptuneQueryException(
                {
                    "message": "Summary API did not return a valid response.",
                    "details": response.content.decode(),
                }
            )
        else:
            return summary

```
  
---|---  
###  query #
```
query(query: str, params: dict = {}) -> Dict[str, Any]

```

Query Neptune Analytics graph.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/analytics.py`

| ```
def query(self, query: str, params: dict = {}) -> Dict[str, Any]:
    """Query Neptune Analytics graph."""
    try:
        logger.debug(f"query() query: {query} parameters: {json.dumps(params)}")
        resp = self.client.execute_query(
            graphIdentifier=self.graph_identifier,
            queryString=query,
            parameters=params,
            language="OPEN_CYPHER",
        )
        return json.loads(resp["payload"].read().decode("UTF-8"))["results"]
    except Exception as e:
        raise NeptuneQueryException(
            {
                "message": "An error occurred while executing the query.",
                "details": str(e),
                "query": query,
                "parameters": str(params),
            }
        )

```
  
---|---  
##  NeptuneAnalyticsPropertyGraphStore #
Bases: `NeptuneBasePropertyGraph`
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/analytics_property_graph.py`

| ```
class NeptuneAnalyticsPropertyGraphStore(NeptuneBasePropertyGraph):
    supports_vector_queries: bool = True

    def __init__(
        self,
        graph_identifier: str,
        client: Any = None,
        credentials_profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Create a new Neptune Analytics graph wrapper instance."""
        self._client = create_neptune_analytics_client(
            graph_identifier, client, credentials_profile_name, region_name
        )
        self.graph_identifier = graph_identifier

    def structured_query(self, query: str, param_map: Dict[str, Any] = None) -> Any:
        """
        Run the structured query.

        Args:
            query (str): The query to run
            param_map (Dict[str, Any] | None, optional): A dictionary of query parameters. Defaults to None.

        Raises:
            NeptuneQueryException: An exception from Neptune with details

        Returns:
            Any: The results of the query

        """
        param_map = param_map or {}

        try:
            logger.debug(
                f"structured_query() query: {query} parameters: {json.dumps(param_map)}"
            )
            resp = self.client.execute_query(
                graphIdentifier=self.graph_identifier,
                queryString=query,
                parameters=param_map,
                language="OPEN_CYPHER",
            )
            return json.loads(resp["payload"].read().decode("UTF-8"))["results"]
        except Exception as e:
            raise NeptuneQueryException(
                {
                    "message": "An error occurred while executing the query.",
                    "details": str(e),
                    "query": query,
                    "parameters": str(param_map),
                }
            )

    def vector_query(self, query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[Any]]:
        """
        Query the graph store with a vector store query.

        Returns:
            (nodes, score): The nodes and their associated score

        """
        conditions = None
        if query.filters:
            conditions = [
                f"e.{filter.key} {filter.operator.value} {filter.value}"
                for filter in query.filters.filters
            ]
        filters = (
            f" {query.filters.condition.value} ".join(conditions).replace("==", "=")
            if conditions is not None
            else "1 = 1"
        )

        data = self.structured_query(
            f"""MATCH (e:`{BASE_ENTITY_LABEL}`)
            WHERE ({filters})
            CALL neptune.algo.vectors.get(e)
            YIELD embedding
            WHERE embedding IS NOT NULL
            CALL neptune.algo.vectors.topKByNode(e)
            YIELD node, score
            WITH e, score
            ORDER BY score DESC LIMIT $limit
            RETURN e.id AS name,
                [l in labels(e) WHERE l <> '{BASE_ENTITY_LABEL}' | l][0] AS type,
                e{{.* , embedding: Null, name: Null, id: Null}} AS properties,
                score""",
            param_map={
                "embedding": query.query_embedding,
                "dimension": len(query.query_embedding),
                "limit": query.similarity_top_k,
            },
        )
        data = data if data else []

        nodes = []
        scores = []
        for record in data:
            node = EntityNode(
                name=record["name"],
                label=record["type"],
                properties=remove_empty_values(record["properties"]),
            )
            nodes.append(node)
            scores.append(record["score"])

        return (nodes, scores)

    def upsert_nodes(self, nodes: List[LabelledNode]) -> None:
        """
        Upsert the nodes in the graph.

        Args:
            nodes (List[LabelledNode]): The list of nodes to upsert

        """
        # Lists to hold separated types
        entity_dicts: List[dict] = []
        chunk_dicts: List[dict] = []

        # Sort by type
        for item in nodes:
            if isinstance(item, EntityNode):
                entity_dicts.append({**item.dict(), "id": item.id})
            elif isinstance(item, ChunkNode):
                chunk_dicts.append({**item.dict(), "id": item.id})
            else:
                # Log that we do not support these types of nodes
                # Or raise an error?
                pass

        if chunk_dicts:
            for d in chunk_dicts:
                self.structured_query(
                    """
                    WITH $data AS row
                    MERGE (c:Chunk {id: row.id})
                    SET c.text = row.text
                    SET c += removeKeyFromMap(row.properties, '')
                    WITH c, row.embedding as e
                    WHERE e IS NOT NULL
                    CALL neptune.algo.vectors.upsert(c, e)
                    RETURN count(*)
                    """,
                    param_map={"data": d},
                )

        if entity_dicts:
            for d in entity_dicts:
                self.structured_query(
                    f"""
                    WITH $data AS row
                    MERGE (e:`{BASE_NODE_LABEL}` {{id: row.id}})
                    SET e += removeKeyFromMap(row.properties, '')
                    SET e.name = row.name, e:`{BASE_ENTITY_LABEL}`
                    SET e:`{d["label"]}`
                    WITH e, row
                    WHERE removeKeyFromMap(row.properties, '').triplet_source_id IS NOT NULL
                    MERGE (c:Chunk {{id: removeKeyFromMap(row.properties, '').triplet_source_id}})
                    MERGE (e)<-[:MENTIONS]-(c)
                    WITH e, row.embedding as em
                    CALL neptune.algo.vectors.upsert(e, em)
                    RETURN count(*) as count
                    """,
                    param_map={"data": d},
                )

    def _get_summary(self) -> Dict:
        """
        Get the Summary of the graph topology.

        Returns:
            Dict: The graph summary

        """
        try:
            response = self.client.get_graph_summary(
                graphIdentifier=self.graph_identifier, mode="detailed"
            )
        except Exception as e:
            raise NeptuneQueryException(
                {
                    "message": ("Summary API error occurred on Neptune Analytics"),
                    "details": str(e),
                }
            )

        try:
            summary = response["graphSummary"]
        except Exception:
            raise NeptuneQueryException(
                {
                    "message": "Summary API did not return a valid response.",
                    "details": response.content.decode(),
                }
            )
        else:
            return summary

```
  
---|---  
###  structured_query #
```
structured_query(query: str, param_map: Dict[str, Any] = None) -> Any

```

Run the structured query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The query to run |  _required_  
`param_map` |  `Dict[str, Any] | None` |  A dictionary of query parameters. Defaults to None. |  `None`  
Raises:
Type | Description  
---|---  
`NeptuneQueryException` |  An exception from Neptune with details  
Returns:
Name | Type | Description  
---|---|---  
`Any` |  `Any` |  The results of the query  
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/analytics_property_graph.py`

| ```
def structured_query(self, query: str, param_map: Dict[str, Any] = None) -> Any:
    """
    Run the structured query.

    Args:
        query (str): The query to run
        param_map (Dict[str, Any] | None, optional): A dictionary of query parameters. Defaults to None.

    Raises:
        NeptuneQueryException: An exception from Neptune with details

    Returns:
        Any: The results of the query

    """
    param_map = param_map or {}

    try:
        logger.debug(
            f"structured_query() query: {query} parameters: {json.dumps(param_map)}"
        )
        resp = self.client.execute_query(
            graphIdentifier=self.graph_identifier,
            queryString=query,
            parameters=param_map,
            language="OPEN_CYPHER",
        )
        return json.loads(resp["payload"].read().decode("UTF-8"))["results"]
    except Exception as e:
        raise NeptuneQueryException(
            {
                "message": "An error occurred while executing the query.",
                "details": str(e),
                "query": query,
                "parameters": str(param_map),
            }
        )

```
  
---|---  
###  vector_query #
```
vector_query(query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[Any]]

```

Query the graph store with a vector store query.
Returns:
Type | Description  
---|---  
`(nodes, score)` |  The nodes and their associated score  
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/analytics_property_graph.py`

| ```
def vector_query(self, query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[Any]]:
    """
    Query the graph store with a vector store query.

    Returns:
        (nodes, score): The nodes and their associated score

    """
    conditions = None
    if query.filters:
        conditions = [
            f"e.{filter.key} {filter.operator.value} {filter.value}"
            for filter in query.filters.filters
        ]
    filters = (
        f" {query.filters.condition.value} ".join(conditions).replace("==", "=")
        if conditions is not None
        else "1 = 1"
    )

    data = self.structured_query(
        f"""MATCH (e:`{BASE_ENTITY_LABEL}`)
        WHERE ({filters})
        CALL neptune.algo.vectors.get(e)
        YIELD embedding
        WHERE embedding IS NOT NULL
        CALL neptune.algo.vectors.topKByNode(e)
        YIELD node, score
        WITH e, score
        ORDER BY score DESC LIMIT $limit
        RETURN e.id AS name,
            [l in labels(e) WHERE l <> '{BASE_ENTITY_LABEL}' | l][0] AS type,
            e{{.* , embedding: Null, name: Null, id: Null}} AS properties,
            score""",
        param_map={
            "embedding": query.query_embedding,
            "dimension": len(query.query_embedding),
            "limit": query.similarity_top_k,
        },
    )
    data = data if data else []

    nodes = []
    scores = []
    for record in data:
        node = EntityNode(
            name=record["name"],
            label=record["type"],
            properties=remove_empty_values(record["properties"]),
        )
        nodes.append(node)
        scores.append(record["score"])

    return (nodes, scores)

```
  
---|---  
###  upsert_nodes #
```
upsert_nodes(nodes: List[LabelledNode]) -> None

```

Upsert the nodes in the graph.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[LabelledNode]` |  The list of nodes to upsert |  _required_  
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/analytics_property_graph.py`

| ```
def upsert_nodes(self, nodes: List[LabelledNode]) -> None:
    """
    Upsert the nodes in the graph.

    Args:
        nodes (List[LabelledNode]): The list of nodes to upsert

    """
    # Lists to hold separated types
    entity_dicts: List[dict] = []
    chunk_dicts: List[dict] = []

    # Sort by type
    for item in nodes:
        if isinstance(item, EntityNode):
            entity_dicts.append({**item.dict(), "id": item.id})
        elif isinstance(item, ChunkNode):
            chunk_dicts.append({**item.dict(), "id": item.id})
        else:
            # Log that we do not support these types of nodes
            # Or raise an error?
            pass

    if chunk_dicts:
        for d in chunk_dicts:
            self.structured_query(
                """
                WITH $data AS row
                MERGE (c:Chunk {id: row.id})
                SET c.text = row.text
                SET c += removeKeyFromMap(row.properties, '')
                WITH c, row.embedding as e
                WHERE e IS NOT NULL
                CALL neptune.algo.vectors.upsert(c, e)
                RETURN count(*)
                """,
                param_map={"data": d},
            )

    if entity_dicts:
        for d in entity_dicts:
            self.structured_query(
                f"""
                WITH $data AS row
                MERGE (e:`{BASE_NODE_LABEL}` {{id: row.id}})
                SET e += removeKeyFromMap(row.properties, '')
                SET e.name = row.name, e:`{BASE_ENTITY_LABEL}`
                SET e:`{d["label"]}`
                WITH e, row
                WHERE removeKeyFromMap(row.properties, '').triplet_source_id IS NOT NULL
                MERGE (c:Chunk {{id: removeKeyFromMap(row.properties, '').triplet_source_id}})
                MERGE (e)<-[:MENTIONS]-(c)
                WITH e, row.embedding as em
                CALL neptune.algo.vectors.upsert(e, em)
                RETURN count(*) as count
                """,
                param_map={"data": d},
            )

```
  
---|---  
##  NeptuneDatabaseGraphStore #
Bases: `NeptuneBaseGraphStore`
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/database.py`

| ```
class NeptuneDatabaseGraphStore(NeptuneBaseGraphStore):
    def __init__(
        self,
        host: str,
        port: int = 8182,
        use_https: bool = True,
        client: Any = None,
        credentials_profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        sign: bool = True,
        node_label: str = "Entity",
        **kwargs: Any,
    ) -> None:
        """Create a new Neptune Database graph wrapper instance."""
        self.node_label = node_label
        self._client = create_neptune_database_client(
            host, port, client, credentials_profile_name, region_name, sign, use_https
        )

    def query(self, query: str, params: dict = {}) -> Dict[str, Any]:
        """Query Neptune database."""
        try:
            logger.debug(f"query() query: {query} parameters: {json.dumps(params)}")
            return self.client.execute_open_cypher_query(
                openCypherQuery=query, parameters=json.dumps(params)
            )["results"]
        except Exception as e:
            raise NeptuneQueryException(
                {
                    "message": "An error occurred while executing the query.",
                    "details": str(e),
                    "query": query,
                    "parameters": str(params),
                }
            )

    def _get_summary(self) -> Dict:
        try:
            response = self.client.get_propertygraph_summary()
        except Exception as e:
            raise NeptuneQueryException(
                {
                    "message": (
                        "Summary API is not available for this instance of Neptune,"
                        "ensure the engine version is >=1.2.1.0"
                    ),
                    "details": str(e),
                }
            )

        try:
            summary = response["payload"]["graphSummary"]
        except Exception:
            raise NeptuneQueryException(
                {
                    "message": "Summary API did not return a valid response.",
                    "details": response.content.decode(),
                }
            )
        else:
            return summary

```
  
---|---  
###  query #
```
query(query: str, params: dict = {}) -> Dict[str, Any]

```

Query Neptune database.
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/database.py`

| ```
def query(self, query: str, params: dict = {}) -> Dict[str, Any]:
    """Query Neptune database."""
    try:
        logger.debug(f"query() query: {query} parameters: {json.dumps(params)}")
        return self.client.execute_open_cypher_query(
            openCypherQuery=query, parameters=json.dumps(params)
        )["results"]
    except Exception as e:
        raise NeptuneQueryException(
            {
                "message": "An error occurred while executing the query.",
                "details": str(e),
                "query": query,
                "parameters": str(params),
            }
        )

```
  
---|---  
##  NeptuneDatabasePropertyGraphStore #
Bases: `NeptuneBasePropertyGraph`
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/database_property_graph.py`

| ```
class NeptuneDatabasePropertyGraphStore(NeptuneBasePropertyGraph):
    supports_vector_queries: bool = False

    def __init__(
        self,
        host: str,
        port: int = 8182,
        client: Any = None,
        credentials_profile_name: Optional[str] = None,
        region_name: Optional[str] = None,
        sign: bool = True,
        use_https: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Init.

        Args:
            host (str): The host endpoint
            port (int, optional): The port. Defaults to 8182.
            client (Any, optional): If provided, this is the client that will be used. Defaults to None.
            credentials_profile_name (Optional[str], optional): If provided this is the credentials profile that will be used. Defaults to None.
            region_name (Optional[str], optional): The region to use. Defaults to None.
            sign (bool, optional): True will SigV4 sign all requests, False will not. Defaults to True.
            use_https (bool, optional): True to use https, False to use http. Defaults to True.

        """
        self._client = create_neptune_database_client(
            host, port, client, credentials_profile_name, region_name, sign, use_https
        )

    def structured_query(self, query: str, param_map: Dict[str, Any] = None) -> Any:
        """
        Run the structured query.

        Args:
            query (str): The query to run
            param_map (Dict[str, Any] | None, optional): A dictionary of query parameters. Defaults to None.

        Raises:
            NeptuneQueryException: An exception from Neptune with details

        Returns:
            Any: The results of the query

        """
        param_map = param_map or {}

        try:
            logger.debug(
                f"structured_query() query: {query} parameters: {json.dumps(param_map)}"
            )

            return self.client.execute_open_cypher_query(
                openCypherQuery=query, parameters=json.dumps(param_map)
            )["results"]
        except Exception as e:
            raise NeptuneQueryException(
                {
                    "message": "An error occurred while executing the query.",
                    "details": str(e),
                    "query": query,
                    "parameters": str(param_map),
                }
            )

    def vector_query(self, query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[Any]]:
        """
        NOT SUPPORTED.

        Args:
            query (VectorStoreQuery): _description_

        Raises:
            NotImplementedError: _description_

        Returns:
            Tuple[List[LabelledNode] | List[float]]: _description_

        """
        raise NotImplementedError

    def upsert_nodes(self, nodes: List[LabelledNode]) -> None:
        """
        Upsert the nodes in the graph.

        Args:
            nodes (List[LabelledNode]): The list of nodes to upsert

        """
        # Lists to hold separated types
        entity_dicts: List[dict] = []
        chunk_dicts: List[dict] = []

        # Sort by type
        for item in nodes:
            if isinstance(item, EntityNode):
                entity_dicts.append({**item.dict(), "id": item.id})
            elif isinstance(item, ChunkNode):
                chunk_dicts.append({**item.dict(), "id": item.id})
            else:
                # Log that we do not support these types of nodes
                # Or raise an error?
                pass

        if chunk_dicts:
            for d in chunk_dicts:
                self.structured_query(
                    """
                    WITH $data AS row
                    MERGE (c:Chunk {id: row.id})
                    SET c.text = row.text
                    SET c += removeKeyFromMap(row.properties, '')
                    RETURN count(*)
                    """,
                    param_map={"data": d},
                )

        if entity_dicts:
            for d in entity_dicts:
                self.structured_query(
                    f"""
                    WITH $data AS row
                    MERGE (e:`{BASE_NODE_LABEL}` {{id: row.id}})
                    SET e += removeKeyFromMap(row.properties, '')
                    SET e.name = row.name, e:`{BASE_ENTITY_LABEL}`
                    SET e:`{d["label"]}`
                    WITH e, row
                    WHERE removeKeyFromMap(row.properties, '').triplet_source_id IS NOT NULL
                    MERGE (c:Chunk {{id: removeKeyFromMap(row.properties, '').triplet_source_id}})
                    MERGE (e)<-[:MENTIONS]-(c)
                    RETURN count(*) as count
                    """,
                    param_map={"data": d},
                )

    def _get_summary(self) -> Dict:
        """
        Get the Summary of the graph schema.

        Returns:
            Dict: The graph summary

        """
        try:
            response = self.client.get_propertygraph_summary()
        except Exception as e:
            raise NeptuneQueryException(
                {
                    "message": (
                        "Summary API is not available for this instance of Neptune,"
                        "ensure the engine version is >=1.2.1.0"
                    ),
                    "details": str(e),
                }
            )

        try:
            summary = response["payload"]["graphSummary"]
        except Exception:
            raise NeptuneQueryException(
                {
                    "message": "Summary API did not return a valid response.",
                    "details": response.content.decode(),
                }
            )
        else:
            return summary

```
  
---|---  
###  structured_query #
```
structured_query(query: str, param_map: Dict[str, Any] = None) -> Any

```

Run the structured query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The query to run |  _required_  
`param_map` |  `Dict[str, Any] | None` |  A dictionary of query parameters. Defaults to None. |  `None`  
Raises:
Type | Description  
---|---  
`NeptuneQueryException` |  An exception from Neptune with details  
Returns:
Name | Type | Description  
---|---|---  
`Any` |  `Any` |  The results of the query  
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/database_property_graph.py`

| ```
def structured_query(self, query: str, param_map: Dict[str, Any] = None) -> Any:
    """
    Run the structured query.

    Args:
        query (str): The query to run
        param_map (Dict[str, Any] | None, optional): A dictionary of query parameters. Defaults to None.

    Raises:
        NeptuneQueryException: An exception from Neptune with details

    Returns:
        Any: The results of the query

    """
    param_map = param_map or {}

    try:
        logger.debug(
            f"structured_query() query: {query} parameters: {json.dumps(param_map)}"
        )

        return self.client.execute_open_cypher_query(
            openCypherQuery=query, parameters=json.dumps(param_map)
        )["results"]
    except Exception as e:
        raise NeptuneQueryException(
            {
                "message": "An error occurred while executing the query.",
                "details": str(e),
                "query": query,
                "parameters": str(param_map),
            }
        )

```
  
---|---  
###  vector_query #
```
vector_query(query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[Any]]

```

NOT SUPPORTED.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `VectorStoreQuery` |  _description_ |  _required_  
Raises:
Type | Description  
---|---  
`NotImplementedError` |  _description_  
Returns:
Type | Description  
---|---  
`Tuple[List[Any]]` |  Tuple[List[LabelledNode] | List[float]]: _description_  
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/database_property_graph.py`

| ```
def vector_query(self, query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[Any]]:
    """
    NOT SUPPORTED.

    Args:
        query (VectorStoreQuery): _description_

    Raises:
        NotImplementedError: _description_

    Returns:
        Tuple[List[LabelledNode] | List[float]]: _description_

    """
    raise NotImplementedError

```
  
---|---  
###  upsert_nodes #
```
upsert_nodes(nodes: List[LabelledNode]) -> None

```

Upsert the nodes in the graph.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[LabelledNode]` |  The list of nodes to upsert |  _required_  
Source code in `llama-index-integrations/graph_stores/llama-index-graph-stores-neptune/llama_index/graph_stores/neptune/database_property_graph.py`

| ```
def upsert_nodes(self, nodes: List[LabelledNode]) -> None:
    """
    Upsert the nodes in the graph.

    Args:
        nodes (List[LabelledNode]): The list of nodes to upsert

    """
    # Lists to hold separated types
    entity_dicts: List[dict] = []
    chunk_dicts: List[dict] = []

    # Sort by type
    for item in nodes:
        if isinstance(item, EntityNode):
            entity_dicts.append({**item.dict(), "id": item.id})
        elif isinstance(item, ChunkNode):
            chunk_dicts.append({**item.dict(), "id": item.id})
        else:
            # Log that we do not support these types of nodes
            # Or raise an error?
            pass

    if chunk_dicts:
        for d in chunk_dicts:
            self.structured_query(
                """
                WITH $data AS row
                MERGE (c:Chunk {id: row.id})
                SET c.text = row.text
                SET c += removeKeyFromMap(row.properties, '')
                RETURN count(*)
                """,
                param_map={"data": d},
            )

    if entity_dicts:
        for d in entity_dicts:
            self.structured_query(
                f"""
                WITH $data AS row
                MERGE (e:`{BASE_NODE_LABEL}` {{id: row.id}})
                SET e += removeKeyFromMap(row.properties, '')
                SET e.name = row.name, e:`{BASE_ENTITY_LABEL}`
                SET e:`{d["label"]}`
                WITH e, row
                WHERE removeKeyFromMap(row.properties, '').triplet_source_id IS NOT NULL
                MERGE (c:Chunk {{id: removeKeyFromMap(row.properties, '').triplet_source_id}})
                MERGE (e)<-[:MENTIONS]-(c)
                RETURN count(*) as count
                """,
                param_map={"data": d},
            )

```
  
---|---
