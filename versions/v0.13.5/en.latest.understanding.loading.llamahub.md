# LlamaHub#
Our data connectors are offered through LlamaHub 🦙. LlamaHub contains a registry of open-source data connectors that you can easily plug into any LlamaIndex application (+ Agent Tools, and Llama Packs).
![](https://docs.llamaindex.ai/en/latest/_static/data_connectors/llamahub.png)
## Usage Pattern#
Get started with:
```
from llama_index.core import download_loader

from llama_index.readers.google import GoogleDocsReader

loader = GoogleDocsReader()
documents = loader.load_data(document_ids=[...])

```

## Built-in connector: SimpleDirectoryReader#
`SimpleDirectoryReader`. Can support parsing a wide range of file types including `.md`, `.pdf`, `.jpg`, `.png`, `.docx`, as well as audio and video types. It is available directly as part of LlamaIndex:
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()

```

## Available connectors#
Browse LlamaHub directly to see the hundreds of connectors available, including:
  * Notion (`NotionPageReader`)
  * Google Docs (`GoogleDocsReader`)
  * Slack (`SlackReader`)
  * Discord (`DiscordReader`)
  * Apify Actors (`ApifyActor`). Can crawl the web, scrape webpages, extract text content, download files including `.pdf`, `.jpg`, `.png`, `.docx`, etc.


