![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Accessing/Customizing Prompts within Higher-Level Modules¶
LlamaIndex contains a variety of higher-level modules (query engines, response synthesizers, retrievers, etc.), many of which make LLM calls + use prompt templates.
This guide shows how you can 1) access the set of prompts for any module (including nested) with `get_prompts`, and 2) update these prompts easily with `update_prompts`.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
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
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Set the default embedding model and LLM
Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")
Settings.llm = OpenAI(model="gpt-4o-mini")

```

from llama_index.core import Settings from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding # Set the default embedding model and LLM Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-small") Settings.llm = OpenAI(model="gpt-4o-mini")
## Setup: Load Data, Build Index, and Get Query Engine¶
Here we build a vector index over a toy dataset (PG's essay), and access the query engine.
The query engine is a simple RAG pipeline consisting of top-k retrieval + LLM synthesis.
Download Data
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

# load documents
documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

```

from llama_index.core import SimpleDirectoryReader # load documents documents = SimpleDirectoryReader("./data/paul_graham/").load_data()
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
query_engine = index.as_query_engine(response_mode="tree_summarize")

```

query_engine = index.as_query_engine(response_mode="tree_summarize")
In [ ]:
Copied!
```
from IPython.display import Markdown, display


# define prompt viewing function
def display_prompt_dict(prompts_dict):
    for k, p in prompts_dict.items():
        text_md = f"**Prompt Key**: {k}<br>" f"**Text:** <br>"
        display(Markdown(text_md))
        print(p.get_template())
        display(Markdown("<br><br>"))

```

from IPython.display import Markdown, display # define prompt viewing function def display_prompt_dict(prompts_dict): for k, p in prompts_dict.items(): text_md = f"**Prompt Key**: {k}  
" f"**Text:**   
" display(Markdown(text_md)) print(p.get_template()) display(Markdown("  
  
"))
## Accessing Prompts¶
Here we get the prompts from the query engine. Note that _all_ prompts are returned, including ones used in sub-modules in the query engine. This allows you to centralize a view of these prompts!
In [ ]:
Copied!
```
prompts_dict = query_engine.get_prompts()

```

prompts_dict = query_engine.get_prompts()
In [ ]:
Copied!
```
display_prompt_dict(prompts_dict)

```

display_prompt_dict(prompts_dict)
**Prompt Key** : response_synthesizer:summary_template  
**Text:**   

```
Context information from multiple sources is below.
---------------------
{context_str}
---------------------
Given the information from multiple sources and not prior knowledge, answer the query.
Query: {query_str}
Answer: 

```

  
  

#### Checking `get_prompts` on Response Synthesizer¶
You can also call `get_prompts` on the underlying response synthesizer, where you'll see the same list.
In [ ]:
Copied!
```
prompts_dict = query_engine.response_synthesizer.get_prompts()
display_prompt_dict(prompts_dict)

```

prompts_dict = query_engine.response_synthesizer.get_prompts() display_prompt_dict(prompts_dict)
**Prompt Key** : summary_template  
**Text:**   

```
Context information from multiple sources is below.
---------------------
{context_str}
---------------------
Given the information from multiple sources and not prior knowledge, answer the query.
Query: {query_str}
Answer: 

```

  
  

#### Checking `get_prompts` with a different response synthesis strategy¶
Here we try the default `compact` method.
We'll see that the set of templates used are different; a QA template and a refine template.
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine(response_mode="compact")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine(response_mode="compact")
In [ ]:
Copied!
```
prompts_dict = query_engine.get_prompts()
display_prompt_dict(prompts_dict)

```

prompts_dict = query_engine.get_prompts() display_prompt_dict(prompts_dict)
**Prompt Key** : response_synthesizer:text_qa_template  
**Text:**   

```
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: 

```

  
  

**Prompt Key** : response_synthesizer:refine_template  
**Text:**   

```
The original query is as follows: {query_str}
We have provided an existing answer: {existing_answer}
We have the opportunity to refine the existing answer (only if needed) with some more context below.
------------
{context_msg}
------------
Given the new context, refine the original answer to better answer the query. If the context isn't useful, return the original answer.
Refined Answer: 

```

  
  

#### Put into query engine, get response¶
In [ ]:
Copied!
```
response = query_engine.query("What did the author do growing up?")
print(str(response))

```

response = query_engine.query("What did the author do growing up?") print(str(response))
```
The author worked on writing and programming outside of school before college. They wrote short stories and tried writing programs on an IBM 1401 computer using an early version of Fortran. They later got a microcomputer and started programming on it, writing simple games and a word processor. They also mentioned their interest in philosophy and AI.

```

## Customize the prompt¶
You can also update/customize the prompts with the `update_prompts` function. Pass in arg values with the keys equal to the keys you see in the prompt dictionary.
Here we'll change the summary prompt to use Shakespeare.
In [ ]:
Copied!
```
from llama_index.core import PromptTemplate

# reset
query_engine = index.as_query_engine(response_mode="tree_summarize")

# shakespeare!
new_summary_tmpl_str = (
    "Context information is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query in the style of a Shakespeare play.\n"
    "Query: {query_str}\n"
    "Answer: "
)
new_summary_tmpl = PromptTemplate(new_summary_tmpl_str)

```

from llama_index.core import PromptTemplate # reset query_engine = index.as_query_engine(response_mode="tree_summarize") # shakespeare! new_summary_tmpl_str = ( "Context information is below.\n" "---------------------\n" "{context_str}\n" "---------------------\n" "Given the context information and not prior knowledge, " "answer the query in the style of a Shakespeare play.\n" "Query: {query_str}\n" "Answer: " ) new_summary_tmpl = PromptTemplate(new_summary_tmpl_str)
In [ ]:
Copied!
```
query_engine.update_prompts(
    {"response_synthesizer:summary_template": new_summary_tmpl}
)

```

query_engine.update_prompts( {"response_synthesizer:summary_template": new_summary_tmpl} )
In [ ]:
Copied!
```
prompts_dict = query_engine.get_prompts()

```

prompts_dict = query_engine.get_prompts()
In [ ]:
Copied!
```
display_prompt_dict(prompts_dict)

```

display_prompt_dict(prompts_dict)
**Prompt Key** : response_synthesizer:summary_template  
**Text:**   

```
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query in the style of a Shakespeare play.
Query: {query_str}
Answer: 

```

  
  

In [ ]:
Copied!
```
response = query_engine.query("What did the author do growing up?")
print(str(response))

```

response = query_engine.query("What did the author do growing up?") print(str(response))
## Accessing Prompts from Other Modules¶
Here we take a look at some other modules: query engines, routers/selectors, evaluators, and others.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import ReActAgent
from llama_index.core.selectors import LLMMultiSelector
from llama_index.core.evaluation import FaithfulnessEvaluator, DatasetGenerator
from llama_index.core.postprocessor import LLMRerank

```

from llama_index.core.agent.workflow import ReActAgent from llama_index.core.selectors import LLMMultiSelector from llama_index.core.evaluation import FaithfulnessEvaluator, DatasetGenerator from llama_index.core.postprocessor import LLMRerank
#### Analyze Prompts: ReActAgent¶
In [ ]:
Copied!
```
agent = ReActAgent(tools=[])

```

agent = ReActAgent(tools=[])
In [ ]:
Copied!
```
prompts_dict = agent.get_prompts()
display_prompt_dict(prompts_dict)

```

prompts_dict = agent.get_prompts() display_prompt_dict(prompts_dict)
**Prompt Key** : react_header  
**Text:**   

```
You are designed to help with a variety of tasks, from answering questions to providing summaries to other types of analyses.

## Tools

You have access to a wide variety of tools. You are responsible for using the tools in any sequence you deem appropriate to complete the task at hand.
This may require breaking the task into subtasks and using different tools to complete each subtask.

You have access to the following tools:
{tool_desc}


## Output Format

Please answer in the same language as the question and use the following format:

```
Thought: The current language of the user is: (user's language). I need to use a tool to help me answer the question.
Action: tool name (one of {tool_names}) if using a tool.
Action Input: the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world", "num_beams": 5}})
```

Please ALWAYS start with a Thought.

NEVER surround your response with markdown code markers. You may use code markers within your response if you need to.

Please use a valid JSON format for the Action Input. Do NOT do this {{'input': 'hello world', 'num_beams': 5}}.

If this format is used, the tool will respond in the following format:

```
Observation: tool response
```

You should keep repeating the above format till you have enough information to answer the question without using any more tools. At that point, you MUST respond in one of the following two formats:

```
Thought: I can answer without using any more tools. I'll use the user's language to answer
Answer: [your answer here (In the same language as the user's question)]

Thought: I cannot answer the question with the provided tools.
Answer: [your answer here (In the same language as the user's question)]
```

## Current Conversation

Below is the current conversation consisting of interleaving human and assistant messages.


```

  
  

#### Analyze Prompts: FLARE Query Engine¶
In [ ]:
Copied!
```
flare_query_engine = FLAREInstructQueryEngine(query_engine)

```

flare_query_engine = FLAREInstructQueryEngine(query_engine)
In [ ]:
Copied!
```
prompts_dict = flare_query_engine.get_prompts()
display_prompt_dict(prompts_dict)

```

prompts_dict = flare_query_engine.get_prompts() display_prompt_dict(prompts_dict)
**Prompt Key** : instruct_prompt  
**Text:**   

```
Skill 1. Use the Search API to look up relevant information by writing     "[Search(query)]" where "query" is the search query you want to look up.     For example:

Query: But what are the risks during production of nanomaterials?
Answer: [Search(What are some nanomaterial production risks?)]

Query: The colors on the flag of Ghana have the following meanings.
Answer: Red is for [Search(What is the meaning of Ghana's flag being red?)],     green for forests, and gold for mineral wealth.

Query: What did the author do during his time in college?
Answer: The author took classes in [Search(What classes did the author take in     college?)].



Skill 2. Solve more complex generation tasks by thinking step by step. For example:

Query: Give a summary of the author's life and career.
Answer: The author was born in 1990. Growing up, he [Search(What did the     author do during his childhood?)].

Query: Can you write a summary of the Great Gatsby.
Answer: The Great Gatsby is a novel written by F. Scott Fitzgerald. It is about     [Search(What is the Great Gatsby about?)].


Now given the following task, and the stub of an existing answer, generate the next portion of the answer. You may use the Search API "[Search(query)]" whenever possible.
If the answer is complete and no longer contains any "[Search(query)]" tags, write     "done" to finish the task.
Do not write "done" if the answer still contains "[Search(query)]" tags.
Do not make up answers. It is better to generate one "[Search(query)]" tag and stop generation
than to fill in the answer with made up information with no "[Search(query)]" tags
or multiple "[Search(query)]" tags that assume a structure in the answer.
Try to limit generation to one sentence if possible.


Query: {query_str}
Existing Answer: {existing_answer}
Answer: 

```

  
  

**Prompt Key** : query_engine:response_synthesizer:summary_template  
**Text:**   

```
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query in the style of a Shakespeare play.
Query: {query_str}
Answer: 

```

  
  

**Prompt Key** : lookahead_answer_inserter:answer_insert_prompt  
**Text:**   

```
An existing 'lookahead response' is given below. The lookahead response
contains `[Search(query)]` tags. Some queries have been executed and the
response retrieved. The queries and answers are also given below.
Also the previous response (the response before the lookahead response)
is given below.
Given the lookahead template, previous response, and also queries and answers,
please 'fill in' the lookahead template with the appropriate answers.

NOTE: Please make sure that the final response grammatically follows
the previous response + lookahead template. For example, if the previous
response is "New York City has a population of " and the lookahead
template is "[Search(What is the population of New York City?)]", then
the final response should be "8.4 million".

NOTE: the lookahead template may not be a complete sentence and may
contain trailing/leading commas, etc. Please preserve the original
formatting of the lookahead template if possible.

NOTE:

NOTE: the exception to the above rule is if the answer to a query
is equivalent to "I don't know" or "I don't have an answer". In this case,
modify the lookahead template to indicate that the answer is not known.

NOTE: the lookahead template may contain multiple `[Search(query)]` tags
    and only a subset of these queries have been executed.
    Do not replace the `[Search(query)]` tags that have not been executed.

Previous Response:


Lookahead Template:
Red is for [Search(What is the meaning of Ghana's     flag being red?)], green for forests, and gold for mineral wealth.

Query-Answer Pairs:
Query: What is the meaning of Ghana's flag being red?
Answer: The red represents the blood of those who died in the country's struggle     for independence

Filled in Answers:
Red is for the blood of those who died in the country's struggle for independence,     green for forests, and gold for mineral wealth.

Previous Response:
One of the largest cities in the world

Lookahead Template:
, the city contains a population of [Search(What is the population     of New York City?)]

Query-Answer Pairs:
Query: What is the population of New York City?
Answer: The population of New York City is 8.4 million

Synthesized Response:
, the city contains a population of 8.4 million

Previous Response:
the city contains a population of

Lookahead Template:
[Search(What is the population of New York City?)]

Query-Answer Pairs:
Query: What is the population of New York City?
Answer: The population of New York City is 8.4 million

Synthesized Response:
8.4 million

Previous Response:
{prev_response}

Lookahead Template:
{lookahead_response}

Query-Answer Pairs:
{query_answer_pairs}

Synthesized Response:


```

  
  

#### Analyze Prompts: LLMMultiSelector¶
In [ ]:
Copied!
```
from llama_index.core.selectors import LLMSingleSelector

selector = LLMSingleSelector.from_defaults()

```

from llama_index.core.selectors import LLMSingleSelector selector = LLMSingleSelector.from_defaults()
In [ ]:
Copied!
```
prompts_dict = selector.get_prompts()
display_prompt_dict(prompts_dict)

```

prompts_dict = selector.get_prompts() display_prompt_dict(prompts_dict)
**Prompt Key** : prompt  
**Text:**   

```
Some choices are given below. It is provided in a numbered list (1 to {num_choices}), where each item in the list corresponds to a summary.
---------------------
{context_list}
---------------------
Using only the choices above and not prior knowledge, return the choice that is most relevant to the question: '{query_str}'


```

  
  

#### Analyze Prompts: FaithfulnessEvaluator¶
In [ ]:
Copied!
```
evaluator = FaithfulnessEvaluator()

```

evaluator = FaithfulnessEvaluator()
In [ ]:
Copied!
```
prompts_dict = evaluator.get_prompts()
display_prompt_dict(prompts_dict)

```

prompts_dict = evaluator.get_prompts() display_prompt_dict(prompts_dict)
**Prompt Key** : eval_template  
**Text:**   

```
Please tell if a given piece of information is supported by the context.
You need to answer with either YES or NO.
Answer YES if any of the context supports the information, even if most of the context is unrelated. Some examples are provided below. 

Information: Apple pie is generally double-crusted.
Context: An apple pie is a fruit pie in which the principal filling ingredient is apples. 
Apple pie is often served with whipped cream, ice cream ('apple pie à la mode'), custard or cheddar cheese.
It is generally double-crusted, with pastry both above and below the filling; the upper crust may be solid or latticed (woven of crosswise strips).
Answer: YES
Information: Apple pies tastes bad.
Context: An apple pie is a fruit pie in which the principal filling ingredient is apples. 
Apple pie is often served with whipped cream, ice cream ('apple pie à la mode'), custard or cheddar cheese.
It is generally double-crusted, with pastry both above and below the filling; the upper crust may be solid or latticed (woven of crosswise strips).
Answer: NO
Information: {query_str}
Context: {context_str}
Answer: 

```

  
  

**Prompt Key** : refine_template  
**Text:**   

```
We want to understand if the following information is present in the context information: {query_str}
We have provided an existing YES/NO answer: {existing_answer}
We have the opportunity to refine the existing answer (only if needed) with some more context below.
------------
{context_msg}
------------
If the existing answer was already YES, still answer YES. If the information is present in the new context, answer YES. Otherwise answer NO.


```

  
  

#### Analyze Prompts: DatasetGenerator¶
In [ ]:
Copied!
```
dataset_generator = DatasetGenerator.from_documents(documents)

```

dataset_generator = DatasetGenerator.from_documents(documents)
In [ ]:
Copied!
```
prompts_dict = dataset_generator.get_prompts()
display_prompt_dict(prompts_dict)

```

prompts_dict = dataset_generator.get_prompts() display_prompt_dict(prompts_dict)
**Prompt Key** : text_question_template  
**Text:**   

```
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge.
generate only questions based on the below query.
{query_str}


```

  
  

**Prompt Key** : text_qa_template  
**Text:**   

```
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: 

```

  
  

#### Analyze Prompts: LLMRerank¶
In [ ]:
Copied!
```
llm_rerank = LLMRerank()

```

llm_rerank = LLMRerank()
In [ ]:
Copied!
```
prompts_dict = dataset_generator.get_prompts()
display_prompt_dict(prompts_dict)

```

prompts_dict = dataset_generator.get_prompts() display_prompt_dict(prompts_dict)
**Prompt Key** : text_question_template  
**Text:**   

```
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge.
generate only questions based on the below query.
{query_str}


```

  
  

**Prompt Key** : text_qa_template  
**Text:**   

```
Context information is below.
---------------------
{context_str}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query_str}
Answer: 

```

  
  

