# Span types
##  BaseSpan #
Bases: `BaseModel`
Base data class representing a span.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`id_` |  `str` |  Id of span. |  `'7c7af04b-08d7-4ce6-b1bf-443e4a90f77e'`  
`parent_id` |  `str | None` |  Id of parent span. |  `None`  
`tags` |  `Dict[str, Any]` |  |  `{}`  
Source code in `llama_index_instrumentation/span/base.py`

| ```
class BaseSpan(BaseModel):
    """Base data class representing a span."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id_: str = Field(default_factory=lambda: str(uuid4()), description="Id of span.")
    parent_id: Optional[str] = Field(default=None, description="Id of parent span.")
    tags: Dict[str, Any] = Field(default={})

```
  
---|---
