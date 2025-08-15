![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Advanced Prompt Techniques (Variable Mappings, Functions)¶
In this notebook we show some advanced prompt techniques. These features allow you to define more custom/expressive prompts, re-use existing ones, and also express certain operations in fewer lines of code.
We show the following features:
  1. Partial formatting
  2. Prompt template variable mappings
  3. Prompt function mappings
  4. Dynamic few-shot examples


In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
## 1. Partial Formatting¶
Partial formatting (`partial_format`) allows you to partially format a prompt, filling in some variables while leaving others to be filled in later.
This is a nice convenience function so you don't have to maintain all the required prompt variables all the way down to `format`, you can partially format as they come in.
This will create a copy of the prompt template.
In [ ]:
Copied!
```
from llama_index.core.prompts import RichPromptTemplate

qa_prompt_tmpl_str = """\
Context information is below.
---------------------
{{ context_str }}
---------------------
Given the context information and not prior knowledge, answer the query.
Please write the answer in the style of {{ tone_name }}
Query: {{ query_str }}
Answer: \
"""

prompt_tmpl = RichPromptTemplate(qa_prompt_tmpl_str)

```

from llama_index.core.prompts import RichPromptTemplate qa_prompt_tmpl_str = """\ Context information is below. --------------------- {{ context_str }} --------------------- Given the context information and not prior knowledge, answer the query. Please write the answer in the style of {{ tone_name }} Query: {{ query_str }} Answer: \ """ prompt_tmpl = RichPromptTemplate(qa_prompt_tmpl_str)
In [ ]:
Copied!
```
partial_prompt_tmpl = prompt_tmpl.partial_format(tone_name="Shakespeare")

```

partial_prompt_tmpl = prompt_tmpl.partial_format(tone_name="Shakespeare")
In [ ]:
Copied!
```
partial_prompt_tmpl.kwargs

```

partial_prompt_tmpl.kwargs
Out[ ]:
```
{'tone_name': 'Shakespeare'}
```

In [ ]:
Copied!
```
fmt_prompt = partial_prompt_tmpl.format(
    context_str="In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters",
    query_str="How many params does llama 2 have",
)
print(fmt_prompt)

```

fmt_prompt = partial_prompt_tmpl.format( context_str="In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters", query_str="How many params does llama 2 have", ) print(fmt_prompt)
```
Context information is below.
---------------------
In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters
---------------------
Given the context information and not prior knowledge, answer the query.
Please write the answer in the style of Shakespeare
Query: How many params does llama 2 have
Answer: 

```

We can also use `format_messages` to format the prompt into `ChatMessage` objects.
In [ ]:
Copied!
```
fmt_prompt = partial_prompt_tmpl.format_messages(
    context_str="In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters",
    query_str="How many params does llama 2 have",
)
print(fmt_prompt)

```

fmt_prompt = partial_prompt_tmpl.format_messages( context_str="In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters", query_str="How many params does llama 2 have", ) print(fmt_prompt)
```
[ChatMessage(role=<MessageRole.USER: 'user'>, additional_kwargs={}, blocks=[TextBlock(block_type='text', text='Context information is below.'), TextBlock(block_type='text', text='---------------------'), TextBlock(block_type='text', text='In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters'), TextBlock(block_type='text', text='---------------------'), TextBlock(block_type='text', text='Given the context information and not prior knowledge, answer the query.'), TextBlock(block_type='text', text='Please write the answer in the style of Shakespeare'), TextBlock(block_type='text', text='Query: How many params does llama 2 have'), TextBlock(block_type='text', text='Answer:')])]

```

## 2. Prompt Template Variable Mappings¶
Template var mappings allow you to specify a mapping from the "expected" prompt keys (e.g. `context_str` and `query_str` for response synthesis), with the keys actually in your template.
This allows you re-use your existing string templates without having to annoyingly change out the template variables.
In [ ]:
Copied!
```
from llama_index.core.prompts import RichPromptTemplate

# NOTE: here notice we use `my_context` and `my_query` as template variables
qa_prompt_tmpl_str = """\
Context information is below.
---------------------
{{ my_context }}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {{ my_query }}
Answer: \
"""

template_var_mappings = {"context_str": "my_context", "query_str": "my_query"}

prompt_tmpl = RichPromptTemplate(
    qa_prompt_tmpl_str, template_var_mappings=template_var_mappings
)

```

from llama_index.core.prompts import RichPromptTemplate # NOTE: here notice we use `my_context` and `my_query` as template variables qa_prompt_tmpl_str = """\ Context information is below. --------------------- {{ my_context }} --------------------- Given the context information and not prior knowledge, answer the query. Query: {{ my_query }} Answer: \ """ template_var_mappings = {"context_str": "my_context", "query_str": "my_query"} prompt_tmpl = RichPromptTemplate( qa_prompt_tmpl_str, template_var_mappings=template_var_mappings )
In [ ]:
Copied!
```
fmt_prompt = prompt_tmpl.format(
    context_str="In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters",
    query_str="How many params does llama 2 have",
)
print(fmt_prompt)

```

fmt_prompt = prompt_tmpl.format( context_str="In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters", query_str="How many params does llama 2 have", ) print(fmt_prompt)
```
Context information is below.
---------------------
In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters
---------------------
Given the context information and not prior knowledge, answer the query.
Query: How many params does llama 2 have
Answer: 

```

### 3. Prompt Function Mappings¶
You can also pass in functions as template variables instead of fixed values.
This allows you to dynamically inject certain values, dependent on other values, during query-time.
Here are some basic examples. We show more advanced examples (e.g. few-shot examples) in our Prompt Engineering for RAG guide.
In [ ]:
Copied!
```
from llama_index.core.prompts import RichPromptTemplate

qa_prompt_tmpl_str = """\
Context information is below.
---------------------
{{ context_str }}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {{ query_str }}
Answer: \
"""


def format_context_fn(**kwargs):
    # format context with bullet points
    context_list = kwargs["context_str"].split("\n\n")
    fmtted_context = "\n\n".join([f"- {c}" for c in context_list])
    return fmtted_context


prompt_tmpl = RichPromptTemplate(
    qa_prompt_tmpl_str, function_mappings={"context_str": format_context_fn}
)

```

from llama_index.core.prompts import RichPromptTemplate qa_prompt_tmpl_str = """\ Context information is below. --------------------- {{ context_str }} --------------------- Given the context information and not prior knowledge, answer the query. Query: {{ query_str }} Answer: \ """ def format_context_fn(**kwargs): # format context with bullet points context_list = kwargs["context_str"].split("\n\n") fmtted_context = "\n\n".join([f"- {c}" for c in context_list]) return fmtted_context prompt_tmpl = RichPromptTemplate( qa_prompt_tmpl_str, function_mappings={"context_str": format_context_fn} )
In [ ]:
Copied!
```
context_str = """\
In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters.

Our fine-tuned LLMs, called Llama 2-Chat, are optimized for dialogue use cases.

Our models outperform open-source chat models on most benchmarks we tested, and based on our human evaluations for helpfulness and safety, may be a suitable substitute for closed-source models.
"""

fmt_prompt = prompt_tmpl.format(
    context_str=context_str, query_str="How many params does llama 2 have"
)
print(fmt_prompt)

```

context_str = """\ In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters. Our fine-tuned LLMs, called Llama 2-Chat, are optimized for dialogue use cases. Our models outperform open-source chat models on most benchmarks we tested, and based on our human evaluations for helpfulness and safety, may be a suitable substitute for closed-source models. """ fmt_prompt = prompt_tmpl.format( context_str=context_str, query_str="How many params does llama 2 have" ) print(fmt_prompt)
```
Context information is below.
---------------------
- In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters.

- Our fine-tuned LLMs, called Llama 2-Chat, are optimized for dialogue use cases.

- Our models outperform open-source chat models on most benchmarks we tested, and based on our human evaluations for helpfulness and safety, may be a suitable substitute for closed-source models.

---------------------
Given the context information and not prior knowledge, answer the query.
Query: How many params does llama 2 have
Answer: 

```

### 4. Dynamic few-shot examples¶
Using the function mappings, you can also dynamically inject few-shot examples based on other prompt variables.
Here's an example that uses a vector store to dynamically inject few-shot text-to-sql examples based on the query.
First, lets define a text-to-sql prompt template.
In [ ]:
Copied!
```
text_to_sql_prompt_tmpl_str = """\
You are a SQL expert. You are given a natural language query, and your job is to convert it into a SQL query.

Here are some examples of how you should convert natural language to SQL:
<examples>
{{ examples }}
</examples>

Now it's your turn.

Query: {{ query_str }}
SQL: 
"""

```

text_to_sql_prompt_tmpl_str = """\ You are a SQL expert. You are given a natural language query, and your job is to convert it into a SQL query. Here are some examples of how you should convert natural language to SQL:  {{ examples }}  Now it's your turn. Query: {{ query_str }} SQL: """
Given this prompt template, lets define and index some few-shot text-to-sql examples.
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
from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Set global default LLM and embed model
Settings.llm = OpenAI(model="gpt-4o-mini")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# Setup few-shot examples
example_nodes = [
    TextNode(
        text="Query: How many params does llama 2 have?\nSQL: SELECT COUNT(*) FROM llama_2_params;"
    ),
    TextNode(
        text="Query: How many layers does llama 2 have?\nSQL: SELECT COUNT(*) FROM llama_2_layers;"
    ),
]

# Create index
index = VectorStoreIndex(nodes=example_nodes)

# Create retriever
retriever = index.as_retriever(similarity_top_k=1)

```

from llama_index.core import Settings, VectorStoreIndex from llama_index.core.schema import TextNode from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding # Set global default LLM and embed model Settings.llm = OpenAI(model="gpt-4o-mini") Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small") # Setup few-shot examples example_nodes = [ TextNode( text="Query: How many params does llama 2 have?\nSQL: SELECT COUNT(*) FROM llama_2_params;" ), TextNode( text="Query: How many layers does llama 2 have?\nSQL: SELECT COUNT(*) FROM llama_2_layers;" ), ] # Create index index = VectorStoreIndex(nodes=example_nodes) # Create retriever retriever = index.as_retriever(similarity_top_k=1)
With our retriever, we can create our prompt template with function mappings to dynamically inject few-shot examples based on the query.
In [ ]:
Copied!
```
from llama_index.core.prompts import RichPromptTemplate


def get_examples_fn(**kwargs):
    query = kwargs["query_str"]
    examples = retriever.retrieve(query)
    return "\n\n".join(node.text for node in examples)


prompt_tmpl = RichPromptTemplate(
    text_to_sql_prompt_tmpl_str,
    function_mappings={"examples": get_examples_fn},
)

```

from llama_index.core.prompts import RichPromptTemplate def get_examples_fn(**kwargs): query = kwargs["query_str"] examples = retriever.retrieve(query) return "\n\n".join(node.text for node in examples) prompt_tmpl = RichPromptTemplate( text_to_sql_prompt_tmpl_str, function_mappings={"examples": get_examples_fn}, )
In [ ]:
Copied!
```
prompt = prompt_tmpl.format(
    query_str="What are the number of parameters in the llama 2 model?"
)
print(prompt)

```

prompt = prompt_tmpl.format( query_str="What are the number of parameters in the llama 2 model?" ) print(prompt)
```
You are a SQL expert. You are given a natural language query, and your job is to convert it into a SQL query.

Here are some examples of how you should convert natural language to SQL:
<examples>
Query: How many params does llama 2 have?
SQL: SELECT COUNT(*) FROM llama_2_params;
</examples>

Now it's your turn.

Query: What are the number of parameters in the llama 2 model?
SQL: 

```

In [ ]:
Copied!
```
response = Settings.llm.complete(prompt)
print(response.text)

```

response = Settings.llm.complete(prompt) print(response.text)
```
SELECT COUNT(*) FROM llama_2_params;

```

