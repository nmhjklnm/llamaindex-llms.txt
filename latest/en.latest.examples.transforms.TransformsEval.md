# Transforms Evaluation¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
Here we try out different transformations and evaluate their quality.
  * First we try out different parsers (PDF, JSON)
  * Then we try out different extractors


In [ ]:
Copied!
```
%pip install llama-index-readers-file
%pip install llama-index-llms-openai
%pip install llama-index-embeddings-openai

```

%pip install llama-index-readers-file %pip install llama-index-llms-openai %pip install llama-index-embeddings-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
## Load Data + Setup¶
Load in the Tesla data.
In [ ]:
Copied!
```
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

```

import pandas as pd pd.set_option("display.max_rows", None) pd.set_option("display.max_columns", None) pd.set_option("display.width", None) pd.set_option("display.max_colwidth", None)
In [ ]:
Copied!
```
!wget "https://www.dropbox.com/scl/fi/mlaymdy1ni1ovyeykhhuk/tesla_2021_10k.htm?rlkey=qf9k4zn0ejrbm716j0gg7r802&dl=1" -O tesla_2021_10k.htm
!wget "https://www.dropbox.com/scl/fi/rkw0u959yb4w8vlzz76sa/tesla_2020_10k.htm?rlkey=tfkdshswpoupav5tqigwz1mp7&dl=1" -O tesla_2020_10k.htm

```

!wget "https://www.dropbox.com/scl/fi/mlaymdy1ni1ovyeykhhuk/tesla_2021_10k.htm?rlkey=qf9k4zn0ejrbm716j0gg7r802&dl=1" -O tesla_2021_10k.htm !wget "https://www.dropbox.com/scl/fi/rkw0u959yb4w8vlzz76sa/tesla_2020_10k.htm?rlkey=tfkdshswpoupav5tqigwz1mp7&dl=1" -O tesla_2020_10k.htm
In [ ]:
Copied!
```
from llama_index.readers.file import FlatReader
from pathlib import Path

reader = FlatReader()
docs = reader.load_data(Path("./tesla_2020_10k.htm"))

```

from llama_index.readers.file import FlatReader from pathlib import Path reader = FlatReader() docs = reader.load_data(Path("./tesla_2020_10k.htm"))
## Generate Eval Dataset / Define Eval Functions¶
Generate a "golden" eval dataset from the Tesla documents.
Also define eval functions for running a pipeline.
Here we define an ingestion pipeline purely for generating a synthetic eval dataset.
In [ ]:
Copied!
```
from llama_index.core.evaluation import DatasetGenerator, QueryResponseDataset
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.file import FlatReader
from llama_index.core.node_parser import HTMLNodeParser, SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline
from pathlib import Path

import nest_asyncio

nest_asyncio.apply()

```

from llama_index.core.evaluation import DatasetGenerator, QueryResponseDataset from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.readers.file import FlatReader from llama_index.core.node_parser import HTMLNodeParser, SentenceSplitter from llama_index.core.ingestion import IngestionPipeline from pathlib import Path import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
reader = FlatReader()
docs = reader.load_data(Path("./tesla_2020_10k.htm"))

pipeline = IngestionPipeline(
    documents=docs,
    transformations=[
        HTMLNodeParser.from_defaults(),
        SentenceSplitter(chunk_size=1024, chunk_overlap=200),
        OpenAIEmbedding(),
    ],
)
eval_nodes = pipeline.run(documents=docs)

```

reader = FlatReader() docs = reader.load_data(Path("./tesla_2020_10k.htm")) pipeline = IngestionPipeline( documents=docs, transformations=[ HTMLNodeParser.from_defaults(), SentenceSplitter(chunk_size=1024, chunk_overlap=200), OpenAIEmbedding(), ], ) eval_nodes = pipeline.run(documents=docs)
In [ ]:
Copied!
```
# NOTE: run this if the dataset isn't already saved
# Note: we only generate from the first 20 nodes, since the rest are references
# eval_llm = OpenAI(model="gpt-4-1106-preview")
eval_llm = OpenAI(model="gpt-3.5-turbo")

dataset_generator = DatasetGenerator(
    eval_nodes[:100],
    llm=eval_llm,
    show_progress=True,
    num_questions_per_chunk=3,
)

```

# NOTE: run this if the dataset isn't already saved # Note: we only generate from the first 20 nodes, since the rest are references # eval_llm = OpenAI(model="gpt-4-1106-preview") eval_llm = OpenAI(model="gpt-3.5-turbo") dataset_generator = DatasetGenerator( eval_nodes[:100], llm=eval_llm, show_progress=True, num_questions_per_chunk=3, )
In [ ]:
Copied!
```
eval_dataset = await dataset_generator.agenerate_dataset_from_nodes(num=100)

```

eval_dataset = await dataset_generator.agenerate_dataset_from_nodes(num=100)
In [ ]:
Copied!
```
len(eval_dataset.qr_pairs)

```

len(eval_dataset.qr_pairs)
Out[ ]:


In [ ]:
Copied!
```
eval_dataset.save_json("data/tesla10k_eval_dataset.json")

```

eval_dataset.save_json("data/tesla10k_eval_dataset.json")
In [ ]:
Copied!
```
# optional
eval_dataset = QueryResponseDataset.from_json(
    "data/tesla10k_eval_dataset.json"
)

```

# optional eval_dataset = QueryResponseDataset.from_json( "data/tesla10k_eval_dataset.json" )
In [ ]:
Copied!
```
eval_qs = eval_dataset.questions
qr_pairs = eval_dataset.qr_pairs
ref_response_strs = [r for (_, r) in qr_pairs]

```

eval_qs = eval_dataset.questions qr_pairs = eval_dataset.qr_pairs ref_response_strs = [r for (_, r) in qr_pairs]
### Run Evals¶
In [ ]:
Copied!
```
from llama_index.core.evaluation import (
    CorrectnessEvaluator,
    SemanticSimilarityEvaluator,
)
from llama_index.core.evaluation.eval_utils import (
    get_responses,
    get_results_df,
)
from llama_index.core.evaluation import BatchEvalRunner

```

from llama_index.core.evaluation import ( CorrectnessEvaluator, SemanticSimilarityEvaluator, ) from llama_index.core.evaluation.eval_utils import ( get_responses, get_results_df, ) from llama_index.core.evaluation import BatchEvalRunner
In [ ]:
Copied!
```
evaluator_c = CorrectnessEvaluator(llm=eval_llm)
evaluator_s = SemanticSimilarityEvaluator(llm=eval_llm)
evaluator_dict = {
    "correctness": evaluator_c,
    "semantic_similarity": evaluator_s,
}
batch_eval_runner = BatchEvalRunner(
    evaluator_dict, workers=2, show_progress=True
)

```

evaluator_c = CorrectnessEvaluator(llm=eval_llm) evaluator_s = SemanticSimilarityEvaluator(llm=eval_llm) evaluator_dict = { "correctness": evaluator_c, "semantic_similarity": evaluator_s, } batch_eval_runner = BatchEvalRunner( evaluator_dict, workers=2, show_progress=True )
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex


async def run_evals(
    pipeline, batch_eval_runner, docs, eval_qs, eval_responses_ref
):
    # get query engine
    nodes = pipeline.run(documents=docs)
    # define vector index (top-k = 2)
    vector_index = VectorStoreIndex(nodes)
    query_engine = vector_index.as_query_engine()

    pred_responses = get_responses(eval_qs, query_engine, show_progress=True)
    eval_results = await batch_eval_runner.aevaluate_responses(
        eval_qs, responses=pred_responses, reference=eval_responses_ref
    )
    return eval_results

```

from llama_index.core import VectorStoreIndex async def run_evals( pipeline, batch_eval_runner, docs, eval_qs, eval_responses_ref ): # get query engine nodes = pipeline.run(documents=docs) # define vector index (top-k = 2) vector_index = VectorStoreIndex(nodes) query_engine = vector_index.as_query_engine() pred_responses = get_responses(eval_qs, query_engine, show_progress=True) eval_results = await batch_eval_runner.aevaluate_responses( eval_qs, responses=pred_responses, reference=eval_responses_ref ) return eval_results
## 1. Try out Different Sentence Splitter (Overlaps)¶
The chunking strategy matters! Here we try the sentence splitter with different overlap values, to see how it impacts performance.
The `IngestionPipeline` lets us concisely define an e2e transformation pipeline for RAG, and we define variants where each corresponds to a different sentence splitter configuration (while keeping other steps fixed).
In [ ]:
Copied!
```
from llama_index.core.node_parser import HTMLNodeParser, SentenceSplitter

# For clarity in the demo, make small splits without overlap
sent_parser_o0 = SentenceSplitter(chunk_size=1024, chunk_overlap=0)
sent_parser_o200 = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
sent_parser_o500 = SentenceSplitter(chunk_size=1024, chunk_overlap=600)

html_parser = HTMLNodeParser.from_defaults()

parser_dict = {
    "sent_parser_o0": sent_parser_o0,
    "sent_parser_o200": sent_parser_o200,
    "sent_parser_o500": sent_parser_o500,
}

```

from llama_index.core.node_parser import HTMLNodeParser, SentenceSplitter # For clarity in the demo, make small splits without overlap sent_parser_o0 = SentenceSplitter(chunk_size=1024, chunk_overlap=0) sent_parser_o200 = SentenceSplitter(chunk_size=1024, chunk_overlap=200) sent_parser_o500 = SentenceSplitter(chunk_size=1024, chunk_overlap=600) html_parser = HTMLNodeParser.from_defaults() parser_dict = { "sent_parser_o0": sent_parser_o0, "sent_parser_o200": sent_parser_o200, "sent_parser_o500": sent_parser_o500, }
Define a separate pipeline for each parser.
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.ingestion import IngestionPipeline

# generate a pipeline for each parser
# keep embedding model fixed
pipeline_dict = {}
for k, parser in parser_dict.items():
    pipeline = IngestionPipeline(
        documents=docs,
        transformations=[
            html_parser,
            parser,
            OpenAIEmbedding(),
        ],
    )
    pipeline_dict[k] = pipeline

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core.ingestion import IngestionPipeline # generate a pipeline for each parser # keep embedding model fixed pipeline_dict = {} for k, parser in parser_dict.items(): pipeline = IngestionPipeline( documents=docs, transformations=[ html_parser, parser, OpenAIEmbedding(), ], ) pipeline_dict[k] = pipeline
In [ ]:
Copied!
```
eval_results_dict = {}
for k, pipeline in pipeline_dict.items():
    eval_results = await run_evals(
        pipeline, batch_eval_runner, docs, eval_qs, ref_response_strs
    )
    eval_results_dict[k] = eval_results

```

eval_results_dict = {} for k, pipeline in pipeline_dict.items(): eval_results = await run_evals( pipeline, batch_eval_runner, docs, eval_qs, ref_response_strs ) eval_results_dict[k] = eval_results
In [ ]:
Copied!
```
# [tmp] save eval results
import pickle

pickle.dump(eval_results_dict, open("eval_results_1.pkl", "wb"))

```

# [tmp] save eval results import pickle pickle.dump(eval_results_dict, open("eval_results_1.pkl", "wb"))
In [ ]:
Copied!
```
eval_results_list = list(eval_results_dict.items())

results_df = get_results_df(
    [v for _, v in eval_results_list],
    [k for k, _ in eval_results_list],
    ["correctness", "semantic_similarity"],
)
display(results_df)

```

eval_results_list = list(eval_results_dict.items()) results_df = get_results_df( [v for _, v in eval_results_list], [k for k, _ in eval_results_list], ["correctness", "semantic_similarity"], ) display(results_df)
| names | correctness | semantic_similarity  
---|---|---|---  
0 | sent_parser_o0 | 4.310 | 0.972838  
1 | sent_parser_o200 | 4.335 | 0.978842  
2 | sent_parser_o500 | 4.270 | 0.971759  
In [ ]:
Copied!
```
# [optional] persist cache in folders so we can reuse
for k, pipeline in pipeline_dict.items():
    pipeline.cache.persist(f"./cache/{k}.json")

```

# [optional] persist cache in folders so we can reuse for k, pipeline in pipeline_dict.items(): pipeline.cache.persist(f"./cache/{k}.json")
## 2. Try out Different Extractors¶
Similarly, metadata extraction can be quite important for good performance. We experiment with this as a last step in an overall ingestion pipeline, and define different ingestion pipeline variants corresponding to different extractors.
We define the set of document extractors we want to try out.
We keep the parsers fixed (HTML parser, sentence splitter w/ overlap 200) and the embedding model fixed (OpenAIEmbedding).
In [ ]:
Copied!
```
from llama_index.core.extractors import (
    TitleExtractor,
    QuestionsAnsweredExtractor,
    SummaryExtractor,
)
from llama_index.core.node_parser import HTMLNodeParser, SentenceSplitter

# generate a pipeline for each extractor
# keep embedding model fixed
extractor_dict = {
    # "title": TitleExtractor(),
    "summary": SummaryExtractor(in_place=False),
    "qa": QuestionsAnsweredExtractor(in_place=False),
    "default": None,
}

# these are the parsers that will run beforehand
html_parser = HTMLNodeParser.from_defaults()
sent_parser_o200 = SentenceSplitter(chunk_size=1024, chunk_overlap=200)

```

from llama_index.core.extractors import ( TitleExtractor, QuestionsAnsweredExtractor, SummaryExtractor, ) from llama_index.core.node_parser import HTMLNodeParser, SentenceSplitter # generate a pipeline for each extractor # keep embedding model fixed extractor_dict = { # "title": TitleExtractor(), "summary": SummaryExtractor(in_place=False), "qa": QuestionsAnsweredExtractor(in_place=False), "default": None, } # these are the parsers that will run beforehand html_parser = HTMLNodeParser.from_defaults() sent_parser_o200 = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
In [ ]:
Copied!
```
pipeline_dict = {}
html_parser = HTMLNodeParser.from_defaults()
for k, extractor in extractor_dict.items():
    if k == "default":
        transformations = [
            html_parser,
            sent_parser_o200,
            OpenAIEmbedding(),
        ]
    else:
        transformations = [
            html_parser,
            sent_parser_o200,
            extractor,
            OpenAIEmbedding(),
        ]

    pipeline = IngestionPipeline(transformations=transformations)
    pipeline_dict[k] = pipeline

```

pipeline_dict = {} html_parser = HTMLNodeParser.from_defaults() for k, extractor in extractor_dict.items(): if k == "default": transformations = [ html_parser, sent_parser_o200, OpenAIEmbedding(), ] else: transformations = [ html_parser, sent_parser_o200, extractor, OpenAIEmbedding(), ] pipeline = IngestionPipeline(transformations=transformations) pipeline_dict[k] = pipeline
In [ ]:
Copied!
```
eval_results_dict_2 = {}
for k, pipeline in pipeline_dict.items():
    eval_results = await run_evals(
        pipeline, batch_eval_runner, docs, eval_qs, ref_response_strs
    )
    eval_results_dict_2[k] = eval_results

```

eval_results_dict_2 = {} for k, pipeline in pipeline_dict.items(): eval_results = await run_evals( pipeline, batch_eval_runner, docs, eval_qs, ref_response_strs ) eval_results_dict_2[k] = eval_results
In [ ]:
Copied!
```
eval_results_list_2 = list(eval_results_dict_2.items())

results_df = get_results_df(
    [v for _, v in eval_results_list_2],
    [k for k, _ in eval_results_list_2],
    ["correctness", "semantic_similarity"],
)
display(results_df)

```

eval_results_list_2 = list(eval_results_dict_2.items()) results_df = get_results_df( [v for _, v in eval_results_list_2], [k for k, _ in eval_results_list_2], ["correctness", "semantic_similarity"], ) display(results_df)
| names | correctness | semantic_similarity  
---|---|---|---  
0 | summary | 4.315 | 0.976951  
1 | qa | 4.355 | 0.978807  
2 | default | 4.305 | 0.978451  
In [ ]:
Copied!
```
# [optional] persist cache in folders so we can reuse
for k, pipeline in pipeline_dict.items():
    pipeline.cache.persist(f"./cache/{k}.json")

```

# [optional] persist cache in folders so we can reuse for k, pipeline in pipeline_dict.items(): pipeline.cache.persist(f"./cache/{k}.json")
## 3. Try out Multiple Extractors (with Caching)¶
TODO
Each extraction step can be expensive due to LLM calls. What if we want to experiment with multiple extractors?
We take advantage of **caching** so that all previous extractor calls are cached, and we only experiment with the final extractor call. The `IngestionPipeline` gives us a clean abstraction to play around with the final extractor.
Try out different extractors
