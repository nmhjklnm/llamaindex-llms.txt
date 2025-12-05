# Span handlers
##  BaseSpanHandler #
Bases: `BaseModel`, `Generic[T]`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`completed_spans` |  `List[TypeVar]` |  List of completed spans. |  `<dynamic>`  
`dropped_spans` |  `List[TypeVar]` |  List of completed spans. |  `<dynamic>`  
`current_span_ids` |  `Dict[Any, Optional[str]]` |  Id of current spans in a given thread. |  `{}`  
Source code in `llama_index_instrumentation/span_handlers/base.py`

| ```
class BaseSpanHandler(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    open_spans: Dict[str, T] = Field(
        default_factory=dict, description="Dictionary of open spans."
    )
    completed_spans: List[T] = Field(
        default_factory=list, description="List of completed spans."
    )
    dropped_spans: List[T] = Field(
        default_factory=list, description="List of completed spans."
    )
    current_span_ids: Dict[Any, Optional[str]] = Field(
        default={}, description="Id of current spans in a given thread."
    )
    _lock: Optional[threading.Lock] = PrivateAttr()

    def __init__(
        self,
        open_spans: Dict[str, T] = {},
        completed_spans: List[T] = [],
        dropped_spans: List[T] = [],
        current_span_ids: Dict[Any, str] = {},
    ):
        super().__init__(
            open_spans=open_spans,
            completed_spans=completed_spans,
            dropped_spans=dropped_spans,
            current_span_ids=current_span_ids,
        )
        self._lock = None

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "BaseSpanHandler"

    @property
    def lock(self) -> threading.Lock:
        if self._lock is None:
            self._lock = threading.Lock()
        return self._lock

    def span_enter(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        parent_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """Logic for entering a span."""
        if id_ in self.open_spans:
            pass  # should probably raise an error here
        else:
            span = self.new_span(
                id_=id_,
                bound_args=bound_args,
                instance=instance,
                parent_span_id=parent_id,
                tags=tags,
            )
            if span:
                with self.lock:
                    self.open_spans[id_] = span

    def span_exit(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        result: Optional[Any] = None,
        **kwargs: Any,
    ) -> None:
        """Logic for exiting a span."""
        span = self.prepare_to_exit_span(
            id_=id_, bound_args=bound_args, instance=instance, result=result
        )
        if span:
            with self.lock:
                del self.open_spans[id_]

    def span_drop(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        err: Optional[BaseException] = None,
        **kwargs: Any,
    ) -> None:
        """Logic for dropping a span i.e. early exit."""
        span = self.prepare_to_drop_span(
            id_=id_, bound_args=bound_args, instance=instance, err=err
        )
        if span:
            with self.lock:
                del self.open_spans[id_]

    @abstractmethod
    def new_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Optional[T]:
        """
        Create a span.

        Subclasses of BaseSpanHandler should create the respective span type T
        and return it. Only NullSpanHandler should return a None here.
        """
        ...

    @abstractmethod
    def prepare_to_exit_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        result: Optional[Any] = None,
        **kwargs: Any,
    ) -> Optional[T]:
        """
        Logic for preparing to exit a span.

        Subclasses of BaseSpanHandler should return back the specific span T
        that is to be exited. If None is returned, then the span won't actually
        be exited.
        """
        ...

    @abstractmethod
    def prepare_to_drop_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        err: Optional[BaseException] = None,
        **kwargs: Any,
    ) -> Optional[T]:
        """
        Logic for preparing to drop a span.

        Subclasses of BaseSpanHandler should return back the specific span T
        that is to be dropped. If None is returned, then the span won't actually
        be dropped.
        """
        ...

```
  
---|---  
###  class_name `classmethod` #
```
class_name() -> str

```

Class name.
Source code in `llama_index_instrumentation/span_handlers/base.py`

| ```
@classmethod
def class_name(cls) -> str:
    """Class name."""
    return "BaseSpanHandler"

```
  
---|---  
###  span_enter #
```
span_enter(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, parent_id: Optional[str] = None, tags: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None

```

Logic for entering a span.
Source code in `llama_index_instrumentation/span_handlers/base.py`

| ```
def span_enter(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    parent_id: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> None:
    """Logic for entering a span."""
    if id_ in self.open_spans:
        pass  # should probably raise an error here
    else:
        span = self.new_span(
            id_=id_,
            bound_args=bound_args,
            instance=instance,
            parent_span_id=parent_id,
            tags=tags,
        )
        if span:
            with self.lock:
                self.open_spans[id_] = span

```
  
---|---  
###  span_exit #
```
span_exit(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, result: Optional[Any] = None, **kwargs: Any) -> None

```

Logic for exiting a span.
Source code in `llama_index_instrumentation/span_handlers/base.py`

| ```
def span_exit(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    result: Optional[Any] = None,
    **kwargs: Any,
) -> None:
    """Logic for exiting a span."""
    span = self.prepare_to_exit_span(
        id_=id_, bound_args=bound_args, instance=instance, result=result
    )
    if span:
        with self.lock:
            del self.open_spans[id_]

```
  
---|---  
###  span_drop #
```
span_drop(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, err: Optional[BaseException] = None, **kwargs: Any) -> None

```

Logic for dropping a span i.e. early exit.
Source code in `llama_index_instrumentation/span_handlers/base.py`

| ```
def span_drop(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    err: Optional[BaseException] = None,
    **kwargs: Any,
) -> None:
    """Logic for dropping a span i.e. early exit."""
    span = self.prepare_to_drop_span(
        id_=id_, bound_args=bound_args, instance=instance, err=err
    )
    if span:
        with self.lock:
            del self.open_spans[id_]

```
  
---|---  
###  new_span `abstractmethod` #
```
new_span(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, parent_span_id: Optional[str] = None, tags: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Optional[T]

```

Create a span.
Subclasses of BaseSpanHandler should create the respective span type T and return it. Only NullSpanHandler should return a None here.
Source code in `llama_index_instrumentation/span_handlers/base.py`

| ```
@abstractmethod
def new_span(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    parent_span_id: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Optional[T]:
    """
    Create a span.

    Subclasses of BaseSpanHandler should create the respective span type T
    and return it. Only NullSpanHandler should return a None here.
    """
    ...

```
  
---|---  
###  prepare_to_exit_span `abstractmethod` #
```
prepare_to_exit_span(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, result: Optional[Any] = None, **kwargs: Any) -> Optional[T]

```

Logic for preparing to exit a span.
Subclasses of BaseSpanHandler should return back the specific span T that is to be exited. If None is returned, then the span won't actually be exited.
Source code in `llama_index_instrumentation/span_handlers/base.py`

| ```
@abstractmethod
def prepare_to_exit_span(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    result: Optional[Any] = None,
    **kwargs: Any,
) -> Optional[T]:
    """
    Logic for preparing to exit a span.

    Subclasses of BaseSpanHandler should return back the specific span T
    that is to be exited. If None is returned, then the span won't actually
    be exited.
    """
    ...

```
  
---|---  
###  prepare_to_drop_span `abstractmethod` #
```
prepare_to_drop_span(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, err: Optional[BaseException] = None, **kwargs: Any) -> Optional[T]

```

Logic for preparing to drop a span.
Subclasses of BaseSpanHandler should return back the specific span T that is to be dropped. If None is returned, then the span won't actually be dropped.
Source code in `llama_index_instrumentation/span_handlers/base.py`

| ```
@abstractmethod
def prepare_to_drop_span(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    err: Optional[BaseException] = None,
    **kwargs: Any,
) -> Optional[T]:
    """
    Logic for preparing to drop a span.

    Subclasses of BaseSpanHandler should return back the specific span T
    that is to be dropped. If None is returned, then the span won't actually
    be dropped.
    """
    ...

```
  
---|---  
##  SimpleSpanHandler #
Bases: `BaseSpanHandler[SimpleSpan]`
Span Handler that manages SimpleSpan's.
Source code in `llama_index_instrumentation/span_handlers/simple.py`

| ```
class SimpleSpanHandler(BaseSpanHandler[SimpleSpan]):
    """Span Handler that manages SimpleSpan's."""

    def class_name(cls) -> str:
        """Class name."""
        return "SimpleSpanHandler"

    def new_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> SimpleSpan:
        """Create a span."""
        return SimpleSpan(id_=id_, parent_id=parent_span_id, tags=tags or {})

    def prepare_to_exit_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        result: Optional[Any] = None,
        **kwargs: Any,
    ) -> SimpleSpan:
        """Logic for preparing to drop a span."""
        span = self.open_spans[id_]
        span = cast(SimpleSpan, span)
        span.end_time = datetime.now()
        span.duration = (span.end_time - span.start_time).total_seconds()
        with self.lock:
            self.completed_spans += [span]
        return span

    def prepare_to_drop_span(
        self,
        id_: str,
        bound_args: inspect.BoundArguments,
        instance: Optional[Any] = None,
        err: Optional[BaseException] = None,
        **kwargs: Any,
    ) -> Optional[SimpleSpan]:
        """Logic for droppping a span."""
        if id_ in self.open_spans:
            with self.lock:
                span = self.open_spans[id_]
                span.metadata = {"error": str(err)}
                self.dropped_spans += [span]
            return span

        return None

    def _get_parents(self) -> List[SimpleSpan]:
        """Helper method to get all parent/root spans."""
        all_spans = self.completed_spans + self.dropped_spans
        return [s for s in all_spans if s.parent_id is None]

    def _build_tree_by_parent(
        self, parent: SimpleSpan, acc: List[SimpleSpan], spans: List[SimpleSpan]
    ) -> List[SimpleSpan]:
        """Builds the tree by parent root."""
        if not spans:
            return acc

        children = [s for s in spans if s.parent_id == parent.id_]
        if not children:
            return acc
        updated_spans = [s for s in spans if s not in children]

        children_trees = [
            self._build_tree_by_parent(
                parent=c, acc=[c], spans=[s for s in updated_spans if c != s]
            )
            for c in children
        ]

        return acc + reduce(lambda x, y: x + y, children_trees)

    def _get_trace_trees(self) -> List["Tree"]:
        """Method for getting trace trees."""
        try:
            from treelib import Tree
        except ImportError as e:
            raise ImportError(
                "`treelib` package is missing. Please install it by using "
                "`pip install treelib`."
            )

        all_spans = self.completed_spans + self.dropped_spans
        for s in all_spans:
            if s.parent_id is None:
                continue
            if not any(ns.id_ == s.parent_id for ns in all_spans):
                warnings.warn(f"Parent with id {s.parent_id} missing from spans")
                s.parent_id += "-MISSING"
                all_spans.append(SimpleSpan(id_=s.parent_id, parent_id=None))

        parents = self._get_parents()
        span_groups = []
        for p in parents:
            this_span_group = self._build_tree_by_parent(
                parent=p, acc=[p], spans=[s for s in all_spans if s != p]
            )
            sorted_span_group = sorted(this_span_group, key=lambda x: x.start_time)
            span_groups.append(sorted_span_group)

        trees = []
        tree = Tree()
        for grp in span_groups:
            for span in grp:
                if span.parent_id is None:
                    # complete old tree unless its empty (i.e., start of loop)
                    if tree.all_nodes():
                        trees.append(tree)
                        # start new tree
                        tree = Tree()

                tree.create_node(
                    tag=f"{span.id_} ({span.duration})",
                    identifier=span.id_,
                    parent=span.parent_id,
                    data=span.start_time,
                )

        trees.append(tree)
        return trees

    def print_trace_trees(self) -> None:
        """Method for viewing trace trees."""
        trees = self._get_trace_trees()
        for tree in trees:
            print(tree.show(stdout=False, sorting=True, key=lambda node: node.data))
            print("")

```
  
---|---  
###  class_name #
```
class_name() -> str

```

Class name.
Source code in `llama_index_instrumentation/span_handlers/simple.py`

| ```
def class_name(cls) -> str:
    """Class name."""
    return "SimpleSpanHandler"

```
  
---|---  
###  new_span #
```
new_span(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, parent_span_id: Optional[str] = None, tags: Optional[Dict[str, Any]] = None, **kwargs: Any) -> SimpleSpan

```

Create a span.
Source code in `llama_index_instrumentation/span_handlers/simple.py`

| ```
def new_span(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    parent_span_id: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> SimpleSpan:
    """Create a span."""
    return SimpleSpan(id_=id_, parent_id=parent_span_id, tags=tags or {})

```
  
---|---  
###  prepare_to_exit_span #
```
prepare_to_exit_span(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, result: Optional[Any] = None, **kwargs: Any) -> SimpleSpan

```

Logic for preparing to drop a span.
Source code in `llama_index_instrumentation/span_handlers/simple.py`

| ```
def prepare_to_exit_span(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    result: Optional[Any] = None,
    **kwargs: Any,
) -> SimpleSpan:
    """Logic for preparing to drop a span."""
    span = self.open_spans[id_]
    span = cast(SimpleSpan, span)
    span.end_time = datetime.now()
    span.duration = (span.end_time - span.start_time).total_seconds()
    with self.lock:
        self.completed_spans += [span]
    return span

```
  
---|---  
###  prepare_to_drop_span #
```
prepare_to_drop_span(id_: str, bound_args: BoundArguments, instance: Optional[Any] = None, err: Optional[BaseException] = None, **kwargs: Any) -> Optional[SimpleSpan]

```

Logic for droppping a span.
Source code in `llama_index_instrumentation/span_handlers/simple.py`

| ```
def prepare_to_drop_span(
    self,
    id_: str,
    bound_args: inspect.BoundArguments,
    instance: Optional[Any] = None,
    err: Optional[BaseException] = None,
    **kwargs: Any,
) -> Optional[SimpleSpan]:
    """Logic for droppping a span."""
    if id_ in self.open_spans:
        with self.lock:
            span = self.open_spans[id_]
            span.metadata = {"error": str(err)}
            self.dropped_spans += [span]
        return span

    return None

```
  
---|---  
###  print_trace_trees #
```
print_trace_trees() -> None

```

Method for viewing trace trees.
Source code in `llama_index_instrumentation/span_handlers/simple.py`

| ```
def print_trace_trees(self) -> None:
    """Method for viewing trace trees."""
    trees = self._get_trace_trees()
    for tree in trees:
        print(tree.show(stdout=False, sorting=True, key=lambda node: node.data))
        print("")

```
  
---|---
