![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Mem0¶
Mem0 (pronounced “mem-zero”) enhances AI assistants and agents with an intelligent memory layer, enabling personalized AI interactions. It remembers user preferences and traits and continuously updates over time, making it ideal for applications like customer support chatbots and AI assistants.
Mem0 offers two powerful ways to leverage our technology: our managed platform and our open source solution.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index llama-index-memory-mem0

```

%pip install llama-index llama-index-memory-mem0
### Setup with Mem0 Platform¶
Set your Mem0 Platform API key as an environment variable. You can replace `<your-mem0-api-key>` with your actual API key:
> Note: You can obtain your Mem0 Platform API key from the Mem0 Platform.
In [ ]:
Copied!
```
import os

os.environ["MEM0_API_KEY"] = "m0-..."

```

import os os.environ["MEM0_API_KEY"] = "m0-..."
Using `from_client` (for Mem0 platform API):
In [ ]:
Copied!
```
from llama_index.memory.mem0 import Mem0Memory

context = {"user_id": "test_users_1"}
memory_from_client = Mem0Memory.from_client(
    context=context,
    api_key="m0-...",
    search_msg_limit=4,  # Default is 5
)

```

from llama_index.memory.mem0 import Mem0Memory context = {"user_id": "test_users_1"} memory_from_client = Mem0Memory.from_client( context=context, api_key="m0-...", search_msg_limit=4, # Default is 5 )
Mem0 Context is used to identify the user, agent or the conversation in the Mem0. It is required to be passed in the at least one of the fields in the `Mem0Memory` constructor.
`search_msg_limit` is optional, default is 5. It is the number of messages from the chat history to be used for memory retrieval from Mem0. More number of messages will result in more context being used for retrieval but will also increase the retrieval time and might result in some unwanted results.
Using `from_config` (for Mem0 OSS)
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "<your-api-key>"
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "test_9",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 1536,  # Change this according to your local model's dimensions
        },
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 1500,
        },
    },
    "embedder": {
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"},
    },
    "version": "v1.1",
}
memory_from_config = Mem0Memory.from_config(
    context=context,
    config=config,
    search_msg_limit=4,  # Default is 5
)

```

os.environ["OPENAI_API_KEY"] = "" config = { "vector_store": { "provider": "qdrant", "config": { "collection_name": "test_9", "host": "localhost", "port": 6333, "embedding_model_dims": 1536, # Change this according to your local model's dimensions }, }, "llm": { "provider": "openai", "config": { "model": "gpt-4o", "temperature": 0.2, "max_tokens": 1500, }, }, "embedder": { "provider": "openai", "config": {"model": "text-embedding-3-small"}, }, "version": "v1.1", } memory_from_config = Mem0Memory.from_config( context=context, config=config, search_msg_limit=4, # Default is 5 )
### Initialize LLM¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o", api_key="sk-...")

```

from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-4o", api_key="sk-...")
## Mem0 for Function Calling Agents¶
Use `Mem0` as memory for `FunctionCallingAgents`.
### Initialize Tools¶
In [ ]:
Copied!
```
def call_fn(name: str):
    """Call the provided name.
    Args:
        name: str (Name of the person)
    """
    print(f"Calling... {name}")


def email_fn(name: str):
    """Email the provided name.
    Args:
        name: str (Name of the person)
    """
    print(f"Emailing... {name}")

```

def call_fn(name: str): """Call the provided name. Args: name: str (Name of the person) """ print(f"Calling... {name}") def email_fn(name: str): """Email the provided name. Args: name: str (Name of the person) """ print(f"Emailing... {name}")
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent

agent = FunctionAgent(
    tools=[email_fn, call_fn],
    llm=llm,
)

```

from llama_index.core.agent.workflow import FunctionAgent agent = FunctionAgent( tools=[email_fn, call_fn], llm=llm, )
In [ ]:
Copied!
```
response = await agent.run("Hi, My name is Mayank.", memory=memory_from_client)
print(str(response))

```

response = await agent.run("Hi, My name is Mayank.", memory=memory_from_client) print(str(response))
```
/Users/loganmarkewich/Library/Caches/pypoetry/virtualenvs/llama-index-caVs7DDe-py3.10/lib/python3.10/site-packages/mem0/client/main.py:33: DeprecationWarning: output_format='v1.0' is deprecated therefore setting it to 'v1.1' by default.Check out the docs for more information: https://docs.mem0.ai/platform/quickstart#4-1-create-memories
  return func(*args, **kwargs)

```

```
Hello Mayank! How can I assist you today?

```

In [ ]:
Copied!
```
response = await agent.run(
    "My preferred way of communication would be Email.",
    memory=memory_from_client,
)
print(str(response))

```

response = await agent.run( "My preferred way of communication would be Email.", memory=memory_from_client, ) print(str(response))
```
Got it, Mayank! Your preferred way of communication is Email. If there's anything specific you need, feel free to let me know!

```

In [ ]:
Copied!
```
response = await agent.run(
    "Send me an update of your product.", memory=memory_from_client
)
print(str(response))

```

response = await agent.run( "Send me an update of your product.", memory=memory_from_client ) print(str(response))
```
Emailing... Mayank
Emailing... Mayank
Calling... Mayank
Emailing... Mayank

```

```
I've sent you an update on our product via email. If you have any other questions or need further assistance, feel free to ask!

```

## Mem0 for ReAct Agents¶
Use `Mem0` as memory for `ReActAgent`.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import ReActAgent

agent = ReActAgent(
    tools=[call_fn, email_fn],
    llm=llm,
)

```

from llama_index.core.agent.workflow import ReActAgent agent = ReActAgent( tools=[call_fn, email_fn], llm=llm, )
In [ ]:
Copied!
```
response = await agent.run("Hi, My name is Mayank.", memory=memory_from_client)
print(str(response))

```

response = await agent.run("Hi, My name is Mayank.", memory=memory_from_client) print(str(response))
In [ ]:
Copied!
```
response = await agent.run(
    "My preferred way of communication would be Email.",
    memory=memory_from_client,
)
print(str(response))

```

response = await agent.run( "My preferred way of communication would be Email.", memory=memory_from_client, ) print(str(response))
In [ ]:
Copied!
```
response = await agent.run(
    "Send me an update of your product.", memory=memory_from_client
)
print(str(response))

```

response = await agent.run( "Send me an update of your product.", memory=memory_from_client ) print(str(response))
In [ ]:
Copied!
```
response = await agent.run(
    "First call me and then communicate me requirements.",
    memory=memory_from_client,
)
print(str(response))

```

response = await agent.run( "First call me and then communicate me requirements.", memory=memory_from_client, ) print(str(response))
