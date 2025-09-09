![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Fireworks¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index llama-index-llms-fireworks

```

%pip install llama-index llama-index-llms-fireworks
## Basic Usage¶
In [ ]:
Copied!
```
from llama_index.llms.fireworks import Fireworks

llm = Fireworks(
    model="accounts/fireworks/models/firefunction-v1",
    # api_key="some key",  # uses FIREWORKS_API_KEY env var by default
)

```

from llama_index.llms.fireworks import Fireworks llm = Fireworks( model="accounts/fireworks/models/firefunction-v1", # api_key="some key", # uses FIREWORKS_API_KEY env var by default )
#### Call `complete` with a prompt¶
In [ ]:
Copied!
```
resp = llm.complete("Paul Graham is ")

```

resp = llm.complete("Paul Graham is ")
In [ ]:
Copied!
```
print(resp)

```

print(resp)
```
Graham is a well-known essayist, programmer, and startup entrepreneur. He is best known for co-founding the venture capital firm, Y Combinator, which has funded and supported numerous successful startups, including Dropbox, Airbnb, and Reddit. Prior to Y Combinator, Graham co-founded Viaweb, one of the first software-as-a-service (SaaS) companies, which was later acquired by Yahoo.

Graham is also known for his influential essays on startups, programming, and personal productivity, which he publishes on his website, www.paulgraham.com. His writing is widely read and respected in the tech and startup communities, and he has been credited with helping to shape the way many people think about startups and entrepreneurship.

In addition to his work in technology and venture capital, Graham has a strong interest in education and has written extensively about the need for reform in the American education system. He is a graduate of Cornell University and holds a Ph.D. in computer science from Harvard University.

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
assistant: Arr matey, ye be askin' for me name? Well, I be known as Captain Redbeard the Terrible! Me crew says I'm a right colorful character, with me flamboyant red beard and me love for all things bright and bold. So hoist the Jolly Roger and let's set sail for adventure, yarr!

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
a well-known essayist, programmer, and venture capitalist. He is best known for co-founding the startup incubator and venture capital firm, Y Combinator, which has funded and helped grow many successful tech companies including Dropbox, Airbnb, and Reddit. Graham is also known for his influential essays on startups, technology, and programming, which he publishes on his website. Prior to his work in venture capital, Graham was a successful programmer and entrepreneur, co-founding the company Viaweb (later acquired by Yahoo) which developed the first web-based application for building online stores.
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
Arr matey, ye be askin' for me name? Well, I be known as Captain Redbeard the Terrible! Me crew says I'm a bit of a character, always crackin' me jokes and singin' shanties. But don't let me fool ya, I be a fierce pirate, feared by all who sail the seven seas!
```

