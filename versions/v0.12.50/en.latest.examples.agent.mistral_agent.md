![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Function Calling Mistral Agent¶
This notebook shows you how to use our Mistral agent, powered by function calling capabilities.
## Initial Setup¶
Let's start by importing some simple building blocks.
The main thing we need is:
  1. the OpenAI API (using our own `llama_index` LLM class)
  2. a place to keep conversation history
  3. a definition for tools that our agent can use.


If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-llms-mistralai
%pip install llama-index-embeddings-mistralai

```

%pip install llama-index %pip install llama-index-llms-mistralai %pip install llama-index-embeddings-mistralai
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
Make sure your MISTRAL_API_KEY is set. Otherwise explicitly specify the `api_key` parameter.
In [ ]:
Copied!
```
from llama_index.llms.mistralai import MistralAI

llm = MistralAI(model="mistral-large-latest", api_key="...")

```

from llama_index.llms.mistralai import MistralAI llm = MistralAI(model="mistral-large-latest", api_key="...")
## Initialize Mistral Agent¶
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
### Chat¶
In [ ]:
Copied!
```
response = await agent.run("What is (121 + 2) * 5?")
print(str(response))

```

response = await agent.run("What is (121 + 2) * 5?") print(str(response))
```
Added user message to memory: What is (121 + 2) * 5?
=== Calling Function ===
Calling function: add with args: {"a": 121, "b": 2}
=== Calling Function ===
Calling function: multiply with args: {"a": 123, "b": 5}
assistant: The result of (121 + 2) * 5 is 615.

```

In [ ]:
Copied!
```
# inspect sources
print(response.tool_calls)

```

# inspect sources print(response.tool_calls)
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
## Mistral Agent over RAG Pipeline¶
Build a Mistral agent over a simple 10K document. We use both Mistral embeddings and mistral-medium to construct the RAG pipeline, and pass it to the Mistral agent as a tool.
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
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.llms.mistralai import MistralAI

embed_model = MistralAIEmbedding(api_key="...")
query_llm = MistralAI(model="mistral-medium", api_key="...")

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

from llama_index.core.tools import QueryEngineTool from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.embeddings.mistralai import MistralAIEmbedding from llama_index.llms.mistralai import MistralAI embed_model = MistralAIEmbedding(api_key="...") query_llm = MistralAI(model="mistral-medium", api_key="...") # load data uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data() # build index uber_index = VectorStoreIndex.from_documents( uber_docs, embed_model=embed_model ) uber_engine = uber_index.as_query_engine(similarity_top_k=3, llm=query_llm) query_engine_tool = QueryEngineTool.from_defaults( query_engine=uber_engine, name="uber_10k", description=( "Provides information about Uber financials for year 2021. " "Use a detailed plain text question as input to the tool." ), )
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent

agent = FunctionAgent(tools=[query_engine_tool], llm=llm)

```

from llama_index.core.agent.workflow import FunctionAgent agent = FunctionAgent(tools=[query_engine_tool], llm=llm)
In [ ]:
Copied!
```
response = await agent.run(
    "Tell me both the risk factors and tailwinds for Uber? Do two parallel tool calls."
)
print(str(response))

```

response = await agent.run( "Tell me both the risk factors and tailwinds for Uber? Do two parallel tool calls." ) print(str(response))
```
Added user message to memory: Tell me both the risk factors and tailwinds for Uber? Do two parallel tool calls.
=== Calling Function ===
Calling function: uber_10k with args: {"input": "What are the risk factors for Uber in 2021?"}
=== Calling Function ===
Calling function: uber_10k with args: {"input": "What are the tailwinds for Uber in 2021?"}
assistant: Based on the information provided, here are the risk factors for Uber in 2021:

1. Failure to offer or develop autonomous vehicle technologies, which could result in inferior performance or safety concerns compared to competitors.
2. Dependence on high-quality personnel and the potential impact of attrition or unsuccessful succession planning on the business.
3. Security or data privacy breaches, unauthorized access, or destruction of proprietary, employee, or user data.
4. Cyberattacks, such as malware, ransomware, viruses, spamming, and phishing attacks, which could harm the company's reputation and operations.
5. Climate change risks, including physical and transitional risks, that may adversely impact the business if not managed effectively.
6. Reliance on third parties to maintain open marketplaces for distributing products and providing software, which could negatively affect the business if interfered with.
7. The need for additional capital to support business growth, which may not be available on reasonable terms or at all.
8. Difficulties in identifying, acquiring, and integrating suitable businesses, which could harm operating results and prospects.
9. Legal and regulatory risks, including extensive government regulation and oversight related to payment and financial services.
10. Intellectual property risks, such as the inability to protect intellectual property or claims of misappropriation by third parties.
11. Volatility in the market price of common stock, which could result in steep declines and loss of investment for shareholders.
12. Economic risks related to the COVID-19 pandemic, which has adversely impacted and could continue to adversely impact the business, financial condition, and results of operations.
13. The potential reclassification of Drivers as employees, workers, or quasi-employees, which could result in material costs associated with defending, settling, or resolving lawsuits and demands for arbitration.

On the other hand, here are some tailwinds for Uber in 2021:

1. Launch of Uber One, a single cross-platform membership program in the United States, which offers discounts, special pricing, priority service, and exclusive perks across rides, delivery, and grocery offerings.
2. Introduction of a "Super App" view on iOS

```

