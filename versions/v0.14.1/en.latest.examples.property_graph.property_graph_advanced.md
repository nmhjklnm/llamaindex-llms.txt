# Property Graph Construction with Predefined Schemas¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In this notebook, we walk through using Neo4j, Ollama and Huggingface to build a property graph.
Specifically, we will be using the `SchemaLLMPathExtractor` which allows us to specify an exact schema containing possible entity types, relation types, and defining how they can be connected together.
This is useful for when you have a specific graph you want to build, and want to limit what the LLM is predicting.
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-llms-ollama
%pip install llama-index-embeddings-huggingface
# Optional
%pip install llama-index-graph-stores-neo4j
%pip install llama-index-graph-stores-nebula

```

%pip install llama-index %pip install llama-index-llms-ollama %pip install llama-index-embeddings-huggingface # Optional %pip install llama-index-graph-stores-neo4j %pip install llama-index-graph-stores-nebula
## Load Data¶
First, lets download some sample data to play with.
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-06-26 11:12:16--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.109.133, 185.199.111.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.007s  

2024-06-26 11:12:16 (10.4 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
## Graph Construction¶
To construct our graph, we are going to take advantage of the `SchemaLLMPathExtractor` to construct our graph.
Given some schema for a graph, we can extract entities and relations that follow this schema, rather than letting the LLM decide entities and relations at random.
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from typing import Literal
from llama_index.llms.ollama import Ollama
from llama_index.core.indices.property_graph import SchemaLLMPathExtractor

# best practice to use upper-case
entities = Literal["PERSON", "PLACE", "ORGANIZATION"]
relations = Literal["HAS", "PART_OF", "WORKED_ON", "WORKED_WITH", "WORKED_AT"]

# define which entities can have which relations
validation_schema = {
    "PERSON": ["HAS", "PART_OF", "WORKED_ON", "WORKED_WITH", "WORKED_AT"],
    "PLACE": ["HAS", "PART_OF", "WORKED_AT"],
    "ORGANIZATION": ["HAS", "PART_OF", "WORKED_WITH"],
}

kg_extractor = SchemaLLMPathExtractor(
    llm=Ollama(
        model="llama3",
        json_mode=True,
        request_timeout=3600,
        # Manually set the context window to limit memory usage
        context_window=8000,
    ),
    possible_entities=entities,
    possible_relations=relations,
    kg_validation_schema=validation_schema,
    # if false, allows for values outside of the schema
    # useful for using the schema as a suggestion
    strict=True,
)

```

from typing import Literal from llama_index.llms.ollama import Ollama from llama_index.core.indices.property_graph import SchemaLLMPathExtractor # best practice to use upper-case entities = Literal["PERSON", "PLACE", "ORGANIZATION"] relations = Literal["HAS", "PART_OF", "WORKED_ON", "WORKED_WITH", "WORKED_AT"] # define which entities can have which relations validation_schema = { "PERSON": ["HAS", "PART_OF", "WORKED_ON", "WORKED_WITH", "WORKED_AT"], "PLACE": ["HAS", "PART_OF", "WORKED_AT"], "ORGANIZATION": ["HAS", "PART_OF", "WORKED_WITH"], } kg_extractor = SchemaLLMPathExtractor( llm=Ollama( model="llama3", json_mode=True, request_timeout=3600, # Manually set the context window to limit memory usage context_window=8000, ), possible_entities=entities, possible_relations=relations, kg_validation_schema=validation_schema, # if false, allows for values outside of the schema # useful for using the schema as a suggestion strict=True, )
Now, You can use SimplePropertyGraph, Neo4j, or NebulaGraph to store the graph.
**Option 1. Neo4j**
To launch Neo4j locally, first ensure you have docker installed. Then, you can launch the database with the following docker command
```
docker run \
    -p 7474:7474 -p 7687:7687 \
    -v $PWD/data:/data -v $PWD/plugins:/plugins \
    --name neo4j-apoc \
    -e NEO4J_apoc_export_file_enabled=true \
    -e NEO4J_apoc_import_file_enabled=true \
    -e NEO4J_apoc_import_file_use__neo4j__config=true \
    -e NEO4JLABS_PLUGINS=\[\"apoc\"\] \
    neo4j:latest

```

From here, you can open the db at http://localhost:7474/. On this page, you will be asked to sign in. Use the default username/password of `neo4j` and `neo4j`.
Once you login for the first time, you will be asked to change the password.
After this, you are ready to create your first property graph!
In [ ]:
Copied!
```
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore

graph_store = Neo4jPropertyGraphStore(
    username="neo4j",
    password="<password>",
    url="bolt://localhost:7687",
)
vec_store = None

```

from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore graph_store = Neo4jPropertyGraphStore( username="neo4j", password="", url="bolt://localhost:7687", ) vec_store = None
**Option 2. NebulaGraph**
To launch NebulaGraph locally, first ensure you have docker installed. Then, you can launch the database with the following docker command.
```
mkdir nebula-docker-compose
cd nebula-docker-compose
curl --output docker-compose.yaml https://raw.githubusercontent.com/vesoft-inc/nebula-docker-compose/master/docker-compose-lite.yaml
docker compose up

```

After this, you are ready to create your first property graph!
> Other options/details for deploying NebulaGraph can be found in the docs:
>   * ad-hoc cluster in Google Colab.
>   * Docker Desktop Extension.
> 

In [ ]:
Copied!
```
from llama_index.graph_stores.nebula import NebulaPropertyGraphStore
from llama_index.core.vector_stores.simple import SimpleVectorStore

graph_store = NebulaPropertyGraphStore(
    space="llamaindex_nebula_property_graph", overwrite=True
)
vec_store = SimpleVectorStore()

```

from llama_index.graph_stores.nebula import NebulaPropertyGraphStore from llama_index.core.vector_stores.simple import SimpleVectorStore graph_store = NebulaPropertyGraphStore( space="llamaindex_nebula_property_graph", overwrite=True ) vec_store = SimpleVectorStore()
_If you want to explore the graph with NebulaGraph Jupyter extension_ , run the following commands. Or just skip them.
In [ ]:
Copied!
```
%pip install jupyter-nebulagraph

```

%pip install jupyter-nebulagraph
In [ ]:
Copied!
```
# load NebulaGraph Jupyter extension to enable %ngql magic
%load_ext ngql
# connect to NebulaGraph service
%ngql --address 127.0.0.1 --port 9669 --user root --password nebula
%ngql CREATE SPACE IF NOT EXISTS llamaindex_nebula_property_graph(vid_type=FIXED_STRING(256));

```

# load NebulaGraph Jupyter extension to enable %ngql magic %load_ext ngql # connect to NebulaGraph service %ngql --address 127.0.0.1 --port 9669 --user root --password nebula %ngql CREATE SPACE IF NOT EXISTS llamaindex_nebula_property_graph(vid_type=FIXED_STRING(256));
In [ ]:
Copied!
```
# use the graph space, which is similar to "use database" in MySQL
# The space was created in async way, so we need to wait for a while before using it, retry it if failed
%ngql USE llamaindex_nebula_property_graph;

```

# use the graph space, which is similar to "use database" in MySQL # The space was created in async way, so we need to wait for a while before using it, retry it if failed %ngql USE llamaindex_nebula_property_graph;
**Start building!**
**NOTE:** Using a local model will be slower when extracting compared to API based models. Local models (like Ollama) are typically limited to sequential processing. Expect this to take about 10 minutes on an M2 Max.
In [ ]:
Copied!
```
from llama_index.core import PropertyGraphIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

index = PropertyGraphIndex.from_documents(
    documents,
    kg_extractors=[kg_extractor],
    embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    property_graph_store=graph_store,
    vector_store=vec_store,
    show_progress=True,
)

```

from llama_index.core import PropertyGraphIndex from llama_index.embeddings.huggingface import HuggingFaceEmbedding index = PropertyGraphIndex.from_documents( documents, kg_extractors=[kg_extractor], embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"), property_graph_store=graph_store, vector_store=vec_store, show_progress=True, )
If we inspect the graph created, we can see that it only includes the relations and entity types that we defined!
In [ ]:
Copied!
```
# If using NebulaGraph Jupyter extension
%ngql MATCH p=()-[]->() RETURN p LIMIT 20;

```

# If using NebulaGraph Jupyter extension %ngql MATCH p=()-[]->() RETURN p LIMIT 20;
In [ ]:
Copied!
```
%ng_draw

```

%ng_draw
Or Neo4j:
![local graph](https://docs.llamaindex.ai/en/latest/examples/property_graph/property_graph_advanced/local_kg.png)
For information on all `kg_extractors`, see the documentation.
## Querying¶
Now that our graph is created, we can query it.
As is the theme with this notebook, we will be using a lower-level API and constructing all our retrievers ourselves!
In [ ]:
Copied!
```
from llama_index.core.indices.property_graph import (
    LLMSynonymRetriever,
    VectorContextRetriever,
)


llm_synonym = LLMSynonymRetriever(
    index.property_graph_store,
    llm=Ollama(
        model="llama3",
        request_timeout=3600,
        # Manually set the context window to limit memory usage
        context_window=8000,
    ),
    include_text=False,
)
vector_context = VectorContextRetriever(
    index.property_graph_store,
    embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    include_text=False,
)

```

from llama_index.core.indices.property_graph import ( LLMSynonymRetriever, VectorContextRetriever, ) llm_synonym = LLMSynonymRetriever( index.property_graph_store, llm=Ollama( model="llama3", request_timeout=3600, # Manually set the context window to limit memory usage context_window=8000, ), include_text=False, ) vector_context = VectorContextRetriever( index.property_graph_store, embed_model=HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5"), include_text=False, )
In [ ]:
Copied!
```
retriever = index.as_retriever(
    sub_retrievers=[
        llm_synonym,
        vector_context,
    ]
)

```

retriever = index.as_retriever( sub_retrievers=[ llm_synonym, vector_context, ] )
In [ ]:
Copied!
```
nodes = retriever.retrieve("What happened at Interleaf?")

for node in nodes:
    print(node.text)

```

nodes = retriever.retrieve("What happened at Interleaf?") for node in nodes: print(node.text)
```
Interleaf -> HAS -> Paul Graham
Interleaf -> HAS -> Emacs
Interleaf -> HAS -> Release Engineering
Interleaf -> HAS -> Viaweb
Interleaf -> HAS -> Y Combinator
Interleaf -> HAS -> impressive technology
Interleaf -> HAS -> smart people

```

We can also create a query engine with similar syntax.
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    sub_retrievers=[
        llm_synonym,
        vector_context,
    ],
    llm=Ollama(
        model="llama3",
        request_timeout=3600,
        # Manually set the context window to limit memory usage
        context_window=8000,
    ),
)

response = query_engine.query("What happened at Interleaf?")

print(str(response))

```

query_engine = index.as_query_engine( sub_retrievers=[ llm_synonym, vector_context, ], llm=Ollama( model="llama3", request_timeout=3600, # Manually set the context window to limit memory usage context_window=8000, ), ) response = query_engine.query("What happened at Interleaf?") print(str(response))
```
Paul Graham worked there, as well as other smart people. Emacs was also present.

```

For more info on all retrievers, see the complete guide.
