# VearchDemo
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
import openai
from IPython.display import Markdown, display
from llama_index import SimpleDirectoryReader, StorageContext, VectorStoreIndex

openai.api_key = ""

```

import openai from IPython.display import Markdown, display from llama_index import SimpleDirectoryReader, StorageContext, VectorStoreIndex openai.api_key = ""
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/examples/data/paul_graham/paul_graham_essay.txt'
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
print("Document ID:", len(documents), documents[0].doc_id)

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/examples/data/paul_graham/paul_graham_essay.txt' # load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data() print("Document ID:", len(documents), documents[0].doc_id)
```
Document ID: 1 8d84aefd-ca73-4c1e-b83d-141c1b1b3ba6

```

In [ ]:
Copied!
```
from llama_index import ServiceContext
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index.vector_stores import VearchVectorStore

"""
vearch cluster
"""
vector_store = VearchVectorStore(
    path_or_url="http://liama-index-router.vectorbase.svc.sq01.n.jd.local",
    table_name="liama_index_test2",
    db_name="liama_index",
    flag=1,
)

"""
vearch standalone
"""
# vector_store = VearchVectorStore(
#         path_or_url = '/data/zhx/zhx/liama_index/knowledge_base/liama_index_teststandalone',
#         # path_or_url = 'http://liama-index-router.vectorbase.svc.sq01.n.jd.local',
#         table_name = 'liama_index_teststandalone',
#         db_name = 'liama_index',
#         flag = 0)

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
service_context = ServiceContext.from_defaults(embed_model=embed_model)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, service_context=service_context
)

```

from llama_index import ServiceContext from llama_index.embeddings import HuggingFaceEmbedding from llama_index.vector_stores import VearchVectorStore """ vearch cluster """ vector_store = VearchVectorStore( path_or_url="http://liama-index-router.vectorbase.svc.sq01.n.jd.local", table_name="liama_index_test2", db_name="liama_index", flag=1, ) """ vearch standalone """ # vector_store = VearchVectorStore( # path_or_url = '/data/zhx/zhx/liama_index/knowledge_base/liama_index_teststandalone', # # path_or_url = 'http://liama-index-router.vectorbase.svc.sq01.n.jd.local', # table_name = 'liama_index_teststandalone', # db_name = 'liama_index', # flag = 0) embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5") service_context = ServiceContext.from_defaults(embed_model=embed_model) storage_context = StorageContext.from_defaults(vector_store=vector_store) index = VectorStoreIndex.from_documents( documents, storage_context=storage_context, service_context=service_context )
```
Loading checkpoint shards:   0%|          | 0/7 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
display(Markdown(f"<b>{response}</b>"))

```

query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?") display(Markdown(f"**{response}** "))
**The author did not provide any information about their growing up.**
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query(
    "What did the author do after his time at Y Combinator?"
)
display(Markdown(f"<b>{response}</b>"))

```

query_engine = index.as_query_engine() response = query_engine.query( "What did the author do after his time at Y Combinator?" ) display(Markdown(f"**{response}** "))
**The author wrote all of Y Combinator's internal software in Arc while continuing to work on Y Combinator, but later stopped working on Arc and focused on writing essays and working on Y Combinator. In 2012, the author's mother had a stroke, and the author realized that Y Combinator was taking up too much of their time and decided to hand it over to someone else. The author suggested this to Robert Morris, who offered unsolicited advice to the author to make sure Y Combinator wasn't the last cool thing the author did. The author ultimately decided to hand over the leadership of Y Combinator to Sam Altman in 2013.**
