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
from llama_index.core.agent import (
    FunctionCallingAgentWorker,
    ReActAgent,
)

from IPython.display import display, HTML

```

from llama_index.core.tools import FunctionTool from llama_index.core.agent import ( FunctionCallingAgentWorker, ReActAgent, ) from IPython.display import display, HTML
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
agent = ReActAgent.from_tools(
    [multiply_tool, add_tool, subtract_tool], llm=llm, verbose=True
)

```

agent = ReActAgent.from_tools( [multiply_tool, add_tool, subtract_tool], llm=llm, verbose=True )
In [ ]:
Copied!
```
response = agent.chat("What is (26 * 2) + 2024?")

```

response = agent.chat("What is (26 * 2) + 2024?")
```
Thought: The user wants to perform a mathematical operation. I need to first multiply 26 by 2 and then add the result to 2024. I'll use the 'multiply' tool first.
Action: multiply
Action Input: {'a': 26, 'b': 2}
Observation: 52
Thought: The multiplication result is 52. Now, I need to add this result to 2024. I'll use the 'add' tool for this.
Action: add
Action Input: {'a': 52, 'b': 2024}
Observation: 2076
Thought: I can answer without using any more tools. I'll use the user's language to answer.
Answer: 2076

```

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
agent_worker = FunctionCallingAgentWorker.from_tools(
    [multiply_tool, add_tool, subtract_tool],
    llm=llm,
    verbose=True,
    allow_parallel_tool_calls=False,
)
agent = agent_worker.as_agent()

```

agent_worker = FunctionCallingAgentWorker.from_tools( [multiply_tool, add_tool, subtract_tool], llm=llm, verbose=True, allow_parallel_tool_calls=False, ) agent = agent_worker.as_agent()
In [ ]:
Copied!
```
response = agent.chat("What is (26 * 2) + 2024?")

```

response = agent.chat("What is (26 * 2) + 2024?")
```
Added user message to memory: What is (26 * 2) + 2024?
=== Calling Function ===
Calling function: multiply with args: {"a": 26, "b": 2}
=== Function Output ===
52
=== Calling Function ===
Calling function: add with args: {"a": 52, "b": 2024}
=== Function Output ===
2076
=== LLM Response ===
The result of (26 * 2) + 2024 is 2076.

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
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
```
--2024-05-16 14:00:56--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.109.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1880483 (1.8M) [application/octet-stream]
Saving to: ‘./uber_2021.pdf’

./uber_2021.pdf     100%[===================>]   1.79M  8.54MB/s    in 0.2s    

2024-05-16 14:00:57 (8.54 MB/s) - ‘./uber_2021.pdf’ saved [1880483/1880483]

--2024-05-16 14:00:57--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.109.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1440303 (1.4M) [application/octet-stream]
Saving to: ‘./lyft_2021.pdf’

./lyft_2021.pdf     100%[===================>]   1.37M  6.90MB/s    in 0.2s    

2024-05-16 14:00:58 (6.90 MB/s) - ‘./lyft_2021.pdf’ saved [1440303/1440303]


```

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
###  `FunctionCallingAgent` with RAG QueryEngineTools.¶
Here we use `Fuction Calling` capabilities of the model.
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import FunctionCallingAgentWorker

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

agent_worker = FunctionCallingAgentWorker.from_tools(
    query_engine_tools,
    llm=llm,
    verbose=True,
    allow_parallel_tool_calls=False,
)
agent = agent_worker.as_agent()

```

from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.agent import FunctionCallingAgentWorker query_engine_tools = [ QueryEngineTool( query_engine=lyft_query_engine, metadata=ToolMetadata( name="lyft_10k", description="Provides information about Lyft financials for year 2021", ), ), QueryEngineTool( query_engine=uber_query_engine, metadata=ToolMetadata( name="uber_10k", description="Provides information about Uber financials for year 2021", ), ), ] agent_worker = FunctionCallingAgentWorker.from_tools( query_engine_tools, llm=llm, verbose=True, allow_parallel_tool_calls=False, ) agent = agent_worker.as_agent()
In [ ]:
Copied!
```
response = agent.chat("What are the investments of Uber in 2021?")

```

response = agent.chat("What are the investments of Uber in 2021?")
```
Added user message to memory: What are the investments of Uber in 2021?
=== Calling Function ===
Calling function: uber_10k with args: {"input": "investments"}
=== Function Output ===
Uber's investments primarily consist of money market funds, cash deposits, U.S. government and agency securities, and investment-grade corporate debt securities. The company's investment policy aims to preserve capital and meet liquidity requirements without significantly increasing risk. As of December 31, 2021, Uber had cash and cash equivalents including restricted cash and cash equivalents totaling $7.8 billion. They also hold investments in other companies, including minority-owned, privately-held affiliates and recently public companies. The carrying value of these investments was $12.6 billion as of December 31, 2021.
=== LLM Response ===
In 2021, Uber's investments primarily consisted of money market funds, cash deposits, U.S. government and agency securities, and investment-grade corporate debt securities. Their investment policy aims to preserve capital and meet liquidity requirements without significantly increasing risk. As of December 31, 2021, Uber had cash and cash equivalents including restricted cash and cash equivalents totaling $7.8 billion. They also hold investments in other companies, including minority-owned, privately-held affiliates and recently public companies. The carrying value of these investments was $12.6 billion as of December 31, 2021.

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
assistant: In 2021, Uber's investments primarily consisted of money market funds, cash deposits, U.S. government and agency securities, and investment-grade corporate debt securities. Their investment policy aims to preserve capital and meet liquidity requirements without significantly increasing risk. As of December 31, 2021, Uber had cash and cash equivalents including restricted cash and cash equivalents totaling $7.8 billion. They also hold investments in other companies, including minority-owned, privately-held affiliates and recently public companies. The carrying value of these investments was $12.6 billion as of December 31, 2021.
In [ ]:
Copied!
```
response = agent.chat("What are lyft investments in 2021?")

```

response = agent.chat("What are lyft investments in 2021?")
```
Added user message to memory: What are lyft investments in 2021?
=== Calling Function ===
Calling function: lyft_10k with args: {"input": "investments"}
=== Function Output ===
The company's investments include cash and cash equivalents, short-term investments, and restricted investments. Cash and cash equivalents include certificates of deposits, commercial paper, and corporate bonds that have an original maturity of 90 days or less and are readily convertible to known amounts of cash. Short-term investments are comprised of commercial paper, certificates of deposit, and corporate bonds, which mature in twelve months or less. Restricted investments are comprised of debt security investments in commercial paper, certificates of deposit, corporate bonds, and U.S. government securities which are held in trust accounts at third-party financial institutions pursuant to certain contracts with insurance providers. The company also has investments in non-marketable equity securities, which are measured at cost, with remeasurements to fair value only upon the occurrence of observable transactions for identical or similar investments of the same issuer or impairment.
=== LLM Response ===
In 2021, Lyft's investments included cash and cash equivalents, short-term investments, and restricted investments. Cash and cash equivalents included certificates of deposits, commercial paper, and corporate bonds that have an original maturity of 90 days or less and are readily convertible to known amounts of cash. Short-term investments were comprised of commercial paper, certificates of deposit, and corporate bonds, which mature in twelve months or less. 

Restricted investments were comprised of debt security investments in commercial paper, certificates of deposit, corporate bonds, and U.S. government securities which are held in trust accounts at third-party financial institutions pursuant to certain contracts with insurance providers. 

The company also had investments in non-marketable equity securities, which are measured at cost, with remeasurements to fair value only upon the occurrence of observable transactions for identical or similar investments of the same issuer or impairment.

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
assistant: In 2021, Lyft's investments included cash and cash equivalents, short-term investments, and restricted investments. Cash and cash equivalents included certificates of deposits, commercial paper, and corporate bonds that have an original maturity of 90 days or less and are readily convertible to known amounts of cash. Short-term investments were comprised of commercial paper, certificates of deposit, and corporate bonds, which mature in twelve months or less. Restricted investments were comprised of debt security investments in commercial paper, certificates of deposit, corporate bonds, and U.S. government securities which are held in trust accounts at third-party financial institutions pursuant to certain contracts with insurance providers. The company also had investments in non-marketable equity securities, which are measured at cost, with remeasurements to fair value only upon the occurrence of observable transactions for identical or similar investments of the same issuer or impairment.
