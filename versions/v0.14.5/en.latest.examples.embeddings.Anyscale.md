![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Anyscale Embeddings¶
This guide shows you how to use Anyscale Embeddings through Anyscale Endpoints.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-anyscale

```

%pip install llama-index-embeddings-anyscale
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.embeddings.anyscale import AnyscaleEmbedding

embed_model = AnyscaleEmbedding(
    api_key=ANYSCALE_ENDPOINT_TOKEN, embed_batch_size=10
)

```

from llama_index.embeddings.anyscale import AnyscaleEmbedding embed_model = AnyscaleEmbedding( api_key=ANYSCALE_ENDPOINT_TOKEN, embed_batch_size=10 )
In [ ]:
Copied!
```
# Basic embedding example
embeddings = embed_model.get_text_embedding(
    "It is raining cats and dogs here!"
)
print(len(embeddings), embeddings[:10])

```

# Basic embedding example embeddings = embed_model.get_text_embedding( "It is raining cats and dogs here!" ) print(len(embeddings), embeddings[:10])
