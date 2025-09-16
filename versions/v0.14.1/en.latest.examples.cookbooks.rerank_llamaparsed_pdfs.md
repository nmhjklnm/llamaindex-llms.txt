![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Reranking top pages from PDF using LlamaParse and ZeroEntropy¶
In this guide, we'll build a simple workflow to parse PDF documents into text using LlamaParse and then query and rerank the textual data.
* * *
### Pre-requisites¶
  * Python 3.8+
  * `zeroentropy` client
  * `llama_cloud_services` client
  * A ZeroEntropy API key (Get yours here)
  * A LlamaParse API key (Get yours here)


### What You'll Learn¶
  * How to use LlamaParse to accurately convert PDF documents into markdown
  * How to use ZeroEntropy to semantically index and query the parsed documents
  * How to rerank your results using ZeroEntropy's reranker zerank-1 to boost accuracy


### Setting up your ZeroEntropy Client and LlamaParse Client¶
First, install dependencies:
In [ ]:
Copied!
```
!pip install zeroentropy python-dotenv llama_cloud_services requests

```

!pip install zeroentropy python-dotenv llama_cloud_services requests
Now load your API keys and initialize the clients
In [ ]:
Copied!
```
# Get your API keys from the ZeroEntropy and LlamaParse websites
# https://dashboard.zeroentropy.dev/
# https://docs.cloud.llamaindex.ai/api_key
ZEROENTROPY_API_KEY = "your_api_key_here"
LLAMAPARSE_API_KEY = "your_api_key_here"

```

# Get your API keys from the ZeroEntropy and LlamaParse websites # https://dashboard.zeroentropy.dev/ # https://docs.cloud.llamaindex.ai/api_key ZEROENTROPY_API_KEY = "your_api_key_here" LLAMAPARSE_API_KEY = "your_api_key_here"
In [ ]:
Copied!
```
from zeroentropy import AsyncZeroEntropy, ConflictError
from llama_cloud_services import LlamaParse
import os

# We initialize the AsyncZeroEntropy client in order to parse multiple documents in parallel
# If you want to parse a single document, you can use the synchronous client instead
zclient = AsyncZeroEntropy(api_key=ZEROENTROPY_API_KEY)

# We initialize the llama_parse client to parse the PDF documents into text
llamaParser = LlamaParse(
    api_key=LLAMAPARSE_API_KEY,
    num_workers=1,  # if multiple files passed, split in `num_workers` API calls
    result_type="text",
    verbose=True,
    language="en",  # optionally define a language, default=en
)

```

from zeroentropy import AsyncZeroEntropy, ConflictError from llama_cloud_services import LlamaParse import os # We initialize the AsyncZeroEntropy client in order to parse multiple documents in parallel # If you want to parse a single document, you can use the synchronous client instead zclient = AsyncZeroEntropy(api_key=ZEROENTROPY_API_KEY) # We initialize the llama_parse client to parse the PDF documents into text llamaParser = LlamaParse( api_key=LLAMAPARSE_API_KEY, num_workers=1, # if multiple files passed, split in `num_workers` API calls result_type="text", verbose=True, language="en", # optionally define a language, default=en )
### Adding a collection to the ZeroEntropy client¶
In [ ]:
Copied!
```
collection_name = "my_collection"
await zclient.collections.add(collection_name=collection_name)

```

collection_name = "my_collection" await zclient.collections.add(collection_name=collection_name)
Now define a function to download and extract PDF files from Dropbox directly to memory:
In [ ]:
Copied!
```
import requests
import zipfile
import asyncio
import io
from typing import List, Tuple


def download_and_extract_dropbox_zip_to_memory(
    url: str,
) -> List[Tuple[str, bytes]]:
    """Download and extract a zip file from Dropbox URL directly to memory.

    Returns:
        List of tuples containing (filename, file_content_bytes)
    """
    try:
        # Download the zip file
        print(f"Downloading zip file from: {url}")
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Read zip content into memory
        zip_content = io.BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            zip_content.write(chunk)
        zip_content.seek(0)

        # Extract files from zip in memory
        files_in_memory = []
        with zipfile.ZipFile(zip_content, "r") as zip_ref:
            for file_info in zip_ref.infolist():
                if (
                    not file_info.is_dir()
                    and file_info.filename.lower().endswith(".pdf")
                ):
                    file_content = zip_ref.read(file_info.filename)
                    files_in_memory.append((file_info.filename, file_content))
                    print(
                        f"Loaded {file_info.filename} ({len(file_content)} bytes)"
                    )

        print(
            f"Successfully loaded {len(files_in_memory)} PDF files into memory"
        )
        return files_in_memory

    except Exception as e:
        print(f"Error downloading/extracting zip file: {e}")
        raise


# Download and extract files from Dropbox directly to memory
dropbox_url = "https://www.dropbox.com/scl/fi/oi6kf91gz8h76d2wt57mb/example_docs.zip?rlkey=mf21tvyb65tyrjkr1t2szt226&dl=1"
files_in_memory = download_and_extract_dropbox_zip_to_memory(dropbox_url)

```

import requests import zipfile import asyncio import io from typing import List, Tuple def download_and_extract_dropbox_zip_to_memory( url: str, ) -> List[Tuple[str, bytes]]: """Download and extract a zip file from Dropbox URL directly to memory. Returns: List of tuples containing (filename, file_content_bytes) """ try: # Download the zip file print(f"Downloading zip file from: {url}") response = requests.get(url, stream=True) response.raise_for_status() # Read zip content into memory zip_content = io.BytesIO() for chunk in response.iter_content(chunk_size=8192): zip_content.write(chunk) zip_content.seek(0) # Extract files from zip in memory files_in_memory = [] with zipfile.ZipFile(zip_content, "r") as zip_ref: for file_info in zip_ref.infolist(): if ( not file_info.is_dir() and file_info.filename.lower().endswith(".pdf") ): file_content = zip_ref.read(file_info.filename) files_in_memory.append((file_info.filename, file_content)) print( f"Loaded {file_info.filename} ({len(file_content)} bytes)" ) print( f"Successfully loaded {len(files_in_memory)} PDF files into memory" ) return files_in_memory except Exception as e: print(f"Error downloading/extracting zip file: {e}") raise # Download and extract files from Dropbox directly to memory dropbox_url = "https://www.dropbox.com/scl/fi/oi6kf91gz8h76d2wt57mb/example_docs.zip?rlkey=mf21tvyb65tyrjkr1t2szt226&dl=1" files_in_memory = download_and_extract_dropbox_zip_to_memory(dropbox_url)
```
Downloading zip file from: https://www.dropbox.com/scl/fi/oi6kf91gz8h76d2wt57mb/example_docs.zip?rlkey=mf21tvyb65tyrjkr1t2szt226&dl=1
Loaded example_docs/S-P-Global-2024-Annual-Report.pdf (2434264 bytes)
Loaded example_docs/annual-report-sg-en-spy.pdf (603698 bytes)
Loaded example_docs/dashboard-sp-500-factor.pdf (1717787 bytes)
Successfully loaded 3 PDF files into memory

```

### Parsing PDFs using LlamaParse¶
Let's download the PDF files from Dropbox and parse them directly in memory using LlamaParse:
In [ ]:
Copied!
```
# Create file-like objects for LlamaParse
file_objects = []
file_names = []

for filename, file_content in files_in_memory:
    # Create a file-like object from bytes
    file_obj = io.BytesIO(file_content)
    file_obj.name = filename  # Set the name attribute for LlamaParse
    file_objects.append(file_obj)
    file_names.append(filename)

# Parse all PDF files at once using LlamaParse
# Include extra_info with file names formatted as dictionaries for byte data parsing
print(f"Parsing {len(file_objects)} PDF files...")

# Use async parsing to avoid nested event loop issues
text_data = await asyncio.gather(
    *[
        llamaParser.aparse(file_obj, extra_info={"file_name": name})
        for file_obj, name in zip(file_objects, file_names)
    ]
)
print(f"Successfully parsed {len(text_data)} documents")

```

# Create file-like objects for LlamaParse file_objects = [] file_names = [] for filename, file_content in files_in_memory: # Create a file-like object from bytes file_obj = io.BytesIO(file_content) file_obj.name = filename # Set the name attribute for LlamaParse file_objects.append(file_obj) file_names.append(filename) # Parse all PDF files at once using LlamaParse # Include extra_info with file names formatted as dictionaries for byte data parsing print(f"Parsing {len(file_objects)} PDF files...") # Use async parsing to avoid nested event loop issues text_data = await asyncio.gather( *[ llamaParser.aparse(file_obj, extra_info={"file_name": name}) for file_obj, name in zip(file_objects, file_names) ] ) print(f"Successfully parsed {len(text_data)} documents")
```
Parsing 3 PDF files...
Started parsing the file under job_id a1324745-c58b-4a24-b757-c6a6a58e57cd
Started parsing the file under job_id 326b947e-9d95-4dc3-aeaf-440b9cc03016
Started parsing the file under job_id b8534aa0-ed69-4079-a720-1b2471066c6f
............Successfully parsed 3 documents

```

## Organizing your documents¶
Once parsed, we form a list of documents with a list of the pages within them.
In [ ]:
Copied!
```
docs = []

for dindex, doc in enumerate(text_data):
    pages = []
    for index, page in enumerate(doc.pages):
        pages.append(page.text)
    docs.append(pages)

print(f"Organized {len(docs)} documents with pages")
if docs:
    print(f"First document has {len(docs[0])} pages")

```

docs = [] for dindex, doc in enumerate(text_data): pages = [] for index, page in enumerate(doc.pages): pages.append(page.text) docs.append(pages) print(f"Organized {len(docs)} documents with pages") if docs: print(f"First document has {len(docs[0])} pages")
```
Organized 3 documents with pages
First document has 104 pages

```

## Querying with ZeroEntropy¶
We'll now define functions to upload the documents as text pages asynchroniously.
In [ ]:
Copied!
```
import asyncio
from tqdm.asyncio import tqdm

sem = asyncio.Semaphore(16)


async def add_document_with_pages(
    collection_name: str, filename: str, pages: list, doc_index: int
):
    """Add a single document with multiple pages to the collection."""
    async with sem:  # Limit concurrent operations
        for retry in range(3):  # Retry logic
            try:
                response = await zclient.documents.add(
                    collection_name=collection_name,
                    path=filename,  # Use the actual filename as path
                    content={
                        "type": "text-pages",
                        "pages": pages,  # Send list of strings directly
                    },
                )
                return response
            except ConflictError:
                print(
                    f"Document '{filename}' already exists in collection '{collection_name}'"
                )
                break
            except Exception as e:
                if retry == 2:  # Last retry
                    print(f"Failed to add document '{filename}': {e}")
                    return None
                await asyncio.sleep(0.1 * (retry + 1))  # Exponential backoff


async def upload_documents_async(
    docs: list, file_names: list, collection_name: str
):
    """
    Upload documents asynchronously to ZeroEntropy collection.

    Args:
        docs: 2D array where docs[i] contains the list of pages (strings) for document i
        file_names: Array where file_names[i] contains the path for document i
        collection_name: Name of the collection to add documents to
    """

    # Validate input arrays have same length
    if len(docs) != len(file_names):
        raise ValueError("docs and file_names must have the same length")

    # Print starting message
    print(f"Starting upload of {len(docs)} documents...")

    # Create tasks for all documents
    tasks = [
        add_document_with_pages(collection_name, file_names[i], docs[i], i)
        for i in range(len(docs))
    ]

    # Execute all tasks concurrently with progress bar
    results = await tqdm.gather(*tasks, desc="Uploading Documents")

    # Count successful uploads
    successful = sum(1 for result in results if result is not None)
    print(f"Successfully uploaded {successful}/{len(docs)} documents")

    return results

```

import asyncio from tqdm.asyncio import tqdm sem = asyncio.Semaphore(16) async def add_document_with_pages( collection_name: str, filename: str, pages: list, doc_index: int ): """Add a single document with multiple pages to the collection.""" async with sem: # Limit concurrent operations for retry in range(3): # Retry logic try: response = await zclient.documents.add( collection_name=collection_name, path=filename, # Use the actual filename as path content={ "type": "text-pages", "pages": pages, # Send list of strings directly }, ) return response except ConflictError: print( f"Document '{filename}' already exists in collection '{collection_name}'" ) break except Exception as e: if retry == 2: # Last retry print(f"Failed to add document '{filename}': {e}") return None await asyncio.sleep(0.1 * (retry + 1)) # Exponential backoff async def upload_documents_async( docs: list, file_names: list, collection_name: str ): """ Upload documents asynchronously to ZeroEntropy collection. Args: docs: 2D array where docs[i] contains the list of pages (strings) for document i file_names: Array where file_names[i] contains the path for document i collection_name: Name of the collection to add documents to """ # Validate input arrays have same length if len(docs) != len(file_names): raise ValueError("docs and file_names must have the same length") # Print starting message print(f"Starting upload of {len(docs)} documents...") # Create tasks for all documents tasks = [ add_document_with_pages(collection_name, file_names[i], docs[i], i) for i in range(len(docs)) ] # Execute all tasks concurrently with progress bar results = await tqdm.gather(*tasks, desc="Uploading Documents") # Count successful uploads successful = sum(1 for result in results if result is not None) print(f"Successfully uploaded {successful}/{len(docs)} documents") return results
### Querying documents with ZeroEntropy¶
First we will upload documents
In [ ]:
Copied!
```
await upload_documents_async(docs, file_names, collection_name)

```

await upload_documents_async(docs, file_names, collection_name)
```
Starting upload of 3 documents...

```

```
Uploading Documents: 100%|██████████| 3/3 [00:00<00:00,  3.42it/s]
```

```
Successfully uploaded 3/3 documents

```



Out[ ]:
```
[DocumentAddResponse(message='Success!'),
 DocumentAddResponse(message='Success!'),
 DocumentAddResponse(message='Success!')]
```

Query for the top 5 pages
In [ ]:
Copied!
```
response = await zclient.queries.top_pages(
    collection_name=collection_name,
    query="What are the top 100 stocks in the S&P 500?",
    k=5,
)

```

response = await zclient.queries.top_pages( collection_name=collection_name, query="What are the top 100 stocks in the S&P 500?", k=5, )
Now let's define a function to rerank the pages in the response:
In [ ]:
Copied!
```
async def rerank_top_pages_with_metadata(
    query: str, top_pages_response, collection_name: str
):
    """
    Rerank the results from a top_pages query and return re-ordered list with metadata.

    Args:
        query: The query string to use for reranking
        top_pages_response: The response object from zclient.queries.top_pages()
        collection_name: Name of the collection to fetch page content from

    Returns:
        List of dicts with 'path', 'page_index', and 'rerank_score' in reranked order
    """

    # Fetch page content and store metadata for each result
    documents = []
    metadata = []

    for result in top_pages_response.results:
        # Fetch the actual page content
        page_info = await zclient.documents.get_page_info(
            collection_name=collection_name,
            path=result.path,
            page_index=result.page_index,
            include_content=True,
        )

        # Get page content and ensure it's not empty
        page_content = page_info.page.content
        if page_content and page_content.strip():
            documents.append(page_content.strip())
            metadata.append(
                {
                    "path": result.path,
                    "page_index": result.page_index,
                    "original_score": result.score,
                }
            )
        else:
            # Include empty pages with fallback content
            documents.append("No content available")
            metadata.append(
                {
                    "path": result.path,
                    "page_index": result.page_index,
                    "original_score": result.score,
                }
            )

    if not documents:
        raise ValueError("No documents found to rerank")

    # Perform reranking
    rerank_response = await zclient.models.rerank(
        model="zerank-1", query=query, documents=documents
    )

    # Create re-ordered list with metadata
    reranked_results = []
    for rerank_result in rerank_response.results:
        original_metadata = metadata[rerank_result.index]
        reranked_results.append(
            {
                "path": original_metadata["path"],
                "page_index": original_metadata["page_index"],
                "rerank_score": rerank_result.relevance_score,
            }
        )

    return reranked_results

```

async def rerank_top_pages_with_metadata( query: str, top_pages_response, collection_name: str ): """ Rerank the results from a top_pages query and return re-ordered list with metadata. Args: query: The query string to use for reranking top_pages_response: The response object from zclient.queries.top_pages() collection_name: Name of the collection to fetch page content from Returns: List of dicts with 'path', 'page_index', and 'rerank_score' in reranked order """ # Fetch page content and store metadata for each result documents = [] metadata = [] for result in top_pages_response.results: # Fetch the actual page content page_info = await zclient.documents.get_page_info( collection_name=collection_name, path=result.path, page_index=result.page_index, include_content=True, ) # Get page content and ensure it's not empty page_content = page_info.page.content if page_content and page_content.strip(): documents.append(page_content.strip()) metadata.append( { "path": result.path, "page_index": result.page_index, "original_score": result.score, } ) else: # Include empty pages with fallback content documents.append("No content available") metadata.append( { "path": result.path, "page_index": result.page_index, "original_score": result.score, } ) if not documents: raise ValueError("No documents found to rerank") # Perform reranking rerank_response = await zclient.models.rerank( model="zerank-1", query=query, documents=documents ) # Create re-ordered list with metadata reranked_results = [] for rerank_result in rerank_response.results: original_metadata = metadata[rerank_result.index] reranked_results.append( { "path": original_metadata["path"], "page_index": original_metadata["page_index"], "rerank_score": rerank_result.relevance_score, } ) return reranked_results
Run the function and see the results!
In [ ]:
Copied!
```
reranked_results = await rerank_top_pages_with_metadata(
    query="What are the top 100 stocks in the S&P 500?",
    top_pages_response=response,
    collection_name=collection_name,
)

# Display results
print("Reranked Results with Metadata:")
for i, result in enumerate(reranked_results, 1):
    print(
        f"Rank {i}: {result['path']} (Page {result['page_index']}) - Score: {result['rerank_score']:.4f}"
    )

```

reranked_results = await rerank_top_pages_with_metadata( query="What are the top 100 stocks in the S&P 500?", top_pages_response=response, collection_name=collection_name, ) # Display results print("Reranked Results with Metadata:") for i, result in enumerate(reranked_results, 1): print( f"Rank {i}: {result['path']} (Page {result['page_index']}) - Score: {result['rerank_score']:.4f}" )
```
Reranked Results with Metadata:
Rank 1: example_docs/dashboard-sp-500-factor.pdf (Page 9) - Score: 0.8472
Rank 2: example_docs/dashboard-sp-500-factor.pdf (Page 12) - Score: 0.8311
Rank 3: example_docs/dashboard-sp-500-factor.pdf (Page 8) - Score: 0.7941
Rank 4: example_docs/dashboard-sp-500-factor.pdf (Page 2) - Score: 0.4571
Rank 5: example_docs/dashboard-sp-500-factor.pdf (Page 4) - Score: 0.4511

```

### ✅ That's It!¶
You've now built a working semantic search engine that processes PDF files entirely in memory using ZeroEntropy and LlamaParse — no local file storage required!
