# Grok 4¶
Grok from xAI uses an OpenAI-compatible API, so you can use it with the OpenAILike integration class.
In [ ]:
Copied!
```
!pip install llama-index-llms-openai-like

```

!pip install llama-index-llms-openai-like
In [ ]:
Copied!
```
grok_api_key = "xai-xxxxxxxx"

```

grok_api_key = "xai-xxxxxxxx"
In [ ]:
Copied!
```
from llama_index.llms.openai_like import OpenAILike

llm = OpenAILike(
    model="grok-4-0709",
    api_base="https://api.x.ai/v1",
    api_key=grok_api_key,
    context_window=128000,
    is_chat_model=True,
    is_function_calling_model=False,
)

response = llm.complete("Hello World!")
print(str(response))

```

from llama_index.llms.openai_like import OpenAILike llm = OpenAILike( model="grok-4-0709", api_base="https://api.x.ai/v1", api_key=grok_api_key, context_window=128000, is_chat_model=True, is_function_calling_model=False, ) response = llm.complete("Hello World!") print(str(response))
```
Hello World! 🌍 That's the universal greeting for programmers everywhere. What adventure brings you here today? 😊

```

