![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Router Fine-tuning¶
In this notebook, we experiment with fine-tuning an LLM-powered router. We try a few different approaches, with query + ground-truth "choice" as the training signal.
  1. Fine-tuning embeddings
  2. Fine-tuning a cross-encoder


Our dataset will be Wikipedia articles of different cities.
We will generate a synthetic dataset for each approach to fine-tune over. We will also run some basic evaluations.
In [ ]:
Copied!
```
%pip install llama-index-finetuning
%pip install llama-index-llms-openai

```

%pip install llama-index-finetuning %pip install llama-index-llms-openai
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
!pip install spacy

```

!pip install spacy
## Setup¶
In [ ]:
Copied!
```
wiki_titles = [
    "Toronto",
    "Seattle",
    "Chicago",
    "Boston",
    "Houston",
    "Tokyo",
    "Berlin",
    "Lisbon",
]

```

wiki_titles = [ "Toronto", "Seattle", "Chicago", "Boston", "Houston", "Tokyo", "Berlin", "Lisbon", ]
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
from llama_index.core import SimpleDirectoryReader

# Load all wiki documents
city_docs = {}
for wiki_title in wiki_titles:
    city_docs[wiki_title] = SimpleDirectoryReader(
        input_files=[f"data/{wiki_title}.txt"]
    ).load_data()

```

from llama_index.core import SimpleDirectoryReader # Load all wiki documents city_docs = {} for wiki_title in wiki_titles: city_docs[wiki_title] = SimpleDirectoryReader( input_files=[f"data/{wiki_title}.txt"] ).load_data()
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)

```

from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo", temperature=0.3)
In [ ]:
Copied!
```
# define descriptions/choices for tools
city_descs_dict = {}
# these choices will be passed to the router selector
choices = []
choice_to_id_dict = {}

for idx, wiki_title in enumerate(wiki_titles):
    vector_desc = (
        "Useful for questions related to specific aspects of"
        f" {wiki_title} (e.g. the history, arts and culture,"
        " sports, demographics, or more)."
    )
    summary_desc = (
        "Useful for any requests that require a holistic summary"
        f" of EVERYTHING about {wiki_title}. For questions about"
        " more specific sections, please use the vector_tool."
    )
    doc_id_vector = f"{wiki_title}_vector"
    doc_id_summary = f"{wiki_title}_summary"
    city_descs_dict[doc_id_vector] = vector_desc
    city_descs_dict[doc_id_summary] = summary_desc

    choices.extend([vector_desc, summary_desc])
    choice_to_id_dict[idx * 2] = f"{wiki_title}_vector"
    choice_to_id_dict[idx * 2 + 1] = f"{wiki_title}_summary"

```

# define descriptions/choices for tools city_descs_dict = {} # these choices will be passed to the router selector choices = [] choice_to_id_dict = {} for idx, wiki_title in enumerate(wiki_titles): vector_desc = ( "Useful for questions related to specific aspects of" f" {wiki_title} (e.g. the history, arts and culture," " sports, demographics, or more)." ) summary_desc = ( "Useful for any requests that require a holistic summary" f" of EVERYTHING about {wiki_title}. For questions about" " more specific sections, please use the vector_tool." ) doc_id_vector = f"{wiki_title}_vector" doc_id_summary = f"{wiki_title}_summary" city_descs_dict[doc_id_vector] = vector_desc city_descs_dict[doc_id_summary] = summary_desc choices.extend([vector_desc, summary_desc]) choice_to_id_dict[idx * 2] = f"{wiki_title}_vector" choice_to_id_dict[idx * 2 + 1] = f"{wiki_title}_summary"
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

llm = OpenAI(model_name="gpt-3.5-turbo")

summary_q_tmpl = """\
You are a summary question generator. Given an existing question which asks for a summary of a given topic, \
generate {num_vary} related queries that also ask for a summary of the topic.

For example, assuming we're generating 3 related questions:
Base Question: Can you tell me more about Boston?
Question Variations:
Give me an overview of Boston as a city.
Can you describe different aspects of Boston, from the history to the sports scene to the food?
Write a concise summary of Boston; I've never been.

Now let's give it a shot! 

Base Question: {base_question}
Question Variations:
"""
summary_q_prompt = PromptTemplate(summary_q_tmpl)

```

from llama_index.llms.openai import OpenAI from llama_index.core import PromptTemplate llm = OpenAI(model_name="gpt-3.5-turbo") summary_q_tmpl = """\ You are a summary question generator. Given an existing question which asks for a summary of a given topic, \ generate {num_vary} related queries that also ask for a summary of the topic. For example, assuming we're generating 3 related questions: Base Question: Can you tell me more about Boston? Question Variations: Give me an overview of Boston as a city. Can you describe different aspects of Boston, from the history to the sports scene to the food? Write a concise summary of Boston; I've never been. Now let's give it a shot! Base Question: {base_question} Question Variations: """ summary_q_prompt = PromptTemplate(summary_q_tmpl)
In [ ]:
Copied!
```
from collections import defaultdict
from llama_index.core.evaluation import DatasetGenerator
from llama_index.core.evaluation import EmbeddingQAFinetuneDataset
from llama_index.core.node_parser import SimpleNodeParser
from tqdm.notebook import tqdm


def generate_dataset(
    wiki_titles,
    city_descs_dict,
    llm,
    summary_q_prompt,
    num_vector_qs_per_node=2,
    num_summary_qs=4,
):
    # generate dataset from each wikipedia page
    queries = {}
    corpus = {}
    relevant_docs = defaultdict(list)
    for idx, wiki_title in enumerate(tqdm(wiki_titles)):
        doc_id_vector = f"{wiki_title}_vector"
        doc_id_summary = f"{wiki_title}_summary"
        corpus[doc_id_vector] = city_descs_dict[doc_id_vector]
        corpus[doc_id_summary] = city_descs_dict[doc_id_summary]

        # generate questions for semantic search
        node_parser = SimpleNodeParser.from_defaults()
        nodes = node_parser.get_nodes_from_documents(city_docs[wiki_title])

        dataset_generator = DatasetGenerator(
            nodes,
            llm=llm,
            num_questions_per_chunk=num_vector_qs_per_node,
        )
        doc_questions = dataset_generator.generate_questions_from_nodes(
            num=len(nodes) * num_vector_qs_per_node
        )
        for query_idx, doc_question in enumerate(doc_questions):
            query_id = f"{wiki_title}_{query_idx}"
            relevant_docs[query_id] = [doc_id_vector]
            queries[query_id] = doc_question

        # generate questions for summarization
        base_q = f"Give me a summary of {wiki_title}"
        fmt_prompt = summary_q_prompt.format(
            num_vary=num_summary_qs,
            base_question=base_q,
        )
        raw_response = llm.complete(fmt_prompt)
        raw_lines = str(raw_response).split("\n")
        doc_summary_questions = [l for l in raw_lines if l != ""]
        print(f"[{idx}] Original Question: {base_q}")
        print(
            f"[{idx}] Generated Question Variations: {doc_summary_questions}"
        )
        for query_idx, doc_summary_question in enumerate(
            doc_summary_questions
        ):
            query_id = f"{wiki_title}_{query_idx}"
            relevant_docs[query_id] = [doc_id_summary]
            queries[query_id] = doc_summary_question

    return EmbeddingQAFinetuneDataset(
        queries=queries, corpus=corpus, relevant_docs=relevant_docs
    )

```

from collections import defaultdict from llama_index.core.evaluation import DatasetGenerator from llama_index.core.evaluation import EmbeddingQAFinetuneDataset from llama_index.core.node_parser import SimpleNodeParser from tqdm.notebook import tqdm def generate_dataset( wiki_titles, city_descs_dict, llm, summary_q_prompt, num_vector_qs_per_node=2, num_summary_qs=4, ): # generate dataset from each wikipedia page queries = {} corpus = {} relevant_docs = defaultdict(list) for idx, wiki_title in enumerate(tqdm(wiki_titles)): doc_id_vector = f"{wiki_title}_vector" doc_id_summary = f"{wiki_title}_summary" corpus[doc_id_vector] = city_descs_dict[doc_id_vector] corpus[doc_id_summary] = city_descs_dict[doc_id_summary] # generate questions for semantic search node_parser = SimpleNodeParser.from_defaults() nodes = node_parser.get_nodes_from_documents(city_docs[wiki_title]) dataset_generator = DatasetGenerator( nodes, llm=llm, num_questions_per_chunk=num_vector_qs_per_node, ) doc_questions = dataset_generator.generate_questions_from_nodes( num=len(nodes) * num_vector_qs_per_node ) for query_idx, doc_question in enumerate(doc_questions): query_id = f"{wiki_title}_{query_idx}" relevant_docs[query_id] = [doc_id_vector] queries[query_id] = doc_question # generate questions for summarization base_q = f"Give me a summary of {wiki_title}" fmt_prompt = summary_q_prompt.format( num_vary=num_summary_qs, base_question=base_q, ) raw_response = llm.complete(fmt_prompt) raw_lines = str(raw_response).split("\n") doc_summary_questions = [l for l in raw_lines if l != ""] print(f"[{idx}] Original Question: {base_q}") print( f"[{idx}] Generated Question Variations: {doc_summary_questions}" ) for query_idx, doc_summary_question in enumerate( doc_summary_questions ): query_id = f"{wiki_title}_{query_idx}" relevant_docs[query_id] = [doc_id_summary] queries[query_id] = doc_summary_question return EmbeddingQAFinetuneDataset( queries=queries, corpus=corpus, relevant_docs=relevant_docs )
In [ ]:
Copied!
```
dataset = generate_dataset(
    wiki_titles,
    city_descs_dict,
    llm,
    summary_q_prompt,
    num_vector_qs_per_node=4,
    num_summary_qs=5,
)

```

dataset = generate_dataset( wiki_titles, city_descs_dict, llm, summary_q_prompt, num_vector_qs_per_node=4, num_summary_qs=5, )
In [ ]:
Copied!
```
# dataset.queries

```

# dataset.queries
In [ ]:
Copied!
```
# [optional] save
dataset.save_json("dataset.json")

```

# [optional] save dataset.save_json("dataset.json")
In [ ]:
Copied!
```
# [optional] load
dataset = EmbeddingQAFinetuneDataset.from_json("dataset.json")

```

# [optional] load dataset = EmbeddingQAFinetuneDataset.from_json("dataset.json")
In [ ]:
Copied!
```
import random


def split_train_val_by_query(dataset, split=0.7):
    """Split dataset by queries."""
    query_ids = list(dataset.queries.keys())
    query_ids_shuffled = random.sample(query_ids, len(query_ids))
    split_idx = int(len(query_ids) * split)
    train_query_ids = query_ids_shuffled[:split_idx]
    eval_query_ids = query_ids_shuffled[split_idx:]

    train_queries = {qid: dataset.queries[qid] for qid in train_query_ids}
    eval_queries = {qid: dataset.queries[qid] for qid in eval_query_ids}

    train_rel_docs = {
        qid: dataset.relevant_docs[qid] for qid in train_query_ids
    }
    eval_rel_docs = {qid: dataset.relevant_docs[qid] for qid in eval_query_ids}

    train_dataset = EmbeddingQAFinetuneDataset(
        queries=train_queries,
        corpus=dataset.corpus,
        relevant_docs=train_rel_docs,
    )
    eval_dataset = EmbeddingQAFinetuneDataset(
        queries=eval_queries,
        corpus=dataset.corpus,
        relevant_docs=eval_rel_docs,
    )
    return train_dataset, eval_dataset

```

import random def split_train_val_by_query(dataset, split=0.7): """Split dataset by queries.""" query_ids = list(dataset.queries.keys()) query_ids_shuffled = random.sample(query_ids, len(query_ids)) split_idx = int(len(query_ids) * split) train_query_ids = query_ids_shuffled[:split_idx] eval_query_ids = query_ids_shuffled[split_idx:] train_queries = {qid: dataset.queries[qid] for qid in train_query_ids} eval_queries = {qid: dataset.queries[qid] for qid in eval_query_ids} train_rel_docs = { qid: dataset.relevant_docs[qid] for qid in train_query_ids } eval_rel_docs = {qid: dataset.relevant_docs[qid] for qid in eval_query_ids} train_dataset = EmbeddingQAFinetuneDataset( queries=train_queries, corpus=dataset.corpus, relevant_docs=train_rel_docs, ) eval_dataset = EmbeddingQAFinetuneDataset( queries=eval_queries, corpus=dataset.corpus, relevant_docs=eval_rel_docs, ) return train_dataset, eval_dataset
In [ ]:
Copied!
```
train_dataset, eval_dataset = split_train_val_by_query(dataset, split=0.7)

```

train_dataset, eval_dataset = split_train_val_by_query(dataset, split=0.7)
## Fine-tuning Embeddings¶
In this section we try to fine-tune embeddings.
In [ ]:
Copied!
```
# generate embeddings dataset
from llama_index.finetuning import SentenceTransformersFinetuneEngine

```

# generate embeddings dataset from llama_index.finetuning import SentenceTransformersFinetuneEngine
In [ ]:
Copied!
```
finetune_engine = SentenceTransformersFinetuneEngine(
    train_dataset,
    model_id="BAAI/bge-small-en",
    model_output_path="test_model3",
    val_dataset=eval_dataset,
    epochs=30,  # can set to higher (haven't tested)
)

```

finetune_engine = SentenceTransformersFinetuneEngine( train_dataset, model_id="BAAI/bge-small-en", model_output_path="test_model3", val_dataset=eval_dataset, epochs=30, # can set to higher (haven't tested) )
In [ ]:
Copied!
```
finetune_engine.finetune()

```

finetune_engine.finetune()
In [ ]:
Copied!
```
ft_embed_model = finetune_engine.get_finetuned_model()

```

ft_embed_model = finetune_engine.get_finetuned_model()
In [ ]:
Copied!
```
ft_embed_model

```

ft_embed_model
Out[ ]:
```
HuggingFaceEmbedding(model_name='test_model3', embed_batch_size=10, callback_manager=<llama_index.callbacks.base.CallbackManager object at 0x2f5ccd210>, tokenizer_name='test_model3', max_length=512, pooling='cls', normalize='True', query_instruction=None, text_instruction=None, cache_folder=None)
```

## Run Evaluations¶
In this section we evaluate the quality of our fine-tuned embedding model vs. our base model in selecting the right choice.
We plug both into our `EmbeddingSelector` abstraction.
We also compare against a base `LLMSingleSelector` using GPT-4.
In [ ]:
Copied!
```
# define baseline embedding model
from llama_index.core.embeddings import resolve_embed_model

base_embed_model = resolve_embed_model("local:BAAI/bge-small-en")

```

# define baseline embedding model from llama_index.core.embeddings import resolve_embed_model base_embed_model = resolve_embed_model("local:BAAI/bge-small-en")
In [ ]:
Copied!
```
from llama_index.core.selectors import (
    EmbeddingSingleSelector,
    LLMSingleSelector,
)

ft_selector = EmbeddingSingleSelector.from_defaults(embed_model=ft_embed_model)
base_selector = EmbeddingSingleSelector.from_defaults(
    embed_model=base_embed_model
)

```

from llama_index.core.selectors import ( EmbeddingSingleSelector, LLMSingleSelector, ) ft_selector = EmbeddingSingleSelector.from_defaults(embed_model=ft_embed_model) base_selector = EmbeddingSingleSelector.from_defaults( embed_model=base_embed_model )
In [ ]:
Copied!
```
import numpy as np


def run_evals(eval_dataset, selector, choices, choice_to_id_dict):
    # we just measure accuracy
    eval_pairs = eval_dataset.query_docid_pairs
    matches = []
    for query, relevant_doc_ids in tqdm(eval_pairs):
        result = selector.select(choices, query)
        # assume single selection for now
        pred_doc_id = choice_to_id_dict[result.inds[0]]
        gt_doc_id = relevant_doc_ids[0]
        matches.append(gt_doc_id == pred_doc_id)
    return np.array(matches)

```

import numpy as np def run_evals(eval_dataset, selector, choices, choice_to_id_dict): # we just measure accuracy eval_pairs = eval_dataset.query_docid_pairs matches = [] for query, relevant_doc_ids in tqdm(eval_pairs): result = selector.select(choices, query) # assume single selection for now pred_doc_id = choice_to_id_dict[result.inds[0]] gt_doc_id = relevant_doc_ids[0] matches.append(gt_doc_id == pred_doc_id) return np.array(matches)
In [ ]:
Copied!
```
ft_matches = run_evals(eval_dataset, ft_selector, choices, choice_to_id_dict)

```

ft_matches = run_evals(eval_dataset, ft_selector, choices, choice_to_id_dict)
In [ ]:
Copied!
```
np.mean(ft_matches)

```

np.mean(ft_matches)
Out[ ]:
```
0.994413407821229
```

In [ ]:
Copied!
```
base_matches = run_evals(
    eval_dataset, base_selector, choices, choice_to_id_dict
)

```

base_matches = run_evals( eval_dataset, base_selector, choices, choice_to_id_dict )
In [ ]:
Copied!
```
np.mean(base_matches)

```

np.mean(base_matches)
Out[ ]:
```
0.12849162011173185
```

In [ ]:
Copied!
```
# also try LLM
from llama_index.llms.openai import OpenAI

eval_llm = OpenAI(model="gpt-3.5-turbo")

llm_selector = LLMSingleSelector.from_defaults(
    llm=eval_llm,
)

```

# also try LLM from llama_index.llms.openai import OpenAI eval_llm = OpenAI(model="gpt-3.5-turbo") llm_selector = LLMSingleSelector.from_defaults( llm=eval_llm, )
In [ ]:
Copied!
```
llm_matches = run_evals(eval_dataset, llm_selector, choices, choice_to_id_dict)

```

llm_matches = run_evals(eval_dataset, llm_selector, choices, choice_to_id_dict)
In [ ]:
Copied!
```
np.mean(llm_matches)

```

np.mean(llm_matches)
Out[ ]:
```
0.659217877094972
```

In [ ]:
Copied!
```
import pandas as pd

eval_df = pd.DataFrame(
    {
        "Base embedding model": np.mean(base_matches),
        "GPT-3.5": np.mean(llm_matches),
        "Fine-tuned embedding model": np.mean(ft_matches),
    },
    index=["Match Rate"],
)
display(eval_df)

```

import pandas as pd eval_df = pd.DataFrame( { "Base embedding model": np.mean(base_matches), "GPT-3.5": np.mean(llm_matches), "Fine-tuned embedding model": np.mean(ft_matches), }, index=["Match Rate"], ) display(eval_df)
| Base embedding model | GPT-3.5 | Fine-tuned embedding model  
---|---|---|---  
Match Rate | 0.128492 | 0.659218 | 0.994413  
## Plug into Router¶
We plug this into our `RouterQueryEngine` as an `EmbeddingSelector` (by default, an `LLMSingleSelector` is used in our router query engine).
In [ ]:
Copied!
```
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core import SummaryIndex
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool

# define indexes/tools for wikipedia entries
tools = []
for idx, wiki_title in enumerate(tqdm(wiki_titles)):
    doc_id_vector = f"{wiki_title}_vector"
    doc_id_summary = f"{wiki_title}_summary"

    vector_index = VectorStoreIndex.from_documents(city_docs[wiki_title])
    summary_index = SummaryIndex.from_documents(city_docs[wiki_title])
    vector_tool = QueryEngineTool.from_defaults(
        query_engine=vector_index.as_query_engine(),
        description=city_descs_dict[doc_id_vector],
    )
    summary_tool = QueryEngineTool.from_defaults(
        query_engine=summary_index.as_query_engine(),
        description=city_descs_dict[doc_id_summary],
    )
    tools.extend([vector_tool, summary_tool])

```

from llama_index.core.query_engine import RouterQueryEngine from llama_index.core import SummaryIndex from llama_index.core import VectorStoreIndex from llama_index.core.tools import QueryEngineTool # define indexes/tools for wikipedia entries tools = [] for idx, wiki_title in enumerate(tqdm(wiki_titles)): doc_id_vector = f"{wiki_title}_vector" doc_id_summary = f"{wiki_title}_summary" vector_index = VectorStoreIndex.from_documents(city_docs[wiki_title]) summary_index = SummaryIndex.from_documents(city_docs[wiki_title]) vector_tool = QueryEngineTool.from_defaults( query_engine=vector_index.as_query_engine(), description=city_descs_dict[doc_id_vector], ) summary_tool = QueryEngineTool.from_defaults( query_engine=summary_index.as_query_engine(), description=city_descs_dict[doc_id_summary], ) tools.extend([vector_tool, summary_tool])
```
  0%|          | 0/8 [00:00<?, ?it/s]
```

In [ ]:
Copied!
```
router_query_engine = RouterQueryEngine.from_defaults(
    selector=ft_selector.from_defaults(), query_engine_tools=tools
)

```

router_query_engine = RouterQueryEngine.from_defaults( selector=ft_selector.from_defaults(), query_engine_tools=tools )
In [ ]:
Copied!
```
response = router_query_engine.query(
    "Tell me more about the sports teams in Toronto"
)

```

response = router_query_engine.query( "Tell me more about the sports teams in Toronto" )
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
Toronto is home to several professional sports teams. In hockey, there is the Toronto Maple Leafs, one of the NHL's Original Six clubs, and the Toronto Marlies of the American Hockey League. The city also has a rich history of hockey championships, with the Maple Leafs winning 13 Stanley Cup titles and the Toronto Marlboros and St. Michael's College School-based Ontario Hockey League teams winning a combined 12 Memorial Cup titles.

In baseball, Toronto is represented by the Toronto Blue Jays, who have won two World Series titles. The Blue Jays play their home games at the Rogers Centre. 

In basketball, there is the Toronto Raptors, who entered the NBA in 1995 and have achieved success in recent years, including winning their first NBA title in 2019. The Raptors play their home games at Scotiabank Arena.

In Canadian football, there is the Toronto Argonauts, which was founded in 1873 and has won 18 Grey Cup Canadian championship titles. The Argonauts play their home games at BMO Field.

In soccer, there is the Toronto FC, who have won seven Canadian Championship titles and the MLS Cup in 2017. They share BMO Field with the Toronto Argonauts.

Other sports teams in Toronto include the Toronto Rock in the National Lacrosse League, the Toronto Wolfpack in rugby league, the Toronto Rush in ultimate disc, and the Toronto Six in the National Women's Hockey League.

Toronto has also hosted various sporting events, such as the Canadian Open tennis tournament, the Toronto Waterfront Marathon, the Grand Prix of Toronto car race, and the Pan American Games in 2015. Additionally, Toronto was named as one of the host cities for the 2026 FIFA World Cup.

```

In [ ]:
Copied!
```
response.source_nodes[0].get_content()

```

response.source_nodes[0].get_content()
Out[ ]:
```
"=== Professional sports ===\nToronto is home to the Toronto Maple Leafs, one of the NHL's Original Six clubs, and has also served as home to the Hockey Hall of Fame since 1958. The city had a rich history of hockey championships. Along with the Maple Leafs' 13 Stanley Cup titles, the Toronto Marlboros and St. Michael's College School-based Ontario Hockey League teams, combined, have won a record 12 Memorial Cup titles. The Toronto Marlies of the American Hockey League also play in Toronto at Coca-Cola Coliseum and are the farm team for the Maple Leafs. The Toronto Six, the first Canadian franchise in the National Women's Hockey League, began play with the 2020–21 season.\nThe city is home to the Toronto Blue Jays MLB baseball team. The team has won two World Series titles (1992, 1993). The Blue Jays play their home games at the Rogers Centre in the downtown core. Toronto has a long history of minor-league professional baseball dating back to the 1800s, culminating in the Toronto Maple Leafs baseball team, whose owner first proposed an MLB team for Toronto.The Toronto Raptors basketball team entered the NBA in 1995, and have since earned eleven playoff spots and five Atlantic Division titles in 24 seasons. They won their first NBA title in 2019. The Raptors are the only NBA team with their own television channel, NBA TV Canada. They play their home games at Scotiabank Arena, which is shared with the Maple Leafs. In 2016, Toronto hosted the 65th NBA All-Star game, the first to be held outside the United States.\nThe city is represented in Canadian football by the CFL's Toronto Argonauts, which was founded in 1873. The club has won 18 Grey Cup Canadian championship titles. The club's home games are played at BMO Field.\n\nToronto is represented in soccer by the Toronto FC MLS team, who have won seven Canadian Championship titles, as well as the MLS Cup in 2017 and the Supporters' Shield for best regular season record, also in 2017. They share BMO Field with the Toronto Argonauts. Toronto has a high level of participation in soccer across the city at several smaller stadiums and fields. Toronto FC had entered the league as an expansion team in 2007.The Toronto Rock is the city's National Lacrosse League team. They won five National Lacrosse League Cup titles in seven years in the late 1990s and the first decade of the 21st century, appearing in an NLL-record five straight championship games from 1999 to 2003, and are first all-time in the number of Champion's Cups won. The Rock formerly shared the Scotiabank Arena with the Maple Leafs and the Raptors, However, the Toronto Rock moved to the nearby city of Hamilton while retaining its Toronto name.\nThe Toronto Wolfpack became Canada's first professional rugby league team and the world's first transatlantic professional sports team when they began play in the Rugby Football League's League One competition in 2017. Due to COVID-19 restrictions on international travel the team withdrew from the Super League in 2020 with its future uncertain. The rugby club's ownership changed in 2021, now 'Team Wolfpack' will play in the newly formed North American Rugby League tournament.Toronto is home to the Toronto Rush, a semi-professional ultimate team that competes in the American Ultimate Disc League (AUDL). Ultimate (disc), in Canada, has its beginning roots in Toronto, with 3300 players competing annually in the Toronto Ultimate Club (League).Toronto has hosted several National Football League (NFL) exhibition games at the Rogers Centre. Ted Rogers leased the Buffalo Bills from Ralph Wilson for the purposes of having the Bills play eight home games in the city between 2008 and 2013.\n\n\n=== Collegiate sports ===\nThe University of Toronto in downtown Toronto was where the first recorded college football game was held in November 1861. Many post-secondary institutions in Toronto are members of U Sports or the Canadian Collegiate Athletic Association, the former for universities and the latter for colleges.\nToronto was home to the International Bowl, an NCAA sanctioned post-season college football game that pitted a Mid-American Conference team against a Big East Conference team. From 2007 to 2010, the game was played at Rogers Centre annually in January."
```

