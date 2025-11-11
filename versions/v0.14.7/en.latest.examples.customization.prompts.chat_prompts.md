![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Chat Prompts Customization¶
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
## Prompt Setup¶
Lets customize them to always answer, even if the context is not helpful!
Using `RichPromptTemplate`, we can define Jinja-formatted prompts.
In [ ]:
Copied!
```
from llama_index.core.prompts import RichPromptTemplate

chat_text_qa_prompt_str = """
{% chat role="system" %}
Always answer the question, even if the context isn't helpful.
{% endchat %}

{% chat role="user" %}
The following is some retrieved context:

<context>
{{ context_str }}
</context>

Using the context, answer the provided question:
{{ query_str }}
{% endchat %}
"""
text_qa_template = RichPromptTemplate(chat_text_qa_prompt_str)

# Refine Prompt
chat_refine_prompt_str = """
{% chat role="system" %}
Always answer the question, even if the context isn't helpful.
{% endchat %}

{% chat role="user" %}
The following is some new retrieved context:

<context>
{{ context_msg }}
</context>

And here is an existing answer to the query:
<existing_answer>
{{ existing_answer }}
</existing_answer>

Using both the new retrieved context and the existing answer, either update or repeat the existing answer to this query:
{{ query_str }}
{% endchat %}
"""
refine_template = RichPromptTemplate(chat_refine_prompt_str)

```

from llama_index.core.prompts import RichPromptTemplate chat_text_qa_prompt_str = """ {% chat role="system" %} Always answer the question, even if the context isn't helpful. {% endchat %} {% chat role="user" %} The following is some retrieved context:  {{ context_str }}  Using the context, answer the provided question: {{ query_str }} {% endchat %} """ text_qa_template = RichPromptTemplate(chat_text_qa_prompt_str) # Refine Prompt chat_refine_prompt_str = """ {% chat role="system" %} Always answer the question, even if the context isn't helpful. {% endchat %} {% chat role="user" %} The following is some new retrieved context:  {{ context_msg }}  And here is an existing answer to the query:  {{ existing_answer }}  Using both the new retrieved context and the existing answer, either update or repeat the existing answer to this query: {{ query_str }} {% endchat %} """ refine_template = RichPromptTemplate(chat_refine_prompt_str)
## Using the Prompts¶
Now, we use the prompts in an index query!
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-proj-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-proj-..."
In [ ]:
Copied!
```
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")

```

from llama_index.core import Settings from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding Settings.llm = OpenAI(model="gpt-4o-mini") Settings.embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")
#### Download Data¶
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
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham/").load_data()

index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham/").load_data() index = VectorStoreIndex.from_documents(documents) query_engine = index.as_query_engine()
### Before Customizing Templates¶
Lets see the default existing prompts:
In [ ]:
Copied!
```
query_engine.get_prompts()

```

query_engine.get_prompts()
Out[ ]:
```
{'response_synthesizer:text_qa_template': SelectorPromptTemplate(metadata={'prompt_type': <PromptType.QUESTION_ANSWER: 'text_qa'>}, template_vars=['context_str', 'query_str'], kwargs={}, output_parser=None, template_var_mappings={}, function_mappings={}, default_template=PromptTemplate(metadata={'prompt_type': <PromptType.QUESTION_ANSWER: 'text_qa'>}, template_vars=['context_str', 'query_str'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template='Context information is below.\n---------------------\n{context_str}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {query_str}\nAnswer: '), conditionals=[(<function is_chat_model at 0x1062d16c0>, ChatPromptTemplate(metadata={'prompt_type': <PromptType.CUSTOM: 'custom'>}, template_vars=['context_str', 'query_str'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, message_templates=[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text="You are an expert Q&A system that is trusted around the world.\nAlways answer the query using the provided context information, and not prior knowledge.\nSome rules to follow:\n1. Never directly reference the given context in your answer.\n2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.")]), ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text='Context information is below.\n---------------------\n{context_str}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {query_str}\nAnswer: ')])]))]),
 'response_synthesizer:refine_template': SelectorPromptTemplate(metadata={'prompt_type': <PromptType.REFINE: 'refine'>}, template_vars=['query_str', 'existing_answer', 'context_msg'], kwargs={}, output_parser=None, template_var_mappings={}, function_mappings={}, default_template=PromptTemplate(metadata={'prompt_type': <PromptType.REFINE: 'refine'>}, template_vars=['query_str', 'existing_answer', 'context_msg'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template="The original query is as follows: {query_str}\nWe have provided an existing answer: {existing_answer}\nWe have the opportunity to refine the existing answer (only if needed) with some more context below.\n------------\n{context_msg}\n------------\nGiven the new context, refine the original answer to better answer the query. If the context isn't useful, return the original answer.\nRefined Answer: "), conditionals=[(<function is_chat_model at 0x1062d16c0>, ChatPromptTemplate(metadata={'prompt_type': <PromptType.CUSTOM: 'custom'>}, template_vars=['context_msg', 'query_str', 'existing_answer'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, message_templates=[ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text="You are an expert Q&A system that strictly operates in two modes when refining existing answers:\n1. **Rewrite** an original answer using the new context.\n2. **Repeat** the original answer if the new context isn't useful.\nNever reference the original answer or context directly in your answer.\nWhen in doubt, just repeat the original answer.\nNew Context: {context_msg}\nQuery: {query_str}\nOriginal Answer: {existing_answer}\nNew Answer: ")])]))])}
```

And how do they respond when asking about unrelated concepts?
In [ ]:
Copied!
```
print(query_engine.query("Who is Joe Biden?"))

```

print(query_engine.query("Who is Joe Biden?"))
```
The provided information does not contain any details about Joe Biden.

```

### After Customizing Templates¶
Now, we can update the templates and observe the change in response!
In [ ]:
Copied!
```
query_engine.update_prompts(
    {
        "response_synthesizer:text_qa_template": text_qa_template,
        "response_synthesizer:refine_template": refine_template,
    }
)

```

query_engine.update_prompts( { "response_synthesizer:text_qa_template": text_qa_template, "response_synthesizer:refine_template": refine_template, } )
In [ ]:
Copied!
```
print(query_engine.query("Who is Joe Biden?"))

```

print(query_engine.query("Who is Joe Biden?"))
```
Joe Biden is the 46th President of the United States, having taken office on January 20, 2021. He previously served as Vice President under President Barack Obama from 2009 to 2017 and has had a long career in politics, including serving as a U.S. Senator from Delaware from 1973 to 2009. Biden is a member of the Democratic Party and has focused on issues such as healthcare, climate change, and economic recovery during his presidency.

```

