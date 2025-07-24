![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Chat Engine - OpenAI Agent Mode¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2023-11-20 14:52:58--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.108.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.02s   

2023-11-20 14:52:58 (2.86 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

### Get started in 5 lines of code¶
Load data and build index
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI

# Necessary to use the latest OpenAI models that support function calling API
llm = OpenAI(model="gpt-3.5-turbo-0613")
data = SimpleDirectoryReader(input_dir="../data/paul_graham/").load_data()
index = VectorStoreIndex.from_documents(data)

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.llms.openai import OpenAI # Necessary to use the latest OpenAI models that support function calling API llm = OpenAI(model="gpt-3.5-turbo-0613") data = SimpleDirectoryReader(input_dir="../data/paul_graham/").load_data() index = VectorStoreIndex.from_documents(data)
Configure chat engine
In [ ]:
Copied!
```
chat_engine = index.as_chat_engine(chat_mode="openai", llm=llm, verbose=True)

```

chat_engine = index.as_chat_engine(chat_mode="openai", llm=llm, verbose=True)
Chat with your data
In [ ]:
Copied!
```
response = chat_engine.chat("Hi")
print(response)

```

response = chat_engine.chat("Hi") print(response)
```
STARTING TURN 1
---------------

Hello! How can I assist you today?

```

In [ ]:
Copied!
```
response = chat_engine.chat(
    "Use the tool to answer: Who did Paul Graham hand over YC to?"
)
print(response)

```

response = chat_engine.chat( "Use the tool to answer: Who did Paul Graham hand over YC to?" ) print(response)
```
STARTING TURN 1
---------------

=== Calling Function ===
Calling function: query_engine_tool with args: {
  "input": "Who did Paul Graham hand over YC to?"
}
Got output: Paul Graham handed over YC to Sam Altman.
========================

STARTING TURN 2
---------------

Paul Graham handed over Y Combinator (YC) to Sam Altman.

```

In [ ]:
Copied!
```
response = chat_engine.stream_chat(
    "Use the tool to answer: Who did Paul Graham hand over YC to?"
)
print(response)

```

response = chat_engine.stream_chat( "Use the tool to answer: Who did Paul Graham hand over YC to?" ) print(response)
```
STARTING TURN 1
---------------

=== Calling Function ===
Calling function: query_engine_tool with args: {
  "input": "Who did Paul Graham hand over YC to?"
}
Got output: Paul Graham handed over YC to Sam Altman.
========================

STARTING TURN 2
---------------



```

### Force chat engine to query the index¶
NOTE: this is a feature unique to the "openai" chat mode (which uses the `OpenAIAgent` under the hood).
In [ ]:
Copied!
```
response = chat_engine.chat(
    "What did Paul Graham do growing up?", tool_choice="query_engine_tool"
)

```

response = chat_engine.chat( "What did Paul Graham do growing up?", tool_choice="query_engine_tool" )
```
STARTING TURN 1
---------------

=== Calling Function ===
Calling function: query_engine_tool with args: {
  "input": "What did Paul Graham do growing up?"
}
Got output: Growing up, Paul Graham worked on writing and programming. He wrote short stories and also tried his hand at programming on the IBM 1401 computer that his school district had. He later got a microcomputer, a TRS-80, and started programming more extensively, writing simple games and even a word processor.
========================

STARTING TURN 2
---------------


```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Growing up, Paul Graham worked on writing and programming. He wrote short stories and also tried his hand at programming on the IBM 1401 computer that his school district had. He later got a microcomputer, a TRS-80, and started programming more extensively, writing simple games and even a word processor.

```

