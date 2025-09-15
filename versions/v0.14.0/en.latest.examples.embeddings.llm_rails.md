![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# LLMRails Embeddings¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-llm-rails

```

%pip install llama-index-embeddings-llm-rails
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# imports

from llama_index.embeddings.llm_rails import LLMRailsEmbedding

```

# imports from llama_index.embeddings.llm_rails import LLMRailsEmbedding
In [ ]:
Copied!
```
# get credentials and create embeddings

import os

api_key = os.environ.get("API_KEY", "your-api-key")
model_id = os.environ.get("MODEL_ID", "your-model-id")


embed_model = LLMRailsEmbedding(model_id=model_id, api_key=api_key)

embeddings = embed_model.get_text_embedding(
    "It is raining cats and dogs here!"
)

```

# get credentials and create embeddings import os api_key = os.environ.get("API_KEY", "your-api-key") model_id = os.environ.get("MODEL_ID", "your-model-id") embed_model = LLMRailsEmbedding(model_id=model_id, api_key=api_key) embeddings = embed_model.get_text_embedding( "It is raining cats and dogs here!" )
