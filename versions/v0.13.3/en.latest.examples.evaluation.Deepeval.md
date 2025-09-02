![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# 🚀 RAG/LLM Evaluators - DeepEval¶
This code tutorial shows how you can easily integrate DeepEval with LlamaIndex. DeepEval makes it easy to unit-test your RAG/LLMs.
You can read more about the DeepEval framework here: https://docs.confident-ai.com/docs/getting-started
Feel free to check out our repository here on GitHub: https://github.com/confident-ai/deepeval
### Set-up and Installation¶
We recommend setting up and installing via pip!
In [ ]:
Copied!
```
!pip install -q -q llama-index
!pip install -U -q deepeval

```

!pip install -q -q llama-index !pip install -U -q deepeval
This step is optional and only if you want a server-hosted dashboard! (Psst I think you should!)
In [ ]:
Copied!
```
!deepeval login

```

!deepeval login
## Types of Metrics¶
DeepEval presents an opinionated framework for unit testing RAG applications. It breaks down evaluations into test cases, and offers a range of evaluation metrics that you can freely evaluate for each test case, including:
  * G-Eval
  * Summarization
  * Answer Relevancy
  * Faithfulness
  * Contextual Recall
  * Contextual Precision
  * Contextual Relevancy
  * RAGAS
  * Hallucination
  * Bias
  * Toxicity


DeepEval incorporates the latest research into its evaluation metrics, which are then used to power LlamaIndex's evaluators. You can learn more about the full list of metrics and how they are calculated here.
## Step 1 - Setting Up Your LlamaIndex Application¶
In [ ]:
Copied!
```
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Read LlamaIndex's quickstart on more details, you will need to store your data in "YOUR_DATA_DIRECTORY" beforehand
documents = SimpleDirectoryReader("YOUR_DATA_DIRECTORY").load_data()
index = VectorStoreIndex.from_documents(documents)
rag_application = index.as_query_engine()

```

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader # Read LlamaIndex's quickstart on more details, you will need to store your data in "YOUR_DATA_DIRECTORY" beforehand documents = SimpleDirectoryReader("YOUR_DATA_DIRECTORY").load_data() index = VectorStoreIndex.from_documents(documents) rag_application = index.as_query_engine()
## Step 2 - Using DeepEval's RAG/LLM evaluators¶
DeepEval offers 6 evaluators out of the box, some for RAG, some directly for LLM outputs (although also works for RAG). Let's try the faithfulness evaluator (which is for evaluating hallucination in RAG):
In [ ]:
Copied!
```
from deepeval.integrations.llamaindex import DeepEvalFaithfulnessEvaluator

# An example input to your RAG application
user_input = "What is LlamaIndex?"

# LlamaIndex returns a response object that contains
# both the output string and retrieved nodes
response_object = rag_application.query(user_input)

evaluator = DeepEvalFaithfulnessEvaluator()
evaluation_result = evaluator.evaluate_response(
    query=user_input, response=response_object
)
print(evaluation_result)

```

from deepeval.integrations.llamaindex import DeepEvalFaithfulnessEvaluator # An example input to your RAG application user_input = "What is LlamaIndex?" # LlamaIndex returns a response object that contains # both the output string and retrieved nodes response_object = rag_application.query(user_input) evaluator = DeepEvalFaithfulnessEvaluator() evaluation_result = evaluator.evaluate_response( query=user_input, response=response_object ) print(evaluation_result)
## Full List of Evaluators¶
Here is how you can import all 6 evaluators from `deepeval`:
```
from deepeval.integrations.llama_index import (
    DeepEvalAnswerRelevancyEvaluator,
    DeepEvalFaithfulnessEvaluator,
    DeepEvalContextualRelevancyEvaluator,
    DeepEvalSummarizationEvaluator,
    DeepEvalBiasEvaluator,
    DeepEvalToxicityEvaluator,
)

```

For all evaluator definitions and to understand how it integrates with DeepEval's testing suite, click here.
## Useful Links¶
  * DeepEval Quickstart
  * Everything you need to know about LLM evaluation metrics


