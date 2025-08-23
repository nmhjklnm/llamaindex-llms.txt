# Faithfulness Evaluator¶
This notebook uses the `FaithfulnessEvaluator` module to measure if the response from a query engine matches any source nodes.  
This is useful for measuring if the response was hallucinated.  
The data is extracted from the New York City wikipedia page.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai pandas[jinja2] spacy

```

%pip install llama-index-llms-openai pandas[jinja2] spacy
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

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Response,
)
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import FaithfulnessEvaluator
from llama_index.core.node_parser import SentenceSplitter
import pandas as pd

pd.set_option("display.max_colwidth", 0)

```

from llama_index.core import ( VectorStoreIndex, SimpleDirectoryReader, Response, ) from llama_index.llms.openai import OpenAI from llama_index.core.evaluation import FaithfulnessEvaluator from llama_index.core.node_parser import SentenceSplitter import pandas as pd pd.set_option("display.max_colwidth", 0)
Using GPT-4 here for evaluation
In [ ]:
Copied!
```
# gpt-4
gpt4 = OpenAI(temperature=0, model="gpt-4")

evaluator_gpt4 = FaithfulnessEvaluator(llm=gpt4)

```

# gpt-4 gpt4 = OpenAI(temperature=0, model="gpt-4") evaluator_gpt4 = FaithfulnessEvaluator(llm=gpt4)
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
splitter = SentenceSplitter(chunk_size=512)
vector_index = VectorStoreIndex.from_documents(
    documents, transformations=[splitter]
)

```

# create vector index splitter = SentenceSplitter(chunk_size=512) vector_index = VectorStoreIndex.from_documents( documents, transformations=[splitter] )
In [ ]:
Copied!
```
from llama_index.core.evaluation import EvaluationResult


# define jupyter display function
def display_eval_df(response: Response, eval_result: EvaluationResult) -> None:
    if response.source_nodes == []:
        print("no response!")
        return
    eval_df = pd.DataFrame(
        {
            "Response": str(response),
            "Source": response.source_nodes[0].node.text[:1000] + "...",
            "Evaluation Result": "Pass" if eval_result.passing else "Fail",
            "Reasoning": eval_result.feedback,
        },
        index=[0],
    )
    eval_df = eval_df.style.set_properties(
        **{
            "inline-size": "600px",
            "overflow-wrap": "break-word",
        },
        subset=["Response", "Source"]
    )
    display(eval_df)

```

from llama_index.core.evaluation import EvaluationResult # define jupyter display function def display_eval_df(response: Response, eval_result: EvaluationResult) -> None: if response.source_nodes == []: print("no response!") return eval_df = pd.DataFrame( { "Response": str(response), "Source": response.source_nodes[0].node.text[:1000] + "...", "Evaluation Result": "Pass" if eval_result.passing else "Fail", "Reasoning": eval_result.feedback, }, index=[0], ) eval_df = eval_df.style.set_properties( **{ "inline-size": "600px", "overflow-wrap": "break-word", }, subset=["Response", "Source"] ) display(eval_df)
To run evaluations you can call the `.evaluate_response()` function on the `Response` object return from the query to run the evaluations. Lets evaluate the outputs of the vector_index.
In [ ]:
Copied!
```
query_engine = vector_index.as_query_engine()
response_vector = query_engine.query("How did New York City get its name?")
eval_result = evaluator_gpt4.evaluate_response(response=response_vector)

```

query_engine = vector_index.as_query_engine() response_vector = query_engine.query("How did New York City get its name?") eval_result = evaluator_gpt4.evaluate_response(response=response_vector)
In [ ]:
Copied!
```
display_eval_df(response_vector, eval_result)

```

display_eval_df(response_vector, eval_result)
| Response | Source | Evaluation Result | Reasoning  
---|---|---|---|---  
0 | New York City got its name when it came under British control in 1664. It was renamed New York after King Charles II of England granted the lands to his brother, the Duke of York. | The city came under British control in 1664 and was renamed New York after King Charles II of England granted the lands to his brother, the Duke of York. The city was regained by the Dutch in July 1673 and was renamed New Orange for one year and three months; the city has been continuously named New York since November 1674. New York City was the capital of the United States from 1785 until 1790, and has been the largest U.S. city since 1790. The Statue of Liberty greeted millions of immigrants as they came to the U.S. by ship in the late 19th and early 20th centuries, and is a symbol of the U.S. and its ideals of liberty and peace. In the 21st century, New York City has emerged as a global node of creativity, entrepreneurship, and as a symbol of freedom and cultural diversity. The New York Times has won the most Pulitzer Prizes for journalism and remains the U.S. media's "newspaper of record". In 2019, New York City was voted the greatest city in the world in a survey of over 30,000 p... | Pass | YES  
## Benchmark on Generated Question¶
Now lets generate a few more questions so that we have more to evaluate with and run a small benchmark.
In [ ]:
Copied!
```
from llama_index.core.evaluation import DatasetGenerator

question_generator = DatasetGenerator.from_documents(documents)
eval_questions = question_generator.generate_questions_from_nodes(5)

eval_questions

```

from llama_index.core.evaluation import DatasetGenerator question_generator = DatasetGenerator.from_documents(documents) eval_questions = question_generator.generate_questions_from_nodes(5) eval_questions
```
/Users/loganmarkewich/giant_change/llama_index/llama-index-core/llama_index/core/evaluation/dataset_generation.py:212: DeprecationWarning: Call to deprecated class DatasetGenerator. (Deprecated in favor of `RagDatasetGenerator` which should be used instead.)
  return cls(
/Users/loganmarkewich/giant_change/llama_index/llama-index-core/llama_index/core/evaluation/dataset_generation.py:309: DeprecationWarning: Call to deprecated class QueryResponseDataset. (Deprecated in favor of `LabelledRagDataset` which should be used instead.)
  return QueryResponseDataset(queries=queries, responses=responses_dict)

```

Out[ ]:
```
['What is the population of New York City as of 2020?',
 'Which city is the second-largest in the United States?',
 'How many people live within 250 miles of New York City?',
 'What are the five boroughs of New York City?',
 'What is the gross metropolitan product of the New York metropolitan area?']
```

In [ ]:
Copied!
```
import asyncio


def evaluate_query_engine(query_engine, questions):
    c = [query_engine.aquery(q) for q in questions]
    results = asyncio.run(asyncio.gather(*c))
    print("finished query")

    total_correct = 0
    for r in results:
        # evaluate with gpt 4
        eval_result = (
            1 if evaluator_gpt4.evaluate_response(response=r).passing else 0
        )
        total_correct += eval_result

    return total_correct, len(results)

```

import asyncio def evaluate_query_engine(query_engine, questions): c = [query_engine.aquery(q) for q in questions] results = asyncio.run(asyncio.gather(*c)) print("finished query") total_correct = 0 for r in results: # evaluate with gpt 4 eval_result = ( 1 if evaluator_gpt4.evaluate_response(response=r).passing else 0 ) total_correct += eval_result return total_correct, len(results)
In [ ]:
Copied!
```
vector_query_engine = vector_index.as_query_engine()
correct, total = evaluate_query_engine(vector_query_engine, eval_questions[:5])

print(f"score: {correct}/{total}")

```

vector_query_engine = vector_index.as_query_engine() correct, total = evaluate_query_engine(vector_query_engine, eval_questions[:5]) print(f"score: {correct}/{total}")
```
finished query
score: 5/5

```

