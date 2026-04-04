![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Benchmarking LLM Evaluators On A Mini MT-Bench (Single Grading) `LabelledEvaluatorDataset`¶
In this notebook, we'll conduct an evaluation of three different evaluators that will be judging another LLM's response for response against a user query. More specifically, we will run benchmarks using a mini version of the MT-Bench single-grading dataset. In this version, we only consider the answers on the 160 questions (i.e., 80 x 2, since there are 80 two-turn dialogues) provided by llama2-70b. The reference answers used for this benchmark are provided by GPT-4. And so, our benchmarks on these three evaluators will assess closeness to GPT-4 (actually, self-consistency for the case of GPT-4).
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
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
!pip install "google-generativeai" -q

```

!pip install "google-generativeai" -q
### Load in Evaluator Dataset¶
Let's load in the llama-dataset from llama-hub.
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import download_llama_dataset

# download dataset
evaluator_dataset, _ = download_llama_dataset(
    "MiniMtBenchSingleGradingDataset", "./mini_mt_bench_data"
)

```

from llama_index.core.llama_dataset import download_llama_dataset # download dataset evaluator_dataset, _ = download_llama_dataset( "MiniMtBenchSingleGradingDataset", "./mini_mt_bench_data" )
In [ ]:
Copied!
```
evaluator_dataset.to_pandas()[:5]

```

evaluator_dataset.to_pandas()[:5]
Out[ ]:
| query | answer | contexts | ground_truth_answer | query_by | answer_by | ground_truth_answer_by | reference_feedback | reference_score | reference_evaluation_by  
---|---|---|---|---|---|---|---|---|---|---  
0 | Compose an engaging travel blog post about a r... | Title: Discovering the Aloha Spirit: A Recent ... | None | None | None | ai (llama2-70b) | None | The generated answer is highly relevant to the... | 5.0 | ai (gpt-4)  
1 | Rewrite your previous response. Start every se... | Absolutely, here's the revised response:\n\nAl... | None | None | None | ai (llama2-70b) | None | The generated answer is highly relevant and co... | 5.0 | ai (gpt-4)  
2 | Draft a professional email seeking your superv... | Subject: Seeking Feedback on Quarterly Financi... | None | None | None | ai (llama2-70b) | None | The generated answer is highly relevant to the... | 5.0 | ai (gpt-4)  
3 | Take a moment to evaluate and critique your ow... | My response was:\n\n"Subject: Seeking Feedback... | None | None | None | ai (llama2-70b) | None | The generated answer is highly relevant to the... | 5.0 | ai (gpt-4)  
4 | Imagine you are writing a blog post comparing ... | Sure, here's an outline for a blog post compar... | None | None | None | ai (llama2-70b) | None | The generated answer is highly relevant to the... | 5.0 | ai (gpt-4)  
### Define Our Evaluators¶
In [ ]:
Copied!
```
from llama_index.core.evaluation import CorrectnessEvaluator
from llama_index.llms.openai import OpenAI
from llama_index.llms.gemini import Gemini
from llama_index.llms.cohere import Cohere

llm_gpt4 = OpenAI(temperature=0, model="gpt-4")
llm_gpt35 = OpenAI(temperature=0, model="gpt-3.5-turbo")
llm_gemini = Gemini(model="models/gemini-pro", temperature=0)


evaluators = {
    "gpt-4": CorrectnessEvaluator(llm=llm_gpt4),
    "gpt-3.5": CorrectnessEvaluator(llm=llm_gpt35),
    "gemini-pro": CorrectnessEvaluator(llm=llm_gemini),
}

```

from llama_index.core.evaluation import CorrectnessEvaluator from llama_index.llms.openai import OpenAI from llama_index.llms.gemini import Gemini from llama_index.llms.cohere import Cohere llm_gpt4 = OpenAI(temperature=0, model="gpt-4") llm_gpt35 = OpenAI(temperature=0, model="gpt-3.5-turbo") llm_gemini = Gemini(model="models/gemini-pro", temperature=0) evaluators = { "gpt-4": CorrectnessEvaluator(llm=llm_gpt4), "gpt-3.5": CorrectnessEvaluator(llm=llm_gpt35), "gemini-pro": CorrectnessEvaluator(llm=llm_gemini), }
### Benchmark With `EvaluatorBenchmarkerPack` (llama-pack)¶
When using the `EvaluatorBenchmarkerPack` with a `LabelledEvaluatorDataset`, the returned benchmarks will contain values for the following quantites:
  * `number_examples`: The number of examples the dataset consists of.
  * `invalid_predictions`: The number of evaluations that could not yield a final evaluation (e.g., due to inability to parse the evaluation output, or an exception thrown by the LLM evaluator)
  * `correlation`: The correlation between the scores of the provided evaluator and those of the reference evaluator (in this case gpt-4).
  * `mae`: The mean absolute error between the scores of the provided evaluator and those of the reference evaluator.
  * `hamming`: The hamming distance between the scores of the provided evaluator and those of the reference evaluator.


NOTE: `correlation`, `mae`, and `hamming` are all computed without invalid predictions. So, essentially these metrics are conditional ones, conditioned on the prediction being valid.
In [ ]:
Copied!
```
from llama_index.core.llama_pack import download_llama_pack

EvaluatorBenchmarkerPack = download_llama_pack(
    "EvaluatorBenchmarkerPack", "./pack"
)

```

from llama_index.core.llama_pack import download_llama_pack EvaluatorBenchmarkerPack = download_llama_pack( "EvaluatorBenchmarkerPack", "./pack" )
#### GPT 3.5¶
In [ ]:
Copied!
```
evaluator_benchmarker = EvaluatorBenchmarkerPack(
    evaluator=evaluators["gpt-3.5"],
    eval_dataset=evaluator_dataset,
    show_progress=True,
)

```

evaluator_benchmarker = EvaluatorBenchmarkerPack( evaluator=evaluators["gpt-3.5"], eval_dataset=evaluator_dataset, show_progress=True, )
In [ ]:
Copied!
```
gpt_3p5_benchmark_df = await evaluator_benchmarker.arun(
    batch_size=100, sleep_time_in_seconds=0
)

```

gpt_3p5_benchmark_df = await evaluator_benchmarker.arun( batch_size=100, sleep_time_in_seconds=0 )
```
/Users/nerdai/Projects/llama_index/docs/examples/evaluation/pack/base.py:142: UserWarning: You've set a large batch_size (>10). If using OpenAI GPT-4 as  `judge_llm` (which is the default judge_llm), you may experience a RateLimitError. Previous successful eval  responses are cached per batch. So hitting a RateLimitError would mean you'd lose all of the current batches successful  GPT-4 calls.
  warnings.warn(
Batch processing of predictions: 100%|████████████████████| 100/100 [00:05<00:00, 18.88it/s]
Batch processing of predictions: 100%|██████████████████████| 60/60 [00:04<00:00, 12.26it/s]

```

In [ ]:
Copied!
```
gpt_3p5_benchmark_df.index = ["gpt-3.5"]
gpt_3p5_benchmark_df

```

gpt_3p5_benchmark_df.index = ["gpt-3.5"] gpt_3p5_benchmark_df
Out[ ]:
| number_examples | invalid_predictions | correlation | mae | hamming  
---|---|---|---|---|---  
gpt-3.5 | 160 | 0 | 0.317047 | 1.11875 | 27  
#### GPT-4¶
In [ ]:
Copied!
```
evaluator_benchmarker = EvaluatorBenchmarkerPack(
    evaluator=evaluators["gpt-4"],
    eval_dataset=evaluator_dataset,
    show_progress=True,
)

```

evaluator_benchmarker = EvaluatorBenchmarkerPack( evaluator=evaluators["gpt-4"], eval_dataset=evaluator_dataset, show_progress=True, )
In [ ]:
Copied!
```
gpt_4_benchmark_df = await evaluator_benchmarker.arun(
    batch_size=100, sleep_time_in_seconds=0
)

```

gpt_4_benchmark_df = await evaluator_benchmarker.arun( batch_size=100, sleep_time_in_seconds=0 )
```
/Users/nerdai/Projects/llama_index/docs/examples/evaluation/pack/base.py:142: UserWarning: You've set a large batch_size (>10). If using OpenAI GPT-4 as  `judge_llm` (which is the default judge_llm), you may experience a RateLimitError. Previous successful eval  responses are cached per batch. So hitting a RateLimitError would mean you'd lose all of the current batches successful  GPT-4 calls.
  warnings.warn(
Batch processing of predictions: 100%|████████████████████| 100/100 [00:13<00:00,  7.26it/s]
Batch processing of predictions: 100%|██████████████████████| 60/60 [00:10<00:00,  5.92it/s]

```

In [ ]:
Copied!
```
gpt_4_benchmark_df.index = ["gpt-4"]
gpt_4_benchmark_df

```

gpt_4_benchmark_df.index = ["gpt-4"] gpt_4_benchmark_df
Out[ ]:
| number_examples | invalid_predictions | correlation | mae | hamming  
---|---|---|---|---|---  
gpt-4 | 160 | 0 | 0.966126 | 0.09375 | 143  
#### Gemini Pro¶
In [ ]:
Copied!
```
evaluator_benchmarker = EvaluatorBenchmarkerPack(
    evaluator=evaluators["gemini-pro"],
    eval_dataset=evaluator_dataset,
    show_progress=True,
)

```

evaluator_benchmarker = EvaluatorBenchmarkerPack( evaluator=evaluators["gemini-pro"], eval_dataset=evaluator_dataset, show_progress=True, )
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
| number_examples | invalid_predictions | correlation | mae | hamming  
---|---|---|---|---|---  
gemini-pro | 160 | 1 | 0.295121 | 1.220126 | 12  
In [ ]:
Copied!
```
evaluator_benchmarker.prediction_dataset.save_json(
    "mt_sg_gemini_predictions.json"
)

```

evaluator_benchmarker.prediction_dataset.save_json( "mt_sg_gemini_predictions.json" )
### In Summary¶
Putting all baselines together.
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
| number_examples | invalid_predictions | correlation | mae | hamming  
---|---|---|---|---|---  
gpt-3.5 | 160 | 0 | 0.317047 | 1.118750 | 27  
gpt-4 | 160 | 0 | 0.966126 | 0.093750 | 143  
gemini-pro | 160 | 1 | 0.295121 | 1.220126 | 12  
From the results above, we make the following observations:
  * GPT-3.5 and Gemini-Pro seem to have similar results, with perhaps the slightes edge to GPT-3.5 in terms of closeness to GPT-4.
  * Though, both don't seem to be too close to GPT-4.
  * GPT-4 seems to be pretty consistent with itself in this benchmark.


