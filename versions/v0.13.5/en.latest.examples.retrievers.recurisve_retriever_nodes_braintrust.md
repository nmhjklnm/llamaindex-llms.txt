![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Recursive Retriever + Node References + Braintrust¶
This guide shows how you can use recursive retrieval to traverse node relationships and fetch nodes based on "references".
Node references are a powerful concept. When you first perform retrieval, you may want to retrieve the reference as opposed to the raw text. You can have multiple references point to the same node.
In this guide we explore some different usages of node references:
  * **Chunk references** : Different chunk sizes referring to a bigger chunk
  * **Metadata references** : Summaries + Generated Questions referring to a bigger chunk


We evaluate how well our recursive retrieval + node reference methods work using Braintrust. Braintrust is the enterprise-grade stack for building AI products. From evaluations, to prompt playground, to data management, we take uncertainty and tedium out of incorporating AI into your business.
You can see example evaluation dashboards here for the:
  * base retriever
  * recursive metadata retreiver
  * recursive chunk retriever


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
%load_ext autoreload
%autoreload 2
# NOTE: Replace YOUR_OPENAI_API_KEY with your OpenAI API Key and YOUR_BRAINTRUST_API_KEY with your BrainTrust API key. Do not put it in quotes.
# Signup for Braintrust at https://braintrustdata.com/ and get your API key at https://www.braintrustdata.com/app/braintrustdata.com/settings/api-keys
# NOTE: Replace YOUR_OPENAI_KEY with your OpenAI API Key and YOUR_BRAINTRUST_API_KEY with your BrainTrust API key. Do not put it in quotes.
%env OPENAI_API_KEY=
%env BRAINTRUST_API_KEY=
%env TOKENIZERS_PARALLELISM=true # This is needed to avoid a warning message from Chroma

```

%load_ext autoreload %autoreload 2 # NOTE: Replace YOUR_OPENAI_API_KEY with your OpenAI API Key and YOUR_BRAINTRUST_API_KEY with your BrainTrust API key. Do not put it in quotes. # Signup for Braintrust at https://braintrustdata.com/ and get your API key at https://www.braintrustdata.com/app/braintrustdata.com/settings/api-keys # NOTE: Replace YOUR_OPENAI_KEY with your OpenAI API Key and YOUR_BRAINTRUST_API_KEY with your BrainTrust API key. Do not put it in quotes. %env OPENAI_API_KEY= %env BRAINTRUST_API_KEY= %env TOKENIZERS_PARALLELISM=true # This is needed to avoid a warning message from Chroma
In [ ]:
Copied!
```
%pip install -U llama_hub llama_index braintrust autoevals pypdf pillow transformers torch torchvision

```

%pip install -U llama_hub llama_index braintrust autoevals pypdf pillow transformers torch torchvision
## Load Data + Setup¶
In this section we download the Llama 2 paper and create an initial set of nodes (chunk size 1024).
In [ ]:
Copied!
```
!mkdir data
!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"

```

!mkdir data !wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"
In [ ]:
Copied!
```
from pathlib import Path
from llama_index.readers.file import PDFReader
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
import json

```

from pathlib import Path from llama_index.readers.file import PDFReader from llama_index.core.response.notebook_utils import display_source_node from llama_index.core.retrievers import RecursiveRetriever from llama_index.core.query_engine import RetrieverQueryEngine from llama_index.core import VectorStoreIndex from llama_index.llms.openai import OpenAI import json
In [ ]:
Copied!
```
loader = PDFReader()
docs0 = loader.load_data(file=Path("./data/llama2.pdf"))

```

loader = PDFReader() docs0 = loader.load_data(file=Path("./data/llama2.pdf"))
In [ ]:
Copied!
```
from llama_index.core import Document

doc_text = "\n\n".join([d.get_content() for d in docs0])
docs = [Document(text=doc_text)]

```

from llama_index.core import Document doc_text = "\n\n".join([d.get_content() for d in docs0]) docs = [Document(text=doc_text)]
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import IndexNode

```

from llama_index.core.node_parser import SentenceSplitter from llama_index.core.schema import IndexNode
In [ ]:
Copied!
```
node_parser = SentenceSplitter(chunk_size=1024)

```

node_parser = SentenceSplitter(chunk_size=1024)
In [ ]:
Copied!
```
base_nodes = node_parser.get_nodes_from_documents(docs)
# set node ids to be a constant
for idx, node in enumerate(base_nodes):
    node.id_ = f"node-{idx}"

```

base_nodes = node_parser.get_nodes_from_documents(docs) # set node ids to be a constant for idx, node in enumerate(base_nodes): node.id_ = f"node-{idx}"
In [ ]:
Copied!
```
from llama_index.core.embeddings import resolve_embed_model

embed_model = resolve_embed_model("local:BAAI/bge-small-en")
llm = OpenAI(model="gpt-3.5-turbo")

```

from llama_index.core.embeddings import resolve_embed_model embed_model = resolve_embed_model("local:BAAI/bge-small-en") llm = OpenAI(model="gpt-3.5-turbo")
## Baseline Retriever¶
Define a baseline retriever that simply fetches the top-k raw text nodes by embedding similarity.
In [ ]:
Copied!
```
base_index = VectorStoreIndex(base_nodes, embed_model=embed_model)
base_retriever = base_index.as_retriever(similarity_top_k=2)

```

base_index = VectorStoreIndex(base_nodes, embed_model=embed_model) base_retriever = base_index.as_retriever(similarity_top_k=2)
In [ ]:
Copied!
```
retrievals = base_retriever.retrieve(
    "Can you tell me about the key concepts for safety finetuning"
)

```

retrievals = base_retriever.retrieve( "Can you tell me about the key concepts for safety finetuning" )
In [ ]:
Copied!
```
for n in retrievals:
    display_source_node(n, source_length=1500)

```

for n in retrievals: display_source_node(n, source_length=1500)
In [ ]:
Copied!
```
query_engine_base = RetrieverQueryEngine.from_args(base_retriever, llm=llm)

```

query_engine_base = RetrieverQueryEngine.from_args(base_retriever, llm=llm)
In [ ]:
Copied!
```
response = query_engine_base.query(
    "Can you tell me about the key concepts for safety finetuning"
)
print(str(response))

```

response = query_engine_base.query( "Can you tell me about the key concepts for safety finetuning" ) print(str(response))
## Chunk References: Smaller Child Chunks Referring to Bigger Parent Chunk¶
In this usage example, we show how to build a graph of smaller chunks pointing to bigger parent chunks.
During query-time, we retrieve smaller chunks, but we follow references to bigger chunks. This allows us to have more context for synthesis.
In [ ]:
Copied!
```
sub_chunk_sizes = [128, 256, 512]
sub_node_parsers = [SentenceSplitter(chunk_size=c) for c in sub_chunk_sizes]

all_nodes = []

for base_node in base_nodes:
    for n in sub_node_parsers:
        sub_nodes = n.get_nodes_from_documents([base_node])
        sub_inodes = [
            IndexNode.from_text_node(sn, base_node.node_id) for sn in sub_nodes
        ]
        all_nodes.extend(sub_inodes)

    # also add original node to node
    original_node = IndexNode.from_text_node(base_node, base_node.node_id)
    all_nodes.append(original_node)

```

sub_chunk_sizes = [128, 256, 512] sub_node_parsers = [SentenceSplitter(chunk_size=c) for c in sub_chunk_sizes] all_nodes = [] for base_node in base_nodes: for n in sub_node_parsers: sub_nodes = n.get_nodes_from_documents([base_node]) sub_inodes = [ IndexNode.from_text_node(sn, base_node.node_id) for sn in sub_nodes ] all_nodes.extend(sub_inodes) # also add original node to node original_node = IndexNode.from_text_node(base_node, base_node.node_id) all_nodes.append(original_node)
In [ ]:
Copied!
```
all_nodes_dict = {n.node_id: n for n in all_nodes}

```

all_nodes_dict = {n.node_id: n for n in all_nodes}
In [ ]:
Copied!
```
vector_index_chunk = VectorStoreIndex(all_nodes, embed_model=embed_model)

```

vector_index_chunk = VectorStoreIndex(all_nodes, embed_model=embed_model)
In [ ]:
Copied!
```
vector_retriever_chunk = vector_index_chunk.as_retriever(similarity_top_k=2)

```

vector_retriever_chunk = vector_index_chunk.as_retriever(similarity_top_k=2)
In [ ]:
Copied!
```
retriever_chunk = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_chunk},
    node_dict=all_nodes_dict,
    verbose=True,
)

```

retriever_chunk = RecursiveRetriever( "vector", retriever_dict={"vector": vector_retriever_chunk}, node_dict=all_nodes_dict, verbose=True, )
In [ ]:
Copied!
```
nodes = retriever_chunk.retrieve(
    "Can you tell me about the key concepts for safety finetuning"
)
for node in nodes:
    display_source_node(node, source_length=2000)

```

nodes = retriever_chunk.retrieve( "Can you tell me about the key concepts for safety finetuning" ) for node in nodes: display_source_node(node, source_length=2000)
In [ ]:
Copied!
```
query_engine_chunk = RetrieverQueryEngine.from_args(retriever_chunk, llm=llm)

```

query_engine_chunk = RetrieverQueryEngine.from_args(retriever_chunk, llm=llm)
In [ ]:
Copied!
```
response = query_engine_chunk.query(
    "Can you tell me about the key concepts for safety finetuning"
)
print(str(response))

```

response = query_engine_chunk.query( "Can you tell me about the key concepts for safety finetuning" ) print(str(response))
## Metadata References: Summaries + Generated Questions referring to a bigger chunk¶
In this usage example, we show how to define additional context that references the source node.
This additional context includes summaries as well as generated questions.
During query-time, we retrieve smaller chunks, but we follow references to bigger chunks. This allows us to have more context for synthesis.
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import IndexNode
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
)

```

from llama_index.core.node_parser import SentenceSplitter from llama_index.core.schema import IndexNode from llama_index.core.extractors import ( SummaryExtractor, QuestionsAnsweredExtractor, )
In [ ]:
Copied!
```
extractors = [
    SummaryExtractor(summaries=["self"], show_progress=True),
    QuestionsAnsweredExtractor(questions=5, show_progress=True),
]

```

extractors = [ SummaryExtractor(summaries=["self"], show_progress=True), QuestionsAnsweredExtractor(questions=5, show_progress=True), ]
In [ ]:
Copied!
```
# run metadata extractor across base nodes, get back dictionaries
metadata_dicts = []
for extractor in extractors:
    metadata_dicts.extend(extractor.extract(base_nodes))

```

# run metadata extractor across base nodes, get back dictionaries metadata_dicts = [] for extractor in extractors: metadata_dicts.extend(extractor.extract(base_nodes))
In [ ]:
Copied!
```
# cache metadata dicts
def save_metadata_dicts(path):
    with open(path, "w") as fp:
        for m in metadata_dicts:
            fp.write(json.dumps(m) + "\n")


def load_metadata_dicts(path):
    with open(path, "r") as fp:
        metadata_dicts = [json.loads(l) for l in fp.readlines()]
        return metadata_dicts

```

# cache metadata dicts def save_metadata_dicts(path): with open(path, "w") as fp: for m in metadata_dicts: fp.write(json.dumps(m) + "\n") def load_metadata_dicts(path): with open(path, "r") as fp: metadata_dicts = [json.loads(l) for l in fp.readlines()] return metadata_dicts
In [ ]:
Copied!
```
save_metadata_dicts("data/llama2_metadata_dicts.jsonl")

```

save_metadata_dicts("data/llama2_metadata_dicts.jsonl")
In [ ]:
Copied!
```
metadata_dicts = load_metadata_dicts("data/llama2_metadata_dicts.jsonl")

```

metadata_dicts = load_metadata_dicts("data/llama2_metadata_dicts.jsonl")
In [ ]:
Copied!
```
# all nodes consists of source nodes, along with metadata
import copy

all_nodes = copy.deepcopy(base_nodes)
for idx, d in enumerate(metadata_dicts):
    inode_q = IndexNode(
        text=d["questions_this_excerpt_can_answer"],
        index_id=base_nodes[idx].node_id,
    )
    inode_s = IndexNode(
        text=d["section_summary"], index_id=base_nodes[idx].node_id
    )
    all_nodes.extend([inode_q, inode_s])

```

# all nodes consists of source nodes, along with metadata import copy all_nodes = copy.deepcopy(base_nodes) for idx, d in enumerate(metadata_dicts): inode_q = IndexNode( text=d["questions_this_excerpt_can_answer"], index_id=base_nodes[idx].node_id, ) inode_s = IndexNode( text=d["section_summary"], index_id=base_nodes[idx].node_id ) all_nodes.extend([inode_q, inode_s])
In [ ]:
Copied!
```
all_nodes_dict = {n.node_id: n for n in all_nodes}

```

all_nodes_dict = {n.node_id: n for n in all_nodes}
In [ ]:
Copied!
```
## Load index into vector index
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo")

vector_index_metadata = VectorStoreIndex(all_nodes)

```

## Load index into vector index from llama_index.core import VectorStoreIndex from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo") vector_index_metadata = VectorStoreIndex(all_nodes)
In [ ]:
Copied!
```
vector_retriever_metadata = vector_index_metadata.as_retriever(
    similarity_top_k=2
)

```

vector_retriever_metadata = vector_index_metadata.as_retriever( similarity_top_k=2 )
In [ ]:
Copied!
```
retriever_metadata = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_metadata},
    node_dict=all_nodes_dict,
    verbose=True,
)

```

retriever_metadata = RecursiveRetriever( "vector", retriever_dict={"vector": vector_retriever_metadata}, node_dict=all_nodes_dict, verbose=True, )
In [ ]:
Copied!
```
nodes = retriever_metadata.retrieve(
    "Can you tell me about the key concepts for safety finetuning"
)
for node in nodes:
    display_source_node(node, source_length=2000)

```

nodes = retriever_metadata.retrieve( "Can you tell me about the key concepts for safety finetuning" ) for node in nodes: display_source_node(node, source_length=2000)
In [ ]:
Copied!
```
query_engine_metadata = RetrieverQueryEngine.from_args(
    retriever_metadata, llm=llm
)

```

query_engine_metadata = RetrieverQueryEngine.from_args( retriever_metadata, llm=llm )
In [ ]:
Copied!
```
response = query_engine_metadata.query(
    "Can you tell me about the key concepts for safety finetuning"
)
print(str(response))

```

response = query_engine_metadata.query( "Can you tell me about the key concepts for safety finetuning" ) print(str(response))
## Evaluation¶
We evaluate how well our recursive retrieval + node reference methods work using Braintrust. Braintrust is the enterprise-grade stack for building AI products. From evaluations, to prompt playground, to data management, we take uncertainty and tedium out of incorporating AI into your business.
We evaluate both chunk references as well as metadata references. We use embedding similarity lookup to retrieve the reference nodes. We compare both methods against a baseline retriever where we fetch the raw nodes directly. In terms of metrics, we evaluate using both hit-rate and MRR.
You can see example evaluation dashboards here for the:
  * base retriever
  * recursive metadata retreiver
  * recursive chunk retriever


### Dataset Generation¶
We first generate a dataset of questions from the set of text chunks.
In [ ]:
Copied!
```
from llama_index.core.evaluation import (
    generate_question_context_pairs,
    EmbeddingQAFinetuneDataset,
)
import nest_asyncio

nest_asyncio.apply()

```

from llama_index.core.evaluation import ( generate_question_context_pairs, EmbeddingQAFinetuneDataset, ) import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
eval_dataset = generate_question_context_pairs(base_nodes)

```

eval_dataset = generate_question_context_pairs(base_nodes)
In [ ]:
Copied!
```
eval_dataset.save_json("data/llama2_eval_dataset.json")

```

eval_dataset.save_json("data/llama2_eval_dataset.json")
In [ ]:
Copied!
```
# optional
eval_dataset = EmbeddingQAFinetuneDataset.from_json(
    "data/llama2_eval_dataset.json"
)

```

# optional eval_dataset = EmbeddingQAFinetuneDataset.from_json( "data/llama2_eval_dataset.json" )
### Compare Results¶
We run evaluations on each of the retrievers to measure hit rate and MRR.
We find that retrievers with node references (either chunk or metadata) tend to perform better than retrieving the raw chunks.
In [ ]:
Copied!
```
import pandas as pd

# set vector retriever similarity top k to higher
top_k = 10


def display_results(names, results_arr):
    """Display results from evaluate."""

    hit_rates = []
    mrrs = []
    for name, eval_results in zip(names, results_arr):
        metric_dicts = []
        for eval_result in eval_results:
            metric_dict = eval_result.metric_vals_dict
            metric_dicts.append(metric_dict)
        results_df = pd.DataFrame(metric_dicts)

        hit_rate = results_df["hit_rate"].mean()
        mrr = results_df["mrr"].mean()
        hit_rates.append(hit_rate)
        mrrs.append(mrr)

    final_df = pd.DataFrame(
        {"retrievers": names, "hit_rate": hit_rates, "mrr": mrrs}
    )
    display(final_df)

```

import pandas as pd # set vector retriever similarity top k to higher top_k = 10 def display_results(names, results_arr): """Display results from evaluate.""" hit_rates = [] mrrs = [] for name, eval_results in zip(names, results_arr): metric_dicts = [] for eval_result in eval_results: metric_dict = eval_result.metric_vals_dict metric_dicts.append(metric_dict) results_df = pd.DataFrame(metric_dicts) hit_rate = results_df["hit_rate"].mean() mrr = results_df["mrr"].mean() hit_rates.append(hit_rate) mrrs.append(mrr) final_df = pd.DataFrame( {"retrievers": names, "hit_rate": hit_rates, "mrr": mrrs} ) display(final_df)
Let's define some scoring functions and define our dataset data variable.
In [ ]:
Copied!
```
queries = eval_dataset.queries
relevant_docs = eval_dataset.relevant_docs
data = [
    ({"input": queries[query], "expected": relevant_docs[query]})
    for query in queries.keys()
]


def hitRateScorer(input, expected, output=None):
    is_hit = any([id in expected for id in output])
    return 1 if is_hit else 0


def mrrScorer(input, expected, output=None):
    for i, id in enumerate(output):
        if id in expected:
            return 1 / (i + 1)
    return 0

```

queries = eval_dataset.queries relevant_docs = eval_dataset.relevant_docs data = [ ({"input": queries[query], "expected": relevant_docs[query]}) for query in queries.keys() ] def hitRateScorer(input, expected, output=None): is_hit = any([id in expected for id in output]) return 1 if is_hit else 0 def mrrScorer(input, expected, output=None): for i, id in enumerate(output): if id in expected: return 1 / (i + 1) return 0
In [ ]:
Copied!
```
import braintrust

# Evaluate the chunk retriever
vector_retriever_chunk = vector_index_chunk.as_retriever(similarity_top_k=10)
retriever_chunk = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_chunk},
    node_dict=all_nodes_dict,
    verbose=False,
)


def runChunkRetriever(input, hooks):
    retrieved_nodes = retriever_chunk.retrieve(input)
    retrieved_ids = [node.node.node_id for node in retrieved_nodes]
    return retrieved_ids


chunkEval = await braintrust.Eval(
    name="llamaindex-recurisve-retrievers",
    data=data,
    task=runChunkRetriever,
    scores=[hitRateScorer, mrrScorer],
)

```

import braintrust # Evaluate the chunk retriever vector_retriever_chunk = vector_index_chunk.as_retriever(similarity_top_k=10) retriever_chunk = RecursiveRetriever( "vector", retriever_dict={"vector": vector_retriever_chunk}, node_dict=all_nodes_dict, verbose=False, ) def runChunkRetriever(input, hooks): retrieved_nodes = retriever_chunk.retrieve(input) retrieved_ids = [node.node.node_id for node in retrieved_nodes] return retrieved_ids chunkEval = await braintrust.Eval( name="llamaindex-recurisve-retrievers", data=data, task=runChunkRetriever, scores=[hitRateScorer, mrrScorer], )
In [ ]:
Copied!
```
# Evaluate the metadata retriever

vector_retriever_metadata = vector_index_metadata.as_retriever(
    similarity_top_k=10
)
retriever_metadata = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_metadata},
    node_dict=all_nodes_dict,
    verbose=False,
)


def runMetaDataRetriever(input, hooks):
    retrieved_nodes = retriever_metadata.retrieve(input)
    retrieved_ids = [node.node.node_id for node in retrieved_nodes]
    return retrieved_ids


metadataEval = await braintrust.Eval(
    name="llamaindex-recurisve-retrievers",
    data=data,
    task=runMetaDataRetriever,
    scores=[hitRateScorer, mrrScorer],
)

```

# Evaluate the metadata retriever vector_retriever_metadata = vector_index_metadata.as_retriever( similarity_top_k=10 ) retriever_metadata = RecursiveRetriever( "vector", retriever_dict={"vector": vector_retriever_metadata}, node_dict=all_nodes_dict, verbose=False, ) def runMetaDataRetriever(input, hooks): retrieved_nodes = retriever_metadata.retrieve(input) retrieved_ids = [node.node.node_id for node in retrieved_nodes] return retrieved_ids metadataEval = await braintrust.Eval( name="llamaindex-recurisve-retrievers", data=data, task=runMetaDataRetriever, scores=[hitRateScorer, mrrScorer], )
In [ ]:
Copied!
```
# Evaluate the base retriever
base_retriever = base_index.as_retriever(similarity_top_k=10)


def runBaseRetriever(input, hooks):
    retrieved_nodes = base_retriever.retrieve(input)
    retrieved_ids = [node.node.node_id for node in retrieved_nodes]
    return retrieved_ids


baseEval = await braintrust.Eval(
    name="llamaindex-recurisve-retrievers",
    data=data,
    task=runBaseRetriever,
    scores=[hitRateScorer, mrrScorer],
)

```

# Evaluate the base retriever base_retriever = base_index.as_retriever(similarity_top_k=10) def runBaseRetriever(input, hooks): retrieved_nodes = base_retriever.retrieve(input) retrieved_ids = [node.node.node_id for node in retrieved_nodes] return retrieved_ids baseEval = await braintrust.Eval( name="llamaindex-recurisve-retrievers", data=data, task=runBaseRetriever, scores=[hitRateScorer, mrrScorer], )
