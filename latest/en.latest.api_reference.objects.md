# Index
LlamaIndex objects.
##  ObjectIndex #
Bases: `Generic[OT]`
Object index.
Source code in `llama-index-core/llama_index/core/objects/base.py`

| ```
class ObjectIndex(Generic[OT]):
    """Object index."""

    def __init__(
        self, index: BaseIndex, object_node_mapping: BaseObjectNodeMapping
    ) -> None:
        self._index = index
        self._object_node_mapping = object_node_mapping

    @property
    def index(self) -> BaseIndex:
        """Index."""
        return self._index

    @property
    def object_node_mapping(self) -> BaseObjectNodeMapping:
        """Object node mapping."""
        return self._object_node_mapping

    @classmethod
    def from_objects(
        cls,
        objects: Sequence[OT],
        object_mapping: Optional[BaseObjectNodeMapping] = None,
        from_node_fn: Optional[Callable[[BaseNode], OT]] = None,
        to_node_fn: Optional[Callable[[OT], BaseNode]] = None,
        index_cls: Type[BaseIndex] = VectorStoreIndex,
        **index_kwargs: Any,
    ) -> "ObjectIndex":
        from llama_index.core.objects.utils import get_object_mapping

        # pick the best mapping if not provided
        if object_mapping is None:
            object_mapping = get_object_mapping(
                objects,
                from_node_fn=from_node_fn,
                to_node_fn=to_node_fn,
            )

        nodes = object_mapping.to_nodes(objects)
        index = index_cls(nodes, **index_kwargs)
        return cls(index, object_mapping)

    @classmethod
    def from_objects_and_index(
        cls,
        objects: Sequence[OT],
        index: BaseIndex,
        object_mapping: Optional[BaseObjectNodeMapping] = None,
        from_node_fn: Optional[Callable[[BaseNode], OT]] = None,
        to_node_fn: Optional[Callable[[OT], BaseNode]] = None,
    ) -> "ObjectIndex":
        from llama_index.core.objects.utils import get_object_mapping

        # pick the best mapping if not provided
        if object_mapping is None:
            object_mapping = get_object_mapping(
                objects,
                from_node_fn=from_node_fn,
                to_node_fn=to_node_fn,
            )

        return cls(index, object_mapping)

    def insert_object(self, obj: Any) -> None:
        self._object_node_mapping.add_object(obj)
        node = self._object_node_mapping.to_node(obj)
        self._index.insert_nodes([node])

    def as_retriever(
        self,
        node_postprocessors: Optional[List[BaseNodePostprocessor]] = None,
        **kwargs: Any,
    ) -> ObjectRetriever:
        return ObjectRetriever(
            retriever=self._index.as_retriever(**kwargs),
            object_node_mapping=self._object_node_mapping,
            node_postprocessors=node_postprocessors,
        )

    def as_node_retriever(self, **kwargs: Any) -> BaseRetriever:
        return self._index.as_retriever(**kwargs)

    def persist(
        self,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        obj_node_mapping_fname: str = DEFAULT_PERSIST_FNAME,
    ) -> None:
        # try to persist object node mapping
        try:
            self._object_node_mapping.persist(
                persist_dir=persist_dir, obj_node_mapping_fname=obj_node_mapping_fname
            )
        except (NotImplementedError, pickle.PickleError) as err:
            warnings.warn(
                (
                    "Unable to persist ObjectNodeMapping. You will need to "
                    "reconstruct the same object node mapping to build this ObjectIndex"
                ),
                stacklevel=2,
            )
        self._index._storage_context.persist(persist_dir=persist_dir)

    @classmethod
    def from_persist_dir(
        cls,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        object_node_mapping: Optional[BaseObjectNodeMapping] = None,
    ) -> "ObjectIndex":
        from llama_index.core.indices import load_index_from_storage

        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(storage_context)
        if object_node_mapping:
            return cls(index=index, object_node_mapping=object_node_mapping)
        else:
            # try to load object_node_mapping
            # assume SimpleObjectNodeMapping for simplicity as its only subclass
            # that supports this method
            try:
                object_node_mapping = SimpleObjectNodeMapping.from_persist_dir(
                    persist_dir=persist_dir
                )
            except Exception as err:
                raise Exception(
                    "Unable to load from persist dir. The object_node_mapping cannot be loaded."
                ) from err
            else:
                return cls(index=index, object_node_mapping=object_node_mapping)

```
  
---|---  
###  index `property` #
```
index: BaseIndex

```

Index.
###  object_node_mapping `property` #
```
object_node_mapping: BaseObjectNodeMapping

```

Object node mapping.
##  ObjectRetriever #
Bases: `Generic[OT]`
Object retriever.
Source code in `llama-index-core/llama_index/core/objects/base.py`

| ```
class ObjectRetriever(Generic[OT]):
    """Object retriever."""

    def __init__(
        self,
        retriever: BaseRetriever,
        object_node_mapping: BaseObjectNodeMapping[OT],
        node_postprocessors: Optional[List[BaseNodePostprocessor]] = None,
    ):
        self._retriever = retriever
        self._object_node_mapping = object_node_mapping
        self._node_postprocessors = node_postprocessors or []

    @property
    def retriever(self) -> BaseRetriever:
        """Retriever."""
        return self._retriever

    @property
    def object_node_mapping(self) -> BaseObjectNodeMapping[OT]:
        """Object node mapping."""
        return self._object_node_mapping

    @property
    def node_postprocessors(self) -> List[BaseNodePostprocessor]:
        """Node postprocessors."""
        return self._node_postprocessors

    def retrieve(self, str_or_query_bundle: QueryType) -> List[OT]:
        if isinstance(str_or_query_bundle, str):
            query_bundle = QueryBundle(query_str=str_or_query_bundle)
        else:
            query_bundle = str_or_query_bundle

        nodes = self._retriever.retrieve(query_bundle)
        for node_postprocessor in self._node_postprocessors:
            nodes = node_postprocessor.postprocess_nodes(
                nodes, query_bundle=query_bundle
            )

        return [self._object_node_mapping.from_node(node.node) for node in nodes]

    async def aretrieve(self, str_or_query_bundle: QueryType) -> List[OT]:
        if isinstance(str_or_query_bundle, str):
            query_bundle = QueryBundle(query_str=str_or_query_bundle)
        else:
            query_bundle = str_or_query_bundle

        nodes = await self._retriever.aretrieve(query_bundle)
        for node_postprocessor in self._node_postprocessors:
            nodes = node_postprocessor.postprocess_nodes(
                nodes, query_bundle=query_bundle
            )

        return [self._object_node_mapping.from_node(node.node) for node in nodes]

```
  
---|---  
###  retriever `property` #
```
retriever: BaseRetriever

```

Retriever.
###  object_node_mapping `property` #
```
object_node_mapping: BaseObjectNodeMapping[OT]

```

Object node mapping.
###  node_postprocessors `property` #
```
node_postprocessors: List[BaseNodePostprocessor]

```

Node postprocessors.
##  SimpleObjectNodeMapping #
Bases: `BaseObjectNodeMapping[Any]`
General node mapping that works for any obj.
More specifically, any object with a meaningful string representation.
Source code in `llama-index-core/llama_index/core/objects/base_node_mapping.py`

| ```
class SimpleObjectNodeMapping(BaseObjectNodeMapping[Any]):
    """
    General node mapping that works for any obj.

    More specifically, any object with a meaningful string representation.

    """

    def __init__(self, objs: Optional[Sequence[Any]] = None) -> None:
        objs = objs or []
        for obj in objs:
            self.validate_object(obj)
        self._objs = {hash(str(obj)): obj for obj in objs}

    @classmethod
    def from_objects(
        cls, objs: Sequence[Any], *args: Any, **kwargs: Any
    ) -> "SimpleObjectNodeMapping":
        return cls(objs)

    @property
    def obj_node_mapping(self) -> Dict[int, Any]:
        return self._objs

    @obj_node_mapping.setter
    def obj_node_mapping(self, mapping: Dict[int, Any]) -> None:
        self._objs = mapping

    def _add_object(self, obj: Any) -> None:
        self._objs[hash(str(obj))] = obj

    def to_node(self, obj: Any) -> TextNode:
        return TextNode(id_=str(hash(str(obj))), text=str(obj))

    def _from_node(self, node: BaseNode) -> Any:
        return self._objs[hash(node.get_content(metadata_mode=MetadataMode.NONE))]

    def persist(
        self,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        obj_node_mapping_fname: str = DEFAULT_PERSIST_FNAME,
    ) -> None:
        """
        Persist object node mapping.

        NOTE: This may fail depending on whether the object types are
        pickle-able.
        """
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir)
        obj_node_mapping_path = concat_dirs(persist_dir, obj_node_mapping_fname)
        try:
            with open(obj_node_mapping_path, "wb") as f:
                pickle.dump(self, f)
        except pickle.PickleError as err:
            raise ValueError("Objs is not pickleable") from err

    @classmethod
    def from_persist_dir(
        cls,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        obj_node_mapping_fname: str = DEFAULT_PERSIST_FNAME,
    ) -> "SimpleObjectNodeMapping":
        obj_node_mapping_path = concat_dirs(persist_dir, obj_node_mapping_fname)
        try:
            with open(obj_node_mapping_path, "rb") as f:
                simple_object_node_mapping = pickle.load(f)
        except pickle.PickleError as err:
            raise ValueError("Objs cannot be loaded.") from err
        return simple_object_node_mapping

```
  
---|---  
###  persist #
```
persist(persist_dir: str = DEFAULT_PERSIST_DIR, obj_node_mapping_fname: str = DEFAULT_PERSIST_FNAME) -> None

```

Persist object node mapping.
NOTE: This may fail depending on whether the object types are pickle-able.
Source code in `llama-index-core/llama_index/core/objects/base_node_mapping.py`

| ```
def persist(
    self,
    persist_dir: str = DEFAULT_PERSIST_DIR,
    obj_node_mapping_fname: str = DEFAULT_PERSIST_FNAME,
) -> None:
    """
    Persist object node mapping.

    NOTE: This may fail depending on whether the object types are
    pickle-able.
    """
    if not os.path.exists(persist_dir):
        os.makedirs(persist_dir)
    obj_node_mapping_path = concat_dirs(persist_dir, obj_node_mapping_fname)
    try:
        with open(obj_node_mapping_path, "wb") as f:
            pickle.dump(self, f)
    except pickle.PickleError as err:
        raise ValueError("Objs is not pickleable") from err

```
  
---|---  
##  SQLTableNodeMapping #
Bases: `BaseObjectNodeMapping[SQLTableSchema]`
SQL Table node mapping.
Source code in `llama-index-core/llama_index/core/objects/table_node_mapping.py`

| ```
class SQLTableNodeMapping(BaseObjectNodeMapping[SQLTableSchema]):
    """SQL Table node mapping."""

    def __init__(self, sql_database: SQLDatabase) -> None:
        self._sql_database = sql_database

    @classmethod
    def from_objects(
        cls,
        objs: Sequence[SQLTableSchema],
        *args: Any,
        sql_database: Optional[SQLDatabase] = None,
        **kwargs: Any,
    ) -> "BaseObjectNodeMapping":
        """Initialize node mapping."""
        if sql_database is None:
            raise ValueError("Must provide sql_database")
        # ignore objs, since we are building from sql_database
        return cls(sql_database)

    def _add_object(self, obj: SQLTableSchema) -> None:
        raise NotImplementedError

    def to_node(self, obj: SQLTableSchema) -> TextNode:
        """To node."""
        # taken from existing schema logic
        table_text = (
            f"Schema of table {obj.table_name}:\n"
            f"{self._sql_database.get_single_table_info(obj.table_name)}\n"
        )

        metadata = {"name": obj.table_name}

        if obj.context_str is not None:
            table_text += f"Context of table {obj.table_name}:\n"
            table_text += obj.context_str
            metadata["context"] = obj.context_str

        table_identity = f"{obj.table_name}{obj.context_str}"

        return TextNode(
            id_=str(uuid.uuid5(namespace=uuid.NAMESPACE_DNS, name=table_identity)),
            text=table_text,
            metadata=metadata,
            excluded_embed_metadata_keys=["name", "context"],
            excluded_llm_metadata_keys=["name", "context"],
        )

    def _from_node(self, node: BaseNode) -> SQLTableSchema:
        """From node."""
        if node.metadata is None:
            raise ValueError("Metadata must be set")
        return SQLTableSchema(
            table_name=node.metadata["name"], context_str=node.metadata.get("context")
        )

    @property
    def obj_node_mapping(self) -> Dict[int, Any]:
        """The mapping data structure between node and object."""
        raise NotImplementedError("Subclasses should implement this!")

    def persist(
        self, persist_dir: str = ..., obj_node_mapping_fname: str = ...
    ) -> None:
        """Persist objs."""
        raise NotImplementedError("Subclasses should implement this!")

    @classmethod
    def from_persist_dir(
        cls,
        persist_dir: str = DEFAULT_PERSIST_DIR,
        obj_node_mapping_fname: str = DEFAULT_PERSIST_FNAME,
    ) -> "SQLTableNodeMapping":
        raise NotImplementedError(
            "This object node mapping does not support persist method."
        )

```
  
---|---  
###  obj_node_mapping `property` #
```
obj_node_mapping: Dict[int, Any]

```

The mapping data structure between node and object.
###  from_objects `classmethod` #
```
from_objects(objs: Sequence[SQLTableSchema], *args: Any, sql_database: Optional[SQLDatabase] = None, **kwargs: Any) -> BaseObjectNodeMapping

```

Initialize node mapping.
Source code in `llama-index-core/llama_index/core/objects/table_node_mapping.py`

| ```
@classmethod
def from_objects(
    cls,
    objs: Sequence[SQLTableSchema],
    *args: Any,
    sql_database: Optional[SQLDatabase] = None,
    **kwargs: Any,
) -> "BaseObjectNodeMapping":
    """Initialize node mapping."""
    if sql_database is None:
        raise ValueError("Must provide sql_database")
    # ignore objs, since we are building from sql_database
    return cls(sql_database)

```
  
---|---  
###  to_node #
```
to_node(obj: SQLTableSchema) -> TextNode

```

To node.
Source code in `llama-index-core/llama_index/core/objects/table_node_mapping.py`

| ```
def to_node(self, obj: SQLTableSchema) -> TextNode:
    """To node."""
    # taken from existing schema logic
    table_text = (
        f"Schema of table {obj.table_name}:\n"
        f"{self._sql_database.get_single_table_info(obj.table_name)}\n"
    )

    metadata = {"name": obj.table_name}

    if obj.context_str is not None:
        table_text += f"Context of table {obj.table_name}:\n"
        table_text += obj.context_str
        metadata["context"] = obj.context_str

    table_identity = f"{obj.table_name}{obj.context_str}"

    return TextNode(
        id_=str(uuid.uuid5(namespace=uuid.NAMESPACE_DNS, name=table_identity)),
        text=table_text,
        metadata=metadata,
        excluded_embed_metadata_keys=["name", "context"],
        excluded_llm_metadata_keys=["name", "context"],
    )

```
  
---|---  
###  persist #
```
persist(persist_dir: str = ..., obj_node_mapping_fname: str = ...) -> None

```

Persist objs.
Source code in `llama-index-core/llama_index/core/objects/table_node_mapping.py`

| ```
def persist(
    self, persist_dir: str = ..., obj_node_mapping_fname: str = ...
) -> None:
    """Persist objs."""
    raise NotImplementedError("Subclasses should implement this!")

```
  
---|---  
##  SQLTableSchema #
Bases: `BaseModel`
Lightweight representation of a SQL table.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`table_name` |  `str` |  |  _required_  
`context_str` |  `str | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/objects/table_node_mapping.py`

| ```
class SQLTableSchema(BaseModel):
    """Lightweight representation of a SQL table."""

    table_name: str
    context_str: Optional[str] = None

```
  
---|---  
##  SimpleQueryToolNodeMapping #
Bases: `BaseQueryToolNodeMapping`
Simple query tool mapping.
Source code in `llama-index-core/llama_index/core/objects/tool_node_mapping.py`

| ```
class SimpleQueryToolNodeMapping(BaseQueryToolNodeMapping):
    """Simple query tool mapping."""

    def __init__(self, objs: Optional[Sequence[QueryEngineTool]] = None) -> None:
        objs = objs or []
        self._tools = {tool.metadata.name: tool for tool in objs}

    def validate_object(self, obj: QueryEngineTool) -> None:
        if not isinstance(obj, QueryEngineTool):
            raise ValueError(f"Object must be of type {QueryEngineTool}")

    @classmethod
    def from_objects(
        cls, objs: Sequence[QueryEngineTool], *args: Any, **kwargs: Any
    ) -> "BaseObjectNodeMapping":
        return cls(objs)

    def _add_object(self, tool: QueryEngineTool) -> None:
        if tool.metadata.name is None:
            raise ValueError("Tool name must be set")
        self._tools[tool.metadata.name] = tool

    def to_node(self, obj: QueryEngineTool) -> TextNode:
        """To node."""
        return convert_tool_to_node(obj)

    def _from_node(self, node: BaseNode) -> QueryEngineTool:
        """From node."""
        if node.metadata is None:
            raise ValueError("Metadata must be set")
        return self._tools[node.metadata["name"]]

```
  
---|---  
###  to_node #
```
to_node(obj: QueryEngineTool) -> TextNode

```

To node.
Source code in `llama-index-core/llama_index/core/objects/tool_node_mapping.py`

| ```
def to_node(self, obj: QueryEngineTool) -> TextNode:
    """To node."""
    return convert_tool_to_node(obj)

```
  
---|---  
##  SimpleToolNodeMapping #
Bases: `BaseToolNodeMapping`
Simple Tool mapping.
In this setup, we assume that the tool name is unique, and that the list of all tools are stored in memory.
Source code in `llama-index-core/llama_index/core/objects/tool_node_mapping.py`

| ```
class SimpleToolNodeMapping(BaseToolNodeMapping):
    """
    Simple Tool mapping.

    In this setup, we assume that the tool name is unique, and
    that the list of all tools are stored in memory.

    """

    def __init__(self, objs: Optional[Sequence[BaseTool]] = None) -> None:
        objs = objs or []
        self._tools = {tool.metadata.name: tool for tool in objs}

    @classmethod
    def from_objects(
        cls, objs: Sequence[BaseTool], *args: Any, **kwargs: Any
    ) -> "BaseObjectNodeMapping":
        return cls(objs)

    def _add_object(self, tool: BaseTool) -> None:
        self._tools[tool.metadata.name] = tool

    def to_node(self, tool: BaseTool) -> TextNode:
        """To node."""
        return convert_tool_to_node(tool)

    def _from_node(self, node: BaseNode) -> BaseTool:
        """From node."""
        if node.metadata is None:
            raise ValueError("Metadata must be set")
        return self._tools[node.metadata["name"]]

```
  
---|---  
###  to_node #
```
to_node(tool: BaseTool) -> TextNode

```

To node.
Source code in `llama-index-core/llama_index/core/objects/tool_node_mapping.py`

| ```
def to_node(self, tool: BaseTool) -> TextNode:
    """To node."""
    return convert_tool_to_node(tool)

```
  
---|---
