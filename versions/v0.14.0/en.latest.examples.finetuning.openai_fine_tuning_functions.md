![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Fine Tuning with Function Calling¶
In this notebook, we walk through how to fine-tune gpt-3.5-turbo with function calls. The primary use case here is structured data extraction. Our main focus is distilling GPT-4 outputs to help improve gpt-3.5-turbo function calling capabilities.
We will walk through some examples, from simple to advanced:
  1. Fine-tuning on some toy messages/structured outputs logged through our OpenAI Pydantic Program object.
  2. Fine-tuning on context-augmented queries/structured outputs over an entire document corpus. Use this in a RAG system.


In [ ]:
Copied!
```
%pip install llama-index-finetuning
%pip install llama-index-llms-openai
%pip install llama-index-finetuning-callbacks
%pip install llama-index-readers-file pymupdf
%pip install llama-index-program-openai

```

%pip install llama-index-finetuning %pip install llama-index-llms-openai %pip install llama-index-finetuning-callbacks %pip install llama-index-readers-file pymupdf %pip install llama-index-program-openai
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
## Fine-tuning Using GPT-4 Pydantic Programs¶
In this section we show how to log inputs/outputs through our low-level Pydantic Program module. We use that dataset to fine-tune an LLM.
### Defining Pydantic Model + Program¶
Here, we define the GPT-4 powered function calling program that will generate structured outputs into a Pydantic object (an Album).
In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram
from pydantic import BaseModel
from llama_index.llms.openai import OpenAI
from llama_index.finetuning.callbacks import OpenAIFineTuningHandler
from llama_index.core.callbacks import CallbackManager
from typing import List


class Song(BaseModel):
    """Data model for a song."""

    title: str
    length_seconds: int


class Album(BaseModel):
    """Data model for an album."""

    name: str
    artist: str
    songs: List[Song]


finetuning_handler = OpenAIFineTuningHandler()
callback_manager = CallbackManager([finetuning_handler])

llm = OpenAI(model="gpt-4", callback_manager=callback_manager)


prompt_template_str = """\
Generate an example album, with an artist and a list of songs. \
Using the movie {movie_name} as inspiration.\
"""
program = OpenAIPydanticProgram.from_defaults(
    output_cls=Album,
    prompt_template_str=prompt_template_str,
    llm=llm,
    verbose=False,
)

```

from llama_index.program.openai import OpenAIPydanticProgram from pydantic import BaseModel from llama_index.llms.openai import OpenAI from llama_index.finetuning.callbacks import OpenAIFineTuningHandler from llama_index.core.callbacks import CallbackManager from typing import List class Song(BaseModel): """Data model for a song.""" title: str length_seconds: int class Album(BaseModel): """Data model for an album.""" name: str artist: str songs: List[Song] finetuning_handler = OpenAIFineTuningHandler() callback_manager = CallbackManager([finetuning_handler]) llm = OpenAI(model="gpt-4", callback_manager=callback_manager) prompt_template_str = """\ Generate an example album, with an artist and a list of songs. \ Using the movie {movie_name} as inspiration.\ """ program = OpenAIPydanticProgram.from_defaults( output_cls=Album, prompt_template_str=prompt_template_str, llm=llm, verbose=False, )
### Log Inputs/Outputs¶
We define some sample movie names as inputs and log the outputs through the function calling program.
In [ ]:
Copied!
```
# NOTE: we need >= 10 movies to use OpenAI fine-tuning
movie_names = [
    "The Shining",
    "The Departed",
    "Titanic",
    "Goodfellas",
    "Pretty Woman",
    "Home Alone",
    "Caged Fury",
    "Edward Scissorhands",
    "Total Recall",
    "Ghost",
    "Tremors",
    "RoboCop",
    "Rocky V",
]

```

# NOTE: we need >= 10 movies to use OpenAI fine-tuning movie_names = [ "The Shining", "The Departed", "Titanic", "Goodfellas", "Pretty Woman", "Home Alone", "Caged Fury", "Edward Scissorhands", "Total Recall", "Ghost", "Tremors", "RoboCop", "Rocky V", ]
In [ ]:
Copied!
```
from tqdm.notebook import tqdm

for movie_name in tqdm(movie_names):
    output = program(movie_name=movie_name)
    print(output.json())

```

from tqdm.notebook import tqdm for movie_name in tqdm(movie_names): output = program(movie_name=movie_name) print(output.json())
```
  0%|          | 0/13 [00:00<?, ?it/s]
```

```
{"name": "The Shining", "artist": "Various Artists", "songs": [{"title": "Main Title", "length_seconds": 180}, {"title": "Opening Credits", "length_seconds": 120}, {"title": "The Overlook Hotel", "length_seconds": 240}, {"title": "Redrum", "length_seconds": 150}, {"title": "Here's Johnny!", "length_seconds": 200}]}
{"name": "The Departed Soundtrack", "artist": "Various Artists", "songs": [{"title": "Gimme Shelter", "length_seconds": 272}, {"title": "Comfortably Numb", "length_seconds": 383}, {"title": "I'm Shipping Up to Boston", "length_seconds": 166}, {"title": "Sweet Dreams (Are Made of This)", "length_seconds": 216}, {"title": "I'm Shipping Up to Boston (Instrumental)", "length_seconds": 166}, {"title": "The Departed Tango", "length_seconds": 123}, {"title": "Thief's Theme", "length_seconds": 201}, {"title": "Well Well Well", "length_seconds": 126}, {"title": "Comfortably Numb (Live)", "length_seconds": 383}, {"title": "Sail On, Sailor", "length_seconds": 181}]}
{"name": "Titanic Soundtrack", "artist": "James Horner", "songs": [{"title": "My Heart Will Go On", "length_seconds": 273}, {"title": "Rose", "length_seconds": 120}, {"title": "Hymn to the Sea", "length_seconds": 365}, {"title": "Southampton", "length_seconds": 180}, {"title": "Take Her to Sea, Mr. Murdoch", "length_seconds": 150}]}
{"name": "Goodfellas Soundtrack", "artist": "Various Artists", "songs": [{"title": "Rags to Riches", "length_seconds": 180}, {"title": "Gimme Shelter", "length_seconds": 270}, {"title": "Layla", "length_seconds": 270}, {"title": "Jump into the Fire", "length_seconds": 240}, {"title": "Atlantis", "length_seconds": 180}, {"title": "Beyond the Sea", "length_seconds": 180}, {"title": "Sunshine of Your Love", "length_seconds": 240}, {"title": "Mannish Boy", "length_seconds": 240}, {"title": "Layla (Piano Exit)", "length_seconds": 120}]}
{"name": "Pretty Woman Soundtrack", "artist": "Various Artists", "songs": [{"title": "Oh, Pretty Woman", "length_seconds": 178}, {"title": "King of Wishful Thinking", "length_seconds": 253}, {"title": "It Must Have Been Love", "length_seconds": 250}, {"title": "Show Me Your Soul", "length_seconds": 285}, {"title": "No Explanation", "length_seconds": 244}]}
{"name": "Home Alone Soundtrack", "artist": "John Williams", "songs": [{"title": "Somewhere in My Memory", "length_seconds": 180}, {"title": "Holiday Flight", "length_seconds": 120}, {"title": "The House", "length_seconds": 150}, {"title": "Star of Bethlehem", "length_seconds": 135}, {"title": "Setting the Trap", "length_seconds": 165}, {"title": "The Attack on the House", "length_seconds": 200}, {"title": "Mom Returns and Finale", "length_seconds": 240}]}
{"name": "Caged Fury", "artist": "The Fury Band", "songs": [{"title": "Caged Fury", "length_seconds": 240}, {"title": "Prison Break", "length_seconds": 180}, {"title": "Behind Bars", "length_seconds": 210}, {"title": "Escape Plan", "length_seconds": 195}, {"title": "Fight for Freedom", "length_seconds": 220}]}
{"name": "Edward Scissorhands Soundtrack", "artist": "Danny Elfman", "songs": [{"title": "Introduction", "length_seconds": 120}, {"title": "Ice Dance", "length_seconds": 180}, {"title": "Edwardo the Barber", "length_seconds": 150}, {"title": "The Grand Finale", "length_seconds": 240}]}
{"name": "Total Recall", "artist": "Various Artists", "songs": [{"title": "Recall", "length_seconds": 240}, {"title": "Mars", "length_seconds": 180}, {"title": "Memory", "length_seconds": 210}, {"title": "Rebellion", "length_seconds": 300}, {"title": "Escape", "length_seconds": 270}]}
{"name": "Ghost", "artist": "Various Artists", "songs": [{"title": "Unchained Melody", "length_seconds": 218}, {"title": "Oh My Love", "length_seconds": 156}, {"title": "Ditto's Theme", "length_seconds": 92}, {"title": "Love Inside", "length_seconds": 180}, {"title": "Ghostly Encounter", "length_seconds": 120}]}
{"name": "Tremors Soundtrack", "artist": "Various Artists", "songs": [{"title": "Main Theme", "length_seconds": 180}, {"title": "Graboids Attack", "length_seconds": 240}, {"title": "Val and Earl's Theme", "length_seconds": 200}, {"title": "Burt's Arsenal", "length_seconds": 220}, {"title": "Nest of the Graboids", "length_seconds": 190}]}
{"name": "RoboCop: The Soundtrack", "artist": "Various Artists", "songs": [{"title": "Main Theme", "length_seconds": 180}, {"title": "Murphy's Death", "length_seconds": 240}, {"title": "RoboCop's Training", "length_seconds": 210}, {"title": "ED-209", "length_seconds": 195}, {"title": "Clarence Boddicker", "length_seconds": 220}, {"title": "RoboCop Saves the Day", "length_seconds": 240}, {"title": "RoboCop's Theme", "length_seconds": 180}]}
{"name": "Rocky V", "artist": "Various Artists", "songs": [{"title": "Measure of a Man", "length_seconds": 240}, {"title": "Can't Stop the Fire", "length_seconds": 210}, {"title": "Go for It!", "length_seconds": 180}, {"title": "Take You Back (Home Sweet Home)", "length_seconds": 200}, {"title": "The Measure of a Man (Reprise)", "length_seconds": 120}]}

```

In [ ]:
Copied!
```
finetuning_handler.save_finetuning_events("mock_finetune_songs.jsonl")

```

finetuning_handler.save_finetuning_events("mock_finetune_songs.jsonl")
```
Wrote 14 examples to mock_finetune_songs.jsonl

```

In [ ]:
Copied!
```
!cat mock_finetune_songs.jsonl

```

!cat mock_finetune_songs.jsonl
### Fine-tune on the Dataset¶
We now define a fine-tuning engine and fine-tune on the mock dataset.
In [ ]:
Copied!
```
from llama_index.finetuning import OpenAIFinetuneEngine

finetune_engine = OpenAIFinetuneEngine(
    "gpt-3.5-turbo",
    "mock_finetune_songs.jsonl",
    # start_job_id="<start-job-id>"  # if you have an existing job, can specify id here
    validate_json=False,  # openai validate json code doesn't support function calling yet
)

```

from llama_index.finetuning import OpenAIFinetuneEngine finetune_engine = OpenAIFinetuneEngine( "gpt-3.5-turbo", "mock_finetune_songs.jsonl", # start_job_id="" # if you have an existing job, can specify id here validate_json=False, # openai validate json code doesn't support function calling yet )
In [ ]:
Copied!
```
finetune_engine.finetune()

```

finetune_engine.finetune()
In [ ]:
Copied!
```
finetune_engine.get_current_job()

```

finetune_engine.get_current_job()
Out[ ]:
```
<FineTuningJob fine_tuning.job id=ftjob-uJ9kQ9pI0p0YNatBDxF3VITv at 0x172a5c9a0> JSON: {
  "object": "fine_tuning.job",
  "id": "ftjob-uJ9kQ9pI0p0YNatBDxF3VITv",
  "model": "gpt-3.5-turbo-0613",
  "created_at": 1696463378,
  "finished_at": 1696463749,
  "fine_tuned_model": "ft:gpt-3.5-turbo-0613:llamaindex::8660TXqx",
  "organization_id": "org-1ZDAvajC6v2ZtAP9hLEIsXRz",
  "result_files": [
    "file-Hbpw15BAwyf3e4HK5Z9g4IK2"
  ],
  "status": "succeeded",
  "validation_file": null,
  "training_file": "file-MNh7snhv0triDIhsrErokSMY",
  "hyperparameters": {
    "n_epochs": 7
  },
  "trained_tokens": 22834,
  "error": null
}
```

### Try it Out!¶
We obtain the fine-tuned LLM and use it with the Pydantic program.
In [ ]:
Copied!
```
ft_llm = finetune_engine.get_finetuned_model(temperature=0.3)

```

ft_llm = finetune_engine.get_finetuned_model(temperature=0.3)
In [ ]:
Copied!
```
ft_program = OpenAIPydanticProgram.from_defaults(
    output_cls=Album,
    prompt_template_str=prompt_template_str,
    llm=ft_llm,
    verbose=False,
)

```

ft_program = OpenAIPydanticProgram.from_defaults( output_cls=Album, prompt_template_str=prompt_template_str, llm=ft_llm, verbose=False, )
In [ ]:
Copied!
```
ft_program(movie_name="Goodfellas")

```

ft_program(movie_name="Goodfellas")
Out[ ]:
```
Album(name='Goodfellas Soundtrack', artist='Various Artists', songs=[Song(title='Rags to Riches', length_seconds=180), Song(title='Gimme Shelter', length_seconds=270), Song(title='Layla', length_seconds=270), Song(title='Jump into the Fire', length_seconds=240), Song(title='Atlantis', length_seconds=180), Song(title='Beyond the Sea', length_seconds=180), Song(title='Sunshine of Your Love', length_seconds=240), Song(title='Mannish Boy', length_seconds=240), Song(title='Layla (Piano Exit)', length_seconds=120)])
```

## Fine-tuning Structured Outputs through a RAG System¶
A use case of function calling is to get structured outputs through a RAG system.
Here we show how to create a training dataset of context-augmented inputs + structured outputs over an unstructured document. We can then fine-tune the LLM and plug it into a RAG system to perform retrieval + output extraction.
In [ ]:
Copied!
```
!mkdir data && wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"

```

!mkdir data && wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"
```
--2023-10-04 23:46:36--  https://arxiv.org/pdf/2307.09288.pdf
Resolving arxiv.org (arxiv.org)... 128.84.21.199
Connecting to arxiv.org (arxiv.org)|128.84.21.199|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 13661300 (13M) [application/pdf]
Saving to: ‘data/llama2.pdf’

data/llama2.pdf     100%[===================>]  13.03M   229KB/s    in 45s     

2023-10-04 23:47:25 (298 KB/s) - ‘data/llama2.pdf’ saved [13661300/13661300]

```

In [ ]:
Copied!
```
from pydantic import Field
from typing import List


class Citation(BaseModel):
    """Citation class."""

    author: str = Field(
        ..., description="Inferred first author (usually last name"
    )
    year: int = Field(..., description="Inferred year")
    desc: str = Field(
        ...,
        description=(
            "Inferred description from the text of the work that the author is"
            " cited for"
        ),
    )


class Response(BaseModel):
    """List of author citations.

    Extracted over unstructured text.

    """

    citations: List[Citation] = Field(
        ...,
        description=(
            "List of author citations (organized by author, year, and"
            " description)."
        ),
    )

```

from pydantic import Field from typing import List class Citation(BaseModel): """Citation class.""" author: str = Field( ..., description="Inferred first author (usually last name" ) year: int = Field(..., description="Inferred year") desc: str = Field( ..., description=( "Inferred description from the text of the work that the author is" " cited for" ), ) class Response(BaseModel): """List of author citations. Extracted over unstructured text. """ citations: List[Citation] = Field( ..., description=( "List of author citations (organized by author, year, and" " description)." ), )
### Load Data + Setup¶
In [ ]:
Copied!
```
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter
from pathlib import Path

```

from llama_index.readers.file import PyMuPDFReader from llama_index.core import Document from llama_index.core.node_parser import SentenceSplitter from pathlib import Path
In [ ]:
Copied!
```
loader = PyMuPDFReader()
docs0 = loader.load(file_path=Path("./data/llama2.pdf"))

```

loader = PyMuPDFReader() docs0 = loader.load(file_path=Path("./data/llama2.pdf"))
In [ ]:
Copied!
```
doc_text = "\n\n".join([d.get_content() for d in docs0])
metadata = {
    "paper_title": "Llama 2: Open Foundation and Fine-Tuned Chat Models"
}
docs = [Document(text=doc_text, metadata=metadata)]

```

doc_text = "\n\n".join([d.get_content() for d in docs0]) metadata = { "paper_title": "Llama 2: Open Foundation and Fine-Tuned Chat Models" } docs = [Document(text=doc_text, metadata=metadata)]
In [ ]:
Copied!
```
chunk_size = 1024
node_parser = SentenceSplitter(chunk_size=chunk_size)
nodes = node_parser.get_nodes_from_documents(docs)

```

chunk_size = 1024 node_parser = SentenceSplitter(chunk_size=chunk_size) nodes = node_parser.get_nodes_from_documents(docs)
In [ ]:
Copied!
```
len(nodes)

```

len(nodes)
Out[ ]:


In [ ]:
Copied!
```
from llama_index.core import Settings

finetuning_handler = OpenAIFineTuningHandler()
callback_manager = CallbackManager([finetuning_handler])

Settings.chunk_size = chunk_size

gpt_4_llm = OpenAI(
    model="gpt-4-0613", temperature=0.3, callback_manager=callback_manager
)

gpt_35_llm = OpenAI(
    model="gpt-3.5-turbo-0613",
    temperature=0.3,
    callback_manager=callback_manager,
)

eval_llm = OpenAI(model="gpt-4-0613", temperature=0)

```

from llama_index.core import Settings finetuning_handler = OpenAIFineTuningHandler() callback_manager = CallbackManager([finetuning_handler]) Settings.chunk_size = chunk_size gpt_4_llm = OpenAI( model="gpt-4-0613", temperature=0.3, callback_manager=callback_manager ) gpt_35_llm = OpenAI( model="gpt-3.5-turbo-0613", temperature=0.3, callback_manager=callback_manager, ) eval_llm = OpenAI(model="gpt-4-0613", temperature=0)
### Generate Dataset¶
Here we show how to generate a training dataset over these unstructured chunks/nodes.
We generate questions to extract citations over different context. We run these questions through a GPT-4 RAG pipeline, extract structured outputs, and log inputs/outputs.
In [ ]:
Copied!
```
# setup dataset generator
from llama_index.core.evaluation import DatasetGenerator
from llama_index.core import SummaryIndex
from llama_index.core import PromptTemplate
from tqdm.notebook import tqdm
from tqdm.asyncio import tqdm_asyncio


fp = open("data/qa_pairs.jsonl", "w")

question_gen_prompt = PromptTemplate(
    """
{query_str}

Context:
{context_str}

Questions:
"""
)

question_gen_query = """\
Snippets from a research paper is given below. It contains citations.
Please generate questions from the text asking about these citations.

For instance, here are some sample questions:
Which citations correspond to related works on transformer models? 
Tell me about authors that worked on advancing RLHF.
Can you tell me citations corresponding to all computer vision works? \
"""

qr_pairs = []
node_questions_tasks = []
for idx, node in enumerate(nodes[:39]):
    num_questions = 1  # change this number to increase number of nodes
    dataset_generator = DatasetGenerator(
        [node],
        question_gen_query=question_gen_query,
        text_question_template=question_gen_prompt,
        llm=eval_llm,
        metadata_mode="all",
        num_questions_per_chunk=num_questions,
    )

    task = dataset_generator.agenerate_questions_from_nodes(num=num_questions)
    node_questions_tasks.append(task)
node_questions_lists = await tqdm_asyncio.gather(*node_questions_tasks)

```

# setup dataset generator from llama_index.core.evaluation import DatasetGenerator from llama_index.core import SummaryIndex from llama_index.core import PromptTemplate from tqdm.notebook import tqdm from tqdm.asyncio import tqdm_asyncio fp = open("data/qa_pairs.jsonl", "w") question_gen_prompt = PromptTemplate( """ {query_str} Context: {context_str} Questions: """ ) question_gen_query = """\ Snippets from a research paper is given below. It contains citations. Please generate questions from the text asking about these citations. For instance, here are some sample questions: Which citations correspond to related works on transformer models? Tell me about authors that worked on advancing RLHF. Can you tell me citations corresponding to all computer vision works? \ """ qr_pairs = [] node_questions_tasks = [] for idx, node in enumerate(nodes[:39]): num_questions = 1 # change this number to increase number of nodes dataset_generator = DatasetGenerator( [node], question_gen_query=question_gen_query, text_question_template=question_gen_prompt, llm=eval_llm, metadata_mode="all", num_questions_per_chunk=num_questions, ) task = dataset_generator.agenerate_questions_from_nodes(num=num_questions) node_questions_tasks.append(task) node_questions_lists = await tqdm_asyncio.gather(*node_questions_tasks)
In [ ]:
Copied!
```
node_questions_lists

```

node_questions_lists
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

gpt4_index = VectorStoreIndex(nodes=nodes)
gpt4_query_engine = gpt4_index.as_query_engine(
    output_cls=Response, similarity_top_k=1, llm=gpt_4_llm
)

```

from llama_index.core import VectorStoreIndex gpt4_index = VectorStoreIndex(nodes=nodes) gpt4_query_engine = gpt4_index.as_query_engine( output_cls=Response, similarity_top_k=1, llm=gpt_4_llm )
In [ ]:
Copied!
```
from json import JSONDecodeError

for idx, node in enumerate(tqdm(nodes[:39])):
    node_questions_0 = node_questions_lists[idx]
    for question in node_questions_0:
        try:
            # note: we don't need to use response, events are logged through fine-tuning handler
            gpt4_query_engine.query(question)
        except Exception as e:
            print(f"Error for question {question}, {repr(e)}")
            pass

```

from json import JSONDecodeError for idx, node in enumerate(tqdm(nodes[:39])): node_questions_0 = node_questions_lists[idx] for question in node_questions_0: try: # note: we don't need to use response, events are logged through fine-tuning handler gpt4_query_engine.query(question) except Exception as e: print(f"Error for question {question}, {repr(e)}") pass
```
  0%|          | 0/39 [00:00<?, ?it/s]
```

```
Error for question Which citations are referred to in the discussion about safety investigations into pretraining data and pretrained models?, ValidationError(model='Response', errors=[{'loc': ('__root__',), 'msg': 'Expecting value: line 1 column 1 (char 0)', 'type': 'value_error.jsondecode', 'ctx': {'msg': 'Expecting value', 'doc': 'Empty Response', 'pos': 0, 'lineno': 1, 'colno': 1}}])

```

In [ ]:
Copied!
```
finetuning_handler.save_finetuning_events("llama2_citation_events.jsonl")

```

finetuning_handler.save_finetuning_events("llama2_citation_events.jsonl")
```
Wrote 83 examples to llama2_citation_events.jsonl

```

### Setup Fine-tuning¶
We kick off fine-tuning over the generated dataset.
In [ ]:
Copied!
```
from llama_index.finetuning import OpenAIFinetuneEngine

finetune_engine = OpenAIFinetuneEngine(
    "gpt-3.5-turbo",
    "llama2_citation_events.jsonl",
    # start_job_id="<start-job-id>"  # if you have an existing job, can specify id here
    validate_json=False,  # openai validate json code doesn't support function calling yet
)

```

from llama_index.finetuning import OpenAIFinetuneEngine finetune_engine = OpenAIFinetuneEngine( "gpt-3.5-turbo", "llama2_citation_events.jsonl", # start_job_id="" # if you have an existing job, can specify id here validate_json=False, # openai validate json code doesn't support function calling yet )
In [ ]:
Copied!
```
finetune_engine.finetune()

```

finetune_engine.finetune()
In [ ]:
Copied!
```
finetune_engine.get_current_job()

```

finetune_engine.get_current_job()
Out[ ]:
```
<FineTuningJob fine_tuning.job id=ftjob-ATYm4yZHP1QvXs1wx85Ix79F at 0x1752b6b60> JSON: {
  "object": "fine_tuning.job",
  "id": "ftjob-ATYm4yZHP1QvXs1wx85Ix79F",
  "model": "gpt-3.5-turbo-0613",
  "created_at": 1696497663,
  "finished_at": 1696498092,
  "fine_tuned_model": "ft:gpt-3.5-turbo-0613:llamaindex::86EwPw83",
  "organization_id": "org-1ZDAvajC6v2ZtAP9hLEIsXRz",
  "result_files": [
    "file-wabcIIxjLqvhqOVohf4qSmE7"
  ],
  "status": "succeeded",
  "validation_file": null,
  "training_file": "file-WbYcsinIbH8vyCAstcoFEr92",
  "hyperparameters": {
    "n_epochs": 3
  },
  "trained_tokens": 132678,
  "error": null
}
```

### Use within RAG Pipeline¶
Let's plug the fine-tuned LLM into a full RAG pipeline that outputs structured outputs.
In [ ]:
Copied!
```
ft_llm = finetune_engine.get_finetuned_model(temperature=0.3)

```

ft_llm = finetune_engine.get_finetuned_model(temperature=0.3)
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

vector_index = VectorStoreIndex(nodes=nodes)
query_engine = vector_index.as_query_engine(
    output_cls=Response, similarity_top_k=1, llm=ft_llm
)

```

from llama_index.core import VectorStoreIndex vector_index = VectorStoreIndex(nodes=nodes) query_engine = vector_index.as_query_engine( output_cls=Response, similarity_top_k=1, llm=ft_llm )
In [ ]:
Copied!
```
# setup baseline as well
base_index = VectorStoreIndex(nodes=nodes)
base_query_engine = base_index.as_query_engine(
    output_cls=Response, similarity_top_k=1, llm=gpt_35_llm
)

```

# setup baseline as well base_index = VectorStoreIndex(nodes=nodes) base_query_engine = base_index.as_query_engine( output_cls=Response, similarity_top_k=1, llm=gpt_35_llm )
In [ ]:
Copied!
```
query_str = """\
Which citation is used to measure the truthfulness of Llama 2? \
"""
# query_str = """\
# Which citation corresponds to the concept of collecting data that represents \
# empirically sampled human preferences in RLHF?\
# """
# query_str = "Which citations in the paper discuss the development and release of Llama 2?"
# query_str = "Which citations are mentioned in the section on RLHF Results?"
# query_str = "Which citation discusses the carbon output related to the production of AI hardware?"


response = query_engine.query(query_str)
print(str(response))

```

query_str = """\ Which citation is used to measure the truthfulness of Llama 2? \ """ # query_str = """\ # Which citation corresponds to the concept of collecting data that represents \ # empirically sampled human preferences in RLHF?\ # """ # query_str = "Which citations in the paper discuss the development and release of Llama 2?" # query_str = "Which citations are mentioned in the section on RLHF Results?" # query_str = "Which citation discusses the carbon output related to the production of AI hardware?" response = query_engine.query(query_str) print(str(response))
```
{"citations": [{"author": "Lin et al.", "year": 2021, "desc": "TruthfulQA, used for LLM hallucinations to measure whether a language model is truthful in generating answers to questions while being informative at the same time."}]}

```

In [ ]:
Copied!
```
base_response = base_query_engine.query(query_str)
print(str(base_response))

```

base_response = base_query_engine.query(query_str) print(str(base_response))
```
{"citations": [{"author": "Lin et al.", "year": 2021, "desc": "TruthfulQA"}]}

```

In [ ]:
Copied!
```
# view sources
print(response.source_nodes[0].get_content())

```

# view sources print(response.source_nodes[0].get_content())
In [ ]:
Copied!
```
# as a reference, take a look at GPT-4 response
gpt4_response = gpt4_query_engine.query(query_str)
print(str(gpt4_response))

```

# as a reference, take a look at GPT-4 response gpt4_response = gpt4_query_engine.query(query_str) print(str(gpt4_response))
```
{"citations": [{"author": "Lin et al.", "year": 2021, "desc": "TruthfulQA, used for LLM hallucinations to measure whether a language model is truthful in generating answers to questions while being informative at the same time."}]}

```

