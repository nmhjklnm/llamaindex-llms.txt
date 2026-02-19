![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Aim Callback¶
Aim is an easy-to-use & supercharged open-source AI metadata tracker it logs all your AI metadata (experiments, prompts, etc) enables a UI to compare & observe them and SDK to query them programmatically. For more please see the Github page.
In this demo, we show the capabilities of Aim for logging events while running queries within LlamaIndex. We use the AimCallback to store the outputs and showing how to explore them using Aim Text Explorer.
**NOTE** : This is a beta feature. The usage within different classes and the API interface for the CallbackManager and AimCallback may change!
## Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-callbacks-aim

```

%pip install llama-index-callbacks-aim
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.core.callbacks import CallbackManager
from llama_index.callbacks.aim import AimCallback
from llama_index.core import SummaryIndex
from llama_index.core import SimpleDirectoryReader

```

from llama_index.core.callbacks import CallbackManager from llama_index.callbacks.aim import AimCallback from llama_index.core import SummaryIndex from llama_index.core import SimpleDirectoryReader
Let's read the documents using `SimpleDirectoryReader` from 'examples/data/paul_graham'.
#### Download Data¶
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
docs = SimpleDirectoryReader("./data/paul_graham").load_data()

```

docs = SimpleDirectoryReader("./data/paul_graham").load_data()
Now lets initialize an AimCallback instance, and add it to the list of callback managers.
In [ ]:
Copied!
```
aim_callback = AimCallback(repo="./")
callback_manager = CallbackManager([aim_callback])

```

aim_callback = AimCallback(repo="./") callback_manager = CallbackManager([aim_callback])
In this snippet, we initialize a callback manager. Next, we create an instance of `SummaryIndex` class, by passing in the document reader and callback. After which we create a query engine which we will use to run queries on the index and retrieve relevant results.
In [ ]:
Copied!
```
index = SummaryIndex.from_documents(docs, callback_manager=callback_manager)
query_engine = index.as_query_engine()

```

index = SummaryIndex.from_documents(docs, callback_manager=callback_manager) query_engine = index.as_query_engine()
Finally let's ask a question to the LM based on our provided document
In [ ]:
Copied!
```
response = query_engine.query("What did the author do growing up?")

```

response = query_engine.query("What did the author do growing up?")
The callback manager will log the `CBEventType.LLM` type of events as an Aim.Text, and we can explore the LM given prompt and the output in the Text Explorer. By first doing `aim up` and navigating by the given url.
