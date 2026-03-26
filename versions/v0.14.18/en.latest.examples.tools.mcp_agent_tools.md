# Use LlamaIndex agent tools as MCP tools¶
We have dozens of agent tools in LlamaHub and they can all be instantly used as MCP tools! This notebook shows how exactly that's done, using the Notion Tool as an example.
First we install our tool, and our MCP server:
In [ ]:
Copied!
```
!pip install llama-index-tools-notion mcp fastmcp

```

!pip install llama-index-tools-notion mcp fastmcp
Bring in our dependencies:
In [ ]:
Copied!
```
# Import dependencies for Model Context Protocol (MCP) fastMCP server
from typing import Any, Dict, List, Optional
from fastmcp import FastMCP

print("MCP fastMCP server dependencies imported successfully!")

```

# Import dependencies for Model Context Protocol (MCP) fastMCP server from typing import Any, Dict, List, Optional from fastmcp import FastMCP print("MCP fastMCP server dependencies imported successfully!")
```
MCP fastMCP server dependencies imported successfully!

```

Instantiate our tools using an API key:
In [ ]:
Copied!
```
# Import and configure LlamaIndex Notion Tool Spec
from llama_index.tools.notion import NotionToolSpec

notion_token = "xxxx"
tool_spec = NotionToolSpec(integration_token=notion_token)

```

# Import and configure LlamaIndex Notion Tool Spec from llama_index.tools.notion import NotionToolSpec notion_token = "xxxx" tool_spec = NotionToolSpec(integration_token=notion_token)
Let's see what tools are available:
In [ ]:
Copied!
```
tools = tool_spec.to_tool_list()

for i, tool in enumerate(tools):
    print(f"Tool {i+1}: {tool.metadata.name}")

```

tools = tool_spec.to_tool_list() for i, tool in enumerate(tools): print(f"Tool {i+1}: {tool.metadata.name}")
```
Tool 1: load_data
Tool 2: search_data

```

Now we create and configure the fastMCP server, and register each tool:
In [ ]:
Copied!
```
mcp_server = FastMCP("MCP Agent Tools Server")

# Register the tools from the Notion ToolSpec
for tool in tools:
    mcp_server.tool(
        name=tool.metadata.name, description=tool.metadata.description
    )(tool.real_fn)

```

mcp_server = FastMCP("MCP Agent Tools Server") # Register the tools from the Notion ToolSpec for tool in tools: mcp_server.tool( name=tool.metadata.name, description=tool.metadata.description )(tool.real_fn)
```
MCP Server configured with tools

```

Now we can run our MCP server complete with our tools!
In [ ]:
Copied!
```
await mcp_server.run_async(transport="streamable-http")

```

await mcp_server.run_async(transport="streamable-http")
```
[06/27/25 16:27:47] INFO     Starting MCP server 'MCP Agent Tools Server' with transport             server.py:1358
                             'streamable-http' on http://127.0.0.1:8000/mcp/                                       

```

```
INFO:     Started server process [24668]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

```

```
INFO:     127.0.0.1:54201 - "POST /mcp/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:54201 - "POST /mcp/ HTTP/1.1" 202 Accepted
INFO:     127.0.0.1:54203 - "GET /mcp/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:54209 - "POST /mcp/ HTTP/1.1" 200 OK

```

```
INFO:     Shutting down
ERROR:    ASGI callable returned without completing response.
ERROR:    Cancel 0 running task(s), timeout graceful shutdown exceeded
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [24668]

```

