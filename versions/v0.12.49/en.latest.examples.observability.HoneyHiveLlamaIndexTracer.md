![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# HoneyHive LlamaIndex Tracer¶
HoneyHive is a platform that helps developers monitor, evaluate and continuously improve their LLM-powered applications.
The `HoneyHiveLlamaIndexTracer` is integrated with HoneyHive to help developers debug and analyze the execution flow of your LLM pipeline, or to let developers customize feedback on specific trace events to create evaluation or fine-tuning datasets from production.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
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
Paste your OpenAI key from: https://platform.openai.com/account/api-keys
 ········

```

```
OpenAI API key configured

```

In [ ]:
Copied!
```
import os
from getpass import getpass

if os.getenv("HONEYHIVE_API_KEY") is None:
    os.environ["HONEYHIVE_API_KEY"] = getpass(
        "Paste your HoneyHive key from:"
        " https://app.honeyhive.ai/settings/account\n"
    )
print("HoneyHive API key configured")

```

import os from getpass import getpass if os.getenv("HONEYHIVE_API_KEY") is None: os.environ["HONEYHIVE_API_KEY"] = getpass( "Paste your HoneyHive key from:" " https://app.honeyhive.ai/settings/account\n" ) print("HoneyHive API key configured")
```
Paste your HoneyHive key from: https://app.honeyhive.ai/settings/account
 ········

```

```
HoneyHive API key configured

```

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
from llama_index.core.callbacks import CallbackManager
from llama_index.core.callbacks import LlamaDebugHandler
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    SimpleKeywordTableIndex,
    StorageContext,
)
from llama_index.core import ComposableGraph
from llama_index.llms.openai import OpenAI
from honeyhive.utils.llamaindex_tracer import HoneyHiveLlamaIndexTracer

```

from llama_index.core.callbacks import CallbackManager from llama_index.core.callbacks import LlamaDebugHandler from llama_index.core import ( VectorStoreIndex, SimpleDirectoryReader, SimpleKeywordTableIndex, StorageContext, ) from llama_index.core import ComposableGraph from llama_index.llms.openai import OpenAI from honeyhive.utils.llamaindex_tracer import HoneyHiveLlamaIndexTracer
## Setup LLM¶
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-4", temperature=0)

```

from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-4", temperature=0)
## HoneyHive Callback Manager Setup¶
**Option 1** : Set Global Evaluation Handler
In [ ]:
Copied!
```
import llama_index.core
from llama_index.core import set_global_handler

set_global_handler(
    "honeyhive",
    project="My LlamaIndex Project",
    name="My LlamaIndex Pipeline",
    api_key=os.environ["HONEYHIVE_API_KEY"],
)
hh_tracer = llama_index.core.global_handler

```

import llama_index.core from llama_index.core import set_global_handler set_global_handler( "honeyhive", project="My LlamaIndex Project", name="My LlamaIndex Pipeline", api_key=os.environ["HONEYHIVE_API_KEY"], ) hh_tracer = llama_index.core.global_handler
**Option 2** : Manually Configure Callback Handler
Also configure a debugger handler for extra notebook visibility.
In [ ]:
Copied!
```
llama_debug = LlamaDebugHandler(print_trace_on_end=True)

hh_tracer = HoneyHiveLlamaIndexTracer(
    project="My LlamaIndex Project",
    name="My LlamaIndex Pipeline",
    api_key=os.environ["HONEYHIVE_API_KEY"],
)

callback_manager = CallbackManager([llama_debug, hh_tracer])

Settings.callback_manager = callback_manager

```

llama_debug = LlamaDebugHandler(print_trace_on_end=True) hh_tracer = HoneyHiveLlamaIndexTracer( project="My LlamaIndex Project", name="My LlamaIndex Pipeline", api_key=os.environ["HONEYHIVE_API_KEY"], ) callback_manager = CallbackManager([llama_debug, hh_tracer]) Settings.callback_manager = callback_manager
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
    |_node_parsing ->  0.080298 seconds
      |_chunking ->  0.078948 seconds
    |_embedding ->  1.117244 seconds
    |_embedding ->  0.382624 seconds
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
    |_query ->  11.334982 seconds
      |_retrieve ->  0.255016 seconds
        |_embedding ->  0.247083 seconds
      |_synthesize ->  11.079581 seconds
        |_templating ->  5.7e-05 seconds
        |_llm ->  11.065533 seconds
**********
Growing up, the author was involved in writing and programming. They wrote short stories and tried their hand at programming on an IBM 1401, using an early version of Fortran. Later, they started programming on a TRS-80 microcomputer that their father bought, creating simple games, a program to predict the flight of their model rockets, and a word processor. Despite their interest in programming, they initially planned to study philosophy in college, but eventually switched to AI.

```

## View HoneyHive Traces¶
When we are done tracing our events we can view them via the HoneyHive platform. Simply login to HoneyHive, go to your `My LlamaIndex Project` project, click the `Data Store` tab and view your `Sessions`.
