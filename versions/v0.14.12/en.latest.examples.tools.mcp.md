# LlamaIndex + MCP Usage¶
The `llama-index-tools-mcp` package provides several tools for using MCP with LlamaIndex.
In [ ]:
Copied!
```
%pip install llama-index-tools-mcp

```

%pip install llama-index-tools-mcp
## Using Tools from an MCP Server¶
Using the `get_tools_from_mcp_url` or `aget_tools_from_mcp_url` function, you can get a list of `FunctionTool`s from an MCP server.
In [ ]:
Copied!
```
from llama_index.tools.mcp import (
    get_tools_from_mcp_url,
    aget_tools_from_mcp_url,
)

# async
tools = await aget_tools_from_mcp_url("http://127.0.0.1:8000/mcp")

```

from llama_index.tools.mcp import ( get_tools_from_mcp_url, aget_tools_from_mcp_url, ) # async tools = await aget_tools_from_mcp_url("http://127.0.0.1:8000/mcp")
By default, this will use our `BasicMCPClient`, which will run a command or connect to the URL and return the tools.
You can also pass in a custom `ClientSession` to use a different client.
You can also specify a list of allowed tools to filter the tools that are returned.
In [ ]:
Copied!
```
from llama_index.tools.mcp import BasicMCPClient

client = BasicMCPClient("http://127.0.0.1:8000/mcp")

tools = await aget_tools_from_mcp_url(
    "http://127.0.0.1:8000/mcp",
    client=client,
    allowed_tools=["tool1", "tool2"],
)

```

from llama_index.tools.mcp import BasicMCPClient client = BasicMCPClient("http://127.0.0.1:8000/mcp") tools = await aget_tools_from_mcp_url( "http://127.0.0.1:8000/mcp", client=client, allowed_tools=["tool1", "tool2"], )
## Converting a Workflow to an MCP App¶
If you have a custom `Workflow`, you can convert it to an MCP app using the `workflow_as_mcp` function.
For example, let's use the following workflow that will make a string loud:
In [ ]:
Copied!
```
from llama_index.core.workflow import (
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
    step,
)
from llama_index.tools.mcp.utils import workflow_as_mcp


class RunEvent(StartEvent):
    msg: str


class InfoEvent(Event):
    msg: str


class LoudWorkflow(Workflow):
    """Useful for converting strings to uppercase and making them louder."""

    @step
    def step_one(self, ctx: Context, ev: RunEvent) -> StopEvent:
        ctx.write_event_to_stream(InfoEvent(msg="Hello, world!"))

        return StopEvent(result=ev.msg.upper() + "!")


workflow = LoudWorkflow()

mcp = workflow_as_mcp(workflow)

```

from llama_index.core.workflow import ( Context, Workflow, Event, StartEvent, StopEvent, step, ) from llama_index.tools.mcp.utils import workflow_as_mcp class RunEvent(StartEvent): msg: str class InfoEvent(Event): msg: str class LoudWorkflow(Workflow): """Useful for converting strings to uppercase and making them louder.""" @step def step_one(self, ctx: Context, ev: RunEvent) -> StopEvent: ctx.write_event_to_stream(InfoEvent(msg="Hello, world!")) return StopEvent(result=ev.msg.upper() + "!") workflow = LoudWorkflow() mcp = workflow_as_mcp(workflow)
This code will automatically generate a `FastMCP` server that will
  * Use the workflow class name as the tool name
  * Use our custom `RunEvent` as the typed inputs to the tool
  * Automatically use the SSE stream for streaming json dumps of the workflow event stream


If this code was in a script called `script.py`, you could launch the MCP server with:
```
mcp dev script.py

```

Or the other commands documented in the MCP CLI README.
Note that to launch from the CLI, you may need to install the MCP CLI:
```
pip install "mcp[cli]"

```

You can further customize the `FastMCP` server by passing in additional arguments to the `workflow_as_mcp` function:
  * `workflow_name`: The name of the workflow. Defaults to the class name.
  * `workflow_description`: The description of the workflow. Defaults to the class docstring.
  * `start_event_model`: The event model to use for the start event. You can either use a custom `StartEvent` class in your workflow or pass in your own pydantic model here to define the inputs to the workflow.
  * `**fastmcp_init_kwargs`: Any extra arguments to pass to the `FastMCP()` server constructor.


## MCP Client Usage¶
The `BasicMCPClient` provides comprehensive access to MCP server capabilities beyond just tools.
### Basic Client Operations¶
In [ ]:
Copied!
```
from llama_index.tools.mcp import BasicMCPClient

# Connect to an MCP server using different transports
http_client = BasicMCPClient("https://example.com/mcp")  # Streamable HTTP
sse_client = BasicMCPClient("https://example.com/sse")  # Server-Sent Events
local_client = BasicMCPClient("python", args=["server.py"])  # stdio

# List available tools
tools = await http_client.list_tools()

# Call a tool
result = await http_client.call_tool("calculate", {"x": 5, "y": 10})

# List available resources
resources = await http_client.list_resources()

# Read a resource
content, mime_type = await http_client.read_resource("config://app")

# List available prompts
prompts = await http_client.list_prompts()

# Get a prompt
prompt_result = await http_client.get_prompt("greet", {"name": "World"})

```

from llama_index.tools.mcp import BasicMCPClient # Connect to an MCP server using different transports http_client = BasicMCPClient("https://example.com/mcp") # Streamable HTTP sse_client = BasicMCPClient("https://example.com/sse") # Server-Sent Events local_client = BasicMCPClient("python", args=["server.py"]) # stdio # List available tools tools = await http_client.list_tools() # Call a tool result = await http_client.call_tool("calculate", {"x": 5, "y": 10}) # List available resources resources = await http_client.list_resources() # Read a resource content, mime_type = await http_client.read_resource("config://app") # List available prompts prompts = await http_client.list_prompts() # Get a prompt prompt_result = await http_client.get_prompt("greet", {"name": "World"})
### OAuth Authentication¶
The client supports OAuth 2.0 authentication for connecting to protected MCP servers.
You can see the MCP docs for full details on configuring the various aspects of OAuth for both clients and servers.
In [ ]:
Copied!
```
from llama_index.tools.mcp import BasicMCPClient

# Simple authentication with in-memory token storage
client = BasicMCPClient.with_oauth(
    "https://api.example.com/mcp",
    client_name="My App",
    redirect_uris=["http://localhost:3000/callback"],
    # Function to handle the redirect URL (e.g., open a browser)
    redirect_handler=lambda url: print(f"Please visit: {url}"),
    # Function to get the authorization code from the user
    callback_handler=lambda: (input("Enter the code: "), None),
)

# Use the authenticated client
tools = await client.list_tools()

```

from llama_index.tools.mcp import BasicMCPClient # Simple authentication with in-memory token storage client = BasicMCPClient.with_oauth( "https://api.example.com/mcp", client_name="My App", redirect_uris=["http://localhost:3000/callback"], # Function to handle the redirect URL (e.g., open a browser) redirect_handler=lambda url: print(f"Please visit: {url}"), # Function to get the authorization code from the user callback_handler=lambda: (input("Enter the code: "), None), ) # Use the authenticated client tools = await client.list_tools()
By default, the client will use an in-memory token storage if no `token_storage` is provided. You can pass in a custom `TokenStorage` instance to use a different storage.
Below is an example showing the default in-memory token storage implementation.
In [ ]:
Copied!
```
from llama_index.tools.mcp import BasicMCPClient
from mcp.client.auth import TokenStorage
from mcp.shared.auth import OAuthToken, OAuthClientInformationFull
from typing import Optional


class DefaultInMemoryTokenStorage(TokenStorage):
    """
    Simple in-memory token storage implementation for OAuth authentication.

    This is the default storage used when none is provided to with_oauth().
    Not suitable for production use across restarts as tokens are only stored
    in memory.
    """

    def __init__(self):
        self._tokens: Optional[OAuthToken] = None
        self._client_info: Optional[OAuthClientInformationFull] = None

    async def get_tokens(self) -> Optional[OAuthToken]:
        """Get the stored OAuth tokens."""
        return self._tokens

    async def set_tokens(self, tokens: OAuthToken) -> None:
        """Store OAuth tokens."""
        self._tokens = tokens

    async def get_client_info(self) -> Optional[OAuthClientInformationFull]:
        """Get the stored client information."""
        return self._client_info

    async def set_client_info(
        self, client_info: OAuthClientInformationFull
    ) -> None:
        """Store client information."""
        self._client_info = client_info


# Use custom storage
client = BasicMCPClient.with_oauth(
    "https://api.example.com/mcp",
    client_name="My App",
    redirect_uris=["http://localhost:3000/callback"],
    redirect_handler=lambda url: print(f"Please visit: {url}"),
    callback_handler=lambda: (input("Enter the code: "), None),
    token_storage=DefaultInMemoryTokenStorage(),
)

```

from llama_index.tools.mcp import BasicMCPClient from mcp.client.auth import TokenStorage from mcp.shared.auth import OAuthToken, OAuthClientInformationFull from typing import Optional class DefaultInMemoryTokenStorage(TokenStorage): """ Simple in-memory token storage implementation for OAuth authentication. This is the default storage used when none is provided to with_oauth(). Not suitable for production use across restarts as tokens are only stored in memory. """ def __init__(self): self._tokens: Optional[OAuthToken] = None self._client_info: Optional[OAuthClientInformationFull] = None async def get_tokens(self) -> Optional[OAuthToken]: """Get the stored OAuth tokens.""" return self._tokens async def set_tokens(self, tokens: OAuthToken) -> None: """Store OAuth tokens.""" self._tokens = tokens async def get_client_info(self) -> Optional[OAuthClientInformationFull]: """Get the stored client information.""" return self._client_info async def set_client_info( self, client_info: OAuthClientInformationFull ) -> None: """Store client information.""" self._client_info = client_info # Use custom storage client = BasicMCPClient.with_oauth( "https://api.example.com/mcp", client_name="My App", redirect_uris=["http://localhost:3000/callback"], redirect_handler=lambda url: print(f"Please visit: {url}"), callback_handler=lambda: (input("Enter the code: "), None), token_storage=DefaultInMemoryTokenStorage(), )
