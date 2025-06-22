![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Hugging Face LLMs¶
There are many ways to interface with LLMs from Hugging Face. Hugging Face itself provides several Python packages to enable access, which LlamaIndex wraps into `LLM` entities:
  * The `transformers` package: use `llama_index.llms.HuggingFaceLLM`
  * The Hugging Face Inference API, wrapped by `huggingface_hub[inference]`: use `llama_index.llms.HuggingFaceInferenceAPI`


There are _many_ possible permutations of these two, so this notebook only details a few. Let's use Hugging Face's Text Generation task as our example.
In the below line, we install the packages necessary for this demo:
  * `transformers[torch]` is needed for `HuggingFaceLLM`
  * `huggingface_hub[inference]` is needed for `HuggingFaceInferenceAPI`
  * The quotes are needed for Z shell (`zsh`)


In [ ]:
Copied!
```
%pip install llama-index-llms-huggingface
%pip install llama-index-llms-huggingface-api

```

%pip install llama-index-llms-huggingface %pip install llama-index-llms-huggingface-api
In [ ]:
Copied!
```
!pip install "transformers[torch]" "huggingface_hub[inference]"

```

!pip install "transformers[torch]" "huggingface_hub[inference]"
Now that we're set up, let's play around:
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import os
from typing import List, Optional

from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI

# SEE: https://huggingface.co/docs/hub/security-tokens
# We just need a token with read permissions for this demo
HF_TOKEN: Optional[str] = os.getenv("HUGGING_FACE_TOKEN")
# NOTE: None default will fall back on Hugging Face's token storage
# when this token gets used within HuggingFaceInferenceAPI

```

import os from typing import List, Optional from llama_index.llms.huggingface import HuggingFaceLLM from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI # SEE: https://huggingface.co/docs/hub/security-tokens # We just need a token with read permissions for this demo HF_TOKEN: Optional[str] = os.getenv("HUGGING_FACE_TOKEN") # NOTE: None default will fall back on Hugging Face's token storage # when this token gets used within HuggingFaceInferenceAPI
In [ ]:
Copied!
```
# This uses https://huggingface.co/HuggingFaceH4/zephyr-7b-alpha
# downloaded (if first invocation) to the local Hugging Face model cache,
# and actually runs the model on your local machine's hardware
locally_run = HuggingFaceLLM(model_name="HuggingFaceH4/zephyr-7b-alpha")

# This will use the same model, but run remotely on Hugging Face's servers,
# accessed via the Hugging Face Inference API
# Note that using your token will not charge you money,
# the Inference API is free it just has rate limits
remotely_run = HuggingFaceInferenceAPI(
    model_name="HuggingFaceH4/zephyr-7b-alpha", token=HF_TOKEN
)

# Or you can skip providing a token, using Hugging Face Inference API anonymously
remotely_run_anon = HuggingFaceInferenceAPI(
    model_name="HuggingFaceH4/zephyr-7b-alpha"
)

# If you don't provide a model_name to the HuggingFaceInferenceAPI,
# Hugging Face's recommended model gets used (thanks to huggingface_hub)
remotely_run_recommended = HuggingFaceInferenceAPI(token=HF_TOKEN)

# You can also connect to a model being served by a local or remote
# Text Generation Inference server
tgi_server = HuggingFaceInferenceAPI(model="http://localhost:8080")

```

# This uses https://huggingface.co/HuggingFaceH4/zephyr-7b-alpha # downloaded (if first invocation) to the local Hugging Face model cache, # and actually runs the model on your local machine's hardware locally_run = HuggingFaceLLM(model_name="HuggingFaceH4/zephyr-7b-alpha") # This will use the same model, but run remotely on Hugging Face's servers, # accessed via the Hugging Face Inference API # Note that using your token will not charge you money, # the Inference API is free it just has rate limits remotely_run = HuggingFaceInferenceAPI( model_name="HuggingFaceH4/zephyr-7b-alpha", token=HF_TOKEN ) # Or you can skip providing a token, using Hugging Face Inference API anonymously remotely_run_anon = HuggingFaceInferenceAPI( model_name="HuggingFaceH4/zephyr-7b-alpha" ) # If you don't provide a model_name to the HuggingFaceInferenceAPI, # Hugging Face's recommended model gets used (thanks to huggingface_hub) remotely_run_recommended = HuggingFaceInferenceAPI(token=HF_TOKEN) # You can also connect to a model being served by a local or remote # Text Generation Inference server tgi_server = HuggingFaceInferenceAPI(model="http://localhost:8080")
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
