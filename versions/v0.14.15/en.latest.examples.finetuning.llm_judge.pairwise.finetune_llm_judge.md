# Knowledge Distillation For Fine-Tuning A GPT-3.5 Judge (Pairwise)¶
There has been recent research that demonstrated GPT-4's ability to closely align to human judges when evaluating LLM generated texts (e.g., see [1], [2]). In this notebook, we demonstrate how to use the `llama_index` library to distill knowledge from GPT-4 to GPT-3.5 so that a smaller GPT-3.5 becomes closer to GPT-4 performance; and by proxy, closer to human judges.
To do so, we will perform the following high level steps:
  1. Generate datasets: `train_dataset` and `test_dataset`
  2. Perform knowledge distillation (using `train_dataset`)
  3. Evaluate the distilled model on `test_dataset`


In [ ]:
Copied!
```
%pip install llama-index-readers-wikipedia
%pip install llama-index-finetuning
%pip install llama-index-llms-openai
%pip install llama-index-llms-mistralai
%pip install llama-index-llms-huggingface-api

```

%pip install llama-index-readers-wikipedia %pip install llama-index-finetuning %pip install llama-index-llms-openai %pip install llama-index-llms-mistralai %pip install llama-index-llms-huggingface-api
In [ ]:
Copied!
```
# NOTE: this notebook makes several API calls to generate text with OpenAI GPT
# models as well as models hosted on HuggingFace. If you prefer not to wait for
# these generations, then the data for this notebook can be obtained with the
# `wget` command provided below.

# !wget "https://www.dropbox.com/scl/fo/m7skpjdbpb0g3p76y6epe/h?rlkey=omh2ysgh9qqqztf81qvjlivu2&dl=1" -O pairwise.zip

```

# NOTE: this notebook makes several API calls to generate text with OpenAI GPT # models as well as models hosted on HuggingFace. If you prefer not to wait for # these generations, then the data for this notebook can be obtained with the # `wget` command provided below. # !wget "https://www.dropbox.com/scl/fo/m7skpjdbpb0g3p76y6epe/h?rlkey=omh2ysgh9qqqztf81qvjlivu2&dl=1" -O pairwise.zip
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
In [ ]:
Copied!
```
import pandas as pd


# define jupyter display function
def display_eval_df(question, source, answer_a, answer_b, result) -> None:
    """Pretty print question/answer + gpt-4 judgement dataset."""
    eval_df = pd.DataFrame(
        {
            "Question": question,
            "Source": source,
            "Model A": answer_a["model"],
            "Answer A": answer_a["text"],
            "Model B": answer_b["model"],
            "Answer B": answer_b["text"],
            "Score": result.score,
            "Judgement": result.feedback,
        },
        index=[0],
    )
    eval_df = eval_df.style.set_properties(
        **{
            "inline-size": "300px",
            "overflow-wrap": "break-word",
        },
        subset=["Answer A", "Answer B"]
    )
    display(eval_df)

```

import pandas as pd # define jupyter display function def display_eval_df(question, source, answer_a, answer_b, result) -> None: """Pretty print question/answer + gpt-4 judgement dataset.""" eval_df = pd.DataFrame( { "Question": question, "Source": source, "Model A": answer_a["model"], "Answer A": answer_a["text"], "Model B": answer_b["model"], "Answer B": answer_b["text"], "Score": result.score, "Judgement": result.feedback, }, index=[0], ) eval_df = eval_df.style.set_properties( **{ "inline-size": "300px", "overflow-wrap": "break-word", }, subset=["Answer A", "Answer B"] ) display(eval_df)
## Step 1 Generate datasets: `train_dataset` and `test_dataset`¶
For our dataset on which we will generate questions and prompt various LLMs to answer, we're going to use the `WikipediaReader` to read "History of " for several cities. We're going to split up our cities into two lists: one to be used for `train_dataset` and the other for `test_dataset`.
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

train_cities = [
    "San Francisco",
    "Toronto",
    "New York City",
    "Vancouver",
    "Montreal",
    "Boston",
]

test_cities = [
    "Tokyo",
    "Singapore",
    "Paris",
]

train_documents = WikipediaReader().load_data(
    pages=[f"History of {x}" for x in train_cities]
)
test_documents = WikipediaReader().load_data(
    pages=[f"History of {x}" for x in test_cities]
)

```

# wikipedia pages from llama_index.readers.wikipedia import WikipediaReader train_cities = [ "San Francisco", "Toronto", "New York City", "Vancouver", "Montreal", "Boston", ] test_cities = [ "Tokyo", "Singapore", "Paris", ] train_documents = WikipediaReader().load_data( pages=[f"History of {x}" for x in train_cities] ) test_documents = WikipediaReader().load_data( pages=[f"History of {x}" for x in test_cities] )
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
With all that out of the way, let's spring into action. First, we will download the reference pdf document and create the set of questions against it.
In [ ]:
Copied!
```
# generate questions against chunks
from llama_index.core.evaluation import DatasetGenerator
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)


# instantiate DatasetGenerator's for train and test
train_dataset_generator = DatasetGenerator.from_documents(
    train_documents,
    question_gen_query=QUESTION_GEN_PROMPT,
    llm=llm,
    show_progress=True,
    num_questions_per_chunk=25,
)

test_dataset_generator = DatasetGenerator.from_documents(
    test_documents,
    question_gen_query=QUESTION_GEN_PROMPT,
    llm=llm,
    show_progress=True,
    num_questions_per_chunk=25,
)

```

# generate questions against chunks from llama_index.core.evaluation import DatasetGenerator from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3) # instantiate DatasetGenerator's for train and test train_dataset_generator = DatasetGenerator.from_documents( train_documents, question_gen_query=QUESTION_GEN_PROMPT, llm=llm, show_progress=True, num_questions_per_chunk=25, ) test_dataset_generator = DatasetGenerator.from_documents( test_documents, question_gen_query=QUESTION_GEN_PROMPT, llm=llm, show_progress=True, num_questions_per_chunk=25, )
In [ ]:
Copied!
```
# use DatasetGenerator to create questions from nodes
train_questions = train_dataset_generator.generate_questions_from_nodes(
    num=200
)

```

# use DatasetGenerator to create questions from nodes train_questions = train_dataset_generator.generate_questions_from_nodes( num=200 )
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 75/75 [00:02<00:00, 36.34it/s]

```

In [ ]:
Copied!
```
test_questions = test_dataset_generator.generate_questions_from_nodes(num=150)

```

test_questions = test_dataset_generator.generate_questions_from_nodes(num=150)
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 64/64 [00:02<00:00, 29.98it/s]

```

In [ ]:
Copied!
```
len(train_questions), len(test_questions)

```

len(train_questions), len(test_questions)
Out[ ]:
```
(75, 64)
```

In [ ]:
Copied!
```
# let's take a look at a few of these
train_questions[:3]

```

# let's take a look at a few of these train_questions[:3]
Out[ ]:
```
['What event in 1906 caused significant damage to San Francisco but was followed by a quick rebuild?',
 'What was the name of the first significant homestead established outside the immediate vicinity of Mission Dolores in San Francisco?',
 "What event in 1855 led to the establishment of San Francisco's first county hospital and the development of California's system of county hospitals for the poor?"]
```

In [ ]:
Copied!
```
test_questions[:3]

```

test_questions[:3]
Out[ ]:
```
['Question: What was the name of the oldest Buddhist temple in Tokyo, founded in 628?',
 'What event marked the end of the samurai system and feudal class divisions in Tokyo?',
 'Question: What role did the Tokyo Imperial University play in the Meiji Era?']
```

#### Generate Answers To The Questions¶
The next step is to generate answers using LLMs. Just a reminder, that the point is to judge these generated answers. So later on, we will use GPT models to judge these answers.
But for the generation of the answers to the questions, we will use two other LLMs, namely: Llama-2 and Mistral. In order to do this, we first a create a vector store for our documents and an associated retriever, which both of the LLM answer-generators will use.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import VectorIndexRetriever

# Create vector index
train_index = VectorStoreIndex.from_documents(documents=train_documents)

# Create the retriver on this index
train_retriever = VectorIndexRetriever(
    index=train_index,
    similarity_top_k=2,
)

# Create vector index for test to be used later
test_index = VectorStoreIndex.from_documents(documents=test_documents)

# Create the retriver for test to be used later
test_retriever = VectorIndexRetriever(
    index=test_index,
    similarity_top_k=2,
)

```

from llama_index.core import VectorStoreIndex from llama_index.core.retrievers import VectorIndexRetriever # Create vector index train_index = VectorStoreIndex.from_documents(documents=train_documents) # Create the retriver on this index train_retriever = VectorIndexRetriever( index=train_index, similarity_top_k=2, ) # Create vector index for test to be used later test_index = VectorStoreIndex.from_documents(documents=test_documents) # Create the retriver for test to be used later test_retriever = VectorIndexRetriever( index=test_index, similarity_top_k=2, )
From here we will build `RetrieverQueryEngine`'s that will take in our queries (i.e. questions) for processing. Note that we use `HuggingFaceInferenceAPI` for our LLM answer-generators, and that Llama-2 requires permissions. If you haven't yet gain accessed to these models, then feel free to swap out Llama-2 with another model of your choosing.
In [ ]:
Copied!
```
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI


def create_query_engine(
    hf_name: str, retriever: VectorIndexRetriever, hf_llm_generators: dict
) -> RetrieverQueryEngine:
    """Create a RetrieverQueryEngine using the HuggingFaceInferenceAPI LLM"""
    if hf_name not in hf_llm_generators:
        raise KeyError("model not listed in hf_llm_generators")
    llm = HuggingFaceInferenceAPI(
        model_name=hf_llm_generators[hf_name],
        context_window=2048,  # to use refine
        token=HUGGING_FACE_TOKEN,
    )
    return RetrieverQueryEngine.from_args(retriever=retriever, llm=llm)

```

from llama_index.core.query_engine import RetrieverQueryEngine from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI def create_query_engine( hf_name: str, retriever: VectorIndexRetriever, hf_llm_generators: dict ) -> RetrieverQueryEngine: """Create a RetrieverQueryEngine using the HuggingFaceInferenceAPI LLM""" if hf_name not in hf_llm_generators: raise KeyError("model not listed in hf_llm_generators") llm = HuggingFaceInferenceAPI( model_name=hf_llm_generators[hf_name], context_window=2048, # to use refine token=HUGGING_FACE_TOKEN, ) return RetrieverQueryEngine.from_args(retriever=retriever, llm=llm)
In [ ]:
Copied!
```
# define our llm-generators (query_engines)
hf_llm_generators = {
    "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.1",
    "llama2-7b-chat": "meta-llama/Llama-2-7b-chat-hf",
}

train_query_engines = {
    mdl: create_query_engine(mdl, train_retriever, hf_llm_generators)
    for mdl in hf_llm_generators.keys()
}

test_query_engines = {
    mdl: create_query_engine(mdl, test_retriever, hf_llm_generators)
    for mdl in hf_llm_generators.keys()
}

```

# define our llm-generators (query_engines) hf_llm_generators = { "mistral-7b-instruct": "mistralai/Mistral-7B-Instruct-v0.1", "llama2-7b-chat": "meta-llama/Llama-2-7b-chat-hf", } train_query_engines = { mdl: create_query_engine(mdl, train_retriever, hf_llm_generators) for mdl in hf_llm_generators.keys() } test_query_engines = { mdl: create_query_engine(mdl, test_retriever, hf_llm_generators) for mdl in hf_llm_generators.keys() }
We're ready to now to produce the answers from the various LLMs. We'll do this now for the `train_dataset` and hold off on doing this for `test_dataset` until the time comes for us to use it.
NOTE: this will take some time to generate. If you'd rather not wait, you have the option of loading the `train_qa.jsonl` that contains Llama-2 and Mistral answers per question.
In [ ]:
Copied!
```
import tqdm
import random

train_dataset = []
for q in tqdm.tqdm(train_questions):
    # randomly select two LLMs to generate answers to this q
    model_versus = random.sample(list(train_query_engines.items()), 2)

    # data for this q
    data_entry = {"question": q}
    responses = []
    source = None

    # generate answers
    for name, engine in model_versus:
        response = engine.query(q)
        response_struct = {}
        response_struct["model"] = name
        response_struct["text"] = str(response)
        if source is not None:
            assert source == response.source_nodes[0].node.text[:1000] + "..."
        else:
            source = response.source_nodes[0].node.text[:1000] + "..."
        responses.append(response_struct)

    data_entry["answers"] = responses
    data_entry["source"] = source
    train_dataset.append(data_entry)

```

import tqdm import random train_dataset = [] for q in tqdm.tqdm(train_questions): # randomly select two LLMs to generate answers to this q model_versus = random.sample(list(train_query_engines.items()), 2) # data for this q data_entry = {"question": q} responses = [] source = None # generate answers for name, engine in model_versus: response = engine.query(q) response_struct = {} response_struct["model"] = name response_struct["text"] = str(response) if source is not None: assert source == response.source_nodes[0].node.text[:1000] + "..." else: source = response.source_nodes[0].node.text[:1000] + "..." responses.append(response_struct) data_entry["answers"] = responses data_entry["source"] = source train_dataset.append(data_entry)
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 75/75 [07:40<00:00,  6.14s/it]

```

### Get GPT-4 Evaluations On The Mistral and LLama-2 Answers¶
As mentioned a couple of times before, the point of this guide is fine-tune an LLM judge from a GPT-4 judge. So, in order to complete our `train_dataset` we now need to instantiate our GPT-4 judge and have it evaluate the answers that were provided by the other LLMs: Llama-2 and Mistral. To do this, we will use the `PairwiseComparisonEvaluator` class. What this judge will do then is it will compare the two answers and provide a verdict as to whether Llama-2's answer is better, Mistral's answer is better, or if it's a tie.
There is a bit of added nuance here since with pairwise evaluations, we have to be mindful of the potential for "position-bias". This is when the judge favours the first answer that was presented to it (within the prompt/context). To account for this position-bias, we invoke the GPT-4 judge to perform to evaluations per sample, where in the second evaluation, we switch the order of presentation of the two answers (i.e., first evaluation: Llama-2 then Mistral, second evaluation: Mistral then Llama-2).
Finally, we also use the `OpenAIFineTuningHandler` which will collect all the chat histories that we will eventually need to fine-tune GPT-3.5.
NOTE: this will take some time to generate the judgements. Again, you have the option to load the `train_qa.jsonl` as `train_dataset`. Moreover, we also stored the JSONL files that we passed to OpenAI to fine-tune GPT-3.5.
In [ ]:
Copied!
```
# instantiate the gpt-4 judge
from llama_index.llms.openai import OpenAI
from llama_index.finetuning.callbacks import OpenAIFineTuningHandler
from llama_index.core.callbacks import CallbackManager
from llama_index.core.evaluation import PairwiseComparisonEvaluator
from llama_index.core import Settings

# NOTE: this finetuning_handler will collect 2x chat_histories for
# each query: one for original, and another for flipped
main_finetuning_handler = OpenAIFineTuningHandler()
callback_manager = CallbackManager([main_finetuning_handler])
Settings.callback_manager = callback_manager

llm_4 = OpenAI(temperature=0, model="gpt-4", callback_manager=callback_manager)

gpt4_judge = PairwiseComparisonEvaluator(llm=llm_4)

```

# instantiate the gpt-4 judge from llama_index.llms.openai import OpenAI from llama_index.finetuning.callbacks import OpenAIFineTuningHandler from llama_index.core.callbacks import CallbackManager from llama_index.core.evaluation import PairwiseComparisonEvaluator from llama_index.core import Settings # NOTE: this finetuning_handler will collect 2x chat_histories for # each query: one for original, and another for flipped main_finetuning_handler = OpenAIFineTuningHandler() callback_manager = CallbackManager([main_finetuning_handler]) Settings.callback_manager = callback_manager llm_4 = OpenAI(temperature=0, model="gpt-4", callback_manager=callback_manager) gpt4_judge = PairwiseComparisonEvaluator(llm=llm_4)
In [ ]:
Copied!
```
for data_entry in tqdm.tqdm(train_dataset):
    final_eval_result = await gpt4_judge.aevaluate(
        query=data_entry["question"],
        response=data_entry["answers"][0]["text"],
        second_response=data_entry["answers"][1]["text"],
        reference=data_entry["source"],
    )

    # save final result
    judgement = {}
    judgement["llm"] = "gpt_4"
    judgement["score"] = final_eval_result.score
    judgement["text"] = final_eval_result.response
    judgement["source"] = final_eval_result.pairwise_source
    data_entry["evaluations"] = [judgement]

```

for data_entry in tqdm.tqdm(train_dataset): final_eval_result = await gpt4_judge.aevaluate( query=data_entry["question"], response=data_entry["answers"][0]["text"], second_response=data_entry["answers"][1]["text"], reference=data_entry["source"], ) # save final result judgement = {} judgement["llm"] = "gpt_4" judgement["score"] = final_eval_result.score judgement["text"] = final_eval_result.response judgement["source"] = final_eval_result.pairwise_source data_entry["evaluations"] = [judgement]
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 75/75 [48:04<00:00, 38.46s/it]

```

Let's see how one of these GPT-4 evaluations looks like.
In [ ]:
Copied!
```
# let's see the last one
display_eval_df(
    question=data_entry["question"],
    source=data_entry["source"],
    answer_a=data_entry["answers"][0],
    answer_b=data_entry["answers"][1],
    result=final_eval_result,
)

```

# let's see the last one display_eval_df( question=data_entry["question"], source=data_entry["source"], answer_a=data_entry["answers"][0], answer_b=data_entry["answers"][1], result=final_eval_result, )
| Question | Source | Model A | Answer A | Model B | Answer B | Score | Judgement  
---|---|---|---|---|---|---|---|---  
0 | What resources are available in Boston for studying and preserving historical artifacts and remains? | In 1963, Boston Mayor John F. Collins and Boston Redevelopment Authority (BRA) executive Edward J. Logue organized a consortium of savings banks, cooperatives, and federal and state savings and loan associations in the city called the Boston Banks Urban Renewal Group (B-BURG) that would reverse redline parts of Dorchester, Roxbury, and Mattapan along Blue Hill Avenue. Despite the passage of legislation by the 156th Massachusetts General Court banning racial discrimination or segregation in housing in 1950, as well as the issuance of Executive Order 11063 by President John F. Kennedy in 1962 requiring all federal agencies to prevent racial discrimination in all federally-funded subsidized housing in the United States, the Boston Housing Authority (BHA) Board actively segregated the public housing developments in the city during the Collins administration as well, with BHA departments engaging in bureaucratic resistance against integration through at least 1966 and the Board retaining co... | llama2-7b-chat |  There are several resources available in Boston for studying and preserving historical artifacts and remains. Some of these include: 1. The Boston Historical Society: This organization provides access to historical artifacts, photographs, and documents related to Boston's history. 2. Boston Mapjunction: This website provides over 200 historical maps of Boston dating back to 1630, as well as aerial photos compared with maps of today. 3. City of Boston Archaeology Program and Lab: The City of Boston has a City Archaeologist on staff to oversee any lots of land to be developed for historical artifacts and significance, and to manage the archaeological remains located on public land in Boston. The program also has an Archaeology Laboratory and Education and Curation Center. 4. The Freedom House Photographs Collection: This collection contains over 2,000 images of Roxbury people, places, and events from 1950 to 1975. 5. Vital Records of Boston: This resource provides access to historical records related to births, marriages, and deaths in Boston. 6. Reading and Everyday Life in | mistral-7b-instruct |  The City of Boston has a City Archaeologist on staff to oversee any lots of land to be developed for historical artifacts and significance, and to manage the archaeological remains located on public land in Boston, and also has a City Archaeology Program and an Archaeology Laboratory, Education and Curation Center. The Freedom House Photographs Collection contains over 2,000 images of Roxbury people, places and events, 1950–1975 (Archives and Special Collections of the Northeastern University Libraries in Boston, MA). | 1.000000 | Assistant A provides a more comprehensive answer, listing several resources available in Boston for studying and preserving historical artifacts and remains. These include the Boston Historical Society, Boston Mapjunction, the City of Boston Archaeology Program and Lab, the Freedom House Photographs Collection, and Vital Records of Boston. This answer is more detailed and provides a wider range of resources for the user to explore. Assistant B, on the other hand, only mentions the City of Boston Archaeology Program and Lab and the Freedom House Photographs Collection. While these are relevant resources, the answer lacks the depth and variety of Assistant A's response. Therefore, based on the depth, variety, and level of detail in the responses, Assistant A's answer is superior. Final Verdict: [[A]]  
#### Special Care To The Fine-Tuning JSONL¶
Since there are two evaluations (one for original order of presentation of the LLM answers and another for a flipped ordering), we need to be careful to choose the correct one to keep in our fine-tuning dataset. What this means is that we need to pick off the correct events that were collected by our `OpenAIFineTuningHandler` and then only use those to prepare the JSONL which we will pass to OpenAI's fine-tuning API.
In [ ]:
Copied!
```
main_finetuning_handler.save_finetuning_events(
    "pairwise_finetuning_events.jsonl"
)

```

main_finetuning_handler.save_finetuning_events( "pairwise_finetuning_events.jsonl" )
```
Wrote 150 examples to pairwise_finetuning_events.jsonl

```

In [ ]:
Copied!
```
import json

# Get the fine_tuning_examples master dataset
with open("pairwise_finetuning_events.jsonl") as f:
    combined_finetuning_events = [json.loads(line) for line in f]

```

import json # Get the fine_tuning_examples master dataset with open("pairwise_finetuning_events.jsonl") as f: combined_finetuning_events = [json.loads(line) for line in f]
In [ ]:
Copied!
```
finetuning_events = (
    []
)  # for storing events using original order of presentation
flipped_finetuning_events = (
    []
)  # for storing events using flipped order of presentation

for ix, event in enumerate(combined_finetuning_events):
    if ix % 2 == 0:  # we always do original ordering first
        finetuning_events += [event]
    else:  # then we flip order and have GPT-4 make another judgement
        flipped_finetuning_events += [event]

```

finetuning_events = ( [] ) # for storing events using original order of presentation flipped_finetuning_events = ( [] ) # for storing events using flipped order of presentation for ix, event in enumerate(combined_finetuning_events): if ix % 2 == 0: # we always do original ordering first finetuning_events += [event] else: # then we flip order and have GPT-4 make another judgement flipped_finetuning_events += [event]
In [ ]:
Copied!
```
assert len(finetuning_events) == len(flipped_finetuning_events)

```

assert len(finetuning_events) == len(flipped_finetuning_events)
In [ ]:
Copied!
```
# we need to pick which of the chat_histories to keep
resolved_finetuning_events = []
for ix, data_entry in enumerate(train_dataset):
    if data_entry["evaluations"][0]["source"] == "original":
        resolved_finetuning_events += [finetuning_events[ix]]
    elif data_entry["evaluations"][0]["source"] == "flipped":
        resolved_finetuning_events += [flipped_finetuning_events[ix]]
    else:
        continue

```

# we need to pick which of the chat_histories to keep resolved_finetuning_events = [] for ix, data_entry in enumerate(train_dataset): if data_entry["evaluations"][0]["source"] == "original": resolved_finetuning_events += [finetuning_events[ix]] elif data_entry["evaluations"][0]["source"] == "flipped": resolved_finetuning_events += [flipped_finetuning_events[ix]] else: continue
In [ ]:
Copied!
```
with open("resolved_pairwise_finetuning_events.jsonl", "w") as outfile:
    for entry in resolved_finetuning_events:
        print(json.dumps(entry), file=outfile)

```

with open("resolved_pairwise_finetuning_events.jsonl", "w") as outfile: for entry in resolved_finetuning_events: print(json.dumps(entry), file=outfile)
## Step 2 Perform knowledge distillation¶
Okay, it's now time to distill some knowledge from GPT-4 to GPT-3.5 To do this, we will make use of the `OpenAIFinetuneEngine` class as well as the `resolved_pairwise_finetuning_events.jsonl` file that we just created.
In [ ]:
Copied!
```
from llama_index.finetuning import OpenAIFinetuneEngine

finetune_engine = OpenAIFinetuneEngine(
    "gpt-3.5-turbo",
    "resolved_pairwise_finetuning_events.jsonl",
)

```

from llama_index.finetuning import OpenAIFinetuneEngine finetune_engine = OpenAIFinetuneEngine( "gpt-3.5-turbo", "resolved_pairwise_finetuning_events.jsonl", )
In [ ]:
Copied!
```
finetune_engine.finetune()

```

finetune_engine.finetune()
```
Num examples: 72
First example:
{'role': 'system', 'content': "Please act as an impartial judge and evaluate the quality of the responses provided by two AI question-answering assistants to the user question perhaps with added reference which are displayed below. You should choose the assistant that follows the user’s instructions and answers the user’s question better using the provided context. Your evaluation should consider factors such as the helpfulness, relevance, accuracy, depth, creativity, and level of detail of their responses. Begin your evaluation by comparing the two responses and provide a short explanation. Avoid any position biases and ensure that the order in which the responses were presented does not influence your decision. Do not allow the length of the responses to influence your evaluation. Do not favor certain names of the assistants. Be as objective as possible. After providing your explanation, output your final verdict by strictly following this format: '[[A]]' if assistant A is better, '[[B]]' if assistant B is better, and '[[C]]' for a tie.\n"}
{'role': 'user', 'content': "[User Question]\nWhat event in 1906 caused significant damage to San Francisco but was followed by a quick rebuild?\n\n[The Start of Reference]\n=== Reconstruction ===\nAlmost immediately after the quake re-planning and reconstruction plans were hatched to quickly rebuild the city. One of the more famous and ambitious plans, proposed before the fire, came from famed urban planner, Daniel Burnham. His bold plan called for Haussmann style avenues, boulevards, and arterial thoroughfares that radiated across the city, a massive civic center complex with classical structures, what would have been the largest urban park in the world, stretching from Twin Peaks to Lake Merced with a large athenaeum at its peak, and various other proposals. This plan was dismissed by critics (both at the time and now), as impractical and unrealistic to municipal supply and demand. Property owners and the Real Estate industry were against the idea as well due to the amounts of their land the city would have to purchase to realize such proposals. While the original street grid was restored, many of Burnham's proposals eventually saw the light of day such ...\n[The End of Reference]\n\n[The Start of Assistant A’s Answer]\n\n\nThe 1906 earthquake and fire caused significant damage to San Francisco, with over 80% of the city destroyed, including almost all of the downtown core. The earthquake, which had a magnitude of 7.8 on the Richter scale, resulted from the rupture of over 270 miles of the San Andreas Fault, centered immediately offshore of San Francisco. Water mains ruptured throughout the city, and the fires that followed burned out of control for days, trapping many residents and causing widespread destruction. Despite the devastation, the city quickly rebuilt, with many of the buildings constructed after the disaster being more earthquake-resistant than those that had come before. The official death toll from this event was initially reported as 478, but was later revised to over 3,000.\n[The End of Assistant A’s Answer]\n\n[The Start of Assistant B’s Answer]\n1906 earthquake and fire.\n[The End of Assistant B’s Answer]"}
{'role': 'assistant', 'content': "Assistant A provides a detailed and comprehensive response to the user's question, explaining the event that caused significant damage to San Francisco in 1906, which was the earthquake and fire. It also provides additional information about the earthquake's magnitude, the extent of the damage, and the city's quick rebuilding efforts. On the other hand, Assistant B's response is very brief and only mentions the earthquake and fire, without providing any additional information or context. Therefore, Assistant A's response is more helpful, relevant, accurate, and detailed. \n\nFinal Verdict: [[A]]"}
No errors found
Num examples missing system message: 0
Num examples missing user message: 0

#### Distribution of num_messages_per_example:
min / max: 3, 3
mean / median: 3.0, 3.0
p5 / p95: 3.0, 3.0

#### Distribution of num_total_tokens_per_example:
min / max: 579, 1198
mean / median: 818.9305555555555, 772.0
p5 / p95: 625.9, 1076.0

#### Distribution of num_assistant_tokens_per_example:
min / max: 66, 248
mean / median: 129.26388888888889, 117.5
p5 / p95: 81.0, 193.9

0 examples may be over the 4096 token limit, they will be truncated during fine-tuning
Dataset has ~58963 tokens that will be charged for during training
By default, you'll train for 3 epochs on this dataset
By default, you'll be charged for ~176889 tokens
As of August 22, 2023, fine-tuning gpt-3.5-turbo is $0.008 / 1K Tokens.
This means your total cost for training will be $0.471704 per epoch.

```

In [ ]:
Copied!
```
# We can check the status of our current job as follows
# This may take some time ...
finetune_engine.get_current_job()

```

# We can check the status of our current job as follows # This may take some time ... finetune_engine.get_current_job()
Out[ ]:
```
<FineTuningJob fine_tuning.job id=ftjob-jLxZggQbHz2F98IlhQEI9KIw at 0x2e6b91170> JSON: {
  "object": "fine_tuning.job",
  "id": "ftjob-jLxZggQbHz2F98IlhQEI9KIw",
  "model": "gpt-3.5-turbo-0613",
  "created_at": 1698817329,
  "finished_at": 1698817949,
  "fine_tuned_model": "ft:gpt-3.5-turbo-0613:llamaindex::8FyRSSOl",
  "organization_id": "org-1ZDAvajC6v2ZtAP9hLEIsXRz",
  "result_files": [
    "file-qLTnxGSZX2rHP0Q7wJIDDNWX"
  ],
  "status": "succeeded",
  "validation_file": null,
  "training_file": "file-xsAaOBjQ949ti0qk1xHHLOiF",
  "hyperparameters": {
    "n_epochs": 3
  },
  "trained_tokens": 176457,
  "error": null
}
```

## 3 Evaluate The Fine-Tuned GPT-3.5 Judge On The Test Dataset¶
Now that we have our fine-tuned GPT-3.5, let's see how well it performs on a test set. But first, remember that we said we'd hold off on creating the `test_dataset` until the time comes that we need it? Well, that time is now. So we will repeat the process of creating the `train_dataset` here but instead now for the `test_dataset`.
NOTE: generating these answers and evaluations will take some time. You have the option of loading `test_qa_complete.jsonl` which has all the evaluations from the three considered LLM judges. You can load that as `test_dataset` and run the code found in the Metrics subsection below.
In [ ]:
Copied!
```
import random

# Use Llama-2 and Mistral LLMs to generate the answers to the test queries
test_dataset = []
for q in tqdm.tqdm(test_questions):
    # randomly select two LLMs to generate answers to this q
    model_versus = random.sample(list(test_query_engines.items()), 2)

    # data for this q
    data_entry = {"question": q}
    responses = []
    source = None

    # generate answers
    for name, engine in model_versus:
        response = engine.query(q)
        response_struct = {}
        response_struct["model"] = name
        response_struct["text"] = str(response)
        if source is not None:
            assert source == response.source_nodes[0].node.text[:1000] + "..."
        else:
            source = response.source_nodes[0].node.text[:1000] + "..."
        responses.append(response_struct)

    data_entry["answers"] = responses
    data_entry["source"] = source
    test_dataset.append(data_entry)

```

import random # Use Llama-2 and Mistral LLMs to generate the answers to the test queries test_dataset = [] for q in tqdm.tqdm(test_questions): # randomly select two LLMs to generate answers to this q model_versus = random.sample(list(test_query_engines.items()), 2) # data for this q data_entry = {"question": q} responses = [] source = None # generate answers for name, engine in model_versus: response = engine.query(q) response_struct = {} response_struct["model"] = name response_struct["text"] = str(response) if source is not None: assert source == response.source_nodes[0].node.text[:1000] + "..." else: source = response.source_nodes[0].node.text[:1000] + "..." responses.append(response_struct) data_entry["answers"] = responses data_entry["source"] = source test_dataset.append(data_entry)
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 64/64 [28:23<00:00, 26.62s/it]

```

In [ ]:
Copied!
```
# get the gpt-4 judgments on the Mistal and Llama-2 answers
for data_entry in tqdm.tqdm(test_dataset):
    final_eval_result = await gpt4_judge.aevaluate(
        query=data_entry["question"],
        response=data_entry["answers"][0]["text"],
        second_response=data_entry["answers"][1]["text"],
        reference=data_entry["source"],
    )

    # save final result
    judgement = {}
    judgement["llm"] = "gpt_4"
    judgement["score"] = final_eval_result.score
    judgement["text"] = final_eval_result.response
    judgement["source"] = final_eval_result.pairwise_source
    data_entry["evaluations"] = [judgement]

```

# get the gpt-4 judgments on the Mistal and Llama-2 answers for data_entry in tqdm.tqdm(test_dataset): final_eval_result = await gpt4_judge.aevaluate( query=data_entry["question"], response=data_entry["answers"][0]["text"], second_response=data_entry["answers"][1]["text"], reference=data_entry["source"], ) # save final result judgement = {} judgement["llm"] = "gpt_4" judgement["score"] = final_eval_result.score judgement["text"] = final_eval_result.response judgement["source"] = final_eval_result.pairwise_source data_entry["evaluations"] = [judgement]
```
100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 64/64 [43:21<00:00, 40.66s/it]

```

In [ ]:
Copied!
```
from llama_index.core.evaluation import EvaluationResult

# use our fine-tuned GPT-3.5 to evaluate the answers
ft_llm = finetune_engine.get_finetuned_model()


ft_gpt_3p5_judge = PairwiseComparisonEvaluator(llm=ft_llm)

for data_entry in tqdm.tqdm(test_dataset):
    try:
        final_eval_result = await ft_gpt_3p5_judge.aevaluate(
            query=data_entry["question"],
            response=data_entry["answers"][0]["text"],
            second_response=data_entry["answers"][1]["text"],
            reference=data_entry["source"],
        )
    except:
        final_eval_result = EvaluationResult(
            query=data_entry["question"],
            response="",
            passing=None,
            score=0.5,
            feedback="",
            pairwise_source="output-cannot-be-parsed",
        )

    # save final result
    judgement = {}
    judgement["llm"] = "ft_gpt_3p5"
    judgement["score"] = final_eval_result.score
    judgement["text"] = final_eval_result.response
    judgement["source"] = final_eval_result.pairwise_source
    data_entry["evaluations"] += [judgement]

```

from llama_index.core.evaluation import EvaluationResult # use our fine-tuned GPT-3.5 to evaluate the answers ft_llm = finetune_engine.get_finetuned_model() ft_gpt_3p5_judge = PairwiseComparisonEvaluator(llm=ft_llm) for data_entry in tqdm.tqdm(test_dataset): try: final_eval_result = await ft_gpt_3p5_judge.aevaluate( query=data_entry["question"], response=data_entry["answers"][0]["text"], second_response=data_entry["answers"][1]["text"], reference=data_entry["source"], ) except: final_eval_result = EvaluationResult( query=data_entry["question"], response="", passing=None, score=0.5, feedback="", pairwise_source="output-cannot-be-parsed", ) # save final result judgement = {} judgement["llm"] = "ft_gpt_3p5" judgement["score"] = final_eval_result.score judgement["text"] = final_eval_result.response judgement["source"] = final_eval_result.pairwise_source data_entry["evaluations"] += [judgement]
```
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 64/64 [04:08<00:00,  3.88s/it]

```

In [ ]:
Copied!
```
# Similarly, use a non-fine-tuned judge to evaluate the answers
gpt_3p5_llm = OpenAI(model="gpt-3.5-turbo")

gpt_3p5_judge = PairwiseComparisonEvaluator(llm=gpt_3p5_llm)

for data_entry in tqdm.tqdm(test_dataset):
    try:
        final_eval_result = await gpt_3p5_judge.aevaluate(
            query=data_entry["question"],
            response=data_entry["answers"][0]["text"],
            second_response=data_entry["answers"][1]["text"],
            reference=data_entry["source"],
        )
    except:
        final_eval_result = EvaluationResult(
            query=data_entry["question"],
            response="",
            passing=None,
            score=0.5,
            feedback="",
            pairwise_source="output-cannot-be-parsed",
        )

    # save final result
    judgement = {}
    judgement["llm"] = "gpt_3p5"
    judgement["score"] = final_eval_result.score
    judgement["text"] = final_eval_result.response
    judgement["source"] = final_eval_result.pairwise_source
    data_entry["evaluations"] += [judgement]

```

# Similarly, use a non-fine-tuned judge to evaluate the answers gpt_3p5_llm = OpenAI(model="gpt-3.5-turbo") gpt_3p5_judge = PairwiseComparisonEvaluator(llm=gpt_3p5_llm) for data_entry in tqdm.tqdm(test_dataset): try: final_eval_result = await gpt_3p5_judge.aevaluate( query=data_entry["question"], response=data_entry["answers"][0]["text"], second_response=data_entry["answers"][1]["text"], reference=data_entry["source"], ) except: final_eval_result = EvaluationResult( query=data_entry["question"], response="", passing=None, score=0.5, feedback="", pairwise_source="output-cannot-be-parsed", ) # save final result judgement = {} judgement["llm"] = "gpt_3p5" judgement["score"] = final_eval_result.score judgement["text"] = final_eval_result.response judgement["source"] = final_eval_result.pairwise_source data_entry["evaluations"] += [judgement]
```
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 64/64 [09:32<00:00,  8.95s/it]

```

### The Metrics¶
Phew! Now that we have generated all of the LLM judges evaluations of the Llama-2/Mistral answers on the test queries. Let's now get a quantitative view on how close fine-tuned GPT-3.5 is to GPT-4.
For this, we report several metrics, namely:
  * Agreement Rate with GPT-4 evaluations
  * Correlation to GPT-4 evaluations
  * Jaccard Similarity to GPT-4 evaluations


We also report the "inconclusive" counts, which is when the LLM judge switches its decision after being presented with the flipped order of presentation of Llama-2 and Mistral answers. Higher inconclusive counts is an indication of the LLM judge being susceptible to position bias, which is no good!
In [ ]:
Copied!
```
!pip install scikit-learn -q

```

!pip install scikit-learn -q
```
[notice] A new release of pip is available: 23.2.1 -> 23.3.1
[notice] To update, run: pip install --upgrade pip

```

In [ ]:
Copied!
```
import numpy as np

# store the scores and inconclusive booleans for each sample per LLM judge
scores = {"gpt_4": [], "gpt_3p5": [], "ft_gpt_3p5": []}
inconclusives = {"gpt_4": [], "gpt_3p5": [], "ft_gpt_3p5": []}

for ix, d in enumerate(test_dataset):
    for e in d["evaluations"]:
        scores[e["llm"]].append(e["score"])
        inconclusives[e["llm"]].append(
            e["source"] not in ["original", "flipped"]
        )

```

import numpy as np # store the scores and inconclusive booleans for each sample per LLM judge scores = {"gpt_4": [], "gpt_3p5": [], "ft_gpt_3p5": []} inconclusives = {"gpt_4": [], "gpt_3p5": [], "ft_gpt_3p5": []} for ix, d in enumerate(test_dataset): for e in d["evaluations"]: scores[e["llm"]].append(e["score"]) inconclusives[e["llm"]].append( e["source"] not in ["original", "flipped"] )
In [ ]:
Copied!
```
REPORT_FMT_STR = (
    "{model}\n"
    "-----------------\n"
    "Number of inconclusives: {inconclusive}\n"
    "Number of agreements with GPT-4: {agreement} out of {total}\n"
    "Agreement rate: {agreement_rate}\n"
    "Correlation: {corr}\n"
    "Jaccard: {jacc}\n\n"
)

```

REPORT_FMT_STR = ( "{model}\n" "-----------------\n" "Number of inconclusives: {inconclusive}\n" "Number of agreements with GPT-4: {agreement} out of {total}\n" "Agreement rate: {agreement_rate}\n" "Correlation: {corr}\n" "Jaccard: {jacc}\n\n" )
In [ ]:
Copied!
```
from sklearn.metrics import jaccard_score

# numpy conversion
np_scores_gpt_4 = np.array(scores["gpt_4"])
np_scores_gpt_3p5 = np.array(scores["gpt_3p5"])
np_scores_ft_gpt_3p5 = np.array(scores["ft_gpt_3p5"])

# can only compare when both judges have non inconclusive results
ft_mask = ~np.array(inconclusives["gpt_4"]) * ~np.array(
    inconclusives["ft_gpt_3p5"]
)
no_ft_mask = ~np.array(inconclusives["gpt_4"]) * ~np.array(
    inconclusives["gpt_3p5"]
)

# agreement rates
agreement_ft = sum(np_scores_gpt_4[ft_mask] == np_scores_ft_gpt_3p5[ft_mask])
agreement_rate_ft = agreement_ft / sum(ft_mask)
agreement_no_ft = sum(
    np_scores_gpt_4[no_ft_mask] == np_scores_gpt_3p5[no_ft_mask]
)
agreement_rate_no_ft = agreement_no_ft / sum(no_ft_mask)

# correlations
corr_ft = np.corrcoef(np_scores_gpt_4[ft_mask], np_scores_ft_gpt_3p5[ft_mask])[
    0, 1
]
corr_no_ft = np.corrcoef(
    np_scores_gpt_4[no_ft_mask], np_scores_gpt_3p5[no_ft_mask]
)[0, 1]

# jaccard
jaccard_ft = jaccard_score(
    np_scores_gpt_4[ft_mask].astype(str),
    np_scores_ft_gpt_3p5[ft_mask].astype(str),
    average="weighted",
)
jaccard_no_ft = jaccard_score(
    np_scores_gpt_4[no_ft_mask].astype(str),
    np_scores_gpt_3p5[no_ft_mask].astype(str),
    average="weighted",
)

print(
    REPORT_FMT_STR.format(
        model="GPT-3.5 w/ fine-tuning",
        inconclusive=sum(inconclusives["ft_gpt_3p5"]),
        agreement=agreement_ft,
        total=sum(ft_mask),
        agreement_rate=agreement_rate_ft,
        corr=corr_ft,
        jacc=jaccard_ft,
    )
)
print(
    REPORT_FMT_STR.format(
        model="GPT-3.5 w/out fine-tuning",
        inconclusive=sum(inconclusives["gpt_3p5"]),
        agreement=agreement_no_ft,
        total=sum(no_ft_mask),
        agreement_rate=agreement_rate_no_ft,
        corr=corr_no_ft,
        jacc=jaccard_no_ft,
    )
)
print(
    f"GPT-4\n-----------------\nInconclusive Count: {sum(inconclusives['gpt_4'])}"
)

```

from sklearn.metrics import jaccard_score # numpy conversion np_scores_gpt_4 = np.array(scores["gpt_4"]) np_scores_gpt_3p5 = np.array(scores["gpt_3p5"]) np_scores_ft_gpt_3p5 = np.array(scores["ft_gpt_3p5"]) # can only compare when both judges have non inconclusive results ft_mask = ~np.array(inconclusives["gpt_4"]) * ~np.array( inconclusives["ft_gpt_3p5"] ) no_ft_mask = ~np.array(inconclusives["gpt_4"]) * ~np.array( inconclusives["gpt_3p5"] ) # agreement rates agreement_ft = sum(np_scores_gpt_4[ft_mask] == np_scores_ft_gpt_3p5[ft_mask]) agreement_rate_ft = agreement_ft / sum(ft_mask) agreement_no_ft = sum( np_scores_gpt_4[no_ft_mask] == np_scores_gpt_3p5[no_ft_mask] ) agreement_rate_no_ft = agreement_no_ft / sum(no_ft_mask) # correlations corr_ft = np.corrcoef(np_scores_gpt_4[ft_mask], np_scores_ft_gpt_3p5[ft_mask])[ 0, 1 ] corr_no_ft = np.corrcoef( np_scores_gpt_4[no_ft_mask], np_scores_gpt_3p5[no_ft_mask] )[0, 1] # jaccard jaccard_ft = jaccard_score( np_scores_gpt_4[ft_mask].astype(str), np_scores_ft_gpt_3p5[ft_mask].astype(str), average="weighted", ) jaccard_no_ft = jaccard_score( np_scores_gpt_4[no_ft_mask].astype(str), np_scores_gpt_3p5[no_ft_mask].astype(str), average="weighted", ) print( REPORT_FMT_STR.format( model="GPT-3.5 w/ fine-tuning", inconclusive=sum(inconclusives["ft_gpt_3p5"]), agreement=agreement_ft, total=sum(ft_mask), agreement_rate=agreement_rate_ft, corr=corr_ft, jacc=jaccard_ft, ) ) print( REPORT_FMT_STR.format( model="GPT-3.5 w/out fine-tuning", inconclusive=sum(inconclusives["gpt_3p5"]), agreement=agreement_no_ft, total=sum(no_ft_mask), agreement_rate=agreement_rate_no_ft, corr=corr_no_ft, jacc=jaccard_no_ft, ) ) print( f"GPT-4\n-----------------\nInconclusive Count: {sum(inconclusives['gpt_4'])}" )
```
GPT-3.5 w/ fine-tuning
-----------------
Number of inconclusives: 15
Number of agreements with GPT-4: 41 out of 47
Agreement rate: 0.8723404255319149
Correlation: 0.765365523658036
Jaccard: 0.773126734505088


GPT-3.5 w/out fine-tuning
-----------------
Number of inconclusives: 24
Number of agreements with GPT-4: 32 out of 38
Agreement rate: 0.8421052631578947
Correlation: 0.671929323262293
Jaccard: 0.7308712958867757


GPT-4
-----------------
Inconclusive Count: 4

```

## Conclusion¶
From the above numbers we see that fine-tuning a GPT-3.5 judge yields higher agreement scores, correlation, and jaccard similarity than a non-fine-tuned GPT-3.5 judge. What's more is that we see the inconclusive counts go down after fine-tuning as well. Overall, we see that fine-tuning here has helped us to get a GPT-3.5 judge that is closer to a GPT-4 judge (and thus by proxy, closer to human judgements) and at the same time helped remedy the position bias that a non-fine-tuned GPT-3.5 would have otherwise.
