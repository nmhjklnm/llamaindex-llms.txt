![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# ModelScope LLMS¶
In this notebook, we show how to use the ModelScope LLM models in LlamaIndex. Check out the ModelScope site.
If you're opening this Notebook on colab, you will need to install LlamaIndex 🦙 and the modelscope.
In [ ]:
Copied!
```
!pip install llama-index-llms-modelscope

```

!pip install llama-index-llms-modelscope
## Basic Usage¶
In [ ]:
Copied!
```
import sys
from llama_index.llms.modelscope import ModelScopeLLM

llm = ModelScopeLLM(model_name="qwen/Qwen3-8B", model_revision="master")

rsp = llm.complete("Hello, who are you?")
print(rsp)

```

import sys from llama_index.llms.modelscope import ModelScopeLLM llm = ModelScopeLLM(model_name="qwen/Qwen3-8B", model_revision="master") rsp = llm.complete("Hello, who are you?") print(rsp)
#### Use Message request¶
In [ ]:
Copied!
```
from llama_index.core.base.llms.types import MessageRole, ChatMessage

messages = [
    ChatMessage(
        role=MessageRole.SYSTEM, content="You are a helpful assistant."
    ),
    ChatMessage(role=MessageRole.USER, content="How to make cake?"),
]
resp = llm.chat(messages)
print(resp)

```

from llama_index.core.base.llms.types import MessageRole, ChatMessage messages = [ ChatMessage( role=MessageRole.SYSTEM, content="You are a helpful assistant." ), ChatMessage(role=MessageRole.USER, content="How to make cake?"), ] resp = llm.chat(messages) print(resp)
