# Query Pipeline with Routing¶
Here we showcase our query pipeline with routing.
Routing lets us dynamically choose underlying query pipelines to use given the query and a set of choices.
We offer this as an out-of-the-box abstraction in our Router Query Engine guide. Here we show you how to compose a similar pipeline using our Query Pipeline syntax - this allows you to not only define query engines but easily stitch it into a chain/DAG with other modules across the compute graph.
## Load Data¶
Load in the Paul Graham essay as an example.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt' -O pg_essay.txt

```

!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt' -O pg_essay.txt
```
--2024-01-10 12:31:00--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.111.133, 185.199.110.133, 185.199.108.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.111.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘pg_essay.txt’

pg_essay.txt        100%[===================>]  73.28K  --.-KB/s    in 0.01s   

2024-01-10 12:31:00 (6.32 MB/s) - ‘pg_essay.txt’ saved [75042/75042]


```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

reader = SimpleDirectoryReader(input_files=["pg_essay.txt"])
documents = reader.load_data()

```

from llama_index.core import SimpleDirectoryReader reader = SimpleDirectoryReader(input_files=["pg_essay.txt"]) documents = reader.load_data()
## Setup Query Pipeline with Routing¶
### Define Modules¶
We define llm, vector index, summary index, and prompt templates.
In [ ]:
Copied!
```
from llama_index.core.query_pipeline import QueryPipeline, InputComponent
from typing import Dict, Any, List, Optional
from llama_index.llms.openai import OpenAI
from llama_index.core import Document, VectorStoreIndex
from llama_index.core import SummaryIndex
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core import PromptTemplate
from llama_index.core.selectors import LLMSingleSelector

# define HyDE template
hyde_str = """\
Please write a passage to answer the question: {query_str}

Try to include as many key details as possible.

Passage: """
hyde_prompt = PromptTemplate(hyde_str)

# define llm
llm = OpenAI(model="gpt-3.5-turbo")


# define synthesizer
summarizer = TreeSummarize(llm=llm)

# define vector retriever
vector_index = VectorStoreIndex.from_documents(documents)
vector_query_engine = vector_index.as_query_engine(similarity_top_k=2)

# define summary query prompts + retrievers
summary_index = SummaryIndex.from_documents(documents)
summary_qrewrite_str = """\
Here's a question:
{query_str}

You are responsible for feeding the question to an agent that given context will try to answer the question.
The context may or may not be relevant. Rewrite the question to highlight the fact that
only some pieces of context (or none) maybe be relevant.
"""
summary_qrewrite_prompt = PromptTemplate(summary_qrewrite_str)
summary_query_engine = summary_index.as_query_engine()

# define selector
selector = LLMSingleSelector.from_defaults()

```

from llama_index.core.query_pipeline import QueryPipeline, InputComponent from typing import Dict, Any, List, Optional from llama_index.llms.openai import OpenAI from llama_index.core import Document, VectorStoreIndex from llama_index.core import SummaryIndex from llama_index.core.response_synthesizers import TreeSummarize from llama_index.core.schema import NodeWithScore, TextNode from llama_index.core import PromptTemplate from llama_index.core.selectors import LLMSingleSelector # define HyDE template hyde_str = """\ Please write a passage to answer the question: {query_str} Try to include as many key details as possible. Passage: """ hyde_prompt = PromptTemplate(hyde_str) # define llm llm = OpenAI(model="gpt-3.5-turbo") # define synthesizer summarizer = TreeSummarize(llm=llm) # define vector retriever vector_index = VectorStoreIndex.from_documents(documents) vector_query_engine = vector_index.as_query_engine(similarity_top_k=2) # define summary query prompts + retrievers summary_index = SummaryIndex.from_documents(documents) summary_qrewrite_str = """\ Here's a question: {query_str} You are responsible for feeding the question to an agent that given context will try to answer the question. The context may or may not be relevant. Rewrite the question to highlight the fact that only some pieces of context (or none) maybe be relevant. """ summary_qrewrite_prompt = PromptTemplate(summary_qrewrite_str) summary_query_engine = summary_index.as_query_engine() # define selector selector = LLMSingleSelector.from_defaults()
### Construct Query Pipelines¶
Define a query pipeline for vector index, summary index, and join it together with a router.
In [ ]:
Copied!
```
# define summary query pipeline
from llama_index.core.query_pipeline import RouterComponent

vector_chain = QueryPipeline(chain=[vector_query_engine])
summary_chain = QueryPipeline(
    chain=[summary_qrewrite_prompt, llm, summary_query_engine], verbose=True
)

choices = [
    "This tool answers specific questions about the document (not summary questions across the document)",
    "This tool answers summary questions about the document (not specific questions)",
]

router_c = RouterComponent(
    selector=selector,
    choices=choices,
    components=[vector_chain, summary_chain],
    verbose=True,
)
# top-level pipeline
qp = QueryPipeline(chain=[router_c], verbose=True)

```

# define summary query pipeline from llama_index.core.query_pipeline import RouterComponent vector_chain = QueryPipeline(chain=[vector_query_engine]) summary_chain = QueryPipeline( chain=[summary_qrewrite_prompt, llm, summary_query_engine], verbose=True ) choices = [ "This tool answers specific questions about the document (not summary questions across the document)", "This tool answers summary questions about the document (not specific questions)", ] router_c = RouterComponent( selector=selector, choices=choices, components=[vector_chain, summary_chain], verbose=True, ) # top-level pipeline qp = QueryPipeline(chain=[router_c], verbose=True)
## Try out Queries¶
In [ ]:
Copied!
```
# compare with sync method
response = qp.run("What did the author do during his time in YC?")
print(str(response))

```

# compare with sync method response = qp.run("What did the author do during his time in YC?") print(str(response))
```
> Running module c0a87442-3165-443d-9709-960e6ddafe7f with input: 
query: What did the author do during his time in YC?

Selecting component 0: The author used a tool to answer specific questions about the document, which suggests that he was engaged in analyzing and extracting specific information from the document during his time in YC..
During his time in YC, the author worked on various tasks related to running Y Combinator. This included selecting and helping founders, dealing with disputes between cofounders, figuring out when people were lying, and fighting with people who maltreated the startups. The author also worked on writing essays and internal software for YC.

```

In [ ]:
Copied!
```
response = qp.run("What is a summary of this document?")
print(str(response))

```

response = qp.run("What is a summary of this document?") print(str(response))
```
> Running module c0a87442-3165-443d-9709-960e6ddafe7f with input: 
query: What is a summary of this document?

Selecting component 1: The summary questions about the document are answered by this tool..
> Running module 0e7e9d49-4c92-45a9-b3bf-0e6ab76b51f9 with input: 
query_str: What is a summary of this document?

> Running module b0ece4e3-e6cd-4229-8663-b0cd0638683c with input: 
messages: Here's a question:
What is a summary of this document?

You are responsible for feeding the question to an agent that given context will try to answer the question.
The context may or may not be relev...

> Running module f247ae78-a71c-4347-ba49-d9357ee93636 with input: 
input: assistant: What is the summary of the document?

The document discusses the development and evolution of Lisp as a programming language. It highlights how Lisp was originally created as a formal model of computation and later transformed into a programming language with the assistance of Steve Russell. The document also emphasizes the unique power and elegance of Lisp in comparison to other languages.

```

