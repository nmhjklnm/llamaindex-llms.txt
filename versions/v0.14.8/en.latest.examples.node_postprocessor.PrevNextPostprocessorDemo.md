![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Forward/Backward Augmentation¶
Showcase capabilities of leveraging Node relationships on top of PG's essay
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
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.postprocessor import (
    PrevNextNodePostprocessor,
    AutoPrevNextNodePostprocessor,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.docstore import SimpleDocumentStore

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.postprocessor import ( PrevNextNodePostprocessor, AutoPrevNextNodePostprocessor, ) from llama_index.core.node_parser import SentenceSplitter from llama_index.core.storage.docstore import SimpleDocumentStore
#### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
### Parse Documents into Nodes, add to Docstore¶
In [ ]:
Copied!
```
# load documents
from llama_index.core import StorageContext


documents = SimpleDirectoryReader("./data/paul_graham").load_data()

# define settings
from llama_index.core import Settings

Settings.chunk_size = 512

# use node parser in settings to parse into nodes
nodes = Settings.node_parser.get_nodes_from_documents(documents)

# add to docstore
docstore = SimpleDocumentStore()
docstore.add_documents(nodes)

storage_context = StorageContext.from_defaults(docstore=docstore)

```

# load documents from llama_index.core import StorageContext documents = SimpleDirectoryReader("./data/paul_graham").load_data() # define settings from llama_index.core import Settings Settings.chunk_size = 512 # use node parser in settings to parse into nodes nodes = Settings.node_parser.get_nodes_from_documents(documents) # add to docstore docstore = SimpleDocumentStore() docstore.add_documents(nodes) storage_context = StorageContext.from_defaults(docstore=docstore)
### Build Index¶
In [ ]:
Copied!
```
# build index
index = VectorStoreIndex(nodes, storage_context=storage_context)

```

# build index index = VectorStoreIndex(nodes, storage_context=storage_context)
### Add PrevNext Node Postprocessor¶
In [ ]:
Copied!
```
node_postprocessor = PrevNextNodePostprocessor(docstore=docstore, num_nodes=4)

```

node_postprocessor = PrevNextNodePostprocessor(docstore=docstore, num_nodes=4)
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=1,
    node_postprocessors=[node_postprocessor],
    response_mode="tree_summarize",
)
response = query_engine.query(
    "What did the author do after handing off Y Combinator to Sam Altman?",
)

```

query_engine = index.as_query_engine( similarity_top_k=1, node_postprocessors=[node_postprocessor], response_mode="tree_summarize", ) response = query_engine.query( "What did the author do after handing off Y Combinator to Sam Altman?", )
In [ ]:
Copied!
```
print(response)

```

print(response)
```
After handing off Y Combinator to Sam Altman, the author decided to take up painting. He spent most of the rest of 2014 painting and eventually ran out of steam in November. He then started writing essays again and wrote a few that weren't about startups. In March 2015, he started working on Lisp again and wrote a new Lisp, called Bel, in itself in Arc. He banned himself from writing essays during most of this time and worked on Bel intensively. In the summer of 2016, he and his family moved to England and he continued working on Bel there. In the fall of 2019, Bel was finally finished and he wrote a bunch of essays about topics he had stacked up. He then started to think about other things he could work on and wrote an essay for himself to answer that question.

```

In [ ]:
Copied!
```
# Try querying index without node postprocessor
query_engine = index.as_query_engine(
    similarity_top_k=1, response_mode="tree_summarize"
)
response = query_engine.query(
    "What did the author do after handing off Y Combinator to Sam Altman?",
)

```

# Try querying index without node postprocessor query_engine = index.as_query_engine( similarity_top_k=1, response_mode="tree_summarize" ) response = query_engine.query( "What did the author do after handing off Y Combinator to Sam Altman?", )
In [ ]:
Copied!
```
print(response)

```

print(response)
```
The author decided to take up painting and spent the rest of 2014 painting. He wanted to see how good he could get if he really focused on it.

```

In [ ]:
Copied!
```
# Try querying index without node postprocessor and higher top-k
query_engine = index.as_query_engine(
    similarity_top_k=3, response_mode="tree_summarize"
)
response = query_engine.query(
    "What did the author do after handing off Y Combinator to Sam Altman?",
)

```

# Try querying index without node postprocessor and higher top-k query_engine = index.as_query_engine( similarity_top_k=3, response_mode="tree_summarize" ) response = query_engine.query( "What did the author do after handing off Y Combinator to Sam Altman?", )
In [ ]:
Copied!
```
print(response)

```

print(response)
```
After handing off Y Combinator to Sam Altman, the author decided to take a break and focus on painting. He also gave a talk to the Harvard Computer Society about how to start a startup, and decided to start angel investing. He also schemed with Robert and Trevor about projects they could work on together. Finally, he and Jessica decided to start their own investment firm, which eventually became Y Combinator.

```

### Add Auto Prev/Next Node Postprocessor¶
In [ ]:
Copied!
```
node_postprocessor = AutoPrevNextNodePostprocessor(
    docstore=docstore,
    num_nodes=3,
    verbose=True,
)

```

node_postprocessor = AutoPrevNextNodePostprocessor( docstore=docstore, num_nodes=3, verbose=True, )
In [ ]:
Copied!
```
# Infer that we need to search nodes after current one
query_engine = index.as_query_engine(
    similarity_top_k=1,
    node_postprocessors=[node_postprocessor],
    response_mode="tree_summarize",
)
response = query_engine.query(
    "What did the author do after handing off Y Combinator to Sam Altman?",
)

```

# Infer that we need to search nodes after current one query_engine = index.as_query_engine( similarity_top_k=1, node_postprocessors=[node_postprocessor], response_mode="tree_summarize", ) response = query_engine.query( "What did the author do after handing off Y Combinator to Sam Altman?", )
```
> Postprocessor Predicted mode: next

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
After handing off Y Combinator to Sam Altman, the author decided to take a break and focus on painting. He spent most of 2014 painting and was able to work more uninterruptedly than he had before. He also wrote a few essays that weren't about startups. In March 2015, he started working on Lisp again and wrote a new Lisp, called Bel, in itself in Arc. He had to ban himself from writing essays during most of this time in order to finish the project. In the summer of 2016, he and his family moved to England and he wrote most of Bel there. In the fall of 2019, Bel was finally finished. He then wrote a bunch of essays about topics he had stacked up and started to think about other things he could work on.

```

In [ ]:
Copied!
```
# Infer that we don't need to search previous or next
response = query_engine.query(
    "What did the author do during his time at Y Combinator?",
)

```

# Infer that we don't need to search previous or next response = query_engine.query( "What did the author do during his time at Y Combinator?", )
```
> Postprocessor Predicted mode: none

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The author did a variety of things during his time at Y Combinator, including hacking, writing essays, and working on YC. He also worked on a new version of Arc and wrote Hacker News in it. Additionally, he noticed the advantages of scaling startup funding and the tight community of alumni dedicated to helping one another.

```

In [ ]:
Copied!
```
# Infer that we need to search nodes before current one
response = query_engine.query(
    "What did the author do before handing off Y Combinator to Sam Altman?",
)

```

# Infer that we need to search nodes before current one response = query_engine.query( "What did the author do before handing off Y Combinator to Sam Altman?", )
```
> Postprocessor Predicted mode: previous

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Before handing off Y Combinator to Sam Altman, the author worked on writing essays, working on Y Combinator, writing all of Y Combinator's internal software in Arc, and fighting with people who maltreated the startups. He also spent time visiting his mother, who had a stroke and was in a nursing home, and thinking about what to do next.

```

In [ ]:
Copied!
```
response = query_engine.query(
    "What did the author do before handing off Y Combinator to Sam Altman?",
)

```

response = query_engine.query( "What did the author do before handing off Y Combinator to Sam Altman?", )
```
> Postprocessor Predicted mode: previous

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Before handing off Y Combinator to Sam Altman, the author worked on YC, wrote essays, and wrote all of YC's internal software in Arc. He also worked on a new version of Arc with Robert Morris, which he tested by writing Hacker News in it.

```

