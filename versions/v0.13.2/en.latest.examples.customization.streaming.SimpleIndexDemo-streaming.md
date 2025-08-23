![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Streaming¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
```
INFO:numexpr.utils:Note: NumExpr detected 12 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
Note: NumExpr detected 12 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
INFO:numexpr.utils:NumExpr defaulting to 8 threads.
NumExpr defaulting to 8 threads.

```

```
/Users/suo/miniconda3/envs/llama/lib/python3.9/site-packages/deeplake/util/check_latest_version.py:32: UserWarning: A newer version of deeplake (3.6.7) is available. It's recommended that you update to the latest version using `pip install -U deeplake`.
  warnings.warn(

```

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
# load documents
documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham").load_data()
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
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine(streaming=True, similarity_top_k=1)
response_stream = query_engine.query(
    "What did the author do growing up?",
)

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine(streaming=True, similarity_top_k=1) response_stream = query_engine.query( "What did the author do growing up?", )
In [ ]:
Copied!
```
response_stream.print_response_stream()

```

response_stream.print_response_stream()
```
The author grew up writing short stories and programming on an IBM 1401. He also nagged his father to buy him a TRS-80 microcomputer, on which he wrote simple games, a program to predict how high his model rockets would fly, and a word processor. He eventually went to college to study philosophy, but found it boring and switched to AI.
```

