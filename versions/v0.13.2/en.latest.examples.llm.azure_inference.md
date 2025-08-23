![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Azure AI model inference¶
This notebook explains how to use `llama-index-llm-azure-inference` package with models deployed with the Azure AI model inference API in Azure AI studio or Azure Machine Learning. The package also support GitHub Models (Preview) endpoints.
In [ ]:
Copied!
```
%pip install llama-index-llms-azure-inference

```

%pip install llama-index-llms-azure-inference
If you're opening this notebook on Google Colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index

```

%pip install llama-index
## Prerequisites¶
The Azure AI model inference is an API that allows developers to get access to a variety of models hosted on Azure AI using a consistent schema. You can use `llama-index-llms-azure-inference` integration package with models that support this API, including models deployed to Azure AI serverless API endpoints and a subset of models from Managed Inference. To read more about the API specification and the models that support it see Azure AI model inference API.
To run this tutorial you need:
  1. Create an Azure subscription.
  2. Create an Azure AI hub resource as explained at How to create and manage an Azure AI Studio hub.
  3. Deploy one model supporting the Azure AI model inference API. In this example we use a `Mistral-Large` deployment.
     * You can follow the instructions at Deploy models as serverless APIs.


Alternatively, you can use GitHub Models endpoints with this integration, including the free tier experience. Read more about GitHub models.
## Environment Setup¶
Follow this steps to get the information you need from the model you want to use:
  1. Go to the Azure AI studio or Azure Machine Learning studio, depending on the product you are using.
  2. Go to deployments (endpoints in Azure Machine Learning) and select the model you have deployed as indicated in the prerequisites.
  3. Copy the endpoint URL and the key.


> If your model was deployed with Microsoft Entra ID support, you don't need a key.
In this scenario, we have placed both the endpoint URL and key in the following environment variables:
In [ ]:
Copied!
```
import os

os.environ["AZURE_INFERENCE_ENDPOINT"] = "<your-endpoint>"
os.environ["AZURE_INFERENCE_CREDENTIAL"] = "<your-credential>"

```

import os os.environ["AZURE_INFERENCE_ENDPOINT"] = "" os.environ["AZURE_INFERENCE_CREDENTIAL"] = ""
## Connect to your deployment and endpoint¶
To use LLMs deployed in Azure AI studio or Azure Machine Learning you need the endpoint and credentials to connect to it. The parameter `model_name` is not required for endpoints serving a single model, like Managed Online Endpoints.
In [ ]:
Copied!
```
from llama_index.llms.azure_inference import AzureAICompletionsModel

```

from llama_index.llms.azure_inference import AzureAICompletionsModel
In [ ]:
Copied!
```
llm = AzureAICompletionsModel(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
)

```

llm = AzureAICompletionsModel( endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"], credential=os.environ["AZURE_INFERENCE_CREDENTIAL"], )
Alternatively, if you endpoint support Microsoft Entra ID, you can use the following code to create the client:
In [ ]:
Copied!
```
from azure.identity import DefaultAzureCredential

llm = AzureAICompletionsModel(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

```

from azure.identity import DefaultAzureCredential llm = AzureAICompletionsModel( endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"], credential=DefaultAzureCredential(), )
> Note: When using Microsoft Entra ID, make sure that the endpoint was deployed with that authentication method and that you have the required permissions to invoke it.
If you are planning to use asynchronous calling, it's a best practice to use the asynchronous version for the credentials:
In [ ]:
Copied!
```
from azure.identity.aio import (
    DefaultAzureCredential as DefaultAzureCredentialAsync,
)

llm = AzureAICompletionsModel(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=DefaultAzureCredentialAsync(),
)

```

from azure.identity.aio import ( DefaultAzureCredential as DefaultAzureCredentialAsync, ) llm = AzureAICompletionsModel( endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"], credential=DefaultAzureCredentialAsync(), )
If your endpoint is serving more than one model, like GitHub Models or Azure AI Services, then you have to indicate the parameter `model_name`:
In [ ]:
Copied!
```
llm = AzureAICompletionsModel(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
    model_name="mistral-large",  # change it to the model you want to use
)

```

llm = AzureAICompletionsModel( endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"], credential=os.environ["AZURE_INFERENCE_CREDENTIAL"], model_name="mistral-large", # change it to the model you want to use )
## Use the model¶
Use the `complete` endpoint for text completion. Ihe `complete` method is still available for model of type `chat-completions`. On those cases, your input text is converted to a message with `role="user"`.
In [ ]:
Copied!
```
response = llm.complete("The sky is a beautiful blue and")
print(response)

```

response = llm.complete("The sky is a beautiful blue and") print(response)
In [ ]:
Copied!
```
response = llm.stream_complete("The sky is a beautiful blue and")
for r in response:
    print(r.delta, end="")

```

response = llm.stream_complete("The sky is a beautiful blue and") for r in response: print(r.delta, end="")
Use the `chat` endpoint for conversation
In [ ]:
Copied!
```
from llama_index.core.llms import ChatMessage

messages = [
    ChatMessage(
        role="system", content="You are a pirate with colorful personality."
    ),
    ChatMessage(role="user", content="Hello"),
]

response = llm.chat(messages)
print(response)

```

from llama_index.core.llms import ChatMessage messages = [ ChatMessage( role="system", content="You are a pirate with colorful personality." ), ChatMessage(role="user", content="Hello"), ] response = llm.chat(messages) print(response)
In [ ]:
Copied!
```
response = llm.stream_chat(messages)
for r in response:
    print(r.delta, end="")

```

response = llm.stream_chat(messages) for r in response: print(r.delta, end="")
Rather than adding same parameters to each chat or completion call, you can set them at the client instance.
In [ ]:
Copied!
```
llm = AzureAICompletionsModel(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
    temperature=0.0,
    model_kwargs={"top_p": 1.0},
)

```

llm = AzureAICompletionsModel( endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"], credential=os.environ["AZURE_INFERENCE_CREDENTIAL"], temperature=0.0, model_kwargs={"top_p": 1.0}, )
In [ ]:
Copied!
```
response = llm.complete("The sky is a beautiful blue and")
print(response)

```

response = llm.complete("The sky is a beautiful blue and") print(response)
For parameters extra parameters that are not supported by the Azure AI model inference API but that are available in the underlying model, you can use the `model_extras` argument. In the following example, the parameter `safe_prompt`, only available for Mistral models, is being passed.
In [ ]:
Copied!
```
llm = AzureAICompletionsModel(
    endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"],
    credential=os.environ["AZURE_INFERENCE_CREDENTIAL"],
    temperature=0.0,
    model_kwargs={"model_extras": {"safe_prompt": True}},
)

```

llm = AzureAICompletionsModel( endpoint=os.environ["AZURE_INFERENCE_ENDPOINT"], credential=os.environ["AZURE_INFERENCE_CREDENTIAL"], temperature=0.0, model_kwargs={"model_extras": {"safe_prompt": True}}, )
In [ ]:
Copied!
```
response = llm.complete("The sky is a beautiful blue and")
print(response)

```

response = llm.complete("The sky is a beautiful blue and") print(response)
## Additional resources¶
To learn more about this integration visit Getting starting with LlamaIndex and Azure AI.
