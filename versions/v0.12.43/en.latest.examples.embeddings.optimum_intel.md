![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Optimized Embedding Model using Optimum-Intel¶
LlamaIndex has support for loading quantized embedding models for Intel, using the Optimum-Intel library.
Optimized models are smaller and faster, with minimal accuracy loss, see the documentation and an optimization guide using the IntelLabs/fastRAG library.
Optimization is based on math instructions in the Xeon® 4th generation or newer processors.
In order to be able to load and use the quantized models, install the required dependency `pip install optimum[exporters] optimum-intel neural-compressor intel_extension_for_pytorch`.
Loading is done using the class `IntelEmbedding`; usage is similar to any HuggingFace local embedding model; See example:
In [ ]:
Copied!
```
%pip install llama-index-embeddings-huggingface-optimum-intel

```

%pip install llama-index-embeddings-huggingface-optimum-intel
In [ ]:
Copied!
```
from llama_index.embeddings.huggingface_optimum_intel import IntelEmbedding

embed_model = IntelEmbedding("Intel/bge-small-en-v1.5-rag-int8-static")

```

from llama_index.embeddings.huggingface_optimum_intel import IntelEmbedding embed_model = IntelEmbedding("Intel/bge-small-en-v1.5-rag-int8-static")
In [ ]:
Copied!
```
embeddings = embed_model.get_text_embedding("Hello World!")
print(len(embeddings))
print(embeddings[:5])

```

embeddings = embed_model.get_text_embedding("Hello World!") print(len(embeddings)) print(embeddings[:5])
```
384
[-0.0032782123889774084, -0.013396517373621464, 0.037944991141557693, -0.04642259329557419, 0.027709005400538445]

```

