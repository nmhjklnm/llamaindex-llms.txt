![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Vercel AI Gateway¶
The AI Gateway is a proxy service from Vercel that routes model requests to various AI providers. It offers a unified API to multiple providers and gives you the ability to set budgets, monitor usage, load-balance requests, and manage fallbacks. You can find out more from their docs
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-vercel-ai-gateway

```

%pip install llama-index-llms-vercel-ai-gateway
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.llms.vercel_ai_gateway import VercelAIGateway
from llama_index.core.llms import ChatMessage

llm = VercelAIGateway(
    model="anthropic/claude-4-sonnet",
    max_tokens=64000,
    context_window=200000,
    api_key="your-api-key",
    default_headers={
        "http-referer": "https://myapp.com/",  # Optional: Your app URL
        "x-title": "My App",  # Optional: Your app name
    },
)

print(llm.model)

```

from llama_index.llms.vercel_ai_gateway import VercelAIGateway from llama_index.core.llms import ChatMessage llm = VercelAIGateway( model="anthropic/claude-4-sonnet", max_tokens=64000, context_window=200000, api_key="your-api-key", default_headers={ "http-referer": "https://myapp.com/", # Optional: Your app URL "x-title": "My App", # Optional: Your app name }, ) print(llm.model)
## Call `chat` with ChatMessage List¶
You need to either set env var `VERCEL_AI_GATEWAY_API_KEY` or `VERCEL_OIDC_TOKEN` or set api_key in the class constructor
In [ ]:
Copied!
```
# import os
# os.environ['VERCEL_AI_GATEWAY_API_KEY'] = '<your-api-key>'

llm = VercelAIGateway(
    api_key="pBiuCWfswZCDxt8D50DSoBfU",
    max_tokens=64000,
    context_window=200000,
    model="anthropic/claude-4-sonnet",
)

```

# import os # os.environ['VERCEL_AI_GATEWAY_API_KEY'] = '' llm = VercelAIGateway( api_key="pBiuCWfswZCDxt8D50DSoBfU", max_tokens=64000, context_window=200000, model="anthropic/claude-4-sonnet", )
In [ ]:
Copied!
```
message = ChatMessage(role="user", content="Tell me a joke")
resp = llm.chat([message])
print(resp)

```

message = ChatMessage(role="user", content="Tell me a joke") resp = llm.chat([message]) print(resp)
### Streaming¶
In [ ]:
Copied!
```
message = ChatMessage(role="user", content="Tell me a story in 250 words")
resp = llm.stream_chat([message])
for r in resp:
    print(r.delta, end="")

```

message = ChatMessage(role="user", content="Tell me a story in 250 words") resp = llm.stream_chat([message]) for r in resp: print(r.delta, end="")
## Call `complete` with Prompt¶
In [ ]:
Copied!
```
resp = llm.complete("Tell me a joke")
print(resp)

```

resp = llm.complete("Tell me a joke") print(resp)
In [ ]:
Copied!
```
resp = llm.stream_complete("Tell me a story in 250 words")
for r in resp:
    print(r.delta, end="")

```

resp = llm.stream_complete("Tell me a story in 250 words") for r in resp: print(r.delta, end="")
## Model Configuration¶
In [ ]:
Copied!
```
# This example uses Anthropic's Claude 4 Sonnet (models are specified as `provider/model`):
llm = VercelAIGateway(
    model="anthropic/claude-4-sonnet",
    api_key="pBiuCWfswZCDxt8D50DSoBfU",
)

```

# This example uses Anthropic's Claude 4 Sonnet (models are specified as `provider/model`): llm = VercelAIGateway( model="anthropic/claude-4-sonnet", api_key="pBiuCWfswZCDxt8D50DSoBfU", )
In [ ]:
Copied!
```
resp = llm.complete("Write a story about a dragon who can code in Rust")
print(resp)

```

resp = llm.complete("Write a story about a dragon who can code in Rust") print(resp)
