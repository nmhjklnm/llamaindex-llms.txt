# Observability with Arize Phoenix - Tracing and Evaluating a LlamaIndex Application¶
LlamaIndex provides high-level APIs that enable users to build powerful applications in a few lines of code. However, it can be challenging to understand what is going on under the hood and to pinpoint the cause of issues. Phoenix makes your LLM applications _observable_ by visualizing the underlying structure of each call to your query engine and surfacing problematic `spans`` of execution based on latency, token count, or other evaluation metrics.
In this tutorial, you will:
  * Build a simple query engine using LlamaIndex that uses retrieval-augmented generation to answer questions over the Paul Graham Essay,
  * Record trace data in OpenInference tracing format using the global `arize_phoenix` handler
  * Inspect the traces and spans of your application to identify sources of latency and cost,
  * Export your trace data as a pandas dataframe and run an LLM Evals.


ℹ️ This notebook requires an OpenAI API key.
Observability Documentation
## 1. Install Dependencies and Import Libraries¶
Install Phoenix, LlamaIndex, and OpenAI.
In [ ]:
Copied!
```
!pip install llama-index
!pip install llama-index-callbacks-arize-phoenix
!pip install arize-phoenix[evals]
!pip install "openinference-instrumentation-llama-index>=1.0.0"

```

!pip install llama-index !pip install llama-index-callbacks-arize-phoenix !pip install arize-phoenix[evals] !pip install "openinference-instrumentation-llama-index>=1.0.0"
In [ ]:
Copied!
```
import json
import os
from getpass import getpass
from urllib.request import urlopen

import nest_asyncio
import openai
import pandas as pd
import phoenix as px
from llama_index.core import (
    Settings,
    set_global_handler,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from phoenix.evals import (
    HallucinationEvaluator,
    OpenAIModel,
    QAEvaluator,
    RelevanceEvaluator,
    run_evals,
)
from phoenix.session.evaluation import (
    get_qa_with_reference,
    get_retrieved_documents,
)
from phoenix.trace import DocumentEvaluations, SpanEvaluations
from tqdm import tqdm

nest_asyncio.apply()
pd.set_option("display.max_colwidth", 1000)

```

import json import os from getpass import getpass from urllib.request import urlopen import nest_asyncio import openai import pandas as pd import phoenix as px from llama_index.core import ( Settings, set_global_handler, ) from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI from phoenix.evals import ( HallucinationEvaluator, OpenAIModel, QAEvaluator, RelevanceEvaluator, run_evals, ) from phoenix.session.evaluation import ( get_qa_with_reference, get_retrieved_documents, ) from phoenix.trace import DocumentEvaluations, SpanEvaluations from tqdm import tqdm nest_asyncio.apply() pd.set_option("display.max_colwidth", 1000)
## 2. Launch Phoenix¶
You can run Phoenix in the background to collect trace data emitted by any LlamaIndex application that has been instrumented with the `OpenInferenceTraceCallbackHandler`. Phoenix supports LlamaIndex's one-click observability which will automatically instrument your LlamaIndex application! You can consult our integration guide for a more detailed explanation of how to instrument your LlamaIndex application.
Launch Phoenix and follow the instructions in the cell output to open the Phoenix UI (the UI should be empty because we have yet to run the LlamaIndex application).
In [ ]:
Copied!
```
session = px.launch_app()

```

session = px.launch_app()
```
🌍 To view the Phoenix app in your browser, visit https://jfgzmj4xrg3-496ff2e9c6d22116-6006-colab.googleusercontent.com/
📺 To view the Phoenix app in a notebook, run `px.active_session().view()`
📖 For more information on how to use Phoenix, check out https://docs.arize.com/phoenix

```

## 3. Configure Your OpenAI API Key¶
Set your OpenAI API key if it is not already set as an environment variable.
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
## 4. Build Index and Create QueryEngine¶
a. Download Data
b. Load Data
c. Setup Phoenix Tracing
d. Setup LLM And Embedding Model
e. Create Index
f. Create Query Engine
### Download Data¶
In [ ]:
Copied!
```
!wget "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt" "paul_graham_essay.txt"

```

!wget "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt" "paul_graham_essay.txt"
```
--2024-04-26 03:09:56--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.109.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘paul_graham_essay.txt’

paul_graham_essay.t 100%[===================>]  73.28K  --.-KB/s    in 0.01s   

2024-04-26 03:09:56 (5.58 MB/s) - ‘paul_graham_essay.txt’ saved [75042/75042]

--2024-04-26 03:09:56--  http://paul_graham_essay.txt/
Resolving paul_graham_essay.txt (paul_graham_essay.txt)... failed: Name or service not known.
wget: unable to resolve host address ‘paul_graham_essay.txt’
FINISHED --2024-04-26 03:09:56--
Total wall clock time: 0.2s
Downloaded: 1 files, 73K in 0.01s (5.58 MB/s)

```

### Load Data¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader(
    input_files=["paul_graham_essay.txt"]
).load_data()

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader documents = SimpleDirectoryReader( input_files=["paul_graham_essay.txt"] ).load_data()
### Setup Phoenix Tracing¶
Enable Phoenix tracing within LlamaIndex by setting `arize_phoenix` as the global handler. This will mount Phoenix's OpenInferenceTraceCallback as the global handler. Phoenix uses OpenInference traces - an open-source standard for capturing and storing LLM application traces that enables LLM applications to seamlessly integrate with LLM observability solutions such as Phoenix.
In [ ]:
Copied!
```
set_global_handler("arize_phoenix")

```

set_global_handler("arize_phoenix")
### Setup LLM and Embedding Model¶
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2)
embed_model = OpenAIEmbedding()

Settings.llm = llm
Settings.embed_model = embed_model

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI from llama_index.core import Settings llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2) embed_model = OpenAIEmbedding() Settings.llm = llm Settings.embed_model = embed_model
### Create Index¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents)
### Create Query Engine.¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(similarity_top_k=5)

```

query_engine = index.as_query_engine(similarity_top_k=5)
## 5. Run Your Query Engine and View Your Traces in Phoenix¶
In [ ]:
Copied!
```
queries = [
    "what did paul graham do growing up?",
    "why did paul graham start YC?",
]

```

queries = [ "what did paul graham do growing up?", "why did paul graham start YC?", ]
In [ ]:
Copied!
```
for query in tqdm(queries):
    query_engine.query(query)

```

for query in tqdm(queries): query_engine.query(query)
```
100%|██████████| 2/2 [00:07<00:00,  3.81s/it]

```

In [ ]:
Copied!
```
print(query_engine.query("Who is Paul Graham?"))

```

print(query_engine.query("Who is Paul Graham?"))
```
Paul Graham is a writer, entrepreneur, and investor known for his involvement in various projects and ventures. He has written essays on diverse topics, founded companies like Viaweb and Y Combinator, and has a strong presence in the startup and technology industry.

```

In [ ]:
Copied!
```
print(f"🚀 Open the Phoenix UI if you haven't already: {session.url}")

```

print(f"🚀 Open the Phoenix UI if you haven't already: {session.url}")
```
🚀 Open the Phoenix UI if you haven't already: https://jfgzmj4xrg4-496ff2e9c6d22116-6006-colab.googleusercontent.com/

```

## 6. Export and Evaluate Your Trace Data¶
You can export your trace data as a pandas dataframe for further analysis and evaluation.
In this case, we will export our `retriever` spans into two separate dataframes:
  * `queries_df`, in which the retrieved documents for each query are concatenated into a single column,
  * `retrieved_documents_df`, in which each retrieved document is "exploded" into its own row to enable the evaluation of each query-document pair in isolation.


This will enable us to compute multiple kinds of evaluations, including:
  * relevance: Are the retrieved documents grounded in the response?
  * Q&A correctness: Are your application's responses grounded in the retrieved context?
  * hallucinations: Is your application making up false information?


In [ ]:
Copied!
```
queries_df = get_qa_with_reference(px.Client())
retrieved_documents_df = get_retrieved_documents(px.Client())

```

queries_df = get_qa_with_reference(px.Client()) retrieved_documents_df = get_retrieved_documents(px.Client())
Next, define your evaluation model and your evaluators.
Evaluators are built on top of language models and prompt the LLM to assess the quality of responses, the relevance of retrieved documents, etc., and provide a quality signal even in the absence of human-labeled data. Pick an evaluator type and instantiate it with the language model you want to use to perform evaluations using our battle-tested evaluation templates.
In [ ]:
Copied!
```
eval_model = OpenAIModel(
    model="gpt-4",
)
hallucination_evaluator = HallucinationEvaluator(eval_model)
qa_correctness_evaluator = QAEvaluator(eval_model)
relevance_evaluator = RelevanceEvaluator(eval_model)

hallucination_eval_df, qa_correctness_eval_df = run_evals(
    dataframe=queries_df,
    evaluators=[hallucination_evaluator, qa_correctness_evaluator],
    provide_explanation=True,
)
relevance_eval_df = run_evals(
    dataframe=retrieved_documents_df,
    evaluators=[relevance_evaluator],
    provide_explanation=True,
)[0]

px.Client().log_evaluations(
    SpanEvaluations(
        eval_name="Hallucination", dataframe=hallucination_eval_df
    ),
    SpanEvaluations(
        eval_name="QA Correctness", dataframe=qa_correctness_eval_df
    ),
    DocumentEvaluations(eval_name="Relevance", dataframe=relevance_eval_df),
)

```

eval_model = OpenAIModel( model="gpt-4", ) hallucination_evaluator = HallucinationEvaluator(eval_model) qa_correctness_evaluator = QAEvaluator(eval_model) relevance_evaluator = RelevanceEvaluator(eval_model) hallucination_eval_df, qa_correctness_eval_df = run_evals( dataframe=queries_df, evaluators=[hallucination_evaluator, qa_correctness_evaluator], provide_explanation=True, ) relevance_eval_df = run_evals( dataframe=retrieved_documents_df, evaluators=[relevance_evaluator], provide_explanation=True, )[0] px.Client().log_evaluations( SpanEvaluations( eval_name="Hallucination", dataframe=hallucination_eval_df ), SpanEvaluations( eval_name="QA Correctness", dataframe=qa_correctness_eval_df ), DocumentEvaluations(eval_name="Relevance", dataframe=relevance_eval_df), )
```
run_evals |          | 0/6 (0.0%) | ⏳ 00:00<? | ?it/s
```

```
run_evals |          | 0/15 (0.0%) | ⏳ 00:00<? | ?it/s
```

For more details on Phoenix, LLM Tracing, and LLM Evals, checkout the documentation.
