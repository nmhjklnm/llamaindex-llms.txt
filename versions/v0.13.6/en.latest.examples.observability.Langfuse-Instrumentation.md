![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Cookbook LlamaIndex Integration (Instrumentation Module)¶
This is a simple cookbook that demonstrates how to use the LlamaIndex Langfuse integration using the instrumentation module by LlamaIndex (available in llama-index v0.10.20 and later).
## Setup¶
Make sure you have both `llama-index` and `langfuse` installed.
In [ ]:
Copied!
```
%pip install langfuse llama_index --upgrade

```

%pip install langfuse llama_index --upgrade
Initialize the integration. Get your API keys from the Langfuse project settings. This example uses OpenAI for embeddings and chat completions. You can also use any other model supported by LlamaIndex.
In [ ]:
Copied!
```
import os

# Get keys for your project from the project settings page: https://cloud.langfuse.com
os.environ["LANGFUSE_PUBLIC_KEY"] = ""
os.environ["LANGFUSE_SECRET_KEY"] = ""
os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com"  # 🇪🇺 EU region
# os.environ["LANGFUSE_HOST"] = "https://us.cloud.langfuse.com" # 🇺🇸 US region

# Your openai key
os.environ["OPENAI_API_KEY"] = ""

```

import os # Get keys for your project from the project settings page: https://cloud.langfuse.com os.environ["LANGFUSE_PUBLIC_KEY"] = "" os.environ["LANGFUSE_SECRET_KEY"] = "" os.environ["LANGFUSE_HOST"] = "https://cloud.langfuse.com" # 🇪🇺 EU region # os.environ["LANGFUSE_HOST"] = "https://us.cloud.langfuse.com" # 🇺🇸 US region # Your openai key os.environ["OPENAI_API_KEY"] = ""
Register the Langfuse `LlamaIndexInstrumentor`:
In [ ]:
Copied!
```
from langfuse.llama_index import LlamaIndexInstrumentor

instrumentor = LlamaIndexInstrumentor()
instrumentor.start()

```

from langfuse.llama_index import LlamaIndexInstrumentor instrumentor = LlamaIndexInstrumentor() instrumentor.start()
## Index¶
In [ ]:
Copied!
```
# Example context, thx ChatGPT
from llama_index.core import Document

doc1 = Document(
    text="""
Maxwell "Max" Silverstein, a lauded movie director, screenwriter, and producer, was born on October 25, 1978, in Boston, Massachusetts. A film enthusiast from a young age, his journey began with home movies shot on a Super 8 camera. His passion led him to the University of Southern California (USC), majoring in Film Production. Eventually, he started his career as an assistant director at Paramount Pictures. Silverstein's directorial debut, “Doors Unseen,” a psychological thriller, earned him recognition at the Sundance Film Festival and marked the beginning of a successful directing career.
"""
)
doc2 = Document(
    text="""
Throughout his career, Silverstein has been celebrated for his diverse range of filmography and unique narrative technique. He masterfully blends suspense, human emotion, and subtle humor in his storylines. Among his notable works are "Fleeting Echoes," "Halcyon Dusk," and the Academy Award-winning sci-fi epic, "Event Horizon's Brink." His contribution to cinema revolves around examining human nature, the complexity of relationships, and probing reality and perception. Off-camera, he is a dedicated philanthropist living in Los Angeles with his wife and two children.
"""
)

```

# Example context, thx ChatGPT from llama_index.core import Document doc1 = Document( text=""" Maxwell "Max" Silverstein, a lauded movie director, screenwriter, and producer, was born on October 25, 1978, in Boston, Massachusetts. A film enthusiast from a young age, his journey began with home movies shot on a Super 8 camera. His passion led him to the University of Southern California (USC), majoring in Film Production. Eventually, he started his career as an assistant director at Paramount Pictures. Silverstein's directorial debut, “Doors Unseen,” a psychological thriller, earned him recognition at the Sundance Film Festival and marked the beginning of a successful directing career. """ ) doc2 = Document( text=""" Throughout his career, Silverstein has been celebrated for his diverse range of filmography and unique narrative technique. He masterfully blends suspense, human emotion, and subtle humor in his storylines. Among his notable works are "Fleeting Echoes," "Halcyon Dusk," and the Academy Award-winning sci-fi epic, "Event Horizon's Brink." His contribution to cinema revolves around examining human nature, the complexity of relationships, and probing reality and perception. Off-camera, he is a dedicated philanthropist living in Los Angeles with his wife and two children. """ )
In [ ]:
Copied!
```
# Example index construction + LLM query
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents([doc1, doc2])

```

# Example index construction + LLM query from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents([doc1, doc2])
## Query¶
In [ ]:
Copied!
```
# Query
response = index.as_query_engine().query("What did he do growing up?")
print(response)

```

# Query response = index.as_query_engine().query("What did he do growing up?") print(response)
```
He made home movies using a Super 8 camera.

```

Example trace: https://cloud.langfuse.com/project/cloramnkj0002jz088vzn1ja4/traces/d933c7cc-20bf-4db3-810d-bab1c8d9a2a1
In [ ]:
Copied!
```
# Chat
response = index.as_chat_engine().chat("What did he do growing up?")
print(response)

```

# Chat response = index.as_chat_engine().chat("What did he do growing up?") print(response)
```
He made home movies using a Super 8 camera growing up.

```

Example trace: https://cloud.langfuse.com/project/cloramnkj0002jz088vzn1ja4/traces/4e285b8f-9789-4cf0-a8b4-45473ac420f1
![LlamaIndex Chat Engine Trace in Langfuse \(via instrumentation module\)](https://langfuse.com/images/cookbook/integration_llama-index_instrumentation_chatengine_trace.png)
## Custom trace properties¶
You can use the `instrumentor.observe` context manager to manage trace IDs, set custom trace properties, and access the trace client for later scoring.
In [ ]:
Copied!
```
with instrumentor.observe(user_id="my-user", session_id="my-session") as trace:
    response = index.as_query_engine().query("What did he do growing up?")

# Use the trace client yielded by the context manager for e.g. scoring:
trace.score(name="my-score", value=0.5)

```

with instrumentor.observe(user_id="my-user", session_id="my-session") as trace: response = index.as_query_engine().query("What did he do growing up?") # Use the trace client yielded by the context manager for e.g. scoring: trace.score(name="my-score", value=0.5)
Example trace: https://cloud.langfuse.com/project/cloramnkj0002jz088vzn1ja4/traces/6f554d6b-a2bc-4fba-904f-aa54de2897ca
