![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Google Cloud LlamaIndex on Vertex AI for RAG¶
In this notebook, we will show you how to get started with the Vertex AI RAG API.
## Installation¶
In [ ]:
Copied!
```
%pip install llama-index-llms-gemini
%pip install llama-index-indices-managed-vertexai

```

%pip install llama-index-llms-gemini %pip install llama-index-indices-managed-vertexai
In [ ]:
Copied!
```
%pip install llama-index
%pip install google-cloud-aiplatform==1.53.0

```

%pip install llama-index %pip install google-cloud-aiplatform==1.53.0
### Setup¶
Follow the steps in this documentation to create a Google Cloud project and enable the Vertex AI API.
https://cloud.google.com/vertex-ai/docs/start/cloud-environment
### Authenticating your notebook environment¶
  * If you are using **Colab** to run this notebook, run the cell below and continue.
  * If you are using **Vertex AI Workbench** , check out the setup instructions here.


In [ ]:
Copied!
```
import sys

# Additional authentication is required for Google Colab
if "google.colab" in sys.modules:
    # Authenticate user to Google Cloud
    from google.colab import auth

    auth.authenticate_user()

    ! gcloud config set project {PROJECT_ID}
    ! gcloud auth application-default login -q

```

import sys # Additional authentication is required for Google Colab if "google.colab" in sys.modules: # Authenticate user to Google Cloud from google.colab import auth auth.authenticate_user() ! gcloud config set project {PROJECT_ID} ! gcloud auth application-default login -q
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
## Basic Usage¶
A `corpus` is a collection of `document`s. A `document` is a body of text that is broken into `chunk`s.
#### Set up LLM for RAG¶
In [ ]:
Copied!
```
from llama_index.core import Settings
from llama_index.llms.vertex import Vertex

vertex_gemini = Vertex(
    model="gemini-1.5-pro-preview-0514",
    temperature=0,
    context_window=100000,
    additional_kwargs={},
)

Settings.llm = vertex_gemini

```

from llama_index.core import Settings from llama_index.llms.vertex import Vertex vertex_gemini = Vertex( model="gemini-1.5-pro-preview-0514", temperature=0, context_window=100000, additional_kwargs={}, ) Settings.llm = vertex_gemini
In [ ]:
Copied!
```
from llama_index.indices.managed.vertexai import VertexAIIndex

# TODO(developer): Replace these values with your project information
project_id = "YOUR_PROJECT_ID"
location = "us-central1"

# Optional: If creating a new corpus
corpus_display_name = "my-corpus"
corpus_description = "Vertex AI Corpus for LlamaIndex"

# Create a corpus or provide an existing corpus ID
index = VertexAIIndex(
    project_id,
    location,
    corpus_display_name=corpus_display_name,
    corpus_description=corpus_description,
)
print(f"Newly created corpus name is {index.corpus_name}.")

# Upload local file
file_name = index.insert_file(
    file_path="data/paul_graham/paul_graham_essay.txt",
    metadata={
        "display_name": "paul_graham_essay",
        "description": "Paul Graham essay",
    },
)

```

from llama_index.indices.managed.vertexai import VertexAIIndex # TODO(developer): Replace these values with your project information project_id = "YOUR_PROJECT_ID" location = "us-central1" # Optional: If creating a new corpus corpus_display_name = "my-corpus" corpus_description = "Vertex AI Corpus for LlamaIndex" # Create a corpus or provide an existing corpus ID index = VertexAIIndex( project_id, location, corpus_display_name=corpus_display_name, corpus_description=corpus_description, ) print(f"Newly created corpus name is {index.corpus_name}.") # Upload local file file_name = index.insert_file( file_path="data/paul_graham/paul_graham_essay.txt", metadata={ "display_name": "paul_graham_essay", "description": "Paul Graham essay", }, )
Let's check that what we've ingested.
In [ ]:
Copied!
```
print(index.list_files())

```

print(index.list_files())
Let's ask the index a question.
In [ ]:
Copied!
```
# Querying.
query_engine = index.as_query_engine()
response = query_engine.query("What did Paul Graham do growing up?")

# Show response.
print(f"Response is {response.response}")

# Show cited passages that were used to construct the response.
for cited_text in [node.text for node in response.source_nodes]:
    print(f"Cited text: {cited_text}")

# Show answerability. 0 means not answerable from the passages.
# 1 means the model is certain the answer can be provided from the passages.
if response.metadata:
    print(
        f"Answerability: {response.metadata.get('answerable_probability', 0)}"
    )

```

# Querying. query_engine = index.as_query_engine() response = query_engine.query("What did Paul Graham do growing up?") # Show response. print(f"Response is {response.response}") # Show cited passages that were used to construct the response. for cited_text in [node.text for node in response.source_nodes]: print(f"Cited text: {cited_text}") # Show answerability. 0 means not answerable from the passages. # 1 means the model is certain the answer can be provided from the passages. if response.metadata: print( f"Answerability: {response.metadata.get('answerable_probability', 0)}" )
