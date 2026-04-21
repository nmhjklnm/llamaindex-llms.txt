![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# ModelScope Embeddings¶
In this notebook, we show how to use the ModelScope Embeddings in LlamaIndex. Check out the ModelScope site.
If you're opening this Notebook on colab, you will need to install LlamaIndex 🦙 and the modelscope.
In [ ]:
Copied!
```
!pip install llama-index-embeddings-modelscope

```

!pip install llama-index-embeddings-modelscope
## Basic Usage¶
In [ ]:
Copied!
```
import sys
from llama_index.embeddings.modelscope.base import ModelScopeEmbedding

model = ModelScopeEmbedding(
    model_name="iic/nlp_gte_sentence-embedding_chinese-base",
    model_revision="master",
)

rsp = model.get_query_embedding("Hello, who are you?")
print(rsp)

rsp = model.get_text_embedding("Hello, who are you?")
print(rsp)

```

import sys from llama_index.embeddings.modelscope.base import ModelScopeEmbedding model = ModelScopeEmbedding( model_name="iic/nlp_gte_sentence-embedding_chinese-base", model_revision="master", ) rsp = model.get_query_embedding("Hello, who are you?") print(rsp) rsp = model.get_text_embedding("Hello, who are you?") print(rsp)
#### Generate Batch Embedding¶
In [ ]:
Copied!
```
from llama_index.embeddings.modelscope.base import ModelScopeEmbedding

model = ModelScopeEmbedding(
    model_name="iic/nlp_gte_sentence-embedding_chinese-base",
    model_revision="master",
)

rsp = model.get_text_embedding_batch(
    ["Hello, who are you?", "I am a student."]
)
print(rsp)

```

from llama_index.embeddings.modelscope.base import ModelScopeEmbedding model = ModelScopeEmbedding( model_name="iic/nlp_gte_sentence-embedding_chinese-base", model_revision="master", ) rsp = model.get_text_embedding_batch( ["Hello, who are you?", "I am a student."] ) print(rsp)
