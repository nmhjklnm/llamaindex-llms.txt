# Build an Order Completion Agent with an Artifact Editor Tool¶
In this example, we'll build a chat assistant that is designed to fill in a custom 'form'.
As an example use-case, we'll build an order taking assistant that will need to get a few set pieces of information from the end-user before proceeding. Like their delivery address, and the contents of their order.
To build this, we're using the new `ArtifactEditorToolSpec` and `ArtifactMemoryBlock`
In [ ]:
Copied!
```
!pip install llama-index llama-index-tools-artifact-editor

```

!pip install llama-index llama-index-tools-artifact-editor
In [ ]:
Copied!
```
import os
import json
from getpass import getpass
from pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI
from llama_index.core.memory import Memory
from llama_index.core.agent.workflow import (
    FunctionAgent,
    AgentWorkflow,
    ToolCallResult,
    AgentStream,
)
from llama_index.tools.artifact_editor import (
    ArtifactEditorToolSpec,
    ArtifactMemoryBlock,
)

```

import os import json from getpass import getpass from pydantic import BaseModel, Field from llama_index.llms.openai import OpenAI from llama_index.core.memory import Memory from llama_index.core.agent.workflow import ( FunctionAgent, AgentWorkflow, ToolCallResult, AgentStream, ) from llama_index.tools.artifact_editor import ( ArtifactEditorToolSpec, ArtifactMemoryBlock, )
In [ ]:
Copied!
```
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass("OpenAI API Key: ")

```

if "OPENAI_API_KEY" not in os.environ: os.environ["OPENAI_API_KEY"] = getpass("OpenAI API Key: ")
In [ ]:
Copied!
```
class Pizza(BaseModel):
    name: str = Field(description="The name of the pizza")
    remove: list[str] | None = Field(
        description="If exists, the ingredients the customer requests to remove",
        default=None,
    )
    add: list[str] | None = Field(
        description="If exists, the ingredients the customer requests to be added",
        default=None,
    )


class Address(BaseModel):
    street_address: str = Field(
        description="The street address of the customer"
    )
    city: str = Field(description="The city of the customer")
    state: str = Field(description="The state of the customer")
    zip_code: str = Field(description="The zip code of the customer")


class Order(BaseModel):
    pizzas: list[Pizza] | None = Field(
        description="The pizzas ordered by the customer", default=None
    )
    address: Address | None = Field(
        description="The full address of the customer", default=None
    )

```

class Pizza(BaseModel): name: str = Field(description="The name of the pizza") remove: list[str] | None = Field( description="If exists, the ingredients the customer requests to remove", default=None, ) add: list[str] | None = Field( description="If exists, the ingredients the customer requests to be added", default=None, ) class Address(BaseModel): street_address: str = Field( description="The street address of the customer" ) city: str = Field(description="The city of the customer") state: str = Field(description="The state of the customer") zip_code: str = Field(description="The zip code of the customer") class Order(BaseModel): pizzas: list[Pizza] | None = Field( description="The pizzas ordered by the customer", default=None ) address: Address | None = Field( description="The full address of the customer", default=None )
In [ ]:
Copied!
```
tool_spec = ArtifactEditorToolSpec(Order)
tools = tool_spec.to_tool_list()

# Initialize the memory
memory = Memory.from_defaults(
    session_id="order_editor",
    memory_blocks=[ArtifactMemoryBlock(artifact_spec=tool_spec)],
    token_limit=60000,
    chat_history_token_ratio=0.7,
)

llm = OpenAI(model="gpt-4.1")

agent = AgentWorkflow(
    agents=[
        FunctionAgent(
            llm=llm,
            tools=tools,
            system_prompt="""You are a worker at a Pizzeria. Your job is to talk to users and gather order information.
            At every step, you should check the order completeness before responding to the user, and ask for any possibly
            missing information.""",
        )
    ],
)

```

tool_spec = ArtifactEditorToolSpec(Order) tools = tool_spec.to_tool_list() # Initialize the memory memory = Memory.from_defaults( session_id="order_editor", memory_blocks=[ArtifactMemoryBlock(artifact_spec=tool_spec)], token_limit=60000, chat_history_token_ratio=0.7, ) llm = OpenAI(model="gpt-4.1") agent = AgentWorkflow( agents=[ FunctionAgent( llm=llm, tools=tools, system_prompt="""You are a worker at a Pizzeria. Your job is to talk to users and gather order information. At every step, you should check the order completeness before responding to the user, and ask for any possibly missing information.""", ) ], )
In [ ]:
Copied!
```
async def chat():
    while True:
        user_msg = input("User: ").strip()
        if user_msg.lower() in ["exit", "quit"]:
            print("\n------ORDER COMPLETION-------\n")
            print(
                f"The Order was placed with the following Order schema:\n: {json.dumps(tool_spec.get_current_artifact(), indent=4)}"
            )
            break

        handler = agent.run(user_msg, memory=memory)
        async for ev in handler.stream_events():
            if isinstance(ev, AgentStream):
                print(ev.delta, end="", flush=True)
            elif isinstance(ev, ToolCallResult):
                print(
                    f"\n\nCalling tool: {ev.tool_name} with kwargs: {ev.tool_kwargs}"
                )

        # response = await handler
        # print(str(response))
        print("\n\nCurrent artifact: ", tool_spec.get_current_artifact())

```

async def chat(): while True: user_msg = input("User: ").strip() if user_msg.lower() in ["exit", "quit"]: print("\n------ORDER COMPLETION-------\n") print( f"The Order was placed with the following Order schema:\n: {json.dumps(tool_spec.get_current_artifact(), indent=4)}" ) break handler = agent.run(user_msg, memory=memory) async for ev in handler.stream_events(): if isinstance(ev, AgentStream): print(ev.delta, end="", flush=True) elif isinstance(ev, ToolCallResult): print( f"\n\nCalling tool: {ev.tool_name} with kwargs: {ev.tool_kwargs}" ) # response = await handler # print(str(response)) print("\n\nCurrent artifact: ", tool_spec.get_current_artifact())
In [ ]:
Copied!
```
await chat()

```

await chat()
```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Hello! Welcome to our pizzeria. Would you like to place an order? If so, could you please tell me what kind of pizza you’d like?

Current artifact:  None

```

```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```

Calling tool: create_artifact with kwargs: {'pizzas': [{'name': 'pepperoni', 'add': ['olives']}, {'name': 'margherita'}]}

```

```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
You’ve ordered:
- 1 Pepperoni pizza with added olives
- 1 Margherita pizza

To complete your order, could you please provide your delivery address (street address, city, state, and zip code)?

Current artifact:  {'pizzas': [{'name': 'pepperoni', 'remove': None, 'add': ['olives']}, {'name': 'margherita', 'remove': None, 'add': None}], 'address': None}

```

```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```

Calling tool: apply_patch with kwargs: {'patch': {'operations': [{'op': 'replace', 'path': '/address', 'value': {'street_address': '1 Sesame Street', 'city': 'Amsterdam', 'state': 'North-Holand', 'zip_code': '1111AB'}}]}}

```

```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Thank you! Your order is now complete:

- 1 Pepperoni pizza with added olives
- 1 Margherita pizza

Delivery address:
1 Sesame Street, Amsterdam, North-Holand, 1111AB

Would you like to add anything else to your order, or should I proceed with placing it?

Current artifact:  {'pizzas': [{'name': 'pepperoni', 'remove': None, 'add': ['olives']}, {'name': 'margherita', 'remove': None, 'add': None}], 'address': {'street_address': '1 Sesame Street', 'city': 'Amsterdam', 'state': 'North-Holand', 'zip_code': '1111AB'}}

```

```
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Great! Your order has been placed:

- 1 Pepperoni pizza with added olives
- 1 Margherita pizza

Delivery to: 1 Sesame Street, Amsterdam, North-Holand, 1111AB

Thank you for ordering with us! Your pizzas will be delivered soon. Have a delicious day!

Current artifact:  {'pizzas': [{'name': 'pepperoni', 'remove': None, 'add': ['olives']}, {'name': 'margherita', 'remove': None, 'add': None}], 'address': {'street_address': '1 Sesame Street', 'city': 'Amsterdam', 'state': 'North-Holand', 'zip_code': '1111AB'}}

------ORDER COMPLETION-------

The Order was placed with the following Order schema:
: {
    "pizzas": [
        {
            "name": "pepperoni",
            "remove": null,
            "add": [
                "olives"
            ]
        },
        {
            "name": "margherita",
            "remove": null,
            "add": null
        }
    ],
    "address": {
        "street_address": "1 Sesame Street",
        "city": "Amsterdam",
        "state": "North-Holand",
        "zip_code": "1111AB"
    }
}

```

