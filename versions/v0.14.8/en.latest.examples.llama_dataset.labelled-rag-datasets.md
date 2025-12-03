![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Benchmarking RAG Pipelines With A `LabelledRagDatatset`¶
The `LabelledRagDataset` is meant to be used for evaluating any given RAG pipeline, for which there could be several configurations (i.e. choosing the `LLM`, values for the `similarity_top_k`, `chunk_size`, and others). We've likened this abstract to traditional machine learning datastets, where `X` features are meant to predict a ground-truth label `y`. In this case, we use the `query` as well as the retrieved `contexts` as the "features" and the answer to the query, called `reference_answer` as the ground-truth label.
And of course, such datasets are comprised of observations or examples. In the case of `LabelledRagDataset`, these are made up with a set of `LabelledRagDataExample`'s.
In this notebook, we will show how one can construct a `LabelledRagDataset` from scratch. Please note that the alternative to this would be to simply download a community supplied `LabelledRagDataset` from `llama-hub` in order to evaluate/benchmark your own RAG pipeline on it.
### The `LabelledRagDataExample` Class¶
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-readers-wikipedia

```

%pip install llama-index-llms-openai %pip install llama-index-readers-wikipedia
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import (
    LabelledRagDataExample,
    CreatedByType,
    CreatedBy,
)

# constructing a LabelledRagDataExample
query = "This is a test query, is it not?"
query_by = CreatedBy(type=CreatedByType.AI, model_name="gpt-4")
reference_answer = "Yes it is."
reference_answer_by = CreatedBy(type=CreatedByType.HUMAN)
reference_contexts = ["This is a sample context"]

rag_example = LabelledRagDataExample(
    query=query,
    query_by=query_by,
    reference_contexts=reference_contexts,
    reference_answer=reference_answer,
    reference_answer_by=reference_answer_by,
)

```

from llama_index.core.llama_dataset import ( LabelledRagDataExample, CreatedByType, CreatedBy, ) # constructing a LabelledRagDataExample query = "This is a test query, is it not?" query_by = CreatedBy(type=CreatedByType.AI, model_name="gpt-4") reference_answer = "Yes it is." reference_answer_by = CreatedBy(type=CreatedByType.HUMAN) reference_contexts = ["This is a sample context"] rag_example = LabelledRagDataExample( query=query, query_by=query_by, reference_contexts=reference_contexts, reference_answer=reference_answer, reference_answer_by=reference_answer_by, )
The `LabelledRagDataExample` is a Pydantic `Model` and so, going from `json` or `dict` (and vice-versa) is possible.
In [ ]:
Copied!
```
print(rag_example.json())

```

print(rag_example.json())
```
{"query": "This is a test query, is it not?", "query_by": {"model_name": "gpt-4", "type": "ai"}, "reference_contexts": ["This is a sample context"], "reference_answer": "Yes it is.", "reference_answer_by": {"model_name": "", "type": "human"}}

```

In [ ]:
Copied!
```
LabelledRagDataExample.parse_raw(rag_example.json())

```

LabelledRagDataExample.parse_raw(rag_example.json())
Out[ ]:
```
LabelledRagDataExample(query='This is a test query, is it not?', query_by=CreatedBy(model_name='gpt-4', type=<CreatedByType.AI: 'ai'>), reference_contexts=['This is a sample context'], reference_answer='Yes it is.', reference_answer_by=CreatedBy(model_name='', type=<CreatedByType.HUMAN: 'human'>))
```

In [ ]:
Copied!
```
rag_example.dict()

```

rag_example.dict()
Out[ ]:
```
{'query': 'This is a test query, is it not?',
 'query_by': {'model_name': 'gpt-4', 'type': <CreatedByType.AI: 'ai'>},
 'reference_contexts': ['This is a sample context'],
 'reference_answer': 'Yes it is.',
 'reference_answer_by': {'model_name': '',
  'type': <CreatedByType.HUMAN: 'human'>}}
```

In [ ]:
Copied!
```
LabelledRagDataExample.parse_obj(rag_example.dict())

```

LabelledRagDataExample.parse_obj(rag_example.dict())
Out[ ]:
```
LabelledRagDataExample(query='This is a test query, is it not?', query_by=CreatedBy(model_name='gpt-4', type=<CreatedByType.AI: 'ai'>), reference_contexts=['This is a sample context'], reference_answer='Yes it is.', reference_answer_by=CreatedBy(model_name='', type=<CreatedByType.HUMAN: 'human'>))
```

Let's create a second example, so we can have a (slightly) more interesting `LabelledRagDataset`.
In [ ]:
Copied!
```
query = "This is a test query, is it so?"
reference_answer = "I think yes, it is."
reference_contexts = ["This is a second sample context"]

rag_example_2 = LabelledRagDataExample(
    query=query,
    query_by=query_by,
    reference_contexts=reference_contexts,
    reference_answer=reference_answer,
    reference_answer_by=reference_answer_by,
)

```

query = "This is a test query, is it so?" reference_answer = "I think yes, it is." reference_contexts = ["This is a second sample context"] rag_example_2 = LabelledRagDataExample( query=query, query_by=query_by, reference_contexts=reference_contexts, reference_answer=reference_answer, reference_answer_by=reference_answer_by, )
### The `LabelledRagDataset` Class¶
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import LabelledRagDataset

rag_dataset = LabelledRagDataset(examples=[rag_example, rag_example_2])

```

from llama_index.core.llama_dataset import LabelledRagDataset rag_dataset = LabelledRagDataset(examples=[rag_example, rag_example_2])
There exists a convienience method to view the dataset as a `pandas.DataFrame`.
In [ ]:
Copied!
```
rag_dataset.to_pandas()

```

rag_dataset.to_pandas()
Out[ ]:
| query | reference_contexts | reference_answer | reference_answer_by | query_by  
---|---|---|---|---|---  
0 | This is a test query, is it not? | [This is a sample context] | Yes it is. | human | ai (gpt-4)  
1 | This is a test query, is it so? | [This is a second sample context] | I think yes, it is. | human | ai (gpt-4)  
#### Serialization¶
To persist and load the dataset to and from disk, there are the `save_json` and `from_json` methods.
In [ ]:
Copied!
```
rag_dataset.save_json("rag_dataset.json")

```

rag_dataset.save_json("rag_dataset.json")
In [ ]:
Copied!
```
reload_rag_dataset = LabelledRagDataset.from_json("rag_dataset.json")

```

reload_rag_dataset = LabelledRagDataset.from_json("rag_dataset.json")
In [ ]:
Copied!
```
reload_rag_dataset.to_pandas()

```

reload_rag_dataset.to_pandas()
Out[ ]:
| query | reference_contexts | reference_answer | reference_answer_by | query_by  
---|---|---|---|---|---  
0 | This is a test query, is it not? | [This is a sample context] | Yes it is. | human | ai (gpt-4)  
1 | This is a test query, is it so? | [This is a second sample context] | I think yes, it is. | human | ai (gpt-4)  
### Building a synthetic `LabelledRagDataset` over Wikipedia¶
For this section, we'll first create a `LabelledRagDataset` using a synthetic generator. Ultimately, we will use GPT-4 to produce both the `query` and `reference_answer` for the synthetic `LabelledRagDataExample`'s.
NOTE: if one has queries, reference answers, and contexts over a text corpus, then it is not necessary to use data synthesis to be able to predict and subsequently evaluate said predictions.
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
!pip install wikipedia -q

```

!pip install wikipedia -q
In [ ]:
Copied!
```
# wikipedia pages
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.core import VectorStoreIndex

cities = [
    "San Francisco",
]

documents = WikipediaReader().load_data(
    pages=[f"History of {x}" for x in cities]
)
index = VectorStoreIndex.from_documents(documents)

```

# wikipedia pages from llama_index.readers.wikipedia import WikipediaReader from llama_index.core import VectorStoreIndex cities = [ "San Francisco", ] documents = WikipediaReader().load_data( pages=[f"History of {x}" for x in cities] ) index = VectorStoreIndex.from_documents(documents)
The `RagDatasetGenerator` can be built over a set of documents to generate `LabelledRagDataExample`'s.
In [ ]:
Copied!
```
# generate questions against chunks
from llama_index.core.llama_dataset.generator import RagDatasetGenerator
from llama_index.llms.openai import OpenAI

# set context for llm provider
llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)

# instantiate a DatasetGenerator
dataset_generator = RagDatasetGenerator.from_documents(
    documents,
    llm=llm,
    num_questions_per_chunk=2,  # set the number of questions per nodes
    show_progress=True,
)

```

# generate questions against chunks from llama_index.core.llama_dataset.generator import RagDatasetGenerator from llama_index.llms.openai import OpenAI # set context for llm provider llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3) # instantiate a DatasetGenerator dataset_generator = RagDatasetGenerator.from_documents( documents, llm=llm, num_questions_per_chunk=2, # set the number of questions per nodes show_progress=True, )
```
Parsing nodes:   0%|          | 0/1 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
len(dataset_generator.nodes)

```

len(dataset_generator.nodes)
Out[ ]:


In [ ]:
Copied!
```
# since there are 13 nodes, there should be a total of 26 questions
rag_dataset = dataset_generator.generate_dataset_from_nodes()

```

# since there are 13 nodes, there should be a total of 26 questions rag_dataset = dataset_generator.generate_dataset_from_nodes()
```
100%|███████████████████████████████████████████████████████| 13/13 [00:02<00:00,  5.04it/s]
100%|█████████████████████████████████████████████████████████| 2/2 [00:02<00:00,  1.14s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:05<00:00,  2.95s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:13<00:00,  6.55s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:07<00:00,  3.89s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:05<00:00,  2.66s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:05<00:00,  2.85s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:04<00:00,  2.03s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:08<00:00,  4.07s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:06<00:00,  3.48s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:04<00:00,  2.34s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:02<00:00,  1.50s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:08<00:00,  4.35s/it]
100%|█████████████████████████████████████████████████████████| 2/2 [00:08<00:00,  4.34s/it]

```

In [ ]:
Copied!
```
rag_dataset.to_pandas()

```

rag_dataset.to_pandas()
Out[ ]:
| query | reference_contexts | reference_answer | reference_answer_by | query_by  
---|---|---|---|---|---  
0 | How did the gold rush of 1849 impact the devel... | [The history of the city of San Francisco, Cal... | The gold rush of 1849 had a significant impact... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
1 | What were the early European settlements estab... | [The history of the city of San Francisco, Cal... | The early European settlements established in ... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
2 | How did the arrival of Europeans impact the se... | [== Arrival of Europeans and early settlement ... | The arrival of Europeans had a significant imp... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
3 | What were some of the challenges faced by the ... | [== Arrival of Europeans and early settlement ... | The early settlers of San Francisco faced seve... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
4 | How did the California gold rush impact the po... | [== 1848 gold rush ==\nThe California gold rus... | The California gold rush in the mid-19th centu... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
5 | Discuss the role of Chinese immigrants in the ... | [== 1848 gold rush ==\nThe California gold rus... | Chinese immigrants played a significant role i... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
6 | How did San Francisco transform into a major c... | [== Paris of the West ==\n\nIt was during the ... | San Francisco transformed into a major city du... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
7 | What were some significant developments and ch... | [== Paris of the West ==\n\nIt was during the ... | During the late 19th and early 20th centuries,... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
8 | How did Abe Ruef contribute to Eugene Schmitz'... | [== Corruption and graft trials ==\n\nMayor Eu... | Abe Ruef contributed $16,000 to Eugene Schmitz... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
9 | Describe the impact of the 1906 earthquake and... | [== Corruption and graft trials ==\n\nMayor Eu... | The 1906 earthquake and fire had a devastating... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
10 | How did the 1906 San Francisco earthquake impa... | [=== Reconstruction ===\nAlmost immediately af... | The 1906 San Francisco earthquake had a signif... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
11 | What major events and developments took place ... | [=== Reconstruction ===\nAlmost immediately af... | During the 1930s and World War II, several maj... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
12 | How did the post-World War II era contribute t... | [== Post-World War II ==\nAfter World War II, ... | After World War II, many American military per... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
13 | Discuss the impact of urban renewal initiative... | [== Post-World War II ==\nAfter World War II, ... | M. Justin Herman led urban renewal initiatives... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
14 | How did San Francisco become a center of count... | [== 1960 – 1970s ==\n\n\n=== "Summer of Love" ... | San Francisco became a center of countercultur... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
15 | Explain the role of San Francisco as a "Gay Me... | [== 1960 – 1970s ==\n\n\n=== "Summer of Love" ... | During the 1960s and beyond, San Francisco bec... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
16 | How did the construction of BART and Muni impa... | [=== New public infrastructure ===\nThe 1970s ... | The construction of BART and Muni in the 1970s... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
17 | What were the major challenges faced by San Fr... | [=== New public infrastructure ===\nThe 1970s ... | In the 1980s, San Francisco faced several majo... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
18 | How did the 1989 Loma Prieta earthquake impact... | [=== 1989 Loma Prieta earthquake ===\n\nOn Oct... | The 1989 Loma Prieta earthquake had significan... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
19 | Discuss the effects of the dot-com boom in the... | [=== 1989 Loma Prieta earthquake ===\n\nOn Oct... | The dot-com boom in the late 1990s had signifi... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
20 | How did the redevelopment of the Mission Bay n... | [== 2010s ==\nThe early 2000s and into the 201... | The redevelopment of the Mission Bay neighborh... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
21 | What significant events occurred in San Franci... | [== 2010s ==\nThe early 2000s and into the 201... | In 2010, the San Francisco Giants won their fi... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
22 | In the context of San Francisco's history, dis... | [=== Cultural themes ===\nBerglund, Barbara (2... | The 1906 earthquake had a significant impact o... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
23 | How did different ethnic and religious communi... | [=== Cultural themes ===\nBerglund, Barbara (2... | Two specific communities mentioned in the sour... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
24 | In the context of San Francisco's history, wha... | [=== Gold rush & early days ===\nHittell, John... | Some significant events and developments durin... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
25 | How did politics shape the growth and transfor... | [=== Gold rush & early days ===\nHittell, John... | The provided sources offer a comprehensive und... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
In [ ]:
Copied!
```
rag_dataset.save_json("rag_dataset.json")

```

rag_dataset.save_json("rag_dataset.json")
