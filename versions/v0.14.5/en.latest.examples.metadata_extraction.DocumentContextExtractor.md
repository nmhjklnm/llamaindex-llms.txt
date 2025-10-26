# Contextual Retrieval With Llama Index¶
This notebook covers contextual retrieval with llama_index DocumentContextExtractor
Based on an Anthropic blost post, the concept is to:
  1. Use an LLM to generate a 'context' for each chunk based on the entire document
  2. embed the chunk + context together
  3. reap the benefits of higher RAG accuracy


While you can also do this manually, the DocumentContextExtractor offers a lot of convenience and error handling, plus you can integrate it into your llama_index pipelines! Let's get started.
NOTE: This notebook costs about $0.02 everytime you run it.
# Install Packages¶
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-readers-file
%pip install llama-index-embeddings-huggingface
%pip install llama-index-llms-openai

```

%pip install llama-index %pip install llama-index-readers-file %pip install llama-index-embeddings-huggingface %pip install llama-index-llms-openai
# Setup an LLM¶
You can use the MockLLM or you can use a real LLM of your choice here. flash 2 and gpt-4o-mini work well.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

OPENAI_API_KEY = "sk-..."
llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
Settings.llm = llm

```

from llama_index.llms.openai import OpenAI from llama_index.core import Settings OPENAI_API_KEY = "sk-..." llm = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY) Settings.llm = llm
# Setup a data pipeline¶
we'll need an embedding model, an index store, a vectore store, and a way to split tokens.
### Build Pipeline & Index¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.storage.docstore.simple_docstore import (
    SimpleDocumentStore,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Initialize document store and embedding model
docstore = SimpleDocumentStore()
embed_model = HuggingFaceEmbedding(model_name="baai/bge-small-en-v1.5")

# Create storage contexts
storage_context = StorageContext.from_defaults(docstore=docstore)
storage_context_no_extra_context = StorageContext.from_defaults()
text_splitter = TokenTextSplitter(
    separator=" ", chunk_size=256, chunk_overlap=10
)

```

from llama_index.core import VectorStoreIndex, StorageContext from llama_index.core.node_parser import TokenTextSplitter from llama_index.core.storage.docstore.simple_docstore import ( SimpleDocumentStore, ) from llama_index.embeddings.huggingface import HuggingFaceEmbedding # Initialize document store and embedding model docstore = SimpleDocumentStore() embed_model = HuggingFaceEmbedding(model_name="baai/bge-small-en-v1.5") # Create storage contexts storage_context = StorageContext.from_defaults(docstore=docstore) storage_context_no_extra_context = StorageContext.from_defaults() text_splitter = TokenTextSplitter( separator=" ", chunk_size=256, chunk_overlap=10 )
```
/Users/loganmarkewich/Library/Caches/pypoetry/virtualenvs/llama-index-caVs7DDe-py3.10/lib/python3.10/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

#### DocumentContextExtractor¶
In [ ]:
Copied!
```
# This is the new part!

from llama_index.core.extractors import DocumentContextExtractor

context_extractor = DocumentContextExtractor(
    # these 2 are mandatory
    docstore=docstore,
    max_context_length=128000,
    # below are optional
    llm=llm,  # default to Settings.llm
    oversized_document_strategy="warn",
    max_output_tokens=100,
    key="context",
    prompt=DocumentContextExtractor.SUCCINCT_CONTEXT_PROMPT,
)

```

# This is the new part! from llama_index.core.extractors import DocumentContextExtractor context_extractor = DocumentContextExtractor( # these 2 are mandatory docstore=docstore, max_context_length=128000, # below are optional llm=llm, # default to Settings.llm oversized_document_strategy="warn", max_output_tokens=100, key="context", prompt=DocumentContextExtractor.SUCCINCT_CONTEXT_PROMPT, )
# Load Data¶
In [ ]:
Copied!
```
!wget "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay_ambiguated.txt" -O "paul_graham_essay_ambiguated.txt"

```

!wget "https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay_ambiguated.txt" -O "paul_graham_essay_ambiguated.txt"
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

reader = SimpleDirectoryReader(
    input_files=["./paul_graham_essay_ambiguated.txt"]
)
documents = reader.load_data()

```

from llama_index.core import SimpleDirectoryReader reader = SimpleDirectoryReader( input_files=["./paul_graham_essay_ambiguated.txt"] ) documents = reader.load_data()
# Run the pipeline, then search¶
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

# need to add documents directly for the DocumentContextExtractor to work
storage_context.docstore.add_documents(documents)
index = VectorStoreIndex.from_documents(
    documents=documents,
    storage_context=storage_context,
    embed_model=embed_model,
    transformations=[text_splitter, context_extractor],
)

index_nocontext = VectorStoreIndex.from_documents(
    documents=documents,
    storage_context=storage_context_no_extra_context,
    embed_model=embed_model,
    transformations=[text_splitter],
)

```

import nest_asyncio nest_asyncio.apply() # need to add documents directly for the DocumentContextExtractor to work storage_context.docstore.add_documents(documents) index = VectorStoreIndex.from_documents( documents=documents, storage_context=storage_context, embed_model=embed_model, transformations=[text_splitter, context_extractor], ) index_nocontext = VectorStoreIndex.from_documents( documents=documents, storage_context=storage_context_no_extra_context, embed_model=embed_model, transformations=[text_splitter], )
```
100%|██████████| 15/15 [00:07<00:00,  2.10it/s]

```

In [ ]:
Copied!
```
test_question = "Which chunks of text discuss the IBM 704?"
retriever = index.as_retriever(similarity_top_k=2)
nodes_fromcontext = retriever.retrieve(test_question)

retriever_nocontext = index_nocontext.as_retriever(similarity_top_k=2)
nodes_nocontext = retriever_nocontext.retrieve(test_question)

```

test_question = "Which chunks of text discuss the IBM 704?" retriever = index.as_retriever(similarity_top_k=2) nodes_fromcontext = retriever.retrieve(test_question) retriever_nocontext = index_nocontext.as_retriever(similarity_top_k=2) nodes_nocontext = retriever_nocontext.retrieve(test_question)
In [ ]:
Copied!
```
# Print each node's content
print("==========")
print("NO CONTEXT")
for i, node in enumerate(nodes_nocontext, 1):
    print(f"\nChunk {i}:")
    print(f"Score: {node.score}")  # Similarity score
    print(f"Content: {node.node.text}")  # The actual text content

# Print each node's content
print("==========")
print("WITH CONTEXT")
for i, node in enumerate(nodes_fromcontext, 1):
    print(f"\nChunk {i}:")
    print(f"Score: {node.score}")  # Similarity score
    print(f"Content: {node.node.text}")  # The actual text content

```

# Print each node's content print("==========") print("NO CONTEXT") for i, node in enumerate(nodes_nocontext, 1): print(f"\nChunk {i}:") print(f"Score: {node.score}") # Similarity score print(f"Content: {node.node.text}") # The actual text content # Print each node's content print("==========") print("WITH CONTEXT") for i, node in enumerate(nodes_fromcontext, 1): print(f"\nChunk {i}:") print(f"Score: {node.score}") # Similarity score print(f"Content: {node.node.text}") # The actual text content
```
==========
NO CONTEXT

Chunk 1:
Score: 0.5710870309825231
Content: it. The result would ordinarily be to print something on the spectacularly loud device.  I was puzzled by the machine. I couldn't figure out what to do with it. And in retrospect there's not much I could have done with it. The only form of input to programs was data stored on cards, and I didn't have any information stored on them. The only other option was to do things that didn't rely on any input, like calculate approximations of pi, but I didn't know enough math to do anything interesting of that type. So I'm not surprised I can't remember any code I wrote, because it can't have done much. My clearest memory is of the moment I learned it was possible for programs not to terminate, when one of mine didn't. On a machine without time-sharing, this was a social as well as a technical error, as the manager's expression made clear. With microcomputers, everything changed. Now you could have one sitting right in front of you, on a desk, that could respond to your keystrokes as it was running instead of just churning through a stack of punched inputs

Chunk 2:
Score: 0.567587387219806
Content: McCarthy's 1960 paper.
But if so there's no reason to suppose that this is the limit of the language that might be known to them. Presumably aliens need numbers and errors and I/O too. So it seems likely there exists at least one path out of McCarthy's Lisp along which discoveredness is preserved.
Thanks to Trevor Blackwell, John Collison, Patrick Collison, Daniel Gackle, Ralph Hazell, Jessica Livingston, Robert Morris, and Harj Taggar for reading drafts of this.
==========
WITH CONTEXT

Chunk 1:
Score: 0.6776241992281743
Content: it. The result would ordinarily be to print something on the spectacularly loud device.  I was puzzled by the machine. I couldn't figure out what to do with it. And in retrospect there's not much I could have done with it. The only form of input to programs was data stored on cards, and I didn't have any information stored on them. The only other option was to do things that didn't rely on any input, like calculate approximations of pi, but I didn't know enough math to do anything interesting of that type. So I'm not surprised I can't remember any code I wrote, because it can't have done much. My clearest memory is of the moment I learned it was possible for programs not to terminate, when one of mine didn't. On a machine without time-sharing, this was a social as well as a technical error, as the manager's expression made clear. With microcomputers, everything changed. Now you could have one sitting right in front of you, on a desk, that could respond to your keystrokes as it was running instead of just churning through a stack of punched inputs

Chunk 2:
Score: 0.6200645958839048
Content: Before college the two main things I worked on, outside of school, were writing and programming. I didn't write essays. I wrote what beginning writers were supposed to write then, and probably still are: short stories. They were awful. They had hardly any plot, just characters with strong feelings, which I imagined made them deep. The first programs I tried writing were on the IBM 1401 that our school district used for what was then called "data processing." This was in 9th grade, so I was 13 or 14. The district's machine happened to be in the basement of our junior high school, and my friend Rich Draves and I got permission to use it. The space was like a mini Bond villain's lair down there, with all these alien-looking machines — CPU, disk drives, printer, card reader — sitting up on a raised floor under bright fluorescent lights. The language we used was an early version of Fortran. You had to type programs on punch cards, then stack them in the reader and press a button to load the code into memory and run it. The result would ordinarily be to print something

```

