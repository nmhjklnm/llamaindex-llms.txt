# Python SDK#
## Client#
The LlamaDeploy Python client.
The client is gives access to both the asyncio and non-asyncio APIs. To access the sync API just use methods of `client.sync`.
Example usage: 
```
from llama_deploy.client import Client

# Use the same client instance
c = Client()

async def an_async_function():
    status = await client.apiserver.status()

def normal_function():
    status = client.sync.apiserver.status()

```

Source code in `llama_deploy/client/client.py`

| ```
class Client(_BaseClient):
    """The LlamaDeploy Python client.

    The client is gives access to both the asyncio and non-asyncio APIs. To access the sync
    API just use methods of `client.sync`.

    Example usage:
```py
    from llama_deploy.client import Client

    # Use the same client instance
    c = Client()

    async def an_async_function():
        status = await client.apiserver.status()

    def normal_function():
        status = client.sync.apiserver.status()
```
    """

    @property
    def sync(self) -> "_SyncClient":
        """Returns the sync version of the client API."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return _SyncClient(**self.model_dump())

        msg = "You cannot use the sync client within an async event loop - just await the async methods directly."
        raise RuntimeError(msg)

    @property
    def apiserver(self) -> ApiServer:
        """Returns the ApiServer model."""
        return ApiServer(client=self, id="apiserver")

    @property
    def core(self) -> Core:
        """Returns the Core model."""
        return Core(client=self, id="core")

```
  
---|---  
##  sync `property` #
```
sync: _SyncClient

```

Returns the sync version of the client API.
##  apiserver `property` #
```
apiserver: ApiServer

```

Returns the ApiServer model.
##  core `property` #
```
core: Core

```

Returns the Core model.
## API Server functionalities#
##  SessionCollection #
Bases: `Collection`
A model representing a collection of session for a given deployment.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`deployment_id` |  `str` |  |  _required_  
Source code in `llama_deploy/client/models/apiserver.py`

| ```
class SessionCollection(Collection):
    """A model representing a collection of session for a given deployment."""

    deployment_id: str

    async def delete(self, session_id: str) -> None:
        """Deletes the session with the provided `session_id`.

        Args:
            session_id: The id of the session that will be removed

        Raises:
            HTTPException: If the session couldn't be found with the id provided.
        """
        delete_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/sessions/delete"

        await self.client.request(
            "POST",
            delete_url,
            params={"session_id": session_id},
            verify=not self.client.disable_ssl,
            timeout=self.client.timeout,
        )

    async def create(self) -> SessionDefinition:
        """"""
        create_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/sessions/create"

        r = await self.client.request(
            "POST",
            create_url,
            verify=not self.client.disable_ssl,
            timeout=self.client.timeout,
        )

        return SessionDefinition(**r.json())

    async def list(self) -> list[SessionDefinition]:
        """Returns a collection of all the sessions in the given deployment."""
        sessions_url = (
            f"{self.client.api_server_url}/deployments/{self.deployment_id}/sessions"
        )
        r = await self.client.request(
            "GET",
            sessions_url,
            verify=not self.client.disable_ssl,
            timeout=self.client.timeout,
        )

        return r.json()

```
  
---|---  
###  delete `async` #
```
delete(session_id: str) -> None

```

Deletes the session with the provided `session_id`.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`session_id` |  `str` |  The id of the session that will be removed |  _required_  
Raises:
Type | Description  
---|---  
`HTTPException` |  If the session couldn't be found with the id provided.  
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def delete(self, session_id: str) -> None:
    """Deletes the session with the provided `session_id`.

    Args:
        session_id: The id of the session that will be removed

    Raises:
        HTTPException: If the session couldn't be found with the id provided.
    """
    delete_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/sessions/delete"

    await self.client.request(
        "POST",
        delete_url,
        params={"session_id": session_id},
        verify=not self.client.disable_ssl,
        timeout=self.client.timeout,
    )

```
  
---|---  
###  create `async` #
```
create() -> SessionDefinition

```

Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def create(self) -> SessionDefinition:
    """"""
    create_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/sessions/create"

    r = await self.client.request(
        "POST",
        create_url,
        verify=not self.client.disable_ssl,
        timeout=self.client.timeout,
    )

    return SessionDefinition(**r.json())

```
  
---|---  
###  list `async` #
```
list() -> list[SessionDefinition]

```

Returns a collection of all the sessions in the given deployment.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def list(self) -> list[SessionDefinition]:
    """Returns a collection of all the sessions in the given deployment."""
    sessions_url = (
        f"{self.client.api_server_url}/deployments/{self.deployment_id}/sessions"
    )
    r = await self.client.request(
        "GET",
        sessions_url,
        verify=not self.client.disable_ssl,
        timeout=self.client.timeout,
    )

    return r.json()

```
  
---|---  
##  Task #
Bases: `Model`
A model representing a task belonging to a given session in the given deployment.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`deployment_id` |  `str` |  |  _required_  
`session_id` |  `str` |  |  _required_  
Source code in `llama_deploy/client/models/apiserver.py`

| ```
class Task(Model):
    """A model representing a task belonging to a given session in the given deployment."""

    deployment_id: str
    session_id: str

    async def results(self) -> TaskResult:
        """Returns the result of a given task."""
        results_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/{self.id}/results"

        r = await self.client.request(
            "GET",
            results_url,
            verify=not self.client.disable_ssl,
            params={"session_id": self.session_id},
            timeout=self.client.timeout,
        )
        return TaskResult.model_validate(r.json())

    async def send_event(self, ev: Event, service_name: str) -> EventDefinition:
        """Sends a human response event."""
        url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/{self.id}/events"

        serializer = JsonSerializer()
        event_def = EventDefinition(
            event_obj_str=serializer.serialize(ev), agent_id=service_name
        )

        r = await self.client.request(
            "POST",
            url,
            verify=not self.client.disable_ssl,
            params={"session_id": self.session_id},
            json=event_def.model_dump(),
            timeout=self.client.timeout,
        )
        return EventDefinition.model_validate(r.json())

    async def events(self) -> AsyncGenerator[dict[str, Any], None]:  # pragma: no cover
        """Returns a generator object to consume the events streamed from a service."""
        events_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/{self.id}/events"

        while True:
            try:
                async with httpx.AsyncClient(
                    verify=not self.client.disable_ssl
                ) as client:
                    async with client.stream(
                        "GET", events_url, params={"session_id": self.session_id}
                    ) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            json_line = json.loads(line)
                            yield json_line
                        break  # Exit the function if successful
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 404:
                    raise  # Re-raise if it's not a 404 error
                await asyncio.sleep(self.client.poll_interval)

```
  
---|---  
###  results `async` #
```
results() -> TaskResult

```

Returns the result of a given task.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def results(self) -> TaskResult:
    """Returns the result of a given task."""
    results_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/{self.id}/results"

    r = await self.client.request(
        "GET",
        results_url,
        verify=not self.client.disable_ssl,
        params={"session_id": self.session_id},
        timeout=self.client.timeout,
    )
    return TaskResult.model_validate(r.json())

```
  
---|---  
###  send_event `async` #
```
send_event(ev: Event, service_name: str) -> EventDefinition

```

Sends a human response event.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def send_event(self, ev: Event, service_name: str) -> EventDefinition:
    """Sends a human response event."""
    url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/{self.id}/events"

    serializer = JsonSerializer()
    event_def = EventDefinition(
        event_obj_str=serializer.serialize(ev), agent_id=service_name
    )

    r = await self.client.request(
        "POST",
        url,
        verify=not self.client.disable_ssl,
        params={"session_id": self.session_id},
        json=event_def.model_dump(),
        timeout=self.client.timeout,
    )
    return EventDefinition.model_validate(r.json())

```
  
---|---  
###  events `async` #
```
events() -> AsyncGenerator[dict[str, Any], None]

```

Returns a generator object to consume the events streamed from a service.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def events(self) -> AsyncGenerator[dict[str, Any], None]:  # pragma: no cover
    """Returns a generator object to consume the events streamed from a service."""
    events_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/{self.id}/events"

    while True:
        try:
            async with httpx.AsyncClient(
                verify=not self.client.disable_ssl
            ) as client:
                async with client.stream(
                    "GET", events_url, params={"session_id": self.session_id}
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        json_line = json.loads(line)
                        yield json_line
                    break  # Exit the function if successful
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise  # Re-raise if it's not a 404 error
            await asyncio.sleep(self.client.poll_interval)

```
  
---|---  
##  TaskCollection #
Bases: `Collection`
A model representing a collection of tasks for a given deployment.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`deployment_id` |  `str` |  |  _required_  
Source code in `llama_deploy/client/models/apiserver.py`

| ```
class TaskCollection(Collection):
    """A model representing a collection of tasks for a given deployment."""

    deployment_id: str

    async def run(self, task: TaskDefinition) -> Any:
        """Runs a task and returns the results once it's done.

        Args:
            task: The definition of the task we want to run.
        """
        run_url = (
            f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/run"
        )
        if task.session_id:
            run_url += f"?session_id={task.session_id}"

        r = await self.client.request(
            "POST",
            run_url,
            verify=not self.client.disable_ssl,
            json=task.model_dump(),
            timeout=self.client.timeout,
        )

        return r.json()

    async def create(self, task: TaskDefinition) -> Task:
        """Runs a task returns it immediately, without waiting for the results."""
        create_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/create"

        r = await self.client.request(
            "POST",
            create_url,
            verify=not self.client.disable_ssl,
            json=task.model_dump(),
            timeout=self.client.timeout,
        )
        response_fields = r.json()

        model_class = self._prepare(Task)
        return model_class(
            client=self.client,
            deployment_id=self.deployment_id,
            id=response_fields["task_id"],
            session_id=response_fields["session_id"],
        )

    async def list(self) -> list[Task]:
        """Returns the list of tasks from this collection."""
        tasks_url = (
            f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks"
        )
        r = await self.client.request(
            "GET",
            tasks_url,
            verify=not self.client.disable_ssl,
            timeout=self.client.timeout,
        )
        task_model_class = self._prepare(Task)
        items = {
            "id": task_model_class(
                client=self.client,
                id=task_def.task_id,
                session_id=task_def.session_id,
                deployment_id=self.deployment_id,
            )
            for task_def in r.json()
        }
        model_class = self._prepare(TaskCollection)
        return model_class(
            client=self.client, deployment_id=self.deployment_id, items=items
        )

```
  
---|---  
###  run `async` #
```
run(task: TaskDefinition) -> Any

```

Runs a task and returns the results once it's done.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task` |  `TaskDefinition` |  The definition of the task we want to run. |  _required_  
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def run(self, task: TaskDefinition) -> Any:
    """Runs a task and returns the results once it's done.

    Args:
        task: The definition of the task we want to run.
    """
    run_url = (
        f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/run"
    )
    if task.session_id:
        run_url += f"?session_id={task.session_id}"

    r = await self.client.request(
        "POST",
        run_url,
        verify=not self.client.disable_ssl,
        json=task.model_dump(),
        timeout=self.client.timeout,
    )

    return r.json()

```
  
---|---  
###  create `async` #
```
create(task: TaskDefinition) -> Task

```

Runs a task returns it immediately, without waiting for the results.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def create(self, task: TaskDefinition) -> Task:
    """Runs a task returns it immediately, without waiting for the results."""
    create_url = f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks/create"

    r = await self.client.request(
        "POST",
        create_url,
        verify=not self.client.disable_ssl,
        json=task.model_dump(),
        timeout=self.client.timeout,
    )
    response_fields = r.json()

    model_class = self._prepare(Task)
    return model_class(
        client=self.client,
        deployment_id=self.deployment_id,
        id=response_fields["task_id"],
        session_id=response_fields["session_id"],
    )

```
  
---|---  
###  list `async` #
```
list() -> list[Task]

```

Returns the list of tasks from this collection.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def list(self) -> list[Task]:
    """Returns the list of tasks from this collection."""
    tasks_url = (
        f"{self.client.api_server_url}/deployments/{self.deployment_id}/tasks"
    )
    r = await self.client.request(
        "GET",
        tasks_url,
        verify=not self.client.disable_ssl,
        timeout=self.client.timeout,
    )
    task_model_class = self._prepare(Task)
    items = {
        "id": task_model_class(
            client=self.client,
            id=task_def.task_id,
            session_id=task_def.session_id,
            deployment_id=self.deployment_id,
        )
        for task_def in r.json()
    }
    model_class = self._prepare(TaskCollection)
    return model_class(
        client=self.client, deployment_id=self.deployment_id, items=items
    )

```
  
---|---  
##  Deployment #
Bases: `Model`
A model representing a deployment.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
class Deployment(Model):
    """A model representing a deployment."""

    @property
    def tasks(self) -> TaskCollection:
        """Returns a collection of tasks from all the sessions in the given deployment."""

        model_class = self._prepare(TaskCollection)
        return model_class(client=self.client, deployment_id=self.id, items={})

    @property
    def sessions(self) -> SessionCollection:
        """Returns a collection of all the sessions in the given deployment."""

        coll_model_class = self._prepare(SessionCollection)
        return coll_model_class(client=self.client, deployment_id=self.id, items={})

```
  
---|---  
###  tasks `property` #
```
tasks: TaskCollection

```

Returns a collection of tasks from all the sessions in the given deployment.
###  sessions `property` #
```
sessions: SessionCollection

```

Returns a collection of all the sessions in the given deployment.
##  DeploymentCollection #
Bases: `Collection`
A model representing a collection of deployments currently active.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
class DeploymentCollection(Collection):
    """A model representing a collection of deployments currently active."""

    async def create(self, config: TextIO, reload: bool = False) -> Deployment:
        """Creates a new deployment from a deployment file.

        If `reload` is true, an existing deployment will be reloaded, otherwise
        an error will be raised.

        Example:
        ```
            with open("deployment.yml") as f:
                await client.apiserver.deployments.create(f)
        ```
        """
        create_url = f"{self.client.api_server_url}/deployments/create"

        files = {"config_file": config.read()}
        r = await self.client.request(
            "POST",
            create_url,
            files=files,
            params={"reload": reload},
            verify=not self.client.disable_ssl,
            timeout=self.client.timeout,
        )

        model_class = self._prepare(Deployment)
        return model_class(client=self.client, id=r.json().get("name"))

    async def get(self, id: str) -> Deployment:
        """Gets a deployment by id."""
        get_url = f"{self.client.api_server_url}/deployments/{id}"
        # Current version of apiserver doesn't returns anything useful in this endpoint, let's just ignore it
        await self.client.request(
            "GET",
            get_url,
            verify=not self.client.disable_ssl,
            timeout=self.client.timeout,
        )
        model_class = self._prepare(Deployment)
        return model_class(client=self.client, id=id)

    async def list(self) -> list[Deployment]:
        deployments_url = f"{self.client.api_server_url}/deployments/"
        r = await self.client.request("GET", deployments_url)
        model_class = self._prepare(Deployment)
        deployments = [model_class(client=self.client, id=name) for name in r.json()]
        return deployments

```
  
---|---  
###  create `async` #
```
create(config: TextIO, reload: bool = False) -> Deployment

```

Creates a new deployment from a deployment file.
If `reload` is true, an existing deployment will be reloaded, otherwise an error will be raised.
Example
```
with open("deployment.yml") as f:
    await client.apiserver.deployments.create(f)

```

Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def create(self, config: TextIO, reload: bool = False) -> Deployment:
    """Creates a new deployment from a deployment file.

    If `reload` is true, an existing deployment will be reloaded, otherwise
    an error will be raised.

    Example:
    ```
        with open("deployment.yml") as f:
            await client.apiserver.deployments.create(f)
    ```
    """
    create_url = f"{self.client.api_server_url}/deployments/create"

    files = {"config_file": config.read()}
    r = await self.client.request(
        "POST",
        create_url,
        files=files,
        params={"reload": reload},
        verify=not self.client.disable_ssl,
        timeout=self.client.timeout,
    )

    model_class = self._prepare(Deployment)
    return model_class(client=self.client, id=r.json().get("name"))

```
  
---|---  
###  get `async` #
```
get(id: str) -> Deployment

```

Gets a deployment by id.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def get(self, id: str) -> Deployment:
    """Gets a deployment by id."""
    get_url = f"{self.client.api_server_url}/deployments/{id}"
    # Current version of apiserver doesn't returns anything useful in this endpoint, let's just ignore it
    await self.client.request(
        "GET",
        get_url,
        verify=not self.client.disable_ssl,
        timeout=self.client.timeout,
    )
    model_class = self._prepare(Deployment)
    return model_class(client=self.client, id=id)

```
  
---|---  
##  ApiServer #
Bases: `Model`
A model representing the API Server instance.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
class ApiServer(Model):
    """A model representing the API Server instance."""

    async def status(self) -> Status:
        """Returns the status of the API Server."""
        status_url = f"{self.client.api_server_url}/status/"

        try:
            r = await self.client.request(
                "GET",
                status_url,
                verify=not self.client.disable_ssl,
                timeout=self.client.timeout,
            )
        except httpx.ConnectError:
            return Status(
                status=StatusEnum.DOWN,
                status_message="API Server is down",
            )

        if r.status_code >= 400:
            body = r.json()
            return Status(status=StatusEnum.UNHEALTHY, status_message=r.text)

        description = "LlamaDeploy is up and running."
        body = r.json()
        deployments = body.get("deployments") or []
        if deployments:
            description += "\nActive deployments:"
            for d in deployments:
                description += f"\n- {d}"
        else:
            description += "\nCurrently there are no active deployments"

        return Status(
            status=StatusEnum.HEALTHY,
            status_message=description,
            deployments=deployments,
        )

    @property
    def deployments(self) -> DeploymentCollection:
        """Returns a collection of deployments currently active in the API Server."""
        model_class = self._prepare(DeploymentCollection)
        return model_class(client=self.client, items={})

```
  
---|---  
###  deployments `property` #
```
deployments: DeploymentCollection

```

Returns a collection of deployments currently active in the API Server.
###  status `async` #
```
status() -> Status

```

Returns the status of the API Server.
Source code in `llama_deploy/client/models/apiserver.py`

| ```
async def status(self) -> Status:
    """Returns the status of the API Server."""
    status_url = f"{self.client.api_server_url}/status/"

    try:
        r = await self.client.request(
            "GET",
            status_url,
            verify=not self.client.disable_ssl,
            timeout=self.client.timeout,
        )
    except httpx.ConnectError:
        return Status(
            status=StatusEnum.DOWN,
            status_message="API Server is down",
        )

    if r.status_code >= 400:
        body = r.json()
        return Status(status=StatusEnum.UNHEALTHY, status_message=r.text)

    description = "LlamaDeploy is up and running."
    body = r.json()
    deployments = body.get("deployments") or []
    if deployments:
        description += "\nActive deployments:"
        for d in deployments:
            description += f"\n- {d}"
    else:
        description += "\nCurrently there are no active deployments"

    return Status(
        status=StatusEnum.HEALTHY,
        status_message=description,
        deployments=deployments,
    )

```
  
---|---  
## Control Plane functionalities#
##  Session #
Bases: `Model`
Source code in `llama_deploy/client/models/core.py`

| ```
class Session(Model):
    async def run(self, service_name: str, **run_kwargs: Any) -> str:
        """Implements the workflow-based run API for a session."""
        task_input = json.dumps(run_kwargs)
        task_def = TaskDefinition(input=task_input, agent_id=service_name)
        task_id = await self._do_create_task(task_def)

        # wait for task to complete, up to timeout seconds
        async def _get_result() -> str:
            while True:
                task_result = await self._do_get_task_result(task_id)

                if isinstance(task_result, TaskResult):
                    return task_result.result or ""
                await asyncio.sleep(self.client.poll_interval)

        return await asyncio.wait_for(_get_result(), timeout=self.client.timeout)

    async def run_nowait(self, service_name: str, **run_kwargs: Any) -> str:
        """Implements the workflow-based run API for a session, but does not wait for the task to complete."""

        task_input = json.dumps(run_kwargs)
        task_def = TaskDefinition(input=task_input, agent_id=service_name)
        task_id = await self._do_create_task(task_def)

        return task_id

    async def create_task(self, task_def: TaskDefinition) -> str:
        """Create a new task in this session.

        Args:
            task_def (Union[str, TaskDefinition]): The task definition or input string.

        Returns:
            str: The ID of the created task.
        """
        return await self._do_create_task(task_def)

    async def _do_create_task(self, task_def: TaskDefinition) -> str:
        """Async-only version of create_task, to be used internally from other methods."""
        task_def.session_id = self.id
        url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks"
        response = await self.client.request("POST", url, json=task_def.model_dump())
        return response.json()

    async def get_task_result(self, task_id: str) -> TaskResult | None:
        """Get the result of a task in this session if it has one.

        Args:
            task_id (str): The ID of the task to get the result for.

        Returns:
            Optional[TaskResult]: The result of the task if it has one, otherwise None.
        """
        return await self._do_get_task_result(task_id)

    async def _do_get_task_result(self, task_id: str) -> TaskResult | None:
        """Async-only version of get_task_result, to be used internally from other methods."""
        url = (
            f"{self.client.control_plane_url}/sessions/{self.id}/tasks/{task_id}/result"
        )
        response = await self.client.request("GET", url)
        data = response.json()
        return TaskResult(**data) if data else None

    async def get_tasks(self) -> list[TaskDefinition]:
        """Get all tasks in this session.

        Returns:
            list[TaskDefinition]: A list of task definitions in the session.
        """
        url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks"
        response = await self.client.request("GET", url)
        return [TaskDefinition(**task) for task in response.json()]

    async def send_event(self, service_name: str, task_id: str, ev: Event) -> None:
        """Send event to a Workflow service.

        Args:
            event (Event): The event to be submitted to the workflow.

        Returns:
            None
        """
        serializer = JsonSerializer()
        event_def = EventDefinition(
            event_obj_str=serializer.serialize(ev), agent_id=service_name
        )

        url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks/{task_id}/send_event"
        await self.client.request("POST", url, json=event_def.model_dump())

    async def send_event_def(self, task_id: str, ev_def: EventDefinition) -> None:
        """Send event to a Workflow service.

        Args:
            event (Event): The event to be submitted to the workflow.

        Returns:
            None
        """
        url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks/{task_id}/send_event"
        await self.client.request("POST", url, json=ev_def.model_dump())

    async def get_task_result_stream(
        self, task_id: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Get the result of a task in this session if it has one.

        Args:
            task_id (str): The ID of the task to get the result for.

        Returns:
            AsyncGenerator[str, None, None]: A generator that yields the result of the task.
        """
        url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks/{task_id}/result_stream"
        start_time = time.time()
        while True:
            try:
                async with httpx.AsyncClient(timeout=self.client.timeout) as client:
                    async with client.stream("GET", url) as response:
                        response.raise_for_status()
                        async for line in response.aiter_lines():
                            json_line = json.loads(line)
                            yield json_line
                        break  # Exit the function if successful
            except httpx.HTTPStatusError as e:
                if e.response.status_code != 404:
                    raise  # Re-raise if it's not a 404 error
                if (
                    self.client.timeout is None  # means no timeout, always poll
                    or time.time() - start_time < self.client.timeout
                ):
                    await asyncio.sleep(self.client.poll_interval)
                else:
                    raise TimeoutError(
                        f"Task result not available after waiting for {self.client.timeout} seconds"
                    )

```
  
---|---  
###  run `async` #
```
run(service_name: str, **run_kwargs: Any) -> str

```

Implements the workflow-based run API for a session.
Source code in `llama_deploy/client/models/core.py`

| ```
async def run(self, service_name: str, **run_kwargs: Any) -> str:
    """Implements the workflow-based run API for a session."""
    task_input = json.dumps(run_kwargs)
    task_def = TaskDefinition(input=task_input, agent_id=service_name)
    task_id = await self._do_create_task(task_def)

    # wait for task to complete, up to timeout seconds
    async def _get_result() -> str:
        while True:
            task_result = await self._do_get_task_result(task_id)

            if isinstance(task_result, TaskResult):
                return task_result.result or ""
            await asyncio.sleep(self.client.poll_interval)

    return await asyncio.wait_for(_get_result(), timeout=self.client.timeout)

```
  
---|---  
###  run_nowait `async` #
```
run_nowait(service_name: str, **run_kwargs: Any) -> str

```

Implements the workflow-based run API for a session, but does not wait for the task to complete.
Source code in `llama_deploy/client/models/core.py`

| ```
async def run_nowait(self, service_name: str, **run_kwargs: Any) -> str:
    """Implements the workflow-based run API for a session, but does not wait for the task to complete."""

    task_input = json.dumps(run_kwargs)
    task_def = TaskDefinition(input=task_input, agent_id=service_name)
    task_id = await self._do_create_task(task_def)

    return task_id

```
  
---|---  
###  create_task `async` #
```
create_task(task_def: TaskDefinition) -> str

```

Create a new task in this session.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_def` |  `Union[str, TaskDefinition]` |  The task definition or input string. |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`str` |  `str` |  The ID of the created task.  
Source code in `llama_deploy/client/models/core.py`

| ```
async def create_task(self, task_def: TaskDefinition) -> str:
    """Create a new task in this session.

    Args:
        task_def (Union[str, TaskDefinition]): The task definition or input string.

    Returns:
        str: The ID of the created task.
    """
    return await self._do_create_task(task_def)

```
  
---|---  
###  get_task_result `async` #
```
get_task_result(task_id: str) -> TaskResult | None

```

Get the result of a task in this session if it has one.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  The ID of the task to get the result for. |  _required_  
Returns:
Type | Description  
---|---  
`TaskResult | None` |  Optional[TaskResult]: The result of the task if it has one, otherwise None.  
Source code in `llama_deploy/client/models/core.py`

| ```
async def get_task_result(self, task_id: str) -> TaskResult | None:
    """Get the result of a task in this session if it has one.

    Args:
        task_id (str): The ID of the task to get the result for.

    Returns:
        Optional[TaskResult]: The result of the task if it has one, otherwise None.
    """
    return await self._do_get_task_result(task_id)

```
  
---|---  
###  get_tasks `async` #
```
get_tasks() -> list[TaskDefinition]

```

Get all tasks in this session.
Returns:
Type | Description  
---|---  
`list[TaskDefinition]` |  list[TaskDefinition]: A list of task definitions in the session.  
Source code in `llama_deploy/client/models/core.py`

| ```
async def get_tasks(self) -> list[TaskDefinition]:
    """Get all tasks in this session.

    Returns:
        list[TaskDefinition]: A list of task definitions in the session.
    """
    url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks"
    response = await self.client.request("GET", url)
    return [TaskDefinition(**task) for task in response.json()]

```
  
---|---  
###  send_event `async` #
```
send_event(service_name: str, task_id: str, ev: Event) -> None

```

Send event to a Workflow service.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`event` |  `Event` |  The event to be submitted to the workflow. |  _required_  
Returns:
Type | Description  
---|---  
`None` |  None  
Source code in `llama_deploy/client/models/core.py`

| ```
async def send_event(self, service_name: str, task_id: str, ev: Event) -> None:
    """Send event to a Workflow service.

    Args:
        event (Event): The event to be submitted to the workflow.

    Returns:
        None
    """
    serializer = JsonSerializer()
    event_def = EventDefinition(
        event_obj_str=serializer.serialize(ev), agent_id=service_name
    )

    url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks/{task_id}/send_event"
    await self.client.request("POST", url, json=event_def.model_dump())

```
  
---|---  
###  send_event_def `async` #
```
send_event_def(task_id: str, ev_def: EventDefinition) -> None

```

Send event to a Workflow service.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`event` |  `Event` |  The event to be submitted to the workflow. |  _required_  
Returns:
Type | Description  
---|---  
`None` |  None  
Source code in `llama_deploy/client/models/core.py`

| ```
async def send_event_def(self, task_id: str, ev_def: EventDefinition) -> None:
    """Send event to a Workflow service.

    Args:
        event (Event): The event to be submitted to the workflow.

    Returns:
        None
    """
    url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks/{task_id}/send_event"
    await self.client.request("POST", url, json=ev_def.model_dump())

```
  
---|---  
###  get_task_result_stream `async` #
```
get_task_result_stream(task_id: str) -> AsyncGenerator[dict[str, Any], None]

```

Get the result of a task in this session if it has one.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`task_id` |  `str` |  The ID of the task to get the result for. |  _required_  
Returns:
Type | Description  
---|---  
`AsyncGenerator[dict[str, Any], None]` |  AsyncGenerator[str, None, None]: A generator that yields the result of the task.  
Source code in `llama_deploy/client/models/core.py`

| ```
async def get_task_result_stream(
    self, task_id: str
) -> AsyncGenerator[dict[str, Any], None]:
    """Get the result of a task in this session if it has one.

    Args:
        task_id (str): The ID of the task to get the result for.

    Returns:
        AsyncGenerator[str, None, None]: A generator that yields the result of the task.
    """
    url = f"{self.client.control_plane_url}/sessions/{self.id}/tasks/{task_id}/result_stream"
    start_time = time.time()
    while True:
        try:
            async with httpx.AsyncClient(timeout=self.client.timeout) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        json_line = json.loads(line)
                        yield json_line
                    break  # Exit the function if successful
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise  # Re-raise if it's not a 404 error
            if (
                self.client.timeout is None  # means no timeout, always poll
                or time.time() - start_time < self.client.timeout
            ):
                await asyncio.sleep(self.client.poll_interval)
            else:
                raise TimeoutError(
                    f"Task result not available after waiting for {self.client.timeout} seconds"
                )

```
  
---|---  
##  SessionCollection #
Bases: `Collection`
Source code in `llama_deploy/client/models/core.py`

| ```
class SessionCollection(Collection):
    async def list(self) -> list[Session]:  # type: ignore
        """Returns a list of all the sessions in the collection."""
        sessions_url = f"{self.client.control_plane_url}/sessions"
        response = await self.client.request("GET", sessions_url)
        sessions = []
        model_class = self._prepare(Session)
        for id, session_def in response.json().items():
            sessions.append(model_class(client=self.client, id=id))
        return sessions

    async def create(self) -> Session:
        """Creates a new session and returns a Session object.

        Returns:
            Session: A Session object representing the newly created session.
        """
        return await self._create()

    async def _create(self) -> Session:
        """Async-only version of create, to be used internally from other methods."""
        create_url = f"{self.client.control_plane_url}/sessions/create"
        response = await self.client.request("POST", create_url)
        session_id = response.json()
        model_class = self._prepare(Session)
        return model_class(client=self.client, id=session_id)

    async def get(self, id: str) -> Session:
        """Gets a session by ID.

        Args:
            session_id: The ID of the session to get.

        Returns:
            Session: A Session object representing the specified session.

        Raises:
            ValueError: If the session does not exist.
        """
        return await self._get(id)

    async def _get(self, id: str) -> Session:
        """Async-only version of get, to be used internally from other methods."""

        get_url = f"{self.client.control_plane_url}/sessions/{id}"
        await self.client.request("GET", get_url)
        model_class = self._prepare(Session)
        return model_class(client=self.client, id=id)

    async def get_or_create(self, id: str) -> Session:
        """Gets a session by ID, or creates a new one if it doesn't exist.

        Returns:
            Session: A Session object representing the specified session.
        """
        try:
            return await self._get(id)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return await self._create()
            raise e

    async def delete(self, session_id: str) -> None:
        """Deletes a session by ID.

        Args:
            session_id: The ID of the session to delete.
        """
        delete_url = f"{self.client.control_plane_url}/sessions/{session_id}/delete"
        await self.client.request("POST", delete_url)

```
  
---|---  
###  list `async` #
```
list() -> list[Session]

```

Returns a list of all the sessions in the collection.
Source code in `llama_deploy/client/models/core.py`

| ```
async def list(self) -> list[Session]:  # type: ignore
    """Returns a list of all the sessions in the collection."""
    sessions_url = f"{self.client.control_plane_url}/sessions"
    response = await self.client.request("GET", sessions_url)
    sessions = []
    model_class = self._prepare(Session)
    for id, session_def in response.json().items():
        sessions.append(model_class(client=self.client, id=id))
    return sessions

```
  
---|---  
###  create `async` #
```
create() -> Session

```

Creates a new session and returns a Session object.
Returns:
Name | Type | Description  
---|---|---  
`Session` |  `Session` |  A Session object representing the newly created session.  
Source code in `llama_deploy/client/models/core.py`

| ```
async def create(self) -> Session:
    """Creates a new session and returns a Session object.

    Returns:
        Session: A Session object representing the newly created session.
    """
    return await self._create()

```
  
---|---  
###  get `async` #
```
get(id: str) -> Session

```

Gets a session by ID.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`session_id` |  |  The ID of the session to get. |  _required_  
Returns:
Name | Type | Description  
---|---|---  
`Session` |  `Session` |  A Session object representing the specified session.  
Raises:
Type | Description  
---|---  
`ValueError` |  If the session does not exist.  
Source code in `llama_deploy/client/models/core.py`

| ```
async def get(self, id: str) -> Session:
    """Gets a session by ID.

    Args:
        session_id: The ID of the session to get.

    Returns:
        Session: A Session object representing the specified session.

    Raises:
        ValueError: If the session does not exist.
    """
    return await self._get(id)

```
  
---|---  
###  get_or_create `async` #
```
get_or_create(id: str) -> Session

```

Gets a session by ID, or creates a new one if it doesn't exist.
Returns:
Name | Type | Description  
---|---|---  
`Session` |  `Session` |  A Session object representing the specified session.  
Source code in `llama_deploy/client/models/core.py`

| ```
async def get_or_create(self, id: str) -> Session:
    """Gets a session by ID, or creates a new one if it doesn't exist.

    Returns:
        Session: A Session object representing the specified session.
    """
    try:
        return await self._get(id)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return await self._create()
        raise e

```
  
---|---  
###  delete `async` #
```
delete(session_id: str) -> None

```

Deletes a session by ID.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`session_id` |  `str` |  The ID of the session to delete. |  _required_  
Source code in `llama_deploy/client/models/core.py`

| ```
async def delete(self, session_id: str) -> None:
    """Deletes a session by ID.

    Args:
        session_id: The ID of the session to delete.
    """
    delete_url = f"{self.client.control_plane_url}/sessions/{session_id}/delete"
    await self.client.request("POST", delete_url)

```
  
---|---  
##  Service #
Bases: `Model`
Source code in `llama_deploy/client/models/core.py`

| ```
class Service(Model):
    pass

```
  
---|---  
##  ServiceCollection #
Bases: `Collection`
Source code in `llama_deploy/client/models/core.py`

| ```
class ServiceCollection(Collection):
    async def list(self) -> list[Service]:  # type: ignore
        """Returns a list containing all the services registered with the control plane.

        Returns:
            list[Service]: List of services registered with the control plane.
        """
        services_url = f"{self.client.control_plane_url}/services"
        response = await self.client.request("GET", services_url)
        services = []
        model_class = self._prepare(Service)

        for name, service in response.json().items():
            services.append(model_class(client=self.client, id=name))

        return services

    async def register(self, service: ServiceDefinition) -> Service:
        """Registers a service with the control plane.

        Args:
            service: Definition of the Service to register.
        """
        register_url = f"{self.client.control_plane_url}/services/register"
        await self.client.request("POST", register_url, json=service.model_dump())
        model_class = self._prepare(Service)
        s = model_class(id=service.service_name, client=self.client)
        self.items[service.service_name] = s
        return s

    async def deregister(self, service_name: str) -> None:
        """Deregisters a service from the control plane.

        Args:
            service_name: The name of the Service to deregister.
        """
        deregister_url = f"{self.client.control_plane_url}/services/deregister"
        await self.client.request(
            "POST",
            deregister_url,
            params={"service_name": service_name},
        )

```
  
---|---  
###  list `async` #
```
list() -> list[Service]

```

Returns a list containing all the services registered with the control plane.
Returns:
Type | Description  
---|---  
`list[Service]` |  list[Service]: List of services registered with the control plane.  
Source code in `llama_deploy/client/models/core.py`

| ```
async def list(self) -> list[Service]:  # type: ignore
    """Returns a list containing all the services registered with the control plane.

    Returns:
        list[Service]: List of services registered with the control plane.
    """
    services_url = f"{self.client.control_plane_url}/services"
    response = await self.client.request("GET", services_url)
    services = []
    model_class = self._prepare(Service)

    for name, service in response.json().items():
        services.append(model_class(client=self.client, id=name))

    return services

```
  
---|---  
###  register `async` #
```
register(service: ServiceDefinition) -> Service

```

Registers a service with the control plane.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`service` |  `ServiceDefinition` |  Definition of the Service to register. |  _required_  
Source code in `llama_deploy/client/models/core.py`

| ```
async def register(self, service: ServiceDefinition) -> Service:
    """Registers a service with the control plane.

    Args:
        service: Definition of the Service to register.
    """
    register_url = f"{self.client.control_plane_url}/services/register"
    await self.client.request("POST", register_url, json=service.model_dump())
    model_class = self._prepare(Service)
    s = model_class(id=service.service_name, client=self.client)
    self.items[service.service_name] = s
    return s

```
  
---|---  
###  deregister `async` #
```
deregister(service_name: str) -> None

```

Deregisters a service from the control plane.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`service_name` |  `str` |  The name of the Service to deregister. |  _required_  
Source code in `llama_deploy/client/models/core.py`

| ```
async def deregister(self, service_name: str) -> None:
    """Deregisters a service from the control plane.

    Args:
        service_name: The name of the Service to deregister.
    """
    deregister_url = f"{self.client.control_plane_url}/services/deregister"
    await self.client.request(
        "POST",
        deregister_url,
        params={"service_name": service_name},
    )

```
  
---|---  
##  Core #
Bases: `Model`
Source code in `llama_deploy/client/models/core.py`

| ```
class Core(Model):
    @property
    def services(self) -> ServiceCollection:
        """Returns a collection containing all the services registered with the control plane.

        Returns:
            ServiceCollection: Collection of services registered with the control plane.
        """
        model_class = self._prepare(ServiceCollection)
        return model_class(client=self.client, items={})

    @property
    def sessions(self) -> SessionCollection:
        """Returns a collection to access all the sessions registered with the control plane.

        Returns:
            SessionCollection: Collection of sessions registered with the control plane.
        """
        model_class = self._prepare(SessionCollection)
        return model_class(client=self.client, items={})

```
  
---|---  
###  services `property` #
```
services: ServiceCollection

```

Returns a collection containing all the services registered with the control plane.
Returns:
Name | Type | Description  
---|---|---  
`ServiceCollection` |  `ServiceCollection` |  Collection of services registered with the control plane.  
###  sessions `property` #
```
sessions: SessionCollection

```

Returns a collection to access all the sessions registered with the control plane.
Returns:
Name | Type | Description  
---|---|---  
`SessionCollection` |  `SessionCollection` |  Collection of sessions registered with the control plane.
