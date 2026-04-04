![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Completion Prompts Customization¶
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

text_qa_template_str = """Context information is below:
<context>
{{ context_str }}
</context>

Using both the context information and also using your own knowledge, answer the question:
{{ query_str }}
"""
text_qa_template = RichPromptTemplate(text_qa_template_str)

refine_template_str = """New context information has been provided:
<context>
{{ context_msg }}
</context>

We also have an existing answer generated using previous context:
<existing_answer>
{{ existing_answer }}
</existing_answer>

Using the new context, either update the existing answer, or repeat it if the new context is not relevant, when answering this query:
{query_str}
"""
refine_template = RichPromptTemplate(refine_template_str)

```

from llama_index.core.prompts import RichPromptTemplate text_qa_template_str = """Context information is below:  {{ context_str }}  Using both the context information and also using your own knowledge, answer the question: {{ query_str }} """ text_qa_template = RichPromptTemplate(text_qa_template_str) refine_template_str = """New context information has been provided:  {{ context_msg }}  We also have an existing answer generated using previous context:  {{ existing_answer }}  Using the new context, either update the existing answer, or repeat it if the new context is not relevant, when answering this query: {query_str} """ refine_template = RichPromptTemplate(refine_template_str)
## Using the Prompts¶
Now, we use the prompts in an index query!
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
### Before Adding Templates¶
Lets see the default existing prompts:
In [ ]:
Copied!
```
query_engine.get_prompts()

```

query_engine.get_prompts()
Out[ ]:
```
{'response_synthesizer:text_qa_template': SelectorPromptTemplate(metadata={'prompt_type': <PromptType.QUESTION_ANSWER: 'text_qa'>}, template_vars=['context_str', 'query_str'], kwargs={}, output_parser=None, template_var_mappings={}, function_mappings={}, default_template=PromptTemplate(metadata={'prompt_type': <PromptType.QUESTION_ANSWER: 'text_qa'>}, template_vars=['context_str', 'query_str'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template='Context information is below.\n---------------------\n{context_str}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {query_str}\nAnswer: '), conditionals=[(<function is_chat_model at 0x10fd61ab0>, ChatPromptTemplate(metadata={'prompt_type': <PromptType.CUSTOM: 'custom'>}, template_vars=['context_str', 'query_str'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, message_templates=[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text="You are an expert Q&A system that is trusted around the world.\nAlways answer the query using the provided context information, and not prior knowledge.\nSome rules to follow:\n1. Never directly reference the given context in your answer.\n2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.")]), ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text='Context information is below.\n---------------------\n{context_str}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {query_str}\nAnswer: ')])]))]),
 'response_synthesizer:refine_template': SelectorPromptTemplate(metadata={'prompt_type': <PromptType.REFINE: 'refine'>}, template_vars=['query_str', 'existing_answer', 'context_msg'], kwargs={}, output_parser=None, template_var_mappings={}, function_mappings={}, default_template=PromptTemplate(metadata={'prompt_type': <PromptType.REFINE: 'refine'>}, template_vars=['query_str', 'existing_answer', 'context_msg'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template="The original query is as follows: {query_str}\nWe have provided an existing answer: {existing_answer}\nWe have the opportunity to refine the existing answer (only if needed) with some more context below.\n------------\n{context_msg}\n------------\nGiven the new context, refine the original answer to better answer the query. If the context isn't useful, return the original answer.\nRefined Answer: "), conditionals=[(<function is_chat_model at 0x10fd61ab0>, ChatPromptTemplate(metadata={'prompt_type': <PromptType.CUSTOM: 'custom'>}, template_vars=['context_msg', 'query_str', 'existing_answer'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, message_templates=[ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text="You are an expert Q&A system that strictly operates in two modes when refining existing answers:\n1. **Rewrite** an original answer using the new context.\n2. **Repeat** the original answer if the new context isn't useful.\nNever reference the original answer or context directly in your answer.\nWhen in doubt, just repeat the original answer.\nNew Context: {context_msg}\nQuery: {query_str}\nOriginal Answer: {existing_answer}\nNew Answer: ")])]))])}
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

### After Adding Templates¶
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
Joe Biden is an American politician and attorney who has served as the 46th president of the United States since January 20, 2021. He was born on November 20, 1942, in Scranton, Pennsylvania. Before his presidency, Biden had a long career in politics, including serving as a U.S. senator from Delaware from 1973 to 2009. He was also the vice president under President Barack Obama from 2009 to 2017.

Biden is a member of the Democratic Party and has been involved in various legislative efforts throughout his career, focusing on issues such as foreign policy, healthcare, and civil rights. His presidency has been marked by efforts to address the COVID-19 pandemic, economic recovery, climate change, and social justice issues.

```

