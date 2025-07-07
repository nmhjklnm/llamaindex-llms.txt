# Ollama
##  OllamaMultiModal #
Bases: `Ollama`
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-ollama/llama_index/multi_modal_llms/ollama/base.py`

| ```
@deprecated(
    reason="This package has been deprecated and will no longer be maintained. Please use llama-index-llms-ollama instead. See Multi Modal LLMs documentation for a complete guide on migration: https://docs.llamaindex.ai/en/stable/understanding/using_llms/using_llms/#multi-modal-llms",
    version="0.5.1",
)
class OllamaMultiModal(Ollama):
    @classmethod
    def class_name(cls) -> str:
        return "Ollama_multi_modal_llm"

    def _get_messages(
        self, prompt: str, image_documents: Sequence[Union[ImageNode, ImageBlock]]
    ) -> Sequence[ChatMessage]:
        if all(isinstance(doc, ImageNode) for doc in image_documents):
            image_blocks = [
                ImageBlock(
                    image=image_document.image,
                    path=image_document.image_path,
                    url=image_document.image_url,
                    image_mimetype=image_document.image_mimetype,
                )
                for image_document in image_documents
            ]
        else:
            image_blocks = image_documents

        return [
            ChatMessage(
                role=MessageRole.USER,
                blocks=[
                    TextBlock(text=prompt),
                    *image_blocks,
                ],
            )
        ]

    @llm_completion_callback()
    def complete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        formatted: bool = False,
        **kwargs: Any,
    ) -> CompletionResponse:
        """Complete."""
        messages = self._get_messages(prompt, image_documents)
        chat_response = self.chat(messages, **kwargs)
        return chat_response_to_completion_response(chat_response)

    @llm_completion_callback()
    def stream_complete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        formatted: bool = False,
        **kwargs: Any,
    ) -> CompletionResponseGen:
        """Stream complete."""
        messages = self._get_messages(prompt, image_documents)
        stream_chat_response = self.stream_chat(messages, **kwargs)
        return stream_chat_response_to_completion_response(stream_chat_response)

    @llm_completion_callback()
    async def acomplete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponse:
        """Async complete."""
        messages = self._get_messages(prompt, image_documents)
        chat_response = await self.achat(messages, **kwargs)
        return chat_response_to_completion_response(chat_response)

    async def astream_complete(
        self,
        prompt: str,
        image_documents: Sequence[Union[ImageNode, ImageBlock]],
        **kwargs: Any,
    ) -> CompletionResponseAsyncGen:
        """Async stream complete."""
        messages = self._get_messages(prompt, image_documents)
        astream_chat_response = await self.astream_chat(messages, **kwargs)
        return astream_chat_response_to_completion_response(astream_chat_response)

```
  
---|---  
###  complete #
```
complete(prompt: str, image_documents: Sequence[Union[ImageNode, ImageBlock]], formatted: bool = False, **kwargs: Any) -> CompletionResponse

```

Complete.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-ollama/llama_index/multi_modal_llms/ollama/base.py`

| ```
@llm_completion_callback()
def complete(
    self,
    prompt: str,
    image_documents: Sequence[Union[ImageNode, ImageBlock]],
    formatted: bool = False,
    **kwargs: Any,
) -> CompletionResponse:
    """Complete."""
    messages = self._get_messages(prompt, image_documents)
    chat_response = self.chat(messages, **kwargs)
    return chat_response_to_completion_response(chat_response)

```
  
---|---  
###  stream_complete #
```
stream_complete(prompt: str, image_documents: Sequence[Union[ImageNode, ImageBlock]], formatted: bool = False, **kwargs: Any) -> CompletionResponseGen

```

Stream complete.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-ollama/llama_index/multi_modal_llms/ollama/base.py`

| ```
@llm_completion_callback()
def stream_complete(
    self,
    prompt: str,
    image_documents: Sequence[Union[ImageNode, ImageBlock]],
    formatted: bool = False,
    **kwargs: Any,
) -> CompletionResponseGen:
    """Stream complete."""
    messages = self._get_messages(prompt, image_documents)
    stream_chat_response = self.stream_chat(messages, **kwargs)
    return stream_chat_response_to_completion_response(stream_chat_response)

```
  
---|---  
###  acomplete `async` #
```
acomplete(prompt: str, image_documents: Sequence[Union[ImageNode, ImageBlock]], **kwargs: Any) -> CompletionResponse

```

Async complete.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-ollama/llama_index/multi_modal_llms/ollama/base.py`

| ```
@llm_completion_callback()
async def acomplete(
    self,
    prompt: str,
    image_documents: Sequence[Union[ImageNode, ImageBlock]],
    **kwargs: Any,
) -> CompletionResponse:
    """Async complete."""
    messages = self._get_messages(prompt, image_documents)
    chat_response = await self.achat(messages, **kwargs)
    return chat_response_to_completion_response(chat_response)

```
  
---|---  
###  astream_complete `async` #
```
astream_complete(prompt: str, image_documents: Sequence[Union[ImageNode, ImageBlock]], **kwargs: Any) -> CompletionResponseAsyncGen

```

Async stream complete.
Source code in `llama-index-integrations/multi_modal_llms/llama-index-multi-modal-llms-ollama/llama_index/multi_modal_llms/ollama/base.py`

| ```
async def astream_complete(
    self,
    prompt: str,
    image_documents: Sequence[Union[ImageNode, ImageBlock]],
    **kwargs: Any,
) -> CompletionResponseAsyncGen:
    """Async stream complete."""
    messages = self._get_messages(prompt, image_documents)
    astream_chat_response = await self.astream_chat(messages, **kwargs)
    return astream_chat_response_to_completion_response(astream_chat_response)

```
  
---|---
