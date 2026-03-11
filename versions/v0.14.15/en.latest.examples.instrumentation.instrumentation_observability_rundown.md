# Built-In Observability Instrumentation¶
Within LlamaIndex, many events and spans are created and logged through our instrumentation system.
This notebook walks through how you would hook into these events and spans to create your own observability tooling.
In [ ]:
Copied!
```
%pip install llama-index treelib

```

%pip install llama-index treelib
## Events¶
LlamaIndex logs several types of events. Events are singular data points that occur during runtime, and usually belong to some parent span.
Below is a thorough list of what is logged, and how to create an event handler to read these events.
In [ ]:
Copied!
```
from typing import Dict, List
from treelib import Tree

from llama_index.core.instrumentation.events import BaseEvent
from llama_index.core.instrumentation.event_handlers import BaseEventHandler

from llama_index.core.instrumentation.events.agent import (
    AgentChatWithStepStartEvent,
    AgentChatWithStepEndEvent,
    AgentRunStepStartEvent,
    AgentRunStepEndEvent,
    AgentToolCallEvent,
)
from llama_index.core.instrumentation.events.chat_engine import (
    StreamChatErrorEvent,
    StreamChatDeltaReceivedEvent,
)
from llama_index.core.instrumentation.events.embedding import (
    EmbeddingStartEvent,
    EmbeddingEndEvent,
)
from llama_index.core.instrumentation.events.llm import (
    LLMPredictEndEvent,
    LLMPredictStartEvent,
    LLMStructuredPredictEndEvent,
    LLMStructuredPredictStartEvent,
    LLMCompletionEndEvent,
    LLMCompletionStartEvent,
    LLMChatEndEvent,
    LLMChatStartEvent,
    LLMChatInProgressEvent,
)
from llama_index.core.instrumentation.events.query import (
    QueryStartEvent,
    QueryEndEvent,
)
from llama_index.core.instrumentation.events.rerank import (
    ReRankStartEvent,
    ReRankEndEvent,
)
from llama_index.core.instrumentation.events.retrieval import (
    RetrievalStartEvent,
    RetrievalEndEvent,
)
from llama_index.core.instrumentation.events.span import (
    SpanDropEvent,
)
from llama_index.core.instrumentation.events.synthesis import (
    SynthesizeStartEvent,
    SynthesizeEndEvent,
    GetResponseEndEvent,
    GetResponseStartEvent,
)


class ExampleEventHandler(BaseEventHandler):
    """Example event handler.

    This event handler is an example of how to create a custom event handler.

    In general, logged events are treated as single events in a point in time,
    that link to a span. The span is a collection of events that are related to
    a single task. The span is identified by a unique span_id.

    While events are independent, there is some hierarchy.
    For example, in query_engine.query() call with a reranker attached:
    - QueryStartEvent
    - RetrievalStartEvent
    - EmbeddingStartEvent
    - EmbeddingEndEvent
    - RetrievalEndEvent
    - RerankStartEvent
    - RerankEndEvent
    - SynthesizeStartEvent
    - GetResponseStartEvent
    - LLMPredictStartEvent
    - LLMChatStartEvent
    - LLMChatEndEvent
    - LLMPredictEndEvent
    - GetResponseEndEvent
    - SynthesizeEndEvent
    - QueryEndEvent
    """

    events: List[BaseEvent] = []

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "ExampleEventHandler"

    def handle(self, event: BaseEvent) -> None:
        """Logic for handling event."""
        print("-----------------------")
        # all events have these attributes
        print(event.id_)
        print(event.timestamp)
        print(event.span_id)

        # event specific attributes
        print(f"Event type: {event.class_name()}")
        if isinstance(event, AgentRunStepStartEvent):
            print(event.task_id)
            print(event.step)
            print(event.input)
        if isinstance(event, AgentRunStepEndEvent):
            print(event.step_output)
        if isinstance(event, AgentChatWithStepStartEvent):
            print(event.user_msg)
        if isinstance(event, AgentChatWithStepEndEvent):
            print(event.response)
        if isinstance(event, AgentToolCallEvent):
            print(event.arguments)
            print(event.tool.name)
            print(event.tool.description)
            print(event.tool.to_openai_tool())
        if isinstance(event, StreamChatDeltaReceivedEvent):
            print(event.delta)
        if isinstance(event, StreamChatErrorEvent):
            print(event.exception)
        if isinstance(event, EmbeddingStartEvent):
            print(event.model_dict)
        if isinstance(event, EmbeddingEndEvent):
            print(event.chunks)
            print(event.embeddings[0][:5])  # avoid printing all embeddings
        if isinstance(event, LLMPredictStartEvent):
            print(event.template)
            print(event.template_args)
        if isinstance(event, LLMPredictEndEvent):
            print(event.output)
        if isinstance(event, LLMStructuredPredictStartEvent):
            print(event.template)
            print(event.template_args)
            print(event.output_cls)
        if isinstance(event, LLMStructuredPredictEndEvent):
            print(event.output)
        if isinstance(event, LLMCompletionStartEvent):
            print(event.model_dict)
            print(event.prompt)
            print(event.additional_kwargs)
        if isinstance(event, LLMCompletionEndEvent):
            print(event.response)
            print(event.prompt)
        if isinstance(event, LLMChatInProgressEvent):
            print(event.messages)
            print(event.response)
        if isinstance(event, LLMChatStartEvent):
            print(event.messages)
            print(event.additional_kwargs)
            print(event.model_dict)
        if isinstance(event, LLMChatEndEvent):
            print(event.messages)
            print(event.response)
        if isinstance(event, RetrievalStartEvent):
            print(event.str_or_query_bundle)
        if isinstance(event, RetrievalEndEvent):
            print(event.str_or_query_bundle)
            print(event.nodes)
        if isinstance(event, ReRankStartEvent):
            print(event.query)
            print(event.nodes)
            print(event.top_n)
            print(event.model_name)
        if isinstance(event, ReRankEndEvent):
            print(event.nodes)
        if isinstance(event, QueryStartEvent):
            print(event.query)
        if isinstance(event, QueryEndEvent):
            print(event.response)
            print(event.query)
        if isinstance(event, SpanDropEvent):
            print(event.err_str)
        if isinstance(event, SynthesizeStartEvent):
            print(event.query)
        if isinstance(event, SynthesizeEndEvent):
            print(event.response)
            print(event.query)
        if isinstance(event, GetResponseStartEvent):
            print(event.query_str)

        self.events.append(event)
        print("-----------------------")

    def _get_events_by_span(self) -> Dict[str, List[BaseEvent]]:
        events_by_span: Dict[str, List[BaseEvent]] = {}
        for event in self.events:
            if event.span_id in events_by_span:
                events_by_span[event.span_id].append(event)
            else:
                events_by_span[event.span_id] = [event]
        return events_by_span

    def _get_event_span_trees(self) -> List[Tree]:
        events_by_span = self._get_events_by_span()

        trees = []
        tree = Tree()

        for span, sorted_events in events_by_span.items():
            # create root node i.e. span node
            tree.create_node(
                tag=f"{span} (SPAN)",
                identifier=span,
                parent=None,
                data=sorted_events[0].timestamp,
            )

            for event in sorted_events:
                tree.create_node(
                    tag=f"{event.class_name()}: {event.id_}",
                    identifier=event.id_,
                    parent=event.span_id,
                    data=event.timestamp,
                )

            trees.append(tree)
            tree = Tree()
        return trees

    def print_event_span_trees(self) -> None:
        """Method for viewing trace trees."""
        trees = self._get_event_span_trees()
        for tree in trees:
            print(
                tree.show(
                    stdout=False, sorting=True, key=lambda node: node.data
                )
            )
            print("")

```

from typing import Dict, List from treelib import Tree from llama_index.core.instrumentation.events import BaseEvent from llama_index.core.instrumentation.event_handlers import BaseEventHandler from llama_index.core.instrumentation.events.agent import ( AgentChatWithStepStartEvent, AgentChatWithStepEndEvent, AgentRunStepStartEvent, AgentRunStepEndEvent, AgentToolCallEvent, ) from llama_index.core.instrumentation.events.chat_engine import ( StreamChatErrorEvent, StreamChatDeltaReceivedEvent, ) from llama_index.core.instrumentation.events.embedding import ( EmbeddingStartEvent, EmbeddingEndEvent, ) from llama_index.core.instrumentation.events.llm import ( LLMPredictEndEvent, LLMPredictStartEvent, LLMStructuredPredictEndEvent, LLMStructuredPredictStartEvent, LLMCompletionEndEvent, LLMCompletionStartEvent, LLMChatEndEvent, LLMChatStartEvent, LLMChatInProgressEvent, ) from llama_index.core.instrumentation.events.query import ( QueryStartEvent, QueryEndEvent, ) from llama_index.core.instrumentation.events.rerank import ( ReRankStartEvent, ReRankEndEvent, ) from llama_index.core.instrumentation.events.retrieval import ( RetrievalStartEvent, RetrievalEndEvent, ) from llama_index.core.instrumentation.events.span import ( SpanDropEvent, ) from llama_index.core.instrumentation.events.synthesis import ( SynthesizeStartEvent, SynthesizeEndEvent, GetResponseEndEvent, GetResponseStartEvent, ) class ExampleEventHandler(BaseEventHandler): """Example event handler. This event handler is an example of how to create a custom event handler. In general, logged events are treated as single events in a point in time, that link to a span. The span is a collection of events that are related to a single task. The span is identified by a unique span_id. While events are independent, there is some hierarchy. For example, in query_engine.query() call with a reranker attached: - QueryStartEvent - RetrievalStartEvent - EmbeddingStartEvent - EmbeddingEndEvent - RetrievalEndEvent - RerankStartEvent - RerankEndEvent - SynthesizeStartEvent - GetResponseStartEvent - LLMPredictStartEvent - LLMChatStartEvent - LLMChatEndEvent - LLMPredictEndEvent - GetResponseEndEvent - SynthesizeEndEvent - QueryEndEvent """ events: List[BaseEvent] = [] @classmethod def class_name(cls) -> str: """Class name.""" return "ExampleEventHandler" def handle(self, event: BaseEvent) -> None: """Logic for handling event.""" print("-----------------------") # all events have these attributes print(event.id_) print(event.timestamp) print(event.span_id) # event specific attributes print(f"Event type: {event.class_name()}") if isinstance(event, AgentRunStepStartEvent): print(event.task_id) print(event.step) print(event.input) if isinstance(event, AgentRunStepEndEvent): print(event.step_output) if isinstance(event, AgentChatWithStepStartEvent): print(event.user_msg) if isinstance(event, AgentChatWithStepEndEvent): print(event.response) if isinstance(event, AgentToolCallEvent): print(event.arguments) print(event.tool.name) print(event.tool.description) print(event.tool.to_openai_tool()) if isinstance(event, StreamChatDeltaReceivedEvent): print(event.delta) if isinstance(event, StreamChatErrorEvent): print(event.exception) if isinstance(event, EmbeddingStartEvent): print(event.model_dict) if isinstance(event, EmbeddingEndEvent): print(event.chunks) print(event.embeddings[0][:5]) # avoid printing all embeddings if isinstance(event, LLMPredictStartEvent): print(event.template) print(event.template_args) if isinstance(event, LLMPredictEndEvent): print(event.output) if isinstance(event, LLMStructuredPredictStartEvent): print(event.template) print(event.template_args) print(event.output_cls) if isinstance(event, LLMStructuredPredictEndEvent): print(event.output) if isinstance(event, LLMCompletionStartEvent): print(event.model_dict) print(event.prompt) print(event.additional_kwargs) if isinstance(event, LLMCompletionEndEvent): print(event.response) print(event.prompt) if isinstance(event, LLMChatInProgressEvent): print(event.messages) print(event.response) if isinstance(event, LLMChatStartEvent): print(event.messages) print(event.additional_kwargs) print(event.model_dict) if isinstance(event, LLMChatEndEvent): print(event.messages) print(event.response) if isinstance(event, RetrievalStartEvent): print(event.str_or_query_bundle) if isinstance(event, RetrievalEndEvent): print(event.str_or_query_bundle) print(event.nodes) if isinstance(event, ReRankStartEvent): print(event.query) print(event.nodes) print(event.top_n) print(event.model_name) if isinstance(event, ReRankEndEvent): print(event.nodes) if isinstance(event, QueryStartEvent): print(event.query) if isinstance(event, QueryEndEvent): print(event.response) print(event.query) if isinstance(event, SpanDropEvent): print(event.err_str) if isinstance(event, SynthesizeStartEvent): print(event.query) if isinstance(event, SynthesizeEndEvent): print(event.response) print(event.query) if isinstance(event, GetResponseStartEvent): print(event.query_str) self.events.append(event) print("-----------------------") def _get_events_by_span(self) -> Dict[str, List[BaseEvent]]: events_by_span: Dict[str, List[BaseEvent]] = {} for event in self.events: if event.span_id in events_by_span: events_by_span[event.span_id].append(event) else: events_by_span[event.span_id] = [event] return events_by_span def _get_event_span_trees(self) -> List[Tree]: events_by_span = self._get_events_by_span() trees = [] tree = Tree() for span, sorted_events in events_by_span.items(): # create root node i.e. span node tree.create_node( tag=f"{span} (SPAN)", identifier=span, parent=None, data=sorted_events[0].timestamp, ) for event in sorted_events: tree.create_node( tag=f"{event.class_name()}: {event.id_}", identifier=event.id_, parent=event.span_id, data=event.timestamp, ) trees.append(tree) tree = Tree() return trees def print_event_span_trees(self) -> None: """Method for viewing trace trees.""" trees = self._get_event_span_trees() for tree in trees: print( tree.show( stdout=False, sorting=True, key=lambda node: node.data ) ) print("")
## Spans¶
Spans are "operations" in LlamaIndex (typically function calls). Spans can contain more spans, and each span contains associated events.
The below code shows how to observe spans as they happen in LlamaIndex
In [ ]:
Copied!
```
from typing import Any, Optional

from llama_index.core.instrumentation.span import SimpleSpan
from llama_index.core.instrumentation.span_handlers.base import BaseSpanHandler


class ExampleSpanHandler(BaseSpanHandler[SimpleSpan]):
    span_dict = {}

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "ExampleSpanHandler"

    def new_span(
        self,
        id_: str,
        bound_args: Any,
        instance: Optional[Any] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[SimpleSpan]:
        """Create a span."""
        # logic for creating a new MyCustomSpan
        if id_ not in self.span_dict:
            self.span_dict[id_] = []
        self.span_dict[id_].append(
            SimpleSpan(id_=id_, parent_id=parent_span_id)
        )

    def prepare_to_exit_span(
        self,
        id_: str,
        bound_args: Any,
        instance: Optional[Any] = None,
        result: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        """Logic for preparing to exit a span."""
        pass
        # if id in self.span_dict:
        #    return self.span_dict[id].pop()

    def prepare_to_drop_span(
        self,
        id_: str,
        bound_args: Any,
        instance: Optional[Any] = None,
        err: Optional[BaseException] = None,
        **kwargs: Any,
    ) -> Any:
        """Logic for preparing to drop a span."""
        pass
        # if id in self.span_dict:
        #    return self.span_dict[id].pop()

```

from typing import Any, Optional from llama_index.core.instrumentation.span import SimpleSpan from llama_index.core.instrumentation.span_handlers.base import BaseSpanHandler class ExampleSpanHandler(BaseSpanHandler[SimpleSpan]): span_dict = {} @classmethod def class_name(cls) -> str: """Class name.""" return "ExampleSpanHandler" def new_span( self, id_: str, bound_args: Any, instance: Optional[Any] = None, parent_span_id: Optional[str] = None, tags: Optional[Dict[str, Any]] = None, **kwargs: Any, ) -> Optional[SimpleSpan]: """Create a span.""" # logic for creating a new MyCustomSpan if id_ not in self.span_dict: self.span_dict[id_] = [] self.span_dict[id_].append( SimpleSpan(id_=id_, parent_id=parent_span_id) ) def prepare_to_exit_span( self, id_: str, bound_args: Any, instance: Optional[Any] = None, result: Optional[Any] = None, **kwargs: Any, ) -> Any: """Logic for preparing to exit a span.""" pass # if id in self.span_dict: # return self.span_dict[id].pop() def prepare_to_drop_span( self, id_: str, bound_args: Any, instance: Optional[Any] = None, err: Optional[BaseException] = None, **kwargs: Any, ) -> Any: """Logic for preparing to drop a span.""" pass # if id in self.span_dict: # return self.span_dict[id].pop()
## Putting it all Together¶
With our span handler and event handler defined, we can attach it to a dispatcher watch events and spans come in.
It is not mandatory to have both a span handler and event handler, you could have either-or, or both.
In [ ]:
Copied!
```
from llama_index.core.instrumentation import get_dispatcher
from llama_index.core.instrumentation.span_handlers import SimpleSpanHandler

# root dispatcher
root_dispatcher = get_dispatcher()

# register span handler
event_handler = ExampleEventHandler()
span_handler = ExampleSpanHandler()
simple_span_handler = SimpleSpanHandler()
root_dispatcher.add_span_handler(span_handler)
root_dispatcher.add_span_handler(simple_span_handler)
root_dispatcher.add_event_handler(event_handler)

```

from llama_index.core.instrumentation import get_dispatcher from llama_index.core.instrumentation.span_handlers import SimpleSpanHandler # root dispatcher root_dispatcher = get_dispatcher() # register span handler event_handler = ExampleEventHandler() span_handler = ExampleSpanHandler() simple_span_handler = SimpleSpanHandler() root_dispatcher.add_span_handler(span_handler) root_dispatcher.add_span_handler(simple_span_handler) root_dispatcher.add_event_handler(event_handler)
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

```

import os os.environ["OPENAI_API_KEY"] = "sk-..."
In [ ]:
Copied!
```
from llama_index.core import Document, VectorStoreIndex

index = VectorStoreIndex.from_documents([Document.example()])

query_engine = index.as_query_engine()

query_engine.query("Tell me about LLMs?")

```

from llama_index.core import Document, VectorStoreIndex index = VectorStoreIndex.from_documents([Document.example()]) query_engine = index.as_query_engine() query_engine.query("Tell me about LLMs?")
```
-----------------------
7182e98f-1b8a-4aba-af18-3982b862c794
2024-05-06 14:00:35.931813
BaseEmbedding.get_text_embedding_batch-632972aa-3345-49cb-ae2f-46f3166e3afc
Event type: EmbeddingStartEvent
{'model_name': 'text-embedding-ada-002', 'embed_batch_size': 100, 'num_workers': None, 'additional_kwargs': {}, 'api_base': 'https://api.openai.com/v1', 'api_version': '', 'max_retries': 10, 'timeout': 60.0, 'default_headers': None, 'reuse_client': True, 'dimensions': None, 'class_name': 'OpenAIEmbedding'}
-----------------------
-----------------------
ba86e41f-cadf-4f1f-8908-8ee90404d668
2024-05-06 14:00:36.256237
BaseEmbedding.get_text_embedding_batch-632972aa-3345-49cb-ae2f-46f3166e3afc
Event type: EmbeddingEndEvent
['filename: README.md\ncategory: codebase\n\nContext\nLLMs are a phenomenal piece of technology for knowledge generation and reasoning.\nThey are pre-trained on large amounts of publicly available data.\nHow do we best augment LLMs with our own private data?\nWe need a comprehensive toolkit to help perform this data augmentation for LLMs.\n\nProposed Solution\nThat\'s where LlamaIndex comes in. LlamaIndex is a "data framework" to help\nyou build LLM  apps. It provides the following tools:\n\nOffers data connectors to ingest your existing data sources and data formats\n(APIs, PDFs, docs, SQL, etc.)\nProvides ways to structure your data (indices, graphs) so that this data can be\neasily used with LLMs.\nProvides an advanced retrieval/query interface over your data:\nFeed in any LLM input prompt, get back retrieved context and knowledge-augmented output.\nAllows easy integrations with your outer application framework\n(e.g. with LangChain, Flask, Docker, ChatGPT, anything else).\nLlamaIndex provides tools for both beginner users and advanced users.\nOur high-level API allows beginner users to use LlamaIndex to ingest and\nquery their data in 5 lines of code. Our lower-level APIs allow advanced users to\ncustomize and extend any module (data connectors, indices, retrievers, query engines,\nreranking modules), to fit their needs.']
[-0.005768016912043095, 0.02242799662053585, -0.020438531413674355, -0.040361806750297546, -0.01757599227130413]
-----------------------
-----------------------
06935377-f1e4-4fb9-b866-86f7520dfe2b
2024-05-06 14:00:36.305798
BaseQueryEngine.query-a766ae6c-6445-43b4-b1fc-9c29bae99556
Event type: QueryStartEvent
Tell me about LLMs?
-----------------------
-----------------------
62608f4f-67a1-4e2c-a653-24a4430529bb
2024-05-06 14:00:36.305998
BaseRetriever.retrieve-4e25a2a3-43a9-45e3-a7b9-59f4d54e8f00
Event type: RetrievalStartEvent
Tell me about LLMs?
-----------------------
-----------------------
e984c840-919b-4dc7-943d-5c49fbff48b8
2024-05-06 14:00:36.306265
BaseEmbedding.get_query_embedding-d30934f4-7bd2-4425-beda-12b5f55bc38b
Event type: EmbeddingStartEvent
{'model_name': 'text-embedding-ada-002', 'embed_batch_size': 100, 'num_workers': None, 'additional_kwargs': {}, 'api_base': 'https://api.openai.com/v1', 'api_version': '', 'max_retries': 10, 'timeout': 60.0, 'default_headers': None, 'reuse_client': True, 'dimensions': None, 'class_name': 'OpenAIEmbedding'}
-----------------------
-----------------------
c09fa993-a892-4efe-9f1b-7238ff6e5c62
2024-05-06 14:00:36.481459
BaseEmbedding.get_query_embedding-d30934f4-7bd2-4425-beda-12b5f55bc38b
Event type: EmbeddingEndEvent
['Tell me about LLMs?']
[0.00793155562132597, 0.011421983130276203, -0.010342259891331196, -0.03294854983687401, -0.03647972270846367]
-----------------------
-----------------------
b076d239-628d-4b4c-94ed-25aa2ca4b02b
2024-05-06 14:00:36.484080
BaseRetriever.retrieve-4e25a2a3-43a9-45e3-a7b9-59f4d54e8f00
Event type: RetrievalEndEvent
Tell me about LLMs?
[NodeWithScore(node=TextNode(id_='8de2b6b2-3fda-4f9b-95a8-a3ced6cfb0e5', embedding=None, metadata={'filename': 'README.md', 'category': 'codebase'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='29e2bc8f-b62c-4752-b5eb-11346c5cbe50', node_type=<ObjectType.DOCUMENT: '4'>, metadata={'filename': 'README.md', 'category': 'codebase'}, hash='3183371414f6a23e9a61e11b45ec45f808b148f9973166cfed62226e3505eb05')}, text='Context\nLLMs are a phenomenal piece of technology for knowledge generation and reasoning.\nThey are pre-trained on large amounts of publicly available data.\nHow do we best augment LLMs with our own private data?\nWe need a comprehensive toolkit to help perform this data augmentation for LLMs.\n\nProposed Solution\nThat\'s where LlamaIndex comes in. LlamaIndex is a "data framework" to help\nyou build LLM  apps. It provides the following tools:\n\nOffers data connectors to ingest your existing data sources and data formats\n(APIs, PDFs, docs, SQL, etc.)\nProvides ways to structure your data (indices, graphs) so that this data can be\neasily used with LLMs.\nProvides an advanced retrieval/query interface over your data:\nFeed in any LLM input prompt, get back retrieved context and knowledge-augmented output.\nAllows easy integrations with your outer application framework\n(e.g. with LangChain, Flask, Docker, ChatGPT, anything else).\nLlamaIndex provides tools for both beginner users and advanced users.\nOur high-level API allows beginner users to use LlamaIndex to ingest and\nquery their data in 5 lines of code. Our lower-level APIs allow advanced users to\ncustomize and extend any module (data connectors, indices, retrievers, query engines,\nreranking modules), to fit their needs.', start_char_idx=1, end_char_idx=1279, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), score=0.807312731672428)]
-----------------------
-----------------------
5e3289be-c597-48e7-ad3f-787722b766ea
2024-05-06 14:00:36.484436
BaseSynthesizer.synthesize-23d8d12d-a36e-423b-8776-042f1ff62546
Event type: SynthesizeStartEvent
Tell me about LLMs?
-----------------------
-----------------------
e9d9fe28-16d5-4301-8510-61aa11fa4951
2024-05-06 14:00:36.486070
Refine.get_response-e085393a-5510-4c3a-ba35-535caf58e159
Event type: GetResponseStartEvent
Tell me about LLMs?
-----------------------
-----------------------
29ce3778-d7cc-4095-b6b7-c811cd61ca5d
2024-05-06 14:00:36.486837
LLM.predict-007a74e7-34ff-488b-81b1-4ffb69df68a0
Event type: LLMPredictStartEvent
metadata={'prompt_type': <PromptType.QUESTION_ANSWER: 'text_qa'>} template_vars=['context_str', 'query_str'] kwargs={'query_str': 'Tell me about LLMs?'} output_parser=None template_var_mappings={} function_mappings={} default_template=PromptTemplate(metadata={'prompt_type': <PromptType.QUESTION_ANSWER: 'text_qa'>}, template_vars=['context_str', 'query_str'], kwargs={'query_str': 'Tell me about LLMs?'}, output_parser=None, template_var_mappings=None, function_mappings=None, template='Context information is below.\n---------------------\n{context_str}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {query_str}\nAnswer: ') conditionals=[(<function is_chat_model at 0x13a72af80>, ChatPromptTemplate(metadata={'prompt_type': <PromptType.CUSTOM: 'custom'>}, template_vars=['context_str', 'query_str'], kwargs={'query_str': 'Tell me about LLMs?'}, output_parser=None, template_var_mappings=None, function_mappings=None, message_templates=[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content="You are an expert Q&A system that is trusted around the world.\nAlways answer the query using the provided context information, and not prior knowledge.\nSome rules to follow:\n1. Never directly reference the given context in your answer.\n2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.", additional_kwargs={}), ChatMessage(role=<MessageRole.USER: 'user'>, content='Context information is below.\n---------------------\n{context_str}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {query_str}\nAnswer: ', additional_kwargs={})]))]
{'context_str': 'filename: README.md\ncategory: codebase\n\nContext\nLLMs are a phenomenal piece of technology for knowledge generation and reasoning.\nThey are pre-trained on large amounts of publicly available data.\nHow do we best augment LLMs with our own private data?\nWe need a comprehensive toolkit to help perform this data augmentation for LLMs.\n\nProposed Solution\nThat\'s where LlamaIndex comes in. LlamaIndex is a "data framework" to help\nyou build LLM  apps. It provides the following tools:\n\nOffers data connectors to ingest your existing data sources and data formats\n(APIs, PDFs, docs, SQL, etc.)\nProvides ways to structure your data (indices, graphs) so that this data can be\neasily used with LLMs.\nProvides an advanced retrieval/query interface over your data:\nFeed in any LLM input prompt, get back retrieved context and knowledge-augmented output.\nAllows easy integrations with your outer application framework\n(e.g. with LangChain, Flask, Docker, ChatGPT, anything else).\nLlamaIndex provides tools for both beginner users and advanced users.\nOur high-level API allows beginner users to use LlamaIndex to ingest and\nquery their data in 5 lines of code. Our lower-level APIs allow advanced users to\ncustomize and extend any module (data connectors, indices, retrievers, query engines,\nreranking modules), to fit their needs.'}
-----------------------
-----------------------
2042b4ab-99b4-410d-a997-ed97dda7a7d1
2024-05-06 14:00:36.487359
LLM.predict-007a74e7-34ff-488b-81b1-4ffb69df68a0
Event type: LLMChatStartEvent
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content="You are an expert Q&A system that is trusted around the world.\nAlways answer the query using the provided context information, and not prior knowledge.\nSome rules to follow:\n1. Never directly reference the given context in your answer.\n2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.", additional_kwargs={}), ChatMessage(role=<MessageRole.USER: 'user'>, content='Context information is below.\n---------------------\nfilename: README.md\ncategory: codebase\n\nContext\nLLMs are a phenomenal piece of technology for knowledge generation and reasoning.\nThey are pre-trained on large amounts of publicly available data.\nHow do we best augment LLMs with our own private data?\nWe need a comprehensive toolkit to help perform this data augmentation for LLMs.\n\nProposed Solution\nThat\'s where LlamaIndex comes in. LlamaIndex is a "data framework" to help\nyou build LLM  apps. It provides the following tools:\n\nOffers data connectors to ingest your existing data sources and data formats\n(APIs, PDFs, docs, SQL, etc.)\nProvides ways to structure your data (indices, graphs) so that this data can be\neasily used with LLMs.\nProvides an advanced retrieval/query interface over your data:\nFeed in any LLM input prompt, get back retrieved context and knowledge-augmented output.\nAllows easy integrations with your outer application framework\n(e.g. with LangChain, Flask, Docker, ChatGPT, anything else).\nLlamaIndex provides tools for both beginner users and advanced users.\nOur high-level API allows beginner users to use LlamaIndex to ingest and\nquery their data in 5 lines of code. Our lower-level APIs allow advanced users to\ncustomize and extend any module (data connectors, indices, retrievers, query engines,\nreranking modules), to fit their needs.\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: Tell me about LLMs?\nAnswer: ', additional_kwargs={})]
{}
{'system_prompt': None, 'pydantic_program_mode': <PydanticProgramMode.DEFAULT: 'default'>, 'model': 'gpt-3.5-turbo', 'temperature': 0.1, 'max_tokens': None, 'logprobs': None, 'top_logprobs': 0, 'additional_kwargs': {}, 'max_retries': 3, 'timeout': 60.0, 'default_headers': None, 'reuse_client': True, 'api_base': 'https://api.openai.com/v1', 'api_version': '', 'class_name': 'openai_llm'}
-----------------------
-----------------------
67b5c0f5-135e-4571-86a4-6e7efa6a40ff
2024-05-06 14:00:37.627923
LLM.predict-007a74e7-34ff-488b-81b1-4ffb69df68a0
Event type: LLMChatEndEvent
[ChatMessage(role=<MessageRole.SYSTEM: 'system'>, content="You are an expert Q&A system that is trusted around the world.\nAlways answer the query using the provided context information, and not prior knowledge.\nSome rules to follow:\n1. Never directly reference the given context in your answer.\n2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.", additional_kwargs={}), ChatMessage(role=<MessageRole.USER: 'user'>, content='Context information is below.\n---------------------\nfilename: README.md\ncategory: codebase\n\nContext\nLLMs are a phenomenal piece of technology for knowledge generation and reasoning.\nThey are pre-trained on large amounts of publicly available data.\nHow do we best augment LLMs with our own private data?\nWe need a comprehensive toolkit to help perform this data augmentation for LLMs.\n\nProposed Solution\nThat\'s where LlamaIndex comes in. LlamaIndex is a "data framework" to help\nyou build LLM  apps. It provides the following tools:\n\nOffers data connectors to ingest your existing data sources and data formats\n(APIs, PDFs, docs, SQL, etc.)\nProvides ways to structure your data (indices, graphs) so that this data can be\neasily used with LLMs.\nProvides an advanced retrieval/query interface over your data:\nFeed in any LLM input prompt, get back retrieved context and knowledge-augmented output.\nAllows easy integrations with your outer application framework\n(e.g. with LangChain, Flask, Docker, ChatGPT, anything else).\nLlamaIndex provides tools for both beginner users and advanced users.\nOur high-level API allows beginner users to use LlamaIndex to ingest and\nquery their data in 5 lines of code. Our lower-level APIs allow advanced users to\ncustomize and extend any module (data connectors, indices, retrievers, query engines,\nreranking modules), to fit their needs.\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: Tell me about LLMs?\nAnswer: ', additional_kwargs={})]
assistant: LLMs are a type of technology used for knowledge generation and reasoning. They are pre-trained on large amounts of publicly available data.
-----------------------
-----------------------
42cb1fc6-3d8a-4dce-81f1-de43617a37fd
2024-05-06 14:00:37.628432
LLM.predict-007a74e7-34ff-488b-81b1-4ffb69df68a0
Event type: LLMPredictEndEvent
LLMs are a type of technology used for knowledge generation and reasoning. They are pre-trained on large amounts of publicly available data.
-----------------------
-----------------------
4498248d-d07a-4460-87c7-3a6f310c4cb3
2024-05-06 14:00:37.628634
Refine.get_response-e085393a-5510-4c3a-ba35-535caf58e159
Event type: GetResponseEndEvent
LLMs are a type of technology used for knowledge generation and reasoning. They are pre-trained on large amounts of publicly available data.
-----------------------
-----------------------
f1d7fda7-de82-4149-8cd9-b9a17dba169b
2024-05-06 14:00:37.628826
BaseSynthesizer.synthesize-23d8d12d-a36e-423b-8776-042f1ff62546
Event type: SynthesizeEndEvent
LLMs are a type of technology used for knowledge generation and reasoning. They are pre-trained on large amounts of publicly available data.
Tell me about LLMs?
-----------------------
-----------------------
2f564649-dbbb-4adc-a552-552f54358112
2024-05-06 14:00:37.629251
BaseQueryEngine.query-a766ae6c-6445-43b4-b1fc-9c29bae99556
Event type: QueryEndEvent
LLMs are a type of technology used for knowledge generation and reasoning. They are pre-trained on large amounts of publicly available data.
Tell me about LLMs?
-----------------------

```

Out[ ]:
```
Response(response='LLMs are a type of technology used for knowledge generation and reasoning. They are pre-trained on large amounts of publicly available data.', source_nodes=[NodeWithScore(node=TextNode(id_='8de2b6b2-3fda-4f9b-95a8-a3ced6cfb0e5', embedding=None, metadata={'filename': 'README.md', 'category': 'codebase'}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={<NodeRelationship.SOURCE: '1'>: RelatedNodeInfo(node_id='29e2bc8f-b62c-4752-b5eb-11346c5cbe50', node_type=<ObjectType.DOCUMENT: '4'>, metadata={'filename': 'README.md', 'category': 'codebase'}, hash='3183371414f6a23e9a61e11b45ec45f808b148f9973166cfed62226e3505eb05')}, text='Context\nLLMs are a phenomenal piece of technology for knowledge generation and reasoning.\nThey are pre-trained on large amounts of publicly available data.\nHow do we best augment LLMs with our own private data?\nWe need a comprehensive toolkit to help perform this data augmentation for LLMs.\n\nProposed Solution\nThat\'s where LlamaIndex comes in. LlamaIndex is a "data framework" to help\nyou build LLM  apps. It provides the following tools:\n\nOffers data connectors to ingest your existing data sources and data formats\n(APIs, PDFs, docs, SQL, etc.)\nProvides ways to structure your data (indices, graphs) so that this data can be\neasily used with LLMs.\nProvides an advanced retrieval/query interface over your data:\nFeed in any LLM input prompt, get back retrieved context and knowledge-augmented output.\nAllows easy integrations with your outer application framework\n(e.g. with LangChain, Flask, Docker, ChatGPT, anything else).\nLlamaIndex provides tools for both beginner users and advanced users.\nOur high-level API allows beginner users to use LlamaIndex to ingest and\nquery their data in 5 lines of code. Our lower-level APIs allow advanced users to\ncustomize and extend any module (data connectors, indices, retrievers, query engines,\nreranking modules), to fit their needs.', start_char_idx=1, end_char_idx=1279, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), score=0.807312731672428)], metadata={'8de2b6b2-3fda-4f9b-95a8-a3ced6cfb0e5': {'filename': 'README.md', 'category': 'codebase'}})
```

In [ ]:
Copied!
```
event_handler.print_event_span_trees()

```

event_handler.print_event_span_trees()
```
BaseEmbedding.get_text_embedding_batch-632972aa-3345-49cb-ae2f-46f3166e3afc (SPAN)
├── EmbeddingStartEvent: 7182e98f-1b8a-4aba-af18-3982b862c794
└── EmbeddingEndEvent: ba86e41f-cadf-4f1f-8908-8ee90404d668


BaseQueryEngine.query-a766ae6c-6445-43b4-b1fc-9c29bae99556 (SPAN)
├── QueryStartEvent: 06935377-f1e4-4fb9-b866-86f7520dfe2b
└── QueryEndEvent: 2f564649-dbbb-4adc-a552-552f54358112


BaseRetriever.retrieve-4e25a2a3-43a9-45e3-a7b9-59f4d54e8f00 (SPAN)
├── RetrievalStartEvent: 62608f4f-67a1-4e2c-a653-24a4430529bb
└── RetrievalEndEvent: b076d239-628d-4b4c-94ed-25aa2ca4b02b


BaseEmbedding.get_query_embedding-d30934f4-7bd2-4425-beda-12b5f55bc38b (SPAN)
├── EmbeddingStartEvent: e984c840-919b-4dc7-943d-5c49fbff48b8
└── EmbeddingEndEvent: c09fa993-a892-4efe-9f1b-7238ff6e5c62


BaseSynthesizer.synthesize-23d8d12d-a36e-423b-8776-042f1ff62546 (SPAN)
├── SynthesizeStartEvent: 5e3289be-c597-48e7-ad3f-787722b766ea
└── SynthesizeEndEvent: f1d7fda7-de82-4149-8cd9-b9a17dba169b


Refine.get_response-e085393a-5510-4c3a-ba35-535caf58e159 (SPAN)
├── GetResponseStartEvent: e9d9fe28-16d5-4301-8510-61aa11fa4951
└── GetResponseEndEvent: 4498248d-d07a-4460-87c7-3a6f310c4cb3


LLM.predict-007a74e7-34ff-488b-81b1-4ffb69df68a0 (SPAN)
├── LLMPredictStartEvent: 29ce3778-d7cc-4095-b6b7-c811cd61ca5d
├── LLMChatStartEvent: 2042b4ab-99b4-410d-a997-ed97dda7a7d1
├── LLMChatEndEvent: 67b5c0f5-135e-4571-86a4-6e7efa6a40ff
└── LLMPredictEndEvent: 42cb1fc6-3d8a-4dce-81f1-de43617a37fd



```

In [ ]:
Copied!
```
simple_span_handler.print_trace_trees()

```

simple_span_handler.print_trace_trees()
```
BaseEmbedding.get_text_embedding_batch-632972aa-3345-49cb-ae2f-46f3166e3afc (0.326418)


BaseQueryEngine.query-a766ae6c-6445-43b4-b1fc-9c29bae99556 (1.323617)
└── RetrieverQueryEngine._query-40135aed-9aa5-4197-a05d-d461afb524d0 (1.32328)
    ├── BaseRetriever.retrieve-4e25a2a3-43a9-45e3-a7b9-59f4d54e8f00 (0.178294)
    │   └── VectorIndexRetriever._retrieve-8ead50e0-7243-42d1-b1ed-d2a2f2ceea48 (0.177893)
    │       └── BaseEmbedding.get_query_embedding-d30934f4-7bd2-4425-beda-12b5f55bc38b (0.176907)
    └── BaseSynthesizer.synthesize-23d8d12d-a36e-423b-8776-042f1ff62546 (1.144761)
        └── CompactAndRefine.get_response-ec49a727-bf17-4d80-bf82-80ec2a906063 (1.144148)
            └── Refine.get_response-e085393a-5510-4c3a-ba35-535caf58e159 (1.142698)
                └── LLM.predict-007a74e7-34ff-488b-81b1-4ffb69df68a0 (1.141744)



```

