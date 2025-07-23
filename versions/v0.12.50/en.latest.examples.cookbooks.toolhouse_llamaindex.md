![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Sales Prospecting Workflow with Toolhouse¶
In this notebook you'll learn how to create a sales prospecting workflow using Toolhouse and LlamaIndex. Sales prospecting allows companies to find the perfect potential customer based on the business's value proposition and target market.
The workflow will use a single agent to perform these activities:
  1. It will ask the agent to determine a business's value proposition by getting the contents of its landing page.
  2. It will search the internet for prospective customers that may benefit from the business's offerings.
  3. It will determine the best company to reach out to.
  4. It will draft a personalized email to the selected company.


## Initial setup¶
Let's make sure all the required libraries are present. This example uses Llama 3.2 on Groq, but you can use any the LLMs supported by LlamaIndex.
In [ ]:
Copied!
```
%pip install llama-index
%pip install llama-index-llms-groq
%pip install toolhouse

```

%pip install llama-index %pip install llama-index-llms-groq %pip install toolhouse
Next, we'll pass the API keys.
To get a Toolhouse API key:
  1. Sign up for Toolhouse or sign in if you're an existing user.
  2. If you're a new user, copy the auto-generated API key you'll receive during onboarding. Existing users can get an API key in the API Keys page.
  3. Paste the API bey below.


To get a Groq API Key, get access on Groq, then past your API key below.
**Important:** store your API keys safely when in production.
In [ ]:
Copied!
```
import os

os.environ[
    "TOOLHOUSE_API_KEY"
] = "Get your Toolhouse API key at https://join.toolhouse.ai"
os.environ[
    "GROQ_API_KEY"
] = "Get your Groq API key at https://console.groq.com"

```

import os os.environ[ "TOOLHOUSE_API_KEY" ] = "Get your Toolhouse API key at https://join.toolhouse.ai" os.environ[ "GROQ_API_KEY" ] = "Get your Groq API key at https://console.groq.com"
## Import libraries¶
We're going to import LlamaIndexas and Toolhouse. We then initialize Toolhouse and the Groq LLM.
In [ ]:
Copied!
```
from llama_index.llms.groq import Groq
from llama_index.core.agent import ReActAgent
from llama_index.core.memory import ChatMemoryBuffer
from toolhouse import Toolhouse, Provider
from llama_index.core.workflow import (
    Context,
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)

```

from llama_index.llms.groq import Groq from llama_index.core.agent import ReActAgent from llama_index.core.memory import ChatMemoryBuffer from toolhouse import Toolhouse, Provider from llama_index.core.workflow import ( Context, Event, StartEvent, StopEvent, Workflow, step, )
In [ ]:
Copied!
```
llm = Groq(model="llama-3.2-11b-vision-preview")

th = Toolhouse(provider=Provider.LLAMAINDEX)
th.set_metadata("id", "llamaindex_agent")
th.set_metadata("timezone", 0)

```

llm = Groq(model="llama-3.2-11b-vision-preview") th = Toolhouse(provider=Provider.LLAMAINDEX) th.set_metadata("id", "llamaindex_agent") th.set_metadata("timezone", 0)
## Install Toolhouse tools¶
The agent will require to search the web and get the contents of a page. To allow this, go to your Toolhouse dashboard and install the following tools:
  * Get page contents
  * Web search


## The Workflow¶
The workflow will have four steps; we created an output event for each step to make the sequential aspect clearer.
Because Toolhouse integrates directly into LlamaIndex, you can pass the Toolhouse tools directly to the agent.
In [ ]:
Copied!
```
class WebsiteContentEvent(Event):
    contents: str


class WebSearchEvent(Event):
    results: str


class RankingEvent(Event):
    results: str


class LogEvent(Event):
    msg: str


class SalesRepWorkflow(Workflow):
    agent = ReActAgent(
        tools=th.get_tools(bundle="llamaindex test"),
        llm=llm,
        memory=ChatMemoryBuffer.from_defaults(),
    )

    @step
    async def get_company_info(
        self, ctx: Context, ev: StartEvent
    ) -> WebsiteContentEvent:
        ctx.write_event_to_stream(
            LogEvent(msg=f"Getting the contents of {ev.url}…")
        )
        prompt = f"Get the contents of {ev.url}, then summarize its key value propositions in a few bullet points."
        contents = await self.agent.achat(prompt)
        return WebsiteContentEvent(contents=str(contents.response))

    @step
    async def find_prospects(
        self, ctx: Context, ev: WebsiteContentEvent
    ) -> WebSearchEvent:
        ctx.write_event_to_stream(
            LogEvent(
                msg=f"Performing web searches to identify companies who can benefit from the business's offerings."
            )
        )
        prompt = f"With that you know about the business, perform a web search to find 5 tech companies who may benefit from the business's product. Only answer with the names of the companies you chose."
        results = await self.agent.achat(prompt)
        return WebSearchEvent(results=str(results.response))

    @step
    async def select_best_company(
        self, ctx: Context, ev: WebSearchEvent
    ) -> RankingEvent:
        ctx.write_event_to_stream(
            LogEvent(
                msg=f"Selecting the best company who can benefit from the business's offering…"
            )
        )
        prompt = "Select one company that can benefit from the business's product. Only use your knowledge to select the company. Respond with just the name of the company. Do not use tools."
        results = await self.agent.achat(prompt)
        ctx.write_event_to_stream(
            LogEvent(
                msg=f"The agent selected this company: {results.response}"
            )
        )
        return RankingEvent(results=str(results.response))

    @step
    async def prepare_email(self, ctx: Context, ev: RankingEvent) -> StopEvent:
        ctx.write_event_to_stream(
            LogEvent(msg=f"Drafting a short email for sales outreach…")
        )
        prompt = f"Draft a short cold sales outreach email for the company you picked. Do not use tools."
        email = await self.agent.achat(prompt)
        ctx.write_event_to_stream(
            LogEvent(msg=f"Here is the email: {email.response}")
        )
        return StopEvent(result=str(email.response))

```

class WebsiteContentEvent(Event): contents: str class WebSearchEvent(Event): results: str class RankingEvent(Event): results: str class LogEvent(Event): msg: str class SalesRepWorkflow(Workflow): agent = ReActAgent( tools=th.get_tools(bundle="llamaindex test"), llm=llm, memory=ChatMemoryBuffer.from_defaults(), ) @step async def get_company_info( self, ctx: Context, ev: StartEvent ) -> WebsiteContentEvent: ctx.write_event_to_stream( LogEvent(msg=f"Getting the contents of {ev.url}…") ) prompt = f"Get the contents of {ev.url}, then summarize its key value propositions in a few bullet points." contents = await self.agent.achat(prompt) return WebsiteContentEvent(contents=str(contents.response)) @step async def find_prospects( self, ctx: Context, ev: WebsiteContentEvent ) -> WebSearchEvent: ctx.write_event_to_stream( LogEvent( msg=f"Performing web searches to identify companies who can benefit from the business's offerings." ) ) prompt = f"With that you know about the business, perform a web search to find 5 tech companies who may benefit from the business's product. Only answer with the names of the companies you chose." results = await self.agent.achat(prompt) return WebSearchEvent(results=str(results.response)) @step async def select_best_company( self, ctx: Context, ev: WebSearchEvent ) -> RankingEvent: ctx.write_event_to_stream( LogEvent( msg=f"Selecting the best company who can benefit from the business's offering…" ) ) prompt = "Select one company that can benefit from the business's product. Only use your knowledge to select the company. Respond with just the name of the company. Do not use tools." results = await self.agent.achat(prompt) ctx.write_event_to_stream( LogEvent( msg=f"The agent selected this company: {results.response}" ) ) return RankingEvent(results=str(results.response)) @step async def prepare_email(self, ctx: Context, ev: RankingEvent) -> StopEvent: ctx.write_event_to_stream( LogEvent(msg=f"Drafting a short email for sales outreach…") ) prompt = f"Draft a short cold sales outreach email for the company you picked. Do not use tools." email = await self.agent.achat(prompt) ctx.write_event_to_stream( LogEvent(msg=f"Here is the email: {email.response}") ) return StopEvent(result=str(email.response))
## Run the workflow¶
Simply instantiate the workflow and pass the URL of a company to get started.
In [ ]:
Copied!
```
workflow = SalesRepWorkflow(timeout=None)
handler = workflow.run(url="https://toolhouse.ai")
async for event in handler.stream_events():
    if isinstance(event, LogEvent):
        print(event.msg)

```

workflow = SalesRepWorkflow(timeout=None) handler = workflow.run(url="https://toolhouse.ai") async for event in handler.stream_events(): if isinstance(event, LogEvent): print(event.msg)
```
Getting the contents of https://toolhouse.ai…
Performing web searches to identify companies who can benefit from the business's offerings.
Selecting the best company who can benefit from the business's offering…
The agent selected this company: Cohere
Drafting a short email for sales outreach…
Here is the email: Subject: Streamline Your LLM Function Calling with Toolhouse

Hi [Cohere Team],

I noticed Cohere is leading the way in providing enterprise-ready LLM solutions. Given that your Command-r model already supports function calling, I thought you'd be interested in Toolhouse's developer toolkit that could enhance your clients' implementation experience.

Toolhouse offers a unified SDK that streamlines LLM function calling across multiple models, including Cohere's. Our platform provides:
- Pre-built, production-ready tools that reduce development time
- Built-in analytics for easier debugging
- A single integration point for multiple LLM tools

Would you be open to a 15-minute call to discuss how Toolhouse could help Cohere's enterprise clients implement function calling more efficiently?

Best regards,
[Name]

```

