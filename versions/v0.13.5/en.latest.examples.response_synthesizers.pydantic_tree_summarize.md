![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Pydantic Tree Summarize¶
In this notebook, we demonstrate how to use tree summarize with structured outputs. Specifically, tree summarize is used to output pydantic objects.
In [ ]:
Copied!
```
import os
import openai

os.environ["OPENAI_API_KEY"] = "sk-..."
openai.api_key = os.environ["OPENAI_API_KEY"]

```

import os import openai os.environ["OPENAI_API_KEY"] = "sk-..." openai.api_key = os.environ["OPENAI_API_KEY"]
# Download Data¶
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
from llama_index.core.types import BaseModel
from typing import List

```

from llama_index.core.response_synthesizers import TreeSummarize from llama_index.core.types import BaseModel from typing import List
### Create pydantic model to structure response¶
In [ ]:
Copied!
```
class Biography(BaseModel):
    """Data model for a biography."""

    name: str
    best_known_for: List[str]
    extra_info: str

```

class Biography(BaseModel): """Data model for a biography.""" name: str best_known_for: List[str] extra_info: str
In [ ]:
Copied!
```
summarizer = TreeSummarize(verbose=True, output_cls=Biography)

```

summarizer = TreeSummarize(verbose=True, output_cls=Biography)
In [ ]:
Copied!
```
response = summarizer.get_response("who is Paul Graham?", [text])

```

response = summarizer.get_response("who is Paul Graham?", [text])
```
5 text chunks after repacking
1 text chunks after repacking

```

### Inspect the response¶
Here, we see the response is in an instance of our `Biography` class.
In [ ]:
Copied!
```
print(response)

```

print(response)
```
name='Paul Graham' best_known_for=['Writing', 'Programming', 'Art', 'Co-founding Viaweb', 'Co-founding Y Combinator', 'Essayist'] extra_info="Paul Graham is a multi-talented individual who has made significant contributions in various fields. He is known for his work in writing, programming, art, co-founding Viaweb, co-founding Y Combinator, and his essays on startups and programming. He started his career by writing short stories and programming on the IBM 1401 computer. He later became interested in artificial intelligence and Lisp programming. He wrote a book called 'On Lisp' and focused on Lisp hacking. Eventually, he decided to pursue art and attended art school. He is known for his paintings, particularly still life paintings. Graham is also a programmer, entrepreneur, and venture capitalist. He co-founded Viaweb, an early e-commerce platform, and Y Combinator, a startup accelerator. He has written influential essays on startups and programming. Additionally, he has made contributions to the field of computer programming and entrepreneurship."

```

In [ ]:
Copied!
```
print(response.name)

```

print(response.name)
```
Paul Graham

```

In [ ]:
Copied!
```
print(response.best_known_for)

```

print(response.best_known_for)
```
['Writing', 'Programming', 'Art', 'Co-founding Viaweb', 'Co-founding Y Combinator', 'Essayist']

```

In [ ]:
Copied!
```
print(response.extra_info)

```

print(response.extra_info)
```
Paul Graham is a multi-talented individual who has made significant contributions in various fields. He is known for his work in writing, programming, art, co-founding Viaweb, co-founding Y Combinator, and his essays on startups and programming. He started his career by writing short stories and programming on the IBM 1401 computer. He later became interested in artificial intelligence and Lisp programming. He wrote a book called 'On Lisp' and focused on Lisp hacking. Eventually, he decided to pursue art and attended art school. He is known for his paintings, particularly still life paintings. Graham is also a programmer, entrepreneur, and venture capitalist. He co-founded Viaweb, an early e-commerce platform, and Y Combinator, a startup accelerator. He has written influential essays on startups and programming. Additionally, he has made contributions to the field of computer programming and entrepreneurship.

```

