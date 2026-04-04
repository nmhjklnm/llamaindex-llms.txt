![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Automated Metadata Extraction for Better Retrieval + Synthesis¶
In this tutorial, we show you how to perform automated metadata extraction for better retrieval results. We use two extractors: a QuestionAnsweredExtractor which generates question/answer pairs from a piece of text, and also a SummaryExtractor which extracts summaries, not only within the current text, but also within adjacent texts.
We show that this allows for "chunk dreaming" - each individual chunk can have more "holistic" details, leading to higher answer quality given retrieved results.
Our data source is taken from Eugene Yan's popular article on LLM Patterns: https://eugeneyan.com/writing/llm-patterns/
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-readers-web

```

%pip install llama-index-llms-openai %pip install llama-index-readers-web
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

import os
import openai

```

import nest_asyncio nest_asyncio.apply() import os import openai
In [ ]:
Copied!
```
# OPTIONAL: setup W&B callback handling for tracing
from llama_index.core import set_global_handler

set_global_handler("wandb", run_args={"project": "llamaindex"})

```

# OPTIONAL: setup W&B callback handling for tracing from llama_index.core import set_global_handler set_global_handler("wandb", run_args={"project": "llamaindex"})
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "sk-..."
openai.api_key = os.environ["OPENAI_API_KEY"]

```

os.environ["OPENAI_API_KEY"] = "sk-..." openai.api_key = os.environ["OPENAI_API_KEY"]
## Define Metadata Extractors¶
Here we define metadata extractors. We define two variants:
  * metadata_extractor_1 only contains the QuestionsAnsweredExtractor
  * metadata_extractor_2 contains both the QuestionsAnsweredExtractor as well as the SummaryExtractor


In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.schema import MetadataMode

```

from llama_index.llms.openai import OpenAI from llama_index.core.schema import MetadataMode
In [ ]:
Copied!
```
llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", max_tokens=512)

```

llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo", max_tokens=512)
We also show how to instantiate the `SummaryExtractor` and `QuestionsAnsweredExtractor`.
In [ ]:
Copied!
```
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
)

node_parser = TokenTextSplitter(
    separator=" ", chunk_size=256, chunk_overlap=128
)


extractors_1 = [
    QuestionsAnsweredExtractor(
        questions=3, llm=llm, metadata_mode=MetadataMode.EMBED
    ),
]

extractors_2 = [
    SummaryExtractor(summaries=["prev", "self", "next"], llm=llm),
    QuestionsAnsweredExtractor(
        questions=3, llm=llm, metadata_mode=MetadataMode.EMBED
    ),
]

```

from llama_index.core.node_parser import TokenTextSplitter from llama_index.core.extractors import ( SummaryExtractor, QuestionsAnsweredExtractor, ) node_parser = TokenTextSplitter( separator=" ", chunk_size=256, chunk_overlap=128 ) extractors_1 = [ QuestionsAnsweredExtractor( questions=3, llm=llm, metadata_mode=MetadataMode.EMBED ), ] extractors_2 = [ SummaryExtractor(summaries=["prev", "self", "next"], llm=llm), QuestionsAnsweredExtractor( questions=3, llm=llm, metadata_mode=MetadataMode.EMBED ), ]
## Load in Data, Run Extractors¶
We load in Eugene's essay (https://eugeneyan.com/writing/llm-patterns/) using our LlamaHub SimpleWebPageReader.
We then run our extractors.
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

```

from llama_index.core import SimpleDirectoryReader
In [ ]:
Copied!
```
# load in blog

from llama_index.readers.web import SimpleWebPageReader

reader = SimpleWebPageReader(html_to_text=True)
docs = reader.load_data(urls=["https://eugeneyan.com/writing/llm-patterns/"])

```

# load in blog from llama_index.readers.web import SimpleWebPageReader reader = SimpleWebPageReader(html_to_text=True) docs = reader.load_data(urls=["https://eugeneyan.com/writing/llm-patterns/"])
In [ ]:
Copied!
```
print(docs[0].get_content())

```

print(docs[0].get_content())
In [ ]:
Copied!
```
orig_nodes = node_parser.get_nodes_from_documents(docs)

```

orig_nodes = node_parser.get_nodes_from_documents(docs)
In [ ]:
Copied!
```
# take just the first 8 nodes for testing
nodes = orig_nodes[20:28]

```

# take just the first 8 nodes for testing nodes = orig_nodes[20:28]
In [ ]:
Copied!
```
print(nodes[3].get_content(metadata_mode="all"))

```

print(nodes[3].get_content(metadata_mode="all"))
```
is to measure the distance that words would
have to move to convert one sequence to another.

However, there are several pitfalls to using these conventional benchmarks and
metrics.

First, there’s **poor correlation between these metrics and human judgments.**
BLEU, ROUGE, and others have had [negative correlation with how humans
evaluate fluency](https://arxiv.org/abs/2008.12009). They also showed moderate
to less correlation with human adequacy scores. In particular, BLEU and ROUGE
have [low correlation with tasks that require creativity and
diversity](https://arxiv.org/abs/2303.16634).

Second, these metrics often have **poor adaptability to a wider variety of
tasks**. Adopting a metric proposed for one task to another is not always
prudent. For example, exact match metrics such as BLEU and ROUGE are a poor
fit for tasks like abstractive summarization or dialogue. Since they’re based
on n-gram overlap between output and reference, they don’t make sense for a
dialogue task where a wide variety

```

### Run metadata extractors¶
In [ ]:
Copied!
```
from llama_index.core.ingestion import IngestionPipeline

# process nodes with metadata extractors
pipeline = IngestionPipeline(transformations=[node_parser, *extractors_1])

nodes_1 = pipeline.run(nodes=nodes, in_place=False, show_progress=True)

```

from llama_index.core.ingestion import IngestionPipeline # process nodes with metadata extractors pipeline = IngestionPipeline(transformations=[node_parser, *extractors_1]) nodes_1 = pipeline.run(nodes=nodes, in_place=False, show_progress=True)
```
Parsing documents into nodes:   0%|          | 0/8 [00:00<?, ?it/s]
```

```
Extracting questions:   0%|          | 0/8 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
print(nodes_1[3].get_content(metadata_mode="all"))

```

print(nodes_1[3].get_content(metadata_mode="all"))
```
[Excerpt from document]
questions_this_excerpt_can_answer: 1. What is the correlation between conventional metrics like BLEU and ROUGE and human judgments in evaluating fluency and adequacy in natural language processing tasks?
2. How do conventional metrics like BLEU and ROUGE perform in tasks that require creativity and diversity?
3. Why are exact match metrics like BLEU and ROUGE not suitable for tasks like abstractive summarization or dialogue in natural language processing?
Excerpt:
-----
is to measure the distance that words would
have to move to convert one sequence to another.

However, there are several pitfalls to using these conventional benchmarks and
metrics.

First, there’s **poor correlation between these metrics and human judgments.**
BLEU, ROUGE, and others have had [negative correlation with how humans
evaluate fluency](https://arxiv.org/abs/2008.12009). They also showed moderate
to less correlation with human adequacy scores. In particular, BLEU and ROUGE
have [low correlation with tasks that require creativity and
diversity](https://arxiv.org/abs/2303.16634).

Second, these metrics often have **poor adaptability to a wider variety of
tasks**. Adopting a metric proposed for one task to another is not always
prudent. For example, exact match metrics such as BLEU and ROUGE are a poor
fit for tasks like abstractive summarization or dialogue. Since they’re based
on n-gram overlap between output and reference, they don’t make sense for a
dialogue task where a wide variety
-----

```

In [ ]:
Copied!
```
# 2nd pass: run summaries, and then metadata extractor

# process nodes with metadata extractor
pipeline = IngestionPipeline(transformations=[node_parser, *extractors_2])

nodes_2 = pipeline.run(nodes=nodes, in_place=False, show_progress=True)

```

# 2nd pass: run summaries, and then metadata extractor # process nodes with metadata extractor pipeline = IngestionPipeline(transformations=[node_parser, *extractors_2]) nodes_2 = pipeline.run(nodes=nodes, in_place=False, show_progress=True)
```
Parsing documents into nodes:   0%|          | 0/8 [00:00<?, ?it/s]
```

```
Extracting summaries:   0%|          | 0/8 [00:00<?, ?it/s]
```

```
Extracting questions:   0%|          | 0/8 [00:00<?, ?it/s]
```

### Visualize some sample data¶
In [ ]:
Copied!
```
print(nodes_2[3].get_content(metadata_mode="all"))

```

print(nodes_2[3].get_content(metadata_mode="all"))
```
[Excerpt from document]
prev_section_summary: The section discusses the comparison between BERTScore and MoverScore, two metrics used to evaluate the quality of text generation models. MoverScore is described as a metric that measures the effort required to transform one text sequence into another by mapping semantically related words. The section also highlights the limitations of conventional benchmarks and metrics, such as poor correlation with human judgments and low correlation with tasks requiring creativity.
next_section_summary: The section discusses the limitations of current evaluation metrics in natural language processing tasks. It highlights three main issues: lack of creativity and diversity in metrics, poor adaptability to different tasks, and poor reproducibility. The section mentions specific metrics like BLEU and ROUGE, and also references studies that have reported high variance in metric scores.
section_summary: The section discusses the limitations of conventional benchmarks and metrics used to measure the distance between word sequences. It highlights two main issues: the poor correlation between these metrics and human judgments, and their limited adaptability to different tasks. The section mentions specific metrics like BLEU and ROUGE, which have been found to have low correlation with human evaluations of fluency, adequacy, creativity, and diversity. It also points out that metrics based on n-gram overlap, such as BLEU and ROUGE, are not suitable for tasks like abstractive summarization or dialogue.
questions_this_excerpt_can_answer: 1. What are the limitations of conventional benchmarks and metrics in measuring the distance between word sequences?
2. How do metrics like BLEU and ROUGE correlate with human judgments in terms of fluency, adequacy, creativity, and diversity?
3. Why are metrics based on n-gram overlap, such as BLEU and ROUGE, not suitable for tasks like abstractive summarization or dialogue?
Excerpt:
-----
is to measure the distance that words would
have to move to convert one sequence to another.

However, there are several pitfalls to using these conventional benchmarks and
metrics.

First, there’s **poor correlation between these metrics and human judgments.**
BLEU, ROUGE, and others have had [negative correlation with how humans
evaluate fluency](https://arxiv.org/abs/2008.12009). They also showed moderate
to less correlation with human adequacy scores. In particular, BLEU and ROUGE
have [low correlation with tasks that require creativity and
diversity](https://arxiv.org/abs/2303.16634).

Second, these metrics often have **poor adaptability to a wider variety of
tasks**. Adopting a metric proposed for one task to another is not always
prudent. For example, exact match metrics such as BLEU and ROUGE are a poor
fit for tasks like abstractive summarization or dialogue. Since they’re based
on n-gram overlap between output and reference, they don’t make sense for a
dialogue task where a wide variety
-----

```

In [ ]:
Copied!
```
print(nodes_2[1].get_content(metadata_mode="all"))

```

print(nodes_2[1].get_content(metadata_mode="all"))
```
[Excerpt from document]
prev_section_summary: The section discusses the F_{BERT} formula used in BERTScore and highlights the advantages of BERTScore over simpler metrics like BLEU and ROUGE. It also introduces MoverScore, another metric that uses contextualized embeddings but allows for many-to-one matching. The key topics are BERTScore, MoverScore, and the differences between them.
next_section_summary: The section discusses the comparison between BERTScore and MoverScore, two metrics used to evaluate the quality of text generation models. MoverScore is described as a metric that measures the effort required to transform one text sequence into another by mapping semantically related words. The section also highlights the limitations of conventional benchmarks and metrics, such as poor correlation with human judgments and low correlation with tasks requiring creativity.
section_summary: The key topics of this section are BERTScore and MoverScore, which are methods used to compute the similarity between generated output and reference in tasks like image captioning and machine translation. BERTScore uses one-to-one matching of tokens, while MoverScore allows for many-to-one matching. MoverScore solves an optimization problem to measure the distance that words would have to move to convert one sequence to another.
questions_this_excerpt_can_answer: 1. What is the main difference between BERTScore and MoverScore?
2. How does MoverScore allow for many-to-one matching of tokens?
3. What problem does MoverScore solve to measure the distance between two sequences?
Excerpt:
-----
to have better correlation for tasks
such as image captioning and machine translation.

**[MoverScore](https://arxiv.org/abs/1909.02622)** also uses contextualized
embeddings to compute the distance between tokens in the generated output and
reference. But unlike BERTScore, which is based on one-to-one matching (or
“hard alignment”) of tokens, MoverScore allows for many-to-one matching (or
“soft alignment”).

![BERTScore \(left\) vs. MoverScore \(right\)](/assets/mover-score.jpg)

BERTScore (left) vs. MoverScore (right;
[source](https://arxiv.org/abs/1909.02622))

MoverScore enables the mapping of semantically related words in one sequence
to their counterparts in another sequence. It does this by solving a
constrained optimization problem that finds the minimum effort to transform
one text into another. The idea is to measure the distance that words would
have to move to convert one sequence to another.

However, there
-----

```

## Setup RAG Query Engines, Compare Results!¶
We setup 3 indexes/query engines on top of the three node variants.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.response.notebook_utils import (
    display_source_node,
    display_response,
)

```

from llama_index.core import VectorStoreIndex from llama_index.core.response.notebook_utils import ( display_source_node, display_response, )
In [ ]:
Copied!
```
# try out different query engines

# index0 = VectorStoreIndex(orig_nodes)
# index1 = VectorStoreIndex(nodes_1 + orig_nodes[8:])
# index2 = VectorStoreIndex(nodes_2 + orig_nodes[8:])

index0 = VectorStoreIndex(orig_nodes)
index1 = VectorStoreIndex(orig_nodes[:20] + nodes_1 + orig_nodes[28:])
index2 = VectorStoreIndex(orig_nodes[:20] + nodes_2 + orig_nodes[28:])

```

# try out different query engines # index0 = VectorStoreIndex(orig_nodes) # index1 = VectorStoreIndex(nodes_1 + orig_nodes[8:]) # index2 = VectorStoreIndex(nodes_2 + orig_nodes[8:]) index0 = VectorStoreIndex(orig_nodes) index1 = VectorStoreIndex(orig_nodes[:20] + nodes_1 + orig_nodes[28:]) index2 = VectorStoreIndex(orig_nodes[:20] + nodes_2 + orig_nodes[28:])
In [ ]:
Copied!
```
query_engine0 = index0.as_query_engine(similarity_top_k=1)
query_engine1 = index1.as_query_engine(similarity_top_k=1)
query_engine2 = index2.as_query_engine(similarity_top_k=1)

```

query_engine0 = index0.as_query_engine(similarity_top_k=1) query_engine1 = index1.as_query_engine(similarity_top_k=1) query_engine2 = index2.as_query_engine(similarity_top_k=1)
### Try out some questions¶
In this question, we see that the naive response `response0` only mentions BLEU and ROUGE, and lacks context about other metrics.
`response2` on the other hand has all metrics within its context.
In [ ]:
Copied!
```
# query_str = "In the original RAG paper, can you describe the two main approaches for generation and compare them?"
query_str = (
    "Can you describe metrics for evaluating text generation quality, compare"
    " them, and tell me about their downsides"
)

response0 = query_engine0.query(query_str)
response1 = query_engine1.query(query_str)
response2 = query_engine2.query(query_str)

```

# query_str = "In the original RAG paper, can you describe the two main approaches for generation and compare them?" query_str = ( "Can you describe metrics for evaluating text generation quality, compare" " them, and tell me about their downsides" ) response0 = query_engine0.query(query_str) response1 = query_engine1.query(query_str) response2 = query_engine2.query(query_str)
In [ ]:
Copied!
```
display_response(
    response0, source_length=1000, show_source=True, show_source_metadata=True
)

```

display_response( response0, source_length=1000, show_source=True, show_source_metadata=True )
In [ ]:
Copied!
```
print(response0.source_nodes[0].node.get_content())

```

print(response0.source_nodes[0].node.get_content())
```
require creativity and
diversity](https://arxiv.org/abs/2303.16634).

Second, these metrics often have **poor adaptability to a wider variety of
tasks**. Adopting a metric proposed for one task to another is not always
prudent. For example, exact match metrics such as BLEU and ROUGE are a poor
fit for tasks like abstractive summarization or dialogue. Since they’re based
on n-gram overlap between output and reference, they don’t make sense for a
dialogue task where a wide variety of responses are possible. An output can
have zero n-gram overlap with the reference but yet be a good response.

Third, these metrics have **poor reproducibility**. Even for the same metric,
[high variance is reported across different
studies](https://arxiv.org/abs/2008.12009), possibly due to variations in
human judgment collection or metric parameter settings. Another study of
[ROUGE scores](https://aclanthology.org/2023.acl-long.107/) across 2,000
studies found that scores were hard

```

In [ ]:
Copied!
```
display_response(
    response1, source_length=1000, show_source=True, show_source_metadata=True
)

```

display_response( response1, source_length=1000, show_source=True, show_source_metadata=True )
In [ ]:
Copied!
```
display_response(
    response2, source_length=1000, show_source=True, show_source_metadata=True
)

```

display_response( response2, source_length=1000, show_source=True, show_source_metadata=True )
In this next question, we ask about BERTScore/MoverScore.
The responses are similar. But `response2` gives slightly more detail than `response0` since it has more information about MoverScore contained in the Metadata.
In [ ]:
Copied!
```
# query_str = "What are some reproducibility issues with the ROUGE metric? Give some details related to benchmarks and also describe other ROUGE issues. "
query_str = (
    "Can you give a high-level overview of BERTScore/MoverScore + formulas if"
    " available?"
)

response0 = query_engine0.query(query_str)
response1 = query_engine1.query(query_str)
response2 = query_engine2.query(query_str)

```

# query_str = "What are some reproducibility issues with the ROUGE metric? Give some details related to benchmarks and also describe other ROUGE issues. " query_str = ( "Can you give a high-level overview of BERTScore/MoverScore + formulas if" " available?" ) response0 = query_engine0.query(query_str) response1 = query_engine1.query(query_str) response2 = query_engine2.query(query_str)
In [ ]:
Copied!
```
display_response(
    response0, source_length=1000, show_source=True, show_source_metadata=True
)

```

display_response( response0, source_length=1000, show_source=True, show_source_metadata=True )
In [ ]:
Copied!
```
display_response(
    response1, source_length=1000, show_source=True, show_source_metadata=True
)

```

display_response( response1, source_length=1000, show_source=True, show_source_metadata=True )
In [ ]:
Copied!
```
display_response(
    response2, source_length=1000, show_source=True, show_source_metadata=True
)

```

display_response( response2, source_length=1000, show_source=True, show_source_metadata=True )
In [ ]:
Copied!
```
response1.source_nodes[0].node.metadata

```

response1.source_nodes[0].node.metadata
Out[ ]:
```
{'questions_this_excerpt_can_answer': '1. What is the advantage of using BERTScore over simpler metrics like BLEU and ROUGE?\n2. How does MoverScore differ from BERTScore in terms of token matching?\n3. What tasks have shown better correlation with BERTScore, such as image captioning and machine translation?'}
```

