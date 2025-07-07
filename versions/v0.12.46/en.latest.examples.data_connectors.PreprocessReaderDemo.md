# Preprocess¶
Preprocess is an API service that splits any kind of document into optimal chunks of text for use in language model tasks.
Given documents in input `Preprocess` splits them into chunks of text that respect the layout and semantics of the original document. We split the content by taking into account sections, paragraphs, lists, images, data tables, text tables, and slides, and following the content semantics for long texts.
Preprocess supports:
  * PDFs
  * Microsoft Office documents (Word, PowerPoint, Excel)
  * OpenOffice documents (ods, odt, odp)
  * HTML content (web pages, articles, emails)
  * plain text.


`PreprocessLoader` interact the `Preprocess API library` to provide document conversion and chunking or to load already chunked files inside LangChain.
## Requirements¶
Install the `Python Preprocess library` if it is not already present:
In [ ]:
Copied!
```
# Install Preprocess Python SDK package
# $ pip install pypreprocess

```

# Install Preprocess Python SDK package # $ pip install pypreprocess
## Usage¶
To use Preprocess loader, you need to pass the `Preprocess API Key`. When initializing `PreprocessReader`, you should pass your `API Key`, if you don't have it yet, please ask for one at support@preprocess.co. Without an `API Key`, the loader will raise an error.
To chunk a file pass a valid filepath and the reader will start converting and chunking it. `Preprocess` will chunk your files by applying an internal `Splitter`. For this reason, you should not parse the document into nodes using a `Splitter` or applying a `Splitter` while transforming documents in your `IngestionPipeline`.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.readers.preprocess import PreprocessReader

```

from llama_index.core import VectorStoreIndex from llama_index.readers.preprocess import PreprocessReader
In [ ]:
Copied!
```
loader = PreprocessReader(
    api_key="your-api-key", filepath="valid/path/to/file"
)

```

loader = PreprocessReader( api_key="your-api-key", filepath="valid/path/to/file" )
If you want to handle the nodes directly:
In [ ]:
Copied!
```
nodes = loader.get_nodes()

# import the nodes in a Vector Store with your configuration
index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine()

```

nodes = loader.get_nodes() # import the nodes in a Vector Store with your configuration index = VectorStoreIndex(nodes) query_engine = index.as_query_engine()
By default `load_data()` returns a document for each chunk, remember to not apply any splitting to these documents
In [ ]:
Copied!
```
documents = loader.load_data()

# don't apply any Splitter parser to documents
# if you have an ingestion pipeline you should not apply a Splitter in the transformations
# import the documents in a Vector Store, if you set the service_context parameter remember to avoid including a splitter
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()

```

documents = loader.load_data() # don't apply any Splitter parser to documents # if you have an ingestion pipeline you should not apply a Splitter in the transformations # import the documents in a Vector Store, if you set the service_context parameter remember to avoid including a splitter index = VectorStoreIndex.from_documents(documents) query_engine = index.as_query_engine()
In [ ]:
Copied!
```
data = loader.load()

```

data = loader.load()
If you want to return only the extracted text and handle it with custom pipelines set `return_whole_document = True`
In [ ]:
Copied!
```
document = loader.load_data(return_whole_document=True)

```

document = loader.load_data(return_whole_document=True)
If you want to load already chunked files you can do it via `process_id` passing it to the reader.
In [ ]:
Copied!
```
# pass a process_id obtained from a previous instance and get the chunks as one string inside a Document
loader = PreprocessReader(api_key="your-api-key", process_id="your-process-id")

```

# pass a process_id obtained from a previous instance and get the chunks as one string inside a Document loader = PreprocessReader(api_key="your-api-key", process_id="your-process-id")
## Other info¶
`PreprocessReader` is based on `pypreprocess` from Preprocess library. For more information or other integration needs please check the documentation.
