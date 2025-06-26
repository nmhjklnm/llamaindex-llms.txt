![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Weaviate Reader¶
In [ ]:
Copied!
```
%pip install llama-index-readers-weaviate

```

%pip install llama-index-readers-weaviate
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
import weaviate
from llama_index.readers.weaviate import WeaviateReader

```

import weaviate from llama_index.readers.weaviate import WeaviateReader
In [ ]:
Copied!
```
# See https://weaviate.io/developers/weaviate/client-libraries/python
# for more details on authentication
resource_owner_config = weaviate.AuthClientPassword(
    username="<username>",
    password="<password>",
)

# initialize reader
reader = WeaviateReader(
    "https://<cluster-id>.semi.network/",
    auth_client_secret=resource_owner_config,
)

```

# See https://weaviate.io/developers/weaviate/client-libraries/python # for more details on authentication resource_owner_config = weaviate.AuthClientPassword( username="", password="", ) # initialize reader reader = WeaviateReader( "https://.semi.network/", auth_client_secret=resource_owner_config, )
You have two options for the Weaviate reader: 1) directly specify the class_name and properties, or 2) input the raw graphql_query. Examples are shown below.
In [ ]:
Copied!
```
# 1) load data using class_name and properties
# docs = reader.load_data(
#    class_name="Author", properties=["name", "description"], separate_documents=True
# )

documents = reader.load_data(
    class_name="<class_name>",
    properties=["property1", "property2", "..."],
    separate_documents=True,
)

```

# 1) load data using class_name and properties # docs = reader.load_data( # class_name="Author", properties=["name", "description"], separate_documents=True # ) documents = reader.load_data( class_name="", properties=["property1", "property2", "..."], separate_documents=True, )
In [ ]:
Copied!
```
# 2) example GraphQL query
# query = """
# {
#   Get {
#     Author {
#       name
#       description
#     }
#   }
# }
# """
# docs = reader.load_data(graphql_query=query, separate_documents=True)

query = """
{
  Get {
    <class_name> {
      <property1>
      <property2>
      ...
    }
  }
}
"""

documents = reader.load_data(graphql_query=query, separate_documents=True)

```

# 2) example GraphQL query # query = """ # { # Get { # Author { # name # description # } # } # } # """ # docs = reader.load_data(graphql_query=query, separate_documents=True) query = """ { Get {  {  ... } } } """ documents = reader.load_data(graphql_query=query, separate_documents=True)
### Create index¶
In [ ]:
Copied!
```
index = SummaryIndex.from_documents(documents)

```

index = SummaryIndex.from_documents(documents)
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("<query_text>")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
