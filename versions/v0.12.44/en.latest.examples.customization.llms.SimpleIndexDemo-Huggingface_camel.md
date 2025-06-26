![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# HuggingFace LLM - Camel-5b¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-huggingface

```

%pip install llama-index-llms-huggingface
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import Settings

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.llms.huggingface import HuggingFaceLLM from llama_index.core import Settings
```
INFO:numexpr.utils:Note: NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
Note: NumExpr detected 16 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
INFO:numexpr.utils:NumExpr defaulting to 8 threads.
NumExpr defaulting to 8 threads.

```

```
/home/loganm/miniconda3/envs/gpt_index/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

#### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
#### Load documents, build the VectorStoreIndex¶
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
# setup prompts - specific to StableLM
from llama_index.core import PromptTemplate

# This will wrap the default prompts that are internal to llama-index
# taken from https://huggingface.co/Writer/camel-5b-hf
query_wrapper_prompt = PromptTemplate(
    "Below is an instruction that describes a task. "
    "Write a response that appropriately completes the request.\n\n"
    "### Instruction:\n{query_str}\n\n### Response:"
)

```

# setup prompts - specific to StableLM from llama_index.core import PromptTemplate # This will wrap the default prompts that are internal to llama-index # taken from https://huggingface.co/Writer/camel-5b-hf query_wrapper_prompt = PromptTemplate( "Below is an instruction that describes a task. " "Write a response that appropriately completes the request.\n\n" "### Instruction:\n{query_str}\n\n### Response:" )
In [ ]:
Copied!
```
import torch

llm = HuggingFaceLLM(
    context_window=2048,
    max_new_tokens=256,
    generate_kwargs={"temperature": 0.25, "do_sample": False},
    query_wrapper_prompt=query_wrapper_prompt,
    tokenizer_name="Writer/camel-5b-hf",
    model_name="Writer/camel-5b-hf",
    device_map="auto",
    tokenizer_kwargs={"max_length": 2048},
    # uncomment this if using CUDA to reduce memory usage
    # model_kwargs={"torch_dtype": torch.float16}
)

Settings.chunk_size = 512
Settings.llm = llm

```

import torch llm = HuggingFaceLLM( context_window=2048, max_new_tokens=256, generate_kwargs={"temperature": 0.25, "do_sample": False}, query_wrapper_prompt=query_wrapper_prompt, tokenizer_name="Writer/camel-5b-hf", model_name="Writer/camel-5b-hf", device_map="auto", tokenizer_kwargs={"max_length": 2048}, # uncomment this if using CUDA to reduce memory usage # model_kwargs={"torch_dtype": torch.float16} ) Settings.chunk_size = 512 Settings.llm = llm
```
Loading checkpoint shards: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:43<00:00, 14.34s/it]

```

In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 27212 tokens
> [build_index_from_nodes] Total embedding token usage: 27212 tokens

```

#### Query Index¶
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?")
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 8 tokens
> [retrieve] Total embedding token usage: 8 tokens

```

```
Token indices sequence length is longer than the specified maximum sequence length for this model (954 > 512). Running this sequence through the model will result in indexing errors
Setting `pad_token_id` to `eos_token_id`:50256 for open-end generation.

```

```
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 1026 tokens
> [get_response] Total LLM token usage: 1026 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The author grew up in a small town in England, attended a prestigious private school, and then went to Cambridge University, where he studied computer science. Afterward, he worked on web infrastructure, wrote essays, and then realized he could write about startups. He then started giving talks, wrote a book, and started interviewing founders for a book on startups.

```

#### Query Index - Streaming¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(streaming=True)

```

query_engine = index.as_query_engine(streaming=True)
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
response_stream = query_engine.query("What did the author do growing up?")

```

# set Logging to DEBUG for more detailed outputs response_stream = query_engine.query("What did the author do growing up?")
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 8 tokens
> [retrieve] Total embedding token usage: 8 tokens

```

```
Setting `pad_token_id` to `eos_token_id`:50256 for open-end generation.

```

```
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 0 tokens
> [get_response] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
# can be slower to start streaming since llama-index often involves many LLM calls
response_stream.print_response_stream()

```

# can be slower to start streaming since llama-index often involves many LLM calls response_stream.print_response_stream()
```
The author grew up in a small town in England, attended a prestigious private school, and then went to Cambridge University, where he studied computer science. Afterward, he worked on web infrastructure, wrote essays, and then realized he could write about startups. He then started giving talks, wrote a book, and started interviewing founders for a book on startups.<|endoftext|>
```

In [ ]:
Copied!
```
# can also get a normal response object
response = response_stream.get_response()
print(response)

```

# can also get a normal response object response = response_stream.get_response() print(response)
In [ ]:
Copied!
```
# can also iterate over the generator yourself
generated_text = ""
for text in response.response_gen:
    generated_text += text

```

# can also iterate over the generator yourself generated_text = "" for text in response.response_gen: generated_text += text
