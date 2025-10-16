# Notion
Notion tool spec.
##  NotionToolSpec #
Bases: `BaseToolSpec`
Notion tool spec.
Currently a simple wrapper around the data loader. TODO: add more methods to the Notion spec.
Source code in `llama-index-integrations/tools/llama-index-tools-notion/llama_index/tools/notion/base.py`

| ```
class NotionToolSpec(BaseToolSpec):
    """
    Notion tool spec.

    Currently a simple wrapper around the data loader.
    TODO: add more methods to the Notion spec.

    """

    spec_functions = ["load_data", "search_data"]

    def __init__(self, integration_token: Optional[str] = None) -> None:
        """Initialize with parameters."""
        self.reader = NotionPageReader(integration_token=integration_token)

    def get_fn_schema_from_fn_name(
        self, fn_name: str, spec_functions: Optional[List[SPEC_FUNCTION_TYPE]] = None
    ) -> Optional[Type[BaseModel]]:
        """Return map from function name."""
        if fn_name == "load_data":
            return NotionLoadDataSchema
        elif fn_name == "search_data":
            return NotionSearchDataSchema
        else:
            raise ValueError(f"Invalid function name: {fn_name}")

    def load_data(
        self,
        page_ids: Optional[List[str]] = None,
        database_ids: Optional[List[str]] = None,
    ) -> str:
        """
        Loads content from a set of page ids or database ids.

        Don't use this endpoint if you don't know the page ids or database ids.

        """
        page_ids = page_ids or []
        docs = self.reader.load_data(page_ids=page_ids, database_ids=database_ids)
        return "\n".join([doc.get_content() for doc in docs])

    def search_data(
        self,
        query: str,
        direction: Optional[str] = None,
        timestamp: Optional[str] = None,
        value: Optional[str] = None,
        property: Optional[str] = None,
        page_size: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Search a list of relevant pages.

        Contains metadata for each page (but not the page content).
        params:
           query: the title of the page or database to search for, which is fuzzy matched.
        """
        payload: Dict[str, Any] = {
            "query": query,
            "page_size": page_size,
        }
        if direction is not None or timestamp is not None:
            payload["sort"] = {}
            if direction is not None:
                payload["sort"]["direction"] = direction
            if timestamp is not None:
                payload["sort"]["timestamp"] = timestamp

        if value is not None or property is not None:
            payload["filter"] = {}
            if value is not None:
                payload["filter"]["value"] = value
            if property is not None:
                payload["filter"]["property"] = property

        response = requests.post(SEARCH_URL, json=payload, headers=self.reader.headers)
        response_json = response.json()
        return response_json["results"]

```
  
---|---  
###  get_fn_schema_from_fn_name #
```
get_fn_schema_from_fn_name(fn_name: str, spec_functions: Optional[List[SPEC_FUNCTION_TYPE]] = None) -> Optional[Type[BaseModel]]

```

Return map from function name.
Source code in `llama-index-integrations/tools/llama-index-tools-notion/llama_index/tools/notion/base.py`

| ```
def get_fn_schema_from_fn_name(
    self, fn_name: str, spec_functions: Optional[List[SPEC_FUNCTION_TYPE]] = None
) -> Optional[Type[BaseModel]]:
    """Return map from function name."""
    if fn_name == "load_data":
        return NotionLoadDataSchema
    elif fn_name == "search_data":
        return NotionSearchDataSchema
    else:
        raise ValueError(f"Invalid function name: {fn_name}")

```
  
---|---  
###  load_data #
```
load_data(page_ids: Optional[List[str]] = None, database_ids: Optional[List[str]] = None) -> str

```

Loads content from a set of page ids or database ids.
Don't use this endpoint if you don't know the page ids or database ids.
Source code in `llama-index-integrations/tools/llama-index-tools-notion/llama_index/tools/notion/base.py`

| ```
def load_data(
    self,
    page_ids: Optional[List[str]] = None,
    database_ids: Optional[List[str]] = None,
) -> str:
    """
    Loads content from a set of page ids or database ids.

    Don't use this endpoint if you don't know the page ids or database ids.

    """
    page_ids = page_ids or []
    docs = self.reader.load_data(page_ids=page_ids, database_ids=database_ids)
    return "\n".join([doc.get_content() for doc in docs])

```
  
---|---  
###  search_data #
```
search_data(query: str, direction: Optional[str] = None, timestamp: Optional[str] = None, value: Optional[str] = None, property: Optional[str] = None, page_size: int = 100) -> List[Dict[str, Any]]

```

Search a list of relevant pages.
Contains metadata for each page (but not the page content). params: query: the title of the page or database to search for, which is fuzzy matched.
Source code in `llama-index-integrations/tools/llama-index-tools-notion/llama_index/tools/notion/base.py`

| ```
def search_data(
    self,
    query: str,
    direction: Optional[str] = None,
    timestamp: Optional[str] = None,
    value: Optional[str] = None,
    property: Optional[str] = None,
    page_size: int = 100,
) -> List[Dict[str, Any]]:
    """
    Search a list of relevant pages.

    Contains metadata for each page (but not the page content).
    params:
       query: the title of the page or database to search for, which is fuzzy matched.
    """
    payload: Dict[str, Any] = {
        "query": query,
        "page_size": page_size,
    }
    if direction is not None or timestamp is not None:
        payload["sort"] = {}
        if direction is not None:
            payload["sort"]["direction"] = direction
        if timestamp is not None:
            payload["sort"]["timestamp"] = timestamp

    if value is not None or property is not None:
        payload["filter"] = {}
        if value is not None:
            payload["filter"]["value"] = value
        if property is not None:
            payload["filter"]["property"] = property

    response = requests.post(SEARCH_URL, json=payload, headers=self.reader.headers)
    response_json = response.json()
    return response_json["results"]

```
  
---|---
