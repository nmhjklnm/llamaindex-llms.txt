# Ingestion Pipeline + Document Management¶
Attaching a `docstore` to the ingestion pipeline will enable document management.
Using the `document.doc_id` or `node.ref_doc_id` as a grounding point, the ingestion pipeline will actively look for duplicate documents.
It works by
  * Storing a map of `doc_id` -> `document_hash`
  * If a duplicate `doc_id` is detected, and the hash has changed, the document will be re-processed
  * If the hash has not changed, the document will be skipped in the pipeline


If we do not attach a vector store, we can only check for and remove duplicate inputs.
If a vector store is attached, we can also handle upserts! We have another guide for upserts and vector stores.
## Create Seed Data¶
In [ ]:
Copied!
```
%pip install llama-index-storage-docstore-redis
%pip install llama-index-storage-docstore-mongodb
%pip install llama-index-embeddings-huggingface

```

%pip install llama-index-storage-docstore-redis %pip install llama-index-storage-docstore-mongodb %pip install llama-index-embeddings-huggingface
In [ ]:
Copied!
```
# Make some test data
!mkdir -p data
!echo "This is a test file: one!" > data/test1.txt
!echo "This is a test file: two!" > data/test2.txt

```

# Make some test data !mkdir -p data !echo "This is a test file: one!" > data/test1.txt !echo "This is a test file: two!" > data/test2.txt
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

# load documents with deterministic IDs
documents = SimpleDirectoryReader("./data", filename_as_id=True).load_data()

```

from llama_index.core import SimpleDirectoryReader # load documents with deterministic IDs documents = SimpleDirectoryReader("./data", filename_as_id=True).load_data()
```
/home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages/deeplake/util/check_latest_version.py:32: UserWarning: A newer version of deeplake (3.8.9) is available. It's recommended that you update to the latest version using `pip install -U deeplake`.
  warnings.warn(

```

## Create Pipeline with Document Store¶
In [ ]:
Copied!
```
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.storage.docstore.redis import RedisDocumentStore
from llama_index.storage.docstore.mongodb import MongoDocumentStore
from llama_index.core.node_parser import SentenceSplitter


pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    ],
    docstore=SimpleDocumentStore(),
)

```

from llama_index.embeddings.huggingface import HuggingFaceEmbedding from llama_index.core.ingestion import IngestionPipeline from llama_index.core.storage.docstore import SimpleDocumentStore from llama_index.storage.docstore.redis import RedisDocumentStore from llama_index.storage.docstore.mongodb import MongoDocumentStore from llama_index.core.node_parser import SentenceSplitter pipeline = IngestionPipeline( transformations=[ SentenceSplitter(), HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"), ], docstore=SimpleDocumentStore(), )
In [ ]:
Copied!
```
nodes = pipeline.run(documents=documents)

```

nodes = pipeline.run(documents=documents)
```
Docstore strategy set to upserts, but no vector store. Switching to duplicates_only strategy.

```

In [ ]:
Copied!
```
print(f"Ingested {len(nodes)} Nodes")

```

print(f"Ingested {len(nodes)} Nodes")
```
Ingested 2 Nodes

```

### [Optional] Save/Load Pipeline¶
Saving the pipeline will save both the internal cache and docstore.
**NOTE:** If you were using remote caches/docstores, this step is not needed
In [ ]:
Copied!
```
pipeline.persist("./pipeline_storage")

```

pipeline.persist("./pipeline_storage")
In [ ]:
Copied!
```
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(),
        HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    ]
)

# restore the pipeline
pipeline.load("./pipeline_storage")

```

pipeline = IngestionPipeline( transformations=[ SentenceSplitter(), HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"), ] ) # restore the pipeline pipeline.load("./pipeline_storage")
## Test the Document Management¶
Here, we can create a new document, as well as edit an existing document, to test the document management.
Both the new document and edited document will be ingested, while the unchanged document will be skipped
In [ ]:
Copied!
```
!echo "This is a test file: three!" > data/test3.txt
!echo "This is a NEW test file: one!" > data/test1.txt

```

!echo "This is a test file: three!" > data/test3.txt !echo "This is a NEW test file: one!" > data/test1.txt
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("./data", filename_as_id=True).load_data()

```

documents = SimpleDirectoryReader("./data", filename_as_id=True).load_data()
In [ ]:
Copied!
```
nodes = pipeline.run(documents=documents)

```

nodes = pipeline.run(documents=documents)
```
Docstore strategy set to upserts, but no vector store. Switching to duplicates_only strategy.

```

In [ ]:
Copied!
```
print(f"Ingested {len(nodes)} Nodes")

```

print(f"Ingested {len(nodes)} Nodes")
```
Ingested 2 Nodes

```

Lets confirm which nodes were ingested:
In [ ]:
Copied!
```
for node in nodes:
    print(f"Node: {node.text}")

```

for node in nodes: print(f"Node: {node.text}")
```
Node: This is a NEW test file: one!
Node: This is a test file: three!

```

We can also verify the docstore has only three documents tracked
In [ ]:
Copied!
```
print(len(pipeline.docstore.docs))

```

print(len(pipeline.docstore.docs))


