# Wordlift
##  WordLiftLoader #
Bases: `BaseReader`
A reader class for fetching and transforming data from WordLift GraphQL API.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`endpoint` |  `str` |  The API endpoint URL. |  _required_  
`headers` |  `dict` |  The request headers. |  _required_  
`query` |  `str` |  The GraphQL query. |  _required_  
`fields` |  `str` |  The fields to extract from the API response. |  _required_  
`configure_options` |  `dict` |  Additional configuration options. |  _required_  
`page` |  `int` |  The page number. |  _required_  
`rows` |  `int` |  The number of rows per page. |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`endpoint` |  `str` |  The API endpoint URL.  
`headers` |  `dict` |  The request headers.  
`query` |  `str` |  The GraphQL query.  
`fields` |  `str` |  The fields to extract from the API response.  
`configure_options` |  `dict` |  Additional configuration options.  
`page` |  `int` |  The page number.  
`rows` |  `int` |  The number of rows per page.  
Source code in `llama-index-integrations/readers/llama-index-readers-wordlift/llama_index/readers/wordlift/base.py`

| ```
class WordLiftLoader(BaseReader):
    """
    A reader class for fetching and transforming data from WordLift GraphQL API.

    Args:
        endpoint (str): The API endpoint URL.
        headers (dict): The request headers.
        query (str): The GraphQL query.
        fields (str): The fields to extract from the API response.
        configure_options (dict): Additional configuration options.
        page (int): The page number.
        rows (int): The number of rows per page.

    Attributes:
        endpoint (str): The API endpoint URL.
        headers (dict): The request headers.
        query (str): The GraphQL query.
        fields (str): The fields to extract from the API response.
        configure_options (dict): Additional configuration options.
        page (int): The page number.
        rows (int): The number of rows per page.

    """

    def __init__(self, endpoint, headers, query, fields, configure_options) -> None:
        self.endpoint = endpoint
        self.headers = headers
        self.query = query
        self.fields = fields
        self.configure_options = configure_options

    def fetch_data(self) -> dict:
        """
        Fetches data from the WordLift GraphQL API.

        Returns:
            dict: The API response data.

        Raises:
            APIConnectionError: If there is an error connecting to the API.

        """
        try:
            query = self.alter_query()
            response = requests.post(
                self.endpoint, json={"query": query}, headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            if ERRORS_KEY in data:
                raise APICallError(data[ERRORS_KEY])
            return data
        except requests.exceptions.RequestException as e:
            logging.error("Error connecting to the API:", exc_info=True)
            raise APICallError("Error connecting to the API") from e

    def transform_data(self, data: dict) -> List[Document]:
        """
        Transforms the fetched data into a list of Document objects.

        Args:
            data (dict): The API response data.

        Returns:
            List[Document]: The list of transformed documents.

        Raises:
            DataTransformError: If there is an error transforming the data.

        """
        try:
            data = data[DATA_KEY][self.fields]
            documents = []
            text_fields = self.configure_options.get("text_fields", [])
            metadata_fields = self.configure_options.get("metadata_fields", [])

            for item in data:
                if not all(key in item for key in text_fields):
                    logging.warning(
                        f"Skipping document due to missing text fields: {item}"
                    )
                    continue
                row = {}
                for key, value in item.items():
                    if key in text_fields or key in metadata_fields:
                        row[key] = value
                    else:
                        row[key] = clean_value(value)

                text_parts = [
                    get_separated_value(row, field.split("."))
                    for field in text_fields
                    if get_separated_value(row, field.split(".")) is not None
                ]

                text_parts = flatten_list(text_parts)
                text = " ".join(text_parts)

                extra_info = {}
                for field in metadata_fields:
                    field_keys = field.split(".")
                    value = get_separated_value(row, field_keys)
                    if value is None:
                        logging.warning(f"Using default value for {field}")
                        value = "n.a"
                    if isinstance(value, list) and len(value) != 0:
                        value = value[0]
                    if is_url(value) and is_valid_html(value):
                        value = value.replace("\n", "")
                        extra_info[field] = value
                    else:
                        cleaned_value = clean_value(value)
                        cleaned_value = cleaned_value.replace("\n", "")
                        extra_info[field] = cleaned_value
                text = text.replace("\n", "")
                plain_text = re.sub("<.*?>", "", text)
                document = Document(text=plain_text, extra_info=extra_info)
                documents.append(document)

            return documents
        except Exception as e:
            logging.error("Error transforming data:", exc_info=True)
            raise DataTransformError("Error transforming data") from e

    def load_data(self) -> List[Document]:
        """
        Loads the data by fetching and transforming it.

        Returns:
            List[Document]: The list of loaded documents.

        """
        try:
            data = self.fetch_data()
            return self.transform_data(data)
        except (APICallError, DataTransformError):
            logging.error("Error loading data:", exc_info=True)
            raise

    def alter_query(self):
        """
        Alters the GraphQL query by adding pagination arguments.

        Returns:
            str: The altered GraphQL query with pagination arguments.

        """
        from graphql import parse, print_ast
        from graphql.language.ast import ArgumentNode, IntValueNode, NameNode

        DEFAULT_PAGE = 0
        DEFAULT_ROWS = 500

        query = self.query
        page = DEFAULT_PAGE
        rows = DEFAULT_ROWS

        ast = parse(query)

        field_node = ast.definitions[0].selection_set.selections[0]

        if not any(arg.name.value == "page" for arg in field_node.arguments):
            page_argument = ArgumentNode(
                name=NameNode(value="page"), value=IntValueNode(value=page)
            )
            rows_argument = ArgumentNode(
                name=NameNode(value="rows"), value=IntValueNode(value=rows)
            )
            field_node.arguments = (*field_node.arguments, page_argument, rows_argument)
        return print_ast(ast)

```
  
---|---  
###  fetch_data #
```
fetch_data() -> dict

```

Fetches data from the WordLift GraphQL API.
Returns:
Name | Type | Description  
---|---|---  
`dict` |  `dict` |  The API response data.  
Raises:
Type | Description  
---|---  
`APIConnectionError` |  If there is an error connecting to the API.  
Source code in `llama-index-integrations/readers/llama-index-readers-wordlift/llama_index/readers/wordlift/base.py`

| ```
def fetch_data(self) -> dict:
    """
    Fetches data from the WordLift GraphQL API.

    Returns:
        dict: The API response data.

    Raises:
        APIConnectionError: If there is an error connecting to the API.

    """
    try:
        query = self.alter_query()
        response = requests.post(
            self.endpoint, json={"query": query}, headers=self.headers
        )
        response.raise_for_status()
        data = response.json()
        if ERRORS_KEY in data:
            raise APICallError(data[ERRORS_KEY])
        return data
    except requests.exceptions.RequestException as e:
        logging.error("Error connecting to the API:", exc_info=True)
        raise APICallError("Error connecting to the API") from e

```
  
---|---  
###  transform_data #
```
transform_data(data: dict) -> List[Document]

```

Transforms the fetched data into a list of Document objects.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`data` |  `dict` |  The API response data. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: The list of transformed documents.  
Raises:
Type | Description  
---|---  
`DataTransformError` |  If there is an error transforming the data.  
Source code in `llama-index-integrations/readers/llama-index-readers-wordlift/llama_index/readers/wordlift/base.py`

| ```
def transform_data(self, data: dict) -> List[Document]:
    """
    Transforms the fetched data into a list of Document objects.

    Args:
        data (dict): The API response data.

    Returns:
        List[Document]: The list of transformed documents.

    Raises:
        DataTransformError: If there is an error transforming the data.

    """
    try:
        data = data[DATA_KEY][self.fields]
        documents = []
        text_fields = self.configure_options.get("text_fields", [])
        metadata_fields = self.configure_options.get("metadata_fields", [])

        for item in data:
            if not all(key in item for key in text_fields):
                logging.warning(
                    f"Skipping document due to missing text fields: {item}"
                )
                continue
            row = {}
            for key, value in item.items():
                if key in text_fields or key in metadata_fields:
                    row[key] = value
                else:
                    row[key] = clean_value(value)

            text_parts = [
                get_separated_value(row, field.split("."))
                for field in text_fields
                if get_separated_value(row, field.split(".")) is not None
            ]

            text_parts = flatten_list(text_parts)
            text = " ".join(text_parts)

            extra_info = {}
            for field in metadata_fields:
                field_keys = field.split(".")
                value = get_separated_value(row, field_keys)
                if value is None:
                    logging.warning(f"Using default value for {field}")
                    value = "n.a"
                if isinstance(value, list) and len(value) != 0:
                    value = value[0]
                if is_url(value) and is_valid_html(value):
                    value = value.replace("\n", "")
                    extra_info[field] = value
                else:
                    cleaned_value = clean_value(value)
                    cleaned_value = cleaned_value.replace("\n", "")
                    extra_info[field] = cleaned_value
            text = text.replace("\n", "")
            plain_text = re.sub("<.*?>", "", text)
            document = Document(text=plain_text, extra_info=extra_info)
            documents.append(document)

        return documents
    except Exception as e:
        logging.error("Error transforming data:", exc_info=True)
        raise DataTransformError("Error transforming data") from e

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Loads the data by fetching and transforming it.
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: The list of loaded documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-wordlift/llama_index/readers/wordlift/base.py`

| ```
def load_data(self) -> List[Document]:
    """
    Loads the data by fetching and transforming it.

    Returns:
        List[Document]: The list of loaded documents.

    """
    try:
        data = self.fetch_data()
        return self.transform_data(data)
    except (APICallError, DataTransformError):
        logging.error("Error loading data:", exc_info=True)
        raise

```
  
---|---  
###  alter_query #
```
alter_query()

```

Alters the GraphQL query by adding pagination arguments.
Returns:
Name | Type | Description  
---|---|---  
`str` |  |  The altered GraphQL query with pagination arguments.  
Source code in `llama-index-integrations/readers/llama-index-readers-wordlift/llama_index/readers/wordlift/base.py`

| ```
def alter_query(self):
    """
    Alters the GraphQL query by adding pagination arguments.

    Returns:
        str: The altered GraphQL query with pagination arguments.

    """
    from graphql import parse, print_ast
    from graphql.language.ast import ArgumentNode, IntValueNode, NameNode

    DEFAULT_PAGE = 0
    DEFAULT_ROWS = 500

    query = self.query
    page = DEFAULT_PAGE
    rows = DEFAULT_ROWS

    ast = parse(query)

    field_node = ast.definitions[0].selection_set.selections[0]

    if not any(arg.name.value == "page" for arg in field_node.arguments):
        page_argument = ArgumentNode(
            name=NameNode(value="page"), value=IntValueNode(value=page)
        )
        rows_argument = ArgumentNode(
            name=NameNode(value="rows"), value=IntValueNode(value=rows)
        )
        field_node.arguments = (*field_node.arguments, page_argument, rows_argument)
    return print_ast(ast)

```
  
---|---
