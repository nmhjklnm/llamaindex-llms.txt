![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# LangChain LLM¶
In [ ]:
Copied!
```
%pip install llama-index-llms-langchain

```

%pip install llama-index-llms-langchain
In [ ]:
Copied!
```
from langchain.llms import OpenAI

```

from langchain.llms import OpenAI
In [ ]:
Copied!
```
from llama_index.llms.langchain import LangChainLLM

```

from llama_index.llms.langchain import LangChainLLM
In [ ]:
Copied!
```
llm = LangChainLLM(llm=OpenAI())

```

llm = LangChainLLM(llm=OpenAI())
In [ ]:
Copied!
```
response_gen = llm.stream_complete("Hi this is")

```

response_gen = llm.stream_complete("Hi this is")
In [ ]:
Copied!
```
for delta in response_gen:
    print(delta.delta, end="")

```

for delta in response_gen: print(delta.delta, end="")
```
 a test

Hello! Welcome to the test. What would you like to learn about?
```

