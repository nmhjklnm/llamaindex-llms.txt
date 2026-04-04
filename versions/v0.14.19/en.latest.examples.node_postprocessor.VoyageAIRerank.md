![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# VoyageAI Rerank¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index > /dev/null
%pip install llama-index-postprocessor-voyageai-rerank > /dev/null
%pip install llama-index-embeddings-voyageai > /dev/null

```

%pip install llama-index > /dev/null %pip install llama-index-postprocessor-voyageai-rerank > /dev/null %pip install llama-index-embeddings-voyageai > /dev/null
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
import os
from llama_index.embeddings.voyageai import VoyageEmbedding

api_key = os.environ["VOYAGE_API_KEY"]
voyageai_embeddings = VoyageEmbedding(
    voyage_api_key=api_key, model_name="voyage-3"
)

# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

# build index
index = VectorStoreIndex.from_documents(
    documents=documents, embed_model=voyageai_embeddings
)

```

import os from llama_index.embeddings.voyageai import VoyageEmbedding api_key = os.environ["VOYAGE_API_KEY"] voyageai_embeddings = VoyageEmbedding( voyage_api_key=api_key, model_name="voyage-3" ) # load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data() # build index index = VectorStoreIndex.from_documents( documents=documents, embed_model=voyageai_embeddings )
#### Retrieve top 10 most relevant nodes, then filter with VoyageAI Rerank¶
In [ ]:
Copied!
```
from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank

voyageai_rerank = VoyageAIRerank(
    api_key=api_key, top_k=2, model="rerank-2", truncation=True
)

```

from llama_index.postprocessor.voyageai_rerank import VoyageAIRerank voyageai_rerank = VoyageAIRerank( api_key=api_key, top_k=2, model="rerank-2", truncation=True )
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[voyageai_rerank],
)
response = query_engine.query(
    "What did Sam Altman do in this essay?",
)

```

query_engine = index.as_query_engine( similarity_top_k=10, node_postprocessors=[voyageai_rerank], ) response = query_engine.query( "What did Sam Altman do in this essay?", )
In [ ]:
Copied!
```
pprint_response(response, show_source=True)

```

pprint_response(response, show_source=True)
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
