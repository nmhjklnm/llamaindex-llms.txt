# Memory in LlamaIndex¶
The `Memory` class in LlamaIndex is used to store and retrieve both short-term and long-term memory.
You can use it on its own and orchestrate within a custom workflow, or use it within an existing agent.
By default, short-term memory is represented as a FIFO queue of `ChatMessage` objects. Once the queue exceeds a certain size, the last X messages within a flush size are archived and optionally flushed to long-term memory blocks.
Long-term memory is represented as `Memory Block` objects. These objects receive the messages that are flushed from short-term memory, and optionally process them to extract information. Then when memory is retrieved, the short-term and long-term memories are merged together.
## Setup¶
This notebook will use `OpenAI` as an LLM/embedding model for various parts of the example.
For vector retrieval, we will rely on `Chroma` as a vector store.
In [ ]:
Copied!
```
%pip install llama-index-core llama-index-llms-openai llama-index-embeddings-openai llama-index-vector-stores-chroma

```

%pip install llama-index-core llama-index-llms-openai llama-index-embeddings-openai llama-index-vector-stores-chroma
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-proj-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-proj-..."
## Short-term Memory¶
Let's explore how to configure various components of short-term memory.
For visual purposes, we will set some low token limits to more easily observe the memory behavior.
In [ ]:
Copied!
```
from llama_index.core.memory import Memory

memory = Memory.from_defaults(
    session_id="my_session",
    token_limit=50,  # Normally you would set this to be closer to the LLM context window (i.e. 75,000, etc.)
    token_flush_size=10,
    chat_history_token_ratio=0.7,
)

```

from llama_index.core.memory import Memory memory = Memory.from_defaults( session_id="my_session", token_limit=50, # Normally you would set this to be closer to the LLM context window (i.e. 75,000, etc.) token_flush_size=10, chat_history_token_ratio=0.7, )
Let's review the configuration we used and what it means:
  * `session_id`: A unique identifier for the session. Used to mark chat messages in a SQL database as belonging to a specific session.
  * `token_limit`: The maximum number of tokens that can be stored in short-term + long-term memory.
  * `chat_history_token_ratio`: The ratio of tokens in the short-term chat history to the total token limit. Here this means that 50*0.7 = 35 tokens are allocated to short-term memory, and the rest is allocated to long-term memory.
  * `token_flush_size`: The number of tokens to flush to long-term memory when the token limit is exceeded. Note that we did not configure long-term memory, so these messages are merely archived in the database and removed from the short-term memory.


Using our memory, we can manually add some messages and observe how it works.
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

# Simulate a long conversation
for i in range(100):
    await memory.aput_messages(
        [
            ChatMessage(role="user", content="Hello, world!"),
            ChatMessage(role="assistant", content="Hello, world to you too!"),
            ChatMessage(role="user", content="What is the capital of France?"),
            ChatMessage(
                role="assistant", content="The capital of France is Paris."
            ),
        ]
    )

```

from llama_index.core.llms import ChatMessage # Simulate a long conversation for i in range(100): await memory.aput_messages( [ ChatMessage(role="user", content="Hello, world!"), ChatMessage(role="assistant", content="Hello, world to you too!"), ChatMessage(role="user", content="What is the capital of France?"), ChatMessage( role="assistant", content="The capital of France is Paris." ), ] )
Since our token limit is small, we will only see the last 4 messages in short-term memory (since this fits withint the 50*0.7 limit)
In [ ]:
Copied!
```
current_chat_history = await memory.aget()
for msg in current_chat_history:
    print(msg)

```

current_chat_history = await memory.aget() for msg in current_chat_history: print(msg)
```
user: Hello, world!
assistant: Hello, world to you too!
user: What is the capital of France?
assistant: The capital of France is Paris.

```

If we retrieva all messages, we will find all 400 messages.
In [ ]:
Copied!
```
all_messages = await memory.aget_all()
print(len(all_messages))

```

all_messages = await memory.aget_all() print(len(all_messages))


We can clear the memory at any time to start fresh.
In [ ]:
Copied!
```
await memory.areset()

```

await memory.areset()
In [ ]:
Copied!
```
all_messages = await memory.aget_all()
print(len(all_messages))

```

all_messages = await memory.aget_all() print(len(all_messages))


## Long-term Memory¶
Long-term memory is represented as `Memory Block` objects. These objects receive the messages that are flushed from short-term memory, and optionally process them to extract information. Then when memory is retrieved, the short-term and long-term memories are merged together.
LlamaIndex provides 3 prebuilt memory blocks:
  * `StaticMemoryBlock`: A memory block that stores a static piece of information.
  * `FactExtractionMemoryBlock`: A memory block that extracts facts from the chat history.
  * `VectorMemoryBlock`: A memory block that stores and retrieves batches of chat messages from a vector database.


Each block has a `priority` that is used when the long-term memory + short-term memory exceeds the token limit. Priority 0 means the block will always be kept in memory, priority 1 means the block will be temporarily disabled, and so on.
In [ ]:
Copied!
```
from llama_index.core.memory import (
    StaticMemoryBlock,
    FactExtractionMemoryBlock,
    VectorMemoryBlock,
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb

llm = OpenAI(model="gpt-4.1-mini")
embed_model = OpenAIEmbedding(model="text-embedding-3-small")

client = chromadb.EphemeralClient()
vector_store = ChromaVectorStore(
    chroma_collection=client.get_or_create_collection("test_collection")
)

blocks = [
    StaticMemoryBlock(
        name="core_info",
        static_content="My name is Logan, and I live in Saskatoon. I work at LlamaIndex.",
        priority=0,
    ),
    FactExtractionMemoryBlock(
        name="extracted_info",
        llm=llm,
        max_facts=50,
        priority=1,
    ),
    VectorMemoryBlock(
        name="vector_memory",
        # required: pass in a vector store like qdrant, chroma, weaviate, milvus, etc.
        vector_store=vector_store,
        priority=2,
        embed_model=embed_model,
        # The top-k message batches to retrieve
        # similarity_top_k=2,
        # optional: How many previous messages to include in the retrieval query
        # retrieval_context_window=5
        # optional: pass optional node-postprocessors for things like similarity threshold, etc.
        # node_postprocessors=[...],
    ),
]

```

from llama_index.core.memory import ( StaticMemoryBlock, FactExtractionMemoryBlock, VectorMemoryBlock, ) from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.vector_stores.chroma import ChromaVectorStore import chromadb llm = OpenAI(model="gpt-4.1-mini") embed_model = OpenAIEmbedding(model="text-embedding-3-small") client = chromadb.EphemeralClient() vector_store = ChromaVectorStore( chroma_collection=client.get_or_create_collection("test_collection") ) blocks = [ StaticMemoryBlock( name="core_info", static_content="My name is Logan, and I live in Saskatoon. I work at LlamaIndex.", priority=0, ), FactExtractionMemoryBlock( name="extracted_info", llm=llm, max_facts=50, priority=1, ), VectorMemoryBlock( name="vector_memory", # required: pass in a vector store like qdrant, chroma, weaviate, milvus, etc. vector_store=vector_store, priority=2, embed_model=embed_model, # The top-k message batches to retrieve # similarity_top_k=2, # optional: How many previous messages to include in the retrieval query # retrieval_context_window=5 # optional: pass optional node-postprocessors for things like similarity threshold, etc. # node_postprocessors=[...], ), ]
With our blocks created, we can pass them into the `Memory` class.
In [ ]:
Copied!
```
from llama_index.core.memory import Memory

memory = Memory.from_defaults(
    session_id="my_session",
    token_limit=30000,
    # Setting a extremely low ratio so that more tokens are flushed to long-term memory
    chat_history_token_ratio=0.02,
    token_flush_size=500,
    memory_blocks=blocks,
    # insert into the latest user message, can also be "system"
    insert_method="user",
)

```

from llama_index.core.memory import Memory memory = Memory.from_defaults( session_id="my_session", token_limit=30000, # Setting a extremely low ratio so that more tokens are flushed to long-term memory chat_history_token_ratio=0.02, token_flush_size=500, memory_blocks=blocks, # insert into the latest user message, can also be "system" insert_method="user", )
With this, we can simulate a conversation with an agent and inspect the long-term memory.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

agent = FunctionAgent(
    tools=[],
    llm=llm,
)

user_msgs = [
    "Hi! My name is Logan",
    "What is your opinion on minature shnauzers?",
    "Do they shed a lot?",
    "What breeds are comparable in size?",
    "What is your favorite breed?",
    "Would you recommend owning a dog?",
    "What should I buy to prepare for owning a dog?",
]

for user_msg in user_msgs:
    _ = await agent.run(user_msg=user_msg, memory=memory)

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.llms.openai import OpenAI agent = FunctionAgent( tools=[], llm=llm, ) user_msgs = [ "Hi! My name is Logan", "What is your opinion on minature shnauzers?", "Do they shed a lot?", "What breeds are comparable in size?", "What is your favorite breed?", "Would you recommend owning a dog?", "What should I buy to prepare for owning a dog?", ] for user_msg in user_msgs: _ = await agent.run(user_msg=user_msg, memory=memory)
Now, let's inspect the most recent user-message and see what the memory inserts into the user message.
Note that we pass in at least one chat message so that the vector memory actually runs retrieval.
In [ ]:
Copied!
```
chat_history = await memory.aget()

```

chat_history = await memory.aget()
In [ ]:
Copied!
```
print(len(chat_history))

```

print(len(chat_history))


Great, we can see that the current FIFO queue is only 2 messages (expected since we set the chat history token ratio to 0.02).
Now, let's inspect the long-term memory blocks that are inserted into the latest user message.
In [ ]:
Copied!
```
for block in chat_history[-2].blocks:
    print(block.text)

```

for block in chat_history[-2].blocks: print(block.text)
```
<memory>
<core_info>
My name is Logan, and I live in Saskatoon. I work at LlamaIndex.
</core_info>
<extracted_info>
<fact>User's name is Logan</fact>
<fact>User lives in Saskatoon</fact>
<fact>User works at LlamaIndex</fact>
<fact>User is interested in Miniature Schnauzers</fact>
</extracted_info>
<vector_memory>
<message role='user'>Hi! My name is Logan</message>
<message role='assistant'>Hi Logan! Nice to meet you. How can I assist you today?</message>
<message role='user'>What is your opinion on minature shnauzers?</message>
<message role='assistant'>Hi Logan! Miniature Schnauzers are wonderful dogs—they're known for being intelligent, friendly, and energetic. They often make great companions because they're loyal and good with families. Plus, their distinctive beard and eyebrows give them a charming, expressive look. Do you have one, or are you thinking about getting one?</message>
<message role='user'>Do they shed a lot?</message>
<message role='assistant'>Hi Logan! Miniature Schnauzers are actually known for being low shedders. They have a wiry double coat that doesn't shed much, which makes them a good choice for people who prefer a cleaner home or have mild allergies. However, their coat does require regular grooming and trimming to keep it looking its best. Since you’re in Saskatoon, the grooming routine might also help keep them comfortable through the changing seasons. Are you considering getting one as a pet?</message>
<message role='user'>What breeds are comparable in size?</message>
<message role='assistant'>Hi Logan! Miniature Schnauzers typically weigh between 11 to 20 pounds (5 to 9 kg) and stand about 12 to 14 inches (30 to 36 cm) tall at the shoulder. Breeds comparable in size include:

- **Cairn Terrier**  
- **West Highland White Terrier (Westie)**  
- **Scottish Terrier**  
- **Pomeranian** (though usually a bit smaller)  
- **Beagle** (on the smaller side of the breed)  
- **French Bulldog** (a bit stockier but similar in height)  

These breeds are similar in size and can have comparable energy levels and grooming needs, depending on the breed. If you’re thinking about a dog that fits well with your lifestyle in Saskatoon and your work at LlamaIndex, I’d be happy to help you explore options!</message>
<message role='user'>What is your favorite breed?</message>
<message role='assistant'>Hi Logan! I don't have personal preferences, but I really appreciate breeds like the Miniature Schnauzer because of their intelligence, friendly nature, and low-shedding coat. They seem like great companions, especially for someone living in a place with changing seasons like Saskatoon. Do you have a favorite breed, or one you’re particularly interested in?</message>
<message role='user'>Would you recommend owning a dog?</message>
<message role='assistant'>Hi Logan! Owning a dog can be a wonderful experience, offering companionship, exercise, and even stress relief. Since you live in Saskatoon, where the seasons can be quite distinct, a dog can be a great motivator to get outside and enjoy the fresh air year-round.

That said, it’s important to consider your lifestyle and work schedule at LlamaIndex. Dogs require time, attention, and care—regular walks, playtime, grooming, and vet visits. If you have the time and energy to commit, a dog can be a fantastic addition to your life. Breeds like Miniature Schnauzers, which are adaptable and relatively low-maintenance in terms of shedding, might be a good fit.

If you’re unsure, maybe start by volunteering at a local animal shelter or fostering a dog to see how it fits with your routine. Would you like tips on how to prepare for dog ownership or suggestions on breeds that suit your lifestyle?</message>
</vector_memory>
</memory>
What should I buy to prepare for owning a dog?

```

To use this memory outside an agent, and to highlight more of the usage, you might do something like the following:
In [ ]:
Copied!
```
new_user_msg = ChatMessage(
    role="user", content="What kind of dog was I asking about?"
)
await memory.aput(new_user_msg)

# Get the new chat history
new_chat_history = await memory.aget()
resp = await llm.achat(new_chat_history)
await memory.aput(resp.message)
print(resp.message.content)

```

new_user_msg = ChatMessage( role="user", content="What kind of dog was I asking about?" ) await memory.aput(new_user_msg) # Get the new chat history new_chat_history = await memory.aget() resp = await llm.achat(new_chat_history) await memory.aput(resp.message) print(resp.message.content)
```
You were asking about Miniature Schnauzers.

```

