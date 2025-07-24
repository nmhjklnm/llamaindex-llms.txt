# Storage context
##  StorageContext `dataclass` #
Storage context.
The storage context container is a utility container for storing nodes, indices, and vectors. It contains the following: - docstore: BaseDocumentStore - index_store: BaseIndexStore - vector_store: BasePydanticVectorStore - graph_store: GraphStore - property_graph_store: PropertyGraphStore (lazily initialized)
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`docstore` |  `BaseDocumentStore` |  |  _required_  
`index_store` |  `BaseIndexStore` |  |  _required_  
`vector_stores` |  `Dict[str, Annotated[BasePydanticVectorStore, SerializeAsAny]]` |  |  _required_  
`graph_store` |  `GraphStore` |  |  _required_  
`property_graph_store` |  `PropertyGraphStore | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/storage/storage_context.py`

| ```
@dataclass
class StorageContext:
    """
    Storage context.

    The storage context container is a utility container for storing nodes,
    indices, and vectors. It contains the following:
    - docstore: BaseDocumentStore
    - index_store: BaseIndexStore
    - vector_store: BasePydanticVectorStore
    - graph_store: GraphStore
    - property_graph_store: PropertyGraphStore (lazily initialized)

    """

    docstore: BaseDocumentStore
    index_store: BaseIndexStore
    vector_stores: Dict[str, SerializeAsAny[BasePydanticVectorStore]]
    graph_store: GraphStore
    property_graph_store: Optional[PropertyGraphStore] = None

    @classmethod
    def from_defaults(
        cls,
        docstore: Optional[BaseDocumentStore] = None,
        index_store: Optional[BaseIndexStore] = None,
        vector_store: Optional[BasePydanticVectorStore] = None,
        image_store: Optional[BasePydanticVectorStore] = None,
        vector_stores: Optional[Dict[str, BasePydanticVectorStore]] = None,
        graph_store: Optional[GraphStore] = None,
        property_graph_store: Optional[PropertyGraphStore] = None,
        persist_dir: Optional[str] = None,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> "StorageContext":
        """
        Create a StorageContext from defaults.

        Args:
            docstore (Optional[BaseDocumentStore]): document store
            index_store (Optional[BaseIndexStore]): index store
            vector_store (Optional[BasePydanticVectorStore]): vector store
            graph_store (Optional[GraphStore]): graph store
            image_store (Optional[BasePydanticVectorStore]): image store

        """
        if persist_dir is None:
            docstore = docstore or SimpleDocumentStore()
            index_store = index_store or SimpleIndexStore()
            graph_store = graph_store or SimpleGraphStore()
            image_store = image_store or SimpleVectorStore()

            if vector_store:
                vector_stores = {DEFAULT_VECTOR_STORE: vector_store}
            else:
                vector_stores = vector_stores or {
                    DEFAULT_VECTOR_STORE: SimpleVectorStore()
                }
            if image_store:
                # append image store to vector stores
                vector_stores[IMAGE_VECTOR_STORE_NAMESPACE] = image_store
        else:
            docstore = docstore or SimpleDocumentStore.from_persist_dir(
                persist_dir, fs=fs
            )
            index_store = index_store or SimpleIndexStore.from_persist_dir(
                persist_dir, fs=fs
            )
            graph_store = graph_store or SimpleGraphStore.from_persist_dir(
                persist_dir, fs=fs
            )

            try:
                property_graph_store = (
                    property_graph_store
                    or SimplePropertyGraphStore.from_persist_dir(persist_dir, fs=fs)
                )
            except FileNotFoundError:
                property_graph_store = None

            if vector_store:
                vector_stores = {DEFAULT_VECTOR_STORE: vector_store}
            elif vector_stores:
                vector_stores = vector_stores
            else:
                vector_stores = SimpleVectorStore.from_namespaced_persist_dir(
                    persist_dir, fs=fs
                )
            if image_store:
                # append image store to vector stores
                vector_stores[IMAGE_VECTOR_STORE_NAMESPACE] = image_store  # type: ignore

        return cls(
            docstore=docstore,
            index_store=index_store,
            vector_stores=vector_stores,  # type: ignore
            graph_store=graph_store,
            property_graph_store=property_graph_store,
        )

    def persist(
        self,
        persist_dir: Union[str, os.PathLike] = DEFAULT_PERSIST_DIR,
        docstore_fname: str = DOCSTORE_FNAME,
        index_store_fname: str = INDEX_STORE_FNAME,
        vector_store_fname: str = VECTOR_STORE_FNAME,
        image_store_fname: str = IMAGE_STORE_FNAME,
        graph_store_fname: str = GRAPH_STORE_FNAME,
        pg_graph_store_fname: str = PG_FNAME,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> None:
        """
        Persist the storage context.

        Args:
            persist_dir (str): directory to persist the storage context

        """
        if fs is not None:
            persist_dir = str(persist_dir)  # NOTE: doesn't support Windows here
            docstore_path = concat_dirs(persist_dir, docstore_fname)
            index_store_path = concat_dirs(persist_dir, index_store_fname)
            graph_store_path = concat_dirs(persist_dir, graph_store_fname)
            pg_graph_store_path = concat_dirs(persist_dir, pg_graph_store_fname)
        else:
            persist_dir = Path(persist_dir)
            docstore_path = str(persist_dir / docstore_fname)
            index_store_path = str(persist_dir / index_store_fname)
            graph_store_path = str(persist_dir / graph_store_fname)
            pg_graph_store_path = str(persist_dir / pg_graph_store_fname)

        self.docstore.persist(persist_path=docstore_path, fs=fs)
        self.index_store.persist(persist_path=index_store_path, fs=fs)
        self.graph_store.persist(persist_path=graph_store_path, fs=fs)

        if self.property_graph_store:
            self.property_graph_store.persist(persist_path=pg_graph_store_path, fs=fs)

        # save each vector store under it's namespace
        for vector_store_name, vector_store in self.vector_stores.items():
            if fs is not None:
                vector_store_path = concat_dirs(
                    str(persist_dir),
                    f"{vector_store_name}{NAMESPACE_SEP}{vector_store_fname}",
                )
            else:
                vector_store_path = str(
                    Path(persist_dir)
                    / f"{vector_store_name}{NAMESPACE_SEP}{vector_store_fname}"
                )

            vector_store.persist(persist_path=vector_store_path, fs=fs)

    def to_dict(self) -> dict:
        all_simple = (
            isinstance(self.docstore, SimpleDocumentStore)
            and isinstance(self.index_store, SimpleIndexStore)
            and isinstance(self.graph_store, SimpleGraphStore)
            and isinstance(
                self.property_graph_store, (SimplePropertyGraphStore, type(None))
            )
            and all(
                isinstance(vs, SimpleVectorStore) for vs in self.vector_stores.values()
            )
        )
        if not all_simple:
            raise ValueError(
                "to_dict only available when using simple doc/index/vector stores"
            )

        assert isinstance(self.docstore, SimpleDocumentStore)
        assert isinstance(self.index_store, SimpleIndexStore)
        assert isinstance(self.graph_store, SimpleGraphStore)
        assert isinstance(
            self.property_graph_store, (SimplePropertyGraphStore, type(None))
        )

        return {
            VECTOR_STORE_KEY: {
                key: vector_store.to_dict()
                for key, vector_store in self.vector_stores.items()
                if isinstance(vector_store, SimpleVectorStore)
            },
            DOC_STORE_KEY: self.docstore.to_dict(),
            INDEX_STORE_KEY: self.index_store.to_dict(),
            GRAPH_STORE_KEY: self.graph_store.to_dict(),
            PG_STORE_KEY: (
                self.property_graph_store.to_dict()
                if self.property_graph_store
                else None
            ),
        }

    @classmethod
    def from_dict(cls, save_dict: dict) -> "StorageContext":
        """Create a StorageContext from dict."""
        docstore = SimpleDocumentStore.from_dict(save_dict[DOC_STORE_KEY])
        index_store = SimpleIndexStore.from_dict(save_dict[INDEX_STORE_KEY])
        graph_store = SimpleGraphStore.from_dict(save_dict[GRAPH_STORE_KEY])
        property_graph_store = (
            SimplePropertyGraphStore.from_dict(save_dict[PG_STORE_KEY])
            if save_dict[PG_STORE_KEY]
            else None
        )

        vector_stores: Dict[str, BasePydanticVectorStore] = {}
        for key, vector_store_dict in save_dict[VECTOR_STORE_KEY].items():
            vector_stores[key] = SimpleVectorStore.from_dict(vector_store_dict)

        return cls(
            docstore=docstore,
            index_store=index_store,
            vector_stores=vector_stores,
            graph_store=graph_store,
            property_graph_store=property_graph_store,
        )

    @property
    def vector_store(self) -> BasePydanticVectorStore:
        """Backwrds compatibility for vector_store property."""
        return self.vector_stores[DEFAULT_VECTOR_STORE]

    def add_vector_store(
        self, vector_store: BasePydanticVectorStore, namespace: str
    ) -> None:
        """Add a vector store to the storage context."""
        self.vector_stores[namespace] = vector_store

```
  
---|---  
###  vector_store `property` #
```
vector_store: BasePydanticVectorStore

```

Backwrds compatibility for vector_store property.
###  from_defaults `classmethod` #
```
from_defaults(docstore: Optional[BaseDocumentStore] = None, index_store: Optional[BaseIndexStore] = None, vector_store: Optional[BasePydanticVectorStore] = None, image_store: Optional[BasePydanticVectorStore] = None, vector_stores: Optional[Dict[str, BasePydanticVectorStore]] = None, graph_store: Optional[GraphStore] = None, property_graph_store: Optional[PropertyGraphStore] = None, persist_dir: Optional[str] = None, fs: Optional[AbstractFileSystem] = None) -> StorageContext

```

Create a StorageContext from defaults.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`docstore` |  `Optional[BaseDocumentStore]` |  document store |  `None`  
`index_store` |  `Optional[BaseIndexStore]` |  index store |  `None`  
`vector_store` |  `Optional[BasePydanticVectorStore]` |  vector store |  `None`  
`graph_store` |  `Optional[GraphStore]` |  graph store |  `None`  
`image_store` |  `Optional[BasePydanticVectorStore]` |  image store |  `None`  
Source code in `llama-index-core/llama_index/core/storage/storage_context.py`

| ```
@classmethod
def from_defaults(
    cls,
    docstore: Optional[BaseDocumentStore] = None,
    index_store: Optional[BaseIndexStore] = None,
    vector_store: Optional[BasePydanticVectorStore] = None,
    image_store: Optional[BasePydanticVectorStore] = None,
    vector_stores: Optional[Dict[str, BasePydanticVectorStore]] = None,
    graph_store: Optional[GraphStore] = None,
    property_graph_store: Optional[PropertyGraphStore] = None,
    persist_dir: Optional[str] = None,
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> "StorageContext":
    """
    Create a StorageContext from defaults.

    Args:
        docstore (Optional[BaseDocumentStore]): document store
        index_store (Optional[BaseIndexStore]): index store
        vector_store (Optional[BasePydanticVectorStore]): vector store
        graph_store (Optional[GraphStore]): graph store
        image_store (Optional[BasePydanticVectorStore]): image store

    """
    if persist_dir is None:
        docstore = docstore or SimpleDocumentStore()
        index_store = index_store or SimpleIndexStore()
        graph_store = graph_store or SimpleGraphStore()
        image_store = image_store or SimpleVectorStore()

        if vector_store:
            vector_stores = {DEFAULT_VECTOR_STORE: vector_store}
        else:
            vector_stores = vector_stores or {
                DEFAULT_VECTOR_STORE: SimpleVectorStore()
            }
        if image_store:
            # append image store to vector stores
            vector_stores[IMAGE_VECTOR_STORE_NAMESPACE] = image_store
    else:
        docstore = docstore or SimpleDocumentStore.from_persist_dir(
            persist_dir, fs=fs
        )
        index_store = index_store or SimpleIndexStore.from_persist_dir(
            persist_dir, fs=fs
        )
        graph_store = graph_store or SimpleGraphStore.from_persist_dir(
            persist_dir, fs=fs
        )

        try:
            property_graph_store = (
                property_graph_store
                or SimplePropertyGraphStore.from_persist_dir(persist_dir, fs=fs)
            )
        except FileNotFoundError:
            property_graph_store = None

        if vector_store:
            vector_stores = {DEFAULT_VECTOR_STORE: vector_store}
        elif vector_stores:
            vector_stores = vector_stores
        else:
            vector_stores = SimpleVectorStore.from_namespaced_persist_dir(
                persist_dir, fs=fs
            )
        if image_store:
            # append image store to vector stores
            vector_stores[IMAGE_VECTOR_STORE_NAMESPACE] = image_store  # type: ignore

    return cls(
        docstore=docstore,
        index_store=index_store,
        vector_stores=vector_stores,  # type: ignore
        graph_store=graph_store,
        property_graph_store=property_graph_store,
    )

```
  
---|---  
###  persist #
```
persist(persist_dir: Union[str, PathLike] = DEFAULT_PERSIST_DIR, docstore_fname: str = DEFAULT_PERSIST_FNAME, index_store_fname: str = DEFAULT_PERSIST_FNAME, vector_store_fname: str = DEFAULT_PERSIST_FNAME, image_store_fname: str = IMAGE_STORE_FNAME, graph_store_fname: str = DEFAULT_PERSIST_FNAME, pg_graph_store_fname: str = DEFAULT_PG_PERSIST_FNAME, fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the storage context.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`persist_dir` |  `str` |  directory to persist the storage context |  `DEFAULT_PERSIST_DIR`  
Source code in `llama-index-core/llama_index/core/storage/storage_context.py`

| ```
def persist(
    self,
    persist_dir: Union[str, os.PathLike] = DEFAULT_PERSIST_DIR,
    docstore_fname: str = DOCSTORE_FNAME,
    index_store_fname: str = INDEX_STORE_FNAME,
    vector_store_fname: str = VECTOR_STORE_FNAME,
    image_store_fname: str = IMAGE_STORE_FNAME,
    graph_store_fname: str = GRAPH_STORE_FNAME,
    pg_graph_store_fname: str = PG_FNAME,
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> None:
    """
    Persist the storage context.

    Args:
        persist_dir (str): directory to persist the storage context

    """
    if fs is not None:
        persist_dir = str(persist_dir)  # NOTE: doesn't support Windows here
        docstore_path = concat_dirs(persist_dir, docstore_fname)
        index_store_path = concat_dirs(persist_dir, index_store_fname)
        graph_store_path = concat_dirs(persist_dir, graph_store_fname)
        pg_graph_store_path = concat_dirs(persist_dir, pg_graph_store_fname)
    else:
        persist_dir = Path(persist_dir)
        docstore_path = str(persist_dir / docstore_fname)
        index_store_path = str(persist_dir / index_store_fname)
        graph_store_path = str(persist_dir / graph_store_fname)
        pg_graph_store_path = str(persist_dir / pg_graph_store_fname)

    self.docstore.persist(persist_path=docstore_path, fs=fs)
    self.index_store.persist(persist_path=index_store_path, fs=fs)
    self.graph_store.persist(persist_path=graph_store_path, fs=fs)

    if self.property_graph_store:
        self.property_graph_store.persist(persist_path=pg_graph_store_path, fs=fs)

    # save each vector store under it's namespace
    for vector_store_name, vector_store in self.vector_stores.items():
        if fs is not None:
            vector_store_path = concat_dirs(
                str(persist_dir),
                f"{vector_store_name}{NAMESPACE_SEP}{vector_store_fname}",
            )
        else:
            vector_store_path = str(
                Path(persist_dir)
                / f"{vector_store_name}{NAMESPACE_SEP}{vector_store_fname}"
            )

        vector_store.persist(persist_path=vector_store_path, fs=fs)

```
  
---|---  
###  from_dict `classmethod` #
```
from_dict(save_dict: dict) -> StorageContext

```

Create a StorageContext from dict.
Source code in `llama-index-core/llama_index/core/storage/storage_context.py`

| ```
@classmethod
def from_dict(cls, save_dict: dict) -> "StorageContext":
    """Create a StorageContext from dict."""
    docstore = SimpleDocumentStore.from_dict(save_dict[DOC_STORE_KEY])
    index_store = SimpleIndexStore.from_dict(save_dict[INDEX_STORE_KEY])
    graph_store = SimpleGraphStore.from_dict(save_dict[GRAPH_STORE_KEY])
    property_graph_store = (
        SimplePropertyGraphStore.from_dict(save_dict[PG_STORE_KEY])
        if save_dict[PG_STORE_KEY]
        else None
    )

    vector_stores: Dict[str, BasePydanticVectorStore] = {}
    for key, vector_store_dict in save_dict[VECTOR_STORE_KEY].items():
        vector_stores[key] = SimpleVectorStore.from_dict(vector_store_dict)

    return cls(
        docstore=docstore,
        index_store=index_store,
        vector_stores=vector_stores,
        graph_store=graph_store,
        property_graph_store=property_graph_store,
    )

```
  
---|---  
###  add_vector_store #
```
add_vector_store(vector_store: BasePydanticVectorStore, namespace: str) -> None

```

Add a vector store to the storage context.
Source code in `llama-index-core/llama_index/core/storage/storage_context.py`

| ```
def add_vector_store(
    self, vector_store: BasePydanticVectorStore, namespace: str
) -> None:
    """Add a vector store to the storage context."""
    self.vector_stores[namespace] = vector_store

```
  
---|---  
Top-level imports for LlamaIndex.
##  load_index_from_storage #
```
load_index_from_storage(storage_context: StorageContext, index_id: Optional[str] = None, **kwargs: Any) -> BaseIndex

```

Load index from storage context.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`storage_context` |  `StorageContext` |  storage context containing docstore, index store and vector store. |  _required_  
`index_id` |  `Optional[str]` |  ID of the index to load. Defaults to None, which assumes there's only a single index in the index store and load it. |  `None`  
`**kwargs` |  `Any` |  Additional keyword args to pass to the index constructors. |  `{}`  
Source code in `llama-index-core/llama_index/core/indices/loading.py`

| ```
def load_index_from_storage(
    storage_context: StorageContext,
    index_id: Optional[str] = None,
    **kwargs: Any,
) -> BaseIndex:
    """
    Load index from storage context.

    Args:
        storage_context (StorageContext): storage context containing
            docstore, index store and vector store.
        index_id (Optional[str]): ID of the index to load.
            Defaults to None, which assumes there's only a single index
            in the index store and load it.
        **kwargs: Additional keyword args to pass to the index constructors.

    """
    index_ids: Optional[Sequence[str]]
    if index_id is None:
        index_ids = None
    else:
        index_ids = [index_id]

    indices = load_indices_from_storage(storage_context, index_ids=index_ids, **kwargs)

    if len(indices) == 0:
        raise ValueError(
            "No index in storage context, check if you specified the right persist_dir."
        )
    elif len(indices) > 1:
        raise ValueError(
            f"Expected to load a single index, but got {len(indices)} instead. "
            "Please specify index_id."
        )

    return indices[0]

```
  
---|---  
##  load_indices_from_storage #
```
load_indices_from_storage(storage_context: StorageContext, index_ids: Optional[Sequence[str]] = None, **kwargs: Any) -> List[BaseIndex]

```

Load multiple indices from storage context.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`storage_context` |  `StorageContext` |  storage context containing docstore, index store and vector store. |  _required_  
`index_id` |  `Optional[Sequence[str]]` |  IDs of the indices to load. Defaults to None, which loads all indices in the index store. |  _required_  
`**kwargs` |  `Any` |  Additional keyword args to pass to the index constructors. |  `{}`  
Source code in `llama-index-core/llama_index/core/indices/loading.py`

| ```
def load_indices_from_storage(
    storage_context: StorageContext,
    index_ids: Optional[Sequence[str]] = None,
    **kwargs: Any,
) -> List[BaseIndex]:
    """
    Load multiple indices from storage context.

    Args:
        storage_context (StorageContext): storage context containing
            docstore, index store and vector store.
        index_id (Optional[Sequence[str]]): IDs of the indices to load.
            Defaults to None, which loads all indices in the index store.
        **kwargs: Additional keyword args to pass to the index constructors.

    """
    if index_ids is None:
        logger.info("Loading all indices.")
        index_structs = storage_context.index_store.index_structs()
    else:
        logger.info(f"Loading indices with ids: {index_ids}")
        index_structs = []
        for index_id in index_ids:
            index_struct = storage_context.index_store.get_index_struct(index_id)
            if index_struct is None:
                raise ValueError(f"Failed to load index with ID {index_id}")
            index_structs.append(index_struct)

    indices = []
    for index_struct in index_structs:
        type_ = index_struct.get_type()
        index_cls = INDEX_STRUCT_TYPE_TO_INDEX_CLASS[type_]
        index = index_cls(
            index_struct=index_struct, storage_context=storage_context, **kwargs
        )
        indices.append(index)
    return indices

```
  
---|---
