# Index
Vector store index types.
##  VectorStoreQueryResult `dataclass` #
Vector store query result.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `Sequence[BaseNode] | None` |  |  `None`  
`similarities` |  `List[float] | None` |  |  `None`  
`ids` |  `List[str] | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@dataclass
class VectorStoreQueryResult:
    """Vector store query result."""

    nodes: Optional[Sequence[BaseNode]] = None
    similarities: Optional[List[float]] = None
    ids: Optional[List[str]] = None

```
  
---|---  
##  VectorStoreQueryMode #
Bases: `str`, `Enum`
Vector store query mode.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class VectorStoreQueryMode(str, Enum):
    """Vector store query mode."""

    DEFAULT = "default"
    SPARSE = "sparse"
    HYBRID = "hybrid"
    TEXT_SEARCH = "text_search"
    SEMANTIC_HYBRID = "semantic_hybrid"

    # fit learners
    SVM = "svm"
    LOGISTIC_REGRESSION = "logistic_regression"
    LINEAR_REGRESSION = "linear_regression"

    # maximum marginal relevance
    MMR = "mmr"

```
  
---|---  
##  FilterOperator #
Bases: `str`, `Enum`
Vector store filter operator.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class FilterOperator(str, Enum):
    """Vector store filter operator."""

    # TODO add more operators
    EQ = "=="  # default operator (string, int, float)
    GT = ">"  # greater than (int, float)
    LT = "<"  # less than (int, float)
    NE = "!="  # not equal to (string, int, float)
    GTE = ">="  # greater than or equal to (int, float)
    LTE = "<="  # less than or equal to (int, float)
    IN = "in"  # In array (string or number)
    NIN = "nin"  # Not in array (string or number)
    ANY = "any"  # Contains any (array of strings)
    ALL = "all"  # Contains all (array of strings)
    TEXT_MATCH = "text_match"  # full text match (allows you to search for a specific substring, token or phrase within the text field)
    TEXT_MATCH_INSENSITIVE = (
        "text_match_insensitive"  # full text match (case insensitive)
    )
    CONTAINS = "contains"  # metadata array contains value (string or number)
    IS_EMPTY = "is_empty"  # the field is not exist or empty (null or empty array)

```
  
---|---  
##  FilterCondition #
Bases: `str`, `Enum`
Vector store filter conditions to combine different filters.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class FilterCondition(str, Enum):
    """Vector store filter conditions to combine different filters."""

    # TODO add more conditions
    AND = "and"
    OR = "or"
    NOT = "not"  # negates the filter condition

```
  
---|---  
##  MetadataFilter #
Bases: `BaseModel`
Comprehensive metadata filter for vector stores to support more operators.
Value uses Strict types, as int, float and str are compatible types and were all converted to string before.
See: https://docs.pydantic.dev/latest/usage/types/#strict-types
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  |  _required_  
`value` |  `Annotated[int, Strict] | Annotated[float, Strict] | Annotated[str, Strict] | List[Annotated[str, Strict]] | List[Annotated[float, Strict]] | List[Annotated[int, Strict]] | None` |  |  _required_  
`operator` |  `FilterOperator` |  |  `<FilterOperator.EQ: '=='>`  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class MetadataFilter(BaseModel):
    r"""
    Comprehensive metadata filter for vector stores to support more operators.

    Value uses Strict types, as int, float and str are compatible types and were all
    converted to string before.

    See: https://docs.pydantic.dev/latest/usage/types/#strict-types
    """

    key: str
    value: Optional[
        Union[
            StrictInt,
            StrictFloat,
            StrictStr,
            List[StrictStr],
            List[StrictFloat],
            List[StrictInt],
        ]
    ]
    operator: FilterOperator = FilterOperator.EQ

    @classmethod
    def from_dict(
        cls,
        filter_dict: Dict,
    ) -> "MetadataFilter":
        """
        Create MetadataFilter from dictionary.

        Args:
            filter_dict: Dict with key, value and operator.

        """
        return MetadataFilter.model_validate(filter_dict)

```
  
---|---  
###  from_dict `classmethod` #
```
from_dict(filter_dict: Dict) -> MetadataFilter

```

Create MetadataFilter from dictionary.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`filter_dict` |  `Dict` |  Dict with key, value and operator. |  _required_  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@classmethod
def from_dict(
    cls,
    filter_dict: Dict,
) -> "MetadataFilter":
    """
    Create MetadataFilter from dictionary.

    Args:
        filter_dict: Dict with key, value and operator.

    """
    return MetadataFilter.model_validate(filter_dict)

```
  
---|---  
##  MetadataFilters #
Bases: `BaseModel`
Metadata filters for vector stores.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`filters` |  `List[Union[MetadataFilter, MetadataFilters]]` |  |  _required_  
`condition` |  `FilterCondition | None` |  |  `<FilterCondition.AND: 'and'>`  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class MetadataFilters(BaseModel):
    """Metadata filters for vector stores."""

    # Exact match filters and Advanced filters with operators like >, <, >=, <=, !=, etc.
    filters: List[Union[MetadataFilter, ExactMatchFilter, "MetadataFilters"]]
    # and/or such conditions for combining different filters
    condition: Optional[FilterCondition] = FilterCondition.AND

    @classmethod
    @deprecated(
        "`from_dict()` is deprecated. "
        "Please use `MetadataFilters(filters=.., condition='and')` directly instead."
    )
    def from_dict(cls, filter_dict: Dict) -> "MetadataFilters":
        """Create MetadataFilters from json."""
        filters = []
        for k, v in filter_dict.items():
            filter = MetadataFilter(key=k, value=v, operator=FilterOperator.EQ)
            filters.append(filter)
        return cls(filters=filters)

    @classmethod
    def from_dicts(
        cls,
        filter_dicts: List[Dict],
        condition: Optional[FilterCondition] = FilterCondition.AND,
    ) -> "MetadataFilters":
        """
        Create MetadataFilters from dicts.

        This takes in a list of individual MetadataFilter objects, along
        with the condition.

        Args:
            filter_dicts: List of dicts, each dict is a MetadataFilter.
            condition: FilterCondition to combine different filters.

        """
        return cls(
            filters=[
                MetadataFilter.from_dict(filter_dict) for filter_dict in filter_dicts
            ],
            condition=condition,
        )

    def legacy_filters(self) -> List[ExactMatchFilter]:
        """Convert MetadataFilters to legacy ExactMatchFilters."""
        filters = []
        for filter in self.filters:
            if (
                isinstance(filter, MetadataFilters)
                or filter.operator != FilterOperator.EQ
            ):
                raise ValueError(
                    "Vector Store only supports exact match filters. "
                    "Please use ExactMatchFilter or FilterOperator.EQ instead."
                )
            filters.append(ExactMatchFilter(key=filter.key, value=filter.value))
        return filters

```
  
---|---  
###  from_dict `classmethod` #
```
from_dict(filter_dict: Dict) -> MetadataFilters

```

Create MetadataFilters from json.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@classmethod
@deprecated(
    "`from_dict()` is deprecated. "
    "Please use `MetadataFilters(filters=.., condition='and')` directly instead."
)
def from_dict(cls, filter_dict: Dict) -> "MetadataFilters":
    """Create MetadataFilters from json."""
    filters = []
    for k, v in filter_dict.items():
        filter = MetadataFilter(key=k, value=v, operator=FilterOperator.EQ)
        filters.append(filter)
    return cls(filters=filters)

```
  
---|---  
###  from_dicts `classmethod` #
```
from_dicts(filter_dicts: List[Dict], condition: Optional[FilterCondition] = AND) -> MetadataFilters

```

Create MetadataFilters from dicts.
This takes in a list of individual MetadataFilter objects, along with the condition.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`filter_dicts` |  `List[Dict]` |  List of dicts, each dict is a MetadataFilter. |  _required_  
`condition` |  `Optional[FilterCondition]` |  FilterCondition to combine different filters. |  `AND`  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@classmethod
def from_dicts(
    cls,
    filter_dicts: List[Dict],
    condition: Optional[FilterCondition] = FilterCondition.AND,
) -> "MetadataFilters":
    """
    Create MetadataFilters from dicts.

    This takes in a list of individual MetadataFilter objects, along
    with the condition.

    Args:
        filter_dicts: List of dicts, each dict is a MetadataFilter.
        condition: FilterCondition to combine different filters.

    """
    return cls(
        filters=[
            MetadataFilter.from_dict(filter_dict) for filter_dict in filter_dicts
        ],
        condition=condition,
    )

```
  
---|---  
###  legacy_filters #
```
legacy_filters() -> List[ExactMatchFilter]

```

Convert MetadataFilters to legacy ExactMatchFilters.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
def legacy_filters(self) -> List[ExactMatchFilter]:
    """Convert MetadataFilters to legacy ExactMatchFilters."""
    filters = []
    for filter in self.filters:
        if (
            isinstance(filter, MetadataFilters)
            or filter.operator != FilterOperator.EQ
        ):
            raise ValueError(
                "Vector Store only supports exact match filters. "
                "Please use ExactMatchFilter or FilterOperator.EQ instead."
            )
        filters.append(ExactMatchFilter(key=filter.key, value=filter.value))
    return filters

```
  
---|---  
##  VectorStoreQuerySpec #
Bases: `BaseModel`
Schema for a structured request for vector store (i.e. to be converted to a VectorStoreQuery).
Currently only used by VectorIndexAutoRetriever.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  |  _required_  
`filters` |  `List[MetadataFilter]` |  |  _required_  
`top_k` |  `int | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class VectorStoreQuerySpec(BaseModel):
    """
    Schema for a structured request for vector store
    (i.e. to be converted to a VectorStoreQuery).

    Currently only used by VectorIndexAutoRetriever.
    """

    query: str
    filters: List[MetadataFilter]
    top_k: Optional[int] = None

```
  
---|---  
##  MetadataInfo #
Bases: `BaseModel`
Information about a metadata filter supported by a vector store.
Currently only used by VectorIndexAutoRetriever.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`name` |  `str` |  |  _required_  
`type` |  `str` |  |  _required_  
`description` |  `str` |  |  _required_  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class MetadataInfo(BaseModel):
    """
    Information about a metadata filter supported by a vector store.

    Currently only used by VectorIndexAutoRetriever.
    """

    name: str
    type: str
    description: str

```
  
---|---  
##  VectorStoreInfo #
Bases: `BaseModel`
Information about a vector store (content and supported metadata filters).
Currently only used by VectorIndexAutoRetriever.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`metadata_info` |  `List[MetadataInfo]` |  |  _required_  
`content_info` |  `str` |  |  _required_  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class VectorStoreInfo(BaseModel):
    """
    Information about a vector store (content and supported metadata filters).

    Currently only used by VectorIndexAutoRetriever.
    """

    metadata_info: List[MetadataInfo]
    content_info: str

```
  
---|---  
##  VectorStoreQuery `dataclass` #
Vector store query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_embedding` |  `List[float] | None` |  |  `None`  
`similarity_top_k` |  `int` |  |  `1`  
`doc_ids` |  `List[str] | None` |  |  `None`  
`node_ids` |  `List[str] | None` |  |  `None`  
`query_str` |  `str | None` |  |  `None`  
`output_fields` |  `List[str] | None` |  |  `None`  
`embedding_field` |  `str | None` |  |  `None`  
`mode` |  `VectorStoreQueryMode` |  |  `<VectorStoreQueryMode.DEFAULT: 'default'>`  
`alpha` |  `float | None` |  |  `None`  
`filters` |  `MetadataFilters | None` |  |  `None`  
`mmr_threshold` |  `float | None` |  |  `None`  
`sparse_top_k` |  `int | None` |  |  `None`  
`hybrid_top_k` |  `int | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@dataclass
class VectorStoreQuery:
    """Vector store query."""

    query_embedding: Optional[List[float]] = None
    similarity_top_k: int = 1
    doc_ids: Optional[List[str]] = None
    node_ids: Optional[List[str]] = None
    query_str: Optional[str] = None
    output_fields: Optional[List[str]] = None
    embedding_field: Optional[str] = None

    mode: VectorStoreQueryMode = VectorStoreQueryMode.DEFAULT

    # NOTE: only for hybrid search (0 for bm25, 1 for vector search)
    alpha: Optional[float] = None

    # metadata filters
    filters: Optional[MetadataFilters] = None

    # only for mmr
    mmr_threshold: Optional[float] = None

    # NOTE: currently only used by postgres hybrid search
    sparse_top_k: Optional[int] = None
    # NOTE: return top k results from hybrid search. similarity_top_k is used for dense search top k
    hybrid_top_k: Optional[int] = None

```
  
---|---  
##  VectorStore #
Bases: `Protocol`
Abstract vector store protocol.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@runtime_checkable
class VectorStore(Protocol):
    """Abstract vector store protocol."""

    stores_text: bool
    is_embedding_query: bool = True

    @property
    def client(self) -> Any:
        """Get client."""
        ...

    def add(
        self,
        nodes: List[BaseNode],
        **add_kwargs: Any,
    ) -> List[str]:
        """Add nodes with embedding to vector store."""
        ...

    async def async_add(
        self,
        nodes: List[BaseNode],
        **kwargs: Any,
    ) -> List[str]:
        """
        Asynchronously add nodes with embedding to vector store.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call add synchronously.
        """
        return self.add(nodes)

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id."""
        ...

    async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call delete synchronously.
        """
        self.delete(ref_doc_id, **delete_kwargs)

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """Query vector store."""
        ...

    async def aquery(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        """
        Asynchronously query vector store.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call query synchronously.
        """
        return self.query(query, **kwargs)

    def persist(
        self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> None:
        return None

```
  
---|---  
###  client `property` #
```
client: Any

```

Get client.
###  add #
```
add(nodes: List[BaseNode], **add_kwargs: Any) -> List[str]

```

Add nodes with embedding to vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
def add(
    self,
    nodes: List[BaseNode],
    **add_kwargs: Any,
) -> List[str]:
    """Add nodes with embedding to vector store."""
    ...

```
  
---|---  
###  async_add `async` #
```
async_add(nodes: List[BaseNode], **kwargs: Any) -> List[str]

```

Asynchronously add nodes with embedding to vector store. NOTE: this is not implemented for all vector stores. If not implemented, it will just call add synchronously.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def async_add(
    self,
    nodes: List[BaseNode],
    **kwargs: Any,
) -> List[str]:
    """
    Asynchronously add nodes with embedding to vector store.
    NOTE: this is not implemented for all vector stores. If not implemented,
    it will just call add synchronously.
    """
    return self.add(nodes)

```
  
---|---  
###  delete #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using with ref_doc_id.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete nodes using with ref_doc_id."""
    ...

```
  
---|---  
###  adelete `async` #
```
adelete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using with ref_doc_id. NOTE: this is not implemented for all vector stores. If not implemented, it will just call delete synchronously.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete nodes using with ref_doc_id.
    NOTE: this is not implemented for all vector stores. If not implemented,
    it will just call delete synchronously.
    """
    self.delete(ref_doc_id, **delete_kwargs)

```
  
---|---  
###  query #
```
query(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Query vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
    """Query vector store."""
    ...

```
  
---|---  
###  aquery `async` #
```
aquery(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Asynchronously query vector store. NOTE: this is not implemented for all vector stores. If not implemented, it will just call query synchronously.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def aquery(
    self, query: VectorStoreQuery, **kwargs: Any
) -> VectorStoreQueryResult:
    """
    Asynchronously query vector store.
    NOTE: this is not implemented for all vector stores. If not implemented,
    it will just call query synchronously.
    """
    return self.query(query, **kwargs)

```
  
---|---  
##  BasePydanticVectorStore #
Bases: `BaseComponent`, `ABC`
Abstract vector store protocol.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`stores_text` |  `bool` |  |  _required_  
`is_embedding_query` |  `bool` |  |  `True`  
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
class BasePydanticVectorStore(BaseComponent, ABC):
    """Abstract vector store protocol."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    stores_text: bool
    is_embedding_query: bool = True

    @property
    @abstractmethod
    def client(self) -> Any:
        """Get client."""

    def get_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
    ) -> List[BaseNode]:
        """Get nodes from vector store."""
        raise NotImplementedError("get_nodes not implemented")

    async def aget_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
    ) -> List[BaseNode]:
        """Asynchronously get nodes from vector store."""
        return self.get_nodes(node_ids, filters)

    @abstractmethod
    def add(
        self,
        nodes: Sequence[BaseNode],
        **kwargs: Any,
    ) -> List[str]:
        """Add nodes to vector store."""

    async def async_add(
        self,
        nodes: Sequence[BaseNode],
        **kwargs: Any,
    ) -> List[str]:
        """
        Asynchronously add nodes to vector store.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call add synchronously.
        """
        return self.add(nodes, **kwargs)

    @abstractmethod
    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id."""

    async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call delete synchronously.
        """
        self.delete(ref_doc_id, **delete_kwargs)

    def delete_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
        **delete_kwargs: Any,
    ) -> None:
        """Delete nodes from vector store."""
        raise NotImplementedError("delete_nodes not implemented")

    async def adelete_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        filters: Optional[MetadataFilters] = None,
        **delete_kwargs: Any,
    ) -> None:
        """Asynchronously delete nodes from vector store."""
        self.delete_nodes(node_ids, filters)

    def clear(self) -> None:
        """Clear all nodes from configured vector store."""
        raise NotImplementedError("clear not implemented")

    async def aclear(self) -> None:
        """Asynchronously clear all nodes from configured vector store."""
        self.clear()

    @abstractmethod
    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """Query vector store."""

    async def aquery(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> VectorStoreQueryResult:
        """
        Asynchronously query vector store.
        NOTE: this is not implemented for all vector stores. If not implemented,
        it will just call query synchronously.
        """
        return self.query(query, **kwargs)

    def persist(
        self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> None:
        return None

```
  
---|---  
###  client `abstractmethod` `property` #
```
client: Any

```

Get client.
###  get_nodes #
```
get_nodes(node_ids: Optional[List[str]] = None, filters: Optional[MetadataFilters] = None) -> List[BaseNode]

```

Get nodes from vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
def get_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    filters: Optional[MetadataFilters] = None,
) -> List[BaseNode]:
    """Get nodes from vector store."""
    raise NotImplementedError("get_nodes not implemented")

```
  
---|---  
###  aget_nodes `async` #
```
aget_nodes(node_ids: Optional[List[str]] = None, filters: Optional[MetadataFilters] = None) -> List[BaseNode]

```

Asynchronously get nodes from vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def aget_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    filters: Optional[MetadataFilters] = None,
) -> List[BaseNode]:
    """Asynchronously get nodes from vector store."""
    return self.get_nodes(node_ids, filters)

```
  
---|---  
###  add `abstractmethod` #
```
add(nodes: Sequence[BaseNode], **kwargs: Any) -> List[str]

```

Add nodes to vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@abstractmethod
def add(
    self,
    nodes: Sequence[BaseNode],
    **kwargs: Any,
) -> List[str]:
    """Add nodes to vector store."""

```
  
---|---  
###  async_add `async` #
```
async_add(nodes: Sequence[BaseNode], **kwargs: Any) -> List[str]

```

Asynchronously add nodes to vector store. NOTE: this is not implemented for all vector stores. If not implemented, it will just call add synchronously.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def async_add(
    self,
    nodes: Sequence[BaseNode],
    **kwargs: Any,
) -> List[str]:
    """
    Asynchronously add nodes to vector store.
    NOTE: this is not implemented for all vector stores. If not implemented,
    it will just call add synchronously.
    """
    return self.add(nodes, **kwargs)

```
  
---|---  
###  delete `abstractmethod` #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using with ref_doc_id.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@abstractmethod
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete nodes using with ref_doc_id."""

```
  
---|---  
###  adelete `async` #
```
adelete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using with ref_doc_id. NOTE: this is not implemented for all vector stores. If not implemented, it will just call delete synchronously.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def adelete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """
    Delete nodes using with ref_doc_id.
    NOTE: this is not implemented for all vector stores. If not implemented,
    it will just call delete synchronously.
    """
    self.delete(ref_doc_id, **delete_kwargs)

```
  
---|---  
###  delete_nodes #
```
delete_nodes(node_ids: Optional[List[str]] = None, filters: Optional[MetadataFilters] = None, **delete_kwargs: Any) -> None

```

Delete nodes from vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
def delete_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    filters: Optional[MetadataFilters] = None,
    **delete_kwargs: Any,
) -> None:
    """Delete nodes from vector store."""
    raise NotImplementedError("delete_nodes not implemented")

```
  
---|---  
###  adelete_nodes `async` #
```
adelete_nodes(node_ids: Optional[List[str]] = None, filters: Optional[MetadataFilters] = None, **delete_kwargs: Any) -> None

```

Asynchronously delete nodes from vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def adelete_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    filters: Optional[MetadataFilters] = None,
    **delete_kwargs: Any,
) -> None:
    """Asynchronously delete nodes from vector store."""
    self.delete_nodes(node_ids, filters)

```
  
---|---  
###  clear #
```
clear() -> None

```

Clear all nodes from configured vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
def clear(self) -> None:
    """Clear all nodes from configured vector store."""
    raise NotImplementedError("clear not implemented")

```
  
---|---  
###  aclear `async` #
```
aclear() -> None

```

Asynchronously clear all nodes from configured vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def aclear(self) -> None:
    """Asynchronously clear all nodes from configured vector store."""
    self.clear()

```
  
---|---  
###  query `abstractmethod` #
```
query(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Query vector store.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
@abstractmethod
def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
    """Query vector store."""

```
  
---|---  
###  aquery `async` #
```
aquery(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Asynchronously query vector store. NOTE: this is not implemented for all vector stores. If not implemented, it will just call query synchronously.
Source code in `llama-index-core/llama_index/core/vector_stores/types.py`

| ```
async def aquery(
    self, query: VectorStoreQuery, **kwargs: Any
) -> VectorStoreQueryResult:
    """
    Asynchronously query vector store.
    NOTE: this is not implemented for all vector stores. If not implemented,
    it will just call query synchronously.
    """
    return self.query(query, **kwargs)

```
  
---|---
