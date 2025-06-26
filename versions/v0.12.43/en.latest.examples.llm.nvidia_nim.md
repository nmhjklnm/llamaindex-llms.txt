# NVIDIA NIMs¶
The `llama-index-llms-nvidia` package contains LlamaIndex integrations building applications with models on NVIDIA NIM inference microservice. NIM supports models across domains like chat, embedding, and re-ranking models from the community as well as NVIDIA. These models are optimized by NVIDIA to deliver the best performance on NVIDIA accelerated infrastructure and deployed as a NIM, an easy-to-use, prebuilt containers that deploy anywhere using a single command on NVIDIA accelerated infrastructure.
NVIDIA hosted deployments of NIMs are available to test on the NVIDIA API catalog. After testing, NIMs can be exported from NVIDIA’s API catalog using the NVIDIA AI Enterprise license and run on-premises or in the cloud, giving enterprises ownership and full control of their IP and AI application.
NIMs are packaged as container images on a per model basis and are distributed as NGC container images through the NVIDIA NGC Catalog. At their core, NIMs provide easy, consistent, and familiar APIs for running inference on an AI model.
In [ ]:
Copied!
```
!pip install llama-index-core
!pip install llama-index-readers-file
!pip install llama-index-llms-nvidia
!pip install llama-index-embeddings-nvidia
!pip install llama-index-postprocessor-nvidia-rerank

```

!pip install llama-index-core !pip install llama-index-readers-file !pip install llama-index-llms-nvidia !pip install llama-index-embeddings-nvidia !pip install llama-index-postprocessor-nvidia-rerank
Bring in a test dataset, a PDF about housing construction in San Francisco in 2021.
In [ ]:
Copied!
```
!mkdir data
!wget "https://www.dropbox.com/scl/fi/p33j9112y0ysgwg77fdjz/2021_Housing_Inventory.pdf?rlkey=yyok6bb18s5o31snjd2dxkxz3&dl=0" -O "data/housing_data.pdf"

```

!mkdir data !wget "https://www.dropbox.com/scl/fi/p33j9112y0ysgwg77fdjz/2021_Housing_Inventory.pdf?rlkey=yyok6bb18s5o31snjd2dxkxz3&dl=0" -O "data/housing_data.pdf"
```
--2024-05-28 17:42:44--  https://www.dropbox.com/scl/fi/p33j9112y0ysgwg77fdjz/2021_Housing_Inventory.pdf?rlkey=yyok6bb18s5o31snjd2dxkxz3&dl=0
Resolving www.dropbox.com (www.dropbox.com)... 162.125.1.18, 2620:100:6016:18::a27d:112
Connecting to www.dropbox.com (www.dropbox.com)|162.125.1.18|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: https://ucc6b49e945b8d71944c85f4a76d.dl.dropboxusercontent.com/cd/0/inline/CTzJ0ZeHC3AFIV3iv1bv9v0oMNXW03OW2waLdeKJNs0X6Tto0MSewm9RZBHwSLhqk4jWFaCmbhMGVXeWa6xPO4mAR4hC3xflJfwgS9Z4lpPUyE4AtlDXpnfsltjEaNeFCSY/file# [following]
--2024-05-28 17:42:45--  https://ucc6b49e945b8d71944c85f4a76d.dl.dropboxusercontent.com/cd/0/inline/CTzJ0ZeHC3AFIV3iv1bv9v0oMNXW03OW2waLdeKJNs0X6Tto0MSewm9RZBHwSLhqk4jWFaCmbhMGVXeWa6xPO4mAR4hC3xflJfwgS9Z4lpPUyE4AtlDXpnfsltjEaNeFCSY/file
Resolving ucc6b49e945b8d71944c85f4a76d.dl.dropboxusercontent.com (ucc6b49e945b8d71944c85f4a76d.dl.dropboxusercontent.com)... 162.125.4.15, 2620:100:6016:15::a27d:10f
Connecting to ucc6b49e945b8d71944c85f4a76d.dl.dropboxusercontent.com (ucc6b49e945b8d71944c85f4a76d.dl.dropboxusercontent.com)|162.125.4.15|:443... connected.
HTTP request sent, awaiting response... 302 Found
Location: /cd/0/inline2/CTySzMwupnuXzKpccOeYJ-7RI0NK0f7XMKBkpicHxSBuuwqAvFly51Fm0oCOwFctgeTqmD3thJsTqfFNOFHNe2JSIkJerj3mMr4Du3C7x1BcSy8t5raSfHQ_qSXF1eHrhdFII8Ou59jbofYVLe0punOl-RIa9k_v722SwkxVbg0KL9MrRL48XjX7JbsYHKTHq-gZSdAmpXpIGqS22eJavcSTuYMIy_GSZtDIs3quHM3PGU4849rG34RjpvAa-XkYDBdE996CxWupZ1C2Red9jEc5Tc6miGgt8-4LbGoxKwKF5I_Q3EqHCbvkibVR8OuKSKPtQZcNJSjsvIImzDLJ2WB6BAp2CBxz8szFF3jF3Gp6Iw/file [following]
--2024-05-28 17:42:45--  https://ucc6b49e945b8d71944c85f4a76d.dl.dropboxusercontent.com/cd/0/inline2/CTySzMwupnuXzKpccOeYJ-7RI0NK0f7XMKBkpicHxSBuuwqAvFly51Fm0oCOwFctgeTqmD3thJsTqfFNOFHNe2JSIkJerj3mMr4Du3C7x1BcSy8t5raSfHQ_qSXF1eHrhdFII8Ou59jbofYVLe0punOl-RIa9k_v722SwkxVbg0KL9MrRL48XjX7JbsYHKTHq-gZSdAmpXpIGqS22eJavcSTuYMIy_GSZtDIs3quHM3PGU4849rG34RjpvAa-XkYDBdE996CxWupZ1C2Red9jEc5Tc6miGgt8-4LbGoxKwKF5I_Q3EqHCbvkibVR8OuKSKPtQZcNJSjsvIImzDLJ2WB6BAp2CBxz8szFF3jF3Gp6Iw/file
Reusing existing connection to ucc6b49e945b8d71944c85f4a76d.dl.dropboxusercontent.com:443.
HTTP request sent, awaiting response... 200 OK
Length: 4808625 (4.6M) [application/pdf]
Saving to: ‘data/housing_data.pdf’

data/housing_data.p 100%[===================>]   4.58M  8.26MB/s    in 0.6s    

2024-05-28 17:42:47 (8.26 MB/s) - ‘data/housing_data.pdf’ saved [4808625/4808625]


```

## Setup¶
Import our dependencies and set up our NVIDIA API key from the API catalog, https://build.nvidia.com for the two models we'll use hosted on the catalog (embedding and re-ranking models).
**To get started:**
  1. Create a free account with NVIDIA, which hosts NVIDIA AI Foundation models.
  2. Click on your model of choice.
  3. Under Input select the Python tab, and click `Get API Key`. Then click `Generate Key`.
  4. Copy and save the generated key as NVIDIA_API_KEY. From there, you should have access to the endpoints.


In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Settings
from google.colab import userdata
import os

os.environ["NVIDIA_API_KEY"] = userdata.get("nvidia-api-key")

```

from llama_index.core import SimpleDirectoryReader, Settings, VectorStoreIndex from llama_index.embeddings.nvidia import NVIDIAEmbedding from llama_index.llms.nvidia import NVIDIA from llama_index.core.node_parser import SentenceSplitter from llama_index.core import Settings from google.colab import userdata import os os.environ["NVIDIA_API_KEY"] = userdata.get("nvidia-api-key")
Let's use a NVIDIA hosted NIM for the embedding model.
NVIDIA's default embeddings only embed the first 512 tokens so we've set our chunk size to 500 to maximize the accuracy of our embeddings.
In [ ]:
Copied!
```
Settings.text_splitter = SentenceSplitter(chunk_size=500)

documents = SimpleDirectoryReader("./data").load_data()

```

Settings.text_splitter = SentenceSplitter(chunk_size=500) documents = SimpleDirectoryReader("./data").load_data()
We set our embedding model to NVIDIA's default. If a chunk exceeds the number of tokens the model can encode, the default is to throw an error, so we set `truncate="END"` to instead discard tokens that go over the limit (hopefully not many because of our chunk size above).
In [ ]:
Copied!
```
Settings.embed_model = NVIDIAEmbedding(model="NV-Embed-QA", truncate="END")

index = VectorStoreIndex.from_documents(documents)

```

Settings.embed_model = NVIDIAEmbedding(model="NV-Embed-QA", truncate="END") index = VectorStoreIndex.from_documents(documents)
Now we've embedded our data and indexed it in memory, we set up our LLM that's self-hosted locally. NIM can be hosted locally using Docker in 5 minutes, following this NIM quick start guide.
Below, we show how to:
  * use Meta's open-source `meta/llama3-8b-instruct` model as a local NIM and
  * `meta/llama3-70b-instruct` as a NIM from the API catalog hosted by NVIDIA.


If you are using a local NIM, make sure you change the `base_url` to your deployed NIM URL!
We're going to retrieve the top 5 most relevant chunks to answer our question.
In [ ]:
Copied!
```
# self-hosted NIM: if you want to use a self-hosted NIM uncomment the line below
# and comment the line using the API catalog
# Settings.llm = NVIDIA(model="meta/llama3-8b-instruct", base_url="http://your-nim-host-address:8000/v1")

# api catalog NIM: if you're using a self-hosted NIM comment the line below
# and un-comment the line using local NIM above
Settings.llm = NVIDIA(model="meta/llama3-70b-instruct")

query_engine = index.as_query_engine(similarity_top_k=20)

```

# self-hosted NIM: if you want to use a self-hosted NIM uncomment the line below # and comment the line using the API catalog # Settings.llm = NVIDIA(model="meta/llama3-8b-instruct", base_url="http://your-nim-host-address:8000/v1") # api catalog NIM: if you're using a self-hosted NIM comment the line below # and un-comment the line using local NIM above Settings.llm = NVIDIA(model="meta/llama3-70b-instruct") query_engine = index.as_query_engine(similarity_top_k=20)
Let's ask it a simple question we know is answered in one place in the document (on page 18).
In [ ]:
Copied!
```
response = query_engine.query(
    "How many new housing units were built in San Francisco in 2021?"
)
print(response)

```

response = query_engine.query( "How many new housing units were built in San Francisco in 2021?" ) print(response)
```
There was a net addition of 4,649 units to the City’s housing stock in 2021.

```

Now let's ask it a more complicated question that requires reading a table (it's on page 41 of the document):
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
There is no specific information about the net gain in housing units in the Mission in 2021. The provided data is about the city's overall housing stock and production, but it does not provide a breakdown by neighborhood, including the Mission.

```

That's no good! This is net new, which isn't the number we wanted. Let's try a more advanced PDF parser, LlamaParse:
In [ ]:
Copied!
```
!pip install llama-parse

```

!pip install llama-parse
In [ ]:
Copied!
```
from llama_parse import LlamaParse

# in a notebook, LlamaParse requires this to work
import nest_asyncio

nest_asyncio.apply()

# you can get a key at cloud.llamaindex.ai
os.environ["LLAMA_CLOUD_API_KEY"] = userdata.get("llama-cloud-key")

# set up parser
parser = LlamaParse(
    result_type="markdown"  # "markdown" and "text" are available
)

# use SimpleDirectoryReader to parse our file
file_extractor = {".pdf": parser}
documents2 = SimpleDirectoryReader(
    "./data", file_extractor=file_extractor
).load_data()

```

from llama_parse import LlamaParse # in a notebook, LlamaParse requires this to work import nest_asyncio nest_asyncio.apply() # you can get a key at cloud.llamaindex.ai os.environ["LLAMA_CLOUD_API_KEY"] = userdata.get("llama-cloud-key") # set up parser parser = LlamaParse( result_type="markdown" # "markdown" and "text" are available ) # use SimpleDirectoryReader to parse our file file_extractor = {".pdf": parser} documents2 = SimpleDirectoryReader( "./data", file_extractor=file_extractor ).load_data()
```
Started parsing the file under job_id 84cb91f7-45ec-4b99-8281-0f4beef6a892

```

In [ ]:
Copied!
```
index2 = VectorStoreIndex.from_documents(documents2)
query_engine2 = index2.as_query_engine(similarity_top_k=20)

```

index2 = VectorStoreIndex.from_documents(documents2) query_engine2 = index2.as_query_engine(similarity_top_k=20)
In [ ]:
Copied!
```
response = query_engine2.query(
    "What was the net gain in housing units in the Mission in 2021?"
)
print(response)

```

response = query_engine2.query( "What was the net gain in housing units in the Mission in 2021?" ) print(response)
```
The net gain in housing units in the Mission in 2021 was 1,305 units.

```

Perfect! With a better parser, the LLM is able to answer the question.
Let's now try a trickier question:
In [ ]:
Copied!
```
response = query_engine2.query(
    "How many affordable housing units were completed in 2021?"
)
print(response)

```

response = query_engine2.query( "How many affordable housing units were completed in 2021?" ) print(response)
```
Repeat: 110

```

The LLM is getting confused; this appears to be the percentage increase in housing units.
Let's try giving the LLM more context (40 instead of 20) and then sorting those chunks with a reranker. We'll use NVIDIA's reranker for this:
In [ ]:
Copied!
```
from llama_index.postprocessor.nvidia_rerank import NVIDIARerank

query_engine3 = index2.as_query_engine(
    similarity_top_k=40, node_postprocessors=[NVIDIARerank(top_n=10)]
)

```

from llama_index.postprocessor.nvidia_rerank import NVIDIARerank query_engine3 = index2.as_query_engine( similarity_top_k=40, node_postprocessors=[NVIDIARerank(top_n=10)] )
In [ ]:
Copied!
```
response = query_engine3.query(
    "How many affordable housing units were completed in 2021?"
)
print(response)

```

response = query_engine3.query( "How many affordable housing units were completed in 2021?" ) print(response)
```
1,495

```

Excellent! Now the figure is correct (this is on page 35, in case you're wondering).
