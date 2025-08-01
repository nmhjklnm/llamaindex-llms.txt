# Graphql
##  GraphQLToolSpec #
Bases: `BaseToolSpec`
Requests Tool.
Source code in `llama-index-integrations/tools/llama-index-tools-graphql/llama_index/tools/graphql/base.py`

| ```
class GraphQLToolSpec(BaseToolSpec):
    """Requests Tool."""

    spec_functions = ["graphql_request"]

    def __init__(self, url: str, headers: Optional[dict] = {}):
        self.headers = headers
        self.url = url

    def graphql_request(self, query: str, variables: str, operation_name: str):
        r"""
        Use this tool to make a GraphQL query against the server.

        Args:
            query (str): The GraphQL query to execute
            variables (str): The variable values for the query
            operation_name (str): The name for the query

        example input:
            "query":"query Ships {\n  ships {\n    id\n    model\n    name\n    type\n    status\n  }\n}",
            "variables":{},
            "operation_name":"Ships"

        """
        res = requests.post(
            self.url,
            headers=self.headers,
            json={
                "query": query,
                "variables": variables,
                "operationName": operation_name,
            },
        )
        return res.text

```
  
---|---  
###  graphql_request #
```
graphql_request(query: str, variables: str, operation_name: str)

```

Use this tool to make a GraphQL query against the server.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The GraphQL query to execute |  _required_  
`variables` |  `str` |  The variable values for the query |  _required_  
`operation_name` |  `str` |  The name for the query |  _required_  
example input
"query":"query Ships {\n ships {\n id\n model\n name\n type\n status\n }\n}", "variables":{}, "operation_name":"Ships"
Source code in `llama-index-integrations/tools/llama-index-tools-graphql/llama_index/tools/graphql/base.py`

| ```
def graphql_request(self, query: str, variables: str, operation_name: str):
    r"""
    Use this tool to make a GraphQL query against the server.

    Args:
        query (str): The GraphQL query to execute
        variables (str): The variable values for the query
        operation_name (str): The name for the query

    example input:
        "query":"query Ships {\n  ships {\n    id\n    model\n    name\n    type\n    status\n  }\n}",
        "variables":{},
        "operation_name":"Ships"

    """
    res = requests.post(
        self.url,
        headers=self.headers,
        json={
            "query": query,
            "variables": variables,
            "operationName": operation_name,
        },
    )
    return res.text

```
  
---|---
