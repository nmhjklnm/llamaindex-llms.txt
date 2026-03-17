![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Chat Engine - Context Mode¶
ContextChatEngine is a simple chat mode built on top of a retriever over your data.
For each chat interaction:
  * first retrieve text from the index using the user message
  * set the retrieved text as context in the system prompt
  * return an answer to the user message


This approach is simple, and works for questions directly related to the knowledge base and general interactions.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
## Get started in 5 lines of code¶
Load data and build index
In [ ]:
Copied!
```
import openai
import os

os.environ["OPENAI_API_KEY"] = "API_KEY_HERE"
openai.api_key = os.environ["OPENAI_API_KEY"]

```

import openai import os os.environ["OPENAI_API_KEY"] = "API_KEY_HERE" openai.api_key = os.environ["OPENAI_API_KEY"]
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data()
index = VectorStoreIndex.from_documents(data)

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data() index = VectorStoreIndex.from_documents(data)
Configure chat engine
Since the context retrieved can take up a large amount of the available LLM context, let's ensure we configure a smaller limit to the chat history!
In [ ]:
Copied!
```
from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=1500)

chat_engine = index.as_chat_engine(
    chat_mode="context",
    memory=memory,
    system_prompt=(
        "You are a chatbot, able to have normal interactions, as well as talk"
        " about an essay discussing Paul Grahams life."
    ),
)

```

from llama_index.core.memory import ChatMemoryBuffer memory = ChatMemoryBuffer.from_defaults(token_limit=1500) chat_engine = index.as_chat_engine( chat_mode="context", memory=memory, system_prompt=( "You are a chatbot, able to have normal interactions, as well as talk" " about an essay discussing Paul Grahams life." ), )
Chat with your data
In [ ]:
Copied!
```
response = chat_engine.chat("Hello!")

```

response = chat_engine.chat("Hello!")
In [ ]:
Copied!
```
print(response)

```

print(response)
```
Hello! How can I assist you today?

```

Ask a follow up question
In [ ]:
Copied!
```
response = chat_engine.chat("What did Paul Graham do growing up?")

```

response = chat_engine.chat("What did Paul Graham do growing up?")
In [ ]:
Copied!
```
print(response)

```

print(response)
```
Growing up, Paul Graham had a keen interest in writing and programming. He spent a lot of time writing short stories, although he admits that they weren't particularly good. In terms of programming, he started working with computers in 9th grade when he had access to an IBM 1401 computer at his school. He learned an early version of Fortran and experimented with writing programs on punch cards. However, he found it challenging to figure out what to do with the computer since he didn't have much data to work with. It wasn't until microcomputers became available that he truly delved into programming, starting with a kit-built microcomputer called the Heathkit. Eventually, he convinced his father to buy a TRS-80, which allowed him to write simple games, create a word processor, and explore programming further.

```

In [ ]:
Copied!
```
response = chat_engine.chat("Can you tell me more?")

```

response = chat_engine.chat("Can you tell me more?")
In [ ]:
Copied!
```
print(response)

```

print(response)
```
Certainly! As Paul Graham continued to explore programming, he became fascinated with the possibilities it offered. He enjoyed the process of creating something out of nothing and the logical thinking required in programming. During his high school years, he also developed an interest in painting and considered pursuing it as a career.

After high school, Paul Graham attended Cornell University, where he studied philosophy. However, he found himself spending more time programming than studying philosophy. He even started a company called Viaweb with some friends, which aimed to create an online store builder. Viaweb eventually became successful and was acquired by Yahoo in 1998.

After the acquisition, Paul Graham moved to California and became a millionaire. However, he soon realized that he was burnt out from the stress of running Viaweb. He decided to leave Yahoo and pursue his passion for painting. He enrolled in the Accademia di Belle Arti in Florence, Italy, to study painting.

During his time in Florence, Paul Graham immersed himself in the world of art and painting. He experimented with different techniques and styles, particularly focusing on still life paintings. He found joy in closely observing everyday objects and capturing their details on canvas.

After a year in Florence, Paul Graham returned to the United States and worked at a software company called Interleaf. Although he was not particularly enthusiastic about the job, it provided him with a steady income and allowed him to save money to pursue his dream of attending the Rhode Island School of Design (RISD) to further his studies in painting.

Overall, Paul Graham's journey from programming to painting reflects his curiosity and willingness to explore different passions. He has found success in both fields and continues to share his insights and experiences through his writings and lectures.

```

Reset conversation state
In [ ]:
Copied!
```
chat_engine.reset()

```

chat_engine.reset()
In [ ]:
Copied!
```
response = chat_engine.chat("Hello! What do you know?")

```

response = chat_engine.chat("Hello! What do you know?")
In [ ]:
Copied!
```
print(response)

```

print(response)
```
Hi there! I know a lot about Paul Graham's life. He is an entrepreneur, programmer, and investor who is best known for co-founding the venture capital firm Y Combinator. He is also the author of several essays on technology and startups, including the influential essay "Hackers and Painters". He has had a long and successful career in the tech industry, and his experiences have shaped his views on entrepreneurship and technology.

```

## Streaming Support¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data()

index = VectorStoreIndex.from_documents(data)

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo", temperature=0) data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data() index = VectorStoreIndex.from_documents(data)
In [ ]:
Copied!
```
chat_engine = index.as_chat_engine(chat_mode="context", llm=llm)

```

chat_engine = index.as_chat_engine(chat_mode="context", llm=llm)
In [ ]:
Copied!
```
response = chat_engine.stream_chat("What did Paul Graham do after YC?")
for token in response.response_gen:
    print(token, end="")

```

response = chat_engine.stream_chat("What did Paul Graham do after YC?") for token in response.response_gen: print(token, end="")
```
After stepping down from his role at Y Combinator (YC), Paul Graham focused on pursuing different interests. Initially, he decided to dedicate his time to painting and see how good he could become with focused practice. He spent most of 2014 painting, but eventually ran out of steam and stopped.

Following his break from painting, Graham returned to writing essays and also resumed working on Lisp, a programming language. He delved into the core of Lisp, which involves writing an interpreter in the language itself. Graham continued to write essays and work on Lisp in the years following his departure from YC.
```

