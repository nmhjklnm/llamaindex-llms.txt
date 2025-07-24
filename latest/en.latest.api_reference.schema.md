# Index
Base schema for data structures.
##  BaseComponent #
Bases: `BaseModel`
Base component object to capture class names.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class BaseComponent(BaseModel):
    """Base component object to capture class names."""

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema = handler.resolve_ref_schema(json_schema)

        # inject class name to help with serde
        if "properties" in json_schema:
            json_schema["properties"]["class_name"] = {
                "title": "Class Name",
                "type": "string",
                "default": cls.class_name(),
            }
        return json_schema

    @classmethod
    def class_name(cls) -> str:
        """
        Get the class name, used as a unique ID in serialization.

        This provides a key that makes serialization robust against actual class
        name changes.
        """
        return "base_component"

    def json(self, **kwargs: Any) -> str:
        return self.to_json(**kwargs)

    @model_serializer(mode="wrap")
    def custom_model_dump(
        self, handler: SerializerFunctionWrapHandler, info: SerializationInfo
    ) -> Dict[str, Any]:
        data = handler(self)
        data["class_name"] = self.class_name()
        return data

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        return self.model_dump(**kwargs)

    def __getstate__(self) -> Dict[str, Any]:
        state = super().__getstate__()

        # remove attributes that are not pickleable -- kind of dangerous
        keys_to_remove = []
        for key, val in state["__dict__"].items():
            try:
                pickle.dumps(val)
            except Exception:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            logging.warning(f"Removing unpickleable attribute {key}")
            del state["__dict__"][key]

        # remove private attributes if they aren't pickleable -- kind of dangerous
        keys_to_remove = []
        private_attrs = state.get("__pydantic_private__", None)
        if private_attrs:
            for key, val in state["__pydantic_private__"].items():
                try:
                    pickle.dumps(val)
                except Exception:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                logging.warning(f"Removing unpickleable private attribute {key}")
                del state["__pydantic_private__"][key]

        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        # Use the __dict__ and __init__ method to set state
        # so that all variables initialize
        try:
            self.__init__(**state["__dict__"])  # type: ignore
        except Exception:
            # Fall back to the default __setstate__ method
            # This may not work if the class had unpickleable attributes
            super().__setstate__(state)

    def to_dict(self, **kwargs: Any) -> Dict[str, Any]:
        data = self.dict(**kwargs)
        data["class_name"] = self.class_name()
        return data

    def to_json(self, **kwargs: Any) -> str:
        data = self.to_dict(**kwargs)
        return json.dumps(data)

    # TODO: return type here not supported by current mypy version
    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs: Any) -> Self:  # type: ignore
        # In SimpleKVStore we rely on shallow coping. Hence, the data will be modified in the store directly.
        # And it is the same when the user is passing a dictionary to create a component. We can't modify the passed down dictionary.
        data = dict(data)
        if isinstance(kwargs, dict):
            data.update(kwargs)
        data.pop("class_name", None)
        return cls(**data)

    @classmethod
    def from_json(cls, data_str: str, **kwargs: Any) -> Self:  # type: ignore
        data = json.loads(data_str)
        return cls.from_dict(data, **kwargs)

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get the class name, used as a unique ID in serialization.
This provides a key that makes serialization robust against actual class name changes.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def class_name(cls) -> str:
    """
    Get the class name, used as a unique ID in serialization.

    This provides a key that makes serialization robust against actual class
    name changes.
    """
    return "base_component"

```
  
---|---  
##  TransformComponent #
Bases: `BaseComponent`, `DispatcherSpanMixin`
Base class for transform components.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class TransformComponent(BaseComponent, DispatcherSpanMixin):
    """Base class for transform components."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @abstractmethod
    def __call__(self, nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]:
        """Transform nodes."""

    async def acall(
        self, nodes: Sequence[BaseNode], **kwargs: Any
    ) -> Sequence[BaseNode]:
        """Async transform nodes."""
        return self.__call__(nodes, **kwargs)

```
  
---|---  
###  acall `async` #
```
acall(nodes: Sequence[BaseNode], **kwargs: Any) -> Sequence[BaseNode]

```

Async transform nodes.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
async def acall(
    self, nodes: Sequence[BaseNode], **kwargs: Any
) -> Sequence[BaseNode]:
    """Async transform nodes."""
    return self.__call__(nodes, **kwargs)

```
  
---|---  
##  NodeRelationship #
Bases: `str`, `Enum`
Node relationships used in `BaseNode` class.
Attributes:
Name | Type | Description  
---|---|---  
`SOURCE` |  |  The node is the source document.  
`PREVIOUS` |  |  The node is the previous node in the document.  
`NEXT` |  |  The node is the next node in the document.  
`PARENT` |  |  The node is the parent node in the document.  
`CHILD` |  |  The node is a child node in the document.  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class NodeRelationship(str, Enum):
    """
    Node relationships used in `BaseNode` class.

    Attributes:
        SOURCE: The node is the source document.
        PREVIOUS: The node is the previous node in the document.
        NEXT: The node is the next node in the document.
        PARENT: The node is the parent node in the document.
        CHILD: The node is a child node in the document.

    """

    SOURCE = auto()
    PREVIOUS = auto()
    NEXT = auto()
    PARENT = auto()
    CHILD = auto()

```
  
---|---  
##  RelatedNodeInfo #
Bases: `BaseComponent`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_id` |  `str` |  |  _required_  
`node_type` |  `Annotated[ObjectType, PlainSerializer] | str | None` |  |  `None`  
`hash` |  `str | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class RelatedNodeInfo(BaseComponent):
    node_id: str
    node_type: Annotated[ObjectType, EnumNameSerializer] | str | None = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    hash: Optional[str] = None

    @classmethod
    def class_name(cls) -> str:
        return "RelatedNodeInfo"

```
  
---|---  
##  BaseNode #
Bases: `BaseComponent`
Base node Object.
Generic abstract interface for retrievable nodes
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`id_` |  `str` |  Unique ID of the node. |  `'26d30387-3086-47e9-a010-7dc4e4c72f9c'`  
`embedding` |  `List[float] | None` |  Embedding of the node. |  `None`  
`excluded_embed_metadata_keys` |  `List[str]` |  Metadata keys that are excluded from text for the embed model. |  `<dynamic>`  
`excluded_llm_metadata_keys` |  `List[str]` |  Metadata keys that are excluded from text for the LLM. |  `<dynamic>`  
`metadata_template` |  `str` |  Template for how metadata is formatted, with {key} and {value} placeholders. |  `'{key}: {value}'`  
`metadata_separator` |  `str` |  Separator between metadata fields when converting to string. |  `'\n'`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class BaseNode(BaseComponent):
    """
    Base node Object.

    Generic abstract interface for retrievable nodes

    """

    # hash is computed on local field, during the validation process
    model_config = ConfigDict(populate_by_name=True, validate_assignment=True)

    id_: str = Field(
        default_factory=lambda: str(uuid.uuid4()), description="Unique ID of the node."
    )
    embedding: Optional[List[float]] = Field(
        default=None, description="Embedding of the node."
    )

    """"
    metadata fields
    - injected as part of the text shown to LLMs as context
    - injected as part of the text for generating embeddings
    - used by vector DBs for metadata filtering

    """
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="A flat dictionary of metadata fields",
        alias="extra_info",
    )
    excluded_embed_metadata_keys: List[str] = Field(
        default_factory=list,
        description="Metadata keys that are excluded from text for the embed model.",
    )
    excluded_llm_metadata_keys: List[str] = Field(
        default_factory=list,
        description="Metadata keys that are excluded from text for the LLM.",
    )
    relationships: Dict[
        Annotated[NodeRelationship, EnumNameSerializer],
        RelatedNodeType,
    ] = Field(
        default_factory=dict,
        description="A mapping of relationships to other node information.",
    )
    metadata_template: str = Field(
        default=DEFAULT_METADATA_TMPL,
        description=(
            "Template for how metadata is formatted, with {key} and "
            "{value} placeholders."
        ),
    )
    metadata_separator: str = Field(
        default="\n",
        description="Separator between metadata fields when converting to string.",
        alias="metadata_seperator",
    )

    @classmethod
    @abstractmethod
    def get_type(cls) -> str:
        """Get Object type."""

    @abstractmethod
    def get_content(self, metadata_mode: MetadataMode = MetadataMode.ALL) -> str:
        """Get object content."""

    def get_metadata_str(self, mode: MetadataMode = MetadataMode.ALL) -> str:
        """Metadata info string."""
        if mode == MetadataMode.NONE:
            return ""

        usable_metadata_keys = set(self.metadata.keys())
        if mode == MetadataMode.LLM:
            for key in self.excluded_llm_metadata_keys:
                if key in usable_metadata_keys:
                    usable_metadata_keys.remove(key)
        elif mode == MetadataMode.EMBED:
            for key in self.excluded_embed_metadata_keys:
                if key in usable_metadata_keys:
                    usable_metadata_keys.remove(key)

        return self.metadata_separator.join(
            [
                self.metadata_template.format(key=key, value=str(value))
                for key, value in self.metadata.items()
                if key in usable_metadata_keys
            ]
        )

    @abstractmethod
    def set_content(self, value: Any) -> None:
        """Set the content of the node."""

    @property
    @abstractmethod
    def hash(self) -> str:
        """Get hash of node."""

    @property
    def node_id(self) -> str:
        return self.id_

    @node_id.setter
    def node_id(self, value: str) -> None:
        self.id_ = value

    @property
    def source_node(self) -> Optional[RelatedNodeInfo]:
        """
        Source object node.

        Extracted from the relationships field.

        """
        if NodeRelationship.SOURCE not in self.relationships:
            return None

        relation = self.relationships[NodeRelationship.SOURCE]
        if isinstance(relation, list):
            raise ValueError("Source object must be a single RelatedNodeInfo object")
        return relation

    @property
    def prev_node(self) -> Optional[RelatedNodeInfo]:
        """Prev node."""
        if NodeRelationship.PREVIOUS not in self.relationships:
            return None

        relation = self.relationships[NodeRelationship.PREVIOUS]
        if not isinstance(relation, RelatedNodeInfo):
            raise ValueError("Previous object must be a single RelatedNodeInfo object")
        return relation

    @property
    def next_node(self) -> Optional[RelatedNodeInfo]:
        """Next node."""
        if NodeRelationship.NEXT not in self.relationships:
            return None

        relation = self.relationships[NodeRelationship.NEXT]
        if not isinstance(relation, RelatedNodeInfo):
            raise ValueError("Next object must be a single RelatedNodeInfo object")
        return relation

    @property
    def parent_node(self) -> Optional[RelatedNodeInfo]:
        """Parent node."""
        if NodeRelationship.PARENT not in self.relationships:
            return None

        relation = self.relationships[NodeRelationship.PARENT]
        if not isinstance(relation, RelatedNodeInfo):
            raise ValueError("Parent object must be a single RelatedNodeInfo object")
        return relation

    @property
    def child_nodes(self) -> Optional[List[RelatedNodeInfo]]:
        """Child nodes."""
        if NodeRelationship.CHILD not in self.relationships:
            return None

        relation = self.relationships[NodeRelationship.CHILD]
        if not isinstance(relation, list):
            raise ValueError("Child objects must be a list of RelatedNodeInfo objects.")
        return relation

    @property
    def ref_doc_id(self) -> Optional[str]:  # pragma: no cover
        """Deprecated: Get ref doc id."""
        source_node = self.source_node
        if source_node is None:
            return None
        return source_node.node_id

    @property
    @deprecated(
        version="0.12.2",
        reason="'extra_info' is deprecated, use 'metadata' instead.",
    )
    def extra_info(self) -> dict[str, Any]:  # pragma: no coverde
        return self.metadata

    @extra_info.setter
    @deprecated(
        version="0.12.2",
        reason="'extra_info' is deprecated, use 'metadata' instead.",
    )
    def extra_info(self, extra_info: dict[str, Any]) -> None:  # pragma: no coverde
        self.metadata = extra_info

    def __str__(self) -> str:
        source_text_truncated = truncate_text(
            self.get_content().strip(), TRUNCATE_LENGTH
        )
        source_text_wrapped = textwrap.fill(
            f"Text: {source_text_truncated}\n", width=WRAP_WIDTH
        )
        return f"Node ID: {self.node_id}\n{source_text_wrapped}"

    def get_embedding(self) -> List[float]:
        """
        Get embedding.

        Errors if embedding is None.

        """
        if self.embedding is None:
            raise ValueError("embedding not set.")
        return self.embedding

    def as_related_node_info(self) -> RelatedNodeInfo:
        """Get node as RelatedNodeInfo."""
        return RelatedNodeInfo(
            node_id=self.node_id,
            node_type=self.get_type(),
            metadata=self.metadata,
            hash=self.hash,
        )

```
  
---|---  
###  embedding `class-attribute` `instance-attribute` #
```
embedding: Optional[List[float]] = Field(default=None, description='Embedding of the node.')

```

" metadata fields - injected as part of the text shown to LLMs as context - injected as part of the text for generating embeddings - used by vector DBs for metadata filtering
###  hash `abstractmethod` `property` #
```
hash: str

```

Get hash of node.
###  source_node `property` #
```
source_node: Optional[RelatedNodeInfo]

```

Source object node.
Extracted from the relationships field.
###  prev_node `property` #
```
prev_node: Optional[RelatedNodeInfo]

```

Prev node.
###  next_node `property` #
```
next_node: Optional[RelatedNodeInfo]

```

Next node.
###  parent_node `property` #
```
parent_node: Optional[RelatedNodeInfo]

```

Parent node.
###  child_nodes `property` #
```
child_nodes: Optional[List[RelatedNodeInfo]]

```

Child nodes.
###  ref_doc_id `property` #
```
ref_doc_id: Optional[str]

```

Deprecated: Get ref doc id.
###  get_type `abstractmethod` `classmethod` #
```
get_type() -> str

```

Get Object type.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
@abstractmethod
def get_type(cls) -> str:
    """Get Object type."""

```
  
---|---  
###  get_content `abstractmethod` #
```
get_content(metadata_mode: MetadataMode = ALL) -> str

```

Get object content.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@abstractmethod
def get_content(self, metadata_mode: MetadataMode = MetadataMode.ALL) -> str:
    """Get object content."""

```
  
---|---  
###  get_metadata_str #
```
get_metadata_str(mode: MetadataMode = ALL) -> str

```

Metadata info string.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def get_metadata_str(self, mode: MetadataMode = MetadataMode.ALL) -> str:
    """Metadata info string."""
    if mode == MetadataMode.NONE:
        return ""

    usable_metadata_keys = set(self.metadata.keys())
    if mode == MetadataMode.LLM:
        for key in self.excluded_llm_metadata_keys:
            if key in usable_metadata_keys:
                usable_metadata_keys.remove(key)
    elif mode == MetadataMode.EMBED:
        for key in self.excluded_embed_metadata_keys:
            if key in usable_metadata_keys:
                usable_metadata_keys.remove(key)

    return self.metadata_separator.join(
        [
            self.metadata_template.format(key=key, value=str(value))
            for key, value in self.metadata.items()
            if key in usable_metadata_keys
        ]
    )

```
  
---|---  
###  set_content `abstractmethod` #
```
set_content(value: Any) -> None

```

Set the content of the node.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@abstractmethod
def set_content(self, value: Any) -> None:
    """Set the content of the node."""

```
  
---|---  
###  get_embedding #
```
get_embedding() -> List[float]

```

Get embedding.
Errors if embedding is None.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def get_embedding(self) -> List[float]:
    """
    Get embedding.

    Errors if embedding is None.

    """
    if self.embedding is None:
        raise ValueError("embedding not set.")
    return self.embedding

```
  
---|---  
###  as_related_node_info #
```
as_related_node_info() -> RelatedNodeInfo

```

Get node as RelatedNodeInfo.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def as_related_node_info(self) -> RelatedNodeInfo:
    """Get node as RelatedNodeInfo."""
    return RelatedNodeInfo(
        node_id=self.node_id,
        node_type=self.get_type(),
        metadata=self.metadata,
        hash=self.hash,
    )

```
  
---|---  
##  MediaResource #
Bases: `BaseModel`
A container class for media content.
This class represents a generic media resource that can be stored and accessed in multiple ways - as raw bytes, on the filesystem, or via URL. It also supports storing vector embeddings for the media content.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`embeddings` |  `dict[Literal['sparse', 'dense'], list[float]] | None` |  Vector representation of this resource. |  `None`  
`data` |  `bytes | None` |  base64 binary representation of this resource. |  `None`  
`text` |  `str | None` |  Text representation of this resource. |  `None`  
`path` |  `Path | None` |  Filesystem path of this resource. |  `None`  
`url` |  `AnyUrl | None` |  URL to reach this resource. |  `None`  
`mimetype` |  `str | None` |  MIME type of this resource. |  `None`  
Attributes:
Name | Type | Description  
---|---|---  
`embeddings` |  |  Multi-vector dict representation of this resource for embedding-based search/retrieval  
`text` |  |  Plain text representation of this resource  
`data` |  |  Raw binary data of the media content  
`mimetype` |  |  The MIME type indicating the format/type of the media content  
`path` |  |  Local filesystem path where the media content can be accessed  
`url` |  |  URL where the media content can be accessed remotely  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class MediaResource(BaseModel):
    """
    A container class for media content.

    This class represents a generic media resource that can be stored and accessed
    in multiple ways - as raw bytes, on the filesystem, or via URL. It also supports
    storing vector embeddings for the media content.

    Attributes:
        embeddings: Multi-vector dict representation of this resource for embedding-based search/retrieval
        text: Plain text representation of this resource
        data: Raw binary data of the media content
        mimetype: The MIME type indicating the format/type of the media content
        path: Local filesystem path where the media content can be accessed
        url: URL where the media content can be accessed remotely

    """

    embeddings: dict[EmbeddingKind, list[float]] | None = Field(
        default=None, description="Vector representation of this resource."
    )
    data: bytes | None = Field(
        default=None,
        exclude=True,
        description="base64 binary representation of this resource.",
    )
    text: str | None = Field(
        default=None, description="Text representation of this resource."
    )
    path: Path | None = Field(
        default=None, description="Filesystem path of this resource."
    )
    url: AnyUrl | None = Field(default=None, description="URL to reach this resource.")
    mimetype: str | None = Field(
        default=None, description="MIME type of this resource."
    )

    model_config = {
        # This ensures validation runs even for None values
        "validate_default": True
    }

    @field_validator("data", mode="after")
    @classmethod
    def validate_data(cls, v: bytes | None, info: ValidationInfo) -> bytes | None:
        """
        If binary data was passed, store the resource as base64 and guess the mimetype when possible.

        In case the model was built passing binary data but without a mimetype,
        we try to guess it using the filetype library. To avoid resource-intense
        operations, we won't load the path or the URL to guess the mimetype.
        """
        if v is None:
            return v

        try:
            # Check if data is already base64 encoded.
            # b64decode() can succeed on random binary data, so we
            # pass verify=True to make sure it's not a false positive
            decoded = base64.b64decode(v, validate=True)
        except BinasciiError:
            # b64decode failed, return encoded
            return base64.b64encode(v)

        # Good as is, return unchanged
        return v

    @field_validator("mimetype", mode="after")
    @classmethod
    def validate_mimetype(cls, v: str | None, info: ValidationInfo) -> str | None:
        if v is not None:
            return v

        # Since this field validator runs after the one for `data`
        # then the contents of `data` should be encoded already
        b64_data = info.data.get("data")
        if b64_data:  # encoded bytes
            decoded_data = base64.b64decode(b64_data)
            if guess := filetype.guess(decoded_data):
                return guess.mime

        # guess from path
        rpath: str | None = info.data["path"]
        if rpath:
            extension = Path(rpath).suffix.replace(".", "")
            if ftype := filetype.get_type(ext=extension):
                return ftype.mime

        return v

    @field_serializer("path")  # type: ignore
    def serialize_path(
        self, path: Optional[Path], _info: ValidationInfo
    ) -> Optional[str]:
        if path is None:
            return path
        return str(path)

    @property
    def hash(self) -> str:
        """
        Generate a hash to uniquely identify the media resource.

        The hash is generated based on the available content (data, path, text or url).
        Returns an empty string if no content is available.
        """
        bits: list[str] = []
        if self.text is not None:
            bits.append(self.text)
        if self.data is not None:
            # Hash the binary data if available
            bits.append(str(sha256(self.data).hexdigest()))
        if self.path is not None:
            # Hash the file path if provided
            bits.append(str(sha256(str(self.path).encode("utf-8")).hexdigest()))
        if self.url is not None:
            # Use the URL string as basis for hash
            bits.append(str(sha256(str(self.url).encode("utf-8")).hexdigest()))

        doc_identity = "".join(bits)
        if not doc_identity:
            return ""
        return str(sha256(doc_identity.encode("utf-8", "surrogatepass")).hexdigest())

```
  
---|---  
###  hash `property` #
```
hash: str

```

Generate a hash to uniquely identify the media resource.
The hash is generated based on the available content (data, path, text or url). Returns an empty string if no content is available.
###  validate_data `classmethod` #
```
validate_data(v: bytes | None, info: ValidationInfo) -> bytes | None

```

If binary data was passed, store the resource as base64 and guess the mimetype when possible.
In case the model was built passing binary data but without a mimetype, we try to guess it using the filetype library. To avoid resource-intense operations, we won't load the path or the URL to guess the mimetype.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@field_validator("data", mode="after")
@classmethod
def validate_data(cls, v: bytes | None, info: ValidationInfo) -> bytes | None:
    """
    If binary data was passed, store the resource as base64 and guess the mimetype when possible.

    In case the model was built passing binary data but without a mimetype,
    we try to guess it using the filetype library. To avoid resource-intense
    operations, we won't load the path or the URL to guess the mimetype.
    """
    if v is None:
        return v

    try:
        # Check if data is already base64 encoded.
        # b64decode() can succeed on random binary data, so we
        # pass verify=True to make sure it's not a false positive
        decoded = base64.b64decode(v, validate=True)
    except BinasciiError:
        # b64decode failed, return encoded
        return base64.b64encode(v)

    # Good as is, return unchanged
    return v

```
  
---|---  
##  Node #
Bases: `BaseNode`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`text_resource` |  `MediaResource | None` |  Text content of the node. |  `None`  
`image_resource` |  `MediaResource | None` |  Image content of the node. |  `None`  
`audio_resource` |  `MediaResource | None` |  Audio content of the node. |  `None`  
`video_resource` |  `MediaResource | None` |  Video content of the node. |  `None`  
`text_template` |  `str` |  Template for how text_resource is formatted, with {content} and {metadata_str} placeholders. |  `'{metadata_str}\n\n{content}'`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class Node(BaseNode):
    text_resource: MediaResource | None = Field(
        default=None, description="Text content of the node."
    )
    image_resource: MediaResource | None = Field(
        default=None, description="Image content of the node."
    )
    audio_resource: MediaResource | None = Field(
        default=None, description="Audio content of the node."
    )
    video_resource: MediaResource | None = Field(
        default=None, description="Video content of the node."
    )
    text_template: str = Field(
        default=DEFAULT_TEXT_NODE_TMPL,
        description=(
            "Template for how text_resource is formatted, with {content} and "
            "{metadata_str} placeholders."
        ),
    )

    @classmethod
    def class_name(cls) -> str:
        return "Node"

    @classmethod
    def get_type(cls) -> str:
        """Get Object type."""
        return ObjectType.MULTIMODAL

    def get_content(self, metadata_mode: MetadataMode = MetadataMode.NONE) -> str:
        """
        Get the text content for the node if available.

        Provided for backward compatibility, use self.text_resource directly instead.
        """
        if self.text_resource:
            metadata_str = self.get_metadata_str(metadata_mode)
            if metadata_mode == MetadataMode.NONE or not metadata_str:
                return self.text_resource.text or ""

            return self.text_template.format(
                content=self.text_resource.text or "",
                metadata_str=metadata_str,
            ).strip()
        return ""

    def set_content(self, value: str) -> None:
        """
        Set the text content of the node.

        Provided for backward compatibility, set self.text_resource instead.
        """
        self.text_resource = MediaResource(text=value)

    @property
    def hash(self) -> str:
        """
        Generate a hash representing the state of the node.

        The hash is generated based on the available resources (audio, image, text or video) and its metadata.
        """
        doc_identities = []
        metadata_str = self.get_metadata_str(mode=MetadataMode.ALL)
        if metadata_str:
            doc_identities.append(metadata_str)
        if self.audio_resource is not None:
            doc_identities.append(self.audio_resource.hash)
        if self.image_resource is not None:
            doc_identities.append(self.image_resource.hash)
        if self.text_resource is not None:
            doc_identities.append(self.text_resource.hash)
        if self.video_resource is not None:
            doc_identities.append(self.video_resource.hash)

        doc_identity = "-".join(doc_identities)
        return str(sha256(doc_identity.encode("utf-8", "surrogatepass")).hexdigest())

```
  
---|---  
###  hash `property` #
```
hash: str

```

Generate a hash representing the state of the node.
The hash is generated based on the available resources (audio, image, text or video) and its metadata.
###  get_type `classmethod` #
```
get_type() -> str

```

Get Object type.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def get_type(cls) -> str:
    """Get Object type."""
    return ObjectType.MULTIMODAL

```
  
---|---  
###  get_content #
```
get_content(metadata_mode: MetadataMode = NONE) -> str

```

Get the text content for the node if available.
Provided for backward compatibility, use self.text_resource directly instead.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def get_content(self, metadata_mode: MetadataMode = MetadataMode.NONE) -> str:
    """
    Get the text content for the node if available.

    Provided for backward compatibility, use self.text_resource directly instead.
    """
    if self.text_resource:
        metadata_str = self.get_metadata_str(metadata_mode)
        if metadata_mode == MetadataMode.NONE or not metadata_str:
            return self.text_resource.text or ""

        return self.text_template.format(
            content=self.text_resource.text or "",
            metadata_str=metadata_str,
        ).strip()
    return ""

```
  
---|---  
###  set_content #
```
set_content(value: str) -> None

```

Set the text content of the node.
Provided for backward compatibility, set self.text_resource instead.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def set_content(self, value: str) -> None:
    """
    Set the text content of the node.

    Provided for backward compatibility, set self.text_resource instead.
    """
    self.text_resource = MediaResource(text=value)

```
  
---|---  
##  TextNode #
Bases: `BaseNode`
Provided for backward compatibility.
Note: we keep the field with the typo "seperator" to maintain backward compatibility for serialized objects.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`text` |  `str` |  Text content of the node. |  `''`  
`mimetype` |  `str` |  MIME type of the node content. |  `'text/plain'`  
`start_char_idx` |  `int | None` |  Start char index of the node. |  `None`  
`end_char_idx` |  `int | None` |  End char index of the node. |  `None`  
`metadata_seperator` |  `str` |  Separator between metadata fields when converting to string. |  `'\n'`  
`text_template` |  `str` |  Template for how text is formatted, with {content} and {metadata_str} placeholders. |  `'{metadata_str}\n\n{content}'`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class TextNode(BaseNode):
    """
    Provided for backward compatibility.

    Note: we keep the field with the typo "seperator" to maintain backward compatibility for
    serialized objects.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Make TextNode forward-compatible with Node by supporting 'text_resource' in the constructor."""
        if "text_resource" in kwargs:
            tr = kwargs.pop("text_resource")
            if isinstance(tr, MediaResource):
                kwargs["text"] = tr.text
            else:
                kwargs["text"] = tr["text"]
        super().__init__(*args, **kwargs)

    text: str = Field(default="", description="Text content of the node.")
    mimetype: str = Field(
        default="text/plain", description="MIME type of the node content."
    )
    start_char_idx: Optional[int] = Field(
        default=None, description="Start char index of the node."
    )
    end_char_idx: Optional[int] = Field(
        default=None, description="End char index of the node."
    )
    metadata_seperator: str = Field(
        default="\n",
        description="Separator between metadata fields when converting to string.",
    )
    text_template: str = Field(
        default=DEFAULT_TEXT_NODE_TMPL,
        description=(
            "Template for how text is formatted, with {content} and "
            "{metadata_str} placeholders."
        ),
    )

    @classmethod
    def class_name(cls) -> str:
        return "TextNode"

    @property
    def hash(self) -> str:
        doc_identity = str(self.text) + str(self.metadata)
        return str(sha256(doc_identity.encode("utf-8", "surrogatepass")).hexdigest())

    @classmethod
    def get_type(cls) -> str:
        """Get Object type."""
        return ObjectType.TEXT

    def get_content(self, metadata_mode: MetadataMode = MetadataMode.NONE) -> str:
        """Get object content."""
        metadata_str = self.get_metadata_str(mode=metadata_mode).strip()
        if metadata_mode == MetadataMode.NONE or not metadata_str:
            return self.text

        return self.text_template.format(
            content=self.text, metadata_str=metadata_str
        ).strip()

    def get_metadata_str(self, mode: MetadataMode = MetadataMode.ALL) -> str:
        """Metadata info string."""
        if mode == MetadataMode.NONE:
            return ""

        usable_metadata_keys = set(self.metadata.keys())
        if mode == MetadataMode.LLM:
            for key in self.excluded_llm_metadata_keys:
                if key in usable_metadata_keys:
                    usable_metadata_keys.remove(key)
        elif mode == MetadataMode.EMBED:
            for key in self.excluded_embed_metadata_keys:
                if key in usable_metadata_keys:
                    usable_metadata_keys.remove(key)

        return self.metadata_seperator.join(
            [
                self.metadata_template.format(key=key, value=str(value))
                for key, value in self.metadata.items()
                if key in usable_metadata_keys
            ]
        )

    def set_content(self, value: str) -> None:
        """Set the content of the node."""
        self.text = value

    def get_node_info(self) -> Dict[str, Any]:
        """Get node info."""
        return {"start": self.start_char_idx, "end": self.end_char_idx}

    def get_text(self) -> str:
        return self.get_content(metadata_mode=MetadataMode.NONE)

    @property
    @deprecated(
        version="0.12.2",
        reason="'node_info' is deprecated, use 'get_node_info' instead.",
    )
    def node_info(self) -> Dict[str, Any]:
        """Deprecated: Get node info."""
        return self.get_node_info()

```
  
---|---  
###  node_info `property` #
```
node_info: Dict[str, Any]

```

Deprecated: Get node info.
###  get_type `classmethod` #
```
get_type() -> str

```

Get Object type.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def get_type(cls) -> str:
    """Get Object type."""
    return ObjectType.TEXT

```
  
---|---  
###  get_content #
```
get_content(metadata_mode: MetadataMode = NONE) -> str

```

Get object content.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def get_content(self, metadata_mode: MetadataMode = MetadataMode.NONE) -> str:
    """Get object content."""
    metadata_str = self.get_metadata_str(mode=metadata_mode).strip()
    if metadata_mode == MetadataMode.NONE or not metadata_str:
        return self.text

    return self.text_template.format(
        content=self.text, metadata_str=metadata_str
    ).strip()

```
  
---|---  
###  get_metadata_str #
```
get_metadata_str(mode: MetadataMode = ALL) -> str

```

Metadata info string.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def get_metadata_str(self, mode: MetadataMode = MetadataMode.ALL) -> str:
    """Metadata info string."""
    if mode == MetadataMode.NONE:
        return ""

    usable_metadata_keys = set(self.metadata.keys())
    if mode == MetadataMode.LLM:
        for key in self.excluded_llm_metadata_keys:
            if key in usable_metadata_keys:
                usable_metadata_keys.remove(key)
    elif mode == MetadataMode.EMBED:
        for key in self.excluded_embed_metadata_keys:
            if key in usable_metadata_keys:
                usable_metadata_keys.remove(key)

    return self.metadata_seperator.join(
        [
            self.metadata_template.format(key=key, value=str(value))
            for key, value in self.metadata.items()
            if key in usable_metadata_keys
        ]
    )

```
  
---|---  
###  set_content #
```
set_content(value: str) -> None

```

Set the content of the node.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def set_content(self, value: str) -> None:
    """Set the content of the node."""
    self.text = value

```
  
---|---  
###  get_node_info #
```
get_node_info() -> Dict[str, Any]

```

Get node info.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def get_node_info(self) -> Dict[str, Any]:
    """Get node info."""
    return {"start": self.start_char_idx, "end": self.end_char_idx}

```
  
---|---  
##  ImageNode #
Bases: `TextNode`
Node with image.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`image` |  `str | None` |  |  `None`  
`image_path` |  `str | None` |  |  `None`  
`image_url` |  `str | None` |  |  `None`  
`image_mimetype` |  `str | None` |  |  `None`  
`text_embedding` |  `List[float] | None` |  Text embedding of image node, if text field is filled out |  `None`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class ImageNode(TextNode):
    """Node with image."""

    # TODO: store reference instead of actual image
    # base64 encoded image str
    image: Optional[str] = None
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    image_mimetype: Optional[str] = None
    text_embedding: Optional[List[float]] = Field(
        default=None,
        description="Text embedding of image node, if text field is filled out",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Make ImageNode forward-compatible with Node by supporting 'image_resource' in the constructor."""
        if "image_resource" in kwargs:
            ir = kwargs.pop("image_resource")
            if isinstance(ir, MediaResource):
                kwargs["image_path"] = ir.path.as_posix() if ir.path else None
                kwargs["image_url"] = ir.url
                kwargs["image_mimetype"] = ir.mimetype
            else:
                kwargs["image_path"] = ir.get("path", None)
                kwargs["image_url"] = ir.get("url", None)
                kwargs["image_mimetype"] = ir.get("mimetype", None)

        mimetype = kwargs.get("image_mimetype")
        if not mimetype and kwargs.get("image_path") is not None:
            # guess mimetype from image_path
            extension = Path(kwargs["image_path"]).suffix.replace(".", "")
            if ftype := filetype.get_type(ext=extension):
                kwargs["image_mimetype"] = ftype.mime

        super().__init__(*args, **kwargs)

    @classmethod
    def get_type(cls) -> str:
        return ObjectType.IMAGE

    @classmethod
    def class_name(cls) -> str:
        return "ImageNode"

    def resolve_image(self) -> ImageType:
        """Resolve an image such that PIL can read it."""
        if self.image is not None:
            import base64

            return BytesIO(base64.b64decode(self.image))
        elif self.image_path is not None:
            return self.image_path
        elif self.image_url is not None:
            # load image from URL
            import requests

            response = requests.get(self.image_url)
            return BytesIO(response.content)
        else:
            raise ValueError("No image found in node.")

    @property
    def hash(self) -> str:
        """Get hash of node."""
        # doc identity depends on if image, image_path, or image_url is set
        image_str = self.image or "None"
        image_path_str = self.image_path or "None"
        image_url_str = self.image_url or "None"
        image_text = self.text or "None"
        doc_identity = f"{image_str}-{image_path_str}-{image_url_str}-{image_text}"
        return str(sha256(doc_identity.encode("utf-8", "surrogatepass")).hexdigest())

```
  
---|---  
###  hash `property` #
```
hash: str

```

Get hash of node.
###  resolve_image #
```
resolve_image() -> ImageType

```

Resolve an image such that PIL can read it.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def resolve_image(self) -> ImageType:
    """Resolve an image such that PIL can read it."""
    if self.image is not None:
        import base64

        return BytesIO(base64.b64decode(self.image))
    elif self.image_path is not None:
        return self.image_path
    elif self.image_url is not None:
        # load image from URL
        import requests

        response = requests.get(self.image_url)
        return BytesIO(response.content)
    else:
        raise ValueError("No image found in node.")

```
  
---|---  
##  IndexNode #
Bases: `TextNode`
Node with reference to any object.
This can include other indices, query engines, retrievers.
This can also include other nodes (though this is overlapping with `relationships` on the Node class).
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`index_id` |  `str` |  |  _required_  
`obj` |  `Any` |  |  `None`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class IndexNode(TextNode):
    """
    Node with reference to any object.

    This can include other indices, query engines, retrievers.

    This can also include other nodes (though this is overlapping with `relationships`
    on the Node class).

    """

    index_id: str
    obj: Any = None

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        from llama_index.core.storage.docstore.utils import doc_to_json

        data = super().dict(**kwargs)

        try:
            if self.obj is None:
                data["obj"] = None
            elif isinstance(self.obj, BaseNode):
                data["obj"] = doc_to_json(self.obj)
            elif isinstance(self.obj, BaseModel):
                data["obj"] = self.obj.model_dump()
            else:
                data["obj"] = json.dumps(self.obj)
        except Exception:
            raise ValueError("IndexNode obj is not serializable: " + str(self.obj))

        return data

    @classmethod
    def from_text_node(
        cls,
        node: TextNode,
        index_id: str,
    ) -> IndexNode:
        """Create index node from text node."""
        # copy all attributes from text node, add index id
        return cls(
            **node.dict(),
            index_id=index_id,
        )

    # TODO: return type here not supported by current mypy version
    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs: Any) -> Self:  # type: ignore
        output = super().from_dict(data, **kwargs)

        obj = data.get("obj")
        parsed_obj = None

        if isinstance(obj, str):
            parsed_obj = TextNode(text=obj)
        elif isinstance(obj, dict):
            from llama_index.core.storage.docstore.utils import json_to_doc

            # check if its a node, else assume stringable
            try:
                parsed_obj = json_to_doc(obj)  # type: ignore[assignment]
            except Exception:
                parsed_obj = TextNode(text=str(obj))

        output.obj = parsed_obj

        return output

    @classmethod
    def get_type(cls) -> str:
        return ObjectType.INDEX

    @classmethod
    def class_name(cls) -> str:
        return "IndexNode"

```
  
---|---  
###  from_text_node `classmethod` #
```
from_text_node(node: TextNode, index_id: str) -> IndexNode

```

Create index node from text node.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def from_text_node(
    cls,
    node: TextNode,
    index_id: str,
) -> IndexNode:
    """Create index node from text node."""
    # copy all attributes from text node, add index id
    return cls(
        **node.dict(),
        index_id=index_id,
    )

```
  
---|---  
##  NodeWithScore #
Bases: `BaseComponent`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node` |  `BaseNode` |  |  _required_  
`score` |  `float | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class NodeWithScore(BaseComponent):
    node: SerializeAsAny[BaseNode]
    score: Optional[float] = None

    def __str__(self) -> str:
        score_str = "None" if self.score is None else f"{self.score: 0.3f}"
        return f"{self.node}\nScore: {score_str}\n"

    def get_score(self, raise_error: bool = False) -> float:
        """Get score."""
        if self.score is None:
            if raise_error:
                raise ValueError("Score not set.")
            else:
                return 0.0
        else:
            return self.score

    @classmethod
    def class_name(cls) -> str:
        return "NodeWithScore"

    ##### pass through methods to BaseNode #####
    @property
    def node_id(self) -> str:
        return self.node.node_id

    @property
    def id_(self) -> str:
        return self.node.id_

    @property
    def text(self) -> str:
        if isinstance(self.node, TextNode):
            return self.node.text
        else:
            raise ValueError("Node must be a TextNode to get text.")

    @property
    def metadata(self) -> Dict[str, Any]:
        return self.node.metadata

    @property
    def embedding(self) -> Optional[List[float]]:
        return self.node.embedding

    def get_text(self) -> str:
        if isinstance(self.node, TextNode):
            return self.node.get_text()
        else:
            raise ValueError("Node must be a TextNode to get text.")

    def get_content(self, metadata_mode: MetadataMode = MetadataMode.NONE) -> str:
        return self.node.get_content(metadata_mode=metadata_mode)

    def get_embedding(self) -> List[float]:
        return self.node.get_embedding()

```
  
---|---  
###  get_score #
```
get_score(raise_error: bool = False) -> float

```

Get score.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def get_score(self, raise_error: bool = False) -> float:
    """Get score."""
    if self.score is None:
        if raise_error:
            raise ValueError("Score not set.")
        else:
            return 0.0
    else:
        return self.score

```
  
---|---  
##  Document #
Bases: `Node`
Generic interface for a data document.
This document connects to data sources.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class Document(Node):
    """
    Generic interface for a data document.

    This document connects to data sources.
    """

    def __init__(self, **data: Any) -> None:
        """
        Keeps backward compatibility with old 'Document' versions.

        If 'text' was passed, store it in 'text_resource'.
        If 'doc_id' was passed, store it in 'id_'.
        If 'extra_info' was passed, store it in 'metadata'.
        """
        if "doc_id" in data:
            value = data.pop("doc_id")
            if "id_" in data:
                msg = "'doc_id' is deprecated and 'id_' will be used instead"
                logging.warning(msg)
            else:
                data["id_"] = value

        if "extra_info" in data:
            value = data.pop("extra_info")
            if "metadata" in data:
                msg = "'extra_info' is deprecated and 'metadata' will be used instead"
                logging.warning(msg)
            else:
                data["metadata"] = value

        if data.get("text"):
            text = data.pop("text")
            if "text_resource" in data:
                text_resource = (
                    data["text_resource"]
                    if isinstance(data["text_resource"], MediaResource)
                    else MediaResource.model_validate(data["text_resource"])
                )
                if (text_resource.text or "").strip() != text.strip():
                    msg = (
                        "'text' is deprecated and 'text_resource' will be used instead"
                    )
                    logging.warning(msg)
            else:
                data["text_resource"] = MediaResource(text=text)

        super().__init__(**data)

    @model_serializer(mode="wrap")
    def custom_model_dump(
        self, handler: SerializerFunctionWrapHandler, info: SerializationInfo
    ) -> Dict[str, Any]:
        """For full backward compatibility with the text field, we customize the model serializer."""
        data = super().custom_model_dump(handler, info)
        exclude_set = set(info.exclude or [])
        if "text" not in exclude_set:
            data["text"] = self.text
        return data

    @property
    def text(self) -> str:
        """Provided for backward compatibility, it returns the content of text_resource."""
        return self.get_content()

    @classmethod
    def get_type(cls) -> str:
        """Get Document type."""
        return ObjectType.DOCUMENT

    @property
    def doc_id(self) -> str:
        """Get document ID."""
        return self.id_

    @doc_id.setter
    def doc_id(self, id_: str) -> None:
        self.id_ = id_

    def __str__(self) -> str:
        source_text_truncated = truncate_text(
            self.get_content().strip(), TRUNCATE_LENGTH
        )
        source_text_wrapped = textwrap.fill(
            f"Text: {source_text_truncated}\n", width=WRAP_WIDTH
        )
        return f"Doc ID: {self.doc_id}\n{source_text_wrapped}"

    @deprecated(
        version="0.12.2",
        reason="'get_doc_id' is deprecated, access the 'id_' property instead.",
    )
    def get_doc_id(self) -> str:  # pragma: nocover
        return self.id_

    def to_langchain_format(self) -> LCDocument:
        """Convert struct to LangChain document format."""
        from llama_index.core.bridge.langchain import (
            Document as LCDocument,  # type: ignore
        )

        metadata = self.metadata or {}
        return LCDocument(page_content=self.text, metadata=metadata, id=self.id_)

    @classmethod
    def from_langchain_format(cls, doc: LCDocument) -> Document:
        """Convert struct from LangChain document format."""
        if doc.id:
            return cls(text=doc.page_content, metadata=doc.metadata, id_=doc.id)
        return cls(text=doc.page_content, metadata=doc.metadata)

    def to_haystack_format(self) -> HaystackDocument:
        """Convert struct to Haystack document format."""
        from haystack import Document as HaystackDocument  # type: ignore

        return HaystackDocument(
            content=self.text, meta=self.metadata, embedding=self.embedding, id=self.id_
        )

    @classmethod
    def from_haystack_format(cls, doc: HaystackDocument) -> Document:
        """Convert struct from Haystack document format."""
        return cls(
            text=doc.content, metadata=doc.meta, embedding=doc.embedding, id_=doc.id
        )

    def to_embedchain_format(self) -> Dict[str, Any]:
        """Convert struct to EmbedChain document format."""
        return {
            "doc_id": self.id_,
            "data": {"content": self.text, "meta_data": self.metadata},
        }

    @classmethod
    def from_embedchain_format(cls, doc: Dict[str, Any]) -> Document:
        """Convert struct from EmbedChain document format."""
        return cls(
            text=doc["data"]["content"],
            metadata=doc["data"]["meta_data"],
            id_=doc["doc_id"],
        )

    def to_semantic_kernel_format(self) -> MemoryRecord:
        """Convert struct to Semantic Kernel document format."""
        import numpy as np
        from semantic_kernel.memory.memory_record import MemoryRecord  # type: ignore

        return MemoryRecord(
            id=self.id_,
            text=self.text,
            additional_metadata=self.get_metadata_str(),
            embedding=np.array(self.embedding) if self.embedding else None,
        )

    @classmethod
    def from_semantic_kernel_format(cls, doc: MemoryRecord) -> Document:
        """Convert struct from Semantic Kernel document format."""
        return cls(
            text=doc._text,
            metadata={"additional_metadata": doc._additional_metadata},
            embedding=doc._embedding.tolist() if doc._embedding is not None else None,
            id_=doc._id,
        )

    def to_vectorflow(self, client: Any) -> None:
        """Send a document to vectorflow, since they don't have a document object."""
        # write document to temp file
        import tempfile

        with tempfile.NamedTemporaryFile() as f:
            f.write(self.text.encode("utf-8"))
            f.flush()
            client.embed(f.name)

    @classmethod
    def example(cls) -> Document:
        return Document(
            text=SAMPLE_TEXT,
            metadata={"filename": "README.md", "category": "codebase"},
        )

    @classmethod
    def class_name(cls) -> str:
        return "Document"

    def to_cloud_document(self) -> CloudDocument:
        """Convert to LlamaCloud document type."""
        from llama_cloud.types.cloud_document import CloudDocument  # type: ignore

        return CloudDocument(
            text=self.text,
            metadata=self.metadata,
            excluded_embed_metadata_keys=self.excluded_embed_metadata_keys,
            excluded_llm_metadata_keys=self.excluded_llm_metadata_keys,
            id=self.id_,
        )

    @classmethod
    def from_cloud_document(
        cls,
        doc: CloudDocument,
    ) -> Document:
        """Convert from LlamaCloud document type."""
        return Document(
            text=doc.text,
            metadata=doc.metadata,
            excluded_embed_metadata_keys=doc.excluded_embed_metadata_keys,
            excluded_llm_metadata_keys=doc.excluded_llm_metadata_keys,
            id_=doc.id,
        )

```
  
---|---  
###  text `property` #
```
text: str

```

Provided for backward compatibility, it returns the content of text_resource.
###  doc_id `property` `writable` #
```
doc_id: str

```

Get document ID.
###  custom_model_dump #
```
custom_model_dump(handler: SerializerFunctionWrapHandler, info: SerializationInfo) -> Dict[str, Any]

```

For full backward compatibility with the text field, we customize the model serializer.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@model_serializer(mode="wrap")
def custom_model_dump(
    self, handler: SerializerFunctionWrapHandler, info: SerializationInfo
) -> Dict[str, Any]:
    """For full backward compatibility with the text field, we customize the model serializer."""
    data = super().custom_model_dump(handler, info)
    exclude_set = set(info.exclude or [])
    if "text" not in exclude_set:
        data["text"] = self.text
    return data

```
  
---|---  
###  get_type `classmethod` #
```
get_type() -> str

```

Get Document type.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def get_type(cls) -> str:
    """Get Document type."""
    return ObjectType.DOCUMENT

```
  
---|---  
###  to_langchain_format #
```
to_langchain_format() -> Document

```

Convert struct to LangChain document format.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def to_langchain_format(self) -> LCDocument:
    """Convert struct to LangChain document format."""
    from llama_index.core.bridge.langchain import (
        Document as LCDocument,  # type: ignore
    )

    metadata = self.metadata or {}
    return LCDocument(page_content=self.text, metadata=metadata, id=self.id_)

```
  
---|---  
###  from_langchain_format `classmethod` #
```
from_langchain_format(doc: Document) -> Document

```

Convert struct from LangChain document format.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def from_langchain_format(cls, doc: LCDocument) -> Document:
    """Convert struct from LangChain document format."""
    if doc.id:
        return cls(text=doc.page_content, metadata=doc.metadata, id_=doc.id)
    return cls(text=doc.page_content, metadata=doc.metadata)

```
  
---|---  
###  to_haystack_format #
```
to_haystack_format() -> Document

```

Convert struct to Haystack document format.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def to_haystack_format(self) -> HaystackDocument:
    """Convert struct to Haystack document format."""
    from haystack import Document as HaystackDocument  # type: ignore

    return HaystackDocument(
        content=self.text, meta=self.metadata, embedding=self.embedding, id=self.id_
    )

```
  
---|---  
###  from_haystack_format `classmethod` #
```
from_haystack_format(doc: Document) -> Document

```

Convert struct from Haystack document format.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def from_haystack_format(cls, doc: HaystackDocument) -> Document:
    """Convert struct from Haystack document format."""
    return cls(
        text=doc.content, metadata=doc.meta, embedding=doc.embedding, id_=doc.id
    )

```
  
---|---  
###  to_embedchain_format #
```
to_embedchain_format() -> Dict[str, Any]

```

Convert struct to EmbedChain document format.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def to_embedchain_format(self) -> Dict[str, Any]:
    """Convert struct to EmbedChain document format."""
    return {
        "doc_id": self.id_,
        "data": {"content": self.text, "meta_data": self.metadata},
    }

```
  
---|---  
###  from_embedchain_format `classmethod` #
```
from_embedchain_format(doc: Dict[str, Any]) -> Document

```

Convert struct from EmbedChain document format.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def from_embedchain_format(cls, doc: Dict[str, Any]) -> Document:
    """Convert struct from EmbedChain document format."""
    return cls(
        text=doc["data"]["content"],
        metadata=doc["data"]["meta_data"],
        id_=doc["doc_id"],
    )

```
  
---|---  
###  to_semantic_kernel_format #
```
to_semantic_kernel_format() -> MemoryRecord

```

Convert struct to Semantic Kernel document format.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def to_semantic_kernel_format(self) -> MemoryRecord:
    """Convert struct to Semantic Kernel document format."""
    import numpy as np
    from semantic_kernel.memory.memory_record import MemoryRecord  # type: ignore

    return MemoryRecord(
        id=self.id_,
        text=self.text,
        additional_metadata=self.get_metadata_str(),
        embedding=np.array(self.embedding) if self.embedding else None,
    )

```
  
---|---  
###  from_semantic_kernel_format `classmethod` #
```
from_semantic_kernel_format(doc: MemoryRecord) -> Document

```

Convert struct from Semantic Kernel document format.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def from_semantic_kernel_format(cls, doc: MemoryRecord) -> Document:
    """Convert struct from Semantic Kernel document format."""
    return cls(
        text=doc._text,
        metadata={"additional_metadata": doc._additional_metadata},
        embedding=doc._embedding.tolist() if doc._embedding is not None else None,
        id_=doc._id,
    )

```
  
---|---  
###  to_vectorflow #
```
to_vectorflow(client: Any) -> None

```

Send a document to vectorflow, since they don't have a document object.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def to_vectorflow(self, client: Any) -> None:
    """Send a document to vectorflow, since they don't have a document object."""
    # write document to temp file
    import tempfile

    with tempfile.NamedTemporaryFile() as f:
        f.write(self.text.encode("utf-8"))
        f.flush()
        client.embed(f.name)

```
  
---|---  
###  to_cloud_document #
```
to_cloud_document() -> CloudDocument

```

Convert to LlamaCloud document type.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def to_cloud_document(self) -> CloudDocument:
    """Convert to LlamaCloud document type."""
    from llama_cloud.types.cloud_document import CloudDocument  # type: ignore

    return CloudDocument(
        text=self.text,
        metadata=self.metadata,
        excluded_embed_metadata_keys=self.excluded_embed_metadata_keys,
        excluded_llm_metadata_keys=self.excluded_llm_metadata_keys,
        id=self.id_,
    )

```
  
---|---  
###  from_cloud_document `classmethod` #
```
from_cloud_document(doc: CloudDocument) -> Document

```

Convert from LlamaCloud document type.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@classmethod
def from_cloud_document(
    cls,
    doc: CloudDocument,
) -> Document:
    """Convert from LlamaCloud document type."""
    return Document(
        text=doc.text,
        metadata=doc.metadata,
        excluded_embed_metadata_keys=doc.excluded_embed_metadata_keys,
        excluded_llm_metadata_keys=doc.excluded_llm_metadata_keys,
        id_=doc.id,
    )

```
  
---|---  
##  ImageDocument #
Bases: `Document`
Backward compatible wrapper around Document containing an image.
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
class ImageDocument(Document):
    """Backward compatible wrapper around Document containing an image."""

    def __init__(self, **kwargs: Any) -> None:
        image = kwargs.pop("image", None)
        image_path = kwargs.pop("image_path", None)
        image_url = kwargs.pop("image_url", None)
        image_mimetype = kwargs.pop("image_mimetype", None)
        text_embedding = kwargs.pop("text_embedding", None)

        if image:
            kwargs["image_resource"] = MediaResource(
                data=image, mimetype=image_mimetype
            )
        elif image_path:
            if not is_image_pil(image_path):
                raise ValueError("The specified file path is not an accessible image")
            kwargs["image_resource"] = MediaResource(
                path=image_path, mimetype=image_mimetype
            )
        elif image_url:
            if not is_image_url_pil(image_url):
                raise ValueError("The specified URL is not an accessible image")
            kwargs["image_resource"] = MediaResource(
                url=image_url, mimetype=image_mimetype
            )

        super().__init__(**kwargs)

    @property
    def image(self) -> str | None:
        if self.image_resource and self.image_resource.data:
            return self.image_resource.data.decode("utf-8")
        return None

    @image.setter
    def image(self, image: str) -> None:
        self.image_resource = MediaResource(data=image.encode("utf-8"))

    @property
    def image_path(self) -> str | None:
        if self.image_resource and self.image_resource.path:
            return str(self.image_resource.path)
        return None

    @image_path.setter
    def image_path(self, image_path: str) -> None:
        self.image_resource = MediaResource(path=Path(image_path))

    @property
    def image_url(self) -> str | None:
        if self.image_resource and self.image_resource.url:
            return str(self.image_resource.url)
        return None

    @image_url.setter
    def image_url(self, image_url: str) -> None:
        self.image_resource = MediaResource(url=AnyUrl(url=image_url))

    @property
    def image_mimetype(self) -> str | None:
        if self.image_resource:
            return self.image_resource.mimetype
        return None

    @image_mimetype.setter
    def image_mimetype(self, image_mimetype: str) -> None:
        if self.image_resource:
            self.image_resource.mimetype = image_mimetype

    @property
    def text_embedding(self) -> list[float] | None:
        if self.text_resource and self.text_resource.embeddings:
            return self.text_resource.embeddings.get("dense")
        return None

    @text_embedding.setter
    def text_embedding(self, embeddings: list[float]) -> None:
        if self.text_resource:
            if self.text_resource.embeddings is None:
                self.text_resource.embeddings = {}
            self.text_resource.embeddings["dense"] = embeddings

    @classmethod
    def class_name(cls) -> str:
        return "ImageDocument"

    def resolve_image(self, as_base64: bool = False) -> BytesIO:
        """
        Resolve an image such that PIL can read it.

        Args:
            as_base64 (bool): whether the resolved image should be returned as base64-encoded bytes

        """
        if self.image_resource is None:
            return BytesIO()

        if self.image_resource.data is not None:
            if as_base64:
                return BytesIO(self.image_resource.data)
            return BytesIO(base64.b64decode(self.image_resource.data))
        elif self.image_resource.path is not None:
            img_bytes = self.image_resource.path.read_bytes()
            if as_base64:
                return BytesIO(base64.b64encode(img_bytes))
            return BytesIO(img_bytes)
        elif self.image_resource.url is not None:
            # load image from URL
            response = requests.get(str(self.image_resource.url))
            img_bytes = response.content
            if as_base64:
                return BytesIO(base64.b64encode(img_bytes))
            return BytesIO(img_bytes)
        else:
            raise ValueError("No image found in the chat message!")

```
  
---|---  
###  resolve_image #
```
resolve_image(as_base64: bool = False) -> BytesIO

```

Resolve an image such that PIL can read it.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`as_base64` |  `bool` |  whether the resolved image should be returned as base64-encoded bytes |  `False`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
def resolve_image(self, as_base64: bool = False) -> BytesIO:
    """
    Resolve an image such that PIL can read it.

    Args:
        as_base64 (bool): whether the resolved image should be returned as base64-encoded bytes

    """
    if self.image_resource is None:
        return BytesIO()

    if self.image_resource.data is not None:
        if as_base64:
            return BytesIO(self.image_resource.data)
        return BytesIO(base64.b64decode(self.image_resource.data))
    elif self.image_resource.path is not None:
        img_bytes = self.image_resource.path.read_bytes()
        if as_base64:
            return BytesIO(base64.b64encode(img_bytes))
        return BytesIO(img_bytes)
    elif self.image_resource.url is not None:
        # load image from URL
        response = requests.get(str(self.image_resource.url))
        img_bytes = response.content
        if as_base64:
            return BytesIO(base64.b64encode(img_bytes))
        return BytesIO(img_bytes)
    else:
        raise ValueError("No image found in the chat message!")

```
  
---|---  
##  QueryBundle `dataclass` #
Bases: `DataClassJsonMixin`
Query bundle.
This dataclass contains the original query string and associated transformations.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_str` |  `str` |  the original user-specified query string. This is currently used by all non embedding-based queries. |  _required_  
`custom_embedding_strs` |  `list[str]` |  list of strings used for embedding the query. This is currently used by all embedding-based queries. |  `None`  
`embedding` |  `list[float]` |  the stored embedding for the query. |  `None`  
`image_path` |  `str` |  |  `None`  
Source code in `llama-index-core/llama_index/core/schema.py`

| ```
@dataclass
class QueryBundle(DataClassJsonMixin):
    """
    Query bundle.

    This dataclass contains the original query string and associated transformations.

    Args:
        query_str (str): the original user-specified query string.
            This is currently used by all non embedding-based queries.
        custom_embedding_strs (list[str]): list of strings used for embedding the query.
            This is currently used by all embedding-based queries.
        embedding (list[float]): the stored embedding for the query.

    """

    query_str: str
    # using single image path as query input
    image_path: Optional[str] = None
    custom_embedding_strs: Optional[List[str]] = None
    embedding: Optional[List[float]] = None

    @property
    def embedding_strs(self) -> List[str]:
        """Use custom embedding strs if specified, otherwise use query str."""
        if self.custom_embedding_strs is None:
            if len(self.query_str) == 0:
                return []
            return [self.query_str]
        else:
            return self.custom_embedding_strs

    @property
    def embedding_image(self) -> List[ImageType]:
        """Use image path for image retrieval."""
        if self.image_path is None:
            return []
        return [self.image_path]

    def __str__(self) -> str:
        """Convert to string representation."""
        return self.query_str

```
  
---|---  
###  embedding_strs `property` #
```
embedding_strs: List[str]

```

Use custom embedding strs if specified, otherwise use query str.
###  embedding_image `property` #
```
embedding_image: List[ImageType]

```

Use image path for image retrieval.
