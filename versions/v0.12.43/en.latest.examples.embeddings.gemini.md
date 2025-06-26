![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Google Gemini Embeddings¶
**NOTE:** This example is deprecated. Please use the `GoogleGenAIEmbedding` class instead, detailed here.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-gemini

```

%pip install llama-index-embeddings-gemini
In [ ]:
Copied!
```
!pip install llama-index 'google-generativeai>=0.3.0' matplotlib

```

!pip install llama-index 'google-generativeai>=0.3.0' matplotlib
In [ ]:
Copied!
```
import os

GOOGLE_API_KEY = ""  # add your GOOGLE API key here
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

```

import os GOOGLE_API_KEY = "" # add your GOOGLE API key here os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
In [ ]:
Copied!
```
# imports
from llama_index.embeddings.gemini import GeminiEmbedding

```

# imports from llama_index.embeddings.gemini import GeminiEmbedding
In [ ]:
Copied!
```
# get API key and create embeddings

model_name = "models/embedding-001"

embed_model = GeminiEmbedding(
    model_name=model_name, api_key=GOOGLE_API_KEY, title="this is a document"
)

embeddings = embed_model.get_text_embedding("Google Gemini Embeddings.")

```

# get API key and create embeddings model_name = "models/embedding-001" embed_model = GeminiEmbedding( model_name=model_name, api_key=GOOGLE_API_KEY, title="this is a document" ) embeddings = embed_model.get_text_embedding("Google Gemini Embeddings.")
```
/Users/haotianzhang/llama_index/venv/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

In [ ]:
Copied!
```
print(f"Dimension of embeddings: {len(embeddings)}")

```

print(f"Dimension of embeddings: {len(embeddings)}")
```
Dimension of embeddings: 768

```

In [ ]:
Copied!
```
embeddings[:5]

```

embeddings[:5]
Out[ ]:
```
[0.028174246, -0.0290093, -0.013280814, 0.008629, 0.025442218]
```

In [ ]:
Copied!
```
embeddings = embed_model.get_query_embedding("Google Gemini Embeddings.")
embeddings[:5]

```

embeddings = embed_model.get_query_embedding("Google Gemini Embeddings.") embeddings[:5]
Out[ ]:
```
[0.028174246, -0.0290093, -0.013280814, 0.008629, 0.025442218]
```

In [ ]:
Copied!
```
embeddings = embed_model.get_text_embedding(
    ["Google Gemini Embeddings.", "Google is awesome."]
)

```

embeddings = embed_model.get_text_embedding( ["Google Gemini Embeddings.", "Google is awesome."] )
In [ ]:
Copied!
```
print(f"Dimension of embeddings: {len(embeddings)}")
print(embeddings[0][:5])
print(embeddings[1][:5])

```

print(f"Dimension of embeddings: {len(embeddings)}") print(embeddings[0][:5]) print(embeddings[1][:5])
```
Dimension of embeddings: 2
[0.028174246, -0.0290093, -0.013280814, 0.008629, 0.025442218]
[0.009427786, -0.009968997, -0.03341217, -0.025396815, 0.03210592]

```

In [ ]:
Copied!
```
embedding = await embed_model.aget_text_embedding("Google Gemini Embeddings.")
print(embedding[:5])

```

embedding = await embed_model.aget_text_embedding("Google Gemini Embeddings.") print(embedding[:5])
```
[0.028174246, -0.0290093, -0.013280814, 0.008629, 0.025442218]

```

In [ ]:
Copied!
```
embeddings = await embed_model.aget_text_embedding_batch(
    [
        "Google Gemini Embeddings.",
        "Google is awesome.",
        "Llamaindex is awesome.",
    ]
)
print(embeddings[0][:5])
print(embeddings[1][:5])
print(embeddings[2][:5])

```

embeddings = await embed_model.aget_text_embedding_batch( [ "Google Gemini Embeddings.", "Google is awesome.", "Llamaindex is awesome.", ] ) print(embeddings[0][:5]) print(embeddings[1][:5]) print(embeddings[2][:5])
```
[0.028174246, -0.0290093, -0.013280814, 0.008629, 0.025442218]
[0.009427786, -0.009968997, -0.03341217, -0.025396815, 0.03210592]
[0.013159992, -0.021570021, -0.060150445, -0.042500723, 0.041159637]

```

In [ ]:
Copied!
```
embedding = await embed_model.aget_query_embedding("Google Gemini Embeddings.")
print(embedding[:5])

```

embedding = await embed_model.aget_query_embedding("Google Gemini Embeddings.") print(embedding[:5])
```
[0.028174246, -0.0290093, -0.013280814, 0.008629, 0.025442218]

```

