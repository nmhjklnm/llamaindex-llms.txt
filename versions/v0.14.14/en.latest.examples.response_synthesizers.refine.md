![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Refine¶
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
### Download Data¶
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
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo")

```

from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo")
In [ ]:
Copied!
```
from llama_index.core.response_synthesizers import Refine

summarizer = Refine(llm=llm, verbose=True)

```

from llama_index.core.response_synthesizers import Refine summarizer = Refine(llm=llm, verbose=True)
In [ ]:
Copied!
```
response = summarizer.get_response("who is Paul Graham?", [text])

```

response = summarizer.get_response("who is Paul Graham?", [text])
```
> Refine context: making fakes for a local antique dealer. She'd ...
> Refine context: look legit, and the key to looking legit is hig...
> Refine context: me 8 years to realize it. Even then it took me ...
> Refine context: was one thing rarer than Rtm offering advice, i...

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Paul Graham is an individual who has played a crucial role in shaping the internet infrastructure and has also pursued a career as a writer. At one point, he received advice from a friend that urged him not to let Y Combinator be his final noteworthy achievement. This advice prompted him to reflect on his future with Y Combinator and ultimately led him to pass on the responsibility to others. He approached Jessica and Sam Altman to assume leadership positions in Y Combinator, aiming to secure its continued success.

```

