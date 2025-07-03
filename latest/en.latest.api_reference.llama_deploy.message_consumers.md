#  `message_consumers`#
##  BaseMessageQueueConsumer #
Bases: `BaseModel`, `ABC`
Consumer of a MessageQueue.
Process messages from a MessageQueue for a specific message type.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`id_` |  `str` |  |  `'0d8a762f-8a8c-4759-8aa3-659ccb17dfe0'`  
`message_type` |  `str` |  Type of the message to consume. |  `'default'`  
`channel` |  `Any` |  The channel if any for which to receive messages. |  `None`  
`consuming_callable` |  `Callable[..., Coroutine[Any, Any, None]]` |  |  `<function default_start_consuming_callable at 0x756fecc61580>`  
Source code in `llama_deploy/message_consumers/base.py`

| ```
class BaseMessageQueueConsumer(BaseModel, ABC):
    """Consumer of a MessageQueue.

    Process messages from a MessageQueue for a specific message type.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id_: str = Field(default_factory=generate_id)
    message_type: str = Field(
        default="default", description="Type of the message to consume."
    )
    channel: Any = Field(
        default=None, description="The channel if any for which to receive messages."
    )
    consuming_callable: StartConsumingCallable = Field(
        default=default_start_consuming_callable
    )

    @abstractmethod
    async def _process_message(self, message: QueueMessage, **kwargs: Any) -> Any:
        """Subclasses should implement logic here."""

    async def process_message(self, message: QueueMessage, **kwargs: Any) -> Any:
        """Logic for processing message."""
        if message.type != self.message_type:
            msg = f"Consumer cannot process messages of type '{message.type}'."
            raise ValueError(msg)
        return await self._process_message(message, **kwargs)

    async def start_consuming(
        self,
    ) -> None:
        """Begin consuming messages."""
        await self.consuming_callable()

```
  
---|---  
###  process_message `async` #
```
process_message(message: QueueMessage, **kwargs: Any) -> Any

```

Logic for processing message.
Source code in `llama_deploy/message_consumers/base.py`

| ```
async def process_message(self, message: QueueMessage, **kwargs: Any) -> Any:
    """Logic for processing message."""
    if message.type != self.message_type:
        msg = f"Consumer cannot process messages of type '{message.type}'."
        raise ValueError(msg)
    return await self._process_message(message, **kwargs)

```
  
---|---  
###  start_consuming `async` #
```
start_consuming() -> None

```

Begin consuming messages.
Source code in `llama_deploy/message_consumers/base.py`

| ```
async def start_consuming(
    self,
) -> None:
    """Begin consuming messages."""
    await self.consuming_callable()

```
  
---|---  
##  CallableMessageConsumer #
Bases: `BaseMessageQueueConsumer`
Message consumer for a callable handler.
For a given message, it will call the handler with the message as input.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`handler` |  `Callable` |  |  _required_  
Source code in `llama_deploy/message_consumers/callable.py`

| ```
class CallableMessageConsumer(BaseMessageQueueConsumer):
    """Message consumer for a callable handler.

    For a given message, it will call the handler with the message as input.
    """

    handler: Callable

    async def _process_message(self, message: QueueMessage, **kwargs: Any) -> None:
        if asyncio.iscoroutinefunction(self.handler):
            await self.handler(message, **kwargs)
        else:
            self.handler(message, **kwargs)

```
  
---|---
