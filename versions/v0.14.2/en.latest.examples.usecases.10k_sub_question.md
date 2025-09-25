![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# 10K Analysis¶
In this demo, we explore answering complex queries by decomposing them into simpler sub-queries.
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
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.llms.openai import OpenAI

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.llms.openai import OpenAI from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.query_engine import SubQuestionQueryEngine
```
/Users/suo/miniconda3/envs/llama/lib/python3.9/site-packages/deeplake/util/check_latest_version.py:32: UserWarning: A newer version of deeplake (3.6.7) is available. It's recommended that you update to the latest version using `pip install -U deeplake`.
  warnings.warn(

```

## Configure LLM service¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

```

import os os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo")

```

from llama_index.core import Settings Settings.llm = OpenAI(temperature=0.2, model="gpt-3.5-turbo")
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
## Load data¶
In [ ]:
Copied!
```
lyft_docs = SimpleDirectoryReader(
    input_files=["./data/10k/lyft_2021.pdf"]
).load_data()
uber_docs = SimpleDirectoryReader(
    input_files=["./data/10k/uber_2021.pdf"]
).load_data()

```

lyft_docs = SimpleDirectoryReader( input_files=["./data/10k/lyft_2021.pdf"] ).load_data() uber_docs = SimpleDirectoryReader( input_files=["./data/10k/uber_2021.pdf"] ).load_data()
## Build indices¶
In [ ]:
Copied!
```
lyft_index = VectorStoreIndex.from_documents(lyft_docs)

```

lyft_index = VectorStoreIndex.from_documents(lyft_docs)
In [ ]:
Copied!
```
uber_index = VectorStoreIndex.from_documents(uber_docs)

```

uber_index = VectorStoreIndex.from_documents(uber_docs)
## Build query engines¶
In [ ]:
Copied!
```
lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)

```

lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
uber_engine = uber_index.as_query_engine(similarity_top_k=3)

```

uber_engine = uber_index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
query_engine_tools = [
    QueryEngineTool(
        query_engine=lyft_engine,
        metadata=ToolMetadata(
            name="lyft_10k",
            description=(
                "Provides information about Lyft financials for year 2021"
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=uber_engine,
        metadata=ToolMetadata(
            name="uber_10k",
            description=(
                "Provides information about Uber financials for year 2021"
            ),
        ),
    ),
]

s_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools
)

```

query_engine_tools = [ QueryEngineTool( query_engine=lyft_engine, metadata=ToolMetadata( name="lyft_10k", description=( "Provides information about Lyft financials for year 2021" ), ), ), QueryEngineTool( query_engine=uber_engine, metadata=ToolMetadata( name="uber_10k", description=( "Provides information about Uber financials for year 2021" ), ), ), ] s_engine = SubQuestionQueryEngine.from_defaults( query_engine_tools=query_engine_tools )
## Run queries¶
In [ ]:
Copied!
```
response = s_engine.query(
    "Compare and contrast the customer segments and geographies that grew the"
    " fastest"
)

```

response = s_engine.query( "Compare and contrast the customer segments and geographies that grew the" " fastest" )
```
Generated 4 sub questions.
[uber_10k] Q: What customer segments grew the fastest for Uber
[uber_10k] Q: What geographies grew the fastest for Uber
[lyft_10k] Q: What customer segments grew the fastest for Lyft
[lyft_10k] Q: What geographies grew the fastest for Lyft
[uber_10k] A: 
Uber experienced the fastest growth in five metropolitan areas—Chicago, Miami, and New York City in the United States, Sao Paulo in Brazil, and London in the United Kingdom. Additionally, Uber experienced growth in suburban and rural areas, though the network is smaller and less liquid in these areas.
[lyft_10k] A: 
Lyft has seen the fastest growth in its ridesharing marketplace, Express Drive, Lyft Rentals, Light Vehicles, Public Transit, and Lyft Autonomous customer segments. These customer segments have seen increased demand due to the convenience and high-quality experience they offer drivers and riders, as well as the investments Lyft has made in its proprietary technology, M&A and strategic partnerships, and brand and marketing efforts.
[lyft_10k] A: 
Lyft has grown rapidly in cities across the United States and in select cities in Canada. The ridesharing market grew rapidly prior to the COVID-19 pandemic, and it is uncertain to what extent market acceptance will continue to grow after the pandemic. The market for Lyft's other offerings, such as its network of Light Vehicles, is also new and unproven, and it is uncertain whether demand for bike and scooter sharing will continue to grow.
[uber_10k] A: in 2021?

The customer segments that grew the fastest for Uber in 2021 were Riders and Eaters, who use the platform for ridesharing services and meal preparation, grocery, and other delivery services, respectively. Additionally, Uber One, Uber Pass, Eats Pass, and Rides Pass membership programs grew significantly in 2021, with over 6 million members.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Uber and Lyft both experienced the fastest growth in their respective customer segments and geographies in 2021. 

For Uber, the fastest growing customer segments were Riders and Eaters, who use the platform for ridesharing services and meal preparation, grocery, and other delivery services, respectively. Additionally, Uber One, Uber Pass, Eats Pass, and Rides Pass membership programs grew significantly in 2021, with over 6 million members. Uber experienced the fastest growth in five metropolitan areas—Chicago, Miami, and New York City in the United States, Sao Paulo in Brazil, and London in the United Kingdom. Additionally, Uber experienced growth in suburban and rural areas, though the network is smaller and less liquid in these areas.

For Lyft, the fastest growing customer segments were ridesharing, Express Drive, Lyft Rentals, Light Vehicles, Public Transit, and Lyft Autonomous. Lyft has grown rapidly in cities across the United States and in select cities in Canada. The ridesharing market grew rapidly prior to the COVID-19 pandemic, and it is uncertain to what extent market acceptance will continue to grow after the pandemic. The market for Lyft's other offerings, such as its network of Light Vehicles, is also new and unproven, and it is uncertain whether demand for bike and scooter sharing will continue to grow.

Overall, Uber and Lyft experienced the fastest growth in different customer segments and geographies. Uber experienced the fastest growth in Riders and Eaters, as well as in five metropolitan areas, while Lyft experienced the fastest growth in ridesharing, Express Drive, Lyft Rentals, Light Vehicles, Public Transit, and Lyft Autonomous, as well as in cities across the United States and in select cities in Canada.

```

In [ ]:
Copied!
```
response = s_engine.query(
    "Compare revenue growth of Uber and Lyft from 2020 to 2021"
)

```

response = s_engine.query( "Compare revenue growth of Uber and Lyft from 2020 to 2021" )
```
Generated 2 sub questions.
[uber_10k] Q: What is the revenue growth of Uber from 2020 to 2021
[lyft_10k] Q: What is the revenue growth of Lyft from 2020 to 2021
[lyft_10k] A: 
The revenue of Lyft grew by 36% from 2020 to 2021.
[uber_10k] A: 
The revenue growth of Uber from 2020 to 2021 was 57%, or 54% on a constant currency basis.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The revenue growth of Uber from 2020 to 2021 was 57%, or 54% on a constant currency basis, while the revenue of Lyft grew by 36% from 2020 to 2021. Therefore, Uber had a higher revenue growth than Lyft from 2020 to 2021.

```

