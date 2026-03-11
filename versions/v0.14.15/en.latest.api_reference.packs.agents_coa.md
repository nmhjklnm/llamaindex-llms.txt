# Agents coa
##  CoAAgentPack #
Bases: `BaseLlamaPack`
Chain-of-abstraction Agent Pack.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`tools` |  `List[BaseTool]` |  List of tools to use. |  _required_  
`llm` |  `Optional[LLM]` |  LLM to use. Defaults to gpt-4. |  `None`  
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/base.py`

| ```
class CoAAgentPack(BaseLlamaPack):
    """
    Chain-of-abstraction Agent Pack.

    Args:
        tools (List[BaseTool]): List of tools to use.
        llm (Optional[LLM]): LLM to use. Defaults to gpt-4.

    """

    def __init__(
        self,
        tools: List[BaseTool],
        llm: Optional[LLM] = None,
        callback_manager: Optional[CallbackManager] = None,
        agent_worker_kwargs: Optional[Dict[str, Any]] = None,
        agent_runner_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Init params."""
        self.llm = llm or Settings.llm
        self.callback_manager = callback_manager or self.llm.callback_manager
        self.agent_worker = CoAAgentWorker.from_tools(
            tools=tools,
            llm=llm,
            verbose=True,
            callback_manager=self.callback_manager,
            **(agent_worker_kwargs or {}),
        )
        self.agent = AgentRunner(
            self.agent_worker,
            callback_manager=self.callback_manager,
            **(agent_runner_kwargs or {}),
        )

    def get_modules(self) -> Dict[str, Any]:
        """Get modules."""
        return {
            "llm": self.llm,
            "callback_manager": self.callback_manager,
            "agent_worker": self.agent_worker,
            "agent": self.agent,
        }

    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the pipeline."""
        return self.agent.chat(*args, **kwargs)

```
  
---|---  
###  get_modules #
```
get_modules() -> Dict[str, Any]

```

Get modules.
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/base.py`

| ```
def get_modules(self) -> Dict[str, Any]:
    """Get modules."""
    return {
        "llm": self.llm,
        "callback_manager": self.callback_manager,
        "agent_worker": self.agent_worker,
        "agent": self.agent,
    }

```
  
---|---  
###  run #
```
run(*args: Any, **kwargs: Any) -> Any

```

Run the pipeline.
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/base.py`

| ```
def run(self, *args: Any, **kwargs: Any) -> Any:
    """Run the pipeline."""
    return self.agent.chat(*args, **kwargs)

```
  
---|---  
##  CoAAgentWorker #
Bases: `BaseAgentWorker`
Chain-of-abstraction Agent Worker.
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
class CoAAgentWorker(BaseAgentWorker):
    """Chain-of-abstraction Agent Worker."""

    def __init__(
        self,
        llm: LLM,
        reasoning_prompt_template: str,
        refine_reasoning_prompt_template: str,
        output_parser: BaseOutputParser,
        tools: Optional[Sequence[BaseTool]] = None,
        tool_retriever: Optional[ObjectRetriever[BaseTool]] = None,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = False,
    ) -> None:
        self.llm = llm
        self.callback_manager = callback_manager or llm.callback_manager

        if tools is None and tool_retriever is None:
            raise ValueError("Either tools or tool_retriever must be provided.")
        self.tools = tools
        self.tool_retriever = tool_retriever

        self.reasoning_prompt_template = reasoning_prompt_template
        self.refine_reasoning_prompt_template = refine_reasoning_prompt_template
        self.output_parser = output_parser
        self.verbose = verbose

    @classmethod
    def from_tools(
        cls,
        tools: Optional[Sequence[BaseTool]] = None,
        tool_retriever: Optional[ObjectRetriever[BaseTool]] = None,
        llm: Optional[LLM] = None,
        reasoning_prompt_template: Optional[str] = None,
        refine_reasoning_prompt_template: Optional[str] = None,
        output_parser: Optional[BaseOutputParser] = None,
        callback_manager: Optional[CallbackManager] = None,
        verbose: bool = False,
        **kwargs: Any,
    ) -> "CoAAgentWorker":
        """
        Convenience constructor method from set of BaseTools (Optional).

        Returns:
            LLMCompilerAgentWorker: the LLMCompilerAgentWorker instance

        """
        llm = llm or Settings.llm
        if callback_manager is not None:
            llm.callback_manager = callback_manager

        reasoning_prompt_template = (
            reasoning_prompt_template or REASONING_PROMPT_TEMPALTE
        )
        refine_reasoning_prompt_template = (
            refine_reasoning_prompt_template or REFINE_REASONING_PROMPT_TEMPALTE
        )
        output_parser = output_parser or ChainOfAbstractionParser(verbose=verbose)

        return cls(
            llm,
            reasoning_prompt_template,
            refine_reasoning_prompt_template,
            output_parser,
            tools=tools,
            tool_retriever=tool_retriever,
            callback_manager=callback_manager,
            verbose=verbose,
        )

    def initialize_step(self, task: Task, **kwargs: Any) -> TaskStep:
        """Initialize step from task."""
        sources: List[ToolOutput] = []
        # temporary memory for new messages
        new_memory = ChatMemoryBuffer.from_defaults()

        # put current history in new memory
        messages = task.memory.get()
        for message in messages:
            new_memory.put(message)

        # initialize task state
        task_state = {
            "sources": sources,
            "new_memory": new_memory,
        }
        task.extra_state.update(task_state)

        return TaskStep(
            task_id=task.task_id,
            step_id=str(uuid.uuid4()),
            input=task.input,
            step_state={"prev_reasoning": ""},
        )

    def get_tools(self, query_str: str) -> List[AsyncBaseTool]:
        """Get tools."""
        if self.tool_retriever:
            tools = self.tool_retriever.retrieve(query_str)
        else:
            tools = self.tools

        return [adapt_to_async_tool(t) for t in tools]

    async def _arun_step(
        self,
        step: TaskStep,
        task: Task,
    ) -> TaskStepOutput:
        """Run step."""
        tools = self.get_tools(task.input)
        tools_by_name = {tool.metadata.name: tool for tool in tools}
        tools_strs = []
        for tool in tools:
            if isinstance(tool, FunctionTool):
                description = tool.metadata.description
                # remove function def, we will make our own
                if "def " in description:
                    description = "\n".join(description.split("\n")[1:])
            else:
                description = tool.metadata.description

            tool_str = json_schema_to_python(
                tool.metadata.fn_schema_str, tool.metadata.name, description=description
            )
            tools_strs.append(tool_str)

        prev_reasoning = step.step_state.get("prev_reasoning", "")

        # show available functions if first step
        if self.verbose and not prev_reasoning:
            print(f"==== Available Parsed Functions ====")
            for tool_str in tools_strs:
                print(tool_str)

        if not prev_reasoning:
            # get the reasoning prompt
            reasoning_prompt = self.reasoning_prompt_template.format(
                functions="\n".join(tools_strs), question=step.input
            )
        else:
            # get the refine reasoning prompt
            reasoning_prompt = self.refine_reasoning_prompt_template.format(
                question=step.input, prev_reasoning=prev_reasoning
            )

        messages = task.extra_state["new_memory"].get()
        reasoning_message = ChatMessage(role="user", content=reasoning_prompt)
        messages.append(reasoning_message)

        # run the reasoning prompt
        response = await self.llm.achat(messages)

        # print the chain of abstraction if first step
        if self.verbose and not prev_reasoning:
            print(f"==== Generated Chain of Abstraction ====")
            print(str(response.message.content))

        # parse the output, run functions
        parsed_response, tool_sources = await self.output_parser.aparse(
            response.message.content, tools_by_name
        )

        if len(tool_sources) == 0 or prev_reasoning:
            is_done = True
            new_steps = []

            # only add to memory when we are done
            task.extra_state["new_memory"].put(
                ChatMessage(role="user", content=task.input)
            )
            task.extra_state["new_memory"].put(
                ChatMessage(role="assistant", content=parsed_response)
            )
        else:
            is_done = False
            new_steps = [
                TaskStep(
                    task_id=task.task_id,
                    step_id=str(uuid.uuid4()),
                    input=task.input,
                    step_state={
                        "prev_reasoning": parsed_response,
                    },
                )
            ]

        agent_response = AgentChatResponse(
            response=parsed_response, sources=tool_sources
        )

        return TaskStepOutput(
            output=agent_response,
            task_step=step,
            is_last=is_done,
            next_steps=new_steps,
        )

    @trace_method("run_step")
    def run_step(self, step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput:
        """Run step."""
        return asyncio.run(self.arun_step(step=step, task=task, **kwargs))

    @trace_method("run_step")
    async def arun_step(
        self, step: TaskStep, task: Task, **kwargs: Any
    ) -> TaskStepOutput:
        """Run step (async)."""
        return await self._arun_step(step, task)

    @trace_method("run_step")
    def stream_step(self, step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput:
        """Run step (stream)."""
        # Streaming isn't really possible, because we need the full response to know if we are done
        raise NotImplementedError

    @trace_method("run_step")
    async def astream_step(
        self, step: TaskStep, task: Task, **kwargs: Any
    ) -> TaskStepOutput:
        """Run step (async stream)."""
        # Streaming isn't really possible, because we need the full response to know if we are done
        raise NotImplementedError

    def finalize_task(self, task: Task, **kwargs: Any) -> None:
        """Finalize task, after all the steps are completed."""
        # add new messages to memory
        task.memory.put_messages(task.extra_state["new_memory"].get_all())
        # reset new memory
        task.extra_state["new_memory"].reset()

```
  
---|---  
###  from_tools `classmethod` #
```
from_tools(tools: Optional[Sequence[BaseTool]] = None, tool_retriever: Optional[ObjectRetriever[BaseTool]] = None, llm: Optional[LLM] = None, reasoning_prompt_template: Optional[str] = None, refine_reasoning_prompt_template: Optional[str] = None, output_parser: Optional[BaseOutputParser] = None, callback_manager: Optional[CallbackManager] = None, verbose: bool = False, **kwargs: Any) -> CoAAgentWorker

```

Convenience constructor method from set of BaseTools (Optional).
Returns:
Name | Type | Description  
---|---|---  
`LLMCompilerAgentWorker` |  `CoAAgentWorker` |  the LLMCompilerAgentWorker instance  
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
@classmethod
def from_tools(
    cls,
    tools: Optional[Sequence[BaseTool]] = None,
    tool_retriever: Optional[ObjectRetriever[BaseTool]] = None,
    llm: Optional[LLM] = None,
    reasoning_prompt_template: Optional[str] = None,
    refine_reasoning_prompt_template: Optional[str] = None,
    output_parser: Optional[BaseOutputParser] = None,
    callback_manager: Optional[CallbackManager] = None,
    verbose: bool = False,
    **kwargs: Any,
) -> "CoAAgentWorker":
    """
    Convenience constructor method from set of BaseTools (Optional).

    Returns:
        LLMCompilerAgentWorker: the LLMCompilerAgentWorker instance

    """
    llm = llm or Settings.llm
    if callback_manager is not None:
        llm.callback_manager = callback_manager

    reasoning_prompt_template = (
        reasoning_prompt_template or REASONING_PROMPT_TEMPALTE
    )
    refine_reasoning_prompt_template = (
        refine_reasoning_prompt_template or REFINE_REASONING_PROMPT_TEMPALTE
    )
    output_parser = output_parser or ChainOfAbstractionParser(verbose=verbose)

    return cls(
        llm,
        reasoning_prompt_template,
        refine_reasoning_prompt_template,
        output_parser,
        tools=tools,
        tool_retriever=tool_retriever,
        callback_manager=callback_manager,
        verbose=verbose,
    )

```
  
---|---  
###  initialize_step #
```
initialize_step(task: Task, **kwargs: Any) -> TaskStep

```

Initialize step from task.
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
def initialize_step(self, task: Task, **kwargs: Any) -> TaskStep:
    """Initialize step from task."""
    sources: List[ToolOutput] = []
    # temporary memory for new messages
    new_memory = ChatMemoryBuffer.from_defaults()

    # put current history in new memory
    messages = task.memory.get()
    for message in messages:
        new_memory.put(message)

    # initialize task state
    task_state = {
        "sources": sources,
        "new_memory": new_memory,
    }
    task.extra_state.update(task_state)

    return TaskStep(
        task_id=task.task_id,
        step_id=str(uuid.uuid4()),
        input=task.input,
        step_state={"prev_reasoning": ""},
    )

```
  
---|---  
###  get_tools #
```
get_tools(query_str: str) -> List[AsyncBaseTool]

```

Get tools.
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
def get_tools(self, query_str: str) -> List[AsyncBaseTool]:
    """Get tools."""
    if self.tool_retriever:
        tools = self.tool_retriever.retrieve(query_str)
    else:
        tools = self.tools

    return [adapt_to_async_tool(t) for t in tools]

```
  
---|---  
###  run_step #
```
run_step(step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput

```

Run step.
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
@trace_method("run_step")
def run_step(self, step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput:
    """Run step."""
    return asyncio.run(self.arun_step(step=step, task=task, **kwargs))

```
  
---|---  
###  arun_step `async` #
```
arun_step(step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput

```

Run step (async).
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
@trace_method("run_step")
async def arun_step(
    self, step: TaskStep, task: Task, **kwargs: Any
) -> TaskStepOutput:
    """Run step (async)."""
    return await self._arun_step(step, task)

```
  
---|---  
###  stream_step #
```
stream_step(step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput

```

Run step (stream).
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
@trace_method("run_step")
def stream_step(self, step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput:
    """Run step (stream)."""
    # Streaming isn't really possible, because we need the full response to know if we are done
    raise NotImplementedError

```
  
---|---  
###  astream_step `async` #
```
astream_step(step: TaskStep, task: Task, **kwargs: Any) -> TaskStepOutput

```

Run step (async stream).
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
@trace_method("run_step")
async def astream_step(
    self, step: TaskStep, task: Task, **kwargs: Any
) -> TaskStepOutput:
    """Run step (async stream)."""
    # Streaming isn't really possible, because we need the full response to know if we are done
    raise NotImplementedError

```
  
---|---  
###  finalize_task #
```
finalize_task(task: Task, **kwargs: Any) -> None

```

Finalize task, after all the steps are completed.
Source code in `llama-index-packs/llama-index-packs-agents-coa/llama_index/packs/agents_coa/step.py`

| ```
def finalize_task(self, task: Task, **kwargs: Any) -> None:
    """Finalize task, after all the steps are completed."""
    # add new messages to memory
    task.memory.put_messages(task.extra_state["new_memory"].get_all())
    # reset new memory
    task.extra_state["new_memory"].reset()

```
  
---|---
