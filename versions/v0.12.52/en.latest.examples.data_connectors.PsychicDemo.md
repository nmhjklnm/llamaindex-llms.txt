![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Psychic Reader¶
Demonstrates the Psychic data connector. Used to query data from many SaaS tools from a single LlamaIndex-compatible API.
## Prerequisites¶
Connections must first be established from the Psychic dashboard or React hook before documents can be loaded. Refer to https://docs.psychic.dev/ for more info.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-readers-psychic

```

%pip install llama-index-readers-psychic
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
import os

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys import os logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
In [ ]:
Copied!
```
from llama_index.core import SummaryIndex
from llama_index.readers.psychic import PsychicReader
from IPython.display import Markdown, display

```

from llama_index.core import SummaryIndex from llama_index.readers.psychic import PsychicReader from IPython.display import Markdown, display
In [ ]:
Copied!
```
# Get Psychic API key from https://dashboard.psychic.dev/api-keys
psychic_key = "PSYCHIC_API_KEY"
# Connector ID and Account ID are typically set programmatically based on the application state.
account_id = "ACCOUNT_ID"
connector_id = "notion"
documents = PsychicReader(psychic_key=psychic_key).load_data(
    connector_id=connector_id, account_id=account_id
)

```

# Get Psychic API key from https://dashboard.psychic.dev/api-keys psychic_key = "PSYCHIC_API_KEY" # Connector ID and Account ID are typically set programmatically based on the application state. account_id = "ACCOUNT_ID" connector_id = "notion" documents = PsychicReader(psychic_key=psychic_key).load_data( connector_id=connector_id, account_id=account_id )
In [ ]:
Copied!
```
# set Logging to DEBUG for more detailed outputs
os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY"
index = SummaryIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("What is Psychic's privacy policy?")
display(Markdown(f"<b>{response}</b>"))

```

# set Logging to DEBUG for more detailed outputs os.environ["OPENAI_API_KEY"] = "OPENAI_API_KEY" index = SummaryIndex.from_documents(documents) query_engine = index.as_query_engine() response = query_engine.query("What is Psychic's privacy policy?") display(Markdown(f"**{response}** "))
```
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
> [build_index_from_nodes] Total LLM token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [build_index_from_nodes] Total embedding token usage: 0 tokens
> [build_index_from_nodes] Total embedding token usage: 0 tokens
> [build_index_from_nodes] Total embedding token usage: 0 tokens
> [build_index_from_nodes] Total embedding token usage: 0 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total LLM token usage: 2383 tokens
> [get_response] Total LLM token usage: 2383 tokens
> [get_response] Total LLM token usage: 2383 tokens
> [get_response] Total LLM token usage: 2383 tokens
INFO:llama_index.token_counter.token_counter:> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens
> [get_response] Total embedding token usage: 0 tokens

```

**Psychic's privacy policy explains how we access, use, store, and share Google user data when you connect your Google Drive or other Google services to our application. By using Psychic, you agree to this Privacy Policy and our Terms of Service. We use the information we collect for the following purposes: to provide you with the Psychic services, including allowing you to access, view, and query files and folders stored in your connected Google Drive; to improve our services, including analyzing usage patterns and troubleshooting issues; and to communicate with you about important updates, promotions, or news related to Psychic. We take the security of your information seriously and implement appropriate security measures to protect it. We may share your information in certain cases, such as with service providers who assist us in providing and maintaining Psychic services, as required by law, or to protect the rights, property, or safety of Psychic, our users, or the public. Psychic provides in-product privacy notifications to inform you about the ways we access, use, store, and share your Google user data. We may update this Privacy Policy from time to time, and your continued use of Psychic after any changes to this Privacy Policy constitutes your acceptance of the updated policy.**
