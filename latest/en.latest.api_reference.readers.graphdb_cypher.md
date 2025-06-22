# Graphdb cypher
##  GraphDBCypherReader #
Bases: `BaseReader`
Graph database Cypher reader.
Combines all Cypher query results into the Document type used by LlamaIndex.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`uri` |  `str` |  Graph Database URI |  _required_  
`username` |  `str` |  Username |  _required_  
`password` |  `str` |  Password |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-graphdb-cypher/llama_index/readers/graphdb_cypher/base.py`

| ```
class GraphDBCypherReader(BaseReader):
    """
    Graph database Cypher reader.

    Combines all Cypher query results into the Document type used by LlamaIndex.

    Args:
        uri (str): Graph Database URI
        username (str): Username
        password (str): Password

    """

    def __init__(self, uri: str, username: str, password: str, database: str) -> None:
        """Initialize with parameters."""
        try:
            from neo4j import GraphDatabase, basic_auth

        except ImportError:
            raise ImportError(
                "`neo4j` package not found, please run `pip install neo4j`"
            )
        if uri:
            if uri is None:
                raise ValueError("`uri` must be provided.")
            self.client = GraphDatabase.driver(
                uri=uri, auth=basic_auth(username, password)
            )
            self.database = database

    def load_data(
        self, query: str, parameters: Optional[Dict] = None
    ) -> List[Document]:
        """
        Run the Cypher with optional parameters and turn results into documents.

        Args:
            query (str): Graph Cypher query string.
            parameters (Optional[Dict]): optional query parameters.

        Returns:
            List[Document]: A list of documents.

        """
        if parameters is None:
            parameters = {}

        records, summary, keys = self.client.execute_query(
            query, parameters, database_=self.database
        )

        return [Document(text=yaml.dump(entry.data())) for entry in records]

```
  
---|---  
###  load_data #
```
load_data(query: str, parameters: Optional[Dict] = None) -> List[Document]

```

Run the Cypher with optional parameters and turn results into documents.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Graph Cypher query string. |  _required_  
`parameters` |  `Optional[Dict]` |  optional query parameters. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-graphdb-cypher/llama_index/readers/graphdb_cypher/base.py`

| ```
def load_data(
    self, query: str, parameters: Optional[Dict] = None
) -> List[Document]:
    """
    Run the Cypher with optional parameters and turn results into documents.

    Args:
        query (str): Graph Cypher query string.
        parameters (Optional[Dict]): optional query parameters.

    Returns:
        List[Document]: A list of documents.

    """
    if parameters is None:
        parameters = {}

    records, summary, keys = self.client.execute_query(
        query, parameters, database_=self.database
    )

    return [Document(text=yaml.dump(entry.data())) for entry in records]

```
  
---|---
