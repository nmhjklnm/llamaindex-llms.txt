![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Make Reader¶
We show how LlamaIndex can fit with your Make.com workflow by sending the GPT Index response to a scenario webhook.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-make-com

```

%pip install llama-index-readers-make-com
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
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.readers.make_com import MakeWrapper

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.readers.make_com import MakeWrapper
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
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
index = VectorStoreIndex.from_documents(documents=documents)

```

documents = SimpleDirectoryReader("./data/paul_graham/").load_data() index = VectorStoreIndex.from_documents(documents=documents)
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
# query index
query_str = "What did the author do growing up?"
query_engine = index.as_query_engine()
response = query_engine.query(query_str)

```

# set Logging to DEBUG for more detailed outputs # query index query_str = "What did the author do growing up?" query_engine = index.as_query_engine() response = query_engine.query(query_str)
In [ ]:
Copied!
```
# Send response to Make.com webhook
wrapper = MakeWrapper()
wrapper.pass_response_to_webhook("<webhook_url>", response, query_str)

```

# Send response to Make.com webhook wrapper = MakeWrapper() wrapper.pass_response_to_webhook("", response, query_str)
