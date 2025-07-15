# LlamaHub Demostration¶
Here we give a simple overview of how to use data loaders and tools (for agents) within LlamaHub.
**NOTES** :
  * You can learn how to use everything in LlamaHub by clicking into each module and looking at the code snippet.
  * Also, you can find a full list of agent tools here.
  * In this guide we'll show how to use `download_loader` and `download_tool`. You can also install `llama-hub` as a package.


## Using a Data Loader¶
In this example we show how to use `SimpleWebPageReader`.
**NOTE** : for any module on LlamaHub, to use with `download_` functions, note down the class name.
In [ ]:
Copied!
```
%pip install llama-index-agent-openai
%pip install llama-index-readers-web
%pip install llama-index-tools-google

```

%pip install llama-index-agent-openai %pip install llama-index-readers-web %pip install llama-index-tools-google
In [ ]:
Copied!
```
from llama_index.readers.web import SimpleWebPageReader

```

from llama_index.readers.web import SimpleWebPageReader
In [ ]:
Copied!
```
reader = SimpleWebPageReader(html_to_text=True)

```

reader = SimpleWebPageReader(html_to_text=True)
In [ ]:
Copied!
```
docs = reader.load_data(urls=["https://eugeneyan.com/writing/llm-patterns/"])

```

docs = reader.load_data(urls=["https://eugeneyan.com/writing/llm-patterns/"])
In [ ]:
Copied!
```
print(docs[0].get_content()[:400])

```

print(docs[0].get_content()[:400])
```
# [eugeneyan](/)

  * [Start Here](/start-here/ "Start Here")
  * [Writing](/writing/ "Writing")
  * [Speaking](/speaking/ "Speaking")
  * [Prototyping](/prototyping/ "Prototyping")
  * [About](/about/ "About")

# Patterns for Building LLM-based Systems & Products

[ [llm](/tag/llm/) [engineering](/tag/engineering/)
[production](/tag/production/) ]  · 66 min read

> Discussions on [HackerNews](htt

```

Now you can plug these docs into your downstream LlamaIndex pipeline.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(docs)
query_engine = index.as_query_engine()

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(docs) query_engine = index.as_query_engine()
In [ ]:
Copied!
```
response = query_engine.query("What are ways to evaluate LLMs?")
print(str(response))

```

response = query_engine.query("What are ways to evaluate LLMs?") print(str(response))
## Using an Agent Tool Spec¶
In this example we show how to load an agent tool.
In [ ]:
Copied!
```
from llama_index.tools.google import GmailToolSpec

```

from llama_index.tools.google import GmailToolSpec
In [ ]:
Copied!
```
tool_spec = GmailToolSpec()

```

tool_spec = GmailToolSpec()
In [ ]:
Copied!
```
# plug into your agent
from llama_index.agent.openai import OpenAIAgent

```

# plug into your agent from llama_index.agent.openai import OpenAIAgent
In [ ]:
Copied!
```
agent = OpenAIAgent.from_tools(tool_spec.to_tool_list())

```

agent = OpenAIAgent.from_tools(tool_spec.to_tool_list())
In [ ]:
Copied!
```
agent.chat("What is my most recent email")

```

agent.chat("What is my most recent email")
