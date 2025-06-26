![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# JSONalyze Query Engine¶
JSONalyze Query Engine is designed to be wired typically after a calling(by agent, etc) of APIs, where we have the returned value as bulk instances of rows, and the next step is to perform statistical analysis on the data.
With JSONalyze, under the hood, in-memory SQLite table is created with the JSON List loaded, the query engine is able to perform SQL queries on the data, and return the Query Result as answer to the analytical questions.
This notebook walks through implementation of JSON Analyze Query Engine, using Workflows.
Specifically we will implement JSONalyzeQueryEngine.
In [ ]:
Copied!
```
!pip install -U llama-index

```

!pip install -U llama-index
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
Since workflows are async first, this all runs fine in a notebook. If you were running in your own code, you would want to use `asyncio.run()` to start an async event loop if one isn't already running.
```
async def main():
    <async code>

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

## The Workflow¶
`jsonalyzer:`
  1. It takes a StartEvent as input and returns a JsonAnalyzerEvent.
  2. The function sets up an in-memory SQLite database, loads JSON data, generates a SQL query based on query using a LLM, executes the query, and returns the results along with the SQL query and table schema.


`synthesize:`
The function uses a LLM to synthesize a response based on the SQL query, table schema, and query results.
The steps will use the built-in `StartEvent` and `StopEvent` events.
## Define Event¶
In [ ]:
Copied!
```
from llama_index.core.workflow import Event
from typing import Dict, List, Any


class JsonAnalyzerEvent(Event):
    """
    Event containing results of JSON analysis.

    Attributes:
        sql_query (str): The generated SQL query.
        table_schema (Dict[str, Any]): Schema of the analyzed table.
        results (List[Dict[str, Any]]): Query execution results.
    """

    sql_query: str
    table_schema: Dict[str, Any]
    results: List[Dict[str, Any]]

```

from llama_index.core.workflow import Event from typing import Dict, List, Any class JsonAnalyzerEvent(Event): """ Event containing results of JSON analysis. Attributes: sql_query (str): The generated SQL query. table_schema (Dict[str, Any]): Schema of the analyzed table. results (List[Dict[str, Any]]): Query execution results. """ sql_query: str table_schema: Dict[str, Any] results: List[Dict[str, Any]]
## Prompt Templates¶
Here we define default `DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL`, `DEFAULT_RESPONSE_SYNTHESIS_PROMPT` and `DEFAULT_TABLE_NAME`.
In [ ]:
Copied!
```
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.prompts import PromptTemplate

DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL = (
    "Given a query, synthesize a response based on SQL query results"
    " to satisfy the query. Only include details that are relevant to"
    " the query. If you don't know the answer, then say that.\n"
    "SQL Query: {sql_query}\n"
    "Table Schema: {table_schema}\n"
    "SQL Response: {sql_response}\n"
    "Query: {query_str}\n"
    "Response: "
)

DEFAULT_RESPONSE_SYNTHESIS_PROMPT = PromptTemplate(
    DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL,
    prompt_type=PromptType.SQL_RESPONSE_SYNTHESIS,
)

DEFAULT_TABLE_NAME = "items"

```

from llama_index.core.prompts.prompt_type import PromptType from llama_index.core.prompts import PromptTemplate DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL = ( "Given a query, synthesize a response based on SQL query results" " to satisfy the query. Only include details that are relevant to" " the query. If you don't know the answer, then say that.\n" "SQL Query: {sql_query}\n" "Table Schema: {table_schema}\n" "SQL Response: {sql_response}\n" "Query: {query_str}\n" "Response: " ) DEFAULT_RESPONSE_SYNTHESIS_PROMPT = PromptTemplate( DEFAULT_RESPONSE_SYNTHESIS_PROMPT_TMPL, prompt_type=PromptType.SQL_RESPONSE_SYNTHESIS, ) DEFAULT_TABLE_NAME = "items"
### The Workflow Itself¶
With our events defined, we can construct our workflow and steps.
Note that the workflow automatically validates itself using type annotations, so the type annotations on our steps are very helpful!
In [ ]:
Copied!
```
from llama_index.core.base.response.schema import Response
from llama_index.core.indices.struct_store.sql_retriever import (
    DefaultSQLParser,
)
from llama_index.core.prompts.default_prompts import DEFAULT_JSONALYZE_PROMPT
from llama_index.core.utils import print_text

from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)

from llama_index.llms.openai import OpenAI

from IPython.display import Markdown, display


class JSONAnalyzeQueryEngineWorkflow(Workflow):
    @step
    async def jsonalyzer(
        self, ctx: Context, ev: StartEvent
    ) -> JsonAnalyzerEvent:
        """
        Analyze JSON data using a SQL-like query approach.

        This asynchronous method sets up an in-memory SQLite database, loads JSON data,
        generates a SQL query based on a natural language question, executes the query,
        and returns the results.

        Args:
            ctx (Context): The context object for storing data during execution.
            ev (StartEvent): The event object containing input parameters.

        Returns:
            JsonAnalyzerEvent: An event object containing the SQL query, table schema, and query results.

        The method performs the following steps:
        1. Imports the required 'sqlite-utils' package.
        2. Extracts necessary data from the input event.
        3. Sets up an in-memory SQLite database and loads the JSON data.
        4. Generates a SQL query using a LLM based on the input question.
        5. Executes the SQL query and retrieves the results.
        6. Returns the results along with the SQL query and table schema.

        Note:
            This method requires the 'sqlite-utils' package to be installed.
        """
        try:
            import sqlite_utils
        except ImportError as exc:
            IMPORT_ERROR_MSG = (
                "sqlite-utils is needed to use this Query Engine:\n"
                "pip install sqlite-utils"
            )

            raise ImportError(IMPORT_ERROR_MSG) from exc

        await ctx.set("query", ev.get("query"))
        await ctx.set("llm", ev.get("llm"))

        query = ev.get("query")
        table_name = ev.get("table_name")
        list_of_dict = ev.get("list_of_dict")
        prompt = DEFAULT_JSONALYZE_PROMPT

        # Instantiate in-memory SQLite database
        db = sqlite_utils.Database(memory=True)
        try:
            # Load list of dictionaries into SQLite database
            db[ev.table_name].insert_all(list_of_dict)
        except sqlite_utils.utils.sqlite3.IntegrityError as exc:
            print_text(
                f"Error inserting into table {table_name}, expected format:"
            )
            print_text("[{col1: val1, col2: val2, ...}, ...]")
            raise ValueError("Invalid list_of_dict") from exc

        # Get the table schema
        table_schema = db[table_name].columns_dict

        # Get the SQL query with text-to-SQL prompt
        response_str = await ev.llm.apredict(
            prompt=prompt,
            table_name=table_name,
            table_schema=table_schema,
            question=query,
        )

        sql_parser = DefaultSQLParser()

        sql_query = sql_parser.parse_response_to_sql(response_str, ev.query)

        try:
            # Execute the SQL query
            results = list(db.query(sql_query))
        except sqlite_utils.utils.sqlite3.OperationalError as exc:
            print_text(f"Error executing query: {sql_query}")
            raise ValueError("Invalid query") from exc

        return JsonAnalyzerEvent(
            sql_query=sql_query, table_schema=table_schema, results=results
        )

    @step
    async def synthesize(
        self, ctx: Context, ev: JsonAnalyzerEvent
    ) -> StopEvent:
        """Synthesize the response."""
        llm = await ctx.get("llm", default=None)
        query = await ctx.get("query", default=None)

        response_str = llm.predict(
            DEFAULT_RESPONSE_SYNTHESIS_PROMPT,
            sql_query=ev.sql_query,
            table_schema=ev.table_schema,
            sql_response=ev.results,
            query_str=query,
        )

        response_metadata = {
            "sql_query": ev.sql_query,
            "table_schema": str(ev.table_schema),
        }

        response = Response(response=response_str, metadata=response_metadata)

        return StopEvent(result=response)

```

from llama_index.core.base.response.schema import Response from llama_index.core.indices.struct_store.sql_retriever import ( DefaultSQLParser, ) from llama_index.core.prompts.default_prompts import DEFAULT_JSONALYZE_PROMPT from llama_index.core.utils import print_text from llama_index.core.workflow import ( Context, Workflow, StartEvent, StopEvent, step, ) from llama_index.llms.openai import OpenAI from IPython.display import Markdown, display class JSONAnalyzeQueryEngineWorkflow(Workflow): @step async def jsonalyzer( self, ctx: Context, ev: StartEvent ) -> JsonAnalyzerEvent: """ Analyze JSON data using a SQL-like query approach. This asynchronous method sets up an in-memory SQLite database, loads JSON data, generates a SQL query based on a natural language question, executes the query, and returns the results. Args: ctx (Context): The context object for storing data during execution. ev (StartEvent): The event object containing input parameters. Returns: JsonAnalyzerEvent: An event object containing the SQL query, table schema, and query results. The method performs the following steps: 1. Imports the required 'sqlite-utils' package. 2. Extracts necessary data from the input event. 3. Sets up an in-memory SQLite database and loads the JSON data. 4. Generates a SQL query using a LLM based on the input question. 5. Executes the SQL query and retrieves the results. 6. Returns the results along with the SQL query and table schema. Note: This method requires the 'sqlite-utils' package to be installed. """ try: import sqlite_utils except ImportError as exc: IMPORT_ERROR_MSG = ( "sqlite-utils is needed to use this Query Engine:\n" "pip install sqlite-utils" ) raise ImportError(IMPORT_ERROR_MSG) from exc await ctx.set("query", ev.get("query")) await ctx.set("llm", ev.get("llm")) query = ev.get("query") table_name = ev.get("table_name") list_of_dict = ev.get("list_of_dict") prompt = DEFAULT_JSONALYZE_PROMPT # Instantiate in-memory SQLite database db = sqlite_utils.Database(memory=True) try: # Load list of dictionaries into SQLite database db[ev.table_name].insert_all(list_of_dict) except sqlite_utils.utils.sqlite3.IntegrityError as exc: print_text( f"Error inserting into table {table_name}, expected format:" ) print_text("[{col1: val1, col2: val2, ...}, ...]") raise ValueError("Invalid list_of_dict") from exc # Get the table schema table_schema = db[table_name].columns_dict # Get the SQL query with text-to-SQL prompt response_str = await ev.llm.apredict( prompt=prompt, table_name=table_name, table_schema=table_schema, question=query, ) sql_parser = DefaultSQLParser() sql_query = sql_parser.parse_response_to_sql(response_str, ev.query) try: # Execute the SQL query results = list(db.query(sql_query)) except sqlite_utils.utils.sqlite3.OperationalError as exc: print_text(f"Error executing query: {sql_query}") raise ValueError("Invalid query") from exc return JsonAnalyzerEvent( sql_query=sql_query, table_schema=table_schema, results=results ) @step async def synthesize( self, ctx: Context, ev: JsonAnalyzerEvent ) -> StopEvent: """Synthesize the response.""" llm = await ctx.get("llm", default=None) query = await ctx.get("query", default=None) response_str = llm.predict( DEFAULT_RESPONSE_SYNTHESIS_PROMPT, sql_query=ev.sql_query, table_schema=ev.table_schema, sql_response=ev.results, query_str=query, ) response_metadata = { "sql_query": ev.sql_query, "table_schema": str(ev.table_schema), } response = Response(response=response_str, metadata=response_metadata) return StopEvent(result=response)
## Create Json List¶
In [ ]:
Copied!
```
json_list = [
    {
        "name": "John Doe",
        "age": 25,
        "major": "Computer Science",
        "email": "john.doe@example.com",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "phone": "+1 123-456-7890",
        "occupation": "Software Engineer",
    },
    {
        "name": "Jane Smith",
        "age": 30,
        "major": "Business Administration",
        "email": "jane.smith@example.com",
        "address": "456 Elm St",
        "city": "San Francisco",
        "state": "CA",
        "country": "USA",
        "phone": "+1 234-567-8901",
        "occupation": "Marketing Manager",
    },
    {
        "name": "Michael Johnson",
        "age": 35,
        "major": "Finance",
        "email": "michael.johnson@example.com",
        "address": "789 Oak Ave",
        "city": "Chicago",
        "state": "IL",
        "country": "USA",
        "phone": "+1 345-678-9012",
        "occupation": "Financial Analyst",
    },
    {
        "name": "Emily Davis",
        "age": 28,
        "major": "Psychology",
        "email": "emily.davis@example.com",
        "address": "234 Pine St",
        "city": "Los Angeles",
        "state": "CA",
        "country": "USA",
        "phone": "+1 456-789-0123",
        "occupation": "Psychologist",
    },
    {
        "name": "Alex Johnson",
        "age": 27,
        "major": "Engineering",
        "email": "alex.johnson@example.com",
        "address": "567 Cedar Ln",
        "city": "Seattle",
        "state": "WA",
        "country": "USA",
        "phone": "+1 567-890-1234",
        "occupation": "Civil Engineer",
    },
    {
        "name": "Jessica Williams",
        "age": 32,
        "major": "Biology",
        "email": "jessica.williams@example.com",
        "address": "890 Walnut Ave",
        "city": "Boston",
        "state": "MA",
        "country": "USA",
        "phone": "+1 678-901-2345",
        "occupation": "Biologist",
    },
    {
        "name": "Matthew Brown",
        "age": 26,
        "major": "English Literature",
        "email": "matthew.brown@example.com",
        "address": "123 Peach St",
        "city": "Atlanta",
        "state": "GA",
        "country": "USA",
        "phone": "+1 789-012-3456",
        "occupation": "Writer",
    },
    {
        "name": "Olivia Wilson",
        "age": 29,
        "major": "Art",
        "email": "olivia.wilson@example.com",
        "address": "456 Plum Ave",
        "city": "Miami",
        "state": "FL",
        "country": "USA",
        "phone": "+1 890-123-4567",
        "occupation": "Artist",
    },
    {
        "name": "Daniel Thompson",
        "age": 31,
        "major": "Physics",
        "email": "daniel.thompson@example.com",
        "address": "789 Apple St",
        "city": "Denver",
        "state": "CO",
        "country": "USA",
        "phone": "+1 901-234-5678",
        "occupation": "Physicist",
    },
    {
        "name": "Sophia Clark",
        "age": 27,
        "major": "Sociology",
        "email": "sophia.clark@example.com",
        "address": "234 Orange Ln",
        "city": "Austin",
        "state": "TX",
        "country": "USA",
        "phone": "+1 012-345-6789",
        "occupation": "Social Worker",
    },
    {
        "name": "Christopher Lee",
        "age": 33,
        "major": "Chemistry",
        "email": "christopher.lee@example.com",
        "address": "567 Mango St",
        "city": "San Diego",
        "state": "CA",
        "country": "USA",
        "phone": "+1 123-456-7890",
        "occupation": "Chemist",
    },
    {
        "name": "Ava Green",
        "age": 28,
        "major": "History",
        "email": "ava.green@example.com",
        "address": "890 Cherry Ave",
        "city": "Philadelphia",
        "state": "PA",
        "country": "USA",
        "phone": "+1 234-567-8901",
        "occupation": "Historian",
    },
    {
        "name": "Ethan Anderson",
        "age": 30,
        "major": "Business",
        "email": "ethan.anderson@example.com",
        "address": "123 Lemon Ln",
        "city": "Houston",
        "state": "TX",
        "country": "USA",
        "phone": "+1 345-678-9012",
        "occupation": "Entrepreneur",
    },
    {
        "name": "Isabella Carter",
        "age": 28,
        "major": "Mathematics",
        "email": "isabella.carter@example.com",
        "address": "456 Grape St",
        "city": "Phoenix",
        "state": "AZ",
        "country": "USA",
        "phone": "+1 456-789-0123",
        "occupation": "Mathematician",
    },
    {
        "name": "Andrew Walker",
        "age": 32,
        "major": "Economics",
        "email": "andrew.walker@example.com",
        "address": "789 Berry Ave",
        "city": "Portland",
        "state": "OR",
        "country": "USA",
        "phone": "+1 567-890-1234",
        "occupation": "Economist",
    },
    {
        "name": "Mia Evans",
        "age": 29,
        "major": "Political Science",
        "email": "mia.evans@example.com",
        "address": "234 Lime St",
        "city": "Washington",
        "state": "DC",
        "country": "USA",
        "phone": "+1 678-901-2345",
        "occupation": "Political Analyst",
    },
]

```

json_list = [ { "name": "John Doe", "age": 25, "major": "Computer Science", "email": "john.doe@example.com", "address": "123 Main St", "city": "New York", "state": "NY", "country": "USA", "phone": "+1 123-456-7890", "occupation": "Software Engineer", }, { "name": "Jane Smith", "age": 30, "major": "Business Administration", "email": "jane.smith@example.com", "address": "456 Elm St", "city": "San Francisco", "state": "CA", "country": "USA", "phone": "+1 234-567-8901", "occupation": "Marketing Manager", }, { "name": "Michael Johnson", "age": 35, "major": "Finance", "email": "michael.johnson@example.com", "address": "789 Oak Ave", "city": "Chicago", "state": "IL", "country": "USA", "phone": "+1 345-678-9012", "occupation": "Financial Analyst", }, { "name": "Emily Davis", "age": 28, "major": "Psychology", "email": "emily.davis@example.com", "address": "234 Pine St", "city": "Los Angeles", "state": "CA", "country": "USA", "phone": "+1 456-789-0123", "occupation": "Psychologist", }, { "name": "Alex Johnson", "age": 27, "major": "Engineering", "email": "alex.johnson@example.com", "address": "567 Cedar Ln", "city": "Seattle", "state": "WA", "country": "USA", "phone": "+1 567-890-1234", "occupation": "Civil Engineer", }, { "name": "Jessica Williams", "age": 32, "major": "Biology", "email": "jessica.williams@example.com", "address": "890 Walnut Ave", "city": "Boston", "state": "MA", "country": "USA", "phone": "+1 678-901-2345", "occupation": "Biologist", }, { "name": "Matthew Brown", "age": 26, "major": "English Literature", "email": "matthew.brown@example.com", "address": "123 Peach St", "city": "Atlanta", "state": "GA", "country": "USA", "phone": "+1 789-012-3456", "occupation": "Writer", }, { "name": "Olivia Wilson", "age": 29, "major": "Art", "email": "olivia.wilson@example.com", "address": "456 Plum Ave", "city": "Miami", "state": "FL", "country": "USA", "phone": "+1 890-123-4567", "occupation": "Artist", }, { "name": "Daniel Thompson", "age": 31, "major": "Physics", "email": "daniel.thompson@example.com", "address": "789 Apple St", "city": "Denver", "state": "CO", "country": "USA", "phone": "+1 901-234-5678", "occupation": "Physicist", }, { "name": "Sophia Clark", "age": 27, "major": "Sociology", "email": "sophia.clark@example.com", "address": "234 Orange Ln", "city": "Austin", "state": "TX", "country": "USA", "phone": "+1 012-345-6789", "occupation": "Social Worker", }, { "name": "Christopher Lee", "age": 33, "major": "Chemistry", "email": "christopher.lee@example.com", "address": "567 Mango St", "city": "San Diego", "state": "CA", "country": "USA", "phone": "+1 123-456-7890", "occupation": "Chemist", }, { "name": "Ava Green", "age": 28, "major": "History", "email": "ava.green@example.com", "address": "890 Cherry Ave", "city": "Philadelphia", "state": "PA", "country": "USA", "phone": "+1 234-567-8901", "occupation": "Historian", }, { "name": "Ethan Anderson", "age": 30, "major": "Business", "email": "ethan.anderson@example.com", "address": "123 Lemon Ln", "city": "Houston", "state": "TX", "country": "USA", "phone": "+1 345-678-9012", "occupation": "Entrepreneur", }, { "name": "Isabella Carter", "age": 28, "major": "Mathematics", "email": "isabella.carter@example.com", "address": "456 Grape St", "city": "Phoenix", "state": "AZ", "country": "USA", "phone": "+1 456-789-0123", "occupation": "Mathematician", }, { "name": "Andrew Walker", "age": 32, "major": "Economics", "email": "andrew.walker@example.com", "address": "789 Berry Ave", "city": "Portland", "state": "OR", "country": "USA", "phone": "+1 567-890-1234", "occupation": "Economist", }, { "name": "Mia Evans", "age": 29, "major": "Political Science", "email": "mia.evans@example.com", "address": "234 Lime St", "city": "Washington", "state": "DC", "country": "USA", "phone": "+1 678-901-2345", "occupation": "Political Analyst", }, ]
## Define LLM¶
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-3.5-turbo")

```

llm = OpenAI(model="gpt-3.5-turbo")
### Run the Workflow!¶
In [ ]:
Copied!
```
w = JSONAnalyzeQueryEngineWorkflow()

```

w = JSONAnalyzeQueryEngineWorkflow()
In [ ]:
Copied!
```
# Run a query

query = "What is the maximum age among the individuals?"

result = await w.run(
    query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME
)

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

# Run a query query = "What is the maximum age among the individuals?" result = await w.run( query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME ) display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
> Question: What is the maximum age among the individuals?
Answer: The maximum age among the individuals is 35.
In [ ]:
Copied!
```
query = "How many individuals have an occupation related to science or engineering?"

result = await w.run(
    query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME
)

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

query = "How many individuals have an occupation related to science or engineering?" result = await w.run( query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME ) display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
> Question: How many individuals have an occupation related to science or engineering?
Answer: There are 0 individuals with an occupation related to science or engineering.
In [ ]:
Copied!
```
query = "How many individuals have a phone number starting with '+1 234'?"

result = await w.run(
    query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME
)

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

query = "How many individuals have a phone number starting with '+1 234'?" result = await w.run( query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME ) display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
> Question: How many individuals have a phone number starting with '+1 234'?
Answer: There are 2 individuals with a phone number starting with '+1 234'.
In [ ]:
Copied!
```
query = "What is the percentage of individuals residing in California (CA)?"

result = await w.run(
    query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME
)

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

query = "What is the percentage of individuals residing in California (CA)?" result = await w.run( query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME ) display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
> Question: What is the percentage of individuals residing in California (CA)?
Answer: The percentage of individuals residing in California (CA) is 18.75%.
In [ ]:
Copied!
```
query = "How many individuals have a major in Psychology?"

result = await w.run(
    query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME
)

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

query = "How many individuals have a major in Psychology?" result = await w.run( query=query, list_of_dict=json_list, llm=llm, table_name=DEFAULT_TABLE_NAME ) display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
> Question: How many individuals have a major in Psychology?
Answer: There is 1 individual who has a major in Psychology.
