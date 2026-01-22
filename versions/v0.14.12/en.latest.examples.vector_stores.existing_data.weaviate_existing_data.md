![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Guide: Using Vector Store Index with Existing Weaviate Vector Store¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-weaviate
%pip install llama-index-embeddings-openai

```

%pip install llama-index-vector-stores-weaviate %pip install llama-index-embeddings-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import weaviate

```

import weaviate
In [ ]:
Copied!
```
client = weaviate.Client("https://test-cluster-bbn8vqsn.weaviate.network")

```

client = weaviate.Client("https://test-cluster-bbn8vqsn.weaviate.network")
## Prepare Sample "Existing" Weaviate Vector Store¶
### Define schema¶
We create a schema for "Book" class, with 4 properties: title (str), author (str), content (str), and year (int)
In [ ]:
Copied!
```
try:
    client.schema.delete_class("Book")
except:
    pass

```

try: client.schema.delete_class("Book") except: pass
In [ ]:
Copied!
```
schema = {
    "classes": [
        {
            "class": "Book",
            "properties": [
                {"name": "title", "dataType": ["text"]},
                {"name": "author", "dataType": ["text"]},
                {"name": "content", "dataType": ["text"]},
                {"name": "year", "dataType": ["int"]},
            ],
        },
    ]
}

if not client.schema.contains(schema):
    client.schema.create(schema)

```

schema = { "classes": [ { "class": "Book", "properties": [ {"name": "title", "dataType": ["text"]}, {"name": "author", "dataType": ["text"]}, {"name": "content", "dataType": ["text"]}, {"name": "year", "dataType": ["int"]}, ], }, ] } if not client.schema.contains(schema): client.schema.create(schema)
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
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding()

```

from llama_index.embeddings.openai import OpenAIEmbedding embed_model = OpenAIEmbedding()
In [ ]:
Copied!
```
with client.batch as batch:
    for book in books:
        vector = embed_model.get_text_embedding(book["content"])
        batch.add_data_object(
            data_object=book, class_name="Book", vector=vector
        )

```

with client.batch as batch: for book in books: vector = embed_model.get_text_embedding(book["content"]) batch.add_data_object( data_object=book, class_name="Book", vector=vector )
## Query Against "Existing" Weaviate Vector Store¶
In [ ]:
Copied!
```
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.response.pprint_utils import pprint_source_node

```

from llama_index.vector_stores.weaviate import WeaviateVectorStore from llama_index.core import VectorStoreIndex from llama_index.core.response.pprint_utils import pprint_source_node
You must properly specify a "index_name" that matches the desired Weaviate class and select a class property as the "text" field.
In [ ]:
Copied!
```
vector_store = WeaviateVectorStore(
    weaviate_client=client, index_name="Book", text_key="content"
)

```

vector_store = WeaviateVectorStore( weaviate_client=client, index_name="Book", text_key="content" )
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
Document ID: cf927ce7-0672-4696-8aae-7e77b33b9659
Similarity: None
Text: author: Harper Lee title: To Kill a Mockingbird year: 1960  To
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
{'author': 'Harper Lee', 'title': 'To Kill a Mockingbird', 'year': 1960}
```

