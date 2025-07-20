![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# HyDE Query Transform¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
#### Load documents, build the VectorStoreIndex¶
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.query_engine import TransformQueryEngine
from IPython.display import Markdown, display

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.indices.query.query_transform import HyDEQueryTransform from llama_index.core.query_engine import TransformQueryEngine from IPython.display import Markdown, display
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
## Example: HyDE improves specific temporal queries¶
In [ ]:
Copied!
```
query_str = "what did paul graham do after going to RISD"

```

query_str = "what did paul graham do after going to RISD"
#### First, we query _without_ transformation: The same query string is used for embedding lookup and also summarization.¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query(query_str)
display(Markdown(f"<b>{response}</b>"))

```

query_engine = index.as_query_engine() response = query_engine.query(query_str) display(Markdown(f"**{response}** "))
> After going to RISD, Paul Graham continued to pursue his passion for painting and art. He took classes in the painting department at the Accademia di Belli Arti in Florence, and he also took the entrance exam for the school. He also continued to work on his book On Lisp, and he took on consulting work to make money. At the school, Paul Graham and the other students had an arrangement where the faculty wouldn't require the students to learn anything, and in return the students wouldn't require the faculty to teach anything. Paul Graham was one of the few students who actually painted the nude model that was provided, while the rest of the students spent their time chatting or occasionally trying to imitate things they'd seen in American art magazines. The model turned out to live just down the street from Paul Graham, and she made a living from a combination of modelling and making fakes for a local antique dealer.
#### Now, we use `HyDEQueryTransform` to generate a hypothetical document and use it for embedding lookup.¶
In [ ]:
Copied!
```
hyde = HyDEQueryTransform(include_original=True)
hyde_query_engine = TransformQueryEngine(query_engine, hyde)
response = hyde_query_engine.query(query_str)
display(Markdown(f"<b>{response}</b>"))

```

hyde = HyDEQueryTransform(include_original=True) hyde_query_engine = TransformQueryEngine(query_engine, hyde) response = hyde_query_engine.query(query_str) display(Markdown(f"**{response}** "))
> After going to RISD, Paul Graham worked as a consultant for Interleaf and then co-founded Viaweb with Robert Morris. They created a software that allowed users to build websites via the web and received $10,000 in seed funding from Idelle's husband Julian. They gave Julian 10% of the company in return for the initial legal work and business advice. Paul Graham had a negative net worth due to taxes he owed, so the seed funding was necessary for him to live on. They opened for business in January 1996 with 6 stores.
> Paul Graham then left Yahoo after his options vested and went back to New York. He resumed his old life, but now he was rich. He tried to paint, but he didn't have much energy or ambition. He eventually moved back to Cambridge and started working on a web app for making web apps. He recruited Dan Giffin and two undergrads to help him, but he eventually realized he didn't want to run a company and decided to build a subset of the project as an open source project. He and Dan worked on a new dialect of Lisp, which he called Arc, in a house he bought in Cambridge. The subset he built as an open source project was the new Lisp, whose
#### In this example, `HyDE` improves output quality significantly, by hallucinating accurately what Paul Graham did after RISD (see below), and thus improving the embedding quality, and final output.¶
In [ ]:
Copied!
```
query_bundle = hyde(query_str)
hyde_doc = query_bundle.embedding_strs[0]

```

query_bundle = hyde(query_str) hyde_doc = query_bundle.embedding_strs[0]
In [ ]:
Copied!
```
hyde_doc

```

hyde_doc
> After graduating from the Rhode Island School of Design (RISD) in 1985, Paul Graham went on to pursue a career in computer programming. He worked as a software developer for several companies, including Viaweb, which he co-founded in 1995. Viaweb was eventually acquired by Yahoo in 1998, and Graham used the proceeds to become a venture capitalist. He founded Y Combinator in 2005, a startup accelerator that has helped launch over 2,000 companies, including Dropbox, Airbnb, and Reddit. Graham has also written several books on programming and startups, and he continues to be an active investor in the tech industry.
## Failure case 1: HyDE may mislead when query can be mis-interpreted without context.¶
In [ ]:
Copied!
```
query_str = "What is Bel?"

```

query_str = "What is Bel?"
### Querying without transformation yields reasonable answer¶
In [ ]:
Copied!
```
response = query_engine.query(query_str)
display(Markdown(f"<b>{response}</b>"))

```

response = query_engine.query(query_str) display(Markdown(f"**{response}** "))
> Bel is a programming language that was written in Arc by Paul Graham over the course of four years (March 26, 2015 to October 12, 2019). It is based on John McCarthy's original Lisp, but with additional features added. It is a spec expressed as code, and is meant to be a formal model of computation, an alternative to the Turing machine.
#### Querying with `HyDEQueryTransform` results in nonsense¶
In [ ]:
Copied!
```
hyde = HyDEQueryTransform(include_original=True)
hyde_query_engine = TransformQueryEngine(query_engine, hyde)
response = hyde_query_engine.query(query_str)
display(Markdown(f"<b>{response}</b>"))

```

hyde = HyDEQueryTransform(include_original=True) hyde_query_engine = TransformQueryEngine(query_engine, hyde) response = hyde_query_engine.query(query_str) display(Markdown(f"**{response}** "))
> Bel is the pseudonym of Paul Graham, the author of the context information who was in need of seed funding to live on and was part of a deal that became the model for Y Combinator's.
#### In this example, `HyDE` mis-interprets Bel without document context (see below), resulting in a completely unrelated embedding string and poor retrieval outcome.¶
In [ ]:
Copied!
```
query_bundle = hyde(query_str)
hyde_doc = query_bundle.embedding_strs[0]

```

query_bundle = hyde(query_str) hyde_doc = query_bundle.embedding_strs[0]
In [ ]:
Copied!
```
hyde_doc

```

hyde_doc
> Bel is an ancient Semitic god, originating from the Middle East. He is often associated with the sun and is sometimes referred to as the "Lord of Heaven". Bel is also known as the god of fertility, abundance, and prosperity. He is often depicted as a bull or a man with a bull's head. In some cultures, Bel is seen as a creator god, responsible for the creation of the universe. He is also associated with the underworld and is sometimes seen as a god of death. Bel is also associated with justice and is often seen as a protector of the innocent. Bel is an important figure in many religions, including Judaism, Christianity, and Islam.
## Failure case 2: HyDE may bias open-ended queries¶
In [ ]:
Copied!
```
query_str = "What would the author say about art vs. engineering?"

```

query_str = "What would the author say about art vs. engineering?"
#### Querying without transformation yields a reasonable answer¶
In [ ]:
Copied!
```
response = query_engine.query(query_str)
display(Markdown(f"<b>{response}</b>"))

```

response = query_engine.query(query_str) display(Markdown(f"**{response}** "))
> The author would likely say that art and engineering are two different disciplines that require different skills and approaches. Art is more focused on expression and creativity, while engineering is more focused on problem-solving and technical knowledge. The author also suggests that art school does not always provide the same level of rigor as engineering school, and that painting students are often encouraged to develop a signature style rather than learn the fundamentals of painting. Furthermore, the author would likely point out that engineering can provide more financial stability than art, as evidenced by the author's own experience of needing seed funding to live on while launching a company.
#### Querying with `HyDEQueryTransform` results in a more biased output¶
In [ ]:
Copied!
```
response = hyde_query_engine.query(query_str)
display(Markdown(f"<b>{response}</b>"))

```

response = hyde_query_engine.query(query_str) display(Markdown(f"**{response}** "))
> The author would likely say that art is a more lasting and independent form of work than engineering. They mention that software written today will be obsolete in a couple decades, and that systems work does not last. In contrast, they note that paintings can last hundreds of years and that it is possible to make a living as an artist. They also mention that as an artist, you can be truly independent and don't need to have a boss or research funding. Furthermore, they note that art can be a source of income for people who may not have access to traditional forms of employment, such as the model in the example who was able to make a living from modelling and making fakes for a local antique dealer.
