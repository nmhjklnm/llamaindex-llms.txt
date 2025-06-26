![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Build RAG with in-line citations¶
This notebook walks through implementation of RAG with in-line citations of source nodes, using Workflows.
Specifically we will implement CitationQueryEngine which gives in-line citations in the response generated based on the nodes.
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
## Download Data¶
In [ ]:
Copied!
```
!mkdir -p 'data/paul_graham/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/paul_graham/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
--2024-08-15 00:23:50--  https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt
Resolving raw.githubusercontent.com (raw.githubusercontent.com)... 2606:50c0:8000::154, 2606:50c0:8001::154, 2606:50c0:8002::154, ...
Connecting to raw.githubusercontent.com (raw.githubusercontent.com)|2606:50c0:8000::154|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 75042 (73K) [text/plain]
Saving to: ‘data/paul_graham/paul_graham_essay.txt’

data/paul_graham/pa 100%[===================>]  73.28K  --.-KB/s    in 0.01s   

2024-08-15 00:23:50 (5.27 MB/s) - ‘data/paul_graham/paul_graham_essay.txt’ saved [75042/75042]


```

Since workflows are async first, this all runs fine in a notebook. If you were running in your own code, you would want to use `asyncio.run()` to start an async event loop if one isn't already running.
```
async def main():
    <async code>

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

```

## Designing the Workflow¶
CitationQueryEngine consists of some clearly defined steps
  1. Indexing data, creating an index
  2. Using that index + a query to retrieve relevant nodes
  3. Add citations to the retrieved nodes.
  4. Synthesizing a final response


With this in mind, we can create events and workflow steps to follow this process!
### The Workflow Events¶
To handle these steps, we need to define a few events:
  1. An event to pass retrieved nodes to the create citations
  2. An event to pass citation nodes to the synthesizer


The other steps will use the built-in `StartEvent` and `StopEvent` events.
In [ ]:
Copied!
```
from llama_index.core.workflow import Event
from llama_index.core.schema import NodeWithScore


class RetrieverEvent(Event):
    """Result of running retrieval"""

    nodes: list[NodeWithScore]


class CreateCitationsEvent(Event):
    """Add citations to the nodes."""

    nodes: list[NodeWithScore]

```

from llama_index.core.workflow import Event from llama_index.core.schema import NodeWithScore class RetrieverEvent(Event): """Result of running retrieval""" nodes: list[NodeWithScore] class CreateCitationsEvent(Event): """Add citations to the nodes.""" nodes: list[NodeWithScore]
## Citation Prompt Templates¶
Here we define default `CITATION_QA_TEMPLATE`, `CITATION_REFINE_TEMPLATE`, `DEFAULT_CITATION_CHUNK_SIZE` and `DEFAULT_CITATION_CHUNK_OVERLAP`.
In [ ]:
Copied!
```
from llama_index.core.prompts import PromptTemplate

CITATION_QA_TEMPLATE = PromptTemplate(
    "Please provide an answer based solely on the provided sources. "
    "When referencing information from a source, "
    "cite the appropriate source(s) using their corresponding numbers. "
    "Every answer should include at least one source citation. "
    "Only cite a source when you are explicitly referencing it. "
    "If none of the sources are helpful, you should indicate that. "
    "For example:\n"
    "Source 1:\n"
    "The sky is red in the evening and blue in the morning.\n"
    "Source 2:\n"
    "Water is wet when the sky is red.\n"
    "Query: When is water wet?\n"
    "Answer: Water will be wet when the sky is red [2], "
    "which occurs in the evening [1].\n"
    "Now it's your turn. Below are several numbered sources of information:"
    "\n------\n"
    "{context_str}"
    "\n------\n"
    "Query: {query_str}\n"
    "Answer: "
)

CITATION_REFINE_TEMPLATE = PromptTemplate(
    "Please provide an answer based solely on the provided sources. "
    "When referencing information from a source, "
    "cite the appropriate source(s) using their corresponding numbers. "
    "Every answer should include at least one source citation. "
    "Only cite a source when you are explicitly referencing it. "
    "If none of the sources are helpful, you should indicate that. "
    "For example:\n"
    "Source 1:\n"
    "The sky is red in the evening and blue in the morning.\n"
    "Source 2:\n"
    "Water is wet when the sky is red.\n"
    "Query: When is water wet?\n"
    "Answer: Water will be wet when the sky is red [2], "
    "which occurs in the evening [1].\n"
    "Now it's your turn. "
    "We have provided an existing answer: {existing_answer}"
    "Below are several numbered sources of information. "
    "Use them to refine the existing answer. "
    "If the provided sources are not helpful, you will repeat the existing answer."
    "\nBegin refining!"
    "\n------\n"
    "{context_msg}"
    "\n------\n"
    "Query: {query_str}\n"
    "Answer: "
)

DEFAULT_CITATION_CHUNK_SIZE = 512
DEFAULT_CITATION_CHUNK_OVERLAP = 20

```

from llama_index.core.prompts import PromptTemplate CITATION_QA_TEMPLATE = PromptTemplate( "Please provide an answer based solely on the provided sources. " "When referencing information from a source, " "cite the appropriate source(s) using their corresponding numbers. " "Every answer should include at least one source citation. " "Only cite a source when you are explicitly referencing it. " "If none of the sources are helpful, you should indicate that. " "For example:\n" "Source 1:\n" "The sky is red in the evening and blue in the morning.\n" "Source 2:\n" "Water is wet when the sky is red.\n" "Query: When is water wet?\n" "Answer: Water will be wet when the sky is red [2], " "which occurs in the evening [1].\n" "Now it's your turn. Below are several numbered sources of information:" "\n------\n" "{context_str}" "\n------\n" "Query: {query_str}\n" "Answer: " ) CITATION_REFINE_TEMPLATE = PromptTemplate( "Please provide an answer based solely on the provided sources. " "When referencing information from a source, " "cite the appropriate source(s) using their corresponding numbers. " "Every answer should include at least one source citation. " "Only cite a source when you are explicitly referencing it. " "If none of the sources are helpful, you should indicate that. " "For example:\n" "Source 1:\n" "The sky is red in the evening and blue in the morning.\n" "Source 2:\n" "Water is wet when the sky is red.\n" "Query: When is water wet?\n" "Answer: Water will be wet when the sky is red [2], " "which occurs in the evening [1].\n" "Now it's your turn. " "We have provided an existing answer: {existing_answer}" "Below are several numbered sources of information. " "Use them to refine the existing answer. " "If the provided sources are not helpful, you will repeat the existing answer." "\nBegin refining!" "\n------\n" "{context_msg}" "\n------\n" "Query: {query_str}\n" "Answer: " ) DEFAULT_CITATION_CHUNK_SIZE = 512 DEFAULT_CITATION_CHUNK_OVERLAP = 20
### The Workflow Itself¶
With our events defined, we can construct our workflow and steps.
Note that the workflow automatically validates itself using type annotations, so the type annotations on our steps are very helpful!
In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.workflow import (
    Context,
    Workflow,
    StartEvent,
    StopEvent,
    step,
)

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

from llama_index.core.schema import (
    MetadataMode,
    NodeWithScore,
    TextNode,
)

from llama_index.core.response_synthesizers import (
    ResponseMode,
    get_response_synthesizer,
)

from typing import Union, List
from llama_index.core.node_parser import SentenceSplitter


class CitationQueryEngineWorkflow(Workflow):
    @step
    async def retrieve(
        self, ctx: Context, ev: StartEvent
    ) -> Union[RetrieverEvent, None]:
        "Entry point for RAG, triggered by a StartEvent with `query`."
        query = ev.get("query")
        if not query:
            return None

        print(f"Query the database with: {query}")

        # store the query in the global context
        await ctx.set("query", query)

        if ev.index is None:
            print("Index is empty, load some documents before querying!")
            return None

        retriever = ev.index.as_retriever(similarity_top_k=2)
        nodes = retriever.retrieve(query)
        print(f"Retrieved {len(nodes)} nodes.")
        return RetrieverEvent(nodes=nodes)

    @step
    async def create_citation_nodes(
        self, ev: RetrieverEvent
    ) -> CreateCitationsEvent:
        """
        Modify retrieved nodes to create granular sources for citations.

        Takes a list of NodeWithScore objects and splits their content
        into smaller chunks, creating new NodeWithScore objects for each chunk.
        Each new node is labeled as a numbered source, allowing for more precise
        citation in query results.

        Args:
            nodes (List[NodeWithScore]): A list of NodeWithScore objects to be processed.

        Returns:
            List[NodeWithScore]: A new list of NodeWithScore objects, where each object
            represents a smaller chunk of the original nodes, labeled as a source.
        """
        nodes = ev.nodes

        new_nodes: List[NodeWithScore] = []

        text_splitter = SentenceSplitter(
            chunk_size=DEFAULT_CITATION_CHUNK_SIZE,
            chunk_overlap=DEFAULT_CITATION_CHUNK_OVERLAP,
        )

        for node in nodes:
            text_chunks = text_splitter.split_text(
                node.node.get_content(metadata_mode=MetadataMode.NONE)
            )

            for text_chunk in text_chunks:
                text = f"Source {len(new_nodes)+1}:\n{text_chunk}\n"

                new_node = NodeWithScore(
                    node=TextNode.parse_obj(node.node), score=node.score
                )
                new_node.node.text = text
                new_nodes.append(new_node)
        return CreateCitationsEvent(nodes=new_nodes)

    @step
    async def synthesize(
        self, ctx: Context, ev: CreateCitationsEvent
    ) -> StopEvent:
        """Return a streaming response using the retrieved nodes."""
        llm = OpenAI(model="gpt-4o-mini")
        query = await ctx.get("query", default=None)

        synthesizer = get_response_synthesizer(
            llm=llm,
            text_qa_template=CITATION_QA_TEMPLATE,
            refine_template=CITATION_REFINE_TEMPLATE,
            response_mode=ResponseMode.COMPACT,
            use_async=True,
        )

        response = await synthesizer.asynthesize(query, nodes=ev.nodes)
        return StopEvent(result=response)

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex from llama_index.core.workflow import ( Context, Workflow, StartEvent, StopEvent, step, ) from llama_index.llms.openai import OpenAI from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.core.schema import ( MetadataMode, NodeWithScore, TextNode, ) from llama_index.core.response_synthesizers import ( ResponseMode, get_response_synthesizer, ) from typing import Union, List from llama_index.core.node_parser import SentenceSplitter class CitationQueryEngineWorkflow(Workflow): @step async def retrieve( self, ctx: Context, ev: StartEvent ) -> Union[RetrieverEvent, None]: "Entry point for RAG, triggered by a StartEvent with `query`." query = ev.get("query") if not query: return None print(f"Query the database with: {query}") # store the query in the global context await ctx.set("query", query) if ev.index is None: print("Index is empty, load some documents before querying!") return None retriever = ev.index.as_retriever(similarity_top_k=2) nodes = retriever.retrieve(query) print(f"Retrieved {len(nodes)} nodes.") return RetrieverEvent(nodes=nodes) @step async def create_citation_nodes( self, ev: RetrieverEvent ) -> CreateCitationsEvent: """ Modify retrieved nodes to create granular sources for citations. Takes a list of NodeWithScore objects and splits their content into smaller chunks, creating new NodeWithScore objects for each chunk. Each new node is labeled as a numbered source, allowing for more precise citation in query results. Args: nodes (List[NodeWithScore]): A list of NodeWithScore objects to be processed. Returns: List[NodeWithScore]: A new list of NodeWithScore objects, where each object represents a smaller chunk of the original nodes, labeled as a source. """ nodes = ev.nodes new_nodes: List[NodeWithScore] = [] text_splitter = SentenceSplitter( chunk_size=DEFAULT_CITATION_CHUNK_SIZE, chunk_overlap=DEFAULT_CITATION_CHUNK_OVERLAP, ) for node in nodes: text_chunks = text_splitter.split_text( node.node.get_content(metadata_mode=MetadataMode.NONE) ) for text_chunk in text_chunks: text = f"Source {len(new_nodes)+1}:\n{text_chunk}\n" new_node = NodeWithScore( node=TextNode.parse_obj(node.node), score=node.score ) new_node.node.text = text new_nodes.append(new_node) return CreateCitationsEvent(nodes=new_nodes) @step async def synthesize( self, ctx: Context, ev: CreateCitationsEvent ) -> StopEvent: """Return a streaming response using the retrieved nodes.""" llm = OpenAI(model="gpt-4o-mini") query = await ctx.get("query", default=None) synthesizer = get_response_synthesizer( llm=llm, text_qa_template=CITATION_QA_TEMPLATE, refine_template=CITATION_REFINE_TEMPLATE, response_mode=ResponseMode.COMPACT, use_async=True, ) response = await synthesizer.asynthesize(query, nodes=ev.nodes) return StopEvent(result=response)
And thats it! Let's explore the workflow we wrote a bit.
  * We have an entry point (the step that accept `StartEvent`)
  * The workflow context is used to store the user query
  * The nodes are retrieved, citations are created, and finally a response is returned


## Create Index¶
In [ ]:
Copied!
```
documents = SimpleDirectoryReader("data/paul_graham").load_data()
index = VectorStoreIndex.from_documents(
    documents=documents,
    embed_model=OpenAIEmbedding(model_name="text-embedding-3-small"),
)

```

documents = SimpleDirectoryReader("data/paul_graham").load_data() index = VectorStoreIndex.from_documents( documents=documents, embed_model=OpenAIEmbedding(model_name="text-embedding-3-small"), )
### Run the Workflow!¶
In [ ]:
Copied!
```
w = CitationQueryEngineWorkflow()

```

w = CitationQueryEngineWorkflow()
In [ ]:
Copied!
```
# Run a query
result = await w.run(query="What information do you have", index=index)

```

# Run a query result = await w.run(query="What information do you have", index=index)
```
Query the database with: What information do you have
Retrieved 2 nodes.

```

In [ ]:
Copied!
```
from IPython.display import Markdown, display

display(Markdown(f"{result}"))

```

from IPython.display import Markdown, display display(Markdown(f"{result}"))
The provided sources contain various insights into Paul Graham's experiences and thoughts on programming, writing, and his educational journey. For instance, he reflects on his early experiences with programming on the IBM 1401, where he struggled to create meaningful programs due to the limitations of the technology at the time [2]. He also describes his transition to using microcomputers, which allowed for more interactive programming experiences [3]. Additionally, Graham shares his initial interest in philosophy during college, which he later found less engaging compared to the fields of artificial intelligence and programming [3]. Overall, the sources highlight his evolution as a writer and programmer, as well as his changing academic interests.
## Check the citations.¶
In [ ]:
Copied!
```
print(result.source_nodes[0].node.get_text())

```

print(result.source_nodes[0].node.get_text())
```
Source 1:
But after Heroku got bought we had enough money to go back to being self-funded.

[15] I've never liked the term "deal flow," because it implies that the number of new startups at any given time is fixed. This is not only false, but it's the purpose of YC to falsify it, by causing startups to be founded that would not otherwise have existed.

[16] She reports that they were all different shapes and sizes, because there was a run on air conditioners and she had to get whatever she could, but that they were all heavier than she could carry now.

[17] Another problem with HN was a bizarre edge case that occurs when you both write essays and run a forum. When you run a forum, you're assumed to see if not every conversation, at least every conversation involving you. And when you write essays, people post highly imaginative misinterpretations of them on forums. Individually these two phenomena are tedious but bearable, but the combination is disastrous. You actually have to respond to the misinterpretations, because the assumption that you're present in the conversation means that not responding to any sufficiently upvoted misinterpretation reads as a tacit admission that it's correct. But that in turn encourages more; anyone who wants to pick a fight with you senses that now is their chance.

[18] The worst thing about leaving YC was not working with Jessica anymore. We'd been working on YC almost the whole time we'd known each other, and we'd neither tried nor wanted to separate it from our personal lives, so leaving was like pulling up a deeply rooted tree.

[19] One way to get more precise about the concept of invented vs discovered is to talk about space aliens. Any sufficiently advanced alien civilization would certainly know about the Pythagorean theorem, for example. I believe, though with less certainty, that they would also know about the Lisp in McCarthy's 1960 paper.

But if so there's no reason to suppose that this is the limit of the language that might be known to them. Presumably aliens need numbers and errors and I/O too. So it seems likely there exists at least one path out of McCarthy's Lisp along which discoveredness is preserved.



Thanks to Trevor Blackwell, John Collison, Patrick Collison, Daniel Gackle, Ralph Hazell, Jessica Livingston, Robert Morris, and Harj Taggar for reading drafts of this.


```

In [ ]:
Copied!
```
print(result.source_nodes[1].node.get_text())

```

print(result.source_nodes[1].node.get_text())
```
Source 2:
What I Worked On

February 2021

Before college the two main things I worked on, outside of school, were writing and programming. I didn't write essays. I wrote what beginning writers were supposed to write then, and probably still are: short stories. My stories were awful. They had hardly any plot, just characters with strong feelings, which I imagined made them deep.

The first programs I tried writing were on the IBM 1401 that our school district used for what was then called "data processing." This was in 9th grade, so I was 13 or 14. The school district's 1401 happened to be in the basement of our junior high school, and my friend Rich Draves and I got permission to use it. It was like a mini Bond villain's lair down there, with all these alien-looking machines — CPU, disk drives, printer, card reader — sitting up on a raised floor under bright fluorescent lights.

The language we used was an early version of Fortran. You had to type programs on punch cards, then stack them in the card reader and press a button to load the program into memory and run it. The result would ordinarily be to print something on the spectacularly loud printer.

I was puzzled by the 1401. I couldn't figure out what to do with it. And in retrospect there's not much I could have done with it. The only form of input to programs was data stored on punched cards, and I didn't have any data stored on punched cards. The only other option was to do things that didn't rely on any input, like calculate approximations of pi, but I didn't know enough math to do anything interesting of that type. So I'm not surprised I can't remember any programs I wrote, because they can't have done much. My clearest memory is of the moment I learned it was possible for programs not to terminate, when one of mine didn't. On a machine without time-sharing, this was a social as well as a technical error, as the data center manager's expression made clear.

With microcomputers, everything changed. Now you could have a computer sitting right in front of you, on a desk, that could respond to your keystrokes as it was running instead of just churning through a stack of punch cards and then stopping.


```

