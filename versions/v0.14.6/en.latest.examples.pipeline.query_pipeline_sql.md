# Query Pipeline for Advanced Text-to-SQL¶
In this guide we show you how to setup a text-to-SQL pipeline over your data with our query pipeline syntax.
This gives you flexibility to enhance text-to-SQL with additional techniques. We show these in the below sections:
  1. **Query-Time Table Retrieval** : Dynamically retrieve relevant tables in the text-to-SQL prompt.
  2. **Query-Time Sample Row retrieval** : Embed/Index each row, and dynamically retrieve example rows for each table in the text-to-SQL prompt.


Our out-of-the box pipelines include our `NLSQLTableQueryEngine` and `SQLTableRetrieverQueryEngine`. (if you want to check out our text-to-SQL guide using these modules, take a look here). This guide implements an advanced version of those modules, giving you the utmost flexibility to apply this to your own setting.
**NOTE:** Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
## Load and Ingest Data¶
### Load Data¶
We use the WikiTableQuestions dataset (Pasupat and Liang 2015) as our test dataset.
We go through all the csv's in one folder, store each in a sqlite database (we will then build an object index over each table schema).
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!wget "https://github.com/ppasupat/WikiTableQuestions/releases/download/v1.0.2/WikiTableQuestions-1.0.2-compact.zip" -O data.zip
!unzip data.zip

```

!wget "https://github.com/ppasupat/WikiTableQuestions/releases/download/v1.0.2/WikiTableQuestions-1.0.2-compact.zip" -O data.zip !unzip data.zip
In [ ]:
Copied!
```
import pandas as pd
from pathlib import Path

data_dir = Path("./WikiTableQuestions/csv/200-csv")
csv_files = sorted([f for f in data_dir.glob("*.csv")])
dfs = []
for csv_file in csv_files:
    print(f"processing file: {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        dfs.append(df)
    except Exception as e:
        print(f"Error parsing {csv_file}: {str(e)}")

```

import pandas as pd from pathlib import Path data_dir = Path("./WikiTableQuestions/csv/200-csv") csv_files = sorted([f for f in data_dir.glob("*.csv")]) dfs = [] for csv_file in csv_files: print(f"processing file: {csv_file}") try: df = pd.read_csv(csv_file) dfs.append(df) except Exception as e: print(f"Error parsing {csv_file}: {str(e)}")
### Extract Table Name and Summary from each Table¶
Here we use gpt-3.5 to extract a table name (with underscores) and summary from each table with our Pydantic program.
In [ ]:
Copied!
```
tableinfo_dir = "WikiTableQuestions_TableInfo"
!mkdir {tableinfo_dir}

```

tableinfo_dir = "WikiTableQuestions_TableInfo" !mkdir {tableinfo_dir}
In [ ]:
Copied!
```
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI


class TableInfo(BaseModel):
    """Information regarding a structured table."""

    table_name: str = Field(
        ..., description="table name (must be underscores and NO spaces)"
    )
    table_summary: str = Field(
        ..., description="short, concise summary/caption of the table"
    )


prompt_str = """\
Give me a summary of the table with the following JSON format.

- The table name must be unique to the table and describe it while being concise. 
- Do NOT output a generic table name (e.g. table, my_table).

Do NOT make the table name one of the following: {exclude_table_name_list}

Table:
{table_str}

Summary: """

program = LLMTextCompletionProgram.from_defaults(
    output_cls=TableInfo,
    llm=OpenAI(model="gpt-3.5-turbo"),
    prompt_template_str=prompt_str,
)

```

from llama_index.core.program import LLMTextCompletionProgram from llama_index.core.bridge.pydantic import BaseModel, Field from llama_index.llms.openai import OpenAI class TableInfo(BaseModel): """Information regarding a structured table.""" table_name: str = Field( ..., description="table name (must be underscores and NO spaces)" ) table_summary: str = Field( ..., description="short, concise summary/caption of the table" ) prompt_str = """\ Give me a summary of the table with the following JSON format. - The table name must be unique to the table and describe it while being concise. - Do NOT output a generic table name (e.g. table, my_table). Do NOT make the table name one of the following: {exclude_table_name_list} Table: {table_str} Summary: """ program = LLMTextCompletionProgram.from_defaults( output_cls=TableInfo, llm=OpenAI(model="gpt-3.5-turbo"), prompt_template_str=prompt_str, )
In [ ]:
Copied!
```
import json


def _get_tableinfo_with_index(idx: int) -> str:
    results_gen = Path(tableinfo_dir).glob(f"{idx}_*")
    results_list = list(results_gen)
    if len(results_list) == 0:
        return None
    elif len(results_list) == 1:
        path = results_list[0]
        return TableInfo.parse_file(path)
    else:
        raise ValueError(
            f"More than one file matching index: {list(results_gen)}"
        )


table_names = set()
table_infos = []
for idx, df in enumerate(dfs):
    table_info = _get_tableinfo_with_index(idx)
    if table_info:
        table_infos.append(table_info)
    else:
        while True:
            df_str = df.head(10).to_csv()
            table_info = program(
                table_str=df_str,
                exclude_table_name_list=str(list(table_names)),
            )
            table_name = table_info.table_name
            print(f"Processed table: {table_name}")
            if table_name not in table_names:
                table_names.add(table_name)
                break
            else:
                # try again
                print(f"Table name {table_name} already exists, trying again.")
                pass

        out_file = f"{tableinfo_dir}/{idx}_{table_name}.json"
        json.dump(table_info.dict(), open(out_file, "w"))
    table_infos.append(table_info)

```

import json def _get_tableinfo_with_index(idx: int) -> str: results_gen = Path(tableinfo_dir).glob(f"{idx}_*") results_list = list(results_gen) if len(results_list) == 0: return None elif len(results_list) == 1: path = results_list[0] return TableInfo.parse_file(path) else: raise ValueError( f"More than one file matching index: {list(results_gen)}" ) table_names = set() table_infos = [] for idx, df in enumerate(dfs): table_info = _get_tableinfo_with_index(idx) if table_info: table_infos.append(table_info) else: while True: df_str = df.head(10).to_csv() table_info = program( table_str=df_str, exclude_table_name_list=str(list(table_names)), ) table_name = table_info.table_name print(f"Processed table: {table_name}") if table_name not in table_names: table_names.add(table_name) break else: # try again print(f"Table name {table_name} already exists, trying again.") pass out_file = f"{tableinfo_dir}/{idx}_{table_name}.json" json.dump(table_info.dict(), open(out_file, "w")) table_infos.append(table_info)
### Put Data in SQL Database¶
We use `sqlalchemy`, a popular SQL database toolkit, to load all the tables.
In [ ]:
Copied!
```
# put data into sqlite db
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
)
import re


# Function to create a sanitized column name
def sanitize_column_name(col_name):
    # Remove special characters and replace spaces with underscores
    return re.sub(r"\W+", "_", col_name)


# Function to create a table from a DataFrame using SQLAlchemy
def create_table_from_dataframe(
    df: pd.DataFrame, table_name: str, engine, metadata_obj
):
    # Sanitize column names
    sanitized_columns = {col: sanitize_column_name(col) for col in df.columns}
    df = df.rename(columns=sanitized_columns)

    # Dynamically create columns based on DataFrame columns and data types
    columns = [
        Column(col, String if dtype == "object" else Integer)
        for col, dtype in zip(df.columns, df.dtypes)
    ]

    # Create a table with the defined columns
    table = Table(table_name, metadata_obj, *columns)

    # Create the table in the database
    metadata_obj.create_all(engine)

    # Insert data from DataFrame into the table
    with engine.connect() as conn:
        for _, row in df.iterrows():
            insert_stmt = table.insert().values(**row.to_dict())
            conn.execute(insert_stmt)
        conn.commit()


engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()
for idx, df in enumerate(dfs):
    tableinfo = _get_tableinfo_with_index(idx)
    print(f"Creating table: {tableinfo.table_name}")
    create_table_from_dataframe(df, tableinfo.table_name, engine, metadata_obj)

```

# put data into sqlite db from sqlalchemy import ( create_engine, MetaData, Table, Column, String, Integer, ) import re # Function to create a sanitized column name def sanitize_column_name(col_name): # Remove special characters and replace spaces with underscores return re.sub(r"\W+", "_", col_name) # Function to create a table from a DataFrame using SQLAlchemy def create_table_from_dataframe( df: pd.DataFrame, table_name: str, engine, metadata_obj ): # Sanitize column names sanitized_columns = {col: sanitize_column_name(col) for col in df.columns} df = df.rename(columns=sanitized_columns) # Dynamically create columns based on DataFrame columns and data types columns = [ Column(col, String if dtype == "object" else Integer) for col, dtype in zip(df.columns, df.dtypes) ] # Create a table with the defined columns table = Table(table_name, metadata_obj, *columns) # Create the table in the database metadata_obj.create_all(engine) # Insert data from DataFrame into the table with engine.connect() as conn: for _, row in df.iterrows(): insert_stmt = table.insert().values(**row.to_dict()) conn.execute(insert_stmt) conn.commit() engine = create_engine("sqlite:///:memory:") metadata_obj = MetaData() for idx, df in enumerate(dfs): tableinfo = _get_tableinfo_with_index(idx) print(f"Creating table: {tableinfo.table_name}") create_table_from_dataframe(df, tableinfo.table_name, engine, metadata_obj)
In [ ]:
Copied!
```
# setup Arize Phoenix for logging/observability
import phoenix as px
import llama_index.core

px.launch_app()
llama_index.core.set_global_handler("arize_phoenix")

```

# setup Arize Phoenix for logging/observability import phoenix as px import llama_index.core px.launch_app() llama_index.core.set_global_handler("arize_phoenix")
```
🌍 To view the Phoenix app in your browser, visit http://127.0.0.1:6006/
📺 To view the Phoenix app in a notebook, run `px.active_session().view()`
📖 For more information on how to use Phoenix, check out https://docs.arize.com/phoenix

```

## Advanced Capability 1: Text-to-SQL with Query-Time Table Retrieval.¶
We now show you how to setup an e2e text-to-SQL with table retrieval.
### Define Modules¶
Here we define the core modules.
  1. Object index + retriever to store table schemas
  2. SQLDatabase object to connect to the above tables + SQLRetriever.
  3. Text-to-SQL Prompt
  4. Response synthesis Prompt
  5. LLM


Object index, retriever, SQLDatabase
In [ ]:
Copied!
```
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core import SQLDatabase, VectorStoreIndex

sql_database = SQLDatabase(engine)

table_node_mapping = SQLTableNodeMapping(sql_database)
table_schema_objs = [
    SQLTableSchema(table_name=t.table_name, context_str=t.table_summary)
    for t in table_infos
]  # add a SQLTableSchema for each table

obj_index = ObjectIndex.from_objects(
    table_schema_objs,
    table_node_mapping,
    VectorStoreIndex,
)
obj_retriever = obj_index.as_retriever(similarity_top_k=3)

```

from llama_index.core.objects import ( SQLTableNodeMapping, ObjectIndex, SQLTableSchema, ) from llama_index.core import SQLDatabase, VectorStoreIndex sql_database = SQLDatabase(engine) table_node_mapping = SQLTableNodeMapping(sql_database) table_schema_objs = [ SQLTableSchema(table_name=t.table_name, context_str=t.table_summary) for t in table_infos ] # add a SQLTableSchema for each table obj_index = ObjectIndex.from_objects( table_schema_objs, table_node_mapping, VectorStoreIndex, ) obj_retriever = obj_index.as_retriever(similarity_top_k=3)
SQLRetriever + Table Parser
In [ ]:
Copied!
```
from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.query_pipeline import FnComponent

sql_retriever = SQLRetriever(sql_database)


def get_table_context_str(table_schema_objs: List[SQLTableSchema]):
    """Get table context string."""
    context_strs = []
    for table_schema_obj in table_schema_objs:
        table_info = sql_database.get_single_table_info(
            table_schema_obj.table_name
        )
        if table_schema_obj.context_str:
            table_opt_context = " The table description is: "
            table_opt_context += table_schema_obj.context_str
            table_info += table_opt_context

        context_strs.append(table_info)
    return "\n\n".join(context_strs)


table_parser_component = FnComponent(fn=get_table_context_str)

```

from llama_index.core.retrievers import SQLRetriever from typing import List from llama_index.core.query_pipeline import FnComponent sql_retriever = SQLRetriever(sql_database) def get_table_context_str(table_schema_objs: List[SQLTableSchema]): """Get table context string.""" context_strs = [] for table_schema_obj in table_schema_objs: table_info = sql_database.get_single_table_info( table_schema_obj.table_name ) if table_schema_obj.context_str: table_opt_context = " The table description is: " table_opt_context += table_schema_obj.context_str table_info += table_opt_context context_strs.append(table_info) return "\n\n".join(context_strs) table_parser_component = FnComponent(fn=get_table_context_str)
Text-to-SQL Prompt + Output Parser
In [ ]:
Copied!
```
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core import PromptTemplate
from llama_index.core.query_pipeline import FnComponent
from llama_index.core.llms import ChatResponse


def parse_response_to_sql(response: ChatResponse) -> str:
    """Parse response to SQL."""
    response = response.message.content
    sql_query_start = response.find("SQLQuery:")
    if sql_query_start != -1:
        response = response[sql_query_start:]
        # TODO: move to removeprefix after Python 3.9+
        if response.startswith("SQLQuery:"):
            response = response[len("SQLQuery:") :]
    sql_result_start = response.find("SQLResult:")
    if sql_result_start != -1:
        response = response[:sql_result_start]
    return response.strip().strip("```").strip()


sql_parser_component = FnComponent(fn=parse_response_to_sql)

text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
    dialect=engine.dialect.name
)
print(text2sql_prompt.template)

```

from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT from llama_index.core import PromptTemplate from llama_index.core.query_pipeline import FnComponent from llama_index.core.llms import ChatResponse def parse_response_to_sql(response: ChatResponse) -> str: """Parse response to SQL.""" response = response.message.content sql_query_start = response.find("SQLQuery:") if sql_query_start != -1: response = response[sql_query_start:] # TODO: move to removeprefix after Python 3.9+ if response.startswith("SQLQuery:"): response = response[len("SQLQuery:") :] sql_result_start = response.find("SQLResult:") if sql_result_start != -1: response = response[:sql_result_start] return response.strip().strip("```").strip() sql_parser_component = FnComponent(fn=parse_response_to_sql) text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format( dialect=engine.dialect.name ) print(text2sql_prompt.template)
```
Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer. You can order the results by a relevant column to return the most interesting examples in the database.

Never query for all the columns from a specific table, only ask for a few relevant columns given the question.

Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Pay attention to which column is in which table. Also, qualify column names with the table name when needed. You are required to use the following format, each taking one line:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

Only use tables listed below.
{schema}

Question: {query_str}
SQLQuery: 

```

Response Synthesis Prompt
In [ ]:
Copied!
```
response_synthesis_prompt_str = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n"
    "SQL: {sql_query}\n"
    "SQL Response: {context_str}\n"
    "Response: "
)
response_synthesis_prompt = PromptTemplate(
    response_synthesis_prompt_str,
)

```

response_synthesis_prompt_str = ( "Given an input question, synthesize a response from the query results.\n" "Query: {query_str}\n" "SQL: {sql_query}\n" "SQL Response: {context_str}\n" "Response: " ) response_synthesis_prompt = PromptTemplate( response_synthesis_prompt_str, )
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-3.5-turbo")

```

llm = OpenAI(model="gpt-3.5-turbo")
### Define Query Pipeline¶
Now that the components are in place, let's define the query pipeline!
In [ ]:
Copied!
```
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
    CustomQueryComponent,
)

qp = QP(
    modules={
        "input": InputComponent(),
        "table_retriever": obj_retriever,
        "table_output_parser": table_parser_component,
        "text2sql_prompt": text2sql_prompt,
        "text2sql_llm": llm,
        "sql_output_parser": sql_parser_component,
        "sql_retriever": sql_retriever,
        "response_synthesis_prompt": response_synthesis_prompt,
        "response_synthesis_llm": llm,
    },
    verbose=True,
)

```

from llama_index.core.query_pipeline import ( QueryPipeline as QP, Link, InputComponent, CustomQueryComponent, ) qp = QP( modules={ "input": InputComponent(), "table_retriever": obj_retriever, "table_output_parser": table_parser_component, "text2sql_prompt": text2sql_prompt, "text2sql_llm": llm, "sql_output_parser": sql_parser_component, "sql_retriever": sql_retriever, "response_synthesis_prompt": response_synthesis_prompt, "response_synthesis_llm": llm, }, verbose=True, )
In [ ]:
Copied!
```
qp.add_chain(["input", "table_retriever", "table_output_parser"])
qp.add_link("input", "text2sql_prompt", dest_key="query_str")
qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
qp.add_chain(
    ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"]
)
qp.add_link(
    "sql_output_parser", "response_synthesis_prompt", dest_key="sql_query"
)
qp.add_link(
    "sql_retriever", "response_synthesis_prompt", dest_key="context_str"
)
qp.add_link("input", "response_synthesis_prompt", dest_key="query_str")
qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

```

qp.add_chain(["input", "table_retriever", "table_output_parser"]) qp.add_link("input", "text2sql_prompt", dest_key="query_str") qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema") qp.add_chain( ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"] ) qp.add_link( "sql_output_parser", "response_synthesis_prompt", dest_key="sql_query" ) qp.add_link( "sql_retriever", "response_synthesis_prompt", dest_key="context_str" ) qp.add_link("input", "response_synthesis_prompt", dest_key="query_str") qp.add_link("response_synthesis_prompt", "response_synthesis_llm")
### Visualize Query Pipeline¶
A really nice property of the query pipeline syntax is you can easily visualize it in a graph via networkx.
In [ ]:
Copied!
```
from pyvis.network import Network

net = Network(notebook=True, cdn_resources="in_line", directed=True)
net.from_nx(qp.dag)

```

from pyvis.network import Network net = Network(notebook=True, cdn_resources="in_line", directed=True) net.from_nx(qp.dag)
In [ ]:
Copied!
```
# Save the network as "text2sql_dag.html"
net.write_html("text2sql_dag.html")

```

# Save the network as "text2sql_dag.html" net.write_html("text2sql_dag.html")
In [ ]:
Copied!
```
from IPython.display import display, HTML

# Read the contents of the HTML file
with open("text2sql_dag.html", "r") as file:
    html_content = file.read()

# Display the HTML content
display(HTML(html_content))

```

from IPython.display import display, HTML # Read the contents of the HTML file with open("text2sql_dag.html", "r") as file: html_content = file.read() # Display the HTML content display(HTML(html_content))
### Run Some Queries!¶
Now we're ready to run some queries across this entire pipeline.
In [ ]:
Copied!
```
response = qp.run(
    query="What was the year that The Notorious B.I.G was signed to Bad Boy?"
)
print(str(response))

```

response = qp.run( query="What was the year that The Notorious B.I.G was signed to Bad Boy?" ) print(str(response))
```
> Running module input with input: 
query: What was the year that The Notorious B.I.G was signed to Bad Boy?

> Running module table_retriever with input: 
input: What was the year that The Notorious B.I.G was signed to Bad Boy?

> Running module table_output_parser with input: 
table_schema_objs: [SQLTableSchema(table_name='Bad_Boy_Artists', context_str='List of artists signed to Bad Boy Records and their album releases'), SQLTableSchema(table_name='Bad_Boy_Artists', context_str='List of artis...

> Running module text2sql_prompt with input: 
query_str: What was the year that The Notorious B.I.G was signed to Bad Boy?
schema: Table 'Bad_Boy_Artists' has columns: Act (VARCHAR), Year_signed (INTEGER), _Albums_released_under_Bad_Boy (VARCHAR), and foreign keys: . The table description is: List of artists signed to Bad Boy Rec...

> Running module text2sql_llm with input: 
messages: Given an input question, first create a syntactically correct sqlite query to run, then look at the results of the query and return the answer. You can order the results by a relevant column to return...

> Running module sql_output_parser with input: 
response: assistant: SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = 'The Notorious B.I.G'
SQLResult: 1993
Answer: The Notorious B.I.G was signed to Bad Boy in 1993.

RAW RESPONSE  SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = 'The Notorious B.I.G'
SQLResult: 1993
Answer: The Notorious B.I.G was signed to Bad Boy in 1993.
> Running module sql_retriever with input: 
input: SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = 'The Notorious B.I.G'

> Running module response_synthesis_prompt with input: 
query_str: What was the year that The Notorious B.I.G was signed to Bad Boy?
sql_query: SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = 'The Notorious B.I.G'
context_str: [NodeWithScore(node=TextNode(id_='4ae2f8fc-b803-4238-8433-7a431c2df391', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, hash='c336a1cbf9...

> Running module response_synthesis_llm with input: 
messages: Given an input question, synthesize a response from the query results.
Query: What was the year that The Notorious B.I.G was signed to Bad Boy?
SQL: SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act =...

assistant: The Notorious B.I.G was signed to Bad Boy in 1993.

```

In [ ]:
Copied!
```
response = qp.run(query="Who won best director in the 1972 academy awards")
print(str(response))

```

response = qp.run(query="Who won best director in the 1972 academy awards") print(str(response))
```
> Running module input with input: 
query: Who won best directory in the 1972 academy awards

> Running module table_retriever with input: 
input: Who won best directory in the 1972 academy awards

> Running module table_output_parser with input: 
table_schema_objs: [SQLTableSchema(table_name='Academy_Awards_1972', context_str='List of award categories and nominees for the 1972 Academy Awards'), SQLTableSchema(table_name='Academy_Awards_1972', context_str='List o...

> Running module text2sql_prompt with input: 
query_str: Who won best directory in the 1972 academy awards
schema: Table 'Academy_Awards_1972' has columns: Award (VARCHAR), Category (VARCHAR), Nominee (VARCHAR), Result (VARCHAR), and foreign keys: . The table description is: List of award categories and nominees f...

> Running module text2sql_llm with input: 
messages: Given an input question, first create a syntactically correct sqlite query to run, then look at the results of the query and return the answer. You can order the results by a relevant column to return...

> Running module sql_output_parser with input: 
response: assistant: SELECT Nominee
FROM Academy_Awards_1972
WHERE Category = 'Best Director' AND Result = 'Won'
SQLResult: The result of the SQLQuery will be the name of the director who won the Best Director ...

RAW RESPONSE  SELECT Nominee
FROM Academy_Awards_1972
WHERE Category = 'Best Director' AND Result = 'Won'
SQLResult: The result of the SQLQuery will be the name of the director who won the Best Director award in the 1972 Academy Awards.
Answer: The winner of the Best Director award in the 1972 Academy Awards was [Director's Name].
> Running module sql_retriever with input: 
input: SELECT Nominee
FROM Academy_Awards_1972
WHERE Category = 'Best Director' AND Result = 'Won'

> Running module response_synthesis_prompt with input: 
query_str: Who won best directory in the 1972 academy awards
sql_query: SELECT Nominee
FROM Academy_Awards_1972
WHERE Category = 'Best Director' AND Result = 'Won'
context_str: [NodeWithScore(node=TextNode(id_='2ebd2cb3-7836-4f93-9898-4c0798da4a41', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, hash='a74ca5f33c...

> Running module response_synthesis_llm with input: 
messages: Given an input question, synthesize a response from the query results.
Query: Who won best directory in the 1972 academy awards
SQL: SELECT Nominee
FROM Academy_Awards_1972
WHERE Category = 'Best Dire...

assistant: The winner for Best Director in the 1972 Academy Awards was William Friedkin.

```

In [ ]:
Copied!
```
response = qp.run(query="What was the term of Pasquale Preziosa?")
print(str(response))

```

response = qp.run(query="What was the term of Pasquale Preziosa?") print(str(response))
```
> Running module input with input: 
query: What was the term of Pasquale Preziosa?

> Running module table_retriever with input: 
input: What was the term of Pasquale Preziosa?

> Running module table_output_parser with input: 
table_schema_objs: [SQLTableSchema(table_name='Italian_Presidents', context_str='List of Italian Presidents and their terms in office'), SQLTableSchema(table_name='Italian_Presidents', context_str='List of Italian Presi...

> Running module text2sql_prompt with input: 
query_str: What was the term of Pasquale Preziosa?
schema: Table 'Italian_Presidents' has columns: Name (VARCHAR), Term_start (VARCHAR), Term_end (VARCHAR), and foreign keys: . The table description is: List of Italian Presidents and their terms in office

Ta...

> Running module text2sql_llm with input: 
messages: Given an input question, first create a syntactically correct sqlite query to run, then look at the results of the query and return the answer. You can order the results by a relevant column to return...

> Running module sql_output_parser with input: 
response: assistant: SELECT Term_start, Term_end
FROM Italian_Presidents
WHERE Name = 'Pasquale Preziosa'
SQLResult: Term_start = '2006-05-18', Term_end = '2006-05-22'
Answer: Pasquale Preziosa's term was from ...

RAW RESPONSE  SELECT Term_start, Term_end
FROM Italian_Presidents
WHERE Name = 'Pasquale Preziosa'
SQLResult: Term_start = '2006-05-18', Term_end = '2006-05-22'
Answer: Pasquale Preziosa's term was from May 18, 2006 to May 22, 2006.
> Running module sql_retriever with input: 
input: SELECT Term_start, Term_end
FROM Italian_Presidents
WHERE Name = 'Pasquale Preziosa'

> Running module response_synthesis_prompt with input: 
query_str: What was the term of Pasquale Preziosa?
sql_query: SELECT Term_start, Term_end
FROM Italian_Presidents
WHERE Name = 'Pasquale Preziosa'
context_str: [NodeWithScore(node=TextNode(id_='75dfe777-3186-4a57-8969-9e33fb8ab41a', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, hash='99f2d91e91...

> Running module response_synthesis_llm with input: 
messages: Given an input question, synthesize a response from the query results.
Query: What was the term of Pasquale Preziosa?
SQL: SELECT Term_start, Term_end
FROM Italian_Presidents
WHERE Name = 'Pasquale Pr...

assistant: Pasquale Preziosa's term started on 25 February 2013 and he is currently the incumbent.

```

## 2. Advanced Capability 2: Text-to-SQL with Query-Time Row Retrieval (along with Table Retrieval)¶
One problem in the previous example is that if the user asks a query that asks for "The Notorious BIG" but the artist is stored as "The Notorious B.I.G", then the generated SELECT statement will likely not return any matches.
We can alleviate this problem by fetching a small number of example rows per table. A naive option would be to just take the first k rows. Instead, we embed, index, and retrieve k relevant rows given the user query to give the text-to-SQL LLM the most contextually relevant information for SQL generation.
We now extend our query pipeline.
### Index Each Table¶
We embed/index the rows of each table, resulting in one index per table.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, load_index_from_storage
from sqlalchemy import text
from llama_index.core.schema import TextNode
from llama_index.core import StorageContext
import os
from pathlib import Path
from typing import Dict


def index_all_tables(
    sql_database: SQLDatabase, table_index_dir: str = "table_index_dir"
) -> Dict[str, VectorStoreIndex]:
    """Index all tables."""
    if not Path(table_index_dir).exists():
        os.makedirs(table_index_dir)

    vector_index_dict = {}
    engine = sql_database.engine
    for table_name in sql_database.get_usable_table_names():
        print(f"Indexing rows in table: {table_name}")
        if not os.path.exists(f"{table_index_dir}/{table_name}"):
            # get all rows from table
            with engine.connect() as conn:
                cursor = conn.execute(text(f'SELECT * FROM "{table_name}"'))
                result = cursor.fetchall()
                row_tups = []
                for row in result:
                    row_tups.append(tuple(row))

            # index each row, put into vector store index
            nodes = [TextNode(text=str(t)) for t in row_tups]

            # put into vector store index (use OpenAIEmbeddings by default)
            index = VectorStoreIndex(nodes)

            # save index
            index.set_index_id("vector_index")
            index.storage_context.persist(f"{table_index_dir}/{table_name}")
        else:
            # rebuild storage context
            storage_context = StorageContext.from_defaults(
                persist_dir=f"{table_index_dir}/{table_name}"
            )
            # load index
            index = load_index_from_storage(
                storage_context, index_id="vector_index"
            )
        vector_index_dict[table_name] = index

    return vector_index_dict


vector_index_dict = index_all_tables(sql_database)

```

from llama_index.core import VectorStoreIndex, load_index_from_storage from sqlalchemy import text from llama_index.core.schema import TextNode from llama_index.core import StorageContext import os from pathlib import Path from typing import Dict def index_all_tables( sql_database: SQLDatabase, table_index_dir: str = "table_index_dir" ) -> Dict[str, VectorStoreIndex]: """Index all tables.""" if not Path(table_index_dir).exists(): os.makedirs(table_index_dir) vector_index_dict = {} engine = sql_database.engine for table_name in sql_database.get_usable_table_names(): print(f"Indexing rows in table: {table_name}") if not os.path.exists(f"{table_index_dir}/{table_name}"): # get all rows from table with engine.connect() as conn: cursor = conn.execute(text(f'SELECT * FROM "{table_name}"')) result = cursor.fetchall() row_tups = [] for row in result: row_tups.append(tuple(row)) # index each row, put into vector store index nodes = [TextNode(text=str(t)) for t in row_tups] # put into vector store index (use OpenAIEmbeddings by default) index = VectorStoreIndex(nodes) # save index index.set_index_id("vector_index") index.storage_context.persist(f"{table_index_dir}/{table_name}") else: # rebuild storage context storage_context = StorageContext.from_defaults( persist_dir=f"{table_index_dir}/{table_name}" ) # load index index = load_index_from_storage( storage_context, index_id="vector_index" ) vector_index_dict[table_name] = index return vector_index_dict vector_index_dict = index_all_tables(sql_database)
```
Indexing rows in table: Academy_Awards_1972
Indexing rows in table: Actress_Awards
Indexing rows in table: Actress_Awards_Table
Indexing rows in table: Actress_Filmography
Indexing rows in table: Afrikaans_Language_Translations
Indexing rows in table: Airport_Information
Indexing rows in table: Average_Temperature_Precipitation
Indexing rows in table: Average_Temperature_and_Precipitation
Indexing rows in table: BBC_Radio_Costs
Indexing rows in table: Bad_Boy_Artists
Indexing rows in table: Boxing_Matches
Indexing rows in table: Club_Performance_Norway
Indexing rows in table: Disappeared_Persons
Indexing rows in table: Drop Events
Indexing rows in table: European_Football_Standings
Indexing rows in table: Football_Team_Records
Indexing rows in table: Gortynia_Municipalities
Indexing rows in table: Grammy_Awards
Indexing rows in table: Italian_Presidents
Indexing rows in table: Kentucky_Derby_Winners
Indexing rows in table: Kinase_Cancer_Relationships
Indexing rows in table: Kodachrome_Film
Indexing rows in table: New_Mexico_Officials
Indexing rows in table: Number_Encoding_Probability
Indexing rows in table: Peak_Chart_Positions
Indexing rows in table: Political Positions of Lord Beaverbrook
Indexing rows in table: Radio_Stations
Indexing rows in table: Renaissance_Discography
Indexing rows in table: Schools_in_Ohio
Indexing rows in table: Temperature_and_Precipitation
Indexing rows in table: Voter_Party_Statistics
Indexing rows in table: Voter_Registration_Statistics
Indexing rows in table: Yamato_District_Area_Population
Indexing rows in table: Yearly_Deaths_and_Accidents

```

In [ ]:
Copied!
```
test_retriever = vector_index_dict["Bad_Boy_Artists"].as_retriever(
    similarity_top_k=1
)
nodes = test_retriever.retrieve("P. Diddy")
print(nodes[0].get_content())

```

test_retriever = vector_index_dict["Bad_Boy_Artists"].as_retriever( similarity_top_k=1 ) nodes = test_retriever.retrieve("P. Diddy") print(nodes[0].get_content())
```
('Diddy', 1993, '6')

```

### Define Expanded Table Parser Component¶
We expand the capability of our `table_parser_component` to not only return the relevant table schemas, but also return relevant rows per table schema.
It now takes in both `table_schema_objs` (output of table retriever), but also the original `query_str` which will then be used for vector retrieval of relevant rows.
In [ ]:
Copied!
```
from llama_index.core.retrievers import SQLRetriever
from typing import List
from llama_index.core.query_pipeline import FnComponent

sql_retriever = SQLRetriever(sql_database)


def get_table_context_and_rows_str(
    query_str: str, table_schema_objs: List[SQLTableSchema]
):
    """Get table context string."""
    context_strs = []
    for table_schema_obj in table_schema_objs:
        # first append table info + additional context
        table_info = sql_database.get_single_table_info(
            table_schema_obj.table_name
        )
        if table_schema_obj.context_str:
            table_opt_context = " The table description is: "
            table_opt_context += table_schema_obj.context_str
            table_info += table_opt_context

        # also lookup vector index to return relevant table rows
        vector_retriever = vector_index_dict[
            table_schema_obj.table_name
        ].as_retriever(similarity_top_k=2)
        relevant_nodes = vector_retriever.retrieve(query_str)
        if len(relevant_nodes) > 0:
            table_row_context = "\nHere are some relevant example rows (values in the same order as columns above)\n"
            for node in relevant_nodes:
                table_row_context += str(node.get_content()) + "\n"
            table_info += table_row_context

        context_strs.append(table_info)
    return "\n\n".join(context_strs)


table_parser_component = FnComponent(fn=get_table_context_and_rows_str)

```

from llama_index.core.retrievers import SQLRetriever from typing import List from llama_index.core.query_pipeline import FnComponent sql_retriever = SQLRetriever(sql_database) def get_table_context_and_rows_str( query_str: str, table_schema_objs: List[SQLTableSchema] ): """Get table context string.""" context_strs = [] for table_schema_obj in table_schema_objs: # first append table info + additional context table_info = sql_database.get_single_table_info( table_schema_obj.table_name ) if table_schema_obj.context_str: table_opt_context = " The table description is: " table_opt_context += table_schema_obj.context_str table_info += table_opt_context # also lookup vector index to return relevant table rows vector_retriever = vector_index_dict[ table_schema_obj.table_name ].as_retriever(similarity_top_k=2) relevant_nodes = vector_retriever.retrieve(query_str) if len(relevant_nodes) > 0: table_row_context = "\nHere are some relevant example rows (values in the same order as columns above)\n" for node in relevant_nodes: table_row_context += str(node.get_content()) + "\n" table_info += table_row_context context_strs.append(table_info) return "\n\n".join(context_strs) table_parser_component = FnComponent(fn=get_table_context_and_rows_str)
### Define Expanded Query Pipeline¶
This looks similar to the query pipeline in section 1, but with an upgraded table_parser_component.
In [ ]:
Copied!
```
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
    CustomQueryComponent,
)

qp = QP(
    modules={
        "input": InputComponent(),
        "table_retriever": obj_retriever,
        "table_output_parser": table_parser_component,
        "text2sql_prompt": text2sql_prompt,
        "text2sql_llm": llm,
        "sql_output_parser": sql_parser_component,
        "sql_retriever": sql_retriever,
        "response_synthesis_prompt": response_synthesis_prompt,
        "response_synthesis_llm": llm,
    },
    verbose=True,
)

```

from llama_index.core.query_pipeline import ( QueryPipeline as QP, Link, InputComponent, CustomQueryComponent, ) qp = QP( modules={ "input": InputComponent(), "table_retriever": obj_retriever, "table_output_parser": table_parser_component, "text2sql_prompt": text2sql_prompt, "text2sql_llm": llm, "sql_output_parser": sql_parser_component, "sql_retriever": sql_retriever, "response_synthesis_prompt": response_synthesis_prompt, "response_synthesis_llm": llm, }, verbose=True, )
In [ ]:
Copied!
```
qp.add_link("input", "table_retriever")
qp.add_link("input", "table_output_parser", dest_key="query_str")
qp.add_link(
    "table_retriever", "table_output_parser", dest_key="table_schema_objs"
)
qp.add_link("input", "text2sql_prompt", dest_key="query_str")
qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
qp.add_chain(
    ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"]
)
qp.add_link(
    "sql_output_parser", "response_synthesis_prompt", dest_key="sql_query"
)
qp.add_link(
    "sql_retriever", "response_synthesis_prompt", dest_key="context_str"
)
qp.add_link("input", "response_synthesis_prompt", dest_key="query_str")
qp.add_link("response_synthesis_prompt", "response_synthesis_llm")

```

qp.add_link("input", "table_retriever") qp.add_link("input", "table_output_parser", dest_key="query_str") qp.add_link( "table_retriever", "table_output_parser", dest_key="table_schema_objs" ) qp.add_link("input", "text2sql_prompt", dest_key="query_str") qp.add_link("table_output_parser", "text2sql_prompt", dest_key="schema") qp.add_chain( ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"] ) qp.add_link( "sql_output_parser", "response_synthesis_prompt", dest_key="sql_query" ) qp.add_link( "sql_retriever", "response_synthesis_prompt", dest_key="context_str" ) qp.add_link("input", "response_synthesis_prompt", dest_key="query_str") qp.add_link("response_synthesis_prompt", "response_synthesis_llm")
In [ ]:
Copied!
```
from pyvis.network import Network

net = Network(notebook=True, cdn_resources="in_line", directed=True)
net.from_nx(qp.dag)
net.show("text2sql_dag.html")

```

from pyvis.network import Network net = Network(notebook=True, cdn_resources="in_line", directed=True) net.from_nx(qp.dag) net.show("text2sql_dag.html")
### Run Some Queries¶
We can now ask about relevant entries even if it doesn't exactly match the entry in the database.
In [ ]:
Copied!
```
response = qp.run(
    query="What was the year that The Notorious BIG was signed to Bad Boy?"
)
print(str(response))

```

response = qp.run( query="What was the year that The Notorious BIG was signed to Bad Boy?" ) print(str(response))
```
> Running module input with input: 
query: What was the year that The Notorious BIG was signed to Bad Boy?

> Running module table_retriever with input: 
input: What was the year that The Notorious BIG was signed to Bad Boy?

> Running module table_output_parser with input: 
query_str: What was the year that The Notorious BIG was signed to Bad Boy?
table_schema_objs: [SQLTableSchema(table_name='Bad_Boy_Artists', context_str='List of artists signed to Bad Boy Records and their album releases'), SQLTableSchema(table_name='Bad_Boy_Artists', context_str='List of artis...

> Running module text2sql_prompt with input: 
query_str: What was the year that The Notorious BIG was signed to Bad Boy?
schema: Table 'Bad_Boy_Artists' has columns: Act (VARCHAR), Year_signed (INTEGER), _Albums_released_under_Bad_Boy (VARCHAR), and foreign keys: . The table description is: List of artists signed to Bad Boy Rec...

> Running module text2sql_llm with input: 
messages: Given an input question, first create a syntactically correct sqlite query to run, then look at the results of the query and return the answer. You can order the results by a relevant column to return...

> Running module sql_output_parser with input: 
response: assistant: SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = 'The Notorious B.I.G'
SQLResult: 1993
Answer: The Notorious BIG was signed to Bad Boy in 1993.

RAW RESPONSE  SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = 'The Notorious B.I.G'
SQLResult: 1993
Answer: The Notorious BIG was signed to Bad Boy in 1993.
> Running module sql_retriever with input: 
input: SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = 'The Notorious B.I.G'

> Running module response_synthesis_prompt with input: 
query_str: What was the year that The Notorious BIG was signed to Bad Boy?
sql_query: SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = 'The Notorious B.I.G'
context_str: [NodeWithScore(node=TextNode(id_='23214862-784c-4f2b-b489-39d61ea96580', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, hash='c336a1cbf9...

> Running module response_synthesis_llm with input: 
messages: Given an input question, synthesize a response from the query results.
Query: What was the year that The Notorious BIG was signed to Bad Boy?
SQL: SELECT Year_signed
FROM Bad_Boy_Artists
WHERE Act = '...

assistant: The Notorious BIG was signed to Bad Boy in 1993.

```

