![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Google PaLM Embeddings¶
**NOTE:** This example is deprecated. Please use the `GoogleGenAIEmbedding` class instead, detailed here.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-google

```

%pip install llama-index-embeddings-google
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
from llama_index.embeddings.google import GooglePaLMEmbedding

```

# imports from llama_index.embeddings.google import GooglePaLMEmbedding
In [ ]:
Copied!
```
# get API key and create embeddings

model_name = "models/embedding-gecko-001"
api_key = "YOUR API KEY"

embed_model = GooglePaLMEmbedding(model_name=model_name, api_key=api_key)

embeddings = embed_model.get_text_embedding("Google PaLM Embeddings.")

```

# get API key and create embeddings model_name = "models/embedding-gecko-001" api_key = "YOUR API KEY" embed_model = GooglePaLMEmbedding(model_name=model_name, api_key=api_key) embeddings = embed_model.get_text_embedding("Google PaLM Embeddings.")
```
/opt/homebrew/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
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
[0.028517298, -0.0028859433, -0.035110522, 0.021982985, -0.0039763353]
```

