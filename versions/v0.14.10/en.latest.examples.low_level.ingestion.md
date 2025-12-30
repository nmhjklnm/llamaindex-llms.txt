![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Building Data Ingestion from Scratch¶
In this tutorial, we show you how to build a data ingestion pipeline into a vector database.
We use Pinecone as the vector database.
We will show how to do the following:
  1. How to load in documents.
  2. How to use a text splitter to split documents.
  3. How to **manually** construct nodes from each text chunk.
  4. [Optional] Add metadata to each Node.
  5. How to generate embeddings for each text chunk.
  6. How to insert into a vector database.


## Pinecone¶
You will need a pinecone.io api key for this tutorial. You can sign up for free to get a Starter account.
If you create a Starter account, you can name your application anything you like.
Once you have an account, navigate to 'API Keys' in the Pinecone console. You can use the default key or create a new one for this tutorial.
Save your api key and its environment (`gcp_starter` for free accounts). You will need them below.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-vector-stores-pinecone
%pip install llama-index-llms-openai

```

%pip install llama-index-embeddings-openai %pip install llama-index-vector-stores-pinecone %pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
## OpenAI¶
You will need an OpenAI api key for this tutorial. Login to your platform.openai.com account, click on your profile picture in the upper right corner, and choose 'API Keys' from the menu. Create an API key for this tutorial and save it. You will need it below.
## Environment¶
First we add our dependencies.
In [ ]:
Copied!
```
!pip -q install python-dotenv pinecone-client llama-index pymupdf

```

!pip -q install python-dotenv pinecone-client llama-index pymupdf
#### Set Environment Variables¶
We create a file for our environment variables. Do not commit this file or share it!
Note: Google Colabs will let you create but not open a .env
In [ ]:
Copied!
```
dotenv_path = (
    "env"  # Google Colabs will not let you open a .env, but you can set
)
with open(dotenv_path, "w") as f:
    f.write('PINECONE_API_KEY="<your api key>"\n')
    f.write('OPENAI_API_KEY="<your api key>"\n')

```

dotenv_path = ( "env" # Google Colabs will not let you open a .env, but you can set ) with open(dotenv_path, "w") as f: f.write('PINECONE_API_KEY=""\n') f.write('OPENAI_API_KEY=""\n')
Set your OpenAI api key, and Pinecone api key and environment in the file we created.
In [ ]:
Copied!
```
import os
from dotenv import load_dotenv

```

import os from dotenv import load_dotenv
In [ ]:
Copied!
```
load_dotenv(dotenv_path=dotenv_path)

```

load_dotenv(dotenv_path=dotenv_path)
## Setup¶
We build an empty Pinecone Index, and define the necessary LlamaIndex wrappers/abstractions so that we can start loading data into Pinecone.
Note: Do not save your API keys in the code or add pinecone_env to your repo!
In [ ]:
Copied!
```
from pinecone import Pinecone, Index, ServerlessSpec

```

from pinecone import Pinecone, Index, ServerlessSpec
In [ ]:
Copied!
```
api_key = os.environ["PINECONE_API_KEY"]
pc = Pinecone(api_key=api_key)

```

api_key = os.environ["PINECONE_API_KEY"] pc = Pinecone(api_key=api_key)
In [ ]:
Copied!
```
index_name = "llamaindex-rag-fs"

```

index_name = "llamaindex-rag-fs"
In [ ]:
Copied!
```
# [Optional] Delete the index before re-running the tutorial.
# pinecone.delete_index(index_name)

```

# [Optional] Delete the index before re-running the tutorial. # pinecone.delete_index(index_name)
In [ ]:
Copied!
```
# dimensions are for text-embedding-ada-002
if index_name not in pc.list_indexes().names():
    pc.create_index(
        index_name,
        dimension=1536,
        metric="euclidean",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

```

# dimensions are for text-embedding-ada-002 if index_name not in pc.list_indexes().names(): pc.create_index( index_name, dimension=1536, metric="euclidean", spec=ServerlessSpec(cloud="aws", region="us-east-1"), )
In [ ]:
Copied!
```
pinecone_index = pc.Index(index_name)

```

pinecone_index = pc.Index(index_name)
In [ ]:
Copied!
```
# [Optional] drop contents in index - will not work on free accounts
pinecone_index.delete(deleteAll=True)

```

# [Optional] drop contents in index - will not work on free accounts pinecone_index.delete(deleteAll=True)
#### Create PineconeVectorStore¶
Simple wrapper abstraction to use in LlamaIndex. Wrap in StorageContext so we can easily load in Nodes.
In [ ]:
Copied!
```
from llama_index.vector_stores.pinecone import PineconeVectorStore

```

from llama_index.vector_stores.pinecone import PineconeVectorStore
In [ ]:
Copied!
```
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

```

vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
## Build an Ingestion Pipeline from Scratch¶
We show how to build an ingestion pipeline as mentioned in the introduction.
Note that steps (2) and (3) can be handled via our `NodeParser` abstractions, which handle splitting and node creation.
For the purposes of this tutorial, we show you how to create these objects manually.
### 1. Load Data¶
In [ ]:
Copied!
```
!mkdir data
!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"

```

!mkdir data !wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"
```
--2023-10-13 01:45:14--  https://arxiv.org/pdf/2307.09288.pdf
Resolving arxiv.org (arxiv.org)... 128.84.21.199
Connecting to arxiv.org (arxiv.org)|128.84.21.199|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 13661300 (13M) [application/pdf]
Saving to: ‘data/llama2.pdf’

data/llama2.pdf     100%[===================>]  13.03M  7.59MB/s    in 1.7s    

2023-10-13 01:45:16 (7.59 MB/s) - ‘data/llama2.pdf’ saved [13661300/13661300]

```

In [ ]:
Copied!
```
import fitz

```

import fitz
In [ ]:
Copied!
```
file_path = "./data/llama2.pdf"
doc = fitz.open(file_path)

```

file_path = "./data/llama2.pdf" doc = fitz.open(file_path)
### 2. Use a Text Splitter to Split Documents¶
Here we import our `SentenceSplitter` to split document texts into smaller chunks, while preserving paragraphs/sentences as much as possible.
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

```

from llama_index.core.node_parser import SentenceSplitter
In [ ]:
Copied!
```
text_parser = SentenceSplitter(
    chunk_size=1024,
    # separator=" ",
)

```

text_parser = SentenceSplitter( chunk_size=1024, # separator=" ", )
In [ ]:
Copied!
```
text_chunks = []
# maintain relationship with source doc index, to help inject doc metadata in (3)
doc_idxs = []
for doc_idx, page in enumerate(doc):
    page_text = page.get_text("text")
    cur_text_chunks = text_parser.split_text(page_text)
    text_chunks.extend(cur_text_chunks)
    doc_idxs.extend([doc_idx] * len(cur_text_chunks))

```

text_chunks = [] # maintain relationship with source doc index, to help inject doc metadata in (3) doc_idxs = [] for doc_idx, page in enumerate(doc): page_text = page.get_text("text") cur_text_chunks = text_parser.split_text(page_text) text_chunks.extend(cur_text_chunks) doc_idxs.extend([doc_idx] * len(cur_text_chunks))
### 3. Manually Construct Nodes from Text Chunks¶
We convert each chunk into a `TextNode` object, a low-level data abstraction in LlamaIndex that stores content but also allows defining metadata + relationships with other Nodes.
We inject metadata from the document into each node.
This essentially replicates logic in our `SentenceSplitter`.
In [ ]:
Copied!
```
from llama_index.core.schema import TextNode

```

from llama_index.core.schema import TextNode
In [ ]:
Copied!
```
nodes = []
for idx, text_chunk in enumerate(text_chunks):
    node = TextNode(
        text=text_chunk,
    )
    src_doc_idx = doc_idxs[idx]
    src_page = doc[src_doc_idx]
    nodes.append(node)

```

nodes = [] for idx, text_chunk in enumerate(text_chunks): node = TextNode( text=text_chunk, ) src_doc_idx = doc_idxs[idx] src_page = doc[src_doc_idx] nodes.append(node)
In [ ]:
Copied!
```
print(nodes[0].metadata)

```

print(nodes[0].metadata)
In [ ]:
Copied!
```
# print a sample node
print(nodes[0].get_content(metadata_mode="all"))

```

# print a sample node print(nodes[0].get_content(metadata_mode="all"))
### [Optional] 4. Extract Metadata from each Node¶
We extract metadata from each Node using our Metadata extractors.
This will add more metadata to each Node.
In [ ]:
Copied!
```
from llama_index.core.extractors import (
    QuestionsAnsweredExtractor,
    TitleExtractor,
)
from llama_index.core.ingestion import IngestionPipeline
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo")

extractors = [
    TitleExtractor(nodes=5, llm=llm),
    QuestionsAnsweredExtractor(questions=3, llm=llm),
]

```

from llama_index.core.extractors import ( QuestionsAnsweredExtractor, TitleExtractor, ) from llama_index.core.ingestion import IngestionPipeline from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo") extractors = [ TitleExtractor(nodes=5, llm=llm), QuestionsAnsweredExtractor(questions=3, llm=llm), ]
In [ ]:
Copied!
```
pipeline = IngestionPipeline(
    transformations=extractors,
)
nodes = await pipeline.arun(nodes=nodes, in_place=False)

```

pipeline = IngestionPipeline( transformations=extractors, ) nodes = await pipeline.arun(nodes=nodes, in_place=False)
In [ ]:
Copied!
```
print(nodes[0].metadata)

```

print(nodes[0].metadata)
### 5. Generate Embeddings for each Node¶
Generate document embeddings for each Node using our OpenAI embedding model (`text-embedding-ada-002`).
Store these on the `embedding` property on each Node.
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
for node in nodes:
    node_embedding = embed_model.get_text_embedding(
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding

```

for node in nodes: node_embedding = embed_model.get_text_embedding( node.get_content(metadata_mode="all") ) node.embedding = node_embedding
### 6. Load Nodes into a Vector Store¶
We now insert these nodes into our `PineconeVectorStore`.
**NOTE** : We skip the VectorStoreIndex abstraction, which is a higher-level abstraction that handles ingestion as well. We use `VectorStoreIndex` in the next section to fast-track retrieval/querying.
In [ ]:
Copied!
```
vector_store.add(nodes)

```

vector_store.add(nodes)
## Retrieve and Query from the Vector Store¶
Now that our ingestion is complete, we can retrieve/query this vector store.
**NOTE** : We can use our high-level `VectorStoreIndex` abstraction here. See the next section to see how to define retrieval at a lower-level!
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core import StorageContext

```

from llama_index.core import VectorStoreIndex from llama_index.core import StorageContext
In [ ]:
Copied!
```
index = VectorStoreIndex.from_vector_store(vector_store)

```

index = VectorStoreIndex.from_vector_store(vector_store)
In [ ]:
Copied!
```
query_engine = index.as_query_engine()

```

query_engine = index.as_query_engine()
In [ ]:
Copied!
```
query_str = "Can you tell me about the key concepts for safety finetuning"

```

query_str = "Can you tell me about the key concepts for safety finetuning"
In [ ]:
Copied!
```
response = query_engine.query(query_str)

```

response = query_engine.query(query_str)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
