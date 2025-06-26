![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Multi-Modal LLM using NVIDIA endpoints for image reasoning¶
In this notebook, we show how to use NVIDIA MultiModal LLM class/abstraction for image understanding/reasoning.
We also show several functions we are now supporting for NVIDIA LLM:
  * `complete` (both sync and async): for a single prompt and list of images
  * `stream complete` (both sync and async): for steaming output of complete


In [ ]:
Copied!
```
%pip install --upgrade --quiet llama-index-multi-modal-llms-nvidia llama-index-embeddings-nvidia llama-index-readers-file

```

%pip install --upgrade --quiet llama-index-multi-modal-llms-nvidia llama-index-embeddings-nvidia llama-index-readers-file
In [ ]:
Copied!
```
import getpass
import os

# del os.environ['NVIDIA_API_KEY']  ## delete key and reset
if os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
    print("Valid NVIDIA_API_KEY already in environment. Delete to reset")
else:
    nvapi_key = getpass.getpass("NVAPI Key (starts with nvapi-): ")
    assert nvapi_key.startswith(
        "nvapi-"
    ), f"{nvapi_key[:5]}... is not a valid key"
    os.environ["NVIDIA_API_KEY"] = nvapi_key

```

import getpass import os # del os.environ['NVIDIA_API_KEY'] ## delete key and reset if os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"): print("Valid NVIDIA_API_KEY already in environment. Delete to reset") else: nvapi_key = getpass.getpass("NVAPI Key (starts with nvapi-): ") assert nvapi_key.startswith( "nvapi-" ), f"{nvapi_key[:5]}... is not a valid key" os.environ["NVIDIA_API_KEY"] = nvapi_key
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from llama_index.multi_modal_llms.nvidia import NVIDIAMultiModal
import base64
from llama_index.core.schema import ImageDocument
from PIL import Image
import requests
from io import BytesIO

# import matplotlib.pyplot as plt
from llama_index.core.multi_modal_llms.generic_utils import load_image_urls

llm = NVIDIAMultiModal()

```

from llama_index.multi_modal_llms.nvidia import NVIDIAMultiModal import base64 from llama_index.core.schema import ImageDocument from PIL import Image import requests from io import BytesIO # import matplotlib.pyplot as plt from llama_index.core.multi_modal_llms.generic_utils import load_image_urls llm = NVIDIAMultiModal()
## Initialize `NVIDIAMultiModal` and Load Images from URLs¶
In [ ]:
Copied!
```
image_urls = [
    "https://res.cloudinary.com/hello-tickets/image/upload/c_limit,f_auto,q_auto,w_1920/v1640835927/o3pfl41q7m5bj8jardk0.jpg",
    "https://www.visualcapitalist.com/wp-content/uploads/2023/10/US_Mortgage_Rate_Surge-Sept-11-1.jpg",
    "https://www.sportsnet.ca/wp-content/uploads/2023/11/CP1688996471-1040x572.jpg",
    # Add yours here!
]

img_response = requests.get(image_urls[0])
img = Image.open(BytesIO(img_response.content))
# plt.imshow(img)

image_url_documents = load_image_urls(image_urls)

```

image_urls = [ "https://res.cloudinary.com/hello-tickets/image/upload/c_limit,f_auto,q_auto,w_1920/v1640835927/o3pfl41q7m5bj8jardk0.jpg", "https://www.visualcapitalist.com/wp-content/uploads/2023/10/US_Mortgage_Rate_Surge-Sept-11-1.jpg", "https://www.sportsnet.ca/wp-content/uploads/2023/11/CP1688996471-1040x572.jpg", # Add yours here! ] img_response = requests.get(image_urls[0]) img = Image.open(BytesIO(img_response.content)) # plt.imshow(img) image_url_documents = load_image_urls(image_urls)
### Complete a prompt with a bunch of images¶
In [ ]:
Copied!
```
response = llm.complete(
    prompt=f"What is this image?",
    image_documents=image_url_documents,
)

print(response)

```

response = llm.complete( prompt=f"What is this image?", image_documents=image_url_documents, ) print(response)
In [ ]:
Copied!
```
await llm.acomplete(
    prompt="tell me about this image",
    image_documents=image_url_documents,
)

```

await llm.acomplete( prompt="tell me about this image", image_documents=image_url_documents, )
### Steam Complete a prompt with a bunch of images¶
In [ ]:
Copied!
```
stream_complete_response = llm.stream_complete(
    prompt=f"What is this image?",
    image_documents=image_url_documents,
)

```

stream_complete_response = llm.stream_complete( prompt=f"What is this image?", image_documents=image_url_documents, )
In [ ]:
Copied!
```
for r in stream_complete_response:
    print(r.text, end="")

```

for r in stream_complete_response: print(r.text, end="")
In [ ]:
Copied!
```
stream_complete_response = await llm.astream_complete(
    prompt=f"What is this image?",
    image_documents=image_url_documents,
)

```

stream_complete_response = await llm.astream_complete( prompt=f"What is this image?", image_documents=image_url_documents, )
In [ ]:
Copied!
```
last_element = None
async for last_element in stream_complete_response:
    pass

print(last_element)

```

last_element = None async for last_element in stream_complete_response: pass print(last_element)
## Passing an image as a base64 encoded string¶
In [ ]:
Copied!
```
imgr_content = base64.b64encode(
    requests.get(
        "https://helloartsy.com/wp-content/uploads/kids/cats/how-to-draw-a-small-cat/how-to-draw-a-small-cat-step-6.jpg"
    ).content
).decode("utf-8")

llm.complete(
    prompt="List models in image",
    image_documents=[ImageDocument(image=imgr_content, mimetype="jpeg")],
)

```

imgr_content = base64.b64encode( requests.get( "https://helloartsy.com/wp-content/uploads/kids/cats/how-to-draw-a-small-cat/how-to-draw-a-small-cat-step-6.jpg" ).content ).decode("utf-8") llm.complete( prompt="List models in image", image_documents=[ImageDocument(image=imgr_content, mimetype="jpeg")], )
## Passing an image as an NVCF asset¶
If your image is sufficiently large or you will pass it multiple times in a chat conversation, you may upload it once and reference it in your chat conversation
See https://docs.nvidia.com/cloud-functions/user-guide/latest/cloud-function/assets.html for details about how upload the image.
In [ ]:
Copied!
```
import requests

content_type = "image/jpg"
description = "example-image-from-lc-nv-ai-e-notebook"

create_response = requests.post(
    "https://api.nvcf.nvidia.com/v2/nvcf/assets",
    headers={
        "Authorization": f"Bearer {os.environ['NVIDIA_API_KEY']}",
        "accept": "application/json",
        "Content-Type": "application/json",
    },
    json={"contentType": content_type, "description": description},
)
create_response.raise_for_status()

upload_response = requests.put(
    create_response.json()["uploadUrl"],
    headers={
        "Content-Type": content_type,
        "x-amz-meta-nvcf-asset-description": description,
    },
    data=img_response.content,
)
upload_response.raise_for_status()

asset_id = create_response.json()["assetId"]
asset_id

```

import requests content_type = "image/jpg" description = "example-image-from-lc-nv-ai-e-notebook" create_response = requests.post( "https://api.nvcf.nvidia.com/v2/nvcf/assets", headers={ "Authorization": f"Bearer {os.environ['NVIDIA_API_KEY']}", "accept": "application/json", "Content-Type": "application/json", }, json={"contentType": content_type, "description": description}, ) create_response.raise_for_status() upload_response = requests.put( create_response.json()["uploadUrl"], headers={ "Content-Type": content_type, "x-amz-meta-nvcf-asset-description": description, }, data=img_response.content, ) upload_response.raise_for_status() asset_id = create_response.json()["assetId"] asset_id
In [ ]:
Copied!
```
response = llm.stream_complete(
    prompt=f"Describe the image",
    image_documents=[
        ImageDocument(metadata={"asset_id": asset_id}, mimetype="png")
    ],
)

```

response = llm.stream_complete( prompt=f"Describe the image", image_documents=[ ImageDocument(metadata={"asset_id": asset_id}, mimetype="png") ], )
In [ ]:
Copied!
```
for r in response:
    print(r.text, end="")

```

for r in response: print(r.text, end="")
## Passing images from local files¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

# put your local directore here
image_documents = SimpleDirectoryReader("./tests/data/").load_data()

llm.complete(
    prompt="Describe the images as an alternative text",
    image_documents=image_documents,
)

```

from llama_index.core import SimpleDirectoryReader # put your local directore here image_documents = SimpleDirectoryReader("./tests/data/").load_data() llm.complete( prompt="Describe the images as an alternative text", image_documents=image_documents, )
### Chat with of images¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

llm.chat(
    [
        ChatMessage(
            role="user",
            content=[
                {"type": "text", "text": "Describe this image:"},
                {"type": "image_url", "image_url": image_urls[1]},
            ],
        )
    ]
)

```

from llama_index.core.llms import ChatMessage llm.chat( [ ChatMessage( role="user", content=[ {"type": "text", "text": "Describe this image:"}, {"type": "image_url", "image_url": image_urls[1]}, ], ) ] )
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

await llm.achat(
    [
        ChatMessage(
            role="user",
            content=[
                {"type": "text", "text": "Describe this image:"},
                {"type": "image_url", "image_url": image_urls[1]},
            ],
        )
    ]
)

```

from llama_index.core.llms import ChatMessage await llm.achat( [ ChatMessage( role="user", content=[ {"type": "text", "text": "Describe this image:"}, {"type": "image_url", "image_url": image_urls[1]}, ], ) ] )
In [ ]:
Copied!
```
llm.chat(
    [
        ChatMessage(
            role="user",
            content=[
                {"type": "text", "text": "Describe the image"},
                {
                    "type": "image_url",
                    "image_url": f'<img src="data:{content_type};asset_id,{asset_id}" />',
                },
            ],
        )
    ]
)

```

llm.chat( [ ChatMessage( role="user", content=[ {"type": "text", "text": "Describe the image"}, { "type": "image_url", "image_url": f'![No description has been provided for this image](data:{content_type};asset_id,{asset_id})', }, ], ) ] )
In [ ]:
Copied!
```
await llm.achat(
    [
        ChatMessage(
            role="user",
            content=[
                {"type": "text", "text": "Describe the image"},
                {
                    "type": "image_url",
                    "image_url": f'<img src="data:{content_type};asset_id,{asset_id}" />',
                },
            ],
        )
    ]
)

```

await llm.achat( [ ChatMessage( role="user", content=[ {"type": "text", "text": "Describe the image"}, { "type": "image_url", "image_url": f'![No description has been provided for this image](data:{content_type};asset_id,{asset_id})', }, ], ) ] )
### Stream Chat a prompt with images¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

streaming_resp = llm.stream_chat(
    [
        ChatMessage(
            role="user",
            content=[
                {"type": "text", "text": "Describe this image:"},
                {"type": "image_url", "image_url": image_urls[1]},
            ],
        )
    ]
)

```

from llama_index.core.llms import ChatMessage streaming_resp = llm.stream_chat( [ ChatMessage( role="user", content=[ {"type": "text", "text": "Describe this image:"}, {"type": "image_url", "image_url": image_urls[1]}, ], ) ] )
In [ ]:
Copied!
```
for r in streaming_resp:
    print(r.delta, end="")

```

for r in streaming_resp: print(r.delta, end="")
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

resp = await llm.astream_chat(
    [
        ChatMessage(
            role="user",
            content=[
                {"type": "text", "text": "Describe this image:"},
                {"type": "image_url", "image_url": image_urls[0]},
            ],
        )
    ]
)

```

from llama_index.core.llms import ChatMessage resp = await llm.astream_chat( [ ChatMessage( role="user", content=[ {"type": "text", "text": "Describe this image:"}, {"type": "image_url", "image_url": image_urls[0]}, ], ) ] )
In [ ]:
Copied!
```
last_element = None
async for last_element in resp:
    pass

print(last_element)

```

last_element = None async for last_element in resp: pass print(last_element)
In [ ]:
Copied!
```
response = llm.stream_chat(
    [
        ChatMessage(
            role="user",
            content=f"""<img src="data:image/jpg;
            ,{asset_id}"/>""",
        )
    ]
)

```

response = llm.stream_chat( [ ChatMessage( role="user", content=f"""![No description has been provided for this image](data:image/jpg;%0A%20%20%20%20%20%20%20%20%20%20%20%20,{asset_id})""", ) ] )
In [ ]:
Copied!
```
for r in response:
    print(r.delta, end="")

```

for r in response: print(r.delta, end="")
