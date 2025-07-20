![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Entity Metadata Extraction¶
In this demo, we use the new `EntityExtractor` to extract entities from each node, stored in metadata. The default model is `tomaarsen/span-marker-mbert-base-multinerd`, which is downloaded an run locally from HuggingFace.
For more information on metadata extraction in LlamaIndex, see our documentation.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-extractors-entity

```

%pip install llama-index-llms-openai %pip install llama-index-extractors-entity
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# Needed to run the entity extractor
# !pip install span_marker

import os

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

```

# Needed to run the entity extractor # !pip install span_marker import os os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
## Setup the Extractor and Parser¶
In [ ]:
Copied!
```
from llama_index.extractors.entity import EntityExtractor
from llama_index.core.node_parser import SentenceSplitter

entity_extractor = EntityExtractor(
    prediction_threshold=0.5,
    label_entities=False,  # include the entity label in the metadata (can be erroneous)
    device="cpu",  # set to "cuda" if you have a GPU
)

node_parser = SentenceSplitter()

transformations = [node_parser, entity_extractor]

```

from llama_index.extractors.entity import EntityExtractor from llama_index.core.node_parser import SentenceSplitter entity_extractor = EntityExtractor( prediction_threshold=0.5, label_entities=False, # include the entity label in the metadata (can be erroneous) device="cpu", # set to "cuda" if you have a GPU ) node_parser = SentenceSplitter() transformations = [node_parser, entity_extractor]
```
/Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages/tqdm/auto.py:22: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm
/Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages/bitsandbytes/cextension.py:34: UserWarning: The installed version of bitsandbytes was compiled without GPU support. 8-bit optimizers, 8-bit multiplication, and GPU quantization are unavailable.
  warn("The installed version of bitsandbytes was compiled without GPU support. "

```

```
'NoneType' object has no attribute 'cadam32bit_grad_fp32'

```

## Load the data¶
Here, we will download the 2023 IPPC Climate Report - Chapter 3 on Oceans and Coastal Ecosystems (172 Pages)
In [ ]:
Copied!
```
!curl https://www.ipcc.ch/report/ar6/wg2/downloads/report/IPCC_AR6_WGII_Chapter03.pdf --output IPCC_AR6_WGII_Chapter03.pdf

```

!curl https://www.ipcc.ch/report/ar6/wg2/downloads/report/IPCC_AR6_WGII_Chapter03.pdf --output IPCC_AR6_WGII_Chapter03.pdf
```
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 20.7M  100 20.7M    0     0  22.1M      0 --:--:-- --:--:-- --:--:-- 22.1M

```

Next, load the documents.
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader(
    input_files=["./IPCC_AR6_WGII_Chapter03.pdf"]
).load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader( input_files=["./IPCC_AR6_WGII_Chapter03.pdf"] ).load_data()
## Extracting Metadata¶
Now, this is a pretty long document. Since we are not running on CPU, for now, we will only run on a subset of documents. Feel free to run it on all documents on your own though!
In [ ]:
Copied!
```
from llama_index.core.ingestion import IngestionPipeline

import random

random.seed(42)
# comment out to run on all documents
# 100 documents takes about 5 minutes on CPU
documents = random.sample(documents, 100)

pipeline = IngestionPipeline(transformations=transformations)

nodes = pipeline.run(documents=documents)

```

from llama_index.core.ingestion import IngestionPipeline import random random.seed(42) # comment out to run on all documents # 100 documents takes about 5 minutes on CPU documents = random.sample(documents, 100) pipeline = IngestionPipeline(transformations=transformations) nodes = pipeline.run(documents=documents)
```
huggingface/tokenizers: The current process just got forked, after parallelism has already been used. Disabling parallelism to avoid deadlocks...
To disable this warning, you can either:
	- Avoid using `tokenizers` before the fork if possible
	- Explicitly set the environment variable TOKENIZERS_PARALLELISM=(true | false)

```

### Examine the outputs¶
In [ ]:
Copied!
```
samples = random.sample(nodes, 5)
for node in samples:
    print(node.metadata)

```

samples = random.sample(nodes, 5) for node in samples: print(node.metadata)
```
{'page_label': '387', 'file_name': 'IPCC_AR6_WGII_Chapter03.pdf'}
{'page_label': '410', 'file_name': 'IPCC_AR6_WGII_Chapter03.pdf', 'entities': {'Parmesan', 'Boyd', 'Riebesell', 'Gattuso'}}
{'page_label': '391', 'file_name': 'IPCC_AR6_WGII_Chapter03.pdf', 'entities': {'Gulev', 'Fox-Kemper'}}
{'page_label': '430', 'file_name': 'IPCC_AR6_WGII_Chapter03.pdf', 'entities': {'Kessouri', 'van der Sleen', 'Brodeur', 'Siedlecki', 'Fiechter', 'Ramajo', 'Carozza'}}
{'page_label': '388', 'file_name': 'IPCC_AR6_WGII_Chapter03.pdf'}

```

## Try a Query!¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2)

index = VectorStoreIndex(nodes=nodes)

```

from llama_index.core import VectorStoreIndex from llama_index.llms.openai import OpenAI from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-3.5-turbo", temperature=0.2) index = VectorStoreIndex(nodes=nodes)
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What is said by Fox-Kemper?")
print(response)

```

query_engine = index.as_query_engine() response = query_engine.query("What is said by Fox-Kemper?") print(response)
```
According to the provided context information, Fox-Kemper is mentioned in relation to the observed and projected trends of ocean warming and marine heatwaves. It is stated that Fox-Kemper et al. (2021) reported that ocean warming has increased on average by 0.88°C from 1850-1900 to 2011-2020. Additionally, it is mentioned that Fox-Kemper et al. (2021) projected that ocean warming will continue throughout the 21st century, with the rate of global ocean warming becoming scenario-dependent from the mid-21st century. Fox-Kemper is also cited as a source for the information on the increasing frequency, intensity, and duration of marine heatwaves over the 20th and early 21st centuries, as well as the projected increase in frequency of marine heatwaves in the future.

```

### Contrast without metadata¶
Here, we re-construct the index, but without metadata
In [ ]:
Copied!
```
for node in nodes:
    node.metadata.pop("entities", None)

print(nodes[0].metadata)

```

for node in nodes: node.metadata.pop("entities", None) print(nodes[0].metadata)
```
{'page_label': '542', 'file_name': 'IPCC_AR6_WGII_Chapter03.pdf'}

```

In [ ]:
Copied!
```
index = VectorStoreIndex(nodes=nodes)

```

index = VectorStoreIndex(nodes=nodes)
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What is said by Fox-Kemper?")
print(response)

```

query_engine = index.as_query_engine() response = query_engine.query("What is said by Fox-Kemper?") print(response)
```
According to the provided context information, Fox-Kemper is mentioned in relation to the decline of the AMOC (Atlantic Meridional Overturning Circulation) over the 21st century. The statement mentions that there is high confidence in the decline of the AMOC, but low confidence for quantitative projections.

```

As we can see, our metadata-enriched index is able to fetch more relevant information.
