![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Sub Question Query Engine¶
In this tutorial, we showcase how to use a **sub question query engine** to tackle the problem of answering a complex query using multiple data sources.  
It first breaks down the complex query into sub questions for each relevant data source, then gather all the intermediate reponses and synthesizes a final response.
### Preparation¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

import nest_asyncio

nest_asyncio.apply()

```

import os os.environ["OPENAI_API_KEY"] = "sk-..." import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler
from llama_index.core import Settings

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.query_engine import SubQuestionQueryEngine from llama_index.core.callbacks import CallbackManager, LlamaDebugHandler from llama_index.core import Settings
In [ ]:
Copied!
```
# Using the LlamaDebugHandler to print the trace of the sub questions
# captured by the SUB_QUESTION callback event type
llama_debug = LlamaDebugHandler(print_trace_on_end=True)
callback_manager = CallbackManager([llama_debug])

Settings.callback_manager = callback_manager

```

# Using the LlamaDebugHandler to print the trace of the sub questions # captured by the SUB_QUESTION callback event type llama_debug = LlamaDebugHandler(print_trace_on_end=True) callback_manager = CallbackManager([llama_debug]) Settings.callback_manager = callback_manager
### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
Will not apply HSTS. The HSTS database must be a regular and non-world-writable file.
ERROR: could not open HSTS store at '/home/loganm/.wget-hsts'. HSTS will be disabled.
--2024-01-28 11:27:04--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.111.133, 185.199.108.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.111.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.04s   

2024-01-28 11:27:05 (1.73 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

In [ ]:
Copied!
```
# load data
pg_essay = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data()

# build index and query engine
vector_query_engine = VectorStoreIndex.from_documents(
    pg_essay,
    use_async=True,
).as_query_engine()

```

# load data pg_essay = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data() # build index and query engine vector_query_engine = VectorStoreIndex.from_documents( pg_essay, use_async=True, ).as_query_engine()
```
**********
Trace: index_construction
    |_CBEventType.NODE_PARSING ->  0.112481 seconds
      |_CBEventType.CHUNKING ->  0.105627 seconds
    |_CBEventType.EMBEDDING ->  0.959998 seconds
**********

```

### Setup sub question query engine¶
In [ ]:
Copied!
```
# setup base query engine as tool
query_engine_tools = [
    QueryEngineTool(
        query_engine=vector_query_engine,
        metadata=ToolMetadata(
            name="pg_essay",
            description="Paul Graham essay on What I Worked On",
        ),
    ),
]

query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
    use_async=True,
)

```

# setup base query engine as tool query_engine_tools = [ QueryEngineTool( query_engine=vector_query_engine, metadata=ToolMetadata( name="pg_essay", description="Paul Graham essay on What I Worked On", ), ), ] query_engine = SubQuestionQueryEngine.from_defaults( query_engine_tools=query_engine_tools, use_async=True, )
### Run queries¶
In [ ]:
Copied!
```
response = query_engine.query(
    "How was Paul Grahams life different before, during, and after YC?"
)

```

response = query_engine.query( "How was Paul Grahams life different before, during, and after YC?" )
```
Generated 3 sub questions.
[pg_essay] Q: What did Paul Graham work on before YC?
[pg_essay] Q: What did Paul Graham work on during YC?
[pg_essay] Q: What did Paul Graham work on after YC?
[pg_essay] A: After YC, Paul Graham worked on starting his own investment firm with Jessica.
[pg_essay] A: During his time at YC, Paul Graham worked on various projects. He wrote all of YC's internal software in Arc and also worked on Hacker News (HN), which was a news aggregator initially meant for startup founders but later changed to engage intellectual curiosity. Additionally, he wrote essays and worked on helping the startups in the YC program with their problems.
[pg_essay] A: Paul Graham worked on writing essays and working on YC before YC.
**********
Trace: query
    |_CBEventType.QUERY ->  66.492657 seconds
      |_CBEventType.LLM ->  2.226621 seconds
      |_CBEventType.SUB_QUESTION ->  62.387177 seconds
        |_CBEventType.QUERY ->  62.386864 seconds
          |_CBEventType.RETRIEVE ->  0.271039 seconds
            |_CBEventType.EMBEDDING ->  0.269134 seconds
          |_CBEventType.SYNTHESIZE ->  62.115674 seconds
            |_CBEventType.TEMPLATING ->  2.8e-05 seconds
            |_CBEventType.LLM ->  62.108522 seconds
      |_CBEventType.SUB_QUESTION ->  2.421552 seconds
        |_CBEventType.QUERY ->  2.421303 seconds
          |_CBEventType.RETRIEVE ->  0.227773 seconds
            |_CBEventType.EMBEDDING ->  0.224198 seconds
          |_CBEventType.SYNTHESIZE ->  2.193355 seconds
            |_CBEventType.TEMPLATING ->  4.2e-05 seconds
            |_CBEventType.LLM ->  2.183101 seconds
      |_CBEventType.SUB_QUESTION ->  1.530997 seconds
        |_CBEventType.QUERY ->  1.530781 seconds
          |_CBEventType.RETRIEVE ->  0.25523 seconds
            |_CBEventType.EMBEDDING ->  0.252898 seconds
          |_CBEventType.SYNTHESIZE ->  1.275401 seconds
            |_CBEventType.TEMPLATING ->  3.2e-05 seconds
            |_CBEventType.LLM ->  1.26685 seconds
      |_CBEventType.SYNTHESIZE ->  1.877223 seconds
        |_CBEventType.TEMPLATING ->  1.6e-05 seconds
        |_CBEventType.LLM ->  1.875031 seconds
**********

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Paul Graham's life was different before, during, and after YC. Before YC, he focused on writing essays and working on YC. During his time at YC, he worked on various projects, including writing software, developing Hacker News, and providing support to startups in the YC program. After YC, he started his own investment firm with Jessica. These different phases in his life involved different areas of focus and responsibilities.

```

In [ ]:
Copied!
```
# iterate through sub_question items captured in SUB_QUESTION event
from llama_index.core.callbacks import CBEventType, EventPayload

for i, (start_event, end_event) in enumerate(
    llama_debug.get_event_pairs(CBEventType.SUB_QUESTION)
):
    qa_pair = end_event.payload[EventPayload.SUB_QUESTION]
    print("Sub Question " + str(i) + ": " + qa_pair.sub_q.sub_question.strip())
    print("Answer: " + qa_pair.answer.strip())
    print("====================================")

```

# iterate through sub_question items captured in SUB_QUESTION event from llama_index.core.callbacks import CBEventType, EventPayload for i, (start_event, end_event) in enumerate( llama_debug.get_event_pairs(CBEventType.SUB_QUESTION) ): qa_pair = end_event.payload[EventPayload.SUB_QUESTION] print("Sub Question " + str(i) + ": " + qa_pair.sub_q.sub_question.strip()) print("Answer: " + qa_pair.answer.strip()) print("====================================")
```
Sub Question 0: What did Paul Graham work on before YC?
Answer: Paul Graham worked on writing essays and working on YC before YC.
====================================
Sub Question 1: What did Paul Graham work on during YC?
Answer: During his time at YC, Paul Graham worked on various projects. He wrote all of YC's internal software in Arc and also worked on Hacker News (HN), which was a news aggregator initially meant for startup founders but later changed to engage intellectual curiosity. Additionally, he wrote essays and worked on helping the startups in the YC program with their problems.
====================================
Sub Question 2: What did Paul Graham work on after YC?
Answer: After YC, Paul Graham worked on starting his own investment firm with Jessica.
====================================

```

