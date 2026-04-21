![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Ollama Embeddings¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-ollama

```

%pip install llama-index-embeddings-ollama
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.embeddings.ollama import OllamaEmbedding

ollama_embedding = OllamaEmbedding(
    model_name="llama2",
    base_url="http://localhost:11434",
    ollama_additional_kwargs={"mirostat": 0},
)

pass_embedding = ollama_embedding.get_text_embedding_batch(
    ["This is a passage!", "This is another passage"], show_progress=True
)
print(pass_embedding)

query_embedding = ollama_embedding.get_query_embedding("Where is blue?")
print(query_embedding)

```

from llama_index.embeddings.ollama import OllamaEmbedding ollama_embedding = OllamaEmbedding( model_name="llama2", base_url="http://localhost:11434", ollama_additional_kwargs={"mirostat": 0}, ) pass_embedding = ollama_embedding.get_text_embedding_batch( ["This is a passage!", "This is another passage"], show_progress=True ) print(pass_embedding) query_embedding = ollama_embedding.get_query_embedding("Where is blue?") print(query_embedding)
