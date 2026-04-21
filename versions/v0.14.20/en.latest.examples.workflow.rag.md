# RAG Workflow with Reranking¶
This notebook walks through setting up a `Workflow` to perform basic RAG with reranking.
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

os.environ["OPENAI_API_KEY"] = "sk-proj-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-proj-..."
### [Optional] Set up observability with Llamatrace¶
Set up tracing to visualize each step in the workflow.
In [ ]:
Copied!
```
%pip install "openinference-instrumentation-llama-index>=3.0.0" "opentelemetry-proto>=1.12.0" opentelemetry-exporter-otlp opentelemetry-sdk

```

%pip install "openinference-instrumentation-llama-index>=3.0.0" "opentelemetry-proto>=1.12.0" opentelemetry-exporter-otlp opentelemetry-sdk
In [ ]:
Copied!
```
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter as HTTPSpanExporter,
)
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor


# Add Phoenix API Key for tracing
PHOENIX_API_KEY = "<YOUR-PHOENIX-API-KEY>"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={PHOENIX_API_KEY}"

# Add Phoenix
span_phoenix_processor = SimpleSpanProcessor(
    HTTPSpanExporter(endpoint="https://app.phoenix.arize.com/v1/traces")
)

# Add them to the tracer
tracer_provider = trace_sdk.TracerProvider()
tracer_provider.add_span_processor(span_processor=span_phoenix_processor)

# Instrument the application
LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

```

from opentelemetry.sdk import trace as trace_sdk from opentelemetry.sdk.trace.export import SimpleSpanProcessor from opentelemetry.exporter.otlp.proto.http.trace_exporter import ( OTLPSpanExporter as HTTPSpanExporter, ) from openinference.instrumentation.llama_index import LlamaIndexInstrumentor # Add Phoenix API Key for tracing PHOENIX_API_KEY = "" os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"api_key={PHOENIX_API_KEY}" # Add Phoenix span_phoenix_processor = SimpleSpanProcessor( HTTPSpanExporter(endpoint="https://app.phoenix.arize.com/v1/traces") ) # Add them to the tracer tracer_provider = trace_sdk.TracerProvider() tracer_provider.add_span_processor(span_processor=span_phoenix_processor) # Instrument the application LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)
In [ ]:
Copied!
```
!mkdir -p data
!wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"

```

!mkdir -p data !wget --user-agent "Mozilla" "https://arxiv.org/pdf/2307.09288.pdf" -O "data/llama2.pdf"
Since workflows are async first, this all runs fine in a notebook. If you were running in your own code, you would want to use `asyncio.run()` to start an async event loop if one isn't already running.
```
async def main():
    <async code>

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

## Designing the Workflow¶
RAG + Reranking consists of some clearly defined steps
  1. Indexing data, creating an index
  2. Using that index + a query to retrieve relevant text chunks
  3. Rerank the text retrieved text chunks using the original query
  4. Synthesizing a final response


With this in mind, we can create events and workflow steps to follow this process!
### The Workflow Events¶
To handle these steps, we need to define a few events:
  1. An event to pass retrieved nodes to the reranker
  2. An event to pass reranked nodes to the synthesizer


The other steps will use the built-in `StartEvent` and `StopEvent` events.
In [ ]:
Copied!
```
from llama_index.core.workflow import Event
from llama_index.core.schema import NodeWithScore


class RetrieverEvent(Event):
    """Result of running retrieval"""

    nodes: list[NodeWithScore]


class RerankEvent(Event):
    """Result of running reranking on retrieved nodes"""

    nodes: list[NodeWithScore]

```

from llama_index.core.workflow import Event from llama_index.core.schema import NodeWithScore class RetrieverEvent(Event): """Result of running retrieval""" nodes: list[NodeWithScore] class RerankEvent(Event): """Result of running reranking on retrieved nodes""" nodes: list[NodeWithScore]
### The Workflow Itself¶
With our events defined, we can construct our workflow and steps.
Note that the workflow automatically validates itself using type annotations, so the type annotations on our steps are very helpful!
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.response_synthesizers import CompactAndRefine
from llama_index.core.postprocessor.llm_rerank import LLMRerank
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding


class RAGWorkflow(Workflow):
    @step
    async def ingest(self, ctx: Context, ev: StartEvent) -> StopEvent | None:
        """Entry point to ingest a document, triggered by a StartEvent with `dirname`."""
        dirname = ev.get("dirname")
        if not dirname:
            return None

        documents = SimpleDirectoryReader(dirname).load_data()
        index = VectorStoreIndex.from_documents(
            documents=documents,
            embed_model=OpenAIEmbedding(model_name="text-embedding-3-small"),
        )
        return StopEvent(result=index)

    @step
    async def retrieve(
        self, ctx: Context, ev: StartEvent
    ) -> RetrieverEvent | None:
        "Entry point for RAG, triggered by a StartEvent with `query`."
        query = ev.get("query")
        index = ev.get("index")

        if not query:
            return None

        print(f"Query the database with: {query}")

        # store the query in the global context
        await ctx.store.set("query", query)

        # get the index from the global context
        if index is None:
            print("Index is empty, load some documents before querying!")
            return None

        retriever = index.as_retriever(similarity_top_k=2)
        nodes = await retriever.aretrieve(query)
        print(f"Retrieved {len(nodes)} nodes.")
        return RetrieverEvent(nodes=nodes)

    @step
    async def rerank(self, ctx: Context, ev: RetrieverEvent) -> RerankEvent:
        # Rerank the nodes
        ranker = LLMRerank(
            choice_batch_size=5, top_n=3, llm=OpenAI(model="gpt-4o-mini")
        )
        print(await ctx.store.get("query", default=None), flush=True)
        new_nodes = ranker.postprocess_nodes(
            ev.nodes, query_str=await ctx.store.get("query", default=None)
        )
        print(f"Reranked nodes to {len(new_nodes)}")
        return RerankEvent(nodes=new_nodes)

    @step
    async def synthesize(self, ctx: Context, ev: RerankEvent) -> StopEvent:
        """Return a streaming response using reranked nodes."""
        llm = OpenAI(model="gpt-4o-mini")
        summarizer = CompactAndRefine(llm=llm, streaming=True, verbose=True)
        query = await ctx.store.get("query", default=None)

        response = await summarizer.asynthesize(query, nodes=ev.nodes)
        return StopEvent(result=response)

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.core.response_synthesizers import CompactAndRefine from llama_index.core.postprocessor.llm_rerank import LLMRerank from llama_index.core.workflow import ( Context, Workflow, StartEvent, StopEvent, step, ) from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding class RAGWorkflow(Workflow): @step async def ingest(self, ctx: Context, ev: StartEvent) -> StopEvent | None: """Entry point to ingest a document, triggered by a StartEvent with `dirname`.""" dirname = ev.get("dirname") if not dirname: return None documents = SimpleDirectoryReader(dirname).load_data() index = VectorStoreIndex.from_documents( documents=documents, embed_model=OpenAIEmbedding(model_name="text-embedding-3-small"), ) return StopEvent(result=index) @step async def retrieve( self, ctx: Context, ev: StartEvent ) -> RetrieverEvent | None: "Entry point for RAG, triggered by a StartEvent with `query`." query = ev.get("query") index = ev.get("index") if not query: return None print(f"Query the database with: {query}") # store the query in the global context await ctx.store.set("query", query) # get the index from the global context if index is None: print("Index is empty, load some documents before querying!") return None retriever = index.as_retriever(similarity_top_k=2) nodes = await retriever.aretrieve(query) print(f"Retrieved {len(nodes)} nodes.") return RetrieverEvent(nodes=nodes) @step async def rerank(self, ctx: Context, ev: RetrieverEvent) -> RerankEvent: # Rerank the nodes ranker = LLMRerank( choice_batch_size=5, top_n=3, llm=OpenAI(model="gpt-4o-mini") ) print(await ctx.store.get("query", default=None), flush=True) new_nodes = ranker.postprocess_nodes( ev.nodes, query_str=await ctx.store.get("query", default=None) ) print(f"Reranked nodes to {len(new_nodes)}") return RerankEvent(nodes=new_nodes) @step async def synthesize(self, ctx: Context, ev: RerankEvent) -> StopEvent: """Return a streaming response using reranked nodes.""" llm = OpenAI(model="gpt-4o-mini") summarizer = CompactAndRefine(llm=llm, streaming=True, verbose=True) query = await ctx.store.get("query", default=None) response = await summarizer.asynthesize(query, nodes=ev.nodes) return StopEvent(result=response)
And thats it! Let's explore the workflow we wrote a bit.
  * We have two entry points (the steps that accept `StartEvent`)
  * The steps themselves decide when they can run
  * The workflow context is used to store the user query
  * The nodes are passed around, and finally a streaming response is returned


### Run the Workflow!¶
In [ ]:
Copied!
```
w = RAGWorkflow()

# Ingest the documents
index = await w.run(dirname="data")

```

w = RAGWorkflow() # Ingest the documents index = await w.run(dirname="data")
In [ ]:
Copied!
```
# Run a query
result = await w.run(query="How was Llama2 trained?", index=index)
async for chunk in result.async_response_gen():
    print(chunk, end="", flush=True)

```

# Run a query result = await w.run(query="How was Llama2 trained?", index=index) async for chunk in result.async_response_gen(): print(chunk, end="", flush=True)
```
Query the database with: How was Llama2 trained?
Retrieved 2 nodes.
How was Llama2 trained?
Reranked nodes to 2
Llama 2 was trained through a multi-step process that began with pretraining using publicly available online sources. This was followed by the creation of an initial version of Llama 2-Chat through supervised fine-tuning. The model was then iteratively refined using Reinforcement Learning with Human Feedback (RLHF) methodologies, which included rejection sampling and Proximal Policy Optimization (PPO). 

During pretraining, the model utilized an optimized auto-regressive transformer architecture, incorporating robust data cleaning, updated data mixes, and training on a significantly larger dataset of 2 trillion tokens. The training process also involved increased context length and the use of grouped-query attention (GQA) to enhance inference scalability.

The training employed the AdamW optimizer with specific hyperparameters, including a cosine learning rate schedule and gradient clipping. The models were pretrained on Meta’s Research SuperCluster and internal production clusters, utilizing NVIDIA A100 GPUs.
```

