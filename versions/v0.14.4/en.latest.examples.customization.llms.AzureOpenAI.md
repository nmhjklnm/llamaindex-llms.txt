![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Azure OpenAI¶
Azure openAI resources unfortunately differ from standard openAI resources as you can't generate embeddings unless you use an embedding model. The regions where these models are available can be found here: https://learn.microsoft.com/en-us/azure/cognitive-services/openai/concepts/models#embeddings-models
Furthermore the regions that support embedding models unfortunately don't support the latest versions (<*>-003) of openAI models, so we are forced to use one region for embeddings and another for the text generation.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-azure-openai
%pip install llama-index-llms-azure-openai

```

%pip install llama-index-embeddings-azure-openai %pip install llama-index-llms-azure-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import logging
import sys

logging.basicConfig(
    stream=sys.stdout, level=logging.INFO
)  # logging.DEBUG for more verbose output
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

from llama_index.llms.azure_openai import AzureOpenAI from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding from llama_index.core import VectorStoreIndex, SimpleDirectoryReader import logging import sys logging.basicConfig( stream=sys.stdout, level=logging.INFO ) # logging.DEBUG for more verbose output logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
Here, we setup the embedding model (for retrieval) and llm (for text generation). Note that you need not only model names (e.g. "text-embedding-ada-002"), but also model deployment names (the one you chose when deploying the model in Azure. You must pass the deployment name as a parameter when you initialize `AzureOpenAI` and `OpenAIEmbedding`.
In [ ]:
Copied!
```
api_key = "<api-key>"
azure_endpoint = "https://<your-resource-name>.openai.azure.com/"
api_version = "2023-07-01-preview"

llm = AzureOpenAI(
    model="gpt-35-turbo-16k",
    deployment_name="my-custom-llm",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

# You need to deploy your own embedding model as well as your own chat completion model
embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="my-custom-embedding",
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
)

```

api_key = "" azure_endpoint = "https://.openai.azure.com/" api_version = "2023-07-01-preview" llm = AzureOpenAI( model="gpt-35-turbo-16k", deployment_name="my-custom-llm", api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version, ) # You need to deploy your own embedding model as well as your own chat completion model embed_model = AzureOpenAIEmbedding( model="text-embedding-ada-002", deployment_name="my-custom-embedding", api_key=api_key, azure_endpoint=azure_endpoint, api_version=api_version, )
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model

```

from llama_index.core import Settings Settings.llm = llm Settings.embed_model = embed_model
In [ ]:
Copied!
```
documents = SimpleDirectoryReader(
    input_files=["../../data/paul_graham/paul_graham_essay.txt"]
).load_data()
index = VectorStoreIndex.from_documents(documents)

```

documents = SimpleDirectoryReader( input_files=["../../data/paul_graham/paul_graham_essay.txt"] ).load_data() index = VectorStoreIndex.from_documents(documents)
```
INFO:httpx:HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
query = "What is most interesting about this essay?"
query_engine = index.as_query_engine()
answer = query_engine.query(query)

print(answer.get_formatted_sources())
print("query was:", query)
print("answer was:", answer)

```

query = "What is most interesting about this essay?" query_engine = index.as_query_engine() answer = query_engine.query(query) print(answer.get_formatted_sources()) print("query was:", query) print("answer was:", answer)
```
INFO:httpx:HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-embedding/embeddings?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-llm/chat/completions?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-llm/chat/completions?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
HTTP Request: POST https://test-simon.openai.azure.com//openai/deployments/my-custom-llm/chat/completions?api-version=2023-07-01-preview "HTTP/1.1 200 OK"
> Source (Doc id: 3e0d1e3f-9099-483f-9abd-8f352c5e730f): A lot of Lisp hackers dream of building a new Lisp, partly because one of the distinctive feature...

> Source (Doc id: 06c1d986-1856-44cd-980d-651252ad1caf): What I Worked On

February 2021

Before college the two main things I worked on, outside of schoo...
query was: What is most interesting about this essay?
answer was: The most interesting aspect of this essay is the author's exploration of the transformative power of publishing essays online. The author reflects on how the internet has democratized the publishing process, allowing anyone to publish their work and reach a wide audience. This realization led the author to start writing and publishing essays online, which eventually became a significant part of their work. The author also discusses the initial skepticism and lack of prestige associated with online essays, but they find encouragement in the potential for genuine discovery and the absence of the desire to impress others. Overall, the essay highlights the author's personal journey and the impact of online publishing on their career.

```

