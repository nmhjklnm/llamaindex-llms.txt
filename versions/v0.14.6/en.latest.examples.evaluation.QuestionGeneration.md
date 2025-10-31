![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# QuestionGeneration¶
This notebook walks through the process of generating a list of questions that could be asked about your data. This is useful for setting up an evaluation pipeline using the `FaithfulnessEvaluator` and `RelevancyEvaluator` evaluation tools.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import logging
import sys
import pandas as pd

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys import pandas as pd logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
from llama_index.core.evaluation import DatasetGenerator, RelevancyEvaluator
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Response
from llama_index.llms.openai import OpenAI

```

from llama_index.core.evaluation import DatasetGenerator, RelevancyEvaluator from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Response from llama_index.llms.openai import OpenAI
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
Load Data
In [ ]:
Copied!
```
reader = SimpleDirectoryReader("./data/paul_graham/")
documents = reader.load_data()

```

reader = SimpleDirectoryReader("./data/paul_graham/") documents = reader.load_data()
In [ ]:
Copied!
```
data_generator = DatasetGenerator.from_documents(documents)

```

data_generator = DatasetGenerator.from_documents(documents)
```
WARNING:llama_index.indices.service_context:chunk_size_limit is deprecated, please specify chunk_size instead
chunk_size_limit is deprecated, please specify chunk_size instead
chunk_size_limit is deprecated, please specify chunk_size instead
chunk_size_limit is deprecated, please specify chunk_size instead
chunk_size_limit is deprecated, please specify chunk_size instead

```

In [ ]:
Copied!
```
eval_questions = data_generator.generate_questions_from_nodes()

```

eval_questions = data_generator.generate_questions_from_nodes()
In [ ]:
Copied!
```
eval_questions

```

eval_questions
Out[ ]:
```
['What were the two main things the author worked on before college?',
 'How did the author describe their early attempts at writing short stories?',
 'What type of computer did the author first work on for programming?',
 'What language did the author use for programming on the IBM 1401?',
 "What was the author's experience with programming on the 1401?",
 'What type of computer did the author eventually get for themselves?',
 "What was the author's initial plan for college?",
 'What made the author change their mind about studying philosophy?',
 "What sparked the author's interest in AI?",
 'What did the author realize about AI during their first year of grad school?',
 'What were the two art schools that the author applied to?',
 'How did the author end up at RISD?',
 'What was the purpose of the foundation classes at RISD?',
 'How did the author manage to pass the entrance exam for the Accademia di Belli Arti?',
 'What was the arrangement between the students and faculty at the Accademia?',
 "What was the author's experience painting still lives in Florence?",
 'What did the author learn about visual perception while painting still lives?',
 'Why did the author decide to leave the Accademia and return to the US?',
 'What did the author learn about technology companies while working at Interleaf?',
 'What lesson did the author learn about the low end and high end in the software industry?',
 "What was the author's motivation for writing another book on Lisp?",
 'How did the author come up with the idea for starting a company to put art galleries online?',
 'What was the initial reaction of art galleries to the idea of being online?',
 'How did the author and his team come up with the concept of a web app?',
 'What were the three main parts of the software developed by the author and his team?',
 'How did the author and his team learn about retail and improve their software based on user feedback?',
 'Why did the author initially believe that the absolute number of users was the most important factor for a startup?',
 "What was the growth rate of the author's company and why was it significant?",
 "How did the author's decision to hire more people impact the financial stability of the company?",
 "What was the outcome of the company's acquisition by Yahoo in 1998?",
 "What was the author's initial reaction when Yahoo bought their startup?",
 "How did the author's lifestyle change after Yahoo bought their startup?",
 'Why did the author leave Yahoo and what did they plan to do?',
 "What was the author's experience like when they returned to New York after becoming rich?",
 'What idea did the author have in the spring of 2000 and why did they decide to start a new company?',
 "Why did the author decide to build a subset of the new company's vision as an open source project?",
 "How did the author's perception of publishing essays change with the advent of the internet?",
 "What is the author's perspective on working on things that are not prestigious?",
 'What other projects did the author work on besides writing essays?',
 'What type of building did the author buy in Cambridge?',
 "What was the concept behind the big party at the narrator's house in October 2003?",
 "How did Jessica Livingston's perception of startups change after meeting friends of the narrator?",
 'What were some of the ideas that the narrator shared with Jessica about fixing venture capital?',
 'How did the idea of starting their own investment firm come about for the narrator and Jessica?',
 'What was the Summer Founders Program and how did it attract applicants?',
 "How did Y Combinator's batch model help solve the problem of isolation for startup founders?",
 "What advantages did YC's scale bring, both in terms of community and customer acquisition?",
 'Why did the narrator consider Hacker News to be a source of stress?',
 "How did the narrator's role in YC differ from other types of work they had done?",
 'What advice did Robert Morris offer the narrator during his visit in 2010?',
 'What was the advice given to the author by Rtm regarding their involvement with Y Combinator?',
 'Why did the author decide to hand over Y Combinator to someone else?',
 "What event in the author's personal life prompted them to reevaluate their priorities?",
 'How did the author spend most of 2014?',
 'What project did the author work on from March 2015 to October 2019?',
 'How did the author manage to write an interpreter for Lisp in itself?',
 "What was the author's experience like living in England?",
 "When was the author's project, Bel, finally finished?",
 'What did the author do during the fall of 2019?',
 "How would you describe the author's journey and decision-making process throughout the document?",
 "How did the author's experience with editing Lisp expressions differ from traditional app editing?",
 'Why did the author receive negative comments when claiming that Lisp was better than other languages?',
 'What is the difference between putting something online and publishing it online?',
 'How did the customs of venture capital practice and essay writing reflect outdated constraints?',
 'Why did Y Combinator change its name to avoid a regional association?',
 "What was the significance of the orange color chosen for Y Combinator's logo?",
 'Why did Y Combinator become a fund for a couple of years before returning to self-funding?',
 'What is the purpose of Y Combinator in relation to the concept of "deal flow"?',
 'How did the combination of running a forum and writing essays lead to a problem for the author?',
 "What was the author's biggest regret about leaving Y Combinator?"]
```

In [ ]:
Copied!
```
# gpt-4
gpt4 = OpenAI(temperature=0, model="gpt-4")

```

# gpt-4 gpt4 = OpenAI(temperature=0, model="gpt-4")
In [ ]:
Copied!
```
evaluator_gpt4 = RelevancyEvaluator(llm=gpt4)

```

evaluator_gpt4 = RelevancyEvaluator(llm=gpt4)
In [ ]:
Copied!
```
# create vector index
vector_index = VectorStoreIndex.from_documents(documents)

```

# create vector index vector_index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
# define jupyter display function
def display_eval_df(query: str, response: Response, eval_result: str) -> None:
    eval_df = pd.DataFrame(
        {
            "Query": query,
            "Response": str(response),
            "Source": (
                response.source_nodes[0].node.get_content()[:1000] + "..."
            ),
            "Evaluation Result": eval_result,
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

# define jupyter display function def display_eval_df(query: str, response: Response, eval_result: str) -> None: eval_df = pd.DataFrame( { "Query": query, "Response": str(response), "Source": ( response.source_nodes[0].node.get_content()[:1000] + "..." ), "Evaluation Result": eval_result, }, index=[0], ) eval_df = eval_df.style.set_properties( **{ "inline-size": "600px", "overflow-wrap": "break-word", }, subset=["Response", "Source"] ) display(eval_df)
In [ ]:
Copied!
```
query_engine = vector_index.as_query_engine()
response_vector = query_engine.query(eval_questions[1])
eval_result = evaluator_gpt4.evaluate_response(
    query=eval_questions[1], response=response_vector
)

```

query_engine = vector_index.as_query_engine() response_vector = query_engine.query(eval_questions[1]) eval_result = evaluator_gpt4.evaluate_response( query=eval_questions[1], response=response_vector )
In [ ]:
Copied!
```
display_eval_df(eval_questions[1], response_vector, eval_result)

```

display_eval_df(eval_questions[1], response_vector, eval_result)
| Query | Response | Source | Evaluation Result  
---|---|---|---|---  
0 | How did the author describe their early attempts at writing short stories? | The author described their early attempts at writing short stories as awful. They mentioned that their stories had hardly any plot and were mostly about characters with strong feelings, which they thought made the stories deep. | What I Worked On February 2021 Before college the two main things I worked on, outside of school, were writing and programming. I didn't write essays. I wrote what beginning writers were supposed to write then, and probably still are: short stories. My stories were awful. They had hardly any plot, just characters with strong feelings, which I imagined made them deep. The first programs I tried writing were on the IBM 1401 that our school district used for what was then called "data processing." This was in 9th grade, so I was 13 or 14. The school district's 1401 happened to be in the basement of our junior high school, and my friend Rich Draves and I got permission to use it. It was like a mini Bond villain's lair down there, with all these alien-looking machines — CPU, disk drives, printer, card reader — sitting up on a raised floor under bright fluorescent lights. The language we used was an early version of Fortran. You had to type programs on punch cards, then stack them in the... | YES
