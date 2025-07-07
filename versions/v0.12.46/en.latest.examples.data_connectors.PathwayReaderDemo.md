![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Pathway Reader¶
> Pathway is an open data processing framework. It allows you to easily develop data transformation pipelines and Machine Learning applications that work with live data sources and changing data.
This notebook demonstrates how to set up a live data indexing pipeline. You can query the results of this pipeline from your LLM application in the same manner as you would a regular reader. However, under the hood, Pathway updates the index on each data change giving you always up-to-date answers.
In this notebook, we will first connect the `llama_index.readers.pathway.PathwayReader` reader to a public demo document processing pipeline that:
  1. Monitors several cloud data sources for data changes.
  2. Builds a vector index for the data.


To have your own document processing pipeline check the hosted offering or build your own by following this notebook.
The basic pipeline described in this document allows to effortlessly build a simple index of files stored in a cloud location. However, Pathway provides everything needed to build realtime data pipelines and apps, including SQL-like able operations such as groupby-reductions and joins between disparate data sources, time-based grouping and windowing of data, and a wide array of connectors.
For more details about Pathway data ingestion pipeline and vector store, visit vector store pipeline.
## Prerequisites¶
Install the `llama-index-readers-pathway` integration
In [ ]:
Copied!
```
%pip install llama-index-readers-pathway

```

%pip install llama-index-readers-pathway
Configure logging
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.ERROR)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.ERROR) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
Set up your OpenAI API key.
In [ ]:
Copied!
```
import getpass
import os

# omit if embedder of choice is not OpenAI
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")

```

import getpass import os # omit if embedder of choice is not OpenAI if "OPENAI_API_KEY" not in os.environ: os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")
## Create the reader and connect to a public pipeline¶
To instantiate and configure `PathwayReader` you need to provide either the `url` or the `host` and `port` of your document indexing pipeline. In the code below we use a publicly available demo pipeline, which REST API you can access at `https://demo-document-indexing.pathway.stream`. This demo ingests documents from Google Drive and Sharepoint and maintains an index for retrieving documents.
In [ ]:
Copied!
```
from llama_index.readers.pathway import PathwayReader

reader = PathwayReader(url="https://demo-document-indexing.pathway.stream")
# let us search with some text
reader.load_data(query_text="What is Pathway")

```

from llama_index.readers.pathway import PathwayReader reader = PathwayReader(url="https://demo-document-indexing.pathway.stream") # let us search with some text reader.load_data(query_text="What is Pathway")
## Create a summary index with llama-index¶
In [ ]:
Copied!
```
docs = reader.load_data(query_text="What is Pathway", k=2)
from llama_index.core import SummaryIndex

index = SummaryIndex.from_documents(docs)
query_engine = index.as_query_engine()
response = query_engine.query("What does Pathway do?")
print(response)

```

docs = reader.load_data(query_text="What is Pathway", k=2) from llama_index.core import SummaryIndex index = SummaryIndex.from_documents(docs) query_engine = index.as_query_engine() response = query_engine.query("What does Pathway do?") print(response)
## Building your own data processing pipeline¶
### Prerequisites¶
Install `pathway` package. Then download sample data.
In [ ]:
Copied!
```
%pip install pathway
%pip install llama-index-embeddings-openai

```

%pip install pathway %pip install llama-index-embeddings-openai
In [ ]:
Copied!
```
!mkdir -p 'data/'
!wget 'https://gist.githubusercontent.com/janchorowski/dd22a293f3d99d1b726eedc7d46d2fc0/raw/pathway_readme.md' -O 'data/pathway_readme.md'

```

!mkdir -p 'data/' !wget 'https://gist.githubusercontent.com/janchorowski/dd22a293f3d99d1b726eedc7d46d2fc0/raw/pathway_readme.md' -O 'data/pathway_readme.md'
### Define data sources tracked by Pathway¶
Pathway can listen to many sources simultaneously, such as local files, S3 folders, cloud storage and any data stream for data changes.
See pathway-io for more information.
In [ ]:
Copied!
```
import pathway as pw

data_sources = []
data_sources.append(
    pw.io.fs.read(
        "./data",
        format="binary",
        mode="streaming",
        with_metadata=True,
    )  # This creates a `pathway` connector that tracks
    # all the files in the ./data directory
)

# This creates a connector that tracks files in Google drive.
# please follow the instructions at https://pathway.com/developers/tutorials/connectors/gdrive-connector/ to get credentials
# data_sources.append(
#     pw.io.gdrive.read(object_id="17H4YpBOAKQzEJ93xmC2z170l0bP2npMy", service_user_credentials_file="credentials.json", with_metadata=True))

```

import pathway as pw data_sources = [] data_sources.append( pw.io.fs.read( "./data", format="binary", mode="streaming", with_metadata=True, ) # This creates a `pathway` connector that tracks # all the files in the ./data directory ) # This creates a connector that tracks files in Google drive. # please follow the instructions at https://pathway.com/developers/tutorials/connectors/gdrive-connector/ to get credentials # data_sources.append( # pw.io.gdrive.read(object_id="17H4YpBOAKQzEJ93xmC2z170l0bP2npMy", service_user_credentials_file="credentials.json", with_metadata=True))
### Create the document indexing pipeline¶
Let us create the document indexing pipeline. The `transformations` should be a list of `TransformComponent`s ending with an `Embedding` transformation.
In this example, let's first split the text first using `TokenTextSplitter`, then embed with `OpenAIEmbedding`.
In [ ]:
Copied!
```
from pathway.xpacks.llm.vector_store import VectorStoreServer
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.node_parser import TokenTextSplitter

embed_model = OpenAIEmbedding(embed_batch_size=10)

transformations_example = [
    TokenTextSplitter(
        chunk_size=150,
        chunk_overlap=10,
        separator=" ",
    ),
    embed_model,
]

processing_pipeline = VectorStoreServer.from_llamaindex_components(
    *data_sources,
    transformations=transformations_example,
)

# Define the Host and port that Pathway will be on
PATHWAY_HOST = "127.0.0.1"
PATHWAY_PORT = 8754

# `threaded` runs pathway in detached mode, we have to set it to False when running from terminal or container
# for more information on `with_cache` check out https://pathway.com/developers/api-docs/persistence-api
processing_pipeline.run_server(
    host=PATHWAY_HOST, port=PATHWAY_PORT, with_cache=False, threaded=True
)

```

from pathway.xpacks.llm.vector_store import VectorStoreServer from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core.node_parser import TokenTextSplitter embed_model = OpenAIEmbedding(embed_batch_size=10) transformations_example = [ TokenTextSplitter( chunk_size=150, chunk_overlap=10, separator=" ", ), embed_model, ] processing_pipeline = VectorStoreServer.from_llamaindex_components( *data_sources, transformations=transformations_example, ) # Define the Host and port that Pathway will be on PATHWAY_HOST = "127.0.0.1" PATHWAY_PORT = 8754 # `threaded` runs pathway in detached mode, we have to set it to False when running from terminal or container # for more information on `with_cache` check out https://pathway.com/developers/api-docs/persistence-api processing_pipeline.run_server( host=PATHWAY_HOST, port=PATHWAY_PORT, with_cache=False, threaded=True )
### Connect the reader to the custom pipeline¶
In [ ]:
Copied!
```
from llama_index.readers.pathway import PathwayReader

reader = PathwayReader(host=PATHWAY_HOST, port=PATHWAY_PORT)
# let us search with some text
reader.load_data(query_text="What is Pathway")

```

from llama_index.readers.pathway import PathwayReader reader = PathwayReader(host=PATHWAY_HOST, port=PATHWAY_PORT) # let us search with some text reader.load_data(query_text="What is Pathway")
