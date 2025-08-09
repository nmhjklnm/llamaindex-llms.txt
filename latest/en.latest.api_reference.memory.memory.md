# Memory
##  Memory #
Bases: `BaseMemory`
A memory module that waterfalls into memory blocks.
Works by orchestrating around - a FIFO queue of messages - a list of memory blocks - various parameters (pressure size, token limit, etc.)
When the FIFO queue reaches the token limit, the oldest messages within the pressure size are ejected from the FIFO queue. The messages are then processed by each memory block.
When pulling messages from this memory, the memory blocks are processed in order, and the messages are injected into the system message or the latest user message.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`token_limit` |  `int` |  The overall token limit of the memory. |  `30000`  
`token_flush_size` |  `int` |  The token size to use for flushing the FIFO queue. |  `3000`  
`chat_history_token_ratio` |  `float` |  Minimum percentage ratio of total token limit reserved for chat history. |  `0.7`  
`memory_blocks` |  `List[BaseMemoryBlock]` |  The list of memory blocks to use. |  `<dynamic>`  
`memory_blocks_template` |  `RichPromptTemplate` |  The template to use for formatting the memory blocks. |  `RichPromptTemplate(metadata={}, template_vars=['memory_blocks'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template_str='\n<memory>\n{% for (block_name, block_content) in memory_blocks %}\n<{{ block_name }}>\n  {% for block in block_content %}\n    {% if block.block_type == "text" %}\n{{ block.text }}\n    {% elif block.block_type == "image" %}\n      {% if block.url %}\n        {{ (block.url | string) | image }}\n      {% elif block.path %}\n        {{ (block.path | string) | image }}\n      {% endif %}\n    {% elif block.block_type == "audio" %}\n      {% if block.url %}\n        {{ (block.url | string) | audio }}\n      {% elif block.path %}\n        {{ (block.path | string) | audio }}\n      {% endif %}\n    {% endif %}\n  {% endfor %}\n</{{ block_name }}>\n{% endfor %}\n</memory>\n')`  
`insert_method` |  `InsertMethod` |  Whether to inject memory blocks into a system message or into the latest user message. |  `<InsertMethod.SYSTEM: 'system'>`  
`image_token_size_estimate` |  `int` |  The token size estimate for images. |  `256`  
`audio_token_size_estimate` |  `int` |  The token size estimate for audio. |  `256`  
`tokenizer_fn` |  `Callable[list, List]` |  The tokenizer function to use for token counting. |  `<dynamic>`  
`sql_store` |  `SQLAlchemyChatStore` |  The chat store to use for storing messages. |  `SQLAlchemyChatStore(table_name='llama_index_memory', async_database_uri='sqlite+aiosqlite:///:memory:')`  
`session_id` |  `str` |  The key to use for storing messages in the chat store. |  `'50eb752f-21f2-484d-91c7-650a03029721'`  
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
class Memory(BaseMemory):
    """
    A memory module that waterfalls into memory blocks.

    Works by orchestrating around
    - a FIFO queue of messages
    - a list of memory blocks
    - various parameters (pressure size, token limit, etc.)

    When the FIFO queue reaches the token limit, the oldest messages within the pressure size are ejected from the FIFO queue.
    The messages are then processed by each memory block.

    When pulling messages from this memory, the memory blocks are processed in order, and the messages are injected into the system message or the latest user message.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    token_limit: int = Field(
        default=DEFAULT_TOKEN_LIMIT,
        description="The overall token limit of the memory.",
    )
    token_flush_size: int = Field(
        default=DEFAULT_FLUSH_SIZE,
        description="The token size to use for flushing the FIFO queue.",
    )
    chat_history_token_ratio: float = Field(
        default=0.7,
        description="Minimum percentage ratio of total token limit reserved for chat history.",
    )
    memory_blocks: List[BaseMemoryBlock] = Field(
        default_factory=list,
        description="The list of memory blocks to use.",
    )
    memory_blocks_template: RichPromptTemplate = Field(
        default=DEFAULT_MEMORY_BLOCKS_TEMPLATE,
        description="The template to use for formatting the memory blocks.",
    )
    insert_method: InsertMethod = Field(
        default=InsertMethod.SYSTEM,
        description="Whether to inject memory blocks into a system message or into the latest user message.",
    )
    image_token_size_estimate: int = Field(
        default=256,
        description="The token size estimate for images.",
    )
    audio_token_size_estimate: int = Field(
        default=256,
        description="The token size estimate for audio.",
    )
    tokenizer_fn: Callable[[str], List] = Field(
        default_factory=get_tokenizer,
        exclude=True,
        description="The tokenizer function to use for token counting.",
    )
    sql_store: SQLAlchemyChatStore = Field(
        default_factory=get_default_chat_store,
        exclude=True,
        description="The chat store to use for storing messages.",
    )
    session_id: str = Field(
        default_factory=generate_chat_store_key,
        description="The key to use for storing messages in the chat store.",
    )

    @classmethod
    def class_name(cls) -> str:
        return "Memory"

    @model_validator(mode="before")
    @classmethod
    def validate_memory(cls, values: dict) -> dict:
        # Validate token limit
        token_limit = values.get("token_limit", -1)
        if token_limit < 1:
            raise ValueError("Token limit must be set and greater than 0.")

        tokenizer_fn = values.get("tokenizer_fn")
        if tokenizer_fn is None:
            values["tokenizer_fn"] = get_tokenizer()

        if values.get("token_flush_size", -1) < 1:
            values["token_flush_size"] = int(token_limit * 0.1)
        elif values.get("token_flush_size", -1) > token_limit:
            values["token_flush_size"] = int(token_limit * 0.1)

        # validate all blocks have unique names
        block_names = [block.name for block in values.get("memory_blocks", [])]
        if len(block_names) != len(set(block_names)):
            raise ValueError("All memory blocks must have unique names.")

        return values

    @classmethod
    def from_defaults(  # type: ignore[override]
        cls,
        session_id: Optional[str] = None,
        chat_history: Optional[List[ChatMessage]] = None,
        token_limit: int = DEFAULT_TOKEN_LIMIT,
        memory_blocks: Optional[List[BaseMemoryBlock[Any]]] = None,
        tokenizer_fn: Optional[Callable[[str], List]] = None,
        chat_history_token_ratio: float = 0.7,
        token_flush_size: int = DEFAULT_FLUSH_SIZE,
        memory_blocks_template: RichPromptTemplate = DEFAULT_MEMORY_BLOCKS_TEMPLATE,
        insert_method: InsertMethod = InsertMethod.SYSTEM,
        image_token_size_estimate: int = 256,
        audio_token_size_estimate: int = 256,
        # SQLAlchemyChatStore parameters
        table_name: str = "llama_index_memory",
        async_database_uri: Optional[str] = None,
        async_engine: Optional[AsyncEngine] = None,
    ) -> "Memory":
        """Initialize Memory."""
        session_id = session_id or generate_chat_store_key()

        # If not using the SQLAlchemyChatStore, provide an error
        sql_store = SQLAlchemyChatStore(
            table_name=table_name,
            async_database_uri=async_database_uri,
            async_engine=async_engine,
        )

        if chat_history is not None:
            asyncio_run(sql_store.set_messages(session_id, chat_history))

        if token_flush_size > token_limit:
            token_flush_size = int(token_limit * 0.7)

        return cls(
            token_limit=token_limit,
            tokenizer_fn=tokenizer_fn or get_tokenizer(),
            sql_store=sql_store,
            session_id=session_id,
            memory_blocks=memory_blocks or [],
            chat_history_token_ratio=chat_history_token_ratio,
            token_flush_size=token_flush_size,
            memory_blocks_template=memory_blocks_template,
            insert_method=insert_method,
            image_token_size_estimate=image_token_size_estimate,
            audio_token_size_estimate=audio_token_size_estimate,
        )

    def _estimate_token_count(
        self,
        message_or_blocks: Union[
            str, ChatMessage, List[ChatMessage], List[ContentBlock]
        ],
    ) -> int:
        """Estimate token count for a message."""
        token_count = 0

        # Normalize the input to a list of ContentBlocks
        if isinstance(message_or_blocks, ChatMessage):
            blocks: List[
                Union[
                    TextBlock,
                    ImageBlock,
                    AudioBlock,
                    DocumentBlock,
                    CitableBlock,
                    CitationBlock,
                ]
            ] = []

            for block in message_or_blocks.blocks:
                if not isinstance(block, CachePoint):
                    blocks.append(block)

            # Estimate the token count for the additional kwargs
            if message_or_blocks.additional_kwargs:
                token_count += len(
                    self.tokenizer_fn(str(message_or_blocks.additional_kwargs))
                )
        elif isinstance(message_or_blocks, List):
            # Type narrow the list
            messages: List[ChatMessage] = []

            if all(isinstance(item, ChatMessage) for item in message_or_blocks):
                messages = cast(List[ChatMessage], message_or_blocks)

                blocks = []
                for msg in messages:
                    for block in msg.blocks:
                        if not isinstance(block, CachePoint):
                            blocks.append(block)

                # Estimate the token count for the additional kwargs
                token_count += sum(
                    len(self.tokenizer_fn(str(msg.additional_kwargs)))
                    for msg in messages
                    if msg.additional_kwargs
                )
            elif all(
                isinstance(
                    item, (TextBlock, ImageBlock, AudioBlock, DocumentBlock, CachePoint)
                )
                for item in message_or_blocks
            ):
                blocks = []
                for item in message_or_blocks:
                    if not isinstance(item, CachePoint):
                        blocks.append(
                            cast(
                                Union[TextBlock, ImageBlock, AudioBlock, DocumentBlock],
                                item,
                            )
                        )
            else:
                raise ValueError(f"Invalid message type: {type(message_or_blocks)}")
        elif isinstance(message_or_blocks, str):
            blocks = [TextBlock(text=message_or_blocks)]
        else:
            raise ValueError(f"Invalid message type: {type(message_or_blocks)}")

        # Estimate the token count for each block
        for block in blocks:
            if isinstance(block, TextBlock):
                token_count += len(self.tokenizer_fn(block.text))
            elif isinstance(block, ImageBlock):
                token_count += self.image_token_size_estimate
            elif isinstance(block, AudioBlock):
                token_count += self.audio_token_size_estimate

        return token_count

    async def _get_memory_blocks_content(
        self,
        chat_history: List[ChatMessage],
        input: Optional[Union[str, ChatMessage]] = None,
        **block_kwargs: Any,
    ) -> Dict[str, Any]:
        """Get content from memory blocks in priority order."""
        content_per_memory_block: Dict[str, Any] = {}

        block_input = chat_history
        if isinstance(input, str):
            block_input = [*chat_history, ChatMessage(role="user", content=input)]

        # Process memory blocks in priority order
        for memory_block in sorted(self.memory_blocks, key=lambda x: -x.priority):
            content = await memory_block.aget(
                block_input, session_id=self.session_id, **block_kwargs
            )

            # Handle different return types from memory blocks
            if content and isinstance(content, list):
                # Memory block returned content blocks
                content_per_memory_block[memory_block.name] = content
            elif content and isinstance(content, str):
                # Memory block returned a string
                content_per_memory_block[memory_block.name] = content
            elif not content:
                continue
            else:
                raise ValueError(
                    f"Invalid content type received from memory block {memory_block.name}: {type(content)}"
                )

        return content_per_memory_block

    async def _truncate_memory_blocks(
        self,
        content_per_memory_block: Dict[str, Any],
        memory_blocks_tokens: int,
        chat_history_tokens: int,
    ) -> Dict[str, Any]:
        """Truncate memory blocks if total token count exceeds limit."""
        if memory_blocks_tokens + chat_history_tokens <= self.token_limit:
            return content_per_memory_block

        tokens_to_truncate = (
            memory_blocks_tokens + chat_history_tokens - self.token_limit
        )
        truncated_content = content_per_memory_block.copy()

        # Truncate memory blocks based on priority
        for memory_block in sorted(
            self.memory_blocks, key=lambda x: x.priority
        ):  # Lower priority first
            # Skip memory blocks with priority 0, they should never be truncated
            if memory_block.priority == 0:
                continue

            if tokens_to_truncate <= 0:
                break

            # Truncate content and measure tokens saved
            content = truncated_content.get(memory_block.name, [])

            truncated_block_content = await memory_block.atruncate(
                content, tokens_to_truncate
            )

            # Calculate tokens saved
            original_tokens = self._estimate_token_count(content)

            if truncated_block_content is None:
                new_tokens = 0
            else:
                new_tokens = self._estimate_token_count(truncated_block_content)

            tokens_saved = original_tokens - new_tokens
            tokens_to_truncate -= tokens_saved

            # Update the content blocks
            if truncated_block_content is None:
                truncated_content[memory_block.name] = []
            else:
                truncated_content[memory_block.name] = truncated_block_content

        # handle case where we still have tokens to truncate
        # just remove the blocks starting from the least priority
        for memory_block in sorted(self.memory_blocks, key=lambda x: x.priority):
            if memory_block.priority == 0:
                continue

            if tokens_to_truncate <= 0:
                break

            # Truncate content and measure tokens saved
            content = truncated_content.pop(memory_block.name)
            tokens_to_truncate -= self._estimate_token_count(content)

        return truncated_content

    async def _format_memory_blocks(
        self, content_per_memory_block: Dict[str, Any]
    ) -> Tuple[List[Tuple[str, List[ContentBlock]]], List[ChatMessage]]:
        """Format memory blocks content into template data and chat messages."""
        memory_blocks_data: List[Tuple[str, List[ContentBlock]]] = []
        chat_message_data: List[ChatMessage] = []

        for block in self.memory_blocks:
            if block.name in content_per_memory_block:
                content = content_per_memory_block[block.name]

                # Skip empty memory blocks
                if not content:
                    continue

                if (
                    isinstance(content, list)
                    and content
                    and isinstance(content[0], ChatMessage)
                ):
                    chat_message_data.extend(content)
                elif isinstance(content, str):
                    memory_blocks_data.append((block.name, [TextBlock(text=content)]))
                else:
                    memory_blocks_data.append((block.name, content))

        return memory_blocks_data, chat_message_data

    def _insert_memory_content(
        self,
        chat_history: List[ChatMessage],
        memory_content: List[ContentBlock],
        chat_message_data: List[ChatMessage],
    ) -> List[ChatMessage]:
        """Insert memory content into chat history based on insert method."""
        result = chat_history.copy()

        # Process chat messages
        if chat_message_data:
            result = [*chat_message_data, *result]

        # Process template-based memory blocks
        if memory_content:
            if self.insert_method == InsertMethod.SYSTEM:
                # Find system message or create a new one
                system_idx = next(
                    (i for i, msg in enumerate(result) if msg.role == "system"), None
                )

                if system_idx is not None:
                    # Update existing system message
                    result[system_idx].blocks = [
                        *memory_content,
                        *result[system_idx].blocks,
                    ]
                else:
                    # Create new system message at the beginning
                    result.insert(0, ChatMessage(role="system", blocks=memory_content))
            elif self.insert_method == InsertMethod.USER:
                # Find the latest user message
                session_idx = next(
                    (i for i, msg in enumerate(reversed(result)) if msg.role == "user"),
                    None,
                )

                if session_idx is not None:
                    # Get actual index (since we enumerated in reverse)
                    actual_idx = len(result) - 1 - session_idx
                    # Update existing user message
                    result[actual_idx].blocks = [
                        *memory_content,
                        *result[actual_idx].blocks,
                    ]
                else:
                    result.append(ChatMessage(role="user", blocks=memory_content))

        return result

    async def aget(
        self, input: Optional[Union[str, ChatMessage]] = None, **block_kwargs: Any
    ) -> List[ChatMessage]:  # type: ignore[override]
        """Get messages with memory blocks included (async)."""
        # Get chat history efficiently
        chat_history = await self.sql_store.get_messages(
            self.session_id, status=MessageStatus.ACTIVE
        )
        chat_history_tokens = sum(
            self._estimate_token_count(message) for message in chat_history
        )

        # Get memory blocks content
        content_per_memory_block = await self._get_memory_blocks_content(
            chat_history, input=input, **block_kwargs
        )

        # Calculate memory blocks tokens
        memory_blocks_tokens = sum(
            self._estimate_token_count(content)
            for content in content_per_memory_block.values()
        )

        # Handle truncation if needed
        truncated_content = await self._truncate_memory_blocks(
            content_per_memory_block, memory_blocks_tokens, chat_history_tokens
        )

        # Format template-based memory blocks
        memory_blocks_data, chat_message_data = await self._format_memory_blocks(
            truncated_content
        )

        # Create messages from template content
        memory_content = []
        if memory_blocks_data:
            memory_block_messages = self.memory_blocks_template.format_messages(
                memory_blocks=memory_blocks_data
            )
            memory_content = (
                memory_block_messages[0].blocks if memory_block_messages else []
            )

        # Insert memory content into chat history
        return self._insert_memory_content(
            chat_history, memory_content, chat_message_data
        )

    async def _manage_queue(self) -> None:
        """
        Manage the FIFO queue.

        This function manages the memory queue using a waterfall approach:
        1. If the queue exceeds the token limit, it removes oldest messages first
        2. Removed messages are archived and passed to memory blocks
        3. It ensures conversation integrity by keeping related messages together
        4. It maintains at least one complete conversation turn
        """
        # Calculate if we need to waterfall
        current_queue = await self.sql_store.get_messages(
            self.session_id, status=MessageStatus.ACTIVE
        )

        # If current queue is empty, return
        if not current_queue:
            return

        tokens_in_current_queue = sum(
            self._estimate_token_count(message) for message in current_queue
        )

        # If we're over the token limit, initiate waterfall
        token_limit = self.token_limit * self.chat_history_token_ratio
        if tokens_in_current_queue > token_limit:
            # Process from oldest to newest, but efficiently with pop() operations
            reversed_queue = current_queue[::-1]  # newest first, oldest last

            # Calculate approximate number of messages to remove
            tokens_to_remove = tokens_in_current_queue - token_limit

            while tokens_to_remove > 0:
                # If only one message left, keep it regardless of token count
                if len(reversed_queue) <= 1:
                    break

                # Collect messages to flush (up to flush size)
                messages_to_flush = []
                flushed_tokens = 0

                # Remove oldest messages (from end of reversed list) until reaching flush size
                while (
                    flushed_tokens < self.token_flush_size
                    and reversed_queue
                    and len(reversed_queue) > 1
                ):
                    message = reversed_queue.pop()
                    messages_to_flush.append(message)
                    flushed_tokens += self._estimate_token_count(message)

                # Ensure we keep at least one message
                if not reversed_queue and messages_to_flush:
                    reversed_queue.append(messages_to_flush.pop())

                # We need to maintain conversation integrity
                # Messages should be removed in complete conversation turns
                chronological_view = reversed_queue[::-1]  # View in chronological order

                # Find the correct conversation boundary
                # We want the first message in our remaining queue to be a user message
                # and the last message to be from assistant or tool
                if chronological_view:
                    # Keep removing messages until first remaining message is from user
                    # This ensures we start with a user message
                    while (
                        chronological_view
                        and chronological_view[0].role != "user"
                        and len(reversed_queue) > 1
                    ):
                        if reversed_queue:
                            messages_to_flush.append(reversed_queue.pop())
                            chronological_view = reversed_queue[::-1]
                        else:
                            break

                    # If we end up with an empty queue, keep at least one full conversation turn
                    if not reversed_queue and messages_to_flush:
                        # Find the most recent complete conversation turn
                        # (user → assistant/tool sequence) in messages_to_flush
                        found_user = False
                        turn_messages: List[ChatMessage] = []

                        # Go through messages_to_flush in reverse (newest first)
                        for msg in reversed(messages_to_flush):
                            if msg.role == "user" and not found_user:
                                found_user = True
                                turn_messages.insert(0, msg)
                            elif found_user:
                                turn_messages.insert(0, msg)
                            else:
                                break

                        # If we found a complete turn, keep it
                        if found_user and turn_messages:
                            # Remove these messages from messages_to_flush
                            for msg in turn_messages:
                                messages_to_flush.remove(msg)
                            # Add them back to the queue
                            reversed_queue = turn_messages[::-1] + reversed_queue

                # Archive the flushed messages
                if messages_to_flush:
                    await self.sql_store.archive_oldest_messages(
                        self.session_id, n=len(messages_to_flush)
                    )

                    # Waterfall the flushed messages to memory blocks
                    await asyncio.gather(
                        *[
                            block.aput(
                                messages_to_flush,
                                from_short_term_memory=True,
                                session_id=self.session_id,
                            )
                            for block in self.memory_blocks
                        ]
                    )

                # Recalculate remaining tokens
                chronological_view = reversed_queue[::-1]
                tokens_in_current_queue = sum(
                    self._estimate_token_count(message)
                    for message in chronological_view
                )
                tokens_to_remove = tokens_in_current_queue - token_limit

                # Exit if we've flushed everything possible but still over limit
                if not messages_to_flush:
                    break

    async def aput(self, message: ChatMessage) -> None:
        """Add a message to the chat store and process waterfall logic if needed."""
        # Add the message to the chat store
        await self.sql_store.add_message(
            self.session_id, message, status=MessageStatus.ACTIVE
        )

        # Ensure the active queue is managed
        await self._manage_queue()

    async def aput_messages(self, messages: List[ChatMessage]) -> None:
        """Add a list of messages to the chat store and process waterfall logic if needed."""
        # Add the messages to the chat store
        await self.sql_store.add_messages(
            self.session_id, messages, status=MessageStatus.ACTIVE
        )

        # Ensure the active queue is managed
        await self._manage_queue()

    async def aset(self, messages: List[ChatMessage]) -> None:
        """Set the chat history."""
        await self.sql_store.set_messages(
            self.session_id, messages, status=MessageStatus.ACTIVE
        )

    async def aget_all(
        self, status: Optional[MessageStatus] = None
    ) -> List[ChatMessage]:
        """Get all messages."""
        return await self.sql_store.get_messages(self.session_id, status=status)

    async def areset(self, status: Optional[MessageStatus] = None) -> None:
        """Reset the memory."""
        await self.sql_store.delete_messages(self.session_id, status=status)

    # ---- Sync method wrappers ----

    def get(
        self, input: Optional[Union[str, ChatMessage]] = None, **block_kwargs: Any
    ) -> List[ChatMessage]:  # type: ignore[override]
        """Get messages with memory blocks included."""
        return asyncio_run(self.aget(input=input, **block_kwargs))

    def get_all(self, status: Optional[MessageStatus] = None) -> List[ChatMessage]:
        """Get all messages."""
        return asyncio_run(self.aget_all(status=status))

    def put(self, message: ChatMessage) -> None:
        """Add a message to the chat store and process waterfall logic if needed."""
        return asyncio_run(self.aput(message))

    def set(self, messages: List[ChatMessage]) -> None:
        """Set the chat history."""
        return asyncio_run(self.aset(messages))

    def reset(self) -> None:
        """Reset the memory."""
        return asyncio_run(self.areset())

```
  
---|---  
###  from_defaults `classmethod` #
```
from_defaults(session_id: Optional[str] = None, chat_history: Optional[List[ChatMessage]] = None, token_limit: int = DEFAULT_TOKEN_LIMIT, memory_blocks: Optional[List[BaseMemoryBlock[Any]]] = None, tokenizer_fn: Optional[Callable[[str], List]] = None, chat_history_token_ratio: float = 0.7, token_flush_size: int = DEFAULT_FLUSH_SIZE, memory_blocks_template: RichPromptTemplate = DEFAULT_MEMORY_BLOCKS_TEMPLATE, insert_method: InsertMethod = SYSTEM, image_token_size_estimate: int = 256, audio_token_size_estimate: int = 256, table_name: str = 'llama_index_memory', async_database_uri: Optional[str] = None, async_engine: Optional[AsyncEngine] = None) -> Memory

```

Initialize Memory.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
@classmethod
def from_defaults(  # type: ignore[override]
    cls,
    session_id: Optional[str] = None,
    chat_history: Optional[List[ChatMessage]] = None,
    token_limit: int = DEFAULT_TOKEN_LIMIT,
    memory_blocks: Optional[List[BaseMemoryBlock[Any]]] = None,
    tokenizer_fn: Optional[Callable[[str], List]] = None,
    chat_history_token_ratio: float = 0.7,
    token_flush_size: int = DEFAULT_FLUSH_SIZE,
    memory_blocks_template: RichPromptTemplate = DEFAULT_MEMORY_BLOCKS_TEMPLATE,
    insert_method: InsertMethod = InsertMethod.SYSTEM,
    image_token_size_estimate: int = 256,
    audio_token_size_estimate: int = 256,
    # SQLAlchemyChatStore parameters
    table_name: str = "llama_index_memory",
    async_database_uri: Optional[str] = None,
    async_engine: Optional[AsyncEngine] = None,
) -> "Memory":
    """Initialize Memory."""
    session_id = session_id or generate_chat_store_key()

    # If not using the SQLAlchemyChatStore, provide an error
    sql_store = SQLAlchemyChatStore(
        table_name=table_name,
        async_database_uri=async_database_uri,
        async_engine=async_engine,
    )

    if chat_history is not None:
        asyncio_run(sql_store.set_messages(session_id, chat_history))

    if token_flush_size > token_limit:
        token_flush_size = int(token_limit * 0.7)

    return cls(
        token_limit=token_limit,
        tokenizer_fn=tokenizer_fn or get_tokenizer(),
        sql_store=sql_store,
        session_id=session_id,
        memory_blocks=memory_blocks or [],
        chat_history_token_ratio=chat_history_token_ratio,
        token_flush_size=token_flush_size,
        memory_blocks_template=memory_blocks_template,
        insert_method=insert_method,
        image_token_size_estimate=image_token_size_estimate,
        audio_token_size_estimate=audio_token_size_estimate,
    )

```
  
---|---  
###  aget `async` #
```
aget(input: Optional[Union[str, ChatMessage]] = None, **block_kwargs: Any) -> List[ChatMessage]

```

Get messages with memory blocks included (async).
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def aget(
    self, input: Optional[Union[str, ChatMessage]] = None, **block_kwargs: Any
) -> List[ChatMessage]:  # type: ignore[override]
    """Get messages with memory blocks included (async)."""
    # Get chat history efficiently
    chat_history = await self.sql_store.get_messages(
        self.session_id, status=MessageStatus.ACTIVE
    )
    chat_history_tokens = sum(
        self._estimate_token_count(message) for message in chat_history
    )

    # Get memory blocks content
    content_per_memory_block = await self._get_memory_blocks_content(
        chat_history, input=input, **block_kwargs
    )

    # Calculate memory blocks tokens
    memory_blocks_tokens = sum(
        self._estimate_token_count(content)
        for content in content_per_memory_block.values()
    )

    # Handle truncation if needed
    truncated_content = await self._truncate_memory_blocks(
        content_per_memory_block, memory_blocks_tokens, chat_history_tokens
    )

    # Format template-based memory blocks
    memory_blocks_data, chat_message_data = await self._format_memory_blocks(
        truncated_content
    )

    # Create messages from template content
    memory_content = []
    if memory_blocks_data:
        memory_block_messages = self.memory_blocks_template.format_messages(
            memory_blocks=memory_blocks_data
        )
        memory_content = (
            memory_block_messages[0].blocks if memory_block_messages else []
        )

    # Insert memory content into chat history
    return self._insert_memory_content(
        chat_history, memory_content, chat_message_data
    )

```
  
---|---  
###  aput `async` #
```
aput(message: ChatMessage) -> None

```

Add a message to the chat store and process waterfall logic if needed.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def aput(self, message: ChatMessage) -> None:
    """Add a message to the chat store and process waterfall logic if needed."""
    # Add the message to the chat store
    await self.sql_store.add_message(
        self.session_id, message, status=MessageStatus.ACTIVE
    )

    # Ensure the active queue is managed
    await self._manage_queue()

```
  
---|---  
###  aput_messages `async` #
```
aput_messages(messages: List[ChatMessage]) -> None

```

Add a list of messages to the chat store and process waterfall logic if needed.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def aput_messages(self, messages: List[ChatMessage]) -> None:
    """Add a list of messages to the chat store and process waterfall logic if needed."""
    # Add the messages to the chat store
    await self.sql_store.add_messages(
        self.session_id, messages, status=MessageStatus.ACTIVE
    )

    # Ensure the active queue is managed
    await self._manage_queue()

```
  
---|---  
###  aset `async` #
```
aset(messages: List[ChatMessage]) -> None

```

Set the chat history.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def aset(self, messages: List[ChatMessage]) -> None:
    """Set the chat history."""
    await self.sql_store.set_messages(
        self.session_id, messages, status=MessageStatus.ACTIVE
    )

```
  
---|---  
###  aget_all `async` #
```
aget_all(status: Optional[MessageStatus] = None) -> List[ChatMessage]

```

Get all messages.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def aget_all(
    self, status: Optional[MessageStatus] = None
) -> List[ChatMessage]:
    """Get all messages."""
    return await self.sql_store.get_messages(self.session_id, status=status)

```
  
---|---  
###  areset `async` #
```
areset(status: Optional[MessageStatus] = None) -> None

```

Reset the memory.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def areset(self, status: Optional[MessageStatus] = None) -> None:
    """Reset the memory."""
    await self.sql_store.delete_messages(self.session_id, status=status)

```
  
---|---  
###  get #
```
get(input: Optional[Union[str, ChatMessage]] = None, **block_kwargs: Any) -> List[ChatMessage]

```

Get messages with memory blocks included.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
def get(
    self, input: Optional[Union[str, ChatMessage]] = None, **block_kwargs: Any
) -> List[ChatMessage]:  # type: ignore[override]
    """Get messages with memory blocks included."""
    return asyncio_run(self.aget(input=input, **block_kwargs))

```
  
---|---  
###  get_all #
```
get_all(status: Optional[MessageStatus] = None) -> List[ChatMessage]

```

Get all messages.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
def get_all(self, status: Optional[MessageStatus] = None) -> List[ChatMessage]:
    """Get all messages."""
    return asyncio_run(self.aget_all(status=status))

```
  
---|---  
###  put #
```
put(message: ChatMessage) -> None

```

Add a message to the chat store and process waterfall logic if needed.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
def put(self, message: ChatMessage) -> None:
    """Add a message to the chat store and process waterfall logic if needed."""
    return asyncio_run(self.aput(message))

```
  
---|---  
###  set #
```
set(messages: List[ChatMessage]) -> None

```

Set the chat history.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
def set(self, messages: List[ChatMessage]) -> None:
    """Set the chat history."""
    return asyncio_run(self.aset(messages))

```
  
---|---  
###  reset #
```
reset() -> None

```

Reset the memory.
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
def reset(self) -> None:
    """Reset the memory."""
    return asyncio_run(self.areset())

```
  
---|---  
##  BaseMemoryBlock #
Bases: `BaseModel`, `Generic[T]`
A base class for memory blocks.
Subclasses must implement the `aget` and `aput` methods. Optionally, subclasses can implement the `atruncate` method, which is used to reduce the size of the memory block.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`name` |  `str` |  The name/identifier of the memory block. |  _required_  
`description` |  `str | None` |  A description of the memory block. |  `None`  
`priority` |  `int` |  Priority of this memory block (0 = never truncate, 1 = highest priority, etc.). |  `0`  
`accept_short_term_memory` |  `bool` |  Whether to accept puts from messages ejected from the short-term memory. |  `True`  
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
class BaseMemoryBlock(BaseModel, Generic[T]):
    """
    A base class for memory blocks.

    Subclasses must implement the `aget` and `aput` methods.
    Optionally, subclasses can implement the `atruncate` method, which is used to reduce the size of the memory block.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(description="The name/identifier of the memory block.")
    description: Optional[str] = Field(
        default=None, description="A description of the memory block."
    )
    priority: int = Field(
        default=0,
        description="Priority of this memory block (0 = never truncate, 1 = highest priority, etc.).",
    )
    accept_short_term_memory: bool = Field(
        default=True,
        description="Whether to accept puts from messages ejected from the short-term memory.",
    )

    @abstractmethod
    async def _aget(
        self, messages: Optional[List[ChatMessage]] = None, **block_kwargs: Any
    ) -> T:
        """Pull the memory block (async)."""

    async def aget(
        self, messages: Optional[List[ChatMessage]] = None, **block_kwargs: Any
    ) -> T:
        """
        Pull the memory block (async).

        Returns:
            T: The memory block content. One of:
            - str: A simple text string to be inserted into the template.
            - List[ContentBlock]: A list of content blocks to be inserted into the template.
            - List[ChatMessage]: A list of chat messages to be directly appended to the chat history.

        """
        return await self._aget(messages, **block_kwargs)

    @abstractmethod
    async def _aput(self, messages: List[ChatMessage]) -> None:
        """Push to the memory block (async)."""

    async def aput(
        self,
        messages: List[ChatMessage],
        from_short_term_memory: bool = False,
        session_id: Optional[str] = None,
    ) -> None:
        """Push to the memory block (async)."""
        if from_short_term_memory and not self.accept_short_term_memory:
            return

        if session_id is not None:
            for message in messages:
                message.additional_kwargs["session_id"] = session_id

        await self._aput(messages)

    async def atruncate(self, content: T, tokens_to_truncate: int) -> Optional[T]:
        """
        Truncate the memory block content to the given token limit.

        By default, truncation will remove the entire block content.

        Args:
            content:
                The content of type T, depending on what the memory block returns.
            tokens_to_truncate:
                The number of tokens requested to truncate the content by.
                Blocks may or may not truncate to the exact number of tokens requested, but it
                can be used as a hint for the block to truncate.

        Returns:
            The truncated content of type T, or None if the content is completely truncated.

        """
        return None

```
  
---|---  
###  aget `async` #
```
aget(messages: Optional[List[ChatMessage]] = None, **block_kwargs: Any) -> T

```

Pull the memory block (async).
Returns:
Name | Type | Description  
---|---|---  
`T` |  `T` |  The memory block content. One of:  
|  `T` | 
  * str: A simple text string to be inserted into the template.

  
|  `T` | 
  * List[ContentBlock]: A list of content blocks to be inserted into the template.

  
|  `T` | 
  * List[ChatMessage]: A list of chat messages to be directly appended to the chat history.

  
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def aget(
    self, messages: Optional[List[ChatMessage]] = None, **block_kwargs: Any
) -> T:
    """
    Pull the memory block (async).

    Returns:
        T: The memory block content. One of:
        - str: A simple text string to be inserted into the template.
        - List[ContentBlock]: A list of content blocks to be inserted into the template.
        - List[ChatMessage]: A list of chat messages to be directly appended to the chat history.

    """
    return await self._aget(messages, **block_kwargs)

```
  
---|---  
###  aput `async` #
```
aput(messages: List[ChatMessage], from_short_term_memory: bool = False, session_id: Optional[str] = None) -> None

```

Push to the memory block (async).
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def aput(
    self,
    messages: List[ChatMessage],
    from_short_term_memory: bool = False,
    session_id: Optional[str] = None,
) -> None:
    """Push to the memory block (async)."""
    if from_short_term_memory and not self.accept_short_term_memory:
        return

    if session_id is not None:
        for message in messages:
            message.additional_kwargs["session_id"] = session_id

    await self._aput(messages)

```
  
---|---  
###  atruncate `async` #
```
atruncate(content: T, tokens_to_truncate: int) -> Optional[T]

```

Truncate the memory block content to the given token limit.
By default, truncation will remove the entire block content.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`content` |  `T` |  The content of type T, depending on what the memory block returns. |  _required_  
`tokens_to_truncate` |  `int` |  The number of tokens requested to truncate the content by. Blocks may or may not truncate to the exact number of tokens requested, but it can be used as a hint for the block to truncate. |  _required_  
Returns:
Type | Description  
---|---  
`Optional[T]` |  The truncated content of type T, or None if the content is completely truncated.  
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
async def atruncate(self, content: T, tokens_to_truncate: int) -> Optional[T]:
    """
    Truncate the memory block content to the given token limit.

    By default, truncation will remove the entire block content.

    Args:
        content:
            The content of type T, depending on what the memory block returns.
        tokens_to_truncate:
            The number of tokens requested to truncate the content by.
            Blocks may or may not truncate to the exact number of tokens requested, but it
            can be used as a hint for the block to truncate.

    Returns:
        The truncated content of type T, or None if the content is completely truncated.

    """
    return None

```
  
---|---  
##  InsertMethod #
Bases: `Enum`
Source code in `llama-index-core/llama_index/core/memory/memory.py`

| ```
class InsertMethod(Enum):
    SYSTEM = "system"
    USER = "user"

```
  
---|---  
##  StaticMemoryBlock #
Bases: `BaseMemoryBlock[List[ContentBlock]]`
A memory block that returns static text.
This block is useful for including constant information or instructions in the context without relying on external processing.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`name` |  `str` |  The name of the memory block. |  `'StaticContent'`  
`static_content` |  `List[Annotated[Union[TextBlock, ImageBlock, AudioBlock, DocumentBlock], FieldInfo]]` |  Static text or content to be returned by this memory block. |  _required_  
Source code in `llama-index-core/llama_index/core/memory/memory_blocks/static.py`

| ```
class StaticMemoryBlock(BaseMemoryBlock[List[ContentBlock]]):
    """
    A memory block that returns static text.

    This block is useful for including constant information or instructions
    in the context without relying on external processing.
    """

    name: str = Field(
        default="StaticContent", description="The name of the memory block."
    )
    static_content: Union[List[ContentBlock]] = Field(
        description="Static text or content to be returned by this memory block."
    )

    @field_validator("static_content", mode="before")
    @classmethod
    def validate_static_content(
        cls, v: Union[str, List[ContentBlock]]
    ) -> List[ContentBlock]:
        if isinstance(v, str):
            v = [TextBlock(text=v)]
        return v

    async def _aget(
        self, messages: Optional[List[ChatMessage]] = None, **block_kwargs: Any
    ) -> List[ContentBlock]:
        """Return the static text, potentially filtered by conditions."""
        return self.static_content

    async def _aput(self, messages: List[ChatMessage]) -> None:
        """No-op for static blocks as they don't change."""

```
  
---|---  
##  VectorMemoryBlock #
Bases: `BaseMemoryBlock[str]`
A memory block that retrieves relevant information from a vector store.
This block stores conversation history in a vector store and retrieves relevant information based on the most recent messages.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`name` |  `str` |  The name of the memory block. |  `'RetrievedMessages'`  
`vector_store` |  `BasePydanticVectorStore` |  The vector store to use for retrieval. |  _required_  
`embed_model` |  `BaseEmbedding` |  The embedding model to use for encoding queries and documents. |  `<dynamic>`  
`similarity_top_k` |  `int` |  Number of top results to return. |  `2`  
`retrieval_context_window` |  `int` |  Maximum number of messages to include for context when retrieving. |  `5`  
`format_template` |  `BasePromptTemplate` |  Template for formatting the retrieved information. |  `RichPromptTemplate(metadata={}, template_vars=['text'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template_str='{{ text }}')`  
`node_postprocessors` |  `List[BaseNodePostprocessor]` |  List of node postprocessors to apply to the retrieved nodes containing messages. |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/memory/memory_blocks/vector.py`

| ```
class VectorMemoryBlock(BaseMemoryBlock[str]):
    """
    A memory block that retrieves relevant information from a vector store.

    This block stores conversation history in a vector store and retrieves
    relevant information based on the most recent messages.
    """

    name: str = Field(
        default="RetrievedMessages", description="The name of the memory block."
    )
    vector_store: BasePydanticVectorStore = Field(
        description="The vector store to use for retrieval."
    )
    embed_model: BaseEmbedding = Field(
        default_factory=get_default_embed_model,
        description="The embedding model to use for encoding queries and documents.",
    )
    similarity_top_k: int = Field(
        default=2, description="Number of top results to return."
    )
    retrieval_context_window: int = Field(
        default=5,
        description="Maximum number of messages to include for context when retrieving.",
    )
    format_template: BasePromptTemplate = Field(
        default=DEFAULT_RETRIEVED_TEXT_TEMPLATE,
        description="Template for formatting the retrieved information.",
    )
    node_postprocessors: List[BaseNodePostprocessor] = Field(
        default_factory=list,
        description="List of node postprocessors to apply to the retrieved nodes containing messages.",
    )
    query_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional keyword arguments for the vector store query.",
    )

    @field_validator("vector_store", mode="before")
    def validate_vector_store(cls, v: Any) -> "BasePydanticVectorStore":
        if not isinstance(v, BasePydanticVectorStore):
            raise ValueError("vector_store must be a BasePydanticVectorStore")
        if not v.stores_text:
            raise ValueError(
                "vector_store must store text to be used as a retrieval memory block"
            )

        return v

    @field_validator("format_template", mode="before")
    @classmethod
    def validate_format_template(cls, v: Any) -> "BasePromptTemplate":
        if isinstance(v, str):
            if "{{" in v and "}}" in v:
                v = RichPromptTemplate(v)
            else:
                v = PromptTemplate(v)

        return v

    def _get_text_from_messages(self, messages: List[ChatMessage]) -> str:
        """Get the text from the messages."""
        text = ""
        for i, message in enumerate(messages):
            for block in message.blocks:
                if isinstance(block, TextBlock):
                    text += block.text
            if len(messages) > 1 and i != len(messages) - 1:
                text += " "
        return text

    async def _aget(
        self,
        messages: Optional[List[ChatMessage]] = None,
        session_id: Optional[str] = None,
        **block_kwargs: Any,
    ) -> str:
        """Retrieve relevant information based on recent messages."""
        if not messages or len(messages) == 0:
            return ""

        # Use the last message or a context window of messages for the query
        if (
            self.retrieval_context_window > 1
            and len(messages) >= self.retrieval_context_window
        ):
            context = messages[-self.retrieval_context_window :]
        else:
            context = messages

        query_text = self._get_text_from_messages(context)
        if not query_text:
            return ""

        # Handle filtering by session_id
        if session_id is not None:
            filter = MetadataFilter(key="session_id", value=session_id)
            if "filters" in self.query_kwargs and isinstance(
                self.query_kwargs["filters"], MetadataFilters
            ):
                # only add session_id filter if it does not exist in the filters list
                session_id_filter_exists = False
                for metadata_filter in self.query_kwargs["filters"].filters:
                    if (
                        isinstance(metadata_filter, MetadataFilter)
                        and metadata_filter.key == "session_id"
                    ):
                        session_id_filter_exists = True
                        break
                if not session_id_filter_exists:
                    self.query_kwargs["filters"].filters.append(filter)
            else:
                self.query_kwargs["filters"] = MetadataFilters(filters=[filter])

        # Create and execute the query
        query_embedding = await self.embed_model.aget_query_embedding(query_text)
        query = VectorStoreQuery(
            query_str=query_text,
            query_embedding=query_embedding,
            similarity_top_k=self.similarity_top_k,
            **self.query_kwargs,
        )

        results = await self.vector_store.aquery(query)
        nodes_with_scores = [
            NodeWithScore(node=node, score=score)
            for node, score in zip(results.nodes or [], results.similarities or [])
        ]
        if not nodes_with_scores:
            return ""

        # Apply postprocessors
        for postprocessor in self.node_postprocessors:
            nodes_with_scores = await postprocessor.apostprocess_nodes(
                nodes_with_scores, query_str=query_text
            )

        # Format the results
        retrieved_text = "\n\n".join([node.get_content() for node in nodes_with_scores])
        return self.format_template.format(text=retrieved_text)

    async def _aput(self, messages: List[ChatMessage]) -> None:
        """Store messages in the vector store for future retrieval."""
        if not messages:
            return

        # Format messages with role, text content, and additional info
        texts = []
        session_id = None
        for message in messages:
            text = self._get_text_from_messages([message])
            if not text:
                continue

            # special case for session_id
            if "session_id" in message.additional_kwargs:
                session_id = message.additional_kwargs.pop("session_id")

            if message.additional_kwargs:
                text += f"\nAdditional Info: ({message.additional_kwargs!s})"

            text = f"<message role='{message.role.value}'>{text}</message>"
            texts.append(text)

        if not texts:
            return

        # Get embeddings
        text_node = TextNode(text="\n".join(texts), metadata={"session_id": session_id})
        text_node.embedding = await self.embed_model.aget_text_embedding(text_node.text)

        # Add to vector store, one node per entire message batch
        await self.vector_store.async_add([text_node])

```
  
---|---  
##  FactExtractionMemoryBlock #
Bases: `BaseMemoryBlock[str]`
A memory block that extracts key facts from conversation history using an LLM.
This block identifies and stores discrete facts disclosed during the conversation, structuring them in XML format for easy parsing and retrieval.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`name` |  `str` |  The name of the memory block. |  `'ExtractedFacts'`  
`llm` |  `LLM` |  The LLM to use for fact extraction. |  `<dynamic>`  
`facts` |  `List[str]` |  List of extracted facts from the conversation. |  `<dynamic>`  
`max_facts` |  `int` |  The maximum number of facts to store. |  `50`  
`fact_extraction_prompt_template` |  `BasePromptTemplate` |  Template for the fact extraction prompt. |  `RichPromptTemplate(metadata={}, template_vars=['existing_facts'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template_str='You are a precise fact extraction system designed to identify key information from conversations.\n\nINSTRUCTIONS:\n1. Review the conversation segment provided prior to this message\n2. Extract specific, concrete facts the user has disclosed or important information discovered\n3. Focus on factual information like preferences, personal details, requirements, constraints, or context\n4. Format each fact as a separate <fact> XML tag\n5. Do not include opinions, summaries, or interpretations - only extract explicit information\n6. Do not duplicate facts that are already in the existing facts list\n\n<existing_facts>\n{{ existing_facts }}\n</existing_facts>\n\nReturn ONLY the extracted facts in this exact format:\n<facts>\n  <fact>Specific fact 1</fact>\n  <fact>Specific fact 2</fact>\n  <!-- More facts as needed -->\n</facts>\n\nIf no new facts are present, return: <facts></facts>')`  
`fact_condense_prompt_template` |  `BasePromptTemplate` |  Template for the fact condense prompt. |  `RichPromptTemplate(metadata={}, template_vars=['existing_facts', 'max_facts'], kwargs={}, output_parser=None, template_var_mappings=None, function_mappings=None, template_str='You are a precise fact condensing system designed to identify key information from conversations.\n\nINSTRUCTIONS:\n1. Review the current list of existing facts\n2. Condense the facts into a more concise list, less than {{ max_facts }} facts\n3. Focus on factual information like preferences, personal details, requirements, constraints, or context\n4. Format each fact as a separate <fact> XML tag\n5. Do not include opinions, summaries, or interpretations - only extract explicit information\n6. Do not duplicate facts that are already in the existing facts list\n\n<existing_facts>\n{{ existing_facts }}\n</existing_facts>\n\nReturn ONLY the condensed facts in this exact format:\n<facts>\n  <fact>Specific fact 1</fact>\n  <fact>Specific fact 2</fact>\n  <!-- More facts as needed -->\n</facts>\n\nIf no new facts are present, return: <facts></facts>')`  
Source code in `llama-index-core/llama_index/core/memory/memory_blocks/fact.py`

| ```
class FactExtractionMemoryBlock(BaseMemoryBlock[str]):
    """
    A memory block that extracts key facts from conversation history using an LLM.

    This block identifies and stores discrete facts disclosed during the conversation,
    structuring them in XML format for easy parsing and retrieval.
    """

    name: str = Field(
        default="ExtractedFacts", description="The name of the memory block."
    )
    llm: LLM = Field(
        default_factory=get_default_llm,
        description="The LLM to use for fact extraction.",
    )
    facts: List[str] = Field(
        default_factory=list,
        description="List of extracted facts from the conversation.",
    )
    max_facts: int = Field(
        default=50, description="The maximum number of facts to store."
    )
    fact_extraction_prompt_template: BasePromptTemplate = Field(
        default=DEFAULT_FACT_EXTRACT_PROMPT,
        description="Template for the fact extraction prompt.",
    )
    fact_condense_prompt_template: BasePromptTemplate = Field(
        default=DEFAULT_FACT_CONDENSE_PROMPT,
        description="Template for the fact condense prompt.",
    )

    @field_validator("fact_extraction_prompt_template", mode="before")
    @classmethod
    def validate_fact_extraction_prompt_template(
        cls, v: Union[str, BasePromptTemplate]
    ) -> BasePromptTemplate:
        if isinstance(v, str):
            if "{{" in v and "}}" in v:
                v = RichPromptTemplate(v)
            else:
                v = PromptTemplate(v)
        return v

    async def _aget(
        self, messages: Optional[List[ChatMessage]] = None, **block_kwargs: Any
    ) -> str:
        """Return the current facts as formatted text."""
        if not self.facts:
            return ""

        return "\n".join([f"<fact>{fact}</fact>" for fact in self.facts])

    async def _aput(self, messages: List[ChatMessage]) -> None:
        """Extract facts from new messages and add them to the facts list."""
        # Skip if no messages
        if not messages:
            return

        # Format existing facts for the prompt
        existing_facts_text = ""
        if self.facts:
            existing_facts_text = "\n".join(
                [f"<fact>{fact}</fact>" for fact in self.facts]
            )

        # Create the prompt
        prompt_messages = self.fact_extraction_prompt_template.format_messages(
            existing_facts=existing_facts_text,
        )

        # Get the facts extraction
        response = await self.llm.achat(messages=[*messages, *prompt_messages])

        # Parse the XML response to extract facts
        facts_text = response.message.content or ""
        new_facts = self._parse_facts_xml(facts_text)

        # Add new facts to the list, avoiding exact-match duplicates
        for fact in new_facts:
            if fact not in self.facts:
                self.facts.append(fact)

        # Condense the facts if they exceed the max_facts
        if len(self.facts) > self.max_facts:
            existing_facts_text = "\n".join(
                [f"<fact>{fact}</fact>" for fact in self.facts]
            )

            prompt_messages = self.fact_condense_prompt_template.format_messages(
                existing_facts=existing_facts_text,
                max_facts=self.max_facts,
            )
            response = await self.llm.achat(messages=[*messages, *prompt_messages])
            new_facts = self._parse_facts_xml(response.message.content or "")
            self.facts = new_facts

    def _parse_facts_xml(self, xml_text: str) -> List[str]:
        """Parse facts from XML format."""
        facts = []

        # Extract content between <fact> tags
        pattern = r"<fact>(.*?)</fact>"
        matches = re.findall(pattern, xml_text, re.DOTALL)

        # Clean up extracted facts
        for match in matches:
            fact = match.strip()
            if fact:
                facts.append(fact)

        return facts

```
  
---|---
