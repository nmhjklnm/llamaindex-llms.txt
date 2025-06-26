#  `messages`#
##  QueueMessage #
Bases: `BaseModel`
A message for the message queue.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`id_` |  `str` |  |  `'4eb07e7a-27d2-48af-9e97-66b66ef82c60'`  
`publisher_id` |  `str` |  Id of publisher. |  `'default'`  
`action` |  `ActionTypes | None` |  |  `None`  
`stats` |  `QueueMessageStats` |  Stats for a queue message. Attributes: publish_time (Optional[str]): The time the message was published. process_start_time (Optional[str]): The time the message processing started. process_end_time (Optional[str]): The time the message processing ended. |  `<dynamic>`  
`type` |  `str` |  Type of the message, used for routing. |  `'default'`  
Attributes:
Name | Type | Description  
---|---|---  
`id_` |  `str` |  The id of the message.  
`publisher_id` |  `str` |  The id of the publisher.  
`data` |  `Dict[str, Any]` |  The data of the message.  
`action` |  `Optional[ActionTypes]` |  The action of the message, used for deciding how to process the message.  
`stats` |  `QueueMessageStats` |  The stats of the message.  
`type` |  `str` |  The type of the message. Typically this is a service name.  
Source code in `llama_deploy/messages/base.py`

| ```
class QueueMessage(BaseModel):
    """A message for the message queue.

    Attributes:
        id_ (str):
            The id of the message.
        publisher_id (str):
            The id of the publisher.
        data (Dict[str, Any]):
            The data of the message.
        action (Optional[ActionTypes]):
            The action of the message, used for deciding how to process the message.
        stats (QueueMessageStats):
            The stats of the message.
        type (str):
            The type of the message. Typically this is a service name.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    id_: str = Field(default_factory=lambda: str(uuid.uuid4()))
    publisher_id: str = Field(default="default", description="Id of publisher.")
    data: Dict[str, Any] = Field(default_factory=dict)
    action: Optional[ActionTypes] = None
    stats: QueueMessageStats = Field(default_factory=QueueMessageStats)
    type: str = Field(
        default="default", description="Type of the message, used for routing."
    )

```
  
---|---
