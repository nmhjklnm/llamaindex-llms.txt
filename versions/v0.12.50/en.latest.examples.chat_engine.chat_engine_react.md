![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Chat Engine - ReAct Agent Mode¶
ReAct is an agent based chat mode built on top of a query engine over your data.
For each chat interaction, the agent enter a ReAct loop:
  * first decide whether to use the query engine tool and come up with appropriate input
  * (optional) use the query engine tool and observe its output
  * decide whether to repeat or give final response


This approach is flexible, since it can flexibility choose between querying the knowledge base or not. However, the performance is also more dependent on the quality of the LLM. You might need to do more coercing to make sure it chooses to query the knowledge base at right times, instead of hallucinating an answer.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-anthropic
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-anthropic %pip install llama-index-llms-openai
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
### Get started in 5 lines of code¶
Load data and build index
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

llm = OpenAI()
data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data()
index = VectorStoreIndex.from_documents(data)

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.llms.openai import OpenAI from llama_index.llms.anthropic import Anthropic llm = OpenAI() data = SimpleDirectoryReader(input_dir="./data/paul_graham/").load_data() index = VectorStoreIndex.from_documents(data)
Configure chat engine
In [ ]:
Copied!
```
chat_engine = index.as_chat_engine(chat_mode="react", llm=llm, verbose=True)

```

chat_engine = index.as_chat_engine(chat_mode="react", llm=llm, verbose=True)
Chat with your data
In [ ]:
Copied!
```
response = chat_engine.chat(
    "Use the tool to answer what did Paul Graham do in the summer of 1995?"
)

```

response = chat_engine.chat( "Use the tool to answer what did Paul Graham do in the summer of 1995?" )
```
Thought: I need to use a tool to help me answer the question.
Action: query_engine_tool
Action Input: {'input': 'What did Paul Graham do in the summer of 1995?'}
Observation: 
In the summer of 1995, Paul Graham worked on building a web application for making web applications. He recruited Dan Giffin, who had worked for Viaweb, and two undergrads who wanted summer jobs, and they got to work trying to build what it's now clear is about twenty companies and several open source projects worth of software. The language for defining applications would of course be a dialect of Lisp.
Response: In the summer of 1995, Paul Graham worked on building a web application for making web applications. He recruited Dan Giffin, who had worked for Viaweb, and two undergrads who wanted summer jobs, and they got to work trying to build what it's now clear is about twenty companies and several open source projects worth of software. The language for defining applications would of course be a dialect of Lisp.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
In the summer of 1995, Paul Graham worked on building a web application for making web applications. He recruited Dan Giffin, who had worked for Viaweb, and two undergrads who wanted summer jobs, and they got to work trying to build what it's now clear is about twenty companies and several open source projects worth of software. The language for defining applications would of course be a dialect of Lisp.

```

### Customize LLM¶
Use Anthropic ("claude-2")
In [ ]:
Copied!
```
llm = Anthropic()

```

llm = Anthropic()
Configure chat engine
In [ ]:
Copied!
```
chat_engine = index.as_chat_engine(llm=llm, chat_mode="react", verbose=True)

```

chat_engine = index.as_chat_engine(llm=llm, chat_mode="react", verbose=True)
In [ ]:
Copied!
```
response = chat_engine.chat("what did Paul Graham do in the summer of 1995?")

```

response = chat_engine.chat("what did Paul Graham do in the summer of 1995?")
```
Thought: I need to use a tool to help me answer the question.
Action: query_engine_tool
Action Input: {'input': 'what did Paul Graham do in the summer of 1995?'}
Observation:  Based on the context, in the summer of 1995 Paul Graham:

- Painted a second still life using the same objects he had used for a previous still life painting.

- Looked for an apartment to buy in New York, trying to find a neighborhood similar to Cambridge, MA. 

- Realized there wasn't really a "Cambridge of New York" after visiting the actual Cambridge.

The passage does not mention what Paul Graham did in the summer of 1995 specifically. It talks about painting a second still life at some point and looking for an apartment in New York at some point, but it does not connect those events to the summer of 1995.
Response: The passage does not provide enough information to know specifically what Paul Graham did in the summer of 1995. It mentions some activities like painting and looking for an apartment in New York, but does not say these occurred specifically in the summer of 1995.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The passage does not provide enough information to know specifically what Paul Graham did in the summer of 1995. It mentions some activities like painting and looking for an apartment in New York, but does not say these occurred specifically in the summer of 1995.

```

In [ ]:
Copied!
```
response = chat_engine.chat("What did I ask you before?")

```

response = chat_engine.chat("What did I ask you before?")
```
Response:  You asked me "what did Paul Graham do in the summer of 1995?".

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
 You asked me "what did Paul Graham do in the summer of 1995?".

```

Reset chat engine
In [ ]:
Copied!
```
chat_engine.reset()

```

chat_engine.reset()
In [ ]:
Copied!
```
response = chat_engine.chat("What did I ask you before?")

```

response = chat_engine.chat("What did I ask you before?")
```
Response: I'm afraid I don't have any context about previous questions in our conversation. This seems to be the start of a new conversation between us.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
I'm afraid I don't have any context about previous questions in our conversation. This seems to be the start of a new conversation between us.

```

