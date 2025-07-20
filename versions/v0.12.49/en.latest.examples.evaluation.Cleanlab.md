![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Trustworthy RAG with LlamaIndex and Cleanlab¶
LLMs occasionally hallucinate incorrect answers, especially for questions not well-supported within their training data. While organizations are adopting Retrieval Augmented Generation (RAG) to power LLMs with proprietary data, incorrect RAG responses remain a problem.
This tutorial shows how to build **trustworthy** RAG applications: use Cleanlab to score the trustworthiness of every LLM response, and diagnose _why_ responses are untrustworthy via evaluations of specific RAG components.
Powered by state-of-the-art uncertainty estimation, Cleanlab trustworthiness scores help you automatically catch incorrect responses from any LLM application. Trust scoring happens in real-time and does not require any data labeling or model training work. Cleanlab provides additional real-time Evals for specific RAG components like the retrieved context, which help you root cause _why_ RAG responses were incorrect. Cleanlab makes it easy to prevent inaccurate responses from your RAG app, and avoid losing your users' trust.
## Setup¶
This tutorial requires a:
  * Cleanlab API Key: Sign up at tlm.cleanlab.ai/ to get a free key
  * OpenAI API Key: To make completion requests to an LLM


Start by installing the required dependencies.
In [ ]:
Copied!
```
%pip install llama-index cleanlab-tlm

```

%pip install llama-index cleanlab-tlm
In [ ]:
Copied!
```
import os, re
from typing import List, ClassVar
import pandas as pd

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

from cleanlab_tlm import TrustworthyRAG, Eval, get_default_evals

```

import os, re from typing import List, ClassVar import pandas as pd from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from cleanlab_tlm import TrustworthyRAG, Eval, get_default_evals
Initialize the OpenAI client using its API key.
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "<your-openai-api-key>"

llm = OpenAI(model="gpt-4o-mini")
embed_model = OpenAIEmbedding(embed_batch_size=10)

```

os.environ["OPENAI_API_KEY"] = "" llm = OpenAI(model="gpt-4o-mini") embed_model = OpenAIEmbedding(embed_batch_size=10)
Now, we initialize Cleanlab's client with default configurations. You can achieve better detection accuracy and latency by adjusting optional configurations.
In [ ]:
Copied!
```
os.environ["CLEANLAB_TLM_API_KEY"] = "<your-cleanlab-api-key"

trustworthy_rag = (
    TrustworthyRAG()
)  # Optional configurations can improve accuracy/latency

```

os.environ["CLEANLAB_TLM_API_KEY"] = "
## Read data¶
This tutorial uses Nvidia’s Q1 FY2024 earnings report as an example data source for populating the RAG application's knowledge base.
In [ ]:
Copied!
```
!wget -nc 'https://cleanlab-public.s3.amazonaws.com/Datasets/NVIDIA_Financial_Results_Q1_FY2024.md'
!mkdir -p ./data
!mv NVIDIA_Financial_Results_Q1_FY2024.md data/

```

!wget -nc 'https://cleanlab-public.s3.amazonaws.com/Datasets/NVIDIA_Financial_Results_Q1_FY2024.md' !mkdir -p ./data !mv NVIDIA_Financial_Results_Q1_FY2024.md data/
```
--2025-05-07 16:13:28--  https://cleanlab-public.s3.amazonaws.com/Datasets/NVIDIA_Financial_Results_Q1_FY2024.md
Resolving cleanlab-public.s3.amazonaws.com (cleanlab-public.s3.amazonaws.com)... 54.231.236.193, 16.182.70.65, 52.217.14.204, ...
Connecting to cleanlab-public.s3.amazonaws.com (cleanlab-public.s3.amazonaws.com)|54.231.236.193|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 7379 (7.2K) [binary/octet-stream]
Saving to: ‘NVIDIA_Financial_Results_Q1_FY2024.md’

NVIDIA_Financial_Re 100%[===================>]   7.21K  --.-KB/s    in 0s      

2025-05-07 16:13:28 (97.7 MB/s) - ‘NVIDIA_Financial_Results_Q1_FY2024.md’ saved [7379/7379]


```

In [ ]:
Copied!
```
with open(
    "data/NVIDIA_Financial_Results_Q1_FY2024.md", "r", encoding="utf-8"
) as file:
    data = file.read()

print(data[:200])

```

with open( "data/NVIDIA_Financial_Results_Q1_FY2024.md", "r", encoding="utf-8" ) as file: data = file.read() print(data[:200])
```
# NVIDIA Announces Financial Results for First Quarter Fiscal 2024

NVIDIA (NASDAQ: NVDA) today reported revenue for the first quarter ended April 30, 2023, of $7.19 billion, down 13% from a year ago 

```

## Build a RAG pipeline¶
Now let's build a simple RAG pipeline with LlamaIndex. We have already initialized the OpenAI API for both as LLM and Embedding model.
In [ ]:
Copied!
```
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader

Settings.llm = llm
Settings.embed_model = embed_model

```

from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader Settings.llm = llm Settings.embed_model = embed_model
### Load Data and Create Index + Query Engine¶
Let's create an index from the document we just pulled above. We stick with the default index from LlamaIndex for this tutorial.
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("data").load_data()
# Optional step since we're loading just one data file
for doc in documents:
    doc.excluded_llm_metadata_keys.append(
        "file_path"
    )  # file_path wouldn't be a useful metadata to add to LLM's context since our datasource contains just 1 file
index = VectorStoreIndex.from_documents(documents)

```

documents = SimpleDirectoryReader("data").load_data() # Optional step since we're loading just one data file for doc in documents: doc.excluded_llm_metadata_keys.append( "file_path" ) # file_path wouldn't be a useful metadata to add to LLM's context since our datasource contains just 1 file index = VectorStoreIndex.from_documents(documents)
The generated index is used to power a query engine over the data.
In [ ]:
Copied!
```
query_engine = index.as_query_engine()

```

query_engine = index.as_query_engine()
Note that Cleanlab is agnostic to the index and the query engine used for RAG, and is compatible with any choices you make for these components of your system.
In addition, you can just use Cleanlab in an existing custom-built RAG pipeline (using any other LLM generator, streaming or not).   
Cleanlab just needs the prompt sent to your LLM (including system instructions, retrieved context, user query, etc.) and the generated response.
We define an event handler that stores the prompt that LlamaIndex sends to the LLM. Refer to the instrumentation documentation for more details.
In [ ]:
Copied!
```
from llama_index.core.instrumentation import get_dispatcher
from llama_index.core.instrumentation.events import BaseEvent
from llama_index.core.instrumentation.event_handlers import BaseEventHandler
from llama_index.core.instrumentation.events.llm import LLMPredictStartEvent


class PromptEventHandler(BaseEventHandler):
    events: ClassVar[List[BaseEvent]] = []
    PROMPT_TEMPLATE: str = ""

    @classmethod
    def class_name(cls) -> str:
        return "PromptEventHandler"

    def handle(self, event) -> None:
        if isinstance(event, LLMPredictStartEvent):
            self.PROMPT_TEMPLATE = event.template.default_template.template
            self.events.append(event)


# Root dispatcher
root_dispatcher = get_dispatcher()

# Register event handler
event_handler = PromptEventHandler()
root_dispatcher.add_event_handler(event_handler)

```

from llama_index.core.instrumentation import get_dispatcher from llama_index.core.instrumentation.events import BaseEvent from llama_index.core.instrumentation.event_handlers import BaseEventHandler from llama_index.core.instrumentation.events.llm import LLMPredictStartEvent class PromptEventHandler(BaseEventHandler): events: ClassVar[List[BaseEvent]] = [] PROMPT_TEMPLATE: str = "" @classmethod def class_name(cls) -> str: return "PromptEventHandler" def handle(self, event) -> None: if isinstance(event, LLMPredictStartEvent): self.PROMPT_TEMPLATE = event.template.default_template.template self.events.append(event) # Root dispatcher root_dispatcher = get_dispatcher() # Register event handler event_handler = PromptEventHandler() root_dispatcher.add_event_handler(event_handler)
For each query, we can fetch the prompt from `event_handler.PROMPT_TEMPLATE`. Let's see it in action.
## Use our RAG application¶
Now that the vector database is loaded with text chunks and their corresponding embeddings, we can start querying it to answer questions.
In [ ]:
Copied!
```
query = "What was NVIDIA's total revenue in the first quarter of fiscal 2024?"

response = query_engine.query(query)
print(response)

```

query = "What was NVIDIA's total revenue in the first quarter of fiscal 2024?" response = query_engine.query(query) print(response)
```
NVIDIA's total revenue in the first quarter of fiscal 2024 was $7.19 billion.

```

This response is indeed correct for our simple query. Let's see the document chunks that LlamaIndex retrieved for this query, from which we can easy verify this response was right.
In [ ]:
Copied!
```
def get_retrieved_context(response, print_chunks=False):
    if isinstance(response, list):
        texts = [node.text for node in response]
    else:
        texts = [src.node.text for src in response.source_nodes]

    if print_chunks:
        for idx, text in enumerate(texts):
            print(f"--- Chunk {idx + 1} ---\n{text[:200]}...")
    return "\n".join(texts)

```

def get_retrieved_context(response, print_chunks=False): if isinstance(response, list): texts = [node.text for node in response] else: texts = [src.node.text for src in response.source_nodes] if print_chunks: for idx, text in enumerate(texts): print(f"--- Chunk {idx + 1} ---\n{text[:200]}...") return "\n".join(texts)
In [ ]:
Copied!
```
context_str = get_retrieved_context(response, True)

```

context_str = get_retrieved_context(response, True)
```
--- Chunk 1 ---
# NVIDIA Announces Financial Results for First Quarter Fiscal 2024

NVIDIA (NASDAQ: NVDA) today reported revenue for the first quarter ended April 30, 2023, of $7.19 billion, down 13% from a year ago ...
--- Chunk 2 ---
- **Gross Margins**: GAAP and non-GAAP gross margins are expected to be 68.6% and 70.0%, respectively, plus or minus 50 basis points.
- **Operating Expenses**: GAAP and non-GAAP operating expenses are...

```

## Add a Trust Layer with Cleanlab¶
Let's add a detection layer to flag untrustworthy RAG responses in real-time. TrustworthyRAG runs Cleanlab's state-of-the-art uncertainty estimator, the Trustworthy Language Model, to provide a **trustworthiness score** indicating overall confidence that your RAG's response is _correct_.
To diagnose _why_ responses are untrustworthy, TrustworthyRAG can run additional evaluations of specific RAG components. Let's see what Evals it runs by default:
In [ ]:
Copied!
```
default_evals = get_default_evals()
for eval in default_evals:
    print(f"{eval.name}")

```

default_evals = get_default_evals() for eval in default_evals: print(f"{eval.name}")
```
context_sufficiency
response_groundedness
response_helpfulness
query_ease

```

Each Eval returns a score between 0-1 (higher is better) that assesses a different aspect of your RAG system:
  1. **context_sufficiency** : Evaluates whether the retrieved context contains sufficient information to completely answer the query. A low score indicates that key information is missing from the context (perhaps due to poor retrieval or missing documents).
  2. **response_groundedness** : Evaluates whether claims/information stated in the response are explicitly supported by the provided context.
  3. **response_helpfulness** : Evaluates whether the response attempts to answer the user query in a helpful manner.
  4. **query_ease** : Evaluates whether the user query seems easy for an AI system to properly handle. Complex, vague, tricky, or disgruntled-sounding queries receive lower scores.


To run TrustworthyRAG, we need the prompt sent to the LLM, which includes the system message, retrieved chunks, the user's query, and the LLM's response. The event handler defined above provides this prompt. Let's define a helper function to run Cleanlab's detection.
In [ ]:
Copied!
```
# Helper function to run real-time Evals
def get_eval(query, response, event_handler, evaluator):
    # Get context used by LLM to generate response
    context = get_retrieved_context(response)
    # Get prompt template used to build the prompt
    pt = event_handler.PROMPT_TEMPLATE
    # Build prompt
    full_prompt = pt.format(context_str=context, query_str=query)

    eval_result = evaluator.score(
        query=query,
        context=context,
        response=response.response,
        prompt=full_prompt,
    )
    # Evaluate the response using TrustworthyRAG
    print("### Evaluation results:")
    for metric, value in eval_result.items():
        print(f"{metric}: {value['score']}")


# Helper function run end-to-end RAG
def get_answer(query, evaluator=trustworthy_rag, event_handler=event_handler):
    response = query_engine.query(query)

    print(
        f"### Query:\n{query}\n\n### Trimmed Context:\n{get_retrieved_context(response)[:300]}..."
    )
    print(f"\n### Generated response:\n{response.response}\n")

    get_eval(query, response, event_handler, evaluator)

```

# Helper function to run real-time Evals def get_eval(query, response, event_handler, evaluator): # Get context used by LLM to generate response context = get_retrieved_context(response) # Get prompt template used to build the prompt pt = event_handler.PROMPT_TEMPLATE # Build prompt full_prompt = pt.format(context_str=context, query_str=query) eval_result = evaluator.score( query=query, context=context, response=response.response, prompt=full_prompt, ) # Evaluate the response using TrustworthyRAG print("### Evaluation results:") for metric, value in eval_result.items(): print(f"{metric}: {value['score']}") # Helper function run end-to-end RAG def get_answer(query, evaluator=trustworthy_rag, event_handler=event_handler): response = query_engine.query(query) print( f"### Query:\n{query}\n\n### Trimmed Context:\n{get_retrieved_context(response)[:300]}..." ) print(f"\n### Generated response:\n{response.response}\n") get_eval(query, response, event_handler, evaluator)
In [ ]:
Copied!
```
get_eval(query, response, event_handler, trustworthy_rag)

```

get_eval(query, response, event_handler, trustworthy_rag)
```
### Evaluation results:
trustworthiness: 1.0
context_sufficiency: 0.9975124377856721
response_groundedness: 0.9975124378045552
response_helpfulness: 0.9975124367363073
query_ease: 0.9975071027792313

```

**Analysis:** The high `trustworthiness_score` indicates this response is very trustworthy, i.e. non-hallucinated and likely correct. The context that was retrieved here is sufficient to answer this query, as reflected by the high `context_sufficiency` score. The high `query_ease` score indicates this is a straightforward query as well.
Now let’s run a _challenging_ query that **cannot** be answered using the only document in our RAG application's knowledge base.
In [ ]:
Copied!
```
get_answer(
    "How does the report explain why NVIDIA's Gaming revenue decreased year over year?"
)

```

get_answer( "How does the report explain why NVIDIA's Gaming revenue decreased year over year?" )
```
### Query:
How does the report explain why NVIDIA's Gaming revenue decreased year over year?

### Trimmed Context:
# NVIDIA Announces Financial Results for First Quarter Fiscal 2024

NVIDIA (NASDAQ: NVDA) today reported revenue for the first quarter ended April 30, 2023, of $7.19 billion, down 13% from a year ago and up 19% from the previous quarter.

- **Quarterly revenue** of $7.19 billion, up 19% from the pre...

### Generated response:
The report indicates that NVIDIA's Gaming revenue decreased year over year by 38%, which is attributed to a combination of factors, although specific reasons are not detailed. The context highlights that the revenue for the first quarter was $2.24 billion, down from the previous year, while it did show an increase of 22% from the previous quarter. This suggests that while there may have been a seasonal or cyclical recovery, the overall year-over-year decline reflects challenges in the gaming segment during that period.

### Evaluation results:
trustworthiness: 0.8018049078305449
context_sufficiency: 0.26134514055082803
response_groundedness: 0.8147481620994604
response_helpfulness: 0.28647897539109127
query_ease: 0.952132218665045

```

**Analysis:** The generator LLM avoids conjecture by providing a reliable response, as seen in the high `trustworthiness_score`. The low `context_sufficiency` score reflects that the retrieved context was lacking, and the response doesn’t actually answer the user’s query, as indicated by the low `response_helpfulness`.
Let’s see how our RAG system responds to another _challenging_ question.
In [ ]:
Copied!
```
get_answer(
    "How much did Nvidia's revenue decrease this quarter vs last quarter, in dollars?"
)

```

get_answer( "How much did Nvidia's revenue decrease this quarter vs last quarter, in dollars?" )
```
### Query:
How much did Nvidia's revenue decrease this quarter vs last quarter, in dollars?

### Trimmed Context:
# NVIDIA Announces Financial Results for First Quarter Fiscal 2024

NVIDIA (NASDAQ: NVDA) today reported revenue for the first quarter ended April 30, 2023, of $7.19 billion, down 13% from a year ago and up 19% from the previous quarter.

- **Quarterly revenue** of $7.19 billion, up 19% from the pre...

### Generated response:
NVIDIA's revenue decreased by $1.10 billion this quarter compared to the last quarter.

### Evaluation results:
trustworthiness: 0.572441384819641
context_sufficiency: 0.9974990573223977
response_groundedness: 0.006136548076912901
response_helpfulness: 0.997512230771839
query_ease: 0.8018484929561781

```

**Analysis** : The generated response incorrectly states that NVIDIA's revenue decreased this quarter, when in fact the referenced report notes a 19% increase quarter-over-quarter.
Cleanlab's low trustworthiness score helps us automatically catch this incorrect RAG response in real-time! To root-cause why this response was untrustworthy, we see the `response_groundedness` score is low, which indicates our LLM model is to blame for fabricating this false information.
Let's try another one:
In [ ]:
Copied!
```
get_answer(
    "If NVIDIA's Data Center segment maintains its Q1 FY2024 quarter-over-quarter growth rate for the next four quarters, what would be its projected annual revenue?"
)

```

get_answer( "If NVIDIA's Data Center segment maintains its Q1 FY2024 quarter-over-quarter growth rate for the next four quarters, what would be its projected annual revenue?" )
```
### Query:
If NVIDIA's Data Center segment maintains its Q1 FY2024 quarter-over-quarter growth rate for the next four quarters, what would be its projected annual revenue?

### Trimmed Context:
# NVIDIA Announces Financial Results for First Quarter Fiscal 2024

NVIDIA (NASDAQ: NVDA) today reported revenue for the first quarter ended April 30, 2023, of $7.19 billion, down 13% from a year ago and up 19% from the previous quarter.

- **Quarterly revenue** of $7.19 billion, up 19% from the pre...

### Generated response:
If NVIDIA's Data Center segment maintains its quarter-over-quarter growth rate of 18% from Q1 FY2024 for the next four quarters, the projected revenue for the next four quarters can be calculated as follows:

1. Q1 FY2024 revenue: $4.28 billion
2. Q2 FY2024 projected revenue: $4.28 billion * 1.18 = $5.05 billion
3. Q3 FY2024 projected revenue: $5.05 billion * 1.18 = $5.95 billion
4. Q4 FY2024 projected revenue: $5.95 billion * 1.18 = $7.02 billion
5. Q5 FY2024 projected revenue: $7.02 billion * 1.18 = $8.27 billion

Now, summing these revenues for the five quarters (including Q1 FY2024):

- Total projected revenue = $4.28 billion + $5.05 billion + $5.95 billion + $7.02 billion + $8.27 billion = $30.57 billion

Therefore, the projected annual revenue for the Data Center segment would be approximately $30.57 billion.

### Evaluation results:
trustworthiness: 0.23124932848015411
context_sufficiency: 0.9299227307108295
response_groundedness: 0.31247206392894905
response_helpfulness: 0.9975055879546202
query_ease: 0.7724662723193096

```

**Analysis** : Reviewing the generated response, we find it overstates (sums up the financials of Q1) the projected revenue. Again Cleanlab helps us automatically catch this incorrect response via its low `trustworthiness_score`. Based on the additional Evals, the root cause of this issue again appears to be the LLM model failing to ground its response in the retrieved context.
### Custom Evals¶
You can also specify custom evaluations to assess specific criteria, and combine them with the default evaluations for comprehensive/tailored assessment of your RAG system.
For instance, here's how to create and run a custom eval that checks the conciseness of the generated response.
In [ ]:
Copied!
```
conciseness_eval = Eval(
    name="response_conciseness",
    criteria="Evaluate whether the Generated response is concise and to the point without unnecessary verbosity or repetition. A good response should be brief but comprehensive, covering all necessary information without extra words or redundant explanations.",
    response_identifier="Generated Response",
)

# Combine default evals with a custom eval
combined_evals = get_default_evals() + [conciseness_eval]

# Initialize TrustworthyRAG with combined evals
combined_trustworthy_rag = TrustworthyRAG(evals=combined_evals)

```

conciseness_eval = Eval( name="response_conciseness", criteria="Evaluate whether the Generated response is concise and to the point without unnecessary verbosity or repetition. A good response should be brief but comprehensive, covering all necessary information without extra words or redundant explanations.", response_identifier="Generated Response", ) # Combine default evals with a custom eval combined_evals = get_default_evals() + [conciseness_eval] # Initialize TrustworthyRAG with combined evals combined_trustworthy_rag = TrustworthyRAG(evals=combined_evals)
In [ ]:
Copied!
```
get_answer(
    "What significant transitions did Jensen comment on?",
    evaluator=combined_trustworthy_rag,
)

```

get_answer( "What significant transitions did Jensen comment on?", evaluator=combined_trustworthy_rag, )
```
### Query:
What significant transitions did Jensen comment on?

### Trimmed Context:
# NVIDIA Announces Financial Results for First Quarter Fiscal 2024

NVIDIA (NASDAQ: NVDA) today reported revenue for the first quarter ended April 30, 2023, of $7.19 billion, down 13% from a year ago and up 19% from the previous quarter.

- **Quarterly revenue** of $7.19 billion, up 19% from the pre...

### Generated response:
Jensen Huang commented on the significant transitions the computer industry is undergoing, particularly in the areas of accelerated computing and generative AI.

### Evaluation results:
trustworthiness: 0.9810004109697261
context_sufficiency: 0.9902170786836257
response_groundedness: 0.9975123614036665
response_helpfulness: 0.9420916924086002
query_ease: 0.5334109647649754
response_conciseness: 0.842668665703559

```

### Replace your LLM with Cleanlab's¶
Beyond evaluating responses already generated from your LLM, Cleanlab can also generate responses and evaluate them simultaneously (using one of many supported models).   
You can do this by calling `trustworthy_rag.generate(query=query, context=context, prompt=full_prompt)`   
This replaces your own LLM within your RAG system and can be more convenient/accurate/faster.  

Let's replace our OpenAI LLM to call Cleanlab's endpoint instead:
In [ ]:
Copied!
```
query = "How much did Nvidia's revenue decrease this quarter vs last quarter, in dollars?"
relevant_chunks = query_engine.retrieve(query)
context = get_retrieved_context(relevant_chunks)
print(f"### Query:\n{query}\n\n### Trimmed Context:\n{context[:300]}")

pt = event_handler.PROMPT_TEMPLATE
full_prompt = pt.format(context_str=context, query_str=query)

result = trustworthy_rag.generate(
    query=query, context=context, prompt=full_prompt
)
print(f"\n### Generated Response:\n{result['response']}\n")
print("### Evaluation Scores:")
for metric, value in result.items():
    if metric != "response":
        print(f"{metric}: {value['score']}")

```

query = "How much did Nvidia's revenue decrease this quarter vs last quarter, in dollars?" relevant_chunks = query_engine.retrieve(query) context = get_retrieved_context(relevant_chunks) print(f"### Query:\n{query}\n\n### Trimmed Context:\n{context[:300]}") pt = event_handler.PROMPT_TEMPLATE full_prompt = pt.format(context_str=context, query_str=query) result = trustworthy_rag.generate( query=query, context=context, prompt=full_prompt ) print(f"\n### Generated Response:\n{result['response']}\n") print("### Evaluation Scores:") for metric, value in result.items(): if metric != "response": print(f"{metric}: {value['score']}")
```
### Query:
How much did Nvidia's revenue decrease this quarter vs last quarter, in dollars?

### Trimmed Context:
# NVIDIA Announces Financial Results for First Quarter Fiscal 2024

NVIDIA (NASDAQ: NVDA) today reported revenue for the first quarter ended April 30, 2023, of $7.19 billion, down 13% from a year ago and up 19% from the previous quarter.

- **Quarterly revenue** of $7.19 billion, up 19% from the pre

### Generated Response:
NVIDIA's revenue for the first quarter of fiscal 2024 was $7.19 billion, and for the previous quarter (Q4 FY23), it was $6.05 billion. Therefore, the revenue increased by $1.14 billion from the previous quarter, not decreased. 

So, the revenue did not decrease this quarter vs last quarter; it actually increased by $1.14 billion.

### Evaluation Scores:
trustworthiness: 0.6810414232214796
context_sufficiency: 0.9974887437375295
response_groundedness: 0.9975116791816968
response_helpfulness: 0.3293002430120912
query_ease: 0.33275910932109172

```

While it remains hard to achieve a RAG application that will accurately answer _any_ possible question, you can easily use Cleanlab to deploy a _trustworthy_ RAG application which at least flags answers that are likely inaccurate. Learn more about optional configurations you can adjust to improve accuracy/latency in the Cleanlab documentation.
