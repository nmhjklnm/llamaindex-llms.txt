# Google Cloud SQL for PostgreSQL - `PostgresDocumentStore` & `PostgresIndexStore`¶
> Cloud SQL is a fully managed relational database service that offers high performance, seamless integration, and impressive scalability. It offers MySQL, PostgreSQL, and SQL Server database engines. Extend your database application to build AI-powered experiences leveraging Cloud SQL's LlamaIndex integrations.
This notebook goes over how to use `Cloud SQL for PostgreSQL` to store documents and indexes with the `PostgresDocumentStore` and `PostgresIndexStore` classes.
Learn more about the package on GitHub.
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
## Before you begin¶
To run this notebook, you will need to do the following:
  * Create a Google Cloud Project
  * Enable the Cloud SQL Admin API.
  * Create a Cloud SQL instance.
  * Create a Cloud SQL database.
  * Add a User to the database.


### 🦙 Library Installation¶
Install the integration library, `llama-index-cloud-sql-pg`, and the library for the embedding service, `llama-index-embeddings-vertex`.
In [ ]:
Copied!
```
%pip install --upgrade --quiet llama-index-cloud-sql-pg llama-index-llms-vertex llama-index

```

%pip install --upgrade --quiet llama-index-cloud-sql-pg llama-index-llms-vertex llama-index
**Colab only:** Uncomment the following cell to restart the kernel or use the button to restart the kernel. For Vertex AI Workbench you can restart the terminal using the button on top.
In [ ]:
Copied!
```
# # Automatically restart kernel after installs so that your environment can access the new packages
# import IPython

# app = IPython.Application.instance()
# app.kernel.do_shutdown(True)

```

# # Automatically restart kernel after installs so that your environment can access the new packages # import IPython # app = IPython.Application.instance() # app.kernel.do_shutdown(True)
### 🔐 Authentication¶
Authenticate to Google Cloud as the IAM user logged into this notebook in order to access your Google Cloud Project.
  * If you are using Colab to run this notebook, use the cell below and continue.
  * If you are using Vertex AI Workbench, check out the setup instructions here.


In [ ]:
Copied!
```
from google.colab import auth

auth.authenticate_user()

```

from google.colab import auth auth.authenticate_user()
### ☁ Set Your Google Cloud Project¶
Set your Google Cloud project so that you can leverage Google Cloud resources within this notebook.
If you don't know your project ID, try the following:
  * Run `gcloud config list`.
  * Run `gcloud projects list`.
  * See the support page: Locate the project ID.


In [ ]:
Copied!
```
# @markdown Please fill in the value below with your Google Cloud project ID and then run the cell.

PROJECT_ID = "my-project-id"  # @param {type:"string"}

# Set the project id
!gcloud config set project {PROJECT_ID}

```

# @markdown Please fill in the value below with your Google Cloud project ID and then run the cell. PROJECT_ID = "my-project-id" # @param {type:"string"} # Set the project id !gcloud config set project {PROJECT_ID}
## Basic Usage¶
### Set Cloud SQL database values¶
Find your database values, in the Cloud SQL Instances page.
In [ ]:
Copied!
```
# @title Set Your Values Here { display-mode: "form" }
REGION = "us-central1"  # @param {type: "string"}
INSTANCE = "my-primary"  # @param {type: "string"}
DATABASE = "my-database"  # @param {type: "string"}
TABLE_NAME = "document_store"  # @param {type: "string"}
USER = "postgres"  # @param {type: "string"}
PASSWORD = "my-password"  # @param {type: "string"}

```

# @title Set Your Values Here { display-mode: "form" } REGION = "us-central1" # @param {type: "string"} INSTANCE = "my-primary" # @param {type: "string"} DATABASE = "my-database" # @param {type: "string"} TABLE_NAME = "document_store" # @param {type: "string"} USER = "postgres" # @param {type: "string"} PASSWORD = "my-password" # @param {type: "string"}
### PostgresEngine Connection Pool¶
One of the requirements and arguments to establish Cloud SQL as a vector store is a `PostgresEngine` object. The `PostgresEngine` configures a connection pool to your Cloud SQL database, enabling successful connections from your application and following industry best practices.
To create a `PostgresEngine` using `PostgresEngine.from_instance()` you need to provide only 4 things:
  1. `project_id` : Project ID of the Google Cloud Project where the Cloud SQL instance is located.
  2. `region` : Region where the Cloud SQL instance is located.
  3. `instance` : The name of the Cloud SQL instance.
  4. `database` : The name of the database to connect to on the Cloud SQL instance.


By default, IAM database authentication will be used as the method of database authentication. This library uses the IAM principal belonging to the Application Default Credentials (ADC) sourced from the envionment.
For more informatin on IAM database authentication please see:
  * Configure an instance for IAM database authentication
  * Manage users with IAM database authentication


Optionally, built-in database authentication using a username and password to access the Cloud SQL database can also be used. Just provide the optional `user` and `password` arguments to `PostgresEngine.from_instance()`:
  * `user` : Database user to use for built-in database authentication and login
  * `password` : Database password to use for built-in database authentication and login.


**Note:** This tutorial demonstrates the async interface. All async methods have corresponding sync methods.
In [ ]:
Copied!
```
from llama_index_cloud_sql_pg import PostgresEngine

engine = await PostgresEngine.afrom_instance(
    project_id=PROJECT_ID,
    region=REGION,
    instance=INSTANCE,
    database=DATABASE,
    user=USER,
    password=PASSWORD,
)

```

from llama_index_cloud_sql_pg import PostgresEngine engine = await PostgresEngine.afrom_instance( project_id=PROJECT_ID, region=REGION, instance=INSTANCE, database=DATABASE, user=USER, password=PASSWORD, )
### Initialize a table¶
The `PostgresDocumentStore` class requires a database table. The `PostgresEngine` engine has a helper method `init_doc_store_table()` that can be used to create a table with the proper schema for you.
In [ ]:
Copied!
```
await engine.ainit_doc_store_table(
    table_name=TABLE_NAME,
)

```

await engine.ainit_doc_store_table( table_name=TABLE_NAME, )
#### Optional Tip: 💡¶
You can also specify a schema name by passing `schema_name` wherever you pass `table_name`.
In [ ]:
Copied!
```
SCHEMA_NAME = "my_schema"

await engine.ainit_doc_store_table(
    table_name=TABLE_NAME,
    schema_name=SCHEMA_NAME,
)

```

SCHEMA_NAME = "my_schema" await engine.ainit_doc_store_table( table_name=TABLE_NAME, schema_name=SCHEMA_NAME, )
### Initialize a default PostgresDocumentStore¶
In [ ]:
Copied!
```
from llama_index_cloud_sql_pg import PostgresDocumentStore

doc_store = await PostgresDocumentStore.create(
    engine=engine,
    table_name=TABLE_NAME,
    # schema_name=SCHEMA_NAME
)

```

from llama_index_cloud_sql_pg import PostgresDocumentStore doc_store = await PostgresDocumentStore.create( engine=engine, table_name=TABLE_NAME, # schema_name=SCHEMA_NAME )
### Download data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
### Load documents¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham").load_data()
print("Document ID:", documents[0].doc_id)

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham").load_data() print("Document ID:", documents[0].doc_id)
### Parse into nodes¶
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

nodes = SentenceSplitter().get_nodes_from_documents(documents)

```

from llama_index.core.node_parser import SentenceSplitter nodes = SentenceSplitter().get_nodes_from_documents(documents)
### Set up an IndexStore¶
In [ ]:
Copied!
```
from llama_index_cloud_sql_pg import PostgresIndexStore


INDEX_TABLE_NAME = "index_store"
await engine.ainit_index_store_table(
    table_name=INDEX_TABLE_NAME,
)

index_store = await PostgresIndexStore.create(
    engine=engine,
    table_name=INDEX_TABLE_NAME,
    # schema_name=SCHEMA_NAME
)

```

from llama_index_cloud_sql_pg import PostgresIndexStore INDEX_TABLE_NAME = "index_store" await engine.ainit_index_store_table( table_name=INDEX_TABLE_NAME, ) index_store = await PostgresIndexStore.create( engine=engine, table_name=INDEX_TABLE_NAME, # schema_name=SCHEMA_NAME )
### Add to Docstore¶
In [ ]:
Copied!
```
from llama_index.core import StorageContext

storage_context = StorageContext.from_defaults(
    docstore=doc_store, index_store=index_store
)

storage_context.docstore.add_documents(nodes)

```

from llama_index.core import StorageContext storage_context = StorageContext.from_defaults( docstore=doc_store, index_store=index_store ) storage_context.docstore.add_documents(nodes)
## Use with Indexes¶
The Document Store can be used with multiple indexes. Each index uses the same underlying nodes.
In [ ]:
Copied!
```
from llama_index.core import Settings, SimpleKeywordTableIndex, SummaryIndex
from llama_index.llms.vertex import Vertex

Settings.llm = Vertex(model="gemini-1.5-flash", project=PROJECT_ID)
summary_index = SummaryIndex(nodes, storage_context=storage_context)
keyword_table_index = SimpleKeywordTableIndex(
    nodes, storage_context=storage_context
)

```

from llama_index.core import Settings, SimpleKeywordTableIndex, SummaryIndex from llama_index.llms.vertex import Vertex Settings.llm = Vertex(model="gemini-1.5-flash", project=PROJECT_ID) summary_index = SummaryIndex(nodes, storage_context=storage_context) keyword_table_index = SimpleKeywordTableIndex( nodes, storage_context=storage_context )
### Query the index¶
In [ ]:
Copied!
```
query_engine = summary_index.as_query_engine()
response = query_engine.query("What did the author do?")
print(response)

```

query_engine = summary_index.as_query_engine() response = query_engine.query("What did the author do?") print(response)
## Load existing indexes¶
The Document Store can be used with multiple indexes. Each index uses the same underlying nodes.
In [ ]:
Copied!
```
# note down index IDs
list_id = summary_index.index_id
keyword_id = keyword_table_index.index_id

```

# note down index IDs list_id = summary_index.index_id keyword_id = keyword_table_index.index_id
In [ ]:
Copied!
```
from llama_index.core import load_index_from_storage

# re-create storage context
storage_context = StorageContext.from_defaults(
    docstore=doc_store, index_store=index_store
)

# load indices
summary_index = load_index_from_storage(
    storage_context=storage_context, index_id=list_id
)
keyword_table_index = load_index_from_storage(
    storage_context=storage_context, index_id=keyword_id
)

```

from llama_index.core import load_index_from_storage # re-create storage context storage_context = StorageContext.from_defaults( docstore=doc_store, index_store=index_store ) # load indices summary_index = load_index_from_storage( storage_context=storage_context, index_id=list_id ) keyword_table_index = load_index_from_storage( storage_context=storage_context, index_id=keyword_id )
