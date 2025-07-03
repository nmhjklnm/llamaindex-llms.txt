# Memgraph Property Graph Index¶
Memgraph is an open source graph database built real-time streaming and fast analysis of your stored data.
Before running Memgraph, ensure you have Docker running in the background. The quickest way to try out Memgraph Platform (Memgraph database + MAGE library + Memgraph Lab) for the first time is running the following command:
For Linux/macOS:
```
curl https://install.memgraph.com | sh

```

For Windows:
```
iwr https://windows.memgraph.com | iex

```

From here, you can check Memgraph's visual tool, Memgraph Lab on the http://localhost:3000/ or the desktop version of the app.
In [ ]:
Copied!
```
%pip install llama-index llama-index-graph-stores-memgraph

```

%pip install llama-index llama-index-graph-stores-memgraph
## Environment setup¶
In [ ]:
Copied!
```
import os

os.environ[
    "OPENAI_API_KEY"
] = "sk-proj-..."  # Replace with your OpenAI API key

```

import os os.environ[ "OPENAI_API_KEY" ] = "sk-proj-..." # Replace with your OpenAI API key
Create the data directory and download the Paul Graham essay we'll be using as the input data for this example.
In [ ]:
Copied!
```
import urllib.request

os.makedirs("data/paul_graham/", exist_ok=True)

url = "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt"
output_path = "data/paul_graham/paul_graham_essay.txt"
urllib.request.urlretrieve(url, output_path)

```

import urllib.request os.makedirs("data/paul_graham/", exist_ok=True) url = "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt" output_path = "data/paul_graham/paul_graham_essay.txt" urllib.request.urlretrieve(url, output_path)
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
Read the file, replace single quotes, save the modified content and load the document data using the `SimpleDirectoryReader`
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

with open(output_path, "r", encoding="utf-8") as file:
    content = file.read()

with open(output_path, "w", encoding="utf-8") as file:
    file.write(content)

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

from llama_index.core import SimpleDirectoryReader with open(output_path, "r", encoding="utf-8") as file: content = file.read() with open(output_path, "w", encoding="utf-8") as file: file.write(content) documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
## Setup Memgraph connection¶
Set up your graph store class by providing the database credentials.
In [ ]:
Copied!
```
from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore

username = ""  # Enter your Memgraph username (default "")
password = ""  # Enter your Memgraph password (default "")
url = ""  # Specify the connection URL, e.g., 'bolt://localhost:7687'

graph_store = MemgraphPropertyGraphStore(
    username=username,
    password=password,
    url=url,
)

```

from llama_index.graph_stores.memgraph import MemgraphPropertyGraphStore username = "" # Enter your Memgraph username (default "") password = "" # Enter your Memgraph password (default "") url = "" # Specify the connection URL, e.g., 'bolt://localhost:7687' graph_store = MemgraphPropertyGraphStore( username=username, password=password, url=url, )
## Index Construction¶
In [ ]:
Copied!
```
from llama_index.core import PropertyGraphIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor

index = PropertyGraphIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(model_name="text-embedding-ada-002"),
    kg_extractors=[
        SchemaLLMPathExtractor(
            llm=OpenAI(model="gpt-3.5-turbo", temperature=0.0)
        )
    ],
    property_graph_store=graph_store,
    show_progress=True,
)

```

from llama_index.core import PropertyGraphIndex from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI from llama_index.core.indices.property_graph import SchemaLLMPathExtractor index = PropertyGraphIndex.from_documents( documents, embed_model=OpenAIEmbedding(model_name="text-embedding-ada-002"), kg_extractors=[ SchemaLLMPathExtractor( llm=OpenAI(model="gpt-3.5-turbo", temperature=0.0) ) ], property_graph_store=graph_store, show_progress=True, )
Now that the graph is created, we can explore it in the UI by visiting http://localhost:3000/.
The easiest way to visualize the entire graph is by running a Cypher command similar to this:
```
MATCH p=()-[]-() RETURN p;

```

This command matches all of the possible paths in the graph and returns entire graph.
To visualize the schema of the graph, visit the Graph schema tab and generate the new schema based on the newly created graph.
To delete an entire graph, use:
```
MATCH (n) DETACH DELETE n;

```

## Querying and retrieval¶
In [ ]:
Copied!
```
retriever = index.as_retriever(include_text=False)

# Example query: "What happened at Interleaf and Viaweb?"
nodes = retriever.retrieve("What happened at Interleaf and Viaweb?")

# Output results
print("Query Results:")
for node in nodes:
    print(node.text)

# Alternatively, using a query engine
query_engine = index.as_query_engine(include_text=True)

# Perform a query and print the detailed response
response = query_engine.query("What happened at Interleaf and Viaweb?")
print("\nDetailed Query Response:")
print(str(response))

```

retriever = index.as_retriever(include_text=False) # Example query: "What happened at Interleaf and Viaweb?" nodes = retriever.retrieve("What happened at Interleaf and Viaweb?") # Output results print("Query Results:") for node in nodes: print(node.text) # Alternatively, using a query engine query_engine = index.as_query_engine(include_text=True) # Perform a query and print the detailed response response = query_engine.query("What happened at Interleaf and Viaweb?") print("\nDetailed Query Response:") print(str(response))
## Loading from an existing graph¶
If you have an existing graph (either created with LlamaIndex or otherwise), we can connect to and use it!
**NOTE:** If your graph was created outside of LlamaIndex, the most useful retrievers will be text to cypher or cypher templates. Other retrievers rely on properties that LlamaIndex inserts.
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4", temperature=0.0)
kg_extractors = [SchemaLLMPathExtractor(llm=llm)]

index = PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
    kg_extractors=kg_extractors,
    embed_model=OpenAIEmbedding(model_name="text-embedding-ada-002"),
    show_progress=True,
)

```

llm = OpenAI(model="gpt-4", temperature=0.0) kg_extractors = [SchemaLLMPathExtractor(llm=llm)] index = PropertyGraphIndex.from_existing( property_graph_store=graph_store, kg_extractors=kg_extractors, embed_model=OpenAIEmbedding(model_name="text-embedding-ada-002"), show_progress=True, )
