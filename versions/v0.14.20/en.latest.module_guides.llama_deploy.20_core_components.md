# Core Components#
LlamaDeploy consists of several core components acting as services in order to provide the environment where multi-agent applications can run and communicate with each other. This sections details each and every component and will help you navigate the rest of the documentation.
## Deployment#
In LlamaDeploy each workflow is wrapped in a _Service_ object, endlessly processing incoming requests in form of _Task_ objects. Each service pulls and publishes messages to and from a _Message Queue_. An internal component called _Control Plane_ handles ongoing tasks, manages the internal state, keeps track of which services are available, and decides which service to forward a _Task_ to.
A well defined set of these components is called _Deployment_.
Deployments can be defined with YAML code, for example:
```
name: QuickStart

control-plane:
  port: 8000

default-service: dummy_workflow

services:
  dummy_workflow:
    name: Dummy Workflow
    source:
      type: local
      name: src
    path: workflow:echo_workflow

```

For more details, see the API reference for the deployment `Config` object.
## API Server#
The API Server is a core component of LlamaDeploy responsible for serving and managing multiple deployments at the same time, and it exposes a HTTP API that can be used for administrative purposes as well as for querying the deployed services. You can interact with the administrative API through `llamactl` or the Python SDK.
For more details see the Python API reference, while the administrative API is documented below.
## FastAPI```
 0.1.0 
```
```
OAS 3.1
```

apiserver.json
###  default
GET
/deployments/
Read Deployments
GET
/deployments/{deployment_name}
Read Deployment
POST
/deployments/create
Create Deployment
POST
/deployments/{deployment_name}/tasks/run
Create Deployment Task
POST
/deployments/{deployment_name}/tasks/create
Create Deployment Task Nowait
POST
/deployments/{deployment_name}/tasks/{task_id}/events
Send Event
GET
/deployments/{deployment_name}/tasks/{task_id}/events
Get Events
GET
/deployments/{deployment_name}/tasks/{task_id}/results
Get Task Result
GET
/deployments/{deployment_name}/tasks
Get Tasks
GET
/deployments/{deployment_name}/sessions
Get Sessions
GET
/deployments/{deployment_name}/sessions/{session_id}
Get Session
POST
/deployments/{deployment_name}/sessions/create
Create Session
POST
/deployments/{deployment_name}/sessions/delete
Delete Session
DELETE
/deployments/{deployment_name}/ui
Proxy
OPTIONS
/deployments/{deployment_name}/ui
Proxy
GET
/deployments/{deployment_name}/ui
Proxy
POST
/deployments/{deployment_name}/ui
Proxy
HEAD
/deployments/{deployment_name}/ui
Proxy
PATCH
/deployments/{deployment_name}/ui
Proxy
PUT
/deployments/{deployment_name}/ui
Proxy
DELETE
/deployments/{deployment_name}/ui/{path}
Proxy
OPTIONS
/deployments/{deployment_name}/ui/{path}
Proxy
GET
/deployments/{deployment_name}/ui/{path}
Proxy
POST
/deployments/{deployment_name}/ui/{path}
Proxy
HEAD
/deployments/{deployment_name}/ui/{path}
Proxy
PATCH
/deployments/{deployment_name}/ui/{path}
Proxy
PUT
/deployments/{deployment_name}/ui/{path}
Proxy
GET
/status/
Status
GET
/status/metrics
Metrics
GET
/
Root
#### Schemas
AudioBlock
Expand all**object**
Body_create_deployment_deployments_create_post
Expand all**object**
ChatMessage
Expand all**object**
DeploymentDefinition
Expand all**object**
DocumentBlock
Expand all**object**
EventDefinition
Expand all**object**
HTTPValidationError
Expand all**object**
ImageBlock
Expand all**object**
MessageRole
Expand all**string**
SessionDefinition
Expand all**object**
Status
Expand all**object**
StatusEnum
Expand all**string**
TaskDefinition
Expand all**object**
TaskResult
Expand all**object**
TextBlock
Expand all**object**
ValidationError
Expand all**object**
## Task#
A Task is an object representing a request for an operation sent to a Service and the response that will be sent back. For the details you can look at the API reference
