# Index
Prompt class.
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
##  BasePromptTemplate #
Bases: `ChainableMixin`, `BaseModel`, `ABC`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`metadata` |  `Dict[str, Any]` |  |  _required_  
`template_vars` |  `List[str]` |  |  _required_  
`kwargs` |  `Dict[str, str]` |  |  _required_  
`output_parser` |  `BaseOutputParser | None` |  |  _required_  
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
class BasePromptTemplate(ChainableMixin, BaseModel, ABC):  # type: ignore[no-redef]
    model_config = ConfigDict(arbitrary_types_allowed=True)
    metadata: Dict[str, Any]
    template_vars: List[str]
    kwargs: Dict[str, str]
    output_parser: Optional[BaseOutputParser]
    template_var_mappings: Optional[Dict[str, Any]] = Field(
        default_factory=dict,  # type: ignore
        description="Template variable mappings (Optional).",
    )
    function_mappings: Optional[Dict[str, AnnotatedCallable]] = Field(
        default_factory=dict,  # type: ignore
        description=(
            "Function mappings (Optional). This is a mapping from template "
            "variable names to functions that take in the current kwargs and "
            "return a string."
        ),
    )

    def _map_template_vars(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """For keys in template_var_mappings, swap in the right keys."""
        template_var_mappings = self.template_var_mappings or {}
        return {template_var_mappings.get(k, k): v for k, v in kwargs.items()}

    def _map_function_vars(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        For keys in function_mappings, compute values and combine w/ kwargs.

        Users can pass in functions instead of fixed values as format variables.
        For each function, we call the function with the current kwargs,
        get back the value, and then use that value in the template
        for the corresponding format variable.

        """
        function_mappings = self.function_mappings or {}
        # first generate the values for the functions
        new_kwargs = {}
        for k, v in function_mappings.items():
            # TODO: figure out what variables to pass into each function
            # is it the kwargs specified during query time? just the fixed kwargs?
            # all kwargs?
            new_kwargs[k] = v(**kwargs)

        # then, add the fixed variables only if not in new_kwargs already
        # (implying that function mapping will override fixed variables)
        for k, v in kwargs.items():
            if k not in new_kwargs:
                new_kwargs[k] = v

        return new_kwargs

    def _map_all_vars(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map both template and function variables.

        We (1) first call function mappings to compute functions,
        and then (2) call the template_var_mappings.

        """
        # map function
        new_kwargs = self._map_function_vars(kwargs)
        # map template vars (to point to existing format vars in string template)
        return self._map_template_vars(new_kwargs)

    @abstractmethod
    def partial_format(self, **kwargs: Any) -> "BasePromptTemplate": ...

    @abstractmethod
    def format(self, llm: Optional[BaseLLM] = None, **kwargs: Any) -> str: ...

    @abstractmethod
    def format_messages(
        self, llm: Optional[BaseLLM] = None, **kwargs: Any
    ) -> List[ChatMessage]: ...

    @abstractmethod
    def get_template(self, llm: Optional[BaseLLM] = None) -> str: ...

    def _as_query_component(
        self, llm: Optional[BaseLLM] = None, **kwargs: Any
    ) -> QueryComponent:
        """As query component."""
        return PromptComponent(prompt=self, format_messages=False, llm=llm)

```
  
---|---  
##  ChatPromptTemplate #
Bases: `BasePromptTemplate`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`message_templates` |  `List[ChatMessage]` |  |  _required_  
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
class ChatPromptTemplate(BasePromptTemplate):  # type: ignore[no-redef]
    message_templates: List[ChatMessage]

    def __init__(
        self,
        message_templates: Sequence[ChatMessage],
        prompt_type: str = PromptType.CUSTOM,
        output_parser: Optional[BaseOutputParser] = None,
        metadata: Optional[Dict[str, Any]] = None,
        template_var_mappings: Optional[Dict[str, Any]] = None,
        function_mappings: Optional[Dict[str, Callable]] = None,
        **kwargs: Any,
    ):
        if metadata is None:
            metadata = {}
        metadata["prompt_type"] = prompt_type

        template_vars = []
        for message_template in message_templates:
            template_vars.extend(get_template_vars(message_template.content or ""))

        super().__init__(
            message_templates=message_templates,
            kwargs=kwargs,
            metadata=metadata,
            output_parser=output_parser,
            template_vars=template_vars,
            template_var_mappings=template_var_mappings,
            function_mappings=function_mappings,
        )

    @classmethod
    def from_messages(
        cls,
        message_templates: Union[List[Tuple[str, str]], List[ChatMessage]],
        **kwargs: Any,
    ) -> "ChatPromptTemplate":
        """From messages."""
        if isinstance(message_templates[0], tuple):
            message_templates = [
                ChatMessage.from_str(role=role, content=content)  # type: ignore[arg-type]
                for role, content in message_templates
            ]
        return cls(message_templates=message_templates, **kwargs)  # type: ignore[arg-type]

    def partial_format(self, **kwargs: Any) -> "ChatPromptTemplate":
        prompt = deepcopy(self)
        prompt.kwargs.update(kwargs)
        return prompt

    def format(
        self,
        llm: Optional[BaseLLM] = None,
        messages_to_prompt: Optional[Callable[[Sequence[ChatMessage]], str]] = None,
        **kwargs: Any,
    ) -> str:
        del llm  # unused
        messages = self.format_messages(**kwargs)

        if messages_to_prompt is not None:
            return messages_to_prompt(messages)

        return default_messages_to_prompt(messages)

    def format_messages(
        self, llm: Optional[BaseLLM] = None, **kwargs: Any
    ) -> List[ChatMessage]:
        del llm  # unused
        """Format the prompt into a list of chat messages."""
        all_kwargs = {
            **self.kwargs,
            **kwargs,
        }
        mapped_all_kwargs = self._map_all_vars(all_kwargs)

        messages: List[ChatMessage] = []
        for message_template in self.message_templates:
            # Handle messages with multiple blocks
            if message_template.blocks:
                formatted_blocks: List[ContentBlock] = []
                for block in message_template.blocks:
                    if isinstance(block, TextBlock):
                        template_vars = get_template_vars(block.text)
                        relevant_kwargs = {
                            k: v
                            for k, v in mapped_all_kwargs.items()
                            if k in template_vars
                        }
                        formatted_text = format_string(block.text, **relevant_kwargs)
                        formatted_blocks.append(TextBlock(text=formatted_text))
                    else:
                        # For non-text blocks (like images), keep them as is
                        # TODO: can images be formatted as variables?
                        formatted_blocks.append(block)

                message = message_template.model_copy()
                message.blocks = formatted_blocks
                messages.append(message)
            else:
                # Handle empty messages (if any)
                messages.append(message_template.model_copy())

        if self.output_parser is not None:
            messages = self.output_parser.format_messages(messages)

        return messages

    def get_template(self, llm: Optional[BaseLLM] = None) -> str:
        return default_messages_to_prompt(self.message_templates)

    def _as_query_component(
        self, llm: Optional[BaseLLM] = None, **kwargs: Any
    ) -> QueryComponent:
        """As query component."""
        return PromptComponent(prompt=self, format_messages=True, llm=llm)

```
  
---|---  
###  from_messages `classmethod` #
```
from_messages(message_templates: Union[List[Tuple[str, str]], List[ChatMessage]], **kwargs: Any) -> ChatPromptTemplate

```

From messages.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
@classmethod
def from_messages(
    cls,
    message_templates: Union[List[Tuple[str, str]], List[ChatMessage]],
    **kwargs: Any,
) -> "ChatPromptTemplate":
    """From messages."""
    if isinstance(message_templates[0], tuple):
        message_templates = [
            ChatMessage.from_str(role=role, content=content)  # type: ignore[arg-type]
            for role, content in message_templates
        ]
    return cls(message_templates=message_templates, **kwargs)  # type: ignore[arg-type]

```
  
---|---  
##  LangchainPromptTemplate #
Bases: `BasePromptTemplate`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`selector` |  `Any` |  |  _required_  
`requires_langchain_llm` |  `bool` |  |  `False`  
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
class LangchainPromptTemplate(BasePromptTemplate):  # type: ignore[no-redef]
    selector: Any
    requires_langchain_llm: bool = False

    def __init__(
        self,
        template: Optional["LangchainTemplate"] = None,
        selector: Optional["LangchainSelector"] = None,
        output_parser: Optional[BaseOutputParser] = None,
        prompt_type: str = PromptType.CUSTOM,
        metadata: Optional[Dict[str, Any]] = None,
        template_var_mappings: Optional[Dict[str, Any]] = None,
        function_mappings: Optional[Dict[str, Callable]] = None,
        requires_langchain_llm: bool = False,
    ) -> None:
        try:
            from llama_index.core.bridge.langchain import (
                ConditionalPromptSelector as LangchainSelector,
            )
        except ImportError:
            raise ImportError(
                "Must install `llama_index[langchain]` to use LangchainPromptTemplate."
            )
        if selector is None:
            if template is None:
                raise ValueError("Must provide either template or selector.")
            selector = LangchainSelector(default_prompt=template)
        else:
            if template is not None:
                raise ValueError("Must provide either template or selector.")
            selector = selector

        kwargs = selector.default_prompt.partial_variables
        template_vars = selector.default_prompt.input_variables

        if metadata is None:
            metadata = {}
        metadata["prompt_type"] = prompt_type

        super().__init__(
            selector=selector,
            metadata=metadata,
            kwargs=kwargs,
            template_vars=template_vars,
            output_parser=output_parser,
            template_var_mappings=template_var_mappings,
            function_mappings=function_mappings,
            requires_langchain_llm=requires_langchain_llm,
        )

    def partial_format(self, **kwargs: Any) -> "BasePromptTemplate":
        """Partially format the prompt."""
        from llama_index.core.bridge.langchain import (
            ConditionalPromptSelector as LangchainSelector,
        )

        mapped_kwargs = self._map_all_vars(kwargs)
        default_prompt = self.selector.default_prompt.partial(**mapped_kwargs)
        conditionals = [
            (condition, prompt.partial(**mapped_kwargs))
            for condition, prompt in self.selector.conditionals
        ]
        lc_selector = LangchainSelector(
            default_prompt=default_prompt, conditionals=conditionals
        )

        # copy full prompt object, replace selector
        lc_prompt = deepcopy(self)
        lc_prompt.selector = lc_selector
        return lc_prompt

    def format(self, llm: Optional[BaseLLM] = None, **kwargs: Any) -> str:
        """Format the prompt into a string."""
        from llama_index.llms.langchain import LangChainLLM  # pants: no-infer-dep

        if llm is not None:
            # if llamaindex LLM is provided, and we require a langchain LLM,
            # then error. but otherwise if `requires_langchain_llm` is False,
            # then we can just use the default prompt
            if not isinstance(llm, LangChainLLM) and self.requires_langchain_llm:
                raise ValueError("Must provide a LangChainLLM.")
            elif not isinstance(llm, LangChainLLM):
                lc_template = self.selector.default_prompt
            else:
                lc_template = self.selector.get_prompt(llm=llm.llm)
        else:
            lc_template = self.selector.default_prompt

        # if there's mappings specified, make sure those are used
        mapped_kwargs = self._map_all_vars(kwargs)
        return lc_template.format(**mapped_kwargs)

    def format_messages(
        self, llm: Optional[BaseLLM] = None, **kwargs: Any
    ) -> List[ChatMessage]:
        """Format the prompt into a list of chat messages."""
        from llama_index.llms.langchain import LangChainLLM  # pants: no-infer-dep
        from llama_index.llms.langchain.utils import (
            from_lc_messages,
        )  # pants: no-infer-dep

        if llm is not None:
            # if llamaindex LLM is provided, and we require a langchain LLM,
            # then error. but otherwise if `requires_langchain_llm` is False,
            # then we can just use the default prompt
            if not isinstance(llm, LangChainLLM) and self.requires_langchain_llm:
                raise ValueError("Must provide a LangChainLLM.")
            elif not isinstance(llm, LangChainLLM):
                lc_template = self.selector.default_prompt
            else:
                lc_template = self.selector.get_prompt(llm=llm.llm)
        else:
            lc_template = self.selector.default_prompt

        # if there's mappings specified, make sure those are used
        mapped_kwargs = self._map_all_vars(kwargs)
        lc_prompt_value = lc_template.format_prompt(**mapped_kwargs)
        lc_messages = lc_prompt_value.to_messages()
        return from_lc_messages(lc_messages)

    def get_template(self, llm: Optional[BaseLLM] = None) -> str:
        from llama_index.llms.langchain import LangChainLLM  # pants: no-infer-dep

        if llm is not None:
            # if llamaindex LLM is provided, and we require a langchain LLM,
            # then error. but otherwise if `requires_langchain_llm` is False,
            # then we can just use the default prompt
            if not isinstance(llm, LangChainLLM) and self.requires_langchain_llm:
                raise ValueError("Must provide a LangChainLLM.")
            elif not isinstance(llm, LangChainLLM):
                lc_template = self.selector.default_prompt
            else:
                lc_template = self.selector.get_prompt(llm=llm.llm)
        else:
            lc_template = self.selector.default_prompt

        try:
            return str(lc_template.template)  # type: ignore
        except AttributeError:
            return str(lc_template)

```
  
---|---  
###  partial_format #
```
partial_format(**kwargs: Any) -> BasePromptTemplate

```

Partially format the prompt.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def partial_format(self, **kwargs: Any) -> "BasePromptTemplate":
    """Partially format the prompt."""
    from llama_index.core.bridge.langchain import (
        ConditionalPromptSelector as LangchainSelector,
    )

    mapped_kwargs = self._map_all_vars(kwargs)
    default_prompt = self.selector.default_prompt.partial(**mapped_kwargs)
    conditionals = [
        (condition, prompt.partial(**mapped_kwargs))
        for condition, prompt in self.selector.conditionals
    ]
    lc_selector = LangchainSelector(
        default_prompt=default_prompt, conditionals=conditionals
    )

    # copy full prompt object, replace selector
    lc_prompt = deepcopy(self)
    lc_prompt.selector = lc_selector
    return lc_prompt

```
  
---|---  
###  format #
```
format(llm: Optional[BaseLLM] = None, **kwargs: Any) -> str

```

Format the prompt into a string.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def format(self, llm: Optional[BaseLLM] = None, **kwargs: Any) -> str:
    """Format the prompt into a string."""
    from llama_index.llms.langchain import LangChainLLM  # pants: no-infer-dep

    if llm is not None:
        # if llamaindex LLM is provided, and we require a langchain LLM,
        # then error. but otherwise if `requires_langchain_llm` is False,
        # then we can just use the default prompt
        if not isinstance(llm, LangChainLLM) and self.requires_langchain_llm:
            raise ValueError("Must provide a LangChainLLM.")
        elif not isinstance(llm, LangChainLLM):
            lc_template = self.selector.default_prompt
        else:
            lc_template = self.selector.get_prompt(llm=llm.llm)
    else:
        lc_template = self.selector.default_prompt

    # if there's mappings specified, make sure those are used
    mapped_kwargs = self._map_all_vars(kwargs)
    return lc_template.format(**mapped_kwargs)

```
  
---|---  
###  format_messages #
```
format_messages(llm: Optional[BaseLLM] = None, **kwargs: Any) -> List[ChatMessage]

```

Format the prompt into a list of chat messages.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def format_messages(
    self, llm: Optional[BaseLLM] = None, **kwargs: Any
) -> List[ChatMessage]:
    """Format the prompt into a list of chat messages."""
    from llama_index.llms.langchain import LangChainLLM  # pants: no-infer-dep
    from llama_index.llms.langchain.utils import (
        from_lc_messages,
    )  # pants: no-infer-dep

    if llm is not None:
        # if llamaindex LLM is provided, and we require a langchain LLM,
        # then error. but otherwise if `requires_langchain_llm` is False,
        # then we can just use the default prompt
        if not isinstance(llm, LangChainLLM) and self.requires_langchain_llm:
            raise ValueError("Must provide a LangChainLLM.")
        elif not isinstance(llm, LangChainLLM):
            lc_template = self.selector.default_prompt
        else:
            lc_template = self.selector.get_prompt(llm=llm.llm)
    else:
        lc_template = self.selector.default_prompt

    # if there's mappings specified, make sure those are used
    mapped_kwargs = self._map_all_vars(kwargs)
    lc_prompt_value = lc_template.format_prompt(**mapped_kwargs)
    lc_messages = lc_prompt_value.to_messages()
    return from_lc_messages(lc_messages)

```
  
---|---  
##  PromptTemplate #
Bases: `BasePromptTemplate`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`template` |  `str` |  |  _required_  
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
class PromptTemplate(BasePromptTemplate):  # type: ignore[no-redef]
    template: str

    def __init__(
        self,
        template: str,
        prompt_type: str = PromptType.CUSTOM,
        output_parser: Optional[BaseOutputParser] = None,
        metadata: Optional[Dict[str, Any]] = None,
        template_var_mappings: Optional[Dict[str, Any]] = None,
        function_mappings: Optional[Dict[str, Callable]] = None,
        **kwargs: Any,
    ) -> None:
        if metadata is None:
            metadata = {}
        metadata["prompt_type"] = prompt_type

        template_vars = get_template_vars(template)

        super().__init__(
            template=template,
            template_vars=template_vars,
            kwargs=kwargs,
            metadata=metadata,
            output_parser=output_parser,
            template_var_mappings=template_var_mappings,
            function_mappings=function_mappings,
        )

    def partial_format(self, **kwargs: Any) -> "PromptTemplate":
        """Partially format the prompt."""
        # NOTE: this is a hack to get around deepcopy failing on output parser
        output_parser = self.output_parser
        self.output_parser = None

        # get function and fixed kwargs, and add that to a copy
        # of the current prompt object
        prompt = deepcopy(self)
        prompt.kwargs.update(kwargs)

        # NOTE: put the output parser back
        prompt.output_parser = output_parser
        self.output_parser = output_parser
        return prompt

    def format(
        self,
        llm: Optional[BaseLLM] = None,
        completion_to_prompt: Optional[Callable[[str], str]] = None,
        **kwargs: Any,
    ) -> str:
        """Format the prompt into a string."""
        del llm  # unused
        all_kwargs = {
            **self.kwargs,
            **kwargs,
        }

        mapped_all_kwargs = self._map_all_vars(all_kwargs)
        prompt = format_string(self.template, **mapped_all_kwargs)

        if self.output_parser is not None:
            prompt = self.output_parser.format(prompt)

        if completion_to_prompt is not None:
            prompt = completion_to_prompt(prompt)

        return prompt

    def format_messages(
        self, llm: Optional[BaseLLM] = None, **kwargs: Any
    ) -> List[ChatMessage]:
        """Format the prompt into a list of chat messages."""
        del llm  # unused
        prompt = self.format(**kwargs)
        return prompt_to_messages(prompt)

    def get_template(self, llm: Optional[BaseLLM] = None) -> str:
        return self.template

```
  
---|---  
###  partial_format #
```
partial_format(**kwargs: Any) -> PromptTemplate

```

Partially format the prompt.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def partial_format(self, **kwargs: Any) -> "PromptTemplate":
    """Partially format the prompt."""
    # NOTE: this is a hack to get around deepcopy failing on output parser
    output_parser = self.output_parser
    self.output_parser = None

    # get function and fixed kwargs, and add that to a copy
    # of the current prompt object
    prompt = deepcopy(self)
    prompt.kwargs.update(kwargs)

    # NOTE: put the output parser back
    prompt.output_parser = output_parser
    self.output_parser = output_parser
    return prompt

```
  
---|---  
###  format #
```
format(llm: Optional[BaseLLM] = None, completion_to_prompt: Optional[Callable[[str], str]] = None, **kwargs: Any) -> str

```

Format the prompt into a string.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def format(
    self,
    llm: Optional[BaseLLM] = None,
    completion_to_prompt: Optional[Callable[[str], str]] = None,
    **kwargs: Any,
) -> str:
    """Format the prompt into a string."""
    del llm  # unused
    all_kwargs = {
        **self.kwargs,
        **kwargs,
    }

    mapped_all_kwargs = self._map_all_vars(all_kwargs)
    prompt = format_string(self.template, **mapped_all_kwargs)

    if self.output_parser is not None:
        prompt = self.output_parser.format(prompt)

    if completion_to_prompt is not None:
        prompt = completion_to_prompt(prompt)

    return prompt

```
  
---|---  
###  format_messages #
```
format_messages(llm: Optional[BaseLLM] = None, **kwargs: Any) -> List[ChatMessage]

```

Format the prompt into a list of chat messages.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def format_messages(
    self, llm: Optional[BaseLLM] = None, **kwargs: Any
) -> List[ChatMessage]:
    """Format the prompt into a list of chat messages."""
    del llm  # unused
    prompt = self.format(**kwargs)
    return prompt_to_messages(prompt)

```
  
---|---  
##  PromptType #
Bases: `str`, `Enum`
Prompt type.
Source code in `llama-index-core/llama_index/core/prompts/prompt_type.py`

| ```
class PromptType(str, Enum):
    """Prompt type."""

    # summarization
    SUMMARY = "summary"
    # tree insert node
    TREE_INSERT = "insert"
    # tree select query prompt
    TREE_SELECT = "tree_select"
    # tree select query prompt (multiple)
    TREE_SELECT_MULTIPLE = "tree_select_multiple"
    # question-answer
    QUESTION_ANSWER = "text_qa"
    # refine
    REFINE = "refine"
    # keyword extract
    KEYWORD_EXTRACT = "keyword_extract"
    # query keyword extract
    QUERY_KEYWORD_EXTRACT = "query_keyword_extract"

    # schema extract
    SCHEMA_EXTRACT = "schema_extract"

    # text to sql
    TEXT_TO_SQL = "text_to_sql"

    # text to graph query
    TEXT_TO_GRAPH_QUERY = "text_to_graph_query"

    # table context
    TABLE_CONTEXT = "table_context"

    # KG extraction prompt
    KNOWLEDGE_TRIPLET_EXTRACT = "knowledge_triplet_extract"

    # Simple Input prompt
    SIMPLE_INPUT = "simple_input"

    # Pandas prompt
    PANDAS = "pandas"

    # JSON path prompt
    JSON_PATH = "json_path"

    # Single select prompt
    SINGLE_SELECT = "single_select"

    # Multiple select prompt
    MULTI_SELECT = "multi_select"

    VECTOR_STORE_QUERY = "vector_store_query"

    # Sub question prompt
    SUB_QUESTION = "sub_question"

    # SQL response synthesis prompt
    SQL_RESPONSE_SYNTHESIS = "sql_response_synthesis"

    # SQL response synthesis prompt (v2)
    SQL_RESPONSE_SYNTHESIS_V2 = "sql_response_synthesis_v2"

    # Conversation
    CONVERSATION = "conversation"

    # Decompose query transform
    DECOMPOSE = "decompose"

    # Choice select
    CHOICE_SELECT = "choice_select"

    # custom (by default)
    CUSTOM = "custom"

    # RankGPT rerank
    RANKGPT_RERANK = "rankgpt_rerank"

```
  
---|---  
##  SelectorPromptTemplate #
Bases: `BasePromptTemplate`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`default_template` |  `BasePromptTemplate` |  |  _required_  
`conditionals` |  `Sequence[Tuple[Callable[list, bool], BasePromptTemplate]] | None` |  |  `None`  
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
class SelectorPromptTemplate(BasePromptTemplate):  # type: ignore[no-redef]
    default_template: SerializeAsAny[BasePromptTemplate]
    conditionals: Optional[
        Sequence[Tuple[Callable[[BaseLLM], bool], BasePromptTemplate]]
    ] = None

    def __init__(
        self,
        default_template: BasePromptTemplate,
        conditionals: Optional[
            Sequence[Tuple[Callable[[BaseLLM], bool], BasePromptTemplate]]
        ] = None,
    ):
        metadata = default_template.metadata
        kwargs = default_template.kwargs
        template_vars = default_template.template_vars
        output_parser = default_template.output_parser
        super().__init__(
            default_template=default_template,
            conditionals=conditionals,
            metadata=metadata,
            kwargs=kwargs,
            template_vars=template_vars,
            output_parser=output_parser,
        )

    def select(self, llm: Optional[BaseLLM] = None) -> BasePromptTemplate:
        # ensure output parser is up to date
        self.default_template.output_parser = self.output_parser

        if llm is None:
            return self.default_template

        if self.conditionals is not None:
            for condition, prompt in self.conditionals:
                if condition(llm):
                    # ensure output parser is up to date
                    prompt.output_parser = self.output_parser
                    return prompt

        return self.default_template

    def partial_format(self, **kwargs: Any) -> "SelectorPromptTemplate":
        default_template = self.default_template.partial_format(**kwargs)
        if self.conditionals is None:
            conditionals = None
        else:
            conditionals = [
                (condition, prompt.partial_format(**kwargs))
                for condition, prompt in self.conditionals
            ]
        return SelectorPromptTemplate(
            default_template=default_template, conditionals=conditionals
        )

    def format(self, llm: Optional[BaseLLM] = None, **kwargs: Any) -> str:
        """Format the prompt into a string."""
        prompt = self.select(llm=llm)
        return prompt.format(**kwargs)

    def format_messages(
        self, llm: Optional[BaseLLM] = None, **kwargs: Any
    ) -> List[ChatMessage]:
        """Format the prompt into a list of chat messages."""
        prompt = self.select(llm=llm)
        return prompt.format_messages(**kwargs)

    def get_template(self, llm: Optional[BaseLLM] = None) -> str:
        prompt = self.select(llm=llm)
        return prompt.get_template(llm=llm)

```
  
---|---  
###  format #
```
format(llm: Optional[BaseLLM] = None, **kwargs: Any) -> str

```

Format the prompt into a string.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def format(self, llm: Optional[BaseLLM] = None, **kwargs: Any) -> str:
    """Format the prompt into a string."""
    prompt = self.select(llm=llm)
    return prompt.format(**kwargs)

```
  
---|---  
###  format_messages #
```
format_messages(llm: Optional[BaseLLM] = None, **kwargs: Any) -> List[ChatMessage]

```

Format the prompt into a list of chat messages.
Source code in `llama-index-core/llama_index/core/prompts/base.py`

| ```
def format_messages(
    self, llm: Optional[BaseLLM] = None, **kwargs: Any
) -> List[ChatMessage]:
    """Format the prompt into a list of chat messages."""
    prompt = self.select(llm=llm)
    return prompt.format_messages(**kwargs)

```
  
---|---  
##  RichPromptTemplate #
Bases: `BasePromptTemplate`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`template_str` |  `str` |  The template string for the prompt. |  _required_  
Source code in `llama-index-core/llama_index/core/prompts/rich.py`

| ```
class RichPromptTemplate(BasePromptTemplate):  # type: ignore[no-redef]
    template_str: str = Field(description="The template string for the prompt.")

    def __init__(
        self,
        template_str: str,
        metadata: Optional[Dict[str, Any]] = None,
        output_parser: Optional[BaseOutputParser] = None,
        template_vars: Optional[List[str]] = None,
        template_var_mappings: Optional[Dict[str, Any]] = None,
        function_mappings: Optional[Dict[str, Callable]] = None,
        **kwargs: Any,
    ):
        template_vars = template_vars or []
        if not template_vars:
            template_vars = Prompt(template_str).variables

        super().__init__(
            template_str=template_str,
            kwargs=kwargs or {},
            metadata=metadata or {},
            output_parser=output_parser,
            template_vars=template_vars,
            template_var_mappings=template_var_mappings,
            function_mappings=function_mappings,
        )

    @property
    def is_chat_template(self) -> bool:
        return "endchat" in self.template_str

    def partial_format(self, **kwargs: Any) -> "RichPromptTemplate":
        prompt = deepcopy(self)
        prompt.kwargs.update(kwargs)
        return prompt

    def format(
        self,
        llm: Optional[BaseLLM] = None,
        messages_to_prompt: Optional[Callable[[Sequence[ChatMessage]], str]] = None,
        **kwargs: Any,
    ) -> str:
        del llm  # unused

        if self.is_chat_template:
            messages = self.format_messages(**kwargs)

            if messages_to_prompt is not None:
                return messages_to_prompt(messages)

            return default_messages_to_prompt(messages)
        else:
            all_kwargs = {
                **self.kwargs,
                **kwargs,
            }
            mapped_all_kwargs = self._map_all_vars(all_kwargs)
            return Prompt(self.template_str).text(data=mapped_all_kwargs)

    def format_messages(
        self, llm: Optional[BaseLLM] = None, **kwargs: Any
    ) -> List[ChatMessage]:
        del llm  # unused
        """Format the prompt into a list of chat messages."""
        all_kwargs = {
            **self.kwargs,
            **kwargs,
        }
        mapped_all_kwargs = self._map_all_vars(all_kwargs)

        banks_prompt = Prompt(self.template_str)
        banks_messages = banks_prompt.chat_messages(data=mapped_all_kwargs)

        llama_messages: list[ChatMessage] = []
        for bank_message in banks_messages:
            if isinstance(bank_message.content, str):
                llama_messages.append(
                    ChatMessage(role=bank_message.role, content=bank_message.content)
                )
            elif isinstance(bank_message.content, list):
                llama_blocks: list[ContentBlock] = []
                for bank_block in bank_message.content:
                    if bank_block.type == BanksContentBlockType.text:
                        llama_blocks.append(TextBlock(text=bank_block.text))
                    elif bank_block.type == BanksContentBlockType.image_url:
                        llama_blocks.append(ImageBlock(url=bank_block.image_url.url))
                    elif bank_block.type == BanksContentBlockType.audio:
                        llama_blocks.append(
                            AudioBlock(audio=bank_block.input_audio.data)
                        )
                    else:
                        raise ValueError(
                            f"Unsupported content block type: {bank_block.type}"
                        )

                llama_messages.append(
                    ChatMessage(role=bank_message.role, content=llama_blocks)
                )
            else:
                raise ValueError(
                    f"Unsupported message content type: {type(bank_message.content)}"
                )

        if self.output_parser is not None:
            llama_messages = self.output_parser.format_messages(llama_messages)

        return llama_messages

    def get_template(self, llm: Optional[BaseLLM] = None) -> str:
        return self.template_str

```
  
---|---  
##  display_prompt_dict #
```
display_prompt_dict(prompts_dict: PromptDictType) -> None

```

Display prompt dict.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`prompts_dict` |  `PromptDictType` |  prompt dict |  _required_  
Source code in `llama-index-core/llama_index/core/prompts/display_utils.py`

| ```
def display_prompt_dict(prompts_dict: PromptDictType) -> None:
    """
    Display prompt dict.

    Args:
        prompts_dict: prompt dict

    """
    from IPython.display import Markdown, display

    for k, p in prompts_dict.items():
        text_md = f"**Prompt Key**: {k}<br>**Text:** <br>"
        display(Markdown(text_md))
        print(p.get_template())
        display(Markdown("<br><br>"))

```
  
---|---
