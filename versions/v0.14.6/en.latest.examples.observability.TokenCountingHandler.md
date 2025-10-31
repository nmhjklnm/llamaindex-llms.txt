![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Token Counting Handler¶
This notebook walks through how to use the TokenCountingHandler and how it can be used to track your prompt, completion, and embedding token usage over time.
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
## Setup¶
Here, we setup the callback and the serivce context. We set global settings so that we don't have to worry about passing it into indexes and queries.
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
import tiktoken
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings


token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode
)

Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2)
Settings.callback_manager = CallbackManager([token_counter])

```

import tiktoken from llama_index.core.callbacks import CallbackManager, TokenCountingHandler from llama_index.llms.openai import OpenAI from llama_index.core import Settings token_counter = TokenCountingHandler( tokenizer=tiktoken.encoding_for_model("gpt-3.5-turbo").encode ) Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2) Settings.callback_manager = CallbackManager([token_counter])
## Token Counting¶
The token counter will track embedding, prompt, and completion token usage. The token counts are **cummulative** and are only reset when you choose to do so, with `token_counter.reset_counts()`.
### Embedding Token Usage¶
Now that the settings is setup, let's track our embedding token usage.
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham").load_data()
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
print(token_counter.total_embedding_token_count)

```

print(token_counter.total_embedding_token_count)


That looks right! Before we go any further, lets reset the counts
In [ ]:
Copied!
```
token_counter.reset_counts()

```

token_counter.reset_counts()
### LLM + Embedding Token Usage¶
Next, let's test a query and see what the counts look like.
In [ ]:
Copied!
```
query_engine = index.as_query_engine(similarity_top_k=4)
response = query_engine.query("What did the author do growing up?")

```

query_engine = index.as_query_engine(similarity_top_k=4) response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
print(
    "Embedding Tokens: ",
    token_counter.total_embedding_token_count,
    "\n",
    "LLM Prompt Tokens: ",
    token_counter.prompt_llm_token_count,
    "\n",
    "LLM Completion Tokens: ",
    token_counter.completion_llm_token_count,
    "\n",
    "Total LLM Token Count: ",
    token_counter.total_llm_token_count,
    "\n",
)

```

print( "Embedding Tokens: ", token_counter.total_embedding_token_count, "\n", "LLM Prompt Tokens: ", token_counter.prompt_llm_token_count, "\n", "LLM Completion Tokens: ", token_counter.completion_llm_token_count, "\n", "Total LLM Token Count: ", token_counter.total_llm_token_count, "\n", )
```
Embedding Tokens:  8 
 LLM Prompt Tokens:  4518 
 LLM Completion Tokens:  45 
 Total LLM Token Count:  4563 


```

### Token Counting + Streaming!¶
The token counting handler also handles token counting during streaming.
Here, token counting will only happen once the stream is completed.
In [ ]:
Copied!
```
token_counter.reset_counts()

query_engine = index.as_query_engine(similarity_top_k=4, streaming=True)
response = query_engine.query("What happened at Interleaf?")

# finish the stream
for token in response.response_gen:
    # print(token, end="", flush=True)
    continue

```

token_counter.reset_counts() query_engine = index.as_query_engine(similarity_top_k=4, streaming=True) response = query_engine.query("What happened at Interleaf?") # finish the stream for token in response.response_gen: # print(token, end="", flush=True) continue
In [ ]:
Copied!
```
print(
    "Embedding Tokens: ",
    token_counter.total_embedding_token_count,
    "\n",
    "LLM Prompt Tokens: ",
    token_counter.prompt_llm_token_count,
    "\n",
    "LLM Completion Tokens: ",
    token_counter.completion_llm_token_count,
    "\n",
    "Total LLM Token Count: ",
    token_counter.total_llm_token_count,
    "\n",
)

```

print( "Embedding Tokens: ", token_counter.total_embedding_token_count, "\n", "LLM Prompt Tokens: ", token_counter.prompt_llm_token_count, "\n", "LLM Completion Tokens: ", token_counter.completion_llm_token_count, "\n", "Total LLM Token Count: ", token_counter.total_llm_token_count, "\n", )
```
Embedding Tokens:  6 
 LLM Prompt Tokens:  4563 
 LLM Completion Tokens:  123 
 Total LLM Token Count:  4686 


```

## Advanced Usage¶
The token counter tracks each token usage event in an object called a `TokenCountingEvent`. This object has the following attributes:
  * prompt -> The prompt string sent to the LLM or Embedding model
  * prompt_token_count -> The token count of the LLM prompt
  * completion -> The string completion received from the LLM (not used for embeddings)
  * completion_token_count -> The token count of the LLM completion (not used for embeddings)
  * total_token_count -> The total prompt + completion tokens for the event
  * event_id -> A string ID for the event, which aligns with other callback handlers


These events are tracked on the token counter in two lists:
  * llm_token_counts
  * embedding_token_counts


Let's explore what these look like!
In [ ]:
Copied!
```
print("Num LLM token count events: ", len(token_counter.llm_token_counts))
print(
    "Num Embedding token count events: ",
    len(token_counter.embedding_token_counts),
)

```

print("Num LLM token count events: ", len(token_counter.llm_token_counts)) print( "Num Embedding token count events: ", len(token_counter.embedding_token_counts), )
```
Num LLM token count events:  2
Num Embedding token count events:  1

```

This makes sense! The previous query embedded the query text, and then made 2 LLM calls (since the top k was 4, and the default chunk size is 1024, two separate calls need to be made so the LLM can read all the retrieved text).
Next, let's quickly see what these events look like for a single event.
In [ ]:
Copied!
```
print("prompt: ", token_counter.llm_token_counts[0].prompt[:100], "...\n")
print(
    "prompt token count: ",
    token_counter.llm_token_counts[0].prompt_token_count,
    "\n",
)

print(
    "completion: ", token_counter.llm_token_counts[0].completion[:100], "...\n"
)
print(
    "completion token count: ",
    token_counter.llm_token_counts[0].completion_token_count,
    "\n",
)

print("total token count", token_counter.llm_token_counts[0].total_token_count)

```

print("prompt: ", token_counter.llm_token_counts[0].prompt[:100], "...\n") print( "prompt token count: ", token_counter.llm_token_counts[0].prompt_token_count, "\n", ) print( "completion: ", token_counter.llm_token_counts[0].completion[:100], "...\n" ) print( "completion token count: ", token_counter.llm_token_counts[0].completion_token_count, "\n", ) print("total token count", token_counter.llm_token_counts[0].total_token_count)
```
prompt:  system: You are an expert Q&A system that is trusted around the world.
Always answer the query using ...

prompt token count:  3873 

completion:  assistant: At Interleaf, the company had added a scripting language inspired by Emacs and made it a  ...

completion token count:  95 

total token count 3968

```

