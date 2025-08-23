![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Building a Router from Scratch¶
In this tutorial, we show you how to build an LLM-powered router module that can route a user query to submodules.
Routers are a simple but effective form of automated decision making that can allow you to perform dynamic retrieval/querying over your data.
In LlamaIndex, this is abstracted away with our Router Modules.
To build a router, we'll walk through the following steps:
  * Crafting an initial prompt to select a set of choices
  * Enforcing structured output (for text completion endpoints)
  * Try integrating with a native function calling endpoint.


And then we'll plug this into a RAG pipeline to dynamically make decisions on QA vs. summarization.
## 1. Setup a Basic Router Prompt¶
At its core, a router is a module that takes in a set of choices. Given a user query, it "selects" a relevant choice.
For simplicity, we'll start with the choices as a set of strings.
In [ ]:
Copied!
```
%pip install llama-index-readers-file pymupdf
%pip install llama-index-program-openai
%pip install llama-index-llms-openai

```

%pip install llama-index-readers-file pymupdf %pip install llama-index-program-openai %pip install llama-index-llms-openai
In [ ]:
Copied!
```
from llama_index.core import PromptTemplate

choices = [
    "Useful for questions related to apples",
    "Useful for questions related to oranges",
]


def get_choice_str(choices):
    choices_str = "\n\n".join(
        [f"{idx+1}. {c}" for idx, c in enumerate(choices)]
    )
    return choices_str


choices_str = get_choice_str(choices)

```

from llama_index.core import PromptTemplate choices = [ "Useful for questions related to apples", "Useful for questions related to oranges", ] def get_choice_str(choices): choices_str = "\n\n".join( [f"{idx+1}. {c}" for idx, c in enumerate(choices)] ) return choices_str choices_str = get_choice_str(choices)
In [ ]:
Copied!
```
router_prompt0 = PromptTemplate(
    "Some choices are given below. It is provided in a numbered list (1 to"
    " {num_choices}), where each item in the list corresponds to a"
    " summary.\n---------------------\n{context_list}\n---------------------\nUsing"
    " only the choices above and not prior knowledge, return the top choices"
    " (no more than {max_outputs}, but only select what is needed) that are"
    " most relevant to the question: '{query_str}'\n"
)

```

router_prompt0 = PromptTemplate( "Some choices are given below. It is provided in a numbered list (1 to" " {num_choices}), where each item in the list corresponds to a" " summary.\n---------------------\n{context_list}\n---------------------\nUsing" " only the choices above and not prior knowledge, return the top choices" " (no more than {max_outputs}, but only select what is needed) that are" " most relevant to the question: '{query_str}'\n" )
Let's try this prompt on a set of toy questions and see what the output brings.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-3.5-turbo")

```

from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-3.5-turbo")
In [ ]:
Copied!
```
def get_formatted_prompt(query_str):
    fmt_prompt = router_prompt0.format(
        num_choices=len(choices),
        max_outputs=2,
        context_list=choices_str,
        query_str=query_str,
    )
    return fmt_prompt

```

def get_formatted_prompt(query_str): fmt_prompt = router_prompt0.format( num_choices=len(choices), max_outputs=2, context_list=choices_str, query_str=query_str, ) return fmt_prompt
In [ ]:
Copied!
```
query_str = "Can you tell me more about the amount of Vitamin C in apples"
fmt_prompt = get_formatted_prompt(query_str)
response = llm.complete(fmt_prompt)

```

query_str = "Can you tell me more about the amount of Vitamin C in apples" fmt_prompt = get_formatted_prompt(query_str) response = llm.complete(fmt_prompt)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
1. Useful for questions related to apples

```

In [ ]:
Copied!
```
query_str = "What are the health benefits of eating orange peels?"
fmt_prompt = get_formatted_prompt(query_str)
response = llm.complete(fmt_prompt)

```

query_str = "What are the health benefits of eating orange peels?" fmt_prompt = get_formatted_prompt(query_str) response = llm.complete(fmt_prompt)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
2. Useful for questions related to oranges

```

In [ ]:
Copied!
```
query_str = (
    "Can you tell me more about the amount of Vitamin C in apples and oranges."
)
fmt_prompt = get_formatted_prompt(query_str)
response = llm.complete(fmt_prompt)

```

query_str = ( "Can you tell me more about the amount of Vitamin C in apples and oranges." ) fmt_prompt = get_formatted_prompt(query_str) response = llm.complete(fmt_prompt)
In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
1. Useful for questions related to apples
2. Useful for questions related to oranges

```

**Observation** : While the response corresponds to the correct choice, it can be hacky to parse into a structured output (e.g. a single integer). We'd need to do some string parsing on the choices to extract out a single number, and make it robust to failure modes.
## 2. A Router Prompt that can generate structured outputs¶
Therefore the next step is to try to prompt the model to output a more structured representation (JSON).
We define an output parser class (`RouterOutputParser`). This output parser will be responsible for both formatting the prompt and also parsing the result into a structured object (an `Answer`).
We then apply the `format` and `parse` methods of the output parser around the LLM call using the router prompt to generate a structured output.
### 2.a Import Answer Class¶
We load in the Answer class from our codebase. It's a very simple dataclass with two fields: `choice` and `reason`
In [ ]:
Copied!
```
from dataclasses import fields
from pydantic import BaseModel
import json

```

from dataclasses import fields from pydantic import BaseModel import json
In [ ]:
Copied!
```
class Answer(BaseModel):
    choice: int
    reason: str

```

class Answer(BaseModel): choice: int reason: str
In [ ]:
Copied!
```
print(json.dumps(Answer.schema(), indent=2))

```

print(json.dumps(Answer.schema(), indent=2))
```
{
  "title": "Answer",
  "type": "object",
  "properties": {
    "choice": {
      "title": "Choice",
      "type": "integer"
    },
    "reason": {
      "title": "Reason",
      "type": "string"
    }
  },
  "required": [
    "choice",
    "reason"
  ]
}

```

### 2.b Define Router Output Parser¶
In [ ]:
Copied!
```
from llama_index.core.types import BaseOutputParser

```

from llama_index.core.types import BaseOutputParser
In [ ]:
Copied!
```
FORMAT_STR = """The output should be formatted as a JSON instance that conforms to 
the JSON schema below. 

Here is the output schema:
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "choice": {
        "type": "integer"
      },
      "reason": {
        "type": "string"
      }
    },
    "required": [
      "choice",
      "reason"
    ],
    "additionalProperties": false
  }
}
"""

```

FORMAT_STR = """The output should be formatted as a JSON instance that conforms to the JSON schema below. Here is the output schema: { "type": "array", "items": { "type": "object", "properties": { "choice": { "type": "integer" }, "reason": { "type": "string" } }, "required": [ "choice", "reason" ], "additionalProperties": false } } """
If we want to put `FORMAT_STR` as part of an f-string as part of a prompt template, then we'll need to escape the curly braces so that they don't get treated as template variables.
In [ ]:
Copied!
```
def _escape_curly_braces(input_string: str) -> str:
    # Replace '{' with '{{' and '}' with '}}' to escape curly braces
    escaped_string = input_string.replace("{", "{{").replace("}", "}}")
    return escaped_string

```

def _escape_curly_braces(input_string: str) -> str: # Replace '{' with '{{' and '}' with '}}' to escape curly braces escaped_string = input_string.replace("{", "{{").replace("}", "}}") return escaped_string
We now define a simple parsing function to extract out the JSON string from the LLM response (by searching for square brackets)
In [ ]:
Copied!
```
def _marshal_output_to_json(output: str) -> str:
    output = output.strip()
    left = output.find("[")
    right = output.find("]")
    output = output[left : right + 1]
    return output

```

def _marshal_output_to_json(output: str) -> str: output = output.strip() left = output.find("[") right = output.find("]") output = output[left : right + 1] return output
We put these together in our `RouterOutputParser`
In [ ]:
Copied!
```
from typing import List


class RouterOutputParser(BaseOutputParser):
    def parse(self, output: str) -> List[Answer]:
        """Parse string."""
        json_output = _marshal_output_to_json(output)
        json_dicts = json.loads(json_output)
        answers = [Answer.from_dict(json_dict) for json_dict in json_dicts]
        return answers

    def format(self, prompt_template: str) -> str:
        return prompt_template + "\n\n" + _escape_curly_braces(FORMAT_STR)

```

from typing import List class RouterOutputParser(BaseOutputParser): def parse(self, output: str) -> List[Answer]: """Parse string.""" json_output = _marshal_output_to_json(output) json_dicts = json.loads(json_output) answers = [Answer.from_dict(json_dict) for json_dict in json_dicts] return answers def format(self, prompt_template: str) -> str: return prompt_template + "\n\n" + _escape_curly_braces(FORMAT_STR)
### 2.c Give it a Try¶
We create a function called `route_query` that will take in the output parser, llm, and prompt template and output a structured answer.
In [ ]:
Copied!
```
output_parser = RouterOutputParser()

```

output_parser = RouterOutputParser()
In [ ]:
Copied!
```
from typing import List


def route_query(
    query_str: str, choices: List[str], output_parser: RouterOutputParser
):
    choices_str

    fmt_base_prompt = router_prompt0.format(
        num_choices=len(choices),
        max_outputs=len(choices),
        context_list=choices_str,
        query_str=query_str,
    )
    fmt_json_prompt = output_parser.format(fmt_base_prompt)

    raw_output = llm.complete(fmt_json_prompt)
    parsed = output_parser.parse(str(raw_output))

    return parsed

```

from typing import List def route_query( query_str: str, choices: List[str], output_parser: RouterOutputParser ): choices_str fmt_base_prompt = router_prompt0.format( num_choices=len(choices), max_outputs=len(choices), context_list=choices_str, query_str=query_str, ) fmt_json_prompt = output_parser.format(fmt_base_prompt) raw_output = llm.complete(fmt_json_prompt) parsed = output_parser.parse(str(raw_output)) return parsed
## 3. Perform Routing with a Function Calling Endpoint¶
In the previous section, we showed how to build a router with a text completion endpoint. This includes formatting the prompt to encourage the model output structured JSON, and a parse function to load in JSON.
This process can feel a bit messy. Function calling endpoints (e.g. OpenAI) abstract away this complexity by allowing the model to natively output structured functions. This obviates the need to manually prompt + parse the outputs.
LlamaIndex offers an abstraction called a `PydanticProgram` that integrates with a function endpoint to produce a structured Pydantic object. We integrate with OpenAI and Guidance.
We redefine our `Answer` class with annotations, as well as an `Answers` class containing a list of answers.
In [ ]:
Copied!
```
from pydantic import Field


class Answer(BaseModel):
    "Represents a single choice with a reason."
    choice: int
    reason: str


class Answers(BaseModel):
    """Represents a list of answers."""

    answers: List[Answer]

```

from pydantic import Field class Answer(BaseModel): "Represents a single choice with a reason." choice: int reason: str class Answers(BaseModel): """Represents a list of answers.""" answers: List[Answer]
In [ ]:
Copied!
```
Answers.schema()

```

Answers.schema()
Out[ ]:
```
{'title': 'Answers',
 'description': 'Represents a list of answers.',
 'type': 'object',
 'properties': {'answers': {'title': 'Answers',
   'type': 'array',
   'items': {'$ref': '#/definitions/Answer'}}},
 'required': ['answers'],
 'definitions': {'Answer': {'title': 'Answer',
   'description': 'Represents a single choice with a reason.',
   'type': 'object',
   'properties': {'choice': {'title': 'Choice', 'type': 'integer'},
    'reason': {'title': 'Reason', 'type': 'string'}},
   'required': ['choice', 'reason']}}}
```

In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram

```

from llama_index.program.openai import OpenAIPydanticProgram
In [ ]:
Copied!
```
router_prompt1 = router_prompt0.partial_format(
    num_choices=len(choices),
    max_outputs=len(choices),
)

```

router_prompt1 = router_prompt0.partial_format( num_choices=len(choices), max_outputs=len(choices), )
In [ ]:
Copied!
```
program = OpenAIPydanticProgram.from_defaults(
    output_cls=Answers,
    prompt=router_prompt1,
    verbose=True,
)

```

program = OpenAIPydanticProgram.from_defaults( output_cls=Answers, prompt=router_prompt1, verbose=True, )
In [ ]:
Copied!
```
query_str = "What are the health benefits of eating orange peels?"
output = program(context_list=choices_str, query_str=query_str)

```

query_str = "What are the health benefits of eating orange peels?" output = program(context_list=choices_str, query_str=query_str)
```
Function call: Answers with args: {
  "answers": [
    {
      "choice": 2,
      "reason": "Orange peels are related to oranges"
    }
  ]
}

```

In [ ]:
Copied!
```
output

```

output
Out[ ]:
```
Answers(answers=[Answer(choice=2, reason='Orange peels are related to oranges')])
```

## 4. Plug Router Module as part of a RAG pipeline¶
In this section we'll put the router module to use in a RAG pipeline. We'll use it to dynamically decide whether to perform question-answering or summarization. We can easily get a question-answering query engine using top-k retrieval through our vector index, while summarization is performed through our summary index. Each query engine is described as a "choice" to our router, and we compose the whole thing into a single query engine.
### Setup: Load Data¶
We load the Llama 2 paper as data.
In [ ]:
Copied!
```
!mkdir data
!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"

```

!mkdir data !wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"
```
mkdir: data: File exists
--2023-09-17 23:37:11--  https://arxiv.org/pdf/2307.09288.pdf
Resolving arxiv.org (arxiv.org)... 128.84.21.199
Connecting to arxiv.org (arxiv.org)|128.84.21.199|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 13661300 (13M) [application/pdf]
Saving to: ‘data/llama2.pdf’

data/llama2.pdf     100%[===================>]  13.03M  1.50MB/s    in 9.5s    

2023-09-17 23:37:22 (1.37 MB/s) - ‘data/llama2.pdf’ saved [13661300/13661300]

```

In [ ]:
Copied!
```
from pathlib import Path
from llama_index.readers.file import PyMuPDFReader

```

from pathlib import Path from llama_index.readers.file import PyMuPDFReader
In [ ]:
Copied!
```
loader = PyMuPDFReader()
documents = loader.load(file_path="./data/llama2.pdf")

```

loader = PyMuPDFReader() documents = loader.load(file_path="./data/llama2.pdf")
### Setup: Define Indexes¶
Define both a vector index and summary index over this data.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.core import SummaryIndex
from llama_index.core.node_parser import SentenceSplitter

splitter = SentenceSplitter(chunk_size=1024)
vector_index = VectorStoreIndex.from_documents(
    documents, transformations=[splitter]
)
summary_index = SummaryIndex.from_documents(
    documents, transformations=[splitter]
)

```

from llama_index.core import VectorStoreIndex from llama_index.core import SummaryIndex from llama_index.core.node_parser import SentenceSplitter splitter = SentenceSplitter(chunk_size=1024) vector_index = VectorStoreIndex.from_documents( documents, transformations=[splitter] ) summary_index = SummaryIndex.from_documents( documents, transformations=[splitter] )
In [ ]:
Copied!
```
vector_query_engine = vector_index.as_query_engine(llm=llm)
summary_query_engine = summary_index.as_query_engine(llm=llm)

```

vector_query_engine = vector_index.as_query_engine(llm=llm) summary_query_engine = summary_index.as_query_engine(llm=llm)
### Define RouterQueryEngine¶
We subclass our `CustomQueryEngine` to define a custom router.
In [ ]:
Copied!
```
from llama_index.core.query_engine import CustomQueryEngine, BaseQueryEngine
from llama_index.core.response_synthesizers import TreeSummarize

```

from llama_index.core.query_engine import CustomQueryEngine, BaseQueryEngine from llama_index.core.response_synthesizers import TreeSummarize
In [ ]:
Copied!
```
class RouterQueryEngine(CustomQueryEngine):
    """Use our Pydantic program to perform routing."""

    query_engines: List[BaseQueryEngine]
    choice_descriptions: List[str]
    verbose: bool = False
    router_prompt: PromptTemplate
    llm: OpenAI
    summarizer: TreeSummarize = Field(default_factory=TreeSummarize)

    def custom_query(self, query_str: str):
        """Define custom query."""

        program = OpenAIPydanticProgram.from_defaults(
            output_cls=Answers,
            prompt=router_prompt1,
            verbose=self.verbose,
            llm=self.llm,
        )

        choices_str = get_choice_str(self.choice_descriptions)
        output = program(context_list=choices_str, query_str=query_str)
        # print choice and reason, and query the underlying engine
        if self.verbose:
            print(f"Selected choice(s):")
            for answer in output.answers:
                print(f"Choice: {answer.choice}, Reason: {answer.reason}")

        responses = []
        for answer in output.answers:
            choice_idx = answer.choice - 1
            query_engine = self.query_engines[choice_idx]
            response = query_engine.query(query_str)
            responses.append(response)

        # if a single choice is picked, we can just return that response
        if len(responses) == 1:
            return responses[0]
        else:
            # if multiple choices are picked, we can pick a summarizer
            response_strs = [str(r) for r in responses]
            result_response = self.summarizer.get_response(
                query_str, response_strs
            )
            return result_response

```

class RouterQueryEngine(CustomQueryEngine): """Use our Pydantic program to perform routing.""" query_engines: List[BaseQueryEngine] choice_descriptions: List[str] verbose: bool = False router_prompt: PromptTemplate llm: OpenAI summarizer: TreeSummarize = Field(default_factory=TreeSummarize) def custom_query(self, query_str: str): """Define custom query.""" program = OpenAIPydanticProgram.from_defaults( output_cls=Answers, prompt=router_prompt1, verbose=self.verbose, llm=self.llm, ) choices_str = get_choice_str(self.choice_descriptions) output = program(context_list=choices_str, query_str=query_str) # print choice and reason, and query the underlying engine if self.verbose: print(f"Selected choice(s):") for answer in output.answers: print(f"Choice: {answer.choice}, Reason: {answer.reason}") responses = [] for answer in output.answers: choice_idx = answer.choice - 1 query_engine = self.query_engines[choice_idx] response = query_engine.query(query_str) responses.append(response) # if a single choice is picked, we can just return that response if len(responses) == 1: return responses[0] else: # if multiple choices are picked, we can pick a summarizer response_strs = [str(r) for r in responses] result_response = self.summarizer.get_response( query_str, response_strs ) return result_response
In [ ]:
Copied!
```
choices = [
    (
        "Useful for answering questions about specific sections of the Llama 2"
        " paper"
    ),
    "Useful for questions that ask for a summary of the whole paper",
]

router_query_engine = RouterQueryEngine(
    query_engines=[vector_query_engine, summary_query_engine],
    choice_descriptions=choices,
    verbose=True,
    router_prompt=router_prompt1,
    llm=OpenAI(model="gpt-4"),
)

```

choices = [ ( "Useful for answering questions about specific sections of the Llama 2" " paper" ), "Useful for questions that ask for a summary of the whole paper", ] router_query_engine = RouterQueryEngine( query_engines=[vector_query_engine, summary_query_engine], choice_descriptions=choices, verbose=True, router_prompt=router_prompt1, llm=OpenAI(model="gpt-4"), )
### Try our constructed Router Query Engine¶
Let's take our self-built router query engine for a spin! We ask a question that routes to the vector query engine, and also another question that routes to the summarization engine.
In [ ]:
Copied!
```
response = router_query_engine.query(
    "How does the Llama 2 model compare to GPT-4 in the experimental results?"
)

```

response = router_query_engine.query( "How does the Llama 2 model compare to GPT-4 in the experimental results?" )
```
Function call: Answers with args: {
  "answers": [
    {
      "choice": 1,
      "reason": "This question is asking for specific information about the Llama 2 model and its comparison to GPT-4 in the experimental results. Therefore, the summary that is useful for answering questions about specific sections of the paper would be most relevant."
    }
  ]
}
Selected choice(s):
Choice: 1, Reason: This question is asking for specific information about the Llama 2 model and its comparison to GPT-4 in the experimental results. Therefore, the summary that is useful for answering questions about specific sections of the paper would be most relevant.

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
```
The Llama 2 model performs better than GPT-4 in the experimental results.

```

In [ ]:
Copied!
```
response = router_query_engine.query("Can you give a summary of this paper?")

```

response = router_query_engine.query("Can you give a summary of this paper?")
```
Function call: Answers with args: {
  "answers": [
    {
      "choice": 2,
      "reason": "This choice is directly related to providing a summary of the whole paper, which is what the question asks for."
    }
  ]
}
Selected choice(s):
Choice: 2, Reason: This choice is directly related to providing a summary of the whole paper, which is what the question asks for.

```

In [ ]:
Copied!
```
print(str(response))

```

print(str(response))
