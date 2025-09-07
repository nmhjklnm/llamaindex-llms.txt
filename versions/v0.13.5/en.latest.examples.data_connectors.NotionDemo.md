![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Notion Reader¶
Demonstrates our Notion data connector
In [ ]:
Copied!
```
%pip install llama-index-readers-notion

```

%pip install llama-index-readers-notion
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
from llama_index.core import SummaryIndex
from llama_index.readers.notion import NotionPageReader
from IPython.display import Markdown, display
import os

```

from llama_index.core import SummaryIndex from llama_index.readers.notion import NotionPageReader from IPython.display import Markdown, display import os
In [ ]:
Copied!
```
integration_token = os.getenv("NOTION_INTEGRATION_TOKEN")
page_ids = ["<page_id>"]
documents = NotionPageReader(integration_token=integration_token).load_data(
    page_ids=page_ids
)

```

integration_token = os.getenv("NOTION_INTEGRATION_TOKEN") page_ids = [""] documents = NotionPageReader(integration_token=integration_token).load_data( page_ids=page_ids )
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
You can also pass the id of a database to index all the pages in that database:
In [ ]:
Copied!
```
database_ids = ["<database-id>"]

# https://developers.notion.com/docs/working-with-databases for how to find your database id

documents = NotionPageReader(integration_token=integration_token).load_data(
    database_ids=database_ids
)

print(documents)

```

database_ids = [""] # https://developers.notion.com/docs/working-with-databases for how to find your database id documents = NotionPageReader(integration_token=integration_token).load_data( database_ids=database_ids ) print(documents)
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
index = SummaryIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("<query_text>")
display(Markdown(f"<b>{response}</b>"))

```

# set Logging to DEBUG for more detailed outputs index = SummaryIndex.from_documents(documents) query_engine = index.as_query_engine() response = query_engine.query("") display(Markdown(f"**{response}** "))
To list all databases in your Notion workspace:
In [ ]:
Copied!
```
reader = NotionPageReader(integration_token=integration_token)
databases = reader.list_databases()
print(databases)

```

reader = NotionPageReader(integration_token=integration_token) databases = reader.list_databases() print(databases)
