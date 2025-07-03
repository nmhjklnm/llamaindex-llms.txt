# Index
##  MultiModalLLMMetadata #
Bases: `BaseModel`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`context_window` |  `int | None` |  Total number of tokens the model can be input when generating a response. |  `3900`  
`num_output` |  `int | None` |  Number of tokens the model can output when generating a response. |  `256`  
`num_input_files` |  `int | None` |  Number of input files the model can take when generating a response. |  `10`  
`is_function_calling_model` |  `bool | None` |  Set True if the model supports function calling messages, similar to OpenAI's function calling API. For example, converting 'Email Anya to see if she wants to get coffee next Friday' to a function call like `send_email(to: string, body: string)`. |  `False`  
`model_name` |  `str` |  The model's name used for logging, testing, and sanity checking. For some models this can be automatically discerned. For other models, like locally loaded models, this must be manually specified. |  `'unknown'`  
`is_chat_model` |  `bool` |  Set True if the model exposes a chat interface (i.e. can be passed a sequence of messages, rather than text), like OpenAI's /v1/chat/completions endpoint. |  `False`  
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
class MultiModalLLMMetadata(BaseModel):
    model_config = ConfigDict(protected_namespaces=("pydantic_model_",))
    context_window: Optional[int] = Field(
        default=DEFAULT_CONTEXT_WINDOW,
        description=(
            "Total number of tokens the model can be input when generating a response."
        ),
    )
    num_output: Optional[int] = Field(
        default=DEFAULT_NUM_OUTPUTS,
        description="Number of tokens the model can output when generating a response.",
    )
    num_input_files: Optional[int] = Field(
        default=DEFAULT_NUM_INPUT_FILES,
        description="Number of input files the model can take when generating a response.",
    )
    is_function_calling_model: Optional[bool] = Field(
        default=False,
        # SEE: https://openai.com/blog/function-calling-and-other-api-updates
        description=(
            "Set True if the model supports function calling messages, similar to"
            " OpenAI's function calling API. For example, converting 'Email Anya to"
            " see if she wants to get coffee next Friday' to a function call like"
            " `send_email(to: string, body: string)`."
        ),
    )
    model_name: str = Field(
        default="unknown",
        description=(
            "The model's name used for logging, testing, and sanity checking. For some"
            " models this can be automatically discerned. For other models, like"
            " locally loaded models, this must be manually specified."
        ),
    )

    is_chat_model: bool = Field(
        default=False,
        description=(
            "Set True if the model exposes a chat interface (i.e. can be passed a"
            " sequence of messages, rather than text), like OpenAI's"
            " /v1/chat/completions endpoint."
        ),
    )

```
  
---|---  
##  MultiModalLLM #
Bases: `ChainableMixin`, `BaseComponent`, `DispatcherSpanMixin`
Multi-Modal LLM interface.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`callback_manager` |  `CallbackManager` |  Callback manager that handles callbacks for events within LlamaIndex. The callback manager provides a way to call handlers on event starts/ends. Additionally, the callback manager traces the current stack of events. It does this by using a few key attributes. - trace_stack - The current stack of events that have not ended yet. When an event ends, it's removed from the stack. Since this is a contextvar, it is unique to each thread/task. - trace_map - A mapping of event ids to their children events. On the start of events, the bottom of the trace stack is used as the current parent event for the trace map. - trace_id - A simple name for the current trace, usually denoting the entrypoint (query, index_construction, insert, etc.) Args: handlers (List[BaseCallbackHandler]): list of handlers to use. Usage: with callback_manager.event(CBEventType.QUERY) as event: event.on_start(payload={key, val}) ... event.on_end(payload={key, val}) |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
class MultiModalLLM(ChainableMixin, BaseComponent, DispatcherSpanMixin):
    """Multi-Modal LLM interface."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    callback_manager: CallbackManager = Field(
        default_factory=CallbackManager, exclude=True
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Help static checkers understand this class hierarchy
        super().__init__(*args, **kwargs)

    @property
    @abstractmethod
    def metadata(self) -> MultiModalLLMMetadata:
        """Multi-Modal LLM metadata."""

    @abstractmethod
    def complete(
        self, prompt: str, image_documents: List[ImageNode], **kwargs: Any
    ) -> CompletionResponse:
        """Completion endpoint for Multi-Modal LLM."""

    @abstractmethod
    def stream_complete(
        self, prompt: str, image_documents: List[ImageNode], **kwargs: Any
    ) -> CompletionResponseGen:
        """Streaming completion endpoint for Multi-Modal LLM."""

    @abstractmethod
    def chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        """Chat endpoint for Multi-Modal LLM."""

    @abstractmethod
    def stream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponseGen:
        """Stream chat endpoint for Multi-Modal LLM."""

    # ===== Async Endpoints =====

    @abstractmethod
    async def acomplete(
        self, prompt: str, image_documents: List[ImageNode], **kwargs: Any
    ) -> CompletionResponse:
        """Async completion endpoint for Multi-Modal LLM."""

    @abstractmethod
    async def astream_complete(
        self, prompt: str, image_documents: List[ImageNode], **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        """Async streaming completion endpoint for Multi-Modal LLM."""

    @abstractmethod
    async def achat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        """Async chat endpoint for Multi-Modal LLM."""

    @abstractmethod
    async def astream_chat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponseAsyncGen:
        """Async streaming chat endpoint for Multi-Modal LLM."""

    def _as_query_component(self, **kwargs: Any) -> QueryComponent:
        """Return query component."""
        if self.metadata.is_chat_model:
            # TODO: we don't have a separate chat component
            return MultiModalCompleteComponent(multi_modal_llm=self, **kwargs)
        else:
            return MultiModalCompleteComponent(multi_modal_llm=self, **kwargs)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        The callback decorators installs events, so they must be applied before
        the span decorators, otherwise the spans wouldn't contain the events.
        """
        for attr in (
            "complete",
            "acomplete",
            "stream_complete",
            "astream_complete",
            "chat",
            "achat",
            "stream_chat",
            "astream_chat",
        ):
            if callable(method := cls.__dict__.get(attr)):
                if attr.endswith("chat"):
                    setattr(cls, attr, llm_chat_callback()(method))
                else:
                    setattr(cls, attr, llm_completion_callback()(method))
        super().__init_subclass__(**kwargs)

```
  
---|---  
###  metadata `abstractmethod` `property` #
```
metadata: MultiModalLLMMetadata

```

Multi-Modal LLM metadata.
###  complete `abstractmethod` #
```
complete(prompt: str, image_documents: List[ImageNode], **kwargs: Any) -> CompletionResponse

```

Completion endpoint for Multi-Modal LLM.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
@abstractmethod
def complete(
    self, prompt: str, image_documents: List[ImageNode], **kwargs: Any
) -> CompletionResponse:
    """Completion endpoint for Multi-Modal LLM."""

```
  
---|---  
###  stream_complete `abstractmethod` #
```
stream_complete(prompt: str, image_documents: List[ImageNode], **kwargs: Any) -> CompletionResponseGen

```

Streaming completion endpoint for Multi-Modal LLM.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
@abstractmethod
def stream_complete(
    self, prompt: str, image_documents: List[ImageNode], **kwargs: Any
) -> CompletionResponseGen:
    """Streaming completion endpoint for Multi-Modal LLM."""

```
  
---|---  
###  chat `abstractmethod` #
```
chat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse

```

Chat endpoint for Multi-Modal LLM.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
@abstractmethod
def chat(
    self,
    messages: Sequence[ChatMessage],
    **kwargs: Any,
) -> ChatResponse:
    """Chat endpoint for Multi-Modal LLM."""

```
  
---|---  
###  stream_chat `abstractmethod` #
```
stream_chat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseGen

```

Stream chat endpoint for Multi-Modal LLM.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
@abstractmethod
def stream_chat(
    self,
    messages: Sequence[ChatMessage],
    **kwargs: Any,
) -> ChatResponseGen:
    """Stream chat endpoint for Multi-Modal LLM."""

```
  
---|---  
###  acomplete `abstractmethod` `async` #
```
acomplete(prompt: str, image_documents: List[ImageNode], **kwargs: Any) -> CompletionResponse

```

Async completion endpoint for Multi-Modal LLM.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
@abstractmethod
async def acomplete(
    self, prompt: str, image_documents: List[ImageNode], **kwargs: Any
) -> CompletionResponse:
    """Async completion endpoint for Multi-Modal LLM."""

```
  
---|---  
###  astream_complete `abstractmethod` `async` #
```
astream_complete(prompt: str, image_documents: List[ImageNode], **kwargs: Any) -> CompletionResponseAsyncGen

```

Async streaming completion endpoint for Multi-Modal LLM.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
@abstractmethod
async def astream_complete(
    self, prompt: str, image_documents: List[ImageNode], **kwargs: Any
) -> CompletionResponseAsyncGen:
    """Async streaming completion endpoint for Multi-Modal LLM."""

```
  
---|---  
###  achat `abstractmethod` `async` #
```
achat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse

```

Async chat endpoint for Multi-Modal LLM.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
@abstractmethod
async def achat(
    self,
    messages: Sequence[ChatMessage],
    **kwargs: Any,
) -> ChatResponse:
    """Async chat endpoint for Multi-Modal LLM."""

```
  
---|---  
###  astream_chat `abstractmethod` `async` #
```
astream_chat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseAsyncGen

```

Async streaming chat endpoint for Multi-Modal LLM.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
@abstractmethod
async def astream_chat(
    self,
    messages: Sequence[ChatMessage],
    **kwargs: Any,
) -> ChatResponseAsyncGen:
    """Async streaming chat endpoint for Multi-Modal LLM."""

```
  
---|---  
##  BaseMultiModalComponent #
Bases: `QueryComponent`
Base LLM component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`multi_modal_llm` |  `MultiModalLLM` |  LLM |  _required_  
`streaming` |  `bool` |  Streaming mode |  `False`  
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
class BaseMultiModalComponent(QueryComponent):
    """Base LLM component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    multi_modal_llm: MultiModalLLM = Field(..., description="LLM")
    streaming: bool = Field(default=False, description="Streaming mode")

    def set_callback_manager(self, callback_manager: Any) -> None:
        """Set callback manager."""

```
  
---|---  
###  set_callback_manager #
```
set_callback_manager(callback_manager: Any) -> None

```

Set callback manager.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
def set_callback_manager(self, callback_manager: Any) -> None:
    """Set callback manager."""

```
  
---|---  
##  MultiModalCompleteComponent #
Bases: `BaseMultiModalComponent`
Multi-modal completion component.
Source code in `llama-index-core/llama_index/core/multi_modal_llms/base.py`

| ```
class MultiModalCompleteComponent(BaseMultiModalComponent):
    """Multi-modal completion component."""

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        if "prompt" not in input:
            raise ValueError("Prompt must be in input dict.")

        # do special check to see if prompt is a list of chat messages
        if isinstance(input["prompt"], get_args(List[ChatMessage])):
            raise NotImplementedError(
                "Chat messages not yet supported as input to multi-modal model."
            )
        else:
            input["prompt"] = validate_and_convert_stringable(input["prompt"])

        # make sure image documents are valid
        if "image_documents" in input:
            if not isinstance(input["image_documents"], list):
                raise ValueError("image_documents must be a list.")
            for doc in input["image_documents"]:
                if not isinstance(doc, (ImageDocument, ImageNode)):
                    raise ValueError(
                        "image_documents must be a list of ImageNode objects."
                    )

        return input

    def _run_component(self, **kwargs: Any) -> Any:
        """Run component."""
        # TODO: support only complete for now
        prompt = kwargs["prompt"]
        image_documents = kwargs.get("image_documents", [])

        response: Any
        if self.streaming:
            response = self.multi_modal_llm.stream_complete(prompt, image_documents)
        else:
            response = self.multi_modal_llm.complete(prompt, image_documents)
        return {"output": response}

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component."""
        # TODO: support only complete for now
        # non-trivial to figure how to support chat/complete/etc.
        prompt = kwargs["prompt"]
        image_documents = kwargs.get("image_documents", [])

        response: Any
        if self.streaming:
            response = await self.multi_modal_llm.astream_complete(
                prompt, image_documents
            )
        else:
            response = await self.multi_modal_llm.acomplete(prompt, image_documents)
        return {"output": response}

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        # TODO: support only complete for now
        return InputKeys.from_keys({"prompt", "image_documents"})

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        return OutputKeys.from_keys({"output"})

```
  
---|---  
###  input_keys `property` #
```
input_keys: InputKeys

```

Input keys.
###  output_keys `property` #
```
output_keys: OutputKeys

```

Output keys.
