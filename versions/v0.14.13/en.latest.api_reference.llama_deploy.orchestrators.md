#  `orchestrators`#
##  BaseOrchestrator #
Bases: `ABC`
Base class for an orchestrator.
The general idea for an orchestrator is to manage the flow of messages between services.
Given some state, and task, figure out the next messages to publish. Then, once the messages are processed, update the state with the results.
Source code in `llama_deploy/orchestrators/base.py`

| ```
class BaseOrchestrator(ABC):
    """Base class for an orchestrator.

    The general idea for an orchestrator is to manage the flow of messages between services.

    Given some state, and task, figure out the next messages to publish. Then, once
    the messages are processed, update the state with the results.
    """

    @abstractmethod
    async def get_next_messages(
        self, task_def: TaskDefinition, state: Dict[str, Any]
    ) -> Tuple[List[QueueMessage], Dict[str, Any]]:
        """Get the next message to process. Returns the message and the new state."""
        ...

    @abstractmethod
    async def add_result_to_state(
        self, result: TaskResult, state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add the result of processing a message to the state. Returns the new state."""
        ...

```
  
---|---  
###  get_next_messages `abstractmethod` `async` #
```
get_next_messages(task_def: TaskDefinition, state: Dict[str, Any]) -> Tuple[List[QueueMessage], Dict[str, Any]]

```

Get the next message to process. Returns the message and the new state.
Source code in `llama_deploy/orchestrators/base.py`

| ```
@abstractmethod
async def get_next_messages(
    self, task_def: TaskDefinition, state: Dict[str, Any]
) -> Tuple[List[QueueMessage], Dict[str, Any]]:
    """Get the next message to process. Returns the message and the new state."""
    ...

```
  
---|---  
###  add_result_to_state `abstractmethod` `async` #
```
add_result_to_state(result: TaskResult, state: Dict[str, Any]) -> Dict[str, Any]

```

Add the result of processing a message to the state. Returns the new state.
Source code in `llama_deploy/orchestrators/base.py`

| ```
@abstractmethod
async def add_result_to_state(
    self, result: TaskResult, state: Dict[str, Any]
) -> Dict[str, Any]:
    """Add the result of processing a message to the state. Returns the new state."""
    ...

```
  
---|---  
##  SimpleOrchestrator #
Bases: `BaseOrchestrator`
A simple orchestrator that handles orchestration between a service and a user.
Currently, the final message is published to the `human` message queue for final processing.
Source code in `llama_deploy/orchestrators/simple.py`

| ```
class SimpleOrchestrator(BaseOrchestrator):
    """A simple orchestrator that handles orchestration between a service and a user.

    Currently, the final message is published to the `human` message queue for final processing.
    """

    def __init__(self, max_retries: int = 3, final_message_type: str = "human") -> None:
        self.max_retries = max_retries
        self.final_message_type = final_message_type

    async def get_next_messages(
        self, task_def: TaskDefinition, state: Dict[str, Any]
    ) -> Tuple[List[QueueMessage], Dict[str, Any]]:
        """Get the next message to process. Returns the message and the new state.

        Assumes the agent_id (i.e. the service name) is the destination for the next message.

        Runs the required service, then sends the result to the final message type.
        """

        destination_messages = []

        if task_def.agent_id is None:
            raise ValueError(
                "Task definition must have an agent_id specified as a service name"
            )

        if task_def.task_id not in state:
            state[task_def.task_id] = {}

        result_key = get_result_key(task_def.task_id)
        if state.get(result_key, None) is not None:
            result = state[result_key]
            if not isinstance(result, TaskResult):
                if isinstance(result, str):
                    result = TaskResult(**json.loads(result))
                elif isinstance(result, dict):
                    result = TaskResult(**result)
                else:
                    raise ValueError(f"Result must be a TaskResult, not {type(result)}")

            assert isinstance(result, TaskResult), "Result must be a TaskResult"

            if self.final_message_type is not None:
                destination = self.final_message_type

                destination_messages = [
                    QueueMessage(
                        type=destination,
                        action=ActionTypes.COMPLETED_TASK,
                        data=result.model_dump(),
                    )
                ]
        else:
            destination = task_def.agent_id
            destination_messages = [
                QueueMessage(
                    type=destination,
                    action=ActionTypes.NEW_TASK,
                    data=task_def.model_dump(),
                )
            ]

        return destination_messages, state

    async def add_result_to_state(
        self, result: TaskResult, state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add the result of processing a message to the state. Returns the new state."""

        # TODO: detect failures + retries
        cur_retries = state.get("retries", -1) + 1
        state["retries"] = cur_retries

        # add result to state
        state[get_result_key(result.task_id)] = result

        return state

```
  
---|---  
###  get_next_messages `async` #
```
get_next_messages(task_def: TaskDefinition, state: Dict[str, Any]) -> Tuple[List[QueueMessage], Dict[str, Any]]

```

Get the next message to process. Returns the message and the new state.
Assumes the agent_id (i.e. the service name) is the destination for the next message.
Runs the required service, then sends the result to the final message type.
Source code in `llama_deploy/orchestrators/simple.py`

| ```
async def get_next_messages(
    self, task_def: TaskDefinition, state: Dict[str, Any]
) -> Tuple[List[QueueMessage], Dict[str, Any]]:
    """Get the next message to process. Returns the message and the new state.

    Assumes the agent_id (i.e. the service name) is the destination for the next message.

    Runs the required service, then sends the result to the final message type.
    """

    destination_messages = []

    if task_def.agent_id is None:
        raise ValueError(
            "Task definition must have an agent_id specified as a service name"
        )

    if task_def.task_id not in state:
        state[task_def.task_id] = {}

    result_key = get_result_key(task_def.task_id)
    if state.get(result_key, None) is not None:
        result = state[result_key]
        if not isinstance(result, TaskResult):
            if isinstance(result, str):
                result = TaskResult(**json.loads(result))
            elif isinstance(result, dict):
                result = TaskResult(**result)
            else:
                raise ValueError(f"Result must be a TaskResult, not {type(result)}")

        assert isinstance(result, TaskResult), "Result must be a TaskResult"

        if self.final_message_type is not None:
            destination = self.final_message_type

            destination_messages = [
                QueueMessage(
                    type=destination,
                    action=ActionTypes.COMPLETED_TASK,
                    data=result.model_dump(),
                )
            ]
    else:
        destination = task_def.agent_id
        destination_messages = [
            QueueMessage(
                type=destination,
                action=ActionTypes.NEW_TASK,
                data=task_def.model_dump(),
            )
        ]

    return destination_messages, state

```
  
---|---  
###  add_result_to_state `async` #
```
add_result_to_state(result: TaskResult, state: Dict[str, Any]) -> Dict[str, Any]

```

Add the result of processing a message to the state. Returns the new state.
Source code in `llama_deploy/orchestrators/simple.py`

| ```
async def add_result_to_state(
    self, result: TaskResult, state: Dict[str, Any]
) -> Dict[str, Any]:
    """Add the result of processing a message to the state. Returns the new state."""

    # TODO: detect failures + retries
    cur_retries = state.get("retries", -1) + 1
    state["retries"] = cur_retries

    # add result to state
    state[get_result_key(result.task_id)] = result

    return state

```
  
---|---  
##  SimpleOrchestratorConfig #
Bases: `BaseSettings`
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`max_retries` |  `int` |  |  `3`  
`final_message_type` |  `str | None` |  |  `None`  
Source code in `llama_deploy/orchestrators/simple.py`

| ```
class SimpleOrchestratorConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SIMPLE_ORCHESTRATOR_")

    max_retries: int = 3
    final_message_type: Optional[str] = None

```
  
---|---
