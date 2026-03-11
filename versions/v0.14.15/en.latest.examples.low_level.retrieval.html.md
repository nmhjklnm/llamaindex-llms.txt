![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Building Retrieval from Scratch¶
In this tutorial, we show you how to build a standard retriever against a vector database, that will fetch nodes via top-k similarity.
We use Pinecone as the vector database. We load in nodes using our high-level ingestion abstractions (to see how to build this from scratch, see our previous tutorial!).
We will show how to do the following:
  1. How to generate a query embedding
  2. How to query the vector database using different search modes (dense, sparse, hybrid)
  3. How to parse results into a set of Nodes
  4. How to put this in a custom retriever


## Setup¶
We build an empty Pinecone Index, and define the necessary LlamaIndex wrappers/abstractions so that we can start loading data into Pinecone.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-file pymupdf
%pip install llama-index-vector-stores-pinecone
%pip install llama-index-embeddings-openai

```

%pip install llama-index-readers-file pymupdf %pip install llama-index-vector-stores-pinecone %pip install llama-index-embeddings-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
#### Build Pinecone Index¶
In [ ]:
Copied!
```
from pinecone import Pinecone, Index, ServerlessSpec
import os

api_key = os.environ["PINECONE_API_KEY"]
pc = Pinecone(api_key=api_key)

```

from pinecone import Pinecone, Index, ServerlessSpec import os api_key = os.environ["PINECONE_API_KEY"] pc = Pinecone(api_key=api_key)
In [ ]:
Copied!
```
# dimensions are for text-embedding-ada-002
dataset_name = "quickstart"
if dataset_name not in pc.list_indexes().names():
    pc.create_index(
        dataset_name,
        dimension=1536,
        metric="euclidean",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

```

# dimensions are for text-embedding-ada-002 dataset_name = "quickstart" if dataset_name not in pc.list_indexes().names(): pc.create_index( dataset_name, dimension=1536, metric="euclidean", spec=ServerlessSpec(cloud="aws", region="us-east-1"), )
In [ ]:
Copied!
```
pinecone_index = pc.Index(dataset_name)

```

pinecone_index = pc.Index(dataset_name)
In [ ]:
Copied!
```
# [Optional] drop contents in index
pinecone_index.delete(deleteAll=True)

```

# [Optional] drop contents in index pinecone_index.delete(deleteAll=True)
#### Create PineconeVectorStore¶
Simple wrapper abstraction to use in LlamaIndex. Wrap in StorageContext so we can easily load in Nodes.
In [ ]:
Copied!
```
from llama_index.vector_stores.pinecone import PineconeVectorStore

```

from llama_index.vector_stores.pinecone import PineconeVectorStore
In [ ]:
Copied!
```
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

```

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
#### Load Documents¶
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
#### Load into Vector Store¶
Load in documents into the PineconeVectorStore.
**NOTE** : We use high-level ingestion abstractions here, with `VectorStoreIndex.from_documents.` We'll refrain from using `VectorStoreIndex` for the rest of this tutorial.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import StorageContext

```

from llama_index.core import VectorStoreIndex from llama_index.core.node_parser import SentenceSplitter from llama_index.core import StorageContext
In [ ]:
Copied!
```
splitter = SentenceSplitter(chunk_size=1024)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, transformations=[splitter], storage_context=storage_context
)

```

splitter = SentenceSplitter(chunk_size=1024) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex.from_documents( documents, transformations=[splitter], storage_context=storage_context )
## Define Vector Retriever¶
Now we're ready to define our retriever against this vector store to retrieve a set of nodes.
We'll show the processes step by step and then wrap it into a function.
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
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding()

```

from llama_index.embeddings.openai import OpenAIEmbedding embed_model = OpenAIEmbedding()
In [ ]:
Copied!
```
query_embedding = embed_model.get_query_embedding(query_str)

```

query_embedding = embed_model.get_query_embedding(query_str)
### 2. Query the Vector Database¶
We show how to query the vector database with different modes: default, sparse, and hybrid.
We first construct a `VectorStoreQuery` and then query the vector db.
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
query_result

```

# returns a VectorStoreQueryResult query_result = vector_store.query(vector_store_query) query_result
### 3. Parse Result into a set of Nodes¶
The `VectorStoreQueryResult` returns the set of nodes and similarities. We construct a `NodeWithScore` object with this.
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
In [ ]:
Copied!
```
from llama_index.core.response.notebook_utils import display_source_node

for node in nodes_with_scores:
    display_source_node(node, source_length=1000)

```

from llama_index.core.response.notebook_utils import display_source_node for node in nodes_with_scores: display_source_node(node, source_length=1000)
### 4. Put this into a Retriever¶
Let's put this into a Retriever subclass that can plug into the rest of LlamaIndex workflows!
In [ ]:
Copied!
```
from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from typing import Any, List


class PineconeRetriever(BaseRetriever):
    """Retriever over a pinecone vector store."""

    def __init__(
        self,
        vector_store: PineconeVectorStore,
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
        if query_bundle.embedding is None:
            query_embedding = self._embed_model.get_query_embedding(
                query_bundle.query_str
            )
        else:
            query_embedding = query_bundle.embedding

        vector_store_query = VectorStoreQuery(
            query_embedding=query_embedding,
            similarity_top_k=self._similarity_top_k,
            mode=self._query_mode,
        )
        query_result = self._vector_store.query(vector_store_query)

        nodes_with_scores = []
        for index, node in enumerate(query_result.nodes):
            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
            nodes_with_scores.append(NodeWithScore(node=node, score=score))

        return nodes_with_scores

```

from llama_index.core import QueryBundle from llama_index.core.retrievers import BaseRetriever from typing import Any, List class PineconeRetriever(BaseRetriever): """Retriever over a pinecone vector store.""" def __init__( self, vector_store: PineconeVectorStore, embed_model: Any, query_mode: str = "default", similarity_top_k: int = 2, ) -> None: """Init params.""" self._vector_store = vector_store self._embed_model = embed_model self._query_mode = query_mode self._similarity_top_k = similarity_top_k super().__init__() def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]: """Retrieve.""" if query_bundle.embedding is None: query_embedding = self._embed_model.get_query_embedding( query_bundle.query_str ) else: query_embedding = query_bundle.embedding vector_store_query = VectorStoreQuery( query_embedding=query_embedding, similarity_top_k=self._similarity_top_k, mode=self._query_mode, ) query_result = self._vector_store.query(vector_store_query) nodes_with_scores = [] for index, node in enumerate(query_result.nodes): score: Optional[float] = None if query_result.similarities is not None: score = query_result.similarities[index] nodes_with_scores.append(NodeWithScore(node=node, score=score)) return nodes_with_scores
In [ ]:
Copied!
```
retriever = PineconeRetriever(
    vector_store, embed_model, query_mode="default", similarity_top_k=2
)

```

retriever = PineconeRetriever( vector_store, embed_model, query_mode="default", similarity_top_k=2 )
In [ ]:
Copied!
```
retrieved_nodes = retriever.retrieve(query_str)
for node in retrieved_nodes:
    display_source_node(node, source_length=1000)

```

retrieved_nodes = retriever.retrieve(query_str) for node in retrieved_nodes: display_source_node(node, source_length=1000)
## Plug this into our RetrieverQueryEngine to synthesize a response¶
**NOTE** : We'll cover more on how to build response synthesis from scratch in future tutorials!
In [ ]:
Copied!
```
from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine.from_args(retriever)

```

from llama_index.core.query_engine import RetrieverQueryEngine query_engine = RetrieverQueryEngine.from_args(retriever)
In [ ]:
Copied!
```
response = query_engine.query(query_str)

```

response = query_engine.query(query_str)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The key concepts for safety fine-tuning include supervised safety fine-tuning, safety RLHF (Reinforcement Learning from Human Feedback), and safety context distillation. Supervised safety fine-tuning involves gathering adversarial prompts and safe demonstrations to train the model to align with safety guidelines. Safety RLHF integrates safety into the RLHF pipeline by training a safety-specific reward model and gathering challenging adversarial prompts for fine-tuning. Safety context distillation refines the RLHF pipeline by generating safer model responses using a safety preprompt and fine-tuning the model on these responses without the preprompt. These concepts are used to mitigate safety risks and improve the safety of the model's responses.

```

