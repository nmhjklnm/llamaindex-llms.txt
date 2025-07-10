# MongoDB Demo¶
This guide shows you how to directly use our `DocumentStore` abstraction backed by MongoDB. By putting nodes in the docstore, this allows you to define multiple indices over the same underlying docstore, instead of duplicating data across indices.
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-storage-docstore-mongodb
%pip install llama-index-storage-index-store-mongodb
%pip install llama-index-llms-openai

```

%pip install llama-index-storage-docstore-mongodb %pip install llama-index-storage-index-store-mongodb %pip install llama-index-llms-openai
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
MONGO_URI = os.environ["MONGO_URI"]

```

MONGO_URI = os.environ["MONGO_URI"]
In [ ]:
Copied!
```
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.storage.index_store.mongodb import MongoIndexStore

```

from llama_index.storage.docstore.mongodb import MongoDocumentStore from llama_index.storage.index_store.mongodb import MongoIndexStore
In [ ]:
Copied!
```
storage_context = StorageContext.from_defaults(
    docstore=MongoDocumentStore.from_uri(uri=MONGO_URI),
    index_store=MongoIndexStore.from_uri(uri=MONGO_URI),
)

```

storage_context = StorageContext.from_defaults( docstore=MongoDocumentStore.from_uri(uri=MONGO_URI), index_store=MongoIndexStore.from_uri(uri=MONGO_URI), )
In [ ]:
Copied!
```
storage_context.docstore.add_documents(nodes)

```

storage_context.docstore.add_documents(nodes)
#### Define Multiple Indexes¶
Each index uses the same underlying Node.
In [ ]:
Copied!
```
summary_index = SummaryIndex(nodes, storage_context=storage_context)

```

summary_index = SummaryIndex(nodes, storage_context=storage_context)
In [ ]:
Copied!
```
vector_index = VectorStoreIndex(nodes, storage_context=storage_context)

```

vector_index = VectorStoreIndex(nodes, storage_context=storage_context)
In [ ]:
Copied!
```
keyword_table_index = SimpleKeywordTableIndex(
    nodes, storage_context=storage_context
)

```

keyword_table_index = SimpleKeywordTableIndex( nodes, storage_context=storage_context )
In [ ]:
Copied!
```
# NOTE: the docstore still has the same nodes
len(storage_context.docstore.docs)

```

# NOTE: the docstore still has the same nodes len(storage_context.docstore.docs)
#### Test out saving and loading¶
In [ ]:
Copied!
```
# NOTE: docstore and index_store is persisted in MongoDB by default
# NOTE: here only need to persist simple vector store to disk
storage_context.persist()

```

# NOTE: docstore and index_store is persisted in MongoDB by default # NOTE: here only need to persist simple vector store to disk storage_context.persist()
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
    docstore=MongoDocumentStore.from_uri(uri=MONGO_URI),
    index_store=MongoIndexStore.from_uri(uri=MONGO_URI),
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

from llama_index.core import load_index_from_storage # re-create storage context storage_context = StorageContext.from_defaults( docstore=MongoDocumentStore.from_uri(uri=MONGO_URI), index_store=MongoIndexStore.from_uri(uri=MONGO_URI), ) # load indices summary_index = load_index_from_storage( storage_context=storage_context, index_id=list_id ) vector_index = load_index_from_storage( storage_context=storage_context, index_id=vector_id ) keyword_table_index = load_index_from_storage( storage_context=storage_context, index_id=keyword_id )
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
