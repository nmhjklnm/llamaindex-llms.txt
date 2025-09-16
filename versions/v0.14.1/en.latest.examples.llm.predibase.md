![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Predibase¶
This notebook shows how you can use Predibase-hosted LLM's within Llamaindex. You can add Predibase to your existing Llamaindex worklow to:
  1. Deploy and query pre-trained or custom open source LLM’s without the hassle
  2. Operationalize an end-to-end Retrieval Augmented Generation (RAG) system
  3. Fine-tune your own LLM in just a few lines of code


## Getting Started¶
  1. Sign up for a free Predibase account here
  2. Create an Account
  3. Go to Settings > My profile and Generate a new API Token.


In [ ]:
Copied!
```
%pip install llama-index-llms-predibase

```

%pip install llama-index-llms-predibase
In [ ]:
Copied!
```
!pip install llama-index --quiet
!pip install predibase --quiet
!pip install sentence-transformers --quiet

```

!pip install llama-index --quiet !pip install predibase --quiet !pip install sentence-transformers --quiet
In [ ]:
Copied!
```
import os

os.environ["PREDIBASE_API_TOKEN"] = "{PREDIBASE_API_TOKEN}"
from llama_index.llms.predibase import PredibaseLLM

```

import os os.environ["PREDIBASE_API_TOKEN"] = "{PREDIBASE_API_TOKEN}" from llama_index.llms.predibase import PredibaseLLM
## Flow 1: Query Predibase LLM directly¶
In [ ]:
Copied!
```
# Predibase-hosted fine-tuned adapter example
llm = PredibaseLLM(
    model_name="mistral-7b",
    predibase_sdk_version=None,  # optional parameter (defaults to the latest Predibase SDK version if omitted)
    adapter_id="e2e_nlg",  # adapter_id is optional
    adapter_version=1,  # optional parameter (applies to Predibase only)
    api_token=None,  # optional parameter for accessing services hosting adapters (e.g., HuggingFace)
    max_new_tokens=512,
    temperature=0.3,
)
# The `model_name` parameter is the Predibase "serverless" base_model ID
# (see https://docs.predibase.com/user-guide/inference/models for the catalog).
# You can also optionally specify a fine-tuned adapter that's hosted on Predibase or HuggingFace
# In the case of Predibase-hosted adapters, you must also specify the adapter_version

```

# Predibase-hosted fine-tuned adapter example llm = PredibaseLLM( model_name="mistral-7b", predibase_sdk_version=None, # optional parameter (defaults to the latest Predibase SDK version if omitted) adapter_id="e2e_nlg", # adapter_id is optional adapter_version=1, # optional parameter (applies to Predibase only) api_token=None, # optional parameter for accessing services hosting adapters (e.g., HuggingFace) max_new_tokens=512, temperature=0.3, ) # The `model_name` parameter is the Predibase "serverless" base_model ID # (see https://docs.predibase.com/user-guide/inference/models for the catalog). # You can also optionally specify a fine-tuned adapter that's hosted on Predibase or HuggingFace # In the case of Predibase-hosted adapters, you must also specify the adapter_version
In [ ]:
Copied!
```
# HuggingFace-hosted fine-tuned adapter example
llm = PredibaseLLM(
    model_name="mistral-7b",
    predibase_sdk_version=None,  # optional parameter (defaults to the latest Predibase SDK version if omitted)
    adapter_id="predibase/e2e_nlg",  # adapter_id is optional
    api_token=os.environ.get(
        "HUGGING_FACE_HUB_TOKEN"
    ),  # optional parameter for accessing services hosting adapters (e.g., HuggingFace)
    max_new_tokens=512,
    temperature=0.3,
)
# The `model_name` parameter is the Predibase "serverless" base_model ID
# (see https://docs.predibase.com/user-guide/inference/models for the catalog).
# You can also optionally specify a fine-tuned adapter that's hosted on Predibase or HuggingFace
# In the case of Predibase-hosted adapters, you can also specify the adapter_version (assumed latest if omitted)

```

# HuggingFace-hosted fine-tuned adapter example llm = PredibaseLLM( model_name="mistral-7b", predibase_sdk_version=None, # optional parameter (defaults to the latest Predibase SDK version if omitted) adapter_id="predibase/e2e_nlg", # adapter_id is optional api_token=os.environ.get( "HUGGING_FACE_HUB_TOKEN" ), # optional parameter for accessing services hosting adapters (e.g., HuggingFace) max_new_tokens=512, temperature=0.3, ) # The `model_name` parameter is the Predibase "serverless" base_model ID # (see https://docs.predibase.com/user-guide/inference/models for the catalog). # You can also optionally specify a fine-tuned adapter that's hosted on Predibase or HuggingFace # In the case of Predibase-hosted adapters, you can also specify the adapter_version (assumed latest if omitted)
In [ ]:
Copied!
```
result = llm.complete("Can you recommend me a nice dry white wine?")
print(result)

```

result = llm.complete("Can you recommend me a nice dry white wine?") print(result)
## Flow 2: Retrieval Augmented Generation (RAG) with Predibase LLM¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.embeddings import resolve_embed_model
from llama_index.core.node_parser import SentenceSplitter

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.embeddings import resolve_embed_model from llama_index.core.node_parser import SentenceSplitter
#### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
### Load Documents¶
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
### Configure Predibase LLM¶
In [ ]:
Copied!
```
# Predibase-hosted fine-tuned adapter
llm = PredibaseLLM(
    model_name="mistral-7b",
    predibase_sdk_version=None,  # optional parameter (defaults to the latest Predibase SDK version if omitted)
    adapter_id="e2e_nlg",  # adapter_id is optional
    api_token=None,  # optional parameter for accessing services hosting adapters (e.g., HuggingFace)
    temperature=0.3,
    context_window=1024,
)

```

# Predibase-hosted fine-tuned adapter llm = PredibaseLLM( model_name="mistral-7b", predibase_sdk_version=None, # optional parameter (defaults to the latest Predibase SDK version if omitted) adapter_id="e2e_nlg", # adapter_id is optional api_token=None, # optional parameter for accessing services hosting adapters (e.g., HuggingFace) temperature=0.3, context_window=1024, )
In [ ]:
Copied!
```
# HuggingFace-hosted fine-tuned adapter
llm = PredibaseLLM(
    model_name="mistral-7b",
    predibase_sdk_version=None,  # optional parameter (defaults to the latest Predibase SDK version if omitted)
    adapter_id="predibase/e2e_nlg",  # adapter_id is optional
    api_token=os.environ.get(
        "HUGGING_FACE_HUB_TOKEN"
    ),  # optional parameter for accessing services hosting adapters (e.g., HuggingFace)
    temperature=0.3,
    context_window=1024,
)

```

# HuggingFace-hosted fine-tuned adapter llm = PredibaseLLM( model_name="mistral-7b", predibase_sdk_version=None, # optional parameter (defaults to the latest Predibase SDK version if omitted) adapter_id="predibase/e2e_nlg", # adapter_id is optional api_token=os.environ.get( "HUGGING_FACE_HUB_TOKEN" ), # optional parameter for accessing services hosting adapters (e.g., HuggingFace) temperature=0.3, context_window=1024, )
In [ ]:
Copied!
```
embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5")
splitter = SentenceSplitter(chunk_size=1024)

```

embed_model = resolve_embed_model("local:BAAI/bge-small-en-v1.5") splitter = SentenceSplitter(chunk_size=1024)
### Setup and Query Index¶
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(
    documents, transformations=[splitter], embed_model=embed_model
)
query_engine = index.as_query_engine(llm=llm)
response = query_engine.query("What did the author do growing up?")

```

index = VectorStoreIndex.from_documents( documents, transformations=[splitter], embed_model=embed_model ) query_engine = index.as_query_engine(llm=llm) response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
print(response)

```

print(response)
