# Dynamodb
##  DynamoDBKVStore #
Bases: `BaseKVStore`
DynamoDB Key-Value store. Stores key-value pairs in a DynamoDB Table. The DynamoDB Table must have both a hash key and a range key, and their types must be string.
You can specify a custom URL for DynamoDB by setting the `DYNAMODB_URL` environment variable. This is useful if you're using a local instance of DynamoDB for development or testing. If `DYNAMODB_URL` is not set, the application will use the default AWS DynamoDB service.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`table` |  `Any` |  DynamoDB Table Service Resource |  _required_  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
class DynamoDBKVStore(BaseKVStore):
    """
    DynamoDB Key-Value store.
    Stores key-value pairs in a DynamoDB Table.
    The DynamoDB Table must have both a hash key and a range key,
        and their types must be string.

    You can specify a custom URL for DynamoDB by setting the `DYNAMODB_URL`
    environment variable. This is useful if you're using a local instance of
    DynamoDB for development or testing. If `DYNAMODB_URL` is not set, the
    application will use the default AWS DynamoDB service.

    Args:
        table (Any): DynamoDB Table Service Resource

    """

    def __init__(self, table: Any):
        """Init a DynamoDBKVStore."""
        self._table = table
        self._boto3_key = Key
        self._key_hash, self._key_range = parse_schema(table)

    @classmethod
    def from_table_name(cls, table_name: str) -> DynamoDBKVStore:
        """
        Load a DynamoDBKVStore from a DynamoDB table name.

        Args:
            table_name (str): DynamoDB table name

        """
        # Get the DynamoDB URL from environment variable
        dynamodb_url = os.getenv("DYNAMODB_URL")

        # Create a session
        session = boto3.Session()

        # If the DynamoDB URL is set, use it as the endpoint URL
        if dynamodb_url:
            ddb = session.resource("dynamodb", endpoint_url=dynamodb_url)
        else:
            # Otherwise, let boto3 use its default configuration
            ddb = session.resource("dynamodb")
        return cls(table=ddb.Table(table_name))

    def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        item = {k: convert_float_to_decimal(v) for k, v in val.items()}
        item[self._key_hash] = collection
        item[self._key_range] = key
        self._table.put_item(Item=item)

    async def aput(
        self, key: str, val: dict, collection: str = DEFAULT_COLLECTION
    ) -> None:
        """
        Put a key-value pair into the store.

        Args:
            key (str): key
            val (dict): value
            collection (str): collection name

        """
        raise NotImplementedError

    def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> dict | None:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        resp = self._table.get_item(
            Key={self._key_hash: collection, self._key_range: key}
        )
        if (item := resp.get("Item")) is None:
            return None
        else:
            return {
                k: convert_decimal_to_int_or_float(v)
                for k, v in item.items()
                if k not in {self._key_hash, self._key_range}
            }

    async def aget(self, key: str, collection: str = DEFAULT_COLLECTION) -> dict | None:
        """
        Get a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        raise NotImplementedError

    def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the store.

        Args:
            collection (str): collection name

        """
        result = {}
        last_evaluated_key = None
        is_first = True
        while last_evaluated_key is not None or is_first:
            if is_first:
                is_first = False
            option = {
                "KeyConditionExpression": self._boto3_key(self._key_hash).eq(collection)
            }
            if last_evaluated_key is not None:
                option["ExclusiveStartKey"] = last_evaluated_key
            resp = self._table.query(**option)
            for item in resp.get("Items", []):
                item.pop(self._key_hash)
                key = item.pop(self._key_range)
                result[key] = {
                    k: convert_decimal_to_int_or_float(v) for k, v in item.items()
                }
            last_evaluated_key = resp.get("LastEvaluatedKey")
        return result

    async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
        """
        Get all values from the store.

        Args:
            collection (str): collection name

        """
        raise NotImplementedError

    def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        resp = self._table.delete_item(
            Key={self._key_hash: collection, self._key_range: key},
            ReturnValues="ALL_OLD",
        )

        if (item := resp.get("Attributes")) is None:
            return False
        else:
            return len(item) > 0

    async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
        """
        Delete a value from the store.

        Args:
            key (str): key
            collection (str): collection name

        """
        raise NotImplementedError

```
  
---|---  
###  from_table_name `classmethod` #
```
from_table_name(table_name: str) -> DynamoDBKVStore

```

Load a DynamoDBKVStore from a DynamoDB table name.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`table_name` |  `str` |  DynamoDB table name |  _required_  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
@classmethod
def from_table_name(cls, table_name: str) -> DynamoDBKVStore:
    """
    Load a DynamoDBKVStore from a DynamoDB table name.

    Args:
        table_name (str): DynamoDB table name

    """
    # Get the DynamoDB URL from environment variable
    dynamodb_url = os.getenv("DYNAMODB_URL")

    # Create a session
    session = boto3.Session()

    # If the DynamoDB URL is set, use it as the endpoint URL
    if dynamodb_url:
        ddb = session.resource("dynamodb", endpoint_url=dynamodb_url)
    else:
        # Otherwise, let boto3 use its default configuration
        ddb = session.resource("dynamodb")
    return cls(table=ddb.Table(table_name))

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
def put(self, key: str, val: dict, collection: str = DEFAULT_COLLECTION) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    item = {k: convert_float_to_decimal(v) for k, v in val.items()}
    item[self._key_hash] = collection
    item[self._key_range] = key
    self._table.put_item(Item=item)

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
async def aput(
    self, key: str, val: dict, collection: str = DEFAULT_COLLECTION
) -> None:
    """
    Put a key-value pair into the store.

    Args:
        key (str): key
        val (dict): value
        collection (str): collection name

    """
    raise NotImplementedError

```
  
---|---  
###  get #
```
get(key: str, collection: str = DEFAULT_COLLECTION) -> dict | None

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
def get(self, key: str, collection: str = DEFAULT_COLLECTION) -> dict | None:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    resp = self._table.get_item(
        Key={self._key_hash: collection, self._key_range: key}
    )
    if (item := resp.get("Item")) is None:
        return None
    else:
        return {
            k: convert_decimal_to_int_or_float(v)
            for k, v in item.items()
            if k not in {self._key_hash, self._key_range}
        }

```
  
---|---  
###  aget `async` #
```
aget(key: str, collection: str = DEFAULT_COLLECTION) -> dict | None

```

Get a value from the store.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`key` |  `str` |  key |  _required_  
`collection` |  `str` |  collection name |  `DEFAULT_COLLECTION`  
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
async def aget(self, key: str, collection: str = DEFAULT_COLLECTION) -> dict | None:
    """
    Get a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    raise NotImplementedError

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
def get_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the store.

    Args:
        collection (str): collection name

    """
    result = {}
    last_evaluated_key = None
    is_first = True
    while last_evaluated_key is not None or is_first:
        if is_first:
            is_first = False
        option = {
            "KeyConditionExpression": self._boto3_key(self._key_hash).eq(collection)
        }
        if last_evaluated_key is not None:
            option["ExclusiveStartKey"] = last_evaluated_key
        resp = self._table.query(**option)
        for item in resp.get("Items", []):
            item.pop(self._key_hash)
            key = item.pop(self._key_range)
            result[key] = {
                k: convert_decimal_to_int_or_float(v) for k, v in item.items()
            }
        last_evaluated_key = resp.get("LastEvaluatedKey")
    return result

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
async def aget_all(self, collection: str = DEFAULT_COLLECTION) -> Dict[str, dict]:
    """
    Get all values from the store.

    Args:
        collection (str): collection name

    """
    raise NotImplementedError

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
def delete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    resp = self._table.delete_item(
        Key={self._key_hash: collection, self._key_range: key},
        ReturnValues="ALL_OLD",
    )

    if (item := resp.get("Attributes")) is None:
        return False
    else:
        return len(item) > 0

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
Source code in `llama-index-integrations/storage/kvstore/llama-index-storage-kvstore-dynamodb/llama_index/storage/kvstore/dynamodb/base.py`

| ```
async def adelete(self, key: str, collection: str = DEFAULT_COLLECTION) -> bool:
    """
    Delete a value from the store.

    Args:
        key (str): key
        collection (str): collection name

    """
    raise NotImplementedError

```
  
---|---
