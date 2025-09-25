# BGEM3Demo
In this notebook, we are going to show how to use BGE-M3 with LlamaIndex.
BGE-M3 is a hybrid multilingual retrieval model that supports over 100 languages and can handle input lengths of up to 8,192 tokens. The model can perform (i) dense retrieval, (ii) sparse retrieval, and (iii) multi-vector retrieval.
## Getting Started¶
In [ ]:
Copied!
```
%pip install llama-index-indices-managed-bge-m3

```

%pip install llama-index-indices-managed-bge-m3
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
## Creating BGEM3Index¶
In [ ]:
Copied!
```
from llama_index.core import Settings
from llama_index.core import Document
from llama_index.indices.managed.bge_m3 import BGEM3Index

Settings.chunk_size = 8192

```

from llama_index.core import Settings from llama_index.core import Document from llama_index.indices.managed.bge_m3 import BGEM3Index Settings.chunk_size = 8192
In [ ]:
Copied!
```
# Let's create some demo corpus
sentences = [
    "BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.",
    "BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document",
]
documents = [Document(doc_id=i, text=s) for i, s in enumerate(sentences)]

```

# Let's create some demo corpus sentences = [ "BGE M3 is an embedding model supporting dense retrieval, lexical matching and multi-vector interaction.", "BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document", ] documents = [Document(doc_id=i, text=s) for i, s in enumerate(sentences)]
In [ ]:
Copied!
```
# Indexing with BGE-M3 model
index = BGEM3Index.from_documents(
    documents,
    weights_for_different_modes=[
        0.4,
        0.2,
        0.4,
    ],  # [dense_weight, sparse_weight, multi_vector_weight]
)

```

# Indexing with BGE-M3 model index = BGEM3Index.from_documents( documents, weights_for_different_modes=[ 0.4, 0.2, 0.4, ], # [dense_weight, sparse_weight, multi_vector_weight] )
## Retrieve relevant documents¶
In [ ]:
Copied!
```
retriever = index.as_retriever()
response = retriever.retrieve("What is BGE-M3?")

```

retriever = index.as_retriever() response = retriever.retrieve("What is BGE-M3?")
## RAG with BGE-M3¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What is BGE-M3?")

```

query_engine = index.as_query_engine() response = query_engine.query("What is BGE-M3?")
