![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Structured LLM Reranker Demonstration (2021 Lyft 10-k)¶
This tutorial showcases how to do a two-stage pass for retrieval. Use embedding-based retrieval with a high top-k value in order to maximize recall and get a large set of candidate items. Then, use LLM-based retrieval to dynamically select the nodes that are actually relevant to the query using structured output.
Usage of `StructuredLLMReranker` is preferred over `LLMReranker` when you are using a model that supports function calling. This class will make use of the structured output capability of the model instead of relying on prompting the model to rank the nodes in a desired format.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.postprocessor import StructuredLLMRerank

from llama_index.llms.openai import OpenAI
from IPython.display import Markdown, display

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from llama_index.core.postprocessor import StructuredLLMRerank from llama_index.llms.openai import OpenAI from IPython.display import Markdown, display
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
```
--2025-03-20 15:13:23--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.111.133, 185.199.108.133, 185.199.110.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.111.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1440303 (1.4M) [application/octet-stream]
Saving to: ‘data/10k/lyft_2021.pdf’

data/10k/lyft_2021. 100%[===================>]   1.37M  --.-KB/s    in 0.06s   

2025-03-20 15:13:24 (23.9 MB/s) - ‘data/10k/lyft_2021.pdf’ saved [1440303/1440303]


```

## Load Data, Build Index¶
In [ ]:
Copied!
```
from llama_index.core import Settings

# LLM (gpt-4o-mini)
Settings.llm = OpenAI(temperature=0, model="gpt-4o-mini")

Settings.chunk_overlap = 0
Settings.chunk_size = 128

```

from llama_index.core import Settings # LLM (gpt-4o-mini) Settings.llm = OpenAI(temperature=0, model="gpt-4o-mini") Settings.chunk_overlap = 0 Settings.chunk_size = 128
In [ ]:
Copied!
```
# load documents
documents = SimpleDirectoryReader(
    input_files=["./data/10k/lyft_2021.pdf"]
).load_data()

```

# load documents documents = SimpleDirectoryReader( input_files=["./data/10k/lyft_2021.pdf"] ).load_data()
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(
    documents,
)

```

index = VectorStoreIndex.from_documents( documents, )
## Retrieval Comparisons¶
In [ ]:
Copied!
```
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle
import pandas as pd
from IPython.display import display, HTML
from copy import deepcopy


def get_retrieved_nodes(
    query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False
):
    query_bundle = QueryBundle(query_str)
    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=vector_top_k,
    )
    retrieved_nodes = retriever.retrieve(query_bundle)

    if with_reranker:
        # configure reranker
        reranker = StructuredLLMRerank(
            choice_batch_size=5,
            top_n=reranker_top_n,
        )
        retrieved_nodes = reranker.postprocess_nodes(
            retrieved_nodes, query_bundle
        )

    return retrieved_nodes


def pretty_print(df):
    return display(HTML(df.to_html().replace("\\n", "<br>")))


def visualize_retrieved_nodes(nodes) -> None:
    result_dicts = []
    for node in nodes:
        node = deepcopy(node)
        node.node.metadata = {}
        node_text = node.node.get_text()
        node_text = node_text.replace("\n", " ")

        result_dict = {"Score": node.score, "Text": node_text}
        result_dicts.append(result_dict)

    pretty_print(pd.DataFrame(result_dicts))

```

from llama_index.core.retrievers import VectorIndexRetriever from llama_index.core import QueryBundle import pandas as pd from IPython.display import display, HTML from copy import deepcopy def get_retrieved_nodes( query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False ): query_bundle = QueryBundle(query_str) # configure retriever retriever = VectorIndexRetriever( index=index, similarity_top_k=vector_top_k, ) retrieved_nodes = retriever.retrieve(query_bundle) if with_reranker: # configure reranker reranker = StructuredLLMRerank( choice_batch_size=5, top_n=reranker_top_n, ) retrieved_nodes = reranker.postprocess_nodes( retrieved_nodes, query_bundle ) return retrieved_nodes def pretty_print(df): return display(HTML(df.to_html().replace("\\\n", "  
"))) def visualize_retrieved_nodes(nodes) -> None: result_dicts = [] for node in nodes: node = deepcopy(node) node.node.metadata = {} node_text = node.node.get_text() node_text = node_text.replace("\n", " ") result_dict = {"Score": node.score, "Text": node_text} result_dicts.append(result_dict) pretty_print(pd.DataFrame(result_dicts))
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "What is Lyft's response to COVID-19?", vector_top_k=5, with_reranker=False
)

```

new_nodes = get_retrieved_nodes( "What is Lyft's response to COVID-19?", vector_top_k=5, with_reranker=False )
In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 0.870327 | Further, COVID-19 has and may continue to negatively impact Lyft’s ability to conduct rental operationsthrough the Express Drive program and Lyft Rentals as a result of restrictions on travel, mandated closures, limited staffing availability, and other factors relatedto COVID-19. For example, in 2020, Lyft Rentals temporarily ceased operations, closing its rental locations, as a result of COVID-19.  
1 | 0.858815 | The Company has adopted a number of measures in response to the COVID-19 pandemic including, but not limited to, establishing new health and safetyrequirements for ridesharing and updating workplace policies. The Company also made adjustments to its expenses and cash flow to correlate with declines in revenuesincluding headcount reductions in 2020. Refer to Note 17 “Restructuring” to the consolidated financial statements for information regarding the 2020 restructuring events.  
2 | 0.857701 | •The responsive measures to the COVID-19 pandemic have caused us to modify our business practices by permitting corporate employees in nearly all of ourlocations to work remotely, limiting employee travel, and canceling, postponing or holding virtual events and meetings.  
3 | 0.855108 | The strength and duration ofthese challenges cannot be presently estimated.In response to the COVID-19 pandemic, we have adopted multiple measures, including, but not limited, to establishing new health and safety requirements forridesharing and updating workplace policies. We also made adjustments to our expenses and cash flow to correlate with declines in revenues including headcountreductions in 2020.  
4 | 0.854779 | In 2020, Flexdrive also began to waive rental fees for drivers who are confirmed to have testedpositive for COVID-19 or requested to quarantine by a medical professional, which it continues to do at this time. Further, Lyft Rentals and Flexdrive have facedsignificantly higher costs in transporting, repossessing, cleaning, and17  
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "What is Lyft's response to COVID-19?",
    vector_top_k=20,
    reranker_top_n=5,
    with_reranker=True,
)

```

new_nodes = get_retrieved_nodes( "What is Lyft's response to COVID-19?", vector_top_k=20, reranker_top_n=5, with_reranker=True, )
In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 10.0 | The Company has adopted a number of measures in response to the COVID-19 pandemic including, but not limited to, establishing new health and safetyrequirements for ridesharing and updating workplace policies. The Company also made adjustments to its expenses and cash flow to correlate with declines in revenuesincluding headcount reductions in 2020. Refer to Note 17 “Restructuring” to the consolidated financial statements for information regarding the 2020 restructuring events.  
1 | 10.0 | We have adopted several measures in response to the COVID-19 pandemic including, but not limited to, establishing new health and safety requirements forridesharing, and updating workplace policies. We also made adjustments to our expenses and cash flow to correlate with declines in revenues including the transaction withWoven Planet completed on July 13, 2021 and headcount reductions in 2020.  
2 | 10.0 | •manage our platform and our business assets and expenses in light of the COVID-19 pandemic and related public health measures issued by various jurisdictions,including travel bans, travel restrictions and shelter-in-place orders, as well as maintain demand for and confidence in the safety of our platform during andfollowing the COVID-19 pandemic;•plan for and manage capital expenditures for our current and future offerings,  
3 | 9.0 | The strength and duration ofthese challenges cannot be presently estimated.In response to the COVID-19 pandemic, we have adopted multiple measures, including, but not limited, to establishing new health and safety requirements forridesharing and updating workplace policies. We also made adjustments to our expenses and cash flow to correlate with declines in revenues including headcountreductions in 2020.  
4 | 9.0 | The strength and duration ofthese challenges cannot be presently estimated.In response to the COVID-19 pandemic, we have adopted multiple measures, including, but not limited, to establishing new health and safety requirements forridesharing and updating workplace policies. We also made adjustments to our expenses and cash flow to correlate with declines in revenues including headcountreductions in 2020.56  
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "What initiatives are the company focusing on independently of COVID-19?",
    vector_top_k=5,
    with_reranker=False,
)

```

new_nodes = get_retrieved_nodes( "What initiatives are the company focusing on independently of COVID-19?", vector_top_k=5, with_reranker=False, )
In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 0.813871 | •The responsive measures to the COVID-19 pandemic have caused us to modify our business practices by permitting corporate employees in nearly all of ourlocations to work remotely, limiting employee travel, and canceling, postponing or holding virtual events and meetings.  
1 | 0.810687 | •manage our platform and our business assets and expenses in light of the COVID-19 pandemic and related public health measures issued by various jurisdictions,including travel bans, travel restrictions and shelter-in-place orders, as well as maintain demand for and confidence in the safety of our platform during andfollowing the COVID-19 pandemic;•plan for and manage capital expenditures for our current and future offerings,  
2 | 0.809540 | The strength and duration ofthese challenges cannot be presently estimated.In response to the COVID-19 pandemic, we have adopted multiple measures, including, but not limited, to establishing new health and safety requirements forridesharing and updating workplace policies. We also made adjustments to our expenses and cash flow to correlate with declines in revenues including headcountreductions in 2020.  
3 | 0.806794 | the timing and extent of spending to support ourefforts to develop our platform, actual insurance payments for which we have made reserves, measures we take in response to the COVID-19 pandemic, our ability tomaintain demand for and confidence in the safety of our platform during and following the COVID-19 pandemic, and the expansion of sales and marketing activities.  
4 | 0.805533 | •anticipate and respond to macroeconomic changes and changes in the markets in which we operate;•maintain and enhance the value of our reputation and brand;•effectively manage our growth and business operations, including the impacts of the COVID-19 pandemic on our business;•successfully expand our geographic reach;•hire, integrate and retain talented people at all levels of our organization;•successfully develop new platform features, offerings and services to enhance the experience of users; and•right-size our real estate portfolio.  
In [ ]:
Copied!
```
new_nodes = get_retrieved_nodes(
    "What initiatives are the company focusing on independently of COVID-19?",
    vector_top_k=40,
    reranker_top_n=5,
    with_reranker=True,
)

```

new_nodes = get_retrieved_nodes( "What initiatives are the company focusing on independently of COVID-19?", vector_top_k=40, reranker_top_n=5, with_reranker=True, )
In [ ]:
Copied!
```
visualize_retrieved_nodes(new_nodes)

```

visualize_retrieved_nodes(new_nodes)
| Score | Text  
---|---|---  
0 | 9.0 | Even as we invest in the business, we also remain focused on finding ways to operate more efficiently.To advance our mission, we aim to build the defining brand of our generation and to advocate through our commitment to social and environmental responsibility.We believe that our brand represents freedom at your fingertips: freedom from the stresses of car ownership and freedom to do and see more.  
1 | 8.0 | We have also invested in sales and marketing to grow our community,cultivate a differentiated brand that resonates with drivers and riders and promote further brand awareness. Together, these investments have enabled us to create a powerfulmultimodal platform and scaled user network.Notwithstanding the impact of COVID-19, we are continuing to invest in the future, both organically and through acquisitions of complementary businesses.  
2 | 8.0 | As a result, we may introduce significantchanges to our existing offerings or develop and introduce new and unproven offerings. For example, in April 2020, we began piloting a delivery service platform inresponse to the COVID-19 pandemic.  
3 | 6.0 | •anticipate and respond to macroeconomic changes and changes in the markets in which we operate;•maintain and enhance the value of our reputation and brand;•effectively manage our growth and business operations, including the impacts of the COVID-19 pandemic on our business;•successfully expand our geographic reach;•hire, integrate and retain talented people at all levels of our organization;•successfully develop new platform features, offerings and services to enhance the experience of users; and•right-size our real estate portfolio.  
4 | 6.0 | has been critical to our success. We face a number ofchallenges that may affect our ability to sustain our corporate culture, including:•failure to identify, attract, reward and retain people in leadership positions in our organization who share and further our culture, values and mission;•the increasing size and geographic diversity of our workforce;•shelter-in-place orders in certain jurisdictions where we operate that have required many of our employees to work remotely,
