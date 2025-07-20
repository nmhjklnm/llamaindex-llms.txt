# Query Pipeline Chat Engine¶
By combining a query pipeline with a memory buffer, we can design our own custom chat engine loop.
In [ ]:
Copied!
```
%pip install llama-index-core
%pip install llama-index-llms-openai
%pip install llama-index-embeddings-openai
%pip install llama-index-postprocessor-colbert-rerank
%pip install llama-index-readers-web

```

%pip install llama-index-core %pip install llama-index-llms-openai %pip install llama-index-embeddings-openai %pip install llama-index-postprocessor-colbert-rerank %pip install llama-index-readers-web
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
## Index Construction¶
As a test, we will index Anthropic's latest documentation about tool/function calling.
In [ ]:
Copied!
```
from llama_index.readers.web import BeautifulSoupWebReader

reader = BeautifulSoupWebReader()

documents = reader.load_data(
    ["https://docs.anthropic.com/claude/docs/tool-use"]
)

```

from llama_index.readers.web import BeautifulSoupWebReader reader = BeautifulSoupWebReader() documents = reader.load_data( ["https://docs.anthropic.com/claude/docs/tool-use"] )
If you inspected the document text, you'd notice that there are way too many blank lines, lets clean that up a bit.
In [ ]:
Copied!
```
lines = documents[0].text.split("\n")

# remove sections with more than two empty lines in a row
fixed_lines = [lines[0]]
for idx in range(1, len(lines)):
    if lines[idx].strip() == "" and lines[idx - 1].strip() == "":
        continue
    fixed_lines.append(lines[idx])

documents[0].text = "\n".join(fixed_lines)

```

lines = documents[0].text.split("\n") # remove sections with more than two empty lines in a row fixed_lines = [lines[0]] for idx in range(1, len(lines)): if lines[idx].strip() == "" and lines[idx - 1].strip() == "": continue fixed_lines.append(lines[idx]) documents[0].text = "\n".join(fixed_lines)
Now, we can create our index using OpenAI embeddings.
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding

index = VectorStoreIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(
        model="text-embedding-3-large", embed_batch_size=256
    ),
)

```

from llama_index.core import VectorStoreIndex from llama_index.embeddings.openai import OpenAIEmbedding index = VectorStoreIndex.from_documents( documents, embed_model=OpenAIEmbedding( model="text-embedding-3-large", embed_batch_size=256 ), )
## Query Pipeline Contruction¶
As a demonstration, lets make a robust query pipeline with HyDE for retrieval and Colbert for reranking.
In [ ]:
Copied!
```
from llama_index.core.query_pipeline import (
    QueryPipeline,
    InputComponent,
    ArgPackComponent,
)
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.openai import OpenAI
from llama_index.postprocessor.colbert_rerank import ColbertRerank

# First, we create an input component to capture the user query
input_component = InputComponent()

# Next, we use the LLM to rewrite a user query
rewrite = (
    "Please write a query to a semantic search engine using the current conversation.\n"
    "\n"
    "\n"
    "{chat_history_str}"
    "\n"
    "\n"
    "Latest message: {query_str}\n"
    'Query:"""\n'
)
rewrite_template = PromptTemplate(rewrite)
llm = OpenAI(
    model="gpt-4-turbo-preview",
    temperature=0.2,
)

# we will retrieve two times, so we need to pack the retrieved nodes into a single list
argpack_component = ArgPackComponent()

# using that, we will retrieve...
retriever = index.as_retriever(similarity_top_k=6)

# then postprocess/rerank with Colbert
reranker = ColbertRerank(top_n=3)

```

from llama_index.core.query_pipeline import ( QueryPipeline, InputComponent, ArgPackComponent, ) from llama_index.core.prompts import PromptTemplate from llama_index.llms.openai import OpenAI from llama_index.postprocessor.colbert_rerank import ColbertRerank # First, we create an input component to capture the user query input_component = InputComponent() # Next, we use the LLM to rewrite a user query rewrite = ( "Please write a query to a semantic search engine using the current conversation.\n" "\n" "\n" "{chat_history_str}" "\n" "\n" "Latest message: {query_str}\n" 'Query:"""\n' ) rewrite_template = PromptTemplate(rewrite) llm = OpenAI( model="gpt-4-turbo-preview", temperature=0.2, ) # we will retrieve two times, so we need to pack the retrieved nodes into a single list argpack_component = ArgPackComponent() # using that, we will retrieve... retriever = index.as_retriever(similarity_top_k=6) # then postprocess/rerank with Colbert reranker = ColbertRerank(top_n=3)
For generating a response using chat history + retrieved nodes, lets create a custom component.
In [ ]:
Copied!
```
# then lastly, we need to create a response using the nodes AND chat history
from typing import Any, Dict, List, Optional
from llama_index.core.bridge.pydantic import Field
from llama_index.core.llms import ChatMessage
from llama_index.core.query_pipeline import CustomQueryComponent
from llama_index.core.schema import NodeWithScore

DEFAULT_CONTEXT_PROMPT = (
    "Here is some context that may be relevant:\n"
    "-----\n"
    "{node_context}\n"
    "-----\n"
    "Please write a response to the following question, using the above context:\n"
    "{query_str}\n"
)


class ResponseWithChatHistory(CustomQueryComponent):
    llm: OpenAI = Field(..., description="OpenAI LLM")
    system_prompt: Optional[str] = Field(
        default=None, description="System prompt to use for the LLM"
    )
    context_prompt: str = Field(
        default=DEFAULT_CONTEXT_PROMPT,
        description="Context prompt to use for the LLM",
    )

    def _validate_component_inputs(
        self, input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        # NOTE: this is OPTIONAL but we show you where to do validation as an example
        return input

    @property
    def _input_keys(self) -> set:
        """Input keys dict."""
        # NOTE: These are required inputs. If you have optional inputs please override
        # `optional_input_keys_dict`
        return {"chat_history", "nodes", "query_str"}

    @property
    def _output_keys(self) -> set:
        return {"response"}

    def _prepare_context(
        self,
        chat_history: List[ChatMessage],
        nodes: List[NodeWithScore],
        query_str: str,
    ) -> List[ChatMessage]:
        node_context = ""
        for idx, node in enumerate(nodes):
            node_text = node.get_content(metadata_mode="llm")
            node_context += f"Context Chunk {idx}:\n{node_text}\n\n"

        formatted_context = self.context_prompt.format(
            node_context=node_context, query_str=query_str
        )
        user_message = ChatMessage(role="user", content=formatted_context)

        chat_history.append(user_message)

        if self.system_prompt is not None:
            chat_history = [
                ChatMessage(role="system", content=self.system_prompt)
            ] + chat_history

        return chat_history

    def _run_component(self, **kwargs) -> Dict[str, Any]:
        """Run the component."""
        chat_history = kwargs["chat_history"]
        nodes = kwargs["nodes"]
        query_str = kwargs["query_str"]

        prepared_context = self._prepare_context(
            chat_history, nodes, query_str
        )

        response = llm.chat(prepared_context)

        return {"response": response}

    async def _arun_component(self, **kwargs: Any) -> Dict[str, Any]:
        """Run the component asynchronously."""
        # NOTE: Optional, but async LLM calls are easy to implement
        chat_history = kwargs["chat_history"]
        nodes = kwargs["nodes"]
        query_str = kwargs["query_str"]

        prepared_context = self._prepare_context(
            chat_history, nodes, query_str
        )

        response = await llm.achat(prepared_context)

        return {"response": response}


response_component = ResponseWithChatHistory(
    llm=llm,
    system_prompt=(
        "You are a Q&A system. You will be provided with the previous chat history, "
        "as well as possibly relevant context, to assist in answering a user message."
    ),
)

```

# then lastly, we need to create a response using the nodes AND chat history from typing import Any, Dict, List, Optional from llama_index.core.bridge.pydantic import Field from llama_index.core.llms import ChatMessage from llama_index.core.query_pipeline import CustomQueryComponent from llama_index.core.schema import NodeWithScore DEFAULT_CONTEXT_PROMPT = ( "Here is some context that may be relevant:\n" "-----\n" "{node_context}\n" "-----\n" "Please write a response to the following question, using the above context:\n" "{query_str}\n" ) class ResponseWithChatHistory(CustomQueryComponent): llm: OpenAI = Field(..., description="OpenAI LLM") system_prompt: Optional[str] = Field( default=None, description="System prompt to use for the LLM" ) context_prompt: str = Field( default=DEFAULT_CONTEXT_PROMPT, description="Context prompt to use for the LLM", ) def _validate_component_inputs( self, input: Dict[str, Any] ) -> Dict[str, Any]: """Validate component inputs during run_component.""" # NOTE: this is OPTIONAL but we show you where to do validation as an example return input @property def _input_keys(self) -> set: """Input keys dict.""" # NOTE: These are required inputs. If you have optional inputs please override # `optional_input_keys_dict` return {"chat_history", "nodes", "query_str"} @property def _output_keys(self) -> set: return {"response"} def _prepare_context( self, chat_history: List[ChatMessage], nodes: List[NodeWithScore], query_str: str, ) -> List[ChatMessage]: node_context = "" for idx, node in enumerate(nodes): node_text = node.get_content(metadata_mode="llm") node_context += f"Context Chunk {idx}:\n{node_text}\n\n" formatted_context = self.context_prompt.format( node_context=node_context, query_str=query_str ) user_message = ChatMessage(role="user", content=formatted_context) chat_history.append(user_message) if self.system_prompt is not None: chat_history = [ ChatMessage(role="system", content=self.system_prompt) ] + chat_history return chat_history def _run_component(self, **kwargs) -> Dict[str, Any]: """Run the component.""" chat_history = kwargs["chat_history"] nodes = kwargs["nodes"] query_str = kwargs["query_str"] prepared_context = self._prepare_context( chat_history, nodes, query_str ) response = llm.chat(prepared_context) return {"response": response} async def _arun_component(self, **kwargs: Any) -> Dict[str, Any]: """Run the component asynchronously.""" # NOTE: Optional, but async LLM calls are easy to implement chat_history = kwargs["chat_history"] nodes = kwargs["nodes"] query_str = kwargs["query_str"] prepared_context = self._prepare_context( chat_history, nodes, query_str ) response = await llm.achat(prepared_context) return {"response": response} response_component = ResponseWithChatHistory( llm=llm, system_prompt=( "You are a Q&A system. You will be provided with the previous chat history, " "as well as possibly relevant context, to assist in answering a user message." ), )
With our modules created, we can link them together in a query pipeline.
In [ ]:
Copied!
```
pipeline = QueryPipeline(
    modules={
        "input": input_component,
        "rewrite_template": rewrite_template,
        "llm": llm,
        "rewrite_retriever": retriever,
        "query_retriever": retriever,
        "join": argpack_component,
        "reranker": reranker,
        "response_component": response_component,
    },
    verbose=False,
)

# run both retrievers -- once with the hallucinated query, once with the real query
pipeline.add_link(
    "input", "rewrite_template", src_key="query_str", dest_key="query_str"
)
pipeline.add_link(
    "input",
    "rewrite_template",
    src_key="chat_history_str",
    dest_key="chat_history_str",
)
pipeline.add_link("rewrite_template", "llm")
pipeline.add_link("llm", "rewrite_retriever")
pipeline.add_link("input", "query_retriever", src_key="query_str")

# each input to the argpack component needs a dest key -- it can be anything
# then, the argpack component will pack all the inputs into a single list
pipeline.add_link("rewrite_retriever", "join", dest_key="rewrite_nodes")
pipeline.add_link("query_retriever", "join", dest_key="query_nodes")

# reranker needs the packed nodes and the query string
pipeline.add_link("join", "reranker", dest_key="nodes")
pipeline.add_link(
    "input", "reranker", src_key="query_str", dest_key="query_str"
)

# synthesizer needs the reranked nodes and query str
pipeline.add_link("reranker", "response_component", dest_key="nodes")
pipeline.add_link(
    "input", "response_component", src_key="query_str", dest_key="query_str"
)
pipeline.add_link(
    "input",
    "response_component",
    src_key="chat_history",
    dest_key="chat_history",
)

```

pipeline = QueryPipeline( modules={ "input": input_component, "rewrite_template": rewrite_template, "llm": llm, "rewrite_retriever": retriever, "query_retriever": retriever, "join": argpack_component, "reranker": reranker, "response_component": response_component, }, verbose=False, ) # run both retrievers -- once with the hallucinated query, once with the real query pipeline.add_link( "input", "rewrite_template", src_key="query_str", dest_key="query_str" ) pipeline.add_link( "input", "rewrite_template", src_key="chat_history_str", dest_key="chat_history_str", ) pipeline.add_link("rewrite_template", "llm") pipeline.add_link("llm", "rewrite_retriever") pipeline.add_link("input", "query_retriever", src_key="query_str") # each input to the argpack component needs a dest key -- it can be anything # then, the argpack component will pack all the inputs into a single list pipeline.add_link("rewrite_retriever", "join", dest_key="rewrite_nodes") pipeline.add_link("query_retriever", "join", dest_key="query_nodes") # reranker needs the packed nodes and the query string pipeline.add_link("join", "reranker", dest_key="nodes") pipeline.add_link( "input", "reranker", src_key="query_str", dest_key="query_str" ) # synthesizer needs the reranked nodes and query str pipeline.add_link("reranker", "response_component", dest_key="nodes") pipeline.add_link( "input", "response_component", src_key="query_str", dest_key="query_str" ) pipeline.add_link( "input", "response_component", src_key="chat_history", dest_key="chat_history", )
Lets test the pipeline to confirm it works!
## Running the Pipeline with Memory¶
The above pipeline uses two inputs -- a query string and a chat_history list.
The query string is simply the string input/query.
The chat history list is a list of ChatMessage objects. We can use a memory module from llama-index to directly manage and create the memory!
In [ ]:
Copied!
```
from llama_index.core.memory import ChatMemoryBuffer

pipeline_memory = ChatMemoryBuffer.from_defaults(token_limit=8000)

```

from llama_index.core.memory import ChatMemoryBuffer pipeline_memory = ChatMemoryBuffer.from_defaults(token_limit=8000)
Lets pre-create a "chat session" and watch it play out.
In [ ]:
Copied!
```
user_inputs = [
    "Hello!",
    "How does tool-use work with Claude-3 work?",
    "What models support it?",
    "Thanks, that what I needed to know!",
]

for msg in user_inputs:
    # get memory
    chat_history = pipeline_memory.get()

    # prepare inputs
    chat_history_str = "\n".join([str(x) for x in chat_history])

    # run pipeline
    response = pipeline.run(
        query_str=msg,
        chat_history=chat_history,
        chat_history_str=chat_history_str,
    )

    # update memory
    user_msg = ChatMessage(role="user", content=msg)
    pipeline_memory.put(user_msg)
    print(str(user_msg))

    pipeline_memory.put(response.message)
    print(str(response.message))
    print()

```

user_inputs = [ "Hello!", "How does tool-use work with Claude-3 work?", "What models support it?", "Thanks, that what I needed to know!", ] for msg in user_inputs: # get memory chat_history = pipeline_memory.get() # prepare inputs chat_history_str = "\n".join([str(x) for x in chat_history]) # run pipeline response = pipeline.run( query_str=msg, chat_history=chat_history, chat_history_str=chat_history_str, ) # update memory user_msg = ChatMessage(role="user", content=msg) pipeline_memory.put(user_msg) print(str(user_msg)) pipeline_memory.put(response.message) print(str(response.message)) print()
```
user: Hello!
assistant: Hello! How can I assist you today?

user: How does tool-use work with Claude-3 work?
assistant: Tool use with Claude-3 operates under a framework designed to extend the model's capabilities by integrating it with external data sources and functionalities through user-provided tools. This process involves several key steps and considerations to ensure effective tool integration and utilization. Here's a breakdown of how tool use works with Claude-3:

1. **Tool Specification**: Users define tools in the API request, specifying the tool's name, a detailed description of its purpose and behavior, and an input schema that outlines the expected parameters. This schema is crucial for Claude to understand when and how to use the tool correctly.

2. **Decision to Use a Tool**: When Claude-3 receives a user prompt that may benefit from tool use, it assesses whether any available tools can assist with the query or task. This decision is based on the context provided by the user and the detailed descriptions of the tools.

3. **Tool Use Request Formation**: If Claude decides to use a tool, it constructs a properly formatted tool use request. This includes selecting the appropriate tool(s) and determining the necessary inputs based on the user's prompt and the tool's input schema.

4. **Execution of Tool Code**: The actual execution of the tool code occurs on the client side. The system extracts the tool name and input from Claude's tool use request, runs the tool code, and then returns the results to Claude.

5. **Formulating a Response**: After receiving the tool results, Claude uses this information to formulate its final response to the user's original prompt. This step may involve interpreting the tool's output and integrating it into a coherent and informative answer.

6. **Sequential Tool Use**: Claude generally prefers using one tool at a time, using the output of one tool to inform its next action. This sequential approach helps manage dependencies between tools and simplifies the tool use process.

7. **Error Handling and Retries**: If a tool use request is invalid or missing required parameters, Claude can retry the request with the missing information filled in, based on error responses from the client side. However, after a few failed attempts, Claude may stop trying and apologize to the user.

8. **Debugging and Improvement**: Developers are encouraged to debug unexpected tool use behavior by examining Claude's chain of thought output and refining tool descriptions and schemas for clarity and comprehensiveness.

By adhering to these steps and best practices, developers can effectively integrate and utilize tools with Claude-3, significantly expanding its capabilities beyond its base knowledge. This framework allows for the creation of complex, agentic orchestrations where Claude can perform a wide variety of tasks, from simple data retrieval to more complex problem-solving scenarios.

user: What models support it?
assistant: The tool use feature, as described in the provided context, is supported by Claude-3 models, including specific versions like Claude-3 Opus and Haiku. These models are designed to interact with external client-side tools and functions, allowing for a wide variety of tasks to be performed by equipping Claude with custom tools. The context specifically mentions Claude-3 Opus as being capable of handling more complex tool use scenarios, including managing multiple tools simultaneously and better catching missing arguments. Haiku is mentioned for dealing with more straightforward tools, inferring missing parameters when they are not explicitly given.

user: Thanks, that what I needed to know!
assistant: You're welcome! If you have any more questions or need further assistance, feel free to ask. Happy to help!


```

