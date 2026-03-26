# Index
##  BaseQuestionGenerator #
Bases: `PromptMixin`, `DispatcherSpanMixin`
Source code in `llama-index-core/llama_index/core/question_gen/types.py`

| ```
class BaseQuestionGenerator(PromptMixin, DispatcherSpanMixin):
    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt modules."""
        return {}

    @abstractmethod
    def generate(
        self, tools: Sequence[ToolMetadata], query: QueryBundle
    ) -> List[SubQuestion]:
        pass

    @abstractmethod
    async def agenerate(
        self, tools: Sequence[ToolMetadata], query: QueryBundle
    ) -> List[SubQuestion]:
        pass

```
  
---|---  
##  SubQuestionList #
Bases: `BaseModel`
A pydantic object wrapping a list of sub-questions.
This is mostly used to make getting a json schema easier.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`items` |  `List[SubQuestion]` |  |  _required_  
Source code in `llama-index-core/llama_index/core/question_gen/types.py`

| ```
class SubQuestionList(BaseModel):
    """
    A pydantic object wrapping a list of sub-questions.

    This is mostly used to make getting a json schema easier.
    """

    items: List[SubQuestion]

```
  
---|---  
##  SubQuestion #
Bases: `BaseModel`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`sub_question` |  `str` |  |  _required_  
`tool_name` |  `str` |  |  _required_  
Source code in `llama-index-core/llama_index/core/question_gen/types.py`

| ```
class SubQuestion(BaseModel):
    sub_question: str
    tool_name: str

```
  
---|---
