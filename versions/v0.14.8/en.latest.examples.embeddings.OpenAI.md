![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# OpenAI Embeddings¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai

```

%pip install llama-index-embeddings-openai
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

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

embed_model = OpenAIEmbedding(embed_batch_size=10)
Settings.embed_model = embed_model

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import Settings embed_model = OpenAIEmbedding(embed_batch_size=10) Settings.embed_model = embed_model
## Using OpenAI `text-embedding-3-large` and `text-embedding-3-small`¶
Note, you may have to update your openai client: `pip install -U openai`
In [ ]:
Copied!
```
# get API key and create embeddings
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding(model="text-embedding-3-large")

embeddings = embed_model.get_text_embedding(
    "Open AI new Embeddings models is great."
)

```

# get API key and create embeddings from llama_index.embeddings.openai import OpenAIEmbedding embed_model = OpenAIEmbedding(model="text-embedding-3-large") embeddings = embed_model.get_text_embedding( "Open AI new Embeddings models is great." )
In [ ]:
Copied!
```
print(embeddings[:5])

```

print(embeddings[:5])
```
[-0.011500772088766098, 0.02457442320883274, -0.01760469563305378, -0.017763426527380943, 0.029841400682926178]

```

In [ ]:
Copied!
```
print(len(embeddings))

```

print(len(embeddings))


In [ ]:
Copied!
```
# get API key and create embeddings
from llama_index.embeddings.openai import OpenAIEmbedding

embed_model = OpenAIEmbedding(
    model="text-embedding-3-small",
)

embeddings = embed_model.get_text_embedding(
    "Open AI new Embeddings models is awesome."
)

```

# get API key and create embeddings from llama_index.embeddings.openai import OpenAIEmbedding embed_model = OpenAIEmbedding( model="text-embedding-3-small", ) embeddings = embed_model.get_text_embedding( "Open AI new Embeddings models is awesome." )
In [ ]:
Copied!
```
print(len(embeddings))

```

print(len(embeddings))


## Change the dimension of output embeddings¶
Note: Make sure you have the latest OpenAI client
In [ ]:
Copied!
```
# get API key and create embeddings
from llama_index.embeddings.openai import OpenAIEmbedding


embed_model = OpenAIEmbedding(
    model="text-embedding-3-large",
    dimensions=512,
)

embeddings = embed_model.get_text_embedding(
    "Open AI new Embeddings models with different dimensions is awesome."
)
print(len(embeddings))

```

# get API key and create embeddings from llama_index.embeddings.openai import OpenAIEmbedding embed_model = OpenAIEmbedding( model="text-embedding-3-large", dimensions=512, ) embeddings = embed_model.get_text_embedding( "Open AI new Embeddings models with different dimensions is awesome." ) print(len(embeddings))


