# Tablestore Demo¶
This guide shows you how to directly use our `DocumentStore` abstraction backed by Tablestore. By putting nodes in the docstore, this allows you to define multiple indices over the same underlying docstore, instead of duplicating data across indices.
In [ ]:
Copied!
```
%pip install llama-index-storage-docstore-tablestore
%pip install llama-index-storage-index-store-tablestore
%pip install llama-index-vector-stores-tablestore

%pip install llama-index-llms-dashscope
%pip install llama-index-embeddings-dashscope

%pip install llama-index
%pip install matplotlib

```

%pip install llama-index-storage-docstore-tablestore %pip install llama-index-storage-index-store-tablestore %pip install llama-index-vector-stores-tablestore %pip install llama-index-llms-dashscope %pip install llama-index-embeddings-dashscope %pip install llama-index %pip install matplotlib
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

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex
from llama_index.core import SummaryIndex
from llama_index.core.response.notebook_utils import display_response
from llama_index.core import Settings

```

from llama_index.core import SimpleDirectoryReader, StorageContext from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex from llama_index.core import SummaryIndex from llama_index.core.response.notebook_utils import display_response from llama_index.core import Settings
#### Config Tablestore¶
Next, we use tablestore's docsstore to perform a demo.
In [ ]:
Copied!
```
import getpass
import os

os.environ["tablestore_end_point"] = getpass.getpass("tablestore end_point:")
os.environ["tablestore_instance_name"] = getpass.getpass(
    "tablestore instance_name:"
)
os.environ["tablestore_access_key_id"] = getpass.getpass(
    "tablestore access_key_id:"
)
os.environ["tablestore_access_key_secret"] = getpass.getpass(
    "tablestore access_key_secret:"
)

```

import getpass import os os.environ["tablestore_end_point"] = getpass.getpass("tablestore end_point:") os.environ["tablestore_instance_name"] = getpass.getpass( "tablestore instance_name:" ) os.environ["tablestore_access_key_id"] = getpass.getpass( "tablestore access_key_id:" ) os.environ["tablestore_access_key_secret"] = getpass.getpass( "tablestore access_key_secret:" )
#### Config DashScope LLM¶
Next, we use dashscope's llm to perform a demo.
In [ ]:
Copied!
```
import os
import getpass

os.environ["DASHSCOPE_API_KEY"] = getpass.getpass("DashScope api key:")

```

import os import getpass os.environ["DASHSCOPE_API_KEY"] = getpass.getpass("DashScope api key:")
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
#### Init Store/Embedding/LLM/StorageContext¶
In [ ]:
Copied!
```
from llama_index.storage.docstore.tablestore import TablestoreDocumentStore
from llama_index.storage.index_store.tablestore import TablestoreIndexStore
from llama_index.vector_stores.tablestore import TablestoreVectorStore
from llama_index.embeddings.dashscope import (
    DashScopeEmbedding,
    DashScopeTextEmbeddingModels,
    DashScopeTextEmbeddingType,
)
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels

embedder = DashScopeEmbedding(
    model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3,  # default demiension is 1024
    text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT,
)

dashscope_llm = DashScope(
    model_name=DashScopeGenerationModels.QWEN_MAX,
    api_key=os.environ["DASHSCOPE_API_KEY"],
)
Settings.llm = dashscope_llm

docstore = TablestoreDocumentStore.from_config(
    endpoint=os.getenv("tablestore_end_point"),
    instance_name=os.getenv("tablestore_instance_name"),
    access_key_id=os.getenv("tablestore_access_key_id"),
    access_key_secret=os.getenv("tablestore_access_key_secret"),
)

index_store = TablestoreIndexStore.from_config(
    endpoint=os.getenv("tablestore_end_point"),
    instance_name=os.getenv("tablestore_instance_name"),
    access_key_id=os.getenv("tablestore_access_key_id"),
    access_key_secret=os.getenv("tablestore_access_key_secret"),
)

vector_store = TablestoreVectorStore(
    endpoint=os.getenv("tablestore_end_point"),
    instance_name=os.getenv("tablestore_instance_name"),
    access_key_id=os.getenv("tablestore_access_key_id"),
    access_key_secret=os.getenv("tablestore_access_key_secret"),
    vector_dimension=1024,  # embedder dimension is 1024
)
vector_store.create_table_if_not_exist()
vector_store.create_search_index_if_not_exist()

storage_context = StorageContext.from_defaults(
    docstore=docstore, index_store=index_store, vector_store=vector_store
)

```

from llama_index.storage.docstore.tablestore import TablestoreDocumentStore from llama_index.storage.index_store.tablestore import TablestoreIndexStore from llama_index.vector_stores.tablestore import TablestoreVectorStore from llama_index.embeddings.dashscope import ( DashScopeEmbedding, DashScopeTextEmbeddingModels, DashScopeTextEmbeddingType, ) from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels embedder = DashScopeEmbedding( model_name=DashScopeTextEmbeddingModels.TEXT_EMBEDDING_V3, # default demiension is 1024 text_type=DashScopeTextEmbeddingType.TEXT_TYPE_DOCUMENT, ) dashscope_llm = DashScope( model_name=DashScopeGenerationModels.QWEN_MAX, api_key=os.environ["DASHSCOPE_API_KEY"], ) Settings.llm = dashscope_llm docstore = TablestoreDocumentStore.from_config( endpoint=os.getenv("tablestore_end_point"), instance_name=os.getenv("tablestore_instance_name"), access_key_id=os.getenv("tablestore_access_key_id"), access_key_secret=os.getenv("tablestore_access_key_secret"), ) index_store = TablestoreIndexStore.from_config( endpoint=os.getenv("tablestore_end_point"), instance_name=os.getenv("tablestore_instance_name"), access_key_id=os.getenv("tablestore_access_key_id"), access_key_secret=os.getenv("tablestore_access_key_secret"), ) vector_store = TablestoreVectorStore( endpoint=os.getenv("tablestore_end_point"), instance_name=os.getenv("tablestore_instance_name"), access_key_id=os.getenv("tablestore_access_key_id"), access_key_secret=os.getenv("tablestore_access_key_secret"), vector_dimension=1024, # embedder dimension is 1024 ) vector_store.create_table_if_not_exist() vector_store.create_search_index_if_not_exist() storage_context = StorageContext.from_defaults( docstore=docstore, index_store=index_store, vector_store=vector_store )
#### Add to docStore¶
In [ ]:
Copied!
```
storage_context.docstore.add_documents(nodes)

```

storage_context.docstore.add_documents(nodes)
#### Define & Add Multiple Indexes¶
Each index uses the same underlying Node.
In [ ]:
Copied!
```
# https://gpt-index.readthedocs.io/en/latest/api_reference/indices/list.html
summary_index = SummaryIndex(nodes, storage_context=storage_context)

```

# https://gpt-index.readthedocs.io/en/latest/api_reference/indices/list.html summary_index = SummaryIndex(nodes, storage_context=storage_context)
In [ ]:
Copied!
```
# https://gpt-index.readthedocs.io/en/latest/api_reference/indices/vector_store.html
vector_index = VectorStoreIndex(
    nodes,
    insert_batch_size=20,
    embed_model=embedder,
    storage_context=storage_context,
)

```

# https://gpt-index.readthedocs.io/en/latest/api_reference/indices/vector_store.html vector_index = VectorStoreIndex( nodes, insert_batch_size=20, embed_model=embedder, storage_context=storage_context, )
In [ ]:
Copied!
```
# https://gpt-index.readthedocs.io/en/latest/api_reference/indices/table.html
keyword_table_index = SimpleKeywordTableIndex(
    nodes=nodes,
    storage_context=storage_context,
    llm=dashscope_llm,
)

```

# https://gpt-index.readthedocs.io/en/latest/api_reference/indices/table.html keyword_table_index = SimpleKeywordTableIndex( nodes=nodes, storage_context=storage_context, llm=dashscope_llm, )
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
# NOTE: docstore and index_store is persisted in Tablestore by default
# NOTE: here only need to persist simple vector store to disk
storage_context.persist()

```

# NOTE: docstore and index_store is persisted in Tablestore by default # NOTE: here only need to persist simple vector store to disk storage_context.persist()
In [ ]:
Copied!
```
# note down index IDs
list_id = summary_index.index_id
vector_id = vector_index.index_id
keyword_id = keyword_table_index.index_id
print(list_id, vector_id, keyword_id)

```

# note down index IDs list_id = summary_index.index_id vector_id = vector_index.index_id keyword_id = keyword_table_index.index_id print(list_id, vector_id, keyword_id)
```
c05fec2a-ac87-4761-beeb-0901f9e6530e d0b021ed-3427-46ad-927d-12d72752dbc4 2e9bfc3a-5e69-408a-9430-7b0c8baf3d77

```

In [ ]:
Copied!
```
from llama_index.core import load_index_from_storage

# re-create storage context
storage_context = StorageContext.from_defaults(
    docstore=docstore, index_store=index_store, vector_store=vector_store
)

summary_index = load_index_from_storage(
    storage_context=storage_context,
    index_id=list_id,
)
keyword_table_index = load_index_from_storage(
    llm=dashscope_llm,
    storage_context=storage_context,
    index_id=keyword_id,
)
# You need to add "vector_store=xxx" to StorageContext to load vector index from Tablestore
vector_index = load_index_from_storage(
    insert_batch_size=20,
    embed_model=embedder,
    storage_context=storage_context,
    index_id=vector_id,
)

```

from llama_index.core import load_index_from_storage # re-create storage context storage_context = StorageContext.from_defaults( docstore=docstore, index_store=index_store, vector_store=vector_store ) summary_index = load_index_from_storage( storage_context=storage_context, index_id=list_id, ) keyword_table_index = load_index_from_storage( llm=dashscope_llm, storage_context=storage_context, index_id=keyword_id, ) # You need to add "vector_store=xxx" to StorageContext to load vector index from Tablestore vector_index = load_index_from_storage( insert_batch_size=20, embed_model=embedder, storage_context=storage_context, index_id=vector_id, )
#### Test out some Queries¶
In [ ]:
Copied!
```
Settings.llm = dashscope_llm
Settings.chunk_size = 1024

```

Settings.llm = dashscope_llm Settings.chunk_size = 1024
In [ ]:
Copied!
```
query_engine = summary_index.as_query_engine()
list_response = query_engine.query("What is a summary of this document?")

```

query_engine = summary_index.as_query_engine() list_response = query_engine.query("What is a summary of this document?")
In [ ]:
Copied!
```
display_response(list_response)

```

display_response(list_response)
In [ ]:
Copied!
```
query_engine = vector_index.as_query_engine()
vector_response = query_engine.query("What did the author do growing up?")

```

query_engine = vector_index.as_query_engine() vector_response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
display_response(vector_response)

```

display_response(vector_response)
**`Final Response:`**Growing up, the author was involved in writing and programming outside of school. Initially, they wrote short stories, which they now consider to be not very good, as they lacked much plot and focused more on characters' emotions. In terms of programming, the author started with an IBM 1401 at their junior high school, where they attempted to write basic programs in Fortran using punch cards. Later, after getting a TRS-80 microcomputer, the author delved deeper into programming, creating simple games, a program to predict the flight height of model rockets, and even a word processor that their father used for writing.
In [ ]:
Copied!
```
query_engine = keyword_table_index.as_query_engine()
keyword_response = query_engine.query(
    "What did the author do after his time at YC?"
)

```

query_engine = keyword_table_index.as_query_engine() keyword_response = query_engine.query( "What did the author do after his time at YC?" )
In [ ]:
Copied!
```
display_response(keyword_response)

```

display_response(keyword_response)
**`Final Response:`**After his time at YC, the author decided to take up painting, dedicating himself to it to see how good he could become. He spent most of 2014 focused on this. However, by November, he lost interest and stopped. Following this, he returned to writing essays and even ventured into topics beyond startups. In March 2015, he also began working on Lisp again.
