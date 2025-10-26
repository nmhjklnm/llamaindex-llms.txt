![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Trustworthy RAG with the Trustworthy Language Model¶
This tutorial demonstrates how to use Cleanlab's Trustworthy Language Model (TLM) in any RAG system, to score the trustworthiness of answers and **automatically catch incorrect/hallucinated responses in real-time**.
Today's RAG and Agent applications often produce unreliable responses, because they depend on LLMs which are fundamentally unreliable. Cleanlab’s Trustworthy Language Model scores the trustworthiness of every LLM response in real-time, using state-of-the-art uncertainty estimates for LLMs. Cleanlab works effectively **no matter your RAG architecture or retrieval and indexing processes**.
To diagnose when RAG answers cannot be trusted, this tutorial demonstrates how to replace your LLM with Cleanlab's to generate responses and score their trustworthiness. You can alternatively use Cleanlab only to score responses from your unmodified RAG system and run other real-time Evals, see our Evaluation tutorial.
## Setup¶
RAG is all about connecting LLMs to data, to better inform their answers. This tutorial uses Nvidia's Q1 FY2024 earnings report as an example dataset. Use the following commands to download the data (earnings report) and store it in a directory named `data/`.
In [ ]:
Copied!
```
!wget -nc 'https://cleanlab-public.s3.amazonaws.com/Datasets/NVIDIA_Financial_Results_Q1_FY2024.md'
!mkdir -p ./data
!mv NVIDIA_Financial_Results_Q1_FY2024.md data/

```

!wget -nc 'https://cleanlab-public.s3.amazonaws.com/Datasets/NVIDIA_Financial_Results_Q1_FY2024.md' !mkdir -p ./data !mv NVIDIA_Financial_Results_Q1_FY2024.md data/
Now let's install the required dependencies.
In [ ]:
Copied!
```
%pip install llama-index-llms-cleanlab llama-index llama-index-embeddings-huggingface

```

%pip install llama-index-llms-cleanlab llama-index llama-index-embeddings-huggingface
We then initialize Cleanlab's TLM. Here we initialize a CleanlabTLM object with default settings.
In [ ]:
Copied!
```
from llama_index.llms.cleanlab import CleanlabTLM

# set api key in env or in llm
# get free API key from: https://cleanlab.ai/
# import os
# os.environ["CLEANLAB_API_KEY"] = "your api key"

llm = CleanlabTLM(api_key="your_api_key")

```

from llama_index.llms.cleanlab import CleanlabTLM # set api key in env or in llm # get free API key from: https://cleanlab.ai/ # import os # os.environ["CLEANLAB_API_KEY"] = "your api key" llm = CleanlabTLM(api_key="your_api_key")
Note: If you encounter `ValidationError` during the above import, please upgrade your python version to >= 3.11
You can achieve better results by playing with the TLM configurations outlined in this advanced TLM tutorial.
For example, if your application requires OpenAI's GPT-4 model and restrict the output tokens to 256, you can configure it using the `options` argument:
```
options = {
    "model": "gpt-4",
    "max_tokens": 256,
}
llm = CleanlabTLM(api_key="your_api_key", options=options)

```

Let's start by asking the LLM a simple question.
In [ ]:
Copied!
```
response = llm.complete("What is NVIDIA's ticker symbol?")
print(response)

```

response = llm.complete("What is NVIDIA's ticker symbol?") print(response)
```
NVIDIA's ticker symbol is NVDA.

```

TLM not only provides a response but also includes a **trustworthiness score** indicating the confidence that this response is good/accurate. You can access this score from the response itself.
In [ ]:
Copied!
```
response.additional_kwargs

```

response.additional_kwargs
Out[ ]:
```
{'trustworthiness_score': 0.9884868983475051}
```

## Build a RAG pipeline with TLM¶
Now let's integrate TLM into a RAG pipeline.
In [ ]:
Copied!
```
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

Settings.llm = llm

```

from llama_index.core import Settings from llama_index.embeddings.huggingface import HuggingFaceEmbedding from llama_index.core import VectorStoreIndex, SimpleDirectoryReader Settings.llm = llm
### Specify Embedding Model¶
RAG uses an embedding model to match queries against document chunks to retrieve the most relevant data. Here we opt for a no-cost, local embedding model from Hugging Face. You can use any other embedding model by referring to this LlamaIndex guide.
In [ ]:
Copied!
```
Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

```

Settings.embed_model = HuggingFaceEmbedding( model_name="BAAI/bge-small-en-v1.5" )
### Load Data and Create Index + Query Engine¶
Let's create an index from the documents stored in the data directory. The system can index multiple files within the same folder, although for this tutorial, we'll use just one document. We stick with the default index from LlamaIndex for this tutorial.
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("data").load_data()
# Optional step since we're loading just one data file
for doc in documents:
    # file_path wouldn't be a useful metadata to add to LLM's context since our datasource contains just 1 file
    doc.excluded_llm_metadata_keys.append("file_path")
index = VectorStoreIndex.from_documents(documents)

```

documents = SimpleDirectoryReader("data").load_data() # Optional step since we're loading just one data file for doc in documents: # file_path wouldn't be a useful metadata to add to LLM's context since our datasource contains just 1 file doc.excluded_llm_metadata_keys.append("file_path") index = VectorStoreIndex.from_documents(documents)
The generated index is used to power a query engine over the data.
In [ ]:
Copied!
```
query_engine = index.as_query_engine()

```

query_engine = index.as_query_engine()
Note that TLM is agnostic to the index and the query engine used for RAG, and is compatible with any choices you make for these components of your system.
In addition, you can just use TLM's trustworthiness score in an existing custom-built RAG pipeline (using any other LLM generator, streaming or not).   
To achieve this, you'd need to fetch the prompt sent to LLM (including system instructions, retrieved context, user query, etc.) and the returned response. TLM requires both to predict trustworthiness.
Details about this approach and example code are available here.
### Extract Trustworthiness Score from LLM response¶
As we saw earlier, Cleanlab's TLM also provides the `trustworthiness_score` in addition to the text, in its response to the prompt.
To get this score out when TLM is used in a RAG pipeline, Llamaindex provides an instrumentation tool that allows us to observe the events running behind the scenes in RAG.   
We can utilise this tooling to extract `trustworthiness_score` from LLM's response.
Let's define a simple event handler that stores this score for every request sent to the LLM. You can refer to Llamaindex's documentation for more details on instrumentation.
In [ ]:
Copied!
```
from typing import Dict, List, ClassVar
from llama_index.core.instrumentation.events import BaseEvent
from llama_index.core.instrumentation.event_handlers import BaseEventHandler
from llama_index.core.instrumentation import get_dispatcher
from llama_index.core.instrumentation.events.llm import LLMCompletionEndEvent


class GetTrustworthinessScore(BaseEventHandler):
    events: ClassVar[List[BaseEvent]] = []
    trustworthiness_score: float = 0.0

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "GetTrustworthinessScore"

    def handle(self, event: BaseEvent) -> Dict:
        if isinstance(event, LLMCompletionEndEvent):
            self.trustworthiness_score = event.response.additional_kwargs[
                "trustworthiness_score"
            ]
            self.events.append(event)


# Root dispatcher
root_dispatcher = get_dispatcher()

# Register event handler
event_handler = GetTrustworthinessScore()
root_dispatcher.add_event_handler(event_handler)

```

from typing import Dict, List, ClassVar from llama_index.core.instrumentation.events import BaseEvent from llama_index.core.instrumentation.event_handlers import BaseEventHandler from llama_index.core.instrumentation import get_dispatcher from llama_index.core.instrumentation.events.llm import LLMCompletionEndEvent class GetTrustworthinessScore(BaseEventHandler): events: ClassVar[List[BaseEvent]] = [] trustworthiness_score: float = 0.0 @classmethod def class_name(cls) -> str: """Class name.""" return "GetTrustworthinessScore" def handle(self, event: BaseEvent) -> Dict: if isinstance(event, LLMCompletionEndEvent): self.trustworthiness_score = event.response.additional_kwargs[ "trustworthiness_score" ] self.events.append(event) # Root dispatcher root_dispatcher = get_dispatcher() # Register event handler event_handler = GetTrustworthinessScore() root_dispatcher.add_event_handler(event_handler)
For each query, we can fetch this score from `event_handler.trustworthiness_score`. Let's see it in action.
## Answering queries with our RAG system¶
Let's try out our RAG pipeline based on TLM. Here we pose questions with differing levels of complexity.
In [ ]:
Copied!
```
# Optional: Define `display_response` helper function


# This method presents formatted responses from our TLM-based RAG pipeline. It parses the output to display both the text response itself and the corresponding trustworthiness score.
def display_response(response):
    response_str = response.response
    trustworthiness_score = event_handler.trustworthiness_score
    print(f"Response: {response_str}")
    print(f"Trustworthiness score: {round(trustworthiness_score, 2)}")

```

# Optional: Define `display_response` helper function # This method presents formatted responses from our TLM-based RAG pipeline. It parses the output to display both the text response itself and the corresponding trustworthiness score. def display_response(response): response_str = response.response trustworthiness_score = event_handler.trustworthiness_score print(f"Response: {response_str}") print(f"Trustworthiness score: {round(trustworthiness_score, 2)}")
### Easy Questions¶
We first pose straightforward questions that can be directly answered by the provided data and can be easily located within a few lines of text.
In [ ]:
Copied!
```
response = query_engine.query(
    "What was NVIDIA's total revenue in the first quarter of fiscal 2024?"
)
display_response(response)

```

response = query_engine.query( "What was NVIDIA's total revenue in the first quarter of fiscal 2024?" ) display_response(response)
```
Response: NVIDIA's total revenue in the first quarter of fiscal 2024 was $7.19 billion.
Trustworthiness score: 1.0

```

In [ ]:
Copied!
```
response = query_engine.query(
    "What was the GAAP earnings per diluted share for the quarter?"
)
display_response(response)

```

response = query_engine.query( "What was the GAAP earnings per diluted share for the quarter?" ) display_response(response)
```
Response: The GAAP earnings per diluted share for the quarter (Q1 FY24) was $0.82.
Trustworthiness score: 0.99

```

In [ ]:
Copied!
```
response = query_engine.query(
    "What significant transitions did Jensen Huang, NVIDIA's CEO, comment on?"
)
display_response(response)

```

response = query_engine.query( "What significant transitions did Jensen Huang, NVIDIA's CEO, comment on?" ) display_response(response)
```
Response: Jensen Huang, NVIDIA's CEO, commented on the significant transitions the computer industry is undergoing, particularly in the areas of accelerated computing and generative AI.
Trustworthiness score: 0.99

```

TLM returns high trustworthiness scores for these responses, indicating high confidence they are accurate. After doing a quick fact-check (reviewing the original earnings report), we can confirm that TLM indeed accurately answered these questions. In case you're curious, here are relevant excerpts from the data context for these questions:
> NVIDIA (NASDAQ: NVDA) today reported revenue for the first quarter ended April 30, 2023, of $7.19 billion, ...
> GAAP earnings per diluted share for the quarter were $0.82, up 28% from a year ago and up 44% from the previous quarter.
> Jensen Huang, founder and CEO of NVIDIA, commented on the significant transitions the computer industry is undergoing, particularly accelerated computing and generative AI, ...
### Questions without Available Context¶
Now let's see how TLM responds to queries that _cannot_ be answered using the provided data.
In [ ]:
Copied!
```
response = query_engine.query(
    "What factors as per the report were responsible to the decline in NVIDIA's proviz revenue?"
)
display_response(response)

```

response = query_engine.query( "What factors as per the report were responsible to the decline in NVIDIA's proviz revenue?" ) display_response(response)
```
Response: The report indicates that NVIDIA's professional visualization revenue declined by 53% year-over-year. While the specific factors contributing to this decline are not detailed in the provided information, several potential reasons can be inferred:

1. **Market Conditions**: The overall market for professional visualization may have faced challenges, leading to reduced demand for NVIDIA's products in this segment.

2. **Increased Competition**: The presence of competitors in the professional visualization space could have impacted NVIDIA's market share and revenue.

3. **Economic Factors**: Broader economic conditions, such as inflation or reduced spending in industries that utilize professional visualization tools, may have contributed to the decline.

4. **Transition to New Technologies**: The introduction of new technologies, such as the NVIDIA Omniverse™ Cloud, may have shifted focus away from traditional professional visualization products, affecting revenue.

5. **Product Lifecycle**: If certain products were nearing the end of their lifecycle or if there were delays in new product launches, this could have impacted sales.

Overall, while the report does not specify the exact reasons for the decline, these factors could be contributing elements based on industry trends and market dynamics.
Trustworthiness score: 0.76

```

The lower TLM trustworthiness score indicates a bit more uncertainty about the response, which aligns with the lack of information available. Let's try some more questions.
In [ ]:
Copied!
```
response = query_engine.query(
    "How does the report explain why NVIDIA's Gaming revenue decreased year over year?"
)
display_response(response)

```

response = query_engine.query( "How does the report explain why NVIDIA's Gaming revenue decreased year over year?" ) display_response(response)
```
Response: The report does not explicitly explain the reasons for the year-over-year decrease in NVIDIA's Gaming revenue. However, it does provide context regarding the overall performance of the gaming segment, noting that first-quarter revenue was $2.24 billion, which is down 38% from a year ago but up 22% from the previous quarter. This suggests that while there may have been a decline compared to the same period last year, there was a recovery compared to the previous quarter. Factors that could contribute to the year-over-year decline might include market conditions, competition, or changes in consumer demand, but these specifics are not detailed in the report.
Trustworthiness score: 0.92

```

In [ ]:
Copied!
```
response = query_engine.query(
    "How does NVIDIA's dividend payout for this quarter compare to the industry average?",
)
display_response(response)

```

response = query_engine.query( "How does NVIDIA's dividend payout for this quarter compare to the industry average?", ) display_response(response)
```
Response: The context information provided does not include specific details about the industry average for dividend payouts. Therefore, I cannot directly compare NVIDIA's dividend payout for this quarter to the industry average. However, NVIDIA announced a quarterly cash dividend of $0.04 per share for shareholders of record on June 8, 2023. To assess how this compares to the industry average, one would need to look up the average dividend payout for similar companies in the technology or semiconductor industry.
Trustworthiness score: 0.93

```

We observe that TLM demonstrates the ability to recognize the limitations of the available information. It refrains from generating speculative responses or hallucinations, thereby maintaining the reliability of the question-answering system. This behavior showcases an understanding of the boundaries of the context and prioritizes accuracy over conjecture.
### Challenging Questions¶
Let's see how our RAG system responds to harder questions, some of which may be misleading.
In [ ]:
Copied!
```
response = query_engine.query(
    "How much did Nvidia's revenue decrease this quarter vs last quarter, in terms of $?"
)
display_response(response)

```

response = query_engine.query( "How much did Nvidia's revenue decrease this quarter vs last quarter, in terms of $?" ) display_response(response)
```
Response: NVIDIA's revenue for the first quarter of fiscal 2024 was $7.19 billion, and it was reported that this revenue was up 19% from the previous quarter. To find the revenue for the previous quarter, we can use the following calculation:

Let \( x \) be the revenue for the previous quarter. 

The equation based on the 19% increase is:
\[ 
x + 0.19x = 7.19 \text{ billion} 
\]
\[ 
1.19x = 7.19 \text{ billion} 
\]
\[ 
x = \frac{7.19 \text{ billion}}{1.19} \approx 6.04 \text{ billion} 
\]

Now, to find the decrease in revenue from the previous quarter to this quarter:
\[ 
\text{Decrease} = 7.19 \text{ billion} - 6.04 \text{ billion} \approx 1.15 \text{ billion} 
\]

Thus, NVIDIA's revenue decreased by approximately $1.15 billion this quarter compared to the last quarter.
Trustworthiness score: 0.6

```

In [ ]:
Copied!
```
response = query_engine.query(
    "This report focuses on Nvidia's Q1FY2024 financial results. There are mentions of other companies in the report like Microsoft, Dell, ServiceNow, etc. Can you name them all here?",
)
display_response(response)

```

response = query_engine.query( "This report focuses on Nvidia's Q1FY2024 financial results. There are mentions of other companies in the report like Microsoft, Dell, ServiceNow, etc. Can you name them all here?", ) display_response(response)
```
Response: The report mentions the following companies: Microsoft and Dell. ServiceNow is also mentioned in the context, but it is not specified in the provided highlights. Therefore, the companies explicitly mentioned in the report are Microsoft and Dell.
Trustworthiness score: 0.6

```

In [ ]:
Copied!
```
response = query_engine.query(
    "How many RTX GPU models, including all custom versions released by third-party manufacturers and all revisions across different series, were officially announced in NVIDIA's Q1 FY2024 financial results?",
)
display_response(response)

```

response = query_engine.query( "How many RTX GPU models, including all custom versions released by third-party manufacturers and all revisions across different series, were officially announced in NVIDIA's Q1 FY2024 financial results?", ) display_response(response)
```
Response: In NVIDIA's Q1 FY2024 financial results, the following RTX GPU models were officially announced:

1. **GeForce RTX 4060 family of GPUs**
2. **GeForce RTX 4070 GPU**
3. **Six new NVIDIA RTX GPUs for mobile and desktop workstations**

This totals to **eight RTX GPU models** announced.
Trustworthiness score: 0.74

```

In [ ]:
Copied!
```
response = query_engine.query(
    "If NVIDIA's Data Center segment maintains its Q1 FY2024 quarter-over-quarter growth rate for the next four quarters, what would be its projected annual revenue?",
)
display_response(response)

```

response = query_engine.query( "If NVIDIA's Data Center segment maintains its Q1 FY2024 quarter-over-quarter growth rate for the next four quarters, what would be its projected annual revenue?", ) display_response(response)
```
Response: To calculate the projected annual revenue for NVIDIA's Data Center segment if it maintains its Q1 FY2024 quarter-over-quarter growth rate, we first need to determine the growth rate from Q4 FY2023 to Q1 FY2024.

NVIDIA reported a record Data Center revenue of $4.28 billion for Q1 FY2024. The revenue for the previous quarter (Q4 FY2023) can be calculated as follows:

Let \( R \) be the revenue for Q4 FY2023. The growth rate from Q4 FY2023 to Q1 FY2024 is given by:

\[
\text{Growth Rate} = \frac{\text{Q1 Revenue} - \text{Q4 Revenue}}{\text{Q4 Revenue}} = \frac{4.28 - R}{R}
\]

We know that the overall revenue for Q1 FY2024 is $7.19 billion, which is up 19% from the previous quarter. Therefore, we can express the revenue for Q4 FY2023 as:

\[
\text{Q1 FY2024 Revenue} = \text{Q4 FY2023 Revenue} \times 1.19
\]

Substituting the known value:

\[
7.19 = R \times 1.19
\]

Solving for \( R \):

\[
R = \frac{7.19}{1.19} \approx 6.03 \text{ billion}
\]

Now, we can calculate the Data Center revenue for Q4 FY2023. Since we don't have the exact figure for the Data Center revenue in Q4 FY2023, we will assume that the Data Center revenue also grew by the same percentage as the overall revenue. 

Now, we can calculate the quarter-over-quarter growth rate for the Data Center segment:

\[
\text{Growth Rate} = \frac{4.28 - R_D}{R_D}
\]

Where \( R_D \) is the Data Center revenue for Q4 FY2023. However, we need to find \( R_D \) first. 

Assuming the Data Center revenue was a certain percentage of the total revenue in Q4 FY2023, we can estimate it. For simplicity, let's assume the Data Center revenue was around 50% of the total revenue in Q4 FY2023 (this is a rough estimate, as we don't have the exact figure).

Thus, \( R_D \approx 0.5 \times 6
Trustworthiness score: 0.69

```

TLM automatically alerts us that these answers are unreliable, by the low trustworthiness score. RAG systems with TLM help you properly exercise caution when you see low trustworthiness scores. Here are the correct answers to the aforementioned questions:
> NVIDIA's revenue increased by $1.14 billion this quarter compared to last quarter.
> Google, Amazon Web Services, Microsoft, Oracle, ServiceNow, Medtronic, Dell Technologies.
> There is not a specific total count of RTX GPUs mentioned.
> Projected annual revenue if this growth rate is maintained for the next four quarters: approximately $26.34 billion.
With TLM, you can easily increase trust in any RAG system!
Read TLM's performance benchmarks to learn about the effectiveness of the trustworthiness scoring.   
Rather than replacing your LLM with Cleanlab's (as done in this tutorial), you can alternatively use Cleanlab only to detect incorrect responses from your existing unmodified RAG system; check out our real-time Evaluation tutorial.  

