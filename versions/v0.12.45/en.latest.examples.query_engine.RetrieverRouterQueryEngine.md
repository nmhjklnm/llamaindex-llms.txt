![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Retriever Router Query Engine¶
In this tutorial, we define a router query engine based on a retriever. The retriever will select a set of nodes, and we will in turn select the right QueryEngine.
We use our new `ToolRetrieverRouterQueryEngine` class for this!
### Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# NOTE: This is ONLY necessary in jupyter notebook.
# Details: Jupyter runs an event-loop behind the scenes.
#          This results in nested event-loops when we start an event-loop to make async queries.
#          This is normally not allowed, we use nest_asyncio to allow it for convenience.
import nest_asyncio

nest_asyncio.apply()

```

# NOTE: This is ONLY necessary in jupyter notebook. # Details: Jupyter runs an event-loop behind the scenes. # This results in nested event-loops when we start an event-loop to make async queries. # This is normally not allowed, we use nest_asyncio to allow it for convenience. import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.core import SummaryIndex

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import ( VectorStoreIndex, SimpleDirectoryReader, StorageContext, ) from llama_index.core import SummaryIndex
```
INFO:numexpr.utils:Note: NumExpr detected 12 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
Note: NumExpr detected 12 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
INFO:numexpr.utils:NumExpr defaulting to 8 threads.
NumExpr defaulting to 8 threads.

```

```
/Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
### Load Data¶
We first show how to convert a Document into a set of Nodes, and insert into a DocumentStore.
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham").load_data()
In [ ]:
Copied!
```
from llama_index.core import Settings

# initialize settings (set chunk size)
Settings.chunk_size = 1024
nodes = Settings.node_parser.get_nodes_from_documents(documents)

```

from llama_index.core import Settings # initialize settings (set chunk size) Settings.chunk_size = 1024 nodes = Settings.node_parser.get_nodes_from_documents(documents)
In [ ]:
Copied!
```
# initialize storage context (by default it's in-memory)
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)

```

# initialize storage context (by default it's in-memory) storage_context = StorageContext.from_defaults() storage_context.docstore.add_documents(nodes)
### Define Summary Index and Vector Index over Same Data¶
In [ ]:
Copied!
```
summary_index = SummaryIndex(nodes, storage_context=storage_context)
vector_index = VectorStoreIndex(nodes, storage_context=storage_context)

```

summary_index = SummaryIndex(nodes, storage_context=storage_context) vector_index = VectorStoreIndex(nodes, storage_context=storage_context)
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens
> [build_index_from_nodes] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 17038 tokens
> [build_index_from_nodes] Total embedding token usage: 17038 tokens

```

### Define Query Engine and Tool for these Indices¶
We define a Query Engine for each Index. We then wrap these with our `QueryEngineTool`.
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool

list_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize", use_async=True
)
vector_query_engine = vector_index.as_query_engine(
    response_mode="tree_summarize", use_async=True
)

list_tool = QueryEngineTool.from_defaults(
    query_engine=list_query_engine,
    description="Useful for questions asking for a biography of the author.",
)
vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description=(
        "Useful for retrieving specific snippets from the author's life, like"
        " his time in college, his time in YC, or more."
    ),
)

```

from llama_index.core.tools import QueryEngineTool list_query_engine = summary_index.as_query_engine( response_mode="tree_summarize", use_async=True ) vector_query_engine = vector_index.as_query_engine( response_mode="tree_summarize", use_async=True ) list_tool = QueryEngineTool.from_defaults( query_engine=list_query_engine, description="Useful for questions asking for a biography of the author.", ) vector_tool = QueryEngineTool.from_defaults( query_engine=vector_query_engine, description=( "Useful for retrieving specific snippets from the author's life, like" " his time in college, his time in YC, or more." ), )
### Define Retrieval-Augmented Router Query Engine¶
We define a router query engine that's augmented with a retrieval mechanism, to help deal with the case when the set of choices is too large.
To do this, we first define an `ObjectIndex` over the set of query engine tools. The `ObjectIndex` is defined an underlying index data structure (e.g. a vector index, keyword index), and can serialize QueryEngineTool objects to/from our indices.
We then use our `ToolRetrieverRouterQueryEngine` class, and pass in an `ObjectRetriever` over `QueryEngineTool` objects. The `ObjectRetriever` corresponds to our `ObjectIndex`.
This retriever can then dyamically retrieve the relevant query engines during query-time. This allows us to pass in an arbitrary number of query engine tools without worrying about prompt limitations.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex

obj_index = ObjectIndex.from_objects(
    [list_tool, vector_tool],
    index_cls=VectorStoreIndex,
)

```

from llama_index.core import VectorStoreIndex from llama_index.core.objects import ObjectIndex obj_index = ObjectIndex.from_objects( [list_tool, vector_tool], index_cls=VectorStoreIndex, )
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 59 tokens
> [build_index_from_nodes] Total embedding token usage: 59 tokens

```

In [ ]:
Copied!
```
from llama_index.core.query_engine import ToolRetrieverRouterQueryEngine

query_engine = ToolRetrieverRouterQueryEngine(obj_index.as_retriever())

```

from llama_index.core.query_engine import ToolRetrieverRouterQueryEngine query_engine = ToolRetrieverRouterQueryEngine(obj_index.as_retriever())
In [ ]:
Copied!
```
response = query_engine.query("What is a biography of the author's life?")

```

response = query_engine.query("What is a biography of the author's life?")
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 10 tokens
> [retrieve] Total embedding token usage: 10 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 0 tokens
> [retrieve] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 2111 tokens
> [get_response] Total LLM token usage: 2111 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 0 tokens
> [retrieve] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 2148 tokens
> [get_response] Total LLM token usage: 2148 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.query_engine.router_query_engine:Combining responses from multiple query engines.
Combining responses from multiple query engines.
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 1063 tokens
> [get_response] Total LLM token usage: 1063 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The author is a creative person who has had a varied and interesting life. They grew up in the US and went to college, but then decided to take a break and pursue their passion for art. They applied to two art schools, RISD in the US and the Accademia di Belli Arti in Florence, and were accepted to both. They chose to go to Florence, where they took the entrance exam and passed. They then spent a year living in Florence, studying art at the Accademia and painting still lives in their bedroom. After their year in Florence, the author returned to the US and completed their BFA program at RISD. They then went on to pursue a PhD in computer science at MIT, where they wrote a dissertation on the evolution of computers. During their time at MIT, they also did consulting work and wrote essays on topics they had been thinking about. After completing their PhD, the author started a software company, Viaweb, which was eventually acquired by Yahoo. They then went on to write essays and articles about their experiences in the tech industry. They also wrote an essay about how to choose what to work on, which was based on their own experience. The author then moved back to Florence, where they found a rent-stabilized apartment and continued to pursue their interest in art. They wrote about their experiences in the art world, and experienced the reactions of readers to their essays. The author is now a successful writer and continues to write essays and articles about topics they are passionate about. 

In summary, the author's life has been a journey of exploration and creativity. They have experienced a wide range of different things in their life, from art school to computer science to the tech industry, and have used their experiences to inform their writing. They have pursued their passion for art, and have used their knowledge and experience to create meaningful work.

```

In [ ]:
Copied!
```
response

```

response
Out[ ]:
```
"\nThe author is a creative person who has had a varied and interesting life. They grew up in the US and went to college, but then decided to take a break and pursue their passion for art. They applied to two art schools, RISD in the US and the Accademia di Belli Arti in Florence, and were accepted to both. They chose to go to Florence, where they took the entrance exam and passed. They then spent a year living in Florence, studying art at the Accademia and painting still lives in their bedroom. After their year in Florence, the author returned to the US and completed their BFA program at RISD. They then went on to pursue a PhD in computer science at MIT, where they wrote a dissertation on the evolution of computers. During their time at MIT, they also did consulting work and wrote essays on topics they had been thinking about. After completing their PhD, the author started a software company, Viaweb, which was eventually acquired by Yahoo. They then went on to write essays and articles about their experiences in the tech industry. They also wrote an essay about how to choose what to work on, which was based on their own experience. The author then moved back to Florence, where they found a rent-stabilized apartment and continued to pursue their interest in art. They wrote about their experiences in the art world, and experienced the reactions of readers to their essays. The author is now a successful writer and continues to write essays and articles about topics they are passionate about. \n\nIn summary, the author's life has been a journey of exploration and creativity. They have experienced a wide range of different things in their life, from art school to computer science to the tech industry, and have used their experiences to inform their writing. They have pursued their passion for art, and have used their knowledge and experience to create meaningful work."
```

In [ ]:
Copied!
```
response = query_engine.query(
    "What did Paul Graham do during his time in college?"
)

```

response = query_engine.query( "What did Paul Graham do during his time in college?" )
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 11 tokens
> [retrieve] Total embedding token usage: 11 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 0 tokens
> [retrieve] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 1947 tokens
> [get_response] Total LLM token usage: 1947 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 0 tokens
> [retrieve] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 1947 tokens
> [get_response] Total LLM token usage: 1947 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.query_engine.router_query_engine:Combining responses from multiple query engines.
Combining responses from multiple query engines.
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 316 tokens
> [get_response] Total LLM token usage: 316 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Paul Graham studied philosophy in college, but he did not pursue AI. He continued to work on programming outside of school, writing simple games, a program to predict how high his model rockets would fly, and a word processor. He eventually convinced his father to buy him a TRS-80 computer, which he used to further his programming skills.

```

