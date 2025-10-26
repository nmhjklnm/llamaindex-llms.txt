# Index
Dataset Module.
##  BaseLlamaDataExample #
Bases: `BaseModel`
Base llama dataset example class.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
class BaseLlamaDataExample(BaseModel):
    """Base llama dataset example class."""

    @property
    @abstractmethod
    def class_name(self) -> str:
        """Class name."""
        return "BaseLlamaDataExample"

```
  
---|---  
###  class_name `abstractmethod` `property` #
```
class_name: str

```

Class name.
##  BaseLlamaDataset #
Bases: `BaseModel`, `Generic[P]`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`examples` |  `List[BaseLlamaDataExample]` |  Data examples of this dataset. |  `[]`  
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
class BaseLlamaDataset(BaseModel, Generic[P]):
    _example_type: ClassVar[Type[BaseLlamaDataExample]]
    examples: List[BaseLlamaDataExample] = Field(
        default=[], description="Data examples of this dataset."
    )
    _predictions_cache: List[BaseLlamaExamplePrediction] = PrivateAttr(
        default_factory=list
    )

    def __getitem__(
        self, val: Union[slice, int]
    ) -> Union[Sequence[BaseLlamaDataExample], BaseLlamaDataExample]:
        """
        Enable slicing and indexing.

        Returns the desired slice on `examples`.
        """
        return self.examples[val]

    @abstractmethod
    def to_pandas(self) -> Any:
        """Create pandas dataframe."""

    def save_json(self, path: str) -> None:
        """Save json."""
        with open(path, "w") as f:
            examples = [self._example_type.model_dump(el) for el in self.examples]
            data = {
                "examples": examples,
            }

            json.dump(data, f, indent=4)

    @classmethod
    def from_json(cls, path: str) -> "BaseLlamaDataset":
        """Load json."""
        with open(path) as f:
            data = json.load(f)

        examples = [cls._example_type.model_validate(el) for el in data["examples"]]

        return cls(
            examples=examples,
        )

    @abstractmethod
    def _construct_prediction_dataset(
        self, predictions: Sequence[BaseLlamaExamplePrediction]
    ) -> BaseLlamaPredictionDataset:
        """
        Construct the specific prediction dataset.

        Args:
            predictions (List[BaseLlamaExamplePrediction]): the list of predictions.

        Returns:
            BaseLlamaPredictionDataset: A dataset of predictions.

        """

    @abstractmethod
    def _predict_example(
        self,
        predictor: P,
        example: BaseLlamaDataExample,
        sleep_time_in_seconds: int = 0,
    ) -> BaseLlamaExamplePrediction:
        """
        Predict on a single example.

        NOTE: Subclasses need to implement this.

        Args:
            predictor (PredictorType): The predictor to make the prediction with.
            example (BaseLlamaDataExample): The example to predict on.

        Returns:
            BaseLlamaExamplePrediction: The prediction.

        """

    def make_predictions_with(
        self,
        predictor: P,
        show_progress: bool = False,
        batch_size: int = 20,
        sleep_time_in_seconds: int = 0,
    ) -> BaseLlamaPredictionDataset:
        """
        Predict with a given query engine.

        Args:
            predictor (PredictorType): The predictor to make predictions with.
            show_progress (bool, optional): Show progress of making predictions.
            batch_size (int): Used to batch async calls, especially to reduce chances
                            of hitting RateLimitError from openai.
            sleep_time_in_seconds (int): Amount of time to sleep between batch call
                            to reduce chance of hitting RateLimitError from openai.

        Returns:
            BaseLlamaPredictionDataset: A dataset of predictions.

        """
        if self._predictions_cache:
            start_example_position = len(self._predictions_cache)
        else:
            start_example_position = 0

        for batch in self._batch_examples(
            batch_size=batch_size, start_position=start_example_position
        ):
            if show_progress:
                example_iterator = tqdm.tqdm(batch)
            else:
                example_iterator = batch
            for example in example_iterator:
                self._predictions_cache.append(
                    self._predict_example(predictor, example, sleep_time_in_seconds)
                )

        return self._construct_prediction_dataset(predictions=self._predictions_cache)

    # async methods
    @abstractmethod
    async def _apredict_example(
        self,
        predictor: P,
        example: BaseLlamaDataExample,
        sleep_time_in_seconds: int,
    ) -> BaseLlamaExamplePrediction:
        """
        Async predict on a single example.

        NOTE: Subclasses need to implement this.

        Args:
            predictor (PredictorType): The predictor to make the prediction with.
            example (BaseLlamaDataExample): The example to predict on.

        Returns:
            BaseLlamaExamplePrediction: The prediction.

        """

    def _batch_examples(
        self,
        batch_size: int = 20,
        start_position: int = 0,
    ) -> Generator[Sequence[BaseLlamaDataExample], None, None]:
        """Batches examples and predictions with a given batch_size."""
        num_examples = len(self.examples)
        for ndx in range(start_position, num_examples, batch_size):
            yield self.examples[ndx : min(ndx + batch_size, num_examples)]

    async def amake_predictions_with(
        self,
        predictor: P,
        show_progress: bool = False,
        batch_size: int = 20,
        sleep_time_in_seconds: int = 1,
    ) -> BaseLlamaPredictionDataset:
        """
        Async predict with a given query engine.

        Args:
            predictor (PredictorType): The predictor to make predictions with.
            show_progress (bool, optional): Show progress of making predictions.
            batch_size (int): Used to batch async calls, especially to reduce chances
                            of hitting RateLimitError from openai.
            sleep_time_in_seconds (int): Amount of time to sleep between batch call
                            to reduce chance of hitting RateLimitError from openai.

        Returns:
            BaseLlamaPredictionDataset: A dataset of predictions.

        """
        if self._predictions_cache:
            start_example_position = len(self._predictions_cache)
        else:
            start_example_position = 0

        for batch in self._batch_examples(
            batch_size=batch_size, start_position=start_example_position
        ):
            tasks = []
            for example in batch:
                tasks.append(
                    self._apredict_example(predictor, example, sleep_time_in_seconds)
                )
            asyncio_mod = asyncio_module(show_progress=show_progress)

            try:
                if show_progress:
                    batch_predictions = await asyncio_mod.gather(
                        *tasks, desc="Batch processing of predictions"
                    )
                else:
                    batch_predictions = await asyncio_mod.gather(*tasks)
            except Exception as err:
                if show_progress:
                    asyncio_mod.close()

                if "RateLimitError" in str(err):
                    raise ValueError(
                        "You've hit rate limits on your OpenAI subscription. This"
                        " class caches previous predictions after each successful"
                        " batch execution. Based off this cache, when executing this"
                        " command again it will attempt to predict on only the examples "
                        "that have not yet been predicted. Try reducing your batch_size."
                    ) from err
                else:
                    raise err  # noqa: TRY201

            self._predictions_cache += batch_predictions
            # time.sleep(sleep_time_in_seconds)

        prediction_dataset = self._construct_prediction_dataset(
            predictions=self._predictions_cache
        )
        self._predictions_cache = []  # clear cache
        return prediction_dataset

    @property
    @abstractmethod
    def class_name(self) -> str:
        """Class name."""
        return "BaseLlamaDataset"

```
  
---|---  
###  class_name `abstractmethod` `property` #
```
class_name: str

```

Class name.
###  to_pandas `abstractmethod` #
```
to_pandas() -> Any

```

Create pandas dataframe.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
@abstractmethod
def to_pandas(self) -> Any:
    """Create pandas dataframe."""

```
  
---|---  
###  save_json #
```
save_json(path: str) -> None

```

Save json.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
def save_json(self, path: str) -> None:
    """Save json."""
    with open(path, "w") as f:
        examples = [self._example_type.model_dump(el) for el in self.examples]
        data = {
            "examples": examples,
        }

        json.dump(data, f, indent=4)

```
  
---|---  
###  from_json `classmethod` #
```
from_json(path: str) -> BaseLlamaDataset

```

Load json.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
@classmethod
def from_json(cls, path: str) -> "BaseLlamaDataset":
    """Load json."""
    with open(path) as f:
        data = json.load(f)

    examples = [cls._example_type.model_validate(el) for el in data["examples"]]

    return cls(
        examples=examples,
    )

```
  
---|---  
###  make_predictions_with #
```
make_predictions_with(predictor: P, show_progress: bool = False, batch_size: int = 20, sleep_time_in_seconds: int = 0) -> BaseLlamaPredictionDataset

```

Predict with a given query engine.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`predictor` |  `PredictorType` |  The predictor to make predictions with. |  _required_  
`show_progress` |  `bool` |  Show progress of making predictions. |  `False`  
`batch_size` |  `int` |  Used to batch async calls, especially to reduce chances of hitting RateLimitError from openai. |  `20`  
`sleep_time_in_seconds` |  `int` |  Amount of time to sleep between batch call to reduce chance of hitting RateLimitError from openai. |  `0`  
Returns:
Name | Type | Description  
---|---|---  
`BaseLlamaPredictionDataset` |  `BaseLlamaPredictionDataset` |  A dataset of predictions.  
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
def make_predictions_with(
    self,
    predictor: P,
    show_progress: bool = False,
    batch_size: int = 20,
    sleep_time_in_seconds: int = 0,
) -> BaseLlamaPredictionDataset:
    """
    Predict with a given query engine.

    Args:
        predictor (PredictorType): The predictor to make predictions with.
        show_progress (bool, optional): Show progress of making predictions.
        batch_size (int): Used to batch async calls, especially to reduce chances
                        of hitting RateLimitError from openai.
        sleep_time_in_seconds (int): Amount of time to sleep between batch call
                        to reduce chance of hitting RateLimitError from openai.

    Returns:
        BaseLlamaPredictionDataset: A dataset of predictions.

    """
    if self._predictions_cache:
        start_example_position = len(self._predictions_cache)
    else:
        start_example_position = 0

    for batch in self._batch_examples(
        batch_size=batch_size, start_position=start_example_position
    ):
        if show_progress:
            example_iterator = tqdm.tqdm(batch)
        else:
            example_iterator = batch
        for example in example_iterator:
            self._predictions_cache.append(
                self._predict_example(predictor, example, sleep_time_in_seconds)
            )

    return self._construct_prediction_dataset(predictions=self._predictions_cache)

```
  
---|---  
###  amake_predictions_with `async` #
```
amake_predictions_with(predictor: P, show_progress: bool = False, batch_size: int = 20, sleep_time_in_seconds: int = 1) -> BaseLlamaPredictionDataset

```

Async predict with a given query engine.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`predictor` |  `PredictorType` |  The predictor to make predictions with. |  _required_  
`show_progress` |  `bool` |  Show progress of making predictions. |  `False`  
`batch_size` |  `int` |  Used to batch async calls, especially to reduce chances of hitting RateLimitError from openai. |  `20`  
`sleep_time_in_seconds` |  `int` |  Amount of time to sleep between batch call to reduce chance of hitting RateLimitError from openai. |  `1`  
Returns:
Name | Type | Description  
---|---|---  
`BaseLlamaPredictionDataset` |  `BaseLlamaPredictionDataset` |  A dataset of predictions.  
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
async def amake_predictions_with(
    self,
    predictor: P,
    show_progress: bool = False,
    batch_size: int = 20,
    sleep_time_in_seconds: int = 1,
) -> BaseLlamaPredictionDataset:
    """
    Async predict with a given query engine.

    Args:
        predictor (PredictorType): The predictor to make predictions with.
        show_progress (bool, optional): Show progress of making predictions.
        batch_size (int): Used to batch async calls, especially to reduce chances
                        of hitting RateLimitError from openai.
        sleep_time_in_seconds (int): Amount of time to sleep between batch call
                        to reduce chance of hitting RateLimitError from openai.

    Returns:
        BaseLlamaPredictionDataset: A dataset of predictions.

    """
    if self._predictions_cache:
        start_example_position = len(self._predictions_cache)
    else:
        start_example_position = 0

    for batch in self._batch_examples(
        batch_size=batch_size, start_position=start_example_position
    ):
        tasks = []
        for example in batch:
            tasks.append(
                self._apredict_example(predictor, example, sleep_time_in_seconds)
            )
        asyncio_mod = asyncio_module(show_progress=show_progress)

        try:
            if show_progress:
                batch_predictions = await asyncio_mod.gather(
                    *tasks, desc="Batch processing of predictions"
                )
            else:
                batch_predictions = await asyncio_mod.gather(*tasks)
        except Exception as err:
            if show_progress:
                asyncio_mod.close()

            if "RateLimitError" in str(err):
                raise ValueError(
                    "You've hit rate limits on your OpenAI subscription. This"
                    " class caches previous predictions after each successful"
                    " batch execution. Based off this cache, when executing this"
                    " command again it will attempt to predict on only the examples "
                    "that have not yet been predicted. Try reducing your batch_size."
                ) from err
            else:
                raise err  # noqa: TRY201

        self._predictions_cache += batch_predictions
        # time.sleep(sleep_time_in_seconds)

    prediction_dataset = self._construct_prediction_dataset(
        predictions=self._predictions_cache
    )
    self._predictions_cache = []  # clear cache
    return prediction_dataset

```
  
---|---  
##  BaseLlamaExamplePrediction #
Bases: `BaseModel`
Base llama dataset example class.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
class BaseLlamaExamplePrediction(BaseModel):
    """Base llama dataset example class."""

    @property
    @abstractmethod
    def class_name(self) -> str:
        """Class name."""
        return "BaseLlamaPrediction"

```
  
---|---  
###  class_name `abstractmethod` `property` #
```
class_name: str

```

Class name.
##  BaseLlamaPredictionDataset #
Bases: `BaseModel`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`predictions` |  `List[BaseLlamaExamplePrediction]` |  Predictions on train_examples. |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
class BaseLlamaPredictionDataset(BaseModel):
    _prediction_type: ClassVar[Type[BaseLlamaExamplePrediction]]
    predictions: List[BaseLlamaExamplePrediction] = Field(
        default_factory=list, description="Predictions on train_examples."
    )

    def __getitem__(
        self, val: Union[slice, int]
    ) -> Union[Sequence[BaseLlamaExamplePrediction], BaseLlamaExamplePrediction]:
        """
        Enable slicing and indexing.

        Returns the desired slice on `predictions`.
        """
        return self.predictions[val]

    @abstractmethod
    def to_pandas(self) -> Any:
        """Create pandas dataframe."""

    def save_json(self, path: str) -> None:
        """Save json."""
        with open(path, "w") as f:
            predictions = None
            if self.predictions:
                predictions = [
                    self._prediction_type.model_dump(el) for el in self.predictions
                ]
            data = {
                "predictions": predictions,
            }

            json.dump(data, f, indent=4)

    @classmethod
    def from_json(cls, path: str) -> "BaseLlamaPredictionDataset":
        """Load json."""
        with open(path) as f:
            data = json.load(f)

        predictions = [
            cls._prediction_type.model_validate(el) for el in data["predictions"]
        ]

        return cls(
            predictions=predictions,
        )

    @property
    @abstractmethod
    def class_name(self) -> str:
        """Class name."""
        return "BaseLlamaPredictionDataset"

```
  
---|---  
###  class_name `abstractmethod` `property` #
```
class_name: str

```

Class name.
###  to_pandas `abstractmethod` #
```
to_pandas() -> Any

```

Create pandas dataframe.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
@abstractmethod
def to_pandas(self) -> Any:
    """Create pandas dataframe."""

```
  
---|---  
###  save_json #
```
save_json(path: str) -> None

```

Save json.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
def save_json(self, path: str) -> None:
    """Save json."""
    with open(path, "w") as f:
        predictions = None
        if self.predictions:
            predictions = [
                self._prediction_type.model_dump(el) for el in self.predictions
            ]
        data = {
            "predictions": predictions,
        }

        json.dump(data, f, indent=4)

```
  
---|---  
###  from_json `classmethod` #
```
from_json(path: str) -> BaseLlamaPredictionDataset

```

Load json.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
@classmethod
def from_json(cls, path: str) -> "BaseLlamaPredictionDataset":
    """Load json."""
    with open(path) as f:
        data = json.load(f)

    predictions = [
        cls._prediction_type.model_validate(el) for el in data["predictions"]
    ]

    return cls(
        predictions=predictions,
    )

```
  
---|---  
##  CreatedBy #
Bases: `BaseModel`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`type` |  `CreatedByType` |  |  _required_  
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
class CreatedBy(BaseModel):
    model_config = ConfigDict(protected_namespaces=("pydantic_model_",))
    model_name: Optional[str] = Field(
        default_factory=str, description="When CreatedByType.AI, specify model name."
    )
    type: CreatedByType

    def __str__(self) -> str:
        if self.type == "ai":
            return f"{self.type!s} ({self.model_name})"
        else:
            return str(self.type)

```
  
---|---  
##  CreatedByType #
Bases: `str`, `Enum`
The kinds of rag data examples.
Source code in `llama-index-core/llama_index/core/llama_dataset/base.py`

| ```
class CreatedByType(str, Enum):
    """The kinds of rag data examples."""

    HUMAN = "human"
    AI = "ai"

    def __str__(self) -> str:
        return self.value

```
  
---|---  
##  EvaluatorExamplePrediction #
Bases: `BaseLlamaExamplePrediction`
Evaluation example prediction class.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`feedback` |  `Optional[str]` |  The evaluator's feedback. |  _required_  
`score` |  `Optional[float]` |  The evaluator's score. |  `None`  
`invalid_prediction` |  `bool` |  Whether or not the prediction is a valid one. |  `False`  
`invalid_reason` |  `str | None` |  Reason as to why prediction is invalid. |  `None`  
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
class EvaluatorExamplePrediction(BaseLlamaExamplePrediction):
    """
    Evaluation example prediction class.

    Args:
        feedback (Optional[str]): The evaluator's feedback.
        score (Optional[float]): The evaluator's score.

    """

    feedback: str = Field(
        default_factory=str,
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    score: Optional[float] = Field(
        default=None,
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    invalid_prediction: bool = Field(
        default=False, description="Whether or not the prediction is a valid one."
    )
    invalid_reason: Optional[str] = Field(
        default=None, description="Reason as to why prediction is invalid."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "EvaluatorExamplePrediction"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Data example class name.
##  EvaluatorPredictionDataset #
Bases: `BaseLlamaPredictionDataset`
Evaluation Prediction Dataset Class.
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
class EvaluatorPredictionDataset(BaseLlamaPredictionDataset):
    """Evaluation Prediction Dataset Class."""

    _prediction_type = EvaluatorExamplePrediction

    def to_pandas(self) -> Any:
        """Create pandas dataframe."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this function. Please install it with `pip install pandas`."
            )

        data: Dict[str, List] = {
            "feedback": [],
            "score": [],
        }
        for pred in self.predictions:
            if not isinstance(pred, EvaluatorExamplePrediction):
                raise ValueError(
                    "EvaluatorPredictionDataset can only contain EvaluatorExamplePrediction instances."
                )
            data["feedback"].append(pred.feedback)
            data["score"].append(pred.score)

        return pd.DataFrame(data)

    @property
    def class_name(self) -> str:
        """Class name."""
        return "EvaluatorPredictionDataset"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Class name.
###  to_pandas #
```
to_pandas() -> Any

```

Create pandas dataframe.
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
def to_pandas(self) -> Any:
    """Create pandas dataframe."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for this function. Please install it with `pip install pandas`."
        )

    data: Dict[str, List] = {
        "feedback": [],
        "score": [],
    }
    for pred in self.predictions:
        if not isinstance(pred, EvaluatorExamplePrediction):
            raise ValueError(
                "EvaluatorPredictionDataset can only contain EvaluatorExamplePrediction instances."
            )
        data["feedback"].append(pred.feedback)
        data["score"].append(pred.score)

    return pd.DataFrame(data)

```
  
---|---  
##  LabelledEvaluatorDataExample #
Bases: `BaseLlamaDataExample`
Evaluation example class.
This data class contains the ingredients to perform a new "prediction" i.e., evaluation. Here an evaluator is meant to evaluate a response against an associated query as well as optionally contexts.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The user query |  _required_  
`query_by` |  `CreatedBy` |  Query generated by human or ai (model-name) |  `None`  
`contexts` |  `Optional[List[str]]` |  The contexts used for response |  `None`  
`answer` |  `str` |  Answer to the query that is to be evaluated. |  _required_  
`answer_by` |  `CreatedBy | None` |  The reference answer generated by human or ai (model-name). |  `None`  
`ground_truth_answer` |  `Optional[str]` |  |  `None`  
`ground_truth_answer_by` |  `Optional[CreatedBy]` |  |  `None`  
`reference_feedback` |  `str` |  The reference feedback evaluation. |  `None`  
`reference_score` |  `float` |  The reference score evaluation. |  `<dynamic>`  
`reference_evaluation_by` |  `CreatedBy` |  Evaluation generated by human or ai (model-name) |  `None`  
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
class LabelledEvaluatorDataExample(BaseLlamaDataExample):
    """
    Evaluation example class.

    This data class contains the ingredients to perform a new "prediction" i.e.,
    evaluation. Here an evaluator is meant to evaluate a response against an
    associated query as well as optionally contexts.

    Args:
        query (str): The user query
        query_by (CreatedBy): Query generated by human or ai (model-name)
        contexts (Optional[List[str]]): The contexts used for response
        answer (str): Answer to the query that is to be evaluated.
        answer_by: The reference answer generated by human or ai (model-name).
        ground_truth_answer (Optional[str]):
        ground_truth_answer_by (Optional[CreatedBy]):
        reference_feedback (str): The reference feedback evaluation.
        reference_score (float): The reference score evaluation.
        reference_evaluation_by (CreatedBy): Evaluation generated by human or ai (model-name)

    """

    query: str = Field(
        default_factory=str, description="The user query for the example."
    )
    query_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the query."
    )
    contexts: Optional[List[str]] = Field(
        default=None,
        description="The contexts used to generate the answer.",
    )
    answer: str = Field(
        default_factory=str,
        description="The provided answer to the example that is to be evaluated.",
    )
    answer_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the answer."
    )
    ground_truth_answer: Optional[str] = Field(
        default=None,
        description="The ground truth answer to the example that is used to evaluate the provided `answer`.",
    )
    ground_truth_answer_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the ground-truth answer."
    )
    reference_feedback: Optional[str] = Field(
        default=None,
        description="The reference feedback (ground-truth).",
    )
    reference_score: float = Field(
        default_factory=float, description="The reference score (ground-truth)."
    )
    reference_evaluation_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the evaluation (feedback and score)."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "LabelledEvaluatorDataExample"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Data example class name.
##  LabelledEvaluatorDataset #
Bases: `BaseLlamaDataset[BaseEvaluator]`
LabelledEvalationDataset class.
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
class LabelledEvaluatorDataset(BaseLlamaDataset[BaseEvaluator]):
    """LabelledEvalationDataset class."""

    _example_type = LabelledEvaluatorDataExample

    def to_pandas(self) -> Any:
        """Create pandas dataframe."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this function. Please install it with `pip install pandas`."
            )

        data: Dict[str, List] = {
            "query": [],
            "answer": [],
            "contexts": [],
            "ground_truth_answer": [],
            "query_by": [],
            "answer_by": [],
            "ground_truth_answer_by": [],
            "reference_feedback": [],
            "reference_score": [],
            "reference_evaluation_by": [],
        }

        for example in self.examples:
            if not isinstance(example, LabelledEvaluatorDataExample):
                raise ValueError(
                    "LabelledEvaluatorDataset can only contain LabelledEvaluatorDataExample instances."
                )
            data["query"].append(example.query)
            data["answer"].append(example.answer)
            data["contexts"].append(example.contexts)
            data["ground_truth_answer"].append(example.ground_truth_answer)
            data["query_by"].append(str(example.query_by))
            data["answer_by"].append(str(example.answer_by))
            data["ground_truth_answer_by"].append(str(example.ground_truth_answer_by))
            data["reference_feedback"].append(example.reference_feedback)
            data["reference_score"].append(example.reference_score)
            data["reference_evaluation_by"].append(str(example.reference_evaluation_by))

        return pd.DataFrame(data)

    async def _apredict_example(  # type: ignore
        self,
        predictor: BaseEvaluator,
        example: LabelledEvaluatorDataExample,
        sleep_time_in_seconds: int,
    ) -> EvaluatorExamplePrediction:
        """Async predict RAG example with a query engine."""
        await asyncio.sleep(sleep_time_in_seconds)
        try:
            eval_result: EvaluationResult = await predictor.aevaluate(
                query=example.query,
                response=example.answer,
                contexts=example.contexts,
                reference=example.ground_truth_answer,
                sleep_time_in_seconds=sleep_time_in_seconds,
            )
        except Exception as err:
            # TODO: raise warning here as well
            return EvaluatorExamplePrediction(
                invalid_prediction=True, invalid_reason=f"Caught error {err!s}"
            )

        if not eval_result.invalid_result:
            return EvaluatorExamplePrediction(
                feedback=eval_result.feedback or "", score=eval_result.score
            )
        else:
            return EvaluatorExamplePrediction(
                invalid_prediction=True, invalid_reason=eval_result.invalid_reason
            )

    def _predict_example(  # type: ignore
        self,
        predictor: BaseEvaluator,
        example: LabelledEvaluatorDataExample,
        sleep_time_in_seconds: int = 0,
    ) -> EvaluatorExamplePrediction:
        """Predict RAG example with a query engine."""
        time.sleep(sleep_time_in_seconds)
        try:
            eval_result: EvaluationResult = predictor.evaluate(
                query=example.query,
                response=example.answer,
                contexts=example.contexts,
                reference=example.ground_truth_answer,
                sleep_time_in_seconds=sleep_time_in_seconds,
            )
        except Exception as err:
            # TODO: raise warning here as well
            return EvaluatorExamplePrediction(
                invalid_prediction=True, invalid_reason=f"Caught error {err!s}"
            )

        if not eval_result.invalid_result:
            return EvaluatorExamplePrediction(
                feedback=eval_result.feedback or "", score=eval_result.score
            )
        else:
            return EvaluatorExamplePrediction(
                invalid_prediction=True, invalid_reason=eval_result.invalid_reason
            )

    def _construct_prediction_dataset(  # type: ignore
        self, predictions: Sequence[EvaluatorExamplePrediction]
    ) -> EvaluatorPredictionDataset:
        """Construct prediction dataset."""
        return EvaluatorPredictionDataset(predictions=predictions)

    @property
    def class_name(self) -> str:
        """Class name."""
        return "LabelledEvaluatorDataset"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Class name.
###  to_pandas #
```
to_pandas() -> Any

```

Create pandas dataframe.
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
def to_pandas(self) -> Any:
    """Create pandas dataframe."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for this function. Please install it with `pip install pandas`."
        )

    data: Dict[str, List] = {
        "query": [],
        "answer": [],
        "contexts": [],
        "ground_truth_answer": [],
        "query_by": [],
        "answer_by": [],
        "ground_truth_answer_by": [],
        "reference_feedback": [],
        "reference_score": [],
        "reference_evaluation_by": [],
    }

    for example in self.examples:
        if not isinstance(example, LabelledEvaluatorDataExample):
            raise ValueError(
                "LabelledEvaluatorDataset can only contain LabelledEvaluatorDataExample instances."
            )
        data["query"].append(example.query)
        data["answer"].append(example.answer)
        data["contexts"].append(example.contexts)
        data["ground_truth_answer"].append(example.ground_truth_answer)
        data["query_by"].append(str(example.query_by))
        data["answer_by"].append(str(example.answer_by))
        data["ground_truth_answer_by"].append(str(example.ground_truth_answer_by))
        data["reference_feedback"].append(example.reference_feedback)
        data["reference_score"].append(example.reference_score)
        data["reference_evaluation_by"].append(str(example.reference_evaluation_by))

    return pd.DataFrame(data)

```
  
---|---  
##  LabelledPairwiseEvaluatorDataExample #
Bases: `LabelledEvaluatorDataExample`
Labelled pairwise evaluation data example class.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`second_answer_by` |  `CreatedBy | None` |  What generated the second answer. |  `None`  
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
class LabelledPairwiseEvaluatorDataExample(LabelledEvaluatorDataExample):
    """Labelled pairwise evaluation data example class."""

    second_answer: str = Field(
        default_factory=str,
        description="The second answer to the example that is to be evaluated along versus `answer`.",
    )
    second_answer_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the second answer."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "LabelledPairwiseEvaluatorDataExample"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Data example class name.
##  LabelledPairwiseEvaluatorDataset #
Bases: `BaseLlamaDataset[BaseEvaluator]`
Labelled pairwise evaluation dataset. For evaluating the evaluator in performing pairwise evaluations.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`BaseLlamaDataset` |  `_type_` |  _description_ |  _required_  
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
class LabelledPairwiseEvaluatorDataset(BaseLlamaDataset[BaseEvaluator]):
    """
    Labelled pairwise evaluation dataset. For evaluating the evaluator in
    performing pairwise evaluations.

    Args:
        BaseLlamaDataset (_type_): _description_

    """

    _example_type = LabelledPairwiseEvaluatorDataExample

    def to_pandas(self) -> Any:
        """Create pandas dataframe."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this function. Please install it with `pip install pandas`."
            )

        data: Dict[str, List] = {
            "query": [],
            "answer": [],
            "second_answer": [],
            "contexts": [],
            "ground_truth_answer": [],
            "query_by": [],
            "answer_by": [],
            "second_answer_by": [],
            "ground_truth_answer_by": [],
            "reference_feedback": [],
            "reference_score": [],
            "reference_evaluation_by": [],
        }
        for example in self.examples:
            if not isinstance(example, LabelledPairwiseEvaluatorDataExample):
                raise ValueError(
                    "LabelledPairwiseEvaluatorDataset can only contain LabelledPairwiseEvaluatorDataExample instances."
                )
            data["query"].append(example.query)
            data["answer"].append(example.answer)
            data["second_answer"].append(example.second_answer)
            data["contexts"].append(example.contexts)
            data["ground_truth_answer"].append(example.ground_truth_answer)
            data["query_by"].append(str(example.query_by))
            data["answer_by"].append(str(example.answer_by))
            data["second_answer_by"].append(str(example.second_answer_by))
            data["ground_truth_answer_by"].append(str(example.ground_truth_answer_by))
            data["reference_feedback"].append(example.reference_feedback)
            data["reference_score"].append(example.reference_score)
            data["reference_evaluation_by"].append(str(example.reference_evaluation_by))

        return pd.DataFrame(data)

    async def _apredict_example(  # type: ignore
        self,
        predictor: BaseEvaluator,
        example: LabelledPairwiseEvaluatorDataExample,
        sleep_time_in_seconds: int,
    ) -> PairwiseEvaluatorExamplePrediction:
        """Async predict evaluation example with an Evaluator."""
        await asyncio.sleep(sleep_time_in_seconds)
        try:
            eval_result: EvaluationResult = await predictor.aevaluate(
                query=example.query,
                response=example.answer,
                second_response=example.second_answer,
                contexts=example.contexts,
                reference=example.ground_truth_answer,
                sleep_time_in_seconds=sleep_time_in_seconds,
            )
        except Exception as err:
            # TODO: raise warning here as well
            return PairwiseEvaluatorExamplePrediction(
                invalid_prediction=True, invalid_reason=f"Caught error {err!s}"
            )

        if not eval_result.invalid_result:
            return PairwiseEvaluatorExamplePrediction(
                feedback=eval_result.feedback or "",
                score=eval_result.score,
                evaluation_source=EvaluationSource(eval_result.pairwise_source),
            )
        else:
            return PairwiseEvaluatorExamplePrediction(
                invalid_prediction=True, invalid_reason=eval_result.invalid_reason
            )

    def _predict_example(  # type: ignore
        self,
        predictor: BaseEvaluator,
        example: LabelledPairwiseEvaluatorDataExample,
        sleep_time_in_seconds: int = 0,
    ) -> PairwiseEvaluatorExamplePrediction:
        """Predict RAG example with a query engine."""
        time.sleep(sleep_time_in_seconds)
        try:
            eval_result: EvaluationResult = predictor.evaluate(
                query=example.query,
                response=example.answer,
                second_response=example.second_answer,
                contexts=example.contexts,
                reference=example.ground_truth_answer,
                sleep_time_in_seconds=sleep_time_in_seconds,
            )
        except Exception as err:
            # TODO: raise warning here as well
            return PairwiseEvaluatorExamplePrediction(
                invalid_prediction=True, invalid_reason=f"Caught error {err!s}"
            )

        if not eval_result.invalid_result:
            return PairwiseEvaluatorExamplePrediction(
                feedback=eval_result.feedback or "",
                score=eval_result.score,
                evaluation_source=EvaluationSource(eval_result.pairwise_source),
            )
        else:
            return PairwiseEvaluatorExamplePrediction(
                invalid_prediction=True, invalid_reason=eval_result.invalid_reason
            )

    def _construct_prediction_dataset(  # type: ignore
        self, predictions: Sequence[PairwiseEvaluatorExamplePrediction]
    ) -> PairwiseEvaluatorPredictionDataset:
        """Construct prediction dataset."""
        return PairwiseEvaluatorPredictionDataset(predictions=predictions)

    @property
    def class_name(self) -> str:
        """Class name."""
        return "LabelledPairwiseEvaluatorDataset"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Class name.
###  to_pandas #
```
to_pandas() -> Any

```

Create pandas dataframe.
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
def to_pandas(self) -> Any:
    """Create pandas dataframe."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for this function. Please install it with `pip install pandas`."
        )

    data: Dict[str, List] = {
        "query": [],
        "answer": [],
        "second_answer": [],
        "contexts": [],
        "ground_truth_answer": [],
        "query_by": [],
        "answer_by": [],
        "second_answer_by": [],
        "ground_truth_answer_by": [],
        "reference_feedback": [],
        "reference_score": [],
        "reference_evaluation_by": [],
    }
    for example in self.examples:
        if not isinstance(example, LabelledPairwiseEvaluatorDataExample):
            raise ValueError(
                "LabelledPairwiseEvaluatorDataset can only contain LabelledPairwiseEvaluatorDataExample instances."
            )
        data["query"].append(example.query)
        data["answer"].append(example.answer)
        data["second_answer"].append(example.second_answer)
        data["contexts"].append(example.contexts)
        data["ground_truth_answer"].append(example.ground_truth_answer)
        data["query_by"].append(str(example.query_by))
        data["answer_by"].append(str(example.answer_by))
        data["second_answer_by"].append(str(example.second_answer_by))
        data["ground_truth_answer_by"].append(str(example.ground_truth_answer_by))
        data["reference_feedback"].append(example.reference_feedback)
        data["reference_score"].append(example.reference_score)
        data["reference_evaluation_by"].append(str(example.reference_evaluation_by))

    return pd.DataFrame(data)

```
  
---|---  
##  PairwiseEvaluatorExamplePrediction #
Bases: `BaseLlamaExamplePrediction`
Pairwise evaluation example prediction class.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`feedback` |  `Optional[str]` |  The evaluator's feedback. |  _required_  
`score` |  `Optional[float]` |  The evaluator's score. |  `None`  
`evaluation_source` |  `EvaluationSource` |  If the evaluation came from original order or flipped; or inconclusive. |  `None`  
`invalid_prediction` |  `bool` |  Whether or not the prediction is a valid one. |  `False`  
`invalid_reason` |  `str | None` |  Reason as to why prediction is invalid. |  `None`  
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
class PairwiseEvaluatorExamplePrediction(BaseLlamaExamplePrediction):
    """
    Pairwise evaluation example prediction class.

    Args:
        feedback (Optional[str]): The evaluator's feedback.
        score (Optional[float]): The evaluator's score.
        evaluation_source (EvaluationSource): If the evaluation came from original order or flipped; or inconclusive.

    """

    feedback: str = Field(
        default_factory=str,
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    score: Optional[float] = Field(
        default=None,
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    evaluation_source: Optional[EvaluationSource] = Field(
        default=None,
        description=(
            "Whether the evaluation comes from original, or flipped ordering. Can also be neither here indicating inconclusive judgement."
        ),
    )
    invalid_prediction: bool = Field(
        default=False, description="Whether or not the prediction is a valid one."
    )
    invalid_reason: Optional[str] = Field(
        default=None, description="Reason as to why prediction is invalid."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "PairwiseEvaluatorExamplePrediction"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Data example class name.
##  PairwiseEvaluatorPredictionDataset #
Bases: `BaseLlamaPredictionDataset`
Pairwise evaluation predictions dataset class.
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
class PairwiseEvaluatorPredictionDataset(BaseLlamaPredictionDataset):
    """Pairwise evaluation predictions dataset class."""

    _prediction_type = PairwiseEvaluatorExamplePrediction

    def to_pandas(self) -> Any:
        """Create pandas dataframe."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this function. Please install it with `pip install pandas`."
            )

        data: Dict[str, List] = {
            "feedback": [],
            "score": [],
            "ordering": [],
        }
        for prediction in self.predictions:
            if not isinstance(prediction, PairwiseEvaluatorExamplePrediction):
                raise ValueError(
                    "PairwiseEvaluatorPredictionDataset can only contain PairwiseEvaluatorExamplePrediction instances."
                )
            data["feedback"].append(prediction.feedback)
            data["score"].append(prediction.score)
            data["ordering"].append(str(prediction.evaluation_source))

        return pd.DataFrame(data)

    @property
    def class_name(self) -> str:
        """Class name."""
        return "PairwiseEvaluatorPredictionDataset"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Class name.
###  to_pandas #
```
to_pandas() -> Any

```

Create pandas dataframe.
Source code in `llama-index-core/llama_index/core/llama_dataset/evaluator_evaluation.py`

| ```
def to_pandas(self) -> Any:
    """Create pandas dataframe."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for this function. Please install it with `pip install pandas`."
        )

    data: Dict[str, List] = {
        "feedback": [],
        "score": [],
        "ordering": [],
    }
    for prediction in self.predictions:
        if not isinstance(prediction, PairwiseEvaluatorExamplePrediction):
            raise ValueError(
                "PairwiseEvaluatorPredictionDataset can only contain PairwiseEvaluatorExamplePrediction instances."
            )
        data["feedback"].append(prediction.feedback)
        data["score"].append(prediction.score)
        data["ordering"].append(str(prediction.evaluation_source))

    return pd.DataFrame(data)

```
  
---|---  
##  LabelledRagDataExample #
Bases: `BaseLlamaDataExample`
RAG example class. Analogous to traditional ML datasets, this dataset contains the "features" (i.e., query + context) to make a prediction and the "label" (i.e., response) to evaluate the prediction.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query` |  `str` |  The user query |  _required_  
`query_by` |  `CreatedBy` |  Query generated by human or ai (model-name) |  `None`  
`reference_contexts` |  `Optional[List[str]]` |  The contexts used for response |  `None`  
`reference_answer` |  `[str]` |  Reference answer to the query. An answer that would receive full marks upon evaluation. |  _required_  
`reference_answer_by` |  `CreatedBy | None` |  The reference answer generated by human or ai (model-name). |  `None`  
Source code in `llama-index-core/llama_index/core/llama_dataset/rag.py`

| ```
class LabelledRagDataExample(BaseLlamaDataExample):
    """
    RAG example class. Analogous to traditional ML datasets, this dataset contains
    the "features" (i.e., query + context) to make a prediction and the "label" (i.e., response)
    to evaluate the prediction.

    Args:
        query (str): The user query
        query_by (CreatedBy): Query generated by human or ai (model-name)
        reference_contexts (Optional[List[str]]): The contexts used for response
        reference_answer ([str]): Reference answer to the query. An answer
                                    that would receive full marks upon evaluation.
        reference_answer_by: The reference answer generated by human or ai (model-name).

    """

    query: str = Field(
        default_factory=str, description="The user query for the example."
    )
    query_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the query."
    )
    reference_contexts: Optional[List[str]] = Field(
        default=None,
        description="The contexts used to generate the reference answer.",
    )
    reference_answer: str = Field(
        default_factory=str,
        description="The reference (ground-truth) answer to the example.",
    )
    reference_answer_by: Optional[CreatedBy] = Field(
        default=None, description="What generated the reference answer."
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "LabelledRagDataExample"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Data example class name.
##  LabelledRagDataset #
Bases: `BaseLlamaDataset[BaseQueryEngine]`
RagDataset class.
Source code in `llama-index-core/llama_index/core/llama_dataset/rag.py`

| ```
class LabelledRagDataset(BaseLlamaDataset[BaseQueryEngine]):
    """RagDataset class."""

    _example_type = LabelledRagDataExample

    def to_pandas(self) -> Any:
        """Create pandas dataframe."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this function. Please install it with `pip install pandas`."
            )

        data: Dict[str, List] = {
            "query": [],
            "reference_contexts": [],
            "reference_answer": [],
            "reference_answer_by": [],
            "query_by": [],
        }
        for example in self.examples:
            if not isinstance(example, LabelledRagDataExample):
                raise ValueError(
                    "All examples in the dataset must be of type LabelledRagDataExample."
                )
            data["query"].append(example.query)
            data["reference_contexts"].append(example.reference_contexts)
            data["reference_answer"].append(example.reference_answer)
            data["reference_answer_by"].append(str(example.reference_answer_by))
            data["query_by"].append(str(example.query_by))

        return pd.DataFrame(data)

    async def _apredict_example(  # type: ignore
        self,
        predictor: BaseQueryEngine,
        example: LabelledRagDataExample,
        sleep_time_in_seconds: int,
    ) -> RagExamplePrediction:
        """Async predict RAG example with a query engine."""
        await asyncio.sleep(sleep_time_in_seconds)
        response = await predictor.aquery(example.query)
        return RagExamplePrediction(
            response=str(response), contexts=[s.text for s in response.source_nodes]
        )

    def _predict_example(  # type: ignore
        self,
        predictor: BaseQueryEngine,
        example: LabelledRagDataExample,
        sleep_time_in_seconds: int = 0,
    ) -> RagExamplePrediction:
        """Predict RAG example with a query engine."""
        time.sleep(sleep_time_in_seconds)
        response = predictor.query(example.query)
        return RagExamplePrediction(
            response=str(response), contexts=[s.text for s in response.source_nodes]
        )

    def _construct_prediction_dataset(  # type: ignore
        self, predictions: Sequence[RagExamplePrediction]
    ) -> RagPredictionDataset:
        """Construct prediction dataset."""
        return RagPredictionDataset(predictions=predictions)

    @property
    def class_name(self) -> str:
        """Class name."""
        return "LabelledRagDataset"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Class name.
###  to_pandas #
```
to_pandas() -> Any

```

Create pandas dataframe.
Source code in `llama-index-core/llama_index/core/llama_dataset/rag.py`

| ```
def to_pandas(self) -> Any:
    """Create pandas dataframe."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for this function. Please install it with `pip install pandas`."
        )

    data: Dict[str, List] = {
        "query": [],
        "reference_contexts": [],
        "reference_answer": [],
        "reference_answer_by": [],
        "query_by": [],
    }
    for example in self.examples:
        if not isinstance(example, LabelledRagDataExample):
            raise ValueError(
                "All examples in the dataset must be of type LabelledRagDataExample."
            )
        data["query"].append(example.query)
        data["reference_contexts"].append(example.reference_contexts)
        data["reference_answer"].append(example.reference_answer)
        data["reference_answer_by"].append(str(example.reference_answer_by))
        data["query_by"].append(str(example.query_by))

    return pd.DataFrame(data)

```
  
---|---  
##  RagExamplePrediction #
Bases: `BaseLlamaExamplePrediction`
RAG example prediction class.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`response` |  `str` |  The response generated by the LLM. |  `''`  
`contexts` |  `Optional[List[str]]` |  The retrieved context (text) for generating response. |  `None`  
Source code in `llama-index-core/llama_index/core/llama_dataset/rag.py`

| ```
class RagExamplePrediction(BaseLlamaExamplePrediction):
    """
    RAG example prediction class.

    Args:
        response (str): The response generated by the LLM.
        contexts (Optional[List[str]]): The retrieved context (text) for generating
                                        response.

    """

    response: str = Field(
        default="",
        description="The generated (predicted) response that can be compared to a reference (ground-truth) answer.",
    )
    contexts: Optional[List[str]] = Field(
        default=None,
        description="The contexts in raw text form used to generate the response.",
    )

    @property
    def class_name(self) -> str:
        """Data example class name."""
        return "RagExamplePrediction"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Data example class name.
##  RagPredictionDataset #
Bases: `BaseLlamaPredictionDataset`
RagDataset class.
Source code in `llama-index-core/llama_index/core/llama_dataset/rag.py`

| ```
class RagPredictionDataset(BaseLlamaPredictionDataset):
    """RagDataset class."""

    _prediction_type = RagExamplePrediction

    def to_pandas(self) -> Any:
        """Create pandas dataframe."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this function. Please install it with `pip install pandas`."
            )

        data: Dict[str, List] = {
            "response": [],
            "contexts": [],
        }
        for pred in self.predictions:
            if not isinstance(pred, RagExamplePrediction):
                raise ValueError(
                    "All predictions in the dataset must be of type RagExamplePrediction."
                )
            data["response"].append(pred.response)
            data["contexts"].append(pred.contexts)

        return pd.DataFrame(data)

    @property
    def class_name(self) -> str:
        """Class name."""
        return "RagPredictionDataset"

```
  
---|---  
###  class_name `property` #
```
class_name: str

```

Class name.
###  to_pandas #
```
to_pandas() -> Any

```

Create pandas dataframe.
Source code in `llama-index-core/llama_index/core/llama_dataset/rag.py`

| ```
def to_pandas(self) -> Any:
    """Create pandas dataframe."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for this function. Please install it with `pip install pandas`."
        )

    data: Dict[str, List] = {
        "response": [],
        "contexts": [],
    }
    for pred in self.predictions:
        if not isinstance(pred, RagExamplePrediction):
            raise ValueError(
                "All predictions in the dataset must be of type RagExamplePrediction."
            )
        data["response"].append(pred.response)
        data["contexts"].append(pred.contexts)

    return pd.DataFrame(data)

```
  
---|---  
##  download_llama_dataset #
```
download_llama_dataset(llama_dataset_class: str, download_dir: str, llama_datasets_url: str = LLAMA_DATASETS_URL, llama_datasets_lfs_url: str = LLAMA_DATASETS_LFS_URL, llama_datasets_source_files_tree_url: str = LLAMA_DATASETS_SOURCE_FILES_GITHUB_TREE_URL, show_progress: bool = False, load_documents: bool = True) -> Tuple[BaseLlamaDataset, List[Document]]

```

Download dataset from datasets-LFS and llamahub.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`dataset_class` |  |  The name of the llamadataset class you want to download, such as `PaulGrahamEssayDataset`. |  _required_  
`custom_dir` |  |  Custom dir name to download loader into (under parent folder). |  _required_  
`custom_path` |  |  Custom dirpath to download loader into. |  _required_  
`llama_datasets_url` |  `str` |  Url for getting ordinary files from llama_datasets repo |  `LLAMA_DATASETS_URL`  
`llama_datasets_lfs_url` |  `str` |  Url for lfs-traced files llama_datasets repo |  `LLAMA_DATASETS_LFS_URL`  
`llama_datasets_source_files_tree_url` |  `str` |  Url for listing source_files contents |  `LLAMA_DATASETS_SOURCE_FILES_GITHUB_TREE_URL`  
`refresh_cache` |  |  If true, the local cache will be skipped and the loader will be fetched directly from the remote repo. |  _required_  
`source_files_dirpath` |  |  The directory for storing source files |  _required_  
`library_path` |  |  File name of the library file. |  _required_  
`base_file_name` |  |  The rag dataset json file |  _required_  
`disable_library_cache` |  |  Boolean to control library cache |  _required_  
`override_path` |  |  Boolean to control overriding path |  _required_  
`show_progress` |  `bool` |  Boolean for showing progress on downloading source files |  `False`  
`load_documents` |  `bool` |  Boolean for whether or not source_files for LabelledRagDataset should be loaded. |  `True`  
Returns:
Type | Description  
---|---  
`Tuple[BaseLlamaDataset, List[Document]]` |  a `BaseLlamaDataset` and a `List[Document]`  
Source code in `llama-index-core/llama_index/core/llama_dataset/download.py`

| ```
def download_llama_dataset(
    llama_dataset_class: str,
    download_dir: str,
    llama_datasets_url: str = LLAMA_DATASETS_URL,
    llama_datasets_lfs_url: str = LLAMA_DATASETS_LFS_URL,
    llama_datasets_source_files_tree_url: str = LLAMA_DATASETS_SOURCE_FILES_GITHUB_TREE_URL,
    show_progress: bool = False,
    load_documents: bool = True,
) -> Tuple[BaseLlamaDataset, List[Document]]:
    """
    Download dataset from datasets-LFS and llamahub.

    Args:
        dataset_class: The name of the llamadataset class you want to download,
            such as `PaulGrahamEssayDataset`.
        custom_dir: Custom dir name to download loader into (under parent folder).
        custom_path: Custom dirpath to download loader into.
        llama_datasets_url: Url for getting ordinary files from llama_datasets repo
        llama_datasets_lfs_url: Url for lfs-traced files llama_datasets repo
        llama_datasets_source_files_tree_url: Url for listing source_files contents
        refresh_cache: If true, the local cache will be skipped and the
            loader will be fetched directly from the remote repo.
        source_files_dirpath: The directory for storing source files
        library_path: File name of the library file.
        base_file_name: The rag dataset json file
        disable_library_cache: Boolean to control library cache
        override_path: Boolean to control overriding path
        show_progress: Boolean for showing progress on downloading source files
        load_documents: Boolean for whether or not source_files for LabelledRagDataset should
                        be loaded.

    Returns:
        a `BaseLlamaDataset` and a `List[Document]`

    """
    filenames: Tuple[str, str] = download(
        llama_dataset_class,
        llama_datasets_url=llama_datasets_url,
        llama_datasets_lfs_url=llama_datasets_lfs_url,
        llama_datasets_source_files_tree_url=llama_datasets_source_files_tree_url,
        refresh_cache=True,
        custom_path=download_dir,
        library_path="library.json",
        disable_library_cache=True,
        override_path=True,
        show_progress=show_progress,
    )
    dataset_filename, source_files_dir = filenames
    track_download(llama_dataset_class, MODULE_TYPE.DATASETS)

    dataset = _resolve_dataset_class(dataset_filename).from_json(dataset_filename)
    documents = []

    # for now only rag datasets need to provide the documents
    # in order to build an index over them
    if "rag_dataset.json" in dataset_filename and load_documents:
        documents = SimpleDirectoryReader(input_dir=source_files_dir).load_data(
            show_progress=show_progress
        )

    return (dataset, documents)

```
  
---|---
