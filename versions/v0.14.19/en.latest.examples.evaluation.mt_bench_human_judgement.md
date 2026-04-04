![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Benchmarking LLM Evaluators On The MT-Bench Human Judgement `LabelledPairwiseEvaluatorDataset`¶
In this notebook guide, we benchmark Gemini and GPT models as LLM evaluators using a slightly adapted version of the MT-Bench Human Judgements dataset. For this dataset, human evaluators compare two llm model responses to a given query and rank them according to their own preference. In the original version, there can be more than one human evaluator for a given example (query, two model responses). In the adapted version that we consider however, we aggregate these 'repeated' entries and convert the 'winner' column of the original schema to instead represent the proportion of times 'model_a' wins across all of the human evaluators. To adapt this to a llama-dataset, and to better consider ties (albeit with small samples) we set an uncertainty threshold for this proportion in that if it is between [0.4, 0.6] then we consider there to be no winner between the two models. We download this dataset from llama-hub. Finally, the LLMs that we benchmark are listed below:
  1. GPT-3.5 (OpenAI)
  2. GPT-4 (OpenAI)
  3. Gemini-Pro (Google)


In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-llms-cohere
%pip install llama-index-llms-gemini

```

%pip install llama-index-llms-openai %pip install llama-index-llms-cohere %pip install llama-index-llms-gemini
In [ ]:
Copied!
```
!pip install "google-generativeai" -q

```

!pip install "google-generativeai" -q
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
### Load In Dataset¶
Let's load in the llama-dataset from llama-hub.
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import download_llama_dataset

# download dataset
pairwise_evaluator_dataset, _ = download_llama_dataset(
    "MtBenchHumanJudgementDataset", "./mt_bench_data"
)

```

from llama_index.core.llama_dataset import download_llama_dataset # download dataset pairwise_evaluator_dataset, _ = download_llama_dataset( "MtBenchHumanJudgementDataset", "./mt_bench_data" )
In [ ]:
Copied!
```
pairwise_evaluator_dataset.to_pandas()[:5]

```

pairwise_evaluator_dataset.to_pandas()[:5]
Out[ ]:
| query | answer | second_answer | contexts | ground_truth_answer | query_by | answer_by | second_answer_by | ground_truth_answer_by | reference_feedback | reference_score | reference_evaluation_by  
---|---|---|---|---|---|---|---|---|---|---|---|---  
0 | Compose an engaging travel blog post about a r... | I recently had the pleasure of visiting Hawaii... | Aloha! I recently had the pleasure of embarkin... | None | None | human | ai (alpaca-13b) | ai (gpt-3.5-turbo) | None | None | 0.0 | human  
1 | Compose an engaging travel blog post about a r... | I recently had the pleasure of visiting Hawaii... | Aloha and welcome to my travel blog post about... | None | None | human | ai (alpaca-13b) | ai (vicuna-13b-v1.2) | None | None | 0.0 | human  
2 | Compose an engaging travel blog post about a r... | Here is a draft travel blog post about a recen... | I recently had the pleasure of visiting Hawaii... | None | None | human | ai (claude-v1) | ai (alpaca-13b) | None | None | 1.0 | human  
3 | Compose an engaging travel blog post about a r... | Here is a draft travel blog post about a recen... | Here is a travel blog post about a recent trip... | None | None | human | ai (claude-v1) | ai (llama-13b) | None | None | 1.0 | human  
4 | Compose an engaging travel blog post about a r... | Aloha! I recently had the pleasure of embarkin... | I recently had the pleasure of visiting Hawaii... | None | None | human | ai (gpt-3.5-turbo) | ai (alpaca-13b) | None | None | 1.0 | human  
### Define Our Evaluators¶
In [ ]:
Copied!
```
from llama_index.core.evaluation import PairwiseComparisonEvaluator
from llama_index.llms.openai import OpenAI
from llama_index.llms.gemini import Gemini
from llama_index.llms.cohere import Cohere


llm_gpt4 = OpenAI(temperature=0, model="gpt-4")
llm_gpt35 = OpenAI(temperature=0, model="gpt-3.5-turbo")
llm_gemini = Gemini(model="models/gemini-pro", temperature=0)

evaluators = {
    "gpt-4": PairwiseComparisonEvaluator(llm=llm_gpt4),
    "gpt-3.5": PairwiseComparisonEvaluator(llm=llm_gpt35),
    "gemini-pro": PairwiseComparisonEvaluator(llm=llm_gemini),
}

```

from llama_index.core.evaluation import PairwiseComparisonEvaluator from llama_index.llms.openai import OpenAI from llama_index.llms.gemini import Gemini from llama_index.llms.cohere import Cohere llm_gpt4 = OpenAI(temperature=0, model="gpt-4") llm_gpt35 = OpenAI(temperature=0, model="gpt-3.5-turbo") llm_gemini = Gemini(model="models/gemini-pro", temperature=0) evaluators = { "gpt-4": PairwiseComparisonEvaluator(llm=llm_gpt4), "gpt-3.5": PairwiseComparisonEvaluator(llm=llm_gpt35), "gemini-pro": PairwiseComparisonEvaluator(llm=llm_gemini), }
### Benchmark With `EvaluatorBenchmarkerPack` (llama-pack)¶
To compare our four evaluators we will benchmark them against `MTBenchHumanJudgementDataset`, wherein references are provided by human evaluators. The benchmarks will return the following quantites:
  * `number_examples`: The number of examples the dataset consists of.
  * `invalid_predictions`: The number of evaluations that could not yield a final evaluation (e.g., due to inability to parse the evaluation output, or an exception thrown by the LLM evaluator)
  * `inconclusives`: Since this is a pairwise comparison, to mitigate the risk for "position bias" we conduct two evaluations — one with original order of presenting the two model answers, and another with the order in which these answers are presented to the evaluator LLM is flipped. A result is inconclusive if the LLM evaluator in the second ordering flips its vote in relation to the first vote.
  * `ties`: A `PairwiseComparisonEvaluator` can also return a "tie" result. This is the number of examples for which it gave a tie result.
  * `agreement_rate_with_ties`: The rate at which the LLM evaluator agrees with the reference (in this case human) evaluator, when also including ties. The denominator used to compute this metric is given by: `number_examples - invalid_predictions - inconclusives`.
  * `agreement_rate_without_ties`: The rate at which the LLM evaluator agress with the reference (in this case human) evaluator, when excluding and ties. The denominator used to compute this metric is given by: `number_examples - invalid_predictions - inconclusives - ties`.


To compute these metrics, we'll make use of the `EvaluatorBenchmarkerPack`.
In [ ]:
Copied!
```
from llama_index.core.llama_pack import download_llama_pack

EvaluatorBenchmarkerPack = download_llama_pack(
    "EvaluatorBenchmarkerPack", "./pack"
)

```

from llama_index.core.llama_pack import download_llama_pack EvaluatorBenchmarkerPack = download_llama_pack( "EvaluatorBenchmarkerPack", "./pack" )
#### GPT-3.5¶
In [ ]:
Copied!
```
evaluator_benchmarker = EvaluatorBenchmarkerPack(
    evaluator=evaluators["gpt-3.5"],
    eval_dataset=pairwise_evaluator_dataset,
    show_progress=True,
)

```

evaluator_benchmarker = EvaluatorBenchmarkerPack( evaluator=evaluators["gpt-3.5"], eval_dataset=pairwise_evaluator_dataset, show_progress=True, )
In [ ]:
Copied!
```
gpt_3p5_benchmark_df = await evaluator_benchmarker.arun(
    batch_size=100, sleep_time_in_seconds=0
)

```

gpt_3p5_benchmark_df = await evaluator_benchmarker.arun( batch_size=100, sleep_time_in_seconds=0 )
In [ ]:
Copied!
```
gpt_3p5_benchmark_df.index = ["gpt-3.5"]
gpt_3p5_benchmark_df

```

gpt_3p5_benchmark_df.index = ["gpt-3.5"] gpt_3p5_benchmark_df
Out[ ]:
| number_examples | invalid_predictions | inconclusives | ties | agreement_rate_with_ties | agreement_rate_without_ties  
---|---|---|---|---|---|---  
gpt-3.5 | 1204 | 82 | 393 | 56 | 0.736626 | 0.793462  
#### GPT-4¶
In [ ]:
Copied!
```
evaluator_benchmarker = EvaluatorBenchmarkerPack(
    evaluator=evaluators["gpt-4"],
    eval_dataset=pairwise_evaluator_dataset,
    show_progress=True,
)

```

evaluator_benchmarker = EvaluatorBenchmarkerPack( evaluator=evaluators["gpt-4"], eval_dataset=pairwise_evaluator_dataset, show_progress=True, )
In [ ]:
Copied!
```
gpt_4_benchmark_df = await evaluator_benchmarker.arun(
    batch_size=100, sleep_time_in_seconds=0
)

```

gpt_4_benchmark_df = await evaluator_benchmarker.arun( batch_size=100, sleep_time_in_seconds=0 )
In [ ]:
Copied!
```
gpt_4_benchmark_df.index = ["gpt-4"]
gpt_4_benchmark_df

```

gpt_4_benchmark_df.index = ["gpt-4"] gpt_4_benchmark_df
Out[ ]:
| number_examples | invalid_predictions | inconclusives | ties | agreement_rate_with_ties | agreement_rate_without_ties  
---|---|---|---|---|---|---  
gpt-4 | 1204 | 0 | 100 | 103 | 0.701087 | 0.77023  
### Gemini Pro¶
NOTE: The rate limit for Gemini models is still very constraining, which is understandable given that they've just been released at the time of writing this notebook. So, we use a very small `batch_size` and moderately high `sleep_time_in_seconds` to reduce risk of getting rate-limited.
In [ ]:
Copied!
```
evaluator_benchmarker = EvaluatorBenchmarkerPack(
    evaluator=evaluators["gemini-pro"],
    eval_dataset=pairwise_evaluator_dataset,
    show_progress=True,
)

```

evaluator_benchmarker = EvaluatorBenchmarkerPack( evaluator=evaluators["gemini-pro"], eval_dataset=pairwise_evaluator_dataset, show_progress=True, )
In [ ]:
Copied!
```
gemini_pro_benchmark_df = await evaluator_benchmarker.arun(
    batch_size=5, sleep_time_in_seconds=0.5
)

```

gemini_pro_benchmark_df = await evaluator_benchmarker.arun( batch_size=5, sleep_time_in_seconds=0.5 )
In [ ]:
Copied!
```
gemini_pro_benchmark_df.index = ["gemini-pro"]
gemini_pro_benchmark_df

```

gemini_pro_benchmark_df.index = ["gemini-pro"] gemini_pro_benchmark_df
Out[ ]:
| number_examples | invalid_predictions | inconclusives | ties | agreement_rate_with_ties | agreement_rate_without_ties  
---|---|---|---|---|---|---  
gemini-pro | 1204 | 2 | 295 | 60 | 0.742007 | 0.793388  
In [ ]:
Copied!
```
evaluator_benchmarker.prediction_dataset.save_json("gemini_predictions.json")

```

evaluator_benchmarker.prediction_dataset.save_json("gemini_predictions.json")
### Summary¶
For convenience, let's put all the results in a single DataFrame.
In [ ]:
Copied!
```
import pandas as pd

final_benchmark = pd.concat(
    [
        gpt_3p5_benchmark_df,
        gpt_4_benchmark_df,
        gemini_pro_benchmark_df,
    ],
    axis=0,
)
final_benchmark

```

import pandas as pd final_benchmark = pd.concat( [ gpt_3p5_benchmark_df, gpt_4_benchmark_df, gemini_pro_benchmark_df, ], axis=0, ) final_benchmark
Out[ ]:
| number_examples | invalid_predictions | inconclusives | ties | agreement_rate_with_ties | agreement_rate_without_ties  
---|---|---|---|---|---|---  
gpt-3.5 | 1204 | 82 | 393 | 56 | 0.736626 | 0.793462  
gpt-4 | 1204 | 0 | 100 | 103 | 0.701087 | 0.770230  
gemini-pro | 1204 | 2 | 295 | 60 | 0.742007 | 0.793388  
From the results above, we make the following observations:
  * In terms of agreement rates, all three models seem quite close, with perhaps a slight edge given to the Gemini models
  * Gemini Pro and GPT-3.5 seem to be a bit more assertive than GPT-4 resulting in only 50-60 ties to GPT-4's 100 ties.
  * However, perhaps related to the previous point, GPT-4 yields the least amount of inconclusives, meaning that it suffers the least from position bias.
  * Overall, it seems that Gemini Pro is up to snuff with GPT models, and would say that it outperforms GPT-3.5 — looks like Gemini can be legit alternatives to GPT models for evaluation tasks.


