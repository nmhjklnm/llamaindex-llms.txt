# Function Calling Program for Structured Extraction¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
This guide shows you how to do structured data extraction with our `FunctionCallingProgram`. Given a function-calling LLM as well as an output Pydantic class, generate a structured Pydantic object. We use three different function calling LLMs:
  * OpenAI
  * Anthropic Claude
  * Mistral


In terms of the target object, you can choose to directly specify `output_cls`, or specify a `PydanticOutputParser` or any other BaseOutputParser that generates a Pydantic object.
in the examples below, we show you different ways of extracting into the `Album` object (which can contain a list of Song objects).
**NOTE** : The `FunctionCallingProgram` only works with LLMs that natively support function calling, by inserting the schema of the Pydantic object as the "tool parameters" for a tool. For all other LLMs, please use our `LLMTextCompletionProgram`, which will directly prompt the model through text to get back a structured output.
## Define `Album` class¶
This is a simple example of parsing an output into an `Album` schema, which can contain multiple songs.
Just pass `Album` into the `output_cls` property on initialization of the `FunctionCallingProgram`.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from pydantic import BaseModel
from typing import List

from llama_index.core.program import FunctionCallingProgram

```

from pydantic import BaseModel from typing import List from llama_index.core.program import FunctionCallingProgram
Define output schema
In [ ]:
Copied!
```
class Song(BaseModel):
    """Data model for a song."""

    title: str
    length_seconds: int


class Album(BaseModel):
    """Data model for an album."""

    name: str
    artist: str
    songs: List[Song]

```

class Song(BaseModel): """Data model for a song.""" title: str length_seconds: int class Album(BaseModel): """Data model for an album.""" name: str artist: str songs: List[Song]
## Define Function Calling Program¶
We define a function calling program with three function-calling LLMs:
  * OpenAI
  * Anthropic
  * Mistral


### Function Calling Program with OpenAI¶
Here we use gpt-3.5-turbo.
We demonstrate structured data extraction "single" function calling and also parallel function calling, allowing us to extract out multiple objects.
#### Function Calling (Single Object)¶
In [ ]:
Copied!
```
from llama_index.core.program import FunctionCallingProgram
from llama_index.llms.openai import OpenAI

```

from llama_index.core.program import FunctionCallingProgram from llama_index.llms.openai import OpenAI
In [ ]:
Copied!
```
prompt_template_str = """\
Generate an example album, with an artist and a list of songs. \
Using the movie {movie_name} as inspiration.\
"""
llm = OpenAI(model="gpt-3.5-turbo")

program = FunctionCallingProgram.from_defaults(
    output_cls=Album,
    prompt_template_str=prompt_template_str,
    verbose=True,
)

```

prompt_template_str = """\ Generate an example album, with an artist and a list of songs. \ Using the movie {movie_name} as inspiration.\ """ llm = OpenAI(model="gpt-3.5-turbo") program = FunctionCallingProgram.from_defaults( output_cls=Album, prompt_template_str=prompt_template_str, verbose=True, )
Run program to get structured output.
In [ ]:
Copied!
```
output = program(movie_name="The Shining")

```

output = program(movie_name="The Shining")
```
=== Calling Function ===
Calling function: Album with args: {"name": "The Shining Soundtrack", "artist": "Various Artists", "songs": [{"title": "Main Title", "length_seconds": 180}, {"title": "Rocky Mountains", "length_seconds": 240}, {"title": "Lullaby", "length_seconds": 200}, {"title": "The Overlook Hotel", "length_seconds": 220}, {"title": "Grady's Story", "length_seconds": 180}, {"title": "The Maze", "length_seconds": 210}]}
=== Function Output ===
name='The Shining Soundtrack' artist='Various Artists' songs=[Song(title='Main Title', length_seconds=180), Song(title='Rocky Mountains', length_seconds=240), Song(title='Lullaby', length_seconds=200), Song(title='The Overlook Hotel', length_seconds=220), Song(title="Grady's Story", length_seconds=180), Song(title='The Maze', length_seconds=210)]

```

The output is a valid Pydantic object that we can then use to call functions/APIs.
In [ ]:
Copied!
```
output

```

output
Out[ ]:
```
Album(name='The Shining Soundtrack', artist='Various Artists', songs=[Song(title='Main Title', length_seconds=180), Song(title='Rocky Mountains', length_seconds=240), Song(title='Lullaby', length_seconds=200), Song(title='The Overlook Hotel', length_seconds=220), Song(title="Grady's Story", length_seconds=180), Song(title='The Maze', length_seconds=210)])
```

#### Function Calling (Parallel Function Calling, Multiple Objects)¶
In [ ]:
Copied!
```
prompt_template_str = """\
Generate example albums, with an artist and a list of songs, using each movie below as inspiration. \

Here are the movies:
{movie_names}
"""
llm = OpenAI(model="gpt-3.5-turbo")

program = FunctionCallingProgram.from_defaults(
    output_cls=Album,
    prompt_template_str=prompt_template_str,
    verbose=True,
    allow_parallel_tool_calls=True,
)
output = program(movie_names="The Shining, The Blair Witch Project, Saw")

```

prompt_template_str = """\ Generate example albums, with an artist and a list of songs, using each movie below as inspiration. \ Here are the movies: {movie_names} """ llm = OpenAI(model="gpt-3.5-turbo") program = FunctionCallingProgram.from_defaults( output_cls=Album, prompt_template_str=prompt_template_str, verbose=True, allow_parallel_tool_calls=True, ) output = program(movie_names="The Shining, The Blair Witch Project, Saw")
```
=== Calling Function ===
Calling function: Album with args: {"name": "The Shining", "artist": "Various Artists", "songs": [{"title": "Main Theme", "length_seconds": 180}, {"title": "The Overlook Hotel", "length_seconds": 240}, {"title": "Redrum", "length_seconds": 200}]}
=== Function Output ===
name='The Shining' artist='Various Artists' songs=[Song(title='Main Theme', length_seconds=180), Song(title='The Overlook Hotel', length_seconds=240), Song(title='Redrum', length_seconds=200)]
=== Calling Function ===
Calling function: Album with args: {"name": "The Blair Witch Project", "artist": "Soundtrack Ensemble", "songs": [{"title": "Into the Woods", "length_seconds": 210}, {"title": "The Rustling Leaves", "length_seconds": 180}, {"title": "The Witch's Curse", "length_seconds": 240}]}
=== Function Output ===
name='The Blair Witch Project' artist='Soundtrack Ensemble' songs=[Song(title='Into the Woods', length_seconds=210), Song(title='The Rustling Leaves', length_seconds=180), Song(title="The Witch's Curse", length_seconds=240)]
=== Calling Function ===
Calling function: Album with args: {"name": "Saw", "artist": "Horror Soundscapes", "songs": [{"title": "The Reverse Bear Trap", "length_seconds": 220}, {"title": "Jigsaw's Game", "length_seconds": 260}, {"title": "Bathroom Escape", "length_seconds": 180}]}
=== Function Output ===
name='Saw' artist='Horror Soundscapes' songs=[Song(title='The Reverse Bear Trap', length_seconds=220), Song(title="Jigsaw's Game", length_seconds=260), Song(title='Bathroom Escape', length_seconds=180)]

```

In [ ]:
Copied!
```
output

```

output
Out[ ]:
```
[Album(name='The Shining', artist='Various Artists', songs=[Song(title='Main Theme', length_seconds=180), Song(title='The Overlook Hotel', length_seconds=240), Song(title='Redrum', length_seconds=200)]),
 Album(name='The Blair Witch Project', artist='Soundtrack Ensemble', songs=[Song(title='Into the Woods', length_seconds=210), Song(title='The Rustling Leaves', length_seconds=180), Song(title="The Witch's Curse", length_seconds=240)]),
 Album(name='Saw', artist='Horror Soundscapes', songs=[Song(title='The Reverse Bear Trap', length_seconds=220), Song(title="Jigsaw's Game", length_seconds=260), Song(title='Bathroom Escape', length_seconds=180)])]
```

### Function Calling Program with Anthropic¶
Here we use Claude Sonnet (all three models support function calling).
In [ ]:
Copied!
```
from llama_index.core.program import FunctionCallingProgram
from llama_index.llms.anthropic import Anthropic

```

from llama_index.core.program import FunctionCallingProgram from llama_index.llms.anthropic import Anthropic
In [ ]:
Copied!
```
prompt_template_str = "Generate a song about {topic}."
llm = Anthropic(model="claude-3-sonnet-20240229")

program = FunctionCallingProgram.from_defaults(
    output_cls=Song,
    prompt_template_str=prompt_template_str,
    llm=llm,
    verbose=True,
)

```

prompt_template_str = "Generate a song about {topic}." llm = Anthropic(model="claude-3-sonnet-20240229") program = FunctionCallingProgram.from_defaults( output_cls=Song, prompt_template_str=prompt_template_str, llm=llm, verbose=True, )
In [ ]:
Copied!
```
output = program(topic="harry potter")

```

output = program(topic="harry potter")
```
=== Calling Function ===
Calling function: Song with args: {"title": "The Boy Who Lived", "length_seconds": 180}
=== Function Output ===
title='The Boy Who Lived' length_seconds=180

```

In [ ]:
Copied!
```
output

```

output
Out[ ]:
```
Song(title='The Boy Who Lived', length_seconds=180)
```

### Function Calling Program with Mistral¶
Here we use mistral-large.
In [ ]:
Copied!
```
from llama_index.core.program import FunctionCallingProgram
from llama_index.llms.mistralai import MistralAI

```

from llama_index.core.program import FunctionCallingProgram from llama_index.llms.mistralai import MistralAI
In [ ]:
Copied!
```
# prompt_template_str = """\
# Generate an example album, with an artist and a list of songs. \
# Use the broadway show {broadway_show} as inspiration. \
# Make sure to use the tool.
# """
prompt_template_str = "Generate a song about {topic}."
llm = MistralAI(model="mistral-large-latest")
program = FunctionCallingProgram.from_defaults(
    output_cls=Song,
    prompt_template_str=prompt_template_str,
    llm=llm,
    verbose=True,
)

```

# prompt_template_str = """\ # Generate an example album, with an artist and a list of songs. \ # Use the broadway show {broadway_show} as inspiration. \ # Make sure to use the tool. # """ prompt_template_str = "Generate a song about {topic}." llm = MistralAI(model="mistral-large-latest") program = FunctionCallingProgram.from_defaults( output_cls=Song, prompt_template_str=prompt_template_str, llm=llm, verbose=True, )
In [ ]:
Copied!
```
output = program(topic="the broadway show Wicked")

```

output = program(topic="the broadway show Wicked")
```
=== Calling Function ===
Calling function: Song with args: {"title": "Defying Gravity", "length_seconds": 240}
=== Function Output ===
title='Defying Gravity' length_seconds=240

```

In [ ]:
Copied!
```
output

```

output
Out[ ]:
```
Song(title='Defying Gravity', length_seconds=240)
```

In [ ]:
Copied!
```
from llama_index.core.output_parsers import PydanticOutputParser

program = LLMTextCompletionProgram.from_defaults(
    output_parser=PydanticOutputParser(output_cls=Album),
    prompt_template_str=prompt_template_str,
    verbose=True,
)

```

from llama_index.core.output_parsers import PydanticOutputParser program = LLMTextCompletionProgram.from_defaults( output_parser=PydanticOutputParser(output_cls=Album), prompt_template_str=prompt_template_str, verbose=True, )
In [ ]:
Copied!
```
output = program(movie_name="Lord of the Rings")
output

```

output = program(movie_name="Lord of the Rings") output
Out[ ]:
```
Album(name='The Fellowship of the Ring', artist='Middle-earth Ensemble', songs=[Song(title='The Shire', length_seconds=240), Song(title='Concerning Hobbits', length_seconds=180), Song(title='The Ring Goes South', length_seconds=300), Song(title='A Knife in the Dark', length_seconds=270), Song(title='Flight to the Ford', length_seconds=210), Song(title='Many Meetings', length_seconds=240), Song(title='The Council of Elrond', length_seconds=330), Song(title='The Great Eye', length_seconds=180), Song(title='The Breaking of the Fellowship', length_seconds=360)])
```

