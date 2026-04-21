![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# SQL Router Query Engine¶
In this tutorial, we define a custom router query engine that can route to either a SQL database or a vector database.
**NOTE:** Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
### Setup¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-wikipedia

```

%pip install llama-index-readers-wikipedia
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

```

# NOTE: This is ONLY necessary in jupyter notebook. # Details: Jupyter runs an event-loop behind the scenes. # This results in nested event-loops when we start an event-loop to make async queries. # This is normally not allowed, we use nest_asyncio to allow it for convenience. import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core import VectorStoreIndex, SQLDatabase
from llama_index.readers.wikipedia import WikipediaReader

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) from llama_index.core import VectorStoreIndex, SQLDatabase from llama_index.readers.wikipedia import WikipediaReader
```
INFO:numexpr.utils:Note: NumExpr detected 12 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
Note: NumExpr detected 12 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
INFO:numexpr.utils:NumExpr defaulting to 8 threads.
NumExpr defaulting to 8 threads.

```

```
/Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

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
Requirement already satisfied: wikipedia in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (1.4.0)
Requirement already satisfied: requests<3.0.0,>=2.0.0 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from wikipedia) (2.28.2)
Requirement already satisfied: beautifulsoup4 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from wikipedia) (4.12.2)
Requirement already satisfied: idna<4,>=2.5 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from requests<3.0.0,>=2.0.0->wikipedia) (3.4)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from requests<3.0.0,>=2.0.0->wikipedia) (3.1.0)
Requirement already satisfied: certifi>=2017.4.17 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from requests<3.0.0,>=2.0.0->wikipedia) (2022.12.7)
Requirement already satisfied: urllib3<1.27,>=1.21.1 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from requests<3.0.0,>=2.0.0->wikipedia) (1.26.15)
Requirement already satisfied: soupsieve>1.2 in /Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages (from beautifulsoup4->wikipedia) (2.4.1)

[notice] A new release of pip available: 22.3.1 -> 23.1.2
[notice] To update, run: pip install --upgrade pip

```

In [ ]:
Copied!
```
cities = ["Toronto", "Berlin", "Tokyo"]
wiki_docs = WikipediaReader().load_data(pages=cities)

```

cities = ["Toronto", "Berlin", "Tokyo"] wiki_docs = WikipediaReader().load_data(pages=cities)
### Build SQL Index¶
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

```

from llama_index.core.query_engine import NLSQLTableQueryEngine
In [ ]:
Copied!
```
sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["city_stats"],
)

```

sql_query_engine = NLSQLTableQueryEngine( sql_database=sql_database, tables=["city_stats"], )
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens
> [build_index_from_nodes] Total embedding token usage: 0 tokens

```

```
/Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages/langchain/sql_database.py:227: UserWarning: This method is deprecated - please use `get_usable_table_names`.
  warnings.warn(

```

### Build Vector Index¶
In [ ]:
Copied!
```
# build a separate vector index per city
# You could also choose to define a single vector index across all docs, and annotate each chunk by metadata
vector_indices = []
for wiki_doc in wiki_docs:
    vector_index = VectorStoreIndex.from_documents([wiki_doc])
    vector_indices.append(vector_index)

```

# build a separate vector index per city # You could also choose to define a single vector index across all docs, and annotate each chunk by metadata vector_indices = [] for wiki_doc in wiki_docs: vector_index = VectorStoreIndex.from_documents([wiki_doc]) vector_indices.append(vector_index)
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 20744 tokens
> [build_index_from_nodes] Total embedding token usage: 20744 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 21947 tokens
> [build_index_from_nodes] Total embedding token usage: 21947 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 12786 tokens
> [build_index_from_nodes] Total embedding token usage: 12786 tokens

```

### Define Query Engines, Set as Tools¶
In [ ]:
Copied!
```
vector_query_engines = [index.as_query_engine() for index in vector_indices]

```

vector_query_engines = [index.as_query_engine() for index in vector_indices]
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
vector_tools = []
for city, query_engine in zip(cities, vector_query_engines):
    vector_tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        description=f"Useful for answering semantic questions about {city}",
    )
    vector_tools.append(vector_tool)

```

from llama_index.core.tools import QueryEngineTool sql_tool = QueryEngineTool.from_defaults( query_engine=sql_query_engine, description=( "Useful for translating a natural language query into a SQL query over" " a table containing: city_stats, containing the population/country of" " each city" ), ) vector_tools = [] for city, query_engine in zip(cities, vector_query_engines): vector_tool = QueryEngineTool.from_defaults( query_engine=query_engine, description=f"Useful for answering semantic questions about {city}", ) vector_tools.append(vector_tool)
### Define Router Query Engine¶
In [ ]:
Copied!
```
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

query_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=([sql_tool] + vector_tools),
)

```

from llama_index.core.query_engine import RouterQueryEngine from llama_index.core.selectors import LLMSingleSelector query_engine = RouterQueryEngine( selector=LLMSingleSelector.from_defaults(), query_engine_tools=([sql_tool] + vector_tools), )
In [ ]:
Copied!
```
response = query_engine.query("Which city has the highest population?")
print(str(response))

```

response = query_engine.query("Which city has the highest population?") print(str(response))
```
INFO:llama_index.query_engine.router_query_engine:Selecting query engine 0: Useful for translating a natural language query into a SQL query over a table containing: city_stats, containing the population/country of each city.
Selecting query engine 0: Useful for translating a natural language query into a SQL query over a table containing: city_stats, containing the population/country of each city.
INFO:llama_index.indices.struct_store.sql_query:> Table desc str: Schema of table city_stats:
Table 'city_stats' has columns: city_name (VARCHAR(16)), population (INTEGER), country (VARCHAR(16)) and foreign keys: .

> Table desc str: Schema of table city_stats:
Table 'city_stats' has columns: city_name (VARCHAR(16)), population (INTEGER), country (VARCHAR(16)) and foreign keys: .

INFO:llama_index.token_counter.token_counter:> [query] Total LLM token usage: 347 tokens
> [query] Total LLM token usage: 347 tokens
INFO:llama_index.token_counter.token_counter:> [query] Total embedding token usage: 0 tokens
> [query] Total embedding token usage: 0 tokens
 Tokyo has the highest population, with 13,960,000 people.

```

In [ ]:
Copied!
```
response = query_engine.query("Tell me about the historical museums in Berlin")
print(str(response))

```

response = query_engine.query("Tell me about the historical museums in Berlin") print(str(response))
```
INFO:llama_index.query_engine.router_query_engine:Selecting query engine 2: Useful for answering semantic questions about Berlin.
Selecting query engine 2: Useful for answering semantic questions about Berlin.
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 8 tokens
> [retrieve] Total embedding token usage: 8 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 2031 tokens
> [get_response] Total LLM token usage: 2031 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

Berlin is home to many historical museums, including the Altes Museum, Neues Museum, Alte Nationalgalerie, Pergamon Museum, and Bode Museum, which are all located on Museum Island. The Gemäldegalerie (Painting Gallery) focuses on the paintings of the "old masters" from the 13th to the 18th centuries, while the Neue Nationalgalerie (New National Gallery, built by Ludwig Mies van der Rohe) specializes in 20th-century European painting. The Hamburger Bahnhof, in Moabit, exhibits a major collection of modern and contemporary art. The expanded Deutsches Historisches Museum reopened in the Zeughaus with an overview of German history spanning more than a millennium. The Bauhaus Archive is a museum of 20th-century design from the famous Bauhaus school. Museum Berggruen houses the collection of noted 20th century collector Heinz Berggruen, and features an extensive assortment of works by Picasso, Matisse, Cézanne, and Giacometti, among others. The Kupferstichkabinett Berlin (Museum of Prints and Drawings) is part of the Staatlichen Museen z

```

In [ ]:
Copied!
```
response = query_engine.query("Which countries are each city from?")
print(str(response))

```

response = query_engine.query("Which countries are each city from?") print(str(response))
```
INFO:llama_index.query_engine.router_query_engine:Selecting query engine 0: Useful for translating a natural language query into a SQL query over a table containing: city_stats, containing the population/country of each city.
Selecting query engine 0: Useful for translating a natural language query into a SQL query over a table containing: city_stats, containing the population/country of each city.
INFO:llama_index.indices.struct_store.sql_query:> Table desc str: Schema of table city_stats:
Table 'city_stats' has columns: city_name (VARCHAR(16)), population (INTEGER), country (VARCHAR(16)) and foreign keys: .

> Table desc str: Schema of table city_stats:
Table 'city_stats' has columns: city_name (VARCHAR(16)), population (INTEGER), country (VARCHAR(16)) and foreign keys: .

INFO:llama_index.token_counter.token_counter:> [query] Total LLM token usage: 334 tokens
> [query] Total LLM token usage: 334 tokens
INFO:llama_index.token_counter.token_counter:> [query] Total embedding token usage: 0 tokens
> [query] Total embedding token usage: 0 tokens
 Toronto is from Canada, Tokyo is from Japan, and Berlin is from Germany.

```

