![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# IBM watsonx.ai¶
> WatsonxEmbeddings is a wrapper for IBM watsonx.ai embedding models.
This example shows how to communicate with `watsonx.ai` embedding models using the `LlamaIndex` Embeddings API.
## Setting up¶
Install the `llama-index-embeddings-ibm` package:
In [ ]:
Copied!
```
!pip install -qU llama-index-embeddings-ibm

```

!pip install -qU llama-index-embeddings-ibm
The cell below defines the credentials required to work with watsonx Embeddings.
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
## Load the model¶
You might need to adjust embedding parameters for different tasks:
In [ ]:
Copied!
```
truncate_input_tokens = 3

```

truncate_input_tokens = 3
Initialize the `WatsonxEmbeddings` class with the previously set parameter.
**Note** :
  * To provide context for the API call, you must pass the `project_id` or `space_id`. To get your project or space ID, open your project or space, go to the **Manage** tab, and click **General**. For more information see: Project documentation or Deployment space documentation.
  * Depending on the region of your provisioned service instance, use one of the urls listed in watsonx.ai API Authentication.


In this example, we’ll use the `project_id` and Dallas URL.
You need to specify the `model_id` that will be used for inferencing. You can find the list of all the available models in Supported foundation models.
In [ ]:
Copied!
```
from llama_index.embeddings.ibm import WatsonxEmbeddings

watsonx_embedding = WatsonxEmbeddings(
    model_id="ibm/slate-125m-english-rtrvr",
    url="https://us-south.ml.cloud.ibm.com",
    project_id="PASTE YOUR PROJECT_ID HERE",
    truncate_input_tokens=truncate_input_tokens,
)

```

from llama_index.embeddings.ibm import WatsonxEmbeddings watsonx_embedding = WatsonxEmbeddings( model_id="ibm/slate-125m-english-rtrvr", url="https://us-south.ml.cloud.ibm.com", project_id="PASTE YOUR PROJECT_ID HERE", truncate_input_tokens=truncate_input_tokens, )
Alternatively, you can use Cloud Pak for Data credentials. For details, see watsonx.ai software setup.
In [ ]:
Copied!
```
watsonx_embedding = WatsonxEmbeddings(
    model_id="ibm/slate-125m-english-rtrvr",
    url="PASTE YOUR URL HERE",
    username="PASTE YOUR USERNAME HERE",
    password="PASTE YOUR PASSWORD HERE",
    instance_id="openshift",
    version="4.8",
    project_id="PASTE YOUR PROJECT_ID HERE",
    truncate_input_tokens=truncate_input_tokens,
)

```

watsonx_embedding = WatsonxEmbeddings( model_id="ibm/slate-125m-english-rtrvr", url="PASTE YOUR URL HERE", username="PASTE YOUR USERNAME HERE", password="PASTE YOUR PASSWORD HERE", instance_id="openshift", version="4.8", project_id="PASTE YOUR PROJECT_ID HERE", truncate_input_tokens=truncate_input_tokens, )
## Usage¶
### Embed query¶
In [ ]:
Copied!
```
query = "Example query."

query_result = watsonx_embedding.get_query_embedding(query)
print(query_result[:5])

```

query = "Example query." query_result = watsonx_embedding.get_query_embedding(query) print(query_result[:5])
```
[-0.05538924, 0.05161056, 0.01207759, 0.0017501727, -0.017691258]

```

### Embed list of texts¶
In [ ]:
Copied!
```
texts = ["This is a content of one document", "This is another document"]

doc_result = watsonx_embedding.get_text_embedding_batch(texts)
print(doc_result[0][:5])

```

texts = ["This is a content of one document", "This is another document"] doc_result = watsonx_embedding.get_text_embedding_batch(texts) print(doc_result[0][:5])
```
[0.009447167, -0.024981938, -0.02601326, -0.04048393, -0.05780444]

```

