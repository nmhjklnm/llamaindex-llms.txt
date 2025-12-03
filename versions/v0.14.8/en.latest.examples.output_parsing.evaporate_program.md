![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Evaporate Demo¶
This demo shows how you can extract DataFrame from raw text using the Evaporate paper (Arora et al.): https://arxiv.org/abs/2304.09433.
The inspiration is to first "fit" on a set of training text. The fitting process uses the LLM to generate a set of parsing functions from the text. These fitted functions are then applied to text during inference time.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-program-evaporate

```

%pip install llama-index-llms-openai %pip install llama-index-program-evaporate
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
%load_ext autoreload
%autoreload 2

```

%load_ext autoreload %autoreload 2
## Use `DFEvaporateProgram`¶
The `DFEvaporateProgram` will extract a 2D dataframe from a set of datapoints given a set of fields, and some training data to "fit" some functions on.
### Load data¶
Here we load a set of cities from Wikipedia.
In [ ]:
Copied!
```
wiki_titles = ["Toronto", "Seattle", "Chicago", "Boston", "Houston"]

```

wiki_titles = ["Toronto", "Seattle", "Chicago", "Boston", "Houston"]
In [ ]:
Copied!
```
from pathlib import Path

import requests

for title in wiki_titles:
    response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            # 'exintro': True,
            "explaintext": True,
        },
    ).json()
    page = next(iter(response["query"]["pages"].values()))
    wiki_text = page["extract"]

    data_path = Path("data")
    if not data_path.exists():
        Path.mkdir(data_path)

    with open(data_path / f"{title}.txt", "w") as fp:
        fp.write(wiki_text)

```

from pathlib import Path import requests for title in wiki_titles: response = requests.get( "https://en.wikipedia.org/w/api.php", params={ "action": "query", "format": "json", "titles": title, "prop": "extracts", # 'exintro': True, "explaintext": True, }, ).json() page = next(iter(response["query"]["pages"].values())) wiki_text = page["extract"] data_path = Path("data") if not data_path.exists(): Path.mkdir(data_path) with open(data_path / f"{title}.txt", "w") as fp: fp.write(wiki_text)
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

# Load all wiki documents
city_docs = {}
for wiki_title in wiki_titles:
    city_docs[wiki_title] = SimpleDirectoryReader(
        input_files=[f"data/{wiki_title}.txt"]
    ).load_data()

```

from llama_index.core import SimpleDirectoryReader # Load all wiki documents city_docs = {} for wiki_title in wiki_titles: city_docs[wiki_title] = SimpleDirectoryReader( input_files=[f"data/{wiki_title}.txt"] ).load_data()
### Parse Data¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings

# setup settings
Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.chunk_size = 512

```

from llama_index.llms.openai import OpenAI from llama_index.core import Settings # setup settings Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo") Settings.chunk_size = 512
In [ ]:
Copied!
```
# get nodes for each document
city_nodes = {}
for wiki_title in wiki_titles:
    docs = city_docs[wiki_title]
    nodes = Settings.node_parser.get_nodes_from_documents(docs)
    city_nodes[wiki_title] = nodes

```

# get nodes for each document city_nodes = {} for wiki_title in wiki_titles: docs = city_docs[wiki_title] nodes = Settings.node_parser.get_nodes_from_documents(docs) city_nodes[wiki_title] = nodes
### Running the DFEvaporateProgram¶
Here we demonstrate how to extract datapoints with our `DFEvaporateProgram`. Given a set of fields, the `DFEvaporateProgram` can first fit functions on a set of training data, and then run extraction over inference data.
In [ ]:
Copied!
```
from llama_index.program.evaporate import DFEvaporateProgram

# define program
program = DFEvaporateProgram.from_defaults(
    fields_to_extract=["population"],
)

```

from llama_index.program.evaporate import DFEvaporateProgram # define program program = DFEvaporateProgram.from_defaults( fields_to_extract=["population"], )
### Fitting Functions¶
In [ ]:
Copied!
```
program.fit_fields(city_nodes["Toronto"][:1])

```

program.fit_fields(city_nodes["Toronto"][:1])
Out[ ]:
```
{'population': 'def get_population_field(text: str):\n    """\n    Function to extract population. \n    """\n    \n    # Use regex to find the population field\n    pattern = r\'(?<=population of )(\\d+,?\\d*)\'\n    population_field = re.search(pattern, text).group(1)\n    \n    # Return the population field as a single value\n    return int(population_field.replace(\',\', \'\'))'}
```

In [ ]:
Copied!
```
# view extracted function
print(program.get_function_str("population"))

```

# view extracted function print(program.get_function_str("population"))
```
def get_population_field(text: str):
    """
    Function to extract population. 
    """
    
    # Use regex to find the population field
    pattern = r'(?<=population of )(\d+,?\d*)'
    population_field = re.search(pattern, text).group(1)
    
    # Return the population field as a single value
    return int(population_field.replace(',', ''))

```

### Run Inference¶
In [ ]:
Copied!
```
seattle_df = program(nodes=city_nodes["Seattle"][:1])

```

seattle_df = program(nodes=city_nodes["Seattle"][:1])
In [ ]:
Copied!
```
seattle_df

```

seattle_df
Out[ ]:
```
DataFrameRowsOnly(rows=[DataFrameRow(row_values=[749256])])
```

## Use `MultiValueEvaporateProgram`¶
In contrast to the `DFEvaporateProgram`, which assumes the output obeys a 2D tabular format (one row per node), the `MultiValueEvaporateProgram` returns a list of `DataFrameRow` objects - each object corresponds to a column, and can contain a variable length of values. This can help if we want to extract multiple values for one field from a given piece of text.
In this example, we use this program to parse gold medal counts.
In [ ]:
Copied!
```
Settings.llm = OpenAI(temperature=0, model="gpt-4")
Settings.chunk_size = 1024
Settings.chunk_overlap = 0

```

Settings.llm = OpenAI(temperature=0, model="gpt-4") Settings.chunk_size = 1024 Settings.chunk_overlap = 0
In [ ]:
Copied!
```
from llama_index.core.data_structs import Node

# Olympic total medal counts: https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table

train_text = """
<table class="wikitable sortable" style="margin-top:0; text-align:center; font-size:90%;">

<tbody><tr>
<th>Team (IOC code)
</th>
<th>No. Summer
</th>
<th>No. Winter
</th>
<th>No. Games
</th></tr>
<tr>
<td align="left"><span id="ALB"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/36/Flag_of_Albania.svg/22px-Flag_of_Albania.svg.png" decoding="async" width="22" height="16" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/36/Flag_of_Albania.svg/33px-Flag_of_Albania.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/36/Flag_of_Albania.svg/44px-Flag_of_Albania.svg.png 2x" data-file-width="980" data-file-height="700" />&#160;<a href="/wiki/Albania_at_the_Olympics" title="Albania at the Olympics">Albania</a>&#160;<span style="font-size:90%;">(ALB)</span></span>
</td>
<td style="background:#f2f2ce;">9</td>
<td style="background:#cedff2;">5</td>
<td>14
</td></tr>
<tr>
<td align="left"><span id="ASA"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/87/Flag_of_American_Samoa.svg/22px-Flag_of_American_Samoa.svg.png" decoding="async" width="22" height="11" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/87/Flag_of_American_Samoa.svg/33px-Flag_of_American_Samoa.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/87/Flag_of_American_Samoa.svg/44px-Flag_of_American_Samoa.svg.png 2x" data-file-width="1000" data-file-height="500" />&#160;<a href="/wiki/American_Samoa_at_the_Olympics" title="American Samoa at the Olympics">American Samoa</a>&#160;<span style="font-size:90%;">(ASA)</span></span>
</td>
<td style="background:#f2f2ce;">9</td>
<td style="background:#cedff2;">2</td>
<td>11
</td></tr>
<tr>
<td align="left"><span id="AND"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Andorra.svg/22px-Flag_of_Andorra.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Andorra.svg/33px-Flag_of_Andorra.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Andorra.svg/44px-Flag_of_Andorra.svg.png 2x" data-file-width="1000" data-file-height="700" />&#160;<a href="/wiki/Andorra_at_the_Olympics" title="Andorra at the Olympics">Andorra</a>&#160;<span style="font-size:90%;">(AND)</span></span>
</td>
<td style="background:#f2f2ce;">12</td>
<td style="background:#cedff2;">13</td>
<td>25
</td></tr>
<tr>
<td align="left"><span id="ANG"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/22px-Flag_of_Angola.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/33px-Flag_of_Angola.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/44px-Flag_of_Angola.svg.png 2x" data-file-width="900" data-file-height="600" />&#160;<a href="/wiki/Angola_at_the_Olympics" title="Angola at the Olympics">Angola</a>&#160;<span style="font-size:90%;">(ANG)</span></span>
</td>
<td style="background:#f2f2ce;">10</td>
<td style="background:#cedff2;">0</td>
<td>10
</td></tr>
<tr>
<td align="left"><span id="ANT"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Antigua_and_Barbuda.svg/22px-Flag_of_Antigua_and_Barbuda.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Antigua_and_Barbuda.svg/33px-Flag_of_Antigua_and_Barbuda.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Antigua_and_Barbuda.svg/44px-Flag_of_Antigua_and_Barbuda.svg.png 2x" data-file-width="900" data-file-height="600" />&#160;<a href="/wiki/Antigua_and_Barbuda_at_the_Olympics" title="Antigua and Barbuda at the Olympics">Antigua and Barbuda</a>&#160;<span style="font-size:90%;">(ANT)</span></span>
</td>
<td style="background:#f2f2ce;">11</td>
<td style="background:#cedff2;">0</td>
<td>11
</td></tr>
<tr>
<td align="left"><span id="ARU"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Aruba.svg/22px-Flag_of_Aruba.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Aruba.svg/33px-Flag_of_Aruba.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Aruba.svg/44px-Flag_of_Aruba.svg.png 2x" data-file-width="900" data-file-height="600" />&#160;<a href="/wiki/Aruba_at_the_Olympics" title="Aruba at the Olympics">Aruba</a>&#160;<span style="font-size:90%;">(ARU)</span></span>
</td>
<td style="background:#f2f2ce;">9</td>
<td style="background:#cedff2;">0</td>
<td>9
</td></tr>
"""
train_nodes = [Node(text=train_text)]

```

from llama_index.core.data_structs import Node # Olympic total medal counts: https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table train_text = """ """ train_nodes = [Node(text=train_text)] Team (IOC code)  | No. Summer  | No. Winter  | No. Games   
---|---|---|---  
![](https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Flag_of_Albania.svg/22px-Flag_of_Albania.svg.png) Albania (ALB) | 9 | 5 | 14   
![](https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Flag_of_American_Samoa.svg/22px-Flag_of_American_Samoa.svg.png) American Samoa (ASA) | 9 | 2 | 11   
![](https://upload.wikimedia.org/wikipedia/commons/thumb/1/19/Flag_of_Andorra.svg/22px-Flag_of_Andorra.svg.png) Andorra (AND) | 12 | 13 | 25   
![](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9d/Flag_of_Angola.svg/22px-Flag_of_Angola.svg.png) Angola (ANG) | 10 | 0 | 10   
![](https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Flag_of_Antigua_and_Barbuda.svg/22px-Flag_of_Antigua_and_Barbuda.svg.png) Antigua and Barbuda (ANT) | 11 | 0 | 11   
![](https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Flag_of_Aruba.svg/22px-Flag_of_Aruba.svg.png) Aruba (ARU) | 9 | 0 | 9   
In [ ]:
Copied!
```
infer_text = """
<td align="left"><span id="BAN"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/22px-Flag_of_Bangladesh.svg.png" decoding="async" width="22" height="13" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/33px-Flag_of_Bangladesh.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/44px-Flag_of_Bangladesh.svg.png 2x" data-file-width="1000" data-file-height="600" />&#160;<a href="/wiki/Bangladesh_at_the_Olympics" title="Bangladesh at the Olympics">Bangladesh</a>&#160;<span style="font-size:90%;">(BAN)</span></span>
</td>
<td style="background:#f2f2ce;">10</td>
<td style="background:#cedff2;">0</td>
<td>10
</td></tr>
<tr>
<td align="left"><span id="BIZ"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Flag_of_Belize.svg/22px-Flag_of_Belize.svg.png" decoding="async" width="22" height="13" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Flag_of_Belize.svg/33px-Flag_of_Belize.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Flag_of_Belize.svg/44px-Flag_of_Belize.svg.png 2x" data-file-width="1000" data-file-height="600" />&#160;<a href="/wiki/Belize_at_the_Olympics" title="Belize at the Olympics">Belize</a>&#160;<span style="font-size:90%;">(BIZ)</span></span> <sup class="reference" id="ref_BIZBIZ"><a href="#endnote_BIZBIZ">[BIZ]</a></sup>
</td>
<td style="background:#f2f2ce;">13</td>
<td style="background:#cedff2;">0</td>
<td>13
</td></tr>
<tr>
<td align="left"><span id="BEN"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/22px-Flag_of_Benin.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/33px-Flag_of_Benin.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/44px-Flag_of_Benin.svg.png 2x" data-file-width="900" data-file-height="600" />&#160;<a href="/wiki/Benin_at_the_Olympics" title="Benin at the Olympics">Benin</a>&#160;<span style="font-size:90%;">(BEN)</span></span> <sup class="reference" id="ref_BENBEN"><a href="#endnote_BENBEN">[BEN]</a></sup>
</td>
<td style="background:#f2f2ce;">12</td>
<td style="background:#cedff2;">0</td>
<td>12
</td></tr>
<tr>
<td align="left"><span id="BHU"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/91/Flag_of_Bhutan.svg/22px-Flag_of_Bhutan.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/91/Flag_of_Bhutan.svg/33px-Flag_of_Bhutan.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/91/Flag_of_Bhutan.svg/44px-Flag_of_Bhutan.svg.png 2x" data-file-width="900" data-file-height="600" />&#160;<a href="/wiki/Bhutan_at_the_Olympics" title="Bhutan at the Olympics">Bhutan</a>&#160;<span style="font-size:90%;">(BHU)</span></span>
</td>
<td style="background:#f2f2ce;">10</td>
<td style="background:#cedff2;">0</td>
<td>10
</td></tr>
<tr>
<td align="left"><span id="BOL"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Bolivia.svg/22px-Flag_of_Bolivia.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Bolivia.svg/33px-Flag_of_Bolivia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Bolivia.svg/44px-Flag_of_Bolivia.svg.png 2x" data-file-width="1100" data-file-height="750" />&#160;<a href="/wiki/Bolivia_at_the_Olympics" title="Bolivia at the Olympics">Bolivia</a>&#160;<span style="font-size:90%;">(BOL)</span></span>
</td>
<td style="background:#f2f2ce;">15</td>
<td style="background:#cedff2;">7</td>
<td>22
</td></tr>
<tr>
<td align="left"><span id="BIH"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bosnia_and_Herzegovina.svg/22px-Flag_of_Bosnia_and_Herzegovina.svg.png" decoding="async" width="22" height="11" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bosnia_and_Herzegovina.svg/33px-Flag_of_Bosnia_and_Herzegovina.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bosnia_and_Herzegovina.svg/44px-Flag_of_Bosnia_and_Herzegovina.svg.png 2x" data-file-width="800" data-file-height="400" />&#160;<a href="/wiki/Bosnia_and_Herzegovina_at_the_Olympics" title="Bosnia and Herzegovina at the Olympics">Bosnia and Herzegovina</a>&#160;<span style="font-size:90%;">(BIH)</span></span>
</td>
<td style="background:#f2f2ce;">8</td>
<td style="background:#cedff2;">8</td>
<td>16
</td></tr>
<tr>
<td align="left"><span id="IVB"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/42/Flag_of_the_British_Virgin_Islands.svg/22px-Flag_of_the_British_Virgin_Islands.svg.png" decoding="async" width="22" height="11" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/42/Flag_of_the_British_Virgin_Islands.svg/33px-Flag_of_the_British_Virgin_Islands.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/42/Flag_of_the_British_Virgin_Islands.svg/44px-Flag_of_the_British_Virgin_Islands.svg.png 2x" data-file-width="1200" data-file-height="600" />&#160;<a href="/wiki/British_Virgin_Islands_at_the_Olympics" title="British Virgin Islands at the Olympics">British Virgin Islands</a>&#160;<span style="font-size:90%;">(IVB)</span></span>
</td>
<td style="background:#f2f2ce;">10</td>
<td style="background:#cedff2;">2</td>
<td>12
</td></tr>
<tr>
<td align="left"><span id="BRU"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Brunei.svg/22px-Flag_of_Brunei.svg.png" decoding="async" width="22" height="11" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Brunei.svg/33px-Flag_of_Brunei.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Brunei.svg/44px-Flag_of_Brunei.svg.png 2x" data-file-width="1440" data-file-height="720" />&#160;<a href="/wiki/Brunei_at_the_Olympics" title="Brunei at the Olympics">Brunei</a>&#160;<span style="font-size:90%;">(BRU)</span></span> <sup class="reference" id="ref_AA"><a href="#endnote_AA">[A]</a></sup>
</td>
<td style="background:#f2f2ce;">6</td>
<td style="background:#cedff2;">0</td>
<td>6
</td></tr>
<tr>
<td align="left"><span id="CAM"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/22px-Flag_of_Cambodia.svg.png" decoding="async" width="22" height="14" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/33px-Flag_of_Cambodia.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/44px-Flag_of_Cambodia.svg.png 2x" data-file-width="1000" data-file-height="640" />&#160;<a href="/wiki/Cambodia_at_the_Olympics" title="Cambodia at the Olympics">Cambodia</a>&#160;<span style="font-size:90%;">(CAM)</span></span>
</td>
<td style="background:#f2f2ce;">10</td>
<td style="background:#cedff2;">0</td>
<td>10
</td></tr>
<tr>
<td align="left"><span id="CPV"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Cape_Verde.svg/22px-Flag_of_Cape_Verde.svg.png" decoding="async" width="22" height="13" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Cape_Verde.svg/33px-Flag_of_Cape_Verde.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Cape_Verde.svg/44px-Flag_of_Cape_Verde.svg.png 2x" data-file-width="1020" data-file-height="600" />&#160;<a href="/wiki/Cape_Verde_at_the_Olympics" title="Cape Verde at the Olympics">Cape Verde</a>&#160;<span style="font-size:90%;">(CPV)</span></span>
</td>
<td style="background:#f2f2ce;">7</td>
<td style="background:#cedff2;">0</td>
<td>7
</td></tr>
<tr>
<td align="left"><span id="CAY"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_the_Cayman_Islands.svg/22px-Flag_of_the_Cayman_Islands.svg.png" decoding="async" width="22" height="11" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_the_Cayman_Islands.svg/33px-Flag_of_the_Cayman_Islands.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_the_Cayman_Islands.svg/44px-Flag_of_the_Cayman_Islands.svg.png 2x" data-file-width="1200" data-file-height="600" />&#160;<a href="/wiki/Cayman_Islands_at_the_Olympics" title="Cayman Islands at the Olympics">Cayman Islands</a>&#160;<span style="font-size:90%;">(CAY)</span></span>
</td>
<td style="background:#f2f2ce;">11</td>
<td style="background:#cedff2;">2</td>
<td>13
</td></tr>
<tr>
<td align="left"><span id="CAF"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Central_African_Republic.svg/22px-Flag_of_the_Central_African_Republic.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Central_African_Republic.svg/33px-Flag_of_the_Central_African_Republic.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Central_African_Republic.svg/44px-Flag_of_the_Central_African_Republic.svg.png 2x" data-file-width="900" data-file-height="600" />&#160;<a href="/wiki/Central_African_Republic_at_the_Olympics" title="Central African Republic at the Olympics">Central African Republic</a>&#160;<span style="font-size:90%;">(CAF)</span></span>
</td>
<td style="background:#f2f2ce;">11</td>
<td style="background:#cedff2;">0</td>
<td>11
</td></tr>
<tr>
<td align="left"><span id="CHA"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Chad.svg/22px-Flag_of_Chad.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Chad.svg/33px-Flag_of_Chad.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Chad.svg/44px-Flag_of_Chad.svg.png 2x" data-file-width="900" data-file-height="600" />&#160;<a href="/wiki/Chad_at_the_Olympics" title="Chad at the Olympics">Chad</a>&#160;<span style="font-size:90%;">(CHA)</span></span>
</td>
<td style="background:#f2f2ce;">13</td>
<td style="background:#cedff2;">0</td>
<td>13
</td></tr>
<tr>
<td align="left"><span id="COM"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/94/Flag_of_the_Comoros.svg/22px-Flag_of_the_Comoros.svg.png" decoding="async" width="22" height="13" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/94/Flag_of_the_Comoros.svg/33px-Flag_of_the_Comoros.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/94/Flag_of_the_Comoros.svg/44px-Flag_of_the_Comoros.svg.png 2x" data-file-width="1000" data-file-height="600" />&#160;<a href="/wiki/Comoros_at_the_Olympics" title="Comoros at the Olympics">Comoros</a>&#160;<span style="font-size:90%;">(COM)</span></span>
</td>
<td style="background:#f2f2ce;">7</td>
<td style="background:#cedff2;">0</td>
<td>7
</td></tr>
<tr>
<td align="left"><span id="CGO"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_the_Republic_of_the_Congo.svg/22px-Flag_of_the_Republic_of_the_Congo.svg.png" decoding="async" width="22" height="15" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_the_Republic_of_the_Congo.svg/33px-Flag_of_the_Republic_of_the_Congo.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_the_Republic_of_the_Congo.svg/44px-Flag_of_the_Republic_of_the_Congo.svg.png 2x" data-file-width="900" data-file-height="600" />&#160;<a href="/wiki/Republic_of_the_Congo_at_the_Olympics" title="Republic of the Congo at the Olympics">Republic of the Congo</a>&#160;<span style="font-size:90%;">(CGO)</span></span>
</td>
<td style="background:#f2f2ce;">13</td>
<td style="background:#cedff2;">0</td>
<td>13
</td></tr>
<tr>
<td align="left"><span id="COD"><img alt="" src="//upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Democratic_Republic_of_the_Congo.svg/22px-Flag_of_the_Democratic_Republic_of_the_Congo.svg.png" decoding="async" width="22" height="17" class="thumbborder" srcset="//upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Democratic_Republic_of_the_Congo.svg/33px-Flag_of_the_Democratic_Republic_of_the_Congo.svg.png 1.5x, //upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Democratic_Republic_of_the_Congo.svg/44px-Flag_of_the_Democratic_Republic_of_the_Congo.svg.png 2x" data-file-width="800" data-file-height="600" />&#160;<a href="/wiki/Democratic_Republic_of_the_Congo_at_the_Olympics" title="Democratic Republic of the Congo at the Olympics">Democratic Republic of the Congo</a>&#160;<span style="font-size:90%;">(COD)</span></span> <sup class="reference" id="ref_CODCOD"><a href="#endnote_CODCOD">[COD]</a></sup>
</td>
<td style="background:#f2f2ce;">11</td>
<td style="background:#cedff2;">0</td>
<td>11
</td></tr>
"""

infer_nodes = [Node(text=infer_text)]

```

infer_text = """ ![](https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Flag_of_Bangladesh.svg/22px-Flag_of_Bangladesh.svg.png) Bangladesh (BAN) 10 0 10 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Flag_of_Belize.svg/22px-Flag_of_Belize.svg.png) Belize (BIZ) [BIZ] 13 0 13 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/Flag_of_Benin.svg/22px-Flag_of_Benin.svg.png) Benin (BEN) [BEN] 12 0 12 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Flag_of_Bhutan.svg/22px-Flag_of_Bhutan.svg.png) Bhutan (BHU) 10 0 10 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Flag_of_Bolivia.svg/22px-Flag_of_Bolivia.svg.png) Bolivia (BOL) 15 7 22 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Flag_of_Bosnia_and_Herzegovina.svg/22px-Flag_of_Bosnia_and_Herzegovina.svg.png) Bosnia and Herzegovina (BIH) 8 8 16 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/4/42/Flag_of_the_British_Virgin_Islands.svg/22px-Flag_of_the_British_Virgin_Islands.svg.png) British Virgin Islands (IVB) 10 2 12 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Flag_of_Brunei.svg/22px-Flag_of_Brunei.svg.png) Brunei (BRU) [A] 6 0 6 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Flag_of_Cambodia.svg/22px-Flag_of_Cambodia.svg.png) Cambodia (CAM) 10 0 10 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Flag_of_Cape_Verde.svg/22px-Flag_of_Cape_Verde.svg.png) Cape Verde (CPV) 7 0 7 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/Flag_of_the_Cayman_Islands.svg/22px-Flag_of_the_Cayman_Islands.svg.png) Cayman Islands (CAY) 11 2 13 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Central_African_Republic.svg/22px-Flag_of_the_Central_African_Republic.svg.png) Central African Republic (CAF) 11 0 11 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Flag_of_Chad.svg/22px-Flag_of_Chad.svg.png) Chad (CHA) 13 0 13 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Flag_of_the_Comoros.svg/22px-Flag_of_the_Comoros.svg.png) Comoros (COM) 7 0 7 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/Flag_of_the_Republic_of_the_Congo.svg/22px-Flag_of_the_Republic_of_the_Congo.svg.png) Republic of the Congo (CGO) 13 0 13 ![](https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Flag_of_the_Democratic_Republic_of_the_Congo.svg/22px-Flag_of_the_Democratic_Republic_of_the_Congo.svg.png) Democratic Republic of the Congo (COD) [COD] 11 0 11 """ infer_nodes = [Node(text=infer_text)]
In [ ]:
Copied!
```
from llama_index.core.program.predefined import MultiValueEvaporateProgram

program = MultiValueEvaporateProgram.from_defaults(
    fields_to_extract=["countries", "medal_count"],
)

```

from llama_index.core.program.predefined import MultiValueEvaporateProgram program = MultiValueEvaporateProgram.from_defaults( fields_to_extract=["countries", "medal_count"], )
In [ ]:
Copied!
```
program.fit_fields(train_nodes[:1])

```

program.fit_fields(train_nodes[:1])
Out[ ]:
```
{'countries': 'def get_countries_field(text: str):\n    """\n    Function to extract countries. \n    """\n    \n    # Use regex to extract the countries field\n    countries_field = re.findall(r\'<a href=".*">(.*)</a>\', text)\n    \n    # Return the result as a list\n    return countries_field',
 'medal_count': 'def get_medal_count_field(text: str):\n    """\n    Function to extract medal_count. \n    """\n    \n    # Use regex to extract the medal count field\n    medal_count_field = re.findall(r\'<td style="background:#f2f2ce;">(.*?)</td>\', text)\n    \n    # Return the result as a list\n    return medal_count_field'}
```

In [ ]:
Copied!
```
print(program.get_function_str("countries"))

```

print(program.get_function_str("countries"))
```
def get_countries_field(text: str):
    """
    Function to extract countries. 
    """
    
    # Use regex to extract the countries field
    countries_field = re.findall(r'<a href=".*">(.*)</a>', text)
    
    # Return the result as a list
    return countries_field

```

In [ ]:
Copied!
```
print(program.get_function_str("medal_count"))

```

print(program.get_function_str("medal_count"))
```
def get_medal_count_field(text: str):
    """
    Function to extract medal_count. 
    """
    
    # Use regex to extract the medal count field
    medal_count_field = re.findall(r'<td style="background:#f2f2ce;">(.*?)</td>', text)
    
    # Return the result as a list
    return medal_count_field

```

In [ ]:
Copied!
```
result = program(nodes=infer_nodes[:1])

```

result = program(nodes=infer_nodes[:1])
In [ ]:
Copied!
```
# output countries
print(f"Countries: {result.columns[0].row_values}\n")
# output medal counts
print(f"Medal Counts: {result.columns[0].row_values}\n")

```

# output countries print(f"Countries: {result.columns[0].row_values}\n") # output medal counts print(f"Medal Counts: {result.columns[0].row_values}\n")
```
Countries: ['Bangladesh', '[BIZ]', '[BEN]', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'British Virgin Islands', '[A]', 'Cambodia', 'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad', 'Comoros', 'Republic of the Congo', '[COD]']

Medal Counts: ['Bangladesh', '[BIZ]', '[BEN]', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'British Virgin Islands', '[A]', 'Cambodia', 'Cape Verde', 'Cayman Islands', 'Central African Republic', 'Chad', 'Comoros', 'Republic of the Congo', '[COD]']


```

## Bonus: Use the underlying `EvaporateExtractor`¶
The underlying `EvaporateExtractor` offers some additional functionality, e.g. actually helping to identify fields over a set of text.
Here we show how you can use `identify_fields` to determine relevant fields around a general `topic` field.
In [ ]:
Copied!
```
# a list of nodes, one node per city, corresponding to intro paragraph
# city_pop_nodes = []
city_pop_nodes = [city_nodes["Toronto"][0], city_nodes["Seattle"][0]]

```

# a list of nodes, one node per city, corresponding to intro paragraph # city_pop_nodes = [] city_pop_nodes = [city_nodes["Toronto"][0], city_nodes["Seattle"][0]]
In [ ]:
Copied!
```
extractor = program.extractor

```

extractor = program.extractor
In [ ]:
Copied!
```
# Try with Toronto and Seattle (should extract "population")
existing_fields = extractor.identify_fields(
    city_pop_nodes, topic="population", fields_top_k=4
)

```

# Try with Toronto and Seattle (should extract "population") existing_fields = extractor.identify_fields( city_pop_nodes, topic="population", fields_top_k=4 )
In [ ]:
Copied!
```
existing_fields

```

existing_fields
Out[ ]:
```
["seattle metropolitan area's population"]
```

