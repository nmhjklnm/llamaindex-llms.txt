![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Document Summary Index¶
This demo showcases the document summary index, over Wikipedia articles on different cities.
The document summary index will extract a summary from each document and store that summary, as well as all nodes corresponding to the document.
Retrieval can be performed through the LLM or embeddings (which is a TODO). We first select the relevant documents to the query based on their summaries. All retrieved nodes corresponding to the selected documents are retrieved.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
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
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# # Uncomment if you want to temporarily disable logger
# logger = logging.getLogger()
# logger.disabled = True

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.WARNING) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout)) # # Uncomment if you want to temporarily disable logger # logger = logging.getLogger() # logger.disabled = True
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
from llama_index.core import SimpleDirectoryReader, get_response_synthesizer
from llama_index.core import DocumentSummaryIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.node_parser import SentenceSplitter

```

from llama_index.core import SimpleDirectoryReader, get_response_synthesizer from llama_index.core import DocumentSummaryIndex from llama_index.llms.openai import OpenAI from llama_index.core.node_parser import SentenceSplitter
### Load Datasets¶
Load Wikipedia pages on different cities
In [ ]:
Copied!
```
wiki_titles = ["Toronto", "Seattle", "Chicago", "Boston", "Houston"]

```

wiki_titles = ["Toronto", "Seattle", "Chicago", "Boston", "Houston"]
In [ ]:
Copied!
```
from pathlib import Path

import requests

for title in wiki_titles:
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            # 'exintro': True,
            "explaintext": True,
        },
    ).json()
    page = next(iter(response["query"]["pages"].values()))
    wiki_text = page["extract"]

    data_path = Path("data")
    if not data_path.exists():
        Path.mkdir(data_path)

    with open(data_path / f"{title}.txt", "w") as fp:
        fp.write(wiki_text)

```

from pathlib import Path import requests for title in wiki_titles: response = requests.get( "https://en.wikipedia.org/w/api.php", params={ "action": "query", "format": "json", "titles": title, "prop": "extracts", # 'exintro': True, "explaintext": True, }, ).json() page = next(iter(response["query"]["pages"].values())) wiki_text = page["extract"] data_path = Path("data") if not data_path.exists(): Path.mkdir(data_path) with open(data_path / f"{title}.txt", "w") as fp: fp.write(wiki_text)
In [ ]:
Copied!
```
# Load all wiki documents
city_docs = []
for wiki_title in wiki_titles:
    docs = SimpleDirectoryReader(
        input_files=[f"data/{wiki_title}.txt"]
    ).load_data()
    docs[0].doc_id = wiki_title
    city_docs.extend(docs)

```

# Load all wiki documents city_docs = [] for wiki_title in wiki_titles: docs = SimpleDirectoryReader( input_files=[f"data/{wiki_title}.txt"] ).load_data() docs[0].doc_id = wiki_title city_docs.extend(docs)
### Build Document Summary Index¶
We show two ways of building the index:
  * default mode of building the document summary index
  * customizing the summary query


In [ ]:
Copied!
```
# LLM (gpt-3.5-turbo)
chatgpt = OpenAI(temperature=0, model="gpt-3.5-turbo")
splitter = SentenceSplitter(chunk_size=1024)

```

# LLM (gpt-3.5-turbo) chatgpt = OpenAI(temperature=0, model="gpt-3.5-turbo") splitter = SentenceSplitter(chunk_size=1024)
In [ ]:
Copied!
```
# default mode of building the index
response_synthesizer = get_response_synthesizer(
    response_mode="tree_summarize", use_async=True
)
doc_summary_index = DocumentSummaryIndex.from_documents(
    city_docs,
    llm=chatgpt,
    transformations=[splitter],
    response_synthesizer=response_synthesizer,
    show_progress=True,
)

```

# default mode of building the index response_synthesizer = get_response_synthesizer( response_mode="tree_summarize", use_async=True ) doc_summary_index = DocumentSummaryIndex.from_documents( city_docs, llm=chatgpt, transformations=[splitter], response_synthesizer=response_synthesizer, show_progress=True, )
```
Parsing documents into nodes:   0%|          | 0/5 [00:00<?, ?it/s]
```

```
Summarizing documents:   0%|          | 0/5 [00:00<?, ?it/s]
```

```
current doc id: Toronto
current doc id: Seattle
current doc id: Chicago
current doc id: Boston
current doc id: Houston

```

```
Generating embeddings:   0%|          | 0/5 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
doc_summary_index.get_document_summary("Boston")

```

doc_summary_index.get_document_summary("Boston")
Out[ ]:
```
"The provided text is about the city of Boston and covers various aspects of the city, including its history, geography, demographics, economy, education system, healthcare facilities, public safety, culture, environment, transportation infrastructure, and international relations. It provides information on Boston's development over time, key events in its history, its significance as a cultural and educational center, its economic sectors, neighborhoods, climate, population, ethnic diversity, landmarks and attractions, colleges and universities, healthcare facilities, public safety measures, cultural scene, annual events, environmental initiatives, churches, pollution control, water purity and availability, climate change and sea level rise, sports teams, parks and recreational areas, government and political system, media, and transportation infrastructure.\n\nSome questions that this text can answer include:\n- What is the history of Boston and how did it develop over time?\n- What were some key events that took place in Boston during the American Revolution?\n- What is the significance of Boston in terms of education and academic research?\n- What are some of the economic sectors that contribute to Boston's economy?\n- How has Boston changed and evolved in the 20th and 21st centuries?\n- What is the geography of Boston and how does it impact the city?\n- What are the neighborhoods in Boston?\n- What is the climate like in Boston?\n- What is the population of Boston and its demographic breakdown?\n- What is the economy of Boston like?\n- What are some notable landmarks and attractions in Boston?\n- What is the ethnic diversity of Boston?\n- What is the religious composition of Boston?\n- What is the impact of colleges and universities on the economy of Boston?\n- What is the role of technology and biotechnology in Boston's economy?\n- What healthcare facilities are located in Boston?\n- How does Boston ensure public safety?\n- What is the cultural scene like in Boston?\n- What are some of the annual events in Boston?\n- What environmental initiatives are being undertaken in Boston?\n- What are some of the churches in Boston and their historical significance?\n- How does Boston control pollution and maintain air quality?\n- What is the status of water purity and availability in Boston?\n- How is Boston addressing climate change and sea level rise?\n- What sports teams are based in Boston and what championships have they won?\n- What are some of the parks and recreational areas in Boston?\n- How is the government and political system structured in Boston?\n- What are some of the major newspapers, radio stations, and television stations in Boston?\n- What is the transportation infrastructure in Boston, including the airport and major highways?\n- What are some notable movies filmed in Boston?\n- Which video games have used Boston as a setting?\n- What are some of Boston's sister cities and partnership relationships?\n- Where can I find more information about Boston's history and landmarks?"
```

In [ ]:
Copied!
```
doc_summary_index.storage_context.persist("index")

```

doc_summary_index.storage_context.persist("index")
In [ ]:
Copied!
```
from llama_index.core import load_index_from_storage
from llama_index.core import StorageContext

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="index")
doc_summary_index = load_index_from_storage(storage_context)

```

from llama_index.core import load_index_from_storage from llama_index.core import StorageContext # rebuild storage context storage_context = StorageContext.from_defaults(persist_dir="index") doc_summary_index = load_index_from_storage(storage_context)
### Perform Retrieval from Document Summary Index¶
We show how to execute queries at a high-level. We also show how to perform retrieval at a lower-level so that you can view the parameters that are in place. We show both LLM-based retrieval and embedding-based retrieval using the document summaries.
#### High-level Querying¶
Note: this uses the default, embedding-based form of retrieval
In [ ]:
Copied!
```
query_engine = doc_summary_index.as_query_engine(
    response_mode="tree_summarize", use_async=True
)

```

query_engine = doc_summary_index.as_query_engine( response_mode="tree_summarize", use_async=True )
In [ ]:
Copied!
```
response = query_engine.query("What are the sports teams in Toronto?")

```

response = query_engine.query("What are the sports teams in Toronto?")
In [ ]:
Copied!
```
print(response)

```

print(response)
```
The sports teams in Toronto include the Toronto Maple Leafs (NHL), Toronto Raptors (NBA), Toronto Blue Jays (MLB), Toronto FC (MLS), Toronto Argonauts (CFL), Toronto Six (NWHL), Toronto Rock (National Lacrosse League), Toronto Wolfpack (Rugby Football League), and Toronto Rush (American Ultimate Disc League).

```

#### LLM-based Retrieval¶
In [ ]:
Copied!
```
from llama_index.core.indices.document_summary import (
    DocumentSummaryIndexLLMRetriever,
)

```

from llama_index.core.indices.document_summary import ( DocumentSummaryIndexLLMRetriever, )
In [ ]:
Copied!
```
retriever = DocumentSummaryIndexLLMRetriever(
    doc_summary_index,
    # choice_select_prompt=None,
    # choice_batch_size=10,
    # choice_top_k=1,
    # format_node_batch_fn=None,
    # parse_choice_select_answer_fn=None,
)

```

retriever = DocumentSummaryIndexLLMRetriever( doc_summary_index, # choice_select_prompt=None, # choice_batch_size=10, # choice_top_k=1, # format_node_batch_fn=None, # parse_choice_select_answer_fn=None, )
In [ ]:
Copied!
```
retrieved_nodes = retriever.retrieve("What are the sports teams in Toronto?")

```

retrieved_nodes = retriever.retrieve("What are the sports teams in Toronto?")
In [ ]:
Copied!
```
print(len(retrieved_nodes))

```

print(len(retrieved_nodes))


In [ ]:
Copied!
```
print(retrieved_nodes[0].score)
print(retrieved_nodes[0].node.get_text())

```

print(retrieved_nodes[0].score) print(retrieved_nodes[0].node.get_text())
```
10.0
Toronto is the most populous city in Canada and the capital city of the Canadian province of Ontario. With a recorded population of 2,794,356 in 2021, it is the fourth-most populous city in North America. The city is the anchor of the Golden Horseshoe, an urban agglomeration of 9,765,188 people (as of 2021) surrounding the western end of Lake Ontario, while the Greater Toronto Area proper had a 2021 population of 6,712,341. Toronto is an international centre of business, finance, arts, sports and culture, and is recognized as one of the most multicultural and cosmopolitan cities in the world.Indigenous peoples have travelled through and inhabited the Toronto area, located on a broad sloping plateau interspersed with rivers, deep ravines, and urban forest, for more than 10,000 years. After the broadly disputed Toronto Purchase, when the Mississauga surrendered the area to the British Crown, the British established the town of York in 1793 and later designated it as the capital of Upper Canada. During the War of 1812, the town was the site of the Battle of York and suffered heavy damage by American troops. York was renamed and incorporated in 1834 as the city of Toronto. It was designated as the capital of the province of Ontario in 1867 during Canadian Confederation. The city proper has since expanded past its original limits through both annexation and amalgamation to its current area of 630.2 km2 (243.3 sq mi).
The diverse population of Toronto reflects its current and historical role as an important destination for immigrants to Canada. More than half of residents were born outside of Canada, more than half of residents belong to a visible minority group, and over 200 distinct ethnic origins are represented among its inhabitants. While the majority of Torontonians speak English as their primary language, over 160 languages are spoken in the city. The mayor of Toronto is elected by direct popular vote to serve as the chief executive of the city. The Toronto City Council is a unicameral legislative body, comprising 25 councillors since the 2018 municipal election, representing geographical wards throughout the city.Toronto is a prominent centre for music, theatre, motion picture production, and television production, and is home to the headquarters of Canada's major national broadcast networks and media outlets. Its varied cultural institutions, which include numerous museums and galleries, festivals and public events, entertainment districts, national historic sites, and sports activities, attract over 43 million tourists each year. Toronto is known for its many skyscrapers and high-rise buildings, in particular the tallest free-standing structure on land outside of Asia, the CN Tower.The city is home to the Toronto Stock Exchange, the headquarters of Canada's five largest banks, and the headquarters of many large Canadian and multinational corporations. Its economy is highly diversified with strengths in technology, design, financial services, life sciences, education, arts, fashion, aerospace, environmental innovation, food services, and tourism. Toronto is the third-largest tech hub in North America after Silicon Valley and New York City, and the fastest growing.


== Toponymy ==

The word Toronto has been recorded with various spellings in French and English, including Tarento, Tarontha, Taronto, Toranto, Torento, Toronto, and Toronton. Taronto referred to "The Narrows", a channel of water through which Lake Simcoe discharges into Lake Couchiching where the Huron had planted tree saplings to corral fish. This narrows was called tkaronto by the Mohawk, meaning "where there are trees standing in the water," and was recorded as early as 1615 by Samuel de Champlain. The word "Toronto", meaning "plenty" also appears in a 1632 French lexicon of the Huron language, which is also an Iroquoian language. It also appears on French maps referring to various locations, including Georgian Bay, Lake Simcoe, and several rivers. A portage route from Lake Ontario to Lake Huron running through this point, known as the Toronto Carrying-Place Trail, led to widespread use of the name.
The pronunciation of the city is broadly   tə-RON-toh, which locals realize as [təˈɹɒno] or [ˈtʃɹɒno], leaving the second 't' silent.


== History ==

```

In [ ]:
Copied!
```
# use retriever as part of a query engine
from llama_index.core.query_engine import RetrieverQueryEngine

# configure response synthesizer
response_synthesizer = get_response_synthesizer(response_mode="tree_summarize")

# assemble query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
)

# query
response = query_engine.query("What are the sports teams in Toronto?")
print(response)

```

# use retriever as part of a query engine from llama_index.core.query_engine import RetrieverQueryEngine # configure response synthesizer response_synthesizer = get_response_synthesizer(response_mode="tree_summarize") # assemble query engine query_engine = RetrieverQueryEngine( retriever=retriever, response_synthesizer=response_synthesizer, ) # query response = query_engine.query("What are the sports teams in Toronto?") print(response)
```
The sports teams in Toronto include the Toronto Maple Leafs (NHL), Toronto Raptors (NBA), Toronto Blue Jays (MLB), Toronto FC (MLS), and Toronto Argonauts (CFL).

```

#### Embedding-based Retrieval¶
In [ ]:
Copied!
```
from llama_index.core.indices.document_summary import (
    DocumentSummaryIndexEmbeddingRetriever,
)

```

from llama_index.core.indices.document_summary import ( DocumentSummaryIndexEmbeddingRetriever, )
In [ ]:
Copied!
```
retriever = DocumentSummaryIndexEmbeddingRetriever(
    doc_summary_index,
    # similarity_top_k=1,
)

```

retriever = DocumentSummaryIndexEmbeddingRetriever( doc_summary_index, # similarity_top_k=1, )
In [ ]:
Copied!
```
retrieved_nodes = retriever.retrieve("What are the sports teams in Toronto?")

```

retrieved_nodes = retriever.retrieve("What are the sports teams in Toronto?")
In [ ]:
Copied!
```
len(retrieved_nodes)

```

len(retrieved_nodes)
Out[ ]:


In [ ]:
Copied!
```
print(retrieved_nodes[0].node.get_text())

```

print(retrieved_nodes[0].node.get_text())
```
Toronto is the most populous city in Canada and the capital city of the Canadian province of Ontario. With a recorded population of 2,794,356 in 2021, it is the fourth-most populous city in North America. The city is the anchor of the Golden Horseshoe, an urban agglomeration of 9,765,188 people (as of 2021) surrounding the western end of Lake Ontario, while the Greater Toronto Area proper had a 2021 population of 6,712,341. Toronto is an international centre of business, finance, arts, sports and culture, and is recognized as one of the most multicultural and cosmopolitan cities in the world.Indigenous peoples have travelled through and inhabited the Toronto area, located on a broad sloping plateau interspersed with rivers, deep ravines, and urban forest, for more than 10,000 years. After the broadly disputed Toronto Purchase, when the Mississauga surrendered the area to the British Crown, the British established the town of York in 1793 and later designated it as the capital of Upper Canada. During the War of 1812, the town was the site of the Battle of York and suffered heavy damage by American troops. York was renamed and incorporated in 1834 as the city of Toronto. It was designated as the capital of the province of Ontario in 1867 during Canadian Confederation. The city proper has since expanded past its original limits through both annexation and amalgamation to its current area of 630.2 km2 (243.3 sq mi).
The diverse population of Toronto reflects its current and historical role as an important destination for immigrants to Canada. More than half of residents were born outside of Canada, more than half of residents belong to a visible minority group, and over 200 distinct ethnic origins are represented among its inhabitants. While the majority of Torontonians speak English as their primary language, over 160 languages are spoken in the city. The mayor of Toronto is elected by direct popular vote to serve as the chief executive of the city. The Toronto City Council is a unicameral legislative body, comprising 25 councillors since the 2018 municipal election, representing geographical wards throughout the city.Toronto is a prominent centre for music, theatre, motion picture production, and television production, and is home to the headquarters of Canada's major national broadcast networks and media outlets. Its varied cultural institutions, which include numerous museums and galleries, festivals and public events, entertainment districts, national historic sites, and sports activities, attract over 43 million tourists each year. Toronto is known for its many skyscrapers and high-rise buildings, in particular the tallest free-standing structure on land outside of Asia, the CN Tower.The city is home to the Toronto Stock Exchange, the headquarters of Canada's five largest banks, and the headquarters of many large Canadian and multinational corporations. Its economy is highly diversified with strengths in technology, design, financial services, life sciences, education, arts, fashion, aerospace, environmental innovation, food services, and tourism. Toronto is the third-largest tech hub in North America after Silicon Valley and New York City, and the fastest growing.


== Toponymy ==

The word Toronto has been recorded with various spellings in French and English, including Tarento, Tarontha, Taronto, Toranto, Torento, Toronto, and Toronton. Taronto referred to "The Narrows", a channel of water through which Lake Simcoe discharges into Lake Couchiching where the Huron had planted tree saplings to corral fish. This narrows was called tkaronto by the Mohawk, meaning "where there are trees standing in the water," and was recorded as early as 1615 by Samuel de Champlain. The word "Toronto", meaning "plenty" also appears in a 1632 French lexicon of the Huron language, which is also an Iroquoian language. It also appears on French maps referring to various locations, including Georgian Bay, Lake Simcoe, and several rivers. A portage route from Lake Ontario to Lake Huron running through this point, known as the Toronto Carrying-Place Trail, led to widespread use of the name.
The pronunciation of the city is broadly   tə-RON-toh, which locals realize as [təˈɹɒno] or [ˈtʃɹɒno], leaving the second 't' silent.


== History ==

```

In [ ]:
Copied!
```
# use retriever as part of a query engine
from llama_index.core.query_engine import RetrieverQueryEngine

# configure response synthesizer
response_synthesizer = get_response_synthesizer(response_mode="tree_summarize")

# assemble query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
)

# query
response = query_engine.query("What are the sports teams in Toronto?")
print(response)

```

# use retriever as part of a query engine from llama_index.core.query_engine import RetrieverQueryEngine # configure response synthesizer response_synthesizer = get_response_synthesizer(response_mode="tree_summarize") # assemble query engine query_engine = RetrieverQueryEngine( retriever=retriever, response_synthesizer=response_synthesizer, ) # query response = query_engine.query("What are the sports teams in Toronto?") print(response)
```
The sports teams in Toronto include the Toronto Maple Leafs (NHL), Toronto Raptors (NBA), Toronto Blue Jays (MLB), Toronto FC (MLS), Toronto Argonauts (CFL), Toronto Rock (NLL), Toronto Wolfpack (Rugby Football League), Toronto Six (NWHL), and Toronto Rush (American Ultimate Disc League).

```

