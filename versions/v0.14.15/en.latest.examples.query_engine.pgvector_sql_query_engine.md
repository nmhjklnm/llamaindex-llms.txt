![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# [Beta] Text-to-SQL with PGVector¶
This notebook demo shows how to perform text-to-SQL with pgvector. This allows us to jointly do both semantic search and structured querying, _all_ within SQL!
This hypothetically enables more expressive queries than semantic search + metadata filters.
**NOTE** : This is a beta feature, interfaces might change. But in the meantime hope you find it useful!
**NOTE:** Any Text-to-SQL application should be aware that executing arbitrary SQL queries can be a security risk. It is recommended to take precautions as needed, such as using restricted roles, read-only databases, sandboxing, etc.
## Setup Data¶
### Load Documents¶
Load in the Lyft 2021 10k document.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-huggingface
%pip install llama-index-readers-file
%pip install llama-index-llms-openai

```

%pip install llama-index-embeddings-huggingface %pip install llama-index-readers-file %pip install llama-index-llms-openai
In [ ]:
Copied!
```
from llama_index.readers.file import PDFReader

```

from llama_index.readers.file import PDFReader
In [ ]:
Copied!
```
reader = PDFReader()

```

reader = PDFReader()
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/10k/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'

```

!mkdir -p 'data/10k/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10k/lyft_2021.pdf' -O 'data/10k/lyft_2021.pdf'
In [ ]:
Copied!
```
docs = reader.load_data("./data/10k/lyft_2021.pdf")

```

docs = reader.load_data("./data/10k/lyft_2021.pdf")
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

node_parser = SentenceSplitter()
nodes = node_parser.get_nodes_from_documents(docs)

```

from llama_index.core.node_parser import SentenceSplitter node_parser = SentenceSplitter() nodes = node_parser.get_nodes_from_documents(docs)
In [ ]:
Copied!
```
print(nodes[8].get_content(metadata_mode="all"))

```

print(nodes[8].get_content(metadata_mode="all"))
### Insert data into Postgres + PGVector¶
Make sure you have all the necessary dependencies installed!
In [ ]:
Copied!
```
!pip install psycopg2-binary pgvector asyncpg "sqlalchemy[asyncio]" greenlet

```

!pip install psycopg2-binary pgvector asyncpg "sqlalchemy[asyncio]" greenlet
In [ ]:
Copied!
```
from pgvector.sqlalchemy import Vector
from sqlalchemy import insert, create_engine, String, text, Integer
from sqlalchemy.orm import declarative_base, mapped_column

```

from pgvector.sqlalchemy import Vector from sqlalchemy import insert, create_engine, String, text, Integer from sqlalchemy.orm import declarative_base, mapped_column
#### Establish Connection¶
In [ ]:
Copied!
```
engine = create_engine("postgresql+psycopg2://localhost/postgres")
with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

```

engine = create_engine("postgresql+psycopg2://localhost/postgres") with engine.connect() as conn: conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector")) conn.commit()
#### Define Table Schema¶
Define as Python class. Note we store the page_label, embedding, and text.
In [ ]:
Copied!
```
Base = declarative_base()


class SECTextChunk(Base):
    __tablename__ = "sec_text_chunk"

    id = mapped_column(Integer, primary_key=True)
    page_label = mapped_column(Integer)
    file_name = mapped_column(String)
    text = mapped_column(String)
    embedding = mapped_column(Vector(384))

```

Base = declarative_base() class SECTextChunk(Base): __tablename__ = "sec_text_chunk" id = mapped_column(Integer, primary_key=True) page_label = mapped_column(Integer) file_name = mapped_column(String) text = mapped_column(String) embedding = mapped_column(Vector(384))
In [ ]:
Copied!
```
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

```

Base.metadata.drop_all(engine) Base.metadata.create_all(engine)
#### Generate embedding for each Node with a sentence_transformers model¶
In [ ]:
Copied!
```
# get embeddings for each row
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en")

for node in nodes:
    text_embedding = embed_model.get_text_embedding(node.get_content())
    node.embedding = text_embedding

```

# get embeddings for each row from llama_index.embeddings.huggingface import HuggingFaceEmbedding embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en") for node in nodes: text_embedding = embed_model.get_text_embedding(node.get_content()) node.embedding = text_embedding
#### Insert into Database¶
In [ ]:
Copied!
```
# insert into database
for node in nodes:
    row_dict = {
        "text": node.get_content(),
        "embedding": node.embedding,
        **node.metadata,
    }
    stmt = insert(SECTextChunk).values(**row_dict)
    with engine.connect() as connection:
        cursor = connection.execute(stmt)
        connection.commit()

```

# insert into database for node in nodes: row_dict = { "text": node.get_content(), "embedding": node.embedding, **node.metadata, } stmt = insert(SECTextChunk).values(**row_dict) with engine.connect() as connection: cursor = connection.execute(stmt) connection.commit()
## Define PGVectorSQLQueryEngine¶
Now that we've loaded the data into the database, we're ready to setup our query engine.
### Define Prompt¶
We create a modified version of our default text-to-SQL prompt to inject awareness of the pgvector syntax. We also prompt it with some few-shot examples of how to use the syntax (<-->).
**NOTE** : This is included by default in the `PGVectorSQLQueryEngine`, we included it here mostly for visibility!
In [ ]:
Copied!
```
from llama_index.core import PromptTemplate

text_to_sql_tmpl = """\
Given an input question, first create a syntactically correct {dialect} \
query to run, then look at the results of the query and return the answer. \
You can order the results by a relevant column to return the most \
interesting examples in the database.

Pay attention to use only the column names that you can see in the schema \
description. Be careful to not query for columns that do not exist. \
Pay attention to which column is in which table. Also, qualify column names \
with the table name when needed. 

IMPORTANT NOTE: you can use specialized pgvector syntax (`<->`) to do nearest \
neighbors/semantic search to a given vector from an embeddings column in the table. \
The embeddings value for a given row typically represents the semantic meaning of that row. \
The vector represents an embedding representation \
of the question, given below. Do NOT fill in the vector values directly, but rather specify a \
`[query_vector]` placeholder. For instance, some select statement examples below \
(the name of the embeddings column is `embedding`):
SELECT * FROM items ORDER BY embedding <-> '[query_vector]' LIMIT 5;
SELECT * FROM items WHERE id != 1 ORDER BY embedding <-> (SELECT embedding FROM items WHERE id = 1) LIMIT 5;
SELECT * FROM items WHERE embedding <-> '[query_vector]' < 5;

You are required to use the following format, \
each taking one line:

Question: Question here
SQLQuery: SQL Query to run
SQLResult: Result of the SQLQuery
Answer: Final answer here

Only use tables listed below.
{schema}


Question: {query_str}
SQLQuery: \
"""
text_to_sql_prompt = PromptTemplate(text_to_sql_tmpl)

```

from llama_index.core import PromptTemplate text_to_sql_tmpl = """\ Given an input question, first create a syntactically correct {dialect} \ query to run, then look at the results of the query and return the answer. \ You can order the results by a relevant column to return the most \ interesting examples in the database. Pay attention to use only the column names that you can see in the schema \ description. Be careful to not query for columns that do not exist. \ Pay attention to which column is in which table. Also, qualify column names \ with the table name when needed. IMPORTANT NOTE: you can use specialized pgvector syntax (`<->`) to do nearest \ neighbors/semantic search to a given vector from an embeddings column in the table. \ The embeddings value for a given row typically represents the semantic meaning of that row. \ The vector represents an embedding representation \ of the question, given below. Do NOT fill in the vector values directly, but rather specify a \ `[query_vector]` placeholder. For instance, some select statement examples below \ (the name of the embeddings column is `embedding`): SELECT * FROM items ORDER BY embedding <-> '[query_vector]' LIMIT 5; SELECT * FROM items WHERE id != 1 ORDER BY embedding <-> (SELECT embedding FROM items WHERE id = 1) LIMIT 5; SELECT * FROM items WHERE embedding <-> '[query_vector]' < 5; You are required to use the following format, \ each taking one line: Question: Question here SQLQuery: SQL Query to run SQLResult: Result of the SQLQuery Answer: Final answer here Only use tables listed below. {schema} Question: {query_str} SQLQuery: \ """ text_to_sql_prompt = PromptTemplate(text_to_sql_tmpl)
### Setup LLM, Embedding Model, and Misc.¶
Besides LLM and embedding model, note we also add annotations on the table itself. This better helps the LLM understand the column schema (e.g. by telling it what the embedding column represents) to better do either tabular querying or semantic search.
In [ ]:
Copied!
```
from llama_index.core import SQLDatabase
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import PGVectorSQLQueryEngine
from llama_index.core import Settings


sql_database = SQLDatabase(engine, include_tables=["sec_text_chunk"])

Settings.llm = OpenAI(model="gpt-4")
Settings.embed_model = embed_model


table_desc = """\
This table represents text chunks from an SEC filing. Each row contains the following columns:

id: id of row
page_label: page number 
file_name: top-level file name
text: all text chunk is here
embedding: the embeddings representing the text chunk

For most queries you should perform semantic search against the `embedding` column values, since \
that encodes the meaning of the text.

"""

context_query_kwargs = {"sec_text_chunk": table_desc}

```

from llama_index.core import SQLDatabase from llama_index.llms.openai import OpenAI from llama_index.core.query_engine import PGVectorSQLQueryEngine from llama_index.core import Settings sql_database = SQLDatabase(engine, include_tables=["sec_text_chunk"]) Settings.llm = OpenAI(model="gpt-4") Settings.embed_model = embed_model table_desc = """\ This table represents text chunks from an SEC filing. Each row contains the following columns: id: id of row page_label: page number file_name: top-level file name text: all text chunk is here embedding: the embeddings representing the text chunk For most queries you should perform semantic search against the `embedding` column values, since \ that encodes the meaning of the text. """ context_query_kwargs = {"sec_text_chunk": table_desc}
### Define Query Engine¶
In [ ]:
Copied!
```
query_engine = PGVectorSQLQueryEngine(
    sql_database=sql_database,
    text_to_sql_prompt=text_to_sql_prompt,
    context_query_kwargs=context_query_kwargs,
)

```

query_engine = PGVectorSQLQueryEngine( sql_database=sql_database, text_to_sql_prompt=text_to_sql_prompt, context_query_kwargs=context_query_kwargs, )
## Run Some Queries¶
Now we're ready to run some queries
In [ ]:
Copied!
```
response = query_engine.query(
    "Can you tell me about the risk factors described in page 6?",
)

```

response = query_engine.query( "Can you tell me about the risk factors described in page 6?", )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Page 6 discusses the impact of the COVID-19 pandemic on the business. It mentions that the pandemic has affected communities in the United States, Canada, and globally. The pandemic has led to a significant decrease in the demand for ridesharing services, which has negatively impacted the company's financial performance. The page also discusses the company's efforts to adapt to the changing environment by focusing on the delivery of essential goods and services. Additionally, it mentions the company's transportation network, which offers riders seamless, personalized, and on-demand access to a variety of mobility options.

```

In [ ]:
Copied!
```
print(response.metadata["sql_query"])

```

print(response.metadata["sql_query"])
In [ ]:
Copied!
```
response = query_engine.query(
    "Tell me more about Lyft's real estate operating leases",
)

```

response = query_engine.query( "Tell me more about Lyft's real estate operating leases", )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Lyft's lease arrangements include vehicle rental programs, office space, and data centers. Leases that do not meet any specific criteria are accounted for as operating leases. The lease term begins when Lyft is available to use the underlying asset and ends upon the termination of the lease. The lease term includes any periods covered by an option to extend if Lyft is reasonably certain to exercise that option. Leasehold improvements are amortized on a straight-line basis over the shorter of the term of the lease, or the useful life of the assets.

```

In [ ]:
Copied!
```
print(response.metadata["sql_query"][:300])

```

print(response.metadata["sql_query"][:300])
```
SELECT * FROM sec_text_chunk WHERE text LIKE '%Lyft%' AND text LIKE '%real estate%' AND text LIKE '%operating leases%' ORDER BY embedding <-> '[-0.007079003844410181, -0.04383348673582077, 0.02910166047513485, 0.02049737051129341, 0.009460929781198502, -0.017539210617542267, 0.04225028306245804, 0.0

```

In [ ]:
Copied!
```
# looked at returned result
print(response.metadata["result"])

```

# looked at returned result print(response.metadata["result"])
```
[(157, 93, 'lyft_2021.pdf', "Leases that do not meet any of the above criteria are accounted for as operating leases.Lessor\nThe\n Company's lease arrangements include vehicle re ... (4356 characters truncated) ...  realized. Leasehold improvements are amortized on a straight-line basis over the shorter of the term of the lease, or the useful life of the assets.", '[0.017818017,-0.024016099,0.0042511695,0.03114478,0.003591422,-0.0097886855,0.02455732,0.013048866,0.018157514,-0.009401044,0.031699456,0.01678178,0. ... (4472 characters truncated) ... 6,0.01127416,0.045080125,-0.017046565,-0.028544193,-0.016320521,0.01062995,-0.021007432,-0.006999497,-0.08426073,-0.014918887,0.059064835,0.03307945]')]

```

In [ ]:
Copied!
```
# structured query
response = query_engine.query(
    "Tell me about the max page number in this table",
)

```

# structured query response = query_engine.query( "Tell me about the max page number in this table", )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The maximum page number in this table is 238.

```

In [ ]:
Copied!
```
print(response.metadata["sql_query"][:300])

```

print(response.metadata["sql_query"][:300])
```
SELECT MAX(page_label) FROM sec_text_chunk;

```

