# Corrective RAG Workflow¶
This notebook shows how to implement corrective RAG using Llamaindex workflows based on this paper
A brief understanding of the paper:
Corrective Retrieval Augmented Generation (CRAG) is a method designed to enhance the robustness of language model generation by evaluating and augmenting the relevance of retrieved documents through an evaluator and large-scale web searches, ensuring more accurate and reliable information is used in generation.
We use `GPT-4` as a relevancy evaluator and `Tavily AI` for web searches. So, we recommend getting `OPENAI_API_KEY` and `tavily_ai_api_key` before proceeding further.
In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
%pip install -U llama-index llama-index-tools-tavily-research

```

%pip install -U llama-index llama-index-tools-tavily-research
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-proj-..."
tavily_ai_api_key = "<Your Tavily AI API Key>"

```

import os os.environ["OPENAI_API_KEY"] = "sk-proj-..." tavily_ai_api_key = ""
In [ ]:
Copied!
```
!mkdir -p 'data/'
!wget 'https://arxiv.org/pdf/2307.09288.pdf' -O 'data/llama2.pdf'

```

!mkdir -p 'data/' !wget 'https://arxiv.org/pdf/2307.09288.pdf' -O 'data/llama2.pdf'
Since workflows are async first, this all runs fine in a notebook. If you were running in your own code, you would want to use `asyncio.run()` to start an async event loop if one isn't already running.
```
async def main():
    <async code>

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

## Designing the Workflow¶
Corrective RAG consists of the following steps:
  1. Ingestion of data — Loads the data into an index and setting up Tavily AI. The ingestion step will be run by itself, taking in a start event and returning a stop event.
  2. Retrieval - Retrives the most relevant nodes based on the query.
  3. Relevance evaluation - Uses an LLM to determine whether the retrieved nodes are relevant to the query given the content of the nodes.
  4. Relevance extraction - Extracts the nodes which the LLM determined to be relevant.
  5. Query transformation and Tavily search - If a node is irrelevant, then uses an LLM to transform the query to tailor towards a web search. Uses Tavily to search the web for a relevant answer based on the query.
  6. Response generation - Builds a summary index given the text from the relevant nodes and the Tavily search and uses this index to get a result given the original query.


The following events are needed:
  1. `PrepEvent` - Event signifying that the index and other objects are prepared.
  2. `RetrieveEvent` - Event containing information about the retrieved nodes.
  3. `RelevanceEvalEvent` - Event containing a list of the results of the relevance evaluation.
  4. `TextExtractEvent` - Event containing the concatenated string of relevant text from relevant nodes.
  5. `QueryEvent` - Event containing both the relevant text and search text.


In [ ]:
Copied!
```
from llama_index.core.workflow import Event
from llama_index.core.schema import NodeWithScore


class PrepEvent(Event):
    """Prep event (prepares for retrieval)."""

    pass


class RetrieveEvent(Event):
    """Retrieve event (gets retrieved nodes)."""

    retrieved_nodes: list[NodeWithScore]


class RelevanceEvalEvent(Event):
    """Relevance evaluation event (gets results of relevance evaluation)."""

    relevant_results: list[str]


class TextExtractEvent(Event):
    """Text extract event. Extracts relevant text and concatenates."""

    relevant_text: str


class QueryEvent(Event):
    """Query event. Queries given relevant text and search text."""

    relevant_text: str
    search_text: str

```

from llama_index.core.workflow import Event from llama_index.core.schema import NodeWithScore class PrepEvent(Event): """Prep event (prepares for retrieval).""" pass class RetrieveEvent(Event): """Retrieve event (gets retrieved nodes).""" retrieved_nodes: list[NodeWithScore] class RelevanceEvalEvent(Event): """Relevance evaluation event (gets results of relevance evaluation).""" relevant_results: list[str] class TextExtractEvent(Event): """Text extract event. Extracts relevant text and concatenates.""" relevant_text: str class QueryEvent(Event): """Query event. Queries given relevant text and search text.""" relevant_text: str search_text: str
Below is the code for the corrective RAG workflow:
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Workflow,
    step,
    Context,
    StartEvent,
    StopEvent,
)
from llama_index.core import (
    VectorStoreIndex,
    Document,
    PromptTemplate,
    SummaryIndex,
)
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.llms.openai import OpenAI
from llama_index.tools.tavily_research.base import TavilyToolSpec
from llama_index.core.base.base_retriever import BaseRetriever

DEFAULT_RELEVANCY_PROMPT_TEMPLATE = PromptTemplate(
    template="""As a grader, your task is to evaluate the relevance of a document retrieved in response to a user's question.

    Retrieved Document:
    -------------------
    {context_str}

    User Question:
    --------------
    {query_str}

    Evaluation Criteria:
    - Consider whether the document contains keywords or topics related to the user's question.
    - The evaluation should not be overly stringent; the primary objective is to identify and filter out clearly irrelevant retrievals.

    Decision:
    - Assign a binary score to indicate the document's relevance.
    - Use 'yes' if the document is relevant to the question, or 'no' if it is not.

    Please provide your binary score ('yes' or 'no') below to indicate the document's relevance to the user question."""
)

DEFAULT_TRANSFORM_QUERY_TEMPLATE = PromptTemplate(
    template="""Your task is to refine a query to ensure it is highly effective for retrieving relevant search results. \n
    Analyze the given input to grasp the core semantic intent or meaning. \n
    Original Query:
    \n ------- \n
    {query_str}
    \n ------- \n
    Your goal is to rephrase or enhance this query to improve its search performance. Ensure the revised query is concise and directly aligned with the intended search objective. \n
    Respond with the optimized query only:"""
)


class CorrectiveRAGWorkflow(Workflow):
    @step
    async def ingest(self, ctx: Context, ev: StartEvent) -> StopEvent | None:
        """Ingest step (for ingesting docs and initializing index)."""
        documents: list[Document] | None = ev.get("documents")

        if documents is None:
            return None

        index = VectorStoreIndex.from_documents(documents)

        return StopEvent(result=index)

    @step
    async def prepare_for_retrieval(
        self, ctx: Context, ev: StartEvent
    ) -> PrepEvent | None:
        """Prepare for retrieval."""

        query_str: str | None = ev.get("query_str")
        retriever_kwargs: dict | None = ev.get("retriever_kwargs", {})

        if query_str is None:
            return None

        tavily_ai_apikey: str | None = ev.get("tavily_ai_apikey")
        index = ev.get("index")

        llm = OpenAI(model="gpt-4")
        await ctx.store.set(
            "relevancy_pipeline",
            QueryPipeline(chain=[DEFAULT_RELEVANCY_PROMPT_TEMPLATE, llm]),
        )
        await ctx.store.set(
            "transform_query_pipeline",
            QueryPipeline(chain=[DEFAULT_TRANSFORM_QUERY_TEMPLATE, llm]),
        )

        await ctx.store.set("llm", llm)
        await ctx.store.set("index", index)
        await ctx.store.set(
            "tavily_tool", TavilyToolSpec(api_key=tavily_ai_apikey)
        )

        await ctx.store.set("query_str", query_str)
        await ctx.store.set("retriever_kwargs", retriever_kwargs)

        return PrepEvent()

    @step
    async def retrieve(
        self, ctx: Context, ev: PrepEvent
    ) -> RetrieveEvent | None:
        """Retrieve the relevant nodes for the query."""
        query_str = await ctx.store.get("query_str")
        retriever_kwargs = await ctx.store.get("retriever_kwargs")

        if query_str is None:
            return None

        index = await ctx.store.get("index", default=None)
        tavily_tool = await ctx.store.get("tavily_tool", default=None)
        if not (index or tavily_tool):
            raise ValueError(
                "Index and tavily tool must be constructed. Run with 'documents' and 'tavily_ai_apikey' params first."
            )

        retriever: BaseRetriever = index.as_retriever(**retriever_kwargs)
        result = retriever.retrieve(query_str)
        await ctx.store.set("retrieved_nodes", result)
        await ctx.store.set("query_str", query_str)
        return RetrieveEvent(retrieved_nodes=result)

    @step
    async def eval_relevance(
        self, ctx: Context, ev: RetrieveEvent
    ) -> RelevanceEvalEvent:
        """Evaluate relevancy of retrieved documents with the query."""
        retrieved_nodes = ev.retrieved_nodes
        query_str = await ctx.store.get("query_str")

        relevancy_results = []
        for node in retrieved_nodes:
            relevancy_pipeline = await ctx.store.get("relevancy_pipeline")
            relevancy = relevancy_pipeline.run(
                context_str=node.text, query_str=query_str
            )
            relevancy_results.append(relevancy.message.content.lower().strip())

        await ctx.store.set("relevancy_results", relevancy_results)
        return RelevanceEvalEvent(relevant_results=relevancy_results)

    @step
    async def extract_relevant_texts(
        self, ctx: Context, ev: RelevanceEvalEvent
    ) -> TextExtractEvent:
        """Extract relevant texts from retrieved documents."""
        retrieved_nodes = await ctx.store.get("retrieved_nodes")
        relevancy_results = ev.relevant_results

        relevant_texts = [
            retrieved_nodes[i].text
            for i, result in enumerate(relevancy_results)
            if result == "yes"
        ]

        result = "\n".join(relevant_texts)
        return TextExtractEvent(relevant_text=result)

    @step
    async def transform_query_pipeline(
        self, ctx: Context, ev: TextExtractEvent
    ) -> QueryEvent:
        """Search the transformed query with Tavily API."""
        relevant_text = ev.relevant_text
        relevancy_results = await ctx.store.get("relevancy_results")
        query_str = await ctx.store.get("query_str")

        # If any document is found irrelevant, transform the query string for better search results.
        if "no" in relevancy_results:
            qp = await ctx.store.get("transform_query_pipeline")
            transformed_query_str = qp.run(query_str=query_str).message.content
            # Conduct a search with the transformed query string and collect the results.
            tavily_tool = await ctx.store.get("tavily_tool")
            search_results = tavily_tool.search(
                transformed_query_str, max_results=5
            )
            search_text = "\n".join([result.text for result in search_results])
        else:
            search_text = ""

        return QueryEvent(relevant_text=relevant_text, search_text=search_text)

    @step
    async def query_result(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        """Get result with relevant text."""
        relevant_text = ev.relevant_text
        search_text = ev.search_text
        query_str = await ctx.store.get("query_str")

        documents = [Document(text=relevant_text + "\n" + search_text)]
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        result = query_engine.query(query_str)
        return StopEvent(result=result)

```

from llama_index.core.workflow import ( Workflow, step, Context, StartEvent, StopEvent, ) from llama_index.core import ( VectorStoreIndex, Document, PromptTemplate, SummaryIndex, ) from llama_index.core.query_pipeline import QueryPipeline from llama_index.llms.openai import OpenAI from llama_index.tools.tavily_research.base import TavilyToolSpec from llama_index.core.base.base_retriever import BaseRetriever DEFAULT_RELEVANCY_PROMPT_TEMPLATE = PromptTemplate( template="""As a grader, your task is to evaluate the relevance of a document retrieved in response to a user's question. Retrieved Document: ------------------- {context_str} User Question: -------------- {query_str} Evaluation Criteria: - Consider whether the document contains keywords or topics related to the user's question. - The evaluation should not be overly stringent; the primary objective is to identify and filter out clearly irrelevant retrievals. Decision: - Assign a binary score to indicate the document's relevance. - Use 'yes' if the document is relevant to the question, or 'no' if it is not. Please provide your binary score ('yes' or 'no') below to indicate the document's relevance to the user question.""" ) DEFAULT_TRANSFORM_QUERY_TEMPLATE = PromptTemplate( template="""Your task is to refine a query to ensure it is highly effective for retrieving relevant search results. \n Analyze the given input to grasp the core semantic intent or meaning. \n Original Query: \n ------- \n {query_str} \n ------- \n Your goal is to rephrase or enhance this query to improve its search performance. Ensure the revised query is concise and directly aligned with the intended search objective. \n Respond with the optimized query only:""" ) class CorrectiveRAGWorkflow(Workflow): @step async def ingest(self, ctx: Context, ev: StartEvent) -> StopEvent | None: """Ingest step (for ingesting docs and initializing index).""" documents: list[Document] | None = ev.get("documents") if documents is None: return None index = VectorStoreIndex.from_documents(documents) return StopEvent(result=index) @step async def prepare_for_retrieval( self, ctx: Context, ev: StartEvent ) -> PrepEvent | None: """Prepare for retrieval.""" query_str: str | None = ev.get("query_str") retriever_kwargs: dict | None = ev.get("retriever_kwargs", {}) if query_str is None: return None tavily_ai_apikey: str | None = ev.get("tavily_ai_apikey") index = ev.get("index") llm = OpenAI(model="gpt-4") await ctx.store.set( "relevancy_pipeline", QueryPipeline(chain=[DEFAULT_RELEVANCY_PROMPT_TEMPLATE, llm]), ) await ctx.store.set( "transform_query_pipeline", QueryPipeline(chain=[DEFAULT_TRANSFORM_QUERY_TEMPLATE, llm]), ) await ctx.store.set("llm", llm) await ctx.store.set("index", index) await ctx.store.set( "tavily_tool", TavilyToolSpec(api_key=tavily_ai_apikey) ) await ctx.store.set("query_str", query_str) await ctx.store.set("retriever_kwargs", retriever_kwargs) return PrepEvent() @step async def retrieve( self, ctx: Context, ev: PrepEvent ) -> RetrieveEvent | None: """Retrieve the relevant nodes for the query.""" query_str = await ctx.store.get("query_str") retriever_kwargs = await ctx.store.get("retriever_kwargs") if query_str is None: return None index = await ctx.store.get("index", default=None) tavily_tool = await ctx.store.get("tavily_tool", default=None) if not (index or tavily_tool): raise ValueError( "Index and tavily tool must be constructed. Run with 'documents' and 'tavily_ai_apikey' params first." ) retriever: BaseRetriever = index.as_retriever(**retriever_kwargs) result = retriever.retrieve(query_str) await ctx.store.set("retrieved_nodes", result) await ctx.store.set("query_str", query_str) return RetrieveEvent(retrieved_nodes=result) @step async def eval_relevance( self, ctx: Context, ev: RetrieveEvent ) -> RelevanceEvalEvent: """Evaluate relevancy of retrieved documents with the query.""" retrieved_nodes = ev.retrieved_nodes query_str = await ctx.store.get("query_str") relevancy_results = [] for node in retrieved_nodes: relevancy_pipeline = await ctx.store.get("relevancy_pipeline") relevancy = relevancy_pipeline.run( context_str=node.text, query_str=query_str ) relevancy_results.append(relevancy.message.content.lower().strip()) await ctx.store.set("relevancy_results", relevancy_results) return RelevanceEvalEvent(relevant_results=relevancy_results) @step async def extract_relevant_texts( self, ctx: Context, ev: RelevanceEvalEvent ) -> TextExtractEvent: """Extract relevant texts from retrieved documents.""" retrieved_nodes = await ctx.store.get("retrieved_nodes") relevancy_results = ev.relevant_results relevant_texts = [ retrieved_nodes[i].text for i, result in enumerate(relevancy_results) if result == "yes" ] result = "\n".join(relevant_texts) return TextExtractEvent(relevant_text=result) @step async def transform_query_pipeline( self, ctx: Context, ev: TextExtractEvent ) -> QueryEvent: """Search the transformed query with Tavily API.""" relevant_text = ev.relevant_text relevancy_results = await ctx.store.get("relevancy_results") query_str = await ctx.store.get("query_str") # If any document is found irrelevant, transform the query string for better search results. if "no" in relevancy_results: qp = await ctx.store.get("transform_query_pipeline") transformed_query_str = qp.run(query_str=query_str).message.content # Conduct a search with the transformed query string and collect the results. tavily_tool = await ctx.store.get("tavily_tool") search_results = tavily_tool.search( transformed_query_str, max_results=5 ) search_text = "\n".join([result.text for result in search_results]) else: search_text = "" return QueryEvent(relevant_text=relevant_text, search_text=search_text) @step async def query_result(self, ctx: Context, ev: QueryEvent) -> StopEvent: """Get result with relevant text.""" relevant_text = ev.relevant_text search_text = ev.search_text query_str = await ctx.store.get("query_str") documents = [Document(text=relevant_text + "\n" + search_text)] index = SummaryIndex.from_documents(documents) query_engine = index.as_query_engine() result = query_engine.query(query_str) return StopEvent(result=result)
## Running the workflow¶
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader

documents = SimpleDirectoryReader("./data").load_data()
workflow = CorrectiveRAGWorkflow()
index = await workflow.run(documents=documents)

```

from llama_index.core import SimpleDirectoryReader documents = SimpleDirectoryReader("./data").load_data() workflow = CorrectiveRAGWorkflow() index = await workflow.run(documents=documents)
In [ ]:
Copied!
```
from IPython.display import Markdown, display

response = await workflow.run(
    query_str="How was Llama2 pretrained?",
    index=index,
    tavily_ai_apikey=tavily_ai_api_key,
)
display(Markdown(str(response)))

```

from IPython.display import Markdown, display response = await workflow.run( query_str="How was Llama2 pretrained?", index=index, tavily_ai_apikey=tavily_ai_api_key, ) display(Markdown(str(response)))
Llama 2 was pretrained using an optimized auto-regressive transformer with several modifications to enhance performance. These modifications included more robust data cleaning, updated data mixes, training on 40% more total tokens, doubling the context length, and using grouped-query attention (GQA) to improve inference scalability for larger models.
In [ ]:
Copied!
```
response = await workflow.run(
    query_str="What is the functionality of latest ChatGPT memory."
)
display(Markdown(str(response)))

```

response = await workflow.run( query_str="What is the functionality of latest ChatGPT memory." ) display(Markdown(str(response)))
The functionality of the latest ChatGPT memory is to autonomously remember information it deems relevant from conversations. This feature aims to save users from having to repeat information and make future conversations more helpful. Users have control over the chatbot's memory, being able to access and manage these memories as needed.
