![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# How to Build a Chatbot¶
LlamaIndex serves as a bridge between your data and Language Learning Models (LLMs), providing a toolkit that enables you to establish a query interface around your data for a variety of tasks, such as question-answering and summarization.
In this tutorial, we'll walk you through building a context-augmented chatbot using a Data Agent. This agent, powered by LLMs, is capable of intelligently executing tasks over your data. The end result is a chatbot agent equipped with a robust set of data interface tools provided by LlamaIndex to answer queries about your data.
**Note** : This tutorial builds upon initial work on creating a query interface over SEC 10-K filings - check it out here.
### Context¶
In this guide, we’ll build a "10-K Chatbot" that uses raw UBER 10-K HTML filings from Dropbox. Users can interact with the chatbot to ask questions related to the 10-K filings.
### Preparation¶
In [ ]:
Copied!
```
%pip install llama-index-readers-file
%pip install llama-index-embeddings-openai
%pip install llama-index-agent-openai
%pip install llama-index-llms-openai
%pip install llama-index-question-gen-openai
%pip install unstructured

```

%pip install llama-index-readers-file %pip install llama-index-embeddings-openai %pip install llama-index-agent-openai %pip install llama-index-llms-openai %pip install llama-index-question-gen-openai %pip install unstructured
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
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# global defaults
Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-large")
Settings.chunk_size = 512
Settings.chunk_overlap = 64

```

from llama_index.core import Settings from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding # global defaults Settings.llm = OpenAI(model="gpt-4o-mini") Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-large") Settings.chunk_size = 512 Settings.chunk_overlap = 64
### Ingest Data¶
Let's first download the raw 10-k files, from 2019-2022.
In [ ]:
Copied!
```
# NOTE: the code examples assume you're operating within a Jupyter notebook.
# download files
!mkdir data
!wget "https://www.dropbox.com/s/948jr9cfs7fgj99/UBER.zip?dl=1" -O data/UBER.zip
!unzip data/UBER.zip -d data

```

# NOTE: the code examples assume you're operating within a Jupyter notebook. # download files !mkdir data !wget "https://www.dropbox.com/s/948jr9cfs7fgj99/UBER.zip?dl=1" -O data/UBER.zip !unzip data/UBER.zip -d data
To parse the HTML files into formatted text, we use the Unstructured library. Thanks to LlamaHub, we can directly integrate with Unstructured, allowing conversion of any text into a Document format that LlamaIndex can ingest.
First we install the necessary packages:
Then we can use the `UnstructuredReader` to parse the HTML files into a list of `Document` objects.
In [ ]:
Copied!
```
from llama_index.readers.file import UnstructuredReader
from pathlib import Path

years = [2022, 2021, 2020, 2019]

```

from llama_index.readers.file import UnstructuredReader from pathlib import Path years = [2022, 2021, 2020, 2019]
In [ ]:
Copied!
```
loader = UnstructuredReader()
doc_set = {}
all_docs = []
for year in years:
    year_docs = loader.load_data(
        file=Path(f"./data/UBER/UBER_{year}.html"), split_documents=False
    )
    # insert year metadata into each year
    for d in year_docs:
        d.metadata = {"year": year}
    doc_set[year] = year_docs
    all_docs.extend(year_docs)

```

loader = UnstructuredReader() doc_set = {} all_docs = [] for year in years: year_docs = loader.load_data( file=Path(f"./data/UBER/UBER_{year}.html"), split_documents=False ) # insert year metadata into each year for d in year_docs: d.metadata = {"year": year} doc_set[year] = year_docs all_docs.extend(year_docs)
### Setting up Vector Indices for each year¶
We first setup a vector index for each year. Each vector index allows us to ask questions about the 10-K filing of a given year.
We build each index and save it to disk.
In [ ]:
Copied!
```
# initialize simple vector indices
# NOTE: don't run this cell if the indices are already loaded!
from llama_index.core import VectorStoreIndex, StorageContext


index_set = {}
for year in years:
    storage_context = StorageContext.from_defaults()
    cur_index = VectorStoreIndex.from_documents(
        doc_set[year],
        storage_context=storage_context,
    )
    index_set[year] = cur_index
    storage_context.persist(persist_dir=f"./storage/{year}")

```

# initialize simple vector indices # NOTE: don't run this cell if the indices are already loaded! from llama_index.core import VectorStoreIndex, StorageContext index_set = {} for year in years: storage_context = StorageContext.from_defaults() cur_index = VectorStoreIndex.from_documents( doc_set[year], storage_context=storage_context, ) index_set[year] = cur_index storage_context.persist(persist_dir=f"./storage/{year}")
To load an index from disk, do the following
In [ ]:
Copied!
```
# Load indices from disk
from llama_index.core import StorageContext, load_index_from_storage

index_set = {}
for year in years:
    storage_context = StorageContext.from_defaults(
        persist_dir=f"./storage/{year}"
    )
    cur_index = load_index_from_storage(
        storage_context,
    )
    index_set[year] = cur_index

```

# Load indices from disk from llama_index.core import StorageContext, load_index_from_storage index_set = {} for year in years: storage_context = StorageContext.from_defaults( persist_dir=f"./storage/{year}" ) cur_index = load_index_from_storage( storage_context, ) index_set[year] = cur_index
### Setting up a Sub Question Query Engine to Synthesize Answers Across 10-K Filings¶
Since we have access to documents of 4 years, we may not only want to ask questions regarding the 10-K document of a given year, but ask questions that require analysis over all 10-K filings.
To address this, we can use a Sub Question Query Engine. It decomposes a query into subqueries, each answered by an individual vector index, and synthesizes the results to answer the overall query.
LlamaIndex provides some wrappers around indices (and query engines) so that they can be used by query engines and agents. First we define a `QueryEngineTool` for each vector index. Each tool has a name and a description; these are what the LLM agent sees to decide which tool to choose.
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool

individual_query_engine_tools = [
    QueryEngineTool.from_defaults(
        query_engine=index_set[year].as_query_engine(),
        name=f"vector_index_{year}",
        description=(
            "useful for when you want to answer queries about the"
            f" {year} SEC 10-K for Uber"
        ),
    )
    for year in years
]

```

from llama_index.core.tools import QueryEngineTool individual_query_engine_tools = [ QueryEngineTool.from_defaults( query_engine=index_set[year].as_query_engine(), name=f"vector_index_{year}", description=( "useful for when you want to answer queries about the" f" {year} SEC 10-K for Uber" ), ) for year in years ]
Now we can create the Sub Question Query Engine, which will allow us to synthesize answers across the 10-K filings. We pass in the `individual_query_engine_tools` we defined above.
In [ ]:
Copied!
```
from llama_index.core.query_engine import SubQuestionQueryEngine

query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=individual_query_engine_tools,
)

```

from llama_index.core.query_engine import SubQuestionQueryEngine query_engine = SubQuestionQueryEngine.from_defaults( query_engine_tools=individual_query_engine_tools, )
### Setting up the Chatbot Agent¶
We use a LlamaIndex Data Agent to setup the outer chatbot agent, which has access to a set of Tools. Specifically, we will use an OpenAIAgent, that takes advantage of OpenAI API function calling. We want to use the separate Tools we defined previously for each index (corresponding to a given year), as well as a tool for the sub question query engine we defined above.
First we define a `QueryEngineTool` for the sub question query engine:
In [ ]:
Copied!
```
query_engine_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="sub_question_query_engine",
    description=(
        "useful for when you want to answer queries that require analyzing"
        " multiple SEC 10-K documents for Uber"
    ),
)

```

query_engine_tool = QueryEngineTool.from_defaults( query_engine=query_engine, name="sub_question_query_engine", description=( "useful for when you want to answer queries that require analyzing" " multiple SEC 10-K documents for Uber" ), )
Then, we combine the Tools we defined above into a single list of tools for the agent:
In [ ]:
Copied!
```
tools = individual_query_engine_tools + [query_engine_tool]

```

tools = individual_query_engine_tools + [query_engine_tool]
Finally, we call `FunctionAgent` to create the agent, passing in the list of tools we defined above.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

agent = FunctionAgent(tools=tools, llm=OpenAI(model="gpt-4o"))

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.llms.openai import OpenAI agent = FunctionAgent(tools=tools, llm=OpenAI(model="gpt-4o"))
### Testing the Agent¶
We can now test the agent with various queries.
If we test it with a simple "hello" query, the agent does not use any Tools.
In [ ]:
Copied!
```
from llama_index.core.workflow import Context

# Setup the context for this specific interaction
ctx = Context(agent)

response = await agent.run("hi, i am bob", ctx=ctx)
print(str(response))

```

from llama_index.core.workflow import Context # Setup the context for this specific interaction ctx = Context(agent) response = await agent.run("hi, i am bob", ctx=ctx) print(str(response))
```
Hello Bob! How can I assist you today?

```

If we test it with a query regarding the 10-k of a given year, the agent will use the relevant vector index Tool.
In [ ]:
Copied!
```
response = await agent.run(
    "What were some of the biggest risk factors in 2020 for Uber?", ctx=ctx
)
print(str(response))

```

response = await agent.run( "What were some of the biggest risk factors in 2020 for Uber?", ctx=ctx ) print(str(response))
```
In 2020, some of the biggest risk factors for Uber included:

1. **Legal and Regulatory Risks**: Extensive government regulation and oversight could adversely impact operations and future prospects.
2. **Data Privacy and Security Risks**: Risks related to data collection, use, and processing could lead to investigations, litigation, and negative publicity.
3. **Economic Impact of COVID-19**: The pandemic adversely affected business operations, demand for services, and financial condition due to governmental restrictions and changes in consumer behavior.
4. **Market Volatility**: Volatility in the market price of common stock could affect investors' ability to resell shares at favorable prices.
5. **Safety Incidents**: Criminal or dangerous activities on the platform could harm the ability to attract and retain drivers and consumers.
6. **Investment Risks**: Substantial investments in new technologies and offerings carry inherent risks, with no guarantee of realizing expected benefits.
7. **Dependence on Metropolitan Areas**: A significant portion of gross bookings comes from large metropolitan areas, which may be negatively impacted by various external factors.
8. **Talent Retention**: Attracting and retaining high-quality personnel is crucial, and issues with attrition or succession planning could adversely affect the business.
9. **Cybersecurity Threats**: Cyberattacks and data breaches could harm reputation and operational results.
10. **Capital Requirements**: The need for additional capital to support growth may not be met on reasonable terms, impacting business expansion.
11. **Acquisition Challenges**: Difficulty in identifying and integrating suitable businesses could harm operating results and future prospects.
12. **Operational Limitations**: Potential restrictions in certain jurisdictions may require modifications to the business model, affecting service delivery.

```

Finally, if we test it with a query to compare/contrast risk factors across years, the agent will use the Sub Question Query Engine Tool.
In [ ]:
Copied!
```
cross_query_str = (
    "Compare/contrast the risk factors described in the Uber 10-K across"
    " years. Give answer in bullet points."
)

response = await agent.run(cross_query_str, ctx=ctx)
print(str(response))

```

cross_query_str = ( "Compare/contrast the risk factors described in the Uber 10-K across" " years. Give answer in bullet points." ) response = await agent.run(cross_query_str, ctx=ctx) print(str(response))
```
Here's a comparison of the risk factors for Uber across the years 2020, 2021, and 2022:

- **COVID-19 Impact**:
  - **2020**: The pandemic significantly affected business operations, demand, and financial condition.
  - **2021**: Continued impact of the pandemic was a concern, affecting various parts of the business.
  - **2022**: The pandemic's impact was less emphasized, with more focus on operational and competitive risks.

- **Driver Classification**:
  - **2020**: Not specifically highlighted.
  - **2021**: Potential reclassification of Drivers as employees could alter the business model.
  - **2022**: Continued risk of reclassification impacting operational costs.

- **Competition**:
  - **2020**: Not specifically highlighted.
  - **2021**: Intense competition with low barriers to entry and well-capitalized competitors.
  - **2022**: Competitive landscape challenges due to established alternatives and low barriers to entry.

- **Financial Concerns**:
  - **2020**: Market volatility and capital requirements were major concerns.
  - **2021**: Historical losses and increased operating expenses raised profitability concerns.
  - **2022**: Significant losses and rising expenses continued to raise profitability concerns.

- **User and Personnel Retention**:
  - **2020**: Talent retention was crucial, with risks from attrition.
  - **2021**: Attracting and retaining a critical mass of users and personnel was essential.
  - **2022**: Continued emphasis on retaining Drivers, consumers, and high-quality personnel.

- **Brand and Reputation**:
  - **2020**: Safety incidents and cybersecurity threats could harm reputation.
  - **2021**: Maintaining and enhancing brand reputation was critical, with past negative publicity being a concern.
  - **2022**: Brand and reputation were under scrutiny, with negative media coverage potentially harming prospects.

- **Operational Challenges**:
  - **2020**: Operational limitations and acquisition challenges were highlighted.
  - **2021**: Challenges in managing growth and optimizing organizational structure.
  - **2022**: Historical workplace culture and the need for organizational optimization were critical.

- **Safety and Liability**:
  - **2020**: Safety incidents and liability claims were significant risks.
  - **2021**: Safety incidents and liability claims, especially with vulnerable road users, were concerns.
  - **2022**: Safety incidents and public reporting could impact reputation and financial results.

Overall, while some risk factors remained consistent across the years, such as competition, financial concerns, and safety, the emphasis shifted slightly with the evolving business environment and external factors like the pandemic.

```

### Setting up the Chatbot Loop¶
Now that we have the chatbot setup, it only takes a few more steps to setup a basic interactive loop to chat with our SEC-augmented chatbot!
In [ ]:
Copied!
```
agent = FunctionAgent(tools=tools, llm=OpenAI(model="gpt-4o"))
ctx = Context(agent)

while True:
    text_input = input("User: ")
    if text_input == "exit":
        break
    response = await agent.run(text_input, ctx=ctx)
    print(f"Agent: {response}")

# User: What were some of the legal proceedings against Uber in 2022?

```

agent = FunctionAgent(tools=tools, llm=OpenAI(model="gpt-4o")) ctx = Context(agent) while True: text_input = input("User: ") if text_input == "exit": break response = await agent.run(text_input, ctx=ctx) print(f"Agent: {response}") # User: What were some of the legal proceedings against Uber in 2022?
