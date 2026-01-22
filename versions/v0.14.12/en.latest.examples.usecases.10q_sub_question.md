![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# 10Q Analysis¶
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
from llama_index.core.response.pprint_utils import pprint_response
from llama_index.llms.openai import OpenAI

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.core.response.pprint_utils import pprint_response from llama_index.llms.openai import OpenAI from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.query_engine import SubQuestionQueryEngine
## Configure LLM service¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"

```

import os os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
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
!mkdir -p 'data/10q/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_march_2022.pdf' -O 'data/10q/uber_10q_march_2022.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_june_2022.pdf' -O 'data/10q/uber_10q_june_2022.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_sept_2022.pdf' -O 'data/10q/uber_10q_sept_2022.pdf'

```

!mkdir -p 'data/10q/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_march_2022.pdf' -O 'data/10q/uber_10q_march_2022.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_june_2022.pdf' -O 'data/10q/uber_10q_june_2022.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_sept_2022.pdf' -O 'data/10q/uber_10q_sept_2022.pdf'
## Load data¶
In [ ]:
Copied!
```
march_2022 = SimpleDirectoryReader(
    input_files=["./data/10q/uber_10q_march_2022.pdf"]
).load_data()
june_2022 = SimpleDirectoryReader(
    input_files=["./data/10q/uber_10q_june_2022.pdf"]
).load_data()
sept_2022 = SimpleDirectoryReader(
    input_files=["./data/10q/uber_10q_sept_2022.pdf"]
).load_data()

```

march_2022 = SimpleDirectoryReader( input_files=["./data/10q/uber_10q_march_2022.pdf"] ).load_data() june_2022 = SimpleDirectoryReader( input_files=["./data/10q/uber_10q_june_2022.pdf"] ).load_data() sept_2022 = SimpleDirectoryReader( input_files=["./data/10q/uber_10q_sept_2022.pdf"] ).load_data()
# Build indices¶
In [ ]:
Copied!
```
march_index = VectorStoreIndex.from_documents(march_2022)
june_index = VectorStoreIndex.from_documents(june_2022)
sept_index = VectorStoreIndex.from_documents(sept_2022)

```

march_index = VectorStoreIndex.from_documents(march_2022) june_index = VectorStoreIndex.from_documents(june_2022) sept_index = VectorStoreIndex.from_documents(sept_2022)
## Build query engines¶
In [ ]:
Copied!
```
march_engine = march_index.as_query_engine(similarity_top_k=3)
june_engine = june_index.as_query_engine(similarity_top_k=3)
sept_engine = sept_index.as_query_engine(similarity_top_k=3)

```

march_engine = march_index.as_query_engine(similarity_top_k=3) june_engine = june_index.as_query_engine(similarity_top_k=3) sept_engine = sept_index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
query_engine_tools = [
    QueryEngineTool(
        query_engine=sept_engine,
        metadata=ToolMetadata(
            name="sept_22",
            description=(
                "Provides information about Uber quarterly financials ending"
                " September 2022"
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=june_engine,
        metadata=ToolMetadata(
            name="june_22",
            description=(
                "Provides information about Uber quarterly financials ending"
                " June 2022"
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=march_engine,
        metadata=ToolMetadata(
            name="march_22",
            description=(
                "Provides information about Uber quarterly financials ending"
                " March 2022"
            ),
        ),
    ),
]

```

query_engine_tools = [ QueryEngineTool( query_engine=sept_engine, metadata=ToolMetadata( name="sept_22", description=( "Provides information about Uber quarterly financials ending" " September 2022" ), ), ), QueryEngineTool( query_engine=june_engine, metadata=ToolMetadata( name="june_22", description=( "Provides information about Uber quarterly financials ending" " June 2022" ), ), ), QueryEngineTool( query_engine=march_engine, metadata=ToolMetadata( name="march_22", description=( "Provides information about Uber quarterly financials ending" " March 2022" ), ), ), ]
In [ ]:
Copied!
```
s_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools
)

```

s_engine = SubQuestionQueryEngine.from_defaults( query_engine_tools=query_engine_tools )
## Run queries¶
In [ ]:
Copied!
```
response = s_engine.query(
    "Analyze Uber revenue growth over the latest two quarter filings"
)

```

response = s_engine.query( "Analyze Uber revenue growth over the latest two quarter filings" )
```
Generated 2 sub questions.
[sept_22] Q: What is the revenue growth of Uber for the quarter ending September 2022
[sept_22] A: compared to the same period in 2021?

The revenue growth of Uber for the quarter ending September 2022 compared to the same period in 2021 is 72%.
[june_22] Q: What is the revenue growth of Uber for the quarter ending June 2022
[june_22] A: compared to the same period in 2021?

The revenue growth of Uber for the quarter ending June 2022 compared to the same period in 2021 is 105%.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Uber's revenue growth over the latest two quarter filings has been strong, with a 72% increase for the quarter ending September 2022 compared to the same period in 2021, and a 105% increase for the quarter ending June 2022 compared to the same period in 2021.

```

In [ ]:
Copied!
```
response = s_engine.query(
    "Analyze change in macro environment over the 3 quarters"
)

```

response = s_engine.query( "Analyze change in macro environment over the 3 quarters" )
```
Generated 3 sub questions.
[sept_22] Q: What is the macro environment in September 2022
[sept_22] A: 
The macro environment in September 2022 is one of recovery from the impacts of the COVID-19 pandemic, with increases in Mobility Trip volumes, a $1.3 billion increase in Freight Gross Bookings resulting from the acquisition of Transplace, a $1.1 billion increase in Mobility revenue due to business model changes in the UK, and a $164 million increase in Delivery revenue due to an increase in certain Courier payments and incentives. Additionally, there was a $2.2 billion net increase in Mobility revenue due to business model changes in the UK and an accrual made for the resolution of historical claims in the UK relating to the classification of drivers, and a $751 million increase in Delivery revenue due to an increase in certain Courier payments and incentives.
[june_22] Q: What is the macro environment in June 2022
[june_22] A: 
In June 2022, the macro environment is characterized by the continued impact of COVID-19 restrictions on global demand, the adoption of new accounting standards, and the potential for shifts in consumer travel patterns due to health concerns.
[march_22] Q: What is the macro environment in March 2022
[march_22] A: 
The macro environment in March 2022 is uncertain, as the effects of the COVID-19 pandemic and the actions taken to mitigate it are still being felt. Travel restrictions, business restrictions, school closures, and limitations on social or public gatherings may still be in place in some regions, and the demand for services may still be affected.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The macro environment has seen a significant change over the three quarters from March 2022 to September 2022. In March 2022, the macro environment was uncertain due to the effects of the COVID-19 pandemic and the actions taken to mitigate it. By June 2022, the macro environment was characterized by the continued impact of COVID-19 restrictions on global demand, the adoption of new accounting standards, and the potential for shifts in consumer travel patterns due to health concerns. By September 2022, the macro environment had shifted to one of recovery from the impacts of the COVID-19 pandemic, with increases in Mobility Trip volumes, a $1.3 billion increase in Freight Gross Bookings resulting from the acquisition of Transplace, a $1.1 billion increase in Mobility revenue due to business model changes in the UK, and a $164 million increase in Delivery revenue due to an increase in certain Courier payments and incentives. Additionally, there was a $2.2 billion net increase in Mobility revenue due to business model changes in the UK and an accrual made for the resolution of historical claims in the UK relating to the classification of drivers, and a $751 million increase in Delivery revenue due to an increase in certain Courier payments and incentives.

```

In [ ]:
Copied!
```
response = s_engine.query("How much cash did Uber have in sept 2022")

```

response = s_engine.query("How much cash did Uber have in sept 2022")
```
Generated 1 sub questions.
[sept_22] Q: How much cash did Uber have in September 2022
[sept_22] A: 
Uber had $4,865 million in cash in September 2022.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
Uber had $4,865 million in cash in September 2022.

```

