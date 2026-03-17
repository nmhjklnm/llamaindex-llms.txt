![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# LongContextReorder¶
Models struggle to access significant details found in the center of extended contexts. A study observed that the best performance typically arises when crucial data is positioned at the start or conclusion of the input context. Additionally, as the input context lengthens, performance drops notably, even in models designed for long contexts.
This module will re-order the retrieved nodes, which can be helpful in cases where a large top-k is needed. The reordering process works as follows:
  1. Input nodes are sorted based on their relevance scores.
  2. Sorted nodes are then reordered in an alternating pattern:
     * Even-indexed nodes are placed at the beginning of the new list.
     * Odd-indexed nodes are placed at the end of the new list.


This approach ensures that the highest-scored (most relevant) nodes are positioned at the beginning and end of the list, with lower-scored nodes in the middle.
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-huggingface
%pip install llama-index-llms-openai

```

%pip install llama-index-embeddings-huggingface %pip install llama-index-llms-openai
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

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os import openai os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

```

from llama_index.embeddings.huggingface import HuggingFaceEmbedding from llama_index.llms.openai import OpenAI from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1) Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
```
/home/loganm/miniconda3/envs/llama-index/lib/python3.11/site-packages/torch/cuda/__init__.py:546: UserWarning: Can't initialize NVML
  warnings.warn("Can't initialize NVML")

```

Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents)
## Run Query¶
In [ ]:
Copied!
```
from llama_index.core.postprocessor import LongContextReorder

reorder = LongContextReorder()

reorder_engine = index.as_query_engine(
    node_postprocessors=[reorder], similarity_top_k=5
)
base_engine = index.as_query_engine(similarity_top_k=5)

```

from llama_index.core.postprocessor import LongContextReorder reorder = LongContextReorder() reorder_engine = index.as_query_engine( node_postprocessors=[reorder], similarity_top_k=5 ) base_engine = index.as_query_engine(similarity_top_k=5)
In [ ]:
Copied!
```
from llama_index.core.response.notebook_utils import display_response

base_response = base_engine.query("Did the author meet Sam Altman?")
display_response(base_response)

```

from llama_index.core.response.notebook_utils import display_response base_response = base_engine.query("Did the author meet Sam Altman?") display_response(base_response)
**`Final Response:`**Yes, the author met Sam Altman when they asked him to be the president of Y Combinator. This was during the time when the author was in a PhD program in computer science and also pursuing their passion for art. They were applying to art schools and eventually ended up attending RISD.
In [ ]:
Copied!
```
reorder_response = reorder_engine.query("Did the author meet Sam Altman?")
display_response(reorder_response)

```

reorder_response = reorder_engine.query("Did the author meet Sam Altman?") display_response(reorder_response)
**`Final Response:`**Yes, the author met Sam Altman when they asked him to be the president of Y Combinator. This meeting occurred at a party at the author's house, where they were introduced by a mutual friend, Jessica Livingston. Jessica later went on to compile a book of interviews with startup founders, and the author shared their thoughts on the flaws of venture capital with her during her job search at a Boston VC firm.
## Inspect Order Diffrences¶
In [ ]:
Copied!
```
print(base_response.get_formatted_sources())

```

print(base_response.get_formatted_sources())
```
> Source (Doc id: 81bc66bb-2c45-4697-9f08-9f848bd78b12): [17]

As well as HN, I wrote all of YC's internal software in Arc. But while I continued to work ...

> Source (Doc id: bd660905-e4e0-4d02-a113-e3810b59c5d1): [19] One way to get more precise about the concept of invented vs discovered is to talk about spa...

> Source (Doc id: 3932e4a4-f17e-4dd2-9d25-5f0e65910dc5): Not so much because it was badly written as because the problem is so convoluted. When you're wor...

> Source (Doc id: 0d801f0a-4a99-475d-aa7c-ad5d601947ea): [10]

Wow, I thought, there's an audience. If I write something and put it on the web, anyone can...

> Source (Doc id: bf726802-4d0d-4ee5-ab2e-ffa8a5461bc4): I was briefly tempted, but they were so slow by present standards; what was the point? No one els...

```

In [ ]:
Copied!
```
print(reorder_response.get_formatted_sources())

```

print(reorder_response.get_formatted_sources())
```
> Source (Doc id: 81bc66bb-2c45-4697-9f08-9f848bd78b12): [17]

As well as HN, I wrote all of YC's internal software in Arc. But while I continued to work ...

> Source (Doc id: 3932e4a4-f17e-4dd2-9d25-5f0e65910dc5): Not so much because it was badly written as because the problem is so convoluted. When you're wor...

> Source (Doc id: bf726802-4d0d-4ee5-ab2e-ffa8a5461bc4): I was briefly tempted, but they were so slow by present standards; what was the point? No one els...

> Source (Doc id: 0d801f0a-4a99-475d-aa7c-ad5d601947ea): [10]

Wow, I thought, there's an audience. If I write something and put it on the web, anyone can...

> Source (Doc id: bd660905-e4e0-4d02-a113-e3810b59c5d1): [19] One way to get more precise about the concept of invented vs discovered is to talk about spa...

```

