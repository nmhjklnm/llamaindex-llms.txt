# Pydantic
Output parsers.
##  PydanticOutputParser #
Bases: `BaseOutputParser`, `Generic[Model]`
Pydantic Output Parser.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`output_cls` |  `BaseModel` |  Pydantic output class. |  _required_  
Source code in `llama-index-core/llama_index/core/output_parsers/pydantic.py`

| ```
class PydanticOutputParser(BaseOutputParser, Generic[Model]):
    """
    Pydantic Output Parser.

    Args:
        output_cls (BaseModel): Pydantic output class.

    """

    def __init__(
        self,
        output_cls: Type[Model],
        excluded_schema_keys_from_format: Optional[List] = None,
        pydantic_format_tmpl: str = PYDANTIC_FORMAT_TMPL,
    ) -> None:
        """Init params."""
        self._output_cls = output_cls
        self._excluded_schema_keys_from_format = excluded_schema_keys_from_format or []
        self._pydantic_format_tmpl = pydantic_format_tmpl

    @property
    def output_cls(self) -> Type[Model]:
        return self._output_cls

    @property
    def format_string(self) -> str:
        """Format string."""
        return self.get_format_string(escape_json=True)

    def get_format_string(self, escape_json: bool = True) -> str:
        """Format string."""
        schema_dict = self._output_cls.model_json_schema()
        for key in self._excluded_schema_keys_from_format:
            del schema_dict[key]

        schema_str = json.dumps(schema_dict)
        output_str = self._pydantic_format_tmpl.format(schema=schema_str)
        if escape_json:
            return output_str.replace("{", "{{").replace("}", "}}")
        else:
            return output_str

    def parse(self, text: str) -> Any:
        """Parse, validate, and correct errors programmatically."""
        json_str = extract_json_str(text)
        return self._output_cls.model_validate_json(json_str)

    def format(self, query: str) -> str:
        """Format a query with structured output formatting instructions."""
        return query + "\n\n" + self.get_format_string(escape_json=True)

```
  
---|---  
###  format_string `property` #
```
format_string: str

```

Format string.
###  get_format_string #
```
get_format_string(escape_json: bool = True) -> str

```

Format string.
Source code in `llama-index-core/llama_index/core/output_parsers/pydantic.py`

| ```
def get_format_string(self, escape_json: bool = True) -> str:
    """Format string."""
    schema_dict = self._output_cls.model_json_schema()
    for key in self._excluded_schema_keys_from_format:
        del schema_dict[key]

    schema_str = json.dumps(schema_dict)
    output_str = self._pydantic_format_tmpl.format(schema=schema_str)
    if escape_json:
        return output_str.replace("{", "{{").replace("}", "}}")
    else:
        return output_str

```
  
---|---  
###  parse #
```
parse(text: str) -> Any

```

Parse, validate, and correct errors programmatically.
Source code in `llama-index-core/llama_index/core/output_parsers/pydantic.py`

| ```
def parse(self, text: str) -> Any:
    """Parse, validate, and correct errors programmatically."""
    json_str = extract_json_str(text)
    return self._output_cls.model_validate_json(json_str)

```
  
---|---  
###  format #
```
format(query: str) -> str

```

Format a query with structured output formatting instructions.
Source code in `llama-index-core/llama_index/core/output_parsers/pydantic.py`

| ```
def format(self, query: str) -> str:
    """Format a query with structured output formatting instructions."""
    return query + "\n\n" + self.get_format_string(escape_json=True)

```
  
---|---
