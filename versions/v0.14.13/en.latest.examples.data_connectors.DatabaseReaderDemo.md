![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Database Reader¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-database

```

%pip install llama-index-readers-database
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
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
from __future__ import absolute_import

# My OpenAI Key
import os

os.environ["OPENAI_API_KEY"] = ""

from llama_index.readers.database import DatabaseReader
from llama_index.core import VectorStoreIndex

```

from __future__ import absolute_import # My OpenAI Key import os os.environ["OPENAI_API_KEY"] = "" from llama_index.readers.database import DatabaseReader from llama_index.core import VectorStoreIndex
In [ ]:
Copied!
```
# Initialize DatabaseReader object with the following parameters:

db = DatabaseReader(
    scheme="postgresql",  # Database Scheme
    host="localhost",  # Database Host
    port="5432",  # Database Port
    user="postgres",  # Database User
    password="FakeExamplePassword",  # Database Password
    dbname="postgres",  # Database Name
)

```

# Initialize DatabaseReader object with the following parameters: db = DatabaseReader( scheme="postgresql", # Database Scheme host="localhost", # Database Host port="5432", # Database Port user="postgres", # Database User password="FakeExamplePassword", # Database Password dbname="postgres", # Database Name )
In [ ]:
Copied!
```
### DatabaseReader class ###
# db is an instance of DatabaseReader:
print(type(db))
# DatabaseReader available method:
print(type(db.load_data))

### SQLDatabase class ###
# db.sql is an instance of SQLDatabase:
print(type(db.sql_database))
# SQLDatabase available methods:
print(type(db.sql_database.from_uri))
print(type(db.sql_database.get_single_table_info))
print(type(db.sql_database.get_table_columns))
print(type(db.sql_database.get_usable_table_names))
print(type(db.sql_database.insert_into_table))
print(type(db.sql_database.run_sql))
# SQLDatabase available properties:
print(type(db.sql_database.dialect))
print(type(db.sql_database.engine))

```

### DatabaseReader class ### # db is an instance of DatabaseReader: print(type(db)) # DatabaseReader available method: print(type(db.load_data)) ### SQLDatabase class ### # db.sql is an instance of SQLDatabase: print(type(db.sql_database)) # SQLDatabase available methods: print(type(db.sql_database.from_uri)) print(type(db.sql_database.get_single_table_info)) print(type(db.sql_database.get_table_columns)) print(type(db.sql_database.get_usable_table_names)) print(type(db.sql_database.insert_into_table)) print(type(db.sql_database.run_sql)) # SQLDatabase available properties: print(type(db.sql_database.dialect)) print(type(db.sql_database.engine))
In [ ]:
Copied!
```
### Testing DatabaseReader
### from SQLDatabase, SQLAlchemy engine and Database URI:

# From SQLDatabase instance:
print(type(db.sql_database))
db_from_sql_database = DatabaseReader(sql_database=db.sql_database)
print(type(db_from_sql_database))

# From SQLAlchemy engine:
print(type(db.sql_database.engine))
db_from_engine = DatabaseReader(engine=db.sql_database.engine)
print(type(db_from_engine))

# From Database URI:
print(type(db.uri))
db_from_uri = DatabaseReader(uri=db.uri)
print(type(db_from_uri))

```

### Testing DatabaseReader ### from SQLDatabase, SQLAlchemy engine and Database URI: # From SQLDatabase instance: print(type(db.sql_database)) db_from_sql_database = DatabaseReader(sql_database=db.sql_database) print(type(db_from_sql_database)) # From SQLAlchemy engine: print(type(db.sql_database.engine)) db_from_engine = DatabaseReader(engine=db.sql_database.engine) print(type(db_from_engine)) # From Database URI: print(type(db.uri)) db_from_uri = DatabaseReader(uri=db.uri) print(type(db_from_uri))
In [ ]:
Copied!
```
# The below SQL Query example returns a list values of each row
# with concatenated text from the name and age columns
# from the users table where the age is greater than or equal to 18

query = f"""
    SELECT
        CONCAT(name, ' is ', age, ' years old.') AS text
    FROM public.users
    WHERE age >= 18
    """

```

# The below SQL Query example returns a list values of each row # with concatenated text from the name and age columns # from the users table where the age is greater than or equal to 18 query = f""" SELECT CONCAT(name, ' is ', age, ' years old.') AS text FROM public.users WHERE age >= 18 """
In [ ]:
Copied!
```
# Please refer to llama_index.utilities.sql_wrapper
# SQLDatabase.run_sql method
texts = db.sql_database.run_sql(command=query)

# Display type(texts) and texts
# type(texts) must return <class 'list'>
print(type(texts))

# Documents must return a list of Tuple objects
print(texts)

```

# Please refer to llama_index.utilities.sql_wrapper # SQLDatabase.run_sql method texts = db.sql_database.run_sql(command=query) # Display type(texts) and texts # type(texts) must return  print(type(texts)) # Documents must return a list of Tuple objects print(texts)
In [ ]:
Copied!
```
# Please refer to llama_index.readers.database.DatabaseReader.load_data
# DatabaseReader.load_data method
documents = db.load_data(query=query)

# Display type(documents) and documents
# type(documents) must return <class 'list'>
print(type(documents))

# Documents must return a list of Document objects
print(documents)

```

# Please refer to llama_index.readers.database.DatabaseReader.load_data # DatabaseReader.load_data method documents = db.load_data(query=query) # Display type(documents) and documents # type(documents) must return  print(type(documents)) # Documents must return a list of Document objects print(documents)
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
