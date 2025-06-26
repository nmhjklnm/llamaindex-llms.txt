# message_queues#
Message queue module.
##  AbstractMessageQueue #
Bases: `ABC`
Message broker interface between publisher and consumer.
Source code in `llama_deploy/message_queues/base.py`

| ```
class AbstractMessageQueue(ABC):
    """Message broker interface between publisher and consumer."""

    @abstractmethod
    async def _publish(self, message: QueueMessage, topic: str) -> Any:
        """Subclasses implement publish logic here."""

    async def publish(
        self,
        message: QueueMessage,
        topic: str,
        callback: PublishCallback | None = None,
        **kwargs: Any,
    ) -> Any:
        """Send message to a consumer."""
        logger.info(
            f"Publishing message of type '{message.type}' with action '{message.action}' to topic '{topic}'"
        )
        logger.debug(f"Message: {message.model_dump()}")

        message.stats.publish_time = message.stats.timestamp_str()
        await self._publish(message, topic)

        if callback:
            if inspect.iscoroutinefunction(callback):
                await callback(message, **kwargs)
            else:
                callback(message, **kwargs)

    @abstractmethod
    async def register_consumer(
        self, consumer: BaseMessageQueueConsumer, topic: str
    ) -> StartConsumingCallable:
        """Register consumer to start consuming messages."""

    @abstractmethod
    async def deregister_consumer(self, consumer: BaseMessageQueueConsumer) -> Any:
        """Deregister consumer to stop publishing messages)."""

    async def get_consumers(
        self, message_type: str
    ) -> Sequence[BaseMessageQueueConsumer]:
        """Gets list of consumers according to a message type."""
        raise NotImplementedError(
            "`get_consumers()` is not implemented for this class."
        )

    @abstractmethod
    async def cleanup(self, *args: Any, **kwargs: dict[str, Any]) -> None:
        """Perform any cleanup before shutting down."""

    @abstractmethod
    def as_config(self) -> BaseModel:
        """Returns the config dict to reconstruct the message queue."""

```
  
---|---  
###  publish `async` #
```
publish(message: QueueMessage, topic: str, callback: PublishCallback | None = None, **kwargs: Any) -> Any

```

Send message to a consumer.
Source code in `llama_deploy/message_queues/base.py`

| ```
async def publish(
    self,
    message: QueueMessage,
    topic: str,
    callback: PublishCallback | None = None,
    **kwargs: Any,
) -> Any:
    """Send message to a consumer."""
    logger.info(
        f"Publishing message of type '{message.type}' with action '{message.action}' to topic '{topic}'"
    )
    logger.debug(f"Message: {message.model_dump()}")

    message.stats.publish_time = message.stats.timestamp_str()
    await self._publish(message, topic)

    if callback:
        if inspect.iscoroutinefunction(callback):
            await callback(message, **kwargs)
        else:
            callback(message, **kwargs)

```
  
---|---  
###  register_consumer `abstractmethod` `async` #
```
register_consumer(consumer: BaseMessageQueueConsumer, topic: str) -> StartConsumingCallable

```

Register consumer to start consuming messages.
Source code in `llama_deploy/message_queues/base.py`

| ```
@abstractmethod
async def register_consumer(
    self, consumer: BaseMessageQueueConsumer, topic: str
) -> StartConsumingCallable:
    """Register consumer to start consuming messages."""

```
  
---|---  
###  deregister_consumer `abstractmethod` `async` #
```
deregister_consumer(consumer: BaseMessageQueueConsumer) -> Any

```

Deregister consumer to stop publishing messages).
Source code in `llama_deploy/message_queues/base.py`

| ```
@abstractmethod
async def deregister_consumer(self, consumer: BaseMessageQueueConsumer) -> Any:
    """Deregister consumer to stop publishing messages)."""

```
  
---|---  
###  get_consumers `async` #
```
get_consumers(message_type: str) -> Sequence[BaseMessageQueueConsumer]

```

Gets list of consumers according to a message type.
Source code in `llama_deploy/message_queues/base.py`

| ```
async def get_consumers(
    self, message_type: str
) -> Sequence[BaseMessageQueueConsumer]:
    """Gets list of consumers according to a message type."""
    raise NotImplementedError(
        "`get_consumers()` is not implemented for this class."
    )

```
  
---|---  
###  cleanup `abstractmethod` `async` #
```
cleanup(*args: Any, **kwargs: dict[str, Any]) -> None

```

Perform any cleanup before shutting down.
Source code in `llama_deploy/message_queues/base.py`

| ```
@abstractmethod
async def cleanup(self, *args: Any, **kwargs: dict[str, Any]) -> None:
    """Perform any cleanup before shutting down."""

```
  
---|---  
###  as_config `abstractmethod` #
```
as_config() -> BaseModel

```

Returns the config dict to reconstruct the message queue.
Source code in `llama_deploy/message_queues/base.py`

| ```
@abstractmethod
def as_config(self) -> BaseModel:
    """Returns the config dict to reconstruct the message queue."""

```
  
---|---
