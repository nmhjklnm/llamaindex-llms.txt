# Firestore
##  FirestoreVectorStore #
Bases: `BasePydanticVectorStore`
Firestore Vector Store.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-firestore/llama_index/vector_stores/firestore/base.py`

| ```
class FirestoreVectorStore(BasePydanticVectorStore):
    """Firestore Vector Store."""

    stores_text: bool = True
    flat_metadata: bool = True

    collection_name: str
    batch_size: Optional[int] = DEFAULT_BATCH_SIZE
    embedding_key: str = "embedding"
    text_key: str = "text"
    metadata_key: str = "metadata"
    distance_strategy: DistanceMeasure = DistanceMeasure.COSINE

    _client: Client

    def __init__(
        self,
        client: Optional[Client] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize params."""
        super().__init__(**kwargs)
        object.__setattr__(self, "_client", client_with_user_agent(client))

    @classmethod
    def class_name(cls) -> str:
        return "FirestoreVectorStore"

    @property
    def client(self) -> Any:
        return self._client

    def add(
        self,
        nodes: List[BaseNode],
    ) -> List[str]:
        """Add nodes to vector store."""
        ids = []
        entries = []
        for node in nodes:
            node_id = node.node_id
            metadata = node_to_metadata_dict(
                node,
                remove_text=not self.stores_text,
                flat_metadata=self.flat_metadata,
            )
            entry = {
                self.embedding_key: node.get_embedding(),
                self.metadata_key: metadata,
            }
            ids.append(node_id)
            entries.append(entry)
        self._upsert_batch(entries, ids)
        return ids

    def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
        """Delete nodes using with ref_doc_id."""
        docs = (
            self._client.collection(self.collection_name)
            .where("metadata.ref_doc_id", "==", ref_doc_id)
            .stream()
        )

        self._delete_batch([doc.id for doc in docs])

    def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
        """Query vector store."""
        if query.query_embedding is None:
            raise ValueError("Query embedding is required.")

        filters = _to_firestore_filter(query.filters) if query.filters else None

        results = self._similarity_search(
            query.query_embedding, query.similarity_top_k, filters=filters, **kwargs
        )

        top_k_ids = []
        top_k_nodes = []
        top_k_similarities = []

        LOGGER.debug(f"Found {len(results)} results.")

        for result in results:
            # Convert the Firestore document to dict
            result_dict = result.to_dict() or {}
            metadata = result_dict.get(self.metadata_key) or {}
            fir_vec: Optional[Vector] = result_dict.get(self.embedding_key)
            if fir_vec is None:
                raise ValueError(
                    "Embedding is missing in Firestore document.", result.id
                )
            embedding = list(fir_vec.to_map_value()["value"])

            # Convert metadata to node, and add text if available
            node = metadata_dict_to_node(metadata, text=result_dict.get(self.text_key))

            # Keep track of the top k ids and nodes
            top_k_ids.append(result.id)
            top_k_nodes.append(node)
            top_k_similarities.append(
                similarity(
                    query.query_embedding,
                    embedding,
                    self._distance_to_similarity_mode(self.distance_strategy),
                )
            )

        return VectorStoreQueryResult(
            nodes=top_k_nodes, ids=top_k_ids, similarities=top_k_similarities
        )

    def _distance_to_similarity_mode(self, distance: DistanceMeasure) -> SimilarityMode:
        """Convert Firestore's distance measure to similarity mode."""
        return {
            DistanceMeasure.COSINE: SimilarityMode.DEFAULT,
            DistanceMeasure.EUCLIDEAN: SimilarityMode.EUCLIDEAN,
            DistanceMeasure.DOT_PRODUCT: SimilarityMode.DOT_PRODUCT,
        }.get(distance, SimilarityMode.DEFAULT)

    def _delete_batch(self, ids: List[str]) -> None:
        """Delete batch of vectors from Firestore."""
        db_batch = self._client.batch()
        for batch in more_itertools.chunked(ids, DEFAULT_BATCH_SIZE):
            for doc_id in batch:
                doc = self._client.collection(self.collection_name).document(doc_id)
                db_batch.delete(doc)
            db_batch.commit()

    def _upsert_batch(self, entries: List[dict], ids: Optional[List[str]]) -> None:
        """Upsert batch of vectors to Firestore."""
        if ids and len(ids) != len(entries):
            raise ValueError("Length of ids and entries should be the same.")

        db_batch = self._client.batch()

        for batch in more_itertools.chunked(entries, DEFAULT_BATCH_SIZE):
            for i, entry in enumerate(batch):
                # Convert the embedding array to a Firestore Vector
                entry[self.embedding_key] = Vector(entry[self.embedding_key])
                doc = self._client.collection(self.collection_name).document(
                    ids[i] if ids else None
                )
                db_batch.set(doc, entry, merge=True)
            db_batch.commit()

    def _similarity_search(
        self,
        query: List[float],
        k: int,
        filters: Union[BaseFilter, BaseCompositeFilter, None] = None,
    ) -> List[DocumentSnapshot]:
        wfilters = None
        collection = self._client.collection(self.collection_name)

        if filters:
            wfilters = collection.where(filter=filters)

        results = (wfilters or collection).find_nearest(
            vector_field=self.embedding_key,
            query_vector=Vector(query),
            distance_measure=self.distance_strategy,
            limit=k,
        )

        return results.get()

```
  
---|---  
###  add #
```
add(nodes: List[BaseNode]) -> List[str]

```

Add nodes to vector store.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-firestore/llama_index/vector_stores/firestore/base.py`

| ```
def add(
    self,
    nodes: List[BaseNode],
) -> List[str]:
    """Add nodes to vector store."""
    ids = []
    entries = []
    for node in nodes:
        node_id = node.node_id
        metadata = node_to_metadata_dict(
            node,
            remove_text=not self.stores_text,
            flat_metadata=self.flat_metadata,
        )
        entry = {
            self.embedding_key: node.get_embedding(),
            self.metadata_key: metadata,
        }
        ids.append(node_id)
        entries.append(entry)
    self._upsert_batch(entries, ids)
    return ids

```
  
---|---  
###  delete #
```
delete(ref_doc_id: str, **delete_kwargs: Any) -> None

```

Delete nodes using with ref_doc_id.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-firestore/llama_index/vector_stores/firestore/base.py`

| ```
def delete(self, ref_doc_id: str, **delete_kwargs: Any) -> None:
    """Delete nodes using with ref_doc_id."""
    docs = (
        self._client.collection(self.collection_name)
        .where("metadata.ref_doc_id", "==", ref_doc_id)
        .stream()
    )

    self._delete_batch([doc.id for doc in docs])

```
  
---|---  
###  query #
```
query(query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult

```

Query vector store.
Source code in `llama-index-integrations/vector_stores/llama-index-vector-stores-firestore/llama_index/vector_stores/firestore/base.py`

| ```
def query(self, query: VectorStoreQuery, **kwargs: Any) -> VectorStoreQueryResult:
    """Query vector store."""
    if query.query_embedding is None:
        raise ValueError("Query embedding is required.")

    filters = _to_firestore_filter(query.filters) if query.filters else None

    results = self._similarity_search(
        query.query_embedding, query.similarity_top_k, filters=filters, **kwargs
    )

    top_k_ids = []
    top_k_nodes = []
    top_k_similarities = []

    LOGGER.debug(f"Found {len(results)} results.")

    for result in results:
        # Convert the Firestore document to dict
        result_dict = result.to_dict() or {}
        metadata = result_dict.get(self.metadata_key) or {}
        fir_vec: Optional[Vector] = result_dict.get(self.embedding_key)
        if fir_vec is None:
            raise ValueError(
                "Embedding is missing in Firestore document.", result.id
            )
        embedding = list(fir_vec.to_map_value()["value"])

        # Convert metadata to node, and add text if available
        node = metadata_dict_to_node(metadata, text=result_dict.get(self.text_key))

        # Keep track of the top k ids and nodes
        top_k_ids.append(result.id)
        top_k_nodes.append(node)
        top_k_similarities.append(
            similarity(
                query.query_embedding,
                embedding,
                self._distance_to_similarity_mode(self.distance_strategy),
            )
        )

    return VectorStoreQueryResult(
        nodes=top_k_nodes, ids=top_k_ids, similarities=top_k_similarities
    )

```
  
---|---
