# Function Calling Google Gemini Agent¶
This notebook shows you how to use Google Gemini Agent, powered by function calling capabilities.
Google's Gemini 2.5 Pro, Gemini 2.5 Flash, Gemini 2.5 Flash-Lite, Gemini 2.0 Flash models support function calling capabilities. You can find a comprehensive capabilities overview on the model overview page.
## Initial Setup¶
Let's start by importing some simple building blocks.
The main thing we need is:
  1. the Google Gemini API (using our own llama_index LLM class)
  2. a place to keep conversation history
  3. a definition for tools that our agent can use.


If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-google-genai llama-index -q

```

%pip install llama-index-llms-google-genai llama-index -q
In [ ]:
Copied!
```
# import os

# os.environ["GOOGLE_API_KEY"] = "..."

```

# import os # os.environ["GOOGLE_API_KEY"] = "..."
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
Make sure your GOOGLE_API_KEY is set. Otherwise explicitly specify the api_key parameter.
In [ ]:
Copied!
```
from llama_index.llms.google_genai import GoogleGenAI
from google.genai import types

llm = GoogleGenAI(
    model="gemini-2.5-flash",
    generation_config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_budget=0
        )  # Disables thinking
    ),
)

```

from llama_index.llms.google_genai import GoogleGenAI from google.genai import types llm = GoogleGenAI( model="gemini-2.5-flash", generation_config=types.GenerateContentConfig( thinking_config=types.ThinkingConfig( thinking_budget=0 ) # Disables thinking ), )
## Initialize Google Gemini Agent¶
Here we initialize a simple Google Gemini Agent agent with calculator functions.
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
Called tool add with args {'b': 2, 'a': 121}
Got result: 123
Called tool multiply with args {'a': 123, 'b': 5}
Got result: 615
The answer is 615.

```

In [ ]:
Copied!
```
# inspect sources
print(response.tool_calls)

```

# inspect sources print(response.tool_calls)
```
[ToolCallResult(tool_name='add', tool_kwargs={'b': 2, 'a': 121}, tool_id='add', tool_output=ToolOutput(content='123', tool_name='add', raw_input={'args': (), 'kwargs': {'b': 2, 'a': 121}}, raw_output=123, is_error=False), return_direct=False), ToolCallResult(tool_name='multiply', tool_kwargs={'a': 123, 'b': 5}, tool_id='multiply', tool_output=ToolOutput(content='615', tool_name='multiply', raw_input={'args': (), 'kwargs': {'a': 123, 'b': 5}}, raw_output=615, is_error=False), return_direct=False)]

```

### Managing Context/Memory¶
By default, `.run()` is stateless. If you want to maintain state, you can pass in a context object.
In [ ]:
Copied!
```
from llama_index.core.workflow import Context

agent = FunctionAgent(llm=llm)
ctx = Context(agent)

response = await agent.run("My name is John Doe", ctx=ctx)
response = await agent.run("What is my name?", ctx=ctx)

print(str(response))

```

from llama_index.core.workflow import Context agent = FunctionAgent(llm=llm) ctx = Context(agent) response = await agent.run("My name is John Doe", ctx=ctx) response = await agent.run("What is my name?", ctx=ctx) print(str(response))
```
Your name is John Doe.

```

## Google Gemini Agent over RAG Pipeline¶
Build a Anthropic agent over a simple 10K document. We use OpenAI embeddings and Gemini 2.0 Flash to construct the RAG pipeline, and pass it to the Gemini 2.5 Flash agent as a tool.
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.google_genai import GoogleGenAI

embed_model = OpenAIEmbedding(model_name="text-embedding-3-large")
query_llm = GoogleGenAI(model="gemini-2.0-flash")

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

from llama_index.core.tools import QueryEngineTool from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.google_genai import GoogleGenAI embed_model = OpenAIEmbedding(model_name="text-embedding-3-large") query_llm = GoogleGenAI(model="gemini-2.0-flash") # load data uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data() # build index uber_index = VectorStoreIndex.from_documents( uber_docs, embed_model=embed_model ) uber_engine = uber_index.as_query_engine(similarity_top_k=3, llm=query_llm) query_engine_tool = QueryEngineTool.from_defaults( query_engine=uber_engine, name="uber_10k", description=( "Provides information about Uber financials for year 2021. " "Use a detailed plain text question as input to the tool." ), )
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
