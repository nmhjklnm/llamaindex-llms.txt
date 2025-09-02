# Zyte Serp Reader¶
Zyte Serp Reader allows you to access the organic results from google search. Given a query string, it provides the URLs of the top search results and the text string associated with those.
In [ ]:
Copied!
```
# %pip install llama-index llama-index-readers-zyte-serp

```

# %pip install llama-index llama-index-readers-zyte-serp
In this notebook we show how Zyte Serp Reader (along with web reader) can be used collect information about a particular topic. Given these documents we can perform queries on this topic.
Recently the Govt. of Ireland announced fiscal budget for 2024 and here we show how we can query information regarding the budget. First we get the relevant information using the Zyte Serp Reader, then the information from these URLs is extracted using web reader and finally a queries are answered using a openai chatgpt model.
In [ ]:
Copied!
```
import os
from llama_index.readers.zyte_serp import ZyteSerpReader
from llama_index.readers.web.zyte_web.base import ZyteWebReader

```

import os from llama_index.readers.zyte_serp import ZyteSerpReader from llama_index.readers.web.zyte_web.base import ZyteWebReader
In [ ]:
Copied!
```
# This is needed to run it in juypter notebook
# import nest_asyncio
# nest_asyncio.apply()

```

# This is needed to run it in juypter notebook # import nest_asyncio # nest_asyncio.apply()
In [ ]:
Copied!
```
zyte_api_key = os.environ.get("ZYTE_API_KEY")

```

zyte_api_key = os.environ.get("ZYTE_API_KEY")
### Get relevant resources (using ZyteSerp)¶
Given a topic, we use the search results from google to get the links to the relevant pages.
In [ ]:
Copied!
```
topic = "Ireland Budget 2025"

```

topic = "Ireland Budget 2025"
In [ ]:
Copied!
```
serp_reader = ZyteSerpReader(api_key=zyte_api_key)

```

serp_reader = ZyteSerpReader(api_key=zyte_api_key)
In [ ]:
Copied!
```
search_results = serp_reader.load_data(topic)

```

search_results = serp_reader.load_data(topic)
In [ ]:
Copied!
```
len(search_results)

```

len(search_results)
Out[ ]:


In [ ]:
Copied!
```
for r in search_results[:4]:
    print(r.text)
    print(r.metadata)

```

for r in search_results[:4]: print(r.text) print(r.metadata)
```
https://www.gov.ie/en/publication/e8315-budget-2025/
{'name': 'Budget 2025', 'rank': 1}
https://www.citizensinformation.ie/en/money-and-tax/budgets/budget-2025/
{'name': 'Budget 2025', 'rank': 2}
https://www.gov.ie/en/publication/cb193-your-guide-to-budget-2025/
{'name': 'Your guide to Budget 2025', 'rank': 3}
https://www.irishtimes.com/your-money/2024/10/01/budget-2025-ireland-main-points/
{'name': 'Budget 2025 main points: Energy credits, bonus welfare ...', 'rank': 4}

```

In [ ]:
Copied!
```
urls = [r.text for r in search_results]

```

urls = [r.text for r in search_results]
Seems we have a list of relevant URL with regard to our topic ("Ireland budget 2024"). Metadata also shows the text and rank associated with the search result entry. Next we get the content of these webpages using web reader.
### Get topic content¶
Given the urls of the webpages which contain information about the topic, we get the content. Since the webpages contain a lot of non-relevant content, we can obtain the filtered content using the "article" mode of the ZyteWebReader which returns only the article content of from the webpage.
In [ ]:
Copied!
```
web_reader = ZyteWebReader(api_key=zyte_api_key, mode="article")
documents = web_reader.load_data(urls)

```

web_reader = ZyteWebReader(api_key=zyte_api_key, mode="article") documents = web_reader.load_data(urls)
In [ ]:
Copied!
```
print(documents[0].text[:200])

```

print(documents[0].text[:200])
```
Budget 2025 - Tax Highlights Ireland

Budget 2025 announced on 1 October 2024 included a substantial "cost-of-living" package including many one-off payments, as well as outlining a framework to direc

```

In [ ]:
Copied!
```
len(documents)

```

len(documents)
Out[ ]:


### Query engine¶
Here a very basic query is performed using VectorStoreIndex. Please make sure that the OPENAI_API_KEY env variable is set before running the following code.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
query_engine = index.as_query_engine()
response = query_engine.query(
    "What kind of energy credits are provided in the budget?"
)
print(response)

```

query_engine = index.as_query_engine() response = query_engine.query( "What kind of energy credits are provided in the budget?" ) print(response)
```
Two €125 electricity credits will be provided - one this year and one in 2025.

```

