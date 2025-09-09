![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Wandb Callback Handler¶
Weights & Biases Prompts is a suite of LLMOps tools built for the development of LLM-powered applications.
The `WandbCallbackHandler` is integrated with W&B Prompts to visualize and inspect the execution flow of your index construction, or querying over your index and more. You can use this handler to persist your created indices as W&B Artifacts allowing you to version control your indices.
In [ ]:
Copied!
```
%pip install llama-index-callbacks-wandb
%pip install llama-index-llms-openai

```

%pip install llama-index-callbacks-wandb %pip install llama-index-llms-openai
In [ ]:
Copied!
```
import os
from getpass import getpass

if os.getenv("OPENAI_API_KEY") is None:
    os.environ["OPENAI_API_KEY"] = getpass(
        "Paste your OpenAI key from:"
        " https://platform.openai.com/account/api-keys\n"
    )
assert os.getenv("OPENAI_API_KEY", "").startswith(
    "sk-"
), "This doesn't look like a valid OpenAI API key"
print("OpenAI API key configured")

```

import os from getpass import getpass if os.getenv("OPENAI_API_KEY") is None: os.environ["OPENAI_API_KEY"] = getpass( "Paste your OpenAI key from:" " https://platform.openai.com/account/api-keys\n" ) assert os.getenv("OPENAI_API_KEY", "").startswith( "sk-" ), "This doesn't look like a valid OpenAI API key" print("OpenAI API key configured")
```
OpenAI API key configured

```

In [ ]:
Copied!
```
from llama_index.core.callbacks import CallbackManager
from llama_index.core.callbacks import LlamaDebugHandler
from llama_index.callbacks.wandb import WandbCallbackHandler
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    SimpleKeywordTableIndex,
    StorageContext,
)
from llama_index.llms.openai import OpenAI

```

from llama_index.core.callbacks import CallbackManager from llama_index.core.callbacks import LlamaDebugHandler from llama_index.callbacks.wandb import WandbCallbackHandler from llama_index.core import ( VectorStoreIndex, SimpleDirectoryReader, SimpleKeywordTableIndex, StorageContext, ) from llama_index.llms.openai import OpenAI
## Setup LLM¶
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-4", temperature=0)

```

from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-4", temperature=0)
## W&B Callback Manager Setup¶
**Option 1** : Set Global Evaluation Handler
In [ ]:
Copied!
```
import llama_index.core
from llama_index.core import set_global_handler

set_global_handler("wandb", run_args={"project": "llamaindex"})
wandb_callback = llama_index.core.global_handler

```

import llama_index.core from llama_index.core import set_global_handler set_global_handler("wandb", run_args={"project": "llamaindex"}) wandb_callback = llama_index.core.global_handler
**Option 2** : Manually Configure Callback Handler
Also configure a debugger handler for extra notebook visibility.
In [ ]:
Copied!
```
llama_debug = LlamaDebugHandler(print_trace_on_end=True)

# wandb.init args
run_args = dict(
    project="llamaindex",
)

wandb_callback = WandbCallbackHandler(run_args=run_args)

Settings.callback_manager = CallbackManager([llama_debug, wandb_callback])

```

llama_debug = LlamaDebugHandler(print_trace_on_end=True) # wandb.init args run_args = dict( project="llamaindex", ) wandb_callback = WandbCallbackHandler(run_args=run_args) Settings.callback_manager = CallbackManager([llama_debug, wandb_callback])
> After running the above cell, you will get the W&B run page URL. Here you will find a trace table with all the events tracked using Weights and Biases' Prompts feature.
## 1. Indexing¶
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
In [ ]:
Copied!
```
docs = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

docs = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(docs)

```

index = VectorStoreIndex.from_documents(docs)
```
**********
Trace: index_construction
    |_node_parsing ->  0.295179 seconds
      |_chunking ->  0.293976 seconds
    |_embedding ->  0.494492 seconds
    |_embedding ->  0.346162 seconds
**********

```

```
wandb: Logged trace tree to W&B.

```

### 1.1 Persist Index as W&B Artifacts¶
In [ ]:
Copied!
```
wandb_callback.persist_index(index, index_name="simple_vector_store")

```

wandb_callback.persist_index(index, index_name="simple_vector_store")
```
wandb: Adding directory to artifact (/Users/loganmarkewich/llama_index/docs/examples/callbacks/wandb/run-20230801_152955-ds93prxa/files/storage)... Done. 0.0s

```

### 1.2 Download Index from W&B Artifacts¶
In [ ]:
Copied!
```
from llama_index.core import load_index_from_storage

storage_context = wandb_callback.load_storage_context(
    artifact_url="ayut/llamaindex/simple_vector_store:v0"
)

# Load the index and initialize a query engine
index = load_index_from_storage(
    storage_context,
)

```

from llama_index.core import load_index_from_storage storage_context = wandb_callback.load_storage_context( artifact_url="ayut/llamaindex/simple_vector_store:v0" ) # Load the index and initialize a query engine index = load_index_from_storage( storage_context, )
```
wandb:   3 of 3 files downloaded.  

```

```
**********
Trace: index_construction
**********

```

## 2. Query Over Index¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
print(response, sep="\n")

```

query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?") print(response, sep="\n")
```
**********
Trace: query
    |_query ->  2.695958 seconds
      |_retrieve ->  0.806379 seconds
        |_embedding ->  0.802871 seconds
      |_synthesize ->  1.8893 seconds
        |_llm ->  1.842434 seconds
**********

```

```
wandb: Logged trace tree to W&B.

```

```
The text does not provide information on what the author did growing up.

```

## Close W&B Callback Handler¶
When we are done tracking our events we can close the wandb run.
In [ ]:
Copied!
```
wandb_callback.finish()

```

wandb_callback.finish()
