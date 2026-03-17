![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Pydantic Extractor¶
Here we test out the capabilities of our `PydanticProgramExtractor` - being able to extract out an entire Pydantic object using an LLM (either a standard text completion LLM or a function calling LLM).
The advantage of this over using a "single" metadata extractor is that we can extract multiple entities with a single LLM call.
## Setup¶
In [ ]:
Copied!
```
%pip install llama-index-readers-web
%pip install llama-index-program-openai

```

%pip install llama-index-readers-web %pip install llama-index-program-openai
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

import os
import openai

```

import nest_asyncio nest_asyncio.apply() import os import openai
In [ ]:
Copied!
```
os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
openai.api_key = os.getenv("OPENAI_API_KEY")

```

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY" openai.api_key = os.getenv("OPENAI_API_KEY")
### Setup the Pydantic Model¶
Here we define a basic structured schema that we want to extract. It contains:
  * entities: unique entities in a text chunk
  * summary: a concise summary of the text chunk
  * contains_number: whether the chunk contains numbers


This is obviously a toy schema. We'd encourage you to be creative about the type of metadata you'd want to extract!
In [ ]:
Copied!
```
from pydantic import BaseModel, Field
from typing import List

```

from pydantic import BaseModel, Field from typing import List
In [ ]:
Copied!
```
class NodeMetadata(BaseModel):
    """Node metadata."""

    entities: List[str] = Field(
        ..., description="Unique entities in this text chunk."
    )
    summary: str = Field(
        ..., description="A concise summary of this text chunk."
    )
    contains_number: bool = Field(
        ...,
        description=(
            "Whether the text chunk contains any numbers (ints, floats, etc.)"
        ),
    )

```

class NodeMetadata(BaseModel): """Node metadata.""" entities: List[str] = Field( ..., description="Unique entities in this text chunk." ) summary: str = Field( ..., description="A concise summary of this text chunk." ) contains_number: bool = Field( ..., description=( "Whether the text chunk contains any numbers (ints, floats, etc.)" ), )
### Setup the Extractor¶
Here we setup the metadata extractor. Note that we provide the prompt template for visibility into what's going on.
In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core.extractors import PydanticProgramExtractor

EXTRACT_TEMPLATE_STR = """\
Here is the content of the section:
----------------
{context_str}
----------------
Given the contextual information, extract out a {class_name} object.\
"""

openai_program = OpenAIPydanticProgram.from_defaults(
    output_cls=NodeMetadata,
    prompt_template_str="{input}",
    # extract_template_str=EXTRACT_TEMPLATE_STR
)

program_extractor = PydanticProgramExtractor(
    program=openai_program, input_key="input", show_progress=True
)

```

from llama_index.program.openai import OpenAIPydanticProgram from llama_index.core.extractors import PydanticProgramExtractor EXTRACT_TEMPLATE_STR = """\ Here is the content of the section: ---------------- {context_str} ---------------- Given the contextual information, extract out a {class_name} object.\ """ openai_program = OpenAIPydanticProgram.from_defaults( output_cls=NodeMetadata, prompt_template_str="{input}", # extract_template_str=EXTRACT_TEMPLATE_STR ) program_extractor = PydanticProgramExtractor( program=openai_program, input_key="input", show_progress=True )
### Load in Data¶
We load in Eugene's essay (https://eugeneyan.com/writing/llm-patterns/) using our LlamaHub SimpleWebPageReader.
In [ ]:
Copied!
```
# load in blog

from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.node_parser import SentenceSplitter

reader = SimpleWebPageReader(html_to_text=True)
docs = reader.load_data(urls=["https://eugeneyan.com/writing/llm-patterns/"])

```

# load in blog from llama_index.readers.web import SimpleWebPageReader from llama_index.core.node_parser import SentenceSplitter reader = SimpleWebPageReader(html_to_text=True) docs = reader.load_data(urls=["https://eugeneyan.com/writing/llm-patterns/"])
In [ ]:
Copied!
```
from llama_index.core.ingestion import IngestionPipeline

node_parser = SentenceSplitter(chunk_size=1024)

pipeline = IngestionPipeline(transformations=[node_parser, program_extractor])

orig_nodes = pipeline.run(documents=docs)

```

from llama_index.core.ingestion import IngestionPipeline node_parser = SentenceSplitter(chunk_size=1024) pipeline = IngestionPipeline(transformations=[node_parser, program_extractor]) orig_nodes = pipeline.run(documents=docs)
In [ ]:
Copied!
```
orig_nodes

```

orig_nodes
## Extract Metadata¶
Now that we've setup the metadata extractor and the data, we're ready to extract some metadata!
We see that the pydantic feature extractor is able to extract _all_ metadata from a given chunk in a single LLM call.
In [ ]:
Copied!
```
sample_entry = program_extractor.extract(orig_nodes[0:1])[0]

```

sample_entry = program_extractor.extract(orig_nodes[0:1])[0]
```
Extracting Pydantic object:   0%|          | 0/1 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
display(sample_entry)

```

display(sample_entry)
```
{'entities': ['eugeneyan', 'HackerNews', 'Karpathy'],
 'summary': 'This section discusses practical patterns for integrating large language models (LLMs) into systems & products. It introduces seven key patterns and provides information on evaluations and benchmarks in the field of language modeling.',
 'contains_number': True}
```

In [ ]:
Copied!
```
new_nodes = program_extractor.process_nodes(orig_nodes)

```

new_nodes = program_extractor.process_nodes(orig_nodes)
```
Extracting Pydantic object:   0%|          | 0/29 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
display(new_nodes[5:7])

```

display(new_nodes[5:7])
