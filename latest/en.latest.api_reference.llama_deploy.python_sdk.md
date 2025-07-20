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
