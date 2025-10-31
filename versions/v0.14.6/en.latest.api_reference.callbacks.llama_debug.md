# Llama debug
##  LlamaDebugHandler #
Bases: `PythonicallyPrintingBaseHandler`
Callback handler that keeps track of debug info.
NOTE: this is a beta feature. The usage within our codebase, and the interface may change.
This handler simply keeps track of event starts/ends, separated by event types. You can use this callback handler to keep track of and debug events.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`event_starts_to_ignore` |  `Optional[List[CBEventType]]` |  list of event types to ignore when tracking event starts. |  `None`  
`event_ends_to_ignore` |  `Optional[List[CBEventType]]` |  list of event types to ignore when tracking event ends. |  `None`  
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
class LlamaDebugHandler(PythonicallyPrintingBaseHandler):
    """
    Callback handler that keeps track of debug info.

    NOTE: this is a beta feature. The usage within our codebase, and the interface
    may change.

    This handler simply keeps track of event starts/ends, separated by event types.
    You can use this callback handler to keep track of and debug events.

    Args:
        event_starts_to_ignore (Optional[List[CBEventType]]): list of event types to
            ignore when tracking event starts.
        event_ends_to_ignore (Optional[List[CBEventType]]): list of event types to
            ignore when tracking event ends.

    """

    def __init__(
        self,
        event_starts_to_ignore: Optional[List[CBEventType]] = None,
        event_ends_to_ignore: Optional[List[CBEventType]] = None,
        print_trace_on_end: bool = True,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the llama debug handler."""
        self._event_pairs_by_type: Dict[CBEventType, List[CBEvent]] = defaultdict(list)
        self._event_pairs_by_id: Dict[str, List[CBEvent]] = defaultdict(list)
        self._sequential_events: List[CBEvent] = []
        self._cur_trace_id: Optional[str] = None
        self._trace_map: Dict[str, List[str]] = defaultdict(list)
        self.print_trace_on_end = print_trace_on_end
        event_starts_to_ignore = (
            event_starts_to_ignore if event_starts_to_ignore else []
        )
        event_ends_to_ignore = event_ends_to_ignore if event_ends_to_ignore else []
        super().__init__(
            event_starts_to_ignore=event_starts_to_ignore,
            event_ends_to_ignore=event_ends_to_ignore,
            logger=logger,
        )

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        """
        Store event start data by event type.

        Args:
            event_type (CBEventType): event type to store.
            payload (Optional[Dict[str, Any]]): payload to store.
            event_id (str): event id to store.
            parent_id (str): parent event id.

        """
        event = CBEvent(event_type, payload=payload, id_=event_id)
        self._event_pairs_by_type[event.event_type].append(event)
        self._event_pairs_by_id[event.id_].append(event)
        self._sequential_events.append(event)
        return event.id_

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """
        Store event end data by event type.

        Args:
            event_type (CBEventType): event type to store.
            payload (Optional[Dict[str, Any]]): payload to store.
            event_id (str): event id to store.

        """
        event = CBEvent(event_type, payload=payload, id_=event_id)
        self._event_pairs_by_type[event.event_type].append(event)
        self._event_pairs_by_id[event.id_].append(event)
        self._sequential_events.append(event)
        self._trace_map = defaultdict(list)

    def get_events(self, event_type: Optional[CBEventType] = None) -> List[CBEvent]:
        """Get all events for a specific event type."""
        if event_type is not None:
            return self._event_pairs_by_type[event_type]

        return self._sequential_events

    def _get_event_pairs(self, events: List[CBEvent]) -> List[List[CBEvent]]:
        """Helper function to pair events according to their ID."""
        event_pairs: Dict[str, List[CBEvent]] = defaultdict(list)
        for event in events:
            event_pairs[event.id_].append(event)

        return sorted(
            event_pairs.values(),
            key=lambda x: datetime.strptime(x[0].time, TIMESTAMP_FORMAT),
        )

    def _get_time_stats_from_event_pairs(
        self, event_pairs: List[List[CBEvent]]
    ) -> EventStats:
        """Calculate time-based stats for a set of event pairs."""
        total_secs = 0.0
        for event_pair in event_pairs:
            start_time = datetime.strptime(event_pair[0].time, TIMESTAMP_FORMAT)
            end_time = datetime.strptime(event_pair[-1].time, TIMESTAMP_FORMAT)
            total_secs += (end_time - start_time).total_seconds()

        return EventStats(
            total_secs=total_secs,
            average_secs=total_secs / len(event_pairs),
            total_count=len(event_pairs),
        )

    def get_event_pairs(
        self, event_type: Optional[CBEventType] = None
    ) -> List[List[CBEvent]]:
        """Pair events by ID, either all events or a specific type."""
        if event_type is not None:
            return self._get_event_pairs(self._event_pairs_by_type[event_type])

        return self._get_event_pairs(self._sequential_events)

    def get_llm_inputs_outputs(self) -> List[List[CBEvent]]:
        """Get the exact LLM inputs and outputs."""
        return self._get_event_pairs(self._event_pairs_by_type[CBEventType.LLM])

    def get_event_time_info(
        self, event_type: Optional[CBEventType] = None
    ) -> EventStats:
        event_pairs = self.get_event_pairs(event_type)
        return self._get_time_stats_from_event_pairs(event_pairs)

    def flush_event_logs(self) -> None:
        """Clear all events from memory."""
        self._event_pairs_by_type = defaultdict(list)
        self._event_pairs_by_id = defaultdict(list)
        self._sequential_events = []

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        """Launch a trace."""
        self._trace_map = defaultdict(list)
        self._cur_trace_id = trace_id

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        """Shutdown the current trace."""
        self._trace_map = trace_map or defaultdict(list)
        if self.print_trace_on_end:
            self.print_trace_map()

    def _print_trace_map(self, cur_event_id: str, level: int = 0) -> None:
        """Recursively print trace map to terminal for debugging."""
        event_pair = self._event_pairs_by_id[cur_event_id]
        if event_pair:
            time_stats = self._get_time_stats_from_event_pairs([event_pair])
            indent = " " * level * 2
            self._print(
                f"{indent}|_{event_pair[0].event_type} -> {time_stats.total_secs} seconds",
            )

        child_event_ids = self._trace_map[cur_event_id]
        for child_event_id in child_event_ids:
            self._print_trace_map(child_event_id, level=level + 1)

    def print_trace_map(self) -> None:
        """Print simple trace map to terminal for debugging of the most recent trace."""
        self._print("*" * 10)
        self._print(f"Trace: {self._cur_trace_id}")
        self._print_trace_map(BASE_TRACE_EVENT, level=1)
        self._print("*" * 10)

    @property
    def event_pairs_by_type(self) -> Dict[CBEventType, List[CBEvent]]:
        return self._event_pairs_by_type

    @property
    def events_pairs_by_id(self) -> Dict[str, List[CBEvent]]:
        return self._event_pairs_by_id

    @property
    def sequential_events(self) -> List[CBEvent]:
        return self._sequential_events

```
  
---|---  
###  on_event_start #
```
on_event_start(event_type: CBEventType, payload: Optional[Dict[str, Any]] = None, event_id: str = '', parent_id: str = '', **kwargs: Any) -> str

```

Store event start data by event type.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`event_type` |  `CBEventType` |  event type to store. |  _required_  
`payload` |  `Optional[Dict[str, Any]]` |  payload to store. |  `None`  
`event_id` |  `str` |  event id to store. |  `''`  
`parent_id` |  `str` |  parent event id. |  `''`  
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def on_event_start(
    self,
    event_type: CBEventType,
    payload: Optional[Dict[str, Any]] = None,
    event_id: str = "",
    parent_id: str = "",
    **kwargs: Any,
) -> str:
    """
    Store event start data by event type.

    Args:
        event_type (CBEventType): event type to store.
        payload (Optional[Dict[str, Any]]): payload to store.
        event_id (str): event id to store.
        parent_id (str): parent event id.

    """
    event = CBEvent(event_type, payload=payload, id_=event_id)
    self._event_pairs_by_type[event.event_type].append(event)
    self._event_pairs_by_id[event.id_].append(event)
    self._sequential_events.append(event)
    return event.id_

```
  
---|---  
###  on_event_end #
```
on_event_end(event_type: CBEventType, payload: Optional[Dict[str, Any]] = None, event_id: str = '', **kwargs: Any) -> None

```

Store event end data by event type.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`event_type` |  `CBEventType` |  event type to store. |  _required_  
`payload` |  `Optional[Dict[str, Any]]` |  payload to store. |  `None`  
`event_id` |  `str` |  event id to store. |  `''`  
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def on_event_end(
    self,
    event_type: CBEventType,
    payload: Optional[Dict[str, Any]] = None,
    event_id: str = "",
    **kwargs: Any,
) -> None:
    """
    Store event end data by event type.

    Args:
        event_type (CBEventType): event type to store.
        payload (Optional[Dict[str, Any]]): payload to store.
        event_id (str): event id to store.

    """
    event = CBEvent(event_type, payload=payload, id_=event_id)
    self._event_pairs_by_type[event.event_type].append(event)
    self._event_pairs_by_id[event.id_].append(event)
    self._sequential_events.append(event)
    self._trace_map = defaultdict(list)

```
  
---|---  
###  get_events #
```
get_events(event_type: Optional[CBEventType] = None) -> List[CBEvent]

```

Get all events for a specific event type.
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def get_events(self, event_type: Optional[CBEventType] = None) -> List[CBEvent]:
    """Get all events for a specific event type."""
    if event_type is not None:
        return self._event_pairs_by_type[event_type]

    return self._sequential_events

```
  
---|---  
###  get_event_pairs #
```
get_event_pairs(event_type: Optional[CBEventType] = None) -> List[List[CBEvent]]

```

Pair events by ID, either all events or a specific type.
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def get_event_pairs(
    self, event_type: Optional[CBEventType] = None
) -> List[List[CBEvent]]:
    """Pair events by ID, either all events or a specific type."""
    if event_type is not None:
        return self._get_event_pairs(self._event_pairs_by_type[event_type])

    return self._get_event_pairs(self._sequential_events)

```
  
---|---  
###  get_llm_inputs_outputs #
```
get_llm_inputs_outputs() -> List[List[CBEvent]]

```

Get the exact LLM inputs and outputs.
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def get_llm_inputs_outputs(self) -> List[List[CBEvent]]:
    """Get the exact LLM inputs and outputs."""
    return self._get_event_pairs(self._event_pairs_by_type[CBEventType.LLM])

```
  
---|---  
###  flush_event_logs #
```
flush_event_logs() -> None

```

Clear all events from memory.
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def flush_event_logs(self) -> None:
    """Clear all events from memory."""
    self._event_pairs_by_type = defaultdict(list)
    self._event_pairs_by_id = defaultdict(list)
    self._sequential_events = []

```
  
---|---  
###  start_trace #
```
start_trace(trace_id: Optional[str] = None) -> None

```

Launch a trace.
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def start_trace(self, trace_id: Optional[str] = None) -> None:
    """Launch a trace."""
    self._trace_map = defaultdict(list)
    self._cur_trace_id = trace_id

```
  
---|---  
###  end_trace #
```
end_trace(trace_id: Optional[str] = None, trace_map: Optional[Dict[str, List[str]]] = None) -> None

```

Shutdown the current trace.
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def end_trace(
    self,
    trace_id: Optional[str] = None,
    trace_map: Optional[Dict[str, List[str]]] = None,
) -> None:
    """Shutdown the current trace."""
    self._trace_map = trace_map or defaultdict(list)
    if self.print_trace_on_end:
        self.print_trace_map()

```
  
---|---  
###  print_trace_map #
```
print_trace_map() -> None

```

Print simple trace map to terminal for debugging of the most recent trace.
Source code in `llama-index-core/llama_index/core/callbacks/llama_debug.py`

| ```
def print_trace_map(self) -> None:
    """Print simple trace map to terminal for debugging of the most recent trace."""
    self._print("*" * 10)
    self._print(f"Trace: {self._cur_trace_id}")
    self._print_trace_map(BASE_TRACE_EVENT, level=1)
    self._print("*" * 10)

```
  
---|---
