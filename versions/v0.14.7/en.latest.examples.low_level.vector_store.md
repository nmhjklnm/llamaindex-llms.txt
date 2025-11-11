![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Building a (Very Simple) Vector Store from Scratch¶
In this tutorial, we show you how to build a simple in-memory vector store that can store documents along with metadata. It will also expose a query interface that can support a variety of queries:
  * semantic search (with embedding similarity)
  * metadata filtering


**NOTE** : Obviously this is not supposed to be a replacement for any actual vector store (e.g. Pinecone, Weaviate, Chroma, Qdrant, Milvus, or others within our wide range of vector store integrations). This is more to teach some key retrieval concepts, like top-k embedding search + metadata filtering.
We won't be covering advanced query/retrieval concepts such as approximate nearest neighbors, sparse/hybrid search, or any of the system concepts that would be required for building an actual database.
## Setup¶
We load in some documents, and parse them into Node objects - chunks that are ready to be inserted into a vector store.
#### Load in Documents¶
In [ ]:
Copied!
```
%pip install llama-index-readers-file pymupdf
%pip install llama-index-embeddings-openai

```

%pip install llama-index-readers-file pymupdf %pip install llama-index-embeddings-openai
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
#### Parse into Nodes¶
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

node_parser = SentenceSplitter(chunk_size=256)
nodes = node_parser.get_nodes_from_documents(documents)

```

from llama_index.core.node_parser import SentenceSplitter node_parser = SentenceSplitter(chunk_size=256) nodes = node_parser.get_nodes_from_documents(documents)
#### Generate Embeddings for each Node¶
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding()
for node in nodes:
    node_embedding = embed_model.get_text_embedding(
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding

```

from llama_index.embeddings.openai import OpenAIEmbedding embed_model = OpenAIEmbedding() for node in nodes: node_embedding = embed_model.get_text_embedding( node.get_content(metadata_mode="all") ) node.embedding = node_embedding
## Build a Simple In-Memory Vector Store¶
Now we'll build our in-memory vector store. We'll store Nodes within a simple Python dictionary. We'll start off implementing embedding search, and add metadata filters.
### 1. Defining the Interface¶
We'll first define the interface for building a vector store. It contains the following items:
  * `get`
  * `add`
  * `delete`
  * `query`
  * `persist` (which we will not implement)


In [ ]:
Copied!
```
from llama_index.core.vector_stores.types import BasePydanticVectorStore
from llama_index.core.vector_stores import (
    VectorStoreQuery,
    VectorStoreQueryResult,
)
from typing import List, Any, Optional, Dict
from llama_index.core.schema import TextNode, BaseNode
import os


class BaseVectorStore(BasePydanticVectorStore):
    """Simple custom Vector Store.

    Stores documents in a simple in-memory dict.

    """

    stores_text: bool = True

    def get(self, text_id: str) -> List[float]:
        """Get embedding."""
        pass

    def add(
        self,
        nodes: List[BaseNode],
    ) -> List[str]:
        """Add nodes to index."""
        pass

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with ref_doc_id.

        Args:
            ref_doc_id (str): The doc_id of the document to delete.

        """
        pass

    def query(
        self,
        query: VectorStoreQuery,
        **kwargs: Any,
    ) -> VectorStoreQueryResult:
        """Get nodes for response."""
        pass

    def persist(self, persist_path, fs=None) -> None:
        """Persist the SimpleVectorStore to a directory.

        NOTE: we are not implementing this for now.

        """
        pass

```

from llama_index.core.vector_stores.types import BasePydanticVectorStore from llama_index.core.vector_stores import ( VectorStoreQuery, VectorStoreQueryResult, ) from typing import List, Any, Optional, Dict from llama_index.core.schema import TextNode, BaseNode import os class BaseVectorStore(BasePydanticVectorStore): """Simple custom Vector Store. Stores documents in a simple in-memory dict. """ stores_text: bool = True def get(self, text_id: str) -> List[float]: """Get embedding.""" pass def add( self, nodes: List[BaseNode], ) -> List[str]: """Add nodes to index.""" pass def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None: """ Delete nodes using with ref_doc_id. Args: ref_doc_id (str): The doc_id of the document to delete. """ pass def query( self, query: VectorStoreQuery, **kwargs: Any, ) -> VectorStoreQueryResult: """Get nodes for response.""" pass def persist(self, persist_path, fs=None) -> None: """Persist the SimpleVectorStore to a directory. NOTE: we are not implementing this for now. """ pass
At a high-level, we subclass our base `VectorStore` abstraction. There's no inherent reason to do this if you're just building a vector store from scratch. We do it because it makes it easy to plug into our downstream abstractions later.
Let's look at some of the classes defined here.
  * `BaseNode` is simply the parent class of our core Node modules. Each Node represents a text chunk + associated metadata.
  * We also use some lower-level constructs, for instance our `VectorStoreQuery` and `VectorStoreQueryResult`. These are just lightweight dataclass containers to represent queries and results. We look at the dataclass fields below.


In [ ]:
Copied!
```
from dataclasses import fields

{f.name: f.type for f in fields(VectorStoreQuery)}

```

from dataclasses import fields {f.name: f.type for f in fields(VectorStoreQuery)}
Out[ ]:
```
{'query_embedding': typing.Optional[typing.List[float]],
 'similarity_top_k': int,
 'doc_ids': typing.Optional[typing.List[str]],
 'node_ids': typing.Optional[typing.List[str]],
 'query_str': typing.Optional[str],
 'output_fields': typing.Optional[typing.List[str]],
 'embedding_field': typing.Optional[str],
 'mode': <enum 'VectorStoreQueryMode'>,
 'alpha': typing.Optional[float],
 'filters': typing.Optional[llama_index.vector_stores.types.MetadataFilters],
 'mmr_threshold': typing.Optional[float],
 'sparse_top_k': typing.Optional[int]}
```

In [ ]:
Copied!
```
{f.name: f.type for f in fields(VectorStoreQueryResult)}

```

{f.name: f.type for f in fields(VectorStoreQueryResult)}
Out[ ]:
```
{'nodes': typing.Optional[typing.Sequence[llama_index.schema.BaseNode]],
 'similarities': typing.Optional[typing.List[float]],
 'ids': typing.Optional[typing.List[str]]}
```

### 2. Defining `add`, `get`, and `delete`¶
We add some basic capabilities to add, get, and delete from a vector store.
The implementation is very simple (everything is just stored in a python dictionary).
In [ ]:
Copied!
```
from llama_index.core.bridge.pydantic import Field


class VectorStore2(BaseVectorStore):
    """VectorStore2 (add/get/delete implemented)."""

    stores_text: bool = True
    node_dict: Dict[str, BaseNode] = Field(default_factory=dict)

    def get(self, text_id: str) -> List[float]:
        """Get embedding."""
        return self.node_dict[text_id]

    def add(
        self,
        nodes: List[BaseNode],
    ) -> List[str]:
        """Add nodes to index."""
        for node in nodes:
            self.node_dict[node.node_id] = node

    def delete(self, node_id: str, **delete_kwargs: Any) -> None:
        """
        Delete nodes using with node_id.

        Args:
            node_id: str

        """
        del self.node_dict[node_id]

```

from llama_index.core.bridge.pydantic import Field class VectorStore2(BaseVectorStore): """VectorStore2 (add/get/delete implemented).""" stores_text: bool = True node_dict: Dict[str, BaseNode] = Field(default_factory=dict) def get(self, text_id: str) -> List[float]: """Get embedding.""" return self.node_dict[text_id] def add( self, nodes: List[BaseNode], ) -> List[str]: """Add nodes to index.""" for node in nodes: self.node_dict[node.node_id] = node def delete(self, node_id: str, **delete_kwargs: Any) -> None: """ Delete nodes using with node_id. Args: node_id: str """ del self.node_dict[node_id]
We run some basic tests just to show it works well.
In [ ]:
Copied!
```
test_node = TextNode(id_="id1", text="hello world")
test_node2 = TextNode(id_="id2", text="foo bar")
test_nodes = [test_node, test_node2]

```

test_node = TextNode(id_="id1", text="hello world") test_node2 = TextNode(id_="id2", text="foo bar") test_nodes = [test_node, test_node2]
In [ ]:
Copied!
```
vector_store = VectorStore2()

```

vector_store = VectorStore2()
In [ ]:
Copied!
```
vector_store.add(test_nodes)

```

vector_store.add(test_nodes)
In [ ]:
Copied!
```
node = vector_store.get("id1")
print(str(node))

```

node = vector_store.get("id1") print(str(node))
```
Node ID: id1
Text: hello world

```

### 3.a Defining `query` (semantic search)¶
We implement a basic version of top-k semantic search. This simply iterates through all document embeddings, and compute cosine-similarity with the query embedding. The top-k documents by cosine similarity are returned.
Cosine similarity: $\dfrac{\vec{d}\vec{q}}{|\vec{d}||\vec{q}|}$ for every document, query embedding pair $\vec{d}$, $\vec{p}$.
**NOTE** : The top-k value is contained in the `VectorStoreQuery` container.
**NOTE** : Similar to the above, we define another subclass just so we don't have to reimplement the above functions (not because this is actually good code practice).
In [ ]:
Copied!
```
from typing import Tuple
import numpy as np


def get_top_k_embeddings(
    query_embedding: List[float],
    doc_embeddings: List[List[float]],
    doc_ids: List[str],
    similarity_top_k: int = 5,
) -> Tuple[List[float], List]:
    """Get top nodes by similarity to the query."""
    # dimensions: D
    qembed_np = np.array(query_embedding)
    # dimensions: N x D
    dembed_np = np.array(doc_embeddings)
    # dimensions: N
    dproduct_arr = np.dot(dembed_np, qembed_np)
    # dimensions: N
    norm_arr = np.linalg.norm(qembed_np) * np.linalg.norm(
        dembed_np, axis=1, keepdims=False
    )
    # dimensions: N
    cos_sim_arr = dproduct_arr / norm_arr

    # now we have the N cosine similarities for each document
    # sort by top k cosine similarity, and return ids
    tups = [(cos_sim_arr[i], doc_ids[i]) for i in range(len(doc_ids))]
    sorted_tups = sorted(tups, key=lambda t: t[0], reverse=True)

    sorted_tups = sorted_tups[:similarity_top_k]

    result_similarities = [s for s, _ in sorted_tups]
    result_ids = [n for _, n in sorted_tups]
    return result_similarities, result_ids

```

from typing import Tuple import numpy as np def get_top_k_embeddings( query_embedding: List[float], doc_embeddings: List[List[float]], doc_ids: List[str], similarity_top_k: int = 5, ) -> Tuple[List[float], List]: """Get top nodes by similarity to the query.""" # dimensions: D qembed_np = np.array(query_embedding) # dimensions: N x D dembed_np = np.array(doc_embeddings) # dimensions: N dproduct_arr = np.dot(dembed_np, qembed_np) # dimensions: N norm_arr = np.linalg.norm(qembed_np) * np.linalg.norm( dembed_np, axis=1, keepdims=False ) # dimensions: N cos_sim_arr = dproduct_arr / norm_arr # now we have the N cosine similarities for each document # sort by top k cosine similarity, and return ids tups = [(cos_sim_arr[i], doc_ids[i]) for i in range(len(doc_ids))] sorted_tups = sorted(tups, key=lambda t: t[0], reverse=True) sorted_tups = sorted_tups[:similarity_top_k] result_similarities = [s for s, _ in sorted_tups] result_ids = [n for _, n in sorted_tups] return result_similarities, result_ids
In [ ]:
Copied!
```
from typing import cast


class VectorStore3A(VectorStore2):
    """Implements semantic/dense search."""

    def query(
        self,
        query: VectorStoreQuery,
        **kwargs: Any,
    ) -> VectorStoreQueryResult:
        """Get nodes for response."""

        query_embedding = cast(List[float], query.query_embedding)
        doc_embeddings = [n.embedding for n in self.node_dict.values()]
        doc_ids = [n.node_id for n in self.node_dict.values()]

        similarities, node_ids = get_top_k_embeddings(
            query_embedding,
            doc_embeddings,
            doc_ids,
            similarity_top_k=query.similarity_top_k,
        )
        result_nodes = [self.node_dict[node_id] for node_id in node_ids]

        return VectorStoreQueryResult(
            nodes=result_nodes, similarities=similarities, ids=node_ids
        )

```

from typing import cast class VectorStore3A(VectorStore2): """Implements semantic/dense search.""" def query( self, query: VectorStoreQuery, **kwargs: Any, ) -> VectorStoreQueryResult: """Get nodes for response.""" query_embedding = cast(List[float], query.query_embedding) doc_embeddings = [n.embedding for n in self.node_dict.values()] doc_ids = [n.node_id for n in self.node_dict.values()] similarities, node_ids = get_top_k_embeddings( query_embedding, doc_embeddings, doc_ids, similarity_top_k=query.similarity_top_k, ) result_nodes = [self.node_dict[node_id] for node_id in node_ids] return VectorStoreQueryResult( nodes=result_nodes, similarities=similarities, ids=node_ids )
### 3.b. Supporting Metadata Filtering¶
The next extension is adding metadata filter support. This means that we will first filter the candidate set with documents that pass the metadata filters, and then perform semantic querying.
For simplicity we use metadata filters for exact matching with an AND condition.
In [ ]:
Copied!
```
from llama_index.core.vector_stores import MetadataFilters
from llama_index.core.schema import BaseNode
from typing import cast


def filter_nodes(nodes: List[BaseNode], filters: MetadataFilters):
    filtered_nodes = []
    for node in nodes:
        matches = True
        for f in filters.filters:
            if f.key not in node.metadata:
                matches = False
                continue
            if f.value != node.metadata[f.key]:
                matches = False
                continue
        if matches:
            filtered_nodes.append(node)
    return filtered_nodes

```

from llama_index.core.vector_stores import MetadataFilters from llama_index.core.schema import BaseNode from typing import cast def filter_nodes(nodes: List[BaseNode], filters: MetadataFilters): filtered_nodes = [] for node in nodes: matches = True for f in filters.filters: if f.key not in node.metadata: matches = False continue if f.value != node.metadata[f.key]: matches = False continue if matches: filtered_nodes.append(node) return filtered_nodes
We add `filter_nodes` as a first-pass over the nodes before running semantic search.
In [ ]:
Copied!
```
def dense_search(query: VectorStoreQuery, nodes: List[BaseNode]):
    """Dense search."""
    query_embedding = cast(List[float], query.query_embedding)
    doc_embeddings = [n.embedding for n in nodes]
    doc_ids = [n.node_id for n in nodes]
    return get_top_k_embeddings(
        query_embedding,
        doc_embeddings,
        doc_ids,
        similarity_top_k=query.similarity_top_k,
    )


class VectorStore3B(VectorStore2):
    """Implements Metadata Filtering."""

    def query(
        self,
        query: VectorStoreQuery,
        **kwargs: Any,
    ) -> VectorStoreQueryResult:
        """Get nodes for response."""
        # 1. First filter by metadata
        nodes = self.node_dict.values()
        if query.filters is not None:
            nodes = filter_nodes(nodes, query.filters)
        if len(nodes) == 0:
            result_nodes = []
            similarities = []
            node_ids = []
        else:
            # 2. Then perform semantic search
            similarities, node_ids = dense_search(query, nodes)
            result_nodes = [self.node_dict[node_id] for node_id in node_ids]
        return VectorStoreQueryResult(
            nodes=result_nodes, similarities=similarities, ids=node_ids
        )

```

def dense_search(query: VectorStoreQuery, nodes: List[BaseNode]): """Dense search.""" query_embedding = cast(List[float], query.query_embedding) doc_embeddings = [n.embedding for n in nodes] doc_ids = [n.node_id for n in nodes] return get_top_k_embeddings( query_embedding, doc_embeddings, doc_ids, similarity_top_k=query.similarity_top_k, ) class VectorStore3B(VectorStore2): """Implements Metadata Filtering.""" def query( self, query: VectorStoreQuery, **kwargs: Any, ) -> VectorStoreQueryResult: """Get nodes for response.""" # 1. First filter by metadata nodes = self.node_dict.values() if query.filters is not None: nodes = filter_nodes(nodes, query.filters) if len(nodes) == 0: result_nodes = [] similarities = [] node_ids = [] else: # 2. Then perform semantic search similarities, node_ids = dense_search(query, nodes) result_nodes = [self.node_dict[node_id] for node_id in node_ids] return VectorStoreQueryResult( nodes=result_nodes, similarities=similarities, ids=node_ids )
### 4. Load Data into our Vector Store¶
Let's load our text chunks into the vector store, and run it on different types of queries: dense search, w/ metadata filters, and more.
In [ ]:
Copied!
```
vector_store = VectorStore3B()
# load data into the vector stores
vector_store.add(nodes)

```

vector_store = VectorStore3B() # load data into the vector stores vector_store.add(nodes)
Define an example question and embed it.
In [ ]:
Copied!
```
query_str = "Can you tell me about the key concepts for safety finetuning"
query_embedding = embed_model.get_query_embedding(query_str)

```

query_str = "Can you tell me about the key concepts for safety finetuning" query_embedding = embed_model.get_query_embedding(query_str)
#### Query the vector store with dense search.¶
In [ ]:
Copied!
```
query_obj = VectorStoreQuery(
    query_embedding=query_embedding, similarity_top_k=2
)

query_result = vector_store.query(query_obj)
for similarity, node in zip(query_result.similarities, query_result.nodes):
    print(
        "\n----------------\n"
        f"[Node ID {node.node_id}] Similarity: {similarity}\n\n"
        f"{node.get_content(metadata_mode='all')}"
        "\n----------------\n\n"
    )

```

query_obj = VectorStoreQuery( query_embedding=query_embedding, similarity_top_k=2 ) query_result = vector_store.query(query_obj) for similarity, node in zip(query_result.similarities, query_result.nodes): print( "\n----------------\n" f"[Node ID {node.node_id}] Similarity: {similarity}\n\n" f"{node.get_content(metadata_mode='all')}" "\n----------------\n\n" )
```
----------------
[Node ID 3f74fdf4-0e2e-473e-9b07-10c51eb62794] Similarity: 0.835677131511819

total_pages: 77
file_path: ./data/llama2.pdf
source: 23

Specifically, we use the following techniques in safety fine-tuning:
1. Supervised Safety Fine-Tuning: We initialize by gathering adversarial prompts and safe demonstra-
tions that are then included in the general supervised fine-tuning process (Section 3.1). This teaches
the model to align with our safety guidelines even before RLHF, and thus lays the foundation for
high-quality human preference data annotation.
2. Safety RLHF: Subsequently, we integrate safety in the general RLHF pipeline described in Sec-
tion 3.2.2. This includes training a safety-specific reward model and gathering more challenging
adversarial prompts for rejection sampling style fine-tuning and PPO optimization.
3. Safety Context Distillation: Finally, we refine our RLHF pipeline with context distillation (Askell
et al., 2021b).
----------------



----------------
[Node ID 5ad5efb3-8442-4e8a-b35a-cc3a10551dc9] Similarity: 0.827877930608312

total_pages: 77
file_path: ./data/llama2.pdf
source: 23

Benchmarks give a summary view of model capabilities and behaviors that allow us to understand general
patterns in the model, but they do not provide a fully comprehensive view of the impact the model may have
on people or real-world outcomes; that would require study of end-to-end product deployments. Further
testing and mitigation should be done to understand bias and other social issues for the specific context
in which a system may be deployed. For this, it may be necessary to test beyond the groups available in
the BOLD dataset (race, religion, and gender). As LLMs are integrated and deployed, we look forward to
continuing research that will amplify their potential for positive impact on these important social issues.
4.2
Safety Fine-Tuning
In this section, we describe our approach to safety fine-tuning, including safety categories, annotation
guidelines, and the techniques we use to mitigate safety risks. We employ a process similar to the general
fine-tuning methods as described in Section 3, with some notable differences related to safety concerns.
----------------

```

#### Query the vector store with dense search + Metadata Filters¶
In [ ]:
Copied!
```
# filters = MetadataFilters(
#     filters=[
#         ExactMatchFilter(key="page", value=3)
#     ]
# )
filters = MetadataFilters.from_dict({"source": "24"})

query_obj = VectorStoreQuery(
    query_embedding=query_embedding, similarity_top_k=2, filters=filters
)

query_result = vector_store.query(query_obj)
for similarity, node in zip(query_result.similarities, query_result.nodes):
    print(
        "\n----------------\n"
        f"[Node ID {node.node_id}] Similarity: {similarity}\n\n"
        f"{node.get_content(metadata_mode='all')}"
        "\n----------------\n\n"
    )

```

# filters = MetadataFilters( # filters=[ # ExactMatchFilter(key="page", value=3) # ] # ) filters = MetadataFilters.from_dict({"source": "24"}) query_obj = VectorStoreQuery( query_embedding=query_embedding, similarity_top_k=2, filters=filters ) query_result = vector_store.query(query_obj) for similarity, node in zip(query_result.similarities, query_result.nodes): print( "\n----------------\n" f"[Node ID {node.node_id}] Similarity: {similarity}\n\n" f"{node.get_content(metadata_mode='all')}" "\n----------------\n\n" )
```
----------------
[Node ID efe54bc0-4f9f-49ad-9dd5-900395a092fa] Similarity: 0.8190195580569283

total_pages: 77
file_path: ./data/llama2.pdf
source: 24

4.2.2
Safety Supervised Fine-Tuning
In accordance with the established guidelines from Section 4.2.1, we gather prompts and demonstrations
of safe model responses from trained annotators, and use the data for supervised fine-tuning in the same
manner as described in Section 3.1. An example can be found in Table 5.
The annotators are instructed to initially come up with prompts that they think could potentially induce
the model to exhibit unsafe behavior, i.e., perform red teaming, as defined by the guidelines. Subsequently,
annotators are tasked with crafting a safe and helpful response that the model should produce.
4.2.3
Safety RLHF
We observe early in the development of Llama 2-Chat that it is able to generalize from the safe demonstrations
in supervised fine-tuning. The model quickly learns to write detailed safe responses, address safety concerns,
explain why the topic might be sensitive, and provide additional helpful information.
----------------



----------------
[Node ID 619c884b-cdbc-44b2-aec0-2692b44740ee] Similarity: 0.8010811332867503

total_pages: 77
file_path: ./data/llama2.pdf
source: 24

In particular, when
the model outputs safe responses, they are often more detailed than what the average annotator writes.
Therefore, after gathering only a few thousand supervised demonstrations, we switched entirely to RLHF to
teach the model how to write more nuanced responses. Comprehensive tuning with RLHF has the added
benefit that it may make the model more robust to jailbreak attempts (Bai et al., 2022a).
We conduct RLHF by first collecting human preference data for safety similar to Section 3.2.2: annotators
write a prompt that they believe can elicit unsafe behavior, and then compare multiple model responses to
the prompts, selecting the response that is safest according to a set of guidelines. We then use the human
preference data to train a safety reward model (see Section 3.2.2), and also reuse the adversarial prompts to
sample from the model during the RLHF stage.
Better Long-Tail Safety Robustness without Hurting Helpfulness
Safety is inherently a long-tail problem,
where the challenge comes from a small number of very specific cases.
----------------

```

## Build a RAG System with the Vector Store¶
Now that we've built the RAG system, it's time to plug it into our downstream system!
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

```

from llama_index.core import VectorStoreIndex
In [ ]:
Copied!
```
index = VectorStoreIndex.from_vector_store(vector_store)

```

index = VectorStoreIndex.from_vector_store(vector_store)
In [ ]:
Copied!
```
query_engine = index.as_query_engine()

```

query_engine = index.as_query_engine()
In [ ]:
Copied!
```
query_str = "Can you tell me about the key concepts for safety finetuning"

```

query_str = "Can you tell me about the key concepts for safety finetuning"
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
The key concepts for safety fine-tuning include supervised safety fine-tuning, safety RLHF (Reinforcement Learning from Human Feedback), and safety context distillation. Supervised safety fine-tuning involves gathering adversarial prompts and safe demonstrations to align the model with safety guidelines before RLHF. Safety RLHF integrates safety into the RLHF pipeline by training a safety-specific reward model and gathering more challenging adversarial prompts for fine-tuning and optimization. Finally, safety context distillation is used to refine the RLHF pipeline. These techniques aim to mitigate safety risks and ensure that the model aligns with safety guidelines.

```

## Conclusion¶
That's it! We've built a simple in-memory vector store that supports very simple inserts, gets, deletes, and supports dense search and metadata filtering. This can then be plugged into the rest of LlamaIndex abstractions.
It doesn't support sparse search yet and is obviously not meant to be used in any sort of actual app. But this should expose some of what's going on under the hood!
