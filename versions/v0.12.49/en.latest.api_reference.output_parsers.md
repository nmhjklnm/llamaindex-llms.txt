# Index
##  BaseOutputParser #
Bases: `DispatcherSpanMixin`, `ABC`
Output parser class.
Source code in `llama-index-core/llama_index/core/types.py`

| ```
class BaseOutputParser(DispatcherSpanMixin, ABC):
    """Output parser class."""

    @abstractmethod
    def parse(self, output: str) -> Any:
        """Parse, validate, and correct errors programmatically."""

    def format(self, query: str) -> str:
        """Format a query with structured output formatting instructions."""
        return query

    def _format_message(self, message: ChatMessage) -> ChatMessage:
        text_blocks: list[tuple[int, TextBlock]] = [
            (idx, block)
            for idx, block in enumerate(message.blocks)
            if isinstance(block, TextBlock)
        ]

        # add text to the last text block, or add a new text block
        format_text = ""
        if text_blocks:
            format_idx = text_blocks[-1][0]
            format_text = text_blocks[-1][1].text

            if format_idx != -1:
                # this should always be a text block
                assert isinstance(message.blocks[format_idx], TextBlock)
                message.blocks[format_idx].text = self.format(format_text)  # type: ignore
        else:
            message.blocks.append(TextBlock(text=self.format(format_text)))

        return message

    def format_messages(self, messages: List[ChatMessage]) -> List[ChatMessage]:
        """Format a list of messages with structured output formatting instructions."""
        # NOTE: apply output parser to either the first message if it's a system message
        #       or the last message
        if messages:
            if messages[0].role == MessageRole.SYSTEM:
                # get text from the last text blocks
                messages[0] = self._format_message(messages[0])
            else:
                messages[-1] = self._format_message(messages[-1])

        return messages

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Type[Any], handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.any_schema()

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> Dict[str, Any]:
        json_schema = handler(core_schema)
        return handler.resolve_ref_schema(json_schema)

```
  
---|---  
###  parse `abstractmethod` #
```
parse(output: str) -> Any

```

Parse, validate, and correct errors programmatically.
Source code in `llama-index-core/llama_index/core/types.py`

| ```
@abstractmethod
def parse(self, output: str) -> Any:
    """Parse, validate, and correct errors programmatically."""

```
  
---|---  
###  format #
```
format(query: str) -> str

```

Format a query with structured output formatting instructions.
Source code in `llama-index-core/llama_index/core/types.py`

| ```
def format(self, query: str) -> str:
    """Format a query with structured output formatting instructions."""
    return query

```
  
---|---  
###  format_messages #
```
format_messages(messages: List[ChatMessage]) -> List[ChatMessage]

```

Format a list of messages with structured output formatting instructions.
Source code in `llama-index-core/llama_index/core/types.py`

| ```
def format_messages(self, messages: List[ChatMessage]) -> List[ChatMessage]:
    """Format a list of messages with structured output formatting instructions."""
    # NOTE: apply output parser to either the first message if it's a system message
    #       or the last message
    if messages:
        if messages[0].role == MessageRole.SYSTEM:
            # get text from the last text blocks
            messages[0] = self._format_message(messages[0])
        else:
            messages[-1] = self._format_message(messages[-1])

    return messages

```
  
---|---
