# Apify
##  ApifyActor #
Bases: `BaseReader`
Apify Actor reader. Calls an Actor on the Apify platform and reads its resulting dataset when it finishes.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`apify_api_token` |  `str` |  Apify API token. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-apify/llama_index/readers/apify/actor/base.py`

| ```
class ApifyActor(BaseReader):
    """
    Apify Actor reader.
    Calls an Actor on the Apify platform and reads its resulting dataset when it finishes.

    Args:
        apify_api_token (str): Apify API token.

    """

    def __init__(self, apify_api_token: str) -> None:
        """Initialize the Apify Actor reader."""
        from apify_client import ApifyClient

        self.apify_api_token = apify_api_token

        client = ApifyClient(apify_api_token)
        if hasattr(client.http_client, "httpx_client"):
            client.http_client.httpx_client.headers["user-agent"] += (
                "; Origin/llama_index"
            )
        self.apify_client = client

    def load_data(
        self,
        actor_id: str,
        run_input: Dict,
        dataset_mapping_function: Callable[[Dict], Document],
        *,
        build: Optional[str] = None,
        memory_mbytes: Optional[int] = None,
        timeout_secs: Optional[int] = None,
    ) -> List[Document]:
        """
        Call an Actor on the Apify platform, wait for it to finish, and return its resulting dataset.

        Args:
            actor_id (str): The ID or name of the Actor.
            run_input (Dict): The input object of the Actor that you're trying to run.
            dataset_mapping_function (Callable): A function that takes a single dictionary (an Apify dataset item) and converts it to an instance of the Document class.
            build (str, optional): Optionally specifies the Actor build to run. It can be either a build tag or build number.
            memory_mbytes (int, optional): Optional memory limit for the run, in megabytes.
            timeout_secs (int, optional): Optional timeout for the run, in seconds.


        Returns:
            List[Document]: List of documents.

        """
        actor_call = self.apify_client.actor(actor_id).call(
            run_input=run_input,
            build=build,
            memory_mbytes=memory_mbytes,
            timeout_secs=timeout_secs,
        )

        reader = ApifyDataset(self.apify_api_token)
        return reader.load_data(
            dataset_id=actor_call.get("defaultDatasetId"),
            dataset_mapping_function=dataset_mapping_function,
        )

```
  
---|---  
###  load_data #
```
load_data(actor_id: str, run_input: Dict, dataset_mapping_function: Callable[[Dict], Document], *, build: Optional[str] = None, memory_mbytes: Optional[int] = None, timeout_secs: Optional[int] = None) -> List[Document]

```

Call an Actor on the Apify platform, wait for it to finish, and return its resulting dataset.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`actor_id` |  `str` |  The ID or name of the Actor. |  _required_  
`run_input` |  `Dict` |  The input object of the Actor that you're trying to run. |  _required_  
`dataset_mapping_function` |  `Callable` |  A function that takes a single dictionary (an Apify dataset item) and converts it to an instance of the Document class. |  _required_  
`build` |  `str` |  Optionally specifies the Actor build to run. It can be either a build tag or build number. |  `None`  
`memory_mbytes` |  `int` |  Optional memory limit for the run, in megabytes. |  `None`  
`timeout_secs` |  `int` |  Optional timeout for the run, in seconds. |  `None`  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-apify/llama_index/readers/apify/actor/base.py`

| ```
def load_data(
    self,
    actor_id: str,
    run_input: Dict,
    dataset_mapping_function: Callable[[Dict], Document],
    *,
    build: Optional[str] = None,
    memory_mbytes: Optional[int] = None,
    timeout_secs: Optional[int] = None,
) -> List[Document]:
    """
    Call an Actor on the Apify platform, wait for it to finish, and return its resulting dataset.

    Args:
        actor_id (str): The ID or name of the Actor.
        run_input (Dict): The input object of the Actor that you're trying to run.
        dataset_mapping_function (Callable): A function that takes a single dictionary (an Apify dataset item) and converts it to an instance of the Document class.
        build (str, optional): Optionally specifies the Actor build to run. It can be either a build tag or build number.
        memory_mbytes (int, optional): Optional memory limit for the run, in megabytes.
        timeout_secs (int, optional): Optional timeout for the run, in seconds.


    Returns:
        List[Document]: List of documents.

    """
    actor_call = self.apify_client.actor(actor_id).call(
        run_input=run_input,
        build=build,
        memory_mbytes=memory_mbytes,
        timeout_secs=timeout_secs,
    )

    reader = ApifyDataset(self.apify_api_token)
    return reader.load_data(
        dataset_id=actor_call.get("defaultDatasetId"),
        dataset_mapping_function=dataset_mapping_function,
    )

```
  
---|---  
##  ApifyDataset #
Bases: `BaseReader`
Apify Dataset reader. Reads a dataset on the Apify platform.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`apify_api_token` |  `str` |  Apify API token. |  _required_  
Source code in `llama-index-integrations/readers/llama-index-readers-apify/llama_index/readers/apify/dataset/base.py`

| ```
class ApifyDataset(BaseReader):
    """
    Apify Dataset reader.
    Reads a dataset on the Apify platform.

    Args:
        apify_api_token (str): Apify API token.

    """

    def __init__(self, apify_api_token: str) -> None:
        """Initialize Apify dataset reader."""
        from apify_client import ApifyClient

        client = ApifyClient(apify_api_token)
        if hasattr(client.http_client, "httpx_client"):
            client.http_client.httpx_client.headers["user-agent"] += (
                "; Origin/llama_index"
            )

        self.apify_client = client

    def load_data(
        self, dataset_id: str, dataset_mapping_function: Callable[[Dict], Document]
    ) -> List[Document]:
        """
        Load data from the Apify dataset.

        Args:
            dataset_id (str): Dataset ID.
            dataset_mapping_function (Callable[[Dict], Document]): Function to map dataset items to Document.


        Returns:
            List[Document]: List of documents.

        """
        items_list = self.apify_client.dataset(dataset_id).list_items(clean=True)

        document_list = []
        for item in items_list.items:
            document = dataset_mapping_function(item)
            if not isinstance(document, Document):
                raise ValueError("Dataset_mapping_function must return a Document")
            document_list.append(document)

        return document_list

```
  
---|---  
###  load_data #
```
load_data(dataset_id: str, dataset_mapping_function: Callable[[Dict], Document]) -> List[Document]

```

Load data from the Apify dataset.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`dataset_id` |  `str` |  Dataset ID. |  _required_  
`dataset_mapping_function` |  `Callable[[Dict], Document]` |  Function to map dataset items to Document. |  _required_  
Returns:
Type | Description  
---|---  
`List[Document]` |  List[Document]: List of documents.  
Source code in `llama-index-integrations/readers/llama-index-readers-apify/llama_index/readers/apify/dataset/base.py`

| ```
def load_data(
    self, dataset_id: str, dataset_mapping_function: Callable[[Dict], Document]
) -> List[Document]:
    """
    Load data from the Apify dataset.

    Args:
        dataset_id (str): Dataset ID.
        dataset_mapping_function (Callable[[Dict], Document]): Function to map dataset items to Document.


    Returns:
        List[Document]: List of documents.

    """
    items_list = self.apify_client.dataset(dataset_id).list_items(clean=True)

    document_list = []
    for item in items_list.items:
        document = dataset_mapping_function(item)
        if not isinstance(document, Document):
            raise ValueError("Dataset_mapping_function must return a Document")
        document_list.append(document)

    return document_list

```
  
---|---
