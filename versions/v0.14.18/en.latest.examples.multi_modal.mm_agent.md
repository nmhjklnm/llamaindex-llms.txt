# [Beta] Multi-modal ReAct Agent¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In this tutorial we show you how to construct a multi-modal ReAct agent.
This is an agent that can take in both text and images as the input task definition, and go through chain-of-thought + tool use to try to solve the task.
This is implemented with our lower-level Agent API, allowing us to explicitly step through the ReAct loop to show you what's happening in each step.
We show two use cases:
  1. **RAG Agent** : Given text/images, can query a RAG pipeline to lookup the answers. (given a screenshot from OpenAI Dev Day 2023)
  2. **Web Agent** : Given text/images, can query a web tool to lookup relevant information from the web (given a picture of shoes).


**NOTE** : This is explicitly a beta feature, the abstractions will likely change over time!
**NOTE** : This currently only works with GPT-4V.
## Augment Image Analysis with a RAG Pipeline¶
In this section we create a multimodal agent equipped with a RAG Tool.
### Setup Data¶
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-readers-web
%pip install llama-index-multi-modal-llms-openai
%pip install llama-index-tools-metaphor

```

%pip install llama-index-llms-openai %pip install llama-index-readers-web %pip install llama-index-multi-modal-llms-openai %pip install llama-index-tools-metaphor
In [ ]:
Copied!
```
# download images we'll use to run queries later
!wget "https://images.openai.com/blob/a2e49de2-ba5b-4869-9c2d-db3b4b5dcc19/new-models-and-developer-products-announced-at-devday.jpg?width=2000" -O other_images/openai/dev_day.png
!wget "https://drive.google.com/uc\?id\=1B4f5ZSIKN0zTTPPRlZ915Ceb3_uF9Zlq\&export\=download" -O other_images/adidas.png

```

# download images we'll use to run queries later !wget "https://images.openai.com/blob/a2e49de2-ba5b-4869-9c2d-db3b4b5dcc19/new-models-and-developer-products-announced-at-devday.jpg?width=2000" -O other_images/openai/dev_day.png !wget "https://drive.google.com/uc\?id\=1B4f5ZSIKN0zTTPPRlZ915Ceb3_uF9Zlq\&export\=download" -O other_images/adidas.png
```
--2024-01-02 20:25:25--  https://images.openai.com/blob/a2e49de2-ba5b-4869-9c2d-db3b4b5dcc19/new-models-and-developer-products-announced-at-devday.jpg?width=2000
Resolving images.openai.com (images.openai.com)... 2606:4700:4400::6812:28cd, 2606:4700:4400::ac40:9333, 172.64.147.51, ...
Connecting to images.openai.com (images.openai.com)|2606:4700:4400::6812:28cd|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 300894 (294K) [image/jpeg]
Saving to: ‘other_images/openai/dev_day.png’

other_images/openai 100%[===================>] 293.84K  --.-KB/s    in 0.02s   

2024-01-02 20:25:25 (13.8 MB/s) - ‘other_images/openai/dev_day.png’ saved [300894/300894]


```

In [ ]:
Copied!
```
from llama_index.readers.web import SimpleWebPageReader

url = "https://openai.com/blog/new-models-and-developer-products-announced-at-devday"
reader = SimpleWebPageReader(html_to_text=True)
documents = reader.load_data(urls=[url])

```

from llama_index.readers.web import SimpleWebPageReader url = "https://openai.com/blog/new-models-and-developer-products-announced-at-devday" reader = SimpleWebPageReader(html_to_text=True) documents = reader.load_data(urls=[url])
### Setup Tools¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata

```

from llama_index.llms.openai import OpenAI from llama_index.core import VectorStoreIndex from llama_index.core.tools import QueryEngineTool, ToolMetadata
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")

```

from llama_index.core import Settings Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
In [ ]:
Copied!
```
vector_index = VectorStoreIndex.from_documents(
    documents,
)

```

vector_index = VectorStoreIndex.from_documents( documents, )
In [ ]:
Copied!
```
query_tool = QueryEngineTool(
    query_engine=vector_index.as_query_engine(),
    metadata=ToolMetadata(
        name=f"vector_tool",
        description=(
            "Useful to lookup new features announced by OpenAI"
            # "Useful to lookup any information regarding the image"
        ),
    ),
)

```

query_tool = QueryEngineTool( query_engine=vector_index.as_query_engine(), metadata=ToolMetadata( name=f"vector_tool", description=( "Useful to lookup new features announced by OpenAI" # "Useful to lookup any information regarding the image" ), ), )
### Setup Agent¶
In [ ]:
Copied!
```
from llama_index.core.agent.react_multimodal.step import (
    MultimodalReActAgentWorker,
)
from llama_index.core.multi_modal_llms import MultiModalLLM
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.agent import Task

mm_llm = OpenAIMultiModal(model="gpt-4o", max_new_tokens=1000)

# Option 2: Initialize with OpenAIAgentWorker
react_step_engine = MultimodalReActAgentWorker.from_tools(
    [query_tool],
    # [],
    multi_modal_llm=mm_llm,
    verbose=True,
)
agent = react_step_engine.as_agent()

```

from llama_index.core.agent.react_multimodal.step import ( MultimodalReActAgentWorker, ) from llama_index.core.multi_modal_llms import MultiModalLLM from llama_index.multi_modal_llms.openai import OpenAIMultiModal from llama_index.core.agent import Task mm_llm = OpenAIMultiModal(model="gpt-4o", max_new_tokens=1000) # Option 2: Initialize with OpenAIAgentWorker react_step_engine = MultimodalReActAgentWorker.from_tools( [query_tool], # [], multi_modal_llm=mm_llm, verbose=True, ) agent = react_step_engine.as_agent()
In [ ]:
Copied!
```
query_str = (
    "The photo shows some new features released by OpenAI. "
    "Can you pinpoint the features in the photo and give more details using relevant tools?"
)

from llama_index.core.schema import ImageDocument

# image document
image_document = ImageDocument(image_path="other_images/openai/dev_day.png")

task = agent.create_task(
    query_str,
    extra_state={"image_docs": [image_document]},
)

```

query_str = ( "The photo shows some new features released by OpenAI. " "Can you pinpoint the features in the photo and give more details using relevant tools?" ) from llama_index.core.schema import ImageDocument # image document image_document = ImageDocument(image_path="other_images/openai/dev_day.png") task = agent.create_task( query_str, extra_state={"image_docs": [image_document]}, )
In [ ]:
Copied!
```
from llama_index.core.agent import AgentRunner


def execute_step(agent: AgentRunner, task: Task):
    step_output = agent.run_step(task.task_id)
    if step_output.is_last:
        response = agent.finalize_response(task.task_id)
        print(f"> Agent finished: {str(response)}")
        return response
    else:
        return None


def execute_steps(agent: AgentRunner, task: Task):
    response = execute_step(agent, task)
    while response is None:
        response = execute_step(agent, task)
    return response

```

from llama_index.core.agent import AgentRunner def execute_step(agent: AgentRunner, task: Task): step_output = agent.run_step(task.task_id) if step_output.is_last: response = agent.finalize_response(task.task_id) print(f"> Agent finished: {str(response)}") return response else: return None def execute_steps(agent: AgentRunner, task: Task): response = execute_step(agent, task) while response is None: response = execute_step(agent, task) return response
In [ ]:
Copied!
```
# Run this and not the below if you just want to run everything at once.
# response = execute_steps(agent, task)

```

# Run this and not the below if you just want to run everything at once. # response = execute_steps(agent, task)
In [ ]:
Copied!
```
response = execute_step(agent, task)

```

response = execute_step(agent, task)
```
Thought: I need to use a tool to help me identify the new features released by OpenAI as shown in the photo.
Action: vector_tool
Action Input: {'input': 'new features released by OpenAI'}
Observation: OpenAI has released several new features, including the GPT-4 Turbo model, the Assistants API, and multimodal capabilities. The GPT-4 Turbo model is more capable, cheaper, and supports a 128K context window. The Assistants API makes it easier for developers to build their own assistive AI apps with goals and the ability to call models and tools. The multimodal capabilities include vision, image creation (DALLÂ·E 3), and text-to-speech (TTS). These new features are being rolled out to OpenAI customers starting at 1pm PT today.

```

In [ ]:
Copied!
```
response = execute_step(agent, task)

```

response = execute_step(agent, task)
```
Thought: The observation provided information about the new features released by OpenAI, which I can now relate to the image provided.
Response: The photo shows a user interface with a section titled "Playground" and several options such as "GPT-4.0-turbo," "Code Interpreter," "Translate," and "Chat." Based on the observation from the tool, these features are part of the new releases by OpenAI. Specifically, "GPT-4.0-turbo" likely refers to the GPT-4 Turbo model, which is a more capable and cost-effective version of the language model with a larger context window. The "Code Interpreter" could be related to the Assistants API, which allows developers to build AI apps that can interpret and execute code. The "Translate" and "Chat" options might be part of the multimodal capabilities, with "Translate" possibly involving text-to-text language translation and "Chat" involving conversational AI capabilities. The multimodal capabilities also include vision and image creation, which could be represented in the Playground interface but are not visible in the provided section of the photo.
> Agent finished: The photo shows a user interface with a section titled "Playground" and several options such as "GPT-4.0-turbo," "Code Interpreter," "Translate," and "Chat." Based on the observation from the tool, these features are part of the new releases by OpenAI. Specifically, "GPT-4.0-turbo" likely refers to the GPT-4 Turbo model, which is a more capable and cost-effective version of the language model with a larger context window. The "Code Interpreter" could be related to the Assistants API, which allows developers to build AI apps that can interpret and execute code. The "Translate" and "Chat" options might be part of the multimodal capabilities, with "Translate" possibly involving text-to-text language translation and "Chat" involving conversational AI capabilities. The multimodal capabilities also include vision and image creation, which could be represented in the Playground interface but are not visible in the provided section of the photo.

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The photo shows a user interface with a section titled "Playground" and several options such as "GPT-4.0-turbo," "Code Interpreter," "Translate," and "Chat." Based on the observation from the tool, these features are part of the new releases by OpenAI. Specifically, "GPT-4.0-turbo" likely refers to the GPT-4 Turbo model, which is a more capable and cost-effective version of the language model with a larger context window. The "Code Interpreter" could be related to the Assistants API, which allows developers to build AI apps that can interpret and execute code. The "Translate" and "Chat" options might be part of the multimodal capabilities, with "Translate" possibly involving text-to-text language translation and "Chat" involving conversational AI capabilities. The multimodal capabilities also include vision and image creation, which could be represented in the Playground interface but are not visible in the provided section of the photo.

```

## Augment Image Analysis with Web Search¶
In this example we show you how to setup a GPT-4V powered agent to lookup information on the web to help better explain a given image.
In [ ]:
Copied!
```
from llama_index.tools.metaphor import MetaphorToolSpec
from llama_index.core.agent.react_multimodal.step import (
    MultimodalReActAgentWorker,
)
from llama_index.core.agent import AgentRunner
from llama_index.core.multi_modal_llms import MultiModalLLM
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.agent import Task

metaphor_tool_spec = MetaphorToolSpec(
    api_key="<api_key>",
)
metaphor_tools = metaphor_tool_spec.to_tool_list()

```

from llama_index.tools.metaphor import MetaphorToolSpec from llama_index.core.agent.react_multimodal.step import ( MultimodalReActAgentWorker, ) from llama_index.core.agent import AgentRunner from llama_index.core.multi_modal_llms import MultiModalLLM from llama_index.multi_modal_llms.openai import OpenAIMultiModal from llama_index.core.agent import Task metaphor_tool_spec = MetaphorToolSpec( api_key="", ) metaphor_tools = metaphor_tool_spec.to_tool_list()
In [ ]:
Copied!
```
mm_llm = OpenAIMultiModal(model="gpt-4o", max_new_tokens=1000)

# Option 2: Initialize with OpenAIAgentWorker
react_step_engine = MultimodalReActAgentWorker.from_tools(
    metaphor_tools,
    # [],
    multi_modal_llm=mm_llm,
    verbose=True,
)
agent = react_step_engine.as_agent()

```

mm_llm = OpenAIMultiModal(model="gpt-4o", max_new_tokens=1000) # Option 2: Initialize with OpenAIAgentWorker react_step_engine = MultimodalReActAgentWorker.from_tools( metaphor_tools, # [], multi_modal_llm=mm_llm, verbose=True, ) agent = react_step_engine.as_agent()
In [ ]:
Copied!
```
from llama_index.core.schema import ImageDocument

query_str = "Look up some reviews regarding these shoes."
image_document = ImageDocument(image_path="other_images/adidas.png")

task = agent.create_task(
    query_str, extra_state={"image_docs": [image_document]}
)

```

from llama_index.core.schema import ImageDocument query_str = "Look up some reviews regarding these shoes." image_document = ImageDocument(image_path="other_images/adidas.png") task = agent.create_task( query_str, extra_state={"image_docs": [image_document]} )
In [ ]:
Copied!
```
response = execute_step(agent, task)

```

response = execute_step(agent, task)
```
Thought: The image shows a pair of shoes from a website that appears to be selling them. The user is asking for reviews of these shoes, but the image does not provide specific details such as the brand or model name. I will need to use a search tool to find reviews based on the visual information provided.
Action: search
Action Input: {'query': 'reviews for yellow and white running shoes with black stripes'}
[Metaphor Tool] Autoprompt: Here is a review for a great pair of yellow and white running shoes with black stripes:
Observation: [{'title': '| On', 'url': 'https://www.on-running.com/en-us/', 'id': 'bO8WCIY4qIAlfi5MbHMw7A'}, {'title': 'ASICS Gel Nimbus 21 Review 2023, Facts, Deals ($81)', 'url': 'https://runrepeat.com/asics-gel-nimbus-21', 'id': 'l-1YebY9dIRt1d8MeHyaBg'}, {'title': 'ASICS UK | Official Running Shoes & Clothing | ASICS', 'url': 'https://www.asics.com/gb/en-gb/', 'id': 'aAY5Tpax5jevadvNMj34_w'}, {'title': 'Asics Gel Nimbus', 'url': 'https://www.thepeacefulrunner.com/asics-gel-nimbus.html', 'id': 'l8joVUIb-c6H5BTKqu7fJw'}, {'title': 'hoka clifton', 'url': 'https://www.zappos.com/hoka-clifton?PID=3428536&AID=11554337&splash=none&cjevent=65a454d2018811ed82ca7c440a82b82a&zap_placement=', 'id': 'iPqidPvLy-wt02B9GdgG8g'}, {'title': '| On United States', 'url': 'https://www.on-running.com/en-us/shop?utm_source=facebook&utm_medium=post&utm_campaign=cloud_x_w45&utm_content=launch', 'id': 'pUaSVBqAbU-VNvj0KEkNlw'}, {'title': 'Shoe Review: Skechers GORun Speed Elite Hyper', 'url': 'https://athleticsillustrated.com/shoe-review-skechers-gorun-speed-elite-hyper/', 'id': 'B3ijN8qSaV1eBkoOCeV9yw'}, {'title': 'Saucony Running Shoes & Running Apparel | Saucony.com', 'url': 'https://www.saucony.com/en/country', 'id': 'ng-HmN8CxK2TAKmA9gPLTg'}, {'title': 'The entire Kalenji range and training plans on Kalenji.co.uk - Shoes, clothing and accessories for running and trail running.', 'url': 'https://www.kalenji.co.uk/', 'id': 'SHrJYCGb5g9yoehuu8zOzg'}, {'title': 'ONEMIX Men Running Shoes Trainers Comfortable Damping Outdoor Athletic Vulcanized Tennis Shoes Trail Sneakers', 'url': 'https://usa.banggood.com/ONEMIX-Men-Running-Shoes-Trainers-Comfortable-Damping-Outdoor-Athletic-Vulcanized-Tennis-Shoes-Trail-Sneakers-p-1745312.html?imageAb=2&p=H320105094792201606N&akmClientCountry=America&a=1675672269.4621&akmClientCountry=America', 'id': 'Dh81GLQU2gi4Efc2z8ZzYA'}]

```

In [ ]:
Copied!
```
response = execute_step(agent, task)

```

response = execute_step(agent, task)
```
Thought: The search results returned a variety of shoe brands and models, but none of them seem to match the specific shoes in the image. To find reviews for the exact shoes, I need more information about the brand or model. Since the image shows a website interface with the brand likely being "UltraBOOST 1.0 DNA" and a discount code "CYBER," I can use this information to refine my search for reviews.
Action: search
Action Input: {'query': 'UltraBOOST 1.0 DNA shoes reviews'}
[Metaphor Tool] Autoprompt: Here is a review of the UltraBOOST 1.0 DNA shoes:
Observation: [{'title': 'Shoe', 'url': 'https://therunningclinic.com/shoe/?id=81645', 'id': 'SR5Ar004nuT97AkWDTdekg'}, {'title': 'Shoe', 'url': 'https://therunningclinic.com/shoe/?id=81644', 'id': 'kiEvTAolb2Kh4OrvSxnqUA'}, {'title': 'On Cloudboom Review', 'url': 'https://www.doctorsofrunning.com/2020/12/on-cloudboom-review.html', 'id': 'J3ARnLPH1KWzrIdGogwxnw'}, {'title': 'Adidas UltraBOOST 5.0 DNA Glow now available', 'url': 'https://dlmag.com/adidas-ultraboost-5-0-dna-glow-now-available', 'id': 'wljZXtnx28OF5YtEXcbwXg'}, {'title': 'Ultraboost 19 Review in 2020 (comparison)', 'url': 'https://www.youtube.com/watch?v=n9_23gq7ER0&amp;t=6s', 'id': 'B3QWxLBJgA9FR6HRmOnW2A'}, {'title': 'Adidas ULTRABOOST LIGHT : Detailed First Impressions', 'url': 'https://www.youtube.com/watch?v=780bVc3yjsk', 'id': 'LOUPO-1rU2tZJd31YFYYXA'}, {'title': 'Adidas Ultraboost Review : 7 pros, 2 cons (2023)', 'url': 'https://runrepeat.com/adidas-ultra-boost', 'id': 'Xqa5dR7IR24En7uL5BCTEg'}, {'title': 'VLOG # 999 | The MOST *Challenging* Running SHOE of 2018', 'url': 'https://www.youtube.com/watch?v=3KWIWLtyrSw', 'id': 'avKLkDhnPT3eTwAvI6Wi7g'}, {'title': 'NEW ARRIVALS', 'url': 'http://www.adidasultraboost.us.org/', 'id': 'NhKaTjMI_rIIS0tWLrJXAA'}, {'title': 'Brooks Hyperion Tempo Review (2020: Better Late Than Never)', 'url': 'https://www.doctorsofrunning.com/2023/01/brooks-hyperion-tempo-review-2020.html', 'id': '3U7runLSyYNIBlRHETTWCA'}]

```

In [ ]:
Copied!
```
# output is hidden because too long
response = execute_step(agent, task)

```

# output is hidden because too long response = execute_step(agent, task)
In [ ]:
Copied!
```
response = execute_step(agent, task)

```

response = execute_step(agent, task)
```
Thought: I can answer without using any more tools.
Response: The Adidas Ultraboost is reviewed as an expensive but versatile shoe suitable for various activities, from running a half marathon to going out on a date. They are considered a good value due to their durability, with the reviewer getting hundreds of miles out of them. The shoes are described as lightweight, breathable, and comfortable enough to wear without socks. However, they are not recommended for wet climates as they do not perform well in the rain. The reviewer also mentions owning seven different models of Adidas Boost, indicating a strong preference for the brand.
> Agent finished: The Adidas Ultraboost is reviewed as an expensive but versatile shoe suitable for various activities, from running a half marathon to going out on a date. They are considered a good value due to their durability, with the reviewer getting hundreds of miles out of them. The shoes are described as lightweight, breathable, and comfortable enough to wear without socks. However, they are not recommended for wet climates as they do not perform well in the rain. The reviewer also mentions owning seven different models of Adidas Boost, indicating a strong preference for the brand.

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The Adidas Ultraboost is reviewed as an expensive but versatile shoe suitable for various activities, from running a half marathon to going out on a date. They are considered a good value due to their durability, with the reviewer getting hundreds of miles out of them. The shoes are described as lightweight, breathable, and comfortable enough to wear without socks. However, they are not recommended for wet climates as they do not perform well in the rain. The reviewer also mentions owning seven different models of Adidas Boost, indicating a strong preference for the brand.

```

