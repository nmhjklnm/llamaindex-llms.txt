![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Hologres¶
> Hologres is a one-stop real-time data warehouse, which can support high performance OLAP analysis and high QPS online services.
To run this notebook you need a Hologres instance running in the cloud. You can get one following this link.
After creating the instance, you should be able to figure out following configurations with Hologres console
In [ ]:
Copied!
```
test_hologres_config = {
    "host": "<host>",
    "port": 80,
    "user": "<user>",
    "password": "<password>",
    "database": "<database>",
    "table_name": "<table_name>",
}

```

test_hologres_config = { "host": "", "port": 80, "user": "", "password": "", "database": "", "table_name": "", }
By the way, you need to ensure you have `llama-index` installed:
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-hologres

```

%pip install llama-index-vector-stores-hologres
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
### Import needed package dependencies:¶
In [ ]:
Copied!
```
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
)
from llama_index.vector_stores.hologres import HologresVectorStore

```

from llama_index.core import ( VectorStoreIndex, SimpleDirectoryReader, StorageContext, ) from llama_index.vector_stores.hologres import HologresVectorStore
### Load some example data:¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!curl 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -o 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !curl 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -o 'data/paul_graham/paul_graham_essay.txt'
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 75042  100 75042    0     0  31985      0  0:00:02  0:00:02 --:--:-- 31987

```

### Read the data:¶
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
print(f"Total documents: {len(documents)}")
print(f"First document, id: {documents[0].doc_id}")
print(f"First document, hash: {documents[0].hash}")
print(
    "First document, text"
    f" ({len(documents[0].text)} characters):\n{'='*20}\n{documents[0].text[:360]} ..."
)

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data() print(f"Total documents: {len(documents)}") print(f"First document, id: {documents[0].doc_id}") print(f"First document, hash: {documents[0].hash}") print( "First document, text" f" ({len(documents[0].text)} characters):\n{'='*20}\n{documents[0].text[:360]} ..." )
```
Total documents: 1
First document, id: 824dafc0-0aa1-4c80-b99c-33895cfc606a
First document, hash: 8430b3bdb65ee0a7853463b71e7e1e20beee3a3ce15ef3ec714919f8653b2eb9
First document, text (75014 characters):
====================


What I Worked On

February 2021

Before college the two main things I worked on, outside of school, were writing and programming. I didn't write essays. I wrote what beginning writers were supposed to write then, and probably still are: short stories. My stories were awful. They had hardly any plot, just characters with strong feelings, which I imagined ma ...

```

### Create the AnalyticDB Vector Store object:¶
In [ ]:
Copied!
```
hologres_store = HologresVectorStore.from_param(
    host=test_hologres_config["host"],
    port=test_hologres_config["port"],
    user=test_hologres_config["user"],
    password=test_hologres_config["password"],
    database=test_hologres_config["database"],
    table_name=test_hologres_config["table_name"],
    embedding_dimension=1536,
    pre_delete_table=True,
)

```

hologres_store = HologresVectorStore.from_param( host=test_hologres_config["host"], port=test_hologres_config["port"], user=test_hologres_config["user"], password=test_hologres_config["password"], database=test_hologres_config["database"], table_name=test_hologres_config["table_name"], embedding_dimension=1536, pre_delete_table=True, )
### Build the Index from the Documents:¶
In [ ]:
Copied!
```
storage_context = StorageContext.from_defaults(vector_store=hologres_store)

index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

storage_context = StorageContext.from_defaults(vector_store=hologres_store) index = VectorStoreIndex.from_documents( documents, storage_context=storage_context )
### Query using the index:¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("Why did the author choose to work on AI?")

print(response.response)

```

query_engine = index.as_query_engine() response = query_engine.query("Why did the author choose to work on AI?") print(response.response)
```
The author was inspired to work on AI due to the influence of a science fiction novel, "The Moon is a Harsh Mistress," which featured an intelligent computer named Mike, and a PBS documentary showcasing Terry Winograd's use of the SHRDLU program. These experiences led the author to believe that creating intelligent machines was an imminent reality and sparked their interest in the field of AI.

```

