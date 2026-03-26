# Relyt¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
Firstly, you will probably need to install dependencies :
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-relyt

```

%pip install llama-index-vector-stores-relyt
In [ ]:
Copied!
```
%pip install llama-index "pgvecto_rs[sdk]"

```

%pip install llama-index "pgvecto_rs[sdk]"
Then start the relyt as the official document:
Setup the logger.
In [ ]:
Copied!
```
import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import os import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
#### Creating a pgvecto_rs client¶
In [ ]:
Copied!
```
from pgvecto_rs.sdk import PGVectoRs

URL = "postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}".format(
    port=os.getenv("RELYT_PORT", "5432"),
    host=os.getenv("RELYT_HOST", "localhost"),
    username=os.getenv("RELYT_USER", "postgres"),
    password=os.getenv("RELYT_PASS", "mysecretpassword"),
    db_name=os.getenv("RELYT_NAME", "postgres"),
)

client = PGVectoRs(
    db_url=URL,
    collection_name="example",
    dimension=1536,  # Using OpenAI’s text-embedding-ada-002
)

```

from pgvecto_rs.sdk import PGVectoRs URL = "postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}".format( port=os.getenv("RELYT_PORT", "5432"), host=os.getenv("RELYT_HOST", "localhost"), username=os.getenv("RELYT_USER", "postgres"), password=os.getenv("RELYT_PASS", "mysecretpassword"), db_name=os.getenv("RELYT_NAME", "postgres"), ) client = PGVectoRs( db_url=URL, collection_name="example", dimension=1536, # Using OpenAI’s text-embedding-ada-002 )
#### Setup OpenAI¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
#### Load documents, build the PGVectoRsStore and VectorStoreIndex¶
In [ ]:
Copied!
```
from IPython.display import Markdown, display

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.vector_stores.relyt import RelytVectorStore

```

from IPython.display import Markdown, display from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.vector_stores.relyt import RelytVectorStore
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham").load_data()
In [ ]:
Copied!
```
# initialize without metadata filter
from llama_index.core import StorageContext

vector_store = RelytVectorStore(client=client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

# initialize without metadata filter from llama_index.core import StorageContext vector_store = RelytVectorStore(client=client) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex.from_documents( documents, storage_context=storage_context )
#### Query Index¶
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?")
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
**The author, growing up, worked on writing and programming. They wrote short stories and also tried writing programs on an IBM 1401 computer. They later got a microcomputer and started programming more extensively, writing simple games and a word processor.**
