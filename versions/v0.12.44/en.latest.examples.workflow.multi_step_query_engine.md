![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# MultiStep Query Engine¶
The `MultiStepQueryEngine` breaks down a complex query into sequential sub-questions.
To answer the query: In which city did the author found his first company, Viaweb?, we need to answer the following sub-questions sequentially:
  1. Who is the author that founded his first company, Viaweb?
  2. In which city did Paul Graham found his first company, Viaweb?


As an example, the answer from each step (sub-query-1) is used to generate the next step's question (sub-query-2), with steps created sequentially rather than all at once.
In this notebook, we will implement the same with MultiStepQueryEngine using workflows.
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

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
Since workflows are async first, this all runs fine in a notebook. If you were running in your own code, you would want to use `asyncio.run()` to start an async event loop if one isn't already running.
```
async def main():
    <async code>

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

## The Workflow¶
## Designing the Workflow¶
MultiStepQueryEngine consists of some clearly defined steps
  1. Indexing data, creating an index.
  2. Create multiple sub-queries to answer the query.
  3. Synthesize the final response


With this in mind, we can create events and workflow steps to follow this process!
### The Workflow Event¶
To handle these steps, we need to define `QueryMultiStepEvent`
The other steps will use the built-in `StartEvent` and `StopEvent` events.
## Define Event¶
In [ ]:
Copied!
```
from llama_index.core.workflow import Event
from typing import Dict, List, Any
from llama_index.core.schema import NodeWithScore


class QueryMultiStepEvent(Event):
    """
    Event containing results of a multi-step query process.

    Attributes:
        nodes (List[NodeWithScore]): List of nodes with their associated scores.
        source_nodes (List[NodeWithScore]): List of source nodes with their scores.
        final_response_metadata (Dict[str, Any]): Metadata associated with the final response.
    """

    nodes: List[NodeWithScore]
    source_nodes: List[NodeWithScore]
    final_response_metadata: Dict[str, Any]

```

from llama_index.core.workflow import Event from typing import Dict, List, Any from llama_index.core.schema import NodeWithScore class QueryMultiStepEvent(Event): """ Event containing results of a multi-step query process. Attributes: nodes (List[NodeWithScore]): List of nodes with their associated scores. source_nodes (List[NodeWithScore]): List of source nodes with their scores. final_response_metadata (Dict[str, Any]): Metadata associated with the final response. """ nodes: List[NodeWithScore] source_nodes: List[NodeWithScore] final_response_metadata: Dict[str, Any]
```
[nltk_data] Downloading package punkt_tab to
[nltk_data]     /Users/ravithejad/Desktop/llamaindex/lib/python3.9/sit
[nltk_data]     e-packages/llama_index/core/_static/nltk_cache...
[nltk_data]   Package punkt_tab is already up-to-date!

```

## Define Workflow¶
In [ ]:
Copied!
```
from llama_index.core.indices.query.query_transform.base import (
    StepDecomposeQueryTransform,
)
from llama_index.core.response_synthesizers import (
    get_response_synthesizer,
)

from llama_index.core.schema import QueryBundle, TextNode

from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)

from llama_index.core import Settings
from llama_index.core.llms import LLM

from typing import cast
from IPython.display import Markdown, display


class MultiStepQueryEngineWorkflow(Workflow):
    def combine_queries(
        self,
        query_bundle: QueryBundle,
        prev_reasoning: str,
        index_summary: str,
        llm: LLM,
    ) -> QueryBundle:
        """Combine queries using StepDecomposeQueryTransform."""
        transform_metadata = {
            "prev_reasoning": prev_reasoning,
            "index_summary": index_summary,
        }
        return StepDecomposeQueryTransform(llm=llm)(
            query_bundle, metadata=transform_metadata
        )

    def default_stop_fn(self, stop_dict: Dict) -> bool:
        """Stop function for multi-step query combiner."""
        query_bundle = cast(QueryBundle, stop_dict.get("query_bundle"))
        if query_bundle is None:
            raise ValueError("Response must be provided to stop function.")

        return "none" in query_bundle.query_str.lower()

    @step
    async def query_multistep(
        self, ctx: Context, ev: StartEvent
    ) -> QueryMultiStepEvent:
        """Execute multi-step query process."""
        prev_reasoning = ""
        cur_response = None
        should_stop = False
        cur_steps = 0

        # use response
        final_response_metadata: Dict[str, Any] = {"sub_qa": []}

        text_chunks = []
        source_nodes = []

        query = ev.get("query")
        await ctx.set("query", ev.get("query"))

        llm = Settings.llm
        stop_fn = self.default_stop_fn

        num_steps = ev.get("num_steps")
        query_engine = ev.get("query_engine")
        index_summary = ev.get("index_summary")

        while not should_stop:
            if num_steps is not None and cur_steps >= num_steps:
                should_stop = True
                break
            elif should_stop:
                break

            updated_query_bundle = self.combine_queries(
                QueryBundle(query_str=query),
                prev_reasoning,
                index_summary,
                llm,
            )

            print(
                f"Created query for the step - {cur_steps} is: {updated_query_bundle}"
            )

            stop_dict = {"query_bundle": updated_query_bundle}
            if stop_fn(stop_dict):
                should_stop = True
                break

            cur_response = query_engine.query(updated_query_bundle)

            # append to response builder
            cur_qa_text = (
                f"\nQuestion: {updated_query_bundle.query_str}\n"
                f"Answer: {cur_response!s}"
            )
            text_chunks.append(cur_qa_text)
            for source_node in cur_response.source_nodes:
                source_nodes.append(source_node)
            # update metadata
            final_response_metadata["sub_qa"].append(
                (updated_query_bundle.query_str, cur_response)
            )

            prev_reasoning += (
                f"- {updated_query_bundle.query_str}\n" f"- {cur_response!s}\n"
            )
            cur_steps += 1

        nodes = [
            NodeWithScore(node=TextNode(text=text_chunk))
            for text_chunk in text_chunks
        ]
        return QueryMultiStepEvent(
            nodes=nodes,
            source_nodes=source_nodes,
            final_response_metadata=final_response_metadata,
        )

    @step
    async def synthesize(
        self, ctx: Context, ev: QueryMultiStepEvent
    ) -> StopEvent:
        """Synthesize the response."""
        response_synthesizer = get_response_synthesizer()
        query = await ctx.get("query", default=None)
        final_response = await response_synthesizer.asynthesize(
            query=query,
            nodes=ev.nodes,
            additional_source_nodes=ev.source_nodes,
        )
        final_response.metadata = ev.final_response_metadata

        return StopEvent(result=final_response)

```

from llama_index.core.indices.query.query_transform.base import ( StepDecomposeQueryTransform, ) from llama_index.core.response_synthesizers import ( get_response_synthesizer, ) from llama_index.core.schema import QueryBundle, TextNode from llama_index.core.workflow import ( Context, Workflow, StartEvent, StopEvent, step, ) from llama_index.core import Settings from llama_index.core.llms import LLM from typing import cast from IPython.display import Markdown, display class MultiStepQueryEngineWorkflow(Workflow): def combine_queries( self, query_bundle: QueryBundle, prev_reasoning: str, index_summary: str, llm: LLM, ) -> QueryBundle: """Combine queries using StepDecomposeQueryTransform.""" transform_metadata = { "prev_reasoning": prev_reasoning, "index_summary": index_summary, } return StepDecomposeQueryTransform(llm=llm)( query_bundle, metadata=transform_metadata ) def default_stop_fn(self, stop_dict: Dict) -> bool: """Stop function for multi-step query combiner.""" query_bundle = cast(QueryBundle, stop_dict.get("query_bundle")) if query_bundle is None: raise ValueError("Response must be provided to stop function.") return "none" in query_bundle.query_str.lower() @step async def query_multistep( self, ctx: Context, ev: StartEvent ) -> QueryMultiStepEvent: """Execute multi-step query process.""" prev_reasoning = "" cur_response = None should_stop = False cur_steps = 0 # use response final_response_metadata: Dict[str, Any] = {"sub_qa": []} text_chunks = [] source_nodes = [] query = ev.get("query") await ctx.set("query", ev.get("query")) llm = Settings.llm stop_fn = self.default_stop_fn num_steps = ev.get("num_steps") query_engine = ev.get("query_engine") index_summary = ev.get("index_summary") while not should_stop: if num_steps is not None and cur_steps >= num_steps: should_stop = True break elif should_stop: break updated_query_bundle = self.combine_queries( QueryBundle(query_str=query), prev_reasoning, index_summary, llm, ) print( f"Created query for the step - {cur_steps} is: {updated_query_bundle}" ) stop_dict = {"query_bundle": updated_query_bundle} if stop_fn(stop_dict): should_stop = True break cur_response = query_engine.query(updated_query_bundle) # append to response builder cur_qa_text = ( f"\nQuestion: {updated_query_bundle.query_str}\n" f"Answer: {cur_response!s}" ) text_chunks.append(cur_qa_text) for source_node in cur_response.source_nodes: source_nodes.append(source_node) # update metadata final_response_metadata["sub_qa"].append( (updated_query_bundle.query_str, cur_response) ) prev_reasoning += ( f"- {updated_query_bundle.query_str}\n" f"- {cur_response!s}\n" ) cur_steps += 1 nodes = [ NodeWithScore(node=TextNode(text=text_chunk)) for text_chunk in text_chunks ] return QueryMultiStepEvent( nodes=nodes, source_nodes=source_nodes, final_response_metadata=final_response_metadata, ) @step async def synthesize( self, ctx: Context, ev: QueryMultiStepEvent ) -> StopEvent: """Synthesize the response.""" response_synthesizer = get_response_synthesizer() query = await ctx.get("query", default=None) final_response = await response_synthesizer.asynthesize( query=query, nodes=ev.nodes, additional_source_nodes=ev.source_nodes, ) final_response.metadata = ev.final_response_metadata return StopEvent(result=final_response)
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-08-26 14:16:04--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8000::154, 2606:50c0:8002::154, 2606:50c0:8001::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8000::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.01s   

2024-08-26 14:16:04 (6.91 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

## Load data¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("data/paul_graham").load_data()

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("data/paul_graham").load_data()
## Setup LLM¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4")

Settings.llm = llm

```

from llama_index.llms.openai import OpenAI llm = OpenAI(model="gpt-4") Settings.llm = llm
## Create Index and QueryEngine¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex

index = VectorStoreIndex.from_documents(
    documents=documents,
)

query_engine = index.as_query_engine()

```

from llama_index.core import VectorStoreIndex index = VectorStoreIndex.from_documents( documents=documents, ) query_engine = index.as_query_engine()
## Run the Workflow!¶
In [ ]:
Copied!
```
w = MultiStepQueryEngineWorkflow(timeout=200)

```

w = MultiStepQueryEngineWorkflow(timeout=200)
### Set the parameters¶
In [ ]:
Copied!
```
# Sets maximum number of steps taken to answer the query.
num_steps = 3

# Set summary of the index, useful to create modified query at each step.
index_summary = "Used to answer questions about the author"

```

# Sets maximum number of steps taken to answer the query. num_steps = 3 # Set summary of the index, useful to create modified query at each step. index_summary = "Used to answer questions about the author"
### Test with a query¶
In [ ]:
Copied!
```
query = "In which city did the author found his first company, Viaweb?"

```

query = "In which city did the author found his first company, Viaweb?"
### Result¶
In [ ]:
Copied!
```
result = await w.run(
    query=query,
    query_engine=query_engine,
    index_summary=index_summary,
    num_steps=num_steps,
)

# If created query in a step is None, the process will be stopped.

display(
    Markdown("> Question: {}".format(query)),
    Markdown("Answer: {}".format(result)),
)

```

result = await w.run( query=query, query_engine=query_engine, index_summary=index_summary, num_steps=num_steps, ) # If created query in a step is None, the process will be stopped. display( Markdown("> Question: {}".format(query)), Markdown("Answer: {}".format(result)), )
```
Created query for the step - 0 is: Who is the author who founded Viaweb?
Created query for the step - 1 is: In which city did Paul Graham found his first company, Viaweb?
Created query for the step - 2 is: None

```

> Question: In which city did the author found his first company, Viaweb?
Answer: The author founded his first company, Viaweb, in Cambridge.
### Display step-queries created¶
In [ ]:
Copied!
```
sub_qa = result.metadata["sub_qa"]
tuples = [(t[0], t[1].response) for t in sub_qa]
display(Markdown(f"{tuples}"))

```

sub_qa = result.metadata["sub_qa"] tuples = [(t[0], t[1].response) for t in sub_qa] display(Markdown(f"{tuples}"))
[('Who is the author who founded Viaweb?', 'The author who founded Viaweb is Paul Graham.'), ('In which city did Paul Graham found his first company, Viaweb?', 'Paul Graham founded his first company, Viaweb, in Cambridge.')]
