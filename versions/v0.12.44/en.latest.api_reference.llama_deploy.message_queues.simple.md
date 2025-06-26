# simple#
##  SimpleMessageQueue #
Bases: `AbstractMessageQueue`
Remote client to be used with a SimpleMessageQueue server.
Source code in `llama_deploy/message_queues/simple/client.py`

| ```
class SimpleMessageQueue(AbstractMessageQueue):
    """Remote client to be used with a SimpleMessageQueue server."""

    def __init__(
        self, config: SimpleMessageQueueConfig = SimpleMessageQueueConfig()
    ) -> None:
        self._config = config
        self._consumers: dict[str, dict[str, BaseMessageQueueConsumer]] = {}

    async def _publish(self, message: QueueMessage, topic: str) -> Any:
        """Sends a message to the SimpleMessageQueueServer."""
        url = f"{self._config.base_url}messages/{topic}"
        async with httpx.AsyncClient(**self._config.client_kwargs) as client:
            result = await client.post(url, json=message.model_dump())
        return result

    async def register_consumer(
        self, consumer: BaseMessageQueueConsumer, topic: str
    ) -> StartConsumingCallable:
        """Register a new consumer."""
        # register topic
        if topic not in self._consumers:
            # call the server to create it
            url = f"{self._config.base_url}topics/{topic}"
            async with httpx.AsyncClient(**self._config.client_kwargs) as client:
                result = await client.post(url)
                result.raise_for_status()

            self._consumers[topic] = {}

        if consumer.id_ in self._consumers[topic]:
            msg = f"Consumer {consumer.id_} already registered for topic {topic}"
            raise ValueError(msg)

        self._consumers[topic][consumer.id_] = consumer
        logger.info(
            f"Consumer '{consumer.id_}' for type '{consumer.message_type}' on topic '{topic}' has been registered."
        )

        async def start_consuming_callable() -> None:
            """StartConsumingCallable.

            Consumer of this queue should call this in order to start consuming.
            """
            url = f"{self._config.base_url}messages/{topic}"
            client = httpx.AsyncClient(**self._config.client_kwargs)
            while True:
                try:
                    result = await client.get(url)
                    result.raise_for_status()
                    if result.json():
                        message = QueueMessage.model_validate(result.json())
                        await consumer.process_message(message)
                    await asyncio.sleep(0.1)

                except httpx.HTTPError as e:
                    logger.error(f"HTTP error occurred: {e}")
                    await asyncio.sleep(1)  # Back off on errors
                    continue

                except asyncio.CancelledError:
                    msg = f"Consumer {consumer.id_} for topic {topic} is shutting down"
                    logger.info(msg)
                    if client:
                        await client.aclose()
                    return  # Clean exit on cancellation

                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    await asyncio.sleep(1)  # Back off on errors
                    continue

        return start_consuming_callable

    async def deregister_consumer(self, consumer: BaseMessageQueueConsumer) -> Any:
        for topic, consumers in self._consumers.copy().items():
            if consumer.id_ in consumers:
                del self._consumers[topic][consumer.id_]

    async def cleanup(self, *args: Any, **kwargs: Dict[str, Any]) -> None:
        # Nothing to clean up
        pass

    def as_config(self) -> SimpleMessageQueueConfig:
        return self._config

```
  
---|---  
###  register_consumer `async` #
```
register_consumer(consumer: BaseMessageQueueConsumer, topic: str) -> StartConsumingCallable

```

Register a new consumer.
Source code in `llama_deploy/message_queues/simple/client.py`

| ```
async def register_consumer(
    self, consumer: BaseMessageQueueConsumer, topic: str
) -> StartConsumingCallable:
    """Register a new consumer."""
    # register topic
    if topic not in self._consumers:
        # call the server to create it
        url = f"{self._config.base_url}topics/{topic}"
        async with httpx.AsyncClient(**self._config.client_kwargs) as client:
            result = await client.post(url)
            result.raise_for_status()

        self._consumers[topic] = {}

    if consumer.id_ in self._consumers[topic]:
        msg = f"Consumer {consumer.id_} already registered for topic {topic}"
        raise ValueError(msg)

    self._consumers[topic][consumer.id_] = consumer
    logger.info(
        f"Consumer '{consumer.id_}' for type '{consumer.message_type}' on topic '{topic}' has been registered."
    )

    async def start_consuming_callable() -> None:
        """StartConsumingCallable.

        Consumer of this queue should call this in order to start consuming.
        """
        url = f"{self._config.base_url}messages/{topic}"
        client = httpx.AsyncClient(**self._config.client_kwargs)
        while True:
            try:
                result = await client.get(url)
                result.raise_for_status()
                if result.json():
                    message = QueueMessage.model_validate(result.json())
                    await consumer.process_message(message)
                await asyncio.sleep(0.1)

            except httpx.HTTPError as e:
                logger.error(f"HTTP error occurred: {e}")
                await asyncio.sleep(1)  # Back off on errors
                continue

            except asyncio.CancelledError:
                msg = f"Consumer {consumer.id_} for topic {topic} is shutting down"
                logger.info(msg)
                if client:
                    await client.aclose()
                return  # Clean exit on cancellation

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(1)  # Back off on errors
                continue

    return start_consuming_callable

```
  
---|---  
##  SimpleMessageQueueConfig #
Bases: `BaseSettings`
Simple message queue configuration.
Parameters:
Name | Type | Description | Default  
---|---|---|---  
`type` |  `Literal[str]` |  |  `'simple'`  
`host` |  `str` |  |  `'127.0.0.1'`  
`port` |  `int` |  |  `8001`  
`raise_exceptions` |  `bool` |  |  `False`  
`use_ssl` |  `bool` |  |  `False`  
Source code in `llama_deploy/message_queues/simple/config.py`

| ```
class SimpleMessageQueueConfig(BaseSettings):
    """Simple message queue configuration."""

    model_config = SettingsConfigDict(env_prefix="SIMPLE_MESSAGE_QUEUE_")

    type: Literal["simple"] = Field(default="simple", exclude=True)
    host: str = "127.0.0.1"
    port: int = 8001
    client_kwargs: dict[str, Any] = Field(default_factory=dict)
    raise_exceptions: bool = False
    use_ssl: bool = False

    @property
    def base_url(self) -> str:
        protocol = "https" if self.use_ssl else "http"
        if self.port != 80:
            return f"{protocol}://{self.host}:{self.port}/"
        return f"{protocol}://{self.host}/"

```
  
---|---  
##  SimpleMessageQueueServer #
SimpleMessageQueueServer.
An in-memory message queue that implements a push model for consumers.
When registering, a specific queue for a consumer is created. When a message is published, it is added to the queue for the given message type.
When launched as a server, exposes the following endpoints: - GET `/`: Home endpoint - POST `/register_consumer`: Register a consumer - POST `/deregister_consumer`: Deregister a consumer - GET `/get_consumers/{message_type}`: Get consumers for a message type - POST `/publish`: Publish a message
Source code in `llama_deploy/message_queues/simple/server.py`

| ```
class SimpleMessageQueueServer:
    """SimpleMessageQueueServer.

    An in-memory message queue that implements a push model for consumers.

    When registering, a specific queue for a consumer is created.
    When a message is published, it is added to the queue for the given message type.

    When launched as a server, exposes the following endpoints:
    - GET `/`: Home endpoint
    - POST `/register_consumer`: Register a consumer
    - POST `/deregister_consumer`: Deregister a consumer
    - GET `/get_consumers/{message_type}`: Get consumers for a message type
    - POST `/publish`: Publish a message
    """

    def __init__(self, config: SimpleMessageQueueConfig = SimpleMessageQueueConfig()):
        self._config = config
        self._consumers: dict[str, dict[str, BaseMessageQueueConsumer]] = {}
        self._queues: dict[str, deque] = {}
        self._running = False
        self._app = FastAPI()

        self._app.add_api_route(
            "/",
            self._home,
            methods=["GET"],
        )
        self._app.add_api_route(
            "/topics/{topic}",
            self._create_topic,
            methods=["POST"],
        )
        self._app.add_api_route(
            "/messages/{topic}",
            self._publish,
            methods=["POST"],
        )
        self._app.add_api_route(
            "/messages/{topic}",
            self._get_messages,
            methods=["GET"],
        )

    async def launch_server(self) -> None:
        """Launch the message queue as a FastAPI server."""
        logger.info(f"Launching message queue server at {self._config.base_url}")
        self._running = True

        cfg = uvicorn.Config(
            self._app, host=self._config.host, port=self._config.port or 80
        )
        server = uvicorn.Server(cfg)

        try:
            await server.serve()
        except asyncio.CancelledError:
            self._running = False
            await asyncio.gather(server.shutdown(), return_exceptions=True)

    #
    # HTTP API endpoints
    #

    async def _home(self) -> Dict[str, str]:
        return {
            "service_name": "message_queue",
            "description": "Message queue for multi-agent system",
        }

    async def _create_topic(self, topic: str) -> Any:
        """If topic already exists, this is a no-op."""
        if topic not in self._queues:
            self._queues[topic] = deque()

    async def _publish(self, message: QueueMessage, topic: str) -> Any:
        """Publish message to a queue."""
        if topic not in self._queues:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"topic {topic} not found"
            )

        self._queues[topic].append(message)

    async def _get_messages(self, topic: str) -> QueueMessage | None:
        if topic not in self._queues:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"topic {topic} not found"
            )
        if queue := self._queues[topic]:
            message: QueueMessage = queue.popleft()
            return message

        return None

```
  
---|---  
###  launch_server `async` #
```
launch_server() -> None

```

Launch the message queue as a FastAPI server.
Source code in `llama_deploy/message_queues/simple/server.py`

| ```
async def launch_server(self) -> None:
    """Launch the message queue as a FastAPI server."""
    logger.info(f"Launching message queue server at {self._config.base_url}")
    self._running = True

    cfg = uvicorn.Config(
        self._app, host=self._config.host, port=self._config.port or 80
    )
    server = uvicorn.Server(cfg)

    try:
        await server.serve()
    except asyncio.CancelledError:
        self._running = False
        await asyncio.gather(server.shutdown(), return_exceptions=True)

```
  
---|---
