# Index
Response builder class.
This class provides general functions for taking in a set of text and generating a response.
Will support different modes, from 1) stuffing chunks into prompt, 2) create and refine separately over each chunk, 3) tree summarization.
##  BaseSynthesizer #
Bases: `PromptMixin`, `DispatcherSpanMixin`
Response builder class.
Source code in `llama-index-core/llama_index/core/response_synthesizers/base.py`

| ```
class BaseSynthesizer(PromptMixin, DispatcherSpanMixin):
    """Response builder class."""

    def __init__(
        self,
        llm: Optional[LLM] = None,
        callback_manager: Optional[CallbackManager] = None,
        prompt_helper: Optional[PromptHelper] = None,
        streaming: bool = False,
        output_cls: Optional[Type[BaseModel]] = None,
    ) -> None:
        """Init params."""
        self._llm = llm or Settings.llm

        if callback_manager:
            self._llm.callback_manager = callback_manager

        self._callback_manager = callback_manager or Settings.callback_manager

        self._prompt_helper = (
            prompt_helper
            or Settings._prompt_helper
            or PromptHelper.from_llm_metadata(
                self._llm.metadata,
            )
        )

        self._streaming = streaming
        self._output_cls = output_cls

    def _get_prompt_modules(self) -> Dict[str, Any]:
        """Get prompt modules."""
        # TODO: keep this for now since response synthesizers don't generally have sub-modules
        return {}

    @property
    def callback_manager(self) -> CallbackManager:
        return self._callback_manager

    @callback_manager.setter
    def callback_manager(self, callback_manager: CallbackManager) -> None:
        """Set callback manager."""
        self._callback_manager = callback_manager
        # TODO: please fix this later
        self._callback_manager = callback_manager
        self._llm.callback_manager = callback_manager

    @abstractmethod
    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        """Get response."""
        ...

    @abstractmethod
    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        """Get response."""
        ...

    def _log_prompt_and_response(
        self,
        formatted_prompt: str,
        response: RESPONSE_TEXT_TYPE,
        log_prefix: str = "",
    ) -> None:
        """Log prompt and response from LLM."""
        logger.debug(f"> {log_prefix} prompt template: {formatted_prompt}")
        logger.debug(f"> {log_prefix} response: {response}")

    def _get_metadata_for_response(
        self,
        nodes: List[BaseNode],
    ) -> Optional[Dict[str, Any]]:
        """Get metadata for response."""
        return {node.node_id: node.metadata for node in nodes}

    def _prepare_response_output(
        self,
        response_str: Optional[RESPONSE_TEXT_TYPE],
        source_nodes: List[NodeWithScore],
    ) -> RESPONSE_TYPE:
        """Prepare response object from response string."""
        response_metadata = self._get_metadata_for_response(
            [node_with_score.node for node_with_score in source_nodes]
        )

        if isinstance(self._llm, StructuredLLM):
            # convert string to output_cls
            output = self._llm.output_cls.model_validate_json(str(response_str))
            return PydanticResponse(
                output,
                source_nodes=source_nodes,
                metadata=response_metadata,
            )

        if isinstance(response_str, str):
            return Response(
                response_str,
                source_nodes=source_nodes,
                metadata=response_metadata,
            )
        if isinstance(response_str, Generator):
            return StreamingResponse(
                response_str,
                source_nodes=source_nodes,
                metadata=response_metadata,
            )
        if isinstance(response_str, AsyncGenerator):
            return AsyncStreamingResponse(
                response_str,
                source_nodes=source_nodes,
                metadata=response_metadata,
            )

        if self._output_cls is not None and isinstance(response_str, self._output_cls):
            return PydanticResponse(
                response_str, source_nodes=source_nodes, metadata=response_metadata
            )

        raise ValueError(
            f"Response must be a string or a generator. Found {type(response_str)}"
        )

    @dispatcher.span
    def synthesize(
        self,
        query: QueryTextType,
        nodes: List[NodeWithScore],
        additional_source_nodes: Optional[Sequence[NodeWithScore]] = None,
        **response_kwargs: Any,
    ) -> RESPONSE_TYPE:
        dispatcher.event(
            SynthesizeStartEvent(
                query=query,
            )
        )

        if len(nodes) == 0:
            if self._streaming:
                empty_response_stream = StreamingResponse(
                    response_gen=empty_response_generator()
                )
                dispatcher.event(
                    SynthesizeEndEvent(
                        query=query,
                        response=empty_response_stream,
                    )
                )
                return empty_response_stream
            else:
                empty_response = Response("Empty Response")
                dispatcher.event(
                    SynthesizeEndEvent(
                        query=query,
                        response=empty_response,
                    )
                )
                return empty_response

        if isinstance(query, str):
            query = QueryBundle(query_str=query)

        with self._callback_manager.event(
            CBEventType.SYNTHESIZE,
            payload={EventPayload.QUERY_STR: query.query_str},
        ) as event:
            response_str = self.get_response(
                query_str=query.query_str,
                text_chunks=[
                    n.node.get_content(metadata_mode=MetadataMode.LLM) for n in nodes
                ],
                **response_kwargs,
            )

            additional_source_nodes = additional_source_nodes or []
            source_nodes = list(nodes) + list(additional_source_nodes)

            response = self._prepare_response_output(response_str, source_nodes)

            event.on_end(payload={EventPayload.RESPONSE: response})

        dispatcher.event(
            SynthesizeEndEvent(
                query=query,
                response=response,
            )
        )
        return response

    @dispatcher.span
    async def asynthesize(
        self,
        query: QueryTextType,
        nodes: List[NodeWithScore],
        additional_source_nodes: Optional[Sequence[NodeWithScore]] = None,
        **response_kwargs: Any,
    ) -> RESPONSE_TYPE:
        dispatcher.event(
            SynthesizeStartEvent(
                query=query,
            )
        )
        if len(nodes) == 0:
            if self._streaming:
                empty_response_stream = AsyncStreamingResponse(
                    response_gen=empty_response_agenerator()
                )
                dispatcher.event(
                    SynthesizeEndEvent(
                        query=query,
                        response=empty_response_stream,
                    )
                )
                return empty_response_stream
            else:
                empty_response = Response("Empty Response")
                dispatcher.event(
                    SynthesizeEndEvent(
                        query=query,
                        response=empty_response,
                    )
                )
                return empty_response

        if isinstance(query, str):
            query = QueryBundle(query_str=query)

        with self._callback_manager.event(
            CBEventType.SYNTHESIZE,
            payload={EventPayload.QUERY_STR: query.query_str},
        ) as event:
            response_str = await self.aget_response(
                query_str=query.query_str,
                text_chunks=[
                    n.node.get_content(metadata_mode=MetadataMode.LLM) for n in nodes
                ],
                **response_kwargs,
            )

            additional_source_nodes = additional_source_nodes or []
            source_nodes = list(nodes) + list(additional_source_nodes)

            response = self._prepare_response_output(response_str, source_nodes)

            event.on_end(payload={EventPayload.RESPONSE: response})

        dispatcher.event(
            SynthesizeEndEvent(
                query=query,
                response=response,
            )
        )
        return response

```
  
---|---  
###  get_response `abstractmethod` #
```
get_response(query_str: str, text_chunks: Sequence[str], **response_kwargs: Any) -> RESPONSE_TEXT_TYPE

```

Get response.
Source code in `llama-index-core/llama_index/core/response_synthesizers/base.py`

| ```
@abstractmethod
def get_response(
    self,
    query_str: str,
    text_chunks: Sequence[str],
    **response_kwargs: Any,
) -> RESPONSE_TEXT_TYPE:
    """Get response."""
    ...

```
  
---|---  
###  aget_response `abstractmethod` `async` #
```
aget_response(query_str: str, text_chunks: Sequence[str], **response_kwargs: Any) -> RESPONSE_TEXT_TYPE

```

Get response.
Source code in `llama-index-core/llama_index/core/response_synthesizers/base.py`

| ```
@abstractmethod
async def aget_response(
    self,
    query_str: str,
    text_chunks: Sequence[str],
    **response_kwargs: Any,
) -> RESPONSE_TEXT_TYPE:
    """Get response."""
    ...

```
  
---|---  
##  get_response_synthesizer #
```
get_response_synthesizer(llm: Optional[LLM] = None, prompt_helper: Optional[PromptHelper] = None, text_qa_template: Optional[BasePromptTemplate] = None, refine_template: Optional[BasePromptTemplate] = None, summary_template: Optional[BasePromptTemplate] = None, simple_template: Optional[BasePromptTemplate] = None, response_mode: ResponseMode = COMPACT, callback_manager: Optional[CallbackManager] = None, use_async: bool = False, streaming: bool = False, structured_answer_filtering: bool = False, output_cls: Optional[Type[BaseModel]] = None, program_factory: Optional[Callable[[BasePromptTemplate], BasePydanticProgram]] = None, verbose: bool = False) -> BaseSynthesizer

```

Get a response synthesizer.
Source code in `llama-index-core/llama_index/core/response_synthesizers/factory.py`

| ```
def get_response_synthesizer(
    llm: Optional[LLM] = None,
    prompt_helper: Optional[PromptHelper] = None,
    text_qa_template: Optional[BasePromptTemplate] = None,
    refine_template: Optional[BasePromptTemplate] = None,
    summary_template: Optional[BasePromptTemplate] = None,
    simple_template: Optional[BasePromptTemplate] = None,
    response_mode: ResponseMode = ResponseMode.COMPACT,
    callback_manager: Optional[CallbackManager] = None,
    use_async: bool = False,
    streaming: bool = False,
    structured_answer_filtering: bool = False,
    output_cls: Optional[Type[BaseModel]] = None,
    program_factory: Optional[
        Callable[[BasePromptTemplate], BasePydanticProgram]
    ] = None,
    verbose: bool = False,
) -> BaseSynthesizer:
    """Get a response synthesizer."""
    text_qa_template = text_qa_template or DEFAULT_TEXT_QA_PROMPT_SEL
    refine_template = refine_template or DEFAULT_REFINE_PROMPT_SEL
    simple_template = simple_template or DEFAULT_SIMPLE_INPUT_PROMPT
    summary_template = summary_template or DEFAULT_TREE_SUMMARIZE_PROMPT_SEL

    callback_manager = callback_manager or Settings.callback_manager
    llm = llm or Settings.llm
    prompt_helper = (
        prompt_helper
        or Settings._prompt_helper
        or PromptHelper.from_llm_metadata(
            llm.metadata,
        )
    )

    if response_mode == ResponseMode.REFINE:
        return Refine(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            text_qa_template=text_qa_template,
            refine_template=refine_template,
            output_cls=output_cls,
            streaming=streaming,
            structured_answer_filtering=structured_answer_filtering,
            program_factory=program_factory,
            verbose=verbose,
        )
    elif response_mode == ResponseMode.COMPACT:
        return CompactAndRefine(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            text_qa_template=text_qa_template,
            refine_template=refine_template,
            output_cls=output_cls,
            streaming=streaming,
            structured_answer_filtering=structured_answer_filtering,
            program_factory=program_factory,
            verbose=verbose,
        )
    elif response_mode == ResponseMode.TREE_SUMMARIZE:
        return TreeSummarize(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            summary_template=summary_template,
            output_cls=output_cls,
            streaming=streaming,
            use_async=use_async,
            verbose=verbose,
        )
    elif response_mode == ResponseMode.SIMPLE_SUMMARIZE:
        return SimpleSummarize(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            text_qa_template=text_qa_template,
            streaming=streaming,
        )
    elif response_mode == ResponseMode.GENERATION:
        return Generation(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            simple_template=simple_template,
            streaming=streaming,
        )
    elif response_mode == ResponseMode.ACCUMULATE:
        return Accumulate(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            text_qa_template=text_qa_template,
            output_cls=output_cls,
            streaming=streaming,
            use_async=use_async,
        )
    elif response_mode == ResponseMode.COMPACT_ACCUMULATE:
        return CompactAndAccumulate(
            llm=llm,
            callback_manager=callback_manager,
            prompt_helper=prompt_helper,
            text_qa_template=text_qa_template,
            output_cls=output_cls,
            streaming=streaming,
            use_async=use_async,
        )
    elif response_mode == ResponseMode.NO_TEXT:
        return NoText(
            callback_manager=callback_manager,
            streaming=streaming,
        )
    elif response_mode == ResponseMode.CONTEXT_ONLY:
        return ContextOnly(
            callback_manager=callback_manager,
            streaming=streaming,
        )
    else:
        raise ValueError(f"Unknown mode: {response_mode}")

```
  
---|---  
##  ResponseMode #
Bases: `str`, `Enum`
Response modes of the response builder (and synthesizer).
Source code in `llama-index-core/llama_index/core/response_synthesizers/type.py`

| ```
class ResponseMode(str, Enum):
    """Response modes of the response builder (and synthesizer)."""

    REFINE = "refine"
    """
    Refine is an iterative way of generating a response.
    We first use the context in the first node, along with the query, to generate an \
    initial answer.
    We then pass this answer, the query, and the context of the second node as input \
    into a “refine prompt” to generate a refined answer. We refine through N-1 nodes, \
    where N is the total number of nodes.
    """

    COMPACT = "compact"
    """
    Compact and refine mode first combine text chunks into larger consolidated chunks \
    that more fully utilize the available context window, then refine answers \
    across them.
    This mode is faster than refine since we make fewer calls to the LLM.
    """

    SIMPLE_SUMMARIZE = "simple_summarize"
    """
    Merge all text chunks into one, and make a LLM call.
    This will fail if the merged text chunk exceeds the context window size.
    """

    TREE_SUMMARIZE = "tree_summarize"
    """
    Build a tree index over the set of candidate nodes, with a summary prompt seeded \
    with the query.
    The tree is built in a bottoms-up fashion, and in the end the root node is \
    returned as the response
    """

    GENERATION = "generation"
    """Ignore context, just use LLM to generate a response."""

    NO_TEXT = "no_text"
    """Return the retrieved context nodes, without synthesizing a final response."""

    CONTEXT_ONLY = "context_only"
    """Returns a concatenated string of all text chunks."""

    ACCUMULATE = "accumulate"
    """Synthesize a response for each text chunk, and then return the concatenation."""

    COMPACT_ACCUMULATE = "compact_accumulate"
    """
    Compact and accumulate mode first combine text chunks into larger consolidated \
    chunks that more fully utilize the available context window, then accumulate \
    answers for each of them and finally return the concatenation.
    This mode is faster than accumulate since we make fewer calls to the LLM.
    """

```
  
---|---  
###  REFINE `class-attribute` `instance-attribute` #
```
REFINE = 'refine'

```

Refine is an iterative way of generating a response. We first use the context in the first node, along with the query, to generate an initial answer. We then pass this answer, the query, and the context of the second node as input into a “refine prompt” to generate a refined answer. We refine through N-1 nodes, where N is the total number of nodes.
###  COMPACT `class-attribute` `instance-attribute` #
```
COMPACT = 'compact'

```

Compact and refine mode first combine text chunks into larger consolidated chunks that more fully utilize the available context window, then refine answers across them. This mode is faster than refine since we make fewer calls to the LLM.
###  SIMPLE_SUMMARIZE `class-attribute` `instance-attribute` #
```
SIMPLE_SUMMARIZE = 'simple_summarize'

```

Merge all text chunks into one, and make a LLM call. This will fail if the merged text chunk exceeds the context window size.
###  TREE_SUMMARIZE `class-attribute` `instance-attribute` #
```
TREE_SUMMARIZE = 'tree_summarize'

```

Build a tree index over the set of candidate nodes, with a summary prompt seeded with the query. The tree is built in a bottoms-up fashion, and in the end the root node is returned as the response
###  GENERATION `class-attribute` `instance-attribute` #
```
GENERATION = 'generation'

```

Ignore context, just use LLM to generate a response.
###  NO_TEXT `class-attribute` `instance-attribute` #
```
NO_TEXT = 'no_text'

```

Return the retrieved context nodes, without synthesizing a final response.
###  CONTEXT_ONLY `class-attribute` `instance-attribute` #
```
CONTEXT_ONLY = 'context_only'

```

Returns a concatenated string of all text chunks.
###  ACCUMULATE `class-attribute` `instance-attribute` #
```
ACCUMULATE = 'accumulate'

```

Synthesize a response for each text chunk, and then return the concatenation.
###  COMPACT_ACCUMULATE `class-attribute` `instance-attribute` #
```
COMPACT_ACCUMULATE = 'compact_accumulate'

```

Compact and accumulate mode first combine text chunks into larger consolidated chunks that more fully utilize the available context window, then accumulate answers for each of them and finally return the concatenation. This mode is faster than accumulate since we make fewer calls to the LLM.
