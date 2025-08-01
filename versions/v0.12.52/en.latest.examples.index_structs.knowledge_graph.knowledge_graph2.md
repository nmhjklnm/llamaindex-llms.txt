# Knowledge Graph Construction w/ WikiData Filtering¶
In this notebook, we compare using REBEL for knowledge graph construction with and without filtering from wikidata.
This is a simplified version, find out more about using wikipedia for filtering, check here
  * Make Meaningful Knowledge Graph from OpenSource REBEL Model


## Setup¶
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-readers-web
%pip install llama-index-readers-papers

```

%pip install llama-index-llms-openai %pip install llama-index-readers-web %pip install llama-index-readers-papers
In [ ]:
Copied!
```
!pip install llama_index transformers wikipedia html2text pyvis

```

!pip install llama_index transformers wikipedia html2text pyvis
```
Requirement already satisfied: llama_index in /usr/local/lib/python3.10/dist-packages (0.8.37)
Requirement already satisfied: transformers in /usr/local/lib/python3.10/dist-packages (4.33.3)
Requirement already satisfied: wikipedia in /usr/local/lib/python3.10/dist-packages (1.4.0)
Requirement already satisfied: html2text in /usr/local/lib/python3.10/dist-packages (2020.1.16)
Requirement already satisfied: pyvis in /usr/local/lib/python3.10/dist-packages (0.3.2)
Requirement already satisfied: tiktoken in /usr/local/lib/python3.10/dist-packages (from llama_index) (0.5.1)
Requirement already satisfied: dataclasses-json in /usr/local/lib/python3.10/dist-packages (from llama_index) (0.6.1)
Requirement already satisfied: langchain>=0.0.303 in /usr/local/lib/python3.10/dist-packages (from llama_index) (0.0.305)
Requirement already satisfied: sqlalchemy>=2.0.15 in /usr/local/lib/python3.10/dist-packages (from llama_index) (2.0.20)
Requirement already satisfied: numpy in /usr/local/lib/python3.10/dist-packages (from llama_index) (1.23.5)
Requirement already satisfied: tenacity<9.0.0,>=8.2.0 in /usr/local/lib/python3.10/dist-packages (from llama_index) (8.2.3)
Requirement already satisfied: openai>=0.26.4 in /usr/local/lib/python3.10/dist-packages (from llama_index) (0.28.1)
Requirement already satisfied: pandas in /usr/local/lib/python3.10/dist-packages (from llama_index) (1.5.3)
Requirement already satisfied: urllib3<2 in /usr/local/lib/python3.10/dist-packages (from llama_index) (1.26.16)
Requirement already satisfied: fsspec>=2023.5.0 in /usr/local/lib/python3.10/dist-packages (from llama_index) (2023.6.0)
Requirement already satisfied: typing-inspect>=0.8.0 in /usr/local/lib/python3.10/dist-packages (from llama_index) (0.9.0)
Requirement already satisfied: typing-extensions>=4.5.0 in /usr/local/lib/python3.10/dist-packages (from llama_index) (4.5.0)
Requirement already satisfied: beautifulsoup4 in /usr/local/lib/python3.10/dist-packages (from llama_index) (4.11.2)
Requirement already satisfied: nest-asyncio in /usr/local/lib/python3.10/dist-packages (from llama_index) (1.5.7)
Requirement already satisfied: nltk in /usr/local/lib/python3.10/dist-packages (from llama_index) (3.8.1)
Requirement already satisfied: tree-sitter-languages in /usr/local/lib/python3.10/dist-packages (from llama_index) (1.7.0)
Requirement already satisfied: filelock in /usr/local/lib/python3.10/dist-packages (from transformers) (3.12.2)
Requirement already satisfied: huggingface-hub<1.0,>=0.15.1 in /usr/local/lib/python3.10/dist-packages (from transformers) (0.17.3)
Requirement already satisfied: packaging>=20.0 in /usr/local/lib/python3.10/dist-packages (from transformers) (23.1)
Requirement already satisfied: pyyaml>=5.1 in /usr/local/lib/python3.10/dist-packages (from transformers) (6.0.1)
Requirement already satisfied: regex!=2019.12.17 in /usr/local/lib/python3.10/dist-packages (from transformers) (2023.6.3)
Requirement already satisfied: requests in /usr/local/lib/python3.10/dist-packages (from transformers) (2.31.0)
Requirement already satisfied: tokenizers!=0.11.3,<0.14,>=0.11.1 in /usr/local/lib/python3.10/dist-packages (from transformers) (0.13.3)
Requirement already satisfied: safetensors>=0.3.1 in /usr/local/lib/python3.10/dist-packages (from transformers) (0.3.3)
Requirement already satisfied: tqdm>=4.27 in /usr/local/lib/python3.10/dist-packages (from transformers) (4.66.1)
Requirement already satisfied: ipython>=5.3.0 in /usr/local/lib/python3.10/dist-packages (from pyvis) (7.34.0)
Requirement already satisfied: jinja2>=2.9.6 in /usr/local/lib/python3.10/dist-packages (from pyvis) (3.1.2)
Requirement already satisfied: jsonpickle>=1.4.1 in /usr/local/lib/python3.10/dist-packages (from pyvis) (3.0.2)
Requirement already satisfied: networkx>=1.11 in /usr/local/lib/python3.10/dist-packages (from pyvis) (3.1)
Requirement already satisfied: setuptools>=18.5 in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (67.7.2)
Requirement already satisfied: jedi>=0.16 in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (0.19.0)
Requirement already satisfied: decorator in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (4.4.2)
Requirement already satisfied: pickleshare in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (0.7.5)
Requirement already satisfied: traitlets>=4.2 in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (5.7.1)
Requirement already satisfied: prompt-toolkit!=3.0.0,!=3.0.1,<3.1.0,>=2.0.0 in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (3.0.39)
Requirement already satisfied: pygments in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (2.16.1)
Requirement already satisfied: backcall in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (0.2.0)
Requirement already satisfied: matplotlib-inline in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (0.1.6)
Requirement already satisfied: pexpect>4.3 in /usr/local/lib/python3.10/dist-packages (from ipython>=5.3.0->pyvis) (4.8.0)
Requirement already satisfied: MarkupSafe>=2.0 in /usr/local/lib/python3.10/dist-packages (from jinja2>=2.9.6->pyvis) (2.1.3)
Requirement already satisfied: aiohttp<4.0.0,>=3.8.3 in /usr/local/lib/python3.10/dist-packages (from langchain>=0.0.303->llama_index) (3.8.5)
Requirement already satisfied: anyio<4.0 in /usr/local/lib/python3.10/dist-packages (from langchain>=0.0.303->llama_index) (3.7.1)
Requirement already satisfied: async-timeout<5.0.0,>=4.0.0 in /usr/local/lib/python3.10/dist-packages (from langchain>=0.0.303->llama_index) (4.0.3)
Requirement already satisfied: jsonpatch<2.0,>=1.33 in /usr/local/lib/python3.10/dist-packages (from langchain>=0.0.303->llama_index) (1.33)
Requirement already satisfied: langsmith<0.1.0,>=0.0.38 in /usr/local/lib/python3.10/dist-packages (from langchain>=0.0.303->llama_index) (0.0.41)
Requirement already satisfied: numexpr<3.0.0,>=2.8.4 in /usr/local/lib/python3.10/dist-packages (from langchain>=0.0.303->llama_index) (2.8.5)
Requirement already satisfied: pydantic<3,>=1 in /usr/local/lib/python3.10/dist-packages (from langchain>=0.0.303->llama_index) (1.10.12)
Requirement already satisfied: marshmallow<4.0.0,>=3.18.0 in /usr/local/lib/python3.10/dist-packages (from dataclasses-json->llama_index) (3.20.1)
Requirement already satisfied: charset-normalizer<4,>=2 in /usr/local/lib/python3.10/dist-packages (from requests->transformers) (3.2.0)
Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.10/dist-packages (from requests->transformers) (3.4)
Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.10/dist-packages (from requests->transformers) (2023.7.22)
Requirement already satisfied: greenlet!=0.4.17 in /usr/local/lib/python3.10/dist-packages (from sqlalchemy>=2.0.15->llama_index) (2.0.2)
Requirement already satisfied: mypy-extensions>=0.3.0 in /usr/local/lib/python3.10/dist-packages (from typing-inspect>=0.8.0->llama_index) (1.0.0)
Requirement already satisfied: soupsieve>1.2 in /usr/local/lib/python3.10/dist-packages (from beautifulsoup4->llama_index) (2.5)
Requirement already satisfied: click in /usr/local/lib/python3.10/dist-packages (from nltk->llama_index) (8.1.7)
Requirement already satisfied: joblib in /usr/local/lib/python3.10/dist-packages (from nltk->llama_index) (1.3.2)
Requirement already satisfied: python-dateutil>=2.8.1 in /usr/local/lib/python3.10/dist-packages (from pandas->llama_index) (2.8.2)
Requirement already satisfied: pytz>=2020.1 in /usr/local/lib/python3.10/dist-packages (from pandas->llama_index) (2023.3.post1)
Requirement already satisfied: tree-sitter in /usr/local/lib/python3.10/dist-packages (from tree-sitter-languages->llama_index) (0.20.2)
Requirement already satisfied: attrs>=17.3.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.3->langchain>=0.0.303->llama_index) (23.1.0)
Requirement already satisfied: multidict<7.0,>=4.5 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.3->langchain>=0.0.303->llama_index) (6.0.4)
Requirement already satisfied: yarl<2.0,>=1.0 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.3->langchain>=0.0.303->llama_index) (1.9.2)
Requirement already satisfied: frozenlist>=1.1.1 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.3->langchain>=0.0.303->llama_index) (1.4.0)
Requirement already satisfied: aiosignal>=1.1.2 in /usr/local/lib/python3.10/dist-packages (from aiohttp<4.0.0,>=3.8.3->langchain>=0.0.303->llama_index) (1.3.1)
Requirement already satisfied: sniffio>=1.1 in /usr/local/lib/python3.10/dist-packages (from anyio<4.0->langchain>=0.0.303->llama_index) (1.3.0)
Requirement already satisfied: exceptiongroup in /usr/local/lib/python3.10/dist-packages (from anyio<4.0->langchain>=0.0.303->llama_index) (1.1.3)
Requirement already satisfied: parso<0.9.0,>=0.8.3 in /usr/local/lib/python3.10/dist-packages (from jedi>=0.16->ipython>=5.3.0->pyvis) (0.8.3)
Requirement already satisfied: jsonpointer>=1.9 in /usr/local/lib/python3.10/dist-packages (from jsonpatch<2.0,>=1.33->langchain>=0.0.303->llama_index) (2.4)
Requirement already satisfied: ptyprocess>=0.5 in /usr/local/lib/python3.10/dist-packages (from pexpect>4.3->ipython>=5.3.0->pyvis) (0.7.0)
Requirement already satisfied: wcwidth in /usr/local/lib/python3.10/dist-packages (from prompt-toolkit!=3.0.0,!=3.0.1,<3.1.0,>=2.0.0->ipython>=5.3.0->pyvis) (0.2.6)
Requirement already satisfied: six>=1.5 in /usr/local/lib/python3.10/dist-packages (from python-dateutil>=2.8.1->pandas->llama_index) (1.16.0)

```

In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
from llama_index.core import KnowledgeGraphIndex
from llama_index.readers.web import SimpleWebPageReader
from llama_index.core.graph_stores import SimpleGraphStore
from llama_index.core import StorageContext
from llama_index.llms.openai import OpenAI

```

from llama_index.core import KnowledgeGraphIndex from llama_index.readers.web import SimpleWebPageReader from llama_index.core.graph_stores import SimpleGraphStore from llama_index.core import StorageContext from llama_index.llms.openai import OpenAI
## 1. extract via huggingface pipeline¶
The initial pipeline uses the provided extraction code from the HuggingFace model card.
In [ ]:
Copied!
```
from transformers import pipeline

triplet_extractor = pipeline(
    "text2text-generation",
    model="Babelscape/rebel-large",
    tokenizer="Babelscape/rebel-large",
    # comment this line to run on CPU
    device="cuda:0",
)


def extract_triplets(input_text):
    text = triplet_extractor.tokenizer.batch_decode(
        [
            triplet_extractor(
                input_text, return_tensors=True, return_text=False
            )[0]["generated_token_ids"]
        ]
    )[0]

    triplets = []
    relation, subject, relation, object_ = "", "", "", ""
    text = text.strip()
    current = "x"
    for token in (
        text.replace("<s>", "")
        .replace("<pad>", "")
        .replace("</s>", "")
        .split()
    ):
        if token == "<triplet>":
            current = "t"
            if relation != "":
                triplets.append(
                    (subject.strip(), relation.strip(), object_.strip())
                )
                relation = ""
            subject = ""
        elif token == "<subj>":
            current = "s"
            if relation != "":
                triplets.append(
                    (subject.strip(), relation.strip(), object_.strip())
                )
            object_ = ""
        elif token == "<obj>":
            current = "o"
            relation = ""
        else:
            if current == "t":
                subject += " " + token
            elif current == "s":
                object_ += " " + token
            elif current == "o":
                relation += " " + token

    if subject != "" and relation != "" and object_ != "":
        triplets.append((subject.strip(), relation.strip(), object_.strip()))

    return triplets

```

from transformers import pipeline triplet_extractor = pipeline( "text2text-generation", model="Babelscape/rebel-large", tokenizer="Babelscape/rebel-large", # comment this line to run on CPU device="cuda:0", ) def extract_triplets(input_text): text = triplet_extractor.tokenizer.batch_decode( [ triplet_extractor( input_text, return_tensors=True, return_text=False )[0]["generated_token_ids"] ] )[0] triplets = [] relation, subject, relation, object_ = "", "", "", "" text = text.strip() current = "x" for token in ( text.replace("~~", "") .replace(" ", "") .replace("~~", "") .split() ): if token == "": current = "t" if relation != "": triplets.append( (subject.strip(), relation.strip(), object_.strip()) ) relation = "" subject = "" elif token == "": current = "s" if relation != "": triplets.append( (subject.strip(), relation.strip(), object_.strip()) ) object_ = "" elif token == "": current = "o" relation = "" else: if current == "t": subject += " " + token elif current == "s": object_ += " " + token elif current == "o": relation += " " + token if subject != "" and relation != "" and object_ != "": triplets.append((subject.strip(), relation.strip(), object_.strip())) return triplets
## 2. Extract with wiki filtering¶
Optionally, we can filter our extracted relations using data from wikipedia.
In [ ]:
Copied!
```
import wikipedia


class WikiFilter:
    def __init__(self):
        self.cache = {}

    def filter(self, candidate_entity):
        # check the cache to avoid network calls
        if candidate_entity in self.cache:
            return self.cache[candidate_entity]["title"]

        # pull the page from wikipedia -- if it exists
        try:
            page = wikipedia.page(candidate_entity, auto_suggest=False)
            entity_data = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary,
            }

            # cache the page title and original entity
            self.cache[candidate_entity] = entity_data
            self.cache[page.title] = entity_data

            return entity_data["title"]
        except:
            return None


wiki_filter = WikiFilter()


def extract_triplets_wiki(text):
    relations = extract_triplets(text)

    filtered_relations = []
    for relation in relations:
        (subj, rel, obj) = relation
        filtered_subj = wiki_filter.filter(subj)
        filtered_obj = wiki_filter.filter(obj)

        # skip if at least one entity not linked to wiki
        if filtered_subj is None and filtered_obj is None:
            continue

        filtered_relations.append(
            (
                filtered_subj or subj,
                rel,
                filtered_obj or obj,
            )
        )

    return filtered_relations

```

import wikipedia class WikiFilter: def __init__(self): self.cache = {} def filter(self, candidate_entity): # check the cache to avoid network calls if candidate_entity in self.cache: return self.cache[candidate_entity]["title"] # pull the page from wikipedia -- if it exists try: page = wikipedia.page(candidate_entity, auto_suggest=False) entity_data = { "title": page.title, "url": page.url, "summary": page.summary, } # cache the page title and original entity self.cache[candidate_entity] = entity_data self.cache[page.title] = entity_data return entity_data["title"] except: return None wiki_filter = WikiFilter() def extract_triplets_wiki(text): relations = extract_triplets(text) filtered_relations = [] for relation in relations: (subj, rel, obj) = relation filtered_subj = wiki_filter.filter(subj) filtered_obj = wiki_filter.filter(obj) # skip if at least one entity not linked to wiki if filtered_subj is None and filtered_obj is None: continue filtered_relations.append( ( filtered_subj or subj, rel, filtered_obj or obj, ) ) return filtered_relations
## Run with Llama_Index¶
In [ ]:
Copied!
```
from llama_index.core import download_loader

from llama_index.readers.papers import ArxivReader

loader = ArxivReader()
documents = loader.load_data(
    search_query="Retrieval Augmented Generation", max_results=1
)

```

from llama_index.core import download_loader from llama_index.readers.papers import ArxivReader loader = ArxivReader() documents = loader.load_data( search_query="Retrieval Augmented Generation", max_results=1 )
In [ ]:
Copied!
```
import os
import openai

os.environ["OPENAI_API_KEY"] = "sk-..."
openai.api_key = os.environ["OPENAI_API_KEY"]

```

import os import openai os.environ["OPENAI_API_KEY"] = "sk-..." openai.api_key = os.environ["OPENAI_API_KEY"]
In [ ]:
Copied!
```
from llama_index.core import Document

# merge all documents into one, since it's split by page
documents = [Document(text="".join([x.text for x in documents]))]

```

from llama_index.core import Document # merge all documents into one, since it's split by page documents = [Document(text="".join([x.text for x in documents]))]
In [ ]:
Copied!
```
from llama_index.core import Settings

# set global configs
llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo")
Settings.llm = llm
Settings.chunk_size = 256

# set up graph storage context
graph_store = SimpleGraphStore()
storage_context = StorageContext.from_defaults(graph_store=graph_store)

```

from llama_index.core import Settings # set global configs llm = OpenAI(temperature=0.1, model="gpt-3.5-turbo") Settings.llm = llm Settings.chunk_size = 256 # set up graph storage context graph_store = SimpleGraphStore() storage_context = StorageContext.from_defaults(graph_store=graph_store)
```
[nltk_data] Downloading package punkt to /tmp/llama_index...
[nltk_data]   Unzipping tokenizers/punkt.zip.

```

NOTE: This next cell takes about 4mins on GPU.
In [ ]:
Copied!
```
index = KnowledgeGraphIndex.from_documents(
    documents,
    max_triplets_per_chunk=3,
    kg_triplet_extract_fn=extract_triplets,
    storage_context=storage_context,
    include_embeddings=True,
)

index1 = KnowledgeGraphIndex.from_documents(
    documents,
    max_triplets_per_chunk=3,
    kg_triplet_extract_fn=extract_triplets_wiki,
    storage_context=storage_context,
    include_embeddings=True,
)

```

index = KnowledgeGraphIndex.from_documents( documents, max_triplets_per_chunk=3, kg_triplet_extract_fn=extract_triplets, storage_context=storage_context, include_embeddings=True, ) index1 = KnowledgeGraphIndex.from_documents( documents, max_triplets_per_chunk=3, kg_triplet_extract_fn=extract_triplets_wiki, storage_context=storage_context, include_embeddings=True, )
```
/usr/local/lib/python3.10/dist-packages/transformers/pipelines/base.py:1101: UserWarning: You seem to be using the pipelines sequentially on GPU. In order to maximize efficiency please use a dataset
  warnings.warn(
/usr/local/lib/python3.10/dist-packages/wikipedia/wikipedia.py:389: GuessedAtParserWarning: No parser was explicitly specified, so I'm using the best available HTML parser for this system ("lxml"). This usually isn't a problem, but if you run this code on another system, or in a different virtual environment, it may use a different parser and behave differently.

The code that caused this warning is on line 389 of the file /usr/local/lib/python3.10/dist-packages/wikipedia/wikipedia.py. To get rid of this warning, pass the additional argument 'features="lxml"' to the BeautifulSoup constructor.

  lis = BeautifulSoup(html).find_all('li')

```

In [ ]:
Copied!
```
## create graph
from pyvis.network import Network

g = index.get_networkx_graph()
net = Network(notebook=True, cdn_resources="in_line", directed=True)
net.from_nx(g)
net.save_graph("non_filtered_graph.html")

from IPython.display import HTML

HTML(filename="non_filtered_graph.html")

```

## create graph from pyvis.network import Network g = index.get_networkx_graph() net = Network(notebook=True, cdn_resources="in_line", directed=True) net.from_nx(g) net.save_graph("non_filtered_graph.html") from IPython.display import HTML HTML(filename="non_filtered_graph.html")
In [ ]:
Copied!
```
## create graph
from pyvis.network import Network

g = index1.get_networkx_graph()
net = Network(notebook=True, cdn_resources="in_line", directed=True)
net.from_nx(g)
net.save_graph("wiki_filtered_graph.html")

from IPython.display import HTML

HTML(filename="wiki_filtered_graph.html")

```

## create graph from pyvis.network import Network g = index1.get_networkx_graph() net = Network(notebook=True, cdn_resources="in_line", directed=True) net.from_nx(g) net.save_graph("wiki_filtered_graph.html") from IPython.display import HTML HTML(filename="wiki_filtered_graph.html")
