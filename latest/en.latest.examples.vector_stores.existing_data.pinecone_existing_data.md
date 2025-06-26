![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Guide: Using Vector Store Index with Existing Pinecone Vector Store¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-vector-stores-pinecone

```

%pip install llama-index-embeddings-openai %pip install llama-index-vector-stores-pinecone
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
import pinecone

```

import os import pinecone
In [ ]:
Copied!
```
api_key = os.environ["PINECONE_API_KEY"]
pinecone.init(api_key=api_key, environment="eu-west1-gcp")

```

api_key = os.environ["PINECONE_API_KEY"] pinecone.init(api_key=api_key, environment="eu-west1-gcp")
## Prepare Sample "Existing" Pinecone Vector Store¶
### Create index¶
In [ ]:
Copied!
```
indexes = pinecone.list_indexes()
print(indexes)

```

indexes = pinecone.list_indexes() print(indexes)
```
['quickstart-index']

```

In [ ]:
Copied!
```
if "quickstart-index" not in indexes:
    # dimensions are for text-embedding-ada-002
    pinecone.create_index(
        "quickstart-index", dimension=1536, metric="euclidean", pod_type="p1"
    )

```

if "quickstart-index" not in indexes: # dimensions are for text-embedding-ada-002 pinecone.create_index( "quickstart-index", dimension=1536, metric="euclidean", pod_type="p1" )
In [ ]:
Copied!
```
pinecone_index = pinecone.Index("quickstart-index")

```

pinecone_index = pinecone.Index("quickstart-index")
In [ ]:
Copied!
```
pinecone_index.delete(deleteAll="true")

```

pinecone_index.delete(deleteAll="true")
Out[ ]:
```
{}
```

### Define sample data¶
We create 4 sample books
In [ ]:
Copied!
```
books = [
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "content": (
            "To Kill a Mockingbird is a novel by Harper Lee published in"
            " 1960..."
        ),
        "year": 1960,
    },
    {
        "title": "1984",
        "author": "George Orwell",
        "content": (
            "1984 is a dystopian novel by George Orwell published in 1949..."
        ),
        "year": 1949,
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "content": (
            "The Great Gatsby is a novel by F. Scott Fitzgerald published in"
            " 1925..."
        ),
        "year": 1925,
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "content": (
            "Pride and Prejudice is a novel by Jane Austen published in"
            " 1813..."
        ),
        "year": 1813,
    },
]

```

books = [ { "title": "To Kill a Mockingbird", "author": "Harper Lee", "content": ( "To Kill a Mockingbird is a novel by Harper Lee published in" " 1960..." ), "year": 1960, }, { "title": "1984", "author": "George Orwell", "content": ( "1984 is a dystopian novel by George Orwell published in 1949..." ), "year": 1949, }, { "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "content": ( "The Great Gatsby is a novel by F. Scott Fitzgerald published in" " 1925..." ), "year": 1925, }, { "title": "Pride and Prejudice", "author": "Jane Austen", "content": ( "Pride and Prejudice is a novel by Jane Austen published in" " 1813..." ), "year": 1813, }, ]
### Add data¶
We add the sample books to our Weaviate "Book" class (with embedding of content field
In [ ]:
Copied!
```
import uuid
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding()

```

import uuid from llama_index.embeddings.openai import OpenAIEmbedding embed_model = OpenAIEmbedding()
In [ ]:
Copied!
```
entries = []
for book in books:
    vector = embed_model.get_text_embedding(book["content"])
    entries.append(
        {"id": str(uuid.uuid4()), "values": vector, "metadata": book}
    )
pinecone_index.upsert(entries)

```

entries = [] for book in books: vector = embed_model.get_text_embedding(book["content"]) entries.append( {"id": str(uuid.uuid4()), "values": vector, "metadata": book} ) pinecone_index.upsert(entries)
Out[ ]:
```
{'upserted_count': 4}
```

## Query Against "Existing" Pinecone Vector Store¶
In [ ]:
Copied!
```
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.response.pprint_utils import pprint_source_node

```

from llama_index.vector_stores.pinecone import PineconeVectorStore from llama_index.core import VectorStoreIndex from llama_index.core.response.pprint_utils import pprint_source_node
You must properly select a class property as the "text" field.
In [ ]:
Copied!
```
vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index, text_key="content"
)

```

vector_store = PineconeVectorStore( pinecone_index=pinecone_index, text_key="content" )
In [ ]:
Copied!
```
retriever = VectorStoreIndex.from_vector_store(vector_store).as_retriever(
    similarity_top_k=1
)

```

retriever = VectorStoreIndex.from_vector_store(vector_store).as_retriever( similarity_top_k=1 )
In [ ]:
Copied!
```
nodes = retriever.retrieve("What is that book about a bird again?")

```

nodes = retriever.retrieve("What is that book about a bird again?")
Let's inspect the retrieved node. We can see that the book data is loaded as LlamaIndex `Node` objects, with the "content" field as the main text.
In [ ]:
Copied!
```
pprint_source_node(nodes[0])

```

pprint_source_node(nodes[0])
```
Document ID: 07e47f1d-cb90-431b-89c7-35462afcda28
Similarity: 0.797243237
Text: author: Harper Lee title: To Kill a Mockingbird year: 1960.0  To
Kill a Mockingbird is a novel by Harper Lee published in 1960......

```

The remaining fields should be loaded as metadata (in `metadata`)
In [ ]:
Copied!
```
nodes[0].node.metadata

```

nodes[0].node.metadata
Out[ ]:
```
{'author': 'Harper Lee', 'title': 'To Kill a Mockingbird', 'year': 1960.0}
```

