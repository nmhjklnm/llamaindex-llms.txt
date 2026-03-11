# Demo: Azure Table Storage as a Docstore¶
This guide shows you how to use our `AzureDocumentStore` and `AzureIndexStore` abstractions which are backed by Azure Table Storage. By putting nodes in the docstore, this allows you to define multiple indices over the same underlying docstore, instead of duplicating data across indices.
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install matplotlib
%pip install llama-index
%pip install llama-index-embeddings-azure-openai
%pip install llama-index-llms-azure-openai
%pip install llama-index-storage-kvstore-azure
%pip install llama-index-storage-docstore-azure
%pip install llama-index-storage-index-store-azure

```

%pip install matplotlib %pip install llama-index %pip install llama-index-embeddings-azure-openai %pip install llama-index-llms-azure-openai %pip install llama-index-storage-kvstore-azure %pip install llama-index-storage-docstore-azure %pip install llama-index-storage-index-store-azure
```
Requirement already satisfied: llama-index-storage-docstore-azure in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (0.1.0)
Requirement already satisfied: llama-index-core<0.11.0,>=0.10.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-storage-docstore-azure) (0.10.35.post1)
Requirement already satisfied: llama-index-storage-kvstore-azure<0.2.0,>=0.1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-storage-docstore-azure) (0.1.0)
Requirement already satisfied: PyYAML>=6.0.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2.0.30)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (3.9.5)
Requirement already satisfied: dataclasses-json in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (0.6.5)
Requirement already satisfied: deprecated>=1.2.9.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2024.3.1)
Requirement already satisfied: httpx in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (0.27.0)
Requirement already satisfied: llamaindex-py-client<0.2.0,>=0.1.18 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (0.1.19)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.6.0)
Requirement already satisfied: networkx>=3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (3.1)
Requirement already satisfied: nltk<4.0.0,>=3.8.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (3.8.1)
Requirement already satisfied: numpy in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.24.4)
Requirement already satisfied: openai>=1.1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.26.0)
Requirement already satisfied: pandas in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2.0.3)
Requirement already satisfied: pillow>=9.0.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (10.3.0)
Requirement already satisfied: requests>=2.31.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2.31.0)
Requirement already satisfied: tenacity<9.0.0,>=8.2.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (8.3.0)
Requirement already satisfied: tiktoken>=0.3.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (0.6.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (4.66.4)
Requirement already satisfied: typing-extensions>=4.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (4.11.0)
Requirement already satisfied: typing-inspect>=0.8.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (0.9.0)
Requirement already satisfied: wrapt in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.16.0)
Requirement already satisfied: azure-data-tables<13.0.0,>=12.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-storage-kvstore-azure<0.2.0,>=0.1.0->llama-index-storage-docstore-azure) (12.5.0)
Requirement already satisfied: aiosignal>=1.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (23.2.0)
Requirement already satisfied: frozenlist>=1.1.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.9.4)
Requirement already satisfied: azure-core<2.0.0,>=1.29.4 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-data-tables<13.0.0,>=12.5.0->llama-index-storage-kvstore-azure<0.2.0,>=0.1.0->llama-index-storage-docstore-azure) (1.30.1)
Requirement already satisfied: isodate<1.0.0,>=0.6.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-data-tables<13.0.0,>=12.5.0->llama-index-storage-kvstore-azure<0.2.0,>=0.1.0->llama-index-storage-docstore-azure) (0.6.1)
Requirement already satisfied: pydantic>=1.10 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2.7.1)
Requirement already satisfied: anyio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (4.3.0)
Requirement already satisfied: certifi in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2024.2.2)
Requirement already satisfied: httpcore==1.* in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.0.5)
Requirement already satisfied: idna in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (3.7)
Requirement already satisfied: sniffio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.3.1)
Requirement already satisfied: h11<0.15,>=0.13 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpcore==1.*->httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (0.14.0)
Requirement already satisfied: click in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (8.1.7)
Requirement already satisfied: joblib in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.4.2)
Requirement already satisfied: regex>=2021.8.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2024.4.28)
Requirement already satisfied: distro<2,>=1.7.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from openai>=1.1.0->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.9.0)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (3.3.2)
Requirement already satisfied: urllib3<3,>=1.21.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2.2.1)
Requirement already satisfied: greenlet!=0.4.17 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from typing-inspect>=0.8.0->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from dataclasses-json->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (3.21.2)
Requirement already satisfied: python-dateutil>=2.8.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2024.1)
Requirement already satisfied: tzdata>=2022.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2024.1)
Requirement already satisfied: six>=1.11.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-core<2.0.0,>=1.29.4->azure-data-tables<13.0.0,>=12.5.0->llama-index-storage-kvstore-azure<0.2.0,>=0.1.0->llama-index-storage-docstore-azure) (1.16.0)
Requirement already satisfied: packaging>=17.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (24.0)
Requirement already satisfied: annotated-types>=0.4.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (0.6.0)
Requirement already satisfied: pydantic-core==2.18.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-docstore-azure) (2.18.2)
Note: you may need to restart the kernel to use updated packages.
Requirement already satisfied: llama-index-storage-index-store-azure in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (0.1.2)
Requirement already satisfied: llama-index-core<0.11.0,>=0.10.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-storage-index-store-azure) (0.10.35.post1)
Requirement already satisfied: llama-index-storage-kvstore-azure<0.2.0,>=0.1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-storage-index-store-azure) (0.1.0)
Requirement already satisfied: PyYAML>=6.0.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2.0.30)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (3.9.5)
Requirement already satisfied: dataclasses-json in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (0.6.5)
Requirement already satisfied: deprecated>=1.2.9.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2024.3.1)
Requirement already satisfied: httpx in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (0.27.0)
Requirement already satisfied: llamaindex-py-client<0.2.0,>=0.1.18 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (0.1.19)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.6.0)
Requirement already satisfied: networkx>=3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (3.1)
Requirement already satisfied: nltk<4.0.0,>=3.8.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (3.8.1)
Requirement already satisfied: numpy in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.24.4)
Requirement already satisfied: openai>=1.1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.26.0)
Requirement already satisfied: pandas in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2.0.3)
Requirement already satisfied: pillow>=9.0.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (10.3.0)
Requirement already satisfied: requests>=2.31.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2.31.0)
Requirement already satisfied: tenacity<9.0.0,>=8.2.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (8.3.0)
Requirement already satisfied: tiktoken>=0.3.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (0.6.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (4.66.4)
Requirement already satisfied: typing-extensions>=4.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (4.11.0)
Requirement already satisfied: typing-inspect>=0.8.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (0.9.0)
Requirement already satisfied: wrapt in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.16.0)
Requirement already satisfied: azure-data-tables<13.0.0,>=12.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-storage-kvstore-azure<0.2.0,>=0.1.0->llama-index-storage-index-store-azure) (12.5.0)
Requirement already satisfied: aiosignal>=1.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (23.2.0)
Requirement already satisfied: frozenlist>=1.1.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.9.4)
Requirement already satisfied: azure-core<2.0.0,>=1.29.4 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-data-tables<13.0.0,>=12.5.0->llama-index-storage-kvstore-azure<0.2.0,>=0.1.0->llama-index-storage-index-store-azure) (1.30.1)
Requirement already satisfied: isodate<1.0.0,>=0.6.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-data-tables<13.0.0,>=12.5.0->llama-index-storage-kvstore-azure<0.2.0,>=0.1.0->llama-index-storage-index-store-azure) (0.6.1)
Requirement already satisfied: pydantic>=1.10 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2.7.1)
Requirement already satisfied: anyio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (4.3.0)
Requirement already satisfied: certifi in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2024.2.2)
Requirement already satisfied: httpcore==1.* in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.0.5)
Requirement already satisfied: idna in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (3.7)
Requirement already satisfied: sniffio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.3.1)
Requirement already satisfied: h11<0.15,>=0.13 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpcore==1.*->httpx->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (0.14.0)
Requirement already satisfied: click in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (8.1.7)
Requirement already satisfied: joblib in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.4.2)
Requirement already satisfied: regex>=2021.8.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2024.4.28)
Requirement already satisfied: distro<2,>=1.7.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from openai>=1.1.0->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.9.0)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (3.3.2)
Requirement already satisfied: urllib3<3,>=1.21.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2.2.1)
Requirement already satisfied: greenlet!=0.4.17 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from typing-inspect>=0.8.0->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from dataclasses-json->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (3.21.2)
Requirement already satisfied: python-dateutil>=2.8.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2024.1)
Requirement already satisfied: tzdata>=2022.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2024.1)
Requirement already satisfied: six>=1.11.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-core<2.0.0,>=1.29.4->azure-data-tables<13.0.0,>=12.5.0->llama-index-storage-kvstore-azure<0.2.0,>=0.1.0->llama-index-storage-index-store-azure) (1.16.0)
Requirement already satisfied: packaging>=17.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (24.0)
Requirement already satisfied: annotated-types>=0.4.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (0.6.0)
Requirement already satisfied: pydantic-core==2.18.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.1->llama-index-storage-index-store-azure) (2.18.2)
Note: you may need to restart the kernel to use updated packages.
Requirement already satisfied: llama-index-embeddings-azure-openai in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (0.1.6)
Requirement already satisfied: llama-index-core<0.11.0,>=0.10.11.post1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-embeddings-azure-openai) (0.10.35.post1)
Requirement already satisfied: llama-index-embeddings-openai<0.2.0,>=0.1.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-embeddings-azure-openai) (0.1.7)
Requirement already satisfied: llama-index-llms-azure-openai<0.2.0,>=0.1.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-embeddings-azure-openai) (0.1.5)
Requirement already satisfied: PyYAML>=6.0.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2.0.30)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (3.9.5)
Requirement already satisfied: dataclasses-json in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (0.6.5)
Requirement already satisfied: deprecated>=1.2.9.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2024.3.1)
Requirement already satisfied: httpx in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (0.27.0)
Requirement already satisfied: llamaindex-py-client<0.2.0,>=0.1.18 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (0.1.19)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.6.0)
Requirement already satisfied: networkx>=3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (3.1)
Requirement already satisfied: nltk<4.0.0,>=3.8.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (3.8.1)
Requirement already satisfied: numpy in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.24.4)
Requirement already satisfied: openai>=1.1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.26.0)
Requirement already satisfied: pandas in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2.0.3)
Requirement already satisfied: pillow>=9.0.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (10.3.0)
Requirement already satisfied: requests>=2.31.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2.31.0)
Requirement already satisfied: tenacity<9.0.0,>=8.2.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (8.3.0)
Requirement already satisfied: tiktoken>=0.3.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (0.6.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (4.66.4)
Requirement already satisfied: typing-extensions>=4.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (4.11.0)
Requirement already satisfied: typing-inspect>=0.8.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (0.9.0)
Requirement already satisfied: wrapt in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.16.0)
Requirement already satisfied: azure-identity<2.0.0,>=1.15.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (1.15.0)
Requirement already satisfied: llama-index-llms-openai<0.2.0,>=0.1.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (0.1.14)
Requirement already satisfied: aiosignal>=1.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (23.2.0)
Requirement already satisfied: frozenlist>=1.1.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.9.4)
Requirement already satisfied: azure-core<2.0.0,>=1.23.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (1.30.1)
Requirement already satisfied: cryptography>=2.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (42.0.7)
Requirement already satisfied: msal<2.0.0,>=1.24.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (1.28.0)
Requirement already satisfied: msal-extensions<2.0.0,>=0.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (1.1.0)
Requirement already satisfied: pydantic>=1.10 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2.7.1)
Requirement already satisfied: anyio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (4.3.0)
Requirement already satisfied: certifi in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2024.2.2)
Requirement already satisfied: httpcore==1.* in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.0.5)
Requirement already satisfied: idna in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (3.7)
Requirement already satisfied: sniffio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.3.1)
Requirement already satisfied: h11<0.15,>=0.13 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpcore==1.*->httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (0.14.0)
Requirement already satisfied: click in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (8.1.7)
Requirement already satisfied: joblib in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.4.2)
Requirement already satisfied: regex>=2021.8.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2024.4.28)
Requirement already satisfied: distro<2,>=1.7.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from openai>=1.1.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.9.0)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (3.3.2)
Requirement already satisfied: urllib3<3,>=1.21.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2.2.1)
Requirement already satisfied: greenlet!=0.4.17 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from typing-inspect>=0.8.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from dataclasses-json->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (3.21.2)
Requirement already satisfied: python-dateutil>=2.8.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2024.1)
Requirement already satisfied: tzdata>=2022.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2024.1)
Requirement already satisfied: six>=1.11.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-core<2.0.0,>=1.23.0->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (1.16.0)
Requirement already satisfied: cffi>=1.12 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from cryptography>=2.5->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (1.16.0)
Requirement already satisfied: packaging>=17.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (24.0)
Requirement already satisfied: PyJWT<3,>=1.0.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from PyJWT[crypto]<3,>=1.0.0->msal<2.0.0,>=1.24.0->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (2.8.0)
Requirement already satisfied: portalocker<3,>=1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from msal-extensions<2.0.0,>=0.3.0->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (2.8.2)
Requirement already satisfied: annotated-types>=0.4.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (0.6.0)
Requirement already satisfied: pydantic-core==2.18.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-embeddings-azure-openai) (2.18.2)
Requirement already satisfied: pycparser in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from cffi>=1.12->cryptography>=2.5->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai<0.2.0,>=0.1.3->llama-index-embeddings-azure-openai) (2.22)
Note: you may need to restart the kernel to use updated packages.
Requirement already satisfied: llama-index-llms-azure-openai in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (0.1.5)
Requirement already satisfied: azure-identity<2.0.0,>=1.15.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-llms-azure-openai) (1.15.0)
Requirement already satisfied: httpx in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-llms-azure-openai) (0.27.0)
Requirement already satisfied: llama-index-core<0.11.0,>=0.10.11.post1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-llms-azure-openai) (0.10.35.post1)
Requirement already satisfied: llama-index-llms-openai<0.2.0,>=0.1.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-llms-azure-openai) (0.1.14)
Requirement already satisfied: azure-core<2.0.0,>=1.23.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (1.30.1)
Requirement already satisfied: cryptography>=2.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (42.0.7)
Requirement already satisfied: msal<2.0.0,>=1.24.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (1.28.0)
Requirement already satisfied: msal-extensions<2.0.0,>=0.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (1.1.0)
Requirement already satisfied: PyYAML>=6.0.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2.0.30)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (3.9.5)
Requirement already satisfied: dataclasses-json in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (0.6.5)
Requirement already satisfied: deprecated>=1.2.9.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2024.3.1)
Requirement already satisfied: llamaindex-py-client<0.2.0,>=0.1.18 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (0.1.19)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.6.0)
Requirement already satisfied: networkx>=3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (3.1)
Requirement already satisfied: nltk<4.0.0,>=3.8.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (3.8.1)
Requirement already satisfied: numpy in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.24.4)
Requirement already satisfied: openai>=1.1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.26.0)
Requirement already satisfied: pandas in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2.0.3)
Requirement already satisfied: pillow>=9.0.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (10.3.0)
Requirement already satisfied: requests>=2.31.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2.31.0)
Requirement already satisfied: tenacity<9.0.0,>=8.2.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (8.3.0)
Requirement already satisfied: tiktoken>=0.3.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (0.6.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (4.66.4)
Requirement already satisfied: typing-extensions>=4.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (4.11.0)
Requirement already satisfied: typing-inspect>=0.8.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (0.9.0)
Requirement already satisfied: wrapt in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.16.0)
Requirement already satisfied: anyio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-llms-azure-openai) (4.3.0)
Requirement already satisfied: certifi in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-llms-azure-openai) (2024.2.2)
Requirement already satisfied: httpcore==1.* in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-llms-azure-openai) (1.0.5)
Requirement already satisfied: idna in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-llms-azure-openai) (3.7)
Requirement already satisfied: sniffio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-llms-azure-openai) (1.3.1)
Requirement already satisfied: h11<0.15,>=0.13 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpcore==1.*->httpx->llama-index-llms-azure-openai) (0.14.0)
Requirement already satisfied: aiosignal>=1.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (23.2.0)
Requirement already satisfied: frozenlist>=1.1.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.9.4)
Requirement already satisfied: six>=1.11.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from azure-core<2.0.0,>=1.23.0->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (1.16.0)
Requirement already satisfied: cffi>=1.12 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from cryptography>=2.5->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (1.16.0)
Requirement already satisfied: pydantic>=1.10 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2.7.1)
Requirement already satisfied: PyJWT<3,>=1.0.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from PyJWT[crypto]<3,>=1.0.0->msal<2.0.0,>=1.24.0->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (2.8.0)
Requirement already satisfied: packaging in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from msal-extensions<2.0.0,>=0.3.0->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (24.0)
Requirement already satisfied: portalocker<3,>=1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from msal-extensions<2.0.0,>=0.3.0->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (2.8.2)
Requirement already satisfied: click in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (8.1.7)
Requirement already satisfied: joblib in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.4.2)
Requirement already satisfied: regex>=2021.8.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2024.4.28)
Requirement already satisfied: distro<2,>=1.7.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from openai>=1.1.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.9.0)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (3.3.2)
Requirement already satisfied: urllib3<3,>=1.21.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2.2.1)
Requirement already satisfied: greenlet!=0.4.17 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from typing-inspect>=0.8.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from dataclasses-json->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (3.21.2)
Requirement already satisfied: python-dateutil>=2.8.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2024.1)
Requirement already satisfied: tzdata>=2022.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2024.1)
Requirement already satisfied: pycparser in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from cffi>=1.12->cryptography>=2.5->azure-identity<2.0.0,>=1.15.0->llama-index-llms-azure-openai) (2.22)
Requirement already satisfied: annotated-types>=0.4.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (0.6.0)
Requirement already satisfied: pydantic-core==2.18.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.11.post1->llama-index-llms-azure-openai) (2.18.2)
Note: you may need to restart the kernel to use updated packages.
Requirement already satisfied: matplotlib in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (3.8.4)
Requirement already satisfied: contourpy>=1.0.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (1.2.1)
Requirement already satisfied: cycler>=0.10 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (0.12.1)
Requirement already satisfied: fonttools>=4.22.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (4.51.0)
Requirement already satisfied: kiwisolver>=1.3.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (1.4.5)
Requirement already satisfied: numpy>=1.21 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (1.24.4)
Requirement already satisfied: packaging>=20.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (24.0)
Requirement already satisfied: pillow>=8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (10.3.0)
Requirement already satisfied: pyparsing>=2.3.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (3.1.2)
Requirement already satisfied: python-dateutil>=2.7 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from matplotlib) (2.9.0.post0)
Requirement already satisfied: six>=1.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from python-dateutil>=2.7->matplotlib) (1.16.0)
Note: you may need to restart the kernel to use updated packages.
Requirement already satisfied: llama-index in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (0.10.27)
Requirement already satisfied: llama-index-agent-openai<0.3.0,>=0.1.4 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.2.2)
Requirement already satisfied: llama-index-cli<0.2.0,>=0.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.11)
Requirement already satisfied: llama-index-core<0.11.0,>=0.10.27 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.10.35.post1)
Requirement already satisfied: llama-index-embeddings-openai<0.2.0,>=0.1.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.7)
Requirement already satisfied: llama-index-indices-managed-llama-cloud<0.2.0,>=0.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.5)
Requirement already satisfied: llama-index-legacy<0.10.0,>=0.9.48 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.9.48)
Requirement already satisfied: llama-index-llms-openai<0.2.0,>=0.1.13 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.14)
Requirement already satisfied: llama-index-multi-modal-llms-openai<0.2.0,>=0.1.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.4)
Requirement already satisfied: llama-index-program-openai<0.2.0,>=0.1.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.5)
Requirement already satisfied: llama-index-question-gen-openai<0.2.0,>=0.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.3)
Requirement already satisfied: llama-index-readers-file<0.2.0,>=0.1.4 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.13)
Requirement already satisfied: llama-index-readers-llama-parse<0.2.0,>=0.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index) (0.1.4)
Requirement already satisfied: openai>=1.14.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-agent-openai<0.3.0,>=0.1.4->llama-index) (1.26.0)
Requirement already satisfied: PyYAML>=6.0.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.27->llama-index) (2.0.30)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (3.9.5)
Requirement already satisfied: dataclasses-json in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (0.6.5)
Requirement already satisfied: deprecated>=1.2.9.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (2024.3.1)
Requirement already satisfied: httpx in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (0.27.0)
Requirement already satisfied: llamaindex-py-client<0.2.0,>=0.1.18 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (0.1.19)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (1.6.0)
Requirement already satisfied: networkx>=3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (3.1)
Requirement already satisfied: nltk<4.0.0,>=3.8.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (3.8.1)
Requirement already satisfied: numpy in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (1.24.4)
Requirement already satisfied: pandas in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (2.0.3)
Requirement already satisfied: pillow>=9.0.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (10.3.0)
Requirement already satisfied: requests>=2.31.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (2.31.0)
Requirement already satisfied: tenacity<9.0.0,>=8.2.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (8.3.0)
Requirement already satisfied: tiktoken>=0.3.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (0.6.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (4.66.4)
Requirement already satisfied: typing-extensions>=4.5.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (4.11.0)
Requirement already satisfied: typing-inspect>=0.8.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (0.9.0)
Requirement already satisfied: wrapt in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.27->llama-index) (1.16.0)
Requirement already satisfied: beautifulsoup4<5.0.0,>=4.12.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (4.12.3)
Requirement already satisfied: pymupdf<2.0.0,>=1.23.21 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (1.24.1)
Requirement already satisfied: pypdf<5.0.0,>=4.0.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (4.1.0)
Requirement already satisfied: striprtf<0.0.27,>=0.0.26 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (0.0.26)
Requirement already satisfied: llama-parse<0.5.0,>=0.4.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llama-index-readers-llama-parse<0.2.0,>=0.1.2->llama-index) (0.4.0)
Requirement already satisfied: aiosignal>=1.1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.27->llama-index) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.27->llama-index) (23.2.0)
Requirement already satisfied: frozenlist>=1.1.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.27->llama-index) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.27->llama-index) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.27->llama-index) (1.9.4)
Requirement already satisfied: soupsieve>1.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from beautifulsoup4<5.0.0,>=4.12.3->llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (2.5)
Requirement already satisfied: pydantic>=1.10 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.27->llama-index) (2.7.1)
Requirement already satisfied: anyio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.27->llama-index) (4.3.0)
Requirement already satisfied: certifi in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.27->llama-index) (2024.2.2)
Requirement already satisfied: httpcore==1.* in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.27->llama-index) (1.0.5)
Requirement already satisfied: idna in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.27->llama-index) (3.7)
Requirement already satisfied: sniffio in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.27->llama-index) (1.3.1)
Requirement already satisfied: h11<0.15,>=0.13 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from httpcore==1.*->httpx->llama-index-core<0.11.0,>=0.10.27->llama-index) (0.14.0)
Requirement already satisfied: click in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.27->llama-index) (8.1.7)
Requirement already satisfied: joblib in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.27->llama-index) (1.4.2)
Requirement already satisfied: regex>=2021.8.3 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.27->llama-index) (2024.4.28)
Requirement already satisfied: distro<2,>=1.7.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from openai>=1.14.0->llama-index-agent-openai<0.3.0,>=0.1.4->llama-index) (1.9.0)
Requirement already satisfied: PyMuPDFb==1.24.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pymupdf<2.0.0,>=1.23.21->llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (1.24.1)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.27->llama-index) (3.3.2)
Requirement already satisfied: urllib3<3,>=1.21.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.27->llama-index) (2.2.1)
Requirement already satisfied: greenlet!=0.4.17 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.27->llama-index) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from typing-inspect>=0.8.0->llama-index-core<0.11.0,>=0.10.27->llama-index) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from dataclasses-json->llama-index-core<0.11.0,>=0.10.27->llama-index) (3.21.2)
Requirement already satisfied: python-dateutil>=2.8.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.27->llama-index) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.27->llama-index) (2024.1)
Requirement already satisfied: tzdata>=2022.1 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.27->llama-index) (2024.1)
Requirement already satisfied: packaging>=17.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core<0.11.0,>=0.10.27->llama-index) (24.0)
Requirement already satisfied: annotated-types>=0.4.0 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.27->llama-index) (0.6.0)
Requirement already satisfied: pydantic-core==2.18.2 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core<0.11.0,>=0.10.27->llama-index) (2.18.2)
Requirement already satisfied: six>=1.5 in /Users/falven/.pyenv/versions/3.11.8/envs/llama_index/lib/python3.11/site-packages (from python-dateutil>=2.8.2->pandas->llama-index-core<0.11.0,>=0.10.27->llama-index) (1.16.0)
Note: you may need to restart the kernel to use updated packages.

```

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
import logging
import sys
import os

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
    logging.WARNING
)

```

import logging import sys import os logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel( logging.WARNING )
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex
from llama_index.core import SummaryIndex
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.response.notebook_utils import display_response
from llama_index.core import Settings
from llama_index.storage.kvstore.azure.base import ServiceMode

```

from llama_index.core import SimpleDirectoryReader, StorageContext from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex from llama_index.core import SummaryIndex from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding from llama_index.llms.azure_openai import AzureOpenAI from llama_index.core.response.notebook_utils import display_response from llama_index.core import Settings from llama_index.storage.kvstore.azure.base import ServiceMode
#### Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-05-08 23:47:52--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 185.199.110.133, 185.199.111.133, 185.199.108.133, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|185.199.110.133|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.01s   

2024-05-08 23:47:52 (6.63 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

#### Load Documents¶
In [ ]:
Copied!
```
reader = SimpleDirectoryReader("./data/paul_graham/")
documents = reader.load_data()

```

reader = SimpleDirectoryReader("./data/paul_graham/") documents = reader.load_data()
#### Parse into Nodes¶
In [ ]:
Copied!
```
from llama_index.core.node_parser import SentenceSplitter

nodes = SentenceSplitter().get_nodes_from_documents(documents)

```

from llama_index.core.node_parser import SentenceSplitter nodes = SentenceSplitter().get_nodes_from_documents(documents)
#### Add to Docstore¶
In [ ]:
Copied!
```
from llama_index.storage.docstore.azure import AzureDocumentStore
from llama_index.storage.index_store.azure import AzureIndexStore

```

from llama_index.storage.docstore.azure import AzureDocumentStore from llama_index.storage.index_store.azure import AzureIndexStore
The AzureDocumentStore and AzureIndexStore classes provide several helper methods `from_connection_string`, `from_account_and_key`, `from_sas_token`, `from_aad_token`... to simplify connecting to our Azure Table Storage service.
In [ ]:
Copied!
```
storage_context = StorageContext.from_defaults(
    docstore=AzureDocumentStore.from_account_and_key(
        "",
        "",
        service_mode=ServiceMode.STORAGE,
    ),
    index_store=AzureIndexStore.from_account_and_key(
        "",
        "",
        service_mode=ServiceMode.STORAGE,
    ),
)

```

storage_context = StorageContext.from_defaults( docstore=AzureDocumentStore.from_account_and_key( "", "", service_mode=ServiceMode.STORAGE, ), index_store=AzureIndexStore.from_account_and_key( "", "", service_mode=ServiceMode.STORAGE, ), )
In [ ]:
Copied!
```
storage_context.docstore.add_documents(nodes)

```

storage_context.docstore.add_documents(nodes)
If we navigate to our Azure Table Storage, we should now be able to see our documents in the table.
# Define our models¶
In staying with the Azure theme, let's define our Azure OpenAI embedding and LLM models.
In [ ]:
Copied!
```
Settings.embed_model = AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="text-embedding-ada-002",
    api_key="",
    azure_endpoint="",
    api_version="2024-03-01-preview",
)
Settings.llm = AzureOpenAI(
    model="gpt-4",
    deployment_name="gpt-4",
    api_key="",
    azure_endpoint="",
    api_version="2024-03-01-preview",
)

```

Settings.embed_model = AzureOpenAIEmbedding( model="text-embedding-ada-002", deployment_name="text-embedding-ada-002", api_key="", azure_endpoint="", api_version="2024-03-01-preview", ) Settings.llm = AzureOpenAI( model="gpt-4", deployment_name="gpt-4", api_key="", azure_endpoint="", api_version="2024-03-01-preview", )
#### Define Multiple Indexes¶
Each index uses the same underlying Nodes.
In [ ]:
Copied!
```
summary_index = SummaryIndex(nodes, storage_context=storage_context)

```

summary_index = SummaryIndex(nodes, storage_context=storage_context)
We should now be able to see our `summary_index` in Azure Table Storage.
In [ ]:
Copied!
```
vector_index = VectorStoreIndex(nodes, storage_context=storage_context)

```

vector_index = VectorStoreIndex(nodes, storage_context=storage_context)
We should now see an entry for our `vector_index` in Azure Table Storage.
In [ ]:
Copied!
```
keyword_table_index = SimpleKeywordTableIndex(
    nodes, storage_context=storage_context
)

```

keyword_table_index = SimpleKeywordTableIndex( nodes, storage_context=storage_context )
We should now see an entry our `keyword_table_index` in Azure Table Storage
In [ ]:
Copied!
```
# NOTE: the docstore still has the same nodes
len(storage_context.docstore.docs)

```

# NOTE: the docstore still has the same nodes len(storage_context.docstore.docs)
Out[ ]:


#### Test out saving and loading¶
In [ ]:
Copied!
```
# NOTE: docstore and index_store are persisted in Azure Table Storage.
# NOTE: This call is only needed to persist the in-memory `SimpleVectorStore`, created by `VectorStoreIndex`, to disk.
storage_context.persist()

```

# NOTE: docstore and index_store are persisted in Azure Table Storage. # NOTE: This call is only needed to persist the in-memory `SimpleVectorStore`, created by `VectorStoreIndex`, to disk. storage_context.persist()
In [ ]:
Copied!
```
# note down index IDs
list_id = summary_index.index_id
vector_id = vector_index.index_id
keyword_id = keyword_table_index.index_id

```

# note down index IDs list_id = summary_index.index_id vector_id = vector_index.index_id keyword_id = keyword_table_index.index_id
In [ ]:
Copied!
```
from llama_index.core import load_index_from_storage

# re-create storage context
storage_context = StorageContext.from_defaults(
    persist_dir="./storage",
    docstore=AzureDocumentStore.from_account_and_key(
        "",
        "",
        service_mode=ServiceMode.STORAGE,
    ),
    index_store=AzureIndexStore.from_account_and_key(
        "",
        "",
        service_mode=ServiceMode.STORAGE,
    ),
)

# load indices
summary_index = load_index_from_storage(
    storage_context=storage_context, index_id=list_id
)
vector_index = load_index_from_storage(
    storage_context=storage_context, index_id=vector_id
)
keyword_table_index = load_index_from_storage(
    storage_context=storage_context, index_id=keyword_id
)

```

from llama_index.core import load_index_from_storage # re-create storage context storage_context = StorageContext.from_defaults( persist_dir="./storage", docstore=AzureDocumentStore.from_account_and_key( "", "", service_mode=ServiceMode.STORAGE, ), index_store=AzureIndexStore.from_account_and_key( "", "", service_mode=ServiceMode.STORAGE, ), ) # load indices summary_index = load_index_from_storage( storage_context=storage_context, index_id=list_id ) vector_index = load_index_from_storage( storage_context=storage_context, index_id=vector_id ) keyword_table_index = load_index_from_storage( storage_context=storage_context, index_id=keyword_id )
```
INFO:llama_index.core.indices.loading:Loading indices with ids: ['cc88721d-b03e-4ecf-8a3d-8eba23af2f12']
Loading indices with ids: ['cc88721d-b03e-4ecf-8a3d-8eba23af2f12']
INFO:llama_index.core.indices.loading:Loading indices with ids: ['399b94e3-8661-4aef-9962-739952206466']
Loading indices with ids: ['399b94e3-8661-4aef-9962-739952206466']
INFO:llama_index.core.indices.loading:Loading indices with ids: ['f69b0db4-25c2-419a-bcab-75e4c35db96b']
Loading indices with ids: ['f69b0db4-25c2-419a-bcab-75e4c35db96b']

```

#### Test out some Queries¶
In [ ]:
Copied!
```
query_engine = summary_index.as_query_engine()
list_response = query_engine.query("What is a summary of this document?")

```

query_engine = summary_index.as_query_engine() list_response = query_engine.query("What is a summary of this document?")
In [ ]:
Copied!
```
display_response(list_response)

```

display_response(list_response)
**`Final Response:`**This document is an extensive reflection by Paul Graham on his multifaceted career, spanning from his initial forays into programming and art to his influential role in the startup ecosystem through the creation of Y Combinator (YC). Graham narrates his early fascination with computers, leading to significant contributions in programming, particularly with Lisp, and his unexpected journey into entrepreneurship with the founding of Viaweb, one of the first online store builders. This venture not only marked a pivotal moment in e-commerce but also set the stage for Graham's deeper involvement in the tech startup world.
The narrative delves into the inception of Y Combinator, highlighting its innovative approach to startup funding and support through the batch model and the Summer Founders Program, which aimed to nurture new startups by providing seed funding and mentorship. Graham shares insights into the challenges and successes of YC, including its role in funding notable startups like Reddit and Twitch, and discusses the personal growth and realizations that led him to eventually step down from YC to pursue other interests, including a return to writing and programming.
Throughout the essay, Graham reflects on the intersections between his interests in technology, writing, and art, and how these have influenced his career decisions and entrepreneurial ventures. He also touches on personal moments, such as the illness and passing of his mother, which prompted introspection and shifts in his professional focus. The document concludes with Graham's continued exploration of programming languages and his decision to work on Lisp again, underscoring a lifelong commitment to learning, creating, and contributing to the fields of technology and entrepreneurship.
In [ ]:
Copied!
```
query_engine = vector_index.as_query_engine()
vector_response = query_engine.query("What did the author do growing up?")

```

query_engine = vector_index.as_query_engine() vector_response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
display_response(vector_response)

```

display_response(vector_response)
**`Final Response:`**Growing up, the author engaged in writing and programming outside of school. Initially, they wrote short stories, which they described as lacking in plot but filled with characters that had strong feelings. Their first attempts at programming were on an IBM 1401, using an early version of Fortran, where they encountered challenges due to the limitations of the technology at the time. Later, with the advent of microcomputers, the author's programming activities expanded, leading them to write simple games, a program to predict the flight of model rockets, and a word processor that was used by their father.
In [ ]:
Copied!
```
query_engine = keyword_table_index.as_query_engine()
keyword_response = query_engine.query(
    "What did the author do after his time at YC?"
)

```

query_engine = keyword_table_index.as_query_engine() keyword_response = query_engine.query( "What did the author do after his time at YC?" )
In [ ]:
Copied!
```
display_response(keyword_response)

```

display_response(keyword_response)
**`Final Response:`**After leaving Y Combinator (YC), the author decided to pursue painting, wanting to see how good he could get if he really focused on it. He spent most of the rest of the year painting, achieving a level of skill that, while not as high as he hoped, was better than before. However, in November, he lost interest in painting and stopped. Subsequently, he resumed writing essays, producing a number of new ones over the following months, including some that were not about startups. In March 2015, he began working on Lisp again, focusing on its core as a language defined by writing an interpreter in itself.
