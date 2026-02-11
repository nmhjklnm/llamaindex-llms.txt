![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# PostgresML Managed Index¶
In this notebook we are going to show how to use PostgresML with LlamaIndex.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index-indices-managed-postgresml

```

!pip install llama-index-indices-managed-postgresml
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.indices.managed.postgresml import PostgresMLIndex

from llama_index.core import SimpleDirectoryReader

# Need this as asyncio can get pretty wild with notebooks and this prevents event loop errors
import nest_asyncio

nest_asyncio.apply()

```

from llama_index.indices.managed.postgresml import PostgresMLIndex from llama_index.core import SimpleDirectoryReader # Need this as asyncio can get pretty wild with notebooks and this prevents event loop errors import nest_asyncio nest_asyncio.apply()
### Loading documents¶
Load the `paul_graham_essay.txt` document.
In [ ]:
Copied!
```
!mkdir data
!curl -o data/paul_graham_essay.txt https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt

```

!mkdir data !curl -o data/paul_graham_essay.txt https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("data").load_data()
print(f"documents loaded into {len(documents)} document objects")
print(f"Document ID of first doc is {documents[0].doc_id}")

```

documents = SimpleDirectoryReader("data").load_data() print(f"documents loaded into {len(documents)} document objects") print(f"Document ID of first doc is {documents[0].doc_id}")
### Upsert the documents into your PostgresML database¶
First let's set the url to our PostgresML database. If you don't have a url yet, you can make one for free here: https://postgresml.org/signup
In [ ]:
Copied!
```
# Let's set some secrets we need
from google.colab import userdata

PGML_DATABASE_URL = userdata.get("PGML_DATABASE_URL")

# If you don't have those secrets set, uncomment the lines below and run them instead
# Make sure to replace {REPLACE_ME} with your keys
# PGML_DATABASE_URL = "{REPLACE_ME}"

```

# Let's set some secrets we need from google.colab import userdata PGML_DATABASE_URL = userdata.get("PGML_DATABASE_URL") # If you don't have those secrets set, uncomment the lines below and run them instead # Make sure to replace {REPLACE_ME} with your keys # PGML_DATABASE_URL = "{REPLACE_ME}"
In [ ]:
Copied!
```
index = PostgresMLIndex.from_documents(
    documents,
    collection_name="llama-index-example-demo",
    pgml_database_url=PGML_DATABASE_URL,
)

```

index = PostgresMLIndex.from_documents( documents, collection_name="llama-index-example-demo", pgml_database_url=PGML_DATABASE_URL, )
### Query the Postgresml Index¶
We can now ask questions using the PostgresMLIndex retriever.
In [ ]:
Copied!
```
query = "What did the author write about?"

```

query = "What did the author write about?"
We can use a retriever to list search our documents:
In [ ]:
Copied!
```
retriever = index.as_retriever()
response = retriever.retrieve(query)
texts = [t.node.text for t in response]

print("The Nodes:")
print(response)
print("\nThe Texts")
print(texts)

```

retriever = index.as_retriever() response = retriever.retrieve(query) texts = [t.node.text for t in response] print("The Nodes:") print(response) print("\nThe Texts") print(texts)
PostgresML allows for easy re-reranking in the same query as doing retrieval:
In [ ]:
Copied!
```
retriever = index.as_retriever(
    limit=2,  # Limit to returning the 2 most related Nodes
    rerank={
        "model": "mixedbread-ai/mxbai-rerank-base-v1",  # Use the mxbai-rerank-base model for reranking
        "num_documents_to_rerank": 100,  # Rerank up to 100 results returned from the vector search
    },
)
response = retriever.retrieve(query)
texts = [t.node.text for t in response]

print("The Nodes:")
print(response)
print("\nThe Texts")
print(texts)

```

retriever = index.as_retriever( limit=2, # Limit to returning the 2 most related Nodes rerank={ "model": "mixedbread-ai/mxbai-rerank-base-v1", # Use the mxbai-rerank-base model for reranking "num_documents_to_rerank": 100, # Rerank up to 100 results returned from the vector search }, ) response = retriever.retrieve(query) texts = [t.node.text for t in response] print("The Nodes:") print(response) print("\nThe Texts") print(texts)
with the as_query_engine(), we can ask questions and get the response in one query:
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query(query)

print("The Response:")
print(response)
print("\nThe Source Nodes:")
print(response.get_formatted_sources())

```

query_engine = index.as_query_engine() response = query_engine.query(query) print("The Response:") print(response) print("\nThe Source Nodes:") print(response.get_formatted_sources())
Note that the "response" object above includes both the summary text but also the source documents used to provide this response (citations). Notice the source nodes are all from the same document. That is because we only uploaded one document which PostgresML automatically split before embedding for us. All parameters can be controlled. See the documentation for more information.
We can enable streaming by passing `streaming=True` when we create our query_engine.
**NOTE: Streaming is painfully slow on google collab due to their internet connectivity.**
In [ ]:
Copied!
```
query_engine = index.as_query_engine(streaming=True)
results = query_engine.query(query)
for text in results.response_gen:
    print(text, end="", flush=True)

```

query_engine = index.as_query_engine(streaming=True) results = query_engine.query(query) for text in results.response_gen: print(text, end="", flush=True)
