# Router QueryEngine and SubQuestion QueryEngine¶
In this notebook we will demonstrate:
  1. **RouterQueryEngine** - Handle user queries to choose from predefined indices.
  2. **SubQuestionQueryEngine** - breaks down the complex query into sub-questions for each relevant data source, then gathers all the intermediate responses and synthesizes a final response.


RouterQueryEngine Documentation
SubQuestionQueryEngine Documentation
## Router QueryEngine¶
Routers act as specialized modules that handle user queries and choose from a set of predefined options, each defined by specific metadata.
There are two main types of core router modules:
  1. **LLM Selectors** : These modules present the available options as a text prompt and use the LLM text completion endpoint to make decisions.
  2. **Pydantic Selectors** : These modules format the options as Pydantic schemas and pass them to a function-calling endpoint, returning the results as Pydantic objects.


### Installation¶
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# NOTE: This is ONLY necessary in jupyter notebook.
# Details: Jupyter runs an event-loop behind the scenes.
#          This results in nested event-loops when we start an event-loop to make async queries.
#          This is normally not allowed, we use nest_asyncio to allow it for convenience.
import nest_asyncio

nest_asyncio.apply()

```

# NOTE: This is ONLY necessary in jupyter notebook. # Details: Jupyter runs an event-loop behind the scenes. # This results in nested event-loops when we start an event-loop to make async queries. # This is normally not allowed, we use nest_asyncio to allow it for convenience. import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
import logging
import sys

# Set up the root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Set logger level to INFO

# Clear out any existing handlers
logger.handlers = []

# Set up the StreamHandler to output to sys.stdout (Colab's output)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)  # Set handler level to INFO

# Add the handler to the logger
logger.addHandler(handler)

from llama_index.core import (
    VectorStoreIndex,
    SummaryIndex,
    SimpleDirectoryReader,
    ServiceContext,
    StorageContext,
)

import openai
import os
from IPython.display import display, HTML


# Setup openai api key
os.environ["OPENAI_API_KEY"] = "sk-..."

```

import logging import sys # Set up the root logger logger = logging.getLogger() logger.setLevel(logging.INFO) # Set logger level to INFO # Clear out any existing handlers logger.handlers = [] # Set up the StreamHandler to output to sys.stdout (Colab's output) handler = logging.StreamHandler(sys.stdout) handler.setLevel(logging.INFO) # Set handler level to INFO # Add the handler to the logger logger.addHandler(handler) from llama_index.core import ( VectorStoreIndex, SummaryIndex, SimpleDirectoryReader, ServiceContext, StorageContext, ) import openai import os from IPython.display import display, HTML # Setup openai api key os.environ["OPENAI_API_KEY"] = "sk-..."
```
NumExpr defaulting to 2 threads.

```

### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-05-16 05:27:42--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.110.133, 185.199.111.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’


          data/paul   0%[                    ]       0  --.-KB/s               
data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.002s  

2024-05-16 05:27:42 (46.3 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

### Load Data¶
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("data/paul_graham").load_data()

```

# load documents documents = SimpleDirectoryReader("data/paul_graham").load_data()
### Create Nodes¶
In [ ]:
Copied!
```
from llama_index.core.text_splitter import SentenceSplitter

# create parser and parse document into nodes
parser = SentenceSplitter(chunk_size=1024, chunk_overlap=100)
nodes = parser(documents)

```

from llama_index.core.text_splitter import SentenceSplitter # create parser and parse document into nodes parser = SentenceSplitter(chunk_size=1024, chunk_overlap=100) nodes = parser(documents)
### Create VectorStoreIndex and SummaryIndex.¶
In [ ]:
Copied!
```
# Summary Index for summarization questions
summary_index = SummaryIndex(nodes)

# Vector Index for answering specific context questions
vector_index = VectorStoreIndex(nodes)

```

# Summary Index for summarization questions summary_index = SummaryIndex(nodes) # Vector Index for answering specific context questions vector_index = VectorStoreIndex(nodes)
```
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

### Define Query Engines.¶
  1. Summary Index Query Engine.
  2. Vector Index Query Engine.


In [ ]:
Copied!
```
# Summary Index Query Engine
summary_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True,
)

# Vector Index Query Engine
vector_query_engine = vector_index.as_query_engine()

```

# Summary Index Query Engine summary_query_engine = summary_index.as_query_engine( response_mode="tree_summarize", use_async=True, ) # Vector Index Query Engine vector_query_engine = vector_index.as_query_engine()
### Build summary index and vector index tools¶
In [ ]:
Copied!
```
from llama_index.core.tools.query_engine import QueryEngineTool, ToolMetadata

# Summary Index tool
summary_tool = QueryEngineTool.from_defaults(
    query_engine=summary_query_engine,
    description="Useful for summarization questions related to Paul Graham eassy on What I Worked On.",
)

# Vector Index tool
vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description="Useful for retrieving specific context from Paul Graham essay on What I Worked On.",
)

```

from llama_index.core.tools.query_engine import QueryEngineTool, ToolMetadata # Summary Index tool summary_tool = QueryEngineTool.from_defaults( query_engine=summary_query_engine, description="Useful for summarization questions related to Paul Graham eassy on What I Worked On.", ) # Vector Index tool vector_tool = QueryEngineTool.from_defaults( query_engine=vector_query_engine, description="Useful for retrieving specific context from Paul Graham essay on What I Worked On.", )
### Define Router Query Engine¶
Various selectors are at your disposal, each offering unique characteristics.
Pydantic selectors, supported exclusively by gpt-4 and the default gpt-3.5-turbo, utilize the OpenAI Function Call API. Instead of interpreting raw JSON, they yield pydantic selection objects.
On the other hand, LLM selectors employ the LLM to generate a JSON output, which is then parsed to query the relevant indexes.
For both selector types, you can opt to route to either a single index or multiple indexes.
### PydanticSingleSelector¶
Use the OpenAI Function API to generate/parse pydantic objects under the hood for the router selector.
In [ ]:
Copied!
```
from llama_index.core.query_engine.router_query_engine import RouterQueryEngine
from llama_index.core.selectors.llm_selectors import (
    LLMSingleSelector,
    LLMMultiSelector,
)
from llama_index.core.selectors.pydantic_selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)

# Create Router Query Engine
query_engine = RouterQueryEngine(
    selector=PydanticSingleSelector.from_defaults(),
    query_engine_tools=[
        summary_tool,
        vector_tool,
    ],
)

```

from llama_index.core.query_engine.router_query_engine import RouterQueryEngine from llama_index.core.selectors.llm_selectors import ( LLMSingleSelector, LLMMultiSelector, ) from llama_index.core.selectors.pydantic_selectors import ( PydanticMultiSelector, PydanticSingleSelector, ) # Create Router Query Engine query_engine = RouterQueryEngine( selector=PydanticSingleSelector.from_defaults(), query_engine_tools=[ summary_tool, vector_tool, ], )
In [ ]:
Copied!
```
response = query_engine.query("What is the summary of the document?")

```

response = query_engine.query("What is the summary of the document?")
```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Selecting query engine 0: The choice is specifically related to summarization questions about Paul Graham's essay on What I Worked On..
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
The document chronicles Paul Graham's journey through various endeavors, including his experiences with writing, programming, and founding software companies like Viaweb and Y Combinator. It discusses his exploration of painting, personal challenges such as his mother's illness, and his decision to step back from Y Combinator to focus on painting before returning to Lisp programming with the development of a new dialect called Bel. The narrative also covers Graham's reflections on his work choices, the transition of Y Combinator's leadership to Sam Altman, and his contemplation on future projects and the impact of customs in evolving fields.
### LLMSingleSelector¶
Utilize OpenAI (or another LLM) to internally interpret the generated JSON and determine a sub-index for routing.
In [ ]:
Copied!
```
# Create Router Query Engine
query_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[
        summary_tool,
        vector_tool,
    ],
)

```

# Create Router Query Engine query_engine = RouterQueryEngine( selector=LLMSingleSelector.from_defaults(), query_engine_tools=[ summary_tool, vector_tool, ], )
In [ ]:
Copied!
```
response = query_engine.query("What is the summary of the document?")

```

response = query_engine.query("What is the summary of the document?")
```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Selecting query engine 0: This choice indicates that the summary is related to summarization questions specifically about Paul Graham's essay on What I Worked On..
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
The document chronicles Paul Graham's journey through various projects and endeavors, from his early experiences with writing and programming to his involvement in building software companies like Viaweb and Y Combinator. It details his exploration of different projects, challenges faced, decisions made, and eventual transition to focusing on painting and writing essays. The narrative also discusses his experimentation with the Lisp programming language and the development of a new Lisp dialect called Bel. The document concludes with Graham reflecting on his past projects and contemplating his future endeavors, emphasizing the importance of pursuing projects aligned with personal goals and interests.
In [ ]:
Copied!
```
response = query_engine.query("What did Paul Graham do after RICS?")

```

response = query_engine.query("What did Paul Graham do after RICS?")
```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Selecting query engine 1: This choice is more relevant as it focuses on retrieving specific context from Paul Graham's essay on What I Worked On, which would likely provide information on what he did after RICS..
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
Paul Graham started painting after RICS.
### PydanticMultiSelector¶
If you anticipate queries being directed to multiple indexes, it's advisable to use a multi-selector. This selector dispatches the query to various sub-indexes and subsequently aggregates the responses through a summary index to deliver a comprehensive answer.
### Let's create a simplekeywordtable index and corresponding tool.¶
In [ ]:
Copied!
```
from llama_index.core import SimpleKeywordTableIndex

keyword_index = SimpleKeywordTableIndex(nodes)

keyword_query_engine = keyword_index.as_query_engine()

keyword_tool = QueryEngineTool.from_defaults(
    query_engine=keyword_query_engine,
    description="Useful for retrieving specific context using keywords from Paul Graham essay on What I Worked On.",
)

```

from llama_index.core import SimpleKeywordTableIndex keyword_index = SimpleKeywordTableIndex(nodes) keyword_query_engine = keyword_index.as_query_engine() keyword_tool = QueryEngineTool.from_defaults( query_engine=keyword_query_engine, description="Useful for retrieving specific context using keywords from Paul Graham essay on What I Worked On.", )
### Build a router query engine.¶
In [ ]:
Copied!
```
query_engine = RouterQueryEngine(
    selector=PydanticMultiSelector.from_defaults(),
    query_engine_tools=[vector_tool, keyword_tool, summary_tool],
)

```

query_engine = RouterQueryEngine( selector=PydanticMultiSelector.from_defaults(), query_engine_tools=[vector_tool, keyword_tool, summary_tool], )
In [ ]:
Copied!
```
# This query could use either a keyword or vector query engine, so it will combine responses from both
response = query_engine.query(
    "What were noteable events and people from the authors time at Interleaf and YC?"
)

```

# This query could use either a keyword or vector query engine, so it will combine responses from both response = query_engine.query( "What were noteable events and people from the authors time at Interleaf and YC?" )
```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Selecting query engine 0: Retrieving specific context from Paul Graham essay on What I Worked On can provide detailed information about noteable events and people from the author's time at Interleaf and YC..
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Selecting query engine 1: Retrieving specific context using keywords from Paul Graham essay on What I Worked On can help identify key events and people related to the author's time at Interleaf and YC..
> Starting query: What were noteable events and people from the authors time at Interleaf and YC?
query keywords: ['noteable', 'authors', 'time', 'interleaf', 'yc', 'events', 'people']
> Extracted keywords: ['time', 'interleaf', 'yc', 'people']
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Combining responses from multiple query engines.
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
Notable events from the author's time at Interleaf include working on software development, observing inefficiencies in managing versions and ports, and learning about the dynamics of technology companies. Notable people mentioned from this time include Robert and Trevor, with whom the author worked on developing software components like the editor, shopping cart, and manager. During the author's time at Y Combinator (YC), notable events include working on various projects such as Hacker News, transitioning leadership to Sam Altman, and shifting focus towards painting after leaving YC. Notable people mentioned from this time include Julian, who provided seed funding for Viaweb, and Robert Morris, who advised the author about not letting YC be the last significant endeavor.
## SubQuestion Query Engine¶
Here, we will demonstrate how to use a sub-question query engine to address the challenge of answering a complex query using multiple data sources.
The SubQuestion Query Engine first breaks down the complex query into sub-questions for each relevant data source, then gathers all the intermediate responses and synthesizes a final response.
### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
```
--2024-05-16 05:36:06--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.109.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1880483 (1.8M) [application/octet-stream]
Saving to: ‘data/10k/uber_2021.pdf’


data/10k/uber_2021.   0%[                    ]       0  --.-KB/s               
data/10k/uber_2021. 100%[===================>]   1.79M  --.-KB/s    in 0.01s   

2024-05-16 05:36:06 (184 MB/s) - ‘data/10k/uber_2021.pdf’ saved [1880483/1880483]

--2024-05-16 05:36:06--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.111.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1440303 (1.4M) [application/octet-stream]
Saving to: ‘data/10k/lyft_2021.pdf’

data/10k/lyft_2021. 100%[===================>]   1.37M  --.-KB/s    in 0.01s   

2024-05-16 05:36:06 (120 MB/s) - ‘data/10k/lyft_2021.pdf’ saved [1440303/1440303]


```

### Load Data¶
In [ ]:
Copied!
```
lyft_docs = SimpleDirectoryReader(
    input_files=["./data/10k/lyft_2021.pdf"]
).load_data()
uber_docs = SimpleDirectoryReader(
    input_files=["./data/10k/uber_2021.pdf"]
).load_data()

```

lyft_docs = SimpleDirectoryReader( input_files=["./data/10k/lyft_2021.pdf"] ).load_data() uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data()
In [ ]:
Copied!
```
print(f"Loaded lyft 10-K with {len(lyft_docs)} pages")
print(f"Loaded Uber 10-K with {len(uber_docs)} pages")

```

print(f"Loaded lyft 10-K with {len(lyft_docs)} pages") print(f"Loaded Uber 10-K with {len(uber_docs)} pages")
```
Loaded lyft 10-K with 238 pages
Loaded Uber 10-K with 307 pages

```

### Create Indices¶
In [ ]:
Copied!
```
lyft_index = VectorStoreIndex.from_documents(lyft_docs)
uber_index = VectorStoreIndex.from_documents(uber_docs)

```

lyft_index = VectorStoreIndex.from_documents(lyft_docs) uber_index = VectorStoreIndex.from_documents(uber_docs)
```
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

### Define Query Engines¶
In [ ]:
Copied!
```
lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)

```

lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
uber_engine = uber_index.as_query_engine(similarity_top_k=3)

```

uber_engine = uber_index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
response = await lyft_engine.aquery(
    "What is the revenue of Lyft in 2021? Answer in millions with page reference"
)

```

response = await lyft_engine.aquery( "What is the revenue of Lyft in 2021? Answer in millions with page reference" )
```
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
The revenue of Lyft in 2021 was $3.208 billion. (Page reference: 79)
In [ ]:
Copied!
```
response = await uber_engine.aquery(
    "What is the revenue of Uber in 2021? Answer in millions, with page reference"
)

```

response = await uber_engine.aquery( "What is the revenue of Uber in 2021? Answer in millions, with page reference" )
```
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
The revenue of Uber in 2021 was $17,455 million. (Reference: page 77)
### Define QueryEngine Tools¶
In [ ]:
Copied!
```
query_engine_tools = [
    QueryEngineTool(
        query_engine=lyft_engine,
        metadata=ToolMetadata(
            name="lyft_10k",
            description="Provides information about Lyft financials for year 2021",
        ),
    ),
    QueryEngineTool(
        query_engine=uber_engine,
        metadata=ToolMetadata(
            name="uber_10k",
            description="Provides information about Uber financials for year 2021",
        ),
    ),
]

```

query_engine_tools = [ QueryEngineTool( query_engine=lyft_engine, metadata=ToolMetadata( name="lyft_10k", description="Provides information about Lyft financials for year 2021", ), ), QueryEngineTool( query_engine=uber_engine, metadata=ToolMetadata( name="uber_10k", description="Provides information about Uber financials for year 2021", ), ), ]
### SubQuestion QueryEngine¶
In [ ]:
Copied!
```
from llama_index.core.query_engine.sub_question_query_engine import (
    SubQuestionQueryEngine,
)

sub_question_query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools
)

```

from llama_index.core.query_engine.sub_question_query_engine import ( SubQuestionQueryEngine, ) sub_question_query_engine = SubQuestionQueryEngine.from_defaults( query_engine_tools=query_engine_tools )
### Querying¶
In [ ]:
Copied!
```
response = await sub_question_query_engine.aquery(
    "Compare revenue growth of Uber and Lyft from 2020 to 2021"
)

```

response = await sub_question_query_engine.aquery( "Compare revenue growth of Uber and Lyft from 2020 to 2021" )
```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
Generated 4 sub questions.
[uber_10k] Q: What was the revenue of Uber in 2020?
[uber_10k] Q: What was the revenue of Uber in 2021?
[lyft_10k] Q: What was the revenue of Lyft in 2020?
[lyft_10k] Q: What was the revenue of Lyft in 2021?
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
[lyft_10k] A: $3,208,323
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
[lyft_10k] A: $2,364,681
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
[uber_10k] A: $11,139 million
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
[uber_10k] A: $17,455
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

display(HTML(f'
{response.response}
'))
Lyft's revenue grew by approximately 35.4% from 2020 to 2021, while Uber's revenue increased by around 56.8% during the same period.
