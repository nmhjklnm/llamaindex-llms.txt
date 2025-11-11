# MLflow Tracing and E2E Integration with LlamaIndex¶
Welcome to this interactive tutorial for LlamaIndex integration with MLflow. This tutorial provides a hands-on learning experience with LlamaIndex and MLflow's core features.
![mlflow-tracing](https://docs.llamaindex.ai/en/latest/_static/integrations/mlflow/mlflow.gif)
__Download this Notebook  

## Why use LlamaIndex with MLflow?¶
The integration of LlamaIndex with MLflow provides a seamless experience for developing and managing LlamaIndex applications:
  * **MLflow Tracing** is a powerful observability tool for monitoring and debugging what happens inside the LlamaIndex models, helping you identify potential bottlenecks or issues quickly.
  * **MLflow Experiment** allows you to track your indices/engines/workflows within MLflow and manage the many moving parts that comprise your LlamaIndex project, such as prompts, LLMs, tools, global configurations, and more.
  * **MLflow Model** packages your LlamaIndex applications with all its dependency versions, input and output interfaces, and other essential metadata.
  * **MLflow Evaluate** facilitates the efficient performance assessment of your LlamaIndex application, ensuring robust performance analytics and quick iterations.


## What you will learn¶
By the end of this tutorial you will have:
  * Created an MVP VectorStoreIndex in LlamaIndex.
  * Make inference using the index as a query engine and inspect it with MLflow Tracing.
  * Logged the index to MLflow Experiment.
  * Explored the MLflow UI to learn about how MLflow Model packages your LlamaIndex application.


These basics will familiarize you with the LlamaIndex user journey in MLflow. If you want to learn more about the integration with more advanced use cases (e.g. tool calling agent), please refer to this advanced tutorial.
## Setup¶
  1. Install MLflow and LlamaIndex:


In [ ]:
Copied!
```
%pip install mlflow>=2.18 llama-index>=0.10.44 -q

```

%pip install mlflow>=2.18 llama-index>=0.10.44 -q
  2. Open a separate terminal and run `mlflow ui --port 5000` to start the MLflow UI, if you haven't already. If you are running this notebook on a cloud environment, refer to the How to Run Tutorial guide to learn different setups for MLflow.
  3. Create an MLflow Experiment and connect the notebook to it


In [ ]:
Copied!
```
import mlflow

mlflow.set_experiment("llama-index-tutorial")
mlflow.set_tracking_uri(
    "http://localhost:5000"
)  # Or your remote tracking server URI

```

import mlflow mlflow.set_experiment("llama-index-tutorial") mlflow.set_tracking_uri( "http://localhost:5000" ) # Or your remote tracking server URI
  4. Set OpenAI API key to the environment variable. If you are using different LLM provider, set the corresponding environment variable.


In [ ]:
Copied!
```
import os
from getpass import getpass

os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")

```

import os from getpass import getpass os.environ["OPENAI_API_KEY"] = getpass("Enter your OpenAI API key: ")
## Enable MLflow Tracing¶
MLflow Tracing for LlamaIndex can be enabled just by one-line of code.
In [ ]:
Copied!
```
mlflow.llama_index.autolog()

```

mlflow.llama_index.autolog()
## Create an Index¶
Vector store indexes are one of the core components in LlamaIndex. They contain embedding vectors of ingested document chunks (and sometimes the document chunks as well). These vectors can be leveraged for inference tasks using different **engine** types in LlamaIndex.
  1. **Query Engine:** : Perform straightforward queries to retrieve relevant information based on a user’s question. Ideal for fetching concise answers or documents matching specific queries, similar to a search engine.
  2. **Chat Engine:** : Engage in conversational AI tasks that require maintaining context and history over multiple interactions. Suitable for interactive applications like customer support bots or virtual assistants, where conversation context is important.


In [ ]:
Copied!
```
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.llms import ChatMessage

# Create an index with a single dummy document
llama_index_example_document = Document.example()
index = VectorStoreIndex.from_documents([llama_index_example_document])

```

from llama_index.core import Document, VectorStoreIndex from llama_index.core.llms import ChatMessage # Create an index with a single dummy document llama_index_example_document = Document.example() index = VectorStoreIndex.from_documents([llama_index_example_document])
## Query the Index¶
Let's use this index to perform inference via a query engine.
In [ ]:
Copied!
```
query_response = index.as_query_engine().query("What is llama_index?")
print(query_response)

```

query_response = index.as_query_engine().query("What is llama_index?") print(query_response)
In addition to the response printed out, you should also see the MLflow Trace UI in the output cell. This provides a detailed yet intuitive visualization of the execution flow of the query engine, helping you understand the internal workings and debug any issues that may arise.
![](https://docs.llamaindex.ai/en/latest/_static/integrations/mlflow/mlflow_query_trace_quickstart.png)
Let's make another query with a chat engine this time, to see the difference in the execution flow.
In [ ]:
Copied!
```
chat_response = index.as_chat_engine().chat(
    "What is llama_index?",
    chat_history=[
        ChatMessage(role="system", content="You are an expert on RAG!")
    ],
)
print(chat_response)

```

chat_response = index.as_chat_engine().chat( "What is llama_index?", chat_history=[ ChatMessage(role="system", content="You are an expert on RAG!") ], ) print(chat_response)
![](https://docs.llamaindex.ai/en/latest/_static/integrations/mlflow/mlflow_chat_trace_quickstart.png)
As shown in the traces, the primary difference is that the query engine executes a static workflow (RAG), while the chat engine uses an agentic workflow to dynamically pulls the necessary context from the index.
You can also check the logged traces in MLflow UI, by navigating to the experiment you created earlier and selecting the `Trace` tab. If you don't want to show the traces in the output cell and only records them in MLflow, run `mlflow.tracing.disable_notebook_display()` in the notebook.
## Save the Index with MLflow¶
The below code logs a LlamaIndex model with MLflow, tracking its parameters and an example input while registering it with a unique model_uri. This ensures consistent, reproducible model management across development, testing, and production, and simplifies deployment and sharing.
Key Parameters:
  * `engine_type`: defines the pyfunc and spark_udf inference type
  * `input_example`: defines the input signature and infers the output signature via a prediction
  * `registered_model_name`: defines the name of the model in the MLflow model registry


In [ ]:
Copied!
```
with mlflow.start_run() as run:
    model_info = mlflow.llama_index.log_model(
        index,
        artifact_path="llama_index",
        engine_type="query",
        input_example="hi",
        registered_model_name="my_llama_index_vector_store",
    )
    model_uri = model_info.model_uri
    print(f"Model identifier for loading: {model_uri}")

```

with mlflow.start_run() as run: model_info = mlflow.llama_index.log_model( index, artifact_path="llama_index", engine_type="query", input_example="hi", registered_model_name="my_llama_index_vector_store", ) model_uri = model_info.model_uri print(f"Model identifier for loading: {model_uri}")
## Load the Index Back and Perform Inference¶
The below code demonstrates three core types of inference that can be done with the loaded model.
  1. **Load and Perform Inference via LlamaIndex:** This method loads the model using `mlflow.llama_index.load_model` and performs direct querying, chat, or retrieval. It is ideal when you want to leverage the full capabilities of the underlying llama index object.
  2. **Load and Perform Inference via MLflow PyFunc:** This method loads the model using `mlflow.pyfunc.load_model`, enabling model predictions in a generic PyFunc format, with the engine type specified at logging time. It is useful for evaluating the model with `mlflow.evaluate` or deploying the model for serving.
  3. **Load and Perform Inference via MLflow Spark UDF:** This method uses `mlflow.pyfunc.spark_udf` to load the model as a Spark UDF, facilitating distributed inference across large datasets in a Spark DataFrame. It is ideal for handling large-scale data processing and, like with PyFunc inference, only supports the engine type defined when logging.


In [ ]:
Copied!
```
print("\n------------- Inference via Llama Index   -------------")
index = mlflow.llama_index.load_model(model_uri)
query_response = index.as_query_engine().query("hi")
print(query_response)

print("\n------------- Inference via MLflow PyFunc -------------")
index = mlflow.pyfunc.load_model(model_uri)
query_response = index.predict("hi")
print(query_response)

```

print("\n------------- Inference via Llama Index -------------") index = mlflow.llama_index.load_model(model_uri) query_response = index.as_query_engine().query("hi") print(query_response) print("\n------------- Inference via MLflow PyFunc -------------") index = mlflow.pyfunc.load_model(model_uri) query_response = index.predict("hi") print(query_response)
In [ ]:
Copied!
```
# Optional: Spark UDF inference
show_spark_udf_inference = False
if show_spark_udf_inference:
    print("\n------------- Inference via MLflow Spark UDF -------------")
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()

    udf = mlflow.pyfunc.spark_udf(spark, model_uri, result_type="string")
    df = spark.createDataFrame([("hi",), ("hello",)], ["text"])
    df.withColumn("response", udf("text")).toPandas()

```

# Optional: Spark UDF inference show_spark_udf_inference = False if show_spark_udf_inference: print("\n------------- Inference via MLflow Spark UDF -------------") from pyspark.sql import SparkSession spark = SparkSession.builder.getOrCreate() udf = mlflow.pyfunc.spark_udf(spark, model_uri, result_type="string") df = spark.createDataFrame([("hi",), ("hello",)], ["text"]) df.withColumn("response", udf("text")).toPandas()
## Explore the MLflow Experiment UI¶
Finally, let's explore the MLflow's UI to what we have logged so far. You can access the UI by opening `http://localhost:5000` in your browser, or run the following cell to display it inside the notebook.
In [ ]:
Copied!
```
# Directly renders MLflow UI within the notebook for easy browsing:)
IFrame(src="http://localhost:5000", width=1000, height=600)

```

# Directly renders MLflow UI within the notebook for easy browsing:) IFrame(src="http://localhost:5000", width=1000, height=600)
Let's navigate to the experiments tab in the top left of the screen and click on our most recent run, as shown in the image below.
![](https://docs.llamaindex.ai/en/latest/_static/integrations/mlflow/mlflow_run_quickstart.png)
The Run page shows the overall metadata about your experiment. You can further navigate to the `Artifacts` tab to see the logged artifacts (models).
MLflow logs artifacts associated with your model and its environment during the MLflow run. Most of the logged files, such as the `conda.yaml`, `python_env.yml`, and `requirements.txt` are standard to all MLflow logging and facilitate reproducibility between environments. However, there are two sets of artifacts that are specific to LlamaIndex:
  * `index`: a directory that stores the serialized vector store. For more details, visit LlamaIndex's serialization docs.
  * `settings.json`: the serialized `llama_index.core.Settings` service context. For more details, visit LlamaIndex's Settings docs


By storing these objects, MLflow is able to recreate the environment in which you logged your model.
![](https://docs.llamaindex.ai/en/latest/_static/integrations/mlflow/mlflow_settings_quickstart.png)
**Important:** MLflow will not serialize API keys. Those must be present in your model loading environment as environment variables.
Finally, you can see the full list of traces that were logged during the tutorial by navigating to the `Tracing` tab. By clicking on a each row, you can see the detailed trace view similar to the one shown in the output cell earlier.
![](https://docs.llamaindex.ai/en/latest/_static/integrations/mlflow/mlflow_traces_list_quickstart.png)
## Customization and Next Steps¶
When working with production systems, typically users leverage a customized service context, which can be done via LlamaIndex's Settings object.
