# Index
##  DEFAULT_PERSIST_DIR `module-attribute` #
```
DEFAULT_PERSIST_DIR = './storage'

```

##  DEFAULT_PERSIST_FNAME `module-attribute` #
```
DEFAULT_PERSIST_FNAME = 'graph_store.json'

```

##  GraphStore #
Bases: `Protocol`
Abstract graph store protocol.
This protocol defines the interface for a graph store, which is responsible for storing and retrieving knowledge graph data.
Attributes:
Name | Type | Description  
---|---|---  
`client` |  `Any` |  Any: The client used to connect to the graph store.  
`get` |  `List[List[str]]` |  Callable[[str], List[List[str]]]: Get triplets for a given subject.  
`get_rel_map` |  `Dict[str, List[List[str]]]` |  Callable[[Optional[List[str]], int], Dict[str, List[List[str]]]]: Get subjects' rel map in max depth.  
`upsert_triplet` |  `None` |  Callable[[str, str, str], None]: Upsert a triplet.  
`delete` |  `None` |  Callable[[str, str, str], None]: Delete a triplet.  
`persist` |  `None` |  Callable[[str, Optional[fsspec.AbstractFileSystem]], None]: Persist the graph store to a file.  
`get_schema` |  `str` |  Callable[[bool], str]: Get the schema of the graph store.  
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@runtime_checkable
class GraphStore(Protocol):
    """
    Abstract graph store protocol.

    This protocol defines the interface for a graph store, which is responsible
    for storing and retrieving knowledge graph data.

    Attributes:
        client: Any: The client used to connect to the graph store.
        get: Callable[[str], List[List[str]]]: Get triplets for a given subject.
        get_rel_map: Callable[[Optional[List[str]], int], Dict[str, List[List[str]]]]:
            Get subjects' rel map in max depth.
        upsert_triplet: Callable[[str, str, str], None]: Upsert a triplet.
        delete: Callable[[str, str, str], None]: Delete a triplet.
        persist: Callable[[str, Optional[fsspec.AbstractFileSystem]], None]:
            Persist the graph store to a file.
        get_schema: Callable[[bool], str]: Get the schema of the graph store.

    """

    schema: str = ""

    @property
    def client(self) -> Any:
        """Get client."""
        ...

    def get(self, subj: str) -> List[List[str]]:
        """Get triplets."""
        ...

    def get_rel_map(
        self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
    ) -> Dict[str, List[List[str]]]:
        """Get depth-aware rel map."""
        ...

    def upsert_triplet(self, subj: str, rel: str, obj: str) -> None:
        """Add triplet."""
        ...

    def delete(self, subj: str, rel: str, obj: str) -> None:
        """Delete triplet."""
        ...

    def persist(
        self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> None:
        """Persist the graph store to a file."""
        return

    def get_schema(self, refresh: bool = False) -> str:
        """Get the schema of the graph store."""
        ...

    def query(self, query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any:
        """Query the graph store with statement and parameters."""
        ...

```
  
---|---  
###  client `property` #
```
client: Any

```

Get client.
###  get #
```
get(subj: str) -> List[List[str]]

```

Get triplets.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def get(self, subj: str) -> List[List[str]]:
    """Get triplets."""
    ...

```
  
---|---  
###  get_rel_map #
```
get_rel_map(subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30) -> Dict[str, List[List[str]]]

```

Get depth-aware rel map.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def get_rel_map(
    self, subjs: Optional[List[str]] = None, depth: int = 2, limit: int = 30
) -> Dict[str, List[List[str]]]:
    """Get depth-aware rel map."""
    ...

```
  
---|---  
###  upsert_triplet #
```
upsert_triplet(subj: str, rel: str, obj: str) -> None

```

Add triplet.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def upsert_triplet(self, subj: str, rel: str, obj: str) -> None:
    """Add triplet."""
    ...

```
  
---|---  
###  delete #
```
delete(subj: str, rel: str, obj: str) -> None

```

Delete triplet.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def delete(self, subj: str, rel: str, obj: str) -> None:
    """Delete triplet."""
    ...

```
  
---|---  
###  persist #
```
persist(persist_path: str, fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the graph store to a file.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def persist(
    self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
) -> None:
    """Persist the graph store to a file."""
    return

```
  
---|---  
###  get_schema #
```
get_schema(refresh: bool = False) -> str

```

Get the schema of the graph store.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def get_schema(self, refresh: bool = False) -> str:
    """Get the schema of the graph store."""
    ...

```
  
---|---  
###  query #
```
query(query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any

```

Query the graph store with statement and parameters.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def query(self, query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any:
    """Query the graph store with statement and parameters."""
    ...

```
  
---|---  
##  PropertyGraphStore #
Bases: `ABC`
Abstract labelled graph store protocol.
This protocol defines the interface for a graph store, which is responsible for storing and retrieving knowledge graph data.
Attributes:
Name | Type | Description  
---|---|---  
`client` |  `Any` |  Any: The client used to connect to the graph store.  
`get` |  `List[LabelledNode]` |  Callable[[str], List[List[str]]]: Get triplets for a given subject.  
`get_rel_map` |  `List[Triplet]` |  Callable[[Optional[List[str]], int], Dict[str, List[List[str]]]]: Get subjects' rel map in max depth.  
`upsert_triplet` |  `List[Triplet]` |  Callable[[str, str, str], None]: Upsert a triplet.  
`delete` |  `None` |  Callable[[str, str, str], None]: Delete a triplet.  
`persist` |  `None` |  Callable[[str, Optional[fsspec.AbstractFileSystem]], None]: Persist the graph store to a file.  
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
class PropertyGraphStore(ABC):
    """
    Abstract labelled graph store protocol.

    This protocol defines the interface for a graph store, which is responsible
    for storing and retrieving knowledge graph data.

    Attributes:
        client: Any: The client used to connect to the graph store.
        get: Callable[[str], List[List[str]]]: Get triplets for a given subject.
        get_rel_map: Callable[[Optional[List[str]], int], Dict[str, List[List[str]]]]:
            Get subjects' rel map in max depth.
        upsert_triplet: Callable[[str, str, str], None]: Upsert a triplet.
        delete: Callable[[str, str, str], None]: Delete a triplet.
        persist: Callable[[str, Optional[fsspec.AbstractFileSystem]], None]:
            Persist the graph store to a file.

    """

    supports_structured_queries: bool = False
    supports_vector_queries: bool = False
    text_to_cypher_template: PromptTemplate = DEFAULT_CYPHER_TEMPALTE

    @property
    def client(self) -> Any:
        """Get client."""

    @abstractmethod
    def get(
        self,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> List[LabelledNode]:
        """Get nodes with matching values."""
        ...

    @abstractmethod
    def get_triplets(
        self,
        entity_names: Optional[List[str]] = None,
        relation_names: Optional[List[str]] = None,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> List[Triplet]:
        """Get triplets with matching values."""
        ...

    @abstractmethod
    def get_rel_map(
        self,
        graph_nodes: List[LabelledNode],
        depth: int = 2,
        limit: int = 30,
        ignore_rels: Optional[List[str]] = None,
    ) -> List[Triplet]:
        """Get depth-aware rel map."""
        ...

    def get_llama_nodes(self, node_ids: List[str]) -> List[BaseNode]:
        """Get llama-index nodes."""
        nodes = self.get(ids=node_ids)
        converted_nodes = []
        for node in nodes:
            try:
                converted_nodes.append(metadata_dict_to_node(node.properties))
                converted_nodes[-1].set_content(node.text)  # type: ignore
            except Exception:
                continue

        return converted_nodes

    @abstractmethod
    def upsert_nodes(self, nodes: Sequence[LabelledNode]) -> None:
        """Upsert nodes."""
        ...

    @abstractmethod
    def upsert_relations(self, relations: List[Relation]) -> None:
        """Upsert relations."""
        ...

    def upsert_llama_nodes(self, llama_nodes: List[BaseNode]) -> None:
        """Add llama-index nodes."""
        converted_nodes = []
        for llama_node in llama_nodes:
            metadata_dict = node_to_metadata_dict(llama_node, remove_text=True)
            converted_nodes.append(
                ChunkNode(
                    text=llama_node.get_content(metadata_mode=MetadataMode.NONE),
                    id_=llama_node.id_,
                    properties=metadata_dict,
                    embedding=llama_node.embedding,
                )
            )
        self.upsert_nodes(converted_nodes)

    @abstractmethod
    def delete(
        self,
        entity_names: Optional[List[str]] = None,
        relation_names: Optional[List[str]] = None,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Delete matching data."""
        ...

    def delete_llama_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        ref_doc_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Delete llama-index nodes.

        Intended to delete any nodes in the graph store associated
        with the given llama-index node_ids or ref_doc_ids.
        """
        nodes = []

        node_ids = node_ids or []
        for id_ in node_ids:
            nodes.extend(self.get(properties={TRIPLET_SOURCE_KEY: id_}))

        if len(node_ids) > 0:
            nodes.extend(self.get(ids=node_ids))

        ref_doc_ids = ref_doc_ids or []
        for id_ in ref_doc_ids:
            nodes.extend(self.get(properties={"ref_doc_id": id_}))

        if len(ref_doc_ids) > 0:
            nodes.extend(self.get(ids=ref_doc_ids))

        self.delete(ids=[node.id for node in nodes])

    @abstractmethod
    def structured_query(
        self, query: str, param_map: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Query the graph store with statement and parameters."""
        ...

    @abstractmethod
    def vector_query(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> Tuple[List[LabelledNode], List[float]]:
        """Query the graph store with a vector store query."""
        ...

    def persist(
        self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
    ) -> None:
        """Persist the graph store to a file."""
        return

    def get_schema(self, refresh: bool = False) -> Any:
        """Get the schema of the graph store."""
        return None

    def get_schema_str(self, refresh: bool = False) -> str:
        """Get the schema of the graph store as a string."""
        return str(self.get_schema(refresh=refresh))

    ### ----- Async Methods ----- ###

    async def aget(
        self,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> List[LabelledNode]:
        """Asynchronously get nodes with matching values."""
        return self.get(properties, ids)

    async def aget_triplets(
        self,
        entity_names: Optional[List[str]] = None,
        relation_names: Optional[List[str]] = None,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> List[Triplet]:
        """Asynchronously get triplets with matching values."""
        return self.get_triplets(entity_names, relation_names, properties, ids)

    async def aget_rel_map(
        self,
        graph_nodes: List[LabelledNode],
        depth: int = 2,
        limit: int = 30,
        ignore_rels: Optional[List[str]] = None,
    ) -> List[Triplet]:
        """Asynchronously get depth-aware rel map."""
        return self.get_rel_map(graph_nodes, depth, limit, ignore_rels)

    async def aget_llama_nodes(self, node_ids: List[str]) -> List[BaseNode]:
        """Asynchronously get nodes."""
        nodes = await self.aget(ids=node_ids)
        converted_nodes = []
        for node in nodes:
            try:
                converted_nodes.append(metadata_dict_to_node(node.properties))
                converted_nodes[-1].set_content(node.text)  # type: ignore
            except Exception:
                continue

        return converted_nodes

    async def aupsert_nodes(self, nodes: List[LabelledNode]) -> None:
        """Asynchronously add nodes."""
        return self.upsert_nodes(nodes)

    async def aupsert_relations(self, relations: List[Relation]) -> None:
        """Asynchronously add relations."""
        return self.upsert_relations(relations)

    async def adelete(
        self,
        entity_names: Optional[List[str]] = None,
        relation_names: Optional[List[str]] = None,
        properties: Optional[dict] = None,
        ids: Optional[List[str]] = None,
    ) -> None:
        """Asynchronously delete matching data."""
        return self.delete(entity_names, relation_names, properties, ids)

    async def adelete_llama_nodes(
        self,
        node_ids: Optional[List[str]] = None,
        ref_doc_ids: Optional[List[str]] = None,
    ) -> None:
        """Asynchronously delete llama-index nodes."""
        return self.delete_llama_nodes(node_ids, ref_doc_ids)

    async def astructured_query(
        self, query: str, param_map: Optional[Dict[str, Any]] = {}
    ) -> Any:
        """Asynchronously query the graph store with statement and parameters."""
        return self.structured_query(query, param_map)

    async def avector_query(
        self, query: VectorStoreQuery, **kwargs: Any
    ) -> Tuple[List[LabelledNode], List[float]]:
        """Asynchronously query the graph store with a vector store query."""
        return self.vector_query(query, **kwargs)

    async def aget_schema(self, refresh: bool = False) -> str:
        """Asynchronously get the schema of the graph store."""
        return self.get_schema(refresh=refresh)

    async def aget_schema_str(self, refresh: bool = False) -> str:
        """Asynchronously get the schema of the graph store as a string."""
        return str(await self.aget_schema(refresh=refresh))

```
  
---|---  
###  client `property` #
```
client: Any

```

Get client.
###  get `abstractmethod` #
```
get(properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> List[LabelledNode]

```

Get nodes with matching values.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@abstractmethod
def get(
    self,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> List[LabelledNode]:
    """Get nodes with matching values."""
    ...

```
  
---|---  
###  get_triplets `abstractmethod` #
```
get_triplets(entity_names: Optional[List[str]] = None, relation_names: Optional[List[str]] = None, properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> List[Triplet]

```

Get triplets with matching values.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@abstractmethod
def get_triplets(
    self,
    entity_names: Optional[List[str]] = None,
    relation_names: Optional[List[str]] = None,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> List[Triplet]:
    """Get triplets with matching values."""
    ...

```
  
---|---  
###  get_rel_map `abstractmethod` #
```
get_rel_map(graph_nodes: List[LabelledNode], depth: int = 2, limit: int = 30, ignore_rels: Optional[List[str]] = None) -> List[Triplet]

```

Get depth-aware rel map.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@abstractmethod
def get_rel_map(
    self,
    graph_nodes: List[LabelledNode],
    depth: int = 2,
    limit: int = 30,
    ignore_rels: Optional[List[str]] = None,
) -> List[Triplet]:
    """Get depth-aware rel map."""
    ...

```
  
---|---  
###  get_llama_nodes #
```
get_llama_nodes(node_ids: List[str]) -> List[BaseNode]

```

Get llama-index nodes.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def get_llama_nodes(self, node_ids: List[str]) -> List[BaseNode]:
    """Get llama-index nodes."""
    nodes = self.get(ids=node_ids)
    converted_nodes = []
    for node in nodes:
        try:
            converted_nodes.append(metadata_dict_to_node(node.properties))
            converted_nodes[-1].set_content(node.text)  # type: ignore
        except Exception:
            continue

    return converted_nodes

```
  
---|---  
###  upsert_nodes `abstractmethod` #
```
upsert_nodes(nodes: Sequence[LabelledNode]) -> None

```

Upsert nodes.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@abstractmethod
def upsert_nodes(self, nodes: Sequence[LabelledNode]) -> None:
    """Upsert nodes."""
    ...

```
  
---|---  
###  upsert_relations `abstractmethod` #
```
upsert_relations(relations: List[Relation]) -> None

```

Upsert relations.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@abstractmethod
def upsert_relations(self, relations: List[Relation]) -> None:
    """Upsert relations."""
    ...

```
  
---|---  
###  upsert_llama_nodes #
```
upsert_llama_nodes(llama_nodes: List[BaseNode]) -> None

```

Add llama-index nodes.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def upsert_llama_nodes(self, llama_nodes: List[BaseNode]) -> None:
    """Add llama-index nodes."""
    converted_nodes = []
    for llama_node in llama_nodes:
        metadata_dict = node_to_metadata_dict(llama_node, remove_text=True)
        converted_nodes.append(
            ChunkNode(
                text=llama_node.get_content(metadata_mode=MetadataMode.NONE),
                id_=llama_node.id_,
                properties=metadata_dict,
                embedding=llama_node.embedding,
            )
        )
    self.upsert_nodes(converted_nodes)

```
  
---|---  
###  delete `abstractmethod` #
```
delete(entity_names: Optional[List[str]] = None, relation_names: Optional[List[str]] = None, properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> None

```

Delete matching data.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@abstractmethod
def delete(
    self,
    entity_names: Optional[List[str]] = None,
    relation_names: Optional[List[str]] = None,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> None:
    """Delete matching data."""
    ...

```
  
---|---  
###  delete_llama_nodes #
```
delete_llama_nodes(node_ids: Optional[List[str]] = None, ref_doc_ids: Optional[List[str]] = None) -> None

```

Delete llama-index nodes.
Intended to delete any nodes in the graph store associated with the given llama-index node_ids or ref_doc_ids.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def delete_llama_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    ref_doc_ids: Optional[List[str]] = None,
) -> None:
    """
    Delete llama-index nodes.

    Intended to delete any nodes in the graph store associated
    with the given llama-index node_ids or ref_doc_ids.
    """
    nodes = []

    node_ids = node_ids or []
    for id_ in node_ids:
        nodes.extend(self.get(properties={TRIPLET_SOURCE_KEY: id_}))

    if len(node_ids) > 0:
        nodes.extend(self.get(ids=node_ids))

    ref_doc_ids = ref_doc_ids or []
    for id_ in ref_doc_ids:
        nodes.extend(self.get(properties={"ref_doc_id": id_}))

    if len(ref_doc_ids) > 0:
        nodes.extend(self.get(ids=ref_doc_ids))

    self.delete(ids=[node.id for node in nodes])

```
  
---|---  
###  structured_query `abstractmethod` #
```
structured_query(query: str, param_map: Optional[Dict[str, Any]] = None) -> Any

```

Query the graph store with statement and parameters.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@abstractmethod
def structured_query(
    self, query: str, param_map: Optional[Dict[str, Any]] = None
) -> Any:
    """Query the graph store with statement and parameters."""
    ...

```
  
---|---  
###  vector_query `abstractmethod` #
```
vector_query(query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[LabelledNode], List[float]]

```

Query the graph store with a vector store query.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
@abstractmethod
def vector_query(
    self, query: VectorStoreQuery, **kwargs: Any
) -> Tuple[List[LabelledNode], List[float]]:
    """Query the graph store with a vector store query."""
    ...

```
  
---|---  
###  persist #
```
persist(persist_path: str, fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the graph store to a file.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def persist(
    self, persist_path: str, fs: Optional[fsspec.AbstractFileSystem] = None
) -> None:
    """Persist the graph store to a file."""
    return

```
  
---|---  
###  get_schema #
```
get_schema(refresh: bool = False) -> Any

```

Get the schema of the graph store.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def get_schema(self, refresh: bool = False) -> Any:
    """Get the schema of the graph store."""
    return None

```
  
---|---  
###  get_schema_str #
```
get_schema_str(refresh: bool = False) -> str

```

Get the schema of the graph store as a string.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
def get_schema_str(self, refresh: bool = False) -> str:
    """Get the schema of the graph store as a string."""
    return str(self.get_schema(refresh=refresh))

```
  
---|---  
###  aget `async` #
```
aget(properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> List[LabelledNode]

```

Asynchronously get nodes with matching values.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def aget(
    self,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> List[LabelledNode]:
    """Asynchronously get nodes with matching values."""
    return self.get(properties, ids)

```
  
---|---  
###  aget_triplets `async` #
```
aget_triplets(entity_names: Optional[List[str]] = None, relation_names: Optional[List[str]] = None, properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> List[Triplet]

```

Asynchronously get triplets with matching values.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def aget_triplets(
    self,
    entity_names: Optional[List[str]] = None,
    relation_names: Optional[List[str]] = None,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> List[Triplet]:
    """Asynchronously get triplets with matching values."""
    return self.get_triplets(entity_names, relation_names, properties, ids)

```
  
---|---  
###  aget_rel_map `async` #
```
aget_rel_map(graph_nodes: List[LabelledNode], depth: int = 2, limit: int = 30, ignore_rels: Optional[List[str]] = None) -> List[Triplet]

```

Asynchronously get depth-aware rel map.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def aget_rel_map(
    self,
    graph_nodes: List[LabelledNode],
    depth: int = 2,
    limit: int = 30,
    ignore_rels: Optional[List[str]] = None,
) -> List[Triplet]:
    """Asynchronously get depth-aware rel map."""
    return self.get_rel_map(graph_nodes, depth, limit, ignore_rels)

```
  
---|---  
###  aget_llama_nodes `async` #
```
aget_llama_nodes(node_ids: List[str]) -> List[BaseNode]

```

Asynchronously get nodes.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def aget_llama_nodes(self, node_ids: List[str]) -> List[BaseNode]:
    """Asynchronously get nodes."""
    nodes = await self.aget(ids=node_ids)
    converted_nodes = []
    for node in nodes:
        try:
            converted_nodes.append(metadata_dict_to_node(node.properties))
            converted_nodes[-1].set_content(node.text)  # type: ignore
        except Exception:
            continue

    return converted_nodes

```
  
---|---  
###  aupsert_nodes `async` #
```
aupsert_nodes(nodes: List[LabelledNode]) -> None

```

Asynchronously add nodes.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def aupsert_nodes(self, nodes: List[LabelledNode]) -> None:
    """Asynchronously add nodes."""
    return self.upsert_nodes(nodes)

```
  
---|---  
###  aupsert_relations `async` #
```
aupsert_relations(relations: List[Relation]) -> None

```

Asynchronously add relations.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def aupsert_relations(self, relations: List[Relation]) -> None:
    """Asynchronously add relations."""
    return self.upsert_relations(relations)

```
  
---|---  
###  adelete `async` #
```
adelete(entity_names: Optional[List[str]] = None, relation_names: Optional[List[str]] = None, properties: Optional[dict] = None, ids: Optional[List[str]] = None) -> None

```

Asynchronously delete matching data.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def adelete(
    self,
    entity_names: Optional[List[str]] = None,
    relation_names: Optional[List[str]] = None,
    properties: Optional[dict] = None,
    ids: Optional[List[str]] = None,
) -> None:
    """Asynchronously delete matching data."""
    return self.delete(entity_names, relation_names, properties, ids)

```
  
---|---  
###  adelete_llama_nodes `async` #
```
adelete_llama_nodes(node_ids: Optional[List[str]] = None, ref_doc_ids: Optional[List[str]] = None) -> None

```

Asynchronously delete llama-index nodes.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def adelete_llama_nodes(
    self,
    node_ids: Optional[List[str]] = None,
    ref_doc_ids: Optional[List[str]] = None,
) -> None:
    """Asynchronously delete llama-index nodes."""
    return self.delete_llama_nodes(node_ids, ref_doc_ids)

```
  
---|---  
###  astructured_query `async` #
```
astructured_query(query: str, param_map: Optional[Dict[str, Any]] = {}) -> Any

```

Asynchronously query the graph store with statement and parameters.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def astructured_query(
    self, query: str, param_map: Optional[Dict[str, Any]] = {}
) -> Any:
    """Asynchronously query the graph store with statement and parameters."""
    return self.structured_query(query, param_map)

```
  
---|---  
###  avector_query `async` #
```
avector_query(query: VectorStoreQuery, **kwargs: Any) -> Tuple[List[LabelledNode], List[float]]

```

Asynchronously query the graph store with a vector store query.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def avector_query(
    self, query: VectorStoreQuery, **kwargs: Any
) -> Tuple[List[LabelledNode], List[float]]:
    """Asynchronously query the graph store with a vector store query."""
    return self.vector_query(query, **kwargs)

```
  
---|---  
###  aget_schema `async` #
```
aget_schema(refresh: bool = False) -> str

```

Asynchronously get the schema of the graph store.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def aget_schema(self, refresh: bool = False) -> str:
    """Asynchronously get the schema of the graph store."""
    return self.get_schema(refresh=refresh)

```
  
---|---  
###  aget_schema_str `async` #
```
aget_schema_str(refresh: bool = False) -> str

```

Asynchronously get the schema of the graph store as a string.
Source code in `llama-index-core/llama_index/core/graph_stores/types.py`

| ```
async def aget_schema_str(self, refresh: bool = False) -> str:
    """Asynchronously get the schema of the graph store as a string."""
    return str(await self.aget_schema(refresh=refresh))

```
  
---|---
