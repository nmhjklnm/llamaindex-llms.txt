# Llm
Bases: `QueryComponent`
Base LLM component.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`llm` |  `LLM` |  LLM |  _required_  
`streaming` |  `bool` |  Streaming mode |  `False`  
Source code in `llama-index-core/llama_index/core/llms/llm.py`

| ```
class BaseLLMComponent(QueryComponent):
    """Base LLM component."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: LLM = Field(..., description="LLM")
    streaming: bool = Field(default=False, description="Streaming mode")

    def set_callback_manager(self, callback_manager: Any) -> None:
        """Set callback manager."""
        self.llm.callback_manager = callback_manager

```
  
---|---  
##  set_callback_manager #
```
set_callback_manager(callback_manager: Any) -> None

```

Set callback manager.
Source code in `llama-index-core/llama_index/core/llms/llm.py`

| ```
def set_callback_manager(self, callback_manager: Any) -> None:
    """Set callback manager."""
    self.llm.callback_manager = callback_manager

```
  
---|---  
Bases: `BaseLLMComponent`
LLM completion component.
Source code in `llama-index-core/llama_index/core/llms/llm.py`

| ```
class LLMCompleteComponent(BaseLLMComponent):
    """LLM completion component."""

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        if "prompt" not in input:
            raise ValueError("Prompt must be in input dict.")

        # do special check to see if prompt is a list of chat messages
        if isinstance(input["prompt"], get_args(List[ChatMessage])):
            if self.llm.messages_to_prompt:
                input["prompt"] = self.llm.messages_to_prompt(input["prompt"])
            input["prompt"] = validate_and_convert_stringable(input["prompt"])
        else:
            input["prompt"] = validate_and_convert_stringable(input["prompt"])
            if self.llm.completion_to_prompt:
                input["prompt"] = self.llm.completion_to_prompt(input["prompt"])

        return input

    def _run_component(self, **kwargs: Any) -> Any:
        """Run component."""
        # TODO: support only complete for now
        # non-trivial to figure how to support chat/complete/etc.
        prompt = kwargs["prompt"]
        # ignore all other kwargs for now

        response: Any
        if self.streaming:
            response = self.llm.stream_complete(prompt, formatted=True)
        else:
            response = self.llm.complete(prompt, formatted=True)
        return {"output": response}

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component."""
        # TODO: support only complete for now
        # non-trivial to figure how to support chat/complete/etc.
        prompt = kwargs["prompt"]
        # ignore all other kwargs for now
        response = await self.llm.acomplete(prompt, formatted=True)
        return {"output": response}

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        # TODO: support only complete for now
        return InputKeys.from_keys({"prompt"})

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        return OutputKeys.from_keys({"output"})

```
  
---|---  
##  input_keys `property` #
```
input_keys: InputKeys

```

Input keys.
##  output_keys `property` #
```
output_keys: OutputKeys

```

Output keys.
Bases: `BaseLLMComponent`
LLM chat component.
Source code in `llama-index-core/llama_index/core/llms/llm.py`

| ```
class LLMChatComponent(BaseLLMComponent):
    """LLM chat component."""

    def _validate_component_inputs(self, input: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component inputs during run_component."""
        if "messages" not in input:
            raise ValueError("Messages must be in input dict.")

        # if `messages` is a string, convert to a list of chat message
        if isinstance(input["messages"], get_args(StringableInput)):
            input["messages"] = validate_and_convert_stringable(input["messages"])
            input["messages"] = prompt_to_messages(str(input["messages"]))

        for message in input["messages"]:
            if not isinstance(message, ChatMessage):
                raise ValueError("Messages must be a list of ChatMessage")
        return input

    def _run_component(self, **kwargs: Any) -> Any:
        """Run component."""
        # TODO: support only complete for now
        # non-trivial to figure how to support chat/complete/etc.
        messages = kwargs["messages"]

        response: Any
        if self.streaming:
            response = self.llm.stream_chat(messages)
        else:
            response = self.llm.chat(messages)
        return {"output": response}

    async def _arun_component(self, **kwargs: Any) -> Any:
        """Run component."""
        # TODO: support only complete for now
        # non-trivial to figure how to support chat/complete/etc.
        messages = kwargs["messages"]

        response: Any
        if self.streaming:
            response = await self.llm.astream_chat(messages)
        else:
            response = await self.llm.achat(messages)
        return {"output": response}

    @property
    def input_keys(self) -> InputKeys:
        """Input keys."""
        # TODO: support only complete for now
        return InputKeys.from_keys({"messages"})

    @property
    def output_keys(self) -> OutputKeys:
        """Output keys."""
        return OutputKeys.from_keys({"output"})

```
  
---|---  
##  input_keys `property` #
```
input_keys: InputKeys

```

Input keys.
##  output_keys `property` #
```
output_keys: OutputKeys

```

Output keys.
