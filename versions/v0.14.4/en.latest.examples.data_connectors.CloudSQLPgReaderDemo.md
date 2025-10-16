# Google Cloud SQL for PostgreSQL - `PostgresReader`¶
> Cloud SQL is a fully managed relational database service that offers high performance, seamless integration, and impressive scalability. It offers MySQL, PostgreSQL, and SQL Server database engines. Extend your database application to build AI-powered experiences leveraging Cloud SQL's LlamaIndex integrations.
This notebook goes over how to use `Cloud SQL for PostgreSQL` to retrieve data as documents with the `PostgresReader` class.
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
Install the integration library, `llama-index-cloud-sql-pg`.
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
TABLE_NAME = "reader_table"  # @param {type: "string"}
USER = "postgres"  # @param {type: "string"}
PASSWORD = "my-password"  # @param {type: "string"}

```

# @title Set Your Values Here { display-mode: "form" } REGION = "us-central1" # @param {type: "string"} INSTANCE = "my-primary" # @param {type: "string"} DATABASE = "my-database" # @param {type: "string"} TABLE_NAME = "reader_table" # @param {type: "string"} USER = "postgres" # @param {type: "string"} PASSWORD = "my-password" # @param {type: "string"}
### PostgresEngine Connection Pool¶
One of the requirements and arguments to establish Cloud SQL as a reader is a `PostgresEngine` object. The `PostgresEngine` configures a connection pool to your Cloud SQL database, enabling successful connections from your application and following industry best practices.
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
### Create PostgresReader¶
When creating an `PostgresReader` for fetching data from Cloud SQL Postgres, you have two main options to specify the data you want to load:
  * using the table_name argument - When you specify the table_name argument, you're telling the reader to fetch all the data from the given table.
  * using the query argument - When you specify the query argument, you can provide a custom SQL query to fetch the data. This allows you to have full control over the SQL query, including selecting specific columns, applying filters, sorting, joining tables, etc.


### Load Documents using the `table_name` argument¶
#### Load Documents via default table¶
The reader returns a list of Documents from the table using the first column as text and all other columns as metadata. The default table will have the first column as text and the second column as metadata (JSON). Each row becomes a document.
In [ ]:
Copied!
```
from llama_index_cloud_sql_pg import PostgresReader

# Creating a basic PostgresReader object
reader = await PostgresReader.create(
    engine,
    table_name=TABLE_NAME,
    # schema_name=SCHEMA_NAME,
)

```

from llama_index_cloud_sql_pg import PostgresReader # Creating a basic PostgresReader object reader = await PostgresReader.create( engine, table_name=TABLE_NAME, # schema_name=SCHEMA_NAME, )
#### Load documents via custom table/metadata or custom page content columns¶
In [ ]:
Copied!
```
reader = await PostgresReader.create(
    engine,
    table_name=TABLE_NAME,
    # schema_name=SCHEMA_NAME,
    content_columns=["product_name"],  # Optional
    metadata_columns=["id"],  # Optional
)

```

reader = await PostgresReader.create( engine, table_name=TABLE_NAME, # schema_name=SCHEMA_NAME, content_columns=["product_name"], # Optional metadata_columns=["id"], # Optional )
### Load Documents using a SQL query¶
The query parameter allows users to specify a custom SQL query which can include filters to load specific documents from a database.
In [ ]:
Copied!
```
table_name = "products"
content_columns = ["product_name", "description"]
metadata_columns = ["id", "content"]

reader = PostgresReader.create(
    engine=engine,
    query=f"SELECT * FROM {table_name};",
    content_columns=content_columns,
    metadata_columns=metadata_columns,
)

```

table_name = "products" content_columns = ["product_name", "description"] metadata_columns = ["id", "content"] reader = PostgresReader.create( engine=engine, query=f"SELECT * FROM {table_name};", content_columns=content_columns, metadata_columns=metadata_columns, )
**Note** : If the `content_columns` and `metadata_columns` are not specified, the reader will automatically treat the first returned column as the document’s `text` and all subsequent columns as `metadata`.
### Set page content format¶
The reader returns a list of Documents, with one document per row, with page content in specified string format, i.e. text (space separated concatenation), JSON, YAML, CSV, etc. JSON and YAML formats include headers, while text and CSV do not include field headers.
In [ ]:
Copied!
```
reader = await PostgresReader.create(
    engine,
    table_name=TABLE_NAME,
    # schema_name=SCHEMA_NAME,
    content_columns=["product_name", "description"],
    format="YAML",
)

```

reader = await PostgresReader.create( engine, table_name=TABLE_NAME, # schema_name=SCHEMA_NAME, content_columns=["product_name", "description"], format="YAML", )
### Load the documents¶
You can choose to load the documents in two ways:
  * Load all the data at once
  * Lazy load data


#### Load data all at once¶
In [ ]:
Copied!
```
docs = await reader.aload_data()

print(docs)

```

docs = await reader.aload_data() print(docs)
#### Lazy Load the data¶
In [ ]:
Copied!
```
docs_iterable = reader.alazy_load_data()

docs = []
async for doc in docs_iterable:
    docs.append(doc)

print(docs)

```

docs_iterable = reader.alazy_load_data() docs = [] async for doc in docs_iterable: docs.append(doc) print(docs)
