# Opendal
##  OpendalAzblobReader #
Bases: `BaseReader`
General reader for any Azblob file or directory.
Source code in `llama-index-integrations/readers/llama-index-readers-opendal/llama_index/readers/opendal/azblob/base.py`

| ```
class OpendalAzblobReader(BaseReader):
    """General reader for any Azblob file or directory."""

    def __init__(
        self,
        container: str,
        path: str = "/",
        endpoint: str = "",
        account_name: str = "",
        account_key: str = "",
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
    ) -> None:
        """
        Initialize Azblob container, along with credentials if needed.

        If key is not set, the entire bucket (filtered by prefix) is parsed.

        Args:
        container (str): the name of your azblob bucket
        path (str): the path of the data. If none is provided,
            this loader will iterate through the entire bucket. If path is endswith `/`, this loader will iterate through the entire dir. Otherwise, this loeader will load the file.
        endpoint Optional[str]: the endpoint of the azblob service.
        account_name (Optional[str]): provide azblob access key directly.
        account_key (Optional[str]): provide azblob access key directly.
        file_extractor (Optional[Dict[str, BaseReader]]): A mapping of file
            extension to a BaseReader class that specifies how to convert that file
            to text. See `SimpleDirectoryReader` for more details.

        """
        super().__init__()

        self.path = path
        self.file_extractor = file_extractor

        # opendal service related config.
        self.options = {
            "container": container,
            "endpoint": endpoint,
            "account_name": account_name,
            "account_key": account_key,
        }

    def load_data(self) -> List[Document]:
        """Load file(s) from OpenDAL."""
        loader = OpendalReader(
            scheme="azblob",
            path=self.path,
            file_extractor=self.file_extractor,
            **self.options,
        )

        return loader.load_data()

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Load file(s) from OpenDAL.
Source code in `llama-index-integrations/readers/llama-index-readers-opendal/llama_index/readers/opendal/azblob/base.py`

| ```
def load_data(self) -> List[Document]:
    """Load file(s) from OpenDAL."""
    loader = OpendalReader(
        scheme="azblob",
        path=self.path,
        file_extractor=self.file_extractor,
        **self.options,
    )

    return loader.load_data()

```
  
---|---  
##  OpendalGcsReader #
Bases: `BaseReader`
General reader for any Gcs file or directory.
Source code in `llama-index-integrations/readers/llama-index-readers-opendal/llama_index/readers/opendal/gcs/base.py`

| ```
class OpendalGcsReader(BaseReader):
    """General reader for any Gcs file or directory."""

    def __init__(
        self,
        bucket: str,
        path: str = "/",
        endpoint: str = "",
        credentials: str = "",
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
    ) -> None:
        """
        Initialize Gcs container, along with credentials if needed.

        If key is not set, the entire bucket (filtered by prefix) is parsed.

        Args:
        bucket (str): the name of your gcs bucket
        path (str): the path of the data. If none is provided,
            this loader will iterate through the entire bucket. If path is endswith `/`, this loader will iterate through the entire dir. Otherwise, this loeader will load the file.
        endpoint Optional[str]: the endpoint of the azblob service.
        credentials (Optional[str]): provide credential string for GCS OAuth2 directly.
        file_extractor (Optional[Dict[str, BaseReader]]): A mapping of file
            extension to a BaseReader class that specifies how to convert that file
            to text. See `SimpleDirectoryReader` for more details.

        """
        super().__init__()

        self.path = path
        self.file_extractor = file_extractor

        # opendal service related config.
        self.options = {
            "bucket": bucket,
            "endpoint": endpoint,
            "credentials": credentials,
        }

    def load_data(self) -> List[Document]:
        """Load file(s) from OpenDAL."""
        loader = OpendalReader(
            scheme="gcs",
            path=self.path,
            file_extractor=self.file_extractor,
            **self.options,
        )

        return loader.load_data()

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Load file(s) from OpenDAL.
Source code in `llama-index-integrations/readers/llama-index-readers-opendal/llama_index/readers/opendal/gcs/base.py`

| ```
def load_data(self) -> List[Document]:
    """Load file(s) from OpenDAL."""
    loader = OpendalReader(
        scheme="gcs",
        path=self.path,
        file_extractor=self.file_extractor,
        **self.options,
    )

    return loader.load_data()

```
  
---|---  
##  OpendalReader #
Bases: `BaseReader`
General reader for any opendal operator.
Source code in `llama-index-integrations/readers/llama-index-readers-opendal/llama_index/readers/opendal/base.py`

| ```
class OpendalReader(BaseReader):
    """General reader for any opendal operator."""

    def __init__(
        self,
        scheme: str,
        path: str = "/",
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
        **kwargs,
    ) -> None:
        """
        Initialize opendal operator, along with credentials if needed.


        Args:
        scheme (str): the scheme of the service
        path (str): the path of the data. If none is provided,
            this loader will iterate through the entire bucket. If path is endswith `/`, this loader will iterate through the entire dir. Otherwise, this loeader will load the file.
        file_extractor (Optional[Dict[str, BaseReader]]): A mapping of file
            extension to a BaseReader class that specifies how to convert that file
            to text. See `SimpleDirectoryReader` for more details.

        """
        import opendal

        super().__init__()

        self.path = path
        self.file_extractor = file_extractor

        self.op = opendal.AsyncOperator(scheme, **kwargs)

    def load_data(self) -> List[Document]:
        """Load file(s) from OpenDAL."""
        with tempfile.TemporaryDirectory() as temp_dir:
            if not self.path.endswith("/"):
                asyncio.run(download_file_from_opendal(self.op, temp_dir, self.path))
            else:
                asyncio.run(download_dir_from_opendal(self.op, temp_dir, self.path))

            loader = SimpleDirectoryReader(temp_dir, file_extractor=self.file_extractor)

            return loader.load_data()

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Load file(s) from OpenDAL.
Source code in `llama-index-integrations/readers/llama-index-readers-opendal/llama_index/readers/opendal/base.py`

| ```
def load_data(self) -> List[Document]:
    """Load file(s) from OpenDAL."""
    with tempfile.TemporaryDirectory() as temp_dir:
        if not self.path.endswith("/"):
            asyncio.run(download_file_from_opendal(self.op, temp_dir, self.path))
        else:
            asyncio.run(download_dir_from_opendal(self.op, temp_dir, self.path))

        loader = SimpleDirectoryReader(temp_dir, file_extractor=self.file_extractor)

        return loader.load_data()

```
  
---|---  
##  OpendalS3Reader #
Bases: `BaseReader`
General reader for any S3 file or directory.
Source code in `llama-index-integrations/readers/llama-index-readers-opendal/llama_index/readers/opendal/s3/base.py`

| ```
class OpendalS3Reader(BaseReader):
    """General reader for any S3 file or directory."""

    def __init__(
        self,
        bucket: str,
        path: str = "/",
        endpoint: str = "",
        region: str = "",
        access_key_id: str = "",
        secret_access_key: str = "",
        file_extractor: Optional[Dict[str, Union[str, BaseReader]]] = None,
    ) -> None:
        """
        Initialize S3 bucket and key, along with credentials if needed.

        If key is not set, the entire bucket (filtered by prefix) is parsed.

        Args:
        bucket (str): the name of your S3 bucket
        path (str): the path of the data. If none is provided,
            this loader will iterate through the entire bucket. If path is endswith `/`, this loader will iterate through the entire dir. Otherwise, this loeader will load the file.
        endpoint Optional[str]: the endpoint of the S3 service.
        region: Optional[str]: the region of the S3 service.
        access_key_id (Optional[str]): provide AWS access key directly.
        secret_access_key (Optional[str]): provide AWS access key directly.
        file_extractor (Optional[Dict[str, BaseReader]]): A mapping of file
            extension to a BaseReader class that specifies how to convert that file
            to text. See `SimpleDirectoryReader` for more details.

        """
        super().__init__()

        self.path = path
        self.file_extractor = file_extractor

        # opendal service related config.
        self.options = {
            "access_key": access_key_id,
            "secret_key": secret_access_key,
            "endpoint": endpoint,
            "region": region,
            "bucket": bucket,
        }

    def load_data(self) -> List[Document]:
        """Load file(s) from OpenDAL."""
        loader = OpendalReader(
            scheme="s3",
            path=self.path,
            file_extractor=self.file_extractor,
            **self.options,
        )

        return loader.load_data()

```
  
---|---  
###  load_data #
```
load_data() -> List[Document]

```

Load file(s) from OpenDAL.
Source code in `llama-index-integrations/readers/llama-index-readers-opendal/llama_index/readers/opendal/s3/base.py`

| ```
def load_data(self) -> List[Document]:
    """Load file(s) from OpenDAL."""
    loader = OpendalReader(
        scheme="s3",
        path=self.path,
        file_extractor=self.file_extractor,
        **self.options,
    )

    return loader.load_data()

```
  
---|---
