# Longrag
##  LongRAGPack #
Bases: `BaseLlamaPack`
Implements Long RAG.
This implementation is based on the following paper: https://arxiv.org/pdf/2406.15319
Source code in `llama-index-packs/llama-index-packs-longrag/llama_index/packs/longrag/base.py`

| ```
class LongRAGPack(BaseLlamaPack):
    """
    Implements Long RAG.

    This implementation is based on the following paper: https://arxiv.org/pdf/2406.15319
    """

    def __init__(
        self,
        data_dir: str,
        llm: t.Optional[LLM] = None,
        chunk_size: t.Optional[int] = DEFAULT_CHUNK_SIZE,
        similarity_top_k: int = DEFAULT_TOP_K,
        small_chunk_size: int = DEFAULT_SMALL_CHUNK_SIZE,
        index: t.Optional[VectorStoreIndex] = None,
        index_kwargs: t.Optional[t.Dict[str, t.Any]] = None,
        verbose: bool = False,
    ):
        """
        Constructor.

        Args:
            data_dir (str): Data directory
            llm (t.Optional[LLM]): LLM
            chunk_size (Optional[int], optional): Splits each doc to chunk_size to demonstrate grouping. Set to None to disable splitting then grouping. Defaults to DEFAULT_CHUNK_SIZE.
            similarity_top_k (int, optional): Top k. Defaults to DEFAULT_TOP_K.
            small_chunk_size (int, optional): Small chunk size to split large documents into smaller embeddings of small_chunk_size. Defaults to DEFAULT_SMALL_CHUNK_SIZE.
            index (Optional[VectorStoreIndex], optional): Vector index to use (from persist dir). If None, creates a new vector index. Defaults to None
            index_kwargs (Optional[Dict[str, Any]], optional): Kwargs to use when constructing VectorStoreIndex. Defaults to None.
            verbose (bool, Optional): Verbose mode. Defaults to False

        """
        # initialize workflow
        self._wf = LongRAGWorkflow(verbose=verbose)

        # initialize vars
        self._data_dir = data_dir
        self._llm = llm or Settings.llm
        self._chunk_size = chunk_size
        self._similarity_top_k = similarity_top_k
        self._small_chunk_size = small_chunk_size

        # run wf initialization
        result = asyncio_run(
            self._wf.run(
                data_dir=self._data_dir,
                llm=self._llm,
                chunk_size=self._chunk_size,
                similarity_top_k=self._similarity_top_k,
                small_chunk_size=self._small_chunk_size,
                index=index,
                index_kwargs=index_kwargs,
            )
        )

        self._retriever = result["retriever"]
        self._query_eng = result["query_engine"]
        self._index = result["index"]

    def get_modules(self) -> t.Dict[str, t.Any]:
        """Get Modules."""
        return {
            "query_engine": self._query_eng,
            "llm": self._llm,
            "retriever": self._retriever,
            "index": self._index,
            "workflow": self._wf,
        }

    def run(self, query: str, *args: t.Any, **kwargs: t.Any) -> t.Any:
        """Runs pipeline."""
        return asyncio_run(self._wf.run(query_str=query))

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get Modules.
Source code in `llama-index-packs/llama-index-packs-longrag/llama_index/packs/longrag/base.py`

| ```
def get_modules(self) -> t.Dict[str, t.Any]:
    """Get Modules."""
    return {
        "query_engine": self._query_eng,
        "llm": self._llm,
        "retriever": self._retriever,
        "index": self._index,
        "workflow": self._wf,
    }

```
  
---|---  
###  run #
```
run(query: str, *args: Any, **kwargs: Any) -> Any

```

Runs pipeline.
Source code in `llama-index-packs/llama-index-packs-longrag/llama_index/packs/longrag/base.py`

| ```
def run(self, query: str, *args: t.Any, **kwargs: t.Any) -> t.Any:
    """Runs pipeline."""
    return asyncio_run(self._wf.run(query_str=query))

```
  
---|---
