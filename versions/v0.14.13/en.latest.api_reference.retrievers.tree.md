# Tree
##  TreeAllLeafRetriever #
Bases: `BaseRetriever`
GPT all leaf retriever.
This class builds a query-specific tree from leaf nodes to return a response. Using this query mode means that the tree index doesn't need to be built when initialized, since we rebuild the tree for each query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`text_qa_template` |  `Optional[BasePromptTemplate]` |  Question-Answer Prompt (see :ref:`Prompt-Templates`). |  _required_  
Source code in `llama-index-core/llama_index/core/indices/tree/all_leaf_retriever.py`

| ```
class TreeAllLeafRetriever(BaseRetriever):
    """
    GPT all leaf retriever.

    This class builds a query-specific tree from leaf nodes to return a response.
    Using this query mode means that the tree index doesn't need to be built
    when initialized, since we rebuild the tree for each query.

    Args:
        text_qa_template (Optional[BasePromptTemplate]): Question-Answer Prompt
            (see :ref:`Prompt-Templates`).

    """

    def __init__(
        self,
        index: TreeIndex,
        callback_manager: Optional[CallbackManager] = None,
        object_map: Optional[dict] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        self._index = index
        self._index_struct = index.index_struct
        self._docstore = index.docstore
        super().__init__(
            callback_manager=callback_manager, object_map=object_map, verbose=verbose
        )

    def _retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        """Get nodes for response."""
        logger.info(f"> Starting query: {query_bundle.query_str}")
        index_struct = cast(IndexGraph, self._index_struct)
        all_nodes = self._docstore.get_node_dict(index_struct.all_nodes)
        sorted_node_list = get_sorted_node_list(all_nodes)
        return [NodeWithScore(node=node) for node in sorted_node_list]

```
  
---|---  
##  TreeSelectLeafEmbeddingRetriever #
Bases: `TreeSelectLeafRetriever`
Tree select leaf embedding retriever.
This class traverses the index graph using the embedding similarity between the query and the node text.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_template` |  `Optional[BasePromptTemplate]` |  Tree Select Query Prompt (see :ref:`Prompt-Templates`). |  `None`  
`query_template_multiple` |  `Optional[BasePromptTemplate]` |  Tree Select Query Prompt (Multiple) (see :ref:`Prompt-Templates`). |  `None`  
`text_qa_template` |  `Optional[BasePromptTemplate]` |  Question-Answer Prompt (see :ref:`Prompt-Templates`). |  `None`  
`refine_template` |  `Optional[BasePromptTemplate]` |  Refinement Prompt (see :ref:`Prompt-Templates`). |  `None`  
`child_branch_factor` |  `int` |  Number of child nodes to consider at each level. If child_branch_factor is 1, then the query will only choose one child node to traverse for any given parent node. If child_branch_factor is 2, then the query will choose two child nodes. |  `1`  
`embed_model` |  `Optional[BaseEmbedding]` |  Embedding model to use for embedding similarity. |  `None`  
Source code in `llama-index-core/llama_index/core/indices/tree/select_leaf_embedding_retriever.py`

| ```
class TreeSelectLeafEmbeddingRetriever(TreeSelectLeafRetriever):
    """
    Tree select leaf embedding retriever.

    This class traverses the index graph using the embedding similarity between the
    query and the node text.

    Args:
        query_template (Optional[BasePromptTemplate]): Tree Select Query Prompt
            (see :ref:`Prompt-Templates`).
        query_template_multiple (Optional[BasePromptTemplate]): Tree Select
            Query Prompt (Multiple)
            (see :ref:`Prompt-Templates`).
        text_qa_template (Optional[BasePromptTemplate]): Question-Answer Prompt
            (see :ref:`Prompt-Templates`).
        refine_template (Optional[BasePromptTemplate]): Refinement Prompt
            (see :ref:`Prompt-Templates`).
        child_branch_factor (int): Number of child nodes to consider at each level.
            If child_branch_factor is 1, then the query will only choose one child node
            to traverse for any given parent node.
            If child_branch_factor is 2, then the query will choose two child nodes.
        embed_model (Optional[BaseEmbedding]): Embedding model to use for
            embedding similarity.

    """

    def __init__(
        self,
        index: TreeIndex,
        embed_model: Optional[BaseEmbedding] = None,
        query_template: Optional[BasePromptTemplate] = None,
        text_qa_template: Optional[BasePromptTemplate] = None,
        refine_template: Optional[BasePromptTemplate] = None,
        query_template_multiple: Optional[BasePromptTemplate] = None,
        child_branch_factor: int = 1,
        verbose: bool = False,
        callback_manager: Optional[CallbackManager] = None,
        object_map: Optional[dict] = None,
        **kwargs: Any,
    ):
        super().__init__(
            index,
            query_template=query_template,
            text_qa_template=text_qa_template,
            refine_template=refine_template,
            query_template_multiple=query_template_multiple,
            child_branch_factor=child_branch_factor,
            verbose=verbose,
            callback_manager=callback_manager,
            object_map=object_map,
            **kwargs,
        )
        self._embed_model = embed_model or Settings.embed_model

    def _query_level(
        self,
        cur_node_ids: Dict[int, str],
        query_bundle: QueryBundle,
        level: int = 0,
    ) -> str:
        """Answer a query recursively."""
        cur_nodes = {
            index: self._docstore.get_node(node_id)
            for index, node_id in cur_node_ids.items()
        }
        cur_node_list = get_sorted_node_list(cur_nodes)

        # Get the node with the highest similarity to the query
        selected_nodes, selected_indices = self._get_most_similar_nodes(
            cur_node_list, query_bundle
        )

        result_response = None
        for node, index in zip(selected_nodes, selected_indices):
            logger.debug(
                f">[Level {level}] Node [{index + 1}] Summary text: "
                f"{' '.join(node.get_content().splitlines())}"
            )

            # Get the response for the selected node
            result_response = self._query_with_selected_node(
                node, query_bundle, level=level, prev_response=result_response
            )

        return cast(str, result_response)

    def _get_query_text_embedding_similarities(
        self, query_bundle: QueryBundle, nodes: List[BaseNode]
    ) -> List[float]:
        """
        Get query text embedding similarity.

        Cache the query embedding and the node text embedding.

        """
        if query_bundle.embedding is None:
            query_bundle.embedding = self._embed_model.get_agg_embedding_from_queries(
                query_bundle.embedding_strs
            )
        similarities = []
        for node in nodes:
            if node.embedding is None:
                node.embedding = self._embed_model.get_text_embedding(
                    node.get_content(metadata_mode=MetadataMode.EMBED)
                )

            similarity = self._embed_model.similarity(
                query_bundle.embedding, node.embedding
            )
            similarities.append(similarity)
        return similarities

    def _get_most_similar_nodes(
        self, nodes: List[BaseNode], query_bundle: QueryBundle
    ) -> Tuple[List[BaseNode], List[int]]:
        """Get the node with the highest similarity to the query."""
        similarities = self._get_query_text_embedding_similarities(query_bundle, nodes)

        selected_nodes: List[BaseNode] = []
        selected_indices: List[int] = []
        for node, _ in sorted(
            zip(nodes, similarities), key=lambda x: x[1], reverse=True
        ):
            if len(selected_nodes) < self.child_branch_factor:
                selected_nodes.append(node)
                selected_indices.append(nodes.index(node))
            else:
                break

        return selected_nodes, selected_indices

    def _select_nodes(
        self,
        cur_node_list: List[BaseNode],
        query_bundle: QueryBundle,
        level: int = 0,
    ) -> List[BaseNode]:
        selected_nodes, _ = self._get_most_similar_nodes(cur_node_list, query_bundle)
        return selected_nodes

```
  
---|---  
##  TreeSelectLeafRetriever #
Bases: `BaseRetriever`
Tree select leaf retriever.
This class traverses the index graph and searches for a leaf node that can best answer the query.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`query_template` |  `Optional[BasePromptTemplate]` |  Tree Select Query Prompt (see :ref:`Prompt-Templates`). |  `None`  
`query_template_multiple` |  `Optional[BasePromptTemplate]` |  Tree Select Query Prompt (Multiple) (see :ref:`Prompt-Templates`). |  `None`  
`child_branch_factor` |  `int` |  Number of child nodes to consider at each level. If child_branch_factor is 1, then the query will only choose one child node to traverse for any given parent node. If child_branch_factor is 2, then the query will choose two child nodes. |  `1`  
Source code in `llama-index-core/llama_index/core/indices/tree/select_leaf_retriever.py`

| ```
class TreeSelectLeafRetriever(BaseRetriever):
    """
    Tree select leaf retriever.

    This class traverses the index graph and searches for a leaf node that can best
    answer the query.

    Args:
        query_template (Optional[BasePromptTemplate]): Tree Select Query Prompt
            (see :ref:`Prompt-Templates`).
        query_template_multiple (Optional[BasePromptTemplate]): Tree Select
            Query Prompt (Multiple)
            (see :ref:`Prompt-Templates`).
        child_branch_factor (int): Number of child nodes to consider at each level.
            If child_branch_factor is 1, then the query will only choose one child node
            to traverse for any given parent node.
            If child_branch_factor is 2, then the query will choose two child nodes.

    """

    def __init__(
        self,
        index: TreeIndex,
        query_template: Optional[BasePromptTemplate] = None,
        text_qa_template: Optional[BasePromptTemplate] = None,
        refine_template: Optional[BasePromptTemplate] = None,
        query_template_multiple: Optional[BasePromptTemplate] = None,
        child_branch_factor: int = 1,
        verbose: bool = False,
        callback_manager: Optional[CallbackManager] = None,
        object_map: Optional[dict] = None,
        **kwargs: Any,
    ):
        self._index = index
        self._llm = index._llm
        self._index_struct = index.index_struct
        self._docstore = index.docstore
        self._prompt_helper = Settings._prompt_helper or PromptHelper.from_llm_metadata(
            self._llm.metadata,
        )

        self._text_qa_template = text_qa_template or DEFAULT_TEXT_QA_PROMPT
        self._refine_template = refine_template or DEFAULT_REFINE_PROMPT_SEL
        self.query_template = query_template or DEFAULT_QUERY_PROMPT
        self.query_template_multiple = (
            query_template_multiple or DEFAULT_QUERY_PROMPT_MULTIPLE
        )
        self.child_branch_factor = child_branch_factor
        super().__init__(
            callback_manager=callback_manager or Settings.callback_manager,
            object_map=object_map,
            verbose=verbose,
        )

    def _query_with_selected_node(
        self,
        selected_node: BaseNode,
        query_bundle: QueryBundle,
        prev_response: Optional[str] = None,
        level: int = 0,
    ) -> str:
        """
        Get response for selected node.

        If not leaf node, it will recursively call _query on the child nodes.
        If prev_response is provided, we will update prev_response with the answer.

        """
        query_str = query_bundle.query_str

        if len(self._index_struct.get_children(selected_node)) == 0:
            response_builder = get_response_synthesizer(
                llm=self._llm,
                text_qa_template=self._text_qa_template,
                refine_template=self._refine_template,
                callback_manager=self.callback_manager,
            )
            # use response builder to get answer from node
            node_text = get_text_from_node(selected_node, level=level)
            cur_response = response_builder.get_response(
                query_str, [node_text], prev_response=prev_response
            )
            cur_response = str(cur_response)
            logger.debug(f">[Level {level}] Current answer response: {cur_response} ")
        else:
            cur_response = self._query_level(
                self._index_struct.get_children(selected_node),
                query_bundle,
                level=level + 1,
            )

        if prev_response is None:
            return cur_response
        else:
            context_msg = selected_node.get_content(metadata_mode=MetadataMode.LLM)
            cur_response = self._llm.predict(
                self._refine_template,
                query_str=query_str,
                existing_answer=prev_response,
                context_msg=context_msg,
            )

            logger.debug(f">[Level {level}] Current refined response: {cur_response} ")
            return str(cur_response)

    def _query_level(
        self,
        cur_node_ids: Dict[int, str],
        query_bundle: QueryBundle,
        level: int = 0,
    ) -> str:
        """Answer a query recursively."""
        query_str = query_bundle.query_str
        cur_nodes = {
            index: self._docstore.get_node(node_id)
            for index, node_id in cur_node_ids.items()
        }
        cur_node_list = get_sorted_node_list(cur_nodes)

        if len(cur_node_list) == 1:
            logger.debug(f">[Level {level}] Only one node left. Querying node.")
            return self._query_with_selected_node(
                cur_node_list[0], query_bundle, level=level
            )
        elif self.child_branch_factor == 1:
            query_template = self.query_template.partial_format(
                num_chunks=len(cur_node_list), query_str=query_str
            )
            text_splitter = self._prompt_helper.get_text_splitter_given_prompt(
                prompt=query_template,
                num_chunks=len(cur_node_list),
                llm=self._llm,
            )
            numbered_node_text = get_numbered_text_from_nodes(
                cur_node_list, text_splitter=text_splitter
            )

            response = self._llm.predict(
                query_template,
                context_list=numbered_node_text,
            )
        else:
            query_template_multiple = self.query_template_multiple.partial_format(
                num_chunks=len(cur_node_list),
                query_str=query_str,
                branching_factor=self.child_branch_factor,
            )

            text_splitter = self._prompt_helper.get_text_splitter_given_prompt(
                prompt=query_template_multiple,
                num_chunks=len(cur_node_list),
                llm=self._llm,
            )
            numbered_node_text = get_numbered_text_from_nodes(
                cur_node_list, text_splitter=text_splitter
            )

            response = self._llm.predict(
                query_template_multiple,
                context_list=numbered_node_text,
            )

        debug_str = f">[Level {level}] Current response: {response}"
        logger.debug(debug_str)
        if self._verbose:
            print_text(debug_str, end="\n")

        numbers = extract_numbers_given_response(response, n=self.child_branch_factor)
        if numbers is None:
            debug_str = (
                f">[Level {level}] Could not retrieve response - no numbers present"
            )
            logger.debug(debug_str)
            if self._verbose:
                print_text(debug_str, end="\n")
            # just join text from current nodes as response
            return response
        result_response = None
        for number_str in numbers:
            number = int(number_str)
            if number > len(cur_node_list):
                logger.debug(
                    f">[Level {level}] Invalid response: {response} - "
                    f"number {number} out of range"
                )
                return response

            # number is 1-indexed, so subtract 1
            selected_node = cur_node_list[number - 1]

            info_str = (
                f">[Level {level}] Selected node: "
                f"[{number}]/[{','.join([str(int(n)) for n in numbers])}]"
            )
            logger.info(info_str)
            if self._verbose:
                print_text(info_str, end="\n")
            debug_str = " ".join(
                selected_node.get_content(metadata_mode=MetadataMode.LLM).splitlines()
            )
            full_debug_str = (
                f">[Level {level}] Node "
                f"[{number}] Summary text: "
                f"{selected_node.get_content(metadata_mode=MetadataMode.LLM)}"
            )
            logger.debug(full_debug_str)
            if self._verbose:
                print_text(full_debug_str, end="\n")
            result_response = self._query_with_selected_node(
                selected_node,
                query_bundle,
                prev_response=result_response,
                level=level,
            )
        # result_response should not be None
        return cast(str, result_response)

    def _query(self, query_bundle: QueryBundle) -> Response:
        """Answer a query."""
        # NOTE: this overrides the _query method in the base class
        info_str = f"> Starting query: {query_bundle.query_str}"
        logger.info(info_str)
        if self._verbose:
            print_text(info_str, end="\n")
        response_str = self._query_level(
            self._index_struct.root_nodes,
            query_bundle,
            level=0,
        ).strip()
        # TODO: fix source nodes
        return Response(response_str, source_nodes=[])

    def _select_nodes(
        self,
        cur_node_list: List[BaseNode],
        query_bundle: QueryBundle,
        level: int = 0,
    ) -> List[BaseNode]:
        query_str = query_bundle.query_str

        if self.child_branch_factor == 1:
            query_template = self.query_template.partial_format(
                num_chunks=len(cur_node_list), query_str=query_str
            )
            text_splitter = self._prompt_helper.get_text_splitter_given_prompt(
                prompt=query_template,
                num_chunks=len(cur_node_list),
                llm=self._llm,
            )
            numbered_node_text = get_numbered_text_from_nodes(
                cur_node_list, text_splitter=text_splitter
            )

            response = self._llm.predict(
                query_template,
                context_list=numbered_node_text,
            )
        else:
            query_template_multiple = self.query_template_multiple.partial_format(
                num_chunks=len(cur_node_list),
                query_str=query_str,
                branching_factor=self.child_branch_factor,
            )

            text_splitter = self._prompt_helper.get_text_splitter_given_prompt(
                prompt=query_template_multiple,
                num_chunks=len(cur_node_list),
                llm=self._llm,
            )
            numbered_node_text = get_numbered_text_from_nodes(
                cur_node_list, text_splitter=text_splitter
            )

            response = self._llm.predict(
                query_template_multiple,
                context_list=numbered_node_text,
            )

        debug_str = f">[Level {level}] Current response: {response}"
        logger.debug(debug_str)
        if self._verbose:
            print_text(debug_str, end="\n")

        numbers = extract_numbers_given_response(response, n=self.child_branch_factor)
        if numbers is None:
            debug_str = (
                f">[Level {level}] Could not retrieve response - no numbers present"
            )
            logger.debug(debug_str)
            if self._verbose:
                print_text(debug_str, end="\n")
            # just join text from current nodes as response
            return []

        selected_nodes = []
        for number_str in numbers:
            number = int(number_str)
            if number > len(cur_node_list):
                logger.debug(
                    f">[Level {level}] Invalid response: {response} - "
                    f"number {number} out of range"
                )
                continue

            # number is 1-indexed, so subtract 1
            selected_node = cur_node_list[number - 1]

            info_str = (
                f">[Level {level}] Selected node: "
                f"[{number}]/[{','.join([str(int(n)) for n in numbers])}]"
            )
            logger.info(info_str)
            if self._verbose:
                print_text(info_str, end="\n")
            debug_str = " ".join(
                selected_node.get_content(metadata_mode=MetadataMode.LLM).splitlines()
            )
            full_debug_str = (
                f">[Level {level}] Node "
                f"[{number}] Summary text: "
                f"{selected_node.get_content(metadata_mode=MetadataMode.LLM)}"
            )
            logger.debug(full_debug_str)
            if self._verbose:
                print_text(full_debug_str, end="\n")
            selected_nodes.append(selected_node)

        return selected_nodes

    def _retrieve_level(
        self,
        cur_node_ids: Dict[int, str],
        query_bundle: QueryBundle,
        level: int = 0,
    ) -> List[BaseNode]:
        """Answer a query recursively."""
        cur_nodes = {
            index: self._docstore.get_node(node_id)
            for index, node_id in cur_node_ids.items()
        }
        cur_node_list = get_sorted_node_list(cur_nodes)

        if len(cur_node_list) > self.child_branch_factor:
            selected_nodes = self._select_nodes(
                cur_node_list,
                query_bundle,
                level=level,
            )
        else:
            selected_nodes = cur_node_list

        children_nodes = {}
        for node in selected_nodes:
            node_dict = self._index_struct.get_children(node)
            children_nodes.update(node_dict)

        if len(children_nodes) == 0:
            # NOTE: leaf level
            return selected_nodes
        else:
            return self._retrieve_level(children_nodes, query_bundle, level + 1)

    def _retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        """Get nodes for response."""
        nodes = self._retrieve_level(
            self._index_struct.root_nodes,
            query_bundle,
            level=0,
        )
        return [NodeWithScore(node=node) for node in nodes]

```
  
---|---  
##  TreeRootRetriever #
Bases: `BaseRetriever`
Tree root retriever.
This class directly retrieves the answer from the root nodes.
Unlike GPTTreeIndexLeafQuery, this class assumes the graph already stores the answer (because it was constructed with a query_str), so it does not attempt to parse information down the graph in order to synthesize an answer.
Source code in `llama-index-core/llama_index/core/indices/tree/tree_root_retriever.py`

| ```
class TreeRootRetriever(BaseRetriever):
    """
    Tree root retriever.

    This class directly retrieves the answer from the root nodes.

    Unlike GPTTreeIndexLeafQuery, this class assumes the graph already stores
    the answer (because it was constructed with a query_str), so it does not
    attempt to parse information down the graph in order to synthesize an answer.
    """

    def __init__(
        self,
        index: TreeIndex,
        callback_manager: Optional[CallbackManager] = None,
        object_map: Optional[dict] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> None:
        self._index = index
        self._index_struct = index.index_struct
        self._docstore = index.docstore
        super().__init__(
            callback_manager=callback_manager, object_map=object_map, verbose=verbose
        )

    def _retrieve(
        self,
        query_bundle: QueryBundle,
    ) -> List[NodeWithScore]:
        """Get nodes for response."""
        logger.info(f"> Starting query: {query_bundle.query_str}")
        root_nodes = self._docstore.get_node_dict(self._index_struct.root_nodes)
        sorted_nodes = get_sorted_node_list(root_nodes)
        return [NodeWithScore(node=node) for node in sorted_nodes]

```
  
---|---
