# Pathway
##  PathwayRetriever #
Bases: `BaseRetriever`
Pathway retriever.
Pathway is an open data processing framework. It allows you to easily develop data transformation pipelines that work with live data sources and changing data.
This is the client that implements Retriever API for PathwayVectorServer.
Source code in `llama-index-integrations/retrievers/llama-index-retrievers-pathway/llama_index/retrievers/pathway/base.py`

| ```
class PathwayRetriever(BaseRetriever):
    """
    Pathway retriever.

    Pathway is an open data processing framework.
    It allows you to easily develop data transformation pipelines
    that work with live data sources and changing data.

    This is the client that implements Retriever API for PathwayVectorServer.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        url: Optional[str] = None,
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        callback_manager: Optional[CallbackManager] = None,
    ) -> None:
        """Initializing the Pathway retriever client."""
        self.client = _VectorStoreClient(host, port, url)
        self.similarity_top_k = similarity_top_k
        super().__init__(callback_manager)

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """Retrieve."""
        rets = self.client(query=query_bundle.query_str, k=self.similarity_top_k)
        items = [
            NodeWithScore(
                node=TextNode(text=ret["text"], extra_info=ret["metadata"]),
                # Transform cosine distance into a similairty score
                # (higher is more similar)
                score=1 - ret["dist"],
            )
            for ret in rets
        ]
        return sorted(items, key=lambda x: x.score or 0.0, reverse=True)

```
  
---|---
