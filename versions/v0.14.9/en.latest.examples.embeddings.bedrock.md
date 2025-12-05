![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Bedrock Embeddings¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-bedrock

```

%pip install llama-index-embeddings-bedrock
In [ ]:
Copied!
```
import os

from llama_index.embeddings.bedrock import BedrockEmbedding

```

import os from llama_index.embeddings.bedrock import BedrockEmbedding
In [ ]:
Copied!
```
embed_model = BedrockEmbedding(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name="<aws-region>",
    profile_name="<aws-profile>",
)

```

embed_model = BedrockEmbedding( aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), aws_session_token=os.getenv("AWS_SESSION_TOKEN"), region_name="", profile_name="", )
In [ ]:
Copied!
```
embedding = embed_model.get_text_embedding("hello world")

```

embedding = embed_model.get_text_embedding("hello world")
## List supported models¶
To check list of supported models of Amazon Bedrock on LlamaIndex, call `BedrockEmbedding.list_supported_models()` as follows.
In [ ]:
Copied!
```
from llama_index.embeddings.bedrock import BedrockEmbedding
import json

supported_models = BedrockEmbedding.list_supported_models()
print(json.dumps(supported_models, indent=2))

```

from llama_index.embeddings.bedrock import BedrockEmbedding import json supported_models = BedrockEmbedding.list_supported_models() print(json.dumps(supported_models, indent=2))
## Provider: Amazon¶
Amazon Bedrock Titan embeddings.
In [ ]:
Copied!
```
from llama_index.embeddings.bedrock import BedrockEmbedding

model = BedrockEmbedding(model_name="amazon.titan-embed-g1-text-02")
embeddings = model.get_text_embedding("hello world")
print(embeddings)

```

from llama_index.embeddings.bedrock import BedrockEmbedding model = BedrockEmbedding(model_name="amazon.titan-embed-g1-text-02") embeddings = model.get_text_embedding("hello world") print(embeddings)
## Provider: Cohere¶
### cohere.embed-english-v3¶
In [ ]:
Copied!
```
model = BedrockEmbedding(model_name="cohere.embed-english-v3")
coherePayload = ["This is a test document", "This is another test document"]

embed1 = model.get_text_embedding("This is a test document")
print(embed1)

embeddings = model.get_text_embedding_batch(coherePayload)
print(embeddings)

```

model = BedrockEmbedding(model_name="cohere.embed-english-v3") coherePayload = ["This is a test document", "This is another test document"] embed1 = model.get_text_embedding("This is a test document") print(embed1) embeddings = model.get_text_embedding_batch(coherePayload) print(embeddings)
### MultiLingual Embeddings from Cohere¶
In [ ]:
Copied!
```
model = BedrockEmbedding(model_name="cohere.embed-multilingual-v3")
coherePayload = [
    "This is a test document",
    "తెలుగు అనేది ద్రావిడ భాషల కుటుంబానికి చెందిన భాష.",
    "Esto es una prueba de documento multilingüe.",
    "攻殻機動隊",
    "Combien de temps ça va prendre ?",
    "Документ проверен",
]
embeddings = model.get_text_embedding_batch(coherePayload)
print(embeddings)

```

model = BedrockEmbedding(model_name="cohere.embed-multilingual-v3") coherePayload = [ "This is a test document", "తెలుగు అనేది ద్రావిడ భాషల కుటుంబానికి చెందిన భాష.", "Esto es una prueba de documento multilingüe.", "攻殻機動隊", "Combien de temps ça va prendre ?", "Документ проверен", ] embeddings = model.get_text_embedding_batch(coherePayload) print(embeddings)
