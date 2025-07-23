![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# RAGChecker: A Fine-grained Evaluation Framework For Diagnosing RAG¶
RAGChecker is a comprehensive evaluation framework designed for Retrieval-Augmented Generation (RAG) systems. It provides a suite of metrics to assess both the retrieval and generation components of RAG systems, offering detailed insights into their performance.
Key features of RAGChecker include:
  * Fine-grained analysis using claim-level entailment checking
  * Comprehensive metrics for overall performance, retriever efficiency, and generator accuracy
  * Actionable insights for improving RAG systems


For more information, visit the RAGChecker GitHub repository.
## RAGChecker Metrics¶
RAGChecker provides a comprehensive set of metrics to evaluate different aspects of RAG systems:
  1. Overall Metrics:
     * Precision: The proportion of correct claims in the model's response.
     * Recall: The proportion of ground truth claims covered by the model's response.
     * F1 Score: The harmonic mean of precision and recall.
  2. Retriever Metrics:
     * Claim Recall: The proportion of ground truth claims covered by the retrieved chunks.
     * Context Precision: The proportion of retrieved chunks that are relevant.
  3. Generator Metrics:
     * Context Utilization: How well the generator uses relevant information from retrieved chunks.
     * Noise Sensitivity: The generator's tendency to include incorrect information from retrieved chunks.
     * Hallucination: The proportion of incorrect claims not found in any retrieved chunks.
     * Self-knowledge: The proportion of correct claims not found in any retrieved chunks.
     * Faithfulness: How closely the generator's response aligns with the retrieved chunks.


These metrics provide a nuanced evaluation of both the retrieval and generation components, allowing for targeted improvements in RAG systems.
## Install Requirements¶
In [ ]:
Copied!
```
%pip install -qU ragchecker llama-index

```

%pip install -qU ragchecker llama-index
## Setup and Imports¶
First, let's import the necessary libraries:
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from ragchecker.integrations.llama_index import response_to_rag_results
from ragchecker import RAGResults, RAGChecker
from ragchecker.metrics import all_metrics

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader from ragchecker.integrations.llama_index import response_to_rag_results from ragchecker import RAGResults, RAGChecker from ragchecker.metrics import all_metrics
## Creating a LlamaIndex Query Engine¶
Now, let's create a simple LlamaIndex query engine using a sample dataset:
In [ ]:
Copied!
```
# Load documents
documents = SimpleDirectoryReader("path/to/your/documents").load_data()

# Create index
index = VectorStoreIndex.from_documents(documents)

# Create query engine
rag_application = index.as_query_engine()

```

# Load documents documents = SimpleDirectoryReader("path/to/your/documents").load_data() # Create index index = VectorStoreIndex.from_documents(documents) # Create query engine rag_application = index.as_query_engine()
## Using RAGChecker with LlamaIndex¶
Now we'll demonstrate how to use the `response_to_rag_results` function to convert LlamaIndex output to the RAGChecker format:
In [ ]:
Copied!
```
# User query and groud truth answer
user_query = "What is RAGChecker?"
gt_answer = "RAGChecker is an advanced automatic evaluation framework designed to assess and diagnose Retrieval-Augmented Generation (RAG) systems. It provides a comprehensive suite of metrics and tools for in-depth analysis of RAG performance."


# Get response from LlamaIndex
response_object = rag_application.query(user_query)

# Convert to RAGChecker format
rag_result = response_to_rag_results(
    query=user_query,
    gt_answer=gt_answer,
    response_object=response_object,
)

# Create RAGResults object
rag_results = RAGResults.from_dict({"results": [rag_result]})
print(rag_results)

```

# User query and groud truth answer user_query = "What is RAGChecker?" gt_answer = "RAGChecker is an advanced automatic evaluation framework designed to assess and diagnose Retrieval-Augmented Generation (RAG) systems. It provides a comprehensive suite of metrics and tools for in-depth analysis of RAG performance." # Get response from LlamaIndex response_object = rag_application.query(user_query) # Convert to RAGChecker format rag_result = response_to_rag_results( query=user_query, gt_answer=gt_answer, response_object=response_object, ) # Create RAGResults object rag_results = RAGResults.from_dict({"results": [rag_result]}) print(rag_results)
## Evaluating with RAGChecker¶
Now that we have our results in the correct format, let's evaluate them using RAGChecker:
In [ ]:
Copied!
```
# Initialize RAGChecker
evaluator = RAGChecker(
    extractor_name="bedrock/meta.llama3-70b-instruct-v1:0",
    checker_name="bedrock/meta.llama3-70b-instruct-v1:0",
    batch_size_extractor=32,
    batch_size_checker=32,
)

# Evaluate using RAGChecker
evaluator.evaluate(rag_results, all_metrics)

# Print detailed results
print(rag_results)

```

# Initialize RAGChecker evaluator = RAGChecker( extractor_name="bedrock/meta.llama3-70b-instruct-v1:0", checker_name="bedrock/meta.llama3-70b-instruct-v1:0", batch_size_extractor=32, batch_size_checker=32, ) # Evaluate using RAGChecker evaluator.evaluate(rag_results, all_metrics) # Print detailed results print(rag_results)
The output will look something like this:
```
RAGResults(
  1 RAG results,
  Metrics:
  {
    "overall_metrics": {
      "precision": 66.7,
      "recall": 27.3,
      "f1": 38.7
    },
    "retriever_metrics": {
      "claim_recall": 54.5,
      "context_precision": 100.0
    },
    "generator_metrics": {
      "context_utilization": 16.7,
      "noise_sensitivity_in_relevant": 0.0,
      "noise_sensitivity_in_irrelevant": 0.0,
      "hallucination": 33.3,
      "self_knowledge": 0.0,
      "faithfulness": 66.7
    }
  }
)

```

This output provides a comprehensive view of the RAG system's performance, including overall metrics, retriever metrics, and generator metrics as described in the earlier section.
### Selecting Specific Metric Groups¶
Instead of evaluating all the metrics with `all_metrics`, you can choose specific metric groups as follows:
In [ ]:
Copied!
```
from ragchecker.metrics import (
    overall_metrics,
    retriever_metrics,
    generator_metrics,
)

```

from ragchecker.metrics import ( overall_metrics, retriever_metrics, generator_metrics, )
### Selecting Individual Metrics¶
For even more granular control, you can choose specific individual metrics for your needs:
In [ ]:
Copied!
```
from ragchecker.metrics import (
    precision,
    recall,
    f1,
    claim_recall,
    context_precision,
    context_utilization,
    noise_sensitivity_in_relevant,
    noise_sensitivity_in_irrelevant,
    hallucination,
    self_knowledge,
    faithfulness,
)

```

from ragchecker.metrics import ( precision, recall, f1, claim_recall, context_precision, context_utilization, noise_sensitivity_in_relevant, noise_sensitivity_in_irrelevant, hallucination, self_knowledge, faithfulness, )
## Conclusion¶
This notebook has demonstrated how to integrate RAGChecker with LlamaIndex to evaluate the performance of RAG systems. We've covered:
  1. Setting up RAGChecker with LlamaIndex
  2. Converting LlamaIndex outputs to RAGChecker format
  3. Evaluating RAG results using various metrics
  4. Customizing evaluations with specific metric groups or individual metrics


By leveraging RAGChecker's comprehensive metrics, you can gain valuable insights into your RAG system's performance, identify areas for improvement, and optimize both retrieval and generation components. This integration provides a powerful tool for developing and refining more effective RAG applications.
