![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# MistralAI Embeddings¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-mistralai

```

%pip install llama-index-embeddings-mistralai
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
from llama_index.embeddings.mistralai import MistralAIEmbedding

```

# imports from llama_index.embeddings.mistralai import MistralAIEmbedding
In [ ]:
Copied!
```
# get API key and create embeddings
api_key = "YOUR API KEY"
model_name = "mistral-embed"
embed_model = MistralAIEmbedding(model_name=model_name, api_key=api_key)

embeddings = embed_model.get_text_embedding("La Plateforme - The Platform")

```

# get API key and create embeddings api_key = "YOUR API KEY" model_name = "mistral-embed" embed_model = MistralAIEmbedding(model_name=model_name, api_key=api_key) embeddings = embed_model.get_text_embedding("La Plateforme - The Platform")
In [ ]:
Copied!
```
print(f"Dimension of embeddings: {len(embeddings)}")

```

print(f"Dimension of embeddings: {len(embeddings)}")
```
Dimension of embeddings: 1024

```

In [ ]:
Copied!
```
embeddings[:5]

```

embeddings[:5]
Out[ ]:
```
[-0.0299224853515625,
 -0.0028362274169921875,
 0.0282745361328125,
 -0.034759521484375,
 -0.0017366409301757812]
```

