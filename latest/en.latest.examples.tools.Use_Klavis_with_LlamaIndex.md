![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# LlamaIndex + Klavis AI Integration¶
This tutorial demonstrates how to build AI agents using LlamaIndex's agent framework with Klavis MCP (Model Context Protocol) servers for enhanced functionality.
## Prerequisites¶
Before we begin, you'll need:
  * **OpenAI API key** - Get at openai.com
  * **Klavis API key** - Get at klavis.ai


In [ ]:
Copied!
```
# Install the required packages
%pip install -qU llama-index llama-index-tools-mcp klavis

```

# Install the required packages %pip install -qU llama-index llama-index-tools-mcp klavis
```
[notice] A new release of pip is available: 25.0 -> 25.1.1
[notice] To update, run: pip install --upgrade pip
Note: you may need to restart the kernel to use updated packages.

```

In [ ]:
Copied!
```
import os
from klavis import Klavis
from llama_index.llms.openai import OpenAI
from llama_index.tools.mcp import BasicMCPClient

# Set environment variables
os.environ[
    "OPENAI_API_KEY"
] = "YOUR_OPENAI_API_KEY"  # Replace with your actual OpenAI API key
os.environ[
    "KLAVIS_API_KEY"
] = "YOUR_KLAVIS_API_KEY"  # Replace with your actual Klavis API key

```

import os from klavis import Klavis from llama_index.llms.openai import OpenAI from llama_index.tools.mcp import BasicMCPClient # Set environment variables os.environ[ "OPENAI_API_KEY" ] = "YOUR_OPENAI_API_KEY" # Replace with your actual OpenAI API key os.environ[ "KLAVIS_API_KEY" ] = "YOUR_KLAVIS_API_KEY" # Replace with your actual Klavis API key
## Case 1: YouTube AI Agent¶
#### Create an AI agent to summarize YouTube videos using LlamaIndex and Klavis MCP Server.¶
#### Step 1 - using Klavis to create youtube MCP Server¶
In [ ]:
Copied!
```
klavis_client = Klavis(api_key=os.getenv("KLAVIS_API_KEY"))

# Create a YouTube MCP server and get the server URL
youtube_mcp_instance = klavis_client.mcp_server.instance.create(
    server_name="YouTube",
    user_id="1234",
    platform_name="Klavis",
)

youtube_mcp_server_url = youtube_mcp_instance.server_url
print(f"🔗 YouTube MCP server created at: {youtube_mcp_server_url}")

```

klavis_client = Klavis(api_key=os.getenv("KLAVIS_API_KEY")) # Create a YouTube MCP server and get the server URL youtube_mcp_instance = klavis_client.mcp_server.instance.create( server_name="YouTube", user_id="1234", platform_name="Klavis", ) youtube_mcp_server_url = youtube_mcp_instance.server_url print(f"🔗 YouTube MCP server created at: {youtube_mcp_server_url}")
```
🔗 YouTube MCP server created at: https://youtube-mcp-server.klavis.ai/sse?instance_id=270cbd51-e737-407d-85ce-6e6162248671

```

#### Step 2 - using Llamaindex to create AI Agent with the MCP Server¶
In [ ]:
Copied!
```
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.tools.mcp import (
    get_tools_from_mcp_url,
    aget_tools_from_mcp_url,
)

llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

youtube_tools = await aget_tools_from_mcp_url(
    youtube_mcp_server_url, client=BasicMCPClient(youtube_mcp_server_url)
)

youtube_agent = FunctionAgent(
    name="youtube_agent",
    description="Agent using MCP-based tools",
    tools=youtube_tools,
    llm=llm,
    system_prompt="You are an AI assistant that uses MCP tools.",
)

```

from llama_index.core.agent.workflow import FunctionAgent from llama_index.tools.mcp import ( get_tools_from_mcp_url, aget_tools_from_mcp_url, ) llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")) youtube_tools = await aget_tools_from_mcp_url( youtube_mcp_server_url, client=BasicMCPClient(youtube_mcp_server_url) ) youtube_agent = FunctionAgent( name="youtube_agent", description="Agent using MCP-based tools", tools=youtube_tools, llm=llm, system_prompt="You are an AI assistant that uses MCP tools.", )
#### Step 3 - Run your AI Agent to summarize your favorite video!¶
In [ ]:
Copied!
```
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=MmiveeGxfX0&t=528s"  # pick a video you like!

response = await youtube_agent.run(
    f"Summarize this video: {YOUTUBE_VIDEO_URL}"
)
print(response)

```

YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=MmiveeGxfX0&t=528s" # pick a video you like! response = await youtube_agent.run( f"Summarize this video: {YOUTUBE_VIDEO_URL}" ) print(response)
```
The video titled "Introducing AgentWorkflow, a way to easily create multi-agent systems in Llamaindex" presents a new system called AgentWorkflow designed for building and orchestrating AI agent systems. It emphasizes the ability to coordinate multiple AI agents while maintaining state and context, making it suitable for both single specialized agents and teams working together.

### Key Features:
- **Flexible Agent Types**: Includes FunctionAgent and ReActAgent.
- **Built-in State Management**: Helps in managing the state of agents effectively.
- **Real-time Monitoring**: Allows users to monitor the agents in action.
- **Human-in-the-loop Capabilities**: Facilitates human oversight in the agent processes.

The video encourages viewers to explore comprehensive tutorials and documentation to learn how to build everything from simple assistants to complex multi-agent systems. 

### Additional Resources:
- Basic Tutorial: [Basic Tutorial](https://docs.llamaindex.ai/en/stable/examples/agent/agent_workflow_basic/)
- Full Documentation: [Full docs](https://docs.llamaindex.ai/en/stable/understanding/agent/multi_agents/)
- Introductory Blog Post: [Blog Post](https://www.llamaindex.ai/blog/introducing-agentworkflow-a-powerful-system-for-building-ai-agent-systems)
- Discord Community: [Join Discord](https://discord.com/invite/eN6D2HQ4aX)

The video has a duration of approximately 16 minutes and 38 seconds and has garnered over 7,161 views.

```

✅ Nice work! You’ve successfully oursource your eyeball and summarized your favorite YouTube video!
## Case 2: Multi-Agent Workflow¶
#### Build a LlamaIndex AgentWorkflow that summarizes YouTube videos and sends the summary via email.¶
#### Step 1 - using Klavis to create YouTube and Gmail MCP Servers¶
In [ ]:
Copied!
```
import webbrowser

klavis_client = Klavis(api_key=os.getenv("KLAVIS_API_KEY"))

# Create YouTube MCP server
youtube_mcp_instance = klavis_client.mcp_server.instance.create(
    server_name="YouTube",
    user_id="1234",
    platform_name="Klavis",
)

# Create Gmail MCP server with OAuth authorization
gmail_mcp_instance = klavis_client.mcp_server.instance.create(
    server_name="Gmail",
    user_id="1234",
    platform_name="Klavis",
)

print("✅ Created YouTube and Gmail MCP instances")

# Open Gmail OAuth authorization
oauth_url = f"https://api.klavis.ai/oauth/gmail/authorize?instance_id={gmail_mcp_instance.instance_id}"
webbrowser.open(oauth_url)
print(
    f"🔐 Opening OAuth authorization for Gmail, if you are not redirected, please open the following URL in your browser: {oauth_url}"
)

```

import webbrowser klavis_client = Klavis(api_key=os.getenv("KLAVIS_API_KEY")) # Create YouTube MCP server youtube_mcp_instance = klavis_client.mcp_server.instance.create( server_name="YouTube", user_id="1234", platform_name="Klavis", ) # Create Gmail MCP server with OAuth authorization gmail_mcp_instance = klavis_client.mcp_server.instance.create( server_name="Gmail", user_id="1234", platform_name="Klavis", ) print("✅ Created YouTube and Gmail MCP instances") # Open Gmail OAuth authorization oauth_url = f"https://api.klavis.ai/oauth/gmail/authorize?instance_id={gmail_mcp_instance.instance_id}" webbrowser.open(oauth_url) print( f"🔐 Opening OAuth authorization for Gmail, if you are not redirected, please open the following URL in your browser: {oauth_url}" )
```
✅ Created YouTube and Gmail MCP instances
🔐 Opening OAuth authorization for Gmail, if you are not redirected, please open the following URL in your browser: https://api.klavis.ai/oauth/gmail/authorize?instance_id=d9d482b3-433a-4330-9a8b-9548c0b0a326

```

#### Step 2 - using LlamaIndex to create Multi-Agent Workflow with the MCP Servers¶
In [ ]:
Copied!
```
from llama_index.llms.openai import OpenAI
from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow
from llama_index.tools.mcp import (
    BasicMCPClient,
    get_tools_from_mcp_url,
    aget_tools_from_mcp_url,
)

llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Get MCP server URLs
youtube_mcp_server_url = youtube_mcp_instance.server_url
gmail_mcp_server_url = gmail_mcp_instance.server_url

# Get tools from both MCP servers
youtube_tools = await aget_tools_from_mcp_url(
    youtube_mcp_server_url, client=BasicMCPClient(youtube_mcp_server_url)
)
gmail_tools = await aget_tools_from_mcp_url(
    gmail_mcp_server_url, client=BasicMCPClient(gmail_mcp_server_url)
)

# Create specialized agents
youtube_agent = FunctionAgent(
    name="youtube_agent",
    description="Agent that can summarize YouTube videos",
    tools=youtube_tools,
    llm=llm,
    system_prompt="You are a YouTube video summarization expert. Use MCP tools to analyze and summarize videos.",
    can_handoff_to=["gmail_agent"],
)

gmail_agent = FunctionAgent(
    name="gmail_agent",
    description="Agent that can send emails via Gmail",
    tools=gmail_tools,
    llm=llm,
    system_prompt="You are an email assistant. Use MCP tools to send emails via Gmail.",
)

# Create multi-agent workflow
workflow = AgentWorkflow(
    agents=[youtube_agent, gmail_agent],
    root_agent="youtube_agent",
)

print("🤖 Multi-agent workflow created with YouTube and Gmail agents!")

```

from llama_index.llms.openai import OpenAI from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow from llama_index.tools.mcp import ( BasicMCPClient, get_tools_from_mcp_url, aget_tools_from_mcp_url, ) llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY")) # Get MCP server URLs youtube_mcp_server_url = youtube_mcp_instance.server_url gmail_mcp_server_url = gmail_mcp_instance.server_url # Get tools from both MCP servers youtube_tools = await aget_tools_from_mcp_url( youtube_mcp_server_url, client=BasicMCPClient(youtube_mcp_server_url) ) gmail_tools = await aget_tools_from_mcp_url( gmail_mcp_server_url, client=BasicMCPClient(gmail_mcp_server_url) ) # Create specialized agents youtube_agent = FunctionAgent( name="youtube_agent", description="Agent that can summarize YouTube videos", tools=youtube_tools, llm=llm, system_prompt="You are a YouTube video summarization expert. Use MCP tools to analyze and summarize videos.", can_handoff_to=["gmail_agent"], ) gmail_agent = FunctionAgent( name="gmail_agent", description="Agent that can send emails via Gmail", tools=gmail_tools, llm=llm, system_prompt="You are an email assistant. Use MCP tools to send emails via Gmail.", ) # Create multi-agent workflow workflow = AgentWorkflow( agents=[youtube_agent, gmail_agent], root_agent="youtube_agent", ) print("🤖 Multi-agent workflow created with YouTube and Gmail agents!")
```
🤖 Multi-agent workflow created with YouTube and Gmail agents!

```

#### Step 3 - run the workflow!¶
In [ ]:
Copied!
```
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=MmiveeGxfX0&t=528s"  # pick a video you like!
EMAIL_RECIPIENT = "zihaolin@klavis.ai"  # Replace with your email

resp = await workflow.run(
    user_msg=f"Summarize this video {YOUTUBE_VIDEO_URL} and send it to {EMAIL_RECIPIENT}"
)
print("\n✅ Report:\n", resp.response.content)

```

YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=MmiveeGxfX0&t=528s" # pick a video you like! EMAIL_RECIPIENT = "zihaolin@klavis.ai" # Replace with your email resp = await workflow.run( user_msg=f"Summarize this video {YOUTUBE_VIDEO_URL} and send it to {EMAIL_RECIPIENT}" ) print("\n✅ Report:\n", resp.response.content)
```
✅ Report:
 The summary of the video "Introducing AgentWorkflow, a way to easily create multi-agent systems in Llamaindex" has been successfully sent to zihaolin@klavis.ai. If you need anything else, feel free to ask!

```

## Summary¶
In this tutorial, we explored how to integrate LlamaIndex with Klavis AI to build powerful AI agents using MCP (Model Context Protocol) servers. Here's what we accomplished:
### Key Takeaways:¶
  1. **Single Agent Setup** : Created a YouTube AI agent that can summarize videos using the Klavis YouTube MCP server
  2. **Multi-Agent Workflow** : Built a sophisticated workflow combining YouTube and Gmail agents to summarize videos and automatically send summaries via email
  3. **MCP Integration** : Learned how to use Klavis MCP servers with LlamaIndex's agent framework for enhanced functionality


This integration opens up endless possibilities for building AI agents that can interact with various services and platforms through Klavis MCP servers. You can now create agents that work with YouTube, Gmail, GitHub, Slack, and many other services supported by Klavis.
Happy building! 🚀
