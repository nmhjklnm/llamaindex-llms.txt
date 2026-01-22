# GPT Builder Demo¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
Inspired by GPTs interface, presented at OpenAI Dev Day 2023. Construct an agent with natural language.
Here you can build your own agent...with another agent!
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-llms-openai
%pip install llama-index-readers-file

```

%pip install llama-index-embeddings-openai %pip install llama-index-llms-openai %pip install llama-index-readers-file
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
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

llm = OpenAI(model="gpt-4o")
Settings.llm = llm
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI from llama_index.core import Settings llm = OpenAI(model="gpt-4o") Settings.llm = llm Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
## Define Candidate Tools¶
We also define a tool retriever to retrieve candidate tools.
In this setting we define tools as different Wikipedia pages.
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

```

from llama_index.core import SimpleDirectoryReader
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
### Build Query Tool for Each Document¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool
from llama_index.core import VectorStoreIndex

# Build tool dictionary
tool_dict = {}

for wiki_title in wiki_titles:
    # build vector index
    vector_index = VectorStoreIndex.from_documents(
        city_docs[wiki_title],
    )
    # define query engines
    vector_query_engine = vector_index.as_query_engine(llm=llm)

    # define tools
    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_query_engine,
        name=wiki_title,
        description=("Useful for questions related to" f" {wiki_title}"),
    )
    tool_dict[wiki_title] = vector_tool

```

from llama_index.core import VectorStoreIndex from llama_index.core.tools import QueryEngineTool from llama_index.core import VectorStoreIndex # Build tool dictionary tool_dict = {} for wiki_title in wiki_titles: # build vector index vector_index = VectorStoreIndex.from_documents( city_docs[wiki_title], ) # define query engines vector_query_engine = vector_index.as_query_engine(llm=llm) # define tools vector_tool = QueryEngineTool.from_defaults( query_engine=vector_query_engine, name=wiki_title, description=("Useful for questions related to" f" {wiki_title}"), ) tool_dict[wiki_title] = vector_tool
### Define Tool Retriever¶
In [ ]:
Copied!
```
# define an "object" index and retriever over these tools
from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex

tool_index = ObjectIndex.from_objects(
    list(tool_dict.values()),
    index_cls=VectorStoreIndex,
)
tool_retriever = tool_index.as_retriever(similarity_top_k=1)

```

# define an "object" index and retriever over these tools from llama_index.core import VectorStoreIndex from llama_index.core.objects import ObjectIndex tool_index = ObjectIndex.from_objects( list(tool_dict.values()), index_cls=VectorStoreIndex, ) tool_retriever = tool_index.as_retriever(similarity_top_k=1)
### Load Data¶
Here we load wikipedia pages from different cities.
## Define Meta-Tools for GPT Builder¶
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.llms import ChatMessage
from llama_index.core import ChatPromptTemplate
from typing import List

GEN_SYS_PROMPT_STR = """\
Task information is given below. 

Given the task, please generate a system prompt for an OpenAI-powered bot to solve this task: 
{task} \
"""

gen_sys_prompt_messages = [
    ChatMessage(
        role="system",
        content="You are helping to build a system prompt for another bot.",
    ),
    ChatMessage(role="user", content=GEN_SYS_PROMPT_STR),
]

GEN_SYS_PROMPT_TMPL = ChatPromptTemplate(gen_sys_prompt_messages)


agent_cache = {}


async def create_system_prompt(task: str):
    """Create system prompt for another agent given an input task."""
    llm = OpenAI(llm="gpt-4")
    fmt_messages = GEN_SYS_PROMPT_TMPL.format_messages(task=task)
    response = await llm.achat(fmt_messages)
    return response.message.content


async def get_tools(task: str):
    """Get the set of relevant tools to use given an input task."""
    subset_tools = await tool_retriever.aretrieve(task)
    return [t.metadata.name for t in subset_tools]


def create_agent(system_prompt: str, tool_names: List[str]):
    """Create an agent given a system prompt and an input set of tools."""
    llm = OpenAI(model="gpt-4o")
    try:
        # get the list of tools
        input_tools = [tool_dict[tn] for tn in tool_names]

        agent = FunctionAgent(
            tools=input_tools, llm=llm, system_prompt=system_prompt
        )
        agent_cache["agent"] = agent
        return_msg = "Agent created successfully."
    except Exception as e:
        return_msg = f"An error occurred when building an agent. Here is the error: {repr(e)}"
    return return_msg

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.core.llms import ChatMessage from llama_index.core import ChatPromptTemplate from typing import List GEN_SYS_PROMPT_STR = """\ Task information is given below. Given the task, please generate a system prompt for an OpenAI-powered bot to solve this task: {task} \ """ gen_sys_prompt_messages = [ ChatMessage( role="system", content="You are helping to build a system prompt for another bot.", ), ChatMessage(role="user", content=GEN_SYS_PROMPT_STR), ] GEN_SYS_PROMPT_TMPL = ChatPromptTemplate(gen_sys_prompt_messages) agent_cache = {} async def create_system_prompt(task: str): """Create system prompt for another agent given an input task.""" llm = OpenAI(llm="gpt-4") fmt_messages = GEN_SYS_PROMPT_TMPL.format_messages(task=task) response = await llm.achat(fmt_messages) return response.message.content async def get_tools(task: str): """Get the set of relevant tools to use given an input task.""" subset_tools = await tool_retriever.aretrieve(task) return [t.metadata.name for t in subset_tools] def create_agent(system_prompt: str, tool_names: List[str]): """Create an agent given a system prompt and an input set of tools.""" llm = OpenAI(model="gpt-4o") try: # get the list of tools input_tools = [tool_dict[tn] for tn in tool_names] agent = FunctionAgent( tools=input_tools, llm=llm, system_prompt=system_prompt ) agent_cache["agent"] = agent return_msg = "Agent created successfully." except Exception as e: return_msg = f"An error occurred when building an agent. Here is the error: {repr(e)}" return return_msg
In [ ]:
Copied!
```
from llama_index.core.tools import FunctionTool

system_prompt_tool = FunctionTool.from_defaults(fn=create_system_prompt)
get_tools_tool = FunctionTool.from_defaults(fn=get_tools)
create_agent_tool = FunctionTool.from_defaults(fn=create_agent)

```

from llama_index.core.tools import FunctionTool system_prompt_tool = FunctionTool.from_defaults(fn=create_system_prompt) get_tools_tool = FunctionTool.from_defaults(fn=get_tools) create_agent_tool = FunctionTool.from_defaults(fn=create_agent)
In [ ]:
Copied!
```
GPT_BUILDER_SYS_STR = """\
You are helping to construct an agent given a user-specified task. You should generally use the tools in this order to build the agent.

1) Create system prompt tool: to create the system prompt for the agent.
2) Get tools tool: to fetch the candidate set of tools to use.
3) Create agent tool: to create the final agent.
"""

prefix_msgs = [ChatMessage(role="system", content=GPT_BUILDER_SYS_STR)]


builder_agent = FunctionAgent(
    tools=[system_prompt_tool, get_tools_tool, create_agent_tool],
    prefix_messages=prefix_msgs,
    llm=OpenAI(model="gpt-4o"),
    verbose=True,
)

```

GPT_BUILDER_SYS_STR = """\ You are helping to construct an agent given a user-specified task. You should generally use the tools in this order to build the agent. 1) Create system prompt tool: to create the system prompt for the agent. 2) Get tools tool: to fetch the candidate set of tools to use. 3) Create agent tool: to create the final agent. """ prefix_msgs = [ChatMessage(role="system", content=GPT_BUILDER_SYS_STR)] builder_agent = FunctionAgent( tools=[system_prompt_tool, get_tools_tool, create_agent_tool], prefix_messages=prefix_msgs, llm=OpenAI(model="gpt-4o"), verbose=True, )
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import ToolCallResult

handler = builder_agent.run("Build an agent that can tell me about Toronto.")
async for event in handler.stream_events():
    if isinstance(event, ToolCallResult):
        print(
            f"Called tool {event.tool_name} with input {event.tool_kwargs}\nGot output: {event.tool_output}"
        )

result = await handler
print(f"Result: {result}")

```

from llama_index.core.agent.workflow import ToolCallResult handler = builder_agent.run("Build an agent that can tell me about Toronto.") async for event in handler.stream_events(): if isinstance(event, ToolCallResult): print( f"Called tool {event.tool_name} with input {event.tool_kwargs}\nGot output: {event.tool_output}" ) result = await handler print(f"Result: {result}")
```
Called tool create_system_prompt with input {'task': 'Tell me about Toronto'}
Got output: "Generate a brief summary about Toronto, including its history, culture, landmarks, and notable features."
Called tool get_tools with input {'task': 'Tell me about Toronto'}
Got output: ['Toronto']
Called tool create_agent with input {'system_prompt': 'Generate a brief summary about Toronto, including its history, culture, landmarks, and notable features.', 'tool_names': ['Toronto']}
Got output: Agent created successfully.
Result: I have created an agent that can provide information about Toronto, including its history, culture, landmarks, and notable features. You can now ask the agent any questions you have about Toronto!

```

In [ ]:
Copied!
```
city_agent = agent_cache["agent"]

```

city_agent = agent_cache["agent"]
In [ ]:
Copied!
```
response = await city_agent.run("Tell me about the parks in Toronto")
print(str(response))

```

response = await city_agent.run("Tell me about the parks in Toronto") print(str(response))
```
Toronto is home to a diverse array of parks and public spaces, offering both urban and natural environments. Key downtown parks include Allan Gardens, Christie Pits, and Trinity Bellwoods Park. For waterfront views, Tommy Thompson Park and the Toronto Islands are popular destinations. In the city's outer areas, large parks like High Park, Humber Bay Park, and Morningside Park provide expansive green spaces. Additionally, parts of Rouge National Urban Park, the largest urban park in North America, are located within Toronto. The city also features notable squares such as Nathan Phillips Square, Yonge–Dundas Square, and Harbourfront Square. Approximately 12.5% of Toronto's land is dedicated to parkland, offering facilities for various activities, including winter sports like ice skating and skiing.

```

