# Cohere citation chat
##  CohereCitationChatEnginePack #
Bases: `BaseLlamaPack`
Source code in `llama-index-packs/llama-index-packs-cohere-citation-chat/llama_index/packs/cohere_citation_chat/base.py`

| ```
class CohereCitationChatEnginePack(BaseLlamaPack):
    def __init__(self, documents: List[Document], cohere_api_key: str = None) -> None:
        """Init params."""
        try:
            from llama_index.llms.cohere import Cohere
            from llama_index.embeddings.cohere import CohereEmbedding
        except ImportError:
            raise ImportError(
                "Please run `pip install llama-index-llms-cohere llama-index-embeddings-cohere` "
                "to use the Cohere."
            )
        self.api_key = cohere_api_key or os.environ.get("COHERE_API_KEY")
        self.llm = Cohere(
            "command",
            api_key=self.api_key,
            temperature=0.5,
            additional_kwargs={"prompt_truncation": "AUTO"},
        )

        self.embed_model_document = CohereEmbedding(
            api_key=self.api_key,
            model_name="embed-english-v3.0",
            input_type="search_document",
        )

        self.index = VectorStoreIndexWithCitationsChat.from_documents(
            documents, llm=self.llm, embed_model=self.embed_model_document
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "vector_index": self.index,
            "llm": self.llm,
        }

    def run(self, **kwargs: Any) -> BaseChatEngine:
        """Run the pipeline."""
        # Change Cohere embed input type. See the documentation here https://docs.cohere.com/reference/embed
        self.index.set_embed_model_input_type("search_query")
        return self.index.as_chat_engine(llm=self.llm)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-cohere-citation-chat/llama_index/packs/cohere_citation_chat/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "vector_index": self.index,
        "llm": self.llm,
    }

```
  
---|---  
###  run #
```
run(**kwargs: Any) -> BaseChatEngine

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-cohere-citation-chat/llama_index/packs/cohere_citation_chat/base.py`

| ```
def run(self, **kwargs: Any) -> BaseChatEngine:
    """Run the pipeline."""
    # Change Cohere embed input type. See the documentation here https://docs.cohere.com/reference/embed
    self.index.set_embed_model_input_type("search_query")
    return self.index.as_chat_engine(llm=self.llm)

```
  
---|---
