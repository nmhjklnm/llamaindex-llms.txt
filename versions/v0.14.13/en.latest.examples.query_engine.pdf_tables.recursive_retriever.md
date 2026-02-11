# Recursive Retriever + Query Engine Demo¶
In this demo, we walk through a use case of showcasing our "RecursiveRetriever" module over hierarchical data.
The concept of recursive retrieval is that we not only explore the directly most relevant nodes, but also explore node relationships to additional retrievers/query engines and execute them. For instance, a node may represent a concise summary of a structured table, and link to a SQL/Pandas query engine over that structured table. Then if the node is retrieved, we want to also query the underlying query engine for the answer.
This can be especially useful for documents with hierarchical relationships. In this example, we walk through a Wikipedia article about billionaires (in PDF form), which contains both text and a variety of embedded structured tables. We first create a Pandas query engine over each table, but also represent each table by an `IndexNode` (stores a link to the query engine); this Node is stored along with other Nodes in a vector store.
During query-time, if an `IndexNode` is fetched, then the underlying query engine/retriever will be queried.
**Notes about Setup**
We use `camelot` to extract text-based tables from PDFs.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-readers-file pymupdf
%pip install llama-index-llms-openai
%pip install llama-index-experimental

```

%pip install llama-index-embeddings-openai %pip install llama-index-readers-file pymupdf %pip install llama-index-llms-openai %pip install llama-index-experimental
In [ ]:
Copied!
```
import camelot

# https://en.wikipedia.org/wiki/The_World%27s_Billionaires
from llama_index.core import VectorStoreIndex
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.core.schema import IndexNode
from llama_index.llms.openai import OpenAI

from llama_index.readers.file import PyMuPDFReader
from typing import List

```

import camelot # https://en.wikipedia.org/wiki/The_World%27s_Billionaires from llama_index.core import VectorStoreIndex from llama_index.experimental.query_engine import PandasQueryEngine from llama_index.core.schema import IndexNode from llama_index.llms.openai import OpenAI from llama_index.readers.file import PyMuPDFReader from typing import List
## Default Settings¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

```

import os os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-3.5-turbo") Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
## Load in Document (and Tables)¶
We use our `PyMuPDFReader` to read in the main text of the document.
We also use `camelot` to extract some structured tables from the document
In [ ]:
Copied!
```
file_path = "billionaires_page.pdf"

```

file_path = "billionaires_page.pdf"
In [ ]:
Copied!
```
# initialize PDF reader
reader = PyMuPDFReader()

```

# initialize PDF reader reader = PyMuPDFReader()
In [ ]:
Copied!
```
docs = reader.load(file_path)

```

docs = reader.load(file_path)
In [ ]:
Copied!
```
# use camelot to parse tables
def get_tables(path: str, pages: List[int]):
    table_dfs = []
    for page in pages:
        table_list = camelot.read_pdf(path, pages=str(page))
        table_df = table_list[0].df
        table_df = (
            table_df.rename(columns=table_df.iloc[0])
            .drop(table_df.index[0])
            .reset_index(drop=True)
        )
        table_dfs.append(table_df)
    return table_dfs

```

# use camelot to parse tables def get_tables(path: str, pages: List[int]): table_dfs = [] for page in pages: table_list = camelot.read_pdf(path, pages=str(page)) table_df = table_list[0].df table_df = ( table_df.rename(columns=table_df.iloc[0]) .drop(table_df.index[0]) .reset_index(drop=True) ) table_dfs.append(table_df) return table_dfs
In [ ]:
Copied!
```
table_dfs = get_tables(file_path, pages=[3, 25])

```

table_dfs = get_tables(file_path, pages=[3, 25])
In [ ]:
Copied!
```
# shows list of top billionaires in 2023
table_dfs[0]

```

# shows list of top billionaires in 2023 table_dfs[0]
Out[ ]:
| No. | Name | Net worth\n(USD) | Age | Nationality | Primary source(s) of wealth  
---|---|---|---|---|---|---  
0 | 1 | Bernard Arnault &\nfamily | $211 billion | 74 | France | LVMH  
1 | 2 | Elon Musk | $180 billion | 51 | United\nStates | Tesla, SpaceX, X Corp.  
2 | 3 | Jeff Bezos | $114 billion | 59 | United\nStates | Amazon  
3 | 4 | Larry Ellison | $107 billion | 78 | United\nStates | Oracle Corporation  
4 | 5 | Warren Buffett | $106 billion | 92 | United\nStates | Berkshire Hathaway  
5 | 6 | Bill Gates | $104 billion | 67 | United\nStates | Microsoft  
6 | 7 | Michael Bloomberg | $94.5 billion | 81 | United\nStates | Bloomberg L.P.  
7 | 8 | Carlos Slim & family | $93 billion | 83 | Mexico | Telmex, América Móvil, Grupo\nCarso  
8 | 9 | Mukesh Ambani | $83.4 billion | 65 | India | Reliance Industries  
9 | 10 | Steve Ballmer | $80.7 billion | 67 | United\nStates | Microsoft  
In [ ]:
Copied!
```
# shows list of top billionaires
table_dfs[1]

```

# shows list of top billionaires table_dfs[1]
Out[ ]:
| Year | Number of billionaires | Group's combined net worth  
---|---|---|---  
0 | 2023[2] | 2,640 | $12.2 trillion  
1 | 2022[6] | 2,668 | $12.7 trillion  
2 | 2021[11] | 2,755 | $13.1 trillion  
3 | 2020 | 2,095 | $8.0 trillion  
4 | 2019 | 2,153 | $8.7 trillion  
5 | 2018 | 2,208 | $9.1 trillion  
6 | 2017 | 2,043 | $7.7 trillion  
7 | 2016 | 1,810 | $6.5 trillion  
8 | 2015[18] | 1,826 | $7.1 trillion  
9 | 2014[67] | 1,645 | $6.4 trillion  
10 | 2013[68] | 1,426 | $5.4 trillion  
11 | 2012 | 1,226 | $4.6 trillion  
12 | 2011 | 1,210 | $4.5 trillion  
13 | 2010 | 1,011 | $3.6 trillion  
14 | 2009 | 793 | $2.4 trillion  
15 | 2008 | 1,125 | $4.4 trillion  
16 | 2007 | 946 | $3.5 trillion  
17 | 2006 | 793 | $2.6 trillion  
18 | 2005 | 691 | $2.2 trillion  
19 | 2004 | 587 | $1.9 trillion  
20 | 2003 | 476 | $1.4 trillion  
21 | 2002 | 497 | $1.5 trillion  
22 | 2001 | 538 | $1.8 trillion  
23 | 2000 | 470 | $898 billion  
24 | Sources: Forbes.[18][67][66][68] |  |   
## Create Pandas Query Engines¶
We create a pandas query engine over each structured table.
These can be executed on their own to answer queries about each table.
**WARNING:** This tool provides the LLM access to the `eval` function. Arbitrary code execution is possible on the machine running this tool. While some level of filtering is done on code, this tool is not recommended to be used in a production setting without heavy sandboxing or virtual machines.
In [ ]:
Copied!
```
# define query engines over these tables
llm = OpenAI(model="gpt-4")

df_query_engines = [
    PandasQueryEngine(table_df, llm=llm) for table_df in table_dfs
]

```

# define query engines over these tables llm = OpenAI(model="gpt-4") df_query_engines = [ PandasQueryEngine(table_df, llm=llm) for table_df in table_dfs ]
In [ ]:
Copied!
```
response = df_query_engines[0].query(
    "What's the net worth of the second richest billionaire in 2023?"
)
print(str(response))

```

response = df_query_engines[0].query( "What's the net worth of the second richest billionaire in 2023?" ) print(str(response))
```
$180 billion

```

In [ ]:
Copied!
```
response = df_query_engines[1].query(
    "How many billionaires were there in 2009?"
)
print(str(response))

```

response = df_query_engines[1].query( "How many billionaires were there in 2009?" ) print(str(response))


## Build Vector Index¶
Build vector index over the chunked document as well as over the additional `IndexNode` objects linked to the tables.
In [ ]:
Copied!
```
from llama_index.core import Settings

doc_nodes = Settings.node_parser.get_nodes_from_documents(docs)

```

from llama_index.core import Settings doc_nodes = Settings.node_parser.get_nodes_from_documents(docs)
In [ ]:
Copied!
```
# define index nodes
summaries = [
    (
        "This node provides information about the world's richest billionaires"
        " in 2023"
    ),
    (
        "This node provides information on the number of billionaires and"
        " their combined net worth from 2000 to 2023."
    ),
]

df_nodes = [
    IndexNode(text=summary, index_id=f"pandas{idx}")
    for idx, summary in enumerate(summaries)
]

df_id_query_engine_mapping = {
    f"pandas{idx}": df_query_engine
    for idx, df_query_engine in enumerate(df_query_engines)
}

```

# define index nodes summaries = [ ( "This node provides information about the world's richest billionaires" " in 2023" ), ( "This node provides information on the number of billionaires and" " their combined net worth from 2000 to 2023." ), ] df_nodes = [ IndexNode(text=summary, index_id=f"pandas{idx}") for idx, summary in enumerate(summaries) ] df_id_query_engine_mapping = { f"pandas{idx}": df_query_engine for idx, df_query_engine in enumerate(df_query_engines) }
In [ ]:
Copied!
```
# construct top-level vector index + query engine
vector_index = VectorStoreIndex(doc_nodes + df_nodes)
vector_retriever = vector_index.as_retriever(similarity_top_k=1)

```

# construct top-level vector index + query engine vector_index = VectorStoreIndex(doc_nodes + df_nodes) vector_retriever = vector_index.as_retriever(similarity_top_k=1)
## Use `RecursiveRetriever` in our `RetrieverQueryEngine`¶
We define a `RecursiveRetriever` object to recursively retrieve/query nodes. We then put this in our `RetrieverQueryEngine` along with a `ResponseSynthesizer` to synthesize a response.
We pass in mappings from id to retriever and id to query engine. We then pass in a root id representing the retriever we query first.
In [ ]:
Copied!
```
# baseline vector index (that doesn't include the extra df nodes).
# used to benchmark
vector_index0 = VectorStoreIndex(doc_nodes)
vector_query_engine0 = vector_index0.as_query_engine()

```

# baseline vector index (that doesn't include the extra df nodes). # used to benchmark vector_index0 = VectorStoreIndex(doc_nodes) vector_query_engine0 = vector_index0.as_query_engine()
In [ ]:
Copied!
```
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import get_response_synthesizer

recursive_retriever = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever},
    query_engine_dict=df_id_query_engine_mapping,
    verbose=True,
)

response_synthesizer = get_response_synthesizer(response_mode="compact")

query_engine = RetrieverQueryEngine.from_args(
    recursive_retriever, response_synthesizer=response_synthesizer
)

```

from llama_index.core.retrievers import RecursiveRetriever from llama_index.core.query_engine import RetrieverQueryEngine from llama_index.core import get_response_synthesizer recursive_retriever = RecursiveRetriever( "vector", retriever_dict={"vector": vector_retriever}, query_engine_dict=df_id_query_engine_mapping, verbose=True, ) response_synthesizer = get_response_synthesizer(response_mode="compact") query_engine = RetrieverQueryEngine.from_args( recursive_retriever, response_synthesizer=response_synthesizer )
In [ ]:
Copied!
```
response = query_engine.query(
    "What's the net worth of the second richest billionaire in 2023?"
)

```

response = query_engine.query( "What's the net worth of the second richest billionaire in 2023?" )
```
Retrieving with query id None: What's the net worth of the second richest billionaire in 2023?
Retrieved node with id, entering: pandas0
Retrieving with query id pandas0: What's the net worth of the second richest billionaire in 2023?
Got response: $180 billion

```

In [ ]:
Copied!
```
response.source_nodes[0].node.get_content()

```

response.source_nodes[0].node.get_content()
Out[ ]:
```
"Query: What's the net worth of the second richest billionaire in 2023?\nResponse: $180\xa0billion"
```

In [ ]:
Copied!
```
str(response)

```

str(response)
Out[ ]:
```
'$180 billion.'
```

In [ ]:
Copied!
```
response = query_engine.query("How many billionaires were there in 2009?")

```

response = query_engine.query("How many billionaires were there in 2009?")
```
Retrieving with query id None: How many billionaires were there in 2009?
Retrieved node with id, entering: pandas1
Retrieving with query id pandas1: How many billionaires were there in 2009?
Got response: 793

```

In [ ]:
Copied!
```
str(response)

```

str(response)
Out[ ]:
```
'793'
```

In [ ]:
Copied!
```
response = vector_query_engine0.query(
    "How many billionaires were there in 2009?"
)

```

response = vector_query_engine0.query( "How many billionaires were there in 2009?" )
In [ ]:
Copied!
```
print(response.source_nodes[0].node.get_content())

```

print(response.source_nodes[0].node.get_content())
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Based on the context information, it is not possible to determine the exact number of billionaires in 2009. The provided information only mentions the number of billionaires in 2013 and 2014.

```

In [ ]:
Copied!
```
response.source_nodes[0].node.get_content()

```

response.source_nodes[0].node.get_content()
In [ ]:
Copied!
```
response = query_engine.query(
    "Which billionaires are excluded from this list?"
)

```

response = query_engine.query( "Which billionaires are excluded from this list?" )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Royal families and dictators whose wealth is contingent on a position are excluded from this list.

```

