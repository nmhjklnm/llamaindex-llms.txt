![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Text-to-SQL Guide (Query Engine + Retriever)¶
This is a basic guide to LlamaIndex's Text-to-SQL capabilities.
  1. We first show how to perform text-to-SQL over a toy dataset: this will do "retrieval" (sql query over db) and "synthesis".
  2. We then show how to buid a TableIndex over the schema to dynamically retrieve relevant tables during query-time.
  3. Next, we show how to use query-time rows and columns retrievers to enhance Text-to-SQL context.
  4. We finally show you how to define a text-to-SQL retriever on its own.


**NOTE:** Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-core llama-index-llms-openai llama-index-embeddings-openai

```

%pip install llama-index-core llama-index-llms-openai llama-index-embeddings-openai
In [ ]:
Copied!
```
import os
import openai

```

import os import openai
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "sk-.."

```

os.environ["OPENAI_API_KEY"] = "sk-.."
In [ ]:
Copied!
```
# import logging
# import sys

# logging.basicConfig(stream=sys.stdout, level=logging.INFO)
# logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

# import logging # import sys # logging.basicConfig(stream=sys.stdout, level=logging.INFO) # logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
from IPython.display import Markdown, display

```

from IPython.display import Markdown, display
### Create Database Schema¶
We use `sqlalchemy`, a popular SQL database toolkit, to create an empty `city_stats` Table
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
)

```

from sqlalchemy import ( create_engine, MetaData, Table, Column, String, Integer, select, )
In [ ]:
Copied!
```
engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()

```

engine = create_engine("sqlite:///:memory:") metadata_obj = MetaData()
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
### Define SQL Database¶
We first define our `SQLDatabase` abstraction (a light wrapper around SQLAlchemy).
In [ ]:
Copied!
```
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI

```

from llama_index.core import SQLDatabase from llama_index.llms.openai import OpenAI
In [ ]:
Copied!
```
llm = OpenAI(temperature=0.1, model="gpt-4.1-mini")

```

llm = OpenAI(temperature=0.1, model="gpt-4.1-mini")
In [ ]:
Copied!
```
sql_database = SQLDatabase(engine, include_tables=["city_stats"])

```

sql_database = SQLDatabase(engine, include_tables=["city_stats"])
We add some testing data to our SQL database.
In [ ]:
Copied!
```
from sqlalchemy import insert

sql_database = SQLDatabase(engine, include_tables=["city_stats"])

rows = [
    {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
    {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
    {
        "city_name": "Chicago",
        "population": 2679000,
        "country": "United States",
    },
    {
        "city_name": "New York",
        "population": 8258000,
        "country": "United States",
    },
    {"city_name": "Seoul", "population": 9776000, "country": "South Korea"},
    {"city_name": "Busan", "population": 3334000, "country": "South Korea"},
]
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

```

from sqlalchemy import insert sql_database = SQLDatabase(engine, include_tables=["city_stats"]) rows = [ {"city_name": "Toronto", "population": 2930000, "country": "Canada"}, {"city_name": "Tokyo", "population": 13960000, "country": "Japan"}, { "city_name": "Chicago", "population": 2679000, "country": "United States", }, { "city_name": "New York", "population": 8258000, "country": "United States", }, {"city_name": "Seoul", "population": 9776000, "country": "South Korea"}, {"city_name": "Busan", "population": 3334000, "country": "South Korea"}, ] for row in rows: stmt = insert(city_stats_table).values(**row) with engine.begin() as connection: cursor = connection.execute(stmt)
In [ ]:
Copied!
```
# view current table
stmt = select(
    city_stats_table.c.city_name,
    city_stats_table.c.population,
    city_stats_table.c.country,
).select_from(city_stats_table)

with engine.connect() as connection:
    results = connection.execute(stmt).fetchall()
    print(results)

```

# view current table stmt = select( city_stats_table.c.city_name, city_stats_table.c.population, city_stats_table.c.country, ).select_from(city_stats_table) with engine.connect() as connection: results = connection.execute(stmt).fetchall() print(results)
```
[('Toronto', 2930000, 'Canada'), ('Tokyo', 13960000, 'Japan'), ('Chicago', 2679000, 'United States'), ('New York', 8258000, 'United States'), ('Seoul', 9776000, 'South Korea'), ('Busan', 3334000, 'South Korea')]

```

### Query Index¶
We first show how we can execute a raw SQL query, which directly executes over the table.
In [ ]:
Copied!
```
from sqlalchemy import text

with engine.connect() as con:
    rows = con.execute(text("SELECT city_name from city_stats"))
    for row in rows:
        print(row)

```

from sqlalchemy import text with engine.connect() as con: rows = con.execute(text("SELECT city_name from city_stats")) for row in rows: print(row)
```
('Busan',)
('Chicago',)
('New York',)
('Seoul',)
('Tokyo',)
('Toronto',)

```

## Part 1: Text-to-SQL Query Engine¶
Once we have constructed our SQL database, we can use the NLSQLTableQueryEngine to construct natural language queries that are synthesized into SQL queries.
Note that we need to specify the tables we want to use with this query engine. If we don't the query engine will pull all the schema context, which could overflow the context window of the LLM.
In [ ]:
Copied!
```
from llama_index.core.query_engine import NLSQLTableQueryEngine

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=["city_stats"], llm=llm
)
query_str = "Which city has the highest population?"
response = query_engine.query(query_str)

```

from llama_index.core.query_engine import NLSQLTableQueryEngine query_engine = NLSQLTableQueryEngine( sql_database=sql_database, tables=["city_stats"], llm=llm ) query_str = "Which city has the highest population?" response = query_engine.query(query_str)
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
**Tokyo has the highest population among all cities, with a population of 13,960,000.**
This query engine should be used in any case where you can specify the tables you want to query over beforehand, or the total size of all the table schema plus the rest of the prompt fits your context window.
## Part 2: Query-Time Retrieval of Tables for Text-to-SQL¶
If we don't know ahead of time which table we would like to use, and the total size of the table schema overflows your context window size, we should store the table schema in an index so that during query time we can retrieve the right schema.
The way we can do this is using the SQLTableNodeMapping object, which takes in a SQLDatabase and produces a Node object for each SQLTableSchema object passed into the ObjectIndex constructor.
In [ ]:
Copied!
```
from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine,
)
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import VectorStoreIndex
from llama_index.core.embeddings.openai import OpenAIEmbedding

# set Logging to DEBUG for more detailed outputs
table_node_mapping = SQLTableNodeMapping(sql_database)
table_schema_objs = [
    (SQLTableSchema(table_name="city_stats"))
]  # add a SQLTableSchema for each table

obj_index = ObjectIndex.from_objects(
    table_schema_objs,
    table_node_mapping,
    VectorStoreIndex,
    embed_model=OpenAIEmbedding(model="text-embedding-3-small"),
)
query_engine = SQLTableRetrieverQueryEngine(
    sql_database, obj_index.as_retriever(similarity_top_k=1)
)

```

from llama_index.core.indices.struct_store.sql_query import ( SQLTableRetrieverQueryEngine, ) from llama_index.core.objects import ( SQLTableNodeMapping, ObjectIndex, SQLTableSchema, ) from llama_index.core import VectorStoreIndex from llama_index.core.embeddings.openai import OpenAIEmbedding # set Logging to DEBUG for more detailed outputs table_node_mapping = SQLTableNodeMapping(sql_database) table_schema_objs = [ (SQLTableSchema(table_name="city_stats")) ] # add a SQLTableSchema for each table obj_index = ObjectIndex.from_objects( table_schema_objs, table_node_mapping, VectorStoreIndex, embed_model=OpenAIEmbedding(model="text-embedding-3-small"), ) query_engine = SQLTableRetrieverQueryEngine( sql_database, obj_index.as_retriever(similarity_top_k=1) )
Now we can take our SQLTableRetrieverQueryEngine and query it for our response.
In [ ]:
Copied!
```
response = query_engine.query("Which city has the highest population?")
display(Markdown(f"<b>{response}</b>"))

```

response = query_engine.query("Which city has the highest population?") display(Markdown(f"**{response}** "))
**Tokyo has the highest population among all cities, with a population of 13,960,000.**
In [ ]:
Copied!
```
# you can also fetch the raw result from SQLAlchemy!
response.metadata["result"]

```

# you can also fetch the raw result from SQLAlchemy! response.metadata["result"]
Out[ ]:
```
[('Tokyo', 13960000)]
```

You can also add additional context information for each table schema you define.
In [ ]:
Copied!
```
# manually set context text
city_stats_text = (
    "This table gives information regarding the population and country of a"
    " given city.\nThe user will query with codewords, where 'foo' corresponds"
    " to population and 'bar'corresponds to city."
)

table_node_mapping = SQLTableNodeMapping(sql_database)
table_schema_objs = [
    (SQLTableSchema(table_name="city_stats", context_str=city_stats_text))
]

```

# manually set context text city_stats_text = ( "This table gives information regarding the population and country of a" " given city.\nThe user will query with codewords, where 'foo' corresponds" " to population and 'bar'corresponds to city." ) table_node_mapping = SQLTableNodeMapping(sql_database) table_schema_objs = [ (SQLTableSchema(table_name="city_stats", context_str=city_stats_text)) ]
## Part 3: Query-Time Retrieval of Rows and Columns for Text-to-SQL¶
One challenge arises when asking a question like: "How many cities are in the US?" In such cases, the generated query might only look for cities where the country is listed as "US," potentially missing entries labeled "United States." To address this issue, you can apply query-time row retrieval, query-time column retrieval, or a combination of both.
### Query-Time Rows Retrieval¶
In query-time rows retrieval, we embed the rows of each table, resulting in one index per table.
In [ ]:
Copied!
```
from llama_index.core.schema import TextNode

with engine.connect() as connection:
    results = connection.execute(stmt).fetchall()

city_nodes = [TextNode(text=str(t)) for t in results]

city_rows_index = VectorStoreIndex(
    city_nodes, embed_model=OpenAIEmbedding(model="text-embedding-3-small")
)
city_rows_retriever = city_rows_index.as_retriever(similarity_top_k=1)

city_rows_retriever.retrieve("US")

```

from llama_index.core.schema import TextNode with engine.connect() as connection: results = connection.execute(stmt).fetchall() city_nodes = [TextNode(text=str(t)) for t in results] city_rows_index = VectorStoreIndex( city_nodes, embed_model=OpenAIEmbedding(model="text-embedding-3-small") ) city_rows_retriever = city_rows_index.as_retriever(similarity_top_k=1) city_rows_retriever.retrieve("US")
Out[ ]:
```
[NodeWithScore(node=TextNode(id_='8ae10176-afd8-40ee-a97b-b24f66235489', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, metadata_template='{key}: {value}', metadata_separator='\n', text="('Chicago', 2679000, 'United States')", mimetype='text/plain', start_char_idx=None, end_char_idx=None, metadata_seperator='\n', text_template='{metadata_str}\n\n{content}'), score=0.7843469586763699)]
```

Then, the rows retriever of each table can be provided to the SQLTableRetrieverQueryEngine.
In [ ]:
Copied!
```
rows_retrievers = {
    "city_stats": city_rows_retriever,
}
query_engine = SQLTableRetrieverQueryEngine(
    sql_database,
    obj_index.as_retriever(similarity_top_k=1),
    rows_retrievers=rows_retrievers,
)

```

rows_retrievers = { "city_stats": city_rows_retriever, } query_engine = SQLTableRetrieverQueryEngine( sql_database, obj_index.as_retriever(similarity_top_k=1), rows_retrievers=rows_retrievers, )
During querying, the row retrievers are used to identify the rows most semantically similar to the input query. These retrieved rows are then incorporated as context to enhance the performance of the text-to-SQL generation.
In [ ]:
Copied!
```
response = query_engine.query("How many cities are in the US?")

```

response = query_engine.query("How many cities are in the US?")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
**There are 2 cities in the United States according to the data in the city_stats table.**
### Query-Time Columns Retrieval¶
While query-time row retrieval enhances text-to-SQL generation, it embeds each row individually, even when many rows share repeated values—such as those in categorical. This can lead to token inefficiency and unnecessary overhead. Moreover, in tables with a large number of columns, the retriever may surface only a subset of relevant values, potentially omitting others that are important for accurate query generation.
To address this issue, query-time column retrieval can be used. This approach indexes each distinct value within selected columns, creating a separate index for each column in the table.
In [ ]:
Copied!
```
city_cols_retrievers = {}

for column_name in ["city_name", "country"]:
    stmt = select(city_stats_table.c[column_name]).distinct()
    with engine.connect() as connection:
        values = connection.execute(stmt).fetchall()
    nodes = [TextNode(text=t[0]) for t in values]

    column_index = VectorStoreIndex(
        nodes, embed_model=OpenAIEmbedding(model="text-embedding-3-small")
    )
    column_retriever = column_index.as_retriever(similarity_top_k=1)

    city_cols_retrievers[column_name] = column_retriever

```

city_cols_retrievers = {} for column_name in ["city_name", "country"]: stmt = select(city_stats_table.c[column_name]).distinct() with engine.connect() as connection: values = connection.execute(stmt).fetchall() nodes = [TextNode(text=t[0]) for t in values] column_index = VectorStoreIndex( nodes, embed_model=OpenAIEmbedding(model="text-embedding-3-small") ) column_retriever = column_index.as_retriever(similarity_top_k=1) city_cols_retrievers[column_name] = column_retriever
Then, columns retrievers of each table can be provided to the SQLTableRetrieverQueryEngine.
In [ ]:
Copied!
```
cols_retrievers = {
    "city_stats": city_cols_retrievers,
}
query_engine = SQLTableRetrieverQueryEngine(
    sql_database,
    obj_index.as_retriever(similarity_top_k=1),
    rows_retrievers=rows_retrievers,
    cols_retrievers=cols_retrievers,
    llm=llm,
)

```

cols_retrievers = { "city_stats": city_cols_retrievers, } query_engine = SQLTableRetrieverQueryEngine( sql_database, obj_index.as_retriever(similarity_top_k=1), rows_retrievers=rows_retrievers, cols_retrievers=cols_retrievers, llm=llm, )
During querying, the columns retrievers are used to identify the values of columns that are the most semantically similar to the input query. These retrieved values are then incorporated as context to enhance the performance of the text-to-SQL generation.
In [ ]:
Copied!
```
response = query_engine.query("How many cities are in the US?")

```

response = query_engine.query("How many cities are in the US?")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
**There are 2 cities in the United States.**
## Part 4: Text-to-SQL Retriever¶
So far our text-to-SQL capability is packaged in a query engine and consists of both retrieval and synthesis.
You can use the SQL retriever on its own. We show you some different parameters you can try, and also show how to plug it into our `RetrieverQueryEngine` to get roughly the same results.
In [ ]:
Copied!
```
from llama_index.core.retrievers import NLSQLRetriever

# default retrieval (return_raw=True)
nl_sql_retriever = NLSQLRetriever(
    sql_database, tables=["city_stats"], llm=llm, return_raw=True
)

```

from llama_index.core.retrievers import NLSQLRetriever # default retrieval (return_raw=True) nl_sql_retriever = NLSQLRetriever( sql_database, tables=["city_stats"], llm=llm, return_raw=True )
In [ ]:
Copied!
```
results = nl_sql_retriever.retrieve(
    "Return the top 5 cities (along with their populations) with the highest population."
)

```

results = nl_sql_retriever.retrieve( "Return the top 5 cities (along with their populations) with the highest population." )
In [ ]:
Copied!
```
from llama_index.core.response.notebook_utils import display_source_node

for n in results:
    display_source_node(n)

```

from llama_index.core.response.notebook_utils import display_source_node for n in results: display_source_node(n)
**Node ID:** f640a54f-7413-4dc0-9135-cd63c7ca8f45  
**Similarity:** None  
**Text:** [('Tokyo', 13960000), ('Seoul', 9776000), ('New York', 8258000), ('Busan', 3334000), ('Toronto', ...  

In [ ]:
Copied!
```
# default retrieval (return_raw=False)
nl_sql_retriever = NLSQLRetriever(
    sql_database, tables=["city_stats"], return_raw=False
)

```

# default retrieval (return_raw=False) nl_sql_retriever = NLSQLRetriever( sql_database, tables=["city_stats"], return_raw=False )
In [ ]:
Copied!
```
results = nl_sql_retriever.retrieve(
    "Return the top 5 cities (along with their populations) with the highest population."
)

```

results = nl_sql_retriever.retrieve( "Return the top 5 cities (along with their populations) with the highest population." )
In [ ]:
Copied!
```
# NOTE: all the content is in the metadata
for n in results:
    display_source_node(n, show_source_metadata=True)

```

# NOTE: all the content is in the metadata for n in results: display_source_node(n, show_source_metadata=True)
**Node ID:** 05c61a90-598e-4c29-a6b4-b27f2579819e  
**Similarity:** None  
**Text:**   
**Metadata:** {'city_name': 'Tokyo', 'population': 13960000}  

**Node ID:** c7f5fc4c-9754-4946-92c6-54a0d2b40fd9  
**Similarity:** None  
**Text:**   
**Metadata:** {'city_name': 'Seoul', 'population': 9776000}  

**Node ID:** 3a00e201-f3b5-430e-af0e-aa4c34a71131  
**Similarity:** None  
**Text:**   
**Metadata:** {'city_name': 'New York', 'population': 8258000}  

**Node ID:** ee911f7f-8aae-4bad-a52d-c0bdfab63942  
**Similarity:** None  
**Text:**   
**Metadata:** {'city_name': 'Busan', 'population': 3334000}  

**Node ID:** dca6b482-52e4-41e0-992f-a58109e6f3f6  
**Similarity:** None  
**Text:**   
**Metadata:** {'city_name': 'Toronto', 'population': 2930000}  

### Plug into our `RetrieverQueryEngine`¶
We compose our SQL Retriever with our standard `RetrieverQueryEngine` to synthesize a response. The result is roughly similar to our packaged `Text-to-SQL` query engines.
In [ ]:
Copied!
```
from llama_index.core.query_engine import RetrieverQueryEngine

query_engine = RetrieverQueryEngine.from_args(nl_sql_retriever, llm=llm)

```

from llama_index.core.query_engine import RetrieverQueryEngine query_engine = RetrieverQueryEngine.from_args(nl_sql_retriever, llm=llm)
In [ ]:
Copied!
```
response = query_engine.query(
    "Return the top 5 cities (along with their populations) with the highest population."
)

```

response = query_engine.query( "Return the top 5 cities (along with their populations) with the highest population." )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The top 5 cities with the highest populations are:

1. Tokyo - 13,960,000
2. Seoul - 9,776,000
3. New York - 8,258,000
4. Busan - 3,334,000
5. Toronto - 2,930,000

```

