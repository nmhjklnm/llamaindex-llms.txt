![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Faiss Reader¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-faiss

```

%pip install llama-index-readers-faiss
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
from llama_index.readers.faiss import FaissReader

```

from llama_index.readers.faiss import FaissReader
In [ ]:
Copied!
```
# Build the Faiss index.
# A guide for how to get started with Faiss is here: https://github.com/facebookresearch/faiss/wiki/Getting-started
# We provide some example code below.

import faiss

# # Example Code
# d = 8
# docs = np.array([
#     [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
#     [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2],
#     [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
#     [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4],
#     [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
# ])
# # id_to_text_map is used for query retrieval
# id_to_text_map = {
#     0: "aaaaaaaaa bbbbbbb cccccc",
#     1: "foooooo barrrrrr",
#     2: "tmp tmptmp tmp",
#     3: "hello world hello world",
#     4: "cat dog cat dog"
# }
# # build the index
# index = faiss.IndexFlatL2(d)
# index.add(docs)

id_to_text_map = {
    "id1": "text blob 1",
    "id2": "text blob 2",
}
index = ...

```

# Build the Faiss index. # A guide for how to get started with Faiss is here: https://github.com/facebookresearch/faiss/wiki/Getting-started # We provide some example code below. import faiss # # Example Code # d = 8 # docs = np.array([ # [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], # [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2], # [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3], # [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4], # [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5] # ]) # # id_to_text_map is used for query retrieval # id_to_text_map = { # 0: "aaaaaaaaa bbbbbbb cccccc", # 1: "foooooo barrrrrr", # 2: "tmp tmptmp tmp", # 3: "hello world hello world", # 4: "cat dog cat dog" # } # # build the index # index = faiss.IndexFlatL2(d) # index.add(docs) id_to_text_map = { "id1": "text blob 1", "id2": "text blob 2", } index = ...
In [ ]:
Copied!
```
reader = FaissReader(index)

```

reader = FaissReader(index)
In [ ]:
Copied!
```
# To load data from the Faiss index, you must specify:
# k: top nearest neighbors
# query: a 2D embedding representation of your queries (rows are queries)
k = 4
query1 = np.array([...])
query2 = np.array([...])
query = np.array([query1, query2])

documents = reader.load_data(query=query, id_to_text_map=id_to_text_map, k=k)

```

# To load data from the Faiss index, you must specify: # k: top nearest neighbors # query: a 2D embedding representation of your queries (rows are queries) k = 4 query1 = np.array([...]) query2 = np.array([...]) query = np.array([query1, query2]) documents = reader.load_data(query=query, id_to_text_map=id_to_text_map, k=k)
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
