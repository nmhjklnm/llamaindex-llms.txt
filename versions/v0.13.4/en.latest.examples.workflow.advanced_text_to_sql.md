# Workflows for Advanced Text-to-SQL¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In this guide we show you how to setup a text-to-SQL workflow over your data with our workflows syntax.
This gives you flexibility to enhance text-to-SQL with additional techniques. We show these in the below sections:
  1. **Query-Time Table Retrieval** : Dynamically retrieve relevant tables in the text-to-SQL prompt.
  2. **Query-Time Sample Row retrieval** : Embed/Index each row, and dynamically retrieve example rows for each table in the text-to-SQL prompt.


Our out-of-the box workflows include our `NLSQLTableQueryEngine` and `SQLTableRetrieverQueryEngine`. (if you want to check out our text-to-SQL guide using these modules, take a look here). This guide implements an advanced version of those modules, giving you the utmost flexibility to apply this to your own setting.
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
Here we use gpt-4o-mini to extract a table name (with underscores) and summary from each table with our Pydantic program.
In [ ]:
Copied!
```
tableinfo_dir = "WikiTableQuestions_TableInfo"
!mkdir {tableinfo_dir}

```

tableinfo_dir = "WikiTableQuestions_TableInfo" !mkdir {tableinfo_dir}
```
mkdir: WikiTableQuestions_TableInfo: File exists

```

In [ ]:
Copied!
```
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.bridge.pydantic import BaseModel, Field
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage


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
prompt_tmpl = ChatPromptTemplate(
    message_templates=[ChatMessage.from_str(prompt_str, role="user")]
)

llm = OpenAI(model="gpt-4o-mini")

```

from llama_index.core.prompts import ChatPromptTemplate from llama_index.core.bridge.pydantic import BaseModel, Field from llama_index.llms.openai import OpenAI from llama_index.core.llms import ChatMessage class TableInfo(BaseModel): """Information regarding a structured table.""" table_name: str = Field( ..., description="table name (must be underscores and NO spaces)" ) table_summary: str = Field( ..., description="short, concise summary/caption of the table" ) prompt_str = """\ Give me a summary of the table with the following JSON format. - The table name must be unique to the table and describe it while being concise. - Do NOT output a generic table name (e.g. table, my_table). Do NOT make the table name one of the following: {exclude_table_name_list} Table: {table_str} Summary: """ prompt_tmpl = ChatPromptTemplate( message_templates=[ChatMessage.from_str(prompt_str, role="user")] ) llm = OpenAI(model="gpt-4o-mini")
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
            table_info = llm.structured_predict(
                TableInfo,
                prompt_tmpl,
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

import json def _get_tableinfo_with_index(idx: int) -> str: results_gen = Path(tableinfo_dir).glob(f"{idx}_*") results_list = list(results_gen) if len(results_list) == 0: return None elif len(results_list) == 1: path = results_list[0] return TableInfo.parse_file(path) else: raise ValueError( f"More than one file matching index: {list(results_gen)}" ) table_names = set() table_infos = [] for idx, df in enumerate(dfs): table_info = _get_tableinfo_with_index(idx) if table_info: table_infos.append(table_info) else: while True: df_str = df.head(10).to_csv() table_info = llm.structured_predict( TableInfo, prompt_tmpl, table_str=df_str, exclude_table_name_list=str(list(table_names)), ) table_name = table_info.table_name print(f"Processed table: {table_name}") if table_name not in table_names: table_names.add(table_name) break else: # try again print(f"Table name {table_name} already exists, trying again.") pass out_file = f"{tableinfo_dir}/{idx}_{table_name}.json" json.dump(table_info.dict(), open(out_file, "w")) table_infos.append(table_info)
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


# engine = create_engine("sqlite:///:memory:")
engine = create_engine("sqlite:///wiki_table_questions.db")
metadata_obj = MetaData()
for idx, df in enumerate(dfs):
    tableinfo = _get_tableinfo_with_index(idx)
    print(f"Creating table: {tableinfo.table_name}")
    create_table_from_dataframe(df, tableinfo.table_name, engine, metadata_obj)

```

# put data into sqlite db from sqlalchemy import ( create_engine, MetaData, Table, Column, String, Integer, ) import re # Function to create a sanitized column name def sanitize_column_name(col_name): # Remove special characters and replace spaces with underscores return re.sub(r"\W+", "_", col_name) # Function to create a table from a DataFrame using SQLAlchemy def create_table_from_dataframe( df: pd.DataFrame, table_name: str, engine, metadata_obj ): # Sanitize column names sanitized_columns = {col: sanitize_column_name(col) for col in df.columns} df = df.rename(columns=sanitized_columns) # Dynamically create columns based on DataFrame columns and data types columns = [ Column(col, String if dtype == "object" else Integer) for col, dtype in zip(df.columns, df.dtypes) ] # Create a table with the defined columns table = Table(table_name, metadata_obj, *columns) # Create the table in the database metadata_obj.create_all(engine) # Insert data from DataFrame into the table with engine.connect() as conn: for _, row in df.iterrows(): insert_stmt = table.insert().values(**row.to_dict()) conn.execute(insert_stmt) conn.commit() # engine = create_engine("sqlite:///:memory:") engine = create_engine("sqlite:///wiki_table_questions.db") metadata_obj = MetaData() for idx, df in enumerate(dfs): tableinfo = _get_tableinfo_with_index(idx) print(f"Creating table: {tableinfo.table_name}") create_table_from_dataframe(df, tableinfo.table_name, engine, metadata_obj)
In [ ]:
Copied!
```
# # setup Arize Phoenix for logging/observability
# import phoenix as px
# import llama_index.core

# px.launch_app()
# llama_index.core.set_global_handler("arize_phoenix")

```

# # setup Arize Phoenix for logging/observability # import phoenix as px # import llama_index.core # px.launch_app() # llama_index.core.set_global_handler("arize_phoenix")
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

```

from llama_index.core.retrievers import SQLRetriever from typing import List sql_retriever = SQLRetriever(sql_database) def get_table_context_str(table_schema_objs: List[SQLTableSchema]): """Get table context string.""" context_strs = [] for table_schema_obj in table_schema_objs: table_info = sql_database.get_single_table_info( table_schema_obj.table_name ) if table_schema_obj.context_str: table_opt_context = " The table description is: " table_opt_context += table_schema_obj.context_str table_info += table_opt_context context_strs.append(table_info) return "\n\n".join(context_strs)
Text-to-SQL Prompt + Output Parser
In [ ]:
Copied!
```
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core import PromptTemplate
from llama_index.core.llms import ChatResponse


def parse_response_to_sql(chat_response: ChatResponse) -> str:
    """Parse response to SQL."""
    response = chat_response.message.content
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


text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
    dialect=engine.dialect.name
)
print(text2sql_prompt.template)

```

from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT from llama_index.core import PromptTemplate from llama_index.core.llms import ChatResponse def parse_response_to_sql(chat_response: ChatResponse) -> str: """Parse response to SQL.""" response = chat_response.message.content sql_query_start = response.find("SQLQuery:") if sql_query_start != -1: response = response[sql_query_start:] # TODO: move to removeprefix after Python 3.9+ if response.startswith("SQLQuery:"): response = response[len("SQLQuery:") :] sql_result_start = response.find("SQLResult:") if sql_result_start != -1: response = response[:sql_result_start] return response.strip().strip("```").strip() text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format( dialect=engine.dialect.name ) print(text2sql_prompt.template)
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
# llm = OpenAI(model="gpt-3.5-turbo")
llm = OpenAI(model="gpt-4o-mini")

```

# llm = OpenAI(model="gpt-3.5-turbo") llm = OpenAI(model="gpt-4o-mini")
### Define Workflow¶
Now that the components are in place, let's define the full workflow!
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Context,
    Event,
)


class TableRetrieveEvent(Event):
    """Result of running table retrieval."""

    table_context_str: str
    query: str


class TextToSQLEvent(Event):
    """Text-to-SQL event."""

    sql: str
    query: str


class TextToSQLWorkflow1(Workflow):
    """Text-to-SQL Workflow that does query-time table retrieval."""

    def __init__(
        self,
        obj_retriever,
        text2sql_prompt,
        sql_retriever,
        response_synthesis_prompt,
        llm,
        *args,
        **kwargs
    ) -> None:
        """Init params."""
        super().__init__(*args, **kwargs)
        self.obj_retriever = obj_retriever
        self.text2sql_prompt = text2sql_prompt
        self.sql_retriever = sql_retriever
        self.response_synthesis_prompt = response_synthesis_prompt
        self.llm = llm

    @step
    def retrieve_tables(
        self, ctx: Context, ev: StartEvent
    ) -> TableRetrieveEvent:
        """Retrieve tables."""
        table_schema_objs = self.obj_retriever.retrieve(ev.query)
        table_context_str = get_table_context_str(table_schema_objs)
        return TableRetrieveEvent(
            table_context_str=table_context_str, query=ev.query
        )

    @step
    def generate_sql(
        self, ctx: Context, ev: TableRetrieveEvent
    ) -> TextToSQLEvent:
        """Generate SQL statement."""
        fmt_messages = self.text2sql_prompt.format_messages(
            query_str=ev.query, schema=ev.table_context_str
        )
        chat_response = self.llm.chat(fmt_messages)
        sql = parse_response_to_sql(chat_response)
        return TextToSQLEvent(sql=sql, query=ev.query)

    @step
    def generate_response(self, ctx: Context, ev: TextToSQLEvent) -> StopEvent:
        """Run SQL retrieval and generate response."""
        retrieved_rows = self.sql_retriever.retrieve(ev.sql)
        fmt_messages = self.response_synthesis_prompt.format_messages(
            sql_query=ev.sql,
            context_str=str(retrieved_rows),
            query_str=ev.query,
        )
        chat_response = llm.chat(fmt_messages)
        return StopEvent(result=chat_response)

```

from llama_index.core.workflow import ( Workflow, StartEvent, StopEvent, step, Context, Event, ) class TableRetrieveEvent(Event): """Result of running table retrieval.""" table_context_str: str query: str class TextToSQLEvent(Event): """Text-to-SQL event.""" sql: str query: str class TextToSQLWorkflow1(Workflow): """Text-to-SQL Workflow that does query-time table retrieval.""" def __init__( self, obj_retriever, text2sql_prompt, sql_retriever, response_synthesis_prompt, llm, *args, **kwargs ) -> None: """Init params.""" super().__init__(*args, **kwargs) self.obj_retriever = obj_retriever self.text2sql_prompt = text2sql_prompt self.sql_retriever = sql_retriever self.response_synthesis_prompt = response_synthesis_prompt self.llm = llm @step def retrieve_tables( self, ctx: Context, ev: StartEvent ) -> TableRetrieveEvent: """Retrieve tables.""" table_schema_objs = self.obj_retriever.retrieve(ev.query) table_context_str = get_table_context_str(table_schema_objs) return TableRetrieveEvent( table_context_str=table_context_str, query=ev.query ) @step def generate_sql( self, ctx: Context, ev: TableRetrieveEvent ) -> TextToSQLEvent: """Generate SQL statement.""" fmt_messages = self.text2sql_prompt.format_messages( query_str=ev.query, schema=ev.table_context_str ) chat_response = self.llm.chat(fmt_messages) sql = parse_response_to_sql(chat_response) return TextToSQLEvent(sql=sql, query=ev.query) @step def generate_response(self, ctx: Context, ev: TextToSQLEvent) -> StopEvent: """Run SQL retrieval and generate response.""" retrieved_rows = self.sql_retriever.retrieve(ev.sql) fmt_messages = self.response_synthesis_prompt.format_messages( sql_query=ev.sql, context_str=str(retrieved_rows), query_str=ev.query, ) chat_response = llm.chat(fmt_messages) return StopEvent(result=chat_response)
### Visualize Workflow¶
A really nice property of workflows is that you can both visualize the execution graph as well as a trace of the most recent execution.
In [ ]:
Copied!
```
from llama_index.utils.workflow import draw_all_possible_flows

draw_all_possible_flows(
    TextToSQLWorkflow1, filename="text_to_sql_table_retrieval.html"
)

```

from llama_index.utils.workflow import draw_all_possible_flows draw_all_possible_flows( TextToSQLWorkflow1, filename="text_to_sql_table_retrieval.html" )
```
text_to_sql_table_retrieval.html

```

In [ ]:
Copied!
```
from IPython.display import display, HTML

# Read the contents of the HTML file
with open("text_to_sql_table_retrieval.html", "r") as file:
    html_content = file.read()

# Display the HTML content
display(HTML(html_content))

```

from IPython.display import display, HTML # Read the contents of the HTML file with open("text_to_sql_table_retrieval.html", "r") as file: html_content = file.read() # Display the HTML content display(HTML(html_content))
# 
# 
### Run Some Queries!¶
Now we're ready to run some queries across this entire workflow.
In [ ]:
Copied!
```
workflow = TextToSQLWorkflow1(
    obj_retriever,
    text2sql_prompt,
    sql_retriever,
    response_synthesis_prompt,
    llm,
    verbose=True,
)

```

workflow = TextToSQLWorkflow1( obj_retriever, text2sql_prompt, sql_retriever, response_synthesis_prompt, llm, verbose=True, )
In [ ]:
Copied!
```
response = await workflow.run(
    query="What was the year that The Notorious B.I.G was signed to Bad Boy?"
)
print(str(response))

```

response = await workflow.run( query="What was the year that The Notorious B.I.G was signed to Bad Boy?" ) print(str(response))
```
Running step retrieve_tables
Step retrieve_tables produced event TableRetrieveEvent
Running step generate_sql
Step generate_sql produced event TextToSQLEvent
Running step generate_response
Step generate_response produced event StopEvent
assistant: The Notorious B.I.G was signed to Bad Boy Records in 1993.
VERBOSE: True
> Table Info: Table 'bad_boy_artists_album_release_summary' has columns: Act (VARCHAR), Year_signed (INTEGER), _Albums_released_under_Bad_Boy (VARCHAR), . The table description is: A summary of artists signed to Bad Boy Records along with the year they were signed and the number of albums they released.
Here are some relevant example rows (values in the same order as columns above)
('The Notorious B.I.G', 1993, '5')

> Table Info: Table 'filmography_of_diane_drummond' has columns: Year (INTEGER), Title (VARCHAR), Role (VARCHAR), Notes (VARCHAR), . The table description is: A list of film and television roles played by Diane Drummond from 1995 to 2001.
Here are some relevant example rows (values in the same order as columns above)
(2013, 'L.A. Slasher', 'The Actress', None)

> Table Info: Table 'progressive_rock_album_chart_positions' has columns: Year (INTEGER), Title (VARCHAR), Chart_Positions_UK (VARCHAR), Chart_Positions_US (VARCHAR), Chart_Positions_NL (VARCHAR), Comments (VARCHAR), . The table description is: Chart positions of progressive rock albums in the UK, US, and NL from 1969 to 1981.
Here are some relevant example rows (values in the same order as columns above)
(1977, 'Novella', '–', '46', '–', '1977 (January in US, August in UK, as the band moved to the Warner Bros Music Group)')

VERBOSE: True
> Table Info: Table 'bad_boy_artists_album_release_summary' has columns: Act (VARCHAR), Year_signed (INTEGER), _Albums_released_under_Bad_Boy (VARCHAR), . The table description is: A summary of artists signed to Bad Boy Records along with the year they were signed and the number of albums they released.
Here are some relevant example rows (values in the same order as columns above)
('The Notorious B.I.G', 1993, '5')

> Table Info: Table 'filmography_of_diane_drummond' has columns: Year (INTEGER), Title (VARCHAR), Role (VARCHAR), Notes (VARCHAR), . The table description is: A list of film and television roles played by Diane Drummond from 1995 to 2001.
Here are some relevant example rows (values in the same order as columns above)
(2013, 'L.A. Slasher', 'The Actress', None)

> Table Info: Table 'progressive_rock_album_chart_positions' has columns: Year (INTEGER), Title (VARCHAR), Chart_Positions_UK (VARCHAR), Chart_Positions_US (VARCHAR), Chart_Positions_NL (VARCHAR), Comments (VARCHAR), . The table description is: Chart positions of progressive rock albums in the UK, US, and NL from 1969 to 1981.
Here are some relevant example rows (values in the same order as columns above)
(1977, 'Novella', '–', '46', '–', '1977 (January in US, August in UK, as the band moved to the Warner Bros Music Group)')


```

In [ ]:
Copied!
```
response = await workflow.run(
    query="Who won best director in the 1972 academy awards"
)
print(str(response))

```

response = await workflow.run( query="Who won best director in the 1972 academy awards" ) print(str(response))
```
Running step retrieve_tables
Step retrieve_tables produced event TableRetrieveEvent
Running step generate_sql
Step generate_sql produced event TextToSQLEvent
Running step generate_response
Step generate_response produced event StopEvent
assistant: William Friedkin won the Best Director award at the 1972 Academy Awards.

```

In [ ]:
Copied!
```
response = await workflow.run(query="What was the term of Pasquale Preziosa?")
print(str(response))

```

response = await workflow.run(query="What was the term of Pasquale Preziosa?") print(str(response))
```
Running step retrieve_tables
Step retrieve_tables produced event TableRetrieveEvent
Running step generate_sql
Step generate_sql produced event TextToSQLEvent
Running step generate_response
Step generate_response produced event StopEvent
assistant: Pasquale Preziosa has been serving since 25 February 2013 and is currently in office as the incumbent.

```

## 2. Advanced Capability 2: Text-to-SQL with Query-Time Row Retrieval (along with Table Retrieval)¶
One problem in the previous example is that if the user asks a query that asks for "The Notorious BIG" but the artist is stored as "The Notorious B.I.G", then the generated SELECT statement will likely not return any matches.
We can alleviate this problem by fetching a small number of example rows per table. A naive option would be to just take the first k rows. Instead, we embed, index, and retrieve k relevant rows given the user query to give the text-to-SQL LLM the most contextually relevant information for SQL generation.
We now extend our workflow.
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
Indexing rows in table: academy_awards_and_nominations_1972
Indexing rows in table: annual_traffic_accident_deaths
Indexing rows in table: bad_boy_artists_album_release_summary
Indexing rows in table: bbc_radio_services_cost_comparison_2012_2013
Indexing rows in table: binary_encoding_probabilities
Indexing rows in table: boxing_match_results_summary
Indexing rows in table: cancer_related_genes_and_functions
Indexing rows in table: diane_drummond_awards_nominations
Indexing rows in table: diane_drummond_oscar_nominations_and_wins
Indexing rows in table: diane_drummond_single_chart_performance
Indexing rows in table: euro_2020_group_stage_results
Indexing rows in table: experiment_drop_events_timeline
Indexing rows in table: filmography_of_diane_drummond
Indexing rows in table: grammy_awards_summary_for_wilco
Indexing rows in table: historical_college_football_records
Indexing rows in table: italian_ministers_term_dates
Indexing rows in table: kodachrome_film_types_and_dates
Indexing rows in table: missing_persons_case_summary
Indexing rows in table: monthly_climate_statistics
Indexing rows in table: monthly_climate_statistics_summary
Indexing rows in table: monthly_weather_statistics
Indexing rows in table: multilingual_greetings_and_phrases
Indexing rows in table: municipalities_merger_summary
Indexing rows in table: new_mexico_government_officials
Indexing rows in table: norwegian_club_performance_summary
Indexing rows in table: ohio_private_schools_summary
Indexing rows in table: progressive_rock_album_chart_positions
Indexing rows in table: regional_airports_usage_summary
Indexing rows in table: south_dakota_radio_stations
Indexing rows in table: triple_crown_winners_summary
Indexing rows in table: uk_ministers_and_titles_history
Indexing rows in table: voter_registration_status_by_party
Indexing rows in table: voter_registration_summary_by_party
Indexing rows in table: yamato_district_population_density

```

### Define Expanded Table Parsing¶
We expand the capability of our table parsing to not only return the relevant table schemas, but also return relevant rows per table schema.
It now takes in both `table_schema_objs` (output of table retriever), but also the original `query_str` which will then be used for vector retrieval of relevant rows.
In [ ]:
Copied!
```
from llama_index.core.retrievers import SQLRetriever
from typing import List

sql_retriever = SQLRetriever(sql_database)


def get_table_context_and_rows_str(
    query_str: str,
    table_schema_objs: List[SQLTableSchema],
    verbose: bool = False,
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

        if verbose:
            print(f"> Table Info: {table_info}")

        context_strs.append(table_info)
    return "\n\n".join(context_strs)

```

from llama_index.core.retrievers import SQLRetriever from typing import List sql_retriever = SQLRetriever(sql_database) def get_table_context_and_rows_str( query_str: str, table_schema_objs: List[SQLTableSchema], verbose: bool = False, ): """Get table context string.""" context_strs = [] for table_schema_obj in table_schema_objs: # first append table info + additional context table_info = sql_database.get_single_table_info( table_schema_obj.table_name ) if table_schema_obj.context_str: table_opt_context = " The table description is: " table_opt_context += table_schema_obj.context_str table_info += table_opt_context # also lookup vector index to return relevant table rows vector_retriever = vector_index_dict[ table_schema_obj.table_name ].as_retriever(similarity_top_k=2) relevant_nodes = vector_retriever.retrieve(query_str) if len(relevant_nodes) > 0: table_row_context = "\nHere are some relevant example rows (values in the same order as columns above)\n" for node in relevant_nodes: table_row_context += str(node.get_content()) + "\n" table_info += table_row_context if verbose: print(f"> Table Info: {table_info}") context_strs.append(table_info) return "\n\n".join(context_strs)
### Define Expanded Workflow¶
We re-use the workflow in section 1, but with an upgraded SQL parsing step after text-to-SQL generation.
It is very easy to subclass and extend an existing workflow, and customizing existing steps to be more advanced. Here we define a new worfklow that overrides the existing `retrieve_tables` step in order to return the relevant rows.
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Workflow,
    StartEvent,
    StopEvent,
    step,
    Context,
    Event,
)


class TextToSQLWorkflow2(TextToSQLWorkflow1):
    """Text-to-SQL Workflow that does query-time row AND table retrieval."""

    @step
    def retrieve_tables(
        self, ctx: Context, ev: StartEvent
    ) -> TableRetrieveEvent:
        """Retrieve tables."""
        table_schema_objs = self.obj_retriever.retrieve(ev.query)
        table_context_str = get_table_context_and_rows_str(
            ev.query, table_schema_objs, verbose=self._verbose
        )
        return TableRetrieveEvent(
            table_context_str=table_context_str, query=ev.query
        )

```

from llama_index.core.workflow import ( Workflow, StartEvent, StopEvent, step, Context, Event, ) class TextToSQLWorkflow2(TextToSQLWorkflow1): """Text-to-SQL Workflow that does query-time row AND table retrieval.""" @step def retrieve_tables( self, ctx: Context, ev: StartEvent ) -> TableRetrieveEvent: """Retrieve tables.""" table_schema_objs = self.obj_retriever.retrieve(ev.query) table_context_str = get_table_context_and_rows_str( ev.query, table_schema_objs, verbose=self._verbose ) return TableRetrieveEvent( table_context_str=table_context_str, query=ev.query )
Since the overall sequence of steps is the same, the graph should look the same.
In [ ]:
Copied!
```
from llama_index.utils.workflow import draw_all_possible_flows

draw_all_possible_flows(
    TextToSQLWorkflow2, filename="text_to_sql_table_retrieval.html"
)

```

from llama_index.utils.workflow import draw_all_possible_flows draw_all_possible_flows( TextToSQLWorkflow2, filename="text_to_sql_table_retrieval.html" )
```
text_to_sql_table_retrieval.html

```

### Run Some Queries¶
We can now ask about relevant entries even if it doesn't exactly match the entry in the database.
In [ ]:
Copied!
```
workflow2 = TextToSQLWorkflow2(
    obj_retriever,
    text2sql_prompt,
    sql_retriever,
    response_synthesis_prompt,
    llm,
    verbose=True,
)

```

workflow2 = TextToSQLWorkflow2( obj_retriever, text2sql_prompt, sql_retriever, response_synthesis_prompt, llm, verbose=True, )
In [ ]:
Copied!
```
response = await workflow2.run(
    query="What was the year that The Notorious BIG was signed to Bad Boy?"
)
print(str(response))

```

response = await workflow2.run( query="What was the year that The Notorious BIG was signed to Bad Boy?" ) print(str(response))
```
Running step retrieve_tables
VERBOSE: True
> Table Info: Table 'bad_boy_artists_album_release_summary' has columns: Act (VARCHAR), Year_signed (INTEGER), _Albums_released_under_Bad_Boy (VARCHAR), . The table description is: A summary of artists signed to Bad Boy Records along with the year they were signed and the number of albums they released.
Here are some relevant example rows (values in the same order as columns above)
('The Notorious B.I.G', 1993, '5')

> Table Info: Table 'filmography_of_diane_drummond' has columns: Year (INTEGER), Title (VARCHAR), Role (VARCHAR), Notes (VARCHAR), . The table description is: A list of film and television roles played by Diane Drummond from 1995 to 2001.
Here are some relevant example rows (values in the same order as columns above)
(2013, 'L.A. Slasher', 'The Actress', None)

> Table Info: Table 'progressive_rock_album_chart_positions' has columns: Year (INTEGER), Title (VARCHAR), Chart_Positions_UK (VARCHAR), Chart_Positions_US (VARCHAR), Chart_Positions_NL (VARCHAR), Comments (VARCHAR), . The table description is: Chart positions of progressive rock albums in the UK, US, and NL from 1969 to 1981.
Here are some relevant example rows (values in the same order as columns above)
(1977, 'Novella', '–', '46', '–', '1977 (January in US, August in UK, as the band moved to the Warner Bros Music Group)')

Step retrieve_tables produced event TableRetrieveEvent
Running step generate_sql
Step generate_sql produced event TextToSQLEvent
Running step generate_response
Step generate_response produced event StopEvent
assistant: The Notorious B.I.G. was signed to Bad Boy Records in 1993.

```

