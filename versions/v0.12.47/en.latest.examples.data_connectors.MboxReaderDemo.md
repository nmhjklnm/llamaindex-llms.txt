![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Mbox Reader¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-mbox

```

%pip install llama-index-readers-mbox
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
%env OPENAI_API_KEY=sk-************

```

%env OPENAI_API_KEY=sk-************
In [ ]:
Copied!
```
from llama_index.readers.mbox import MboxReader
from llama_index.core import VectorStoreIndex

```

from llama_index.readers.mbox import MboxReader from llama_index.core import VectorStoreIndex
In [ ]:
Copied!
```
documents = MboxReader().load_data(
    "mbox_data_dir", max_count=1000
)  # Returns list of documents

```

documents = MboxReader().load_data( "mbox_data_dir", max_count=1000 ) # Returns list of documents
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(
    documents
)  # Initialize index with documents

```

index = VectorStoreIndex.from_documents( documents ) # Initialize index with documents
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
res = query_engine.query("When did i have that call with the London office?")

```

query_engine = index.as_query_engine() res = query_engine.query("When did i have that call with the London office?")
```
> [query] Total LLM token usage: 100 tokens
> [query] Total embedding token usage: 10 tokens

```

In [ ]:
Copied!
```
res.response

```

res.response
```
> There is a call scheduled with the London office at 12am GMT on the 10th of February.
```

