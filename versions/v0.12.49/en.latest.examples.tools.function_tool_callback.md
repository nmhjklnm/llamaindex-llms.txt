# Function call with callback¶
This is a feature that allows applying some human-in-the-loop concepts in FunctionTool.
Basically, a callback function is added that enables the developer to request user input in the middle of an agent interaction, as well as allowing any programmatic action.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-agents-openai

```

%pip install llama-index-llms-openai %pip install llama-index-agents-openai
In [ ]:
Copied!
```
from llama_index.core.tools import FunctionTool
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
import os

```

from llama_index.core.tools import FunctionTool from llama_index.agent.openai import OpenAIAgent from llama_index.llms.openai import OpenAI import os
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "sk-"

```

os.environ["OPENAI_API_KEY"] = "sk-"
Function to display to the user the data produced for function calling and request their input to return to the interaction.
In [ ]:
Copied!
```
def callback(message):
    confirmation = input(
        f"{message[1]}\nDo you approve of sending this greeting?\nInput(Y/N):"
    )

    if confirmation.lower() == "y":
        # Here you can trigger an action such as sending an email, message, api call, etc.
        return "Greeting sent successfully."
    else:
        return (
            "Greeting has not been approved, talk a bit about how to improve"
        )

```

def callback(message): confirmation = input( f"{message[1]}\nDo you approve of sending this greeting?\nInput(Y/N):" ) if confirmation.lower() == "y": # Here you can trigger an action such as sending an email, message, api call, etc. return "Greeting sent successfully." else: return ( "Greeting has not been approved, talk a bit about how to improve" )
Simple function that only requires a recipient and a greeting message.
In [ ]:
Copied!
```
def send_hello(destination: str, message: str) -> str:
    """
    Say hello with a rhyme
    destination: str - Name of recipient
    message: str - Greeting message with a rhyme to the recipient's name
    """

    return destination, message


hello_tool = FunctionTool.from_defaults(fn=send_hello, callback=callback)

```

def send_hello(destination: str, message: str) -> str: """ Say hello with a rhyme destination: str - Name of recipient message: str - Greeting message with a rhyme to the recipient's name """ return destination, message hello_tool = FunctionTool.from_defaults(fn=send_hello, callback=callback)
In [ ]:
Copied!
```
hello_tool.to_langchain_tool

```

hello_tool.to_langchain_tool
Out[ ]:
```
<bound method FunctionTool.to_langchain_tool of <llama_index.core.tools.function_tool.FunctionTool object at 0x7f7da9fa5670>>
```

In [ ]:
Copied!
```
llm = OpenAI()
agent = OpenAIAgent.from_tools([hello_tool])

```

llm = OpenAI() agent = OpenAIAgent.from_tools([hello_tool])
In [ ]:
Copied!
```
response = agent.chat("Send hello to Karen")
print(str(response))

```

response = agent.chat("Send hello to Karen") print(str(response))
```
The hello message has been sent to Karen with the rhyme "Hello Karen, you're a star!"

```

In [ ]:
Copied!
```
response = agent.chat("Send hello to Joe")
print(str(response))

```

response = agent.chat("Send hello to Joe") print(str(response))
```
I have successfully sent a hello message to Joe with the greeting "Hello Joe, you're a pro!"

```

