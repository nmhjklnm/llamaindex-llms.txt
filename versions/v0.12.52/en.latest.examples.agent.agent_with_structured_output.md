# Agents with Structured Outputs¶
When you run your agent or multi-agent framework, you might want it to output the result in a specific format. In this notebook, we will see a simple example of how to apply this to a FunctionAgent!🦙🚀
Let's first install the needed dependencies
In [ ]:
Copied!
```
! pip install llama-index

```

! pip install llama-index
In [ ]:
Copied!
```
from getpass import getpass
import os

os.environ["OPENAI_API_KEY"] = getpass()

```

from getpass import getpass import os os.environ["OPENAI_API_KEY"] = getpass()
Let's now define our structured output format
In [ ]:
Copied!
```
from pydantic import BaseModel, Field


class MathResult(BaseModel):
    operation: str = Field(description="The operation that has been performed")
    result: int = Field(description="Result of the operation")

```

from pydantic import BaseModel, Field class MathResult(BaseModel): operation: str = Field(description="The operation that has been performed") result: int = Field(description="Result of the operation")
And a very simple calculator agent
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent

llm = OpenAI(model="gpt-4.1")


def add(x: int, y: int):
    """Add two numbers"""
    return x + y


def multiply(x: int, y: int):
    """Multiply two numbers"""
    return x * y


agent = FunctionAgent(
    llm=llm,
    output_cls=MathResult,
    tools=[add, multiply],
    system_prompt="You are a calculator agent that can add or multiply two numbers by calling tools",
    name="calculator",
)

```

from llama_index.llms.openai import OpenAI from llama_index.core.agent.workflow import FunctionAgent llm = OpenAI(model="gpt-4.1") def add(x: int, y: int): """Add two numbers""" return x + y def multiply(x: int, y: int): """Multiply two numbers""" return x * y agent = FunctionAgent( llm=llm, output_cls=MathResult, tools=[add, multiply], system_prompt="You are a calculator agent that can add or multiply two numbers by calling tools", name="calculator", )
Let's now run the agent
In [ ]:
Copied!
```
response = await agent.run("What is the result of 10 multiplied by 4?")

```

response = await agent.run("What is the result of 10 multiplied by 4?")
Finally, we can get the structured output
In [ ]:
Copied!
```
# print the structured output as a plain dictionary
print(response.structured_response)
# print the structured output as a Pydantic model
print(response.get_pydantic_model(MathResult))

```

# print the structured output as a plain dictionary print(response.structured_response) # print the structured output as a Pydantic model print(response.get_pydantic_model(MathResult))
