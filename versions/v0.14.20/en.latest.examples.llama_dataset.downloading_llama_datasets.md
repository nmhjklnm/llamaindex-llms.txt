![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Downloading a LlamaDataset from LlamaHub¶
You can browse our available benchmark datasets via llamahub.ai. This notebook guide depicts how you can download the dataset and its source text documents. In particular, the `download_llama_dataset` will download the evaluation dataset (i.e., `LabelledRagDataset`) as well as the `Document`'s of the source text files used to build the evaluation dataset in the first place.
Finally, in this notebook, we also demonstrate the end to end workflow of downloading an evaluation dataset, making predictions on it using your own RAG pipeline (query engine) and then evaluating these predictions.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import download_llama_dataset

# download and install dependencies
rag_dataset, documents = download_llama_dataset(
    "PaulGrahamEssayDataset", "./paul_graham"
)

```

from llama_index.core.llama_dataset import download_llama_dataset # download and install dependencies rag_dataset, documents = download_llama_dataset( "PaulGrahamEssayDataset", "./paul_graham" )
```
github url: https://raw.githubusercontent.com/nerdai/llama-hub/datasets/llama_hub/llama_datasets/library.json
github url: https://media.githubusercontent.com/media/run-llama/llama_datasets/main/llama_datasets/paul_graham_essay/rag_dataset.json
github url: https://media.githubusercontent.com/media/run-llama/llama_datasets/main/llama_datasets/paul_graham_essay/source.txt

```

In [ ]:
Copied!
```
rag_dataset.to_pandas()[:5]

```

rag_dataset.to_pandas()[:5]
Out[ ]:
| query | reference_contexts | reference_answer | reference_answer_by | query_by  
---|---|---|---|---|---  
0 | In the essay, the author mentions his early ex... | [What I Worked On\n\nFebruary 2021\n\nBefore c... | The first computer the author used for program... | ai (gpt-4) | ai (gpt-4)  
1 | The author switched his major from philosophy ... | [What I Worked On\n\nFebruary 2021\n\nBefore c... | The two specific influences that led the autho... | ai (gpt-4) | ai (gpt-4)  
2 | In the essay, the author discusses his initial... | [I couldn't have put this into words when I wa... | The two main influences that initially drew th... | ai (gpt-4) | ai (gpt-4)  
3 | The author mentions his shift of interest towa... | [I couldn't have put this into words when I wa... | The author shifted his interest towards Lisp a... | ai (gpt-4) | ai (gpt-4)  
4 | In the essay, the author mentions his interest... | [So I looked around to see what I could salvag... | The author in the essay is Paul Graham, who wa... | ai (gpt-4) | ai (gpt-4)  
With `documents`, you can build your own RAG pipeline, to then predict and perform evaluations to compare against the benchmarks listed in the `DatasetCard` associated with the datasets llamahub.ai.
### Predictions¶
**NOTE** : The rest of the notebook illustrates how to manually perform predictions and subsequent evaluations for demonstrative purposes. Alternatively you can use the `RagEvaluatorPack` that will take care of predicting and evaluating using a RAG system that you would have provided.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

# a basic RAG pipeline, uses defaults
index = VectorStoreIndex.from_documents(documents=documents)
query_engine = index.as_query_engine()

```

from llama_index.core import VectorStoreIndex # a basic RAG pipeline, uses defaults index = VectorStoreIndex.from_documents(documents=documents) query_engine = index.as_query_engine()
You can now create predictions and perform evaluation manually or download the `PredictAndEvaluatePack` to do this for you in a single line of code.
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
# manually
prediction_dataset = await rag_dataset.amake_predictions_with(
    query_engine=query_engine, show_progress=True
)

```

# manually prediction_dataset = await rag_dataset.amake_predictions_with( query_engine=query_engine, show_progress=True )
```
100%|███████████████████████████████████████████████████████| 44/44 [00:08<00:00,  4.90it/s]

```

In [ ]:
Copied!
```
prediction_dataset.to_pandas()[:5]

```

prediction_dataset.to_pandas()[:5]
Out[ ]:
| response | contexts  
---|---|---  
0 | The author mentions that the first computer he... | [What I Worked On\n\nFebruary 2021\n\nBefore c...  
1 | The author switched his major from philosophy ... | [I couldn't have put this into words when I wa...  
2 | The author mentions two main influences that i... | [I couldn't have put this into words when I wa...  
3 | The author mentions that he shifted his intere... | [So I looked around to see what I could salvag...  
4 | The author mentions his interest in both compu... | [What I Worked On\n\nFebruary 2021\n\nBefore c...  
### Evaluation¶
Now that we have our predictions, we can perform evaluations on two dimensions:
  1. The generated response: how well the predicted response matches the reference answer.
  2. The retrieved contexts: how well the retrieved contexts for the prediction match the reference contexts.


NOTE: For retrieved contexts, we are unable to use standard retrieval metrics such as `hit rate` and `mean reciprocal rank` due to the fact that doing so requires we have the same index that was used to generate the ground truth data. But, it is not necessary for a `LabelledRagDataset` to be even created by an index. As such, we will use `semantic similarity` between the prediction's contexts and the reference contexts as a measure of goodness.
In [ ]:
Copied!
```
import tqdm

```

import tqdm
For evaluating the response, we will use the LLM-As-A-Judge pattern. Specifically, we will use `CorrectnessEvaluator`, `FaithfulnessEvaluator` and `RelevancyEvaluator`.
For evaluating the goodness of the retrieved contexts we will use `SemanticSimilarityEvaluator`.
In [ ]:
Copied!
```
# instantiate the gpt-4 judge
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import (
    CorrectnessEvaluator,
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    SemanticSimilarityEvaluator,
)

judges = {}

judges["correctness"] = CorrectnessEvaluator(
    llm=OpenAI(temperature=0, model="gpt-4"),
)

judges["relevancy"] = RelevancyEvaluator(
    llm=OpenAI(temperature=0, model="gpt-4"),
)

judges["faithfulness"] = FaithfulnessEvaluator(
    llm=OpenAI(temperature=0, model="gpt-4"),
)

judges["semantic_similarity"] = SemanticSimilarityEvaluator()

```

# instantiate the gpt-4 judge from llama_index.llms.openai import OpenAI from llama_index.core.evaluation import ( CorrectnessEvaluator, FaithfulnessEvaluator, RelevancyEvaluator, SemanticSimilarityEvaluator, ) judges = {} judges["correctness"] = CorrectnessEvaluator( llm=OpenAI(temperature=0, model="gpt-4"), ) judges["relevancy"] = RelevancyEvaluator( llm=OpenAI(temperature=0, model="gpt-4"), ) judges["faithfulness"] = FaithfulnessEvaluator( llm=OpenAI(temperature=0, model="gpt-4"), ) judges["semantic_similarity"] = SemanticSimilarityEvaluator()
Loop through the (`labelled_example`, `prediction`) pais and perform the evaluations on each of them individually.
In [ ]:
Copied!
```
evals = {
    "correctness": [],
    "relevancy": [],
    "faithfulness": [],
    "context_similarity": [],
}

for example, prediction in tqdm.tqdm(
    zip(rag_dataset.examples, prediction_dataset.predictions)
):
    correctness_result = judges["correctness"].evaluate(
        query=example.query,
        response=prediction.response,
        reference=example.reference_answer,
    )

    relevancy_result = judges["relevancy"].evaluate(
        query=example.query,
        response=prediction.response,
        contexts=prediction.contexts,
    )

    faithfulness_result = judges["faithfulness"].evaluate(
        query=example.query,
        response=prediction.response,
        contexts=prediction.contexts,
    )

    semantic_similarity_result = judges["semantic_similarity"].evaluate(
        query=example.query,
        response="\n".join(prediction.contexts),
        reference="\n".join(example.reference_contexts),
    )

    evals["correctness"].append(correctness_result)
    evals["relevancy"].append(relevancy_result)
    evals["faithfulness"].append(faithfulness_result)
    evals["context_similarity"].append(semantic_similarity_result)

```

evals = { "correctness": [], "relevancy": [], "faithfulness": [], "context_similarity": [], } for example, prediction in tqdm.tqdm( zip(rag_dataset.examples, prediction_dataset.predictions) ): correctness_result = judges["correctness"].evaluate( query=example.query, response=prediction.response, reference=example.reference_answer, ) relevancy_result = judges["relevancy"].evaluate( query=example.query, response=prediction.response, contexts=prediction.contexts, ) faithfulness_result = judges["faithfulness"].evaluate( query=example.query, response=prediction.response, contexts=prediction.contexts, ) semantic_similarity_result = judges["semantic_similarity"].evaluate( query=example.query, response="\n".join(prediction.contexts), reference="\n".join(example.reference_contexts), ) evals["correctness"].append(correctness_result) evals["relevancy"].append(relevancy_result) evals["faithfulness"].append(faithfulness_result) evals["context_similarity"].append(semantic_similarity_result)
```
44it [07:15,  9.90s/it]

```

In [ ]:
Copied!
```
import json

# saving evaluations
evaluations_objects = {
    "context_similarity": [e.dict() for e in evals["context_similarity"]],
    "correctness": [e.dict() for e in evals["correctness"]],
    "faithfulness": [e.dict() for e in evals["faithfulness"]],
    "relevancy": [e.dict() for e in evals["relevancy"]],
}

with open("evaluations.json", "w") as json_file:
    json.dump(evaluations_objects, json_file)

```

import json # saving evaluations evaluations_objects = { "context_similarity": [e.dict() for e in evals["context_similarity"]], "correctness": [e.dict() for e in evals["correctness"]], "faithfulness": [e.dict() for e in evals["faithfulness"]], "relevancy": [e.dict() for e in evals["relevancy"]], } with open("evaluations.json", "w") as json_file: json.dump(evaluations_objects, json_file)
Now, we can use our notebook utility functions to view these evaluations.
In [ ]:
Copied!
```
import pandas as pd
from llama_index.core.evaluation.notebook_utils import get_eval_results_df

deep_eval_df, mean_correctness_df = get_eval_results_df(
    ["base_rag"] * len(evals["correctness"]),
    evals["correctness"],
    metric="correctness",
)
deep_eval_df, mean_relevancy_df = get_eval_results_df(
    ["base_rag"] * len(evals["relevancy"]),
    evals["relevancy"],
    metric="relevancy",
)
_, mean_faithfulness_df = get_eval_results_df(
    ["base_rag"] * len(evals["faithfulness"]),
    evals["faithfulness"],
    metric="faithfulness",
)
_, mean_context_similarity_df = get_eval_results_df(
    ["base_rag"] * len(evals["context_similarity"]),
    evals["context_similarity"],
    metric="context_similarity",
)

mean_scores_df = pd.concat(
    [
        mean_correctness_df.reset_index(),
        mean_relevancy_df.reset_index(),
        mean_faithfulness_df.reset_index(),
        mean_context_similarity_df.reset_index(),
    ],
    axis=0,
    ignore_index=True,
)
mean_scores_df = mean_scores_df.set_index("index")
mean_scores_df.index = mean_scores_df.index.set_names(["metrics"])

```

import pandas as pd from llama_index.core.evaluation.notebook_utils import get_eval_results_df deep_eval_df, mean_correctness_df = get_eval_results_df( ["base_rag"] * len(evals["correctness"]), evals["correctness"], metric="correctness", ) deep_eval_df, mean_relevancy_df = get_eval_results_df( ["base_rag"] * len(evals["relevancy"]), evals["relevancy"], metric="relevancy", ) _, mean_faithfulness_df = get_eval_results_df( ["base_rag"] * len(evals["faithfulness"]), evals["faithfulness"], metric="faithfulness", ) _, mean_context_similarity_df = get_eval_results_df( ["base_rag"] * len(evals["context_similarity"]), evals["context_similarity"], metric="context_similarity", ) mean_scores_df = pd.concat( [ mean_correctness_df.reset_index(), mean_relevancy_df.reset_index(), mean_faithfulness_df.reset_index(), mean_context_similarity_df.reset_index(), ], axis=0, ignore_index=True, ) mean_scores_df = mean_scores_df.set_index("index") mean_scores_df.index = mean_scores_df.index.set_names(["metrics"])
In [ ]:
Copied!
```
mean_scores_df

```

mean_scores_df
Out[ ]:
rag | base_rag  
---|---  
metrics |   
mean_correctness_score | 4.238636  
mean_relevancy_score | 0.977273  
mean_faithfulness_score | 0.977273  
mean_context_similarity_score | 0.933568  
On this toy example, we see that the basic RAG pipeline performs quite well against the evaluation benchmark (`rag_dataset`)! For completeness, to perform the above steps instead by using the `RagEvaluatorPack`, use the code provided below:
In [ ]:
Copied!
```
from llama_index.core.llama_pack import download_llama_pack

RagEvaluatorPack = download_llama_pack("RagEvaluatorPack", "./pack")
rag_evaluator = RagEvaluatorPack(
    query_engine=query_engine, rag_dataset=rag_dataset, show_progress=True
)

############################################################################
# NOTE: If have a lower tier subscription for OpenAI API like Usage Tier 1 #
# then you'll need to use different batch_size and sleep_time_in_seconds.  #
# For Usage Tier 1, settings that seemed to work well were batch_size=5,   #
# and sleep_time_in_seconds=15 (as of December 2023.)                      #
############################################################################

benchmark_df = await rag_evaluator_pack.arun(
    batch_size=20,  # batches the number of openai api calls to make
    sleep_time_in_seconds=1,  # seconds to sleep before making an api call
)

```

from llama_index.core.llama_pack import download_llama_pack RagEvaluatorPack = download_llama_pack("RagEvaluatorPack", "./pack") rag_evaluator = RagEvaluatorPack( query_engine=query_engine, rag_dataset=rag_dataset, show_progress=True ) ############################################################################ # NOTE: If have a lower tier subscription for OpenAI API like Usage Tier 1 # # then you'll need to use different batch_size and sleep_time_in_seconds. # # For Usage Tier 1, settings that seemed to work well were batch_size=5, # # and sleep_time_in_seconds=15 (as of December 2023.) # ############################################################################ benchmark_df = await rag_evaluator_pack.arun( batch_size=20, # batches the number of openai api calls to make sleep_time_in_seconds=1, # seconds to sleep before making an api call )
