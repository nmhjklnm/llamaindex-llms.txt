![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# MistralAI Cookbook¶
MistralAI released mixtral-8x22b.
It is a sparse Mixture-of-Experts (SMoE) model that uses only 39B active parameters out of 141B, offering unparalleled cost efficiency for its size with 64K tokens context window, multilingual, strong maths coding, coding and Function calling capabilities.
This is a cook-book in showcasing the usage of `mixtral-8x22b` model with llama-index.
### Setup LLM and Embedding Model¶
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

import os

os.environ["MISTRAL_API_KEY"] = "<YOUR MISTRAL API KEY>"

from llama_index.llms.mistralai import MistralAI
from llama_index.embeddings.mistralai import MistralAIEmbedding
from llama_index.core import Settings

llm = MistralAI(model="open-mixtral-8x22b", temperature=0.1)
embed_model = MistralAIEmbedding(model_name="mistral-embed")

Settings.llm = llm
Settings.embed_model = embed_model

```

import nest_asyncio nest_asyncio.apply() import os os.environ["MISTRAL_API_KEY"] = "" from llama_index.llms.mistralai import MistralAI from llama_index.embeddings.mistralai import MistralAIEmbedding from llama_index.core import Settings llm = MistralAI(model="open-mixtral-8x22b", temperature=0.1) embed_model = MistralAIEmbedding(model_name="mistral-embed") Settings.llm = llm Settings.embed_model = embed_model
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
--2024-04-17 20:33:54--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8000::154, 2606:50c0:8001::154, 2606:50c0:8002::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8000::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1880483 (1.8M) [application/octet-stream]
Saving to: './uber_2021.pdf'

./uber_2021.pdf     100%[===================>]   1.79M  --.-KB/s    in 0.1s    

2024-04-17 20:33:54 (18.5 MB/s) - './uber_2021.pdf' saved [1880483/1880483]

--2024-04-17 20:33:55--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8001::154, 2606:50c0:8002::154, 2606:50c0:8003::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8001::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1440303 (1.4M) [application/octet-stream]
Saving to: './lyft_2021.pdf'

./lyft_2021.pdf     100%[===================>]   1.37M  --.-KB/s    in 0.1s    

2024-04-17 20:33:55 (11.6 MB/s) - './lyft_2021.pdf' saved [1440303/1440303]


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
uber_query_engine = uber_index.as_query_engine(similarity_top_k=5)

lyft_index = VectorStoreIndex.from_documents(lyft_docs)
lyft_query_engine = lyft_index.as_query_engine(similarity_top_k=5)

```

from llama_index.core import VectorStoreIndex uber_index = VectorStoreIndex.from_documents(uber_docs) uber_query_engine = uber_index.as_query_engine(similarity_top_k=5) lyft_index = VectorStoreIndex.from_documents(lyft_docs) lyft_query_engine = lyft_index.as_query_engine(similarity_top_k=5)
In [ ]:
Copied!
```
response = uber_query_engine.query("What is the revenue of uber in 2021?")
print(response)

```

response = uber_query_engine.query("What is the revenue of uber in 2021?") print(response)
```
Uber's revenue in 2021 was $17,455 million.

```

In [ ]:
Copied!
```
response = lyft_query_engine.query("What are lyft investments in 2021?")
print(response)

```

response = lyft_query_engine.query("What are lyft investments in 2021?") print(response)
```
In 2021, Lyft invested in several areas to advance its mission and maintain its position as a leader in the transportation industry. These investments include:

1. Expansion of Light Vehicles and Lyft Autonomous: Lyft continued to invest in the expansion of its network of Light Vehicles and Lyft Autonomous, focusing on the deployment and scaling of third-party self-driving technology on the Lyft network.

2. Efficient Operations: Lyft remained focused on finding ways to operate more efficiently while continuing to invest in the business.

3. Brand and Social Responsibility: Lyft aimed to build the defining brand of its generation and advocate through its commitment to social and environmental responsibility. This includes initiatives like LyftUp, which aims to make affordable and reliable transportation accessible to people regardless of their income or zip code.

4. Electric Vehicles: Lyft committed to reaching 100% electric vehicles (EVs) on its network by the end of 2030.

5. Driver Experience: Lyft invested in improving the driver experience, including access to rental cars for ridesharing through the Express Drive program and affordable and convenient vehicle maintenance services through Driver Centers and Mobile Services.

6. Marketplace Technology: Lyft invested in its proprietary technology to deliver a convenient and high-quality experience to drivers and riders. This includes investments in mapping, routing, payments, in-app navigation, matching technologies, and data science.

7. Mergers and Acquisitions: Lyft selectively considered acquisitions that contribute to the growth of its current business, help it expand into adjacent markets, or add new capabilities to its network. In the past, Lyft acquired Bikeshare Holdings LLC and Flexdrive, LLC.

8. Intellectual Property: Lyft invested in a patent program to identify and protect its strategic intellectual property in ridesharing, autonomous vehicle-related technology, telecommunications, networking, and other technologies relevant to its business. As of December 31, 2021, Lyft held 343 issued U.S. patents and had 310 U.S. patent applications pending.

9. Trademarks and Service Marks: Lyft had an ongoing trademark and service mark registration program to register its brand names, product names, taglines,

```

###  `FunctionCallingAgent` with RAG QueryEngineTools.¶
Here we use `Fuction Calling` capabilities of the model.
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import FunctionCallingAgent

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

agent = FunctionCallingAgent.from_tools(
    query_engine_tools,
    llm=llm,
    verbose=True,
    allow_parallel_tool_calls=False,
)

```

from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.agent import FunctionCallingAgent query_engine_tools = [ QueryEngineTool( query_engine=lyft_query_engine, metadata=ToolMetadata( name="lyft_10k", description="Provides information about Lyft financials for year 2021", ), ), QueryEngineTool( query_engine=uber_query_engine, metadata=ToolMetadata( name="uber_10k", description="Provides information about Uber financials for year 2021", ), ), ] agent = FunctionCallingAgent.from_tools( query_engine_tools, llm=llm, verbose=True, allow_parallel_tool_calls=False, )
In [ ]:
Copied!
```
response = agent.chat("What is the revenue of uber in 2021.")

```

response = agent.chat("What is the revenue of uber in 2021.")
```
Added user message to memory: What is the revenue of uber in 2021.
=== Calling Function ===
Calling function: uber_10k with args: {"input": "revenue"}
=== Function Output ===
Uber's revenue is primarily derived from fees paid by Mobility Drivers for using their platforms and related services to facilitate and complete Mobility services. Additionally, revenue is generated from fees paid by end-users for connection services obtained via the platform in certain markets. Uber's revenue also includes immaterial revenue streams such as financial partnerships products and Vehicle Solutions.

Uber's Delivery revenue is derived from Merchants' and Couriers' use of the Delivery platform and related services to facilitate and complete Delivery transactions. In certain markets where Uber is responsible for delivery services, delivery fees charged to end-users are also included in revenue. Advertising revenue from sponsored listing fees paid by merchants and brands in exchange for advertising services is also included in Delivery revenue.

Freight revenue consists of revenue from freight transportation services provided to shippers. After the acquisition of Transplace in the fourth quarter of 2021, Freight revenue also includes revenue from transportation management.

All Other revenue primarily includes collaboration revenue related to Uber's Advanced Technologies Group (ATG) business and revenue from New Mobility offerings and products. ATG collaboration revenue was related to a three-year joint collaboration agreement entered into in 2019. New Mobility offerings and products provided users access to rides through a variety of modes, including dockless e-bikes and e-scooters, platform incubator group offerings, and other immaterial revenue streams.

Uber's revenue is presented in the following tables for the years ended December 31, 2019, 2020, and 2021, respectively (in millions):

| Year Ended December 31, | 2019 | 2020 | 2021 |
| --- | --- | --- | --- |
| Mobility revenue | $10,707 | $6,089 | $6,953 |
| Delivery revenue | 1,401 | 3,904 | 8,362 |
| Freight revenue | 731 | 1,011 | 2,132 |
| All Other revenue | 161 | 135 | 8 |
| Total revenue
=== LLM Response ===
Uber's revenue for the year 2021 is presented in the following table:

| Year Ended December 31, | 2019 | 2020 | 2021 |
|---|---|---|---|
| Mobility revenue | $10,707 | $6,089 | $6,953 |
| Delivery revenue | 1,401 | 3,904 | 8,362 |
| Freight revenue | 731 | 1,011 | 2,132 |
| All Other revenue | 161 | 135 | 8 |
| Total revenue | $13,000 | $11,139 | $17,455 |

Uber's total revenue for the year 2021 was $17,455 million.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
assistant: Uber's revenue for the year 2021 is presented in the following table:

| Year Ended December 31, | 2019 | 2020 | 2021 |
|---|---|---|---|
| Mobility revenue | $10,707 | $6,089 | $6,953 |
| Delivery revenue | 1,401 | 3,904 | 8,362 |
| Freight revenue | 731 | 1,011 | 2,132 |
| All Other revenue | 161 | 135 | 8 |
| Total revenue | $13,000 | $11,139 | $17,455 |

Uber's total revenue for the year 2021 was $17,455 million.

```

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
The company's investments include cash and cash equivalents, short-term investments, and restricted investments. Cash equivalents consist of certificates of deposits, commercial paper, and corporate bonds with an original maturity of 90 days or less. Short-term investments are comprised of commercial paper, certificates of deposit, and corporate bonds that mature in twelve months or less. Restricted investments are held in trust accounts at third-party financial institutions and include debt security investments in commercial paper, certificates of deposit, corporate bonds, and U.S. government securities. The company also has investments in non-marketable equity securities, which are measured at cost with remeasurements to fair value only upon the occurrence of observable transactions for identical or similar investments of the same issuer or impairment.
=== LLM Response ===
Lyft's investments in 2021 include cash and cash equivalents, short-term investments, and restricted investments. Cash equivalents consist of certificates of deposits, commercial paper, and corporate bonds with an original maturity of 90 days or less. Short-term investments are comprised of commercial paper, certificates of deposit, and corporate bonds that mature in twelve months or less. Restricted investments are held in trust accounts at third-party financial institutions and include debt security investments in commercial paper, certificates of deposit, corporate bonds, and U.S. government securities. The company also has investments in non-marketable equity securities, which are measured at cost with remeasurements to fair value only upon the occurrence of observable transactions for identical or similar investments of the same issuer or impairment.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
assistant: Lyft's investments in 2021 include cash and cash equivalents, short-term investments, and restricted investments. Cash equivalents consist of certificates of deposits, commercial paper, and corporate bonds with an original maturity of 90 days or less. Short-term investments are comprised of commercial paper, certificates of deposit, and corporate bonds that mature in twelve months or less. Restricted investments are held in trust accounts at third-party financial institutions and include debt security investments in commercial paper, certificates of deposit, corporate bonds, and U.S. government securities. The company also has investments in non-marketable equity securities, which are measured at cost with remeasurements to fair value only upon the occurrence of observable transactions for identical or similar investments of the same issuer or impairment.

```

### Agents and Tools usage¶
In [ ]:
Copied!
```
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import (
    FunctionCallingAgent,
    ReActAgent,
)

```

from llama_index.core.tools import FunctionTool from llama_index.core.agent import ( FunctionCallingAgent, ReActAgent, )
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
### With Function Calling.¶
In [ ]:
Copied!
```
agent = FunctionCallingAgent.from_tools(
    [multiply_tool, add_tool, subtract_tool],
    llm=llm,
    verbose=True,
    allow_parallel_tool_calls=False,
)

```

agent = FunctionCallingAgent.from_tools( [multiply_tool, add_tool, subtract_tool], llm=llm, verbose=True, allow_parallel_tool_calls=False, )
In [ ]:
Copied!
```
response = agent.chat("What is (26 * 2) + 2024?")
print(response)

```

response = agent.chat("What is (26 * 2) + 2024?") print(response)
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
assistant: The result of (26 * 2) + 2024 is 2076.

```

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
print(response)

```

response = agent.chat("What is (26 * 2) + 2024?") print(response)
```
Thought: I need to use a tool to help me answer the question.
Action: multiply
Action Input: {"a": 26, "b": 2}

Observation: 52

Thought: I need to use another tool to continue answering the question.
Action: add
Action Input: {"a": 52, "b": 2024}

Observation: 2076

Thought: I can answer without using any more tools. I'll use the user's language to answer
Answer: (26 * 2) + 2024 equals 2076.
(26 * 2) + 2024 equals 2076.

```

