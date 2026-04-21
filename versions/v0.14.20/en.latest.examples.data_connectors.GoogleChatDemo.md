# Google Chat Reader Test¶
Demonstrates our Google Chat data connector.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index llama-index-readers-google

```

%pip install llama-index llama-index-readers-google
```
Requirement already satisfied: llama-index in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (0.10.47)
Requirement already satisfied: llama-index-readers-google in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (0.2.8)
Requirement already satisfied: llama-index-agent-openai<0.3.0,>=0.1.4 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.2.7)
Requirement already satisfied: llama-index-cli<0.2.0,>=0.1.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.12)
Requirement already satisfied: llama-index-core==0.10.47 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.10.47)
Requirement already satisfied: llama-index-embeddings-openai<0.2.0,>=0.1.5 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.10)
Requirement already satisfied: llama-index-indices-managed-llama-cloud<0.2.0,>=0.1.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.6)
Requirement already satisfied: llama-index-legacy<0.10.0,>=0.9.48 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.9.48)
Requirement already satisfied: llama-index-llms-openai<0.2.0,>=0.1.13 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.22)
Requirement already satisfied: llama-index-multi-modal-llms-openai<0.2.0,>=0.1.3 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.6)
Requirement already satisfied: llama-index-program-openai<0.2.0,>=0.1.3 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.6)
Requirement already satisfied: llama-index-question-gen-openai<0.2.0,>=0.1.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.3)
Requirement already satisfied: llama-index-readers-file<0.2.0,>=0.1.4 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.25)
Requirement already satisfied: llama-index-readers-llama-parse<0.2.0,>=0.1.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index) (0.1.4)
Requirement already satisfied: PyYAML>=6.0.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (6.0.1)
Requirement already satisfied: SQLAlchemy>=1.4.49 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from SQLAlchemy[asyncio]>=1.4.49->llama-index-core==0.10.47->llama-index) (2.0.31)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.6 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (3.9.5)
Requirement already satisfied: dataclasses-json in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (0.6.7)
Requirement already satisfied: deprecated>=1.2.9.3 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (1.2.14)
Requirement already satisfied: dirtyjson<2.0.0,>=1.0.8 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (1.0.8)
Requirement already satisfied: fsspec>=2023.5.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (2024.6.0)
Requirement already satisfied: httpx in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (0.27.0)
Requirement already satisfied: llamaindex-py-client<0.2.0,>=0.1.18 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (0.1.19)
Requirement already satisfied: nest-asyncio<2.0.0,>=1.5.8 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (1.6.0)
Requirement already satisfied: networkx>=3.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (3.3)
Requirement already satisfied: nltk<4.0.0,>=3.8.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (3.8.1)
Requirement already satisfied: numpy<2.0.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (1.26.4)
Requirement already satisfied: openai>=1.1.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (1.35.3)
Requirement already satisfied: pandas in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (2.2.2)
Requirement already satisfied: pillow>=9.0.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (10.3.0)
Requirement already satisfied: requests>=2.31.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (2.32.3)
Requirement already satisfied: tenacity!=8.4.0,<9.0.0,>=8.2.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (8.4.1)
Requirement already satisfied: tiktoken>=0.3.3 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (0.7.0)
Requirement already satisfied: tqdm<5.0.0,>=4.66.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (4.66.4)
Requirement already satisfied: typing-extensions>=4.5.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (4.12.2)
Requirement already satisfied: typing-inspect>=0.8.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (0.9.0)
Requirement already satisfied: wrapt in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-core==0.10.47->llama-index) (1.16.0)
Requirement already satisfied: gkeepapi<0.16.0,>=0.15.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-google) (0.15.1)
Requirement already satisfied: google-api-python-client<3.0.0,>=2.115.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-google) (2.134.0)
Requirement already satisfied: google-auth-httplib2<0.3.0,>=0.2.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-google) (0.2.0)
Requirement already satisfied: google-auth-oauthlib<2.0.0,>=1.2.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-google) (1.2.0)
Requirement already satisfied: pydrive<2.0.0,>=1.3.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-google) (1.3.1)
Requirement already satisfied: gpsoauth>=1.0.3 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from gkeepapi<0.16.0,>=0.15.1->llama-index-readers-google) (1.1.1)
Requirement already satisfied: future>=0.16.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from gkeepapi<0.16.0,>=0.15.1->llama-index-readers-google) (1.0.0)
Requirement already satisfied: httplib2<1.dev0,>=0.19.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (0.22.0)
Requirement already satisfied: google-auth!=2.24.0,!=2.25.0,<3.0.0.dev0,>=1.32.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (2.30.0)
Requirement already satisfied: google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (2.19.0)
Requirement already satisfied: uritemplate<5,>=3.0.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (4.1.1)
Requirement already satisfied: requests-oauthlib>=0.7.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-auth-oauthlib<2.0.0,>=1.2.0->llama-index-readers-google) (2.0.0)
Requirement already satisfied: beautifulsoup4<5.0.0,>=4.12.3 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (4.12.3)
Requirement already satisfied: pypdf<5.0.0,>=4.0.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (4.2.0)
Requirement already satisfied: striprtf<0.0.27,>=0.0.26 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (0.0.26)
Requirement already satisfied: llama-parse<0.5.0,>=0.4.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llama-index-readers-llama-parse<0.2.0,>=0.1.2->llama-index) (0.4.4)
Requirement already satisfied: oauth2client>=4.0.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from pydrive<2.0.0,>=1.3.1->llama-index-readers-google) (4.1.3)
Requirement already satisfied: aiosignal>=1.1.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core==0.10.47->llama-index) (1.3.1)
Requirement already satisfied: attrs>=17.3.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core==0.10.47->llama-index) (23.2.0)
Requirement already satisfied: frozenlist>=1.1.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core==0.10.47->llama-index) (1.4.1)
Requirement already satisfied: multidict<7.0,>=4.5 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core==0.10.47->llama-index) (6.0.5)
Requirement already satisfied: yarl<2.0,>=1.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from aiohttp<4.0.0,>=3.8.6->llama-index-core==0.10.47->llama-index) (1.9.4)
Requirement already satisfied: soupsieve>1.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from beautifulsoup4<5.0.0,>=4.12.3->llama-index-readers-file<0.2.0,>=0.1.4->llama-index) (2.5)
Requirement already satisfied: googleapis-common-protos<2.0.dev0,>=1.56.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5->google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (1.63.1)
Requirement already satisfied: protobuf!=3.20.0,!=3.20.1,!=4.21.0,!=4.21.1,!=4.21.2,!=4.21.3,!=4.21.4,!=4.21.5,<5.0.0.dev0,>=3.19.5 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5->google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (4.25.3)
Requirement already satisfied: proto-plus<2.0.0dev,>=1.22.3 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-api-core!=2.0.*,!=2.1.*,!=2.2.*,!=2.3.0,<3.0.0.dev0,>=1.31.5->google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (1.24.0)
Requirement already satisfied: cachetools<6.0,>=2.0.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-auth!=2.24.0,!=2.25.0,<3.0.0.dev0,>=1.32.0->google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (5.3.3)
Requirement already satisfied: pyasn1-modules>=0.2.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-auth!=2.24.0,!=2.25.0,<3.0.0.dev0,>=1.32.0->google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (0.4.0)
Requirement already satisfied: rsa<5,>=3.1.4 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from google-auth!=2.24.0,!=2.25.0,<3.0.0.dev0,>=1.32.0->google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (4.9)
Requirement already satisfied: pycryptodomex>=3.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from gpsoauth>=1.0.3->gkeepapi<0.16.0,>=0.15.1->llama-index-readers-google) (3.20.0)
Requirement already satisfied: urllib3<2.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from gpsoauth>=1.0.3->gkeepapi<0.16.0,>=0.15.1->llama-index-readers-google) (1.26.19)
Requirement already satisfied: pyparsing!=3.0.0,!=3.0.1,!=3.0.2,!=3.0.3,<4,>=2.4.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from httplib2<1.dev0,>=0.19.0->google-api-python-client<3.0.0,>=2.115.0->llama-index-readers-google) (3.1.2)
Requirement already satisfied: pydantic>=1.10 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core==0.10.47->llama-index) (2.7.4)
Requirement already satisfied: anyio in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core==0.10.47->llama-index) (4.4.0)
Requirement already satisfied: certifi in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core==0.10.47->llama-index) (2024.6.2)
Requirement already satisfied: httpcore==1.* in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core==0.10.47->llama-index) (1.0.5)
Requirement already satisfied: idna in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core==0.10.47->llama-index) (3.7)
Requirement already satisfied: sniffio in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from httpx->llama-index-core==0.10.47->llama-index) (1.3.1)
Requirement already satisfied: h11<0.15,>=0.13 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from httpcore==1.*->httpx->llama-index-core==0.10.47->llama-index) (0.14.0)
Requirement already satisfied: click in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core==0.10.47->llama-index) (8.1.7)
Requirement already satisfied: joblib in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core==0.10.47->llama-index) (1.4.2)
Requirement already satisfied: regex>=2021.8.3 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from nltk<4.0.0,>=3.8.1->llama-index-core==0.10.47->llama-index) (2024.5.15)
Requirement already satisfied: pyasn1>=0.1.7 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from oauth2client>=4.0.0->pydrive<2.0.0,>=1.3.1->llama-index-readers-google) (0.6.0)
Requirement already satisfied: six>=1.6.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from oauth2client>=4.0.0->pydrive<2.0.0,>=1.3.1->llama-index-readers-google) (1.16.0)
Requirement already satisfied: distro<2,>=1.7.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from openai>=1.1.0->llama-index-core==0.10.47->llama-index) (1.9.0)
Requirement already satisfied: charset-normalizer<4,>=2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from requests>=2.31.0->llama-index-core==0.10.47->llama-index) (3.3.2)
Requirement already satisfied: oauthlib>=3.0.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from requests-oauthlib>=0.7.0->google-auth-oauthlib<2.0.0,>=1.2.0->llama-index-readers-google) (3.2.2)
Requirement already satisfied: greenlet!=0.4.17 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from SQLAlchemy>=1.4.49->SQLAlchemy[asyncio]>=1.4.49->llama-index-core==0.10.47->llama-index) (3.0.3)
Requirement already satisfied: mypy-extensions>=0.3.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from typing-inspect>=0.8.0->llama-index-core==0.10.47->llama-index) (1.0.0)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from dataclasses-json->llama-index-core==0.10.47->llama-index) (3.21.3)
Requirement already satisfied: python-dateutil>=2.8.2 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from pandas->llama-index-core==0.10.47->llama-index) (2.9.0.post0)
Requirement already satisfied: pytz>=2020.1 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from pandas->llama-index-core==0.10.47->llama-index) (2024.1)
Requirement already satisfied: tzdata>=2022.7 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from pandas->llama-index-core==0.10.47->llama-index) (2024.1)
Requirement already satisfied: packaging>=17.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from marshmallow<4.0.0,>=3.18.0->dataclasses-json->llama-index-core==0.10.47->llama-index) (24.1)
Requirement already satisfied: annotated-types>=0.4.0 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core==0.10.47->llama-index) (0.7.0)
Requirement already satisfied: pydantic-core==2.18.4 in /Users/jonathanliu/Library/Caches/pypoetry/virtualenvs/llama-index-RvIdVF4_-py3.11/lib/python3.11/site-packages (from pydantic>=1.10->llamaindex-py-client<0.2.0,>=0.1.18->llama-index-core==0.10.47->llama-index) (2.18.4)

[notice] A new release of pip is available: 24.0 -> 24.1
[notice] To update, run: pip install --upgrade pip
Note: you may need to restart the kernel to use updated packages.

```

This loader takes in IDs of Google Chat spaces or messages and parses the chat history into `Document`s. The space/message ID can be found in the URL, as shown below:
  * mail.google.com/chat/u/0/#chat/space/**< CHAT_ID>**


Before using this loader, you need to create a Google Cloud Platform (GCP) project with a Google Workspace account. Then, you need to authorize the app with user credentials. Follow the prerequisites and steps 1 and 2 of this guide. After downloading the client secret JSON file, rename it as **`credentials.json`**and save it into your project folder.
This example parses a chat between two users. They first discuss math homework, then they plan a trip to San Francisco in a thread. At the end, they discuss finishing an essay. See the full thread here.
## Basic Usage¶
The example below loads the entire chat history into a `SummaryIndex`.
In [ ]:
Copied!
```
from llama_index.core import SummaryIndex
from llama_index.readers.google import GoogleChatReader

space_ids = [
    "AAAAtTPwdzg"
]  # The Google account you authenticated with must have access to this space
reader = GoogleChatReader()
docs = reader.load_data(space_names=space_ids)

```

from llama_index.core import SummaryIndex from llama_index.readers.google import GoogleChatReader space_ids = [ "AAAAtTPwdzg" ] # The Google account you authenticated with must have access to this space reader = GoogleChatReader() docs = reader.load_data(space_names=space_ids)
In [ ]:
Copied!
```
index = SummaryIndex.from_documents(docs)

```

index = SummaryIndex.from_documents(docs)
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query("What was the overall conversation about?")

```

query_engine = index.as_query_engine() response = query_engine.query("What was the overall conversation about?")
In [ ]:
Copied!
```
from IPython.display import Markdown, display

display(Markdown(f"{response}"))

```

from IPython.display import Markdown, display display(Markdown(f"{response}"))
The overall conversation was about discussing and planning a trip to San Francisco, including visiting various landmarks and using public transportation to get around the city. Additionally, there was a brief mention of finishing homework and essays before the trip.
## Filtering and Ordering¶
### Ordering¶
You can order the chat history by ascending or descending order.
In [ ]:
Copied!
```
docs = reader.load_data(space_names=space_ids, order_asc=False)

index = SummaryIndex.from_documents(docs)
query_engine = index.as_query_engine()
response = query_engine.query(
    "List the things that the users discussed in the order they were discussed in. Make the list short."
)
display(Markdown(f"{response}"))

```

docs = reader.load_data(space_names=space_ids, order_asc=False) index = SummaryIndex.from_documents(docs) query_engine = index.as_query_engine() response = query_engine.query( "List the things that the users discussed in the order they were discussed in. Make the list short." ) display(Markdown(f"{response}"))
  1. Visiting San Francisco
  2. Planning a trip itinerary in San Francisco
  3. Taking public transit to San Francisco
  4. Discussing transportation options in San Francisco
  5. Working on a math problem together


Even though the messages were retrieved in reverse order, the list is still in the correct order because messages have a timestamp in their metadata.
### Message Limiting¶
Messages can be limited to a certain number using the `num_messages` parameter. However, the number of messages that are loaded may not be exactly this number. If `order_asc` is True, then takes the first `num_messages` messages within the given time frame. If `order_desc` is True, then takes the last `num_messages` messages within the time frame.
In [ ]:
Copied!
```
docs = reader.load_data(
    space_names=space_ids, num_messages=10
)  # in ascending order, only contains messages about math HW

index = SummaryIndex.from_documents(docs)
query_engine = index.as_query_engine()
response = query_engine.query("What was discussed in this conversation?")
display(Markdown(f"{response}"))

```

docs = reader.load_data( space_names=space_ids, num_messages=10 ) # in ascending order, only contains messages about math HW index = SummaryIndex.from_documents(docs) query_engine = index.as_query_engine() response = query_engine.query("What was discussed in this conversation?") display(Markdown(f"{response}"))
The conversation revolved around a student seeking help with their math homework, specifically understanding and applying the chain rule in calculus to find the derivative of a function involving cosine. The student was stuck on problem 4b and needed assistance with taking the derivative of cos(2x). The other participant explained the application of the chain rule step by step, leading to the correct derivative of -2sin(2x). The student expressed gratitude for the explanation and indicated that they could now proceed with solving the remaining problems.
Notice that the summary is only about the first 10 messages, which only involves help on the math homework. Below is an example of retrieving the last 16 messages, which only involves the essay. The "cost of a trip" refers to a reply in the SF trip thread that was made during the discussion of the essay.
In [ ]:
Copied!
```
docs = reader.load_data(
    space_names=space_ids, num_messages=16, order_asc=False
)  # in descending order, only contains messages about essay

index = SummaryIndex.from_documents(docs)
query_engine = index.as_query_engine()
response = query_engine.query("What was discussed in this conversation?")
display(Markdown(f"{response}"))

```

docs = reader.load_data( space_names=space_ids, num_messages=16, order_asc=False ) # in descending order, only contains messages about essay index = SummaryIndex.from_documents(docs) query_engine = index.as_query_engine() response = query_engine.query("What was discussed in this conversation?") display(Markdown(f"{response}"))
The conversation revolved around the completion of an essay, specifically focusing on the contrast between old money and new money rather than the American Dream and The Great Gatsby. There were mentions of procrastination, starting work on the essay, and concerns about the cost of a trip.
### Time Frame¶
A `before` and `after` time frame can also be specified. These parameters take in `datetime` objects.
In [ ]:
Copied!
```
import datetime

date1 = datetime.datetime.fromisoformat(
    "2024-06-25 14:27:00-07:00"
)  # when they start talking about trip
docs = reader.load_data(space_names=space_ids, before=date1)

index = SummaryIndex.from_documents(docs)
query_engine = index.as_query_engine()
response = query_engine.query(
    "What was discussed in this conversation?"
)  # should only be about math HW
display(Markdown(f"{response}"))

```

import datetime date1 = datetime.datetime.fromisoformat( "2024-06-25 14:27:00-07:00" ) # when they start talking about trip docs = reader.load_data(space_names=space_ids, before=date1) index = SummaryIndex.from_documents(docs) query_engine = index.as_query_engine() response = query_engine.query( "What was discussed in this conversation?" ) # should only be about math HW display(Markdown(f"{response}"))
The conversation revolved around a student seeking help with understanding the chain rule in calculus, specifically how to take the derivative of cos(2x). The student was stuck on problem 4b and requested assistance, to which the other student explained the application of the chain rule step by step. The explanation clarified how to differentiate cos(2x) using the chain rule, resulting in the derivative being -2sin(2x). The student who sought help expressed gratitude and indicated that they could now proceed with solving the remaining problems.
In [ ]:
Copied!
```
date2 = datetime.datetime.fromisoformat(
    "2024-06-25 14:51:00-07:00"
)  # when they start talking about essay
docs = reader.load_data(space_names=space_ids, after=date2)

index = SummaryIndex.from_documents(docs)
query_engine = index.as_query_engine()
response = query_engine.query(
    "What was discussed in this conversation?"
)  # should only be about essay + cost of trip (in thread)
display(Markdown(f"{response}"))

```

date2 = datetime.datetime.fromisoformat( "2024-06-25 14:51:00-07:00" ) # when they start talking about essay docs = reader.load_data(space_names=space_ids, after=date2) index = SummaryIndex.from_documents(docs) query_engine = index.as_query_engine() response = query_engine.query( "What was discussed in this conversation?" ) # should only be about essay + cost of trip (in thread) display(Markdown(f"{response}"))
The conversation revolved around finishing an essay on the contrast between old money and new money, concerns about the cost of a trip, and reassurances that transportation expenses would be affordable.
In [ ]:
Copied!
```
docs = reader.load_data(space_names=space_ids, after=date1, before=date2)

index = SummaryIndex.from_documents(docs)
query_engine = index.as_query_engine()
response = query_engine.query(
    "What was discussed in this conversation?"
)  # should only be about trip
display(Markdown(f"{response}"))

```

docs = reader.load_data(space_names=space_ids, after=date1, before=date2) index = SummaryIndex.from_documents(docs) query_engine = index.as_query_engine() response = query_engine.query( "What was discussed in this conversation?" ) # should only be about trip display(Markdown(f"{response}"))
The conversation revolved around planning a trip to San Francisco for the weekend. They discussed visiting various landmarks such as the Golden Gate Bridge, Fisherman's Wharf, and the Ferry Building, with the possibility of going to Alcatraz or Twin Peaks if time allowed. They also talked about transportation options like taking Caltrain or BART, renting a scooter or BayWheels bike, and using public transit to move around the city. Additionally, they mentioned exploring Chinatown and taking bus routes back to the city center for flexibility.
