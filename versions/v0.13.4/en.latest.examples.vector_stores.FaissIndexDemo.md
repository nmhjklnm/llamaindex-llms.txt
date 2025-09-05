![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Faiss Vector Store¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-faiss

```

%pip install llama-index-vector-stores-faiss
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
#### Creating a Faiss Index¶
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
import faiss

# dimensions of text-ada-embedding-002
d = 1536
faiss_index = faiss.IndexFlatL2(d)

```

import faiss # dimensions of text-ada-embedding-002 d = 1536 faiss_index = faiss.IndexFlatL2(d)
#### Load documents, build the VectorStoreIndex¶
In [ ]:
Copied!
```
from llama_index.core import (
    SimpleDirectoryReader,
    load_index_from_storage,
    VectorStoreIndex,
    StorageContext,
)
from llama_index.vector_stores.faiss import FaissVectorStore
from IPython.display import Markdown, display

```

from llama_index.core import ( SimpleDirectoryReader, load_index_from_storage, VectorStoreIndex, StorageContext, ) from llama_index.vector_stores.faiss import FaissVectorStore from IPython.display import Markdown, display
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
vector_store = FaissVectorStore(faiss_index=faiss_index)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

vector_store = FaissVectorStore(faiss_index=faiss_index) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex.from_documents( documents, storage_context=storage_context )
In [ ]:
Copied!
```
# save index to disk
index.storage_context.persist()

```

# save index to disk index.storage_context.persist()
In [ ]:
Copied!
```
# load index from disk
vector_store = FaissVectorStore.from_persist_dir("./storage")
storage_context = StorageContext.from_defaults(
    vector_store=vector_store, persist_dir="./storage"
)
index = load_index_from_storage(storage_context=storage_context)

```

# load index from disk vector_store = FaissVectorStore.from_persist_dir("./storage") storage_context = StorageContext.from_defaults( vector_store=vector_store, persist_dir="./storage" ) index = load_index_from_storage(storage_context=storage_context)
#### Query Index¶
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query(
    "What did the author do after his time at Y Combinator?"
)

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query( "What did the author do after his time at Y Combinator?" )
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
