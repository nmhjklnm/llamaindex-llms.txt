# Dataset generation
Evaluation modules.
##  DatasetGenerator #
Bases: `PromptMixin`
Generate dataset (question/ question-answer pairs) based on the given documents.
NOTE: this is a beta feature, subject to change!
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`nodes` |  `List[Node]` |  List of nodes. (Optional) |  _required_  
`llm` |  `LLM` |  Language model. |  `None`  
`callback_manager` |  `CallbackManager` |  Callback manager. |  `None`  
`num_questions_per_chunk` |  `int` |  number of question to be generated per chunk. Each document is chunked of size 512 words. |  `10`  
`text_question_template` |  `BasePromptTemplate | None` |  Question generation template. |  `None`  
`question_gen_query` |  `str | None` |  Question generation query. |  `None`  
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
@deprecated(
    "Deprecated in favor of `RagDatasetGenerator` which should be used instead.",
    action="always",
)
class DatasetGenerator(PromptMixin):
    """Generate dataset (question/ question-answer pairs) \
    based on the given documents.

    NOTE: this is a beta feature, subject to change!

    Args:
        nodes (List[Node]): List of nodes. (Optional)
        llm (LLM): Language model.
        callback_manager (CallbackManager): Callback manager.
        num_questions_per_chunk: number of question to be \
        generated per chunk. Each document is chunked of size 512 words.
        text_question_template: Question generation template.
        question_gen_query: Question generation query.

    """

    def __init__(
        self,
        nodes: List[BaseNode],
        llm: Optional[LLM] = None,
        callback_manager: Optional[CallbackManager] = None,
        num_questions_per_chunk: int = 10,
        text_question_template: BasePromptTemplate | None = None,
        text_qa_template: BasePromptTemplate | None = None,
        question_gen_query: str | None = None,
        metadata_mode: MetadataMode = MetadataMode.NONE,
        show_progress: bool = False,
    ) -> None:
        """Init params."""
        self.llm = llm or Settings.llm
        self.callback_manager = callback_manager or Settings.callback_manager
        self.text_question_template = text_question_template or PromptTemplate(
            DEFAULT_QUESTION_GENERATION_PROMPT
        )
        self.text_qa_template = text_qa_template or DEFAULT_TEXT_QA_PROMPT
        self.question_gen_query = (
            question_gen_query
            or f"You are a Teacher/Professor. Your task is to setup \
                        {num_questions_per_chunk} questions for an upcoming \
                        quiz/examination. The questions should be diverse in nature \
                            across the document. Restrict the questions to the \
                                context information provided."
        )
        self.nodes = nodes
        self._metadata_mode = metadata_mode
        self._show_progress = show_progress

    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        llm: Optional[LLM] = None,
        transformations: Optional[List[TransformComponent]] = None,
        callback_manager: Optional[CallbackManager] = None,
        num_questions_per_chunk: int = 10,
        text_question_template: BasePromptTemplate | None = None,
        text_qa_template: BasePromptTemplate | None = None,
        question_gen_query: str | None = None,
        required_keywords: List[str] | None = None,
        exclude_keywords: List[str] | None = None,
        show_progress: bool = False,
    ) -> DatasetGenerator:
        """Generate dataset from documents."""
        llm = llm or Settings.llm
        transformations = transformations or Settings.transformations
        callback_manager = callback_manager or Settings.callback_manager

        nodes = run_transformations(
            documents, transformations, show_progress=show_progress
        )

        # use node postprocessor to filter nodes
        required_keywords = required_keywords or []
        exclude_keywords = exclude_keywords or []
        node_postprocessor = KeywordNodePostprocessor(
            callback_manager=callback_manager,
            required_keywords=required_keywords,
            exclude_keywords=exclude_keywords,
        )
        node_with_scores = [NodeWithScore(node=node) for node in nodes]
        node_with_scores = node_postprocessor.postprocess_nodes(node_with_scores)
        nodes = [node_with_score.node for node_with_score in node_with_scores]

        return cls(
            nodes=nodes,
            llm=llm,
            callback_manager=callback_manager,
            num_questions_per_chunk=num_questions_per_chunk,
            text_question_template=text_question_template,
            text_qa_template=text_qa_template,
            question_gen_query=question_gen_query,
            show_progress=show_progress,
        )

    async def _agenerate_dataset(
        self,
        nodes: List[BaseNode],
        num: int | None = None,
        generate_response: bool = False,
    ) -> QueryResponseDataset:
        """Node question generator."""
        query_tasks: List[Coroutine] = []
        queries: Dict[str, str] = {}
        responses_dict: Dict[str, str] = {}

        if self._show_progress:
            from tqdm.asyncio import tqdm_asyncio

            async_module = tqdm_asyncio
        else:
            async_module = asyncio

        summary_indices: List[SummaryIndex] = []
        for node in nodes:
            if num is not None and len(query_tasks) >= num:
                break
            index = SummaryIndex.from_documents(
                [
                    Document(
                        text=node.get_content(metadata_mode=self._metadata_mode),
                        metadata=node.metadata,  # type: ignore
                    )
                ],
                callback_manager=self.callback_manager,
            )

            query_engine = index.as_query_engine(
                llm=self.llm,
                text_qa_template=self.text_question_template,
                use_async=True,
            )
            task = query_engine.aquery(
                self.question_gen_query,
            )
            query_tasks.append(task)
            summary_indices.append(index)

        responses = await async_module.gather(*query_tasks)
        for idx, response in enumerate(responses):
            result = str(response).strip().split("\n")
            cleaned_questions = [
                re.sub(r"^\d+[\).\s]", "", question).strip() for question in result
            ]
            cleaned_questions = [
                question for question in cleaned_questions if len(question) > 0
            ]
            cur_queries = {
                str(uuid.uuid4()): question for question in cleaned_questions
            }
            queries.update(cur_queries)

            if generate_response:
                index = summary_indices[idx]
                qr_tasks = []
                cur_query_items = list(cur_queries.items())
                cur_query_keys = [query_id for query_id, _ in cur_query_items]
                for query_id, query in cur_query_items:
                    qa_query_engine = index.as_query_engine(
                        llm=self.llm,
                        text_qa_template=self.text_qa_template,
                    )
                    qr_task = qa_query_engine.aquery(query)
                    qr_tasks.append(qr_task)
                qr_responses = await async_module.gather(*qr_tasks)
                for query_id, qa_response in zip(cur_query_keys, qr_responses):
                    responses_dict[query_id] = str(qa_response)
            else:
                pass

        query_ids = list(queries.keys())
        if num is not None:
            query_ids = query_ids[:num]
            # truncate queries, responses to the subset of query ids
            queries = {query_id: queries[query_id] for query_id in query_ids}
            if generate_response:
                responses_dict = {
                    query_id: responses_dict[query_id] for query_id in query_ids
                }

        return QueryResponseDataset(queries=queries, responses=responses_dict)

    async def agenerate_questions_from_nodes(self, num: int | None = None) -> List[str]:
        """Generates questions for each document."""
        dataset = await self._agenerate_dataset(
            self.nodes, num=num, generate_response=False
        )
        return dataset.questions

    async def agenerate_dataset_from_nodes(
        self, num: int | None = None
    ) -> QueryResponseDataset:
        """Generates questions for each document."""
        return await self._agenerate_dataset(
            self.nodes, num=num, generate_response=True
        )

    def generate_questions_from_nodes(self, num: int | None = None) -> List[str]:
        """Generates questions for each document."""
        return asyncio_run(self.agenerate_questions_from_nodes(num=num))

    def generate_dataset_from_nodes(
        self, num: int | None = None
    ) -> QueryResponseDataset:
        """Generates questions for each document."""
        return asyncio_run(self.agenerate_dataset_from_nodes(num=num))

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {
            "text_question_template": self.text_question_template,
            "text_qa_template": self.text_qa_template,
        }

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt modules."""
        return {}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "text_question_template" in prompts:
            self.text_question_template = prompts["text_question_template"]
        if "text_qa_template" in prompts:
            self.text_qa_template = prompts["text_qa_template"]

```
  
---|---  
###  from_documents `classmethod` #
```
from_documents(documents: List[Document], llm: Optional[LLM] = None, transformations: Optional[List[TransformComponent]] = None, callback_manager: Optional[CallbackManager] = None, num_questions_per_chunk: int = 10, text_question_template: BasePromptTemplate | None = None, text_qa_template: BasePromptTemplate | None = None, question_gen_query: str | None = None, required_keywords: List[str] | None = None, exclude_keywords: List[str] | None = None, show_progress: bool = False) -> DatasetGenerator

```

Generate dataset from documents.
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
@classmethod
def from_documents(
    cls,
    documents: List[Document],
    llm: Optional[LLM] = None,
    transformations: Optional[List[TransformComponent]] = None,
    callback_manager: Optional[CallbackManager] = None,
    num_questions_per_chunk: int = 10,
    text_question_template: BasePromptTemplate | None = None,
    text_qa_template: BasePromptTemplate | None = None,
    question_gen_query: str | None = None,
    required_keywords: List[str] | None = None,
    exclude_keywords: List[str] | None = None,
    show_progress: bool = False,
) -> DatasetGenerator:
    """Generate dataset from documents."""
    llm = llm or Settings.llm
    transformations = transformations or Settings.transformations
    callback_manager = callback_manager or Settings.callback_manager

    nodes = run_transformations(
        documents, transformations, show_progress=show_progress
    )

    # use node postprocessor to filter nodes
    required_keywords = required_keywords or []
    exclude_keywords = exclude_keywords or []
    node_postprocessor = KeywordNodePostprocessor(
        callback_manager=callback_manager,
        required_keywords=required_keywords,
        exclude_keywords=exclude_keywords,
    )
    node_with_scores = [NodeWithScore(node=node) for node in nodes]
    node_with_scores = node_postprocessor.postprocess_nodes(node_with_scores)
    nodes = [node_with_score.node for node_with_score in node_with_scores]

    return cls(
        nodes=nodes,
        llm=llm,
        callback_manager=callback_manager,
        num_questions_per_chunk=num_questions_per_chunk,
        text_question_template=text_question_template,
        text_qa_template=text_qa_template,
        question_gen_query=question_gen_query,
        show_progress=show_progress,
    )

```
  
---|---  
###  agenerate_questions_from_nodes `async` #
```
agenerate_questions_from_nodes(num: int | None = None) -> List[str]

```

Generates questions for each document.
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
async def agenerate_questions_from_nodes(self, num: int | None = None) -> List[str]:
    """Generates questions for each document."""
    dataset = await self._agenerate_dataset(
        self.nodes, num=num, generate_response=False
    )
    return dataset.questions

```
  
---|---  
###  agenerate_dataset_from_nodes `async` #
```
agenerate_dataset_from_nodes(num: int | None = None) -> QueryResponseDataset

```

Generates questions for each document.
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
async def agenerate_dataset_from_nodes(
    self, num: int | None = None
) -> QueryResponseDataset:
    """Generates questions for each document."""
    return await self._agenerate_dataset(
        self.nodes, num=num, generate_response=True
    )

```
  
---|---  
###  generate_questions_from_nodes #
```
generate_questions_from_nodes(num: int | None = None) -> List[str]

```

Generates questions for each document.
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
def generate_questions_from_nodes(self, num: int | None = None) -> List[str]:
    """Generates questions for each document."""
    return asyncio_run(self.agenerate_questions_from_nodes(num=num))

```
  
---|---  
###  generate_dataset_from_nodes #
```
generate_dataset_from_nodes(num: int | None = None) -> QueryResponseDataset

```

Generates questions for each document.
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
def generate_dataset_from_nodes(
    self, num: int | None = None
) -> QueryResponseDataset:
    """Generates questions for each document."""
    return asyncio_run(self.agenerate_dataset_from_nodes(num=num))

```
  
---|---  
##  QueryResponseDataset #
Bases: `BaseModel`
Query Response Dataset.
The response can be empty if the dataset is generated from documents.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`queries` |  `Dict[str, str]` |  Query id -> query. |  _required_  
`responses` |  `Dict[str, str]` |  Query id -> response. |  _required_  
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
@deprecated(
    "Deprecated in favor of `LabelledRagDataset` which should be used instead.",
    action="always",
)
class QueryResponseDataset(BaseModel):
    """
    Query Response Dataset.

    The response can be empty if the dataset is generated from documents.

    Args:
        queries (Dict[str, str]): Query id -> query.
        responses (Dict[str, str]): Query id -> response.

    """

    queries: Dict[str, str] = Field(
        default_factory=dict, description="Query id -> query"
    )
    responses: Dict[str, str] = Field(
        default_factory=dict, description="Query id -> response"
    )

    @classmethod
    def from_qr_pairs(
        cls,
        qr_pairs: List[Tuple[str, str]],
    ) -> QueryResponseDataset:
        """Create from qr pairs."""
        # define ids as simple integers
        queries = {str(idx): query for idx, (query, _) in enumerate(qr_pairs)}
        responses = {str(idx): response for idx, (_, response) in enumerate(qr_pairs)}
        return cls(queries=queries, responses=responses)

    @property
    def qr_pairs(self) -> List[Tuple[str, str]]:
        """Get pairs."""
        # if query_id not in response, throw error
        for query_id in self.queries:
            if query_id not in self.responses:
                raise ValueError(f"Query id {query_id} not in responses")

        return [
            (self.queries[query_id], self.responses[query_id])
            for query_id in self.queries
        ]

    @property
    def questions(self) -> List[str]:
        """Get questions."""
        return list(self.queries.values())

    def save_json(self, path: str) -> None:
        """Save json."""
        with open(path, "w") as f:
            json.dump(self.model_dump(), f, indent=4)

    @classmethod
    def from_json(cls, path: str) -> QueryResponseDataset:
        """Load json."""
        with open(path) as f:
            data = json.load(f)
        return cls(**data)

```
  
---|---  
###  qr_pairs `property` #
```
qr_pairs: List[Tuple[str, str]]

```

Get pairs.
###  questions `property` #
```
questions: List[str]

```

Get questions.
###  from_qr_pairs `classmethod` #
```
from_qr_pairs(qr_pairs: List[Tuple[str, str]]) -> QueryResponseDataset

```

Create from qr pairs.
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
@classmethod
def from_qr_pairs(
    cls,
    qr_pairs: List[Tuple[str, str]],
) -> QueryResponseDataset:
    """Create from qr pairs."""
    # define ids as simple integers
    queries = {str(idx): query for idx, (query, _) in enumerate(qr_pairs)}
    responses = {str(idx): response for idx, (_, response) in enumerate(qr_pairs)}
    return cls(queries=queries, responses=responses)

```
  
---|---  
###  save_json #
```
save_json(path: str) -> None

```

Save json.
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
def save_json(self, path: str) -> None:
    """Save json."""
    with open(path, "w") as f:
        json.dump(self.model_dump(), f, indent=4)

```
  
---|---  
###  from_json `classmethod` #
```
from_json(path: str) -> QueryResponseDataset

```

Load json.
Source code in `llama-index-core/llama_index/core/evaluation/dataset_generation.py`

| ```
@classmethod
def from_json(cls, path: str) -> QueryResponseDataset:
    """Load json."""
    with open(path) as f:
        data = json.load(f)
    return cls(**data)

```
  
---|---
