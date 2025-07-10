![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Retrieval-Augmented Agents¶
In this tutorial, we show you how to use our `FunctionAgent` or `ReActAgent` implementation with a tool retriever, to augment any existing agent and store/index an arbitrary number of tools.
Our indexing/retrieval modules help to remove the complexity of having too many functions to fit in the prompt.
## Initial Setup¶
Let's start by importing some simple building blocks.
The main thing we need is:
  1. the OpenAI API
  2. a place to keep conversation history
  3. a definition for tools that our agent can use.


If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
Let's define some very simple calculator tools for our agent.
In [ ]:
Copied!
```
from llama_index.core.tools import FunctionTool


def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


def useless(a: int, b: int) -> int:
    """Toy useless function."""
    pass


multiply_tool = FunctionTool.from_defaults(multiply, name="multiply")
add_tool = FunctionTool.from_defaults(add, name="add")

# toy-example of many tools
useless_tools = [
    FunctionTool.from_defaults(useless, name=f"useless_{str(idx)}")
    for idx in range(28)
]

all_tools = [multiply_tool] + [add_tool] + useless_tools

all_tools_map = {t.metadata.name: t for t in all_tools}

```

from llama_index.core.tools import FunctionTool def multiply(a: int, b: int) -> int: """Multiply two integers and returns the result integer""" return a * b def add(a: int, b: int) -> int: """Add two integers and returns the result integer""" return a + b def useless(a: int, b: int) -> int: """Toy useless function.""" pass multiply_tool = FunctionTool.from_defaults(multiply, name="multiply") add_tool = FunctionTool.from_defaults(add, name="add") # toy-example of many tools useless_tools = [ FunctionTool.from_defaults(useless, name=f"useless_{str(idx)}") for idx in range(28) ] all_tools = [multiply_tool] + [add_tool] + useless_tools all_tools_map = {t.metadata.name: t for t in all_tools}
## Building an Object Index¶
We have an `ObjectIndex` construct in LlamaIndex that allows the user to use our index data structures over arbitrary objects. The ObjectIndex will handle serialiation to/from the object, and use an underying index (e.g. VectorStoreIndex, SummaryIndex, KeywordTableIndex) as the storage mechanism.
In this case, we have a large collection of Tool objects, and we'd want to define an ObjectIndex over these Tools.
The index comes bundled with a retrieval mechanism, an `ObjectRetriever`.
This can be passed in to our agent so that it can perform Tool retrieval during query-time.
In [ ]:
Copied!
```
# define an "object" index over these tools
from llama_index.core import VectorStoreIndex
from llama_index.core.objects import ObjectIndex

obj_index = ObjectIndex.from_objects(
    all_tools,
    index_cls=VectorStoreIndex,
    # if we were using an external vector store, we could pass the stroage context and any other kwargs
    # storage_context=storage_context,
    # embed_model=embed_model,
    # ...
)

```

# define an "object" index over these tools from llama_index.core import VectorStoreIndex from llama_index.core.objects import ObjectIndex obj_index = ObjectIndex.from_objects( all_tools, index_cls=VectorStoreIndex, # if we were using an external vector store, we could pass the stroage context and any other kwargs # storage_context=storage_context, # embed_model=embed_model, # ... )
To reload the index later, we can use the `from_objects_and_index` method.
In [ ]:
Copied!
```
# from llama_index.core import StorageContext, load_index_from_storage

# saving and loading from disk
# obj_index.index.storage_context.persist(persist_dir="obj_index_storage")

# reloading from disk
# vector_index = load_index_from_storage(StorageContext.from_defaults(persist_dir="obj_index_storage"))

# or if using an external vector store, no need to persist, just reload the index
# vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store, ...)

# Then, we can reload the ObjectIndex
# obj_index = ObjectIndex.from_objects_and_index(
#     all_tools,
#     index=vector_index,
# )

```

# from llama_index.core import StorageContext, load_index_from_storage # saving and loading from disk # obj_index.index.storage_context.persist(persist_dir="obj_index_storage") # reloading from disk # vector_index = load_index_from_storage(StorageContext.from_defaults(persist_dir="obj_index_storage")) # or if using an external vector store, no need to persist, just reload the index # vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store, ...) # Then, we can reload the ObjectIndex # obj_index = ObjectIndex.from_objects_and_index( # all_tools, # index=vector_index, # )
## Agent w/ Tool Retrieval¶
Agents in LlamaIndex can be used with a `ToolRetriever` to retrieve tools during query-time.
During query-time, we would first use the `ObjectRetriever` to retrieve a set of relevant Tools. These tools would then be passed into the agent; more specifically, their function signatures would be passed into the OpenAI Function calling API.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

agent = FunctionAgent(
    tool_retriever=obj_index.as_retriever(similarity_top_k=2),
    llm=OpenAI(model="gpt-4o"),
)

# context to hold the session/state
ctx = Context(agent)

```

from llama_index.core.agent.workflow import FunctionAgent, ReActAgent from llama_index.core.workflow import Context from llama_index.llms.openai import OpenAI agent = FunctionAgent( tool_retriever=obj_index.as_retriever(similarity_top_k=2), llm=OpenAI(model="gpt-4o"), ) # context to hold the session/state ctx = Context(agent)
In [ ]:
Copied!
```
resp = await agent.run(
    "What's 212 multiplied by 122? Make sure to use Tools", ctx=ctx
)
print(str(resp))
print(resp.tool_calls)

```

resp = await agent.run( "What's 212 multiplied by 122? Make sure to use Tools", ctx=ctx ) print(str(resp)) print(resp.tool_calls)
```
The result of multiplying 212 by 122 is 25,864.
[ToolCallResult(tool_name='multiply', tool_kwargs={'a': 212, 'b': 122}, tool_id='call_4Ygos3MpRH7Gj3R79HISRGyH', tool_output=ToolOutput(content='25864', tool_name='multiply', raw_input={'args': (), 'kwargs': {'a': 212, 'b': 122}}, raw_output=25864, is_error=False), return_direct=False)]

```

In [ ]:
Copied!
```
resp = await agent.run(
    "What's 212 added to 122 ? Make sure to use Tools", ctx=ctx
)
print(str(resp))
print(resp.tool_calls)

```

resp = await agent.run( "What's 212 added to 122 ? Make sure to use Tools", ctx=ctx ) print(str(resp)) print(resp.tool_calls)
```
The result of adding 212 to 122 is 334.
[ToolCallResult(tool_name='add', tool_kwargs={'a': 212, 'b': 122}, tool_id='call_rXUfwQ477bcd6bxafQHgETaa', tool_output=ToolOutput(content='334', tool_name='add', raw_input={'args': (), 'kwargs': {'a': 212, 'b': 122}}, raw_output=334, is_error=False), return_direct=False)]

```

