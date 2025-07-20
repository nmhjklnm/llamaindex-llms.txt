# 🦙 LlamaDeploy 🤖#
LlamaDeploy (formerly `llama-agents`) is an async-first framework for deploying, scaling, and productionizing agentic multi-service systems based on workflows from `llama_index`. With LlamaDeploy, you can build any number of workflows in `llama_index` and then run them as services, accessible through a HTTP API by a user interface or other services part of your system.
The goal of LlamaDeploy is to easily transition something that you built in a notebook to something running on the cloud with the minimum amount of changes to the original code, possibly zero. In order to make this transition a pleasant one, you can interact with LlamaDeploy in two ways:
  * Using the `llamactl` CLI from a shell.
  * Through the _LlamaDeploy SDK_ from a Python application or script.


Both the SDK and the CLI are part of the LlamaDeploy Python package. To install, just run:
```
pip install -U llama-deploy

```

Tip
For a comprehensive guide to LlamaDeploy's architecture and detailed descriptions of its components, visit our
official documentation.
## Why LlamaDeploy?#
  1. **Seamless Deployment** : It bridges the gap between development and production, allowing you to deploy `llama_index` workflows with minimal changes to your code.
  2. **Flexibility** : By using a hub-and-spoke architecture, you can easily swap out components (like message queues) or add new services without disrupting the entire system.
  3. **Fault Tolerance** : With built-in retry mechanisms and failure handling, LlamaDeploy adds robustness in production environments.
  4. **Async-First** : Designed for high-concurrency scenarios, making it suitable for real-time and high-throughput applications.


Note
This project was initially released under the name `llama-agents`, but the introduction of Workflows in `llama_index` turned out to be the most intuitive way for our users to develop agentic applications. We then decided to add new agentic features in `llama_index` directly, and focus LlamaDeploy on closing the gap between local development and remote execution of agents as services.
## Quick Start with `llamactl`#
Spin up a running deployment in minutes using the interactive CLI wizard:
```
# 1. Install the package & CLI
pip install -U llama-deploy

# 2. Scaffold a new project (interactive)
llamactl init

#    or non-interactive
llamactl init --name project-name --template basic

# 3. Enter the project
cd project-name

# 4. Start the control-plane API server (new terminal)
python -m llama_deploy.apiserver

# 5. Deploy the generated workflow (another terminal)
llamactl deploy deployment.yml

# 6. Call it!
llamactl run --deployment hello-deploy --arg message "Hello world!"

```

Looking for more templates or integrations? Check the `examples` directory for end-to-end demos (message queues, web UIs, etc.) or read the full documentation.
