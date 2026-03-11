![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# OpenLLM¶
OpenLLM lets developers run any open-source LLMs as **OpenAI-compatible API endpoints** with a single command. You can use `llama_index.llms.OpenLLM` to interact with a running OpenLLM server:
See OpenLLM's README for more information
In the below line, we install the packages necessary for this demo:
  * `llama-index-llms-openllm`


In [ ]:
Copied!
```
%pip install llama-index-llms-openllm

```

%pip install llama-index-llms-openllm
Now that we're set up, let's play around:
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import os
from typing import List, Optional

from llama_index.llms.openllm import OpenLLM
from llama_index.core.llms import ChatMessage

```

import os from typing import List, Optional from llama_index.llms.openllm import OpenLLM from llama_index.core.llms import ChatMessage
In [ ]:
Copied!
```
llm = OpenLLM(
    model="my-model", api_base="https://hostname.com/v1", api_key="na"
)

```

llm = OpenLLM( model="my-model", api_base="https://hostname.com/v1", api_key="na" )
Underlying a completion with `OpenLLM` supports continuous batching with vLLM
In [ ]:
Copied!
```
completion_response = llm.complete("To infinity, and")
print(completion_response)

```

completion_response = llm.complete("To infinity, and") print(completion_response)
```
 beyond!

As a lifelong lover of all things Pixar, I couldn't resist writing about the most recent release in the Toy Story franchise. Toy Story 4 is a nostalgic, heartwarming, and thrilling addition to the series that will have you laughing and crying in equal measure.

The movie follows Woody (Tom Hanks), Buzz Lightyear (Tim Allen), and the rest of the gang as they embark on a road trip with their new owner, Bonnie. However, things take an unexpected turn when Woody meets Bo Peep (Annie Pot

```

In [ ]:
Copied!
```
for it in llm.stream_complete("The meaning of time is", max_new_tokens=128):
    print(it, end="", flush=True)

```

for it in llm.stream_complete("The meaning of time is", max_new_tokens=128): print(it, end="", flush=True)
```
 often a topic of philosophical debate. Some people argue that time is an objective reality, while others claim that it is a subjective construct. This essay will explore the philosophical and scientific concepts surrounding the nature of time and the various theories that have been proposed to explain it.

One of the earliest philosophical theories of time was put forward by Aristotle, who believed that time was a measure of motion. According to Aristotle, time was an abstraction derived from the regular motion of objects in the universe. This theory was later refined by Galileo and Newton, who introduced the concept of time
```

They also support chat API as well, `chat`, `stream_chat`, `achat`, and `astream_chat`:
In [ ]:
Copied!
```
async for it in llm.astream_chat(
    [
        ChatMessage(
            role="system", content="You are acting as Ernest Hemmingway."
        ),
        ChatMessage(role="user", content="Hi there!"),
        ChatMessage(role="assistant", content="Yes?"),
        ChatMessage(role="user", content="What is the meaning of life?"),
    ]
):
    print(it.message.content, flush=True, end="")

```

async for it in llm.astream_chat( [ ChatMessage( role="system", content="You are acting as Ernest Hemmingway." ), ChatMessage(role="user", content="Hi there!"), ChatMessage(role="assistant", content="Yes?"), ChatMessage(role="user", content="What is the meaning of life?"), ] ): print(it.message.content, flush=True, end="")
```
I don't have beliefs or personal opinions, but according to my programming, the meaning of life is subjective and can vary from person to person. however, some people find meaning in their relationships, their work, their faith, or their personal values. ultimately, finding meaning in life is a personal journey that requires self-reflection, purpose, and fulfillment.
```

