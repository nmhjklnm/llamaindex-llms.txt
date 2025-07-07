# Azure Cosmos DB No SQL Vector Store¶
In this notebook we are going to show a quick demo of how to use AzureCosmosDBNoSqlVectorSearch to perform vector searches in LlamaIndex.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-llms-azure-openai

```

%pip install llama-index-embeddings-openai %pip install llama-index-llms-azure-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import os
import json
import openai
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

```

import os import json import openai from llama_index.llms.azure_openai import AzureOpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
# Setup Azure OpenAI¶
The first step is to configure the llm and the embeddings model. These models will be used to create embeddings for the documents loaded into the database and for llm completions.
In [ ]:
Copied!
```
llm = AzureOpenAI(
    model="AZURE_OPENAI_MODEL",
    deployment_name="AZURE_OPENAI_DEPLOYMENT_NAME",
    azure_endpoint="AZURE_OPENAI_BASE",
    api_key="AZURE_OPENAI_KEY",
    api_version="AZURE_OPENAI_VERSION",
)

embed_model = AzureOpenAIEmbedding(
    model="AZURE_OPENAI_EMBEDDING_MODEL",
    deployment_name="AZURE_OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME",
    azure_endpoint="AZURE_OPENAI_BASE",
    api_key="AZURE_OPENAI_KEY",
    api_version="AZURE_OPENAI_VERSION",
)

```

llm = AzureOpenAI( model="AZURE_OPENAI_MODEL", deployment_name="AZURE_OPENAI_DEPLOYMENT_NAME", azure_endpoint="AZURE_OPENAI_BASE", api_key="AZURE_OPENAI_KEY", api_version="AZURE_OPENAI_VERSION", ) embed_model = AzureOpenAIEmbedding( model="AZURE_OPENAI_EMBEDDING_MODEL", deployment_name="AZURE_OPENAI_EMBEDDING_MODEL_DEPLOYMENT_NAME", azure_endpoint="AZURE_OPENAI_BASE", api_key="AZURE_OPENAI_KEY", api_version="AZURE_OPENAI_VERSION", )
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model

```

from llama_index.core import Settings Settings.llm = llm Settings.embed_model = embed_model
# Loading Documents¶
In this example we will be using the paul_graham essay which will be processed by the SimpleDirectoryReader.
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader(
    input_files=[r"\docs\examples\data\paul_graham\paul_graham_essay.txt"]
).load_data()

print("Document ID:", documents[0].doc_id)

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader( input_files=[r"\docs\examples\data\paul_graham\paul_graham_essay.txt"] ).load_data() print("Document ID:", documents[0].doc_id)
# Create the index¶
Here we establish the connection to cosmos db nosql and create a vector store index.
In [ ]:
Copied!
```
from azure.cosmos import CosmosClient, PartitionKey
from llama_index.vector_stores.azurecosmosnosql import (
    AzureCosmosDBNoSqlVectorSearch,
)
from llama_index.core import StorageContext

# create cosmos client
URI = "AZURE_COSMOSDB_URI"
KEY = "AZURE_COSMOSDB_KEY"
client = CosmosClient(URI, credential=KEY)

# specify vector store properties
indexing_policy = {
    "indexingMode": "consistent",
    "includedPaths": [{"path": "/*"}],
    "excludedPaths": [{"path": '/"_etag"/?'}],
    "vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}],
}

vector_embedding_policy = {
    "vectorEmbeddings": [
        {
            "path": "/embedding",
            "dataType": "float32",
            "distanceFunction": "cosine",
            "dimensions": 3072,
        }
    ]
}

partition_key = PartitionKey(path="/id")
cosmos_container_properties_test = {"partition_key": partition_key}
cosmos_database_properties_test = {}

# create vector store
store = AzureCosmosDBNoSqlVectorSearch(
    cosmos_client=client,
    vector_embedding_policy=vector_embedding_policy,
    indexing_policy=indexing_policy,
    cosmos_container_properties=cosmos_container_properties_test,
    cosmos_database_properties=cosmos_database_properties_test,
    create_container=True,
)

storage_context = StorageContext.from_defaults(vector_store=store)

index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

from azure.cosmos import CosmosClient, PartitionKey from llama_index.vector_stores.azurecosmosnosql import ( AzureCosmosDBNoSqlVectorSearch, ) from llama_index.core import StorageContext # create cosmos client URI = "AZURE_COSMOSDB_URI" KEY = "AZURE_COSMOSDB_KEY" client = CosmosClient(URI, credential=KEY) # specify vector store properties indexing_policy = { "indexingMode": "consistent", "includedPaths": [{"path": "/*"}], "excludedPaths": [{"path": '/"_etag"/?'}], "vectorIndexes": [{"path": "/embedding", "type": "quantizedFlat"}], } vector_embedding_policy = { "vectorEmbeddings": [ { "path": "/embedding", "dataType": "float32", "distanceFunction": "cosine", "dimensions": 3072, } ] } partition_key = PartitionKey(path="/id") cosmos_container_properties_test = {"partition_key": partition_key} cosmos_database_properties_test = {} # create vector store store = AzureCosmosDBNoSqlVectorSearch( cosmos_client=client, vector_embedding_policy=vector_embedding_policy, indexing_policy=indexing_policy, cosmos_container_properties=cosmos_container_properties_test, cosmos_database_properties=cosmos_database_properties_test, create_container=True, ) storage_context = StorageContext.from_defaults(vector_store=store) index = VectorStoreIndex.from_documents( documents, storage_context=storage_context )
# Query the index¶
We can now ask questions using our index.
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What did the author love working on?")

```

query_engine = index.as_query_engine() response = query_engine.query("What did the author love working on?")
In [ ]:
Copied!
```
import textwrap

print(textwrap.fill(str(response), 100))

```

import textwrap print(textwrap.fill(str(response), 100))
