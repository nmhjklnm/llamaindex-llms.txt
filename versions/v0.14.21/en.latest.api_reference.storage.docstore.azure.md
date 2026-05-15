# Azure
##  AzureDocumentStore #
Bases: `KVDocumentStore`
Azure Document (Node) store. An Azure Table store for Document and Node objects.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
class AzureDocumentStore(KVDocumentStore):
    """
    Azure Document (Node) store.
    An Azure Table store for Document and Node objects.
    """

    _kvstore: AzureKVStore

    def __init__(
        self,
        azure_kvstore: AzureKVStore,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """Initialize an AzureDocumentStore."""
        super().__init__(
            azure_kvstore,
            namespace,
            batch_size,
            node_collection_suffix,
            ref_doc_collection_suffix,
            metadata_collection_suffix,
        )

    @classmethod
    def from_connection_string(
        cls,
        connection_string: str,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        **kwargs,
    ) -> "AzureDocumentStore":
        """Initialize an AzureDocumentStore from an Azure connection string."""
        azure_kvstore = AzureKVStore.from_connection_string(
            connection_string,
            service_mode=service_mode,
            partition_key=partition_key,
        )
        return cls(
            azure_kvstore,
            namespace,
            node_collection_suffix,
            ref_doc_collection_suffix,
            metadata_collection_suffix,
            **kwargs,
        )

    @classmethod
    def from_account_and_key(
        cls,
        account_name: str,
        account_key: str,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        **kwargs,
    ) -> "AzureDocumentStore":
        """Initialize an AzureDocumentStore from an account name and key."""
        azure_kvstore = AzureKVStore.from_account_and_key(
            account_name,
            account_key,
            service_mode=service_mode,
            partition_key=partition_key,
        )
        return cls(
            azure_kvstore,
            namespace,
            node_collection_suffix,
            ref_doc_collection_suffix,
            metadata_collection_suffix,
            **kwargs,
        )

    @classmethod
    def from_account_and_id(
        cls,
        account_name: str,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        **kwargs,
    ) -> "AzureDocumentStore":
        """Initialize an AzureDocumentStore from an account name and managed ID."""
        azure_kvstore = AzureKVStore.from_account_and_id(
            account_name,
            service_mode=service_mode,
            partition_key=partition_key,
        )
        return cls(
            azure_kvstore,
            namespace,
            node_collection_suffix,
            ref_doc_collection_suffix,
            metadata_collection_suffix,
            **kwargs,
        )

    @classmethod
    def from_sas_token(
        cls,
        endpoint: str,
        sas_token: str,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        **kwargs,
    ) -> "AzureDocumentStore":
        """Initialize an AzureDocumentStore from a SAS token."""
        azure_kvstore = AzureKVStore.from_sas_token(
            endpoint,
            sas_token,
            service_mode=service_mode,
            partition_key=partition_key,
        )
        return cls(
            azure_kvstore,
            namespace,
            node_collection_suffix,
            ref_doc_collection_suffix,
            metadata_collection_suffix,
            **kwargs,
        )

    @classmethod
    def from_aad_token(
        cls,
        endpoint: str,
        namespace: Optional[str] = None,
        node_collection_suffix: Optional[str] = None,
        ref_doc_collection_suffix: Optional[str] = None,
        metadata_collection_suffix: Optional[str] = None,
        service_mode: ServiceMode = ServiceMode.STORAGE,
        partition_key: Optional[str] = None,
        **kwargs,
    ) -> "AzureDocumentStore":
        """Initialize an AzureDocumentStore from an AAD token."""
        azure_kvstore = AzureKVStore.from_aad_token(
            endpoint,
            service_mode=service_mode,
            partition_key=partition_key,
        )
        return cls(
            azure_kvstore,
            namespace,
            node_collection_suffix,
            ref_doc_collection_suffix,
            metadata_collection_suffix,
            **kwargs,
        )

    def _extract_doc_metadatas(
        self, ref_doc_kv_pairs: List[Tuple[str, dict]]
    ) -> List[Tuple[str, Optional[dict]]]:
        """Prepare reference document key-value pairs."""
        doc_metadatas: List[Tuple[str, dict]] = [
            (doc_id, {"metadata": doc_dict.get("metadata")})
            for doc_id, doc_dict in ref_doc_kv_pairs
        ]
        return doc_metadatas

    def add_documents(
        self,
        docs: Sequence[BaseNode],
        allow_update: bool = True,
        batch_size: Optional[int] = None,
        store_text: bool = True,
    ) -> None:
        """Add documents to the store."""
        batch_size = batch_size or self._batch_size

        node_kv_pairs, metadata_kv_pairs, ref_doc_kv_pairs = super()._prepare_kv_pairs(
            docs, allow_update, store_text
        )

        # Change ref_doc_kv_pairs
        ref_doc_kv_pairs = self._extract_doc_metadatas(ref_doc_kv_pairs)

        self._kvstore.put_all(
            node_kv_pairs,
            collection=self._node_collection,
            batch_size=batch_size,
        )

        self._kvstore.put_all(
            metadata_kv_pairs,
            collection=self._metadata_collection,
            batch_size=batch_size,
        )

        self._kvstore.put_all(
            ref_doc_kv_pairs,
            collection=self._ref_doc_collection,
            batch_size=batch_size,
        )

    async def async_add_documents(
        self,
        docs: Sequence[BaseNode],
        allow_update: bool = True,
        batch_size: Optional[int] = None,
        store_text: bool = True,
    ) -> None:
        """Add documents to the store."""
        batch_size = batch_size or self._batch_size

        (
            node_kv_pairs,
            metadata_kv_pairs,
            ref_doc_kv_pairs,
        ) = await super()._async_prepare_kv_pairs(docs, allow_update, store_text)

        # Change ref_doc_kv_pairs
        ref_doc_kv_pairs = self._extract_doc_metadatas(ref_doc_kv_pairs)

        await asyncio.gather(
            self._kvstore.aput_all(
                node_kv_pairs,
                collection=self._node_collection,
                batch_size=batch_size,
            ),
            self._kvstore.aput_all(
                metadata_kv_pairs,
                collection=self._metadata_collection,
                batch_size=batch_size,
            ),
            self._kvstore.aput_all(
                ref_doc_kv_pairs,
                collection=self._ref_doc_collection,
                batch_size=batch_size,
            ),
        )

    def get_ref_doc_info(self, ref_doc_id: str) -> Optional[RefDocInfo]:
        """Get the RefDocInfo for a given ref_doc_id."""
        ref_doc_infos = self._kvstore.query(
            f"PartitionKey eq '{self._kvstore.partition_key}' and ref_doc_id eq '{ref_doc_id}'",
            self._metadata_collection,
            select="RowKey",
        )

        node_ids = [doc["RowKey"] for doc in ref_doc_infos]
        if not node_ids:
            return None

        doc_metadata = self._kvstore.get(
            ref_doc_id, collection=self._ref_doc_collection, select="metadata"
        )

        ref_doc_info_dict = {
            "node_ids": node_ids,
            "metadata": doc_metadata.get("metadata"),
        }

        # TODO: deprecated legacy support
        return self._remove_legacy_info(ref_doc_info_dict)

    async def aget_ref_doc_info(self, ref_doc_id: str) -> Optional[RefDocInfo]:
        """Get the RefDocInfo for a given ref_doc_id."""
        metadatas = await self._kvstore.aquery(
            f"PartitionKey eq '{self._kvstore.partition_key}' and RowKey eq '{ref_doc_id}'",
            self._metadata_collection,
            select="RowKey",
        )

        node_ids = [metadata["RowKey"] async for metadata in metadatas]

        if not node_ids:
            return None

        doc_metadata = await self._kvstore.aget(
            ref_doc_id, collection=self._ref_doc_collection, select="metadata"
        )

        ref_doc_info_dict = {
            "node_ids": node_ids,
            "metadata": doc_metadata.get("metadata") if doc_metadata else None,
        }

        # TODO: deprecated legacy support
        return self._remove_legacy_info(ref_doc_info_dict)

    def get_all_ref_doc_info(self) -> Optional[Dict[str, RefDocInfo]]:
        """
        Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents.
        """
        ref_doc_infos = self._kvstore.query(
            f"PartitionKey eq '{self._kvstore.partition_key}'",
            self._metadata_collection,
            select=["RowKey", "ref_doc_id"],
        )

        # TODO: deprecated legacy support
        all_ref_doc_infos = defaultdict(lambda: {"node_ids": [], "metadata": None})
        for ref_doc_info in ref_doc_infos:
            ref_doc_id = ref_doc_info["ref_doc_id"]
            ref_doc_info_dict = all_ref_doc_infos[ref_doc_id]
            ref_doc_info_dict["node_ids"].append(ref_doc_info["RowKey"])

            if ref_doc_info_dict["metadata"] is None:
                ref_doc = self._kvstore.get(
                    ref_doc_id, collection=self._ref_doc_collection, select="metadata"
                )
                ref_doc_info_dict["metadata"] = ref_doc.get("metadata")

        for ref_doc_id, ref_doc_info_dict in all_ref_doc_infos.items():
            all_ref_doc_infos[ref_doc_id] = self._remove_legacy_info(ref_doc_info_dict)

        return all_ref_doc_infos

    async def aget_all_ref_doc_info(self) -> Optional[Dict[str, RefDocInfo]]:
        """
        Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents.
        """
        ref_doc_infos = await self._kvstore.aquery(
            f"PartitionKey eq '{self._kvstore.partition_key}'",
            self._metadata_collection,
            select=["RowKey", "ref_doc_id"],
        )

        # TODO: deprecated legacy support
        all_ref_doc_infos = defaultdict(lambda: {"node_ids": [], "metadata": None})
        async for ref_doc_info in ref_doc_infos:
            ref_doc_id = ref_doc_info["ref_doc_id"]
            ref_doc_info_dict = all_ref_doc_infos[ref_doc_id]
            ref_doc_info_dict["node_ids"].append(ref_doc_info["RowKey"])

            if ref_doc_info_dict["metadata"] is None:
                ref_doc = await self._kvstore.aget(
                    ref_doc_id, collection=self._ref_doc_collection, select="metadata"
                )
                ref_doc_info_dict["metadata"] = ref_doc.get("metadata")

        for ref_doc_id, ref_doc_info_dict in all_ref_doc_infos.items():
            all_ref_doc_infos[ref_doc_id] = self._remove_legacy_info(ref_doc_info_dict)

        return all_ref_doc_infos

    def _remove_from_ref_doc_node(self, doc_id: str) -> None:
        """
        Helper function to remove node doc_id from ref_doc_collection.
        If ref_doc has no more doc_ids, delete it from the collection.
        """
        self._kvstore.delete(doc_id, collection=self._metadata_collection)

    async def _aremove_from_ref_doc_node(self, doc_id: str) -> None:
        """
        Helper function to remove node doc_id from ref_doc_collection.
        If ref_doc has no more doc_ids, delete it from the collection.
        """
        await self._kvstore.adelete(doc_id, collection=self._metadata_collection)

```
  
---|---  
###  from_connection_string `classmethod` #
```
from_connection_string(connection_string: str, namespace: Optional[str] = None, node_collection_suffix: Optional[str] = None, ref_doc_collection_suffix: Optional[str] = None, metadata_collection_suffix: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, **kwargs) -> AzureDocumentStore

```

Initialize an AzureDocumentStore from an Azure connection string.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
@classmethod
def from_connection_string(
    cls,
    connection_string: str,
    namespace: Optional[str] = None,
    node_collection_suffix: Optional[str] = None,
    ref_doc_collection_suffix: Optional[str] = None,
    metadata_collection_suffix: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    **kwargs,
) -> "AzureDocumentStore":
    """Initialize an AzureDocumentStore from an Azure connection string."""
    azure_kvstore = AzureKVStore.from_connection_string(
        connection_string,
        service_mode=service_mode,
        partition_key=partition_key,
    )
    return cls(
        azure_kvstore,
        namespace,
        node_collection_suffix,
        ref_doc_collection_suffix,
        metadata_collection_suffix,
        **kwargs,
    )

```
  
---|---  
###  from_account_and_key `classmethod` #
```
from_account_and_key(account_name: str, account_key: str, namespace: Optional[str] = None, node_collection_suffix: Optional[str] = None, ref_doc_collection_suffix: Optional[str] = None, metadata_collection_suffix: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, **kwargs) -> AzureDocumentStore

```

Initialize an AzureDocumentStore from an account name and key.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
@classmethod
def from_account_and_key(
    cls,
    account_name: str,
    account_key: str,
    namespace: Optional[str] = None,
    node_collection_suffix: Optional[str] = None,
    ref_doc_collection_suffix: Optional[str] = None,
    metadata_collection_suffix: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    **kwargs,
) -> "AzureDocumentStore":
    """Initialize an AzureDocumentStore from an account name and key."""
    azure_kvstore = AzureKVStore.from_account_and_key(
        account_name,
        account_key,
        service_mode=service_mode,
        partition_key=partition_key,
    )
    return cls(
        azure_kvstore,
        namespace,
        node_collection_suffix,
        ref_doc_collection_suffix,
        metadata_collection_suffix,
        **kwargs,
    )

```
  
---|---  
###  from_account_and_id `classmethod` #
```
from_account_and_id(account_name: str, namespace: Optional[str] = None, node_collection_suffix: Optional[str] = None, ref_doc_collection_suffix: Optional[str] = None, metadata_collection_suffix: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, **kwargs) -> AzureDocumentStore

```

Initialize an AzureDocumentStore from an account name and managed ID.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
@classmethod
def from_account_and_id(
    cls,
    account_name: str,
    namespace: Optional[str] = None,
    node_collection_suffix: Optional[str] = None,
    ref_doc_collection_suffix: Optional[str] = None,
    metadata_collection_suffix: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    **kwargs,
) -> "AzureDocumentStore":
    """Initialize an AzureDocumentStore from an account name and managed ID."""
    azure_kvstore = AzureKVStore.from_account_and_id(
        account_name,
        service_mode=service_mode,
        partition_key=partition_key,
    )
    return cls(
        azure_kvstore,
        namespace,
        node_collection_suffix,
        ref_doc_collection_suffix,
        metadata_collection_suffix,
        **kwargs,
    )

```
  
---|---  
###  from_sas_token `classmethod` #
```
from_sas_token(endpoint: str, sas_token: str, namespace: Optional[str] = None, node_collection_suffix: Optional[str] = None, ref_doc_collection_suffix: Optional[str] = None, metadata_collection_suffix: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, **kwargs) -> AzureDocumentStore

```

Initialize an AzureDocumentStore from a SAS token.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
@classmethod
def from_sas_token(
    cls,
    endpoint: str,
    sas_token: str,
    namespace: Optional[str] = None,
    node_collection_suffix: Optional[str] = None,
    ref_doc_collection_suffix: Optional[str] = None,
    metadata_collection_suffix: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    **kwargs,
) -> "AzureDocumentStore":
    """Initialize an AzureDocumentStore from a SAS token."""
    azure_kvstore = AzureKVStore.from_sas_token(
        endpoint,
        sas_token,
        service_mode=service_mode,
        partition_key=partition_key,
    )
    return cls(
        azure_kvstore,
        namespace,
        node_collection_suffix,
        ref_doc_collection_suffix,
        metadata_collection_suffix,
        **kwargs,
    )

```
  
---|---  
###  from_aad_token `classmethod` #
```
from_aad_token(endpoint: str, namespace: Optional[str] = None, node_collection_suffix: Optional[str] = None, ref_doc_collection_suffix: Optional[str] = None, metadata_collection_suffix: Optional[str] = None, service_mode: ServiceMode = STORAGE, partition_key: Optional[str] = None, **kwargs) -> AzureDocumentStore

```

Initialize an AzureDocumentStore from an AAD token.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
@classmethod
def from_aad_token(
    cls,
    endpoint: str,
    namespace: Optional[str] = None,
    node_collection_suffix: Optional[str] = None,
    ref_doc_collection_suffix: Optional[str] = None,
    metadata_collection_suffix: Optional[str] = None,
    service_mode: ServiceMode = ServiceMode.STORAGE,
    partition_key: Optional[str] = None,
    **kwargs,
) -> "AzureDocumentStore":
    """Initialize an AzureDocumentStore from an AAD token."""
    azure_kvstore = AzureKVStore.from_aad_token(
        endpoint,
        service_mode=service_mode,
        partition_key=partition_key,
    )
    return cls(
        azure_kvstore,
        namespace,
        node_collection_suffix,
        ref_doc_collection_suffix,
        metadata_collection_suffix,
        **kwargs,
    )

```
  
---|---  
###  add_documents #
```
add_documents(docs: Sequence[BaseNode], allow_update: bool = True, batch_size: Optional[int] = None, store_text: bool = True) -> None

```

Add documents to the store.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
def add_documents(
    self,
    docs: Sequence[BaseNode],
    allow_update: bool = True,
    batch_size: Optional[int] = None,
    store_text: bool = True,
) -> None:
    """Add documents to the store."""
    batch_size = batch_size or self._batch_size

    node_kv_pairs, metadata_kv_pairs, ref_doc_kv_pairs = super()._prepare_kv_pairs(
        docs, allow_update, store_text
    )

    # Change ref_doc_kv_pairs
    ref_doc_kv_pairs = self._extract_doc_metadatas(ref_doc_kv_pairs)

    self._kvstore.put_all(
        node_kv_pairs,
        collection=self._node_collection,
        batch_size=batch_size,
    )

    self._kvstore.put_all(
        metadata_kv_pairs,
        collection=self._metadata_collection,
        batch_size=batch_size,
    )

    self._kvstore.put_all(
        ref_doc_kv_pairs,
        collection=self._ref_doc_collection,
        batch_size=batch_size,
    )

```
  
---|---  
###  async_add_documents `async` #
```
async_add_documents(docs: Sequence[BaseNode], allow_update: bool = True, batch_size: Optional[int] = None, store_text: bool = True) -> None

```

Add documents to the store.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
async def async_add_documents(
    self,
    docs: Sequence[BaseNode],
    allow_update: bool = True,
    batch_size: Optional[int] = None,
    store_text: bool = True,
) -> None:
    """Add documents to the store."""
    batch_size = batch_size or self._batch_size

    (
        node_kv_pairs,
        metadata_kv_pairs,
        ref_doc_kv_pairs,
    ) = await super()._async_prepare_kv_pairs(docs, allow_update, store_text)

    # Change ref_doc_kv_pairs
    ref_doc_kv_pairs = self._extract_doc_metadatas(ref_doc_kv_pairs)

    await asyncio.gather(
        self._kvstore.aput_all(
            node_kv_pairs,
            collection=self._node_collection,
            batch_size=batch_size,
        ),
        self._kvstore.aput_all(
            metadata_kv_pairs,
            collection=self._metadata_collection,
            batch_size=batch_size,
        ),
        self._kvstore.aput_all(
            ref_doc_kv_pairs,
            collection=self._ref_doc_collection,
            batch_size=batch_size,
        ),
    )

```
  
---|---  
###  get_ref_doc_info #
```
get_ref_doc_info(ref_doc_id: str) -> Optional[RefDocInfo]

```

Get the RefDocInfo for a given ref_doc_id.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
def get_ref_doc_info(self, ref_doc_id: str) -> Optional[RefDocInfo]:
    """Get the RefDocInfo for a given ref_doc_id."""
    ref_doc_infos = self._kvstore.query(
        f"PartitionKey eq '{self._kvstore.partition_key}' and ref_doc_id eq '{ref_doc_id}'",
        self._metadata_collection,
        select="RowKey",
    )

    node_ids = [doc["RowKey"] for doc in ref_doc_infos]
    if not node_ids:
        return None

    doc_metadata = self._kvstore.get(
        ref_doc_id, collection=self._ref_doc_collection, select="metadata"
    )

    ref_doc_info_dict = {
        "node_ids": node_ids,
        "metadata": doc_metadata.get("metadata"),
    }

    # TODO: deprecated legacy support
    return self._remove_legacy_info(ref_doc_info_dict)

```
  
---|---  
###  aget_ref_doc_info `async` #
```
aget_ref_doc_info(ref_doc_id: str) -> Optional[RefDocInfo]

```

Get the RefDocInfo for a given ref_doc_id.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
async def aget_ref_doc_info(self, ref_doc_id: str) -> Optional[RefDocInfo]:
    """Get the RefDocInfo for a given ref_doc_id."""
    metadatas = await self._kvstore.aquery(
        f"PartitionKey eq '{self._kvstore.partition_key}' and RowKey eq '{ref_doc_id}'",
        self._metadata_collection,
        select="RowKey",
    )

    node_ids = [metadata["RowKey"] async for metadata in metadatas]

    if not node_ids:
        return None

    doc_metadata = await self._kvstore.aget(
        ref_doc_id, collection=self._ref_doc_collection, select="metadata"
    )

    ref_doc_info_dict = {
        "node_ids": node_ids,
        "metadata": doc_metadata.get("metadata") if doc_metadata else None,
    }

    # TODO: deprecated legacy support
    return self._remove_legacy_info(ref_doc_info_dict)

```
  
---|---  
###  get_all_ref_doc_info #
```
get_all_ref_doc_info() -> Optional[Dict[str, RefDocInfo]]

```

Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
def get_all_ref_doc_info(self) -> Optional[Dict[str, RefDocInfo]]:
    """
    Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents.
    """
    ref_doc_infos = self._kvstore.query(
        f"PartitionKey eq '{self._kvstore.partition_key}'",
        self._metadata_collection,
        select=["RowKey", "ref_doc_id"],
    )

    # TODO: deprecated legacy support
    all_ref_doc_infos = defaultdict(lambda: {"node_ids": [], "metadata": None})
    for ref_doc_info in ref_doc_infos:
        ref_doc_id = ref_doc_info["ref_doc_id"]
        ref_doc_info_dict = all_ref_doc_infos[ref_doc_id]
        ref_doc_info_dict["node_ids"].append(ref_doc_info["RowKey"])

        if ref_doc_info_dict["metadata"] is None:
            ref_doc = self._kvstore.get(
                ref_doc_id, collection=self._ref_doc_collection, select="metadata"
            )
            ref_doc_info_dict["metadata"] = ref_doc.get("metadata")

    for ref_doc_id, ref_doc_info_dict in all_ref_doc_infos.items():
        all_ref_doc_infos[ref_doc_id] = self._remove_legacy_info(ref_doc_info_dict)

    return all_ref_doc_infos

```
  
---|---  
###  aget_all_ref_doc_info `async` #
```
aget_all_ref_doc_info() -> Optional[Dict[str, RefDocInfo]]

```

Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents.
Source code in `llama-index-integrations/storage/docstore/llama-index-storage-docstore-azure/llama_index/storage/docstore/azure/base.py`

| ```
async def aget_all_ref_doc_info(self) -> Optional[Dict[str, RefDocInfo]]:
    """
    Get a mapping of ref_doc_id -> RefDocInfo for all ingested documents.
    """
    ref_doc_infos = await self._kvstore.aquery(
        f"PartitionKey eq '{self._kvstore.partition_key}'",
        self._metadata_collection,
        select=["RowKey", "ref_doc_id"],
    )

    # TODO: deprecated legacy support
    all_ref_doc_infos = defaultdict(lambda: {"node_ids": [], "metadata": None})
    async for ref_doc_info in ref_doc_infos:
        ref_doc_id = ref_doc_info["ref_doc_id"]
        ref_doc_info_dict = all_ref_doc_infos[ref_doc_id]
        ref_doc_info_dict["node_ids"].append(ref_doc_info["RowKey"])

        if ref_doc_info_dict["metadata"] is None:
            ref_doc = await self._kvstore.aget(
                ref_doc_id, collection=self._ref_doc_collection, select="metadata"
            )
            ref_doc_info_dict["metadata"] = ref_doc.get("metadata")

    for ref_doc_id, ref_doc_info_dict in all_ref_doc_infos.items():
        all_ref_doc_infos[ref_doc_id] = self._remove_legacy_info(ref_doc_info_dict)

    return all_ref_doc_infos

```
  
---|---
