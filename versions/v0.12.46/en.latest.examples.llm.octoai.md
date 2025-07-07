![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# OctoAI¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-octoai
%pip install llama-index
%pip install octoai-sdk

```

%pip install llama-index-llms-octoai %pip install llama-index %pip install octoai-sdk
Include your OctoAI API key below. You can get yours at OctoAI.
Here are some instructions in case you need more guidance.
In [ ]:
Copied!
```
OCTOAI_API_KEY = ""

```

OCTOAI_API_KEY = ""
#### Initialize the Integration with the default model¶
In [ ]:
Copied!
```
from llama_index.llms.octoai import OctoAI

octoai = OctoAI(token=OCTOAI_API_KEY)

```

from llama_index.llms.octoai import OctoAI octoai = OctoAI(token=OCTOAI_API_KEY)
#### Call `complete` with a prompt¶
In [ ]:
Copied!
```
response = octoai.complete("Paul Graham is ")
print(response)

```

response = octoai.complete("Paul Graham is ") print(response)
#### Call `chat` with a list of messages¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system",
        content="Below is an instruction that describes a task. Write a response that appropriately completes the request.",
    ),
    ChatMessage(role="user", content="Write a blog about Seattle"),
]
response = octoai.chat(messages)
print(response)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="Below is an instruction that describes a task. Write a response that appropriately completes the request.", ), ChatMessage(role="user", content="Write a blog about Seattle"), ] response = octoai.chat(messages) print(response)
## Streaming¶
Using `stream_complete` endpoint
In [ ]:
Copied!
```
response = octoai.stream_complete("Paul Graham is ")
for r in response:
    print(r.delta, end="")

```

response = octoai.stream_complete("Paul Graham is ") for r in response: print(r.delta, end="")
Using `stream_chat` with a list of messages
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system",
        content="Below is an instruction that describes a task. Write a response that appropriately completes the request.",
    ),
    ChatMessage(role="user", content="Write a blog about Seattle"),
]
response = octoai.stream_chat(messages)
for r in response:
    print(r.delta, end="")

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="Below is an instruction that describes a task. Write a response that appropriately completes the request.", ), ChatMessage(role="user", content="Write a blog about Seattle"), ] response = octoai.stream_chat(messages) for r in response: print(r.delta, end="")
## Configure Model¶
In [ ]:
Copied!
```
# To customize your API token, do this
# otherwise it will lookup OCTOAI_TOKEN from your env variable
octoai = OctoAI(
    model="mistral-7b-instruct", max_tokens=128, token=OCTOAI_API_KEY
)

response = octoai.complete("Paul Graham is ")
print(response)

```

# To customize your API token, do this # otherwise it will lookup OCTOAI_TOKEN from your env variable octoai = OctoAI( model="mistral-7b-instruct", max_tokens=128, token=OCTOAI_API_KEY ) response = octoai.complete("Paul Graham is ") print(response)
