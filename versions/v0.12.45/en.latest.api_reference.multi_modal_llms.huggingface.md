# Huggingface
##  HuggingFaceMultiModal #
Bases: `MultiModalLLM`
This class provides a base implementation for interacting with HuggingFace multi-modal models. It handles model initialization, input preparation, and text/image-based interaction.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-huggingface/llama_index/multi_modal_llms/huggingface/base.py`

| ```
class HuggingFaceMultiModal(MultiModalLLM):
    """
    This class provides a base implementation for interacting with HuggingFace multi-modal models.
    It handles model initialization, input preparation, and text/image-based interaction.
    """

    model_name: str = Field(
        description="The name of the Hugging Face multi-modal model to use."
    )
    device: str = Field(
        default="cuda" if torch.cuda.is_available() else "cpu",
        description="The device to run the model on.",
    )
    device_map: Union[Dict[str, Any], str] = Field(
        default="auto",
        description="Tell HF accelerate where to put each layer of the model. In auto mode, HF accelerate determines this on it's own",
    )
    torch_dtype: Any = Field(
        default=torch.float16 if torch.cuda.is_available() else torch.float32,
        description="The torch dtype to use.",
    )
    trust_remote_code: bool = Field(
        default=False,
        description="Whether to trust remote code when loading the model.",
    )
    context_window: int = Field(
        default=DEFAULT_CONTEXT_WINDOW,
        description="The maximum number of context tokens for the model.",
    )
    max_new_tokens: int = Field(
        default=DEFAULT_NUM_OUTPUTS,
        description="The maximum number of new tokens to generate.",
    )
    temperature: float = Field(
        default=0.0, description="The temperature to use for sampling."
    )
    additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional kwargs for model initialization and generation.",
    )

    _model: Any = PrivateAttr()
    _processor: Any = PrivateAttr()
    _config: Any = PrivateAttr()

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the HuggingFace multi-modal model and processor based on the provided configuration.
        """
        super().__init__(**kwargs)
        try:
            # Load model configuration
            self._config = AutoConfig.from_pretrained(
                self.model_name, trust_remote_code=True
            )
            architecture = self._config.architectures[0]
            AutoModelClass = AutoModelForCausalLM  # Default model class

            # Special cases for specific model architectures
            if "Qwen2VLForConditionalGeneration" in architecture:
                AutoModelClass = Qwen2VLForConditionalGeneration
            if "PaliGemmaForConditionalGeneration" in architecture:
                AutoModelClass = PaliGemmaForConditionalGeneration
            if "MllamaForConditionalGeneration" in architecture:
                AutoModelClass = MllamaForConditionalGeneration

            # Load the model based on the architecture
            self._model = AutoModelClass.from_pretrained(
                self.model_name,
                device_map=self.device_map,
                torch_dtype=self.torch_dtype,
                trust_remote_code=self.trust_remote_code,
                **self.additional_kwargs,
            )
            # Load the processor (for handling text and image inputs)
            self._processor = AutoProcessor.from_pretrained(
                self.model_name, trust_remote_code=self.trust_remote_code
            )
        except Exception as e:
            raise ValueError(f"Failed to initialize the model and processor: {e!s}")

    @classmethod
    def class_name(cls) -> str:
        """Returns the class name for the model."""
        return "HuggingFace_multi_modal_llm"

    @property
    def metadata(self) -> MultiModalLLMMetadata:
        """Multi Modal LLM metadata."""
        return MultiModalLLMMetadata(
            context_window=self.context_window,
            num_output=self.max_new_tokens,
            model_name=self.model_name,
        )

    # each unique model will override it
    def _prepare_messages(
        self, messages: Sequence[ChatMessage], image_documents: Sequence[ImageDocument]
    ) -> Dict[str, Any]:
        """
        Abstract method: Prepares input messages and image documents for the model.
        This must be overridden by subclasses.
        """
        raise NotImplementedError

    # each unique model will override it
    def _generate(self, prepared_inputs: Dict[str, Any]) -> str:
        """
        Abstract method: Generates text based on the prepared inputs.
        This must be overridden by subclasses.
        """
        raise NotImplementedError

    # some models will override it, some won't
    def complete(
        self, prompt: str, image_documents: Sequence[ImageDocument], **kwargs: Any
    ) -> CompletionResponse:
        """
        Completes a task based on a text prompt and optional images.
        The method prepares inputs and generates the corresponding text.
        """
        prepared_inputs = self._prepare_messages(
            [ChatMessage(role="user", content=prompt)], image_documents
        )
        generated_text = self._generate(prepared_inputs)
        return CompletionResponse(text=generated_text)

    # some models will override it, some won't
    def chat(
        self,
        messages: Sequence[ChatMessage],
        image_documents: Sequence[ImageDocument],
        **kwargs: Any,
    ) -> ChatResponse:
        """
        Engages in a chat-style interaction by processing a sequence of messages and optional images.
        """
        prepared_inputs = self._prepare_messages(messages, image_documents)
        generated_text = self._generate(prepared_inputs)
        return ChatResponse(
            message=ChatMessage(role="assistant", content=generated_text),
            raw={"model_output": generated_text},
        )

    async def astream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        raise NotImplementedError(
            "HuggingFaceMultiModal does not support async streaming chat yet."
        )

    async def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseAsyncGen:
        raise NotImplementedError(
            "HuggingFaceMultiModal does not support streaming chat yet."
        )

    async def astream_complete(
        self, prompt: str, image_documents: Sequence[ImageNode], **kwargs: Any
    ) -> CompletionResponseAsyncGen:
        raise NotImplementedError(
            "HuggingFaceMultiModal does not support async streaming completion yet."
        )

    async def acomplete(
        self, prompt: str, image_documents: Sequence[ImageNode], **kwargs: Any
    ) -> CompletionResponse:
        raise NotImplementedError(
            "HuggingFaceMultiModal does not support async completion yet."
        )

    async def achat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponse:
        raise NotImplementedError(
            "HuggingFaceMultiModal does not support async chat yet."
        )

    async def stream_complete(
        self, prompt: str, image_documents: Sequence[ImageNode], **kwargs: Any
    ) -> CompletionResponse:
        raise NotImplementedError(
            "HuggingFaceMultiModal does not support async completion yet."
        )

    # we check the model architecture here
    @classmethod
    def from_model_name(cls, model_name: str, **kwargs: Any) -> "HuggingFaceMultiModal":
        """Checks the model architecture and initializes the model."""
        config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
        # we check the architecture because users would want to use their own finetuned versions of VLMs
        architecture = config.architectures[0]

        if "Phi3VForCausalLM" in architecture:
            return Phi35VisionMultiModal(model_name=model_name, **kwargs)
        elif "Florence2ForConditionalGeneration" in architecture:
            return Florence2MultiModal(model_name=model_name, **kwargs)
        elif "Qwen2VLForConditionalGeneration" in architecture:
            return Qwen2VisionMultiModal(model_name=model_name, **kwargs)
        elif "PaliGemmaForConditionalGeneration" in architecture:
            return PaliGemmaMultiModal(model_name=model_name, **kwargs)
        elif "MllamaForConditionalGeneration" in architecture:
            return LlamaMultiModal(model_name=model_name, **kwargs)
        else:
            raise ValueError(
                f"Unsupported model architecture: {architecture}. "
                f"We currently support: {', '.join(SUPPORTED_VLMS)}"
            )

```
  
---|---  
###  metadata `property` #
```
metadata: MultiModalLLMMetadata

```

Multi Modal LLM metadata.
###  class_name `classmethod` #
```
class_name() -> str

```

Returns the class name for the model.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-huggingface/llama_index/multi_modal_llms/huggingface/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Returns the class name for the model."""
    return "HuggingFace_multi_modal_llm"

```
  
---|---  
###  complete #
```
complete(prompt: str, image_documents: Sequence[ImageDocument], **kwargs: Any) -> CompletionResponse

```

Completes a task based on a text prompt and optional images. The method prepares inputs and generates the corresponding text.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-huggingface/llama_index/multi_modal_llms/huggingface/base.py`

| ```
def complete(
    self, prompt: str, image_documents: Sequence[ImageDocument], **kwargs: Any
) -> CompletionResponse:
    """
    Completes a task based on a text prompt and optional images.
    The method prepares inputs and generates the corresponding text.
    """
    prepared_inputs = self._prepare_messages(
        [ChatMessage(role="user", content=prompt)], image_documents
    )
    generated_text = self._generate(prepared_inputs)
    return CompletionResponse(text=generated_text)

```
  
---|---  
###  chat #
```
chat(messages: Sequence[ChatMessage], image_documents: Sequence[ImageDocument], **kwargs: Any) -> ChatResponse

```

Engages in a chat-style interaction by processing a sequence of messages and optional images.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-huggingface/llama_index/multi_modal_llms/huggingface/base.py`

| ```
def chat(
    self,
    messages: Sequence[ChatMessage],
    image_documents: Sequence[ImageDocument],
    **kwargs: Any,
) -> ChatResponse:
    """
    Engages in a chat-style interaction by processing a sequence of messages and optional images.
    """
    prepared_inputs = self._prepare_messages(messages, image_documents)
    generated_text = self._generate(prepared_inputs)
    return ChatResponse(
        message=ChatMessage(role="assistant", content=generated_text),
        raw={"model_output": generated_text},
    )

```
  
---|---  
###  from_model_name `classmethod` #
```
from_model_name(model_name: str, **kwargs: Any) -> HuggingFaceMultiModal

```

Checks the model architecture and initializes the model.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-huggingface/llama_index/multi_modal_llms/huggingface/base.py`

| ```
@classmethod
def from_model_name(cls, model_name: str, **kwargs: Any) -> "HuggingFaceMultiModal":
    """Checks the model architecture and initializes the model."""
    config = AutoConfig.from_pretrained(model_name, trust_remote_code=True)
    # we check the architecture because users would want to use their own finetuned versions of VLMs
    architecture = config.architectures[0]

    if "Phi3VForCausalLM" in architecture:
        return Phi35VisionMultiModal(model_name=model_name, **kwargs)
    elif "Florence2ForConditionalGeneration" in architecture:
        return Florence2MultiModal(model_name=model_name, **kwargs)
    elif "Qwen2VLForConditionalGeneration" in architecture:
        return Qwen2VisionMultiModal(model_name=model_name, **kwargs)
    elif "PaliGemmaForConditionalGeneration" in architecture:
        return PaliGemmaMultiModal(model_name=model_name, **kwargs)
    elif "MllamaForConditionalGeneration" in architecture:
        return LlamaMultiModal(model_name=model_name, **kwargs)
    else:
        raise ValueError(
            f"Unsupported model architecture: {architecture}. "
            f"We currently support: {', '.join(SUPPORTED_VLMS)}"
        )

```
  
---|---
