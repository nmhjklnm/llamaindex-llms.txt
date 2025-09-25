![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
![View Article](https://img.shields.io/badge/View%20Article-blue)
# Optimizing for relevance using MongoDB and LlamaIndex¶
In this notebook, we will explore and tune different retrieval options in MongoDB's LlamaIndex integration to get the most relevant results.
## Step 1: Install libraries¶
  * **pymongo** : Python package to interact with MongoDB databases and collections
  * **llama-index** : Python package for the LlamaIndex LLM framework
  * **llama-index-llms-openai** : Python package to use OpenAI models via their LlamaIndex integration
  * **llama-index-vector-stores-mongodb** : Python package for MongoDB’s LlamaIndex integration


In [ ]:
Copied!
```
!pip install -qU pymongo llama-index llama-index-llms-openai llama-index-vector-stores-mongodb

```

!pip install -qU pymongo llama-index llama-index-llms-openai llama-index-vector-stores-mongodb
```
[notice] A new release of pip is available: 23.2.1 -> 24.2
[notice] To update, run: pip install --upgrade pip

```

## Step 2: Setup prerequisites¶
  * **Set the MongoDB connection string** : Follow the steps here to get the connection string from the Atlas UI.
  * **Set the OpenAI API key** : Steps to obtain an API key as here


In [ ]:
Copied!
```
import os
import getpass
from pymongo import MongoClient

```

import os import getpass from pymongo import MongoClient
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")

```

os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter your OpenAI API key: ")
In [ ]:
Copied!
```
MONGODB_URI = getpass.getpass("Enter your MongoDB URI: ")
mongodb_client = MongoClient(
    MONGODB_URI, appname="devrel.content.retrieval_strategies_llamaindex"
)

```

MONGODB_URI = getpass.getpass("Enter your MongoDB URI: ") mongodb_client = MongoClient( MONGODB_URI, appname="devrel.content.retrieval_strategies_llamaindex" )
## Step 3: Load and process the dataset¶
In [ ]:
Copied!
```
from datasets import load_dataset
import pandas as pd
from llama_index.core import Document

```

from datasets import load_dataset import pandas as pd from llama_index.core import Document
In [ ]:
Copied!
```
data = load_dataset("MongoDB/embedded_movies", split="train")
data = pd.DataFrame(data)

```

data = load_dataset("MongoDB/embedded_movies", split="train") data = pd.DataFrame(data)
In [ ]:
Copied!
```
data.head()

```

data.head()
Out[ ]:
| plot | runtime | genres | fullplot | directors | writers | countries | poster | languages | cast | title | num_mflix_comments | rated | imdb | awards | type | metacritic | plot_embedding  
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---  
0 | Young Pauline is left a lot of money when her ... | 199.0 | [Action] | Young Pauline is left a lot of money when her ... | [Louis J. Gasnier, Donald MacKenzie] | [Charles W. Goddard (screenplay), Basil Dickey... | [USA] | https://m.media-amazon.com/images/M/MV5BMzgxOD... | [English] | [Pearl White, Crane Wilbur, Paul Panzer, Edwar... | The Perils of Pauline | 0 | None | {'id': 4465, 'rating': 7.6, 'votes': 744} | {'nominations': 0, 'text': '1 win.', 'wins': 1} | movie | NaN | [0.0007293965299999999, -0.026834568000000003,...  
1 | A penniless young man tries to save an heiress... | 22.0 | [Comedy, Short, Action] | As a penniless man worries about how he will m... | [Alfred J. Goulding, Hal Roach] | [H.M. Walker (titles)] | [USA] | https://m.media-amazon.com/images/M/MV5BNzE1OW... | [English] | [Harold Lloyd, Mildred Davis, 'Snub' Pollard, ... | From Hand to Mouth | 0 | TV-G | {'id': 10146, 'rating': 7.0, 'votes': 639} | {'nominations': 1, 'text': '1 nomination.', 'w... | movie | NaN | [-0.022837115, -0.022941574000000003, 0.014937...  
2 | Michael "Beau" Geste leaves England in disgrac... | 101.0 | [Action, Adventure, Drama] | Michael "Beau" Geste leaves England in disgrac... | [Herbert Brenon] | [Herbert Brenon (adaptation), John Russell (ad... | [USA] | None | [English] | [Ronald Colman, Neil Hamilton, Ralph Forbes, A... | Beau Geste | 0 | None | {'id': 16634, 'rating': 6.9, 'votes': 222} | {'nominations': 0, 'text': '1 win.', 'wins': 1} | movie | NaN | [0.00023330492999999998, -0.028511643000000003...  
3 | Seeking revenge, an athletic young man joins t... | 88.0 | [Adventure, Action] | A nobleman vows to avenge the death of his fat... | [Albert Parker] | [Douglas Fairbanks (story), Jack Cunningham (a... | [USA] | https://m.media-amazon.com/images/M/MV5BMzU0ND... | None | [Billie Dove, Tempe Pigott, Donald Crisp, Sam ... | The Black Pirate | 1 | None | {'id': 16654, 'rating': 7.2, 'votes': 1146} | {'nominations': 0, 'text': '1 win.', 'wins': 1} | movie | NaN | [-0.005927917, -0.033394486, 0.0015323418, -0....  
4 | An irresponsible young millionaire changes his... | 58.0 | [Action, Comedy, Romance] | The Uptown Boy, J. Harold Manners (Lloyd) is a... | [Sam Taylor] | [Ted Wilde (story), John Grey (story), Clyde B... | [USA] | https://m.media-amazon.com/images/M/MV5BMTcxMT... | [English] | [Harold Lloyd, Jobyna Ralston, Noah Young, Jim... | For Heaven's Sake | 0 | PASSED | {'id': 16895, 'rating': 7.6, 'votes': 918} | {'nominations': 1, 'text': '1 nomination.', 'w... | movie | NaN | [-0.0059373598, -0.026604708, -0.0070914757000...  
In [ ]:
Copied!
```
# Fill Nones in the dataframe
data = data.fillna(
    {"genres": "[]", "languages": "[]", "cast": "[]", "imdb": "{}"}
)

```

# Fill Nones in the dataframe data = data.fillna( {"genres": "[]", "languages": "[]", "cast": "[]", "imdb": "{}"} )
In [ ]:
Copied!
```
documents = []

for _, row in data.iterrows():
    # Extract required fields
    title = row["title"]
    rating = row["imdb"].get("rating", 0)
    languages = row["languages"]
    cast = row["cast"]
    genres = row["genres"]
    # Create the metadata attribute
    metadata = {"title": title, "rating": rating, "languages": languages}
    # Create the text attribute
    text = f"Title: {title}\nPlot: {row['fullplot']}\nCast: {', '.join(item for item in cast)}\nGenres: {', '.join(item for item in  genres)}\nLanguages: {', '.join(item for item in languages)}\nRating: {rating}"
    documents.append(Document(text=text, metadata=metadata))

```

documents = [] for _, row in data.iterrows(): # Extract required fields title = row["title"] rating = row["imdb"].get("rating", 0) languages = row["languages"] cast = row["cast"] genres = row["genres"] # Create the metadata attribute metadata = {"title": title, "rating": rating, "languages": languages} # Create the text attribute text = f"Title: {title}\nPlot: {row['fullplot']}\nCast: {', '.join(item for item in cast)}\nGenres: {', '.join(item for item in genres)}\nLanguages: {', '.join(item for item in languages)}\nRating: {rating}" documents.append(Document(text=text, metadata=metadata))
In [ ]:
Copied!
```
print(documents[0].text)

```

print(documents[0].text)
```
Title: The Perils of Pauline
Plot: Young Pauline is left a lot of money when her wealthy uncle dies. However, her uncle's secretary has been named as her guardian until she marries, at which time she will officially take possession of her inheritance. Meanwhile, her "guardian" and his confederates constantly come up with schemes to get rid of Pauline so that he can get his hands on the money himself.
Cast: Pearl White, Crane Wilbur, Paul Panzer, Edward Josè
Genres: Action
Languages: English
Rating: 7.6

```

In [ ]:
Copied!
```
print(documents[0].metadata)

```

print(documents[0].metadata)
```
{'title': 'The Perils of Pauline', 'rating': 7.6, 'languages': ['English']}

```

## Step 4: Create MongoDB Atlas vector store¶
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core.settings import Settings
from llama_index.core import VectorStoreIndex, StorageContext
from pymongo.operations import SearchIndexModel
from pymongo.errors import OperationFailure

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch from llama_index.core.settings import Settings from llama_index.core import VectorStoreIndex, StorageContext from pymongo.operations import SearchIndexModel from pymongo.errors import OperationFailure
In [ ]:
Copied!
```
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

```

Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
In [ ]:
Copied!
```
VS_INDEX_NAME = "vector_index"
FTS_INDEX_NAME = "fts_index"
DB_NAME = "llamaindex"
COLLECTION_NAME = "hybrid_search"
collection = mongodb_client[DB_NAME][COLLECTION_NAME]

```

VS_INDEX_NAME = "vector_index" FTS_INDEX_NAME = "fts_index" DB_NAME = "llamaindex" COLLECTION_NAME = "hybrid_search" collection = mongodb_client[DB_NAME][COLLECTION_NAME]
In [ ]:
Copied!
```
vector_store = MongoDBAtlasVectorSearch(
    mongodb_client,
    db_name=DB_NAME,
    collection_name=COLLECTION_NAME,
    vector_index_name=VS_INDEX_NAME,
    fulltext_index_name=FTS_INDEX_NAME,
    embedding_key="embedding",
    text_key="text",
)
# If the collection has documents with embeddings already, create the vector store index from the vector store
if collection.count_documents({}) > 0:
    vector_store_index = VectorStoreIndex.from_vector_store(vector_store)
# If the collection does not have documents, embed and ingest them into the vector store
else:
    vector_store_context = StorageContext.from_defaults(
        vector_store=vector_store
    )
    vector_store_index = VectorStoreIndex.from_documents(
        documents, storage_context=vector_store_context, show_progress=True
    )

```

vector_store = MongoDBAtlasVectorSearch( mongodb_client, db_name=DB_NAME, collection_name=COLLECTION_NAME, vector_index_name=VS_INDEX_NAME, fulltext_index_name=FTS_INDEX_NAME, embedding_key="embedding", text_key="text", ) # If the collection has documents with embeddings already, create the vector store index from the vector store if collection.count_documents({}) > 0: vector_store_index = VectorStoreIndex.from_vector_store(vector_store) # If the collection does not have documents, embed and ingest them into the vector store else: vector_store_context = StorageContext.from_defaults( vector_store=vector_store ) vector_store_index = VectorStoreIndex.from_documents( documents, storage_context=vector_store_context, show_progress=True )
## Step 5: Create Atlas Search indexes¶
In [ ]:
Copied!
```
vs_model = SearchIndexModel(
    definition={
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "numDimensions": 1536,
                "similarity": "cosine",
            },
            {"type": "filter", "path": "metadata.rating"},
            {"type": "filter", "path": "metadata.language"},
        ]
    },
    name=VS_INDEX_NAME,
    type="vectorSearch",
)

```

vs_model = SearchIndexModel( definition={ "fields": [ { "type": "vector", "path": "embedding", "numDimensions": 1536, "similarity": "cosine", }, {"type": "filter", "path": "metadata.rating"}, {"type": "filter", "path": "metadata.language"}, ] }, name=VS_INDEX_NAME, type="vectorSearch", )
In [ ]:
Copied!
```
fts_model = SearchIndexModel(
    definition={
        "mappings": {"dynamic": False, "fields": {"text": {"type": "string"}}}
    },
    name=FTS_INDEX_NAME,
    type="search",
)

```

fts_model = SearchIndexModel( definition={ "mappings": {"dynamic": False, "fields": {"text": {"type": "string"}}} }, name=FTS_INDEX_NAME, type="search", )
In [ ]:
Copied!
```
for model in [vs_model, fts_model]:
    try:
        collection.create_search_index(model=model)
    except OperationFailure:
        print(
            f"Duplicate index found for model {model}. Skipping index creation."
        )

```

for model in [vs_model, fts_model]: try: collection.create_search_index(model=model) except OperationFailure: print( f"Duplicate index found for model {model}. Skipping index creation." )
```
Duplicate index found for model <pymongo.operations.SearchIndexModel object at 0x31d4c33d0>. Skipping index creation.
Duplicate index found for model <pymongo.operations.SearchIndexModel object at 0x31d4c1c60>. Skipping index creation.

```

## Step 6: Get movie recommendations¶
In [ ]:
Copied!
```
def get_recommendations(query: str, mode: str, **kwargs) -> None:
    """
    Get movie recommendations

    Args:
        query (str): User query
        mode (str): Retrieval mode. One of (default, text_search, hybrid)
    """
    query_engine = vector_store_index.as_query_engine(
        similarity_top_k=5, vector_store_query_mode=mode, **kwargs
    )
    response = query_engine.query(query)
    nodes = response.source_nodes
    for node in nodes:
        title = node.metadata["title"]
        rating = node.metadata["rating"]
        score = node.score
        print(f"Title: {title} | Rating: {rating} | Relevance Score: {score}")

```

def get_recommendations(query: str, mode: str, **kwargs) -> None: """ Get movie recommendations Args: query (str): User query mode (str): Retrieval mode. One of (default, text_search, hybrid) """ query_engine = vector_store_index.as_query_engine( similarity_top_k=5, vector_store_query_mode=mode, **kwargs ) response = query_engine.query(query) nodes = response.source_nodes for node in nodes: title = node.metadata["title"] rating = node.metadata["rating"] score = node.score print(f"Title: {title} | Rating: {rating} | Relevance Score: {score}")
### Full-text search¶
In [ ]:
Copied!
```
get_recommendations(
    query="Action movies about humans fighting machines",
    mode="text_search",
)

```

get_recommendations( query="Action movies about humans fighting machines", mode="text_search", )
```
Title: Hellboy II: The Golden Army | Rating: 7.0 | Relevance Score: 5.93734884262085
Title: The Matrix Revolutions | Rating: 6.7 | Relevance Score: 4.574477195739746
Title: The Matrix | Rating: 8.7 | Relevance Score: 4.387373924255371
Title: Go with Peace Jamil | Rating: 6.9 | Relevance Score: 3.5394840240478516
Title: Terminator Salvation | Rating: 6.7 | Relevance Score: 3.3378987312316895

```

### Vector search¶
In [ ]:
Copied!
```
get_recommendations(
    query="Action movies about humans fighting machines", mode="default"
)

```

get_recommendations( query="Action movies about humans fighting machines", mode="default" )
```
Title: Death Machine | Rating: 5.7 | Relevance Score: 0.7407287359237671
Title: Real Steel | Rating: 7.1 | Relevance Score: 0.7364246845245361
Title: Soldier | Rating: 5.9 | Relevance Score: 0.7282171249389648
Title: Terminator 3: Rise of the Machines | Rating: 6.4 | Relevance Score: 0.7266112565994263
Title: Last Action Hero | Rating: 6.2 | Relevance Score: 0.7250100374221802

```

### Hybrid search¶
In [ ]:
Copied!
```
# Vector and full-text search weighted equal by default
get_recommendations(
    query="Action movies about humans fighting machines", mode="hybrid"
)

```

# Vector and full-text search weighted equal by default get_recommendations( query="Action movies about humans fighting machines", mode="hybrid" )
```
Title: Hellboy II: The Golden Army | Rating: 7.0 | Relevance Score: 0.5
Title: Death Machine | Rating: 5.7 | Relevance Score: 0.5
Title: The Matrix Revolutions | Rating: 6.7 | Relevance Score: 0.25
Title: Real Steel | Rating: 7.1 | Relevance Score: 0.25
Title: Soldier | Rating: 5.9 | Relevance Score: 0.16666666666666666

```

In [ ]:
Copied!
```
# Higher alpha, vector search dominates
get_recommendations(
    query="Action movies about humans fighting machines",
    mode="hybrid",
    alpha=0.7,
)

```

# Higher alpha, vector search dominates get_recommendations( query="Action movies about humans fighting machines", mode="hybrid", alpha=0.7, )
```
Title: Death Machine | Rating: 5.7 | Relevance Score: 0.7
Title: Real Steel | Rating: 7.1 | Relevance Score: 0.35
Title: Hellboy II: The Golden Army | Rating: 7.0 | Relevance Score: 0.30000000000000004
Title: Soldier | Rating: 5.9 | Relevance Score: 0.2333333333333333
Title: Terminator 3: Rise of the Machines | Rating: 6.4 | Relevance Score: 0.175

```

In [ ]:
Copied!
```
# Lower alpha, full-text search dominates
get_recommendations(
    query="Action movies about humans fighting machines",
    mode="hybrid",
    alpha=0.3,
)

```

# Lower alpha, full-text search dominates get_recommendations( query="Action movies about humans fighting machines", mode="hybrid", alpha=0.3, )
```
Title: Hellboy II: The Golden Army | Rating: 7.0 | Relevance Score: 0.7
Title: The Matrix Revolutions | Rating: 6.7 | Relevance Score: 0.35
Title: Death Machine | Rating: 5.7 | Relevance Score: 0.3
Title: The Matrix | Rating: 8.7 | Relevance Score: 0.2333333333333333
Title: Go with Peace Jamil | Rating: 6.9 | Relevance Score: 0.175

```

### Combining metadata filters with search¶
In [ ]:
Copied!
```
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
    FilterCondition,
)

```

from llama_index.core.vector_stores import ( MetadataFilter, MetadataFilters, FilterOperator, FilterCondition, )
In [ ]:
Copied!
```
filters = MetadataFilters(
    filters=[
        MetadataFilter(
            key="metadata.rating", value=7, operator=FilterOperator.GT
        ),
        MetadataFilter(
            key="metadata.languages",
            value="English",
            operator=FilterOperator.EQ,
        ),
    ],
    condition=FilterCondition.AND,
)

```

filters = MetadataFilters( filters=[ MetadataFilter( key="metadata.rating", value=7, operator=FilterOperator.GT ), MetadataFilter( key="metadata.languages", value="English", operator=FilterOperator.EQ, ), ], condition=FilterCondition.AND, )
In [ ]:
Copied!
```
get_recommendations(
    query="Action movies about humans fighting machines",
    mode="hybrid",
    alpha=0.7,
    filters=filters,
)

```

get_recommendations( query="Action movies about humans fighting machines", mode="hybrid", alpha=0.7, filters=filters, )
```
Title: Real Steel | Rating: 7.1 | Relevance Score: 0.7
Title: T2 3-D: Battle Across Time | Rating: 7.8 | Relevance Score: 0.35
Title: The Matrix | Rating: 8.7 | Relevance Score: 0.30000000000000004
Title: Predator | Rating: 7.8 | Relevance Score: 0.2333333333333333
Title: Transformers | Rating: 7.1 | Relevance Score: 0.175

```

