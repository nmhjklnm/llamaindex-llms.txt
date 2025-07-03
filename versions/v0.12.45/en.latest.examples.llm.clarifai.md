![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Clarifai LLM¶
## Example notebook to call different LLM models using Clarifai¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-clarifai

```

%pip install llama-index-llms-clarifai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
Install clarifai
In [ ]:
Copied!
```
!pip install clarifai

```

!pip install clarifai
Set clarifai PAT as environment variable.
In [ ]:
Copied!
```
import os

os.environ["CLARIFAI_PAT"] = "<YOUR CLARIFAI PAT>"

```

import os os.environ["CLARIFAI_PAT"] = ""
Import clarifai package
In [ ]:
Copied!
```
from llama_index.llms.clarifai import Clarifai

```

from llama_index.llms.clarifai import Clarifai
Explore various models according to your prefrence from Our Models page
In [ ]:
Copied!
```
# Example parameters
params = dict(
    user_id="clarifai",
    app_id="ml",
    model_name="llama2-7b-alternative-4k",
    model_url=(
        "https://clarifai.com/clarifai/ml/models/llama2-7b-alternative-4k"
    ),
)

```

# Example parameters params = dict( user_id="clarifai", app_id="ml", model_name="llama2-7b-alternative-4k", model_url=( "https://clarifai.com/clarifai/ml/models/llama2-7b-alternative-4k" ), )
Initialize the LLM
In [ ]:
Copied!
```
# Method:1 using model_url parameter
llm_model = Clarifai(model_url=params["model_url"])

```

# Method:1 using model_url parameter llm_model = Clarifai(model_url=params["model_url"])
In [ ]:
Copied!
```
# Method:2 using model_name, app_id & user_id parameters
llm_model = Clarifai(
    model_name=params["model_name"],
    app_id=params["app_id"],
    user_id=params["user_id"],
)

```

# Method:2 using model_name, app_id & user_id parameters llm_model = Clarifai( model_name=params["model_name"], app_id=params["app_id"], user_id=params["user_id"], )
Call `complete` function
In [ ]:
Copied!
```
llm_reponse = llm_model.complete(
    prompt="write a 10 line rhyming poem about science"
)

```

llm_reponse = llm_model.complete( prompt="write a 10 line rhyming poem about science" )
In [ ]:
Copied!
```
print(llm_reponse)

```

print(llm_reponse)
```
.
Science is fun, it's true!
From atoms to galaxies, it's all new!
With experiments and tests, we learn so fast,
And discoveries come from the past.
It helps us understand the world around,
And makes our lives more profound.
So let's embrace this wondrous art,
And see where it takes us in the start!

```

Call `chat` function
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(role="user", content="write about climate change in 50 lines")
]
Response = llm_model.chat(messages)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage(role="user", content="write about climate change in 50 lines") ] Response = llm_model.chat(messages)
In [ ]:
Copied!
```
print(Response)

```

print(Response)
```
user:  or less.
Climate change is a serious threat to our planet and its inhabitants. Rising temperatures are causing extreme weather events, such as hurricanes, droughts, and wildfires. Sea levels are rising, threatening coastal communities and ecosystems. The melting of polar ice caps is disrupting global navigation and commerce. Climate change is also exacerbating air pollution, which can lead to respiratory problems and other health issues. It's essential that we take action now to reduce greenhouse gas emissions and transition to renewable energy sources to mitigate the worst effects of climate change.

```

### Using Inference parameters¶
Alternatively you can call models with inference parameters.
In [ ]:
Copied!
```
# Here is an inference parameter example for GPT model.
inference_params = dict(temperature=str(0.3), max_tokens=20)

```

# Here is an inference parameter example for GPT model. inference_params = dict(temperature=str(0.3), max_tokens=20)
In [ ]:
Copied!
```
llm_reponse = llm_model.complete(
    prompt="What is nuclear fission and fusion?",
    inference_params=params,
)

```

llm_reponse = llm_model.complete( prompt="What is nuclear fission and fusion?", inference_params=params, )
In [ ]:
Copied!
```
messages = [ChatMessage(role="user", content="Explain about the big bang")]
Response = llm_model.chat(messages, inference_params=params)

```

messages = [ChatMessage(role="user", content="Explain about the big bang")] Response = llm_model.chat(messages, inference_params=params)
