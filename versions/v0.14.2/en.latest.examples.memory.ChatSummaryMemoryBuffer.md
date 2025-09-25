# Chat Summary Memory Buffer¶
In this demo, we use the new _ChatSummaryMemoryBuffer_ to limit the chat history to a certain token length, and iteratively summarize all messages that do not fit in the memory buffer. This can be useful if you want to limit costs and latency (assuming the summarization prompt uses and generates fewer tokens than including the entire history).
The original _ChatMemoryBuffer_ gives you the option to truncate the history after a certain number of tokens, which is useful to limit costs and latency, but also removes potentially relevant information from the chat history.
The newer _ChatSummaryMemoryBuffer_ aims to makes this a bit more flexible, so the user has more control over which chat_history is retained.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index

```

%pip install llama-index-llms-openai %pip install llama-index
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

```

import os os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
In [ ]:
Copied!
```
from llama_index.core.memory import ChatSummaryMemoryBuffer
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.llms.openai import OpenAI as OpenAiLlm
import tiktoken

```

from llama_index.core.memory import ChatSummaryMemoryBuffer from llama_index.core.llms import ChatMessage, MessageRole from llama_index.llms.openai import OpenAI as OpenAiLlm import tiktoken
First, we simulate some chat history that will not fit in the memory buffer in its entirety.
In [ ]:
Copied!
```
chat_history = [
    ChatMessage(role="user", content="What is LlamaIndex?"),
    ChatMessage(
        role="assistant",
        content="LlamaaIndex is the leading data framework for building LLM applications",
    ),
    ChatMessage(role="user", content="Can you give me some more details?"),
    ChatMessage(
        role="assistant",
        content="""LlamaIndex is a framework for building context-augmented LLM applications. Context augmentation refers to any use case that applies LLMs on top of your private or domain-specific data. Some popular use cases include the following: 
        Question-Answering Chatbots (commonly referred to as RAG systems, which stands for "Retrieval-Augmented Generation"), Document Understanding and Extraction, Autonomous Agents that can perform research and take actions
        LlamaIndex provides the tools to build any of these above use cases from prototype to production. The tools allow you to both ingest/process this data and implement complex query workflows combining data access with LLM prompting.""",
    ),
]

```

chat_history = [ ChatMessage(role="user", content="What is LlamaIndex?"), ChatMessage( role="assistant", content="LlamaaIndex is the leading data framework for building LLM applications", ), ChatMessage(role="user", content="Can you give me some more details?"), ChatMessage( role="assistant", content="""LlamaIndex is a framework for building context-augmented LLM applications. Context augmentation refers to any use case that applies LLMs on top of your private or domain-specific data. Some popular use cases include the following: Question-Answering Chatbots (commonly referred to as RAG systems, which stands for "Retrieval-Augmented Generation"), Document Understanding and Extraction, Autonomous Agents that can perform research and take actions LlamaIndex provides the tools to build any of these above use cases from prototype to production. The tools allow you to both ingest/process this data and implement complex query workflows combining data access with LLM prompting.""", ), ]
By supplying an _llm_ and _token_limit_ for summarization, we create a _ChatSummaryMemoryBuffer_ instance.
In [ ]:
Copied!
```
model = "gpt-4-0125-preview"
summarizer_llm = OpenAiLlm(model_name=model, max_tokens=256)
tokenizer_fn = tiktoken.encoding_for_model(model).encode
memory = ChatSummaryMemoryBuffer.from_defaults(
    chat_history=chat_history,
    llm=summarizer_llm,
    token_limit=2,
    tokenizer_fn=tokenizer_fn,
)

history = memory.get()

```

model = "gpt-4-0125-preview" summarizer_llm = OpenAiLlm(model_name=model, max_tokens=256) tokenizer_fn = tiktoken.encoding_for_model(model).encode memory = ChatSummaryMemoryBuffer.from_defaults( chat_history=chat_history, llm=summarizer_llm, token_limit=2, tokenizer_fn=tokenizer_fn, ) history = memory.get()
When printing the history, we can observe that older messages have been summarized.
In [ ]:
Copied!
```
print(history)

```

print(history)
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content='The user inquired about LlamaIndex, a leading data framework for developing LLM applications. The assistant explained that LlamaIndex is used for building context-augmented LLM applications, giving examples such as Question-Answering Chatbots, Document Understanding and Extraction, and Autonomous Agents. It was mentioned that LlamaIndex provides tools for ingesting and processing data, as well as implementing complex query workflows combining data access with LLM prompting.', additional_kwargs={})]

```

Let's add some new chat history.
In [ ]:
Copied!
```
new_chat_history = [
    ChatMessage(role="user", content="Why context augmentation?"),
    ChatMessage(
        role="assistant",
        content="LLMs offer a natural language interface between humans and data. Widely available models come pre-trained on huge amounts of publicly available data. However, they are not trained on your data, which may be private or specific to the problem you're trying to solve. It's behind APIs, in SQL databases, or trapped in PDFs and slide decks. LlamaIndex provides tooling to enable context augmentation. A popular example is Retrieval-Augmented Generation (RAG) which combines context with LLMs at inference time. Another is finetuning.",
    ),
    ChatMessage(role="user", content="Who is LlamaIndex for?"),
    ChatMessage(
        role="assistant",
        content="LlamaIndex provides tools for beginners, advanced users, and everyone in between. Our high-level API allows beginner users to use LlamaIndex to ingest and query their data in 5 lines of code. For more complex applications, our lower-level APIs allow advanced users to customize and extend any module—data connectors, indices, retrievers, query engines, reranking modules—to fit their needs.",
    ),
]
memory.put(new_chat_history[0])
memory.put(new_chat_history[1])
memory.put(new_chat_history[2])
memory.put(new_chat_history[3])
history = memory.get()

```

new_chat_history = [ ChatMessage(role="user", content="Why context augmentation?"), ChatMessage( role="assistant", content="LLMs offer a natural language interface between humans and data. Widely available models come pre-trained on huge amounts of publicly available data. However, they are not trained on your data, which may be private or specific to the problem you're trying to solve. It's behind APIs, in SQL databases, or trapped in PDFs and slide decks. LlamaIndex provides tooling to enable context augmentation. A popular example is Retrieval-Augmented Generation (RAG) which combines context with LLMs at inference time. Another is finetuning.", ), ChatMessage(role="user", content="Who is LlamaIndex for?"), ChatMessage( role="assistant", content="LlamaIndex provides tools for beginners, advanced users, and everyone in between. Our high-level API allows beginner users to use LlamaIndex to ingest and query their data in 5 lines of code. For more complex applications, our lower-level APIs allow advanced users to customize and extend any module—data connectors, indices, retrievers, query engines, reranking modules—to fit their needs.", ), ] memory.put(new_chat_history[0]) memory.put(new_chat_history[1]) memory.put(new_chat_history[2]) memory.put(new_chat_history[3]) history = memory.get()
The history will now be updated with a new summary, containing the latest information.
In [ ]:
Copied!
```
print(history)

```

print(history)
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content='The user asked about LlamaIndex and why context augmentation is important. The assistant explained that LlamaIndex is for building context-augmented LLM applications, which are necessary because LLMs are not trained on specific private or problem-specific data. LlamaIndex provides tools for beginners and advanced users to ingest and query data easily, as well as customize modules for more complex applications.', additional_kwargs={})]

```

Using a longer _token_limit_ allows the user to control the balance between retaining the full chat history and summarization.
In [ ]:
Copied!
```
memory = ChatSummaryMemoryBuffer.from_defaults(
    chat_history=chat_history + new_chat_history,
    llm=summarizer_llm,
    token_limit=256,
    tokenizer_fn=tokenizer_fn,
)
print(memory.get())

```

memory = ChatSummaryMemoryBuffer.from_defaults( chat_history=chat_history + new_chat_history, llm=summarizer_llm, token_limit=256, tokenizer_fn=tokenizer_fn, ) print(memory.get())
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content='The user inquired about LlamaIndex, and the assistant explained that it is a data framework for creating context-augmented LLM applications. These applications can include question-answering chatbots, document understanding and extraction, and autonomous agents for research and actions. LlamaIndex provides tools for building these applications from prototype to production, enabling data processing, complex query workflows, and LLM prompting.', additional_kwargs={}), ChatMessage(role=<MessageRole.USER: 'user'>, content='Why context augmentation?', additional_kwargs={}), ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content="LLMs offer a natural language interface between humans and data. Widely available models come pre-trained on huge amounts of publicly available data. However, they are not trained on your data, which may be private or specific to the problem you're trying to solve. It's behind APIs, in SQL databases, or trapped in PDFs and slide decks. LlamaIndex provides tooling to enable context augmentation. A popular example is Retrieval-Augmented Generation (RAG) which combines context with LLMs at inference time. Another is finetuning.", additional_kwargs={}), ChatMessage(role=<MessageRole.USER: 'user'>, content='Who is LlamaIndex for?', additional_kwargs={}), ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content='LlamaIndex provides tools for beginners, advanced users, and everyone in between. Our high-level API allows beginner users to use LlamaIndex to ingest and query their data in 5 lines of code. For more complex applications, our lower-level APIs allow advanced users to customize and extend any module—data connectors, indices, retrievers, query engines, reranking modules—to fit their needs.', additional_kwargs={})]

```

