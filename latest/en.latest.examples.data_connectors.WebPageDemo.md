![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Web Page Reader¶
Demonstrates our web page reader.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index llama-index-readers-web

```

%pip install llama-index llama-index-readers-web
In [ ]:
Copied!
```
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

```

import logging import sys logging.basicConfig(stream=sys.stdout, level=logging.INFO) logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
#### Using SimpleWebPageReader¶
In [ ]:
Copied!
```
from llama_index.core import SummaryIndex
from llama_index.readers.web import SimpleWebPageReader
from IPython.display import Markdown, display
import os

```

from llama_index.core import SummaryIndex from llama_index.readers.web import SimpleWebPageReader from IPython.display import Markdown, display import os
In [ ]:
Copied!
```
# NOTE: the html_to_text=True option requires html2text to be installed

```

# NOTE: the html_to_text=True option requires html2text to be installed
In [ ]:
Copied!
```
documents = SimpleWebPageReader(html_to_text=True).load_data(
    ["http://paulgraham.com/worked.html"]
)

```

documents = SimpleWebPageReader(html_to_text=True).load_data( ["http://paulgraham.com/worked.html"] )
In [ ]:
Copied!
```
documents[0]

```

documents[0]
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
response = query_engine.query("What did the author do growing up?")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
# Using Spider Reader 🕷¶
Spider is the fastest crawler. It converts any website into pure HTML, markdown, metadata or text while enabling you to crawl with custom actions using AI.
Spider allows you to use high performance proxies to prevent detection, caches AI actions, webhooks for crawling status, scheduled crawls etc...
**Prerequisites:** you need to have a Spider api key to use this loader. You can get one on spider.cloud.
In [ ]:
Copied!
```
# Scrape single URL
from llama_index.readers.web import SpiderWebReader

spider_reader = SpiderWebReader(
    api_key="YOUR_API_KEY",  # Get one at https://spider.cloud
    mode="scrape",
    # params={} # Optional parameters see more on https://spider.cloud/docs/api
)

documents = spider_reader.load_data(url="https://spider.cloud")
print(documents)

```

# Scrape single URL from llama_index.readers.web import SpiderWebReader spider_reader = SpiderWebReader( api_key="YOUR_API_KEY", # Get one at https://spider.cloud mode="scrape", # params={} # Optional parameters see more on https://spider.cloud/docs/api ) documents = spider_reader.load_data(url="https://spider.cloud") print(documents)
```
[Document(id_='54a6ecf3-b33e-41e9-8cec-48657aa2ed9b', embedding=None, metadata={'description': 'Collect data rapidly from any website. Seamlessly scrape websites and get data tailored for LLM workloads.', 'domain': 'spider.cloud', 'extracted_data': None, 'file_size': 101750, 'keywords': None, 'pathname': '/', 'resource_type': 'html', 'title': 'Spider - Fastest Web Crawler', 'url': '48f1bc3c-3fbb-408a-865b-c191a1bb1f48/spider.cloud/index.html', 'user_id': '48f1bc3c-3fbb-408a-865b-c191a1bb1f48'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text='Spider - Fastest Web Crawler[Spider v1 Logo Spider ](/)[Pricing](/credits/new)[GitHubGithub637](https://github.com/spider-rs/spider)The World\'s Fastest and Cheapest Crawler API==========View Demo* Basic* StreamingExample requestPythonCopy```import requests, osheaders = {    \'Authorization\': os.environ["SPIDER_API_KEY"],    \'Content-Type\': \'application/json\',}json_data = {"limit":50,"url":"http://www.example.com"}response = requests.post(\'https://api.spider.cloud/crawl\',  headers=headers,  json=json_data)print(response.json())

Crawl domain following all deeper subpages
In [ ]:
Copied!
```
# Crawl domain with deeper crawling following subpages
from llama_index.readers.web import SpiderWebReader

spider_reader = SpiderWebReader(
    api_key="YOUR_API_KEY",
    mode="crawl",
    # params={} # Optional parameters see more on https://spider.cloud/docs/api
)

documents = spider_reader.load_data(url="https://spider.cloud")
print(documents)

```

# Crawl domain with deeper crawling following subpages from llama_index.readers.web import SpiderWebReader spider_reader = SpiderWebReader( api_key="YOUR_API_KEY", mode="crawl", # params={} # Optional parameters see more on https://spider.cloud/docs/api ) documents = spider_reader.load_data(url="https://spider.cloud") print(documents)
```
[Document(id_='63f7ccbf-c6c8-4f69-80f7-f6763f761a39', embedding=None, metadata={'description': 'Our privacy policy and how it plays a part in the data collected.', 'domain': 'spider.cloud', 'extracted_data': None, 'file_size': 26647, 'keywords': None, 'pathname': '/privacy', 'resource_type': 'html', 'title': 'Privacy', 'url': '48f1bc3c-3fbb-408a-865b-c191a1bb1f48/spider.cloud/privacy.html', 'user_id': '48f1bc3c-3fbb-408a-865b-c191a1bb1f48'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text="Privacy[Spider v1 Logo Spider ](/) [Credits](/credits/new)[GitHubGithub637](https://github.com/spider-rs/spider)Privacy Policy==========Learn about how we take privacy with the Spider project.[Spider](https://spider.cloud) offers a cutting-edge data scraping service with powerful AI capabilities. Our data collecting platform is designed to help users maximize the benefits of data collection while embracing the advancements in AI technology. With our innovative tools, we provide a seamless and fast interactive experience. This privacy policy details Spider's approach to product development, deployment, and usage, encompassing the Crawler, AI products, and features.[AI Development at Spider----------](#ai-development-at-spider)Spider leverages a robust combination of proprietary code, open-source frameworks, and synthetic datasets to train its cutting-edge products. To continuously improve our offerings, Spider may utilize inputs from user-generated prompts and content, obtained from trusted third-party providers. By harnessing this diverse data, Spider can deliver highly precise and pertinent recommendations to our valued users. While the foundational data crawling aspect of Spider is openly available on Github, the dashboard and AI components remain closed source. Spider respects all robots.txt files declared on websites allowing data to be extracted without harming the website.[Security, Privacy, and Trust----------](#security-privacy-and-trust)At Spider, our utmost priority is the development and implementation of Crawlers, AI technologies, and products that adhere to ethical, moral, and legal standards. We are dedicated to creating a secure and respectful environment for all users. Safeguarding user data and ensuring transparency in its usage are core principles we uphold. In line with this commitment, we provide the following important disclosures when utilizing our AI-related products:* Spider ensures comprehensive disclosure of features that utilize third-party AI platforms. To provide clarity, these integrations will be clearly indicated through distinct markers, designations, explanatory notes that appear when hovering, references to the underlying codebase, or any other suitable form of notification as determined by the system. Our commitment to transparency aims to keep users informed about the involvement of third-party AI platforms in our products.* We collect and use personal data as set forth in our [Privacy Policy](https://spider.cloud/privacy) which governs the collection and usage of personal data. If you choose to input personal data into our AI products, please be aware that such information may be processed through third-party AI providers. For any inquiries or concerns regarding data privacy, feel free to reach out to us at [Spider Help Github](https://github.com/orgs/spider-rs/discussions). We are here to assist you.* Except for user-generated prompts and/or content as inputs, Spider does not use customer data, including the code related to the use of Spider's deployment services, to train or finetune any models used.* We periodically review and update our policies and procedures in an effort to comply with applicable data protection regulations and industry standards.* We use reasonable measures designed to maintain the safety of users and avoid harm to people and the environment. Spider's design and development process includes considerations for ethical, security, and regulatory requirements with certain safeguards to prevent and report misuse or abuse.[Third-Party Service Providers----------](#third-party-service-providers)In providing AI products and services, we leverage various third-party providers in the AI space to enhance our services and capabilities, and will continue to do so for certain product features.This page will be updated from time to time with information about Spider's use of AI. The current list of third-party AI providers integrated into Spider is as follows:* [Anthropic](https://console.anthropic.com/legal/terms)* [Azure Cognitive Services](https://learn.microsoft.com/en-us/legal/cognitive-services/openai/data-privacy)* [Cohere](https://cohere.com/terms-of-use)* [ElevenLabs](https://elevenlabs.io/terms)* [Hugging Face](https://huggingface.co/terms-of-service)* [Meta AI](https://www.facebook.com/policies_center/)* [OpenAI](https://openai.com/policies)* [Pinecone](https://www.pinecone.io/terms)* [Replicate](https://replicate.com/terms)We prioritize the safety of our users and take appropriate measures to avoid harm both to individuals and the environment. Our design and development processes incorporate considerations for ethical practices, security protocols, and regulatory requirements, along with established safeguards to prevent and report any instances of misuse or abuse. We are committed to maintaining a secure and respectful environment and upholding responsible practices throughout our services.[Acceptable Use----------](#acceptable-use)Spider's products are intended to provide helpful and respectful responses to user prompts and queries while collecting data along the web. We don't allow the use of our Scraper or AI tools, products and services for the following usages:* Denial of Service Attacks* Illegal activity* Inauthentic, deceptive, or impersonation behavior* Any other use that would violate Spider's standard published policies, codes of conduct, or terms of service.Any violation of this Spider AI Policy or any Spider policies or terms of service may result in termination of use of services at Spider's sole discretion. We will review and update this Spider AI Policy so that it remains relevant and effective. If you have feedback or would like to report any concerns or issues related to the use of AI systems, please reach out to [support@spider.cloud](mailto:support@spider.cloud).[More Information----------](#more-information)To learn more about Spider's integration of AI capabilities into products and features, check out the following resources:* [Spider-Rust](https://github.com/spider-rs)* [Spider](/)* [About](/)[API](/docs/api) [Pricing](/credits/new) [Guides](/guides) [About](/about) [Docs](https://docs.rs/spider/latest/spider/) [Privacy](/privacy) [Terms](/eula)© 2024 Spider from A11yWatchTheme Light Dark Toggle Theme [GitHubGithub](https://github.com/spider-rs/spider)", start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), Document(id_='18e4d35d-ff48-4d00-b924-abab7a06fbec', embedding=None, metadata={'description': 'Learn how to crawl and scrape websites with the fastest web crawler built for the job.', 'domain': 'spider.cloud', 'extracted_data': None, 'file_size': 27058, 'keywords': None, 'pathname': '/guides', 'resource_type': 'html', 'title': 'Spider Guides', 'url': '48f1bc3c-3fbb-408a-865b-c191a1bb1f48/spider.cloud/guides.html', 'user_id': '48f1bc3c-3fbb-408a-865b-c191a1bb1f48'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text='Spider Guides[Spider v1 Logo Spider ](/) [Credits](/credits/new)[GitHubGithub637](https://github.com/spider-rs/spider)Spider Guides==========Learn how to crawl and scrape websites easily.(4) Total Guides* [  Spider v1 Logo  Spider Platform  ----------  How to use the platform to collect data from the internet fast, affordable, and unblockable.  ](/guides/spider)* [  Spider v1 Logo  Spider API  ----------  How to use the Spider API to curate data from any source blazing fast. The most advanced crawler that handles all workloads of all sizes.  ](/guides/spider-api)* [  Spider v1 Logo  Extract Contacts  ----------  Get contact information from any website in real time with AI. The only way to accurately get dynamic information from websites.  ](/guides/pipelines-extract-contacts)* [  Spider v1 Logo  Website Archiving  ----------  The programmable time machine that can store pages and all assets for easy website archiving.  ](/guides/website-archiving)[API](/docs/api) [Pricing](/credits/new) [Guides](/guides) [About](/about) [Docs](https://docs.rs/spider/latest/spider/) [Privacy](/privacy) [Terms](/eula)© 2024 Spider from A11yWatchTheme Light Dark Toggle Theme [GitHubGithub](https://github.com/spider-rs/spider)', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), Document(id_='b10c6402-bc35-4fec-b97c-fa30bde54ce8', embedding=None, metadata={'description': 'Complete reference documentation for the Spider API. Includes code snippets and examples for quickly getting started with the system.', 'domain': 'spider.cloud', 'extracted_data': None, 'file_size': 195426, 'keywords': None, 'pathname': '/docs/api', 'resource_type': 'html', 'title': 'Spider API Reference', 'url': '48f1bc3c-3fbb-408a-865b-c191a1bb1f48/spider.cloud/docs*_*api.html', 'user_id': '48f1bc3c-3fbb-408a-865b-c191a1bb1f48'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text='Spider API Reference[Spider v1 Logo Spider ](/) [Credits](/credits/new)[GitHubGithub637](https://github.com/spider-rs/spider)API Reference==========The Spider API is based on REST. Our API is predictable, returns [JSON-encoded](http://www.json.org/) responses, uses standard HTTP response codes, authentication, and verbs. Set your API secret key in the `authorization` header to commence. You can use the `content-type` header with `application/json`, `application/xml`, `text/csv`, and `application/jsonl` for shaping the response.The Spider API supports multi domain actions. You can work with multiple domains per request by adding the urls comma separated.The Spider API differs for every account as we release new versions and tailor functionality. You can add `v1` before any path to pin to the version.Just getting started?----------Check out our [development quickstart](/guides/spider-api) guide.Not a developer?----------Use Spiders [no-code options or apps](/guides/spider) to get started with Spider and to do more with your Spider account no code required.Base UrlJSONCopy```https://api.spider.cloud

For guides and documentation, visit Spider
# Using Browserbase Reader 🅱️¶
Browserbase is a serverless platform for running headless browsers, it offers advanced debugging, session recordings, stealth mode, integrated proxies and captcha solving.
## Installation and Setup¶
  * Get an API key and Project ID from browserbase.com and set it in environment variables (`BROWSERBASE_API_KEY`, `BROWSERBASE_PROJECT_ID`).
  * Install the Browserbase SDK:


In [ ]:
Copied!
```
%pip install browserbase

```

%pip install browserbase
In [ ]:
Copied!
```
from llama_index.readers.web import BrowserbaseWebReader

```

from llama_index.readers.web import BrowserbaseWebReader
In [ ]:
Copied!
```
reader = BrowserbaseWebReader()
docs = reader.load_data(
    urls=[
        "https://example.com",
    ],
    # Text mode
    text_content=False,
)

```

reader = BrowserbaseWebReader() docs = reader.load_data( urls=[ "https://example.com", ], # Text mode text_content=False, )
### Using FireCrawl Reader 🔥¶
Firecrawl is an api that turns entire websites into clean, LLM accessible markdown.
Using Firecrawl to gather an entire website
In [ ]:
Copied!
```
from llama_index.readers.web import FireCrawlWebReader

```

from llama_index.readers.web import FireCrawlWebReader
In [ ]:
Copied!
```
# using firecrawl to crawl a website
firecrawl_reader = FireCrawlWebReader(
    api_key="<your_api_key>",  # Replace with your actual API key from https://www.firecrawl.dev/
    mode="scrape",  # Choose between "crawl" and "scrape" for single page scraping
    params={"additional": "parameters"},  # Optional additional parameters
)

# Load documents from a single page URL
documents = firecrawl_reader.load_data(url="http://paulgraham.com/")

```

# using firecrawl to crawl a website firecrawl_reader = FireCrawlWebReader( api_key="", # Replace with your actual API key from https://www.firecrawl.dev/ mode="scrape", # Choose between "crawl" and "scrape" for single page scraping params={"additional": "parameters"}, # Optional additional parameters ) # Load documents from a single page URL documents = firecrawl_reader.load_data(url="http://paulgraham.com/")
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
response = query_engine.query("What did the author do growing up?")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
Using firecrawl for a single page
In [ ]:
Copied!
```
# Initialize the FireCrawlWebReader with your API key and desired mode
from llama_index.readers.web.firecrawl_web.base import FireCrawlWebReader

firecrawl_reader = FireCrawlWebReader(
    api_key="<your_api_key>",  # Replace with your actual API key from https://www.firecrawl.dev/
    mode="scrape",  # Choose between "crawl" and "scrape" for single page scraping
    params={"additional": "parameters"},  # Optional additional parameters
)

# Load documents from a single page URL
documents = firecrawl_reader.load_data(url="http://paulgraham.com/worked.html")

```

# Initialize the FireCrawlWebReader with your API key and desired mode from llama_index.readers.web.firecrawl_web.base import FireCrawlWebReader firecrawl_reader = FireCrawlWebReader( api_key="", # Replace with your actual API key from https://www.firecrawl.dev/ mode="scrape", # Choose between "crawl" and "scrape" for single page scraping params={"additional": "parameters"}, # Optional additional parameters ) # Load documents from a single page URL documents = firecrawl_reader.load_data(url="http://paulgraham.com/worked.html")
```
Running cells with '/opt/homebrew/bin/python3' requires the ipykernel package.

Run the following command to install 'ipykernel' into the Python environment. 

Command: '/opt/homebrew/bin/python3 -m pip install ipykernel -U --user --force-reinstall'
```

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
response = query_engine.query("What did the author do growing up?")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
Using FireCrawl's extract mode to extract structured data from URLs
In [ ]:
Copied!
```
# Initialize the FireCrawlWebReader with your API key and extract mode
from llama_index.readers.web.firecrawl_web.base import FireCrawlWebReader

firecrawl_reader = FireCrawlWebReader(
    api_key="<your_api_key>",  # Replace with your actual API key from https://www.firecrawl.dev/
    mode="extract",  # Use extract mode to extract structured data
    params={
        "prompt": "Extract the title, author, and main points from this essay",
        # Required prompt parameter for extract mode
    },
)

# Load documents by providing a list of URLs to extract data from
documents = firecrawl_reader.load_data(
    urls=[
        "https://www.paulgraham.com",
        "https://www.paulgraham.com/worked.html",
    ]
)

```

# Initialize the FireCrawlWebReader with your API key and extract mode from llama_index.readers.web.firecrawl_web.base import FireCrawlWebReader firecrawl_reader = FireCrawlWebReader( api_key="", # Replace with your actual API key from https://www.firecrawl.dev/ mode="extract", # Use extract mode to extract structured data params={ "prompt": "Extract the title, author, and main points from this essay", # Required prompt parameter for extract mode }, ) # Load documents by providing a list of URLs to extract data from documents = firecrawl_reader.load_data( urls=[ "https://www.paulgraham.com", "https://www.paulgraham.com/worked.html", ] )
In [ ]:
Copied!
```
index = SummaryIndex.from_documents(documents)

```

index = SummaryIndex.from_documents(documents)
In [ ]:
Copied!
```
# Query the extracted structured data
query_engine = index.as_query_engine()
response = query_engine.query("What are the main points from these essays?")

display(Markdown(f"<b>{response}</b>"))

```

# Query the extracted structured data query_engine = index.as_query_engine() response = query_engine.query("What are the main points from these essays?") display(Markdown(f"**{response}** "))
# Using Hyperbrowser Reader ⚡¶
Hyperbrowser is a platform for running and scaling headless browsers. It lets you launch and manage browser sessions at scale and provides easy to use solutions for any webscraping needs, such as scraping a single page or crawling an entire site.
Key Features:
  * Instant Scalability - Spin up hundreds of browser sessions in seconds without infrastructure headaches
  * Simple Integration - Works seamlessly with popular tools like Puppeteer and Playwright
  * Powerful APIs - Easy to use APIs for scraping/crawling any site, and much more
  * Bypass Anti-Bot Measures - Built-in stealth mode, ad blocking, automatic CAPTCHA solving, and rotating proxies


For more information about Hyperbrowser, please visit the Hyperbrowser website or if you want to check out the docs, you can visit the Hyperbrowser docs.
## Installation and Setup¶
  * Head to Hyperbrowser to sign up and generate an API key. Once you've done this set the `HYPERBROWSER_API_KEY` environment variable or you can pass it to the `HyperbrowserWebReader` constructor.
  * Install the Hyperbrowser SDK:


In [ ]:
Copied!
```
%pip install hyperbrowser

```

%pip install hyperbrowser
In [ ]:
Copied!
```
from llama_index.readers.web import HyperbrowserWebReader

reader = HyperbrowserWebReader(api_key="your_api_key_here")
docs = reader.load_data(
    urls=["https://example.com"],
    operation="scrape",
)
docs

```

from llama_index.readers.web import HyperbrowserWebReader reader = HyperbrowserWebReader(api_key="your_api_key_here") docs = reader.load_data( urls=["https://example.com"], operation="scrape", ) docs
#### Using TrafilaturaWebReader¶
In [ ]:
Copied!
```
from llama_index.readers.web import TrafilaturaWebReader

```

from llama_index.readers.web import TrafilaturaWebReader
```
---------------------------------------------------------------------------
ModuleNotFoundError                       Traceback (most recent call last)
Cell In[7], line 1
----> 1 from llama_index.readers.web import TrafilaturaWebReader

ModuleNotFoundError: No module named 'llama_index.readers.web'
```

In [ ]:
Copied!
```
documents = TrafilaturaWebReader().load_data(
    ["http://paulgraham.com/worked.html"]
)

```

documents = TrafilaturaWebReader().load_data( ["http://paulgraham.com/worked.html"] )
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
response = query_engine.query("What did the author do growing up?")

```

# set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("What did the author do growing up?")
In [ ]:
Copied!
```
display(Markdown(f"<b>{response}</b>"))

```

display(Markdown(f"**{response}** "))
### Using RssReader¶
In [ ]:
Copied!
```
from llama_index.core import SummaryIndex
from llama_index.readers.web import RssReader

documents = RssReader().load_data(
    ["https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"]
)

index = SummaryIndex.from_documents(documents)

# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("What happened in the news today?")

```

from llama_index.core import SummaryIndex from llama_index.readers.web import RssReader documents = RssReader().load_data( ["https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml"] ) index = SummaryIndex.from_documents(documents) # set Logging to DEBUG for more detailed outputs query_engine = index.as_query_engine() response = query_engine.query("What happened in the news today?")
## Using ScrapFly¶
ScrapFly is a web scraping API with headless browser capabilities, proxies, and anti-bot bypass. It allows for extracting web page data into accessible LLM markdown or text. Install ScrapFly Python SDK using pip:
```
pip install scrapfly-sdk

```

Here is a basic usage of ScrapflyReader
In [ ]:
Copied!
```
from llama_index.readers.web import ScrapflyReader

# Initiate ScrapflyReader with your ScrapFly API key
scrapfly_reader = ScrapflyReader(
    api_key="Your ScrapFly API key",  # Get your API key from https://www.scrapfly.io/
    ignore_scrape_failures=True,  # Ignore unprocessable web pages and log their exceptions
)

# Load documents from URLs as markdown
documents = scrapfly_reader.load_data(
    urls=["https://web-scraping.dev/products"]
)

```

from llama_index.readers.web import ScrapflyReader # Initiate ScrapflyReader with your ScrapFly API key scrapfly_reader = ScrapflyReader( api_key="Your ScrapFly API key", # Get your API key from https://www.scrapfly.io/ ignore_scrape_failures=True, # Ignore unprocessable web pages and log their exceptions ) # Load documents from URLs as markdown documents = scrapfly_reader.load_data( urls=["https://web-scraping.dev/products"] )
The ScrapflyReader also allows passigng ScrapeConfig object for customizing the scrape request. See the documentation for the full feature details and their API params: https://scrapfly.io/docs/scrape-api/getting-started
In [ ]:
Copied!
```
from llama_index.readers.web import ScrapflyReader

# Initiate ScrapflyReader with your ScrapFly API key
scrapfly_reader = ScrapflyReader(
    api_key="Your ScrapFly API key",  # Get your API key from https://www.scrapfly.io/
    ignore_scrape_failures=True,  # Ignore unprocessable web pages and log their exceptions
)

scrapfly_scrape_config = {
    "asp": True,  # Bypass scraping blocking and antibot solutions, like Cloudflare
    "render_js": True,  # Enable JavaScript rendering with a cloud headless browser
    "proxy_pool": "public_residential_pool",  # Select a proxy pool (datacenter or residnetial)
    "country": "us",  # Select a proxy location
    "auto_scroll": True,  # Auto scroll the page
    "js": "",  # Execute custom JavaScript code by the headless browser
}

# Load documents from URLs as markdown
documents = scrapfly_reader.load_data(
    urls=["https://web-scraping.dev/products"],
    scrape_config=scrapfly_scrape_config,  # Pass the scrape config
    scrape_format="markdown",  # The scrape result format, either `markdown`(default) or `text`
)

```

from llama_index.readers.web import ScrapflyReader # Initiate ScrapflyReader with your ScrapFly API key scrapfly_reader = ScrapflyReader( api_key="Your ScrapFly API key", # Get your API key from https://www.scrapfly.io/ ignore_scrape_failures=True, # Ignore unprocessable web pages and log their exceptions ) scrapfly_scrape_config = { "asp": True, # Bypass scraping blocking and antibot solutions, like Cloudflare "render_js": True, # Enable JavaScript rendering with a cloud headless browser "proxy_pool": "public_residential_pool", # Select a proxy pool (datacenter or residnetial) "country": "us", # Select a proxy location "auto_scroll": True, # Auto scroll the page "js": "", # Execute custom JavaScript code by the headless browser } # Load documents from URLs as markdown documents = scrapfly_reader.load_data( urls=["https://web-scraping.dev/products"], scrape_config=scrapfly_scrape_config, # Pass the scrape config scrape_format="markdown", # The scrape result format, either `markdown`(default) or `text` )
# Using ZyteWebReader¶
ZyteWebReader allows a user to access the content of webpage in different modes ("article", "html-text", "html"). It enables user to change setting such as browser rendering and JS as the content of many sites would require setting these options to access relevant content. All supported options can be found here: https://docs.zyte.com/zyte-api/usage/reference.html
To install dependencies:
```
pip install zyte-api

```

To get access to your ZYTE API key please visit: https://docs.zyte.com/zyte-api/get-started.html
In [ ]:
Copied!
```
from llama_index.readers.web import ZyteWebReader

# Required to run it in notebook
# import nest_asyncio
# nest_asyncio.apply()


# Initiate ZyteWebReader with your Zyte API key
zyte_reader = ZyteWebReader(
    api_key="your ZYTE API key here",
    mode="article",  # or "html-text" or "html"
)

urls = [
    "https://www.zyte.com/blog/web-scraping-apis/",
    "https://www.zyte.com/blog/system-integrators-extract-big-data/",
]

documents = zyte_reader.load_data(
    urls=urls,
)

print(len(documents[0].text))

```

from llama_index.readers.web import ZyteWebReader # Required to run it in notebook # import nest_asyncio # nest_asyncio.apply() # Initiate ZyteWebReader with your Zyte API key zyte_reader = ZyteWebReader( api_key="your ZYTE API key here", mode="article", # or "html-text" or "html" ) urls = [ "https://www.zyte.com/blog/web-scraping-apis/", "https://www.zyte.com/blog/system-integrators-extract-big-data/", ] documents = zyte_reader.load_data( urls=urls, ) print(len(documents[0].text))


Browser rendering and javascript can be enabled by passing setting corresponding parameters during initialization.
In [ ]:
Copied!
```
zyte_dw_params = {
    "browserHtml": True,  # Enable browser rendering
    "javascript": True,  # Enable JavaScript
}

# Initiate ZyteWebReader with your Zyte API key and use default "article" mode
zyte_reader = ZyteWebReader(
    api_key="your ZYTE API key here",
    download_kwargs=zyte_dw_params,
)

# Load documents from URLs
documents = zyte_reader.load_data(
    urls=urls,
)

```

zyte_dw_params = { "browserHtml": True, # Enable browser rendering "javascript": True, # Enable JavaScript } # Initiate ZyteWebReader with your Zyte API key and use default "article" mode zyte_reader = ZyteWebReader( api_key="your ZYTE API key here", download_kwargs=zyte_dw_params, ) # Load documents from URLs documents = zyte_reader.load_data( urls=urls, )
In [ ]:
Copied!
```
len(documents[0].text)

```

len(documents[0].text)
Out[ ]:


Set "continue_on_failure" to False if you'd like to stop when any request fails.
In [ ]:
Copied!
```
zyte_reader = ZyteWebReader(
    api_key="your ZYTE API key here",
    mode="html-text",
    download_kwargs=zyte_dw_params,
    continue_on_failure=False,
)

# Load documents from URLs
documents = zyte_reader.load_data(
    urls=urls,
)

```

zyte_reader = ZyteWebReader( api_key="your ZYTE API key here", mode="html-text", download_kwargs=zyte_dw_params, continue_on_failure=False, ) # Load documents from URLs documents = zyte_reader.load_data( urls=urls, )
In [ ]:
Copied!
```
len(documents[0].text)

```

len(documents[0].text)
Out[ ]:


In default mode ("article") only the article text is extracted while in the "html-text" full text is extracted from the webpage, there the length of the text is significantly longer.
# Using AgentQLWebReader 🐠¶
Use AgentQL to scrape structured data from a website.
In [ ]:
Copied!
```
from llama_index.readers.web import AgentQLWebReader
from llama_index.core import VectorStoreIndex
from IPython.display import Markdown, display

```

from llama_index.readers.web import AgentQLWebReader from llama_index.core import VectorStoreIndex from IPython.display import Markdown, display
In [ ]:
Copied!
```
# Using AgentQL to crawl a website
agentql_reader = AgentQLWebReader(
    api_key="YOUR_API_KEY",  # Replace with your actual API key from https://dev.agentql.com
    params={
        "is_scroll_to_bottom_enabled": True
    },  # Optional additional parameters
)

# Load documents from a single page URL
document = agentql_reader.load_data(
    url="https://www.ycombinator.com/companies?batch=W25",
    query="{ company[] { name location description industry_category link(a link to the company's detail on Ycombinator)} }",
)

```

# Using AgentQL to crawl a website agentql_reader = AgentQLWebReader( api_key="YOUR_API_KEY", # Replace with your actual API key from https://dev.agentql.com params={ "is_scroll_to_bottom_enabled": True }, # Optional additional parameters ) # Load documents from a single page URL document = agentql_reader.load_data( url="https://www.ycombinator.com/companies?batch=W25", query="{ company[] { name location description industry_category link(a link to the company's detail on Ycombinator)} }", )
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(document)
query_engine = index.as_query_engine()
response = query_engine.query(
    "Find companies that are working on web agent, list their names, locations and link"
)

display(Markdown(f"<b>{response}</b>"))

```

index = VectorStoreIndex.from_documents(document) query_engine = index.as_query_engine() response = query_engine.query( "Find companies that are working on web agent, list their names, locations and link" ) display(Markdown(f"**{response}** "))
# Using OxylabsWebReader¶
OxylabsWebReader allows a user to scrape any website with different parameters while bypassing most of the anti-bot tools. Check out the Oxylabs documentation to get the full list of parameters.
Claim free API credentials by creating an Oxylabs account here.
In [ ]:
Copied!
```
from llama_index.readers.web import OxylabsWebReader


reader = OxylabsWebReader(
    username="OXYLABS_USERNAME", password="OXYLABS_PASSWORD"
)

documents = reader.load_data(
    [
        "https://sandbox.oxylabs.io/products/1",
        "https://sandbox.oxylabs.io/products/2",
    ]
)

print(documents[0].text)

```

from llama_index.readers.web import OxylabsWebReader reader = OxylabsWebReader( username="OXYLABS_USERNAME", password="OXYLABS_PASSWORD" ) documents = reader.load_data( [ "https://sandbox.oxylabs.io/products/1", "https://sandbox.oxylabs.io/products/2", ] ) print(documents[0].text)
```
The Legend of Zelda: Ocarina of Time | Oxylabs Scraping Sandbox

[![]()![logo](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)](/)

Game platforms:

* **All**

* [Nintendo platform](/products/category/nintendo)

+ wii
+ wii-u
+ nintendo-64
+ switch
+ gamecube
+ game-boy-advance
+ 3ds
+ ds

* [Xbox platform](/products/category/xbox-platform)

* **Dreamcast**

* [Playstation platform](/products/category/playstation-platform)

* **Pc**

* **Stadia**

Go Back

Note!This is a sandbox website used for web scraping. Information listed in this website does not have any real meaning and should not be associated with the actual products.

![The Legend of Zelda: Ocarina of Time](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)

The Legend of Zelda: Ocarina of Time
------------------------------------

**Developer:** Nintendo**Platform:****Type:** singleplayer

As a young boy, Link is tricked by Ganondorf, the King of the Gerudo Thieves. The evil human uses Link to gain access to the Sacred Realm, where he places his tainted hands on Triforce and transforms the beautiful Hyrulean landscape into a barren wasteland. Link is determined to fix the problems he helped to create, so with the help of Rauru he travels through time gathering the powers of the Seven Sages.

91,99 €

In stock

Add to Basket

[![The_Legend_of_Zelda:_Majora's_Mask](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)

#### The Legend of Zelda: Majora's Mask](/products/20)

Action Adventure Fantasy

Thrown into a parallel world by the mischievous actions of a possessed Skull Kid, Link finds a land in grave danger. The dark power of a relic called Majora's Mask has wreaked havoc on the citizens of Termina, but their most urgent problem is a suicidal moon crashing toward the world. Link has only 72 hours to find a way to stop its descent.

91,99 €

Add to Basket

[![Indiana_Jones_and_the_Infernal_Machine](data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)

#### Indiana Jones and the Infernal Machine](/products/1836)

Action Adventure Historic

1947. The nazis have been crushed, the Cold War has begun and Soviet agents are sniffing around an ancient ruin. Grab your whip and fedora and join Indy in a globespanning race to unearth the mysterious "Infernal Machine". Survive the challenges of unusual beasts, half the Red Army and more (including - oh no - snakes!) . Puzzle your way through 17 chapters of an action-packed story. Travel the world to exotic locales, from the ruins of Babylon to Egyptian deserts. All the weapons you'll need, including firearms, explosives-and of course Indy's trusty whip and revolver.

80,99 €

Add to Basket

```

Another example with parameters for selecting the geolocation, user agent type, JavaScript rendering, headers, and cookies.
In [ ]:
Copied!
```
documents = reader.load_data(
    [
        "https://sandbox.oxylabs.io/products/3",
    ],
    {
        "geo_location": "Berlin, Germany",
        "render": "html",
        "user_agent_type": "mobile",
        "context": [
            {"key": "force_headers", "value": True},
            {"key": "force_cookies", "value": True},
            {
                "key": "headers",
                "value": {
                    "Content-Type": "text/html",
                    "Custom-Header-Name": "custom header content",
                },
            },
            {
                "key": "cookies",
                "value": [
                    {"key": "NID", "value": "1234567890"},
                    {"key": "1P JAR", "value": "0987654321"},
                ],
            },
            {"key": "http_method", "value": "get"},
            {"key": "follow_redirects", "value": True},
            {"key": "successful_status_codes", "value": [808, 909]},
        ],
    },
)

```

documents = reader.load_data( [ "https://sandbox.oxylabs.io/products/3", ], { "geo_location": "Berlin, Germany", "render": "html", "user_agent_type": "mobile", "context": [ {"key": "force_headers", "value": True}, {"key": "force_cookies", "value": True}, { "key": "headers", "value": { "Content-Type": "text/html", "Custom-Header-Name": "custom header content", }, }, { "key": "cookies", "value": [ {"key": "NID", "value": "1234567890"}, {"key": "1P JAR", "value": "0987654321"}, ], }, {"key": "http_method", "value": "get"}, {"key": "follow_redirects", "value": True}, {"key": "successful_status_codes", "value": [808, 909]}, ], }, )
