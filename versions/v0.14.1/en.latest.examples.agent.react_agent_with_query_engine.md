![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# ReAct Agent with Query Engine (RAG) Tools¶
In this section, we show how to setup an agent powered by the ReAct loop for financial analysis.
The agent has access to two "tools": one to query the 2021 Lyft 10-K and the other to query the 2021 Uber 10-K.
Note that you can plug in any LLM to use as a ReAct agent.
## Build Query Engine Tools¶
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
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
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

```

from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-4o-mini") Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
In [ ]:
Copied!
```
from llama_index.core import StorageContext, load_index_from_storage

try:
    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/lyft"
    )
    lyft_index = load_index_from_storage(storage_context)

    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/uber"
    )
    uber_index = load_index_from_storage(storage_context)

    index_loaded = True
except:
    index_loaded = False

```

from llama_index.core import StorageContext, load_index_from_storage try: storage_context = StorageContext.from_defaults( persist_dir="./storage/lyft" ) lyft_index = load_index_from_storage(storage_context) storage_context = StorageContext.from_defaults( persist_dir="./storage/uber" ) uber_index = load_index_from_storage(storage_context) index_loaded = True except: index_loaded = False
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

if not index_loaded:
    # load data
    lyft_docs = SimpleDirectoryReader(
        input_files=["./data/10k/lyft_2021.pdf"]
    ).load_data()
    uber_docs = SimpleDirectoryReader(
        input_files=["./data/10k/uber_2021.pdf"]
    ).load_data()

    # build index
    lyft_index = VectorStoreIndex.from_documents(lyft_docs)
    uber_index = VectorStoreIndex.from_documents(uber_docs)

    # persist index
    lyft_index.storage_context.persist(persist_dir="./storage/lyft")
    uber_index.storage_context.persist(persist_dir="./storage/uber")

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex if not index_loaded: # load data lyft_docs = SimpleDirectoryReader( input_files=["./data/10k/lyft_2021.pdf"] ).load_data() uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data() # build index lyft_index = VectorStoreIndex.from_documents(lyft_docs) uber_index = VectorStoreIndex.from_documents(uber_docs) # persist index lyft_index.storage_context.persist(persist_dir="./storage/lyft") uber_index.storage_context.persist(persist_dir="./storage/uber")
In [ ]:
Copied!
```
lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)
uber_engine = uber_index.as_query_engine(similarity_top_k=3)

```

lyft_engine = lyft_index.as_query_engine(similarity_top_k=3) uber_engine = uber_index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool

query_engine_tools = [
    QueryEngineTool.from_defaults(
        query_engine=lyft_engine,
        name="lyft_10k",
        description=(
            "Provides information about Lyft financials for year 2021. "
            "Use a detailed plain text question as input to the tool."
        ),
    ),
    QueryEngineTool.from_defaults(
        query_engine=uber_engine,
        name="uber_10k",
        description=(
            "Provides information about Uber financials for year 2021. "
            "Use a detailed plain text question as input to the tool."
        ),
    ),
]

```

from llama_index.core.tools import QueryEngineTool query_engine_tools = [ QueryEngineTool.from_defaults( query_engine=lyft_engine, name="lyft_10k", description=( "Provides information about Lyft financials for year 2021. " "Use a detailed plain text question as input to the tool." ), ), QueryEngineTool.from_defaults( query_engine=uber_engine, name="uber_10k", description=( "Provides information about Uber financials for year 2021. " "Use a detailed plain text question as input to the tool." ), ), ]
## Setup ReAct Agent¶
Here we setup our ReAct agent with the tools we created above.
You can **optionally** specify a system prompt which will be added to the core ReAct system prompt.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context

agent = ReActAgent(
    tools=query_engine_tools,
    llm=OpenAI(model="gpt-4o-mini"),
    # system_prompt="..."
)

# context to hold this session/state

ctx = Context(agent)

```

from llama_index.core.agent.workflow import ReActAgent from llama_index.core.workflow import Context agent = ReActAgent( tools=query_engine_tools, llm=OpenAI(model="gpt-4o-mini"), # system_prompt="..." ) # context to hold this session/state ctx = Context(agent)
## Run Some Example Queries¶
By streaming the result, we can see the full response, including the thought process and tool calls.
If we wanted to stream only the result, we can buffer the stream and start streaming once `Answer:` is in the response.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import ToolCallResult, AgentStream

handler = agent.run("What was Lyft's revenue growth in 2021?", ctx=ctx)

async for ev in handler.stream_events():
    # if isinstance(ev, ToolCallResult):
    #     print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}")
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)

response = await handler

```

from llama_index.core.agent.workflow import ToolCallResult, AgentStream handler = agent.run("What was Lyft's revenue growth in 2021?", ctx=ctx) async for ev in handler.stream_events(): # if isinstance(ev, ToolCallResult): # print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}") if isinstance(ev, AgentStream): print(f"{ev.delta}", end="", flush=True) response = await handler
```
Thought: The current language of the user is: English. I need to use a tool to help me answer the question.
Action: lyft_10k
Action Input: {"input": "What was Lyft's revenue growth in 2021?"}Thought: I can answer without using any more tools. I'll use the user's language to answer.
Answer: Lyft's revenue growth in 2021 was 36% compared to the prior year.
```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Lyft's revenue growth in 2021 was 36% compared to the prior year.

```

In [ ]:
Copied!
```
handler = agent.run(
    "Compare and contrast the revenue growth of Uber and Lyft in 2021, then give an analysis",
    ctx=ctx,
)

async for ev in handler.stream_events():
    # if isinstance(ev, ToolCallResult):
    #     print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}")
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)

response = await handler

```

handler = agent.run( "Compare and contrast the revenue growth of Uber and Lyft in 2021, then give an analysis", ctx=ctx, ) async for ev in handler.stream_events(): # if isinstance(ev, ToolCallResult): # print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}") if isinstance(ev, AgentStream): print(f"{ev.delta}", end="", flush=True) response = await handler
```
Thought: The current language of the user is: English. I need to use a tool to gather information about Uber's revenue growth in 2021 to compare it with Lyft's.
Action: uber_10k
Action Input: {'input': "What was Uber's revenue growth in 2021?"}Thought: I now have the revenue growth information for both Uber and Lyft in 2021. Lyft's revenue growth was 36%, while Uber's was 57%. I will now provide a comparison and analysis.
Thought: I can answer without using any more tools. I'll use the user's language to answer.
Answer: In 2021, Uber experienced a revenue growth of 57%, increasing from $11.139 billion in 2020 to $17.455 billion. In contrast, Lyft's revenue growth was 36%. 

When comparing the two, Uber outperformed Lyft in terms of revenue growth, indicating a stronger recovery or expansion in its business operations during that year. This could be attributed to Uber's diversified services, including food delivery through Uber Eats, which may have contributed significantly to its revenue. Lyft, primarily focused on ride-sharing, may have faced more challenges in scaling its growth compared to Uber.

Overall, while both companies showed positive growth, Uber's higher percentage suggests it was able to capitalize on market opportunities more effectively than Lyft in 2021.
```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
In 2021, Uber experienced a revenue growth of 57%, increasing from $11.139 billion in 2020 to $17.455 billion. In contrast, Lyft's revenue growth was 36%. 

When comparing the two, Uber outperformed Lyft in terms of revenue growth, indicating a stronger recovery or expansion in its business operations during that year. This could be attributed to Uber's diversified services, including food delivery through Uber Eats, which may have contributed significantly to its revenue. Lyft, primarily focused on ride-sharing, may have faced more challenges in scaling its growth compared to Uber.

Overall, while both companies showed positive growth, Uber's higher percentage suggests it was able to capitalize on market opportunities more effectively than Lyft in 2021.

```

