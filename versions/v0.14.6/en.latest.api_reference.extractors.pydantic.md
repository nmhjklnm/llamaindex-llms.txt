# Pydantic
##  PydanticProgramExtractor #
Bases: `BaseExtractor`, `Generic[Model]`
Pydantic program extractor.
Uses an LLM to extract out a Pydantic object. Return attributes of that object in a dictionary.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`program` |  `BasePydanticProgram[TypeVar]` |  Pydantic program to extract. |  _required_  
`input_key` |  `str` |  Key to use as input to the program (the program template string must expose this key). |  `'input'`  
`extract_template_str` |  `str` |  Template to use for extraction. |  `'Here is the content of the section:\n----------------\n{context_str}\n----------------\nGiven the contextual information, extract out a {class_name} object.'`  
Source code in `llama-index-core/llama_index/core/extractors/metadata_extractors.py`

| ```
class PydanticProgramExtractor(BaseExtractor, Generic[Model]):
    """
    Pydantic program extractor.

    Uses an LLM to extract out a Pydantic object. Return attributes of that object
    in a dictionary.

    """

    program: SerializeAsAny[BasePydanticProgram[Model]] = Field(
        ..., description="Pydantic program to extract."
    )
    input_key: str = Field(
        default="input",
        description=(
            "Key to use as input to the program (the program "
            "template string must expose this key)."
        ),
    )
    extract_template_str: str = Field(
        default=DEFAULT_EXTRACT_TEMPLATE_STR,
        description="Template to use for extraction.",
    )

    @classmethod
    def class_name(cls) -> str:
        return "PydanticModelExtractor"

    async def _acall_program(self, node: BaseNode) -> Dict[str, Any]:
        """Call the program on a node."""
        if self.is_text_node_only and not isinstance(node, TextNode):
            return {}

        extract_str = self.extract_template_str.format(
            context_str=node.get_content(metadata_mode=self.metadata_mode),
            class_name=self.program.output_cls.__name__,
        )

        ret_object = await self.program.acall(**{self.input_key: extract_str})
        assert not isinstance(ret_object, list)

        return ret_object.model_dump()

    async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
        """Extract pydantic program."""
        program_jobs = []
        for node in nodes:
            program_jobs.append(self._acall_program(node))

        metadata_list: List[Dict] = await run_jobs(
            program_jobs, show_progress=self.show_progress, workers=self.num_workers
        )

        return metadata_list

```
  
---|---  
###  aextract `async` #
```
aextract(nodes: Sequence[BaseNode]) -> List[Dict]

```

Extract pydantic program.
Source code in `llama-index-core/llama_index/core/extractors/metadata_extractors.py`

| ```
async def aextract(self, nodes: Sequence[BaseNode]) -> List[Dict]:
    """Extract pydantic program."""
    program_jobs = []
    for node in nodes:
        program_jobs.append(self._acall_program(node))

    metadata_list: List[Dict] = await run_jobs(
        program_jobs, show_progress=self.show_progress, workers=self.num_workers
    )

    return metadata_list

```
  
---|---
