# Oracle Cloud Infrastructure Generative AI¶
Oracle Cloud Infrastructure (OCI) Generative AI is a fully managed service that provides a set of state-of-the-art, customizable large language models (LLMs) that cover a wide range of use cases, and which is available through a single API. Using the OCI Generative AI service you can access ready-to-use pretrained models, or create and host your own fine-tuned custom models based on your own data on dedicated AI clusters. Detailed documentation of the service and API is available **here** and **here**.
This notebook explains how to use OCI's Genrative AI models with LlamaIndex.
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-oci-genai

```

%pip install llama-index-llms-oci-genai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
You will also need to install the OCI sdk
In [ ]:
Copied!
```
!pip install -U oci

```

!pip install -U oci
## Basic Usage¶
Using LLMs offered by OCI Generative AI with LlamaIndex only requires you to initialize the OCIGenAI interface with your OCI endpoint, model ID, OCID, and authentication method.
#### Call `complete` with a prompt¶
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI

llm = OCIGenAI(
    model="MY_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)

resp = llm.complete("Paul Graham is ")
print(resp)

```

from llama_index.llms.oci_genai import OCIGenAI llm = OCIGenAI( model="MY_MODEL", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", ) resp = llm.complete("Paul Graham is ") print(resp)
#### Call `chat` with a list of messages¶
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="Tell me a story"),
]

llm = OCIGenAI(
    model="MY_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)

resp = llm.chat(messages)
print(resp)

```

from llama_index.llms.oci_genai import OCIGenAI from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="Tell me a story"), ] llm = OCIGenAI( model="MY_MODEL", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", ) resp = llm.chat(messages) print(resp)
## Streaming¶
Using `stream_complete` endpoint
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI

llm = OCIGenAI(
    model="MY_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)

resp = llm.stream_complete("Paul Graham is ")
for r in resp:
    print(r.delta, end="")

```

from llama_index.llms.oci_genai import OCIGenAI llm = OCIGenAI( model="MY_MODEL", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", ) resp = llm.stream_complete("Paul Graham is ") for r in resp: print(r.delta, end="")
Using `stream_chat` endpoint
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="Tell me a story"),
]

llm = OCIGenAI(
    model="MY_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)

resp = llm.stream_chat(messages)
for r in resp:
    print(r.delta, end="")

```

from llama_index.llms.oci_genai import OCIGenAI from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="Tell me a story"), ] llm = OCIGenAI( model="MY_MODEL", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", ) resp = llm.stream_chat(messages) for r in resp: print(r.delta, end="")
## Async¶
Native async currently not supported. Async calls will revert to synchronous
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="Tell me a story"),
]

llm = OCIGenAI(
    model="MY_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)

resp = llm.achat(messages)
print(resp)

resp = llm.astream_chat(messages)
for r in resp:
    print(r.delta, end="")

```

from llama_index.llms.oci_genai import OCIGenAI from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="Tell me a story"), ] llm = OCIGenAI( model="MY_MODEL", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", ) resp = llm.achat(messages) print(resp) resp = llm.astream_chat(messages) for r in resp: print(r.delta, end="")
## Configure Model¶
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI

llm = OCIGenAI(
    model="cohere.command",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)

resp = llm.complete("Paul Graham is ")
print(resp)

```

from llama_index.llms.oci_genai import OCIGenAI llm = OCIGenAI( model="cohere.command", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", ) resp = llm.complete("Paul Graham is ") print(resp)
## Authentication¶
The authentication methods supported for LlamaIndex are equivalent to those used with other OCI services and follow the **standard SDK authentication** methods, specifically API Key, session token, instance principal, and resource principal.
API key is the default authentication method. The following example demonstrates how to use a different authentication method (session token)
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI

llm = OCIGenAI(
    model="MY_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
    auth_type="SECURITY_TOKEN",
    auth_profile="MY_PROFILE",  # replace with your profile name
    auth_file_location="MY_CONFIG_FILE_LOCATION",  # replace with file location where profile name configs present
)

resp = llm.complete("Paul Graham is ")
print(resp)

```

from llama_index.llms.oci_genai import OCIGenAI llm = OCIGenAI( model="MY_MODEL", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", auth_type="SECURITY_TOKEN", auth_profile="MY_PROFILE", # replace with your profile name auth_file_location="MY_CONFIG_FILE_LOCATION", # replace with file location where profile name configs present ) resp = llm.complete("Paul Graham is ") print(resp)
## Dedicated AI Cluster¶
To access models hosted in a dedicated AI cluster **create an endpoint** whose assigned OCID (currently prefixed by ‘ocid1.generativeaiendpoint.oc1.us-chicago-1’) is used as your model ID.
When accessing models hosted in a dedicated AI cluster you will need to initialize the OCIGenAI interface with two extra required params ("provider" and "context_size").
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI
from llama_index.core.llms import ChatMessage

llm = OCIGenAI(
    model="ocid1.generativeaiendpoint.oc1.us-chicago-1....",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="DEDICATED_COMPARTMENT_OCID",
    auth_profile="MY_PROFILE",  # replace with your profile name,
    auth_file_location="MY_CONFIG_FILE_LOCATION",  # replace with file location where profile name configs present
    provider="MODEL_PROVIDER",  # e.g., "cohere" or "meta"
    context_size="MODEL_CONTEXT_SIZE",  # e.g., 128000
)

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="Tell me a story"),
]

resp = llm.chat(messages)
print(resp)

```

from llama_index.llms.oci_genai import OCIGenAI from llama_index.core.llms import ChatMessage llm = OCIGenAI( model="ocid1.generativeaiendpoint.oc1.us-chicago-1....", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="DEDICATED_COMPARTMENT_OCID", auth_profile="MY_PROFILE", # replace with your profile name, auth_file_location="MY_CONFIG_FILE_LOCATION", # replace with file location where profile name configs present provider="MODEL_PROVIDER", # e.g., "cohere" or "meta" context_size="MODEL_CONTEXT_SIZE", # e.g., 128000 ) messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="Tell me a story"), ] resp = llm.chat(messages) print(resp)
## Basic tool calling in llamaindex¶
Only Cohere supports tool calling for now
In [ ]:
Copied!
```
from llama_index.llms.oci_genai import OCIGenAI
from llama_index.core.tools import FunctionTool

llm = OCIGenAI(
    model="MY_MODEL",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)


def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Addition function on two integers."""
    return a + b


add_tool = FunctionTool.from_defaults(fn=add)
multiply_tool = FunctionTool.from_defaults(fn=multiply)

response = llm.chat_with_tools(
    tools=[add_tool, multiply_tool],
    user_msg="What is 3 * 12? Also, what is 11 + 49?",
)

print(response)
tool_calls = response.message.additional_kwargs.get("tool_calls", [])
print(tool_calls)

```

from llama_index.llms.oci_genai import OCIGenAI from llama_index.core.tools import FunctionTool llm = OCIGenAI( model="MY_MODEL", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", ) def multiply(a: int, b: int) -> int: """Multiple two integers and returns the result integer""" return a * b def add(a: int, b: int) -> int: """Addition function on two integers.""" return a + b add_tool = FunctionTool.from_defaults(fn=add) multiply_tool = FunctionTool.from_defaults(fn=multiply) response = llm.chat_with_tools( tools=[add_tool, multiply_tool], user_msg="What is 3 * 12? Also, what is 11 + 49?", ) print(response) tool_calls = response.message.additional_kwargs.get("tool_calls", []) print(tool_calls)
