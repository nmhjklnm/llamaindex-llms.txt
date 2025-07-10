![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Redis Docstore+Index Store Demo¶
This guide shows you how to directly use our `DocumentStore` abstraction and `IndexStore` abstraction backed by Redis. By putting nodes in the docstore, this allows you to define multiple indices over the same underlying docstore, instead of duplicating data across indices.
The index itself is also stored in Redis through the `IndexStore`.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-storage-docstore-redis
%pip install llama-index-storage-index-store-redis
%pip install llama-index-llms-openai

```

%pip install llama-index-storage-docstore-redis %pip install llama-index-storage-index-store-redis %pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
import logging
import sys
import os

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys import os logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex
from llama_index.core import SummaryIndex
from llama_index.core import ComposableGraph
from llama_index.llms.openai import OpenAI
from llama_index.core.response.notebook_utils import display_response
from llama_index.core import Settings

```

from llama_index.core import SimpleDirectoryReader, StorageContext from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex from llama_index.core import SummaryIndex from llama_index.core import ComposableGraph from llama_index.llms.openai import OpenAI from llama_index.core.response.notebook_utils import display_response from llama_index.core import Settings
```
INFO:numexpr.utils:Note: NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
Note: NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
INFO:numexpr.utils:NumExpr defaulting to 8 threads.
NumExpr defaulting to 8 threads.

```

```
/home/loganm/miniconda3/envs/llama-index/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

#### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
#### Load Documents¶
In [ ]:
Copied!
```
reader = SimpleDirectoryReader("./data/paul_graham/")
documents = reader.load_data()

```

reader = SimpleDirectoryReader("./data/paul_graham/") documents = reader.load_data()
#### Parse into Nodes¶
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

nodes = SentenceSplitter().get_nodes_from_documents(documents)

```

from llama_index.core.node_parser import SentenceSplitter nodes = SentenceSplitter().get_nodes_from_documents(documents)
#### Add to Docstore¶
In [ ]:
Copied!
```
REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

```

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1") REDIS_PORT = os.getenv("REDIS_PORT", 6379)
In [ ]:
Copied!
```
from llama_index.storage.docstore.redis import RedisDocumentStore
from llama_index.storage.index_store.redis import RedisIndexStore

```

from llama_index.storage.docstore.redis import RedisDocumentStore from llama_index.storage.index_store.redis import RedisIndexStore
```
/home/loganm/miniconda3/envs/llama-index/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

In [ ]:
Copied!
```
storage_context = StorageContext.from_defaults(
    docstore=RedisDocumentStore.from_host_and_port(
        host=REDIS_HOST, port=REDIS_PORT, namespace="llama_index"
    ),
    index_store=RedisIndexStore.from_host_and_port(
        host=REDIS_HOST, port=REDIS_PORT, namespace="llama_index"
    ),
)

```

storage_context = StorageContext.from_defaults( docstore=RedisDocumentStore.from_host_and_port( host=REDIS_HOST, port=REDIS_PORT, namespace="llama_index" ), index_store=RedisIndexStore.from_host_and_port( host=REDIS_HOST, port=REDIS_PORT, namespace="llama_index" ), )
In [ ]:
Copied!
```
storage_context.docstore.add_documents(nodes)

```

storage_context.docstore.add_documents(nodes)
In [ ]:
Copied!
```
len(storage_context.docstore.docs)

```

len(storage_context.docstore.docs)
Out[ ]:


#### Define Multiple Indexes¶
Each index uses the same underlying Node.
In [ ]:
Copied!
```
summary_index = SummaryIndex(nodes, storage_context=storage_context)

```

summary_index = SummaryIndex(nodes, storage_context=storage_context)
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens
> [build_index_from_nodes] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
vector_index = VectorStoreIndex(nodes, storage_context=storage_context)

```

vector_index = VectorStoreIndex(nodes, storage_context=storage_context)
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 17050 tokens
> [build_index_from_nodes] Total embedding token usage: 17050 tokens

```

In [ ]:
Copied!
```
keyword_table_index = SimpleKeywordTableIndex(
    nodes, storage_context=storage_context
)

```

keyword_table_index = SimpleKeywordTableIndex( nodes, storage_context=storage_context )
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens
> [build_index_from_nodes] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
# NOTE: the docstore still has the same nodes
len(storage_context.docstore.docs)

```

# NOTE: the docstore still has the same nodes len(storage_context.docstore.docs)
Out[ ]:


#### Test out saving and loading¶
In [ ]:
Copied!
```
# NOTE: docstore and index_store is persisted in Redis by default
# NOTE: here only need to persist simple vector store to disk
storage_context.persist(persist_dir="./storage")

```

# NOTE: docstore and index_store is persisted in Redis by default # NOTE: here only need to persist simple vector store to disk storage_context.persist(persist_dir="./storage")
In [ ]:
Copied!
```
# note down index IDs
list_id = summary_index.index_id
vector_id = vector_index.index_id
keyword_id = keyword_table_index.index_id

```

# note down index IDs list_id = summary_index.index_id vector_id = vector_index.index_id keyword_id = keyword_table_index.index_id
In [ ]:
Copied!
```
from llama_index.core import load_index_from_storage

# re-create storage context
storage_context = StorageContext.from_defaults(
    docstore=RedisDocumentStore.from_host_and_port(
        host=REDIS_HOST, port=REDIS_PORT, namespace="llama_index"
    ),
    index_store=RedisIndexStore.from_host_and_port(
        host=REDIS_HOST, port=REDIS_PORT, namespace="llama_index"
    ),
)

# load indices
summary_index = load_index_from_storage(
    storage_context=storage_context, index_id=list_id
)
vector_index = load_index_from_storage(
    storage_context=storage_context, index_id=vector_id
)
keyword_table_index = load_index_from_storage(
    storage_context=storage_context, index_id=keyword_id
)

```

from llama_index.core import load_index_from_storage # re-create storage context storage_context = StorageContext.from_defaults( docstore=RedisDocumentStore.from_host_and_port( host=REDIS_HOST, port=REDIS_PORT, namespace="llama_index" ), index_store=RedisIndexStore.from_host_and_port( host=REDIS_HOST, port=REDIS_PORT, namespace="llama_index" ), ) # load indices summary_index = load_index_from_storage( storage_context=storage_context, index_id=list_id ) vector_index = load_index_from_storage( storage_context=storage_context, index_id=vector_id ) keyword_table_index = load_index_from_storage( storage_context=storage_context, index_id=keyword_id )
```
INFO:llama_index.indices.loading:Loading indices with ids: ['24e98f9b-9586-4fc6-8341-8dce895e5bcc']
Loading indices with ids: ['24e98f9b-9586-4fc6-8341-8dce895e5bcc']
INFO:llama_index.indices.loading:Loading indices with ids: ['f7b2aeb3-4dad-4750-8177-78d5ae706284']
Loading indices with ids: ['f7b2aeb3-4dad-4750-8177-78d5ae706284']
INFO:llama_index.indices.loading:Loading indices with ids: ['9a9198b4-7cb9-4c96-97a7-5f404f43b9cd']
Loading indices with ids: ['9a9198b4-7cb9-4c96-97a7-5f404f43b9cd']

```

#### Test out some Queries¶
In [ ]:
Copied!
```
chatgpt = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.llm = chatgpt
Settings.chunk_size = 1024

```

chatgpt = OpenAI(temperature=0, model="gpt-3.5-turbo") Settings.llm = chatgpt Settings.chunk_size = 1024
In [ ]:
Copied!
```
query_engine = summary_index.as_query_engine()
list_response = query_engine.query("What is a summary of this document?")

```

query_engine = summary_index.as_query_engine() list_response = query_engine.query("What is a summary of this document?")
```
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 26111 tokens
> [get_response] Total LLM token usage: 26111 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
display_response(list_response)

```

display_response(list_response)
**`Final Response:`**This document is a narrative of the author's journey from writing and programming as a young person to pursuing a career in art. It describes his experiences in high school, college, and graduate school, and how he eventually decided to pursue art as a career. He applied to art schools and eventually was accepted to RISD and the Accademia di Belli Arti in Florence. He passed the entrance exam for the Accademia and began studying art there. He then moved to New York and worked freelance while writing a book on Lisp. He eventually started a company to put art galleries online, but it was unsuccessful. He then pivoted to creating software to build online stores, which eventually became successful. He had the idea to run the software on the server and let users control it by clicking on links, which meant users wouldn't need anything more than a browser. This kind of software, known as "internet storefronts," was eventually successful. He and his team worked hard to make the software user-friendly and inexpensive, and eventually the company was bought by Yahoo. After the sale, he left to pursue his dream of painting, and eventually found success in New York. He was able to afford luxuries such as taxis and restaurants, and he experimented with a new kind of still life painting. He also had the idea to create a web app for making web apps, which he eventually pursued and was successful with. He then started Y Combinator, an investment firm that focused on helping startups, with his own money and the help of his friends Robert and Trevor. He wrote essays and books, invited undergrads to apply to the Summer Founders Program, and eventually married Jessica Livingston. After his mother's death, he decided to quit Y Combinator and pursue painting, but eventually ran out of steam and started writing essays and working on Lisp again. He wrote a new Lisp, called Bel, in itself in Arc, and it took him four years to complete. During this time, he worked hard to make the language user-friendly and precise, and he also took time to enjoy life with his family. He encountered various obstacles along the way, such as customs that constrained him even after the restrictions that caused them had disappeared, and he also had to deal with misinterpretations of his essays on forums. In the end, he was successful in creating Bel and was able to pursue his dream of painting.
In [ ]:
Copied!
```
query_engine = vector_index.as_query_engine()
vector_response = query_engine.query("What did the author do growing up?")

```

query_engine = vector_index.as_query_engine() vector_response = query_engine.query("What did the author do growing up?")
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 8 tokens
> [retrieve] Total embedding token usage: 8 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 0 tokens
> [get_response] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
display_response(vector_response)

```

display_response(vector_response)
**`Final Response:`**None
In [ ]:
Copied!
```
query_engine = keyword_table_index.as_query_engine()
keyword_response = query_engine.query(
    "What did the author do after his time at YC?"
)

```

query_engine = keyword_table_index.as_query_engine() keyword_response = query_engine.query( "What did the author do after his time at YC?" )
```
INFO:llama_index.indices.keyword_table.retrievers:> Starting query: What did the author do after his time at YC?
> Starting query: What did the author do after his time at YC?
INFO:llama_index.indices.keyword_table.retrievers:query keywords: ['action', 'yc', 'after', 'time', 'author']
query keywords: ['action', 'yc', 'after', 'time', 'author']
INFO:llama_index.indices.keyword_table.retrievers:> Extracted keywords: ['yc', 'time']
> Extracted keywords: ['yc', 'time']
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 10216 tokens
> [get_response] Total LLM token usage: 10216 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
display_response(keyword_response)

```

display_response(keyword_response)
**`Final Response:`**After his time at YC, the author decided to pursue painting and writing. He wanted to see how good he could get if he really focused on it, so he started painting the day after he stopped working on YC. He spent most of the rest of 2014 painting and was able to become better than he had been before. He also wrote essays and started working on Lisp again in March 2015. He then spent 4 years working on a new Lisp, called Bel, which he wrote in itself in Arc. He had to ban himself from writing essays during most of this time, and he moved to England in the summer of 2016. He also wrote a book about Lisp hacking, called On Lisp, which was published in 1993. In the fall of 2019, Bel was finally finished. He also experimented with a new kind of still life painting, and tried to build a web app for making web apps, which he named Aspra. He eventually decided to build a subset of this app as an open source project, which was the new Lisp dialect he called Arc.
