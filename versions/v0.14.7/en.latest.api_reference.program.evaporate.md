# Evaporate
##  DFEvaporateProgram #
Bases: `BaseEvaporateProgram[DataFrameRowsOnly]`
Evaporate DF program.
Given a set of fields, extracts a dataframe from a set of nodes. Each node corresponds to a row in the dataframe - each value in the row corresponds to a field value.
Source code in `llama-index-integrations/program/llama-index-program-evaporate/llama_index/program/evaporate/base.py`

| ```
class DFEvaporateProgram(BaseEvaporateProgram[DataFrameRowsOnly]):
    """
    Evaporate DF program.

    Given a set of fields, extracts a dataframe from a set of nodes.
    Each node corresponds to a row in the dataframe - each value in the row
    corresponds to a field value.

    """

    def fit(
        self,
        nodes: List[BaseNode],
        field: str,
        field_context: Optional[Any] = None,
        expected_output: Optional[Any] = None,
        inplace: bool = True,
    ) -> str:
        """Given the input Nodes and fields, synthesize the python code."""
        fn = self._extractor.extract_fn_from_nodes(nodes, field)
        logger.debug(f"Extracted function: {fn}")
        if inplace:
            self._field_fns[field] = fn
        return fn

    def _inference(
        self, nodes: List[BaseNode], fn_str: str, field_name: str
    ) -> List[Any]:
        """Given the input, call the python code and return the result."""
        results = self._extractor.run_fn_on_nodes(nodes, fn_str, field_name)
        logger.debug(f"Results: {results}")
        return results

    @property
    def output_cls(self) -> Type[DataFrameRowsOnly]:
        """Output class."""
        return DataFrameRowsOnly

    def __call__(self, *args: Any, **kwds: Any) -> DataFrameRowsOnly:
        """Call evaporate on inference data."""
        # TODO: either specify `nodes` or `texts` in kwds
        if "nodes" in kwds:
            nodes = kwds["nodes"]
        elif "texts" in kwds:
            nodes = [TextNode(text=t) for t in kwds["texts"]]
        else:
            raise ValueError("Must provide either `nodes` or `texts`.")

        col_dict = {}
        for field in self._fields:
            col_dict[field] = self._inference(nodes, self._field_fns[field], field)

        df = pd.DataFrame(col_dict, columns=self._fields)

        # convert pd.DataFrame to DataFrameRowsOnly
        df_row_objs = []
        for row_arr in df.values:
            df_row_objs.append(DataFrameRow(row_values=list(row_arr)))
        return DataFrameRowsOnly(rows=df_row_objs)

```
  
---|---  
###  output_cls `property` #
```
output_cls: Type[DataFrameRowsOnly]

```

Output class.
###  fit #
```
fit(nodes: List[BaseNode], field: str, field_context: Optional[Any] = None, expected_output: Optional[Any] = None, inplace: bool = True) -> str

```

Given the input Nodes and fields, synthesize the python code.
Source code in `llama-index-integrations/program/llama-index-program-evaporate/llama_index/program/evaporate/base.py`

| ```
def fit(
    self,
    nodes: List[BaseNode],
    field: str,
    field_context: Optional[Any] = None,
    expected_output: Optional[Any] = None,
    inplace: bool = True,
) -> str:
    """Given the input Nodes and fields, synthesize the python code."""
    fn = self._extractor.extract_fn_from_nodes(nodes, field)
    logger.debug(f"Extracted function: {fn}")
    if inplace:
        self._field_fns[field] = fn
    return fn

```
  
---|---
