![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# OpenAI function calling for Sub-Question Query Engine¶
In this notebook, we showcase how to use OpenAI function calling to improve the robustness of our sub-question query engine.
The sub-question query engine is designed to accept swappable question generators that implement the `BaseQuestionGenerator` interface.  
To leverage the power of openai function calling API, we implemented a new `OpenAIQuestionGenerator` (powered by our `OpenAIPydanticProgram`)
## OpenAI Question Generator¶
Unlike the default `LLMQuestionGenerator` that supports generic LLMs via the completion API, `OpenAIQuestionGenerator` only works with the latest OpenAI models that supports the function calling API.
The benefit is that these models are fine-tuned to output JSON objects, so we can worry less about output parsing issues.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-question-gen-openai

```

%pip install llama-index-question-gen-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.question_gen.openai import OpenAIQuestionGenerator

```

from llama_index.question_gen.openai import OpenAIQuestionGenerator
In [ ]:
Copied!
```
question_gen = OpenAIQuestionGenerator.from_defaults()

```

question_gen = OpenAIQuestionGenerator.from_defaults()
Let's test it out!
In [ ]:
Copied!
```
from llama_index.core.tools import ToolMetadata
from llama_index.core import QueryBundle

```

from llama_index.core.tools import ToolMetadata from llama_index.core import QueryBundle
In [ ]:
Copied!
```
tools = [
    ToolMetadata(
        name="march_22",
        description=(
            "Provides information about Uber quarterly financials ending March"
            " 2022"
        ),
    ),
    ToolMetadata(
        name="june_22",
        description=(
            "Provides information about Uber quarterly financials ending June"
            " 2022"
        ),
    ),
    ToolMetadata(
        name="sept_22",
        description=(
            "Provides information about Uber quarterly financials ending"
            " September 2022"
        ),
    ),
    ToolMetadata(
        name="sept_21",
        description=(
            "Provides information about Uber quarterly financials ending"
            " September 2022"
        ),
    ),
    ToolMetadata(
        name="june_21",
        description=(
            "Provides information about Uber quarterly financials ending June"
            " 2022"
        ),
    ),
    ToolMetadata(
        name="march_21",
        description=(
            "Provides information about Uber quarterly financials ending March"
            " 2022"
        ),
    ),
]

```

tools = [ ToolMetadata( name="march_22", description=( "Provides information about Uber quarterly financials ending March" " 2022" ), ), ToolMetadata( name="june_22", description=( "Provides information about Uber quarterly financials ending June" " 2022" ), ), ToolMetadata( name="sept_22", description=( "Provides information about Uber quarterly financials ending" " September 2022" ), ), ToolMetadata( name="sept_21", description=( "Provides information about Uber quarterly financials ending" " September 2022" ), ), ToolMetadata( name="june_21", description=( "Provides information about Uber quarterly financials ending June" " 2022" ), ), ToolMetadata( name="march_21", description=( "Provides information about Uber quarterly financials ending March" " 2022" ), ), ]
In [ ]:
Copied!
```
sub_questions = question_gen.generate(
    tools=tools,
    query=QueryBundle(
        "Compare the fastest growing sectors for Uber in the first two"
        " quarters of 2022"
    ),
)

```

sub_questions = question_gen.generate( tools=tools, query=QueryBundle( "Compare the fastest growing sectors for Uber in the first two" " quarters of 2022" ), )
In [ ]:
Copied!
```
sub_questions

```

sub_questions
Out[ ]:
```
[SubQuestion(sub_question='What were the fastest growing sectors for Uber in March 2022?', tool_name='march_22'),
 SubQuestion(sub_question='What were the fastest growing sectors for Uber in June 2022?', tool_name='june_22')]
```

