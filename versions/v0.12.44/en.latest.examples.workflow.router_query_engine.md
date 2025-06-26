![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Router Query Engine¶
`RouterQueryEngine` chooses the most appropriate query engine from multiple options to process a given query.
This notebook walks through implementation of Router Query Engine, using workflows.
Specifically we will implement RouterQueryEngine.
In [ ]:
Copied!
```
!pip install -U llama-index

```

!pip install -U llama-index
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-.."

```

import os os.environ["OPENAI_API_KEY"] = "sk-.."
Since workflows are async first, this all runs fine in a notebook. If you were running in your own code, you would want to use `asyncio.run()` to start an async event loop if one isn't already running.
```
async def main():
    <async code>

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

## Define Events¶
In [ ]:
Copied!
```
from llama_index.core.workflow import Event
from llama_index.core.base.base_selector import SelectorResult
from typing import Dict, List, Any
from llama_index.core.base.response.schema import RESPONSE_TYPE


class QueryEngineSelectionEvent(Event):
    """Result of selecting the query engine tools."""

    selected_query_engines: SelectorResult


class SynthesizeEvent(Event):
    """Event for synthesizing the response from different query engines."""

    result: List[RESPONSE_TYPE]
    selected_query_engines: SelectorResult

```

from llama_index.core.workflow import Event from llama_index.core.base.base_selector import SelectorResult from typing import Dict, List, Any from llama_index.core.base.response.schema import RESPONSE_TYPE class QueryEngineSelectionEvent(Event): """Result of selecting the query engine tools.""" selected_query_engines: SelectorResult class SynthesizeEvent(Event): """Event for synthesizing the response from different query engines.""" result: List[RESPONSE_TYPE] selected_query_engines: SelectorResult
## The Workflow¶
`selector:`
  1. It takes a StartEvent as input and returns a QueryEngineSelectionEvent.
  2. The `LLMSingleSelector`/ `PydanticSingleSelector`/ `PydanticMultiSelector` will select one/ multiple query engine tools.


`generate_responses:`
This function uses the selected query engines to generate responses and returns SynthesizeEvent.
`synthesize_responses:`
This function combines the generated responses and synthesizes the final response if multiple query engines are selected otherwise returns the single generated response.
The steps will use the built-in `StartEvent` and `StopEvent` events.
With our events defined, we can construct our workflow and steps.
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)

from llama_index.llms.openai import OpenAI
from llama_index.core.selectors.utils import get_selector_from_llm
from llama_index.core.base.response.schema import (
    PydanticResponse,
    Response,
    AsyncStreamingResponse,
)
from llama_index.core.bridge.pydantic import BaseModel
from llama_index.core.response_synthesizers import TreeSummarize
from llama_index.core.schema import QueryBundle
from llama_index.core import Settings

from IPython.display import Markdown, display
import asyncio


class RouterQueryEngineWorkflow(Workflow):
    @step
    async def selector(
        self, ctx: Context, ev: StartEvent
    ) -> QueryEngineSelectionEvent:
        """
        Selects a single/ multiple query engines based on the query.
        """

        await ctx.set("query", ev.get("query"))
        await ctx.set("llm", ev.get("llm"))
        await ctx.set("query_engine_tools", ev.get("query_engine_tools"))
        await ctx.set("summarizer", ev.get("summarizer"))

        llm = Settings.llm
        select_multiple_query_engines = ev.get("select_multi")
        query = ev.get("query")
        query_engine_tools = ev.get("query_engine_tools")

        selector = get_selector_from_llm(
            llm, is_multi=select_multiple_query_engines
        )

        query_engines_metadata = [
            query_engine.metadata for query_engine in query_engine_tools
        ]

        selected_query_engines = await selector.aselect(
            query_engines_metadata, query
        )

        return QueryEngineSelectionEvent(
            selected_query_engines=selected_query_engines
        )

    @step
    async def generate_responses(
        self, ctx: Context, ev: QueryEngineSelectionEvent
    ) -> SynthesizeEvent:
        """Generate the responses from the selected query engines."""

        query = await ctx.get("query", default=None)
        selected_query_engines = ev.selected_query_engines
        query_engine_tools = await ctx.get("query_engine_tools")

        query_engines = [engine.query_engine for engine in query_engine_tools]

        print(
            f"number of selected query engines: {len(selected_query_engines.selections)}"
        )

        if len(selected_query_engines.selections) > 1:
            tasks = []
            for selected_query_engine in selected_query_engines.selections:
                print(
                    f"Selected query engine: {selected_query_engine.index}: {selected_query_engine.reason}"
                )
                query_engine = query_engines[selected_query_engine.index]
                tasks.append(query_engine.aquery(query))

            response_generated = await asyncio.gather(*tasks)

        else:
            query_engine = query_engines[
                selected_query_engines.selections[0].index
            ]

            print(
                f"Selected query engine: {selected_query_engines.ind}: {selected_query_engines.reason}"
            )

            response_generated = [await query_engine.aquery(query)]

        return SynthesizeEvent(
            result=response_generated,
            selected_query_engines=selected_query_engines,
        )

    async def acombine_responses(
        self,
        summarizer: TreeSummarize,
        responses: List[RESPONSE_TYPE],
        query_bundle: QueryBundle,
    ) -> RESPONSE_TYPE:
        """Async combine multiple response from sub-engines."""

        print("Combining responses from multiple query engines.")

        response_strs = []
        source_nodes = []
        for response in responses:
            if isinstance(
                response, (AsyncStreamingResponse, PydanticResponse)
            ):
                response_obj = await response.aget_response()
            else:
                response_obj = response
            source_nodes.extend(response_obj.source_nodes)
            response_strs.append(str(response))

        summary = await summarizer.aget_response(
            query_bundle.query_str, response_strs
        )

        if isinstance(summary, str):
            return Response(response=summary, source_nodes=source_nodes)
        elif isinstance(summary, BaseModel):
            return PydanticResponse(
                response=summary, source_nodes=source_nodes
            )
        else:
            return AsyncStreamingResponse(
                response_gen=summary, source_nodes=source_nodes
            )

    @step
    async def synthesize_responses(
        self, ctx: Context, ev: SynthesizeEvent
    ) -> StopEvent:
        """Synthesizes the responses from the generated responses."""

        response_generated = ev.result
        query = await ctx.get("query", default=None)
        summarizer = await ctx.get("summarizer")
        selected_query_engines = ev.selected_query_engines

        if len(response_generated) > 1:
            response = await self.acombine_responses(
                summarizer, response_generated, QueryBundle(query_str=query)
            )
        else:
            response = response_generated[0]

        response.metadata = response.metadata or {}
        response.metadata["selector_result"] = selected_query_engines

        return StopEvent(result=response)

```

from llama_index.core.workflow import ( Context, Workflow, StartEvent, StopEvent, step, ) from llama_index.llms.openai import OpenAI from llama_index.core.selectors.utils import get_selector_from_llm from llama_index.core.base.response.schema import ( PydanticResponse, Response, AsyncStreamingResponse, ) from llama_index.core.bridge.pydantic import BaseModel from llama_index.core.response_synthesizers import TreeSummarize from llama_index.core.schema import QueryBundle from llama_index.core import Settings from IPython.display import Markdown, display import asyncio class RouterQueryEngineWorkflow(Workflow): @step async def selector( self, ctx: Context, ev: StartEvent ) -> QueryEngineSelectionEvent: """ Selects a single/ multiple query engines based on the query. """ await ctx.set("query", ev.get("query")) await ctx.set("llm", ev.get("llm")) await ctx.set("query_engine_tools", ev.get("query_engine_tools")) await ctx.set("summarizer", ev.get("summarizer")) llm = Settings.llm select_multiple_query_engines = ev.get("select_multi") query = ev.get("query") query_engine_tools = ev.get("query_engine_tools") selector = get_selector_from_llm( llm, is_multi=select_multiple_query_engines ) query_engines_metadata = [ query_engine.metadata for query_engine in query_engine_tools ] selected_query_engines = await selector.aselect( query_engines_metadata, query ) return QueryEngineSelectionEvent( selected_query_engines=selected_query_engines ) @step async def generate_responses( self, ctx: Context, ev: QueryEngineSelectionEvent ) -> SynthesizeEvent: """Generate the responses from the selected query engines.""" query = await ctx.get("query", default=None) selected_query_engines = ev.selected_query_engines query_engine_tools = await ctx.get("query_engine_tools") query_engines = [engine.query_engine for engine in query_engine_tools] print( f"number of selected query engines: {len(selected_query_engines.selections)}" ) if len(selected_query_engines.selections) > 1: tasks = [] for selected_query_engine in selected_query_engines.selections: print( f"Selected query engine: {selected_query_engine.index}: {selected_query_engine.reason}" ) query_engine = query_engines[selected_query_engine.index] tasks.append(query_engine.aquery(query)) response_generated = await asyncio.gather(*tasks) else: query_engine = query_engines[ selected_query_engines.selections[0].index ] print( f"Selected query engine: {selected_query_engines.ind}: {selected_query_engines.reason}" ) response_generated = [await query_engine.aquery(query)] return SynthesizeEvent( result=response_generated, selected_query_engines=selected_query_engines, ) async def acombine_responses( self, summarizer: TreeSummarize, responses: List[RESPONSE_TYPE], query_bundle: QueryBundle, ) -> RESPONSE_TYPE: """Async combine multiple response from sub-engines.""" print("Combining responses from multiple query engines.") response_strs = [] source_nodes = [] for response in responses: if isinstance( response, (AsyncStreamingResponse, PydanticResponse) ): response_obj = await response.aget_response() else: response_obj = response source_nodes.extend(response_obj.source_nodes) response_strs.append(str(response)) summary = await summarizer.aget_response( query_bundle.query_str, response_strs ) if isinstance(summary, str): return Response(response=summary, source_nodes=source_nodes) elif isinstance(summary, BaseModel): return PydanticResponse( response=summary, source_nodes=source_nodes ) else: return AsyncStreamingResponse( response_gen=summary, source_nodes=source_nodes ) @step async def synthesize_responses( self, ctx: Context, ev: SynthesizeEvent ) -> StopEvent: """Synthesizes the responses from the generated responses.""" response_generated = ev.result query = await ctx.get("query", default=None) summarizer = await ctx.get("summarizer") selected_query_engines = ev.selected_query_engines if len(response_generated) > 1: response = await self.acombine_responses( summarizer, response_generated, QueryBundle(query_str=query) ) else: response = response_generated[0] response.metadata = response.metadata or {} response.metadata["selector_result"] = selected_query_engines return StopEvent(result=response)
## Define LLM¶
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4o-mini")
Settings.llm = llm

```

llm = OpenAI(model="gpt-4o-mini") Settings.llm = llm
## Define Summarizer¶
In [ ]:
Copied!
```
from llama_index.core.prompts.default_prompt_selectors import (
    DEFAULT_TREE_SUMMARIZE_PROMPT_SEL,
)

summarizer = TreeSummarize(
    llm=llm,
    summary_template=DEFAULT_TREE_SUMMARIZE_PROMPT_SEL,
)

```

from llama_index.core.prompts.default_prompt_selectors import ( DEFAULT_TREE_SUMMARIZE_PROMPT_SEL, ) summarizer = TreeSummarize( llm=llm, summary_template=DEFAULT_TREE_SUMMARIZE_PROMPT_SEL, )
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-08-26 22:46:42--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8000::154, 2606:50c0:8003::154, 2606:50c0:8002::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8000::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.02s   

2024-08-26 22:46:42 (3.82 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

## Load Data¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data/paul_graham").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data/paul_graham").load_data()
## Create Nodes¶
In [ ]:
Copied!
```
nodes = Settings.node_parser.get_nodes_from_documents(documents)

```

nodes = Settings.node_parser.get_nodes_from_documents(documents)
## Create Indices¶
We will create three indices SummaryIndex, VectorStoreIndex and SimpleKeywordTableIndex.
In [ ]:
Copied!
```
from llama_index.core import (
    VectorStoreIndex,
    SummaryIndex,
    SimpleKeywordTableIndex,
)

summary_index = SummaryIndex(nodes)
vector_index = VectorStoreIndex(nodes)
keyword_index = SimpleKeywordTableIndex(nodes)

```

from llama_index.core import ( VectorStoreIndex, SummaryIndex, SimpleKeywordTableIndex, ) summary_index = SummaryIndex(nodes) vector_index = VectorStoreIndex(nodes) keyword_index = SimpleKeywordTableIndex(nodes)
## Create Query Engine Tools¶
In [ ]:
Copied!
```
from llama_index.core.tools import QueryEngineTool

list_query_engine = summary_index.as_query_engine(
    response_mode="tree_summarize",
    use_async=True,
)
vector_query_engine = vector_index.as_query_engine()
keyword_query_engine = keyword_index.as_query_engine()

list_tool = QueryEngineTool.from_defaults(
    query_engine=list_query_engine,
    description=(
        "Useful for summarization questions related to Paul Graham eassy on"
        " What I Worked On."
    ),
)

vector_tool = QueryEngineTool.from_defaults(
    query_engine=vector_query_engine,
    description=(
        "Useful for retrieving specific context from Paul Graham essay on What"
        " I Worked On."
    ),
)

keyword_tool = QueryEngineTool.from_defaults(
    query_engine=keyword_query_engine,
    description=(
        "Useful for retrieving specific context using keywords from Paul"
        " Graham essay on What I Worked On."
    ),
)

query_engine_tools = [list_tool, vector_tool, keyword_tool]

```

from llama_index.core.tools import QueryEngineTool list_query_engine = summary_index.as_query_engine( response_mode="tree_summarize", use_async=True, ) vector_query_engine = vector_index.as_query_engine() keyword_query_engine = keyword_index.as_query_engine() list_tool = QueryEngineTool.from_defaults( query_engine=list_query_engine, description=( "Useful for summarization questions related to Paul Graham eassy on" " What I Worked On." ), ) vector_tool = QueryEngineTool.from_defaults( query_engine=vector_query_engine, description=( "Useful for retrieving specific context from Paul Graham essay on What" " I Worked On." ), ) keyword_tool = QueryEngineTool.from_defaults( query_engine=keyword_query_engine, description=( "Useful for retrieving specific context using keywords from Paul" " Graham essay on What I Worked On." ), ) query_engine_tools = [list_tool, vector_tool, keyword_tool]
## Run the Workflow!¶
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

w = RouterQueryEngineWorkflow(timeout=200)

```

import nest_asyncio nest_asyncio.apply() w = RouterQueryEngineWorkflow(timeout=200)
### Querying¶
#### Summarization Query¶
In [ ]:
Copied!
```
# This should use summary query engine/ tool.

query = "Provide the summary of the document?"

result = await w.run(
    query=query,
    llm=llm,
    query_engine_tools=query_engine_tools,
    summarizer=summarizer,
    select_multi=True,  # You can change it to default it to select only one query engine.
)

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

# This should use summary query engine/ tool. query = "Provide the summary of the document?" result = await w.run( query=query, llm=llm, query_engine_tools=query_engine_tools, summarizer=summarizer, select_multi=True, # You can change it to default it to select only one query engine. ) display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
```
number of selected query engines: 1
Selected query engine: 0: This choice directly addresses the need for a summary of the document.

```

> Question: Provide the summary of the document?
Answer: The document recounts the journey of an individual who transitioned from writing and programming in his youth to exploring artificial intelligence and eventually becoming a successful entrepreneur and essayist. Initially drawn to philosophy in college, he found it unfulfilling and shifted his focus to AI, inspired by literature and documentaries. His academic pursuits led him to reverse-engineer a natural language program, but he soon realized the limitations of AI at the time.
After completing his PhD, he ventured into the art world, taking classes and painting, while also working on a book about Lisp programming. His experiences in the tech industry, particularly at a software company, shaped his understanding of business dynamics and the importance of being an entry-level option in the market.
In the mid-1990s, he co-founded Viaweb, an early web application for building online stores, which was later acquired by Yahoo. Following this, he became involved in angel investing and co-founded Y Combinator, a startup accelerator that revolutionized seed funding by supporting multiple startups simultaneously.
The narrative highlights the author's reflections on the nature of work, the significance of pursuing unprestigious projects, and the evolution of his interests from programming to writing essays. He emphasizes the value of independent thinking and the impact of the internet on publishing and entrepreneurship. Ultimately, the document illustrates a life characterized by exploration, creativity, and a commitment to helping others succeed in their ventures.
#### Pointed Context Query¶
In [ ]:
Copied!
```
# This should use vector query engine/ tool.

query = "What did the author do growing up?"

result = await w.run(
    query=query,
    llm=llm,
    query_engine_tools=query_engine_tools,
    summarizer=summarizer,
    select_multi=False,  # You can change it to select multiple query engines.
)

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

# This should use vector query engine/ tool. query = "What did the author do growing up?" result = await w.run( query=query, llm=llm, query_engine_tools=query_engine_tools, summarizer=summarizer, select_multi=False, # You can change it to select multiple query engines. ) display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
```
number of selected query engines: 1
Selected query engine: 1: The question asks for specific context about the author's experiences growing up, which aligns with retrieving specific context from the essay.

```

> Question: What did the author do growing up?
Answer: Growing up, the author focused on writing and programming outside of school. Initially, he wrote short stories, which he later described as lacking in plot but rich in character emotions. He began programming at a young age on an IBM 1401, where he experimented with early Fortran and punch cards. Eventually, he convinced his father to buy a TRS-80 microcomputer, which allowed him to write simple games and a word processor. Despite enjoying programming, he initially planned to study philosophy in college, believing it to be a pursuit of ultimate truths. However, he later switched his focus to artificial intelligence after finding philosophy courses unengaging.
In [ ]:
Copied!
```
# This query could use either a keyword or vector query engine
# so it will combine responses from both

query = "What were noteable events and people from the authors time at Interleaf and YC?"

result = await w.run(
    query=query,
    llm=llm,
    query_engine_tools=query_engine_tools,
    summarizer=summarizer,
    select_multi=True,  # Since query should use two query engine tools, we enabled it.
)

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

# This query could use either a keyword or vector query engine # so it will combine responses from both query = "What were noteable events and people from the authors time at Interleaf and YC?" result = await w.run( query=query, llm=llm, query_engine_tools=query_engine_tools, summarizer=summarizer, select_multi=True, # Since query should use two query engine tools, we enabled it. ) display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
```
number of selected query engines: 2
Selected query engine: 1: This choice is useful for retrieving specific context related to notable events and people from the author's time at Interleaf and YC.
Selected query engine: 2: This choice allows for retrieving specific context using keywords, which can help in identifying notable events and people.
Combining responses from multiple query engines.

```

> Question: What were noteable events and people from the authors time at Interleaf and YC?
Answer: Notable events during the author's time at Interleaf included the establishment of a large Release Engineering group, which underscored the complexities of software updates and version management. The company also made a significant decision to incorporate a scripting language inspired by Emacs, aimed at attracting Lisp hackers to enhance their software capabilities. The author reflected on this period as the closest they had to a normal job, despite acknowledging their shortcomings as an employee.
At Y Combinator (YC), key events included the launch of the first Summer Founders Program, which received 225 applications and funded eight startups, featuring notable figures such as the founders of Reddit, Justin Kan and Emmett Shear (who later founded Twitch), and Aaron Swartz. The program fostered a supportive community among founders and marked a transition for YC from a small initiative to a larger organization. Significant individuals during this time included Jessica Livingston, with whom the author had a close professional and personal relationship, as well as Robert Morris and Trevor Blackwell, who contributed to the development of shopping cart software and were recognized for their programming skills, respectively. Sam Altman, who later became the second president of YC, was also mentioned as a significant figure in this period.
