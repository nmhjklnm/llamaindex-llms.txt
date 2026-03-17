![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Elasticsearch Embeddings¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-elasticsearch
%pip install llama-index-embeddings-elasticsearch

```

%pip install llama-index-vector-stores-elasticsearch %pip install llama-index-embeddings-elasticsearch
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# imports

from llama_index.embeddings.elasticsearch import ElasticsearchEmbedding
from llama_index.vector_stores.elasticsearch import ElasticsearchStore
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core import Settings

```

# imports from llama_index.embeddings.elasticsearch import ElasticsearchEmbedding from llama_index.vector_stores.elasticsearch import ElasticsearchStore from llama_index.core import StorageContext, VectorStoreIndex from llama_index.core import Settings
In [ ]:
Copied!
```
# get credentials and create embeddings

import os

host = os.environ.get("ES_HOST", "localhost:9200")
username = os.environ.get("ES_USERNAME", "elastic")
password = os.environ.get("ES_PASSWORD", "changeme")
index_name = os.environ.get("INDEX_NAME", "your-index-name")
model_id = os.environ.get("MODEL_ID", "your-model-id")


embeddings = ElasticsearchEmbedding.from_credentials(
    model_id=model_id, es_url=host, es_username=username, es_password=password
)

```

# get credentials and create embeddings import os host = os.environ.get("ES_HOST", "localhost:9200") username = os.environ.get("ES_USERNAME", "elastic") password = os.environ.get("ES_PASSWORD", "changeme") index_name = os.environ.get("INDEX_NAME", "your-index-name") model_id = os.environ.get("MODEL_ID", "your-model-id") embeddings = ElasticsearchEmbedding.from_credentials( model_id=model_id, es_url=host, es_username=username, es_password=password )
In [ ]:
Copied!
```
# set global settings
Settings.embed_model = embeddings
Settings.chunk_size = 512

```

# set global settings Settings.embed_model = embeddings Settings.chunk_size = 512
In [ ]:
Copied!
```
# usage with elasticsearch vector store

vector_store = ElasticsearchStore(
    index_name=index_name, es_url=host, es_user=username, es_password=password
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context,
)

query_engine = index.as_query_engine()


response = query_engine.query("hello world")

```

# usage with elasticsearch vector store vector_store = ElasticsearchStore( index_name=index_name, es_url=host, es_user=username, es_password=password ) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex.from_vector_store( vector_store=vector_store, storage_context=storage_context, ) query_engine = index.as_query_engine() response = query_engine.query("hello world")
