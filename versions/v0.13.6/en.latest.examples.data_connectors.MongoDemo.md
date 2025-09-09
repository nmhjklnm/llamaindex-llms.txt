![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# MongoDB Reader¶
Demonstrates our MongoDB data connector
In [ ]:
Copied!
```
%pip install llama-index-readers-mongodb

```

%pip install llama-index-readers-mongodb
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙 and pymongo.
In [ ]:
Copied!
```
!pip install llama-index pymongo

```

!pip install llama-index pymongo
In [ ]:
Copied!
```
from llama_index.core import SummaryIndex
from llama_index.readers.mongodb import SimpleMongoReader
from IPython.display import Markdown, display
import os

```

from llama_index.core import SummaryIndex from llama_index.readers.mongodb import SimpleMongoReader from IPython.display import Markdown, display import os
In [ ]:
Copied!
```
host = "<host>"
port = "<port>"
db_name = "<db_name>"
collection_name = "<collection_name>"
# query_dict is passed into db.collection.find()
query_dict = {}
field_names = ["text"]
reader = SimpleMongoReader(host, port)
documents = reader.load_data(
    db_name, collection_name, field_names, query_dict=query_dict
)

```

host = "" port = "" db_name = "" collection_name = "" # query_dict is passed into db.collection.find() query_dict = {} field_names = ["text"] reader = SimpleMongoReader(host, port) documents = reader.load_data( db_name, collection_name, field_names, query_dict=query_dict )
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
