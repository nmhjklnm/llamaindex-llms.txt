![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# MongoDB Atlas Vector Store¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-mongodb

```

%pip install llama-index-vector-stores-mongodb
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# Provide URI to constructor, or use environment variable
import pymongo
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.core import SimpleDirectoryReader

```

# Provide URI to constructor, or use environment variable import pymongo from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch from llama_index.core import VectorStoreIndex from llama_index.core import StorageContext from llama_index.core import SimpleDirectoryReader
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
In [ ]:
Copied!
```
# mongo_uri = os.environ["MONGO_URI"]
mongo_uri = (
    "mongodb+srv://<username>:<password>@<host>?retryWrites=true&w=majority"
)
mongodb_client = pymongo.MongoClient(mongo_uri)
store = MongoDBAtlasVectorSearch(mongodb_client)
store.create_vector_search_index(
    dimensions=1536, path="embedding", similarity="cosine"
)
storage_context = StorageContext.from_defaults(vector_store=store)
uber_docs = SimpleDirectoryReader(
    input_files=["./data/10k/uber_2021.pdf"]
).load_data()
index = VectorStoreIndex.from_documents(
    uber_docs, storage_context=storage_context
)

```

# mongo_uri = os.environ["MONGO_URI"] mongo_uri = ( "mongodb+srv://:@?retryWrites=true&w=majority" ) mongodb_client = pymongo.MongoClient(mongo_uri) store = MongoDBAtlasVectorSearch(mongodb_client) store.create_vector_search_index( dimensions=1536, path="embedding", similarity="cosine" ) storage_context = StorageContext.from_defaults(vector_store=store) uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data() index = VectorStoreIndex.from_documents( uber_docs, storage_context=storage_context )
In [ ]:
Copied!
```
response = index.as_query_engine().query("What was Uber's revenue?")
display(Markdown(f"<b>{response}</b>"))

```

response = index.as_query_engine().query("What was Uber's revenue?") display(Markdown(f"**{response}** "))
**Uber's revenue for 2021 was $17,455 million.**
In [ ]:
Copied!
```
from llama_index.core import Response

# Initial size

print(store._collection.count_documents({}))
# Get a ref_doc_id
typed_response = (
    response if isinstance(response, Response) else response.get_response()
)
ref_doc_id = typed_response.source_nodes[0].node.ref_doc_id
print(store._collection.count_documents({"metadata.ref_doc_id": ref_doc_id}))
# Test store delete
if ref_doc_id:
    store.delete(ref_doc_id)
    print(store._collection.count_documents({}))

```

from llama_index.core import Response # Initial size print(store._collection.count_documents({})) # Get a ref_doc_id typed_response = ( response if isinstance(response, Response) else response.get_response() ) ref_doc_id = typed_response.source_nodes[0].node.ref_doc_id print(store._collection.count_documents({"metadata.ref_doc_id": ref_doc_id})) # Test store delete if ref_doc_id: store.delete(ref_doc_id) print(store._collection.count_documents({}))


Note: For MongoDB Atlas, you have to create an Atlas Search Index.
MongoDB Docs | Create an Atlas Vector Search Index
