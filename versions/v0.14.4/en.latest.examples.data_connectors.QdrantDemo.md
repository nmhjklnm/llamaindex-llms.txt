![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Qdrant Reader¶
In [ ]:
Copied!
```
%pip install llama-index-readers-qdrant

```

%pip install llama-index-readers-qdrant
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.readers.qdrant import QdrantReader

```

from llama_index.readers.qdrant import QdrantReader
In [ ]:
Copied!
```
reader = QdrantReader(host="localhost")

```

reader = QdrantReader(host="localhost")
In [ ]:
Copied!
```
# the query_vector is an embedding representation of your query_vector
# Example query vector:
#   query_vector=[0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]

query_vector = [n1, n2, n3, ...]

```

# the query_vector is an embedding representation of your query_vector # Example query vector: # query_vector=[0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3] query_vector = [n1, n2, n3, ...]
In [ ]:
Copied!
```
# NOTE: Required args are collection_name, query_vector.
# See the Python client: https://github.com/qdrant/qdrant_client
# for more details.
documents = reader.load_data(
    collection_name="demo", query_vector=query_vector, limit=5
)

```

# NOTE: Required args are collection_name, query_vector. # See the Python client: https://github.com/qdrant/qdrant_client # for more details. documents = reader.load_data( collection_name="demo", query_vector=query_vector, limit=5 )
### Create index¶
In [ ]:
Copied!
```
index = SummaryIndex.from_documents(documents)

```

index = SummaryIndex.from_documents(documents)
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("<query_text>")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
