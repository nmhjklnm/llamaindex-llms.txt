![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# HotpotQADistractor Demo¶
This notebook walks through evaluating a query engine using the HotpotQA dataset. In this task, the LLM must answer a question given a pre-configured context. The answer usually has to be concise, and accuracy is measured by calculating the overlap (measured by F1) and exact match.
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
from llama_index.core.evaluation.benchmarks import HotpotQAEvaluator
from llama_index.core import VectorStoreIndex
from llama_index.core import Document
from llama_index.llms.openai import OpenAI
from llama_index.core.embeddings import resolve_embed_model

llm = OpenAI(model="gpt-3.5-turbo")
embed_model = resolve_embed_model(
    "local:sentence-transformers/all-MiniLM-L6-v2"
)

index = VectorStoreIndex.from_documents(
    [Document.example()], embed_model=embed_model, show_progress=True
)

```

from llama_index.core.evaluation.benchmarks import HotpotQAEvaluator from llama_index.core import VectorStoreIndex from llama_index.core import Document from llama_index.llms.openai import OpenAI from llama_index.core.embeddings import resolve_embed_model llm = OpenAI(model="gpt-3.5-turbo") embed_model = resolve_embed_model( "local:sentence-transformers/all-MiniLM-L6-v2" ) index = VectorStoreIndex.from_documents( [Document.example()], embed_model=embed_model, show_progress=True )
```
Parsing documents into nodes: 100%|██████████| 1/1 [00:00<00:00, 129.13it/s]
Generating embeddings: 100%|██████████| 1/1 [00:00<00:00, 36.62it/s]

```

First we try with a very simple engine. In this particular benchmark, the retriever and hence index is actually ignored, as the documents retrieved for each query is provided in the dataset. This is known as the "distractor" setting in HotpotQA.
In [ ]:
Copied!
```
engine = index.as_query_engine(llm=llm)

HotpotQAEvaluator().run(engine, queries=5, show_result=True)

```

engine = index.as_query_engine(llm=llm) HotpotQAEvaluator().run(engine, queries=5, show_result=True)
```
Dataset: hotpot_dev_distractor downloaded at: /Users/loganmarkewich/Library/Caches/llama_index/datasets/HotpotQA
Evaluating on dataset: hotpot_dev_distractor
-------------------------------------
Loading 5 queries out of 7405 (fraction: 0.00068)
Question:  Were Scott Derrickson and Ed Wood of the same nationality?
Response: No.
Correct answer:  yes
EM: 0 F1: 0
-------------------------------------
Question:  What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?
Response: Unknown
Correct answer:  Chief of Protocol
EM: 0 F1: 0
-------------------------------------
Question:  What science fantasy young adult series, told in first person, has a set of companion books narrating the stories of enslaved worlds and alien species?
Response: Animorphs
Correct answer:  Animorphs
EM: 1 F1: 1.0
-------------------------------------
Question:  Are the Laleli Mosque and Esma Sultan Mansion located in the same neighborhood?
Response: Yes.
Correct answer:  no
EM: 0 F1: 0
-------------------------------------
Question:  The director of the romantic comedy "Big Stone Gap" is based in what New York city?
Response: Greenwich Village
Correct answer:  Greenwich Village, New York City
EM: 0 F1: 0.5714285714285715
-------------------------------------
Scores:  {'exact_match': 0.2, 'f1': 0.31428571428571433}

```

Now we try with a sentence transformer reranker, which selects 3 out of the 10 nodes proposed by the retriever
In [ ]:
Copied!
```
from llama_index.core.postprocessor import SentenceTransformerRerank

rerank = SentenceTransformerRerank(top_n=3)

engine = index.as_query_engine(
    llm=llm,
    node_postprocessors=[rerank],
)

HotpotQAEvaluator().run(engine, queries=5, show_result=True)

```

from llama_index.core.postprocessor import SentenceTransformerRerank rerank = SentenceTransformerRerank(top_n=3) engine = index.as_query_engine( llm=llm, node_postprocessors=[rerank], ) HotpotQAEvaluator().run(engine, queries=5, show_result=True)
```
Dataset: hotpot_dev_distractor downloaded at: /Users/loganmarkewich/Library/Caches/llama_index/datasets/HotpotQA
Evaluating on dataset: hotpot_dev_distractor
-------------------------------------
Loading 5 queries out of 7405 (fraction: 0.00068)
Question:  Were Scott Derrickson and Ed Wood of the same nationality?
Response: No.
Correct answer:  yes
EM: 0 F1: 0
-------------------------------------
Question:  What government position was held by the woman who portrayed Corliss Archer in the film Kiss and Tell?
Response: No government position.
Correct answer:  Chief of Protocol
EM: 0 F1: 0
-------------------------------------
Question:  What science fantasy young adult series, told in first person, has a set of companion books narrating the stories of enslaved worlds and alien species?
Response: Animorphs
Correct answer:  Animorphs
EM: 1 F1: 1.0
-------------------------------------
Question:  Are the Laleli Mosque and Esma Sultan Mansion located in the same neighborhood?
Response: No.
Correct answer:  no
EM: 1 F1: 1.0
-------------------------------------
Question:  The director of the romantic comedy "Big Stone Gap" is based in what New York city?
Response: New York City.
Correct answer:  Greenwich Village, New York City
EM: 0 F1: 0.7499999999999999
-------------------------------------
Scores:  {'exact_match': 0.4, 'f1': 0.55}

```

The F1 and exact match scores appear to improve slightly.
Note that the benchmark optimizes for producing short factoid answers without explanations, although it is known that CoT prompting can sometimes help in output quality.
The scores used are also not a perfect measure of correctness, but can be a quick way to identify how changes in your query engine change the output.
