![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# JSON Query Engine¶
The JSON query engine is useful for querying JSON documents that conform to a JSON schema.
This JSON schema is then used in the context of a prompt to convert a natural language query into a structured JSON Path query. This JSON Path query is then used to retrieve data to answer the given question.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
# First, install the jsonpath-ng package which is used by default to parse & execute the JSONPath queries.
!pip install jsonpath-ng

```

# First, install the jsonpath-ng package which is used by default to parse & execute the JSONPath queries. !pip install jsonpath-ng
```
Requirement already satisfied: jsonpath-ng in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (1.5.3)
Requirement already satisfied: ply in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from jsonpath-ng) (3.11)
Requirement already satisfied: six in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from jsonpath-ng) (1.16.0)
Requirement already satisfied: decorator in /Users/loganmarkewich/llama_index/llama-index/lib/python3.9/site-packages (from jsonpath-ng) (5.1.1)
WARNING: You are using pip version 21.2.4; however, version 23.2.1 is available.
You should consider upgrading via the '/Users/loganmarkewich/llama_index/llama-index/bin/python3 -m pip install --upgrade pip' command.

```

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
import os
import openai

os.environ["OPENAI_API_KEY"] = "YOUR_KEY_HERE"

```

import os import openai os.environ["OPENAI_API_KEY"] = "YOUR_KEY_HERE"
In [ ]:
Copied!
```
from IPython.display import Markdown, display

```

from IPython.display import Markdown, display
### Let's start on a Toy JSON¶
Very simple JSON object containing data from a blog post site with user comments.
We will also provide a JSON schema (which we were able to generate by giving ChatGPT a sample of the JSON).
#### Advice¶
Do make sure that you've provided a helpful `"description"` value for each of the fields in your JSON schema.
As you can see in the given example, the description for the `"username"` field mentions that usernames are lowercased. You'll see that this ends up being helpful for the LLM in producing the correct JSON path query.
In [ ]:
Copied!
```
# Test on some sample data
json_value = {
    "blogPosts": [
        {
            "id": 1,
            "title": "First blog post",
            "content": "This is my first blog post",
        },
        {
            "id": 2,
            "title": "Second blog post",
            "content": "This is my second blog post",
        },
    ],
    "comments": [
        {
            "id": 1,
            "content": "Nice post!",
            "username": "jerry",
            "blogPostId": 1,
        },
        {
            "id": 2,
            "content": "Interesting thoughts",
            "username": "simon",
            "blogPostId": 2,
        },
        {
            "id": 3,
            "content": "Loved reading this!",
            "username": "simon",
            "blogPostId": 2,
        },
    ],
}

# JSON Schema object that the above JSON value conforms to
json_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "Schema for a very simple blog post app",
    "type": "object",
    "properties": {
        "blogPosts": {
            "description": "List of blog posts",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "description": "Unique identifier for the blog post",
                        "type": "integer",
                    },
                    "title": {
                        "description": "Title of the blog post",
                        "type": "string",
                    },
                    "content": {
                        "description": "Content of the blog post",
                        "type": "string",
                    },
                },
                "required": ["id", "title", "content"],
            },
        },
        "comments": {
            "description": "List of comments on blog posts",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "description": "Unique identifier for the comment",
                        "type": "integer",
                    },
                    "content": {
                        "description": "Content of the comment",
                        "type": "string",
                    },
                    "username": {
                        "description": (
                            "Username of the commenter (lowercased)"
                        ),
                        "type": "string",
                    },
                    "blogPostId": {
                        "description": (
                            "Identifier for the blog post to which the comment"
                            " belongs"
                        ),
                        "type": "integer",
                    },
                },
                "required": ["id", "content", "username", "blogPostId"],
            },
        },
    },
    "required": ["blogPosts", "comments"],
}

```

# Test on some sample data json_value = { "blogPosts": [ { "id": 1, "title": "First blog post", "content": "This is my first blog post", }, { "id": 2, "title": "Second blog post", "content": "This is my second blog post", }, ], "comments": [ { "id": 1, "content": "Nice post!", "username": "jerry", "blogPostId": 1, }, { "id": 2, "content": "Interesting thoughts", "username": "simon", "blogPostId": 2, }, { "id": 3, "content": "Loved reading this!", "username": "simon", "blogPostId": 2, }, ], } # JSON Schema object that the above JSON value conforms to json_schema = { "$schema": "http://json-schema.org/draft-07/schema#", "description": "Schema for a very simple blog post app", "type": "object", "properties": { "blogPosts": { "description": "List of blog posts", "type": "array", "items": { "type": "object", "properties": { "id": { "description": "Unique identifier for the blog post", "type": "integer", }, "title": { "description": "Title of the blog post", "type": "string", }, "content": { "description": "Content of the blog post", "type": "string", }, }, "required": ["id", "title", "content"], }, }, "comments": { "description": "List of comments on blog posts", "type": "array", "items": { "type": "object", "properties": { "id": { "description": "Unique identifier for the comment", "type": "integer", }, "content": { "description": "Content of the comment", "type": "string", }, "username": { "description": ( "Username of the commenter (lowercased)" ), "type": "string", }, "blogPostId": { "description": ( "Identifier for the blog post to which the comment" " belongs" ), "type": "integer", }, }, "required": ["id", "content", "username", "blogPostId"], }, }, }, "required": ["blogPosts", "comments"], }
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.indices.struct_store import JSONQueryEngine

llm = OpenAI(model="gpt-4")

nl_query_engine = JSONQueryEngine(
    json_value=json_value,
    json_schema=json_schema,
    llm=llm,
)
raw_query_engine = JSONQueryEngine(
    json_value=json_value,
    json_schema=json_schema,
    llm=llm,
    synthesize_response=False,
)

```

from llama_index.llms.openai import OpenAI from llama_index.core.indices.struct_store import JSONQueryEngine llm = OpenAI(model="gpt-4") nl_query_engine = JSONQueryEngine( json_value=json_value, json_schema=json_schema, llm=llm, ) raw_query_engine = JSONQueryEngine( json_value=json_value, json_schema=json_schema, llm=llm, synthesize_response=False, )
In [ ]:
Copied!
```
nl_response = nl_query_engine.query(
    "What comments has Jerry been writing?",
)
raw_response = raw_query_engine.query(
    "What comments has Jerry been writing?",
)

```

nl_response = nl_query_engine.query( "What comments has Jerry been writing?", ) raw_response = raw_query_engine.query( "What comments has Jerry been writing?", )
In [ ]:
Copied!
```
display(
    Markdown(f"<h1>Natural language Response</h1><br><b>{nl_response}</b>")
)
display(Markdown(f"<h1>Raw JSON Response</h1><br><b>{raw_response}</b>"))

```

display( Markdown(f"
# Natural language Response
  
**{nl_response}** ") ) display(Markdown(f"
# Raw JSON Response
  
**{raw_response}** "))
# Natural language Response
  
**Jerry has written the comment "Nice post!".**
# Raw JSON Response
  
**["Nice post!"]**
In [ ]:
Copied!
```
# get the json path query string. Same would apply to raw_response
print(nl_response.metadata["json_path_response_str"])

```

# get the json path query string. Same would apply to raw_response print(nl_response.metadata["json_path_response_str"])
```
$.comments[?(@.username=='jerry')].content

```

