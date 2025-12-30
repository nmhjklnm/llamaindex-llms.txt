# API Call Observability¶
Using the new `instrumentation` package, we can get direct observability into API calls made using LLMs and emebdding models.
In this notebook, we explore doing this in order to add observability to LLM and embedding calls.
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
## Defining an Event Handler¶
In [ ]:
Copied!
```
from llama_index.core.instrumentation.event_handlers import BaseEventHandler
from llama_index.core.instrumentation.events.llm import (
    LLMCompletionEndEvent,
    LLMChatEndEvent,
)
from llama_index.core.instrumentation.events.embedding import EmbeddingEndEvent


class ModelEventHandler(BaseEventHandler):
    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "ModelEventHandler"

    def handle(self, event) -> None:
        """Logic for handling event."""
        if isinstance(event, LLMCompletionEndEvent):
            print(f"LLM Prompt length: {len(event.prompt)}")
            print(f"LLM Completion: {str(event.response.text)}")
        elif isinstance(event, LLMChatEndEvent):
            messages_str = "\n".join([str(x) for x in event.messages])
            print(f"LLM Input Messages length: {len(messages_str)}")
            print(f"LLM Response: {str(event.response.message)}")
        elif isinstance(event, EmbeddingEndEvent):
            print(f"Embedding {len(event.chunks)} text chunks")

```

from llama_index.core.instrumentation.event_handlers import BaseEventHandler from llama_index.core.instrumentation.events.llm import ( LLMCompletionEndEvent, LLMChatEndEvent, ) from llama_index.core.instrumentation.events.embedding import EmbeddingEndEvent class ModelEventHandler(BaseEventHandler): @classmethod def class_name(cls) -> str: """Class name.""" return "ModelEventHandler" def handle(self, event) -> None: """Logic for handling event.""" if isinstance(event, LLMCompletionEndEvent): print(f"LLM Prompt length: {len(event.prompt)}") print(f"LLM Completion: {str(event.response.text)}") elif isinstance(event, LLMChatEndEvent): messages_str = "\n".join([str(x) for x in event.messages]) print(f"LLM Input Messages length: {len(messages_str)}") print(f"LLM Response: {str(event.response.message)}") elif isinstance(event, EmbeddingEndEvent): print(f"Embedding {len(event.chunks)} text chunks")
## Attaching the Event Handler¶
In [ ]:
Copied!
```
from llama_index.core.instrumentation import get_dispatcher

# root dispatcher
root_dispatcher = get_dispatcher()

# register event handler
root_dispatcher.add_event_handler(ModelEventHandler())

```

from llama_index.core.instrumentation import get_dispatcher # root dispatcher root_dispatcher = get_dispatcher() # register event handler root_dispatcher.add_event_handler(ModelEventHandler())
## Invoke the Handler!¶
In [ ]:
Copied!
```
from llama_index.core import Document, VectorStoreIndex

index = VectorStoreIndex.from_documents([Document.example()])

```

from llama_index.core import Document, VectorStoreIndex index = VectorStoreIndex.from_documents([Document.example()])
```
Embedding 1 text chunks

```

In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("Tell me about LLMs?")

```

query_engine = index.as_query_engine() response = query_engine.query("Tell me about LLMs?")
```
Embedding 1 text chunks
LLM Input Messages length: 1879
LLM Response: assistant: LlamaIndex is a "data framework" designed to assist in building LLM apps. It offers tools such as data connectors for various data sources, ways to structure data for easy use with LLMs, an advanced retrieval/query interface, and integrations with different application frameworks. It caters to both beginner and advanced users, providing a high-level API for simple data ingestion and querying, as well as lower-level APIs for customization and extension of modules to suit specific requirements.

```

In [ ]:
Copied!
```
query_engine = index.as_query_engine(streaming=True)
response = query_engine.query("Repeat only these two words: Hello world!")
for r in response.response_gen:
    ...

```

query_engine = index.as_query_engine(streaming=True) response = query_engine.query("Repeat only these two words: Hello world!") for r in response.response_gen: ...
```
Embedding 1 text chunks
LLM Input Messages length: 1890
LLM Response: assistant: 
LLM Input Messages length: 1890
LLM Response: assistant: Hello
LLM Input Messages length: 1890
LLM Response: assistant: Hello world
LLM Input Messages length: 1890
LLM Response: assistant: Hello world!
LLM Input Messages length: 1890
LLM Response: assistant: Hello world!

```

