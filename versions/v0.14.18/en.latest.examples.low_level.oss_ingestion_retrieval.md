![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Building RAG from Scratch (Open-source only!)¶
In this tutorial, we show you how to build a data ingestion pipeline into a vector database, and then build a retrieval pipeline from that vector database, from scratch.
Notably, we use a fully open-source stack:
  * Sentence Transformers as the embedding model
  * Postgres as the vector store (we support many other vector stores too!)
  * Llama 2 as the LLM (through llama.cpp)


## Setup¶
We setup our open-source components.
  1. Sentence Transformers
  2. Llama 2
  3. We initialize postgres and wrap it with our wrappers/abstractions.


#### Sentence Transformers¶
In [ ]:
Copied!
```
%pip install llama-index-readers-file pymupdf
%pip install llama-index-vector-stores-postgres
%pip install llama-index-embeddings-huggingface
%pip install llama-index-llms-llama-cpp

```

%pip install llama-index-readers-file pymupdf %pip install llama-index-vector-stores-postgres %pip install llama-index-embeddings-huggingface %pip install llama-index-llms-llama-cpp
In [ ]:
Copied!
```
# sentence transformers
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")

```

# sentence transformers from llama_index.embeddings.huggingface import HuggingFaceEmbedding embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")
#### Llama CPP¶
In this notebook, we use the `llama-2-chat-13b-ggml` model, along with the proper prompt formatting.
Check out our Llama CPP guide for full setup instructions/details.
In [ ]:
Copied!
```
!pip install llama-cpp-python

```

!pip install llama-cpp-python
```
Requirement already satisfied: llama-cpp-python in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (0.2.7)
Requirement already satisfied: numpy>=1.20.0 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from llama-cpp-python) (1.23.5)
Requirement already satisfied: typing-extensions>=4.5.0 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from llama-cpp-python) (4.7.1)
Requirement already satisfied: diskcache>=5.6.1 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from llama-cpp-python) (5.6.3)

[notice] A new release of pip available: 22.3.1 -> 23.2.1
[notice] To update, run: pip install --upgrade pip

```

In [ ]:
Copied!
```
from llama_index.llms.llama_cpp import LlamaCPP

# model_url = "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGML/resolve/main/llama-2-13b-chat.ggmlv3.q4_0.bin"
model_url = "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/resolve/main/llama-2-13b-chat.Q4_0.gguf"

llm = LlamaCPP(
    # You can pass in the URL to a GGML model to download it automatically
    model_url=model_url,
    # optionally, you can set the path to a pre-downloaded model instead of model_url
    model_path=None,
    temperature=0.1,
    max_new_tokens=256,
    # llama2 has a context window of 4096 tokens, but we set it lower to allow for some wiggle room
    context_window=3900,
    # kwargs to pass to __call__()
    generate_kwargs={},
    # kwargs to pass to __init__()
    # set to at least 1 to use GPU
    model_kwargs={"n_gpu_layers": 1},
    verbose=True,
)

```

from llama_index.llms.llama_cpp import LlamaCPP # model_url = "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGML/resolve/main/llama-2-13b-chat.ggmlv3.q4_0.bin" model_url = "https://huggingface.co/TheBloke/Llama-2-13B-chat-GGUF/resolve/main/llama-2-13b-chat.Q4_0.gguf" llm = LlamaCPP( # You can pass in the URL to a GGML model to download it automatically model_url=model_url, # optionally, you can set the path to a pre-downloaded model instead of model_url model_path=None, temperature=0.1, max_new_tokens=256, # llama2 has a context window of 4096 tokens, but we set it lower to allow for some wiggle room context_window=3900, # kwargs to pass to __call__() generate_kwargs={}, # kwargs to pass to __init__() # set to at least 1 to use GPU model_kwargs={"n_gpu_layers": 1}, verbose=True, )
#### Initialize Postgres¶
Using an existing postgres running at localhost, create the database we'll be using.
**NOTE** : Of course there are plenty of other open-source/self-hosted databases you can use! e.g. Chroma, Qdrant, Weaviate, and many more. Take a look at our vector store guide.
**NOTE** : You will need to setup postgres on your local system. Here's an example of how to set it up on OSX: https://www.sqlshack.com/setting-up-a-postgresql-database-on-mac/.
**NOTE** : You will also need to install pgvector (https://github.com/pgvector/pgvector).
You can add a role like the following:
```
CREATE ROLE <user> WITH LOGIN PASSWORD '<password>';
ALTER ROLE <user> SUPERUSER;

```

In [ ]:
Copied!
```
!pip install psycopg2-binary pgvector asyncpg "sqlalchemy[asyncio]" greenlet

```

!pip install psycopg2-binary pgvector asyncpg "sqlalchemy[asyncio]" greenlet
In [ ]:
Copied!
```
import psycopg2

db_name = "vector_db"
host = "localhost"
password = "password"
port = "5432"
user = "jerry"
# conn = psycopg2.connect(connection_string)
conn = psycopg2.connect(
    dbname="postgres",
    host=host,
    password=password,
    port=port,
    user=user,
)
conn.autocommit = True

with conn.cursor() as c:
    c.execute(f"DROP DATABASE IF EXISTS {db_name}")
    c.execute(f"CREATE DATABASE {db_name}")

```

import psycopg2 db_name = "vector_db" host = "localhost" password = "password" port = "5432" user = "jerry" # conn = psycopg2.connect(connection_string) conn = psycopg2.connect( dbname="postgres", host=host, password=password, port=port, user=user, ) conn.autocommit = True with conn.cursor() as c: c.execute(f"DROP DATABASE IF EXISTS {db_name}") c.execute(f"CREATE DATABASE {db_name}")
In [ ]:
Copied!
```
from sqlalchemy import make_url
from llama_index.vector_stores.postgres import PGVectorStore

vector_store = PGVectorStore.from_params(
    database=db_name,
    host=host,
    password=password,
    port=port,
    user=user,
    table_name="llama2_paper",
    embed_dim=384,  # openai embedding dimension
)

```

from sqlalchemy import make_url from llama_index.vector_stores.postgres import PGVectorStore vector_store = PGVectorStore.from_params( database=db_name, host=host, password=password, port=port, user=user, table_name="llama2_paper", embed_dim=384, # openai embedding dimension )
## Build an Ingestion Pipeline from Scratch¶
We show how to build an ingestion pipeline as mentioned in the introduction.
We fast-track the steps here (can skip metadata extraction). More details can be found in our dedicated ingestion guide.
### 1. Load Data¶
In [ ]:
Copied!
```
!mkdir data
!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"

```

!mkdir data !wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"
In [ ]:
Copied!
```
from pathlib import Path
from llama_index.readers.file import PyMuPDFReader

```

from pathlib import Path from llama_index.readers.file import PyMuPDFReader
In [ ]:
Copied!
```
loader = PyMuPDFReader()
documents = loader.load(file_path="./data/llama2.pdf")

```

loader = PyMuPDFReader() documents = loader.load(file_path="./data/llama2.pdf")
### 2. Use a Text Splitter to Split Documents¶
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

```

from llama_index.core.node_parser import SentenceSplitter
In [ ]:
Copied!
```
text_parser = SentenceSplitter(
    chunk_size=1024,
    # separator=" ",
)

```

text_parser = SentenceSplitter( chunk_size=1024, # separator=" ", )
In [ ]:
Copied!
```
text_chunks = []
# maintain relationship with source doc index, to help inject doc metadata in (3)
doc_idxs = []
for doc_idx, doc in enumerate(documents):
    cur_text_chunks = text_parser.split_text(doc.text)
    text_chunks.extend(cur_text_chunks)
    doc_idxs.extend([doc_idx] * len(cur_text_chunks))

```

text_chunks = [] # maintain relationship with source doc index, to help inject doc metadata in (3) doc_idxs = [] for doc_idx, doc in enumerate(documents): cur_text_chunks = text_parser.split_text(doc.text) text_chunks.extend(cur_text_chunks) doc_idxs.extend([doc_idx] * len(cur_text_chunks))
### 3. Manually Construct Nodes from Text Chunks¶
In [ ]:
Copied!
```
from llama_index.core.schema import TextNode

nodes = []
for idx, text_chunk in enumerate(text_chunks):
    node = TextNode(
        text=text_chunk,
    )
    src_doc = documents[doc_idxs[idx]]
    node.metadata = src_doc.metadata
    nodes.append(node)

```

from llama_index.core.schema import TextNode nodes = [] for idx, text_chunk in enumerate(text_chunks): node = TextNode( text=text_chunk, ) src_doc = documents[doc_idxs[idx]] node.metadata = src_doc.metadata nodes.append(node)
### 4. Generate Embeddings for each Node¶
Here we generate embeddings for each Node using a sentence_transformers model.
In [ ]:
Copied!
```
for node in nodes:
    node_embedding = embed_model.get_text_embedding(
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding

```

for node in nodes: node_embedding = embed_model.get_text_embedding( node.get_content(metadata_mode="all") ) node.embedding = node_embedding
### 5. Load Nodes into a Vector Store¶
We now insert these nodes into our `PostgresVectorStore`.
In [ ]:
Copied!
```
vector_store.add(nodes)

```

vector_store.add(nodes)
## Build Retrieval Pipeline from Scratch¶
We show how to build a retrieval pipeline. Similar to ingestion, we fast-track the steps. Take a look at our retrieval guide for more details!
In [ ]:
Copied!
```
query_str = "Can you tell me about the key concepts for safety finetuning"

```

query_str = "Can you tell me about the key concepts for safety finetuning"
### 1. Generate a Query Embedding¶
In [ ]:
Copied!
```
query_embedding = embed_model.get_query_embedding(query_str)

```

query_embedding = embed_model.get_query_embedding(query_str)
### 2. Query the Vector Database¶
In [ ]:
Copied!
```
# construct vector store query
from llama_index.core.vector_stores import VectorStoreQuery

query_mode = "default"
# query_mode = "sparse"
# query_mode = "hybrid"

vector_store_query = VectorStoreQuery(
    query_embedding=query_embedding, similarity_top_k=2, mode=query_mode
)

```

# construct vector store query from llama_index.core.vector_stores import VectorStoreQuery query_mode = "default" # query_mode = "sparse" # query_mode = "hybrid" vector_store_query = VectorStoreQuery( query_embedding=query_embedding, similarity_top_k=2, mode=query_mode )
In [ ]:
Copied!
```
# returns a VectorStoreQueryResult
query_result = vector_store.query(vector_store_query)
print(query_result.nodes[0].get_content())

```

# returns a VectorStoreQueryResult query_result = vector_store.query(vector_store_query) print(query_result.nodes[0].get_content())
### 3. Parse Result into a Set of Nodes¶
In [ ]:
Copied!
```
from llama_index.core.schema import NodeWithScore
from typing import Optional

nodes_with_scores = []
for index, node in enumerate(query_result.nodes):
    score: Optional[float] = None
    if query_result.similarities is not None:
        score = query_result.similarities[index]
    nodes_with_scores.append(NodeWithScore(node=node, score=score))

```

from llama_index.core.schema import NodeWithScore from typing import Optional nodes_with_scores = [] for index, node in enumerate(query_result.nodes): score: Optional[float] = None if query_result.similarities is not None: score = query_result.similarities[index] nodes_with_scores.append(NodeWithScore(node=node, score=score))
### 4. Put into a Retriever¶
In [ ]:
Copied!
```
from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from typing import Any, List


class VectorDBRetriever(BaseRetriever):
    """Retriever over a postgres vector store."""

    def __init__(
        self,
        vector_store: PGVectorStore,
        embed_model: Any,
        query_mode: str = "default",
        similarity_top_k: int = 2,
    ) -> None:
        """Init params."""
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
        query_embedding = embed_model.get_query_embedding(
            query_bundle.query_str
        )
        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )
        query_result = vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        return nodes_with_scores

```

from llama_index.core import QueryBundle from llama_index.core.retrievers import BaseRetriever from typing import Any, List class VectorDBRetriever(BaseRetriever): """Retriever over a postgres vector store.""" def __init__( self, vector_store: PGVectorStore, embed_model: Any, query_mode: str = "default", similarity_top_k: int = 2, ) -> None: """Init params.""" self._vector_store = vector_store self._embed_model = embed_model self._query_mode = query_mode self._similarity_top_k = similarity_top_k super().__init__() def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]: """Retrieve.""" query_embedding = embed_model.get_query_embedding( query_bundle.query_str ) vector_store_query = VectorStoreQuery( query_embedding=query_embedding, similarity_top_k=self._similarity_top_k, mode=self._query_mode, ) query_result = vector_store.query(vector_store_query) nodes_with_scores = [] for index, node in enumerate(query_result.nodes): score: Optional[float] = None if query_result.similarities is not None: score = query_result.similarities[index] nodes_with_scores.append(NodeWithScore(node=node, score=score)) return nodes_with_scores
In [ ]:
Copied!
```
retriever = VectorDBRetriever(
    vector_store, embed_model, query_mode="default", similarity_top_k=2
)

```

retriever = VectorDBRetriever( vector_store, embed_model, query_mode="default", similarity_top_k=2 )
## Plug this into our RetrieverQueryEngine to synthesize a response¶
In [ ]:
Copied!
```
from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm)

```

from llama_index.core.query_engine import RetrieverQueryEngine query_engine = RetrieverQueryEngine.from_args(retriever, llm=llm)
In [ ]:
Copied!
```
query_str = "How does Llama 2 perform compared to other open-source models?"

response = query_engine.query(query_str)

```

query_str = "How does Llama 2 perform compared to other open-source models?" response = query_engine.query(query_str)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
 Based on the results shown in Table 3, Llama 2 outperforms all open-source models on most of the benchmarks, with an average improvement of around 5 points over the next best model (GPT-3.5).

```

In [ ]:
Copied!
```
print(response.source_nodes[0].get_content())

```

print(response.source_nodes[0].get_content())
