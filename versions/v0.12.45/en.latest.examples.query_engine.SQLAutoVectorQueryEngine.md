![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# SQL Auto Vector Query Engine¶
In this tutorial, we show you how to use our SQLAutoVectorQueryEngine.
This query engine allows you to combine insights from your structured tables with your unstructured data. It first decides whether to query your structured tables for insights. Once it does, it can then infer a corresponding query to the vector store in order to fetch corresponding documents.
**NOTE:** Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
In [ ]:
Copied!
```
%pip install llama-index-vector-stores-pinecone
%pip install llama-index-readers-wikipedia
%pip install llama-index-llms-openai

```

%pip install llama-index-vector-stores-pinecone %pip install llama-index-readers-wikipedia %pip install llama-index-llms-openai
In [ ]:
Copied!
```
import openai
import os

os.environ["OPENAI_API_KEY"] = "[You API key]"

```

import openai import os os.environ["OPENAI_API_KEY"] = "[You API key]"
### Setup¶
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
# NOTE: This is ONLY necessary in jupyter notebook.
# Details: Jupyter runs an event-loop behind the scenes.
#          This results in nested event-loops when we start an event-loop to make async queries.
#          This is normally not allowed, we use nest_asyncio to allow it for convenience.
import nest_asyncio

nest_asyncio.apply()

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

# NOTE: This is ONLY necessary in jupyter notebook. # Details: Jupyter runs an event-loop behind the scenes. # This results in nested event-loops when we start an event-loop to make async queries. # This is normally not allowed, we use nest_asyncio to allow it for convenience. import nest_asyncio nest_asyncio.apply() import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
### Create Common Objects¶
This includes a `ServiceContext` object containing abstractions such as the LLM and chunk size. This also includes a `StorageContext` object containing our vector store abstractions.
In [ ]:
Copied!
```
# define pinecone index
import pinecone
import os

api_key = os.environ["PINECONE_API_KEY"]
pinecone.init(api_key=api_key, environment="us-west1-gcp-free")

# dimensions are for text-embedding-ada-002
# pinecone.create_index("quickstart", dimension=1536, metric="euclidean", pod_type="p1")
pinecone_index = pinecone.Index("quickstart")

```

# define pinecone index import pinecone import os api_key = os.environ["PINECONE_API_KEY"] pinecone.init(api_key=api_key, environment="us-west1-gcp-free") # dimensions are for text-embedding-ada-002 # pinecone.create_index("quickstart", dimension=1536, metric="euclidean", pod_type="p1") pinecone_index = pinecone.Index("quickstart")
```
/Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages/pinecone/index.py:4: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from tqdm.autonotebook import tqdm

```

In [ ]:
Copied!
```
# OPTIONAL: delete all
pinecone_index.delete(deleteAll=True)

```

# OPTIONAL: delete all pinecone_index.delete(deleteAll=True)
Out[ ]:
```
{}
```

In [ ]:
Copied!
```
from llama_index.core import StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex


# define pinecone vector index
vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index, namespace="wiki_cities"
)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
vector_index = VectorStoreIndex([], storage_context=storage_context)

```

from llama_index.core import StorageContext from llama_index.vector_stores.pinecone import PineconeVectorStore from llama_index.core import VectorStoreIndex # define pinecone vector index vector_store = PineconeVectorStore( pinecone_index=pinecone_index, namespace="wiki_cities" ) storage_context = StorageContext.from_defaults(vector_store=vector_store) vector_index = VectorStoreIndex([], storage_context=storage_context)
### Create Database Schema + Test Data¶
Here we introduce a toy scenario where there are 100 tables (too big to fit into the prompt)
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

```

from sqlalchemy import ( create_engine, MetaData, Table, Column, String, Integer, select, column, )
In [ ]:
Copied!
```
engine = create_engine("sqlite:///:memory:", future=True)
metadata_obj = MetaData()

```

engine = create_engine("sqlite:///:memory:", future=True) metadata_obj = MetaData()
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

We introduce some test data into the `city_stats` table
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

### Load Data¶
We first show how to convert a Document into a set of Nodes, and insert into a DocumentStore.
In [ ]:
Copied!
```
# install wikipedia python package
!pip install wikipedia

```

# install wikipedia python package !pip install wikipedia
```
Requirement already satisfied: wikipedia in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (1.4.0)
Requirement already satisfied: beautifulsoup4 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from wikipedia) (4.12.2)
Requirement already satisfied: requests<3.0.0,>=2.0.0 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from wikipedia) (2.31.0)
Requirement already satisfied: idna<4,>=2.5 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from requests<3.0.0,>=2.0.0->wikipedia) (3.4)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from requests<3.0.0,>=2.0.0->wikipedia) (3.2.0)
Requirement already satisfied: certifi>=2017.4.17 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from requests<3.0.0,>=2.0.0->wikipedia) (2023.5.7)
Requirement already satisfied: urllib3<3,>=1.21.1 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from requests<3.0.0,>=2.0.0->wikipedia) (1.26.16)
Requirement already satisfied: soupsieve>1.2 in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from beautifulsoup4->wikipedia) (2.4.1)
WARNING: You are using pip version 21.2.4; however, version 23.2 is available.
You should consider upgrading via the '/Users/loganmarkewich/llama_index/llama-index/bin/python3 -m pip install --upgrade pip' command.

```

In [ ]:
Copied!
```
from llama_index.readers.wikipedia import WikipediaReader

cities = ["Toronto", "Berlin", "Tokyo"]
wiki_docs = WikipediaReader().load_data(pages=cities)

```

from llama_index.readers.wikipedia import WikipediaReader cities = ["Toronto", "Berlin", "Tokyo"] wiki_docs = WikipediaReader().load_data(pages=cities)
### Build SQL Index¶
In [ ]:
Copied!
```
from llama_index.core import SQLDatabase

sql_database = SQLDatabase(engine, include_tables=["city_stats"])

```

from llama_index.core import SQLDatabase sql_database = SQLDatabase(engine, include_tables=["city_stats"])
In [ ]:
Copied!
```
from llama_index.core.query_engine import NLSQLTableQueryEngine

sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["city_stats"],
)

```

from llama_index.core.query_engine import NLSQLTableQueryEngine sql_query_engine = NLSQLTableQueryEngine( sql_database=sql_database, tables=["city_stats"], )
### Build Vector Index¶
In [ ]:
Copied!
```
from llama_index.core import Settings

# Insert documents into vector index
# Each document has metadata of the city attached
for city, wiki_doc in zip(cities, wiki_docs):
    nodes = Settings.node_parser.get_nodes_from_documents([wiki_doc])
    # add metadata to each node
    for node in nodes:
        node.metadata = {"title": city}
    vector_index.insert_nodes(nodes)

```

from llama_index.core import Settings # Insert documents into vector index # Each document has metadata of the city attached for city, wiki_doc in zip(cities, wiki_docs): nodes = Settings.node_parser.get_nodes_from_documents([wiki_doc]) # add metadata to each node for node in nodes: node.metadata = {"title": city} vector_index.insert_nodes(nodes)
```
Upserted vectors: 100%|██████████| 20/20 [00:00<00:00, 22.37it/s]
Upserted vectors: 100%|██████████| 22/22 [00:00<00:00, 23.14it/s]
Upserted vectors: 100%|██████████| 13/13 [00:00<00:00, 17.67it/s]

```

### Define Query Engines, Set as Tools¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.retrievers import VectorIndexAutoRetriever
from llama_index.core.vector_stores import MetadataInfo, VectorStoreInfo
from llama_index.core.query_engine import RetrieverQueryEngine


vector_store_info = VectorStoreInfo(
    content_info="articles about different cities",
    metadata_info=[
        MetadataInfo(
            name="title", type="str", description="The name of the city"
        ),
    ],
)
vector_auto_retriever = VectorIndexAutoRetriever(
    vector_index, vector_store_info=vector_store_info
)

retriever_query_engine = RetrieverQueryEngine.from_args(
    vector_auto_retriever, llm=OpenAI(model="gpt-4")
)

```

from llama_index.llms.openai import OpenAI from llama_index.core.retrievers import VectorIndexAutoRetriever from llama_index.core.vector_stores import MetadataInfo, VectorStoreInfo from llama_index.core.query_engine import RetrieverQueryEngine vector_store_info = VectorStoreInfo( content_info="articles about different cities", metadata_info=[ MetadataInfo( name="title", type="str", description="The name of the city" ), ], ) vector_auto_retriever = VectorIndexAutoRetriever( vector_index, vector_store_info=vector_store_info ) retriever_query_engine = RetrieverQueryEngine.from_args( vector_auto_retriever, llm=OpenAI(model="gpt-4") )
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool

sql_tool = QueryEngineTool.from_defaults(
    query_engine=sql_query_engine,
    description=(
        "Useful for translating a natural language query into a SQL query over"
        " a table containing: city_stats, containing the population/country of"
        " each city"
    ),
)
vector_tool = QueryEngineTool.from_defaults(
    query_engine=retriever_query_engine,
    description=(
        f"Useful for answering semantic questions about different cities"
    ),
)

```

from llama_index.core.tools import QueryEngineTool sql_tool = QueryEngineTool.from_defaults( query_engine=sql_query_engine, description=( "Useful for translating a natural language query into a SQL query over" " a table containing: city_stats, containing the population/country of" " each city" ), ) vector_tool = QueryEngineTool.from_defaults( query_engine=retriever_query_engine, description=( f"Useful for answering semantic questions about different cities" ), )
### Define SQLAutoVectorQueryEngine¶
In [ ]:
Copied!
```
from llama_index.core.query_engine import SQLAutoVectorQueryEngine

query_engine = SQLAutoVectorQueryEngine(
    sql_tool, vector_tool, llm=OpenAI(model="gpt-4")
)

```

from llama_index.core.query_engine import SQLAutoVectorQueryEngine query_engine = SQLAutoVectorQueryEngine( sql_tool, vector_tool, llm=OpenAI(model="gpt-4") )
In [ ]:
Copied!
```
response = query_engine.query(
    "Tell me about the arts and culture of the city with the highest"
    " population"
)

```

response = query_engine.query( "Tell me about the arts and culture of the city with the highest" " population" )
```
Querying SQL database: Useful for translating a natural language query into a SQL query over a table containing city_stats, containing the population/country of each city
INFO:llama_index.query_engine.sql_join_query_engine:> Querying SQL database: Useful for translating a natural language query into a SQL query over a table containing city_stats, containing the population/country of each city
> Querying SQL database: Useful for translating a natural language query into a SQL query over a table containing city_stats, containing the population/country of each city
INFO:llama_index.indices.struct_store.sql_query:> Table desc str: Table 'city_stats' has columns: city_name (VARCHAR(16)), population (INTEGER), country (VARCHAR(16)) and foreign keys: .
> Table desc str: Table 'city_stats' has columns: city_name (VARCHAR(16)), population (INTEGER), country (VARCHAR(16)) and foreign keys: .
SQL query: SELECT city_name, population FROM city_stats ORDER BY population DESC LIMIT 1;
SQL response: 
Tokyo is the city with the highest population, with 13.96 million people. It is a vibrant city with a rich culture and a wide variety of art forms. From traditional Japanese art such as calligraphy and woodblock prints to modern art galleries and museums, Tokyo has something for everyone. There are also many festivals and events throughout the year that celebrate the city's culture and art.
Transformed query given SQL response: What are some specific cultural festivals, events, and notable art galleries or museums in Tokyo?
INFO:llama_index.query_engine.sql_join_query_engine:> Transformed query given SQL response: What are some specific cultural festivals, events, and notable art galleries or museums in Tokyo?
> Transformed query given SQL response: What are some specific cultural festivals, events, and notable art galleries or museums in Tokyo?
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using query str: cultural festivals events art galleries museums Tokyo
Using query str: cultural festivals events art galleries museums Tokyo
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using filters: {'title': 'Tokyo'}
Using filters: {'title': 'Tokyo'}
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using top_k: 2
Using top_k: 2
query engine response: The context information mentions the Tokyo National Museum, which houses 37% of the country's artwork national treasures. It also mentions the Studio Ghibli anime center as a subcultural attraction. However, the text does not provide information on specific cultural festivals or events in Tokyo.
INFO:llama_index.query_engine.sql_join_query_engine:> query engine response: The context information mentions the Tokyo National Museum, which houses 37% of the country's artwork national treasures. It also mentions the Studio Ghibli anime center as a subcultural attraction. However, the text does not provide information on specific cultural festivals or events in Tokyo.
> query engine response: The context information mentions the Tokyo National Museum, which houses 37% of the country's artwork national treasures. It also mentions the Studio Ghibli anime center as a subcultural attraction. However, the text does not provide information on specific cultural festivals or events in Tokyo.
Final response: Tokyo, the city with the highest population of 13.96 million people, is known for its vibrant culture and diverse art forms. It is home to traditional Japanese art such as calligraphy and woodblock prints, as well as modern art galleries and museums. Notably, the Tokyo National Museum houses 37% of the country's artwork national treasures, and the Studio Ghibli anime center is a popular subcultural attraction. While there are many festivals and events throughout the year that celebrate the city's culture and art, specific examples were not provided in the available information.

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Tokyo, the city with the highest population of 13.96 million people, is known for its vibrant culture and diverse art forms. It is home to traditional Japanese art such as calligraphy and woodblock prints, as well as modern art galleries and museums. Notably, the Tokyo National Museum houses 37% of the country's artwork national treasures, and the Studio Ghibli anime center is a popular subcultural attraction. While there are many festivals and events throughout the year that celebrate the city's culture and art, specific examples were not provided in the available information.

```

In [ ]:
Copied!
```
response = query_engine.query("Tell me about the history of Berlin")

```

response = query_engine.query("Tell me about the history of Berlin")
```
Querying other query engine: Useful for answering semantic questions about different cities
INFO:llama_index.query_engine.sql_join_query_engine:> Querying other query engine: Useful for answering semantic questions about different cities
> Querying other query engine: Useful for answering semantic questions about different cities
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using query str: history of Berlin
Using query str: history of Berlin
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using filters: {'title': 'Berlin'}
Using filters: {'title': 'Berlin'}
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using top_k: 2
Using top_k: 2
Query Engine response: Berlin's history dates back to around 60,000 BC, with the earliest human traces found in the area. A Mesolithic deer antler mask found in Biesdorf (Berlin) was dated around 9000 BC. During Neolithic times, a large number of communities existed in the area and in the Bronze Age, up to 1000 people lived in 50 villages. Early Germanic tribes took settlement from 500 BC and Slavic settlements and castles began around 750 AD.

The earliest evidence of middle age settlements in the area of today's Berlin are remnants of a house foundation dated to 1174, found in excavations in Berlin Mitte, and a wooden beam dated from approximately 1192. The first written records of towns in the area of present-day Berlin date from the late 12th century. Spandau is first mentioned in 1197 and Köpenick in 1209, although these areas did not join Berlin until 1920. 

The central part of Berlin can be traced back to two towns. Cölln on the Fischerinsel is first mentioned in a 1237 document, and Berlin, across the Spree in what is now called the Nikolaiviertel, is referenced in a document from 1244. 1237 is considered the founding date of the city. The two towns over time formed close economic and social ties, and profited from the staple right on the two important trade routes Via Imperii and from Bruges to Novgorod. In 1307, they formed an alliance with a common external policy, their internal administrations still being separated. In 1415, Frederick I became the elector of the Margraviate of Brandenburg, which he ruled until 1440.

The name Berlin has its roots in the language of West Slavic inhabitants of the area of today's Berlin, and may be related to the Old Polabian stem berl-/birl- ("swamp"). or Proto-Slavic bьrlogъ, (lair, den). Since the Ber- at the beginning sounds like the German word Bär ("bear"), a bear appears in the coat of arms of the city. It is therefore an example of canting arms.

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Berlin's history dates back to around 60,000 BC, with the earliest human traces found in the area. A Mesolithic deer antler mask found in Biesdorf (Berlin) was dated around 9000 BC. During Neolithic times, a large number of communities existed in the area and in the Bronze Age, up to 1000 people lived in 50 villages. Early Germanic tribes took settlement from 500 BC and Slavic settlements and castles began around 750 AD.

The earliest evidence of middle age settlements in the area of today's Berlin are remnants of a house foundation dated to 1174, found in excavations in Berlin Mitte, and a wooden beam dated from approximately 1192. The first written records of towns in the area of present-day Berlin date from the late 12th century. Spandau is first mentioned in 1197 and Köpenick in 1209, although these areas did not join Berlin until 1920. 

The central part of Berlin can be traced back to two towns. Cölln on the Fischerinsel is first mentioned in a 1237 document, and Berlin, across the Spree in what is now called the Nikolaiviertel, is referenced in a document from 1244. 1237 is considered the founding date of the city. The two towns over time formed close economic and social ties, and profited from the staple right on the two important trade routes Via Imperii and from Bruges to Novgorod. In 1307, they formed an alliance with a common external policy, their internal administrations still being separated. In 1415, Frederick I became the elector of the Margraviate of Brandenburg, which he ruled until 1440.

The name Berlin has its roots in the language of West Slavic inhabitants of the area of today's Berlin, and may be related to the Old Polabian stem berl-/birl- ("swamp"). or Proto-Slavic bьrlogъ, (lair, den). Since the Ber- at the beginning sounds like the German word Bär ("bear"), a bear appears in the coat of arms of the city. It is therefore an example of canting arms.

```

In [ ]:
Copied!
```
response = query_engine.query(
    "Can you give me the country corresponding to each city?"
)

```

response = query_engine.query( "Can you give me the country corresponding to each city?" )
```
Querying SQL database: Useful for translating a natural language query into a SQL query over a table containing: city_stats, containing the population/country of each city
INFO:llama_index.query_engine.sql_join_query_engine:> Querying SQL database: Useful for translating a natural language query into a SQL query over a table containing: city_stats, containing the population/country of each city
> Querying SQL database: Useful for translating a natural language query into a SQL query over a table containing: city_stats, containing the population/country of each city
INFO:llama_index.indices.struct_store.sql_query:> Table desc str: Table 'city_stats' has columns: city_name (VARCHAR(16)), population (INTEGER), country (VARCHAR(16)) and foreign keys: .
> Table desc str: Table 'city_stats' has columns: city_name (VARCHAR(16)), population (INTEGER), country (VARCHAR(16)) and foreign keys: .
SQL query: SELECT city_name, country FROM city_stats;
SQL response:  Toronto is in Canada, Tokyo is in Japan, and Berlin is in Germany.
Transformed query given SQL response: What countries are New York, San Francisco, and other cities in?
INFO:llama_index.query_engine.sql_join_query_engine:> Transformed query given SQL response: What countries are New York, San Francisco, and other cities in?
> Transformed query given SQL response: What countries are New York, San Francisco, and other cities in?
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using query str: New York San Francisco
Using query str: New York San Francisco
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using filters: {'title': 'San Francisco'}
Using filters: {'title': 'San Francisco'}
INFO:llama_index.indices.vector_store.retrievers.auto_retriever.auto_retriever:Using top_k: 2
Using top_k: 2
query engine response: None
INFO:llama_index.query_engine.sql_join_query_engine:> query engine response: None
> query engine response: None
Final response: The country corresponding to each city is as follows: Toronto is in Canada, Tokyo is in Japan, and Berlin is in Germany. Unfortunately, I do not have information on the countries for New York, San Francisco, and other cities.

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The country corresponding to each city is as follows: Toronto is in Canada, Tokyo is in Japan, and Berlin is in Germany. Unfortunately, I do not have information on the countries for New York, San Francisco, and other cities.

```

