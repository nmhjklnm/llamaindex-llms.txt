![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Upstage Embeddings¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-upstage==0.2.1

```

%pip install llama-index-embeddings-upstage==0.2.1
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

os.environ["UPSTAGE_API_KEY"] = "YOUR_API_KEY"

```

import os os.environ["UPSTAGE_API_KEY"] = "YOUR_API_KEY"
In [ ]:
Copied!
```
from llama_index.embeddings.upstage import UpstageEmbedding
from llama_index.core import Settings

embed_model = UpstageEmbedding()
Settings.embed_model = embed_model

```

from llama_index.embeddings.upstage import UpstageEmbedding from llama_index.core import Settings embed_model = UpstageEmbedding() Settings.embed_model = embed_model
## Using Upstage Embeddings¶
Note, you may have to update your openai client: `pip install -U openai`
In [ ]:
Copied!
```
# get API key and create embeddings
from llama_index.embeddings.upstage import UpstageEmbedding

embed_model = UpstageEmbedding()

embeddings = embed_model.get_text_embedding(
    "Upstage new Embeddings models is great."
)

```

# get API key and create embeddings from llama_index.embeddings.upstage import UpstageEmbedding embed_model = UpstageEmbedding() embeddings = embed_model.get_text_embedding( "Upstage new Embeddings models is great." )
In [ ]:
Copied!
```
print(embeddings[:5])

```

print(embeddings[:5])
```
[0.02535058930516243, 0.007272760849446058, 0.015372460708022118, -0.007840132340788841, 0.0017625312320888042]

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
embeddings = embed_model.get_query_embedding(
    "What are some great Embeddings model?"
)

```

embeddings = embed_model.get_query_embedding( "What are some great Embeddings model?" )
In [ ]:
Copied!
```
print(embeddings[:5])

```

print(embeddings[:5])
```
[0.03518765792250633, 0.01018011849373579, 0.013282101601362228, -0.008568626828491688, -0.005505830980837345]

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
# embed documents
embeddings = embed_model.get_text_embedding_batch(
    [
        "Upstage new Embeddings models is awesome.",
        "Upstage LLM is also awesome.",
    ]
)

```

# embed documents embeddings = embed_model.get_text_embedding_batch( [ "Upstage new Embeddings models is awesome.", "Upstage LLM is also awesome.", ] )
In [ ]:
Copied!
```
print(len(embeddings))

```

print(len(embeddings))


In [ ]:
Copied!
```
print(embeddings[0][:5])

```

print(embeddings[0][:5])
```
[0.028246860951185226, 0.008945596404373646, 0.01719627156853676, -0.005711239762604237, 0.0016300849383696914]

```

