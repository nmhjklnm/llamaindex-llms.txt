![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Knowledge Graph RAG Query Engine¶
## Graph RAG¶
Graph RAG is an Knowledge-enabled RAG approach to retrieve information from Knowledge Graph on given task. Typically, this is to build context based on entities' SubGraph related to the task.
## GraphStore backed RAG vs VectorStore RAG¶
As we compared how Graph RAG helps in some use cases in this tutorial, it's shown Knowledge Graph as the unique format of information could mitigate several issues caused by the nature of the "split and embedding" RAG approach.
## Why Knowledge Graph RAG Query Engine¶
In Llama Index, there are two scenarios we could apply Graph RAG:
  * Build Knowledge Graph from documents with Llama Index, with LLM or even local models, to do this, we should go for `KnowledgeGraphIndex`.
  * Leveraging existing Knowledge Graph, in this case, we should use `KnowledgeGraphRAGQueryEngine`.


> Note, the third query engine that's related to KG in Llama Index is `NL2GraphQuery` or `Text2Cypher`, for either exiting KG or not, it could be done with `KnowledgeGraphQueryEngine`.
Before we start the `Knowledge Graph RAG QueryEngine` demo, let's first get ready for basic preparation of Llama Index.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-azure-openai
%pip install llama-index-graph-stores-nebula
%pip install llama-index-llms-openai
%pip install llama-index-embeddings-azure-openai

```

%pip install llama-index-llms-azure-openai %pip install llama-index-graph-stores-nebula %pip install llama-index-llms-openai %pip install llama-index-embeddings-azure-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
### OpenAI¶
In [ ]:
Copied!
```
# For OpenAI

import os

os.environ["OPENAI_API_KEY"] = "sk-..."

import logging
import sys

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO
)  # logging.DEBUG for more verbose output


# define LLM
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.chunk_size = 512

```

# For OpenAI import os os.environ["OPENAI_API_KEY"] = "sk-..." import logging import sys logging.basicConfig( stream=sys.stdout, level=logging.INFO ) # logging.DEBUG for more verbose output # define LLM from llama_index.llms.openai import OpenAI from llama_index.core import Settings Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo") Settings.chunk_size = 512
### Azure¶
In [ ]:
Copied!
```
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

# For Azure OpenAI
api_key = "<api-key>"
azure_endpoint = "https://<your-resource-name>.openai.azure.com/"
api_version = "2023-07-01-preview"

llm = AzureOpenAI(
    model="gpt-35-turbo-16k",
    deployment_name="my-custom-llm",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

# You need to deploy your own embedding model as well as your own chat completion model
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="my-custom-embedding",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

```

from llama_index.llms.azure_openai import AzureOpenAI from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding # For Azure OpenAI api_key = "" azure_endpoint = "https://.openai.azure.com/" api_version = "2023-07-01-preview" llm = AzureOpenAI( model="gpt-35-turbo-16k", deployment_name="my-custom-llm", api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version, ) # You need to deploy your own embedding model as well as your own chat completion model embed_model = AzureOpenAIEmbedding( model="text-embedding-ada-002", deployment_name="my-custom-embedding", api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version, )
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model
Settings.chunk_size = 512

```

from llama_index.core import Settings Settings.llm = llm Settings.embed_model = embed_model Settings.chunk_size = 512
## Prepare for NebulaGraph¶
We take NebulaGraphStore as an example in this demo, thus before next step to perform Graph RAG on existing KG, let's ensure we have a running NebulaGraph with defined data schema.
This step installs the clients of NebulaGraph, and prepare contexts that defines a NebulaGraph Graph Space.
In [ ]:
Copied!
```
# Create a NebulaGraph (version 3.5.0 or newer) cluster with:
# Option 0 for machines with Docker: `curl -fsSL nebula-up.siwei.io/install.sh | bash`
# Option 1 for Desktop: NebulaGraph Docker Extension https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext

# If not, create it with the following commands from NebulaGraph's console:
# CREATE SPACE llamaindex(vid_type=FIXED_STRING(256), partition_num=1, replica_factor=1);
# :sleep 10;
# USE llamaindex;
# CREATE TAG entity(name string);
# CREATE EDGE relationship(relationship string);
# :sleep 10;
# CREATE TAG INDEX entity_index ON entity(name(256));

%pip install ipython-ngql nebula3-python

os.environ["NEBULA_USER"] = "root"
os.environ["NEBULA_PASSWORD"] = "nebula"  # default is "nebula"
os.environ[
    "NEBULA_ADDRESS"
] = "127.0.0.1:9669"  # assumed we have NebulaGraph installed locally

space_name = "llamaindex"
edge_types, rel_prop_names = ["relationship"], [
    "relationship"
]  # default, could be omit if create from an empty kg
tags = ["entity"]  # default, could be omit if create from an empty kg

```

# Create a NebulaGraph (version 3.5.0 or newer) cluster with: # Option 0 for machines with Docker: `curl -fsSL nebula-up.siwei.io/install.sh | bash` # Option 1 for Desktop: NebulaGraph Docker Extension https://hub.docker.com/extensions/weygu/nebulagraph-dd-ext # If not, create it with the following commands from NebulaGraph's console: # CREATE SPACE llamaindex(vid_type=FIXED_STRING(256), partition_num=1, replica_factor=1); # :sleep 10; # USE llamaindex; # CREATE TAG entity(name string); # CREATE EDGE relationship(relationship string); # :sleep 10; # CREATE TAG INDEX entity_index ON entity(name(256)); %pip install ipython-ngql nebula3-python os.environ["NEBULA_USER"] = "root" os.environ["NEBULA_PASSWORD"] = "nebula" # default is "nebula" os.environ[ "NEBULA_ADDRESS" ] = "127.0.0.1:9669" # assumed we have NebulaGraph installed locally space_name = "llamaindex" edge_types, rel_prop_names = ["relationship"], [ "relationship" ] # default, could be omit if create from an empty kg tags = ["entity"] # default, could be omit if create from an empty kg
```
Requirement already satisfied: ipython-ngql in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (0.5)
Requirement already satisfied: nebula3-python in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (3.4.0)
Requirement already satisfied: Jinja2 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from ipython-ngql) (3.1.2)
Requirement already satisfied: pandas in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from ipython-ngql) (2.0.3)
Requirement already satisfied: httplib2>=0.20.0 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from nebula3-python) (0.22.0)
Requirement already satisfied: six>=1.16.0 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from nebula3-python) (1.16.0)
Requirement already satisfied: pytz>=2021.1 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from nebula3-python) (2023.3)
Requirement already satisfied: future>=0.18.0 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from nebula3-python) (0.18.3)
Requirement already satisfied: pyparsing!=3.0.0,!=3.0.1,!=3.0.2,!=3.0.3,<4,>=2.4.2 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from httplib2>=0.20.0->nebula3-python) (3.0.9)
Requirement already satisfied: MarkupSafe>=2.0 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from Jinja2->ipython-ngql) (2.1.3)
Requirement already satisfied: numpy>=1.20.3 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from pandas->ipython-ngql) (1.25.2)
Requirement already satisfied: tzdata>=2022.1 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from pandas->ipython-ngql) (2023.3)
Requirement already satisfied: python-dateutil>=2.8.2 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from pandas->ipython-ngql) (2.8.2)
WARNING: You are using pip version 21.2.4; however, version 23.2.1 is available.
You should consider upgrading via the '/Users/loganmarkewich/llama_index/llama-index/bin/python -m pip install --upgrade pip' command.
Note: you may need to restart the kernel to use updated packages.

```

Then we could instiatate a `NebulaGraphStore`, in order to create a `StorageContext`'s `graph_store` as it.
In [ ]:
Copied!
```
from llama_index.core import StorageContext
from llama_index.graph_stores.nebula import NebulaGraphStore

graph_store = NebulaGraphStore(
    space_name=space_name,
    edge_types=edge_types,
    rel_prop_names=rel_prop_names,
    tags=tags,
)
storage_context = StorageContext.from_defaults(graph_store=graph_store)

```

from llama_index.core import StorageContext from llama_index.graph_stores.nebula import NebulaGraphStore graph_store = NebulaGraphStore( space_name=space_name, edge_types=edge_types, rel_prop_names=rel_prop_names, tags=tags, ) storage_context = StorageContext.from_defaults(graph_store=graph_store)
Here, we assumed to have the same Knowledge Graph from this tutorial
## Perform Graph RAG Query¶
Finally, let's demo how to do Graph RAG towards an existing Knowledge Graph.
All we need to do is to use `RetrieverQueryEngine` and configure the retriver of it to be `KnowledgeGraphRAGRetriever`.
The `KnowledgeGraphRAGRetriever` performs the following steps:
  * Search related Entities of the quesion/task
  * Get SubGraph of those Entities (default 2-depth) from the KG
  * Build Context based on the SubGraph


Please note, the way to Search related Entities could be either Keyword extraction based or Embedding based, which is controlled by argument `retriever_mode` of the `KnowledgeGraphRAGRetriever`, and supported options are:
  * "keyword"
  * "embedding"(not yet implemented)
  * "keyword_embedding"(not yet implemented)


Here is the example on how to use `RetrieverQueryEngine` and `KnowledgeGraphRAGRetriever`:
In [ ]:
Copied!
```
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import KnowledgeGraphRAGRetriever

graph_rag_retriever = KnowledgeGraphRAGRetriever(
    storage_context=storage_context,
    verbose=True,
)

query_engine = RetrieverQueryEngine.from_args(
    graph_rag_retriever,
)

```

from llama_index.core.query_engine import RetrieverQueryEngine from llama_index.core.retrievers import KnowledgeGraphRAGRetriever graph_rag_retriever = KnowledgeGraphRAGRetriever( storage_context=storage_context, verbose=True, ) query_engine = RetrieverQueryEngine.from_args( graph_rag_retriever, )
Then we can query it like:
In [ ]:
Copied!
```
from IPython.display import display, Markdown

response = query_engine.query(
    "Tell me about Peter Quill?",
)
display(Markdown(f"<b>{response}</b>"))

```

from IPython.display import display, Markdown response = query_engine.query( "Tell me about Peter Quill?", ) display(Markdown(f"**{response}** "))
```
Entities processed: ['Star', 'Lord', 'Marvel', 'Quill', 'Galaxy', 'Guardians', 'Guardians of the Galaxy', 'Star-Lord', 'Peter Quill', 'Peter']
Entities processed: ['Star', 'Lord', 'Marvel', 'Quill', 'Galaxy', 'Guardians', 'Guardians of the Galaxy', 'Star-Lord', 'Peter Quill', 'Peter']
Graph RAG context:
The following are knowledge sequence in max depth 2 in the form of `subject predicate, object, predicate_next_hop, object_next_hop ...` extracted based on key entities as subject:
Guardians, is member of, Guardians, was experimented on, by the High Evolutionary
Guardians, is member of, Guardians, considered to tell, origins
Guardians, is member of, Guardians, origins, team-up movie
Guardians, is member of, Guardians, befriended, his fellow Batch 89 test subjects
Guardians, is member of, Guardians, sought to enhance and anthropomorphize animal lifeforms, to create an ideal society
Guardians, is member of, Guardians, is creator of, Rocket
Guardians, is member of, Guardians, is, Mantis
Guardians, is member of, Guardians, is half-sister of, Mantis
Guardians, is member of, Guardians, is, Kraglin
Guardians, is member of, Guardians, developed psionic abilities, after being abandoned in outer space
Guardians, is member of, Guardians, would portray, Cosmo
Guardians, is member of, Guardians, recalls, his past
Guardians, is member of, Guardians
Guardians, is member of, Guardians, focus on, third Guardians-centric film
Guardians, is member of, Guardians, is, Rocket
Guardians, is member of, Guardians, backstory, flashbacks
Guardians, is member of, Guardians, is former second-in-command of, Ravagers
Quill, is half-sister of, Mantis, is member of, Guardians
Quill, is half-sister of, Mantis, is, Mantis
Quill, is in a state of depression, following the appearance of a variant of his dead lover Gamora
Quill, is half-sister of, Mantis
Peter Quill, is leader of, Guardians of the Galaxy, is sequel to, Guardians of the Galaxy
Peter Quill, was raised by, a group of alien thieves and smugglers
Peter Quill, would return to the MCU, May 2021
Peter Quill, is leader of, Guardians of the Galaxy
Peter Quill, is half-human, half-Celestial
Peter Quill, was abducted from Earth, as a child
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, released in, Dolby Cinema
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, released on, Disney+
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, is sequel to, Guardians of the Galaxy Vol. 2

```

****
Peter Quill is the leader of the Guardians of the Galaxy and the main protagonist of the Guardians of the Galaxy films. He was raised by a group of alien thieves and smugglers, and was abducted from Earth as a child. He is half-human, half-Celestial, and has the ability to wield an energy weapon called the Infinity Stone. He is set to return to the MCU in May 2021.
In [ ]:
Copied!
```
response = await query_engine.aquery(
    "Tell me about Peter Quill?",
)
display(Markdown(f"<b>{response}</b>"))

```

response = await query_engine.aquery( "Tell me about Peter Quill?", ) display(Markdown(f"**{response}** "))
```
INFO:openai:message='OpenAI API response' path=https://api.openai.com/v1/completions processing_ms=611 request_id=1c07a89e18f19ac7bbc508507c2902d9 response_code=200
Entities processed: ['Star', 'Lord', 'Marvel', 'Quill', 'Galaxy', 'Guardians', 'Guardians of the Galaxy', 'Star-Lord', 'Peter Quill', 'Peter']
INFO:openai:message='OpenAI API response' path=https://api.openai.com/v1/completions processing_ms=992 request_id=6517cb63da3364acd33e816a9b3ee242 response_code=200
Entities processed: ['Star', 'Lord', 'Marvel', 'Quill', 'Galaxy', 'Guardians', 'Guardians of the Galaxy', 'Star-Lord', 'Peter Quill', 'Peter']
Graph RAG context:
The following are knowledge sequence in max depth 2 in the form of `subject predicate, object, predicate_next_hop, object_next_hop ...` extracted based on key entities as subject:
Guardians, is member of, Guardians, was experimented on, by the High Evolutionary
Guardians, is member of, Guardians, considered to tell, origins
Guardians, is member of, Guardians, origins, team-up movie
Guardians, is member of, Guardians, befriended, his fellow Batch 89 test subjects
Guardians, is member of, Guardians, sought to enhance and anthropomorphize animal lifeforms, to create an ideal society
Guardians, is member of, Guardians, is creator of, Rocket
Guardians, is member of, Guardians, is, Mantis
Guardians, is member of, Guardians, is half-sister of, Mantis
Guardians, is member of, Guardians, is, Kraglin
Guardians, is member of, Guardians, developed psionic abilities, after being abandoned in outer space
Guardians, is member of, Guardians, would portray, Cosmo
Guardians, is member of, Guardians, recalls, his past
Guardians, is member of, Guardians
Guardians, is member of, Guardians, focus on, third Guardians-centric film
Guardians, is member of, Guardians, is, Rocket
Guardians, is member of, Guardians, backstory, flashbacks
Guardians, is member of, Guardians, is former second-in-command of, Ravagers
Quill, is half-sister of, Mantis, is member of, Guardians
Quill, is half-sister of, Mantis, is, Mantis
Quill, is in a state of depression, following the appearance of a variant of his dead lover Gamora
Quill, is half-sister of, Mantis
Peter Quill, is leader of, Guardians of the Galaxy, is sequel to, Guardians of the Galaxy
Peter Quill, was raised by, a group of alien thieves and smugglers
Peter Quill, would return to the MCU, May 2021
Peter Quill, is leader of, Guardians of the Galaxy
Peter Quill, is half-human, half-Celestial
Peter Quill, was abducted from Earth, as a child
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, released in, Dolby Cinema
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, released on, Disney+
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, is sequel to, Guardians of the Galaxy Vol. 2
INFO:openai:message='OpenAI API response' path=https://api.openai.com/v1/completions processing_ms=2384 request_id=b5a7e601affa751fbc7f957f3359a238 response_code=200

```

****
Peter Quill is the leader of the Guardians of the Galaxy and the main protagonist of the Guardians of the Galaxy films. He was raised by a group of alien thieves and smugglers, and was abducted from Earth as a child. He is half-human, half-Celestial, and has the ability to wield an energy weapon called the Infinity Stone. He is set to return to the MCU in May 2021.
## Include nl2graphquery as Context in Graph RAG¶
The nature of (Sub)Graph RAG and nl2graphquery are different. No one is better than the other but just when one fits more in certain type of questions. To understand more on how they differ from the other, see this demo comparing the two.
While in real world cases, we may not always know which approach works better, thus, one way to best leverage KG in RAG are fetching both retrieval results as context and letting LLM + Prompt generate answer with them all being involved.
So, optionally, we could choose to synthesise answer from two piece of retrieved context from KG:
  * Graph RAG, the default retrieval method, which extracts subgraph that's related to the key entities in the question.
  * NL2GraphQuery, generate Knowledge Graph Query based on query and the Schema of the Knowledge Graph, which is by default switched off.


We could set `with_nl2graphquery=True` to enable it like:
In [ ]:
Copied!
```
graph_rag_retriever_with_nl2graphquery = KnowledgeGraphRAGRetriever(
    storage_context=storage_context,
    verbose=True,
    with_nl2graphquery=True,
)

query_engine_with_nl2graphquery = RetrieverQueryEngine.from_args(
    graph_rag_retriever_with_nl2graphquery,
)

```

graph_rag_retriever_with_nl2graphquery = KnowledgeGraphRAGRetriever( storage_context=storage_context, verbose=True, with_nl2graphquery=True, ) query_engine_with_nl2graphquery = RetrieverQueryEngine.from_args( graph_rag_retriever_with_nl2graphquery, )
In [ ]:
Copied!
```
response = query_engine_with_nl2graphquery.query(
    "What do you know about Peter Quill?",
)
display(Markdown(f"<b>{response}</b>"))

```

response = query_engine_with_nl2graphquery.query( "What do you know about Peter Quill?", ) display(Markdown(f"**{response}** "))
```
Graph Store Query:
```
MATCH (p:`entity`)-[:`relationship`]->(m:`entity`) WHERE p.`entity`.`name` == 'Peter Quill'
RETURN m.`entity`.`name`;
```
Graph Store Response:
{'m.entity.name': ['May 2021', 'as a child', 'Guardians of the Galaxy', 'a group of alien thieves and smugglers', 'half-Celestial']}
Entities processed: ['Star', 'Lord', 'Marvel', 'Quill', 'Galaxy', 'Guardians', 'Guardians of the Galaxy', 'Star-Lord', 'Peter Quill', 'Peter']
Entities processed: ['Star', 'Lord', 'Marvel', 'Quill', 'Galaxy', 'Guardians', 'Guardians of the Galaxy', 'Star-Lord', 'Peter Quill', 'Peter']
Graph RAG context:
The following are knowledge sequence in max depth 2 in the form of `subject predicate, object, predicate_next_hop, object_next_hop ...` extracted based on key entities as subject:
Guardians, is member of, Guardians, was experimented on, by the High Evolutionary
Guardians, is member of, Guardians, considered to tell, origins
Guardians, is member of, Guardians, origins, team-up movie
Guardians, is member of, Guardians, befriended, his fellow Batch 89 test subjects
Guardians, is member of, Guardians, sought to enhance and anthropomorphize animal lifeforms, to create an ideal society
Guardians, is member of, Guardians, is creator of, Rocket
Guardians, is member of, Guardians, is, Mantis
Guardians, is member of, Guardians, is half-sister of, Mantis
Guardians, is member of, Guardians, is, Kraglin
Guardians, is member of, Guardians, developed psionic abilities, after being abandoned in outer space
Guardians, is member of, Guardians, would portray, Cosmo
Guardians, is member of, Guardians, recalls, his past
Guardians, is member of, Guardians
Guardians, is member of, Guardians, focus on, third Guardians-centric film
Guardians, is member of, Guardians, is, Rocket
Guardians, is member of, Guardians, backstory, flashbacks
Guardians, is member of, Guardians, is former second-in-command of, Ravagers
Quill, is half-sister of, Mantis, is member of, Guardians
Quill, is half-sister of, Mantis, is, Mantis
Quill, is in a state of depression, following the appearance of a variant of his dead lover Gamora
Quill, is half-sister of, Mantis
Peter Quill, is leader of, Guardians of the Galaxy, is sequel to, Guardians of the Galaxy
Peter Quill, was raised by, a group of alien thieves and smugglers
Peter Quill, would return to the MCU, May 2021
Peter Quill, is leader of, Guardians of the Galaxy
Peter Quill, is half-human, half-Celestial
Peter Quill, was abducted from Earth, as a child
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, released in, Dolby Cinema
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, released on, Disney+
Guardians of the Galaxy, is sequel to, Guardians of the Galaxy, is sequel to, Guardians of the Galaxy Vol. 2

```

****
Peter Quill is the leader of the Guardians of the Galaxy and was abducted from Earth as a child. He is half-human and half-Celestial, and was raised by a group of alien thieves and smugglers. He would return to the MCU in May 2021.
And let's check the response's metadata to know more details of the retrival of Graph RAG with nl2graphquery by inspecting `response.metadata`.
  * **text2Cypher** , it generates a Cypher Query towards the answer as the context.


```
Graph Store Query: MATCH (e:`entity`)-[r:`relationship`]->(e2:`entity`)
WHERE e.`entity`.`name` == 'Peter Quill'
RETURN e2.`entity`.`name`

```

  * **SubGraph RAG** , it get the SubGraph of 'Peter Quill' to build the context.
  * Finally, it combined the two nodes of context, to synthesize the answer.


In [ ]:
Copied!
```
import pprint

pp = pprint.PrettyPrinter()
pp.pprint(response.metadata)

```

import pprint pp = pprint.PrettyPrinter() pp.pprint(response.metadata)
```
{'46faf6d6-8a71-44c8-ae81-794e71a62fbc': {'graph_schema': 'Node properties: '
                                                          "[{'tag': 'entity', "
                                                          "'properties': "
                                                          "[('name', "
                                                          "'string')]}]\n"
                                                          'Edge properties: '
                                                          "[{'edge': "
                                                          "'relationship', "
                                                          "'properties': "
                                                          "[('relationship', "
                                                          "'string')]}]\n"
                                                          'Relationships: '
                                                          "['(:entity)-[:relationship]->(:entity)']\n",
                                          'graph_store_query': '```\n'
                                                               'MATCH '
                                                               '(p:`entity`)-[:`relationship`]->(m:`entity`) '
                                                               'WHERE '
                                                               'p.`entity`.`name` '
                                                               "== 'Peter "
                                                               "Quill'\n"
                                                               'RETURN '
                                                               'm.`entity`.`name`;\n'
                                                               '```',
                                          'graph_store_response': {'m.entity.name': ['May '
                                                                                     '2021',
                                                                                     'as '
                                                                                     'a '
                                                                                     'child',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy',
                                                                                     'a '
                                                                                     'group '
                                                                                     'of '
                                                                                     'alien '
                                                                                     'thieves '
                                                                                     'and '
                                                                                     'smugglers',
                                                                                     'half-Celestial']},
                                          'query_str': 'What do you know about '
                                                       'Peter Quill?'},
 'def19bbf-d8ac-43b2-a121-675748cc9454': {'kg_rel_map': {'Guardians': ['Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'was '
                                                                       'experimented '
                                                                       'on, by '
                                                                       'the '
                                                                       'High '
                                                                       'Evolutionary',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'considered '
                                                                       'to '
                                                                       'tell, '
                                                                       'origins',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'origins, '
                                                                       'team-up '
                                                                       'movie',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'befriended, '
                                                                       'his '
                                                                       'fellow '
                                                                       'Batch '
                                                                       '89 '
                                                                       'test '
                                                                       'subjects',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'sought '
                                                                       'to '
                                                                       'enhance '
                                                                       'and '
                                                                       'anthropomorphize '
                                                                       'animal '
                                                                       'lifeforms, '
                                                                       'to '
                                                                       'create '
                                                                       'an '
                                                                       'ideal '
                                                                       'society',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'is '
                                                                       'creator '
                                                                       'of, '
                                                                       'Rocket',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'is, '
                                                                       'Mantis',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'is '
                                                                       'half-sister '
                                                                       'of, '
                                                                       'Mantis',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'is, '
                                                                       'Kraglin',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'developed '
                                                                       'psionic '
                                                                       'abilities, '
                                                                       'after '
                                                                       'being '
                                                                       'abandoned '
                                                                       'in '
                                                                       'outer '
                                                                       'space',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'would '
                                                                       'portray, '
                                                                       'Cosmo',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'recalls, '
                                                                       'his '
                                                                       'past',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'focus '
                                                                       'on, '
                                                                       'third '
                                                                       'Guardians-centric '
                                                                       'film',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'is, '
                                                                       'Rocket',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'backstory, '
                                                                       'flashbacks',
                                                                       'Guardians, '
                                                                       'is '
                                                                       'member '
                                                                       'of, '
                                                                       'Guardians, '
                                                                       'is '
                                                                       'former '
                                                                       'second-in-command '
                                                                       'of, '
                                                                       'Ravagers'],
                                                         'Guardians of the Galaxy': ['Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'in, '
                                                                                     'Dolby '
                                                                                     'Cinema',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'on, '
                                                                                     'Disney+',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy '
                                                                                     'Vol. '
                                                                                     '2',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'in, '
                                                                                     '3D',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'in, '
                                                                                     '4DX',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'grossed, '
                                                                                     '$32 '
                                                                                     'million '
                                                                                     'in '
                                                                                     'its '
                                                                                     'third '
                                                                                     'weekend',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'leader '
                                                                                     'of, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'in, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy '
                                                                                     'Vol. '
                                                                                     '3',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'wrote '
                                                                                     'and '
                                                                                     'directed, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy '
                                                                                     'Vol. '
                                                                                     '3',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is, '
                                                                                     'American '
                                                                                     'superhero '
                                                                                     'film',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'grossed, '
                                                                                     '$845.4 '
                                                                                     'million',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'was '
                                                                                     'fired '
                                                                                     'from, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy '
                                                                                     'Vol. '
                                                                                     '3',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'leader '
                                                                                     'of, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'was '
                                                                                     'abducted '
                                                                                     'from '
                                                                                     'Earth, '
                                                                                     'as '
                                                                                     'a '
                                                                                     'child',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'grossed, '
                                                                                     '$359 '
                                                                                     'million '
                                                                                     'in '
                                                                                     'the '
                                                                                     'United '
                                                                                     'States '
                                                                                     'and '
                                                                                     'Canada',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'on, '
                                                                                     'digital '
                                                                                     'download',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'in, '
                                                                                     'IMAX',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'leader '
                                                                                     'of, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'half-human, '
                                                                                     'half-Celestial',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'leader '
                                                                                     'of, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'was '
                                                                                     'raised '
                                                                                     'by, '
                                                                                     'a '
                                                                                     'group '
                                                                                     'of '
                                                                                     'alien '
                                                                                     'thieves '
                                                                                     'and '
                                                                                     'smugglers',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'screened '
                                                                                     'at, '
                                                                                     'Dongdaemun '
                                                                                     'Design '
                                                                                     'Plaza',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'in, '
                                                                                     'ScreenX',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'leader '
                                                                                     'of, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'would '
                                                                                     'return '
                                                                                     'to '
                                                                                     'the '
                                                                                     'MCU, '
                                                                                     'May '
                                                                                     '2021',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'grossed, '
                                                                                     '$486.4 '
                                                                                     'million '
                                                                                     'in '
                                                                                     'other '
                                                                                     'territories',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'on, '
                                                                                     'Ultra '
                                                                                     'HD '
                                                                                     'Blu-ray',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'on, '
                                                                                     'DVD',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'grossed, '
                                                                                     '$92 '
                                                                                     'million '
                                                                                     'for '
                                                                                     'a '
                                                                                     'drop '
                                                                                     'of '
                                                                                     '40% '
                                                                                     'from '
                                                                                     'its '
                                                                                     'opening '
                                                                                     'weekend',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'premiered '
                                                                                     'at, '
                                                                                     'Disneyland '
                                                                                     'Paris',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'released '
                                                                                     'on, '
                                                                                     'Blu-ray',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'could '
                                                                                     'happen, '
                                                                                     'April '
                                                                                     '2017',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'made, '
                                                                                     '$48.2 '
                                                                                     'million '
                                                                                     'on '
                                                                                     'its '
                                                                                     'first '
                                                                                     'day',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'grossed, '
                                                                                     '$168.1 '
                                                                                     'million '
                                                                                     'in '
                                                                                     'its '
                                                                                     'opening '
                                                                                     'weekend',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'debuted '
                                                                                     'with, '
                                                                                     '$118.4 '
                                                                                     'million',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'would '
                                                                                     'likely '
                                                                                     'center '
                                                                                     'on, '
                                                                                     'new '
                                                                                     'group '
                                                                                     'of '
                                                                                     'characters',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'retained '
                                                                                     'the '
                                                                                     'top '
                                                                                     'spot '
                                                                                     'at '
                                                                                     'the '
                                                                                     'box '
                                                                                     'office '
                                                                                     'with, '
                                                                                     '$62 '
                                                                                     'million',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'be '
                                                                                     'his '
                                                                                     'last '
                                                                                     'Guardians '
                                                                                     'film, '
                                                                                     'September '
                                                                                     '2019',
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'is '
                                                                                     'sequel '
                                                                                     'to, '
                                                                                     'Guardians '
                                                                                     'of '
                                                                                     'the '
                                                                                     'Galaxy, '
                                                                                     'nominated '
                                                                                     'for, '
                                                                                     'Best '
                                                                                     'Picture'],
                                                         'Marvel': ['Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Marvel, '
                                                                    'stated, '
                                                                    'that in '
                                                                    'addition '
                                                                    'to having '
                                                                    'the  '
                                                                    'basic '
                                                                    'story  '
                                                                    'for '
                                                                    'Guardians '
                                                                    'of the '
                                                                    'Galaxy '
                                                                    'Vol.2 '
                                                                    '(2017) '
                                                                    'while '
                                                                    'working '
                                                                    'on the '
                                                                    'first '
                                                                    'film',
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Marvel, '
                                                                    'was '
                                                                    'unsure, '
                                                                    'if he '
                                                                    'would be '
                                                                    'involved '
                                                                    'with a '
                                                                    'third '
                                                                    'Guardians '
                                                                    'film',
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Marvel, '
                                                                    'was '
                                                                    'privately '
                                                                    'notified '
                                                                    'by, Horn',
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Guardians '
                                                                    'of the '
                                                                    'Galaxy '
                                                                    'Vol. 3',
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Marvel',
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Marvel, '
                                                                    'wrote and '
                                                                    'directed, '
                                                                    'Guardians '
                                                                    'of the '
                                                                    'Galaxy '
                                                                    'Vol. 3',
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Disney',
                                                                    'Marvel, '
                                                                    'was fired '
                                                                    'from, '
                                                                    'Marvel, '
                                                                    'could '
                                                                    'return as '
                                                                    'director '
                                                                    'for, '
                                                                    'Vol.3'],
                                                         'Peter Quill': ['Peter '
                                                                         'Quill, '
                                                                         'is '
                                                                         'leader '
                                                                         'of, '
                                                                         'Guardians '
                                                                         'of '
                                                                         'the '
                                                                         'Galaxy, '
                                                                         'is '
                                                                         'sequel '
                                                                         'to, '
                                                                         'Guardians '
                                                                         'of '
                                                                         'the '
                                                                         'Galaxy',
                                                                         'Peter '
                                                                         'Quill, '
                                                                         'was '
                                                                         'raised '
                                                                         'by, '
                                                                         'a '
                                                                         'group '
                                                                         'of '
                                                                         'alien '
                                                                         'thieves '
                                                                         'and '
                                                                         'smugglers',
                                                                         'Peter '
                                                                         'Quill, '
                                                                         'would '
                                                                         'return '
                                                                         'to '
                                                                         'the '
                                                                         'MCU, '
                                                                         'May '
                                                                         '2021',
                                                                         'Peter '
                                                                         'Quill, '
                                                                         'is '
                                                                         'leader '
                                                                         'of, '
                                                                         'Guardians '
                                                                         'of '
                                                                         'the '
                                                                         'Galaxy',
                                                                         'Peter '
                                                                         'Quill, '
                                                                         'is '
                                                                         'half-human, '
                                                                         'half-Celestial',
                                                                         'Peter '
                                                                         'Quill, '
                                                                         'was '
                                                                         'abducted '
                                                                         'from '
                                                                         'Earth, '
                                                                         'as a '
                                                                         'child'],
                                                         'Quill': ['Quill, is '
                                                                   'half-sister '
                                                                   'of, '
                                                                   'Mantis, is '
                                                                   'member of, '
                                                                   'Guardians',
                                                                   'Quill, is '
                                                                   'half-sister '
                                                                   'of, '
                                                                   'Mantis, '
                                                                   'is, Mantis',
                                                                   'Quill, is '
                                                                   'in a state '
                                                                   'of '
                                                                   'depression, '
                                                                   'following '
                                                                   'the '
                                                                   'appearance '
                                                                   'of a '
                                                                   'variant of '
                                                                   'his dead '
                                                                   'lover '
                                                                   'Gamora',
                                                                   'Quill, is '
                                                                   'half-sister '
                                                                   'of, '
                                                                   'Mantis']},
                                          'kg_rel_text': ['Guardians, is '
                                                          'member of, '
                                                          'Guardians, was '
                                                          'experimented on, by '
                                                          'the High '
                                                          'Evolutionary',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, '
                                                          'considered to tell, '
                                                          'origins',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, origins, '
                                                          'team-up movie',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, '
                                                          'befriended, his '
                                                          'fellow Batch 89 '
                                                          'test subjects',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, sought '
                                                          'to enhance and '
                                                          'anthropomorphize '
                                                          'animal lifeforms, '
                                                          'to create an ideal '
                                                          'society',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, is '
                                                          'creator of, Rocket',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, is, '
                                                          'Mantis',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, is '
                                                          'half-sister of, '
                                                          'Mantis',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, is, '
                                                          'Kraglin',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, '
                                                          'developed psionic '
                                                          'abilities, after '
                                                          'being abandoned in '
                                                          'outer space',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, would '
                                                          'portray, Cosmo',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, recalls, '
                                                          'his past',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, focus '
                                                          'on, third '
                                                          'Guardians-centric '
                                                          'film',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, is, '
                                                          'Rocket',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, '
                                                          'backstory, '
                                                          'flashbacks',
                                                          'Guardians, is '
                                                          'member of, '
                                                          'Guardians, is '
                                                          'former '
                                                          'second-in-command '
                                                          'of, Ravagers',
                                                          'Quill, is '
                                                          'half-sister of, '
                                                          'Mantis, is member '
                                                          'of, Guardians',
                                                          'Quill, is '
                                                          'half-sister of, '
                                                          'Mantis, is, Mantis',
                                                          'Quill, is in a '
                                                          'state of '
                                                          'depression, '
                                                          'following the '
                                                          'appearance of a '
                                                          'variant of his dead '
                                                          'lover Gamora',
                                                          'Quill, is '
                                                          'half-sister of, '
                                                          'Mantis',
                                                          'Peter Quill, is '
                                                          'leader of, '
                                                          'Guardians of the '
                                                          'Galaxy, is sequel '
                                                          'to, Guardians of '
                                                          'the Galaxy',
                                                          'Peter Quill, was '
                                                          'raised by, a group '
                                                          'of alien thieves '
                                                          'and smugglers',
                                                          'Peter Quill, would '
                                                          'return to the MCU, '
                                                          'May 2021',
                                                          'Peter Quill, is '
                                                          'leader of, '
                                                          'Guardians of the '
                                                          'Galaxy',
                                                          'Peter Quill, is '
                                                          'half-human, '
                                                          'half-Celestial',
                                                          'Peter Quill, was '
                                                          'abducted from '
                                                          'Earth, as a child',
                                                          'Guardians of the '
                                                          'Galaxy, is sequel '
                                                          'to, Guardians of '
                                                          'the Galaxy, '
                                                          'released in, Dolby '
                                                          'Cinema',
                                                          'Guardians of the '
                                                          'Galaxy, is sequel '
                                                          'to, Guardians of '
                                                          'the Galaxy, '
                                                          'released on, '
                                                          'Disney+',
                                                          'Guardians of the '
                                                          'Galaxy, is sequel '
                                                          'to, Guardians of '
                                                          'the Galaxy, is '
                                                          'sequel to, '
                                                          'Guardians of the '
                                                          'Galaxy Vol. 2']}}

```

