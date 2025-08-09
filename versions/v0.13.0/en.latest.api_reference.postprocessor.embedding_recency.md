# Embedding recency
Node PostProcessor module.
##  EmbeddingRecencyPostprocessor #
Bases: `BaseNodePostprocessor`
Embedding Recency post-processor.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`embed_model` |  `BaseEmbedding` |  |  `<dynamic>`  
`date_key` |  `str` |  |  `'date'`  
`similarity_cutoff` |  `float` |  |  `0.7`  
`query_embedding_tmpl` |  `str` |  |  `'The current document is provided.\n----------------\n{context_str}\n----------------\nGiven the document, we wish to find documents that contain \nsimilar context. Note that these documents are older than the current document, meaning that certain details may be changed. \nHowever, the high-level context should be similar.\n'`  
Source code in `llama-index-core/llama_index/core/postprocessor/node_recency.py`

| ```
class EmbeddingRecencyPostprocessor(BaseNodePostprocessor):
    """Embedding Recency post-processor."""

    embed_model: SerializeAsAny[BaseEmbedding] = Field(
        default_factory=lambda: Settings.embed_model
    )
    date_key: str = "date"
    similarity_cutoff: float = Field(default=0.7)
    query_embedding_tmpl: str = Field(default=DEFAULT_QUERY_EMBEDDING_TMPL)

    @classmethod
    def class_name(cls) -> str:
        return "EmbeddingRecencyPostprocessor"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for this function. Please install it with `pip install pandas`."
            )

        if query_bundle is None:
            raise ValueError("Missing query bundle in extra info.")

        # sort nodes by date
        node_dates = pd.to_datetime(
            [node.node.metadata[self.date_key] for node in nodes]
        )
        sorted_node_idxs = np.flip(node_dates.argsort())
        sorted_nodes: List[NodeWithScore] = [nodes[idx] for idx in sorted_node_idxs]

        # get embeddings for each node
        texts = [node.get_content(metadata_mode=MetadataMode.EMBED) for node in nodes]
        text_embeddings = self.embed_model.get_text_embedding_batch(texts=texts)

        node_ids_to_skip: Set[str] = set()
        for idx, node in enumerate(sorted_nodes):
            if node.node.node_id in node_ids_to_skip:
                continue
            # get query embedding for the "query" node
            # NOTE: not the same as the text embedding because
            # we want to optimize for retrieval results

            query_text = self.query_embedding_tmpl.format(
                context_str=node.node.get_content(metadata_mode=MetadataMode.EMBED),
            )
            query_embedding = self.embed_model.get_query_embedding(query_text)

            for idx2 in range(idx + 1, len(sorted_nodes)):
                if sorted_nodes[idx2].node.node_id in node_ids_to_skip:
                    continue
                node2 = sorted_nodes[idx2]
                if (
                    np.dot(query_embedding, text_embeddings[idx2])
                    > self.similarity_cutoff
                ):
                    node_ids_to_skip.add(node2.node.node_id)

        return [
            node for node in sorted_nodes if node.node.node_id not in node_ids_to_skip
        ]

```
  
---|---
