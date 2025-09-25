# Fine Tuning GPT-3.5-Turbo¶
In this notebook, we walk through an example of fine-tuning gpt-3.5-turbo.
Specifically, we attempt to distill GPT-4's knowledge, by generating training data with GPT-4 to then fine-tune GPT-3.5.
All training data is generated using two different sections of our index data, creating both a training and evalution set.
We then finetune with our `OpenAIFinetuneEngine` wrapper abstraction.
Evaluation is done using the `ragas` library, which we will detail later on.
In [ ]:
Copied!
```
%pip install llama-index-finetuning
%pip install llama-index-finetuning-callbacks
%pip install llama-index-llms-openai

```

%pip install llama-index-finetuning %pip install llama-index-finetuning-callbacks %pip install llama-index-llms-openai
In [ ]:
Copied!
```
# !pip install llama-index pypdf sentence-transformers ragas

```

# !pip install llama-index pypdf sentence-transformers ragas
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
openai.api_key = os.environ["OPENAI_API_KEY"]

```

os.environ["OPENAI_API_KEY"] = "sk-..." openai.api_key = os.environ["OPENAI_API_KEY"]
## Data Setup¶
Here, we first down load the PDF that we will use to generate training data.
In [ ]:
Copied!
```
!curl https://www.ipcc.ch/report/ar6/wg2/downloads/report/IPCC_AR6_WGII_Chapter03.pdf --output IPCC_AR6_WGII_Chapter03.pdf

```

!curl https://www.ipcc.ch/report/ar6/wg2/downloads/report/IPCC_AR6_WGII_Chapter03.pdf --output IPCC_AR6_WGII_Chapter03.pdf
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 20.7M  100 20.7M    0     0   397k      0  0:00:53  0:00:53 --:--:--  417k84k      0  0:00:55  0:00:24  0:00:31  406k    0   395k      0  0:00:53  0:00:48  0:00:05  403k0   396k      0  0:00:53  0:00:53 --:--:--  406k

```

The next step is generating a training and eval dataset.
We will generate 40 questions on different sections of the PDF we downloaded.
We can use GPT-3.5 on the eval questions to get our baseline performance.
Then, we will use GPT-4 on the train questions to generate our training data. The training data will be collected with out `OpenAIFineTuningHandler`.
This step is entirely optional if you don't want to spend the time/tokens -- the eval and training questions are also provided in this folder, as well as the training data!
### Train Generation¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import DatasetGenerator

documents = SimpleDirectoryReader(
    input_files=["IPCC_AR6_WGII_Chapter03.pdf"]
).load_data()

# Shuffle the documents
import random

random.seed(42)
random.shuffle(documents)

gpt_35_llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)

```

from llama_index.core import SimpleDirectoryReader from llama_index.llms.openai import OpenAI from llama_index.core.evaluation import DatasetGenerator documents = SimpleDirectoryReader( input_files=["IPCC_AR6_WGII_Chapter03.pdf"] ).load_data() # Shuffle the documents import random random.seed(42) random.shuffle(documents) gpt_35_llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)
In [ ]:
Copied!
```
question_gen_query = (
    "You are a Teacher/ Professor. Your task is to setup "
    "a quiz/examination. Using the provided context, formulate "
    "a single question that captures an important fact from the "
    "context. Restrict the question to the context information provided."
)

dataset_generator = DatasetGenerator.from_documents(
    documents[:50],
    question_gen_query=question_gen_query,
    llm=gpt_35_llm,
)

```

question_gen_query = ( "You are a Teacher/ Professor. Your task is to setup " "a quiz/examination. Using the provided context, formulate " "a single question that captures an important fact from the " "context. Restrict the question to the context information provided." ) dataset_generator = DatasetGenerator.from_documents( documents[:50], question_gen_query=question_gen_query, llm=gpt_35_llm, )
In [ ]:
Copied!
```
# NOTE: this may take some time. Go grab a coffee!
questions = dataset_generator.generate_questions_from_nodes(num=40)
print("Generated ", len(questions), " questions")

```

# NOTE: this may take some time. Go grab a coffee! questions = dataset_generator.generate_questions_from_nodes(num=40) print("Generated ", len(questions), " questions")
```
Generated  40  questions

```

In [ ]:
Copied!
```
with open("train_questions.txt", "w") as f:
    for question in questions:
        f.write(question + "\n")

```

with open("train_questions.txt", "w") as f: for question in questions: f.write(question + "\n")
### Eval Generation¶
Now, lets generate questions on a completely different set of documents, in order to create our eval dataset.
In [ ]:
Copied!
```
dataset_generator = DatasetGenerator.from_documents(
    documents[
        50:
    ],  # since we generated ~1 question for 40 documents, we can skip the first 40
    question_gen_query=question_gen_query,
    llm=gpt_35_llm,
)

```

dataset_generator = DatasetGenerator.from_documents( documents[ 50: ], # since we generated ~1 question for 40 documents, we can skip the first 40 question_gen_query=question_gen_query, llm=gpt_35_llm, )
In [ ]:
Copied!
```
# NOTE: this may take some time. Go grab a coffee!
questions = dataset_generator.generate_questions_from_nodes(num=40)
print("Generated ", len(questions), " questions")

```

# NOTE: this may take some time. Go grab a coffee! questions = dataset_generator.generate_questions_from_nodes(num=40) print("Generated ", len(questions), " questions")
```
Generated  40  questions

```

In [ ]:
Copied!
```
with open("eval_questions.txt", "w") as f:
    for question in questions:
        f.write(question + "\n")

```

with open("eval_questions.txt", "w") as f: for question in questions: f.write(question + "\n")
## Initial Eval with GPT-3.5-Turbo Query Engine¶
For this eval, we will be using the `ragas` evaluation library.
Ragas has a ton of evaluation metrics for RAG pipelines, and you can read about them here.
For this notebook, we will be using the following two metrics
  * `answer_relevancy` - This measures how relevant is the generated answer to the prompt. If the generated answer is incomplete or contains redundant information the score will be low. This is quantified by working out the chance of an LLM generating the given question using the generated answer. Values range (0,1), higher the better.
  * `faithfulness` - This measures the factual consistency of the generated answer against the given context. This is done using a multi step paradigm that includes creation of statements from the generated answer followed by verifying each of these statements against the context. The answer is scaled to (0,1) range. Higher the better.


In [ ]:
Copied!
```
questions = []
with open("eval_questions.txt", "r") as f:
    for line in f:
        questions.append(line.strip())

```

questions = [] with open("eval_questions.txt", "r") as f: for line in f: questions.append(line.strip())
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

# limit the context window to 2048 tokens so that refine is used
from llama_index.core import Settings

Settings.context_window = 2048

index = VectorStoreIndex.from_documents(
    documents,
)

query_engine = index.as_query_engine(similarity_top_k=2, llm=gpt_35_llm)

```

from llama_index.core import VectorStoreIndex # limit the context window to 2048 tokens so that refine is used from llama_index.core import Settings Settings.context_window = 2048 index = VectorStoreIndex.from_documents( documents, ) query_engine = index.as_query_engine(similarity_top_k=2, llm=gpt_35_llm)
In [ ]:
Copied!
```
contexts = []
answers = []

for question in questions:
    response = query_engine.query(question)
    contexts.append([x.node.get_content() for x in response.source_nodes])
    answers.append(str(response))

```

contexts = [] answers = [] for question in questions: response = query_engine.query(question) contexts.append([x.node.get_content() for x in response.source_nodes]) answers.append(str(response))
In [ ]:
Copied!
```
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness

ds = Dataset.from_dict(
    {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
    }
)

result = evaluate(ds, [answer_relevancy, faithfulness])
print(result)

```

from datasets import Dataset from ragas import evaluate from ragas.metrics import answer_relevancy, faithfulness ds = Dataset.from_dict( { "question": questions, "answer": answers, "contexts": contexts, } ) result = evaluate(ds, [answer_relevancy, faithfulness]) print(result)
```
evaluating with [answer_relevancy]

```

```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [01:02<00:00, 20.69s/it]

```

```
evaluating with [faithfulness]

```

```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [03:52<00:00, 77.37s/it]

```

```
{'ragas_score': 0.8356, 'answer_relevancy': 0.9725, 'faithfulness': 0.7325}

```

## GPT-4 to Collect Training Data¶
Here, we use GPT-4 and the `OpenAIFineTuningHandler` to collect data that we want to train on.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.finetuning.callbacks import OpenAIFineTuningHandler
from llama_index.core.callbacks import CallbackManager

finetuning_handler = OpenAIFineTuningHandler()
callback_manager = CallbackManager([finetuning_handler])

llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)
llm.callback_manager = callback_manager

```

from llama_index.llms.openai import OpenAI from llama_index.finetuning.callbacks import OpenAIFineTuningHandler from llama_index.core.callbacks import CallbackManager finetuning_handler = OpenAIFineTuningHandler() callback_manager = CallbackManager([finetuning_handler]) llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3) llm.callback_manager = callback_manager
In [ ]:
Copied!
```
questions = []
with open("train_questions.txt", "r") as f:
    for line in f:
        questions.append(line.strip())

```

questions = [] with open("train_questions.txt", "r") as f: for line in f: questions.append(line.strip())
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(
    documents,
)

query_engine = index.as_query_engine(similarity_top_k=2, llm=llm)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents( documents, ) query_engine = index.as_query_engine(similarity_top_k=2, llm=llm)
In [ ]:
Copied!
```
for question in questions:
    response = query_engine.query(question)

```

for question in questions: response = query_engine.query(question)
## Create `OpenAIFinetuneEngine`¶
We create an `OpenAIFinetuneEngine`: the finetune engine will take care of launching a finetuning job, and returning an LLM model that you can directly plugin to the rest of LlamaIndex workflows.
We use the default constructor, but we can also directly pass in our finetuning_handler into this engine with the `from_finetuning_handler` class method.
In [ ]:
Copied!
```
finetuning_handler.save_finetuning_events("finetuning_events.jsonl")

```

finetuning_handler.save_finetuning_events("finetuning_events.jsonl")
In [ ]:
Copied!
```
from llama_index.finetuning import OpenAIFinetuneEngine

finetune_engine = OpenAIFinetuneEngine(
    "gpt-3.5-turbo",
    "finetuning_events.jsonl",
    # start_job_id="<start-job-id>"  # if you have an existing job, can specify id here
)

# finetune_engine = OpenAIFinetuneEngine.from_finetuning_handler(
#     finetuning_handler,
#     "gpt-3.5-turbo",
#     "tmp.jsonl"
# )

```

from llama_index.finetuning import OpenAIFinetuneEngine finetune_engine = OpenAIFinetuneEngine( "gpt-3.5-turbo", "finetuning_events.jsonl", # start_job_id="" # if you have an existing job, can specify id here ) # finetune_engine = OpenAIFinetuneEngine.from_finetuning_handler( # finetuning_handler, # "gpt-3.5-turbo", # "tmp.jsonl" # )
In [ ]:
Copied!
```
finetune_engine.finetune()

```

finetune_engine.finetune()
```
Num examples: 61
First example:
{'role': 'system', 'content': "You are an expert Q&A system that is trusted around the world.\nAlways answer the query using the provided context information, and not prior knowledge.\nSome rules to follow:\n1. Never directly reference the given context in your answer.\n2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines."}
{'role': 'user', 'content': 'Context information is below.\n---------------------\npage_label: 410\nfile_name: IPCC_AR6_WGII_Chapter03.pdf\n\nIt is challenging to apply this experimental approach to communities or ecosystems (see Figure \nBox\xa03.1.1).To date, most research on community or ecosystem response to climate-induced drivers has been in large-volume (>10,000 l) \nmesocosms (Riebesell and Gattuso, 2014), or at natural analogues such as CO 2 seeps, in which only one driver (ocean acidification) is \naltered (see (4) in Figure Box\xa03.1.1).Only very recently have two drivers been incorporated into climate-change manipulation studies \nexamining responses of primary producers to secondary consumers (see (5) in Figure Box\xa03.1.1a; Nagelkerken et\xa0al., 2020).Therefore, \n‘natural experiments’ from the geological past (Reddin et\xa0al., 2020) provide insights into how food webs and their constituents respond to \ncomplex change involving multiple drivers.Contemporary observations are occasionally long enough (>50\xa0years) to capture community \nresponses to complex climate change.For example, Brun et\xa0al.(2019) reported a shift in zooplankton community structure in the North \nAtlantic (1960–2014), with major biogeochemical ramifications.Conducting sufficiently long manipulation experiments to study the effect of adaptation on organisms is equally difficult (see Figure \nBox\xa03.1.1b), with much research restricted to multi-year studies of the microevolution of fast-growing (more than one division per day) \nphytoplankton species responding to single drivers (Lohbeck et\xa0al., 2012; Schaum et\xa0al., 2016).In a few experimental evolution studies \n(see (7) in Figure Box\xa03.1.1a; Brennan et\xa0al., 2017), multiple drivers have been used, but none have used communities or ecosystems (see \nFigure Box\xa03.1.1b).Nevertheless, the fossil record provides limited evidence of adaptations to less rapid (relative to present day) climate \nchange (Jackson et\xa0al., 2018).Despite the need to explore ecological or biogeochemical responses to projected future ocean conditions, \nlogistical challenges require that assessments of climate-change impacts at scales larger than mesocosms use large-scale, long-term in \nsitu observational studies (as documented in Section\xa03.4).\n\npage_label: 409\nfile_name: IPCC_AR6_WGII_Chapter03.pdf\n\n3\n409Oceans and Coastal Ecosystems and Their Services  Chapter 3\nunderlies inhibited thermal adaptation under nitrogen-limited \nconditions (low confidence) (Aranguren-Gassis et\xa0 al., 2019).When \nselection is strong due to unfavourable environmental conditions, \nmicrobial populations can encounter functional and evolutionary \ntrade-offs evidenced by reducing growth rates while increasing \ntolerance and metabolism of reactive oxygen species (Lindberg and \nCollins, 2020).Other trade-offs can be observed in offspring quality \nand number (Lindberg and Collins, 2020).These findings contribute \ntowards a mechanistic framework describing the range of evolutionary \nstrategies in response to multiple drivers (Collins et\xa0al., 2020), but other \nhazards, such as extreme events (e.g., MHWs), still need to be included \nbecause their characteristics may alter the potential for adaptation of \nspecies and populations to climate change (Gruber et\xa0al., 2021).3.3.5 Ecological Response to Multiple Drivers\nAssessing ecological responses to multiple climate-induced drivers \nrequires a combination of approaches, including laboratory- and \nfield-based experiments, field observations (e.g., natural gradients, \nclimate analogues), study of paleo-analogues and the development \nof mechanistic and empirical models (Clapham, 2019; Gissi et\xa0 al., \n2021).Experimental studies of food-web responses are often limited \nto an individual driver, although recent manipulations have used a \nmatrix of >1000-l mesocosms to explore ecological responses to both \nwarming and acidification (see Box\xa0 3.1; Nagelkerken et\xa0 al., 2020).Hence, complementary approaches are needed to indirectly explore \nthe mechanisms underlying ecosystem responses to global climate \nchange (Parmesan et\xa0al., 2013).Observations from time series longer \nthan modes of natural variability (i.e., decades) are essential for \nrevealing and attributing ecological responses to climate change (e.g., \nSection\xa03.4; Barton et\xa0al., 2015b; Brun et\xa0al., 2019).Also, paleorecords \nprovide insights into the influence of multiple drivers on marine \nbiota (Cross-Chapter Box\xa0 PALEO in Chapter\xa0 1; Reddin et\xa0 al., 2020).Specifically, associations between vulnerabilities and traits of marine \nectotherms in laboratory experiments correspond with organismal \nresponses to ancient hyperthermal events (medium confidence) \n(Reddin et\xa0 al., 2020).This corroboration suggests that responses to \nmultiple drivers inferred from the fossil record can help provide insights \ninto the future status of functional groups, and hence food webs, under \nrapid climate change.Multi-species and integrated end-to-end ecosystem models are \npowerful tools to explore and project outcomes to the often-interacting \ncumulative effects of climate change and other anthropogenic drivers \n(Section\xa03.1; Kaplan and Marshall, 2016; Koenigstein et\xa0al., 2016; Peck \nand Pinnegar, 2018; Tittensor et\xa0 al., 2018; Gissi et\xa0 al., 2021).These \nmodels can integrate some aspects of the knowledge accrued from \nmanipulation experiments, paleo- and contemporary observations, help \ntest the relative importance of specific drivers and driver combinations, \nand identify synergistic or antagonistic responses (Koenigstein et\xa0al., \n2016; Payne et\xa0al., 2016; Skogen et\xa0al., 2018; Tittensor et\xa0al., 2018).As these models are associated with wide-ranging uncertainties \n(SM3.2.2; Payne et\xa0 al., 2016; Trolle et\xa0 al., 2019; Heneghan et\xa0 al., \n2021), they cannot be expected to accurately project the trajectories \nof complex marine ecosystems under climate change; hence, they are \nmost useful for assessing overall trends and in particular for providing a plausible envelope of trajectories across a range of assumptions \n(Fulton et\xa0al., 2018; Peck et\xa0al., 2018; Tittensor et\xa0al., 2018).\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: What are some approaches used to assess ecological responses to multiple climate-induced drivers in the context of climate change and the oceans?\nAnswer: '}
{'role': 'assistant', 'content': 'Several approaches are used to assess ecological responses to multiple climate-induced drivers. These include laboratory- and field-based experiments, field observations such as natural gradients and climate analogues, the study of paleo-analogues, and the development of mechanistic and empirical models. Experimental studies often focus on individual drivers, but recent manipulations have used large-volume mesocosms to explore ecological responses to both warming and acidification. Observations from time series longer than modes of natural variability are essential for revealing and attributing ecological responses to climate change. Paleorecords also provide insights into the influence of multiple drivers on marine biota. Multi-species and integrated end-to-end ecosystem models are powerful tools to explore and project outcomes to the often-interacting cumulative effects of climate change and other anthropogenic drivers. These models can integrate some aspects of the knowledge accrued from manipulation experiments, paleo- and contemporary observations, help test the relative importance of specific drivers and driver combinations, and identify synergistic or antagonistic responses.'}
No errors found
Num examples missing system message: 21
Num examples missing user message: 0

#### Distribution of num_messages_per_example:
min / max: 2, 3
mean / median: 2.6557377049180326, 3.0
p5 / p95: 2.0, 3.0

#### Distribution of num_total_tokens_per_example:
min / max: 229, 2011
mean / median: 1274.27868852459, 1385.0
p5 / p95: 533.0, 1848.0

#### Distribution of num_assistant_tokens_per_example:
min / max: 11, 334
mean / median: 72.36065573770492, 37.0
p5 / p95: 23.0, 193.0

0 examples may be over the 4096 token limit, they will be truncated during fine-tuning
Dataset has ~77731 tokens that will be charged for during training
By default, you'll train for 3 epochs on this dataset
By default, you'll be charged for ~233193 tokens
As of Augest 22, 2023, fine-tuning gpt-3.5-turbo is $0.008 / 1K Tokens.
This means your total cost for training will be $0.621848 per epoch.
Waiting for file to be ready...

```

In [ ]:
Copied!
```
finetune_engine.get_current_job()

```

finetune_engine.get_current_job()
Out[ ]:
```
<FineTuningJob fine_tuning.job id=ftjob-u9T7BF5zRxVX4n5b9Jtbb5cR at 0x2c641fe20> JSON: {
  "object": "fine_tuning.job",
  "id": "ftjob-u9T7BF5zRxVX4n5b9Jtbb5cR",
  "model": "gpt-3.5-turbo-0613",
  "created_at": 1693254044,
  "finished_at": null,
  "fine_tuned_model": null,
  "organization_id": "org-1ZDAvajC6v2ZtAP9hLEIsXRz",
  "result_files": [],
  "status": "running",
  "validation_file": null,
  "training_file": "file-j1fwmqIAoqZXWZQ8EqwHucXs",
  "hyperparameters": {
    "n_epochs": 3
  },
  "trained_tokens": null
}
```

In [ ]:
Copied!
```
ft_llm = finetune_engine.get_finetuned_model(temperature=0.3)

```

ft_llm = finetune_engine.get_finetuned_model(temperature=0.3)
## Evaluation¶
After some time, your model will be done training!
The next step is running our fine-tuned model on our eval dataset again to measure any performance increase.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.finetuning.callbacks import OpenAIFineTuningHandler
from llama_index.core.callbacks import CallbackManager


# Option 1: pass in ft_llm directly into Settings
from llama_index.core import Settings

Settings.llm = ft_llm
Settings.context_window = (
    2048  # limit the context window artifically to test refine process
)

# # Option 2: you can also specify the model name manually
# ft_model_name = "ft:gpt-3.5-turbo-0613:..."
# Settings.llm = OpenAI(model=ft_model_name, temperature=0.3)

```

from llama_index.llms.openai import OpenAI from llama_index.finetuning.callbacks import OpenAIFineTuningHandler from llama_index.core.callbacks import CallbackManager # Option 1: pass in ft_llm directly into Settings from llama_index.core import Settings Settings.llm = ft_llm Settings.context_window = ( 2048 # limit the context window artifically to test refine process ) # # Option 2: you can also specify the model name manually # ft_model_name = "ft:gpt-3.5-turbo-0613:..." # Settings.llm = OpenAI(model=ft_model_name, temperature=0.3)
In [ ]:
Copied!
```
questions = []
with open("eval_questions.txt", "r") as f:
    for line in f:
        questions.append(line.strip())

```

questions = [] with open("eval_questions.txt", "r") as f: for line in f: questions.append(line.strip())
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine(similarity_top_k=2, llm=ft_llm)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents) query_engine = index.as_query_engine(similarity_top_k=2, llm=ft_llm)
In [ ]:
Copied!
```
contexts = []
answers = []

for question in questions:
    response = query_engine.query(question)
    contexts.append([x.node.get_content() for x in response.source_nodes])
    answers.append(str(response))

```

contexts = [] answers = [] for question in questions: response = query_engine.query(question) contexts.append([x.node.get_content() for x in response.source_nodes]) answers.append(str(response))
In [ ]:
Copied!
```
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness

ds = Dataset.from_dict(
    {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
    }
)

result = evaluate(ds, [answer_relevancy, faithfulness])
print(result)

```

from datasets import Dataset from ragas import evaluate from ragas.metrics import answer_relevancy, faithfulness ds = Dataset.from_dict( { "question": questions, "answer": answers, "contexts": contexts, } ) result = evaluate(ds, [answer_relevancy, faithfulness]) print(result)
```
evaluating with [answer_relevancy]

```

```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [00:49<00:00, 16.34s/it]

```

```
evaluating with [faithfulness]

```

```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [04:04<00:00, 81.44s/it]

```

```
{'ragas_score': 0.8680, 'answer_relevancy': 0.9607, 'faithfulness': 0.7917}

```

## Exploring Differences¶
Let's quickly compare the differences in responses, to demonstrate that fine tuning did indeed change something.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
questions = []
with open("eval_questions.txt", "r") as f:
    for line in f:
        questions.append(line.strip())

```

questions = [] with open("eval_questions.txt", "r") as f: for line in f: questions.append(line.strip())
In [ ]:
Copied!
```
print(questions[12])

```

print(questions[12])
```
What is a key barrier globally for ocean health, governance, and adaptation to climate change, according to the report?

```

### Original¶
In [ ]:
Copied!
```
from llama_index.core.response.notebook_utils import display_response
from llama_index.llms.openai import OpenAI


gpt_35_llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)

```

from llama_index.core.response.notebook_utils import display_response from llama_index.llms.openai import OpenAI gpt_35_llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)
In [ ]:
Copied!
```
query_engine = index.as_query_engine(llm=gpt_35_llm)

response = query_engine.query(questions[12])

display_response(response)

```

query_engine = index.as_query_engine(llm=gpt_35_llm) response = query_engine.query(questions[12]) display_response(response)
**`Final Response:`**A key barrier globally for ocean health, governance, and adaptation to climate change, according to the report, is the availability of technology, knowledge, and financial support, as well as existing governance structures.
### Fine-Tuned¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(llm=ft_llm)

response = query_engine.query(questions[12])

display_response(response)

```

query_engine = index.as_query_engine(llm=ft_llm) response = query_engine.query(questions[12]) display_response(response)
**`Final Response:`**The report identifies a broad range of barriers and limits for adaptation to climate change in ecosystems and human systems. These include the availability of technology, knowledge, and financial support, as well as existing governance structures. Existing ocean-governance structures are already facing multi-dimensional, scale-related challenges because of climate change.
As we can see, the fine-tuned model provides a more thorough response! This lines up with the increased faithfullness score from ragas, since the answer is more representative of the retrieved context.
## Conclusion¶
So, in conclusion, finetuning with only ~61 questions actually helped improve our eval scores!
**answer_relevancy: 0.9725 - > 0.9607**
The answer relevancy dips slightly but it's very small.
**faithfulness: 0.7325 - > 0.7917**
The faithfulness appears to have been improved! This mains the anwers given better fuffil the original question that was asked.
