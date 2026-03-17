# Mongodb
##  MongoDBKVStore #
Bases: `BaseKVStore`
MongoDB Key-Value store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`mongo_client` |  `Any` |  MongoDB client |  _required_  
`uri` |  `Optional[str]` |  MongoDB URI |  `None`  
`host` |  `Optional[str]` |  MongoDB host |  `None`  
`port` |  `Optional[int]` |  MongoDB port |  `None`  
`db_name` |  `Optional[str]` |  MongoDB database name |  `None`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
class MongoDBKVStore(BaseKVStore):
    """
    MongoDB Key-Value store.

    Args:
        mongo_client (Any): MongoDB client
        uri (Optional[str]): MongoDB URI
        host (Optional[str]): MongoDB host
        port (Optional[int]): MongoDB port
        db_name (Optional[str]): MongoDB database name

    """

    def __init__(
        self,
        mongo_client: Any,
        mongo_aclient: Optional[Any] = None,
        uri: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        db_name: Optional[str] = None,
    ) -> None:
        """Init a MongoDBKVStore."""
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            from pymongo import MongoClient
        except ImportError:
            raise ImportError(IMPORT_ERROR_MSG)

        self._client = cast(MongoClient, mongo_client)
        self._aclient = (
            cast(AsyncIOMotorClient, mongo_aclient) if mongo_aclient else None
        )

        self._uri = uri
        self._host = host
        self._port = port

        self._db_name = db_name or "db_docstore"
        self._db = self._client[self._db_name]
        self._adb = self._aclient[self._db_name] if self._aclient else None

    @classmethod
    def from_uri(
        cls,
        uri: str,
        db_name: Optional[str] = None,
    ) -> "MongoDBKVStore":
        """
        Load a MongoDBKVStore from a MongoDB URI.

        Args:
            uri (str): MongoDB URI
            db_name (Optional[str]): MongoDB database name

        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            from pymongo import MongoClient
        except ImportError:
            raise ImportError(IMPORT_ERROR_MSG)

        mongo_client: MongoClient = MongoClient(uri, appname=APP_NAME)
        mongo_aclient: AsyncIOMotorClient = AsyncIOMotorClient(uri)
        return cls(
            mongo_client=mongo_client,
            mongo_aclient=mongo_aclient,
            db_name=db_name,
            uri=uri,
        )

    @classmethod
    def from_host_and_port(
        cls,
        host: str,
        port: int,
        db_name: Optional[str] = None,
    ) -> "MongoDBKVStore":
        """
        Load a MongoDBKVStore from a MongoDB host and port.

        Args:
            host (str): MongoDB host
            port (int): MongoDB port
            db_name (Optional[str]): MongoDB database name

        """
        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            from pymongo import MongoClient
        except ImportError:
            raise ImportError(IMPORT_ERROR_MSG)

        mongo_client: MongoClient = MongoClient(host, port, appname=APP_NAME)
        mongo_aclient: AsyncIOMotorClient = AsyncIOMotorClient(
            host, port, appname=APP_NAME
        )
        return cls(
            mongo_client=mongo_client,
            mongo_aclient=mongo_aclient,
            db_name=db_name,
            host=host,
            port=port,
        )

    def _check_async_client(self) -> None:
        if self._adb is None:
            raise ValueError("MongoDBKVStore was not initialized with an async client")

    def put(
        self,
        key: str,
        val: dict,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        self.put_all([(key, val)], collection=collection)

    async def aput(
        self,
        key: str,
        val: dict,
        collection: str = DEFAULT_COLLECTION,
    ) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        await self.aput_all([(key, val)], collection=collection)

    def put_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        from pymongo import UpdateOne

        # Prepare documents with '_id' set to the key for batch insertion
        docs = [{"_id": key, **value} for key, value in kv_pairs]

        # Insert documents in batches
        for batch in (
            docs[i : i + batch_size] for i in range(0, len(docs), batch_size)
        ):
            new_docs = []
            for doc in batch:
                new_docs.append(
                    UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
                )

            self._db[collection].bulk_write(new_docs)

    async def aput_all(
        self,
        kv_pairs: List[Tuple[str, dict]],
        collection: str = DEFAULT_COLLECTION,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        from pymongo import UpdateOne

        self._check_async_client()

        # Prepare documents with '_id' set to the key for batch insertion
        docs = [{"_id": key, **value} for key, value in kv_pairs]

        # Insert documents in batches
        for batch in (
            docs[i : i + batch_size] for i in range(0, len(docs), batch_size)
        ):
            new_docs = []
            for doc in batch:
                new_docs.append(
                    UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
                )

            await self._adb[collection].bulk_write(new_docs)

    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        result = self._db[collection].find_one({"_id": key})
        if result is not None:
            result.pop("_id")
            return result
        return None

    async def aget(
        self, key: str, collection: str = DEFAULT_COLLECTION
    ) -> Optional[dict]:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        self._check_async_client()

        result = await self._adb[collection].find_one({"_id": key})
        if result is not None:
            result.pop("_id")
            return result
        return None

    def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the store.

        Args:
            collection (str): collection name

        """
        results = self._db[collection].find()
        output = {}
        for result in results:
            key = result.pop("_id")
            output[key] = result
        return output

    async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the store.

        Args:
            collection (str): collection name

        """
        self._check_async_client()

        results = self._adb[collection].find()
        output = {}
        for result in await results.to_list(length=None):
            key = result.pop("_id")
            output[key] = result
        return output

    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        result = self._db[collection].delete_one({"_id": key})
        return result.deleted_count > 0

    async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        self._check_async_client()

        result = await self._adb[collection].delete_one({"_id": key})
        return result.deleted_count > 0

```
  
---|---  
###  from_uri `classmethod` #
```
from_uri(uri: str, db_name: Optional[str] = None) -> MongoDBKVStore

```

Load a MongoDBKVStore from a MongoDB URI.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`uri` |  `str` |  MongoDB URI |  _required_  
`db_name` |  `Optional[str]` |  MongoDB database name |  `None`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
@classmethod
def from_uri(
    cls,
    uri: str,
    db_name: Optional[str] = None,
) -> "MongoDBKVStore":
    """
    Load a MongoDBKVStore from a MongoDB URI.

    Args:
        uri (str): MongoDB URI
        db_name (Optional[str]): MongoDB database name

    """
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from pymongo import MongoClient
    except ImportError:
        raise ImportError(IMPORT_ERROR_MSG)

    mongo_client: MongoClient = MongoClient(uri, appname=APP_NAME)
    mongo_aclient: AsyncIOMotorClient = AsyncIOMotorClient(uri)
    return cls(
        mongo_client=mongo_client,
        mongo_aclient=mongo_aclient,
        db_name=db_name,
        uri=uri,
    )

```
  
---|---  
###  from_host_and_port `classmethod` #
```
from_host_and_port(host: str, port: int, db_name: Optional[str] = None) -> MongoDBKVStore

```

Load a MongoDBKVStore from a MongoDB host and port.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`host` |  `str` |  MongoDB host |  _required_  
`port` |  `int` |  MongoDB port |  _required_  
`db_name` |  `Optional[str]` |  MongoDB database name |  `None`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
@classmethod
def from_host_and_port(
    cls,
    host: str,
    port: int,
    db_name: Optional[str] = None,
) -> "MongoDBKVStore":
    """
    Load a MongoDBKVStore from a MongoDB host and port.

    Args:
        host (str): MongoDB host
        port (int): MongoDB port
        db_name (Optional[str]): MongoDB database name

    """
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from pymongo import MongoClient
    except ImportError:
        raise ImportError(IMPORT_ERROR_MSG)

    mongo_client: MongoClient = MongoClient(host, port, appname=APP_NAME)
    mongo_aclient: AsyncIOMotorClient = AsyncIOMotorClient(
        host, port, appname=APP_NAME
    )
    return cls(
        mongo_client=mongo_client,
        mongo_aclient=mongo_aclient,
        db_name=db_name,
        host=host,
        port=port,
    )

```
  
---|---  
###  put #
```
put(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
def put(
    self,
    key: str,
    val: dict,
    collection: str = DEFAULT_COLLECTION,
) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    self.put_all([(key, val)], collection=collection)

```
  
---|---  
###  aput `async` #
```
aput(key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None

```

Put a key-value pair into the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`val` |  `dict` |  value |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
async def aput(
    self,
    key: str,
    val: dict,
    collection: str = DEFAULT_COLLECTION,
) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    await self.aput_all([(key, val)], collection=collection)

```
  
---|---  
###  get #
```
get(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    result = self._db[collection].find_one({"_id": key})
    if result is not None:
        result.pop("_id")
        return result
    return None

```
  
---|---  
###  aget `async` #
```
aget(key: str, collection: str = DEFAULT_COLLECTION) -> Optional[dict]

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
async def aget(
    self, key: str, collection: str = DEFAULT_COLLECTION
) -> Optional[dict]:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    self._check_async_client()

    result = await self._adb[collection].find_one({"_id": key})
    if result is not None:
        result.pop("_id")
        return result
    return None

```
  
---|---  
###  get_all #
```
get_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the store.

    Args:
        collection (str): collection name

    """
    results = self._db[collection].find()
    output = {}
    for result in results:
        key = result.pop("_id")
        output[key] = result
    return output

```
  
---|---  
###  aget_all `async` #
```
aget_all(collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]

```

Get all values from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the store.

    Args:
        collection (str): collection name

    """
    self._check_async_client()

    results = self._adb[collection].find()
    output = {}
    for result in await results.to_list(length=None):
        key = result.pop("_id")
        output[key] = result
    return output

```
  
---|---  
###  delete #
```
delete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    result = self._db[collection].delete_one({"_id": key})
    return result.deleted_count > 0

```
  
---|---  
###  adelete `async` #
```
adelete(key: str, collection: str = DEFAULT_COLLECTION) -> bool

```

Delete a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-mongodb/llama_index/storage/kvstore/mongodb/base.py`

| ```
async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    self._check_async_client()

    result = await self._adb[collection].delete_one({"_id": key})
    return result.deleted_count > 0

```
  
---|---
