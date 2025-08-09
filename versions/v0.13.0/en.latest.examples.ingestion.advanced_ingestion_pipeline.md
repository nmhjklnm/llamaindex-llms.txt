![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-weaviate
%pip install llama-index-embeddings-huggingface

```

%pip install llama-index-vector-stores-weaviate %pip install llama-index-embeddings-huggingface
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
# Advanced Ingestion Pipeline¶
In this notebook, we implement an `IngestionPipeline` with the following features
  * MongoDB transformation caching
  * Automatic vector databse insertion
  * A custom transformation


## Redis Cache Setup¶
All node + transformation combinations will have their outputs cached, which will save time on duplicate runs.
In [ ]:
Copied!
```
from llama_index.core.ingestion.cache import RedisCache
from llama_index.core.ingestion import IngestionCache

ingest_cache = IngestionCache(
    cache=RedisCache.from_host_and_port(host="127.0.0.1", port=6379),
    collection="my_test_cache",
)

```

from llama_index.core.ingestion.cache import RedisCache from llama_index.core.ingestion import IngestionCache ingest_cache = IngestionCache( cache=RedisCache.from_host_and_port(host="127.0.0.1", port=6379), collection="my_test_cache", )
## Vector DB Setup¶
For this example, we use weaviate as a vector store.
In [ ]:
Copied!
```
!pip install weaviate-client

```

!pip install weaviate-client
In [ ]:
Copied!
```
import weaviate

auth_config = weaviate.AuthApiKey(api_key="...")

client = weaviate.Client(url="https://...", auth_client_secret=auth_config)

```

import weaviate auth_config = weaviate.AuthApiKey(api_key="...") client = weaviate.Client(url="https://...", auth_client_secret=auth_config)
In [ ]:
Copied!
```
from llama_index.vector_stores.weaviate import WeaviateVectorStore

vector_store = WeaviateVectorStore(
    weaviate_client=client, index_name="CachingTest"
)

```

from llama_index.vector_stores.weaviate import WeaviateVectorStore vector_store = WeaviateVectorStore( weaviate_client=client, index_name="CachingTest" )
## Transformation Setup¶
In [ ]:
Copied!
```
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

text_splitter = TokenTextSplitter(chunk_size=512)
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

```

from llama_index.core.node_parser import TokenTextSplitter from llama_index.embeddings.huggingface import HuggingFaceEmbedding text_splitter = TokenTextSplitter(chunk_size=512) embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
```
/home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm
Downloading (…)lve/main/config.json: 100%|██████████| 743/743 [00:00<00:00, 3.51MB/s]
Downloading pytorch_model.bin: 100%|██████████| 134M/134M [00:03<00:00, 34.6MB/s] 
Downloading (…)okenizer_config.json: 100%|██████████| 366/366 [00:00<00:00, 2.20MB/s]
Downloading (…)solve/main/vocab.txt: 100%|██████████| 232k/232k [00:00<00:00, 2.47MB/s]
Downloading (…)/main/tokenizer.json: 100%|██████████| 711k/711k [00:00<00:00, 7.34MB/s]
Downloading (…)cial_tokens_map.json: 100%|██████████| 125/125 [00:00<00:00, 620kB/s]

```

### Custom Transformation¶
In [ ]:
Copied!
```
import re
from llama_index.core.schema import TransformComponent


class TextCleaner(TransformComponent):
    def __call__(self, nodes, **kwargs):
        for node in nodes:
            node.text = re.sub(r"[^0-9A-Za-z ]", "", node.text)
        return nodes

```

import re from llama_index.core.schema import TransformComponent class TextCleaner(TransformComponent): def __call__(self, nodes, **kwargs): for node in nodes: node.text = re.sub(r"[^0-9A-Za-z ]", "", node.text) return nodes
## Running the pipeline¶
In [ ]:
Copied!
```
from llama_index.core.ingestion import IngestionPipeline

pipeline = IngestionPipeline(
    transformations=[
        TextCleaner(),
        text_splitter,
        embed_model,
        TitleExtractor(),
    ],
    vector_store=vector_store,
    cache=ingest_cache,
)

```

from llama_index.core.ingestion import IngestionPipeline pipeline = IngestionPipeline( transformations=[ TextCleaner(), text_splitter, embed_model, TitleExtractor(), ], vector_store=vector_store, cache=ingest_cache, )
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("../data/paul_graham/").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("../data/paul_graham/").load_data()
In [ ]:
Copied!
```
nodes = pipeline.run(documents=documents)

```

nodes = pipeline.run(documents=documents)
## Using our populated vector store¶
In [ ]:
Copied!
```
import os

# needed for the LLM in the query engine
os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os # needed for the LLM in the query engine os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    embed_model=embed_model,
)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_vector_store( vector_store=vector_store, embed_model=embed_model, )
In [ ]:
Copied!
```
query_engine = index.as_query_engine()

print(query_engine.query("What did the author do growing up?"))

```

query_engine = index.as_query_engine() print(query_engine.query("What did the author do growing up?"))
```
The author worked on writing and programming growing up. They wrote short stories and also tried programming on an IBM 1401 computer using an early version of Fortran.

```

## Re-run Ingestion to test Caching¶
The next code block will execute almost instantly due to caching.
In [ ]:
Copied!
```
pipeline = IngestionPipeline(
    transformations=[TextCleaner(), text_splitter, embed_model],
    cache=ingest_cache,
)

nodes = pipeline.run(documents=documents)

```

pipeline = IngestionPipeline( transformations=[TextCleaner(), text_splitter, embed_model], cache=ingest_cache, ) nodes = pipeline.run(documents=documents)
## Clear the cache¶
In [ ]:
Copied!
```
ingest_cache.clear()

```

ingest_cache.clear()
