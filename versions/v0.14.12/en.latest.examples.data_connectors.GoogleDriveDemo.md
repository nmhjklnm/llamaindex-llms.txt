![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Google Drive Reader¶
Demonstrates our Google Drive data connector
## Prerequisites¶
Follow these steps to setup your environment.
  1. Enable the Google Drive API in your GCP project.
  2. Configure an OAuth Consent screen for your GCP project.
     * It is fine to make it "External" if you're not in a Google Workspace.
  3. Create client credentials for your application (this notebook).
     * Make sure to use "Desktop app" as the application type.
     * Move these client credentials to the directory this notebook is in, and name it "credentials.json".


If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index llama-index-readers-google

```

%pip install llama-index llama-index-readers-google
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
from llama_index.core import SummaryIndex
from llama_index.readers.google import GoogleDriveReader
from IPython.display import Markdown, display

```

from llama_index.core import SummaryIndex from llama_index.readers.google import GoogleDriveReader from IPython.display import Markdown, display
## Choose Folder to Read¶
You can find a folder ID by navigating to a folder in Google Drive then selecting the last part of the URL.
For example, with this URL: `https://drive.google.com/drive/u/0/folders/abcdefgh12345678` the folder ID is `abcdefgh12345678`
In [ ]:
Copied!
```
# Replace the placeholder with your chosen folder ID
folder_id = ["<your_folder_id>"]

# Make sure credentials.json file exists in the current directory (data_connectors)
documents = GoogleDriveReader().load_data(folder_id=folder_id)

```

# Replace the placeholder with your chosen folder ID folder_id = [""] # Make sure credentials.json file exists in the current directory (data_connectors) documents = GoogleDriveReader().load_data(folder_id=folder_id)
In [ ]:
Copied!
```
index = SummaryIndex.from_documents(documents)

```

index = SummaryIndex.from_documents(documents)
In [ ]:
Copied!
```
# Set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("<query_text>")

```

# Set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
