![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Tree Summarize¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
## Load Data¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

```

from llama_index.core import SimpleDirectoryReader
In [ ]:
Copied!
```
reader = SimpleDirectoryReader(
    input_files=["./data/paul_graham/paul_graham_essay.txt"]
)

```

reader = SimpleDirectoryReader( input_files=["./data/paul_graham/paul_graham_essay.txt"] )
In [ ]:
Copied!
```
docs = reader.load_data()

```

docs = reader.load_data()
In [ ]:
Copied!
```
text = docs[0].text

```

text = docs[0].text
## Summarize¶
In [ ]:
Copied!
```
from llama_index.core.response_synthesizers import TreeSummarize

```

from llama_index.core.response_synthesizers import TreeSummarize
In [ ]:
Copied!
```
summarizer = TreeSummarize(verbose=True)

```

summarizer = TreeSummarize(verbose=True)
In [ ]:
Copied!
```
response = await summarizer.aget_response("who is Paul Graham?", [text])

```

response = await summarizer.aget_response("who is Paul Graham?", [text])
```
6 text chunks after repacking
1 text chunks after repacking

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Paul Graham is a computer scientist, writer, artist, entrepreneur, investor, and essayist. He is best known for his work in artificial intelligence, Lisp programming, and writing the book On Lisp, as well as for co-founding the startup accelerator Y Combinator and for his essays on technology, business, and start-ups. He is also the creator of the programming language Arc and the Lisp dialect Bel.

```

