![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Cohere Rerank¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index > /dev/null
%pip install llama-index-postprocessor-cohere-rerank > /dev/null

```

%pip install llama-index > /dev/null %pip install llama-index-postprocessor-cohere-rerank > /dev/null
```
[notice] A new release of pip is available: 23.3.2 -> 24.0
[notice] To update, run: pip install --upgrade pip
Note: you may need to restart the kernel to use updated packages.

```

In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.response.pprint_utils import pprint_response

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.response.pprint_utils import pprint_response
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-05-09 17:56:26--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8003::154, 2606:50c0:8000::154, 2606:50c0:8002::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8003::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.009s  

2024-05-09 17:56:26 (7.81 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

# build index
index = VectorStoreIndex.from_documents(documents=documents)

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data() # build index index = VectorStoreIndex.from_documents(documents=documents)
#### Retrieve top 10 most relevant nodes, then filter with Cohere Rerank¶
In [ ]:
Copied!
```
import os
from llama_index.postprocessor.cohere_rerank import CohereRerank


api_key = os.environ["COHERE_API_KEY"]
cohere_rerank = CohereRerank(api_key=api_key, top_n=2)

```

import os from llama_index.postprocessor.cohere_rerank import CohereRerank api_key = os.environ["COHERE_API_KEY"] cohere_rerank = CohereRerank(api_key=api_key, top_n=2)
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[cohere_rerank],
)
response = query_engine.query(
    "What did Sam Altman do in this essay?",
)

```

query_engine = index.as_query_engine( similarity_top_k=10, node_postprocessors=[cohere_rerank], ) response = query_engine.query( "What did Sam Altman do in this essay?", )
In [ ]:
Copied!
```
pprint_response(response, show_source=True)

```

pprint_response(response, show_source=True)
```
Final Response: Sam Altman was asked if he wanted to be the president
of Y Combinator. Initially, he declined as he wanted to start a
startup focused on making nuclear reactors. However, after persistent
persuasion, he eventually agreed to become the president of Y
Combinator starting with the winter 2014 batch.
______________________________________________________________________
Source Node 1/2
Node ID: 7ecf4eb2-215d-45e4-ba08-44d9219c7fa6
Similarity: 0.93033177
Text: When I was dealing with some urgent problem during YC, there was
about a 60% chance it had to do with HN, and a 40% chance it had do
with everything else combined. [17]  As well as HN, I wrote all of
YC's internal software in Arc. But while I continued to work a good
deal in Arc, I gradually stopped working on Arc, partly because I
didn't have t...
______________________________________________________________________
Source Node 2/2
Node ID: 88be17e9-e0a0-49e1-9ff8-f2b7aa7493ed
Similarity: 0.86269903
Text: Up till that point YC had been controlled by the original LLC we
four had started. But we wanted YC to last for a long time, and to do
that it couldn't be controlled by the founders. So if Sam said yes,
we'd let him reorganize YC. Robert and I would retire, and Jessica and
Trevor would become ordinary partners.  When we asked Sam if he wanted
to...

```

### Directly retrieve top 2 most similar nodes¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=2,
)
response = query_engine.query(
    "What did Sam Altman do in this essay?",
)

```

query_engine = index.as_query_engine( similarity_top_k=2, ) response = query_engine.query( "What did Sam Altman do in this essay?", )
Retrieved context is irrelevant and response is hallucinated.
In [ ]:
Copied!
```
pprint_response(response, show_source=True)

```

pprint_response(response, show_source=True)
```
Final Response: Sam Altman was asked to become the president of Y
Combinator, initially declined the offer to pursue starting a startup
focused on nuclear reactors, but eventually agreed to take over
starting with the winter 2014 batch.
______________________________________________________________________
Source Node 1/2
Node ID: 7ecf4eb2-215d-45e4-ba08-44d9219c7fa6
Similarity: 0.8308840369082053
Text: When I was dealing with some urgent problem during YC, there was
about a 60% chance it had to do with HN, and a 40% chance it had do
with everything else combined. [17]  As well as HN, I wrote all of
YC's internal software in Arc. But while I continued to work a good
deal in Arc, I gradually stopped working on Arc, partly because I
didn't have t...
______________________________________________________________________
Source Node 2/2
Node ID: 88be17e9-e0a0-49e1-9ff8-f2b7aa7493ed
Similarity: 0.8230144027954406
Text: Up till that point YC had been controlled by the original LLC we
four had started. But we wanted YC to last for a long time, and to do
that it couldn't be controlled by the founders. So if Sam said yes,
we'd let him reorganize YC. Robert and I would retire, and Jessica and
Trevor would become ordinary partners.  When we asked Sam if he wanted
to...

```

