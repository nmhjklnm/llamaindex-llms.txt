![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Supabase Vector Store¶
In this notebook we are going to show how to use Vecs to perform vector searches in LlamaIndex.  
See this guide for instructions on hosting a database on Supabase
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-supabase

```

%pip install llama-index-vector-stores-supabase
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import logging
import sys

# Uncomment to see debug logs
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import SimpleDirectoryReader, Document, StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.supabase import SupabaseVectorStore
import textwrap

```

import logging import sys # Uncomment to see debug logs # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG) # logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import SimpleDirectoryReader, Document, StorageContext from llama_index.core import VectorStoreIndex from llama_index.vector_stores.supabase import SupabaseVectorStore import textwrap
### Setup OpenAI¶
The first step is to configure the OpenAI key. It will be used to created embeddings for the documents loaded into the index
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "[your_openai_api_key]"

```

import os os.environ["OPENAI_API_KEY"] = "[your_openai_api_key]"
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
### Loading documents¶
Load the documents stored in the `./data/paul_graham/` using the SimpleDirectoryReader
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
print(
    "Document ID:",
    documents[0].doc_id,
    "Document Hash:",
    documents[0].doc_hash,
)

```

documents = SimpleDirectoryReader("./data/paul_graham/").load_data() print( "Document ID:", documents[0].doc_id, "Document Hash:", documents[0].doc_hash, )
```
Document ID: fb056993-ee9e-4463-80b4-32cf9509d1d8 Document Hash: 77ae91ab542f3abb308c4d7c77c9bc4c9ad0ccd63144802b7cbe7e1bb3a4094e

```

### Create an index backed by Supabase's vector store.¶
This will work with all Postgres providers that support pgvector. If the collection does not exist, we will attempt to create a new collection
> Note: you need to pass in the embedding dimension if not using OpenAI's text-embedding-ada-002, e.g. `vector_store = SupabaseVectorStore(..., dimension=...)`
In [ ]:
Copied!
```
vector_store = SupabaseVectorStore(
    postgres_connection_string=(
        "postgresql://<user>:<password>@<host>:<port>/<db_name>"
    ),
    collection_name="base_demo",
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

vector_store = SupabaseVectorStore( postgres_connection_string=( "postgresql://:@:/" ), collection_name="base_demo", ) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex.from_documents( documents, storage_context=storage_context )
### Query the index¶
We can now ask questions using our index.
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("Who is the author?")

```

query_engine = index.as_query_engine() response = query_engine.query("Who is the author?")
```
/Users/suo/miniconda3/envs/llama/lib/python3.9/site-packages/vecs/collection.py:182: UserWarning: Query does not have a covering index for cosine_distance. See Collection.create_index
  warnings.warn(

```

In [ ]:
Copied!
```
print(textwrap.fill(str(response), 100))

```

print(textwrap.fill(str(response), 100))
```
 The author of this text is Paul Graham.

```

In [ ]:
Copied!
```
response = query_engine.query("What did the author do growing up?")

```

response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
print(textwrap.fill(str(response), 100))

```

print(textwrap.fill(str(response), 100))
```
 The author grew up writing essays, learning Italian, exploring Florence, painting people, working
with computers, attending RISD, living in a rent-stabilized apartment, building an online store
builder, editing Lisp expressions, publishing essays online, writing essays, painting still life,
working on spam filters, cooking for groups, and buying a building in Cambridge.

```

## Using metadata filters¶
In [ ]:
Copied!
```
from llama_index.core.schema import TextNode

nodes = [
    TextNode(
        **{
            "text": "The Shawshank Redemption",
            "metadata": {
                "author": "Stephen King",
                "theme": "Friendship",
            },
        }
    ),
    TextNode(
        **{
            "text": "The Godfather",
            "metadata": {
                "director": "Francis Ford Coppola",
                "theme": "Mafia",
            },
        }
    ),
    TextNode(
        **{
            "text": "Inception",
            "metadata": {
                "director": "Christopher Nolan",
            },
        }
    ),
]

```

from llama_index.core.schema import TextNode nodes = [ TextNode( **{ "text": "The Shawshank Redemption", "metadata": { "author": "Stephen King", "theme": "Friendship", }, } ), TextNode( **{ "text": "The Godfather", "metadata": { "director": "Francis Ford Coppola", "theme": "Mafia", }, } ), TextNode( **{ "text": "Inception", "metadata": { "director": "Christopher Nolan", }, } ), ]
In [ ]:
Copied!
```
vector_store = SupabaseVectorStore(
    postgres_connection_string=(
        "postgresql://<user>:<password>@<host>:<port>/<db_name>"
    ),
    collection_name="metadata_filters_demo",
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex(nodes, storage_context=storage_context)

```

vector_store = SupabaseVectorStore( postgres_connection_string=( "postgresql://:@:/" ), collection_name="metadata_filters_demo", ) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex(nodes, storage_context=storage_context)
Define metadata filters
In [ ]:
Copied!
```
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters

filters = MetadataFilters(
    filters=[ExactMatchFilter(key="theme", value="Mafia")]
)

```

from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters filters = MetadataFilters( filters=[ExactMatchFilter(key="theme", value="Mafia")] )
Retrieve from vector store with filters
In [ ]:
Copied!
```
retriever = index.as_retriever(filters=filters)
retriever.retrieve("What is inception about?")

```

retriever = index.as_retriever(filters=filters) retriever.retrieve("What is inception about?")
Out[ ]:
```
[NodeWithScore(node=Node(text='The Godfather', doc_id='f837ed85-aacb-4552-b88a-7c114a5be15d', embedding=None, doc_hash='f8ee912e238a39fe2e620fb232fa27ade1e7f7c819b6d5b9cb26f3dddc75b6c0', extra_info={'theme': 'Mafia', 'director': 'Francis Ford Coppola'}, node_info={'_node_type': '1'}, relationships={}), score=0.20671339734643313)]
```

