# BatchEvalRunner - Running Multiple Evaluations¶
The `BatchEvalRunner` class can be used to run a series of evaluations asynchronously. The async jobs are limited to a defined size of `num_workers`.
## Setup¶
In [ ]:
Copied!
```
%pip install llama-index-llms-openai llama-index-embeddings-openai

```

%pip install llama-index-llms-openai llama-index-embeddings-openai
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
import os
import openai

os.environ["OPENAI_API_KEY"] = "sk-..."
# openai.api_key = os.environ["OPENAI_API_KEY"]

```

import os import openai os.environ["OPENAI_API_KEY"] = "sk-..." # openai.api_key = os.environ["OPENAI_API_KEY"]
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
)
from llama_index.core.node_parser import SentenceSplitter
import pandas as pd

pd.set_option("display.max_colwidth", 0)

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Response from llama_index.llms.openai import OpenAI from llama_index.core.evaluation import ( FaithfulnessEvaluator, RelevancyEvaluator, CorrectnessEvaluator, ) from llama_index.core.node_parser import SentenceSplitter import pandas as pd pd.set_option("display.max_colwidth", 0)
Using GPT-4 here for evaluation
In [ ]:
Copied!
```
# gpt-4
gpt4 = OpenAI(temperature=0, model="gpt-4")

faithfulness_gpt4 = FaithfulnessEvaluator(llm=gpt4)
relevancy_gpt4 = RelevancyEvaluator(llm=gpt4)
correctness_gpt4 = CorrectnessEvaluator(llm=gpt4)

```

# gpt-4 gpt4 = OpenAI(temperature=0, model="gpt-4") faithfulness_gpt4 = FaithfulnessEvaluator(llm=gpt4) relevancy_gpt4 = RelevancyEvaluator(llm=gpt4) correctness_gpt4 = CorrectnessEvaluator(llm=gpt4)
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("./test_wiki_data/").load_data()

```

documents = SimpleDirectoryReader("./test_wiki_data/").load_data()
In [ ]:
Copied!
```
# create vector index
llm = OpenAI(temperature=0.3, model="gpt-3.5-turbo")
splitter = SentenceSplitter(chunk_size=512)
vector_index = VectorStoreIndex.from_documents(
    documents, transformations=[splitter]
)

```

# create vector index llm = OpenAI(temperature=0.3, model="gpt-3.5-turbo") splitter = SentenceSplitter(chunk_size=512) vector_index = VectorStoreIndex.from_documents( documents, transformations=[splitter] )
## Question Generation¶
To run evaluations in batch, you can create the runner and then call the `.aevaluate_queries()` function on a list of queries.
First, we can generate some questions and then run evaluation on them.
In [ ]:
Copied!
```
%pip install spacy datasets span-marker scikit-learn

```

%pip install spacy datasets span-marker scikit-learn
In [ ]:
Copied!
```
from llama_index.core.evaluation import DatasetGenerator

dataset_generator = DatasetGenerator.from_documents(documents, llm=llm)

qas = dataset_generator.generate_dataset_from_nodes(num=3)

```

from llama_index.core.evaluation import DatasetGenerator dataset_generator = DatasetGenerator.from_documents(documents, llm=llm) qas = dataset_generator.generate_dataset_from_nodes(num=3)
```
/Users/yi/Code/llama/llama_index/llama-index-core/llama_index/core/evaluation/dataset_generation.py:212: DeprecationWarning: Call to deprecated class DatasetGenerator. (Deprecated in favor of `RagDatasetGenerator` which should be used instead.)
  return cls(
/Users/yi/Code/llama/llama_index/llama-index-core/llama_index/core/evaluation/dataset_generation.py:309: DeprecationWarning: Call to deprecated class QueryResponseDataset. (Deprecated in favor of `LabelledRagDataset` which should be used instead.)
  return QueryResponseDataset(queries=queries, responses=responses_dict)

```

## Running Batch Evaluation¶
Now, we can run our batch evaluation!
In [ ]:
Copied!
```
from llama_index.core.evaluation import BatchEvalRunner

runner = BatchEvalRunner(
    {"faithfulness": faithfulness_gpt4, "relevancy": relevancy_gpt4},
    workers=8,
)

eval_results = await runner.aevaluate_queries(
    vector_index.as_query_engine(llm=llm), queries=qas.questions
)

# If we had ground-truth answers, we could also include the correctness evaluator like below.
# The correctness evaluator depends on additional kwargs, which are passed in as a dictionary.
# Each question is mapped to a set of kwargs
#

# runner = BatchEvalRunner(
#     {"correctness": correctness_gpt4},
#     workers=8,
# )

# eval_results = await runner.aevaluate_queries(
#     vector_index.as_query_engine(),
#     queries=qas.queries,
#     reference=[qr[1] for qr in qas.qr_pairs],
# )

```

from llama_index.core.evaluation import BatchEvalRunner runner = BatchEvalRunner( {"faithfulness": faithfulness_gpt4, "relevancy": relevancy_gpt4}, workers=8, ) eval_results = await runner.aevaluate_queries( vector_index.as_query_engine(llm=llm), queries=qas.questions ) # If we had ground-truth answers, we could also include the correctness evaluator like below. # The correctness evaluator depends on additional kwargs, which are passed in as a dictionary. # Each question is mapped to a set of kwargs # # runner = BatchEvalRunner( # {"correctness": correctness_gpt4}, # workers=8, # ) # eval_results = await runner.aevaluate_queries( # vector_index.as_query_engine(), # queries=qas.queries, # reference=[qr[1] for qr in qas.qr_pairs], # )
In [ ]:
Copied!
```
print(len([qr for qr in qas.qr_pairs]))

```

print(len([qr for qr in qas.qr_pairs]))


## Inspecting Outputs¶
In [ ]:
Copied!
```
print(eval_results.keys())

print(eval_results["faithfulness"][0].dict().keys())

print(eval_results["faithfulness"][0].passing)
print(eval_results["faithfulness"][0].response)
print(eval_results["faithfulness"][0].contexts)

```

print(eval_results.keys()) print(eval_results["faithfulness"][0].dict().keys()) print(eval_results["faithfulness"][0].passing) print(eval_results["faithfulness"][0].response) print(eval_results["faithfulness"][0].contexts)
```
dict_keys(['faithfulness', 'relevancy'])
dict_keys(['query', 'contexts', 'response', 'passing', 'feedback', 'score', 'pairwise_source', 'invalid_result', 'invalid_reason'])
True
The population of New York City as of 2020 was 8,804,190.
['=== Population density ===\n\nIn 2020, the city had an estimated population density of 29,302.37 inhabitants per square mile (11,313.71/km2), rendering it the nation\'s most densely populated of all larger municipalities (those with more than 100,000 residents), with several small cities (of fewer than 100,000) in adjacent Hudson County, New Jersey having greater density, as per the 2010 census. Geographically co-extensive with New York County, the borough of Manhattan\'s 2017 population density of 72,918 inhabitants per square mile (28,154/km2) makes it the highest of any county in the United States and higher than the density of any individual American city. The next three densest counties in the United States, placing second through fourth, are also New York boroughs: Brooklyn, the Bronx, and Queens respectively.\n\n\n=== Race and ethnicity ===\n\nThe city\'s population in 2020 was 30.9% White (non-Hispanic), 28.7% Hispanic or Latino, 20.2% Black or African American (non-Hispanic), 15.6% Asian, and 0.2% Native American (non-Hispanic). A total of 3.4% of the non-Hispanic population identified with more than one race. Throughout its history, New York has been a major port of entry for immigrants into the United States. More than 12 million European immigrants were received at Ellis Island between 1892 and 1924. The term "melting pot" was first coined to describe densely populated immigrant neighborhoods on the Lower East Side. By 1900, Germans constituted the largest immigrant group, followed by the Irish, Jews, and Italians. In 1940, Whites represented 92% of the city\'s population.Approximately 37% of the city\'s population is foreign born, and more than half of all children are born to mothers who are immigrants as of 2013. In New York, no single country or region of origin dominates.', "New York, often called New York City or NYC, is the most populous city in the United States. With a 2020 population of 8,804,190 distributed over 300.46 square miles (778.2 km2), New York City is the most densely populated major city in the United States and more than twice as populous as Los Angeles, the nation's second-largest city. New York City is located at the southern tip of New York State. It constitutes the geographical and demographic center of both the Northeast megalopolis and the New York metropolitan area, the largest metropolitan area in the U.S. by both population and urban area. With over 20.1 million people in its metropolitan statistical area and 23.5 million in its combined statistical area as of 2020, New York is one of the world's most populous megacities, and over 58 million people live within 250 mi (400 km) of the city. New York City is a global cultural, financial, entertainment, and media center with a significant influence on commerce, health care and life sciences, research, technology, education, politics, tourism, dining, art, fashion, and sports. Home to the headquarters of the United Nations, New York is an important center for international diplomacy, and is sometimes described as the capital of the world.Situated on one of the world's largest natural harbors and extending into the Atlantic Ocean, New York City comprises five boroughs, each of which is coextensive with a respective county of the state of New York. The five boroughs, which were created in 1898 when local governments were consolidated into a single municipal entity, are: Brooklyn (in Kings County), Queens (in Queens County), Manhattan (in New York County), The Bronx (in Bronx County), and Staten Island (in Richmond County).As of 2021, the New York metropolitan area is the largest metropolitan economy in the world with a gross metropolitan product of over $2.4 trillion. If the New York metropolitan area were a sovereign state, it would have the eighth-largest economy in the world. New York City is an established safe haven for global investors."]

```

## Reporting Total Scores¶
In [ ]:
Copied!
```
def get_eval_results(key, eval_results):
    results = eval_results[key]
    correct = 0
    for result in results:
        if result.passing:
            correct += 1
    score = correct / len(results)
    print(f"{key} Score: {score}")
    return score

```

def get_eval_results(key, eval_results): results = eval_results[key] correct = 0 for result in results: if result.passing: correct += 1 score = correct / len(results) print(f"{key} Score: {score}") return score
In [ ]:
Copied!
```
score = get_eval_results("faithfulness", eval_results)

```

score = get_eval_results("faithfulness", eval_results)
```
faithfulness Score: 1.0

```

In [ ]:
Copied!
```
score = get_eval_results("relevancy", eval_results)

```

score = get_eval_results("relevancy", eval_results)
```
relevancy Score: 1.0

```

