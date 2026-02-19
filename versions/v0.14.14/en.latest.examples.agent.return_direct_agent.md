# Controlling Agent Reasoning Loop with Return Direct Tools¶
All tools have an option for `return_direct` -- if this is set to `True`, and the associated tool is called (without any other tools being called), the agent reasoning loop is ended and the tool output is returned directly.
This can be useful for speeding up response times when you know the tool output is good enough, to avoid the agent re-writing the response, and for ending the reasoning loop.
This notebook walks through a notebook where an agent needs to gather information from a user in order to make a restaurant booking.
In [ ]:
Copied!
```
%pip install llama-index-core llama-index-llms-anthropic

```

%pip install llama-index-core llama-index-llms-anthropic
In [ ]:
Copied!
```
import os

os.environ["ANTHROPIC_API_KEY"] = "sk-..."

```

import os os.environ["ANTHROPIC_API_KEY"] = "sk-..."
## Tools setup¶
In [ ]:
Copied!
```
from typing import Optional

from llama_index.core.tools import FunctionTool
from pydantic import BaseModel

# we will store booking under random IDs
bookings = {}


# we will represent and track the state of a booking as a Pydantic model
class Booking(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None


def get_booking_state(user_id: str) -> str:
    """Get the current state of a booking for a given booking ID."""
    try:
        return str(bookings[user_id].dict())
    except:
        return f"Booking ID {user_id} not found"


def update_booking(user_id: str, property: str, value: str) -> str:
    """Update a property of a booking for a given booking ID. Only enter details that are explicitly provided."""
    booking = bookings[user_id]
    setattr(booking, property, value)
    return f"Booking ID {user_id} updated with {property} = {value}"


def create_booking(user_id: str) -> str:
    """Create a new booking and return the booking ID."""
    bookings[user_id] = Booking()
    return "Booking created, but not yet confirmed. Please provide your name, email, phone, date, and time."


def confirm_booking(user_id: str) -> str:
    """Confirm a booking for a given booking ID."""
    booking = bookings[user_id]

    if booking.name is None:
        raise ValueError("Please provide your name.")

    if booking.email is None:
        raise ValueError("Please provide your email.")

    if booking.phone is None:
        raise ValueError("Please provide your phone number.")

    if booking.date is None:
        raise ValueError("Please provide the date of your booking.")

    if booking.time is None:
        raise ValueError("Please provide the time of your booking.")

    return f"Booking ID {user_id} confirmed!"


# create tools for each function
get_booking_state_tool = FunctionTool.from_defaults(fn=get_booking_state)
update_booking_tool = FunctionTool.from_defaults(fn=update_booking)
create_booking_tool = FunctionTool.from_defaults(
    fn=create_booking, return_direct=True
)
confirm_booking_tool = FunctionTool.from_defaults(
    fn=confirm_booking, return_direct=True
)

```

from typing import Optional from llama_index.core.tools import FunctionTool from pydantic import BaseModel # we will store booking under random IDs bookings = {} # we will represent and track the state of a booking as a Pydantic model class Booking(BaseModel): name: Optional[str] = None email: Optional[str] = None phone: Optional[str] = None date: Optional[str] = None time: Optional[str] = None def get_booking_state(user_id: str) -> str: """Get the current state of a booking for a given booking ID.""" try: return str(bookings[user_id].dict()) except: return f"Booking ID {user_id} not found" def update_booking(user_id: str, property: str, value: str) -> str: """Update a property of a booking for a given booking ID. Only enter details that are explicitly provided.""" booking = bookings[user_id] setattr(booking, property, value) return f"Booking ID {user_id} updated with {property} = {value}" def create_booking(user_id: str) -> str: """Create a new booking and return the booking ID.""" bookings[user_id] = Booking() return "Booking created, but not yet confirmed. Please provide your name, email, phone, date, and time." def confirm_booking(user_id: str) -> str: """Confirm a booking for a given booking ID.""" booking = bookings[user_id] if booking.name is None: raise ValueError("Please provide your name.") if booking.email is None: raise ValueError("Please provide your email.") if booking.phone is None: raise ValueError("Please provide your phone number.") if booking.date is None: raise ValueError("Please provide the date of your booking.") if booking.time is None: raise ValueError("Please provide the time of your booking.") return f"Booking ID {user_id} confirmed!" # create tools for each function get_booking_state_tool = FunctionTool.from_defaults(fn=get_booking_state) update_booking_tool = FunctionTool.from_defaults(fn=update_booking) create_booking_tool = FunctionTool.from_defaults( fn=create_booking, return_direct=True ) confirm_booking_tool = FunctionTool.from_defaults( fn=confirm_booking, return_direct=True )
## A user has walked in! Let's help them make a booking¶
In [ ]:
Copied!
```
from llama_index.llms.anthropic import Anthropic
from llama_index.core.llms import ChatMessage
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context

llm = Anthropic(model="claude-3-sonnet-20240229", temperature=0.1)

user = "user123"
system_prompt = f"""You are now connected to the booking system and helping {user} with making a booking.
Only enter details that the user has explicitly provided.
Do not make up any details.
"""

agent = FunctionAgent(
    tools=[
        get_booking_state_tool,
        update_booking_tool,
        create_booking_tool,
        confirm_booking_tool,
    ],
    llm=llm,
    system_prompt=system_prompt,
)

# create a context for the agent to hold the state/history of a session
ctx = Context(agent)

```

from llama_index.llms.anthropic import Anthropic from llama_index.core.llms import ChatMessage from llama_index.core.agent.workflow import FunctionAgent from llama_index.core.workflow import Context llm = Anthropic(model="claude-3-sonnet-20240229", temperature=0.1) user = "user123" system_prompt = f"""You are now connected to the booking system and helping {user} with making a booking. Only enter details that the user has explicitly provided. Do not make up any details. """ agent = FunctionAgent( tools=[ get_booking_state_tool, update_booking_tool, create_booking_tool, confirm_booking_tool, ], llm=llm, system_prompt=system_prompt, ) # create a context for the agent to hold the state/history of a session ctx = Context(agent)
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import AgentStream, ToolCallResult

handler = agent.run(
    "Hello! I would like to make a booking, around 5pm?", ctx=ctx
)

async for ev in handler.stream_events():
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)
    elif isinstance(ev, ToolCallResult):
        print(
            f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}"
        )

response = await handler

```

from llama_index.core.agent.workflow import AgentStream, ToolCallResult handler = agent.run( "Hello! I would like to make a booking, around 5pm?", ctx=ctx ) async for ev in handler.stream_events(): if isinstance(ev, AgentStream): print(f"{ev.delta}", end="", flush=True) elif isinstance(ev, ToolCallResult): print( f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}" ) response = await handler
```
Okay, let's create a new booking for you.{"user_id": "user123"}
Call create_booking with {'user_id': 'user123'}
Returned: Booking created, but not yet confirmed. Please provide your name, email, phone, date, and time.

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Booking created, but not yet confirmed. Please provide your name, email, phone, date, and time.

```

Perfect, we can see the function output was retruned directly, with no modification or final LLM call!
In [ ]:
Copied!
```
handler = agent.run(
    "Sure! My name is Logan, and my email is test@gmail.com?", ctx=ctx
)

async for ev in handler.stream_events():
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)
    elif isinstance(ev, ToolCallResult):
        print(
            f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}"
        )

response = await handler

```

handler = agent.run( "Sure! My name is Logan, and my email is test@gmail.com?", ctx=ctx ) async for ev in handler.stream_events(): if isinstance(ev, AgentStream): print(f"{ev.delta}", end="", flush=True) elif isinstance(ev, ToolCallResult): print( f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}" ) response = await handler
```
Got it, thanks for providing your name and email. I've updated the booking with that information.{"user_id": "user123", "property": "name", "value": "Logan"}{"user_id": "user123", "property": "email", "value": "test@gmail.com"}
Call update_booking with {'user_id': 'user123', 'property': 'name', 'value': 'Logan'}
Returned: Booking ID user123 updated with name = Logan

Call update_booking with {'user_id': 'user123', 'property': 'email', 'value': 'test@gmail.com'}
Returned: Booking ID user123 updated with email = test@gmail.com
Please also provide your phone number, preferred date, and time for the booking.
```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Please also provide your phone number, preferred date, and time for the booking.

```

In [ ]:
Copied!
```
handler = agent.run(
    "Right! My phone number is 1234567890, the date of the booking is April 5, at 5pm.",
    ctx=ctx,
)

async for ev in handler.stream_events():
    if isinstance(ev, AgentStream):
        print(f"{ev.delta}", end="", flush=True)
    elif isinstance(ev, ToolCallResult):
        print(
            f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}"
        )

response = await handler

```

handler = agent.run( "Right! My phone number is 1234567890, the date of the booking is April 5, at 5pm.", ctx=ctx, ) async for ev in handler.stream_events(): if isinstance(ev, AgentStream): print(f"{ev.delta}", end="", flush=True) elif isinstance(ev, ToolCallResult): print( f"\nCall {ev.tool_name} with {ev.tool_kwargs}\nReturned: {ev.tool_output}" ) response = await handler
```
Great, thank you for providing the additional details. I've updated the booking with your phone number, date, and time.{"user_id": "user123", "property": "phone", "value": "1234567890"}{"user_id": "user123", "property": "date", "value": "2023-04-05"}{"user_id": "user123", "property": "time", "value": "17:00"}
Call update_booking with {'user_id': 'user123', 'property': 'phone', 'value': '1234567890'}
Returned: Booking ID user123 updated with phone = 1234567890

Call update_booking with {'user_id': 'user123', 'property': 'date', 'value': '2023-04-05'}
Returned: Booking ID user123 updated with date = 2023-04-05

Call update_booking with {'user_id': 'user123', 'property': 'time', 'value': '17:00'}
Returned: Booking ID user123 updated with time = 17:00
Looks like I have all the necessary details. Let me confirm this booking for you.{"user_id": "user123"}
Call confirm_booking with {'user_id': 'user123'}
Returned: Booking ID user123 confirmed!

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Booking ID user123 confirmed!

```

In [ ]:
Copied!
```
print(bookings["user123"])

```

print(bookings["user123"])
```
name='Logan' email='test@gmail.com' phone='1234567890' date='2023-04-05' time='17:00'

```

