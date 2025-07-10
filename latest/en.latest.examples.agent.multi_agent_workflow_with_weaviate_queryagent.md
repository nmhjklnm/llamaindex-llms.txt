# Multi-Agent Workflow with Weaviate QueryAgent¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In this example, we will be building a LlamaIndex Agent Workflow that ends up being a multi-agent system that aims to be a Docs Assistant capable of:
  * Writing new content to a "LlamaIndexDocs" collection in Weaviate
  * Writing new content to a "WeaviateDocs" collection in Weaviate
  * Using the Weaviate `QueryAgent` to answer questions based on the contents of these collections.


The `QueryAgent` is a full agent prodcut by Weaviate, that is capable of doing regular search, as well as aggregations over the collections you give it access to. Our 'orchestrator' agent will decide when to invoke the Weaviate QueryAgent, leaving the job of creating Weaviate specific search queries to it.
**Things you will need:**
  * An OpenAI API key (or switch to another provider and adjust the code below)
  * A Weaviate sandbox (this is free)
  * Your Weaviate sandbox URL and API key


![Workflow Overview](https://docs.llamaindex.ai/en/latest/_static/agents/workflow-weaviate-multiagent.png)
## Install & Import Dependencies¶
In [ ]:
Copied!
```
!pip install llama-index-core llama-index-utils-workflow weaviate-client[agents] llama-index-llms-openai llama-index-readers-web

```

!pip install llama-index-core llama-index-utils-workflow weaviate-client[agents] llama-index-llms-openai llama-index-readers-web
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    Workflow,
    step,
    Event,
    Context,
)
from llama_index.utils.workflow import draw_all_possible_flows
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent

from enum import Enum
from pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI
from typing import List, Union
import json

import weaviate
from weaviate.auth import Auth
from weaviate.agents.query import QueryAgent
from weaviate.classes.config import Configure, Property, DataType

import os
from getpass import getpass

```

from llama_index.core.workflow import ( StartEvent, StopEvent, Workflow, step, Event, Context, ) from llama_index.utils.workflow import draw_all_possible_flows from llama_index.readers.web import SimpleWebPageReader from llama_index.core.llms import ChatMessage from llama_index.core.tools import FunctionTool from llama_index.llms.openai import OpenAI from llama_index.core.agent.workflow import FunctionAgent from enum import Enum from pydantic import BaseModel, Field from llama_index.llms.openai import OpenAI from typing import List, Union import json import weaviate from weaviate.auth import Auth from weaviate.agents.query import QueryAgent from weaviate.classes.config import Configure, Property, DataType import os from getpass import getpass
## Set up Weaviate¶
To use the Weaviate Query Agent, first, create a Weaviate Cloud account👇
  1. Create Serverless Weaviate Cloud account and set up a free Sandbox
  2. Go to 'Embedding' and enable it, by default, this will make it so that we use `Snowflake/snowflake-arctic-embed-l-v2.0` as the embedding model
  3. Take note of the `WEAVIATE_URL` and `WEAVIATE_API_KEY` to connect to your cluster below


> Info: We recommend using Weaviate Embeddings so you do not have to provide any extra keys for external embedding providers.
In [ ]:
Copied!
```
if "WEAVIATE_API_KEY" not in os.environ:
    os.environ["WEAVIATE_API_KEY"] = getpass("Add Weaviate API Key")
if "WEAVIATE_URL" not in os.environ:
    os.environ["WEAVIATE_URL"] = getpass("Add Weaviate URL")

```

if "WEAVIATE_API_KEY" not in os.environ: os.environ["WEAVIATE_API_KEY"] = getpass("Add Weaviate API Key") if "WEAVIATE_URL" not in os.environ: os.environ["WEAVIATE_URL"] = getpass("Add Weaviate URL")
In [ ]:
Copied!
```
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.environ.get("WEAVIATE_URL"),
    auth_credentials=Auth.api_key(os.environ.get("WEAVIATE_API_KEY")),
)

```

client = weaviate.connect_to_weaviate_cloud( cluster_url=os.environ.get("WEAVIATE_URL"), auth_credentials=Auth.api_key(os.environ.get("WEAVIATE_API_KEY")), )
### Create WeaviateDocs and LlamaIndexDocs Collections¶
The helper function below will create a "WeaviateDocs" and "LlamaIndexDocs" collection in Weaviate (if they don't exist already). It will also set up a `QueryAgent` that has access to both of these collections.
The Weaviate `QueryAgent` is designed to be able to query Weviate Collections for both regular search and aggregations, and also handles the burden of creating the Weaviate specific queries internally.
The Agent will use the collection descriptions, as well as the property descriptions while formilating the queries.
In [ ]:
Copied!
```
def fresh_setup_weaviate(client):
    if client.collections.exists("WeaviateDocs"):
        client.collections.delete("WeaviateDocs")
    client.collections.create(
        "WeaviateDocs",
        description="A dataset with the contents of Weaviate technical Docs and website",
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
        properties=[
            Property(
                name="url",
                data_type=DataType.TEXT,
                description="the source URL of the webpage",
            ),
            Property(
                name="text",
                data_type=DataType.TEXT,
                description="the content of the webpage",
            ),
        ],
    )

    if client.collections.exists("LlamaIndexDocs"):
        client.collections.delete("LlamaIndexDocs")
    client.collections.create(
        "LlamaIndexDocs",
        description="A dataset with the contents of LlamaIndex technical Docs and website",
        vectorizer_config=Configure.Vectorizer.text2vec_weaviate(),
        properties=[
            Property(
                name="url",
                data_type=DataType.TEXT,
                description="the source URL of the webpage",
            ),
            Property(
                name="text",
                data_type=DataType.TEXT,
                description="the content of the webpage",
            ),
        ],
    )

    agent = QueryAgent(
        client=client, collections=["LlamaIndexDocs", "WeaviateDocs"]
    )
    return agent

```

def fresh_setup_weaviate(client): if client.collections.exists("WeaviateDocs"): client.collections.delete("WeaviateDocs") client.collections.create( "WeaviateDocs", description="A dataset with the contents of Weaviate technical Docs and website", vectorizer_config=Configure.Vectorizer.text2vec_weaviate(), properties=[ Property( name="url", data_type=DataType.TEXT, description="the source URL of the webpage", ), Property( name="text", data_type=DataType.TEXT, description="the content of the webpage", ), ], ) if client.collections.exists("LlamaIndexDocs"): client.collections.delete("LlamaIndexDocs") client.collections.create( "LlamaIndexDocs", description="A dataset with the contents of LlamaIndex technical Docs and website", vectorizer_config=Configure.Vectorizer.text2vec_weaviate(), properties=[ Property( name="url", data_type=DataType.TEXT, description="the source URL of the webpage", ), Property( name="text", data_type=DataType.TEXT, description="the content of the webpage", ), ], ) agent = QueryAgent( client=client, collections=["LlamaIndexDocs", "WeaviateDocs"] ) return agent
### Write Contents of Webpage to the Collections¶
The helper function below uses the `SimpleWebPageReader` to write the contents of a webpage to the relevant Weaviate collection
In [ ]:
Copied!
```
def write_webpages_to_weaviate(client, urls: list[str], collection_name: str):
    documents = SimpleWebPageReader(html_to_text=True).load_data(urls)
    collection = client.collections.get(collection_name)
    with collection.batch.dynamic() as batch:
        for doc in documents:
            batch.add_object(properties={"url": doc.id_, "text": doc.text})

```

def write_webpages_to_weaviate(client, urls: list[str], collection_name: str): documents = SimpleWebPageReader(html_to_text=True).load_data(urls) collection = client.collections.get(collection_name) with collection.batch.dynamic() as batch: for doc in documents: batch.add_object(properties={"url": doc.id_, "text": doc.text})
## Create a Function Calling Agent¶
Now that we have the relevant functions to write to a collection and also the `QueryAgent` at hand, we can start by using the `FunctionAgent`, which is a simple tool calling agent.
In [ ]:
Copied!
```
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass("openai-key")

```

if "OPENAI_API_KEY" not in os.environ: os.environ["OPENAI_API_KEY"] = getpass("openai-key")
In [ ]:
Copied!
```
weaviate_agent = fresh_setup_weaviate(client)

```

weaviate_agent = fresh_setup_weaviate(client)
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4o-mini")


def write_to_weaviate_collection(urls=list[str]):
    """Useful for writing new content to the WeaviateDocs collection"""
    write_webpages_to_weaviate(client, urls, "WeaviateDocs")


def write_to_li_collection(urls=list[str]):
    """Useful for writing new content to the LlamaIndexDocs collection"""
    write_webpages_to_weaviate(client, urls, "LlamaIndexDocs")


def query_agent(query: str) -> str:
    """Useful for asking questions about Weaviate and LlamaIndex"""
    response = weaviate_agent.run(query)
    return response.final_answer


agent = FunctionAgent(
    tools=[write_to_weaviate_collection, write_to_li_collection, query_agent],
    llm=llm,
    system_prompt="""You are a helpful assistant that can write the
      contents of urls to WeaviateDocs and LlamaIndexDocs collections,
      as well as forwarding questions to a QueryAgent""",
)

```

llm = OpenAI(model="gpt-4o-mini") def write_to_weaviate_collection(urls=list[str]): """Useful for writing new content to the WeaviateDocs collection""" write_webpages_to_weaviate(client, urls, "WeaviateDocs") def write_to_li_collection(urls=list[str]): """Useful for writing new content to the LlamaIndexDocs collection""" write_webpages_to_weaviate(client, urls, "LlamaIndexDocs") def query_agent(query: str) -> str: """Useful for asking questions about Weaviate and LlamaIndex""" response = weaviate_agent.run(query) return response.final_answer agent = FunctionAgent( tools=[write_to_weaviate_collection, write_to_li_collection, query_agent], llm=llm, system_prompt="""You are a helpful assistant that can write the contents of urls to WeaviateDocs and LlamaIndexDocs collections, as well as forwarding questions to a QueryAgent""", )
In [ ]:
Copied!
```
response = await agent.run(
    user_msg="Can you save https://docs.llamaindex.ai/en/stable/examples/agent/agent_workflow_basic/"
)
print(str(response))

```

response = await agent.run( user_msg="Can you save https://docs.llamaindex.ai/en/stable/examples/agent/agent_workflow_basic/" ) print(str(response))
In [ ]:
Copied!
```
response = await agent.run(
    user_msg="""What are llama index workflows? And can you save
    these to weaviate docs: https://weaviate.io/blog/what-are-agentic-workflows
    and https://weaviate.io/blog/ai-agents"""
)
print(str(response))

```

response = await agent.run( user_msg="""What are llama index workflows? And can you save these to weaviate docs: https://weaviate.io/blog/what-are-agentic-workflows and https://weaviate.io/blog/ai-agents""" ) print(str(response))
```
Llama Index workflows refer to orchestrations involving one or more AI agents within the LlamaIndex framework. These workflows manage complex tasks dynamically by leveraging components such as large language models (LLMs), tools, and memory states. Key features of Llama Index workflows include:

- Support for single or multiple agents managed within an AgentWorkflow orchestrator.
- Ability to maintain state across runs via serializable context objects.
- Integration of external tools with type annotations, including asynchronous functions.
- Streaming of intermediate outputs and event-based interactions.
- Human-in-the-loop capabilities to confirm or guide agent actions during workflow execution.

These workflows enable agents to execute sequences of operations, call external tools asynchronously, maintain conversation or task states, stream partial results, and incorporate human inputs when necessary. They embody dynamic, agent-driven sequences of task decomposition, tool use, and reflection, allowing AI systems to plan, act, and improve iteratively toward specific goals.

I have also saved the contents from the provided URLs to the WeaviateDocs collection.

```

In [ ]:
Copied!
```
response = await agent.run(
    user_msg="How many docs do I have in the weaviate and llamaindex collections in total?"
)
print(str(response))

```

response = await agent.run( user_msg="How many docs do I have in the weaviate and llamaindex collections in total?" ) print(str(response))
```
You have a total of 2 documents in the WeaviateDocs collection and 1 document in the LlamaIndexDocs collection. In total, that makes 3 documents across both collections.

```

In [ ]:
Copied!
```
weaviate_agent = fresh_setup_weaviate(client)

```

weaviate_agent = fresh_setup_weaviate(client)
## Create a Workflow with Branches¶
### Simple Example: Create Events¶
A LlamaIndex Workflow has 2 fundamentals:
  * An Event
  * A Step


An step may return an event, and an event may trigger a step!
For our use-case, we can imagine thet there are 4 events:
In [ ]:
Copied!
```
class EvaluateQuery(Event):
    query: str


class WriteLlamaIndexDocsEvent(Event):
    urls: list[str]


class WriteWeaviateDocsEvent(Event):
    urls: list[str]


class QueryAgentEvent(Event):
    query: str

```

class EvaluateQuery(Event): query: str class WriteLlamaIndexDocsEvent(Event): urls: list[str] class WriteWeaviateDocsEvent(Event): urls: list[str] class QueryAgentEvent(Event): query: str
### Simple Example: A Branching Workflow (that does nothing yet)¶
In [ ]:
Copied!
```
class DocsAssistantWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> EvaluateQuery:
        return EvaluateQuery(query=ev.query)

    @step
    async def evaluate_query(
        self, ctx: Context, ev: EvaluateQuery
    ) -> QueryAgentEvent | WriteLlamaIndexDocsEvent | WriteWeaviateDocsEvent | StopEvent:
        if ev.query == "llama":
            return WriteLlamaIndexDocsEvent(urls=[ev.query])
        if ev.query == "weaviate":
            return WriteWeaviateDocsEvent(urls=[ev.query])
        if ev.query == "question":
            return QueryAgentEvent(query=ev.query)
        return StopEvent()

    @step
    async def write_li_docs(
        self, ctx: Context, ev: WriteLlamaIndexDocsEvent
    ) -> StopEvent:
        print(f"Got a request to write something to LlamaIndexDocs")
        return StopEvent()

    @step
    async def write_weaviate_docs(
        self, ctx: Context, ev: WriteWeaviateDocsEvent
    ) -> StopEvent:
        print(f"Got a request to write something to WeaviateDocs")
        return StopEvent()

    @step
    async def query_agent(
        self, ctx: Context, ev: QueryAgentEvent
    ) -> StopEvent:
        print(f"Got a request to forward a query to the QueryAgent")
        return StopEvent()

```

class DocsAssistantWorkflow(Workflow): @step async def start(self, ctx: Context, ev: StartEvent) -> EvaluateQuery: return EvaluateQuery(query=ev.query) @step async def evaluate_query( self, ctx: Context, ev: EvaluateQuery ) -> QueryAgentEvent | WriteLlamaIndexDocsEvent | WriteWeaviateDocsEvent | StopEvent: if ev.query == "llama": return WriteLlamaIndexDocsEvent(urls=[ev.query]) if ev.query == "weaviate": return WriteWeaviateDocsEvent(urls=[ev.query]) if ev.query == "question": return QueryAgentEvent(query=ev.query) return StopEvent() @step async def write_li_docs( self, ctx: Context, ev: WriteLlamaIndexDocsEvent ) -> StopEvent: print(f"Got a request to write something to LlamaIndexDocs") return StopEvent() @step async def write_weaviate_docs( self, ctx: Context, ev: WriteWeaviateDocsEvent ) -> StopEvent: print(f"Got a request to write something to WeaviateDocs") return StopEvent() @step async def query_agent( self, ctx: Context, ev: QueryAgentEvent ) -> StopEvent: print(f"Got a request to forward a query to the QueryAgent") return StopEvent()
In [ ]:
Copied!
```
workflow_that_does_nothing = DocsAssistantWorkflow()

# draw_all_possible_flows(workflow_that_does_nothing)

```

workflow_that_does_nothing = DocsAssistantWorkflow() # draw_all_possible_flows(workflow_that_does_nothing)
In [ ]:
Copied!
```
print(
    await workflow_that_does_nothing.run(start_event=StartEvent(query="llama"))
)

```

print( await workflow_that_does_nothing.run(start_event=StartEvent(query="llama")) )
```
Got a request to write something to LlamaIndexDocs
None

```

### Classify the Query with Structured Outputs¶
In [ ]:
Copied!
```
class SaveToLlamaIndexDocs(BaseModel):
    """The URLs to parse and save into a llama-index specific docs collection."""

    llama_index_urls: List[str] = Field(default_factory=list)


class SaveToWeaviateDocs(BaseModel):
    """The URLs to parse and save into a weaviate specific docs collection."""

    weaviate_urls: List[str] = Field(default_factory=list)


class Ask(BaseModel):
    """The natural language questions that can be asked to a Q&A agent."""

    queries: List[str] = Field(default_factory=list)


class Actions(BaseModel):
    """Actions to take based on the latest user message."""

    actions: List[
        Union[SaveToLlamaIndexDocs, SaveToWeaviateDocs, Ask]
    ] = Field(default_factory=list)

```

class SaveToLlamaIndexDocs(BaseModel): """The URLs to parse and save into a llama-index specific docs collection.""" llama_index_urls: List[str] = Field(default_factory=list) class SaveToWeaviateDocs(BaseModel): """The URLs to parse and save into a weaviate specific docs collection.""" weaviate_urls: List[str] = Field(default_factory=list) class Ask(BaseModel): """The natural language questions that can be asked to a Q&A agent.""" queries: List[str] = Field(default_factory=list) class Actions(BaseModel): """Actions to take based on the latest user message.""" actions: List[ Union[SaveToLlamaIndexDocs, SaveToWeaviateDocs, Ask] ] = Field(default_factory=list)
#### Create a Workflow¶
Let's create a workflow that, still, does nothing, but the incoming user query will be converted to our structure. Based on the contents of that structure, the workflow will decide which step to run.
Notice how whichever step runs first, will return a `StopEvent`... This is good, but maybe we can improve that later!
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAIResponses


class DocsAssistantWorkflow(Workflow):
    def __init__(self, *args, **kwargs):
        self.llm = OpenAIResponses(model="gpt-4.1-mini")
        self.system_prompt = """You are a docs assistant. You evaluate incoming queries and break them down to subqueries when needed.
                          You decide on the next best course of action. Overall, here are the options:
                          - You can write the contents of a URL to llamaindex docs (if it's a llamaindex url)
                          - You can write the contents of a URL to weaviate docs (if it's a weaviate url)
                          - You can answer a question about llamaindex and weaviate using the QueryAgent"""
        super().__init__(*args, **kwargs)

    @step
    async def start(self, ev: StartEvent) -> EvaluateQuery:
        return EvaluateQuery(query=ev.query)

    @step
    async def evaluate_query(
        self, ev: EvaluateQuery
    ) -> QueryAgentEvent | WriteLlamaIndexDocsEvent | WriteWeaviateDocsEvent:
        sllm = self.llm.as_structured_llm(Actions)
        response = await sllm.achat(
            [
                ChatMessage(role="system", content=self.system_prompt),
                ChatMessage(role="user", content=ev.query),
            ]
        )
        actions = response.raw.actions
        print(actions)
        for action in actions:
            if isinstance(action, SaveToLlamaIndexDocs):
                return WriteLlamaIndexDocsEvent(urls=action.llama_index_urls)
            elif isinstance(action, SaveToWeaviateDocs):
                return WriteWeaviateDocsEvent(urls=action.weaviate_urls)
            elif isinstance(action, Ask):
                for query in action.queries:
                    return QueryAgentEvent(query=query)

    @step
    async def write_li_docs(self, ev: WriteLlamaIndexDocsEvent) -> StopEvent:
        print(f"Writing {ev.urls} to LlamaIndex Docs")
        return StopEvent()

    @step
    async def write_weaviate_docs(
        self, ev: WriteWeaviateDocsEvent
    ) -> StopEvent:
        print(f"Writing {ev.urls} to Weaviate Docs")
        return StopEvent()

    @step
    async def query_agent(self, ev: QueryAgentEvent) -> StopEvent:
        print(f"Sending `'{ev.query}`' to agent")
        return StopEvent()


everything_docs_agent_beta = DocsAssistantWorkflow()

```

from llama_index.llms.openai import OpenAIResponses class DocsAssistantWorkflow(Workflow): def __init__(self, *args, **kwargs): self.llm = OpenAIResponses(model="gpt-4.1-mini") self.system_prompt = """You are a docs assistant. You evaluate incoming queries and break them down to subqueries when needed. You decide on the next best course of action. Overall, here are the options: - You can write the contents of a URL to llamaindex docs (if it's a llamaindex url) - You can write the contents of a URL to weaviate docs (if it's a weaviate url) - You can answer a question about llamaindex and weaviate using the QueryAgent""" super().__init__(*args, **kwargs) @step async def start(self, ev: StartEvent) -> EvaluateQuery: return EvaluateQuery(query=ev.query) @step async def evaluate_query( self, ev: EvaluateQuery ) -> QueryAgentEvent | WriteLlamaIndexDocsEvent | WriteWeaviateDocsEvent: sllm = self.llm.as_structured_llm(Actions) response = await sllm.achat( [ ChatMessage(role="system", content=self.system_prompt), ChatMessage(role="user", content=ev.query), ] ) actions = response.raw.actions print(actions) for action in actions: if isinstance(action, SaveToLlamaIndexDocs): return WriteLlamaIndexDocsEvent(urls=action.llama_index_urls) elif isinstance(action, SaveToWeaviateDocs): return WriteWeaviateDocsEvent(urls=action.weaviate_urls) elif isinstance(action, Ask): for query in action.queries: return QueryAgentEvent(query=query) @step async def write_li_docs(self, ev: WriteLlamaIndexDocsEvent) -> StopEvent: print(f"Writing {ev.urls} to LlamaIndex Docs") return StopEvent() @step async def write_weaviate_docs( self, ev: WriteWeaviateDocsEvent ) -> StopEvent: print(f"Writing {ev.urls} to Weaviate Docs") return StopEvent() @step async def query_agent(self, ev: QueryAgentEvent) -> StopEvent: print(f"Sending `'{ev.query}`' to agent") return StopEvent() everything_docs_agent_beta = DocsAssistantWorkflow()
In [ ]:
Copied!
```
async def run_docs_agent_beta(query: str):
    print(
        await everything_docs_agent_beta.run(
            start_event=StartEvent(query=query)
        )
    )

```

async def run_docs_agent_beta(query: str): print( await everything_docs_agent_beta.run( start_event=StartEvent(query=query) ) )
In [ ]:
Copied!
```
await run_docs_agent_beta(
    """Can you save https://www.llamaindex.ai/blog/get-citations-and-reasoning-for-extracted-data-in-llamaextract
    and https://www.llamaindex.ai/blog/llamaparse-update-may-2025-new-models-skew-detection-and-more??"""
)

```

await run_docs_agent_beta( """Can you save https://www.llamaindex.ai/blog/get-citations-and-reasoning-for-extracted-data-in-llamaextract and https://www.llamaindex.ai/blog/llamaparse-update-may-2025-new-models-skew-detection-and-more??""" )
```
[SaveToLlamaIndexDocs(llama_index_urls=['https://www.llamaindex.ai/blog/get-citations-and-reasoning-for-extracted-data-in-llamaextract', 'https://www.llamaindex.ai/blog/llamaparse-update-may-2025-new-models-skew-detection-and-more'])]
Writing ['https://www.llamaindex.ai/blog/get-citations-and-reasoning-for-extracted-data-in-llamaextract', 'https://www.llamaindex.ai/blog/llamaparse-update-may-2025-new-models-skew-detection-and-more'] to LlamaIndex Docs
None

```

In [ ]:
Copied!
```
await run_docs_agent_beta(
    "How many documents do we have in the LlamaIndexDocs collection now?"
)

```

await run_docs_agent_beta( "How many documents do we have in the LlamaIndexDocs collection now?" )
```
[Ask(queries=['How many documents are in the LlamaIndexDocs collection?'])]
Sending `'How many documents are in the LlamaIndexDocs collection?`' to agent
None

```

In [ ]:
Copied!
```
await run_docs_agent_beta("What are LlamaIndex workflows?")

```

await run_docs_agent_beta("What are LlamaIndex workflows?")
```
[Ask(queries=['What are LlamaIndex workflows?'])]
Sending `'What are LlamaIndex workflows?`' to agent
None

```

In [ ]:
Copied!
```
await run_docs_agent_beta(
    "Can you save https://weaviate.io/blog/graph-rag and https://weaviate.io/blog/genai-apps-with-weaviate-and-databricks??"
)

```

await run_docs_agent_beta( "Can you save https://weaviate.io/blog/graph-rag and https://weaviate.io/blog/genai-apps-with-weaviate-and-databricks??" )
```
[SaveToWeaviateDocs(weaviate_urls=['https://weaviate.io/blog/graph-rag', 'https://weaviate.io/blog/genai-apps-with-weaviate-and-databricks'])]
Writing ['https://weaviate.io/blog/graph-rag', 'https://weaviate.io/blog/genai-apps-with-weaviate-and-databricks'] to Weaviate Docs
None

```

## Run Multiple Branches & Put it all togehter¶
In these cases, it makes sense to run multiple branches. So, a single step can trigger multiple events at once! We can `send_event` via the context 👇
In [ ]:
Copied!
```
class ActionCompleted(Event):
    result: str


class DocsAssistantWorkflow(Workflow):
    def __init__(self, *args, **kwargs):
        self.llm = OpenAIResponses(model="gpt-4.1-mini")
        self.system_prompt = """You are a docs assistant. You evaluate incoming queries and break them down to subqueries when needed.
                      You decide on the next best course of action. Overall, here are the options:
                      - You can write the contents of a URL to llamaindex docs (if it's a llamaindex url)
                      - You can write the contents of a URL to weaviate docs (if it's a weaviate url)
                      - You can answer a question about llamaindex and weaviate using the QueryAgent"""
        super().__init__(*args, **kwargs)

    @step
    async def start(self, ctx: Context, ev: StartEvent) -> EvaluateQuery:
        return EvaluateQuery(query=ev.query)

    @step
    async def evaluate_query(
        self, ctx: Context, ev: EvaluateQuery
    ) -> QueryAgentEvent | WriteLlamaIndexDocsEvent | WriteWeaviateDocsEvent | None:
        await ctx.store.set("results", [])
        sllm = self.llm.as_structured_llm(Actions)
        response = await sllm.achat(
            [
                ChatMessage(role="system", content=self.system_prompt),
                ChatMessage(role="user", content=ev.query),
            ]
        )
        actions = response.raw.actions
        await ctx.store.set("num_events", len(actions))
        await ctx.store.set("results", [])
        print(actions)
        for action in actions:
            if isinstance(action, SaveToLlamaIndexDocs):
                ctx.send_event(
                    WriteLlamaIndexDocsEvent(urls=action.llama_index_urls)
                )
            elif isinstance(action, SaveToWeaviateDocs):
                ctx.send_event(
                    WriteWeaviateDocsEvent(urls=action.weaviate_urls)
                )
            elif isinstance(action, Ask):
                for query in action.queries:
                    ctx.send_event(QueryAgentEvent(query=query))

    @step
    async def write_li_docs(
        self, ctx: Context, ev: WriteLlamaIndexDocsEvent
    ) -> ActionCompleted:
        print(f"Writing {ev.urls} to LlamaIndex Docs")
        write_webpages_to_weaviate(
            client, urls=ev.urls, collection_name="LlamaIndexDocs"
        )
        results = await ctx.store.get("results")
        results.append(f"Wrote {ev.urls} it LlamaIndex Docs")
        return ActionCompleted(result=f"Writing {ev.urls} to LlamaIndex Docs")

    @step
    async def write_weaviate_docs(
        self, ctx: Context, ev: WriteWeaviateDocsEvent
    ) -> ActionCompleted:
        print(f"Writing {ev.urls} to Weaviate Docs")
        write_webpages_to_weaviate(
            client, urls=ev.urls, collection_name="WeaviateDocs"
        )
        results = await ctx.store.get("results")
        results.append(f"Wrote {ev.urls} it Weavite Docs")
        return ActionCompleted(result=f"Writing {ev.urls} to Weaviate Docs")

    @step
    async def query_agent(
        self, ctx: Context, ev: QueryAgentEvent
    ) -> ActionCompleted:
        print(f"Sending {ev.query} to agent")
        response = weaviate_agent.run(ev.query)
        results = await ctx.store.get("results")
        results.append(f"QueryAgent responded with:\n {response.final_answer}")
        return ActionCompleted(result=f"Sending `'{ev.query}`' to agent")

    @step
    async def collect(
        self, ctx: Context, ev: ActionCompleted
    ) -> StopEvent | None:
        num_events = await ctx.store.get("num_events")
        evs = ctx.collect_events(ev, [ActionCompleted] * num_events)
        if evs is None:
            return None
        return StopEvent(result=[ev.result for ev in evs])


everything_docs_agent = DocsAssistantWorkflow(timeout=None)

```

class ActionCompleted(Event): result: str class DocsAssistantWorkflow(Workflow): def __init__(self, *args, **kwargs): self.llm = OpenAIResponses(model="gpt-4.1-mini") self.system_prompt = """You are a docs assistant. You evaluate incoming queries and break them down to subqueries when needed. You decide on the next best course of action. Overall, here are the options: - You can write the contents of a URL to llamaindex docs (if it's a llamaindex url) - You can write the contents of a URL to weaviate docs (if it's a weaviate url) - You can answer a question about llamaindex and weaviate using the QueryAgent""" super().__init__(*args, **kwargs) @step async def start(self, ctx: Context, ev: StartEvent) -> EvaluateQuery: return EvaluateQuery(query=ev.query) @step async def evaluate_query( self, ctx: Context, ev: EvaluateQuery ) -> QueryAgentEvent | WriteLlamaIndexDocsEvent | WriteWeaviateDocsEvent | None: await ctx.store.set("results", []) sllm = self.llm.as_structured_llm(Actions) response = await sllm.achat( [ ChatMessage(role="system", content=self.system_prompt), ChatMessage(role="user", content=ev.query), ] ) actions = response.raw.actions await ctx.store.set("num_events", len(actions)) await ctx.store.set("results", []) print(actions) for action in actions: if isinstance(action, SaveToLlamaIndexDocs): ctx.send_event( WriteLlamaIndexDocsEvent(urls=action.llama_index_urls) ) elif isinstance(action, SaveToWeaviateDocs): ctx.send_event( WriteWeaviateDocsEvent(urls=action.weaviate_urls) ) elif isinstance(action, Ask): for query in action.queries: ctx.send_event(QueryAgentEvent(query=query)) @step async def write_li_docs( self, ctx: Context, ev: WriteLlamaIndexDocsEvent ) -> ActionCompleted: print(f"Writing {ev.urls} to LlamaIndex Docs") write_webpages_to_weaviate( client, urls=ev.urls, collection_name="LlamaIndexDocs" ) results = await ctx.store.get("results") results.append(f"Wrote {ev.urls} it LlamaIndex Docs") return ActionCompleted(result=f"Writing {ev.urls} to LlamaIndex Docs") @step async def write_weaviate_docs( self, ctx: Context, ev: WriteWeaviateDocsEvent ) -> ActionCompleted: print(f"Writing {ev.urls} to Weaviate Docs") write_webpages_to_weaviate( client, urls=ev.urls, collection_name="WeaviateDocs" ) results = await ctx.store.get("results") results.append(f"Wrote {ev.urls} it Weavite Docs") return ActionCompleted(result=f"Writing {ev.urls} to Weaviate Docs") @step async def query_agent( self, ctx: Context, ev: QueryAgentEvent ) -> ActionCompleted: print(f"Sending {ev.query} to agent") response = weaviate_agent.run(ev.query) results = await ctx.store.get("results") results.append(f"QueryAgent responded with:\n {response.final_answer}") return ActionCompleted(result=f"Sending `'{ev.query}`' to agent") @step async def collect( self, ctx: Context, ev: ActionCompleted ) -> StopEvent | None: num_events = await ctx.store.get("num_events") evs = ctx.collect_events(ev, [ActionCompleted] * num_events) if evs is None: return None return StopEvent(result=[ev.result for ev in evs]) everything_docs_agent = DocsAssistantWorkflow(timeout=None)
In [ ]:
Copied!
```
async def run_docs_agent(query: str):
    handler = everything_docs_agent.run(start_event=StartEvent(query=query))
    result = await handler
    for response in await handler.ctx.store.get("results"):
        print(response)

```

async def run_docs_agent(query: str): handler = everything_docs_agent.run(start_event=StartEvent(query=query)) result = await handler for response in await handler.ctx.store.get("results"): print(response)
In [ ]:
Copied!
```
await run_docs_agent(
    "Can you save https://docs.llamaindex.ai/en/stable/understanding/workflows/ and https://docs.llamaindex.ai/en/stable/understanding/workflows/branches_and_loops/"
)

```

await run_docs_agent( "Can you save https://docs.llamaindex.ai/en/stable/understanding/workflows/ and https://docs.llamaindex.ai/en/stable/understanding/workflows/branches_and_loops/" )
```
[SaveToLlamaIndexDocs(llama_index_urls=['https://docs.llamaindex.ai/en/stable/understanding/workflows/']), SaveToLlamaIndexDocs(llama_index_urls=['https://docs.llamaindex.ai/en/stable/understanding/workflows/branches_and_loops/'])]
Writing ['https://docs.llamaindex.ai/en/stable/understanding/workflows/'] to LlamaIndex Docs
Writing ['https://docs.llamaindex.ai/en/stable/understanding/workflows/branches_and_loops/'] to LlamaIndex Docs
Wrote ['https://docs.llamaindex.ai/en/stable/understanding/workflows/'] it LlamaIndex Docs
Wrote ['https://docs.llamaindex.ai/en/stable/understanding/workflows/branches_and_loops/'] it LlamaIndex Docs

```

In [ ]:
Copied!
```
await run_docs_agent(
    "How many documents do we have in the LlamaIndexDocs collection now?"
)

```

await run_docs_agent( "How many documents do we have in the LlamaIndexDocs collection now?" )
```
[Ask(queries=['How many documents are in the LlamaIndexDocs collection?'])]
Sending How many documents are in the LlamaIndexDocs collection? to agent
QueryAgent responded with:
 The LlamaIndexDocs collection contains 2 documents, specifically related to workflows and branches and loops within the documentation.

```

In [ ]:
Copied!
```
await run_docs_agent(
    "What are LlamaIndex workflows? And can you save https://weaviate.io/blog/graph-rag"
)

```

await run_docs_agent( "What are LlamaIndex workflows? And can you save https://weaviate.io/blog/graph-rag" )
```
[Ask(queries=['What are LlamaIndex workflows?'])]
Sending What are LlamaIndex workflows? to agent
QueryAgent responded with:
 LlamaIndex workflows are an event-driven, step-based framework designed to control and manage the execution flow of complex applications, particularly those involving generative AI. They break an application into discrete Steps, each triggered by Events and capable of emitting further Events, allowing for complex logic involving loops, branches, and parallel execution.

In a LlamaIndex workflow, steps perform functions ranging from simple tasks to complex agents, with inputs and outputs communicated via Events. This event-driven model facilitates maintainability and clarity, overcoming limitations of previous approaches like directed acyclic graphs (DAGs) which struggled with complex flows involving loops and branching.

Key features include:
- **Loops:** Steps can return events that loop back to previous steps to enable iterative processes.
- **Branches:** Workflows can branch into different paths based on conditions, allowing for multiple distinct sequences of steps.
- **Parallelism:** Multiple branches or steps can run concurrently and synchronize their results.
- **State Maintenance:** Workflows support maintaining state and context throughout execution.
- **Observability and Debugging:** Supported by various components and callbacks for monitoring.

An example workflow might involve judging whether a query is of sufficient quality, looping to improve it if not, then concurrently executing different retrieval-augmented generation (RAG) strategies, and finally judging their responses to produce a single output.

Workflows are especially useful as applications grow in complexity, enabling developers to organize and control intricate AI logic more naturally and efficiently than traditional graph-based methods. For simpler pipelines, LlamaIndex suggests using workflows optionally, but for advanced agentic applications, workflows provide a flexible and powerful control abstraction.

```

In [ ]:
Copied!
```
await run_docs_agent("How do I use loops in llamaindex workflows?")

```

await run_docs_agent("How do I use loops in llamaindex workflows?")
```
[Ask(queries=['How to use loops in llamaindex workflows'])]
Sending How to use loops in llamaindex workflows to agent
QueryAgent responded with:
 In LlamaIndex workflows, loops are implemented using an event-driven approach where you define custom event types and steps that emit events to control the workflow's execution flow. To create a loop, you define a custom event (e.g., `LoopEvent`) and a workflow step that can return either the event continuing the loop or another event to proceed. For example, a workflow step might randomly decide to either loop back (emit `LoopEvent` again) or continue to a next step emitting a different event.

This allows creating flexible looping behaviors where any step can loop back to any other step by returning the corresponding event instances. The approach leverages Python's async functions decorated with `@step`, which process events and return the next event(s), enabling both loops and conditional branching in workflows.

Thus, loops in LlamaIndex workflows are event-based, using custom event types and the return of events from steps to signal iterations until a condition is met.

Example:

```python
from llamaindex.workflow import Workflow, Event, StartEvent, StopEvent, step
import random

class LoopEvent(Event):
    loop_output: str

class FirstEvent(Event):
    first_output: str

class MyWorkflow(Workflow):
    @step
    async def step_one(self, ev: StartEvent | LoopEvent) -> FirstEvent | LoopEvent:
        if random.randint(0, 1) == 0:
            print("Bad thing happened")
            return LoopEvent(loop_output="Back to step one.")
        else:
            print("Good thing happened")
            return FirstEvent(first_output="First step complete.")

    # ... other steps ...

# Running this workflow will cause step_one to loop randomly until it proceeds.
```

You can combine loops with branching and parallel execution in workflows to build complex control flows. For detailed guidance and examples, consult the LlamaIndex documentation under "Branches and Loops" and the "Workflows" guides.

```

