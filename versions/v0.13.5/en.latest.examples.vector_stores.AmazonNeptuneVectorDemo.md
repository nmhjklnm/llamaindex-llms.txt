# Amazon Neptune - Neptune Analytics vector store¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-neptune

```

%pip install llama-index-vector-stores-neptune
## Initiate Neptune Analytics vector wrapper¶
In [ ]:
Copied!
```
from llama_index.vector_stores.neptune import NeptuneAnalyticsVectorStore

graph_identifier = ""
embed_dim = 1536

neptune_vector_store = NeptuneAnalyticsVectorStore(
    graph_identifier=graph_identifier, embedding_dimension=1536
)

```

from llama_index.vector_stores.neptune import NeptuneAnalyticsVectorStore graph_identifier = "" embed_dim = 1536 neptune_vector_store = NeptuneAnalyticsVectorStore( graph_identifier=graph_identifier, embedding_dimension=1536 )
## Load documents, build the VectorStoreIndex¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from IPython.display import Markdown, display

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from IPython.display import Markdown, display
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
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
from llama_index.core import StorageContext

storage_context = StorageContext.from_defaults(
    vector_store=neptune_vector_store
)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

from llama_index.core import StorageContext storage_context = StorageContext.from_defaults( vector_store=neptune_vector_store ) index = VectorStoreIndex.from_documents( documents, storage_context=storage_context )
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What happened at interleaf?")
display(Markdown(f"<b>{response}</b>"))

```

query_engine = index.as_query_engine() response = query_engine.query("What happened at interleaf?") display(Markdown(f"**{response}** "))
