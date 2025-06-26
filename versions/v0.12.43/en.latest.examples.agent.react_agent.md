![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# ReAct Agent - A Simple Intro with Calculator Tools¶
This is a notebook that showcases the ReAct agent over very simple calculator tools (no fancy RAG pipelines or API calls).
We show how it can reason step-by-step over different tools to achieve the end goal.
The main advantage of the ReAct agent over a Function Calling agent is that it can work with any LLM regardless of whether it supports function calling.
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
## Define Function Tools¶
We setup some trivial `multiply` and `add` tools. Note that you can define arbitrary functions and pass it to the `FunctionTool` (which will process the docstring and parameter signature).
In [ ]:
Copied!
```
def multiply(a: int, b: int) -> int:
    """Multiply two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b

```

def multiply(a: int, b: int) -> int: """Multiply two integers and returns the result integer""" return a * b def add(a: int, b: int) -> int: """Add two integers and returns the result integer""" return a + b
## Run Some Queries¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.workflow import Context

llm = OpenAI(model="gpt-4o-mini")
agent = ReActAgent(tools=[multiply, add], llm=llm)

# Create a context to store the conversation history/session state
ctx = Context(agent)

```

from llama_index.llms.openai import OpenAI from llama_index.core.agent.workflow import ReActAgent from llama_index.core.workflow import Context llm = OpenAI(model="gpt-4o-mini") agent = ReActAgent(tools=[multiply, add], llm=llm) # Create a context to store the conversation history/session state ctx = Context(agent)
## Run Some Example Queries¶
By streaming the result, we can see the full response, including the thought process and tool calls.
If we wanted to stream only the result, we can buffer the stream and start streaming once `Answer:` is in the response.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import AgentStream, ToolCallResult

handler = agent.run("What is 20+(2*4)?", ctx=ctx)

async for ev in handler.stream_events():
    # if isinstance(ev, ToolCallResult):
    #     print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}")
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)

response = await handler

```

from llama_index.core.agent.workflow import AgentStream, ToolCallResult handler = agent.run("What is 20+(2*4)?", ctx=ctx) async for ev in handler.stream_events(): # if isinstance(ev, ToolCallResult): # print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}") if isinstance(ev, AgentStream): print(f"{ev.delta}", end="", flush=True) response = await handler
```
Thought: The current language of the user is: English. I need to use a tool to help me answer the question.
Action: multiply
Action Input: {"a": 2, "b": 4}Thought: Now I have the result of the multiplication, which is 8. I will add this to 20 to complete the calculation.
Action: add
Action Input: {'a': 20, 'b': 8}Thought: I can answer without using any more tools. I'll use the user's language to answer.
Answer: The result of 20 + (2 * 4) is 28.
```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The result of 20 + (2 * 4) is 28.

```

In [ ]:
Copied!
```
print(response.tool_calls)

```

print(response.tool_calls)
```
[ToolCallResult(tool_name='multiply', tool_kwargs={'a': 2, 'b': 4}, tool_id='a394d807-a9b7-42e0-8bff-f47a432d1530', tool_output=ToolOutput(content='8', tool_name='multiply', raw_input={'args': (), 'kwargs': {'a': 2, 'b': 4}}, raw_output=8, is_error=False), return_direct=False), ToolCallResult(tool_name='add', tool_kwargs={'a': 20, 'b': 8}, tool_id='784ccd85-ae9a-4184-9613-3696742064c7', tool_output=ToolOutput(content='28', tool_name='add', raw_input={'args': (), 'kwargs': {'a': 20, 'b': 8}}, raw_output=28, is_error=False), return_direct=False)]

```

## View Prompts¶
Let's take a look at the core system prompt powering the ReAct agent!
Within the agent, the current conversation history is dumped below this line.
In [ ]:
Copied!
```
prompt_dict = agent.get_prompts()
for k, v in prompt_dict.items():
    print(f"Prompt: {k}\n\nValue: {v.template}")

```

prompt_dict = agent.get_prompts() for k, v in prompt_dict.items(): print(f"Prompt: {k}\n\nValue: {v.template}")
```
Prompt: react_header

Value: You are designed to help with a variety of tasks, from answering questions to providing summaries to other types of analyses.

## Tools

You have access to a wide variety of tools. You are responsible for using the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools to complete each subtask.

You have access to the following tools:
{tool_desc}


## Output Format

Please answer in the same language as the question and use the following format:

```
Thought: The current language of the user is: (user's language). I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

Please ALWAYS start with a Thought.

NEVER surround your response with markdown code markers. You may use code markers within your response if you need to.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the tool will respond in the following format:

```
Observation: tool response
```

You should keep repeating the above format till you have enough information to answer the question without using any more tools. At that point, you MUST respond in one of the following two formats:

```
Thought: I can answer without using any more tools. I'll use the user's language to answer
Answer: [your answer here (In the same language as the user's question)]

Thought: I cannot answer the question with the provided tools.
Answer: [your answer here (In the same language as the user's question)]
```

## Current Conversation

Below is the current conversation consisting of interleaving human and assistant messages.


```

### Customizing the Prompt¶
For fun, let's try instructing the agent to output the answer along with reasoning in bullet points. See "## Additional Rules" section.
In [ ]:
Copied!
```
from llama_index.core import PromptTemplate

react_system_header_str = """\

You are designed to help with a variety of tasks, from answering questions \
    to providing summaries to other types of analyses.

## Tools
You have access to a wide variety of tools. You are responsible for using
the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools
to complete each subtask.

You have access to the following tools:
{tool_desc}

## Output Format
To answer the question, please use the following format.

```
Thought: I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

Please ALWAYS start with a Thought.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the user will respond in the following format:

```
Observation: tool response
```

You should keep repeating the above format until you have enough information
to answer the question without using any more tools. At that point, you MUST respond
in the one of the following two formats:

```
Thought: I can answer without using any more tools.
Answer: [your answer here]

Thought: I cannot answer the question with the provided tools.
Answer: Sorry, I cannot answer your query.
```

## Additional Rules
- The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history.
- You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments.

## Current Conversation
Below is the current conversation consisting of interleaving human and assistant messages.

"""
react_system_prompt = PromptTemplate(react_system_header_str)

```

from llama_index.core import PromptTemplate react_system_header_str = """\ You are designed to help with a variety of tasks, from answering questions \ to providing summaries to other types of analyses. ## Tools You have access to a wide variety of tools. You are responsible for using the tools in any sequence you deem appropriate to complete the task at hand. This may require breaking the task into subtasks and using different tools to complete each subtask. You have access to the following tools: {tool_desc} ## Output Format To answer the question, please use the following format. ``` Thought: I need to use a tool to help me answer the question. Action: tool name (one of {tool_names}) if using a tool. Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}}) ``` Please ALWAYS start with a Thought. Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}. If this format is used, the user will respond in the following format: ``` Observation: tool response ``` You should keep repeating the above format until you have enough information to answer the question without using any more tools. At that point, you MUST respond in the one of the following two formats: ``` Thought: I can answer without using any more tools. Answer: [your answer here] ``` ``` Thought: I cannot answer the question with the provided tools. Answer: Sorry, I cannot answer your query. ``` ## Additional Rules - The answer MUST contain a sequence of bullet points that explain how you arrived at the answer. This can include aspects of the previous conversation history. - You MUST obey the function signature of each tool. Do NOT pass in no arguments if the function expects arguments. ## Current Conversation Below is the current conversation consisting of interleaving human and assistant messages. """ react_system_prompt = PromptTemplate(react_system_header_str)
In [ ]:
Copied!
```
agent.get_prompts()

```

agent.get_prompts()
Out[ ]:
```
{'react_header': PromptTemplate(metadata={'prompt_type': <PromptType.CUSTOM: 'custom'>}, template_vars=['tool_desc', 'tool_names'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template='You are designed to help with a variety of tasks, from answering questions to providing summaries to other types of analyses.\n\n## Tools\n\nYou have access to a wide variety of tools. You are responsible for using the tools in any sequence you deem appropriate to complete the task at hand.\nThis may require breaking the task into subtasks and using different tools to complete each subtask.\n\nYou have access to the following tools:\n{tool_desc}\n\n\n## Output Format\n\nPlease answer in the same language as the question and use the following format:\n\n

In [ ]:
Copied!
```
agent.update_prompts({"react_header": react_system_prompt})

```

agent.update_prompts({"react_header": react_system_prompt})
In [ ]:
Copied!
```
handler = agent.run("What is 5+3+2")

async for ev in handler.stream_events():
    # if isinstance(ev, ToolCallResult):
    #     print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}")
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)

response = await handler

```

handler = agent.run("What is 5+3+2") async for ev in handler.stream_events(): # if isinstance(ev, ToolCallResult): # print(f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}") if isinstance(ev, AgentStream): print(f"{ev.delta}", end="", flush=True) response = await handler
```
Thought: The current language of the user is: English. I need to use a tool to help me answer the question.
Action: add
Action Input: {"a": 5, "b": 3}Thought: I need to add the result (8) to the remaining number (2).
Action: add
Action Input: {'a': 8, 'b': 2}Thought: I can answer without using any more tools. I'll use the user's language to answer.
Answer: The result of 5 + 3 + 2 is 10.
```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The result of 5 + 3 + 2 is 10.

```

