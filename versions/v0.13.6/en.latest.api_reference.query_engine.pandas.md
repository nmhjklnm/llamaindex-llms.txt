# Pandas
##  PandasQueryEngine #
Bases: `BaseQueryEngine`
Pandas query engine.
Convert natural language to Pandas python code.
WARNING: This tool provides the Agent access to the `eval` function. Arbitrary code execution is possible on the machine running this tool. This tool is not recommended to be used in a production setting, and would require heavy sandboxing or virtual machines
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`df` |  `DataFrame` |  Pandas dataframe to use. |  _required_  
`instruction_str` |  `Optional[str]` |  Instruction string to use. |  `None`  
`instruction_parser` |  `Optional[PandasInstructionParser]` |  The output parser that takes the pandas query output string and returns a string. It defaults to PandasInstructionParser and takes pandas DataFrame, and any output kwargs as parameters. eg.kwargs["max_colwidth"] = [int] is used to set the length of text that each column can display during str(df). Set it to a higher number if there is possibly long text in the dataframe. |  `None`  
`pandas_prompt` |  `Optional[BasePromptTemplate]` |  Pandas prompt to use. |  `None`  
`output_kwargs` |  `dict` |  Additional output processor kwargs for the PandasInstructionParser. |  `None`  
`head` |  `int` |  Number of rows to show in the table context. |  `5`  
`verbose` |  `bool` |  Whether to print verbose output. |  `False`  
`llm` |  `Optional[LLM]` |  Language model to use. |  `None`  
`synthesize_response` |  `bool` |  Whether to synthesize a response from the query results. Defaults to False. |  `False`  
`response_synthesis_prompt` |  `Optional[BasePromptTemplate]` |  A Response Synthesis BasePromptTemplate to use for the query. Defaults to DEFAULT_RESPONSE_SYNTHESIS_PROMPT. |  `None`  
Examples:
`pip install llama-index-experimental`
```
import pandas as pd
from llama_index.experimental.query_engine.pandas import PandasQueryEngine

df = pd.DataFrame(
    {
        "city": ["Toronto", "Tokyo", "Berlin"],
        "population": [2930000, 13960000, 3645000]
    }
)

query_engine = PandasQueryEngine(df=df, verbose=True)

response = query_engine.query("What is the population of Tokyo?")

```

Source code in `llama-index-experimental/llama_index/experimental/query_engine/pandas/pandas_query_engine.py`

| ```
class PandasQueryEngine(BaseQueryEngine):
    """
    Pandas query engine.

    Convert natural language to Pandas python code.

    WARNING: This tool provides the Agent access to the `eval` function.
    Arbitrary code execution is possible on the machine running this tool.
    This tool is not recommended to be used in a production setting, and would
    require heavy sandboxing or virtual machines


    Args:
        df (pd.DataFrame): Pandas dataframe to use.
        instruction_str (Optional[str]): Instruction string to use.
        instruction_parser (Optional[PandasInstructionParser]): The output parser
            that takes the pandas query output string and returns a string.
            It defaults to PandasInstructionParser and takes pandas DataFrame,
            and any output kwargs as parameters.
            eg.kwargs["max_colwidth"] = [int] is used to set the length of text
            that each column can display during str(df). Set it to a higher number
            if there is possibly long text in the dataframe.
        pandas_prompt (Optional[BasePromptTemplate]): Pandas prompt to use.
        output_kwargs (dict): Additional output processor kwargs for the
            PandasInstructionParser.
        head (int): Number of rows to show in the table context.
        verbose (bool): Whether to print verbose output.
        llm (Optional[LLM]): Language model to use.
        synthesize_response (bool): Whether to synthesize a response from the
            query results. Defaults to False.
        response_synthesis_prompt (Optional[BasePromptTemplate]): A
            Response Synthesis BasePromptTemplate to use for the query. Defaults to
            DEFAULT_RESPONSE_SYNTHESIS_PROMPT.

    Examples:
        `pip install llama-index-experimental`

    ```python
        import pandas as pd
        from llama_index.experimental.query_engine.pandas import PandasQueryEngine

        df = pd.DataFrame(
            {
                "city": ["Toronto", "Tokyo", "Berlin"],
                "population": [2930000, 13960000, 3645000]
            }
        )

        query_engine = PandasQueryEngine(df=df, verbose=True)

        response = query_engine.query("What is the population of Tokyo?")
    ```

    """

    def __init__(
        self,
        df: pd.DataFrame,
        instruction_str: Optional[str] = None,
        instruction_parser: Optional[PandasInstructionParser] = None,
        pandas_prompt: Optional[BasePromptTemplate] = None,
        output_kwargs: Optional[dict] = None,
        head: int = 5,
        verbose: bool = False,
        llm: Optional[LLM] = None,
        synthesize_response: bool = False,
        response_synthesis_prompt: Optional[BasePromptTemplate] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        self._df = df

        self._head = head
        self._pandas_prompt = pandas_prompt or DEFAULT_PANDAS_PROMPT
        self._instruction_str = instruction_str or DEFAULT_INSTRUCTION_STR
        self._instruction_parser = instruction_parser or PandasInstructionParser(
            df, output_kwargs or {}
        )
        self._verbose = verbose

        self._llm = llm or Settings.llm
        self._synthesize_response = synthesize_response
        self._response_synthesis_prompt = (
            response_synthesis_prompt or DEFAULT_RESPONSE_SYNTHESIS_PROMPT
        )

        super().__init__(callback_manager=Settings.callback_manager)

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {}

    def _get_prompts(self) -> Dict[str, Any]:
        """Get prompts."""
        return {
            "pandas_prompt": self._pandas_prompt,
            "response_synthesis_prompt": self._response_synthesis_prompt,
        }

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "pandas_prompt" in prompts:
            self._pandas_prompt = prompts["pandas_prompt"]
        if "response_synthesis_prompt" in prompts:
            self._response_synthesis_prompt = prompts["response_synthesis_prompt"]

    @classmethod
    def from_index(cls, index: PandasIndex, **kwargs: Any) -> "PandasQueryEngine":
        logger.warning(
            "PandasIndex is deprecated. "
            "Directly construct PandasQueryEngine with df instead."
        )
        return cls(df=index.df, **kwargs)

    def _get_table_context(self) -> str:
        """Get table context."""
        return str(self._df.head(self._head))

    def _query(self, query_bundle: QueryBundle) -> Response:
        """Answer a query."""
        context = self._get_table_context()

        pandas_response_str = self._llm.predict(
            self._pandas_prompt,
            df_str=context,
            query_str=query_bundle.query_str,
            instruction_str=self._instruction_str,
        )

        if self._verbose:
            print_text(f"> Pandas Instructions:\n```\n{pandas_response_str}\n```\n")
        pandas_output = self._instruction_parser.parse(pandas_response_str)
        if self._verbose:
            print_text(f"> Pandas Output: {pandas_output}\n")

        response_metadata = {
            "pandas_instruction_str": pandas_response_str,
            "raw_pandas_output": pandas_output,
        }
        if self._synthesize_response:
            response_str = str(
                self._llm.predict(
                    self._response_synthesis_prompt,
                    query_str=query_bundle.query_str,
                    pandas_instructions=pandas_response_str,
                    pandas_output=pandas_output,
                )
            )
        else:
            response_str = str(pandas_output)

        return Response(response=response_str, metadata=response_metadata)

    async def _aquery(self, query_bundle: QueryBundle) -> Response:
        return self._query(query_bundle)

```
  
---|---
