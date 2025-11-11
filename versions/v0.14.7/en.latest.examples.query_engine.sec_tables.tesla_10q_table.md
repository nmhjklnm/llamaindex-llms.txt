![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Joint Tabular/Semantic QA over Tesla 10K¶
In this example, we show how to ask questions over 10K with understanding of both the unstructured text as well as embedded tables.
We use Unstructured to parse out the tables, and use LlamaIndex recursive retrieval to index/retrieve tables if necessary given the user question.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-file
%pip install llama-index-llms-openai

```

%pip install llama-index-readers-file %pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
%load_ext autoreload
%autoreload 2

```

%load_ext autoreload %autoreload 2
In [ ]:
Copied!
```
from pydantic import BaseModel
from unstructured.partition.html import partition_html
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)

```

from pydantic import BaseModel from unstructured.partition.html import partition_html import pandas as pd pd.set_option("display.max_rows", None) pd.set_option("display.max_columns", None) pd.set_option("display.width", None) pd.set_option("display.max_colwidth", None)
## Perform Data Extraction¶
In these sections we use Unstructured to parse out the table and non-table elements.
### Extract Elements¶
We use Unstructured to extract table and non-table elements from the 10-K filing.
In [ ]:
Copied!
```
!wget "https://www.dropbox.com/scl/fi/mlaymdy1ni1ovyeykhhuk/tesla_2021_10k.htm?rlkey=qf9k4zn0ejrbm716j0gg7r802&dl=1" -O tesla_2021_10k.htm
!wget "https://www.dropbox.com/scl/fi/rkw0u959yb4w8vlzz76sa/tesla_2020_10k.htm?rlkey=tfkdshswpoupav5tqigwz1mp7&dl=1" -O tesla_2020_10k.htm

```

!wget "https://www.dropbox.com/scl/fi/mlaymdy1ni1ovyeykhhuk/tesla_2021_10k.htm?rlkey=qf9k4zn0ejrbm716j0gg7r802&dl=1" -O tesla_2021_10k.htm !wget "https://www.dropbox.com/scl/fi/rkw0u959yb4w8vlzz76sa/tesla_2020_10k.htm?rlkey=tfkdshswpoupav5tqigwz1mp7&dl=1" -O tesla_2020_10k.htm
In [ ]:
Copied!
```
from llama_index.readers.file import FlatReader
from pathlib import Path

reader = FlatReader()
docs_2021 = reader.load_data(Path("tesla_2021_10k.htm"))
docs_2020 = reader.load_data(Path("tesla_2020_10k.htm"))

```

from llama_index.readers.file import FlatReader from pathlib import Path reader = FlatReader() docs_2021 = reader.load_data(Path("tesla_2021_10k.htm")) docs_2020 = reader.load_data(Path("tesla_2020_10k.htm"))
In [ ]:
Copied!
```
from llama_index.core.node_parser import UnstructuredElementNodeParser

node_parser = UnstructuredElementNodeParser()

```

from llama_index.core.node_parser import UnstructuredElementNodeParser node_parser = UnstructuredElementNodeParser()
In [ ]:
Copied!
```
import os
import pickle

if not os.path.exists("2021_nodes.pkl"):
    raw_nodes_2021 = node_parser.get_nodes_from_documents(docs_2021)
    pickle.dump(raw_nodes_2021, open("2021_nodes.pkl", "wb"))
else:
    raw_nodes_2021 = pickle.load(open("2021_nodes.pkl", "rb"))

```

import os import pickle if not os.path.exists("2021_nodes.pkl"): raw_nodes_2021 = node_parser.get_nodes_from_documents(docs_2021) pickle.dump(raw_nodes_2021, open("2021_nodes.pkl", "wb")) else: raw_nodes_2021 = pickle.load(open("2021_nodes.pkl", "rb"))
```
100%|██████████████████████████████████████████████████████████████████| 105/105 [14:59<00:00,  8.56s/it]

```

In [ ]:
Copied!
```
base_nodes_2021, node_mappings_2021 = node_parser.get_base_nodes_and_mappings(
    raw_nodes_2021
)

```

base_nodes_2021, node_mappings_2021 = node_parser.get_base_nodes_and_mappings( raw_nodes_2021 )
In [ ]:
Copied!
```
example_index_node = [b for b in base_nodes_2021 if isinstance(b, IndexNode)][
    20
]

# Index Node
print(
    f"\n--------\n{example_index_node.get_content(metadata_mode='all')}\n--------\n"
)
# Index Node ID
print(f"\n--------\nIndex ID: {example_index_node.index_id}\n--------\n")
# Referenceed Table
print(
    f"\n--------\n{node_mappings_2021[example_index_node.index_id].get_content()}\n--------\n"
)

```

example_index_node = [b for b in base_nodes_2021 if isinstance(b, IndexNode)][ 20 ] # Index Node print( f"\n--------\n{example_index_node.get_content(metadata_mode='all')}\n--------\n" ) # Index Node ID print(f"\n--------\nIndex ID: {example_index_node.index_id}\n--------\n") # Referenceed Table print( f"\n--------\n{node_mappings_2021[example_index_node.index_id].get_content()}\n--------\n" )
```
--------
col_schema: Column: Type
Type: string
Summary: Type of net income (loss) per share calculation (basic or diluted)

Column: Amount
Type: string
Summary: Net income (loss) per share amount

Column: Weighted Average Shares
Type: string
Summary: Number of shares used in calculating net income (loss) per share

Summary of net income (loss) per share of common stock attributable to common stockholders
--------


--------
Index ID: id_617_table
--------


--------
                                                                                                                                                                                                                                             
0                                                                                                                       Year Ended December 31,                                                                                              
1                                                                                                                                          2021                      2020                      2019                                          
2                                                    Revenues                                                                                                                                                                                
3                                            Automotive sales                                                                                 $    44,125                    $    24,604                     $    19,358                     
4                               Automotive regulatory credits                                                                                       1,465                          1,580                             594                     
5                                          Automotive leasing                                                                                       1,642                          1,052                             869                     
6                                   Total automotive revenues                                                                                      47,232                         27,236                          20,821                     
7                               Energy generation and storage                                                                                       2,789                          1,994                           1,531                     
8                                          Services and other                                                                                       3,802                          2,306                           2,226                     
9                                              Total revenues                                                                                      53,823                         31,536                          24,578                     
10                                           Cost of revenues                                                                                                                                                                                
11                                           Automotive sales                                                                                      32,415                         19,696                          15,939                     
12                                         Automotive leasing                                                                                         978                            563                             459                     
13                          Total automotive cost of revenues                                                                                      33,393                         20,259                          16,398                     
14                              Energy generation and storage                                                                                       2,918                          1,976                           1,341                     
15                                         Services and other                                                                                       3,906                          2,671                           2,770                     
16                                     Total cost of revenues                                                                                      40,217                         24,906                          20,509                     
17                                               Gross profit                                                                                      13,606                          6,630                           4,069                     
18                                         Operating expenses                                                                                                                                                                                
19                                   Research and development                                                                                       2,593                          1,491                           1,343                     
20                        Selling, general and administrative                                                                                       4,517                          3,145                           2,646                     
21                                    Restructuring and other                                                                                           (   27    )                         —                              149               
22                                   Total operating expenses                                                                                       7,083                          4,636                           4,138                     
23                              Income (loss) from operations                                                                                       6,523                          1,994                               (    69       )       
24                                            Interest income                                                                                          56                             30                              44                     
25                                           Interest expense                                                                                           (  371    )                         (   748     )                       (  685    )  
26                                Other income (expense), net                                                                                         135                              (  122        )                      45               
27                          Income (loss) before income taxes                                                                                       6,343                          1,154                               (   665       )       
28                                 Provision for income taxes                                                                                         699                            292                             110                     
29                                          Net income (loss)                                                                                       5,644                            862                               (   775       )       
30    Net income attributable to noncontrolling interests and  redeemable noncontrolling interests in subsidiaries                                         125                            141                               87               
31      Net income (loss) attributable to common stockholders                                                                                 $     5,519                    $       721                     $         (   862       )       
32                                                                                                                                                                                                                                           
33                Net income (loss) per share of common stock                  attributable to common stockholders                                                                                                                           
34                                                      Basic                                                                                 $      5.60                    $      0.74                     $         (  0.98       )       
35                                                    Diluted                                                                                 $      4.90                    $      0.64                     $         (  0.98       )       
36              Weighted average shares used in computing net              income (loss) per share of common stock                                                                                                                           
37                                                      Basic                                                                                         986                            933                             887                     
38                                                    Diluted                                                                                       1,129                          1,083                             887                     
--------


```

## Setup Recursive Retriever¶
Now that we've extracted tables and their summaries, we can setup a recursive retriever in LlamaIndex to query these tables.
### Construct Retrievers¶
In [ ]:
Copied!
```
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import VectorStoreIndex

```

from llama_index.core.retrievers import RecursiveRetriever from llama_index.core.query_engine import RetrieverQueryEngine from llama_index.core import VectorStoreIndex
In [ ]:
Copied!
```
# construct top-level vector index + query engine
vector_index = VectorStoreIndex(base_nodes_2021)
vector_retriever = vector_index.as_retriever(similarity_top_k=1)
vector_query_engine = vector_index.as_query_engine(similarity_top_k=1)

```

# construct top-level vector index + query engine vector_index = VectorStoreIndex(base_nodes_2021) vector_retriever = vector_index.as_retriever(similarity_top_k=1) vector_query_engine = vector_index.as_query_engine(similarity_top_k=1)
In [ ]:
Copied!
```
from llama_index.core.retrievers import RecursiveRetriever

recursive_retriever = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever},
    node_dict=node_mappings_2021,
    verbose=True,
)
query_engine = RetrieverQueryEngine.from_args(recursive_retriever)

```

from llama_index.core.retrievers import RecursiveRetriever recursive_retriever = RecursiveRetriever( "vector", retriever_dict={"vector": vector_retriever}, node_dict=node_mappings_2021, verbose=True, ) query_engine = RetrieverQueryEngine.from_args(recursive_retriever)
### Run some Queries¶
In [ ]:
Copied!
```
response = query_engine.query("What was the revenue in 2020?")
print(str(response))

```

response = query_engine.query("What was the revenue in 2020?") print(str(response))
```
Retrieving with query id None: What was the revenue in 2020?
Retrieved node with id, entering: id_478_table
Retrieving with query id id_478_table: What was the revenue in 2020?
The revenue in 2020 was $31,536 million.

```

In [ ]:
Copied!
```
# compare against the baseline retriever
response = vector_query_engine.query("What was the revenue in 2020?")
print(str(response))

```

# compare against the baseline retriever response = vector_query_engine.query("What was the revenue in 2020?") print(str(response))
```
The revenue in 2020 was a number.

```

In [ ]:
Copied!
```
response = query_engine.query("What were the total cash flows in 2021?")

```

response = query_engine.query("What were the total cash flows in 2021?")
```
Retrieving with query id None: What were the total cash flows in 2021?
Retrieved node with id, entering: id_558_table
Retrieving with query id id_558_table: What were the total cash flows in 2021?

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The total cash flows in 2021 were $11,497 million.

```

In [ ]:
Copied!
```
response = vector_query_engine.query("What were the total cash flows in 2021?")
print(str(response))

```

response = vector_query_engine.query("What were the total cash flows in 2021?") print(str(response))
```
The total cash flows in 2021 cannot be determined based on the given context information.

```

In [ ]:
Copied!
```
response = query_engine.query("What are the risk factors for Tesla?")
print(str(response))

```

response = query_engine.query("What are the risk factors for Tesla?") print(str(response))
```
Retrieving with query id None: What are the risk factors for Tesla?
Retrieving text node: Employees may leave Tesla or choose other employers over Tesla due to various factors, such as a very competitive labor market for talented individuals with automotive or technology experience, or any negative publicity related to us. In regions where we

19

have or will have operations, particularly significant engineering and manufacturing centers, there is strong competition for individuals with skillsets needed for our business, including specialized knowledge of electric vehicles, engineering and electrical and building construction expertise. Moreover, we may be impacted by perceptions relating to reductions in force that we have conducted in the past in order to optimize our organizational structure and reduce costs and the departure of certain senior personnel for various reasons. Likewise, as a result of our temporary suspension of various U.S. manufacturing operations in the first half of 2020, in April 2020, we temporarily furloughed certain hourly employees and reduced most salaried employees’ base salaries. We also compete with both mature and prosperous companies that have far greater financial resources than we do and start-ups and emerging companies that promise short-term growth opportunities.

Finally, our compensation philosophy for all of our personnel reflects our startup origins, with an emphasis on equity-based awards and benefits in order to closely align their incentives with the long-term interests of our stockholders. We periodically seek and obtain approval from our stockholders for future increases to the number of awards available under our equity incentive and employee stock purchase plans. If we are unable to obtain the requisite stockholder approvals for such future increases, we may have to expend additional cash to compensate our employees and our ability to retain and hire qualified personnel may be harmed.

We are highly dependent on the services of Elon Musk, Technoking of Tesla and our Chief Executive Officer.

We are highly dependent on the services of Elon Musk, Technoking of Tesla and our Chief Executive Officer. Although Mr. Musk spends significant time with Tesla and is highly active in our management, he does not devote his full time and attention to Tesla. Mr. Musk also currently serves as Chief Executive Officer and Chief Technical Officer of Space Exploration Technologies Corp., a developer and manufacturer of space launch vehicles, and is involved in other emerging technology ventures.

Our information technology systems or data, or those of our service providers or customers or users could be subject to cyber-attacks or other security incidents, which could result in data breaches, intellectual property theft, claims, litigation, regulatory investigations, significant liability, reputational damage and other adverse consequences.

We continue to expand our information technology systems as our operations grow, such as product data management, procurement, inventory management, production planning and execution, sales, service and logistics, dealer management, financial, tax and regulatory compliance systems. This includes the implementation of new internally developed systems and the deployment of such systems in the U.S. and abroad. While, we maintain information technology measures designed to protect us against intellectual property theft, data breaches, sabotage and other external or internal cyber-attacks or misappropriation, our systems and those of our service providers are potentially vulnerable to malware, ransomware, viruses, denial-of-service attacks, phishing attacks, social engineering, computer hacking, unauthorized access, exploitation of bugs, defects and vulnerabilities, breakdowns, damage, interruptions, system malfunctions, power outages, terrorism, acts of vandalism, security breaches, security incidents, inadvertent or intentional actions by employees or other third parties, and other cyber-attacks.

To the extent any security incident results in unauthorized access or damage to or acquisition, use, corruption, loss, destruction, alteration or dissemination of our data, including intellectual property and personal information, or our products or vehicles, or for it to be believed or reported that any of these occurred, it could disrupt our business, harm our reputation, compel us to comply with applicable data breach notification laws, subject us to time consuming, distracting and expensive litigation, regulatory investigation and oversight, mandatory corrective action, require us to verify the correctness of database contents, or otherwise subject us to liability under laws, regulations and contractual obligations, including those that protect the privacy and security of personal information. This could result in increased costs to us and result in significant legal and financial exposure and/or reputational harm.

We also rely on service providers, and similar incidents relating to their information technology systems could also have a material adverse effect on our business. There have been and may continue to be significant supply chain attacks. Our service providers, including our workforce management software provider, have been subject to ransomware and other security incidents, and we cannot guarantee that our or our service providers’ systems have not been breached or that they do not contain exploitable defects, bugs, or vulnerabilities that could result in a security incident, or other disruption to, our or our service providers’ systems. Our ability to monitor our service providers’ security measures is limited, and, in any event, malicious third parties may be able to circumvent those security measures.
The risk factors for Tesla include a highly competitive labor market for skilled individuals in the automotive and technology sectors, negative publicity, competition for individuals with specialized knowledge in electric vehicles and engineering, perceptions related to past reductions in force and departure of senior personnel, competition from companies with greater financial resources, dependence on the services of Elon Musk as CEO, potential cyber-attacks or security incidents leading to data breaches and reputational damage, and reliance on service providers who may be vulnerable to security incidents.

```

In [ ]:
Copied!
```
response = vector_query_engine.query("What are the risk factors for Tesla?")
print(str(response))

```

response = vector_query_engine.query("What are the risk factors for Tesla?") print(str(response))
```
The risk factors for Tesla include strong competition for skilled individuals in the labor market, negative publicity, potential impacts from reductions in force and departure of senior personnel, competition from companies with greater financial resources, dependence on the services of Elon Musk, potential cyber-attacks or security incidents, and reliance on service providers who may be vulnerable to security breaches. These factors could disrupt Tesla's business, harm its reputation, result in legal and financial exposure, and impact its ability to retain and hire qualified personnel.

```

## Try Table Comparisons¶
In this setting we load in both the 2021 and 2020 10K filings, parse each into a hierarchy of tables/text objects, define a recursive retriever over each, and then compose both with a SubQuestionQueryEngine.
This allows us to execute document comparisons against both.
### Define E2E Recursive Retriever Function¶
In [ ]:
Copied!
```
import pickle
import os


def create_recursive_retriever_over_doc(docs, nodes_save_path=None):
    """Big function to go from document path -> recursive retriever."""
    node_parser = UnstructuredElementNodeParser()
    if nodes_save_path is not None and os.path.exists(nodes_save_path):
        raw_nodes = pickle.load(open(nodes_save_path, "rb"))
    else:
        raw_nodes = node_parser.get_nodes_from_documents(docs)
        if nodes_save_path is not None:
            pickle.dump(raw_nodes, open(nodes_save_path, "wb"))

    base_nodes, node_mappings = node_parser.get_base_nodes_and_mappings(
        raw_nodes
    )

    ### Construct Retrievers
    # construct top-level vector index + query engine
    vector_index = VectorStoreIndex(base_nodes)
    vector_retriever = vector_index.as_retriever(similarity_top_k=2)
    recursive_retriever = RecursiveRetriever(
        "vector",
        retriever_dict={"vector": vector_retriever},
        node_dict=node_mappings,
        verbose=True,
    )
    query_engine = RetrieverQueryEngine.from_args(recursive_retriever)
    return query_engine, base_nodes

```

import pickle import os def create_recursive_retriever_over_doc(docs, nodes_save_path=None): """Big function to go from document path -> recursive retriever.""" node_parser = UnstructuredElementNodeParser() if nodes_save_path is not None and os.path.exists(nodes_save_path): raw_nodes = pickle.load(open(nodes_save_path, "rb")) else: raw_nodes = node_parser.get_nodes_from_documents(docs) if nodes_save_path is not None: pickle.dump(raw_nodes, open(nodes_save_path, "wb")) base_nodes, node_mappings = node_parser.get_base_nodes_and_mappings( raw_nodes ) ### Construct Retrievers # construct top-level vector index + query engine vector_index = VectorStoreIndex(base_nodes) vector_retriever = vector_index.as_retriever(similarity_top_k=2) recursive_retriever = RecursiveRetriever( "vector", retriever_dict={"vector": vector_retriever}, node_dict=node_mappings, verbose=True, ) query_engine = RetrieverQueryEngine.from_args(recursive_retriever) return query_engine, base_nodes
### Create Sub Question Query Engine¶
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
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine

```

from llama_index.core.tools import QueryEngineTool, ToolMetadata from llama_index.core.query_engine import SubQuestionQueryEngine
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4")

```

from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-4")
In [ ]:
Copied!
```
query_engine_2021, nodes_2021 = create_recursive_retriever_over_doc(
    docs_2021, nodes_save_path="2021_nodes.pkl"
)
query_engine_2020, nodes_2020 = create_recursive_retriever_over_doc(
    docs_2020, nodes_save_path="2020_nodes.pkl"
)

```

query_engine_2021, nodes_2021 = create_recursive_retriever_over_doc( docs_2021, nodes_save_path="2021_nodes.pkl" ) query_engine_2020, nodes_2020 = create_recursive_retriever_over_doc( docs_2020, nodes_save_path="2020_nodes.pkl" )
```
100%|████████████████████████████████████████████████████████████████████| 89/89 [06:29<00:00,  4.38s/it]

```

In [ ]:
Copied!
```
# setup base query engine as tool
query_engine_tools = [
    QueryEngineTool(
        query_engine=query_engine_2021,
        metadata=ToolMetadata(
            name="tesla_2021_10k",
            description=(
                "Provides information about Tesla financials for year 2021"
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=query_engine_2020,
        metadata=ToolMetadata(
            name="tesla_2020_10k",
            description=(
                "Provides information about Tesla financials for year 2020"
            ),
        ),
    ),
]

sub_query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
    llm=llm,
    use_async=True,
)

```

# setup base query engine as tool query_engine_tools = [ QueryEngineTool( query_engine=query_engine_2021, metadata=ToolMetadata( name="tesla_2021_10k", description=( "Provides information about Tesla financials for year 2021" ), ), ), QueryEngineTool( query_engine=query_engine_2020, metadata=ToolMetadata( name="tesla_2020_10k", description=( "Provides information about Tesla financials for year 2020" ), ), ), ] sub_query_engine = SubQuestionQueryEngine.from_defaults( query_engine_tools=query_engine_tools, llm=llm, use_async=True, )
### Try out some Comparisons¶
In [ ]:
Copied!
```
response = sub_query_engine.query(
    "Can you compare and contrast the cash flow in 2021 with 2020?"
)

```

response = sub_query_engine.query( "Can you compare and contrast the cash flow in 2021 with 2020?" )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
In 2021, Tesla's cash flow was $11,497 million, which was significantly higher than in 2020, when it was $5.94 billion. This indicates a substantial increase in cash flow from one year to the next.

```

In [ ]:
Copied!
```
response = sub_query_engine.query(
    "Can you compare and contrast the R&D expenditures in 2021 vs. 2020?"
)

```

response = sub_query_engine.query( "Can you compare and contrast the R&D expenditures in 2021 vs. 2020?" )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
In 2021, Tesla spent $2.593 billion on research and development (R&D), which was significantly higher than the $1.491 billion they spent in 2020. This indicates an increase in R&D expenditure from 2020 to 2021.

```

In [ ]:
Copied!
```
response = sub_query_engine.query(
    "Can you compare and contrast the risk factors in 2021 vs. 2020?"
)

```

response = sub_query_engine.query( "Can you compare and contrast the risk factors in 2021 vs. 2020?" )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
In 2021, Tesla faced risks such as competition for skilled labor, negative publicity, potential impacts from staff reductions and the departure of senior personnel, competition from financially stronger companies, dependence on Elon Musk, potential cyber-attacks or security incidents, competition in the energy generation and storage business, potential issues with components manufactured at their Gigafactories, risks associated with international operations, and the potential for product defects or delays in functionality.

In contrast, the risks in 2020 were largely influenced by the global COVID-19 pandemic, which affected macroeconomic conditions, government regulations, and social behaviors. This led to temporary suspensions of operations at manufacturing facilities, temporary employee furloughs and compensation reductions, and challenges in new vehicle deliveries, used vehicle sales, and energy product deployments. Global trade conditions and consumer trends, such as port congestion and microchip supply shortages, also posed risks to Tesla's business.

While both years presented unique challenges, the risks in 2021 were more related to competition, personnel, and manufacturing issues, whereas in 2020, the risks were largely driven by external factors such as the pandemic and global trade conditions.

```

#### Try Comparing against Baseline¶
In [ ]:
Copied!
```
vector_index_2021 = VectorStoreIndex(nodes_2021)
vector_query_engine_2021 = vector_index_2021.as_query_engine(
    similarity_top_k=2
)
vector_index_2020 = VectorStoreIndex(nodes_2020)
vector_query_engine_2020 = vector_index_2020.as_query_engine(
    similarity_top_k=2
)
# setup base query engine as tool
query_engine_tools = [
    QueryEngineTool(
        query_engine=vector_query_engine_2021,
        metadata=ToolMetadata(
            name="tesla_2021_10k",
            description=(
                "Provides information about Tesla financials for year 2021"
            ),
        ),
    ),
    QueryEngineTool(
        query_engine=vector_query_engine_2020,
        metadata=ToolMetadata(
            name="tesla_2020_10k",
            description=(
                "Provides information about Tesla financials for year 2020"
            ),
        ),
    ),
]

base_sub_query_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
    llm=llm,
    use_async=True,
)

```

vector_index_2021 = VectorStoreIndex(nodes_2021) vector_query_engine_2021 = vector_index_2021.as_query_engine( similarity_top_k=2 ) vector_index_2020 = VectorStoreIndex(nodes_2020) vector_query_engine_2020 = vector_index_2020.as_query_engine( similarity_top_k=2 ) # setup base query engine as tool query_engine_tools = [ QueryEngineTool( query_engine=vector_query_engine_2021, metadata=ToolMetadata( name="tesla_2021_10k", description=( "Provides information about Tesla financials for year 2021" ), ), ), QueryEngineTool( query_engine=vector_query_engine_2020, metadata=ToolMetadata( name="tesla_2020_10k", description=( "Provides information about Tesla financials for year 2020" ), ), ), ] base_sub_query_engine = SubQuestionQueryEngine.from_defaults( query_engine_tools=query_engine_tools, llm=llm, use_async=True, )
In [ ]:
Copied!
```
response = base_sub_query_engine.query(
    "Can you compare and contrast the cash flow in 2021 with 2020?"
)
print(str(response))

```

response = base_sub_query_engine.query( "Can you compare and contrast the cash flow in 2021 with 2020?" ) print(str(response))
```
Generated 2 sub questions.
[tesla_2021_10k] Q: What was the cash flow of Tesla in 2021?
[tesla_2020_10k] Q: What was the cash flow of Tesla in 2020?
[tesla_2020_10k] A: Tesla had a cash flow of $5.94 billion in 2020.
[tesla_2021_10k] A: The cash flow of Tesla in 2021 cannot be determined based on the given context information.
I'm sorry, but the cash flow of Tesla in 2021 is not specified, so a comparison with the 2020 cash flow of $5.94 billion cannot be made.

```

