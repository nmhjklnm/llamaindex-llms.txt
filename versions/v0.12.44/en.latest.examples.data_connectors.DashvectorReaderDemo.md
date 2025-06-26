![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# DashVector Reader¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-dashvector

```

%pip install llama-index-readers-dashvector
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
import os

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys import os logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
api_key = os.environ["DASHVECTOR_API_KEY"]

```

api_key = os.environ["DASHVECTOR_API_KEY"]
In [ ]:
Copied!
```
from llama_index.readers.dashvector import DashVectorReader

reader = DashVectorReader(api_key=api_key)

```

from llama_index.readers.dashvector import DashVectorReader reader = DashVectorReader(api_key=api_key)
In [ ]:
Copied!
```
import numpy as np

# the query_vector is an embedding representation of your query_vector
query_vector = [n1, n2, n3, ...]

```

import numpy as np # the query_vector is an embedding representation of your query_vector query_vector = [n1, n2, n3, ...]
In [ ]:
Copied!
```
# NOTE: Required args are index_name, id_to_text_map, vector.
# In addition, we can pass through the metadata filter that meet the SQL syntax.
# See the Python client: https://pypi.org/project/dashvector/ for more details.
documents = reader.load_data(
    collection_name="quickstart",
    topk=3,
    vector=query_vector,
    filter="key = 'value'",
    output_fields=["key1", "key2"],
)

```

# NOTE: Required args are index_name, id_to_text_map, vector. # In addition, we can pass through the metadata filter that meet the SQL syntax. # See the Python client: https://pypi.org/project/dashvector/ for more details. documents = reader.load_data( collection_name="quickstart", topk=3, vector=query_vector, filter="key = 'value'", output_fields=["key1", "key2"], )
### Create index¶
In [ ]:
Copied!
```
from llama_index.core import ListIndex
from IPython.display import Markdown, display

index = ListIndex.from_documents(documents)

```

from llama_index.core import ListIndex from IPython.display import Markdown, display index = ListIndex.from_documents(documents)
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
