# Netmind AI Embeddings¶
This notebook shows how to use `Netmind AI` for embeddings.
Visit https://www.netmind.ai/ and sign up to get an API key.
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-netmind

```

%pip install llama-index-embeddings-netmind
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
# os.environ["NETMIND_API_KEY"] = "your-api-key"

from llama_index.embeddings.netmind import NetmindEmbedding

embed_model = NetmindEmbedding(
    model_name="BAAI/bge-m3", api_key="your-api-key"
)

```

# You can set the API key in the embeddings or env # import os # os.environ["NETMIND_API_KEY"] = "your-api-key" from llama_index.embeddings.netmind import NetmindEmbedding embed_model = NetmindEmbedding( model_name="BAAI/bge-m3", api_key="your-api-key" )
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
[-0.04039396345615387, 0.03703497350215912, -0.02897450141608715, 0.016117244958877563, -0.03569157049059868]

```

