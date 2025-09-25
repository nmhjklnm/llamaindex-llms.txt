![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Cohere init8 and binary Embeddings Retrieval Evaluation¶
Cohere Embed is the first embedding model that natively supports float, int8, binary and ubinary embeddings. Refer to their main blog post for more details on Cohere int8 & binary Embeddings.
This notebook helps you to evaluate these different embedding types and pick one for your RAG pipeline. It uses our `RetrieverEvaluator` to evaluate the quality of the embeddings using the Retriever module LlamaIndex.
Observed Metrics:
  1. Hit-Rate
  2. MRR (Mean-Reciprocal-Rank)


For any given question, these will compare the quality of retrieved results from the ground-truth context. The eval dataset is created using our synthetic dataset generation module. We will use GPT-4 for dataset generation to avoid bias.
# Note: The results shown at the end of the notebook are very specific to dataset, and various other parameters considered. We recommend you to use the notebook as reference to experiment on your dataset and evaluate the usage of different embedding types in your RAG pipeline.¶
## Installation¶
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-embeddings-cohere

```

%pip install llama-index-llms-openai %pip install llama-index-embeddings-cohere
## Setup API Keys¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "YOUR OPENAI KEY"
os.environ["COHERE_API_KEY"] = "YOUR COHEREAI API KEY"

```

import os os.environ["OPENAI_API_KEY"] = "YOUR OPENAI KEY" os.environ["COHERE_API_KEY"] = "YOUR COHEREAI API KEY"
## Setup¶
Here we load in data (PG essay), parse into Nodes. We then index this data using our simple vector index and get a retriever for the following different embedding types.
  1. `float`
  2. `int8`
  3. `binary`
  4. `ubinary`


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
from llama_index.core.evaluation import generate_question_context_pairs
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.cohere import CohereEmbedding

```

from llama_index.core.evaluation import generate_question_context_pairs from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.node_parser import SentenceSplitter from llama_index.llms.openai import OpenAI from llama_index.embeddings.cohere import CohereEmbedding
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-03-27 20:26:33--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.111.133, 185.199.108.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.111.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.03s   

2024-03-27 20:26:34 (2.18 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

## Load Data¶
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
## Create Nodes¶
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
## Create retrievers for different embedding types¶
In [ ]:
Copied!
```
# llm for question generation
# Take any other llm other than from cohereAI to avoid bias.
llm = OpenAI(model="gpt-4")


# Function to return embedding model
def cohere_embedding(
    model_name: str, input_type: str, embedding_type: str
) -> CohereEmbedding:
    return CohereEmbedding(
        api_key=os.environ["COHERE_API_KEY"],
        model_name=model_name,
        input_type=input_type,
        embedding_type=embedding_type,
    )


# Function to return retriver for different embedding type embedding model
def retriver(nodes, embedding_type="float", model_name="embed-english-v3.0"):
    vector_index = VectorStoreIndex(
        nodes,
        embed_model=cohere_embedding(
            model_name, "search_document", embedding_type
        ),
    )
    retriever = vector_index.as_retriever(
        similarity_top_k=2,
        embed_model=cohere_embedding(
            model_name, "search_query", embedding_type
        ),
    )
    return retriever

```

# llm for question generation # Take any other llm other than from cohereAI to avoid bias. llm = OpenAI(model="gpt-4") # Function to return embedding model def cohere_embedding( model_name: str, input_type: str, embedding_type: str ) -> CohereEmbedding: return CohereEmbedding( api_key=os.environ["COHERE_API_KEY"], model_name=model_name, input_type=input_type, embedding_type=embedding_type, ) # Function to return retriver for different embedding type embedding model def retriver(nodes, embedding_type="float", model_name="embed-english-v3.0"): vector_index = VectorStoreIndex( nodes, embed_model=cohere_embedding( model_name, "search_document", embedding_type ), ) retriever = vector_index.as_retriever( similarity_top_k=2, embed_model=cohere_embedding( model_name, "search_query", embedding_type ), ) return retriever
In [ ]:
Copied!
```
# Build retriever for float embedding type
retriver_float = retriver(nodes)

# Build retriever for int8 embedding type
retriver_int8 = retriver(nodes, "int8")

# Build retriever for binary embedding type
retriver_binary = retriver(nodes, "binary")

# Build retriever for ubinary embedding type
retriver_ubinary = retriver(nodes, "ubinary")

```

# Build retriever for float embedding type retriver_float = retriver(nodes) # Build retriever for int8 embedding type retriver_int8 = retriver(nodes, "int8") # Build retriever for binary embedding type retriver_binary = retriver(nodes, "binary") # Build retriever for ubinary embedding type retriver_ubinary = retriver(nodes, "ubinary")
### Try out Retrieval¶
We'll try out retrieval over a sample query with `float` retriever.
In [ ]:
Copied!
```
retrieved_nodes = retriver_float.retrieve("What did the author do growing up?")

```

retrieved_nodes = retriver_float.retrieve("What did the author do growing up?")
In [ ]:
Copied!
```
from llama_index.core.response.notebook_utils import display_source_node

for node in retrieved_nodes:
    display_source_node(node, source_length=1000)

```

from llama_index.core.response.notebook_utils import display_source_node for node in retrieved_nodes: display_source_node(node, source_length=1000)
**Node ID:** node_2  
**Similarity:** 0.3641554823852197  
**Text:** I remember vividly how impressed and envious I felt watching him sitting in front of it, typing programs right into the computer.
Computers were expensive in those days and it took me years of nagging before I convinced my father to buy one, a TRS-80, in about 1980. The gold standard then was the Apple II, but a TRS-80 was good enough. This was when I really started programming. I wrote simple games, a program to predict how high my model rockets would fly, and a word processor that my father used to write at least one book. There was only room in memory for about 2 pages of text, so he'd write 2 pages at a time and then print them out, but it was a lot better than a typewriter.
Though I liked programming, I didn't plan to study it in college. In college I was going to study philosophy, which sounded much more powerful. It seemed, to my naive high school self, to be the study of the ultimate truths, compared to which the things studied in other fields would be mere domain knowledg...  

**Node ID:** node_0  
**Similarity:** 0.36283154406791923  
**Text:** What I Worked On
February 2021
Before college the two main things I worked on, outside of school, were writing and programming. I didn't write essays. I wrote what beginning writers were supposed to write then, and probably still are: short stories. My stories were awful. They had hardly any plot, just characters with strong feelings, which I imagined made them deep.
The first programs I tried writing were on the IBM 1401 that our school district used for what was then called "data processing." This was in 9th grade, so I was 13 or 14. The school district's 1401 happened to be in the basement of our junior high school, and my friend Rich Draves and I got permission to use it. It was like a mini Bond villain's lair down there, with all these alien-looking machines — CPU, disk drives, printer, card reader — sitting up on a raised floor under bright fluorescent lights.
The language we used was an early version of Fortran. You had to type programs on punch cards, then stack them in ...  

## Evaluation dataset - Synthetic Dataset Generation of (query, context) pairs¶
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
100%|██████████| 59/59 [04:10<00:00,  4.24s/it]

```

In [ ]:
Copied!
```
queries = qa_dataset.queries.values()
print(list(queries)[0])

```

queries = qa_dataset.queries.values() print(list(queries)[0])
```
"Describe the author's initial experiences with programming on the IBM 1401. What were some of the challenges he faced and how did these experiences shape his understanding of programming?"

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
### Define `RetrieverEvaluator` for different embedding_types¶
In [ ]:
Copied!
```
from llama_index.core.evaluation import RetrieverEvaluator

metrics = ["mrr", "hit_rate"]

# Retrieval evaluator for float embedding type
retriever_evaluator_float = RetrieverEvaluator.from_metric_names(
    metrics, retriever=retriver_float
)

# Retrieval evaluator for int8 embedding type
retriever_evaluator_int8 = RetrieverEvaluator.from_metric_names(
    metrics, retriever=retriver_int8
)

# Retrieval evaluator for binary embedding type
retriever_evaluator_binary = RetrieverEvaluator.from_metric_names(
    metrics, retriever=retriver_binary
)

# Retrieval evaluator for ubinary embedding type
retriever_evaluator_ubinary = RetrieverEvaluator.from_metric_names(
    metrics, retriever=retriver_ubinary
)

```

from llama_index.core.evaluation import RetrieverEvaluator metrics = ["mrr", "hit_rate"] # Retrieval evaluator for float embedding type retriever_evaluator_float = RetrieverEvaluator.from_metric_names( metrics, retriever=retriver_float ) # Retrieval evaluator for int8 embedding type retriever_evaluator_int8 = RetrieverEvaluator.from_metric_names( metrics, retriever=retriver_int8 ) # Retrieval evaluator for binary embedding type retriever_evaluator_binary = RetrieverEvaluator.from_metric_names( metrics, retriever=retriver_binary ) # Retrieval evaluator for ubinary embedding type retriever_evaluator_ubinary = RetrieverEvaluator.from_metric_names( metrics, retriever=retriver_ubinary )
In [ ]:
Copied!
```
# try it out on a sample query
sample_id, sample_query = list(qa_dataset.queries.items())[0]
sample_expected = qa_dataset.relevant_docs[sample_id]

eval_result = retriever_evaluator_float.evaluate(sample_query, sample_expected)
print(eval_result)

```

# try it out on a sample query sample_id, sample_query = list(qa_dataset.queries.items())[0] sample_expected = qa_dataset.relevant_docs[sample_id] eval_result = retriever_evaluator_float.evaluate(sample_query, sample_expected) print(eval_result)
```
Query: "Describe the author's initial experiences with programming on the IBM 1401. What were some of the challenges he faced and how did these experiences shape his understanding of programming?"
Metrics: {'mrr': 0.5, 'hit_rate': 1.0}


```

In [ ]:
Copied!
```
# Evaluation on the entire dataset

# float embedding type
eval_results_float = await retriever_evaluator_float.aevaluate_dataset(
    qa_dataset
)

# int8 embedding type
eval_results_int8 = await retriever_evaluator_int8.aevaluate_dataset(
    qa_dataset
)

# binary embedding type
eval_results_binary = await retriever_evaluator_binary.aevaluate_dataset(
    qa_dataset
)

# ubinary embedding type
eval_results_ubinary = await retriever_evaluator_ubinary.aevaluate_dataset(
    qa_dataset
)

```

# Evaluation on the entire dataset # float embedding type eval_results_float = await retriever_evaluator_float.aevaluate_dataset( qa_dataset ) # int8 embedding type eval_results_int8 = await retriever_evaluator_int8.aevaluate_dataset( qa_dataset ) # binary embedding type eval_results_binary = await retriever_evaluator_binary.aevaluate_dataset( qa_dataset ) # ubinary embedding type eval_results_ubinary = await retriever_evaluator_ubinary.aevaluate_dataset( qa_dataset )
#### Define `display_results` to get the display the results in dataframe with each retriever.¶
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

    hit_rate = full_df["hit_rate"].mean()
    mrr = full_df["mrr"].mean()
    columns = {"Embedding Type": [name], "hit_rate": [hit_rate], "mrr": [mrr]}

    metric_df = pd.DataFrame(columns)

    return metric_df

```

import pandas as pd def display_results(name, eval_results): """Display results from evaluate.""" metric_dicts = [] for eval_result in eval_results: metric_dict = eval_result.metric_vals_dict metric_dicts.append(metric_dict) full_df = pd.DataFrame(metric_dicts) hit_rate = full_df["hit_rate"].mean() mrr = full_df["mrr"].mean() columns = {"Embedding Type": [name], "hit_rate": [hit_rate], "mrr": [mrr]} metric_df = pd.DataFrame(columns) return metric_df
## Evaluation Results¶
In [ ]:
Copied!
```
# metrics for float embedding type
metrics_float = display_results("float", eval_results_float)

# metrics for int8 embedding type
metrics_int8 = display_results("int8", eval_results_int8)

# metrics for binary embedding type
metrics_binary = display_results("binary", eval_results_binary)

# metrics for ubinary embedding type
metrics_ubinary = display_results("ubinary", eval_results_ubinary)

```

# metrics for float embedding type metrics_float = display_results("float", eval_results_float) # metrics for int8 embedding type metrics_int8 = display_results("int8", eval_results_int8) # metrics for binary embedding type metrics_binary = display_results("binary", eval_results_binary) # metrics for ubinary embedding type metrics_ubinary = display_results("ubinary", eval_results_ubinary)
In [ ]:
Copied!
```
combined_metrics = pd.concat(
    [metrics_float, metrics_int8, metrics_binary, metrics_ubinary]
)
combined_metrics.set_index(["Embedding Type"], append=True, inplace=True)

```

combined_metrics = pd.concat( [metrics_float, metrics_int8, metrics_binary, metrics_ubinary] ) combined_metrics.set_index(["Embedding Type"], append=True, inplace=True)
In [ ]:
Copied!
```
combined_metrics

```

combined_metrics
Out[ ]:
|  | hit_rate | mrr  
---|---|---|---  
| Embedding Type |  |   
0 | float | 0.805085 | 0.665254  
int8 | 0.813559 | 0.673729  
binary | 0.491525 | 0.394068  
ubinary | 0.449153 | 0.377119  
# Note: The results shown above are very specific to dataset, and various other parameters considered. We recommend you to use the notebook as reference to experiment on your dataset and evaluate the usage of different embedding types in your RAG pipeline.¶
