![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Retriever Query Engine with Custom Retrievers - Simple Hybrid Search¶
In this tutorial, we show you how to define a very simple version of hybrid search!
Combine keyword lookup retrieval with vector retrieval using "AND" and "OR" conditions.
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
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
Will not apply HSTS. The HSTS database must be a regular and non-world-writable file.
ERROR: could not open HSTS store at '/home/loganm/.wget-hsts'. HSTS will be disabled.
--2023-11-23 12:54:37--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.109.133, 185.199.111.133, 185.199.108.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.109.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.04s   

2023-11-23 12:54:37 (1.77 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

### Load Data¶
We first show how to convert a Document into a set of Nodes, and insert into a DocumentStore.
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

# load documents
documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

from llama_index.core import SimpleDirectoryReader # load documents documents = SimpleDirectoryReader("./data/paul_graham").load_data()
In [ ]:
Copied!
```
from llama_index.core import Settings

nodes = Settings.node_parser.get_nodes_from_documents(documents)

```

from llama_index.core import Settings nodes = Settings.node_parser.get_nodes_from_documents(documents)
In [ ]:
Copied!
```
from llama_index.core import StorageContext

# initialize storage context (by default it's in-memory)
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)

```

from llama_index.core import StorageContext # initialize storage context (by default it's in-memory) storage_context = StorageContext.from_defaults() storage_context.docstore.add_documents(nodes)
### Define Vector Index and Keyword Table Index over Same Data¶
We build a vector index and keyword index over the same DocumentStore
In [ ]:
Copied!
```
from llama_index.core import SimpleKeywordTableIndex, VectorStoreIndex

vector_index = VectorStoreIndex(nodes, storage_context=storage_context)
keyword_index = SimpleKeywordTableIndex(nodes, storage_context=storage_context)

```

from llama_index.core import SimpleKeywordTableIndex, VectorStoreIndex vector_index = VectorStoreIndex(nodes, storage_context=storage_context) keyword_index = SimpleKeywordTableIndex(nodes, storage_context=storage_context)
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

### Define Custom Retriever¶
We now define a custom retriever class that can implement basic hybrid search with both keyword lookup and semantic search.
  * setting "AND" means we take the intersection of the two retrieved sets
  * setting "OR" means we take the union


In [ ]:
Copied!
```
# import QueryBundle
from llama_index.core import QueryBundle

# import NodeWithScore
from llama_index.core.schema import NodeWithScore

# Retrievers
from llama_index.core.retrievers import (
    BaseRetriever,
    VectorIndexRetriever,
    KeywordTableSimpleRetriever,
)

from typing import List

```

# import QueryBundle from llama_index.core import QueryBundle # import NodeWithScore from llama_index.core.schema import NodeWithScore # Retrievers from llama_index.core.retrievers import ( BaseRetriever, VectorIndexRetriever, KeywordTableSimpleRetriever, ) from typing import List
In [ ]:
Copied!
```
class CustomRetriever(BaseRetriever):
    """Custom retriever that performs both semantic search and hybrid search."""

    def __init__(
        self,
        vector_retriever: VectorIndexRetriever,
        keyword_retriever: KeywordTableSimpleRetriever,
        mode: str = "AND",
    ) -> None:
        """Init params."""

        self._vector_retriever = vector_retriever
        self._keyword_retriever = keyword_retriever
        if mode not in ("AND", "OR"):
            raise ValueError("Invalid mode.")
        self._mode = mode
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve nodes given query."""

        vector_nodes = self._vector_retriever.retrieve(query_bundle)
        keyword_nodes = self._keyword_retriever.retrieve(query_bundle)

        vector_ids = {n.node.node_id for n in vector_nodes}
        keyword_ids = {n.node.node_id for n in keyword_nodes}

        combined_dict = {n.node.node_id: n for n in vector_nodes}
        combined_dict.update({n.node.node_id: n for n in keyword_nodes})

        if self._mode == "AND":
            retrieve_ids = vector_ids.intersection(keyword_ids)
        else:
            retrieve_ids = vector_ids.union(keyword_ids)

        retrieve_nodes = [combined_dict[rid] for rid in retrieve_ids]
        return retrieve_nodes

```

class CustomRetriever(BaseRetriever): """Custom retriever that performs both semantic search and hybrid search.""" def __init__( self, vector_retriever: VectorIndexRetriever, keyword_retriever: KeywordTableSimpleRetriever, mode: str = "AND", ) -> None: """Init params.""" self._vector_retriever = vector_retriever self._keyword_retriever = keyword_retriever if mode not in ("AND", "OR"): raise ValueError("Invalid mode.") self._mode = mode super().__init__() def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]: """Retrieve nodes given query.""" vector_nodes = self._vector_retriever.retrieve(query_bundle) keyword_nodes = self._keyword_retriever.retrieve(query_bundle) vector_ids = {n.node.node_id for n in vector_nodes} keyword_ids = {n.node.node_id for n in keyword_nodes} combined_dict = {n.node.node_id: n for n in vector_nodes} combined_dict.update({n.node.node_id: n for n in keyword_nodes}) if self._mode == "AND": retrieve_ids = vector_ids.intersection(keyword_ids) else: retrieve_ids = vector_ids.union(keyword_ids) retrieve_nodes = [combined_dict[rid] for rid in retrieve_ids] return retrieve_nodes
### Plugin Retriever into Query Engine¶
Plugin retriever into a query engine, and run some queries
In [ ]:
Copied!
```
from llama_index.core import get_response_synthesizer
from llama_index.core.query_engine import RetrieverQueryEngine

# define custom retriever
vector_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=2)
keyword_retriever = KeywordTableSimpleRetriever(index=keyword_index)
custom_retriever = CustomRetriever(vector_retriever, keyword_retriever)

# define response synthesizer
response_synthesizer = get_response_synthesizer()

# assemble query engine
custom_query_engine = RetrieverQueryEngine(
    retriever=custom_retriever,
    response_synthesizer=response_synthesizer,
)

# vector query engine
vector_query_engine = RetrieverQueryEngine(
    retriever=vector_retriever,
    response_synthesizer=response_synthesizer,
)
# keyword query engine
keyword_query_engine = RetrieverQueryEngine(
    retriever=keyword_retriever,
    response_synthesizer=response_synthesizer,
)

```

from llama_index.core import get_response_synthesizer from llama_index.core.query_engine import RetrieverQueryEngine # define custom retriever vector_retriever = VectorIndexRetriever(index=vector_index, similarity_top_k=2) keyword_retriever = KeywordTableSimpleRetriever(index=keyword_index) custom_retriever = CustomRetriever(vector_retriever, keyword_retriever) # define response synthesizer response_synthesizer = get_response_synthesizer() # assemble query engine custom_query_engine = RetrieverQueryEngine( retriever=custom_retriever, response_synthesizer=response_synthesizer, ) # vector query engine vector_query_engine = RetrieverQueryEngine( retriever=vector_retriever, response_synthesizer=response_synthesizer, ) # keyword query engine keyword_query_engine = RetrieverQueryEngine( retriever=keyword_retriever, response_synthesizer=response_synthesizer, )
In [ ]:
Copied!
```
response = custom_query_engine.query(
    "What did the author do during his time at YC?"
)

```

response = custom_query_engine.query( "What did the author do during his time at YC?" )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:llama_index.indices.keyword_table.retrievers:> Starting query: What did the author do during his time at YC?

```

```
> Starting query: What did the author do during his time at YC?
INFO:llama_index.indices.keyword_table.retrievers:query keywords: ['author', 'yc', 'time']
query keywords: ['author', 'yc', 'time']
INFO:llama_index.indices.keyword_table.retrievers:> Extracted keywords: ['yc', 'time']
> Extracted keywords: ['yc', 'time']
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
During his time at YC, the author worked on various projects, including writing essays and working on YC itself. He also wrote all of YC's internal software in Arc. Additionally, he mentioned that he dealt with urgent problems, with about a 60% chance of them being related to Hacker News (HN), and a 40% chance of them being related to everything else combined. The author also mentioned that YC was different from other kinds of work he had done, as the problems of the startups in each batch became their problems, and he worked hard even at the parts of the job he didn't like.

```

In [ ]:
Copied!
```
# hybrid search can allow us to not retrieve nodes that are irrelevant
# Yale is never mentioned in the essay
response = custom_query_engine.query(
    "What did the author do during his time at Yale?"
)

```

# hybrid search can allow us to not retrieve nodes that are irrelevant # Yale is never mentioned in the essay response = custom_query_engine.query( "What did the author do during his time at Yale?" )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:llama_index.indices.keyword_table.retrievers:> Starting query: What did the author do during his time at Yale?
> Starting query: What did the author do during his time at Yale?
INFO:llama_index.indices.keyword_table.retrievers:query keywords: ['author', 'yale', 'time']
query keywords: ['author', 'yale', 'time']
INFO:llama_index.indices.keyword_table.retrievers:> Extracted keywords: ['time']
> Extracted keywords: ['time']

```

In [ ]:
Copied!
```
print(str(response))
len(response.source_nodes)

```

print(str(response)) len(response.source_nodes)
```
Empty Response

```

Out[ ]:


In [ ]:
Copied!
```
# in contrast, vector search will return an answer
response = vector_query_engine.query(
    "What did the author do during his time at Yale?"
)

```

# in contrast, vector search will return an answer response = vector_query_engine.query( "What did the author do during his time at Yale?" )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
print(str(response))
len(response.source_nodes)

```

print(str(response)) len(response.source_nodes)
```
The context information does not provide any information about the author's time at Yale.

```

Out[ ]:


