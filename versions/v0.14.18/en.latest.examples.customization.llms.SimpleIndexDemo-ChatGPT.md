![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# ChatGPT¶
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
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from IPython.display import Markdown, display

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core import Settings from llama_index.llms.openai import OpenAI from IPython.display import Markdown, display
#### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
#### Load documents, build the VectorStoreIndex¶
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham").load_data()
In [ ]:
Copied!
```
# set global settings config
llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.llm = llm
Settings.chunk_size = 512

```

# set global settings config llm = OpenAI(temperature=0, model="gpt-3.5-turbo") Settings.llm = llm Settings.chunk_size = 512
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
#### Query Index¶
By default, with the help of langchain's PromptSelector abstraction, we use a modified refine prompt tailored for ChatGPT-use if the ChatGPT model is used.
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=3,
    streaming=True,
)
response = query_engine.query(
    "What did the author do growing up?",
)

```

query_engine = index.as_query_engine( similarity_top_k=3, streaming=True, ) response = query_engine.query( "What did the author do growing up?", )
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 8 tokens
> [retrieve] Total embedding token usage: 8 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 0 tokens
> [get_response] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
response.print_response_stream()

```

response.print_response_stream()
```
Before college, the author worked on writing short stories and programming on an IBM 1401 using an early version of Fortran. They also worked on programming with microcomputers and eventually created a new dialect of Lisp called Arc. They later realized the potential of publishing essays on the web and began writing and publishing them. The author also worked on spam filters, painting, and cooking for groups.
```

In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=5,
    streaming=True,
)
response = query_engine.query(
    "What did the author do during his time at RISD?",
)

```

query_engine = index.as_query_engine( similarity_top_k=5, streaming=True, ) response = query_engine.query( "What did the author do during his time at RISD?", )
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 12 tokens
> [retrieve] Total embedding token usage: 12 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 0 tokens
> [get_response] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
response.print_response_stream()

```

response.print_response_stream()
```
The author attended RISD and took classes in fundamental subjects like drawing, color, and design. They also learned a lot in the color class they took, but otherwise, they were basically teaching themselves to paint. The author dropped out of RISD in 1993.
```

**Refine Prompt** : Here is the chat refine prompt
In [ ]:
Copied!
```
from llama_index.core.prompts.chat_prompts import CHAT_REFINE_PROMPT

```

from llama_index.core.prompts.chat_prompts import CHAT_REFINE_PROMPT
In [ ]:
Copied!
```
dict(CHAT_REFINE_PROMPT.prompt)

```

dict(CHAT_REFINE_PROMPT.prompt)
#### Query Index (Using the standard Refine Prompt)¶
If we use the "standard" refine prompt (where the prompt is one text template instead of multiple messages), we find that the results over ChatGPT are worse.
In [ ]:
Copied!
```
from llama_index.core.prompts.default_prompts import DEFAULT_REFINE_PROMPT

```

from llama_index.core.prompts.default_prompts import DEFAULT_REFINE_PROMPT
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    refine_template=DEFAULT_REFINE_PROMPT,
    similarity_top_k=5,
    streaming=True,
)
response = query_engine.query(
    "What did the author do during his time at RISD?",
)

```

query_engine = index.as_query_engine( refine_template=DEFAULT_REFINE_PROMPT, similarity_top_k=5, streaming=True, ) response = query_engine.query( "What did the author do during his time at RISD?", )
In [ ]:
Copied!
```
response.print_response_stream()

```

response.print_response_stream()
