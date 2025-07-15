![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Multi-Tenancy RAG with LlamaIndex¶
In this notebook you will look into building Multi-Tenancy RAG System using LlamaIndex.
  1. Setup
  2. Download Data
  3. Load Data
  4. Create Index
  5. Create Ingestion Pipeline
  6. Update Metadata and Insert documents
  7. Define Query Engines for each user
  8. Querying


## Setup¶
You should ensure you have `llama-index` and `pypdf` is installed.
In [ ]:
Copied!
```
!pip install llama-index pypdf

```

!pip install llama-index pypdf
### Set OpenAI Key¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY"

```

import os os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY"
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter

from IPython.display import HTML

```

from llama_index.core import VectorStoreIndex from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter from llama_index.core import SimpleDirectoryReader from llama_index.core.ingestion import IngestionPipeline from llama_index.core.node_parser import SentenceSplitter from IPython.display import HTML
## Download Data¶
We will use `An LLM Compiler for Parallel Function Calling` and `Dense X Retrieval: What Retrieval Granularity Should We Use?` papers for the demonstartions.
In [ ]:
Copied!
```
!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2312.04511.pdf" -O "llm_compiler.pdf"
!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2312.06648.pdf" -O "dense_x_retrieval.pdf"

```

!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2312.04511.pdf" -O "llm_compiler.pdf" !wget --user-agent "Mozilla" "https://arxiv.org/pdf/2312.06648.pdf" -O "dense_x_retrieval.pdf"
```
--2024-01-15 14:29:26--  https://arxiv.org/pdf/2312.04511.pdf
Resolving arxiv.org (arxiv.org)... 151.101.131.42, 151.101.67.42, 151.101.3.42, ...
Connecting to arxiv.org (arxiv.org)|151.101.131.42|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 755837 (738K) [application/pdf]
Saving to: ‘llm_compiler.pdf’


llm_compiler.pdf      0%[                    ]       0  --.-KB/s               
llm_compiler.pdf    100%[===================>] 738.12K  --.-KB/s    in 0.004s  

2024-01-15 14:29:26 (163 MB/s) - ‘llm_compiler.pdf’ saved [755837/755837]

--2024-01-15 14:29:26--  https://arxiv.org/pdf/2312.06648.pdf
Resolving arxiv.org (arxiv.org)... 151.101.131.42, 151.101.67.42, 151.101.3.42, ...
Connecting to arxiv.org (arxiv.org)|151.101.131.42|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1103758 (1.1M) [application/pdf]
Saving to: ‘dense_x_retrieval.pdf’

dense_x_retrieval.p 100%[===================>]   1.05M  --.-KB/s    in 0.005s  

2024-01-15 14:29:26 (208 MB/s) - ‘dense_x_retrieval.pdf’ saved [1103758/1103758]


```

## Load Data¶
In [ ]:
Copied!
```
reader = SimpleDirectoryReader(input_files=["dense_x_retrieval.pdf"])
documents_jerry = reader.load_data()

reader = SimpleDirectoryReader(input_files=["llm_compiler.pdf"])
documents_ravi = reader.load_data()

```

reader = SimpleDirectoryReader(input_files=["dense_x_retrieval.pdf"]) documents_jerry = reader.load_data() reader = SimpleDirectoryReader(input_files=["llm_compiler.pdf"]) documents_ravi = reader.load_data()
## Create an Empty Index¶
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents=[])

```

index = VectorStoreIndex.from_documents(documents=[])
## Create Ingestion Pipeline¶
In [ ]:
Copied!
```
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=512, chunk_overlap=20),
    ]
)

```

pipeline = IngestionPipeline( transformations=[ SentenceSplitter(chunk_size=512, chunk_overlap=20), ] )
## Update Metadata and Insert Documents¶
In [ ]:
Copied!
```
for document in documents_jerry:
    document.metadata["user"] = "Jerry"

nodes = pipeline.run(documents=documents_jerry)
# Insert nodes into the index
index.insert_nodes(nodes)

```

for document in documents_jerry: document.metadata["user"] = "Jerry" nodes = pipeline.run(documents=documents_jerry) # Insert nodes into the index index.insert_nodes(nodes)
In [ ]:
Copied!
```
for document in documents_ravi:
    document.metadata["user"] = "Ravi"

nodes = pipeline.run(documents=documents_ravi)
# Insert nodes into the index
index.insert_nodes(nodes)

```

for document in documents_ravi: document.metadata["user"] = "Ravi" nodes = pipeline.run(documents=documents_ravi) # Insert nodes into the index index.insert_nodes(nodes)
## Define Query Engines¶
Define query engines for both the users with necessary filters.
In [ ]:
Copied!
```
# For Jerry
jerry_query_engine = index.as_query_engine(
    filters=MetadataFilters(
        filters=[
            ExactMatchFilter(
                key="user",
                value="Jerry",
            )
        ]
    ),
    similarity_top_k=3,
)

# For Ravi
ravi_query_engine = index.as_query_engine(
    filters=MetadataFilters(
        filters=[
            ExactMatchFilter(
                key="user",
                value="Ravi",
            )
        ]
    ),
    similarity_top_k=3,
)

```

# For Jerry jerry_query_engine = index.as_query_engine( filters=MetadataFilters( filters=[ ExactMatchFilter( key="user", value="Jerry", ) ] ), similarity_top_k=3, ) # For Ravi ravi_query_engine = index.as_query_engine( filters=MetadataFilters( filters=[ ExactMatchFilter( key="user", value="Ravi", ) ] ), similarity_top_k=3, )
## Querying¶
In [ ]:
Copied!
```
# Jerry has Dense X Rerieval paper and should be able to answer following question.
response = jerry_query_engine.query(
    "what are propositions mentioned in the paper?"
)
# Print response
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

# Jerry has Dense X Rerieval paper and should be able to answer following question. response = jerry_query_engine.query( "what are propositions mentioned in the paper?" ) # Print response display(HTML(f'
{response.response}
'))
The paper mentions propositions as an alternative retrieval unit choice. Propositions are defined as atomic expressions of meanings in text that correspond to distinct pieces of meaning in the text. They are minimal and cannot be further split into separate propositions. Each proposition is contextualized and self-contained, including all the necessary context from the text to interpret its meaning. The paper demonstrates the concept of propositions using an example about the Leaning Tower of Pisa, where the passage is split into three propositions, each corresponding to a distinct factoid about the tower.
In [ ]:
Copied!
```
# Ravi has LLMCompiler paper
response = ravi_query_engine.query("what are steps involved in LLMCompiler?")

# Print response
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

# Ravi has LLMCompiler paper response = ravi_query_engine.query("what are steps involved in LLMCompiler?") # Print response display(HTML(f'
{response.response}
'))
LLMCompiler consists of three key components: an LLM Planner, a Task Fetching Unit, and an Executor. The LLM Planner identifies the execution flow by defining different function calls and their dependencies based on user inputs. The Task Fetching Unit dispatches the function calls that can be executed in parallel after substituting variables with the actual outputs of preceding tasks. Finally, the Executor executes the dispatched function calling tasks using the associated tools. These components work together to optimize the parallel function calling performance of LLMs.
In [ ]:
Copied!
```
# This should not be answered as Jerry does not have information about LLMCompiler
response = jerry_query_engine.query("what are steps involved in LLMCompiler?")

# Print response
display(HTML(f'<p style="font-size:20px">{response.response}</p>'))

```

# This should not be answered as Jerry does not have information about LLMCompiler response = jerry_query_engine.query("what are steps involved in LLMCompiler?") # Print response display(HTML(f'
{response.response}
'))
The steps involved in LLMCompiler are not mentioned in the given context information.
