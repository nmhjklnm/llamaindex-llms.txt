# Simple multi modal
##  SimpleMultiModalQueryEngine #
Bases: `BaseQueryEngine`
Simple Multi Modal Retriever query engine.
Assumes that retrieved text context fits within context window of LLM, along with images.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`retriever` |  `MultiModalVectorIndexRetriever` |  A retriever object. |  _required_  
`multi_modal_llm` |  `Optional[LLM]` |  An LLM model. |  `None`  
`text_qa_template` |  `Optional[BasePromptTemplate]` |  Text QA Prompt Template. |  `None`  
`image_qa_template` |  `Optional[BasePromptTemplate]` |  Image QA Prompt Template. |  `None`  
`node_postprocessors` |  `Optional[List[BaseNodePostprocessor]]` |  Node Postprocessors. |  `None`  
`callback_manager` |  `Optional[CallbackManager]` |  A callback manager. |  `None`  
Source code in `llama-index-core/llama_index/core/query_engine/multi_modal.py`

| ```
class SimpleMultiModalQueryEngine(BaseQueryEngine):
    """
    Simple Multi Modal Retriever query engine.

    Assumes that retrieved text context fits within context window of LLM, along with images.

    Args:
        retriever (MultiModalVectorIndexRetriever): A retriever object.
        multi_modal_llm (Optional[LLM]): An LLM model.
        text_qa_template (Optional[BasePromptTemplate]): Text QA Prompt Template.
        image_qa_template (Optional[BasePromptTemplate]): Image QA Prompt Template.
        node_postprocessors (Optional[List[BaseNodePostprocessor]]): Node Postprocessors.
        callback_manager (Optional[CallbackManager]): A callback manager.

    """

    def __init__(
        self,
        retriever: "MultiModalVectorIndexRetriever",
        multi_modal_llm: Optional[LLM] = None,
        text_qa_template: Optional[BasePromptTemplate] = None,
        image_qa_template: Optional[BasePromptTemplate] = None,
        node_postprocessors: Optional[List[BaseNodePostprocessor]] = None,
        callback_manager: Optional[CallbackManager] = None,
        **kwargs: Any,
    ) -> None:
        self._retriever = retriever
        if multi_modal_llm:
            self._multi_modal_llm = multi_modal_llm
        else:
            try:
                from llama_index.llms.openai import (
                    OpenAIResponses,
                )  # pants: no-infer-dep

                self._multi_modal_llm = OpenAIResponses(
                    model="gpt-4.1", max_output_tokens=1000
                )
            except ImportError as e:
                raise ImportError(
                    "`llama-index-llms-openai` package cannot be found. "
                    "Please install it by using `pip install `llama-index-llms-openai`"
                )
        self._text_qa_template = text_qa_template or DEFAULT_TEXT_QA_PROMPT
        self._image_qa_template = image_qa_template or DEFAULT_TEXT_QA_PROMPT

        self._node_postprocessors = node_postprocessors or []
        callback_manager = callback_manager or CallbackManager([])
        for node_postprocessor in self._node_postprocessors:
            node_postprocessor.callback_manager = callback_manager

        super().__init__(callback_manager)

    def _get_prompts(self) -> Dict[str, Any]:
        """Get prompts."""
        return {"text_qa_template": self._text_qa_template}

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {}

    def _apply_node_postprocessors(
        self, nodes: List[NodeWithScore], query_bundle: QueryBundle
    ) -> List[NodeWithScore]:
        for node_postprocessor in self._node_postprocessors:
            nodes = node_postprocessor.postprocess_nodes(
                nodes, query_bundle=query_bundle
            )
        return nodes

    def retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        nodes = self._retriever.retrieve(query_bundle)
        return self._apply_node_postprocessors(nodes, query_bundle=query_bundle)

    async def aretrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        nodes = await self._retriever.aretrieve(query_bundle)
        return self._apply_node_postprocessors(nodes, query_bundle=query_bundle)

    def synthesize(
        self,
        query_bundle: QueryBundle,
        nodes: List[NodeWithScore],
        additional_source_nodes: Optional[Sequence[NodeWithScore]] = None,
    ) -> RESPONSE_TYPE:
        image_nodes, text_nodes = _get_image_and_text_nodes(nodes)
        context_str = "\n\n".join(
            [r.get_content(metadata_mode=MetadataMode.LLM) for r in text_nodes]
        )
        fmt_prompt = self._text_qa_template.format(
            context_str=context_str, query_str=query_bundle.query_str
        )

        blocks: List[Union[ImageBlock, TextBlock]] = [
            image_node_to_image_block(image_node.node)
            for image_node in image_nodes
            if isinstance(image_node.node, ImageNode)
        ]

        blocks.append(TextBlock(text=fmt_prompt))

        llm_response = self._multi_modal_llm.chat(
            [ChatMessage(role="user", blocks=blocks)]
        )
        return Response(
            response=llm_response.message.content,
            source_nodes=nodes,
            metadata={"text_nodes": text_nodes, "image_nodes": image_nodes},
        )

    def _get_response_with_images(
        self,
        prompt_str: str,
        image_nodes: List[NodeWithScore],
    ) -> RESPONSE_TYPE:
        assert all(isinstance(node.node, ImageNode) for node in image_nodes)

        fmt_prompt = self._image_qa_template.format(
            query_str=prompt_str,
        )

        blocks: List[Union[ImageBlock, TextBlock]] = [
            image_node_to_image_block(image_node.node)
            for image_node in image_nodes
            if isinstance(image_node.node, ImageNode)
        ]

        blocks.append(TextBlock(text=fmt_prompt))

        llm_response = self._multi_modal_llm.chat(
            [ChatMessage(role="user", blocks=blocks)]
        )
        return Response(
            response=llm_response.message.content,
            source_nodes=image_nodes,
            metadata={"image_nodes": image_nodes},
        )

    async def asynthesize(
        self,
        query_bundle: QueryBundle,
        nodes: List[NodeWithScore],
        additional_source_nodes: Optional[Sequence[NodeWithScore]] = None,
    ) -> RESPONSE_TYPE:
        image_nodes, text_nodes = _get_image_and_text_nodes(nodes)
        context_str = "\n\n".join(
            [r.get_content(metadata_mode=MetadataMode.LLM) for r in text_nodes]
        )
        fmt_prompt = self._text_qa_template.format(
            context_str=context_str, query_str=query_bundle.query_str
        )

        blocks: List[Union[ImageBlock, TextBlock]] = [
            image_node_to_image_block(image_node.node)
            for image_node in image_nodes
            if isinstance(image_node.node, ImageNode)
        ]

        blocks.append(TextBlock(text=fmt_prompt))

        llm_response = await self._multi_modal_llm.achat(
            [ChatMessage(role="user", blocks=blocks)]
        )
        return Response(
            response=llm_response.message.content,
            source_nodes=nodes,
            metadata={"text_nodes": text_nodes, "image_nodes": image_nodes},
        )

    def _query(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Answer a query."""
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            with self.callback_manager.event(
                CBEventType.RETRIEVE,
                payload={EventPayload.QUERY_STR: query_bundle.query_str},
            ) as retrieve_event:
                nodes = self.retrieve(query_bundle)

                retrieve_event.on_end(
                    payload={EventPayload.NODES: nodes},
                )

            response = self.synthesize(
                query_bundle,
                nodes=nodes,
            )

            query_event.on_end(payload={EventPayload.RESPONSE: response})

        return response

    def image_query(self, image_path: QueryType, prompt_str: str) -> RESPONSE_TYPE:
        """Answer a image query."""
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: str(image_path)}
        ) as query_event:
            with self.callback_manager.event(
                CBEventType.RETRIEVE,
                payload={EventPayload.QUERY_STR: str(image_path)},
            ) as retrieve_event:
                nodes = self._retriever.image_to_image_retrieve(image_path)

                retrieve_event.on_end(
                    payload={EventPayload.NODES: nodes},
                )

            image_nodes, _ = _get_image_and_text_nodes(nodes)
            response = self._get_response_with_images(
                prompt_str=prompt_str,
                image_nodes=image_nodes,
            )

            query_event.on_end(payload={EventPayload.RESPONSE: response})

        return response

    async def _aquery(self, query_bundle: QueryBundle) -> RESPONSE_TYPE:
        """Answer a query."""
        with self.callback_manager.event(
            CBEventType.QUERY, payload={EventPayload.QUERY_STR: query_bundle.query_str}
        ) as query_event:
            with self.callback_manager.event(
                CBEventType.RETRIEVE,
                payload={EventPayload.QUERY_STR: query_bundle.query_str},
            ) as retrieve_event:
                nodes = await self.aretrieve(query_bundle)

                retrieve_event.on_end(
                    payload={EventPayload.NODES: nodes},
                )

            response = await self.asynthesize(
                query_bundle,
                nodes=nodes,
            )

            query_event.on_end(payload={EventPayload.RESPONSE: response})

        return response

    @property
    def retriever(self) -> "MultiModalVectorIndexRetriever":
        """Get the retriever object."""
        return self._retriever

```
  
---|---  
###  retriever `property` #
```
retriever: MultiModalVectorIndexRetriever

```

Get the retriever object.
###  image_query #
```
image_query(image_path: QueryType, prompt_str: str) -> RESPONSE_TYPE

```

Answer a image query.
Source code in `llama-index-core/llama_index/core/query_engine/multi_modal.py`

| ```
def image_query(self, image_path: QueryType, prompt_str: str) -> RESPONSE_TYPE:
    """Answer a image query."""
    with self.callback_manager.event(
        CBEventType.QUERY, payload={EventPayload.QUERY_STR: str(image_path)}
    ) as query_event:
        with self.callback_manager.event(
            CBEventType.RETRIEVE,
            payload={EventPayload.QUERY_STR: str(image_path)},
        ) as retrieve_event:
            nodes = self._retriever.image_to_image_retrieve(image_path)

            retrieve_event.on_end(
                payload={EventPayload.NODES: nodes},
            )

        image_nodes, _ = _get_image_and_text_nodes(nodes)
        response = self._get_response_with_images(
            prompt_str=prompt_str,
            image_nodes=image_nodes,
        )

        query_event.on_end(payload={EventPayload.RESPONSE: response})

    return response

```
  
---|---
