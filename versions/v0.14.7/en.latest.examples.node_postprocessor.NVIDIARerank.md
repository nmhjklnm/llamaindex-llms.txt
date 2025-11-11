# NVIDIA NIMs¶
The llama-index-postprocessor-nvidia-rerank` package contains LlamaIndex integrations building applications with models on NVIDIA NIM inference microservice. NIM supports models across domains like chat, embedding, and re-ranking models from the community as well as NVIDIA. These models are optimized by NVIDIA to deliver the best performance on NVIDIA accelerated infrastructure and deployed as a NIM, an easy-to-use, prebuilt containers that deploy anywhere using a single command on NVIDIA accelerated infrastructure.
NVIDIA hosted deployments of NIMs are available to test on the NVIDIA API catalog. After testing, NIMs can be exported from NVIDIA’s API catalog using the NVIDIA AI Enterprise license and run on-premises or in the cloud, giving enterprises ownership and full control of their IP and AI application.
NIMs are packaged as container images on a per model basis and are distributed as NGC container images through the NVIDIA NGC Catalog. At their core, NIMs provide easy, consistent, and familiar APIs for running inference on an AI model.
# NVIDIA's Rerank connector¶
This example goes over how to use LlamaIndex to interact with the supported NVIDIA Retrieval QA Ranking Model for retrieval-augmented generation via the `NVIDIARerank` class.
# Reranking¶
Reranking is a critical piece of high accuracy, efficient retrieval pipelines.
Two important use cases:
  * Combining results from multiple data sources
  * Enhancing accuracy for single data sources


## Combining results from multiple sources¶
Consider a pipeline with data from a semantic store, such as VectorStoreIndex, as well as a BM25 store.
Each store is queried independently and returns results that the individual store considers to be highly relevant. Figuring out the overall relevance of the results is where reranking comes into play.
Follow along with the Advanced - Hybrid Retriever + Re-Ranking use case, substitute the reranker with -
## Installation¶
In [ ]:
Copied!
```
%pip install --upgrade --quiet llama-index-postprocessor-nvidia-rerank llama-index-llms-nvidia llama-index-readers-file

```

%pip install --upgrade --quiet llama-index-postprocessor-nvidia-rerank llama-index-llms-nvidia llama-index-readers-file
## Setup¶
**To get started:**
  1. Create a free account with NVIDIA, which hosts NVIDIA AI Foundation models.
  2. Click on your model of choice.
  3. Under Input select the Python tab, and click `Get API Key`. Then click `Generate Key`.
  4. Copy and save the generated key as NVIDIA_API_KEY. From there, you should have access to the endpoints.


In [ ]:
Copied!
```
import getpass
import os

# del os.environ['NVIDIA_API_KEY']  ## delete key and reset
if os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
    print("Valid NVIDIA_API_KEY already in environment. Delete to reset")
else:
    nvapi_key = getpass.getpass("NVAPI Key (starts with nvapi-): ")
    assert nvapi_key.startswith(
        "nvapi-"
    ), f"{nvapi_key[:5]}... is not a valid key"
    os.environ["NVIDIA_API_KEY"] = nvapi_key

```

import getpass import os # del os.environ['NVIDIA_API_KEY'] ## delete key and reset if os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"): print("Valid NVIDIA_API_KEY already in environment. Delete to reset") else: nvapi_key = getpass.getpass("NVAPI Key (starts with nvapi-): ") assert nvapi_key.startswith( "nvapi-" ), f"{nvapi_key[:5]}... is not a valid key" os.environ["NVIDIA_API_KEY"] = nvapi_key
## Working with API Catalog¶
In [ ]:
Copied!
```
from llama_index.postprocessor.nvidia_rerank import NVIDIARerank
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
import os

reranker = NVIDIARerank(top_n=4)

```

from llama_index.postprocessor.nvidia_rerank import NVIDIARerank from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex from llama_index.embeddings.nvidia import NVIDIAEmbedding from llama_index.llms.nvidia import NVIDIA from llama_index.core.node_parser import SentenceSplitter from llama_index.core import Settings import os reranker = NVIDIARerank(top_n=4)
```
None of PyTorch, TensorFlow >= 2.0, or Flax have been found. Models won't be available and only tokenizers, configuration and file/data utilities can be used.

```

In [ ]:
Copied!
```
!mkdir data
!wget "https://www.dropbox.com/scl/fi/p33j9112y0ysgwg77fdjz/2021_Housing_Inventory.pdf?rlkey=yyok6bb18s5o31snjd2dxkxz3&dl=0" -O "data/housing_data.pdf"

```

!mkdir data !wget "https://www.dropbox.com/scl/fi/p33j9112y0ysgwg77fdjz/2021_Housing_Inventory.pdf?rlkey=yyok6bb18s5o31snjd2dxkxz3&dl=0" -O "data/housing_data.pdf"
```
mkdir: cannot create directory ‘data’: File exists
--2024-07-03 10:33:17--  https://www.dropbox.com/scl/fi/p33j9112y0ysgwg77fdjz/2021_Housing_Inventory.pdf?rlkey=yyok6bb18s5o31snjd2dxkxz3&dl=0
Resolving www.dropbox.com (www.dropbox.com)... 162.125.81.18, 2620:100:6031:18::a27d:5112
Connecting to www.dropbox.com (www.dropbox.com)|162.125.81.18|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: https://uc471d2c8af935aa4ab2f86937a6.dl.dropboxusercontent.com/cd/0/inline/CV9Hy3nIrjnOf-Fqsgd-YhHcMaj0AHvOQaE1b4sdiKnOBqZL_u9ml6dAGctGxr5I79yD_kI8BNwDtFl_ll_sdfdt0iXcIYosfxaPr2NdbkRAMR6vg9UXuCU8kNEFi0D3Grs/file# [following]
--2024-07-03 10:33:18--  https://uc471d2c8af935aa4ab2f86937a6.dl.dropboxusercontent.com/cd/0/inline/CV9Hy3nIrjnOf-Fqsgd-YhHcMaj0AHvOQaE1b4sdiKnOBqZL_u9ml6dAGctGxr5I79yD_kI8BNwDtFl_ll_sdfdt0iXcIYosfxaPr2NdbkRAMR6vg9UXuCU8kNEFi0D3Grs/file
Resolving uc471d2c8af935aa4ab2f86937a6.dl.dropboxusercontent.com (uc471d2c8af935aa4ab2f86937a6.dl.dropboxusercontent.com)... 162.125.81.15, 2620:100:6031:15::a27d:510f
Connecting to uc471d2c8af935aa4ab2f86937a6.dl.dropboxusercontent.com (uc471d2c8af935aa4ab2f86937a6.dl.dropboxusercontent.com)|162.125.81.15|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: /cd/0/inline2/CV9Ugj_mK7TSMb3sw_BdQFrj2rzx-SI2cfGU7-VF4bcW3PdhxO4qw--AXQKUidWtDL_54rViwvbaBGHMvtMEAK_lCIwXXj5XwkKpJKTmP0mDrz8eU2qu0FGyi4uOGfO7TeNLFMFY_bBGUMHMatvKJVPF59Ps94-8LC40ba-Cgv2YKZtcU-UjFpLh-Fnf6emkG-c8eUWB2uKPX_Lx0E4hCENQEPOGOfMhDHU0DC8k6khZiilmLtjXsDJ0H4y3efQ-Fz-VsWCC2FcoGpDcxXGu1Ysp5-mP2eHpH3qOx20d2IrndwN4RGLAqzR6cfsOHPMvoYPyLjOW1322t1O46mXqcjv94OPEEIIHI-2K8xL4pBjLUQ/file [following]
--2024-07-03 10:33:18--  https://uc471d2c8af935aa4ab2f86937a6.dl.dropboxusercontent.com/cd/0/inline2/CV9Ugj_mK7TSMb3sw_BdQFrj2rzx-SI2cfGU7-VF4bcW3PdhxO4qw--AXQKUidWtDL_54rViwvbaBGHMvtMEAK_lCIwXXj5XwkKpJKTmP0mDrz8eU2qu0FGyi4uOGfO7TeNLFMFY_bBGUMHMatvKJVPF59Ps94-8LC40ba-Cgv2YKZtcU-UjFpLh-Fnf6emkG-c8eUWB2uKPX_Lx0E4hCENQEPOGOfMhDHU0DC8k6khZiilmLtjXsDJ0H4y3efQ-Fz-VsWCC2FcoGpDcxXGu1Ysp5-mP2eHpH3qOx20d2IrndwN4RGLAqzR6cfsOHPMvoYPyLjOW1322t1O46mXqcjv94OPEEIIHI-2K8xL4pBjLUQ/file
Reusing existing connection to uc471d2c8af935aa4ab2f86937a6.dl.dropboxusercontent.com:443.
HTTP request sent, awaiting response... 200 OK
Length: 4808625 (4.6M) [application/pdf]
Saving to: ‘data/housing_data.pdf’

data/housing_data.p 100%[===================>]   4.58M  2.68MB/s    in 1.7s    

2024-07-03 10:33:21 (2.68 MB/s) - ‘data/housing_data.pdf’ saved [4808625/4808625]


```

In [ ]:
Copied!
```
Settings.text_splitter = SentenceSplitter(chunk_size=500)

documents = SimpleDirectoryReader("./data").load_data()

```

Settings.text_splitter = SentenceSplitter(chunk_size=500) documents = SimpleDirectoryReader("./data").load_data()
In [ ]:
Copied!
```
Settings.embed_model = NVIDIAEmbedding(model="NV-Embed-QA", truncate="END")

index = VectorStoreIndex.from_documents(documents)

```

Settings.embed_model = NVIDIAEmbedding(model="NV-Embed-QA", truncate="END") index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
Settings.llm = NVIDIA()

query_engine = index.as_query_engine(
    similarity_top_k=20, node_postprocessors=[reranker]
)

```

Settings.llm = NVIDIA() query_engine = index.as_query_engine( similarity_top_k=20, node_postprocessors=[reranker] )
In [ ]:
Copied!
```
response = query_engine.query(
    "What was the net gain in housing units in the Mission in 2021?"
)
print(response)

```

response = query_engine.query( "What was the net gain in housing units in the Mission in 2021?" ) print(response)
```
The net gain in housing units in the Mission in 2021 was not specified in the provided context information.

```

## Working with NVIDIA NIMs¶
In addition to connecting to hosted NVIDIA NIMs, this connector can be used to connect to local microservice instances. This helps you take your applications local when necessary.
For instructions on how to setup local microservice instances, see https://developer.nvidia.com/blog/nvidia-nim-offers-optimized-inference-microservices-for-deploying-ai-models-at-scale/
In [ ]:
Copied!
```
from llama_index.llms.nvidia import NVIDIA

# connect to a rerank NIM running at localhost:1976
reranker = NVIDIARerank(base_url="http://localhost:1976/v1")

```

from llama_index.llms.nvidia import NVIDIA # connect to a rerank NIM running at localhost:1976 reranker = NVIDIARerank(base_url="http://localhost:1976/v1")
