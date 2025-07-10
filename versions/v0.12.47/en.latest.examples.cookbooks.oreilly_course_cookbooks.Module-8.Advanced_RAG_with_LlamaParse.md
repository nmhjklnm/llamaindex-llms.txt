# Advanced RAG with LlamaParse
## Building Advanced RAG With LlamaParse¶
In this notebook we will demonstrate the following:
  1. Using LlamaParse.
  2. Using Recursive Retrieval with LlamaParse to query tables/ text within a document hierarchically.


LlamaParse Documentation
#### Installation¶
In [ ]:
Copied!
```
!pip install llama-index
!pip install llama-index-postprocessor-flag-embedding-reranker
!pip install git+https://github.com/FlagOpen/FlagEmbedding.git
!pip install llama-parse

```

!pip install llama-index !pip install llama-index-postprocessor-flag-embedding-reranker !pip install git+https://github.com/FlagOpen/FlagEmbedding.git !pip install llama-parse
```
Collecting llama-index
  Downloading llama_index-0.11.5-py3-none-any.whl.metadata (11 kB)
Collecting llama-index-agent-openai<0.4.0,>=0.3.0 (from llama-index)
  Downloading llama_index_agent_openai-0.3.0-py3-none-any.whl.metadata (728 bytes)
Collecting llama-index-cli<0.4.0,>=0.3.0 (from llama-index)
  Downloading llama_index_cli-0.3.0-py3-none-any.whl.metadata (1.5 kB)
Collecting llama-index-core<0.12.0,>=0.11.5 (from llama-index)
  Downloading llama_index_core-0.11.5-py3-none-any.whl.metadata (2.4 kB)
Collecting llama-index-embeddings-openai<0.3.0,>=0.2.4 (from llama-index)
  Downloading llama_index_embeddings_openai-0.2.4-py3-none-any.whl.metadata (635 bytes)
Collecting llama-index-indices-managed-llama-cloud>=0.3.0 (from llama-index)
  Downloading llama_index_indices_managed_llama_cloud-0.3.0-py3-none-any.whl.metadata (3.8 kB)
Collecting llama-index-legacy<0.10.0,>=0.9.48 (from llama-index)
  Downloading llama_index_legacy-0.9.48.post3-py3-none-any.whl.metadata (8.5 kB)
Collecting llama-index-llms-openai<0.3.0,>=0.2.2 (from llama-index)
  Downloading llama_index_llms_openai-0.2.2-py3-none-any.whl.metadata (705 bytes)
Collecting llama-index-multi-modal-llms-openai<0.3.0,>=0.2.0 (from llama-index)
  Downloading llama_index_multi_modal_llms_openai-0.2.0-py3-none-any.whl.metadata (728 bytes)
Collecting llama-index-program-openai<0.3.0,>=0.2.0 (from llama-index)
  Downloading llama_index_program_openai-0.2.0-py3-none-any.whl.metadata (766 bytes)
Collecting llama-index-question-gen-openai<0.3.0,>=0.2.0 (from llama-index)
  Downloading llama_index_question_gen_openai-0.2.0-py3-none-any.whl.metadata (785 bytes)
Collecting llama-index-readers-file<0.3.0,>=0.2.0 (from llama-index)
  Downloading llama_index_readers_file-0.2.0-py3-none-any.whl.metadata (5.4 kB)
Collecting llama-index-readers-llama-parse>=0.3.0 (from llama-index)
  Downloading llama_index_readers_llama_parse-0.3.0-py3-none-any.whl.metadata (3.5 kB)
Collecting nltk>3.8.1 (from llama-index)
  Downloading nltk-3.9.1-py3-none-any.whl.metadata (2.9 kB)
Collecting openai>=1.14.0 (from llama-index-agent-openai<0.4.0,>=0.3.0->llama-index)
  Downloading openai-1.43.0-py3-none-any.whl.metadata (22 kB)
Requirement already satisfied: PyYAML>=6.0.1 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.5->llama-index) (6.0.1)
Collecting SQLAlchemy>=1.4.49 (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading SQLAlchemy-2.0.34-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (9.6 kB)
Collecting aiohttp<4.0.0,>=3.8.6 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading aiohttp-3.10.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (7.5 kB)
Collecting dataclasses-json (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading dataclasses_json-0.6.7-py3-none-any.whl.metadata (25 kB)
Collecting deprecated>=1.2.9.3 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading Deprecated-1.2.14-py2.py3-none-any.whl.metadata (5.4 kB)
Collecting dirtyjson<2.0.0,>=1.0.8 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading dirtyjson-1.0.8-py3-none-any.whl.metadata (11 kB)
Collecting fsspec>=2023.5.0 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading fsspec-2024.9.0-py3-none-any.whl.metadata (11 kB)
Collecting httpx (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading httpx-0.27.2-py3-none-any.whl.metadata (7.1 kB)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.5->llama-index) (1.5.8)
Requirement already satisfied: networkx>=3.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.5->llama-index) (3.0)
Requirement already satisfied: numpy<2.0.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.5->llama-index) (1.24.1)
Requirement already satisfied: pillow>=9.0.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.5->llama-index) (9.3.0)
Collecting pydantic<3.0.0,>=2.7.0 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading pydantic-2.8.2-py3-none-any.whl.metadata (125 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 125.2/125.2 kB 29.6 MB/s eta 0:00:00
Requirement already satisfied: requests>=2.31.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.5->llama-index) (2.31.0)
Collecting tenacity!=8.4.0,<9.0.0,>=8.2.0 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading tenacity-8.5.0-py3-none-any.whl.metadata (1.2 kB)
Collecting tiktoken>=0.3.3 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading tiktoken-0.7.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
Collecting tqdm<5.0.0,>=4.66.1 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading tqdm-4.66.5-py3-none-any.whl.metadata (57 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 57.6/57.6 kB 24.4 MB/s eta 0:00:00
Collecting typing-extensions>=4.5.0 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading typing_extensions-4.12.2-py3-none-any.whl.metadata (3.0 kB)
Collecting typing-inspect>=0.8.0 (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading typing_inspect-0.9.0-py3-none-any.whl.metadata (1.5 kB)
Collecting wrapt (from llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading wrapt-1.16.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
Collecting llama-cloud>=0.0.11 (from llama-index-indices-managed-llama-cloud>=0.3.0->llama-index)
  Downloading llama_cloud-0.0.15-py3-none-any.whl.metadata (751 bytes)
Collecting pandas (from llama-index-legacy<0.10.0,>=0.9.48->llama-index)
  Downloading pandas-2.2.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (19 kB)
Collecting beautifulsoup4<5.0.0,>=4.12.3 (from llama-index-readers-file<0.3.0,>=0.2.0->llama-index)
  Downloading beautifulsoup4-4.12.3-py3-none-any.whl.metadata (3.8 kB)
Collecting pypdf<5.0.0,>=4.0.1 (from llama-index-readers-file<0.3.0,>=0.2.0->llama-index)
  Downloading pypdf-4.3.1-py3-none-any.whl.metadata (7.4 kB)
Collecting striprtf<0.0.27,>=0.0.26 (from llama-index-readers-file<0.3.0,>=0.2.0->llama-index)
  Downloading striprtf-0.0.26-py3-none-any.whl.metadata (2.1 kB)
Collecting llama-parse>=0.5.0 (from llama-index-readers-llama-parse>=0.3.0->llama-index)
  Downloading llama_parse-0.5.2-py3-none-any.whl.metadata (4.5 kB)
Collecting click (from nltk>3.8.1->llama-index)
  Downloading click-8.1.7-py3-none-any.whl.metadata (3.0 kB)
Collecting joblib (from nltk>3.8.1->llama-index)
  Downloading joblib-1.4.2-py3-none-any.whl.metadata (5.4 kB)
Collecting regex>=2021.8.3 (from nltk>3.8.1->llama-index)
  Downloading regex-2024.7.24-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (40 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 40.5/40.5 kB 12.3 MB/s eta 0:00:00
Collecting aiohappyeyeballs>=2.3.0 (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading aiohappyeyeballs-2.4.0-py3-none-any.whl.metadata (5.9 kB)
Collecting aiosignal>=1.1.2 (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading aiosignal-1.3.1-py3-none-any.whl.metadata (4.0 kB)
Requirement already satisfied: attrs>=17.3.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.5->llama-index) (23.1.0)
Collecting frozenlist>=1.1.1 (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading frozenlist-1.4.1-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (12 kB)
Collecting multidict<7.0,>=4.5 (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading multidict-6.0.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (4.2 kB)
Collecting yarl<2.0,>=1.0 (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading yarl-1.9.11-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (43 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 43.0/43.0 kB 17.7 MB/s eta 0:00:00
Collecting async-timeout<5.0,>=4.0 (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading async_timeout-4.0.3-py3-none-any.whl.metadata (4.2 kB)
Requirement already satisfied: soupsieve>1.2 in /usr/local/lib/python3.10/dist-packages (from beautifulsoup4<5.0.0,>=4.12.3->llama-index-readers-file<0.3.0,>=0.2.0->llama-index) (2.5)
Requirement already satisfied: anyio in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core<0.12.0,>=0.11.5->llama-index) (4.0.0)
Requirement already satisfied: certifi in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core<0.12.0,>=0.11.5->llama-index) (2022.12.7)
Collecting httpcore==1.* (from httpx->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading httpcore-1.0.5-py3-none-any.whl.metadata (20 kB)
Requirement already satisfied: idna in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core<0.12.0,>=0.11.5->llama-index) (3.4)
Requirement already satisfied: sniffio in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core<0.12.0,>=0.11.5->llama-index) (1.3.0)
Collecting h11<0.15,>=0.13 (from httpcore==1.*->httpx->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading h11-0.14.0-py3-none-any.whl.metadata (8.2 kB)
Requirement already satisfied: distro<2,>=1.7.0 in /usr/lib/python3/dist-packages (from openai>=1.14.0->llama-index-agent-openai<0.4.0,>=0.3.0->llama-index) (1.7.0)
Collecting jiter<1,>=0.4.0 (from openai>=1.14.0->llama-index-agent-openai<0.4.0,>=0.3.0->llama-index)
  Downloading jiter-0.5.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.6 kB)
Collecting annotated-types>=0.4.0 (from pydantic<3.0.0,>=2.7.0->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.20.1 (from pydantic<3.0.0,>=2.7.0->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading pydantic_core-2.20.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
Requirement already satisfied: charset-normalizer<4,>=2 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core<0.12.0,>=0.11.5->llama-index) (2.1.1)
Requirement already satisfied: urllib3<3,>=1.21.1 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core<0.12.0,>=0.11.5->llama-index) (1.26.13)
Collecting greenlet!=0.4.17 (from SQLAlchemy>=1.4.49->SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading greenlet-3.0.3-cp310-cp310-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl.metadata (3.8 kB)
Collecting mypy-extensions>=0.3.0 (from typing-inspect>=0.8.0->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading mypy_extensions-1.0.0-py3-none-any.whl.metadata (1.1 kB)
Collecting marshmallow<4.0.0,>=3.18.0 (from dataclasses-json->llama-index-core<0.12.0,>=0.11.5->llama-index)
  Downloading marshmallow-3.22.0-py3-none-any.whl.metadata (7.2 kB)
Requirement already satisfied: python-dateutil>=2.8.2 in /usr/local/lib/python3.10/dist-packages (from pandas->llama-index-legacy<0.10.0,>=0.9.48->llama-index) (2.8.2)
Collecting pytz>=2020.1 (from pandas->llama-index-legacy<0.10.0,>=0.9.48->llama-index)
  Downloading pytz-2024.1-py2.py3-none-any.whl.metadata (22 kB)
Collecting tzdata>=2022.7 (from pandas->llama-index-legacy<0.10.0,>=0.9.48->llama-index)
  Downloading tzdata-2024.1-py2.py3-none-any.whl.metadata (1.4 kB)
Requirement already satisfied: exceptiongroup>=1.0.2 in /usr/local/lib/python3.10/dist-packages (from anyio->httpx->llama-index-core<0.12.0,>=0.11.5->llama-index) (1.1.3)
Requirement already satisfied: packaging>=17.0 in /usr/local/lib/python3.10/dist-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core<0.12.0,>=0.11.5->llama-index) (23.2)
Requirement already satisfied: six>=1.5 in /usr/lib/python3/dist-packages (from python-dateutil>=2.8.2->pandas->llama-index-legacy<0.10.0,>=0.9.48->llama-index) (1.16.0)
Downloading llama_index-0.11.5-py3-none-any.whl (6.8 kB)
Downloading llama_index_agent_openai-0.3.0-py3-none-any.whl (13 kB)
Downloading llama_index_cli-0.3.0-py3-none-any.whl (27 kB)
Downloading llama_index_core-0.11.5-py3-none-any.whl (1.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.6/1.6 MB 111.3 MB/s eta 0:00:00
Downloading llama_index_embeddings_openai-0.2.4-py3-none-any.whl (6.1 kB)
Downloading llama_index_indices_managed_llama_cloud-0.3.0-py3-none-any.whl (9.5 kB)
Downloading llama_index_legacy-0.9.48.post3-py3-none-any.whl (1.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 96.6 MB/s eta 0:00:00
Downloading llama_index_llms_openai-0.2.2-py3-none-any.whl (12 kB)
Downloading llama_index_multi_modal_llms_openai-0.2.0-py3-none-any.whl (5.9 kB)
Downloading llama_index_program_openai-0.2.0-py3-none-any.whl (5.3 kB)
Downloading llama_index_question_gen_openai-0.2.0-py3-none-any.whl (2.9 kB)
Downloading llama_index_readers_file-0.2.0-py3-none-any.whl (38 kB)
Downloading llama_index_readers_llama_parse-0.3.0-py3-none-any.whl (2.5 kB)
Downloading nltk-3.9.1-py3-none-any.whl (1.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.5/1.5 MB 103.2 MB/s eta 0:00:00
Downloading aiohttp-3.10.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.2/1.2 MB 102.9 MB/s eta 0:00:00
Downloading beautifulsoup4-4.12.3-py3-none-any.whl (147 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 147.9/147.9 kB 42.6 MB/s eta 0:00:00
Downloading Deprecated-1.2.14-py2.py3-none-any.whl (9.6 kB)
Downloading dirtyjson-1.0.8-py3-none-any.whl (25 kB)
Downloading fsspec-2024.9.0-py3-none-any.whl (179 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 179.3/179.3 kB 43.2 MB/s eta 0:00:00
Downloading llama_cloud-0.0.15-py3-none-any.whl (180 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 180.2/180.2 kB 45.8 MB/s eta 0:00:00
Downloading httpx-0.27.2-py3-none-any.whl (76 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 76.4/76.4 kB 36.8 MB/s eta 0:00:00
Downloading httpcore-1.0.5-py3-none-any.whl (77 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 77.9/77.9 kB 22.5 MB/s eta 0:00:00
Downloading llama_parse-0.5.2-py3-none-any.whl (9.5 kB)
Downloading openai-1.43.0-py3-none-any.whl (365 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 365.7/365.7 kB 72.7 MB/s eta 0:00:00
Downloading pydantic-2.8.2-py3-none-any.whl (423 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 423.9/423.9 kB 102.7 MB/s eta 0:00:00
Downloading pydantic_core-2.20.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (2.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2.1/2.1 MB 102.0 MB/s eta 0:00:00
Downloading pypdf-4.3.1-py3-none-any.whl (295 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 295.8/295.8 kB 60.4 MB/s eta 0:00:00
Downloading regex-2024.7.24-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (776 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 776.5/776.5 kB 104.0 MB/s eta 0:00:00
Downloading SQLAlchemy-2.0.34-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (3.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.1/3.1 MB 104.5 MB/s eta 0:00:00
Downloading striprtf-0.0.26-py3-none-any.whl (6.9 kB)
Downloading tenacity-8.5.0-py3-none-any.whl (28 kB)
Downloading tiktoken-0.7.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (1.1 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 1.1/1.1 MB 92.9 MB/s eta 0:00:00
Downloading tqdm-4.66.5-py3-none-any.whl (78 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 78.4/78.4 kB 21.9 MB/s eta 0:00:00
Downloading typing_extensions-4.12.2-py3-none-any.whl (37 kB)
Downloading typing_inspect-0.9.0-py3-none-any.whl (8.8 kB)
Downloading wrapt-1.16.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (80 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 80.3/80.3 kB 25.1 MB/s eta 0:00:00
Downloading click-8.1.7-py3-none-any.whl (97 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 97.9/97.9 kB 32.5 MB/s eta 0:00:00
Downloading dataclasses_json-0.6.7-py3-none-any.whl (28 kB)
Downloading joblib-1.4.2-py3-none-any.whl (301 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 301.8/301.8 kB 85.3 MB/s eta 0:00:00
Downloading pandas-2.2.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (13.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 13.0/13.0 MB 90.8 MB/s eta 0:00:00ta 0:00:01
Downloading aiohappyeyeballs-2.4.0-py3-none-any.whl (12 kB)
Downloading aiosignal-1.3.1-py3-none-any.whl (7.6 kB)
Downloading annotated_types-0.7.0-py3-none-any.whl (13 kB)
Downloading async_timeout-4.0.3-py3-none-any.whl (5.7 kB)
Downloading frozenlist-1.4.1-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (239 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 239.5/239.5 kB 59.9 MB/s eta 0:00:00
Downloading greenlet-3.0.3-cp310-cp310-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl (616 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 616.0/616.0 kB 112.1 MB/s eta 0:00:00
Downloading jiter-0.5.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (318 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 318.9/318.9 kB 103.0 MB/s eta 0:00:00
Downloading marshmallow-3.22.0-py3-none-any.whl (49 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 49.3/49.3 kB 15.5 MB/s eta 0:00:00
Downloading multidict-6.0.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (124 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 124.3/124.3 kB 53.9 MB/s eta 0:00:00
Downloading mypy_extensions-1.0.0-py3-none-any.whl (4.7 kB)
Downloading pytz-2024.1-py2.py3-none-any.whl (505 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 505.5/505.5 kB 106.5 MB/s eta 0:00:00
Downloading tzdata-2024.1-py2.py3-none-any.whl (345 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 345.4/345.4 kB 92.3 MB/s eta 0:00:00
Downloading yarl-1.9.11-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (468 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 468.3/468.3 kB 72.9 MB/s eta 0:00:00
Downloading h11-0.14.0-py3-none-any.whl (58 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 58.3/58.3 kB 27.2 MB/s eta 0:00:00
Installing collected packages: striprtf, pytz, dirtyjson, wrapt, tzdata, typing-extensions, tqdm, tenacity, regex, mypy-extensions, multidict, marshmallow, joblib, jiter, h11, greenlet, fsspec, frozenlist, click, beautifulsoup4, async-timeout, annotated-types, aiohappyeyeballs, yarl, typing-inspect, tiktoken, SQLAlchemy, pypdf, pydantic-core, pandas, nltk, httpcore, deprecated, aiosignal, pydantic, httpx, dataclasses-json, aiohttp, openai, llama-index-core, llama-cloud, llama-parse, llama-index-readers-file, llama-index-legacy, llama-index-indices-managed-llama-cloud, llama-index-embeddings-openai, llama-index-readers-llama-parse, llama-index-llms-openai, llama-index-agent-openai, llama-index-program-openai, llama-index-question-gen-openai, llama-index-multi-modal-llms-openai, llama-index-cli, llama-index
  Attempting uninstall: typing-extensions
    Found existing installation: typing_extensions 4.4.0
    Uninstalling typing_extensions-4.4.0:
      Successfully uninstalled typing_extensions-4.4.0
  Attempting uninstall: fsspec
    Found existing installation: fsspec 2023.4.0
    Uninstalling fsspec-2023.4.0:
      Successfully uninstalled fsspec-2023.4.0
  Attempting uninstall: beautifulsoup4
    Found existing installation: beautifulsoup4 4.12.2
    Uninstalling beautifulsoup4-4.12.2:
      Successfully uninstalled beautifulsoup4-4.12.2
Successfully installed SQLAlchemy-2.0.34 aiohappyeyeballs-2.4.0 aiohttp-3.10.5 aiosignal-1.3.1 annotated-types-0.7.0 async-timeout-4.0.3 beautifulsoup4-4.12.3 click-8.1.7 dataclasses-json-0.6.7 deprecated-1.2.14 dirtyjson-1.0.8 frozenlist-1.4.1 fsspec-2024.9.0 greenlet-3.0.3 h11-0.14.0 httpcore-1.0.5 httpx-0.27.2 jiter-0.5.0 joblib-1.4.2 llama-cloud-0.0.15 llama-index-0.11.5 llama-index-agent-openai-0.3.0 llama-index-cli-0.3.0 llama-index-core-0.11.5 llama-index-embeddings-openai-0.2.4 llama-index-indices-managed-llama-cloud-0.3.0 llama-index-legacy-0.9.48.post3 llama-index-llms-openai-0.2.2 llama-index-multi-modal-llms-openai-0.2.0 llama-index-program-openai-0.2.0 llama-index-question-gen-openai-0.2.0 llama-index-readers-file-0.2.0 llama-index-readers-llama-parse-0.3.0 llama-parse-0.5.2 marshmallow-3.22.0 multidict-6.0.5 mypy-extensions-1.0.0 nltk-3.9.1 openai-1.43.0 pandas-2.2.2 pydantic-2.8.2 pydantic-core-2.20.1 pypdf-4.3.1 pytz-2024.1 regex-2024.7.24 striprtf-0.0.26 tenacity-8.5.0 tiktoken-0.7.0 tqdm-4.66.5 typing-extensions-4.12.2 typing-inspect-0.9.0 tzdata-2024.1 wrapt-1.16.0 yarl-1.9.11
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

[notice] A new release of pip is available: 23.3.1 -> 24.2
[notice] To update, run: python -m pip install --upgrade pip
Collecting llama-index-postprocessor-flag-embedding-reranker
  Downloading llama_index_postprocessor_flag_embedding_reranker-0.2.0-py3-none-any.whl.metadata (714 bytes)
Requirement already satisfied: llama-index-core<0.12.0,>=0.11.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-postprocessor-flag-embedding-reranker) (0.11.5)
Requirement already satisfied: PyYAML>=6.0.1 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /usr/local/lib/python3.10/dist-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2.0.34)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (3.10.5)
Requirement already satisfied: dataclasses-json in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (0.6.7)
Requirement already satisfied: deprecated>=1.2.9.3 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2024.9.0)
Requirement already satisfied: httpx in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (0.27.2)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.5.8)
Requirement already satisfied: networkx>=3.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (3.0)
Requirement already satisfied: nltk>3.8.1 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (3.9.1)
Requirement already satisfied: numpy<2.0.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.24.1)
Requirement already satisfied: pillow>=9.0.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (9.3.0)
Requirement already satisfied: pydantic<3.0.0,>=2.7.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2.8.2)
Requirement already satisfied: requests>=2.31.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2.31.0)
Requirement already satisfied: tenacity!=8.4.0,<9.0.0,>=8.2.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (8.5.0)
Requirement already satisfied: tiktoken>=0.3.3 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (0.7.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (4.66.5)
Requirement already satisfied: typing-extensions>=4.5.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (4.12.2)
Requirement already satisfied: typing-inspect>=0.8.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (0.9.0)
Requirement already satisfied: wrapt in /usr/local/lib/python3.10/dist-packages (from llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.16.0)
Requirement already satisfied: aiohappyeyeballs>=2.3.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2.4.0)
Requirement already satisfied: aiosignal>=1.1.2 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (23.1.0)
Requirement already satisfied: frozenlist>=1.1.1 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.9.11)
Requirement already satisfied: async-timeout<5.0,>=4.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (4.0.3)
Requirement already satisfied: click in /usr/local/lib/python3.10/dist-packages (from nltk>3.8.1->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (8.1.7)
Requirement already satisfied: joblib in /usr/local/lib/python3.10/dist-packages (from nltk>3.8.1->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.4.2)
Requirement already satisfied: regex>=2021.8.3 in /usr/local/lib/python3.10/dist-packages (from nltk>3.8.1->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2024.7.24)
Requirement already satisfied: annotated-types>=0.4.0 in /usr/local/lib/python3.10/dist-packages (from pydantic<3.0.0,>=2.7.0->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (0.7.0)
Requirement already satisfied: pydantic-core==2.20.1 in /usr/local/lib/python3.10/dist-packages (from pydantic<3.0.0,>=2.7.0->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2.20.1)
Requirement already satisfied: charset-normalizer<4,>=2 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2.1.1)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (3.4)
Requirement already satisfied: urllib3<3,>=1.21.1 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.26.13)
Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (2022.12.7)
Requirement already satisfied: greenlet!=0.4.17 in /usr/local/lib/python3.10/dist-packages (from SQLAlchemy>=1.4.49->SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /usr/local/lib/python3.10/dist-packages (from typing-inspect>=0.8.0->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /usr/local/lib/python3.10/dist-packages (from dataclasses-json->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (3.22.0)
Requirement already satisfied: anyio in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (4.0.0)
Requirement already satisfied: httpcore==1.* in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.0.5)
Requirement already satisfied: sniffio in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.3.0)
Requirement already satisfied: h11<0.15,>=0.13 in /usr/local/lib/python3.10/dist-packages (from httpcore==1.*->httpx->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (0.14.0)
Requirement already satisfied: packaging>=17.0 in /usr/local/lib/python3.10/dist-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (23.2)
Requirement already satisfied: exceptiongroup>=1.0.2 in /usr/local/lib/python3.10/dist-packages (from anyio->httpx->llama-index-core<0.12.0,>=0.11.0->llama-index-postprocessor-flag-embedding-reranker) (1.1.3)
Downloading llama_index_postprocessor_flag_embedding_reranker-0.2.0-py3-none-any.whl (3.0 kB)
Installing collected packages: llama-index-postprocessor-flag-embedding-reranker
Successfully installed llama-index-postprocessor-flag-embedding-reranker-0.2.0
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

[notice] A new release of pip is available: 23.3.1 -> 24.2
[notice] To update, run: python -m pip install --upgrade pip
Collecting git+https://github.com/FlagOpen/FlagEmbedding.git
  Cloning https://github.com/FlagOpen/FlagEmbedding.git to /tmp/pip-req-build-g7g78sb6
  Running command git clone --filter=blob:none --quiet https://github.com/FlagOpen/FlagEmbedding.git /tmp/pip-req-build-g7g78sb6
  Resolved https://github.com/FlagOpen/FlagEmbedding.git to commit ddad0f9cb9a46be41fdb5d9cde47cfedf2e43241
  Preparing metadata (setup.py) ... done
Requirement already satisfied: torch>=1.6.0 in /usr/local/lib/python3.10/dist-packages (from FlagEmbedding==1.2.11) (2.1.0+cu118)
Collecting transformers>=4.33.0 (from FlagEmbedding==1.2.11)
  Downloading transformers-4.44.2-py3-none-any.whl.metadata (43 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 43.7/43.7 kB 2.2 MB/s eta 0:00:00
Collecting datasets (from FlagEmbedding==1.2.11)
  Downloading datasets-2.21.0-py3-none-any.whl.metadata (21 kB)
Collecting accelerate>=0.20.1 (from FlagEmbedding==1.2.11)
  Downloading accelerate-0.34.0-py3-none-any.whl.metadata (19 kB)
Collecting sentence_transformers (from FlagEmbedding==1.2.11)
  Downloading sentence_transformers-3.0.1-py3-none-any.whl.metadata (10 kB)
Collecting peft (from FlagEmbedding==1.2.11)
  Downloading peft-0.12.0-py3-none-any.whl.metadata (13 kB)
Requirement already satisfied: numpy<3.0.0,>=1.17 in /usr/local/lib/python3.10/dist-packages (from accelerate>=0.20.1->FlagEmbedding==1.2.11) (1.24.1)
Requirement already satisfied: packaging>=20.0 in /usr/local/lib/python3.10/dist-packages (from accelerate>=0.20.1->FlagEmbedding==1.2.11) (23.2)
Requirement already satisfied: psutil in /usr/local/lib/python3.10/dist-packages (from accelerate>=0.20.1->FlagEmbedding==1.2.11) (5.9.6)
Requirement already satisfied: pyyaml in /usr/local/lib/python3.10/dist-packages (from accelerate>=0.20.1->FlagEmbedding==1.2.11) (6.0.1)
Collecting huggingface-hub>=0.21.0 (from accelerate>=0.20.1->FlagEmbedding==1.2.11)
  Downloading huggingface_hub-0.24.6-py3-none-any.whl.metadata (13 kB)
Collecting safetensors>=0.4.3 (from accelerate>=0.20.1->FlagEmbedding==1.2.11)
  Downloading safetensors-0.4.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.8 kB)
Requirement already satisfied: filelock in /usr/local/lib/python3.10/dist-packages (from torch>=1.6.0->FlagEmbedding==1.2.11) (3.9.0)
Requirement already satisfied: typing-extensions in /usr/local/lib/python3.10/dist-packages (from torch>=1.6.0->FlagEmbedding==1.2.11) (4.12.2)
Requirement already satisfied: sympy in /usr/local/lib/python3.10/dist-packages (from torch>=1.6.0->FlagEmbedding==1.2.11) (1.12)
Requirement already satisfied: networkx in /usr/local/lib/python3.10/dist-packages (from torch>=1.6.0->FlagEmbedding==1.2.11) (3.0)
Requirement already satisfied: jinja2 in /usr/local/lib/python3.10/dist-packages (from torch>=1.6.0->FlagEmbedding==1.2.11) (3.1.2)
Requirement already satisfied: fsspec in /usr/local/lib/python3.10/dist-packages (from torch>=1.6.0->FlagEmbedding==1.2.11) (2024.9.0)
Requirement already satisfied: triton==2.1.0 in /usr/local/lib/python3.10/dist-packages (from torch>=1.6.0->FlagEmbedding==1.2.11) (2.1.0)
Requirement already satisfied: regex!=2019.12.17 in /usr/local/lib/python3.10/dist-packages (from transformers>=4.33.0->FlagEmbedding==1.2.11) (2024.7.24)
Requirement already satisfied: requests in /usr/local/lib/python3.10/dist-packages (from transformers>=4.33.0->FlagEmbedding==1.2.11) (2.31.0)
Collecting tokenizers<0.20,>=0.19 (from transformers>=4.33.0->FlagEmbedding==1.2.11)
  Downloading tokenizers-0.19.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.7 kB)
Requirement already satisfied: tqdm>=4.27 in /usr/local/lib/python3.10/dist-packages (from transformers>=4.33.0->FlagEmbedding==1.2.11) (4.66.5)
Collecting pyarrow>=15.0.0 (from datasets->FlagEmbedding==1.2.11)
  Downloading pyarrow-17.0.0-cp310-cp310-manylinux_2_28_x86_64.whl.metadata (3.3 kB)
Collecting dill<0.3.9,>=0.3.0 (from datasets->FlagEmbedding==1.2.11)
  Downloading dill-0.3.8-py3-none-any.whl.metadata (10 kB)
Requirement already satisfied: pandas in /usr/local/lib/python3.10/dist-packages (from datasets->FlagEmbedding==1.2.11) (2.2.2)
Collecting requests (from transformers>=4.33.0->FlagEmbedding==1.2.11)
  Downloading requests-2.32.3-py3-none-any.whl.metadata (4.6 kB)
Collecting xxhash (from datasets->FlagEmbedding==1.2.11)
  Downloading xxhash-3.5.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (12 kB)
Collecting multiprocess (from datasets->FlagEmbedding==1.2.11)
  Downloading multiprocess-0.70.16-py310-none-any.whl.metadata (7.2 kB)
Collecting fsspec (from torch>=1.6.0->FlagEmbedding==1.2.11)
  Downloading fsspec-2024.6.1-py3-none-any.whl.metadata (11 kB)
Requirement already satisfied: aiohttp in /usr/local/lib/python3.10/dist-packages (from datasets->FlagEmbedding==1.2.11) (3.10.5)
Collecting scikit-learn (from sentence_transformers->FlagEmbedding==1.2.11)
  Downloading scikit_learn-1.5.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (12 kB)
Collecting scipy (from sentence_transformers->FlagEmbedding==1.2.11)
  Downloading scipy-1.14.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (60 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 60.8/60.8 kB 29.0 MB/s eta 0:00:00
Requirement already satisfied: Pillow in /usr/local/lib/python3.10/dist-packages (from sentence_transformers->FlagEmbedding==1.2.11) (9.3.0)
Requirement already satisfied: aiohappyeyeballs>=2.3.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp->datasets->FlagEmbedding==1.2.11) (2.4.0)
Requirement already satisfied: aiosignal>=1.1.2 in /usr/local/lib/python3.10/dist-packages (from aiohttp->datasets->FlagEmbedding==1.2.11) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp->datasets->FlagEmbedding==1.2.11) (23.1.0)
Requirement already satisfied: frozenlist>=1.1.1 in /usr/local/lib/python3.10/dist-packages (from aiohttp->datasets->FlagEmbedding==1.2.11) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /usr/local/lib/python3.10/dist-packages (from aiohttp->datasets->FlagEmbedding==1.2.11) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp->datasets->FlagEmbedding==1.2.11) (1.9.11)
Requirement already satisfied: async-timeout<5.0,>=4.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp->datasets->FlagEmbedding==1.2.11) (4.0.3)
Requirement already satisfied: charset-normalizer<4,>=2 in /usr/local/lib/python3.10/dist-packages (from requests->transformers>=4.33.0->FlagEmbedding==1.2.11) (2.1.1)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.10/dist-packages (from requests->transformers>=4.33.0->FlagEmbedding==1.2.11) (3.4)
Requirement already satisfied: urllib3<3,>=1.21.1 in /usr/local/lib/python3.10/dist-packages (from requests->transformers>=4.33.0->FlagEmbedding==1.2.11) (1.26.13)
Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.10/dist-packages (from requests->transformers>=4.33.0->FlagEmbedding==1.2.11) (2022.12.7)
Requirement already satisfied: MarkupSafe>=2.0 in /usr/local/lib/python3.10/dist-packages (from jinja2->torch>=1.6.0->FlagEmbedding==1.2.11) (2.1.2)
Requirement already satisfied: python-dateutil>=2.8.2 in /usr/local/lib/python3.10/dist-packages (from pandas->datasets->FlagEmbedding==1.2.11) (2.8.2)
Requirement already satisfied: pytz>=2020.1 in /usr/local/lib/python3.10/dist-packages (from pandas->datasets->FlagEmbedding==1.2.11) (2024.1)
Requirement already satisfied: tzdata>=2022.7 in /usr/local/lib/python3.10/dist-packages (from pandas->datasets->FlagEmbedding==1.2.11) (2024.1)
Requirement already satisfied: joblib>=1.2.0 in /usr/local/lib/python3.10/dist-packages (from scikit-learn->sentence_transformers->FlagEmbedding==1.2.11) (1.4.2)
Collecting threadpoolctl>=3.1.0 (from scikit-learn->sentence_transformers->FlagEmbedding==1.2.11)
  Downloading threadpoolctl-3.5.0-py3-none-any.whl.metadata (13 kB)
Requirement already satisfied: mpmath>=0.19 in /usr/local/lib/python3.10/dist-packages (from sympy->torch>=1.6.0->FlagEmbedding==1.2.11) (1.3.0)
Requirement already satisfied: six>=1.5 in /usr/lib/python3/dist-packages (from python-dateutil>=2.8.2->pandas->datasets->FlagEmbedding==1.2.11) (1.16.0)
Downloading accelerate-0.34.0-py3-none-any.whl (324 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 324.3/324.3 kB 47.4 MB/s eta 0:00:00
Downloading transformers-4.44.2-py3-none-any.whl (9.5 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 9.5/9.5 MB 98.4 MB/s eta 0:00:00ta 0:00:01
Downloading datasets-2.21.0-py3-none-any.whl (527 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 527.3/527.3 kB 93.9 MB/s eta 0:00:00
Downloading peft-0.12.0-py3-none-any.whl (296 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 296.4/296.4 kB 57.9 MB/s eta 0:00:00
Downloading sentence_transformers-3.0.1-py3-none-any.whl (227 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 227.1/227.1 kB 49.7 MB/s eta 0:00:00
Downloading dill-0.3.8-py3-none-any.whl (116 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 116.3/116.3 kB 31.4 MB/s eta 0:00:00
Downloading fsspec-2024.6.1-py3-none-any.whl (177 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 177.6/177.6 kB 43.2 MB/s eta 0:00:00
Downloading huggingface_hub-0.24.6-py3-none-any.whl (417 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 417.5/417.5 kB 84.8 MB/s eta 0:00:00
Downloading pyarrow-17.0.0-cp310-cp310-manylinux_2_28_x86_64.whl (39.9 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 39.9/39.9 MB 78.9 MB/s eta 0:00:00:00:0100:01
Downloading requests-2.32.3-py3-none-any.whl (64 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 64.9/64.9 kB 22.1 MB/s eta 0:00:00
Downloading safetensors-0.4.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (435 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 435.5/435.5 kB 78.8 MB/s eta 0:00:00
Downloading tokenizers-0.19.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (3.6 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 3.6/3.6 MB 97.8 MB/s eta 0:00:00:00:01
Downloading multiprocess-0.70.16-py310-none-any.whl (134 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 134.8/134.8 kB 53.1 MB/s eta 0:00:00
Downloading scikit_learn-1.5.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (13.4 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 13.4/13.4 MB 94.4 MB/s eta 0:00:00ta 0:00:01
Downloading scipy-1.14.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (41.2 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 41.2/41.2 MB 74.2 MB/s eta 0:00:00:00:0100:01
Downloading xxhash-3.5.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (194 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 194.1/194.1 kB 57.2 MB/s eta 0:00:00
Downloading threadpoolctl-3.5.0-py3-none-any.whl (18 kB)
Building wheels for collected packages: FlagEmbedding
  Building wheel for FlagEmbedding (setup.py) ... done
  Created wheel for FlagEmbedding: filename=FlagEmbedding-1.2.11-py3-none-any.whl size=1532999 sha256=e8fdb11999cd20961dbf8a2cdca1f2a8e9daae60c7ace5a2181e529e49f69801
  Stored in directory: /tmp/pip-ephem-wheel-cache-0w5j143m/wheels/41/cf/a5/5dee96ed64e5aaffe5aa3d583828258fdefed9a305db6e7f48
Successfully built FlagEmbedding
Installing collected packages: xxhash, threadpoolctl, scipy, safetensors, requests, pyarrow, fsspec, dill, scikit-learn, multiprocess, huggingface-hub, tokenizers, accelerate, transformers, datasets, sentence_transformers, peft, FlagEmbedding
  Attempting uninstall: requests
    Found existing installation: requests 2.31.0
    Uninstalling requests-2.31.0:
      Successfully uninstalled requests-2.31.0
  Attempting uninstall: fsspec
    Found existing installation: fsspec 2024.9.0
    Uninstalling fsspec-2024.9.0:
      Successfully uninstalled fsspec-2024.9.0
Successfully installed FlagEmbedding-1.2.11 accelerate-0.34.0 datasets-2.21.0 dill-0.3.8 fsspec-2024.6.1 huggingface-hub-0.24.6 multiprocess-0.70.16 peft-0.12.0 pyarrow-17.0.0 requests-2.32.3 safetensors-0.4.4 scikit-learn-1.5.1 scipy-1.14.1 sentence_transformers-3.0.1 threadpoolctl-3.5.0 tokenizers-0.19.1 transformers-4.44.2 xxhash-3.5.0
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

[notice] A new release of pip is available: 23.3.1 -> 24.2
[notice] To update, run: python -m pip install --upgrade pip
Requirement already satisfied: llama-parse in /usr/local/lib/python3.10/dist-packages (0.5.2)
Requirement already satisfied: llama-index-core>=0.11.0 in /usr/local/lib/python3.10/dist-packages (from llama-parse) (0.11.5)
Requirement already satisfied: PyYAML>=6.0.1 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /usr/local/lib/python3.10/dist-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core>=0.11.0->llama-parse) (2.0.34)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (3.10.5)
Requirement already satisfied: dataclasses-json in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (0.6.7)
Requirement already satisfied: deprecated>=1.2.9.3 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (2024.6.1)
Requirement already satisfied: httpx in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (0.27.2)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (1.5.8)
Requirement already satisfied: networkx>=3.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (3.0)
Requirement already satisfied: nltk>3.8.1 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (3.9.1)
Requirement already satisfied: numpy<2.0.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (1.24.1)
Requirement already satisfied: pillow>=9.0.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (9.3.0)
Requirement already satisfied: pydantic<3.0.0,>=2.7.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (2.8.2)
Requirement already satisfied: requests>=2.31.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (2.32.3)
Requirement already satisfied: tenacity!=8.4.0,<9.0.0,>=8.2.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (8.5.0)
Requirement already satisfied: tiktoken>=0.3.3 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (0.7.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (4.66.5)
Requirement already satisfied: typing-extensions>=4.5.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (4.12.2)
Requirement already satisfied: typing-inspect>=0.8.0 in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (0.9.0)
Requirement already satisfied: wrapt in /usr/local/lib/python3.10/dist-packages (from llama-index-core>=0.11.0->llama-parse) (1.16.0)
Requirement already satisfied: aiohappyeyeballs>=2.3.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core>=0.11.0->llama-parse) (2.4.0)
Requirement already satisfied: aiosignal>=1.1.2 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core>=0.11.0->llama-parse) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core>=0.11.0->llama-parse) (23.1.0)
Requirement already satisfied: frozenlist>=1.1.1 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core>=0.11.0->llama-parse) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core>=0.11.0->llama-parse) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core>=0.11.0->llama-parse) (1.9.11)
Requirement already satisfied: async-timeout<5.0,>=4.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core>=0.11.0->llama-parse) (4.0.3)
Requirement already satisfied: click in /usr/local/lib/python3.10/dist-packages (from nltk>3.8.1->llama-index-core>=0.11.0->llama-parse) (8.1.7)
Requirement already satisfied: joblib in /usr/local/lib/python3.10/dist-packages (from nltk>3.8.1->llama-index-core>=0.11.0->llama-parse) (1.4.2)
Requirement already satisfied: regex>=2021.8.3 in /usr/local/lib/python3.10/dist-packages (from nltk>3.8.1->llama-index-core>=0.11.0->llama-parse) (2024.7.24)
Requirement already satisfied: annotated-types>=0.4.0 in /usr/local/lib/python3.10/dist-packages (from pydantic<3.0.0,>=2.7.0->llama-index-core>=0.11.0->llama-parse) (0.7.0)
Requirement already satisfied: pydantic-core==2.20.1 in /usr/local/lib/python3.10/dist-packages (from pydantic<3.0.0,>=2.7.0->llama-index-core>=0.11.0->llama-parse) (2.20.1)
Requirement already satisfied: charset-normalizer<4,>=2 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core>=0.11.0->llama-parse) (2.1.1)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core>=0.11.0->llama-parse) (3.4)
Requirement already satisfied: urllib3<3,>=1.21.1 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core>=0.11.0->llama-parse) (1.26.13)
Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.10/dist-packages (from requests>=2.31.0->llama-index-core>=0.11.0->llama-parse) (2022.12.7)
Requirement already satisfied: greenlet!=0.4.17 in /usr/local/lib/python3.10/dist-packages (from SQLAlchemy>=1.4.49->SQLAlchemy[asyncio]>=1.4.49->llama-index-core>=0.11.0->llama-parse) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /usr/local/lib/python3.10/dist-packages (from typing-inspect>=0.8.0->llama-index-core>=0.11.0->llama-parse) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /usr/local/lib/python3.10/dist-packages (from dataclasses-json->llama-index-core>=0.11.0->llama-parse) (3.22.0)
Requirement already satisfied: anyio in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core>=0.11.0->llama-parse) (4.0.0)
Requirement already satisfied: httpcore==1.* in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core>=0.11.0->llama-parse) (1.0.5)
Requirement already satisfied: sniffio in /usr/local/lib/python3.10/dist-packages (from httpx->llama-index-core>=0.11.0->llama-parse) (1.3.0)
Requirement already satisfied: h11<0.15,>=0.13 in /usr/local/lib/python3.10/dist-packages (from httpcore==1.*->httpx->llama-index-core>=0.11.0->llama-parse) (0.14.0)
Requirement already satisfied: packaging>=17.0 in /usr/local/lib/python3.10/dist-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core>=0.11.0->llama-parse) (23.2)
Requirement already satisfied: exceptiongroup>=1.0.2 in /usr/local/lib/python3.10/dist-packages (from anyio->httpx->llama-index-core>=0.11.0->llama-parse) (1.1.3)
WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv

[notice] A new release of pip is available: 23.3.1 -> 24.2
[notice] To update, run: python -m pip install --upgrade pip

```

#### Download Data¶
In [ ]:
Copied!
```
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_march_2022.pdf' -O './uber_10q_march_2022.pdf'

```

!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_march_2022.pdf' -O './uber_10q_march_2022.pdf'
```
--2024-09-05 07:01:47--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/10q/uber_10q_march_2022.pdf
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.109.133, 185.199.108.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1260185 (1.2M) [application/octet-stream]
Saving to: ‘./uber_10q_march_2022.pdf’

./uber_10q_march_20 100%[===================>]   1.20M  --.-KB/s    in 0.02s   

2024-09-05 07:01:48 (77.6 MB/s) - ‘./uber_10q_march_2022.pdf’ saved [1260185/1260185]


```

#### Setting API Keys¶
In [ ]:
Copied!
```
# llama-parse is async-first, running the async code in a notebook requires the use of nest_asyncio
import nest_asyncio

nest_asyncio.apply()

import os

# API access to llama-cloud
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-..."

# Using OpenAI API for embeddings/llms
os.environ["OPENAI_API_KEY"] = "sk-..."

```

# llama-parse is async-first, running the async code in a notebook requires the use of nest_asyncio import nest_asyncio nest_asyncio.apply() import os # API access to llama-cloud os.environ["LLAMA_CLOUD_API_KEY"] = "llx-..." # Using OpenAI API for embeddings/llms os.environ["OPENAI_API_KEY"] = "sk-..."
#### Setting LLM and Embedding Model¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.core import Settings

embed_model = OpenAIEmbedding(model="text-embedding-3-small")
llm = OpenAI(model="gpt-3.5-turbo-0125")

Settings.llm = llm
Settings.embed_model = embed_model

```

from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import VectorStoreIndex from llama_index.core import Settings embed_model = OpenAIEmbedding(model="text-embedding-3-small") llm = OpenAI(model="gpt-3.5-turbo-0125") Settings.llm = llm Settings.embed_model = embed_model
#### LlamaParse PDF reader for PDF Parsing¶
We compare two different retrieval/ queryengine strategies.
  1. Using raw Markdown text as nodes for building index and applying a simple query engine for generating results.
  2. Using MarkdownElementNodeParser for parsing the LlamaParse output Markdown results and building a recursive retriever query engine for generation.


In [ ]:
Copied!
```
# LlamaParse PDF reader for PDF Parsing
from llama_parse import LlamaParse

documents = LlamaParse(result_type="markdown").load_data(
    "./uber_10q_march_2022.pdf"
)
# Started parsing the file under job_id b76a572b-d2bb-42ae-bad9-b9810049f1af

```

# LlamaParse PDF reader for PDF Parsing from llama_parse import LlamaParse documents = LlamaParse(result_type="markdown").load_data( "./uber_10q_march_2022.pdf" ) # Started parsing the file under job_id b76a572b-d2bb-42ae-bad9-b9810049f1af
```
Started parsing the file under job_id 0ef2f65b-9cab-4ca8-b221-d20f1f6d1336

```

In [ ]:
Copied!
```
print(documents[0].text[:1000] + "...")

```

print(documents[0].text[:1000] + "...")
```
# UNITED STATES SECURITIES AND EXCHANGE COMMISSION

# Washington, D.C. 20549

# FORM 10-Q

(Mark One)

☒ QUARTERLY REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

For the quarterly period ended March 31, 2022

OR

☐ TRANSITION REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

For the transition period from_____ to _____

Commission File Number: 001-38902

# UBER TECHNOLOGIES, INC.

(Exact name of registrant as specified in its charter)

Not Applicable

(Former name, former address and former fiscal year, if changed since last report)

|Delaware|45-2647441|
|---|---|
|(State or other jurisdiction of incorporation or organization)|(I.R.S. Employer Identification No.)|
|1515 3rd Street|San Francisco, California 94158|
|(Address of principal executive offices, including zip code)|(415) 612-8582|
|(Registrant’s telephone number, including area code)| |

# Securities registered pursuant to Section 12(b) of the Act:

|Title of each c...

```

In [ ]:
Copied!
```
from llama_index.core.node_parser import MarkdownElementNodeParser

node_parser = MarkdownElementNodeParser(
    llm=OpenAI(model="gpt-3.5-turbo-0125"), num_workers=8
)

nodes = node_parser.get_nodes_from_documents(documents)

```

from llama_index.core.node_parser import MarkdownElementNodeParser node_parser = MarkdownElementNodeParser( llm=OpenAI(model="gpt-3.5-turbo-0125"), num_workers=8 ) nodes = node_parser.get_nodes_from_documents(documents)
```
3it [00:00, 41803.69it/s]
1it [00:00, 22310.13it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
1it [00:00, 20867.18it/s]
1it [00:00, 22429.43it/s]
1it [00:00, 21399.51it/s]
1it [00:00, 20460.02it/s]
1it [00:00, 19508.39it/s]
1it [00:00, 19508.39it/s]
5it [00:00, 85598.04it/s]
0it [00:00, ?it/s]
2it [00:00, 41527.76it/s]
2it [00:00, 46091.25it/s]
2it [00:00, 40524.68it/s]
2it [00:00, 38836.15it/s]
2it [00:00, 42366.71it/s]
2it [00:00, 41943.04it/s]
1it [00:00, 23967.45it/s]
1it [00:00, 24818.37it/s]
1it [00:00, 25890.77it/s]
4it [00:00, 72628.64it/s]
2it [00:00, 38836.15it/s]
3it [00:00, 41943.04it/s]
0it [00:00, ?it/s]
3it [00:00, 58254.22it/s]
3it [00:00, 53773.13it/s]
1it [00:00, 25575.02it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
1it [00:00, 26051.58it/s]
1it [00:00, 21509.25it/s]
0it [00:00, ?it/s]
1it [00:00, 16008.79it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
2it [00:00, 42153.81it/s]
4it [00:00, 76260.07it/s]
5it [00:00, 75166.74it/s]
2it [00:00, 39383.14it/s]
2it [00:00, 39756.44it/s]
1it [00:00, 24244.53it/s]
2it [00:00, 42153.81it/s]
0it [00:00, ?it/s]
1it [00:00, 23045.63it/s]
1it [00:00, 23431.87it/s]
1it [00:00, 24528.09it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
1it [00:00, 10810.06it/s]
2it [00:00, 8473.34it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
1it [00:00, 12633.45it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]
0it [00:00, ?it/s]

```

In [ ]:
Copied!
```
text_nodes, index_nodes = node_parser.get_nodes_and_objects(nodes)

```

text_nodes, index_nodes = node_parser.get_nodes_and_objects(nodes)
In [ ]:
Copied!
```
text_nodes[0]

```

text_nodes[0]
Out[ ]:
```
TextNode(id_='c6ffea61-1221-40e3-b0e0-5b24cfbd02d5', embedding=None, metadata={}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='33b7b29c-8eba-458b-a25f-bb8f88951e92', node_type=<ObjectType.DOCUMENT: '4'>, metadata={}, hash='3d4ec5b02a042598b0ea47cdac56453869c17b531a10f60343e9598e05a9390e'), <NodeRelationship.NEXT: '3'>: RelatedNodeInfo(node_id='de618b65-c78a-4390-8536-4e9e295c0e49', node_type=<ObjectType.INDEX: '3'>, metadata={'col_schema': 'Column: Delaware\nType: string\nSummary: State or other jurisdiction of incorporation or organization\n\nColumn: 45-2647441\nType: string\nSummary: I.R.S. Employer Identification No.'}, hash='c008153189b8dd031a3e5e694239a50ebd21f42602676f072d9746241fcef858')}, text='UNITED STATES SECURITIES AND EXCHANGE COMMISSION\n\n Washington, D.C. 20549\n\n FORM 10-Q\n\n(Mark One)\n\n☒ QUARTERLY REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934\n\nFor the quarterly period ended March 31, 2022\n\nOR\n\n☐ TRANSITION REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934\n\nFor the transition period from_____ to _____\n\nCommission File Number: 001-38902\n\n UBER TECHNOLOGIES, INC.\n\n(Exact name of registrant as specified in its charter)\n\nNot Applicable\n\n(Former name, former address and former fiscal year, if changed since last report)', mimetype='text/plain', start_char_idx=1, end_char_idx=595, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n')
```

In [ ]:
Copied!
```
index_nodes[0]

```

index_nodes[0]
Out[ ]:
```
IndexNode(id_='de618b65-c78a-4390-8536-4e9e295c0e49', embedding=None, metadata={'col_schema': 'Column: Delaware\nType: string\nSummary: State or other jurisdiction of incorporation or organization\n\nColumn: 45-2647441\nType: string\nSummary: I.R.S. Employer Identification No.'}, excluded_embed_metadata_keys=['col_schema'], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='33b7b29c-8eba-458b-a25f-bb8f88951e92', node_type=<ObjectType.DOCUMENT: '4'>, metadata={}, hash='3d4ec5b02a042598b0ea47cdac56453869c17b531a10f60343e9598e05a9390e'), <NodeRelationship.PREVIOUS: '2'>: RelatedNodeInfo(node_id='c6ffea61-1221-40e3-b0e0-5b24cfbd02d5', node_type=<ObjectType.TEXT: '1'>, metadata={}, hash='0cafbb2bbffe3085738e748c9ed19c5b88f6b300d876820fc3caa7afa8f0627f'), <NodeRelationship.NEXT: '3'>: RelatedNodeInfo(node_id='c57f8dab-7b69-4850-8885-6a9cf0f531f9', node_type=<ObjectType.TEXT: '1'>, metadata={'table_df': "{'Delaware': {0: '(State or other jurisdiction of incorporation or organization)', 1: '1515 3rd Street', 2: '(Address of principal executive offices, including zip code)', 3: '(Registrant’s telephone number, including area code)'}, '45-2647441': {0: '(I.R.S. Employer Identification No.)', 1: 'San Francisco, California 94158', 2: '(415) 612-8582', 3: ' '}}", 'table_summary': "Table providing information about a company's incorporation details, address of principal executive offices, and contact information.,\nwith the following columns:\n- Delaware: State or other jurisdiction of incorporation or organization\n- 45-2647441: I.R.S. Employer Identification No.\n"}, hash='fadc844962620525c1d3c8d7ff1693a090642818928f9ce7600117258a39aa04')}, text="Table providing information about a company's incorporation details, address of principal executive offices, and contact information.,\nwith the following columns:\n- Delaware: State or other jurisdiction of incorporation or organization\n- 45-2647441: I.R.S. Employer Identification No.\n", mimetype='text/plain', start_char_idx=601, end_char_idx=919, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n', index_id='c57f8dab-7b69-4850-8885-6a9cf0f531f9', obj=TextNode(id_='c57f8dab-7b69-4850-8885-6a9cf0f531f9', embedding=None, metadata={'table_df': "{'Delaware': {0: '(State or other jurisdiction of incorporation or organization)', 1: '1515 3rd Street', 2: '(Address of principal executive offices, including zip code)', 3: '(Registrant’s telephone number, including area code)'}, '45-2647441': {0: '(I.R.S. Employer Identification No.)', 1: 'San Francisco, California 94158', 2: '(415) 612-8582', 3: ' '}}", 'table_summary': "Table providing information about a company's incorporation details, address of principal executive offices, and contact information.,\nwith the following columns:\n- Delaware: State or other jurisdiction of incorporation or organization\n- 45-2647441: I.R.S. Employer Identification No.\n"}, excluded_embed_metadata_keys=['table_df', 'table_summary'], excluded_llm_metadata_keys=['table_df', 'table_summary'], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='33b7b29c-8eba-458b-a25f-bb8f88951e92', node_type=<ObjectType.DOCUMENT: '4'>, metadata={}, hash='3d4ec5b02a042598b0ea47cdac56453869c17b531a10f60343e9598e05a9390e'), <NodeRelationship.PREVIOUS: '2'>: RelatedNodeInfo(node_id='de618b65-c78a-4390-8536-4e9e295c0e49', node_type=<ObjectType.INDEX: '3'>, metadata={'col_schema': 'Column: Delaware\nType: string\nSummary: State or other jurisdiction of incorporation or organization\n\nColumn: 45-2647441\nType: string\nSummary: I.R.S. Employer Identification No.'}, hash='c008153189b8dd031a3e5e694239a50ebd21f42602676f072d9746241fcef858'), <NodeRelationship.NEXT: '3'>: RelatedNodeInfo(node_id='c0fa90a9-fe14-46fa-8434-cd70e134d40e', node_type=<ObjectType.TEXT: '1'>, metadata={}, hash='cc6b1c09572e3a0bd06a93ccea32a5562b36a393a36ede3852f4a5fc946c51fd')}, text="Table providing information about a company's incorporation details, address of principal executive offices, and contact information.,\nwith the following columns:\n- Delaware: State or other jurisdiction of incorporation or organization\n- 45-2647441: I.R.S. Employer Identification No.\n\n|Delaware|45-2647441|\n|---|---|\n|(State or other jurisdiction of incorporation or organization)|(I.R.S. Employer Identification No.)|\n|1515 3rd Street|San Francisco, California 94158|\n|(Address of principal executive offices, including zip code)|(415) 612-8582|\n|(Registrant’s telephone number, including area code)| |\n", mimetype='text/plain', start_char_idx=601, end_char_idx=919, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'))
```

#### Build Index¶
In [ ]:
Copied!
```
recursive_index = VectorStoreIndex(nodes=text_nodes + index_nodes)
raw_index = VectorStoreIndex.from_documents(documents)

```

recursive_index = VectorStoreIndex(nodes=text_nodes + index_nodes) raw_index = VectorStoreIndex.from_documents(documents)
#### Create Query Engines¶
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
```
tokenizer_config.json:   0%|          | 0.00/443 [00:00<?, ?B/s]
```

```
sentencepiece.bpe.model:   0%|          | 0.00/5.07M [00:00<?, ?B/s]
```

```
tokenizer.json:   0%|          | 0.00/17.1M [00:00<?, ?B/s]
```

```
special_tokens_map.json:   0%|          | 0.00/279 [00:00<?, ?B/s]
```

```
config.json:   0%|          | 0.00/801 [00:00<?, ?B/s]
```

```
model.safetensors:   0%|          | 0.00/2.24G [00:00<?, ?B/s]
```

In [ ]:
Copied!
```
recursive_query_engine = recursive_index.as_query_engine(
    similarity_top_k=15, node_postprocessors=[reranker], verbose=True
)

```

recursive_query_engine = recursive_index.as_query_engine( similarity_top_k=15, node_postprocessors=[reranker], verbose=True )
In [ ]:
Copied!
```
raw_query_engine = raw_index.as_query_engine(
    similarity_top_k=15, node_postprocessors=[reranker]
)

```

raw_query_engine = raw_index.as_query_engine( similarity_top_k=15, node_postprocessors=[reranker] )
#### Querying with two different query engines¶
we compare base query engine vs recursive query engine with tables
##### Table Query Task: Queries for Table Question Answering¶
In [ ]:
Copied!
```
query = "What is the change of free cash flow and what is the rate from the financial and operational highlights?"

response_1 = raw_query_engine.query(query)
print("\n************New LlamaParse+ Basic Query Engine************")
print(response_1)

response_2 = recursive_query_engine.query(query)
print(
    "\n************New LlamaParse+ Recursive Retriever Query Engine************"
)
print(response_2)

```

query = "What is the change of free cash flow and what is the rate from the financial and operational highlights?" response_1 = raw_query_engine.query(query) print("\n************New LlamaParse+ Basic Query Engine************") print(response_1) response_2 = recursive_query_engine.query(query) print( "\n************New LlamaParse+ Recursive Retriever Query Engine************" ) print(response_2)
```
************New LlamaParse+ Basic Query Engine************
The change in free cash flow from the financial and operational highlights is an increase of $826 million, from a net cash used in operating activities of $611 million in 2021 to net cash provided by operating activities of $215 million in 2022. The rate of this change is a positive improvement.
Retrieval entering 015f9778-1f7c-44cd-9e26-90f2c9e21550: TextNode
Retrieving from object TextNode with query What is the change of free cash flow and what is the rate from the financial and operational highlights?
Retrieval entering 5e8febd0-0c43-4552-9499-9465674b8877: TextNode
Retrieving from object TextNode with query What is the change of free cash flow and what is the rate from the financial and operational highlights?
Retrieval entering d3c8d59b-9d7e-4088-94e9-3e58aba09f10: TextNode
Retrieving from object TextNode with query What is the change of free cash flow and what is the rate from the financial and operational highlights?
Retrieval entering 25385e8f-24df-4660-959b-c499cc220246: TextNode
Retrieving from object TextNode with query What is the change of free cash flow and what is the rate from the financial and operational highlights?
Retrieval entering 6b48fe6f-a60e-425a-aba5-22b62d1b4512: TextNode
Retrieving from object TextNode with query What is the change of free cash flow and what is the rate from the financial and operational highlights?
Retrieval entering aa60761d-1d8a-4896-aef9-e41553f17558: TextNode
Retrieving from object TextNode with query What is the change of free cash flow and what is the rate from the financial and operational highlights?
Retrieval entering d0634d58-0589-47cb-9921-d2d57d88240f: TextNode
Retrieving from object TextNode with query What is the change of free cash flow and what is the rate from the financial and operational highlights?
Retrieval entering 492b36c1-8b39-4db9-8dca-dd9f6c488a9d: TextNode
Retrieving from object TextNode with query What is the change of free cash flow and what is the rate from the financial and operational highlights?

************New LlamaParse+ Recursive Retriever Query Engine************
The change in free cash flow from 2021 to 2022 is an increase of $635 million. This change represents a significant improvement in free cash flow performance over the period.

```

