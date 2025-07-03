![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Codestral from MistralAI Cookbook¶
MistralAI released codestral-latest - a code model.
Codestral is a new code model from mistralai tailored for code generation, fluent in over 80 programming languages. It simplifies coding tasks by completing functions, writing tests, and filling in code snippets, enhancing developer efficiency and reducing errors. Codestral operates through a unified API endpoint, making it a versatile tool for software development.
This cookbook showcases how to use the `codestral-latest` model with llama-index. It guides you through using the Codestral fill-in-the-middle and instruct endpoints.
### Setup LLM¶
In [ ]:
Copied!
```
import os

os.environ["MISTRAL_API_KEY"] = "<YOUR MISTRAL API KEY>"

from llama_index.llms.mistralai import MistralAI

llm = MistralAI(model="codestral-latest", temperature=0.1)

```

import os os.environ["MISTRAL_API_KEY"] = "" from llama_index.llms.mistralai import MistralAI llm = MistralAI(model="codestral-latest", temperature=0.1)
### Instruct mode usage¶
#### Write a function for fibonacci¶
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [ChatMessage(role="user", content="Write a function for fibonacci")]

response = llm.chat(messages)

print(response)

```

from llama_index.core.llms import ChatMessage messages = [ChatMessage(role="user", content="Write a function for fibonacci")] response = llm.chat(messages) print(response)
```
assistant: Sure, here is a simple Python function that calculates the nth number in the Fibonacci sequence:

```python
def fibonacci(n):
    if n <= 0:
        print("Input should be positive integer.")
    elif n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        a, b = 0, 1
        for i in range(2, n):
            a, b = b, a + b
        return b
```

You can use this function to find the nth number in the Fibonacci sequence by calling `fibonacci(n)`, where `n` is the position of the number you want to find. For example, `fibonacci(10)` will return the 10th number in the Fibonacci sequence.

```

#### Write a function to build RAG pipeline using LlamaIndex.¶
Note: The output is mostly accurate, but it is based on an older LlamaIndex package.
In [ ]:
Copied!
```
messages = [
    ChatMessage(
        role="user",
        content="Write a function to build RAG pipeline using LlamaIndex.",
    )
]

response = llm.chat(messages)

print(response)

```

messages = [ ChatMessage( role="user", content="Write a function to build RAG pipeline using LlamaIndex.", ) ] response = llm.chat(messages) print(response)
```
assistant: Sure, I can help you with that. Here's a basic example of how you can build a Retrieval Augmented Generation (RAG) pipeline using LlamaIndex. This example assumes that you have a list of documents.

```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader

def build_rag_pipeline(documents_path):
    # Load documents
    documents = SimpleDirectoryReader(documents_path).load_data()

    # Create index
    index = VectorStoreIndex.from_documents(documents)

    # Create query engine
    query_engine = index.as_query_engine()

    return query_engine

# Usage
query_engine = build_rag_pipeline("path_to_your_documents")
response = query_engine.query("Your query here")
print(response)
```

In this code:

1. We first import the necessary classes from LlamaIndex.
2. We define a function `build_rag_pipeline` that takes a path to a directory of documents as input.
3. We load the documents using `SimpleDirectoryReader`.
4. We create an index from the documents using `VectorStoreIndex.from_documents`.
5. We create a query engine from the index using `index.as_query_engine`.
6. Finally, we return the query engine.

You can use the query engine to ask questions about the documents. The query engine will use the index to retrieve relevant documents and then generate a response based on those documents.

```

### Fill-in-the-middle¶
This feature allows users to set a starting point with a prompt and an optional ending with a suffix and stop. The Codestral model then generates the intervening code, perfect for tasks requiring specific code generation.
#### Fill the code with start and end of the code.¶
In [ ]:
Copied!
```
prompt = "def multiply("
suffix = "return a*b"

response = llm.fill_in_middle(prompt, suffix)

print(
    f"""
{prompt}
{response.text}
{suffix}
"""
)

```

prompt = "def multiply(" suffix = "return a*b" response = llm.fill_in_middle(prompt, suffix) print( f""" {prompt} {response.text} {suffix} """ )
```
def multiply(
a, b):
  """
  This function multiplies two numbers
  """
  
return a*b


```

#### Fill the code with start, end of the code and stop tokens.¶
In [ ]:
Copied!
```
prompt = "def multiply(a,"
suffix = ""
stop = ["\n\n\n"]

response = llm.fill_in_middle(prompt, suffix, stop)

print(
    f"""
{prompt}
{response.text}
{suffix}
"""
)

```

prompt = "def multiply(a," suffix = "" stop = ["\n\n\n"] response = llm.fill_in_middle(prompt, suffix, stop) print( f""" {prompt} {response.text} {suffix} """ )
```
def multiply(a,
 b):

    return a * b

# test the function
print(multiply(2, 3))  # should print 6
print(multiply(-1, 5))  # should print -5
print(multiply(0, 99))  # should print 0

# we can also test the function with large numbers
print(multiply(123456789, 987654321))  # should print 121932631132635269

# the function should also work with floating point numbers
print(multiply(3.14, 2.71))  # should print approximately 8.5392

# the function should also work with negative floating point numbers
print(multiply(-3.14, 2.71))  # should print approximately -8.5392

# the function should also work with mixed types (integer and floating point)
print(multiply(2, 3.14))  # should print approximately 6.28



```

