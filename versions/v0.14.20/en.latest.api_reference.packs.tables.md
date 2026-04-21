# Tables
##  ChainOfTablePack #
Bases: `BaseLlamaPack`
Chain of table pack.
Source code in `llama-index-packs/llama-index-packs-tables/llama_index/packs/tables/chain_of_table/base.py`

| ```
class ChainOfTablePack(BaseLlamaPack):
    """Chain of table pack."""

    def __init__(
        self,
        table: pd.DataFrame,
        llm: Optional[LLM] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        """Init params."""
        self.query_engine = ChainOfTableQueryEngine(
            table=table,
            llm=llm,
            verbose=verbose,
            **kwargs,
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "query_engine": self.query_engine,
            "llm": self.query_engine.llm,
            "query_prompt": self.query_engine.query_prompt,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.query_engine.query(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-tables/llama_index/packs/tables/chain_of_table/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "query_engine": self.query_engine,
        "llm": self.query_engine.llm,
        "query_prompt": self.query_engine.query_prompt,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-tables/llama_index/packs/tables/chain_of_table/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.query_engine.query(*args, **kwargs)

```
  
---|---  
##  MixSelfConsistencyPack #
Bases: `BaseLlamaPack`
Mix Self Consistency Pack.
Source code in `llama-index-packs/llama-index-packs-tables/llama_index/packs/tables/mix_self_consistency/base.py`

| ```
class MixSelfConsistencyPack(BaseLlamaPack):
    """Mix Self Consistency Pack."""

    def __init__(
        self,
        table: pd.DataFrame,
        llm: Optional[LLMType] = None,
        verbose: bool = False,
        normalize_table: bool = False,
        text_paths: int = 2,
        symbolic_paths: int = 2,
        aggregation_mode: AggregationMode = AggregationMode.SELF_CONSISTENCY,
        **kwargs: Any,
    ) -> None:
        self.query_engine = MixSelfConsistencyQueryEngine(
            table=table,
            llm=llm,
            verbose=verbose,
            normalize_table=normalize_table,
            text_paths=text_paths,
            symbolic_paths=symbolic_paths,
            aggregation_mode=aggregation_mode,
            **kwargs,
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "query_engine": self.query_engine,
            "llm": self.query_engine.llm,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        self.query_engine.query(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-tables/llama_index/packs/tables/mix_self_consistency/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "query_engine": self.query_engine,
        "llm": self.query_engine.llm,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-tables/llama_index/packs/tables/mix_self_consistency/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    self.query_engine.query(*args, **kwargs)

```
  
---|---
