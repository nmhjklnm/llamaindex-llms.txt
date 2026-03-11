# Agents#
An "agent" is an automated reasoning and decision engine. It takes in a user input/query and can make internal decisions for executing that query in order to return the correct result. The key agent components can include, but are not limited to:
  * Breaking down a complex question into smaller ones
  * Choosing an external Tool to use + coming up with parameters for calling the Tool
  * Planning out a set of tasks
  * Storing previously completed tasks in a memory module


LlamaIndex provides a comprehensive framework for building agentic systems with varying degrees of complexity:
  * **If you want to build agents quickly** : Use our prebuilt agent and tool architectures to rapidly setup agentic systems.
  * **If you want full control over your agentic system** : Build and deploy custom agentic workflows from scratch using our Workflows.


## Use Cases#
The scope of possible use cases for agents is vast and ever-expanding. That said, here are some practical use cases that can deliver immediate value.
  * **Agentic RAG** : Build a context-augmented research assistant over your data that not only answers simple questions, but complex research tasks. Our getting started guide is a great place to start.
  * **Report Generation** : Generate a multimodal report using a multi-agent researcher + writer workflow + LlamaParse. Notebook.
  * **Customer Support** : Check out starter template for building a multi-agent concierge with workflows.


Others: - **Productivity Assistant** : Build an agent that can operate over common workflow tools like email, calendar. Check out our GSuite agent tutorial.
  * **Coding Assistant** : Build an agent that can operate over code. Check out our code interpreter tutorial.


## Resources#
**Prebuilt Agents and Tools**
The following component guides are the central hubs for getting started in building with agents:
  * Agents
  * Tools


**Custom Agentic Workflows**
LlamaIndex Workflows allow you to build very custom, agentic workflows through a core event-driven orchestration foundation.
  * Workflows Tutorial Sequence
  * Workflows Component Guide
  * Building a ReAct agent workflow
  * Deploying Workflows


**Building with Agentic Ingredients**
If you want to leverage core agentic ingredients in your workflow, LlamaIndex has robust abstractions for every agent sub-ingredient.
  * **Query Planning** : Routing, Sub-Questions, Query Transformations.
  * **Function Calling and Tool Use** : Check out our OpenAI, Mistral guides as examples.


## Ecosystem#
  * **Deploy Agents as Microservices** : Deploy your agentic workflows as microservices with llama_deploy (repo)
  * **Community-Built Agents** : We offer a collection of 40+ agent tools for use with your agent in LlamaHub 🦙.


