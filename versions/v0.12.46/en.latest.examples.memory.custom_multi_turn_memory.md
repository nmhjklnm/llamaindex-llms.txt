# Reducing Multi-Turn Confusion with LlamaIndex Memory¶
Recent research has shown the performance of an LLM significantly degrades given multi-turn conversations.
To help avoid this, we can implement a custom short-term and long-term memory in LlamaIndex to ensure that the conversation turns never get too long, and condense the memory as we go.
Using the code from this notebook, you may see improvements in your own agents as it works to limit how many turns are in your chat history.
**NOTE:** This notebook was tested with `llama-index-core>=0.12.37`, as that version included some fixes to make this work nicely.
In [ ]:
Copied!
```
%pip install -U llama-index-core llama-index-llms-openai

```

%pip install -U llama-index-core llama-index-llms-openai
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
## Setup¶
To make this work, we need two things
  1. A memory block that condenses a;; past chat messages into a single string while maintaining a token limit
  2. A `Memory` instance that uses that memory block, and has token limits configured such that multi-turn conversations are always flushed to the memory block for handling


First, the custom memory block:
In [ ]:
Copied!
```
import tiktoken
from pydantic import Field
from typing import List, Optional, Any
from llama_index.core.llms import ChatMessage, TextBlock
from llama_index.core.memory import Memory, BaseMemoryBlock


class CondensedMemoryBlock(BaseMemoryBlock[str]):
    current_memory: List[str] = Field(default_factory=list)
    token_limit: int = Field(default=50000)
    tokenizer: tiktoken.Encoding = tiktoken.encoding_for_model(
        "gpt-4o"
    )  # all openai models use 4o tokenizer these days

    async def _aget(
        self, messages: Optional[List[ChatMessage]] = None, **block_kwargs: Any
    ) -> str:
        """Return the current memory block contents."""
        return "\n".join(self.current_memory)

    async def _aput(self, messages: List[ChatMessage]) -> None:
        """Push messages into the memory block. (Only handles text content)"""
        # construct a string for each message
        for message in messages:
            text_contents = "\n".join(
                block.text
                for block in message.blocks
                if isinstance(block, TextBlock)
            )
            memory_str = f"<message role={message.role}>"

            if text_contents:
                memory_str += f"\n{text_contents}"

            # include additional kwargs, like tool calls, when needed
            # filter out injected session_id
            kwargs = {
                key: val
                for key, val in message.additional_kwargs.items()
                if key != "session_id"
            }
            if kwargs:
                memory_str += f"\n({kwargs})"

            memory_str += "\n</message>"
            self.current_memory.append(memory_str)

        # ensure this memory block doesn't get too large
        message_length = sum(
            len(self.tokenizer.encode(message))
            for message in self.current_memory
        )
        while message_length > self.token_limit:
            self.current_memory = self.current_memory[1:]
            message_length = sum(
                len(self.tokenizer.encode(message))
                for message in self.current_memory
            )

```

import tiktoken from pydantic import Field from typing import List, Optional, Any from llama_index.core.llms import ChatMessage, TextBlock from llama_index.core.memory import Memory, BaseMemoryBlock class CondensedMemoryBlock(BaseMemoryBlock[str]): current_memory: List[str] = Field(default_factory=list) token_limit: int = Field(default=50000) tokenizer: tiktoken.Encoding = tiktoken.encoding_for_model( "gpt-4o" ) # all openai models use 4o tokenizer these days async def _aget( self, messages: Optional[List[ChatMessage]] = None, **block_kwargs: Any ) -> str: """Return the current memory block contents.""" return "\n".join(self.current_memory) async def _aput(self, messages: List[ChatMessage]) -> None: """Push messages into the memory block. (Only handles text content)""" # construct a string for each message for message in messages: text_contents = "\n".join( block.text for block in message.blocks if isinstance(block, TextBlock) ) memory_str = f"" if text_contents: memory_str += f"\n{text_contents}" # include additional kwargs, like tool calls, when needed # filter out injected session_id kwargs = { key: val for key, val in message.additional_kwargs.items() if key != "session_id" } if kwargs: memory_str += f"\n({kwargs})" memory_str += "\n" self.current_memory.append(memory_str) # ensure this memory block doesn't get too large message_length = sum( len(self.tokenizer.encode(message)) for message in self.current_memory ) while message_length > self.token_limit: self.current_memory = self.current_memory[1:] message_length = sum( len(self.tokenizer.encode(message)) for message in self.current_memory )
And then, a `Memory` instance that uses that block while configuring a very limited token limit for the short-term memory:
In [ ]:
Copied!
```
block = CondensedMemoryBlock(name="condensed_memory")

memory = Memory.from_defaults(
    session_id="test-mem-01",
    token_limit=60000,
    token_flush_size=5000,
    async_database_uri="sqlite+aiosqlite:///:memory:",
    memory_blocks=[block],
    insert_method="user",
    # Prevent the short-term chat history from containing too many turns!
    # This limit will effectively mean that the short-term memory is always flushed
    chat_history_token_ratio=0.0001,
)

```

block = CondensedMemoryBlock(name="condensed_memory") memory = Memory.from_defaults( session_id="test-mem-01", token_limit=60000, token_flush_size=5000, async_database_uri="sqlite+aiosqlite:///:memory:", memory_blocks=[block], insert_method="user", # Prevent the short-term chat history from containing too many turns! # This limit will effectively mean that the short-term memory is always flushed chat_history_token_ratio=0.0001, )
## Usage¶
Let's explore using this with some dummy messages, and observe how the memory is managed.
In [ ]:
Copied!
```
initial_messages = [
    ChatMessage(role="user", content="Hello! My name is Logan"),
    ChatMessage(role="assistant", content="Hello! How can I help you?"),
    ChatMessage(role="user", content="What is the capital of France?"),
    ChatMessage(role="assistant", content="The capital of France is Paris"),
]

```

initial_messages = [ ChatMessage(role="user", content="Hello! My name is Logan"), ChatMessage(role="assistant", content="Hello! How can I help you?"), ChatMessage(role="user", content="What is the capital of France?"), ChatMessage(role="assistant", content="The capital of France is Paris"), ]
In [ ]:
Copied!
```
await memory.aput_messages(initial_messages)

```

await memory.aput_messages(initial_messages)
Then, lets add our next user message!
In [ ]:
Copied!
```
await memory.aput_messages(
    [ChatMessage(role="user", content="What was my name again?")]
)

```

await memory.aput_messages( [ChatMessage(role="user", content="What was my name again?")] )
With that, we can explore what the chat history looks like before sending to an LLM.
In [ ]:
Copied!
```
chat_history = await memory.aget()

for message in chat_history:
    print(message.role)
    print(message.content)
    print()

```

chat_history = await memory.aget() for message in chat_history: print(message.role) print(message.content) print()
```
MessageRole.USER
<memory>
<condensed_memory>
<message role=MessageRole.USER>
Hello! My name is Logan
</message>
<message role=MessageRole.ASSISTANT>
Hello! How can I help you?
</message>
<message role=MessageRole.USER>
What is the capital of France?
</message>
<message role=MessageRole.ASSISTANT>
The capital of France is Paris
</message>
</condensed_memory>
</memory>
What was my name again?


```

Great! Even though we added many messages, it gets condensed into a single user message!
Let's try with an actual agent next.
## Agent Usage¶
Here, we can create a `FunctionAgent` with some simple tools that uses our memory.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI


def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    return a / b


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b


llm = OpenAI(model="gpt-4.1-mini")

agent = FunctionAgent(
    tools=[multiply, divide, add, subtract],
    llm=llm,
    system_prompt="You are a helpful assistant that can do simple math operations with tools.",
)

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.llms.openai import OpenAI def multiply(a: float, b: float) -> float: """Multiply two numbers.""" return a * b def divide(a: float, b: float) -> float: """Divide two numbers.""" return a / b def add(a: float, b: float) -> float: """Add two numbers.""" return a + b def subtract(a: float, b: float) -> float: """Subtract two numbers.""" return a - b llm = OpenAI(model="gpt-4.1-mini") agent = FunctionAgent( tools=[multiply, divide, add, subtract], llm=llm, system_prompt="You are a helpful assistant that can do simple math operations with tools.", )
In [ ]:
Copied!
```
block = CondensedMemoryBlock(name="condensed_memory")

memory = Memory.from_defaults(
    session_id="test-mem-01",
    token_limit=60000,
    token_flush_size=5000,
    async_database_uri="sqlite+aiosqlite:///:memory:",
    memory_blocks=[block],
    insert_method="user",
    # Prevent the short-term chat history from containing too many turns!
    # This limit will effectively mean that the short-term memory is always flushed
    chat_history_token_ratio=0.0001,
)

```

block = CondensedMemoryBlock(name="condensed_memory") memory = Memory.from_defaults( session_id="test-mem-01", token_limit=60000, token_flush_size=5000, async_database_uri="sqlite+aiosqlite:///:memory:", memory_blocks=[block], insert_method="user", # Prevent the short-term chat history from containing too many turns! # This limit will effectively mean that the short-term memory is always flushed chat_history_token_ratio=0.0001, )
In [ ]:
Copied!
```
resp = await agent.run("What is (3214 * 322) / 2?", memory=memory)
print(resp)

```

resp = await agent.run("What is (3214 * 322) / 2?", memory=memory) print(resp)
```
The value of (3214 * 322) / 2 is 517454.0.

```

In [ ]:
Copied!
```
current_chat_history = await memory.aget()
for message in current_chat_history:
    print(message.role)
    print(message.content)
    print()

```

current_chat_history = await memory.aget() for message in current_chat_history: print(message.role) print(message.content) print()
```
MessageRole.ASSISTANT
The value of (3214 * 322) / 2 is 517454.0.

MessageRole.USER
<memory>
<condensed_memory>
<message role=MessageRole.USER>
What is (3214 * 322) / 2?
</message>
<message role=MessageRole.ASSISTANT>
({'tool_calls': [{'index': 0, 'id': 'call_U78I0CSWETFQlRBCWPpswEmq', 'function': {'arguments': '{"a": 3214, "b": 322}', 'name': 'multiply'}, 'type': 'function'}, {'index': 1, 'id': 'call_3eFXqalMN9PyiCVEYE073bEl', 'function': {'arguments': '{"a": 3214, "b": 2}', 'name': 'divide'}, 'type': 'function'}]})
</message>
<message role=MessageRole.TOOL>
1034908
({'tool_call_id': 'call_U78I0CSWETFQlRBCWPpswEmq'})
</message>
<message role=MessageRole.TOOL>
1607.0
({'tool_call_id': 'call_3eFXqalMN9PyiCVEYE073bEl'})
</message>
<message role=MessageRole.ASSISTANT>
({'tool_calls': [{'index': 0, 'id': 'call_GvtLKm7FCzlaucfYnaxOLBVW', 'function': {'arguments': '{"a":1034908,"b":2}', 'name': 'divide'}, 'type': 'function'}]})
</message>
<message role=MessageRole.TOOL>
517454.0
({'tool_call_id': 'call_GvtLKm7FCzlaucfYnaxOLBVW'})
</message>
</condensed_memory>
</memory>


```

Perfect! Since the memory didn't have a new user message yet, it added one with our current memory. On the next user message, that memory and the user message would get combined like we saw earlier.
Let's try a few follow ups to confirm this is working properly
In [ ]:
Copied!
```
resp = await agent.run(
    "What was the last question I asked you?", memory=memory
)
print(resp)

```

resp = await agent.run( "What was the last question I asked you?", memory=memory ) print(resp)
```
The last question you asked was: "What is (3214 * 322) / 2?"

```

In [ ]:
Copied!
```
resp = await agent.run(
    "And how did you go about answering that message?", memory=memory
)
print(resp)

```

resp = await agent.run( "And how did you go about answering that message?", memory=memory ) print(resp)
```
To answer your question "What is (3214 * 322) / 2?", I followed these steps:

1. First, I multiplied 3214 by 322.
2. Then, I divided the result of that multiplication by 2.
3. Finally, I provided you with the result of the calculation, which is 517454.0.

```

