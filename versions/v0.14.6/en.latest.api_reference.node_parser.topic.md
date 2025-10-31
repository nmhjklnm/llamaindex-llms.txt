# Topic
##  TopicNodeParser #
Bases: `NodeParser`
Topic Based node parser.
Source code in `llama-index-integrations/node_parser/llama-index-node-parser-topic/llama_index/node_parser/topic/base.py`

| ```
class TopicNodeParser(NodeParser):
    """Topic Based node parser."""

    max_chunk_size: int = Field(
        default=1000,
        description="The maximum number of tokens in a chunk.",
    )

    window_size: int = Field(
        default=5,
        description="Paragraph sliding window size",
    )

    llm: LLM = Field(
        description="The LLM model to use for parsing.",
    )
    similarity_method: str = Field(
        default="llm",
        description="The method to use for determining if a new proposition belongs to the same topic. Choose 'llm' or 'embedding'.",
    )
    embed_model: SerializeAsAny[BaseEmbedding] = Field(
        description="The embedding model to use for determining similarity between propositions.",
    )
    similarity_threshold: float = Field(
        default=0.8,
        description="The threshold for determining similarity between propositions.",
    )
    tokenizer: Callable = Field(
        description="The tokenizer to use for tokenizing text.",
    )

    @classmethod
    def class_name(cls) -> str:
        return "TopicNodeParser"

    @classmethod
    def from_defaults(
        cls,
        callback_manager: Optional[CallbackManager] = None,
        id_func: Optional[Callable[[int, Document], str]] = None,
        tokenizer: Optional[Callable] = None,
        max_chunk_size: int = 1000,
        window_size: int = 5,
        llm: Optional[LLM] = None,
        embed_model: Optional[BaseEmbedding] = None,
        similarity_method: str = "llm",
        similarity_threshold: float = 0.8,
    ) -> "TopicNodeParser":
        """Initialize with parameters."""
        from llama_index.core import Settings

        callback_manager = callback_manager or CallbackManager([])
        id_func = id_func or default_id_func
        tokenizer = tokenizer or get_tokenizer()
        llm = llm or Settings.llm
        embed_model = embed_model or Settings.embed_model

        return cls(
            callback_manager=callback_manager,
            id_func=id_func,
            tokenizer=tokenizer,
            max_chunk_size=max_chunk_size,
            window_size=window_size,
            llm=llm,
            embed_model=embed_model,
            similarity_threshold=similarity_threshold,
            similarity_method=similarity_method,
        )

    def _parse_nodes(
        self,
        nodes: Sequence[BaseNode],
        show_progress: bool = False,
        **kwargs: Any,
    ) -> List[BaseNode]:
        """Parse document into nodes."""
        all_nodes: List[BaseNode] = []
        nodes_with_progress = get_tqdm_iterable(nodes, show_progress, "Parsing nodes")

        for node in nodes_with_progress:
            nodes = self.build_topic_based_nodes_from_documents([node])
            all_nodes.extend(nodes)

        return all_nodes

    def split_into_paragraphs(self, text: str) -> List[str]:
        """Split the document into paragraphs based on line breaks."""
        return re.split(r"\n\s*\n", text)

    def proposition_transfer(self, paragraph: str) -> List[str]:
        """
        Convert a paragraph into a list of self-sustaining statements using LLM.
        """
        messages = [
            ChatMessage(role="system", content=PROPOSITION_SYSTEM_PROMPT),
            ChatMessage(role="user", content=paragraph),
        ]

        response = str(self.llm.chat(messages))

        json_start = response.find("[")
        json_end = response.rfind("]") + 1
        if json_start != -1 and json_end != -1:
            json_content = response[json_start:json_end]
            # Parse the JSON response
            try:
                return json.loads(json_content)
            except json.JSONDecodeError:
                print(f"Failed to parse JSON: {json_content}")
                return []
        else:
            print(f"No valid JSON found in the response: {response}")
            return []

    def is_same_topic_llm(self, current_chunk: List[str], new_proposition: str) -> bool:
        """
        Use zero-shot classification with LLM to determine if the new proposition belongs to the same topic.
        """
        current_text = " ".join(current_chunk)
        messages = [
            ChatMessage(role="system", content=TOPIC_CLASSIFICATION_SYSTEM_PROMPT),
            ChatMessage(
                role="user",
                content=f"Text 1: {current_text}\n\nText 2: {new_proposition}",
            ),
        ]

        response = self.llm.chat(messages)

        return "same topic" in str(response).lower()

    def is_same_topic_embedding(
        self, current_chunk: List[str], new_proposition: str
    ) -> bool:
        """
        Use embedding-based similarity to determine if the new proposition belongs to the same topic.
        """
        current_text = " ".join(current_chunk)
        current_text_embedding = self.embed_model.get_text_embedding(current_text)
        new_proposition_embedding = self.embed_model.get_text_embedding(new_proposition)

        similarity_score = similarity(current_text_embedding, new_proposition_embedding)
        return similarity_score > self.similarity_threshold

    def semantic_chunking(self, paragraphs: List[str]) -> List[str]:
        """
        Perform semantic chunking on the given paragraphs.
        max_chunk_size: It is based on hard threshold of 1000 characters.
        As per paper the hard threshold that the longest chunk cannot excess the context length limitation of LLM.
        Here we are using 1000 tokens as the threshold.
        """
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_chunk_size: int = 0
        half_window = self.window_size // 2
        # Cache for storing propositions
        proposition_cache: Dict[int, List[str]] = {}

        for i in range(len(paragraphs)):
            # Define the window range
            start_idx = max(0, i - half_window)
            end_idx = min(len(paragraphs), i + half_window + 1)

            # Generate and cache propositions for paragraphs in the window
            window_propositions = []
            for j in range(start_idx, end_idx):
                if j not in proposition_cache:
                    proposition_cache[j] = self.proposition_transfer(paragraphs[j])
                window_propositions.extend(proposition_cache[j])

            for prop in window_propositions:
                if current_chunk:
                    if self.similarity_method == "llm":
                        is_same_topic = self.is_same_topic_llm(current_chunk, prop)
                    elif self.similarity_method == "embedding":
                        is_same_topic = self.is_same_topic_embedding(
                            current_chunk, prop
                        )
                    else:
                        raise ValueError(
                            "Invalid similarity method. Choose 'llm' or 'embedding'."
                        )
                else:
                    is_same_topic = True

                if not current_chunk or (
                    is_same_topic
                    and current_chunk_size + len(self.tokenizer(prop))
                    <= self.max_chunk_size
                ):
                    current_chunk.append(prop)
                    current_chunk_size += len(prop)
                else:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [prop]
                    current_chunk_size = len(self.tokenizer(prop))

            # If we've reached the max chunk size, start a new chunk
            if current_chunk_size >= self.max_chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_chunk_size = 0

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def build_topic_based_nodes_from_documents(
        self, documents: Sequence[Document]
    ) -> List[BaseNode]:
        """Build topic based nodes from documents."""
        all_nodes: List[BaseNode] = []
        for doc in documents:
            paragraphs = self.split_into_paragraphs(doc.text)
            chunks = self.semantic_chunking(paragraphs)
            nodes = build_nodes_from_splits(
                chunks,
                doc,
                id_func=self.id_func,
            )
            all_nodes.extend(nodes)

        return all_nodes

```
  
---|---  
###  from_defaults `classmethod` #
```
from_defaults(callback_manager: Optional[CallbackManager] = None, id_func: Optional[Callable[[int, Document], str]] = None, tokenizer: Optional[Callable] = None, max_chunk_size: int = 1000, window_size: int = 5, llm: Optional[LLM] = None, embed_model: Optional[BaseEmbedding] = None, similarity_method: str = 'llm', similarity_threshold: float = 0.8) -> TopicNodeParser

```

Initialize with parameters.
Source code in `llama-index-integrations/node_parser/llama-index-node-parser-topic/llama_index/node_parser/topic/base.py`

| ```
@classmethod
def from_defaults(
    cls,
    callback_manager: Optional[CallbackManager] = None,
    id_func: Optional[Callable[[int, Document], str]] = None,
    tokenizer: Optional[Callable] = None,
    max_chunk_size: int = 1000,
    window_size: int = 5,
    llm: Optional[LLM] = None,
    embed_model: Optional[BaseEmbedding] = None,
    similarity_method: str = "llm",
    similarity_threshold: float = 0.8,
) -> "TopicNodeParser":
    """Initialize with parameters."""
    from llama_index.core import Settings

    callback_manager = callback_manager or CallbackManager([])
    id_func = id_func or default_id_func
    tokenizer = tokenizer or get_tokenizer()
    llm = llm or Settings.llm
    embed_model = embed_model or Settings.embed_model

    return cls(
        callback_manager=callback_manager,
        id_func=id_func,
        tokenizer=tokenizer,
        max_chunk_size=max_chunk_size,
        window_size=window_size,
        llm=llm,
        embed_model=embed_model,
        similarity_threshold=similarity_threshold,
        similarity_method=similarity_method,
    )

```
  
---|---  
###  split_into_paragraphs #
```
split_into_paragraphs(text: str) -> List[str]

```

Split the document into paragraphs based on line breaks.
Source code in `llama-index-integrations/node_parser/llama-index-node-parser-topic/llama_index/node_parser/topic/base.py`

| ```
def split_into_paragraphs(self, text: str) -> List[str]:
    """Split the document into paragraphs based on line breaks."""
    return re.split(r"\n\s*\n", text)

```
  
---|---  
###  proposition_transfer #
```
proposition_transfer(paragraph: str) -> List[str]

```

Convert a paragraph into a list of self-sustaining statements using LLM.
Source code in `llama-index-integrations/node_parser/llama-index-node-parser-topic/llama_index/node_parser/topic/base.py`

| ```
def proposition_transfer(self, paragraph: str) -> List[str]:
    """
    Convert a paragraph into a list of self-sustaining statements using LLM.
    """
    messages = [
        ChatMessage(role="system", content=PROPOSITION_SYSTEM_PROMPT),
        ChatMessage(role="user", content=paragraph),
    ]

    response = str(self.llm.chat(messages))

    json_start = response.find("[")
    json_end = response.rfind("]") + 1
    if json_start != -1 and json_end != -1:
        json_content = response[json_start:json_end]
        # Parse the JSON response
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {json_content}")
            return []
    else:
        print(f"No valid JSON found in the response: {response}")
        return []

```
  
---|---  
###  is_same_topic_llm #
```
is_same_topic_llm(current_chunk: List[str], new_proposition: str) -> bool

```

Use zero-shot classification with LLM to determine if the new proposition belongs to the same topic.
Source code in `llama-index-integrations/node_parser/llama-index-node-parser-topic/llama_index/node_parser/topic/base.py`

| ```
def is_same_topic_llm(self, current_chunk: List[str], new_proposition: str) -> bool:
    """
    Use zero-shot classification with LLM to determine if the new proposition belongs to the same topic.
    """
    current_text = " ".join(current_chunk)
    messages = [
        ChatMessage(role="system", content=TOPIC_CLASSIFICATION_SYSTEM_PROMPT),
        ChatMessage(
            role="user",
            content=f"Text 1: {current_text}\n\nText 2: {new_proposition}",
        ),
    ]

    response = self.llm.chat(messages)

    return "same topic" in str(response).lower()

```
  
---|---  
###  is_same_topic_embedding #
```
is_same_topic_embedding(current_chunk: List[str], new_proposition: str) -> bool

```

Use embedding-based similarity to determine if the new proposition belongs to the same topic.
Source code in `llama-index-integrations/node_parser/llama-index-node-parser-topic/llama_index/node_parser/topic/base.py`

| ```
def is_same_topic_embedding(
    self, current_chunk: List[str], new_proposition: str
) -> bool:
    """
    Use embedding-based similarity to determine if the new proposition belongs to the same topic.
    """
    current_text = " ".join(current_chunk)
    current_text_embedding = self.embed_model.get_text_embedding(current_text)
    new_proposition_embedding = self.embed_model.get_text_embedding(new_proposition)

    similarity_score = similarity(current_text_embedding, new_proposition_embedding)
    return similarity_score > self.similarity_threshold

```
  
---|---  
###  semantic_chunking #
```
semantic_chunking(paragraphs: List[str]) -> List[str]

```

Perform semantic chunking on the given paragraphs. max_chunk_size: It is based on hard threshold of 1000 characters. As per paper the hard threshold that the longest chunk cannot excess the context length limitation of LLM. Here we are using 1000 tokens as the threshold.
Source code in `llama-index-integrations/node_parser/llama-index-node-parser-topic/llama_index/node_parser/topic/base.py`

| ```
def semantic_chunking(self, paragraphs: List[str]) -> List[str]:
    """
    Perform semantic chunking on the given paragraphs.
    max_chunk_size: It is based on hard threshold of 1000 characters.
    As per paper the hard threshold that the longest chunk cannot excess the context length limitation of LLM.
    Here we are using 1000 tokens as the threshold.
    """
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_chunk_size: int = 0
    half_window = self.window_size // 2
    # Cache for storing propositions
    proposition_cache: Dict[int, List[str]] = {}

    for i in range(len(paragraphs)):
        # Define the window range
        start_idx = max(0, i - half_window)
        end_idx = min(len(paragraphs), i + half_window + 1)

        # Generate and cache propositions for paragraphs in the window
        window_propositions = []
        for j in range(start_idx, end_idx):
            if j not in proposition_cache:
                proposition_cache[j] = self.proposition_transfer(paragraphs[j])
            window_propositions.extend(proposition_cache[j])

        for prop in window_propositions:
            if current_chunk:
                if self.similarity_method == "llm":
                    is_same_topic = self.is_same_topic_llm(current_chunk, prop)
                elif self.similarity_method == "embedding":
                    is_same_topic = self.is_same_topic_embedding(
                        current_chunk, prop
                    )
                else:
                    raise ValueError(
                        "Invalid similarity method. Choose 'llm' or 'embedding'."
                    )
            else:
                is_same_topic = True

            if not current_chunk or (
                is_same_topic
                and current_chunk_size + len(self.tokenizer(prop))
                <= self.max_chunk_size
            ):
                current_chunk.append(prop)
                current_chunk_size += len(prop)
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [prop]
                current_chunk_size = len(self.tokenizer(prop))

        # If we've reached the max chunk size, start a new chunk
        if current_chunk_size >= self.max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_chunk_size = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

```
  
---|---  
###  build_topic_based_nodes_from_documents #
```
build_topic_based_nodes_from_documents(documents: Sequence[Document]) -> List[BaseNode]

```

Build topic based nodes from documents.
Source code in `llama-index-integrations/node_parser/llama-index-node-parser-topic/llama_index/node_parser/topic/base.py`

| ```
def build_topic_based_nodes_from_documents(
    self, documents: Sequence[Document]
) -> List[BaseNode]:
    """Build topic based nodes from documents."""
    all_nodes: List[BaseNode] = []
    for doc in documents:
        paragraphs = self.split_into_paragraphs(doc.text)
        chunks = self.semantic_chunking(paragraphs)
        nodes = build_nodes_from_splits(
            chunks,
            doc,
            id_func=self.id_func,
        )
        all_nodes.extend(nodes)

    return all_nodes

```
  
---|---
