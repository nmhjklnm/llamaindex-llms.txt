# NebulaGraph Property Graph Index¶
NebulaGraph is an open-source distributed graph database built for super large-scale graphs with milliseconds of latency.
If you already have an existing graph, please skip to the end of this notebook.
In [ ]:
Copied!
```
%pip install llama-index llama-index-graph-stores-nebula jupyter-nebulagraph

```

%pip install llama-index llama-index-graph-stores-nebula jupyter-nebulagraph
## Docker Setup¶
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
# load NebulaGraph Jupyter extension to enable %ngql magic
%load_ext ngql
# connect to NebulaGraph service
%ngql --address 127.0.0.1 --port 9669 --user root --password nebula
# create a graph space(think of a Database Instance) named: llamaindex_nebula_property_graph
%ngql CREATE SPACE IF NOT EXISTS llamaindex_nebula_property_graph(vid_type=FIXED_STRING(256));

```

# load NebulaGraph Jupyter extension to enable %ngql magic %load_ext ngql # connect to NebulaGraph service %ngql --address 127.0.0.1 --port 9669 --user root --password nebula # create a graph space(think of a Database Instance) named: llamaindex_nebula_property_graph %ngql CREATE SPACE IF NOT EXISTS llamaindex_nebula_property_graph(vid_type=FIXED_STRING(256));
```
Connection Pool Created

```

Out[ ]:  
---  
In [ ]:
Copied!
```
# use the graph space, which is similar to "use database" in MySQL
# The space was created in async way, so we need to wait for a while before using it, retry it if failed
%ngql USE llamaindex_nebula_property_graph;

```

# use the graph space, which is similar to "use database" in MySQL # The space was created in async way, so we need to wait for a while before using it, retry it if failed %ngql USE llamaindex_nebula_property_graph;
Out[ ]:  
---  
## Env Setup¶
We need just a few environment setups to get started.
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-proj-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-proj-..."
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
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
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
We choose using gpt-4o and local embedding model intfloat/multilingual-e5-large . You can change to what you like, by editing the following lines:
In [ ]:
Copied!
```
%pip install llama-index-embeddings-huggingface

```

%pip install llama-index-embeddings-huggingface
In [ ]:
Copied!
```
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.llm = OpenAI(model="gpt-4o", temperature=0.3)
Settings.embed_model = HuggingFaceEmbedding(
    model_name="intfloat/multilingual-e5-large"
)
# Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")

```

from llama_index.core import Settings from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.embeddings.huggingface import HuggingFaceEmbedding Settings.llm = OpenAI(model="gpt-4o", temperature=0.3) Settings.embed_model = HuggingFaceEmbedding( model_name="intfloat/multilingual-e5-large" ) # Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")
## Index Construction¶
Prepare property graph store
In [ ]:
Copied!
```
from llama_index.graph_stores.nebula import NebulaPropertyGraphStore

graph_store = NebulaPropertyGraphStore(
    space="llamaindex_nebula_property_graph", overwrite=True
)

```

from llama_index.graph_stores.nebula import NebulaPropertyGraphStore graph_store = NebulaPropertyGraphStore( space="llamaindex_nebula_property_graph", overwrite=True )
And vector store:
In [ ]:
Copied!
```
from llama_index.core.vector_stores.simple import SimpleVectorStore

vec_store = SimpleVectorStore()

```

from llama_index.core.vector_stores.simple import SimpleVectorStore vec_store = SimpleVectorStore()
Finally, build the index!
In [ ]:
Copied!
```
from llama_index.core.indices.property_graph import PropertyGraphIndex
from llama_index.core.storage.storage_context import StorageContext
from llama_index.llms.openai import OpenAI

index = PropertyGraphIndex.from_documents(
    documents,
    property_graph_store=graph_store,
    vector_store=vec_store,
    show_progress=True,
)

index.storage_context.vector_store.persist("./data/nebula_vec_store.json")

```

from llama_index.core.indices.property_graph import PropertyGraphIndex from llama_index.core.storage.storage_context import StorageContext from llama_index.llms.openai import OpenAI index = PropertyGraphIndex.from_documents( documents, property_graph_store=graph_store, vector_store=vec_store, show_progress=True, ) index.storage_context.vector_store.persist("./data/nebula_vec_store.json")
```
/Users/loganmarkewich/Library/Caches/pypoetry/virtualenvs/llama-index-caVs7DDe-py3.11/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm
Parsing nodes: 100%|██████████| 1/1 [00:00<00:00, 20.96it/s]
Extracting paths from text: 100%|██████████| 22/22 [00:19<00:00,  1.15it/s]
Extracting implicit paths: 100%|██████████| 22/22 [00:00<00:00, 25253.06it/s]
Generating embeddings: 100%|██████████| 1/1 [00:01<00:00,  1.06s/it]
Generating embeddings: 100%|██████████| 5/5 [00:02<00:00,  2.50it/s]

```

Now that the graph is created, we can explore it with jupyter-nebulagraph
In [ ]:
Copied!
```
%ngql SHOW TAGS

```

%ngql SHOW TAGS
Out[ ]:
| Name  
---|---  
0 | Chunk__  
1 | Entity__  
2 | Node__  
3 | Props__  
In [ ]:
Copied!
```
%ngql SHOW EDGES

```

%ngql SHOW EDGES
Out[ ]:
| Name  
---|---  
0 | Relation__  
1 | __meta__node_label__  
2 | __meta__rel_label__  
In [ ]:
Copied!
```
%ngql MATCH p=(v:Entity__)-[r]->(t:Entity__) RETURN v.Entity__.name AS src, r.label AS relation, t.Entity__.name AS dest LIMIT 15;

```

%ngql MATCH p=(v:Entity__)-[r]->(t:Entity__) RETURN v.Entity__.name AS src, r.label AS relation, t.Entity__.name AS dest LIMIT 15;
Out[ ]:
| src | relation | dest  
---|---|---|---  
0 | We | Charged | $100 a month for a small store  
1 | We | Charged | $300 a month for a big store  
2 | We | Got to work | Build software  
3 | We | Started | Company  
4 | We | Start | Investment firm  
5 | We | Opened for business | January 1996  
6 | We | Had | One that worked  
7 | We | Decided to try making | Version of store builder  
8 | Growth rate | Takes care of | Absolute number  
9 | Stock | Went up | 5x  
10 | Jessica livingston | In charge of | Marketing at boston investment bank  
11 | Language | Would be | Dialect of lisp  
12 | Language | Used | Early version of fortran  
13 | Arc | Compiled into | Scheme  
14 | Deal | Became | Model for y combinator's  
In [ ]:
Copied!
```
%ngql MATCH p=(v:Entity__)-[r]->(t:Entity__) RETURN p LIMIT 2;

```

%ngql MATCH p=(v:Entity__)-[r]->(t:Entity__) RETURN p LIMIT 2;
Out[ ]:
| p  
---|---  
0 | ("We" :Props__{_node_content: __NULL__, _node_type: __NULL__, creation_date: "2024-05-31", doc_id: __NULL__, document_id: __NULL__, file_name: "paul_graham_essay.txt", file_path: "/Users/loganmarkewich/giant_change/llama_index/docs/docs/examples/property_graph/data/paul_graham/paul_graham_essay.txt", file_size: 75042, file_type: "text/plain", last_modified_date: "2024-05-31", ref_doc_id: __NULL__, triplet_source_id: "4145ba08-a096-4ac1-8f7c-f40642c857cc"} :Node__{label: "entity"} :Entity__{name: "We"})-[:Relation__@0{label: "Charged", file_path: "/Users/loganmarkewich/giant_change/llama_index/docs/docs/examples/property_graph/data/paul_graham/paul_graham_essay.txt", file_name: "paul_graham_essay.txt", file_type: "text/plain", file_size: 75042, _node_type: __NULL__, creation_date: "2024-05-31", document_id: __NULL__, last_modified_date: "2024-05-31", doc_id: __NULL__, _node_content: __NULL__, ref_doc_id: __NULL__, triplet_source_id: "0faa4540-57bb-4b94-8bc2-46431d980182"}]->("$100 a month for a small store" :Props__{_node_content: __NULL__, _node_type: __NULL__, creation_date: "2024-05-31", doc_id: __NULL__, document_id: __NULL__, file_name: "paul_graham_essay.txt", file_path: "/Users/loganmarkewich/giant_change/llama_index/docs/docs/examples/property_graph/data/paul_graham/paul_graham_essay.txt", file_size: 75042, file_type: "text/plain", last_modified_date: "2024-05-31", ref_doc_id: __NULL__, triplet_source_id: "0faa4540-57bb-4b94-8bc2-46431d980182"} :Node__{label: "entity"} :Entity__{name: "$100 a month for a small store"})  
1 | ("We" :Props__{_node_content: __NULL__, _node_type: __NULL__, creation_date: "2024-05-31", doc_id: __NULL__, document_id: __NULL__, file_name: "paul_graham_essay.txt", file_path: "/Users/loganmarkewich/giant_change/llama_index/docs/docs/examples/property_graph/data/paul_graham/paul_graham_essay.txt", file_size: 75042, file_type: "text/plain", last_modified_date: "2024-05-31", ref_doc_id: __NULL__, triplet_source_id: "4145ba08-a096-4ac1-8f7c-f40642c857cc"} :Node__{label: "entity"} :Entity__{name: "We"})-[:Relation__@0{label: "Charged", file_path: "/Users/loganmarkewich/giant_change/llama_index/docs/docs/examples/property_graph/data/paul_graham/paul_graham_essay.txt", file_name: "paul_graham_essay.txt", file_type: "text/plain", file_size: 75042, _node_type: __NULL__, creation_date: "2024-05-31", document_id: __NULL__, last_modified_date: "2024-05-31", doc_id: __NULL__, _node_content: __NULL__, ref_doc_id: __NULL__, triplet_source_id: "0faa4540-57bb-4b94-8bc2-46431d980182"}]->("$300 a month for a big store" :Props__{_node_content: __NULL__, _node_type: __NULL__, creation_date: "2024-05-31", doc_id: __NULL__, document_id: __NULL__, file_name: "paul_graham_essay.txt", file_path: "/Users/loganmarkewich/giant_change/llama_index/docs/docs/examples/property_graph/data/paul_graham/paul_graham_essay.txt", file_size: 75042, file_type: "text/plain", last_modified_date: "2024-05-31", ref_doc_id: __NULL__, triplet_source_id: "0faa4540-57bb-4b94-8bc2-46431d980182"} :Node__{label: "entity"} :Entity__{name: "$300 a month for a big store"})  
In [ ]:
Copied!
```
%ng_draw

```

%ng_draw
## Querying and Retrieval¶
In [ ]:
Copied!
```
retriever = index.as_retriever(
    include_text=False,  # include source text in returned nodes, default True
)

nodes = retriever.retrieve("What happened at Interleaf and Viaweb?")

for node in nodes:
    print(node.text)

```

retriever = index.as_retriever( include_text=False, # include source text in returned nodes, default True ) nodes = retriever.retrieve("What happened at Interleaf and Viaweb?") for node in nodes: print(node.text)
```
Interleaf -> Got a job at -> I
Interleaf -> Crushed -> Moore's law
Interleaf -> Was -> Company
Interleaf -> Built -> Impressive technology
Interleaf -> Added -> Scripting language
Interleaf -> Had -> Smart people
Interleaf -> Made -> Software for creating documents
Viaweb -> Called -> Company
Viaweb -> Worked for -> Dan giffin
Viaweb -> Was -> Application service provider
In viaweb -> Was -> Code editor
Viaweb stock -> Was -> Valuable
Viaweb logo -> Had -> White v on red circle

```

In [ ]:
Copied!
```
query_engine = index.as_query_engine(include_text=True)

response = query_engine.query("What happened at Interleaf and Viaweb?")

print(str(response))

```

query_engine = index.as_query_engine(include_text=True) response = query_engine.query("What happened at Interleaf and Viaweb?") print(str(response))
```
Interleaf was a company that built impressive technology and had smart people, but it was ultimately crushed by Moore's Law in the 1990s due to the exponential growth in the power of commodity processors. Despite adding a scripting language and making software for creating documents, it could not keep up with the rapid advancements in hardware.

Viaweb, on the other hand, was an application service provider that created a code editor for users to define their own page styles, which were actually Lisp expressions. The company was eventually bought by Yahoo in the summer of 1998. The Viaweb stock became valuable, and the acquisition marked a significant turning point for its founders. The Viaweb logo featured a white "V" on a red circle, which later inspired the Y Combinator logo.

```

## Loading from an existing Graph¶
If you have an existing graph, we can connect to and use it!
In [ ]:
Copied!
```
from llama_index.graph_stores.nebula import NebulaPropertyGraphStore

graph_store = NebulaPropertyGraphStore(
    space="llamaindex_nebula_property_graph"
)

from llama_index.core.vector_stores.simple import SimpleVectorStore

vec_store = SimpleVectorStore.from_persist_path("./data/nebula_vec_store.json")

index = PropertyGraphIndex.from_existing(
    property_graph_store=graph_store,
    vector_store=vec_store,
)

```

from llama_index.graph_stores.nebula import NebulaPropertyGraphStore graph_store = NebulaPropertyGraphStore( space="llamaindex_nebula_property_graph" ) from llama_index.core.vector_stores.simple import SimpleVectorStore vec_store = SimpleVectorStore.from_persist_path("./data/nebula_vec_store.json") index = PropertyGraphIndex.from_existing( property_graph_store=graph_store, vector_store=vec_store, )
From here, we can still insert more documents!
In [ ]:
Copied!
```
from llama_index.core import Document

document = Document(text="LlamaIndex is great!")

index.insert(document)

```

from llama_index.core import Document document = Document(text="LlamaIndex is great!") index.insert(document)
In [ ]:
Copied!
```
nodes = index.as_retriever(include_text=False).retrieve("LlamaIndex")

print(nodes[0].text)

```

nodes = index.as_retriever(include_text=False).retrieve("LlamaIndex") print(nodes[0].text)
```
Llamaindex -> Is -> Great

```

