![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Upstage¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-upstage llama-index

```

%pip install llama-index-llms-upstage llama-index
## Basic Usage¶
#### Call `complete` with a prompt¶
In [ ]:
Copied!
```
import os

os.environ["UPSTAGE_API_KEY"] = "YOUR_API_KEY"

```

import os os.environ["UPSTAGE_API_KEY"] = "YOUR_API_KEY"
In [ ]:
Copied!
```
from llama_index.llms.upstage import Upstage

llm = Upstage(
    model="solar-mini",
    # api_key="YOUR_API_KEY"  # uses UPSTAGE_API_KEY env var by default
)

resp = llm.complete("Paul Graham is ")

```

from llama_index.llms.upstage import Upstage llm = Upstage( model="solar-mini", # api_key="YOUR_API_KEY" # uses UPSTAGE_API_KEY env var by default ) resp = llm.complete("Paul Graham is ")
In [ ]:
Copied!
```
print(resp)

```

print(resp)
```
Paul Graham is a computer scientist, entrepreneur, and essayist. He is best known as the co-founder of the venture capital firm Y Combinator, which has funded and incubated many successful startups. He is also the author of several influential essays on entrepreneurship, startup culture, and technology.

```

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
```
assistant: I am Captain Redbeard, the fearless pirate!

```

## Streaming¶
Using `stream_complete` endpoint
In [ ]:
Copied!
```
resp = llm.stream_complete("Paul Graham is ")

```

resp = llm.stream_complete("Paul Graham is ")
In [ ]:
Copied!
```
for r in resp:
    print(r.delta, end="")

```

for r in resp: print(r.delta, end="")
```
Paul Graham is a computer scientist, entrepreneur, and essayist. He is best known for co-founding the startup accelerator Y Combinator, which has helped launch some of the most successful tech companies in the world, including Airbnb, Dropbox, and Stripe. He is also the author of several influential essays on startup culture and entrepreneurship, including "How to Start a Startup" and "Hackers & Painters."
```

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
```
I am Captain Redbeard, the fearless pirate!
```

## Function Calling¶
Upstage models have native support for function calling. This conveniently integrates with LlamaIndex tool abstractions, letting you plug in any arbitrary Python function to the LLM.
In [ ]:
Copied!
```
from pydantic import BaseModel
from llama_index.core.tools import FunctionTool


class Song(BaseModel):
    """A song with name and artist"""

    name: str
    artist: str


def generate_song(name: str, artist: str) -> Song:
    """Generates a song with provided name and artist."""
    return Song(name=name, artist=artist)


tool = FunctionTool.from_defaults(fn=generate_song)

```

from pydantic import BaseModel from llama_index.core.tools import FunctionTool class Song(BaseModel): """A song with name and artist""" name: str artist: str def generate_song(name: str, artist: str) -> Song: """Generates a song with provided name and artist.""" return Song(name=name, artist=artist) tool = FunctionTool.from_defaults(fn=generate_song)
In [ ]:
Copied!
```
from llama_index.llms.upstage import Upstage

llm = Upstage()
response = llm.predict_and_call([tool], "Generate a song")
print(str(response))

```

from llama_index.llms.upstage import Upstage llm = Upstage() response = llm.predict_and_call([tool], "Generate a song") print(str(response))
```
name='My Song' artist='John Doe'

```

We can also do multiple function calling.
In [ ]:
Copied!
```
llm = Upstage()
response = llm.predict_and_call(
    [tool],
    "Generate five songs from the Beatles",
    allow_parallel_tool_calls=True,
)
for s in response.sources:
    print(f"Name: {s.tool_name}, Input: {s.raw_input}, Output: {str(s)}")

```

llm = Upstage() response = llm.predict_and_call( [tool], "Generate five songs from the Beatles", allow_parallel_tool_calls=True, ) for s in response.sources: print(f"Name: {s.tool_name}, Input: {s.raw_input}, Output: {str(s)}")
```
Name: generate_song, Input: {'args': (), 'kwargs': {'name': 'Beatles', 'artist': 'Beatles'}}, Output: name='Beatles' artist='Beatles'

```

## Async¶
In [ ]:
Copied!
```
from llama_index.llms.upstage import Upstage

llm = Upstage()

```

from llama_index.llms.upstage import Upstage llm = Upstage()
In [ ]:
Copied!
```
resp = await llm.acomplete("Paul Graham is ")

```

resp = await llm.acomplete("Paul Graham is ")
In [ ]:
Copied!
```
print(resp)

```

print(resp)
```
Paul Graham is a computer scientist, entrepreneur, and essayist. He is best known as the co-founder of the startup accelerator Y Combinator, which has helped launch and fund many successful tech companies. He is also the author of several influential essays on startups, entrepreneurship, and technology, including "How to Start a Startup" and "Hackers & Painters."

```

In [ ]:
Copied!
```
resp = await llm.astream_complete("Paul Graham is ")

```

resp = await llm.astream_complete("Paul Graham is ")
In [ ]:
Copied!
```
async for delta in resp:
    print(delta.delta, end="")

```

async for delta in resp: print(delta.delta, end="")
```
Paul Graham is a computer scientist, entrepreneur, and essayist. He is best known as the co-founder of the startup accelerator Y Combinator, which has helped launch some of the most successful tech companies in the world, including Airbnb, Dropbox, and Stripe. Graham is also a prolific writer, and his essays on topics such as startup advice, artificial intelligence, and the future of work have been widely read and influential in the tech industry.
```

Async function calling is also supported.
In [ ]:
Copied!
```
llm = Upstage()
response = await llm.apredict_and_call([tool], "Generate a song")
print(str(response))

```

llm = Upstage() response = await llm.apredict_and_call([tool], "Generate a song") print(str(response))
```
name='My Song' artist='Me'

```

