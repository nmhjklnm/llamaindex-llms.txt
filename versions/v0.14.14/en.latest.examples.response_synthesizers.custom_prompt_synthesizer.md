![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Pydantic Tree Summarize¶
In this notebook, we demonstrate how to use tree summarize with structured outputs. Specifically, tree summarize is used to output pydantic objects.
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
import os
import openai

```

import os import openai
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "sk-..."
openai.api_key = os.environ["OPENAI_API_KEY"]

```

os.environ["OPENAI_API_KEY"] = "sk-..." openai.api_key = os.environ["OPENAI_API_KEY"]
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
## Define Custom Prompt¶
In [ ]:
Copied!
```
from llama_index.core import PromptTemplate

```

from llama_index.core import PromptTemplate
In [ ]:
Copied!
```
# NOTE: we add an extra tone_name variable here
qa_prompt_tmpl = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query.\n"
    "Please also write the answer in the style of {tone_name}.\n"
    "Query: {query_str}\n"
    "Answer: "
)
qa_prompt = PromptTemplate(qa_prompt_tmpl)

refine_prompt_tmpl = (
    "The original query is as follows: {query_str}\n"
    "We have provided an existing answer: {existing_answer}\n"
    "We have the opportunity to refine the existing answer "
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{context_msg}\n"
    "------------\n"
    "Given the new context, refine the original answer to better "
    "answer the query. "
    "Please also write the answer in the style of {tone_name}.\n"
    "If the context isn't useful, return the original answer.\n"
    "Refined Answer: "
)
refine_prompt = PromptTemplate(refine_prompt_tmpl)

```

# NOTE: we add an extra tone_name variable here qa_prompt_tmpl = ( "Context information is below.\n" "---------------------\n" "{context_str}\n" "---------------------\n" "Given the context information and not prior knowledge, " "answer the query.\n" "Please also write the answer in the style of {tone_name}.\n" "Query: {query_str}\n" "Answer: " ) qa_prompt = PromptTemplate(qa_prompt_tmpl) refine_prompt_tmpl = ( "The original query is as follows: {query_str}\n" "We have provided an existing answer: {existing_answer}\n" "We have the opportunity to refine the existing answer " "(only if needed) with some more context below.\n" "------------\n" "{context_msg}\n" "------------\n" "Given the new context, refine the original answer to better " "answer the query. " "Please also write the answer in the style of {tone_name}.\n" "If the context isn't useful, return the original answer.\n" "Refined Answer: " ) refine_prompt = PromptTemplate(refine_prompt_tmpl)
## Try out Response Synthesis with Custom Prompt¶
We try out a few different response synthesis strategies with the custom prompt.
In [ ]:
Copied!
```
from llama_index.core.response_synthesizers import TreeSummarize, Refine
from llama_index.core.types import BaseModel
from typing import List

```

from llama_index.core.response_synthesizers import TreeSummarize, Refine from llama_index.core.types import BaseModel from typing import List
In [ ]:
Copied!
```
summarizer = TreeSummarize(verbose=True, summary_template=qa_prompt)

```

summarizer = TreeSummarize(verbose=True, summary_template=qa_prompt)
In [ ]:
Copied!
```
response = summarizer.get_response(
    "who is Paul Graham?", [text], tone_name="a Shakespeare play"
)

```

response = summarizer.get_response( "who is Paul Graham?", [text], tone_name="a Shakespeare play" )
```
5 text chunks after repacking
1 text chunks after repacking

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Paul Graham, a noble and esteemed gentleman, is a man of many talents and accomplishments. He hath traversed the realms of art, entrepreneurship, and writing, leaving a lasting impact on each. With his brush, he hath brought life to canvases, capturing the essence of what he saw. In the realm of technology, he hath revolutionized the way we do business, founding Viaweb and bringing the power of the web to entrepreneurs and artists alike. His wisdom and guidance hath shaped the future of technology and entrepreneurship through his co-founding of Y Combinator. But above all, Paul Graham is a visionary, a trailblazer, and a true Renaissance man, whose intellectual curiosity and quest for lasting creation hath inspired generations to come.

```

In [ ]:
Copied!
```
summarizer = Refine(
    verbose=True, text_qa_template=qa_prompt, refine_template=refine_prompt
)

```

summarizer = Refine( verbose=True, text_qa_template=qa_prompt, refine_template=refine_prompt )
In [ ]:
Copied!
```
response = summarizer.get_response(
    "who is Paul Graham?", [text], tone_name="a haiku"
)

```

response = summarizer.get_response( "who is Paul Graham?", [text], tone_name="a haiku" )
```
> Refine context: made a living from a combination of modelling a...
> Refine context: to have studied art, because the main goal of a...
> Refine context: I had been intimately involved with building th...
> Refine context: I didn't understand what he meant, but graduall...

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Paul Graham, a web pioneer,
Co-founded Y Combinator,
But stepped down to ensure,
Long-term success and more.

```

In [ ]:
Copied!
```
# try with pydantic model
class Biography(BaseModel):
    """Data model for a biography."""

    name: str
    best_known_for: List[str]
    extra_info: str

```

# try with pydantic model class Biography(BaseModel): """Data model for a biography.""" name: str best_known_for: List[str] extra_info: str
In [ ]:
Copied!
```
summarizer = TreeSummarize(
    verbose=True, summary_template=qa_prompt, output_cls=Biography
)

```

summarizer = TreeSummarize( verbose=True, summary_template=qa_prompt, output_cls=Biography )
In [ ]:
Copied!
```
response = summarizer.get_response(
    "who is Paul Graham?", [text], tone_name="a business memo"
)

```

response = summarizer.get_response( "who is Paul Graham?", [text], tone_name="a business memo" )
```
5 text chunks after repacking
1 text chunks after repacking

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
name='Paul Graham' best_known_for=['Co-founder of Y Combinator', 'Writer', 'Investor'] extra_info="Paul Graham is a renowned entrepreneur, writer, and investor. He is best known as the co-founder of Y Combinator, a highly successful startup accelerator. Graham has played a significant role in shaping the startup ecosystem and has been instrumental in the success of numerous startups. He is also a prolific writer, known for his insightful essays on a wide range of topics, including technology, startups, and entrepreneurship. Graham's writings have been widely read and have had a profound impact on the tech community. In addition to his work with Y Combinator and his writing, Graham is also an active investor, providing seed funding and mentorship to early-stage startups. His contributions to the startup world have earned him a reputation as one of the most influential figures in the industry."

```

