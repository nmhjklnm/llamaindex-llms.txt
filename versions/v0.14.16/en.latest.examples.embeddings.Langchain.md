# LangChain Embeddings¶
This guide shows you how to use embedding models from LangChain.
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-langchain

```

%pip install llama-index-embeddings-langchain
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from langchain.embeddings import HuggingFaceEmbeddings
from llama_index.embeddings.langchain import LangchainEmbedding

lc_embed_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)
embed_model = LangchainEmbedding(lc_embed_model)

```

from langchain.embeddings import HuggingFaceEmbeddings from llama_index.embeddings.langchain import LangchainEmbedding lc_embed_model = HuggingFaceEmbeddings( model_name="sentence-transformers/all-mpnet-base-v2" ) embed_model = LangchainEmbedding(lc_embed_model)
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
```
768 [-0.005906202830374241, 0.04911914840340614, -0.04757878929376602, -0.04320324584841728, 0.02837090566754341, -0.017371710389852524, -0.04422023147344589, -0.019035547971725464, 0.04941621795296669, -0.03839121758937836]

```

