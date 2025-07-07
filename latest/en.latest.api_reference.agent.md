# Agent Classes#
##  AgentWorkflow #
Bases: `Workflow`, `PromptMixin`
A workflow for managing multiple agents with handoffs.
Source code in `llama-index-core/llama_index/core/agent/workflow/multi_agent_workflow.py`

| ```
class AgentWorkflow(Workflow, PromptMixin, metaclass=AgentWorkflowMeta):
    """A workflow for managing multiple agents with handoffs."""

    def __init__(
        self,
        agents: List[BaseWorkflowAgent],
        initial_state: Optional[Dict] = None,
        root_agent: Optional[str] = None,
        handoff_prompt: Optional[Union[str, BasePromptTemplate]] = None,
        handoff_output_prompt: Optional[Union[str, BasePromptTemplate]] = None,
        state_prompt: Optional[Union[str, BasePromptTemplate]] = None,
        timeout: Optional[float] = None,
        **workflow_kwargs: Any,
    ):
        super().__init__(timeout=timeout, **workflow_kwargs)
        if not agents:
            raise ValueError("At least one agent must be provided")

        # Raise an error if any agent has no name or no description
        if len(agents) > 1 and any(
            agent.name == DEFAULT_AGENT_NAME for agent in agents
        ):
            raise ValueError("All agents must have a name in a multi-agent workflow")

        if len(agents) > 1 and any(
            agent.description == DEFAULT_AGENT_DESCRIPTION for agent in agents
        ):
            raise ValueError(
                "All agents must have a description in a multi-agent workflow"
            )

        if any(agent.initial_state for agent in agents):
            raise ValueError(
                "Initial state is not supported per-agent in AgentWorkflow"
            )

        self.agents = {cfg.name: cfg for cfg in agents}
        if len(agents) == 1:
            root_agent = agents[0].name
        elif root_agent is None:
            raise ValueError("Exactly one root agent must be provided")
        else:
            root_agent = root_agent

        if root_agent not in self.agents:
            raise ValueError(f"Root agent {root_agent} not found in provided agents")

        self.root_agent = root_agent
        self.initial_state = initial_state or {}

        handoff_prompt = handoff_prompt or DEFAULT_HANDOFF_PROMPT
        if isinstance(handoff_prompt, str):
            handoff_prompt = PromptTemplate(handoff_prompt)
            if "{agent_info}" not in handoff_prompt.get_template():
                raise ValueError("Handoff prompt must contain {agent_info}")
        self.handoff_prompt = handoff_prompt

        handoff_output_prompt = handoff_output_prompt or DEFAULT_HANDOFF_OUTPUT_PROMPT
        if isinstance(handoff_output_prompt, str):
            handoff_output_prompt = PromptTemplate(handoff_output_prompt)
            if (
                "{to_agent}" not in handoff_output_prompt.get_template()
                or "{reason}" not in handoff_output_prompt.get_template()
            ):
                raise ValueError(
                    "Handoff output prompt must contain {to_agent} and {reason}"
                )
        self.handoff_output_prompt = handoff_output_prompt

        state_prompt = state_prompt or DEFAULT_STATE_PROMPT
        if isinstance(state_prompt, str):
            state_prompt = PromptTemplate(state_prompt)
            if (
                "{state}" not in state_prompt.get_template()
                or "{msg}" not in state_prompt.get_template()
            ):
                raise ValueError("State prompt must contain {state} and {msg}")
        self.state_prompt = state_prompt

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {
            "handoff_prompt": self.handoff_prompt,
            "handoff_output_prompt": self.handoff_output_prompt,
            "state_prompt": self.state_prompt,
        }

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {agent.name: agent for agent in self.agents.values()}

    def _update_prompts(self, prompts_dict: PromptDictType) -> None:
        """Update prompts."""
        if "handoff_prompt" in prompts_dict:
            self.handoff_prompt = prompts_dict["handoff_prompt"]
        if "handoff_output_prompt" in prompts_dict:
            self.handoff_output_prompt = prompts_dict["handoff_output_prompt"]
        if "state_prompt" in prompts_dict:
            self.state_prompt = prompts_dict["state_prompt"]

    def _ensure_tools_are_async(
        self, tools: Sequence[BaseTool]
    ) -> Sequence[AsyncBaseTool]:
        """Ensure all tools are async."""
        return [adapt_to_async_tool(tool) for tool in tools]

    def _get_handoff_tool(
        self, current_agent: BaseWorkflowAgent
    ) -> Optional[AsyncBaseTool]:
        """Creates a handoff tool for the given agent."""
        # Do not create a handoff tool if there is only one agent
        if len(self.agents) == 1:
            return None

        agent_info = {cfg.name: cfg.description for cfg in self.agents.values()}

        # Filter out agents that the current agent cannot handoff to
        configs_to_remove = []
        for name in agent_info:
            if name == current_agent.name:
                configs_to_remove.append(name)
            elif (
                current_agent.can_handoff_to is not None
                and name not in current_agent.can_handoff_to
            ):
                configs_to_remove.append(name)

        for name in configs_to_remove:
            agent_info.pop(name)

        if not agent_info:
            return None

        fn_tool_prompt = self.handoff_prompt.format(agent_info=str(agent_info))
        return FunctionTool.from_defaults(
            async_fn=handoff, description=fn_tool_prompt, return_direct=True
        )

    async def get_tools(
        self, agent_name: str, input_str: Optional[str] = None
    ) -> Sequence[AsyncBaseTool]:
        """Get tools for the given agent."""
        agent_tools = self.agents[agent_name].tools or []
        tools = [*agent_tools]
        retriever = self.agents[agent_name].tool_retriever
        if retriever is not None:
            retrieved_tools = await retriever.aretrieve(input_str or "")
            tools.extend(retrieved_tools)

        if (
            self.agents[agent_name].can_handoff_to
            or self.agents[agent_name].can_handoff_to is None
        ):
            handoff_tool = self._get_handoff_tool(self.agents[agent_name])
            if handoff_tool:
                tools.append(handoff_tool)

        return self._ensure_tools_are_async(cast(List[BaseTool], tools))

    async def _init_context(self, ctx: Context, ev: StartEvent) -> None:
        """Initialize the context once, if needed."""
        if not await ctx.store.get("memory", default=None):
            default_memory = ev.get("memory", default=None)
            default_memory = default_memory or ChatMemoryBuffer.from_defaults(
                llm=self.agents[self.root_agent].llm or Settings.llm
            )
            await ctx.store.set("memory", default_memory)
        if not await ctx.store.get("agents", default=None):
            await ctx.store.set("agents", list(self.agents.keys()))
        if not await ctx.store.get("can_handoff_to", default=None):
            await ctx.store.set(
                "can_handoff_to",
                {
                    agent: agent_cfg.can_handoff_to
                    for agent, agent_cfg in self.agents.items()
                },
            )
        if not await ctx.store.get("state", default=None):
            await ctx.store.set("state", self.initial_state)
        if not await ctx.store.get("current_agent_name", default=None):
            await ctx.store.set("current_agent_name", self.root_agent)
        if not await ctx.store.get("handoff_output_prompt", default=None):
            await ctx.store.set(
                "handoff_output_prompt", self.handoff_output_prompt.get_template()
            )
        if not await ctx.get("max_iterations", default=None):
            max_iterations = (
                ev.get("max_iterations", default=None) or DEFAULT_MAX_ITERATIONS
            )
            await ctx.set("max_iterations", max_iterations)

        # Reset the number of iterations
        await ctx.set("num_iterations", 0)

        # always set to false initially
        await ctx.store.set("formatted_input_with_state", False)

    async def _call_tool(
        self,
        ctx: Context,
        tool: AsyncBaseTool,
        tool_input: dict,
    ) -> ToolOutput:
        """Call the given tool with the given input."""
        try:
            if (
                isinstance(tool, FunctionTool)
                and tool.requires_context
                and tool.ctx_param_name is not None
            ):
                new_tool_input = {**tool_input}
                new_tool_input[tool.ctx_param_name] = ctx
                tool_output = await tool.acall(**new_tool_input)
            else:
                tool_output = await tool.acall(**tool_input)
        except Exception as e:
            tool_output = ToolOutput(
                content=str(e),
                tool_name=tool.metadata.get_name(),
                raw_input=tool_input,
                raw_output=str(e),
                is_error=True,
            )

        return tool_output

    @step
    async def init_run(self, ctx: Context, ev: AgentWorkflowStartEvent) -> AgentInput:
        """Sets up the workflow and validates inputs."""
        await self._init_context(ctx, ev)

        user_msg: Optional[Union[str, ChatMessage]] = ev.get("user_msg")
        chat_history: Optional[List[ChatMessage]] = ev.get("chat_history", [])

        # Convert string user_msg to ChatMessage
        if isinstance(user_msg, str):
            user_msg = ChatMessage(role="user", content=user_msg)

        # Add messages to memory
        memory: BaseMemory = await ctx.store.get("memory")

        # First set chat history if it exists
        if chat_history:
            await memory.aset(chat_history)

        # Then add user message if it exists
        if user_msg:
            await memory.aput(user_msg)
            content_str = "\n".join(
                [
                    block.text
                    for block in user_msg.blocks
                    if isinstance(block, TextBlock)
                ]
            )
            await ctx.store.set("user_msg_str", content_str)
        elif chat_history:
            # If no user message, use the last message from chat history as user_msg_str
            content_str = "\n".join(
                [
                    block.text
                    for block in chat_history[-1].blocks
                    if isinstance(block, TextBlock)
                ]
            )
            await ctx.store.set("user_msg_str", content_str)
        else:
            raise ValueError("Must provide either user_msg or chat_history")

        # Get all messages from memory
        input_messages = await memory.aget()

        # send to the current agent
        current_agent_name: str = await ctx.store.get("current_agent_name")
        return AgentInput(input=input_messages, current_agent_name=current_agent_name)

    @step
    async def setup_agent(self, ctx: Context, ev: AgentInput) -> AgentSetup:
        """Main agent handling logic."""
        current_agent_name = ev.current_agent_name
        agent = self.agents[current_agent_name]
        llm_input = [*ev.input]

        if agent.system_prompt:
            llm_input = [
                ChatMessage(role="system", content=agent.system_prompt),
                *llm_input,
            ]

        state = await ctx.store.get("state", default=None)
        formatted_input_with_state = await ctx.store.get(
            "formatted_input_with_state", default=False
        )
        if state and not formatted_input_with_state:
            # update last message with current state
            for block in llm_input[-1].blocks[::-1]:
                if isinstance(block, TextBlock):
                    block.text = self.state_prompt.format(state=state, msg=block.text)
                    break
            await ctx.store.set("formatted_input_with_state", True)

        return AgentSetup(
            input=llm_input,
            current_agent_name=ev.current_agent_name,
        )

    @step
    async def run_agent_step(self, ctx: Context, ev: AgentSetup) -> AgentOutput:
        """Run the agent."""
        memory: BaseMemory = await ctx.store.get("memory")
        agent = self.agents[ev.current_agent_name]
        user_msg_str = await ctx.store.get("user_msg_str")
        tools = await self.get_tools(ev.current_agent_name, user_msg_str or "")

        agent_output = await agent.take_step(
            ctx,
            ev.input,
            tools,
            memory,
        )

        ctx.write_event_to_stream(agent_output)
        return agent_output

    @step
    async def parse_agent_output(
        self, ctx: Context, ev: AgentOutput
    ) -> Union[StopEvent, ToolCall, None]:
        max_iterations = await ctx.get("max_iterations", default=DEFAULT_MAX_ITERATIONS)
        num_iterations = await ctx.get("num_iterations", default=0)
        num_iterations += 1
        await ctx.set("num_iterations", num_iterations)

        if num_iterations >= max_iterations:
            raise WorkflowRuntimeError(
                f"Max iterations of {max_iterations} reached! Either something went wrong, or you can "
                "increase the max iterations with `.run(.., max_iterations=...)`"
            )

        if not ev.tool_calls:
            agent = self.agents[ev.current_agent_name]
            memory: BaseMemory = await ctx.store.get("memory")
            output = await agent.finalize(ctx, ev, memory)

            cur_tool_calls: List[ToolCallResult] = await ctx.store.get(
                "current_tool_calls", default=[]
            )
            output.tool_calls.extend(cur_tool_calls)  # type: ignore
            await ctx.store.set("current_tool_calls", [])

            return StopEvent(result=output)

        await ctx.store.set("num_tool_calls", len(ev.tool_calls))

        for tool_call in ev.tool_calls:
            ctx.send_event(
                ToolCall(
                    tool_name=tool_call.tool_name,
                    tool_kwargs=tool_call.tool_kwargs,
                    tool_id=tool_call.tool_id,
                )
            )

        return None

    @step
    async def call_tool(self, ctx: Context, ev: ToolCall) -> ToolCallResult:
        """Calls the tool and handles the result."""
        ctx.write_event_to_stream(
            ToolCall(
                tool_name=ev.tool_name,
                tool_kwargs=ev.tool_kwargs,
                tool_id=ev.tool_id,
            )
        )

        current_agent_name = await ctx.store.get("current_agent_name")
        tools = await self.get_tools(current_agent_name, ev.tool_name)
        tools_by_name = {tool.metadata.name: tool for tool in tools}
        if ev.tool_name not in tools_by_name:
            tool = None
            result = ToolOutput(
                content=f"Tool {ev.tool_name} not found. Please select a tool that is available.",
                tool_name=ev.tool_name,
                raw_input=ev.tool_kwargs,
                raw_output=None,
                is_error=True,
            )
        else:
            tool = tools_by_name[ev.tool_name]
            result = await self._call_tool(ctx, tool, ev.tool_kwargs)

        result_ev = ToolCallResult(
            tool_name=ev.tool_name,
            tool_kwargs=ev.tool_kwargs,
            tool_id=ev.tool_id,
            tool_output=result,
            return_direct=tool.metadata.return_direct if tool else False,
        )

        ctx.write_event_to_stream(result_ev)
        return result_ev

    @step
    async def aggregate_tool_results(
        self, ctx: Context, ev: ToolCallResult
    ) -> Union[AgentInput, StopEvent, None]:
        """Aggregate tool results and return the next agent input."""
        num_tool_calls = await ctx.store.get("num_tool_calls", default=0)
        if num_tool_calls == 0:
            raise ValueError("No tool calls found, cannot aggregate results.")

        tool_call_results: list[ToolCallResult] = ctx.collect_events(  # type: ignore
            ev, expected=[ToolCallResult] * num_tool_calls
        )
        if not tool_call_results:
            return None

        memory: BaseMemory = await ctx.store.get("memory")
        agent_name: str = await ctx.store.get("current_agent_name")
        agent: BaseWorkflowAgent = self.agents[agent_name]

        # track tool calls made during a .run() call
        cur_tool_calls: List[ToolCallResult] = await ctx.store.get(
            "current_tool_calls", default=[]
        )
        cur_tool_calls.extend(tool_call_results)
        await ctx.store.set("current_tool_calls", cur_tool_calls)

        await agent.handle_tool_call_results(ctx, tool_call_results, memory)

        # set the next agent, if needed
        # the handoff tool sets this
        next_agent_name = await ctx.store.get("next_agent", default=None)
        if next_agent_name:
            await ctx.store.set("current_agent_name", next_agent_name)
            await ctx.store.set("next_agent", None)

        if any(
            tool_call_result.return_direct for tool_call_result in tool_call_results
        ):
            # if any tool calls return directly, take the first one
            return_direct_tool = next(
                tool_call_result
                for tool_call_result in tool_call_results
                if tool_call_result.return_direct
            )

            # always finalize the agent, even if we're just handing off
            result = AgentOutput(
                response=ChatMessage(
                    role="assistant",
                    content=return_direct_tool.tool_output.content or "",
                ),
                tool_calls=[
                    ToolSelection(
                        tool_id=t.tool_id,
                        tool_name=t.tool_name,
                        tool_kwargs=t.tool_kwargs,
                    )
                    for t in cur_tool_calls
                ],
                raw=return_direct_tool.tool_output.raw_output,
                current_agent_name=agent.name,
            )
            result = await agent.finalize(ctx, result, memory)

            # we don't want to stop the system if we're just handing off
            if return_direct_tool.tool_name != "handoff":
                await ctx.store.set("current_tool_calls", [])
                return StopEvent(result=result)

        user_msg_str = await ctx.store.get("user_msg_str")
        input_messages = await memory.aget(input=user_msg_str)

        # get this again, in case it changed
        agent_name = await ctx.store.get("current_agent_name")
        agent = self.agents[agent_name]

        return AgentInput(input=input_messages, current_agent_name=agent.name)

    def run(
        self,
        user_msg: Optional[Union[str, ChatMessage]] = None,
        chat_history: Optional[List[ChatMessage]] = None,
        memory: Optional[BaseMemory] = None,
        ctx: Optional[Context] = None,
        stepwise: bool = False,
        checkpoint_callback: Optional[CheckpointCallback] = None,
        max_iterations: Optional[int] = None,
        **kwargs: Any,
    ) -> WorkflowHandler:
        # Detect if hitl is needed
        if ctx is not None and ctx.is_running:
            return super().run(
                ctx=ctx,
                stepwise=stepwise,
                checkpoint_callback=checkpoint_callback,
                **kwargs,
            )
        else:
            return super().run(
                start_event=AgentWorkflowStartEvent(
                    user_msg=user_msg,
                    chat_history=chat_history,
                    memory=memory,
                    max_iterations=max_iterations,
                    **kwargs,
                ),
                ctx=ctx,
                stepwise=stepwise,
                checkpoint_callback=checkpoint_callback,
            )

    @classmethod
    def from_tools_or_functions(
        cls,
        tools_or_functions: List[Union[BaseTool, Callable]],
        llm: Optional[LLM] = None,
        system_prompt: Optional[str] = None,
        state_prompt: Optional[Union[str, BasePromptTemplate]] = None,
        initial_state: Optional[dict] = None,
        timeout: Optional[float] = None,
        verbose: bool = False,
    ) -> "AgentWorkflow":
        """
        Initializes an AgentWorkflow from a list of tools or functions.

        The workflow will be initialized with a single agent that uses the provided tools or functions.

        If the LLM is a function calling model, the workflow will use the FunctionAgent.
        Otherwise, it will use the ReActAgent.
        """
        llm = llm or Settings.llm
        agent_cls = (
            FunctionAgent if llm.metadata.is_function_calling_model else ReActAgent
        )

        tools = [
            FunctionTool.from_defaults(fn=tool)
            if not isinstance(tool, BaseTool)
            else tool
            for tool in tools_or_functions
        ]
        return cls(
            agents=[
                agent_cls(
                    name="Agent",
                    description="A single agent that uses the provided tools or functions.",
                    tools=tools,
                    llm=llm,
                    system_prompt=system_prompt,
                )
            ],
            state_prompt=state_prompt,
            initial_state=initial_state,
            timeout=timeout,
            verbose=verbose,
        )

```
  
---|---  
###  get_tools `async` #
```
get_tools(agent_name: str, input_str: Optional[str] = None) -> Sequence[AsyncBaseTool]

```

Get tools for the given agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/multi_agent_workflow.py`

| ```
async def get_tools(
    self, agent_name: str, input_str: Optional[str] = None
) -> Sequence[AsyncBaseTool]:
    """Get tools for the given agent."""
    agent_tools = self.agents[agent_name].tools or []
    tools = [*agent_tools]
    retriever = self.agents[agent_name].tool_retriever
    if retriever is not None:
        retrieved_tools = await retriever.aretrieve(input_str or "")
        tools.extend(retrieved_tools)

    if (
        self.agents[agent_name].can_handoff_to
        or self.agents[agent_name].can_handoff_to is None
    ):
        handoff_tool = self._get_handoff_tool(self.agents[agent_name])
        if handoff_tool:
            tools.append(handoff_tool)

    return self._ensure_tools_are_async(cast(List[BaseTool], tools))

```
  
---|---  
###  init_run `async` #
```
init_run(ctx: Context, ev: AgentWorkflowStartEvent) -> AgentInput

```

Sets up the workflow and validates inputs.
Source code in `llama-index-core/llama_index/core/agent/workflow/multi_agent_workflow.py`

| ```
@step
async def init_run(self, ctx: Context, ev: AgentWorkflowStartEvent) -> AgentInput:
    """Sets up the workflow and validates inputs."""
    await self._init_context(ctx, ev)

    user_msg: Optional[Union[str, ChatMessage]] = ev.get("user_msg")
    chat_history: Optional[List[ChatMessage]] = ev.get("chat_history", [])

    # Convert string user_msg to ChatMessage
    if isinstance(user_msg, str):
        user_msg = ChatMessage(role="user", content=user_msg)

    # Add messages to memory
    memory: BaseMemory = await ctx.store.get("memory")

    # First set chat history if it exists
    if chat_history:
        await memory.aset(chat_history)

    # Then add user message if it exists
    if user_msg:
        await memory.aput(user_msg)
        content_str = "\n".join(
            [
                block.text
                for block in user_msg.blocks
                if isinstance(block, TextBlock)
            ]
        )
        await ctx.store.set("user_msg_str", content_str)
    elif chat_history:
        # If no user message, use the last message from chat history as user_msg_str
        content_str = "\n".join(
            [
                block.text
                for block in chat_history[-1].blocks
                if isinstance(block, TextBlock)
            ]
        )
        await ctx.store.set("user_msg_str", content_str)
    else:
        raise ValueError("Must provide either user_msg or chat_history")

    # Get all messages from memory
    input_messages = await memory.aget()

    # send to the current agent
    current_agent_name: str = await ctx.store.get("current_agent_name")
    return AgentInput(input=input_messages, current_agent_name=current_agent_name)

```
  
---|---  
###  setup_agent `async` #
```
setup_agent(ctx: Context, ev: AgentInput) -> AgentSetup

```

Main agent handling logic.
Source code in `llama-index-core/llama_index/core/agent/workflow/multi_agent_workflow.py`

| ```
@step
async def setup_agent(self, ctx: Context, ev: AgentInput) -> AgentSetup:
    """Main agent handling logic."""
    current_agent_name = ev.current_agent_name
    agent = self.agents[current_agent_name]
    llm_input = [*ev.input]

    if agent.system_prompt:
        llm_input = [
            ChatMessage(role="system", content=agent.system_prompt),
            *llm_input,
        ]

    state = await ctx.store.get("state", default=None)
    formatted_input_with_state = await ctx.store.get(
        "formatted_input_with_state", default=False
    )
    if state and not formatted_input_with_state:
        # update last message with current state
        for block in llm_input[-1].blocks[::-1]:
            if isinstance(block, TextBlock):
                block.text = self.state_prompt.format(state=state, msg=block.text)
                break
        await ctx.store.set("formatted_input_with_state", True)

    return AgentSetup(
        input=llm_input,
        current_agent_name=ev.current_agent_name,
    )

```
  
---|---  
###  run_agent_step `async` #
```
run_agent_step(ctx: Context, ev: AgentSetup) -> AgentOutput

```

Run the agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/multi_agent_workflow.py`

| ```
@step
async def run_agent_step(self, ctx: Context, ev: AgentSetup) -> AgentOutput:
    """Run the agent."""
    memory: BaseMemory = await ctx.store.get("memory")
    agent = self.agents[ev.current_agent_name]
    user_msg_str = await ctx.store.get("user_msg_str")
    tools = await self.get_tools(ev.current_agent_name, user_msg_str or "")

    agent_output = await agent.take_step(
        ctx,
        ev.input,
        tools,
        memory,
    )

    ctx.write_event_to_stream(agent_output)
    return agent_output

```
  
---|---  
###  call_tool `async` #
```
call_tool(ctx: Context, ev: ToolCall) -> ToolCallResult

```

Calls the tool and handles the result.
Source code in `llama-index-core/llama_index/core/agent/workflow/multi_agent_workflow.py`

| ```
@step
async def call_tool(self, ctx: Context, ev: ToolCall) -> ToolCallResult:
    """Calls the tool and handles the result."""
    ctx.write_event_to_stream(
        ToolCall(
            tool_name=ev.tool_name,
            tool_kwargs=ev.tool_kwargs,
            tool_id=ev.tool_id,
        )
    )

    current_agent_name = await ctx.store.get("current_agent_name")
    tools = await self.get_tools(current_agent_name, ev.tool_name)
    tools_by_name = {tool.metadata.name: tool for tool in tools}
    if ev.tool_name not in tools_by_name:
        tool = None
        result = ToolOutput(
            content=f"Tool {ev.tool_name} not found. Please select a tool that is available.",
            tool_name=ev.tool_name,
            raw_input=ev.tool_kwargs,
            raw_output=None,
            is_error=True,
        )
    else:
        tool = tools_by_name[ev.tool_name]
        result = await self._call_tool(ctx, tool, ev.tool_kwargs)

    result_ev = ToolCallResult(
        tool_name=ev.tool_name,
        tool_kwargs=ev.tool_kwargs,
        tool_id=ev.tool_id,
        tool_output=result,
        return_direct=tool.metadata.return_direct if tool else False,
    )

    ctx.write_event_to_stream(result_ev)
    return result_ev

```
  
---|---  
###  aggregate_tool_results `async` #
```
aggregate_tool_results(ctx: Context, ev: ToolCallResult) -> Union[AgentInput, StopEvent, None]

```

Aggregate tool results and return the next agent input.
Source code in `llama-index-core/llama_index/core/agent/workflow/multi_agent_workflow.py`

| ```
@step
async def aggregate_tool_results(
    self, ctx: Context, ev: ToolCallResult
) -> Union[AgentInput, StopEvent, None]:
    """Aggregate tool results and return the next agent input."""
    num_tool_calls = await ctx.store.get("num_tool_calls", default=0)
    if num_tool_calls == 0:
        raise ValueError("No tool calls found, cannot aggregate results.")

    tool_call_results: list[ToolCallResult] = ctx.collect_events(  # type: ignore
        ev, expected=[ToolCallResult] * num_tool_calls
    )
    if not tool_call_results:
        return None

    memory: BaseMemory = await ctx.store.get("memory")
    agent_name: str = await ctx.store.get("current_agent_name")
    agent: BaseWorkflowAgent = self.agents[agent_name]

    # track tool calls made during a .run() call
    cur_tool_calls: List[ToolCallResult] = await ctx.store.get(
        "current_tool_calls", default=[]
    )
    cur_tool_calls.extend(tool_call_results)
    await ctx.store.set("current_tool_calls", cur_tool_calls)

    await agent.handle_tool_call_results(ctx, tool_call_results, memory)

    # set the next agent, if needed
    # the handoff tool sets this
    next_agent_name = await ctx.store.get("next_agent", default=None)
    if next_agent_name:
        await ctx.store.set("current_agent_name", next_agent_name)
        await ctx.store.set("next_agent", None)

    if any(
        tool_call_result.return_direct for tool_call_result in tool_call_results
    ):
        # if any tool calls return directly, take the first one
        return_direct_tool = next(
            tool_call_result
            for tool_call_result in tool_call_results
            if tool_call_result.return_direct
        )

        # always finalize the agent, even if we're just handing off
        result = AgentOutput(
            response=ChatMessage(
                role="assistant",
                content=return_direct_tool.tool_output.content or "",
            ),
            tool_calls=[
                ToolSelection(
                    tool_id=t.tool_id,
                    tool_name=t.tool_name,
                    tool_kwargs=t.tool_kwargs,
                )
                for t in cur_tool_calls
            ],
            raw=return_direct_tool.tool_output.raw_output,
            current_agent_name=agent.name,
        )
        result = await agent.finalize(ctx, result, memory)

        # we don't want to stop the system if we're just handing off
        if return_direct_tool.tool_name != "handoff":
            await ctx.store.set("current_tool_calls", [])
            return StopEvent(result=result)

    user_msg_str = await ctx.store.get("user_msg_str")
    input_messages = await memory.aget(input=user_msg_str)

    # get this again, in case it changed
    agent_name = await ctx.store.get("current_agent_name")
    agent = self.agents[agent_name]

    return AgentInput(input=input_messages, current_agent_name=agent.name)

```
  
---|---  
###  from_tools_or_functions `classmethod` #
```
from_tools_or_functions(tools_or_functions: List[Union[BaseTool, Callable]], llm: Optional[LLM] = None, system_prompt: Optional[str] = None, state_prompt: Optional[Union[str, BasePromptTemplate]] = None, initial_state: Optional[dict] = None, timeout: Optional[float] = None, verbose: bool = False) -> AgentWorkflow

```

Initializes an AgentWorkflow from a list of tools or functions.
The workflow will be initialized with a single agent that uses the provided tools or functions.
If the LLM is a function calling model, the workflow will use the FunctionAgent. Otherwise, it will use the ReActAgent.
Source code in `llama-index-core/llama_index/core/agent/workflow/multi_agent_workflow.py`

| ```
@classmethod
def from_tools_or_functions(
    cls,
    tools_or_functions: List[Union[BaseTool, Callable]],
    llm: Optional[LLM] = None,
    system_prompt: Optional[str] = None,
    state_prompt: Optional[Union[str, BasePromptTemplate]] = None,
    initial_state: Optional[dict] = None,
    timeout: Optional[float] = None,
    verbose: bool = False,
) -> "AgentWorkflow":
    """
    Initializes an AgentWorkflow from a list of tools or functions.

    The workflow will be initialized with a single agent that uses the provided tools or functions.

    If the LLM is a function calling model, the workflow will use the FunctionAgent.
    Otherwise, it will use the ReActAgent.
    """
    llm = llm or Settings.llm
    agent_cls = (
        FunctionAgent if llm.metadata.is_function_calling_model else ReActAgent
    )

    tools = [
        FunctionTool.from_defaults(fn=tool)
        if not isinstance(tool, BaseTool)
        else tool
        for tool in tools_or_functions
    ]
    return cls(
        agents=[
            agent_cls(
                name="Agent",
                description="A single agent that uses the provided tools or functions.",
                tools=tools,
                llm=llm,
                system_prompt=system_prompt,
            )
        ],
        state_prompt=state_prompt,
        initial_state=initial_state,
        timeout=timeout,
        verbose=verbose,
    )

```
  
---|---  
##  BaseWorkflowAgent #
Bases: `Workflow`, `BaseModel`, `PromptMixin`
Base class for all agents, combining config and logic.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`name` |  `str` |  The name of the agent |  `'Agent'`  
`description` |  `str` |  The description of what the agent does and is responsible for |  `'An agent that can perform a task'`  
`system_prompt` |  `str | None` |  The system prompt for the agent |  `None`  
`tools` |  `List[Union[BaseTool, Callable]] | None` |  The tools that the agent can use |  `None`  
`tool_retriever` |  `ObjectRetriever | None` |  The tool retriever for the agent, can be provided instead of tools |  `None`  
`can_handoff_to` |  `List[str] | None` |  The agent names that this agent can hand off to |  `None`  
`llm` |  `LLM` |  The LLM that the agent uses |  `<dynamic>`  
`state_prompt` |  `str | BasePromptTemplate` |  The prompt to use to update the state of the agent |  `'Current state:\n{state}\n\nCurrent message:\n{msg}\n'`  
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
class BaseWorkflowAgent(
    Workflow, BaseModel, PromptMixin, metaclass=BaseWorkflowAgentMeta
):
    """Base class for all agents, combining config and logic."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(default=DEFAULT_AGENT_NAME, description="The name of the agent")
    description: str = Field(
        default=DEFAULT_AGENT_DESCRIPTION,
        description="The description of what the agent does and is responsible for",
    )
    system_prompt: Optional[str] = Field(
        default=None, description="The system prompt for the agent"
    )
    tools: Optional[List[Union[BaseTool, Callable]]] = Field(
        default=None, description="The tools that the agent can use"
    )
    tool_retriever: Optional[ObjectRetriever] = Field(
        default=None,
        description="The tool retriever for the agent, can be provided instead of tools",
    )
    can_handoff_to: Optional[List[str]] = Field(
        default=None, description="The agent names that this agent can hand off to"
    )
    llm: LLM = Field(
        default_factory=get_default_llm, description="The LLM that the agent uses"
    )
    initial_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="The initial state of the agent, can be used by accessed under `await ctx.store.get('state')`",
    )
    state_prompt: Union[str, BasePromptTemplate] = Field(
        default=DEFAULT_STATE_PROMPT,
        description="The prompt to use to update the state of the agent",
        validate_default=True,
    )

    def __init__(
        self,
        name: str = DEFAULT_AGENT_NAME,
        description: str = DEFAULT_AGENT_DESCRIPTION,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Union[BaseTool, Callable]]] = None,
        tool_retriever: Optional[ObjectRetriever] = None,
        can_handoff_to: Optional[List[str]] = None,
        llm: Optional[LLM] = None,
        initial_state: Optional[Dict[str, Any]] = None,
        state_prompt: Optional[Union[str, BasePromptTemplate]] = None,
        timeout: Optional[float] = None,
        verbose: bool = False,
        **kwargs: Any,
    ):
        # Filter out workflow-specific kwargs
        workflow_kwargs = {k: v for k, v in kwargs.items() if k in WORKFLOW_KWARGS}
        model_kwargs = {k: v for k, v in kwargs.items() if k not in WORKFLOW_KWARGS}

        # Initialize BaseModel with the Pydantic fields
        if isinstance(state_prompt, str):
            state_prompt = PromptTemplate(state_prompt)
        elif state_prompt is None:
            state_prompt = DEFAULT_STATE_PROMPT

        BaseModel.__init__(
            self,
            name=name,
            description=description,
            system_prompt=system_prompt,
            tools=tools,
            tool_retriever=tool_retriever,
            can_handoff_to=can_handoff_to,
            llm=llm or get_default_llm(),
            initial_state=initial_state or {},
            state_prompt=state_prompt,
            **model_kwargs,
        )

        # Initialize Workflow with workflow-specific parameters
        Workflow.__init__(self, timeout=timeout, verbose=verbose, **workflow_kwargs)

    @field_validator("tools", mode="before")
    def validate_tools(
        cls, v: Optional[Sequence[Union[BaseTool, Callable]]]
    ) -> Optional[Sequence[BaseTool]]:
        """
        Validate tools.

        If tools are not of type BaseTool, they will be converted to FunctionTools.
        This assumes the inputs are tools or callable functions.
        """
        if v is None:
            return None

        validated_tools: List[BaseTool] = []
        for tool in v:
            if not isinstance(tool, BaseTool):
                validated_tools.append(FunctionTool.from_defaults(tool))
            else:
                validated_tools.append(tool)

        for tool in validated_tools:
            if tool.metadata.name == "handoff":
                raise ValueError(
                    "'handoff' is a reserved tool name. Please use a different name."
                )

        return validated_tools  # type: ignore[return-value]

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        return {}

    def _get_prompt_modules(self) -> PromptMixinType:
        """Get prompt sub-modules."""
        return {}

    def _update_prompts(self, prompts_dict: PromptDictType) -> None:
        """Update prompts."""

    @abstractmethod
    async def take_step(
        self,
        ctx: Context,
        llm_input: List[ChatMessage],
        tools: Sequence[AsyncBaseTool],
        memory: BaseMemory,
    ) -> AgentOutput:
        """Take a single step with the agent."""

    @abstractmethod
    async def handle_tool_call_results(
        self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
    ) -> None:
        """Handle tool call results."""

    @abstractmethod
    async def finalize(
        self, ctx: Context, output: AgentOutput, memory: BaseMemory
    ) -> AgentOutput:
        """Finalize the agent's execution."""

    def _ensure_tools_are_async(
        self, tools: Sequence[BaseTool]
    ) -> Sequence[AsyncBaseTool]:
        """Ensure all tools are async."""
        return [adapt_to_async_tool(tool) for tool in tools]

    async def get_tools(
        self, input_str: Optional[str] = None
    ) -> Sequence[AsyncBaseTool]:
        """Get tools for the given agent."""
        tools = [*self.tools] if self.tools else []
        if self.tool_retriever is not None:
            retrieved_tools = await self.tool_retriever.aretrieve(input_str or "")
            tools.extend(retrieved_tools)

        return self._ensure_tools_are_async(cast(List[BaseTool], tools))

    async def _init_context(self, ctx: Context, ev: AgentWorkflowStartEvent) -> None:
        """Initialize the context once, if needed."""
        if not await ctx.store.get("memory", default=None):
            default_memory = ev.get("memory", default=None)
            default_memory = default_memory or ChatMemoryBuffer.from_defaults(
                llm=self.llm or Settings.llm
            )
            await ctx.store.set("memory", default_memory)
        if not await ctx.store.get("state", default=None):
            await ctx.store.set("state", self.initial_state.copy())

        if not await ctx.get("max_iterations", default=None):
            max_iterations = (
                ev.get("max_iterations", default=None) or DEFAULT_MAX_ITERATIONS
            )
            await ctx.set("max_iterations", max_iterations)

        # Reset the number of iterations
        await ctx.set("num_iterations", 0)

        # always set to false initially
        await ctx.store.set("formatted_input_with_state", False)

    async def _call_tool(
        self,
        ctx: Context,
        tool: AsyncBaseTool,
        tool_input: dict,
    ) -> ToolOutput:
        """Call the given tool with the given input."""
        try:
            if (
                isinstance(tool, FunctionTool)
                and tool.requires_context
                and tool.ctx_param_name is not None
            ):
                new_tool_input = {**tool_input}
                new_tool_input[tool.ctx_param_name] = ctx
                tool_output = await tool.acall(**new_tool_input)
            else:
                tool_output = await tool.acall(**tool_input)
        except Exception as e:
            tool_output = ToolOutput(
                content=str(e),
                tool_name=tool.metadata.get_name(),
                raw_input=tool_input,
                raw_output=str(e),
                is_error=True,
            )

        return tool_output

    @step
    async def init_run(self, ctx: Context, ev: AgentWorkflowStartEvent) -> AgentInput:
        """Sets up the workflow and validates inputs."""
        await self._init_context(ctx, ev)

        user_msg: Optional[Union[str, ChatMessage]] = ev.get("user_msg")
        chat_history: Optional[List[ChatMessage]] = ev.get("chat_history", [])

        # Convert string user_msg to ChatMessage
        if isinstance(user_msg, str):
            user_msg = ChatMessage(role="user", content=user_msg)

        # Add messages to memory
        memory: BaseMemory = await ctx.store.get("memory")

        # First set chat history if it exists
        if chat_history:
            await memory.aset(chat_history)

        # Then add user message if it exists
        if user_msg:
            await memory.aput(user_msg)
            content_str = "\n".join(
                [
                    block.text
                    for block in user_msg.blocks
                    if isinstance(block, TextBlock)
                ]
            )
            await ctx.store.set("user_msg_str", content_str)
        elif chat_history:
            # If no user message, use the last message from chat history as user_msg_str
            content_str = "\n".join(
                [
                    block.text
                    for block in chat_history[-1].blocks
                    if isinstance(block, TextBlock)
                ]
            )
            await ctx.store.set("user_msg_str", content_str)
        else:
            raise ValueError("Must provide either user_msg or chat_history")

        # Get all messages from memory
        input_messages = await memory.aget()

        # send to the current agent
        return AgentInput(input=input_messages, current_agent_name=self.name)

    @step
    async def setup_agent(self, ctx: Context, ev: AgentInput) -> AgentSetup:
        """Main agent handling logic."""
        llm_input = [*ev.input]

        if self.system_prompt:
            llm_input = [
                ChatMessage(role="system", content=self.system_prompt),
                *llm_input,
            ]

        state = await ctx.store.get("state", default=None)
        formatted_input_with_state = await ctx.store.get(
            "formatted_input_with_state", default=False
        )
        if state and not formatted_input_with_state:
            # update last message with current state
            for block in llm_input[-1].blocks[::-1]:
                if isinstance(block, TextBlock):
                    block.text = self.state_prompt.format(state=state, msg=block.text)
                    break
            await ctx.store.set("formatted_input_with_state", True)

        return AgentSetup(
            input=llm_input,
            current_agent_name=ev.current_agent_name,
        )

    @step
    async def run_agent_step(self, ctx: Context, ev: AgentSetup) -> AgentOutput:
        """Run the agent."""
        memory: BaseMemory = await ctx.store.get("memory")
        user_msg_str = await ctx.store.get("user_msg_str")
        tools = await self.get_tools(user_msg_str or "")

        agent_output = await self.take_step(
            ctx,
            ev.input,
            tools,
            memory,
        )

        ctx.write_event_to_stream(agent_output)
        return agent_output

    @step
    async def parse_agent_output(
        self, ctx: Context, ev: AgentOutput
    ) -> Union[StopEvent, ToolCall, None]:
        max_iterations = await ctx.get("max_iterations", default=DEFAULT_MAX_ITERATIONS)
        num_iterations = await ctx.get("num_iterations", default=0)
        num_iterations += 1
        await ctx.set("num_iterations", num_iterations)

        if num_iterations >= max_iterations:
            raise WorkflowRuntimeError(
                f"Max iterations of {max_iterations} reached! Either something went wrong, or you can "
                "increase the max iterations with `.run(.., max_iterations=...)`"
            )

        if not ev.tool_calls:
            memory: BaseMemory = await ctx.store.get("memory")
            output = await self.finalize(ctx, ev, memory)

            cur_tool_calls: List[ToolCallResult] = await ctx.store.get(
                "current_tool_calls", default=[]
            )
            output.tool_calls.extend(cur_tool_calls)  # type: ignore
            await ctx.store.set("current_tool_calls", [])

            return StopEvent(result=output)

        await ctx.store.set("num_tool_calls", len(ev.tool_calls))

        for tool_call in ev.tool_calls:
            ctx.send_event(
                ToolCall(
                    tool_name=tool_call.tool_name,
                    tool_kwargs=tool_call.tool_kwargs,
                    tool_id=tool_call.tool_id,
                )
            )

        return None

    @step
    async def call_tool(self, ctx: Context, ev: ToolCall) -> ToolCallResult:
        """Calls the tool and handles the result."""
        ctx.write_event_to_stream(
            ToolCall(
                tool_name=ev.tool_name,
                tool_kwargs=ev.tool_kwargs,
                tool_id=ev.tool_id,
            )
        )

        tools = await self.get_tools(ev.tool_name)
        tools_by_name = {tool.metadata.name: tool for tool in tools}
        if ev.tool_name not in tools_by_name:
            tool = None
            result = ToolOutput(
                content=f"Tool {ev.tool_name} not found. Please select a tool that is available.",
                tool_name=ev.tool_name,
                raw_input=ev.tool_kwargs,
                raw_output=None,
                is_error=True,
            )
        else:
            tool = tools_by_name[ev.tool_name]
            result = await self._call_tool(ctx, tool, ev.tool_kwargs)

        result_ev = ToolCallResult(
            tool_name=ev.tool_name,
            tool_kwargs=ev.tool_kwargs,
            tool_id=ev.tool_id,
            tool_output=result,
            return_direct=tool.metadata.return_direct if tool else False,
        )

        ctx.write_event_to_stream(result_ev)
        return result_ev

    @step
    async def aggregate_tool_results(
        self, ctx: Context, ev: ToolCallResult
    ) -> Union[AgentInput, StopEvent, None]:
        """Aggregate tool results and return the next agent input."""
        num_tool_calls = await ctx.store.get("num_tool_calls", default=0)
        if num_tool_calls == 0:
            raise ValueError("No tool calls found, cannot aggregate results.")

        tool_call_results: list[ToolCallResult] = ctx.collect_events(  # type: ignore
            ev, expected=[ToolCallResult] * num_tool_calls
        )
        if not tool_call_results:
            return None

        memory: BaseMemory = await ctx.store.get("memory")

        # track tool calls made during a .run() call
        cur_tool_calls: List[ToolCallResult] = await ctx.store.get(
            "current_tool_calls", default=[]
        )
        cur_tool_calls.extend(tool_call_results)
        await ctx.store.set("current_tool_calls", cur_tool_calls)

        await self.handle_tool_call_results(ctx, tool_call_results, memory)

        if any(
            tool_call_result.return_direct for tool_call_result in tool_call_results
        ):
            # if any tool calls return directly, take the first one
            return_direct_tool = next(
                tool_call_result
                for tool_call_result in tool_call_results
                if tool_call_result.return_direct
            )

            # always finalize the agent, even if we're just handing off
            result = AgentOutput(
                response=ChatMessage(
                    role="assistant",
                    content=return_direct_tool.tool_output.content or "",
                ),
                tool_calls=[
                    ToolSelection(
                        tool_id=t.tool_id,
                        tool_name=t.tool_name,
                        tool_kwargs=t.tool_kwargs,
                    )
                    for t in cur_tool_calls
                ],
                raw=return_direct_tool.tool_output.raw_output,
                current_agent_name=self.name,
            )
            result = await self.finalize(ctx, result, memory)

        user_msg_str = await ctx.store.get("user_msg_str")
        input_messages = await memory.aget(input=user_msg_str)

        return AgentInput(input=input_messages, current_agent_name=self.name)

    def run(
        self,
        user_msg: Optional[Union[str, ChatMessage]] = None,
        chat_history: Optional[List[ChatMessage]] = None,
        memory: Optional[BaseMemory] = None,
        ctx: Optional[Context] = None,
        stepwise: bool = False,
        checkpoint_callback: Optional[CheckpointCallback] = None,
        max_iterations: Optional[int] = None,
        **kwargs: Any,
    ) -> WorkflowHandler:
        # Detect if hitl is needed
        if ctx is not None and ctx.is_running:
            return super().run(
                ctx=ctx,
                stepwise=stepwise,
                checkpoint_callback=checkpoint_callback,
                **kwargs,
            )
        else:
            return super().run(
                start_event=AgentWorkflowStartEvent(
                    user_msg=user_msg,
                    chat_history=chat_history,
                    memory=memory,
                    max_iterations=max_iterations,
                    **kwargs,
                ),
                ctx=ctx,
                stepwise=stepwise,
                checkpoint_callback=checkpoint_callback,
            )

```
  
---|---  
###  validate_tools #
```
validate_tools(v: Optional[Sequence[Union[BaseTool, Callable]]]) -> Optional[Sequence[BaseTool]]

```

Validate tools.
If tools are not of type BaseTool, they will be converted to FunctionTools. This assumes the inputs are tools or callable functions.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@field_validator("tools", mode="before")
def validate_tools(
    cls, v: Optional[Sequence[Union[BaseTool, Callable]]]
) -> Optional[Sequence[BaseTool]]:
    """
    Validate tools.

    If tools are not of type BaseTool, they will be converted to FunctionTools.
    This assumes the inputs are tools or callable functions.
    """
    if v is None:
        return None

    validated_tools: List[BaseTool] = []
    for tool in v:
        if not isinstance(tool, BaseTool):
            validated_tools.append(FunctionTool.from_defaults(tool))
        else:
            validated_tools.append(tool)

    for tool in validated_tools:
        if tool.metadata.name == "handoff":
            raise ValueError(
                "'handoff' is a reserved tool name. Please use a different name."
            )

    return validated_tools  # type: ignore[return-value]

```
  
---|---  
###  take_step `abstractmethod` `async` #
```
take_step(ctx: Context, llm_input: List[ChatMessage], tools: Sequence[AsyncBaseTool], memory: BaseMemory) -> AgentOutput

```

Take a single step with the agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@abstractmethod
async def take_step(
    self,
    ctx: Context,
    llm_input: List[ChatMessage],
    tools: Sequence[AsyncBaseTool],
    memory: BaseMemory,
) -> AgentOutput:
    """Take a single step with the agent."""

```
  
---|---  
###  handle_tool_call_results `abstractmethod` `async` #
```
handle_tool_call_results(ctx: Context, results: List[ToolCallResult], memory: BaseMemory) -> None

```

Handle tool call results.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@abstractmethod
async def handle_tool_call_results(
    self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
) -> None:
    """Handle tool call results."""

```
  
---|---  
###  finalize `abstractmethod` `async` #
```
finalize(ctx: Context, output: AgentOutput, memory: BaseMemory) -> AgentOutput

```

Finalize the agent's execution.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@abstractmethod
async def finalize(
    self, ctx: Context, output: AgentOutput, memory: BaseMemory
) -> AgentOutput:
    """Finalize the agent's execution."""

```
  
---|---  
###  get_tools `async` #
```
get_tools(input_str: Optional[str] = None) -> Sequence[AsyncBaseTool]

```

Get tools for the given agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
async def get_tools(
    self, input_str: Optional[str] = None
) -> Sequence[AsyncBaseTool]:
    """Get tools for the given agent."""
    tools = [*self.tools] if self.tools else []
    if self.tool_retriever is not None:
        retrieved_tools = await self.tool_retriever.aretrieve(input_str or "")
        tools.extend(retrieved_tools)

    return self._ensure_tools_are_async(cast(List[BaseTool], tools))

```
  
---|---  
###  init_run `async` #
```
init_run(ctx: Context, ev: AgentWorkflowStartEvent) -> AgentInput

```

Sets up the workflow and validates inputs.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@step
async def init_run(self, ctx: Context, ev: AgentWorkflowStartEvent) -> AgentInput:
    """Sets up the workflow and validates inputs."""
    await self._init_context(ctx, ev)

    user_msg: Optional[Union[str, ChatMessage]] = ev.get("user_msg")
    chat_history: Optional[List[ChatMessage]] = ev.get("chat_history", [])

    # Convert string user_msg to ChatMessage
    if isinstance(user_msg, str):
        user_msg = ChatMessage(role="user", content=user_msg)

    # Add messages to memory
    memory: BaseMemory = await ctx.store.get("memory")

    # First set chat history if it exists
    if chat_history:
        await memory.aset(chat_history)

    # Then add user message if it exists
    if user_msg:
        await memory.aput(user_msg)
        content_str = "\n".join(
            [
                block.text
                for block in user_msg.blocks
                if isinstance(block, TextBlock)
            ]
        )
        await ctx.store.set("user_msg_str", content_str)
    elif chat_history:
        # If no user message, use the last message from chat history as user_msg_str
        content_str = "\n".join(
            [
                block.text
                for block in chat_history[-1].blocks
                if isinstance(block, TextBlock)
            ]
        )
        await ctx.store.set("user_msg_str", content_str)
    else:
        raise ValueError("Must provide either user_msg or chat_history")

    # Get all messages from memory
    input_messages = await memory.aget()

    # send to the current agent
    return AgentInput(input=input_messages, current_agent_name=self.name)

```
  
---|---  
###  setup_agent `async` #
```
setup_agent(ctx: Context, ev: AgentInput) -> AgentSetup

```

Main agent handling logic.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@step
async def setup_agent(self, ctx: Context, ev: AgentInput) -> AgentSetup:
    """Main agent handling logic."""
    llm_input = [*ev.input]

    if self.system_prompt:
        llm_input = [
            ChatMessage(role="system", content=self.system_prompt),
            *llm_input,
        ]

    state = await ctx.store.get("state", default=None)
    formatted_input_with_state = await ctx.store.get(
        "formatted_input_with_state", default=False
    )
    if state and not formatted_input_with_state:
        # update last message with current state
        for block in llm_input[-1].blocks[::-1]:
            if isinstance(block, TextBlock):
                block.text = self.state_prompt.format(state=state, msg=block.text)
                break
        await ctx.store.set("formatted_input_with_state", True)

    return AgentSetup(
        input=llm_input,
        current_agent_name=ev.current_agent_name,
    )

```
  
---|---  
###  run_agent_step `async` #
```
run_agent_step(ctx: Context, ev: AgentSetup) -> AgentOutput

```

Run the agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@step
async def run_agent_step(self, ctx: Context, ev: AgentSetup) -> AgentOutput:
    """Run the agent."""
    memory: BaseMemory = await ctx.store.get("memory")
    user_msg_str = await ctx.store.get("user_msg_str")
    tools = await self.get_tools(user_msg_str or "")

    agent_output = await self.take_step(
        ctx,
        ev.input,
        tools,
        memory,
    )

    ctx.write_event_to_stream(agent_output)
    return agent_output

```
  
---|---  
###  call_tool `async` #
```
call_tool(ctx: Context, ev: ToolCall) -> ToolCallResult

```

Calls the tool and handles the result.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@step
async def call_tool(self, ctx: Context, ev: ToolCall) -> ToolCallResult:
    """Calls the tool and handles the result."""
    ctx.write_event_to_stream(
        ToolCall(
            tool_name=ev.tool_name,
            tool_kwargs=ev.tool_kwargs,
            tool_id=ev.tool_id,
        )
    )

    tools = await self.get_tools(ev.tool_name)
    tools_by_name = {tool.metadata.name: tool for tool in tools}
    if ev.tool_name not in tools_by_name:
        tool = None
        result = ToolOutput(
            content=f"Tool {ev.tool_name} not found. Please select a tool that is available.",
            tool_name=ev.tool_name,
            raw_input=ev.tool_kwargs,
            raw_output=None,
            is_error=True,
        )
    else:
        tool = tools_by_name[ev.tool_name]
        result = await self._call_tool(ctx, tool, ev.tool_kwargs)

    result_ev = ToolCallResult(
        tool_name=ev.tool_name,
        tool_kwargs=ev.tool_kwargs,
        tool_id=ev.tool_id,
        tool_output=result,
        return_direct=tool.metadata.return_direct if tool else False,
    )

    ctx.write_event_to_stream(result_ev)
    return result_ev

```
  
---|---  
###  aggregate_tool_results `async` #
```
aggregate_tool_results(ctx: Context, ev: ToolCallResult) -> Union[AgentInput, StopEvent, None]

```

Aggregate tool results and return the next agent input.
Source code in `llama-index-core/llama_index/core/agent/workflow/base_agent.py`

| ```
@step
async def aggregate_tool_results(
    self, ctx: Context, ev: ToolCallResult
) -> Union[AgentInput, StopEvent, None]:
    """Aggregate tool results and return the next agent input."""
    num_tool_calls = await ctx.store.get("num_tool_calls", default=0)
    if num_tool_calls == 0:
        raise ValueError("No tool calls found, cannot aggregate results.")

    tool_call_results: list[ToolCallResult] = ctx.collect_events(  # type: ignore
        ev, expected=[ToolCallResult] * num_tool_calls
    )
    if not tool_call_results:
        return None

    memory: BaseMemory = await ctx.store.get("memory")

    # track tool calls made during a .run() call
    cur_tool_calls: List[ToolCallResult] = await ctx.store.get(
        "current_tool_calls", default=[]
    )
    cur_tool_calls.extend(tool_call_results)
    await ctx.store.set("current_tool_calls", cur_tool_calls)

    await self.handle_tool_call_results(ctx, tool_call_results, memory)

    if any(
        tool_call_result.return_direct for tool_call_result in tool_call_results
    ):
        # if any tool calls return directly, take the first one
        return_direct_tool = next(
            tool_call_result
            for tool_call_result in tool_call_results
            if tool_call_result.return_direct
        )

        # always finalize the agent, even if we're just handing off
        result = AgentOutput(
            response=ChatMessage(
                role="assistant",
                content=return_direct_tool.tool_output.content or "",
            ),
            tool_calls=[
                ToolSelection(
                    tool_id=t.tool_id,
                    tool_name=t.tool_name,
                    tool_kwargs=t.tool_kwargs,
                )
                for t in cur_tool_calls
            ],
            raw=return_direct_tool.tool_output.raw_output,
            current_agent_name=self.name,
        )
        result = await self.finalize(ctx, result, memory)

    user_msg_str = await ctx.store.get("user_msg_str")
    input_messages = await memory.aget(input=user_msg_str)

    return AgentInput(input=input_messages, current_agent_name=self.name)

```
  
---|---  
##  FunctionAgent #
Bases: `BaseWorkflowAgent`
Function calling agent implementation.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`scratchpad_key` |  `str` |  |  `'scratchpad'`  
`allow_parallel_tool_calls` |  `bool` |  If True, the agent will call multiple tools in parallel. If False, the agent will call tools sequentially. |  `True`  
Source code in `llama-index-core/llama_index/core/agent/workflow/function_agent.py`

| ```
class FunctionAgent(BaseWorkflowAgent):
    """Function calling agent implementation."""

    scratchpad_key: str = "scratchpad"
    allow_parallel_tool_calls: bool = Field(
        default=True,
        description="If True, the agent will call multiple tools in parallel. If False, the agent will call tools sequentially.",
    )

    async def take_step(
        self,
        ctx: Context,
        llm_input: List[ChatMessage],
        tools: Sequence[AsyncBaseTool],
        memory: BaseMemory,
    ) -> AgentOutput:
        """Take a single step with the function calling agent."""
        if not self.llm.metadata.is_function_calling_model:
            raise ValueError("LLM must be a FunctionCallingLLM")

        scratchpad: List[ChatMessage] = await ctx.store.get(
            self.scratchpad_key, default=[]
        )
        current_llm_input = [*llm_input, *scratchpad]

        ctx.write_event_to_stream(
            AgentInput(input=current_llm_input, current_agent_name=self.name)
        )

        response = await self.llm.astream_chat_with_tools(  # type: ignore
            tools=tools,
            chat_history=current_llm_input,
            allow_parallel_tool_calls=self.allow_parallel_tool_calls,
        )
        # last_chat_response will be used later, after the loop.
        # We initialize it so it's valid even when 'response' is empty
        last_chat_response = ChatResponse(message=ChatMessage())
        async for last_chat_response in response:
            tool_calls = self.llm.get_tool_calls_from_response(  # type: ignore
                last_chat_response, error_on_no_tool_call=False
            )
            raw = (
                last_chat_response.raw.model_dump()
                if isinstance(last_chat_response.raw, BaseModel)
                else last_chat_response.raw
            )
            ctx.write_event_to_stream(
                AgentStream(
                    delta=last_chat_response.delta or "",
                    response=last_chat_response.message.content or "",
                    tool_calls=tool_calls or [],
                    raw=raw,
                    current_agent_name=self.name,
                )
            )

        tool_calls = self.llm.get_tool_calls_from_response(  # type: ignore
            last_chat_response, error_on_no_tool_call=False
        )

        # only add to scratchpad if we didn't select the handoff tool
        scratchpad.append(last_chat_response.message)
        await ctx.store.set(self.scratchpad_key, scratchpad)

        raw = (
            last_chat_response.raw.model_dump()
            if isinstance(last_chat_response.raw, BaseModel)
            else last_chat_response.raw
        )
        return AgentOutput(
            response=last_chat_response.message,
            tool_calls=tool_calls or [],
            raw=raw,
            current_agent_name=self.name,
        )

    async def handle_tool_call_results(
        self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
    ) -> None:
        """Handle tool call results for function calling agent."""
        scratchpad: List[ChatMessage] = await ctx.store.get(
            self.scratchpad_key, default=[]
        )

        for tool_call_result in results:
            scratchpad.append(
                ChatMessage(
                    role="tool",
                    blocks=tool_call_result.tool_output.blocks,
                    additional_kwargs={"tool_call_id": tool_call_result.tool_id},
                )
            )

            if (
                tool_call_result.return_direct
                and tool_call_result.tool_name != "handoff"
            ):
                scratchpad.append(
                    ChatMessage(
                        role="assistant",
                        content=str(tool_call_result.tool_output.content),
                        additional_kwargs={"tool_call_id": tool_call_result.tool_id},
                    )
                )
                break

        await ctx.store.set(self.scratchpad_key, scratchpad)

    async def finalize(
        self, ctx: Context, output: AgentOutput, memory: BaseMemory
    ) -> AgentOutput:
        """
        Finalize the function calling agent.

        Adds all in-progress messages to memory.
        """
        scratchpad: List[ChatMessage] = await ctx.store.get(
            self.scratchpad_key, default=[]
        )
        await memory.aput_messages(scratchpad)

        # reset scratchpad
        await ctx.store.set(self.scratchpad_key, [])

        return output

```
  
---|---  
###  take_step `async` #
```
take_step(ctx: Context, llm_input: List[ChatMessage], tools: Sequence[AsyncBaseTool], memory: BaseMemory) -> AgentOutput

```

Take a single step with the function calling agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/function_agent.py`

| ```
async def take_step(
    self,
    ctx: Context,
    llm_input: List[ChatMessage],
    tools: Sequence[AsyncBaseTool],
    memory: BaseMemory,
) -> AgentOutput:
    """Take a single step with the function calling agent."""
    if not self.llm.metadata.is_function_calling_model:
        raise ValueError("LLM must be a FunctionCallingLLM")

    scratchpad: List[ChatMessage] = await ctx.store.get(
        self.scratchpad_key, default=[]
    )
    current_llm_input = [*llm_input, *scratchpad]

    ctx.write_event_to_stream(
        AgentInput(input=current_llm_input, current_agent_name=self.name)
    )

    response = await self.llm.astream_chat_with_tools(  # type: ignore
        tools=tools,
        chat_history=current_llm_input,
        allow_parallel_tool_calls=self.allow_parallel_tool_calls,
    )
    # last_chat_response will be used later, after the loop.
    # We initialize it so it's valid even when 'response' is empty
    last_chat_response = ChatResponse(message=ChatMessage())
    async for last_chat_response in response:
        tool_calls = self.llm.get_tool_calls_from_response(  # type: ignore
            last_chat_response, error_on_no_tool_call=False
        )
        raw = (
            last_chat_response.raw.model_dump()
            if isinstance(last_chat_response.raw, BaseModel)
            else last_chat_response.raw
        )
        ctx.write_event_to_stream(
            AgentStream(
                delta=last_chat_response.delta or "",
                response=last_chat_response.message.content or "",
                tool_calls=tool_calls or [],
                raw=raw,
                current_agent_name=self.name,
            )
        )

    tool_calls = self.llm.get_tool_calls_from_response(  # type: ignore
        last_chat_response, error_on_no_tool_call=False
    )

    # only add to scratchpad if we didn't select the handoff tool
    scratchpad.append(last_chat_response.message)
    await ctx.store.set(self.scratchpad_key, scratchpad)

    raw = (
        last_chat_response.raw.model_dump()
        if isinstance(last_chat_response.raw, BaseModel)
        else last_chat_response.raw
    )
    return AgentOutput(
        response=last_chat_response.message,
        tool_calls=tool_calls or [],
        raw=raw,
        current_agent_name=self.name,
    )

```
  
---|---  
###  handle_tool_call_results `async` #
```
handle_tool_call_results(ctx: Context, results: List[ToolCallResult], memory: BaseMemory) -> None

```

Handle tool call results for function calling agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/function_agent.py`

| ```
async def handle_tool_call_results(
    self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
) -> None:
    """Handle tool call results for function calling agent."""
    scratchpad: List[ChatMessage] = await ctx.store.get(
        self.scratchpad_key, default=[]
    )

    for tool_call_result in results:
        scratchpad.append(
            ChatMessage(
                role="tool",
                blocks=tool_call_result.tool_output.blocks,
                additional_kwargs={"tool_call_id": tool_call_result.tool_id},
            )
        )

        if (
            tool_call_result.return_direct
            and tool_call_result.tool_name != "handoff"
        ):
            scratchpad.append(
                ChatMessage(
                    role="assistant",
                    content=str(tool_call_result.tool_output.content),
                    additional_kwargs={"tool_call_id": tool_call_result.tool_id},
                )
            )
            break

    await ctx.store.set(self.scratchpad_key, scratchpad)

```
  
---|---  
###  finalize `async` #
```
finalize(ctx: Context, output: AgentOutput, memory: BaseMemory) -> AgentOutput

```

Finalize the function calling agent.
Adds all in-progress messages to memory.
Source code in `llama-index-core/llama_index/core/agent/workflow/function_agent.py`

| ```
async def finalize(
    self, ctx: Context, output: AgentOutput, memory: BaseMemory
) -> AgentOutput:
    """
    Finalize the function calling agent.

    Adds all in-progress messages to memory.
    """
    scratchpad: List[ChatMessage] = await ctx.store.get(
        self.scratchpad_key, default=[]
    )
    await memory.aput_messages(scratchpad)

    # reset scratchpad
    await ctx.store.set(self.scratchpad_key, [])

    return output

```
  
---|---  
##  ReActAgent #
Bases: `BaseWorkflowAgent`
React agent implementation.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`reasoning_key` |  `str` |  |  `'current_reasoning'`  
`output_parser` |  `ReActOutputParser` |  The react output parser |  `<llama_index.core.agent.react.output_parser.ReActOutputParser object at 0x7059fb1bb410>`  
`formatter` |  `ReActChatFormatter` |  The react chat formatter to format the reasoning steps and chat history into an llm input. |  `<dynamic>`  
Source code in `llama-index-core/llama_index/core/agent/workflow/react_agent.py`

| ```
class ReActAgent(BaseWorkflowAgent):
    """React agent implementation."""

    reasoning_key: str = "current_reasoning"
    output_parser: ReActOutputParser = Field(
        default_factory=ReActOutputParser, description="The react output parser"
    )
    formatter: ReActChatFormatter = Field(
        default_factory=default_formatter,
        description="The react chat formatter to format the reasoning steps and chat history into an llm input.",
    )

    @model_validator(mode="after")
    def validate_formatter(self) -> "ReActAgent":
        """Validate the formatter."""
        if (
            self.formatter.context
            and self.system_prompt
            and self.system_prompt not in self.formatter.context
        ):
            self.formatter.context = (
                self.system_prompt + "\n\n" + self.formatter.context.strip()
            )
        elif not self.formatter.context and self.system_prompt:
            self.formatter.context = self.system_prompt

        return self

    def _get_prompts(self) -> PromptDictType:
        """Get prompts."""
        # TODO: the ReAct formatter does not explicitly specify PromptTemplate
        # objects, but wrap it in this to obey the interface
        react_header = self.formatter.system_header
        return {"react_header": PromptTemplate(react_header)}

    def _update_prompts(self, prompts: PromptDictType) -> None:
        """Update prompts."""
        if "react_header" in prompts:
            react_header = prompts["react_header"]
            if isinstance(react_header, str):
                react_header = PromptTemplate(react_header)
            self.formatter.system_header = react_header.get_template()

    async def take_step(
        self,
        ctx: Context,
        llm_input: List[ChatMessage],
        tools: Sequence[AsyncBaseTool],
        memory: BaseMemory,
    ) -> AgentOutput:
        """Take a single step with the React agent."""
        # remove system prompt, since the react prompt will be combined with it
        if llm_input[0].role == "system":
            system_prompt = llm_input[0].content or ""
            llm_input = llm_input[1:]
        else:
            system_prompt = ""

        output_parser = self.output_parser
        react_chat_formatter = self.formatter

        # Format initial chat input
        current_reasoning: list[BaseReasoningStep] = await ctx.store.get(
            self.reasoning_key, default=[]
        )
        input_chat = react_chat_formatter.format(
            tools,
            chat_history=llm_input,
            current_reasoning=current_reasoning,
        )
        ctx.write_event_to_stream(
            AgentInput(input=input_chat, current_agent_name=self.name)
        )

        # Initial LLM call
        response = await self.llm.astream_chat(input_chat)
        # last_chat_response will be used later, after the loop.
        # We initialize it so it's valid even when 'response' is empty
        last_chat_response = ChatResponse(message=ChatMessage())
        async for last_chat_response in response:
            raw = (
                last_chat_response.raw.model_dump()
                if isinstance(last_chat_response.raw, BaseModel)
                else last_chat_response.raw
            )
            ctx.write_event_to_stream(
                AgentStream(
                    delta=last_chat_response.delta or "",
                    response=last_chat_response.message.content or "",
                    tool_calls=[],
                    raw=raw,
                    current_agent_name=self.name,
                )
            )

        # Parse reasoning step and check if done
        message_content = last_chat_response.message.content
        if not message_content:
            raise ValueError("Got empty message")

        try:
            reasoning_step = output_parser.parse(message_content, is_streaming=False)
        except ValueError as e:
            error_msg = f"Error: Could not parse output. Please follow the thought-action-input format. Try again. Details: {e!s}"
            await memory.aput(last_chat_response.message)
            await memory.aput(ChatMessage(role="user", content=error_msg))

            raw = (
                last_chat_response.raw.model_dump()
                if isinstance(last_chat_response.raw, BaseModel)
                else last_chat_response.raw
            )
            return AgentOutput(
                response=last_chat_response.message,
                tool_calls=[],
                raw=raw,
                current_agent_name=self.name,
            )

        # add to reasoning if not a handoff
        current_reasoning.append(reasoning_step)
        await ctx.store.set(self.reasoning_key, current_reasoning)

        # If response step, we're done
        raw = (
            last_chat_response.raw.model_dump()
            if isinstance(last_chat_response.raw, BaseModel)
            else last_chat_response.raw
        )
        if reasoning_step.is_done:
            return AgentOutput(
                response=last_chat_response.message,
                tool_calls=[],
                raw=raw,
                current_agent_name=self.name,
            )

        reasoning_step = cast(ActionReasoningStep, reasoning_step)
        if not isinstance(reasoning_step, ActionReasoningStep):
            raise ValueError(f"Expected ActionReasoningStep, got {reasoning_step}")

        # Create tool call
        tool_calls = [
            ToolSelection(
                tool_id=str(uuid.uuid4()),
                tool_name=reasoning_step.action,
                tool_kwargs=reasoning_step.action_input,
            )
        ]

        return AgentOutput(
            response=last_chat_response.message,
            tool_calls=tool_calls,
            raw=raw,
            current_agent_name=self.name,
        )

    async def handle_tool_call_results(
        self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
    ) -> None:
        """Handle tool call results for React agent."""
        current_reasoning: list[BaseReasoningStep] = await ctx.store.get(
            self.reasoning_key, default=[]
        )
        for tool_call_result in results:
            obs_step = ObservationReasoningStep(
                observation=str(tool_call_result.tool_output.content),
                return_direct=tool_call_result.return_direct,
            )
            current_reasoning.append(obs_step)

            if (
                tool_call_result.return_direct
                and tool_call_result.tool_name != "handoff"
            ):
                current_reasoning.append(
                    ResponseReasoningStep(
                        thought=obs_step.observation,
                        response=obs_step.observation,
                        is_streaming=False,
                    )
                )
                break

        await ctx.store.set(self.reasoning_key, current_reasoning)

    async def finalize(
        self, ctx: Context, output: AgentOutput, memory: BaseMemory
    ) -> AgentOutput:
        """Finalize the React agent."""
        current_reasoning: list[BaseReasoningStep] = await ctx.store.get(
            self.reasoning_key, default=[]
        )

        if len(current_reasoning) > 0 and isinstance(
            current_reasoning[-1], ResponseReasoningStep
        ):
            reasoning_str = "\n".join([x.get_content() for x in current_reasoning])

            if reasoning_str:
                reasoning_msg = ChatMessage(role="assistant", content=reasoning_str)
                await memory.aput(reasoning_msg)
                await ctx.store.set(self.reasoning_key, [])

            # remove "Answer:" from the response
            if output.response.content and "Answer:" in output.response.content:
                start_idx = output.response.content.find("Answer:")
                if start_idx != -1:
                    output.response.content = output.response.content[
                        start_idx + len("Answer:") :
                    ].strip()

            # clear scratchpad
            await ctx.store.set(self.reasoning_key, [])

        return output

```
  
---|---  
###  validate_formatter #
```
validate_formatter() -> ReActAgent

```

Validate the formatter.
Source code in `llama-index-core/llama_index/core/agent/workflow/react_agent.py`

| ```
@model_validator(mode="after")
def validate_formatter(self) -> "ReActAgent":
    """Validate the formatter."""
    if (
        self.formatter.context
        and self.system_prompt
        and self.system_prompt not in self.formatter.context
    ):
        self.formatter.context = (
            self.system_prompt + "\n\n" + self.formatter.context.strip()
        )
    elif not self.formatter.context and self.system_prompt:
        self.formatter.context = self.system_prompt

    return self

```
  
---|---  
###  take_step `async` #
```
take_step(ctx: Context, llm_input: List[ChatMessage], tools: Sequence[AsyncBaseTool], memory: BaseMemory) -> AgentOutput

```

Take a single step with the React agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/react_agent.py`

| ```
async def take_step(
    self,
    ctx: Context,
    llm_input: List[ChatMessage],
    tools: Sequence[AsyncBaseTool],
    memory: BaseMemory,
) -> AgentOutput:
    """Take a single step with the React agent."""
    # remove system prompt, since the react prompt will be combined with it
    if llm_input[0].role == "system":
        system_prompt = llm_input[0].content or ""
        llm_input = llm_input[1:]
    else:
        system_prompt = ""

    output_parser = self.output_parser
    react_chat_formatter = self.formatter

    # Format initial chat input
    current_reasoning: list[BaseReasoningStep] = await ctx.store.get(
        self.reasoning_key, default=[]
    )
    input_chat = react_chat_formatter.format(
        tools,
        chat_history=llm_input,
        current_reasoning=current_reasoning,
    )
    ctx.write_event_to_stream(
        AgentInput(input=input_chat, current_agent_name=self.name)
    )

    # Initial LLM call
    response = await self.llm.astream_chat(input_chat)
    # last_chat_response will be used later, after the loop.
    # We initialize it so it's valid even when 'response' is empty
    last_chat_response = ChatResponse(message=ChatMessage())
    async for last_chat_response in response:
        raw = (
            last_chat_response.raw.model_dump()
            if isinstance(last_chat_response.raw, BaseModel)
            else last_chat_response.raw
        )
        ctx.write_event_to_stream(
            AgentStream(
                delta=last_chat_response.delta or "",
                response=last_chat_response.message.content or "",
                tool_calls=[],
                raw=raw,
                current_agent_name=self.name,
            )
        )

    # Parse reasoning step and check if done
    message_content = last_chat_response.message.content
    if not message_content:
        raise ValueError("Got empty message")

    try:
        reasoning_step = output_parser.parse(message_content, is_streaming=False)
    except ValueError as e:
        error_msg = f"Error: Could not parse output. Please follow the thought-action-input format. Try again. Details: {e!s}"
        await memory.aput(last_chat_response.message)
        await memory.aput(ChatMessage(role="user", content=error_msg))

        raw = (
            last_chat_response.raw.model_dump()
            if isinstance(last_chat_response.raw, BaseModel)
            else last_chat_response.raw
        )
        return AgentOutput(
            response=last_chat_response.message,
            tool_calls=[],
            raw=raw,
            current_agent_name=self.name,
        )

    # add to reasoning if not a handoff
    current_reasoning.append(reasoning_step)
    await ctx.store.set(self.reasoning_key, current_reasoning)

    # If response step, we're done
    raw = (
        last_chat_response.raw.model_dump()
        if isinstance(last_chat_response.raw, BaseModel)
        else last_chat_response.raw
    )
    if reasoning_step.is_done:
        return AgentOutput(
            response=last_chat_response.message,
            tool_calls=[],
            raw=raw,
            current_agent_name=self.name,
        )

    reasoning_step = cast(ActionReasoningStep, reasoning_step)
    if not isinstance(reasoning_step, ActionReasoningStep):
        raise ValueError(f"Expected ActionReasoningStep, got {reasoning_step}")

    # Create tool call
    tool_calls = [
        ToolSelection(
            tool_id=str(uuid.uuid4()),
            tool_name=reasoning_step.action,
            tool_kwargs=reasoning_step.action_input,
        )
    ]

    return AgentOutput(
        response=last_chat_response.message,
        tool_calls=tool_calls,
        raw=raw,
        current_agent_name=self.name,
    )

```
  
---|---  
###  handle_tool_call_results `async` #
```
handle_tool_call_results(ctx: Context, results: List[ToolCallResult], memory: BaseMemory) -> None

```

Handle tool call results for React agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/react_agent.py`

| ```
async def handle_tool_call_results(
    self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
) -> None:
    """Handle tool call results for React agent."""
    current_reasoning: list[BaseReasoningStep] = await ctx.store.get(
        self.reasoning_key, default=[]
    )
    for tool_call_result in results:
        obs_step = ObservationReasoningStep(
            observation=str(tool_call_result.tool_output.content),
            return_direct=tool_call_result.return_direct,
        )
        current_reasoning.append(obs_step)

        if (
            tool_call_result.return_direct
            and tool_call_result.tool_name != "handoff"
        ):
            current_reasoning.append(
                ResponseReasoningStep(
                    thought=obs_step.observation,
                    response=obs_step.observation,
                    is_streaming=False,
                )
            )
            break

    await ctx.store.set(self.reasoning_key, current_reasoning)

```
  
---|---  
###  finalize `async` #
```
finalize(ctx: Context, output: AgentOutput, memory: BaseMemory) -> AgentOutput

```

Finalize the React agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/react_agent.py`

| ```
async def finalize(
    self, ctx: Context, output: AgentOutput, memory: BaseMemory
) -> AgentOutput:
    """Finalize the React agent."""
    current_reasoning: list[BaseReasoningStep] = await ctx.store.get(
        self.reasoning_key, default=[]
    )

    if len(current_reasoning) > 0 and isinstance(
        current_reasoning[-1], ResponseReasoningStep
    ):
        reasoning_str = "\n".join([x.get_content() for x in current_reasoning])

        if reasoning_str:
            reasoning_msg = ChatMessage(role="assistant", content=reasoning_str)
            await memory.aput(reasoning_msg)
            await ctx.store.set(self.reasoning_key, [])

        # remove "Answer:" from the response
        if output.response.content and "Answer:" in output.response.content:
            start_idx = output.response.content.find("Answer:")
            if start_idx != -1:
                output.response.content = output.response.content[
                    start_idx + len("Answer:") :
                ].strip()

        # clear scratchpad
        await ctx.store.set(self.reasoning_key, [])

    return output

```
  
---|---  
##  CodeActAgent #
Bases: `BaseWorkflowAgent`
A workflow agent that can execute code.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`scratchpad_key` |  `str` |  |  `'scratchpad'`  
`code_execute_fn` |  `Callable | Awaitable` |  The function to execute code. Required in order to execute code generated by the agent. The function protocol is as follows: async def code_execute_fn(code: str) -> Dict[str, Any] |  _required_  
`code_act_system_prompt` |  `str | BasePromptTemplate` |  The system prompt for the code act agent. |  `'You are a helpful AI assistant that can write and execute Python code to solve problems.\n\nYou will be given a task to perform. You should output:\n- Python code wrapped in <execute>...</execute> tags that provides the solution to the task, or a step towards the solution. Any output you want to extract from the code should be printed to the console.\n- Text to be shown directly to the user, if you want to ask for more information or provide the final answer.\n- If the previous code execution can be used to respond to the user, then respond directly (typically you want to avoid mentioning anything related to the code execution in your response).\n\n## Response Format:\nExample of proper code format:\n<execute>\nimport math\n\ndef calculate_area(radius):\n    return math.pi * radius**2\n\n# Calculate the area for radius = 5\narea = calculate_area(5)\nprint(f"The area of the circle is {area:.2f} square units")\n</execute>\n\nIn addition to the Python Standard Library and any functions you have already written, you can use the following functions:\n{tool_descriptions}\n\nVariables defined at the top level of previous code snippets can be also be referenced in your code.\n\n## Final Answer Guidelines:\n- When providing a final answer, focus on directly answering the user\'s question\n- Avoid referencing the code you generated unless specifically asked\n- Present the results clearly and concisely as if you computed them directly\n- If relevant, you can briefly mention general methods used, but don\'t include code snippets in the final answer\n- Structure your response like you\'re directly answering the user\'s query, not explaining how you solved it\n\nReminder: Always place your Python code between <execute>...</execute> tags when you want to run code. You can include explanations and other content outside these tags.\n'`  
Source code in `llama-index-core/llama_index/core/agent/workflow/codeact_agent.py`

| ```
class CodeActAgent(BaseWorkflowAgent):
    """
    A workflow agent that can execute code.
    """

    scratchpad_key: str = "scratchpad"

    code_execute_fn: Union[Callable, Awaitable] = Field(
        description=(
            "The function to execute code. Required in order to execute code generated by the agent.\n"
            "The function protocol is as follows: async def code_execute_fn(code: str) -> Dict[str, Any]"
        ),
    )

    code_act_system_prompt: Union[str, BasePromptTemplate] = Field(
        default=DEFAULT_CODE_ACT_PROMPT,
        description="The system prompt for the code act agent.",
        validate_default=True,
    )

    def __init__(
        self,
        code_execute_fn: Union[Callable, Awaitable],
        name: str = "code_act_agent",
        description: str = "A workflow agent that can execute code.",
        system_prompt: Optional[str] = None,
        tools: Optional[List[Union[BaseTool, Callable]]] = None,
        tool_retriever: Optional[ObjectRetriever] = None,
        can_handoff_to: Optional[List[str]] = None,
        llm: Optional[LLM] = None,
        code_act_system_prompt: Union[
            str, BasePromptTemplate
        ] = DEFAULT_CODE_ACT_PROMPT,
    ):
        tools = tools or []
        tools.append(  # type: ignore
            FunctionTool.from_defaults(code_execute_fn, name=EXECUTE_TOOL_NAME)  # type: ignore
        )
        if isinstance(code_act_system_prompt, str):
            if system_prompt:
                code_act_system_prompt += "\n" + system_prompt
            code_act_system_prompt = PromptTemplate(code_act_system_prompt)
        elif isinstance(code_act_system_prompt, BasePromptTemplate):
            if system_prompt:
                code_act_system_str = code_act_system_prompt.get_template()
                code_act_system_str += "\n" + system_prompt
            code_act_system_prompt = PromptTemplate(code_act_system_str)

        super().__init__(
            name=name,
            description=description,
            system_prompt=system_prompt,
            tools=tools,
            tool_retriever=tool_retriever,
            can_handoff_to=can_handoff_to,
            llm=llm,
            code_act_system_prompt=code_act_system_prompt,
            code_execute_fn=code_execute_fn,
        )

    def _get_tool_fns(self, tools: Sequence[BaseTool]) -> List[Callable]:
        """Get the tool functions while validating that they are valid tools for the CodeActAgent."""
        callables = []
        for tool in tools:
            if (
                tool.metadata.name == "handoff"
                or tool.metadata.name == EXECUTE_TOOL_NAME
            ):
                continue

            if isinstance(tool, FunctionTool):
                if tool.requires_context:
                    raise ValueError(
                        f"Tool {tool.metadata.name} requires context. "
                        "CodeActAgent only supports tools that do not require context."
                    )

                callables.append(tool.real_fn)
            else:
                raise ValueError(
                    f"Tool {tool.metadata.name} is not a FunctionTool. "
                    "CodeActAgent only supports Functions and FunctionTools."
                )

        return callables

    def _extract_code_from_response(self, response_text: str) -> Optional[str]:
        """
        Extract code from the LLM response using XML-style <execute> tags.

        Args:
            response_text: The LLM response text

        Returns:
            Extracted code or None if no code found

        """
        # Match content between <execute> and </execute> tags
        execute_pattern = r"<execute>(.*?)</execute>"
        execute_matches = re.findall(execute_pattern, response_text, re.DOTALL)

        if execute_matches:
            return "\n\n".join([x.strip() for x in execute_matches])

        return None

    def _get_tool_descriptions(self, tools: Sequence[BaseTool]) -> str:
        """
        Generate tool descriptions for the system prompt using tool metadata.

        Args:
            tools: List of available tools

        Returns:
            Tool descriptions as a string

        """
        tool_descriptions = []

        tool_fns = self._get_tool_fns(tools)
        for fn in tool_fns:
            signature = inspect.signature(fn)
            fn_name: str = fn.__name__
            docstring: Optional[str] = inspect.getdoc(fn)

            tool_description = f"def {fn_name}{signature!s}:"
            if docstring:
                tool_description += f'\n  """\n{docstring}\n  """\n'

            tool_description += "\n  ...\n"
            tool_descriptions.append(tool_description)

        return "\n\n".join(tool_descriptions)

    async def take_step(
        self,
        ctx: Context,
        llm_input: List[ChatMessage],
        tools: Sequence[BaseTool],
        memory: BaseMemory,
    ) -> AgentOutput:
        """Take a single step with the code act agent."""
        if not self.code_execute_fn:
            raise ValueError("code_execute_fn must be provided for CodeActAgent")

        # Get current scratchpad
        scratchpad: List[ChatMessage] = await ctx.store.get(
            self.scratchpad_key, default=[]
        )
        current_llm_input = [*llm_input, *scratchpad]

        # Create a system message with tool descriptions
        tool_descriptions = self._get_tool_descriptions(tools)
        system_prompt = self.code_act_system_prompt.format(
            tool_descriptions=tool_descriptions
        )

        # Add or overwrite system message
        has_system = False
        for i, msg in enumerate(current_llm_input):
            if msg.role.value == "system":
                current_llm_input[i] = ChatMessage(role="system", content=system_prompt)
                has_system = True
                break

        if not has_system:
            current_llm_input.insert(
                0, ChatMessage(role="system", content=system_prompt)
            )

        # Write the input to the event stream
        ctx.write_event_to_stream(
            AgentInput(input=current_llm_input, current_agent_name=self.name)
        )

        # For now, only support the handoff tool
        # All other tools should be part of the code execution
        if any(tool.metadata.name == "handoff" for tool in tools):
            if not isinstance(self.llm, FunctionCallingLLM):
                raise ValueError("llm must be a function calling LLM to use handoff")

            tools = [tool for tool in tools if tool.metadata.name == "handoff"]
            response = await self.llm.astream_chat_with_tools(
                tools, chat_history=current_llm_input
            )
        else:
            response = await self.llm.astream_chat(current_llm_input)

        # Initialize for streaming
        last_chat_response = ChatResponse(message=ChatMessage())
        full_response_text = ""

        # Process streaming response
        async for last_chat_response in response:
            delta = last_chat_response.delta or ""
            full_response_text += delta

            # Create a raw object for the event stream
            raw = (
                last_chat_response.raw.model_dump()
                if isinstance(last_chat_response.raw, BaseModel)
                else last_chat_response.raw
            )

            # Write delta to the event stream
            ctx.write_event_to_stream(
                AgentStream(
                    delta=delta,
                    response=full_response_text,
                    # We'll add the tool call after processing the full response
                    tool_calls=[],
                    raw=raw,
                    current_agent_name=self.name,
                )
            )

        # Extract code from the response
        code = self._extract_code_from_response(full_response_text)

        # Create a tool call for executing the code if code was found
        tool_calls = []
        if code:
            tool_id = str(uuid.uuid4())

            tool_calls = [
                ToolSelection(
                    tool_id=tool_id,
                    tool_name=EXECUTE_TOOL_NAME,
                    tool_kwargs={"code": code},
                )
            ]

        if isinstance(self.llm, FunctionCallingLLM):
            extra_tool_calls = self.llm.get_tool_calls_from_response(
                last_chat_response, error_on_no_tool_call=False
            )
            tool_calls.extend(extra_tool_calls)

        # Add the response to the scratchpad
        message = ChatMessage(role="assistant", content=full_response_text)
        scratchpad.append(message)
        await ctx.store.set(self.scratchpad_key, scratchpad)

        # Create the raw object for the output
        raw = (
            last_chat_response.raw.model_dump()
            if isinstance(last_chat_response.raw, BaseModel)
            else last_chat_response.raw
        )

        return AgentOutput(
            response=message,
            tool_calls=tool_calls,
            raw=raw,
            current_agent_name=self.name,
        )

    async def handle_tool_call_results(
        self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
    ) -> None:
        """Handle tool call results for code act agent."""
        scratchpad: List[ChatMessage] = await ctx.store.get(
            self.scratchpad_key, default=[]
        )

        # handle code execution and handoff
        for tool_call_result in results:
            # Format the output as a tool response message
            if tool_call_result.tool_name == EXECUTE_TOOL_NAME:
                code_result = f"Result of executing the code given:\n\n{tool_call_result.tool_output.content}"
                scratchpad.append(
                    ChatMessage(
                        role="user",
                        content=code_result,
                    )
                )
            elif tool_call_result.tool_name == "handoff":
                scratchpad.append(
                    ChatMessage(
                        role="tool",
                        blocks=tool_call_result.tool_output.blocks,
                        additional_kwargs={"tool_call_id": tool_call_result.tool_id},
                    )
                )
            else:
                raise ValueError(f"Unknown tool name: {tool_call_result.tool_name}")

        await ctx.store.set(self.scratchpad_key, scratchpad)

    async def finalize(
        self, ctx: Context, output: AgentOutput, memory: BaseMemory
    ) -> AgentOutput:
        """
        Finalize the code act agent.

        Adds all in-progress messages to memory.
        """
        scratchpad: List[ChatMessage] = await ctx.store.get(
            self.scratchpad_key, default=[]
        )
        await memory.aput_messages(scratchpad)

        # reset scratchpad
        await ctx.store.set(self.scratchpad_key, [])

        return output

```
  
---|---  
###  take_step `async` #
```
take_step(ctx: Context, llm_input: List[ChatMessage], tools: Sequence[BaseTool], memory: BaseMemory) -> AgentOutput

```

Take a single step with the code act agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/codeact_agent.py`

| ```
async def take_step(
    self,
    ctx: Context,
    llm_input: List[ChatMessage],
    tools: Sequence[BaseTool],
    memory: BaseMemory,
) -> AgentOutput:
    """Take a single step with the code act agent."""
    if not self.code_execute_fn:
        raise ValueError("code_execute_fn must be provided for CodeActAgent")

    # Get current scratchpad
    scratchpad: List[ChatMessage] = await ctx.store.get(
        self.scratchpad_key, default=[]
    )
    current_llm_input = [*llm_input, *scratchpad]

    # Create a system message with tool descriptions
    tool_descriptions = self._get_tool_descriptions(tools)
    system_prompt = self.code_act_system_prompt.format(
        tool_descriptions=tool_descriptions
    )

    # Add or overwrite system message
    has_system = False
    for i, msg in enumerate(current_llm_input):
        if msg.role.value == "system":
            current_llm_input[i] = ChatMessage(role="system", content=system_prompt)
            has_system = True
            break

    if not has_system:
        current_llm_input.insert(
            0, ChatMessage(role="system", content=system_prompt)
        )

    # Write the input to the event stream
    ctx.write_event_to_stream(
        AgentInput(input=current_llm_input, current_agent_name=self.name)
    )

    # For now, only support the handoff tool
    # All other tools should be part of the code execution
    if any(tool.metadata.name == "handoff" for tool in tools):
        if not isinstance(self.llm, FunctionCallingLLM):
            raise ValueError("llm must be a function calling LLM to use handoff")

        tools = [tool for tool in tools if tool.metadata.name == "handoff"]
        response = await self.llm.astream_chat_with_tools(
            tools, chat_history=current_llm_input
        )
    else:
        response = await self.llm.astream_chat(current_llm_input)

    # Initialize for streaming
    last_chat_response = ChatResponse(message=ChatMessage())
    full_response_text = ""

    # Process streaming response
    async for last_chat_response in response:
        delta = last_chat_response.delta or ""
        full_response_text += delta

        # Create a raw object for the event stream
        raw = (
            last_chat_response.raw.model_dump()
            if isinstance(last_chat_response.raw, BaseModel)
            else last_chat_response.raw
        )

        # Write delta to the event stream
        ctx.write_event_to_stream(
            AgentStream(
                delta=delta,
                response=full_response_text,
                # We'll add the tool call after processing the full response
                tool_calls=[],
                raw=raw,
                current_agent_name=self.name,
            )
        )

    # Extract code from the response
    code = self._extract_code_from_response(full_response_text)

    # Create a tool call for executing the code if code was found
    tool_calls = []
    if code:
        tool_id = str(uuid.uuid4())

        tool_calls = [
            ToolSelection(
                tool_id=tool_id,
                tool_name=EXECUTE_TOOL_NAME,
                tool_kwargs={"code": code},
            )
        ]

    if isinstance(self.llm, FunctionCallingLLM):
        extra_tool_calls = self.llm.get_tool_calls_from_response(
            last_chat_response, error_on_no_tool_call=False
        )
        tool_calls.extend(extra_tool_calls)

    # Add the response to the scratchpad
    message = ChatMessage(role="assistant", content=full_response_text)
    scratchpad.append(message)
    await ctx.store.set(self.scratchpad_key, scratchpad)

    # Create the raw object for the output
    raw = (
        last_chat_response.raw.model_dump()
        if isinstance(last_chat_response.raw, BaseModel)
        else last_chat_response.raw
    )

    return AgentOutput(
        response=message,
        tool_calls=tool_calls,
        raw=raw,
        current_agent_name=self.name,
    )

```
  
---|---  
###  handle_tool_call_results `async` #
```
handle_tool_call_results(ctx: Context, results: List[ToolCallResult], memory: BaseMemory) -> None

```

Handle tool call results for code act agent.
Source code in `llama-index-core/llama_index/core/agent/workflow/codeact_agent.py`

| ```
async def handle_tool_call_results(
    self, ctx: Context, results: List[ToolCallResult], memory: BaseMemory
) -> None:
    """Handle tool call results for code act agent."""
    scratchpad: List[ChatMessage] = await ctx.store.get(
        self.scratchpad_key, default=[]
    )

    # handle code execution and handoff
    for tool_call_result in results:
        # Format the output as a tool response message
        if tool_call_result.tool_name == EXECUTE_TOOL_NAME:
            code_result = f"Result of executing the code given:\n\n{tool_call_result.tool_output.content}"
            scratchpad.append(
                ChatMessage(
                    role="user",
                    content=code_result,
                )
            )
        elif tool_call_result.tool_name == "handoff":
            scratchpad.append(
                ChatMessage(
                    role="tool",
                    blocks=tool_call_result.tool_output.blocks,
                    additional_kwargs={"tool_call_id": tool_call_result.tool_id},
                )
            )
        else:
            raise ValueError(f"Unknown tool name: {tool_call_result.tool_name}")

    await ctx.store.set(self.scratchpad_key, scratchpad)

```
  
---|---  
###  finalize `async` #
```
finalize(ctx: Context, output: AgentOutput, memory: BaseMemory) -> AgentOutput

```

Finalize the code act agent.
Adds all in-progress messages to memory.
Source code in `llama-index-core/llama_index/core/agent/workflow/codeact_agent.py`

| ```
async def finalize(
    self, ctx: Context, output: AgentOutput, memory: BaseMemory
) -> AgentOutput:
    """
    Finalize the code act agent.

    Adds all in-progress messages to memory.
    """
    scratchpad: List[ChatMessage] = await ctx.store.get(
        self.scratchpad_key, default=[]
    )
    await memory.aput_messages(scratchpad)

    # reset scratchpad
    await ctx.store.set(self.scratchpad_key, [])

    return output

```
  
---|---  
##  AgentInput #
Bases: `Event`
LLM input.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`input` |  `list[ChatMessage]` |  |  _required_  
`current_agent_name` |  `str` |  |  _required_  
Source code in `llama-index-core/llama_index/core/agent/workflow/workflow_events.py`

| ```
class AgentInput(Event):
    """LLM input."""

    input: list[ChatMessage]
    current_agent_name: str

```
  
---|---  
##  AgentStream #
Bases: `Event`
Agent stream.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`delta` |  `str` |  |  _required_  
`response` |  `str` |  |  _required_  
`current_agent_name` |  `str` |  |  _required_  
`tool_calls` |  `list[ToolSelection]` |  |  _required_  
`raw` |  `Any` |  |  _required_  
Source code in `llama-index-core/llama_index/core/agent/workflow/workflow_events.py`

| ```
class AgentStream(Event):
    """Agent stream."""

    delta: str
    response: str
    current_agent_name: str
    tool_calls: list[ToolSelection]
    raw: Optional[Any] = Field(default=None, exclude=True)

```
  
---|---  
##  AgentOutput #
Bases: `Event`
LLM output.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`response` |  `ChatMessage` |  |  _required_  
`tool_calls` |  `list[ToolSelection]` |  |  _required_  
`raw` |  `Any` |  |  _required_  
`current_agent_name` |  `str` |  |  _required_  
Source code in `llama-index-core/llama_index/core/agent/workflow/workflow_events.py`

| ```
class AgentOutput(Event):
    """LLM output."""

    response: ChatMessage
    tool_calls: list[ToolSelection]
    raw: Optional[Any] = Field(default=None, exclude=True)
    current_agent_name: str

    def __str__(self) -> str:
        return self.response.content or ""

```
  
---|---  
##  ToolCall #
Bases: `Event`
All tool calls are surfaced.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`tool_name` |  `str` |  |  _required_  
`tool_kwargs` |  `dict` |  |  _required_  
`tool_id` |  `str` |  |  _required_  
Source code in `llama-index-core/llama_index/core/agent/workflow/workflow_events.py`

| ```
class ToolCall(Event):
    """All tool calls are surfaced."""

    tool_name: str
    tool_kwargs: dict
    tool_id: str

```
  
---|---  
##  ToolCallResult #
Bases: `Event`
Tool call result.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`tool_name` |  `str` |  |  _required_  
`tool_kwargs` |  `dict` |  |  _required_  
`tool_id` |  `str` |  |  _required_  
`tool_output` |  `ToolOutput` |  |  _required_  
`return_direct` |  `bool` |  |  _required_  
Source code in `llama-index-core/llama_index/core/agent/workflow/workflow_events.py`

| ```
class ToolCallResult(Event):
    """Tool call result."""

    tool_name: str
    tool_kwargs: dict
    tool_id: str
    tool_output: ToolOutput
    return_direct: bool

```
  
---|---
