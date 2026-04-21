![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Defining a Custom Query Engine¶
You can (and should) define your custom query engines in order to plug into your downstream LlamaIndex workflows, whether you're building RAG, agents, or other applications.
We provide a `CustomQueryEngine` that makes it easy to define your own queries.
## Setup¶
We first load some sample data and index it.
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
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data//paul_graham/").load_data()

```

# load documents documents = SimpleDirectoryReader("./data//paul_graham/").load_data()
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)
retriever = index.as_retriever()

```

index = VectorStoreIndex.from_documents(documents) retriever = index.as_retriever()
## Building a Custom Query Engine¶
We build a custom query engine that simulates a RAG pipeline. First perform retrieval, and then synthesis.
To define a `CustomQueryEngine`, you just have to define some initialization parameters as attributes and implement the `custom_query` function.
By default, the `custom_query` can return a `Response` object (which the response synthesizer returns), but it can also just return a string. These are options 1 and 2 respectively.
In [ ]:
Copied!
```
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.retrievers import BaseRetriever
from llama_index.core import get_response_synthesizer
from llama_index.core.response_synthesizers import BaseSynthesizer

```

from llama_index.core.query_engine import CustomQueryEngine from llama_index.core.retrievers import BaseRetriever from llama_index.core import get_response_synthesizer from llama_index.core.response_synthesizers import BaseSynthesizer
### Option 1 (`RAGQueryEngine`)¶
In [ ]:
Copied!
```
class RAGQueryEngine(CustomQueryEngine):
    """RAG Query Engine."""

    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer

    def custom_query(self, query_str: str):
        nodes = self.retriever.retrieve(query_str)
        response_obj = self.response_synthesizer.synthesize(query_str, nodes)
        return response_obj

```

class RAGQueryEngine(CustomQueryEngine): """RAG Query Engine.""" retriever: BaseRetriever response_synthesizer: BaseSynthesizer def custom_query(self, query_str: str): nodes = self.retriever.retrieve(query_str) response_obj = self.response_synthesizer.synthesize(query_str, nodes) return response_obj
### Option 2 (`RAGStringQueryEngine`)¶
In [ ]:
Copied!
```
# Option 2: return a string (we use a raw LLM call for illustration)

from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

qa_prompt = PromptTemplate(
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query.\n"
    "Query: {query_str}\n"
    "Answer: "
)


class RAGStringQueryEngine(CustomQueryEngine):
    """RAG String Query Engine."""

    retriever: BaseRetriever
    response_synthesizer: BaseSynthesizer
    llm: OpenAI
    qa_prompt: PromptTemplate

    def custom_query(self, query_str: str):
        nodes = self.retriever.retrieve(query_str)

        context_str = "\n\n".join([n.node.get_content() for n in nodes])
        response = self.llm.complete(
            qa_prompt.format(context_str=context_str, query_str=query_str)
        )

        return str(response)

```

# Option 2: return a string (we use a raw LLM call for illustration) from llama_index.llms.openai import OpenAI from llama_index.core import PromptTemplate qa_prompt = PromptTemplate( "Context information is below.\n" "---------------------\n" "{context_str}\n" "---------------------\n" "Given the context information and not prior knowledge, " "answer the query.\n" "Query: {query_str}\n" "Answer: " ) class RAGStringQueryEngine(CustomQueryEngine): """RAG String Query Engine.""" retriever: BaseRetriever response_synthesizer: BaseSynthesizer llm: OpenAI qa_prompt: PromptTemplate def custom_query(self, query_str: str): nodes = self.retriever.retrieve(query_str) context_str = "\n\n".join([n.node.get_content() for n in nodes]) response = self.llm.complete( qa_prompt.format(context_str=context_str, query_str=query_str) ) return str(response)
## Trying it out¶
We now try it out on our sample data.
### Trying Option 1 (`RAGQueryEngine`)¶
In [ ]:
Copied!
```
synthesizer = get_response_synthesizer(response_mode="compact")
query_engine = RAGQueryEngine(
    retriever=retriever, response_synthesizer=synthesizer
)

```

synthesizer = get_response_synthesizer(response_mode="compact") query_engine = RAGQueryEngine( retriever=retriever, response_synthesizer=synthesizer )
In [ ]:
Copied!
```
response = query_engine.query("What did the author do growing up?")

```

response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The author worked on writing and programming outside of school before college. They wrote short stories and tried writing programs on an IBM 1401 computer using an early version of Fortran. They also mentioned getting a microcomputer, building it themselves, and writing simple games and programs on it.

```

In [ ]:
Copied!
```
print(response.source_nodes[0].get_content())

```

print(response.source_nodes[0].get_content())
### Trying Option 2 (`RAGStringQueryEngine`)¶
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-3.5-turbo")

query_engine = RAGStringQueryEngine(
    retriever=retriever,
    response_synthesizer=synthesizer,
    llm=llm,
    qa_prompt=qa_prompt,
)

```

llm = OpenAI(model="gpt-3.5-turbo") query_engine = RAGStringQueryEngine( retriever=retriever, response_synthesizer=synthesizer, llm=llm, qa_prompt=qa_prompt, )
In [ ]:
Copied!
```
response = query_engine.query("What did the author do growing up?")

```

response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The author worked on writing and programming before college. They wrote short stories and started programming on the IBM 1401 computer in 9th grade. They later got a microcomputer and continued programming, writing simple games and a word processor.

```

