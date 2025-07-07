![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Context-Augmented Function Calling Agent¶
In this tutorial, we show you how to to make your agent context-aware.
Our indexing/retrieval modules help to remove the complexity of having too many functions to fit in the prompt.
## Initial Setup¶
Here we setup a normal FunctionAgent, and then augment it with context. This agent will perform retrieval first before calling any tools. This can help ground the agent's tool picking and answering capabilities in context.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
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
from llama_index.core.settings import Settings

Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

```

from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core.settings import Settings Settings.llm = OpenAI(model="gpt-4o-mini") Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
In [ ]:
Copied!
```
import json
from typing import Sequence

from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.tools import QueryEngineTool

```

import json from typing import Sequence from llama_index.core import ( SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, ) from llama_index.core.tools import QueryEngineTool
In [ ]:
Copied!
```
try:
    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/march"
    )
    march_index = load_index_from_storage(storage_context)

    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/june"
    )
    june_index = load_index_from_storage(storage_context)

    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/sept"
    )
    sept_index = load_index_from_storage(storage_context)

    index_loaded = True
except:
    index_loaded = False

```

try: storage_context = StorageContext.from_defaults( persist_dir="./storage/march" ) march_index = load_index_from_storage(storage_context) storage_context = StorageContext.from_defaults( persist_dir="./storage/june" ) june_index = load_index_from_storage(storage_context) storage_context = StorageContext.from_defaults( persist_dir="./storage/sept" ) sept_index = load_index_from_storage(storage_context) index_loaded = True except: index_loaded = False
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/10q/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_march_2022.pdf' -O 'data/10q/uber_10q_march_2022.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_june_2022.pdf' -O 'data/10q/uber_10q_june_2022.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_sept_2022.pdf' -O 'data/10q/uber_10q_sept_2022.pdf'

```

!mkdir -p 'data/10q/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_march_2022.pdf' -O 'data/10q/uber_10q_march_2022.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_june_2022.pdf' -O 'data/10q/uber_10q_june_2022.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_sept_2022.pdf' -O 'data/10q/uber_10q_sept_2022.pdf'
In [ ]:
Copied!
```
# build indexes across the three data sources
if not index_loaded:
    # load data
    march_docs = SimpleDirectoryReader(
        input_files=["./data/10q/uber_10q_march_2022.pdf"]
    ).load_data()
    june_docs = SimpleDirectoryReader(
        input_files=["./data/10q/uber_10q_june_2022.pdf"]
    ).load_data()
    sept_docs = SimpleDirectoryReader(
        input_files=["./data/10q/uber_10q_sept_2022.pdf"]
    ).load_data()

    # build index
    march_index = VectorStoreIndex.from_documents(march_docs)
    june_index = VectorStoreIndex.from_documents(june_docs)
    sept_index = VectorStoreIndex.from_documents(sept_docs)

    # persist index
    march_index.storage_context.persist(persist_dir="./storage/march")
    june_index.storage_context.persist(persist_dir="./storage/june")
    sept_index.storage_context.persist(persist_dir="./storage/sept")

```

# build indexes across the three data sources if not index_loaded: # load data march_docs = SimpleDirectoryReader( input_files=["./data/10q/uber_10q_march_2022.pdf"] ).load_data() june_docs = SimpleDirectoryReader( input_files=["./data/10q/uber_10q_june_2022.pdf"] ).load_data() sept_docs = SimpleDirectoryReader( input_files=["./data/10q/uber_10q_sept_2022.pdf"] ).load_data() # build index march_index = VectorStoreIndex.from_documents(march_docs) june_index = VectorStoreIndex.from_documents(june_docs) sept_index = VectorStoreIndex.from_documents(sept_docs) # persist index march_index.storage_context.persist(persist_dir="./storage/march") june_index.storage_context.persist(persist_dir="./storage/june") sept_index.storage_context.persist(persist_dir="./storage/sept")
In [ ]:
Copied!
```
march_engine = march_index.as_query_engine(similarity_top_k=3)
june_engine = june_index.as_query_engine(similarity_top_k=3)
sept_engine = sept_index.as_query_engine(similarity_top_k=3)

```

march_engine = march_index.as_query_engine(similarity_top_k=3) june_engine = june_index.as_query_engine(similarity_top_k=3) sept_engine = sept_index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
query_engine_tools = [
    QueryEngineTool.from_defaults(
        query_engine=march_engine,
        name="uber_march_10q",
        description=(
            "Provides information about Uber 10Q filings for March 2022. "
            "Use a detailed plain text question as input to the tool."
        ),
    ),
    QueryEngineTool.from_defaults(
        query_engine=june_engine,
        name="uber_june_10q",
        description=(
            "Provides information about Uber financials for June 2021. "
            "Use a detailed plain text question as input to the tool."
        ),
    ),
    QueryEngineTool.from_defaults(
        query_engine=sept_engine,
        name="uber_sept_10q",
        description=(
            "Provides information about Uber financials for Sept 2021. "
            "Use a detailed plain text question as input to the tool."
        ),
    ),
]

```

query_engine_tools = [ QueryEngineTool.from_defaults( query_engine=march_engine, name="uber_march_10q", description=( "Provides information about Uber 10Q filings for March 2022. " "Use a detailed plain text question as input to the tool." ), ), QueryEngineTool.from_defaults( query_engine=june_engine, name="uber_june_10q", description=( "Provides information about Uber financials for June 2021. " "Use a detailed plain text question as input to the tool." ), ), QueryEngineTool.from_defaults( query_engine=sept_engine, name="uber_sept_10q", description=( "Provides information about Uber financials for Sept 2021. " "Use a detailed plain text question as input to the tool." ), ), ]
### Try Context-Augmented Agent¶
Here we augment our agent with context in different settings:
  * toy context: we define some abbreviations that map to financial terms (e.g. R=Revenue). We supply this as context to the agent


In [ ]:
Copied!
```
from llama_index.core import Document
from llama_index.core.agent.workflow import FunctionAgent

```

from llama_index.core import Document from llama_index.core.agent.workflow import FunctionAgent
In [ ]:
Copied!
```
# toy index - stores a list of abbreviations
texts = [
    "Abbreviation: 'Y' = Revenue",
    "Abbreviation: 'X' = Risk Factors",
    "Abbreviation: 'Z' = Costs",
]
docs = [Document(text=t) for t in texts]
context_index = VectorStoreIndex.from_documents(docs)
context_retriever = context_index.as_retriever(similarity_top_k=2)

```

# toy index - stores a list of abbreviations texts = [ "Abbreviation: 'Y' = Revenue", "Abbreviation: 'X' = Risk Factors", "Abbreviation: 'Z' = Costs", ] docs = [Document(text=t) for t in texts] context_index = VectorStoreIndex.from_documents(docs) context_retriever = context_index.as_retriever(similarity_top_k=2)
In [ ]:
Copied!
```
from llama_index.core.tools import BaseTool

system_prompt_template = """You are a helpful assistant. 
Here is some context that you can use to answer the user's question and for help with picking the right tool:

{context}
"""


async def get_agent_with_context_awareness(
    query: str, context_retriever, tools: list[BaseTool]
) -> FunctionAgent:
    context_nodes = await context_retriever.aretrieve(query)
    context_text = "\n----\n".join([n.node.text for n in context_nodes])

    return FunctionAgent(
        tools=tools,
        llm=OpenAI(model="gpt-4o"),
        system_prompt=system_prompt_template.format(context=context_text),
    )

```

from llama_index.core.tools import BaseTool system_prompt_template = """You are a helpful assistant. Here is some context that you can use to answer the user's question and for help with picking the right tool: {context} """ async def get_agent_with_context_awareness( query: str, context_retriever, tools: list[BaseTool] ) -> FunctionAgent: context_nodes = await context_retriever.aretrieve(query) context_text = "\n----\n".join([n.node.text for n in context_nodes]) return FunctionAgent( tools=tools, llm=OpenAI(model="gpt-4o"), system_prompt=system_prompt_template.format(context=context_text), )
In [ ]:
Copied!
```
query = "What is the 'X' of March 2022?"
agent = await get_agent_with_context_awareness(
    query, context_retriever, query_engine_tools
)

response = await agent.run(query)

```

query = "What is the 'X' of March 2022?" agent = await get_agent_with_context_awareness( query, context_retriever, query_engine_tools ) response = await agent.run(query)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The risk factors mentioned in Uber's 10-Q filing for March 2022 include uncertainties related to the COVID-19 pandemic, such as the severity and duration of the outbreak, potential future waves or variants of the virus, the administration and efficacy of vaccines, and the impact of governmental actions. There are also concerns regarding the effects on drivers, merchants, consumers, and business partners, as well as other factors that may affect the company's business, results of operations, financial position, and cash flows.

```

In [ ]:
Copied!
```
query = "What is the 'Y' and 'Z' in September 2022?"
agent = await get_agent_with_context_awareness(
    query, context_retriever, query_engine_tools
)

response = await agent.run(query)

```

query = "What is the 'Y' and 'Z' in September 2022?" agent = await get_agent_with_context_awareness( query, context_retriever, query_engine_tools ) response = await agent.run(query)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
In September 2022, Uber's revenue (Y) was $8,343 million, and the total costs (Z) were $8,839 million.

```

### Managing Context/Memory¶
By default, each `.run()` call is stateless. We can manage context by using a serializable `Context` object.
In [ ]:
Copied!
```
from llama_index.core.workflow import Context

ctx = Context(agent)

query = "What is the 'Y' and 'Z' in September 2022?"
agent = await get_agent_with_context_awareness(
    query, context_retriever, query_engine_tools
)
response = await agent.run(query, ctx=ctx)

query = "What did I just ask?"
agent = await get_agent_with_context_awareness(
    query, context_retriever, query_engine_tools
)
response = await agent.run(query, ctx=ctx)
print(str(response))

```

from llama_index.core.workflow import Context ctx = Context(agent) query = "What is the 'Y' and 'Z' in September 2022?" agent = await get_agent_with_context_awareness( query, context_retriever, query_engine_tools ) response = await agent.run(query, ctx=ctx) query = "What did I just ask?" agent = await get_agent_with_context_awareness( query, context_retriever, query_engine_tools ) response = await agent.run(query, ctx=ctx) print(str(response))
```
You asked for the revenue ('Y') and costs ('Z') for Uber in September 2022.

```

### Use Uber 10-Q as context, use Calculator as Tool¶
In [ ]:
Copied!
```
from llama_index.core.tools import FunctionTool


def magic_formula(revenue: int, cost: int) -> int:
    """Runs MAGIC_FORMULA on revenue and cost."""
    return revenue - cost


magic_tool = FunctionTool.from_defaults(magic_formula)

```

from llama_index.core.tools import FunctionTool def magic_formula(revenue: int, cost: int) -> int: """Runs MAGIC_FORMULA on revenue and cost.""" return revenue - cost magic_tool = FunctionTool.from_defaults(magic_formula)
In [ ]:
Copied!
```
context_retriever = sept_index.as_retriever(similarity_top_k=3)

```

context_retriever = sept_index.as_retriever(similarity_top_k=3)
In [ ]:
Copied!
```
query = "Can you run MAGIC_FORMULA on Uber's revenue and cost?"
agent = await get_agent_with_context_awareness(
    query, context_retriever, [magic_tool]
)
response = await agent.run(query)
print(str(response))

```

query = "Can you run MAGIC_FORMULA on Uber's revenue and cost?" agent = await get_agent_with_context_awareness( query, context_retriever, [magic_tool] ) response = await agent.run(query) print(str(response))
```
The result of running MAGIC_FORMULA on Uber's revenue of $8,343 million and cost of $5,173 million is 3,170.

```

