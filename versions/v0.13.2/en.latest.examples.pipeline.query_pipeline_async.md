# Query Pipeline with Async/Parallel Execution¶
Here we showcase our query pipeline with async + parallel execution.
We do this by setting up a RAG pipeline that does the following:
  1. Send query to multiple RAG query engines.
  2. Combine results.


In the process we'll also show some nice abstractions for joining results (e.g. our `ArgPackComponent()`)
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
## Setup Query Pipeline¶
We setup a parallel query pipeline that executes multiple chunk sizes at once, and combines the results.
### Define Modules¶
This includes:
  * LLM
  * Chunk Sizes
  * Query Engines


In [ ]:
Copied!
```
from llama_index.core.query_pipeline import (
    QueryPipeline,
    InputComponent,
    ArgPackComponent,
)
from typing import Dict, Any, List, Optional
from llama_index.core.llama_pack import BaseLlamaPack
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core.node_parser import SentenceSplitter


llm = OpenAI(model="gpt-3.5-turbo")
chunk_sizes = [128, 256, 512, 1024]
query_engines = {}
for chunk_size in chunk_sizes:
    splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=0)
    nodes = splitter.get_nodes_from_documents(documents)
    vector_index = VectorStoreIndex(nodes)
    query_engines[str(chunk_size)] = vector_index.as_query_engine(llm=llm)

```

from llama_index.core.query_pipeline import ( QueryPipeline, InputComponent, ArgPackComponent, ) from typing import Dict, Any, List, Optional from llama_index.core.llama_pack import BaseLlamaPack from llama_index.core.llms import LLM from llama_index.llms.openai import OpenAI from llama_index.core import Document, VectorStoreIndex from llama_index.core.response_synthesizers import TreeSummarize from llama_index.core.schema import NodeWithScore, TextNode from llama_index.core.node_parser import SentenceSplitter llm = OpenAI(model="gpt-3.5-turbo") chunk_sizes = [128, 256, 512, 1024] query_engines = {} for chunk_size in chunk_sizes: splitter = SentenceSplitter(chunk_size=chunk_size, chunk_overlap=0) nodes = splitter.get_nodes_from_documents(documents) vector_index = VectorStoreIndex(nodes) query_engines[str(chunk_size)] = vector_index.as_query_engine(llm=llm)
### Construct Query Pipeline¶
Connect input to multiple query engines, and join the results.
In [ ]:
Copied!
```
# construct query pipeline
p = QueryPipeline(verbose=True)
module_dict = {
    **query_engines,
    "input": InputComponent(),
    "summarizer": TreeSummarize(),
    "join": ArgPackComponent(
        convert_fn=lambda x: NodeWithScore(node=TextNode(text=str(x)))
    ),
}
p.add_modules(module_dict)
# add links from input to query engine (id'ed by chunk_size)
for chunk_size in chunk_sizes:
    p.add_link("input", str(chunk_size))
    p.add_link(str(chunk_size), "join", dest_key=str(chunk_size))
p.add_link("join", "summarizer", dest_key="nodes")
p.add_link("input", "summarizer", dest_key="query_str")

```

# construct query pipeline p = QueryPipeline(verbose=True) module_dict = { **query_engines, "input": InputComponent(), "summarizer": TreeSummarize(), "join": ArgPackComponent( convert_fn=lambda x: NodeWithScore(node=TextNode(text=str(x))) ), } p.add_modules(module_dict) # add links from input to query engine (id'ed by chunk_size) for chunk_size in chunk_sizes: p.add_link("input", str(chunk_size)) p.add_link(str(chunk_size), "join", dest_key=str(chunk_size)) p.add_link("join", "summarizer", dest_key="nodes") p.add_link("input", "summarizer", dest_key="query_str")
## Try out Queries¶
Let's compare the async performance vs. synchronous performance!
In our experiments we get a 2x speedup.
In [ ]:
Copied!
```
import time

start_time = time.time()
response = await p.arun(input="What did the author do during his time in YC?")
print(str(response))
end_time = time.time()
print(f"Time taken: {end_time - start_time}")

```

import time start_time = time.time() response = await p.arun(input="What did the author do during his time in YC?") print(str(response)) end_time = time.time() print(f"Time taken: {end_time - start_time}")
```
> Running modules and inputs in parallel: 
Module key: input. Input: 
input: What did the author do during his time in YC?


> Running modules and inputs in parallel: 
Module key: 128. Input: 
input: What did the author do during his time in YC?

Module key: 256. Input: 
input: What did the author do during his time in YC?

Module key: 512. Input: 
input: What did the author do during his time in YC?

Module key: 1024. Input: 
input: What did the author do during his time in YC?


> Running modules and inputs in parallel: 
Module key: join. Input: 
128: The author worked on solving the problems of startups that were part of the YC program.
256: The author worked on YC's internal software in Arc and also wrote essays during his time in YC.
512: During his time in YC, the author worked on various projects. Initially, he intended to do three things: hack, write essays, and work on YC. However, as YC grew and he became more excited about it, it...
1024: During his time in YC, the author worked on YC's internal software in Arc and wrote essays. He also worked on various projects related to YC, such as helping startups and solving their problems. Addit...


> Running modules and inputs in parallel: 
Module key: summarizer. Input: 
query_str: What did the author do during his time in YC?
nodes: [NodeWithScore(node=TextNode(id_='7e0b0aeb-04e3-4518-b534-2cf68c07ae1f', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, hash='fe9144af45...


During his time in YC, the author worked on various projects, including YC's internal software in Arc and writing essays. He also helped startups and solved their problems, and was involved in disputes between cofounders. Additionally, the author worked hard to ensure the success of YC and dealt with people who maltreated startups.
Time taken: 3.943013906478882

```

In [ ]:
Copied!
```
# compare with sync method

start_time = time.time()
response = p.run(input="What did the author do during his time in YC?")
print(str(response))
end_time = time.time()
print(f"Time taken: {end_time - start_time}")

```

# compare with sync method start_time = time.time() response = p.run(input="What did the author do during his time in YC?") print(str(response)) end_time = time.time() print(f"Time taken: {end_time - start_time}")
```
> Running module input with input: 
input: What did the author do during his time in YC?

> Running module 128 with input: 
input: What did the author do during his time in YC?

> Running module 256 with input: 
input: What did the author do during his time in YC?

> Running module 512 with input: 
input: What did the author do during his time in YC?

> Running module 1024 with input: 
input: What did the author do during his time in YC?

> Running module join with input: 
128: The author worked on solving the problems of startups that were part of the YC program.
256: The author worked on YC's internal software in Arc and also wrote essays.
512: During his time in YC, the author worked on various projects. Initially, he intended to do three things: hack, write essays, and work on YC. However, as YC grew and he became more excited about it, it...
1024: During his time in YC, the author worked on YC's internal software in Arc, wrote essays, and worked on various projects related to YC. He also engaged in solving the problems faced by startups that we...

> Running module summarizer with input: 
query_str: What did the author do during his time in YC?
nodes: [NodeWithScore(node=TextNode(id_='4d698e2f-811e-42ce-bd0d-9b5615b0bbfd', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, hash='fe9144af45...

During his time in YC, the author worked on YC's internal software in Arc, wrote essays, and worked on various projects related to YC. He also engaged in solving the problems faced by startups that were part of YC's program. Additionally, the author mentioned working on tasks he didn't particularly enjoy, such as resolving disputes between cofounders and dealing with people who mistreated startups.
Time taken: 7.640604019165039

```

