![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# How to Finetune a cross-encoder using LLamaIndex¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-finetuning-cross-encoders
%pip install llama-index-llms-openai

```

%pip install llama-index-finetuning-cross-encoders %pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# Download Requirements
!pip install datasets --quiet
!pip install sentence-transformers --quiet
!pip install openai --quiet

```

# Download Requirements !pip install datasets --quiet !pip install sentence-transformers --quiet !pip install openai --quiet
```
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 519.6/519.6 kB 7.7 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 115.3/115.3 kB 11.6 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 194.1/194.1 kB 19.2 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 134.8/134.8 kB 13.0 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 302.0/302.0 kB 25.5 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 86.0/86.0 kB 1.9 MB/s eta 0:00:00
  Preparing metadata (setup.py) ... done
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 7.7/7.7 MB 42.3 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 43.9 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.8/3.8 MB 52.1 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.3/1.3 MB 58.6 MB/s eta 0:00:00
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 295.0/295.0 kB 27.1 MB/s eta 0:00:00
  Building wheel for sentence-transformers (setup.py) ... done
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 77.0/77.0 kB 1.8 MB/s eta 0:00:00

```

## Process¶
  * Download the QASPER Dataset from HuggingFace Hub using Datasets Library (https://huggingface.co/datasets/allenai/qasper)
  * From the train and test splits of the dataset extract 800 and 80 samples respectively
  * Use the 800 samples collected from train data which have the respective questions framed on a research paper to generate a dataset in the respective format required for CrossEncoder finetuning. Currently the format we use is that a single sample of fine tune data consists of two sentences(question and context) and a score either 0 or 1 where 1 shows that the question and context are relevant to each other and 0 shows they are not relevant to each other.
  * Use the 100 samples of test set to extract two kinds of evaluation datasets
    * Rag Eval Dataset:-One dataset consists of samples where a single sample consists of a research paper content, list of questions on the research paper, answers of the list of questions on the research paper. While forming this dataset we keep only questions which have long answers/ free-form answers for better comparision with RAG generated answers.
    * Reranking Eval Dataset:- The other datasets consists of samples where a single sample consists of the research paper content, list of questions on the research paper, list of contexts from the research paper contents relevant to each question
  * We finetuned the cross-encoder using helper utilities written in llamaindex and push it to HuggingFace Hub using the huggingface cli tokens login which can be found here:- https://huggingface.co/settings/tokens
  * We evaluate on both datasets using two metrics and three cases
    1. Just OpenAI embeddings without any reranker
    2. OpenAI embeddings combined with cross-encoder/ms-marco-MiniLM-L-12-v2 as reranker
    3. OpenAI embeddings combined with our fine-tuned cross encoder model as reranker


  * Evaluation Criteria for each Eval Dataset
    * Hits metric:- For evaluating the Reranking Eval Dataset we just simply use the retriever+ post-processor functionalities of LLamaIndex to see in the different cases how many times does the relevant context gets retrieved and call it the hits metric.
    * Pairwise Comparision Evaluator:- We use the Pairwise Comparision Evaluator provided by LLamaIndex (https://github.com/run-llama/llama_index/blob/main/llama_index/evaluation/pairwise.py) to compare the responses of the respective query engines created in each case with the reference free-form answers provided.


## Load the Dataset¶
In [ ]:
Copied!
```
from datasets import load_dataset
import random


# Download QASPER dataset from HuggingFace https://huggingface.co/datasets/allenai/qasper
dataset = load_dataset("allenai/qasper")

# Split the dataset into train, validation, and test splits
train_dataset = dataset["train"]
validation_dataset = dataset["validation"]
test_dataset = dataset["test"]

random.seed(42)  # Set a random seed for reproducibility

# Randomly sample 800 rows from the training split
train_sampled_indices = random.sample(range(len(train_dataset)), 800)
train_samples = [train_dataset[i] for i in train_sampled_indices]


# Randomly sample 100 rows from the test split
test_sampled_indices = random.sample(range(len(test_dataset)), 80)
test_samples = [test_dataset[i] for i in test_sampled_indices]

# Now we have 800 research papers for training and 80 research papers to evaluate on

```

from datasets import load_dataset import random # Download QASPER dataset from HuggingFace https://huggingface.co/datasets/allenai/qasper dataset = load_dataset("allenai/qasper") # Split the dataset into train, validation, and test splits train_dataset = dataset["train"] validation_dataset = dataset["validation"] test_dataset = dataset["test"] random.seed(42) # Set a random seed for reproducibility # Randomly sample 800 rows from the training split train_sampled_indices = random.sample(range(len(train_dataset)), 800) train_samples = [train_dataset[i] for i in train_sampled_indices] # Randomly sample 100 rows from the test split test_sampled_indices = random.sample(range(len(test_dataset)), 80) test_samples = [test_dataset[i] for i in test_sampled_indices] # Now we have 800 research papers for training and 80 research papers to evaluate on
## QASPER Dataset¶
  * Each row has the below 6 columns
    * id: Unique identifier of the research paper
    * title: Title of the Research paper
    * abstract: Abstract of the research paper
    * full_text: full text of the research paper
    * qas: Questions and answers pertaining to each research paper
    * figures_and_tables: figures and tables of each research paper


In [ ]:
Copied!
```
# Get full text paper data , questions on the paper from training samples of QASPER to generate training dataset for cross-encoder finetuning
from typing import List


# Utility function to get full-text of the research papers from the dataset
def get_full_text(sample: dict) -> str:
    """
    :param dict sample: the row sample from QASPER
    """
    title = sample["title"]
    abstract = sample["abstract"]
    sections_list = sample["full_text"]["section_name"]
    paragraph_list = sample["full_text"]["paragraphs"]
    combined_sections_with_paras = ""
    if len(sections_list) == len(paragraph_list):
        combined_sections_with_paras += title + "\t"
        combined_sections_with_paras += abstract + "\t"
        for index in range(0, len(sections_list)):
            combined_sections_with_paras += str(sections_list[index]) + "\t"
            combined_sections_with_paras += "".join(paragraph_list[index])
        return combined_sections_with_paras

    else:
        print("Not the same number of sections as paragraphs list")


# utility function to extract list of questions from the dataset
def get_questions(sample: dict) -> List[str]:
    """
    :param dict sample: the row sample from QASPER
    """
    questions_list = sample["qas"]["question"]
    return questions_list


doc_qa_dict_list = []

for train_sample in train_samples:
    full_text = get_full_text(train_sample)
    questions_list = get_questions(train_sample)
    local_dict = {"paper": full_text, "questions": questions_list}
    doc_qa_dict_list.append(local_dict)

```

# Get full text paper data , questions on the paper from training samples of QASPER to generate training dataset for cross-encoder finetuning from typing import List # Utility function to get full-text of the research papers from the dataset def get_full_text(sample: dict) -> str: """ :param dict sample: the row sample from QASPER """ title = sample["title"] abstract = sample["abstract"] sections_list = sample["full_text"]["section_name"] paragraph_list = sample["full_text"]["paragraphs"] combined_sections_with_paras = "" if len(sections_list) == len(paragraph_list): combined_sections_with_paras += title + "\t" combined_sections_with_paras += abstract + "\t" for index in range(0, len(sections_list)): combined_sections_with_paras += str(sections_list[index]) + "\t" combined_sections_with_paras += "".join(paragraph_list[index]) return combined_sections_with_paras else: print("Not the same number of sections as paragraphs list") # utility function to extract list of questions from the dataset def get_questions(sample: dict) -> List[str]: """ :param dict sample: the row sample from QASPER """ questions_list = sample["qas"]["question"] return questions_list doc_qa_dict_list = [] for train_sample in train_samples: full_text = get_full_text(train_sample) questions_list = get_questions(train_sample) local_dict = {"paper": full_text, "questions": questions_list} doc_qa_dict_list.append(local_dict)
In [ ]:
Copied!
```
len(doc_qa_dict_list)

```

len(doc_qa_dict_list)
Out[ ]:


In [ ]:
Copied!
```
# Save training data as a csv
import pandas as pd

df_train = pd.DataFrame(doc_qa_dict_list)
df_train.to_csv("train.csv")

```

# Save training data as a csv import pandas as pd df_train = pd.DataFrame(doc_qa_dict_list) df_train.to_csv("train.csv")
### Generate RAG Eval test data¶
In [ ]:
Copied!
```
# Get evaluation data papers , questions and answers
"""
The Answers field in the dataset follow the below format:-
Unanswerable answers have "unanswerable" set to true.

The remaining answers have exactly one of the following fields being non-empty.

"extractive_spans" are spans in the paper which serve as the answer.
"free_form_answer" is a written out answer.
"yes_no" is true iff the answer is Yes, and false iff the answer is No.

We accept only free-form answers and for all the other kind of answers we set their value to 'Unacceptable',
to better evaluate the performance of the query engine using pairwise comparison evaluator as it uses GPT-4 which is biased towards preferring long answers more.
https://www.anyscale.com/blog/a-comprehensive-guide-for-building-rag-based-llm-applications-part-1

So in the case of 'yes_no' answers it can favour Query Engine answers more than reference answers.
Also in the case of extracted spans it can favour reference answers more than Query engine generated answers.

"""


eval_doc_qa_answer_list = []


# Utility function to extract answers from the dataset
def get_answers(sample: dict) -> List[str]:
    """
    :param dict sample: the row sample from the train split of QASPER
    """
    final_answers_list = []
    answers = sample["qas"]["answers"]
    for answer in answers:
        local_answer = ""
        types_of_answers = answer["answer"][0]
        if types_of_answers["unanswerable"] == False:
            if types_of_answers["free_form_answer"] != "":
                local_answer = types_of_answers["free_form_answer"]
            else:
                local_answer = "Unacceptable"
        else:
            local_answer = "Unacceptable"

        final_answers_list.append(local_answer)

    return final_answers_list


for test_sample in test_samples:
    full_text = get_full_text(test_sample)
    questions_list = get_questions(test_sample)
    answers_list = get_answers(test_sample)
    local_dict = {
        "paper": full_text,
        "questions": questions_list,
        "answers": answers_list,
    }
    eval_doc_qa_answer_list.append(local_dict)

```

# Get evaluation data papers , questions and answers """ The Answers field in the dataset follow the below format:- Unanswerable answers have "unanswerable" set to true. The remaining answers have exactly one of the following fields being non-empty. "extractive_spans" are spans in the paper which serve as the answer. "free_form_answer" is a written out answer. "yes_no" is true iff the answer is Yes, and false iff the answer is No. We accept only free-form answers and for all the other kind of answers we set their value to 'Unacceptable', to better evaluate the performance of the query engine using pairwise comparison evaluator as it uses GPT-4 which is biased towards preferring long answers more. https://www.anyscale.com/blog/a-comprehensive-guide-for-building-rag-based-llm-applications-part-1 So in the case of 'yes_no' answers it can favour Query Engine answers more than reference answers. Also in the case of extracted spans it can favour reference answers more than Query engine generated answers. """ eval_doc_qa_answer_list = [] # Utility function to extract answers from the dataset def get_answers(sample: dict) -> List[str]: """ :param dict sample: the row sample from the train split of QASPER """ final_answers_list = [] answers = sample["qas"]["answers"] for answer in answers: local_answer = "" types_of_answers = answer["answer"][0] if types_of_answers["unanswerable"] == False: if types_of_answers["free_form_answer"] != "": local_answer = types_of_answers["free_form_answer"] else: local_answer = "Unacceptable" else: local_answer = "Unacceptable" final_answers_list.append(local_answer) return final_answers_list for test_sample in test_samples: full_text = get_full_text(test_sample) questions_list = get_questions(test_sample) answers_list = get_answers(test_sample) local_dict = { "paper": full_text, "questions": questions_list, "answers": answers_list, } eval_doc_qa_answer_list.append(local_dict)
In [ ]:
Copied!
```
len(eval_doc_qa_answer_list)

```

len(eval_doc_qa_answer_list)


In [ ]:
Copied!
```
# Save eval data as a csv
import pandas as pd

df_test = pd.DataFrame(eval_doc_qa_answer_list)
df_test.to_csv("test.csv")

# The Rag Eval test data can be found at the below dropbox link
# https://www.dropbox.com/scl/fi/3lmzn6714oy358mq0vawm/test.csv?rlkey=yz16080te4van7fvnksi9kaed&dl=0

```

# Save eval data as a csv import pandas as pd df_test = pd.DataFrame(eval_doc_qa_answer_list) df_test.to_csv("test.csv") # The Rag Eval test data can be found at the below dropbox link # https://www.dropbox.com/scl/fi/3lmzn6714oy358mq0vawm/test.csv?rlkey=yz16080te4van7fvnksi9kaed&dl=0
### Generate Finetuning Dataset¶
In [ ]:
Copied!
```
# Download the latest version of llama-index
!pip install llama-index --quiet

```

# Download the latest version of llama-index !pip install llama-index --quiet
In [ ]:
Copied!
```
# Generate the respective training dataset from the initial train data collected from QASPER in the format required by
import os
from llama_index.core import SimpleDirectoryReader
import openai
from llama_index.finetuning.cross_encoders.dataset_gen import (
    generate_ce_fine_tuning_dataset,
    generate_synthetic_queries_over_documents,
)

from llama_index.finetuning.cross_encoders import CrossEncoderFinetuneEngine

os.environ["OPENAI_API_KEY"] = "sk-"
openai.api_key = os.environ["OPENAI_API_KEY"]

```

# Generate the respective training dataset from the initial train data collected from QASPER in the format required by import os from llama_index.core import SimpleDirectoryReader import openai from llama_index.finetuning.cross_encoders.dataset_gen import ( generate_ce_fine_tuning_dataset, generate_synthetic_queries_over_documents, ) from llama_index.finetuning.cross_encoders import CrossEncoderFinetuneEngine os.environ["OPENAI_API_KEY"] = "sk-" openai.api_key = os.environ["OPENAI_API_KEY"]
In [ ]:
Copied!
```
from llama_index.core import Document

final_finetuning_data_list = []
for paper in doc_qa_dict_list:
    questions_list = paper["questions"]
    documents = [Document(text=paper["paper"])]
    local_finetuning_dataset = generate_ce_fine_tuning_dataset(
        documents=documents,
        questions_list=questions_list,
        max_chunk_length=256,
        top_k=5,
    )
    final_finetuning_data_list.extend(local_finetuning_dataset)

```

from llama_index.core import Document final_finetuning_data_list = [] for paper in doc_qa_dict_list: questions_list = paper["questions"] documents = [Document(text=paper["paper"])] local_finetuning_dataset = generate_ce_fine_tuning_dataset( documents=documents, questions_list=questions_list, max_chunk_length=256, top_k=5, ) final_finetuning_data_list.extend(local_finetuning_dataset)
In [ ]:
Copied!
```
# Total samples in the final fine-tuning dataset
len(final_finetuning_data_list)

```

# Total samples in the final fine-tuning dataset len(final_finetuning_data_list)
Out[ ]:


In [ ]:
Copied!
```
# Save final fine-tuning dataset
import pandas as pd

df_finetuning_dataset = pd.DataFrame(final_finetuning_data_list)
df_finetuning_dataset.to_csv("fine_tuning.csv")

# The finetuning dataset can be found at the below dropbox link:-
# https://www.dropbox.com/scl/fi/zu6vtisp1j3wg2hbje5xv/fine_tuning.csv?rlkey=0jr6fud8sqk342agfjbzvwr9x&dl=0

```

# Save final fine-tuning dataset import pandas as pd df_finetuning_dataset = pd.DataFrame(final_finetuning_data_list) df_finetuning_dataset.to_csv("fine_tuning.csv") # The finetuning dataset can be found at the below dropbox link:- # https://www.dropbox.com/scl/fi/zu6vtisp1j3wg2hbje5xv/fine_tuning.csv?rlkey=0jr6fud8sqk342agfjbzvwr9x&dl=0
In [ ]:
Copied!
```
# Load fine-tuning dataset

finetuning_dataset = final_finetuning_data_list

```

# Load fine-tuning dataset finetuning_dataset = final_finetuning_data_list
In [ ]:
Copied!
```
finetuning_dataset[0]

```

finetuning_dataset[0]
Out[ ]:
```
CrossEncoderFinetuningDatasetSample(query='Do they repot results only on English data?', context='addition to precision, recall, and F1 scores for both tasks, we show the average of the F1 scores across both tasks. On the ADE dataset, we achieve SOTA results for both the NER and RE tasks. On the CoNLL04 dataset, we achieve SOTA results on the NER task, while our performance on the RE task is competitive with other recent models. On both datasets, we achieve SOTA results when considering the average F1 score across both tasks. The largest gain relative to the previous SOTA performance is on the RE task of the ADE dataset, where we see an absolute improvement of 4.5 on the macro-average F1 score.While the model of Eberts and Ulges eberts2019span outperforms our proposed architecture on the CoNLL04 RE task, their results come at the cost of greater model complexity. As mentioned above, Eberts and Ulges fine-tune the BERTBASE model, which has 110 million trainable parameters. In contrast, given the hyperparameters used for final training on the CoNLL04 dataset, our proposed architecture has approximately 6 million trainable parameters.The fact that the optimal number of task-specific layers differed between the two datasets demonstrates the', score=0)
```

### Generate Reranking Eval test data¶
In [ ]:
Copied!
```
# Download RAG Eval test data
!wget -O test.csv https://www.dropbox.com/scl/fi/3lmzn6714oy358mq0vawm/test.csv?rlkey=yz16080te4van7fvnksi9kaed&dl=0

```

# Download RAG Eval test data !wget -O test.csv https://www.dropbox.com/scl/fi/3lmzn6714oy358mq0vawm/test.csv?rlkey=yz16080te4van7fvnksi9kaed&dl=0
In [ ]:
Copied!
```
# Generate Reranking Eval Dataset from the Eval data
import pandas as pd
import ast  # Used to safely evaluate the string as a list

# Load Eval Data
df_test = pd.read_csv("/content/test.csv", index_col=0)

df_test["questions"] = df_test["questions"].apply(ast.literal_eval)
df_test["answers"] = df_test["answers"].apply(ast.literal_eval)
print(f"Number of papers in the test sample:- {len(df_test)}")

```

# Generate Reranking Eval Dataset from the Eval data import pandas as pd import ast # Used to safely evaluate the string as a list # Load Eval Data df_test = pd.read_csv("/content/test.csv", index_col=0) df_test["questions"] = df_test["questions"].apply(ast.literal_eval) df_test["answers"] = df_test["answers"].apply(ast.literal_eval) print(f"Number of papers in the test sample:- {len(df_test)}")
```
Number of papers in the test sample:- 80

```

In [ ]:
Copied!
```
from llama_index.core import Document

final_eval_data_list = []
for index, row in df_test.iterrows():
    documents = [Document(text=row["paper"])]
    query_list = row["questions"]
    local_eval_dataset = generate_ce_fine_tuning_dataset(
        documents=documents,
        questions_list=query_list,
        max_chunk_length=256,
        top_k=5,
    )
    relevant_query_list = []
    relevant_context_list = []

    for item in local_eval_dataset:
        if item.score == 1:
            relevant_query_list.append(item.query)
            relevant_context_list.append(item.context)

    if len(relevant_query_list) > 0:
        final_eval_data_list.append(
            {
                "paper": row["paper"],
                "questions": relevant_query_list,
                "context": relevant_context_list,
            }
        )

```

from llama_index.core import Document final_eval_data_list = [] for index, row in df_test.iterrows(): documents = [Document(text=row["paper"])] query_list = row["questions"] local_eval_dataset = generate_ce_fine_tuning_dataset( documents=documents, questions_list=query_list, max_chunk_length=256, top_k=5, ) relevant_query_list = [] relevant_context_list = [] for item in local_eval_dataset: if item.score == 1: relevant_query_list.append(item.query) relevant_context_list.append(item.context) if len(relevant_query_list) > 0: final_eval_data_list.append( { "paper": row["paper"], "questions": relevant_query_list, "context": relevant_context_list, } )
In [ ]:
Copied!
```
# Length of Reranking Eval Dataset
len(final_eval_data_list)

```

# Length of Reranking Eval Dataset len(final_eval_data_list)
Out[ ]:


In [ ]:
Copied!
```
# Save Reranking eval dataset
import pandas as pd

df_finetuning_dataset = pd.DataFrame(final_eval_data_list)
df_finetuning_dataset.to_csv("reranking_test.csv")

# The reranking dataset can be found at the below dropbox link
# https://www.dropbox.com/scl/fi/mruo5rm46k1acm1xnecev/reranking_test.csv?rlkey=hkniwowq0xrc3m0ywjhb2gf26&dl=0

```

# Save Reranking eval dataset import pandas as pd df_finetuning_dataset = pd.DataFrame(final_eval_data_list) df_finetuning_dataset.to_csv("reranking_test.csv") # The reranking dataset can be found at the below dropbox link # https://www.dropbox.com/scl/fi/mruo5rm46k1acm1xnecev/reranking_test.csv?rlkey=hkniwowq0xrc3m0ywjhb2gf26&dl=0
## Finetune Cross-Encoder¶
In [ ]:
Copied!
```
!pip install huggingface_hub --quiet

```

!pip install huggingface_hub --quiet
In [ ]:
Copied!
```
from huggingface_hub import notebook_login

notebook_login()

```

from huggingface_hub import notebook_login notebook_login()
```
VBox(children=(HTML(value='<center> <img\nsrc=https://huggingface.co/front/assets/huggingface_logo-noborder.sv…
```

In [ ]:
Copied!
```
from sentence_transformers import SentenceTransformer

# Initialise the cross-encoder fine-tuning engine
finetuning_engine = CrossEncoderFinetuneEngine(
    dataset=finetuning_dataset, epochs=2, batch_size=8
)

# Finetune the cross-encoder model
finetuning_engine.finetune()

```

from sentence_transformers import SentenceTransformer # Initialise the cross-encoder fine-tuning engine finetuning_engine = CrossEncoderFinetuneEngine( dataset=finetuning_dataset, epochs=2, batch_size=8 ) # Finetune the cross-encoder model finetuning_engine.finetune()
```
Epoch:   0%|          | 0/2 [00:00<?, ?it/s]
```

```
Iteration:   0%|          | 0/1460 [00:00<?, ?it/s]
```

```
Iteration:   0%|          | 0/1460 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
# Push model to HuggingFace Hub
finetuning_engine.push_to_hub(
    repo_id="bpHigh/Cross-Encoder-LLamaIndex-Demo-v2"
)

```

# Push model to HuggingFace Hub finetuning_engine.push_to_hub( repo_id="bpHigh/Cross-Encoder-LLamaIndex-Demo-v2" )
```
pytorch_model.bin:   0%|          | 0.00/134M [00:00<?, ?B/s]
```

## Reranking Evaluation¶
In [ ]:
Copied!
```
!pip install nest-asyncio --quiet

```

!pip install nest-asyncio --quiet
In [ ]:
Copied!
```
# attach to the same event-loop
import nest_asyncio

nest_asyncio.apply()

```

# attach to the same event-loop import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
# Download Reranking test data
!wget -O reranking_test.csv https://www.dropbox.com/scl/fi/mruo5rm46k1acm1xnecev/reranking_test.csv?rlkey=hkniwowq0xrc3m0ywjhb2gf26&dl=0

```

# Download Reranking test data !wget -O reranking_test.csv https://www.dropbox.com/scl/fi/mruo5rm46k1acm1xnecev/reranking_test.csv?rlkey=hkniwowq0xrc3m0ywjhb2gf26&dl=0
```
--2023-10-12 04:47:18--  https://www.dropbox.com/scl/fi/mruo5rm46k1acm1xnecev/reranking_test.csv?rlkey=hkniwowq0xrc3m0ywjhb2gf26
Resolving www.dropbox.com (www.dropbox.com)... 162.125.85.18, 2620:100:6035:18::a27d:5512
Connecting to www.dropbox.com (www.dropbox.com)|162.125.85.18|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: https://uc414efe80c7598407c86166866d.dl.dropboxusercontent.com/cd/0/inline/CFcxAwrNZkpcZLmEipK-DxnJF6BKMu8rKmoRp-FUoqRF83K1t0kG0OzBliY-8E7EmbRqkkRZENO4ayEUPgul8lzY7iyARc7kauQ4iHdGps9_Y4jHyuLstzxbVT1TDQyhotVUYWZ9uHNmDHI9UFWAKBVm/file# [following]
--2023-10-12 04:47:18--  https://uc414efe80c7598407c86166866d.dl.dropboxusercontent.com/cd/0/inline/CFcxAwrNZkpcZLmEipK-DxnJF6BKMu8rKmoRp-FUoqRF83K1t0kG0OzBliY-8E7EmbRqkkRZENO4ayEUPgul8lzY7iyARc7kauQ4iHdGps9_Y4jHyuLstzxbVT1TDQyhotVUYWZ9uHNmDHI9UFWAKBVm/file
Resolving uc414efe80c7598407c86166866d.dl.dropboxusercontent.com (uc414efe80c7598407c86166866d.dl.dropboxusercontent.com)... 162.125.80.15, 2620:100:6035:15::a27d:550f
Connecting to uc414efe80c7598407c86166866d.dl.dropboxusercontent.com (uc414efe80c7598407c86166866d.dl.dropboxusercontent.com)|162.125.80.15|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 967072 (944K) [text/plain]
Saving to: ‘reranking_test.csv’

reranking_test.csv  100%[===================>] 944.41K  3.55MB/s    in 0.3s    

2023-10-12 04:47:19 (3.55 MB/s) - ‘reranking_test.csv’ saved [967072/967072]


```

In [ ]:
Copied!
```
# Load Reranking Dataset
import pandas as pd
import ast

df_reranking = pd.read_csv("/content/reranking_test.csv", index_col=0)
df_reranking["questions"] = df_reranking["questions"].apply(ast.literal_eval)
df_reranking["context"] = df_reranking["context"].apply(ast.literal_eval)
print(f"Number of papers in the reranking eval dataset:- {len(df_reranking)}")

```

# Load Reranking Dataset import pandas as pd import ast df_reranking = pd.read_csv("/content/reranking_test.csv", index_col=0) df_reranking["questions"] = df_reranking["questions"].apply(ast.literal_eval) df_reranking["context"] = df_reranking["context"].apply(ast.literal_eval) print(f"Number of papers in the reranking eval dataset:- {len(df_reranking)}")
```
Number of papers in the reranking eval dataset:- 38

```

In [ ]:
Copied!
```
df_reranking.head(1)

```

df_reranking.head(1)
Out[ ]:
| paper | questions | context  
---|---|---|---  
0 | Identifying Condition-Action Statements in Med... | [What supervised machine learning models do th... | [Identifying Condition-Action Statements in Me...  
In [ ]:
Copied!
```
# We evaluate by calculating hits for each (question, context) pair,
# we retrieve top-k documents with the question, and
# it’s a hit if the results contain the context
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.llms.openai import OpenAI
from llama_index.core import Document
from llama_index.core import Settings

import os
import openai
import pandas as pd

os.environ["OPENAI_API_KEY"] = "sk-"
openai.api_key = os.environ["OPENAI_API_KEY"]

Settings.chunk_size = 256

rerank_base = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-12-v2", top_n=3
)

rerank_finetuned = SentenceTransformerRerank(
    model="bpHigh/Cross-Encoder-LLamaIndex-Demo-v2", top_n=3
)

```

# We evaluate by calculating hits for each (question, context) pair, # we retrieve top-k documents with the question, and # it’s a hit if the results contain the context from llama_index.core.postprocessor import SentenceTransformerRerank from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response from llama_index.core.retrievers import VectorIndexRetriever from llama_index.llms.openai import OpenAI from llama_index.core import Document from llama_index.core import Settings import os import openai import pandas as pd os.environ["OPENAI_API_KEY"] = "sk-" openai.api_key = os.environ["OPENAI_API_KEY"] Settings.chunk_size = 256 rerank_base = SentenceTransformerRerank( model="cross-encoder/ms-marco-MiniLM-L-12-v2", top_n=3 ) rerank_finetuned = SentenceTransformerRerank( model="bpHigh/Cross-Encoder-LLamaIndex-Demo-v2", top_n=3 )
```
Downloading (…)lve/main/config.json:   0%|          | 0.00/854 [00:00<?, ?B/s]
```

```
Downloading pytorch_model.bin:   0%|          | 0.00/134M [00:00<?, ?B/s]
```

```
Downloading (…)okenizer_config.json:   0%|          | 0.00/366 [00:00<?, ?B/s]
```

```
Downloading (…)solve/main/vocab.txt:   0%|          | 0.00/232k [00:00<?, ?B/s]
```

```
Downloading (…)/main/tokenizer.json:   0%|          | 0.00/712k [00:00<?, ?B/s]
```

```
Downloading (…)cial_tokens_map.json:   0%|          | 0.00/125 [00:00<?, ?B/s]
```

In [ ]:
Copied!
```
without_reranker_hits = 0
base_reranker_hits = 0
finetuned_reranker_hits = 0
total_number_of_context = 0
for index, row in df_reranking.iterrows():
    documents = [Document(text=row["paper"])]
    query_list = row["questions"]
    context_list = row["context"]

    assert len(query_list) == len(context_list)
    vector_index = VectorStoreIndex.from_documents(documents)

    retriever_without_reranker = vector_index.as_query_engine(
        similarity_top_k=3, response_mode="no_text"
    )
    retriever_with_base_reranker = vector_index.as_query_engine(
        similarity_top_k=8,
        response_mode="no_text",
        node_postprocessors=[rerank_base],
    )
    retriever_with_finetuned_reranker = vector_index.as_query_engine(
        similarity_top_k=8,
        response_mode="no_text",
        node_postprocessors=[rerank_finetuned],
    )

    for index in range(0, len(query_list)):
        query = query_list[index]
        context = context_list[index]
        total_number_of_context += 1

        response_without_reranker = retriever_without_reranker.query(query)
        without_reranker_nodes = response_without_reranker.source_nodes

        for node in without_reranker_nodes:
            if context in node.node.text or node.node.text in context:
                without_reranker_hits += 1

        response_with_base_reranker = retriever_with_base_reranker.query(query)
        with_base_reranker_nodes = response_with_base_reranker.source_nodes

        for node in with_base_reranker_nodes:
            if context in node.node.text or node.node.text in context:
                base_reranker_hits += 1

        response_with_finetuned_reranker = (
            retriever_with_finetuned_reranker.query(query)
        )
        with_finetuned_reranker_nodes = (
            response_with_finetuned_reranker.source_nodes
        )

        for node in with_finetuned_reranker_nodes:
            if context in node.node.text or node.node.text in context:
                finetuned_reranker_hits += 1

        assert (
            len(with_finetuned_reranker_nodes)
            == len(with_base_reranker_nodes)
            == len(without_reranker_nodes)
            == 3
        )

```

without_reranker_hits = 0 base_reranker_hits = 0 finetuned_reranker_hits = 0 total_number_of_context = 0 for index, row in df_reranking.iterrows(): documents = [Document(text=row["paper"])] query_list = row["questions"] context_list = row["context"] assert len(query_list) == len(context_list) vector_index = VectorStoreIndex.from_documents(documents) retriever_without_reranker = vector_index.as_query_engine( similarity_top_k=3, response_mode="no_text" ) retriever_with_base_reranker = vector_index.as_query_engine( similarity_top_k=8, response_mode="no_text", node_postprocessors=[rerank_base], ) retriever_with_finetuned_reranker = vector_index.as_query_engine( similarity_top_k=8, response_mode="no_text", node_postprocessors=[rerank_finetuned], ) for index in range(0, len(query_list)): query = query_list[index] context = context_list[index] total_number_of_context += 1 response_without_reranker = retriever_without_reranker.query(query) without_reranker_nodes = response_without_reranker.source_nodes for node in without_reranker_nodes: if context in node.node.text or node.node.text in context: without_reranker_hits += 1 response_with_base_reranker = retriever_with_base_reranker.query(query) with_base_reranker_nodes = response_with_base_reranker.source_nodes for node in with_base_reranker_nodes: if context in node.node.text or node.node.text in context: base_reranker_hits += 1 response_with_finetuned_reranker = ( retriever_with_finetuned_reranker.query(query) ) with_finetuned_reranker_nodes = ( response_with_finetuned_reranker.source_nodes ) for node in with_finetuned_reranker_nodes: if context in node.node.text or node.node.text in context: finetuned_reranker_hits += 1 assert ( len(with_finetuned_reranker_nodes) == len(with_base_reranker_nodes) == len(without_reranker_nodes) == 3 )
### Results¶
As we can see below we get more hits with finetuned_cross_encoder compared to other options.
In [ ]:
Copied!
```
without_reranker_scores = [without_reranker_hits]
base_reranker_scores = [base_reranker_hits]
finetuned_reranker_scores = [finetuned_reranker_hits]
reranker_eval_dict = {
    "Metric": "Hits",
    "OpenAI_Embeddings": without_reranker_scores,
    "Base_cross_encoder": base_reranker_scores,
    "Finetuned_cross_encoder": finetuned_reranker_hits,
    "Total Relevant Context": total_number_of_context,
}
df_reranker_eval_results = pd.DataFrame(reranker_eval_dict)
display(df_reranker_eval_results)

```

without_reranker_scores = [without_reranker_hits] base_reranker_scores = [base_reranker_hits] finetuned_reranker_scores = [finetuned_reranker_hits] reranker_eval_dict = { "Metric": "Hits", "OpenAI_Embeddings": without_reranker_scores, "Base_cross_encoder": base_reranker_scores, "Finetuned_cross_encoder": finetuned_reranker_hits, "Total Relevant Context": total_number_of_context, } df_reranker_eval_results = pd.DataFrame(reranker_eval_dict) display(df_reranker_eval_results)
| Metric | OpenAI_Embeddings | Base_cross_encoder | Finetuned_cross_encoder | Total Relevant Context  
---|---|---|---|---|---  
0 | Hits | 30 | 34 | 37 | 85  
## RAG Evaluation¶
In [ ]:
Copied!
```
# Download RAG Eval test data
!wget -O test.csv https://www.dropbox.com/scl/fi/3lmzn6714oy358mq0vawm/test.csv?rlkey=yz16080te4van7fvnksi9kaed&dl=0

```

# Download RAG Eval test data !wget -O test.csv https://www.dropbox.com/scl/fi/3lmzn6714oy358mq0vawm/test.csv?rlkey=yz16080te4van7fvnksi9kaed&dl=0
```
--2023-10-12 04:47:36--  https://www.dropbox.com/scl/fi/3lmzn6714oy358mq0vawm/test.csv?rlkey=yz16080te4van7fvnksi9kaed
Resolving www.dropbox.com (www.dropbox.com)... 162.125.85.18, 2620:100:6035:18::a27d:5512
Connecting to www.dropbox.com (www.dropbox.com)|162.125.85.18|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: https://ucb6087b1b853dad24e8201987fc.dl.dropboxusercontent.com/cd/0/inline/CFfI9UezsVwFpN4CHgYrSFveuNE01DfczDaeFGZO-Ud5VdDRff1LNG7hEhkBZwVljuRde-EZU336ASpnZs32qVePvpQEFnKB2SeplFpMt50G0m5IZepyV6pYPbNAhm0muYE_rjhlolHxRUQP_iaJBX9z/file# [following]
--2023-10-12 04:47:38--  https://ucb6087b1b853dad24e8201987fc.dl.dropboxusercontent.com/cd/0/inline/CFfI9UezsVwFpN4CHgYrSFveuNE01DfczDaeFGZO-Ud5VdDRff1LNG7hEhkBZwVljuRde-EZU336ASpnZs32qVePvpQEFnKB2SeplFpMt50G0m5IZepyV6pYPbNAhm0muYE_rjhlolHxRUQP_iaJBX9z/file
Resolving ucb6087b1b853dad24e8201987fc.dl.dropboxusercontent.com (ucb6087b1b853dad24e8201987fc.dl.dropboxusercontent.com)... 162.125.80.15, 2620:100:6035:15::a27d:550f
Connecting to ucb6087b1b853dad24e8201987fc.dl.dropboxusercontent.com (ucb6087b1b853dad24e8201987fc.dl.dropboxusercontent.com)|162.125.80.15|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1821706 (1.7M) [text/plain]
Saving to: ‘test.csv’

test.csv            100%[===================>]   1.74M  6.37MB/s    in 0.3s    

2023-10-12 04:47:38 (6.37 MB/s) - ‘test.csv’ saved [1821706/1821706]


```

In [ ]:
Copied!
```
import pandas as pd
import ast  # Used to safely evaluate the string as a list

# Load Eval Data
df_test = pd.read_csv("/content/test.csv", index_col=0)

df_test["questions"] = df_test["questions"].apply(ast.literal_eval)
df_test["answers"] = df_test["answers"].apply(ast.literal_eval)
print(f"Number of papers in the test sample:- {len(df_test)}")

```

import pandas as pd import ast # Used to safely evaluate the string as a list # Load Eval Data df_test = pd.read_csv("/content/test.csv", index_col=0) df_test["questions"] = df_test["questions"].apply(ast.literal_eval) df_test["answers"] = df_test["answers"].apply(ast.literal_eval) print(f"Number of papers in the test sample:- {len(df_test)}")
```
Number of papers in the test sample:- 80

```

In [ ]:
Copied!
```
# Look at one sample of eval data which has a research paper questions on it and the respective reference answers
df_test.head(1)

```

# Look at one sample of eval data which has a research paper questions on it and the respective reference answers df_test.head(1)
Out[ ]:
| paper | questions | answers  
---|---|---|---  
0 | Identifying Condition-Action Statements in Med... | [What supervised machine learning models do th... | [Unacceptable, Unacceptable, 1470 sentences, U...  
### Baseline Evaluation¶
Just using OpenAI Embeddings for retrieval without any re-ranker
#### Eval Method:-¶
  1. Iterate over each row of the test dataset:-
    1. For the current row being iterated, create a vector index using the paper document provided in the paper column of the dataset
    2. Query the vector index with a top_k value of top 3 nodes without any reranker
    3. Compare the generated answers with the reference answers of the respective sample using Pairwise Comparison Evaluator and add the scores to a list
  2. Repeat 1 until all the rows have been iterated
  3. Calculate avg scores over all samples/ rows


In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response
from llama_index.llms.openai import OpenAI
from llama_index.core import Document
from llama_index.core.evaluation import PairwiseComparisonEvaluator
from llama_index.core.evaluation.eval_utils import (
    get_responses,
    get_results_df,
)

import os
import openai
import pandas as pd

os.environ["OPENAI_API_KEY"] = "sk-"
openai.api_key = os.environ["OPENAI_API_KEY"]

gpt4 = OpenAI(temperature=0, model="gpt-4")

evaluator_gpt4_pairwise = PairwiseComparisonEvaluator(llm=gpt4)

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response from llama_index.llms.openai import OpenAI from llama_index.core import Document from llama_index.core.evaluation import PairwiseComparisonEvaluator from llama_index.core.evaluation.eval_utils import ( get_responses, get_results_df, ) import os import openai import pandas as pd os.environ["OPENAI_API_KEY"] = "sk-" openai.api_key = os.environ["OPENAI_API_KEY"] gpt4 = OpenAI(temperature=0, model="gpt-4") evaluator_gpt4_pairwise = PairwiseComparisonEvaluator(llm=gpt4)
In [ ]:
Copied!
```
pairwise_scores_list = []

no_reranker_dict_list = []


# Iterate over the rows of the dataset
for index, row in df_test.iterrows():
    documents = [Document(text=row["paper"])]
    query_list = row["questions"]
    reference_answers_list = row["answers"]
    number_of_accepted_queries = 0
    # Create vector index for the current row being iterated
    vector_index = VectorStoreIndex.from_documents(documents)

    # Query the vector index with a top_k value of top 3 documents without any reranker
    query_engine = vector_index.as_query_engine(similarity_top_k=3)

    assert len(query_list) == len(reference_answers_list)
    pairwise_local_score = 0

    for index in range(0, len(query_list)):
        query = query_list[index]
        reference = reference_answers_list[index]

        if reference != "Unacceptable":
            number_of_accepted_queries += 1

            response = str(query_engine.query(query))

            no_reranker_dict = {
                "query": query,
                "response": response,
                "reference": reference,
            }
            no_reranker_dict_list.append(no_reranker_dict)

            # Compare the generated answers with the reference answers of the respective sample using
            # Pairwise Comparison Evaluator and add the scores to a list

            pairwise_eval_result = await evaluator_gpt4_pairwise.aevaluate(
                query, response=response, reference=reference
            )

            pairwise_score = pairwise_eval_result.score

            pairwise_local_score += pairwise_score

        else:
            pass

    if number_of_accepted_queries > 0:
        avg_pairwise_local_score = (
            pairwise_local_score / number_of_accepted_queries
        )
        pairwise_scores_list.append(avg_pairwise_local_score)


overal_pairwise_average_score = sum(pairwise_scores_list) / len(
    pairwise_scores_list
)

df_responses = pd.DataFrame(no_reranker_dict_list)
df_responses.to_csv("No_Reranker_Responses.csv")

```

pairwise_scores_list = [] no_reranker_dict_list = [] # Iterate over the rows of the dataset for index, row in df_test.iterrows(): documents = [Document(text=row["paper"])] query_list = row["questions"] reference_answers_list = row["answers"] number_of_accepted_queries = 0 # Create vector index for the current row being iterated vector_index = VectorStoreIndex.from_documents(documents) # Query the vector index with a top_k value of top 3 documents without any reranker query_engine = vector_index.as_query_engine(similarity_top_k=3) assert len(query_list) == len(reference_answers_list) pairwise_local_score = 0 for index in range(0, len(query_list)): query = query_list[index] reference = reference_answers_list[index] if reference != "Unacceptable": number_of_accepted_queries += 1 response = str(query_engine.query(query)) no_reranker_dict = { "query": query, "response": response, "reference": reference, } no_reranker_dict_list.append(no_reranker_dict) # Compare the generated answers with the reference answers of the respective sample using # Pairwise Comparison Evaluator and add the scores to a list pairwise_eval_result = await evaluator_gpt4_pairwise.aevaluate( query, response=response, reference=reference ) pairwise_score = pairwise_eval_result.score pairwise_local_score += pairwise_score else: pass if number_of_accepted_queries > 0: avg_pairwise_local_score = ( pairwise_local_score / number_of_accepted_queries ) pairwise_scores_list.append(avg_pairwise_local_score) overal_pairwise_average_score = sum(pairwise_scores_list) / len( pairwise_scores_list ) df_responses = pd.DataFrame(no_reranker_dict_list) df_responses.to_csv("No_Reranker_Responses.csv")
In [ ]:
Copied!
```
results_dict = {
    "name": ["Without Reranker"],
    "pairwise score": [overal_pairwise_average_score],
}
results_df = pd.DataFrame(results_dict)
display(results_df)

```

results_dict = { "name": ["Without Reranker"], "pairwise score": [overal_pairwise_average_score], } results_df = pd.DataFrame(results_dict) display(results_df)
| name | pairwise score  
---|---|---  
0 | Without Reranker | 0.553788  
### Evaluate with base reranker¶
OpenAI Embeddings + `cross-encoder/ms-marco-MiniLM-L-12-v2` as reranker
#### Eval Method:-¶
  1. Iterate over each row of the test dataset:-
    1. For the current row being iterated, create a vector index using the paper document provided in the paper column of the dataset
    2. Query the vector index with a top_k value of top 5 nodes.
    3. Use cross-encoder/ms-marco-MiniLM-L-12-v2 as a reranker as a NodePostprocessor to get top_k value of top 3 nodes out of the 8 nodes
    4. Compare the generated answers with the reference answers of the respective sample using Pairwise Comparison Evaluator and add the scores to a list
  2. Repeat 1 until all the rows have been iterated
  3. Calculate avg scores over all samples/ rows


In [ ]:
Copied!
```
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response
from llama_index.llms.openai import OpenAI
from llama_index.core import Document
from llama_index.core.evaluation import PairwiseComparisonEvaluator
import os
import openai

os.environ["OPENAI_API_KEY"] = "sk-"
openai.api_key = os.environ["OPENAI_API_KEY"]

rerank = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-12-v2", top_n=3
)

gpt4 = OpenAI(temperature=0, model="gpt-4")

evaluator_gpt4_pairwise = PairwiseComparisonEvaluator(llm=gpt4)

```

from llama_index.core.postprocessor import SentenceTransformerRerank from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response from llama_index.llms.openai import OpenAI from llama_index.core import Document from llama_index.core.evaluation import PairwiseComparisonEvaluator import os import openai os.environ["OPENAI_API_KEY"] = "sk-" openai.api_key = os.environ["OPENAI_API_KEY"] rerank = SentenceTransformerRerank( model="cross-encoder/ms-marco-MiniLM-L-12-v2", top_n=3 ) gpt4 = OpenAI(temperature=0, model="gpt-4") evaluator_gpt4_pairwise = PairwiseComparisonEvaluator(llm=gpt4)
```
Downloading (…)lve/main/config.json:   0%|          | 0.00/791 [00:00<?, ?B/s]
```

```
Downloading pytorch_model.bin:   0%|          | 0.00/134M [00:00<?, ?B/s]
```

```
Downloading (…)okenizer_config.json:   0%|          | 0.00/316 [00:00<?, ?B/s]
```

```
Downloading (…)solve/main/vocab.txt:   0%|          | 0.00/232k [00:00<?, ?B/s]
```

```
Downloading (…)cial_tokens_map.json:   0%|          | 0.00/112 [00:00<?, ?B/s]
```

In [ ]:
Copied!
```
pairwise_scores_list = []

base_reranker_dict_list = []


# Iterate over the rows of the dataset
for index, row in df_test.iterrows():
    documents = [Document(text=row["paper"])]
    query_list = row["questions"]
    reference_answers_list = row["answers"]

    number_of_accepted_queries = 0
    # Create vector index for the current row being iterated
    vector_index = VectorStoreIndex.from_documents(documents)

    # Query the vector index with a top_k value of top 8 nodes with reranker
    # as cross-encoder/ms-marco-MiniLM-L-12-v2
    query_engine = vector_index.as_query_engine(
        similarity_top_k=8, node_postprocessors=[rerank]
    )

    assert len(query_list) == len(reference_answers_list)
    pairwise_local_score = 0

    for index in range(0, len(query_list)):
        query = query_list[index]
        reference = reference_answers_list[index]

        if reference != "Unacceptable":
            number_of_accepted_queries += 1

            response = str(query_engine.query(query))

            base_reranker_dict = {
                "query": query,
                "response": response,
                "reference": reference,
            }
            base_reranker_dict_list.append(base_reranker_dict)

            # Compare the generated answers with the reference answers of the respective sample using
            # Pairwise Comparison Evaluator and add the scores to a list

            pairwise_eval_result = await evaluator_gpt4_pairwise.aevaluate(
                query=query, response=response, reference=reference
            )

            pairwise_score = pairwise_eval_result.score

            pairwise_local_score += pairwise_score

        else:
            pass

    if number_of_accepted_queries > 0:
        avg_pairwise_local_score = (
            pairwise_local_score / number_of_accepted_queries
        )
        pairwise_scores_list.append(avg_pairwise_local_score)

overal_pairwise_average_score = sum(pairwise_scores_list) / len(
    pairwise_scores_list
)

df_responses = pd.DataFrame(base_reranker_dict_list)
df_responses.to_csv("Base_Reranker_Responses.csv")

```

pairwise_scores_list = [] base_reranker_dict_list = [] # Iterate over the rows of the dataset for index, row in df_test.iterrows(): documents = [Document(text=row["paper"])] query_list = row["questions"] reference_answers_list = row["answers"] number_of_accepted_queries = 0 # Create vector index for the current row being iterated vector_index = VectorStoreIndex.from_documents(documents) # Query the vector index with a top_k value of top 8 nodes with reranker # as cross-encoder/ms-marco-MiniLM-L-12-v2 query_engine = vector_index.as_query_engine( similarity_top_k=8, node_postprocessors=[rerank] ) assert len(query_list) == len(reference_answers_list) pairwise_local_score = 0 for index in range(0, len(query_list)): query = query_list[index] reference = reference_answers_list[index] if reference != "Unacceptable": number_of_accepted_queries += 1 response = str(query_engine.query(query)) base_reranker_dict = { "query": query, "response": response, "reference": reference, } base_reranker_dict_list.append(base_reranker_dict) # Compare the generated answers with the reference answers of the respective sample using # Pairwise Comparison Evaluator and add the scores to a list pairwise_eval_result = await evaluator_gpt4_pairwise.aevaluate( query=query, response=response, reference=reference ) pairwise_score = pairwise_eval_result.score pairwise_local_score += pairwise_score else: pass if number_of_accepted_queries > 0: avg_pairwise_local_score = ( pairwise_local_score / number_of_accepted_queries ) pairwise_scores_list.append(avg_pairwise_local_score) overal_pairwise_average_score = sum(pairwise_scores_list) / len( pairwise_scores_list ) df_responses = pd.DataFrame(base_reranker_dict_list) df_responses.to_csv("Base_Reranker_Responses.csv")
In [ ]:
Copied!
```
results_dict = {
    "name": ["With base cross-encoder/ms-marco-MiniLM-L-12-v2 as Reranker"],
    "pairwise score": [overal_pairwise_average_score],
}
results_df = pd.DataFrame(results_dict)
display(results_df)

```

results_dict = { "name": ["With base cross-encoder/ms-marco-MiniLM-L-12-v2 as Reranker"], "pairwise score": [overal_pairwise_average_score], } results_df = pd.DataFrame(results_dict) display(results_df)
| name | pairwise score  
---|---|---  
0 | With base cross-encoder/ms-marco-MiniLM-L-12-v... | 0.556818  
### Evaluate with Fine-Tuned re-ranker¶
OpenAI Embeddings + `bpHigh/Cross-Encoder-LLamaIndex-Demo-v2` as reranker
#### Eval Method:-¶
  1. Iterate over each row of the test dataset:-
    1. For the current row being iterated, create a vector index using the paper document provided in the paper column of the dataset
    2. Query the vector index with a top_k value of top 5 nodes.
    3. Use finetuned version of cross-encoder/ms-marco-MiniLM-L-12-v2 saved as bpHigh/Cross-Encoder-LLamaIndex-Demo as a reranker as a NodePostprocessor to get top_k value of top 3 nodes out of the 8 nodes
    4. Compare the generated answers with the reference answers of the respective sample using Pairwise Comparison Evaluator and add the scores to a list
  2. Repeat 1 until all the rows have been iterated
  3. Calculate avg scores over all samples/ rows


In [ ]:
Copied!
```
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response
from llama_index.llms.openai import OpenAI
from llama_index.core import Document
from llama_index.core.evaluation import PairwiseComparisonEvaluator
import os
import openai

os.environ["OPENAI_API_KEY"] = "sk-"
openai.api_key = os.environ["OPENAI_API_KEY"]

rerank = SentenceTransformerRerank(
    model="bpHigh/Cross-Encoder-LLamaIndex-Demo-v2", top_n=3
)


gpt4 = OpenAI(temperature=0, model="gpt-4")

evaluator_gpt4_pairwise = PairwiseComparisonEvaluator(llm=gpt4)

```

from llama_index.core.postprocessor import SentenceTransformerRerank from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response from llama_index.llms.openai import OpenAI from llama_index.core import Document from llama_index.core.evaluation import PairwiseComparisonEvaluator import os import openai os.environ["OPENAI_API_KEY"] = "sk-" openai.api_key = os.environ["OPENAI_API_KEY"] rerank = SentenceTransformerRerank( model="bpHigh/Cross-Encoder-LLamaIndex-Demo-v2", top_n=3 ) gpt4 = OpenAI(temperature=0, model="gpt-4") evaluator_gpt4_pairwise = PairwiseComparisonEvaluator(llm=gpt4)
In [ ]:
Copied!
```
pairwise_scores_list = []


finetuned_reranker_dict_list = []

# Iterate over the rows of the dataset
for index, row in df_test.iterrows():
    documents = [Document(text=row["paper"])]
    query_list = row["questions"]
    reference_answers_list = row["answers"]

    number_of_accepted_queries = 0
    # Create vector index for the current row being iterated
    vector_index = VectorStoreIndex.from_documents(documents)

    # Query the vector index with a top_k value of top 8 nodes with reranker
    # as cross-encoder/ms-marco-MiniLM-L-12-v2
    query_engine = vector_index.as_query_engine(
        similarity_top_k=8, node_postprocessors=[rerank]
    )

    assert len(query_list) == len(reference_answers_list)
    pairwise_local_score = 0

    for index in range(0, len(query_list)):
        query = query_list[index]
        reference = reference_answers_list[index]

        if reference != "Unacceptable":
            number_of_accepted_queries += 1

            response = str(query_engine.query(query))

            finetuned_reranker_dict = {
                "query": query,
                "response": response,
                "reference": reference,
            }
            finetuned_reranker_dict_list.append(finetuned_reranker_dict)

            # Compare the generated answers with the reference answers of the respective sample using
            # Pairwise Comparison Evaluator and add the scores to a list

            pairwise_eval_result = await evaluator_gpt4_pairwise.aevaluate(
                query, response=response, reference=reference
            )

            pairwise_score = pairwise_eval_result.score

            pairwise_local_score += pairwise_score

        else:
            pass

    if number_of_accepted_queries > 0:
        avg_pairwise_local_score = (
            pairwise_local_score / number_of_accepted_queries
        )
        pairwise_scores_list.append(avg_pairwise_local_score)

overal_pairwise_average_score = sum(pairwise_scores_list) / len(
    pairwise_scores_list
)
df_responses = pd.DataFrame(finetuned_reranker_dict_list)
df_responses.to_csv("Finetuned_Reranker_Responses.csv")

```

pairwise_scores_list = [] finetuned_reranker_dict_list = [] # Iterate over the rows of the dataset for index, row in df_test.iterrows(): documents = [Document(text=row["paper"])] query_list = row["questions"] reference_answers_list = row["answers"] number_of_accepted_queries = 0 # Create vector index for the current row being iterated vector_index = VectorStoreIndex.from_documents(documents) # Query the vector index with a top_k value of top 8 nodes with reranker # as cross-encoder/ms-marco-MiniLM-L-12-v2 query_engine = vector_index.as_query_engine( similarity_top_k=8, node_postprocessors=[rerank] ) assert len(query_list) == len(reference_answers_list) pairwise_local_score = 0 for index in range(0, len(query_list)): query = query_list[index] reference = reference_answers_list[index] if reference != "Unacceptable": number_of_accepted_queries += 1 response = str(query_engine.query(query)) finetuned_reranker_dict = { "query": query, "response": response, "reference": reference, } finetuned_reranker_dict_list.append(finetuned_reranker_dict) # Compare the generated answers with the reference answers of the respective sample using # Pairwise Comparison Evaluator and add the scores to a list pairwise_eval_result = await evaluator_gpt4_pairwise.aevaluate( query, response=response, reference=reference ) pairwise_score = pairwise_eval_result.score pairwise_local_score += pairwise_score else: pass if number_of_accepted_queries > 0: avg_pairwise_local_score = ( pairwise_local_score / number_of_accepted_queries ) pairwise_scores_list.append(avg_pairwise_local_score) overal_pairwise_average_score = sum(pairwise_scores_list) / len( pairwise_scores_list ) df_responses = pd.DataFrame(finetuned_reranker_dict_list) df_responses.to_csv("Finetuned_Reranker_Responses.csv")
In [ ]:
Copied!
```
results_dict = {
    "name": ["With fine-tuned cross-encoder/ms-marco-MiniLM-L-12-v2"],
    "pairwise score": [overal_pairwise_average_score],
}
results_df = pd.DataFrame(results_dict)
display(results_df)

```

results_dict = { "name": ["With fine-tuned cross-encoder/ms-marco-MiniLM-L-12-v2"], "pairwise score": [overal_pairwise_average_score], } results_df = pd.DataFrame(results_dict) display(results_df)
| name | pairwise score  
---|---|---  
0 | With fine-tuned cross-encoder/ms-marco-MiniLM-... | 0.6  
### Results¶
As we can see we get the highest pairwise score with finetuned cross-encoder.
Although I would like to point that the reranking eval based on hits is a more robust metric compared to pairwise comparision evaluator as I have seen inconsistencies with the scores and there are also many inherent biases present when evaluating using GPT-4
