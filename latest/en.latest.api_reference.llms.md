# Index
##  LLM #
Bases: `BaseLLM`
The LLM class is the main class for interacting with language models.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`system_prompt` |  `str | None` |  System prompt for LLM calls. |  `None`  
`messages_to_prompt` |  `MessagesToPromptType | None` |  Function to convert a list of messages to an LLM prompt. |  `None`  
`completion_to_prompt` |  `CompletionToPromptType | None` |  Function to convert a completion to an LLM prompt. |  `None`  
`output_parser` |  `BaseOutputParser | None` |  Output parser to parse, validate, and correct errors programmatically. |  `None`  
`pydantic_program_mode` |  `PydanticProgramMode` |  |  `<PydanticProgramMode.DEFAULT: 'default'>`  
`query_wrapper_prompt` |  `BasePromptTemplate | None` |  Query wrapper prompt for LLM calls. |  `None`  
Attributes:
Name | Type | Description  
---|---|---  
`system_prompt` |  `Optional[str]` |  System prompt for LLM calls.  
`messages_to_prompt` |  `Callable` |  Function to convert a list of messages to an LLM prompt.  
`completion_to_prompt` |  `Callable` |  Function to convert a completion to an LLM prompt.  
`output_parser` |  `Optional[BaseOutputParser]` |  Output parser to parse, validate, and correct errors programmatically.  
`pydantic_program_mode` |  `PydanticProgramMode` |  Pydantic program mode to use for structured prediction.  
###  metadata `abstractmethod` `property` #
```
metadata: LLMMetadata

```

LLM metadata.
Returns:
Name | Type | Description  
---|---|---  
`LLMMetadata` |  `LLMMetadata` |  LLM metadata containing various information about the LLM.  
###  class_name `classmethod` #
```
class_name() -> str

```

Get the class name, used as a unique ID in serialization.
This provides a key that makes serialization robust against actual class name changes.
###  as_query_component #
```
as_query_component(partial: Optional[Dict[str, Any]] = None, **kwargs: Any) -> QueryComponent

```

Get query component.
###  convert_chat_messages #
```
convert_chat_messages(messages: Sequence[ChatMessage]) -> List[Any]

```

Convert chat messages to an LLM specific message format.
###  chat `abstractmethod` #
```
chat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse

```

Chat endpoint for LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`messages` |  `Sequence[ChatMessage]` |  Sequence of chat messages. |  _required_  
`kwargs` |  `Any` |  Additional keyword arguments to pass to the LLM. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`ChatResponse` |  `ChatResponse` |  Chat response from the LLM.  
Examples:
```
from llama_index.core.llms import ChatMessage

response = llm.chat([ChatMessage(role="user", content="Hello")])
print(response.content)

```

###  complete `abstractmethod` #
```
complete(prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse

```

Completion endpoint for LLM.
If the LLM is a chat model, the prompt is transformed into a single `user` message.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  Prompt to send to the LLM. |  _required_  
`formatted` |  `bool` |  Whether the prompt is already formatted for the LLM, by default False. |  `False`  
`kwargs` |  `Any` |  Additional keyword arguments to pass to the LLM. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`CompletionResponse` |  `CompletionResponse` |  Completion response from the LLM.  
Examples:
```
response = llm.complete("your prompt")
print(response.text)

```

###  stream_chat `abstractmethod` #
```
stream_chat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseGen

```

Streaming chat endpoint for LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`messages` |  `Sequence[ChatMessage]` |  Sequence of chat messages. |  _required_  
`kwargs` |  `Any` |  Additional keyword arguments to pass to the LLM. |  `{}`  
Yields:
Name | Type | Description  
---|---|---  
`ChatResponse` |  `ChatResponseGen` |  A generator of ChatResponse objects, each containing a new token of the response.  
Examples:
```
from llama_index.core.llms import ChatMessage

gen = llm.stream_chat([ChatMessage(role="user", content="Hello")])
for response in gen:
    print(response.delta, end="", flush=True)

```

###  stream_complete `abstractmethod` #
```
stream_complete(prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseGen

```

Streaming completion endpoint for LLM.
If the LLM is a chat model, the prompt is transformed into a single `user` message.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  Prompt to send to the LLM. |  _required_  
`formatted` |  `bool` |  Whether the prompt is already formatted for the LLM, by default False. |  `False`  
`kwargs` |  `Any` |  Additional keyword arguments to pass to the LLM. |  `{}`  
Yields:
Name | Type | Description  
---|---|---  
`CompletionResponse` |  `CompletionResponseGen` |  A generator of CompletionResponse objects, each containing a new token of the response.  
Examples:
```
gen = llm.stream_complete("your prompt")
for response in gen:
    print(response.text, end="", flush=True)

```

###  achat `abstractmethod` `async` #
```
achat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse

```

Async chat endpoint for LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`messages` |  `Sequence[ChatMessage]` |  Sequence of chat messages. |  _required_  
`kwargs` |  `Any` |  Additional keyword arguments to pass to the LLM. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`ChatResponse` |  `ChatResponse` |  Chat response from the LLM.  
Examples:
```
from llama_index.core.llms import ChatMessage

response = await llm.achat([ChatMessage(role="user", content="Hello")])
print(response.content)

```

###  acomplete `abstractmethod` `async` #
```
acomplete(prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse

```

Async completion endpoint for LLM.
If the LLM is a chat model, the prompt is transformed into a single `user` message.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  Prompt to send to the LLM. |  _required_  
`formatted` |  `bool` |  Whether the prompt is already formatted for the LLM, by default False. |  `False`  
`kwargs` |  `Any` |  Additional keyword arguments to pass to the LLM. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`CompletionResponse` |  `CompletionResponse` |  Completion response from the LLM.  
Examples:
```
response = await llm.acomplete("your prompt")
print(response.text)

```

###  astream_chat `abstractmethod` `async` #
```
astream_chat(messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponseAsyncGen

```

Async streaming chat endpoint for LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`messages` |  `Sequence[ChatMessage]` |  Sequence of chat messages. |  _required_  
`kwargs` |  `Any` |  Additional keyword arguments to pass to the LLM. |  `{}`  
Yields:
Name | Type | Description  
---|---|---  
`ChatResponse` |  `ChatResponseAsyncGen` |  An async generator of ChatResponse objects, each containing a new token of the response.  
Examples:
```
from llama_index.core.llms import ChatMessage

gen = await llm.astream_chat([ChatMessage(role="user", content="Hello")])
async for response in gen:
    print(response.delta, end="", flush=True)

```

###  astream_complete `abstractmethod` `async` #
```
astream_complete(prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponseAsyncGen

```

Async streaming completion endpoint for LLM.
If the LLM is a chat model, the prompt is transformed into a single `user` message.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `str` |  Prompt to send to the LLM. |  _required_  
`formatted` |  `bool` |  Whether the prompt is already formatted for the LLM, by default False. |  `False`  
`kwargs` |  `Any` |  Additional keyword arguments to pass to the LLM. |  `{}`  
Yields:
Name | Type | Description  
---|---|---  
`CompletionResponse` |  `CompletionResponseAsyncGen` |  An async generator of CompletionResponse objects, each containing a new token of the response.  
Examples:
```
gen = await llm.astream_complete("your prompt")
async for response in gen:
    print(response.text, end="", flush=True)

```

###  structured_predict #
```
structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Model

```

Structured predict.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`output_cls` |  `BaseModel` |  Output class to use for structured prediction. |  _required_  
`prompt` |  `PromptTemplate` |  Prompt template to use for structured prediction. |  _required_  
`llm_kwargs` |  `Optional[Dict[str, Any]]` |  Arguments that are passed down to the LLM invoked by the program. |  `None`  
`prompt_args` |  `Any` |  Additional arguments to format the prompt with. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`BaseModel` |  `Model` |  The structured prediction output.  
Examples:
```
from pydantic import BaseModel

class Test(BaseModel):
    \"\"\"My test class.\"\"\"
    name: str

from llama_index.core.prompts import PromptTemplate

prompt = PromptTemplate("Please predict a Test with a random name related to {topic}.")
output = llm.structured_predict(Test, prompt, topic="cats")
print(output.name)

```

###  astructured_predict `async` #
```
astructured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Model

```

Async Structured predict.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`output_cls` |  `BaseModel` |  Output class to use for structured prediction. |  _required_  
`prompt` |  `PromptTemplate` |  Prompt template to use for structured prediction. |  _required_  
`llm_kwargs` |  `Optional[Dict[str, Any]]` |  Arguments that are passed down to the LLM invoked by the program. |  `None`  
`prompt_args` |  `Any` |  Additional arguments to format the prompt with. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`BaseModel` |  `Model` |  The structured prediction output.  
Examples:
```
from pydantic import BaseModel

class Test(BaseModel):
    \"\"\"My test class.\"\"\"
    name: str

from llama_index.core.prompts import PromptTemplate

prompt = PromptTemplate("Please predict a Test with a random name related to {topic}.")
output = await llm.astructured_predict(Test, prompt, topic="cats")
print(output.name)

```

###  stream_structured_predict #
```
stream_structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> Generator[Union[Model, FlexibleModel], None, None]

```

Stream Structured predict.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`output_cls` |  `BaseModel` |  Output class to use for structured prediction. |  _required_  
`prompt` |  `PromptTemplate` |  Prompt template to use for structured prediction. |  _required_  
`llm_kwargs` |  `Optional[Dict[str, Any]]` |  Arguments that are passed down to the LLM invoked by the program. |  `None`  
`prompt_args` |  `Any` |  Additional arguments to format the prompt with. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`Generator` |  `None` |  A generator returning partial copies of the model or list of models.  
Examples:
```
from pydantic import BaseModel

class Test(BaseModel):
    \"\"\"My test class.\"\"\"
    name: str

from llama_index.core.prompts import PromptTemplate

prompt = PromptTemplate("Please predict a Test with a random name related to {topic}.")
stream_output = llm.stream_structured_predict(Test, prompt, topic="cats")
for partial_output in stream_output:
    # stream partial outputs until completion
    print(partial_output.name)

```

###  astream_structured_predict `async` #
```
astream_structured_predict(output_cls: Type[Model], prompt: PromptTemplate, llm_kwargs: Optional[Dict[str, Any]] = None, **prompt_args: Any) -> AsyncGenerator[Union[Model, FlexibleModel], None]

```

Async Stream Structured predict.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`output_cls` |  `BaseModel` |  Output class to use for structured prediction. |  _required_  
`prompt` |  `PromptTemplate` |  Prompt template to use for structured prediction. |  _required_  
`llm_kwargs` |  `Optional[Dict[str, Any]]` |  Arguments that are passed down to the LLM invoked by the program. |  `None`  
`prompt_args` |  `Any` |  Additional arguments to format the prompt with. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`Generator` |  `AsyncGenerator[Union[Model, FlexibleModel], None]` |  A generator returning partial copies of the model or list of models.  
Examples:
```
from pydantic import BaseModel

class Test(BaseModel):
    \"\"\"My test class.\"\"\"
    name: str

from llama_index.core.prompts import PromptTemplate

prompt = PromptTemplate("Please predict a Test with a random name related to {topic}.")
stream_output = await llm.astream_structured_predict(Test, prompt, topic="cats")
async for partial_output in stream_output:
    # stream partial outputs until completion
    print(partial_output.name)

```

###  predict #
```
predict(prompt: BasePromptTemplate, **prompt_args: Any) -> str

```

Predict for a given prompt.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `BasePromptTemplate` |  The prompt to use for prediction. |  _required_  
`prompt_args` |  `Any` |  Additional arguments to format the prompt with. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The prediction output.  
Examples:
```
from llama_index.core.prompts import PromptTemplate

prompt = PromptTemplate("Please write a random name related to {topic}.")
output = llm.predict(prompt, topic="cats")
print(output)

```

###  stream #
```
stream(prompt: BasePromptTemplate, **prompt_args: Any) -> TokenGen

```

Stream predict for a given prompt.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `BasePromptTemplate` |  The prompt to use for prediction. |  _required_  
`prompt_args` |  `Any` |  Additional arguments to format the prompt with. |  `{}`  
Yields:
Name | Type | Description  
---|---|---  
`str` |  `TokenGen` |  Each streamed token.  
Examples:
```
from llama_index.core.prompts import PromptTemplate

prompt = PromptTemplate("Please write a random name related to {topic}.")
gen = llm.stream_predict(prompt, topic="cats")
for token in gen:
    print(token, end="", flush=True)

```

###  apredict `async` #
```
apredict(prompt: BasePromptTemplate, **prompt_args: Any) -> str

```

Async Predict for a given prompt.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompt` |  `BasePromptTemplate` |  The prompt to use for prediction. |  _required_  
`prompt_args` |  `Any` |  Additional arguments to format the prompt with. |  `{}`  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The prediction output.  
Examples:
```
from llama_index.core.prompts import PromptTemplate

prompt = PromptTemplate("Please write a random name related to {topic}.")
output = await llm.apredict(prompt, topic="cats")
print(output)

```

###  astream `async` #
```
astream(prompt: BasePromptTemplate, **prompt_args: Any) -> TokenAsyncGen

```

Async stream predict for a given prompt.
prompt (BasePromptTemplate): The prompt to use for prediction. prompt_args (Any): Additional arguments to format the prompt with.
Yields:
Name | Type | Description  
---|---|---  
`str` |  `TokenAsyncGen` |  An async generator that yields strings of tokens.  
Examples:
```
from llama_index.core.prompts import PromptTemplate

prompt = PromptTemplate("Please write a random name related to {topic}.")
gen = await llm.astream_predict(prompt, topic="cats")
async for token in gen:
    print(token, end="", flush=True)

```

###  predict_and_call #
```
predict_and_call(tools: List[BaseTool], user_msg: Optional[Union[str, ChatMessage]] = None, chat_history: Optional[List[ChatMessage]] = None, verbose: bool = False, **kwargs: Any) -> AgentChatResponse

```

Predict and call the tool.
By default uses a ReAct agent to do tool calling (through text prompting), but function calling LLMs will implement this differently.
###  apredict_and_call `async` #
```
apredict_and_call(tools: List[BaseTool], user_msg: Optional[Union[str, ChatMessage]] = None, chat_history: Optional[List[ChatMessage]] = None, verbose: bool = False, **kwargs: Any) -> AgentChatResponse

```

Predict and call the tool.
###  as_structured_llm #
```
as_structured_llm(output_cls: Type[BaseModel], **kwargs: Any) -> StructuredLLM

```

Return a structured LLM around a given object.
##  MessageRole #
Bases: `str`, `Enum`
Message role.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class MessageRole(str, Enum):
    """Message role."""

    SYSTEM = "system"
    DEVELOPER = "developer"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"
    CHATBOT = "chatbot"
    MODEL = "model"

```
  
---|---  
##  TextBlock #
Bases: `BaseModel`
A representation of text data to directly pass to/from the LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`block_type` |  `Literal['text']` |  |  `'text'`  
`text` |  `str` |  |  _required_  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class TextBlock(BaseModel):
    """A representation of text data to directly pass to/from the LLM."""

    block_type: Literal["text"] = "text"
    text: str

```
  
---|---  
##  ImageBlock #
Bases: `BaseModel`
A representation of image data to directly pass to/from the LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`block_type` |  `Literal['image']` |  |  `'image'`  
`image` |  `bytes | None` |  |  `None`  
`path` |  `Annotated[Path, PathType] | None` |  |  `None`  
`url` |  `AnyUrl | str | None` |  |  `None`  
`image_mimetype` |  `str | None` |  |  `None`  
`detail` |  `str | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class ImageBlock(BaseModel):
    """A representation of image data to directly pass to/from the LLM."""

    block_type: Literal["image"] = "image"
    image: bytes | None = None
    path: FilePath | None = None
    url: AnyUrl | str | None = None
    image_mimetype: str | None = None
    detail: str | None = None

    @field_validator("url", mode="after")
    @classmethod
    def urlstr_to_anyurl(cls, url: str | AnyUrl | None) -> AnyUrl | None:
        """Store the url as Anyurl."""
        if isinstance(url, AnyUrl):
            return url
        if url is None:
            return None

        return AnyUrl(url=url)

    @model_validator(mode="after")
    def image_to_base64(self) -> Self:
        """
        Store the image as base64 and guess the mimetype when possible.

        In case the model was built passing image data but without a mimetype,
        we try to guess it using the filetype library. To avoid resource-intense
        operations, we won't load the path or the URL to guess the mimetype.
        """
        if not self.image:
            if not self.image_mimetype:
                path = self.path or self.url
                if path:
                    suffix = Path(str(path)).suffix.replace(".", "") or None
                    mimetype = filetype.get_type(ext=suffix)
                    if mimetype and str(mimetype.mime).startswith("image/"):
                        self.image_mimetype = str(mimetype.mime)

            return self

        try:
            # Check if self.image is already base64 encoded.
            # b64decode() can succeed on random binary data, so we
            # pass verify=True to make sure it's not a false positive
            decoded_img = base64.b64decode(self.image, validate=True)
        except BinasciiError:
            decoded_img = self.image
            self.image = base64.b64encode(self.image)

        self._guess_mimetype(decoded_img)
        return self

    def _guess_mimetype(self, img_data: bytes) -> None:
        if not self.image_mimetype:
            guess = filetype.guess(img_data)
            self.image_mimetype = guess.mime if guess else None

    def resolve_image(self, as_base64: bool = False) -> BytesIO:
        """
        Resolve an image such that PIL can read it.

        Args:
            as_base64 (bool): whether the resolved image should be returned as base64-encoded bytes

        """
        data_buffer = resolve_binary(
            raw_bytes=self.image,
            path=self.path,
            url=str(self.url) if self.url else None,
            as_base64=as_base64,
        )

        # Check size by seeking to end and getting position
        data_buffer.seek(0, 2)  # Seek to end
        size = data_buffer.tell()
        data_buffer.seek(0)  # Reset to beginning

        if size == 0:
            raise ValueError("resolve_image returned zero bytes")
        return data_buffer

```
  
---|---  
###  urlstr_to_anyurl `classmethod` #
```
urlstr_to_anyurl(url: str | AnyUrl | None) -> AnyUrl | None

```

Store the url as Anyurl.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
@field_validator("url", mode="after")
@classmethod
def urlstr_to_anyurl(cls, url: str | AnyUrl | None) -> AnyUrl | None:
    """Store the url as Anyurl."""
    if isinstance(url, AnyUrl):
        return url
    if url is None:
        return None

    return AnyUrl(url=url)

```
  
---|---  
###  image_to_base64 #
```
image_to_base64() -> Self

```

Store the image as base64 and guess the mimetype when possible.
In case the model was built passing image data but without a mimetype, we try to guess it using the filetype library. To avoid resource-intense operations, we won't load the path or the URL to guess the mimetype.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
@model_validator(mode="after")
def image_to_base64(self) -> Self:
    """
    Store the image as base64 and guess the mimetype when possible.

    In case the model was built passing image data but without a mimetype,
    we try to guess it using the filetype library. To avoid resource-intense
    operations, we won't load the path or the URL to guess the mimetype.
    """
    if not self.image:
        if not self.image_mimetype:
            path = self.path or self.url
            if path:
                suffix = Path(str(path)).suffix.replace(".", "") or None
                mimetype = filetype.get_type(ext=suffix)
                if mimetype and str(mimetype.mime).startswith("image/"):
                    self.image_mimetype = str(mimetype.mime)

        return self

    try:
        # Check if self.image is already base64 encoded.
        # b64decode() can succeed on random binary data, so we
        # pass verify=True to make sure it's not a false positive
        decoded_img = base64.b64decode(self.image, validate=True)
    except BinasciiError:
        decoded_img = self.image
        self.image = base64.b64encode(self.image)

    self._guess_mimetype(decoded_img)
    return self

```
  
---|---  
###  resolve_image #
```
resolve_image(as_base64: bool = False) -> BytesIO

```

Resolve an image such that PIL can read it.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`as_base64` |  `bool` |  whether the resolved image should be returned as base64-encoded bytes |  `False`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
def resolve_image(self, as_base64: bool = False) -> BytesIO:
    """
    Resolve an image such that PIL can read it.

    Args:
        as_base64 (bool): whether the resolved image should be returned as base64-encoded bytes

    """
    data_buffer = resolve_binary(
        raw_bytes=self.image,
        path=self.path,
        url=str(self.url) if self.url else None,
        as_base64=as_base64,
    )

    # Check size by seeking to end and getting position
    data_buffer.seek(0, 2)  # Seek to end
    size = data_buffer.tell()
    data_buffer.seek(0)  # Reset to beginning

    if size == 0:
        raise ValueError("resolve_image returned zero bytes")
    return data_buffer

```
  
---|---  
##  AudioBlock #
Bases: `BaseModel`
A representation of audio data to directly pass to/from the LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`block_type` |  `Literal['audio']` |  |  `'audio'`  
`audio` |  `bytes | None` |  |  `None`  
`path` |  `Annotated[Path, PathType] | None` |  |  `None`  
`url` |  `AnyUrl | str | None` |  |  `None`  
`format` |  `str | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class AudioBlock(BaseModel):
    """A representation of audio data to directly pass to/from the LLM."""

    block_type: Literal["audio"] = "audio"
    audio: bytes | None = None
    path: FilePath | None = None
    url: AnyUrl | str | None = None
    format: str | None = None

    @field_validator("url", mode="after")
    @classmethod
    def urlstr_to_anyurl(cls, url: str | AnyUrl) -> AnyUrl:
        """Store the url as Anyurl."""
        if isinstance(url, AnyUrl):
            return url
        return AnyUrl(url=url)

    @model_validator(mode="after")
    def audio_to_base64(self) -> Self:
        """
        Store the audio as base64 and guess the mimetype when possible.

        In case the model was built passing audio data but without a mimetype,
        we try to guess it using the filetype library. To avoid resource-intense
        operations, we won't load the path or the URL to guess the mimetype.
        """
        if not self.audio:
            return self

        try:
            # Check if audio is already base64 encoded
            decoded_audio = base64.b64decode(self.audio)
        except Exception:
            decoded_audio = self.audio
            # Not base64 - encode it
            self.audio = base64.b64encode(self.audio)

        self._guess_format(decoded_audio)

        return self

    def _guess_format(self, audio_data: bytes) -> None:
        if not self.format:
            guess = filetype.guess(audio_data)
            self.format = guess.extension if guess else None

    def resolve_audio(self, as_base64: bool = False) -> BytesIO:
        """
        Resolve an audio such that PIL can read it.

        Args:
            as_base64 (bool): whether the resolved audio should be returned as base64-encoded bytes

        """
        data_buffer = resolve_binary(
            raw_bytes=self.audio,
            path=self.path,
            url=str(self.url) if self.url else None,
            as_base64=as_base64,
        )
        # Check size by seeking to end and getting position
        data_buffer.seek(0, 2)  # Seek to end
        size = data_buffer.tell()
        data_buffer.seek(0)  # Reset to beginning

        if size == 0:
            raise ValueError("resolve_image returned zero bytes")
        return data_buffer

```
  
---|---  
###  urlstr_to_anyurl `classmethod` #
```
urlstr_to_anyurl(url: str | AnyUrl) -> AnyUrl

```

Store the url as Anyurl.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
@field_validator("url", mode="after")
@classmethod
def urlstr_to_anyurl(cls, url: str | AnyUrl) -> AnyUrl:
    """Store the url as Anyurl."""
    if isinstance(url, AnyUrl):
        return url
    return AnyUrl(url=url)

```
  
---|---  
###  audio_to_base64 #
```
audio_to_base64() -> Self

```

Store the audio as base64 and guess the mimetype when possible.
In case the model was built passing audio data but without a mimetype, we try to guess it using the filetype library. To avoid resource-intense operations, we won't load the path or the URL to guess the mimetype.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
@model_validator(mode="after")
def audio_to_base64(self) -> Self:
    """
    Store the audio as base64 and guess the mimetype when possible.

    In case the model was built passing audio data but without a mimetype,
    we try to guess it using the filetype library. To avoid resource-intense
    operations, we won't load the path or the URL to guess the mimetype.
    """
    if not self.audio:
        return self

    try:
        # Check if audio is already base64 encoded
        decoded_audio = base64.b64decode(self.audio)
    except Exception:
        decoded_audio = self.audio
        # Not base64 - encode it
        self.audio = base64.b64encode(self.audio)

    self._guess_format(decoded_audio)

    return self

```
  
---|---  
###  resolve_audio #
```
resolve_audio(as_base64: bool = False) -> BytesIO

```

Resolve an audio such that PIL can read it.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`as_base64` |  `bool` |  whether the resolved audio should be returned as base64-encoded bytes |  `False`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
def resolve_audio(self, as_base64: bool = False) -> BytesIO:
    """
    Resolve an audio such that PIL can read it.

    Args:
        as_base64 (bool): whether the resolved audio should be returned as base64-encoded bytes

    """
    data_buffer = resolve_binary(
        raw_bytes=self.audio,
        path=self.path,
        url=str(self.url) if self.url else None,
        as_base64=as_base64,
    )
    # Check size by seeking to end and getting position
    data_buffer.seek(0, 2)  # Seek to end
    size = data_buffer.tell()
    data_buffer.seek(0)  # Reset to beginning

    if size == 0:
        raise ValueError("resolve_image returned zero bytes")
    return data_buffer

```
  
---|---  
##  DocumentBlock #
Bases: `BaseModel`
A representation of a document to directly pass to the LLM.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`block_type` |  `Literal['document']` |  |  `'document'`  
`data` |  `bytes | None` |  |  `None`  
`path` |  `Annotated[Path, PathType] | str | None` |  |  `None`  
`url` |  `str | None` |  |  `None`  
`title` |  `str | None` |  |  `None`  
`document_mimetype` |  `str | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class DocumentBlock(BaseModel):
    """A representation of a document to directly pass to the LLM."""

    block_type: Literal["document"] = "document"
    data: Optional[bytes] = None
    path: Optional[Union[FilePath | str]] = None
    url: Optional[str] = None
    title: Optional[str] = None
    document_mimetype: Optional[str] = None

    @model_validator(mode="after")
    def document_validation(self) -> Self:
        self.document_mimetype = self.document_mimetype or self._guess_mimetype()

        if not self.title:
            self.title = "input_document"

        # skip data validation if it's not provided
        if not self.data:
            return self

        try:
            decoded_document = base64.b64decode(self.data, validate=True)
        except BinasciiError:
            self.data = base64.b64encode(self.data)

        return self

    def resolve_document(self) -> BytesIO:
        """
        Resolve a document such that it is represented by a BufferIO object.
        """
        data_buffer = resolve_binary(
            raw_bytes=self.data,
            path=self.path,
            url=str(self.url) if self.url else None,
            as_base64=False,
        )
        # Check size by seeking to end and getting position
        data_buffer.seek(0, 2)  # Seek to end
        size = data_buffer.tell()
        data_buffer.seek(0)  # Reset to beginning

        if size == 0:
            raise ValueError("resolve_image returned zero bytes")
        return data_buffer

    def _get_b64_string(self, data_buffer: BytesIO) -> str:
        """
        Get base64-encoded string from a BytesIO buffer.
        """
        data = data_buffer.read()
        return base64.b64encode(data).decode("utf-8")

    def _get_b64_bytes(self, data_buffer: BytesIO) -> bytes:
        """
        Get base64-encoded bytes from a BytesIO buffer.
        """
        data = data_buffer.read()
        return base64.b64encode(data)

    def guess_format(self) -> str | None:
        path = self.path or self.url
        if not path:
            return None

        return Path(str(path)).suffix.replace(".", "")

    def _guess_mimetype(self) -> str | None:
        if self.data:
            guess = filetype.guess(self.data)
            return str(guess.mime) if guess else None

        suffix = self.guess_format()
        if not suffix:
            return None

        guess = filetype.get_type(ext=suffix)
        return str(guess.mime) if guess else None

```
  
---|---  
###  resolve_document #
```
resolve_document() -> BytesIO

```

Resolve a document such that it is represented by a BufferIO object.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
def resolve_document(self) -> BytesIO:
    """
    Resolve a document such that it is represented by a BufferIO object.
    """
    data_buffer = resolve_binary(
        raw_bytes=self.data,
        path=self.path,
        url=str(self.url) if self.url else None,
        as_base64=False,
    )
    # Check size by seeking to end and getting position
    data_buffer.seek(0, 2)  # Seek to end
    size = data_buffer.tell()
    data_buffer.seek(0)  # Reset to beginning

    if size == 0:
        raise ValueError("resolve_image returned zero bytes")
    return data_buffer

```
  
---|---  
##  CachePoint #
Bases: `BaseModel`
Used to set the point to cache up to, if the LLM supports caching.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class CachePoint(BaseModel):
    """Used to set the point to cache up to, if the LLM supports caching."""

    block_type: Literal["cache"] = "cache"
    cache_control: CacheControl

```
  
---|---  
##  CitableBlock #
Bases: `BaseModel`
Supports providing citable content to LLMs that have built-in citation support.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class CitableBlock(BaseModel):
    """Supports providing citable content to LLMs that have built-in citation support."""

    block_type: Literal["citable"] = "citable"
    title: str
    source: str
    # TODO: We could maybe expand the types here,
    # limiting for now to known use cases
    content: List[
        Annotated[
            Union[TextBlock, ImageBlock, DocumentBlock],
            Field(discriminator="block_type"),
        ]
    ]

    @field_validator("content", mode="before")
    @classmethod
    def validate_content(cls, v: Any) -> Any:
        if isinstance(v, str):
            return [TextBlock(text=v)]

        return v

```
  
---|---  
##  CitationBlock #
Bases: `BaseModel`
A representation of cited content from past messages.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class CitationBlock(BaseModel):
    """A representation of cited content from past messages."""

    block_type: Literal["citation"] = "citation"
    cited_content: Annotated[
        Union[TextBlock, ImageBlock], Field(discriminator="block_type")
    ]
    source: str
    title: str
    additional_location_info: Dict[str, int]

    @field_validator("cited_content", mode="before")
    @classmethod
    def validate_cited_content(cls, v: Any) -> Any:
        if isinstance(v, str):
            return TextBlock(text=v)

        return v

```
  
---|---  
##  ChatMessage #
Bases: `BaseModel`
Chat message.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`role` |  `MessageRole` |  |  `<MessageRole.USER: 'user'>`  
`blocks` |  `list[Annotated[Union[TextBlock, ImageBlock, AudioBlock, DocumentBlock], FieldInfo]]` |  Built-in mutable sequence. If no argument is given, the constructor creates a new empty list. The argument must be an iterable if specified. |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class ChatMessage(BaseModel):
    """Chat message."""

    role: MessageRole = MessageRole.USER
    additional_kwargs: dict[str, Any] = Field(default_factory=dict)
    blocks: list[ContentBlock] = Field(default_factory=list)

    def __init__(self, /, content: Any | None = None, **data: Any) -> None:
        """
        Keeps backward compatibility with the old `content` field.

        If content was passed and contained text, store a single TextBlock.
        If content was passed and it was a list, assume it's a list of content blocks and store it.
        """
        if content is not None:
            if isinstance(content, str):
                data["blocks"] = [TextBlock(text=content)]
            elif isinstance(content, list):
                data["blocks"] = content

        super().__init__(**data)

    @model_validator(mode="after")
    def legacy_additional_kwargs_image(self) -> Self:
        """
        Provided for backward compatibility.

        If `additional_kwargs` contains an `images` key, assume the value is a list
        of ImageDocument and convert them into image blocks.
        """
        if documents := self.additional_kwargs.get("images"):
            documents = cast(list[ImageDocument], documents)
            for doc in documents:
                img_base64_bytes = doc.resolve_image(as_base64=True).read()
                self.blocks.append(ImageBlock(image=img_base64_bytes))
        return self

    @property
    def content(self) -> str | None:
        """
        Keeps backward compatibility with the old `content` field.

        Returns:
            The cumulative content of the TextBlock blocks, None if there are none.

        """
        content_strs = []
        for block in self.blocks:
            if isinstance(block, TextBlock):
                content_strs.append(block.text)

        ct = "\n".join(content_strs) or None
        if ct is None and len(content_strs) == 1:
            return ""
        return ct

    @content.setter
    def content(self, content: str) -> None:
        """
        Keeps backward compatibility with the old `content` field.

        Raises:
            ValueError: if blocks contains more than a block, or a block that's not TextBlock.

        """
        if not self.blocks:
            self.blocks = [TextBlock(text=content)]
        elif len(self.blocks) == 1 and isinstance(self.blocks[0], TextBlock):
            self.blocks = [TextBlock(text=content)]
        else:
            raise ValueError(
                "ChatMessage contains multiple blocks, use 'ChatMessage.blocks' instead."
            )

    def __str__(self) -> str:
        return f"{self.role.value}: {self.content}"

    @classmethod
    def from_str(
        cls,
        content: str,
        role: Union[MessageRole, str] = MessageRole.USER,
        **kwargs: Any,
    ) -> Self:
        if isinstance(role, str):
            role = MessageRole(role)
        return cls(role=role, blocks=[TextBlock(text=content)], **kwargs)

    def _recursive_serialization(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            value.model_rebuild()  # ensures all fields are initialized and serializable
            return value.model_dump()  # type: ignore
        if isinstance(value, dict):
            return {
                key: self._recursive_serialization(value)
                for key, value in value.items()
            }
        if isinstance(value, list):
            return [self._recursive_serialization(item) for item in value]
        return value

    @field_serializer("additional_kwargs", check_fields=False)
    def serialize_additional_kwargs(self, value: Any, _info: Any) -> Any:
        return self._recursive_serialization(value)

```
  
---|---  
###  content `property` `writable` #
```
content: str | None

```

Keeps backward compatibility with the old `content` field.
Returns:
Type | Description  
---|---  
`str | None` |  The cumulative content of the TextBlock blocks, None if there are none.  
###  legacy_additional_kwargs_image #
```
legacy_additional_kwargs_image() -> Self

```

Provided for backward compatibility.
If `additional_kwargs` contains an `images` key, assume the value is a list of ImageDocument and convert them into image blocks.
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
@model_validator(mode="after")
def legacy_additional_kwargs_image(self) -> Self:
    """
    Provided for backward compatibility.

    If `additional_kwargs` contains an `images` key, assume the value is a list
    of ImageDocument and convert them into image blocks.
    """
    if documents := self.additional_kwargs.get("images"):
        documents = cast(list[ImageDocument], documents)
        for doc in documents:
            img_base64_bytes = doc.resolve_image(as_base64=True).read()
            self.blocks.append(ImageBlock(image=img_base64_bytes))
    return self

```
  
---|---  
##  LogProb #
Bases: `BaseModel`
LogProb of a token.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`logprob` |  `float` |  Convert a string or number to a floating-point number, if possible. |  `<dynamic>`  
`bytes` |  `List[int]` |  Built-in mutable sequence. If no argument is given, the constructor creates a new empty list. The argument must be an iterable if specified. |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class LogProb(BaseModel):
    """LogProb of a token."""

    token: str = Field(default_factory=str)
    logprob: float = Field(default_factory=float)
    bytes: List[int] = Field(default_factory=list)

```
  
---|---  
##  ChatResponse #
Bases: `BaseModel`
Chat response.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`message` |  `ChatMessage` |  |  _required_  
`raw` |  `Any | None` |  |  `None`  
`delta` |  `str | None` |  |  `None`  
`logprobs` |  `List[List[LogProb]] | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class ChatResponse(BaseModel):
    """Chat response."""

    message: ChatMessage
    raw: Optional[Any] = None
    delta: Optional[str] = None
    logprobs: Optional[List[List[LogProb]]] = None
    additional_kwargs: dict = Field(default_factory=dict)

    def __str__(self) -> str:
        return str(self.message)

```
  
---|---  
##  CompletionResponse #
Bases: `BaseModel`
Completion response.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`text` |  `str` |  |  _required_  
`raw` |  `Any | None` |  |  `None`  
`logprobs` |  `List[List[LogProb]] | None` |  |  `None`  
`delta` |  `str | None` |  |  `None`  
Fields
text: Text content of the response if not streaming, or if streaming, the current extent of streamed text. additional_kwargs: Additional information on the response(i.e. token counts, function calling information). raw: Optional raw JSON that was parsed to populate text, if relevant. delta: New text that just streamed in (only relevant when streaming).
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class CompletionResponse(BaseModel):
    """
    Completion response.

    Fields:
        text: Text content of the response if not streaming, or if streaming,
            the current extent of streamed text.
        additional_kwargs: Additional information on the response(i.e. token
            counts, function calling information).
        raw: Optional raw JSON that was parsed to populate text, if relevant.
        delta: New text that just streamed in (only relevant when streaming).
    """

    text: str
    additional_kwargs: dict = Field(default_factory=dict)
    raw: Optional[Any] = None
    logprobs: Optional[List[List[LogProb]]] = None
    delta: Optional[str] = None

    def __str__(self) -> str:
        return self.text

```
  
---|---  
##  LLMMetadata #
Bases: `BaseModel`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`context_window` |  `int` |  Total number of tokens the model can be input and output for one response. |  `3900`  
`num_output` |  `int` |  Number of tokens the model can output when generating a response. |  `256`  
`is_chat_model` |  `bool` |  Set True if the model exposes a chat interface (i.e. can be passed a sequence of messages, rather than text), like OpenAI's /v1/chat/completions endpoint. |  `False`  
`is_function_calling_model` |  `bool` |  Set True if the model supports function calling messages, similar to OpenAI's function calling API. For example, converting 'Email Anya to see if she wants to get coffee next Friday' to a function call like `send_email(to: string, body: string)`. |  `False`  
`model_name` |  `str` |  The model's name used for logging, testing, and sanity checking. For some models this can be automatically discerned. For other models, like locally loaded models, this must be manually specified. |  `'unknown'`  
`system_role` |  `MessageRole` |  The role this specific LLM providerexpects for system prompt. E.g. 'SYSTEM' for OpenAI, 'CHATBOT' for Cohere |  `<MessageRole.SYSTEM: 'system'>`  
Source code in `llama-index-core/llama_index/core/base/llms/types.py`

| ```
class LLMMetadata(BaseModel):
    model_config = ConfigDict(
        protected_namespaces=("pydantic_model_",), arbitrary_types_allowed=True
    )
    context_window: int = Field(
        default=DEFAULT_CONTEXT_WINDOW,
        description=(
            "Total number of tokens the model can be input and output for one response."
        ),
    )
    num_output: int = Field(
        default=DEFAULT_NUM_OUTPUTS,
        description="Number of tokens the model can output when generating a response.",
    )
    is_chat_model: bool = Field(
        default=False,
        description=(
            "Set True if the model exposes a chat interface (i.e. can be passed a"
            " sequence of messages, rather than text), like OpenAI's"
            " /v1/chat/completions endpoint."
        ),
    )
    is_function_calling_model: bool = Field(
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
    system_role: MessageRole = Field(
        default=MessageRole.SYSTEM,
        description="The role this specific LLM provider"
        "expects for system prompt. E.g. 'SYSTEM' for OpenAI, 'CHATBOT' for Cohere",
    )

```
  
---|---
