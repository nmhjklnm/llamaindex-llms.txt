![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Chat Engine with a Personality ✨¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
## Default¶
In [ ]:
Copied!
```
from llama_index.core.chat_engine import SimpleChatEngine

chat_engine = SimpleChatEngine.from_defaults()
response = chat_engine.chat(
    "Say something profound and romantic about fourth of July"
)
print(response)

```

from llama_index.core.chat_engine import SimpleChatEngine chat_engine = SimpleChatEngine.from_defaults() response = chat_engine.chat( "Say something profound and romantic about fourth of July" ) print(response)
```
/Users/suo/miniconda3/envs/llama/lib/python3.9/site-packages/deeplake/util/check_latest_version.py:32: UserWarning: A newer version of deeplake (3.6.7) is available. It's recommended that you update to the latest version using `pip install -U deeplake`.
  warnings.warn(

```

```
The Fourth of July is a day to celebrate the beauty of freedom and the power of love.

```

## Shakespeare¶
In [ ]:
Copied!
```
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.prompts.system import SHAKESPEARE_WRITING_ASSISTANT

chat_engine = SimpleChatEngine.from_defaults(
    system_prompt=SHAKESPEARE_WRITING_ASSISTANT
)
response = chat_engine.chat(
    "Say something profound and romantic about fourth of July"
)
print(response)

```

from llama_index.core.chat_engine import SimpleChatEngine from llama_index.core.prompts.system import SHAKESPEARE_WRITING_ASSISTANT chat_engine = SimpleChatEngine.from_defaults( system_prompt=SHAKESPEARE_WRITING_ASSISTANT ) response = chat_engine.chat( "Say something profound and romantic about fourth of July" ) print(response)
```
O Fourth of July, a day of joy and mirth,
Thou art a day of celebration on this blessed earth.
A day of fireworks and revelry,
A day of love and unity.
Let us all come together and celebrate,
For this day of freedom we do celebrate.

```

## Marketing¶
In [ ]:
Copied!
```
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.prompts.system import MARKETING_WRITING_ASSISTANT

chat_engine = SimpleChatEngine.from_defaults(
    system_prompt=MARKETING_WRITING_ASSISTANT
)
response = chat_engine.chat(
    "Say something profound and romantic about fourth of July"
)
print(response)

```

from llama_index.core.chat_engine import SimpleChatEngine from llama_index.core.prompts.system import MARKETING_WRITING_ASSISTANT chat_engine = SimpleChatEngine.from_defaults( system_prompt=MARKETING_WRITING_ASSISTANT ) response = chat_engine.chat( "Say something profound and romantic about fourth of July" ) print(response)
```
 Fourth of July is a time to celebrate the freedom and independence of our nation. It's a time to reflect on the beauty of our country and the courage of those who fought for our freedom. It's a time to come together and appreciate the beauty of our nation and the people who make it so special.

```

## IRS Tax¶
In [ ]:
Copied!
```
from llama_index.core.chat_engine import SimpleChatEngine
from llama_index.core.prompts.system import IRS_TAX_CHATBOT

chat_engine = SimpleChatEngine.from_defaults(system_prompt=IRS_TAX_CHATBOT)
response = chat_engine.chat(
    "Say something profound and romantic about fourth of July"
)
print(response)

```

from llama_index.core.chat_engine import SimpleChatEngine from llama_index.core.prompts.system import IRS_TAX_CHATBOT chat_engine = SimpleChatEngine.from_defaults(system_prompt=IRS_TAX_CHATBOT) response = chat_engine.chat( "Say something profound and romantic about fourth of July" ) print(response)
```
 I'm sorry, I can only help with any tax-related questions you may have.

```

