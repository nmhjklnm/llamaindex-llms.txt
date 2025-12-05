![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Multi-Modal LLM using DashScope qwen-vl model for image reasoning¶
In this notebook, we show how to use DashScope qwen-vl MultiModal LLM class/abstraction for image understanding/reasoning. Async is not currently supported
We also show several functions we are now supporting for DashScope LLM:
  * `complete` (sync): for a single prompt and list of images
  * `chat` (sync): for multiple chat messages
  * `stream complete` (sync): for steaming output of complete
  * `stream chat` (sync): for steaming output of chat
  * multi round conversation.


In [ ]:
Copied!
```
!pip install -U llama-index-multi-modal-llms-dashscope

```

!pip install -U llama-index-multi-modal-llms-dashscope
## Use DashScope to understand Images from URLs¶
In [ ]:
Copied!
```
# Set API key
%env DASHSCOPE_API_KEY=YOUR_DASHSCOPE_API_KEY

```

# Set API key %env DASHSCOPE_API_KEY=YOUR_DASHSCOPE_API_KEY
## Initialize `DashScopeMultiModal` and Load Images from URLs¶
In [ ]:
Copied!
```
from llama_index.multi_modal_llms.dashscope import (
    DashScopeMultiModal,
    DashScopeMultiModalModels,
)

from llama_index.core.multi_modal_llms.generic_utils import load_image_urls


image_urls = [
    "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg",
]

image_documents = load_image_urls(image_urls)

dashscope_multi_modal_llm = DashScopeMultiModal(
    model_name=DashScopeMultiModalModels.QWEN_VL_MAX,
)

```

from llama_index.multi_modal_llms.dashscope import ( DashScopeMultiModal, DashScopeMultiModalModels, ) from llama_index.core.multi_modal_llms.generic_utils import load_image_urls image_urls = [ "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg", ] image_documents = load_image_urls(image_urls) dashscope_multi_modal_llm = DashScopeMultiModal( model_name=DashScopeMultiModalModels.QWEN_VL_MAX, )
### Complete a prompt with images¶
In [ ]:
Copied!
```
complete_response = dashscope_multi_modal_llm.complete(
    prompt="What's in the image?",
    image_documents=image_documents,
)
print(complete_response)

```

complete_response = dashscope_multi_modal_llm.complete( prompt="What's in the image?", image_documents=image_documents, ) print(complete_response)
```
The image captures a serene moment on a sandy beach at sunset. A woman, dressed in a blue and white plaid shirt, is seated on the ground. She is holding a treat in her hand, which is being gently taken by a dog. The dog, wearing a blue harness, is sitting next to the woman, its paw resting on her leg. The backdrop of this heartwarming scene is the vast ocean, with the sun setting in the distance, casting a warm glow over the entire landscape. The image beautifully encapsulates the bond between the woman and her dog, set against the tranquil beauty of nature.

```

In [ ]:
Copied!
```
### Complete a prompt with multi images
multi_image_urls = [
    "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg",
    "https://dashscope.oss-cn-beijing.aliyuncs.com/images/panda.jpeg",
]

multi_image_documents = load_image_urls(multi_image_urls)
complete_response = dashscope_multi_modal_llm.complete(
    prompt="What animals are in the pictures?",
    image_documents=multi_image_documents,
)
print(complete_response)

```

### Complete a prompt with multi images multi_image_urls = [ "https://dashscope.oss-cn-beijing.aliyuncs.com/images/dog_and_girl.jpeg", "https://dashscope.oss-cn-beijing.aliyuncs.com/images/panda.jpeg", ] multi_image_documents = load_image_urls(multi_image_urls) complete_response = dashscope_multi_modal_llm.complete( prompt="What animals are in the pictures?", image_documents=multi_image_documents, ) print(complete_response)
```
There is a dog in Picture 1, and there is a panda in Picture 2.

```

### Steam Complete a prompt with a bunch of images¶
In [ ]:
Copied!
```
stream_complete_response = dashscope_multi_modal_llm.stream_complete(
    prompt="What's in the image?",
    image_documents=image_documents,
)

for r in stream_complete_response:
    print(r.delta, end="")

```

stream_complete_response = dashscope_multi_modal_llm.stream_complete( prompt="What's in the image?", image_documents=image_documents, ) for r in stream_complete_response: print(r.delta, end="")
```
The image captures a serene moment on a sandy beach at sunset. A woman, dressed in a blue and white plaid shirt, is seated on the ground. She is holding a treat in her hand, which is being gently taken by a dog. The dog, wearing a blue harness, is sitting next to the woman, its paw resting on her leg. The backdrop of this heartwarming scene is the vast ocean, with the sun setting in the distance, casting a warm glow over the entire landscape. The image beautifully encapsulates the bond between the woman and her dog, set against the tranquil beauty of nature.
```

### multi round conversation with chat messages¶
In [ ]:
Copied!
```
from llama_index.core.base.llms.types import MessageRole
from llama_index.multi_modal_llms.dashscope.utils import (
    create_dashscope_multi_modal_chat_message,
)

chat_message_user_1 = create_dashscope_multi_modal_chat_message(
    "What's in the image?", MessageRole.USER, image_documents
)
chat_response = dashscope_multi_modal_llm.chat([chat_message_user_1])
print(chat_response.message.content[0]["text"])
chat_message_assistent_1 = create_dashscope_multi_modal_chat_message(
    chat_response.message.content[0]["text"], MessageRole.ASSISTANT, None
)
chat_message_user_2 = create_dashscope_multi_modal_chat_message(
    "what are they doing?", MessageRole.USER, None
)
chat_response = dashscope_multi_modal_llm.chat(
    [chat_message_user_1, chat_message_assistent_1, chat_message_user_2]
)
print(chat_response.message.content[0]["text"])

```

from llama_index.core.base.llms.types import MessageRole from llama_index.multi_modal_llms.dashscope.utils import ( create_dashscope_multi_modal_chat_message, ) chat_message_user_1 = create_dashscope_multi_modal_chat_message( "What's in the image?", MessageRole.USER, image_documents ) chat_response = dashscope_multi_modal_llm.chat([chat_message_user_1]) print(chat_response.message.content[0]["text"]) chat_message_assistent_1 = create_dashscope_multi_modal_chat_message( chat_response.message.content[0]["text"], MessageRole.ASSISTANT, None ) chat_message_user_2 = create_dashscope_multi_modal_chat_message( "what are they doing?", MessageRole.USER, None ) chat_response = dashscope_multi_modal_llm.chat( [chat_message_user_1, chat_message_assistent_1, chat_message_user_2] ) print(chat_response.message.content[0]["text"])
```
The image shows two photos of a panda sitting on a wooden log in an enclosure. In the top photo, the panda is sitting upright with its front paws on the log, facing three crows that are perched on the log. The panda looks alert and curious, while the crows seem to be observing the panda. In the bottom photo, the panda is lying down on the log, its head resting on its front paws. One crow has landed on the ground next to the log, and it seems to be interacting with the panda. The background of the photo shows green plants and a wire fence, creating a natural and relaxed atmosphere.
The woman is sitting on the beach with her dog, and they are giving each other high fives. The panda and the crows are sitting together on a log, and the panda seems to be communicating with the crows.

```

### Stream Chat through a list of chat messages¶
In [ ]:
Copied!
```
stream_chat_response = dashscope_multi_modal_llm.stream_chat(
    [chat_message_user_1, chat_message_assistent_1, chat_message_user_2]
)
for r in stream_chat_response:
    print(r.delta, end="")

```

stream_chat_response = dashscope_multi_modal_llm.stream_chat( [chat_message_user_1, chat_message_assistent_1, chat_message_user_2] ) for r in stream_chat_response: print(r.delta, end="")
```
The woman is sitting on the beach, holding a treat in her hand, while the dog is sitting next to her, taking the treat from her hand.
```

### Use images from local files¶
Use local file:  
Linux&mac file schema: file:///home/images/test.png  
Windows file schema: file://D:/images/abc.png
In [ ]:
Copied!
```
from llama_index.multi_modal_llms.dashscope.utils import load_local_images

local_images = [
    "file://THE_FILE_PATH1",
    "file://THE_FILE_PATH2",
]

image_documents = load_local_images(local_images)
chat_message_local = create_dashscope_multi_modal_chat_message(
    "What animals are in the pictures?", MessageRole.USER, image_documents
)
chat_response = dashscope_multi_modal_llm.chat([chat_message_local])
print(chat_response.message.content[0]["text"])

```

from llama_index.multi_modal_llms.dashscope.utils import load_local_images local_images = [ "file://THE_FILE_PATH1", "file://THE_FILE_PATH2", ] image_documents = load_local_images(local_images) chat_message_local = create_dashscope_multi_modal_chat_message( "What animals are in the pictures?", MessageRole.USER, image_documents ) chat_response = dashscope_multi_modal_llm.chat([chat_message_local]) print(chat_response.message.content[0]["text"])
```
There is a dog in Picture 1, and there is a panda in Picture 2.

```

