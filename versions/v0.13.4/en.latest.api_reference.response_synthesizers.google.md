# Google
##  GoogleTextSynthesizer #
Bases: `BaseSynthesizer`
Google's Attributed Question and Answering service.
Given a user's query and a list of passages, Google's server will return a response that is grounded to the provided list of passages. It will not base the response on parametric memory.
Source code in `llama-index-integrations/response_synthesizers/llama-index-response-synthesizers-google/llama_index/response_synthesizers/google/base.py`

| ```
class GoogleTextSynthesizer(BaseSynthesizer):
    """
    Google's Attributed Question and Answering service.

    Given a user's query and a list of passages, Google's server will return
    a response that is grounded to the provided list of passages. It will not
    base the response on parametric memory.
    """

    _client: Any
    _temperature: float
    _answer_style: Any
    _safety_setting: List[Any]

    def __init__(
        self,
        *,
        temperature: float,
        answer_style: Any,
        safety_setting: List[Any],
        **kwargs: Any,
    ):
        """
        Create a new Google AQA.

        Prefer to use the factory `from_defaults` instead for type safety.
        See `from_defaults` for more documentation.
        """
        try:
            import llama_index.vector_stores.google.genai_extension as genaix
        except ImportError:
            raise ImportError(_import_err_msg)

        super().__init__(
            llm=MockLLM(),
            output_cls=SynthesizedResponse,
            **kwargs,
        )

        self._client = genaix.build_generative_service()
        self._temperature = temperature
        self._answer_style = answer_style
        self._safety_setting = safety_setting

    # Type safe factory that is only available if Google is installed.
    @classmethod
    def from_defaults(
        cls,
        temperature: float = 0.7,
        answer_style: int = 1,
        safety_setting: List["genai.SafetySetting"] = [],
    ) -> "GoogleTextSynthesizer":
        """
        Create a new Google AQA.

        Example:
          responder = GoogleTextSynthesizer.create(
              temperature=0.7,
              answer_style=AnswerStyle.ABSTRACTIVE,
              safety_setting=[
                  SafetySetting(
                      category=HARM_CATEGORY_SEXUALLY_EXPLICIT,
                      threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                  ),
              ]
          )

        Args:
          temperature: 0.0 to 1.0.
          answer_style: See `google.ai.generativelanguage.GenerateAnswerRequest.AnswerStyle`
            The default is ABSTRACTIVE (1).
          safety_setting: See `google.ai.generativelanguage.SafetySetting`.

        Returns:
          an instance of GoogleTextSynthesizer.

        """
        return cls(
            temperature=temperature,
            answer_style=answer_style,
            safety_setting=safety_setting,
        )

    def get_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> SynthesizedResponse:
        """
        Generate a grounded response on provided passages.

        Args:
            query_str: The user's question.
            text_chunks: A list of passages that should be used to answer the
                question.

        Returns:
            A `SynthesizedResponse` object.

        """
        try:
            import llama_index.vector_stores.google.genai_extension as genaix

            import google.ai.generativelanguage as genai
        except ImportError:
            raise ImportError(_import_err_msg)

        client = cast(genai.GenerativeServiceClient, self._client)
        response = genaix.generate_answer(
            prompt=query_str,
            passages=list(text_chunks),
            answer_style=self._answer_style,
            safety_settings=self._safety_setting,
            temperature=self._temperature,
            client=client,
        )

        return SynthesizedResponse(
            answer=response.answer,
            attributed_passages=[
                passage.text for passage in response.attributed_passages
            ],
            answerable_probability=response.answerable_probability,
        )

    async def aget_response(
        self,
        query_str: str,
        text_chunks: Sequence[str],
        **response_kwargs: Any,
    ) -> RESPONSE_TEXT_TYPE:
        # TODO: Implement a true async version.
        return self.get_response(query_str, text_chunks, **response_kwargs)

    def synthesize(
        self,
        query: QueryTextType,
        nodes: List[NodeWithScore],
        additional_source_nodes: Optional[Sequence[NodeWithScore]] = None,
        **response_kwargs: Any,
    ) -> Response:
        """
        Returns a grounded response based on provided passages.

        Returns:
            Response's `source_nodes` will begin with a list of attributed
            passages. These passages are the ones that were used to construct
            the grounded response. These passages will always have no score,
            the only way to mark them as attributed passages. Then, the list
            will follow with the originally provided passages, which will have
            a score from the retrieval.

            Response's `metadata` may also have have an entry with key
            `answerable_probability`, which is the model's estimate of the
            probability that its answer is correct and grounded in the input
            passages.

        """
        if len(nodes) == 0:
            return Response("Empty Response")

        if isinstance(query, str):
            query = QueryBundle(query_str=query)

        with self._callback_manager.event(
            CBEventType.SYNTHESIZE, payload={EventPayload.QUERY_STR: query.query_str}
        ) as event:
            internal_response = self.get_response(
                query_str=query.query_str,
                text_chunks=[
                    n.node.get_content(metadata_mode=MetadataMode.LLM) for n in nodes
                ],
                **response_kwargs,
            )

            additional_source_nodes = list(additional_source_nodes or [])

            external_response = self._prepare_external_response(
                internal_response, nodes + additional_source_nodes
            )

            event.on_end(payload={EventPayload.RESPONSE: external_response})

        return external_response

    async def asynthesize(
        self,
        query: QueryTextType,
        nodes: List[NodeWithScore],
        additional_source_nodes: Optional[Sequence[NodeWithScore]] = None,
        **response_kwargs: Any,
    ) -> Response:
        # TODO: Implement a true async version.
        return self.synthesize(query, nodes, additional_source_nodes, **response_kwargs)

    def _prepare_external_response(
        self,
        response: SynthesizedResponse,
        source_nodes: List[NodeWithScore],
    ) -> Response:
        return Response(
            response=response.answer,
            source_nodes=[
                NodeWithScore(node=TextNode(text=passage))
                for passage in response.attributed_passages
            ]
            + source_nodes,
            metadata={
                "answerable_probability": response.answerable_probability,
            },
        )

    def _get_prompts(self) -> PromptDictType:
        # Not used.
        return {}

    def _update_prompts(self, prompts_dict: PromptDictType) -> None:
        # Not used.
        ...

```
  
---|---  
###  from_defaults `classmethod` #
```
from_defaults(temperature: float = 0.7, answer_style: int = 1, safety_setting: List[SafetySetting] = []) -> GoogleTextSynthesizer

```

Create a new Google AQA.
Example
responder = GoogleTextSynthesizer.create( temperature=0.7, answer_style=AnswerStyle.ABSTRACTIVE, safety_setting=[ SafetySetting( category=HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE, ), ] )
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`temperature` |  `float` |  0.0 to 1.0. |  `0.7`  
`answer_style` |  `int` |  See `google.ai.generativelanguage.GenerateAnswerRequest.AnswerStyle` The default is ABSTRACTIVE (1). |  `1`  
`safety_setting` |  `List[SafetySetting]` |  See `google.ai.generativelanguage.SafetySetting`. |  `[]`  
Returns:
Type | Description  
---|---  
`GoogleTextSynthesizer` |  an instance of GoogleTextSynthesizer.  
Source code in `llama-index-integrations/response_synthesizers/llama-index-response-synthesizers-google/llama_index/response_synthesizers/google/base.py`

| ```
@classmethod
def from_defaults(
    cls,
    temperature: float = 0.7,
    answer_style: int = 1,
    safety_setting: List["genai.SafetySetting"] = [],
) -> "GoogleTextSynthesizer":
    """
    Create a new Google AQA.

    Example:
      responder = GoogleTextSynthesizer.create(
          temperature=0.7,
          answer_style=AnswerStyle.ABSTRACTIVE,
          safety_setting=[
              SafetySetting(
                  category=HARM_CATEGORY_SEXUALLY_EXPLICIT,
                  threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
              ),
          ]
      )

    Args:
      temperature: 0.0 to 1.0.
      answer_style: See `google.ai.generativelanguage.GenerateAnswerRequest.AnswerStyle`
        The default is ABSTRACTIVE (1).
      safety_setting: See `google.ai.generativelanguage.SafetySetting`.

    Returns:
      an instance of GoogleTextSynthesizer.

    """
    return cls(
        temperature=temperature,
        answer_style=answer_style,
        safety_setting=safety_setting,
    )

```
  
---|---  
###  get_response #
```
get_response(query_str: str, text_chunks: Sequence[str], **response_kwargs: Any) -> SynthesizedResponse

```

Generate a grounded response on provided passages.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_str` |  `str` |  The user's question. |  _required_  
`text_chunks` |  `Sequence[str]` |  A list of passages that should be used to answer the question. |  _required_  
Returns:
Type | Description  
---|---  
`SynthesizedResponse` |  A `SynthesizedResponse` object.  
Source code in `llama-index-integrations/response_synthesizers/llama-index-response-synthesizers-google/llama_index/response_synthesizers/google/base.py`

| ```
def get_response(
    self,
    query_str: str,
    text_chunks: Sequence[str],
    **response_kwargs: Any,
) -> SynthesizedResponse:
    """
    Generate a grounded response on provided passages.

    Args:
        query_str: The user's question.
        text_chunks: A list of passages that should be used to answer the
            question.

    Returns:
        A `SynthesizedResponse` object.

    """
    try:
        import llama_index.vector_stores.google.genai_extension as genaix

        import google.ai.generativelanguage as genai
    except ImportError:
        raise ImportError(_import_err_msg)

    client = cast(genai.GenerativeServiceClient, self._client)
    response = genaix.generate_answer(
        prompt=query_str,
        passages=list(text_chunks),
        answer_style=self._answer_style,
        safety_settings=self._safety_setting,
        temperature=self._temperature,
        client=client,
    )

    return SynthesizedResponse(
        answer=response.answer,
        attributed_passages=[
            passage.text for passage in response.attributed_passages
        ],
        answerable_probability=response.answerable_probability,
    )

```
  
---|---  
###  synthesize #
```
synthesize(query: QueryTextType, nodes: List[NodeWithScore], additional_source_nodes: Optional[Sequence[NodeWithScore]] = None, **response_kwargs: Any) -> Response

```

Returns a grounded response based on provided passages.
Returns:
Type | Description  
---|---  
`Response` |  Response's `source_nodes` will begin with a list of attributed  
`Response` |  passages. These passages are the ones that were used to construct  
`Response` |  the grounded response. These passages will always have no score,  
`Response` |  the only way to mark them as attributed passages. Then, the list  
`Response` |  will follow with the originally provided passages, which will have  
`Response` |  a score from the retrieval.  
`Response` |  Response's `metadata` may also have have an entry with key  
`Response` |  `answerable_probability`, which is the model's estimate of the  
`Response` |  probability that its answer is correct and grounded in the input  
`Response` |  passages.  
Source code in `llama-index-integrations/response_synthesizers/llama-index-response-synthesizers-google/llama_index/response_synthesizers/google/base.py`

| ```
def synthesize(
    self,
    query: QueryTextType,
    nodes: List[NodeWithScore],
    additional_source_nodes: Optional[Sequence[NodeWithScore]] = None,
    **response_kwargs: Any,
) -> Response:
    """
    Returns a grounded response based on provided passages.

    Returns:
        Response's `source_nodes` will begin with a list of attributed
        passages. These passages are the ones that were used to construct
        the grounded response. These passages will always have no score,
        the only way to mark them as attributed passages. Then, the list
        will follow with the originally provided passages, which will have
        a score from the retrieval.

        Response's `metadata` may also have have an entry with key
        `answerable_probability`, which is the model's estimate of the
        probability that its answer is correct and grounded in the input
        passages.

    """
    if len(nodes) == 0:
        return Response("Empty Response")

    if isinstance(query, str):
        query = QueryBundle(query_str=query)

    with self._callback_manager.event(
        CBEventType.SYNTHESIZE, payload={EventPayload.QUERY_STR: query.query_str}
    ) as event:
        internal_response = self.get_response(
            query_str=query.query_str,
            text_chunks=[
                n.node.get_content(metadata_mode=MetadataMode.LLM) for n in nodes
            ],
            **response_kwargs,
        )

        additional_source_nodes = list(additional_source_nodes or [])

        external_response = self._prepare_external_response(
            internal_response, nodes + additional_source_nodes
        )

        event.on_end(payload={EventPayload.RESPONSE: external_response})

    return external_response

```
  
---|---
