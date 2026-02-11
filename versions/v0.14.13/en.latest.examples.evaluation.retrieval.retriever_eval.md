![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Retrieval Evaluation¶
This notebook uses our `RetrieverEvaluator` to evaluate the quality of any Retriever module defined in LlamaIndex.
We specify a set of different evaluation metrics: this includes hit-rate, MRR, Precision, Recall, AP, and NDCG. For any given question, these will compare the quality of retrieved results from the ground-truth context.
To ease the burden of creating the eval dataset in the first place, we can rely on synthetic data generation.
## Setup¶
Here we load in data (PG essay), parse into Nodes. We then index this data using our simple vector index and get a retriever.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-readers-file

```

%pip install llama-index-llms-openai %pip install llama-index-readers-file
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.node_parser import SentenceSplitter from llama_index.llms.openai import OpenAI
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
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
node_parser = SentenceSplitter(chunk_size=512)
nodes = node_parser.get_nodes_from_documents(documents)

```

node_parser = SentenceSplitter(chunk_size=512) nodes = node_parser.get_nodes_from_documents(documents)
In [ ]:
Copied!
```
# by default, the node ids are set to random uuids. To ensure same id's per run, we manually set them.
for idx, node in enumerate(nodes):
    node.id_ = f"node_{idx}"

```

# by default, the node ids are set to random uuids. To ensure same id's per run, we manually set them. for idx, node in enumerate(nodes): node.id_ = f"node_{idx}"
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4")

```

llm = OpenAI(model="gpt-4")
In [ ]:
Copied!
```
vector_index = VectorStoreIndex(nodes)
retriever = vector_index.as_retriever(similarity_top_k=2)

```

vector_index = VectorStoreIndex(nodes) retriever = vector_index.as_retriever(similarity_top_k=2)
### Try out Retrieval¶
We'll try out retrieval over a simple dataset.
In [ ]:
Copied!
```
retrieved_nodes = retriever.retrieve("What did the author do growing up?")

```

retrieved_nodes = retriever.retrieve("What did the author do growing up?")
In [ ]:
Copied!
```
from llama_index.core.response.notebook_utils import display_source_node

for node in retrieved_nodes:
    display_source_node(node, source_length=1000)

```

from llama_index.core.response.notebook_utils import display_source_node for node in retrieved_nodes: display_source_node(node, source_length=1000)
**Node ID:** node_38  
**Similarity:** 0.814377909267451  
**Text:** I also worked on spam filters, and did some more painting. I used to have dinners for a group of friends every thursday night, which taught me how to cook for groups. And I bought another building in Cambridge, a former candy factory (and later, twas said, porn studio), to use as an office.
One night in October 2003 there was a big party at my house. It was a clever idea of my friend Maria Daniels, who was one of the thursday diners. Three separate hosts would all invite their friends to one party. So for every guest, two thirds of the other guests would be people they didn't know but would probably like. One of the guests was someone I didn't know but would turn out to like a lot: a woman called Jessica Livingston. A couple days later I asked her out.
Jessica was in charge of marketing at a Boston investment bank. This bank thought it understood startups, but over the next year, as she met friends of mine from the startup world, she was surprised how different reality was. And ho...  

**Node ID:** node_0  
**Similarity:** 0.8122448657654567  
**Text:** What I Worked On
February 2021
Before college the two main things I worked on, outside of school, were writing and programming. I didn't write essays. I wrote what beginning writers were supposed to write then, and probably still are: short stories. My stories were awful. They had hardly any plot, just characters with strong feelings, which I imagined made them deep.
The first programs I tried writing were on the IBM 1401 that our school district used for what was then called "data processing." This was in 9th grade, so I was 13 or 14. The school district's 1401 happened to be in the basement of our junior high school, and my friend Rich Draves and I got permission to use it. It was like a mini Bond villain's lair down there, with all these alien-looking machines — CPU, disk drives, printer, card reader — sitting up on a raised floor under bright fluorescent lights.
The language we used was an early version of Fortran. You had to type programs on punch cards, then stack them in ...  

## Build an Evaluation dataset of (query, context) pairs¶
Here we build a simple evaluation dataset over the existing text corpus.
We use our `generate_question_context_pairs` to generate a set of (question, context) pairs over a given unstructured text corpus. This uses the LLM to auto-generate questions from each context chunk.
We get back a `EmbeddingQAFinetuneDataset` object. At a high-level this contains a set of ids mapping to queries and relevant doc chunks, as well as the corpus itself.
In [ ]:
Copied!
```
from llama_index.core.evaluation import (
    generate_question_context_pairs,
    EmbeddingQAFinetuneDataset,
)

```

from llama_index.core.evaluation import ( generate_question_context_pairs, EmbeddingQAFinetuneDataset, )
In [ ]:
Copied!
```
qa_dataset = generate_question_context_pairs(
    nodes, llm=llm, num_questions_per_chunk=2
)

```

qa_dataset = generate_question_context_pairs( nodes, llm=llm, num_questions_per_chunk=2 )
```
100%|██████████| 61/61 [06:10<00:00,  6.08s/it]

```

In [ ]:
Copied!
```
queries = qa_dataset.queries.values()
print(list(queries)[2])

```

queries = qa_dataset.queries.values() print(list(queries)[2])
```
"Describe the transition from using the IBM 1401 to microcomputers, as mentioned in the text. What were the key differences and how did these changes impact the user's interaction with the computer?"

```

In [ ]:
Copied!
```
# [optional] save
qa_dataset.save_json("pg_eval_dataset.json")

```

# [optional] save qa_dataset.save_json("pg_eval_dataset.json")
In [ ]:
Copied!
```
# [optional] load
qa_dataset = EmbeddingQAFinetuneDataset.from_json("pg_eval_dataset.json")

```

# [optional] load qa_dataset = EmbeddingQAFinetuneDataset.from_json("pg_eval_dataset.json")
## Use `RetrieverEvaluator` for Retrieval Evaluation¶
We're now ready to run our retrieval evals. We'll run our `RetrieverEvaluator` over the eval dataset that we generated.
We define two functions: `get_eval_results` and also `display_results` that run our retriever over the dataset.
In [ ]:
Copied!
```
include_cohere_rerank = False

if include_cohere_rerank:
    !pip install cohere -q

```

include_cohere_rerank = False if include_cohere_rerank: !pip install cohere -q
In [ ]:
Copied!
```
from llama_index.core.evaluation import RetrieverEvaluator

metrics = ["hit_rate", "mrr", "precision", "recall", "ap", "ndcg"]

if include_cohere_rerank:
    metrics.append(
        "cohere_rerank_relevancy"  # requires COHERE_API_KEY environment variable to be set
    )

retriever_evaluator = RetrieverEvaluator.from_metric_names(
    metrics, retriever=retriever
)

```

from llama_index.core.evaluation import RetrieverEvaluator metrics = ["hit_rate", "mrr", "precision", "recall", "ap", "ndcg"] if include_cohere_rerank: metrics.append( "cohere_rerank_relevancy" # requires COHERE_API_KEY environment variable to be set ) retriever_evaluator = RetrieverEvaluator.from_metric_names( metrics, retriever=retriever )
In [ ]:
Copied!
```
# try it out on a sample query
sample_id, sample_query = list(qa_dataset.queries.items())[0]
sample_expected = qa_dataset.relevant_docs[sample_id]

eval_result = retriever_evaluator.evaluate(sample_query, sample_expected)
print(eval_result)

```

# try it out on a sample query sample_id, sample_query = list(qa_dataset.queries.items())[0] sample_expected = qa_dataset.relevant_docs[sample_id] eval_result = retriever_evaluator.evaluate(sample_query, sample_expected) print(eval_result)
```
Query: Describe the author's initial experiences with programming on the IBM 1401. What challenges did he face and how did these experiences shape his understanding of programming?
Metrics: {'hit_rate': 1.0, 'mrr': 1.0, 'precision': 0.5, 'recall': 1.0, 'ap': 1.0, 'ndcg': 0.6131471927654584}


```

In [ ]:
Copied!
```
# try it out on an entire dataset
eval_results = await retriever_evaluator.aevaluate_dataset(qa_dataset)

```

# try it out on an entire dataset eval_results = await retriever_evaluator.aevaluate_dataset(qa_dataset)
```
Retrying llama_index.embeddings.openai.base.aget_embedding in 0.6914689476274432 seconds as it raised RateLimitError: Error code: 429 - {'statusCode': 429, 'message': 'Rate limit is exceeded. Try again in 3 seconds.'}.
Retrying llama_index.embeddings.openai.base.aget_embedding in 1.072244476250501 seconds as it raised RateLimitError: Error code: 429 - {'statusCode': 429, 'message': 'Rate limit is exceeded. Try again in 3 seconds.'}.
Retrying llama_index.embeddings.openai.base.aget_embedding in 0.8123380504307198 seconds as it raised RateLimitError: Error code: 429 - {'statusCode': 429, 'message': 'Rate limit is exceeded. Try again in 4 seconds.'}.
Retrying llama_index.embeddings.openai.base.aget_embedding in 0.9520260756712478 seconds as it raised RateLimitError: Error code: 429 - {'statusCode': 429, 'message': 'Rate limit is exceeded. Try again in 6 seconds.'}.
Retrying llama_index.embeddings.openai.base.aget_embedding in 1.3700745779005286 seconds as it raised RateLimitError: Error code: 429 - {'statusCode': 429, 'message': 'Rate limit is exceeded. Try again in 4 seconds.'}.

```

In [ ]:
Copied!
```
import pandas as pd


def display_results(name, eval_results):
    """Display results from evaluate."""

    metric_dicts = []
    for eval_result in eval_results:
        metric_dict = eval_result.metric_vals_dict
        metric_dicts.append(metric_dict)

    full_df = pd.DataFrame(metric_dicts)

    columns = {
        "retrievers": [name],
        **{k: [full_df[k].mean()] for k in metrics},
    }

    if include_cohere_rerank:
        crr_relevancy = full_df["cohere_rerank_relevancy"].mean()
        columns.update({"cohere_rerank_relevancy": [crr_relevancy]})

    metric_df = pd.DataFrame(columns)

    return metric_df

```

import pandas as pd def display_results(name, eval_results): """Display results from evaluate.""" metric_dicts = [] for eval_result in eval_results: metric_dict = eval_result.metric_vals_dict metric_dicts.append(metric_dict) full_df = pd.DataFrame(metric_dicts) columns = { "retrievers": [name], **{k: [full_df[k].mean()] for k in metrics}, } if include_cohere_rerank: crr_relevancy = full_df["cohere_rerank_relevancy"].mean() columns.update({"cohere_rerank_relevancy": [crr_relevancy]}) metric_df = pd.DataFrame(columns) return metric_df
In [ ]:
Copied!
```
display_results("top-2 eval", eval_results)

```

display_results("top-2 eval", eval_results)
Out[ ]:
| retrievers | hit_rate | mrr | precision | recall | ap | ndcg  
---|---|---|---|---|---|---|---  
0 | top-2 eval | 0.770492 | 0.655738 | 0.385246 | 0.770492 | 0.655738 | 0.420488
