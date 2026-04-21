![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Chroma Reader¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-chroma

```

%pip install llama-index-readers-chroma
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
from llama_index.readers.chroma import ChromaReader

```

from llama_index.readers.chroma import ChromaReader
In [ ]:
Copied!
```
# The chroma reader loads data from a persisted Chroma collection.
# This requires a collection name and a persist directory.

reader = ChromaReader(
    collection_name="chroma_collection",
    persist_directory="examples/data_connectors/chroma_collection",
)

```

# The chroma reader loads data from a persisted Chroma collection. # This requires a collection name and a persist directory. reader = ChromaReader( collection_name="chroma_collection", persist_directory="examples/data_connectors/chroma_collection", )
In [ ]:
Copied!
```
# the query_vector is an embedding representation of your query.
# Example query vector:
#   query_vector=[0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]

query_vector = [n1, n2, n3, ...]

```

# the query_vector is an embedding representation of your query. # Example query vector: # query_vector=[0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3] query_vector = [n1, n2, n3, ...]
In [ ]:
Copied!
```
# NOTE: Required args are collection_name, query_vector.
# See the Python client: https://github.com/chroma-core/chroma
# for more details.
documents = reader.load_data(
    collection_name="demo", query_vector=query_vector, limit=5
)

```

# NOTE: Required args are collection_name, query_vector. # See the Python client: https://github.com/chroma-core/chroma # for more details. documents = reader.load_data( collection_name="demo", query_vector=query_vector, limit=5 )
### Create index¶
In [ ]:
Copied!
```
from llama_index.core import SummaryIndex

index = SummaryIndex.from_documents(documents)

```

from llama_index.core import SummaryIndex index = SummaryIndex.from_documents(documents)
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
