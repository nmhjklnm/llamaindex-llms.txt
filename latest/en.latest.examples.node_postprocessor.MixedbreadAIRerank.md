![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Mixedbread AI Rerank¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index > /dev/null
%pip install llama-index-postprocessor-mixedbreadai-rerank > /dev/null
%pip install llama-index-llms-openai > /dev/null

```

%pip install llama-index > /dev/null %pip install llama-index-postprocessor-mixedbreadai-rerank > /dev/null %pip install llama-index-llms-openai > /dev/null
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
--2025-07-24 19:14:25--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8000::154, 2606:50c0:8001::154, 2606:50c0:8002::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8000::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.03s   

2025-07-24 19:14:25 (2.35 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

In [ ]:
Copied!
```
import os
from llama_index.embeddings.mixedbreadai import MixedbreadAIEmbedding

# You can visit https://www.mixedbread.ai/api-reference#quick-start-guide
# to get an api key
mixedbread_api_key = os.environ.get("MXBAI_API_KEY", "your-api-key")
model_name = "mixedbread-ai/mxbai-embed-large-v1"

mixbreadai_embeddings = MixedbreadAIEmbedding(
    api_key=mixedbread_api_key, model_name=model_name
)

# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

# build index
index = VectorStoreIndex.from_documents(
    documents=documents, embed_model=mixbreadai_embeddings
)

```

import os from llama_index.embeddings.mixedbreadai import MixedbreadAIEmbedding # You can visit https://www.mixedbread.ai/api-reference#quick-start-guide # to get an api key mixedbread_api_key = os.environ.get("MXBAI_API_KEY", "your-api-key") model_name = "mixedbread-ai/mxbai-embed-large-v1" mixbreadai_embeddings = MixedbreadAIEmbedding( api_key=mixedbread_api_key, model_name=model_name ) # load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data() # build index index = VectorStoreIndex.from_documents( documents=documents, embed_model=mixbreadai_embeddings )
## Retrieve top 10 most relevant nodes, then filter with MixedbreadAI Rerank¶
In [ ]:
Copied!
```
from llama_index.postprocessor.mixedbreadai_rerank import MixedbreadAIRerank

mixedbreadai_rerank = MixedbreadAIRerank(
    api_key=mixedbread_api_key,
    top_n=2,
    model="mixedbread-ai/mxbai-rerank-large-v1",
)

```

from llama_index.postprocessor.mixedbreadai_rerank import MixedbreadAIRerank mixedbreadai_rerank = MixedbreadAIRerank( api_key=mixedbread_api_key, top_n=2, model="mixedbread-ai/mxbai-rerank-large-v1", )
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[mixedbreadai_rerank],
)
response = query_engine.query(
    "What did Sam Altman do in this essay?",
)

```

query_engine = index.as_query_engine( similarity_top_k=10, node_postprocessors=[mixedbreadai_rerank], ) response = query_engine.query( "What did Sam Altman do in this essay?", )
In [ ]:
Copied!
```
pprint_response(response, show_source=True)

```

pprint_response(response, show_source=True)
```
Final Response: Sam Altman was asked to become the president of Y
Combinator (YC) after the original founders decided to step back and
reorganize the company to ensure its longevity. Initially hesitant due
to his interest in starting a nuclear reactor startup, Sam eventually
agreed to take over as president starting with the winter 2014 batch.
______________________________________________________________________
Source Node 1/2
Node ID: 9bef8795-4532-44eb-a590-45abf15b11e5
Similarity: 0.109680176
Text: This seemed strange advice, because YC was doing great. But if
there was one thing rarer than Rtm offering advice, it was Rtm being
wrong. So this set me thinking. It was true that on my current
trajectory, YC would be the last thing I did, because it was only
taking up more of my attention. It had already eaten Arc, and was in
the process of ea...
______________________________________________________________________
Source Node 2/2
Node ID: 3060722a-0e57-492e-9071-2148e5eec2be
Similarity: 0.041625977
Text: But after Heroku got bought we had enough money to go back to
being self-funded.  [15] I've never liked the term "deal flow,"
because it implies that the number of new startups at any given time
is fixed. This is not only false, but it's the purpose of YC to
falsify it, by causing startups to be founded that would not otherwise
have existed.  [1...

```

## Directly retrieve top 2 most similar nodes¶
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
Final Response: Sam Altman worked on the application builder, while
Dan worked on network infrastructure, and two undergrads worked on the
first two services (images and phone calls). Later on, Sam realized he
didn't want to run a company and decided to build a subset of the
project as an open source project.
______________________________________________________________________
Source Node 1/2
Node ID: a42ab697-0bd1-40fc-8e23-64148e62fe6d
Similarity: 0.557881093860686
Text: I started working on the application builder, Dan worked on
network infrastructure, and the two undergrads worked on the first two
services (images and phone calls). But about halfway through the
summer I realized I really didn't want to run a company — especially
not a big one, which it was looking like this would have to be. I'd
only started V...
______________________________________________________________________
Source Node 2/2
Node ID: a398b429-fad6-4284-a201-835e5c1fec3c
Similarity: 0.49815489887733433
Text: But alas it was more like the Accademia than not. Better
organized, certainly, and a lot more expensive, but it was now
becoming clear that art school did not bear the same relationship to
art that medical school bore to medicine. At least not the painting
department. The textile department, which my next door neighbor
belonged to, seemed to be ...

```

