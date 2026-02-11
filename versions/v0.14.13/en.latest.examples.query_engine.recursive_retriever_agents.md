![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Recursive Retriever + Document Agents¶
This guide shows how to combine recursive retrieval and "document agents" for advanced decision making over heterogeneous documents.
There are two motivating factors that lead to solutions for better retrieval:
  * Decoupling retrieval embeddings from chunk-based synthesis. Oftentimes fetching documents by their summaries will return more relevant context to queries rather than raw chunks. This is something that recursive retrieval directly allows.
  * Within a document, users may need to dynamically perform tasks beyond fact-based question-answering. We introduce the concept of "document agents" - agents that have access to both vector search and summary tools for a given document.


### Setup and Download Data¶
In this section, we'll define imports and then download Wikipedia articles about different cities. Each article is stored separately.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-agent-openai

```

%pip install llama-index-llms-openai %pip install llama-index-agent-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import SummaryIndex
from llama_index.core.schema import IndexNode
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.llms.openai import OpenAI

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core import SummaryIndex from llama_index.core.schema import IndexNode from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.llms.openai import OpenAI
In [ ]:
Copied!
```
wiki_titles = ["Toronto", "Seattle", "Chicago", "Boston", "Houston"]

```

wiki_titles = ["Toronto", "Seattle", "Chicago", "Boston", "Houston"]
In [ ]:
Copied!
```
from pathlib import Path

import requests

for title in wiki_titles:
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            # 'exintro': True,
            "explaintext": True,
        },
    ).json()
    page = next(iter(response["query"]["pages"].values()))
    wiki_text = page["extract"]

    data_path = Path("data")
    if not data_path.exists():
        Path.mkdir(data_path)

    with open(data_path / f"{title}.txt", "w") as fp:
        fp.write(wiki_text)

```

from pathlib import Path import requests for title in wiki_titles: response = requests.get( "https://en.wikipedia.org/w/api.php", params={ "action": "query", "format": "json", "titles": title, "prop": "extracts", # 'exintro': True, "explaintext": True, }, ).json() page = next(iter(response["query"]["pages"].values())) wiki_text = page["extract"] data_path = Path("data") if not data_path.exists(): Path.mkdir(data_path) with open(data_path / f"{title}.txt", "w") as fp: fp.write(wiki_text)
In [ ]:
Copied!
```
# Load all wiki documents
city_docs = {}
for wiki_title in wiki_titles:
    city_docs[wiki_title] = SimpleDirectoryReader(
        input_files=[f"data/{wiki_title}.txt"]
    ).load_data()

```

# Load all wiki documents city_docs = {} for wiki_title in wiki_titles: city_docs[wiki_title] = SimpleDirectoryReader( input_files=[f"data/{wiki_title}.txt"] ).load_data()
Define LLM + Service Context + Callback Manager
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")

```

from llama_index.core import Settings Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
## Build Document Agent for each Document¶
In this section we define "document agents" for each document.
First we define both a vector index (for semantic search) and summary index (for summarization) for each document. The two query engines are then converted into tools that are passed to an OpenAI function calling agent.
This document agent can dynamically choose to perform semantic search or summarization within a given document.
We create a separate document agent for each city.
In [ ]:
Copied!
```
from llama_index.agent.openai import OpenAIAgent

# Build agents dictionary
agents = {}

for wiki_title in wiki_titles:
    # build vector index
    vector_index = VectorStoreIndex.from_documents(
        city_docs[wiki_title],
    )
    # build summary index
    summary_index = SummaryIndex.from_documents(
        city_docs[wiki_title],
    )
    # define query engines
    vector_query_engine = vector_index.as_query_engine()
    list_query_engine = summary_index.as_query_engine()

    # define tools
    query_engine_tools = [
        QueryEngineTool(
            query_engine=vector_query_engine,
            metadata=ToolMetadata(
                name="vector_tool",
                description=(
                    f"Useful for retrieving specific context from {wiki_title}"
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=list_query_engine,
            metadata=ToolMetadata(
                name="summary_tool",
                description=(
                    "Useful for summarization questions related to"
                    f" {wiki_title}"
                ),
            ),
        ),
    ]

    # build agent
    function_llm = OpenAI(model="gpt-3.5-turbo-0613")
    agent = OpenAIAgent.from_tools(
        query_engine_tools,
        llm=function_llm,
        verbose=True,
    )

    agents[wiki_title] = agent

```

from llama_index.agent.openai import OpenAIAgent # Build agents dictionary agents = {} for wiki_title in wiki_titles: # build vector index vector_index = VectorStoreIndex.from_documents( city_docs[wiki_title], ) # build summary index summary_index = SummaryIndex.from_documents( city_docs[wiki_title], ) # define query engines vector_query_engine = vector_index.as_query_engine() list_query_engine = summary_index.as_query_engine() # define tools query_engine_tools = [ QueryEngineTool( query_engine=vector_query_engine, metadata=ToolMetadata( name="vector_tool", description=( f"Useful for retrieving specific context from {wiki_title}" ), ), ), QueryEngineTool( query_engine=list_query_engine, metadata=ToolMetadata( name="summary_tool", description=( "Useful for summarization questions related to" f" {wiki_title}" ), ), ), ] # build agent function_llm = OpenAI(model="gpt-3.5-turbo-0613") agent = OpenAIAgent.from_tools( query_engine_tools, llm=function_llm, verbose=True, ) agents[wiki_title] = agent
## Build Composable Retriever over these Agents¶
Now we define a set of summary nodes, where each node links to the corresponding Wikipedia city article. We then define a composable retriever + query engine on top of these Nodes to route queries down to a given node, which will in turn route it to the relevant document agent.
In [ ]:
Copied!
```
# define top-level nodes
objects = []
for wiki_title in wiki_titles:
    # define index node that links to these agents
    wiki_summary = (
        f"This content contains Wikipedia articles about {wiki_title}. Use"
        " this index if you need to lookup specific facts about"
        f" {wiki_title}.\nDo not use this index if you want to analyze"
        " multiple cities."
    )
    node = IndexNode(
        text=wiki_summary, index_id=wiki_title, obj=agents[wiki_title]
    )
    objects.append(node)

```

# define top-level nodes objects = [] for wiki_title in wiki_titles: # define index node that links to these agents wiki_summary = ( f"This content contains Wikipedia articles about {wiki_title}. Use" " this index if you need to lookup specific facts about" f" {wiki_title}.\nDo not use this index if you want to analyze" " multiple cities." ) node = IndexNode( text=wiki_summary, index_id=wiki_title, obj=agents[wiki_title] ) objects.append(node)
In [ ]:
Copied!
```
# define top-level retriever
vector_index = VectorStoreIndex(
    objects=objects,
)
query_engine = vector_index.as_query_engine(similarity_top_k=1, verbose=True)

```

# define top-level retriever vector_index = VectorStoreIndex( objects=objects, ) query_engine = vector_index.as_query_engine(similarity_top_k=1, verbose=True)
## Running Example Queries¶
In [ ]:
Copied!
```
# should use Boston agent -> vector tool
response = query_engine.query("Tell me about the sports teams in Boston")

```

# should use Boston agent -> vector tool response = query_engine.query("Tell me about the sports teams in Boston")
```
Retrieval entering Boston: OpenAIAgent
Retrieving from object OpenAIAgent with query Tell me about the sports teams in Boston
Added user message to memory: Tell me about the sports teams in Boston

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Boston is home to several professional sports teams across different leagues, including a successful baseball team in Major League Baseball, a highly successful American football team in the National Football League, one of the most successful basketball teams in the NBA, a professional ice hockey team in the National Hockey League, and a professional soccer team in Major League Soccer. These teams have a rich history, passionate fan bases, and have achieved great success both locally and nationally.

```

In [ ]:
Copied!
```
# should use Houston agent -> vector tool
response = query_engine.query("Tell me about the sports teams in Houston")

```

# should use Houston agent -> vector tool response = query_engine.query("Tell me about the sports teams in Houston")
```
Retrieval entering Houston: OpenAIAgent
Retrieving from object OpenAIAgent with query Tell me about the sports teams in Houston
Added user message to memory: Tell me about the sports teams in Houston

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Houston is home to several professional sports teams across different leagues, including the Houston Texans in the NFL, the Houston Rockets in the NBA, the Houston Astros in MLB, the Houston Dynamo in MLS, and the Houston Dash in NWSL. These teams compete in football, basketball, baseball, soccer, and women's soccer respectively, and have achieved various levels of success in their respective leagues. Additionally, the city also has minor league baseball, hockey, and other sports teams that cater to sports enthusiasts.

```

In [ ]:
Copied!
```
# should use Seattle agent -> summary tool
response = query_engine.query(
    "Give me a summary on all the positive aspects of Chicago"
)

```

# should use Seattle agent -> summary tool response = query_engine.query( "Give me a summary on all the positive aspects of Chicago" )
```
Retrieval entering Chicago: OpenAIAgent
Retrieving from object OpenAIAgent with query Give me a summary on all the positive aspects of Chicago
Added user message to memory: Give me a summary on all the positive aspects of Chicago
=== Calling Function ===
Calling function: summary_tool with args: {
  "input": "positive aspects of Chicago"
}
Got output: Chicago is recognized for its robust economy, acting as a key hub for finance, culture, commerce, industry, education, technology, telecommunications, and transportation. It stands out in the derivatives market and is a top-ranking city in terms of gross domestic product. Chicago is a favored destination for tourists, known for its rich art scene covering visual arts, literature, film, theater, comedy, food, dance, and music. The city hosts prestigious educational institutions and professional sports teams across different leagues.
========================


```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Chicago is known for its strong economy with a focus on finance, culture, commerce, industry, education, technology, telecommunications, and transportation. It is a major player in the derivatives market and boasts a high gross domestic product. The city is a popular tourist destination with a vibrant art scene that includes visual arts, literature, film, theater, comedy, food, dance, and music. Additionally, Chicago is home to prestigious educational institutions and professional sports teams across various leagues.

```

