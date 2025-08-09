# Multimodal rag guardrail gemini llmguard llmguard
## Multimodal RAG Pipeline with Guardrails Provided by LLM-GUARD¶
This guide introduces a robust **Multimodal Retrieval-Augmented Generation (RAG)** pipeline enhanced with integrated **guardrails** **LLM GUARD** for secure, reliable, and contextually accurate responses. The pipeline processes multimodal inputs such as text, tables, images, and diagrams while employing guardrails to monitor and validate both input and output. For detail information discover my README.md at: https://github.com/vntuananhbui/MultimodalRAG-LlamaIndex-Guardrail/blob/main/README.md
### Note:¶
This pipeline leverages the **Gemini 1.5 Flash** model through a free API for inference, making it accessible and cost-effective for development and experimentation.
### Extension:¶
You can also use other framework of Guardrails such as **Guardrail AI, etc...** also.
* * *
## Overview of the Pipeline¶
The Multimodal RAG pipeline is designed to overcome the limitations of traditional text-based RAG systems by natively handling diverse document layouts and modalities. It leverages both text and image embeddings to retrieve and synthesize context-aware answers.
### Key Features:¶
  1. **Multimodal Input Processing** :
     * Handles text, images, and complex layouts directly.
     * Converts document content into robust embeddings for retrieval.
  2. **Guardrails Integration** :
     * Adds input/output scanners to enforce safety and quality.
     * Dynamically validates queries and responses for risks such as toxicity or token overflow.
  3. **Custom Query Engine** :
     * Designed to incorporate guardrails into query handling.
     * Dynamically blocks, sanitizes, or validates inputs/outputs based on scanner results.
  4. **Cost-Effective Implementation** :
     * Uses **Gemini 1.5 Flash** via a free API, minimizing costs while maintaining high performance.


* * *
## Why Add Guardrails to Multimodal RAG?¶
While Multimodal RAG pipelines are powerful, they are prone to risks such as inappropriate inputs, hallucinated outputs, or exceeding token limits. Guardrails act as safeguards, ensuring:
  * **Safety** : Prevents harmful or offensive queries and outputs.
  * **Reliability** : Validates the integrity of responses.
  * **Scalability** : Enables the pipeline to handle complex scenarios dynamically.


* * *
## Architecture Overview¶
### 1. Input Scanners¶
Input scanners validate incoming queries before they are processed. For example:
  * **Toxicity Scanner** : Detects and blocks harmful language.
  * **Token Limit Scanner** : Ensures queries do not exceed processing limits.


### 2. Custom Query Engine¶
The query engine integrates retrieval and synthesis while applying guardrails at multiple stages:
  * **Pre-processing** : Validates input queries using scanners.
  * **Processing** : Retrieves relevant nodes using multimodal embeddings.
  * **Post-processing** : Sanitizes and validates outputs.


### 3. Multimodal LLM¶
The pipeline uses a **multimodal LLM (e.g., Gemini 1.5 Flash)** capable of understanding and generating context-aware text and image-based outputs. Its free API access makes it suitable for development without incurring significant costs.
* * *
## Guardrails Workflow¶
### Input Validation¶
  1. Scans incoming queries using pre-defined scanners.
  2. Blocks or sanitizes queries based on scanner results.


### Retrieval¶
  1. Fetches relevant text and image nodes.
  2. Converts content into embeddings for synthesis.


### Output Validation¶
  1. Analyzes generated responses with output scanners.
  2. Blocks or sanitizes outputs based on thresholds (e.g., toxicity).


* * *
## Benefits of the Multimodal RAG with Guardrails¶
  1. **Improved Safety** : Queries and responses are validated to reduce risk.
  2. **Enhanced Robustness** : Multimodal inputs are processed without loss of context.
  3. **Dynamic Control** : Guardrails provide flexibility to handle diverse inputs and outputs.
  4. **Cost-Efficiency** : Selective application of input/output validation optimizes resources, while the free **Gemini 1.5 Flash** API reduces operational expenses.


* * *
This pipeline demonstrates how a **natively multimodal RAG system** can be augmented with **guardrails** to deliver secure, reliable, and high-quality results in complex document environments while remaining cost-effective through the use of free APIs.
## Setup¶
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
### Setup Observability¶
### Load Data¶
Here we load the Conoco Phillips 2023 investor meeting slide deck.
In [ ]:
Copied!
```
!mkdir data
!mkdir data_images
!wget "https://static.conocophillips.com/files/2023-conocophillips-aim-presentation.pdf" -O data/conocophillips.pdf

```

!mkdir data !mkdir data_images !wget "https://static.conocophillips.com/files/2023-conocophillips-aim-presentation.pdf" -O data/conocophillips.pdf
```
mkdir: data: File exists
mkdir: data_images: File exists
zsh:1: command not found: wget

```

### Install Dependency¶
In [ ]:
Copied!
```
!pip install llama-index
!pip install llama-parse
!pip install llama-index-llms-langchain
!pip install llama-index-embeddings-huggingface
!pip install llama-index-llms-gemini
!pip install llama-index-multi-modal-llms-gemini
!pip install litellm
!pip install llm-guard

```

!pip install llama-index !pip install llama-parse !pip install llama-index-llms-langchain !pip install llama-index-embeddings-huggingface !pip install llama-index-llms-gemini !pip install llama-index-multi-modal-llms-gemini !pip install litellm !pip install llm-guard
### Model Setup¶
Setup models that will be used for downstream orchestration.
In [ ]:
Copied!
```
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini
from llama_index.multi_modal_llms.gemini import GeminiMultiModal
import os

LlamaCloud_API_KEY = ""
MultiGeminiKey = ""
GOOGLE_API_KEY = ""
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
gemini_multimodal = GeminiMultiModal(
    model_name="models/gemini-1.5-flash", api_key=MultiGeminiKey
)
api_key = GOOGLE_API_KEY
llamaAPI_KEY = LlamaCloud_API_KEY
llm = Gemini(model="models/gemini-1.5-flash", api_key=api_key)
Settings.llm = llm

```

from llama_index.core import Settings from llama_index.embeddings.huggingface import HuggingFaceEmbedding from llama_index.llms.gemini import Gemini from llama_index.multi_modal_llms.gemini import GeminiMultiModal import os LlamaCloud_API_KEY = "" MultiGeminiKey = "" GOOGLE_API_KEY = "" os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY os.environ["GEMINI_API_KEY"] = GOOGLE_API_KEY embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5") gemini_multimodal = GeminiMultiModal( model_name="models/gemini-1.5-flash", api_key=MultiGeminiKey ) api_key = GOOGLE_API_KEY llamaAPI_KEY = LlamaCloud_API_KEY llm = Gemini(model="models/gemini-1.5-flash", api_key=api_key) Settings.llm = llm
## Use LlamaParse to Parse Text and Images¶
In this example, use LlamaParse to parse both the text and images from the document.
We parse out the text in two ways:
  * in regular `text` mode using our default text layout algorithm
  * in `markdown` mode using GPT-4o (`gpt4o_mode=True`). This also allows us to capture page screenshots


In [ ]:
Copied!
```
from llama_parse import LlamaParse


parser_text = LlamaParse(result_type="text", api_key=llamaAPI_KEY)
parser_gpt4o = LlamaParse(
    result_type="markdown", gpt4o_mode=True, api_key=llamaAPI_KEY
)

```

from llama_parse import LlamaParse parser_text = LlamaParse(result_type="text", api_key=llamaAPI_KEY) parser_gpt4o = LlamaParse( result_type="markdown", gpt4o_mode=True, api_key=llamaAPI_KEY )
In [ ]:
Copied!
```
print(f"Parsing text...")
docs_text = parser_text.load_data("data/conocophillips.pdf")
print(f"Parsing PDF file...")
md_json_objs = parser_gpt4o.get_json_result("data/conocophillips.pdf")
md_json_list = md_json_objs[0]["pages"]

```

print(f"Parsing text...") docs_text = parser_text.load_data("data/conocophillips.pdf") print(f"Parsing PDF file...") md_json_objs = parser_gpt4o.get_json_result("data/conocophillips.pdf") md_json_list = md_json_objs[0]["pages"]
```
Parsing text...
Started parsing the file under job_id e79a470b-e8d3-4f55-a048-d1b3d81b6d1e
Parsing PDF file...
Started parsing the file under job_id 84943607-b630-45bd-bf89-8470840e73b5

```

In [ ]:
Copied!
```
print(md_json_list[10]["md"])

```

print(md_json_list[10]["md"])
```
# Commitment to Disciplined Reinvestment Rate

| Period       | Description                        | Reinvestment Rate | WTI Average |
|--------------|------------------------------------|-------------------|-------------|
| 2012-2016    | Industry Growth Focus              | >100%             | ~$75/BBL    |
| 2017-2022    | ConocoPhillips Strategy Reset      | <60%              | ~$63/BBL    |
| 2023E        |                                    |                   | at $80/BBL  |
| 2024-2028    | Disciplined Reinvestment Rate      | ~50%              | at $60/BBL  |
| 2029-2032    |                                    | ~6% CFO CAGR      | at $60/BBL  |

- **Historic Reinvestment Rate**: Shown in gray.
- **Reinvestment Rate at $60/BBL WTI**: Shown in blue.
- **Reinvestment Rate at $80/BBL WTI**: Shown with dashed lines.

**Note**: Reinvestment rate and cash from operations (CFO) are non-GAAP measures. Definitions and reconciliations are included in the Appendix.

```

In [ ]:
Copied!
```
image_dicts = parser_gpt4o.get_images(
    md_json_objs, download_path="data_images"
)

```

image_dicts = parser_gpt4o.get_images( md_json_objs, download_path="data_images" )
## Build Multimodal Index¶
In this section we build the multimodal index over the parsed deck.
We do this by creating **text** nodes from the document that contain metadata referencing the original image path.
In this example we're indexing the text node for retrieval. The text node has a reference to both the parsed text as well as the image screenshot.
#### Get Text Nodes¶
In [ ]:
Copied!
```
from llama_index.core.schema import TextNode
from typing import Optional

```

from llama_index.core.schema import TextNode from typing import Optional
In [ ]:
Copied!
```
# get pages loaded through llamaparse
import re


def get_page_number(file_name):
    match = re.search(r"-page-(\d+)\.jpg$", str(file_name))
    if match:
        return int(match.group(1))
    return 0


def _get_sorted_image_files(image_dir):
    """Get image files sorted by page."""
    raw_files = [f for f in list(Path(image_dir).iterdir()) if f.is_file()]
    sorted_files = sorted(raw_files, key=get_page_number)
    return sorted_files

```

# get pages loaded through llamaparse import re def get_page_number(file_name): match = re.search(r"-page-(\d+)\\.jpg$", str(file_name)) if match: return int(match.group(1)) return 0 def _get_sorted_image_files(image_dir): """Get image files sorted by page.""" raw_files = [f for f in list(Path(image_dir).iterdir()) if f.is_file()] sorted_files = sorted(raw_files, key=get_page_number) return sorted_files
In [ ]:
Copied!
```
# Assuming TextNode class is defined somewhere else in your code
# Attach image metadata to the text nodes
def get_text_nodes(docs, image_dir=None, json_dicts=None):
    """Split docs into nodes, by separator."""
    nodes = []

    # Get image files (if provided)
    image_files = (
        _get_sorted_image_files(image_dir) if image_dir is not None else None
    )

    # Get markdown texts (if provided)
    md_texts = (
        [d["md"] for d in json_dicts] if json_dicts is not None else None
    )

    # Split docs into chunks by separator
    doc_chunks = [c for d in docs for c in d.text.split("---")]

    # Handle both single-page and multi-page cases
    for idx, doc_chunk in enumerate(doc_chunks):
        chunk_metadata = {"page_num": idx + 1}

        # Check if there are image files and handle the single-page case
        if image_files is not None:
            # Use the first image file if there's only one
            image_file = (
                image_files[idx] if idx < len(image_files) else image_files[0]
            )
            chunk_metadata["image_path"] = str(image_file)

        # Check if there are markdown texts and handle the single-page case
        if md_texts is not None:
            # Use the first markdown text if there's only one
            parsed_text_md = (
                md_texts[idx] if idx < len(md_texts) else md_texts[0]
            )
            chunk_metadata["parsed_text_markdown"] = parsed_text_md

        # Add the chunk text as metadata
        chunk_metadata["parsed_text"] = doc_chunk

        # Create the TextNode with the parsed text and metadata
        node = TextNode(
            text="",
            metadata=chunk_metadata,
        )
        nodes.append(node)

    return nodes

```

# Assuming TextNode class is defined somewhere else in your code # Attach image metadata to the text nodes def get_text_nodes(docs, image_dir=None, json_dicts=None): """Split docs into nodes, by separator.""" nodes = [] # Get image files (if provided) image_files = ( _get_sorted_image_files(image_dir) if image_dir is not None else None ) # Get markdown texts (if provided) md_texts = ( [d["md"] for d in json_dicts] if json_dicts is not None else None ) # Split docs into chunks by separator doc_chunks = [c for d in docs for c in d.text.split("---")] # Handle both single-page and multi-page cases for idx, doc_chunk in enumerate(doc_chunks): chunk_metadata = {"page_num": idx + 1} # Check if there are image files and handle the single-page case if image_files is not None: # Use the first image file if there's only one image_file = ( image_files[idx] if idx < len(image_files) else image_files[0] ) chunk_metadata["image_path"] = str(image_file) # Check if there are markdown texts and handle the single-page case if md_texts is not None: # Use the first markdown text if there's only one parsed_text_md = ( md_texts[idx] if idx < len(md_texts) else md_texts[0] ) chunk_metadata["parsed_text_markdown"] = parsed_text_md # Add the chunk text as metadata chunk_metadata["parsed_text"] = doc_chunk # Create the TextNode with the parsed text and metadata node = TextNode( text="", metadata=chunk_metadata, ) nodes.append(node) return nodes
In [ ]:
Copied!
```
from pathlib import Path

# this will split into pages
text_nodes = get_text_nodes(
    docs_text,
    image_dir="/Users/macintosh/TA-DOCUMENT/StudyZone/ComputerScience/Artificial Intelligence/Llama_index/llama_index/docs/docs/examples/rag_guardrail/data_images",
    json_dicts=md_json_list,
)

```

from pathlib import Path # this will split into pages text_nodes = get_text_nodes( docs_text, image_dir="/Users/macintosh/TA-DOCUMENT/StudyZone/ComputerScience/Artificial Intelligence/Llama_index/llama_index/docs/docs/examples/rag_guardrail/data_images", json_dicts=md_json_list, )
In [ ]:
Copied!
```
print(text_nodes[0].get_content(metadata_mode="all"))

```

print(text_nodes[0].get_content(metadata_mode="all"))
```
page_num: 1
image_path: /Users/macintosh/TA-DOCUMENT/StudyZone/ComputerScience/Artificial Intelligence/Llama_index/llama_index/docs/docs/examples/rag_guardrail/data_images/84943607-b630-45bd-bf89-8470840e73b5-page_51.jpg
parsed_text_markdown: NO_CONTENT_HERE
parsed_text: ConocoPhillips
                2023 Analyst & Investor Meeting

```

#### Build Index¶
Once the text nodes are ready, we feed into our vector store index abstraction, which will index these nodes into a simple in-memory vector store (of course, you should definitely check out our 40+ vector store integrations!)
In [ ]:
Copied!
```
import os
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

if not os.path.exists("storage_nodes"):
    index = VectorStoreIndex(text_nodes, embed_model=embed_model)
    # save index to disk
    index.set_index_id("vector_index")
    index.storage_context.persist("./storage_nodes")
else:
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="storage_nodes")
    # load index
    index = load_index_from_storage(storage_context, index_id="vector_index")

retriever = index.as_retriever()

```

import os from llama_index.core import ( StorageContext, VectorStoreIndex, load_index_from_storage, ) if not os.path.exists("storage_nodes"): index = VectorStoreIndex(text_nodes, embed_model=embed_model) # save index to disk index.set_index_id("vector_index") index.storage_context.persist("./storage_nodes") else: # rebuild storage context storage_context = StorageContext.from_defaults(persist_dir="storage_nodes") # load index index = load_index_from_storage(storage_context, index_id="vector_index") retriever = index.as_retriever()
## Build Guardrail¶
Define the global rail output formal for guardrail
In [ ]:
Copied!
```
def result_response(
    guardrail_type,
    activated,
    guard_output,
    is_valid,
    risk_score,
    threshold,
    response_text,
):
    """
    Standardizes the result format for all guardrail checks.
    """
    return {
        "guardrail_type": guardrail_type,
        "activated": activated,
        "guardrail_detail": {
            "guard_output": guard_output,
            "is_valid": is_valid,
            "risk_score/threshold": f"{risk_score}/{threshold}",
            "response_text": response_text,
        },
    }

```

def result_response( guardrail_type, activated, guard_output, is_valid, risk_score, threshold, response_text, ): """ Standardizes the result format for all guardrail checks. """ return { "guardrail_type": guardrail_type, "activated": activated, "guardrail_detail": { "guard_output": guard_output, "is_valid": is_valid, "risk_score/threshold": f"{risk_score}/{threshold}", "response_text": response_text, }, }
## Adding scanner for Guardrail.¶
Here you can visit "https://llm-guard.com" for discover the nessessary scanner. Below is 2 example scanners you should follow this format function. Here we use Gemini 1.5 Flash for the response of Scanner. Hence, you can choose your own LLMs such as ChatGPT, ...
In [ ]:
Copied!
```
from llm_guard.input_scanners import Toxicity
from llm_guard.input_scanners.toxicity import MatchType
from litellm import completion


def guardrail_toxicLanguage(prompt):
    # Interact with the LLM to generate a response
    print(f"Prompt: {prompt}")

    # Generate the response using the LLM (Gemini-1.5-flash)
    response = completion(
        model="gemini/gemini-1.5-flash",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    response_text = response.choices[0].message.content

    # Define the threshold and scan for toxicity
    threshold = 0.5
    toxic_scanner = Toxicity(threshold=threshold, match_type=MatchType.FULL)
    sanitized_output, is_valid, risk_score = toxic_scanner.scan(prompt)

    return result_response(
        guardrail_type="Toxicity",
        activated=not is_valid,
        guard_output=sanitized_output,
        is_valid=is_valid,
        risk_score=risk_score,
        threshold=threshold,
        response_text=response_text,
    )

```

from llm_guard.input_scanners import Toxicity from llm_guard.input_scanners.toxicity import MatchType from litellm import completion def guardrail_toxicLanguage(prompt): # Interact with the LLM to generate a response print(f"Prompt: {prompt}") # Generate the response using the LLM (Gemini-1.5-flash) response = completion( model="gemini/gemini-1.5-flash", messages=[ {"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}, ], ) response_text = response.choices[0].message.content # Define the threshold and scan for toxicity threshold = 0.5 toxic_scanner = Toxicity(threshold=threshold, match_type=MatchType.FULL) sanitized_output, is_valid, risk_score = toxic_scanner.scan(prompt) return result_response( guardrail_type="Toxicity", activated=not is_valid, guard_output=sanitized_output, is_valid=is_valid, risk_score=risk_score, threshold=threshold, response_text=response_text, )
```
huggingface/tokenizers: The current process just got forked, after parallelism has already been used. Disabling parallelism to avoid deadlocks...
To disable this warning, you can either:
	- Avoid using `tokenizers` before the fork if possible
	- Explicitly set the environment variable TOKENIZERS_PARALLELISM=(true | false)

```

In [ ]:
Copied!
```
from llm_guard.input_scanners import TokenLimit
from llm_guard import scan_output
from litellm import completion


def guardrail_tokenlimit(prompt):
    threshold = 400
    response = completion(
        model="gemini/gemini-1.5-flash",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )
    response_text = response.choices[0].message.content

    scanner = TokenLimit(limit=threshold, encoding_name="cl100k_base")
    sanitized_output, is_valid, risk_score = scanner.scan(prompt)

    # Use the global rail to format the result
    result = result_response(
        guardrail_type="Token limit",
        activated=not is_valid,
        guard_output=sanitized_output,
        is_valid=is_valid,
        risk_score=risk_score,
        threshold=threshold,
        response_text=response_text,
    )

    return result

```

from llm_guard.input_scanners import TokenLimit from llm_guard import scan_output from litellm import completion def guardrail_tokenlimit(prompt): threshold = 400 response = completion( model="gemini/gemini-1.5-flash", messages=[ {"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}, ], ) response_text = response.choices[0].message.content scanner = TokenLimit(limit=threshold, encoding_name="cl100k_base") sanitized_output, is_valid, risk_score = scanner.scan(prompt) # Use the global rail to format the result result = result_response( guardrail_type="Token limit", activated=not is_valid, guard_output=sanitized_output, is_valid=is_valid, risk_score=risk_score, threshold=threshold, response_text=response_text, ) return result
###  `InputScanner` - `OutputScanner` Function¶
The `InputScanner` function runs a series of scanners on a given input query and evaluates whether any of them detect a threat. It returns a boolean value indicating whether a threat was detected and a list of results from scanners that returned a positive detection.
#### Parameters:¶
  * `query` (_str_): The input to be scanned for potential threats.
  * `listOfScanners` (_list_): A list of scanner functions. Each scanner function should accept the query as input and return a dictionary with a key `"activated"` (boolean) to indicate whether a threat was detected.


#### Returns:¶
  * `detected` (_bool_): `True` if any scanner detects a threat, otherwise `False`.
  * `triggered_scanners` (_list_): A list of dictionaries returned by the scanners that detected a threat.


#### Key Steps:¶
  1. Initialize `detected` to `False` to track if any scanner finds a threat.
  2. Create an empty list `triggered_scanners` to store results from scanners that detect a threat.
  3. Iterate over each scanner in `listOfScanners`:
     * Run the scanner on the `query`.
     * Check if the scanner's result includes `"activated": True`.
     * If a threat is detected:
       * Set `detected` to `True`.
       * Append the scanner's result to `triggered_scanners`.
  4. Return the `detected` status and the list of `triggered_scanners`.


In [ ]:
Copied!
```
def InputScanner(query, listOfScanners):
    """
    Runs all scanners on the query and returns:
    - True if any scanner detects a threat.
    - A list of results from scanners that returned True.
    """
    detected = False  # Track if any scanner detects a threat
    triggered_scanners = []  # Store results from triggered scanners

    # Run each scanner on the query
    for scanner in listOfScanners:
        result = scanner(query)

        if result[
            "activated"
        ]:  # Check if the scanner found a threat (activated=True)
            detected = True  # Set detected to True if any scanner triggers
            triggered_scanners.append(result)  # Track which scanner triggered

    return detected, triggered_scanners

```

def InputScanner(query, listOfScanners): """ Runs all scanners on the query and returns: - True if any scanner detects a threat. - A list of results from scanners that returned True. """ detected = False # Track if any scanner detects a threat triggered_scanners = [] # Store results from triggered scanners # Run each scanner on the query for scanner in listOfScanners: result = scanner(query) if result[ "activated" ]: # Check if the scanner found a threat (activated=True) detected = True # Set detected to True if any scanner triggers triggered_scanners.append(result) # Track which scanner triggered return detected, triggered_scanners
In [ ]:
Copied!
```
def OutputScanner(response, query, context, listOfScanners):
    """
    Runs all scanners on the response and returns:
    - True if any scanner detects a threat.
    - A list of results from scanners that returned True.
    """
    detected = False  # Track if any scanner detects a threat
    triggered_scanners = []  # Store results from triggered scanners

    # Run each scanner on the response
    for scanner in listOfScanners:
        # Check if scanner is `evaluate_rag_response` (which needs query & context)
        if scanner.__name__ == "evaluate_rag_response":
            result = scanner(
                response, query, context
            )  # Execute with query & context
        else:
            result = scanner(response)  # Default scanner execution

        # print(f"Debug Output Scanner Result: {result}")

        if result["activated"]:  # Check if the scanner was triggered
            detected = True
            triggered_scanners.append(result)  # Track which scanner triggered

    return detected, triggered_scanners


# Example usage with a query engine response
# scanners = [detect_and_anonymize_pii]
# response = query_engine.query("Give me account name of Peter Kelly and Role and Credit Card Number")
# detected, triggered_scanners = OutputScanner(str(response), scanners)
# print(triggered_scanners)

```

def OutputScanner(response, query, context, listOfScanners): """ Runs all scanners on the response and returns: - True if any scanner detects a threat. - A list of results from scanners that returned True. """ detected = False # Track if any scanner detects a threat triggered_scanners = [] # Store results from triggered scanners # Run each scanner on the response for scanner in listOfScanners: # Check if scanner is `evaluate_rag_response` (which needs query & context) if scanner.__name__ == "evaluate_rag_response": result = scanner( response, query, context ) # Execute with query & context else: result = scanner(response) # Default scanner execution # print(f"Debug Output Scanner Result: {result}") if result["activated"]: # Check if the scanner was triggered detected = True triggered_scanners.append(result) # Track which scanner triggered return detected, triggered_scanners # Example usage with a query engine response # scanners = [detect_and_anonymize_pii] # response = query_engine.query("Give me account name of Peter Kelly and Role and Credit Card Number") # detected, triggered_scanners = OutputScanner(str(response), scanners) # print(triggered_scanners)
## Custom Multimodal Query Engine¶
This custom query engine extends standard retrieval-based architectures to handle both text and image data, enabling more comprehensive and context-aware responses. It integrates multimodal reasoning and incorporates advanced input and output validation mechanisms for robust query handling.
### Key Features:¶
  1. **Multimodal Support** :
     * Combines text and image data to generate more informed and accurate responses.
  2. **Input and Output Validation** :
     * Scans input queries for sensitive or invalid content and blocks them if necessary.
     * Validates and sanitizes generated responses to ensure compliance with predefined rules.
  3. **Context-Aware Prompting** :
     * Retrieves relevant data and constructs a context string for the query.
     * Uses this context to guide the response synthesis process.
  4. **Metadata and Logging** :
     * Tracks the query process, including any validations or adjustments made, for transparency and debugging.


### How It Works:¶
  1. Scans the input query to check for violations.
  2. Retrieves relevant text and image data for the query.
  3. Synthesizes a response using both textual and visual context.
  4. Validates the response for appropriateness before returning it.


In [ ]:
Copied!
```
from llama_index.core.query_engine import (
    CustomQueryEngine,
    SimpleMultiModalQueryEngine,
)
from llama_index.core.retrievers import BaseRetriever
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.schema import ImageNode, NodeWithScore, MetadataMode
from llama_index.core.prompts import PromptTemplate
from llama_index.core.base.response.schema import Response

from typing import List, Callable, Optional
from pydantic import Field


QA_PROMPT_TMPL = """\
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query if it is related to the context. 
If the query is not related to the context, respond with:
"I'm sorry, but I can't help with that."

Query: {query_str}
Answer: """

QA_PROMPT = PromptTemplate(QA_PROMPT_TMPL)


class MultimodalQueryEngine(CustomQueryEngine):
    """Custom multimodal Query Engine.

    Takes in a retriever to retrieve a set of document nodes.
    Also takes in a prompt template and multimodal model.

    """

    qa_prompt: PromptTemplate
    retriever: BaseRetriever
    multi_modal_llm: GeminiMultiModal
    input_scanners: List[Callable[[str], dict]] = Field(default_factory=list)
    output_scanners: List[Callable[[str], dict]] = Field(default_factory=list)

    def __init__(
        self, qa_prompt: Optional[PromptTemplate] = None, **kwargs
    ) -> None:
        """Initialize."""
        super().__init__(qa_prompt=qa_prompt or QA_PROMPT, **kwargs)

    def custom_query(self, query_str: str):
        query_metadata = {
            "input_scanners": [],
            "output_scanners": [],
            "retrieved_nodes": [],
            "response_status": "success",
        }

        input_detected, input_triggered = InputScanner(
            query_str, self.input_scanners
        )
        if input_triggered:
            # print("Triggered Input Scanners:", input_triggered)
            # Log triggered input scanners in metadata
            query_metadata["input_scanners"] = input_triggered
            # If input contains sensitive information, block the query
            if input_detected:
                return Response(
                    response="I'm sorry, but I can't help with that.",
                    source_nodes=[],
                    metadata={
                        "guardrail": "Input Scanner",
                        "triggered_scanners": input_triggered,
                        "response_status": "blocked",
                    },
                )

        # retrieve text nodes
        nodes = self.retriever.retrieve(query_str)
        # create ImageNode items from text nodes
        image_nodes = [
            NodeWithScore(node=ImageNode(image_path=n.metadata["image_path"]))
            for n in nodes
        ]

        # create context string from text nodes, dump into the prompt
        context_str = "\n\n".join(
            [r.get_content(metadata_mode=MetadataMode.LLM) for r in nodes]
        )
        fmt_prompt = self.qa_prompt.format(
            context_str=context_str, query_str=query_str
        )

        # synthesize an answer from formatted text and images
        llm_response = self.multi_modal_llm.complete(
            prompt=fmt_prompt,
            image_documents=[image_node.node for image_node in image_nodes],
        )

        # Step 5: Run Output Scanners
        output_detected, output_triggered = OutputScanner(
            str(llm_response),
            str(query_str),
            str(context_str),
            self.output_scanners,
        )
        if output_triggered:
            # print("Triggered Output Scanners:", output_triggered)
            query_metadata[
                "output_scanners"
            ] = output_triggered  # Store output scanner info

        final_response = str(llm_response)
        if output_detected:
            final_response = "I'm sorry, but I can't help with that."
            query_metadata["response_status"] = "sanitized"
        # Return the response with detailed metadata
        return Response(
            response=final_response,
            source_nodes=nodes,
            metadata=query_metadata,
        )

```

from llama_index.core.query_engine import ( CustomQueryEngine, SimpleMultiModalQueryEngine, ) from llama_index.core.retrievers import BaseRetriever from llama_index.multi_modal_llms.openai import OpenAIMultiModal from llama_index.core.schema import ImageNode, NodeWithScore, MetadataMode from llama_index.core.prompts import PromptTemplate from llama_index.core.base.response.schema import Response from typing import List, Callable, Optional from pydantic import Field QA_PROMPT_TMPL = """\ --------------------- {context_str} --------------------- Given the context information and not prior knowledge, answer the query if it is related to the context. If the query is not related to the context, respond with: "I'm sorry, but I can't help with that." Query: {query_str} Answer: """ QA_PROMPT = PromptTemplate(QA_PROMPT_TMPL) class MultimodalQueryEngine(CustomQueryEngine): """Custom multimodal Query Engine. Takes in a retriever to retrieve a set of document nodes. Also takes in a prompt template and multimodal model. """ qa_prompt: PromptTemplate retriever: BaseRetriever multi_modal_llm: GeminiMultiModal input_scanners: List[Callable[[str], dict]] = Field(default_factory=list) output_scanners: List[Callable[[str], dict]] = Field(default_factory=list) def __init__( self, qa_prompt: Optional[PromptTemplate] = None, **kwargs ) -> None: """Initialize.""" super().__init__(qa_prompt=qa_prompt or QA_PROMPT, **kwargs) def custom_query(self, query_str: str): query_metadata = { "input_scanners": [], "output_scanners": [], "retrieved_nodes": [], "response_status": "success", } input_detected, input_triggered = InputScanner( query_str, self.input_scanners ) if input_triggered: # print("Triggered Input Scanners:", input_triggered) # Log triggered input scanners in metadata query_metadata["input_scanners"] = input_triggered # If input contains sensitive information, block the query if input_detected: return Response( response="I'm sorry, but I can't help with that.", source_nodes=[], metadata={ "guardrail": "Input Scanner", "triggered_scanners": input_triggered, "response_status": "blocked", }, ) # retrieve text nodes nodes = self.retriever.retrieve(query_str) # create ImageNode items from text nodes image_nodes = [ NodeWithScore(node=ImageNode(image_path=n.metadata["image_path"])) for n in nodes ] # create context string from text nodes, dump into the prompt context_str = "\n\n".join( [r.get_content(metadata_mode=MetadataMode.LLM) for r in nodes] ) fmt_prompt = self.qa_prompt.format( context_str=context_str, query_str=query_str ) # synthesize an answer from formatted text and images llm_response = self.multi_modal_llm.complete( prompt=fmt_prompt, image_documents=[image_node.node for image_node in image_nodes], ) # Step 5: Run Output Scanners output_detected, output_triggered = OutputScanner( str(llm_response), str(query_str), str(context_str), self.output_scanners, ) if output_triggered: # print("Triggered Output Scanners:", output_triggered) query_metadata[ "output_scanners" ] = output_triggered # Store output scanner info final_response = str(llm_response) if output_detected: final_response = "I'm sorry, but I can't help with that." query_metadata["response_status"] = "sanitized" # Return the response with detailed metadata return Response( response=final_response, source_nodes=nodes, metadata=query_metadata, )
### Input and Output Scanners Configuration¶
You can put the scanner which you need to guard your RAG
In [ ]:
Copied!
```
input_scanners = [guardrail_toxicLanguage, guardrail_tokenlimit]
output_scanners = [guardrail_toxicLanguage]

```

input_scanners = [guardrail_toxicLanguage, guardrail_tokenlimit] output_scanners = [guardrail_toxicLanguage]
In [ ]:
Copied!
```
query_engine = MultimodalQueryEngine(
    retriever=index.as_retriever(similarity_top_k=9),
    multi_modal_llm=gemini_multimodal,
    input_scanners=input_scanners,
    output_scanners=output_scanners,
)

```

query_engine = MultimodalQueryEngine( retriever=index.as_retriever(similarity_top_k=9), multi_modal_llm=gemini_multimodal, input_scanners=input_scanners, output_scanners=output_scanners, )
## Try out Queries¶
Let's try out queries.
In [ ]:
Copied!
```
query = "Tell me about the diverse geographies where Conoco Phillips has a production base"
response = query_engine.query(query)

```

query = "Tell me about the diverse geographies where Conoco Phillips has a production base" response = query_engine.query(query)
```
Prompt: Tell me about the diverse geographies where Conoco Phillips has a production base
2024-12-03 17:43:08 [debug    ] Initialized classification model device=device(type='mps') model=Model(path='unitary/unbiased-toxic-roberta', subfolder='', revision='36295dd80b422dc49f40052021430dae76241adc', onnx_path='ProtectAI/unbiased-toxic-roberta-onnx', onnx_revision='34480fa958f6657ad835c345808475755b6974a7', onnx_subfolder='', onnx_filename='model.onnx', kwargs={}, pipeline_kwargs={'batch_size': 1, 'device': device(type='mps'), 'padding': 'max_length', 'top_k': None, 'function_to_apply': 'sigmoid', 'return_token_type_ids': False, 'max_length': 512, 'truncation': True}, tokenizer_kwargs={})
2024-12-03 17:43:09 [debug    ] Not toxicity found in the text results=[[{'label': 'toxicity', 'score': 0.00041448281263001263}, {'label': 'male', 'score': 0.00018738119979389012}, {'label': 'insult', 'score': 0.00011956175148952752}, {'label': 'female', 'score': 0.00011725842341547832}, {'label': 'psychiatric_or_mental_illness', 'score': 8.512590284226462e-05}, {'label': 'white', 'score': 7.451862620655447e-05}, {'label': 'christian', 'score': 5.6545581173850223e-05}, {'label': 'muslim', 'score': 5.644273551297374e-05}, {'label': 'black', 'score': 3.8606172893196344e-05}, {'label': 'obscene', 'score': 3.222753730369732e-05}, {'label': 'identity_attack', 'score': 3.1757666874909773e-05}, {'label': 'threat', 'score': 2.8462023692554794e-05}, {'label': 'jewish', 'score': 2.7872381906490773e-05}, {'label': 'homosexual_gay_or_lesbian', 'score': 2.5694836949696764e-05}, {'label': 'sexual_explicit', 'score': 1.859129588410724e-05}, {'label': 'severe_toxicity', 'score': 1.0931341876130318e-06}]]
2024-12-03 17:43:15 [debug    ] Prompt fits the maximum tokens num_tokens=15 threshold=400
Prompt: ConocoPhillips has a diverse production base across several geographic locations.  These include:

* **Alaska:**  The company has a significant presence in Alaska's conventional basins, including the Prudhoe Bay area, with a long history of production and existing infrastructure.  The Willow project is also located in Alaska.
* **Lower 48 (United States):**  ConocoPhillips operates extensively in the Lower 48 states, focusing on unconventional plays in the Permian Basin (Delaware and Midland Basins), Eagle Ford, and Bakken.
* **International:** The company has operations in other international locations, including Qatar (LNG), and previously had operations in the UK, Australia, Indonesia, and Canada (though some of these have been divested).  They also have a global marketing presence with offices in London, Singapore, Houston, Calgary, Beijing, and Tokyo.
2024-12-03 17:43:36 [debug    ] Initialized classification model device=device(type='mps') model=Model(path='unitary/unbiased-toxic-roberta', subfolder='', revision='36295dd80b422dc49f40052021430dae76241adc', onnx_path='ProtectAI/unbiased-toxic-roberta-onnx', onnx_revision='34480fa958f6657ad835c345808475755b6974a7', onnx_subfolder='', onnx_filename='model.onnx', kwargs={}, pipeline_kwargs={'batch_size': 1, 'device': device(type='mps'), 'padding': 'max_length', 'top_k': None, 'function_to_apply': 'sigmoid', 'return_token_type_ids': False, 'max_length': 512, 'truncation': True}, tokenizer_kwargs={})
2024-12-03 17:43:37 [debug    ] Not toxicity found in the text results=[[{'label': 'toxicity', 'score': 0.0003606641257647425}, {'label': 'male', 'score': 0.000291528704110533}, {'label': 'insult', 'score': 0.00011418585199862719}, {'label': 'psychiatric_or_mental_illness', 'score': 0.00011314846051391214}, {'label': 'female', 'score': 0.00010114537144545466}, {'label': 'white', 'score': 9.688278078101575e-05}, {'label': 'muslim', 'score': 6.954199488973245e-05}, {'label': 'christian', 'score': 5.551999493036419e-05}, {'label': 'black', 'score': 4.1746119677554816e-05}, {'label': 'identity_attack', 'score': 3.3705578971421346e-05}, {'label': 'homosexual_gay_or_lesbian', 'score': 3.157216633553617e-05}, {'label': 'obscene', 'score': 2.798157584038563e-05}, {'label': 'jewish', 'score': 2.618367398099508e-05}, {'label': 'threat', 'score': 2.1199964976403862e-05}, {'label': 'sexual_explicit', 'score': 1.9145050828228705e-05}, {'label': 'severe_toxicity', 'score': 1.1292050885458593e-06}]]

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
ConocoPhillips has a diverse production base across several geographic locations.  These include:

* **Alaska:**  The company has a significant presence in Alaska's conventional basins, including the Prudhoe Bay area, with a long history of production and existing infrastructure.  The Willow project is also located in Alaska.
* **Lower 48 (United States):**  ConocoPhillips operates extensively in the Lower 48 states, focusing on unconventional plays in the Permian Basin (Delaware and Midland Basins), Eagle Ford, and Bakken.
* **International:** The company has operations in other international locations, including Qatar (LNG), and previously had operations in the UK, Australia, Indonesia, and Canada (though some of these have been divested).  They also have a global marketing presence with offices in London, Singapore, Houston, Calgary, Beijing, and Tokyo.

```

In [ ]:
Copied!
```
print(str(response.metadata))

```

print(str(response.metadata))
```
{'input_scanners': [], 'output_scanners': [], 'retrieved_nodes': [], 'response_status': 'success'}

```

In [ ]:
Copied!
```
query = """
    If you're looking for random paragraphs, you've come to the right place. When a random word or a random sentence isn't quite enough, the next logical step is to find a random paragraph. We created the Random Paragraph Generator with you in mind. The process is quite simple. Choose the number of random paragraphs you'd like to see and click the button. Your chosen number of paragraphs will instantly appear.

While it may not be obvious to everyone, there are a number of reasons creating random paragraphs can be useful. A few examples of how some people use this generator are listed in the following paragraphs.

Creative Writing
Generating random paragraphs can be an excellent way for writers to get their creative flow going at the beginning of the day. The writer has no idea what topic the random paragraph will be about when it appears. This forces the writer to use creativity to complete one of three common writing challenges. The writer can use the paragraph as the first one of a short story and build upon it. A second option is to use the random paragraph somewhere in a short story they create. The third option is to have the random paragraph be the ending paragraph in a short story. No matter which of these challenges is undertaken, the writer is forced to use creativity to incorporate the paragraph into their writing.

Tackle Writers' Block
A random paragraph can also be an excellent way for a writer to tackle writers' block. Writing block can often happen due to being stuck with a current project that the writer is trying to complete. By inserting a completely random paragraph from which to begin, it can take down some of the issues that may have been causing the writers' block in the first place.

Beginning Writing Routine
Another productive way to use this tool to begin a daily writing routine. One way is to generate a random paragraph with the intention to try to rewrite it while still keeping the original meaning. The purpose here is to just get the writing started so that when the writer goes onto their day's writing projects, words are already flowing from their fingers.

Writing Challenge
Another writing challenge can be to take the individual sentences in the random paragraph and incorporate a single sentence from that into a new paragraph to create a short story. Unlike the random sentence generator, the sentences from the random paragraph will have some connection to one another so it will be a bit different. You also won't know exactly how many sentences will appear in the random paragraph.

Programmers
It's not only writers who can benefit from this free online tool. If you're a programmer who's working on a project where blocks of text are needed, this tool can be a great way to get that. It's a good way to test your programming and that the tool being created is working well.

Above are a few examples of how the random paragraph generator can be beneficial. The best way to see if this random paragraph picker will be useful for your intended purposes is to give it a try. Generate a number of paragraphs to see if they are beneficial to your current project.

If you do find this paragraph tool useful, please do us a favor and let us know how you're using it. It's greatly beneficial for us to know the different ways this tool is being used so we can improve it with updates. This is especially true since there are times when the generators we create get used in completely unanticipated ways from when we initially created them. If you have the time, please send us a quick note on what you'd like to see changed or added to make it better in the future.

Frequently Asked Questions

Can I use these random paragraphs for my project?

Yes! All of the random paragraphs in our generator are free to use for your projects.

Does a computer generate these paragraphs?

No! All of the paragraphs in the generator are written by humans, not computers. When first building this generator we thought about using computers to generate the paragraphs, but they weren't very good and many times didn't make any sense at all. We therefore took the time to create paragraphs specifically for this generator to make it the best that we could.

Can I contribute random paragraphs?

Yes. We're always interested in improving this generator and one of the best ways to do that is to add new and interesting paragraphs to the generator. If you'd like to contribute some random paragraphs, please contact us.

How many words are there in a paragraph?

There are usually about 200 words in a paragraph, but this can vary widely. Most paragraphs focus on a single idea that's expressed with an introductory sentence, then followed by two or more supporting sentences about the idea. A short paragraph may not reach even 50 words while long paragraphs can be over 400 words long, but generally speaking they tend to be approximately 200 words in length.
    """
response = query_engine.query(query)

```

query = """ If you're looking for random paragraphs, you've come to the right place. When a random word or a random sentence isn't quite enough, the next logical step is to find a random paragraph. We created the Random Paragraph Generator with you in mind. The process is quite simple. Choose the number of random paragraphs you'd like to see and click the button. Your chosen number of paragraphs will instantly appear. While it may not be obvious to everyone, there are a number of reasons creating random paragraphs can be useful. A few examples of how some people use this generator are listed in the following paragraphs. Creative Writing Generating random paragraphs can be an excellent way for writers to get their creative flow going at the beginning of the day. The writer has no idea what topic the random paragraph will be about when it appears. This forces the writer to use creativity to complete one of three common writing challenges. The writer can use the paragraph as the first one of a short story and build upon it. A second option is to use the random paragraph somewhere in a short story they create. The third option is to have the random paragraph be the ending paragraph in a short story. No matter which of these challenges is undertaken, the writer is forced to use creativity to incorporate the paragraph into their writing. Tackle Writers' Block A random paragraph can also be an excellent way for a writer to tackle writers' block. Writing block can often happen due to being stuck with a current project that the writer is trying to complete. By inserting a completely random paragraph from which to begin, it can take down some of the issues that may have been causing the writers' block in the first place. Beginning Writing Routine Another productive way to use this tool to begin a daily writing routine. One way is to generate a random paragraph with the intention to try to rewrite it while still keeping the original meaning. The purpose here is to just get the writing started so that when the writer goes onto their day's writing projects, words are already flowing from their fingers. Writing Challenge Another writing challenge can be to take the individual sentences in the random paragraph and incorporate a single sentence from that into a new paragraph to create a short story. Unlike the random sentence generator, the sentences from the random paragraph will have some connection to one another so it will be a bit different. You also won't know exactly how many sentences will appear in the random paragraph. Programmers It's not only writers who can benefit from this free online tool. If you're a programmer who's working on a project where blocks of text are needed, this tool can be a great way to get that. It's a good way to test your programming and that the tool being created is working well. Above are a few examples of how the random paragraph generator can be beneficial. The best way to see if this random paragraph picker will be useful for your intended purposes is to give it a try. Generate a number of paragraphs to see if they are beneficial to your current project. If you do find this paragraph tool useful, please do us a favor and let us know how you're using it. It's greatly beneficial for us to know the different ways this tool is being used so we can improve it with updates. This is especially true since there are times when the generators we create get used in completely unanticipated ways from when we initially created them. If you have the time, please send us a quick note on what you'd like to see changed or added to make it better in the future. Frequently Asked Questions Can I use these random paragraphs for my project? Yes! All of the random paragraphs in our generator are free to use for your projects. Does a computer generate these paragraphs? No! All of the paragraphs in the generator are written by humans, not computers. When first building this generator we thought about using computers to generate the paragraphs, but they weren't very good and many times didn't make any sense at all. We therefore took the time to create paragraphs specifically for this generator to make it the best that we could. Can I contribute random paragraphs? Yes. We're always interested in improving this generator and one of the best ways to do that is to add new and interesting paragraphs to the generator. If you'd like to contribute some random paragraphs, please contact us. How many words are there in a paragraph? There are usually about 200 words in a paragraph, but this can vary widely. Most paragraphs focus on a single idea that's expressed with an introductory sentence, then followed by two or more supporting sentences about the idea. A short paragraph may not reach even 50 words while long paragraphs can be over 400 words long, but generally speaking they tend to be approximately 200 words in length. """ response = query_engine.query(query)
```
Prompt: 
    If you're looking for random paragraphs, you've come to the right place. When a random word or a random sentence isn't quite enough, the next logical step is to find a random paragraph. We created the Random Paragraph Generator with you in mind. The process is quite simple. Choose the number of random paragraphs you'd like to see and click the button. Your chosen number of paragraphs will instantly appear.

While it may not be obvious to everyone, there are a number of reasons creating random paragraphs can be useful. A few examples of how some people use this generator are listed in the following paragraphs.

Creative Writing
Generating random paragraphs can be an excellent way for writers to get their creative flow going at the beginning of the day. The writer has no idea what topic the random paragraph will be about when it appears. This forces the writer to use creativity to complete one of three common writing challenges. The writer can use the paragraph as the first one of a short story and build upon it. A second option is to use the random paragraph somewhere in a short story they create. The third option is to have the random paragraph be the ending paragraph in a short story. No matter which of these challenges is undertaken, the writer is forced to use creativity to incorporate the paragraph into their writing.

Tackle Writers' Block
A random paragraph can also be an excellent way for a writer to tackle writers' block. Writing block can often happen due to being stuck with a current project that the writer is trying to complete. By inserting a completely random paragraph from which to begin, it can take down some of the issues that may have been causing the writers' block in the first place.

Beginning Writing Routine
Another productive way to use this tool to begin a daily writing routine. One way is to generate a random paragraph with the intention to try to rewrite it while still keeping the original meaning. The purpose here is to just get the writing started so that when the writer goes onto their day's writing projects, words are already flowing from their fingers.

Writing Challenge
Another writing challenge can be to take the individual sentences in the random paragraph and incorporate a single sentence from that into a new paragraph to create a short story. Unlike the random sentence generator, the sentences from the random paragraph will have some connection to one another so it will be a bit different. You also won't know exactly how many sentences will appear in the random paragraph.

Programmers
It's not only writers who can benefit from this free online tool. If you're a programmer who's working on a project where blocks of text are needed, this tool can be a great way to get that. It's a good way to test your programming and that the tool being created is working well.

Above are a few examples of how the random paragraph generator can be beneficial. The best way to see if this random paragraph picker will be useful for your intended purposes is to give it a try. Generate a number of paragraphs to see if they are beneficial to your current project.

If you do find this paragraph tool useful, please do us a favor and let us know how you're using it. It's greatly beneficial for us to know the different ways this tool is being used so we can improve it with updates. This is especially true since there are times when the generators we create get used in completely unanticipated ways from when we initially created them. If you have the time, please send us a quick note on what you'd like to see changed or added to make it better in the future.

Frequently Asked Questions

Can I use these random paragraphs for my project?

Yes! All of the random paragraphs in our generator are free to use for your projects.

Does a computer generate these paragraphs?

No! All of the paragraphs in the generator are written by humans, not computers. When first building this generator we thought about using computers to generate the paragraphs, but they weren't very good and many times didn't make any sense at all. We therefore took the time to create paragraphs specifically for this generator to make it the best that we could.

Can I contribute random paragraphs?

Yes. We're always interested in improving this generator and one of the best ways to do that is to add new and interesting paragraphs to the generator. If you'd like to contribute some random paragraphs, please contact us.

How many words are there in a paragraph?

There are usually about 200 words in a paragraph, but this can vary widely. Most paragraphs focus on a single idea that's expressed with an introductory sentence, then followed by two or more supporting sentences about the idea. A short paragraph may not reach even 50 words while long paragraphs can be over 400 words long, but generally speaking they tend to be approximately 200 words in length.
    
2024-12-03 17:43:42 [debug    ] Initialized classification model device=device(type='mps') model=Model(path='unitary/unbiased-toxic-roberta', subfolder='', revision='36295dd80b422dc49f40052021430dae76241adc', onnx_path='ProtectAI/unbiased-toxic-roberta-onnx', onnx_revision='34480fa958f6657ad835c345808475755b6974a7', onnx_subfolder='', onnx_filename='model.onnx', kwargs={}, pipeline_kwargs={'batch_size': 1, 'device': device(type='mps'), 'padding': 'max_length', 'top_k': None, 'function_to_apply': 'sigmoid', 'return_token_type_ids': False, 'max_length': 512, 'truncation': True}, tokenizer_kwargs={})
2024-12-03 17:43:42 [debug    ] Not toxicity found in the text results=[[{'label': 'toxicity', 'score': 0.0011976422974839807}, {'label': 'insult', 'score': 0.00045695927110500634}, {'label': 'male', 'score': 0.00018701529188547283}, {'label': 'psychiatric_or_mental_illness', 'score': 0.00014795312017668039}, {'label': 'white', 'score': 9.39662495511584e-05}, {'label': 'female', 'score': 7.459904009010643e-05}, {'label': 'obscene', 'score': 6.114380084909499e-05}, {'label': 'threat', 'score': 5.259696990833618e-05}, {'label': 'muslim', 'score': 4.745226033264771e-05}, {'label': 'identity_attack', 'score': 3.541662226780318e-05}, {'label': 'black', 'score': 3.5083121474599466e-05}, {'label': 'christian', 'score': 3.272023604949936e-05}, {'label': 'sexual_explicit', 'score': 3.164245936204679e-05}, {'label': 'jewish', 'score': 1.5377421732409857e-05}, {'label': 'homosexual_gay_or_lesbian', 'score': 1.5361225450760685e-05}, {'label': 'severe_toxicity', 'score': 1.3027844261159771e-06}]]
2024-12-03 17:43:46 [warning  ] Prompt is too big. Splitting into chunks chunks=["\n    If you're looking for random paragraphs, you've come to the right place. When a random word or a random sentence isn't quite enough, the next logical step is to find a random paragraph. We created the Random Paragraph Generator with you in mind. The process is quite simple. Choose the number of random paragraphs you'd like to see and click the button. Your chosen number of paragraphs will instantly appear.\n\nWhile it may not be obvious to everyone, there are a number of reasons creating random paragraphs can be useful. A few examples of how some people use this generator are listed in the following paragraphs.\n\nCreative Writing\nGenerating random paragraphs can be an excellent way for writers to get their creative flow going at the beginning of the day. The writer has no idea what topic the random paragraph will be about when it appears. This forces the writer to use creativity to complete one of three common writing challenges. The writer can use the paragraph as the first one of a short story and build upon it. A second option is to use the random paragraph somewhere in a short story they create. The third option is to have the random paragraph be the ending paragraph in a short story. No matter which of these challenges is undertaken, the writer is forced to use creativity to incorporate the paragraph into their writing.\n\nTackle Writers' Block\nA random paragraph can also be an excellent way for a writer to tackle writers' block. Writing block can often happen due to being stuck with a current project that the writer is trying to complete. By inserting a completely random paragraph from which to begin, it can take down some of the issues that may have been causing the writers' block in the first place.\n\nBeginning Writing Routine\nAnother productive way to use this tool to begin a daily writing routine. One way is to generate a random paragraph with the intention to try to rewrite it while still keeping the original meaning. The purpose here is to just get the writing started so that when the writer goes onto their day's writing", " projects, words are already flowing from their fingers.\n\nWriting Challenge\nAnother writing challenge can be to take the individual sentences in the random paragraph and incorporate a single sentence from that into a new paragraph to create a short story. Unlike the random sentence generator, the sentences from the random paragraph will have some connection to one another so it will be a bit different. You also won't know exactly how many sentences will appear in the random paragraph.\n\nProgrammers\nIt's not only writers who can benefit from this free online tool. If you're a programmer who's working on a project where blocks of text are needed, this tool can be a great way to get that. It's a good way to test your programming and that the tool being created is working well.\n\nAbove are a few examples of how the random paragraph generator can be beneficial. The best way to see if this random paragraph picker will be useful for your intended purposes is to give it a try. Generate a number of paragraphs to see if they are beneficial to your current project.\n\nIf you do find this paragraph tool useful, please do us a favor and let us know how you're using it. It's greatly beneficial for us to know the different ways this tool is being used so we can improve it with updates. This is especially true since there are times when the generators we create get used in completely unanticipated ways from when we initially created them. If you have the time, please send us a quick note on what you'd like to see changed or added to make it better in the future.\n\nFrequently Asked Questions\n\nCan I use these random paragraphs for my project?\n\nYes! All of the random paragraphs in our generator are free to use for your projects.\n\nDoes a computer generate these paragraphs?\n\nNo! All of the paragraphs in the generator are written by humans, not computers. When first building this generator we thought about using computers to generate the paragraphs, but they weren't very good and many times didn't make any sense at all", ". We therefore took the time to create paragraphs specifically for this generator to make it the best that we could.\n\nCan I contribute random paragraphs?\n\nYes. We're always interested in improving this generator and one of the best ways to do that is to add new and interesting paragraphs to the generator. If you'd like to contribute some random paragraphs, please contact us.\n\nHow many words are there in a paragraph?\n\nThere are usually about 200 words in a paragraph, but this can vary widely. Most paragraphs focus on a single idea that's expressed with an introductory sentence, then followed by two or more supporting sentences about the idea. A short paragraph may not reach even 50 words while long paragraphs can be over 400 words long, but generally speaking they tend to be approximately 200 words in length.\n    "] num_tokens=961

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
I'm sorry, but I can't help with that.

```

In [ ]:
Copied!
```
print(str(response.metadata))

```

print(str(response.metadata))
```
{'guardrail': 'Input Scanner', 'triggered_scanners': [{'guardrail_type': 'Token limit', 'activated': True, 'guardrail_detail': {'guard_output': "\n    If you're looking for random paragraphs, you've come to the right place. When a random word or a random sentence isn't quite enough, the next logical step is to find a random paragraph. We created the Random Paragraph Generator with you in mind. The process is quite simple. Choose the number of random paragraphs you'd like to see and click the button. Your chosen number of paragraphs will instantly appear.\n\nWhile it may not be obvious to everyone, there are a number of reasons creating random paragraphs can be useful. A few examples of how some people use this generator are listed in the following paragraphs.\n\nCreative Writing\nGenerating random paragraphs can be an excellent way for writers to get their creative flow going at the beginning of the day. The writer has no idea what topic the random paragraph will be about when it appears. This forces the writer to use creativity to complete one of three common writing challenges. The writer can use the paragraph as the first one of a short story and build upon it. A second option is to use the random paragraph somewhere in a short story they create. The third option is to have the random paragraph be the ending paragraph in a short story. No matter which of these challenges is undertaken, the writer is forced to use creativity to incorporate the paragraph into their writing.\n\nTackle Writers' Block\nA random paragraph can also be an excellent way for a writer to tackle writers' block. Writing block can often happen due to being stuck with a current project that the writer is trying to complete. By inserting a completely random paragraph from which to begin, it can take down some of the issues that may have been causing the writers' block in the first place.\n\nBeginning Writing Routine\nAnother productive way to use this tool to begin a daily writing routine. One way is to generate a random paragraph with the intention to try to rewrite it while still keeping the original meaning. The purpose here is to just get the writing started so that when the writer goes onto their day's writing", 'is_valid': False, 'risk_score/threshold': '1.0/400', 'response_text': "This text describes a random paragraph generator and its various uses.  Here's a summary broken down by section:\n\n**Introduction:** The text introduces a random paragraph generator, highlighting its simplicity and ease of use.\n\n**Uses of the Generator:**  The core of the text details how the generator can be beneficial in several contexts:\n\n* **Creative Writing:**  It aids writers in overcoming writer's block, sparking creativity, and providing starting points or endings for short stories.  Three specific challenges are suggested: using the paragraph as the beginning, middle, or end of a story.\n\n* **Tackling Writer's Block:** The random paragraph acts as a disruption to overcome creative stagnation.\n\n* **Beginning a Writing Routine:** It helps initiate the writing process by providing a text to rewrite or use as inspiration.\n\n* **Writing Challenges:** The paragraph's sentences can be individually incorporated into new writing projects.\n\n* **Programmers:** The generator provides useful blocks of text for testing purposes in software development.\n\n\n**Call to Action & Feedback:** The authors encourage users to try the generator, provide feedback, and contribute to its improvement by suggesting additions or changes.\n\n**Frequently Asked Questions (FAQ):**  The FAQ section addresses common questions about the generator, clarifying:\n\n* **Usage rights:**  The paragraphs are free to use.\n* **Paragraph generation:**  Human-written paragraphs are used, not computer-generated ones.\n* **Contribution:** Users can contribute their own paragraphs.\n* **Paragraph length:** Paragraphs are roughly 200 words but can vary significantly.\n\n\nIn essence, the text is a well-structured promotional piece for a random paragraph generator, emphasizing its versatility and usefulness for both writers and programmers, while encouraging user engagement and participation.\n"}}], 'response_status': 'blocked'}

```

