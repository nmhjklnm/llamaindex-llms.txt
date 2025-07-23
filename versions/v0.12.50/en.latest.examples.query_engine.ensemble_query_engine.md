![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Ensemble Query Engine Guide¶
Oftentimes when building a RAG application there are different query pipelines you need to experiment with (e.g. top-k retrieval, keyword search, knowledge graphs).
Thought: what if we could try a bunch of strategies at once, and have the LLM 1) rate the relevance of each query, and 2) synthesize the results?
This guide showcases this over the Great Gatsby. We do ensemble retrieval over different chunk sizes and also different indices.
**NOTE** : Please also see our closely-related Ensemble Retrieval Guide!
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
## Setup¶
In [ ]:
Copied!
```
# NOTE: This is ONLY necessary in jupyter notebook.
# Details: Jupyter runs an event-loop behind the scenes.
#          This results in nested event-loops when we start an event-loop to make async queries.
#          This is normally not allowed, we use nest_asyncio to allow it for convenience.
import nest_asyncio

nest_asyncio.apply()

```

# NOTE: This is ONLY necessary in jupyter notebook. # Details: Jupyter runs an event-loop behind the scenes. # This results in nested event-loops when we start an event-loop to make async queries. # This is normally not allowed, we use nest_asyncio to allow it for convenience. import nest_asyncio nest_asyncio.apply()
## Download Data¶
In [ ]:
Copied!
```
!wget 'https://raw.githubusercontent.com/jerryjliu/llama_index/main/examples/gatsby/gatsby_full.txt' -O 'gatsby_full.txt'

```

!wget 'https://raw.githubusercontent.com/jerryjliu/llama_index/main/examples/gatsby/gatsby_full.txt' -O 'gatsby_full.txt'
## Load Data¶
We first show how to convert a Document into a set of Nodes, and insert into a DocumentStore.
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

# try loading great gatsby

documents = SimpleDirectoryReader(
    input_files=["./gatsby_full.txt"]
).load_data()

```

from llama_index.core import SimpleDirectoryReader # try loading great gatsby documents = SimpleDirectoryReader( input_files=["./gatsby_full.txt"] ).load_data()
## Define Query Engines¶
In [ ]:
Copied!
```
# initialize settings (set chunk size)
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.chunk_size = 1024

nodes = Settings.node_parser.get_nodes_from_documents(documents)

```

# initialize settings (set chunk size) from llama_index.llms.openai import OpenAI from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-3.5-turbo") Settings.chunk_size = 1024 nodes = Settings.node_parser.get_nodes_from_documents(documents)
In [ ]:
Copied!
```
from llama_index.core import StorageContext

# initialize storage context (by default it's in-memory)
storage_context = StorageContext.from_defaults()
storage_context.docstore.add_documents(nodes)

```

from llama_index.core import StorageContext # initialize storage context (by default it's in-memory) storage_context = StorageContext.from_defaults() storage_context.docstore.add_documents(nodes)
In [ ]:
Copied!
```
from llama_index.core import SimpleKeywordTableIndex, VectorStoreIndex

keyword_index = SimpleKeywordTableIndex(
    nodes,
    storage_context=storage_context,
    show_progress=True,
)
vector_index = VectorStoreIndex(
    nodes,
    storage_context=storage_context,
    show_progress=True,
)

```

from llama_index.core import SimpleKeywordTableIndex, VectorStoreIndex keyword_index = SimpleKeywordTableIndex( nodes, storage_context=storage_context, show_progress=True, ) vector_index = VectorStoreIndex( nodes, storage_context=storage_context, show_progress=True, )
```
Extracting keywords from nodes:   0%|          | 0/77 [00:00<?, ?it/s]
```

```
Generating embeddings:   0%|          | 0/77 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
from llama_index.core import PromptTemplate

QA_PROMPT_TMPL = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the question. If the answer is not in the context, inform "
    "the user that you can't answer the question - DO NOT MAKE UP AN ANSWER.\n"
    "In addition to returning the answer, also return a relevance score as to "
    "how relevant the answer is to the question. "
    "Question: {query_str}\n"
    "Answer (including relevance score): "
)
QA_PROMPT = PromptTemplate(QA_PROMPT_TMPL)

keyword_query_engine = keyword_index.as_query_engine(
    text_qa_template=QA_PROMPT
)
vector_query_engine = vector_index.as_query_engine(text_qa_template=QA_PROMPT)

```

from llama_index.core import PromptTemplate QA_PROMPT_TMPL = ( "Context information is below.\n" "---------------------\n" "{context_str}\n" "---------------------\n" "Given the context information and not prior knowledge, " "answer the question. If the answer is not in the context, inform " "the user that you can't answer the question - DO NOT MAKE UP AN ANSWER.\n" "In addition to returning the answer, also return a relevance score as to " "how relevant the answer is to the question. " "Question: {query_str}\n" "Answer (including relevance score): " ) QA_PROMPT = PromptTemplate(QA_PROMPT_TMPL) keyword_query_engine = keyword_index.as_query_engine( text_qa_template=QA_PROMPT ) vector_query_engine = vector_index.as_query_engine(text_qa_template=QA_PROMPT)
In [ ]:
Copied!
```
response = vector_query_engine.query(
    "Describe and summarize the interactions between Gatsby and Daisy"
)

```

response = vector_query_engine.query( "Describe and summarize the interactions between Gatsby and Daisy" )
In [ ]:
Copied!
```
print(response)

```

print(response)
```
Gatsby and Daisy's interactions are described as intimate and conspiring. They sit opposite each other at a kitchen table, with Gatsby's hand covering Daisy's hand. They communicate through nods and seem to have a natural intimacy. Gatsby waits for Daisy to go to bed and is reluctant to leave until he knows what she will do. They have a conversation in which Gatsby tells the story of his youth with Dan Cody. Daisy's face is smeared with tears, but Gatsby glows with a new well-being. Gatsby invites Daisy to his house and expresses his desire for her to come. They admire Gatsby's house together and discuss the interesting people who visit. The relevance score of this answer is 10/10.

```

In [ ]:
Copied!
```
response = keyword_query_engine.query(
    "Describe and summarize the interactions between Gatsby and Daisy"
)

```

response = keyword_query_engine.query( "Describe and summarize the interactions between Gatsby and Daisy" )
```
> Starting query: Describe and summarize the interactions between Gatsby and Daisy
query keywords: ['describe', 'interactions', 'gatsby', 'summarize', 'daisy']
> Extracted keywords: ['gatsby', 'daisy']

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The interactions between Gatsby and Daisy are characterized by a sense of tension and longing. Gatsby is visibly disappointed when Daisy expresses her dissatisfaction with their time together and insists that she didn't have a good time. He feels distant from her and struggles to make her understand his emotions. Gatsby dismisses the significance of the dance and instead focuses on his desire for Daisy to confess her love for him and leave Tom. He yearns for a deep connection with Daisy, but feels that she doesn't fully comprehend his feelings. These interactions highlight the complexities of their relationship and the challenges they face in rekindling their romance. The relevance score for these interactions is 8 out of 10.

```

## Define Router Query Engine¶
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool


keyword_tool = QueryEngineTool.from_defaults(
    query_engine=keyword_query_engine,
    description="Useful for answering questions about this essay",
)

vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description="Useful for answering questions about this essay",
)

```

from llama_index.core.tools import QueryEngineTool keyword_tool = QueryEngineTool.from_defaults( query_engine=keyword_query_engine, description="Useful for answering questions about this essay", ) vector_tool = QueryEngineTool.from_defaults( query_engine=vector_query_engine, description="Useful for answering questions about this essay", )
In [ ]:
Copied!
```
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)
from llama_index.core.response_synthesizers import TreeSummarize

TREE_SUMMARIZE_PROMPT_TMPL = (
    "Context information from multiple sources is below. Each source may or"
    " may not have \na relevance score attached to"
    " it.\n---------------------\n{context_str}\n---------------------\nGiven"
    " the information from multiple sources and their associated relevance"
    " scores (if provided) and not prior knowledge, answer the question. If"
    " the answer is not in the context, inform the user that you can't answer"
    " the question.\nQuestion: {query_str}\nAnswer: "
)

tree_summarize = TreeSummarize(
    summary_template=PromptTemplate(TREE_SUMMARIZE_PROMPT_TMPL)
)

query_engine = RouterQueryEngine(
    selector=LLMMultiSelector.from_defaults(),
    query_engine_tools=[
        keyword_tool,
        vector_tool,
    ],
    summarizer=tree_summarize,
)

```

from llama_index.core.query_engine import RouterQueryEngine from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector from llama_index.core.selectors import ( PydanticMultiSelector, PydanticSingleSelector, ) from llama_index.core.response_synthesizers import TreeSummarize TREE_SUMMARIZE_PROMPT_TMPL = ( "Context information from multiple sources is below. Each source may or" " may not have \na relevance score attached to" " it.\n---------------------\n{context_str}\n---------------------\nGiven" " the information from multiple sources and their associated relevance" " scores (if provided) and not prior knowledge, answer the question. If" " the answer is not in the context, inform the user that you can't answer" " the question.\nQuestion: {query_str}\nAnswer: " ) tree_summarize = TreeSummarize( summary_template=PromptTemplate(TREE_SUMMARIZE_PROMPT_TMPL) ) query_engine = RouterQueryEngine( selector=LLMMultiSelector.from_defaults(), query_engine_tools=[ keyword_tool, vector_tool, ], summarizer=tree_summarize, )
## Experiment with Queries¶
In [ ]:
Copied!
```
response = await query_engine.aquery(
    "Describe and summarize the interactions between Gatsby and Daisy"
)
print(response)

```

response = await query_engine.aquery( "Describe and summarize the interactions between Gatsby and Daisy" ) print(response)
```
message='OpenAI API response' path=https://api.openai.com/v1/chat/completions processing_ms=1590 request_id=b049001384d0e2f2d96e308903351ca3 response_code=200
Selecting query engine 0: Useful for answering questions about this essay.
Selecting query engine 1: Useful for answering questions about this essay.
> Starting query: Describe and summarize the interactions between Gatsby and Daisy
query keywords: ['interactions', 'summarize', 'describe', 'daisy', 'gatsby']
> Extracted keywords: ['daisy', 'gatsby']
message='OpenAI API response' path=https://api.openai.com/v1/embeddings processing_ms=75 request_id=3f76f611bb063605c3c2365437480f87 response_code=200
message='OpenAI API response' path=https://api.openai.com/v1/chat/completions processing_ms=4482 request_id=597221bd776638356f16034c4d8ad2f6 response_code=200
message='OpenAI API response' path=https://api.openai.com/v1/chat/completions processing_ms=5773 request_id=50a6030879054f470a1e45952b4b80b3 response_code=200
message='OpenAI API response' path=https://api.openai.com/v1/chat/completions processing_ms=6478 request_id=9171e42c7ced18baedc77cc89ec7478c response_code=200
message='OpenAI API response' path=https://api.openai.com/v1/chat/completions processing_ms=6166 request_id=f3218012e3f9a12e00daeee0b9b06f67 response_code=200
message='OpenAI API response' path=https://api.openai.com/v1/chat/completions processing_ms=4808 request_id=ab6887cbec9a44c2342d6402e28129d6 response_code=200
Combining responses from multiple query engines.
message='OpenAI API response' path=https://api.openai.com/v1/chat/completions processing_ms=4506 request_id=5fd128dab043f58111521d19e7c4f59a response_code=200
The interactions between Gatsby and Daisy are portrayed as intense, passionate, and filled with longing and desire. Gatsby is deeply in love with Daisy and throws extravagant parties in the hopes of winning her back. Despite Daisy's marriage to Tom Buchanan, they reconnect and begin an affair. They spend time together at Gatsby's lavish house and even plan to run away together. However, their relationship ends tragically when Daisy accidentally kills Tom's mistress, Myrtle, while driving Gatsby's car. Gatsby takes the blame for the accident and is later killed by Myrtle's husband. Overall, their interactions explore themes of love, wealth, and the pursuit of happiness.

```

In [ ]:
Copied!
```
response.source_nodes

```

response.source_nodes
Out[ ]:
```
[]
```

In [ ]:
Copied!
```
response = await query_engine.aquery(
    "What part of his past is Gatsby trying to recapture?"
)
print(response)

```

response = await query_engine.aquery( "What part of his past is Gatsby trying to recapture?" ) print(response)
```
Selecting query engine 0: Keywords: Gatsby, past, recapture.
> Starting query: What part of his past is Gatsby trying to recapture?
query keywords: ['gatsby', 'past', 'recapture']
> Extracted keywords: ['gatsby', 'past']

```

```
KeyboardInterrupt


```

