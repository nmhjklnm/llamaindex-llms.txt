![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Mixedbread AI Embeddings¶
Explore the capabilities of MixedBread AI's embedding models with custom encoding formats (binary, int, float, base64, etc.), embedding dimensions (Matryoshka) and context prompts.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-mixedbreadai

```

%pip install llama-index-embeddings-mixedbreadai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import os
from llama_index.embeddings.mixedbreadai import MixedbreadAIEmbedding
from llama_index.embeddings.mixedbreadai import EncodingFormat

```

import os from llama_index.embeddings.mixedbreadai import MixedbreadAIEmbedding from llama_index.embeddings.mixedbreadai import EncodingFormat
In [ ]:
Copied!
```
# API Key and Embedding Initialization

# You can visit https://www.mixedbread.ai/api-reference#quick-start-guide
# to get an api key
mixedbread_api_key = os.environ.get("MXBAI_API_KEY", "your-api-key")

# Please check https://www.mixedbread.ai/docs/embeddings/models#whats-new-in-the-mixedbread-embed-model-family
# for our embedding models
model_name = "mixedbread-ai/mxbai-embed-large-v1"

```

# API Key and Embedding Initialization # You can visit https://www.mixedbread.ai/api-reference#quick-start-guide # to get an api key mixedbread_api_key = os.environ.get("MXBAI_API_KEY", "your-api-key") # Please check https://www.mixedbread.ai/docs/embeddings/models#whats-new-in-the-mixedbread-embed-model-family # for our embedding models model_name = "mixedbread-ai/mxbai-embed-large-v1"
In [ ]:
Copied!
```
oven = MixedbreadAIEmbedding(api_key=mixedbread_api_key, model_name=model_name)

embeddings = oven.get_query_embedding("Why bread is so tasty?")

print(len(embeddings))
print(embeddings[:5])

```

oven = MixedbreadAIEmbedding(api_key=mixedbread_api_key, model_name=model_name) embeddings = oven.get_query_embedding("Why bread is so tasty?") print(len(embeddings)) print(embeddings[:5])
```
1024
[0.011276245, 0.0309906, -0.0060424805, 0.029174805, -0.03857422]

```

### Using prompt for contextual embedding¶
The prompt can improve the model's understanding of how the embedding will be used in subsequent tasks, which in turn increases the performance. Our experiments show that having domain specific prompts can increase the performance.
In [ ]:
Copied!
```
prompt_for_retrieval = (
    "Represent this sentence for searching relevant passages:"
)

contextual_oven = MixedbreadAIEmbedding(
    api_key=mixedbread_api_key,
    model_name=model_name,
    prompt=prompt_for_retrieval,
)

contextual_embeddings = contextual_oven.get_query_embedding(
    "What bread is invented in Germany?"
)

print(len(contextual_embeddings))
print(contextual_embeddings[:5])

```

prompt_for_retrieval = ( "Represent this sentence for searching relevant passages:" ) contextual_oven = MixedbreadAIEmbedding( api_key=mixedbread_api_key, model_name=model_name, prompt=prompt_for_retrieval, ) contextual_embeddings = contextual_oven.get_query_embedding( "What bread is invented in Germany?" ) print(len(contextual_embeddings)) print(contextual_embeddings[:5])
```
1024
[-0.023544312, -0.015213013, 0.008407593, 0.00340271, -0.044708252]

```

## Quantization and Matryoshka support¶
The Mixedbread AI embedding supports quantization and matryoshka to reduce the size of embeddings for better storage while retaining most of the performance. See these posts for more information:
  * Binary and Scalar Embedding Quantization for Significantly Faster & Cheaper Retrieval
  * 64 bytes per embedding, yee-haw.


### Using different encoding formats¶
The default `encoding_format` is `float`. We also support `float16`, `binary`, `ubinary`, `int8`, `uint8`, `base64`.
In [ ]:
Copied!
```
# with `binary` embedding types
binary_oven = MixedbreadAIEmbedding(
    api_key=mixedbread_api_key,
    model_name=model_name,
    encoding_format=EncodingFormat.BINARY,
)

binary_embeddings = binary_oven.get_text_embedding(
    "The bread is tiny but still filling!"
)

print(len(binary_embeddings))
print(binary_embeddings[:5])

```

# with `binary` embedding types binary_oven = MixedbreadAIEmbedding( api_key=mixedbread_api_key, model_name=model_name, encoding_format=EncodingFormat.BINARY, ) binary_embeddings = binary_oven.get_text_embedding( "The bread is tiny but still filling!" ) print(len(binary_embeddings)) print(binary_embeddings[:5])
```
128
[-121.0, 96.0, -108.0, 111.0, 110.0]

```

### Using different embedding dimensions¶
Mixedbread AI embedding models support Matryoshka dimension truncation. The default dimension is set to the model's maximum. Keep an eye on our website to see what models support Matryoshka.
In [ ]:
Copied!
```
# with truncated dimension
half_oven = MixedbreadAIEmbedding(
    api_key=mixedbread_api_key,
    model_name=model_name,
    dimensions=512,  # 1024 is the maximum of `mxbai-embed-large-v1`
)

half_embeddings = half_oven.get_text_embedding(
    "I want the better half of my bread."
)

print(len(half_embeddings))
print(half_embeddings[:5])

```

# with truncated dimension half_oven = MixedbreadAIEmbedding( api_key=mixedbread_api_key, model_name=model_name, dimensions=512, # 1024 is the maximum of `mxbai-embed-large-v1` ) half_embeddings = half_oven.get_text_embedding( "I want the better half of my bread." ) print(len(half_embeddings)) print(half_embeddings[:5])
```
512
[-0.014221191, -0.013671875, -0.03314209, 0.025909424, -0.035095215]

```

