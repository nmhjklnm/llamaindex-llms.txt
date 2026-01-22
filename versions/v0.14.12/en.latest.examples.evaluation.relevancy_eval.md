# Relevancy Evaluator¶
This notebook uses the `RelevancyEvaluator` to measure if the response + source nodes match the query.  
This is useful for measuring if the query was actually answered by the response.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai pandas[jinja2] spacy

```

%pip install llama-index-llms-openai pandas[jinja2] spacy
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
from llama_index.core import (
    TreeIndex,
    VectorStoreIndex,
    SimpleDirectoryReader,
    Response,
)
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import RelevancyEvaluator
from llama_index.core.node_parser import SentenceSplitter
import pandas as pd

pd.set_option("display.max_colwidth", 0)

```

from llama_index.core import ( TreeIndex, VectorStoreIndex, SimpleDirectoryReader, Response, ) from llama_index.llms.openai import OpenAI from llama_index.core.evaluation import RelevancyEvaluator from llama_index.core.node_parser import SentenceSplitter import pandas as pd pd.set_option("display.max_colwidth", 0)
In [ ]:
Copied!
```
# gpt-3 (davinci)
gpt3 = OpenAI(temperature=0, model="gpt-3.5-turbo")

# gpt-4
gpt4 = OpenAI(temperature=0, model="gpt-4")

```

# gpt-3 (davinci) gpt3 = OpenAI(temperature=0, model="gpt-3.5-turbo") # gpt-4 gpt4 = OpenAI(temperature=0, model="gpt-4")
In [ ]:
Copied!
```
evaluator = RelevancyEvaluator(llm=gpt3)
evaluator_gpt4 = RelevancyEvaluator(llm=gpt4)

```

evaluator = RelevancyEvaluator(llm=gpt3) evaluator_gpt4 = RelevancyEvaluator(llm=gpt4)
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("./test_wiki_data").load_data()

```

documents = SimpleDirectoryReader("./test_wiki_data").load_data()
In [ ]:
Copied!
```
# create vector index
splitter = SentenceSplitter(chunk_size=512)
vector_index = VectorStoreIndex.from_documents(
    documents, transformations=[splitter]
)

```

# create vector index splitter = SentenceSplitter(chunk_size=512) vector_index = VectorStoreIndex.from_documents( documents, transformations=[splitter] )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
from llama_index.core.evaluation import EvaluationResult


# define jupyter display function
def display_eval_df(
    query: str, response: Response, eval_result: EvaluationResult
) -> None:
    eval_df = pd.DataFrame(
        {
            "Query": query,
            "Response": str(response),
            "Source": response.source_nodes[0].node.text[:1000] + "...",
            "Evaluation Result": "Pass" if eval_result.passing else "Fail",
            "Reasoning": eval_result.feedback,
        },
        index=[0],
    )
    eval_df = eval_df.style.set_properties(
        **{
            "inline-size": "600px",
            "overflow-wrap": "break-word",
        },
        subset=["Response", "Source"]
    )
    display(eval_df)

```

from llama_index.core.evaluation import EvaluationResult # define jupyter display function def display_eval_df( query: str, response: Response, eval_result: EvaluationResult ) -> None: eval_df = pd.DataFrame( { "Query": query, "Response": str(response), "Source": response.source_nodes[0].node.text[:1000] + "...", "Evaluation Result": "Pass" if eval_result.passing else "Fail", "Reasoning": eval_result.feedback, }, index=[0], ) eval_df = eval_df.style.set_properties( **{ "inline-size": "600px", "overflow-wrap": "break-word", }, subset=["Response", "Source"] ) display(eval_df)
### Evaluate Response¶
Evaluate response relative to source nodes as well as query.
In [ ]:
Copied!
```
query_str = (
    "What battles took place in New York City in the American Revolution?"
)
query_engine = vector_index.as_query_engine()
response_vector = query_engine.query(query_str)
eval_result = evaluator_gpt4.evaluate_response(
    query=query_str, response=response_vector
)

```

query_str = ( "What battles took place in New York City in the American Revolution?" ) query_engine = vector_index.as_query_engine() response_vector = query_engine.query(query_str) eval_result = evaluator_gpt4.evaluate_response( query=query_str, response=response_vector )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display_eval_df(query_str, response_vector, eval_result)

```

display_eval_df(query_str, response_vector, eval_result)
| Query | Response | Source | Evaluation Result | Reasoning  
---|---|---|---|---|---  
0 | What battles took place in New York City in the American Revolution? | The Battle of Long Island was the largest battle of the American Revolutionary War that took place in New York City. | === American Revolution === The Stamp Act Congress met in New York in October 1765, as the Sons of Liberty organization emerged in the city and skirmished over the next ten years with British troops stationed there. The Battle of Long Island, the largest battle of the American Revolutionary War, was fought in August 1776 within the modern-day borough of Brooklyn. After the battle, in which the Americans were defeated, the British made the city their military and political base of operations in North America. The city was a haven for Loyalist refugees and escaped slaves who joined the British lines for freedom newly promised by the Crown for all fighters. As many as 10,000 escaped slaves crowded into the city during the British occupation. When the British forces evacuated at the close of the war in 1783, they transported 3,000 freedmen for resettlement in Nova Scotia. They resettled other freedmen in England and the Caribbean. The only attempt at a peaceful solution to the war took pl... | Pass | The context confirms that the Battle of Long Island, which was the largest battle of the American Revolutionary War, took place in New York City.  
In [ ]:
Copied!
```
query_str = "What are the airports in New York City?"
query_engine = vector_index.as_query_engine()
response_vector = query_engine.query(query_str)
eval_result = evaluator_gpt4.evaluate_response(
    query=query_str, response=response_vector
)

```

query_str = "What are the airports in New York City?" query_engine = vector_index.as_query_engine() response_vector = query_engine.query(query_str) eval_result = evaluator_gpt4.evaluate_response( query=query_str, response=response_vector )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display_eval_df(query_str, response_vector, eval_result)

```

display_eval_df(query_str, response_vector, eval_result)
| Query | Response | Source | Evaluation Result | Reasoning  
---|---|---|---|---|---  
0 | What are the airports in New York City? | The airports in New York City include John F. Kennedy International Airport, Newark Liberty International Airport, LaGuardia Airport, Stewart International Airport, Long Island MacArthur Airport, Trenton-Mercer Airport, and Westchester County Airport. | along the Northeast Corridor, and long-distance train service to other North American cities.The Staten Island Railway rapid transit system solely serves Staten Island, operating 24 hours a day. The Port Authority Trans-Hudson (PATH train) links Midtown and Lower Manhattan to northeastern New Jersey, primarily Hoboken, Jersey City, and Newark. Like the New York City Subway, the PATH operates 24 hours a day; meaning three of the six rapid transit systems in the world which operate on 24-hour schedules are wholly or partly in New York (the others are a portion of the Chicago "L", the PATCO Speedline serving Philadelphia, and the Copenhagen Metro). Multibillion-dollar heavy rail transit projects under construction in New York City include the Second Avenue Subway, and the East Side Access project. ==== Buses ==== New York City's public bus fleet runs 24/7 and is the largest in North America. The Port Authority Bus Terminal, the main intercity bus terminal of the city, serves 7,000 buse... | Pass | The context provides information about the airports in New York City, which includes John F. Kennedy International Airport, Newark Liberty International Airport, LaGuardia Airport, Stewart International Airport, Long Island MacArthur Airport, Trenton-Mercer Airport, and Westchester County Airport. This matches the response to the query.  
In [ ]:
Copied!
```
query_str = "Who is the mayor of New York City?"
query_engine = vector_index.as_query_engine()
response_vector = query_engine.query(query_str)
eval_result = evaluator_gpt4.evaluate_response(
    query=query_str, response=response_vector
)

```

query_str = "Who is the mayor of New York City?" query_engine = vector_index.as_query_engine() response_vector = query_engine.query(query_str) eval_result = evaluator_gpt4.evaluate_response( query=query_str, response=response_vector )
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display_eval_df(query_str, response_vector, eval_result)

```

display_eval_df(query_str, response_vector, eval_result)
| Query | Response | Source | Evaluation Result | Reasoning  
---|---|---|---|---|---  
0 | Who is the mayor of New York City? | The mayor of New York City is Eric Adams. | === Politics === The present mayor is Eric Adams. He was elected in 2021 with 67% of the vote, and assumed office on January 1, 2022. The Democratic Party holds the majority of public offices. As of April 2016, 69% of registered voters in the city are Democrats and 10% are Republicans. New York City has not been carried by a Republican presidential election since President Calvin Coolidge won the five boroughs in 1924. A Republican candidate for statewide office has not won all five boroughs of the city since it was incorporated in 1898. In 2012, Democrat Barack Obama became the first presidential candidate of any party to receive more than 80% of the overall vote in New York City, sweeping all five boroughs. Party platforms center on affordable housing, education, and economic development, and labor politics are of importance in the city. Thirteen out of 27 U.S. congressional districts in the state of New York include portions of New York City.New York is one of the most important so... | Pass | The context confirms that Eric Adams is the current mayor of New York City, as stated in the response.  
### Evaluate Source Nodes¶
Evaluate the set of returned sources, and determine which sources actually contain the answer to a given query.
In [ ]:
Copied!
```
from typing import List


# define jupyter display function
def display_eval_sources(
    query: str, response: Response, eval_result: List[str]
) -> None:
    sources = [s.node.get_text() for s in response.source_nodes]
    eval_df = pd.DataFrame(
        {
            "Source": sources,
            "Eval Result": eval_result,
        },
    )
    eval_df.style.set_caption(query)
    eval_df = eval_df.style.set_properties(
        **{
            "inline-size": "600px",
            "overflow-wrap": "break-word",
        },
        subset=["Source"]
    )

    display(eval_df)

```

from typing import List # define jupyter display function def display_eval_sources( query: str, response: Response, eval_result: List[str] ) -> None: sources = [s.node.get_text() for s in response.source_nodes] eval_df = pd.DataFrame( { "Source": sources, "Eval Result": eval_result, }, ) eval_df.style.set_caption(query) eval_df = eval_df.style.set_properties( **{ "inline-size": "600px", "overflow-wrap": "break-word", }, subset=["Source"] ) display(eval_df)
In [ ]:
Copied!
```
# NOTE: you can set response_mode="no_text" to get just the sources
query_str = "What are the airports in New York City?"
query_engine = vector_index.as_query_engine(
    similarity_top_k=3, response_mode="no_text"
)
response_vector = query_engine.query(query_str)
eval_source_result_full = [
    evaluator_gpt4.evaluate(
        query=query_str,
        response=response_vector.response,
        contexts=[source_node.get_content()],
    )
    for source_node in response_vector.source_nodes
]
eval_source_result = [
    "Pass" if result.passing else "Fail" for result in eval_source_result_full
]

```

# NOTE: you can set response_mode="no_text" to get just the sources query_str = "What are the airports in New York City?" query_engine = vector_index.as_query_engine( similarity_top_k=3, response_mode="no_text" ) response_vector = query_engine.query(query_str) eval_source_result_full = [ evaluator_gpt4.evaluate( query=query_str, response=response_vector.response, contexts=[source_node.get_content()], ) for source_node in response_vector.source_nodes ] eval_source_result = [ "Pass" if result.passing else "Fail" for result in eval_source_result_full ]
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/embeddings "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display_eval_sources(query_str, response_vector, eval_source_result)

```

display_eval_sources(query_str, response_vector, eval_source_result)
| Source | Eval Result  
---|---|---  
0 | along the Northeast Corridor, and long-distance train service to other North American cities.The Staten Island Railway rapid transit system solely serves Staten Island, operating 24 hours a day. The Port Authority Trans-Hudson (PATH train) links Midtown and Lower Manhattan to northeastern New Jersey, primarily Hoboken, Jersey City, and Newark. Like the New York City Subway, the PATH operates 24 hours a day; meaning three of the six rapid transit systems in the world which operate on 24-hour schedules are wholly or partly in New York (the others are a portion of the Chicago "L", the PATCO Speedline serving Philadelphia, and the Copenhagen Metro). Multibillion-dollar heavy rail transit projects under construction in New York City include the Second Avenue Subway, and the East Side Access project. ==== Buses ==== New York City's public bus fleet runs 24/7 and is the largest in North America. The Port Authority Bus Terminal, the main intercity bus terminal of the city, serves 7,000 buses and 200,000 commuters daily, making it the busiest bus station in the world. === Air === New York's airspace is the busiest in the United States and one of the world's busiest air transportation corridors. The three busiest airports in the New York metropolitan area include John F. Kennedy International Airport, Newark Liberty International Airport, and LaGuardia Airport; 130.5 million travelers used these three airports in 2016. JFK and Newark Liberty were the busiest and fourth busiest U.S. gateways for international air passengers, respectively, in 2012; as of 2011, JFK was the busiest airport for international passengers in North America.Plans have advanced to expand passenger volume at a fourth airport, Stewart International Airport near Newburgh, New York, by the Port Authority of New York and New Jersey. Plans were announced in July 2015 to entirely rebuild LaGuardia Airport in a multibillion-dollar project to replace its aging facilities. Other commercial airports in or serving the New York metropolitan area include Long Island MacArthur Airport, Trenton–Mercer Airport and Westchester County Airport. The primary general aviation airport serving the area is Teterboro Airport. | Pass  
1 | See or edit raw graph data. === Parks === The city of New York has a complex park system, with various lands operated by the National Park Service, the New York State Office of Parks, Recreation and Historic Preservation, and the New York City Department of Parks and Recreation. In its 2018 ParkScore ranking, the Trust for Public Land reported that the park system in New York City was the ninth-best park system among the fifty most populous U.S. cities. ParkScore ranks urban park systems by a formula that analyzes median park size, park acres as percent of city area, the percent of city residents within a half-mile of a park, spending of park services per resident, and the number of playgrounds per 10,000 residents. In 2021, the New York City Council banned the use of synthetic pesticides by city agencies and instead required organic lawn management. The effort was started by teacher Paula Rogovin's kindergarten class at P.S. 290. ==== National parks ==== Gateway National Recreation Area contains over 26,000 acres (110 km2), most of it in New York City. In Brooklyn and Queens, the park contains over 9,000 acres (36 km2) of salt marsh, wetlands, islands, and water, including most of Jamaica Bay and the Jamaica Bay Wildlife Refuge. Also in Queens, the park includes a significant portion of the western Rockaway Peninsula, most notably Jacob Riis Park and Fort Tilden. In Staten Island, it includes Fort Wadsworth, with historic pre-Civil War era Battery Weed and Fort Tompkins, and Great Kills Park, with beaches, trails, and a marina. The Statue of Liberty National Monument and Ellis Island Immigration Museum are managed by the National Park Service and are in both New York and New Jersey. They are joined in the harbor by Governors Island National Monument. Historic sites under federal management on Manhattan Island include Stonewall National Monument; Castle Clinton National Monument; Federal Hall National Memorial; Theodore Roosevelt Birthplace National Historic Site; General Grant National Memorial (Grant's Tomb); African Burial Ground National Monument; and Hamilton Grange National Memorial. Hundreds of properties are listed on the National Register of Historic Places or as a National Historic Landmark. | Fail  
2 | New York has witnessed a growing combined volume of international and domestic tourists, reflecting over 60 million visitors to the city per year, the world's busiest tourist destination. Approximately 12 million visitors to New York City have been from outside the United States, with the highest numbers from the United Kingdom, Canada, Brazil, and China. Multiple sources have called New York the most photographed city in the world.I Love New York (stylized I ❤ NY) is both a logo and a song that are the basis of an advertising campaign and have been used since 1977 to promote tourism in New York City, and later to promote New York State as well. The trademarked logo, owned by New York State Empire State Development, appears in souvenir shops and brochures throughout the city and state, some licensed, many not. The song is the state song of New York. The majority of the most high-profile tourist destinations to the city are situated in Manhattan. These include Times Square; Broadway theater productions; the Empire State Building; the Statue of Liberty; Ellis Island; the United Nations headquarters; the World Trade Center (including the National September 11 Memorial & Museum and One World Trade Center); the art museums along Museum Mile; green spaces such as Central Park, Washington Square Park, the High Line, and the medieval gardens of The Cloisters; the Stonewall Inn; Rockefeller Center; ethnic enclaves including the Manhattan Chinatown, Koreatown, Curry Hill, Harlem, Spanish Harlem, Little Italy, and Little Australia; luxury shopping along Fifth and Madison Avenues; and events such as the Halloween Parade in Greenwich Village; the Brooklyn Bridge (shared with Brooklyn); the Macy's Thanksgiving Day Parade; the lighting of the Rockefeller Center Christmas Tree; the St. Patrick's Day Parade; seasonal activities such as ice skating in Central Park in the wintertime; the Tribeca Film Festival; and free performances in Central Park at SummerStage.Points of interest have also developed in the city outside Manhattan and have made the outer boroughs tourist destinations in their own right. | Fail  
In [ ]:
Copied!
```
# NOTE: you can set response_mode="no_text" to get just the sources
query_str = "Who is the mayor of New York City?"
query_engine = vector_index.as_query_engine(
    similarity_top_k=3, response_mode="no_text"
)
eval_source_result_full = [
    evaluator_gpt4.evaluate(
        query=query_str,
        response=response_vector.response,
        contexts=[source_node.get_content()],
    )
    for source_node in response_vector.source_nodes
]
eval_source_result = [
    "Pass" if result.passing else "Fail" for result in eval_source_result_full
]

```

# NOTE: you can set response_mode="no_text" to get just the sources query_str = "Who is the mayor of New York City?" query_engine = vector_index.as_query_engine( similarity_top_k=3, response_mode="no_text" ) eval_source_result_full = [ evaluator_gpt4.evaluate( query=query_str, response=response_vector.response, contexts=[source_node.get_content()], ) for source_node in response_vector.source_nodes ] eval_source_result = [ "Pass" if result.passing else "Fail" for result in eval_source_result_full ]
```
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
INFO:httpx:HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"

```

In [ ]:
Copied!
```
display_eval_sources(query_str, response_vector, eval_source_result)

```

display_eval_sources(query_str, response_vector, eval_source_result)
| Source | Eval Result  
---|---|---  
0 | along the Northeast Corridor, and long-distance train service to other North American cities.The Staten Island Railway rapid transit system solely serves Staten Island, operating 24 hours a day. The Port Authority Trans-Hudson (PATH train) links Midtown and Lower Manhattan to northeastern New Jersey, primarily Hoboken, Jersey City, and Newark. Like the New York City Subway, the PATH operates 24 hours a day; meaning three of the six rapid transit systems in the world which operate on 24-hour schedules are wholly or partly in New York (the others are a portion of the Chicago "L", the PATCO Speedline serving Philadelphia, and the Copenhagen Metro). Multibillion-dollar heavy rail transit projects under construction in New York City include the Second Avenue Subway, and the East Side Access project. ==== Buses ==== New York City's public bus fleet runs 24/7 and is the largest in North America. The Port Authority Bus Terminal, the main intercity bus terminal of the city, serves 7,000 buses and 200,000 commuters daily, making it the busiest bus station in the world. === Air === New York's airspace is the busiest in the United States and one of the world's busiest air transportation corridors. The three busiest airports in the New York metropolitan area include John F. Kennedy International Airport, Newark Liberty International Airport, and LaGuardia Airport; 130.5 million travelers used these three airports in 2016. JFK and Newark Liberty were the busiest and fourth busiest U.S. gateways for international air passengers, respectively, in 2012; as of 2011, JFK was the busiest airport for international passengers in North America.Plans have advanced to expand passenger volume at a fourth airport, Stewart International Airport near Newburgh, New York, by the Port Authority of New York and New Jersey. Plans were announced in July 2015 to entirely rebuild LaGuardia Airport in a multibillion-dollar project to replace its aging facilities. Other commercial airports in or serving the New York metropolitan area include Long Island MacArthur Airport, Trenton–Mercer Airport and Westchester County Airport. The primary general aviation airport serving the area is Teterboro Airport. | Fail  
1 | See or edit raw graph data. === Parks === The city of New York has a complex park system, with various lands operated by the National Park Service, the New York State Office of Parks, Recreation and Historic Preservation, and the New York City Department of Parks and Recreation. In its 2018 ParkScore ranking, the Trust for Public Land reported that the park system in New York City was the ninth-best park system among the fifty most populous U.S. cities. ParkScore ranks urban park systems by a formula that analyzes median park size, park acres as percent of city area, the percent of city residents within a half-mile of a park, spending of park services per resident, and the number of playgrounds per 10,000 residents. In 2021, the New York City Council banned the use of synthetic pesticides by city agencies and instead required organic lawn management. The effort was started by teacher Paula Rogovin's kindergarten class at P.S. 290. ==== National parks ==== Gateway National Recreation Area contains over 26,000 acres (110 km2), most of it in New York City. In Brooklyn and Queens, the park contains over 9,000 acres (36 km2) of salt marsh, wetlands, islands, and water, including most of Jamaica Bay and the Jamaica Bay Wildlife Refuge. Also in Queens, the park includes a significant portion of the western Rockaway Peninsula, most notably Jacob Riis Park and Fort Tilden. In Staten Island, it includes Fort Wadsworth, with historic pre-Civil War era Battery Weed and Fort Tompkins, and Great Kills Park, with beaches, trails, and a marina. The Statue of Liberty National Monument and Ellis Island Immigration Museum are managed by the National Park Service and are in both New York and New Jersey. They are joined in the harbor by Governors Island National Monument. Historic sites under federal management on Manhattan Island include Stonewall National Monument; Castle Clinton National Monument; Federal Hall National Memorial; Theodore Roosevelt Birthplace National Historic Site; General Grant National Memorial (Grant's Tomb); African Burial Ground National Monument; and Hamilton Grange National Memorial. Hundreds of properties are listed on the National Register of Historic Places or as a National Historic Landmark. | Fail  
2 | New York has witnessed a growing combined volume of international and domestic tourists, reflecting over 60 million visitors to the city per year, the world's busiest tourist destination. Approximately 12 million visitors to New York City have been from outside the United States, with the highest numbers from the United Kingdom, Canada, Brazil, and China. Multiple sources have called New York the most photographed city in the world.I Love New York (stylized I ❤ NY) is both a logo and a song that are the basis of an advertising campaign and have been used since 1977 to promote tourism in New York City, and later to promote New York State as well. The trademarked logo, owned by New York State Empire State Development, appears in souvenir shops and brochures throughout the city and state, some licensed, many not. The song is the state song of New York. The majority of the most high-profile tourist destinations to the city are situated in Manhattan. These include Times Square; Broadway theater productions; the Empire State Building; the Statue of Liberty; Ellis Island; the United Nations headquarters; the World Trade Center (including the National September 11 Memorial & Museum and One World Trade Center); the art museums along Museum Mile; green spaces such as Central Park, Washington Square Park, the High Line, and the medieval gardens of The Cloisters; the Stonewall Inn; Rockefeller Center; ethnic enclaves including the Manhattan Chinatown, Koreatown, Curry Hill, Harlem, Spanish Harlem, Little Italy, and Little Australia; luxury shopping along Fifth and Madison Avenues; and events such as the Halloween Parade in Greenwich Village; the Brooklyn Bridge (shared with Brooklyn); the Macy's Thanksgiving Day Parade; the lighting of the Rockefeller Center Christmas Tree; the St. Patrick's Day Parade; seasonal activities such as ice skating in Central Park in the wintertime; the Tribeca Film Festival; and free performances in Central Park at SummerStage.Points of interest have also developed in the city outside Manhattan and have made the outer boroughs tourist destinations in their own right. | Fail
