#  `apiserver`#
##  Deployment #
A Deployment consists of running services and core component instances.
Every Deployment is self contained, running a dedicated instance of the control plane and the message queue along with any service defined in the configuration object.
Source code in `llama_deploy/apiserver/deployment.py`

| ```
class Deployment:
    """A Deployment consists of running services and core component instances.

    Every Deployment is self contained, running a dedicated instance of the control plane
    and the message queue along with any service defined in the configuration object.
    """

    def __init__(self, *, config: DeploymentConfig, root_path: Path) -> None:
        """Creates a Deployment instance.

        Args:
            config: The configuration object defining this deployment
            root_path: The path on the filesystem used to store deployment data
        """
        self._name = config.name
        self._path = root_path / config.name
        self._queue_client = self._load_message_queue_client(config.message_queue)
        self._control_plane_config = config.control_plane
        self._control_plane = ControlPlaneServer(
            self._queue_client,
            SimpleOrchestrator(**SimpleOrchestratorConfig().model_dump()),
            config=config.control_plane,
        )
        self._client = Client(control_plane_url=config.control_plane.url)
        self._default_service: str | None = None
        self._running = False
        self._service_tasks: list[asyncio.Task] = []
        self._service_startup_complete = asyncio.Event()
        # Ready to load services
        self._workflow_services: dict[str, WorkflowService] = self._load_services(
            config
        )

    @property
    def default_service(self) -> str | None:
        return self._default_service

    @property
    def client(self) -> Client:
        """Returns an async client to interact with this deployment."""
        return self._client

    @property
    def name(self) -> str:
        """Returns the name of this deployment."""
        return self._name

    @property
    def path(self) -> Path:
        """Returns the absolute path to the root of this deployment."""
        return self._path.resolve()

    @property
    def service_names(self) -> list[str]:
        """Returns the list of service names in this deployment."""
        return list(self._workflow_services.keys())

    async def start(self) -> None:
        """The task that will be launched in this deployment asyncio loop.

        This task is responsible for launching asyncio tasks for the core components and the services.
        All the tasks are gathered before returning.
        """
        self._running = True

        # Control Plane
        tasks = await self._start_control_plane()

        # Start the services. It makes no sense for a deployment to have no services but
        # the configuration allows it, so let's be defensive here.
        if self._workflow_services:
            tasks.append(asyncio.create_task(self._run_services()))

        # Run allthethings
        await asyncio.gather(*tasks)
        self._running = False

    async def reload(self, config: DeploymentConfig) -> None:
        """Reload this deployment by restarting its services.

        The reload process consists in cancelling the services tasks
        and rely on the fact that _run_services() will restart them
        with the new configuration. This function won't return until
        _run_services will trigger the _service_startup_complete signal.
        """
        self._workflow_services = self._load_services(config)
        self._default_service = config.default_service

        for t in self._service_tasks:
            # t is awaited in _run_services(), we don't need to await here
            t.cancel()

        # Hold until _run_services() has restarted all the tasks
        await self._service_startup_complete.wait()

    async def _start_control_plane(self) -> list[asyncio.Task]:
        tasks = []
        cp_consumer_fn = await self._control_plane.register_to_message_queue()
        tasks.append(asyncio.create_task(self._control_plane.launch_server()))
        tasks.append(asyncio.create_task(cp_consumer_fn()))
        # Wait for the Control Plane to boot
        try:
            async for attempt in AsyncRetrying(
                wait=wait_exponential(min=1, max=10),
            ):
                with attempt:
                    async with httpx.AsyncClient() as client:
                        response = await client.get(self._control_plane_config.url)
                        response.raise_for_status()
        except RetryError:
            msg = f"Unable to reach Control Plane at {self._control_plane_config.url}"
            raise DeploymentError(msg)

        return tasks

    async def _run_services(self) -> None:
        """Start an asyncio task for each service and gather them.

        For the time self._running holds true, the tasks will be restarted
        if they are all cancelled. This is to support the reload process
        (see reload() for more details).
        """
        while self._running:
            self._service_tasks = []
            # If this is a reload, self._workflow_services contains the updated configurations
            for wfs in self._workflow_services.values():
                service_task = asyncio.create_task(wfs.launch_server())
                self._service_tasks.append(service_task)
                consumer_fn = await wfs.register_to_message_queue()
                await wfs.register_to_control_plane(self._control_plane_config.url)
                consumer_task = asyncio.create_task(consumer_fn())
                # Make sure the service is up and running before proceeding
                url = wfs.config.url
                try:
                    async for attempt in AsyncRetrying(
                        wait=wait_exponential(min=1, max=10),
                    ):
                        with attempt:
                            async with httpx.AsyncClient() as client:
                                response = await client.get(url)
                                response.raise_for_status()
                except RetryError:
                    msg = f"Unable to reach WorkflowService at {url}"
                    raise DeploymentError(msg)

                self._service_tasks.append(consumer_task)

            # If this is a reload, unblock the reload() function signalling that tasks are up and running
            self._service_startup_complete.set()
            await asyncio.gather(*self._service_tasks)

    def _load_services(self, config: DeploymentConfig) -> dict[str, WorkflowService]:
        """Creates WorkflowService instances according to the configuration object."""
        workflow_services = {}
        for service_id, service_config in config.services.items():
            source = service_config.source
            if source is None:
                # this is a default service, skip for now
                # TODO: check the service name is valid and supported
                # TODO: possibly start the default service if not running already
                continue

            # FIXME: Momentarily assuming everything is a workflow
            if service_config.path is None:
                msg = "path field in service definition must be set"
                raise ValueError(msg)

            if service_config.port is None:
                # This won't happen if we arrive here from Manager.deploy(), the manager will assign a port
                msg = "port field in service definition must be set"
                raise ValueError(msg)

            if service_config.host is None:
                # This won't happen if we arrive here from Manager.deploy(), the manager will assign a host
                msg = "host field in service definition must be set"
                raise ValueError(msg)

            # Sync the service source
            destination = (self._path / service_id).resolve()

            if destination.exists():
                # FIXME: this could be managed at the source manager level, so that
                # each implementation can decide what to do with existing data. For
                # example, the git source manager might decide to perform a git pull
                # instead of a brand new git clone. Leaving these optimnizations for
                # later, for the time being having an empty data folder works smoothly
                # for any source manager currently supported.
                rmtree(str(destination))

            source_manager = SOURCE_MANAGERS[source.type](config)
            source_manager.sync(source.name, str(destination))

            # Install dependencies
            self._install_dependencies(service_config)

            # Set environment variables
            self._set_environment_variables(service_config, destination)

            # Search for a workflow instance in the service path
            pythonpath = (destination / service_config.path).parent.resolve()
            sys.path.append(str(pythonpath))
            module_name, workflow_name = Path(service_config.path).name.split(":")
            module = importlib.import_module(module_name)

            workflow = getattr(module, workflow_name)
            workflow_config = WorkflowServiceConfig(
                host=service_config.host,
                port=service_config.port,
                internal_host="0.0.0.0",
                internal_port=service_config.port,
                service_name=service_id,
            )
            workflow_services[service_id] = WorkflowService(
                workflow=workflow,
                message_queue=self._queue_client,
                config=workflow_config,
            )

        if config.default_service in workflow_services:
            self._default_service = config.default_service
        else:
            msg = f"There is no service with id '{config.default_service}' in this deployment, cannot set default."
            logger.warning(msg)

        return workflow_services

    @staticmethod
    def _set_environment_variables(
        service_config: Service, root: Path | None = None
    ) -> None:
        """Sets environment variables for the service."""
        env_vars: dict[str, str | None] = {}

        if service_config.env:
            env_vars.update(**service_config.env)

        if service_config.env_files:
            for env_file in service_config.env_files:
                # use dotenv to parse env_file
                env_file_path = root / env_file if root else Path(env_file)
                env_vars.update(**dotenv_values(env_file_path))

        for k, v in env_vars.items():
            if v:
                os.environ[k] = v

    @staticmethod
    def _install_dependencies(service_config: Service) -> None:
        """Runs `pip install` on the items listed under `python-dependencies` in the service configuration."""
        if not service_config.python_dependencies:
            return

        try:
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    *service_config.python_dependencies,
                ]
            )
        except subprocess.CalledProcessError as e:
            msg = f"Unable to install service dependencies using command '{e.cmd}': {e.stderr}"
            raise DeploymentError(msg) from None

    def _load_message_queue_client(
        self, cfg: MessageQueueConfig | None
    ) -> AbstractMessageQueue:
        # Use the SimpleMessageQueue as the default
        if cfg is None:
            # we use model_validate instead of __init__ to avoid static checkers complaining over field aliases
            cfg = SimpleMessageQueueConfig()

        if cfg.type == "aws":
            return AWSMessageQueue(cfg)
        elif cfg.type == "kafka":
            return KafkaMessageQueue(cfg)
        elif cfg.type == "rabbitmq":
            return RabbitMQMessageQueue(cfg)
        elif cfg.type == "redis":
            return RedisMessageQueue(cfg)
        elif cfg.type == "simple":
            return SimpleMessageQueue(cfg)
        elif cfg.type == "solace":
            return SolaceMessageQueue(cfg)  # pragma: no cover
        else:
            msg = f"Unsupported message queue: {cfg.type}"
            raise ValueError(msg)

```
  
---|---  
###  client `property` #
```
client: Client

```

Returns an async client to interact with this deployment.
###  name `property` #
```
name: str

```

Returns the name of this deployment.
###  path `property` #
```
path: Path

```

Returns the absolute path to the root of this deployment.
###  service_names `property` #
```
service_names: list[str]

```

Returns the list of service names in this deployment.
###  start `async` #
```
start() -> None

```

The task that will be launched in this deployment asyncio loop.
This task is responsible for launching asyncio tasks for the core components and the services. All the tasks are gathered before returning.
Source code in `llama_deploy/apiserver/deployment.py`

| ```
async def start(self) -> None:
    """The task that will be launched in this deployment asyncio loop.

    This task is responsible for launching asyncio tasks for the core components and the services.
    All the tasks are gathered before returning.
    """
    self._running = True

    # Control Plane
    tasks = await self._start_control_plane()

    # Start the services. It makes no sense for a deployment to have no services but
    # the configuration allows it, so let's be defensive here.
    if self._workflow_services:
        tasks.append(asyncio.create_task(self._run_services()))

    # Run allthethings
    await asyncio.gather(*tasks)
    self._running = False

```
  
---|---  
###  reload `async` #
```
reload(config: DeploymentConfig) -> None

```

Reload this deployment by restarting its services.
The reload process consists in cancelling the services tasks and rely on the fact that _run_services() will restart them with the new configuration. This function won't return until _run_services will trigger the _service_startup_complete signal.
Source code in `llama_deploy/apiserver/deployment.py`

| ```
async def reload(self, config: DeploymentConfig) -> None:
    """Reload this deployment by restarting its services.

    The reload process consists in cancelling the services tasks
    and rely on the fact that _run_services() will restart them
    with the new configuration. This function won't return until
    _run_services will trigger the _service_startup_complete signal.
    """
    self._workflow_services = self._load_services(config)
    self._default_service = config.default_service

    for t in self._service_tasks:
        # t is awaited in _run_services(), we don't need to await here
        t.cancel()

    # Hold until _run_services() has restarted all the tasks
    await self._service_startup_complete.wait()

```
  
---|---  
##  Manager #
The Manager orchestrates deployments and their runtime.
Usage example
```
config = Config.from_yaml(data_path / "git_service.yaml")
manager = Manager(tmp_path)
t = threading.Thread(target=asyncio.run, args=(manager.serve(),))
t.start()
manager.deploy(config)
t.join()

```

Source code in `llama_deploy/apiserver/deployment.py`

| ```
class Manager:
    """The Manager orchestrates deployments and their runtime.

    Usage example:
    ```python
        config = Config.from_yaml(data_path / "git_service.yaml")
        manager = Manager(tmp_path)
        t = threading.Thread(target=asyncio.run, args=(manager.serve(),))
        t.start()
        manager.deploy(config)
        t.join()
    ```
    """

    def __init__(
        self, deployments_path: Path = Path(".deployments"), max_deployments: int = 10
    ) -> None:
        """Creates a Manager instance.

        Args:
            deployments_path: The filesystem path where deployments will create their root path.
            max_deployments: The maximum number of deployments supported by this manager.
        """
        self._deployments: dict[str, Any] = {}
        self._deployments_path = deployments_path
        self._max_deployments = max_deployments
        self._pool = ThreadPool(processes=max_deployments)
        self._last_control_plane_port = 8002
        self._simple_message_queue_server: asyncio.Task | None = None

    @property
    def deployment_names(self) -> list[str]:
        """Return a list of names for the active deployments."""
        return list(self._deployments.keys())

    def get_deployment(self, deployment_name: str) -> Deployment | None:
        return self._deployments.get(deployment_name)

    async def serve(self) -> None:
        """The server loop, it keeps the manager running."""
        event = asyncio.Event()
        try:
            # Waits indefinitely since `event` will never be set
            await event.wait()
        except asyncio.CancelledError:
            if self._simple_message_queue_server is not None:
                self._simple_message_queue_server.cancel()
                await self._simple_message_queue_server

    async def deploy(self, config: DeploymentConfig, reload: bool = False) -> None:
        """Creates a Deployment instance and starts the relative runtime.

        Args:
            config: The deployment configuration.
            reload: Reload an existing deployment instead of raising an error.

        Raises:
            ValueError: If a deployment with the same name already exists or the maximum number of deployment exceeded.
            DeploymentError: If it wasn't possible to create a deployment.
        """
        if not reload:
            # Raise an error if deployment already exists
            if config.name in self._deployments:
                msg = f"Deployment already exists: {config.name}"
                raise ValueError(msg)

            # Raise an error if we can't create any new deployment
            if len(self._deployments) == self._max_deployments:
                msg = "Reached the maximum number of deployments, cannot schedule more"
                raise ValueError(msg)

            # Set the control plane TCP port in the config where not specified
            self._assign_control_plane_address(config)

            # Get the message queue configuration
            msg_queue = config.message_queue or SimpleMessageQueueConfig()

            # Spawn SimpleMessageQueue server if needed
            if (
                isinstance(msg_queue, SimpleMessageQueueConfig)
                and self._simple_message_queue_server is None
            ):
                self._simple_message_queue_server = asyncio.create_task(
                    SimpleMessageQueueServer(msg_queue).launch_server()
                )

                # the other components need the queue to run in order to start, give the queue some time to start
                try:
                    async for attempt in AsyncRetrying(
                        wait=wait_exponential(min=1, max=10),
                    ):
                        with attempt:
                            async with httpx.AsyncClient() as client:
                                response = await client.get(msg_queue.base_url)
                                response.raise_for_status()
                except RetryError:
                    msg = f"Unable to reach SimpleMessageQueueServer at {msg_queue.base_url}"
                    raise DeploymentError(msg)

            deployment = Deployment(config=config, root_path=self._deployments_path)
            self._deployments[config.name] = deployment
            self._pool.apply_async(func=asyncio.run, args=(deployment.start(),))
        else:
            if config.name not in self._deployments:
                msg = f"Cannot find deployment to reload: {config.name}"
                raise ValueError(msg)

            deployment = self._deployments[config.name]
            await deployment.reload(config)

    def _assign_control_plane_address(self, config: DeploymentConfig) -> None:
        for service in config.services.values():
            if not service.port:
                service.port = self._last_control_plane_port
                self._last_control_plane_port += 1
            if not service.host:
                service.host = "localhost"

```
  
---|---  
###  deployment_names `property` #
```
deployment_names: list[str]

```

Return a list of names for the active deployments.
###  serve `async` #
```
serve() -> None

```

The server loop, it keeps the manager running.
Source code in `llama_deploy/apiserver/deployment.py`

| ```
async def serve(self) -> None:
    """The server loop, it keeps the manager running."""
    event = asyncio.Event()
    try:
        # Waits indefinitely since `event` will never be set
        await event.wait()
    except asyncio.CancelledError:
        if self._simple_message_queue_server is not None:
            self._simple_message_queue_server.cancel()
            await self._simple_message_queue_server

```
  
---|---  
###  deploy `async` #
```
deploy(config: DeploymentConfig, reload: bool = False) -> None

```

Creates a Deployment instance and starts the relative runtime.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`config` |  `DeploymentConfig` |  The deployment configuration. |  _required_  
`reload` |  `bool` |  Reload an existing deployment instead of raising an error. |  `False`  
Raises:
Type | Description  
---|---  
`ValueError` |  If a deployment with the same name already exists or the maximum number of deployment exceeded.  
`DeploymentError` |  If it wasn't possible to create a deployment.  
Source code in `llama_deploy/apiserver/deployment.py`

| ```
async def deploy(self, config: DeploymentConfig, reload: bool = False) -> None:
    """Creates a Deployment instance and starts the relative runtime.

    Args:
        config: The deployment configuration.
        reload: Reload an existing deployment instead of raising an error.

    Raises:
        ValueError: If a deployment with the same name already exists or the maximum number of deployment exceeded.
        DeploymentError: If it wasn't possible to create a deployment.
    """
    if not reload:
        # Raise an error if deployment already exists
        if config.name in self._deployments:
            msg = f"Deployment already exists: {config.name}"
            raise ValueError(msg)

        # Raise an error if we can't create any new deployment
        if len(self._deployments) == self._max_deployments:
            msg = "Reached the maximum number of deployments, cannot schedule more"
            raise ValueError(msg)

        # Set the control plane TCP port in the config where not specified
        self._assign_control_plane_address(config)

        # Get the message queue configuration
        msg_queue = config.message_queue or SimpleMessageQueueConfig()

        # Spawn SimpleMessageQueue server if needed
        if (
            isinstance(msg_queue, SimpleMessageQueueConfig)
            and self._simple_message_queue_server is None
        ):
            self._simple_message_queue_server = asyncio.create_task(
                SimpleMessageQueueServer(msg_queue).launch_server()
            )

            # the other components need the queue to run in order to start, give the queue some time to start
            try:
                async for attempt in AsyncRetrying(
                    wait=wait_exponential(min=1, max=10),
                ):
                    with attempt:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(msg_queue.base_url)
                            response.raise_for_status()
            except RetryError:
                msg = f"Unable to reach SimpleMessageQueueServer at {msg_queue.base_url}"
                raise DeploymentError(msg)

        deployment = Deployment(config=config, root_path=self._deployments_path)
        self._deployments[config.name] = deployment
        self._pool.apply_async(func=asyncio.run, args=(deployment.start(),))
    else:
        if config.name not in self._deployments:
            msg = f"Cannot find deployment to reload: {config.name}"
            raise ValueError(msg)

        deployment = self._deployments[config.name]
        await deployment.reload(config)

```
  
---|---  
##  DeploymentConfig #
Bases: `BaseModel`
Model definition mapping a deployment config file.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`name` |  `str` |  |  _required_  
`control_plane` |  `ControlPlaneConfig` |  |  _required_  
`message_queue` |  `Annotated[Union[AWSMessageQueueConfig, KafkaMessageQueueConfig, RabbitMQMessageQueueConfig, RedisMessageQueueConfig, SimpleMessageQueueConfig, SolaceMessageQueueConfig], FieldInfo] | None` |  |  `None`  
`default_service` |  `str | None` |  |  `None`  
`services` |  `dict[str, Service]` |  |  _required_  
`base_path` |  `Path` |  |  `PosixPath('.')`  
Source code in `llama_deploy/apiserver/deployment_config_parser.py`

| ```
class DeploymentConfig(BaseModel):
    """Model definition mapping a deployment config file."""

    name: str
    control_plane: ControlPlaneConfig = Field(alias="control-plane")
    message_queue: MessageQueueConfig | None = Field(None, alias="message-queue")
    default_service: str | None = Field(None, alias="default-service")
    services: dict[str, Service]
    base_path: Path = Path()

    @classmethod
    def from_yaml_bytes(cls, src: bytes) -> Self:
        """Read config data from bytes containing yaml code."""
        config = yaml.safe_load(src) or {}
        return cls(**config)

    @classmethod
    def from_yaml(cls, path: Path) -> Self:
        """Read config data from a yaml file."""
        with open(path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file) or {}
        return cls(**config, base_path=path.parent)

```
  
---|---  
###  from_yaml_bytes `classmethod` #
```
from_yaml_bytes(src: bytes) -> Self

```

Read config data from bytes containing yaml code.
Source code in `llama_deploy/apiserver/deployment_config_parser.py`

| ```
@classmethod
def from_yaml_bytes(cls, src: bytes) -> Self:
    """Read config data from bytes containing yaml code."""
    config = yaml.safe_load(src) or {}
    return cls(**config)

```
  
---|---  
###  from_yaml `classmethod` #
```
from_yaml(path: Path) -> Self

```

Read config data from a yaml file.
Source code in `llama_deploy/apiserver/deployment_config_parser.py`

| ```
@classmethod
def from_yaml(cls, path: Path) -> Self:
    """Read config data from a yaml file."""
    with open(path, "r") as yaml_file:
        config = yaml.safe_load(yaml_file) or {}
    return cls(**config, base_path=path.parent)

```
  
---|---  
##  SourceManager #
Bases: `ABC`
Protocol to be implemented by classes responsible for managing Deployment sources.
Source code in `llama_deploy/apiserver/source_managers/base.py`

| ```
class SourceManager(ABC):
    """Protocol to be implemented by classes responsible for managing Deployment sources."""

    def __init__(self, config: DeploymentConfig) -> None:
        self._config = config

    @abstractmethod
    def sync(
        self, source: str, destination: str | None = None
    ) -> None:  # pragma: no cover
        """Fetches resources from `source` so they can be used in a deployment.

        Optionally uses `destination` to store data when this makes sense for the
        specific source type.
        """

```
  
---|---  
###  sync `abstractmethod` #
```
sync(source: str, destination: str | None = None) -> None

```

Fetches resources from `source` so they can be used in a deployment.
Optionally uses `destination` to store data when this makes sense for the specific source type.
Source code in `llama_deploy/apiserver/source_managers/base.py`

| ```
@abstractmethod
def sync(
    self, source: str, destination: str | None = None
) -> None:  # pragma: no cover
    """Fetches resources from `source` so they can be used in a deployment.

    Optionally uses `destination` to store data when this makes sense for the
    specific source type.
    """

```
  
---|---  
##  GitSourceManager #
Bases: `SourceManager`
A SourceManager specialized for sources of type `git`.
Source code in `llama_deploy/apiserver/source_managers/git.py`

| ```
class GitSourceManager(SourceManager):
    """A SourceManager specialized for sources of type `git`."""

    def sync(self, source: str, destination: str | None = None) -> None:
        """Clones the repository at URL `source` into a local path `destination`.

        Args:
            source: The URL of the git repository. It can optionally contain a branch target using the name convention
                `git_repo_url@branch_name`. For example, "https://example.com/llama_deploy.git@branch_name".
            destination: The path in the local filesystem where to clone the git repository.
        """
        if not destination:
            raise ValueError("Destination cannot be empty")

        url, branch_name = self._parse_source(source)
        kwargs: dict[str, Any] = {"url": url, "to_path": destination}
        if branch_name:
            kwargs["multi_options"] = [f"-b {branch_name}", "--single-branch"]

        Repo.clone_from(**kwargs)

    @staticmethod
    def _parse_source(source: str) -> tuple[str, str | None]:
        branch_name = None
        toks = source.split("@")
        url = toks[0]
        if len(toks) > 1:
            branch_name = toks[1]

        return url, branch_name

```
  
---|---  
###  sync #
```
sync(source: str, destination: str | None = None) -> None

```

Clones the repository at URL `source` into a local path `destination`.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`source` |  `str` |  The URL of the git repository. It can optionally contain a branch target using the name convention `git_repo_url@branch_name`. For example, "https://example.com/llama_deploy.git@branch_name". |  _required_  
`destination` |  `str | None` |  The path in the local filesystem where to clone the git repository. |  `None`  
Source code in `llama_deploy/apiserver/source_managers/git.py`

| ```
def sync(self, source: str, destination: str | None = None) -> None:
    """Clones the repository at URL `source` into a local path `destination`.

    Args:
        source: The URL of the git repository. It can optionally contain a branch target using the name convention
            `git_repo_url@branch_name`. For example, "https://example.com/llama_deploy.git@branch_name".
        destination: The path in the local filesystem where to clone the git repository.
    """
    if not destination:
        raise ValueError("Destination cannot be empty")

    url, branch_name = self._parse_source(source)
    kwargs: dict[str, Any] = {"url": url, "to_path": destination}
    if branch_name:
        kwargs["multi_options"] = [f"-b {branch_name}", "--single-branch"]

    Repo.clone_from(**kwargs)

```
  
---|---  
##  LocalSourceManager #
Bases: `SourceManager`
A SourceManager specialized for sources of type `local`.
Source code in `llama_deploy/apiserver/source_managers/local.py`

| ```
class LocalSourceManager(SourceManager):
    """A SourceManager specialized for sources of type `local`."""

    def sync(self, source: str, destination: str | None = None) -> None:
        """Copies the folder with path `source` into a local path `destination`.

        Args:
            source: The filesystem path to the folder containing the source code.
            destination: The path in the local filesystem where to copy the source directory.
        """
        if not destination:
            raise ValueError("Destination cannot be empty")

        try:
            final_path = self._config.base_path / source
            shutil.copytree(final_path, destination, dirs_exist_ok=True)
        except Exception as e:
            msg = f"Unable to copy {source} into {destination}: {e}"
            raise ValueError(msg) from e

```
  
---|---  
###  sync #
```
sync(source: str, destination: str | None = None) -> None

```

Copies the folder with path `source` into a local path `destination`.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`source` |  `str` |  The filesystem path to the folder containing the source code. |  _required_  
`destination` |  `str | None` |  The path in the local filesystem where to copy the source directory. |  `None`  
Source code in `llama_deploy/apiserver/source_managers/local.py`

| ```
def sync(self, source: str, destination: str | None = None) -> None:
    """Copies the folder with path `source` into a local path `destination`.

    Args:
        source: The filesystem path to the folder containing the source code.
        destination: The path in the local filesystem where to copy the source directory.
    """
    if not destination:
        raise ValueError("Destination cannot be empty")

    try:
        final_path = self._config.base_path / source
        shutil.copytree(final_path, destination, dirs_exist_ok=True)
    except Exception as e:
        msg = f"Unable to copy {source} into {destination}: {e}"
        raise ValueError(msg) from e

```
  
---|---
