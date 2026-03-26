# Agents¶
### Installation¶
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
### Setup LLM and Embedding Model¶
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

import os

os.environ["OPENAI_API_KEY"] = "sk-..."

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

llm = OpenAI(model="gpt-4", temperature=0.1)
embed_model = OpenAIEmbedding()

Settings.llm = llm
Settings.embed_model = embed_model

```

import nest_asyncio nest_asyncio.apply() import os os.environ["OPENAI_API_KEY"] = "sk-..." from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import Settings llm = OpenAI(model="gpt-4", temperature=0.1) embed_model = OpenAIEmbedding() Settings.llm = llm Settings.embed_model = embed_model
### Agents and Tools usage¶
In [ ]:
Copied!
```
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import (
    FunctionAgent,
    ReActAgent,
)

from IPython.display import display, HTML

```

from llama_index.core.tools import FunctionTool from llama_index.core.agent.workflow import ( FunctionAgent, ReActAgent, ) from IPython.display import display, HTML
In [ ]:
Copied!
```
def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract two integers and returns the result integer"""
    return a - b


multiply_tool = FunctionTool.from_defaults(fn=multiply)
add_tool = FunctionTool.from_defaults(fn=add)
subtract_tool = FunctionTool.from_defaults(fn=subtract)

```

def multiply(a: int, b: int) -> int: """Multiply two integers and returns the result integer""" return a * b def add(a: int, b: int) -> int: """Add two integers and returns the result integer""" return a + b def subtract(a: int, b: int) -> int: """Subtract two integers and returns the result integer""" return a - b multiply_tool = FunctionTool.from_defaults(fn=multiply) add_tool = FunctionTool.from_defaults(fn=add) subtract_tool = FunctionTool.from_defaults(fn=subtract)
### With ReAct Agent¶
In [ ]:
Copied!
```
agent = ReActAgent(
    tools=[multiply_tool, add_tool, subtract_tool],
    llm=llm,
)

```

agent = ReActAgent( tools=[multiply_tool, add_tool, subtract_tool], llm=llm, )
In [ ]:
Copied!
```
response = await agent.run("What is (26 * 2) + 2024?")

```

response = await agent.run("What is (26 * 2) + 2024?")
In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
2076
### With Function Calling.¶
In [ ]:
Copied!
```
agent = FunctionAgent(
    tools=[multiply_tool, add_tool, subtract_tool],
    llm=llm,
)

```

agent = FunctionAgent( tools=[multiply_tool, add_tool, subtract_tool], llm=llm, )
In [ ]:
Copied!
```
response = await agent.run("What is (26 * 2) + 2024?")

```

response = await agent.run("What is (26 * 2) + 2024?")
In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response}</p>'))

```

display(HTML(f'
{response}
'))
assistant: The result of (26 * 2) + 2024 is 2076.
## Agent with RAG Query Engine Tools¶
### Download Data¶
We will use `Uber-2021` and `Lyft-2021` 10K SEC filings.
In [ ]:
Copied!
```
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O './uber_2021.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O './lyft_2021.pdf'

```

!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O './uber_2021.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O './lyft_2021.pdf'
### Load Data¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

uber_docs = SimpleDirectoryReader(input_files=["./uber_2021.pdf"]).load_data()
lyft_docs = SimpleDirectoryReader(input_files=["./lyft_2021.pdf"]).load_data()

```

from llama_index.core import SimpleDirectoryReader uber_docs = SimpleDirectoryReader(input_files=["./uber_2021.pdf"]).load_data() lyft_docs = SimpleDirectoryReader(input_files=["./lyft_2021.pdf"]).load_data()
### Build RAG on uber and lyft docs¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

uber_index = VectorStoreIndex.from_documents(uber_docs)
uber_query_engine = uber_index.as_query_engine(similarity_top_k=3)

lyft_index = VectorStoreIndex.from_documents(lyft_docs)
lyft_query_engine = lyft_index.as_query_engine(similarity_top_k=3)

```

from llama_index.core import VectorStoreIndex uber_index = VectorStoreIndex.from_documents(uber_docs) uber_query_engine = uber_index.as_query_engine(similarity_top_k=3) lyft_index = VectorStoreIndex.from_documents(lyft_docs) lyft_query_engine = lyft_index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
response = uber_query_engine.query("What are the investments of Uber in 2021?")

```

response = uber_query_engine.query("What are the investments of Uber in 2021?")
In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
In 2021, Uber made significant investments to expand its international operations and compete with local and other global competitors. This included the acquisitions of Careem and Cornershop. Additionally, Uber continued to develop new technologies to enhance existing offerings and services, and to expand the range of its offerings through research and development. They also launched Uber One in the United States, a cross-platform membership program that brings together the best of Uber.
In [ ]:
Copied!
```
response = lyft_query_engine.query("What are lyft investments in 2021?")

```

response = lyft_query_engine.query("What are lyft investments in 2021?")
In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
In 2021, Lyft continued to invest in expanding its network of Light Vehicles and Lyft Autonomous, focusing on the deployment and scaling of third-party self-driving technology on the Lyft network. The company also made a commitment to reach 100% electric vehicles on the Lyft network by the end of 2030. Additionally, Lyft completed a transaction with Woven Planet, a subsidiary of Toyota Motor Corporation, for the divestiture of certain assets related to its self-driving vehicle division, Level 5.
###  `FunctionAgent` with RAG QueryEngineTools.¶
Here we use `Fuction Calling` capabilities of the model.
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent.workflow import FunctionAgent

query_engine_tools = [
    QueryEngineTool(
        query_engine=lyft_query_engine,
        metadata=ToolMetadata(
            name="lyft_10k",
            description="Provides information about Lyft financials for year 2021",
        ),
    ),
    QueryEngineTool(
        query_engine=uber_query_engine,
        metadata=ToolMetadata(
            name="uber_10k",
            description="Provides information about Uber financials for year 2021",
        ),
    ),
]

agent = FunctionAgent(
    tools=query_engine_tools,
    llm=llm,
)

```

from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.agent.workflow import FunctionAgent query_engine_tools = [ QueryEngineTool( query_engine=lyft_query_engine, metadata=ToolMetadata( name="lyft_10k", description="Provides information about Lyft financials for year 2021", ), ), QueryEngineTool( query_engine=uber_query_engine, metadata=ToolMetadata( name="uber_10k", description="Provides information about Uber financials for year 2021", ), ), ] agent = FunctionAgent( tools=query_engine_tools, llm=llm, )
In [ ]:
Copied!
```
response = await agent.run("What are the investments of Uber in 2021?")

```

response = await agent.run("What are the investments of Uber in 2021?")
In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response}</p>'))

```

display(HTML(f'
{response}
'))
assistant: In 2021, Uber's investments primarily consisted of money market funds, cash deposits, U.S. government and agency securities, and investment-grade corporate debt securities. Their investment policy aims to preserve capital and meet liquidity requirements without significantly increasing risk. As of December 31, 2021, Uber had cash and cash equivalents including restricted cash and cash equivalents totaling $7.8 billion. They also hold investments in other companies, including minority-owned, privately-held affiliates and recently public companies. The carrying value of these investments was $12.6 billion as of December 31, 2021.
In [ ]:
Copied!
```
response = await agent.run("What are lyft investments in 2021?")

```

response = await agent.run("What are lyft investments in 2021?")
In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response}</p>'))

```

display(HTML(f'
{response}
'))
assistant: In 2021, Lyft's investments included cash and cash equivalents, short-term investments, and restricted investments. Cash and cash equivalents included certificates of deposits, commercial paper, and corporate bonds that have an original maturity of 90 days or less and are readily convertible to known amounts of cash. Short-term investments were comprised of commercial paper, certificates of deposit, and corporate bonds, which mature in twelve months or less. Restricted investments were comprised of debt security investments in commercial paper, certificates of deposit, corporate bonds, and U.S. government securities which are held in trust accounts at third-party financial institutions pursuant to certain contracts with insurance providers. The company also had investments in non-marketable equity securities, which are measured at cost, with remeasurements to fair value only upon the occurrence of observable transactions for identical or similar investments of the same issuer or impairment.
