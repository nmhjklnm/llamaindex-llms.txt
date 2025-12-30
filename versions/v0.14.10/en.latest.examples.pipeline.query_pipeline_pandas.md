# Query Pipeline over Pandas DataFrames¶
This is a simple example that builds a query pipeline that can perform structured operations over a Pandas DataFrame to satisfy a user query, using LLMs to infer the set of operations.
This can be treated as the "from-scratch" version of our `PandasQueryEngine`.
WARNING: This tool provides the LLM access to the `eval` function. Arbitrary code execution is possible on the machine running this tool. This tool is not recommended to be used in a production setting, and would require heavy sandboxing or virtual machines.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai llama-index-experimental

```

%pip install llama-index-llms-openai llama-index-experimental
In [ ]:
Copied!
```
from llama_index.core.query_pipeline import (
    QueryPipeline as QP,
    Link,
    InputComponent,
)
from llama_index.experimental.query_engine.pandas import (
    PandasInstructionParser,
)
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

```

from llama_index.core.query_pipeline import ( QueryPipeline as QP, Link, InputComponent, ) from llama_index.experimental.query_engine.pandas import ( PandasInstructionParser, ) from llama_index.llms.openai import OpenAI from llama_index.core import PromptTemplate
## Download Data¶
Here we load the Titanic CSV dataset.
In [ ]:
Copied!
```
!wget 'https://raw.githubusercontent.com/jerryjliu/llama_index/main/docs/docs/examples/data/csv/titanic_train.csv' -O 'titanic_train.csv'

```

!wget 'https://raw.githubusercontent.com/jerryjliu/llama_index/main/docs/docs/examples/data/csv/titanic_train.csv' -O 'titanic_train.csv'
```
--2024-01-13 18:39:07--  https://raw.githubusercontent.com/jerryjliu/llama_index/main/docs/docs/examples/data/csv/titanic_train.csv
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8003::154, 2606:50c0:8001::154, 2606:50c0:8002::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8003::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 57726 (56K) [text/plain]
Saving to: ‘titanic_train.csv’

titanic_train.csv   100%[===================>]  56.37K  --.-KB/s    in 0.007s  

2024-01-13 18:39:07 (7.93 MB/s) - ‘titanic_train.csv’ saved [57726/57726]


```

In [ ]:
Copied!
```
import pandas as pd

df = pd.read_csv("./titanic_train.csv")

```

import pandas as pd df = pd.read_csv("./titanic_train.csv")
## Define Modules¶
Here we define the set of modules:
  1. Pandas prompt to infer pandas instructions from user query
  2. Pandas output parser to execute pandas instructions on dataframe, get back dataframe
  3. Response synthesis prompt to synthesize a final response given the dataframe
  4. LLM


The pandas output parser specifically is designed to safely execute Python code. It includes a lot of safety checks that may be annoying to write from scratch. This includes only importing from a set of approved modules (e.g. no modules that would alter the file system like `os`), and also making sure that no private/dunder methods are being called.
In [ ]:
Copied!
```
instruction_str = (
    "1. Convert the query to executable Python code using Pandas.\n"
    "2. The final line of code should be a Python expression that can be called with the `eval()` function.\n"
    "3. The code should represent a solution to the query.\n"
    "4. PRINT ONLY THE EXPRESSION.\n"
    "5. Do not quote the expression.\n"
)

pandas_prompt_str = (
    "You are working with a pandas dataframe in Python.\n"
    "The name of the dataframe is `df`.\n"
    "This is the result of `print(df.head())`:\n"
    "{df_str}\n\n"
    "Follow these instructions:\n"
    "{instruction_str}\n"
    "Query: {query_str}\n\n"
    "Expression:"
)
response_synthesis_prompt_str = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n\n"
    "Pandas Instructions (optional):\n{pandas_instructions}\n\n"
    "Pandas Output: {pandas_output}\n\n"
    "Response: "
)

pandas_prompt = PromptTemplate(pandas_prompt_str).partial_format(
    instruction_str=instruction_str, df_str=df.head(5)
)
pandas_output_parser = PandasInstructionParser(df)
response_synthesis_prompt = PromptTemplate(response_synthesis_prompt_str)
llm = OpenAI(model="gpt-3.5-turbo")

```

instruction_str = ( "1. Convert the query to executable Python code using Pandas.\n" "2. The final line of code should be a Python expression that can be called with the `eval()` function.\n" "3. The code should represent a solution to the query.\n" "4. PRINT ONLY THE EXPRESSION.\n" "5. Do not quote the expression.\n" ) pandas_prompt_str = ( "You are working with a pandas dataframe in Python.\n" "The name of the dataframe is `df`.\n" "This is the result of `print(df.head())`:\n" "{df_str}\n\n" "Follow these instructions:\n" "{instruction_str}\n" "Query: {query_str}\n\n" "Expression:" ) response_synthesis_prompt_str = ( "Given an input question, synthesize a response from the query results.\n" "Query: {query_str}\n\n" "Pandas Instructions (optional):\n{pandas_instructions}\n\n" "Pandas Output: {pandas_output}\n\n" "Response: " ) pandas_prompt = PromptTemplate(pandas_prompt_str).partial_format( instruction_str=instruction_str, df_str=df.head(5) ) pandas_output_parser = PandasInstructionParser(df) response_synthesis_prompt = PromptTemplate(response_synthesis_prompt_str) llm = OpenAI(model="gpt-3.5-turbo")
## Build Query Pipeline¶
Looks like this: input query_str -> pandas_prompt -> llm1 -> pandas_output_parser -> response_synthesis_prompt -> llm2
Additional connections to response_synthesis_prompt: llm1 -> pandas_instructions, and pandas_output_parser -> pandas_output.
In [ ]:
Copied!
```
qp = QP(
    modules={
        "input": InputComponent(),
        "pandas_prompt": pandas_prompt,
        "llm1": llm,
        "pandas_output_parser": pandas_output_parser,
        "response_synthesis_prompt": response_synthesis_prompt,
        "llm2": llm,
    },
    verbose=True,
)
qp.add_chain(["input", "pandas_prompt", "llm1", "pandas_output_parser"])
qp.add_links(
    [
        Link("input", "response_synthesis_prompt", dest_key="query_str"),
        Link(
            "llm1", "response_synthesis_prompt", dest_key="pandas_instructions"
        ),
        Link(
            "pandas_output_parser",
            "response_synthesis_prompt",
            dest_key="pandas_output",
        ),
    ]
)
# add link from response synthesis prompt to llm2
qp.add_link("response_synthesis_prompt", "llm2")

```

qp = QP( modules={ "input": InputComponent(), "pandas_prompt": pandas_prompt, "llm1": llm, "pandas_output_parser": pandas_output_parser, "response_synthesis_prompt": response_synthesis_prompt, "llm2": llm, }, verbose=True, ) qp.add_chain(["input", "pandas_prompt", "llm1", "pandas_output_parser"]) qp.add_links( [ Link("input", "response_synthesis_prompt", dest_key="query_str"), Link( "llm1", "response_synthesis_prompt", dest_key="pandas_instructions" ), Link( "pandas_output_parser", "response_synthesis_prompt", dest_key="pandas_output", ), ] ) # add link from response synthesis prompt to llm2 qp.add_link("response_synthesis_prompt", "llm2")
## Run Query¶
In [ ]:
Copied!
```
response = qp.run(
    query_str="What is the correlation between survival and age?",
)

```

response = qp.run( query_str="What is the correlation between survival and age?", )
```
> Running module input with input: 
query_str: What is the correlation between survival and age?

> Running module pandas_prompt with input: 
query_str: What is the correlation between survival and age?

> Running module llm1 with input: 
messages: You are working with a pandas dataframe in Python.
The name of the dataframe is `df`.
This is the result of `print(df.head())`:
   survived  pclass                                               name  ...

> Running module pandas_output_parser with input: 
input: assistant: df['survived'].corr(df['age'])

> Running module response_synthesis_prompt with input: 
query_str: What is the correlation between survival and age?
pandas_instructions: assistant: df['survived'].corr(df['age'])
pandas_output: -0.07722109457217755

> Running module llm2 with input: 
messages: Given an input question, synthesize a response from the query results.
Query: What is the correlation between survival and age?

Pandas Instructions (optional):
df['survived'].corr(df['age'])

Pandas ...


```

In [ ]:
Copied!
```
print(response.message.content)

```

print(response.message.content)
```
The correlation between survival and age is -0.0772. This indicates a weak negative correlation, suggesting that as age increases, the likelihood of survival slightly decreases.

```

