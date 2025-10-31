# Metadata Extraction and Augmentation w/ Marvin¶
This notebook walks through using `Marvin` to extract and augment metadata from text. Marvin uses the LLM to identify and extract metadata. Metadata can be anything from additional and enhanced questions and answers to business object identification and elaboration. This notebook will demonstrate pulling out and elaborating on Sports Supplement information in a csv document.
Note: You will need to supply a valid open ai key below to run this notebook.
## Setup¶
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-extractors-marvin

```

%pip install llama-index-llms-openai %pip install llama-index-extractors-marvin
In [ ]:
Copied!
```
# !pip install marvin

```

# !pip install marvin
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.extractors.marvin import MarvinMetadataExtractor

```

from llama_index.core import SimpleDirectoryReader from llama_index.llms.openai import OpenAI from llama_index.core.node_parser import TokenTextSplitter from llama_index.extractors.marvin import MarvinMetadataExtractor
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
import os
import openai

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os import openai os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("data").load_data()

# limit document text length
documents[0].text = documents[0].text[:10000]

```

documents = SimpleDirectoryReader("data").load_data() # limit document text length documents[0].text = documents[0].text[:10000]
In [ ]:
Copied!
```
import marvin

from pydantic import BaseModel, Field

marvin.settings.openai.api_key = os.environ["OPENAI_API_KEY"]
marvin.settings.openai.chat.completions.model = "gpt-4o"


class SportsSupplement(BaseModel):
    name: str = Field(..., description="The name of the sports supplement")
    description: str = Field(
        ..., description="A description of the sports supplement"
    )
    pros_cons: str = Field(
        ..., description="The pros and cons of the sports supplement"
    )

```

import marvin from pydantic import BaseModel, Field marvin.settings.openai.api_key = os.environ["OPENAI_API_KEY"] marvin.settings.openai.chat.completions.model = "gpt-4o" class SportsSupplement(BaseModel): name: str = Field(..., description="The name of the sports supplement") description: str = Field( ..., description="A description of the sports supplement" ) pros_cons: str = Field( ..., description="The pros and cons of the sports supplement" )
In [ ]:
Copied!
```
# construct text splitter to split texts into chunks for processing
# this takes a while to process, you can increase processing time by using larger chunk_size
# file size is a factor too of course
node_parser = TokenTextSplitter(
    separator=" ", chunk_size=512, chunk_overlap=128
)

# create metadata extractor
metadata_extractor = MarvinMetadataExtractor(
    marvin_model=SportsSupplement
)  # let's extract custom entities for each node.

# use node_parser to get nodes from the documents
from llama_index.core.ingestion import IngestionPipeline

pipeline = IngestionPipeline(transformations=[node_parser, metadata_extractor])

nodes = pipeline.run(documents=documents, show_progress=True)

```

# construct text splitter to split texts into chunks for processing # this takes a while to process, you can increase processing time by using larger chunk_size # file size is a factor too of course node_parser = TokenTextSplitter( separator=" ", chunk_size=512, chunk_overlap=128 ) # create metadata extractor metadata_extractor = MarvinMetadataExtractor( marvin_model=SportsSupplement ) # let's extract custom entities for each node. # use node_parser to get nodes from the documents from llama_index.core.ingestion import IngestionPipeline pipeline = IngestionPipeline(transformations=[node_parser, metadata_extractor]) nodes = pipeline.run(documents=documents, show_progress=True)
```
Parsing nodes: 100%|██████████| 1/1 [00:00<00:00, 41.49it/s]
Extracting marvin metadata: 100%|██████████| 9/9 [00:22<00:00,  2.46s/it]

```

In [ ]:
Copied!
```
from pprint import pprint

for i in range(5):
    pprint(nodes[i].metadata)

```

from pprint import pprint for i in range(5): pprint(nodes[i].metadata)
```
{'creation_date': '2024-08-07',
 'file_name': 'Sports Supplements.csv',
 'file_path': '/data001/home/dongwoo.jeong/llama_index/docs/docs/examples/metadata_extraction/data/Sports '
              'Supplements.csv',
 'file_size': 62403,
 'file_type': 'text/csv',
 'last_modified_date': '2024-08-07',
 'marvin_metadata': {'description': 'L-arginine alpha-ketoglutarate is a '
                                    'supplement often used to improve peak '
                                    'power output and strength–power during '
                                    'weight training. A 2006 study by Campbell '
                                    'et al. found that AAKG supplementation '
                                    'improved maximum effort 1-repetition '
                                    'bench press and Wingate peak power '
                                    'performance.',
                     'name': 'AAKG',
                     'pros_cons': 'Pros: Improves peak power output and '
                                  'strength–power. Cons: No significant effect '
                                  'on body composition, aerobic capacity, or '
                                  'muscle endurance.'}}
{'creation_date': '2024-08-07',
 'file_name': 'Sports Supplements.csv',
 'file_path': '/data001/home/dongwoo.jeong/llama_index/docs/docs/examples/metadata_extraction/data/Sports '
              'Supplements.csv',
 'file_size': 62403,
 'file_type': 'text/csv',
 'last_modified_date': '2024-08-07',
 'marvin_metadata': {'description': 'Baking soda, also known as bicarbonate of '
                                    'soda or sodium bicarbonate (NaHCO3), is '
                                    'used to enhance high-intensity '
                                    'performance in anaerobic activities such '
                                    'as rowing, cycling, swimming, and '
                                    'running. It works by making the blood '
                                    'more alkaline, which can improve '
                                    'performance in lactic-acid-fueled events '
                                    'like the 800m sprint.',
                     'name': 'Baking soda',
                     'pros_cons': 'Pros: Improves performance in '
                                  'high-intensity, anaerobic activities. Cons: '
                                  'Can cause a badly upset stomach.'}}
{'creation_date': '2024-08-07',
 'file_name': 'Sports Supplements.csv',
 'file_path': '/data001/home/dongwoo.jeong/llama_index/docs/docs/examples/metadata_extraction/data/Sports '
              'Supplements.csv',
 'file_size': 62403,
 'file_type': 'text/csv',
 'last_modified_date': '2024-08-07',
 'marvin_metadata': {'description': 'Branched-chain amino acids (BCAAs) are '
                                    'essential nutrients that the body obtains '
                                    'from proteins found in food, especially '
                                    'meat, dairy products, and legumes. They '
                                    'include leucine, isoleucine, and valine.',
                     'name': 'BCAAs',
                     'pros_cons': 'Pros: May help with fatigue resistance, '
                                  'aerobic endurance, and performance in '
                                  'activities like cycling and circuit '
                                  'training. Cons: Limited evidence on '
                                  'long-term benefits and potential side '
                                  'effects.'}}
{'creation_date': '2024-08-07',
 'file_name': 'Sports Supplements.csv',
 'file_path': '/data001/home/dongwoo.jeong/llama_index/docs/docs/examples/metadata_extraction/data/Sports '
              'Supplements.csv',
 'file_size': 62403,
 'file_type': 'text/csv',
 'last_modified_date': '2024-08-07',
 'marvin_metadata': {'description': 'Branched-chain amino acids (BCAAs) are '
                                    'essential nutrients that the body obtains '
                                    'from proteins found in food, especially '
                                    'meat, dairy products, and legumes. They '
                                    'include leucine, isoleucine, and valine. '
                                    'BCAAs are commonly used to improve '
                                    'exercise performance and reduce protein '
                                    'and muscle breakdown during intense '
                                    'exercise.',
                     'name': 'BCAAs',
                     'pros_cons': 'Pros: \n'
                                  '1. May improve aerobic performance, '
                                  'endurance, power, and strength.\n'
                                  '2. Can enhance immune defenses in athletes '
                                  'and general fitness.\n'
                                  '3. Useful for various types of exercise '
                                  'including cycling and running.\n'
                                  '\n'
                                  'Cons: \n'
                                  '1. Limited evidence on long-term benefits.\n'
                                  '2. Potential for overconsumption leading to '
                                  'imbalances.\n'
                                  '3. Some studies show no significant '
                                  'benefit.'}}
{'creation_date': '2024-08-07',
 'file_name': 'Sports Supplements.csv',
 'file_path': '/data001/home/dongwoo.jeong/llama_index/docs/docs/examples/metadata_extraction/data/Sports '
              'Supplements.csv',
 'file_size': 62403,
 'file_type': 'text/csv',
 'last_modified_date': '2024-08-07',
 'marvin_metadata': {'description': 'Branched-chain amino acids (BCAAs) are '
                                    'essential nutrients that the body obtains '
                                    'from proteins found in food, especially '
                                    'meat, dairy products, and legumes. They '
                                    'include leucine, isoleucine, and valine.',
                     'name': 'BCAAs',
                     'pros_cons': 'Pros: May support immune defenses in '
                                  'athletes, aid in general fitness, assist in '
                                  'running, swimming, and rowing, and help '
                                  'with body composition, fat burning, muscle '
                                  'building, muscle damage, soreness, '
                                  'recovery, and injury prevention. Cons: '
                                  'Effectiveness can vary based on individual '
                                  'response and specific use case.'}}

```

