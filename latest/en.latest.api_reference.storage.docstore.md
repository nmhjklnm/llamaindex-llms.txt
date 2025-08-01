# Index
##  RefDocInfo `dataclass` #
Bases: `DataClassJsonMixin`
Dataclass to represent ingested documents.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_ids` |  `List` |  Built-in mutable sequence. If no argument is given, the constructor creates a new empty list. The argument must be an iterable if specified. |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@dataclass
class RefDocInfo(DataClassJsonMixin):
    """Dataclass to represent ingested documents."""

    node_ids: List = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

```
  
---|---  
##  BaseDocumentStore #
Bases: `ABC`
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
class BaseDocumentStore(ABC):
    # ===== Save/load =====
    def persist(
        self,
        persist_path: str = DEFAULT_PERSIST_PATH,
        fs: Optional[fsspec.AbstractFileSystem] = None,
    ) -> None:
        """Persist the docstore to a file."""

    # ===== Main interface =====
    @property
    @abstractmethod
    def docs(self) -> Dict[str, BaseNode]: ...

    @abstractmethod
    def add_documents(
        self,
        docs: Sequence[BaseNode],
        allow_update: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
        store_text: bool = True,
    ) -> None: ...

    @abstractmethod
    async def async_add_documents(
        self,
        docs: Sequence[BaseNode],
        allow_update: bool = True,
        batch_size: int = DEFAULT_BATCH_SIZE,
        store_text: bool = True,
    ) -> None: ...

    @abstractmethod
    def get_document(self, doc_id: str, raise_error: bool = True) -> Optional[BaseNode]: ...

    @abstractmethod
    async def aget_document(self, doc_id: str, raise_error: bool = True) -> Optional[BaseNode]: ...

    @abstractmethod
    def delete_document(self, doc_id: str, raise_error: bool = True) -> None:
        """Delete a document from the store."""
        ...

    @abstractmethod
    async def adelete_document(self, doc_id: str, raise_error: bool = True) -> None:
        """Delete a document from the store."""
        ...

    @abstractmethod
    def document_exists(self, doc_id: str) -> bool: ...

    @abstractmethod
    async def adocument_exists(self, doc_id: str) -> bool: ...

    # ===== Hash =====
    @abstractmethod
    def set_document_hash(self, doc_id: str, doc_hash: str) -> None: ...

    @abstractmethod
    async def aset_document_hash(self, doc_id: str, doc_hash: str) -> None: ...

    @abstractmethod
    def set_document_hashes(self, doc_hashes: Dict[str, str]) -> None: ...

    @abstractmethod
    async def aset_document_hashes(self, doc_hashes: Dict[str, str]) -> None: ...

    @abstractmethod
    def get_document_hash(self, doc_id: str) -> Optional[str]: ...

    @abstractmethod
    async def aget_document_hash(self, doc_id: str) -> Optional[str]: ...

    @abstractmethod
    def get_all_document_hashes(self) -> Dict[str, str]: ...

    @abstractmethod
    async def aget_all_document_hashes(self) -> Dict[str, str]: ...

    # ==== Ref Docs =====
    @abstractmethod
    def get_all_ref_doc_info(self) -> Optional[Dict[str, RefDocInfo]]:
        """Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents."""

    @abstractmethod
    async def aget_all_ref_doc_info(self) -> Optional[Dict[str, RefDocInfo]]:
        """Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents."""

    @abstractmethod
    def get_ref_doc_info(self, ref_doc_id: str) -> Optional[RefDocInfo]:
        """Get the RefDocInfo for a given ref_doc_id."""

    @abstractmethod
    async def aget_ref_doc_info(self, ref_doc_id: str) -> Optional[RefDocInfo]:
        """Get the RefDocInfo for a given ref_doc_id."""

    @abstractmethod
    def delete_ref_doc(self, ref_doc_id: str, raise_error: bool = True) -> None:
        """Delete a ref_doc and all it's associated nodes."""

    @abstractmethod
    async def adelete_ref_doc(self, ref_doc_id: str, raise_error: bool = True) -> None:
        """Delete a ref_doc and all it's associated nodes."""

    # ===== Nodes =====
    def get_nodes(self, node_ids: List[str], raise_error: bool = True) -> List[BaseNode]:
        """
        Get nodes from docstore.

        Args:
            node_ids (List[str]): node ids
            raise_error (bool): raise error if node_id not found

        """
        nodes: list[BaseNode] = []

        for node_id in node_ids:
            # if needed for type checking
            if not raise_error:
                if node := self.get_node(node_id=node_id, raise_error=False):
                    nodes.append(node)
                continue

            nodes.append(self.get_node(node_id=node_id, raise_error=True))

        return nodes

    async def aget_nodes(self, node_ids: List[str], raise_error: bool = True) -> List[BaseNode]:
        """
        Get nodes from docstore.

        Args:
            node_ids (List[str]): node ids
            raise_error (bool): raise error if node_id not found

        """
        nodes: list[BaseNode] = []

        for node_id in node_ids:
            # if needed for type checking
            if not raise_error:
                if node := await self.aget_node(node_id=node_id, raise_error=False):
                    nodes.append(node)
                continue

            nodes.append(await self.aget_node(node_id=node_id, raise_error=True))

        return nodes

    @overload
    def get_node(self, node_id: str, raise_error: Literal[True] = True) -> BaseNode: ...

    @overload
    def get_node(self, node_id: str, raise_error: Literal[False] = False) -> Optional[BaseNode]: ...

    def get_node(self, node_id: str, raise_error: bool = True) -> Optional[BaseNode]:
        """
        Get node from docstore.

        Args:
            node_id (str): node id
            raise_error (bool): raise error if node_id not found

        """
        doc = self.get_document(node_id, raise_error=raise_error)

        if doc is None:
            # The doc store should have raised an error if the node_id is not found, but it didn't
            # so we raise an error here
            if raise_error:
                raise ValueError(f"Node {node_id} not found")
            return None

        # The document should always be a BaseNode, but we check to be safe
        if not isinstance(doc, BaseNode):
            raise ValueError(f"Document {node_id} is not a Node.")

        return doc

    @overload
    async def aget_node(self, node_id: str, raise_error: Literal[True] = True) -> BaseNode: ...

    @overload
    async def aget_node(self, node_id: str, raise_error: Literal[False] = False) -> Optional[BaseNode]: ...

    async def aget_node(self, node_id: str, raise_error: bool = True) -> Optional[BaseNode]:
        """
        Get node from docstore.

        Args:
            node_id (str): node id
            raise_error (bool): raise error if node_id not found

        """
        doc = await self.aget_document(node_id, raise_error=raise_error)

        if doc is None:
            # The doc store should have raised an error if the node_id is not found, but it didn't
            # so we raise an error here
            if raise_error:
                raise ValueError(f"Node {node_id} not found")
            return None

        # The document should always be a BaseNode, but we check to be safe
        if not isinstance(doc, BaseNode):
            raise ValueError(f"Document {node_id} is not a Node.")

        return doc

    def get_node_dict(self, node_id_dict: Dict[int, str]) -> Dict[int, BaseNode]:
        """
        Get node dict from docstore given a mapping of index to node ids.

        Args:
            node_id_dict (Dict[int, str]): mapping of index to node ids

        """
        return {index: self.get_node(node_id) for index, node_id in node_id_dict.items()}

    async def aget_node_dict(self, node_id_dict: Dict[int, str]) -> Dict[int, BaseNode]:
        """
        Get node dict from docstore given a mapping of index to node ids.

        Args:
            node_id_dict (Dict[int, str]): mapping of index to node ids

        """
        return {index: await self.aget_node(node_id) for index, node_id in node_id_dict.items()}

```
  
---|---  
###  persist #
```
persist(persist_path: str = DEFAULT_PERSIST_PATH, fs: Optional[AbstractFileSystem] = None) -> None

```

Persist the docstore to a file.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
def persist(
    self,
    persist_path: str = DEFAULT_PERSIST_PATH,
    fs: Optional[fsspec.AbstractFileSystem] = None,
) -> None:
    """Persist the docstore to a file."""

```
  
---|---  
###  delete_document `abstractmethod` #
```
delete_document(doc_id: str, raise_error: bool = True) -> None

```

Delete a document from the store.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@abstractmethod
def delete_document(self, doc_id: str, raise_error: bool = True) -> None:
    """Delete a document from the store."""
    ...

```
  
---|---  
###  adelete_document `abstractmethod` `async` #
```
adelete_document(doc_id: str, raise_error: bool = True) -> None

```

Delete a document from the store.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@abstractmethod
async def adelete_document(self, doc_id: str, raise_error: bool = True) -> None:
    """Delete a document from the store."""
    ...

```
  
---|---  
###  get_all_ref_doc_info `abstractmethod` #
```
get_all_ref_doc_info() -> Optional[Dict[str, RefDocInfo]]

```

Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@abstractmethod
def get_all_ref_doc_info(self) -> Optional[Dict[str, RefDocInfo]]:
    """Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents."""

```
  
---|---  
###  aget_all_ref_doc_info `abstractmethod` `async` #
```
aget_all_ref_doc_info() -> Optional[Dict[str, RefDocInfo]]

```

Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@abstractmethod
async def aget_all_ref_doc_info(self) -> Optional[Dict[str, RefDocInfo]]:
    """Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents."""

```
  
---|---  
###  get_ref_doc_info `abstractmethod` #
```
get_ref_doc_info(ref_doc_id: str) -> Optional[RefDocInfo]

```

Get the RefDocInfo for a given ref_doc_id.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@abstractmethod
def get_ref_doc_info(self, ref_doc_id: str) -> Optional[RefDocInfo]:
    """Get the RefDocInfo for a given ref_doc_id."""

```
  
---|---  
###  aget_ref_doc_info `abstractmethod` `async` #
```
aget_ref_doc_info(ref_doc_id: str) -> Optional[RefDocInfo]

```

Get the RefDocInfo for a given ref_doc_id.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@abstractmethod
async def aget_ref_doc_info(self, ref_doc_id: str) -> Optional[RefDocInfo]:
    """Get the RefDocInfo for a given ref_doc_id."""

```
  
---|---  
###  delete_ref_doc `abstractmethod` #
```
delete_ref_doc(ref_doc_id: str, raise_error: bool = True) -> None

```

Delete a ref_doc and all it's associated nodes.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@abstractmethod
def delete_ref_doc(self, ref_doc_id: str, raise_error: bool = True) -> None:
    """Delete a ref_doc and all it's associated nodes."""

```
  
---|---  
###  adelete_ref_doc `abstractmethod` `async` #
```
adelete_ref_doc(ref_doc_id: str, raise_error: bool = True) -> None

```

Delete a ref_doc and all it's associated nodes.
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
@abstractmethod
async def adelete_ref_doc(self, ref_doc_id: str, raise_error: bool = True) -> None:
    """Delete a ref_doc and all it's associated nodes."""

```
  
---|---  
###  get_nodes #
```
get_nodes(node_ids: List[str], raise_error: bool = True) -> List[BaseNode]

```

Get nodes from docstore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_ids` |  `List[str]` |  node ids |  _required_  
`raise_error` |  `bool` |  raise error if node_id not found |  `True`  
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
def get_nodes(self, node_ids: List[str], raise_error: bool = True) -> List[BaseNode]:
    """
    Get nodes from docstore.

    Args:
        node_ids (List[str]): node ids
        raise_error (bool): raise error if node_id not found

    """
    nodes: list[BaseNode] = []

    for node_id in node_ids:
        # if needed for type checking
        if not raise_error:
            if node := self.get_node(node_id=node_id, raise_error=False):
                nodes.append(node)
            continue

        nodes.append(self.get_node(node_id=node_id, raise_error=True))

    return nodes

```
  
---|---  
###  aget_nodes `async` #
```
aget_nodes(node_ids: List[str], raise_error: bool = True) -> List[BaseNode]

```

Get nodes from docstore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_ids` |  `List[str]` |  node ids |  _required_  
`raise_error` |  `bool` |  raise error if node_id not found |  `True`  
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
async def aget_nodes(self, node_ids: List[str], raise_error: bool = True) -> List[BaseNode]:
    """
    Get nodes from docstore.

    Args:
        node_ids (List[str]): node ids
        raise_error (bool): raise error if node_id not found

    """
    nodes: list[BaseNode] = []

    for node_id in node_ids:
        # if needed for type checking
        if not raise_error:
            if node := await self.aget_node(node_id=node_id, raise_error=False):
                nodes.append(node)
            continue

        nodes.append(await self.aget_node(node_id=node_id, raise_error=True))

    return nodes

```
  
---|---  
###  get_node #
```
get_node(node_id: str, raise_error: Literal[True] = True) -> BaseNode

```

```
get_node(node_id: str, raise_error: Literal[False] = False) -> Optional[BaseNode]

```

```
get_node(node_id: str, raise_error: bool = True) -> Optional[BaseNode]

```

Get node from docstore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_id` |  `str` |  node id |  _required_  
`raise_error` |  `bool` |  raise error if node_id not found |  `True`  
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
def get_node(self, node_id: str, raise_error: bool = True) -> Optional[BaseNode]:
    """
    Get node from docstore.

    Args:
        node_id (str): node id
        raise_error (bool): raise error if node_id not found

    """
    doc = self.get_document(node_id, raise_error=raise_error)

    if doc is None:
        # The doc store should have raised an error if the node_id is not found, but it didn't
        # so we raise an error here
        if raise_error:
            raise ValueError(f"Node {node_id} not found")
        return None

    # The document should always be a BaseNode, but we check to be safe
    if not isinstance(doc, BaseNode):
        raise ValueError(f"Document {node_id} is not a Node.")

    return doc

```
  
---|---  
###  aget_node `async` #
```
aget_node(node_id: str, raise_error: Literal[True] = True) -> BaseNode

```

```
aget_node(node_id: str, raise_error: Literal[False] = False) -> Optional[BaseNode]

```

```
aget_node(node_id: str, raise_error: bool = True) -> Optional[BaseNode]

```

Get node from docstore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_id` |  `str` |  node id |  _required_  
`raise_error` |  `bool` |  raise error if node_id not found |  `True`  
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
async def aget_node(self, node_id: str, raise_error: bool = True) -> Optional[BaseNode]:
    """
    Get node from docstore.

    Args:
        node_id (str): node id
        raise_error (bool): raise error if node_id not found

    """
    doc = await self.aget_document(node_id, raise_error=raise_error)

    if doc is None:
        # The doc store should have raised an error if the node_id is not found, but it didn't
        # so we raise an error here
        if raise_error:
            raise ValueError(f"Node {node_id} not found")
        return None

    # The document should always be a BaseNode, but we check to be safe
    if not isinstance(doc, BaseNode):
        raise ValueError(f"Document {node_id} is not a Node.")

    return doc

```
  
---|---  
###  get_node_dict #
```
get_node_dict(node_id_dict: Dict[int, str]) -> Dict[int, BaseNode]

```

Get node dict from docstore given a mapping of index to node ids.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_id_dict` |  `Dict[int, str]` |  mapping of index to node ids |  _required_  
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
def get_node_dict(self, node_id_dict: Dict[int, str]) -> Dict[int, BaseNode]:
    """
    Get node dict from docstore given a mapping of index to node ids.

    Args:
        node_id_dict (Dict[int, str]): mapping of index to node ids

    """
    return {index: self.get_node(node_id) for index, node_id in node_id_dict.items()}

```
  
---|---  
###  aget_node_dict `async` #
```
aget_node_dict(node_id_dict: Dict[int, str]) -> Dict[int, BaseNode]

```

Get node dict from docstore given a mapping of index to node ids.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`node_id_dict` |  `Dict[int, str]` |  mapping of index to node ids |  _required_  
Source code in `llama-index-core/llama_index/core/storage/docstore/types.py`

| ```
async def aget_node_dict(self, node_id_dict: Dict[int, str]) -> Dict[int, BaseNode]:
    """
    Get node dict from docstore given a mapping of index to node ids.

    Args:
        node_id_dict (Dict[int, str]): mapping of index to node ids

    """
    return {index: await self.aget_node(node_id) for index, node_id in node_id_dict.items()}

```
  
---|---
