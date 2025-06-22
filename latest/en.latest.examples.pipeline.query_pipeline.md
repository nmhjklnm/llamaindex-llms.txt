# An Introduction to LlamaIndex Query Pipelines¶
## Overview¶
LlamaIndex provides a declarative query API that allows you to chain together different modules in order to orchestrate simple-to-advanced workflows over your data.
This is centered around our `QueryPipeline` abstraction. Load in a variety of modules (from LLMs to prompts to retrievers to other pipelines), connect them all together into a sequential chain or DAG, and run it end2end.
**NOTE** : You can orchestrate all these workflows without the declarative pipeline abstraction (by using the modules imperatively and writing your own functions). So what are the advantages of `QueryPipeline`?
  * Express common workflows with fewer lines of code/boilerplate
  * Greater readability
  * Greater parity / better integration points with common low-code / no-code solutions (e.g. LangFlow)
  * [In the future] A declarative interface allows easy serializability of pipeline components, providing portability of pipelines/easier deployment to different systems.


## Cookbook¶
In this cookbook we give you an introduction to our `QueryPipeline` interface and show you some basic workflows you can tackle.
  * Chain together prompt and LLM
  * Chain together query rewriting (prompt + LLM) with retrieval
  * Chain together a full RAG query pipeline (query rewriting, retrieval, reranking, response synthesis)
  * Setting up a custom query component
  * Executing a pipeline step-by-step


## Setup¶
Here we setup some data + indexes (from PG's essay) that we'll be using in the rest of the cookbook.
In [ ]:
Copied!
```
%pip install llama-index-embeddings-openai
%pip install llama-index-postprocessor-cohere-rerank
%pip install llama-index-llms-openai

```

%pip install llama-index-embeddings-openai %pip install llama-index-postprocessor-cohere-rerank %pip install llama-index-llms-openai
In [ ]:
Copied!
```
# setup Arize Phoenix for logging/observability
import phoenix as px

px.launch_app()
import llama_index.core

llama_index.core.set_global_handler("arize_phoenix")

```

# setup Arize Phoenix for logging/observability import phoenix as px px.launch_app() import llama_index.core llama_index.core.set_global_handler("arize_phoenix")
```
🌍 To view the Phoenix app in your browser, visit http://127.0.0.1:6006/
📺 To view the Phoenix app in a notebook, run `px.active_session().view()`
📖 For more information on how to use Phoenix, check out https://docs.arize.com/phoenix

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
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

Settings.llm = OpenAI(model="gpt-3.5-turbo")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

```

from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core import Settings Settings.llm = OpenAI(model="gpt-3.5-turbo") Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

reader = SimpleDirectoryReader("../data/paul_graham")

```

from llama_index.core import SimpleDirectoryReader reader = SimpleDirectoryReader("../data/paul_graham")
In [ ]:
Copied!
```
docs = reader.load_data()

```

docs = reader.load_data()
In [ ]:
Copied!
```
import os
from llama_index.core import (
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)

if not os.path.exists("storage"):
    index = VectorStoreIndex.from_documents(docs)
    # save index to disk
    index.set_index_id("vector_index")
    index.storage_context.persist("./storage")
else:
    # rebuild storage context
    storage_context = StorageContext.from_defaults(persist_dir="storage")
    # load index
    index = load_index_from_storage(storage_context, index_id="vector_index")

```

import os from llama_index.core import ( StorageContext, VectorStoreIndex, load_index_from_storage, ) if not os.path.exists("storage"): index = VectorStoreIndex.from_documents(docs) # save index to disk index.set_index_id("vector_index") index.storage_context.persist("./storage") else: # rebuild storage context storage_context = StorageContext.from_defaults(persist_dir="storage") # load index index = load_index_from_storage(storage_context, index_id="vector_index")
## 1. Chain Together Prompt and LLM¶
In this section we show a super simple workflow of chaining together a prompt with LLM.
We simply define `chain` on initialization. This is a special case of a query pipeline where the components are purely sequential, and we automatically convert outputs into the right format for the next inputs.
In [ ]:
Copied!
```
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core import PromptTemplate

# try chaining basic prompts
prompt_str = "Please generate related movies to {movie_name}"
prompt_tmpl = PromptTemplate(prompt_str)
llm = OpenAI(model="gpt-3.5-turbo")

p = QueryPipeline(chain=[prompt_tmpl, llm], verbose=True)

```

from llama_index.core.query_pipeline import QueryPipeline from llama_index.core import PromptTemplate # try chaining basic prompts prompt_str = "Please generate related movies to {movie_name}" prompt_tmpl = PromptTemplate(prompt_str) llm = OpenAI(model="gpt-3.5-turbo") p = QueryPipeline(chain=[prompt_tmpl, llm], verbose=True)
In [ ]:
Copied!
```
output = p.run(movie_name="The Departed")

```

output = p.run(movie_name="The Departed")
```
> Running module 8dc57d24-9691-4d8d-87d7-151865a7cd1b with input: 
movie_name: The Departed

> Running module 7ed9e26c-a704-4b0b-9cfd-991266e754c0 with input: 
messages: Please generate related movies to The Departed


```

In [ ]:
Copied!
```
print(str(output))

```

print(str(output))
```
assistant: 1. Infernal Affairs (2002) - The original Hong Kong film that inspired The Departed
2. The Town (2010) - A crime thriller directed by and starring Ben Affleck
3. Mystic River (2003) - A crime drama directed by Clint Eastwood
4. Goodfellas (1990) - A classic mobster film directed by Martin Scorsese
5. The Irishman (2019) - Another crime drama directed by Martin Scorsese, starring Robert De Niro and Al Pacino
6. The Departed (2006) - The Departed is a 2006 American crime film directed by Martin Scorsese and written by William Monahan. It is a remake of the 2002 Hong Kong film Infernal Affairs. The film stars Leonardo DiCaprio, Matt Damon, Jack Nicholson, and Mark Wahlberg, with Martin Sheen, Ray Winstone, Vera Farmiga, and Alec Baldwin in supporting roles.

```

### View Intermediate Inputs/Outputs¶
For debugging and other purposes, we can also view the inputs and outputs at each step.
In [ ]:
Copied!
```
output, intermediates = p.run_with_intermediates(movie_name="The Departed")

```

output, intermediates = p.run_with_intermediates(movie_name="The Departed")
```
> Running module 8dc57d24-9691-4d8d-87d7-151865a7cd1b with input: 
movie_name: The Departed

> Running module 7ed9e26c-a704-4b0b-9cfd-991266e754c0 with input: 
messages: Please generate related movies to The Departed


```

In [ ]:
Copied!
```
intermediates["8dc57d24-9691-4d8d-87d7-151865a7cd1b"]

```

intermediates["8dc57d24-9691-4d8d-87d7-151865a7cd1b"]
Out[ ]:
```
ComponentIntermediates(inputs={'movie_name': 'The Departed'}, outputs={'prompt': 'Please generate related movies to The Departed'})
```

In [ ]:
Copied!
```
intermediates["7ed9e26c-a704-4b0b-9cfd-991266e754c0"]

```

intermediates["7ed9e26c-a704-4b0b-9cfd-991266e754c0"]
Out[ ]:
```
ComponentIntermediates(inputs={'messages': 'Please generate related movies to The Departed'}, outputs={'output': ChatResponse(message=ChatMessage(role=<MessageRole.ASSISTANT: 'assistant'>, content='1. Infernal Affairs (2002) - The original Hong Kong film that inspired The Departed\n2. The Town (2010) - A crime thriller directed by Ben Affleck\n3. Mystic River (2003) - A crime drama directed by Clint Eastwood\n4. Goodfellas (1990) - A classic crime film directed by Martin Scorsese\n5. The Irishman (2019) - Another crime film directed by Martin Scorsese, starring Robert De Niro and Al Pacino\n6. The Godfather (1972) - A classic crime film directed by Francis Ford Coppola\n7. Heat (1995) - A crime thriller directed by Michael Mann, starring Al Pacino and Robert De Niro\n8. The Departed (2006) - A crime thriller directed by Martin Scorsese, starring Leonardo DiCaprio and Matt Damon.', additional_kwargs={}), raw={'id': 'chatcmpl-9EKf2nZ4latFJvHy0gzOUZbaB8xwY', 'choices': [Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='1. Infernal Affairs (2002) - The original Hong Kong film that inspired The Departed\n2. The Town (2010) - A crime thriller directed by Ben Affleck\n3. Mystic River (2003) - A crime drama directed by Clint Eastwood\n4. Goodfellas (1990) - A classic crime film directed by Martin Scorsese\n5. The Irishman (2019) - Another crime film directed by Martin Scorsese, starring Robert De Niro and Al Pacino\n6. The Godfather (1972) - A classic crime film directed by Francis Ford Coppola\n7. Heat (1995) - A crime thriller directed by Michael Mann, starring Al Pacino and Robert De Niro\n8. The Departed (2006) - A crime thriller directed by Martin Scorsese, starring Leonardo DiCaprio and Matt Damon.', role='assistant', function_call=None, tool_calls=None))], 'created': 1713203040, 'model': 'gpt-3.5-turbo-0125', 'object': 'chat.completion', 'system_fingerprint': 'fp_c2295e73ad', 'usage': CompletionUsage(completion_tokens=184, prompt_tokens=15, total_tokens=199)}, delta=None, logprobs=None, additional_kwargs={})})
```

### Try Output Parsing¶
Let's parse the outputs into a structured Pydantic object.
In [ ]:
Copied!
```
from typing import List
from pydantic import BaseModel, Field
from llama_index.core.output_parsers import PydanticOutputParser


class Movie(BaseModel):
    """Object representing a single movie."""

    name: str = Field(..., description="Name of the movie.")
    year: int = Field(..., description="Year of the movie.")


class Movies(BaseModel):
    """Object representing a list of movies."""

    movies: List[Movie] = Field(..., description="List of movies.")


llm = OpenAI(model="gpt-3.5-turbo")
output_parser = PydanticOutputParser(Movies)
json_prompt_str = """\
Please generate related movies to {movie_name}. Output with the following JSON format: 
"""
json_prompt_str = output_parser.format(json_prompt_str)

```

from typing import List from pydantic import BaseModel, Field from llama_index.core.output_parsers import PydanticOutputParser class Movie(BaseModel): """Object representing a single movie.""" name: str = Field(..., description="Name of the movie.") year: int = Field(..., description="Year of the movie.") class Movies(BaseModel): """Object representing a list of movies.""" movies: List[Movie] = Field(..., description="List of movies.") llm = OpenAI(model="gpt-3.5-turbo") output_parser = PydanticOutputParser(Movies) json_prompt_str = """\ Please generate related movies to {movie_name}. Output with the following JSON format: """ json_prompt_str = output_parser.format(json_prompt_str)
In [ ]:
Copied!
```
# add JSON spec to prompt template
json_prompt_tmpl = PromptTemplate(json_prompt_str)

p = QueryPipeline(chain=[json_prompt_tmpl, llm, output_parser], verbose=True)
output = p.run(movie_name="Toy Story")

```

# add JSON spec to prompt template json_prompt_tmpl = PromptTemplate(json_prompt_str) p = QueryPipeline(chain=[json_prompt_tmpl, llm, output_parser], verbose=True) output = p.run(movie_name="Toy Story")
```
> Running module 2e4093c5-ae62-420a-be91-9c28c057bada with input: 
movie_name: Toy Story

> Running module 3b41f95c-f54b-41d7-8ef0-8e45b5d7eeb0 with input: 
messages: Please generate related movies to Toy Story. Output with the following JSON format: 



Here's a JSON schema to follow:
{"title": "Movies", "description": "Object representing a list of movies.", "typ...

> Running module 27e79a16-72de-4ce2-8b2e-94932c4069c3 with input: 
input: assistant: {
  "movies": [
    {
      "name": "Finding Nemo",
      "year": 2003
    },
    {
      "name": "Monsters, Inc.",
      "year": 2001
    },
    {
      "name": "Cars",
      "year": 2006
...


```

In [ ]:
Copied!
```
output

```

output
Out[ ]:
```
Movies(movies=[Movie(name='Finding Nemo', year=2003), Movie(name='Monsters, Inc.', year=2001), Movie(name='Cars', year=2006), Movie(name='The Incredibles', year=2004), Movie(name='Ratatouille', year=2007)])
```

### Streaming Support¶
The query pipelines have LLM streaming support (simply do `as_query_component(streaming=True)`). Intermediate outputs will get autoconverted, and the final output can be a streaming output. Here's some examples.
**1. Chain multiple Prompts with Streaming**
In [ ]:
Copied!
```
prompt_str = "Please generate related movies to {movie_name}"
prompt_tmpl = PromptTemplate(prompt_str)
# let's add some subsequent prompts for fun
prompt_str2 = """\
Here's some text:

{text}

Can you rewrite this with a summary of each movie?
"""
prompt_tmpl2 = PromptTemplate(prompt_str2)
llm = OpenAI(model="gpt-3.5-turbo")
llm_c = llm.as_query_component(streaming=True)

p = QueryPipeline(
    chain=[prompt_tmpl, llm_c, prompt_tmpl2, llm_c], verbose=True
)
# p = QueryPipeline(chain=[prompt_tmpl, llm_c], verbose=True)

```

prompt_str = "Please generate related movies to {movie_name}" prompt_tmpl = PromptTemplate(prompt_str) # let's add some subsequent prompts for fun prompt_str2 = """\ Here's some text: {text} Can you rewrite this with a summary of each movie? """ prompt_tmpl2 = PromptTemplate(prompt_str2) llm = OpenAI(model="gpt-3.5-turbo") llm_c = llm.as_query_component(streaming=True) p = QueryPipeline( chain=[prompt_tmpl, llm_c, prompt_tmpl2, llm_c], verbose=True ) # p = QueryPipeline(chain=[prompt_tmpl, llm_c], verbose=True)
In [ ]:
Copied!
```
output = p.run(movie_name="The Dark Knight")
for o in output:
    print(o.delta, end="")

```

output = p.run(movie_name="The Dark Knight") for o in output: print(o.delta, end="")
```
> Running module 213af6d4-3450-46af-9087-b80656ae6951 with input: 
movie_name: The Dark Knight

> Running module 3ff7e987-f5f3-4b36-a3e1-be5a4821d9d9 with input: 
messages: Please generate related movies to The Dark Knight

> Running module a2841bd3-c833-4427-9a7e-83b19872b064 with input: 
text: <generator object llm_chat_callback.<locals>.wrap.<locals>.wrapped_llm_chat.<locals>.wrapped_gen at 0x298d338b0>

> Running module c7e0a454-213a-460e-b029-f2d42fd7d938 with input: 
messages: Here's some text:

1. Batman Begins (2005)
2. The Dark Knight Rises (2012)
3. Batman v Superman: Dawn of Justice (2016)
4. Man of Steel (2013)
5. The Avengers (2012)
6. Iron Man (2008)
7. Captain Amer...

1. Batman Begins (2005): A young Bruce Wayne becomes Batman to fight crime in Gotham City, facing his fears and training under the guidance of Ra's al Ghul.
2. The Dark Knight Rises (2012): Batman returns to protect Gotham City from the ruthless terrorist Bane, who plans to destroy the city and its symbol of hope.
3. Batman v Superman: Dawn of Justice (2016): Batman and Superman clash as their ideologies collide, leading to an epic battle while a new threat emerges that threatens humanity.
4. Man of Steel (2013): The origin story of Superman, as he embraces his powers and faces General Zod, a fellow Kryptonian seeking to destroy Earth.
5. The Avengers (2012): Earth's mightiest heroes, including Iron Man, Captain America, Thor, and Hulk, join forces to stop Loki and his alien army from conquering the world.
6. Iron Man (2008): Billionaire Tony Stark builds a high-tech suit to escape captivity and becomes the superhero Iron Man, using his technology to fight against evil.
7. Captain America: The Winter Soldier (2014): Captain America teams up with Black Widow and Falcon to uncover a conspiracy within S.H.I.E.L.D. while facing a deadly assassin known as the Winter Soldier.
8. The Amazing Spider-Man (2012): Peter Parker, a high school student bitten by a radioactive spider, becomes Spider-Man and battles the Lizard, a monstrous villain threatening New York City.
9. Watchmen (2009): Set in an alternate reality, a group of retired vigilantes investigates the murder of one of their own, uncovering a conspiracy that could have catastrophic consequences.
10. Sin City (2005): A neo-noir anthology film set in the crime-ridden city of Basin City, following various characters as they navigate through corruption, violence, and redemption.
11. V for Vendetta (2005): In a dystopian future, a masked vigilante known as V fights against a totalitarian government, inspiring the people to rise up and reclaim their freedom.
12. Blade Runner 2049 (2017): A young blade runner uncovers a long-buried secret that leads him to seek out former blade runner Rick Deckard, while unraveling the mysteries of a future society.
13. Inception (2010): A skilled thief enters people's dreams to steal information, but is tasked with planting an idea instead, leading to a mind-bending journey through multiple layers of reality.
14. The Matrix (1999): A computer hacker discovers the truth about reality, joining a group of rebels fighting against sentient machines that have enslaved humanity in a simulated world.
15. The Crow (1994): A musician, resurrected by a supernatural crow, seeks vengeance against the gang that murdered him and his fiancée, unleashing a dark and atmospheric tale of revenge.
```

**2. Feed streaming output to output parser**
In [ ]:
Copied!
```
p = QueryPipeline(
    chain=[
        json_prompt_tmpl,
        llm.as_query_component(streaming=True),
        output_parser,
    ],
    verbose=True,
)
output = p.run(movie_name="Toy Story")
print(output)

```

p = QueryPipeline( chain=[ json_prompt_tmpl, llm.as_query_component(streaming=True), output_parser, ], verbose=True, ) output = p.run(movie_name="Toy Story") print(output)
```
> Running module fe1dbf6a-56e0-44bf-97d7-a2a1fe9d9b8c with input: 
movie_name: Toy Story

> Running module a8eaaf91-df9d-46c4-bbae-06c15cd15123 with input: 
messages: Please generate related movies to Toy Story. Output with the following JSON format: 



Here's a JSON schema to follow:
{"title": "Movies", "description": "Object representing a list of movies.", "typ...

> Running module fcbc0b09-0ef5-43e0-b007-c4508fd6742f with input: 
input: <generator object llm_chat_callback.<locals>.wrap.<locals>.wrapped_llm_chat.<locals>.wrapped_gen at 0x298d32dc0>

movies=[Movie(name='Finding Nemo', year=2003), Movie(name='Monsters, Inc.', year=2001), Movie(name='The Incredibles', year=2004), Movie(name='Cars', year=2006), Movie(name='Ratatouille', year=2007)]

```

## Chain Together Query Rewriting Workflow (prompts + LLM) with Retrieval¶
Here we try a slightly more complex workflow where we send the input through two prompts before initiating retrieval.
  1. Generate question about given topic.
  2. Hallucinate answer given question, for better retrieval.


Since each prompt only takes in one input, note that the `QueryPipeline` will automatically chain LLM outputs into the prompt and then into the LLM.
You'll see how to define links more explicitly in the next section.
In [ ]:
Copied!
```
# !pip install llama-index-postprocessor-cohere-rerank

```

# !pip install llama-index-postprocessor-cohere-rerank
In [ ]:
Copied!
```
from llama_index.postprocessor.cohere_rerank import CohereRerank

# generate question regarding topic
prompt_str1 = "Please generate a concise question about Paul Graham's life regarding the following topic {topic}"
prompt_tmpl1 = PromptTemplate(prompt_str1)
# use HyDE to hallucinate answer.
prompt_str2 = (
    "Please write a passage to answer the question\n"
    "Try to include as many key details as possible.\n"
    "\n"
    "\n"
    "{query_str}\n"
    "\n"
    "\n"
    'Passage:"""\n'
)
prompt_tmpl2 = PromptTemplate(prompt_str2)

llm = OpenAI(model="gpt-3.5-turbo")
retriever = index.as_retriever(similarity_top_k=5)
p = QueryPipeline(
    chain=[prompt_tmpl1, llm, prompt_tmpl2, llm, retriever], verbose=True
)

```

from llama_index.postprocessor.cohere_rerank import CohereRerank # generate question regarding topic prompt_str1 = "Please generate a concise question about Paul Graham's life regarding the following topic {topic}" prompt_tmpl1 = PromptTemplate(prompt_str1) # use HyDE to hallucinate answer. prompt_str2 = ( "Please write a passage to answer the question\n" "Try to include as many key details as possible.\n" "\n" "\n" "{query_str}\n" "\n" "\n" 'Passage:"""\n' ) prompt_tmpl2 = PromptTemplate(prompt_str2) llm = OpenAI(model="gpt-3.5-turbo") retriever = index.as_retriever(similarity_top_k=5) p = QueryPipeline( chain=[prompt_tmpl1, llm, prompt_tmpl2, llm, retriever], verbose=True )
In [ ]:
Copied!
```
nodes = p.run(topic="college")
len(nodes)

```

nodes = p.run(topic="college") len(nodes)
```
> Running module f5435516-61b6-49e9-9926-220cfb6443bd with input: 
topic: college

> Running module 1dcaa097-cedc-4466-81bb-f8fd8768762b with input: 
messages: Please generate a concise question about Paul Graham's life regarding the following topic college

> Running module 891afa10-5fe0-47ed-bdee-42a59d0e916d with input: 
query_str: assistant: How did Paul Graham's college experience shape his career and entrepreneurial mindset?

> Running module 5bcd9964-b972-41a9-960d-96894c57a372 with input: 
messages: Please write a passage to answer the question
Try to include as many key details as possible.


How did Paul Graham's college experience shape his career and entrepreneurial mindset?


Passage:"""


> Running module 0b81a91a-2c90-4700-8ba1-25ffad5311fd with input: 
input: assistant: Paul Graham's college experience played a pivotal role in shaping his career and entrepreneurial mindset. As a student at Cornell University, Graham immersed himself in the world of compute...


```

Out[ ]:


## Create a Full RAG Pipeline as a DAG¶
Here we chain together a full RAG pipeline consisting of query rewriting, retrieval, reranking, and response synthesis.
Here we can't use `chain` syntax because certain modules depend on multiple inputs (for instance, response synthesis expects both the retrieved nodes and the original question). Instead we'll construct a DAG explicitly, through `add_modules` and then `add_link`.
### 1. RAG Pipeline with Query Rewriting¶
We use an LLM to rewrite the query first before passing it to our downstream modules - retrieval/reranking/synthesis.
In [ ]:
Copied!
```
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.response_synthesizers import TreeSummarize


# define modules
prompt_str = "Please generate a question about Paul Graham's life regarding the following topic {topic}"
prompt_tmpl = PromptTemplate(prompt_str)
llm = OpenAI(model="gpt-3.5-turbo")
retriever = index.as_retriever(similarity_top_k=3)
reranker = CohereRerank()
summarizer = TreeSummarize(llm=llm)

```

from llama_index.postprocessor.cohere_rerank import CohereRerank from llama_index.core.response_synthesizers import TreeSummarize # define modules prompt_str = "Please generate a question about Paul Graham's life regarding the following topic {topic}" prompt_tmpl = PromptTemplate(prompt_str) llm = OpenAI(model="gpt-3.5-turbo") retriever = index.as_retriever(similarity_top_k=3) reranker = CohereRerank() summarizer = TreeSummarize(llm=llm)
In [ ]:
Copied!
```
# define query pipeline
p = QueryPipeline(verbose=True)
p.add_modules(
    {
        "llm": llm,
        "prompt_tmpl": prompt_tmpl,
        "retriever": retriever,
        "summarizer": summarizer,
        "reranker": reranker,
    }
)

```

# define query pipeline p = QueryPipeline(verbose=True) p.add_modules( { "llm": llm, "prompt_tmpl": prompt_tmpl, "retriever": retriever, "summarizer": summarizer, "reranker": reranker, } )
Next we draw links between modules with `add_link`. `add_link` takes in the source/destination module ids, and optionally the `source_key` and `dest_key`. Specify the `source_key` or `dest_key` if there are multiple outputs/inputs respectively.
You can view the set of input/output keys for each module through `module.as_query_component().input_keys` and `module.as_query_component().output_keys`.
Here we explicitly specify `dest_key` for the `reranker` and `summarizer` modules because they take in two inputs (query_str and nodes).
In [ ]:
Copied!
```
p.add_link("prompt_tmpl", "llm")
p.add_link("llm", "retriever")
p.add_link("retriever", "reranker", dest_key="nodes")
p.add_link("llm", "reranker", dest_key="query_str")
p.add_link("reranker", "summarizer", dest_key="nodes")
p.add_link("llm", "summarizer", dest_key="query_str")

# look at summarizer input keys
print(summarizer.as_query_component().input_keys)

```

p.add_link("prompt_tmpl", "llm") p.add_link("llm", "retriever") p.add_link("retriever", "reranker", dest_key="nodes") p.add_link("llm", "reranker", dest_key="query_str") p.add_link("reranker", "summarizer", dest_key="nodes") p.add_link("llm", "summarizer", dest_key="query_str") # look at summarizer input keys print(summarizer.as_query_component().input_keys)
```
required_keys={'query_str', 'nodes'} optional_keys=set()

```

We use `networkx` to store the graph representation. This gives us an easy way to view the DAG!
In [ ]:
Copied!
```
## create graph
from pyvis.network import Network

net = Network(notebook=True, cdn_resources="in_line", directed=True)
net.from_nx(p.dag)
net.show("rag_dag.html")

## another option using `pygraphviz`
# from networkx.drawing.nx_agraph import to_agraph
# from IPython.display import Image
# agraph = to_agraph(p.dag)
# agraph.layout(prog="dot")
# agraph.draw('rag_dag.png')
# display(Image('rag_dag.png'))

```

## create graph from pyvis.network import Network net = Network(notebook=True, cdn_resources="in_line", directed=True) net.from_nx(p.dag) net.show("rag_dag.html") ## another option using `pygraphviz` # from networkx.drawing.nx_agraph import to_agraph # from IPython.display import Image # agraph = to_agraph(p.dag) # agraph.layout(prog="dot") # agraph.draw('rag_dag.png') # display(Image('rag_dag.png'))
```
rag_dag.html

```

Out[ ]:
In [ ]:
Copied!
```
response = p.run(topic="YC")

```

response = p.run(topic="YC")
```
> Running module prompt_tmpl with input: 
topic: YC

> Running module llm with input: 
messages: Please generate a question about Paul Graham's life regarding the following topic YC

> Running module retriever with input: 
input: assistant: What role did Paul Graham play in the founding and development of Y Combinator (YC)?

> Running module reranker with input: 
query_str: assistant: What role did Paul Graham play in the founding and development of Y Combinator (YC)?
nodes: [NodeWithScore(node=TextNode(id_='ccd39041-5a64-4bd3-aca7-48f804b5a23f', embedding=None, metadata={'file_path': '../data/paul_graham/paul_graham_essay.txt', 'file_name': 'paul_graham_essay.txt', 'file...

> Running module summarizer with input: 
query_str: assistant: What role did Paul Graham play in the founding and development of Y Combinator (YC)?
nodes: [NodeWithScore(node=TextNode(id_='120574dd-a5c9-4985-ab3e-37b1070b500a', embedding=None, metadata={'file_path': '../data/paul_graham/paul_graham_essay.txt', 'file_name': 'paul_graham_essay.txt', 'file...


```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Paul Graham played a significant role in the founding and development of Y Combinator (YC). He was one of the co-founders of YC and provided the initial funding for the investment firm. Along with his partners, he implemented the ideas they had been discussing and started their own investment firm. Paul Graham also played a key role in shaping the unique batch model of YC, where a group of startups is funded and provided intensive support for a period of three months. He was actively involved in selecting and helping the founders, and he also wrote essays and worked on YC's internal software.

```

In [ ]:
Copied!
```
# you can do async too
response = await p.arun(topic="YC")
print(str(response))

```

# you can do async too response = await p.arun(topic="YC") print(str(response))
```
> Running modules and inputs in parallel: 
Module key: prompt_tmpl. Input: 
topic: YC


> Running modules and inputs in parallel: 
Module key: llm. Input: 
messages: Please generate a question about Paul Graham's life regarding the following topic YC


> Running modules and inputs in parallel: 
Module key: retriever. Input: 
input: assistant: What role did Paul Graham play in the founding and development of Y Combinator (YC)?


> Running modules and inputs in parallel: 
Module key: reranker. Input: 
query_str: assistant: What role did Paul Graham play in the founding and development of Y Combinator (YC)?
nodes: [NodeWithScore(node=TextNode(id_='ccd39041-5a64-4bd3-aca7-48f804b5a23f', embedding=None, metadata={'file_path': '../data/paul_graham/paul_graham_essay.txt', 'file_name': 'paul_graham_essay.txt', 'file...


> Running modules and inputs in parallel: 
Module key: summarizer. Input: 
query_str: assistant: What role did Paul Graham play in the founding and development of Y Combinator (YC)?
nodes: [NodeWithScore(node=TextNode(id_='120574dd-a5c9-4985-ab3e-37b1070b500a', embedding=None, metadata={'file_path': '../data/paul_graham/paul_graham_essay.txt', 'file_name': 'paul_graham_essay.txt', 'file...


Paul Graham played a significant role in the founding and development of Y Combinator (YC). He was one of the co-founders of YC and provided the initial funding for the investment firm. Along with his partners, he implemented the ideas they had been discussing and decided to start their own investment firm. Paul Graham also played a key role in shaping the unique batch model of YC, where a group of startups is funded and provided intensive support for a period of three months. He was actively involved in selecting and helping the founders and worked on various projects related to YC, including writing essays and developing internal software.

```

### 2. RAG Pipeline without Query Rewriting¶
Here we setup a RAG pipeline without the query rewriting step.
Here we need a way to link the input query to both the retriever, reranker, and summarizer. We can do this by defining a special `InputComponent`, allowing us to link the inputs to multiple downstream modules.
In [ ]:
Copied!
```
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.query_pipeline import InputComponent

retriever = index.as_retriever(similarity_top_k=5)
summarizer = TreeSummarize(llm=OpenAI(model="gpt-3.5-turbo"))
reranker = CohereRerank()

```

from llama_index.postprocessor.cohere_rerank import CohereRerank from llama_index.core.response_synthesizers import TreeSummarize from llama_index.core.query_pipeline import InputComponent retriever = index.as_retriever(similarity_top_k=5) summarizer = TreeSummarize(llm=OpenAI(model="gpt-3.5-turbo")) reranker = CohereRerank()
In [ ]:
Copied!
```
p = QueryPipeline(verbose=True)
p.add_modules(
    {
        "input": InputComponent(),
        "retriever": retriever,
        "summarizer": summarizer,
    }
)
p.add_link("input", "retriever")
p.add_link("input", "summarizer", dest_key="query_str")
p.add_link("retriever", "summarizer", dest_key="nodes")

```

p = QueryPipeline(verbose=True) p.add_modules( { "input": InputComponent(), "retriever": retriever, "summarizer": summarizer, } ) p.add_link("input", "retriever") p.add_link("input", "summarizer", dest_key="query_str") p.add_link("retriever", "summarizer", dest_key="nodes")
In [ ]:
Copied!
```
output = p.run(input="what did the author do in YC")

```

output = p.run(input="what did the author do in YC")
```
> Running module input with input: 
input: what did the author do in YC

> Running module retriever with input: 
input: what did the author do in YC

> Running module summarizer with input: 
query_str: what did the author do in YC
nodes: [NodeWithScore(node=TextNode(id_='86dea730-ca35-4bcb-9f9b-4c99e8eadd08', embedding=None, metadata={'file_path': '../data/paul_graham/paul_graham_essay.txt', 'file_name': 'paul_graham_essay.txt', 'file...


```

In [ ]:
Copied!
```
print(str(output))

```

print(str(output))
```
The author worked on various projects at YC, including writing essays and working on YC's internal software. They also played a key role in the creation and operation of YC by funding the program with their own money and organizing a batch model where they would fund a group of startups twice a year. They provided support and guidance to the startups during a three-month intensive program and used their building in Cambridge as the headquarters for YC. Additionally, they hosted weekly dinners where experts on startups would give talks.

```

## Defining a Custom Component in a Query Pipeline¶
You can easily define a custom component. Simply subclass a `QueryComponent`, implement validation/run functions + some helpers, and plug it in.
Let's wrap the related movie generation prompt+LLM chain from the first example into a custom component.
In [ ]:
Copied!
```
from llama_index.core.query_pipeline import (
    CustomQueryComponent,
    InputKeys,
    OutputKeys,
)
from typing import Dict, Any
from llama_index.core.llms.llm import LLM
from pydantic import Field


class RelatedMovieComponent(CustomQueryComponent):
    """Related movie component."""

    llm: LLM = Field(..., description="OpenAI LLM")

    def _validate_component_inputs(
        self, input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        # NOTE: this is OPTIONAL but we show you here how to do validation as an example
        return input

    @property
    def _input_keys(self) -> set:
        """Input keys dict."""
        # NOTE: These are required inputs. If you have optional inputs please override
        # `optional_input_keys_dict`
        return {"movie"}

    @property
    def _output_keys(self) -> set:
        return {"output"}

    def _run_component(self, **kwargs) -> Dict[str, Any]:
        """Run the component."""
        # use QueryPipeline itself here for convenience
        prompt_str = "Please generate related movies to {movie_name}"
        prompt_tmpl = PromptTemplate(prompt_str)
        p = QueryPipeline(chain=[prompt_tmpl, llm])
        return {"output": p.run(movie_name=kwargs["movie"])}

```

from llama_index.core.query_pipeline import ( CustomQueryComponent, InputKeys, OutputKeys, ) from typing import Dict, Any from llama_index.core.llms.llm import LLM from pydantic import Field class RelatedMovieComponent(CustomQueryComponent): """Related movie component.""" llm: LLM = Field(..., description="OpenAI LLM") def _validate_component_inputs( self, input: Dict[str, Any] ) -> Dict[str, Any]: """Validate component inputs during run_component.""" # NOTE: this is OPTIONAL but we show you here how to do validation as an example return input @property def _input_keys(self) -> set: """Input keys dict.""" # NOTE: These are required inputs. If you have optional inputs please override # `optional_input_keys_dict` return {"movie"} @property def _output_keys(self) -> set: return {"output"} def _run_component(self, **kwargs) -> Dict[str, Any]: """Run the component.""" # use QueryPipeline itself here for convenience prompt_str = "Please generate related movies to {movie_name}" prompt_tmpl = PromptTemplate(prompt_str) p = QueryPipeline(chain=[prompt_tmpl, llm]) return {"output": p.run(movie_name=kwargs["movie"])}
Let's try the custom component out! We'll also add a step to convert the output to Shakespeare.
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-3.5-turbo")
component = RelatedMovieComponent(llm=llm)

# let's add some subsequent prompts for fun
prompt_str = """\
Here's some text:

{text}

Can you rewrite this in the voice of Shakespeare?
"""
prompt_tmpl = PromptTemplate(prompt_str)

p = QueryPipeline(chain=[component, prompt_tmpl, llm], verbose=True)

```

llm = OpenAI(model="gpt-3.5-turbo") component = RelatedMovieComponent(llm=llm) # let's add some subsequent prompts for fun prompt_str = """\ Here's some text: {text} Can you rewrite this in the voice of Shakespeare? """ prompt_tmpl = PromptTemplate(prompt_str) p = QueryPipeline(chain=[component, prompt_tmpl, llm], verbose=True)
In [ ]:
Copied!
```
output = p.run(movie="Love Actually")

```

output = p.run(movie="Love Actually")
```
> Running module 31ca224a-f226-4956-882b-73878843d869 with input: 
movie: Love Actually

> Running module febb41b5-2528-416a-bde7-6accdb0f9c51 with input: 
text: assistant: 1. "Valentine's Day" (2010)
2. "New Year's Eve" (2011)
3. "The Holiday" (2006)
4. "Crazy, Stupid, Love" (2011)
5. "Notting Hill" (1999)
6. "Four Weddings and a Funeral" (1994)
7. "Bridget J...

> Running module e834ffbe-e97c-4ab0-9726-24f1534745b2 with input: 
messages: Here's some text:

1. "Valentine's Day" (2010)
2. "New Year's Eve" (2011)
3. "The Holiday" (2006)
4. "Crazy, Stupid, Love" (2011)
5. "Notting Hill" (1999)
6. "Four Weddings and a Funeral" (1994)
7. "B...


```

In [ ]:
Copied!
```
print(str(output))

```

print(str(output))
```
assistant: 1. "Valentine's Day" (2010) - "A day of love, where hearts entwine, 
   And Cupid's arrow finds its mark divine."

2. "New Year's Eve" (2011) - "When old year fades, and new year dawns,
   We gather 'round, to celebrate the morns."

3. "The Holiday" (2006) - "Two souls, adrift in search of cheer,
   Find solace in a holiday so dear."

4. "Crazy, Stupid, Love" (2011) - "A tale of love, both wild and mad,
   Where hearts are lost, then found, and glad."

5. "Notting Hill" (1999) - "In London town, where love may bloom,
   A humble man finds love, and breaks the gloom."

6. "Four Weddings and a Funeral" (1994) - "Four times the vows, and one time mourn,
   Love's journey, with laughter and tears adorned."

7. "Bridget Jones's Diary" (2001) - "A maiden fair, with wit and charm,
   Records her life, and love's alarm."

8. "About Time" (2013) - "A tale of time, where love transcends,
   And moments cherished, never truly ends."

9. "The Best Exotic Marigold Hotel" (2011) - "In India's land, where dreams unfold,
   A hotel blooms, where hearts find gold."

10. "The Notebook" (2004) - "A love that spans both time and space,
    Where words and memories find their place."

11. "Serendipity" (2001) - "By chance or fate, two souls collide,
    In search of love, they cannot hide."

12. "P.S. I Love You" (2007) - "In letters penned, from love's embrace,
    A departed soul, still finds its trace."

13. "500 Days of Summer" (2009) - "A tale of love, both sweet and sour,
    Where seasons change, and hearts devour."

14. "The Fault in Our Stars" (2014) - "Two hearts, aflame, in starlit skies,
    Love's tragedy, where hope never dies."

15. "La La Land" (2016) - "In dreams and songs, two hearts entwine,
    A city's magic, where love's stars align."

```

## Stepwise Execution of a Pipeline¶
Executing a pipeline one step at a time is a great idea if you:
  * want to better debug the order of execution
  * log data in between each step
  * give feedback to a user as to what is being processed
  * and more!


To execute a pipeline, you must create a `run_state`, and then loop through the exection. A basic example is below.
In [ ]:
Copied!
```
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI

# try chaining basic prompts
prompt_str = "Please generate related movies to {movie_name}"
prompt_tmpl = PromptTemplate(prompt_str)
llm = OpenAI(model="gpt-3.5-turbo")

p = QueryPipeline(chain=[prompt_tmpl, llm], verbose=True)

```

from llama_index.core.query_pipeline import QueryPipeline from llama_index.core import PromptTemplate from llama_index.llms.openai import OpenAI # try chaining basic prompts prompt_str = "Please generate related movies to {movie_name}" prompt_tmpl = PromptTemplate(prompt_str) llm = OpenAI(model="gpt-3.5-turbo") p = QueryPipeline(chain=[prompt_tmpl, llm], verbose=True)
In [ ]:
Copied!
```
run_state = p.get_run_state(movie_name="The Departed")

next_module_keys = p.get_next_module_keys(run_state)

while True:
    for module_key in next_module_keys:
        # get the module and input
        module = run_state.module_dict[module_key]
        module_input = run_state.all_module_inputs[module_key]

        # run the module
        output_dict = module.run_component(**module_input)

        # process the output
        p.process_component_output(
            output_dict,
            module_key,
            run_state,
        )

    # get the next module keys
    next_module_keys = p.get_next_module_keys(
        run_state,
    )

    # if no more modules to run, break
    if not next_module_keys:
        run_state.result_outputs[module_key] = output_dict
        break

# the final result is at `module_key`
# it is a dict of 'output' -> ChatResponse object in this case
print(run_state.result_outputs[module_key]["output"].message.content)

```

run_state = p.get_run_state(movie_name="The Departed") next_module_keys = p.get_next_module_keys(run_state) while True: for module_key in next_module_keys: # get the module and input module = run_state.module_dict[module_key] module_input = run_state.all_module_inputs[module_key] # run the module output_dict = module.run_component(**module_input) # process the output p.process_component_output( output_dict, module_key, run_state, ) # get the next module keys next_module_keys = p.get_next_module_keys( run_state, ) # if no more modules to run, break if not next_module_keys: run_state.result_outputs[module_key] = output_dict break # the final result is at `module_key` # it is a dict of 'output' -> ChatResponse object in this case print(run_state.result_outputs[module_key]["output"].message.content)
```
1. Infernal Affairs (2002) - The original Hong Kong film that inspired The Departed
2. The Town (2010) - A crime thriller directed by Ben Affleck
3. Mystic River (2003) - A crime drama directed by Clint Eastwood
4. Goodfellas (1990) - A classic mobster film directed by Martin Scorsese
5. The Irishman (2019) - Another crime drama directed by Martin Scorsese, starring Robert De Niro and Al Pacino
6. The Departed (2006) - The Departed is a 2006 American crime film directed by Martin Scorsese and written by William Monahan. It is a remake of the 2002 Hong Kong film Infernal Affairs. The film stars Leonardo DiCaprio, Matt Damon, Jack Nicholson, and Mark Wahlberg, with Martin Sheen, Ray Winstone, Vera Farmiga, and Alec Baldwin in supporting roles.

```

