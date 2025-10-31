# Building a Live RAG Pipeline over Google Drive Files¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In this guide we show you how to build a "live" RAG pipeline over Google Drive files.
This pipeline will index Google Drive files and dump them to a Redis vector store. Afterwards, every time you rerun the ingestion pipeline, the pipeline will propagate **incremental updates** , so that only changed documents are updated in the vector store. This means that we don't re-index all the documents!
We use the following data source - you will need to copy these files and upload them to your own Google Drive directory!
**NOTE** : You will also need to setup a service account and credentials.json. See our LlamaHub page for the Google Drive loader for more details: https://llamahub.ai/l/readers/llama-index-readers-google?from=readers
## Setup¶
We install required packages and launch the Redis Docker image.
In [ ]:
Copied!
```
%pip install llama-index-storage-docstore-redis
%pip install llama-index-vector-stores-redis
%pip install llama-index-embeddings-huggingface
%pip install llama-index-readers-google

```

%pip install llama-index-storage-docstore-redis %pip install llama-index-vector-stores-redis %pip install llama-index-embeddings-huggingface %pip install llama-index-readers-google
In [ ]:
Copied!
```
# if creating a new container
!docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest
# # if starting an existing container
# !docker start -a redis-stack

```

# if creating a new container !docker run -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest # # if starting an existing container # !docker start -a redis-stack
```
d32273cc1267d3221afa780db0edcd6ce5eee08ae88886f645410b9a220d4916

```

In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
## Define Ingestion Pipeline¶
Here we define the ingestion pipeline. Given a set of documents, we will run sentence splitting/embedding transformations, and then load them into a Redis docstore/vector store.
The vector store is for indexing the data + storing the embeddings, the docstore is for tracking duplicates.
In [ ]:
Copied!
```
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.ingestion import (
    DocstoreStrategy,
    IngestionPipeline,
    IngestionCache,
)
from llama_index.storage.kvstore.redis import RedisKVStore as RedisCache
from llama_index.storage.docstore.redis import RedisDocumentStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.redis import RedisVectorStore

from redisvl.schema import IndexSchema

```

from llama_index.embeddings.huggingface import HuggingFaceEmbedding from llama_index.core.ingestion import ( DocstoreStrategy, IngestionPipeline, IngestionCache, ) from llama_index.storage.kvstore.redis import RedisKVStore as RedisCache from llama_index.storage.docstore.redis import RedisDocumentStore from llama_index.core.node_parser import SentenceSplitter from llama_index.vector_stores.redis import RedisVectorStore from redisvl.schema import IndexSchema
In [ ]:
Copied!
```
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

```

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
```
model.safetensors:   0%|          | 0.00/133M [00:00<?, ?B/s]
```

```
tokenizer_config.json:   0%|          | 0.00/366 [00:00<?, ?B/s]
```

```
vocab.txt:   0%|          | 0.00/232k [00:00<?, ?B/s]
```

```
tokenizer.json:   0%|          | 0.00/711k [00:00<?, ?B/s]
```

```
special_tokens_map.json:   0%|          | 0.00/125 [00:00<?, ?B/s]
```

```
1_Pooling/config.json:   0%|          | 0.00/190 [00:00<?, ?B/s]
```

In [ ]:
Copied!
```
custom_schema = IndexSchema.from_dict(
    {
        "index": {"name": "gdrive", "prefix": "doc"},
        # customize fields that are indexed
        "fields": [
            # required fields for llamaindex
            {"type": "tag", "name": "id"},
            {"type": "tag", "name": "doc_id"},
            {"type": "text", "name": "text"},
            # custom vector field for bge-small-en-v1.5 embeddings
            {
                "type": "vector",
                "name": "vector",
                "attrs": {
                    "dims": 384,
                    "algorithm": "hnsw",
                    "distance_metric": "cosine",
                },
            },
        ],
    }
)

vector_store = RedisVectorStore(
    schema=custom_schema,
    redis_url="redis://localhost:6379",
)

```

custom_schema = IndexSchema.from_dict( { "index": {"name": "gdrive", "prefix": "doc"}, # customize fields that are indexed "fields": [ # required fields for llamaindex {"type": "tag", "name": "id"}, {"type": "tag", "name": "doc_id"}, {"type": "text", "name": "text"}, # custom vector field for bge-small-en-v1.5 embeddings { "type": "vector", "name": "vector", "attrs": { "dims": 384, "algorithm": "hnsw", "distance_metric": "cosine", }, }, ], } ) vector_store = RedisVectorStore( schema=custom_schema, redis_url="redis://localhost:6379", )
In [ ]:
Copied!
```
# Optional: clear vector store if exists
if vector_store.index_exists():
    vector_store.delete_index()

```

# Optional: clear vector store if exists if vector_store.index_exists(): vector_store.delete_index()
In [ ]:
Copied!
```
# Set up the ingestion cache layer
cache = IngestionCache(
    cache=RedisCache.from_host_and_port("localhost", 6379),
    collection="redis_cache",
)

```

# Set up the ingestion cache layer cache = IngestionCache( cache=RedisCache.from_host_and_port("localhost", 6379), collection="redis_cache", )
In [ ]:
Copied!
```
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        embed_model,
    ],
    docstore=RedisDocumentStore.from_host_and_port(
        "localhost", 6379, namespace="document_store"
    ),
    vector_store=vector_store,
    cache=cache,
    docstore_strategy=DocstoreStrategy.UPSERTS,
)

```

pipeline = IngestionPipeline( transformations=[ SentenceSplitter(), embed_model, ], docstore=RedisDocumentStore.from_host_and_port( "localhost", 6379, namespace="document_store" ), vector_store=vector_store, cache=cache, docstore_strategy=DocstoreStrategy.UPSERTS, )
### Define our Vector Store Index¶
We define our index to wrap the underlying vector store.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_vector_store(
    pipeline.vector_store, embed_model=embed_model
)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_vector_store( pipeline.vector_store, embed_model=embed_model )
## Load Initial Data¶
Here we load data from our Google Drive Loader on LlamaHub.
The loaded docs are the header sections of our Use Cases from our documentation.
In [ ]:
Copied!
```
from llama_index.readers.google import GoogleDriveReader

```

from llama_index.readers.google import GoogleDriveReader
In [ ]:
Copied!
```
loader = GoogleDriveReader()

```

loader = GoogleDriveReader()
In [ ]:
Copied!
```
def load_data(folder_id: str):
    docs = loader.load_data(folder_id=folder_id)
    for doc in docs:
        doc.id_ = doc.metadata["file_name"]
    return docs


docs = load_data(folder_id="1RFhr3-KmOZCR5rtp4dlOMNl3LKe1kOA5")
# print(docs)

```

def load_data(folder_id: str): docs = loader.load_data(folder_id=folder_id) for doc in docs: doc.id_ = doc.metadata["file_name"] return docs docs = load_data(folder_id="1RFhr3-KmOZCR5rtp4dlOMNl3LKe1kOA5") # print(docs)
In [ ]:
Copied!
```
nodes = pipeline.run(documents=docs)
print(f"Ingested {len(nodes)} Nodes")

```

nodes = pipeline.run(documents=docs) print(f"Ingested {len(nodes)} Nodes")
Since this is our first time starting up the vector store, we see that we've transformed/ingested all the documents into it (by chunking, and then by embedding).
### Ask Questions over Initial Data¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine()

```

query_engine = index.as_query_engine()
In [ ]:
Copied!
```
response = query_engine.query("What are the sub-types of question answering?")

```

response = query_engine.query("What are the sub-types of question answering?")
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The sub-types of question answering mentioned in the context are semantic search and summarization.

```

## Modify and Reload the Data¶
Let's try modifying our ingested data!
We modify the "Q&A" doc to include an extra "structured analytics" block of text. See our updated document as a reference.
Now let's rerun the ingestion pipeline.
In [ ]:
Copied!
```
docs = load_data(folder_id="1RFhr3-KmOZCR5rtp4dlOMNl3LKe1kOA5")
nodes = pipeline.run(documents=docs)
print(f"Ingested {len(nodes)} Nodes")

```

docs = load_data(folder_id="1RFhr3-KmOZCR5rtp4dlOMNl3LKe1kOA5") nodes = pipeline.run(documents=docs) print(f"Ingested {len(nodes)} Nodes")
Notice how only one node is ingested. This is beacuse only one document changed, while the other documents stayed the same. This means that we only need to re-transform and re-embed one document!
### Ask Questions over New Data¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine()

```

query_engine = index.as_query_engine()
In [ ]:
Copied!
```
response = query_engine.query("What are the sub-types of question answering?")

```

response = query_engine.query("What are the sub-types of question answering?")
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The sub-types of question answering mentioned in the context are semantic search, summarization, and structured analytics.

```

