# Deplot Reader Demo¶
In this notebook we showcase the capabilities of our ImageTabularChartReader, which is powered by the DePlot model https://arxiv.org/abs/2212.10505.
In [ ]:
Copied!
```
%pip install llama-index-readers-file

```

%pip install llama-index-readers-file
In [ ]:
Copied!
```
from llama_index.readers.file import ImageTabularChartReader
from llama_index.core import SummaryIndex
from llama_index.core.response.notebook_utils import display_response
from pathlib import Path

```

from llama_index.readers.file import ImageTabularChartReader from llama_index.core import SummaryIndex from llama_index.core.response.notebook_utils import display_response from pathlib import Path
In [ ]:
Copied!
```
loader = ImageTabularChartReader(keep_image=True)

```

loader = ImageTabularChartReader(keep_image=True)
## Load Protected Waters Chart¶
This chart shows the percentage of marine territorial waters that are protected for each country.
In [ ]:
Copied!
```
documents = loader.load_data(file=Path("./marine_chart.png"))

```

documents = loader.load_data(file=Path("./marine_chart.png"))
In [ ]:
Copied!
```
print(documents[0].text)

```

print(documents[0].text)
```
Figure or chart with tabular data: Country | Share of marine territorial waters that are protected, 2016 <0x0A> Greenland | 4.52 <0x0A> Mauritania | 4.15 <0x0A> Indonesia | 2.88 <0x0A> Ireland | 2.33

```

In [ ]:
Copied!
```
summary_index = SummaryIndex.from_documents(documents)
response = summary_index.as_query_engine().query(
    "What is the difference between the shares of Greenland and the share of"
    " Mauritania?"
)

```

summary_index = SummaryIndex.from_documents(documents) response = summary_index.as_query_engine().query( "What is the difference between the shares of Greenland and the share of" " Mauritania?" )
```
Retrying langchain.llms.openai.completion_with_retry.<locals>._completion_with_retry in 4.0 seconds as it raised APIConnectionError: Error communicating with OpenAI: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')).

```

In [ ]:
Copied!
```
display_response(response, show_source=True)

```

display_response(response, show_source=True)
## Load Pew Research Chart¶
Here we load in a Pew Research chart showing international views of the US/Biden.
Source: https://www.pewresearch.org/global/2023/06/27/international-views-of-biden-and-u-s-largely-positive/
In [ ]:
Copied!
```
documents = loader.load_data(file=Path("./pew1.png"))

```

documents = loader.load_data(file=Path("./pew1.png"))
In [ ]:
Copied!
```
print(documents[0].text)

```

print(documents[0].text)
```
Figure or chart with tabular data: Entity | Values <0x0A> Does not | 50.0 <0x0A> % who say the U.S take into account the interests of countries like theirs | 49.0 <0x0A> Does not | 38.0 <0x0A> % who say the U.S contribute to peace and stability around the world | 61.0 <0x0A> Does not | 15.0 <0x0A> % who say the U.S interfere in the affairs of other countries | 15.0 <0x0A>% who have confidence | 54.0 <0x0A> Views of President Biden | 30.0 <0x0A> Favorable | 59.0 <0x0A> Views of the U.S. | 9.0

```

In [ ]:
Copied!
```
summary_index = SummaryIndex.from_documents(documents)
response = summary_index.as_query_engine().query(
    "What percentage says that the US contributes to peace and stability?"
)

```

summary_index = SummaryIndex.from_documents(documents) response = summary_index.as_query_engine().query( "What percentage says that the US contributes to peace and stability?" )
In [ ]:
Copied!
```
display_response(response, show_source=True)

```

display_response(response, show_source=True)
