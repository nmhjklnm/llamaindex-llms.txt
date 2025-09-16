![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Chat Engine - Simple Mode REPL¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
### Get started in 3 lines of code¶
Using GPT3 ("text-davinci-003")
In [ ]:
Copied!
```
from llama_index.core.chat_engine import SimpleChatEngine

chat_engine = SimpleChatEngine.from_defaults()
chat_engine.chat_repl()

```

from llama_index.core.chat_engine import SimpleChatEngine chat_engine = SimpleChatEngine.from_defaults() chat_engine.chat_repl()
```
Assistant: Hi there! How can I help you?


```

```
Human:  Tell me a joke

```

```
Assistant: Why did the chicken cross the playground?
To get to the other slide!


```

```
Human:  That's not funny

```

```
Assistant: I'm sorry you didn't find it funny. Is there something else I can help you with?


```

```
Human:  Tell me another one

```

```
Assistant: Why did the scarecrow win the Nobel Prize?
Because he was outstanding in his field!


```

```
Human:  Still not funny, sing me a song

```

```
Assistant: Oh, I'm a lumberjack and I'm okay
I sleep all night and I work all day
I cut down trees, I eat my lunch
I go to the lavatory on Wednesday and Saturday
Everybody knows my song!


```

```
Human:  exit

```

### Customize LLM¶
Use ChatGPT ("gpt-3.5-turbo")
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo")

```

from llama_index.llms.openai import OpenAI llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo")
In [ ]:
Copied!
```
from llama_index.core.chat_engine import SimpleChatEngine

chat_engine = SimpleChatEngine.from_defaults(llm=llm)
chat_engine.chat_repl()

```

from llama_index.core.chat_engine import SimpleChatEngine chat_engine = SimpleChatEngine.from_defaults(llm=llm) chat_engine.chat_repl()
```
model='gpt-3.5-turbo' temperature=0.0 max_tokens=None additional_kwargs={} max_retries=10
===== Entering Chat REPL =====
Type "exit" to exit.


```

```
Human:  Hi

```

```
Assistant: Hello! How can I assist you today?


```

```
Human:  Tell me a joke

```

```
Assistant: Sure, here's a joke for you:

Why don't scientists trust atoms?

Because they make up everything!


```

```
Human:  That's not funny

```

```
Assistant: I apologize if the joke didn't meet your expectations. Humor can be subjective, and what one person finds funny, another may not. Is there anything else I can assist you with?


```

```
Human:  Tell me another one

```

```
Assistant: Of course! Here's another joke for you:

Why don't skeletons fight each other?

They don't have the guts!


```

```
Human:  Still not funny, sing me a song

```

```
Assistant: Certainly! Here's a little song for you:

(Verse 1)
In a world of endless possibilities,
I'll sing a song to bring you some ease.
With melodies that dance upon the air,
I hope this tune will show you I care.

(Chorus)
La la la, a melody so sweet,
La la la, let the music take the lead.
Close your eyes and let your worries fade,
As I sing this song, a serenade.

(Verse 2)
Through the highs and lows, the ups and downs,
I'll sing a song to turn your frown around.
With harmonies that lift your spirits high,
I hope this melody will make you sigh.

(Chorus)
La la la, a melody so sweet,
La la la, let the music take the lead.
Close your eyes and let your worries fade,
As I sing this song, a serenade.

(Outro)
So let the music fill your heart and soul,
As I sing this song, let your worries go.
May this melody bring you joy and cheer,
And remind you that I'm always here.

I hope you enjoyed the song! Let me know if there's anything else I can do for you.


```

```
Human:  exit

```

## Streaming Support¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo-0613")

```

from llama_index.llms.openai import OpenAI llm = OpenAI(temperature=0.0, model="gpt-3.5-turbo-0613")
In [ ]:
Copied!
```
from llama_index.core.chat_engine import SimpleChatEngine

chat_engine = SimpleChatEngine.from_defaults(llm=llm)

```

from llama_index.core.chat_engine import SimpleChatEngine chat_engine = SimpleChatEngine.from_defaults(llm=llm)
In [ ]:
Copied!
```
response = chat_engine.stream_chat(
    "Write me a poem about raining cats and dogs."
)
for token in response.response_gen:
    print(token, end="")

```

response = chat_engine.stream_chat( "Write me a poem about raining cats and dogs." ) for token in response.response_gen: print(token, end="")
```
In a world where whimsy takes its flight,
Where dreams and reality intertwine,
A tale unfolds, both strange and bright,
Of raining cats and dogs, so divine.

From the heavens, a tempest brews,
Clouds gather, dark and thick,
And as the wind begins to choose,
The sky releases a whimsical trick.

Down they fall, with paws and tails,
Cats and dogs, in a watery dance,
Tiny meows and barks prevail,
As they descend in a wild romance.

The felines, graceful, land with poise,
Their fur glistening, sleek and fine,
With eyes that gleam like emerald joys,
They prance and purr, in a feline line.

The canines, playful, splash and bound,
Their wagging tails a joyful sight,
With tongues that pant and ears that sound,
They frolic and bark, with all their might.

Together they create a symphony,
A chorus of meows and barks,
A spectacle for all to see,
As they dance upon the parks.

Children giggle, adults stare,
Amazed by this peculiar sight,
For in this moment, they're all aware,
Of the magic raining from the height.

And as the storm begins to wane,
The cats and dogs return above,
Leaving behind a world untamed,
A memory of a rain so rare and of love.

So, let us cherish this whimsical tale,
Of raining cats and dogs, so grand,
For in the extraordinary, we prevail,
And find enchantment in the palm of our hand.
```

