![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Llama2 + VectorStoreIndex¶
This notebook walks through the proper setup to use llama-2 with LlamaIndex. Specifically, we look at using a vector store index.
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-replicate

```

%pip install llama-index-llms-replicate
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
### Keys¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["REPLICATE_API_TOKEN"] = "YOUR_REPLICATE_TOKEN"

```

import os os.environ["OPENAI_API_KEY"] = "sk-..." os.environ["REPLICATE_API_TOKEN"] = "YOUR_REPLICATE_TOKEN"
### Load documents, build the VectorStoreIndex¶
In [ ]:
Copied!
```
# Optional logging
# import logging
# import sys

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from IPython.display import Markdown, display

```

# Optional logging # import logging # import sys # logging.basicConfig(stream=sys.stdout, level=logging.INFO) # logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from IPython.display import Markdown, display
In [ ]:
Copied!
```
from llama_index.llms.replicate import Replicate
from llama_index.core.llms.llama_utils import (
    messages_to_prompt,
    completion_to_prompt,
)

# The replicate endpoint
LLAMA_13B_V2_CHAT = "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5"


# inject custom system prompt into llama-2
def custom_completion_to_prompt(completion: str) -> str:
    return completion_to_prompt(
        completion,
        system_prompt=(
            "You are a Q&A assistant. Your goal is to answer questions as "
            "accurately as possible is the instructions and context provided."
        ),
    )


llm = Replicate(
    model=LLAMA_13B_V2_CHAT,
    temperature=0.01,
    # override max tokens since it's interpreted
    # as context window instead of max tokens
    context_window=4096,
    # override completion representation for llama 2
    completion_to_prompt=custom_completion_to_prompt,
    # if using llama 2 for data agents, also override the message representation
    messages_to_prompt=messages_to_prompt,
)

```

from llama_index.llms.replicate import Replicate from llama_index.core.llms.llama_utils import ( messages_to_prompt, completion_to_prompt, ) # The replicate endpoint LLAMA_13B_V2_CHAT = "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5" # inject custom system prompt into llama-2 def custom_completion_to_prompt(completion: str) -> str: return completion_to_prompt( completion, system_prompt=( "You are a Q&A assistant. Your goal is to answer questions as " "accurately as possible is the instructions and context provided." ), ) llm = Replicate( model=LLAMA_13B_V2_CHAT, temperature=0.01, # override max tokens since it's interpreted # as context window instead of max tokens context_window=4096, # override completion representation for llama 2 completion_to_prompt=custom_completion_to_prompt, # if using llama 2 for data agents, also override the message representation messages_to_prompt=messages_to_prompt, )
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = llm

```

from llama_index.core import Settings Settings.llm = llm
Download Data
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
## Querying¶
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine()
In [ ]:
Copied!
```
response = query_engine.query("What did the author do growing up?")
display(Markdown(f"<b>{response}</b>"))

```

response = query_engine.query("What did the author do growing up?") display(Markdown(f"**{response}** "))
**Based on the context information provided, the author's activities growing up were:**
  1. Writing short stories, which were "awful" and had "hardly any plot."
  2. Programming on an IBM 1401 computer in 9th grade, using an early version of Fortran language.
  3. Building simple games, a program to predict the height of model rockets, and a word processor for his father.
  4. Reading science fiction novels, such as "The Moon is a Harsh Mistress" by Heinlein, which inspired him to work on AI.
  5. Living in Florence, Italy, and walking through the city's streets to the Accademia.


Please note that these activities are mentioned in the text and are not based on prior knowledge or assumptions.
### Streaming Support¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(streaming=True)
response = query_engine.query("What happened at interleaf?")
for token in response.response_gen:
    print(token, end="")

```

query_engine = index.as_query_engine(streaming=True) response = query_engine.query("What happened at interleaf?") for token in response.response_gen: print(token, end="")
```
 Based on the context information provided, it appears that the author worked at Interleaf, a company that made software for creating and managing documents. The author mentions that Interleaf was "on the way down" and that the company's Release Engineering group was large compared to the group that actually wrote the software. It is inferred that Interleaf was experiencing financial difficulties and that the author was nervous about money. However, there is no explicit mention of what specifically happened at Interleaf.
```

