# Mongo
##  MongoChatStore #
Bases: `BaseChatStore`
MongoDB chat store implementation.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
class MongoChatStore(BaseChatStore):
    """MongoDB chat store implementation."""

    mongo_uri: str = Field(
        default="mongodb://localhost:27017", description="MongoDB URI."
    )
    db_name: str = Field(default="default", description="MongoDB database name.")
    collection_name: str = Field(
        default="sessions", description="MongoDB collection name."
    )
    ttl_seconds: Optional[int] = Field(
        default=None, description="Time to live in seconds."
    )
    _mongo_client: Optional[MongoClient] = PrivateAttr()
    _async_client: Optional[AsyncIOMotorClient] = PrivateAttr()

    def __init__(
        self,
        mongo_uri: str = "mongodb://localhost:27017",
        db_name: str = "default",
        collection_name: str = "sessions",
        mongo_client: Optional[MongoClient] = None,
        amongo_client: Optional[AsyncIOMotorClient] = None,
        ttl_seconds: Optional[int] = None,
        collection: Optional[Collection] = None,
        async_collection: Optional[AsyncIOMotorCollection] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the MongoDB chat store.

        Args:
            mongo_uri: MongoDB connection URI
            db_name: Database name
            collection_name: Collection name for storing chat messages
            mongo_client: Optional pre-configured MongoDB client
            amongo_client: Optional pre-configured async MongoDB client
            ttl_seconds: Optional time-to-live for messages in seconds
            **kwargs: Additional arguments to pass to MongoDB client

        """
        super().__init__(ttl=ttl_seconds)

        self._mongo_client = mongo_client or MongoClient(mongo_uri, **kwargs)
        self._async_client = amongo_client or AsyncIOMotorClient(mongo_uri, **kwargs)

        if collection:
            self._collection = collection
        else:
            self._collection = self._mongo_client[db_name][collection_name]

        if async_collection:
            self._async_collection = async_collection
        else:
            self._async_collection = self._async_client[db_name][collection_name]

        # Create TTL index if ttl is specified
        if ttl_seconds:
            self._collection.create_index("created_at", expireAfterSeconds=ttl_seconds)

    @classmethod
    def class_name(cls) -> str:
        """Get class name."""
        return "MongoChatStore"

    def set_messages(self, key: str, messages: List[ChatMessage]) -> None:
        """
        Set messages for a key.

        Args:
            key: Key to set messages for
            messages: List of ChatMessage objects

        """
        # Delete existing messages for this key
        self._collection.delete_many({"session_id": key})

        # Insert new messages
        if messages:
            current_time = datetime.now()
            message_dicts = [
                {
                    "session_id": key,
                    "index": i,
                    "message": _message_to_dict(msg),
                    "created_at": current_time,
                }
                for i, msg in enumerate(messages)
            ]
            self._collection.insert_many(message_dicts)

    async def aset_messages(self, key: str, messages: List[ChatMessage]) -> None:
        """
        Set messages for a key asynchronously.

        Args:
            key: Key to set messages for
            messages: List of ChatMessage objects

        """
        # Delete existing messages for this key
        await self._async_collection.delete_many({"session_id": key})

        # Insert new messages
        if messages:
            current_time = datetime.now()
            message_dicts = [
                {
                    "session_id": key,
                    "index": i,
                    "message": _message_to_dict(msg),
                    "created_at": current_time,
                }
                for i, msg in enumerate(messages)
            ]
            await self._async_collection.insert_many(message_dicts)

    def get_messages(self, key: str) -> List[ChatMessage]:
        """
        Get messages for a key.

        Args:
            key: Key to get messages for

        """
        # Find all messages for this key, sorted by index
        docs = list(self._collection.find({"session_id": key}, sort=[("index", 1)]))

        # Convert to ChatMessage objects
        return [_dict_to_message(doc["message"]) for doc in docs]

    async def aget_messages(self, key: str) -> List[ChatMessage]:
        """
        Get messages for a key asynchronously.

        Args:
            key: Key to get messages for

        """
        # Find all messages for this key, sorted by index
        cursor = self._async_collection.find({"session_id": key}).sort("index", 1)

        # Convert to list and then to ChatMessage objects
        docs = await cursor.to_list(length=None)
        return [_dict_to_message(doc["message"]) for doc in docs]

    def add_message(
        self, key: str, message: ChatMessage, idx: Optional[int] = None
    ) -> None:
        """
        Add a message for a key.

        Args:
            key: Key to add message for
            message: ChatMessage object to add

        """
        if idx is None:
            # Get the current highest index
            highest_idx_doc = self._collection.find_one(
                {"session_id": key}, sort=[("index", -1)]
            )
            idx = 0 if highest_idx_doc is None else highest_idx_doc["index"] + 1

        # Insert the new message with current timestamp
        self._collection.insert_one(
            {
                "session_id": key,
                "index": idx,
                "message": _message_to_dict(message),
                "created_at": datetime.now(),
            }
        )

    async def async_add_message(
        self, key: str, message: ChatMessage, idx: Optional[int] = None
    ) -> None:
        """
        Add a message for a key asynchronously.

        Args:
            key: Key to add message for
            message: ChatMessage object to add

        """
        if idx is None:
            # Get the current highest index
            highest_idx_doc = await self._async_collection.find_one(
                {"session_id": key}, sort=[("index", -1)]
            )
            idx = 0 if highest_idx_doc is None else highest_idx_doc["index"] + 1

        # Insert the new message with current timestamp
        await self._async_collection.insert_one(
            {
                "session_id": key,
                "index": idx,
                "message": _message_to_dict(message),
                "created_at": datetime.now(),
            }
        )

    def delete_messages(self, key: str) -> Optional[List[ChatMessage]]:
        """
        Delete messages for a key.

        Args:
            key: Key to delete messages for

        """
        # Get messages before deleting
        messages = self.get_messages(key)

        # Delete all messages for this key
        self._collection.delete_many({"session_id": key})

        return messages

    async def adelete_messages(self, key: str) -> Optional[List[ChatMessage]]:
        """
        Delete messages for a key asynchronously.

        Args:
            key: Key to delete messages for

        """
        # Get messages before deleting
        messages = await self.aget_messages(key)

        # Delete all messages for this key
        await self._async_collection.delete_many({"session_id": key})

        return messages

    def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """
        Delete specific message for a key.

        Args:
            key: Key to delete message for
            idx: Index of message to delete

        """
        # Find the message to delete
        doc = self._collection.find_one({"session_id": key, "index": idx})
        if doc is None:
            return None

        # Delete the message
        self._collection.delete_one({"session_id": key, "index": idx})

        # Reindex remaining messages
        self._collection.update_many(
            {"session_id": key, "index": {"$gt": idx}}, {"$inc": {"index": -1}}
        )

        return _dict_to_message(doc["message"])

    async def adelete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
        """
        Delete specific message for a key asynchronously.

        Args:
            key: Key to delete message for
            idx: Index of message to delete

        """
        # Find the message to delete
        doc = await self._async_collection.find_one({"session_id": key, "index": idx})
        if doc is None:
            return None

        # Delete the message
        await self._async_collection.delete_one({"session_id": key, "index": idx})

        # Reindex remaining messages
        await self._async_collection.update_many(
            {"session_id": key, "index": {"$gt": idx}}, {"$inc": {"index": -1}}
        )

        return _dict_to_message(doc["message"])

    def delete_last_message(self, key: str) -> Optional[ChatMessage]:
        """
        Delete last message for a key.

        Args:
            key: Key to delete last message for

        """
        # Find the last message
        last_msg_doc = self._collection.find_one(
            {"session_id": key}, sort=[("index", -1)]
        )

        if last_msg_doc is None:
            return None

        # Delete the last message
        self._collection.delete_one({"_id": last_msg_doc["_id"]})

        return _dict_to_message(last_msg_doc["message"])

    async def adelete_last_message(self, key: str) -> Optional[ChatMessage]:
        """
        Delete last message for a key asynchronously.

        Args:
            key: Key to delete last message for

        """
        # Find the last message
        last_msg_doc = await self._async_collection.find_one(
            {"session_id": key}, sort=[("index", -1)]
        )

        if last_msg_doc is None:
            return None

        # Delete the last message
        await self._async_collection.delete_one({"_id": last_msg_doc["_id"]})

        return _dict_to_message(last_msg_doc["message"])

    def get_keys(self) -> List[str]:
        """
        Get all keys (session IDs).

        Returns:
            List of session IDs

        """
        # Get distinct session IDs
        return self._collection.distinct("session_id")

    async def aget_keys(self) -> List[str]:
        """
        Get all keys (session IDs) asynchronously.

        Returns:
            List of session IDs

        """
        # Get distinct session IDs
        return await self._async_collection.distinct("session_id")

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Get class name.
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Get class name."""
    return "MongoChatStore"

```
  
---|---  
###  set_messages #
```
set_messages(key: str, messages: List[ChatMessage]) -> None

```

Set messages for a key.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to set messages for |  _required_  
`messages` |  `List[ChatMessage]` |  List of ChatMessage objects |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
def set_messages(self, key: str, messages: List[ChatMessage]) -> None:
    """
    Set messages for a key.

    Args:
        key: Key to set messages for
        messages: List of ChatMessage objects

    """
    # Delete existing messages for this key
    self._collection.delete_many({"session_id": key})

    # Insert new messages
    if messages:
        current_time = datetime.now()
        message_dicts = [
            {
                "session_id": key,
                "index": i,
                "message": _message_to_dict(msg),
                "created_at": current_time,
            }
            for i, msg in enumerate(messages)
        ]
        self._collection.insert_many(message_dicts)

```
  
---|---  
###  aset_messages `async` #
```
aset_messages(key: str, messages: List[ChatMessage]) -> None

```

Set messages for a key asynchronously.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to set messages for |  _required_  
`messages` |  `List[ChatMessage]` |  List of ChatMessage objects |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
async def aset_messages(self, key: str, messages: List[ChatMessage]) -> None:
    """
    Set messages for a key asynchronously.

    Args:
        key: Key to set messages for
        messages: List of ChatMessage objects

    """
    # Delete existing messages for this key
    await self._async_collection.delete_many({"session_id": key})

    # Insert new messages
    if messages:
        current_time = datetime.now()
        message_dicts = [
            {
                "session_id": key,
                "index": i,
                "message": _message_to_dict(msg),
                "created_at": current_time,
            }
            for i, msg in enumerate(messages)
        ]
        await self._async_collection.insert_many(message_dicts)

```
  
---|---  
###  get_messages #
```
get_messages(key: str) -> List[ChatMessage]

```

Get messages for a key.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to get messages for |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
def get_messages(self, key: str) -> List[ChatMessage]:
    """
    Get messages for a key.

    Args:
        key: Key to get messages for

    """
    # Find all messages for this key, sorted by index
    docs = list(self._collection.find({"session_id": key}, sort=[("index", 1)]))

    # Convert to ChatMessage objects
    return [_dict_to_message(doc["message"]) for doc in docs]

```
  
---|---  
###  aget_messages `async` #
```
aget_messages(key: str) -> List[ChatMessage]

```

Get messages for a key asynchronously.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to get messages for |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
async def aget_messages(self, key: str) -> List[ChatMessage]:
    """
    Get messages for a key asynchronously.

    Args:
        key: Key to get messages for

    """
    # Find all messages for this key, sorted by index
    cursor = self._async_collection.find({"session_id": key}).sort("index", 1)

    # Convert to list and then to ChatMessage objects
    docs = await cursor.to_list(length=None)
    return [_dict_to_message(doc["message"]) for doc in docs]

```
  
---|---  
###  add_message #
```
add_message(key: str, message: ChatMessage, idx: Optional[int] = None) -> None

```

Add a message for a key.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to add message for |  _required_  
`message` |  `ChatMessage` |  ChatMessage object to add |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
def add_message(
    self, key: str, message: ChatMessage, idx: Optional[int] = None
) -> None:
    """
    Add a message for a key.

    Args:
        key: Key to add message for
        message: ChatMessage object to add

    """
    if idx is None:
        # Get the current highest index
        highest_idx_doc = self._collection.find_one(
            {"session_id": key}, sort=[("index", -1)]
        )
        idx = 0 if highest_idx_doc is None else highest_idx_doc["index"] + 1

    # Insert the new message with current timestamp
    self._collection.insert_one(
        {
            "session_id": key,
            "index": idx,
            "message": _message_to_dict(message),
            "created_at": datetime.now(),
        }
    )

```
  
---|---  
###  async_add_message `async` #
```
async_add_message(key: str, message: ChatMessage, idx: Optional[int] = None) -> None

```

Add a message for a key asynchronously.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to add message for |  _required_  
`message` |  `ChatMessage` |  ChatMessage object to add |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
async def async_add_message(
    self, key: str, message: ChatMessage, idx: Optional[int] = None
) -> None:
    """
    Add a message for a key asynchronously.

    Args:
        key: Key to add message for
        message: ChatMessage object to add

    """
    if idx is None:
        # Get the current highest index
        highest_idx_doc = await self._async_collection.find_one(
            {"session_id": key}, sort=[("index", -1)]
        )
        idx = 0 if highest_idx_doc is None else highest_idx_doc["index"] + 1

    # Insert the new message with current timestamp
    await self._async_collection.insert_one(
        {
            "session_id": key,
            "index": idx,
            "message": _message_to_dict(message),
            "created_at": datetime.now(),
        }
    )

```
  
---|---  
###  delete_messages #
```
delete_messages(key: str) -> Optional[List[ChatMessage]]

```

Delete messages for a key.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to delete messages for |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
def delete_messages(self, key: str) -> Optional[List[ChatMessage]]:
    """
    Delete messages for a key.

    Args:
        key: Key to delete messages for

    """
    # Get messages before deleting
    messages = self.get_messages(key)

    # Delete all messages for this key
    self._collection.delete_many({"session_id": key})

    return messages

```
  
---|---  
###  adelete_messages `async` #
```
adelete_messages(key: str) -> Optional[List[ChatMessage]]

```

Delete messages for a key asynchronously.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to delete messages for |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
async def adelete_messages(self, key: str) -> Optional[List[ChatMessage]]:
    """
    Delete messages for a key asynchronously.

    Args:
        key: Key to delete messages for

    """
    # Get messages before deleting
    messages = await self.aget_messages(key)

    # Delete all messages for this key
    await self._async_collection.delete_many({"session_id": key})

    return messages

```
  
---|---  
###  delete_message #
```
delete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Delete specific message for a key.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to delete message for |  _required_  
`idx` |  `int` |  Index of message to delete |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
def delete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """
    Delete specific message for a key.

    Args:
        key: Key to delete message for
        idx: Index of message to delete

    """
    # Find the message to delete
    doc = self._collection.find_one({"session_id": key, "index": idx})
    if doc is None:
        return None

    # Delete the message
    self._collection.delete_one({"session_id": key, "index": idx})

    # Reindex remaining messages
    self._collection.update_many(
        {"session_id": key, "index": {"$gt": idx}}, {"$inc": {"index": -1}}
    )

    return _dict_to_message(doc["message"])

```
  
---|---  
###  adelete_message `async` #
```
adelete_message(key: str, idx: int) -> Optional[ChatMessage]

```

Delete specific message for a key asynchronously.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to delete message for |  _required_  
`idx` |  `int` |  Index of message to delete |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
async def adelete_message(self, key: str, idx: int) -> Optional[ChatMessage]:
    """
    Delete specific message for a key asynchronously.

    Args:
        key: Key to delete message for
        idx: Index of message to delete

    """
    # Find the message to delete
    doc = await self._async_collection.find_one({"session_id": key, "index": idx})
    if doc is None:
        return None

    # Delete the message
    await self._async_collection.delete_one({"session_id": key, "index": idx})

    # Reindex remaining messages
    await self._async_collection.update_many(
        {"session_id": key, "index": {"$gt": idx}}, {"$inc": {"index": -1}}
    )

    return _dict_to_message(doc["message"])

```
  
---|---  
###  delete_last_message #
```
delete_last_message(key: str) -> Optional[ChatMessage]

```

Delete last message for a key.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to delete last message for |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
def delete_last_message(self, key: str) -> Optional[ChatMessage]:
    """
    Delete last message for a key.

    Args:
        key: Key to delete last message for

    """
    # Find the last message
    last_msg_doc = self._collection.find_one(
        {"session_id": key}, sort=[("index", -1)]
    )

    if last_msg_doc is None:
        return None

    # Delete the last message
    self._collection.delete_one({"_id": last_msg_doc["_id"]})

    return _dict_to_message(last_msg_doc["message"])

```
  
---|---  
###  adelete_last_message `async` #
```
adelete_last_message(key: str) -> Optional[ChatMessage]

```

Delete last message for a key asynchronously.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  Key to delete last message for |  _required_  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
async def adelete_last_message(self, key: str) -> Optional[ChatMessage]:
    """
    Delete last message for a key asynchronously.

    Args:
        key: Key to delete last message for

    """
    # Find the last message
    last_msg_doc = await self._async_collection.find_one(
        {"session_id": key}, sort=[("index", -1)]
    )

    if last_msg_doc is None:
        return None

    # Delete the last message
    await self._async_collection.delete_one({"_id": last_msg_doc["_id"]})

    return _dict_to_message(last_msg_doc["message"])

```
  
---|---  
###  get_keys #
```
get_keys() -> List[str]

```

Get all keys (session IDs).
Returns:
Type | Description  
---|---  
`List[str]` |  List of session IDs  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
def get_keys(self) -> List[str]:
    """
    Get all keys (session IDs).

    Returns:
        List of session IDs

    """
    # Get distinct session IDs
    return self._collection.distinct("session_id")

```
  
---|---  
###  aget_keys `async` #
```
aget_keys() -> List[str]

```

Get all keys (session IDs) asynchronously.
Returns:
Type | Description  
---|---  
`List[str]` |  List of session IDs  
Source code in `llama-index-integrations/storage/chat_store/llama-index-storage-chat-store-mongo/llama_index/storage/chat_store/mongo/base.py`

| ```
async def aget_keys(self) -> List[str]:
    """
    Get all keys (session IDs) asynchronously.

    Returns:
        List of session IDs

    """
    # Get distinct session IDs
    return await self._async_collection.distinct("session_id")

```
  
---|---
