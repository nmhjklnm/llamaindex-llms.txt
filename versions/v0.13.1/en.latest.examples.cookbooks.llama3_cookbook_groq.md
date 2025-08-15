# Llama3 Cookbook with Groq¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
Meta developed and released the Meta Llama 3 family of large language models (LLMs), a collection of pretrained and instruction tuned generative text models in 8 and 70B sizes. The Llama 3 instruction tuned models are optimized for dialogue use cases and outperform many of the available open source chat models on common industry benchmarks.
In this notebook, we demonstrate how to use Llama3 with LlamaIndex for a comprehensive set of use cases.
  1. Basic completion / chat
  2. Basic RAG (Vector Search, Summarization)
  3. Advanced RAG (Routing)
  4. Text-to-SQL
  5. Structured Data Extraction
  6. Chat Engine + Memory
  7. Agents


We use Llama3-8B and Llama3-70B through Groq.
## Installation and Setup¶
In [ ]:
Copied!
```
!pip install llama-index
!pip install llama-index-llms-groq
!pip install llama-index-embeddings-huggingface
!pip install llama-parse

```

!pip install llama-index !pip install llama-index-llms-groq !pip install llama-index-embeddings-huggingface !pip install llama-parse
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
### Setup LLM using Groq¶
To use Groq, you need to make sure that `GROQ_API_KEY` is specified as an environment variable.
In [ ]:
Copied!
```
import os

os.environ["GROQ_API_KEY"] = "<GROQ_API_KEY>"

```

import os os.environ["GROQ_API_KEY"] = ""
In [ ]:
Copied!
```
from llama_index.llms.groq import Groq

llm = Groq(model="llama3-8b-8192")
llm_70b = Groq(model="llama3-70b-8192")

```

from llama_index.llms.groq import Groq llm = Groq(model="llama3-8b-8192") llm_70b = Groq(model="llama3-70b-8192")
### Setup Embedding Model¶
In [ ]:
Copied!
```
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

```

from llama_index.embeddings.huggingface import HuggingFaceEmbedding embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
### Define Global Settings Configuration¶
In LlamaIndex, you can define global settings so you don't have to pass the LLM / embedding model objects everywhere.
In [ ]:
Copied!
```
from llama_index.core import Settings

Settings.llm = llm
Settings.embed_model = embed_model

```

from llama_index.core import Settings Settings.llm = llm Settings.embed_model = embed_model
### Download Data¶
Here you'll download data that's used in section 2 and onwards.
We'll download some articles on Kendrick, Drake, and their beef (as of May 2024).
In [ ]:
Copied!
```
!mkdir data
!wget "https://www.dropbox.com/scl/fi/t1soxfjdp0v44an6sdymd/drake_kendrick_beef.pdf?rlkey=u9546ymb7fj8lk2v64r6p5r5k&st=wjzzrgil&dl=1" -O data/drake_kendrick_beef.pdf
!wget "https://www.dropbox.com/scl/fi/nts3n64s6kymner2jppd6/drake.pdf?rlkey=hksirpqwzlzqoejn55zemk6ld&st=mohyfyh4&dl=1" -O data/drake.pdf
!wget "https://www.dropbox.com/scl/fi/8ax2vnoebhmy44bes2n1d/kendrick.pdf?rlkey=fhxvn94t5amdqcv9vshifd3hj&st=dxdtytn6&dl=1" -O data/kendrick.pdf

```

!mkdir data !wget "https://www.dropbox.com/scl/fi/t1soxfjdp0v44an6sdymd/drake_kendrick_beef.pdf?rlkey=u9546ymb7fj8lk2v64r6p5r5k&st=wjzzrgil&dl=1" -O data/drake_kendrick_beef.pdf !wget "https://www.dropbox.com/scl/fi/nts3n64s6kymner2jppd6/drake.pdf?rlkey=hksirpqwzlzqoejn55zemk6ld&st=mohyfyh4&dl=1" -O data/drake.pdf !wget "https://www.dropbox.com/scl/fi/8ax2vnoebhmy44bes2n1d/kendrick.pdf?rlkey=fhxvn94t5amdqcv9vshifd3hj&st=dxdtytn6&dl=1" -O data/kendrick.pdf
### Load Data¶
We load data using LlamaParse by default, but you can also choose to opt for our free pypdf reader (in SimpleDirectoryReader by default) if you don't have an account!
  1. LlamaParse: Signup for an account here: cloud.llamaindex.ai. You get 1k free pages a day, and paid plan is 7k free pages + 0.3c per additional page. LlamaParse is a good option if you want to parse complex documents, like PDFs with charts, tables, and more.
  2. Default PDF Parser (In `SimpleDirectoryReader`). If you don't want to signup for an account / use a PDF service, just use the default PyPDF reader bundled in our file loader. It's a good choice for getting started!


In [ ]:
Copied!
```
from llama_parse import LlamaParse

docs_kendrick = LlamaParse(result_type="text").load_data("./data/kendrick.pdf")
docs_drake = LlamaParse(result_type="text").load_data("./data/drake.pdf")
docs_both = LlamaParse(result_type="text").load_data(
    "./data/drake_kendrick_beef.pdf"
)


# from llama_index.core import SimpleDirectoryReader

# docs_kendrick = SimpleDirectoryReader(input_files=["data/kendrick.pdf"]).load_data()
# docs_drake = SimpleDirectoryReader(input_files=["data/drake.pdf"]).load_data()
# docs_both = SimpleDirectoryReader(input_files=["data/drake_kendrick_beef.pdf"]).load_data()

```

from llama_parse import LlamaParse docs_kendrick = LlamaParse(result_type="text").load_data("./data/kendrick.pdf") docs_drake = LlamaParse(result_type="text").load_data("./data/drake.pdf") docs_both = LlamaParse(result_type="text").load_data( "./data/drake_kendrick_beef.pdf" ) # from llama_index.core import SimpleDirectoryReader # docs_kendrick = SimpleDirectoryReader(input_files=["data/kendrick.pdf"]).load_data() # docs_drake = SimpleDirectoryReader(input_files=["data/drake.pdf"]).load_data() # docs_both = SimpleDirectoryReader(input_files=["data/drake_kendrick_beef.pdf"]).load_data()
```
Started parsing the file under job_id 391f5fe8-aed3-46a3-af7d-18341b1b20d7
Started parsing the file under job_id 08c335d5-417b-4249-b53d-a7a9b65293a8
Started parsing the file under job_id e3a91a73-5db0-4df0-9590-c9393cb048cf

```

## 1. Basic Completion and Chat¶
### Call complete with a prompt¶
In [ ]:
Copied!
```
response = llm.complete("do you like drake or kendrick better?")

print(response)

```

response = llm.complete("do you like drake or kendrick better?") print(response)
```
I'm just an AI, I don't have personal preferences or opinions, nor do I have the capacity to enjoy or dislike music. I can provide information and insights about different artists and their work, but I don't have personal feelings or biases.

However, I can tell you that both Drake and Kendrick Lamar are highly acclaimed and influential artists in the music industry. They have both received widespread critical acclaim and have won numerous awards for their work.

Drake is known for his introspective and emotive lyrics, as well as his ability to blend different genres such as hip-hop, R&B, and pop. He has been praised for his storytelling ability and his ability to connect with his audience.

Kendrick Lamar, on the other hand, is known for his socially conscious lyrics and his ability to tackle complex issues such as racism, inequality, and social justice. He has been praised for his lyrical depth and his ability to blend different genres such as hip-hop, jazz, and funk.

Ultimately, whether you prefer Drake or Kendrick Lamar depends on your personal taste in music and what you value in an artist.

```

In [ ]:
Copied!
```
stream_response = llm.stream_complete(
    "you're a drake fan. tell me why you like drake more than kendrick"
)

for t in stream_response:
    print(t.delta, end="")

```

stream_response = llm.stream_complete( "you're a drake fan. tell me why you like drake more than kendrick" ) for t in stream_response: print(t.delta, end="")
```
Man, I'm a die-hard Drake fan, and I gotta say, I love the 6 God for many reasons. Now, I know some people might say Kendrick is the king of hip-hop, and I respect that, but for me, Drake's got something special. Here's why:

1. **Relatability**: Drake's lyrics are like a diary entry. He's got this ability to tap into the emotions and struggles of everyday people. His songs are like a reflection of our own experiences, you know? He's not just rapping about gangsta life or material possessions; he's talking about the real stuff, like relationships, fame, and the struggles of growing up. That's what makes his music so relatable and authentic.

2. **Vocal delivery**: Drake's got this smooth, melodic flow that's unmatched. His vocals are like butter – they just glide over the beat. He's got this effortless swag that makes his songs feel like a warm hug on a cold day. Kendrick's got a great flow too, but Drake's got this unique, laid-back vibe that's hard to replicate.

3. **Storytelling**: Drake's a master storyteller. He's got this ability to paint vivid pictures with his words, taking you on a journey through his life experiences. His songs are like mini-movies, with characters, settings, and plot twists. Kendrick's got great storytelling skills too, but Drake's got this extra something that makes his stories feel more intimate and personal.

4. **Production**: Drake's got an ear for beats that's unmatched. He's always pushing the boundaries of what a hip-hop beat can be. From the atmospheric soundscapes of "Take Care" to the trap-infused bangers of "Scorpion," Drake's always experimenting and innovating. Kendrick's got great production too, but Drake's got this versatility that's hard to match.

5. **Emotional depth**: Drake's music is like a therapy session. He's not afraid to get vulnerable and open up about his emotions. He's got this ability to tap into the human experience and share his own struggles and triumphs. Kendrick's got great emotional depth too, but Drake's got this extra layer of vulnerability that makes his music feel more honest and authentic.

So, there you have it – that's why I'm a Drake fan through and through. He's got this unique blend of relatability, vocal delivery, storytelling, production, and emotional depth that sets him apart from the rest.
```

### Call chat with a list of messages¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(role="system", content="You are Kendrick."),
    ChatMessage(role="user", content="Write a verse."),
]
response = llm.chat(messages)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage(role="system", content="You are Kendrick."), ChatMessage(role="user", content="Write a verse."), ] response = llm.chat(messages)
In [ ]:
Copied!
```
print(response)

```

print(response)
```
assistant: "I'm the king of the game, no debate
My rhymes so tight, they're like a weight
I'm the voice of the streets, the people's champ
My flow's on fire, leaving the haters in the slam"

```

## 2. Basic RAG (Vector Search, Summarization)¶
### Basic RAG (Vector Search)¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(docs_both)
query_engine = index.as_query_engine(similarity_top_k=3)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(docs_both) query_engine = index.as_query_engine(similarity_top_k=3)
In [ ]:
Copied!
```
response = query_engine.query("Tell me about family matters")

```

response = query_engine.query("Tell me about family matters")
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The concept of "Family Matters" is a central theme in the ongoing beef between Drake and Kendrick Lamar. It refers to a seven-and-a-half-minute diss track released by Drake in response to Kendrick's diss track "Family Matters." The track is a scathing attack on Kendrick, with Drake addressing various allegations and accusations made by Kendrick. The track is notable for its dark and sinister tone, with Drake delivering a series of personal attacks on Kendrick and his family. The track also features Drake addressing his own family, including his son Adonis and his parents, Dennis and Sandi Graham.

```

### Basic RAG (Summarization)¶
In [ ]:
Copied!
```
from llama_index.core import SummaryIndex

summary_index = SummaryIndex.from_documents(docs_both)
summary_engine = summary_index.as_query_engine()

```

from llama_index.core import SummaryIndex summary_index = SummaryIndex.from_documents(docs_both) summary_engine = summary_index.as_query_engine()
In [ ]:
Copied!
```
response = summary_engine.query(
    "Given your assessment of this article, who won the beef?"
)

```

response = summary_engine.query( "Given your assessment of this article, who won the beef?" )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
It's difficult to declare a clear winner in this beef, as both Kendrick Lamar and Drake have delivered scathing diss tracks, and the beef has been marked by a series of intense exchanges.

```

## 3. Advanced RAG (Routing)¶
### Build a Router that can choose whether to do vector search or summarization¶
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool, ToolMetadata

vector_tool = QueryEngineTool(
    index.as_query_engine(),
    metadata=ToolMetadata(
        name="vector_search",
        description="Useful for searching for specific facts.",
    ),
)

summary_tool = QueryEngineTool(
    index.as_query_engine(response_mode="tree_summarize"),
    metadata=ToolMetadata(
        name="summary",
        description="Useful for summarizing an entire document.",
    ),
)

```

from llama_index.core.tools import QueryEngineTool, ToolMetadata vector_tool = QueryEngineTool( index.as_query_engine(), metadata=ToolMetadata( name="vector_search", description="Useful for searching for specific facts.", ), ) summary_tool = QueryEngineTool( index.as_query_engine(response_mode="tree_summarize"), metadata=ToolMetadata( name="summary", description="Useful for summarizing an entire document.", ), )
In [ ]:
Copied!
```
from llama_index.core.query_engine import RouterQueryEngine

query_engine = RouterQueryEngine.from_defaults(
    [vector_tool, summary_tool], select_multi=False, verbose=True, llm=llm_70b
)

response = query_engine.query(
    "Tell me about the song meet the grahams - why is it significant"
)

```

from llama_index.core.query_engine import RouterQueryEngine query_engine = RouterQueryEngine.from_defaults( [vector_tool, summary_tool], select_multi=False, verbose=True, llm=llm_70b ) response = query_engine.query( "Tell me about the song meet the grahams - why is it significant" )
```
Selecting query engine 0: The question asks for specific facts about the song 'Meet the Grahams', so a search for specific facts is required..

```

In [ ]:
Copied!
```
print(response)

```

print(response)
```
The "Meet the Grahams" artwork is significant because it's the full picture that Kendrick Lamar teased earlier on "6.16 in LA." It shows a pair of Maybach gloves, a shirt, receipts, and prescription bottles, including one for Ozempic prescribed to Drake.

```

## 4. Text-to-SQL¶
Here, we download and use a sample SQLite database with 11 tables, with various info about music, playlists, and customers. We will limit to a select few tables for this test.
In [ ]:
Copied!
```
!wget "https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip" -O "./data/chinook.zip"
!unzip "./data/chinook.zip"

```

!wget "https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip" -O "./data/chinook.zip" !unzip "./data/chinook.zip"
```
--2024-05-10 23:40:37--  https://www.sqlitetutorial.net/wp-content/uploads/2018/03/chinook.zip
Resolving www.sqlitetutorial.net (www.sqlitetutorial.net)... 2606:4700:3037::6815:1e8d, 2606:4700:3037::ac43:acfa, 104.21.30.141, ...
Connecting to www.sqlitetutorial.net (www.sqlitetutorial.net)|2606:4700:3037::6815:1e8d|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 305596 (298K) [application/zip]
Saving to: ‘./data/chinook.zip’

./data/chinook.zip  100%[===================>] 298.43K  --.-KB/s    in 0.02s   

2024-05-10 23:40:37 (13.9 MB/s) - ‘./data/chinook.zip’ saved [305596/305596]


```

```
huggingface/tokenizers: The current process just got forked, after parallelism has already been used. Disabling parallelism to avoid deadlocks...
To disable this warning, you can either:
	- Avoid using `tokenizers` before the fork if possible
	- Explicitly set the environment variable TOKENIZERS_PARALLELISM=(true | false)

```

```
Archive:  ./data/chinook.zip
  inflating: chinook.db              

```

```
huggingface/tokenizers: The current process just got forked, after parallelism has already been used. Disabling parallelism to avoid deadlocks...
To disable this warning, you can either:
	- Avoid using `tokenizers` before the fork if possible
	- Explicitly set the environment variable TOKENIZERS_PARALLELISM=(true | false)

```

In [ ]:
Copied!
```
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
    column,
)

engine = create_engine("sqlite:///chinook.db")

```

from sqlalchemy import ( create_engine, MetaData, Table, Column, String, Integer, select, column, ) engine = create_engine("sqlite:///chinook.db")
In [ ]:
Copied!
```
from llama_index.core import SQLDatabase

sql_database = SQLDatabase(engine)

```

from llama_index.core import SQLDatabase sql_database = SQLDatabase(engine)
In [ ]:
Copied!
```
from llama_index.core.indices.struct_store import NLSQLTableQueryEngine

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["albums", "tracks", "artists"],
    llm=llm_70b,
)

```

from llama_index.core.indices.struct_store import NLSQLTableQueryEngine query_engine = NLSQLTableQueryEngine( sql_database=sql_database, tables=["albums", "tracks", "artists"], llm=llm_70b, )
In [ ]:
Copied!
```
response = query_engine.query("What are some albums?")

print(response)

```

response = query_engine.query("What are some albums?") print(response)
```
Here are some albums: For Those About To Rock We Salute You, Balls to the Wall, Restless and Wild, Let There Be Rock, Big Ones, Jagged Little Pill, Facelift, Warner 25 Anos, Plays Metallica By Four Cellos, and Audioslave.

```

In [ ]:
Copied!
```
response = query_engine.query("What are some artists? Limit it to 5.")

print(response)

```

response = query_engine.query("What are some artists? Limit it to 5.") print(response)
```
Here are 5 artists: AC/DC, Accept, Aerosmith, Alanis Morissette, and Alice In Chains.

```

This last query should be a more complex join
In [ ]:
Copied!
```
response = query_engine.query(
    "What are some tracks from the artist AC/DC? Limit it to 3"
)

print(response)

```

response = query_engine.query( "What are some tracks from the artist AC/DC? Limit it to 3" ) print(response)
```
Here are three tracks from the legendary Australian rock band AC/DC: "For Those About To Rock (We Salute You)", "Put The Finger On You", and "Let's Get It Up".

```

In [ ]:
Copied!
```
print(response.metadata["sql_query"])

```

print(response.metadata["sql_query"])
```
SELECT tracks.Name FROM tracks INNER JOIN albums ON tracks.AlbumId = albums.AlbumId INNER JOIN artists ON albums.ArtistId = artists.ArtistId WHERE artists.Name = 'AC/DC' LIMIT 3;

```

## 5. Structured Data Extraction¶
An important use case for function calling is extracting structured objects. LlamaIndex provides an intuitive interface for this through `structured_predict` - simply define the target Pydantic class (can be nested), and given a prompt, we extract out the desired object.
**NOTE** : Since there's no native function calling support with Llama3, the structured extraction is performed by prompting the LLM + output parsing.
In [ ]:
Copied!
```
from llama_index.llms.groq import Groq
from llama_index.core.prompts import PromptTemplate
from pydantic import BaseModel


class Restaurant(BaseModel):
    """A restaurant with name, city, and cuisine."""

    name: str
    city: str
    cuisine: str


llm = Groq(model="llama3-8b-8192", pydantic_program_mode="llm")
prompt_tmpl = PromptTemplate(
    "Generate a restaurant in a given city {city_name}"
)

```

from llama_index.llms.groq import Groq from llama_index.core.prompts import PromptTemplate from pydantic import BaseModel class Restaurant(BaseModel): """A restaurant with name, city, and cuisine.""" name: str city: str cuisine: str llm = Groq(model="llama3-8b-8192", pydantic_program_mode="llm") prompt_tmpl = PromptTemplate( "Generate a restaurant in a given city {city_name}" )
In [ ]:
Copied!
```
restaurant_obj = llm.structured_predict(
    Restaurant, prompt_tmpl, city_name="Miami"
)
print(restaurant_obj)

```

restaurant_obj = llm.structured_predict( Restaurant, prompt_tmpl, city_name="Miami" ) print(restaurant_obj)
```
name='Café Havana' city='Miami' cuisine='Cuban'

```

## 6. Adding Chat History to RAG (Chat Engine)¶
In this section we create a stateful chatbot from a RAG pipeline, with our chat engine abstraction.
Unlike a stateless query engine, the chat engine maintains conversation history (through a memory module like buffer memory). It performs retrieval given a condensed question, and feeds the condensed question + context + chat history into the final LLM prompt.
Related resource: https://docs.llamaindex.ai/en/stable/examples/chat_engine/chat_engine_condense_plus_context/
In [ ]:
Copied!
```
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondensePlusContextChatEngine

memory = ChatMemoryBuffer.from_defaults(token_limit=3900)

chat_engine = CondensePlusContextChatEngine.from_defaults(
    index.as_retriever(),
    memory=memory,
    llm=llm,
    context_prompt=(
        "You are a chatbot, able to have normal interactions, as well as talk"
        " about the Kendrick and Drake beef."
        "Here are the relevant documents for the context:\n"
        "{context_str}"
        "\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
    ),
    verbose=True,
)

```

from llama_index.core.memory import ChatMemoryBuffer from llama_index.core.chat_engine import CondensePlusContextChatEngine memory = ChatMemoryBuffer.from_defaults(token_limit=3900) chat_engine = CondensePlusContextChatEngine.from_defaults( index.as_retriever(), memory=memory, llm=llm, context_prompt=( "You are a chatbot, able to have normal interactions, as well as talk" " about the Kendrick and Drake beef." "Here are the relevant documents for the context:\n" "{context_str}" "\nInstruction: Use the previous chat history, or the context above, to interact and help the user." ), verbose=True, )
In [ ]:
Copied!
```
response = chat_engine.chat(
    "Tell me about the songs Drake released in the beef."
)
print(str(response))

```

response = chat_engine.chat( "Tell me about the songs Drake released in the beef." ) print(str(response))
```
Condensed question: Tell me about the songs Drake released in the beef.
Context: https://www.gq.com/story/the-kendrick-lamar-drake-beef-explained                                        27/34
---
     5/10/24, 10:08 PM                                        The Kendrick Lamar/Drake Beef, Explained | GQ
          May 5: Drake hits back with “The Heart Part 6”
                     The HEART PART 6   DRAKE


THE HEART PART 6 - DRAKETHE HEART PART 6 - DRAKE
          The most productive weekend in the history of rap beef continues, with Drake saying
          fuck all to the Sunday Truce and doing exactly what Joe Budden advised: to hit back at
          Kendrick's onslaught with a record in the vein of his time-stamp series, straight bars over
          a hard beat. Only, Kendrick already beat him to a time-stamp title last week with “6:16
          in LA,” so Drake counters by co-opting one of Kendrick's recurring series: “The Heart.”
          (The last official entry, “The Heart Part 5,” heralded Kendrick's Mr. Morale and The Big
          Steppers album. Surely you remember the music video, where Kendrick applies deepfake
          technology to take on the visages of everyone from Kanye and Nipsey Hussle to OJ.)
          Drake even takes a page out of Kendrick's diss manual and applies some classic soul to
          the proceedings, countering Kendrick's Teddy Pendergrass and Al Green samples (on
          “Euphoria” and “6:16,” respectively) with an Aretha Franklin sample here.
          Aretha sings “Let me see you proooove it,” setting the tone for Drake's angle here that
          Kendrick's been hitting him with baseless accusations. “The Heart Part 6” is in full
          reaction mode to everything that's transpired over the last three days, including direct
         Maial
          rebuttals to Kendrick's “Not Like Us;” it was clearly written in the last 24 hours. DrakeSign up for Manual, our new flagship newsletter
                                   Useful advice on style, health, and more, four days a week.
          sounds…a little over it all, while nevertheless still promising that shit is about to get
          dark. (This is now his second track in a row where he plainly states he'd rather be on



     https://www.gq.com/story/the-kendrick-lamar-drake-beef-explained                                                              28/34
---
5/10/24, 10:08 PM                                        The Kendrick Lamar/Drake Beef, Explained | GQ
     vacation somewhere than holed up in cold Toronto writing disses.) Drake, buddy,
     domestic abuse and pedophilia accusations are in the air—we've been pitch black for the
     last few songs already.



     You would think Drake would sound a little more celebratory than he does to start the
     song, where he takes a victory lap for allegedly going full Sydney Bristow and triple-
     crossing Kendrick into leaping on Fake Child Intel. “We plotted for a week and then we
     fed you the information…we thought about giving a fake name or a destination/but you
     so thirsty, you not concerned with investigation.” Who's lying or who was fooled? Only
     the Pusha T Investigative Team can solve this.



     Drake doesn't dwell there, though, instead moving on to Kendrick's family, doubling
     down on the two angles that formed the basis of “Family Matters”: that Kendrick has
     beaten his partner Whitney in the past, he's estranged from their family, and one of his
     two kids is actually fathered by his friend and creative partner Dave Free. To drive this
     last point home, “The Heart Part 6” artwork is an Instagram screenshot of Dave leaving
     heart emojis under, presumably, a picture Whitney posted.



     Continuing his through line of using Kendrick's confessional raps on Mr. Morale as
     ammo, Drake refers back to “Mother I Sober,” the track where Kendrick unpacks his
     mother's sexual abuse and how it informed an incident in his childhood where his
     mother was worried he was being abused by a family member even though Kendrick says
     he wasn't. Dr. Drake's read: He actually was molseted, and that's why he's so hell-bent
     on calling OVO “certified pedophiles.”

5/10/24, 10:08 PMThe Kendrick Lamar/Drake Beef, Explained | GQ
          Christopher Polk/Getty Images                                                                 Email address
         Maial                       Sign up for Manual, our new flagship newsletter
                                     Useful advice on style, health,Cultureand more, four days a week.        SIGN ME UP



                     The Kendrick Lamar/Drake Beef, ExplainedNO THANKS



     https://www.gq.com/story/the-kendrick-lamar-drake-beef-explained                                                     1/34
---
5/10/24, 10:08 PM                                         The Kendrick Lamar/Drake Beef, Explained | GQ



     Kendrick and Drake diss each other multiple times in one weekend, A.I. shenanigans, shots fired
          at and from Future, Metro Boomin, Rick Ross, Weeknd, and more in a new chapter in rap
                                                           geopolitics.



                                                       By Frazier Tharpe
                                                           May 5, 2024



     There's the back-to-back effect, and then there's the unrestrained chaos of dropping long
     diss tracks, densely loaded with viciously personal power punches, within an hour of each
     other. On the first weekend in May, Drake commandeered everyone's Friday night to
     turn up the heat in his beef with Kendrick Lamar with a three-part reply and
     accompanying music video—only for Kendrick to hit right back with what may be one
     of the most scathing diss tracks in rap history. This Cold War is firmly and decidedly
     thawed all the way out—and the [Maybach] gloves are off.



     To paraphrase prime Jigga-era Jay-Z, the summer just got hotter. Read on for a full
     account of 2024's most constantly-evolving rap beef.



     Read More



     The Drake/Kendrick Lamar Beef Has a Winner. Where Do
     We Go From Here?



     The low blows thrown during this weekend’s volley of diss songs have
     changed hip-hop’s rules of engagement forever—and may have shifted
     both Drake and Kendrick’s legacies in the bargain.
     By Lawrence Burney



     March 29: Kendrick Lamar declares war, on an album that may be wholly
     dedicated to dissing Drake.



     Future and Metro Boomin’s decade-in-the-making new album We Don’t Trust You was
     already one of the most feverishly anticipated rap releases in some time, and on the song
    Maial
     “Like That,” Kendrick delivers on that Christmas Eve energy with a guest verse that may
                               Sign up for Manual, our new flagship newsletter
     as well be a “Control” sequel. But whereas that name-naming 2013 landmark was
                               Useful advice on style, health, and more, four days a week.
     ultimately rooted in the spirit of competition, this time the gloves are off and the love is
     done.



https://www.gq.com/story/the-kendrick-lamar-drake-beef-explained                                         2/34
---
     5/10/24, 10:08 PM                                        The Kendrick Lamar/Drake Beef, Explained | GQ
                     Future; Metro Boomin Kendrick Lamar                    Like That (Official Audio)


Future, Metro Boomin, Kendrick Lamar - Like That (OFuture, Metro Boomin, Kendrick Lamar - Like That (Offifficial Audio)cial Audio)
          Kendrick sets the tone early, declaring that he’s “choosing violence” and it’s time for an
          opponent to “prove that he’s a problem.” And though no names are officially named, a
          reference to Drake’s song “First Person Shooter” and the album it lives on, For All the
          Dogs, means we have to consider this something more than a subliminal. On “FPS”
          Drake brags about taking Michael Jackson’s mantle for having the most Billboard Hot
          100 No. 1 songs, going as far as to hit the “Beat It” steps with a sequined glove in the
          video. Here, Kendrick finally, formally casts himself as direct opposition, ending his verse
          with a haymaker referencing MJ’s own longtime Cold War enemy: “Prince outlived Mike
          Jack.” Sheesh.
According to the article, Drake released a song called "The Heart Part 6" in response to Kendrick Lamar's diss track. This song is part of the ongoing beef between the two rappers.

```

In [ ]:
Copied!
```
response = chat_engine.chat("What about Kendrick?")
print(str(response))

```

response = chat_engine.chat("What about Kendrick?") print(str(response))
```
Condensed question: What did Kendrick Lamar release in response to Drake's "The Heart Part 6"?
Context: https://www.gq.com/story/the-kendrick-lamar-drake-beef-explained                                        27/34
---
     5/10/24, 10:08 PM                                        The Kendrick Lamar/Drake Beef, Explained | GQ
          May 5: Drake hits back with “The Heart Part 6”
                     The HEART PART 6   DRAKE


THE HEART PART 6 - DRAKETHE HEART PART 6 - DRAKE
          The most productive weekend in the history of rap beef continues, with Drake saying
          fuck all to the Sunday Truce and doing exactly what Joe Budden advised: to hit back at
          Kendrick's onslaught with a record in the vein of his time-stamp series, straight bars over
          a hard beat. Only, Kendrick already beat him to a time-stamp title last week with “6:16
          in LA,” so Drake counters by co-opting one of Kendrick's recurring series: “The Heart.”
          (The last official entry, “The Heart Part 5,” heralded Kendrick's Mr. Morale and The Big
          Steppers album. Surely you remember the music video, where Kendrick applies deepfake
          technology to take on the visages of everyone from Kanye and Nipsey Hussle to OJ.)
          Drake even takes a page out of Kendrick's diss manual and applies some classic soul to
          the proceedings, countering Kendrick's Teddy Pendergrass and Al Green samples (on
          “Euphoria” and “6:16,” respectively) with an Aretha Franklin sample here.
          Aretha sings “Let me see you proooove it,” setting the tone for Drake's angle here that
          Kendrick's been hitting him with baseless accusations. “The Heart Part 6” is in full
          reaction mode to everything that's transpired over the last three days, including direct
         Maial
          rebuttals to Kendrick's “Not Like Us;” it was clearly written in the last 24 hours. DrakeSign up for Manual, our new flagship newsletter
                                   Useful advice on style, health, and more, four days a week.
          sounds…a little over it all, while nevertheless still promising that shit is about to get
          dark. (This is now his second track in a row where he plainly states he'd rather be on



     https://www.gq.com/story/the-kendrick-lamar-drake-beef-explained                                                              28/34
---
5/10/24, 10:08 PM                                        The Kendrick Lamar/Drake Beef, Explained | GQ
     vacation somewhere than holed up in cold Toronto writing disses.) Drake, buddy,
     domestic abuse and pedophilia accusations are in the air—we've been pitch black for the
     last few songs already.



     You would think Drake would sound a little more celebratory than he does to start the
     song, where he takes a victory lap for allegedly going full Sydney Bristow and triple-
     crossing Kendrick into leaping on Fake Child Intel. “We plotted for a week and then we
     fed you the information…we thought about giving a fake name or a destination/but you
     so thirsty, you not concerned with investigation.” Who's lying or who was fooled? Only
     the Pusha T Investigative Team can solve this.



     Drake doesn't dwell there, though, instead moving on to Kendrick's family, doubling
     down on the two angles that formed the basis of “Family Matters”: that Kendrick has
     beaten his partner Whitney in the past, he's estranged from their family, and one of his
     two kids is actually fathered by his friend and creative partner Dave Free. To drive this
     last point home, “The Heart Part 6” artwork is an Instagram screenshot of Dave leaving
     heart emojis under, presumably, a picture Whitney posted.



     Continuing his through line of using Kendrick's confessional raps on Mr. Morale as
     ammo, Drake refers back to “Mother I Sober,” the track where Kendrick unpacks his
     mother's sexual abuse and how it informed an incident in his childhood where his
     mother was worried he was being abused by a family member even though Kendrick says
     he wasn't. Dr. Drake's read: He actually was molseted, and that's why he's so hell-bent
     on calling OVO “certified pedophiles.”

Cole would go on to respond to Kendrick with “7 Minute Drill,” a diss track more
     notable for Cole admitting on it that he doesn't want to really go there with his onetime
     friend than any especially vicious jabs. As the internet spent the weekend debating if J.
     Cole's heart was really in it, by Sunday he would go onstage at his own Dreamville
     Festival to confirm just that. He publicly retracted his diss, apologized to and bigged up
     Lamar, and even vowed to stay out of it even if Kendrick should respond to “Drill.”



     So why do Future and Metro Boomin suddenly have issues with Drake after doing
     dozens of collaborations with him?



     We’ve gone hundreds of words without returning to the duo who delivered this moment:
     Future, the fourth face on that 2010s Rap Mount Rushmore, and Metro Boomin, the
     superproducer he’s made some of his most potent music with. There’s a deeper layer to
     Kendrick choosing a Future and Metro album as the stage to finally go at Drake: Metro
     has seemingly had his own problems with the 6ix God. Late last year he posted and
     subsequently deleted a tweet about his acclaimed album Heroes and Villains continuing to
     lose awards to Drake (and frequent Metro collaborator 21 Savage’s) album Her Loss.
    Maial
     During a livestream not long after, Drake hilariously referenced “the non-believers, the
                              Sign up for Manual, our new flagship newsletter
                              Useful advice on style, health, and more, four days a week.
     underachievers, the tweet-and-deleters,” adding “you guys make me sick to my stomach,



https://www.gq.com/story/the-kendrick-lamar-drake-beef-explained                                        6/34
---
5/10/24, 10:08 PM                                        The Kendrick Lamar/Drake Beef, Explained | GQ
     fam.” Despite trading a few more subliminal potshots across Twitter and IG, Metro
     downplayed any beef, saying that the issue was “not deep at all.”
     Still, when eagle-eyed fans took note of Metro unfollowing Drake on Instagram—the
     definitive 21st century signpost of an un-amicable split—ahead of the album’s release, it
     didn’t take a hip-hop scholar to assume that, as Kendrick would declare, “it’s up.” And
     for those wondering how a producer-rapper beef would even reasonably play out, Metro
     makes it clear by serving up a new creative peak on “Like That,” with an obscenely
     screwface-inducing beat sampling 80s rap duo Rodney O and Joe Cooley's classic
     “Everlasting Bass,” (which was famously earlier sampled on Three 6 Mafia’s “Who the
     Crunkest”,) alongside Eazy-E's classic “Eazy Duz It” as well as a splash of “Ridin
     Spinners.” In effect Kendrick and Metro are following playbooks beloved by the likes of
     Jay-Z before them, or even Drake with “Back to Back,” in dissing your opponent on a
     song that’s an undeniable banger whether people know the context or not.



     But why would Future, who has approximately 30 (thirty) collaborations with Drake,
     including the 2015 collab album What a Time to Be Alive and two fairly recent tracks on
     Future’s last solo album, cede airtime on his new project to a noted Drake enemy? No
     one knows for sure at press time, but it’s possible they have issues of their own. Despite
     their prolific collaborations, their relationship has had its rough moments from day one.
     Recall 2011, when an ascendant Future got an assist from Drake remixing the former’s
     “Tony Montana,” only to publicly bemoan Drake refusing to do a video. And while they
     toured together in 2016, who can forget that time in 2013 when Future was briefly,
     allegedly booted off of Drake’s tour for less-than-flattering comments about his music in
     an interview.
According to the article, Kendrick Lamar released a song called "6:16 in LA" which was part of the beef.

```

## 7. Agents¶
Here we build agents with Llama 3. We perform RAG over simple functions as well as the documents above.
### Agents And Tools¶
In [ ]:
Copied!
```
import json
from typing import Sequence, List

from llama_index.core.llms import ChatMessage
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.core.agent import ReActAgent

import nest_asyncio

nest_asyncio.apply()

```

import json from typing import Sequence, List from llama_index.core.llms import ChatMessage from llama_index.core.tools import BaseTool, FunctionTool from llama_index.core.agent import ReActAgent import nest_asyncio nest_asyncio.apply()
### Define Tools¶
In [ ]:
Copied!
```
def multiply(a: int, b: int) -> int:
    """Multiple two integers and returns the result integer"""
    return a * b


def add(a: int, b: int) -> int:
    """Add two integers and returns the result integer"""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract two integers and returns the result integer"""
    return a - b


def divide(a: int, b: int) -> int:
    """Divides two integers and returns the result integer"""
    return a / b


multiply_tool = FunctionTool.from_defaults(fn=multiply)
add_tool = FunctionTool.from_defaults(fn=add)
subtract_tool = FunctionTool.from_defaults(fn=subtract)
divide_tool = FunctionTool.from_defaults(fn=divide)

```

def multiply(a: int, b: int) -> int: """Multiple two integers and returns the result integer""" return a * b def add(a: int, b: int) -> int: """Add two integers and returns the result integer""" return a + b def subtract(a: int, b: int) -> int: """Subtract two integers and returns the result integer""" return a - b def divide(a: int, b: int) -> int: """Divides two integers and returns the result integer""" return a / b multiply_tool = FunctionTool.from_defaults(fn=multiply) add_tool = FunctionTool.from_defaults(fn=add) subtract_tool = FunctionTool.from_defaults(fn=subtract) divide_tool = FunctionTool.from_defaults(fn=divide)
### ReAct Agent¶
In [ ]:
Copied!
```
agent = ReActAgent.from_tools(
    [multiply_tool, add_tool, subtract_tool, divide_tool],
    llm=llm_70b,
    verbose=True,
)

```

agent = ReActAgent.from_tools( [multiply_tool, add_tool, subtract_tool, divide_tool], llm=llm_70b, verbose=True, )
### Querying¶
In [ ]:
Copied!
```
response = agent.chat("What is (121 + 2) * 5?")
print(str(response))

```

response = agent.chat("What is (121 + 2) * 5?") print(str(response))
```
Thought: The current language of the user is: English. I need to use a tool to help me answer the question.
Action: add
Action Input: {'a': 121, 'b': 2}
Observation: 123
Thought: Now I have the result of the addition, I need to multiply it by 5.
Action: multiply
Action Input: {'a': 123, 'b': 5}
Observation: 615
Thought: I can answer without using any more tools. I'll use the user's language to answer
Answer: 615
615

```

### ReAct Agent With RAG QueryEngine Tools¶
In [ ]:
Copied!
```
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)

from llama_index.core.tools import QueryEngineTool, ToolMetadata

```

from llama_index.core import ( SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage, ) from llama_index.core.tools import QueryEngineTool, ToolMetadata
### Create ReAct Agent using RAG QueryEngine Tools¶
In [ ]:
Copied!
```
drake_tool = QueryEngineTool(
    drake_index.as_query_engine(),
    metadata=ToolMetadata(
        name="drake_search",
        description="Useful for searching over Drake's life.",
    ),
)

kendrick_tool = QueryEngineTool(
    kendrick_index.as_query_engine(),
    metadata=ToolMetadata(
        name="kendrick_search",
        description="Useful for searching over Kendrick's life.",
    ),
)

query_engine_tools = [drake_tool, kendrick_tool]

```

drake_tool = QueryEngineTool( drake_index.as_query_engine(), metadata=ToolMetadata( name="drake_search", description="Useful for searching over Drake's life.", ), ) kendrick_tool = QueryEngineTool( kendrick_index.as_query_engine(), metadata=ToolMetadata( name="kendrick_search", description="Useful for searching over Kendrick's life.", ), ) query_engine_tools = [drake_tool, kendrick_tool]
In [ ]:
Copied!
```
agent = ReActAgent.from_tools(
    query_engine_tools,  ## TODO: define query tools
    llm=llm_70b,
    verbose=True,
)

```

agent = ReActAgent.from_tools( query_engine_tools, ## TODO: define query tools llm=llm_70b, verbose=True, )
### Querying¶
In [ ]:
Copied!
```
response = agent.chat("Tell me about how Kendrick and Drake grew up")
print(str(response))

```

response = agent.chat("Tell me about how Kendrick and Drake grew up") print(str(response))
```
Thought: The current language of the user is: English. I need to use a tool to help me answer the question.
Action: kendrick_search
Action Input: {'input': "Kendrick Lamar's childhood"}
Observation: Kendrick Lamar was born on June 17, 1987, in Compton, California. He is the first child of Kenneth "Kenny" Duckworth, a former gang hustler, and Paula Oliver, a hairdresser. Both of his parents are African Americans from the South Side of Chicago. When they were teenagers, they relocated to Compton in 1984 due to his father's affiliation with the Gangster Disciples. Lamar was named after singer-songwriter Eddie Kendricks of the Temptations.
Thought: I need more information about Drake's childhood to compare their upbringings.
Action: drake_search
Action Input: {'input': "Drake's childhood"}
Observation: Drake's parents divorced when he was five years old. After the divorce, he and his mother remained in Toronto; his father returned to Memphis, where he was incarcerated for a number of years on drug-related charges.
Thought: I have information about both Kendrick and Drake's childhoods. I can now compare their upbringings.
Answer: Kendrick Lamar grew up in Compton, California, with his parents, who were both from the South Side of Chicago. He was exposed to gang culture from a young age due to his father's affiliation with the Gangster Disciples. On the other hand, Drake grew up in Toronto, Canada, with his mother after his parents' divorce when he was five years old. His father was incarcerated in Memphis for drug-related charges.
Kendrick Lamar grew up in Compton, California, with his parents, who were both from the South Side of Chicago. He was exposed to gang culture from a young age due to his father's affiliation with the Gangster Disciples. On the other hand, Drake grew up in Toronto, Canada, with his mother after his parents' divorce when he was five years old. His father was incarcerated in Memphis for drug-related charges.

```

