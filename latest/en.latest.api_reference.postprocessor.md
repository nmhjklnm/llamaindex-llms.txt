# Index
##  BaseNodePostprocessor #
Bases: `BaseComponent`, `DispatcherSpanMixin`, `ABC`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`callback_manager` |  `CallbackManager` |  Callback manager that handles callbacks for events within LlamaIndex. The callback manager provides a way to call handlers on event starts/ends. Additionally, the callback manager traces the current stack of events. It does this by using a few key attributes. - trace_stack - The current stack of events that have not ended yet. When an event ends, it's removed from the stack. Since this is a contextvar, it is unique to each thread/task. - trace_map - A mapping of event ids to their children events. On the start of events, the bottom of the trace stack is used as the current parent event for the trace map. - trace_id - A simple name for the current trace, usually denoting the entrypoint (query, index_construction, insert, etc.) Args: handlers (List[BaseCallbackHandler]): list of handlers to use. Usage: with callback_manager.event(CBEventType.QUERY) as event: event.on_start(payload={key, val}) ... event.on_end(payload={key, val}) |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/postprocessor/types.py`

| ```
class BaseNodePostprocessor(BaseComponent, DispatcherSpanMixin, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    callback_manager: CallbackManager = Field(
        default_factory=CallbackManager, exclude=True
    )

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        # set by default since most postprocessors don't require prompts
        return {}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt modules."""
        return {}

    # implement class_name so users don't have to worry about it when extending
    @classmethod
    def class_name(cls) -> str:
        return "BaseNodePostprocessor"

    def postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
        query_str: Optional[str] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""
        if query_str is not None and query_bundle is not None:
            raise ValueError("Cannot specify both query_str and query_bundle")
        elif query_str is not None:
            query_bundle = QueryBundle(query_str)
        else:
            pass
        return self._postprocess_nodes(nodes, query_bundle)

    @abstractmethod
    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes."""

    async def apostprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
        query_str: Optional[str] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes (async)."""
        if query_str is not None and query_bundle is not None:
            raise ValueError("Cannot specify both query_str and query_bundle")
        elif query_str is not None:
            query_bundle = QueryBundle(query_str)
        else:
            pass
        return await self._apostprocess_nodes(nodes, query_bundle)

    async def _apostprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        """Postprocess nodes (async)."""
        return await asyncio.to_thread(self._postprocess_nodes, nodes, query_bundle)

```
  
---|---  
###  postprocess_nodes #
```
postprocess_nodes(nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle] = None, query_str: Optional[str] = None) -> List[NodeWithScore]

```

Postprocess nodes.
Source code in `llama-index-core/llama_index/core/postprocessor/types.py`

| ```
def postprocess_nodes(
    self,
    nodes: List[NodeWithScore],
    query_bundle: Optional[QueryBundle] = None,
    query_str: Optional[str] = None,
) -> List[NodeWithScore]:
    """Postprocess nodes."""
    if query_str is not None and query_bundle is not None:
        raise ValueError("Cannot specify both query_str and query_bundle")
    elif query_str is not None:
        query_bundle = QueryBundle(query_str)
    else:
        pass
    return self._postprocess_nodes(nodes, query_bundle)

```
  
---|---  
###  apostprocess_nodes `async` #
```
apostprocess_nodes(nodes: List[NodeWithScore], query_bundle: Optional[QueryBundle] = None, query_str: Optional[str] = None) -> List[NodeWithScore]

```

Postprocess nodes (async).
Source code in `llama-index-core/llama_index/core/postprocessor/types.py`

| ```
async def apostprocess_nodes(
    self,
    nodes: List[NodeWithScore],
    query_bundle: Optional[QueryBundle] = None,
    query_str: Optional[str] = None,
) -> List[NodeWithScore]:
    """Postprocess nodes (async)."""
    if query_str is not None and query_bundle is not None:
        raise ValueError("Cannot specify both query_str and query_bundle")
    elif query_str is not None:
        query_bundle = QueryBundle(query_str)
    else:
        pass
    return await self._apostprocess_nodes(nodes, query_bundle)

```
  
---|---
