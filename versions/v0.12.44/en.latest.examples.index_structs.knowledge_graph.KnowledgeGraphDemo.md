# Knowledge Graph Index¶
This tutorial gives a basic overview of how to use our `KnowledgeGraphIndex`, which handles automated knowledge graph construction from unstructured text as well as entity-based querying.
If you would like to query knowledge graphs in more flexible ways, including pre-existing ones, please check out our `KnowledgeGraphQueryEngine` and other constructs.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
# My OpenAI Key
import os

os.environ["OPENAI_API_KEY"] = "INSERT OPENAI KEY"

```

# My OpenAI Key import os os.environ["OPENAI_API_KEY"] = "INSERT OPENAI KEY"
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO)
## Using Knowledge Graph¶
#### Building the Knowledge Graph¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, KnowledgeGraphIndex
from llama_index.core.graph_stores import SimpleGraphStore

from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from IPython.display import Markdown, display

```

from llama_index.core import SimpleDirectoryReader, KnowledgeGraphIndex from llama_index.core.graph_stores import SimpleGraphStore from llama_index.llms.openai import OpenAI from llama_index.core import Settings from IPython.display import Markdown, display
```
INFO:numexpr.utils:NumExpr defaulting to 8 threads.

```

In [ ]:
Copied!
```
documents = SimpleDirectoryReader(
    "../../../../examples/paul_graham_essay/data"
).load_data()

```

documents = SimpleDirectoryReader( "../../../../examples/paul_graham_essay/data" ).load_data()
In [ ]:
Copied!
```
# define LLM
# NOTE: at the time of demo, text-davinci-002 did not have rate-limit errors

llm = OpenAI(temperature=0, model="text-davinci-002")
Settings.llm = llm
Settings.chunk_size = 512

```

# define LLM # NOTE: at the time of demo, text-davinci-002 did not have rate-limit errors llm = OpenAI(temperature=0, model="text-davinci-002") Settings.llm = llm Settings.chunk_size = 512
In [ ]:
Copied!
```
from llama_index.core import StorageContext

graph_store = SimpleGraphStore()
storage_context = StorageContext.from_defaults(graph_store=graph_store)

# NOTE: can take a while!
index = KnowledgeGraphIndex.from_documents(
    documents,
    max_triplets_per_chunk=2,
    storage_context=storage_context,
)

```

from llama_index.core import StorageContext graph_store = SimpleGraphStore() storage_context = StorageContext.from_defaults(graph_store=graph_store) # NOTE: can take a while! index = KnowledgeGraphIndex.from_documents( documents, max_triplets_per_chunk=2, storage_context=storage_context, )
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens

```

#### [Optional] Try building the graph and manually add triplets!¶
#### Querying the Knowledge Graph¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    include_text=False, response_mode="tree_summarize"
)
response = query_engine.query(
    "Tell me more about Interleaf",
)

```

query_engine = index.as_query_engine( include_text=False, response_mode="tree_summarize" ) response = query_engine.query( "Tell me more about Interleaf", )
```
INFO:llama_index.indices.knowledge_graph.retrievers:> Starting query: Tell me more about Interleaf
INFO:llama_index.indices.knowledge_graph.retrievers:> Query keywords: ['Interleaf', 'company', 'software', 'history']
ERROR:llama_index.indices.knowledge_graph.retrievers:Index was not constructed with embeddings, skipping embedding usage...
INFO:llama_index.indices.knowledge_graph.retrievers:> Extracted relationships: The following are knowledge triplets in max depth 2 in the form of `subject [predicate, object, predicate_next_hop, object_next_hop ...]`
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 116 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 116 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
**Interleaf was a software company that developed and published document preparation and desktop publishing software. It was founded in 1986 and was headquartered in Waltham, Massachusetts. The company was acquired by Quark, Inc. in 2000.**
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    include_text=True, response_mode="tree_summarize"
)
response = query_engine.query(
    "Tell me more about what the author worked on at Interleaf",
)

```

query_engine = index.as_query_engine( include_text=True, response_mode="tree_summarize" ) response = query_engine.query( "Tell me more about what the author worked on at Interleaf", )
```
INFO:llama_index.indices.knowledge_graph.retrievers:> Starting query: Tell me more about what the author worked on at Interleaf
INFO:llama_index.indices.knowledge_graph.retrievers:> Query keywords: ['author', 'Interleaf', 'work']
ERROR:llama_index.indices.knowledge_graph.retrievers:Index was not constructed with embeddings, skipping embedding usage...
INFO:llama_index.indices.knowledge_graph.retrievers:> Extracted relationships: The following are knowledge triplets in max depth 2 in the form of `subject [predicate, object, predicate_next_hop, object_next_hop ...]`
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 104 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 104 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
**The author worked on a number of projects at Interleaf, including the development of the company's flagship product, the Interleaf Publisher.**
#### Query with embeddings¶
In [ ]:
Copied!
```
# NOTE: can take a while!
new_index = KnowledgeGraphIndex.from_documents(
    documents,
    max_triplets_per_chunk=2,
    include_embeddings=True,
)

```

# NOTE: can take a while! new_index = KnowledgeGraphIndex.from_documents( documents, max_triplets_per_chunk=2, include_embeddings=True, )
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
# query using top 3 triplets plus keywords (duplicate triplets are removed)
query_engine = index.as_query_engine(
    include_text=True,
    response_mode="tree_summarize",
    embedding_mode="hybrid",
    similarity_top_k=5,
)
response = query_engine.query(
    "Tell me more about what the author worked on at Interleaf",
)

```

# query using top 3 triplets plus keywords (duplicate triplets are removed) query_engine = index.as_query_engine( include_text=True, response_mode="tree_summarize", embedding_mode="hybrid", similarity_top_k=5, ) response = query_engine.query( "Tell me more about what the author worked on at Interleaf", )
```
INFO:llama_index.indices.knowledge_graph.retrievers:> Starting query: Tell me more about what the author worked on at Interleaf
INFO:llama_index.indices.knowledge_graph.retrievers:> Query keywords: ['author', 'Interleaf', 'work']
ERROR:llama_index.indices.knowledge_graph.retrievers:Index was not constructed with embeddings, skipping embedding usage...
INFO:llama_index.indices.knowledge_graph.retrievers:> Extracted relationships: The following are knowledge triplets in max depth 2 in the form of `subject [predicate, object, predicate_next_hop, object_next_hop ...]`
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 104 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 104 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
**The author worked on a number of projects at Interleaf, including the development of the company's flagship product, the Interleaf Publisher.**
#### Visualizing the Graph¶
In [ ]:
Copied!
```
## create graph
from pyvis.network import Network

g = index.get_networkx_graph()
net = Network(notebook=True, cdn_resources="in_line", directed=True)
net.from_nx(g)
net.show("example.html")

```

## create graph from pyvis.network import Network g = index.get_networkx_graph() net = Network(notebook=True, cdn_resources="in_line", directed=True) net.from_nx(g) net.show("example.html")
```
example.html

```

Out[ ]:
#### [Optional] Try building the graph and manually add triplets!¶
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

```

from llama_index.core.node_parser import SentenceSplitter
In [ ]:
Copied!
```
node_parser = SentenceSplitter()

```

node_parser = SentenceSplitter()
In [ ]:
Copied!
```
nodes = node_parser.get_nodes_from_documents(documents)

```

nodes = node_parser.get_nodes_from_documents(documents)
In [ ]:
Copied!
```
# initialize an empty index for now
index = KnowledgeGraphIndex(
    [],
)

```

# initialize an empty index for now index = KnowledgeGraphIndex( [], )
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
# add keyword mappings and nodes manually
# add triplets (subject, relationship, object)

# for node 0
node_0_tups = [
    ("author", "worked on", "writing"),
    ("author", "worked on", "programming"),
]
for tup in node_0_tups:
    index.upsert_triplet_and_node(tup, nodes[0])

# for node 1
node_1_tups = [
    ("Interleaf", "made software for", "creating documents"),
    ("Interleaf", "added", "scripting language"),
    ("software", "generate", "web sites"),
]
for tup in node_1_tups:
    index.upsert_triplet_and_node(tup, nodes[1])

```

# add keyword mappings and nodes manually # add triplets (subject, relationship, object) # for node 0 node_0_tups = [ ("author", "worked on", "writing"), ("author", "worked on", "programming"), ] for tup in node_0_tups: index.upsert_triplet_and_node(tup, nodes[0]) # for node 1 node_1_tups = [ ("Interleaf", "made software for", "creating documents"), ("Interleaf", "added", "scripting language"), ("software", "generate", "web sites"), ] for tup in node_1_tups: index.upsert_triplet_and_node(tup, nodes[1])
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    include_text=False, response_mode="tree_summarize"
)
response = query_engine.query(
    "Tell me more about Interleaf",
)

```

query_engine = index.as_query_engine( include_text=False, response_mode="tree_summarize" ) response = query_engine.query( "Tell me more about Interleaf", )
```
INFO:llama_index.indices.knowledge_graph.retrievers:> Starting query: Tell me more about Interleaf
INFO:llama_index.indices.knowledge_graph.retrievers:> Query keywords: ['Interleaf', 'company', 'software', 'history']
ERROR:llama_index.indices.knowledge_graph.retrievers:Index was not constructed with embeddings, skipping embedding usage...
INFO:llama_index.indices.knowledge_graph.retrievers:> Extracted relationships: The following are knowledge triplets in max depth 2 in the form of `subject [predicate, object, predicate_next_hop, object_next_hop ...]`
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 116 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 116 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
str(response)

```

str(response)
Out[ ]:
```
'\nInterleaf was a software company that developed and published document preparation and desktop publishing software. It was founded in 1986 and was headquartered in Waltham, Massachusetts. The company was acquired by Quark, Inc. in 2000.'
```

