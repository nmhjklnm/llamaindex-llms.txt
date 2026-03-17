# Build with RichPromptTemplate¶
Introduced in `llama-index-core==0.12.27`, `RichPromptTemplate` is a new prompt template that allows you to build prompts with rich formatting using Jinja syntax.
Using this, you can build:
  * basic prompts with variables
  * chat prompt templates in a single string
  * prompts that accept text, images, and audio
  * advanced prompts that loop or parse objects
  * and more!


Let's look at some examples.
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
## Basic Prompt with Variables¶
In `RichPromptTemplate`, you can use the `{{ }}` syntax to insert variables into your prompt.
In [ ]:
Copied!
```
from llama_index.core.prompts import RichPromptTemplate

prompt = RichPromptTemplate("Hello, {{ name }}!")

```

from llama_index.core.prompts import RichPromptTemplate prompt = RichPromptTemplate("Hello, {{ name }}!")
You can format the prompt into either a string or list of chat messages.
In [ ]:
Copied!
```
print(prompt.format(name="John"))

```

print(prompt.format(name="John"))
```
Hello, John!

```

In [ ]:
Copied!
```
print(prompt.format_messages(name="John"))

```

print(prompt.format_messages(name="John"))
```
[ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text='Hello, John!')])]

```

## Chat Prompt Templates¶
You can also define chat message blocks directly in the prompt template.
In [ ]:
Copied!
```
prompt = RichPromptTemplate(
    """
{% chat role="system" %}
You are now chatting with {{ user }}
{% endchat %}

{% chat role="user" %}
{{ user_msg }}
{% endchat %}
"""
)

```

prompt = RichPromptTemplate( """ {% chat role="system" %} You are now chatting with {{ user }} {% endchat %} {% chat role="user" %} {{ user_msg }} {% endchat %} """ )
In [ ]:
Copied!
```
print(prompt.format_messages(user="John", user_msg="Hello!"))

```

print(prompt.format_messages(user="John", user_msg="Hello!"))
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text='You are now chatting with John')]), ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text='Hello!')])]

```

## Prompts with Images and Audio¶
Assuming the LLM you are using supports it, you can also include images and audio in your prompts!
### Images¶
In [ ]:
Copied!
```
!wget https://cdn.pixabay.com/photo/2016/07/07/16/46/dice-1502706_640.jpg -O image.png

```

!wget https://cdn.pixabay.com/photo/2016/07/07/16/46/dice-1502706_640.jpg -O image.png
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o-mini", api_key="sk-...")

prompt = RichPromptTemplate(
    """
Describe the following image:
{{ image_path | image}}
"""
)

```

from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-4o-mini", api_key="sk-...") prompt = RichPromptTemplate( """ Describe the following image: {{ image_path | image}} """ )
In [ ]:
Copied!
```
messages = prompt.format_messages(image_path="./image.png")
response = llm.chat(messages)
print(response.message.content)

```

messages = prompt.format_messages(image_path="./image.png") response = llm.chat(messages) print(response.message.content)
```
The image features three white dice with black dots, captured in a monochrome setting. The dice are positioned on a checkered surface, which appears to be a wooden board. The background is blurred, creating a sense of depth, while the focus remains on the dice. The overall composition emphasizes the randomness and chance associated with rolling dice.

```

### Audio¶
In [ ]:
Copied!
```
!wget AUDIO_URL = "https://science.nasa.gov/wp-content/uploads/2024/04/sounds-of-mars-one-small-step-earth.wav" -O audio.wav

```

!wget AUDIO_URL = "https://science.nasa.gov/wp-content/uploads/2024/04/sounds-of-mars-one-small-step-earth.wav" -O audio.wav
In [ ]:
Copied!
```
prompt = RichPromptTemplate(
    """
Describe the following audio:
{{ audio_path | audio }}
"""
)
messages = prompt.format_messages(audio_path="./audio.wav")

```

prompt = RichPromptTemplate( """ Describe the following audio: {{ audio_path | audio }} """ ) messages = prompt.format_messages(audio_path="./audio.wav")
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4o-audio-preview", api_key="sk-...")
response = llm.chat(messages)
print(response.message.content)

```

llm = OpenAI(model="gpt-4o-audio-preview", api_key="sk-...") response = llm.chat(messages) print(response.message.content)
```
The audio features a famous quote, "That's one small step for man, one giant leap for mankind." This statement was made during a significant historical event, symbolizing a monumental achievement for humanity.

```

## [Advanced] Loops and Objects¶
Now, we can take this a step further. Lets assume we have a list of images and text that we want to include in our prompt.
We can use the `{% for x in y %}` loop syntax to loop through the list and include the images and text in our prompt.
In [ ]:
Copied!
```
text_and_images = [
    ("This is a test", "./image.png"),
    ("This is another test", "./image.png"),
]

prompt = RichPromptTemplate(
    """
{% for text, image_path in text_and_images %}
Here is some text:
{{ text }}
Here is an image:
{{ image_path | image }}
{% endfor %}
"""
)

messages = prompt.format_messages(text_and_images=text_and_images)

```

text_and_images = [ ("This is a test", "./image.png"), ("This is another test", "./image.png"), ] prompt = RichPromptTemplate( """ {% for text, image_path in text_and_images %} Here is some text: {{ text }} Here is an image: {{ image_path | image }} {% endfor %} """ ) messages = prompt.format_messages(text_and_images=text_and_images)
Lets inspect the messages to see what we have.
In [ ]:
Copied!
```
for message in messages:
    print(message.role.value)
    for block in message.blocks:
        print(str(block)[:100])
    print("\n")

```

for message in messages: print(message.role.value) for block in message.blocks: print(str(block)[:100]) print("\n")
```
user
block_type='text' text='Here is some text:'
block_type='text' text='This is a test'
block_type='text' text='Here is an image:'
block_type='image' image=None path=None url=AnyUrl('data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABA
block_type='text' text='Here is some text:'
block_type='text' text='This is another test'
block_type='text' text='Here is an image:'
block_type='image' image=None path=None url=AnyUrl('data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABA



```

As you can see, we have a single message with a list of blocks, each representing a new block of content (text or image).
(Note: the images are resolved as base64 encoded strings when rendering the prompt)
