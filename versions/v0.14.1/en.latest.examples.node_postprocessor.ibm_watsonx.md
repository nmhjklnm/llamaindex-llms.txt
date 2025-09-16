![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# IBM watsonx.ai¶
> WatsonxRerank is a wrapper for IBM watsonx.ai Rerank.
The aim of these examples is to show how to take advantage of `watsonx.ai` Rerank, Embeddings and LLMs using the `LlamaIndex` postprocessor API.
## Setting up¶
Install required packages:
In [ ]:
Copied!
```
%pip install -qU llama-index
%pip install -qU llama-index-llms-ibm
%pip install -qU llama-index-postprocessor-ibm
%pip install -qU llama-index-embeddings-ibm

```

%pip install -qU llama-index %pip install -qU llama-index-llms-ibm %pip install -qU llama-index-postprocessor-ibm %pip install -qU llama-index-embeddings-ibm
The cell below defines the credentials required to work with watsonx Foundation Models, Embeddings and Rerank.
**Action:** Provide the IBM Cloud user API key. For details, see Managing user API keys.
In [ ]:
Copied!
```
import os
from getpass import getpass

watsonx_api_key = getpass()
os.environ["WATSONX_APIKEY"] = watsonx_api_key

```

import os from getpass import getpass watsonx_api_key = getpass() os.environ["WATSONX_APIKEY"] = watsonx_api_key
Additionally, you can pass additional secrets as an environment variable:
In [ ]:
Copied!
```
import os

os.environ["WATSONX_URL"] = "your service instance url"
os.environ["WATSONX_TOKEN"] = "your token for accessing the CPD cluster"
os.environ["WATSONX_PASSWORD"] = "your password for accessing the CPD cluster"
os.environ["WATSONX_USERNAME"] = "your username for accessing the CPD cluster"
os.environ[
    "WATSONX_INSTANCE_ID"
] = "your instance_id for accessing the CPD cluster"

```

import os os.environ["WATSONX_URL"] = "your service instance url" os.environ["WATSONX_TOKEN"] = "your token for accessing the CPD cluster" os.environ["WATSONX_PASSWORD"] = "your password for accessing the CPD cluster" os.environ["WATSONX_USERNAME"] = "your username for accessing the CPD cluster" os.environ[ "WATSONX_INSTANCE_ID" ] = "your instance_id for accessing the CPD cluster"
**Note** :
  * To provide context for the API call, you must pass the `project_id` or `space_id`. To get your project or space ID, open your project or space, go to the **Manage** tab, and click **General**. For more information see: Project documentation or Deployment space documentation.
  * Depending on the region of your provisioned service instance, use one of the urls listed in watsonx.ai API Authentication.


In this example, we’ll use the `project_id` and Dallas URL.
Provide `PROJECT_ID` that will be used for initialize each watsonx integration instance.
In [ ]:
Copied!
```
PROJECT_ID = "PASTE YOUR PROJECT_ID HERE"
URL = "https://us-south.ml.cloud.ibm.com"

```

PROJECT_ID = "PASTE YOUR PROJECT_ID HERE" URL = "https://us-south.ml.cloud.ibm.com"
## Download data and load documents¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2025-02-24 10:46:16--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8000::154, 2606:50c0:8001::154, 2606:50c0:8002::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8000::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73,28K  --.-KB/s    in 0,06s   

2025-02-24 10:46:17 (1,30 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
## Load the Rerank¶
You might need to adjust rerank parameters for different tasks:
In [ ]:
Copied!
```
truncate_input_tokens = 512

```

truncate_input_tokens = 512
#### Initialize `WatsonxRerank` instance.¶
You need to specify the `model_id` that will be used for rerank. You can find the list of all the available models in Supported reranker models.
In [ ]:
Copied!
```
from llama_index.postprocessor.ibm import WatsonxRerank

watsonx_rerank = WatsonxRerank(
    model_id="cross-encoder/ms-marco-minilm-l-12-v2",
    top_n=2,
    url=URL,
    project_id=PROJECT_ID,
    truncate_input_tokens=truncate_input_tokens,
)

```

from llama_index.postprocessor.ibm import WatsonxRerank watsonx_rerank = WatsonxRerank( model_id="cross-encoder/ms-marco-minilm-l-12-v2", top_n=2, url=URL, project_id=PROJECT_ID, truncate_input_tokens=truncate_input_tokens, )
Alternatively, you can use Cloud Pak for Data credentials. For details, see watsonx.ai software setup.
In [ ]:
Copied!
```
from llama_index.postprocessor.ibm import WatsonxRerank

watsonx_rerank = WatsonxRerank(
    model_id="cross-encoder/ms-marco-minilm-l-12-v2",
    url=URL,
    username="PASTE YOUR USERNAME HERE",
    password="PASTE YOUR PASSWORD HERE",
    instance_id="openshift",
    version="5.1",
    project_id=PROJECT_ID,
    truncate_input_tokens=truncate_input_tokens,
)

```

from llama_index.postprocessor.ibm import WatsonxRerank watsonx_rerank = WatsonxRerank( model_id="cross-encoder/ms-marco-minilm-l-12-v2", url=URL, username="PASTE YOUR USERNAME HERE", password="PASTE YOUR PASSWORD HERE", instance_id="openshift", version="5.1", project_id=PROJECT_ID, truncate_input_tokens=truncate_input_tokens, )
## Load the embedding model¶
#### Initialize the `WatsonxEmbeddings` instance.¶
> For more information about `WatsonxEmbeddings` please refer to the sample notebook: ![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
You might need to adjust embedding parameters for different tasks:
In [ ]:
Copied!
```
truncate_input_tokens = 512

```

truncate_input_tokens = 512
You need to specify the `model_id` that will be used for embedding. You can find the list of all the available models in Supported embedding models.
In [ ]:
Copied!
```
from llama_index.embeddings.ibm import WatsonxEmbeddings

watsonx_embedding = WatsonxEmbeddings(
    model_id="ibm/slate-30m-english-rtrvr",
    url=URL,
    project_id=PROJECT_ID,
    truncate_input_tokens=truncate_input_tokens,
)

```

from llama_index.embeddings.ibm import WatsonxEmbeddings watsonx_embedding = WatsonxEmbeddings( model_id="ibm/slate-30m-english-rtrvr", url=URL, project_id=PROJECT_ID, truncate_input_tokens=truncate_input_tokens, )
Change default settings
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.chunk_size = 512

```

from llama_index.core import Settings Settings.chunk_size = 512
#### Build index¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(
    documents=documents, embed_model=watsonx_embedding
)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents( documents=documents, embed_model=watsonx_embedding )
## Load the LLM¶
#### Initialize the `WatsonxLLM` instance.¶
> For more information about `WatsonxLLM` please refer to the sample notebook: ![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
You need to specify the `model_id` that will be used for inferencing. You can find the list of all the available models in Supported foundation models.
You might need to adjust model `parameters` for different models or tasks. For details, refer to Available MetaNames.
In [ ]:
Copied!
```
max_new_tokens = 128

```

max_new_tokens = 128
In [ ]:
Copied!
```
from llama_index.llms.ibm import WatsonxLLM

watsonx_llm = WatsonxLLM(
    model_id="meta-llama/llama-3-3-70b-instruct",
    url=URL,
    project_id=PROJECT_ID,
    max_new_tokens=max_new_tokens,
)

```

from llama_index.llms.ibm import WatsonxLLM watsonx_llm = WatsonxLLM( model_id="meta-llama/llama-3-3-70b-instruct", url=URL, project_id=PROJECT_ID, max_new_tokens=max_new_tokens, )
## Send a query¶
#### Retrieve top 10 most relevant nodes, then filter with `WatsonxRerank`¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    llm=watsonx_llm,
    similarity_top_k=10,
    node_postprocessors=[watsonx_rerank],
)
response = query_engine.query(
    "What did Sam Altman do in this essay?",
)

```

query_engine = index.as_query_engine( llm=watsonx_llm, similarity_top_k=10, node_postprocessors=[watsonx_rerank], ) response = query_engine.query( "What did Sam Altman do in this essay?", )
In [ ]:
Copied!
```
from llama_index.core.response.pprint_utils import pprint_response

pprint_response(response, show_source=True)

```

from llama_index.core.response.pprint_utils import pprint_response pprint_response(response, show_source=True)
```
Final Response: In this essay, Sam Altman was recruited to be the
president of Y Combinator (YC), and he agreed to take over the role
starting with the winter 2014 batch. He initially declined the offer,
wanting to start a startup to make nuclear reactors, but eventually
agreed after being persuaded. He began learning the job and taking
over responsibilities from the author in the latter part of 2013, and
officially took over as president in 2014.
______________________________________________________________________
Source Node 1/2
Node ID: 2ed5d8e7-2681-49b0-a112-ea35cc9a8b9e
Similarity: 3.2075154781341553
Text: "You know," he said, "you should make sure Y Combinator isn't
the last cool thing you do."  At the time I didn't understand what he
meant, but gradually it dawned on me that he was saying I should quit.
This seemed strange advice, because YC was doing great. But if there
was one thing rarer than Rtm offering advice, it was Rtm being wrong.
So th...
______________________________________________________________________
Source Node 2/2
Node ID: 6ae17865-aaa7-46a5-bc49-f38abf4a825e
Similarity: -1.3127477169036865
Text: I asked Jessica if she wanted to be president, but she didn't,
so we decided we'd try to recruit Sam Altman. We talked to Robert and
Trevor and we agreed to make it a complete changing of the guard. Up
till that point YC had been controlled by the original LLC we four had
started. But we wanted YC to last for a long time, and to do that it
could...

```

#### Directly retrieve top 2 most similar nodes¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    llm=watsonx_llm,
    similarity_top_k=2,
)
response = query_engine.query(
    "What did Sam Altman do in this essay?",
)

```

query_engine = index.as_query_engine( llm=watsonx_llm, similarity_top_k=2, ) response = query_engine.query( "What did Sam Altman do in this essay?", )
Retrieved context is irrelevant and response is hallucinated.
In [ ]:
Copied!
```
pprint_response(response, show_source=True)

```

pprint_response(response, show_source=True)
```
Final Response: Sam Altman was one of the founders of the first batch
of startups funded by the Summer Founders Program, and he later became
the second president of YC.
______________________________________________________________________
Source Node 1/2
Node ID: ba52769a-7342-4e6c-af02-4159216a79a8
Similarity: 0.6396056863136902
Text: We knew undergrads were deciding then about summer jobs, so in a
matter of days we cooked up something we called the Summer Founders
Program, and I posted an announcement on my site, inviting undergrads
to apply. I had never imagined that writing essays would be a way to
get "deal flow," as investors call it, but it turned out to be the
perfect ...
______________________________________________________________________
Source Node 2/2
Node ID: 43a6cf9f-8284-45db-bbbd-44109fcb9373
Similarity: 0.6334836031239921
Text: I wrote this new Lisp, called Bel, in itself in Arc. That may
sound like a contradiction, but it's an indication of the sort of
trickery I had to engage in to make this work. By means of an
egregious collection of hacks I managed to make something close enough
to an interpreter written in itself that could actually run. Not fast,
but fast enough...

```

