![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# UpTrain Callback Handler¶
UpTrain (github || website || docs) is an open-source platform to evaluate and improve GenAI applications. It provides grades for 20+ preconfigured checks (covering language, code, embedding use cases), performs root cause analysis on failure cases and gives insights on how to resolve them.
This notebook showcases how to use UpTrain Callback Handler to evaluate different components of your RAG pipelines.
## 1. **RAG Query Engine Evaluations** :¶
The RAG query engine plays a crucial role in retrieving context and generating responses. To ensure its performance and response quality, we conduct the following evaluations:
  * **Context Relevance** : Determines if the retrieved context has sufficient information to answer the user query or not.
  * **Factual Accuracy** : Assesses if the LLM's response can be verified via the retrieved context.
  * **Response Completeness** : Checks if the response contains all the information required to answer the user query comprehensively.


## 2. **Sub-Question Query Generation Evaluation** :¶
The SubQuestionQueryGeneration operator decomposes a question into sub-questions, generating responses for each using an RAG query engine. To measure it's accuracy, we use:
  * **Sub Query Completeness** : Assures that the sub-questions accurately and comprehensively cover the original query.


## 3. **Re-Ranking Evaluations** :¶
Re-ranking involves reordering nodes based on relevance to the query and choosing the top nodes. Different evaluations are performed based on the number of nodes returned after re-ranking.
a. Same Number of Nodes
  * **Context Reranking** : Checks if the order of re-ranked nodes is more relevant to the query than the original order.


b. Different Number of Nodes:
  * **Context Conciseness** : Examines whether the reduced number of nodes still provides all the required information.


These evaluations collectively ensure the robustness and effectiveness of the RAG query engine, SubQuestionQueryGeneration operator, and the re-ranking process in the LlamaIndex pipeline.
####  **Note:**¶
  * We have performed evaluations using basic RAG query engine, the same evaluations can be performed using the advanced RAG query engine as well.
  * Same is true for Re-Ranking evaluations, we have performed evaluations using SentenceTransformerRerank, the same evaluations can be performed using other re-rankers as well.


## Install Dependencies and Import Libraries¶
Install notebook dependencies.
In [ ]:
Copied!
```
%pip install llama-index-readers-web
%pip install llama-index-callbacks-uptrain
%pip install -q html2text llama-index pandas tqdm uptrain torch sentence-transformers

```

%pip install llama-index-readers-web %pip install llama-index-callbacks-uptrain %pip install -q html2text llama-index pandas tqdm uptrain torch sentence-transformers
Import libraries.
In [ ]:
Copied!
```
from getpass import getpass

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.callbacks import CallbackManager
from llama_index.callbacks.uptrain.base import UpTrainCallbackHandler
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.postprocessor import SentenceTransformerRerank

import os

```

from getpass import getpass from llama_index.core import Settings, VectorStoreIndex from llama_index.core.node_parser import SentenceSplitter from llama_index.readers.web import SimpleWebPageReader from llama_index.core.callbacks import CallbackManager from llama_index.callbacks.uptrain.base import UpTrainCallbackHandler from llama_index.core.query_engine import SubQuestionQueryEngine from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.postprocessor import SentenceTransformerRerank import os
## Setup¶
UpTrain provides you with:
  1. Dashboards with advanced drill-down and filtering options
  2. Insights and common topics among failing cases
  3. Observability and real-time monitoring of production data
  4. Regression testing via seamless integration with your CI/CD pipelines


You can choose between the following options for evaluating using UpTrain:
### 1. **UpTrain's Open-Source Software (OSS)** :¶
You can use the open-source evaluation service to evaluate your model. In this case, you will need to provide an OpenAI API key. You can get yours here.
In order to view your evaluations in the UpTrain dashboard, you will need to set it up by running the following commands in your terminal:
```
git clone https://github.com/uptrain-ai/uptrain
cd uptrain
bash run_uptrain.sh

```

This will start the UpTrain dashboard on your local machine. You can access it at `http://localhost:3000/dashboard`.
Parameters:
  * key_type="openai"
  * api_key="OPENAI_API_KEY"
  * project_name="PROJECT_NAME"


### 2. **UpTrain Managed Service and Dashboards** :¶
Alternatively, you can use UpTrain's managed service to evaluate your model. You can create a free UpTrain account here and get free trial credits. If you want more trial credits, book a call with the maintainers of UpTrain here.
The benefits of using the managed service are:
  1. No need to set up the UpTrain dashboard on your local machine.
  2. Access to many LLMs without needing their API keys.


Once you perform the evaluations, you can view them in the UpTrain dashboard at `https://dashboard.uptrain.ai/dashboard`
Parameters:
  * key_type="uptrain"
  * api_key="UPTRAIN_API_KEY"
  * project_name="PROJECT_NAME"


**Note:** The `project_name` will be the project name under which the evaluations performed will be shown in the UpTrain dashboard.
## Create the UpTrain Callback Handler¶
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = getpass()

callback_handler = UpTrainCallbackHandler(
    key_type="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    project_name="uptrain_llamaindex",
)

Settings.callback_manager = CallbackManager([callback_handler])

```

os.environ["OPENAI_API_KEY"] = getpass() callback_handler = UpTrainCallbackHandler( key_type="openai", api_key=os.environ["OPENAI_API_KEY"], project_name="uptrain_llamaindex", ) Settings.callback_manager = CallbackManager([callback_handler])
## Load and Parse Documents¶
Load documents from Paul Graham's essay "What I Worked On".
In [ ]:
Copied!
```
documents = SimpleWebPageReader().load_data(
    [
        "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt"
    ]
)

```

documents = SimpleWebPageReader().load_data( [ "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt" ] )
Parse the document into nodes.
In [ ]:
Copied!
```
parser = SentenceSplitter()
nodes = parser.get_nodes_from_documents(documents)

```

parser = SentenceSplitter() nodes = parser.get_nodes_from_documents(documents)
# 1. RAG Query Engine Evaluation¶
UpTrain callback handler will automatically capture the query, context and response once generated and will run the following three evaluations _(Graded from 0 to 1)_ on the response:
  * **Context Relevance** : Determines if the retrieved context has sufficient information to answer the user query or not.
  * **Factual Accuracy** : Assesses if the LLM's response can be verified via the retrieved context.
  * **Response Completeness** : Checks if the response contains all the information required to answer the user query comprehensively.


In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(
    documents,
)
query_engine = index.as_query_engine()

max_characters_per_line = 80
queries = [
    "What did Paul Graham do growing up?",
    "When and how did Paul Graham's mother die?",
    "What, in Paul Graham's opinion, is the most distinctive thing about YC?",
    "When and how did Paul Graham meet Jessica Livingston?",
    "What is Bel, and when and where was it written?",
]
for query in queries:
    response = query_engine.query(query)

```

index = VectorStoreIndex.from_documents( documents, ) query_engine = index.as_query_engine() max_characters_per_line = 80 queries = [ "What did Paul Graham do growing up?", "When and how did Paul Graham's mother die?", "What, in Paul Graham's opinion, is the most distinctive thing about YC?", "When and how did Paul Graham meet Jessica Livingston?", "What is Bel, and when and where was it written?", ] for query in queries: response = query_engine.query(query)
```
100%|██████████| 1/1 [00:01<00:00,  1.33s/it]
100%|██████████| 1/1 [00:01<00:00,  1.36s/it]
100%|██████████| 1/1 [00:03<00:00,  3.50s/it]
100%|██████████| 1/1 [00:01<00:00,  1.32s/it]

```

```
Question: What did Paul Graham do growing up?
Response: Growing up, Paul Graham worked on writing short stories and programming. He started programming on an IBM 1401 in 9th grade using an early version of Fortran. Later, he got a TRS-80 computer and wrote simple games, a rocket prediction program, and a word processor. Despite his interest in programming, he initially planned to study philosophy in college before eventually switching to AI.

Context Relevance Score: 0.0
Factual Accuracy Score: 1.0
Response Completeness Score: 1.0


```

```
100%|██████████| 1/1 [00:01<00:00,  1.59s/it]
100%|██████████| 1/1 [00:00<00:00,  1.01it/s]
100%|██████████| 1/1 [00:01<00:00,  1.76s/it]
100%|██████████| 1/1 [00:01<00:00,  1.28s/it]

```

```
Question: When and how did Paul Graham's mother die?
Response: Paul Graham's mother died when he was 18 years old, from a brain tumor.

Context Relevance Score: 0.0
Factual Accuracy Score: 0.0
Response Completeness Score: 0.5


```

```
100%|██████████| 1/1 [00:01<00:00,  1.75s/it]
100%|██████████| 1/1 [00:01<00:00,  1.55s/it]
100%|██████████| 1/1 [00:03<00:00,  3.39s/it]
100%|██████████| 1/1 [00:01<00:00,  1.48s/it]

```

```
Question: What, in Paul Graham's opinion, is the most distinctive thing about YC?
Response: The most distinctive thing about Y Combinator, according to Paul Graham, is that instead of deciding for himself what to work on, the problems come to him. Every 6 months, a new batch of startups brings their problems, which then become the focus of YC. This engagement with a variety of startup problems and the direct involvement in solving them is what Graham finds most unique about Y Combinator.

Context Relevance Score: 1.0
Factual Accuracy Score: 0.3333333333333333
Response Completeness Score: 1.0


```

```
100%|██████████| 1/1 [00:01<00:00,  1.92s/it]
100%|██████████| 1/1 [00:00<00:00,  1.20it/s]
100%|██████████| 1/1 [00:02<00:00,  2.15s/it]
100%|██████████| 1/1 [00:01<00:00,  1.08s/it]

```

```
Question: When and how did Paul Graham meet Jessica Livingston?
Response: Paul Graham met Jessica Livingston at a big party at his house in October 2003.

Context Relevance Score: 1.0
Factual Accuracy Score: 0.5
Response Completeness Score: 1.0


```

```
100%|██████████| 1/1 [00:01<00:00,  1.82s/it]
100%|██████████| 1/1 [00:01<00:00,  1.14s/it]
100%|██████████| 1/1 [00:03<00:00,  3.19s/it]
100%|██████████| 1/1 [00:01<00:00,  1.50s/it]
```

```
Question: What is Bel, and when and where was it written?
Response: Bel is a new Lisp that was written in Arc. It was developed over a period of 4 years, from March 26, 2015 to October 12, 2019. The majority of Bel was written in England.

Context Relevance Score: 1.0
Factual Accuracy Score: 1.0
Response Completeness Score: 1.0


```



# 2. Sub-Question Query Engine Evaluation¶
The **sub-question query engine** is used to tackle the problem of answering a complex query using multiple data sources. It first breaks down the complex query into sub-questions for each relevant data source, then gathers all the intermediate responses and synthesizes a final response.
UpTrain callback handler will automatically capture the sub-question and the responses for each of them once generated and will run the following three evaluations _(Graded from 0 to 1)_ on the response:
  * **Context Relevance** : Determines if the retrieved context has sufficient information to answer the user query or not.
  * **Factual Accuracy** : Assesses if the LLM's response can be verified via the retrieved context.
  * **Response Completeness** : Checks if the response contains all the information required to answer the user query comprehensively.


In addition to the above evaluations, the callback handler will also run the following evaluation:
  * **Sub Query Completeness** : Assures that the sub-questions accurately and comprehensively cover the original query.


In [ ]:
Copied!
```
# build index and query engine
vector_query_engine = VectorStoreIndex.from_documents(
    documents=documents,
    use_async=True,
).as_query_engine()

query_engine_tools = [
    QueryEngineTool(
        query_engine=vector_query_engine,
        metadata=ToolMetadata(
            name="documents",
            description="Paul Graham essay on What I Worked On",
        ),
    ),
]

query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
    use_async=True,
)

response = query_engine.query(
    "How was Paul Grahams life different before, during, and after YC?"
)

```

# build index and query engine vector_query_engine = VectorStoreIndex.from_documents( documents=documents, use_async=True, ).as_query_engine() query_engine_tools = [ QueryEngineTool( query_engine=vector_query_engine, metadata=ToolMetadata( name="documents", description="Paul Graham essay on What I Worked On", ), ), ] query_engine = SubQuestionQueryEngine.from_defaults( query_engine_tools=query_engine_tools, use_async=True, ) response = query_engine.query( "How was Paul Grahams life different before, during, and after YC?" )
```
Generated 3 sub questions.
[documents] Q: What did Paul Graham work on before YC?
[documents] Q: What did Paul Graham work on during YC?
[documents] Q: What did Paul Graham work on after YC?
[documents] A: After Y Combinator, Paul Graham decided to focus on painting as his next endeavor.
[documents] A: Paul Graham worked on writing essays and working on Y Combinator during YC.
[documents] A: Before Y Combinator, Paul Graham worked on projects with his colleagues Robert and Trevor.

```

```
100%|██████████| 3/3 [00:02<00:00,  1.47it/s]
100%|██████████| 3/3 [00:00<00:00,  3.28it/s]
100%|██████████| 3/3 [00:01<00:00,  1.68it/s]
100%|██████████| 3/3 [00:01<00:00,  2.28it/s]

```

```
Question: What did Paul Graham work on after YC?
Response: After Y Combinator, Paul Graham decided to focus on painting as his next endeavor.

Context Relevance Score: 0.0
Factual Accuracy Score: 0.0
Response Completeness Score: 0.5


Question: What did Paul Graham work on during YC?
Response: Paul Graham worked on writing essays and working on Y Combinator during YC.

Context Relevance Score: 0.0
Factual Accuracy Score: 1.0
Response Completeness Score: 0.5


Question: What did Paul Graham work on before YC?
Response: Before Y Combinator, Paul Graham worked on projects with his colleagues Robert and Trevor.

Context Relevance Score: 0.0
Factual Accuracy Score: 0.0
Response Completeness Score: 0.5


```

```
100%|██████████| 1/1 [00:01<00:00,  1.24s/it]
```

```
Question: How was Paul Grahams life different before, during, and after YC?
Sub Query Completeness Score: 1.0


```



# 3. Re-ranking¶
Re-ranking is the process of reordering the nodes based on their relevance to the query. There are multiple classes of re-ranking algorithms offered by Llamaindex. We have used LLMRerank for this example.
The re-ranker allows you to enter the number of top n nodes that will be returned after re-ranking. If this value remains the same as the original number of nodes, the re-ranker will only re-rank the nodes and not change the number of nodes. Otherwise, it will re-rank the nodes and return the top n nodes.
We will perform different evaluations based on the number of nodes returned after re-ranking.
## 3a. Re-ranking (With same number of nodes)¶
If the number of nodes returned after re-ranking is the same as the original number of nodes, the following evaluation will be performed:
  * **Context Reranking** : Checks if the order of re-ranked nodes is more relevant to the query than the original order.


In [ ]:
Copied!
```
callback_handler = UpTrainCallbackHandler(
    key_type="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    project_name="uptrain_llamaindex",
)
Settings.callback_manager = CallbackManager([callback_handler])

rerank_postprocessor = SentenceTransformerRerank(
    top_n=3,  # number of nodes after reranking
    keep_retrieval_score=True,
)

index = VectorStoreIndex.from_documents(
    documents=documents,
)

query_engine = index.as_query_engine(
    similarity_top_k=3,  # number of nodes before reranking
    node_postprocessors=[rerank_postprocessor],
)

response = query_engine.query(
    "What did Sam Altman do in this essay?",
)

```

callback_handler = UpTrainCallbackHandler( key_type="openai", api_key=os.environ["OPENAI_API_KEY"], project_name="uptrain_llamaindex", ) Settings.callback_manager = CallbackManager([callback_handler]) rerank_postprocessor = SentenceTransformerRerank( top_n=3, # number of nodes after reranking keep_retrieval_score=True, ) index = VectorStoreIndex.from_documents( documents=documents, ) query_engine = index.as_query_engine( similarity_top_k=3, # number of nodes before reranking node_postprocessors=[rerank_postprocessor], ) response = query_engine.query( "What did Sam Altman do in this essay?", )
```
100%|██████████| 1/1 [00:01<00:00,  1.89s/it]

```

```
Question: What did Sam Altman do in this essay?
Context Reranking Score: 1.0


```

```
100%|██████████| 1/1 [00:01<00:00,  1.88s/it]
100%|██████████| 1/1 [00:01<00:00,  1.44s/it]
100%|██████████| 1/1 [00:02<00:00,  2.77s/it]
100%|██████████| 1/1 [00:01<00:00,  1.45s/it]
```

```
Question: What did Sam Altman do in this essay?
Response: Sam Altman was asked to become the president of Y Combinator after the original founders decided to step down and reorganize the company for long-term sustainability.

Context Relevance Score: 1.0
Factual Accuracy Score: 1.0
Response Completeness Score: 0.5


```



# 3b. Re-ranking (With different number of nodes)¶
If the number of nodes returned after re-ranking is the lesser as the original number of nodes, the following evaluation will be performed:
  * **Context Conciseness** : Examines whether the reduced number of nodes still provides all the required information.


In [ ]:
Copied!
```
callback_handler = UpTrainCallbackHandler(
    key_type="openai",
    api_key=os.environ["OPENAI_API_KEY"],
    project_name="uptrain_llamaindex",
)
Settings.callback_manager = CallbackManager([callback_handler])

rerank_postprocessor = SentenceTransformerRerank(
    top_n=2,  # Number of nodes after re-ranking
    keep_retrieval_score=True,
)

index = VectorStoreIndex.from_documents(
    documents=documents,
)
query_engine = index.as_query_engine(
    similarity_top_k=5,  # Number of nodes before re-ranking
    node_postprocessors=[rerank_postprocessor],
)

# Use your advanced RAG
response = query_engine.query(
    "What did Sam Altman do in this essay?",
)

```

callback_handler = UpTrainCallbackHandler( key_type="openai", api_key=os.environ["OPENAI_API_KEY"], project_name="uptrain_llamaindex", ) Settings.callback_manager = CallbackManager([callback_handler]) rerank_postprocessor = SentenceTransformerRerank( top_n=2, # Number of nodes after re-ranking keep_retrieval_score=True, ) index = VectorStoreIndex.from_documents( documents=documents, ) query_engine = index.as_query_engine( similarity_top_k=5, # Number of nodes before re-ranking node_postprocessors=[rerank_postprocessor], ) # Use your advanced RAG response = query_engine.query( "What did Sam Altman do in this essay?", )
```
100%|██████████| 1/1 [00:02<00:00,  2.22s/it]

```

```
Question: What did Sam Altman do in this essay?
Context Conciseness Score: 0.0


```

```
100%|██████████| 1/1 [00:01<00:00,  1.58s/it]
100%|██████████| 1/1 [00:00<00:00,  1.19it/s]
100%|██████████| 1/1 [00:01<00:00,  1.62s/it]
100%|██████████| 1/1 [00:01<00:00,  1.42s/it]
```

```
Question: What did Sam Altman do in this essay?
Response: Sam Altman offered unsolicited advice to the author during a visit to California for interviews.

Context Relevance Score: 0.0
Factual Accuracy Score: 1.0
Response Completeness Score: 0.5


```



# UpTrain's Dashboard and Insights¶
Here's a short video showcasing the dashboard and the insights:
![llamaindex_uptrain.gif](https://uptrain-assets.s3.ap-south-1.amazonaws.com/images/llamaindex/llamaindex_uptrain.gif)
