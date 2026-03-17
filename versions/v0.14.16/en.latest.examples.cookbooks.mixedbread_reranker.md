![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# mixedbread Rerank Cookbook¶
mixedbread.ai has released three fully open-source reranker models under the Apache 2.0 license. For more in-depth information, you can check out their detailed blog post. The following are the three models:
  1. `mxbai-rerank-xsmall-v1`
  2. `mxbai-rerank-base-v1`
  3. `mxbai-rerank-large-v1`


In this notebook, we'll demonstrate how to use the `mxbai-rerank-base-v1` model with the `SentenceTransformerRerank` module in LlamaIndex. This setup allows you to seamlessly swap in any reranker model of your choice using the `SentenceTransformerRerank` module to enhance your RAG pipeline.
### Installation¶
In [ ]:
Copied!
```
!pip install llama-index
!pip install sentence-transformers

```

!pip install llama-index !pip install sentence-transformers
### Set API Keys¶
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
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
)

from llama_index.core.postprocessor import SentenceTransformerRerank

```

from llama_index.core import ( VectorStoreIndex, SimpleDirectoryReader, ) from llama_index.core.postprocessor import SentenceTransformerRerank
### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-03-01 09:52:09--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.108.133, 185.199.109.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.007s  

2024-03-01 09:52:09 (9.86 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

### Load Documents¶
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
### Build Index¶
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents=documents)

```

index = VectorStoreIndex.from_documents(documents=documents)
### Define postprocessor for `mxbai-rerank-base-v1` reranker¶
In [ ]:
Copied!
```
from llama_index.core.postprocessor import SentenceTransformerRerank

postprocessor = SentenceTransformerRerank(
    model="mixedbread-ai/mxbai-rerank-base-v1", top_n=2
)

```

from llama_index.core.postprocessor import SentenceTransformerRerank postprocessor = SentenceTransformerRerank( model="mixedbread-ai/mxbai-rerank-base-v1", top_n=2 )
### Create Query Engine¶
We will first retrieve 10 relevant nodes and pick top-2 nodes using the defined postprocessor.
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[postprocessor],
)

```

query_engine = index.as_query_engine( similarity_top_k=10, node_postprocessors=[postprocessor], )
### Test Queries¶
In [ ]:
Copied!
```
response = query_engine.query(
    "Why did Sam Altman decline the offer of becoming president of Y Combinator?",
)

print(response)

```

response = query_engine.query( "Why did Sam Altman decline the offer of becoming president of Y Combinator?", ) print(response)
```
Sam Altman initially declined the offer of becoming president of Y Combinator because he wanted to start a startup focused on making nuclear reactors.

```

In [ ]:
Copied!
```
response = query_engine.query(
    "Why did Paul Graham start YC?",
)

print(response)

```

response = query_engine.query( "Why did Paul Graham start YC?", ) print(response)
```
Paul Graham started YC because he and his partners wanted to create an investment firm where they could implement their own ideas and provide the kind of support to startups that they felt was lacking when they were founders themselves. They aimed to not only make seed investments but also assist startups with various aspects of setting up a company, similar to the help they had received from others in the past.

```

