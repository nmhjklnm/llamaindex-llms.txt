# Azure openai
##  AzureOpenAIMultiModal #
Bases: `AzureOpenAI`
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-azure-openai/llama_index/multi_modal_llms/azure_openai/base.py`

| ```
@deprecated(
    reason="This class is deprecated and will be no longer maintained. Use AzureOpenAI from llama-index-llms-azure-openai instead.  See Multi Modal LLMs documentation for a complete guide on migration: https://docs.llamaindex.ai/en/stable/understanding/using_llms/using_llms/#multi-modal-llms",
    version="0.4.1",
)
class AzureOpenAIMultiModal(AzureOpenAI):
    @classmethod
    def class_name(cls) -> str:
        return "azure_openai_multi_modal_llm"

    def _get_multi_modal_chat_message(
        self,
        prompt: str,
        role: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        image_detail: Optional[str] = "low",
        **kwargs: Any,
    ) -> ChatMessage:
        chat_msg = ChatMessage(role=role, content=prompt)
        if not image_documents:
            # if image_documents is empty, return text only chat message
            return chat_msg

        for image_document in image_documents:
            if isinstance(image_document, ImageNode):
                chat_msg.blocks.append(image_node_to_image_block(image_document))
            else:
                chat_msg.blocks.append(image_document)
        return chat_msg

    def complete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponse:
        chat_message = self._get_multi_modal_chat_message(
            prompt=prompt,
            role=MessageRole.USER,
            image_documents=image_documents,
        )
        chat_response = self.chat([chat_message], **kwargs)
        return chat_response_to_completion_response(chat_response)

    def stream_complete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponseGen:
        chat_message = self._get_multi_modal_chat_message(
            prompt=prompt,
            role=MessageRole.USER,
            image_documents=image_documents,
        )
        chat_response = self.stream_chat([chat_message], **kwargs)
        return stream_chat_response_to_completion_response(chat_response)

    # ===== Async Endpoints =====

    async def acomplete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponse:
        chat_message = self._get_multi_modal_chat_message(
            prompt=prompt,
            role=MessageRole.USER,
            image_documents=image_documents,
        )
        chat_response = await self.achat([chat_message], **kwargs)
        return chat_response_to_completion_response(chat_response)

    async def astream_complete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponseAsyncGen:
        chat_message = self._get_multi_modal_chat_message(
            prompt=prompt,
            role=MessageRole.USER,
            image_documents=image_documents,
        )
        chat_response = await self.astream_chat([chat_message], **kwargs)
        return astream_chat_response_to_completion_response(chat_response)

```
  
---|---
