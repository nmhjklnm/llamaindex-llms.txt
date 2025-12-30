# Databricks¶
Integrate with Databricks LLMs APIs.
## Pre-requisites¶
  * Databricks personal access token to query and access Databricks model serving endpoints.
  * Databricks workspace in a supported region for Foundation Model APIs pay-per-token.


## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
% pip install llama-index-llms-databricks

```

% pip install llama-index-llms-databricks
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.llms.databricks import Databricks

```

from llama_index.llms.databricks import Databricks
```
None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.

```

```
export DATABRICKS_TOKEN=<your api key>
export DATABRICKS_SERVING_ENDPOINT=<your api serving endpoint>

```

Alternatively, you can pass your API key and serving endpoint to the LLM when you init it:
In [ ]:
Copied!
```
llm = Databricks(
    model="databricks-dbrx-instruct",
    api_key="your_api_key",
    api_base="https://[your-work-space].cloud.databricks.com/serving-endpoints/",
)

```

llm = Databricks( model="databricks-dbrx-instruct", api_key="your_api_key", api_base="https://[your-work-space].cloud.databricks.com/serving-endpoints/", )
A list of available LLM models can be found here.
In [ ]:
Copied!
```
response = llm.complete("Explain the importance of open source LLMs")

```

response = llm.complete("Explain the importance of open source LLMs")
In [ ]:
Copied!
```
print(response)

```

print(response)
#### Call `chat` with a list of messages¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="What is your name"),
]
resp = llm.chat(messages)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="What is your name"), ] resp = llm.chat(messages)
In [ ]:
Copied!
```
print(resp)

```

print(resp)
### Streaming¶
Using `stream_complete` endpoint
In [ ]:
Copied!
```
response = llm.stream_complete("Explain the importance of open source LLMs")

```

response = llm.stream_complete("Explain the importance of open source LLMs")
In [ ]:
Copied!
```
for r in response:
    print(r.delta, end="")

```

for r in response: print(r.delta, end="")
Using `stream_chat` endpoint
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="What is your name"),
]
resp = llm.stream_chat(messages)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="What is your name"), ] resp = llm.stream_chat(messages)
In [ ]:
Copied!
```
for r in resp:
    print(r.delta, end="")

```

for r in resp: print(r.delta, end="")
