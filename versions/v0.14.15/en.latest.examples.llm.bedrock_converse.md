![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Bedrock Converse¶
## Basic Usage¶
#### Call `complete` with a prompt¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-bedrock-converse

```

%pip install llama-index-llms-bedrock-converse
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.llms.bedrock_converse import BedrockConverse

profile_name = "Your aws profile name"
resp = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    profile_name=profile_name,
).complete("Paul Graham is ")

```

from llama_index.llms.bedrock_converse import BedrockConverse profile_name = "Your aws profile name" resp = BedrockConverse( model="anthropic.claude-3-haiku-20240307-v1:0", profile_name=profile_name, ).complete("Paul Graham is ")
In [ ]:
Copied!
```
print(resp)

```

print(resp)
#### Call `chat` with a list of messages¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage
from llama_index.llms.bedrock_converse import BedrockConverse

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="Tell me a story"),
]

resp = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    profile_name=profile_name,
).chat(messages)

```

from llama_index.core.llms import ChatMessage from llama_index.llms.bedrock_converse import BedrockConverse messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="Tell me a story"), ] resp = BedrockConverse( model="anthropic.claude-3-haiku-20240307-v1:0", profile_name=profile_name, ).chat(messages)
In [ ]:
Copied!
```
print(resp)

```

print(resp)
## Streaming¶
Using `stream_complete` endpoint
In [ ]:
Copied!
```
from llama_index.llms.bedrock_converse import BedrockConverse

llm = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    profile_name=profile_name,
)
resp = llm.stream_complete("Paul Graham is ")

```

from llama_index.llms.bedrock_converse import BedrockConverse llm = BedrockConverse( model="anthropic.claude-3-haiku-20240307-v1:0", profile_name=profile_name, ) resp = llm.stream_complete("Paul Graham is ")
In [ ]:
Copied!
```
for r in resp:
    print(r.delta, end="")

```

for r in resp: print(r.delta, end="")
Using `stream_chat` endpoint
In [ ]:
Copied!
```
from llama_index.llms.bedrock_converse import BedrockConverse

llm = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    profile_name=profile_name,
)
messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="Tell me a story"),
]
resp = llm.stream_chat(messages)

```

from llama_index.llms.bedrock_converse import BedrockConverse llm = BedrockConverse( model="anthropic.claude-3-haiku-20240307-v1:0", profile_name=profile_name, ) messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="Tell me a story"), ] resp = llm.stream_chat(messages)
In [ ]:
Copied!
```
for r in resp:
    print(r.delta, end="")

```

for r in resp: print(r.delta, end="")
## Configure Model¶
In [ ]:
Copied!
```
from llama_index.llms.bedrock_converse import BedrockConverse

llm = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    profile_name=profile_name,
)

```

from llama_index.llms.bedrock_converse import BedrockConverse llm = BedrockConverse( model="anthropic.claude-3-haiku-20240307-v1:0", profile_name=profile_name, )
In [ ]:
Copied!
```
resp = llm.complete("Paul Graham is ")

```

resp = llm.complete("Paul Graham is ")
In [ ]:
Copied!
```
print(resp)

```

print(resp)
## Connect to Bedrock with Access Keys¶
In [ ]:
Copied!
```
from llama_index.llms.bedrock_converse import BedrockConverse

llm = BedrockConverse(
    model="us.amazon.nova-lite-v1:0",
    aws_access_key_id="AWS Access Key ID to use",
    aws_secret_access_key="AWS Secret Access Key to use",
    aws_session_token="AWS Session Token to use",
    region_name="AWS Region to use, eg. us-east-1",
)

resp = llm.complete("Paul Graham is ")

```

from llama_index.llms.bedrock_converse import BedrockConverse llm = BedrockConverse( model="us.amazon.nova-lite-v1:0", aws_access_key_id="AWS Access Key ID to use", aws_secret_access_key="AWS Secret Access Key to use", aws_session_token="AWS Session Token to use", region_name="AWS Region to use, eg. us-east-1", ) resp = llm.complete("Paul Graham is ")
In [ ]:
Copied!
```
print(resp)

```

print(resp)
## Function Calling¶
Claude, Command and Mistral Large models supports native function calling through AWS Bedrock Converse. There's a seamless integration with LlamaIndex tools, through the `predict_and_call` function on the `llm`.
This allows the user to attach any tools and let the LLM decide which tools to call (if any).
If you wish to perform tool calling as part of an agentic loop, check out our agent guides instead.
**NOTE** : Not all models from AWS Bedrock support function calling and the Converse API. Check the available features of each LLM here.
In [ ]:
Copied!
```
from llama_index.llms.bedrock_converse import BedrockConverse
from llama_index.core.tools import FunctionTool


def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


def mystery(a: int, b: int) -> int:
    """Mystery function on two integers."""
    return a * b + a + b


mystery_tool = FunctionTool.from_defaults(fn=mystery)
multiply_tool = FunctionTool.from_defaults(fn=multiply)

llm = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    profile_name=profile_name,
)

```

from llama_index.llms.bedrock_converse import BedrockConverse from llama_index.core.tools import FunctionTool def multiply(a: int, b: int) -> int: """Multiple two integers and returns the result integer""" return a * b def mystery(a: int, b: int) -> int: """Mystery function on two integers.""" return a * b + a + b mystery_tool = FunctionTool.from_defaults(fn=mystery) multiply_tool = FunctionTool.from_defaults(fn=multiply) llm = BedrockConverse( model="anthropic.claude-3-haiku-20240307-v1:0", profile_name=profile_name, )
In [ ]:
Copied!
```
response = llm.predict_and_call(
    [mystery_tool, multiply_tool],
    user_msg="What happens if I run the mystery function on 5 and 7",
)

```

response = llm.predict_and_call( [mystery_tool, multiply_tool], user_msg="What happens if I run the mystery function on 5 and 7", )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
In [ ]:
Copied!
```
response = llm.predict_and_call(
    [mystery_tool, multiply_tool],
    user_msg=(
        """What happens if I run the mystery function on the following pairs of numbers? Generate a separate result for each row:
- 1 and 2
- 8 and 4
- 100 and 20

NOTE: you need to run the mystery function for all of the pairs above at the same time \
"""
    ),
    allow_parallel_tool_calls=True,
)

```

response = llm.predict_and_call( [mystery_tool, multiply_tool], user_msg=( """What happens if I run the mystery function on the following pairs of numbers? Generate a separate result for each row: - 1 and 2 - 8 and 4 - 100 and 20 NOTE: you need to run the mystery function for all of the pairs above at the same time \ """ ), allow_parallel_tool_calls=True, )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
In [ ]:
Copied!
```
for s in response.sources:
    print(f"Name: {s.tool_name}, Input: {s.raw_input}, Output: {str(s)}")

```

for s in response.sources: print(f"Name: {s.tool_name}, Input: {s.raw_input}, Output: {str(s)}")
## Async¶
In [ ]:
Copied!
```
from llama_index.llms.bedrock_converse import BedrockConverse

llm = BedrockConverse(
    model="anthropic.claude-3-haiku-20240307-v1:0",
    aws_access_key_id="AWS Access Key ID to use",
    aws_secret_access_key="AWS Secret Access Key to use",
    aws_session_token="AWS Session Token to use",
    region_name="AWS Region to use, eg. us-east-1",
)
resp = await llm.acomplete("Paul Graham is ")

```

from llama_index.llms.bedrock_converse import BedrockConverse llm = BedrockConverse( model="anthropic.claude-3-haiku-20240307-v1:0", aws_access_key_id="AWS Access Key ID to use", aws_secret_access_key="AWS Secret Access Key to use", aws_session_token="AWS Session Token to use", region_name="AWS Region to use, eg. us-east-1", ) resp = await llm.acomplete("Paul Graham is ")
In [ ]:
Copied!
```
print(resp)

```

print(resp)
