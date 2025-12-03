![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Chat Engine - Best Mode¶
The default chat engine mode is "best", which uses the "openai" mode if you are using an OpenAI model that supports the latest function calling API, otherwise uses the "react" mode
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-anthropic
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-anthropic %pip install llama-index-llms-openai
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
--2024-01-27 12:15:55--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8001::154, 2606:50c0:8002::154, 2606:50c0:8003::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8001::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.008s  

2024-01-27 12:15:55 (9.38 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

### Get started in 5 lines of code¶
Load data and build index
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

llm = OpenAI(model="gpt-4")
data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data()
index = VectorStoreIndex.from_documents(data)

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.llms.openai import OpenAI from llama_index.llms.anthropic import Anthropic llm = OpenAI(model="gpt-4") data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data() index = VectorStoreIndex.from_documents(data)
Configure chat engine
In [ ]:
Copied!
```
chat_engine = index.as_chat_engine(chat_mode="best", llm=llm, verbose=True)

```

chat_engine = index.as_chat_engine(chat_mode="best", llm=llm, verbose=True)
Chat with your data
In [ ]:
Copied!
```
response = chat_engine.chat(
    "What are the first programs Paul Graham tried writing?"
)

```

response = chat_engine.chat( "What are the first programs Paul Graham tried writing?" )
```
Added user message to memory: What are the first programs Paul Graham tried writing?
=== Calling Function ===
Calling function: query_engine_tool with args: {
  "input": "What are the first programs Paul Graham tried writing?"
}
Got output: The first programs Paul Graham tried writing were on the IBM 1401 that their school district used for what was then called "data processing." The language he used was an early version of Fortran.
========================


```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The first programs Paul Graham tried writing were on the IBM 1401. He used an early version of Fortran for these initial programs.

```

