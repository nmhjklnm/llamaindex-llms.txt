# Cassandra Database Tools¶
Apache Cassandra® is a widely used database for storing transactional application data. The introduction of functions and tooling in Large Language Models has opened up some exciting use cases for existing data in Generative AI applications. The Cassandra Database toolkit enables AI engineers to efficiently integrate Agents with Cassandra data, offering the following features:
  * Fast data access through optimized queries. Most queries should run in single-digit ms or less.
  * Schema introspection to enhance LLM reasoning capabilities
  * Compatibility with various Cassandra deployments, including Apache Cassandra®, DataStax Enterprise™, and DataStax Astra™
  * Currently, the toolkit is limited to SELECT queries and schema introspection operations. (Safety first)


## Quick Start¶
  * Install the cassio library
  * Set environment variables for the Cassandra database you are connecting to
  * Initialize CassandraDatabase
  * Pass the tools to your agent with spec.to_tool_list()
  * Sit back and watch it do all your work for you


## Theory of Operation¶
Cassandra Query Language (CQL) is the primary _human-centric_ way of interacting with a Cassandra database. While offering some flexibility when generating queries, it requires knowledge of Cassandra data modeling best practices. LLM function calling gives an agent the ability to reason and then choose a tool to satisfy the request. Agents using LLMs should reason using Cassandra-specific logic when choosing the appropriate tool or chain of tools. This reduces the randomness introduced when LLMs are forced to provide a top-down solution. Do you want an LLM to have complete unfettered access to your database? Yeah. Probably not. To accomplish this, we provide a prompt for use when constructing questions for the agent:
```
You are an Apache Cassandra expert query analysis bot with the following features 
and rules:
 - You will take a question from the end user about finding specific 
   data in the database.
 - You will examine the schema of the database and create a query path. 
 - You will provide the user with the correct query to find the data they are looking 
   for, showing the steps provided by the query path.
 - You will use best practices for querying Apache Cassandra using partition keys 
   and clustering columns.
 - Avoid using ALLOW FILTERING in the query.
 - The goal is to find a query path, so it may take querying other tables to get 
   to the final answer. 

The following is an example of a query path in JSON format:

 {
  "query_paths": [
    {
      "description": "Direct query to users table using email",
      "steps": [
        {
          "table": "user_credentials",
          "query": 
             "SELECT userid FROM user_credentials WHERE email = 'example@example.com';"
        },
        {
          "table": "users",
          "query": "SELECT * FROM users WHERE userid = ?;"
        }
      ]
    }
  ]
}

```

## Tools Provided¶
###  `cassandra_db_schema`¶
Gathers all schema information for the connected database or a specific schema. Critical for the agent when determining actions.
###  `cassandra_db_select_table_data`¶
Selects data from a specific keyspace and table. The agent can pass paramaters for a predicate and limits on the number of returned records.
###  `cassandra_db_query`¶
Experimental alternative to `cassandra_db_select_table_data` which takes a query string completely formed by the agent instead of parameters. _Warning_ : This can lead to unusual queries that may not be as performant(or even work). This may be removed in future releases. If it does something cool, we want to know about that too. You never know!
## Environment Setup¶
Install the following Python modules:
```
pip install ipykernel python-dotenv cassio llama-index llama-index-agent-openai llama-index-llms-openai llama-index-tools-cassandra

```

### .env file¶
Connection is via `cassio` using `auto=True` parameter, and the notebook uses OpenAI. You should create a `.env` file accordingly.
For Cassandra, set:
```
CASSANDRA_CONTACT_POINTS
CASSANDRA_USERNAME
CASSANDRA_PASSWORD
CASSANDRA_KEYSPACE

```

For Astra, set:
```
ASTRA_DB_APPLICATION_TOKEN
ASTRA_DB_DATABASE_ID
ASTRA_DB_KEYSPACE

```

For example:
```
# Connection to Astra:
ASTRA_DB_DATABASE_ID=a1b2c3d4-...
ASTRA_DB_APPLICATION_TOKEN=AstraCS:...
ASTRA_DB_KEYSPACE=notebooks

# Also set 
OPENAI_API_KEY=sk-....

```

(You may also modify the below code to directly connect with `cassio`.)
In [ ]:
Copied!
```
from dotenv import load_dotenv

load_dotenv(override=True)

```

from dotenv import load_dotenv load_dotenv(override=True)
In [ ]:
Copied!
```
# Import necessary libraries
import os

import cassio

from llama_index.tools.cassandra.base import CassandraDatabaseToolSpec
from llama_index.tools.cassandra.cassandra_database_wrapper import (
    CassandraDatabase,
)

from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI

```

# Import necessary libraries import os import cassio from llama_index.tools.cassandra.base import CassandraDatabaseToolSpec from llama_index.tools.cassandra.cassandra_database_wrapper import ( CassandraDatabase, ) from llama_index.agent.openai import OpenAIAgent from llama_index.llms.openai import OpenAI
## Connect to a Cassandra Database¶
In [ ]:
Copied!
```
cassio.init(auto=True)

session = cassio.config.resolve_session()
if not session:
    raise Exception(
        "Check environment configuration or manually configure cassio connection parameters"
    )

```

cassio.init(auto=True) session = cassio.config.resolve_session() if not session: raise Exception( "Check environment configuration or manually configure cassio connection parameters" )
In [ ]:
Copied!
```
# Test data prep

session = cassio.config.resolve_session()

session.execute("""DROP KEYSPACE IF EXISTS llamaindex_agent_test; """)

session.execute(
    """
CREATE KEYSPACE if not exists llamaindex_agent_test 
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
"""
)

session.execute(
    """
    CREATE TABLE IF NOT EXISTS llamaindex_agent_test.user_credentials (
    user_email text PRIMARY KEY,
    user_id UUID,
    password TEXT
);
"""
)

session.execute(
    """
    CREATE TABLE IF NOT EXISTS llamaindex_agent_test.users (
    id UUID PRIMARY KEY,
    name TEXT,
    email TEXT
);"""
)

session.execute(
    """
    CREATE TABLE IF NOT EXISTS llamaindex_agent_test.user_videos ( 
    user_id UUID,
    video_id UUID,
    title TEXT,
    description TEXT,
    PRIMARY KEY (user_id, video_id)
);
"""
)

user_id = "522b1fe2-2e36-4cef-a667-cd4237d08b89"
video_id = "27066014-bad7-9f58-5a30-f63fe03718f6"

session.execute(
    f"""
    INSERT INTO llamaindex_agent_test.user_credentials (user_id, user_email) 
    VALUES ({user_id}, 'patrick@datastax.com');
"""
)

session.execute(
    f"""
    INSERT INTO llamaindex_agent_test.users (id, name, email) 
    VALUES ({user_id}, 'Patrick McFadin', 'patrick@datastax.com');
"""
)

session.execute(
    f"""
    INSERT INTO llamaindex_agent_test.user_videos (user_id, video_id, title)
    VALUES ({user_id}, {video_id}, 'Use Langflow to Build an LLM Application in 5 Minutes');
"""
)

session.set_keyspace("llamaindex_agent_test")

```

# Test data prep session = cassio.config.resolve_session() session.execute("""DROP KEYSPACE IF EXISTS llamaindex_agent_test; """) session.execute( """ CREATE KEYSPACE if not exists llamaindex_agent_test WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}; """ ) session.execute( """ CREATE TABLE IF NOT EXISTS llamaindex_agent_test.user_credentials ( user_email text PRIMARY KEY, user_id UUID, password TEXT ); """ ) session.execute( """ CREATE TABLE IF NOT EXISTS llamaindex_agent_test.users ( id UUID PRIMARY KEY, name TEXT, email TEXT );""" ) session.execute( """ CREATE TABLE IF NOT EXISTS llamaindex_agent_test.user_videos ( user_id UUID, video_id UUID, title TEXT, description TEXT, PRIMARY KEY (user_id, video_id) ); """ ) user_id = "522b1fe2-2e36-4cef-a667-cd4237d08b89" video_id = "27066014-bad7-9f58-5a30-f63fe03718f6" session.execute( f""" INSERT INTO llamaindex_agent_test.user_credentials (user_id, user_email) VALUES ({user_id}, 'patrick@datastax.com'); """ ) session.execute( f""" INSERT INTO llamaindex_agent_test.users (id, name, email) VALUES ({user_id}, 'Patrick McFadin', 'patrick@datastax.com'); """ ) session.execute( f""" INSERT INTO llamaindex_agent_test.user_videos (user_id, video_id, title) VALUES ({user_id}, {video_id}, 'Use Langflow to Build an LLM Application in 5 Minutes'); """ ) session.set_keyspace("llamaindex_agent_test")
In [ ]:
Copied!
```
# Create a CassandraDatabaseToolSpec object
db = CassandraDatabase()

spec = CassandraDatabaseToolSpec(db=db)

tools = spec.to_tool_list()
for tool in tools:
    print(tool.metadata.name)
    print(tool.metadata.description)
    print(tool.metadata.fn_schema)

```

# Create a CassandraDatabaseToolSpec object db = CassandraDatabase() spec = CassandraDatabaseToolSpec(db=db) tools = spec.to_tool_list() for tool in tools: print(tool.metadata.name) print(tool.metadata.description) print(tool.metadata.fn_schema)
```
cassandra_db_schema
cassandra_db_schema(keyspace: str) -> List[llama_index.core.schema.Document]
Input to this tool is a keyspace name, output is a table description
            of Apache Cassandra tables.
            If the query is not correct, an error message will be returned.
            If an error is returned, report back to the user that the keyspace
            doesn't exist and stop.

        Args:
            keyspace (str): The name of the keyspace for which to return the schema.

        Returns:
            List[Document]: A list of Document objects, each containing a table description.
        
<class 'pydantic.main.cassandra_db_schema'>
cassandra_db_select_table_data
cassandra_db_select_table_data(keyspace: str, table: str, predicate: str, limit: int) -> List[llama_index.core.schema.Document]
Tool for getting data from a table in an Apache Cassandra database.
            Use the WHERE clause to specify the predicate for the query that uses the
            primary key. A blank predicate will return all rows. Avoid this if possible.
            Use the limit to specify the number of rows to return. A blank limit will
            return all rows.

        Args:
            keyspace (str): The name of the keyspace containing the table.
            table (str): The name of the table for which to return data.
            predicate (str): The predicate for the query that uses the primary key.
            limit (int): The maximum number of rows to return.

        Returns:
            List[Document]: A list of Document objects, each containing a row of data.
        
<class 'pydantic.main.cassandra_db_select_table_data'>

```

In [ ]:
Copied!
```
# Choose the LLM that will drive the agent
# Only certain models support this
llm = OpenAI(model="gpt-4-1106-preview")

# Create the Agent with our tools. Verbose will echo the agent's actions
agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True)

```

# Choose the LLM that will drive the agent # Only certain models support this llm = OpenAI(model="gpt-4-1106-preview") # Create the Agent with our tools. Verbose will echo the agent's actions agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True)
### Invoking the agent with tools¶
We've created an agent that uses an LLM for reasoning and communication with a tool list for actions, Now we can simply ask questions of the agent and watch it utilize the tools we've given it.
In [ ]:
Copied!
```
# Ask our new agent a series of questions. What how the agent uses tools to get the answers.
agent.chat("What tables are in the keyspace llamaindex_agent_test?")
agent.chat("What is the userid for patrick@datastax.com ?")
agent.chat("What videos did user patrick@datastax.com upload?")

```

# Ask our new agent a series of questions. What how the agent uses tools to get the answers. agent.chat("What tables are in the keyspace llamaindex_agent_test?") agent.chat("What is the userid for patrick@datastax.com ?") agent.chat("What videos did user patrick@datastax.com upload?")
```
Added user message to memory: What tables are in the keyspace llamaindex_agent_test?
=== Calling Function ===
Calling function: cassandra_db_schema with args: {"keyspace":"llamaindex_agent_test"}
Got output: [Document(id_='4b6011e6-62e6-4db2-9198-046534b7c8dd', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text='Table Name: user_credentials\n- Keyspace: llamaindex_agent_test\n- Columns\n  - password (text)\n  - user_email (text)\n  - user_id (uuid)\n- Partition Keys: (user_email)\n- Clustering Keys: \n\nTable Name: user_videos\n- Keyspace: llamaindex_agent_test\n- Columns\n  - description (text)\n  - title (text)\n  - user_id (uuid)\n  - video_id (uuid)\n- Partition Keys: (user_id)\n- Clustering Keys: (video_id asc)\n\n\nTable Name: users\n- Keyspace: llamaindex_agent_test\n- Columns\n  - email (text)\n  - id (uuid)\n  - name (text)\n- Partition Keys: (id)\n- Clustering Keys: \n\n', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n')]
========================

Added user message to memory: What is the userid for patrick@datastax.com ?
=== Calling Function ===
Calling function: cassandra_db_select_table_data with args: {"keyspace":"llamaindex_agent_test","table":"user_credentials","predicate":"user_email = 'patrick@datastax.com'","limit":1}
Got output: [Document(id_='e5620177-c735-46f8-a09a-a0e062efcdec', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text="Row(user_email='patrick@datastax.com', password=None, user_id=UUID('522b1fe2-2e36-4cef-a667-cd4237d08b89'))", start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n')]
========================

Added user message to memory: What videos did user patrick@datastax.com upload?
=== Calling Function ===
Calling function: cassandra_db_select_table_data with args: {"keyspace":"llamaindex_agent_test","table":"user_videos","predicate":"user_id = 522b1fe2-2e36-4cef-a667-cd4237d08b89","limit":10}
Got output: [Document(id_='e3ecfba1-e8e1-4ce3-b321-3f51e12077a1', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text="Row(user_id=UUID('522b1fe2-2e36-4cef-a667-cd4237d08b89'), video_id=UUID('27066014-bad7-9f58-5a30-f63fe03718f6'), description=None, title='Use Langflow to Build an LLM Application in 5 Minutes')", start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n')]
========================

```

Out[ ]:
```
AgentChatResponse(response='The user `patrick@datastax.com` uploaded the following video in the `llamaindex_agent_test` keyspace:\n\n- Title: "Use Langflow to Build an LLM Application in 5 Minutes"\n- Video ID: `27066014-bad7-9f58-5a30-f63fe03718f6`\n- Description: Not provided', sources=[ToolOutput(content='[Document(id_=\'e3ecfba1-e8e1-4ce3-b321-3f51e12077a1\', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text="Row(user_id=UUID(\'522b1fe2-2e36-4cef-a667-cd4237d08b89\'), video_id=UUID(\'27066014-bad7-9f58-5a30-f63fe03718f6\'), description=None, title=\'Use Langflow to Build an LLM Application in 5 Minutes\')", start_char_idx=None, end_char_idx=None, text_template=\'{metadata_str}\\n\\n{content}\', metadata_template=\'{key}: {value}\', metadata_seperator=\'\\n\')]', tool_name='cassandra_db_select_table_data', raw_input={'args': (), 'kwargs': {'keyspace': 'llamaindex_agent_test', 'table': 'user_videos', 'predicate': 'user_id = 522b1fe2-2e36-4cef-a667-cd4237d08b89', 'limit': 10}}, raw_output=[Document(id_='e3ecfba1-e8e1-4ce3-b321-3f51e12077a1', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text="Row(user_id=UUID('522b1fe2-2e36-4cef-a667-cd4237d08b89'), video_id=UUID('27066014-bad7-9f58-5a30-f63fe03718f6'), description=None, title='Use Langflow to Build an LLM Application in 5 Minutes')", start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n')], is_error=False)], source_nodes=[], is_dummy_stream=False)
```

