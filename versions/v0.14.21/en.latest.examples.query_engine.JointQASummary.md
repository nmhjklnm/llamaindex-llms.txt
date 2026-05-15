![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Joint QA Summary Query Engine¶
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
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
## Load Data¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

reader = SimpleDirectoryReader("./data/paul_graham/")
documents = reader.load_data()

```

from llama_index.core import SimpleDirectoryReader reader = SimpleDirectoryReader("./data/paul_graham/") documents = reader.load_data()
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

gpt4 = OpenAI(temperature=0, model="gpt-4")

chatgpt = OpenAI(temperature=0, model="gpt-3.5-turbo")

```

from llama_index.llms.openai import OpenAI gpt4 = OpenAI(temperature=0, model="gpt-4") chatgpt = OpenAI(temperature=0, model="gpt-3.5-turbo")
In [ ]:
Copied!
```
from llama_index.core.composability import QASummaryQueryEngineBuilder

# NOTE: can also specify an existing docstore, summary text, qa_text, etc.
query_engine_builder = QASummaryQueryEngineBuilder(
    llm=gpt4,
)
query_engine = query_engine_builder.build_from_documents(documents)

```

from llama_index.core.composability import QASummaryQueryEngineBuilder # NOTE: can also specify an existing docstore, summary text, qa_text, etc. query_engine_builder = QASummaryQueryEngineBuilder( llm=gpt4, ) query_engine = query_engine_builder.build_from_documents(documents)
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 20729 tokens
> [build_index_from_nodes] Total embedding token usage: 20729 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens
> [build_index_from_nodes] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
response = query_engine.query(
    "Can you give me a summary of the author's life?",
)

```

response = query_engine.query( "Can you give me a summary of the author's life?", )
```
INFO:llama_index.query_engine.router_query_engine:Selecting query engine 1 because: This choice is relevant because it is specifically for summarization queries, which matches the request for a summary of the author's life..
Selecting query engine 1 because: This choice is relevant because it is specifically for summarization queries, which matches the request for a summary of the author's life..
INFO:llama_index.indices.common_tree.base:> Building index from nodes: 6 chunks
> Building index from nodes: 6 chunks
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 1012 tokens
> [get_response] Total LLM token usage: 1012 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 23485 tokens
> [get_response] Total LLM token usage: 23485 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
response = query_engine.query(
    "What did the author do growing up?",
)

```

response = query_engine.query( "What did the author do growing up?", )
```
INFO:llama_index.query_engine.router_query_engine:Selecting query engine 0 because: This choice is relevant because it involves retrieving specific context from documents, which is needed to answer the question about the author's activities growing up..
Selecting query engine 0 because: This choice is relevant because it involves retrieving specific context from documents, which is needed to answer the question about the author's activities growing up..
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 8 tokens
> [retrieve] Total embedding token usage: 8 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 1893 tokens
> [get_response] Total LLM token usage: 1893 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
response = query_engine.query(
    "What did the author do during his time in art school?",
)

```

response = query_engine.query( "What did the author do during his time in art school?", )
```
INFO:llama_index.query_engine.router_query_engine:Selecting query engine 0 because: This choice is relevant because it involves retrieving specific context from documents, which is needed to answer the question about the author's activities in art school..
Selecting query engine 0 because: This choice is relevant because it involves retrieving specific context from documents, which is needed to answer the question about the author's activities in art school..
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 12 tokens
> [retrieve] Total embedding token usage: 12 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 1883 tokens
> [get_response] Total LLM token usage: 1883 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

