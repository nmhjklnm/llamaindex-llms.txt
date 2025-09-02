![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Oracle Cloud Infrastructure Generative AI¶
Oracle Cloud Infrastructure (OCI) Generative AI is a fully managed service that provides a set of state-of-the-art, customizable large language models (LLMs) that cover a wide range of use cases, and which is available through a single API. Using the OCI Generative AI service you can access ready-to-use pretrained models, or create and host your own fine-tuned custom models based on your own data on dedicated AI clusters. Detailed documentation of the service and API is available **here** and **here**.
This notebook explains how to use OCI's Genrative AI embedding models with LlamaIndex.
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-oci-genai

```

%pip install llama-index-embeddings-oci-genai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
You will also need to install the OCI sdk
In [ ]:
Copied!
```
!pip install -U oci

```

!pip install -U oci
## Basic Usage¶
In [ ]:
Copied!
```
from llama_index.embeddings.oci_genai import OCIGenAIEmbeddings

embedding = OCIGenAIEmbeddings(
    model_name="cohere.embed-english-light-v3.0",
    service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com",
    compartment_id="MY_OCID",
)

e1 = embedding.get_text_embedding("This is a test document")
print(e1[-5:])

e2 = embedding.get_query_embedding("This is a test document")
print(e2[-5:])

docs = ["This is a test document", "This is another test document"]
e3 = embedding.get_text_embedding_batch(docs)
print(e3)

```

from llama_index.embeddings.oci_genai import OCIGenAIEmbeddings embedding = OCIGenAIEmbeddings( model_name="cohere.embed-english-light-v3.0", service_endpoint="https://inference.generativeai.us-chicago-1.oci.oraclecloud.com", compartment_id="MY_OCID", ) e1 = embedding.get_text_embedding("This is a test document") print(e1[-5:]) e2 = embedding.get_query_embedding("This is a test document") print(e2[-5:]) docs = ["This is a test document", "This is another test document"] e3 = embedding.get_text_embedding_batch(docs) print(e3)
