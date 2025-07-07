# Databricks Embeddings¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-embeddings-databricks

```

%pip install llama-index %pip install llama-index-embeddings-databricks
In [ ]:
Copied!
```
import os
from llama_index.core import Settings
from llama_index.embeddings.databricks import DatabricksEmbedding

```

import os from llama_index.core import Settings from llama_index.embeddings.databricks import DatabricksEmbedding
In [ ]:
Copied!
```
# Set up the DatabricksEmbedding class with the required model, API key and serving endpoint
os.environ["DATABRICKS_TOKEN"] = "<MY TOKEN>"
os.environ["DATABRICKS_SERVING_ENDPOINT"] = "<MY ENDPOINT>"
embed_model = DatabricksEmbedding(model="databricks-bge-large-en")
Settings.embed_model = embed_model

```

# Set up the DatabricksEmbedding class with the required model, API key and serving endpoint os.environ["DATABRICKS_TOKEN"] = "" os.environ["DATABRICKS_SERVING_ENDPOINT"] = "" embed_model = DatabricksEmbedding(model="databricks-bge-large-en") Settings.embed_model = embed_model
In [ ]:
Copied!
```
# Embed some text
embeddings = embed_model.get_text_embedding(
    "The DatabricksEmbedding integration works great."
)

```

# Embed some text embeddings = embed_model.get_text_embedding( "The DatabricksEmbedding integration works great." )
