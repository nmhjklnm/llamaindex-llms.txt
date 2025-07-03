![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Multi-Step Query Engine¶
We have a multi-step query engine that's able to decompose a complex query into sequential subquestions. This guide walks you through how to set it up!
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
#### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
#### Load documents, build the VectorStoreIndex¶
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
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from IPython.display import Markdown, display

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.llms.openai import OpenAI from IPython.display import Markdown, display
In [ ]:
Copied!
```
# LLM (gpt-3.5)
gpt35 = OpenAI(temperature=0, model="gpt-3.5-turbo")

# LLM (gpt-4)
gpt4 = OpenAI(temperature=0, model="gpt-4")

```

# LLM (gpt-3.5) gpt35 = OpenAI(temperature=0, model="gpt-3.5-turbo") # LLM (gpt-4) gpt4 = OpenAI(temperature=0, model="gpt-4")
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
#### Query Index¶
In [ ]:
Copied!
```
from llama_index.core.indices.query.query_transform.base import (
    StepDecomposeQueryTransform,
)

# gpt-4
step_decompose_transform = StepDecomposeQueryTransform(llm=gpt4, verbose=True)

# gpt-3
step_decompose_transform_gpt3 = StepDecomposeQueryTransform(
    llm=gpt35, verbose=True
)

```

from llama_index.core.indices.query.query_transform.base import ( StepDecomposeQueryTransform, ) # gpt-4 step_decompose_transform = StepDecomposeQueryTransform(llm=gpt4, verbose=True) # gpt-3 step_decompose_transform_gpt3 = StepDecomposeQueryTransform( llm=gpt35, verbose=True )
In [ ]:
Copied!
```
index_summary = "Used to answer questions about the author"

```

index_summary = "Used to answer questions about the author"
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
from llama_index.core.query_engine import MultiStepQueryEngine

query_engine = index.as_query_engine(llm=gpt4)
query_engine = MultiStepQueryEngine(
    query_engine=query_engine,
    query_transform=step_decompose_transform,
    index_summary=index_summary,
)
response_gpt4 = query_engine.query(
    "Who was in the first batch of the accelerator program the author"
    " started?",
)

```

# set Logging to DEBUG for more detailed outputs from llama_index.core.query_engine import MultiStepQueryEngine query_engine = index.as_query_engine(llm=gpt4) query_engine = MultiStepQueryEngine( query_engine=query_engine, query_transform=step_decompose_transform, index_summary=index_summary, ) response_gpt4 = query_engine.query( "Who was in the first batch of the accelerator program the author" " started?", )
```
> Current query: Who was in the first batch of the accelerator program the author started?
> New query: Who is the author of the accelerator program?
> Current query: Who was in the first batch of the accelerator program the author started?
> New query: Who was in the first batch of the accelerator program started by Paul Graham?
> Current query: Who was in the first batch of the accelerator program the author started?
> New query: None

```

In [ ]:
Copied!
```
display(Markdown(f"<b>{response_gpt4}</b>"))

```

display(Markdown(f"**{response_gpt4}** "))
**In the first batch of the accelerator program started by the author, the participants included the founders of Reddit, Justin Kan and Emmett Shear who later founded Twitch, Aaron Swartz who had helped write the RSS spec and later became a martyr for open access, and Sam Altman who later became the second president of YC.**
In [ ]:
Copied!
```
sub_qa = response_gpt4.metadata["sub_qa"]
tuples = [(t[0], t[1].response) for t in sub_qa]
print(tuples)

```

sub_qa = response_gpt4.metadata["sub_qa"] tuples = [(t[0], t[1].response) for t in sub_qa] print(tuples)
```
[('Who is the author of the accelerator program?', 'The author of the accelerator program is Paul Graham.'), ('Who was in the first batch of the accelerator program started by Paul Graham?', 'The first batch of the accelerator program started by Paul Graham included the founders of Reddit, Justin Kan and Emmett Shear who later founded Twitch, Aaron Swartz who had helped write the RSS spec and later became a martyr for open access, and Sam Altman who later became the second president of YC.')]

```

In [ ]:
Copied!
```
response_gpt4 = query_engine.query(
    "In which city did the author found his first company, Viaweb?",
)

```

response_gpt4 = query_engine.query( "In which city did the author found his first company, Viaweb?", )
```
> Current query: In which city did the author found his first company, Viaweb?
> New query: Who is the author who founded Viaweb?
> Current query: In which city did the author found his first company, Viaweb?
> New query: In which city did Paul Graham found his first company, Viaweb?
> Current query: In which city did the author found his first company, Viaweb?
> New query: None

```

In [ ]:
Copied!
```
print(response_gpt4)

```

print(response_gpt4)
```
The author founded his first company, Viaweb, in Cambridge.

```

In [ ]:
Copied!
```
query_engine = index.as_query_engine(llm=gpt35)
query_engine = MultiStepQueryEngine(
    query_engine=query_engine,
    query_transform=step_decompose_transform_gpt3,
    index_summary=index_summary,
)

response_gpt3 = query_engine.query(
    "In which city did the author found his first company, Viaweb?",
)

```

query_engine = index.as_query_engine(llm=gpt35) query_engine = MultiStepQueryEngine( query_engine=query_engine, query_transform=step_decompose_transform_gpt3, index_summary=index_summary, ) response_gpt3 = query_engine.query( "In which city did the author found his first company, Viaweb?", )
```
> Current query: In which city did the author found his first company, Viaweb?
> New query: None

```

In [ ]:
Copied!
```
print(response_gpt3)

```

print(response_gpt3)
```
Empty Response

```

