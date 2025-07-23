# Modelscope
##  ModelScopeLLM #
Bases: `CustomLLM`
ModelScope LLM.
Source code in `llama-index-integrations/llms/llama-index-llms-modelscope/llama_index/llms/modelscope/base.py`

| ```
class ModelScopeLLM(CustomLLM):
    """ModelScope LLM."""

    model_name: str = Field(
        default=DEFAULT_MODELSCOPE_MODEL,
        description=(
            "The model name to use from ModelScope. "
            "Unused if `model` is passed in directly."
        ),
    )
    model_revision: str = Field(
        default=DEFAULT_MODELSCOPE_MODEL_REVISION,
        description=(
            "The model revision to use from ModelScope. "
            "Unused if `model` is passed in directly."
        ),
    )
    task_name: str = Field(
        default=DEFAULT_MODELSCOPE_TASK,
        description=("The ModelScope task type, for llm use default chat."),
    )
    dtype: str = Field(
        default=DEFAULT_MODELSCOPE_DTYPE,
        description=("The ModelScope task type, for llm use default chat."),
    )
    context_window: int = Field(
        default=DEFAULT_CONTEXT_WINDOW,
        description="The maximum number of tokens available for input.",
        gt=0,
    )
    max_new_tokens: int = Field(
        default=DEFAULT_NUM_OUTPUTS,
        description="The maximum number of tokens to generate.",
        gt=0,
    )
    system_prompt: str = Field(
        default="",
        description=(
            "The system prompt, containing any extra instructions or context. "
            "The model card on ModelScope should specify if this is needed."
        ),
    )
    query_wrapper_prompt: PromptTemplate = Field(
        default=PromptTemplate("{query_str}"),
        description=(
            "The query wrapper prompt, containing the query placeholder. "
            "The model card on ModelScope should specify if this is needed. "
            "Should contain a `{query_str}` placeholder."
        ),
    )
    device_map: str = Field(
        default="auto", description="The device_map to use. Defaults to 'auto'."
    )
    tokenizer_kwargs: dict = Field(
        default_factory=dict, description="The kwargs to pass to the tokenizer."
    )
    model_kwargs: dict = Field(
        default_factory=dict,
        description="The kwargs to pass to the model during initialization.",
    )
    generate_kwargs: dict = Field(
        default_factory=dict,
        description="The kwargs to pass to the model during generation.",
    )

    _pipeline: Any = PrivateAttr()

    def __init__(
        self,
        model_name: str = DEFAULT_MODELSCOPE_MODEL,
        model_revision: str = DEFAULT_MODELSCOPE_MODEL_REVISION,
        task_name: str = DEFAULT_MODELSCOPE_TASK,
        dtype: str = DEFAULT_MODELSCOPE_DTYPE,
        model: Optional[Any] = None,
        device_map: Optional[str] = "auto",
        model_kwargs: Optional[dict] = None,
        generate_kwargs: Optional[dict] = None,
        callback_manager: Optional[CallbackManager] = None,
        pydantic_program_mode: PydanticProgramMode = PydanticProgramMode.DEFAULT,
    ) -> None:
        """Initialize params."""
        model_kwargs = model_kwargs or {}
        if model:
            pipeline = model
        else:
            pipeline = pipeline_builder(
                task=task_name,
                model=model_name,
                model_revision=model_revision,
                llm_first=True,
                torch_dtype=_STR_DTYPE_TO_TORCH_DTYPE[dtype],
                device_map=device_map,
            )

        super().__init__(
            model_kwargs=model_kwargs or {},
            generate_kwargs=generate_kwargs or {},
            callback_manager=callback_manager,
            pydantic_program_mode=pydantic_program_mode,
        )
        self._pipeline = pipeline

    @classmethod
    def class_name(cls) -> str:
        return "ModelScope_LLM"

    @property
    def metadata(self) -> LLMMetadata:
        """LLM metadata."""
        return LLMMetadata(
            context_window=self.context_window,
            num_output=self.max_new_tokens,
            model_name=self.model_name,
            is_chat_model=False,
        )

    @llm_completion_callback()
    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        return text_to_completion_response(self._pipeline(prompt, **kwargs))

    @llm_completion_callback()
    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        yield self.complete(prompt, **kwargs)

    @llm_chat_callback()
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        return modelscope_message_to_chat_response(
            self._pipeline(chat_message_to_modelscope_messages(messages), **kwargs)
        )

    @llm_chat_callback()
    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        yield self.chat(messages, **kwargs)

```
  
---|---  
###  metadata `property` #
```
metadata: LLMMetadata

```

LLM metadata.
