![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Vertex AI Search Retriever¶
This notebook walks you through how to setup a Retriever that can fetch from Vertex AI search datastore
### Pre-requirements¶
  * Set up a Google Cloud project
  * Set up a Vertex AI Search datastore
  * Enable Vertex AI API


### Install library¶
In [ ]:
Copied!
```
%pip install llama-index-retrievers-vertexai-search

```

%pip install llama-index-retrievers-vertexai-search
### Restart current runtime¶
To use the newly installed packages in this Jupyter runtime, you must restart the runtime. You can do this by running the cell below, which will restart the current kernel.
In [ ]:
Copied!
```
# Colab only
# Automatically restart kernel after installs so that your environment can access the new packages
import IPython

app = IPython.Application.instance()
app.kernel.do_shutdown(True)

```

# Colab only # Automatically restart kernel after installs so that your environment can access the new packages import IPython app = IPython.Application.instance() app.kernel.do_shutdown(True)
### Authenticate your notebook environment (Colab only)¶
If you are running this notebook on Google Colab, you will need to authenticate your environment. To do this, run the new cell below. This step is not required if you are using Vertex AI Workbench.
In [ ]:
Copied!
```
# Colab only
import sys

if "google.colab" in sys.modules:
    from google.colab import auth

    auth.authenticate_user()

```

# Colab only import sys if "google.colab" in sys.modules: from google.colab import auth auth.authenticate_user()
In [ ]:
Copied!
```
# If you're using JupyterLab instance, uncomment and run the below code.
#!gcloud auth login

```

# If you're using JupyterLab instance, uncomment and run the below code. #!gcloud auth login
In [ ]:
Copied!
```
from llama_index.retrievers.vertexai_search import VertexAISearchRetriever

# Please note it's underscore '_' in vertexai_search

```

from llama_index.retrievers.vertexai_search import VertexAISearchRetriever # Please note it's underscore '_' in vertexai_search
### Set Google Cloud project information and initialize Vertex AI SDK¶
To get started using Vertex AI, you must have an existing Google Cloud project and enable the Vertex AI API.
Learn more about setting up a project and a development environment.
In [ ]:
Copied!
```
PROJECT_ID = "{your project id}"  # @param {type:"string"}
LOCATION = "us-central1"  # @param {type:"string"}
import vertexai

vertexai.init(project=PROJECT_ID, location=LOCATION)

```

PROJECT_ID = "{your project id}" # @param {type:"string"} LOCATION = "us-central1" # @param {type:"string"} import vertexai vertexai.init(project=PROJECT_ID, location=LOCATION)
### Test Structured datastore¶
In [ ]:
Copied!
```
DATA_STORE_ID = "{your id}"  # @param {type:"string"}
LOCATION_ID = "global"

```

DATA_STORE_ID = "{your id}" # @param {type:"string"} LOCATION_ID = "global"
In [ ]:
Copied!
```
struct_retriever = VertexAISearchRetriever(
    project_id=PROJECT_ID,
    data_store_id=DATA_STORE_ID,
    location_id=LOCATION_ID,
    engine_data_type=1,
)

```

struct_retriever = VertexAISearchRetriever( project_id=PROJECT_ID, data_store_id=DATA_STORE_ID, location_id=LOCATION_ID, engine_data_type=1, )
In [ ]:
Copied!
```
query = "harry potter"
retrieved_results = struct_retriever.retrieve(query)

```

query = "harry potter" retrieved_results = struct_retriever.retrieve(query)
In [ ]:
Copied!
```
print(retrieved_results[0])

```

print(retrieved_results[0])
### Test Unstructured datastore¶
In [ ]:
Copied!
```
DATA_STORE_ID = "{your id}"
LOCATION_ID = "global"

```

DATA_STORE_ID = "{your id}" LOCATION_ID = "global"
In [ ]:
Copied!
```
unstruct_retriever = VertexAISearchRetriever(
    project_id=PROJECT_ID,
    data_store_id=DATA_STORE_ID,
    location_id=LOCATION_ID,
    engine_data_type=0,
)

```

unstruct_retriever = VertexAISearchRetriever( project_id=PROJECT_ID, data_store_id=DATA_STORE_ID, location_id=LOCATION_ID, engine_data_type=0, )
In [ ]:
Copied!
```
query = "alphabet 2018 earning"
retrieved_results2 = unstruct_retriever.retrieve(query)

```

query = "alphabet 2018 earning" retrieved_results2 = unstruct_retriever.retrieve(query)
In [ ]:
Copied!
```
print(retrieved_results2[0])

```

print(retrieved_results2[0])
### Test Website datastore¶
In [ ]:
Copied!
```
DATA_STORE_ID = "{your id}"
LOCATION_ID = "global"
website_retriever = VertexAISearchRetriever(
    project_id=PROJECT_ID,
    data_store_id=DATA_STORE_ID,
    location_id=LOCATION_ID,
    engine_data_type=2,
)

```

DATA_STORE_ID = "{your id}" LOCATION_ID = "global" website_retriever = VertexAISearchRetriever( project_id=PROJECT_ID, data_store_id=DATA_STORE_ID, location_id=LOCATION_ID, engine_data_type=2, )
In [ ]:
Copied!
```
query = "what's diamaxol"
retrieved_results3 = website_retriever.retrieve(query)

```

query = "what's diamaxol" retrieved_results3 = website_retriever.retrieve(query)
In [ ]:
Copied!
```
print(retrieved_results3[0])

```

print(retrieved_results3[0])
## Use in Query Engine¶
In [ ]:
Copied!
```
# import modules needed
from llama_index.core import Settings
from llama_index.llms.vertex import Vertex
from llama_index.embeddings.vertex import VertexTextEmbedding

```

# import modules needed from llama_index.core import Settings from llama_index.llms.vertex import Vertex from llama_index.embeddings.vertex import VertexTextEmbedding
In [ ]:
Copied!
```
vertex_gemini = Vertex(
    model="gemini-1.5-pro",
    temperature=0,
    context_window=100000,
    additional_kwargs={},
)
# setup the index/query llm
Settings.llm = vertex_gemini

```

vertex_gemini = Vertex( model="gemini-1.5-pro", temperature=0, context_window=100000, additional_kwargs={}, ) # setup the index/query llm Settings.llm = vertex_gemini
In [ ]:
Copied!
```
from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine.from_args(struct_retriever)

```

from llama_index.core.query_engine import RetrieverQueryEngine query_engine = RetrieverQueryEngine.from_args(struct_retriever)
In [ ]:
Copied!
```
response = query_engine.query("Tell me about harry potter")
print(str(response))

```

response = query_engine.query("Tell me about harry potter") print(str(response))
