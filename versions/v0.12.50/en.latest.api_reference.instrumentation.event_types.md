# Event types
##  BaseEvent #
Bases: `BaseModel`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`timestamp` |  `datetime` |  |  `datetime.datetime(2025, 7, 19, 18, 39, 12, 68600)`  
`id_` |  `str` |  |  `'db8384cb-5be4-4751-87a1-d98fa4b26e8a'`  
`tags` |  `Dict[str, Any]` |  |  `{}`  
Source code in `llama_index_instrumentation/base/event.py`

| ```
class BaseEvent(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        # copy_on_model_validation = "deep"  # not supported in Pydantic V2...
    )
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
    id_: str = Field(default_factory=lambda: str(uuid4()))
    span_id: Optional[str] = Field(default_factory=active_span_id.get)  # type: ignore
    tags: Dict[str, Any] = Field(default={})

    @classmethod
    def class_name(cls) -> str:
        """Return class name."""
        return "BaseEvent"

    def dict(self, **kwargs: Any) -> Dict[str, Any]:
        """Keep for backwards compatibility."""
        return self.model_dump(**kwargs)

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        data = super().model_dump(**kwargs)
        data["class_name"] = self.class_name()
        return data

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Return class name.
Source code in `llama_index_instrumentation/base/event.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Return class name."""
    return "BaseEvent"

```
  
---|---  
###  dict #
```
dict(**kwargs: Any) -> Dict[str, Any]

```

Keep for backwards compatibility.
Source code in `llama_index_instrumentation/base/event.py`

| ```
def dict(self, **kwargs: Any) -> Dict[str, Any]:
    """Keep for backwards compatibility."""
    return self.model_dump(**kwargs)

```
  
---|---  
##  AgentChatWithStepEndEvent #
Bases: `BaseEvent`
AgentChatWithStepEndEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`response` |  `Optional[AGENT_CHAT_RESPONSE_TYPE]` |  Agent chat response. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
class AgentChatWithStepEndEvent(BaseEvent):
    """
    AgentChatWithStepEndEvent.

    Args:
        response (Optional[AGENT_CHAT_RESPONSE_TYPE]): Agent chat response.

    """

    response: Optional[AGENT_CHAT_RESPONSE_TYPE]

    @model_validator(mode="before")
    @classmethod
    def validate_response(cls: Any, values: Any) -> Any:
        """Validate response."""
        response = values.get("response")
        if response is None:
            pass
        elif not isinstance(response, AgentChatResponse) and not isinstance(
            response, StreamingAgentChatResponse
        ):
            raise ValueError(
                "response must be of type AgentChatResponse or StreamingAgentChatResponse"
            )

        return values

    @field_validator("response", mode="before")
    @classmethod
    def validate_response_type(cls: Any, response: Any) -> Any:
        """Validate response type."""
        if response is None:
            return response
        if not isinstance(response, AgentChatResponse) and not isinstance(
            response, StreamingAgentChatResponse
        ):
            raise ValueError(
                "response must be of type AgentChatResponse or StreamingAgentChatResponse"
            )
        return response

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "AgentChatWithStepEndEvent"

```
  
---|---  
###  validate_response `classmethod` #
```
validate_response(values: Any) -> Any

```

Validate response.
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
@model_validator(mode="before")
@classmethod
def validate_response(cls: Any, values: Any) -> Any:
    """Validate response."""
    response = values.get("response")
    if response is None:
        pass
    elif not isinstance(response, AgentChatResponse) and not isinstance(
        response, StreamingAgentChatResponse
    ):
        raise ValueError(
            "response must be of type AgentChatResponse or StreamingAgentChatResponse"
        )

    return values

```
  
---|---  
###  validate_response_type `classmethod` #
```
validate_response_type(response: Any) -> Any

```

Validate response type.
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
@field_validator("response", mode="before")
@classmethod
def validate_response_type(cls: Any, response: Any) -> Any:
    """Validate response type."""
    if response is None:
        return response
    if not isinstance(response, AgentChatResponse) and not isinstance(
        response, StreamingAgentChatResponse
    ):
        raise ValueError(
            "response must be of type AgentChatResponse or StreamingAgentChatResponse"
        )
    return response

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "AgentChatWithStepEndEvent"

```
  
---|---  
##  AgentChatWithStepStartEvent #
Bases: `BaseEvent`
AgentChatWithStepStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`user_msg` |  `str` |  User input message. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
class AgentChatWithStepStartEvent(BaseEvent):
    """
    AgentChatWithStepStartEvent.

    Args:
        user_msg (str): User input message.

    """

    user_msg: str

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "AgentChatWithStepStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "AgentChatWithStepStartEvent"

```
  
---|---  
##  AgentRunStepEndEvent #
Bases: `BaseEvent`
AgentRunStepEndEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`step_output` |  `TaskStepOutput` |  Task step output. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
class AgentRunStepEndEvent(BaseEvent):
    """
    AgentRunStepEndEvent.

    Args:
        step_output (TaskStepOutput): Task step output.

    """

    step_output: TaskStepOutput

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "AgentRunStepEndEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "AgentRunStepEndEvent"

```
  
---|---  
##  AgentRunStepStartEvent #
Bases: `BaseEvent`
AgentRunStepStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  Task ID. |  _required_  
`step` |  `Optional[TaskStep]` |  Task step. |  _required_  
`input` |  `Optional[str]` |  Optional input. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
class AgentRunStepStartEvent(BaseEvent):
    """
    AgentRunStepStartEvent.

    Args:
        task_id (str): Task ID.
        step (Optional[TaskStep]): Task step.
        input (Optional[str]): Optional input.

    """

    task_id: str
    step: Optional[TaskStep]
    input: Optional[str]

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "AgentRunStepStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "AgentRunStepStartEvent"

```
  
---|---  
##  AgentToolCallEvent #
Bases: `BaseEvent`
AgentToolCallEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`arguments` |  `str` |  Arguments. |  _required_  
`tool` |  `ToolMetadata` |  Tool metadata. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
class AgentToolCallEvent(BaseEvent):
    """
    AgentToolCallEvent.

    Args:
        arguments (str): Arguments.
        tool (ToolMetadata): Tool metadata.

    """

    arguments: str
    tool: ToolMetadata

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "AgentToolCallEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/agent.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "AgentToolCallEvent"

```
  
---|---  
##  StreamChatDeltaReceivedEvent #
Bases: `BaseEvent`
StreamChatDeltaReceivedEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`delta` |  `str` |  Delta received from the stream chat. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/chat_engine.py`

| ```
class StreamChatDeltaReceivedEvent(BaseEvent):
    """
    StreamChatDeltaReceivedEvent.

    Args:
        delta (str): Delta received from the stream chat.

    """

    delta: str

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "StreamChatDeltaReceivedEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/chat_engine.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "StreamChatDeltaReceivedEvent"

```
  
---|---  
##  StreamChatEndEvent #
Bases: `BaseEvent`
StreamChatEndEvent.
Fired at the end of writing to the stream chat-engine queue.
Source code in `llama-index-core/llama_index/core/instrumentation/events/chat_engine.py`

| ```
class StreamChatEndEvent(BaseEvent):
    """
    StreamChatEndEvent.

    Fired at the end of writing to the stream chat-engine queue.
    """

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "StreamChatEndEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/chat_engine.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "StreamChatEndEvent"

```
  
---|---  
##  StreamChatErrorEvent #
Bases: `BaseEvent`
StreamChatErrorEvent.
Fired when an exception is raised during the stream chat-engine operation.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`exception` |  `Exception` |  Exception raised during the stream chat operation. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/chat_engine.py`

| ```
class StreamChatErrorEvent(BaseEvent):
    """
    StreamChatErrorEvent.

    Fired when an exception is raised during the stream chat-engine operation.

    Args:
        exception (Exception): Exception raised during the stream chat operation.

    """

    exception: Exception

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "StreamChatErrorEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/chat_engine.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "StreamChatErrorEvent"

```
  
---|---  
##  StreamChatStartEvent #
Bases: `BaseEvent`
StreamChatStartEvent.
Fired at the start of writing to the stream chat-engine queue.
Source code in `llama-index-core/llama_index/core/instrumentation/events/chat_engine.py`

| ```
class StreamChatStartEvent(BaseEvent):
    """
    StreamChatStartEvent.

    Fired at the start of writing to the stream chat-engine queue.
    """

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "StreamChatStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/chat_engine.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "StreamChatStartEvent"

```
  
---|---  
##  EmbeddingEndEvent #
Bases: `BaseEvent`
EmbeddingEndEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`chunks` |  `List[str]` |  List of chunks. |  _required_  
`embeddings` |  `List[List[float]]` |  List of embeddings. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/embedding.py`

| ```
class EmbeddingEndEvent(BaseEvent):
    """
    EmbeddingEndEvent.

    Args:
        chunks (List[str]): List of chunks.
        embeddings (List[List[float]]): List of embeddings.

    """

    chunks: List[str]
    embeddings: List[List[float]]

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "EmbeddingEndEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/embedding.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "EmbeddingEndEvent"

```
  
---|---  
##  EmbeddingStartEvent #
Bases: `BaseEvent`
EmbeddingStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`model_dict` |  `dict` |  Model dictionary containing details about the embedding model. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/embedding.py`

| ```
class EmbeddingStartEvent(BaseEvent):
    """
    EmbeddingStartEvent.

    Args:
        model_dict (dict): Model dictionary containing details about the embedding model.

    """

    model_config = ConfigDict(protected_namespaces=("pydantic_model_",))
    model_dict: dict

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "EmbeddingStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/embedding.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "EmbeddingStartEvent"

```
  
---|---  
##  LLMChatEndEvent #
Bases: `BaseEvent`
LLMChatEndEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`messages` |  `List[ChatMessage]` |  List of chat messages. |  _required_  
`response` |  `Optional[ChatResponse]` |  Last chat response. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
class LLMChatEndEvent(BaseEvent):
    """
    LLMChatEndEvent.

    Args:
        messages (List[ChatMessage]): List of chat messages.
        response (Optional[ChatResponse]): Last chat response.

    """

    messages: List[ChatMessage]
    response: Optional[ChatResponse]

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "LLMChatEndEvent"

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        if self.response is not None and isinstance(self.response.raw, BaseModel):
            self.response.raw = self.response.raw.model_dump()

        return super().model_dump(**kwargs)

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "LLMChatEndEvent"

```
  
---|---  
##  LLMChatStartEvent #
Bases: `BaseEvent`
LLMChatStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`messages` |  `List[ChatMessage]` |  List of chat messages. |  _required_  
`additional_kwargs` |  `dict` |  Additional keyword arguments. |  _required_  
`model_dict` |  `dict` |  Model dictionary. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
class LLMChatStartEvent(BaseEvent):
    """
    LLMChatStartEvent.

    Args:
        messages (List[ChatMessage]): List of chat messages.
        additional_kwargs (dict): Additional keyword arguments.
        model_dict (dict): Model dictionary.

    """

    model_config = ConfigDict(protected_namespaces=("pydantic_model_",))
    messages: List[ChatMessage]
    additional_kwargs: dict
    model_dict: dict

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "LLMChatStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "LLMChatStartEvent"

```
  
---|---  
##  LLMCompletionEndEvent #
Bases: `BaseEvent`
LLMCompletionEndEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  The prompt to be completed. |  _required_  
`response` |  `CompletionResponse` |  Completion response. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
class LLMCompletionEndEvent(BaseEvent):
    """
    LLMCompletionEndEvent.

    Args:
        prompt (str): The prompt to be completed.
        response (CompletionResponse): Completion response.

    """

    prompt: str
    response: CompletionResponse

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "LLMCompletionEndEvent"

    def model_dump(self, **kwargs: Any) -> Dict[str, Any]:
        if isinstance(self.response.raw, BaseModel):
            self.response.raw = self.response.raw.model_dump()

        return super().model_dump(**kwargs)

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "LLMCompletionEndEvent"

```
  
---|---  
##  LLMCompletionStartEvent #
Bases: `BaseEvent`
LLMCompletionStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  The prompt to be completed. |  _required_  
`additional_kwargs` |  `dict` |  Additional keyword arguments. |  _required_  
`model_dict` |  `dict` |  Model dictionary. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
class LLMCompletionStartEvent(BaseEvent):
    """
    LLMCompletionStartEvent.

    Args:
        prompt (str): The prompt to be completed.
        additional_kwargs (dict): Additional keyword arguments.
        model_dict (dict): Model dictionary.

    """

    model_config = ConfigDict(protected_namespaces=("pydantic_model_",))
    prompt: str
    additional_kwargs: dict
    model_dict: dict

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "LLMCompletionStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "LLMCompletionStartEvent"

```
  
---|---  
##  LLMPredictEndEvent #
Bases: `BaseEvent`
LLMPredictEndEvent.
The result of an llm.predict() call.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`output` |  `str` |  Output. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
class LLMPredictEndEvent(BaseEvent):
    """
    LLMPredictEndEvent.

    The result of an llm.predict() call.

    Args:
        output (str): Output.

    """

    output: str

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "LLMPredictEndEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "LLMPredictEndEvent"

```
  
---|---  
##  LLMPredictStartEvent #
Bases: `BaseEvent`
LLMPredictStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`template` |  `BasePromptTemplate` |  Prompt template. |  _required_  
`template_args` |  `Optional[dict]` |  Prompt template arguments. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
class LLMPredictStartEvent(BaseEvent):
    """
    LLMPredictStartEvent.

    Args:
        template (BasePromptTemplate): Prompt template.
        template_args (Optional[dict]): Prompt template arguments.

    """

    template: SerializeAsAny[BasePromptTemplate]
    template_args: Optional[dict]

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "LLMPredictStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/llm.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "LLMPredictStartEvent"

```
  
---|---  
##  QueryEndEvent #
Bases: `BaseEvent`
QueryEndEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `QueryType` |  Query as a string or query bundle. |  _required_  
`response` |  `RESPONSE_TYPE` |  Response. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/query.py`

| ```
class QueryEndEvent(BaseEvent):
    """
    QueryEndEvent.

    Args:
        query (QueryType): Query as a string or query bundle.
        response (RESPONSE_TYPE): Response.

    """

    query: QueryType
    response: RESPONSE_TYPE

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "QueryEndEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/query.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "QueryEndEvent"

```
  
---|---  
##  QueryStartEvent #
Bases: `BaseEvent`
QueryStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `QueryType` |  Query as a string or query bundle. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/query.py`

| ```
class QueryStartEvent(BaseEvent):
    """
    QueryStartEvent.

    Args:
        query (QueryType): Query as a string or query bundle.

    """

    query: QueryType

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "QueryStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/query.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "QueryStartEvent"

```
  
---|---  
##  RetrievalEndEvent #
Bases: `BaseEvent`
RetrievalEndEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`str_or_query_bundle` |  `QueryType` |  Query bundle. |  _required_  
`nodes` |  `List[NodeWithScore]` |  List of nodes with scores. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/retrieval.py`

| ```
class RetrievalEndEvent(BaseEvent):
    """
    RetrievalEndEvent.

    Args:
        str_or_query_bundle (QueryType): Query bundle.
        nodes (List[NodeWithScore]): List of nodes with scores.

    """

    str_or_query_bundle: QueryType
    nodes: List[NodeWithScore]

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "RetrievalEndEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/retrieval.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "RetrievalEndEvent"

```
  
---|---  
##  RetrievalStartEvent #
Bases: `BaseEvent`
RetrievalStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`str_or_query_bundle` |  `QueryType` |  Query bundle. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/retrieval.py`

| ```
class RetrievalStartEvent(BaseEvent):
    """
    RetrievalStartEvent.

    Args:
        str_or_query_bundle (QueryType): Query bundle.

    """

    str_or_query_bundle: QueryType

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "RetrievalStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/retrieval.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "RetrievalStartEvent"

```
  
---|---  
##  GetResponseEndEvent #
Bases: `BaseEvent`
GetResponseEndEvent.
Source code in `llama-index-core/llama_index/core/instrumentation/events/synthesis.py`

| ```
class GetResponseEndEvent(BaseEvent):
    """GetResponseEndEvent."""

    # TODO: consumes the first chunk of generators??
    # response: RESPONSE_TEXT_TYPE

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "GetResponseEndEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/synthesis.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "GetResponseEndEvent"

```
  
---|---  
##  GetResponseStartEvent #
Bases: `BaseEvent`
GetResponseStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_str` |  `str` |  Query string. |  _required_  
`text_chunks` |  `List[str]` |  List of text chunks. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/synthesis.py`

| ```
class GetResponseStartEvent(BaseEvent):
    """
    GetResponseStartEvent.

    Args:
        query_str (str): Query string.
        text_chunks (List[str]): List of text chunks.

    """

    query_str: str
    text_chunks: List[str]

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "GetResponseStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/synthesis.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "GetResponseStartEvent"

```
  
---|---  
##  SynthesizeEndEvent #
Bases: `BaseEvent`
SynthesizeEndEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `QueryType` |  Query as a string or query bundle. |  _required_  
`response` |  `RESPONSE_TYPE` |  Response. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/synthesis.py`

| ```
class SynthesizeEndEvent(BaseEvent):
    """
    SynthesizeEndEvent.

    Args:
        query (QueryType): Query as a string or query bundle.
        response (RESPONSE_TYPE): Response.

    """

    query: QueryType
    response: RESPONSE_TYPE

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "SynthesizeEndEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/synthesis.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "SynthesizeEndEvent"

```
  
---|---  
##  SynthesizeStartEvent #
Bases: `BaseEvent`
SynthesizeStartEvent.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `QueryType` |  Query as a string or query bundle. |  _required_  
Source code in `llama-index-core/llama_index/core/instrumentation/events/synthesis.py`

| ```
class SynthesizeStartEvent(BaseEvent):
    """
    SynthesizeStartEvent.

    Args:
        query (QueryType): Query as a string or query bundle.

    """

    query: QueryType

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "SynthesizeStartEvent"

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama-index-core/llama_index/core/instrumentation/events/synthesis.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "SynthesizeStartEvent"

```
  
---|---
