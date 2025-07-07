![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Llama API¶
Llama API is a hosted API for Llama 2 with function calling support.
## Setup¶
To start, go to https://www.llama-api.com/ to obtain an API key
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-program-openai
%pip install llama-index-llms-llama-api

```

%pip install llama-index-program-openai %pip install llama-index-llms-llama-api
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.llms.llama_api import LlamaAPI

```

from llama_index.llms.llama_api import LlamaAPI
In [ ]:
Copied!
```
api_key = "LL-your-key"

```

api_key = "LL-your-key"
In [ ]:
Copied!
```
llm = LlamaAPI(api_key=api_key)

```

llm = LlamaAPI(api_key=api_key)
## Basic Usage¶
#### Call `complete` with a prompt¶
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
```
Paul Graham is a well-known computer scientist and entrepreneur, best known for his work as a co-founder of Viaweb and later Y Combinator, a successful startup accelerator. He is also a prominent essayist and has written extensively on topics such as entrepreneurship, software development, and the tech industry.

```

#### Call `chat` with a list of messages¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with a colorful personality"
    ),
    ChatMessage(role="user", content="What is your name"),
]
resp = llm.chat(messages)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="You are a pirate with a colorful personality" ), ChatMessage(role="user", content="What is your name"), ] resp = llm.chat(messages)
In [ ]:
Copied!
```
print(resp)

```

print(resp)
```
assistant: Arrrr, me hearty! Me name be Captain Blackbeak, the scurviest dog on the seven seas! Yer lookin' fer a swashbucklin' adventure, eh? Well, hoist the sails and set course fer the high seas, matey! I be here to help ye find yer treasure and battle any scurvy dogs who dare cross our path! So, what be yer first question, landlubber?

```

## Function Calling¶
In [ ]:
Copied!
```
from pydantic import BaseModel
from llama_index.core.llms.openai_utils import to_openai_function


class Song(BaseModel):
    """A song with name and artist"""

    name: str
    artist: str


song_fn = to_openai_function(Song)

```

from pydantic import BaseModel from llama_index.core.llms.openai_utils import to_openai_function class Song(BaseModel): """A song with name and artist""" name: str artist: str song_fn = to_openai_function(Song)
In [ ]:
Copied!
```
llm = LlamaAPI(api_key=api_key)
response = llm.complete("Generate a song", functions=[song_fn])
function_call = response.additional_kwargs["function_call"]
print(function_call)

```

llm = LlamaAPI(api_key=api_key) response = llm.complete("Generate a song", functions=[song_fn]) function_call = response.additional_kwargs["function_call"] print(function_call)
```
{'name': 'Song', 'arguments': {'name': 'Happy', 'artist': 'Pharrell Williams'}}

```

## Structured Data Extraction¶
This is a simple example of parsing an output into an `Album` schema, which can contain multiple songs.
Define output schema
In [ ]:
Copied!
```
from pydantic import BaseModel
from typing import List


class Song(BaseModel):
    """Data model for a song."""

    title: str
    length_mins: int


class Album(BaseModel):
    """Data model for an album."""

    name: str
    artist: str
    songs: List[Song]

```

from pydantic import BaseModel from typing import List class Song(BaseModel): """Data model for a song.""" title: str length_mins: int class Album(BaseModel): """Data model for an album.""" name: str artist: str songs: List[Song]
Define pydantic program (llama API is OpenAI-compatible)
In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram

prompt_template_str = """\
Extract album and songs from the text provided.
For each song, make sure to specify the title and the length_mins.
{text}
"""

llm = LlamaAPI(api_key=api_key, temperature=0.0)

program = OpenAIPydanticProgram.from_defaults(
    output_cls=Album,
    llm=llm,
    prompt_template_str=prompt_template_str,
    verbose=True,
)

```

from llama_index.program.openai import OpenAIPydanticProgram prompt_template_str = """\ Extract album and songs from the text provided. For each song, make sure to specify the title and the length_mins. {text} """ llm = LlamaAPI(api_key=api_key, temperature=0.0) program = OpenAIPydanticProgram.from_defaults( output_cls=Album, llm=llm, prompt_template_str=prompt_template_str, verbose=True, )
Run program to get structured output.
In [ ]:
Copied!
```
output = program(
    text="""
"Echoes of Eternity" is a compelling and thought-provoking album, skillfully crafted by the renowned artist, Seraphina Rivers. \
This captivating musical collection takes listeners on an introspective journey, delving into the depths of the human experience \
and the vastness of the universe. With her mesmerizing vocals and poignant songwriting, Seraphina Rivers infuses each track with \
raw emotion and a sense of cosmic wonder. The album features several standout songs, including the hauntingly beautiful "Stardust \
Serenade," a celestial ballad that lasts for six minutes, carrying listeners through a celestial dreamscape. "Eclipse of the Soul" \
captivates with its enchanting melodies and spans over eight minutes, inviting introspection and contemplation. Another gem, "Infinity \
Embrace," unfolds like a cosmic odyssey, lasting nearly ten minutes, drawing listeners deeper into its ethereal atmosphere. "Echoes of Eternity" \
is a masterful testament to Seraphina Rivers' artistic prowess, leaving an enduring impact on all who embark on this musical voyage through \
time and space.
"""
)

```

output = program( text=""" "Echoes of Eternity" is a compelling and thought-provoking album, skillfully crafted by the renowned artist, Seraphina Rivers. \ This captivating musical collection takes listeners on an introspective journey, delving into the depths of the human experience \ and the vastness of the universe. With her mesmerizing vocals and poignant songwriting, Seraphina Rivers infuses each track with \ raw emotion and a sense of cosmic wonder. The album features several standout songs, including the hauntingly beautiful "Stardust \ Serenade," a celestial ballad that lasts for six minutes, carrying listeners through a celestial dreamscape. "Eclipse of the Soul" \ captivates with its enchanting melodies and spans over eight minutes, inviting introspection and contemplation. Another gem, "Infinity \ Embrace," unfolds like a cosmic odyssey, lasting nearly ten minutes, drawing listeners deeper into its ethereal atmosphere. "Echoes of Eternity" \ is a masterful testament to Seraphina Rivers' artistic prowess, leaving an enduring impact on all who embark on this musical voyage through \ time and space. """ )
```
Function call: Album with args: {'name': 'Echoes of Eternity', 'artist': 'Seraphina Rivers', 'songs': [{'title': 'Stardust Serenade', 'length_mins': 6}, {'title': 'Eclipse of the Soul', 'length_mins': 8}, {'title': 'Infinity Embrace', 'length_mins': 10}]}

```

In [ ]:
Copied!
```
output

```

output
Out[ ]:
```
Album(name='Echoes of Eternity', artist='Seraphina Rivers', songs=[Song(title='Stardust Serenade', length_mins=6), Song(title='Eclipse of the Soul', length_mins=8), Song(title='Infinity Embrace', length_mins=10)])
```

