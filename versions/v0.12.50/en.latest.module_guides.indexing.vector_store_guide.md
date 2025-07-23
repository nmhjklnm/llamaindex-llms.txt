# Vector Store Index usage examples¶
In this guide, we show how to use the vector store index with different vector store implementations.
From how to get started with few lines of code with the default in-memory vector store with default query configuration, to using a custom hosted vector store, with advanced settings such as metadata filters.
### Construct vector store and index¶
**Default**
By default, `VectorStoreIndex` uses a in-memory `SimpleVectorStore` that's initialized as part of the default storage context.
In [ ]:
Copied!
```
from llama_index import VectorStoreIndex, SimpleDirectoryReader

# Load documents and build index
documents = SimpleDirectoryReader(
    "../../examples/data/paul_graham"
).load_data()
index = VectorStoreIndex.from_documents(documents)

```

from llama_index import VectorStoreIndex, SimpleDirectoryReader # Load documents and build index documents = SimpleDirectoryReader( "../../examples/data/paul_graham" ).load_data() index = VectorStoreIndex.from_documents(documents)
**Custom vector stores**
You can use a custom vector store (in this case `PineconeVectorStore`) as follows:
In [ ]:
Copied!
```
import pinecone
from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext
from llama_index.vector_stores import PineconeVectorStore

# init pinecone
pinecone.init(api_key="<api_key>", environment="<environment>")
pinecone.create_index(
    "quickstart", dimension=1536, metric="euclidean", pod_type="p1"
)

# construct vector store and customize storage context
storage_context = StorageContext.from_defaults(
    vector_store=PineconeVectorStore(pinecone.Index("quickstart"))
)

# Load documents and build index
documents = SimpleDirectoryReader(
    "../../examples/data/paul_graham"
).load_data()
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

```

import pinecone from llama_index import VectorStoreIndex, SimpleDirectoryReader, StorageContext from llama_index.vector_stores import PineconeVectorStore # init pinecone pinecone.init(api_key="", environment="") pinecone.create_index( "quickstart", dimension=1536, metric="euclidean", pod_type="p1" ) # construct vector store and customize storage context storage_context = StorageContext.from_defaults( vector_store=PineconeVectorStore(pinecone.Index("quickstart")) ) # Load documents and build index documents = SimpleDirectoryReader( "../../examples/data/paul_graham" ).load_data() index = VectorStoreIndex.from_documents( documents, storage_context=storage_context )
For more examples of how to initialize different vector stores, see Vector Store Integrations.
## Connect to external vector stores (with existing embeddings)¶
If you have already computed embeddings and dumped them into an external vector store (e.g. Pinecone, Chroma), you can use it with LlamaIndex by:
In [ ]:
Copied!
```
vector_store = PineconeVectorStore(pinecone.Index("quickstart"))
index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

```

vector_store = PineconeVectorStore(pinecone.Index("quickstart")) index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
### Query¶
**Default**
You can start querying by getting the default query engine:
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")

```

query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?")
**Configure standard query setting**
To configure query settings, you can directly pass it as keyword args when building the query engine:
In [ ]:
Copied!
```
from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters

query_engine = index.as_query_engine(
    similarity_top_k=3,
    vector_store_query_mode="default",
    filters=MetadataFilters(
        filters=[
            ExactMatchFilter(key="name", value="paul graham"),
        ]
    ),
    alpha=None,
    doc_ids=None,
)
response = query_engine.query("what did the author do growing up?")

```

from llama_index.vector_stores.types import ExactMatchFilter, MetadataFilters query_engine = index.as_query_engine( similarity_top_k=3, vector_store_query_mode="default", filters=MetadataFilters( filters=[ ExactMatchFilter(key="name", value="paul graham"), ] ), alpha=None, doc_ids=None, ) response = query_engine.query("what did the author do growing up?")
Note that metadata filtering is applied against metadata specified in `Node.metadata`.
Alternatively, if you are using the lower-level compositional API:
In [ ]:
Copied!
```
from llama_index import get_response_synthesizer
from llama_index.indices.vector_store.retrievers import VectorIndexRetriever
from llama_index.query_engine.retriever_query_engine import (
    RetrieverQueryEngine,
)

# build retriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=3,
    vector_store_query_mode="default",
    filters=[ExactMatchFilter(key="name", value="paul graham")],
    alpha=None,
    doc_ids=None,
)

# build query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever, response_synthesizer=get_response_synthesizer()
)

# query
response = query_engine.query("what did the author do growing up?")

```

from llama_index import get_response_synthesizer from llama_index.indices.vector_store.retrievers import VectorIndexRetriever from llama_index.query_engine.retriever_query_engine import ( RetrieverQueryEngine, ) # build retriever retriever = VectorIndexRetriever( index=index, similarity_top_k=3, vector_store_query_mode="default", filters=[ExactMatchFilter(key="name", value="paul graham")], alpha=None, doc_ids=None, ) # build query engine query_engine = RetrieverQueryEngine( retriever=retriever, response_synthesizer=get_response_synthesizer() ) # query response = query_engine.query("what did the author do growing up?")
**Configure vector store specific keyword arguments**
You can customize keyword arguments unique to a specific vector store implementation as well by passing in `vector_store_kwargs`
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=3,
    # only works for pinecone
    vector_store_kwargs={
        "filter": {"name": "paul graham"},
    },
)
response = query_engine.query("what did the author do growing up?")

```

query_engine = index.as_query_engine( similarity_top_k=3, # only works for pinecone vector_store_kwargs={ "filter": {"name": "paul graham"}, }, ) response = query_engine.query("what did the author do growing up?")
**Use an auto retriever**
You can also use an LLM to automatically decide query setting for you! Right now, we support automatically setting exact match metadata filters and top k parameters.
In [ ]:
Copied!
```
from llama_index import get_response_synthesizer
from llama_index.indices.vector_store.retrievers import (
    VectorIndexAutoRetriever,
)
from llama_index.query_engine.retriever_query_engine import (
    RetrieverQueryEngine,
)
from llama_index.vector_stores.types import MetadataInfo, VectorStoreInfo


vector_store_info = VectorStoreInfo(
    content_info="brief biography of celebrities",
    metadata_info=[
        MetadataInfo(
            name="category",
            type="str",
            description="Category of the celebrity, one of [Sports, Entertainment, Business, Music]",
        ),
        MetadataInfo(
            name="country",
            type="str",
            description="Country of the celebrity, one of [United States, Barbados, Portugal]",
        ),
    ],
)

# build retriever
retriever = VectorIndexAutoRetriever(
    index, vector_store_info=vector_store_info
)

# build query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever, response_synthesizer=get_response_synthesizer()
)

# query
response = query_engine.query(
    "Tell me about two celebrities from United States"
)

```

from llama_index import get_response_synthesizer from llama_index.indices.vector_store.retrievers import ( VectorIndexAutoRetriever, ) from llama_index.query_engine.retriever_query_engine import ( RetrieverQueryEngine, ) from llama_index.vector_stores.types import MetadataInfo, VectorStoreInfo vector_store_info = VectorStoreInfo( content_info="brief biography of celebrities", metadata_info=[ MetadataInfo( name="category", type="str", description="Category of the celebrity, one of [Sports, Entertainment, Business, Music]", ), MetadataInfo( name="country", type="str", description="Country of the celebrity, one of [United States, Barbados, Portugal]", ), ], ) # build retriever retriever = VectorIndexAutoRetriever( index, vector_store_info=vector_store_info ) # build query engine query_engine = RetrieverQueryEngine( retriever=retriever, response_synthesizer=get_response_synthesizer() ) # query response = query_engine.query( "Tell me about two celebrities from United States" )
