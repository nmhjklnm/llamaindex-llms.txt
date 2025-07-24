![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Fine Tuning MistralAI models using Finetuning API¶
In this notebook, we walk through an example of fine-tuning `open-mistral-7b` using MistralAI finetuning API.
Specifically, we attempt to distill `mistral-large-latest`'s knowledge, by generating training data with `mistral-large-latest` to then fine-tune `open-mistral-7b`.
All training data is generated using two different sections of our index data, creating both a training and evalution set.
We will use `mistral-small-largest` to create synthetic training and evaluation questions to avoid any biases towards `open-mistral-7b` and `mistral-large-latest`.
We then finetune with our `MistraAIFinetuneEngine` wrapper abstraction.
Evaluation is done using the `ragas` library, which we will detail later on.
We can monitor the metrics on `Weights & Biases`
In [ ]:
Copied!
```
%pip install llama-index-finetuning
%pip install llama-index-finetuning-callbacks
%pip install llama-index-llms-mistralai
%pip install llama-index-embeddings-mistralai

```

%pip install llama-index-finetuning %pip install llama-index-finetuning-callbacks %pip install llama-index-llms-mistralai %pip install llama-index-embeddings-mistralai
In [ ]:
Copied!
```
# !pip install llama-index pypdf sentence-transformers ragas

```

# !pip install llama-index pypdf sentence-transformers ragas
In [ ]:
Copied!
```
# NESTED ASYNCIO LOOP NEEDED TO RUN ASYNC IN A NOTEBOOK
import nest_asyncio

nest_asyncio.apply()

```

# NESTED ASYNCIO LOOP NEEDED TO RUN ASYNC IN A NOTEBOOK import nest_asyncio nest_asyncio.apply()
## Set API Key¶
In [ ]:
Copied!
```
import os

os.environ["MISTRAL_API_KEY"] = "<YOUR MISTRALAI API KEY>"

```

import os os.environ["MISTRAL_API_KEY"] = ""
## Download Data¶
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
100 20.7M  100 20.7M    0     0   249k      0  0:01:25  0:01:25 --:--:--  266k0  0:01:31  0:00:25  0:01:06  267k 251k

```

The next step is generating a training and eval dataset.
We will generate 40 training and 40 evaluation questions on different sections of the PDF we downloaded.
We can use `open-mistral-7b` on the eval questions to get our baseline performance.
Then, we will use `mistral-large-latest` on the train questions to generate our training data.
## Load Data¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader
from llama_index.core.evaluation import DatasetGenerator

documents = SimpleDirectoryReader(
    input_files=["IPCC_AR6_WGII_Chapter03.pdf"]
).load_data()

```

from llama_index.core import SimpleDirectoryReader from llama_index.core.evaluation import DatasetGenerator documents = SimpleDirectoryReader( input_files=["IPCC_AR6_WGII_Chapter03.pdf"] ).load_data()
## Setup LLM and Embedding Model¶
In [ ]:
Copied!
```
from llama_index.llms.mistralai import MistralAI
from llama_index.embeddings.mistralai import MistralAIEmbedding

open_mistral = MistralAI(
    model="open-mistral-7b", temperature=0.1
)  # model to be finetuning
mistral_small = MistralAI(
    model="mistral-small-latest", temperature=0.1
)  # model for question generation
embed_model = MistralAIEmbedding()

```

from llama_index.llms.mistralai import MistralAI from llama_index.embeddings.mistralai import MistralAIEmbedding open_mistral = MistralAI( model="open-mistral-7b", temperature=0.1 ) # model to be finetuning mistral_small = MistralAI( model="mistral-small-latest", temperature=0.1 ) # model for question generation embed_model = MistralAIEmbedding()
## Training and Evaluation Data Generation¶
In [ ]:
Copied!
```
question_gen_query = (
    "You are a Teacher/ Professor. Your task is to setup "
    "a quiz/examination. Using the provided context, formulate "
    "a single question that captures an important fact from the "
    "context. Restrict the question to the context information provided."
    "You should generate only question and nothing else."
)

dataset_generator = DatasetGenerator.from_documents(
    documents[:80],
    question_gen_query=question_gen_query,
    llm=mistral_small,
)

```

question_gen_query = ( "You are a Teacher/ Professor. Your task is to setup " "a quiz/examination. Using the provided context, formulate " "a single question that captures an important fact from the " "context. Restrict the question to the context information provided." "You should generate only question and nothing else." ) dataset_generator = DatasetGenerator.from_documents( documents[:80], question_gen_query=question_gen_query, llm=mistral_small, )
```
/Users/ravithejad/Desktop/llamaindex/lib/python3.9/site-packages/llama_index/core/evaluation/dataset_generation.py:215: DeprecationWarning: Call to deprecated class DatasetGenerator. (Deprecated in favor of `RagDatasetGenerator` which should be used instead.)
  return cls(

```

We will generate 40 training and 40 evaluation questions
In [ ]:
Copied!
```
# Note: This might take sometime.
questions = dataset_generator.generate_questions_from_nodes(num=40)
print("Generated ", len(questions), " questions")

```

# Note: This might take sometime. questions = dataset_generator.generate_questions_from_nodes(num=40) print("Generated ", len(questions), " questions")
```
Generated  40  questions

```

```
/Users/ravithejad/Desktop/llamaindex/lib/python3.9/site-packages/llama_index/core/evaluation/dataset_generation.py:312: DeprecationWarning: Call to deprecated class QueryResponseDataset. (Deprecated in favor of `LabelledRagDataset` which should be used instead.)
  return QueryResponseDataset(queries=queries, responses=responses_dict)

```

In [ ]:
Copied!
```
questions[10:15]

```

questions[10:15]
Out[ ]:
```
['What is the estimated relative human dependence on marine ecosystems for coastal protection, nutrition, fisheries economic benefits, and overall, as depicted in Figure 3.1?',
 'What are the limitations of the overall index mentioned in the context, and how were values for reference regions computed?',
 'What are the primary non-climate drivers that alter marine ecosystems and their services, as mentioned in the context?',
 'What are the main challenges in detecting and attributing climate impacts on marine-dependent human systems, according to the provided context?',
 'What new insights have been gained from experimental evidence about evolutionary adaptation, particularly in relation to eukaryotic organisms and their limited adaptation options to climate change, as mentioned in Section 3.3.4 of the IPCC AR6 WGII Chapter 03?']
```

In [ ]:
Copied!
```
with open("train_questions.txt", "w") as f:
    for question in questions:
        f.write(question + "\n")

```

with open("train_questions.txt", "w") as f: for question in questions: f.write(question + "\n")
Now, lets generate questions on a completely different set of documents, in order to create our eval dataset.
In [ ]:
Copied!
```
dataset_generator = DatasetGenerator.from_documents(
    documents[80:],
    question_gen_query=question_gen_query,
    llm=mistral_small,
)

```

dataset_generator = DatasetGenerator.from_documents( documents[80:], question_gen_query=question_gen_query, llm=mistral_small, )
```
/Users/ravithejad/Desktop/llamaindex/lib/python3.9/site-packages/llama_index/core/evaluation/dataset_generation.py:215: DeprecationWarning: Call to deprecated class DatasetGenerator. (Deprecated in favor of `RagDatasetGenerator` which should be used instead.)
  return cls(

```

In [ ]:
Copied!
```
# Note: This might take sometime.
questions = dataset_generator.generate_questions_from_nodes(num=40)
print("Generated ", len(questions), " questions")

```

# Note: This might take sometime. questions = dataset_generator.generate_questions_from_nodes(num=40) print("Generated ", len(questions), " questions")
```
Generated  40  questions

```

```
/Users/ravithejad/Desktop/llamaindex/lib/python3.9/site-packages/llama_index/core/evaluation/dataset_generation.py:312: DeprecationWarning: Call to deprecated class QueryResponseDataset. (Deprecated in favor of `LabelledRagDataset` which should be used instead.)
  return QueryResponseDataset(queries=queries, responses=responses_dict)

```

In [ ]:
Copied!
```
with open("eval_questions.txt", "w") as f:
    for question in questions:
        f.write(question + "\n")

```

with open("eval_questions.txt", "w") as f: for question in questions: f.write(question + "\n")
## Initial Eval with `open-mistral-7b` Query Engine¶
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
from llama_index.embeddings.mistralai import MistralAIEmbedding

# limit the context window to 2048 tokens so that refine is used
from llama_index.core import Settings

Settings.context_window = 2048
Settings.llm = open_mistral
Settings.embed_model = MistralAIEmbedding()

index = VectorStoreIndex.from_documents(
    documents,
)

query_engine = index.as_query_engine(similarity_top_k=2)

```

from llama_index.core import VectorStoreIndex from llama_index.embeddings.mistralai import MistralAIEmbedding # limit the context window to 2048 tokens so that refine is used from llama_index.core import Settings Settings.context_window = 2048 Settings.llm = open_mistral Settings.embed_model = MistralAIEmbedding() index = VectorStoreIndex.from_documents( documents, ) query_engine = index.as_query_engine(similarity_top_k=2)
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
# We will use OpenAI LLM for evaluation using RAGAS

os.environ["OPENAI_API_KEY"] = "<YOUR OPENAI API KEY>"

```

# We will use OpenAI LLM for evaluation using RAGAS os.environ["OPENAI_API_KEY"] = ""
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

```

from datasets import Dataset from ragas import evaluate from ragas.metrics import answer_relevancy, faithfulness ds = Dataset.from_dict( { "question": questions, "answer": answers, "contexts": contexts, } ) result = evaluate(ds, [answer_relevancy, faithfulness])
```
Evaluating: 100%|██████████| 80/80 [01:12<00:00,  1.10it/s]

```

Let's check the results before finetuning.
In [ ]:
Copied!
```
print(result)

```

print(result)
```
{'answer_relevancy': 0.8151, 'faithfulness': 0.8360}

```

##  `mistral-large-latest` to Collect Training Data¶
Here, we use `mistral-large-latest` to collect data that we want `open-mistral-7b` to finetune on.
In [ ]:
Copied!
```
from llama_index.llms.mistralai import MistralAI
from llama_index.finetuning.callbacks import MistralAIFineTuningHandler
from llama_index.core.callbacks import CallbackManager

finetuning_handler = MistralAIFineTuningHandler()
callback_manager = CallbackManager([finetuning_handler])

llm = MistralAI(model="mistral-large-latest", temperature=0.1)
llm.callback_manager = callback_manager

```

from llama_index.llms.mistralai import MistralAI from llama_index.finetuning.callbacks import MistralAIFineTuningHandler from llama_index.core.callbacks import CallbackManager finetuning_handler = MistralAIFineTuningHandler() callback_manager = CallbackManager([finetuning_handler]) llm = MistralAI(model="mistral-large-latest", temperature=0.1) llm.callback_manager = callback_manager
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

Settings.embed_model = MistralAIEmbedding()
Settings.llm = llm

index = VectorStoreIndex.from_documents(
    documents,
)

query_engine = index.as_query_engine(similarity_top_k=2)

```

from llama_index.core import VectorStoreIndex Settings.embed_model = MistralAIEmbedding() Settings.llm = llm index = VectorStoreIndex.from_documents( documents, ) query_engine = index.as_query_engine(similarity_top_k=2)
```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
from tqdm import tqdm

contexts = []
answers = []

for question in tqdm(questions, desc="Processing questions"):
    response = query_engine.query(question)
    contexts.append(
        "\n".join([x.node.get_content() for x in response.source_nodes])
    )
    answers.append(str(response))

```

from tqdm import tqdm contexts = [] answers = [] for question in tqdm(questions, desc="Processing questions"): response = query_engine.query(question) contexts.append( "\n".join([x.node.get_content() for x in response.source_nodes]) ) answers.append(str(response))
```
Processing questions:   0%|          | 0/40 [00:00<?, ?it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:   2%|▎         | 1/40 [00:02<01:43,  2.66s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:   5%|▌         | 2/40 [00:13<04:38,  7.34s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:   8%|▊         | 3/40 [00:19<04:08,  6.71s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  10%|█         | 4/40 [00:24<03:35,  5.98s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  12%|█▎        | 5/40 [00:28<03:04,  5.26s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  15%|█▌        | 6/40 [00:33<02:55,  5.17s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  18%|█▊        | 7/40 [00:42<03:35,  6.52s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  20%|██        | 8/40 [00:45<02:50,  5.32s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  22%|██▎       | 9/40 [00:51<02:58,  5.75s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  25%|██▌       | 10/40 [00:55<02:29,  4.99s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  28%|██▊       | 11/40 [01:00<02:24,  5.00s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  30%|███       | 12/40 [01:03<02:08,  4.59s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  32%|███▎      | 13/40 [01:06<01:45,  3.90s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  35%|███▌      | 14/40 [01:15<02:21,  5.44s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  38%|███▊      | 15/40 [01:18<02:00,  4.82s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  40%|████      | 16/40 [01:29<02:42,  6.76s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  42%|████▎     | 17/40 [01:37<02:45,  7.20s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  45%|████▌     | 18/40 [01:42<02:18,  6.31s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  48%|████▊     | 19/40 [01:47<02:03,  5.89s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  50%|█████     | 20/40 [01:48<01:33,  4.66s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  52%|█████▎    | 21/40 [01:53<01:25,  4.50s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  55%|█████▌    | 22/40 [01:55<01:11,  3.98s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  57%|█████▊    | 23/40 [01:58<00:59,  3.47s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  60%|██████    | 24/40 [02:00<00:48,  3.03s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  62%|██████▎   | 25/40 [02:04<00:50,  3.38s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  65%|██████▌   | 26/40 [02:06<00:42,  3.03s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  68%|██████▊   | 27/40 [02:22<01:29,  6.89s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  70%|███████   | 28/40 [02:25<01:08,  5.73s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  72%|███████▎  | 29/40 [02:32<01:08,  6.24s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  75%|███████▌  | 30/40 [02:34<00:49,  4.99s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  78%|███████▊  | 31/40 [02:37<00:37,  4.19s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  80%|████████  | 32/40 [02:42<00:36,  4.54s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  82%|████████▎ | 33/40 [02:46<00:30,  4.39s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  85%|████████▌ | 34/40 [02:48<00:22,  3.67s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  88%|████████▊ | 35/40 [02:53<00:20,  4.01s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  90%|█████████ | 36/40 [02:58<00:17,  4.28s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  92%|█████████▎| 37/40 [03:13<00:22,  7.45s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  95%|█████████▌| 38/40 [03:16<00:12,  6.20s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions:  98%|█████████▊| 39/40 [03:18<00:05,  5.06s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing questions: 100%|██████████| 40/40 [03:30<00:00,  5.25s/it]

```

In [ ]:
Copied!
```
import json
from typing import List


def convert_data_jsonl_format(
    questions: List[str],
    contexts: List[str],
    answers: List[str],
    output_file: str,
) -> None:
    with open(output_file, "w") as outfile:
        for context, question, answer in zip(contexts, questions, answers):
            message_dict = {
                "messages": [
                    {
                        "role": "assistant",
                        "content": "You are a helpful assistant to answer user queries based on provided context.",
                    },
                    {
                        "role": "user",
                        "content": f"context: {context} \n\n question: {question}",
                    },
                    {"role": "assistant", "content": answer},
                ]
            }
            # Write the JSON object in a single line
            json.dump(message_dict, outfile)
            # Add a newline character after each JSON object
            outfile.write("\n")

```

import json from typing import List def convert_data_jsonl_format( questions: List[str], contexts: List[str], answers: List[str], output_file: str, ) -> None: with open(output_file, "w") as outfile: for context, question, answer in zip(contexts, questions, answers): message_dict = { "messages": [ { "role": "assistant", "content": "You are a helpful assistant to answer user queries based on provided context.", }, { "role": "user", "content": f"context: {context} \n\n question: {question}", }, {"role": "assistant", "content": answer}, ] } # Write the JSON object in a single line json.dump(message_dict, outfile) # Add a newline character after each JSON object outfile.write("\n")
In [ ]:
Copied!
```
convert_data_jsonl_format(questions, contexts, answers, "training.jsonl")

```

convert_data_jsonl_format(questions, contexts, answers, "training.jsonl")
## Create `MistralAIFinetuneEngine`¶
We create an `MistralAIFinetuneEngine`: the finetune engine will take care of launching a finetuning job, and returning an LLM model that you can directly plugin to the rest of LlamaIndex workflows.
We use the default constructor, but we can also directly pass in our finetuning_handler into this engine with the `from_finetuning_handler` class method.
In [ ]:
Copied!
```
from llama_index.llms.mistralai import MistralAI
from llama_index.finetuning.callbacks import MistralAIFineTuningHandler
from llama_index.core.callbacks import CallbackManager
from llama_index.finetuning.mistralai import MistralAIFinetuneEngine

# Wandb for monitorning the training logs
wandb_integration_dict = {
    "project": "mistralai",
    "run_name": "finetuning",
    "api_key": "<api_key>",
}

finetuning_engine = MistralAIFinetuneEngine(
    base_model="open-mistral-7b",
    training_path="training.jsonl",
    # validation_path="<validation file>", # validation file is optional
    verbose=True,
    training_steps=5,
    learning_rate=0.0001,
    wandb_integration_dict=wandb_integration_dict,
)

```

from llama_index.llms.mistralai import MistralAI from llama_index.finetuning.callbacks import MistralAIFineTuningHandler from llama_index.core.callbacks import CallbackManager from llama_index.finetuning.mistralai import MistralAIFinetuneEngine # Wandb for monitorning the training logs wandb_integration_dict = { "project": "mistralai", "run_name": "finetuning", "api_key": "", } finetuning_engine = MistralAIFinetuneEngine( base_model="open-mistral-7b", training_path="training.jsonl", # validation_path="", # validation file is optional verbose=True, training_steps=5, learning_rate=0.0001, wandb_integration_dict=wandb_integration_dict, )
In [ ]:
Copied!
```
# starts the finetuning of open-mistral-7b

finetuning_engine.finetune()

```

# starts the finetuning of open-mistral-7b finetuning_engine.finetune()
In [ ]:
Copied!
```
# This will show the current status of the job - 'RUNNING'
finetuning_engine.get_current_job()

```

# This will show the current status of the job - 'RUNNING' finetuning_engine.get_current_job()
```
INFO:httpx:HTTP Request: GET https://api.mistral.ai/v1/fine_tuning/jobs/19f5943a-3000-4568-b227-e45c36ac15f1 "HTTP/1.1 200 OK"
HTTP Request: GET https://api.mistral.ai/v1/fine_tuning/jobs/19f5943a-3000-4568-b227-e45c36ac15f1 "HTTP/1.1 200 OK"

```

Out[ ]:
```
DetailedJob(id='19f5943a-3000-4568-b227-e45c36ac15f1', hyperparameters=TrainingParameters(training_steps=5, learning_rate=0.0001), fine_tuned_model=None, model='open-mistral-7b', status='RUNNING', job_type='FT', created_at=1718613228, modified_at=1718613229, training_files=['07270085-65e6-441e-b99d-ef6f75dd5a30'], validation_files=[], object='job', integrations=[WandbIntegration(type='wandb', project='mistralai', name=None, run_name='finetuning')], events=[Event(name='status-updated', data={'status': 'RUNNING'}, created_at=1718613229), Event(name='status-updated', data={'status': 'QUEUED'}, created_at=1718613228)], checkpoints=[], estimated_start_time=None)
```

In [ ]:
Copied!
```
# This will show the current status of the job - 'SUCCESS'
finetuning_engine.get_current_job()

```

# This will show the current status of the job - 'SUCCESS' finetuning_engine.get_current_job()
```
INFO:httpx:HTTP Request: GET https://api.mistral.ai/v1/fine_tuning/jobs/19f5943a-3000-4568-b227-e45c36ac15f1 "HTTP/1.1 200 OK"
HTTP Request: GET https://api.mistral.ai/v1/fine_tuning/jobs/19f5943a-3000-4568-b227-e45c36ac15f1 "HTTP/1.1 200 OK"

```

Out[ ]:
```
DetailedJob(id='19f5943a-3000-4568-b227-e45c36ac15f1', hyperparameters=TrainingParameters(training_steps=5, learning_rate=0.0001), fine_tuned_model='ft:open-mistral-7b:35c6fa92:20240617:19f5943a', model='open-mistral-7b', status='SUCCESS', job_type='FT', created_at=1718613228, modified_at=1718613306, training_files=['07270085-65e6-441e-b99d-ef6f75dd5a30'], validation_files=[], object='job', integrations=[WandbIntegration(type='wandb', project='mistralai', name=None, run_name='finetuning')], events=[Event(name='status-updated', data={'status': 'SUCCESS'}, created_at=1718613306), Event(name='status-updated', data={'status': 'RUNNING'}, created_at=1718613229), Event(name='status-updated', data={'status': 'QUEUED'}, created_at=1718613228)], checkpoints=[], estimated_start_time=None)
```

In [ ]:
Copied!
```
ft_llm = finetuning_engine.get_finetuned_model(temperature=0.1)

```

ft_llm = finetuning_engine.get_finetuned_model(temperature=0.1)
```
INFO:httpx:HTTP Request: GET https://api.mistral.ai/v1/fine_tuning/jobs/19f5943a-3000-4568-b227-e45c36ac15f1 "HTTP/1.1 200 OK"
HTTP Request: GET https://api.mistral.ai/v1/fine_tuning/jobs/19f5943a-3000-4568-b227-e45c36ac15f1 "HTTP/1.1 200 OK"
INFO:llama_index.finetuning.mistralai.base:status of the job_id: 19f5943a-3000-4568-b227-e45c36ac15f1 is SUCCESS
status of the job_id: 19f5943a-3000-4568-b227-e45c36ac15f1 is SUCCESS

```

## Evaluation¶
Once the finetuned model is created, the next step is running our fine-tuned model on our eval dataset again to measure any performance increase.
In [ ]:
Copied!
```
from llama_index.core import Settings
from llama_index.llms.mistralai import MistralAI
from llama_index.embeddings.mistralai import MistralAIEmbedding

# Setting up finetuned llm
Settings.llm = ft_llm
Settings.context_window = (
    2048  # limit the context window artifically to test refine process
)
Settings.embed_model = MistralAIEmbedding()

```

from llama_index.core import Settings from llama_index.llms.mistralai import MistralAI from llama_index.embeddings.mistralai import MistralAIEmbedding # Setting up finetuned llm Settings.llm = ft_llm Settings.context_window = ( 2048 # limit the context window artifically to test refine process ) Settings.embed_model = MistralAIEmbedding()
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
```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
contexts = []
answers = []

for question in tqdm(questions, desc="Processing Questions"):
    response = query_engine.query(question)
    contexts.append([x.node.get_content() for x in response.source_nodes])
    answers.append(str(response))

```

contexts = [] answers = [] for question in tqdm(questions, desc="Processing Questions"): response = query_engine.query(question) contexts.append([x.node.get_content() for x in response.source_nodes]) answers.append(str(response))
```
Processing Questions:   0%|          | 0/40 [00:00<?, ?it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:   2%|▎         | 1/40 [00:06<04:16,  6.58s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:   5%|▌         | 2/40 [00:11<03:32,  5.58s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:   8%|▊         | 3/40 [00:14<02:45,  4.48s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  10%|█         | 4/40 [00:19<02:41,  4.48s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  12%|█▎        | 5/40 [00:21<02:16,  3.90s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  15%|█▌        | 6/40 [00:27<02:25,  4.29s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  18%|█▊        | 7/40 [00:29<02:00,  3.66s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  20%|██        | 8/40 [00:31<01:41,  3.16s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  22%|██▎       | 9/40 [00:33<01:25,  2.74s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  25%|██▌       | 10/40 [00:36<01:26,  2.90s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  28%|██▊       | 11/40 [00:38<01:18,  2.71s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  30%|███       | 12/40 [00:40<01:08,  2.44s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  32%|███▎      | 13/40 [00:47<01:42,  3.81s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  35%|███▌      | 14/40 [00:50<01:30,  3.46s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  38%|███▊      | 15/40 [01:01<02:22,  5.71s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  40%|████      | 16/40 [01:06<02:14,  5.59s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  42%|████▎     | 17/40 [01:09<01:49,  4.76s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  45%|████▌     | 18/40 [01:13<01:39,  4.54s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  48%|████▊     | 19/40 [01:16<01:27,  4.15s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  50%|█████     | 20/40 [01:20<01:19,  3.99s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  52%|█████▎    | 21/40 [01:27<01:34,  4.97s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  55%|█████▌    | 22/40 [01:30<01:17,  4.33s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  57%|█████▊    | 23/40 [01:32<01:02,  3.70s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  60%|██████    | 24/40 [01:40<01:18,  4.90s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  62%|██████▎   | 25/40 [01:44<01:12,  4.80s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  65%|██████▌   | 26/40 [01:48<01:02,  4.45s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  68%|██████▊   | 27/40 [01:54<01:02,  4.80s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  70%|███████   | 28/40 [02:03<01:15,  6.28s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  72%|███████▎  | 29/40 [02:06<00:57,  5.21s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  75%|███████▌  | 30/40 [02:09<00:44,  4.47s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  78%|███████▊  | 31/40 [02:11<00:33,  3.77s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  80%|████████  | 32/40 [02:13<00:26,  3.30s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  82%|████████▎ | 33/40 [02:15<00:19,  2.77s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  85%|████████▌ | 34/40 [02:21<00:22,  3.73s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  88%|████████▊ | 35/40 [02:24<00:18,  3.70s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  90%|█████████ | 36/40 [02:29<00:16,  4.02s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  92%|█████████▎| 37/40 [02:36<00:14,  4.83s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  95%|█████████▌| 38/40 [02:38<00:08,  4.12s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions:  98%|█████████▊| 39/40 [02:40<00:03,  3.42s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Processing Questions: 100%|██████████| 40/40 [02:44<00:00,  4.11s/it]

```

In [ ]:
Copied!
```
ds = Dataset.from_dict(
    {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
    }
)

result = evaluate(ds, [answer_relevancy, faithfulness])

```

ds = Dataset.from_dict( { "question": questions, "answer": answers, "contexts": contexts, } ) result = evaluate(ds, [answer_relevancy, faithfulness])
```
Evaluating:   0%|          | 0/80 [00:00<?, ?it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:   1%|▏         | 1/80 [00:05<06:55,  5.26s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:   2%|▎         | 2/80 [00:12<08:11,  6.30s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  11%|█▏        | 9/80 [00:13<01:15,  1.06s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  12%|█▎        | 10/80 [00:15<01:23,  1.20s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  14%|█▍        | 11/80 [00:17<01:33,  1.35s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  18%|█▊        | 14/80 [00:18<00:58,  1.12it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  19%|█▉        | 15/80 [00:19<01:03,  1.03it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  20%|██        | 16/80 [00:20<01:01,  1.03it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  26%|██▋       | 21/80 [00:22<00:32,  1.80it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  28%|██▊       | 22/80 [00:25<00:52,  1.10it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  41%|████▏     | 33/80 [00:27<00:19,  2.43it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  42%|████▎     | 34/80 [00:32<00:36,  1.25it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  49%|████▉     | 39/80 [00:33<00:23,  1.73it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  55%|█████▌    | 44/80 [00:34<00:15,  2.31it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  56%|█████▋    | 45/80 [00:35<00:17,  1.98it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  57%|█████▊    | 46/80 [00:39<00:30,  1.12it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  62%|██████▎   | 50/80 [00:40<00:19,  1.54it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  68%|██████▊   | 54/80 [00:44<00:20,  1.26it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  71%|███████▏  | 57/80 [00:45<00:15,  1.51it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  76%|███████▋  | 61/80 [00:47<00:11,  1.66it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  78%|███████▊  | 62/80 [00:49<00:13,  1.31it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  82%|████████▎ | 66/80 [00:50<00:07,  1.76it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
Evaluating:  88%|████████▊ | 70/80 [00:52<00:05,  1.86it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  89%|████████▉ | 71/80 [00:52<00:04,  1.87it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  90%|█████████ | 72/80 [00:55<00:06,  1.32it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  91%|█████████▏| 73/80 [00:57<00:07,  1.05s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  92%|█████████▎| 74/80 [00:58<00:05,  1.06it/s]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  94%|█████████▍| 75/80 [01:01<00:07,  1.41s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  95%|█████████▌| 76/80 [01:03<00:06,  1.61s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  96%|█████████▋| 77/80 [01:07<00:06,  2.27s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  98%|█████████▊| 78/80 [01:16<00:07,  3.94s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating:  99%|█████████▉| 79/80 [01:17<00:03,  3.07s/it]
```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

```
Evaluating: 100%|██████████| 80/80 [01:19<00:00,  1.01it/s]

```

Let's check the results with finetuned model
In [ ]:
Copied!
```
print(result)

```

print(result)
```
{'answer_relevancy': 0.8016, 'faithfulness': 0.8924}

```

## Observation:¶
`open-mistral-7b` : 'answer_relevancy': **0.8151** , 'faithfulness': **0.8360**
`open-mistral-7b-finetuned` : 'answer_relevancy': **0.8016** , 'faithfulness': **0.8924**
As you can see there is an increase in faithfulness score and small drop in answer relevancy.
## Exploring Differences¶
Let's quickly compare the differences in responses, to demonstrate that fine tuning did indeed change something.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents)
```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"

```

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
print(questions[20])

```

print(questions[20])
```
What are some examples of economic losses due to disruptions in ocean and coastal ecosystem services partly attributable to climate change, as mentioned in the context?

```

### Original `open-mistral-7b  `¶
In [ ]:
Copied!
```
from llama_index.core.response.notebook_utils import display_response

```

from llama_index.core.response.notebook_utils import display_response
In [ ]:
Copied!
```
query_engine = index.as_query_engine(llm=open_mistral)

response = query_engine.query(questions[20])

display_response(response)

```

query_engine = index.as_query_engine(llm=open_mistral) response = query_engine.query(questions[20]) display_response(response)
```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

**`Final Response:`**Economic losses due to disruptions in ocean and coastal ecosystem services partly attributable to climate change, as mentioned in the context, include:
  1. The estimated loss of 800 million USD in the farmed-salmon industry in Chile due to a climate-driven harmful algal bloom.
  2. The closure of the Dungeness crab and razor clam fishery in the USA due to a climate-driven algal bloom, which harmed 84% of surveyed residents from 16 California coastal communities.
  3. Substantial economic losses for fisheries resulting from recent climate-driven harmful algal blooms and marine pathogen outbreaks in Asia, North America, and South America.
  4. Declines in tourism and real estate values, associated with climate-driven harmful algal blooms, in the USA, France, and England.


### Fine-Tuned `open-mistral-7b`¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(llm=ft_llm)

response = query_engine.query(questions[20])

display_response(response)

```

query_engine = index.as_query_engine(llm=ft_llm) response = query_engine.query(questions[20]) display_response(response)
```
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.mistral.ai/v1/chat/completions "HTTP/1.1 200 OK"

```

**`Final Response:`**Economic losses due to disruptions in ocean and coastal ecosystem services partly attributable to climate change have been recorded in various industries and regions. For instance, substantial economic losses for fisheries resulting from climate-driven harmful algal blooms and marine pathogen outbreaks have been reported in Asia, North America, and South America. A notable example is the 2016 event in Chile, which caused an estimated loss of 800 million USD in the farmed-salmon industry and led to regional government protests. Similarly, the recent closure of the Dungeness crab and razor clam fishery in the USA due to a climate-driven algal bloom harmed 84% of surveyed residents from 16 California coastal communities.
In addition, declines in tourism and real estate values, associated with climate-driven harmful algal blooms, have been recorded in the USA, France, and England. These disruptions can have significant economic impacts on coastal communities, particularly those that heavily rely on tourism for income or have a strong cultural identity linked to the ocean.
Moreover, changes in the abundance or quality of goods from the ocean, such as non-food products like dietary supplements, food preservatives, pharmaceuticals, biofuels, sponges, cosmetic products, jewellery coral, cultured pearls, and aquarium species, will also be affected by climate change. These changes can lead to economic losses for industries that rely on these resources.
Finally, the vulnerability of communities to losses in marine ecosystem services varies within and among communities. However, climate-change impacts exacerbate existing inequalities already experienced by some communities, including Indigenous Peoples, Pacific Island countries and territories, and marginalized peoples, such as migrants and women in fisheries and mariculture. These inequities increase the risk to their fundamental human rights by disrupting livelihoods and food security, while leading to loss of social, economic, and cultural rights.
As we can see, the fine-tuned model provides a more thorough response! This lines up with the increased faithfullness score from ragas, since the answer is more representative of the retrieved context.
## Conclusion¶
So, in conclusion, finetuning with only ~40 questions actually helped improve our eval scores!
**answer_relevancy: 0.0.8151 - > 0.8016**
The answer relevancy dips slightly but it's very small.
**faithfulness: 0.8360 - > 0.8924**
The faithfulness appears to have been improved! This mains the anwers given better fuffil the original question that was asked.
