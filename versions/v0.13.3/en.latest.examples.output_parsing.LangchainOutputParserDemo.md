![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Langchain Output Parsing¶
Download Data
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
Will not apply HSTS. The HSTS database must be a regular and non-world-writable file.
ERROR: could not open HSTS store at '/home/loganm/.wget-hsts'. HSTS will be disabled.
--2023-12-11 10:24:04--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.109.133, 185.199.108.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.04s   

2023-12-11 10:24:04 (1.74 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

#### Load documents, build the VectorStoreIndex¶
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from IPython.display import Markdown, display

import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from IPython.display import Markdown, display import os os.environ["OPENAI_API_KEY"] = "sk-..."
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
index = VectorStoreIndex.from_documents(documents, chunk_size=512)

```

index = VectorStoreIndex.from_documents(documents, chunk_size=512)
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

#### Define Query + Langchain Output Parser¶
In [ ]:
Copied!
```
from llama_index.core.output_parsers import LangchainOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

```

from llama_index.core.output_parsers import LangchainOutputParser from langchain.output_parsers import StructuredOutputParser, ResponseSchema
**Define custom QA and Refine Prompts**
In [ ]:
Copied!
```
response_schemas = [
    ResponseSchema(
        name="Education",
        description=(
            "Describes the author's educational experience/background."
        ),
    ),
    ResponseSchema(
        name="Work",
        description="Describes the author's work experience/background.",
    ),
]

```

response_schemas = [ ResponseSchema( name="Education", description=( "Describes the author's educational experience/background." ), ), ResponseSchema( name="Work", description="Describes the author's work experience/background.", ), ]
In [ ]:
Copied!
```
lc_output_parser = StructuredOutputParser.from_response_schemas(
    response_schemas
)
output_parser = LangchainOutputParser(lc_output_parser)

```

lc_output_parser = StructuredOutputParser.from_response_schemas( response_schemas ) output_parser = LangchainOutputParser(lc_output_parser)
In [ ]:
Copied!
```
from llama_index.core.prompts.default_prompts import (
    DEFAULT_TEXT_QA_PROMPT_TMPL,
)

# take a look at the new QA template!
fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL)
print(fmt_qa_tmpl)

```

from llama_index.core.prompts.default_prompts import ( DEFAULT_TEXT_QA_PROMPT_TMPL, ) # take a look at the new QA template! fmt_qa_tmpl = output_parser.format(DEFAULT_TEXT_QA_PROMPT_TMPL) print(fmt_qa_tmpl)
```
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: 

The output should be a markdown code snippet formatted in the following schema, including the leading and trailing "```json" and "json
{{
	"Education": string  // Describes the author's educational experience/background.
	"Work": string  // Describes the author's work experience/background.
}}


#### Query Index¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(output_parser=output_parser)

query_engine = index.as_query_engine(
    llm=llm,
)
response = query_engine.query(
    "What are a few things the author did growing up?",
)

```

from llama_index.llms.openai import OpenAI llm = OpenAI(output_parser=output_parser) query_engine = index.as_query_engine( llm=llm, ) response = query_engine.query( "What are a few things the author did growing up?", )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
{'Education': 'The author did not plan to study programming in college, but initially planned to study philosophy.', 'Work': 'Growing up, the author worked on writing short stories and programming. They wrote simple games, a program to predict rocket heights, and a word processor.'}

```

