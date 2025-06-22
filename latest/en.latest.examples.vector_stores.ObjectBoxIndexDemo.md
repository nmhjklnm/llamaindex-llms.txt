# ObjectBox VectorStore Demo¶
This notebook will demonstrate the use of ObjectBox as an efficient, on-device vector-store with LlamaIndex. We will consider a simple RAG use-case where given a document, the user can ask questions and get relevant answers from a LLM in natural language. The RAG pipeline will be configured along the following verticals:
  * A builtin `SimpleDirectoryReader` reader from LlamaIndex
  * A builtin `SentenceSplitter` node-parser from LlamaIndex
  * Models from HuggingFace as embedding providers
  * ObjectBox as NoSQL and vector datastore
  * Google's Gemini as a remote LLM service


## 1) Installing dependencies¶
We install integrations for HuggingFace and Gemini to use along with LlamaIndex
In [ ]:
Copied!
```
!pip install llama_index_vector_stores_objectbox --quiet
!pip install llama-index --quiet
!pip install llama-index-embeddings-huggingface --quiet
!pip install llama-index-llms-gemini --quiet

```

!pip install llama_index_vector_stores_objectbox --quiet !pip install llama-index --quiet !pip install llama-index-embeddings-huggingface --quiet !pip install llama-index-llms-gemini --quiet
```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 0.0/1.6 MB ? eta -:--:--
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╺━━ 1.5/1.6 MB 40.2 MB/s eta 0:00:01
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.6/1.6 MB 25.4 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.0/4.0 MB 44.0 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.5/1.5 MB 38.9 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.1/1.1 MB 37.5 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 76.4/76.4 kB 5.2 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 77.9/77.9 kB 4.9 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 49.3/49.3 kB 3.1 MB/s eta 0:00:00
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 58.3/58.3 kB 3.4 MB/s eta 0:00:00

```

## 2) Downloading the documents¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
## 3) Setup a LLM for RAG (Gemini)¶
We use Google Gemini's cloud-based API as a LLM. You can get an API-key from the console.
In [ ]:
Copied!
```
from llama_index.llms.gemini import Gemini
import getpass

gemini_key_api = getpass.getpass("Gemini API Key: ")
gemini_llm = Gemini(api_key=gemini_key_api)

```

from llama_index.llms.gemini import Gemini import getpass gemini_key_api = getpass.getpass("Gemini API Key: ") gemini_llm = Gemini(api_key=gemini_key_api)
## 4) Setup an embedding model for RAG (HuggingFace `bge-small-en-v1.5`)¶
HuggingFace hosts a variety of embedding models, which could be observed from the MTEB Leaderboard.
In [ ]:
Copied!
```
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

hf_embedding = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
embedding_dim = 384

```

from llama_index.embeddings.huggingface import HuggingFaceEmbedding hf_embedding = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5") embedding_dim = 384
## 5) Prepare documents and nodes¶
In a RAG pipeline, the first step is to read the given documents. We use the `SimpleDirectoryReader` that selects the best file reader by checking the file extension from the directory.
Next, we produce chunks (text subsequences) from the contents read by the `SimpleDirectoryReader` from the documents. A `SentenceSplitter` is a text-splitter that preserves sentence boundaries while splitting the text into chunks of size `chunk_size`.
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter

reader = SimpleDirectoryReader("./data/paul_graham")
documents = reader.load_data()

node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
nodes = node_parser.get_nodes_from_documents(documents)

```

from llama_index.core import SimpleDirectoryReader from llama_index.core.node_parser import SentenceSplitter reader = SimpleDirectoryReader("./data/paul_graham") documents = reader.load_data() node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20) nodes = node_parser.get_nodes_from_documents(documents)
## 6) Configure `ObjectBoxVectorStore`¶
The `ObjectBoxVectorStore` can be initialized with several options:
  * `embedding_dim` (required): The dimensions of the embeddings that the vector DB will hold
  * `distance_type`: Choose from `COSINE`, `DOT_PRODUCT`, `DOT_PRODUCT_NON_NORMALIZED` and `EUCLIDEAN`
  * `db_directory`: The path of the directory where the `.mdb` ObjectBox database file should be created
  * `clear_db`: Deletes the existing database file if it exists on `db_directory`
  * `do_log`: Enables logging from the ObjectBox integration


In [ ]:
Copied!
```
from llama_index.vector_stores.objectbox import ObjectBoxVectorStore
from llama_index.core import StorageContext, VectorStoreIndex, Settings
from objectbox import VectorDistanceType

vector_store = ObjectBoxVectorStore(
    embedding_dim,
    distance_type=VectorDistanceType.COSINE,
    db_directory="obx_data",
    clear_db=False,
    do_log=True,
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)

Settings.llm = gemini_llm
Settings.embed_model = hf_embedding

index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)

```

from llama_index.vector_stores.objectbox import ObjectBoxVectorStore from llama_index.core import StorageContext, VectorStoreIndex, Settings from objectbox import VectorDistanceType vector_store = ObjectBoxVectorStore( embedding_dim, distance_type=VectorDistanceType.COSINE, db_directory="obx_data", clear_db=False, do_log=True, ) storage_context = StorageContext.from_defaults(vector_store=vector_store) Settings.llm = gemini_llm Settings.embed_model = hf_embedding index = VectorStoreIndex(nodes=nodes, storage_context=storage_context)
## 7) Chat with the document¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("Who is Paul Graham?")
print(response)

```

query_engine = index.as_query_engine() response = query_engine.query("Who is Paul Graham?") print(response)
## Optional: Configuring `ObjectBoxVectorStore` as a retriever¶
A LlamaIndex retriever is responsible for fetching similar chunks from a vector DB given a query.
In [ ]:
Copied!
```
retriever = index.as_retriever()
response = retriever.retrieve("What did the author do growing up?")

for node in response:
    print("Retrieved chunk text:\n", node.node.get_text())
    print("Retrieved chunk metadata:\n", node.node.get_metadata_str())
    print("\n\n\n")

```

retriever = index.as_retriever() response = retriever.retrieve("What did the author do growing up?") for node in response: print("Retrieved chunk text:\n", node.node.get_text()) print("Retrieved chunk metadata:\n", node.node.get_metadata_str()) print("\n\n\n")
## Optional: Removing chunks associated with a single query using `delete_nodes`¶
We can use the `ObjectBoxVectorStore.delete_nodes` method to remove chunks (nodes) from the vector DB providing a list containing node IDs as an argument.
In [ ]:
Copied!
```
response = retriever.retrieve("What did the author do growing up?")

node_ids = []
for node in response:
    node_ids.append(node.node_id)
print(f"Nodes to be removed: {node_ids}")

print(f"No. of vectors before deletion: {vector_store.count()}")
vector_store.delete_nodes(node_ids)
print(f"No. of vectors after deletion: {vector_store.count()}")

```

response = retriever.retrieve("What did the author do growing up?") node_ids = [] for node in response: node_ids.append(node.node_id) print(f"Nodes to be removed: {node_ids}") print(f"No. of vectors before deletion: {vector_store.count()}") vector_store.delete_nodes(node_ids) print(f"No. of vectors after deletion: {vector_store.count()}")
## Optional: Removing a single document from the vector DB¶
The `ObjectBoxVectorStore.delete` method can be used to remove chunks (nodes) associated with a single document whose `id_` is provided as an argument.
In [ ]:
Copied!
```
document = documents[0]
print(f"Document to be deleted {document.id_}")

print(f"No. of vectors before deletion: {vector_store.count()}")
vector_store.delete(document.id_)
print(f"No. of vectors after document deletion: {vector_store.count()}")

```

document = documents[0] print(f"Document to be deleted {document.id_}") print(f"No. of vectors before deletion: {vector_store.count()}") vector_store.delete(document.id_) print(f"No. of vectors after document deletion: {vector_store.count()}")
