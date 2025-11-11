![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# HuggingFace LLM - StableLM¶
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
documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham").load_data()
In [ ]:
Copied!
```
# setup prompts - specific to StableLM
from llama_index.core import PromptTemplate

system_prompt = """<|SYSTEM|># StableLM Tuned (Alpha version)
- StableLM is a helpful and harmless open-source AI language model developed by StabilityAI.
- StableLM is excited to be able to help the user, but will refuse to do anything that could be considered harmful to the user.
- StableLM is more than just an information source, StableLM is also able to write poetry, short stories, and make jokes.
- StableLM will refuse to participate in anything that could harm a human.
"""

# This will wrap the default prompts that are internal to llama-index
query_wrapper_prompt = PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>")

```

# setup prompts - specific to StableLM from llama_index.core import PromptTemplate system_prompt = """<|SYSTEM|># StableLM Tuned (Alpha version) - StableLM is a helpful and harmless open-source AI language model developed by StabilityAI. - StableLM is excited to be able to help the user, but will refuse to do anything that could be considered harmful to the user. - StableLM is more than just an information source, StableLM is also able to write poetry, short stories, and make jokes. - StableLM will refuse to participate in anything that could harm a human. """ # This will wrap the default prompts that are internal to llama-index query_wrapper_prompt = PromptTemplate("<|USER|>{query_str}<|ASSISTANT|>")
In [ ]:
Copied!
```
import torch

llm = HuggingFaceLLM(
    context_window=4096,
    max_new_tokens=256,
    generate_kwargs={"temperature": 0.7, "do_sample": False},
    system_prompt=system_prompt,
    query_wrapper_prompt=query_wrapper_prompt,
    tokenizer_name="StabilityAI/stablelm-tuned-alpha-3b",
    model_name="StabilityAI/stablelm-tuned-alpha-3b",
    device_map="auto",
    stopping_ids=[50278, 50279, 50277, 1, 0],
    tokenizer_kwargs={"max_length": 4096},
    # uncomment this if using CUDA to reduce memory usage
    # model_kwargs={"torch_dtype": torch.float16}
)

Settings.llm = llm
Settings.chunk_size = 1024

```

import torch llm = HuggingFaceLLM( context_window=4096, max_new_tokens=256, generate_kwargs={"temperature": 0.7, "do_sample": False}, system_prompt=system_prompt, query_wrapper_prompt=query_wrapper_prompt, tokenizer_name="StabilityAI/stablelm-tuned-alpha-3b", model_name="StabilityAI/stablelm-tuned-alpha-3b", device_map="auto", stopping_ids=[50278, 50279, 50277, 1, 0], tokenizer_kwargs={"max_length": 4096}, # uncomment this if using CUDA to reduce memory usage # model_kwargs={"torch_dtype": torch.float16} ) Settings.llm = llm Settings.chunk_size = 1024
```
Loading checkpoint shards: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [00:24<00:00, 12.21s/it]

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
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 20729 tokens
> [build_index_from_nodes] Total embedding token usage: 20729 tokens

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
Setting `pad_token_id` to `eos_token_id`:0 for open-end generation.

```

```
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 2126 tokens
> [get_response] Total LLM token usage: 2126 tokens
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
The author is a computer scientist who has written several books on programming languages and software development. He worked on the IBM 1401 and wrote a program to calculate pi. He also wrote a program to predict how high a rocket ship would fly. The program was written in Fortran and used a TRS-80 microcomputer. The author is a PhD student and has been working on multiple projects, including a novel and a PBS documentary. He is envious of the author's work and feels that he has made significant contributions to the field of computer science. He is working on multiple projects and is envious of the author's work. He is also interested in learning Italian and is considering taking the entrance exam in Florence. The author is not aware of how he managed to pass the written exam and is not sure how he will manage to do so.

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
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 0 tokens

```

```
Setting `pad_token_id` to `eos_token_id`:0 for open-end generation.

```

```
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
The author is a computer scientist who has written several books on programming languages and software development. He worked on the IBM 1401 and wrote a program to calculate pi. He also wrote a program to predict how high a rocket ship would fly. The program was written in Fortran and used a TRS-80 microcomputer. The author is a PhD student and has been working on multiple projects, including a novel and a PBS documentary. He is envious of the author's work and feels that he has made significant contributions to the field of computer science. He is working on multiple projects and is envious of the author's work. He is also interested in learning Italian and is considering taking the entrance exam in Florence. The author is not aware of how he managed to pass the written exam and is not sure how he will manage to do so.<|USER|>
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
