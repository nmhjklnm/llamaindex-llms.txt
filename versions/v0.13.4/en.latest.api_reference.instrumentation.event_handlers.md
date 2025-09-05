# Event handlers
##  BaseEventHandler #
Bases: `BaseModel`
Base callback handler that can be used to track event starts and ends.
Source code in `llama_index_instrumentation/event_handlers/base.py`

| ```
class BaseEventHandler(BaseModel):
    """Base callback handler that can be used to track event starts and ends."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "BaseEventHandler"

    @abstractmethod
    def handle(self, event: BaseEvent, **kwargs: Any) -> Any:
        """Logic for handling event."""

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama_index_instrumentation/event_handlers/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "BaseEventHandler"

```
  
---|---  
###  handle `abstractmethod` #
```
handle(event: BaseEvent, **kwargs: Any) -> Any

```

Logic for handling event.
Source code in `llama_index_instrumentation/event_handlers/base.py`

| ```
@abstractmethod
def handle(self, event: BaseEvent, **kwargs: Any) -> Any:
    """Logic for handling event."""

```
  
---|---
