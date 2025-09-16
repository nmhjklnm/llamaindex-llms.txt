![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Lantern Vector Store¶
In this notebook we are going to show how to use Postgresql and Lantern to perform vector searches in LlamaIndex
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-lantern
%pip install llama-index-embeddings-openai

```

%pip install llama-index-vector-stores-lantern %pip install llama-index-embeddings-openai
In [ ]:
Copied!
```
!pip install psycopg2-binary llama-index asyncpg

```

!pip install psycopg2-binary llama-index asyncpg 
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.lantern import LanternVectorStore
import textwrap
import openai

```

from llama_index.core import SimpleDirectoryReader, StorageContext from llama_index.core import VectorStoreIndex from llama_index.vector_stores.lantern import LanternVectorStore import textwrap import openai
### Setup OpenAI¶
The first step is to configure the openai key. It will be used to created embeddings for the documents loaded into the index
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "<your_key>"
openai.api_key = "<your_key>"

```

import os os.environ["OPENAI_API_KEY"] = "" openai.api_key = ""
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
### Loading documents¶
Load the documents stored in the `data/paul_graham/` using the SimpleDirectoryReader
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("./data/paul_graham").load_data()
print("Document ID:", documents[0].doc_id)

```

documents = SimpleDirectoryReader("./data/paul_graham").load_data() print("Document ID:", documents[0].doc_id)
### Create the Database¶
Using an existing postgres running at localhost, create the database we'll be using.
In [ ]:
Copied!
```
import psycopg2

connection_string = "postgresql://postgres:postgres@localhost:5432"
db_name = "postgres"
conn = psycopg2.connect(connection_string)
conn.autocommit = True

with conn.cursor() as c:
    c.execute(f"DROP DATABASE IF EXISTS {db_name}")
    c.execute(f"CREATE DATABASE {db_name}")

```

import psycopg2 connection_string = "postgresql://postgres:postgres@localhost:5432" db_name = "postgres" conn = psycopg2.connect(connection_string) conn.autocommit = True with conn.cursor() as c: c.execute(f"DROP DATABASE IF EXISTS {db_name}") c.execute(f"CREATE DATABASE {db_name}")
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

# Setup global settings with embedding model
# So query strings will be transformed to embeddings and HNSW index will be used
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import Settings # Setup global settings with embedding model # So query strings will be transformed to embeddings and HNSW index will be used Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
### Create the index¶
Here we create an index backed by Postgres using the documents loaded previously. LanternVectorStore takes a few arguments.
In [ ]:
Copied!
```
from sqlalchemy import make_url

url = make_url(connection_string)
vector_store = LanternVectorStore.from_params(
    database=db_name,
    host=url.host,
    password=url.password,
    port=url.port,
    user=url.username,
    table_name="paul_graham_essay",
    embed_dim=1536,  # openai embedding dimension
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, show_progress=True
)
query_engine = index.as_query_engine()

```

from sqlalchemy import make_url url = make_url(connection_string) vector_store = LanternVectorStore.from_params( database=db_name, host=url.host, password=url.password, port=url.port, user=url.username, table_name="paul_graham_essay", embed_dim=1536, # openai embedding dimension ) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex.from_documents( documents, storage_context=storage_context, show_progress=True ) query_engine = index.as_query_engine()
### Query the index¶
We can now ask questions using our index.
In [ ]:
Copied!
```
response = query_engine.query("What did the author do?")

```

response = query_engine.query("What did the author do?")
In [ ]:
Copied!
```
print(textwrap.fill(str(response), 100))

```

print(textwrap.fill(str(response), 100))
In [ ]:
Copied!
```
response = query_engine.query("What happened in the mid 1980s?")

```

response = query_engine.query("What happened in the mid 1980s?")
In [ ]:
Copied!
```
print(textwrap.fill(str(response), 100))

```

print(textwrap.fill(str(response), 100))
### Querying existing index¶
In [ ]:
Copied!
```
vector_store = LanternVectorStore.from_params(
    database=db_name,
    host=url.host,
    password=url.password,
    port=url.port,
    user=url.username,
    table_name="paul_graham_essay",
    embed_dim=1536,  # openai embedding dimension
    m=16,  # HNSW M parameter
    ef_construction=128,  # HNSW ef construction parameter
    ef=64,  # HNSW ef search parameter
)

# Read more about HNSW parameters here: https://github.com/nmslib/hnswlib/blob/master/ALGO_PARAMS.md

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
query_engine = index.as_query_engine()

```

vector_store = LanternVectorStore.from_params( database=db_name, host=url.host, password=url.password, port=url.port, user=url.username, table_name="paul_graham_essay", embed_dim=1536, # openai embedding dimension m=16, # HNSW M parameter ef_construction=128, # HNSW ef construction parameter ef=64, # HNSW ef search parameter ) # Read more about HNSW parameters here: https://github.com/nmslib/hnswlib/blob/master/ALGO_PARAMS.md index = VectorStoreIndex.from_vector_store(vector_store=vector_store) query_engine = index.as_query_engine()
In [ ]:
Copied!
```
response = query_engine.query("What did the author do?")

```

response = query_engine.query("What did the author do?")
In [ ]:
Copied!
```
print(textwrap.fill(str(response), 100))

```

print(textwrap.fill(str(response), 100))
### Hybrid Search¶
To enable hybrid search, you need to:
  1. pass in `hybrid_search=True` when constructing the `LanternVectorStore` (and optionally configure `text_search_config` with the desired language)
  2. pass in `vector_store_query_mode="hybrid"` when constructing the query engine (this config is passed to the retriever under the hood). You can also optionally set the `sparse_top_k` to configure how many results we should obtain from sparse text search (default is using the same value as `similarity_top_k`).


In [ ]:
Copied!
```
from sqlalchemy import make_url

url = make_url(connection_string)
hybrid_vector_store = LanternVectorStore.from_params(
    database=db_name,
    host=url.host,
    password=url.password,
    port=url.port,
    user=url.username,
    table_name="paul_graham_essay_hybrid_search",
    embed_dim=1536,  # openai embedding dimension
    hybrid_search=True,
    text_search_config="english",
)

storage_context = StorageContext.from_defaults(
    vector_store=hybrid_vector_store
)
hybrid_index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

from sqlalchemy import make_url url = make_url(connection_string) hybrid_vector_store = LanternVectorStore.from_params( database=db_name, host=url.host, password=url.password, port=url.port, user=url.username, table_name="paul_graham_essay_hybrid_search", embed_dim=1536, # openai embedding dimension hybrid_search=True, text_search_config="english", ) storage_context = StorageContext.from_defaults( vector_store=hybrid_vector_store ) hybrid_index = VectorStoreIndex.from_documents( documents, storage_context=storage_context )
In [ ]:
Copied!
```
hybrid_query_engine = hybrid_index.as_query_engine(
    vector_store_query_mode="hybrid", sparse_top_k=2
)
hybrid_response = hybrid_query_engine.query(
    "Who does Paul Graham think of with the word schtick"
)

```

hybrid_query_engine = hybrid_index.as_query_engine( vector_store_query_mode="hybrid", sparse_top_k=2 ) hybrid_response = hybrid_query_engine.query( "Who does Paul Graham think of with the word schtick" )
In [ ]:
Copied!
```
print(hybrid_response)

```

print(hybrid_response)
