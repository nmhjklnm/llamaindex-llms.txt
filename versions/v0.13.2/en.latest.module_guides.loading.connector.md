# Data Connectors (LlamaHub)#
## Concept#
A data connector (aka `Reader`) ingest data from different data sources and data formats into a simple `Document` representation (text and simple metadata).
Tip
Once you've ingested your data, you can build an Index on top, ask questions using a Query Engine, and have a conversation using a Chat Engine.
## LlamaHub#
Our data connectors are offered through LlamaHub 🦙. LlamaHub is an open-source repository containing data loaders that you can easily plug and play into any LlamaIndex application.
![](https://docs.llamaindex.ai/en/latest/_static/data_connectors/llamahub.png)
## Usage Pattern#
Get started with:
```
from llama_index.core import download_loader

from llama_index.readers.google import GoogleDocsReader

loader = GoogleDocsReader()
documents = loader.load_data(document_ids=[...])

```

See the full usage pattern guide for more details.
## Modules#
Some sample data connectors:
  * local file directory (`SimpleDirectoryReader`). Can support parsing a wide range of file types: `.pdf`, `.jpg`, `.png`, `.docx`, etc.
  * Notion (`NotionPageReader`)
  * Google Docs (`GoogleDocsReader`)
  * Slack (`SlackReader`)
  * Discord (`DiscordReader`)
  * Apify Actors (`ApifyActor`). Can crawl the web, scrape webpages, extract text content, download files including `.pdf`, `.jpg`, `.png`, `.docx`, etc.


See the modules guide for more details.
