![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# AirtrainAI Cookbook¶
Airtrain is a tool supporting unstructured/low-structured text datasets. It allows automated clustering, document classification, and more.
This cookbook showcases how to ingest and transform/enrich data with LlamaIndex and then upload the data to Airtrain for further processing and exploration.
## Installation & Setup¶
In [ ]:
Copied!
```
# Install some libraries we'll use for our examples. These
# are not required to use Airtrain with LlamaIndex, and are just
# there to help us illustrate use.
%pip install llama-index-embeddings-openai==0.2.4
%pip install llama-index-readers-web==0.2.2
%pip install llama-index-readers-github==0.2.0

# Install Airtrain SDK with LlamaIndex integration
%pip install airtrain-py[llama-index]

```

# Install some libraries we'll use for our examples. These # are not required to use Airtrain with LlamaIndex, and are just # there to help us illustrate use. %pip install llama-index-embeddings-openai==0.2.4 %pip install llama-index-readers-web==0.2.2 %pip install llama-index-readers-github==0.2.0 # Install Airtrain SDK with LlamaIndex integration %pip install airtrain-py[llama-index]
In [ ]:
Copied!
```
# Running async code in a notebook requires using nest_asyncio, and we will
# use some async examples. So we will set up nest_asyncio here. Outside
# an async context or outside a notebook, this step is not required.
import nest_asyncio

nest_asyncio.apply()

```

# Running async code in a notebook requires using nest_asyncio, and we will # use some async examples. So we will set up nest_asyncio here. Outside # an async context or outside a notebook, this step is not required. import nest_asyncio nest_asyncio.apply()
### API Key Setup¶
Set up the API keys that will be required to run the examples that follow. The GitHub API token and OpenAI API key are only required for the example 'Usage with Readers/Embeddings/Splitters'. Instructions for getting a GitHub access token are here while an OpenAI API key can be obtained here.
To obtain your Airtrain API Key:
  * Create an Airtrain Account by visting here
  * View "Settings" in the lower left, then go to "Billing" to sign up for a pro account or start a trial
  * Copy your API key from the "Airtrain API Key" tab in "Billing"


Note that the Airtrain trial only allows ONE dataset at a time. As this notebook creates many, you may need to delete the dataset in the Airtrain UI as you go along, to make space for another one.
In [ ]:
Copied!
```
import os

os.environ["GITHUB_TOKEN"] = "<your GitHub token>"
os.environ["OPENAI_API_KEY"] = "<your OpenAi API key>"

os.environ["AIRTRAIN_API_KEY"] = "<your Airtrain API key>"

```

import os os.environ["GITHUB_TOKEN"] = "" os.environ["OPENAI_API_KEY"] = "" os.environ["AIRTRAIN_API_KEY"] = ""
## Example 1: Usage with Readers/Embeddings/Splitters¶
Some of the core abstractions in LlamaIndex are Documents and Nodes. Airtrain's LlamaIndex integration allows you to create an Airtrain dataset using any iterable collection of either of these, via the `upload_from_llama_nodes` function.
To illustrate the flexibility of this, we'll do both:
  1. Create a dataset directly of documents. In this case whole pages from the Sematic docs.
  2. Use OpenAI embeddings and the `SemanticSplitterNodeParser` to split those documents into nodes, and create a dataset from those.


In [ ]:
Copied!
```
import os

import airtrain as at
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.github import GithubRepositoryReader, GithubClient

```

import os import airtrain as at from llama_index.core.node_parser import SemanticSplitterNodeParser from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.readers.github import GithubRepositoryReader, GithubClient
The next step is to set up our reader. In this case we're using the GitHub reader, but that's just for illustrative purposes. Airtrain can ingest documents no matter what reader they came from originally.
In [ ]:
Copied!
```
github_token = os.environ.get("GITHUB_TOKEN")
github_client = GithubClient(github_token=github_token, verbose=True)
reader = GithubRepositoryReader(
    github_client=github_client,
    owner="sematic-ai",
    repo="sematic",
    use_parser=False,
    verbose=False,
    filter_directories=(
        ["docs"],
        GithubRepositoryReader.FilterType.INCLUDE,
    ),
    filter_file_extensions=(
        [
            ".md",
        ],
        GithubRepositoryReader.FilterType.INCLUDE,
    ),
)
read_kwargs = dict(branch="main")

```

github_token = os.environ.get("GITHUB_TOKEN") github_client = GithubClient(github_token=github_token, verbose=True) reader = GithubRepositoryReader( github_client=github_client, owner="sematic-ai", repo="sematic", use_parser=False, verbose=False, filter_directories=( ["docs"], GithubRepositoryReader.FilterType.INCLUDE, ), filter_file_extensions=( [ ".md", ], GithubRepositoryReader.FilterType.INCLUDE, ), ) read_kwargs = dict(branch="main")
Read the documents with the reader
In [ ]:
Copied!
```
documents = reader.load_data(**read_kwargs)

```

documents = reader.load_data(**read_kwargs)
### Create dataset directly from documents¶
You can create an Airtrain dataset directly from these documents without doing any further processing. In this case, Airtrain will automatically embed the documents for you before generating further insights. Each row in the dataset will represent an entire markdown document. Airtrain will automatically provide insights like semantic clustering of your documents, allowing you to browse through the documents by looking at ones that cover similar topics or uncovering subsets of documents that you might want to remove.
Though additional processing beyond basic document retrieval is not _required_ , it is _allowed_. You can enrich the documents with metadata, filter them, or manipulate them in any way you like before uploading to Airtrain.
In [ ]:
Copied!
```
result = at.upload_from_llama_nodes(
    documents,
    name="Sematic Docs Dataset: Whole Documents",
)
print(f"Uploaded {result.size} rows to '{result.name}'. View at: {result.url}")

```

result = at.upload_from_llama_nodes( documents, name="Sematic Docs Dataset: Whole Documents", ) print(f"Uploaded {result.size} rows to '{result.name}'. View at: {result.url}")
```
Uploaded 42 rows to 'Sematic Docs Dataset: Whole Documents'. View at: https://app.airtrain.ai/dataset/7fd09dca-81b9-42b8-acc9-01ce08302b16

```

### Create dataset after splitting and embedding¶
If you wish to view a dataset oriented towards nodes within documents rather than whole documents, you can do that as well. Airtrain will automatically create insights like a 2d PCA projection of your embedding vectors, so you can visually explore the embedding space from which your RAG nodes will be retrieved. You can also click on individual rows and look at the ones that are nearest to it in the full n-dimensional embedding space, to drill down further. Automated clusters and other insights will also be generated to enrich and aid your exploration.
Here we'll use OpenAI embeddings and a `SemanticSplitterNodeParser` splitter, but you can use any other LlamaIndex tooling you like to process your nodes before uploading to Airtrain. You can even skip embedding them yourself entirely, in which case Airtrain will embed the nodes for you.
In [ ]:
Copied!
```
embed_model = OpenAIEmbedding()
splitter = SemanticSplitterNodeParser(
    buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model
)
nodes = splitter.get_nodes_from_documents(documents)

```

embed_model = OpenAIEmbedding() splitter = SemanticSplitterNodeParser( buffer_size=1, breakpoint_percentile_threshold=95, embed_model=embed_model ) nodes = splitter.get_nodes_from_documents(documents)
⚠️ **Note** ⚠️: If you are on an Airtrain trial and already created a whole-document dataset, you will need to delete it before uploading a new dataset.
In [ ]:
Copied!
```
result = at.upload_from_llama_nodes(
    nodes,
    name="Sematic Docs, split + embedded",
)
print(f"Uploaded {result.size} rows to {result.name}. View at: {result.url}")

```

result = at.upload_from_llama_nodes( nodes, name="Sematic Docs, split + embedded", ) print(f"Uploaded {result.size} rows to {result.name}. View at: {result.url}")
```
Uploaded 137 rows to Sematic Docs, split + embedded. View at: https://app.airtrain.ai/dataset/ebec9bcc-6ed8-4165-a0de-29bef740c70b

```

## Example 2: Using the Workflow API¶
Since documents and nodes are the core abstractions the Airtrain integration works with, and these abstractions are shared in LlamaIndex's workflows API, you can also use Airtrain as part of a broader workflow. Here we will illustrate usage by scraping a few Hacker News comment threads, but again you are not restricted to web scraping workflows; any workflow producing documents or nodes will do.
In [ ]:
Copied!
```
import asyncio

from llama_index.core.schema import Node
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.readers.web import AsyncWebPageReader

from airtrain import DatasetMetadata, upload_from_llama_nodes

```

import asyncio from llama_index.core.schema import Node from llama_index.core.workflow import ( Context, Event, StartEvent, StopEvent, Workflow, step, ) from llama_index.readers.web import AsyncWebPageReader from airtrain import DatasetMetadata, upload_from_llama_nodes
Specify the comment threads we'll be scraping from. The particular ones in this example were on or near the front page on September 30th, 2024. If you wish to ingest from pages besides Hacker News, be aware that some sites have their content rendered client-side, in which case you might want to use a reader like the `WholeSiteReader`, which uses a headless Chrome driver to render the page before returning the documents. For here we'll use a page with server-side rendered HTML for simplicity.
In [ ]:
Copied!
```
URLS = [
    "https://news.ycombinator.com/item?id=41694044",
    "https://news.ycombinator.com/item?id=41696046",
    "https://news.ycombinator.com/item?id=41693087",
    "https://news.ycombinator.com/item?id=41695756",
    "https://news.ycombinator.com/item?id=41666269",
    "https://news.ycombinator.com/item?id=41697137",
    "https://news.ycombinator.com/item?id=41695840",
    "https://news.ycombinator.com/item?id=41694712",
    "https://news.ycombinator.com/item?id=41690302",
    "https://news.ycombinator.com/item?id=41695076",
    "https://news.ycombinator.com/item?id=41669747",
    "https://news.ycombinator.com/item?id=41694504",
    "https://news.ycombinator.com/item?id=41697032",
    "https://news.ycombinator.com/item?id=41694025",
    "https://news.ycombinator.com/item?id=41652935",
    "https://news.ycombinator.com/item?id=41693979",
    "https://news.ycombinator.com/item?id=41696236",
    "https://news.ycombinator.com/item?id=41696434",
    "https://news.ycombinator.com/item?id=41688469",
    "https://news.ycombinator.com/item?id=41646782",
    "https://news.ycombinator.com/item?id=41689332",
    "https://news.ycombinator.com/item?id=41688018",
    "https://news.ycombinator.com/item?id=41668896",
    "https://news.ycombinator.com/item?id=41690087",
    "https://news.ycombinator.com/item?id=41679497",
    "https://news.ycombinator.com/item?id=41687739",
    "https://news.ycombinator.com/item?id=41686722",
    "https://news.ycombinator.com/item?id=41689138",
    "https://news.ycombinator.com/item?id=41691530",
]

```

URLS = [ "https://news.ycombinator.com/item?id=41694044", "https://news.ycombinator.com/item?id=41696046", "https://news.ycombinator.com/item?id=41693087", "https://news.ycombinator.com/item?id=41695756", "https://news.ycombinator.com/item?id=41666269", "https://news.ycombinator.com/item?id=41697137", "https://news.ycombinator.com/item?id=41695840", "https://news.ycombinator.com/item?id=41694712", "https://news.ycombinator.com/item?id=41690302", "https://news.ycombinator.com/item?id=41695076", "https://news.ycombinator.com/item?id=41669747", "https://news.ycombinator.com/item?id=41694504", "https://news.ycombinator.com/item?id=41697032", "https://news.ycombinator.com/item?id=41694025", "https://news.ycombinator.com/item?id=41652935", "https://news.ycombinator.com/item?id=41693979", "https://news.ycombinator.com/item?id=41696236", "https://news.ycombinator.com/item?id=41696434", "https://news.ycombinator.com/item?id=41688469", "https://news.ycombinator.com/item?id=41646782", "https://news.ycombinator.com/item?id=41689332", "https://news.ycombinator.com/item?id=41688018", "https://news.ycombinator.com/item?id=41668896", "https://news.ycombinator.com/item?id=41690087", "https://news.ycombinator.com/item?id=41679497", "https://news.ycombinator.com/item?id=41687739", "https://news.ycombinator.com/item?id=41686722", "https://news.ycombinator.com/item?id=41689138", "https://news.ycombinator.com/item?id=41691530", ]
Next we'll define a basic event, as events are the standard way to pass data between steps in LlamaIndex workflows.
In [ ]:
Copied!
```
class CompletedDocumentRetrievalEvent(Event):
    name: str
    documents: list[Node]

```

class CompletedDocumentRetrievalEvent(Event): name: str documents: list[Node]
After that we'll define the workflow itself. In our case, this will have one step to ingest the documents from the web, one to ingest them to Airtrain, and one to wrap up the workflow.
In [ ]:
Copied!
```
class IngestToAirtrainWorkflow(Workflow):
    @step
    async def ingest_documents(
        self, ctx: Context, ev: StartEvent
    ) -> CompletedDocumentRetrievalEvent | None:
        if not ev.get("urls"):
            return None
        reader = AsyncWebPageReader(html_to_text=True)
        documents = await reader.aload_data(urls=ev.get("urls"))
        return CompletedDocumentRetrievalEvent(
            name=ev.get("name"), documents=documents
        )

    @step
    async def ingest_documents_to_airtrain(
        self, ctx: Context, ev: CompletedDocumentRetrievalEvent
    ) -> StopEvent | None:
        dataset_meta = upload_from_llama_nodes(ev.documents, name=ev.name)
        return StopEvent(result=dataset_meta)

```

class IngestToAirtrainWorkflow(Workflow): @step async def ingest_documents( self, ctx: Context, ev: StartEvent ) -> CompletedDocumentRetrievalEvent | None: if not ev.get("urls"): return None reader = AsyncWebPageReader(html_to_text=True) documents = await reader.aload_data(urls=ev.get("urls")) return CompletedDocumentRetrievalEvent( name=ev.get("name"), documents=documents ) @step async def ingest_documents_to_airtrain( self, ctx: Context, ev: CompletedDocumentRetrievalEvent ) -> StopEvent | None: dataset_meta = upload_from_llama_nodes(ev.documents, name=ev.name) return StopEvent(result=dataset_meta)
Since the workflow API treats async code as a first-class citizen, we'll define an async `main` to drive the workflow.
In [ ]:
Copied!
```
async def main() -> None:
    workflow = IngestToAirtrainWorkflow()
    result = await workflow.run(
        name="My HN Discussions Dataset",
        urls=URLS,
    )
    print(
        f"Uploaded {result.size} rows to {result.name}. View at: {result.url}"
    )

```

async def main() -> None: workflow = IngestToAirtrainWorkflow() result = await workflow.run( name="My HN Discussions Dataset", urls=URLS, ) print( f"Uploaded {result.size} rows to {result.name}. View at: {result.url}" )
Finally, we'll execute the async main using an asyncio event loop.
⚠️ **Note** ⚠️: If you are on an Airtrain trial and already ran examples above, you will need to delete the resulting dataset(s) before uploading a new one.
In [ ]:
Copied!
```
asyncio.run(main())  # actually run the main & the workflow

```

asyncio.run(main()) # actually run the main & the workflow
```
error fetching page from https://news.ycombinator.com/item?id=41693087
error fetching page from https://news.ycombinator.com/item?id=41666269
error fetching page from https://news.ycombinator.com/item?id=41697137
error fetching page from https://news.ycombinator.com/item?id=41697032
error fetching page from https://news.ycombinator.com/item?id=41652935
error fetching page from https://news.ycombinator.com/item?id=41696434
error fetching page from https://news.ycombinator.com/item?id=41688469
error fetching page from https://news.ycombinator.com/item?id=41646782
error fetching page from https://news.ycombinator.com/item?id=41668896

```

```
Uploaded 20 rows to My HN Discussions Dataset. View at: https://app.airtrain.ai/dataset/bd330f0a-6ff1-4e51-9fe2-9900a1a42308

```

