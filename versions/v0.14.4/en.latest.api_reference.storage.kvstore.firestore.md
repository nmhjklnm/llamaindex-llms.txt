# Firestore
##  FirestoreKVStore #
Bases: `BaseKVStore`
Firestore Key-Value store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`project` |  `str` |  The project which the client acts on behalf of. |  `None`  
`database` |  `str` |  The database name that the client targets. |  `DEFAULT_FIRESTORE_DATABASE`  
`credentials` |  `Credentials` |  The OAuth2 Credentials to access Firestore. If not passed, falls back to the default inferred from the environment. |  `None`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
class FirestoreKVStore(BaseKVStore):
    """
    Firestore Key-Value store.

    Args:
        project (str): The project which the client acts on behalf of.
        database (str): The database name that the client targets.
        credentials (google.auth.credentials.Credentials): The OAuth2
            Credentials to access Firestore. If not passed, falls back
            to the default inferred from the environment.

    """

    def __init__(
        self,
        project: Optional[str] = None,
        database: str = DEFAULT_FIRESTORE_DATABASE,
        credentials: Optional[Credentials] = None,
    ) -> None:
        client_info = DEFAULT_CLIENT_INFO
        client_info.user_agent = USER_AGENT
        self._adb = AsyncClient(
            project=project,
            database=database,
            client_info=client_info,
            credentials=credentials,
        )
        self._db = Client(
            project=project,
            database=database,
            client_info=client_info,
            credentials=credentials,
        )

    def firestore_collection(self, collection: str) -> str:
        return collection.replace("/", SLASH_REPLACEMENT)

    def replace_field_name_set(self, val: Dict[str, Any]) -> Dict[str, Any]:
        val = val.copy()
        for k, v in FIELD_NAME_REPLACE_SET.items():
            if k in val:
                val[v] = val[k]
                val.pop(k)
        return val

    def replace_field_name_get(self, val: Dict[str, Any]) -> Dict[str, Any]:
        val = val.copy()
        for k, v in FIELD_NAME_REPLACE_GET.items():
            if k in val:
                val[v] = val[k]
                val.pop(k)
        return val

    def put(
        self,
        key: str,
        val: dict,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        """
        Put a key-value pair into the Firestore collection.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        collection_id = self.firestore_collection(collection)
        val = self.replace_field_name_set(val)
        doc = self._db.collection(collection_id).document(key)
        doc.set(val, merge=True)

    async def aput(
        self,
        key: str,
        val: dict,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        """
        Put a key-value pair into the Firestore collection.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        collection_id = self.firestore_collection(collection)
        val = self.replace_field_name_set(val)
        doc = self._adb.collection(collection_id).document(key)
        await doc.set(val, merge=True)

    def put_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        batch = self._db.batch()
        for i, (key, val) in enumerate(kv_pairs, start=1):
            collection_id = self.firestore_collection(collection)
            val = self.replace_field_name_set(val)
            batch.set(self._db.collection(collection_id).document(key), val, merge=True)
            if i % batch_size == 0:
                batch.commit()
                batch = self._db.batch()
        batch.commit()

    async def aput_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        """
        Put a dictionary of key-value pairs into the Firestore collection.

        Args:
            kv_pairs (List[Tuple[str, dict]]): key-value pairs
            collection (str): collection name

        """
        batch = self._adb.batch()
        for i, (key, val) in enumerate(kv_pairs, start=1):
            collection_id = self.firestore_collection(collection)
            doc = self._adb.collection(collection_id).document(key)
            val = self.replace_field_name_set(val)
            batch.set(doc, val, merge=True)
            if i % batch_size == 0:
                await batch.commit()
                batch = self._adb.batch()
        await batch.commit()

    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
        """
        Get a key-value pair from the Firestore.

        Args:
            key (str): key
            collection (str): collection name

        """
        collection_id = self.firestore_collection(collection)
        result = self._db.collection(collection_id).document(key).get().to_dict()
        if not result:
            return None

        return self.replace_field_name_get(result)

    async def aget(
        self, key: str, collection: str = DEFAULT_COLLECTION
    ) -> Optional[dict]:
        """
        Get a key-value pair from the Firestore.

        Args:
            key (str): key
            collection (str): collection name

        """
        collection_id = self.firestore_collection(collection)
        result = (
            await self._adb.collection(collection_id).document(key).get()
        ).to_dict()
        if not result:
            return None

        return self.replace_field_name_get(result)

    def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the Firestore collection.

        Args:
            collection (str): collection name

        """
        collection_id = self.firestore_collection(collection)
        docs = self._db.collection(collection_id).list_documents()
        output = {}
        for doc in docs:
            key = doc.id
            val = self.replace_field_name_get(doc.get().to_dict())
            output[key] = val
        return output

    async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the Firestore collection.

        Args:
            collection (str): collection name

        """
        collection_id = self.firestore_collection(collection)
        docs = self._adb.collection(collection_id).list_documents()
        output = {}
        async for doc in docs:
            key = doc.id
            data = (await doc.get()).to_dict()
            if data is None:
                continue
            val = self.replace_field_name_get(data)
            output[key] = val
        return output

    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the Firestore.

        Args:
            key (str): key
            collection (str): collection name

        """
        collection_id = self.firestore_collection(collection)
        doc = self._db.collection(collection_id).document(key)
        doc.delete()
        return True

    async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the Firestore.

        Args:
            key (str): key
            collection (str): collection name

        """
        collection_id = self.firestore_collection(collection)
        doc = self._adb.collection(collection_id).document(key)
        await doc.delete()
        return True

```
  
---|---  
###  put #
```
put(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the Firestore collection.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
def put(
    self,
    key: str,
    val: dict,
    collection: str = DEFAULT_COLLECTION,
) -> None:
    """
    Put a key-value pair into the Firestore collection.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    collection_id = self.firestore_collection(collection)
    val = self.replace_field_name_set(val)
    doc = self._db.collection(collection_id).document(key)
    doc.set(val, merge=True)

```
  
---|---  
###  aput `async` #
```
aput(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the Firestore collection.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
async def aput(
    self,
    key: str,
    val: dict,
    collection: str = DEFAULT_COLLECTION,
) -> None:
    """
    Put a key-value pair into the Firestore collection.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    collection_id = self.firestore_collection(collection)
    val = self.replace_field_name_set(val)
    doc = self._adb.collection(collection_id).document(key)
    await doc.set(val, merge=True)

```
  
---|---  
###  aput_all `async` #
```
aput_all(kv_pairs: List[Tuple[str, dict]], collection: str = DEFAULT_COLLECTION, batch_size: int = DEFAULT_BATCH_SIZE) -> None

```

Put a dictionary of key-value pairs into the Firestore collection.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`kv_pairs` |  `List[Tuple[str, dict]]` |  key-value pairs |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
async def aput_all(
    self,
    kv_pairs: List[Tuple[str, dict]],
    collection: str = DEFAULT_COLLECTION,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> None:
    """
    Put a dictionary of key-value pairs into the Firestore collection.

    Args:
        kv_pairs (List[Tuple[str, dict]]): key-value pairs
        collection (str): collection name

    """
    batch = self._adb.batch()
    for i, (key, val) in enumerate(kv_pairs, start=1):
        collection_id = self.firestore_collection(collection)
        doc = self._adb.collection(collection_id).document(key)
        val = self.replace_field_name_set(val)
        batch.set(doc, val, merge=True)
        if i % batch_size == 0:
            await batch.commit()
            batch = self._adb.batch()
    await batch.commit()

```
  
---|---  
###  get #
```
get(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a key-value pair from the Firestore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
    """
    Get a key-value pair from the Firestore.

    Args:
        key (str): key
        collection (str): collection name

    """
    collection_id = self.firestore_collection(collection)
    result = self._db.collection(collection_id).document(key).get().to_dict()
    if not result:
        return None

    return self.replace_field_name_get(result)

```
  
---|---  
###  aget `async` #
```
aget(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a key-value pair from the Firestore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
async def aget(
    self, key: str, collection: str = DEFAULT_COLLECTION
) -> Optional[dict]:
    """
    Get a key-value pair from the Firestore.

    Args:
        key (str): key
        collection (str): collection name

    """
    collection_id = self.firestore_collection(collection)
    result = (
        await self._adb.collection(collection_id).document(key).get()
    ).to_dict()
    if not result:
        return None

    return self.replace_field_name_get(result)

```
  
---|---  
###  get_all #
```
get_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the Firestore collection.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the Firestore collection.

    Args:
        collection (str): collection name

    """
    collection_id = self.firestore_collection(collection)
    docs = self._db.collection(collection_id).list_documents()
    output = {}
    for doc in docs:
        key = doc.id
        val = self.replace_field_name_get(doc.get().to_dict())
        output[key] = val
    return output

```
  
---|---  
###  aget_all `async` #
```
aget_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the Firestore collection.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the Firestore collection.

    Args:
        collection (str): collection name

    """
    collection_id = self.firestore_collection(collection)
    docs = self._adb.collection(collection_id).list_documents()
    output = {}
    async for doc in docs:
        key = doc.id
        data = (await doc.get()).to_dict()
        if data is None:
            continue
        val = self.replace_field_name_get(data)
        output[key] = val
    return output

```
  
---|---  
###  delete #
```
delete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the Firestore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the Firestore.

    Args:
        key (str): key
        collection (str): collection name

    """
    collection_id = self.firestore_collection(collection)
    doc = self._db.collection(collection_id).document(key)
    doc.delete()
    return True

```
  
---|---  
###  adelete `async` #
```
adelete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the Firestore.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-firestore/llama_index/storage/kvstore/firestore/base.py`

| ```
async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the Firestore.

    Args:
        key (str): key
        collection (str): collection name

    """
    collection_id = self.firestore_collection(collection)
    doc = self._adb.collection(collection_id).document(key)
    await doc.delete()
    return True

```
  
---|---
