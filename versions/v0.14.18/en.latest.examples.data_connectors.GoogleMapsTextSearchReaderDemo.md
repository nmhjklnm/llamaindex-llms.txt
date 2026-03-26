![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Google Maps Text Search Reader¶
This notebook demonstrates how to use the GoogleMapsTextSearchReader from the llama_index library to load and query data from the Google Maps Places API.
If you're opening this Notebook on colab, you will need to install the llama-index library.
In [ ]:
Copied!
```
!pip install llama-index llama-index-readers-google

```

!pip install llama-index llama-index-readers-google
### Importing Necessary Libraries¶
We will import the necessary libraries including the GoogleMapsTextSearchReader from llama_index and other utility libraries.
In [ ]:
Copied!
```
import logging
import sys
from llama_index.readers.google import GoogleMapsTextSearchReader
from llama_index.core import VectorStoreIndex
from IPython.display import Markdown, display
import os

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys from llama_index.readers.google import GoogleMapsTextSearchReader from llama_index.core import VectorStoreIndex from IPython.display import Markdown, display import os logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
### Setting Up API Key¶
Make sure you have your Google Maps API key ready. You can set it directly in the code or store it in an environment variable named `GOOGLE_MAPS_API_KEY`.
In [ ]:
Copied!
```
# Set your API key here if not using environment variable
os.environ["GOOGLE_MAPS_API_KEY"] = api_key

```

# Set your API key here if not using environment variable os.environ["GOOGLE_MAPS_API_KEY"] = api_key
### Loading Data from Google Maps¶
Using the `GoogleMapsTextSearchReader`, we will load data for a search query. In this example, we search for quality Turkish food in Istanbul.
In [ ]:
Copied!
```
loader = GoogleMapsTextSearchReader()
documents = loader.load_data(
    text="I want to eat quality Turkish food in Istanbul",
    number_of_results=160,
)

# Displaying the first document to understand its structure
print(documents[0])

```

loader = GoogleMapsTextSearchReader() documents = loader.load_data( text="I want to eat quality Turkish food in Istanbul", number_of_results=160, ) # Displaying the first document to understand its structure print(documents[0])
### Indexing the Loaded Data¶
We will now create a VectorStoreIndex from the loaded documents. This index will allow us to perform efficient queries on the data.
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents)

```

index = VectorStoreIndex.from_documents(documents)
### Querying the Index¶
Finally, we will query the index to find the Turkish restaurant with the best reviews.
In [ ]:
Copied!
```
response = index.query("Which Turkish restaurant has the best reviews?")
display(Markdown(f"<b>{response}</b>"))

```

response = index.query("Which Turkish restaurant has the best reviews?") display(Markdown(f"**{response}** "))
### Summary¶
In this notebook, we demonstrated how to use the GoogleMapsTextSearchReader to load data from Google Maps, index it using the VectorStoreIndex, and perform a query to find the best-reviewed Turkish restaurant in Istanbul.
