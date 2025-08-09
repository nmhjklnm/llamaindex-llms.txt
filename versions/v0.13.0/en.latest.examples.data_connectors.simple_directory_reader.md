![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Simple Directory Reader¶
The `SimpleDirectoryReader` is the most commonly used data connector that _just works_.  
Simply pass in a input directory or a list of files.  
It will select the best file reader based on the file extensions.
### Get Started¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
```
Requirement already satisfied: llama-index in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (0.10.11)
Requirement already satisfied: llama-index-agent-openai<0.2.0,>=0.1.4 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.4)
Requirement already satisfied: llama-index-cli<0.2.0,>=0.1.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.3)
Requirement already satisfied: llama-index-core<0.11.0,>=0.10.11.post1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.10.11.post1)
Requirement already satisfied: llama-index-embeddings-openai<0.2.0,>=0.1.5 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.5)
Requirement already satisfied: llama-index-indices-managed-llama-cloud<0.2.0,>=0.1.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.2)
Requirement already satisfied: llama-index-legacy<0.10.0,>=0.9.48 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.9.48)
Requirement already satisfied: llama-index-llms-openai<0.2.0,>=0.1.5 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.5)
Requirement already satisfied: llama-index-multi-modal-llms-openai<0.2.0,>=0.1.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.3)
Requirement already satisfied: llama-index-program-openai<0.2.0,>=0.1.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.3)
Requirement already satisfied: llama-index-question-gen-openai<0.2.0,>=0.1.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.2)
Requirement already satisfied: llama-index-readers-file<0.2.0,>=0.1.4 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.4)
Requirement already satisfied: llama-index-readers-llama-parse<0.2.0,>=0.1.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.2)
Requirement already satisfied: llama-index-vector-stores-chroma<0.2.0,>=0.1.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.1.2)
Requirement already satisfied: PyYAML>=6.0.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2.0.27)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (3.9.3)
Requirement already satisfied: dataclasses-json in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (0.6.4)
Requirement already satisfied: deprecated>=1.2.9.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2024.2.0)
Requirement already satisfied: httpx in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (0.27.0)
Requirement already satisfied: llamaindex-py-client<0.2.0,>=0.1.13 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (0.1.13)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.6.0)
Requirement already satisfied: networkx>=3.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (3.1)
Requirement already satisfied: nltk<4.0.0,>=3.8.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (3.8.1)
Requirement already satisfied: numpy in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.24.4)
Requirement already satisfied: openai>=1.1.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.12.0)
Requirement already satisfied: pandas in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2.0.3)
Requirement already satisfied: pillow>=9.0.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (10.2.0)
Requirement already satisfied: requests>=2.31.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2.31.0)
Requirement already satisfied: tenacity<9.0.0,>=8.2.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (8.2.3)
Requirement already satisfied: tiktoken>=0.3.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (0.6.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (4.66.2)
Requirement already satisfied: typing-extensions>=4.5.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (4.9.0)
Requirement already satisfied: typing-inspect>=0.8.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (0.9.0)
Requirement already satisfied: beautifulsoup4<5.0.0,>=4.12.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (4.12.3)
Requirement already satisfied: bs4<0.0.3,>=0.0.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (0.0.2)
Requirement already satisfied: pymupdf<2.0.0,>=1.23.21 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (1.23.25)
Requirement already satisfied: pypdf<5.0.0,>=4.0.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (4.0.2)
Requirement already satisfied: llama-parse<0.4.0,>=0.3.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-readers-llama-parse<0.2.0,>=0.1.2->llama-index) (0.3.4)
Requirement already satisfied: aiosignal>=1.1.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (23.2.0)
Requirement already satisfied: frozenlist>=1.1.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.9.4)
Requirement already satisfied: soupsieve>1.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from beautifulsoup4<5.0.0,>=4.12.3->llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (2.5)
Requirement already satisfied: wrapt<2,>=1.10 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from deprecated>=1.2.9.3->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.16.0)
Requirement already satisfied: chromadb<0.5.0,>=0.4.22 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.4.22)
Requirement already satisfied: onnxruntime<2.0.0,>=1.17.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.17.0)
Requirement already satisfied: tokenizers<0.16.0,>=0.15.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.15.2)
Requirement already satisfied: pydantic>=1.10 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from llamaindex-py-client<0.2.0,>=0.1.13->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.10.14)
Requirement already satisfied: anyio in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (4.3.0)
Requirement already satisfied: certifi in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2024.2.2)
Requirement already satisfied: httpcore==1.* in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.0.4)
Requirement already satisfied: idna in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (3.6)
Requirement already satisfied: sniffio in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.3.0)
Requirement already satisfied: h11<0.15,>=0.13 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from httpcore==1.*->httpx->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (0.14.0)
Requirement already satisfied: click in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (8.1.7)
Requirement already satisfied: joblib in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.3.2)
Requirement already satisfied: regex>=2021.8.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2023.12.25)
Requirement already satisfied: distro<2,>=1.7.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from openai>=1.1.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.9.0)
Requirement already satisfied: PyMuPDFb==1.23.22 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from pymupdf<2.0.0,>=1.23.21->llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (1.23.22)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (3.3.2)
Requirement already satisfied: urllib3<3,>=1.21.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2.0.7)
Requirement already satisfied: greenlet!=0.4.17 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from typing-inspect>=0.8.0->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from dataclasses-json->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (3.20.2)
Requirement already satisfied: python-dateutil>=2.8.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2.8.2)
Requirement already satisfied: pytz>=2020.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2024.1)
Requirement already satisfied: tzdata>=2022.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (2024.1)
Requirement already satisfied: build>=1.0.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.0.3)
Requirement already satisfied: chroma-hnswlib==0.7.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.7.3)
Requirement already satisfied: fastapi>=0.95.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.109.2)
Requirement already satisfied: uvicorn>=0.18.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from uvicorn[standard]>=0.18.3->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.27.1)
Requirement already satisfied: posthog>=2.4.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (3.4.2)
Requirement already satisfied: pulsar-client>=3.1.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (3.4.0)
Requirement already satisfied: opentelemetry-api>=1.2.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.22.0)
Requirement already satisfied: opentelemetry-exporter-otlp-proto-grpc>=1.2.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.22.0)
Requirement already satisfied: opentelemetry-instrumentation-fastapi>=0.41b0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.43b0)
Requirement already satisfied: opentelemetry-sdk>=1.2.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.22.0)
Requirement already satisfied: pypika>=0.48.9 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.48.9)
Requirement already satisfied: overrides>=7.3.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (7.7.0)
Requirement already satisfied: importlib-resources in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (6.1.1)
Requirement already satisfied: grpcio>=1.58.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.60.1)
Requirement already satisfied: bcrypt>=4.0.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (4.1.2)
Requirement already satisfied: typer>=0.9.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.9.0)
Requirement already satisfied: kubernetes>=28.1.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (29.0.0)
Requirement already satisfied: mmh3>=4.0.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (4.1.0)
Requirement already satisfied: packaging>=17.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (23.2)
Requirement already satisfied: coloredlogs in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from onnxruntime<2.0.0,>=1.17.0->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (15.0.1)
Requirement already satisfied: flatbuffers in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from onnxruntime<2.0.0,>=1.17.0->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (23.5.26)
Requirement already satisfied: protobuf in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from onnxruntime<2.0.0,>=1.17.0->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (4.25.3)
Requirement already satisfied: sympy in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from onnxruntime<2.0.0,>=1.17.0->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.12)
Requirement already satisfied: six>=1.5 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from python-dateutil>=2.8.2->pandas->llama-index-core<0.11.0,>=0.10.11.post1->llama-index) (1.16.0)
Requirement already satisfied: huggingface_hub<1.0,>=0.16.4 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from tokenizers<0.16.0,>=0.15.1->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.20.3)
Requirement already satisfied: pyproject_hooks in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from build>=1.0.3->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.0.0)
Requirement already satisfied: starlette<0.37.0,>=0.36.3 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from fastapi>=0.95.2->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.36.3)
Requirement already satisfied: filelock in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from huggingface_hub<1.0,>=0.16.4->tokenizers<0.16.0,>=0.15.1->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (3.13.1)
Requirement already satisfied: google-auth>=1.0.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from kubernetes>=28.1.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (2.28.0)
Requirement already satisfied: websocket-client!=0.40.0,!=0.41.*,!=0.42.*,>=0.32.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from kubernetes>=28.1.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.7.0)
Requirement already satisfied: requests-oauthlib in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from kubernetes>=28.1.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.3.1)
Requirement already satisfied: oauthlib>=3.2.2 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from kubernetes>=28.1.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (3.2.2)
Requirement already satisfied: importlib-metadata<7.0,>=6.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-api>=1.2.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (6.11.0)
Requirement already satisfied: backoff<3.0.0,>=1.10.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-exporter-otlp-proto-grpc>=1.2.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (2.2.1)
Requirement already satisfied: googleapis-common-protos~=1.52 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-exporter-otlp-proto-grpc>=1.2.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.62.0)
Requirement already satisfied: opentelemetry-exporter-otlp-proto-common==1.22.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-exporter-otlp-proto-grpc>=1.2.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.22.0)
Requirement already satisfied: opentelemetry-proto==1.22.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-exporter-otlp-proto-grpc>=1.2.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.22.0)
Requirement already satisfied: opentelemetry-instrumentation-asgi==0.43b0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-instrumentation-fastapi>=0.41b0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.43b0)
Requirement already satisfied: opentelemetry-instrumentation==0.43b0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-instrumentation-fastapi>=0.41b0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.43b0)
Requirement already satisfied: opentelemetry-semantic-conventions==0.43b0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-instrumentation-fastapi>=0.41b0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.43b0)
Requirement already satisfied: opentelemetry-util-http==0.43b0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-instrumentation-fastapi>=0.41b0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.43b0)
Requirement already satisfied: setuptools>=16.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-instrumentation==0.43b0->opentelemetry-instrumentation-fastapi>=0.41b0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (69.1.0)
Requirement already satisfied: asgiref~=3.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from opentelemetry-instrumentation-asgi==0.43b0->opentelemetry-instrumentation-fastapi>=0.41b0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (3.7.2)
Requirement already satisfied: monotonic>=1.5 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from posthog>=2.4.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.6)
Requirement already satisfied: httptools>=0.5.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from uvicorn[standard]>=0.18.3->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.6.1)
Requirement already satisfied: python-dotenv>=0.13 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from uvicorn[standard]>=0.18.3->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.0.1)
Requirement already satisfied: uvloop!=0.15.0,!=0.15.1,>=0.14.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from uvicorn[standard]>=0.18.3->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.19.0)
Requirement already satisfied: watchfiles>=0.13 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from uvicorn[standard]>=0.18.3->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.21.0)
Requirement already satisfied: websockets>=10.4 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from uvicorn[standard]>=0.18.3->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (12.0)
Requirement already satisfied: humanfriendly>=9.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from coloredlogs->onnxruntime<2.0.0,>=1.17.0->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (10.0)
Requirement already satisfied: mpmath>=0.19 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from sympy->onnxruntime<2.0.0,>=1.17.0->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (1.3.0)
Requirement already satisfied: cachetools<6.0,>=2.0.0 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from google-auth>=1.0.1->kubernetes>=28.1.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (5.3.2)
Requirement already satisfied: pyasn1-modules>=0.2.1 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from google-auth>=1.0.1->kubernetes>=28.1.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.3.0)
Requirement already satisfied: rsa<5,>=3.1.4 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from google-auth>=1.0.1->kubernetes>=28.1.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (4.9)
Requirement already satisfied: zipp>=0.5 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from importlib-metadata<7.0,>=6.0->opentelemetry-api>=1.2.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (3.17.0)
Requirement already satisfied: pyasn1<0.6.0,>=0.4.6 in /Users/sourabhdesai/Library/Caches/pypoetry/virtualenvs/llama-index-cXQhuK8v-py3.11/lib/python3.11/site-packages (from pyasn1-modules>=0.2.1->google-auth>=1.0.1->kubernetes>=28.1.0->chromadb<0.5.0,>=0.4.22->llama-index-vector-stores-chroma<0.2.0,>=0.1.1->llama-index-cli<0.2.0,>=0.1.2->llama-index) (0.5.1)

[notice] A new release of pip is available: 23.3.2 -> 24.0
[notice] To update, run: pip install --upgrade pip

```

Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay1.txt'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay2.txt'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay3.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay1.txt' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay2.txt' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay3.txt'
```
--2024-03-21 16:03:25--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8003::154, 2606:50c0:8000::154, 2606:50c0:8001::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8003::154|:443... connected.
HTTP request sent, awaiting response... 404 Not Found
2024-03-21 16:03:25 ERROR 404: Not Found.

--2024-03-21 16:03:25--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8003::154, 2606:50c0:8000::154, 2606:50c0:8001::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8003::154|:443... connected.
HTTP request sent, awaiting response... 404 Not Found
2024-03-21 16:03:25 ERROR 404: Not Found.

--2024-03-21 16:03:25--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8003::154, 2606:50c0:8000::154, 2606:50c0:8001::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8003::154|:443... connected.
HTTP request sent, awaiting response... 404 Not Found
2024-03-21 16:03:25 ERROR 404: Not Found.


```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

```

from llama_index.core import SimpleDirectoryReader
Load specific files
In [ ]:
Copied!
```
reader = SimpleDirectoryReader(
    input_files=["./data/paul_graham/paul_graham_essay1.txt"]
)

```

reader = SimpleDirectoryReader( input_files=["./data/paul_graham/paul_graham_essay1.txt"] )
In [ ]:
Copied!
```
docs = reader.load_data()
print(f"Loaded {len(docs)} docs")

```

docs = reader.load_data() print(f"Loaded {len(docs)} docs")
```
Loaded 1 docs

```

Load all (top-level) files from directory
In [ ]:
Copied!
```
reader = SimpleDirectoryReader(input_dir="./data/paul_graham/")

```

reader = SimpleDirectoryReader(input_dir="./data/paul_graham/")
In [ ]:
Copied!
```
docs = reader.load_data()
print(f"Loaded {len(docs)} docs")

```

docs = reader.load_data() print(f"Loaded {len(docs)} docs")
```
Loaded 3 docs

```

Load all (recursive) files from directory
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/nested'
!echo "This is a nested file" > 'data/paul_graham/nested/nested_file.md'

```

!mkdir -p 'data/paul_graham/nested' !echo "This is a nested file" > 'data/paul_graham/nested/nested_file.md'
In [ ]:
Copied!
```
# only load markdown files
required_exts = [".md"]

reader = SimpleDirectoryReader(
    input_dir="./data",
    required_exts=required_exts,
    recursive=True,
)

```

# only load markdown files required_exts = [".md"] reader = SimpleDirectoryReader( input_dir="./data", required_exts=required_exts, recursive=True, )
In [ ]:
Copied!
```
docs = reader.load_data()
print(f"Loaded {len(docs)} docs")

```

docs = reader.load_data() print(f"Loaded {len(docs)} docs")
```
Loaded 1 docs

```

Create an iterator to load files and process them as they load
In [ ]:
Copied!
```
reader = SimpleDirectoryReader(
    input_dir="./data",
    recursive=True,
)

all_docs = []
for docs in reader.iter_data():
    for doc in docs:
        # do something with the doc
        doc.text = doc.text.upper()
        all_docs.append(doc)

print(len(all_docs))

```

reader = SimpleDirectoryReader( input_dir="./data", recursive=True, ) all_docs = [] for docs in reader.iter_data(): for doc in docs: # do something with the doc doc.text = doc.text.upper() all_docs.append(doc) print(len(all_docs))


Async execution is available through `aload_data`
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

reader = SimpleDirectoryReader(
    input_dir="./data",
    recursive=True,
)

all_docs = await reader.aload_data()

print(len(all_docs))

```

import nest_asyncio nest_asyncio.apply() reader = SimpleDirectoryReader( input_dir="./data", recursive=True, ) all_docs = await reader.aload_data() print(len(all_docs))


## Full Configuration¶
This is the full list of arguments that can be passed to the `SimpleDirectoryReader`:
```
class SimpleDirectoryReader(BaseReader):
    """Simple directory reader.

    Load files from file directory.
    Automatically select the best file reader given file extensions.

    Args:
        input_dir (str): Path to the directory.
        input_files (List): List of file paths to read
            (Optional; overrides input_dir, exclude)
        exclude (List): glob of python file paths to exclude (Optional)
        exclude_hidden (bool): Whether to exclude hidden files (dotfiles).
        exclude_empty (bool): Whether to exclude empty files (Optional).
        encoding (str): Encoding of the files.
            Default is utf-8.
        errors (str): how encoding and decoding errors are to be handled,
              see https://docs.python.org/3/library/functions.html#open
        recursive (bool): Whether to recursively search in subdirectories.
            False by default.
        filename_as_id (bool): Whether to use the filename as the document id.
            False by default.
        required_exts (Optional[List[str]]): List of required extensions.
            Default is None.
        file_extractor (Optional[Dict[str, BaseReader]]): A mapping of file
            extension to a BaseReader class that specifies how to convert that file
            to text. If not specified, use default from DEFAULT_FILE_READER_CLS.
        num_files_limit (Optional[int]): Maximum number of files to read.
            Default is None.
        file_metadata (Optional[Callable[str, Dict]]): A function that takes
            in a filename and returns a Dict of metadata for the Document.
            Default is None.
        fs (Optional[fsspec.AbstractFileSystem]): File system to use. Defaults
        to using the local file system. Can be changed to use any remote file system
        exposed via the fsspec interface.
    """

```

