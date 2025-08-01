# Chat Summary Memory Buffer¶
**NOTE:** This example of memory is deprecated in favor of the newer and more flexible `Memory` class. See the latest docs.
The `ChatSummaryMemoryBuffer` is a memory buffer that stores the last X messages that fit into a token limit. It also summarizes the chat history into a single message.
In [ ]:
Copied!
```
%pip install llama-index-core

```

%pip install llama-index-core
## Setup¶
In [ ]:
Copied!
```
from llama_index.core.memory import ChatSummaryMemoryBuffer

memory = ChatSummaryMemoryBuffer.from_defaults(
    token_limit=40000,
    # optional set the summary prompt, here's the default:
    # summarize_prompt=(
    #     "The following is a conversation between the user and assistant. "
    #     "Write a concise summary about the contents of this conversation."
    # )
)

```

from llama_index.core.memory import ChatSummaryMemoryBuffer memory = ChatSummaryMemoryBuffer.from_defaults( token_limit=40000, # optional set the summary prompt, here's the default: # summarize_prompt=( # "The following is a conversation between the user and assistant. " # "Write a concise summary about the contents of this conversation." # ) )
## Using Standalone¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

chat_history = [
    ChatMessage(role="user", content="Hello, how are you?"),
    ChatMessage(role="assistant", content="I'm doing well, thank you!"),
]

# put a list of messages
memory.put_messages(chat_history)

# put one message at a time
# memory.put_message(chat_history[0])

```

from llama_index.core.llms import ChatMessage chat_history = [ ChatMessage(role="user", content="Hello, how are you?"), ChatMessage(role="assistant", content="I'm doing well, thank you!"), ] # put a list of messages memory.put_messages(chat_history) # put one message at a time # memory.put_message(chat_history[0])
In [ ]:
Copied!
```
# Get the last X messages that fit into a token limit
history = memory.get()

```

# Get the last X messages that fit into a token limit history = memory.get()
In [ ]:
Copied!
```
# Get all messages
all_history = memory.get_all()

```

# Get all messages all_history = memory.get_all()
In [ ]:
Copied!
```
# clear the memory
memory.reset()

```

# clear the memory memory.reset()
## Using with Agents¶
You can set the memory in any agent in the `.run()` method.
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-proj-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-proj-..."
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import ReActAgent, FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI


memory = ChatMemoryBuffer.from_defaults(token_limit=40000)

agent = FunctionAgent(tools=[], llm=OpenAI(model="gpt-4o-mini"))

# context to hold the chat history/state
ctx = Context(agent)

```

from llama_index.core.agent.workflow import ReActAgent, FunctionAgent from llama_index.core.workflow import Context from llama_index.llms.openai import OpenAI memory = ChatMemoryBuffer.from_defaults(token_limit=40000) agent = FunctionAgent(tools=[], llm=OpenAI(model="gpt-4o-mini")) # context to hold the chat history/state ctx = Context(agent)
In [ ]:
Copied!
```
resp = await agent.run("Hello, how are you?", ctx=ctx, memory=memory)

```

resp = await agent.run("Hello, how are you?", ctx=ctx, memory=memory)
In [ ]:
Copied!
```
print(memory.get_all())

```

print(memory.get_all())
```
[ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text='Hello, how are you?')]), ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text="Hello! I'm just a program, so I don't have feelings, but I'm here and ready to help you. How can I assist you today?")])]

```

