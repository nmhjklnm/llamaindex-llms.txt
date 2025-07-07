![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Simple Composable Memory¶
**NOTE:** This example of memory is deprecated in favor of the newer and more flexible `Memory` class. See the latest docs.
In this notebook, we demonstrate how to inject multiple memory sources into an agent. Specifically, we use the `SimpleComposableMemory` which is comprised of a `primary_memory` as well as potentially several secondary memory sources (stored in `secondary_memory_sources`). The main difference is that `primary_memory` will be used as the main chat buffer for the agent, where as any retrieved messages from `secondary_memory_sources` will be injected to the system prompt message only.
Multiple memory sources may be of use for example in situations where you have a longer-term memory such as `VectorMemory` that you want to use in addition to the default `ChatMemoryBuffer`. What you'll see in this notebook is that with a `SimpleComposableMemory` you'll be able to effectively "load" the desired messages from long-term memory into the main memory (i.e. the `ChatMemoryBuffer`).
## How `SimpleComposableMemory` Works?¶
We begin with the basic usage of the `SimpleComposableMemory`. Here we construct a `VectorMemory` as well as a default `ChatMemoryBuffer`. The `VectorMemory` will be our secondary memory source, whereas the `ChatMemoryBuffer` will be the main or primary one. To instantiate a `SimpleComposableMemory` object, we need to supply a `primary_memory` and (optionally) a list of `secondary_memory_sources`.
![SimpleComposableMemoryIllustration](https://d3ddy8balm3goa.cloudfront.net/llamaindex/simple-composable-memory.excalidraw.svg)
In [ ]:
Copied!
```
from llama_index.core.memory import (
    VectorMemory,
    SimpleComposableMemory,
    ChatMemoryBuffer,
)
from llama_index.core.llms import ChatMessage
from llama_index.embeddings.openai import OpenAIEmbedding

vector_memory = VectorMemory.from_defaults(
    vector_store=None,  # leave as None to use default in-memory vector store
    embed_model=OpenAIEmbedding(),
    retriever_kwargs={"similarity_top_k": 1},
)

# let's set some initial messages in our secondary vector memory
msgs = [
    ChatMessage.from_str("You are a SOMEWHAT helpful assistant.", "system"),
    ChatMessage.from_str("Bob likes burgers.", "user"),
    ChatMessage.from_str("Indeed, Bob likes apples.", "assistant"),
    ChatMessage.from_str("Alice likes apples.", "user"),
]
vector_memory.set(msgs)

chat_memory_buffer = ChatMemoryBuffer.from_defaults()

composable_memory = SimpleComposableMemory.from_defaults(
    primary_memory=chat_memory_buffer,
    secondary_memory_sources=[vector_memory],
)

```

from llama_index.core.memory import ( VectorMemory, SimpleComposableMemory, ChatMemoryBuffer, ) from llama_index.core.llms import ChatMessage from llama_index.embeddings.openai import OpenAIEmbedding vector_memory = VectorMemory.from_defaults( vector_store=None, # leave as None to use default in-memory vector store embed_model=OpenAIEmbedding(), retriever_kwargs={"similarity_top_k": 1}, ) # let's set some initial messages in our secondary vector memory msgs = [ ChatMessage.from_str("You are a SOMEWHAT helpful assistant.", "system"), ChatMessage.from_str("Bob likes burgers.", "user"), ChatMessage.from_str("Indeed, Bob likes apples.", "assistant"), ChatMessage.from_str("Alice likes apples.", "user"), ] vector_memory.set(msgs) chat_memory_buffer = ChatMemoryBuffer.from_defaults() composable_memory = SimpleComposableMemory.from_defaults( primary_memory=chat_memory_buffer, secondary_memory_sources=[vector_memory], )
In [ ]:
Copied!
```
composable_memory.primary_memory

```

composable_memory.primary_memory
Out[ ]:
```
ChatMemoryBuffer(chat_store=SimpleChatStore(store={}), chat_store_key='chat_history', token_limit=3000, tokenizer_fn=functools.partial(<bound method Encoding.encode of <Encoding 'cl100k_base'>>, allowed_special='all'))
```

In [ ]:
Copied!
```
composable_memory.secondary_memory_sources

```

composable_memory.secondary_memory_sources
Out[ ]:
```
[VectorMemory(vector_index=<llama_index.core.indices.vector_store.base.VectorStoreIndex object at 0x137b912a0>, retriever_kwargs={'similarity_top_k': 1}, batch_by_user_message=True, cur_batch_textnode=TextNode(id_='288b0ef3-570e-4698-a1ae-b3531df66361', embedding=None, metadata={'sub_dicts': [{'role': <MessageRole.USER: 'user'>, 'content': 'Alice likes apples.', 'additional_kwargs': {}}]}, excluded_embed_metadata_keys=['sub_dicts'], excluded_llm_metadata_keys=['sub_dicts'], relationships={}, text='Alice likes apples.', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'))]
```

###  `put()` messages into memory¶
Since `SimpleComposableMemory` is itself a subclass of `BaseMemory`, we add messages to it in the same way as we do for other memory modules. Note that for `SimpleComposableMemory`, invoking `.put()` effectively calls `.put()` on all memory sources. In other words, the message gets added to `primary` and `secondary` sources.
In [ ]:
Copied!
```
msgs = [
    ChatMessage.from_str("You are a REALLY helpful assistant.", "system"),
    ChatMessage.from_str("Jerry likes juice.", "user"),
]

```

msgs = [ ChatMessage.from_str("You are a REALLY helpful assistant.", "system"), ChatMessage.from_str("Jerry likes juice.", "user"), ]
In [ ]:
Copied!
```
# load into all memory sources modules"
for m in msgs:
    composable_memory.put(m)

```

# load into all memory sources modules" for m in msgs: composable_memory.put(m)
###  `get()` messages from memory¶
When `.get()` is invoked, we similarly execute all of the `.get()` methods of `primary` memory as well as all of the `secondary` sources. This leaves us with sequence of lists of messages that we have to must "compose" into a sensible single set of messages (to pass downstream to our agents). Special care must be applied here in general to ensure that the final sequence of messages are both sensible and conform to the chat APIs of the LLM provider.
For `SimpleComposableMemory`, we **inject the messages from the`secondary` sources in the system message of the `primary` memory**. The rest of the message history of the `primary` source is left intact, and this composition is what is ultimately returned.
In [ ]:
Copied!
```
msgs = composable_memory.get("What does Bob like?")
msgs

```

msgs = composable_memory.get("What does Bob like?") msgs
Out[ ]:
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content='You are a REALLY helpful assistant.\n\nBelow are a set of relevant dialogues retrieved from potentially several memory sources:\n\n=====Relevant messages from memory source 1=====\n\n\tUSER: Bob likes burgers.\n\tASSISTANT: Indeed, Bob likes apples.\n\n=====End of relevant messages from memory source 1======\n\nThis is the end of the retrieved message dialogues.', additional_kwargs={}),
 ChatMessage(role=<MessageRole.USER: 'user'>, content='Jerry likes juice.', additional_kwargs={})]
```

In [ ]:
Copied!
```
# see the memory injected into the system message of the primary memory
print(msgs[0])

```

# see the memory injected into the system message of the primary memory print(msgs[0])
```
system: You are a REALLY helpful assistant.

Below are a set of relevant dialogues retrieved from potentially several memory sources:

=====Relevant messages from memory source 1=====

	USER: Bob likes burgers.
	ASSISTANT: Indeed, Bob likes apples.

=====End of relevant messages from memory source 1======

This is the end of the retrieved message dialogues.

```

### Successive calls to `get()`¶
Successive calls of `get()` will simply replace the loaded `secondary` memory messages in the system prompt.
In [ ]:
Copied!
```
msgs = composable_memory.get("What does Alice like?")
msgs

```

msgs = composable_memory.get("What does Alice like?") msgs
Out[ ]:
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content='You are a REALLY helpful assistant.\n\nBelow are a set of relevant dialogues retrieved from potentially several memory sources:\n\n=====Relevant messages from memory source 1=====\n\n\tUSER: Alice likes apples.\n\n=====End of relevant messages from memory source 1======\n\nThis is the end of the retrieved message dialogues.', additional_kwargs={}),
 ChatMessage(role=<MessageRole.USER: 'user'>, content='Jerry likes juice.', additional_kwargs={})]
```

In [ ]:
Copied!
```
# see the memory injected into the system message of the primary memory
print(msgs[0])

```

# see the memory injected into the system message of the primary memory print(msgs[0])
```
system: You are a REALLY helpful assistant.

Below are a set of relevant dialogues retrieved from potentially several memory sources:

=====Relevant messages from memory source 1=====

	USER: Alice likes apples.

=====End of relevant messages from memory source 1======

This is the end of the retrieved message dialogues.

```

### What if `get()` retrieves `secondary` messages that already exist in `primary` memory?¶
In the event that messages retrieved from `secondary` memory already exist in `primary` memory, then these rather redundant secondary messages will not get added to the system message. In the below example, the message "Jerry likes juice." was `put` into all memory sources, so the system message is not altered.
In [ ]:
Copied!
```
msgs = composable_memory.get("What does Jerry like?")
msgs

```

msgs = composable_memory.get("What does Jerry like?") msgs
Out[ ]:
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content='You are a REALLY helpful assistant.', additional_kwargs={}),
 ChatMessage(role=<MessageRole.USER: 'user'>, content='Jerry likes juice.', additional_kwargs={})]
```

### How to `reset` memory¶
Similar to the other methods `put()` and `get()`, calling `reset()` will execute `reset()` on both the `primary` and `secondary` memory sources. If you want to reset only the `primary` then you should call the `reset()` method only from it.
####  `reset()` only primary memory¶
In [ ]:
Copied!
```
composable_memory.primary_memory.reset()

```

composable_memory.primary_memory.reset()
In [ ]:
Copied!
```
composable_memory.primary_memory.get()

```

composable_memory.primary_memory.get()
Out[ ]:
```
[]
```

In [ ]:
Copied!
```
composable_memory.secondary_memory_sources[0].get("What does Alice like?")

```

composable_memory.secondary_memory_sources[0].get("What does Alice like?")
Out[ ]:
```
[ChatMessage(role=<MessageRole.USER: 'user'>, content='Alice likes apples.', additional_kwargs={})]
```

####  `reset()` all memory sources¶
In [ ]:
Copied!
```
composable_memory.reset()

```

composable_memory.reset()
In [ ]:
Copied!
```
composable_memory.primary_memory.get()

```

composable_memory.primary_memory.get()
Out[ ]:
```
[]
```

In [ ]:
Copied!
```
composable_memory.secondary_memory_sources[0].get("What does Alice like?")

```

composable_memory.secondary_memory_sources[0].get("What does Alice like?")
Out[ ]:
```
[]
```

## Use `SimpleComposableMemory` With An Agent¶
Here we will use a `SimpleComposableMemory` with an agent and demonstrate how a secondary, long-term memory source can be used to use messages from on agent conversation as part of another conversation with another agent session.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
from llama_index.core.agent import FunctionCallingAgent

import nest_asyncio

nest_asyncio.apply()

```

from llama_index.llms.openai import OpenAI from llama_index.core.tools import FunctionTool from llama_index.core.agent import FunctionCallingAgent import nest_asyncio nest_asyncio.apply()
### Define our memory modules¶
In [ ]:
Copied!
```
vector_memory = VectorMemory.from_defaults(
    vector_store=None,  # leave as None to use default in-memory vector store
    embed_model=OpenAIEmbedding(),
    retriever_kwargs={"similarity_top_k": 2},
)

chat_memory_buffer = ChatMemoryBuffer.from_defaults()

composable_memory = SimpleComposableMemory.from_defaults(
    primary_memory=chat_memory_buffer,
    secondary_memory_sources=[vector_memory],
)

```

vector_memory = VectorMemory.from_defaults( vector_store=None, # leave as None to use default in-memory vector store embed_model=OpenAIEmbedding(), retriever_kwargs={"similarity_top_k": 2}, ) chat_memory_buffer = ChatMemoryBuffer.from_defaults() composable_memory = SimpleComposableMemory.from_defaults( primary_memory=chat_memory_buffer, secondary_memory_sources=[vector_memory], )
### Define our Agent¶
In [ ]:
Copied!
```
def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b


def mystery(a: int, b: int) -> int:
    """Mystery function on two numbers"""
    return a**2 - b**2


multiply_tool = FunctionTool.from_defaults(fn=multiply)
mystery_tool = FunctionTool.from_defaults(fn=mystery)

```

def multiply(a: int, b: int) -> int: """Multiply two integers and returns the result integer""" return a * b def mystery(a: int, b: int) -> int: """Mystery function on two numbers""" return a**2 - b**2 multiply_tool = FunctionTool.from_defaults(fn=multiply) mystery_tool = FunctionTool.from_defaults(fn=mystery)
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-3.5-turbo-0613")
agent = FunctionCallingAgent.from_tools(
    [multiply_tool, mystery_tool],
    llm=llm,
    memory=composable_memory,
    verbose=True,
)

```

llm = OpenAI(model="gpt-3.5-turbo-0613") agent = FunctionCallingAgent.from_tools( [multiply_tool, mystery_tool], llm=llm, memory=composable_memory, verbose=True, )
### Execute some function calls¶
When `.chat()` is invoked, the messages are put into the composable memory, which we understand from the previous section implies that all the messages are put in both `primary` and `secondary` sources.
In [ ]:
Copied!
```
response = agent.chat("What is the mystery function on 5 and 6?")

```

response = agent.chat("What is the mystery function on 5 and 6?")
```
Added user message to memory: What is the mystery function on 5 and 6?
=== Calling Function ===
Calling function: mystery with args: {"a": 5, "b": 6}
=== Function Output ===
-11
=== LLM Response ===
The mystery function on 5 and 6 returns -11.

```

In [ ]:
Copied!
```
response = agent.chat("What happens if you multiply 2 and 3?")

```

response = agent.chat("What happens if you multiply 2 and 3?")
```
Added user message to memory: What happens if you multiply 2 and 3?
=== Calling Function ===
Calling function: multiply with args: {"a": 2, "b": 3}
=== Function Output ===
6
=== LLM Response ===
If you multiply 2 and 3, the result is 6.

```

### New Agent Sessions¶
Now that we've added the messages to our `vector_memory`, we can see the effect of having this memory be used with a new agent session versus when it is used. Specifically, we ask the new agents to "recall" the outputs of the function calls, rather than re-computing.
#### An Agent without our past memory¶
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-3.5-turbo-0613")
agent_without_memory = FunctionCallingAgent.from_tools(
    [multiply_tool, mystery_tool], llm=llm, verbose=True
)

```

llm = OpenAI(model="gpt-3.5-turbo-0613") agent_without_memory = FunctionCallingAgent.from_tools( [multiply_tool, mystery_tool], llm=llm, verbose=True )
In [ ]:
Copied!
```
response = agent_without_memory.chat(
    "What was the output of the mystery function on 5 and 6 again? Don't recompute."
)

```

response = agent_without_memory.chat( "What was the output of the mystery function on 5 and 6 again? Don't recompute." )
```
Added user message to memory: What was the output of the mystery function on 5 and 6 again? Don't recompute.
=== LLM Response ===
I'm sorry, but I don't have access to the previous output of the mystery function on 5 and 6.

```

#### An Agent with our past memory¶
We see that the agent without access to the our past memory cannot complete the task. With this next agent we will indeed pass in our previous long-term memory (i.e., `vector_memory`). Note that we even use a fresh `ChatMemoryBuffer` which means there is no `chat_history` with this agent. Nonetheless, it will be able to retrieve from our long-term memory to get the past dialogue it needs.
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-3.5-turbo-0613")

composable_memory = SimpleComposableMemory.from_defaults(
    primary_memory=ChatMemoryBuffer.from_defaults(),
    secondary_memory_sources=[
        vector_memory.copy(
            deep=True
        )  # using a copy here for illustration purposes
        # later will use original vector_memory again
    ],
)

agent_with_memory = FunctionCallingAgent.from_tools(
    [multiply_tool, mystery_tool],
    llm=llm,
    memory=composable_memory,
    verbose=True,
)

```

llm = OpenAI(model="gpt-3.5-turbo-0613") composable_memory = SimpleComposableMemory.from_defaults( primary_memory=ChatMemoryBuffer.from_defaults(), secondary_memory_sources=[ vector_memory.copy( deep=True ) # using a copy here for illustration purposes # later will use original vector_memory again ], ) agent_with_memory = FunctionCallingAgent.from_tools( [multiply_tool, mystery_tool], llm=llm, memory=composable_memory, verbose=True, )
In [ ]:
Copied!
```
agent_with_memory.chat_history  # an empty chat history

```

agent_with_memory.chat_history # an empty chat history
Out[ ]:
```
[]
```

In [ ]:
Copied!
```
response = agent_with_memory.chat(
    "What was the output of the mystery function on 5 and 6 again? Don't recompute."
)

```

response = agent_with_memory.chat( "What was the output of the mystery function on 5 and 6 again? Don't recompute." )
```
Added user message to memory: What was the output of the mystery function on 5 and 6 again? Don't recompute.
=== LLM Response ===
The output of the mystery function on 5 and 6 is -11.

```

In [ ]:
Copied!
```
response = agent_with_memory.chat(
    "What was the output of the multiply function on 2 and 3 again? Don't recompute."
)

```

response = agent_with_memory.chat( "What was the output of the multiply function on 2 and 3 again? Don't recompute." )
```
Added user message to memory: What was the output of the multiply function on 2 and 3 again? Don't recompute.
=== LLM Response ===
The output of the multiply function on 2 and 3 is 6.

```

In [ ]:
Copied!
```
agent_with_memory.chat_history

```

agent_with_memory.chat_history
Out[ ]:
```
[ChatMessage(role=<MessageRole.USER: 'user'>, content="What was the output of the mystery function on 5 and 6 again? Don't recompute.", additional_kwargs={}),
 ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content='The output of the mystery function on 5 and 6 is -11.', additional_kwargs={}),
 ChatMessage(role=<MessageRole.USER: 'user'>, content="What was the output of the multiply function on 2 and 3 again? Don't recompute.", additional_kwargs={}),
 ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content='The output of the multiply function on 2 and 3 is 6.', additional_kwargs={})]
```

### What happens under the hood with `.chat(user_input)`¶
Under the hood, `.chat(user_input)` call effectively will call the memory's `.get()` method with `user_input` as the argument. As we learned in the previous section, this will ultimately return a composition of the `primary` and all of the `secondary` memory sources. These composed messages are what is being passed to the LLM's chat API as the chat history.
In [ ]:
Copied!
```
composable_memory = SimpleComposableMemory.from_defaults(
    primary_memory=ChatMemoryBuffer.from_defaults(),
    secondary_memory_sources=[
        vector_memory.copy(
            deep=True
        )  # copy for illustrative purposes to explain what
        # happened under the hood from previous subsection
    ],
)
agent_with_memory = agent_worker.as_agent(memory=composable_memory)

```

composable_memory = SimpleComposableMemory.from_defaults( primary_memory=ChatMemoryBuffer.from_defaults(), secondary_memory_sources=[ vector_memory.copy( deep=True ) # copy for illustrative purposes to explain what # happened under the hood from previous subsection ], ) agent_with_memory = agent_worker.as_agent(memory=composable_memory)
In [ ]:
Copied!
```
agent_with_memory.memory.get(
    "What was the output of the mystery function on 5 and 6 again? Don't recompute."
)

```

agent_with_memory.memory.get( "What was the output of the mystery function on 5 and 6 again? Don't recompute." )
Out[ ]:
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content='You are a helpful assistant.\n\nBelow are a set of relevant dialogues retrieved from potentially several memory sources:\n\n=====Relevant messages from memory source 1=====\n\n\tUSER: What is the mystery function on 5 and 6?\n\tASSISTANT: None\n\tTOOL: -11\n\tASSISTANT: The mystery function on 5 and 6 returns -11.\n\n=====End of relevant messages from memory source 1======\n\nThis is the end of the retrieved message dialogues.', additional_kwargs={})]
```

In [ ]:
Copied!
```
print(
    agent_with_memory.memory.get(
        "What was the output of the mystery function on 5 and 6 again? Don't recompute."
    )[0]
)

```

print( agent_with_memory.memory.get( "What was the output of the mystery function on 5 and 6 again? Don't recompute." )[0] )
```
system: You are a helpful assistant.

Below are a set of relevant dialogues retrieved from potentially several memory sources:

=====Relevant messages from memory source 1=====

	USER: What is the mystery function on 5 and 6?
	ASSISTANT: None
	TOOL: -11
	ASSISTANT: The mystery function on 5 and 6 returns -11.

=====End of relevant messages from memory source 1======

This is the end of the retrieved message dialogues.

```

