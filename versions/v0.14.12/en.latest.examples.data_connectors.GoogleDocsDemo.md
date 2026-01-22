![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Google Docs Reader¶
Demonstrates our Google Docs data connector
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-google

```

%pip install llama-index-readers-google
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
from llama_index.core import SummaryIndex
from llama_index.readers.google import GoogleDocsReader
from IPython.display import Markdown, display
import os

```

from llama_index.core import SummaryIndex from llama_index.readers.google import GoogleDocsReader from IPython.display import Markdown, display import os
In [ ]:
Copied!
```
# make sure credentials.json file exists
document_ids = ["<document_id>"]
documents = GoogleDocsReader().load_data(document_ids=document_ids)

```

# make sure credentials.json file exists document_ids = [""] documents = GoogleDocsReader().load_data(document_ids=document_ids)
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
