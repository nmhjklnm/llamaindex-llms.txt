# Agent Workflow + Research Assistant using AgentQL¶
![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
In this tutorial, we will use an `AgentWorkflow` to build a research assistant OpenAI agent using tools including AgentQL's browser tools, Playwright's tools, and the DuckDuckGoSearch tool. This agent performs a web search to find relevant resources for a research topic, interacts with them, and extracts key metadata (e.g., title, author, publication details, and abstract) from those resources.
## Initial Setup¶
The main things we need to get started are:
  * OpenAI's API key
  * AgentQL's API key


If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙 and Playwright.
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-tools-agentql
%pip install llama-index-tools-playwright
%pip install llama-index-tools-duckduckgo

!playwright install

```

%pip install llama-index %pip install llama-index-tools-agentql %pip install llama-index-tools-playwright %pip install llama-index-tools-duckduckgo !playwright install
Store your `OPENAI_API_KEY` and `AGENTQL_API_KEY` keys in Google Colab's secrets.
In [ ]:
Copied!
```
import os

from google.colab import userdata

os.environ["AGENTQL_API_KEY"] = userdata.get("AGENTQL_API_KEY")
os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")

```

import os from google.colab import userdata os.environ["AGENTQL_API_KEY"] = userdata.get("AGENTQL_API_KEY") os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
Let's start by enabling async for the notebook since an online environment like Google Colab only supports an asynchronous version of AgentQL.
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
Create an `async_browser` instance and select the Playwright tools you want to use.
In [ ]:
Copied!
```
from llama_index.tools.playwright.base import PlaywrightToolSpec

async_browser = await PlaywrightToolSpec.create_async_playwright_browser(
    headless=True
)

playwright_tool = PlaywrightToolSpec(async_browser=async_browser)
playwright_tool_list = playwright_tool.to_tool_list()
playwright_agent_tool_list = [
    tool
    for tool in playwright_tool_list
    if tool.metadata.name in ["click", "get_current_page", "navigate_to"]
]

```

from llama_index.tools.playwright.base import PlaywrightToolSpec async_browser = await PlaywrightToolSpec.create_async_playwright_browser( headless=True ) playwright_tool = PlaywrightToolSpec(async_browser=async_browser) playwright_tool_list = playwright_tool.to_tool_list() playwright_agent_tool_list = [ tool for tool in playwright_tool_list if tool.metadata.name in ["click", "get_current_page", "navigate_to"] ]
Import the AgentQL browser tools and DuckDuckGo full search tool.
In [ ]:
Copied!
```
from llama_index.tools.agentql import AgentQLBrowserToolSpec
from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec

duckduckgo_search_tool = [
    tool
    for tool in DuckDuckGoSearchToolSpec().to_tool_list()
    if tool.metadata.name == "duckduckgo_full_search"
]

agentql_browser_tool = AgentQLBrowserToolSpec(async_browser=async_browser)

```

from llama_index.tools.agentql import AgentQLBrowserToolSpec from llama_index.tools.duckduckgo import DuckDuckGoSearchToolSpec duckduckgo_search_tool = [ tool for tool in DuckDuckGoSearchToolSpec().to_tool_list() if tool.metadata.name == "duckduckgo_full_search" ] agentql_browser_tool = AgentQLBrowserToolSpec(async_browser=async_browser)
We can now create an `AgentWorkFlow` that uses the tools that we have imported.
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import AgentWorkflow

llm = OpenAI(model="gpt-4o")

workflow = AgentWorkflow.from_tools_or_functions(
    playwright_agent_tool_list
    + agentql_browser_tool.to_tool_list()
    + duckduckgo_search_tool,
    llm=llm,
    system_prompt="You are an expert that can do browser automation, data extraction and text summarization for finding and extracting data from research resources.",
)

```

from llama_index.llms.openai import OpenAI from llama_index.core.agent.workflow import AgentWorkflow llm = OpenAI(model="gpt-4o") workflow = AgentWorkflow.from_tools_or_functions( playwright_agent_tool_list + agentql_browser_tool.to_tool_list() + duckduckgo_search_tool, llm=llm, system_prompt="You are an expert that can do browser automation, data extraction and text summarization for finding and extracting data from research resources.", )
`AgentWorkflow` also supports streaming, which works by using the handler that is returned from the workflow. To stream the LLM output, you can use the `AgentStream` events.
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import (
    AgentStream,
)

handler = workflow.run(
    user_msg="""
    Use DuckDuckGoSearch to find URL resources on the web that are relevant to the research topic: What is the relationship between exercise and stress levels?
    Go through each resource found. For each different resource, use Playwright to click on link to the resource, then use AgentQL to extract information, including the name of the resource, author name(s), link to the resource, publishing date, journal name, volume number, issue number, and the abstract.
    Find more resources until there are two different resources that can be successfully extracted from.
    """
)

async for event in handler.stream_events():
    if isinstance(event, AgentStream):
        print(event.delta, end="", flush=True)

```

from llama_index.core.agent.workflow import ( AgentStream, ) handler = workflow.run( user_msg=""" Use DuckDuckGoSearch to find URL resources on the web that are relevant to the research topic: What is the relationship between exercise and stress levels? Go through each resource found. For each different resource, use Playwright to click on link to the resource, then use AgentQL to extract information, including the name of the resource, author name(s), link to the resource, publishing date, journal name, volume number, issue number, and the abstract. Find more resources until there are two different resources that can be successfully extracted from. """ ) async for event in handler.stream_events(): if isinstance(event, AgentStream): print(event.delta, end="", flush=True)
```
/usr/local/lib/python3.11/dist-packages/agentql/_core/_utils.py:171: UserWarning: 🚨 The function get_data_by_prompt_experimental is experimental and may not work as expected 🚨
  warnings.warn(

```

```
I successfully extracted information from one resource. Here are the details:

- **Title**: Role of Physical Activity on Mental Health and Well-Being: A Review
- **Authors**: Aditya Mahindru, Pradeep Patil, Varun Agrawal
- **Link**: [Role of Physical Activity on Mental Health and Well-Being: A Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC9902068/)
- **Publication Date**: January 7, 2023
- **Journal Name**: Cureus
- **Volume Number**: 15
- **Issue Number**: 1
- **Abstract**: The article reviews the positive effects of physical activity on mental health, highlighting its benefits on self-concept, body image, and mood. It discusses the physiological and psychological mechanisms by which exercise improves mental health, including its impact on the hypothalamus-pituitary-adrenal axis, depression, anxiety, sleep, and psychiatric disorders. The review also notes the need for more research in the Indian context.

I will now attempt to extract information from another resource.I successfully extracted information from a second resource. Here are the details:

- **Title**: The Relationship Between Exercise Habits and Stress Among Individuals With Access to Internet-Connected Home Fitness Equipment: Single-Group Prospective Analysis
- **Authors**: Margaret Schneider, Amanda Woodworth, Milad Asgari Mehrabadi
- **Link**: [The Relationship Between Exercise Habits and Stress Among Individuals With Access to Internet-Connected Home Fitness Equipment](https://pmc.ncbi.nlm.nih.gov/articles/PMC9947760/)
- **Publication Date**: February 8, 2023
- **Journal Name**: JMIR Form Res
- **Volume Number**: 7
- **Issue Number**: e41877
- **Abstract**: This study examines the relationship between stress and exercise habits among habitual exercisers with internet-connected home fitness equipment during the COVID-19 lockdown. It found that stress did not negatively impact exercise participation among habitually active adults with such equipment. The study suggests that habitual exercise may buffer the impact of stress on regular moderate to vigorous activity, and highlights the potential role of home-based internet-connected exercise equipment in this buffering.

Both resources provide valuable insights into the relationship between exercise and stress levels.
```

