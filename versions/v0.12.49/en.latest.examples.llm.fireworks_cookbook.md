![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Fireworks Function Calling Cookbook¶
Fireworks.ai supports function calling for its LLMs, similar to OpenAI. This lets users directly describe the set of tools/functions available and have the model dynamically pick the right function calls to invoke, without complex prompting on the user's part.
Since our Fireworks LLM directly subclasses OpenAI, we can use our existing abstractions with Fireworks.
We show this on three levels: directly on the model API, as part of a Pydantic Program (structured output extraction), and as part of an agent.
In [ ]:
Copied!
```
%pip install llama-index-llms-fireworks

```

%pip install llama-index-llms-fireworks
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

os.environ["FIREWORKS_API_KEY"] = ""

```

import os os.environ["FIREWORKS_API_KEY"] = ""
In [ ]:
Copied!
```
from llama_index.llms.fireworks import Fireworks

## define fireworks model
llm = Fireworks(
    model="accounts/fireworks/models/firefunction-v1", temperature=0
)

```

from llama_index.llms.fireworks import Fireworks ## define fireworks model llm = Fireworks( model="accounts/fireworks/models/firefunction-v1", temperature=0 )
```
/Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

## Function Calling on the LLM Module¶
You can directly input function calls on the LLM module.
In [ ]:
Copied!
```
from pydantic import BaseModel
from llama_index.llms.openai.utils import to_openai_tool


class Song(BaseModel):
    """A song with name and artist"""

    name: str
    artist: str


# this converts pydantic model into function to extract structured outputs
song_fn = to_openai_tool(Song)


response = llm.complete("Generate a song from Beyonce", tools=[song_fn])
tool_calls = response.additional_kwargs["tool_calls"]
print(tool_calls)

```

from pydantic import BaseModel from llama_index.llms.openai.utils import to_openai_tool class Song(BaseModel): """A song with name and artist""" name: str artist: str # this converts pydantic model into function to extract structured outputs song_fn = to_openai_tool(Song) response = llm.complete("Generate a song from Beyonce", tools=[song_fn]) tool_calls = response.additional_kwargs["tool_calls"] print(tool_calls)
```
[ChatCompletionMessageToolCall(id='call_34ZaM0xPl1cveODjVUpO78ra', function=Function(arguments='{"name": "Crazy in Love", "artist": "Beyonce"}', name='Song'), type='function', index=0)]

```

## Using a Pydantic Program¶
Our Pydantic programs allow structured output extraction into a Pydantic object. `OpenAIPydanticProgram` takes advantage of function calling for structured output extraction.
In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram

```

from llama_index.program.openai import OpenAIPydanticProgram
In [ ]:
Copied!
```
prompt_template_str = "Generate a song about {artist_name}"
program = OpenAIPydanticProgram.from_defaults(
    output_cls=Song, prompt_template_str=prompt_template_str, llm=llm
)

```

prompt_template_str = "Generate a song about {artist_name}" program = OpenAIPydanticProgram.from_defaults( output_cls=Song, prompt_template_str=prompt_template_str, llm=llm )
In [ ]:
Copied!
```
output = program(artist_name="Eminem")

```

output = program(artist_name="Eminem")
In [ ]:
Copied!
```
output

```

output
Out[ ]:
```
Song(name='Rap God', artist='Eminem')
```

## Using An OpenAI Agent¶
In [ ]:
Copied!
```
from llama_index.agent.openai import OpenAIAgent

```

from llama_index.agent.openai import OpenAIAgent
In [ ]:
Copied!
```
from llama_index.core.tools import BaseTool, FunctionTool


def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


multiply_tool = FunctionTool.from_defaults(fn=multiply)


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


add_tool = FunctionTool.from_defaults(fn=add)

```

from llama_index.core.tools import BaseTool, FunctionTool def multiply(a: int, b: int) -> int: """Multiple two integers and returns the result integer""" return a * b multiply_tool = FunctionTool.from_defaults(fn=multiply) def add(a: int, b: int) -> int: """Add two integers and returns the result integer""" return a + b add_tool = FunctionTool.from_defaults(fn=add)
In [ ]:
Copied!
```
agent = OpenAIAgent.from_tools(
    [multiply_tool, add_tool], llm=llm, verbose=True
)

```

agent = OpenAIAgent.from_tools( [multiply_tool, add_tool], llm=llm, verbose=True )
In [ ]:
Copied!
```
response = agent.chat("What is (121 * 3) + 42?")
print(str(response))

```

response = agent.chat("What is (121 * 3) + 42?") print(str(response))
```
Added user message to memory: What is (121 * 3) + 42?
=== Calling Function ===
Calling function: multiply with args: {"a": 121, "b": 3}
Got output: 363
========================

=== Calling Function ===
Calling function: add with args: {"a": 363, "b": 42}
Got output: 405
========================

The result of (121 * 3) + 42 is 405.

```

