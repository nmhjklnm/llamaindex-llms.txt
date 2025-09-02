![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Slack Reader¶
Demonstrates our Slack data connector
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-slack

```

%pip install llama-index-readers-slack
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
from llama_index.core import SummaryIndex
from llama_index.readers.slack import SlackReader
from IPython.display import Markdown, display
import os

```

from llama_index.core import SummaryIndex from llama_index.readers.slack import SlackReader from IPython.display import Markdown, display import os
Load data using Channel IDs
In [ ]:
Copied!
```
slack_token = os.getenv("SLACK_BOT_TOKEN")
channel_ids = ["<channel_id>"]
documents = SlackReader(slack_token=slack_token).load_data(
    channel_ids=channel_ids
)

```

slack_token = os.getenv("SLACK_BOT_TOKEN") channel_ids = [""] documents = SlackReader(slack_token=slack_token).load_data( channel_ids=channel_ids )
Load data using Channel Names/Regex Patterns
In [ ]:
Copied!
```
slack_token = os.getenv("SLACK_BOT_TOKEN")
channel_patterns = ["<channel_name>", "<regex_pattern>"]
slack_reader = SlackReader(slack_token=slack_token)
channel_ids = slack_reader.get_channel_ids(channel_patterns=channel_patterns)
documents = slack_reader.load_data(channel_ids=channel_ids)

```

slack_token = os.getenv("SLACK_BOT_TOKEN") channel_patterns = ["", ""] slack_reader = SlackReader(slack_token=slack_token) channel_ids = slack_reader.get_channel_ids(channel_patterns=channel_patterns) documents = slack_reader.load_data(channel_ids=channel_ids)
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
