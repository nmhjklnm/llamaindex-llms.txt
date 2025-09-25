# Async Ingestion Pipeline + Metadata Extraction¶
Recently, LlamaIndex has introduced async metadata extraction. Let's compare metadata extraction speeds in an ingestion pipeline using a newer and older version of LlamaIndex.
We will test a pipeline using the classic Paul Graham essay.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-llms-openai

```

%pip install llama-index-embeddings-openai %pip install llama-index-llms-openai
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
## New LlamaIndex Ingestion¶
Using a version of LlamaIndex greater or equal to v0.9.7, we can take advantage of improved async metadata extraction within ingestion pipelines.
**NOTE:** Restart your notebook after installing a new version!
In [ ]:
Copied!
```
!pip install "llama_index>=0.9.7"

```

!pip install "llama_index>=0.9.7"
**NOTE:** The `num_workers` kwarg controls how many requests can be outgoing at a given time using an async semaphore. Setting it higher may increase speeds, but can also lead to timeouts or rate limits, so set it wisely.
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.extractors import TitleExtractor, SummaryExtractor
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import MetadataMode


def build_pipeline():
    llm = OpenAI(model="gpt-3.5-turbo-1106", temperature=0.1)

    transformations = [
        SentenceSplitter(chunk_size=1024, chunk_overlap=20),
        TitleExtractor(
            llm=llm, metadata_mode=MetadataMode.EMBED, num_workers=8
        ),
        SummaryExtractor(
            llm=llm, metadata_mode=MetadataMode.EMBED, num_workers=8
        ),
        OpenAIEmbedding(),
    ]

    return IngestionPipeline(transformations=transformations)

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI from llama_index.core.ingestion import IngestionPipeline from llama_index.core.extractors import TitleExtractor, SummaryExtractor from llama_index.core.node_parser import SentenceSplitter from llama_index.core.schema import MetadataMode def build_pipeline(): llm = OpenAI(model="gpt-3.5-turbo-1106", temperature=0.1) transformations = [ SentenceSplitter(chunk_size=1024, chunk_overlap=20), TitleExtractor( llm=llm, metadata_mode=MetadataMode.EMBED, num_workers=8 ), SummaryExtractor( llm=llm, metadata_mode=MetadataMode.EMBED, num_workers=8 ), OpenAIEmbedding(), ] return IngestionPipeline(transformations=transformations)
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham").load_data()
In [ ]:
Copied!
```
import time

times = []
for _ in range(3):
    time.sleep(30)  # help prevent rate-limits/timeouts, keeps each run fair
    pipline = build_pipeline()
    start = time.time()
    nodes = await pipline.arun(documents=documents)
    end = time.time()
    times.append(end - start)

print(f"Average time: {sum(times) / len(times)}")

```

import time times = [] for _ in range(3): time.sleep(30) # help prevent rate-limits/timeouts, keeps each run fair pipline = build_pipeline() start = time.time() nodes = await pipline.arun(documents=documents) end = time.time() times.append(end - start) print(f"Average time: {sum(times) / len(times)}")
```
100%|██████████| 5/5 [00:01<00:00,  3.99it/s]
100%|██████████| 18/18 [00:07<00:00,  2.36it/s]
100%|██████████| 5/5 [00:01<00:00,  2.97it/s]
100%|██████████| 18/18 [00:06<00:00,  2.63it/s]
100%|██████████| 5/5 [00:01<00:00,  3.84it/s]
100%|██████████| 18/18 [01:07<00:00,  3.75s/it]

```

```
Average time: 31.196589946746826

```

The current `openai` python client package is a tad unstable -- sometimes async jobs will timeout, skewing the average. You can see the last progress bar took 1 minute instead of the previous 6 or 7 seconds, skewing the average.
## Old LlamaIndex Ingestion¶
Now, lets compare to an older version of LlamaIndex, which was using "fake" async for metadata extraction.
**NOTE:** Restart your notebook after installing the new version!
In [ ]:
Copied!
```
!pip install "llama_index<0.9.6"

```

!pip install "llama_index<0.9.6"
```
Collecting llama_index<0.9.6
  Obtaining dependency information for llama_index<0.9.6 from https://files.pythonhosted.org/packages/ac/3c/dee8ec4fecaaeabbd8a61ade9ddb6af09d05553c2a0acbebd1b559eaeb30/llama_index-0.9.5-py3-none-any.whl.metadata
  Downloading llama_index-0.9.5-py3-none-any.whl.metadata (8.2 kB)
Requirement already satisfied: SQLAlchemy[asyncio]>=1.4.49 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (2.0.23)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (3.8.6)
Requirement already satisfied: aiostream<0.6.0,>=0.5.2 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (0.5.2)
Requirement already satisfied: beautifulsoup4<5.0.0,>=4.12.2 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (4.12.2)
Requirement already satisfied: dataclasses-json in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (0.5.14)
Requirement already satisfied: deprecated>=1.2.9.3 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (1.2.14)
Requirement already satisfied: fsspec>=2023.5.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (2023.10.0)
Requirement already satisfied: httpx in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (0.24.1)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (1.5.8)
Requirement already satisfied: nltk<4.0.0,>=3.8.1 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (3.8.1)
Requirement already satisfied: numpy in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (1.24.4)
Requirement already satisfied: openai>=1.1.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (1.3.5)
Requirement already satisfied: pandas in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (2.0.3)
Requirement already satisfied: tenacity<9.0.0,>=8.2.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (8.2.3)
Requirement already satisfied: tiktoken>=0.3.3 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (0.5.1)
Requirement already satisfied: typing-extensions>=4.5.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (4.8.0)
Requirement already satisfied: typing-inspect>=0.8.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (0.8.0)
Requirement already satisfied: urllib3<2 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from llama_index<0.9.6) (1.26.18)
Requirement already satisfied: attrs>=17.3.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama_index<0.9.6) (23.1.0)
Requirement already satisfied: charset-normalizer<4.0,>=2.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama_index<0.9.6) (3.3.2)
Requirement already satisfied: multidict<7.0,>=4.5 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama_index<0.9.6) (6.0.4)
Requirement already satisfied: async-timeout<5.0,>=4.0.0a3 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama_index<0.9.6) (4.0.3)
Requirement already satisfied: yarl<2.0,>=1.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama_index<0.9.6) (1.9.2)
Requirement already satisfied: frozenlist>=1.1.1 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama_index<0.9.6) (1.4.0)
Requirement already satisfied: aiosignal>=1.1.2 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama_index<0.9.6) (1.3.1)
Requirement already satisfied: soupsieve>1.2 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from beautifulsoup4<5.0.0,>=4.12.2->llama_index<0.9.6) (2.5)
Requirement already satisfied: wrapt<2,>=1.10 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from deprecated>=1.2.9.3->llama_index<0.9.6) (1.15.0)
Requirement already satisfied: click in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama_index<0.9.6) (8.1.7)
Requirement already satisfied: joblib in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama_index<0.9.6) (1.3.2)
Requirement already satisfied: regex>=2021.8.3 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama_index<0.9.6) (2023.10.3)
Requirement already satisfied: tqdm in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama_index<0.9.6) (4.66.1)
Requirement already satisfied: anyio<4,>=3.5.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from openai>=1.1.0->llama_index<0.9.6) (3.7.1)
Requirement already satisfied: distro<2,>=1.7.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from openai>=1.1.0->llama_index<0.9.6) (1.8.0)
Requirement already satisfied: pydantic<3,>=1.9.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from openai>=1.1.0->llama_index<0.9.6) (1.10.12)
Requirement already satisfied: certifi in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from httpx->llama_index<0.9.6) (2023.7.22)
Requirement already satisfied: httpcore<0.18.0,>=0.15.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from httpx->llama_index<0.9.6) (0.17.3)
Requirement already satisfied: idna in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from httpx->llama_index<0.9.6) (3.4)
Requirement already satisfied: sniffio in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from httpx->llama_index<0.9.6) (1.3.0)
Requirement already satisfied: greenlet!=0.4.17 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama_index<0.9.6) (3.0.1)
Requirement already satisfied: requests>=2.26.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from tiktoken>=0.3.3->llama_index<0.9.6) (2.31.0)
Requirement already satisfied: mypy-extensions>=0.3.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from typing-inspect>=0.8.0->llama_index<0.9.6) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from dataclasses-json->llama_index<0.9.6) (3.20.1)
Requirement already satisfied: python-dateutil>=2.8.2 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from pandas->llama_index<0.9.6) (2.8.2)
Requirement already satisfied: pytz>=2020.1 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from pandas->llama_index<0.9.6) (2023.3.post1)
Requirement already satisfied: tzdata>=2022.1 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from pandas->llama_index<0.9.6) (2023.3)
Requirement already satisfied: h11<0.15,>=0.13 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from httpcore<0.18.0,>=0.15.0->httpx->llama_index<0.9.6) (0.14.0)
Requirement already satisfied: packaging>=17.0 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama_index<0.9.6) (23.2)
Requirement already satisfied: six>=1.5 in /home/loganm/.cache/pypoetry/virtualenvs/llama-index-4a-wkI5X-py3.11/lib/python3.11/site-packages (from python-dateutil>=2.8.2->pandas->llama_index<0.9.6) (1.16.0)
Downloading llama_index-0.9.5-py3-none-any.whl (893 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 893.9/893.9 kB 6.0 MB/s eta 0:00:00a 0:00:01
Installing collected packages: llama_index
  Attempting uninstall: llama_index
    Found existing installation: llama-index 0.9.8.post1
    Uninstalling llama-index-0.9.8.post1:
      Successfully uninstalled llama-index-0.9.8.post1
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
trulens-eval 0.18.0 requires llama-index==0.8.69, but you have llama-index 0.9.5 which is incompatible.
trulens-eval 0.18.0 requires typing-extensions==4.5.0, but you have typing-extensions 4.8.0 which is incompatible.
Successfully installed llama_index-0.9.5

[notice] A new release of pip is available: 23.2.1 -> 23.3.1
[notice] To update, run: pip install --upgrade pip

```

In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.extractors import TitleExtractor, SummaryExtractor
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import MetadataMode


def build_pipeline():
    llm = OpenAI(model="gpt-3.5-turbo-1106", temperature=0.1)

    transformations = [
        SentenceSplitter(chunk_size=1024, chunk_overlap=20),
        TitleExtractor(llm=llm, metadata_mode=MetadataMode.EMBED),
        SummaryExtractor(llm=llm, metadata_mode=MetadataMode.EMBED),
        OpenAIEmbedding(),
    ]

    return IngestionPipeline(transformations=transformations)

```

from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI from llama_index.core.ingestion import IngestionPipeline from llama_index.core.extractors import TitleExtractor, SummaryExtractor from llama_index.core.node_parser import SentenceSplitter from llama_index.core.schema import MetadataMode def build_pipeline(): llm = OpenAI(model="gpt-3.5-turbo-1106", temperature=0.1) transformations = [ SentenceSplitter(chunk_size=1024, chunk_overlap=20), TitleExtractor(llm=llm, metadata_mode=MetadataMode.EMBED), SummaryExtractor(llm=llm, metadata_mode=MetadataMode.EMBED), OpenAIEmbedding(), ] return IngestionPipeline(transformations=transformations)
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham").load_data()
In [ ]:
Copied!
```
import time

times = []
for _ in range(3):
    time.sleep(30)  # help prevent rate-limits/timeouts, keeps each run fair
    pipline = build_pipeline()
    start = time.time()
    nodes = await pipline.arun(documents=documents)
    end = time.time()
    times.append(end - start)

print(f"Average time: {sum(times) / len(times)}")

```

import time times = [] for _ in range(3): time.sleep(30) # help prevent rate-limits/timeouts, keeps each run fair pipline = build_pipeline() start = time.time() nodes = await pipline.arun(documents=documents) end = time.time() times.append(end - start) print(f"Average time: {sum(times) / len(times)}")
```
Extracting titles:   0%|          | 0/5 [00:00<?, ?it/s]
```

```
Extracting summaries:   0%|          | 0/18 [00:00<?, ?it/s]
```

```
Extracting titles:   0%|          | 0/5 [00:00<?, ?it/s]
```

```
Extracting summaries:   0%|          | 0/18 [00:00<?, ?it/s]
```

```
Extracting titles:   0%|          | 0/5 [00:00<?, ?it/s]
```

```
Extracting summaries:   0%|          | 0/18 [00:00<?, ?it/s]
```

```
Average time: 106.17690531412761

```

