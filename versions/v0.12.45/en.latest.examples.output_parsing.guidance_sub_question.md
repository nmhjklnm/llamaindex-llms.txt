![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Guidance for Sub-Question Query Engine¶
In this notebook, we showcase how to use **guidance** to improve the robustness of our sub-question query engine.
The sub-question query engine is designed to accept swappable question generators that implement the `BaseQuestionGenerator` interface.  
To leverage the power of **guidance**, we implemented a new `GuidanceQuestionGenerator` (powered by our `GuidancePydanticProgram`)
## Guidance Question Generator¶
Unlike the default `LLMQuestionGenerator`, guidance guarantees that we will get the desired structured output, and eliminate output parsing errors.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-question-gen-guidance

```

%pip install llama-index-question-gen-guidance
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.question_gen.guidance import GuidanceQuestionGenerator
from guidance.llms import OpenAI as GuidanceOpenAI

```

from llama_index.question_gen.guidance import GuidanceQuestionGenerator from guidance.llms import OpenAI as GuidanceOpenAI
In [ ]:
Copied!
```
question_gen = GuidanceQuestionGenerator.from_defaults(
    guidance_llm=GuidanceOpenAI("text-davinci-003"), verbose=False
)

```

question_gen = GuidanceQuestionGenerator.from_defaults( guidance_llm=GuidanceOpenAI("text-davinci-003"), verbose=False )
Let's test it out!
In [ ]:
Copied!
```
from llama_index.core.tools import ToolMetadata
from llama_index.core import QueryBundle

```

from llama_index.core.tools import ToolMetadata from llama_index.core import QueryBundle
In [ ]:
Copied!
```
tools = [
    ToolMetadata(
        name="lyft_10k",
        description="Provides information about Lyft financials for year 2021",
    ),
    ToolMetadata(
        name="uber_10k",
        description="Provides information about Uber financials for year 2021",
    ),
]

```

tools = [ ToolMetadata( name="lyft_10k", description="Provides information about Lyft financials for year 2021", ), ToolMetadata( name="uber_10k", description="Provides information about Uber financials for year 2021", ), ]
In [ ]:
Copied!
```
sub_questions = question_gen.generate(
    tools=tools,
    query=QueryBundle("Compare and contrast Uber and Lyft financial in 2021"),
)

```

sub_questions = question_gen.generate( tools=tools, query=QueryBundle("Compare and contrast Uber and Lyft financial in 2021"), )
In [ ]:
Copied!
```
sub_questions

```

sub_questions
Out[ ]:
```
[SubQuestion(sub_question='What is the revenue of Uber', tool_name='uber_10k'),
 SubQuestion(sub_question='What is the EBITDA of Uber', tool_name='uber_10k'),
 SubQuestion(sub_question='What is the net income of Uber', tool_name='uber_10k'),
 SubQuestion(sub_question='What is the revenue of Lyft', tool_name='lyft_10k'),
 SubQuestion(sub_question='What is the EBITDA of Lyft', tool_name='lyft_10k'),
 SubQuestion(sub_question='What is the net income of Lyft', tool_name='lyft_10k')]
```

## Using Guidance Question Generator with Sub-Question Query Engine¶
### Prepare data and base query engines¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.response.pprint_utils import pprint_response

from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.core.response.pprint_utils import pprint_response from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.query_engine import SubQuestionQueryEngine
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/uber_2021.pdf' -O 'data/10k/uber_2021.pdf' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
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
In [ ]:
Copied!
```
lyft_index = VectorStoreIndex.from_documents(lyft_docs)
uber_index = VectorStoreIndex.from_documents(uber_docs)

```

lyft_index = VectorStoreIndex.from_documents(lyft_docs) uber_index = VectorStoreIndex.from_documents(uber_docs)
In [ ]:
Copied!
```
lyft_engine = lyft_index.as_query_engine(similarity_top_k=3)
uber_engine = uber_index.as_query_engine(similarity_top_k=3)

```

lyft_engine = lyft_index.as_query_engine(similarity_top_k=3) uber_engine = uber_index.as_query_engine(similarity_top_k=3)
### Construct sub-question query engine and run some queries!¶
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
    question_gen=question_gen,  # use guidance based question_gen defined above
    query_engine_tools=query_engine_tools,
)

```

query_engine_tools = [ QueryEngineTool( query_engine=lyft_engine, metadata=ToolMetadata( name="lyft_10k", description=( "Provides information about Lyft financials for year 2021" ), ), ), QueryEngineTool( query_engine=uber_engine, metadata=ToolMetadata( name="uber_10k", description=( "Provides information about Uber financials for year 2021" ), ), ), ] s_engine = SubQuestionQueryEngine.from_defaults( question_gen=question_gen, # use guidance based question_gen defined above query_engine_tools=query_engine_tools, )
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
[uber_10k] A: in 2021?

The customer segments that grew the fastest for Uber in 2021 were its Mobility Drivers, Couriers, Riders, and Eaters. These segments experienced growth due to the continued stay-at-home order demand related to COVID-19, as well as Uber's membership programs, such as Uber One, Uber Pass, Eats Pass, and Rides Pass. Additionally, Uber's marketplace-centric advertising helped to connect merchants and brands with its platform network, further driving growth.
[uber_10k] Q: What geographies grew the fastest for Uber
[uber_10k] A: 
Based on the context information, it appears that Uber experienced the most growth in large metropolitan areas, such as Chicago, Miami, New York City, Sao Paulo, and London. Additionally, Uber experienced growth in suburban and rural areas, as well as in countries such as Argentina, Germany, Italy, Japan, South Korea, and Spain.
[lyft_10k] Q: What customer segments grew the fastest for Lyft
[lyft_10k] A: 
The customer segments that grew the fastest for Lyft were ridesharing, light vehicles, and public transit. Ridesharing grew as Lyft was able to predict demand and proactively incentivize drivers to be available for rides in the right place at the right time. Light vehicles grew as users were looking for options that were more active, usually lower-priced, and often more efficient for short trips during heavy traffic. Public transit grew as Lyft integrated third-party public transit data into the Lyft App to offer users a robust view of transportation options around them.
[lyft_10k] Q: What geographies grew the fastest for Lyft
[lyft_10k] A: 
It is not possible to answer this question with the given context information.

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The customer segments that grew the fastest for Uber in 2021 were its Mobility Drivers, Couriers, Riders, and Eaters. These segments experienced growth due to the continued stay-at-home order demand related to COVID-19, as well as Uber's membership programs, such as Uber One, Uber Pass, Eats Pass, and Rides Pass. Additionally, Uber's marketplace-centric advertising helped to connect merchants and brands with its platform network, further driving growth. Uber experienced the most growth in large metropolitan areas, such as Chicago, Miami, New York City, Sao Paulo, and London. Additionally, Uber experienced growth in suburban and rural areas, as well as in countries such as Argentina, Germany, Italy, Japan, South Korea, and Spain.

The customer segments that grew the fastest for Lyft were ridesharing, light vehicles, and public transit. Ridesharing grew as Lyft was able to predict demand and proactively incentivize drivers to be available for rides in the right place at the right time. Light vehicles grew as users were looking for options that were more active, usually lower-priced, and often more efficient for short trips during heavy traffic. Public transit grew as Lyft integrated third-party public transit data into the Lyft App to offer users a robust view of transportation options around them. It is not possible to answer the question of which geographies grew the fastest for Lyft with the given context information.

In summary, Uber and Lyft both experienced growth in customer segments related to their respective services, such as Mobility Drivers, Couriers, Riders, and Eaters for Uber, and ridesharing, light vehicles, and public transit for Lyft. Uber experienced the most growth in large metropolitan areas, as well as in suburban and rural areas, and in countries such as Argentina, Germany, Italy, Japan, South Korea, and Spain. It is not possible to answer the question of which geographies grew the fastest for Lyft with the given context information.

```

