![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# OpenAI Agent + Query Engine Experimental Cookbook¶
In this notebook, we try out the OpenAIAgent across a variety of query engine tools and datasets. We explore how OpenAIAgent can compare/replace existing workflows solved by our retrievers/query engines.
  * Auto retrieval
  * Joint SQL and vector search


**NOTE:** Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
## AutoRetrieval from a Vector Database¶
Our existing "auto-retrieval" capabilities (in `VectorIndexAutoRetriever`) allow an LLM to infer the right query parameters for a vector database - including both the query string and metadata filter.
Since the OpenAI Function API can infer function parameters, we explore its capabilities in performing auto-retrieval here.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-llms-openai
%pip install llama-index-readers-wikipedia
%pip install llama-index-vector-stores-pinecone

```

%pip install llama-index %pip install llama-index-llms-openai %pip install llama-index-readers-wikipedia %pip install llama-index-vector-stores-pinecone
In [ ]:
Copied!
```
import os

os.environ["PINECONE_API_KEY"] = "..."
os.environ["OPENAI_API_KEY"] = "..."

```

import os os.environ["PINECONE_API_KEY"] = "..." os.environ["OPENAI_API_KEY"] = "..."
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

```

from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-4o-mini") Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
In [ ]:
Copied!
```
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

```

from pinecone import Pinecone, ServerlessSpec pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
In [ ]:
Copied!
```
# dimensions are for text-embedding-3-small
pc.create_index(
    name="quickstart-index",
    dimension=1536,
    metric="euclidean",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)

# may need to wait for index to be created
import time

time.sleep(10)

```

# dimensions are for text-embedding-3-small pc.create_index( name="quickstart-index", dimension=1536, metric="euclidean", spec=ServerlessSpec(cloud="aws", region="us-east-1"), ) # may need to wait for index to be created import time time.sleep(10)
Out[ ]:
```
{
    "name": "quickstart-index",
    "metric": "euclidean",
    "host": "quickstart-index-c2e1535.svc.aped-4627-b74a.pinecone.io",
    "spec": {
        "serverless": {
            "cloud": "aws",
            "region": "us-east-1"
        }
    },
    "status": {
        "ready": true,
        "state": "Ready"
    },
    "vector_type": "dense",
    "dimension": 1536,
    "deletion_protection": "disabled",
    "tags": null
}
```

In [ ]:
Copied!
```
index = pc.Index("quickstart-index")

```

index = pc.Index("quickstart-index")
In [ ]:
Copied!
```
# Optional: delete data in your pinecone index
# index.delete(deleteAll=True, namespace="test")

```

# Optional: delete data in your pinecone index # index.delete(deleteAll=True, namespace="test")
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore

```

from llama_index.core import VectorStoreIndex, StorageContext from llama_index.vector_stores.pinecone import PineconeVectorStore
In [ ]:
Copied!
```
from llama_index.core.schema import TextNode

nodes = [
    TextNode(
        text=(
            "Michael Jordan is a retired professional basketball player,"
            " widely regarded as one of the greatest basketball players of all"
            " time."
        ),
        metadata={
            "category": "Sports",
            "country": "United States",
            "gender": "male",
            "born": 1963,
        },
    ),
    TextNode(
        text=(
            "Angelina Jolie is an American actress, filmmaker, and"
            " humanitarian. She has received numerous awards for her acting"
            " and is known for her philanthropic work."
        ),
        metadata={
            "category": "Entertainment",
            "country": "United States",
            "gender": "female",
            "born": 1975,
        },
    ),
    TextNode(
        text=(
            "Elon Musk is a business magnate, industrial designer, and"
            " engineer. He is the founder, CEO, and lead designer of SpaceX,"
            " Tesla, Inc., Neuralink, and The Boring Company."
        ),
        metadata={
            "category": "Business",
            "country": "United States",
            "gender": "male",
            "born": 1971,
        },
    ),
    TextNode(
        text=(
            "Rihanna is a Barbadian singer, actress, and businesswoman. She"
            " has achieved significant success in the music industry and is"
            " known for her versatile musical style."
        ),
        metadata={
            "category": "Music",
            "country": "Barbados",
            "gender": "female",
            "born": 1988,
        },
    ),
    TextNode(
        text=(
            "Cristiano Ronaldo is a Portuguese professional footballer who is"
            " considered one of the greatest football players of all time. He"
            " has won numerous awards and set multiple records during his"
            " career."
        ),
        metadata={
            "category": "Sports",
            "country": "Portugal",
            "gender": "male",
            "born": 1985,
        },
    ),
]

```

from llama_index.core.schema import TextNode nodes = [ TextNode( text=( "Michael Jordan is a retired professional basketball player," " widely regarded as one of the greatest basketball players of all" " time." ), metadata={ "category": "Sports", "country": "United States", "gender": "male", "born": 1963, }, ), TextNode( text=( "Angelina Jolie is an American actress, filmmaker, and" " humanitarian. She has received numerous awards for her acting" " and is known for her philanthropic work." ), metadata={ "category": "Entertainment", "country": "United States", "gender": "female", "born": 1975, }, ), TextNode( text=( "Elon Musk is a business magnate, industrial designer, and" " engineer. He is the founder, CEO, and lead designer of SpaceX," " Tesla, Inc., Neuralink, and The Boring Company." ), metadata={ "category": "Business", "country": "United States", "gender": "male", "born": 1971, }, ), TextNode( text=( "Rihanna is a Barbadian singer, actress, and businesswoman. She" " has achieved significant success in the music industry and is" " known for her versatile musical style." ), metadata={ "category": "Music", "country": "Barbados", "gender": "female", "born": 1988, }, ), TextNode( text=( "Cristiano Ronaldo is a Portuguese professional footballer who is" " considered one of the greatest football players of all time. He" " has won numerous awards and set multiple records during his" " career." ), metadata={ "category": "Sports", "country": "Portugal", "gender": "male", "born": 1985, }, ), ]
In [ ]:
Copied!
```
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext

vector_store = PineconeVectorStore(pinecone_index=index, namespace="test")
storage_context = StorageContext.from_defaults(vector_store=vector_store)

```

from llama_index.vector_stores.pinecone import PineconeVectorStore from llama_index.core import StorageContext vector_store = PineconeVectorStore(pinecone_index=index, namespace="test") storage_context = StorageContext.from_defaults(vector_store=vector_store)
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex(nodes, storage_context=storage_context)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex(nodes, storage_context=storage_context)
```
Upserted vectors:   0%|          | 0/5 [00:00<?, ?it/s]
```

#### Define Function Tool¶
Here we define the function interface, which is passed to OpenAI to perform auto-retrieval.
We were not able to get OpenAI to work with nested pydantic objects or tuples as arguments, so we converted the metadata filter keys and values into lists for the function API to work with.
In [ ]:
Copied!
```
# define function tool
from llama_index.core.tools import FunctionTool
from llama_index.core.vector_stores import (
    VectorStoreInfo,
    MetadataInfo,
    MetadataFilter,
    MetadataFilters,
    FilterCondition,
    FilterOperator,
)
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine

from typing import List, Tuple, Any
from pydantic import BaseModel, Field


# define vector store info describing schema of vector store
vector_store_info = VectorStoreInfo(
    content_info="brief biography of celebrities",
    metadata_info=[
        MetadataInfo(
            name="category",
            type="str",
            description=(
                "Category of the celebrity, one of [Sports, Entertainment,"
                " Business, Music]"
            ),
        ),
        MetadataInfo(
            name="country",
            type="str",
            description=(
                "Country of the celebrity, one of [United States, Barbados,"
                " Portugal]"
            ),
        ),
        MetadataInfo(
            name="gender",
            type="str",
            description=("Gender of the celebrity, one of [male, female]"),
        ),
        MetadataInfo(
            name="born",
            type="int",
            description=("Born year of the celebrity, could be any integer"),
        ),
    ],
)

```

# define function tool from llama_index.core.tools import FunctionTool from llama_index.core.vector_stores import ( VectorStoreInfo, MetadataInfo, MetadataFilter, MetadataFilters, FilterCondition, FilterOperator, ) from llama_index.core.retrievers import VectorIndexRetriever from llama_index.core.query_engine import RetrieverQueryEngine from typing import List, Tuple, Any from pydantic import BaseModel, Field # define vector store info describing schema of vector store vector_store_info = VectorStoreInfo( content_info="brief biography of celebrities", metadata_info=[ MetadataInfo( name="category", type="str", description=( "Category of the celebrity, one of [Sports, Entertainment," " Business, Music]" ), ), MetadataInfo( name="country", type="str", description=( "Country of the celebrity, one of [United States, Barbados," " Portugal]" ), ), MetadataInfo( name="gender", type="str", description=("Gender of the celebrity, one of [male, female]"), ), MetadataInfo( name="born", type="int", description=("Born year of the celebrity, could be any integer"), ), ], )
Define AutoRetrieve Functions
In [ ]:
Copied!
```
from typing import Any, Annotated


async def auto_retrieve_fn(
    query: Annotated[str, "The natural language query/question to answer."],
    filter_key_list: Annotated[
        List[str], "List of metadata filter field names"
    ],
    filter_value_list: Annotated[
        List[Any],
        "List of metadata filter field values (corresponding to names in filter_key_list)",
    ],
    filter_operator_list: Annotated[
        List[str],
        "Metadata filters conditions (could be one of <, <=, >, >=, ==, !=)",
    ],
    filter_condition: Annotated[
        str, "Metadata filters condition values (could be AND or OR)"
    ],
    top_k: Annotated[
        int, "The number of results to return from the vector database."
    ],
):
    """Auto retrieval function.

    Performs auto-retrieval from a vector database, and then applies a set of filters.

    """
    query = query or "Query"

    metadata_filters = [
        MetadataFilter(key=k, value=v, operator=op)
        for k, v, op in zip(
            filter_key_list, filter_value_list, filter_operator_list
        )
    ]
    retriever = VectorIndexRetriever(
        index,
        filters=MetadataFilters(
            filters=metadata_filters, condition=filter_condition.lower()
        ),
        top_k=top_k,
    )
    query_engine = RetrieverQueryEngine.from_args(retriever)

    response = await query_engine.aquery(query)
    return str(response)


description = f"""\
Use this tool to look up biographical information about celebrities.
The vector database schema is given below:

<schema>
{vector_store_info.model_dump_json()}
</schema>
"""

auto_retrieve_tool = FunctionTool.from_defaults(
    auto_retrieve_fn,
    name="celebrity_bios",
    description=description,
)

```

from typing import Any, Annotated async def auto_retrieve_fn( query: Annotated[str, "The natural language query/question to answer."], filter_key_list: Annotated[ List[str], "List of metadata filter field names" ], filter_value_list: Annotated[ List[Any], "List of metadata filter field values (corresponding to names in filter_key_list)", ], filter_operator_list: Annotated[ List[str], "Metadata filters conditions (could be one of <, <=, >, >=, ==, !=)", ], filter_condition: Annotated[ str, "Metadata filters condition values (could be AND or OR)" ], top_k: Annotated[ int, "The number of results to return from the vector database." ], ): """Auto retrieval function. Performs auto-retrieval from a vector database, and then applies a set of filters. """ query = query or "Query" metadata_filters = [ MetadataFilter(key=k, value=v, operator=op) for k, v, op in zip( filter_key_list, filter_value_list, filter_operator_list ) ] retriever = VectorIndexRetriever( index, filters=MetadataFilters( filters=metadata_filters, condition=filter_condition.lower() ), top_k=top_k, ) query_engine = RetrieverQueryEngine.from_args(retriever) response = await query_engine.aquery(query) return str(response) description = f"""\ Use this tool to look up biographical information about celebrities. The vector database schema is given below:  {vector_store_info.model_dump_json()}  """ auto_retrieve_tool = FunctionTool.from_defaults( auto_retrieve_fn, name="celebrity_bios", description=description, )
#### Initialize Agent¶
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI

agent = FunctionAgent(
    tools=[auto_retrieve_tool],
    llm=OpenAI(model="gpt-4o"),
    system_prompt=(
        "You are a helpful assistant that can answer questions about celebrities by writing a filtered query to a vector database. "
        "Unless the user is asking to compare things, you generally only need to make one call to the retriever."
    ),
)

# hold the context/session state for the agent
ctx = Context(agent)

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.core.workflow import Context from llama_index.llms.openai import OpenAI agent = FunctionAgent( tools=[auto_retrieve_tool], llm=OpenAI(model="gpt-4o"), system_prompt=( "You are a helpful assistant that can answer questions about celebrities by writing a filtered query to a vector database. " "Unless the user is asking to compare things, you generally only need to make one call to the retriever." ), ) # hold the context/session state for the agent ctx = Context(agent)
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import (
    ToolCallResult,
    ToolCall,
    AgentStream,
    AgentInput,
    AgentOutput,
)

handler = agent.run(
    "Tell me about two celebrities from the United States. ", ctx=ctx
)

async for ev in handler.stream_events():
    if isinstance(ev, ToolCallResult):
        print(
            f"\nCalled tool {ev.tool_name} with args {ev.tool_kwargs}, got response: {ev.tool_output}"
        )
    elif isinstance(ev, AgentStream):
        print(ev.delta, end="", flush=True)

response = await handler

```

from llama_index.core.agent.workflow import ( ToolCallResult, ToolCall, AgentStream, AgentInput, AgentOutput, ) handler = agent.run( "Tell me about two celebrities from the United States. ", ctx=ctx ) async for ev in handler.stream_events(): if isinstance(ev, ToolCallResult): print( f"\nCalled tool {ev.tool_name} with args {ev.tool_kwargs}, got response: {ev.tool_output}" ) elif isinstance(ev, AgentStream): print(ev.delta, end="", flush=True) response = await handler
```
Called tool celebrity_bios with args {'query': 'celebrities from the United States', 'filter_key_list': ['country'], 'filter_value_list': ['United States'], 'filter_operator_list': ['=='], 'filter_condition': 'AND', 'top_k': 2}, got response: Angelina Jolie and Elon Musk are notable celebrities from the United States.
Here are two celebrities from the United States:

1. **Angelina Jolie**: She is a renowned actress, filmmaker, and humanitarian. Jolie has received numerous accolades, including an Academy Award and three Golden Globe Awards. She is also known for her humanitarian efforts, particularly her work with refugees as a Special Envoy for the United Nations High Commissioner for Refugees (UNHCR).

2. **Elon Musk**: He is a prominent entrepreneur and business magnate. Musk is the CEO and lead designer of SpaceX, CEO and product architect of Tesla, Inc., and has been involved in numerous other ventures, including Neuralink and The Boring Company. He is known for his ambitious vision of the future, including space exploration and sustainable energy.
```

In [ ]:
Copied!
```
handler = agent.run("Tell me about two celebrities born after 1980. ", ctx=ctx)

async for ev in handler.stream_events():
    if isinstance(ev, ToolCallResult):
        print(
            f"\nCalled tool {ev.tool_name} with args {ev.tool_kwargs}, got response: {ev.tool_output}"
        )
    elif isinstance(ev, AgentStream):
        print(ev.delta, end="", flush=True)

response = await handler

```

handler = agent.run("Tell me about two celebrities born after 1980. ", ctx=ctx) async for ev in handler.stream_events(): if isinstance(ev, ToolCallResult): print( f"\nCalled tool {ev.tool_name} with args {ev.tool_kwargs}, got response: {ev.tool_output}" ) elif isinstance(ev, AgentStream): print(ev.delta, end="", flush=True) response = await handler
```
Called tool celebrity_bios with args {'query': 'celebrities born after 1980', 'filter_key_list': ['born'], 'filter_value_list': [1980], 'filter_operator_list': ['>'], 'filter_condition': 'AND', 'top_k': 2}, got response: Rihanna, born in 1988, is a celebrity who fits the criteria of being born after 1980.
Here is a celebrity born after 1980:

- **Rihanna**: Born in 1988, Rihanna is a Barbadian singer, actress, and businesswoman. She gained worldwide fame with her music career, producing hits like "Umbrella," "Diamonds," and "Work." Beyond music, Rihanna has made a significant impact in the fashion and beauty industries with her Fenty brand, known for its inclusivity and innovation.
```

In [ ]:
Copied!
```
response = await agent.run(
    "Tell me about few celebrities under category business and born after 1950. ",
    ctx=ctx,
)
print(str(response))

```

response = await agent.run( "Tell me about few celebrities under category business and born after 1950. ", ctx=ctx, ) print(str(response))
```
Here is a celebrity in the business category who was born after 1950:

- **Elon Musk**: He is a prominent entrepreneur and business magnate, born in 1971. Musk is the CEO and lead designer of SpaceX, CEO and product architect of Tesla, Inc., and has been involved in numerous other ventures, including Neuralink and The Boring Company. He is known for his ambitious vision of the future, including space exploration and sustainable energy.

```

## Joint Text-to-SQL and Semantic Search¶
This is currently handled by our `SQLAutoVectorQueryEngine`.
Let's try implementing this by giving our `OpenAIAgent` access to two query tools: SQL and Vector
**NOTE:** Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
#### Load and Index Structured Data¶
We load sample structured datapoints into a SQL db and index it.
In [ ]:
Copied!
```
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
    column,
)
from llama_index.core import SQLDatabase
from llama_index.core.indices import SQLStructStoreIndex

engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

```

from sqlalchemy import ( create_engine, MetaData, Table, Column, String, Integer, select, column, ) from llama_index.core import SQLDatabase from llama_index.core.indices import SQLStructStoreIndex engine = create_engine("sqlite:///:memory:", future=True) metadata_obj = MetaData()
In [ ]:
Copied!
```
# create city SQL table
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("country", String(16), nullable=False),
)

metadata_obj.create_all(engine)

```

# create city SQL table table_name = "city_stats" city_stats_table = Table( table_name, metadata_obj, Column("city_name", String(16), primary_key=True), Column("population", Integer), Column("country", String(16), nullable=False), ) metadata_obj.create_all(engine)
In [ ]:
Copied!
```
# print tables
metadata_obj.tables.keys()

```

# print tables metadata_obj.tables.keys()
Out[ ]:
```
dict_keys(['city_stats'])
```

In [ ]:
Copied!
```
from sqlalchemy import insert

rows = [
    {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
    {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
    {"city_name": "Berlin", "population": 3645000, "country": "Germany"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

```

from sqlalchemy import insert rows = [ {"city_name": "Toronto", "population": 2930000, "country": "Canada"}, {"city_name": "Tokyo", "population": 13960000, "country": "Japan"}, {"city_name": "Berlin", "population": 3645000, "country": "Germany"}, ] for row in rows: stmt = insert(city_stats_table).values(**row) with engine.begin() as connection: cursor = connection.execute(stmt)
In [ ]:
Copied!
```
with engine.connect() as connection:
    cursor = connection.exec_driver_sql("SELECT * FROM city_stats")
    print(cursor.fetchall())

```

with engine.connect() as connection: cursor = connection.exec_driver_sql("SELECT * FROM city_stats") print(cursor.fetchall())
```
[('Toronto', 2930000, 'Canada'), ('Tokyo', 13960000, 'Japan'), ('Berlin', 3645000, 'Germany')]

```

In [ ]:
Copied!
```
sql_database = SQLDatabase(engine, include_tables=["city_stats"])

```

sql_database = SQLDatabase(engine, include_tables=["city_stats"])
In [ ]:
Copied!
```
from llama_index.core.query_engine import NLSQLTableQueryEngine

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["city_stats"],
)

```

from llama_index.core.query_engine import NLSQLTableQueryEngine query_engine = NLSQLTableQueryEngine( sql_database=sql_database, tables=["city_stats"], )
#### Load and Index Unstructured Data¶
We load unstructured data into a vector index backed by Pinecone
In [ ]:
Copied!
```
# install wikipedia python package
%pip install wikipedia llama-index-readers-wikipedia

```

# install wikipedia python package %pip install wikipedia llama-index-readers-wikipedia
In [ ]:
Copied!
```
from llama_index.readers.wikipedia import WikipediaReader

cities = ["Toronto", "Berlin", "Tokyo"]
wiki_docs = WikipediaReader().load_data(pages=cities)

```

from llama_index.readers.wikipedia import WikipediaReader cities = ["Toronto", "Berlin", "Tokyo"] wiki_docs = WikipediaReader().load_data(pages=cities)
In [ ]:
Copied!
```
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

```

from pinecone import Pinecone, ServerlessSpec pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
In [ ]:
Copied!
```
# dimensions are for text-embedding-3-small
pc.create_index(
    name="quickstart-sql",
    dimension=1536,
    metric="euclidean",
    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
)

# may need to wait for index to be created
import time

time.sleep(10)

```

# dimensions are for text-embedding-3-small pc.create_index( name="quickstart-sql", dimension=1536, metric="euclidean", spec=ServerlessSpec(cloud="aws", region="us-east-1"), ) # may need to wait for index to be created import time time.sleep(10)
In [ ]:
Copied!
```
# define pinecone index
index = pc.Index("quickstart-sql")

```

# define pinecone index index = pc.Index("quickstart-sql")
In [ ]:
Copied!
```
# OPTIONAL: delete all
index.delete(deleteAll=True)

```

# OPTIONAL: delete all index.delete(deleteAll=True)
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# define node parser and LLM
Settings.llm = OpenAI(temperature=0, model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.node_parser = TokenTextSplitter(chunk_size=1024)

# define pinecone vector index
vector_store = PineconeVectorStore(
    pinecone_index=index, namespace="wiki_cities"
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
vector_index = VectorStoreIndex([], storage_context=storage_context)

```

from llama_index.core import VectorStoreIndex, StorageContext from llama_index.vector_stores.pinecone import PineconeVectorStore from llama_index.core.node_parser import TokenTextSplitter from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding # define node parser and LLM Settings.llm = OpenAI(temperature=0, model="gpt-4o-mini") Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small") Settings.node_parser = TokenTextSplitter(chunk_size=1024) # define pinecone vector index vector_store = PineconeVectorStore( pinecone_index=index, namespace="wiki_cities" ) storage_context = StorageContext.from_defaults(vector_store=vector_store) vector_index = VectorStoreIndex([], storage_context=storage_context)
In [ ]:
Copied!
```
# Insert documents into vector index
# Each document has metadata of the city attached
for city, wiki_doc in zip(cities, wiki_docs):
    nodes = Settings.node_parser.get_nodes_from_documents([wiki_doc])
    # add metadata to each node
    for node in nodes:
        node.metadata = {"title": city}
    vector_index.insert_nodes(nodes)

```

# Insert documents into vector index # Each document has metadata of the city attached for city, wiki_doc in zip(cities, wiki_docs): nodes = Settings.node_parser.get_nodes_from_documents([wiki_doc]) # add metadata to each node for node in nodes: node.metadata = {"title": city} vector_index.insert_nodes(nodes)
#### Define Query Engines / Tools¶
In [ ]:
Copied!
```
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores import MetadataInfo, VectorStoreInfo
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.tools import QueryEngineTool


vector_store_info = VectorStoreInfo(
    content_info="articles about different cities",
    metadata_info=[
        MetadataInfo(
            name="title", type="str", description="The name of the city"
        ),
    ],
)

# pre-built auto-retriever, this works similarly to our custom auto-retriever above
vector_auto_retriever = VectorIndexAutoRetriever(
    vector_index, vector_store_info=vector_store_info
)

retriever_query_engine = RetrieverQueryEngine.from_args(
    vector_auto_retriever,
)

```

from llama_index.core.retrievers import VectorIndexAutoRetriever from llama_index.core.vector_stores import MetadataInfo, VectorStoreInfo from llama_index.core.query_engine import RetrieverQueryEngine from llama_index.core.tools import QueryEngineTool vector_store_info = VectorStoreInfo( content_info="articles about different cities", metadata_info=[ MetadataInfo( name="title", type="str", description="The name of the city" ), ], ) # pre-built auto-retriever, this works similarly to our custom auto-retriever above vector_auto_retriever = VectorIndexAutoRetriever( vector_index, vector_store_info=vector_store_info ) retriever_query_engine = RetrieverQueryEngine.from_args( vector_auto_retriever, )
In [ ]:
Copied!
```
sql_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="sql_tool",
    description=(
        "Useful for translating a natural language query into a SQL query over"
        " a table containing: city_stats, containing the population/country of"
        " each city"
    ),
)
vector_tool = QueryEngineTool.from_defaults(
    query_engine=retriever_query_engine,
    name="vector_tool",
    description=(
        "Useful for answering semantic questions about different cities"
    ),
)

```

sql_tool = QueryEngineTool.from_defaults( query_engine=query_engine, name="sql_tool", description=( "Useful for translating a natural language query into a SQL query over" " a table containing: city_stats, containing the population/country of" " each city" ), ) vector_tool = QueryEngineTool.from_defaults( query_engine=retriever_query_engine, name="vector_tool", description=( "Useful for answering semantic questions about different cities" ), )
#### Initialize Agent¶
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import Context

agent = FunctionAgent(
    tools=[sql_tool, vector_tool],
    llm=OpenAI(model="gpt-4o"),
)

# hold the context/session state for the agent
ctx = Context(agent)

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.llms.openai import OpenAI from llama_index.core.workflow import Context agent = FunctionAgent( tools=[sql_tool, vector_tool], llm=OpenAI(model="gpt-4o"), ) # hold the context/session state for the agent ctx = Context(agent)
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import (
    ToolCallResult,
    ToolCall,
    AgentStream,
    AgentInput,
    AgentOutput,
)

handler = agent.run(
    "Tell me about the arts and culture of the city with the highest population. ",
    ctx=ctx,
)

async for ev in handler.stream_events():
    if isinstance(ev, ToolCallResult):
        print(
            f"\nCalled tool {ev.tool_name} with args {ev.tool_kwargs}, got response: {ev.tool_output}"
        )
    elif isinstance(ev, AgentStream):
        print(ev.delta, end="", flush=True)

response = await handler

```

from llama_index.core.agent.workflow import ( ToolCallResult, ToolCall, AgentStream, AgentInput, AgentOutput, ) handler = agent.run( "Tell me about the arts and culture of the city with the highest population. ", ctx=ctx, ) async for ev in handler.stream_events(): if isinstance(ev, ToolCallResult): print( f"\nCalled tool {ev.tool_name} with args {ev.tool_kwargs}, got response: {ev.tool_output}" ) elif isinstance(ev, AgentStream): print(ev.delta, end="", flush=True) response = await handler
```
Called tool sql_tool with args {'input': 'SELECT city FROM city_stats ORDER BY population DESC LIMIT 1;'}, got response: The city with the highest population is Tokyo.

Called tool vector_tool with args {'input': 'Tell me about the arts and culture of Tokyo.'}, got response: Tokyo boasts a vibrant arts and culture scene, characterized by a diverse range of museums, galleries, and performance venues. Ueno Park is a cultural hub, housing the Tokyo National Museum, which specializes in traditional Japanese art, alongside the National Museum of Western Art, a UNESCO World Heritage site, and the National Museum of Nature and Science. The park also features Ueno Zoo, known for its giant pandas.

The city is home to numerous notable museums, including the Artizon Museum, the National Museum of Emerging Science and Innovation, and the Edo-Tokyo Museum, which explores the city's history. Contemporary art is showcased at the Mori Art Museum and the Sumida Hokusai Museum, while the Sompo Museum of Art is recognized for its collection, including Van Gogh's "Sunflowers."

The performing arts thrive in Tokyo, with venues like the National Noh Theatre and Kabuki-za dedicated to traditional Japanese theatre. The New National Theatre Tokyo hosts a variety of performances, including opera and ballet. Major concert venues such as the Nippon Budokan and Tokyo Dome frequently feature popular music acts.

Tokyo's nightlife is vibrant, particularly in districts like Shibuya and Roppongi, which are filled with bars, clubs, and live music venues. The city is also known for its festivals, such as the Sannō Matsuri and the Sanja Festival, which celebrate traditional culture.

Shopping districts like Ginza and Nihombashi offer a blend of high-end retail and cultural experiences, while areas like Jinbōchō are famous for their literary connections, featuring bookstores and cafes linked to renowned authors. Overall, Tokyo's arts and culture reflect a rich tapestry of traditional and contemporary influences, making it a dynamic city for cultural exploration.
Tokyo, the city with the highest population, boasts a vibrant arts and culture scene. It features a diverse range of museums, galleries, and performance venues. Ueno Park serves as a cultural hub, housing the Tokyo National Museum, the National Museum of Western Art, and the National Museum of Nature and Science. The park also includes Ueno Zoo, known for its giant pandas.

Notable museums in Tokyo include the Artizon Museum, the National Museum of Emerging Science and Innovation, and the Edo-Tokyo Museum, which explores the city's history. Contemporary art is showcased at the Mori Art Museum and the Sumida Hokusai Museum, while the Sompo Museum of Art is recognized for its collection, including Van Gogh's "Sunflowers."

The performing arts thrive with venues like the National Noh Theatre and Kabuki-za dedicated to traditional Japanese theatre. The New National Theatre Tokyo hosts a variety of performances, including opera and ballet. Major concert venues such as the Nippon Budokan and Tokyo Dome frequently feature popular music acts.

Tokyo's nightlife is vibrant, especially in districts like Shibuya and Roppongi, filled with bars, clubs, and live music venues. The city is also known for its festivals, such as the Sannō Matsuri and the Sanja Festival, celebrating traditional culture.

Shopping districts like Ginza and Nihombashi offer a blend of high-end retail and cultural experiences, while areas like Jinbōchō are famous for their literary connections, featuring bookstores and cafes linked to renowned authors. Overall, Tokyo's arts and culture reflect a rich tapestry of traditional and contemporary influences, making it a dynamic city for cultural exploration.
```

In [ ]:
Copied!
```
handler = agent.run("Tell me about the history of Berlin", ctx=ctx)

async for ev in handler.stream_events():
    if isinstance(ev, ToolCallResult):
        print(
            f"\nCalled tool {ev.tool_name} with args {ev.tool_kwargs}, got response: {ev.tool_output}"
        )
    elif isinstance(ev, AgentStream):
        print(ev.delta, end="", flush=True)

response = await handler

```

handler = agent.run("Tell me about the history of Berlin", ctx=ctx) async for ev in handler.stream_events(): if isinstance(ev, ToolCallResult): print( f"\nCalled tool {ev.tool_name} with args {ev.tool_kwargs}, got response: {ev.tool_output}" ) elif isinstance(ev, AgentStream): print(ev.delta, end="", flush=True) response = await handler
```
Called tool vector_tool with args {'input': 'Tell me about the history of Berlin.'}, got response: Berlin's history dates back to prehistoric times, with evidence of human settlements as early as 60,000 BC. The area saw the emergence of various cultures, including the Maglemosian culture around 9,000 BC and the Lusatian culture around 2,000 BC, as dense human settlements developed along the Spree and Havel rivers. By 500 BC, Germanic tribes began to settle in the region, followed by Slavic tribes in the 7th century.

In the 12th century, the region came under German rule with the establishment of the Margraviate of Brandenburg. The first written records of towns in the area appear in the late 12th century, with Berlin's founding date considered to be 1237. The towns of Berlin and Cölln formed close economic ties and eventually merged, with the Hohenzollern family ruling the area from the 14th century until 1918.

The Thirty Years' War in the 17th century devastated Berlin, leading to significant population loss. However, under Frederick William, known as the "Great Elector," the city experienced a revival through policies promoting immigration and religious tolerance. The establishment of the Kingdom of Prussia in 1701 marked a significant turning point, with Berlin becoming its capital.

The 19th century brought the Industrial Revolution, transforming Berlin into a major economic center and leading to rapid population growth. By the late 19th century, Berlin was the capital of the newly founded German Empire. The city continued to grow and evolve through the 20th century, experiencing significant events such as World War II, the division into East and West Berlin during the Cold War, and reunification in 1990, when it once again became the capital of a unified Germany.

Today, Berlin is recognized as a global city of culture, politics, media, and science, with a diverse economy and rich historical heritage.
Berlin's history is rich and varied, dating back to prehistoric times with evidence of human settlements as early as 60,000 BC. The area saw the emergence of various cultures, including the Maglemosian culture around 9,000 BC and the Lusatian culture around 2,000 BC, with dense settlements along the Spree and Havel rivers. By 500 BC, Germanic tribes settled in the region, followed by Slavic tribes in the 7th century.

In the 12th century, the region came under German rule with the establishment of the Margraviate of Brandenburg. Berlin's founding date is considered to be 1237, with the towns of Berlin and Cölln forming close economic ties and eventually merging. The Hohenzollern family ruled the area from the 14th century until 1918.

The Thirty Years' War in the 17th century devastated Berlin, but it experienced a revival under Frederick William, the "Great Elector," through policies promoting immigration and religious tolerance. The establishment of the Kingdom of Prussia in 1701 marked a significant turning point, with Berlin becoming its capital.

The 19th century brought the Industrial Revolution, transforming Berlin into a major economic center and leading to rapid population growth. By the late 19th century, Berlin was the capital of the newly founded German Empire. The city continued to evolve through the 20th century, experiencing significant events such as World War II, the division into East and West Berlin during the Cold War, and reunification in 1990, when it once again became the capital of a unified Germany.

Today, Berlin is recognized as a global city of culture, politics, media, and science, with a diverse economy and rich historical heritage.
```

In [ ]:
Copied!
```
response = await agent.run(
    "Can you give me the country corresponding to each city?", ctx=ctx
)

print(str(response))

```

response = await agent.run( "Can you give me the country corresponding to each city?", ctx=ctx ) print(str(response))
```
Here are the cities along with their corresponding countries:

- Toronto is in Canada.
- Tokyo is in Japan.
- Berlin is in Germany.

```

