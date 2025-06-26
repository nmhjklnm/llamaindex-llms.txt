![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# FLARE Query Engine¶
Adapted from the paper "Active Retrieval Augmented Generation"
Currently implements FLARE Instruct, which tells the LLM to generate retrieval instructions.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-4", temperature=0)
Settings.chunk_size = 512

```

from llama_index.llms.openai import OpenAI from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-4", temperature=0) Settings.chunk_size = 512
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
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

documents = SimpleDirectoryReader("./data/paul_graham").load_data()
index = VectorStoreIndex.from_documents(
    documents,
)

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex documents = SimpleDirectoryReader("./data/paul_graham").load_data() index = VectorStoreIndex.from_documents( documents, )
In [ ]:
Copied!
```
index_query_engine = index.as_query_engine(similarity_top_k=2)

```

index_query_engine = index.as_query_engine(similarity_top_k=2)
In [ ]:
Copied!
```
from llama_index.core.query_engine import FLAREInstructQueryEngine

flare_query_engine = FLAREInstructQueryEngine(
    query_engine=index_query_engine,
    max_iterations=7,
    verbose=True,
)

```

from llama_index.core.query_engine import FLAREInstructQueryEngine flare_query_engine = FLAREInstructQueryEngine( query_engine=index_query_engine, max_iterations=7, verbose=True, )
In [ ]:
Copied!
```
response = flare_query_engine.query(
    "Can you tell me about the author's trajectory in the startup world?"
)

```

response = flare_query_engine.query( "Can you tell me about the author's trajectory in the startup world?" )
```
Query: Can you tell me about the author's trajectory in the startup world?
Current response: 
Lookahead response: The author began their journey in the startup world by [Search(What did the author do in the startup world?)]
Updated lookahead response: The author began their journey in the startup world by co-founding Y Combinator (YC), a startup accelerator that provided funding and support to startups in batches. They aimed to fix issues in the venture capital industry by making a larger number of smaller investments, funding younger and more technical founders, and allowing founders to remain as CEOs. The author also wrote Hacker News, a news aggregator initially for startup founders, in a new version of Arc programming language.
Current response:  The author began their journey in the startup world by co-founding Y Combinator (YC), a startup accelerator that provided funding and support to startups in batches. They aimed to fix issues in the venture capital industry by making a larger number of smaller investments, funding younger and more technical founders, and allowing founders to remain as CEOs. The author also wrote Hacker News, a news aggregator initially for startup founders, in a new version of Arc programming language.
Lookahead response: Since then, the author has been involved in mentoring and advising numerous startups, helping them grow and succeed in their respective industries. [Search(What are some notable startups the author has worked with?)]
Updated lookahead response: Since then, the author has been involved in mentoring and advising numerous startups, helping them grow and succeed in their respective industries. Some notable startups the author has worked with include Reddit, Justin Kan and Emmett Shear (who went on to found Twitch), Aaron Swartz (who helped write the RSS spec), and Sam Altman (who later became the second president of YC).
Current response: The author began their journey in the startup world by co-founding Y Combinator (YC), a startup accelerator that provided funding and support to startups in batches. They aimed to fix issues in the venture capital industry by making a larger number of smaller investments, funding younger and more technical founders, and allowing founders to remain as CEOs. The author also wrote Hacker News, a news aggregator initially for startup founders, in a new version of Arc programming language. Since then, the author has been involved in mentoring and advising numerous startups, helping them grow and succeed in their respective industries. Some notable startups the author has worked with include Reddit, Justin Kan and Emmett Shear (who went on to found Twitch), Aaron Swartz (who helped write the RSS spec), and Sam Altman (who later became the second president of YC).
Lookahead response: done

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The author began their journey in the startup world by co-founding Y Combinator (YC), a startup accelerator that provided funding and support to startups in batches. They aimed to fix issues in the venture capital industry by making a larger number of smaller investments, funding younger and more technical founders, and allowing founders to remain as CEOs. The author also wrote Hacker News, a news aggregator initially for startup founders, in a new version of Arc programming language. Since then, the author has been involved in mentoring and advising numerous startups, helping them grow and succeed in their respective industries. Some notable startups the author has worked with include Reddit, Justin Kan and Emmett Shear (who went on to found Twitch), Aaron Swartz (who helped write the RSS spec), and Sam Altman (who later became the second president of YC). 

```

In [ ]:
Copied!
```
response = flare_query_engine.query(
    "Can you tell me about what the author did during his time at YC?"
)

```

response = flare_query_engine.query( "Can you tell me about what the author did during his time at YC?" )
```
Query: Can you tell me about what the author did during his time at YC?
Current response: 
Lookahead response: During his time at YC, the author [Search(What did the author do at YC?)]
Updated lookahead response: During his time at YC, the author worked on selecting and helping founders at YC, solving their problems, and engaging with their startups. They also wrote all of YC's internal software in Arc and managed Hacker News, which was a source of stress for them.
Current response:  During his time at YC, the author worked on selecting and helping founders at YC, solving their problems, and engaging with their startups. They also wrote all of YC's internal software in Arc and managed Hacker News, which was a source of stress for them.
Lookahead response: done

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
During his time at YC, the author worked on selecting and helping founders at YC, solving their problems, and engaging with their startups. They also wrote all of YC's internal software in Arc and managed Hacker News, which was a source of stress for them. 

```

In [ ]:
Copied!
```
response = flare_query_engine.query(
    "Tell me about the author's life from childhood to adulthood"
)

```

response = flare_query_engine.query( "Tell me about the author's life from childhood to adulthood" )
```
Query: Tell me about the author's life from childhood to adulthood
Current response: 
Lookahead response: The author grew up in a small town, where they [Search(What did the author do during their childhood?)] and later went on to attend college, majoring in [Search(What did the author major in during college?)].
Updated lookahead response: The author grew up in a small town, where they mainly worked on writing and programming outside of school. They wrote short stories and tried programming on the IBM 1401 using an early version of Fortran and later went on to attend college, majoring in 
Current response:  The author grew up in a small town, where they mainly worked on writing and programming outside of school. They wrote short stories and tried programming on the IBM 1401 using an early version of Fortran and later went on to attend college, majoring in
Lookahead response: computer science and English literature. After college, they [Search(What did the author do after college?)]
Updated lookahead response: computer science and English literature. After college, they wrote essays on various topics, worked on spam filters, did some painting, and hosted dinners for friends. They also bought a building in Cambridge to use as an office. Later, the author applied to art schools, got accepted into RISD, and attended their foundation classes. They also received an invitation to take the entrance exam at the Accademia di Belli Arti in Florence.
Current response: The author grew up in a small town, where they mainly worked on writing and programming outside of school. They wrote short stories and tried programming on the IBM 1401 using an early version of Fortran and later went on to attend college, majoring in computer science and English literature. After college, they wrote essays on various topics, worked on spam filters, did some painting, and hosted dinners for friends. They also bought a building in Cambridge to use as an office. Later, the author applied to art schools, got accepted into RISD, and attended their foundation classes. They also received an invitation to take the entrance exam at the Accademia di Belli Arti in Florence.
Lookahead response: During their time at RISD and the Accademia di Belli Arti, the author honed their artistic skills and further developed their writing, eventually transitioning into a successful career as an author and artist. [Search(What did the author achieve in their career?)]
Updated lookahead response: During their time at RISD and the Accademia di Belli Arti, the author honed their artistic skills and further developed their writing, eventually transitioning into a successful career as an author and artist. The author achieved several things in their career, including publishing essays online, writing a book called "Hackers & Painters," working on spam filters, doing some painting, and hosting dinners for friends. They also discussed ideas about venture capital and how it could be improved.
Current response: The author grew up in a small town, where they mainly worked on writing and programming outside of school. They wrote short stories and tried programming on the IBM 1401 using an early version of Fortran and later went on to attend college, majoring in computer science and English literature. After college, they wrote essays on various topics, worked on spam filters, did some painting, and hosted dinners for friends. They also bought a building in Cambridge to use as an office. Later, the author applied to art schools, got accepted into RISD, and attended their foundation classes. They also received an invitation to take the entrance exam at the Accademia di Belli Arti in Florence. During their time at RISD and the Accademia di Belli Arti, the author honed their artistic skills and further developed their writing, eventually transitioning into a successful career as an author and artist. The author achieved several things in their career, including publishing essays online, writing a book called "Hackers & Painters," working on spam filters, doing some painting, and hosting dinners for friends. They also discussed ideas about venture capital and how it could be improved.
Lookahead response: done

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The author grew up in a small town, where they mainly worked on writing and programming outside of school. They wrote short stories and tried programming on the IBM 1401 using an early version of Fortran and later went on to attend college, majoring in computer science and English literature. After college, they wrote essays on various topics, worked on spam filters, did some painting, and hosted dinners for friends. They also bought a building in Cambridge to use as an office. Later, the author applied to art schools, got accepted into RISD, and attended their foundation classes. They also received an invitation to take the entrance exam at the Accademia di Belli Arti in Florence. During their time at RISD and the Accademia di Belli Arti, the author honed their artistic skills and further developed their writing, eventually transitioning into a successful career as an author and artist. The author achieved several things in their career, including publishing essays online, writing a book called "Hackers & Painters," working on spam filters, doing some painting, and hosting dinners for friends. They also discussed ideas about venture capital and how it could be improved. 

```

In [ ]:
Copied!
```
response = index_query_engine.query(
    "Can you tell me about the author's trajectory in the startup world?"
)

```

response = index_query_engine.query( "Can you tell me about the author's trajectory in the startup world?" )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The author's trajectory in the startup world began with their involvement in various projects and activities, such as writing essays on different topics, working on spam filters, and painting. They also hosted dinners for friends, which helped them learn how to cook for groups and network with people from various backgrounds.

In October 2003, the author met Jessica Livingston at a party, who later became a significant figure in their startup journey. Jessica worked in marketing at a Boston investment bank and was intrigued by the stories of startup founders she met through the author. She decided to compile a book of interviews with these founders.

In early 2005, Jessica interviewed for a marketing job at a Boston VC firm, which led the author to discuss the issues with venture capital and how it could be improved. The author also gave a talk at the Harvard Computer Society about starting a startup, which made them realize they should start angel investing.

On March 11, the author, Jessica, and their friends Robert and Trevor decided to start their own investment firm, implementing the ideas they had discussed. They founded Y Combinator, an angel investment firm that made unconventional choices in the startup world. The author's trajectory in the startup world has been marked by their involvement in various projects, networking, and eventually co-founding a successful investment firm.

```

In [ ]:
Copied!
```
response = index_query_engine.query(
    "Tell me about the author's life from childhood to adulthood"
)

```

response = index_query_engine.query( "Tell me about the author's life from childhood to adulthood" )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The author's life from childhood to adulthood includes a variety of experiences and interests. They wrote numerous essays on various topics, which were later compiled into a book called Hackers & Painters. They also worked on spam filters and pursued painting as a hobby. The author used to host dinners for friends every Thursday night, which taught them how to cook for groups. They bought a building in Cambridge, which was a former candy factory and later a porn studio, to use as an office.

In October 2003, the author met Jessica Livingston at a party, and they started dating a few days later. Jessica worked in marketing at a Boston investment bank and later decided to compile a book of interviews with startup founders. When she was looking for a new job, the author shared their thoughts on how venture capital should be improved.

The author also attended the Accademia, a prestigious institution, to study painting. However, they were disappointed with the lack of teaching and learning taking place there. The author painted still lives in their bedroom at night, using leftover scraps of canvas.

```

