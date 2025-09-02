# Building a Browser Agent with AgentQL¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
AgentQL tools provide web interaction and structured data extraction from any web page using an AgentQL query or a Natural Language prompt. AgentQL can be used across multiple languages and web pages without breaking over time and change.
This tutorial shows you how to:
  * Create a browser agent with AgentQL tools and LlamaIndex
  * How to use AgentQL tools to navigate the Internet
  * How to use AgentQL tools to scrape content from the Internet


## Overview¶
AgentQL provides three function tools. The first doesn't require a browser and relies on the REST API:
  * **`extract_web_data_with_rest_api`**extracts structured data as JSON from a web page given a URL using either anAgentQL query or a Natural Language description of the data.


The other two tools must be used with a `Playwright` browser or a remote browser instance via Chrome DevTools Protocal (CDP):
  * **`extract_web_data_from_browser`**extracts structured data as JSON from the active web page in a browser using either anAgentQL query or a Natural Language description.
  * **`get_web_element_from_browser`**finds a web element on the active web page in a browser using a Natural Language description and returns its CSS selector for further interaction.


### Tool features¶
Tool | Web Data Extraction | Web Element Extraction | Use With Local Browser  
---|---|---|---  
| extract_web_data_with_rest_api | ✅ | ❌ | ❌ | extract_web_data_from_browser | ✅ | ❌ | ✅ | get_web_element_from_browser | ❌ | ✅ | ✅
## Set up¶
In [ ]:
Copied!
```
%pip install llama-index-tools-agentql llama-index-tools-playwright llama-index

```

%pip install llama-index-tools-agentql llama-index-tools-playwright llama-index
### Credentials¶
To use the AgentQL tools, you will need to get your own API key from the AgentQL Dev Portal and set the AgentQL environment variable:
In [ ]:
Copied!
```
import os

os.environ["AGENTQL_API_KEY"] = "YOUR_AGENTQL_API_KEY"

```

import os os.environ["AGENTQL_API_KEY"] = "YOUR_AGENTQL_API_KEY"
### Set up Playwright browser and AgentQL tools¶
To run this notebook, install Playwright browser and configure Jupyter Notebook's `asyncio` loop.
In [ ]:
Copied!
```
!playwright install

# This import is required only for jupyter notebooks, since they have their own eventloop
import nest_asyncio

nest_asyncio.apply()

```

!playwright install # This import is required only for jupyter notebooks, since they have their own eventloop import nest_asyncio nest_asyncio.apply()
## Instantiation¶
###  `AgentQLRestAPIToolSpec`¶
`AgentQLRestAPIToolSpec` provides `extract_web_data_with_rest_api` function tool.
You can instantiate `AgentQLRestAPIToolSpec` with the following param:
  * `timeout`: The number of seconds to wait for a request before timing out. Increase if data extraction times out. **Defaults to`900`.**
  * `is_stealth_mode_enabled`: Whether to enable experimental anti-bot evasion strategies. This feature may not work for all websites at all times. Data extraction may take longer to complete with this mode enabled. **Defaults to`False`.**
  * `wait_for`: The number of seconds to wait for the page to load before extracting data. **Defaults to`0`.**
  * `is_scroll_to_bottom_enabled`: Whether to scroll to bottom of the page before extracting data. **Defaults to`False`.**
  * `mode`: `"standard"` uses deep data analysis, while `"fast"` trades some depth of analysis for speed and is adequate for most usecases. Learn more about the modes in this guide. **Defaults to`"fast"`.**
  * `is_screenshot_enabled`: Whether to take a screenshot before extracting data. Returned in 'metadata' as a Base64 string. **Defaults to`False`.**


`AgentQLRestAPIToolSpec` is using AgentQL REST API, for more details about the parameters read API Reference docs.
In [ ]:
Copied!
```
from llama_index.tools.agentql import AgentQLRestAPIToolSpec

agentql_rest_api_tool = AgentQLRestAPIToolSpec()

```

from llama_index.tools.agentql import AgentQLRestAPIToolSpec agentql_rest_api_tool = AgentQLRestAPIToolSpec()
###  `AgentQLBrowserToolSpec`¶
`AgentQLBrowserToolSpec` provides 2 tools: `extract_web_data_from_browser` and `get_web_element_from_browser`.
This tool spec can be instantiated with the following params:
  * `async_browser`: An async playwright browser instance.
  * `timeout_for_data`: The number of seconds to wait for a extract data request before timing out. **Defaults to`900`.**
  * `timeout_for_element`: The number of seconds to wait for a get element request before timing out. **Defaults to`900`.**
  * `wait_for_network_idle`: Whether to wait until the network reaches a full idle state before executing. **Defaults to`True`.**
  * `include_hidden_for_data`: Whether to take into account visually hidden elements on the page for extract data. **Defaults to`True`.**
  * `include_hidden_for_element`: Whether to take into account visually hidden elements on the page for get element. **Defaults to`False`.**
  * `mode`: `"standard"` uses deep data analysis, while `"fast"` trades some depth of analysis for speed and is adequate for most usecases. Learn more about the modes in this guide. **Defaults to`"fast"`.**


`AgentQLBrowserToolSpec` is using AgentQL SDK. You can find more details about the parameters and the functions in SDK API Reference.
> **Note:** To instantiate `AgentQLBrowserToolSpec` you need to provide a browser instance. You can create one using `create_async_playwright_browser` utility method from LlamaIndex's Playwright ToolSpec.
In [ ]:
Copied!
```
from llama_index.tools.playwright.base import PlaywrightToolSpec
from llama_index.tools.agentql import AgentQLBrowserToolSpec

async_browser = await PlaywrightToolSpec.create_async_playwright_browser()
agentql_browser_tool = AgentQLBrowserToolSpec(async_browser=async_browser)

```

from llama_index.tools.playwright.base import PlaywrightToolSpec from llama_index.tools.agentql import AgentQLBrowserToolSpec async_browser = await PlaywrightToolSpec.create_async_playwright_browser() agentql_browser_tool = AgentQLBrowserToolSpec(async_browser=async_browser)
## Invoking the AgentQL tools¶
###  `extract_web_data_with_rest_api`¶
This tool uses AgentQL's REST API under the hood, sending the publically available web page's URL to AgentQL's endpoint. This will not work with private pages or logged in sessions. Use `extract_web_data_from_browser` for those usecases.
  * `url`: The URL of the web page you want to extract data from.
  * `query`: The AgentQL query to execute. Use this if you want to extract data in a structure you define. Learn more about how to write an AgentQL query in the docs.
  * `prompt`: A Natural Language description of the data to extract from the page. AgentQL will infer the data’s structure from your prompt.


> **Note:** You must define either a `query` or a `prompt` to use AgentQL.
In [ ]:
Copied!
```
# You can invoke the tool with either a query or a prompt

# await agentql_rest_api_tool.extract_web_data_with_rest_api(
#     url="https://www.agentql.com/blog",
#     prompt="the blog posts with title, url, author and publication date",
# )

await agentql_rest_api_tool.extract_web_data_with_rest_api(
    url="https://www.agentql.com/blog",
    query="{ posts[] { title url author date }}",
)

```

# You can invoke the tool with either a query or a prompt # await agentql_rest_api_tool.extract_web_data_with_rest_api( # url="https://www.agentql.com/blog", # prompt="the blog posts with title, url, author and publication date", # ) await agentql_rest_api_tool.extract_web_data_with_rest_api( url="https://www.agentql.com/blog", query="{ posts[] { title url author date }}", )
Out[ ]:
```
{'data': {'posts': [{'title': 'AgentQL MCP Server: Structured Web Data for Claude, Cursor, Windsurf, and more',
    'url': 'https://www.agentql.com/blog/2025-mcp-integration',
    'author': 'Rachel-Lee Nabors',
    'date': 'Mar 12, 2025'},
   {'title': 'Dify + AgentQL: Build AI Apps with Live Web Data, No Code Needed',
    'url': 'https://www.agentql.com/blog/2025-dify-integration',
    'author': 'Rachel-Lee Nabors',
    'date': 'Mar 11, 2025'},
   {'title': 'Zapier + AgentQL: No-Code Web Data for Smarter Workflows',
    'url': 'https://www.agentql.com/blog/2025-zapier-integration',
    'author': 'Rachel-Lee Nabors',
    'date': 'Mar 10, 2025'},
   {'title': 'Something is coming.',
    'url': 'https://www.agentql.com/blog/2025-iw-teaser',
    'author': 'Rachel-Lee Nabors',
    'date': 'Mar 7, 2025'},
   {'title': 'Automated web application testing with AI and Playwright',
    'url': 'https://www.agentql.com/blog/2025-automated-testing-web-ai-playwright',
    'author': 'Vladimir de Turckheim',
    'date': 'Feb 26, 2025'}]},
 'metadata': {'request_id': '5a43ab86-f68b-4470-bca9-ab51a791041a',
  'generated_query': None,
  'screenshot': None}}
```

#### Stealth Mode¶
AgentQL provides experimental anti-bot evasion strategies to avoid detection by anti-bot services.
> **Note** : Stealth mode is experimental and may not work for all websites at all times. The data extraction may take longer to complete comparing to non-stealth mode.
In [ ]:
Copied!
```
# agentql_rest_api_tool = AgentQLRestAPIToolSpec(is_stealth_mode_enabled=True)

await agentql_rest_api_tool.extract_web_data_with_rest_api(
    url="https://www.patagonia.com/shop/web-specials/womens",
    query="{ items[] { name price}}",
)

```

# agentql_rest_api_tool = AgentQLRestAPIToolSpec(is_stealth_mode_enabled=True) await agentql_rest_api_tool.extract_web_data_with_rest_api( url="https://www.patagonia.com/shop/web-specials/womens", query="{ items[] { name price}}", )
Out[ ]:
```
{'data': {'items': [{'name': "W's Recycled Down Sweater™ Parka - Pitch Blue (PIBL) (28460)",
    'price': 178.99},
   {'name': "W's Recycled Down Sweater™ Parka - Shelter Brown (SHBN) (28460)",
    'price': 178.99},
   {'name': "W's Recycled Down Sweater™ Parka - Pine Needle Green (PNGR) (28460)",
    'price': 178.99},
   {'name': "W's Recycled Down Sweater™ Parka - Burnished Red (BURR) (28460)",
    'price': 178.99},
   {'name': "W's Nano Puff® Jacket - Burnished Red (BURR) (84217)",
    'price': 118.99},
   {'name': "W's Nano Puff® Jacket - Pine Needle Green (PNGR) (84217)",
    'price': 118.99},
   {'name': "W's Powder Town Jacket - Vivid Apricot (VAPC) (31635)",
    'price': 208.99},
   {'name': "W's Powder Town Jacket - Pine Needle Green (PNGR) (31635)",
    'price': 208.99},
   {'name': "W's Powder Town Jacket - Dulse Mauve (DLMA) (31635)",
    'price': 208.99},
   {'name': "W's Powder Town Jacket - Smolder Blue w/Dulse Mauve (SBMA) (31635)",
    'price': 208.99},
   {'name': "W's Powder Town Pants - Pine Needle Green (PNGR) (31645)",
    'price': 148.99},
   {'name': "W's Powder Town Pants - Thermal Blue (TMBL) (31645)",
    'price': 173.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Dulse Mauve (DLMA) (25455)",
    'price': 68.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Synched Flight Small: Natural (SYNL) (25455)",
    'price': 96.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Thermal Blue (TMBL) (25455)",
    'price': 82.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Across Oceans: Pitch Blue (ASPH) (25455)",
    'price': 68.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Terra Pink (TRPI) (25455)",
    'price': 68.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Small Currents: Natural (SCNL) (25455)",
    'price': 68.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Nickel w/Vivid Apricot (NLVA) (25455)",
    'price': 68.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Echo Purple (ECPU) (25455)",
    'price': 68.99},
   {'name': "W's Lightweight Synchilla® Snap-T® Pullover - Oatmeal Heather w/Vessel Blue (OHVL) (25455)",
    'price': 68.99},
   {'name': "W's Down Sweater™ - Seabird Grey (SBDY) (84684)",
    'price': 166.99},
   {'name': "W's Pine Bank 3-in-1 Parka - Shelter Brown (SHBN) (21025)",
    'price': 273.99},
   {'name': "W's Pine Bank 3-in-1 Parka - Pitch Blue (PIBL) (21025)",
    'price': 328.99},
   {'name': "W's Pine Bank 3-in-1 Parka - Burnished Red (BURR) (21025)",
    'price': 273.99},
   {'name': "W's Pine Bank 3-in-1 Parka - Pine Needle Green (PNGR) (21025)",
    'price': 273.99},
   {'name': "W's SnowDrifter Jacket - Vessel Blue (VSLB) (30071)",
    'price': 268.99},
   {'name': "W's SnowDrifter Jacket - Dulse Mauve (DLMA) (30071)",
    'price': 268.99},
   {'name': "W's SnowDrifter Jacket - Vivid Apricot (VAPC) (30071)",
    'price': 268.99},
   {'name': "W's SnowDrifter Jacket - Thermal Blue (TMBL) (30071)",
    'price': 268.99},
   {'name': "W's Re-Tool Half-Snap Pullover - Burnished Red (BURR) (26465)",
    'price': 78.99},
   {'name': "W's Re-Tool Half-Snap Pullover - Vessel Blue (VSLB) (26465)",
    'price': 94.99},
   {'name': "W's Re-Tool Half-Snap Pullover - Dulse Mauve (DLMA) (26465)",
    'price': 78.99},
   {'name': "W's Re-Tool Half-Snap Pullover - Shelter Brown (SHBN) (26465)",
    'price': 78.99},
   {'name': "W's Insulated Storm Shift Jacket - Dulse Mauve (DLMA) (31835)",
    'price': 383.99},
   {'name': "W's Insulated Storm Shift Jacket - Pine Needle Green (PNGR) (31835)",
    'price': 328.99},
   {'name': "W's SnowDrifter Bibs - Black (BLK) (30081)", 'price': 238.99},
   {'name': "W's SnowDrifter Bibs - Smolder Blue (SMDB) (30081)",
    'price': 278.99},
   {'name': "W's SnowDrifter Bibs - Dulse Mauve (DLMA) (30081)",
    'price': 238.99},
   {'name': "W's SnowDrifter Bibs - Pine Needle Green (PNGR) (30081)",
    'price': 238.99},
   {'name': "W's Recycled Wool-Blend Crewneck Sweater - Chevron Cable: Natural (CHNL) (51025)",
    'price': 73.99},
   {'name': "W's Recycled Wool-Blend Crewneck Sweater - Only Earth: Beeswax Tan (OETN) (51025)",
    'price': 103.99},
   {'name': "W's Recycled Wool-Blend Crewneck Sweater - Snowdrift: Thermal Blue (SDTL) (51025)",
    'price': 88.99},
   {'name': "W's Recycled Wool-Blend Crewneck Sweater - Ridge: Pine Needle Green (RPNG) (51025)",
    'price': 88.99},
   {'name': "W's Recycled Wool-Blend Crewneck Sweater - Chevron Cable: Madder Red (CHMR) (51025)",
    'price': 88.99},
   {'name': "W's Recycled Wool-Blend Crewneck Sweater - Smolder Blue (SMDB) (51025)",
    'price': 73.99},
   {'name': "W's Recycled Wool-Blend Crewneck Sweater - Fireside: Shelter Brown (FISN) (51025)",
    'price': 73.99},
   {'name': "W's Micro D® Joggers - Synched Flight Small: Natural (SYNL) (22020)",
    'price': 48.99},
   {'name': "W's Micro D® Joggers - Endless Blue (ENLB) (22020)",
    'price': 58.99},
   {'name': "W's Micro D® Joggers - Small Currents: Natural (SCNL) (22020)",
    'price': 48.99},
   {'name': "W's Better Sweater® 1/4-Zip - Stormy Mauve (STMA) (25618)",
    'price': 68.99},
   {'name': "W's Better Sweater® 1/4-Zip - Dulse Mauve (DLMA) (25618)",
    'price': 82.99},
   {'name': "W's Better Sweater® 1/4-Zip - Torrey Pine Green (TPGN) (25618)",
    'price': 82.99},
   {'name': "W's Better Sweater® 1/4-Zip - Nouveau Green (NUVG) (25618)",
    'price': 68.99},
   {'name': "W's Better Sweater® 1/4-Zip - Raptor Brown (RPBN) (25618)",
    'price': 68.99},
   {'name': "W's Insulated Powder Town Pants - Black (BLK) (31185)",
    'price': 160.99},
   {'name': "W's Insulated Powder Town Pants - Smolder Blue (SMDB) (31185)",
    'price': 160.99},
   {'name': "W's Insulated Powder Town Pants - Dulse Mauve (DLMA) (31185)",
    'price': 160.99},
   {'name': "W's Insulated Powder Town Pants - Vivid Apricot (VAPC) (31185)",
    'price': 160.99},
   {'name': "W's Insulated Powder Town Pants - Across Oceans: Smolder Blue (ASBE) (31185)",
    'price': 160.99},
   {'name': 'Atom Sling 8L - Vessel Blue (VSLB) (48262)', 'price': 44.99},
   {'name': 'Atom Sling 8L - Buckhorn Green (BUGR) (48262)', 'price': 44.99},
   {'name': 'Atom Sling 8L - Dulse Mauve (DLMA) (48262)', 'price': 44.99},
   {'name': "W's Classic Retro-X® Jacket - Natural w/Smolder Blue (NTSB) (23074)",
    'price': 136.99},
   {'name': "W's Classic Retro-X® Jacket - Nest Brown w/Dulse Mauve (NBDU) (23074)",
    'price': 113.99},
   {'name': "W's Classic Retro-X® Jacket - Small Currents: Natural (SCNL) (23074)",
    'price': 113.99},
   {'name': "W's Los Gatos 1/4-Zip - Salt Grey (SGRY) (25236)",
    'price': 53.99},
   {'name': "W's Los Gatos 1/4-Zip - Dulse Mauve (DLMA) (25236)",
    'price': 64.99},
   {'name': "W's Stand Up® Cropped Corduroy Overalls - Nest Brown (NESB) (75100)",
    'price': 68.99},
   {'name': "W's Stand Up® Cropped Corduroy Overalls - Pitch Blue (PIBL) (75100)",
    'price': 68.99},
   {'name': "W's Stand Up® Cropped Corduroy Overalls - Beeswax Tan (BWX) (75100)",
    'price': 68.99},
   {'name': "W's Synchilla® Jacket - Oatmeal Heather w/Natural (OTNL) (22955)",
    'price': 88.99},
   {'name': "W's Synchilla® Jacket - Black (BLK) (22955)", 'price': 73.99},
   {'name': "W's Synchilla® Jacket - Pitch Blue (PIBL) (22955)",
    'price': 73.99},
   {'name': "W's Synchilla® Jacket - Beeswax Tan (BWX) (22955)",
    'price': 73.99},
   {'name': "W's Insulated Powder Town Jacket - Vivid Apricot (VAPC) (31200)",
    'price': 238.99},
   {'name': "W's Insulated Powder Town Jacket - Black (BLK) (31200)",
    'price': 278.99},
   {'name': "W's Insulated Powder Town Jacket - Across Oceans: Smolder Blue (ASBE) (31200)",
    'price': 238.99},
   {'name': "W's Powder Town Bibs - Smolder Blue (SMDB) (31650)",
    'price': 178.99},
   {'name': "W's Powder Town Bibs - Dulse Mauve (DLMA) (31650)",
    'price': 208.99},
   {'name': "W's Powder Town Bibs - Pine Needle Green (PNGR) (31650)",
    'price': 178.99},
   {'name': "W's Powder Town Bibs - Seabird Grey (SBDY) (31650)",
    'price': 178.99},
   {'name': "W's Retro Pile Marsupial - Thermal Blue (TMBL) (22835)",
    'price': 73.99},
   {'name': "W's Retro Pile Marsupial - Shroom Taupe (STPE) (22835)",
    'price': 88.99},
   {'name': "W's Retro Pile Marsupial - Shelter Brown (SHBN) (22835)",
    'price': 73.99},
   {'name': "W's Cord Fjord Coat - Dulse Mauve (DLMA) (26881)",
    'price': 163.99},
   {'name': "W's Cord Fjord Coat - Shelter Brown (SHBN) (26881)",
    'price': 163.99},
   {'name': "W's Regenerative Organic Certified® Cotton Essential Top - Thermal Blue (TMBL) (42171)",
    'price': 41.99},
   {'name': "W's Regenerative Organic Certified® Cotton Essential Top - Pine Needle Green (PNGR) (42171)",
    'price': 41.99},
   {'name': "W's Lonesome Mesa Long Coat - Pitch Blue (PIBL) (26655)",
    'price': 148.99},
   {'name': "W's Lonesome Mesa Long Coat - Pine Needle Green (PNGR) (26655)",
    'price': 148.99}]},
 'metadata': {'request_id': '0016c761-92c1-47b5-9b8f-f71f9727d58d',
  'generated_query': None,
  'screenshot': None}}
```

###  `extract_web_data_from_browser`¶
  * `query`: The AgentQL query to execute. Use this if you want to extract data in a structure you define. Learn more about how to write an AgentQL query in the docs.
  * `prompt`: A Natural Language description of the data to extract from the page. AgentQL will infer the data’s structure from your prompt.


> **Note:** You must define either a `query` or a `prompt` to use AgentQL.
To extract data, first you must navigate to a web page using LlamaIndex's Playwright click tool.
In [ ]:
Copied!
```
playwright_tool = PlaywrightToolSpec(async_browser=async_browser)
await playwright_tool.navigate_to("https://www.agentql.com/blog")

# You can invoke the tool with either a query or a prompt

# await agentql_browser_tool.extract_web_data_from_browser(
#     query="{ posts[] { title url }}",
# )

await agentql_browser_tool.extract_web_data_from_browser(
    prompt="the blog posts with title and url",
)

```

playwright_tool = PlaywrightToolSpec(async_browser=async_browser) await playwright_tool.navigate_to("https://www.agentql.com/blog") # You can invoke the tool with either a query or a prompt # await agentql_browser_tool.extract_web_data_from_browser( # query="{ posts[] { title url }}", # ) await agentql_browser_tool.extract_web_data_from_browser( prompt="the blog posts with title and url", )
```
/Users/jisonz/Library/Caches/pypoetry/virtualenvs/llama-index-AJEGkUS0-py3.13/lib/python3.13/site-packages/agentql/_core/_utils.py:167: UserWarning: 🚨 The function get_data_by_prompt_experimental is experimental and may not work as expected 🚨
  warnings.warn(

```

Out[ ]:
```
{'blog_post': [{'title': 'AgentQL MCP Server: Structured Web Data for Claude, Cursor, Windsurf, and more',
   'url': 'https://www.agentql.com/blog/2025-mcp-integration'},
  {'title': 'Dify + AgentQL: Build AI Apps with Live Web Data, No Code Needed',
   'url': 'https://www.agentql.com/blog/2025-dify-integration'},
  {'title': 'Zapier + AgentQL: No-Code Web Data for Smarter Workflows',
   'url': 'https://www.agentql.com/blog/2025-zapier-integration'},
  {'title': 'Something is coming.',
   'url': 'https://www.agentql.com/blog/2025-iw-teaser'},
  {'title': 'Automated web application testing with AI and Playwright',
   'url': 'https://www.agentql.com/blog/2025-automated-testing-web-ai-playwright'}]}
```

###  `get_web_element_from_browser`¶
  * `prompt`: A Natural Language description of the web element to find on the page.


In [ ]:
Copied!
```
await playwright_tool.navigate_to("https://www.agentql.com/blog")
print(await playwright_tool.get_current_page())

next_page_button = await agentql_browser_tool.get_web_element_from_browser(
    prompt="The next page navigation button",
)
next_page_button

```

await playwright_tool.navigate_to("https://www.agentql.com/blog") print(await playwright_tool.get_current_page()) next_page_button = await agentql_browser_tool.get_web_element_from_browser( prompt="The next page navigation button", ) next_page_button
```
https://www.agentql.com/blog

```

Out[ ]:
```
"[tf623_id='1111']"
```

Click on the element and check the url again
In [ ]:
Copied!
```
await playwright_tool.click(next_page_button)

```

await playwright_tool.click(next_page_button)
Out[ ]:
```
"Clicked element '[tf623_id='1111']'"
```

In [ ]:
Copied!
```
print(await playwright_tool.get_current_page())

```

print(await playwright_tool.get_current_page())
```
https://www.agentql.com/blog/page/2

```

## Using the AgentQL tools with agent¶
To get started, you will need an OpenAI api key
In [ ]:
Copied!
```
# set your openai key, if using openai
import os

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

```

# set your openai key, if using openai import os os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI

# We add playwright's click, get_current_page, and navigate_to tools to the agent along with agentql tools
playwright_tool = PlaywrightToolSpec(async_browser=async_browser)
playwright_tool_list = playwright_tool.to_tool_list()
playwright_agent_tool_list = [
    tool
    for tool in playwright_tool_list
    if tool.metadata.name in ["click", "get_current_page", "navigate_to"]
]

agent = FunctionAgent(
    tools=playwright_agent_tool_list + agentql_browser_tool.to_tool_list(),
    llm=OpenAI(model="gpt-4o"),
)

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.llms.openai import OpenAI # We add playwright's click, get_current_page, and navigate_to tools to the agent along with agentql tools playwright_tool = PlaywrightToolSpec(async_browser=async_browser) playwright_tool_list = playwright_tool.to_tool_list() playwright_agent_tool_list = [ tool for tool in playwright_tool_list if tool.metadata.name in ["click", "get_current_page", "navigate_to"] ] agent = FunctionAgent( tools=playwright_agent_tool_list + agentql_browser_tool.to_tool_list(), llm=OpenAI(model="gpt-4o"), )
In [ ]:
Copied!
```
print(
    await agent.run(
        """
        Navigate to https://blog.samaltman.com/archive,
        Find blog posts titled "What I wish someone had told me", click on the link,
        Extract the blog text and number of views.
        """
    )
)

```

print( await agent.run( """ Navigate to https://blog.samaltman.com/archive, Find blog posts titled "What I wish someone had told me", click on the link, Extract the blog text and number of views. """ ) )
```
I have extracted the blog post titled "What I wish someone had told me" along with the number of views. Here are the details:

**Blog Text:**
> Optimism, obsession, self-belief, raw horsepower and personal connections are how things get started. Cohesive teams, the right combination of calmness and urgency, and unreasonable commitment are how things get finished. Long-term orientation is in short supply; try not to worry about what people think in the short term, which will get easier over time. It is easier for a team to do a hard thing that really matters than to do an easy thing that doesn’t really matter; audacious ideas motivate people. Incentives are superpowers; set them carefully. Concentrate your resources on a small number of high-conviction bets; this is easy to say but evidently hard to do. You can delete more stuff than you think. Communicate clearly and concisely. Fight bullshit and bureaucracy every time you see it and get other people to fight it too. Do not let the org chart get in the way of people working productively together. Outcomes are what count; don’t let good process excuse bad results. Spend more time recruiting. Take risks on high-potential people with a fast rate of improvement. Look for evidence of getting stuff done in addition to intelligence. Superstars are even more valuable than they seem, but you have to evaluate people on their net impact on the performance of the organization. Fast iteration can make up for a lot; it’s usually ok to be wrong if you iterate quickly. Plans should be measured in decades, execution should be measured in weeks. Don’t fight the business equivalent of the laws of physics. Inspiration is perishable and life goes by fast. Inaction is a particularly insidious type of risk. Scale often has surprising emergent properties. Compounding exponentials are magic. In particular, you really want to build a business that gets a compounding advantage with scale. Get back up and keep going. Working with great people is one of the best parts of life.

**Number of Views:** 531,222

```

