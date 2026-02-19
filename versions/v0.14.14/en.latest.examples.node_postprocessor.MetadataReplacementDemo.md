![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Metadata Replacement + Node Sentence Window¶
In this notebook, we use the `SentenceWindowNodeParser` to parse documents into single sentences per node. Each node also contains a "window" with the sentences on either side of the node sentence.
Then, after retrieval, before passing the retrieved sentences to the LLM, the single sentences are replaced with a window containing the surrounding sentences using the `MetadataReplacementNodePostProcessor`.
This is most useful for large documents/indexes, as it helps to retrieve more fine-grained details.
By default, the sentence window is 5 sentences on either side of the original sentence.
In this case, chunk size settings are not used, in favor of following the window settings.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-embeddings-huggingface
%pip install llama-index-llms-openai

```

%pip install llama-index-embeddings-openai %pip install llama-index-embeddings-huggingface %pip install llama-index-llms-openai
In [ ]:
Copied!
```
%load_ext autoreload
%autoreload 2

```

%load_ext autoreload %autoreload 2
## Setup¶
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
import os
import openai

```

import os import openai
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "sk-..."

```

os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.node_parser import SentenceSplitter

# create the sentence window node parser w/ default settings
node_parser = SentenceWindowNodeParser.from_defaults(
    window_size=3,
    window_metadata_key="window",
    original_text_metadata_key="original_text",
)

# base node parser is a sentence splitter
text_splitter = SentenceSplitter()

llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)
embed_model = HuggingFaceEmbedding(
    model_name="sentence-transformers/all-mpnet-base-v2", max_length=512
)

from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model
Settings.text_splitter = text_splitter

```

from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.embeddings.huggingface import HuggingFaceEmbedding from llama_index.core.node_parser import SentenceWindowNodeParser from llama_index.core.node_parser import SentenceSplitter # create the sentence window node parser w/ default settings node_parser = SentenceWindowNodeParser.from_defaults( window_size=3, window_metadata_key="window", original_text_metadata_key="original_text", ) # base node parser is a sentence splitter text_splitter = SentenceSplitter() llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1) embed_model = HuggingFaceEmbedding( model_name="sentence-transformers/all-mpnet-base-v2", max_length=512 ) from llama_index.core import Settings Settings.llm = llm Settings.embed_model = embed_model Settings.text_splitter = text_splitter
## Load Data, Build the Index¶
In this section, we load data and build the vector index.
### Load Data¶
Here, we build an index using chapter 3 of the recent IPCC climate report.
In [ ]:
Copied!
```
!curl https://www.ipcc.ch/report/ar6/wg2/downloads/report/IPCC_AR6_WGII_Chapter03.pdf --output IPCC_AR6_WGII_Chapter03.pdf

```

!curl https://www.ipcc.ch/report/ar6/wg2/downloads/report/IPCC_AR6_WGII_Chapter03.pdf --output IPCC_AR6_WGII_Chapter03.pdf
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0curl: (6) Could not resolve host: www..ch

```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader(
    input_files=["./IPCC_AR6_WGII_Chapter03.pdf"]
).load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader( input_files=["./IPCC_AR6_WGII_Chapter03.pdf"] ).load_data()
### Extract Nodes¶
We extract out the set of nodes that will be stored in the VectorIndex. This includes both the nodes with the sentence window parser, as well as the "base" nodes extracted using the standard parser.
In [ ]:
Copied!
```
nodes = node_parser.get_nodes_from_documents(documents)

```

nodes = node_parser.get_nodes_from_documents(documents)
In [ ]:
Copied!
```
base_nodes = text_splitter.get_nodes_from_documents(documents)

```

base_nodes = text_splitter.get_nodes_from_documents(documents)
### Build the Indexes¶
We build both the sentence index, as well as the "base" index (with default chunk sizes).
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

sentence_index = VectorStoreIndex(nodes)

```

from llama_index.core import VectorStoreIndex sentence_index = VectorStoreIndex(nodes)
In [ ]:
Copied!
```
base_index = VectorStoreIndex(base_nodes)

```

base_index = VectorStoreIndex(base_nodes)
## Querying¶
### With MetadataReplacementPostProcessor¶
Here, we now use the `MetadataReplacementPostProcessor` to replace the sentence in each node with it's surrounding context.
In [ ]:
Copied!
```
from llama_index.core.postprocessor import MetadataReplacementPostProcessor

query_engine = sentence_index.as_query_engine(
    similarity_top_k=2,
    # the target key defaults to `window` to match the node_parser's default
    node_postprocessors=[
        MetadataReplacementPostProcessor(target_metadata_key="window")
    ],
)
window_response = query_engine.query(
    "What are the concerns surrounding the AMOC?"
)
print(window_response)

```

from llama_index.core.postprocessor import MetadataReplacementPostProcessor query_engine = sentence_index.as_query_engine( similarity_top_k=2, # the target key defaults to `window` to match the node_parser's default node_postprocessors=[ MetadataReplacementPostProcessor(target_metadata_key="window") ], ) window_response = query_engine.query( "What are the concerns surrounding the AMOC?" ) print(window_response)
```
There is low confidence in the quantification of Atlantic Meridional Overturning Circulation (AMOC) changes in the 20th century due to low agreement in quantitative reconstructed and simulated trends. Additionally, direct observational records since the mid-2000s remain too short to determine the relative contributions of internal variability, natural forcing, and anthropogenic forcing to AMOC change. However, it is very likely that AMOC will decline for all SSP scenarios over the 21st century, but it will not involve an abrupt collapse before 2100.

```

We can also check the original sentence that was retrieved for each node, as well as the actual window of sentences that was sent to the LLM.
In [ ]:
Copied!
```
window = window_response.source_nodes[0].node.metadata["window"]
sentence = window_response.source_nodes[0].node.metadata["original_text"]

print(f"Window: {window}")
print("------------------")
print(f"Original Sentence: {sentence}")

```

window = window_response.source_nodes[0].node.metadata["window"] sentence = window_response.source_nodes[0].node.metadata["original_text"] print(f"Window: {window}") print("------------------") print(f"Original Sentence: {sentence}")
```
Window: Nevertheless, projected future annual cumulative upwelling wind 
changes at most locations and seasons remain within ±10–20% of 
present-day values (medium confidence) (WGI AR6 Section  9.2.3.5; 
Fox-Kemper et al., 2021).
 Continuous observation of the Atlantic meridional overturning 
circulation (AMOC) has improved the understanding of its variability 
(Frajka-Williams et  al., 2019), but there is low confidence in the 
quantification of AMOC changes in the 20th century because of low 
agreement in quantitative reconstructed and simulated trends (WGI 
AR6 Sections 2.3.3, 9.2.3.1; Fox-Kemper et al., 2021; Gulev et al., 2021). 
 Direct observational records since the mid-2000s remain too short to 
determine the relative contributions of internal variability, natural 
forcing and anthropogenic forcing to AMOC change (high confidence) 
(WGI AR6 Sections 2.3.3, 9.2.3.1; Fox-Kemper et al., 2021; Gulev et al., 
2021).  Over the 21st century, AMOC will very likely decline for all SSP 
scenarios but will not involve an abrupt collapse before 2100 (WGI 
AR6 Sections 4.3.2, 9.2.3.1; Fox-Kemper et al., 2021; Lee et al., 2021).
 3.2.2.4 Sea Ice Changes
Sea ice is a key driver of polar marine life, hosting unique ecosystems 
and affecting diverse marine organisms and food webs through its 
impact on light penetration and supplies of nutrients and organic 
matter (Arrigo, 2014).  Since the late 1970s, Arctic sea ice area has 
decreased for all months, with an estimated decrease of 2 million km2 
(or 25%) for summer sea ice (averaged for August, September and 
October) in 2010–2019 as compared with 1979–1988 (WGI AR6 
Section 9.3.1.1; Fox-Kemper et al., 2021). 
------------------
Original Sentence: Over the 21st century, AMOC will very likely decline for all SSP 
scenarios but will not involve an abrupt collapse before 2100 (WGI 
AR6 Sections 4.3.2, 9.2.3.1; Fox-Kemper et al., 2021; Lee et al., 2021).

```

### Contrast with normal VectorStoreIndex¶
In [ ]:
Copied!
```
query_engine = base_index.as_query_engine(similarity_top_k=2)
vector_response = query_engine.query(
    "What are the concerns surrounding the AMOC?"
)
print(vector_response)

```

query_engine = base_index.as_query_engine(similarity_top_k=2) vector_response = query_engine.query( "What are the concerns surrounding the AMOC?" ) print(vector_response)
```
The concerns surrounding the AMOC are not provided in the given context information.

```

Well, that didn't work. Let's bump up the top k! This will be slower and use more tokens compared to the sentence window index.
In [ ]:
Copied!
```
query_engine = base_index.as_query_engine(similarity_top_k=5)
vector_response = query_engine.query(
    "What are the concerns surrounding the AMOC?"
)
print(vector_response)

```

query_engine = base_index.as_query_engine(similarity_top_k=5) vector_response = query_engine.query( "What are the concerns surrounding the AMOC?" ) print(vector_response)
```
There are concerns surrounding the AMOC (Atlantic Meridional Overturning Circulation). The context information mentions that the AMOC will decline over the 21st century, with high confidence but low confidence for quantitative projections.

```

## Analysis¶
So the `SentenceWindowNodeParser` + `MetadataReplacementNodePostProcessor` combo is the clear winner here. But why?
Embeddings at a sentence level seem to capture more fine-grained details, like the word `AMOC`.
We can also compare the retrieved chunks for each index!
In [ ]:
Copied!
```
for source_node in window_response.source_nodes:
    print(source_node.node.metadata["original_text"])
    print("--------")

```

for source_node in window_response.source_nodes: print(source_node.node.metadata["original_text"]) print("--------")
```
Over the 21st century, AMOC will very likely decline for all SSP 
scenarios but will not involve an abrupt collapse before 2100 (WGI 
AR6 Sections 4.3.2, 9.2.3.1; Fox-Kemper et al., 2021; Lee et al., 2021).

--------
Direct observational records since the mid-2000s remain too short to 
determine the relative contributions of internal variability, natural 
forcing and anthropogenic forcing to AMOC change (high confidence) 
(WGI AR6 Sections 2.3.3, 9.2.3.1; Fox-Kemper et al., 2021; Gulev et al., 
2021). 
--------

```

Here, we can see that the sentence window index easily retrieved two nodes that talk about AMOC. Remember, the embeddings are based purely on the original sentence here, but the LLM actually ends up reading the surrounding context as well!
Now, let's try and disect why the naive vector index failed.
In [ ]:
Copied!
```
for node in vector_response.source_nodes:
    print("AMOC mentioned?", "AMOC" in node.node.text)
    print("--------")

```

for node in vector_response.source_nodes: print("AMOC mentioned?", "AMOC" in node.node.text) print("--------")
```
AMOC mentioned? False
--------
AMOC mentioned? False
--------
AMOC mentioned? True
--------
AMOC mentioned? False
--------
AMOC mentioned? False
--------

```

So source node at index [2] mentions AMOC, but what did this text actually look like?
In [ ]:
Copied!
```
print(vector_response.source_nodes[2].node.text)

```

print(vector_response.source_nodes[2].node.text)
```
2021; Gulev et al. 
2021)The AMOC will decline over the 21st century 
(high confidence, but low confidence for 
quantitative projections).4.3.2.3, 9.2.3 (Fox-Kemper 
et al. 2021; Lee et al. 
2021)
Sea ice
Arctic sea ice 
changes‘Current Arctic sea ice coverage levels are the 
lowest since at least 1850 for both annual mean 
and late-summer values (high confidence).’2.3.2.1, 9.3.1 (Fox-Kemper 
et al. 2021; Gulev et al. 
2021)‘The Arctic will become practically ice-free in 
September by the end of the 21st century under 
SSP2-4.5, SSP3-7.0 and SSP5-8.5[…](high 
confidence).’4.3.2.1, 9.3.1 (Fox-Kemper 
et al. 2021; Lee et al. 
2021)
Antarctic sea ice 
changesThere is no global significant trend in 
Antarctic sea ice area from 1979 to 2020 (high 
confidence).2.3.2.1, 9.3.2 (Fox-Kemper 
et al. 2021; Gulev et al. 
2021)There is low confidence in model simulations of 
future Antarctic sea ice.9.3.2 (Fox-Kemper et al. 
2021)
Ocean chemistry
Changes in salinityThe ‘large-scale, near-surface salinity contrasts 
have intensified since at least 1950 […] 
(virtually certain).’2.3.3.2, 9.2.2.2 
(Fox-Kemper et al. 2021; 
Gulev et al. 2021)‘Fresh ocean regions will continue to get fresher 
and salty ocean regions will continue to get 
saltier in the 21st century (medium confidence).’9.2.2.2 (Fox-Kemper et al. 
2021)
Ocean acidificationOcean surface pH has declined globally over the 
past four decades (virtually certain).2.3.3.5, 5.3.2.2 (Canadell 
et al. 2021; Gulev et al. 
2021)Ocean surface pH will continue to decrease 
‘through the 21st century, except for the 
lower-emission scenarios SSP1-1.9 and SSP1-2.6 
[…] (high confidence).’4.3.2.5, 4.5.2.2, 5.3.4.1 
(Lee et al. 2021; Canadell 
et al. 2021)
Ocean 
deoxygenationDeoxygenation has occurred in most open 
ocean regions since the mid-20th century (high 
confidence).2.3.3.6, 5.3.3.2 (Canadell 
et al. 2021; Gulev et al. 
2021)Subsurface oxygen content ‘is projected to 
transition to historically unprecedented condition 
with decline over the 21st century (medium 
confidence).’5.3.3.2 (Canadell et al. 
2021)
Changes in nutrient 
concentrationsNot assessed in WGI Not assessed in WGI

```

So AMOC is disuccsed, but sadly it is in the middle chunk. With LLMs, it is often observed that text in the middle of retrieved context is often ignored or less useful. A recent paper "Lost in the Middle" discusses this here.
## [Optional] Evaluation¶
We more rigorously evaluate how well the sentence window retriever works compared to the base retriever.
We define/load an eval benchmark dataset and then run different evaluations over it.
**WARNING** : This can be _expensive_ , especially with GPT-4. Use caution and tune the sample size to fit your budget.
In [ ]:
Copied!
```
from llama_index.core.evaluation import DatasetGenerator, QueryResponseDataset

from llama_index.llms.openai import OpenAI
import nest_asyncio
import random

nest_asyncio.apply()

```

from llama_index.core.evaluation import DatasetGenerator, QueryResponseDataset from llama_index.llms.openai import OpenAI import nest_asyncio import random nest_asyncio.apply()
In [ ]:
Copied!
```
len(base_nodes)

```

len(base_nodes)
Out[ ]:


In [ ]:
Copied!
```
num_nodes_eval = 30
# there are 428 nodes total. Take the first 200 to generate questions (the back half of the doc is all references)
sample_eval_nodes = random.sample(base_nodes[:200], num_nodes_eval)
# NOTE: run this if the dataset isn't already saved
# generate questions from the largest chunks (1024)
dataset_generator = DatasetGenerator(
    sample_eval_nodes,
    llm=OpenAI(model="gpt-4"),
    show_progress=True,
    num_questions_per_chunk=2,
)

```

num_nodes_eval = 30 # there are 428 nodes total. Take the first 200 to generate questions (the back half of the doc is all references) sample_eval_nodes = random.sample(base_nodes[:200], num_nodes_eval) # NOTE: run this if the dataset isn't already saved # generate questions from the largest chunks (1024) dataset_generator = DatasetGenerator( sample_eval_nodes, llm=OpenAI(model="gpt-4"), show_progress=True, num_questions_per_chunk=2, )
In [ ]:
Copied!
```
eval_dataset = await dataset_generator.agenerate_dataset_from_nodes()

```

eval_dataset = await dataset_generator.agenerate_dataset_from_nodes()
In [ ]:
Copied!
```
eval_dataset.save_json("data/ipcc_eval_qr_dataset.json")

```

eval_dataset.save_json("data/ipcc_eval_qr_dataset.json")
In [ ]:
Copied!
```
# optional
eval_dataset = QueryResponseDataset.from_json("data/ipcc_eval_qr_dataset.json")

```

# optional eval_dataset = QueryResponseDataset.from_json("data/ipcc_eval_qr_dataset.json")
### Compare Results¶
In [ ]:
Copied!
```
import asyncio
import nest_asyncio

nest_asyncio.apply()

```

import asyncio import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from llama_index.core.evaluation import (
    CorrectnessEvaluator,
    SemanticSimilarityEvaluator,
    RelevancyEvaluator,
    FaithfulnessEvaluator,
    PairwiseComparisonEvaluator,
)


from collections import defaultdict
import pandas as pd

# NOTE: can uncomment other evaluators
evaluator_c = CorrectnessEvaluator(llm=OpenAI(model="gpt-4"))
evaluator_s = SemanticSimilarityEvaluator()
evaluator_r = RelevancyEvaluator(llm=OpenAI(model="gpt-4"))
evaluator_f = FaithfulnessEvaluator(llm=OpenAI(model="gpt-4"))
# pairwise_evaluator = PairwiseComparisonEvaluator(llm=OpenAI(model="gpt-4"))

```

from llama_index.core.evaluation import ( CorrectnessEvaluator, SemanticSimilarityEvaluator, RelevancyEvaluator, FaithfulnessEvaluator, PairwiseComparisonEvaluator, ) from collections import defaultdict import pandas as pd # NOTE: can uncomment other evaluators evaluator_c = CorrectnessEvaluator(llm=OpenAI(model="gpt-4")) evaluator_s = SemanticSimilarityEvaluator() evaluator_r = RelevancyEvaluator(llm=OpenAI(model="gpt-4")) evaluator_f = FaithfulnessEvaluator(llm=OpenAI(model="gpt-4")) # pairwise_evaluator = PairwiseComparisonEvaluator(llm=OpenAI(model="gpt-4"))
In [ ]:
Copied!
```
from llama_index.core.evaluation.eval_utils import (
    get_responses,
    get_results_df,
)
from llama_index.core.evaluation import BatchEvalRunner

max_samples = 30

eval_qs = eval_dataset.questions
ref_response_strs = [r for (_, r) in eval_dataset.qr_pairs]

# resetup base query engine and sentence window query engine
# base query engine
base_query_engine = base_index.as_query_engine(similarity_top_k=2)
# sentence window query engine
query_engine = sentence_index.as_query_engine(
    similarity_top_k=2,
    # the target key defaults to `window` to match the node_parser's default
    node_postprocessors=[
        MetadataReplacementPostProcessor(target_metadata_key="window")
    ],
)

```

from llama_index.core.evaluation.eval_utils import ( get_responses, get_results_df, ) from llama_index.core.evaluation import BatchEvalRunner max_samples = 30 eval_qs = eval_dataset.questions ref_response_strs = [r for (_, r) in eval_dataset.qr_pairs] # resetup base query engine and sentence window query engine # base query engine base_query_engine = base_index.as_query_engine(similarity_top_k=2) # sentence window query engine query_engine = sentence_index.as_query_engine( similarity_top_k=2, # the target key defaults to `window` to match the node_parser's default node_postprocessors=[ MetadataReplacementPostProcessor(target_metadata_key="window") ], )
In [ ]:
Copied!
```
import numpy as np

base_pred_responses = get_responses(
    eval_qs[:max_samples], base_query_engine, show_progress=True
)
pred_responses = get_responses(
    eval_qs[:max_samples], query_engine, show_progress=True
)

pred_response_strs = [str(p) for p in pred_responses]
base_pred_response_strs = [str(p) for p in base_pred_responses]

```

import numpy as np base_pred_responses = get_responses( eval_qs[:max_samples], base_query_engine, show_progress=True ) pred_responses = get_responses( eval_qs[:max_samples], query_engine, show_progress=True ) pred_response_strs = [str(p) for p in pred_responses] base_pred_response_strs = [str(p) for p in base_pred_responses]
In [ ]:
Copied!
```
evaluator_dict = {
    "correctness": evaluator_c,
    "faithfulness": evaluator_f,
    "relevancy": evaluator_r,
    "semantic_similarity": evaluator_s,
}
batch_runner = BatchEvalRunner(evaluator_dict, workers=2, show_progress=True)

```

evaluator_dict = { "correctness": evaluator_c, "faithfulness": evaluator_f, "relevancy": evaluator_r, "semantic_similarity": evaluator_s, } batch_runner = BatchEvalRunner(evaluator_dict, workers=2, show_progress=True)
Run evaluations over faithfulness/semantic similarity.
In [ ]:
Copied!
```
eval_results = await batch_runner.aevaluate_responses(
    queries=eval_qs[:max_samples],
    responses=pred_responses[:max_samples],
    reference=ref_response_strs[:max_samples],
)

```

eval_results = await batch_runner.aevaluate_responses( queries=eval_qs[:max_samples], responses=pred_responses[:max_samples], reference=ref_response_strs[:max_samples], )
In [ ]:
Copied!
```
base_eval_results = await batch_runner.aevaluate_responses(
    queries=eval_qs[:max_samples],
    responses=base_pred_responses[:max_samples],
    reference=ref_response_strs[:max_samples],
)

```

base_eval_results = await batch_runner.aevaluate_responses( queries=eval_qs[:max_samples], responses=base_pred_responses[:max_samples], reference=ref_response_strs[:max_samples], )
In [ ]:
Copied!
```
results_df = get_results_df(
    [eval_results, base_eval_results],
    ["Sentence Window Retriever", "Base Retriever"],
    ["correctness", "relevancy", "faithfulness", "semantic_similarity"],
)
display(results_df)

```

results_df = get_results_df( [eval_results, base_eval_results], ["Sentence Window Retriever", "Base Retriever"], ["correctness", "relevancy", "faithfulness", "semantic_similarity"], ) display(results_df)
| names | correctness | relevancy | faithfulness | semantic_similarity  
---|---|---|---|---|---  
0 | Sentence Window Retriever | 4.366667 | 0.933333 | 0.933333 | 0.959583  
1 | Base Retriever | 4.216667 | 0.900000 | 0.933333 | 0.958664
