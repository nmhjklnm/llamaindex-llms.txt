![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Together AI Embeddings¶
This notebook shows how to use `Together AI` for embeddings. Together AI provides access to many state-of-the-art embedding models.
Visit https://together.ai and sign up to get an API key.
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-together

```

%pip install llama-index-embeddings-together
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# You can set the API key in the embeddings or env
# import os
# os.environ["TOEGETHER_API_KEY"] = "your-api-key"

from llama_index.embeddings.together import TogetherEmbedding

embed_model = TogetherEmbedding(
    model_name="togethercomputer/m2-bert-80M-8k-retrieval", api_key="..."
)

```

# You can set the API key in the embeddings or env # import os # os.environ["TOEGETHER_API_KEY"] = "your-api-key" from llama_index.embeddings.together import TogetherEmbedding embed_model = TogetherEmbedding( model_name="togethercomputer/m2-bert-80M-8k-retrieval", api_key="..." )
## Get Embeddings¶
In [ ]:
Copied!
```
embeddings = embed_model.get_text_embedding("hello world")

```

embeddings = embed_model.get_text_embedding("hello world")
In [ ]:
Copied!
```
print(len(embeddings))

```

print(len(embeddings))


In [ ]:
Copied!
```
print(embeddings[:5])

```

print(embeddings[:5])
```
[-0.11657876, -0.012690996, 0.24342081, 0.32781482, 0.022501636]

```

