#  `types`#
##  DeploymentDefinition #
Bases: `BaseModel`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`name` |  `str` |  |  _required_  
Source code in `llama_deploy/types/apiserver.py`

| ```
class DeploymentDefinition(BaseModel):
    name: str

```
  
---|---  
##  Status #
Bases: `BaseModel`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`status` |  `StatusEnum` |  |  _required_  
`status_message` |  `str` |  |  _required_  
`max_deployments` |  `int | None` |  |  `None`  
`deployments` |  `list[str] | None` |  |  `None`  
Source code in `llama_deploy/types/apiserver.py`

| ```
class Status(BaseModel):
    status: StatusEnum
    status_message: str
    max_deployments: int | None = None
    deployments: list[str] | None = None

```
  
---|---  
##  ActionTypes #
Bases: `str`, `Enum`
Action types for messages. Different consumers will handle (or ignore) different action types.
Source code in `llama_deploy/types/core.py`

| ```
class ActionTypes(str, Enum):
    """
    Action types for messages.
    Different consumers will handle (or ignore) different action types.
    """

    NEW_TASK = "new_task"
    COMPLETED_TASK = "completed_task"
    REQUEST_FOR_HELP = "request_for_help"
    NEW_TOOL_CALL = "new_tool_call"
    COMPLETED_TOOL_CALL = "completed_tool_call"
    TASK_STREAM = "task_stream"
    SEND_EVENT = "send_event"

```
  
---|---  
##  ChatMessage #
Bases: `BaseModel`
Chat message.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`role` |  `MessageRole` |  |  `<MessageRole.USER: 'user'>`  
`blocks` |  `list[Annotated[Union[TextBlock, ImageBlock, AudioBlock, DocumentBlock], FieldInfo]]` |  Built-in mutable sequence. If no argument is given, the constructor creates a new empty list. The argument must be an iterable if specified. |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class ChatMessage(BaseModel):
    """Chat message."""

    role: MessageRole = MessageRole.USER
    additional_kwargs: dict[str, Any] = Field(default_factory=dict)
    blocks: list[ContentBlock] = Field(default_factory=list)

    def __init__(self, /, content: Any | None = None, **data: Any) -> None:
        """
        Keeps backward compatibility with the old `content` field.

        If content was passed and contained text, store a single TextBlock.
        If content was passed and it was a list, assume it's a list of content blocks and store it.
        """
        if content is not None:
            if isinstance(content, str):
                data["blocks"] = [TextBlock(text=content)]
            elif isinstance(content, list):
                data["blocks"] = content

        super().__init__(**data)

    @model_validator(mode="after")
    def legacy_additional_kwargs_image(self) -> Self:
        """
        Provided for backward compatibility.

        If `additional_kwargs` contains an `images` key, assume the value is a list
        of ImageDocument and convert them into image blocks.
        """
        if documents := self.additional_kwargs.get("images"):
            documents = cast(list[ImageDocument], documents)
            for doc in documents:
                img_base64_bytes = doc.resolve_image(as_base64=True).read()
                self.blocks.append(ImageBlock(image=img_base64_bytes))
        return self

    @property
    def content(self) -> str | None:
        """
        Keeps backward compatibility with the old `content` field.

        Returns:
            The cumulative content of the TextBlock blocks, None if there are none.

        """
        content_strs = []
        for block in self.blocks:
            if isinstance(block, TextBlock):
                content_strs.append(block.text)

        ct = "\n".join(content_strs) or None
        if ct is None and len(content_strs) == 1:
            return ""
        return ct

    @content.setter
    def content(self, content: str) -> None:
        """
        Keeps backward compatibility with the old `content` field.

        Raises:
            ValueError: if blocks contains more than a block, or a block that's not TextBlock.

        """
        if not self.blocks:
            self.blocks = [TextBlock(text=content)]
        elif len(self.blocks) == 1 and isinstance(self.blocks[0], TextBlock):
            self.blocks = [TextBlock(text=content)]
        else:
            raise ValueError(
                "ChatMessage contains multiple blocks, use 'ChatMessage.blocks' instead."
            )

    def __str__(self) -> str:
        return f"{self.role.value}: {self.content}"

    @classmethod
    def from_str(
        cls,
        content: str,
        role: Union[MessageRole, str] = MessageRole.USER,
        **kwargs: Any,
    ) -> Self:
        if isinstance(role, str):
            role = MessageRole(role)
        return cls(role=role, blocks=[TextBlock(text=content)], **kwargs)

    def _recursive_serialization(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            value.model_rebuild()  # ensures all fields are initialized and serializable
            return value.model_dump()  # type: ignore
        if isinstance(value, dict):
            return {
                key: self._recursive_serialization(value)
                for key, value in value.items()
            }
        if isinstance(value, list):
            return [self._recursive_serialization(item) for item in value]
        return value

    @field_serializer("additional_kwargs", check_fields=False)
    def serialize_additional_kwargs(self, value: Any, _info: Any) -> Any:
        return self._recursive_serialization(value)

```
  
---|---  
###  content `property` `writable` #
```
content: str | None

```

Keeps backward compatibility with the old `content` field.
Returns:
Type | Description  
---|---  
`str | None` |  The cumulative content of the TextBlock blocks, None if there are none.  
###  legacy_additional_kwargs_image #
```
legacy_additional_kwargs_image() -> Self

```

Provided for backward compatibility.
If `additional_kwargs` contains an `images` key, assume the value is a list of ImageDocument and convert them into image blocks.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
@model_validator(mode="after")
def legacy_additional_kwargs_image(self) -> Self:
    """
    Provided for backward compatibility.

    If `additional_kwargs` contains an `images` key, assume the value is a list
    of ImageDocument and convert them into image blocks.
    """
    if documents := self.additional_kwargs.get("images"):
        documents = cast(list[ImageDocument], documents)
        for doc in documents:
            img_base64_bytes = doc.resolve_image(as_base64=True).read()
            self.blocks.append(ImageBlock(image=img_base64_bytes))
    return self

```
  
---|---  
##  EventDefinition #
Bases: `BaseModel`
The definition of event.
To be used as payloads for service endpoints when wanting to send serialized Events.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`agent_id` |  `str` |  |  _required_  
`event_obj_str` |  `str` |  |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`event_object_str` |  `str` |  serialized string of event.  
Source code in `llama_deploy/types/core.py`

| ```
class EventDefinition(BaseModel):
    """The definition of event.

    To be used as payloads for service endpoints when wanting to send serialized
    Events.

    Attributes:
        event_object_str (str): serialized string of event.
    """

    agent_id: str
    event_obj_str: str

```
  
---|---  
##  HumanResponse #
Bases: `BaseModel`
A simple human response.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`result` |  `str` |  |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`response` |  `str` |  The human response.  
Source code in `llama_deploy/types/core.py`

| ```
class HumanResponse(BaseModel):
    """
    A simple human response.

    Attributes:
        response (str):
            The human response.
    """

    result: str

```
  
---|---  
##  ServiceDefinition #
Bases: `BaseModel`
The definition of a service, bundles useful information describing the service.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`service_name` |  `str` |  The name of the service. |  _required_  
`description` |  `str` |  A description of the service and it's purpose. |  _required_  
`prompt` |  `list[ChatMessage]` |  Specific instructions for the service. |  `<dynamic>`  
`host` |  `str | None` |  |  `None`  
`port` |  `int | None` |  |  `None`  
Attributes:
Name | Type | Description  
---|---|---  
`service_name` |  `str` |  The name of the service.  
`description` |  `str` |  A description of the service and it's purpose.  
`prompt` |  `list[ChatMessage]` |  Specific instructions for the service.  
`host` |  `str | None` |  The host of the service, if its a network service.  
`port` |  `int | None` |  The port of the service, if its a network service.  
Source code in `llama_deploy/types/core.py`

| ```
class ServiceDefinition(BaseModel):
    """
    The definition of a service, bundles useful information describing the service.

    Attributes:
        service_name (str):
            The name of the service.
        description (str):
            A description of the service and it's purpose.
        prompt (list[ChatMessage]):
            Specific instructions for the service.
        host (str | None):
            The host of the service, if its a network service.
        port (int | None):
            The port of the service, if its a network service.
    """

    service_name: str = Field(description="The name of the service.")
    description: str = Field(
        description="A description of the service and it's purpose."
    )
    prompt: list[ChatMessage] = Field(
        default_factory=list, description="Specific instructions for the service."
    )
    host: str | None = None
    port: int | None = None

```
  
---|---  
##  SessionDefinition #
Bases: `BaseModel`
The definition of a session.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`session_id` |  `str` |  |  `'0d1b5112-6687-43e3-bd33-b663ae0fff27'`  
`task_ids` |  `list[str]` |  Built-in mutable sequence. If no argument is given, the constructor creates a new empty list. The argument must be an iterable if specified. |  `<dynamic>`  
Attributes:
Name | Type | Description  
---|---|---  
`session_id` |  `str` |  The session ID. Defaults to a random UUID.  
`task_definitions` |  `list[str]` |  The task ids in order, representing the session.  
`state` |  `dict` |  The current session state.  
Source code in `llama_deploy/types/core.py`

| ```
class SessionDefinition(BaseModel):
    """
    The definition of a session.

    Attributes:
        session_id (str):
            The session ID. Defaults to a random UUID.
        task_definitions (list[str]):
            The task ids in order, representing the session.
        state (dict):
            The current session state.
    """

    session_id: str = Field(default_factory=generate_id)
    task_ids: list[str] = Field(default_factory=list)
    state: dict = Field(default_factory=dict)

    @property
    def current_task_id(self) -> str | None:
        if len(self.task_ids) == 0:
            return None

        return self.task_ids[-1]

```
  
---|---  
##  TaskDefinition #
Bases: `BaseModel`
The definition and state of a task.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`input` |  `str` |  |  _required_  
`task_id` |  `str` |  |  `'16bae25f-845c-44eb-a1a4-3921902eb745'`  
`session_id` |  `str | None` |  |  `None`  
`agent_id` |  `str | None` |  |  `None`  
Attributes:
Name | Type | Description  
---|---|---  
`input` |  `str` |  The task input.  
`session_id` |  `str` |  The session ID that the task belongs to.  
`task_id` |  `str` |  The task ID. Defaults to a random UUID.  
`agent_id` |  `str` |  The agent ID that the task should be sent to. If blank, the orchestrator decides.  
Source code in `llama_deploy/types/core.py`

| ```
class TaskDefinition(BaseModel):
    """
    The definition and state of a task.

    Attributes:
        input (str):
            The task input.
        session_id (str):
            The session ID that the task belongs to.
        task_id (str):
            The task ID. Defaults to a random UUID.
        agent_id (str):
            The agent ID that the task should be sent to.
            If blank, the orchestrator decides.
    """

    input: str
    task_id: str = Field(default_factory=generate_id)
    session_id: str | None = None
    agent_id: str | None = None

```
  
---|---  
##  TaskResult #
Bases: `BaseModel`
The result of a task.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  |  _required_  
`history` |  `list[ChatMessage]` |  |  _required_  
`result` |  `str` |  |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`task_id` |  `str` |  The task ID.  
`history` |  `list[ChatMessage]` |  The task history.  
`result` |  `str` |  The task result.  
`data` |  `dict` |  Additional data about the task or result.  
`is_last` |  `bool` |  If not true, there are more results to be streamed.  
`index` |  `int` |  The index of the task in the session.  
Source code in `llama_deploy/types/core.py`

| ```
class TaskResult(BaseModel):
    """
    The result of a task.

    Attributes:
        task_id (str):
            The task ID.
        history (list[ChatMessage]):
            The task history.
        result (str):
            The task result.
        data (dict):
            Additional data about the task or result.
        is_last (bool):
            If not true, there are more results to be streamed.
        index (int):
            The index of the task in the session.
    """

    task_id: str
    history: list[ChatMessage]
    result: str
    data: dict = Field(default_factory=dict)

```
  
---|---  
##  TaskStream #
Bases: `BaseModel`
A stream of data generated by a task.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  |  _required_  
`session_id` |  `str | None` |  |  _required_  
`data` |  `dict` |  |  _required_  
`index` |  `int` |  |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`task_id` |  `str` |  The associated task ID.  
`data` |  `list[dict]` |  The stream data.  
`index` |  `int` |  The index of the stream data.  
Source code in `llama_deploy/types/core.py`

| ```
class TaskStream(BaseModel):
    """
    A stream of data generated by a task.

    Attributes:
        task_id (str):
            The associated task ID.
        data (list[dict]):
            The stream data.
        index (int):
            The index of the stream data.
    """

    task_id: str
    session_id: str | None
    data: dict
    index: int

```
  
---|---  
##  ToolCall #
Bases: `BaseModel`
A tool call.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`id_` |  `str` |  |  `'91fe55c7-4a26-4bb5-a0e1-dccb884745e6'`  
`tool_call_bundle` |  `ToolCallBundle` |  |  _required_  
`source_id` |  `str` |  |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`id_` |  `str` |  The tool call ID. Defaults to a random UUID.  
`tool_call_bundle` |  `ToolCallBundle` |  The tool call bundle.  
`source_id` |  `str` |  The source ID.  
Source code in `llama_deploy/types/core.py`

| ```
class ToolCall(BaseModel):
    """
    A tool call.

    Attributes:
        id_ (str):
            The tool call ID. Defaults to a random UUID.
        tool_call_bundle (ToolCallBundle):
            The tool call bundle.
        source_id (str):
            The source ID.
    """

    id_: str = Field(default_factory=generate_id)
    tool_call_bundle: ToolCallBundle
    source_id: str

```
  
---|---  
##  ToolCallBundle #
Bases: `BaseModel`
A bundle of information for a tool call.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`tool_name` |  `str` |  |  _required_  
`tool_args` |  `list[Any]` |  |  _required_  
`tool_kwargs` |  `dict[str, Any]` |  |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`tool_name` |  `str` |  The name of the tool.  
`tool_args` |  `list[Any]` |  The tool arguments.  
`tool_kwargs` |  `dict[str, Any]` |  The tool keyword arguments  
Source code in `llama_deploy/types/core.py`

| ```
class ToolCallBundle(BaseModel):
    """
    A bundle of information for a tool call.

    Attributes:
        tool_name (str):
            The name of the tool.
        tool_args (list[Any]):
            The tool arguments.
        tool_kwargs (dict[str, Any]):
            The tool keyword arguments
    """

    tool_name: str
    tool_args: list[Any]
    tool_kwargs: dict[str, Any]

```
  
---|---  
##  ToolCallResult #
Bases: `BaseModel`
A tool call result.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`id_` |  `str` |  |  _required_  
`tool_message` |  `ChatMessage` |  |  _required_  
`result` |  `str` |  |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`id_` |  `str` |  The tool call ID. Should match the ID of the tool call.  
`tool_message` |  `ChatMessage` |  The tool message.  
`result` |  `str` |  The tool result.  
Source code in `llama_deploy/types/core.py`

| ```
class ToolCallResult(BaseModel):
    """
    A tool call result.

    Attributes:
        id_ (str):
            The tool call ID. Should match the ID of the tool call.
        tool_message (ChatMessage):
            The tool message.
        result (str):
            The tool result.
    """

    id_: str
    tool_message: ChatMessage
    result: str

```
  
---|---
