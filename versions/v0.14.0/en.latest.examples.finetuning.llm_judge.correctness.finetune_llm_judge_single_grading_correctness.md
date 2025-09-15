# Knowledge Distillation For Fine-Tuning A GPT-3.5 Judge (Correctness)¶
This notebook has to do with fine-tuning an LLM Judge that evaluates the responses of another LLM to a user query. More specifically, we demonstrate how to use the `llama_index` library to distill knowledge from a GPT-4 Judge to a GPT-3.5 Judge. To do so, we will take the following steps:
  1. Generate datasets: `train` and `test`
  2. Perform knowledge distillation (using `train`)
  3. Evaluate the distilled model on `test`


More specifically, we will use `CorrectnessEvaluator` as our LLM Judge.
In [ ]:
Copied!
```
%pip install llama-index-readers-wikipedia
%pip install llama-index-finetuning
%pip install llama-index-llms-openai
%pip install llama-index-finetuning-callbacks
%pip install llama-index-llms-huggingface-api

```

%pip install llama-index-readers-wikipedia %pip install llama-index-finetuning %pip install llama-index-llms-openai %pip install llama-index-finetuning-callbacks %pip install llama-index-llms-huggingface-api
In [ ]:
Copied!
```
# NOTE: this notebook makes several API calls to generate text with OpenAI GPT
# models as well as models hosted on HuggingFace. If you prefer not to wait for
# these generations, then the data for this notebook can be obtained with the
# `wget` command provided below.

# !wget "https://www.dropbox.com/scl/fo/3kkm8v6qvhxnu449xwp3d/h?rlkey=fxom1yixru1nags9mmao1hkg2&dl=1" -O correctness.zip

```

# NOTE: this notebook makes several API calls to generate text with OpenAI GPT # models as well as models hosted on HuggingFace. If you prefer not to wait for # these generations, then the data for this notebook can be obtained with the # `wget` command provided below. # !wget "https://www.dropbox.com/scl/fo/3kkm8v6qvhxnu449xwp3d/h?rlkey=fxom1yixru1nags9mmao1hkg2&dl=1" -O correctness.zip
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
import os

# we will be using models on HuggingFace as our LLM answer generators
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

# we will use GPT-4 and GPT-3.5 + OpenAI Fine-Tuning
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

```

import os # we will be using models on HuggingFace as our LLM answer generators HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN") # we will use GPT-4 and GPT-3.5 + OpenAI Fine-Tuning OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
## Step 1 Generate datasets: `train_dataset` and `test_dataset`¶
For our dataset on which we will generate questions and prompt various LLMs to answer, we're going to use the `WikipediaReader` to read "History of " for several cities.
In [ ]:
Copied!
```
!pip install wikipedia -q

```

!pip install wikipedia -q
```
[notice] A new release of pip is available: 23.2.1 -> 23.3.1
[notice] To update, run: pip install --upgrade pip

```

In [ ]:
Copied!
```
# wikipedia pages
from llama_index.readers.wikipedia import WikipediaReader

cities = [
    "San Francisco",
    "Toronto",
    "New York",
    "Vancouver",
    "Montreal",
    "Tokyo",
    "Singapore",
    "Paris",
]

documents = WikipediaReader().load_data(
    pages=[f"History of {x}" for x in cities]
)

```

# wikipedia pages from llama_index.readers.wikipedia import WikipediaReader cities = [ "San Francisco", "Toronto", "New York", "Vancouver", "Montreal", "Tokyo", "Singapore", "Paris", ] documents = WikipediaReader().load_data( pages=[f"History of {x}" for x in cities] )
### Use a `DatasetGenerator` to build `train_dataset` and `test_dataset`¶
Now that we have our train and test set of `Document`'s, the next step is to generate the questions. For this we will use the `DatasetGenerator`, which uses an LLM to generate questions from given set of documents.
#### Generate Questions¶
In [ ]:
Copied!
```
QUESTION_GEN_PROMPT = (
    "You are a Teacher/ Professor. Your task is to setup "
    "a quiz/examination. Using the provided context, formulate "
    "a single question that captures an important fact from the "
    "context. Restrict the question to the context information provided."
)

```

QUESTION_GEN_PROMPT = ( "You are a Teacher/ Professor. Your task is to setup " "a quiz/examination. Using the provided context, formulate " "a single question that captures an important fact from the " "context. Restrict the question to the context information provided." )
In [ ]:
Copied!
```
# generate questions against chunks
from llama_index.core.evaluation import DatasetGenerator
from llama_index.llms.openai import OpenAI

# set context for llm provider
gpt_35_llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)

# instantiate a DatasetGenerator
dataset_generator = DatasetGenerator.from_documents(
    documents,
    question_gen_query=QUESTION_GEN_PROMPT,
    llm=gpt_35_llm,
    num_questions_per_chunk=25,
)

```

# generate questions against chunks from llama_index.core.evaluation import DatasetGenerator from llama_index.llms.openai import OpenAI # set context for llm provider gpt_35_llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3) # instantiate a DatasetGenerator dataset_generator = DatasetGenerator.from_documents( documents, question_gen_query=QUESTION_GEN_PROMPT, llm=gpt_35_llm, num_questions_per_chunk=25, )
In [ ]:
Copied!
```
qrd = dataset_generator.generate_dataset_from_nodes(num=350)

```

qrd = dataset_generator.generate_dataset_from_nodes(num=350)
In [ ]:
Copied!
```
# If you want to save it for future use
# qrd.save_json("qrd.json")

```

# If you want to save it for future use # qrd.save_json("qrd.json")
#### Generate Answers To The Questions¶
The next step is to generate answers using an LLM. Just a reminder, that the point is to judge these generated answers. So later on, we will use GPT models to judge these answers.
For the generation of the answers to the questions, we will use another LLM, namely: Llama-2. In order to do this, we first a create a vector store for our documents and an associated retriever, which this LLM answer-generator will use.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever

# Create vector index
the_index = VectorStoreIndex.from_documents(documents=documents)

# Create the retriver on this index
the_retriever = VectorIndexRetriever(
    index=the_index,
    similarity_top_k=2,
)

```

from llama_index.core import VectorStoreIndex from llama_index.core.retrievers import VectorIndexRetriever # Create vector index the_index = VectorStoreIndex.from_documents(documents=documents) # Create the retriver on this index the_retriever = VectorIndexRetriever( index=the_index, similarity_top_k=2, )
From here we will build `RetrieverQueryEngine`'s that will take in our queries (i.e. questions) for processing. Note that we use `HuggingFaceInferenceAPI` for our LLM answer-generators, and that Llama-2 requires permissions. If you haven't yet gain accessed to these models, then feel free to swap out Llama-2 with another model of your choosing.
At this point we will break off the generated questions into two sets: one for building `train_dataset` and another for `test_dataset` that we will build in the next section.
In [ ]:
Copied!
```
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI

llm = HuggingFaceInferenceAPI(
    model_name="meta-llama/Llama-2-7b-chat-hf",
    context_window=2048,  # to use refine
    token=HUGGING_FACE_TOKEN,
)

query_engine = RetrieverQueryEngine.from_args(retriever=the_retriever, llm=llm)

```

from llama_index.core.query_engine import RetrieverQueryEngine from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI llm = HuggingFaceInferenceAPI( model_name="meta-llama/Llama-2-7b-chat-hf", context_window=2048, # to use refine token=HUGGING_FACE_TOKEN, ) query_engine = RetrieverQueryEngine.from_args(retriever=the_retriever, llm=llm)
```
/Users/nerdai/Library/Caches/pypoetry/virtualenvs/llama-index-e6cjsBOJ-py3.10/lib/python3.10/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

In [ ]:
Copied!
```
import tqdm

# we will use 65% of the generated questions for training
train_dataset = []
num_train_questions = int(0.65 * len(qrd.qr_pairs))

for q, a in tqdm.tqdm(qrd.qr_pairs[:num_train_questions]):
    # data for this q
    data_entry = {"question": q, "reference": a}
    response = query_engine.query(q)
    response_struct = {}
    response_struct["model"] = "llama-2"
    response_struct["text"] = str(response)
    response_struct["context"] = (
        response.source_nodes[0].node.text[:1000] + "..."
    )

    data_entry["response_data"] = response_struct
    train_dataset.append(data_entry)

```

import tqdm # we will use 65% of the generated questions for training train_dataset = [] num_train_questions = int(0.65 * len(qrd.qr_pairs)) for q, a in tqdm.tqdm(qrd.qr_pairs[:num_train_questions]): # data for this q data_entry = {"question": q, "reference": a} response = query_engine.query(q) response_struct = {} response_struct["model"] = "llama-2" response_struct["text"] = str(response) response_struct["context"] = ( response.source_nodes[0].node.text[:1000] + "..." ) data_entry["response_data"] = response_struct train_dataset.append(data_entry)
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 79/79 [08:30<00:00,  6.46s/it]

```

### Get GPT-4 Evaluations On The Mistral and LLama-2 Answers¶
As mentioned a couple of times before, the point of this guide is fine-tune an LLM judge from a GPT-4 judge. So, in order to complete our `train_dataset` we now need to instantiate our GPT-4 judge and have it evaluate the answers that were provided by Llama-2. To do this, we will use the `CorrectnessEvaluator` class. What this judge will do then is it will compare the answer to a reference answer and provide a score between 1 and 5 (higher is better) on how close the provided answer aligns to the reference one.
Note also that we use the `OpenAIFineTuningHandler` which will collect all the chat histories that we will eventually need to fine-tune GPT-3.5.
In [ ]:
Copied!
```
# instantiate the gpt-4 judge
from llama_index.llms.openai import OpenAI
from llama_index.finetuning.callbacks import OpenAIFineTuningHandler
from llama_index.core.callbacks import CallbackManager
from llama_index.core.evaluation import CorrectnessEvaluator

finetuning_handler = OpenAIFineTuningHandler()
callback_manager = CallbackManager([finetuning_handler])
gpt_4_llm = OpenAI(
    temperature=0, model="gpt-4", callback_manager=callback_manager
)

gpt4_judge = CorrectnessEvaluator(llm=gpt_4_llm)

```

# instantiate the gpt-4 judge from llama_index.llms.openai import OpenAI from llama_index.finetuning.callbacks import OpenAIFineTuningHandler from llama_index.core.callbacks import CallbackManager from llama_index.core.evaluation import CorrectnessEvaluator finetuning_handler = OpenAIFineTuningHandler() callback_manager = CallbackManager([finetuning_handler]) gpt_4_llm = OpenAI( temperature=0, model="gpt-4", callback_manager=callback_manager ) gpt4_judge = CorrectnessEvaluator(llm=gpt_4_llm)
In [ ]:
Copied!
```
import tqdm

# for `training`
for data_entry in tqdm.tqdm(train_dataset):
    eval_result = await gpt4_judge.aevaluate(
        query=data_entry["question"],
        response=data_entry["response_data"]["text"],
        context=data_entry["response_data"]["context"],
        reference=data_entry["reference"],
    )

    # save final result
    judgement = {}
    judgement["llm"] = "gpt_4"
    judgement["score"] = eval_result.score
    judgement["text"] = eval_result.response
    data_entry["evaluations"] = [judgement]

```

import tqdm # for `training` for data_entry in tqdm.tqdm(train_dataset): eval_result = await gpt4_judge.aevaluate( query=data_entry["question"], response=data_entry["response_data"]["text"], context=data_entry["response_data"]["context"], reference=data_entry["reference"], ) # save final result judgement = {} judgement["llm"] = "gpt_4" judgement["score"] = eval_result.score judgement["text"] = eval_result.response data_entry["evaluations"] = [judgement]
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 79/79 [12:31<00:00,  9.51s/it]

```

In [ ]:
Copied!
```
finetuning_handler.save_finetuning_events("correction_finetuning_events.jsonl")

```

finetuning_handler.save_finetuning_events("correction_finetuning_events.jsonl")
```
Wrote 79 examples to correction_finetuning_events.jsonl

```

## Step 2 Perform knowledge distillation¶
Okay, it's now time to distill some knowledge from GPT-4 to GPT-3.5 To do this, we will make use of the `OpenAIFinetuneEngine` class as well as the `correction_finetuning_events.jsonl` file that we just created.
In [ ]:
Copied!
```
from llama_index.finetuning import OpenAIFinetuneEngine

finetune_engine = OpenAIFinetuneEngine(
    "gpt-3.5-turbo",
    "correction_finetuning_events.jsonl",
)

```

from llama_index.finetuning import OpenAIFinetuneEngine finetune_engine = OpenAIFinetuneEngine( "gpt-3.5-turbo", "correction_finetuning_events.jsonl", )
In [ ]:
Copied!
```
# We can check the status of our current job as follows
# This may take some time ...
finetune_engine.finetune()

```

# We can check the status of our current job as follows # This may take some time ... finetune_engine.finetune()
```
Num examples: 79
First example:
{'role': 'system', 'content': '\nYou are an expert evaluation system for a question answering chatbot.\n\nYou are given the following information:\n- a user query,\n- a reference answer, and\n- a generated answer.\n\nYour job is to judge the relevance and correctness of the generated answer.\nOutput a single score that represents a holistic evaluation.\nYou must return your response in a line with only the score.\nDo not return answers in any other format.\nOn a separate line provide your reasoning for the score as well.\n\nFollow these guidelines for scoring:\n- Your score has to be between 1 and 5, where 1 is the worst and 5 is the best.\n- If the generated answer is not relevant to the user query, you should give a score of 1.\n- If the generated answer is relevant but contains mistakes, you should give a score between 2 and 3.\n- If the generated answer is relevant and fully correct, you should give a score between 4 and 5.\n\nExample Response:\n4.0\nThe generated answer has the exact same metrics as the reference answer,     but it is not as concise.\n\n'}
{'role': 'user', 'content': '\n## User Query\nWhat event in 1906 caused significant damage to San Francisco but was followed by a quick rebuild?\n\n## Reference Answer\nThe great earthquake and fire in 1906 caused significant damage to San Francisco but was followed by a quick rebuild.\n\n## Generated Answer\n1906 earthquake and fire.\n'}
{'role': 'assistant', 'content': '4.0\nThe generated answer is relevant and correct, but it lacks the detail and context provided in the reference answer.'}
No errors found
Num examples missing system message: 0
Num examples missing user message: 0

#### Distribution of num_messages_per_example:
min / max: 3, 3
mean / median: 3.0, 3.0
p5 / p95: 3.0, 3.0

#### Distribution of num_total_tokens_per_example:
min / max: 315, 782
mean / median: 479.49367088607596, 465.0
p5 / p95: 355.6, 634.6

#### Distribution of num_assistant_tokens_per_example:
min / max: 19, 110
mean / median: 57.63291139240506, 56.0
p5 / p95: 29.6, 83.2

0 examples may be over the 4096 token limit, they will be truncated during fine-tuning
Dataset has ~37880 tokens that will be charged for during training
By default, you'll train for 3 epochs on this dataset
By default, you'll be charged for ~113640 tokens
As of August 22, 2023, fine-tuning gpt-3.5-turbo is $0.008 / 1K Tokens.
This means your total cost for training will be $0.30304000000000003 per epoch.

```

In [ ]:
Copied!
```
finetune_engine.get_current_job()

```

finetune_engine.get_current_job()
Out[ ]:
```
<FineTuningJob fine_tuning.job id=ftjob-9y8G7rzbCkzPjsKtPMsfwRSu at 0x1778d6a70> JSON: {
  "object": "fine_tuning.job",
  "id": "ftjob-9y8G7rzbCkzPjsKtPMsfwRSu",
  "model": "gpt-3.5-turbo-0613",
  "created_at": 1698851177,
  "finished_at": 1698851823,
  "fine_tuned_model": "ft:gpt-3.5-turbo-0613:llamaindex::8G7FovVj",
  "organization_id": "org-1ZDAvajC6v2ZtAP9hLEIsXRz",
  "result_files": [
    "file-bx2ObrpVPq7Q2pmv743W1eFQ"
  ],
  "status": "succeeded",
  "validation_file": null,
  "training_file": "file-xAwZ2NSzbck3p8u24kznzySX",
  "hyperparameters": {
    "n_epochs": 3
  },
  "trained_tokens": 113166,
  "error": null
}
```

## 3 Evaluate The Fine-Tuned GPT-3.5 Judge On The Test Dataset¶
Now that we have our fine-tuned GPT-3.5, let's see how well it performs on a test set. But first, remember that we said we'd hold off on creating the `test_dataset` until the time comes that we need it? Well, that time is now. So we will repeat the process of creating the `train_dataset` here but instead now for the `test_dataset`.
NOTE: generating these answers and evaluations will take some time.
In [ ]:
Copied!
```
# Use Llama-2 to generate answers to the test questions
test_dataset = []
for q, a in tqdm.tqdm(qrd.qr_pairs[num_train_questions:]):
    # data for this q
    data_entry = {"question": q, "reference": a}
    response = query_engine.query(q)
    response_struct = {}
    response_struct["model"] = "llama-2"
    response_struct["text"] = str(response)
    response_struct["context"] = (
        response.source_nodes[0].node.text[:1000] + "..."
    )

    data_entry["response_data"] = response_struct
    test_dataset.append(data_entry)

```

# Use Llama-2 to generate answers to the test questions test_dataset = [] for q, a in tqdm.tqdm(qrd.qr_pairs[num_train_questions:]): # data for this q data_entry = {"question": q, "reference": a} response = query_engine.query(q) response_struct = {} response_struct["model"] = "llama-2" response_struct["text"] = str(response) response_struct["context"] = ( response.source_nodes[0].node.text[:1000] + "..." ) data_entry["response_data"] = response_struct test_dataset.append(data_entry)
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 44/44 [05:07<00:00,  6.99s/it]

```

In [ ]:
Copied!
```
# get the gpt-4 judgements on the Llama-2 answers
for data_entry in tqdm.tqdm(test_dataset):
    eval_result = await gpt4_judge.aevaluate(
        query=data_entry["question"],
        response=data_entry["response_data"]["text"],
        context=data_entry["response_data"]["context"],
        reference=data_entry["reference"],
    )

    # save final result
    judgement = {}
    judgement["llm"] = "gpt_4"
    judgement["score"] = eval_result.score
    judgement["text"] = eval_result.response
    data_entry["evaluations"] = [judgement]

```

# get the gpt-4 judgements on the Llama-2 answers for data_entry in tqdm.tqdm(test_dataset): eval_result = await gpt4_judge.aevaluate( query=data_entry["question"], response=data_entry["response_data"]["text"], context=data_entry["response_data"]["context"], reference=data_entry["reference"], ) # save final result judgement = {} judgement["llm"] = "gpt_4" judgement["score"] = eval_result.score judgement["text"] = eval_result.response data_entry["evaluations"] = [judgement]
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 44/44 [06:52<00:00,  9.37s/it]

```

In [ ]:
Copied!
```
from llama_index.core.evaluation import EvaluationResult

# use our fine-tuned GPT-3.5 to evaluate the answers
ft_llm = finetune_engine.get_finetuned_model()

ft_gpt_3p5_judge = CorrectnessEvaluator(llm=ft_llm)

for data_entry in tqdm.tqdm(test_dataset):
    eval_result = await ft_gpt_3p5_judge.aevaluate(
        query=data_entry["question"],
        response=data_entry["response_data"]["text"],
        context=data_entry["response_data"]["context"],
        reference=data_entry["reference"],
    )

    # save final result
    judgement = {}
    judgement["llm"] = "ft_gpt_3p5"
    judgement["score"] = eval_result.score
    judgement["text"] = eval_result.response
    data_entry["evaluations"] += [judgement]

```

from llama_index.core.evaluation import EvaluationResult # use our fine-tuned GPT-3.5 to evaluate the answers ft_llm = finetune_engine.get_finetuned_model() ft_gpt_3p5_judge = CorrectnessEvaluator(llm=ft_llm) for data_entry in tqdm.tqdm(test_dataset): eval_result = await ft_gpt_3p5_judge.aevaluate( query=data_entry["question"], response=data_entry["response_data"]["text"], context=data_entry["response_data"]["context"], reference=data_entry["reference"], ) # save final result judgement = {} judgement["llm"] = "ft_gpt_3p5" judgement["score"] = eval_result.score judgement["text"] = eval_result.response data_entry["evaluations"] += [judgement]
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 44/44 [00:44<00:00,  1.02s/it]

```

In [ ]:
Copied!
```
# Similarly, use a non-fine-tuned judge to evaluate the answers
gpt_3p5_llm = OpenAI(model="gpt-3.5-turbo")

gpt_3p5_judge = CorrectnessEvaluator(llm=gpt_3p5_llm)

for data_entry in tqdm.tqdm(test_dataset):
    eval_result = await gpt_3p5_judge.aevaluate(
        query=data_entry["question"],
        response=data_entry["response_data"]["text"],
        context=data_entry["response_data"]["context"],
        reference=data_entry["reference"],
    )

    # save final result
    judgement = {}
    judgement["llm"] = "gpt_3p5"
    judgement["score"] = eval_result.score
    judgement["text"] = eval_result.response
    data_entry["evaluations"] += [judgement]

```

# Similarly, use a non-fine-tuned judge to evaluate the answers gpt_3p5_llm = OpenAI(model="gpt-3.5-turbo") gpt_3p5_judge = CorrectnessEvaluator(llm=gpt_3p5_llm) for data_entry in tqdm.tqdm(test_dataset): eval_result = await gpt_3p5_judge.aevaluate( query=data_entry["question"], response=data_entry["response_data"]["text"], context=data_entry["response_data"]["context"], reference=data_entry["reference"], ) # save final result judgement = {} judgement["llm"] = "gpt_3p5" judgement["score"] = eval_result.score judgement["text"] = eval_result.response data_entry["evaluations"] += [judgement]
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 44/44 [01:36<00:00,  2.19s/it]

```

### The Metrics¶
Phew! Now that we have generated all of the LLM judges evaluations of the Llama-2/Mistral answers on the test queries. Let's now get a quantitative view on how close fine-tuned GPT-3.5 is to GPT-4.
For this, we report the Correlation between the scores of the fine-tuned (and, not-fine-tuned) GPT-3.5 to that of the GPT-4 judge.
In [ ]:
Copied!
```
REPORT_FMT_STR = (
    "{model}\n"
    "-----------------\n"
    "Number of obs.: {total_obs}\n"
    "Correlation with GPT-4: {corr}\n"
)

```

REPORT_FMT_STR = ( "{model}\n" "-----------------\n" "Number of obs.: {total_obs}\n" "Correlation with GPT-4: {corr}\n" )
In [ ]:
Copied!
```
import numpy as np

scores = {"gpt_4": [], "gpt_3p5": [], "ft_gpt_3p5": []}
for ix, d in enumerate(test_dataset):
    for e in d["evaluations"]:
        scores[e["llm"]].append(e["score"])

```

import numpy as np scores = {"gpt_4": [], "gpt_3p5": [], "ft_gpt_3p5": []} for ix, d in enumerate(test_dataset): for e in d["evaluations"]: scores[e["llm"]].append(e["score"])
In [ ]:
Copied!
```
# numpy conversion
np_scores_gpt_4 = np.array(scores["gpt_4"])
np_scores_gpt_3p5 = np.array(scores["gpt_3p5"])
np_scores_ft_gpt_3p5 = np.array(scores["ft_gpt_3p5"])

# correlations
corr_ft = np.corrcoef(np_scores_gpt_4, np_scores_ft_gpt_3p5)[0, 1]
corr_no_ft = np.corrcoef(np_scores_gpt_4, np_scores_gpt_3p5)[0, 1]

print(
    REPORT_FMT_STR.format(
        model="GPT-3.5 w/ fine-tuning",
        total_obs=np_scores_gpt_4.shape[0],
        corr=corr_ft,
    )
)
print("\n")
print(
    REPORT_FMT_STR.format(
        model="GPT-3.5 w/out fine-tuning",
        total_obs=np_scores_gpt_4.shape[0],
        corr=corr_no_ft,
    )
)

```

# numpy conversion np_scores_gpt_4 = np.array(scores["gpt_4"]) np_scores_gpt_3p5 = np.array(scores["gpt_3p5"]) np_scores_ft_gpt_3p5 = np.array(scores["ft_gpt_3p5"]) # correlations corr_ft = np.corrcoef(np_scores_gpt_4, np_scores_ft_gpt_3p5)[0, 1] corr_no_ft = np.corrcoef(np_scores_gpt_4, np_scores_gpt_3p5)[0, 1] print( REPORT_FMT_STR.format( model="GPT-3.5 w/ fine-tuning", total_obs=np_scores_gpt_4.shape[0], corr=corr_ft, ) ) print("\n") print( REPORT_FMT_STR.format( model="GPT-3.5 w/out fine-tuning", total_obs=np_scores_gpt_4.shape[0], corr=corr_no_ft, ) )
```
GPT-3.5 w/ fine-tuning
-----------------
Number of obs.: 44
Correlation with GPT-4: 0.9279850303778618



GPT-3.5 w/out fine-tuning
-----------------
Number of obs.: 44
Correlation with GPT-4: 0.8737418723878325


```

## Conclusion¶
From the above numbers we see that fine-tuning a GPT-3.5 judge yields higher correlation to GPT-4 that does its non-fine-tuned counterpart. Thus, for this case, we see that fine-tuning has helped us to obtain a GPT-3.5 judge that is closer to a GPT-4 judge (and thus by proxy, closer to human judgements).
