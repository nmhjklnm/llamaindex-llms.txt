![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# SQL Query Engine with LlamaIndex + DuckDB¶
This guide showcases the core LlamaIndex SQL capabilities with DuckDB.
We go through some core LlamaIndex data structures, including the `NLSQLTableQueryEngine` and `SQLTableRetrieverQueryEngine`.
**NOTE:** Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
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
!pip install duckdb duckdb-engine

```

!pip install duckdb duckdb-engine
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
from llama_index.core import SQLDatabase, SimpleDirectoryReader, Document
from llama_index.readers.wikipedia import WikipediaReader
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine

```

from llama_index.core import SQLDatabase, SimpleDirectoryReader, Document from llama_index.readers.wikipedia import WikipediaReader from llama_index.core.query_engine import NLSQLTableQueryEngine from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
In [ ]:
Copied!
```
from IPython.display import Markdown, display

```

from IPython.display import Markdown, display
## Basic Text-to-SQL with our `NLSQLTableQueryEngine`¶
In this initial example, we walk through populating a SQL database with some test datapoints, and querying it with our text-to-SQL capabilities.
### Create Database Schema + Test Data¶
We use sqlalchemy, a popular SQL database toolkit, to connect to DuckDB and create an empty `city_stats` Table. We then populate it with some test data.
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
engine = create_engine("duckdb:///:memory:")
# uncomment to make this work with MotherDuck
# engine = create_engine("duckdb:///md:llama-index")
metadata_obj = MetaData()

```

engine = create_engine("duckdb:///:memory:") # uncomment to make this work with MotherDuck # engine = create_engine("duckdb:///md:llama-index") metadata_obj = MetaData()
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
    {
        "city_name": "Chicago",
        "population": 2679000,
        "country": "United States",
    },
    {"city_name": "Seoul", "population": 9776000, "country": "South Korea"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

```

from sqlalchemy import insert rows = [ {"city_name": "Toronto", "population": 2930000, "country": "Canada"}, {"city_name": "Tokyo", "population": 13960000, "country": "Japan"}, { "city_name": "Chicago", "population": 2679000, "country": "United States", }, {"city_name": "Seoul", "population": 9776000, "country": "South Korea"}, ] for row in rows: stmt = insert(city_stats_table).values(**row) with engine.begin() as connection: cursor = connection.execute(stmt)
In [ ]:
Copied!
```
with engine.connect() as connection:
    cursor = connection.exec_driver_sql("SELECT * FROM city_stats")
    print(cursor.fetchall())

```

with engine.connect() as connection: cursor = connection.exec_driver_sql("SELECT * FROM city_stats") print(cursor.fetchall())
```
[('Toronto', 2930000, 'Canada'), ('Tokyo', 13960000, 'Japan'), ('Chicago', 2679000, 'United States'), ('Seoul', 9776000, 'South Korea')]

```

### Create SQLDatabase Object¶
We first define our SQLDatabase abstraction (a light wrapper around SQLAlchemy).
In [ ]:
Copied!
```
from llama_index.core import SQLDatabase

```

from llama_index.core import SQLDatabase
In [ ]:
Copied!
```
sql_database = SQLDatabase(engine, include_tables=["city_stats"])

```

sql_database = SQLDatabase(engine, include_tables=["city_stats"])
```
/Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages/duckdb_engine/__init__.py:162: DuckDBEngineWarning: duckdb-engine doesn't yet support reflection on indices
  warnings.warn(

```

### Query Index¶
Here we demonstrate the capabilities of `NLSQLTableQueryEngine`, which performs text-to-SQL.
  1. We construct a `NLSQLTableQueryEngine` and pass in our SQL database object.
  2. We run queries against the query engine.


In [ ]:
Copied!
```
query_engine = NLSQLTableQueryEngine(sql_database)

```

query_engine = NLSQLTableQueryEngine(sql_database)
In [ ]:
Copied!
```
response = query_engine.query("Which city has the highest population?")

```

response = query_engine.query("Which city has the highest population?")
```
INFO:llama_index.indices.struct_store.sql_query:> Table desc str: Table 'city_stats' has columns: city_name (VARCHAR), population (INTEGER), country (VARCHAR) and foreign keys: .
> Table desc str: Table 'city_stats' has columns: city_name (VARCHAR), population (INTEGER), country (VARCHAR) and foreign keys: .

```

```
/Users/jerryliu/Programming/gpt_index/.venv/lib/python3.10/site-packages/langchain/sql_database.py:238: UserWarning: This method is deprecated - please use `get_usable_table_names`.
  warnings.warn(

```

```
INFO:llama_index.token_counter.token_counter:> [query] Total LLM token usage: 332 tokens
> [query] Total LLM token usage: 332 tokens
INFO:llama_index.token_counter.token_counter:> [query] Total embedding token usage: 0 tokens
> [query] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
str(response)

```

str(response)
Out[ ]:
```
' Tokyo has the highest population, with 13,960,000 people.'
```

In [ ]:
Copied!
```
response.metadata

```

response.metadata
Out[ ]:
```
{'result': [('Tokyo', 13960000)],
 'sql_query': 'SELECT city_name, population \nFROM city_stats \nORDER BY population DESC \nLIMIT 1;'}
```

## Advanced Text-to-SQL with our `SQLTableRetrieverQueryEngine`¶
In this guide, we tackle the setting where you have a large number of tables in your database, and putting all the table schemas into the prompt may overflow the text-to-SQL prompt.
We first index the schemas with our `ObjectIndex`, and then use our `SQLTableRetrieverQueryEngine` abstraction on top.
In [ ]:
Copied!
```
engine = create_engine("duckdb:///:memory:")
# uncomment to make this work with MotherDuck
# engine = create_engine("duckdb:///md:llama-index")
metadata_obj = MetaData()

```

engine = create_engine("duckdb:///:memory:") # uncomment to make this work with MotherDuck # engine = create_engine("duckdb:///md:llama-index") metadata_obj = MetaData()
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
all_table_names = ["city_stats"]
# create a ton of dummy tables
n = 100
for i in range(n):
    tmp_table_name = f"tmp_table_{i}"
    tmp_table = Table(
        tmp_table_name,
        metadata_obj,
        Column(f"tmp_field_{i}_1", String(16), primary_key=True),
        Column(f"tmp_field_{i}_2", Integer),
        Column(f"tmp_field_{i}_3", String(16), nullable=False),
    )
    all_table_names.append(f"tmp_table_{i}")

metadata_obj.create_all(engine)

```

# create city SQL table table_name = "city_stats" city_stats_table = Table( table_name, metadata_obj, Column("city_name", String(16), primary_key=True), Column("population", Integer), Column("country", String(16), nullable=False), ) all_table_names = ["city_stats"] # create a ton of dummy tables n = 100 for i in range(n): tmp_table_name = f"tmp_table_{i}" tmp_table = Table( tmp_table_name, metadata_obj, Column(f"tmp_field_{i}_1", String(16), primary_key=True), Column(f"tmp_field_{i}_2", Integer), Column(f"tmp_field_{i}_3", String(16), nullable=False), ) all_table_names.append(f"tmp_table_{i}") metadata_obj.create_all(engine)
In [ ]:
Copied!
```
# insert dummy data
from sqlalchemy import insert

rows = [
    {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
    {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
    {
        "city_name": "Chicago",
        "population": 2679000,
        "country": "United States",
    },
    {"city_name": "Seoul", "population": 9776000, "country": "South Korea"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

```

# insert dummy data from sqlalchemy import insert rows = [ {"city_name": "Toronto", "population": 2930000, "country": "Canada"}, {"city_name": "Tokyo", "population": 13960000, "country": "Japan"}, { "city_name": "Chicago", "population": 2679000, "country": "United States", }, {"city_name": "Seoul", "population": 9776000, "country": "South Korea"}, ] for row in rows: stmt = insert(city_stats_table).values(**row) with engine.begin() as connection: cursor = connection.execute(stmt)
In [ ]:
Copied!
```
sql_database = SQLDatabase(engine, include_tables=["city_stats"])

```

sql_database = SQLDatabase(engine, include_tables=["city_stats"])
### Construct Object Index¶
In [ ]:
Copied!
```
from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import VectorStoreIndex

```

from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine from llama_index.core.objects import ( SQLTableNodeMapping, ObjectIndex, SQLTableSchema, ) from llama_index.core import VectorStoreIndex
In [ ]:
Copied!
```
table_node_mapping = SQLTableNodeMapping(sql_database)

table_schema_objs = []
for table_name in all_table_names:
    table_schema_objs.append(SQLTableSchema(table_name=table_name))

obj_index = ObjectIndex.from_objects(
    table_schema_objs,
    table_node_mapping,
    VectorStoreIndex,
)

```

table_node_mapping = SQLTableNodeMapping(sql_database) table_schema_objs = [] for table_name in all_table_names: table_schema_objs.append(SQLTableSchema(table_name=table_name)) obj_index = ObjectIndex.from_objects( table_schema_objs, table_node_mapping, VectorStoreIndex, )
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 6343 tokens
> [build_index_from_nodes] Total embedding token usage: 6343 tokens

```

### Query Index with `SQLTableRetrieverQueryEngine`¶
In [ ]:
Copied!
```
query_engine = SQLTableRetrieverQueryEngine(
    sql_database,
    obj_index.as_retriever(similarity_top_k=1),
)

```

query_engine = SQLTableRetrieverQueryEngine( sql_database, obj_index.as_retriever(similarity_top_k=1), )
In [ ]:
Copied!
```
response = query_engine.query("Which city has the highest population?")

```

response = query_engine.query("Which city has the highest population?")
```
INFO:llama_index.token_counter.token_counter:> [retrieve] Total LLM token usage: 0 tokens
> [retrieve] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [retrieve] Total embedding token usage: 7 tokens
> [retrieve] Total embedding token usage: 7 tokens
INFO:llama_index.indices.struct_store.sql_query:> Table desc str: Table 'city_stats' has columns: city_name (VARCHAR), population (INTEGER), country (VARCHAR) and foreign keys: .
> Table desc str: Table 'city_stats' has columns: city_name (VARCHAR), population (INTEGER), country (VARCHAR) and foreign keys: .
INFO:llama_index.token_counter.token_counter:> [query] Total LLM token usage: 337 tokens
> [query] Total LLM token usage: 337 tokens
INFO:llama_index.token_counter.token_counter:> [query] Total embedding token usage: 0 tokens
> [query] Total embedding token usage: 0 tokens

```

In [ ]:
Copied!
```
response

```

response
Out[ ]:
```
Response(response=' The city with the highest population is Tokyo, with a population of 13,960,000.', source_nodes=[], metadata={'result': [('Tokyo', 13960000)], 'sql_query': 'SELECT city_name, population \nFROM city_stats \nORDER BY population DESC \nLIMIT 1;'})
```

