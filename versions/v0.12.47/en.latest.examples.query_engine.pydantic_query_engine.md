![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Query Engine with Pydantic Outputs¶
Every query engine has support for integrated structured responses using the following `response_mode`s in `RetrieverQueryEngine`:
  * `refine`
  * `compact`
  * `tree_summarize`
  * `accumulate` (beta, requires extra parsing to convert to objects)
  * `compact_accumulate` (beta, requires extra parsing to convert to objects)


In this notebook, we walk through a small example demonstrating the usage.
Under the hood, every LLM response will be a pydantic object. If that response needs to be refined or summarized, it is converted into a JSON string for the next response. Then, the final response is returned as a pydantic object.
**NOTE:** This can technically work with any LLM, but non-openai is support is still in development and considered beta.
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-anthropic
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-anthropic %pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import os
import openai

os.environ["OPENAI_API_KEY"] = "sk-..."
openai.api_key = os.environ["OPENAI_API_KEY"]

```

import os import openai os.environ["OPENAI_API_KEY"] = "sk-..." openai.api_key = os.environ["OPENAI_API_KEY"]
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
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham").load_data()
### Create our Pydanitc Output Object¶
In [ ]:
Copied!
```
from typing import List
from pydantic import BaseModel


class Biography(BaseModel):
    """Data model for a biography."""

    name: str
    best_known_for: List[str]
    extra_info: str

```

from typing import List from pydantic import BaseModel class Biography(BaseModel): """Data model for a biography.""" name: str best_known_for: List[str] extra_info: str
## Create the Index + Query Engine (OpenAI)¶
When using OpenAI, the function calling API will be leveraged for reliable structured outputs.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)

index = VectorStoreIndex.from_documents(
    documents,
)

```

from llama_index.core import VectorStoreIndex from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1) index = VectorStoreIndex.from_documents( documents, )
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    output_cls=Biography, response_mode="compact", llm=llm
)

```

query_engine = index.as_query_engine( output_cls=Biography, response_mode="compact", llm=llm )
In [ ]:
Copied!
```
response = query_engine.query("Who is Paul Graham?")

```

response = query_engine.query("Who is Paul Graham?")
In [ ]:
Copied!
```
print(response.name)
print(response.best_known_for)
print(response.extra_info)

```

print(response.name) print(response.best_known_for) print(response.extra_info)
```
Paul Graham
['working on Bel', 'co-founding Viaweb', 'creating the programming language Arc']
Paul Graham is a computer scientist, entrepreneur, and writer. He is best known for his work on Bel, a programming language, and for co-founding Viaweb, an early web application company that was later acquired by Yahoo. Graham also created the programming language Arc. He has written numerous essays on topics such as startups, programming, and life.

```

In [ ]:
Copied!
```
# get the full pydanitc object
print(type(response.response))

```

# get the full pydanitc object print(type(response.response))
```
<class '__main__.Biography'>

```

## Create the Index + Query Engine (Non-OpenAI, Beta)¶
When using an LLM that does not support function calling, we rely on the LLM to write the JSON itself, and we parse the JSON into the proper pydantic object.
In [ ]:
Copied!
```
import os

os.environ["ANTHROPIC_API_KEY"] = "sk-..."

```

import os os.environ["ANTHROPIC_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.llms.anthropic import Anthropic

llm = Anthropic(model="claude-instant-1.2", temperature=0.1)

index = VectorStoreIndex.from_documents(
    documents,
)

```

from llama_index.core import VectorStoreIndex from llama_index.llms.anthropic import Anthropic llm = Anthropic(model="claude-instant-1.2", temperature=0.1) index = VectorStoreIndex.from_documents( documents, )
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    output_cls=Biography, response_mode="tree_summarize", llm=llm
)

```

query_engine = index.as_query_engine( output_cls=Biography, response_mode="tree_summarize", llm=llm )
In [ ]:
Copied!
```
response = query_engine.query("Who is Paul Graham?")

```

response = query_engine.query("Who is Paul Graham?")
In [ ]:
Copied!
```
print(response.name)
print(response.best_known_for)
print(response.extra_info)

```

print(response.name) print(response.best_known_for) print(response.extra_info)
```
Paul Graham
['Co-founder of Y Combinator', 'Essayist and programmer']
He is known for creating Viaweb, one of the first web application builders, and for founding Y Combinator, one of the world's top startup accelerators. Graham has also written extensively about technology, investing, and philosophy.

```

In [ ]:
Copied!
```
# get the full pydanitc object
print(type(response.response))

```

# get the full pydanitc object print(type(response.response))
```
<class '__main__.Biography'>

```

## Accumulate Examples (Beta)¶
Accumulate with pydantic objects requires some extra parsing. This is still a beta feature, but it's still possible to get accumulate pydantic objects.
In [ ]:
Copied!
```
from typing import List
from pydantic import BaseModel


class Company(BaseModel):
    """Data model for a companies mentioned."""

    company_name: str
    context_info: str

```

from typing import List from pydantic import BaseModel class Company(BaseModel): """Data model for a companies mentioned.""" company_name: str context_info: str
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex,
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1)

index = VectorStoreIndex.from_documents(
    documents,
)

```

from llama_index.core import VectorStoreIndex, from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo", temperature=0.1) index = VectorStoreIndex.from_documents( documents, )
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    output_cls=Company, response_mode="accumulate", llm=llm
)

```

query_engine = index.as_query_engine( output_cls=Company, response_mode="accumulate", llm=llm )
In [ ]:
Copied!
```
response = query_engine.query("What companies are mentioned in the text?")

```

response = query_engine.query("What companies are mentioned in the text?")
In accumulate, responses are separated by a default separator, and prepended with a prefix.
In [ ]:
Copied!
```
companies = []

# split by the default separator
for response_str in str(response).split("\n---------------------\n"):
    # remove the prefix --  every response starts like `Response 1: {...}`
    # so, we find the first bracket and remove everything before it
    response_str = response_str[response_str.find("{") :]
    companies.append(Company.parse_raw(response_str))

```

companies = [] # split by the default separator for response_str in str(response).split("\n---------------------\n"): # remove the prefix -- every response starts like `Response 1: {...}` # so, we find the first bracket and remove everything before it response_str = response_str[response_str.find("{") :] companies.append(Company.parse_raw(response_str))
In [ ]:
Copied!
```
print(companies)

```

print(companies)
```
[Company(company_name='Yahoo', context_info='Yahoo bought us'), Company(company_name='Yahoo', context_info="I'd been meaning to since Yahoo bought us")]

```

