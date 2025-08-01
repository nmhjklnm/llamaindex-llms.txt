# NVIDIA NIMs¶
The `llama-index-llms-nvidia` package contains LlamaIndex integrations building applications with models on NVIDIA NIM inference microservice. NIM supports models across domains like chat, embedding, and re-ranking models from the community as well as NVIDIA. These models are optimized by NVIDIA to deliver the best performance on NVIDIA accelerated infrastructure and deployed as a NIM, an easy-to-use, prebuilt containers that deploy anywhere using a single command on NVIDIA accelerated infrastructure.
NVIDIA hosted deployments of NIMs are available to test on the NVIDIA API catalog. After testing, NIMs can be exported from NVIDIA’s API catalog using the NVIDIA AI Enterprise license and run on-premises or in the cloud, giving enterprises ownership and full control of their IP and AI application.
NIMs are packaged as container images on a per model basis and are distributed as NGC container images through the NVIDIA NGC Catalog. At their core, NIMs provide easy, consistent, and familiar APIs for running inference on an AI model.
# NVIDIA's LLM connector¶
This example goes over how to use LlamaIndex to interact with and develop LLM-powered systems using the publicly-accessible AI Foundation endpoints.
With this connector, you'll be able to connect to and generate from compatible models available as hosted NVIDIA NIMs, such as:
  * Google's gemma-7b
  * Mistal AI's mistral-7b-instruct-v0.2
  * And more!


## Installation¶
In [ ]:
Copied!
```
%pip install --upgrade --quiet llama-index-llms-nvidia llama-index-embeddings-nvidia llama-index-readers-file

```

%pip install --upgrade --quiet llama-index-llms-nvidia llama-index-embeddings-nvidia llama-index-readers-file
## Setup¶
**To get started:**
  1. Create a free account with NVIDIA, which hosts NVIDIA AI Foundation models.
  2. Click on your model of choice.
  3. Under Input select the Python tab, and click `Get API Key`. Then click `Generate Key`.
  4. Copy and save the generated key as NVIDIA_API_KEY. From there, you should have access to the endpoints.


In [ ]:
Copied!
```
import getpass
import os

# del os.environ['NVIDIA_API_KEY']  ## delete key and reset
if os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
    print("Valid NVIDIA_API_KEY already in environment. Delete to reset")
else:
    nvapi_key = getpass.getpass("NVAPI Key (starts with nvapi-): ")
    assert nvapi_key.startswith(
        "nvapi-"
    ), f"{nvapi_key[:5]}... is not a valid key"
    os.environ["NVIDIA_API_KEY"] = nvapi_key

```

import getpass import os # del os.environ['NVIDIA_API_KEY'] ## delete key and reset if os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"): print("Valid NVIDIA_API_KEY already in environment. Delete to reset") else: nvapi_key = getpass.getpass("NVAPI Key (starts with nvapi-): ") assert nvapi_key.startswith( "nvapi-" ), f"{nvapi_key[:5]}... is not a valid key" os.environ["NVIDIA_API_KEY"] = nvapi_key
In [ ]:
Copied!
```
# llama-parse is async-first, running the async code in a notebook requires the use of nest_asyncio
import nest_asyncio

nest_asyncio.apply()

```

# llama-parse is async-first, running the async code in a notebook requires the use of nest_asyncio import nest_asyncio nest_asyncio.apply()
## Working with NVIDIA API Catalog¶
In [ ]:
Copied!
```
from llama_index.llms.nvidia import NVIDIA
from llama_index.core.llms import ChatMessage, MessageRole

llm = NVIDIA()

messages = [
    ChatMessage(
        role=MessageRole.SYSTEM, content=("You are a helpful assistant.")
    ),
    ChatMessage(
        role=MessageRole.USER,
        content=("What are the most popular house pets in North America?"),
    ),
]

llm.chat(messages)

```

from llama_index.llms.nvidia import NVIDIA from llama_index.core.llms import ChatMessage, MessageRole llm = NVIDIA() messages = [ ChatMessage( role=MessageRole.SYSTEM, content=("You are a helpful assistant.") ), ChatMessage( role=MessageRole.USER, content=("What are the most popular house pets in North America?"), ), ] llm.chat(messages)
## Working with NVIDIA NIMs¶
In addition to connecting to hosted NVIDIA NIMs, this connector can be used to connect to local microservice instances. This helps you take your applications local when necessary.
For instructions on how to setup local microservice instances, see https://developer.nvidia.com/blog/nvidia-nim-offers-optimized-inference-microservices-for-deploying-ai-models-at-scale/
In [ ]:
Copied!
```
from llama_index.llms.nvidia import NVIDIA

# connect to an chat NIM running at localhost:8080, spcecifying a specific model
llm = NVIDIA(
    base_url="http://localhost:8080/v1", model="meta/llama3-8b-instruct"
)

```

from llama_index.llms.nvidia import NVIDIA # connect to an chat NIM running at localhost:8080, spcecifying a specific model llm = NVIDIA( base_url="http://localhost:8080/v1", model="meta/llama3-8b-instruct" )
## Loading a specific model¶
Now we can load our `NVIDIA` LLM by passing in the model name, as found in the docs - located here
> NOTE: The default model is `meta/llama3-8b-instruct`.
In [ ]:
Copied!
```
# default model
llm = NVIDIA()
llm.model

```

# default model llm = NVIDIA() llm.model
We can observe which model our `llm` object is currently associated with the `.model` attribute.
In [ ]:
Copied!
```
llm = NVIDIA(model="mistralai/mistral-7b-instruct-v0.2")
llm.model

```

llm = NVIDIA(model="mistralai/mistral-7b-instruct-v0.2") llm.model
## Basic Functionality¶
Now we can explore the different ways you can use the connector within the LlamaIndex ecosystem!
Before we begin, lets set up a list of `ChatMessage` objects - which is the expected input for some of the methods.
We'll follow the same basic pattern for each example:
  1. We'll point our `NVIDIA` LLM to our desired model
  2. We'll examine how to use the endpoint to achieve the desired task!


### Complete: `.complete()`¶
We can use `.complete()`/`.acomplete()` (which takes a string) to prompt a response from the selected model.
Let's use our default model for this task.
In [ ]:
Copied!
```
completion_llm = NVIDIA()

```

completion_llm = NVIDIA()
We can verify this is the expected default by checking the `.model` attribute.
In [ ]:
Copied!
```
completion_llm.model

```

completion_llm.model
Let's call `.complete()` on our model with a string, in this case `"Hello!"`, and observe the response.
In [ ]:
Copied!
```
completion_llm.complete("Hello!")

```

completion_llm.complete("Hello!")
As is expected by LlamaIndex - we get a `CompletionResponse` in response.
#### Async Complete: `.acomplete()`¶
There is also an async implementation which can be leveraged in the same way!
In [ ]:
Copied!
```
await completion_llm.acomplete("Hello!")

```

await completion_llm.acomplete("Hello!")
#### Chat: `.chat()`¶
Now we can try the same thing using the `.chat()` method. This method expects a list of chat messages - so we'll use the one we created above.
We'll use the `mistralai/mixtral-8x7b-instruct-v0.1` model for the example.
In [ ]:
Copied!
```
chat_llm = NVIDIA(model="mistralai/mixtral-8x7b-instruct-v0.1")

```

chat_llm = NVIDIA(model="mistralai/mixtral-8x7b-instruct-v0.1")
All we need to do now is call `.chat()` on our list of `ChatMessages` and observe our response.
You'll also notice that we can pass in a few additional key-word arguments that can influence the generation - in this case, we've used the `seed` parameter to influence our generation and the `stop` parameter to indicate we want the model to stop generating once it reaches a certain token!
> NOTE: You can find information about what additional kwargs are supported by the model's endpoint by referencing the API documentation for the selected model. Mixtral's is located here as an example!
In [ ]:
Copied!
```
chat_llm.chat(messages, seed=4, stop=["cat", "cats", "Cat", "Cats"])

```

chat_llm.chat(messages, seed=4, stop=["cat", "cats", "Cat", "Cats"])
As expected, we receive a `ChatResponse` in response.
#### Async Chat: (`achat`)¶
We also have an async implementation of the `.chat()` method which can be called in the following way.
In [ ]:
Copied!
```
await chat_llm.achat(messages)

```

await chat_llm.achat(messages)
### Stream: `.stream_chat()`¶
We can also use the models found on `build.nvidia.com` for streaming use-cases!
Let's select another model and observe this behaviour. We'll use Google's `gemma-7b` model for this task.
In [ ]:
Copied!
```
stream_llm = NVIDIA(model="google/gemma-7b")

```

stream_llm = NVIDIA(model="google/gemma-7b")
Let's call our model with `.stream_chat()`, which again expects a list of `ChatMessage` objects, and capture the response.
In [ ]:
Copied!
```
streamed_response = stream_llm.stream_chat(messages)

```

streamed_response = stream_llm.stream_chat(messages)
In [ ]:
Copied!
```
streamed_response

```

streamed_response
As we can see, the response is a generator with the streamed response.
Let's take a look at the final response once the generation is complete.
In [ ]:
Copied!
```
last_element = None
for last_element in streamed_response:
    pass

print(last_element)

```

last_element = None for last_element in streamed_response: pass print(last_element)
#### Async Stream: `.astream_chat()`¶
We have the equivalent async method for streaming as well, which can be used in a similar way to the sync implementation.
In [ ]:
Copied!
```
streamed_response = await stream_llm.astream_chat(messages)

```

streamed_response = await stream_llm.astream_chat(messages)
In [ ]:
Copied!
```
streamed_response

```

streamed_response
In [ ]:
Copied!
```
last_element = None
async for last_element in streamed_response:
    pass

print(last_element)

```

last_element = None async for last_element in streamed_response: pass print(last_element)
## Streaming Query Engine Responses¶
Let's look at a slightly more involved example using a query engine!
We'll start by loading some data (we'll be using the Hitchhiker's Guide to the Galaxy).
### Loading Data¶
Let's first create a directory where our data can live.
In [ ]:
Copied!
```
!mkdir -p 'data/hhgttg'

```

!mkdir -p 'data/hhgttg'
We'll download our data from the above source.
In [ ]:
Copied!
```
!wget 'https://web.eecs.utk.edu/~hqi/deeplearning/project/hhgttg.txt' -O 'data/hhgttg/hhgttg.txt'

```

!wget 'https://web.eecs.utk.edu/~hqi/deeplearning/project/hhgttg.txt' -O 'data/hhgttg/hhgttg.txt'
We'll need to have an embedding model for this step! We'll use NVIDIA `NV-Embed-QA` model to achieve this, and save it in our `Settings`.
In [ ]:
Copied!
```
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.core import Settings

embedder = NVIDIAEmbedding(model="NV-Embed-QA", truncate="END")
Settings.embed_model = embedder

```

from llama_index.embeddings.nvidia import NVIDIAEmbedding from llama_index.core import Settings embedder = NVIDIAEmbedding(model="NV-Embed-QA", truncate="END") Settings.embed_model = embedder
Now we can load our document and create an index leveraging the above
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("data/hhgttg").load_data()
index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader documents = SimpleDirectoryReader("data/hhgttg").load_data() index = VectorStoreIndex.from_documents(documents)
Now we can create a simple query engine and set our `streaming` parameter to `True`.
In [ ]:
Copied!
```
streaming_qe = index.as_query_engine(streaming=True)

```

streaming_qe = index.as_query_engine(streaming=True)
Let's send a query to our query engine, and then stream the response.
In [ ]:
Copied!
```
streaming_response = streaming_qe.query(
    "What is the significance of the number 42?",
)

```

streaming_response = streaming_qe.query( "What is the significance of the number 42?", )
In [ ]:
Copied!
```
streaming_response.print_response_stream()

```

streaming_response.print_response_stream()
### Tool calling¶
Starting in v0.2.1, NVIDIA supports tool calling.
NVIDIA provides integration with the variety of models on build.nvidia.com as well as local NIMs. Not all these models are trained for tool calling. Be sure to select a model that does have tool calling for your experimention and applications.
You can get a list of models that are known to support tool calling with,
`NOTE:` For more examples refer : nvidia_agent.ipynb
In [ ]:
Copied!
```
tool_models = [
    model
    for model in NVIDIA().available_models
    if model.is_function_calling_model
]

```

tool_models = [ model for model in NVIDIA().available_models if model.is_function_calling_model ]
With a tool capable model,
In [ ]:
Copied!
```
from llama_index.core.tools import FunctionTool


def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


add_tool = FunctionTool.from_defaults(fn=add)

llm = NVIDIA("meta/llama-3.1-70b-instruct")
from llama_index.core.agent import FunctionAgent

agent_worker = FunctionAgent(
    tools=[multiply_tool, add_tool],
    llm=llm,
)

response = await agent.run("What is (121 * 3) + 42?")
print(str(response))

```

from llama_index.core.tools import FunctionTool def multiply(a: int, b: int) -> int: """Multiple two integers and returns the result integer""" return a * b multiply_tool = FunctionTool.from_defaults(fn=multiply) def add(a: int, b: int) -> int: """Add two integers and returns the result integer""" return a + b add_tool = FunctionTool.from_defaults(fn=add) llm = NVIDIA("meta/llama-3.1-70b-instruct") from llama_index.core.agent import FunctionAgent agent_worker = FunctionAgent( tools=[multiply_tool, add_tool], llm=llm, ) response = await agent.run("What is (121 * 3) + 42?") print(str(response))
