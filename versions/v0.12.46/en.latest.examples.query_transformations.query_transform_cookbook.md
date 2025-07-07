# Query Transform Cookbook¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
A user query can be transformed and decomposed in many ways before being executed as part of a RAG query engine, agent, or any other pipeline.
In this guide we show you different ways to transform, decompose queries, and find the set of relevant tools. Each technique might be applicable for different use cases!
For naming purposes, we define the underlying pipeline as a "tool". Here are the different query transformations:
  1. **Routing** : Keep the query, but identify the relevant subset of tools that the query applies to. Output those tools as the relevant choices.
  2. **Query-Rewriting** : Keep the tools, but rewrite the query in a variety of different ways to execute against the same tools.
  3. **Sub-Questions** : Decompose queries into multiple sub-questions over different tools (identified by their metadata).
  4. **ReAct Agent Tool Picking** : Given the initial query, identify 1) the tool to pick, and 2) the query to execute on the tool.


The goal of this guide is to show you how to use these query transforms as **modular** components. Of course, each of these components plug into a bigger system (e.g. the sub-question generator is a part of our `SubQuestionQueryEngine`) - and the guides for each of these are linked below.
Take a look and let us know your thoughts!
In [ ]:
Copied!
```
%pip install llama-index-question-gen-openai
%pip install llama-index-llms-openai

```

%pip install llama-index-question-gen-openai %pip install llama-index-llms-openai
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
## Routing¶
In this example, we show how a query can be used to select the set of relevant tool choices.
We use our `selector` abstraction to pick the relevant tool(s) - it can be a single tool, or a multiple tool depending on the abstraction.
We have four selectors: combination of (LLM or function calling) x (single selection or multi-selection)
In [ ]:
Copied!
```
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core.selectors import (
    PydanticMultiSelector,
    PydanticSingleSelector,
)

```

from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector from llama_index.core.selectors import ( PydanticMultiSelector, PydanticSingleSelector, )
In [ ]:
Copied!
```
# pydantic selectors feed in pydantic objects to a function calling API
# single selector (pydantic, function calling)
# selector = PydanticSingleSelector.from_defaults()

# multi selector (pydantic, function calling)
# selector = PydanticMultiSelector.from_defaults()

# LLM selectors use text completion endpoints
# single selector (LLM)
# selector = LLMSingleSelector.from_defaults()
# multi selector (LLM)
selector = LLMMultiSelector.from_defaults()

```

# pydantic selectors feed in pydantic objects to a function calling API # single selector (pydantic, function calling) # selector = PydanticSingleSelector.from_defaults() # multi selector (pydantic, function calling) # selector = PydanticMultiSelector.from_defaults() # LLM selectors use text completion endpoints # single selector (LLM) # selector = LLMSingleSelector.from_defaults() # multi selector (LLM) selector = LLMMultiSelector.from_defaults()
In [ ]:
Copied!
```
from llama_index.core.tools import ToolMetadata

tool_choices = [
    ToolMetadata(
        name="covid_nyt",
        description=("This tool contains a NYT news article about COVID-19"),
    ),
    ToolMetadata(
        name="covid_wiki",
        description=("This tool contains the Wikipedia page about COVID-19"),
    ),
    ToolMetadata(
        name="covid_tesla",
        description=("This tool contains the Wikipedia page about apples"),
    ),
]

```

from llama_index.core.tools import ToolMetadata tool_choices = [ ToolMetadata( name="covid_nyt", description=("This tool contains a NYT news article about COVID-19"), ), ToolMetadata( name="covid_wiki", description=("This tool contains the Wikipedia page about COVID-19"), ), ToolMetadata( name="covid_tesla", description=("This tool contains the Wikipedia page about apples"), ), ]
In [ ]:
Copied!
```
display_prompt_dict(selector.get_prompts())

```

display_prompt_dict(selector.get_prompts())
**Prompt Key** : prompt  
**Text:**   

```
Some choices are given below. It is provided in a numbered list (1 to {num_choices}), where each item in the list corresponds to a summary.
---------------------
{context_list}
---------------------
Using only the choices above and not prior knowledge, return the top choices (no more than {max_outputs}, but only select what is needed) that are most relevant to the question: '{query_str}'


The output should be ONLY JSON formatted as a JSON instance.

Here is an example:
[
    {{
        choice: 1,
        reason: "<insert reason for choice>"
    }},
    ...
]


```

  
  

In [ ]:
Copied!
```
selector_result = selector.select(
    tool_choices, query="Tell me more about COVID-19"
)

```

selector_result = selector.select( tool_choices, query="Tell me more about COVID-19" )
In [ ]:
Copied!
```
selector_result.selections

```

selector_result.selections
Out[ ]:
```
[SingleSelection(index=0, reason='This tool contains a NYT news article about COVID-19'),
 SingleSelection(index=1, reason='This tool contains the Wikipedia page about COVID-19')]
```

Learn more about our routing abstractions in our dedicated Router page.
## Query Rewriting¶
In this section, we show you how to rewrite queries into multiple queries. You can then execute all these queries against a retriever.
This is a key step in advanced retrieval techniques. By doing query rewriting, you can generate multiple queries for [ensemble retrieval] and [fusion], leading to higher-quality retrieved results.
Unlike the sub-question generator, this is just a prompt call, and exists independently of tools.
### Query Rewriting (Custom)¶
Here we show you how to use a prompt to generate multiple queries, using our LLM and prompt abstractions.
In [ ]:
Copied!
```
from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI

query_gen_str = """\
You are a helpful assistant that generates multiple search queries based on a \
single input query. Generate {num_queries} search queries, one on each line, \
related to the following input query:
Query: {query}
Queries:
"""
query_gen_prompt = PromptTemplate(query_gen_str)

llm = OpenAI(model="gpt-3.5-turbo")


def generate_queries(query: str, llm, num_queries: int = 4):
    response = llm.predict(
        query_gen_prompt, num_queries=num_queries, query=query
    )
    # assume LLM proper put each query on a newline
    queries = response.split("\n")
    queries_str = "\n".join(queries)
    print(f"Generated queries:\n{queries_str}")
    return queries

```

from llama_index.core import PromptTemplate from llama_index.llms.openai import OpenAI query_gen_str = """\ You are a helpful assistant that generates multiple search queries based on a \ single input query. Generate {num_queries} search queries, one on each line, \ related to the following input query: Query: {query} Queries: """ query_gen_prompt = PromptTemplate(query_gen_str) llm = OpenAI(model="gpt-3.5-turbo") def generate_queries(query: str, llm, num_queries: int = 4): response = llm.predict( query_gen_prompt, num_queries=num_queries, query=query ) # assume LLM proper put each query on a newline queries = response.split("\n") queries_str = "\n".join(queries) print(f"Generated queries:\n{queries_str}") return queries
In [ ]:
Copied!
```
queries = generate_queries("What happened at Interleaf and Viaweb?", llm)

```

queries = generate_queries("What happened at Interleaf and Viaweb?", llm)
```
Generated queries:
1. What were the major events or milestones in the history of Interleaf and Viaweb?
2. Who were the founders and key figures involved in the development of Interleaf and Viaweb?
3. What were the products or services offered by Interleaf and Viaweb?
4. Are there any notable success stories or failures associated with Interleaf and Viaweb?

```

In [ ]:
Copied!
```
queries

```

queries
Out[ ]:
```
['1. What were the major events or milestones in the history of Interleaf and Viaweb?',
 '2. Who were the founders and key figures involved in the development of Interleaf and Viaweb?',
 '3. What were the products or services offered by Interleaf and Viaweb?',
 '4. Are there any notable success stories or failures associated with Interleaf and Viaweb?']
```

For more details about an e2e implementation with a retriever, check out our guides on our fusion retriever:
  * Module Guide
  * Build a Fusion Retriever from Scratch


### Query Rewriting (using QueryTransform)¶
In this section we show you how to do query transformations using our QueryTransform class.
In [ ]:
Copied!
```
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.llms.openai import OpenAI

```

from llama_index.core.indices.query.query_transform import HyDEQueryTransform from llama_index.llms.openai import OpenAI
In [ ]:
Copied!
```
hyde = HyDEQueryTransform(include_original=True)
llm = OpenAI(model="gpt-3.5-turbo")

query_bundle = hyde.run("What is Bel?")

```

hyde = HyDEQueryTransform(include_original=True) llm = OpenAI(model="gpt-3.5-turbo") query_bundle = hyde.run("What is Bel?")
This generates a query bundle that contains the original query, but also `custom_embedding_strs` representing the queries that should be embedded.
In [ ]:
Copied!
```
new_query.custom_embedding_strs

```

new_query.custom_embedding_strs
Out[ ]:
```
['Bel is a term that has multiple meanings and can be interpreted in various ways depending on the context. In ancient Mesopotamian mythology, Bel was a prominent deity and one of the chief gods of the Babylonian pantheon. He was often associated with the sky, storms, and fertility. Bel was considered to be the father of the gods and held great power and authority over the other deities.\n\nIn addition to its mythological significance, Bel is also a title that was used to address rulers and leaders in ancient Babylon. It was a term of respect and reverence, similar to the modern-day title of "king" or "emperor." The title of Bel was bestowed upon those who held significant political and military power, and it symbolized their authority and dominion over their subjects.\n\nFurthermore, Bel is also a common given name in various cultures around the world. It can be found in different forms and variations, such as Belinda, Isabel, or Bella. As a personal name, Bel often carries connotations of beauty, grace, and strength.\n\nIn summary, Bel can refer to a powerful deity in ancient Mesopotamian mythology, a title of respect for rulers and leaders, or a personal name with positive attributes. The meaning of Bel can vary depending on the specific context in which it is used.',
 'What is Bel?']
```

## Sub-Questions¶
Given a set of tools and a user query, decide both the 1) set of sub-questions to generate, and 2) the tools that each sub-question should run over.
We run through an example using the `OpenAIQuestionGenerator`, which depends on function calling, and also the `LLMQuestionGenerator`, which depends on prompting.
In [ ]:
Copied!
```
from llama_index.core.question_gen import LLMQuestionGenerator
from llama_index.question_gen.openai import OpenAIQuestionGenerator
from llama_index.llms.openai import OpenAI

```

from llama_index.core.question_gen import LLMQuestionGenerator from llama_index.question_gen.openai import OpenAIQuestionGenerator from llama_index.llms.openai import OpenAI
In [ ]:
Copied!
```
llm = OpenAI()
question_gen = OpenAIQuestionGenerator.from_defaults(llm=llm)

```

llm = OpenAI() question_gen = OpenAIQuestionGenerator.from_defaults(llm=llm)
In [ ]:
Copied!
```
display_prompt_dict(question_gen.get_prompts())

```

display_prompt_dict(question_gen.get_prompts())
**Prompt Key** : question_gen_prompt  
**Text:**   

```
You are a world class state of the art agent.

You have access to multiple tools, each representing a different data source or API.
Each of the tools has a name and a description, formatted as a JSON dictionary.
The keys of the dictionary are the names of the tools and the values are the descriptions.
Your purpose is to help answer a complex user question by generating a list of sub questions that can be answered by the tools.

These are the guidelines you consider when completing your task:
* Be as specific as possible
* The sub questions should be relevant to the user question
* The sub questions should be answerable by the tools provided
* You can generate multiple sub questions for each tool
* Tools must be specified by their name, not their description
* You don't need to use a tool if you don't think it's relevant

Output the list of sub questions by calling the SubQuestionList function.

## Tools
```json
{tools_str}
```

## User Question
{query_str}


```

  
  

In [ ]:
Copied!
```
from llama_index.core.tools import ToolMetadata

tool_choices = [
    ToolMetadata(
        name="uber_2021_10k",
        description=(
            "Provides information about Uber financials for year 2021"
        ),
    ),
    ToolMetadata(
        name="lyft_2021_10k",
        description=(
            "Provides information about Lyft financials for year 2021"
        ),
    ),
]

```

from llama_index.core.tools import ToolMetadata tool_choices = [ ToolMetadata( name="uber_2021_10k", description=( "Provides information about Uber financials for year 2021" ), ), ToolMetadata( name="lyft_2021_10k", description=( "Provides information about Lyft financials for year 2021" ), ), ]
In [ ]:
Copied!
```
from llama_index.core import QueryBundle

query_str = "Compare and contrast Uber and Lyft"
choices = question_gen.generate(tool_choices, QueryBundle(query_str=query_str))

```

from llama_index.core import QueryBundle query_str = "Compare and contrast Uber and Lyft" choices = question_gen.generate(tool_choices, QueryBundle(query_str=query_str))
The outputs are `SubQuestion` Pydantic objects.
In [ ]:
Copied!
```
choices

```

choices
Out[ ]:
```
[SubQuestion(sub_question='What are the financials of Uber for the year 2021?', tool_name='uber_2021_10k'),
 SubQuestion(sub_question='What are the financials of Lyft for the year 2021?', tool_name='lyft_2021_10k')]
```

For details on how to plug this into your RAG pipeline in a more packaged fashion, check out our SubQuestionQueryEngine.
## Query Transformation with ReAct Prompt¶
ReAct is a popular framework for agents, and here we show how the core ReAct prompt can be used to transform queries.
We use the `ReActChatFormatter` to get the set of input messages for the LLM.
In [ ]:
Copied!
```
from llama_index.core.agent import ReActChatFormatter
from llama_index.core.agent.react.output_parser import ReActOutputParser
from llama_index.core.tools import FunctionTool
from llama_index.core.llms import ChatMessage

```

from llama_index.core.agent import ReActChatFormatter from llama_index.core.agent.react.output_parser import ReActOutputParser from llama_index.core.tools import FunctionTool from llama_index.core.llms import ChatMessage
In [ ]:
Copied!
```
def execute_sql(sql: str) -> str:
    """Given a SQL input string, execute it."""
    # NOTE: This is a mock function
    return f"Executed {sql}"


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


tool1 = FunctionTool.from_defaults(fn=execute_sql)
tool2 = FunctionTool.from_defaults(fn=add)
tools = [tool1, tool2]

```

def execute_sql(sql: str) -> str: """Given a SQL input string, execute it.""" # NOTE: This is a mock function return f"Executed {sql}" def add(a: int, b: int) -> int: """Add two numbers.""" return a + b tool1 = FunctionTool.from_defaults(fn=execute_sql) tool2 = FunctionTool.from_defaults(fn=add) tools = [tool1, tool2]
Here we get the input prompt messages to pass to the LLM. Take a look!
In [ ]:
Copied!
```
chat_formatter = ReActChatFormatter()
output_parser = ReActOutputParser()
input_msgs = chat_formatter.format(
    tools,
    [
        ChatMessage(
            content="Can you find the top three rows from the table named `revenue_years`",
            role="user",
        )
    ],
)
input_msgs

```

chat_formatter = ReActChatFormatter() output_parser = ReActOutputParser() input_msgs = chat_formatter.format( tools, [ ChatMessage( content="Can you find the top three rows from the table named `revenue_years`", role="user", ) ], ) input_msgs
Out[ ]:
```
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content='\nYou are designed to help with a variety of tasks, from answering questions     to providing summaries to other types of analyses.\n\n## Tools\nYou have access to a wide variety of tools. You are responsible for using\nthe tools in any sequence you deem appropriate to complete the task at hand.\nThis may require breaking the task into subtasks and using different tools\nto complete each subtask.\n\nYou have access to the following tools:\n> Tool Name: execute_sql\nTool Description: execute_sql(sql: str) -> str\nGiven a SQL input string, execute it.\nTool Args: {\'title\': \'execute_sql\', \'type\': \'object\', \'properties\': {\'sql\': {\'title\': \'Sql\', \'type\': \'string\'}}, \'required\': [\'sql\']}\n\n> Tool Name: add\nTool Description: add(a: int, b: int) -> int\nAdd two numbers.\nTool Args: {\'title\': \'add\', \'type\': \'object\', \'properties\': {\'a\': {\'title\': \'A\', \'type\': \'integer\'}, \'b\': {\'title\': \'B\', \'type\': \'integer\'}}, \'required\': [\'a\', \'b\']}\n\n\n## Output Format\nTo answer the question, please use the following format.\n\n```\nThought: I need to use a tool to help me answer the question.\nAction: tool name (one of execute_sql, add) if using a tool.\nAction Input: the input to the tool, in a JSON format representing the kwargs (e.g. {"input": "hello world", "num_beams": 5})\n```\n\nPlease ALWAYS start with a Thought.\n\nPlease use a valid JSON format for the Action Input. Do NOT do this {\'input\': \'hello world\', \'num_beams\': 5}.\n\nIf this format is used, the user will respond in the following format:\n\n```\nObservation: tool response\n```\n\nYou should keep repeating the above format until you have enough information\nto answer the question without using any more tools. At that point, you MUST respond\nin the one of the following two formats:\n\n```\nThought: I can answer without using any more tools.\nAnswer: [your answer here]\n```\n\n```\nThought: I cannot answer the question with the provided tools.\nAnswer: Sorry, I cannot answer your query.\n```\n\n## Current Conversation\nBelow is the current conversation consisting of interleaving human and assistant messages.\n\n', additional_kwargs={}),
 ChatMessage(role=<MessageRole.USER: 'user'>, content='Can you find the top three rows from the table named `revenue_years`', additional_kwargs={})]
```

Next we get the output from the model.
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4-1106-preview")

```

llm = OpenAI(model="gpt-4-1106-preview")
In [ ]:
Copied!
```
response = llm.chat(input_msgs)

```

response = llm.chat(input_msgs)
Finally we use our ReActOutputParser to parse the content into a structured output, and analyze the action inputs.
In [ ]:
Copied!
```
reasoning_step = output_parser.parse(response.message.content)

```

reasoning_step = output_parser.parse(response.message.content)
In [ ]:
Copied!
```
reasoning_step.action_input

```

reasoning_step.action_input
Out[ ]:
```
{'sql': 'SELECT * FROM revenue_years ORDER BY revenue DESC LIMIT 3'}
```

