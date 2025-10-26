#  `message_publishers`#
##  MessageQueuePublisherMixin #
Bases: `ABC`
PublisherMixin.
Mixin for a message queue publisher. Allows for accessing common properties and methods for: - Publisher ID. - Message queue. - Publish callback. - Publish method.
Source code in `llama_deploy/message_publishers/publisher.py`

| ```
class MessageQueuePublisherMixin(ABC):
    """PublisherMixin.

    Mixin for a message queue publisher. Allows for accessing common properties and methods for:
    - Publisher ID.
    - Message queue.
    - Publish callback.
    - Publish method.
    """

    @property
    @abstractmethod
    def publisher_id(self) -> str: ...

    @property
    @abstractmethod
    def message_queue(self) -> AbstractMessageQueue: ...

    @property
    def publish_callback(self) -> Optional[PublishCallback]:
        return None

    @abstractmethod
    def get_topic(self, msg_type: str) -> str: ...

    async def publish(self, message: QueueMessage, **kwargs: Any) -> Any:
        """Publish message."""
        message.publisher_id = self.publisher_id
        return await self.message_queue.publish(
            message,
            callback=self.publish_callback,
            topic=self.get_topic(message.type),
            **kwargs,
        )

```
  
---|---  
###  publish `async` #
```
publish(message: QueueMessage, **kwargs: Any) -> Any

```

Publish message.
Source code in `llama_deploy/message_publishers/publisher.py`

| ```
async def publish(self, message: QueueMessage, **kwargs: Any) -> Any:
    """Publish message."""
    message.publisher_id = self.publisher_id
    return await self.message_queue.publish(
        message,
        callback=self.publish_callback,
        topic=self.get_topic(message.type),
        **kwargs,
    )

```
  
---|---
