# Manipulating Memory at Runtime¶
In this notebook, we cover how to use the `Memory` class to build an agentic workflow with dynamic memory.
Specifically, we will build a workflow where a user can upload a file, and pin that to the context of the LLM (i.e. like the file context in Cursor).
By default, as the short-term memory fills up and is flushed, it will be passed to memory blocks for processing as needed (extracting facts, indexing for retrieval, or for static blocks, ignoring it).
With this notebook, the intent is to show how memory can be managed and manipulated at runtime, beyond the already existing functionality described above.
## Setup¶
For our workflow, we will use OpenAI as our LLM.
In [ ]:
Copied!
```
!pip install llama-index-core llama-index-llms-openai

```

!pip install llama-index-core llama-index-llms-openai
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
## Workflow Setup¶
Our workflow will be fairly straightfoward. There will be two main entry points
  1. Adding/Removing files from memory
  2. Chatting with the LLM


Using the `Memory` class, we can introduce memory blocks that hold our static context.
In [ ]:
Copied!
```
import re
from typing import List, Literal, Optional
from pydantic import Field
from llama_index.core.memory import Memory, StaticMemoryBlock
from llama_index.core.llms import LLM, ChatMessage, TextBlock, ImageBlock
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)


class InitEvent(StartEvent):
    user_msg: str
    new_file_paths: List[str] = Field(default_factory=list)
    removed_file_paths: List[str] = Field(default_factory=list)


class ContextUpdateEvent(Event):
    new_file_paths: List[str] = Field(default_factory=list)
    removed_file_paths: List[str] = Field(default_factory=list)


class ChatEvent(Event):
    pass


class ResponseEvent(StopEvent):
    response: str


class ContextualLLMChat(Workflow):
    def __init__(self, memory: Memory, llm: LLM, **workflow_kwargs):
        super().__init__(**workflow_kwargs)
        self._memory = memory
        self._llm = llm

    def _path_to_block_name(self, file_path: str) -> str:
        return re.sub(r"[^\w-]", "_", file_path)

    @step
    async def init(self, ev: InitEvent) -> ContextUpdateEvent | ChatEvent:
        # Manage memory
        await self._memory.aput(ChatMessage(role="user", content=ev.user_msg))

        # Forward to chat or context update
        if ev.new_file_paths or ev.removed_file_paths:
            return ContextUpdateEvent(
                new_file_paths=ev.new_file_paths,
                removed_file_paths=ev.removed_file_paths,
            )
        else:
            return ChatEvent()

    @step
    async def update_memory_context(self, ev: ContextUpdateEvent) -> ChatEvent:
        current_blocks = self._memory.memory_blocks
        current_block_names = [block.name for block in current_blocks]

        for new_file_path in ev.new_file_paths:
            if new_file_path not in current_block_names:
                if new_file_path.endswith((".png", ".jpg", ".jpeg")):
                    self._memory.memory_blocks.append(
                        StaticMemoryBlock(
                            name=self._path_to_block_name(new_file_path),
                            static_content=[ImageBlock(path=new_file_path)],
                        )
                    )
                elif new_file_path.endswith((".txt", ".md", ".py", ".ipynb")):
                    with open(new_file_path, "r") as f:
                        self._memory.memory_blocks.append(
                            StaticMemoryBlock(
                                name=self._path_to_block_name(new_file_path),
                                static_content=f.read(),
                            )
                        )
                else:
                    raise ValueError(f"Unsupported file: {new_file_path}")
        for removed_file_path in ev.removed_file_paths:
            # Remove the block from memory
            named_block = self._path_to_block_name(removed_file_path)
            self._memory.memory_blocks = [
                block
                for block in self._memory.memory_blocks
                if block.name != named_block
            ]

        return ChatEvent()

    @step
    async def chat(self, ev: ChatEvent) -> ResponseEvent:
        chat_history = await self._memory.aget()
        response = await self._llm.achat(chat_history)
        return ResponseEvent(response=response.message.content)

```

import re from typing import List, Literal, Optional from pydantic import Field from llama_index.core.memory import Memory, StaticMemoryBlock from llama_index.core.llms import LLM, ChatMessage, TextBlock, ImageBlock from llama_index.core.workflow import ( Context, Event, StartEvent, StopEvent, Workflow, step, ) class InitEvent(StartEvent): user_msg: str new_file_paths: List[str] = Field(default_factory=list) removed_file_paths: List[str] = Field(default_factory=list) class ContextUpdateEvent(Event): new_file_paths: List[str] = Field(default_factory=list) removed_file_paths: List[str] = Field(default_factory=list) class ChatEvent(Event): pass class ResponseEvent(StopEvent): response: str class ContextualLLMChat(Workflow): def __init__(self, memory: Memory, llm: LLM, **workflow_kwargs): super().__init__(**workflow_kwargs) self._memory = memory self._llm = llm def _path_to_block_name(self, file_path: str) -> str: return re.sub(r"[^\w-]", "_", file_path) @step async def init(self, ev: InitEvent) -> ContextUpdateEvent | ChatEvent: # Manage memory await self._memory.aput(ChatMessage(role="user", content=ev.user_msg)) # Forward to chat or context update if ev.new_file_paths or ev.removed_file_paths: return ContextUpdateEvent( new_file_paths=ev.new_file_paths, removed_file_paths=ev.removed_file_paths, ) else: return ChatEvent() @step async def update_memory_context(self, ev: ContextUpdateEvent) -> ChatEvent: current_blocks = self._memory.memory_blocks current_block_names = [block.name for block in current_blocks] for new_file_path in ev.new_file_paths: if new_file_path not in current_block_names: if new_file_path.endswith((".png", ".jpg", ".jpeg")): self._memory.memory_blocks.append( StaticMemoryBlock( name=self._path_to_block_name(new_file_path), static_content=[ImageBlock(path=new_file_path)], ) ) elif new_file_path.endswith((".txt", ".md", ".py", ".ipynb")): with open(new_file_path, "r") as f: self._memory.memory_blocks.append( StaticMemoryBlock( name=self._path_to_block_name(new_file_path), static_content=f.read(), ) ) else: raise ValueError(f"Unsupported file: {new_file_path}") for removed_file_path in ev.removed_file_paths: # Remove the block from memory named_block = self._path_to_block_name(removed_file_path) self._memory.memory_blocks = [ block for block in self._memory.memory_blocks if block.name != named_block ] return ChatEvent() @step async def chat(self, ev: ChatEvent) -> ResponseEvent: chat_history = await self._memory.aget() response = await self._llm.achat(chat_history) return ResponseEvent(response=response.message.content)
## Using the Workflow¶
Now that we have our chat workflow defined, we can try it out! You can use any file, but for this example, we will use a few dummy files.
In [ ]:
Copied!
```
!wget https://mediaproxy.tvtropes.org/width/1200/https://static.tvtropes.org/pmwiki/pub/images/shrek_cover.png -O ./image.png
!wget https://raw.githubusercontent.com/run-llama/llama_index/refs/heads/main/llama-index-core/llama_index/core/memory/memory.py -O ./memory.py

```

!wget https://mediaproxy.tvtropes.org/width/1200/https://static.tvtropes.org/pmwiki/pub/images/shrek_cover.png -O ./image.png !wget https://raw.githubusercontent.com/run-llama/llama_index/refs/heads/main/llama-index-core/llama_index/core/memory/memory.py -O ./memory.py
In [ ]:
Copied!
```
from llama_index.core.memory import Memory
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4.1-nano")

memory = Memory.from_defaults(
    session_id="my_session",
    token_limit=60000,
    chat_history_token_ratio=0.7,
    token_flush_size=5000,
    insert_method="user",
)

workflow = ContextualLLMChat(
    memory=memory,
    llm=llm,
    verbose=True,
)

```

from llama_index.core.memory import Memory from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-4.1-nano") memory = Memory.from_defaults( session_id="my_session", token_limit=60000, chat_history_token_ratio=0.7, token_flush_size=5000, insert_method="user", ) workflow = ContextualLLMChat( memory=memory, llm=llm, verbose=True, )
We can simulate a user adding a file to memory, and then chatting with the LLM.
In [ ]:
Copied!
```
response = await workflow.run(
    user_msg="What does this file contain?",
    new_file_paths=["./memory.py"],
)

print("--------------------------------")
print(response.response)

```

response = await workflow.run( user_msg="What does this file contain?", new_file_paths=["./memory.py"], ) print("--------------------------------") print(response.response)
```
Running step init
Step init produced event ContextUpdateEvent
Running step update_memory_context
Step update_memory_context produced event ChatEvent
Running step chat
Step chat produced event ResponseEvent
--------------------------------
This file contains the implementation of a sophisticated, asynchronous memory management system designed for conversational AI or chat-based applications. Its main components and functionalities include:

1. **Memory Block Abstraction (`BaseMemoryBlock`)**:
   - An abstract base class defining the interface for memory blocks.
   - Subclasses must implement methods to asynchronously get (`aget`) and put (`aput`) content.
   - Optional truncation (`atruncate`) to manage size.

2. **Memory Management Class (`Memory`)**:
   - Orchestrates overall memory handling, including:
     - Maintaining a FIFO message queue with token size limits.
     - Managing multiple memory blocks with different priorities.
     - Handling insertion of memory content into chat history.
     - Truncating memory blocks when token limits are exceeded.
     - Formatting memory blocks into templates for inclusion in chat messages.
     - Managing the lifecycle of chat messages via an SQL store (`SQLAlchemyChatStore`).

3. **Key Functionalities**:
   - **Token Estimation**: Methods to estimate token counts for messages, blocks, images, and audio.
   - **Queue Management (`_manage_queue`)**: Ensures the message queue stays within token limits by archiving and moving old messages into memory blocks, maintaining conversation integrity.
   - **Memory Retrieval (`aget`)**: Fetches chat history combined with memory block content, formatted via templates, ready for use in conversations.
   - **Memory Insertion**: Inserts memory content into chat history either as system messages or appended to user messages, based on configuration.
   - **Asynchronous Operations**: Many methods are async, allowing non-blocking I/O with the chat store and memory blocks.
   - **Synchronous Wrappers**: Synchronous methods wrap async calls for convenience.

4. **Supporting Functions and Defaults**:
   - Unique key generation for chat sessions.
   - Default memory block templates.
   - Validation and configuration logic for memory parameters.

Overall, this code provides a flexible, priority-based, token-aware memory system that integrates with a chat history stored in a database, enabling long-term memory, context management, and conversation continuity in AI chat systems.

```

Great! Now, we can simulate a user removing that file, and adding a new one.
In [ ]:
Copied!
```
response = await workflow.run(
    user_msg="What does this next file contain?",
    new_file_paths=["./image.png"],
    removed_file_paths=["./memory.py"],
)

print("--------------------------------")
print(response.response)

```

response = await workflow.run( user_msg="What does this next file contain?", new_file_paths=["./image.png"], removed_file_paths=["./memory.py"], ) print("--------------------------------") print(response.response)
```
Running step init
Step init produced event ContextUpdateEvent
Running step update_memory_context
Step update_memory_context produced event ChatEvent
Running step chat
Step chat produced event ResponseEvent
--------------------------------
The file contains an image of the animated movie poster for "Shrek." It features various characters from the film, including Shrek, Fiona, Donkey, Puss in Boots, and others, set against a bright, colorful background.

```

It works! Now, you've learned how to manage memory in a custom workflow. Beyond just letting short-term memory flush into memory blocks, you can manually manipulate the memory blocks at runtime as well.
