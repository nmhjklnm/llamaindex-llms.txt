![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# DataFrame Structured Data Extraction¶
This demo shows how you can extract tabular DataFrames from raw text.
This was directly inspired by jxnl's dataframe example here: https://github.com/jxnl/openai_function_call/blob/main/auto_dataframe.py.
We show this with different levels of complexity, all backed by the OpenAI Function API:
  * (more code) How to build an extractor yourself using our OpenAIPydanticProgram
  * (less code) Using our out-of-the-box `DFFullProgram` and `DFRowsProgram` objects


## Build a DF Extractor Yourself (Using OpenAIPydanticProgram)¶
Our OpenAIPydanticProgram is a wrapper around an OpenAI LLM that supports function calling - it will return structured outputs in the form of a Pydantic object.
We import our `DataFrame` and `DataFrameRowsOnly` objects.
To create an output extractor, you just need to 1) specify the relevant Pydantic object, and 2) Add the right prompt
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-program-openai

```

%pip install llama-index-llms-openai %pip install llama-index-program-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core.program import (
    DFFullProgram,
    DataFrame,
    DataFrameRowsOnly,
)
from llama_index.llms.openai import OpenAI

```

from llama_index.program.openai import OpenAIPydanticProgram from llama_index.core.program import ( DFFullProgram, DataFrame, DataFrameRowsOnly, ) from llama_index.llms.openai import OpenAI
In [ ]:
Copied!
```
program = OpenAIPydanticProgram.from_defaults(
    output_cls=DataFrame,
    llm=OpenAI(temperature=0, model="gpt-4-0613"),
    prompt_template_str=(
        "Please extract the following query into a structured data according"
        " to: {input_str}.Please extract both the set of column names and a"
        " set of rows."
    ),
    verbose=True,
)

```

program = OpenAIPydanticProgram.from_defaults( output_cls=DataFrame, llm=OpenAI(temperature=0, model="gpt-4-0613"), prompt_template_str=( "Please extract the following query into a structured data according" " to: {input_str}.Please extract both the set of column names and a" " set of rows." ), verbose=True, )
In [ ]:
Copied!
```
# NOTE: the test example is taken from jxnl's repo

response_obj = program(
    input_str="""My name is John and I am 25 years old. I live in 
        New York and I like to play basketball. His name is 
        Mike and he is 30 years old. He lives in San Francisco 
        and he likes to play baseball. Sarah is 20 years old 
        and she lives in Los Angeles. She likes to play tennis.
        Her name is Mary and she is 35 years old. 
        She lives in Chicago."""
)
response_obj

```

# NOTE: the test example is taken from jxnl's repo response_obj = program( input_str="""My name is John and I am 25 years old. I live in New York and I like to play basketball. His name is Mike and he is 30 years old. He lives in San Francisco and he likes to play baseball. Sarah is 20 years old and she lives in Los Angeles. She likes to play tennis. Her name is Mary and she is 35 years old. She lives in Chicago.""" ) response_obj
```
Function call: DataFrame with args: {
  "columns": [
    {
      "column_name": "Name",
      "column_desc": "Name of the person"
    },
    {
      "column_name": "Age",
      "column_desc": "Age of the person"
    },
    {
      "column_name": "City",
      "column_desc": "City where the person lives"
    },
    {
      "column_name": "Hobby",
      "column_desc": "What the person likes to do"
    }
  ],
  "rows": [
    {
      "row_values": ["John", 25, "New York", "play basketball"]
    },
    {
      "row_values": ["Mike", 30, "San Francisco", "play baseball"]
    },
    {
      "row_values": ["Sarah", 20, "Los Angeles", "play tennis"]
    },
    {
      "row_values": ["Mary", 35, "Chicago", "play tennis"]
    }
  ]
}

```

Out[ ]:
```
DataFrame(description=None, columns=[DataFrameColumn(column_name='Name', column_desc='Name of the person'), DataFrameColumn(column_name='Age', column_desc='Age of the person'), DataFrameColumn(column_name='City', column_desc='City where the person lives'), DataFrameColumn(column_name='Hobby', column_desc='What the person likes to do')], rows=[DataFrameRow(row_values=['John', 25, 'New York', 'play basketball']), DataFrameRow(row_values=['Mike', 30, 'San Francisco', 'play baseball']), DataFrameRow(row_values=['Sarah', 20, 'Los Angeles', 'play tennis']), DataFrameRow(row_values=['Mary', 35, 'Chicago', 'play tennis'])])
```

In [ ]:
Copied!
```
program = OpenAIPydanticProgram.from_defaults(
    output_cls=DataFrameRowsOnly,
    llm=OpenAI(temperature=0, model="gpt-4-0613"),
    prompt_template_str=(
        "Please extract the following text into a structured data:"
        " {input_str}. The column names are the following: ['Name', 'Age',"
        " 'City', 'Favorite Sport']. Do not specify additional parameters that"
        " are not in the function schema. "
    ),
    verbose=True,
)

```

program = OpenAIPydanticProgram.from_defaults( output_cls=DataFrameRowsOnly, llm=OpenAI(temperature=0, model="gpt-4-0613"), prompt_template_str=( "Please extract the following text into a structured data:" " {input_str}. The column names are the following: ['Name', 'Age'," " 'City', 'Favorite Sport']. Do not specify additional parameters that" " are not in the function schema. " ), verbose=True, )
In [ ]:
Copied!
```
program(
    input_str="""My name is John and I am 25 years old. I live in 
        New York and I like to play basketball. His name is 
        Mike and he is 30 years old. He lives in San Francisco 
        and he likes to play baseball. Sarah is 20 years old 
        and she lives in Los Angeles. She likes to play tennis.
        Her name is Mary and she is 35 years old. 
        She lives in Chicago."""
)

```

program( input_str="""My name is John and I am 25 years old. I live in New York and I like to play basketball. His name is Mike and he is 30 years old. He lives in San Francisco and he likes to play baseball. Sarah is 20 years old and she lives in Los Angeles. She likes to play tennis. Her name is Mary and she is 35 years old. She lives in Chicago.""" )
```
Function call: DataFrameRowsOnly with args: {
  "rows": [
    {
      "row_values": ["John", 25, "New York", "basketball"]
    },
    {
      "row_values": ["Mike", 30, "San Francisco", "baseball"]
    },
    {
      "row_values": ["Sarah", 20, "Los Angeles", "tennis"]
    },
    {
      "row_values": ["Mary", 35, "Chicago", ""]
    }
  ]
}

```

Out[ ]:
```
DataFrameRowsOnly(rows=[DataFrameRow(row_values=['John', 25, 'New York', 'basketball']), DataFrameRow(row_values=['Mike', 30, 'San Francisco', 'baseball']), DataFrameRow(row_values=['Sarah', 20, 'Los Angeles', 'tennis']), DataFrameRow(row_values=['Mary', 35, 'Chicago', ''])])
```

## Use our DataFrame Programs¶
We provide convenience wrappers for `DFFullProgram` and `DFRowsProgram`. This allows a simpler object creation interface than specifying all details through the `OpenAIPydanticProgram`.
In [ ]:
Copied!
```
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core.program import DFFullProgram, DFRowsProgram
import pandas as pd

# initialize empty df
df = pd.DataFrame(
    {
        "Name": pd.Series(dtype="str"),
        "Age": pd.Series(dtype="int"),
        "City": pd.Series(dtype="str"),
        "Favorite Sport": pd.Series(dtype="str"),
    }
)

# initialize program, using existing df as schema
df_rows_program = DFRowsProgram.from_defaults(
    pydantic_program_cls=OpenAIPydanticProgram, df=df
)

```

from llama_index.program.openai import OpenAIPydanticProgram from llama_index.core.program import DFFullProgram, DFRowsProgram import pandas as pd # initialize empty df df = pd.DataFrame( { "Name": pd.Series(dtype="str"), "Age": pd.Series(dtype="int"), "City": pd.Series(dtype="str"), "Favorite Sport": pd.Series(dtype="str"), } ) # initialize program, using existing df as schema df_rows_program = DFRowsProgram.from_defaults( pydantic_program_cls=OpenAIPydanticProgram, df=df )
In [ ]:
Copied!
```
# parse text, using existing df as schema
result_obj = df_rows_program(
    input_str="""My name is John and I am 25 years old. I live in 
        New York and I like to play basketball. His name is 
        Mike and he is 30 years old. He lives in San Francisco 
        and he likes to play baseball. Sarah is 20 years old 
        and she lives in Los Angeles. She likes to play tennis.
        Her name is Mary and she is 35 years old. 
        She lives in Chicago."""
)

```

# parse text, using existing df as schema result_obj = df_rows_program( input_str="""My name is John and I am 25 years old. I live in New York and I like to play basketball. His name is Mike and he is 30 years old. He lives in San Francisco and he likes to play baseball. Sarah is 20 years old and she lives in Los Angeles. She likes to play tennis. Her name is Mary and she is 35 years old. She lives in Chicago.""" )
In [ ]:
Copied!
```
result_obj.to_df(existing_df=df)

```

result_obj.to_df(existing_df=df)
```
/Users/jerryliu/Programming/gpt_index/llama_index/program/predefined/df.py:65: FutureWarning: The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.
  return existing_df.append(new_df, ignore_index=True)

```

Out[ ]:
| Name | Age | City | Favorite Sport  
---|---|---|---|---  
0 | John | 25 | New York | Basketball  
1 | Mike | 30 | San Francisco | Baseball  
2 | Sarah | 20 | Los Angeles | Tennis  
3 | Mary | 35 | Chicago |   
In [ ]:
Copied!
```
# initialize program that can do joint schema extraction and structured data extraction
df_full_program = DFFullProgram.from_defaults(
    pydantic_program_cls=OpenAIPydanticProgram,
)

```

# initialize program that can do joint schema extraction and structured data extraction df_full_program = DFFullProgram.from_defaults( pydantic_program_cls=OpenAIPydanticProgram, )
In [ ]:
Copied!
```
result_obj = df_full_program(
    input_str="""My name is John and I am 25 years old. I live in 
        New York and I like to play basketball. His name is 
        Mike and he is 30 years old. He lives in San Francisco 
        and he likes to play baseball. Sarah is 20 years old 
        and she lives in Los Angeles. She likes to play tennis.
        Her name is Mary and she is 35 years old. 
        She lives in Chicago."""
)

```

result_obj = df_full_program( input_str="""My name is John and I am 25 years old. I live in New York and I like to play basketball. His name is Mike and he is 30 years old. He lives in San Francisco and he likes to play baseball. Sarah is 20 years old and she lives in Los Angeles. She likes to play tennis. Her name is Mary and she is 35 years old. She lives in Chicago.""" )
In [ ]:
Copied!
```
result_obj.to_df()

```

result_obj.to_df()
Out[ ]:
| Name | Age | Location | Hobby  
---|---|---|---|---  
0 | John | 25 | New York | Basketball  
1 | Mike | 30 | San Francisco | Baseball  
2 | Sarah | 20 | Los Angeles | Tennis  
3 | Mary | 35 | Chicago |   
In [ ]:
Copied!
```
# initialize empty df
df = pd.DataFrame(
    {
        "City": pd.Series(dtype="str"),
        "State": pd.Series(dtype="str"),
        "Population": pd.Series(dtype="int"),
    }
)

# initialize program, using existing df as schema
df_rows_program = DFRowsProgram.from_defaults(
    pydantic_program_cls=OpenAIPydanticProgram, df=df
)

```

# initialize empty df df = pd.DataFrame( { "City": pd.Series(dtype="str"), "State": pd.Series(dtype="str"), "Population": pd.Series(dtype="int"), } ) # initialize program, using existing df as schema df_rows_program = DFRowsProgram.from_defaults( pydantic_program_cls=OpenAIPydanticProgram, df=df )
In [ ]:
Copied!
```
input_text = """San Francisco is in California, has a population of 800,000. 
New York City is the most populous city in the United States. \
With a 2020 population of 8,804,190 distributed over 300.46 square miles (778.2 km2), \
New York City is the most densely populated major city in the United States.
New York City is in New York State.
Boston (US: /ˈbɔːstən/),[8] officially the City of Boston, is the capital and largest city of the Commonwealth of Massachusetts \
and the cultural and financial center of the New England region of the Northeastern United States. \
The city boundaries encompass an area of about 48.4 sq mi (125 km2)[9] and a population of 675,647 as of 2020.[4]
"""

# parse text, using existing df as schema
result_obj = df_rows_program(input_str=input_text)

```

input_text = """San Francisco is in California, has a population of 800,000. New York City is the most populous city in the United States. \ With a 2020 population of 8,804,190 distributed over 300.46 square miles (778.2 km2), \ New York City is the most densely populated major city in the United States. New York City is in New York State. Boston (US: /ˈbɔːstən/),[8] officially the City of Boston, is the capital and largest city of the Commonwealth of Massachusetts \ and the cultural and financial center of the New England region of the Northeastern United States. \ The city boundaries encompass an area of about 48.4 sq mi (125 km2)[9] and a population of 675,647 as of 2020.[4] """ # parse text, using existing df as schema result_obj = df_rows_program(input_str=input_text)
In [ ]:
Copied!
```
new_df = result_obj.to_df(existing_df=df)
new_df

```

new_df = result_obj.to_df(existing_df=df) new_df
```
/Users/jerryliu/Programming/gpt_index/llama_index/program/predefined/df.py:65: FutureWarning: The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.
  return existing_df.append(new_df, ignore_index=True)

```

Out[ ]:
| City | State | Population  
---|---|---|---  
0 | San Francisco | California | 800000  
1 | New York City | New York | 8804190  
2 | Boston | Massachusetts | 675647
