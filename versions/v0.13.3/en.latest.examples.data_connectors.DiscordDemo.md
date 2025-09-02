![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Discord Reader¶
Demonstrates our Discord data connector
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-discord

```

%pip install llama-index-readers-discord
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
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
# This is due to the fact that we use asyncio.loop_until_complete in
# the DiscordReader. Since the Jupyter kernel itself runs on
# an event loop, we need to add some help with nesting
!pip install nest_asyncio
import nest_asyncio

nest_asyncio.apply()

```

# This is due to the fact that we use asyncio.loop_until_complete in # the DiscordReader. Since the Jupyter kernel itself runs on # an event loop, we need to add some help with nesting !pip install nest_asyncio import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
from llama_index.core import SummaryIndex
from llama_index.readers.discord import DiscordReader
from IPython.display import Markdown, display
import os

```

from llama_index.core import SummaryIndex from llama_index.readers.discord import DiscordReader from IPython.display import Markdown, display import os
In [ ]:
Copied!
```
discord_token = os.getenv("DISCORD_TOKEN")
channel_ids = [1057178784895348746]  # Replace with your channel_id
documents = DiscordReader(discord_token=discord_token).load_data(
    channel_ids=channel_ids
)

```

discord_token = os.getenv("DISCORD_TOKEN") channel_ids = [1057178784895348746] # Replace with your channel_id documents = DiscordReader(discord_token=discord_token).load_data( channel_ids=channel_ids )
In [ ]:
Copied!
```
index = SummaryIndex.from_documents(documents)

```

index = SummaryIndex.from_documents(documents)
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("<query_text>")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
