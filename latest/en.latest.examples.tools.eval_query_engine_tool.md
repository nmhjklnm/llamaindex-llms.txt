![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Evaluation Query Engine Tool¶
In this section we will show you how you can use an `EvalQueryEngineTool` with an agent. Some reasons you may want to use a `EvalQueryEngineTool`:
  1. Use specific kind of evaluation for a tool, and not just the agent's reasoning
  2. Use a different LLM for evaluating tool responses than the agent LLM


An `EvalQueryEngineTool` is built on top of the `QueryEngineTool`. Along with wrapping an existing query engine, it also must be given an existing evaluator to evaluate the responses of that query engine.
## Install Dependencies¶
In [ ]:
Copied!
```
%pip install llama-index-embeddings-huggingface
%pip install llama-index-llms-openai
%pip install llama-index-agents-openai

```

%pip install llama-index-embeddings-huggingface %pip install llama-index-llms-openai %pip install llama-index-agents-openai
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
## Initialize and Set LLM and Local Embedding Model¶
In [ ]:
Copied!
```
from llama_index.core.settings import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI

Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)
Settings.llm = OpenAI()

```

from llama_index.core.settings import Settings from llama_index.embeddings.huggingface import HuggingFaceEmbedding from llama_index.llms.openai import OpenAI Settings.embed_model = HuggingFaceEmbedding( model_name="BAAI/bge-small-en-v1.5" ) Settings.llm = OpenAI()
## Download and Index Data¶
This is something we are donig for the sake of this demo. In production environments, data stores and indexes should already exist and not be created on the fly.
### Create Storage Contexts¶
In [ ]:
Copied!
```
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
)

try:
    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/lyft",
    )
    lyft_index = load_index_from_storage(storage_context)

    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/uber"
    )
    uber_index = load_index_from_storage(storage_context)

    index_loaded = True
except:
    index_loaded = False

```

from llama_index.core import ( StorageContext, load_index_from_storage, ) try: storage_context = StorageContext.from_defaults( persist_dir="./storage/lyft", ) lyft_index = load_index_from_storage(storage_context) storage_context = StorageContext.from_defaults( persist_dir="./storage/uber" ) uber_index = load_index_from_storage(storage_context) index_loaded = True except: index_loaded = False
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
### Load Data¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

if not index_loaded:
    # load data
    lyft_docs = SimpleDirectoryReader(
        input_files=["./data/10k/lyft_2021.pdf"]
    ).load_data()
    uber_docs = SimpleDirectoryReader(
        input_files=["./data/10k/uber_2021.pdf"]
    ).load_data()

    # build index
    lyft_index = VectorStoreIndex.from_documents(lyft_docs)
    uber_index = VectorStoreIndex.from_documents(uber_docs)

    # persist index
    lyft_index.storage_context.persist(persist_dir="./storage/lyft")
    uber_index.storage_context.persist(persist_dir="./storage/uber")

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex if not index_loaded: # load data lyft_docs = SimpleDirectoryReader( input_files=["./data/10k/lyft_2021.pdf"] ).load_data() uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data() # build index lyft_index = VectorStoreIndex.from_documents(lyft_docs) uber_index = VectorStoreIndex.from_documents(uber_docs) # persist index lyft_index.storage_context.persist(persist_dir="./storage/lyft") uber_index.storage_context.persist(persist_dir="./storage/uber")
## Create Query Engines¶
In [ ]:
Copied!
```
lyft_engine = lyft_index.as_query_engine(similarity_top_k=5)
uber_engine = uber_index.as_query_engine(similarity_top_k=5)

```

lyft_engine = lyft_index.as_query_engine(similarity_top_k=5) uber_engine = uber_index.as_query_engine(similarity_top_k=5)
## Create Evaluator¶
In [ ]:
Copied!
```
from llama_index.core.evaluation import RelevancyEvaluator

evaluator = RelevancyEvaluator()

```

from llama_index.core.evaluation import RelevancyEvaluator evaluator = RelevancyEvaluator()
## Create Query Engine Tools¶
In [ ]:
Copied!
```
from llama_index.core.tools import ToolMetadata
from llama_index.core.tools.eval_query_engine import EvalQueryEngineTool

query_engine_tools = [
    EvalQueryEngineTool(
        evaluator=evaluator,
        query_engine=lyft_engine,
        metadata=ToolMetadata(
            name="lyft",
            description=(
                "Provides information about Lyft's financials for year 2021. "
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    ),
    EvalQueryEngineTool(
        evaluator=evaluator,
        query_engine=uber_engine,
        metadata=ToolMetadata(
            name="uber",
            description=(
                "Provides information about Uber's financials for year 2021. "
                "Use a detailed plain text question as input to the tool."
            ),
        ),
    ),
]

```

from llama_index.core.tools import ToolMetadata from llama_index.core.tools.eval_query_engine import EvalQueryEngineTool query_engine_tools = [ EvalQueryEngineTool( evaluator=evaluator, query_engine=lyft_engine, metadata=ToolMetadata( name="lyft", description=( "Provides information about Lyft's financials for year 2021. " "Use a detailed plain text question as input to the tool." ), ), ), EvalQueryEngineTool( evaluator=evaluator, query_engine=uber_engine, metadata=ToolMetadata( name="uber", description=( "Provides information about Uber's financials for year 2021. " "Use a detailed plain text question as input to the tool." ), ), ), ]
## Setup OpenAI Agent¶
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

agent = FunctionAgent(tools=query_engine_tools, llm=OpenAI(model="gpt-4.1"))

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.llms.openai import OpenAI agent = FunctionAgent(tools=query_engine_tools, llm=OpenAI(model="gpt-4.1"))
## Query Engine Passes Evaluation¶
Here we are asking a question about Lyft's financials. This is what we should expect to happen:
  1. The agent will use the `lyftk` tool first
  2. The `EvalQueryEngineTool` will evaluate the response of the query engine using its evaluator
  3. The output of the query engine will pass evaluation because it contains Lyft's financials


In [ ]:
Copied!
```
response = await agent.run("What was Lyft's revenue growth in 2021?")
print(str(response))

```

response = await agent.run("What was Lyft's revenue growth in 2021?") print(str(response))
```
Added user message to memory: What was Lyft's revenue growth in 2021?
=== Calling Function ===
Calling function: lyft with args: {"input": "What was Lyft's revenue growth in 2021?"}
Got output: Lyft's revenue growth in 2021 was $3,208,323, which increased compared to the revenue in 2020 and 2019.
========================

=== Calling Function ===
Calling function: uber with args: {"input": "What was Lyft's revenue growth in 2021?"}
Got output: Could not use tool uber because it failed evaluation.
Reason: NO
========================

Lyft's revenue grew by $3,208,323 in 2021, which increased compared to the revenue in 2020 and 2019.

```

