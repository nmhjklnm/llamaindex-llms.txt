# Retrieval
Evaluation modules.
##  BaseRetrievalEvaluator #
Bases: `BaseModel`
Base Retrieval Evaluator class.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`metrics` |  `List[BaseRetrievalMetric]` |  List of metrics to evaluate |  _required_  
Source code in `llama-index-core/llama_index/core/evaluation/retrieval/base.py`

| ```
class BaseRetrievalEvaluator(BaseModel):
    """Base Retrieval Evaluator class."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    metrics: List[BaseRetrievalMetric] = Field(
        ..., description="List of metrics to evaluate"
    )

    @classmethod
    def from_metric_names(
        cls, metric_names: List[str], **kwargs: Any
    ) -> "BaseRetrievalEvaluator":
        """
        Create evaluator from metric names.

        Args:
            metric_names (List[str]): List of metric names
            **kwargs: Additional arguments for the evaluator

        """
        metric_types = resolve_metrics(metric_names)
        return cls(metrics=[metric() for metric in metric_types], **kwargs)

    @abstractmethod
    async def _aget_retrieved_ids_and_texts(
        self, query: str, mode: RetrievalEvalMode = RetrievalEvalMode.TEXT
    ) -> Tuple[List[str], List[str]]:
        """Get retrieved ids and texts."""
        raise NotImplementedError

    def evaluate(
        self,
        query: str,
        expected_ids: List[str],
        expected_texts: Optional[List[str]] = None,
        mode: RetrievalEvalMode = RetrievalEvalMode.TEXT,
        **kwargs: Any,
    ) -> RetrievalEvalResult:
        """
        Run evaluation results with query string and expected ids.

        Args:
            query (str): Query string
            expected_ids (List[str]): Expected ids

        Returns:
            RetrievalEvalResult: Evaluation result

        """
        return asyncio_run(
            self.aevaluate(
                query=query,
                expected_ids=expected_ids,
                expected_texts=expected_texts,
                mode=mode,
                **kwargs,
            )
        )

    # @abstractmethod
    async def aevaluate(
        self,
        query: str,
        expected_ids: List[str],
        expected_texts: Optional[List[str]] = None,
        mode: RetrievalEvalMode = RetrievalEvalMode.TEXT,
        **kwargs: Any,
    ) -> RetrievalEvalResult:
        """
        Run evaluation with query string, retrieved contexts,
        and generated response string.

        Subclasses can override this method to provide custom evaluation logic and
        take in additional arguments.
        """
        retrieved_ids, retrieved_texts = await self._aget_retrieved_ids_and_texts(
            query, mode
        )
        metric_dict = {}
        for metric in self.metrics:
            eval_result = metric.compute(
                query, expected_ids, retrieved_ids, expected_texts, retrieved_texts
            )
            metric_dict[metric.metric_name] = eval_result

        return RetrievalEvalResult(
            query=query,
            expected_ids=expected_ids,
            expected_texts=expected_texts,
            retrieved_ids=retrieved_ids,
            retrieved_texts=retrieved_texts,
            mode=mode,
            metric_dict=metric_dict,
        )

    async def aevaluate_dataset(
        self,
        dataset: EmbeddingQAFinetuneDataset,
        workers: int = 2,
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[RetrievalEvalResult]:
        """Run evaluation with dataset."""
        semaphore = asyncio.Semaphore(workers)

        async def eval_worker(
            query: str, expected_ids: List[str], mode: RetrievalEvalMode
        ) -> RetrievalEvalResult:
            async with semaphore:
                return await self.aevaluate(query, expected_ids=expected_ids, mode=mode)

        response_jobs = []
        mode = RetrievalEvalMode.from_str(dataset.mode)
        for query_id, query in dataset.queries.items():
            expected_ids = dataset.relevant_docs[query_id]
            response_jobs.append(eval_worker(query, expected_ids, mode))
        if show_progress:
            from tqdm.asyncio import tqdm_asyncio

            eval_results = await tqdm_asyncio.gather(*response_jobs)
        else:
            eval_results = await asyncio.gather(*response_jobs)

        return eval_results

```
  
---|---  
###  from_metric_names `classmethod` #
```
from_metric_names(metric_names: List[str], **kwargs: Any) -> BaseRetrievalEvaluator

```

Create evaluator from metric names.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`metric_names` |  `List[str]` |  List of metric names |  _required_  
`**kwargs` |  `Any` |  Additional arguments for the evaluator |  `{}`  
Source code in `llama-index-core/llama_index/core/evaluation/retrieval/base.py`

| ```
@classmethod
def from_metric_names(
    cls, metric_names: List[str], **kwargs: Any
) -> "BaseRetrievalEvaluator":
    """
    Create evaluator from metric names.

    Args:
        metric_names (List[str]): List of metric names
        **kwargs: Additional arguments for the evaluator

    """
    metric_types = resolve_metrics(metric_names)
    return cls(metrics=[metric() for metric in metric_types], **kwargs)

```
  
---|---  
###  evaluate #
```
evaluate(query: str, expected_ids: List[str], expected_texts: Optional[List[str]] = None, mode: RetrievalEvalMode = TEXT, **kwargs: Any) -> RetrievalEvalResult

```

Run evaluation results with query string and expected ids.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query string |  _required_  
`expected_ids` |  `List[str]` |  Expected ids |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`RetrievalEvalResult` |  `RetrievalEvalResult` |  Evaluation result  
Source code in `llama-index-core/llama_index/core/evaluation/retrieval/base.py`

| ```
def evaluate(
    self,
    query: str,
    expected_ids: List[str],
    expected_texts: Optional[List[str]] = None,
    mode: RetrievalEvalMode = RetrievalEvalMode.TEXT,
    **kwargs: Any,
) -> RetrievalEvalResult:
    """
    Run evaluation results with query string and expected ids.

    Args:
        query (str): Query string
        expected_ids (List[str]): Expected ids

    Returns:
        RetrievalEvalResult: Evaluation result

    """
    return asyncio_run(
        self.aevaluate(
            query=query,
            expected_ids=expected_ids,
            expected_texts=expected_texts,
            mode=mode,
            **kwargs,
        )
    )

```
  
---|---  
###  aevaluate `async` #
```
aevaluate(query: str, expected_ids: List[str], expected_texts: Optional[List[str]] = None, mode: RetrievalEvalMode = TEXT, **kwargs: Any) -> RetrievalEvalResult

```

Run evaluation with query string, retrieved contexts, and generated response string.
Subclasses can override this method to provide custom evaluation logic and take in additional arguments.
Source code in `llama-index-core/llama_index/core/evaluation/retrieval/base.py`

| ```
async def aevaluate(
    self,
    query: str,
    expected_ids: List[str],
    expected_texts: Optional[List[str]] = None,
    mode: RetrievalEvalMode = RetrievalEvalMode.TEXT,
    **kwargs: Any,
) -> RetrievalEvalResult:
    """
    Run evaluation with query string, retrieved contexts,
    and generated response string.

    Subclasses can override this method to provide custom evaluation logic and
    take in additional arguments.
    """
    retrieved_ids, retrieved_texts = await self._aget_retrieved_ids_and_texts(
        query, mode
    )
    metric_dict = {}
    for metric in self.metrics:
        eval_result = metric.compute(
            query, expected_ids, retrieved_ids, expected_texts, retrieved_texts
        )
        metric_dict[metric.metric_name] = eval_result

    return RetrievalEvalResult(
        query=query,
        expected_ids=expected_ids,
        expected_texts=expected_texts,
        retrieved_ids=retrieved_ids,
        retrieved_texts=retrieved_texts,
        mode=mode,
        metric_dict=metric_dict,
    )

```
  
---|---  
###  aevaluate_dataset `async` #
```
aevaluate_dataset(dataset: EmbeddingQAFinetuneDataset, workers: int = 2, show_progress: bool = False, **kwargs: Any) -> List[RetrievalEvalResult]

```

Run evaluation with dataset.
Source code in `llama-index-core/llama_index/core/evaluation/retrieval/base.py`

| ```
async def aevaluate_dataset(
    self,
    dataset: EmbeddingQAFinetuneDataset,
    workers: int = 2,
    show_progress: bool = False,
    **kwargs: Any,
) -> List[RetrievalEvalResult]:
    """Run evaluation with dataset."""
    semaphore = asyncio.Semaphore(workers)

    async def eval_worker(
        query: str, expected_ids: List[str], mode: RetrievalEvalMode
    ) -> RetrievalEvalResult:
        async with semaphore:
            return await self.aevaluate(query, expected_ids=expected_ids, mode=mode)

    response_jobs = []
    mode = RetrievalEvalMode.from_str(dataset.mode)
    for query_id, query in dataset.queries.items():
        expected_ids = dataset.relevant_docs[query_id]
        response_jobs.append(eval_worker(query, expected_ids, mode))
    if show_progress:
        from tqdm.asyncio import tqdm_asyncio

        eval_results = await tqdm_asyncio.gather(*response_jobs)
    else:
        eval_results = await asyncio.gather(*response_jobs)

    return eval_results

```
  
---|---  
##  RetrieverEvaluator #
Bases: `BaseRetrievalEvaluator`
Retriever evaluator.
This module will evaluate a retriever using a set of metrics.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`metrics` |  `List[BaseRetrievalMetric]` |  Sequence of metrics to evaluate |  _required_  
`retriever` |  `BaseRetriever` |  Retriever to evaluate. |  _required_  
`node_postprocessors` |  `Optional[List[BaseNodePostprocessor]]` |  Post-processor to apply after retrieval. |  `None`  
Source code in `llama-index-core/llama_index/core/evaluation/retrieval/evaluator.py`

| ```
class RetrieverEvaluator(BaseRetrievalEvaluator):
    """
    Retriever evaluator.

    This module will evaluate a retriever using a set of metrics.

    Args:
        metrics (List[BaseRetrievalMetric]): Sequence of metrics to evaluate
        retriever: Retriever to evaluate.
        node_postprocessors (Optional[List[BaseNodePostprocessor]]): Post-processor to apply after retrieval.


    """

    retriever: BaseRetriever = Field(..., description="Retriever to evaluate")
    node_postprocessors: Optional[List[SerializeAsAny[BaseNodePostprocessor]]] = Field(
        default=None, description="Optional post-processor"
    )

    async def _aget_retrieved_ids_and_texts(
        self, query: str, mode: RetrievalEvalMode = RetrievalEvalMode.TEXT
    ) -> Tuple[List[str], List[str]]:
        """Get retrieved ids and texts, potentially applying a post-processor."""
        retrieved_nodes = await self.retriever.aretrieve(query)

        if self.node_postprocessors:
            for node_postprocessor in self.node_postprocessors:
                retrieved_nodes = node_postprocessor.postprocess_nodes(
                    retrieved_nodes, query_str=query
                )

        return (
            [node.node.node_id for node in retrieved_nodes],
            [node.text for node in retrieved_nodes],
        )

```
  
---|---  
##  RetrievalEvalResult #
Bases: `BaseModel`
Retrieval eval result.
NOTE: this abstraction might change in the future.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  Query string |  _required_  
`expected_ids` |  `List[str]` |  Expected ids |  _required_  
`expected_texts` |  `List[str] | None` |  Expected texts associated with nodes provided in `expected_ids` |  `None`  
`retrieved_ids` |  `List[str]` |  Retrieved ids |  _required_  
`retrieved_texts` |  `List[str]` |  Retrieved texts |  _required_  
`mode` |  `RetrievalEvalMode` |  text or image |  `<RetrievalEvalMode.TEXT: 'text'>`  
`metric_dict` |  `Dict[str, RetrievalMetricResult]` |  Metric dictionary for the evaluation |  _required_  
Attributes:
Name | Type | Description  
---|---|---  
`query` |  `str` |  Query string  
`expected_ids` |  `List[str]` |  Expected ids  
`retrieved_ids` |  `List[str]` |  Retrieved ids  
`metric_dict` |  `Dict[str, BaseRetrievalMetric]` |  Metric dictionary for the evaluation  
Source code in `llama-index-core/llama_index/core/evaluation/retrieval/base.py`

| ```
class RetrievalEvalResult(BaseModel):
    """
    Retrieval eval result.

    NOTE: this abstraction might change in the future.

    Attributes:
        query (str): Query string
        expected_ids (List[str]): Expected ids
        retrieved_ids (List[str]): Retrieved ids
        metric_dict (Dict[str, BaseRetrievalMetric]): \
            Metric dictionary for the evaluation

    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    query: str = Field(..., description="Query string")
    expected_ids: List[str] = Field(..., description="Expected ids")
    expected_texts: Optional[List[str]] = Field(
        default=None,
        description="Expected texts associated with nodes provided in `expected_ids`",
    )
    retrieved_ids: List[str] = Field(..., description="Retrieved ids")
    retrieved_texts: List[str] = Field(..., description="Retrieved texts")
    mode: "RetrievalEvalMode" = Field(
        default=RetrievalEvalMode.TEXT, description="text or image"
    )
    metric_dict: Dict[str, RetrievalMetricResult] = Field(
        ..., description="Metric dictionary for the evaluation"
    )

    @property
    def metric_vals_dict(self) -> Dict[str, float]:
        """Dictionary of metric values."""
        return {k: v.score for k, v in self.metric_dict.items()}

    def __str__(self) -> str:
        """String representation."""
        return f"Query: {self.query}\nMetrics: {self.metric_vals_dict!s}\n"

```
  
---|---  
###  metric_vals_dict `property` #
```
metric_vals_dict: Dict[str, float]

```

Dictionary of metric values.
