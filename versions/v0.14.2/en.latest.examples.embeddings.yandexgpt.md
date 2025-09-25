# YandexGPT¶
In [ ]:
Copied!
```
%pip install llama-index-embeddings-yandexgpt

```

%pip install llama-index-embeddings-yandexgpt
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.embeddings.yandexgpt import YandexGPTEmbedding

yandexgpt_embedding = YandexGPTEmbedding(
    api_key="your-api-key", folder_id="your-folder-id"
)

text_embedding = yandexgpt_embedding._get_text_embeddings(
    ["This is a passage!", "This is another passage"]
)
print(text_embedding)

query_embedding = yandexgpt_embedding._get_query_embedding("Where is blue?")
print(query_embedding)

```

from llama_index.embeddings.yandexgpt import YandexGPTEmbedding yandexgpt_embedding = YandexGPTEmbedding( api_key="your-api-key", folder_id="your-folder-id" ) text_embedding = yandexgpt_embedding._get_text_embeddings( ["This is a passage!", "This is another passage"] ) print(text_embedding) query_embedding = yandexgpt_embedding._get_query_embedding("Where is blue?") print(query_embedding)
