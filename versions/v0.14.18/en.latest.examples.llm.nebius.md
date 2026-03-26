![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Nebius LLMs¶
This notebook demonstrates how to use LLMs from Nebius AI Studio with LlamaIndex. Nebius AI Studio implements all state-of-the-art LLMs available for commercial use.
First, let's install LlamaIndex and dependencies of Nebius AI Studio.
In [ ]:
Copied!
```
%pip install llama-index-llms-nebius llama-index

```

%pip install llama-index-llms-nebius llama-index
Upload your Nebius AI Studio key from system variables below or simply insert it. You can get it by registering for free at Nebius AI Studio and issuing the key at API Keys section."
In [ ]:
Copied!
```
import os

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY")  # NEBIUS_API_KEY = ""

```

import os NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY") # NEBIUS_API_KEY = ""
In [ ]:
Copied!
```
from llama_index.llms.nebius import NebiusLLM

llm = NebiusLLM(
    api_key=NEBIUS_API_KEY, model="meta-llama/Llama-3.3-70B-Instruct-fast"
)

```

from llama_index.llms.nebius import NebiusLLM llm = NebiusLLM( api_key=NEBIUS_API_KEY, model="meta-llama/Llama-3.3-70B-Instruct-fast" )
```
None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.

```

#### Call `complete` with a prompt¶
In [ ]:
Copied!
```
response = llm.complete("Amsterdam is the capital of ")
print(response)

```

response = llm.complete("Amsterdam is the capital of ") print(response)
```
The Netherlands! Amsterdam is indeed the capital and largest city of the Netherlands.

```

#### Call `chat` with a list of messages¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(role="system", content="You are a helpful AI assistant."),
    ChatMessage(
        role="user",
        content="Answer briefly: who is Wall-e?",
    ),
]
response = llm.chat(messages)
print(response)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage(role="system", content="You are a helpful AI assistant."), ChatMessage( role="user", content="Answer briefly: who is Wall-e?", ), ] response = llm.chat(messages) print(response)
```
assistant: WALL-E is a small waste-collecting robot and the main character in the 2008 Pixar animated film of the same name.

```

### Streaming¶
#### Using `stream_complete` endpoint¶
In [ ]:
Copied!
```
response = llm.stream_complete("Amsterdam is the capital of ")
for r in response:
    print(r.delta, end="")

```

response = llm.stream_complete("Amsterdam is the capital of ") for r in response: print(r.delta, end="")
```
The Netherlands! Amsterdam is indeed the capital and largest city of the Netherlands.
```

#### Using `stream_chat` with a list of messages¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(role="system", content="You are a helpful AI assistant."),
    ChatMessage(
        role="user",
        content="Answer briefly: who is Wall-e?",
    ),
]
response = llm.stream_chat(messages)
for r in response:
    print(r.delta, end="")

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage(role="system", content="You are a helpful AI assistant."), ChatMessage( role="user", content="Answer briefly: who is Wall-e?", ), ] response = llm.stream_chat(messages) for r in response: print(r.delta, end="")
```
WALL-E is a small waste-collecting robot and the main character in the 2008 Pixar animated film of the same name.
```

