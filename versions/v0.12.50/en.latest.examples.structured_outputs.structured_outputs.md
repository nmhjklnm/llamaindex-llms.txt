# Examples of Structured Data Extraction in LlamaIndex¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
If you haven't yet read our structured data extraction tutorial, we recommend starting there. This notebook demonstrates some of the techniques introduced in the tutorial.
We start with the simple syntax around LLMs, then move on to how to use it with higher-level modules like a query engine and agent.
A lot of the underlying behavior around structured outputs is powered by our Pydantic Program modules. Check out our in-depth structured outputs guide for more details.
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

llm = OpenAI(model="gpt-4o")
embed_model = OpenAIEmbedding(model="text-embedding-3-small")
Settings.llm = llm
Settings.embed_model = embed_model

```

from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import Settings llm = OpenAI(model="gpt-4o") embed_model = OpenAIEmbedding(model="text-embedding-3-small") Settings.llm = llm Settings.embed_model = embed_model
## 1. Simple Structured Extraction¶
You can convert any LLM to a "structured LLM" by attaching an output class to it through `as_structured_llm`.
Here we pass a simple `Album` class which contains a list of songs. We can then use the normal LLM endpoints like chat/complete.
**NOTE** : async is supported but streaming is coming soon.
In [ ]:
Copied!
```
from typing import List
from pydantic import BaseModel, Field


class Song(BaseModel):
    """Data model for a song."""

    title: str
    length_seconds: int


class Album(BaseModel):
    """Data model for an album."""

    name: str
    artist: str
    songs: List[Song]

```

from typing import List from pydantic import BaseModel, Field class Song(BaseModel): """Data model for a song.""" title: str length_seconds: int class Album(BaseModel): """Data model for an album.""" name: str artist: str songs: List[Song]
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

sllm = llm.as_structured_llm(output_cls=Album)
input_msg = ChatMessage.from_str("Generate an example album from The Shining")

```

from llama_index.core.llms import ChatMessage sllm = llm.as_structured_llm(output_cls=Album) input_msg = ChatMessage.from_str("Generate an example album from The Shining")
#### Sync¶
In [ ]:
Copied!
```
output = sllm.chat([input_msg])
# get actual object
output_obj = output.raw

```

output = sllm.chat([input_msg]) # get actual object output_obj = output.raw
In [ ]:
Copied!
```
print(str(output))
print(output_obj)

```

print(str(output)) print(output_obj)
```
assistant: {"name": "The Shining: Original Soundtrack", "artist": "Various Artists", "songs": [{"title": "Main Title", "length_seconds": 180}, {"title": "Rocky Mountains", "length_seconds": 210}, {"title": "Lontano", "length_seconds": 720}, {"title": "Music for Strings, Percussion and Celesta", "length_seconds": 540}, {"title": "Utrenja (Excerpt)", "length_seconds": 300}, {"title": "The Awakening of Jacob", "length_seconds": 480}, {"title": "De Natura Sonoris No. 2", "length_seconds": 540}, {"title": "Home", "length_seconds": 180}, {"title": "Midnight, the Stars and You", "length_seconds": 180}, {"title": "It's All Forgotten Now", "length_seconds": 150}, {"title": "Masquerade", "length_seconds": 180}]}
name='The Shining: Original Soundtrack' artist='Various Artists' songs=[Song(title='Main Title', length_seconds=180), Song(title='Rocky Mountains', length_seconds=210), Song(title='Lontano', length_seconds=720), Song(title='Music for Strings, Percussion and Celesta', length_seconds=540), Song(title='Utrenja (Excerpt)', length_seconds=300), Song(title='The Awakening of Jacob', length_seconds=480), Song(title='De Natura Sonoris No. 2', length_seconds=540), Song(title='Home', length_seconds=180), Song(title='Midnight, the Stars and You', length_seconds=180), Song(title="It's All Forgotten Now", length_seconds=150), Song(title='Masquerade', length_seconds=180)]

```

#### Async¶
In [ ]:
Copied!
```
output = await sllm.achat([input_msg])
# get actual object
output_obj = output.raw
print(str(output))

```

output = await sllm.achat([input_msg]) # get actual object output_obj = output.raw print(str(output))
```
assistant: {"name": "The Shining: Original Soundtrack", "artist": "Various Artists", "songs": [{"title": "Main Title (The Shining)", "length_seconds": 180}, {"title": "Rocky Mountains", "length_seconds": 210}, {"title": "Lontano", "length_seconds": 240}, {"title": "Music for Strings, Percussion and Celesta", "length_seconds": 300}, {"title": "Utrenja (Excerpt)", "length_seconds": 180}, {"title": "The Awakening of Jacob", "length_seconds": 150}, {"title": "De Natura Sonoris No. 2", "length_seconds": 270}, {"title": "Home", "length_seconds": 200}, {"title": "Heartbeats and Worry", "length_seconds": 160}, {"title": "The Overlook", "length_seconds": 220}]}

```

#### Streaming¶
In [ ]:
Copied!
```
from IPython.display import clear_output
from pprint import pprint

stream_output = sllm.stream_chat([input_msg])
for partial_output in stream_output:
    clear_output(wait=True)
    pprint(partial_output.raw.dict())

output_obj = partial_output.raw
print(str(output))

```

from IPython.display import clear_output from pprint import pprint stream_output = sllm.stream_chat([input_msg]) for partial_output in stream_output: clear_output(wait=True) pprint(partial_output.raw.dict()) output_obj = partial_output.raw print(str(output))
```
{'artist': 'Various Artists',
 'name': 'The Shining: Original Soundtrack',
 'songs': [{'length_seconds': 180, 'title': 'Main Title'},
           {'length_seconds': 210, 'title': 'Rocky Mountains'},
           {'length_seconds': 240, 'title': 'Lontano'},
           {'length_seconds': 540,
            'title': 'Music for Strings, Percussion and Celesta'},
           {'length_seconds': 300, 'title': 'Utrenja (Excerpt)'},
           {'length_seconds': 360, 'title': 'The Awakening of Jacob'},
           {'length_seconds': 420, 'title': 'De Natura Sonoris No. 2'},
           {'length_seconds': 180, 'title': 'Home'},
           {'length_seconds': 180, 'title': 'Midnight, the Stars and You'},
           {'length_seconds': 150, 'title': "It's All Forgotten Now"},
           {'length_seconds': 120, 'title': 'Masquerade'}]}
assistant: {"name": "The Shining: Original Soundtrack", "artist": "Various Artists", "songs": [{"title": "Main Title (The Shining)", "length_seconds": 180}, {"title": "Rocky Mountains", "length_seconds": 210}, {"title": "Lontano", "length_seconds": 240}, {"title": "Music for Strings, Percussion and Celesta", "length_seconds": 300}, {"title": "Utrenja (Excerpt)", "length_seconds": 180}, {"title": "The Awakening of Jacob", "length_seconds": 150}, {"title": "De Natura Sonoris No. 2", "length_seconds": 270}, {"title": "Home", "length_seconds": 200}, {"title": "Heartbeats and Worry", "length_seconds": 160}, {"title": "The Overlook", "length_seconds": 220}]}

```

#### Async Streaming¶
In [ ]:
Copied!
```
from IPython.display import clear_output
from pprint import pprint

stream_output = await sllm.astream_chat([input_msg])
async for partial_output in stream_output:
    clear_output(wait=True)
    pprint(partial_output.raw.dict())

```

from IPython.display import clear_output from pprint import pprint stream_output = await sllm.astream_chat([input_msg]) async for partial_output in stream_output: clear_output(wait=True) pprint(partial_output.raw.dict())
```
{'artist': 'Various Artists',
 'name': 'The Shining: Original Soundtrack',
 'songs': [{'length_seconds': 180, 'title': 'Main Title'},
           {'length_seconds': 210, 'title': 'Rocky Mountains'},
           {'length_seconds': 720, 'title': 'Lontano'},
           {'length_seconds': 540,
            'title': 'Music for Strings, Percussion and Celesta'},
           {'length_seconds': 300, 'title': 'Utrenja (Excerpt)'},
           {'length_seconds': 480, 'title': 'The Awakening of Jacob'},
           {'length_seconds': 540, 'title': 'De Natura Sonoris No. 2'},
           {'length_seconds': 180, 'title': 'Home'},
           {'length_seconds': 180, 'title': 'Midnight, the Stars and You'},
           {'length_seconds': 180, 'title': "It's All Forgotten Now"},
           {'length_seconds': 180, 'title': 'Masquerade'}]}

```

### 1.b Use the `structured_predict` Function¶
Instead of explicitly doing `llm.as_structured_llm(...)`, every LLM class has a `structured_predict` function which allows you to more easily call the LLM with a prompt template + template variables to return a strutured output in one line of code.
In [ ]:
Copied!
```
# use query pipelines
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.llms.openai import OpenAI

chat_prompt_tmpl = ChatPromptTemplate(
    message_templates=[
        ChatMessage.from_str(
            "Generate an example album from {movie_name}", role="user"
        )
    ]
)

llm = OpenAI(model="gpt-4o")
album = llm.structured_predict(
    Album, chat_prompt_tmpl, movie_name="Lord of the Rings"
)
album

```

# use query pipelines from llama_index.core.prompts import ChatPromptTemplate from llama_index.core.llms import ChatMessage from llama_index.llms.openai import OpenAI chat_prompt_tmpl = ChatPromptTemplate( message_templates=[ ChatMessage.from_str( "Generate an example album from {movie_name}", role="user" ) ] ) llm = OpenAI(model="gpt-4o") album = llm.structured_predict( Album, chat_prompt_tmpl, movie_name="Lord of the Rings" ) album
Out[ ]:
```
Album(name='Songs of Middle-earth', artist='Various Artists', songs=[Song(title='The Shire', length_seconds=180), Song(title='The Fellowship', length_seconds=240), Song(title="Gollum's Theme", length_seconds=200), Song(title="Rohan's Call", length_seconds=220), Song(title="The Battle of Helm's Deep", length_seconds=300), Song(title='Lothlórien', length_seconds=210), Song(title='The Return of the King', length_seconds=250), Song(title='Into the West', length_seconds=260)])
```

## 2. Plug into RAG Pipeline¶
You can also plug this into a RAG pipeline. Below we show structured extraction from an Apple 10K report.
In [ ]:
Copied!
```
!mkdir data
!wget "https://s2.q4cdn.com/470004039/files/doc_financials/2021/q4/_10-K-2021-(As-Filed).pdf" -O data/apple_2021_10k.pdf

```

!mkdir data !wget "https://s2.q4cdn.com/470004039/files/doc_financials/2021/q4/_10-K-2021-(As-Filed).pdf" -O data/apple_2021_10k.pdf
#### Option 1: Use LlamaParse¶
You will need an account at https://cloud.llamaindex.ai/ and an API Key to use LlamaParse, our document parser for 10K filings.
In [ ]:
Copied!
```
from llama_parse import LlamaParse

# os.environ["LLAMA_CLOUD_API_KEY"] = "llx-..."
orig_docs = LlamaParse(result_type="text").load_data(
    "./data/apple_2021_10k.pdf"
)

```

from llama_parse import LlamaParse # os.environ["LLAMA_CLOUD_API_KEY"] = "llx-..." orig_docs = LlamaParse(result_type="text").load_data( "./data/apple_2021_10k.pdf" )
```
Started parsing the file under job_id cac11eca-7e00-452f-93f6-19c861b4c130

```

In [ ]:
Copied!
```
from copy import deepcopy
from llama_index.core.schema import TextNode


def get_page_nodes(docs, separator="\n---\n"):
    """Split each document into page node, by separator."""
    nodes = []
    for doc in docs:
        doc_chunks = doc.text.split(separator)
        for doc_chunk in doc_chunks:
            node = TextNode(
                text=doc_chunk,
                metadata=deepcopy(doc.metadata),
            )
            nodes.append(node)

    return nodes


docs = get_page_nodes(orig_docs)
print(docs[0].get_content())

```

from copy import deepcopy from llama_index.core.schema import TextNode def get_page_nodes(docs, separator="\n---\n"): """Split each document into page node, by separator.""" nodes = [] for doc in docs: doc_chunks = doc.text.split(separator) for doc_chunk in doc_chunks: node = TextNode( text=doc_chunk, metadata=deepcopy(doc.metadata), ) nodes.append(node) return nodes docs = get_page_nodes(orig_docs) print(docs[0].get_content())
```
                                                              UNITED STATES
                                    SECURITIES AND EXCHANGE COMMISSION
                                                          Washington, D.C. 20549

                                                               FORM 10-K
(Mark One)
        ☒ ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934
                                                  For the fiscal year ended September 25, 2021
                                                                            or
     ☐ TRANSITION REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934
                                                For the transition period from               to          .
                                                       Commission File Number: 001-36743

                                                               Apple Inc.
                                              (Exact name of Registrant as specified in its charter)

                            California                                                                          94-2404110
                     (State or other jurisdiction                                                    (I.R.S. Employer Identification No.)
                  of incorporation or organization)

                     One Apple Park Way
                     Cupertino, California                                                                         95014
              (Address of principal executive offices)                                                            (Zip Code)
                                                                    (408) 996-1010
                                                 (Registrant’s telephone number, including area code)

                                               Securities registered pursuant to Section 12(b) of the Act:

                                                                         Trading
                         Title of each class                            symbol(s)               Name of each exchange on which registered
      Common Stock, $0.00001 par value per share                         AAPL                       The Nasdaq Stock Market LLC
                    1.000% Notes due 2022                                   —                       The Nasdaq Stock Market LLC
                    1.375% Notes due 2024                                   —                       The Nasdaq Stock Market LLC
                    0.000% Notes due 2025                                   —                       The Nasdaq Stock Market LLC
                    0.875% Notes due 2025                                   —                       The Nasdaq Stock Market LLC
                    1.625% Notes due 2026                                   —                       The Nasdaq Stock Market LLC
                    2.000% Notes due 2027                                   —                       The Nasdaq Stock Market LLC
                    1.375% Notes due 2029                                   —                       The Nasdaq Stock Market LLC
                    3.050% Notes due 2029                                   —                       The Nasdaq Stock Market LLC
                    0.500% Notes due 2031                                   —                       The Nasdaq Stock Market LLC
                    3.600% Notes due 2042                                   —                       The Nasdaq Stock Market LLC

                                           Securities registered pursuant to Section 12(g) of the Act: None

Indicate by check mark if the Registrant is a well-known seasoned issuer, as defined in Rule 405 of the Securities Act.
                                                                    Yes ☒      No ☐
Indicate by check mark if the Registrant is not required to file reports pursuant to Section 13 or Section 15(d) of the Act.
                                                                    Yes ☐      No ☒

```

#### Option 2: Use SimpleDirectoryReader¶
You can also choose to use the free PDF parser bundled into our `SimpleDirectoryReader`.
In [ ]:
Copied!
```
# # OPTION 2: Use SimpleDirectoryReader
# from llama_index.core import SimpleDirectoryReader

# reader = SimpleDirectoryReader(input_files=["apple_2021_10k.pdf"])
# docs = reader.load_data()

```

# # OPTION 2: Use SimpleDirectoryReader # from llama_index.core import SimpleDirectoryReader # reader = SimpleDirectoryReader(input_files=["apple_2021_10k.pdf"]) # docs = reader.load_data()
#### Build RAG Pipeline, Define Structured Output Schema¶
We build a RAG pipeline with our trusty VectorStoreIndex and reranker module. We then define the output as a Pydantic model. This allows us to create a structured LLM with the output class attached.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

# skip chunking since we're doing page-level chunking
index = VectorStoreIndex(docs)

```

from llama_index.core import VectorStoreIndex # skip chunking since we're doing page-level chunking index = VectorStoreIndex(docs)
In [ ]:
Copied!
```
from llama_index.postprocessor.flag_embedding_reranker import (
    FlagEmbeddingReranker,
)

reranker = FlagEmbeddingReranker(
    top_n=5,
    model="BAAI/bge-reranker-large",
)

```

from llama_index.postprocessor.flag_embedding_reranker import ( FlagEmbeddingReranker, ) reranker = FlagEmbeddingReranker( top_n=5, model="BAAI/bge-reranker-large", )
In [ ]:
Copied!
```
from pydantic import BaseModel, Field
from typing import List


class Output(BaseModel):
    """Output containing the response, page numbers, and confidence."""

    response: str = Field(..., description="The answer to the question.")
    page_numbers: List[int] = Field(
        ...,
        description="The page numbers of the sources used to answer this question. Do not include a page number if the context is irrelevant.",
    )
    confidence: float = Field(
        ...,
        description="Confidence value between 0-1 of the correctness of the result.",
    )
    confidence_explanation: str = Field(
        ..., description="Explanation for the confidence score"
    )


sllm = llm.as_structured_llm(output_cls=Output)

```

from pydantic import BaseModel, Field from typing import List class Output(BaseModel): """Output containing the response, page numbers, and confidence.""" response: str = Field(..., description="The answer to the question.") page_numbers: List[int] = Field( ..., description="The page numbers of the sources used to answer this question. Do not include a page number if the context is irrelevant.", ) confidence: float = Field( ..., description="Confidence value between 0-1 of the correctness of the result.", ) confidence_explanation: str = Field( ..., description="Explanation for the confidence score" ) sllm = llm.as_structured_llm(output_cls=Output)
#### Run Queries¶
In [ ]:
Copied!
```
query_engine = index.as_query_engine(
    similarity_top_k=5,
    node_postprocessors=[reranker],
    llm=sllm,
    response_mode="tree_summarize",  # you can also select other modes like `compact`, `refine`
)

```

query_engine = index.as_query_engine( similarity_top_k=5, node_postprocessors=[reranker], llm=sllm, response_mode="tree_summarize", # you can also select other modes like `compact`, `refine` )
In [ ]:
Copied!
```
response = query_engine.query("Net sales for each product category in 2021")
print(str(response))

```

response = query_engine.query("Net sales for each product category in 2021") print(str(response))
```
{"response": "In 2021, the net sales for each product category were as follows: iPhone: $191,973 million, Mac: $35,190 million, iPad: $31,862 million, Wearables, Home and Accessories: $38,367 million, and Services: $68,425 million.", "page_numbers": [21], "confidence": 1.0, "confidence_explanation": "The figures are directly taken from the provided data, ensuring high accuracy."}

```

In [ ]:
Copied!
```
response.response.dict()

```

response.response.dict()
Out[ ]:
```
{'response': 'In 2021, the net sales for each product category were as follows: iPhone: $191,973 million, Mac: $35,190 million, iPad: $31,862 million, Wearables, Home and Accessories: $38,367 million, and Services: $68,425 million.',
 'page_numbers': [21],
 'confidence': 1.0,
 'confidence_explanation': 'The figures are directly taken from the provided data, ensuring high accuracy.'}
```

