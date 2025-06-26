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
