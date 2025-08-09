![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Twitter Reader¶
In [ ]:
Copied!
```
%pip install llama-index-readers-twitter

```

%pip install llama-index-readers-twitter
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
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
from llama_index.core import VectorStoreIndex
from llama_index.readers.twitter import TwitterTweetReader
from IPython.display import Markdown, display
import os

```

from llama_index.core import VectorStoreIndex from llama_index.readers.twitter import TwitterTweetReader from IPython.display import Markdown, display import os
In [ ]:
Copied!
```
# create an app in https://developer.twitter.com/en/apps
BEARER_TOKEN = "<bearer_token>"

```

# create an app in https://developer.twitter.com/en/apps BEARER_TOKEN = ""
In [ ]:
Copied!
```
# create reader, specify twitter handles
reader = TwitterTweetReader(BEARER_TOKEN)
documents = reader.load_data(["@twitter_handle1"])

```

# create reader, specify twitter handles reader = TwitterTweetReader(BEARER_TOKEN) documents = reader.load_data(["@twitter_handle1"])
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("<query_text>")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
