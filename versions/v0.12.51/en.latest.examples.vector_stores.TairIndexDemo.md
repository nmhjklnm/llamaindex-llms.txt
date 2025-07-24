![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Tair Vector Store¶
In this notebook we are going to show a quick demo of using the TairVectorStore.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-tair

```

%pip install llama-index-vector-stores-tair
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
import sys
import logging
import textwrap

import warnings

warnings.filterwarnings("ignore")

# stop huggingface warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Uncomment to see debug logs
# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import (
    GPTVectorStoreIndex,
    SimpleDirectoryReader,
    Document,
)
from llama_index.vector_stores.tair import TairVectorStore
from IPython.display import Markdown, display

```

import os import sys import logging import textwrap import warnings warnings.filterwarnings("ignore") # stop huggingface warnings os.environ["TOKENIZERS_PARALLELISM"] = "false" # Uncomment to see debug logs # logging.basicConfig(stream=sys.stdout, level=logging.INFO) # logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import ( GPTVectorStoreIndex, SimpleDirectoryReader, Document, ) from llama_index.vector_stores.tair import TairVectorStore from IPython.display import Markdown, display
### Setup OpenAI¶
Lets first begin by adding the openai api key. This will allow us to access openai for embeddings and to use chatgpt.
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-<your key here>"

```

import os os.environ["OPENAI_API_KEY"] = "sk-"
### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
### Read in a dataset¶
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham").load_data()
print(
    "Document ID:",
    documents[0].doc_id,
    "Document Hash:",
    documents[0].doc_hash,
)

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham").load_data() print( "Document ID:", documents[0].doc_id, "Document Hash:", documents[0].doc_hash, )
### Build index from documents¶
Let's build a vector index with `GPTVectorStoreIndex`, using `TairVectorStore` as its backend. Replace `tair_url` with the actual url of your Tair instance.
In [ ]:
Copied!
```
from llama_index.core import StorageContext

tair_url = "redis://{username}:{password}@r-bp****************.redis.rds.aliyuncs.com:{port}"

vector_store = TairVectorStore(
    tair_url=tair_url, index_name="pg_essays", overwrite=True
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = GPTVectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

from llama_index.core import StorageContext tair_url = "redis://{username}:{password}@r-bp****************.redis.rds.aliyuncs.com:{port}" vector_store = TairVectorStore( tair_url=tair_url, index_name="pg_essays", overwrite=True ) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = GPTVectorStoreIndex.from_documents( documents, storage_context=storage_context )
### Query the data¶
Now we can use the index as knowledge base and ask questions to it.
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What did the author learn?")
print(textwrap.fill(str(response), 100))

```

query_engine = index.as_query_engine() response = query_engine.query("What did the author learn?") print(textwrap.fill(str(response), 100))
In [ ]:
Copied!
```
response = query_engine.query("What was a hard moment for the author?")
print(textwrap.fill(str(response), 100))

```

response = query_engine.query("What was a hard moment for the author?") print(textwrap.fill(str(response), 100))
### Deleting documents¶
To delete a document from the index, use `delete` method.
In [ ]:
Copied!
```
document_id = documents[0].doc_id
document_id

```

document_id = documents[0].doc_id document_id
In [ ]:
Copied!
```
info = vector_store.client.tvs_get_index("pg_essays")
print("Number of documents", int(info["data_count"]))

```

info = vector_store.client.tvs_get_index("pg_essays") print("Number of documents", int(info["data_count"]))
In [ ]:
Copied!
```
vector_store.delete(document_id)

```

vector_store.delete(document_id)
In [ ]:
Copied!
```
info = vector_store.client.tvs_get_index("pg_essays")
print("Number of documents", int(info["data_count"]))

```

info = vector_store.client.tvs_get_index("pg_essays") print("Number of documents", int(info["data_count"]))
### Deleting index¶
Delete the entire index using `delete_index` method.
In [ ]:
Copied!
```
vector_store.delete_index()

```

vector_store.delete_index()
In [ ]:
Copied!
```
print("Check index existence:", vector_store.client._index_exists())

```

print("Check index existence:", vector_store.client._index_exists())
