# AWSDocDBDemo
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-vector-stores-awsdocdb

```

%pip install llama-index %pip install llama-index-vector-stores-awsdocdb
In [ ]:
Copied!
```
import pymongo
from llama_index.vector_stores.awsdocdb import AWSDocDbVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext
from llama_index.core import SimpleDirectoryReader
import os

```

import pymongo from llama_index.vector_stores.awsdocdb import AWSDocDbVectorStore from llama_index.core import VectorStoreIndex from llama_index.core import StorageContext from llama_index.core import SimpleDirectoryReader import os
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
mongo_uri = os.environ["MONGO_URI"]
mongodb_client = pymongo.MongoClient(mongo_uri)
store = AWSDocDbVectorStore(mongodb_client)
storage_context = StorageContext.from_defaults(vector_store=store)
uber_docs = SimpleDirectoryReader(
    input_files=["./data/10k/uber_2021.pdf"]
).load_data()
index = VectorStoreIndex.from_documents(
    uber_docs, storage_context=storage_context
)

```

mongo_uri = os.environ["MONGO_URI"] mongodb_client = pymongo.MongoClient(mongo_uri) store = AWSDocDbVectorStore(mongodb_client) storage_context = StorageContext.from_defaults(vector_store=store) uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data() index = VectorStoreIndex.from_documents( uber_docs, storage_context=storage_context )
In [ ]:
Copied!
```
response = index.as_query_engine().query("What was Uber's revenue?")
display(f"{response}")

```

response = index.as_query_engine().query("What was Uber's revenue?") display(f"{response}")
In [ ]:
Copied!
```
from llama_index.core import Response

print(store._collection.count_documents({}))
typed_response = (
    response if isinstance(response, Response) else response.get_response()
)
ref_doc_id = typed_response.source_nodes[0].node.ref_doc_id
print(store._collection.count_documents({"metadata.ref_doc_id": ref_doc_id}))

```

from llama_index.core import Response print(store._collection.count_documents({})) typed_response = ( response if isinstance(response, Response) else response.get_response() ) ref_doc_id = typed_response.source_nodes[0].node.ref_doc_id print(store._collection.count_documents({"metadata.ref_doc_id": ref_doc_id}))
In [ ]:
Copied!
```
# Test delete
if ref_doc_id:
    store.delete(ref_doc_id)
    print(store._collection.count_documents({}))

```

# Test delete if ref_doc_id: store.delete(ref_doc_id) print(store._collection.count_documents({}))
