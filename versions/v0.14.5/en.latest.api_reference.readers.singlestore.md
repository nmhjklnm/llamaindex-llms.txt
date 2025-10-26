# Singlestore
##  SingleStoreReader #
Bases: `BaseReader`
SingleStore reader.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`scheme` |  `str` |  Database Scheme. |  _required_  
`host` |  `str` |  Database Host. |  _required_  
`port` |  `str` |  Database Port. |  _required_  
`user` |  `str` |  Database User. |  _required_  
`password` |  `str` |  Database Password. |  _required_  
`dbname` |  `str` |  Database Name. |  _required_  
`table_name` |  `str` |  Table Name. |  _required_  
`content_field` |  `str` |  Content Field. |  `'text'`  
`vector_field` |  `str` |  Vector Field. |  `'embedding'`  
Source code in `llama-index-integrations/readers/llama-index-readers-singlestore/llama_index/readers/singlestore/base.py`

| ```
class SingleStoreReader(BaseReader):
    """
    SingleStore reader.

    Args:
        scheme (str): Database Scheme.
        host (str): Database Host.
        port (str): Database Port.
        user (str): Database User.
        password (str): Database Password.
        dbname (str): Database Name.
        table_name (str): Table Name.
        content_field (str): Content Field.
        vector_field (str): Vector Field.

    """

    def __init__(
        self,
        scheme: str,
        host: str,
        port: str,
        user: str,
        password: str,
        dbname: str,
        table_name: str,
        content_field: str = "text",
        vector_field: str = "embedding",
    ):
        """Initialize with parameters."""
        self.scheme = scheme
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        self.table_name = table_name
        self.content_field = content_field
        self.vector_field = vector_field

        try:
            import pymysql

            pymysql.install_as_MySQLdb()
        except ImportError:
            pass

        self.DatabaseReader = DatabaseReader
        self.reader = self.DatabaseReader(
            scheme=self.scheme,
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            dbname=self.dbname,
        )

    def load_data(self, search_embedding: str, top_k: int = 5) -> List[Document]:
        """
        Load data from SingleStore.

        Args:
            search_embedding (str): The embedding to search.
            top_k (int): Number of results to return.

        Returns:
            List[Document]: A list of documents.

        """
        query = f"""
        SELECT {self.content_field}, DOT_PRODUCT_F64({self.vector_field}, JSON_ARRAY_PACK_F64(\'{search_embedding}\')) AS score
        FROM {self.table_name}
        ORDER BY score
        DESC LIMIT {top_k}
        """

        return self.reader.load_data(query=query)

```
  
---|---  
###  load_data #
```
load_data(search_embedding: str, top_k: int = 5) -> List[Document]

```

Load data from SingleStore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`search_embedding` |  `str` |  The embedding to search. |  _required_  
`top_k` |  `int` |  Number of results to return. |  `5`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: A list of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-singlestore/llama_index/readers/singlestore/base.py`

| ```
def load_data(self, search_embedding: str, top_k: int = 5) -> List[Document]:
    """
    Load data from SingleStore.

    Args:
        search_embedding (str): The embedding to search.
        top_k (int): Number of results to return.

    Returns:
        List[Document]: A list of documents.

    """
    query = f"""
    SELECT {self.content_field}, DOT_PRODUCT_F64({self.vector_field}, JSON_ARRAY_PACK_F64(\'{search_embedding}\')) AS score
    FROM {self.table_name}
    ORDER BY score
    DESC LIMIT {top_k}
    """

    return self.reader.load_data(query=query)

```
  
---|---
