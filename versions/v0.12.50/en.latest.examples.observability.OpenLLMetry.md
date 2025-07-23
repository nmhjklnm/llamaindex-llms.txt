![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Observability with OpenLLMetry¶
OpenLLMetry is an open-source project based on OpenTelemetry for tracing and monitoring LLM applications. It connects to all major observability platforms (like Datadog, Dynatrace, Honeycomb, New Relic and others) and installs in minutes.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙 and OpenLLMetry.
In [ ]:
Copied!
```
!pip install llama-index
!pip install traceloop-sdk

```

!pip install llama-index !pip install traceloop-sdk
## Configure API keys¶
Sign-up to Traceloop at app.traceloop.com. Then, go to the API keys page and create a new API key. Copy the key and paste it in the cell below.
If you prefer to use a different observability platform like Datadog, Dynatrace, Honeycomb or others, you can find instructions on how to configure it here.
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."
os.environ["TRACELOOP_API_KEY"] = "..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..." os.environ["TRACELOOP_API_KEY"] = "..."
## Initialize OpenLLMetry¶
In [ ]:
Copied!
```
from traceloop.sdk import Traceloop

Traceloop.init()

```

from traceloop.sdk import Traceloop Traceloop.init()
```
Traceloop syncing configuration and prompts
Traceloop exporting traces to https://api.traceloop.com authenticating with bearer token


```

## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-01-12 12:43:16--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.109.133, 185.199.108.133, 185.199.111.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.109.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.02s   

2024-01-12 12:43:17 (3.68 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

docs = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

from llama_index.core import SimpleDirectoryReader docs = SimpleDirectoryReader("./data/paul_graham/").load_data()
## Run a query¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(docs)
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
print(response)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(docs) query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?") print(response)
```
The author wrote short stories and also worked on programming, specifically on an IBM 1401 computer in 9th grade. They used an early version of Fortran and typed programs on punch cards. They also mentioned getting a microcomputer, a TRS-80, in about 1980 and started programming on it.

```

## Go to Traceloop or your favorite platform to view the results¶
![Traceloop](https://docs.llamaindex.ai/en/stable/_images/openllmetry.png)
