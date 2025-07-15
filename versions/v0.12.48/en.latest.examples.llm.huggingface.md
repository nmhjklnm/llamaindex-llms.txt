![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Hugging Face LLMs¶
There are many ways to interface with LLMs from Hugging Face, either locally or via Hugging Face's Inference Providers. Hugging Face itself provides several Python packages to enable access, which LlamaIndex wraps into `LLM` entities:
  * The `transformers` package: use `llama_index.llms.HuggingFaceLLM`
  * The Hugging Face Inference Providers, wrapped by `huggingface_hub[inference]`: use `llama_index.llms.HuggingFaceInferenceAPI`


There are _many_ possible permutations of these two, so this notebook only details a few. Let's use Hugging Face's Text Generation task as our example.
In the below line, we install the packages necessary for this demo:
  * `transformers[torch]` is needed for `HuggingFaceLLM`
  * `huggingface_hub[inference]` is needed for `HuggingFaceInferenceAPI`
  * The quotes are needed for Z shell (`zsh`)


In [ ]:
Copied!
```
%pip install llama-index-llms-huggingface # for local inference
%pip install llama-index-llms-huggingface-api # for remote inference

```

%pip install llama-index-llms-huggingface # for local inference %pip install llama-index-llms-huggingface-api # for remote inference
In [ ]:
Copied!
```
!pip install "transformers[torch]" "huggingface_hub[inference]"

```

!pip install "transformers[torch]" "huggingface_hub[inference]"
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
Now that we're set up, let's play around:
# Setup Hugging Face Account¶
First, you need to create a Hugging Face account and get a token. You can sign up here. Then you'll need to create a token here.
```
export HUGGING_FACE_TOKEN=hf_your_token_here

```

In [ ]:
Copied!
```
import os
from typing import List, Optional

from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI

HF_TOKEN: Optional[str] = os.getenv("HUGGING_FACE_TOKEN")
# NOTE: None default will fall back on Hugging Face's token storage
# when this token gets used within HuggingFaceInferenceAPI

```

import os from typing import List, Optional from llama_index.llms.huggingface import HuggingFaceLLM from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI HF_TOKEN: Optional[str] = os.getenv("HUGGING_FACE_TOKEN") # NOTE: None default will fall back on Hugging Face's token storage # when this token gets used within HuggingFaceInferenceAPI
## Use a model via Inference Providers¶
The easiest way to use an open source model is to use the Hugging Face Inference Providers. Let's use the DeepSeek R1 model, which is great for complex tasks.
With inference providers, you can use the model on serverless infrastructure from inference providers.
In [ ]:
Copied!
```
remotely_run = HuggingFaceInferenceAPI(
    model_name="deepseek-ai/DeepSeek-R1-0528",
    token=HF_TOKEN,
    provider="auto",  # this will use the best provider available
)

```

remotely_run = HuggingFaceInferenceAPI( model_name="deepseek-ai/DeepSeek-R1-0528", token=HF_TOKEN, provider="auto", # this will use the best provider available )
We can also specify our preferred inference provider. Let's use the `together` provider.
In [ ]:
Copied!
```
remotely_run = HuggingFaceInferenceAPI(
    model_name="Qwen/Qwen3-235B-A22B",
    token=HF_TOKEN,
    provider="together",  # this will use the best provider available
)

```

remotely_run = HuggingFaceInferenceAPI( model_name="Qwen/Qwen3-235B-A22B", token=HF_TOKEN, provider="together", # this will use the best provider available )
## Use an open source model locally¶
First, we'll use an open source model that's optimized for local inference. This model is downloaded (if first invocation) to the local Hugging Face model cache, and actually runs the model on your local machine's hardware.
We'll use the Gemma 3N E4B model, which is optimized for local inference.
In [ ]:
Copied!
```
locally_run = HuggingFaceLLM(model_name="google/gemma-3n-E4B-it")

```

locally_run = HuggingFaceLLM(model_name="google/gemma-3n-E4B-it")
## Use a dedicated Inference Endpoint¶
We can also spin up a dedicated Inference Endpoint for a model and use that to run the model.
In [ ]:
Copied!
```
endpoint_server = HuggingFaceInferenceAPI(
    model="https://(<your-endpoint>.eu-west-1.aws.endpoints.huggingface.cloud"
)

```

endpoint_server = HuggingFaceInferenceAPI( model="https://(.eu-west-1.aws.endpoints.huggingface.cloud" )
## Use a local inference engine (vLLM or TGI)¶
We can also use a local inference engine like vLLM or TGI to run the model.
In [ ]:
Copied!
```
# You can also connect to a model being served by a local or remote
# Text Generation Inference server
tgi_server = HuggingFaceInferenceAPI(model="http://localhost:8080")

```

# You can also connect to a model being served by a local or remote # Text Generation Inference server tgi_server = HuggingFaceInferenceAPI(model="http://localhost:8080")
Underlying a completion with `HuggingFaceInferenceAPI` is Hugging Face's Text Generation task.
In [ ]:
Copied!
```
completion_response = remotely_run_recommended.complete("To infinity, and")
print(completion_response)

```

completion_response = remotely_run_recommended.complete("To infinity, and") print(completion_response)
```
 beyond!
The Infinity Wall Clock is a unique and stylish way to keep track of time. The clock is made of a durable, high-quality plastic and features a bright LED display. The Infinity Wall Clock is powered by batteries and can be mounted on any wall. It is a great addition to any home or office.

```

## Setting a tokenizer¶
If you are modifying the LLM, you should also change the global tokenizer to match!
In [ ]:
Copied!
```
from llama_index.core import set_global_tokenizer
from transformers import AutoTokenizer

set_global_tokenizer(
    AutoTokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-alpha").encode
)

```

from llama_index.core import set_global_tokenizer from transformers import AutoTokenizer set_global_tokenizer( AutoTokenizer.from_pretrained("HuggingFaceH4/zephyr-7b-alpha").encode )
If you're curious, other Hugging Face Inference API tasks wrapped are:
  * `llama_index.llms.HuggingFaceInferenceAPI.chat`: Conversational task
  * `llama_index.embeddings.HuggingFaceInferenceAPIEmbedding`: Feature Extraction task


And yes, Hugging Face embedding models are supported with:
  * `transformers[torch]`: wrapped by `HuggingFaceEmbedding`
  * `huggingface_hub[inference]`: wrapped by `HuggingFaceInferenceAPIEmbedding`


Both of the above two subclass `llama_index.embeddings.base.BaseEmbedding`.
