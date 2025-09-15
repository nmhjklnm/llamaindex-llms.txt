# Dashscope
##  DashScopeMultiModal #
Bases: `DashScope`
DashScope LLM.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-dashscope/llama_index/multi_modal_llms/dashscope/base.py`

| ```
@deprecated(
    reason="This package has been deprecated and will no longer be maintained. Please use the package llama-index-llms-dashscopre instead.  See Multi Modal LLMs documentation for a complete guide on migration: https://docs.llamaindex.ai/en/stable/understanding/using_llms/using_llms/#multi-modal-llms",
    version="0.3.1",
)
class DashScopeMultiModal(DashScope):
    """DashScope LLM."""

    model_name: str = Field(
        default=DashScopeMultiModalModels.QWEN_VL_MAX,
        description="The DashScope model to use.",
    )
    incremental_output: Optional[bool] = Field(
        description="Control stream output, If False, the subsequent \
                                                            output will include the content that has been \
                                                            output previously.",
        default=True,
    )
    top_k: Optional[int] = Field(
        description="Sample counter when generate.", default=None
    )
    top_p: Optional[float] = Field(
        description="Sample probability threshold when generate."
    )
    seed: Optional[int] = Field(
        description="Random seed when generate.", default=1234, ge=0
    )
    api_key: Optional[str] = Field(
        default=None, description="The DashScope API key.", exclude=True
    )

    def __init__(
        self,
        model_name: Optional[str] = DashScopeMultiModalModels.QWEN_VL_MAX,
        incremental_output: Optional[int] = True,
        top_k: Optional[int] = None,
        top_p: Optional[float] = None,
        seed: Optional[int] = 1234,
        api_key: Optional[str] = None,
        callback_manager: Optional[CallbackManager] = None,
        **kwargs: Any,
    ):
        super().__init__(
            model_name=model_name,
            incremental_output=incremental_output,
            top_k=top_k,
            top_p=top_p,
            seed=seed,
            api_key=api_key,
            callback_manager=callback_manager,
            **kwargs,
        )

    @classmethod
    def class_name(cls) -> str:
        return "DashScopeMultiModal_LLM"

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            model_name=self.model_name, **DASHSCOPE_MODEL_META[self.model_name]
        )

    def _get_default_parameters(self) -> Dict:
        params: Dict[Any, Any] = {}
        params["incremental_output"] = self.incremental_output
        if self.top_k is not None:
            params["top_k"] = self.top_k

        if self.top_p is not None:
            params["top_p"] = self.top_p
        if self.seed is not None:
            params["seed"] = self.seed

        return params

    def _get_input_parameters(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> Tuple[ChatMessage, Dict]:
        parameters = self._get_default_parameters()
        parameters.update(kwargs)
        parameters["stream"] = False
        if image_documents is None:
            message = ChatMessage(
                role=MessageRole.USER.value, content=[{"text": prompt}]
            )
        else:
            if all(isinstance(doc, ImageNode) for doc in image_documents):
                image_docs = cast(
                    List[ImageBlock],
                    [image_node_to_image_block(node) for node in image_documents],
                )
            else:
                image_docs = cast(List[ImageBlock], image_documents)
            content = []
            for image_document in image_docs:
                content.append({"image": image_document.url})
            content.append({"text": prompt})
            message = ChatMessage(role=MessageRole.USER.value, content=content)
        return message, parameters

    def complete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponse:
        message, parameters = self._get_input_parameters(
            prompt, image_documents, **kwargs
        )
        parameters.pop("incremental_output", None)
        parameters.pop("stream", None)
        messages = chat_message_to_dashscope_multi_modal_messages([message])
        response = call_with_messages(
            model=self.model_name,
            messages=messages,
            api_key=self.api_key,
            parameters=parameters,
        )
        return dashscope_response_to_completion_response(response)

    def stream_complete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponseGen:
        message, parameters = self._get_input_parameters(
            prompt, image_documents, **kwargs
        )
        parameters["incremental_output"] = True
        parameters["stream"] = True
        responses = call_with_messages(
            model=self.model_name,
            messages=chat_message_to_dashscope_multi_modal_messages([message]),
            api_key=self.api_key,
            parameters=parameters,
        )

        def gen() -> CompletionResponseGen:
            content = ""
            for response in responses:
                if response.status_code == HTTPStatus.OK:
                    top_choice = response["output"]["choices"][0]
                    incremental_output = top_choice["message"]["content"]
                    if incremental_output:
                        incremental_output = incremental_output[0]["text"]
                    else:
                        incremental_output = ""

                    content += incremental_output
                    yield CompletionResponse(
                        text=content, delta=incremental_output, raw=response
                    )
                else:
                    yield CompletionResponse(text="", raw=response)
                    return

        return gen()

    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        parameters = self._get_default_parameters()
        parameters.update({**kwargs})
        parameters.pop("stream", None)
        parameters.pop("incremental_output", None)
        response = call_with_messages(
            model=self.model_name,
            messages=chat_message_to_dashscope_multi_modal_messages(messages),
            api_key=self.api_key,
            parameters=parameters,
        )
        return dashscope_response_to_chat_response(response)

    def stream_chat(
        self, messages: Sequence[ChatMessage], **kwargs: Any
    ) -> ChatResponseGen:
        parameters = self._get_default_parameters()
        parameters.update({**kwargs})
        parameters["stream"] = True
        parameters["incremental_output"] = True
        responses = call_with_messages(
            model=self.model_name,
            messages=chat_message_to_dashscope_multi_modal_messages(messages),
            api_key=self.api_key,
            parameters=parameters,
        )

        def gen() -> ChatResponseGen:
            content = ""
            for response in responses:
                if response.status_code == HTTPStatus.OK:
                    top_choice = response["output"]["choices"][0]
                    incremental_output = top_choice["message"]["content"]
                    if incremental_output:
                        incremental_output = incremental_output[0]["text"]
                    else:
                        incremental_output = ""

                    content += incremental_output
                    role = top_choice["message"]["role"]
                    yield ChatResponse(
                        message=ChatMessage(role=role, content=content),
                        delta=incremental_output,
                        raw=response,
                    )
                else:
                    yield ChatResponse(message=ChatMessage(), raw=response)
                    return

        return gen()

    # TODO: use proper async methods
    async def acomplete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponse:
        return self.complete(prompt, image_documents, **kwargs)

    async def achat(
        self,
        messages: Sequence[ChatMessage],
        **kwargs: Any,
    ) -> ChatResponse:
        return self.chat(messages, **kwargs)

```
  
---|---
