![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Qdrant FastEmbed Embeddings¶
LlamaIndex supports FastEmbed for embeddings generation.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-fastembed

```

%pip install llama-index-embeddings-fastembed
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
To use this provider, the `fastembed` package needs to be installed.
In [ ]:
Copied!
```
%pip install fastembed

```

%pip install fastembed
The list of supported models can be found here.
In [ ]:
Copied!
```
from llama_index.embeddings.fastembed import FastEmbedEmbedding

embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")

```

from llama_index.embeddings.fastembed import FastEmbedEmbedding embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")
```
100%|██████████| 76.7M/76.7M [00:18<00:00, 4.23MiB/s]

```

In [ ]:
Copied!
```
embeddings = embed_model.get_text_embedding("Some text to embed.")
print(len(embeddings))
print(embeddings[:5])

```

embeddings = embed_model.get_text_embedding("Some text to embed.") print(len(embeddings)) print(embeddings[:5])
```
384
[-0.04166769981384277, 0.0018720313673838973, 0.02632238157093525, -0.036030545830726624, -0.014812108129262924]

```

