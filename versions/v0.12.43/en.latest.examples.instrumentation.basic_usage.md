# Instrumentation: Basic Usage¶
The `instrumentation` module can be used for observability and monitoring of your llama-index application. It is comprised of the following core abstractions:
  * `Event` — represents a single moment in time that a certain occurrence took place within the execution of the application’s code.
  * `EventHandler` — listen to the occurrences of `Event`'s and execute code logic at these moments in time.
  * `Span` — represents the execution flow of a particular part in the application’s code and thus contains `Event`'s.
  * `SpanHandler` — is responsible for the entering, exiting, and dropping (i.e., early exiting due to error) of `Span`'s.
  * `Dispatcher` — emits `Event`'s as well as signals to enter/exit/drop a `Span` to the appropriate handlers.


In this notebook, we demonstrate the basic usage pattern of `instrumentation`:
  1. Define your custom `EventHandler`
  2. Define your custom `SpanHandler` which handles an associated `Span` type
  3. Attach your `EventHandler` and `SpanHandler` to the dispatcher of choice (here, we'll attach it to the root dispatcher).


In [ ]:
Copied!
```
import nest_asyncio

nest_asyncio.apply()

```

import nest_asyncio nest_asyncio.apply()
### Custom Event Handlers¶
In [ ]:
Copied!
```
from llama_index.core.instrumentation.event_handlers import BaseEventHandler

```

from llama_index.core.instrumentation.event_handlers import BaseEventHandler
Defining your custom `EventHandler` involves subclassing the `BaseEventHandler`. Doing so, requires defining logic for the abstract method `handle()`.
In [ ]:
Copied!
```
class MyEventHandler(BaseEventHandler):
    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "MyEventHandler"

    def handle(self, event) -> None:
        """Logic for handling event."""
        # THIS IS WHERE YOU ADD YOUR LOGIC TO HANDLE EVENTS
        print(event.dict())
        print("")
        with open("log.txt", "a") as f:
            f.write(str(event))
            f.write("\n")

```

class MyEventHandler(BaseEventHandler): @classmethod def class_name(cls) -> str: """Class name.""" return "MyEventHandler" def handle(self, event) -> None: """Logic for handling event.""" # THIS IS WHERE YOU ADD YOUR LOGIC TO HANDLE EVENTS print(event.dict()) print("") with open("log.txt", "a") as f: f.write(str(event)) f.write("\n")
### Custom Span Handlers¶
`SpanHandler` also involve subclassing a base class, in this case `BaseSpanHandler`. However, since `SpanHandler`'s work with an associated `Span` type, you will need to create this as well if you want to handle a new `Span` type.
In [ ]:
Copied!
```
from llama_index.core.instrumentation.span import BaseSpan

```

from llama_index.core.instrumentation.span import BaseSpan
In [ ]:
Copied!
```
import inspect
from typing import Any, Dict, Optional
from llama_index.core.bridge.pydantic import Field
from llama_index.core.instrumentation.span.base import BaseSpan
from llama_index.core.instrumentation.span_handlers import BaseSpanHandler


class MyCustomSpan(BaseSpan):
    custom_field_1: Any = Field(...)
    custom_field_2: Any = Field(...)


class MyCustomSpanHandler(BaseSpanHandler[MyCustomSpan]):
    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "MyCustomSpanHandler"

    def new_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[MyCustomSpan]:
        """Create a span."""
        # logic for creating a new MyCustomSpan
        pass

    def prepare_to_exit_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        result: Optional[Any] = None,
        **kwargs: Any,
    ) -> Any:
        """Logic for preparing to exit a span."""
        pass

    def prepare_to_drop_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        err: Optional[BaseException] = None,
        **kwargs: Any,
    ) -> Any:
        """Logic for preparing to drop a span."""
        pass

```

import inspect from typing import Any, Dict, Optional from llama_index.core.bridge.pydantic import Field from llama_index.core.instrumentation.span.base import BaseSpan from llama_index.core.instrumentation.span_handlers import BaseSpanHandler class MyCustomSpan(BaseSpan): custom_field_1: Any = Field(...) custom_field_2: Any = Field(...) class MyCustomSpanHandler(BaseSpanHandler[MyCustomSpan]): @classmethod def class_name(cls) -> str: """Class name.""" return "MyCustomSpanHandler" def new_span( self, id_: str, bound_args: inspect.BoundArguments, instance: Optional[Any] = None, parent_span_id: Optional[str] = None, tags: Optional[Dict[str, Any]] = None, **kwargs: Any, ) -> Optional[MyCustomSpan]: """Create a span.""" # logic for creating a new MyCustomSpan pass def prepare_to_exit_span( self, id_: str, bound_args: inspect.BoundArguments, instance: Optional[Any] = None, result: Optional[Any] = None, **kwargs: Any, ) -> Any: """Logic for preparing to exit a span.""" pass def prepare_to_drop_span( self, id_: str, bound_args: inspect.BoundArguments, instance: Optional[Any] = None, err: Optional[BaseException] = None, **kwargs: Any, ) -> Any: """Logic for preparing to drop a span.""" pass
For this notebook, we'll use `SimpleSpanHandler` that works with the `SimpleSpan` type.
In [ ]:
Copied!
```
from llama_index.core.instrumentation.span_handlers import SimpleSpanHandler

```

from llama_index.core.instrumentation.span_handlers import SimpleSpanHandler
### Dispatcher¶
Now that we have our `EventHandler` and our `SpanHandler`, we can attach it to a `Dispatcher` that will emit `Event`'s and signals to start/exit/drop a `Span` to the appropriate handlers. Those that are familiar with `Logger` from the `logging` Python module, might notice that `Dispatcher` adopts a similar interface. What's more is that `Dispatcher` also utilizes a similar hierarchy and propagation scheme as `Logger`. Specifically, a `dispatcher` will emit `Event`'s to its handlers and by default propagate these events to its parent `Dispatcher` for it to send to its own handlers.
In [ ]:
Copied!
```
import llama_index.core.instrumentation as instrument

dispatcher = instrument.get_dispatcher()  # modify root dispatcher

```

import llama_index.core.instrumentation as instrument dispatcher = instrument.get_dispatcher() # modify root dispatcher
In [ ]:
Copied!
```
span_handler = SimpleSpanHandler()

dispatcher.add_event_handler(MyEventHandler())
dispatcher.add_span_handler(span_handler)

```

span_handler = SimpleSpanHandler() dispatcher.add_event_handler(MyEventHandler()) dispatcher.add_span_handler(span_handler)
You can also get dispatcher's by name. Purely for the sake of demonstration, in the cells below we get the dispatcher that is defined in the `base.base_query_engine` submodule of `llama_index.core`.
In [ ]:
Copied!
```
qe_dispatcher = instrument.get_dispatcher(
    "llama_index.core.base.base_query_engine"
)

```

qe_dispatcher = instrument.get_dispatcher( "llama_index.core.base.base_query_engine" )
In [ ]:
Copied!
```
qe_dispatcher

```

qe_dispatcher
Out[ ]:
```
Dispatcher(name='llama_index.core.base.base_query_engine', event_handlers=[], span_handlers=[NullSpanHandler(open_spans={}, current_span_id=None)], parent_name='root', manager=<llama_index.core.instrumentation.dispatcher.Manager object at 0x1481ab4c0>, root_name='root', propagate=True)
```

In [ ]:
Copied!
```
qe_dispatcher.parent

```

qe_dispatcher.parent
Out[ ]:
```
Dispatcher(name='root', event_handlers=[NullEventHandler(), MyEventHandler()], span_handlers=[NullSpanHandler(open_spans={}, current_span_id=None), SimpleSpanHandler(open_spans={}, current_span_id=None, completed_spans=[])], parent_name='', manager=None, root_name='root', propagate=False)
```

### Test It Out¶
In [ ]:
Copied!
```
!mkdir -p 'data/'
!wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'

```

!mkdir -p 'data/' !wget 'https://raw.githubusercontent.com/run-llama/llama_index/main/docs/docs/examples/data/paul_graham/paul_graham_essay.txt' -O 'data/paul_graham/paul_graham_essay.txt'
```
data/paul_graham/paul_graham_essay.txt: No such file or directory

```

In [ ]:
Copied!
```
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

documents = SimpleDirectoryReader(input_dir="./data").load_data()
index = VectorStoreIndex.from_documents(documents)

```

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex documents = SimpleDirectoryReader(input_dir="./data").load_data() index = VectorStoreIndex.from_documents(documents)
In [ ]:
Copied!
```
query_engine = index.as_query_engine()

```

query_engine = index.as_query_engine()
#### Sync¶
In [ ]:
Copied!
```
query_result = query_engine.query("Who is Paul?")

```

query_result = query_engine.query("Who is Paul?")
```
{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 50, 614289), 'id_': UUID('35643a53-52da-4547-b770-dba7600c9070'), 'class_name': 'QueryStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 50, 615966), 'id_': UUID('18fa9b70-6fbc-4ce7-9e45-1f292766e820'), 'class_name': 'RetrievalStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 50, 810658), 'id_': UUID('2aed6810-99a1-49ab-a6c4-5f242f1b1de3'), 'class_name': 'RetrievalEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 50, 811651), 'id_': UUID('6f8d96a2-4da0-485f-9a73-4dae2d026b48'), 'class_name': 'SynthesizeStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 50, 818960), 'id_': UUID('005e52bd-25f6-49cb-8766-5399098b7e51'), 'class_name': 'GetResponseStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 50, 823964), 'id_': UUID('52273f18-2865-42d3-a11e-acbe5bb56748'), 'class_name': 'LLMPredictStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 52, 375382), 'id_': UUID('54516719-425b-422a-b38c-8bd002d8fa74'), 'class_name': 'LLMPredictEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 52, 376003), 'id_': UUID('24ec9eb3-d2ad-46f7-8db2-faf68075c7b3'), 'class_name': 'GetResponseEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 52, 376347), 'id_': UUID('6d453292-374c-4fef-8bc4-ae164455a133'), 'class_name': 'SynthesizeEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 57, 52, 376505), 'id_': UUID('9919903a-dbb1-4bdf-8029-3e4fcd9ea073'), 'class_name': 'QueryEndEvent'}


```

#### Async¶
`Dispatcher` also works on async methods.
In [ ]:
Copied!
```
query_result = await query_engine.aquery("Who is Paul?")

```

query_result = await query_engine.aquery("Who is Paul?")
```
{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 35, 276918), 'id_': UUID('8ea98ded-91f2-45cf-b418-b92b3c7693bf'), 'class_name': 'QueryStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 35, 279006), 'id_': UUID('60ff04ce-0972-4fe1-bfaf-5ffaaea3ef4a'), 'class_name': 'RetrievalStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 35, 555879), 'id_': UUID('c29bb55e-b2e1-4637-a6cb-745a2424da90'), 'class_name': 'RetrievalEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 35, 557244), 'id_': UUID('dee202a1-f760-495e-a6f8-3644a535ff13'), 'class_name': 'SynthesizeStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 35, 564098), 'id_': UUID('c524828c-cdd7-4ddd-876a-5fda5f10143d'), 'class_name': 'GetResponseStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 35, 568930), 'id_': UUID('bd8e78ce-9a87-41a8-b009-e0694e09e0b3'), 'class_name': 'LLMPredictStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 37, 70264), 'id_': UUID('54633e8f-8f89-4a4c-9e79-f059f9dbecc2'), 'class_name': 'LLMPredictEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 37, 71236), 'id_': UUID('0a110c5c-3d4c-4eeb-8066-b8e512e69838'), 'class_name': 'GetResponseEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 37, 71652), 'id_': UUID('1152f15e-ac5b-4292-ad9f-45f8404183f9'), 'class_name': 'SynthesizeEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 58, 37, 71891), 'id_': UUID('8aa8f930-1ac2-4924-a185-00a06bc7ba79'), 'class_name': 'QueryEndEvent'}


```

#### Streaming¶
`Dispatcher` also works on methods that support streaming!
In [ ]:
Copied!
```
chat_engine = index.as_chat_engine()

```

chat_engine = index.as_chat_engine()
In [ ]:
Copied!
```
streaming_response = chat_engine.stream_chat("Tell me a joke.")

```

streaming_response = chat_engine.stream_chat("Tell me a joke.")
```
{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 31, 345865), 'id_': UUID('1d9643ca-368b-4e08-9878-ed7682196007'), 'class_name': 'AgentChatWithStepStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 31, 346727), 'id_': UUID('c38a18e3-0c2c-43b3-a1a9-0fb2e696e627'), 'class_name': 'AgentRunStepStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 31, 348524), 'id_': UUID('9a49dd15-715c-474a-b704-b9e8df919c50'), 'class_name': 'StreamChatStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 31, 975148), 'id_': UUID('c3b5b9eb-104d-461e-a081-e65ec9dc3131'), 'class_name': 'StreamChatEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 31, 977522), 'id_': UUID('2e6c3935-8ece-49bf-aacc-de18fd79da42'), 'class_name': 'QueryStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 31, 978389), 'id_': UUID('5c43f441-d262-427f-8ef7-b3b6e6e86f44'), 'class_name': 'RetrievalStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 32, 188462), 'id_': UUID('724dd93f-39a8-4b12-b056-194c4cf3ed72'), 'class_name': 'RetrievalEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 32, 189601), 'id_': UUID('27e5ac36-d313-4df6-bc8b-40b79e59698e'), 'class_name': 'SynthesizeStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 32, 208520), 'id_': UUID('77ec49c0-fb24-46dd-b843-954e241a0eb0'), 'class_name': 'GetResponseStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 32, 214106), 'id_': UUID('b28106fa-8d8e-49ca-92af-a37e0db45b9f'), 'class_name': 'LLMPredictStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 59544), 'id_': UUID('0e40cac7-9eb4-48d3-81bc-d01a5b3c0440'), 'class_name': 'LLMPredictEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 60941), 'id_': UUID('77e1d7eb-5807-4184-9e18-de4fdde18654'), 'class_name': 'GetResponseEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 61349), 'id_': UUID('565c9019-89b0-4dec-bb54-0d9642030009'), 'class_name': 'SynthesizeEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 61677), 'id_': UUID('3cba488e-1d69-4b75-a601-2cf467816ef0'), 'class_name': 'QueryEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 62157), 'id_': UUID('a550a4c7-40b3-43ac-abb5-5cab4b759888'), 'class_name': 'AgentRunStepEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 62417), 'id_': UUID('d99b6fd9-bf35-4c37-9625-da39cc5aef23'), 'class_name': 'AgentRunStepStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 63294), 'id_': UUID('b8015c1d-53b7-4530-812c-2ded8dab4c67'), 'class_name': 'StreamChatStartEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 387260), 'id_': UUID('d5bbdb58-be35-444d-b0f0-0ccbc570e54e'), 'delta': 'Why', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 389911), 'id_': UUID('91e78251-def6-4bfb-9712-20c4c0d2690a'), 'class_name': 'AgentRunStepEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 389700), 'id_': UUID('8b181253-1ea6-4ffb-b384-c425307d7b88'), 'delta': ' did', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 390495), 'id_': UUID('57dd72cf-8b8c-4596-8de7-4a701fc50125'), 'class_name': 'AgentChatWithStepEndEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 409497), 'id_': UUID('e6ceba61-5c78-4ee3-972e-c9e02dbddc7c'), 'delta': ' the', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 410653), 'id_': UUID('e9d8d9fe-1080-455c-8add-06b1774506bc'), 'delta': ' computer', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 449414), 'id_': UUID('04cffd87-ca8a-4efb-af2a-a99964610e4c'), 'delta': ' keep', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 450316), 'id_': UUID('21824a0a-3674-42d1-91c7-d8a865c2b270'), 'delta': ' its', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 495431), 'id_': UUID('a677507c-6b74-454f-a185-3df008e9e5ff'), 'delta': ' drinks', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 496188), 'id_': UUID('8b94885c-ce78-46cc-8ee6-938484ae2980'), 'delta': ' on', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 527857), 'id_': UUID('dc356d5d-c968-4d43-9903-bc158b73338a'), 'delta': ' the', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 529075), 'id_': UUID('f8a2637f-e746-418d-8921-4e7e8c26956f'), 'delta': ' motherboard', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 554042), 'id_': UUID('dd21cd77-c329-4947-ad77-7683885e0ce1'), 'delta': '?', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 557320), 'id_': UUID('93a2a7e1-7fe5-4eb8-851e-1b3dea4df6b5'), 'delta': ' Because', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 608305), 'id_': UUID('445cb52e-9cf3-4f85-aba3-6383974e6b5f'), 'delta': ' it', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 609392), 'id_': UUID('bd7bb3dc-5bd7-418e-a18a-203cdb701bcb'), 'delta': ' had', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 609896), 'id_': UUID('e981bdb3-57ca-456e-8353-be087ea6bb55'), 'delta': ' too', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 610659), 'id_': UUID('79b3eb21-6f8d-4a87-9f26-04e757a29da3'), 'delta': ' many', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 667840), 'id_': UUID('73073cd6-dfae-4632-a302-a4841a08f272'), 'delta': ' bytes', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 669579), 'id_': UUID('c30da40c-bf7d-49f0-9505-2345fc67fde7'), 'delta': '!', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 670733), 'id_': UUID('f9baf8fc-8755-4740-8fe4-f5a3c9d77f9e'), 'delta': ' 😄', 'class_name': 'StreamChatDeltaReceivedEvent'}

{'timestamp': datetime.datetime(2024, 3, 14, 15, 59, 33, 672180), 'id_': UUID('e07eb812-68b5-4027-8ee0-87bf6cd5c744'), 'class_name': 'StreamChatEndEvent'}


```

In [ ]:
Copied!
```
for token in streaming_response.response_gen:
    print(token, end="")

```

for token in streaming_response.response_gen: print(token, end="")
```
Why did the computer keep its drinks on the motherboard? Because it had too many bytes! 😄
```

### Printing Basic Trace Trees with `SimpleSpanHandler`¶
In [ ]:
Copied!
```
span_handler.print_trace_trees()

```

span_handler.print_trace_trees()
```
BaseQueryEngine.query-bda10f51-e5c8-4ef8-9467-c816b0c92797 (1.762367)
└── RetrieverQueryEngine._query-35da82df-8e64-43c5-9046-11df14b3b9f7 (1.760649)
    ├── BaseRetriever.retrieve-237d1b8d-f8b1-4e0b-908c-00087f086c2c (0.19558)
    │   └── VectorIndexRetriever._retrieve-af6479b8-3210-41df-9d6f-3af31059f274 (0.194024)
    └── BaseSynthesizer.synthesize-bf923672-6e60-4015-b6fe-0d0c9d1d35e3 (1.564853)
        └── CompactAndRefine.get_response-447c173e-4016-4376-9c56-a7171ea1ddf0 (1.564162)
            └── Refine.get_response-83b1159d-d33f-401f-a76e-bc3ee5095b57 (1.557365)
                └── LLM.predict-a5ab2252-1eb1-4413-9ef0-efa14c2c3b6b (1.552019)


BaseQueryEngine.aquery-7f3daee7-540f-4189-a350-a37e7e0596d5 (1.79559)
└── RetrieverQueryEngine._aquery-cc049d88-933a-41d3-abb4-06c5bd567e45 (1.793149)
    ├── BaseRetriever.aretrieve-c1a2ae34-3916-4069-81ba-7ba9b9d7235d (0.278098)
    │   └── VectorIndexRetriever._aretrieve-ef38d533-dd12-4fa5-9879-cd885124d8aa (0.276331)
    └── BaseSynthesizer.asynthesize-e3f02693-1563-4eec-898e-1043bbeec870 (1.514635)
        └── CompactAndRefine.aget_response-6cfcc5f8-1a47-4dde-aca7-8bd6543ce457 (1.513896)
            └── Refine.aget_response-7c2a4f67-f4bb-4065-b934-ac8dae7a9529 (1.507486)
                └── LLM.apredict-3ccf1ad0-d0b3-44bd-b64a-83bb652ed4c8 (1.502215)


AgentRunner.stream_chat-ae3bc1f0-b9ff-456c-a3b4-7264a5757336 (2.045523)
└── AgentRunner._chat-dd1d6afa-276a-4f7b-8c01-eb39df07b74d (2.045444)
    ├── AgentRunner._run_step-be8844fc-bd2c-4845-b5c5-378e9a1c97b5 (1.715629)
    │   ├── StreamingAgentChatResponse.write_response_to_history-b3fddc19-ee88-442b-9c95-0ea7e68fe4f3 (0.62843)
    │   └── BaseQueryEngine.query-4eb2f0ea-89c0-48d8-a757-92961a4c4275 (1.084424)
    │       └── RetrieverQueryEngine._query-fc5f2290-b715-4d33-82a6-d0eea3ba8625 (1.083421)
    │           ├── BaseRetriever.retrieve-62017ac0-3d6b-4ca4-91e9-d0548d226536 (0.211132)
    │           │   └── VectorIndexRetriever._retrieve-c77b4ae8-702c-42a9-b50a-a394c031c728 (0.209355)
    │           └── BaseSynthesizer.synthesize-7b6caba0-8156-4611-9f8a-baa3a7e5e151 (0.872036)
    │               └── CompactAndRefine.get_response-ec9651ef-4a88-4395-89da-52c2336baca3 (0.871197)
    │                   └── Refine.get_response-57a69243-b676-4f33-8c61-73a5ba6af03c (0.852795)
    │                       └── LLM.predict-b0fe909f-31e5-4655-8428-5dee6f6de7c8 (0.847305)
    └── AgentRunner._run_step-9a126f49-c704-45a8-9104-0e0a9d19c956 (0.327996)
        └── StreamingAgentChatResponse.write_response_to_history-b727aeea-dd0a-4c7a-9212-cf591caf7bb5 (0.609362)



```

