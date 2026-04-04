![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# AIMon Rerank¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙
In [ ]:
Copied!
```
%%capture
!pip install llama-index
!pip install llama-index-postprocessor-aimon-rerank

```

%%capture !pip install llama-index !pip install llama-index-postprocessor-aimon-rerank
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.response.pprint_utils import pprint_response

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.response.pprint_utils import pprint_response
An OpenAI and AIMon API key is required for this notebook. Import the AIMon and OpenAI API keys from Colab Secrets
In [ ]:
Copied!
```
import os

# Import Colab Secrets userdata module.
from google.colab import userdata

os.environ["AIMON_API_KEY"] = userdata.get("AIMON_API_KEY")
os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")

```

import os # Import Colab Secrets userdata module. from google.colab import userdata os.environ["AIMON_API_KEY"] = userdata.get("AIMON_API_KEY") os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
Download data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2025-03-10 18:01:07--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.108.133, 185.199.111.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.108.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.03s   

2025-03-10 18:01:08 (2.59 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

Generate documents and build an index
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

# build index
index = VectorStoreIndex.from_documents(documents=documents)

```

# load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data() # build index index = VectorStoreIndex.from_documents(documents=documents)
Define a task definition for the AIMon reranker and instantiate an instance of the AIMonRerank class. The task definition serves as an explicit instruction to the system, defining what the reranking evaluation should focus on.
In [ ]:
Copied!
```
import os
from llama_index.postprocessor.aimon_rerank import AIMonRerank

task_definition = "Your task is to assess the actions of an individual specified in the user query against the context documents supplied."

aimon_rerank = AIMonRerank(
    top_n=2,
    api_key=userdata.get("AIMON_API_KEY"),
    task_definition=task_definition,
)

```

import os from llama_index.postprocessor.aimon_rerank import AIMonRerank task_definition = "Your task is to assess the actions of an individual specified in the user query against the context documents supplied." aimon_rerank = AIMonRerank( top_n=2, api_key=userdata.get("AIMON_API_KEY"), task_definition=task_definition, )
#### Directly retrieve top 2 most similar nodes (i.e., without using a reranker)¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(similarity_top_k=2)
response = query_engine.query("What did Sam Altman do in this essay?")

```

query_engine = index.as_query_engine(similarity_top_k=2) response = query_engine.query("What did Sam Altman do in this essay?")
In [ ]:
Copied!
```
pprint_response(response, show_source=True)

```

pprint_response(response, show_source=True)
```
Final Response: Sam Altman was asked to become the president of Y
Combinator, initially declined the offer to pursue starting a startup
focused on nuclear reactors, but eventually agreed to take over
starting with the winter 2014 batch.
______________________________________________________________________
Source Node 1/2
Node ID: 2940ea4a-69ec-4fc4-9dd4-8ed54a9d4f1b
Similarity: 0.8305926707169754
Text: When I was dealing with some urgent problem during YC, there was
about a 60% chance it had to do with HN, and a 40% chance it had do
with everything else combined. [17]  As well as HN, I wrote all of
YC's internal software in Arc. But while I continued to work a good
deal in Arc, I gradually stopped working on Arc, partly because I
didn't have t...
______________________________________________________________________
Source Node 2/2
Node ID: 2f043635-e4ce-4054-92f3-b624fd90ae04
Similarity: 0.8239262662012308
Text: Up till that point YC had been controlled by the original LLC we
four had started. But we wanted YC to last for a long time, and to do
that it couldn't be controlled by the founders. So if Sam said yes,
we'd let him reorganize YC. Robert and I would retire, and Jessica and
Trevor would become ordinary partners.  When we asked Sam if he wanted
to...

```

#### Retrieve top 10 most relevant nodes, but then rerank with AIMon Reranker¶
![Diagram depicting working of AIMon reranker](https://raw.githubusercontent.com/devvratbhardwaj/images/refs/heads/main/AIMon_Reranker.svg)
Explanation of the reranking process:
The diagram illustrates how a reranker refines document retrieval for a more accurate response.
  1. **Initial Retrieval (Vector DB)** :
     * A query is sent to the vector database.
     * The system retrieves the **top 10 most relevant records** based on similarity scores (`top_k = 10`).
  2. **Reranking with AIMon** :
     * Instead of using only the highest-scoring records directly, these 10 records are reranked using the **AIMon Reranker**.
     * The reranker evaluates the documents based on their actual relevance to the query, rather than just raw similarity scores.
     * During this step, a **task definition** is applied, serving as an explicit instruction that defines what the reranking evaluation should focus on.
     * This ensures that the selected records are not just statistically similar but also **contextually relevant** to the intended task.
  3. **Final Selection (`top_n = 2`)**:
     * After reranking, the system selects the **top 2 most contextually relevant records** for response generation.
     * The **task definition ensures** that these records align with the query’s intent, leading to a **more precise and informative response**.


In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=10, node_postprocessors=[aimon_rerank]
)
response = query_engine.query("What did Sam Altman do in this essay?")

```

query_engine = index.as_query_engine( similarity_top_k=10, node_postprocessors=[aimon_rerank] ) response = query_engine.query("What did Sam Altman do in this essay?")
```
Total number of batches formed: 1
Processing batch 1/1 with 10 context documents.
Finished processing. Total batches sent to AIMon reranker: 1
Top 2 nodes selected after reranking.

```

In [ ]:
Copied!
```
pprint_response(response, show_source=True)

```

pprint_response(response, show_source=True)
```
Final Response: Sam Altman was asked to become the president of Y
Combinator, initially declined the offer to pursue starting a startup
focused on nuclear reactors, but eventually agreed to take over as
president starting with the winter 2014 batch.
______________________________________________________________________
Source Node 1/2
Node ID: 2940ea4a-69ec-4fc4-9dd4-8ed54a9d4f1b
Similarity: 0.48260445005911023
Text: When I was dealing with some urgent problem during YC, there was
about a 60% chance it had to do with HN, and a 40% chance it had do
with everything else combined. [17]  As well as HN, I wrote all of
YC's internal software in Arc. But while I continued to work a good
deal in Arc, I gradually stopped working on Arc, partly because I
didn't have t...
______________________________________________________________________
Source Node 2/2
Node ID: 0baaf5af-6e6b-4889-8407-e49d1753980c
Similarity: 0.48151918284717965
Text: As Jessica and I were walking home from dinner on March 11, at
the corner of Garden and Walker streets, these three threads
converged. Screw the VCs who were taking so long to make up their
minds. We'd start our own investment firm and actually implement the
ideas we'd been talking about. I'd fund it, and Jessica could quit her
job and work for ...

```

#### Conclusion¶
The AIMon reranker, using task definition, shifted retrieval focus from general YC leadership changes to Sam Altman’s specific actions. Initially, high-similarity documents lacked his decision-making details. After reranking, lower-similarity but contextually relevant documents highlighted his reluctance and timeline, ensuring a more accurate, task-aligned response over purely similarity-based retrieval.
