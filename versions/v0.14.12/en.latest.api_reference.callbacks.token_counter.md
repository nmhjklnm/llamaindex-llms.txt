# Token counter
##  TokenCountingHandler #
Bases: `PythonicallyPrintingBaseHandler`
Callback handler for counting tokens in LLM and Embedding events.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`tokenizer` |  `Optional[Callable[[str], List]]` |  Tokenizer to use. Defaults to the global tokenizer (see llama_index.core.utils.globals_helper). |  `None`  
`event_starts_to_ignore` |  `Optional[List[CBEventType]]` |  List of event types to ignore at the start of a trace. |  `None`  
`event_ends_to_ignore` |  `Optional[List[CBEventType]]` |  List of event types to ignore at the end of a trace. |  `None`  
Source code in `llama-index-core/llama_index/core/callbacks/token_counting.py`

| ```
class TokenCountingHandler(PythonicallyPrintingBaseHandler):
    """
    Callback handler for counting tokens in LLM and Embedding events.

    Args:
        tokenizer:
            Tokenizer to use. Defaults to the global tokenizer
            (see llama_index.core.utils.globals_helper).
        event_starts_to_ignore: List of event types to ignore at the start of a trace.
        event_ends_to_ignore: List of event types to ignore at the end of a trace.

    """

    def __init__(
        self,
        tokenizer: Optional[Callable[[str], List]] = None,
        event_starts_to_ignore: Optional[List[CBEventType]] = None,
        event_ends_to_ignore: Optional[List[CBEventType]] = None,
        verbose: bool = False,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.llm_token_counts: List[TokenCountingEvent] = []
        self.embedding_token_counts: List[TokenCountingEvent] = []
        self.tokenizer = tokenizer or get_tokenizer()

        self._token_counter = TokenCounter(tokenizer=self.tokenizer)
        self._verbose = verbose

        super().__init__(
            event_starts_to_ignore=event_starts_to_ignore or [],
            event_ends_to_ignore=event_ends_to_ignore or [],
            logger=logger,
        )

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        return

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        return

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        return event_id

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[Dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Count the LLM or Embedding tokens as needed."""
        if (
            event_type == CBEventType.LLM
            and event_type not in self.event_ends_to_ignore
            and payload is not None
        ):
            self.llm_token_counts.append(
                get_llm_token_counts(
                    token_counter=self._token_counter,
                    payload=payload,
                    event_id=event_id,
                )
            )

            if self._verbose:
                self._print(
                    "LLM Prompt Token Usage: "
                    f"{self.llm_token_counts[-1].prompt_token_count}\n"
                    "LLM Completion Token Usage: "
                    f"{self.llm_token_counts[-1].completion_token_count}",
                )
        elif (
            event_type == CBEventType.EMBEDDING
            and event_type not in self.event_ends_to_ignore
            and payload is not None
        ):
            total_chunk_tokens = 0
            for chunk in payload.get(EventPayload.CHUNKS, []):
                self.embedding_token_counts.append(
                    TokenCountingEvent(
                        event_id=event_id,
                        prompt=chunk,
                        prompt_token_count=self._token_counter.get_string_tokens(chunk),
                        completion="",
                        completion_token_count=0,
                    )
                )
                total_chunk_tokens += self.embedding_token_counts[-1].total_token_count

            if self._verbose:
                self._print(f"Embedding Token Usage: {total_chunk_tokens}")

    @property
    def total_llm_token_count(self) -> int:
        """Get the current total LLM token count."""
        return sum([x.total_token_count for x in self.llm_token_counts])

    @property
    def prompt_llm_token_count(self) -> int:
        """Get the current total LLM prompt token count."""
        return sum([x.prompt_token_count for x in self.llm_token_counts])

    @property
    def completion_llm_token_count(self) -> int:
        """Get the current total LLM completion token count."""
        return sum([x.completion_token_count for x in self.llm_token_counts])

    @property
    def total_embedding_token_count(self) -> int:
        """Get the current total Embedding token count."""
        return sum([x.total_token_count for x in self.embedding_token_counts])

    def reset_counts(self) -> None:
        """Reset the token counts."""
        self.llm_token_counts = []
        self.embedding_token_counts = []

```
  
---|---  
###  total_llm_token_count `property` #
```
total_llm_token_count: int

```

Get the current total LLM token count.
###  prompt_llm_token_count `property` #
```
prompt_llm_token_count: int

```

Get the current total LLM prompt token count.
###  completion_llm_token_count `property` #
```
completion_llm_token_count: int

```

Get the current total LLM completion token count.
###  total_embedding_token_count `property` #
```
total_embedding_token_count: int

```

Get the current total Embedding token count.
###  on_event_end #
```
on_event_end(event_type: CBEventType, payload: Optional[Dict[str, Any]] = None, event_id: str = '', **kwargs: Any) -> None

```

Count the LLM or Embedding tokens as needed.
Source code in `llama-index-core/llama_index/core/callbacks/token_counting.py`

| ```
def on_event_end(
    self,
    event_type: CBEventType,
    payload: Optional[Dict[str, Any]] = None,
    event_id: str = "",
    **kwargs: Any,
) -> None:
    """Count the LLM or Embedding tokens as needed."""
    if (
        event_type == CBEventType.LLM
        and event_type not in self.event_ends_to_ignore
        and payload is not None
    ):
        self.llm_token_counts.append(
            get_llm_token_counts(
                token_counter=self._token_counter,
                payload=payload,
                event_id=event_id,
            )
        )

        if self._verbose:
            self._print(
                "LLM Prompt Token Usage: "
                f"{self.llm_token_counts[-1].prompt_token_count}\n"
                "LLM Completion Token Usage: "
                f"{self.llm_token_counts[-1].completion_token_count}",
            )
    elif (
        event_type == CBEventType.EMBEDDING
        and event_type not in self.event_ends_to_ignore
        and payload is not None
    ):
        total_chunk_tokens = 0
        for chunk in payload.get(EventPayload.CHUNKS, []):
            self.embedding_token_counts.append(
                TokenCountingEvent(
                    event_id=event_id,
                    prompt=chunk,
                    prompt_token_count=self._token_counter.get_string_tokens(chunk),
                    completion="",
                    completion_token_count=0,
                )
            )
            total_chunk_tokens += self.embedding_token_counts[-1].total_token_count

        if self._verbose:
            self._print(f"Embedding Token Usage: {total_chunk_tokens}")

```
  
---|---  
###  reset_counts #
```
reset_counts() -> None

```

Reset the token counts.
Source code in `llama-index-core/llama_index/core/callbacks/token_counting.py`

| ```
def reset_counts(self) -> None:
    """Reset the token counts."""
    self.llm_token_counts = []
    self.embedding_token_counts = []

```
  
---|---
