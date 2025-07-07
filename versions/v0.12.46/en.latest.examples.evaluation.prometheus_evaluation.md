![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Evaluation using Prometheus model¶
Evaluation is a crucial aspect of iterating over your RAG (Retrieval-Augmented Generation) pipeline. This process has relied heavily on GPT-4. However, a new open-source model named Prometheus has recently emerged as an alternative for evaluation purposes.
In this notebook, we will demonstrate how you can utilize the Prometheus model for evaluation, integrating it with the LlamaIndex abstractions.
If you're unfamiliar with the Prometheus model, you might find the paper summary prepared by Andrei informative. It's important to note that this model requires rubric scores to be included in the prompt for effective evaluation. For more detailed information, you can refer to the specific prompts outlined in the notebook.
![Prometheus Paper Card](https://docs.llamaindex.ai/en/latest/examples/evaluation/data/images/prometheus_paper_card.png)
We will demonstrate the correctness evaluation using the Prometheus model with two datasets from the Llama Datasets. If you haven't yet explored Llama Datasets, I recommend taking some time to read about them here.
  1. Paul Graham Essay
  2. Llama2


### Note: We are showcasing original Prometheus model for the analysis here. You can re-run the analysis with quantized version of the model.¶
In [ ]:
Copied!
```
%pip install llama-index-llms-openai
%pip install llama-index-llms-huggingface-api

```

%pip install llama-index-llms-openai %pip install llama-index-llms-huggingface-api
In [ ]:
Copied!
```
# attach to the same event-loop
import nest_asyncio

nest_asyncio.apply()

```

# attach to the same event-loop import nest_asyncio nest_asyncio.apply()
## Download Datasets¶
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import download_llama_dataset

paul_graham_rag_dataset, paul_graham_documents = download_llama_dataset(
    "PaulGrahamEssayDataset", "./data/paul_graham"
)

llama2_rag_dataset, llama2_documents = download_llama_dataset(
    "Llama2PaperDataset", "./data/llama2"
)

```

from llama_index.core.llama_dataset import download_llama_dataset paul_graham_rag_dataset, paul_graham_documents = download_llama_dataset( "PaulGrahamEssayDataset", "./data/paul_graham" ) llama2_rag_dataset, llama2_documents = download_llama_dataset( "Llama2PaperDataset", "./data/llama2" )
## Define Prometheus LLM hosted on HuggingFace.¶
We hosted the model on HF Inference endpoint using Nvidia A10G GPU.
In [ ]:
Copied!
```
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI

HF_TOKEN = "YOUR HF TOKEN"
HF_ENDPOINT_URL = (
    "https://q3yljc2cypyrvw3i.us-east-1.aws.endpoints.huggingface.cloud"
)

prometheus_llm = HuggingFaceInferenceAPI(
    model_name=HF_ENDPOINT_URL,
    token=HF_TOKEN,
    temperature=0.1,
    do_sample=True,
    top_p=0.95,
    top_k=40,
    repetition_penalty=1.1,
)

```

from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI HF_TOKEN = "YOUR HF TOKEN" HF_ENDPOINT_URL = ( "https://q3yljc2cypyrvw3i.us-east-1.aws.endpoints.huggingface.cloud" ) prometheus_llm = HuggingFaceInferenceAPI( model_name=HF_ENDPOINT_URL, token=HF_TOKEN, temperature=0.1, do_sample=True, top_p=0.95, top_k=40, repetition_penalty=1.1, )
```
/opt/homebrew/lib/python3.11/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html
  from .autonotebook import tqdm as notebook_tqdm

```

## Prompt templates.¶
We will use same prompts for Prometheus model and GPT-4 to make consistent performance comparison.
### Correctness Evaluation Prompt¶
In [ ]:
Copied!
```
prometheus_correctness_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query, a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given. 
			1. Write a detailed feedback that assesses the quality of the response strictly based on the given score rubric, not evaluating in general. 
			2. After writing a feedback, write a score that is either 1 or 2 or 3 or 4 or 5. You should refer to the score rubric. 
			3. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (1 or 2 or 3 or 4 or 5)" 
			4. Please do not generate any other opening, closing, and explanations. 
            5. Only evaluate on common things between generated answer and reference answer. Don't evaluate on things which are present in reference answer but not in generated answer.

			###The instruction to evaluate: Your task is to evaluate the generated answer and reference answer for the query: {query}
			
            ###Generate answer to evaluate: {generated_answer} 

            ###Reference Answer (Score 5): {reference_answer}
            
    		###Score Rubrics: 
            Score 1: If the generated answer is not relevant to the user query and reference answer.
            Score 2: If the generated answer is according to reference answer but not relevant to user query.
            Score 3: If the generated answer is relevant to the user query and reference answer but contains mistakes.
    		Score 4: If the generated answer is relevant to the user query and has the exact same metrics as the reference answer, but it is not as concise.
            Score 5: If the generated answer is relevant to the user query and fully correct according to the reference answer.
    
    		###Feedback:"""

```

prometheus_correctness_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query, a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given. 1. Write a detailed feedback that assesses the quality of the response strictly based on the given score rubric, not evaluating in general. 2. After writing a feedback, write a score that is either 1 or 2 or 3 or 4 or 5. You should refer to the score rubric. 3. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (1 or 2 or 3 or 4 or 5)" 4. Please do not generate any other opening, closing, and explanations. 5. Only evaluate on common things between generated answer and reference answer. Don't evaluate on things which are present in reference answer but not in generated answer. ###The instruction to evaluate: Your task is to evaluate the generated answer and reference answer for the query: {query} ###Generate answer to evaluate: {generated_answer} ###Reference Answer (Score 5): {reference_answer} ###Score Rubrics: Score 1: If the generated answer is not relevant to the user query and reference answer. Score 2: If the generated answer is according to reference answer but not relevant to user query. Score 3: If the generated answer is relevant to the user query and reference answer but contains mistakes. Score 4: If the generated answer is relevant to the user query and has the exact same metrics as the reference answer, but it is not as concise. Score 5: If the generated answer is relevant to the user query and fully correct according to the reference answer. ###Feedback:"""
In [ ]:
Copied!
```
prometheus_correctness_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query, a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given. 
			1. Write a detailed feedback that assesses the quality of the response strictly based on the given score rubric, not evaluating in general. 
			2. After writing a feedback, write a score that is either 1 or 2 or 3 or 4 or 5. You should refer to the score rubric. 
			3. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (1 or 2 or 3 or 4 or 5)" 
			4. Please do not generate any other opening, closing, and explanations. 
            5. Only evaluate on common things between generated answer and reference answer. Don't evaluate on things which are present in reference answer but not in generated answer.

			###The instruction to evaluate: Your task is to evaluate the generated answer and reference answer for the query: {query}
			
            ###Generate answer to evaluate: {generated_answer} 

            ###Reference Answer (Score 5): {reference_answer}
            
    		###Score Rubrics: 
            Score 1: If the generated answer is not relevant to the user query and reference answer.
            Score 2: If the generated answer is correct according to reference answer but not relevant to user query.
            Score 3: If the generated answer is relevant to the user query and correct according to reference answer but has some mistakes in facts.
    		Score 4: If the generated answer is relevant to the user query and has the exact same metrics and correct as the reference answer, but it is not as concise.
            Score 5: If the generated answer is relevant to the user query and fully correct according to the reference answer.
    
    		###Feedback:"""

```

prometheus_correctness_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query, a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given. 1. Write a detailed feedback that assesses the quality of the response strictly based on the given score rubric, not evaluating in general. 2. After writing a feedback, write a score that is either 1 or 2 or 3 or 4 or 5. You should refer to the score rubric. 3. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (1 or 2 or 3 or 4 or 5)" 4. Please do not generate any other opening, closing, and explanations. 5. Only evaluate on common things between generated answer and reference answer. Don't evaluate on things which are present in reference answer but not in generated answer. ###The instruction to evaluate: Your task is to evaluate the generated answer and reference answer for the query: {query} ###Generate answer to evaluate: {generated_answer} ###Reference Answer (Score 5): {reference_answer} ###Score Rubrics: Score 1: If the generated answer is not relevant to the user query and reference answer. Score 2: If the generated answer is correct according to reference answer but not relevant to user query. Score 3: If the generated answer is relevant to the user query and correct according to reference answer but has some mistakes in facts. Score 4: If the generated answer is relevant to the user query and has the exact same metrics and correct as the reference answer, but it is not as concise. Score 5: If the generated answer is relevant to the user query and fully correct according to the reference answer. ###Feedback:"""
### Faithfulness Evaluation Prompt¶
In [ ]:
Copied!
```
prometheus_faithfulness_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), an information, a context, and a score rubric representing evaluation criteria are given. 
	        1. You are provided with evaluation task with the help of information, context information to give result based on score rubrics.
            2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 
			3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 
            4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)” 
            5. Please do not generate any other opening, closing, and explanations. 

        ###The instruction to evaluate: Your task is to evaluate if the given piece of information is supported by context.

        ###Information: {query_str} 

        ###Context: {context_str}
            
        ###Score Rubrics: 
        Score YES: If the given piece of information is supported by context.
        Score NO: If the given piece of information is not supported by context
    
        ###Feedback: """

prometheus_faithfulness_refine_prompt_template = """###Task Description: An instruction (might include an Input inside it), a information, a context information, an existing answer, and a score rubric representing a evaluation criteria are given. 
			1. You are provided with evaluation task with the help of information, context information and an existing answer.
            2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general.
			3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 
			4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)" 
			5. Please do not generate any other opening, closing, and explanations. 

			###The instruction to evaluate: If the information is present in the context and also provided with an existing answer.

			###Existing answer: {existing_answer} 

            ###Information: {query_str}

            ###Context: {context_msg}
            
    		###Score Rubrics: 
            Score YES: If the existing answer is already YES or If the Information is present in the context.
            Score NO: If the existing answer is NO and If the Information is not present in the context.
    
    		###Feedback: """

```

prometheus_faithfulness_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), an information, a context, and a score rubric representing evaluation criteria are given. 1. You are provided with evaluation task with the help of information, context information to give result based on score rubrics. 2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)” 5. Please do not generate any other opening, closing, and explanations. ###The instruction to evaluate: Your task is to evaluate if the given piece of information is supported by context. ###Information: {query_str} ###Context: {context_str} ###Score Rubrics: Score YES: If the given piece of information is supported by context. Score NO: If the given piece of information is not supported by context ###Feedback: """ prometheus_faithfulness_refine_prompt_template = """###Task Description: An instruction (might include an Input inside it), a information, a context information, an existing answer, and a score rubric representing a evaluation criteria are given. 1. You are provided with evaluation task with the help of information, context information and an existing answer. 2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)" 5. Please do not generate any other opening, closing, and explanations. ###The instruction to evaluate: If the information is present in the context and also provided with an existing answer. ###Existing answer: {existing_answer} ###Information: {query_str} ###Context: {context_msg} ###Score Rubrics: Score YES: If the existing answer is already YES or If the Information is present in the context. Score NO: If the existing answer is NO and If the Information is not present in the context. ###Feedback: """
### Relevancy Evaluation Prompt¶
In [ ]:
Copied!
```
prometheus_relevancy_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query with response, context, and a score rubric representing evaluation criteria are given. 
            1. You are provided with evaluation task with the help of a query with response and context.
            2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 
			3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 
            4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)” 
            5. Please do not generate any other opening, closing, and explanations. 

        ###The instruction to evaluate: Your task is to evaluate if the response for the query is in line with the context information provided.

        ###Query and Response: {query_str} 

        ###Context: {context_str}
            
        ###Score Rubrics: 
        Score YES: If the response for the query is in line with the context information provided.
        Score NO: If the response for the query is not in line with the context information provided.
    
        ###Feedback: """

prometheus_relevancy_refine_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query with response, context, an existing answer, and a score rubric representing a evaluation criteria are given. 
			1. You are provided with evaluation task with the help of a query with response and context and an existing answer.
            2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 
			3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 
			4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)" 
			5. Please do not generate any other opening, closing, and explanations. 

			###The instruction to evaluate: Your task is to evaluate if the response for the query is in line with the context information provided.

			###Query and Response: {query_str} 

            ###Context: {context_str}
            
    		###Score Rubrics: 
            Score YES: If the existing answer is already YES or If the response for the query is in line with the context information provided.
            Score NO: If the existing answer is NO and If the response for the query is in line with the context information provided.
    
    		###Feedback: """

```

prometheus_relevancy_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query with response, context, and a score rubric representing evaluation criteria are given. 1. You are provided with evaluation task with the help of a query with response and context. 2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)” 5. Please do not generate any other opening, closing, and explanations. ###The instruction to evaluate: Your task is to evaluate if the response for the query is in line with the context information provided. ###Query and Response: {query_str} ###Context: {context_str} ###Score Rubrics: Score YES: If the response for the query is in line with the context information provided. Score NO: If the response for the query is not in line with the context information provided. ###Feedback: """ prometheus_relevancy_refine_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query with response, context, an existing answer, and a score rubric representing a evaluation criteria are given. 1. You are provided with evaluation task with the help of a query with response and context and an existing answer. 2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)" 5. Please do not generate any other opening, closing, and explanations. ###The instruction to evaluate: Your task is to evaluate if the response for the query is in line with the context information provided. ###Query and Response: {query_str} ###Context: {context_str} ###Score Rubrics: Score YES: If the existing answer is already YES or If the response for the query is in line with the context information provided. Score NO: If the existing answer is NO and If the response for the query is in line with the context information provided. ###Feedback: """
Set OpenAI Key for indexing
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY"

from llama_index.llms.openai import OpenAI

gpt4_llm = OpenAI("gpt-4")

```

import os os.environ["OPENAI_API_KEY"] = "YOUR OPENAI API KEY" from llama_index.llms.openai import OpenAI gpt4_llm = OpenAI("gpt-4")
## Define parser function¶
It will be used in correctness evaluator.
In [ ]:
Copied!
```
from typing import Tuple
import re


def parser_function(output_str: str) -> Tuple[float, str]:
    # Pattern to match the feedback and response
    # This pattern looks for any text ending with '[RESULT]' followed by a number
    pattern = r"(.+?) \[RESULT\] (\d)"

    # Using regex to find all matches
    matches = re.findall(pattern, output_str)

    # Check if any match is found
    if matches:
        # Assuming there's only one match in the text, extract feedback and response
        feedback, score = matches[0]
        score = float(score.strip()) if score is not None else score
        return score, feedback.strip()
    else:
        return None, None

```

from typing import Tuple import re def parser_function(output_str: str) -> Tuple[float, str]: # Pattern to match the feedback and response # This pattern looks for any text ending with '[RESULT]' followed by a number pattern = r"(.+?) \\[RESULT\\] (\d)" # Using regex to find all matches matches = re.findall(pattern, output_str) # Check if any match is found if matches: # Assuming there's only one match in the text, extract feedback and response feedback, score = matches[0] score = float(score.strip()) if score is not None else score return score, feedback.strip() else: return None, None
## Define Correctness, FaithFulness, Relevancy Evaluators¶
In [ ]:
Copied!
```
from llama_index.core.evaluation import (
    CorrectnessEvaluator,
    FaithfulnessEvaluator,
    RelevancyEvaluator,
)
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler
import tiktoken


# CorrectnessEvaluator with Prometheus model
prometheus_correctness_evaluator = CorrectnessEvaluator(
    llm=prometheus_llm,
    parser_function=parser_function,
    eval_template=prometheus_correctness_eval_prompt_template,
)

# FaithfulnessEvaluator with Prometheus model
prometheus_faithfulness_evaluator = FaithfulnessEvaluator(
    llm=prometheus_llm,
    eval_template=prometheus_faithfulness_eval_prompt_template,
    refine_template=prometheus_faithfulness_refine_prompt_template,
)

# RelevancyEvaluator with Prometheus model
prometheus_relevancy_evaluator = RelevancyEvaluator(
    llm=prometheus_llm,
    eval_template=prometheus_relevancy_eval_prompt_template,
    refine_template=prometheus_relevancy_refine_prompt_template,
)

# Set the encoding model to `gpt-4` for token counting.
token_counter = TokenCountingHandler(
    tokenizer=tiktoken.encoding_for_model("gpt-4").encode
)

callback_manager = CallbackManager([token_counter])
gpt4_llm.callback_manager = callback_manager

# CorrectnessEvaluator with GPT-4 model
gpt4_correctness_evaluator = CorrectnessEvaluator(
    llm=gpt4_llm,
    # parser_function=parser_function,
)

# FaithfulnessEvaluator with GPT-4 model
gpt4_faithfulness_evaluator = FaithfulnessEvaluator(
    llm=gpt4_llm,
    eval_template=prometheus_faithfulness_eval_prompt_template,
    refine_template=prometheus_faithfulness_refine_prompt_template,
)

# RelevancyEvaluator with GPT-4 model
gpt4_relevancy_evaluator = RelevancyEvaluator(
    llm=gpt4_llm,
    eval_template=prometheus_relevancy_eval_prompt_template,
    refine_template=prometheus_relevancy_refine_prompt_template,
)

# create a dictionary of evaluators
prometheus_evaluators = {
    "correctness": prometheus_correctness_evaluator,
    "faithfulness": prometheus_faithfulness_evaluator,
    "relevancy": prometheus_relevancy_evaluator,
}

gpt4_evaluators = {
    "correctness": gpt4_correctness_evaluator,
    "faithfulness": gpt4_faithfulness_evaluator,
    "relevancy": gpt4_relevancy_evaluator,
}

```

from llama_index.core.evaluation import ( CorrectnessEvaluator, FaithfulnessEvaluator, RelevancyEvaluator, ) from llama_index.core.callbacks import CallbackManager, TokenCountingHandler import tiktoken # CorrectnessEvaluator with Prometheus model prometheus_correctness_evaluator = CorrectnessEvaluator( llm=prometheus_llm, parser_function=parser_function, eval_template=prometheus_correctness_eval_prompt_template, ) # FaithfulnessEvaluator with Prometheus model prometheus_faithfulness_evaluator = FaithfulnessEvaluator( llm=prometheus_llm, eval_template=prometheus_faithfulness_eval_prompt_template, refine_template=prometheus_faithfulness_refine_prompt_template, ) # RelevancyEvaluator with Prometheus model prometheus_relevancy_evaluator = RelevancyEvaluator( llm=prometheus_llm, eval_template=prometheus_relevancy_eval_prompt_template, refine_template=prometheus_relevancy_refine_prompt_template, ) # Set the encoding model to `gpt-4` for token counting. token_counter = TokenCountingHandler( tokenizer=tiktoken.encoding_for_model("gpt-4").encode ) callback_manager = CallbackManager([token_counter]) gpt4_llm.callback_manager = callback_manager # CorrectnessEvaluator with GPT-4 model gpt4_correctness_evaluator = CorrectnessEvaluator( llm=gpt4_llm, # parser_function=parser_function, ) # FaithfulnessEvaluator with GPT-4 model gpt4_faithfulness_evaluator = FaithfulnessEvaluator( llm=gpt4_llm, eval_template=prometheus_faithfulness_eval_prompt_template, refine_template=prometheus_faithfulness_refine_prompt_template, ) # RelevancyEvaluator with GPT-4 model gpt4_relevancy_evaluator = RelevancyEvaluator( llm=gpt4_llm, eval_template=prometheus_relevancy_eval_prompt_template, refine_template=prometheus_relevancy_refine_prompt_template, ) # create a dictionary of evaluators prometheus_evaluators = { "correctness": prometheus_correctness_evaluator, "faithfulness": prometheus_faithfulness_evaluator, "relevancy": prometheus_relevancy_evaluator, } gpt4_evaluators = { "correctness": gpt4_correctness_evaluator, "faithfulness": gpt4_faithfulness_evaluator, "relevancy": gpt4_relevancy_evaluator, }
## Let's create a function to create `query_engine` and `rag_dataset` for different datasets.¶
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import LabelledRagDataset
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex


def create_query_engine_rag_dataset(dataset_path):
    rag_dataset = LabelledRagDataset.from_json(
        f"{dataset_path}/rag_dataset.json"
    )
    documents = SimpleDirectoryReader(
        input_dir=f"{dataset_path}/source_files"
    ).load_data()

    index = VectorStoreIndex.from_documents(documents=documents)
    query_engine = index.as_query_engine()

    return query_engine, rag_dataset

```

from llama_index.core.llama_dataset import LabelledRagDataset from llama_index.core import SimpleDirectoryReader, VectorStoreIndex def create_query_engine_rag_dataset(dataset_path): rag_dataset = LabelledRagDataset.from_json( f"{dataset_path}/rag_dataset.json" ) documents = SimpleDirectoryReader( input_dir=f"{dataset_path}/source_files" ).load_data() index = VectorStoreIndex.from_documents(documents=documents) query_engine = index.as_query_engine() return query_engine, rag_dataset
## Function to run batch evaluations on defined evaluators¶
In [ ]:
Copied!
```
from llama_index.core.evaluation import BatchEvalRunner


async def batch_eval_runner(
    evaluators, query_engine, questions, reference=None, num_workers=8
):
    batch_runner = BatchEvalRunner(
        evaluators, workers=num_workers, show_progress=True
    )

    eval_results = await batch_runner.aevaluate_queries(
        query_engine, queries=questions, reference=reference
    )

    return eval_results

```

from llama_index.core.evaluation import BatchEvalRunner async def batch_eval_runner( evaluators, query_engine, questions, reference=None, num_workers=8 ): batch_runner = BatchEvalRunner( evaluators, workers=num_workers, show_progress=True ) eval_results = await batch_runner.aevaluate_queries( query_engine, queries=questions, reference=reference ) return eval_results
## Function to check the distribution of scores¶
In [ ]:
Copied!
```
from collections import Counter
from typing import List, Dict


def get_scores_distribution(scores: List[float]) -> Dict[str, float]:
    # Counting the occurrences of each score
    score_counts = Counter(scores)

    # Total number of scores
    total_scores = len(scores)

    # Calculating the percentage distribution
    percentage_distribution = {
        score: (count / total_scores) * 100
        for score, count in score_counts.items()
    }

    return percentage_distribution

```

from collections import Counter from typing import List, Dict def get_scores_distribution(scores: List[float]) -> Dict[str, float]: # Counting the occurrences of each score score_counts = Counter(scores) # Total number of scores total_scores = len(scores) # Calculating the percentage distribution percentage_distribution = { score: (count / total_scores) * 100 for score, count in score_counts.items() } return percentage_distribution
## Function to check correctness, faithfulness and relevancy evaluation score¶
In [ ]:
Copied!
```
def get_eval_results(key, eval_results):
    results = eval_results[key]
    correct = 0
    for result in results:
        if result.passing:
            correct += 1
    score = correct / len(results)
    print(f"{key} Score: {round(score, 2)}")
    return score

```

def get_eval_results(key, eval_results): results = eval_results[key] correct = 0 for result in results: if result.passing: correct += 1 score = correct / len(results) print(f"{key} Score: {round(score, 2)}") return score
## Function to compute `Hamming Distance`.¶
In [ ]:
Copied!
```
def hamming_distance(list1, list2):
    if len(list1) != len(list2):
        raise ValueError("Lists must be of the same length")
    return sum(el1 != el2 for el1, el2 in zip(list1, list2))

```

def hamming_distance(list1, list2): if len(list1) != len(list2): raise ValueError("Lists must be of the same length") return sum(el1 != el2 for el1, el2 in zip(list1, list2))
## Evaluation on PaulGraham Essay text¶
In [ ]:
Copied!
```
query_engine, rag_dataset = create_query_engine_rag_dataset(
    "./data/paul_graham"
)

```

query_engine, rag_dataset = create_query_engine_rag_dataset( "./data/paul_graham" )
In [ ]:
Copied!
```
# Get questions for evaluation
questions = [example.query for example in rag_dataset.examples]

# Get reference answers for evaluation
reference = [[example.reference_answer] for example in rag_dataset.examples]

```

# Get questions for evaluation questions = [example.query for example in rag_dataset.examples] # Get reference answers for evaluation reference = [[example.reference_answer] for example in rag_dataset.examples]
### Compute Correctness, Faithfulness and Relevancy Evaluation¶
In [ ]:
Copied!
```
prometheus_eval_results = await batch_eval_runner(
    prometheus_evaluators, query_engine, questions, reference
)

```

prometheus_eval_results = await batch_eval_runner( prometheus_evaluators, query_engine, questions, reference )
```
100%|██████████| 44/44 [00:30<00:00,  1.43it/s]
100%|██████████| 132/132 [01:56<00:00,  1.13it/s]

```

In [ ]:
Copied!
```
gpt4_eval_results = await batch_eval_runner(
    gpt4_evaluators, query_engine, questions, reference
)

```

gpt4_eval_results = await batch_eval_runner( gpt4_evaluators, query_engine, questions, reference )
```
100%|██████████| 44/44 [00:26<00:00,  1.66it/s]
100%|██████████| 132/132 [02:32<00:00,  1.16s/it]

```

### Correctness Evaluation score distribution with Prometheus Evaluator.¶
In [ ]:
Copied!
```
prometheus_scores = [
    result.score for result in prometheus_eval_results["correctness"]
]
get_scores_distribution(prometheus_scores)

```

prometheus_scores = [ result.score for result in prometheus_eval_results["correctness"] ] get_scores_distribution(prometheus_scores)
Out[ ]:
```
{3.0: 50.0,
 1.0: 43.18181818181818,
 5.0: 2.272727272727273,
 4.0: 4.545454545454546}
```

### Correctness Evaluation score distribution with GPT-4 Evaluator.¶
In [ ]:
Copied!
```
gpt4_scores = [result.score for result in gpt4_eval_results["correctness"]]
get_scores_distribution(gpt4_scores)

```

gpt4_scores = [result.score for result in gpt4_eval_results["correctness"]] get_scores_distribution(gpt4_scores)
Out[ ]:
```
{4.5: 50.0,
 5.0: 34.090909090909086,
 2.5: 9.090909090909092,
 4.0: 2.272727272727273,
 3.5: 4.545454545454546}
```

### Feedback comparison between prometheus and gpt-4.¶
In [ ]:
Copied!
```
query = prometheus_eval_results["correctness"][0].query
response = prometheus_eval_results["correctness"][0].response
reference_answer = reference[0][0]

# prometheus feedback and score
prometheus_feedback = prometheus_eval_results["correctness"][0].feedback
prometheus_score = prometheus_eval_results["correctness"][0].score

# GPT4 feedback and score
gpt4_feedback = gpt4_eval_results["correctness"][0].feedback
gpt4_score = gpt4_eval_results["correctness"][0].score

```

query = prometheus_eval_results["correctness"][0].query response = prometheus_eval_results["correctness"][0].response reference_answer = reference[0][0] # prometheus feedback and score prometheus_feedback = prometheus_eval_results["correctness"][0].feedback prometheus_score = prometheus_eval_results["correctness"][0].score # GPT4 feedback and score gpt4_feedback = gpt4_eval_results["correctness"][0].feedback gpt4_score = gpt4_eval_results["correctness"][0].score
In [ ]:
Copied!
```
print(f"Query: {query} \n\n")
print(f"Generated Answer: {response} \n\n")
print(f"Reference Answer: {reference_answer} \n\n")
print(
    f"Prometheus Feedback: {prometheus_feedback} \n\n {prometheus_score} \n\n"
)
print(f"GPT-4 Feedback: {gpt4_feedback} \n\n {gpt4_score}")

```

print(f"Query: {query} \n\n") print(f"Generated Answer: {response} \n\n") print(f"Reference Answer: {reference_answer} \n\n") print( f"Prometheus Feedback: {prometheus_feedback} \n\n {prometheus_score} \n\n" ) print(f"GPT-4 Feedback: {gpt4_feedback} \n\n {gpt4_score}")
```
Query: In the essay, the author mentions his early experiences with programming. Describe the first computer he used for programming, the language he used, and the challenges he faced. 


Generated Answer: The author mentions that the first computer he used for programming was the IBM 1401, which was located in the basement of his junior high school. He used an early version of Fortran as the programming language. The author faced challenges in figuring out what to do with the computer, as the only form of input was data stored on punched cards, and he didn't have any. Additionally, he didn't know enough math to do anything interesting with the computer. 


Reference Answer: The first computer the author used for programming was the IBM 1401, which was used by his school district for data processing. He started using it in 9th grade, around the age of 13 or 14. The programming language he used was an early version of Fortran. The author faced several challenges while using this computer. The only form of input to programs was data stored on punched cards, and he didn't have any data stored on punched cards. The only other option was to do things that didn't rely on any input, like calculate approximations of pi, but he didn't know enough math to do anything interesting of that type. Therefore, he couldn't figure out what to do with it and in retrospect, he believes there's not much he could have done with it. 


Prometheus Feedback: The generated response is relevant to the user query and correctly describes the first computer the author used for programming, the programming language he used, and the challenges he faced. However, it has some inaccuracies in the details. The author did not use the IBM 1401 in the basement of his junior high school, but rather in 9th grade, around the age of 13 or 14. The author did not have any data stored on punched cards, but the only form of input was data stored on punched cards. The author did not know enough math to do anything interesting with the computer, but he didn't know enough math to do anything interesting of that type. So the overall score is 3. 

 3.0 


GPT-4 Feedback: The generated answer is highly relevant and almost completely accurate. It correctly identifies the first computer the author used (IBM 1401), the programming language (Fortran), and the challenges he faced (lack of input data and insufficient math knowledge). However, it omits the detail about the author's age and grade level when he started programming, which was included in the reference answer. 

 4.5

```

#### Observation:¶
The feedback from Prometheus is more detailed, noting that certain specifics were omitted in the generated response, resulting in a score of `3.0`. Conversely, GPT-4's feedback is broader and less specific, awarding a score of `5.0`, despite the absence of some details.
### Prometheus Faithfulness and Relevancy Evaluation scores.¶
In [ ]:
Copied!
```
_ = get_eval_results("faithfulness", prometheus_eval_results)

_ = get_eval_results("relevancy", prometheus_eval_results)

```

_ = get_eval_results("faithfulness", prometheus_eval_results) _ = get_eval_results("relevancy", prometheus_eval_results)
```
faithfulness Score: 0.75
relevancy Score: 0.86

```

### GPT-4 Faithfulness and Relevancy Evaluation scores.¶
In [ ]:
Copied!
```
_ = get_eval_results("faithfulness", gpt4_eval_results)

_ = get_eval_results("relevancy", gpt4_eval_results)

```

_ = get_eval_results("faithfulness", gpt4_eval_results) _ = get_eval_results("relevancy", gpt4_eval_results)
```
faithfulness Score: 0.98
relevancy Score: 0.95

```

### Hamming Distance comparison between Prometheus and GPT-4¶
(Lower the better)
In [ ]:
Copied!
```
prometheus_faithfulness_scores = [
    result.score for result in prometheus_eval_results["faithfulness"]
]
prometheus_relevancy_scores = [
    result.score for result in prometheus_eval_results["relevancy"]
]

gpt4_faithfulness_scores = [
    result.score for result in gpt4_eval_results["faithfulness"]
]
gpt4_relevancy_scores = [
    result.score for result in gpt4_eval_results["relevancy"]
]

faithfulness_hamming_distance = hamming_distance(
    prometheus_faithfulness_scores, gpt4_faithfulness_scores
)
relevancy_hamming_distance = hamming_distance(
    prometheus_relevancy_scores, gpt4_relevancy_scores
)

print(f"Faithfulness Hamming Distance: {faithfulness_hamming_distance}")
print(f"Relevancy Hamming Distance: {relevancy_hamming_distance}")

```

prometheus_faithfulness_scores = [ result.score for result in prometheus_eval_results["faithfulness"] ] prometheus_relevancy_scores = [ result.score for result in prometheus_eval_results["relevancy"] ] gpt4_faithfulness_scores = [ result.score for result in gpt4_eval_results["faithfulness"] ] gpt4_relevancy_scores = [ result.score for result in gpt4_eval_results["relevancy"] ] faithfulness_hamming_distance = hamming_distance( prometheus_faithfulness_scores, gpt4_faithfulness_scores ) relevancy_hamming_distance = hamming_distance( prometheus_relevancy_scores, gpt4_relevancy_scores ) print(f"Faithfulness Hamming Distance: {faithfulness_hamming_distance}") print(f"Relevancy Hamming Distance: {relevancy_hamming_distance}")
```
Faithfulness Hamming Distance: 10
Relevancy Hamming Distance: 8

```

#### Observation:¶
The comparison reveals that approximately `77%` and `81%` of the scores are common in case of both `Faithfulness` and `Relevancy` between Prometheus and GPT-4 evaluations respectively. This indicates a decent correlation in terms of faithfulness and relevance scoring between the Prometheus and GPT-4 models.
### GPT-4 Cost analysis¶
In [ ]:
Copied!
```
prompt_token_count = token_counter.prompt_llm_token_count
completion_token_count = token_counter.completion_llm_token_count

total_cost_paul_graham_essay = (
    prompt_token_count * 0.03 + completion_token_count * 0.06
) / 1000

token_counter.reset_counts()

```

prompt_token_count = token_counter.prompt_llm_token_count completion_token_count = token_counter.completion_llm_token_count total_cost_paul_graham_essay = ( prompt_token_count * 0.03 + completion_token_count * 0.06 ) / 1000 token_counter.reset_counts()
## Evaluation with Llama2 paper¶
In [ ]:
Copied!
```
query_engine, rag_dataset = create_query_engine_rag_dataset("./data/llama2")

```

query_engine, rag_dataset = create_query_engine_rag_dataset("./data/llama2")
In [ ]:
Copied!
```
questions = [example.query for example in rag_dataset.examples]

```

questions = [example.query for example in rag_dataset.examples]
In [ ]:
Copied!
```
reference = [[example.reference_answer] for example in rag_dataset.examples]

```

reference = [[example.reference_answer] for example in rag_dataset.examples]
### Compute Correctness, Faithfulness and Relevancy Evaluation¶
In [ ]:
Copied!
```
prometheus_eval_results = await batch_eval_runner(
    prometheus_evaluators, query_engine, questions, reference
)

```

prometheus_eval_results = await batch_eval_runner( prometheus_evaluators, query_engine, questions, reference )
```
100%|██████████| 100/100 [01:02<00:00,  1.61it/s]
100%|██████████| 300/300 [04:34<00:00,  1.09it/s]

```

In [ ]:
Copied!
```
gpt4_eval_results = await batch_eval_runner(
    gpt4_evaluators, query_engine, questions, reference
)

```

gpt4_eval_results = await batch_eval_runner( gpt4_evaluators, query_engine, questions, reference )
```
100%|██████████| 100/100 [01:06<00:00,  1.51it/s]
100%|██████████| 300/300 [06:22<00:00,  1.27s/it]

```

### Correctness Evaluation score distribution with Prometheus Evaluator.¶
In [ ]:
Copied!
```
prometheus_scores = [
    result.score for result in prometheus_eval_results["correctness"]
]
get_scores_distribution(prometheus_scores)

```

prometheus_scores = [ result.score for result in prometheus_eval_results["correctness"] ] get_scores_distribution(prometheus_scores)
Out[ ]:
```
{3.0: 56.00000000000001, 1.0: 26.0, 5.0: 9.0, 4.0: 8.0, 2.0: 1.0}
```

### Correctness Evaluation score distribution with GPT-4 Evaluator.¶
In [ ]:
Copied!
```
gpt4_scores = [result.score for result in gpt4_eval_results["correctness"]]
get_scores_distribution(gpt4_scores)

```

gpt4_scores = [result.score for result in gpt4_eval_results["correctness"]] get_scores_distribution(gpt4_scores)
Out[ ]:
```
{4.5: 57.99999999999999,
 1.0: 6.0,
 4.0: 12.0,
 5.0: 10.0,
 2.0: 5.0,
 3.5: 5.0,
 2.5: 3.0,
 3.0: 1.0}
```

### Feedback comparison between prometheus and gpt-4 for correctness.¶
In [ ]:
Copied!
```
query = prometheus_eval_results["correctness"][0].query
response = prometheus_eval_results["correctness"][0].response
reference_answer = reference[0][0]

# prometheus feedback and score
prometheus_feedback = prometheus_eval_results["correctness"][0].feedback
prometheus_score = prometheus_eval_results["correctness"][0].score

# GPT4 feedback and score
gpt4_feedback = gpt4_eval_results["correctness"][0].feedback
gpt4_score = gpt4_eval_results["correctness"][0].score

print(f"Query: {query} \n\n")
print(f"Generated Answer: {response} \n\n")
print(f"Reference Answer: {reference_answer} \n\n")
print(
    f"Prometheus Feedback: {prometheus_feedback} \n\n {prometheus_score} \n\n"
)
print(f"GPT-4 Feedback: {gpt4_feedback} \n\n {gpt4_score}")

```

query = prometheus_eval_results["correctness"][0].query response = prometheus_eval_results["correctness"][0].response reference_answer = reference[0][0] # prometheus feedback and score prometheus_feedback = prometheus_eval_results["correctness"][0].feedback prometheus_score = prometheus_eval_results["correctness"][0].score # GPT4 feedback and score gpt4_feedback = gpt4_eval_results["correctness"][0].feedback gpt4_score = gpt4_eval_results["correctness"][0].score print(f"Query: {query} \n\n") print(f"Generated Answer: {response} \n\n") print(f"Reference Answer: {reference_answer} \n\n") print( f"Prometheus Feedback: {prometheus_feedback} \n\n {prometheus_score} \n\n" ) print(f"GPT-4 Feedback: {gpt4_feedback} \n\n {gpt4_score}")
```
Query: Based on the abstract of "Llama 2: Open Foundation and Fine-Tuned Chat Models," what are the two primary objectives achieved in this work, and what is the range of parameters for the large language models developed? 


Generated Answer: The two primary objectives achieved in this work are the development and release of Llama 2, a collection of pretrained and fine-tuned large language models (LLMs), and the optimization of these models for dialogue use cases. The range of parameters for the large language models developed is from 7 billion to 70 billion. 


Reference Answer: The two primary objectives achieved in the work described in the abstract of "Llama 2: Open Foundation and Fine-Tuned Chat Models" are:

1. The development and release of a collection of pretrained and fine-tuned large language models (LLMs) specifically optimized for dialogue use cases.
2. The demonstration that these fine-tuned LLMs, referred to as Llama 2-Chat, outperform open-source chat models on most benchmarks tested and may be a suitable substitute for closed-source models, particularly in terms of helpfulness and safety based on human evaluations.

The range of parameters for the large language models developed in this work is from 7 billion to 70 billion parameters. 


Prometheus Feedback: The generated response is relevant to the user query and correctly identifies the two primary objectives of the work described in the abstract of "Llama  2: Open Foundation and Fine-Tuned Chat Models." However, it does not mention the demonstration of the fine-tuned LLMs outperforming open-source chat models on most benchmarks tested, which is a key point in the reference response. The range of parameters for the large language models developed is correctly identified, but the response does not mention the specific models referred to as Llama 2-Chat. So the overall score is 3. 

 3.0 


GPT-4 Feedback: The generated answer is relevant and almost fully correct. It correctly identifies the two primary objectives and the range of parameters for the large language models. However, it misses the detail about Llama 2-Chat outperforming other models on most benchmarks and potentially being a suitable substitute for closed-source models. 

 4.5

```

#### Observation:¶
The feedback from Prometheus is little more precise compared to GPT-4 and it penalises and gives a score of `3.0` but GPT-4 gives a score of `4.5`.
### Prometheus Faithfulness and Relevancy Evaluation scores.¶
In [ ]:
Copied!
```
_ = get_eval_results("faithfulness", prometheus_eval_results)

_ = get_eval_results("relevancy", prometheus_eval_results)

```

_ = get_eval_results("faithfulness", prometheus_eval_results) _ = get_eval_results("relevancy", prometheus_eval_results)
```
faithfulness Score: 0.39
relevancy Score: 0.57

```

### GPT-4 Faithfulness and Relevancy Evaluation scores.¶
In [ ]:
Copied!
```
_ = get_eval_results("faithfulness", gpt4_eval_results)

_ = get_eval_results("relevancy", gpt4_eval_results)

```

_ = get_eval_results("faithfulness", gpt4_eval_results) _ = get_eval_results("relevancy", gpt4_eval_results)
```
faithfulness Score: 0.93
relevancy Score: 0.98

```

### Hamming Distance comparison between Prometheus and GPT-4¶
In [ ]:
Copied!
```
prometheus_faithfulness_scores = [
    result.score for result in prometheus_eval_results["faithfulness"]
]
prometheus_relevancy_scores = [
    result.score for result in prometheus_eval_results["relevancy"]
]

gpt4_faithfulness_scores = [
    result.score for result in gpt4_eval_results["faithfulness"]
]
gpt4_relevancy_scores = [
    result.score for result in gpt4_eval_results["relevancy"]
]

faithfulness_hamming_distance = hamming_distance(
    prometheus_faithfulness_scores, gpt4_faithfulness_scores
)
relevancy_hamming_distance = hamming_distance(
    prometheus_relevancy_scores, gpt4_relevancy_scores
)

print(f"Faithfulness Hamming Distance: {faithfulness_hamming_distance}")
print(f"Relevancy Hamming Distance: {relevancy_hamming_distance}")

```

prometheus_faithfulness_scores = [ result.score for result in prometheus_eval_results["faithfulness"] ] prometheus_relevancy_scores = [ result.score for result in prometheus_eval_results["relevancy"] ] gpt4_faithfulness_scores = [ result.score for result in gpt4_eval_results["faithfulness"] ] gpt4_relevancy_scores = [ result.score for result in gpt4_eval_results["relevancy"] ] faithfulness_hamming_distance = hamming_distance( prometheus_faithfulness_scores, gpt4_faithfulness_scores ) relevancy_hamming_distance = hamming_distance( prometheus_relevancy_scores, gpt4_relevancy_scores ) print(f"Faithfulness Hamming Distance: {faithfulness_hamming_distance}") print(f"Relevancy Hamming Distance: {relevancy_hamming_distance}")
```
Faithfulness Hamming Distance: 58
Relevancy Hamming Distance: 41

```

#### Observation:¶
The comparison reveals that approximately `44%` of the scores in case of `Faithfulness` and `63%` in case of `Relevancy` are common between Prometheus and GPT-4 evaluations. This indicates a decent amount of correlation in terms of faithfulness and relevance scoring between the Prometheus and GPT-4 models.
### Feedback comparison between prometheus and gpt-4 for faithfulness and relevancy¶
In [ ]:
Copied!
```
# Get the query
query = questions[0]

# Get the response/ generated answer for the query
response = prometheus_eval_results["faithfulness"][0].response
# Get the retrieved contexts as they are used for faithfulness and relevancy
contexts = prometheus_eval_results["faithfulness"][0].contexts

# Get the faithfulness and relevancy feedbacks from prometheus model
prometheus_faithfulness_feedback = prometheus_eval_results["faithfulness"][
    0
].feedback
prometheus_relevancy_feedback = prometheus_eval_results["relevancy"][
    0
].feedback

# Get the faithfulness and relevancy feedbacks from gpt4 model
gpt4_faithfulness_feedback = gpt4_eval_results["faithfulness"][0].feedback
gpt4_relevancy_feedback = gpt4_eval_results["relevancy"][0].feedback

# Get the failthfulness and relevancy scores from prometheus model
prometheus_faithfulness_score = prometheus_eval_results["faithfulness"][
    0
].score
prometheus_relevancy_score = prometheus_eval_results["relevancy"][0].score

# Get the faithfulness and relevancy scores from gpt4 model
gpt4_faithfulness_score = gpt4_eval_results["faithfulness"][0].score
gpt4_relevancy_score = gpt4_eval_results["relevancy"][0].score

```

# Get the query query = questions[0] # Get the response/ generated answer for the query response = prometheus_eval_results["faithfulness"][0].response # Get the retrieved contexts as they are used for faithfulness and relevancy contexts = prometheus_eval_results["faithfulness"][0].contexts # Get the faithfulness and relevancy feedbacks from prometheus model prometheus_faithfulness_feedback = prometheus_eval_results["faithfulness"][ 0 ].feedback prometheus_relevancy_feedback = prometheus_eval_results["relevancy"][ 0 ].feedback # Get the faithfulness and relevancy feedbacks from gpt4 model gpt4_faithfulness_feedback = gpt4_eval_results["faithfulness"][0].feedback gpt4_relevancy_feedback = gpt4_eval_results["relevancy"][0].feedback # Get the failthfulness and relevancy scores from prometheus model prometheus_faithfulness_score = prometheus_eval_results["faithfulness"][ 0 ].score prometheus_relevancy_score = prometheus_eval_results["relevancy"][0].score # Get the faithfulness and relevancy scores from gpt4 model gpt4_faithfulness_score = gpt4_eval_results["faithfulness"][0].score gpt4_relevancy_score = gpt4_eval_results["relevancy"][0].score
In [ ]:
Copied!
```
print(f"Query: {query} \n\n")
print(f"Generated Answer: {response}")

```

print(f"Query: {query} \n\n") print(f"Generated Answer: {response}")
```
Query: Based on the abstract of "Llama 2: Open Foundation and Fine-Tuned Chat Models," what are the two primary objectives achieved in this work, and what is the range of parameters for the large language models developed? 


Generated Answer: The two primary objectives achieved in this work are the development and release of Llama 2, a collection of pretrained and fine-tuned large language models (LLMs), and the optimization of these models for dialogue use cases. The range of parameters for the large language models developed is from 7 billion to 70 billion.

```

In [ ]:
Copied!
```
print(f"Context-1: {contexts[0]}")

```

print(f"Context-1: {contexts[0]}")
```
Context-1: Llama 2 : Open Foundation and Fine-Tuned Chat Models
Hugo Touvron∗Louis Martin†Kevin Stone†
Peter Albert Amjad Almahairi Yasmine Babaei Nikolay Bashlykov Soumya Batra
Prajjwal Bhargava Shruti Bhosale Dan Bikel Lukas Blecher Cristian Canton Ferrer Moya Chen
Guillem Cucurull David Esiobu Jude Fernandes Jeremy Fu Wenyin Fu Brian Fuller
Cynthia Gao Vedanuj Goswami Naman Goyal Anthony Hartshorn Saghar Hosseini Rui Hou
Hakan Inan Marcin Kardas Viktor Kerkez Madian Khabsa Isabel Kloumann Artem Korenev
Punit Singh Koura Marie-Anne Lachaux Thibaut Lavril Jenya Lee Diana Liskovich
Yinghai Lu Yuning Mao Xavier Martinet Todor Mihaylov Pushkar Mishra
Igor Molybog Yixin Nie Andrew Poulton Jeremy Reizenstein Rashi Rungta Kalyan Saladi
Alan Schelten Ruan Silva Eric Michael Smith Ranjan Subramanian Xiaoqing Ellen Tan Binh Tang
Ross Taylor Adina Williams Jian Xiang Kuan Puxin Xu Zheng Yan Iliyan Zarov Yuchen Zhang
Angela Fan Melanie Kambadur Sharan Narang Aurelien Rodriguez Robert Stojnic
Sergey Edunov Thomas Scialom∗
GenAI, Meta
Abstract
In this work, we develop and release Llama 2, a collection of pretrained and fine-tuned
large language models (LLMs) ranging in scale from 7 billion to 70 billion parameters.
Our fine-tuned LLMs, called Llama 2-Chat , are optimized for dialogue use cases. Our
models outperform open-source chat models on most benchmarks we tested, and based on
ourhumanevaluationsforhelpfulnessandsafety,maybeasuitablesubstituteforclosed-
source models. We provide a detailed description of our approach to fine-tuning and safety
improvements of Llama 2-Chat in order to enable the community to build on our work and
contribute to the responsible development of LLMs.
∗Equal contribution, corresponding authors: {tscialom, htouvron}@meta.com
†Second author
Contributions for all the authors can be found in Section A.1.arXiv:2307.09288v2  [cs.CL]  19 Jul 2023

```

In [ ]:
Copied!
```
print(f"Context-2: {contexts[1]}")

```

print(f"Context-2: {contexts[1]}")
```
Context-2: (2021)alsoilluminatesthedifficultiestiedtochatbot-oriented
LLMs, with concerns ranging from privacy to misleading expertise claims. Deng et al. (2023) proposes
a taxonomic framework to tackle these issues, and Bergman et al. (2022) delves into the balance between
potential positive and negative impacts from releasing dialogue models.
InvestigationsintoredteamingrevealspecificchallengesintunedLLMs,withstudiesbyGangulietal.(2022)
and Zhuoet al. (2023) showcasing a variety ofsuccessful attack typesand their effects onthe generation of
harmful content. National security agencies and various researchers, such as (Mialon et al., 2023), have also
raisedredflagsaroundadvancedemergentmodelbehaviors,cyberthreats,andpotentialmisuseinareaslike
biological warfare. Lastly, broader societal issues like job displacement due to accelerated AI research and an
over-reliance on LLMs leading to training data degradation are also pertinent considerations (Acemoglu
andRestrepo,2018;AutorandSalomons,2018;Webb,2019;Shumailovetal.,2023). Wearecommittedto
continuing our work engaging with the broader policy, academic, and industry community on these issues.
7 Conclusion
Inthisstudy,wehaveintroduced Llama 2,anewfamilyofpretrainedandfine-tunedmodelswithscales
of7billionto70billionparameters. Thesemodelshavedemonstratedtheircompetitivenesswithexisting
open-source chat models, as well as competency that is equivalent to some proprietary models on evaluation
setsweexamined,althoughtheystilllagbehindothermodelslikeGPT-4. Wemeticulouslyelaboratedonthe
methodsandtechniquesappliedinachievingourmodels,withaheavyemphasisontheiralignmentwiththe
principlesofhelpfulnessandsafety. Tocontributemoresignificantlytosocietyandfosterthepaceofresearch,
wehaveresponsiblyopenedaccessto Llama 2 andLlama 2-Chat . Aspartofourongoingcommitmentto
transparency and safety, we plan to make further improvements to Llama 2-Chat in future work.
36

```

In [ ]:
Copied!
```
print(
    f"Prometheus Faithfulness Feedback: {prometheus_faithfulness_feedback}\n\n"
)
print(f"Prometheus Faithfulness Score: {prometheus_faithfulness_score}\n\n")
print(f"Prometheus Relevancy Feedback: {prometheus_relevancy_feedback}\n\n")
print(f"Prometheus Relevancy Score: {prometheus_relevancy_score}")

```

print( f"Prometheus Faithfulness Feedback: {prometheus_faithfulness_feedback}\n\n" ) print(f"Prometheus Faithfulness Score: {prometheus_faithfulness_score}\n\n") print(f"Prometheus Relevancy Feedback: {prometheus_relevancy_feedback}\n\n") print(f"Prometheus Relevancy Score: {prometheus_relevancy_score}")
```
Prometheus Faithfulness Feedback: 
        The information provided in the context is not supported by the given information. The context is about the development and release of Llama 2, a collection of pretrained and fine-tuned large language models (LLMs), and the optimization of these models for dialogue use cases. However, the information provided in the context does not align with the given information. The context does not mention the range of parameters for the large language models developed, which is the primary objective mentioned in the information. The context only talks about the development and release of Llama 2 and its optimization for dialogue use cases, but it does not provide any information about the range of parameters for the large language models developed. So the overall score is NO. [RESULT] NO


Prometheus Faithfulness Score: 0.0


Prometheus Relevancy Feedback: 
        The response is not in line with the context information provided. The query asked for the two primary objectives achieved in the work and the range of parameters for the large language models developed. However, the response provided the abstract of the paper and mentioned the authors, which is not relevant to the query. The response also did not mention the two primary objectives achieved in the work or the range of parameters for the large language models developed. So the overall score is NO. [RESULT] NO


Prometheus Relevancy Score: 0.0

```

#### If you compare the feedback and contexts, there is mention of range of parameters in the context and response but the feedback says the model could not find such information.¶
In [ ]:
Copied!
```
print(f"GPT-4 Faithfulness Feedback: {gpt4_faithfulness_feedback}\n\n")
print(f"GPT-4 Faithfulness Score: {gpt4_faithfulness_score}\n\n")
print(f"GPT-4 Relevancy Feedback: {gpt4_relevancy_feedback}\n\n")
print(f"GPT-4 Relevancy Score: {gpt4_relevancy_score}")

```

print(f"GPT-4 Faithfulness Feedback: {gpt4_faithfulness_feedback}\n\n") print(f"GPT-4 Faithfulness Score: {gpt4_faithfulness_score}\n\n") print(f"GPT-4 Relevancy Feedback: {gpt4_relevancy_feedback}\n\n") print(f"GPT-4 Relevancy Score: {gpt4_relevancy_score}")
```
GPT-4 Faithfulness Feedback: The given piece of information is well supported by the context. The context clearly states that Llama 2, a collection of pretrained and fine-tuned large language models (LLMs), was developed and released. It also mentions that these models range in scale from 7 billion to 70 billion parameters. Furthermore, the context confirms that these models are optimized for dialogue use cases. Therefore, the information provided is accurate and is corroborated by the context. [RESULT] YES


GPT-4 Faithfulness Score: 1.0


GPT-4 Relevancy Feedback: The response accurately reflects the context provided. The response correctly identifies the two primary objectives of the work as the development and release of Llama 2, a collection of pretrained and fine-tuned large language models (LLMs), and the optimization of these models for dialogue use cases. This is in line with the information provided in the abstract of the context. The response also correctly states the range of parameters for the large language models developed as being from 7 billion to 70 billion, which is also confirmed in the context. Therefore, the response is in line with the context information provided. [RESULT] YES


GPT-4 Relevancy Score: 1.0

```

#### GPT-4 Evaluates it correctly, unlike prometheus model.¶
### GPT-4 Cost analysis¶
In [ ]:
Copied!
```
prompt_token_count = token_counter.prompt_llm_token_count
completion_token_count = token_counter.completion_llm_token_count

total_cost_llama2 = (
    prompt_token_count * 0.03 + completion_token_count * 0.06
) / 1000

```

prompt_token_count = token_counter.prompt_llm_token_count completion_token_count = token_counter.completion_llm_token_count total_cost_llama2 = ( prompt_token_count * 0.03 + completion_token_count * 0.06 ) / 1000
## Total Cost Analysis¶
### Prometheus Model - `$2.167` for `144` queries (`44` for Paul Graham Essay and `100` for Llama2 paper) which accounts to `$0.015` per query.¶
### GPT4 Model - `$22` (total_cost_paul_graham_essay + total_cost_llama2) - which accounts to `$0.15` per query.¶
## Observation:¶
  1. The cost for evaluation (approx.): `$2.167` for Prometheus Model and `$22` for GPT4.
  2. The Prometheus model, though offering more detailed feedback than GPT-4, occasionally provides incorrect feedback, necessitating cautious application.
  3. If a generated answer lacks certain facts present in the reference answer, the Prometheus model applies stricter penalties to scores than GPT-4.
  4. The faithfulness and relevancy feedback of Promethes shows more hallucinations/ wrong interpretations in the feedback compared to GPT-4.
  5. The commonality between faithfulness and relevancy scores of Promethes and GPT-4 is different across two datasets and so should be used cautiously in production.


Note: The endpoint on HF is served on AWS Nvidia A100G · 1x GPU · 80 GB which costs $6.5/h. We used Prometheus model for the analysis here. We also made similar analysis with GPTQ Quantized version of Prometheus model and observed abit more hallucinations in feedback compared to original unquantized model. Thanks to authors of the paper and Tom Jobbins for providing the quantized version of the model.
