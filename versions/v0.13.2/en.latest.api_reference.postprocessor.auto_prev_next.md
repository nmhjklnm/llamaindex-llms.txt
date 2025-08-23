# Auto prev next
Node PostProcessor module.
##  AutoPrevNextNodePostprocessor #
Bases: `BaseNodePostprocessor`
Previous/Next Node post-processor.
Allows users to fetch additional nodes from the document store, based on the prev/next relationships of the nodes.
NOTE: difference with PrevNextPostprocessor is that this infers forward/backwards direction.
NOTE: this is a beta feature.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`docstore` |  `BaseDocumentStore` |  The document store. |  _required_  
`num_nodes` |  `int` |  The number of nodes to return (default: 1) |  `1`  
`infer_prev_next_tmpl` |  `str` |  The template to use for inference. Required fields are {context_str} and {query_str}. |  `"The current context information is provided. \nA question is also provided. \nYou are a retrieval agent deciding whether to search the document store for additional prior context or future context. \nGiven the context and question, return PREVIOUS or NEXT or NONE. \nExamples: \n\nContext: Describes the author's experience at Y Combinator.Question: What did the author do after his time at Y Combinator? \nAnswer: NEXT \n\nContext: Describes the author's experience at Y Combinator.Question: What did the author do before his time at Y Combinator? \nAnswer: PREVIOUS \n\nContext: Describe the author's experience at Y Combinator.Question: What did the author do at Y Combinator? \nAnswer: NONE \n\nContext: {context_str}\nQuestion: {query_str}\nAnswer: "`  
`llm` |  `Annotated[LLM, SerializeAsAny] | None` |  |  `None`  
`refine_prev_next_tmpl` |  `str` |  |  `'The current context information is provided. \nA question is also provided. \nAn existing answer is also provided.\nYou are a retrieval agent deciding whether to search the document store for additional prior context or future context. \nGiven the context, question, and previous answer, return PREVIOUS or NEXT or NONE.\nExamples: \n\nContext: {context_msg}\nQuestion: {query_str}\nExisting Answer: {existing_answer}\nAnswer: '`  
`verbose` |  `bool` |  |  `False`  
`response_mode` |  `ResponseMode` |  |  `<ResponseMode.COMPACT: 'compact'>`  
Source code in `llama-index-core/llama_index/core/postprocessor/node.py`

| ```
class AutoPrevNextNodePostprocessor(BaseNodePostprocessor):
    """
    Previous/Next Node post-processor.

    Allows users to fetch additional nodes from the document store,
    based on the prev/next relationships of the nodes.

    NOTE: difference with PrevNextPostprocessor is that
    this infers forward/backwards direction.

    NOTE: this is a beta feature.

    Args:
        docstore (BaseDocumentStore): The document store.
        num_nodes (int): The number of nodes to return (default: 1)
        infer_prev_next_tmpl (str): The template to use for inference.
            Required fields are {context_str} and {query_str}.

    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    docstore: BaseDocumentStore
    llm: Optional[SerializeAsAny[LLM]] = None
    num_nodes: int = Field(default=1)
    infer_prev_next_tmpl: str = Field(default=DEFAULT_INFER_PREV_NEXT_TMPL)
    refine_prev_next_tmpl: str = Field(default=DEFAULT_REFINE_INFER_PREV_NEXT_TMPL)
    verbose: bool = Field(default=False)
    response_mode: ResponseMode = Field(default=ResponseMode.COMPACT)

    @classmethod
    def class_name(cls) -> str:
        return "AutoPrevNextNodePostprocessor"

    def _parse_prediction(self, raw_pred: str) -> str:
        """Parse prediction."""
        pred = raw_pred.strip().lower()
        if "previous" in pred:
            return "previous"
        elif "next" in pred:
            return "next"
        elif "none" in pred:
            return "none"
        raise ValueError(f"Invalid prediction: {raw_pred}")

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        llm = self.llm or Settings.llm

        if query_bundle is None:
            raise ValueError("Missing query bundle.")

        infer_prev_next_prompt = PromptTemplate(
            self.infer_prev_next_tmpl,
        )
        refine_infer_prev_next_prompt = PromptTemplate(self.refine_prev_next_tmpl)

        all_nodes: Dict[str, NodeWithScore] = {}
        for node in nodes:
            all_nodes[node.node.node_id] = node
            # use response builder instead of llm directly
            # to be more robust to handling long context
            response_builder = get_response_synthesizer(
                llm=llm,
                text_qa_template=infer_prev_next_prompt,
                refine_template=refine_infer_prev_next_prompt,
                response_mode=self.response_mode,
            )
            raw_pred = response_builder.get_response(
                text_chunks=[node.node.get_content()],
                query_str=query_bundle.query_str,
            )
            raw_pred = cast(str, raw_pred)
            mode = self._parse_prediction(raw_pred)

            logger.debug(f"> Postprocessor Predicted mode: {mode}")
            if self.verbose:
                print(f"> Postprocessor Predicted mode: {mode}")

            if mode == "next":
                all_nodes.update(get_forward_nodes(node, self.num_nodes, self.docstore))
            elif mode == "previous":
                all_nodes.update(
                    get_backward_nodes(node, self.num_nodes, self.docstore)
                )
            elif mode == "none":
                pass
            else:
                raise ValueError(f"Invalid mode: {mode}")

        sorted_nodes = sorted(all_nodes.values(), key=lambda x: x.node.node_id)
        return list(sorted_nodes)

```
  
---|---
