![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Function Calling Anthropic Agent¶
This notebook shows you how to use our Anthropic agent, powered by function calling capabilities.
**NOTE:** Only claude-3* models support function calling using Anthropic's API.
## Initial Setup¶
Let's start by importing some simple building blocks.
The main thing we need is:
  1. the Anthropic API (using our own `llama_index` LLM class)
  2. a place to keep conversation history
  3. a definition for tools that our agent can use.


If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-llms-anthropic
%pip install llama-index-embeddings-openai

```

%pip install llama-index %pip install llama-index-llms-anthropic %pip install llama-index-embeddings-openai
Let's define some very simple calculator tools for our agent.
In [ ]:
Copied!
```
def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b

```

def multiply(a: int, b: int) -> int: """Multiple two integers and returns the result integer""" return a * b def add(a: int, b: int) -> int: """Add two integers and returns the result integer""" return a + b
Make sure your ANTHROPIC_API_KEY is set. Otherwise explicitly specify the `api_key` parameter.
In [ ]:
Copied!
```
from llama_index.llms.anthropic import Anthropic

llm = Anthropic(model="claude-3-opus-20240229", api_key="sk-...")

```

from llama_index.llms.anthropic import Anthropic llm = Anthropic(model="claude-3-opus-20240229", api_key="sk-...")
## Initialize Anthropic Agent¶
Here we initialize a simple Mistral agent with calculator functions.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent

agent = FunctionAgent(
    tools=[multiply, add],
    llm=llm,
)

```

from llama_index.core.agent.workflow import FunctionAgent agent = FunctionAgent( tools=[multiply, add], llm=llm, )
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import ToolCallResult


async def run_agent_verbose(query: str):
    handler = agent.run(query)
    async for event in handler.stream_events():
        if isinstance(event, ToolCallResult):
            print(
                f"Called tool {event.tool_name} with args {event.tool_kwargs}\nGot result: {event.tool_output}"
            )

    return await handler

```

from llama_index.core.agent.workflow import ToolCallResult async def run_agent_verbose(query: str): handler = agent.run(query) async for event in handler.stream_events(): if isinstance(event, ToolCallResult): print( f"Called tool {event.tool_name} with args {event.tool_kwargs}\nGot result: {event.tool_output}" ) return await handler
### Chat¶
In [ ]:
Copied!
```
response = await run_agent_verbose("What is (121 + 2) * 5?")
print(str(response))

```

response = await run_agent_verbose("What is (121 + 2) * 5?") print(str(response))
```
Called tool add with args {'a': 121, 'b': 2}
Got result: 123
Called tool multiply with args {'a': 123, 'b': 5}
Got result: 615
Therefore, (121 + 2) * 5 = 615

```

In [ ]:
Copied!
```
# inspect sources
print(response.tool_calls)

```

# inspect sources print(response.tool_calls)
```
[ToolCallResult(tool_name='add', tool_kwargs={'a': 121, 'b': 2}, tool_id='toolu_01MH6ME7ppxGPSJcCMEUAN5Q', tool_output=ToolOutput(content='123', tool_name='add', raw_input={'args': (), 'kwargs': {'a': 121, 'b': 2}}, raw_output=123, is_error=False), return_direct=False), ToolCallResult(tool_name='multiply', tool_kwargs={'a': 123, 'b': 5}, tool_id='toolu_01JE5TVERND5YC97E68gYoPw', tool_output=ToolOutput(content='615', tool_name='multiply', raw_input={'args': (), 'kwargs': {'a': 123, 'b': 5}}, raw_output=615, is_error=False), return_direct=False)]

```

### Managing Context/Memory¶
By default, `.run()` is stateless. If you want to maintain state, you can pass in a `context` object.
In [ ]:
Copied!
```
from llama_index.core.workflow import Context

ctx = Context(agent)

response = await agent.run("My name is John Doe", ctx=ctx)
response = await agent.run("What is my name?", ctx=ctx)

print(str(response))

```

from llama_index.core.workflow import Context ctx = Context(agent) response = await agent.run("My name is John Doe", ctx=ctx) response = await agent.run("What is my name?", ctx=ctx) print(str(response))
## Anthropic Agent over RAG Pipeline¶
Build a Anthropic agent over a simple 10K document. We use OpenAI embeddings and claude-3-haiku-20240307 to construct the RAG pipeline, and pass it to the Anthropic Opus agent as a tool.
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
```
--2025-03-24 12:52:55--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.111.133, 185.199.108.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.111.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1880483 (1.8M) [application/octet-stream]
Saving to: ‘data/10k/uber_2021.pdf’

data/10k/uber_2021. 100%[===================>]   1.79M  8.98MB/s    in 0.2s    

2025-03-24 12:52:56 (8.98 MB/s) - ‘data/10k/uber_2021.pdf’ saved [1880483/1880483]


```

In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.anthropic import Anthropic

embed_model = OpenAIEmbedding(
    model_name="text-embedding-3-large", api_key="sk-proj-..."
)
query_llm = Anthropic(model="claude-3-haiku-20240307", api_key="sk-...")

# load data
uber_docs = SimpleDirectoryReader(
    input_files=["./data/10k/uber_2021.pdf"]
).load_data()

# build index
uber_index = VectorStoreIndex.from_documents(
    uber_docs, embed_model=embed_model
)
uber_engine = uber_index.as_query_engine(similarity_top_k=3, llm=query_llm)
query_engine_tool = QueryEngineTool.from_defaults(
    query_engine=uber_engine,
    name="uber_10k",
    description=(
        "Provides information about Uber financials for year 2021. "
        "Use a detailed plain text question as input to the tool."
    ),
)

```

from llama_index.core.tools import QueryEngineTool from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.anthropic import Anthropic embed_model = OpenAIEmbedding( model_name="text-embedding-3-large", api_key="sk-proj-..." ) query_llm = Anthropic(model="claude-3-haiku-20240307", api_key="sk-...") # load data uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data() # build index uber_index = VectorStoreIndex.from_documents( uber_docs, embed_model=embed_model ) uber_engine = uber_index.as_query_engine(similarity_top_k=3, llm=query_llm) query_engine_tool = QueryEngineTool.from_defaults( query_engine=uber_engine, name="uber_10k", description=( "Provides information about Uber financials for year 2021. " "Use a detailed plain text question as input to the tool." ), )
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent

agent = FunctionAgent(tools=[query_engine_tool], llm=llm, verbose=True)

```

from llama_index.core.agent.workflow import FunctionAgent agent = FunctionAgent(tools=[query_engine_tool], llm=llm, verbose=True)
In [ ]:
Copied!
```
response = await agent.run(
    "Tell me both the risk factors and tailwinds for Uber?"
)
print(str(response))

```

response = await agent.run( "Tell me both the risk factors and tailwinds for Uber?" ) print(str(response))
```
In summary, based on Uber's 2021 10-K filing, some of the company's key risk factors included:

- Significant expected increases in operating expenses 
- Challenges attracting and retaining drivers, consumers, merchants, shippers, and carriers
- Risks to Uber's brand and reputation
- Challenges from Uber's historical workplace culture 
- Difficulties optimizing organizational structure and managing growth
- Risks related to criminal activity by platform users
- Risks from new offerings and technologies like autonomous vehicles
- Data security and privacy risks
- Climate change exposure 
- Reliance on third-party platforms
- Regulatory and legal risks
- Intellectual property risks

In terms of growth opportunities and tailwinds, Uber's strategy in 2021 focused on restructuring by divesting certain markets and business lines, and instead partnering with and taking minority ownership positions in local ridesharing and delivery companies in those markets. This suggests Uber saw opportunities to still participate in the growth of those markets through its investments, rather than operating independently.

```

