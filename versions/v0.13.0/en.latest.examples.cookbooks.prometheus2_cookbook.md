![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Prometheus-2 Cookbook¶
In this notebook we will demonstrate usage of Prometheus 2: An Open Source Language Model Specialized in Evaluating Other Language Models.
#### Abstract from the paper:¶
Proprietary LMs such as GPT-4 are often employed to assess the quality of responses from various LMs. However, concerns including transparency, controllability, and affordability strongly motivate the development of open-source LMs specialized in evaluations. On the other hand, existing open evaluator LMs exhibit critical shortcomings: 1) they issue scores that significantly diverge from those assigned by humans, and 2) they lack the flexibility to perform both direct assessment and pairwise ranking, the two most prevalent forms of assessment. Additionally, they do not possess the ability to evaluate based on custom evaluation criteria, focusing instead on general attributes like helpfulness and harmlessness. To address these issues, we introduce Prometheus 2, a more powerful evaluator LM than its predecessor that closely mirrors human and GPT-4 judgements. Moreover, it is capable of processing both direct assessment and pair-wise ranking formats grouped with a user-defined evaluation criteria. On four direct assessment benchmarks and four pairwise ranking benchmarks, Prometheus 2 scores the highest correlation and agreement with humans and proprietary LM judges among all tested open evaluator LMs.
#### Note: The base models for building Prometheus-2 are Mistral-7B and Mixtral8x7B.¶
Here we will demonstrate the usage of Prometheus-2 as evaluator for the following evaluators available with LlamaIndex:
  1. Pairwise Evaluator - Assesses whether the LLM would favor one response over another from two different query engines.
  2. Faithfulness Evaluator - Determines if the answer remains faithful to the retrieved contexts, indicating the absence of hallucination.
  3. Correctness Evaluator - Determines whether the generated answer matches the reference answer provided for the query, which requires labels.
  4. Relevancy Evaluator - Evaluates the relevance of retrieved contexts and the response to a query.


  * If you're unfamiliar with the above evaluators, please refer to our Evaluation Guide for more information.
  * The prompts for the demonstration are inspired/ taken from the promethues-eval repository.


## Installation¶
In [ ]:
Copied!
```
!pip install llama-index
!pip install llama-index-llms-huggingface-api

```

!pip install llama-index !pip install llama-index-llms-huggingface-api
### Setup API Keys¶
In [ ]:
Copied!
```
import os

os.environ["OPENAI_API_KEY"] = "sk-"  # OPENAI API KEY

```

import os os.environ["OPENAI_API_KEY"] = "sk-" # OPENAI API KEY
In [ ]:
Copied!
```
# attach to the same event-loop
import nest_asyncio

nest_asyncio.apply()

from typing import Tuple, Optional
from IPython.display import Markdown, display

```

# attach to the same event-loop import nest_asyncio nest_asyncio.apply() from typing import Tuple, Optional from IPython.display import Markdown, display
### Download Data¶
For the demonstration, we will utilize the PaulGrahamEssay dataset and define a sample query along with a reference answer.
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import download_llama_dataset

paul_graham_rag_dataset, paul_graham_documents = download_llama_dataset(
    "PaulGrahamEssayDataset", "./data/paul_graham"
)

```

from llama_index.core.llama_dataset import download_llama_dataset paul_graham_rag_dataset, paul_graham_documents = download_llama_dataset( "PaulGrahamEssayDataset", "./data/paul_graham" )
Get Query and Reference(Ground truth) answer for the demonstration.
In [ ]:
Copied!
```
query = paul_graham_rag_dataset[0].query
reference = paul_graham_rag_dataset[0].reference_answer

```

query = paul_graham_rag_dataset[0].query reference = paul_graham_rag_dataset[0].reference_answer
### Setup LLM and Embedding model.¶
You need to deploy the model on huggingface or can load it locally. Here we deployed it using HF Inference Endpoints.
We will use OpenAI Embedding model and LLM for building Index, prometheus LLM for evaluation.
In [ ]:
Copied!
```
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI

HF_TOKEN = "YOUR HF TOKEN"
HF_ENDPOINT_URL = "YOUR HF ENDPOINT URL"

prometheus_llm = HuggingFaceInferenceAPI(
    model_name=HF_ENDPOINT_URL,
    token=HF_TOKEN,
    temperature=0.0,
    do_sample=True,
    top_p=0.95,
    top_k=40,
    repetition_penalty=1.1,
    num_output=1024,
)

```

from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI HF_TOKEN = "YOUR HF TOKEN" HF_ENDPOINT_URL = "YOUR HF ENDPOINT URL" prometheus_llm = HuggingFaceInferenceAPI( model_name=HF_ENDPOINT_URL, token=HF_TOKEN, temperature=0.0, do_sample=True, top_p=0.95, top_k=40, repetition_penalty=1.1, num_output=1024, )
In [ ]:
Copied!
```
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI


Settings.llm = OpenAI()
Settings.embed_model = OpenAIEmbedding()
Settings.chunk_size = 512

```

from llama_index.core import Settings from llama_index.embeddings.openai import OpenAIEmbedding from llama_index.llms.openai import OpenAI Settings.llm = OpenAI() Settings.embed_model = OpenAIEmbedding() Settings.chunk_size = 512
### Pairwise Evaluation¶
#### Build two QueryEngines for pairwise evaluation.¶
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import LabelledRagDataset
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex


dataset_path = "./data/paul_graham"
rag_dataset = LabelledRagDataset.from_json(f"{dataset_path}/rag_dataset.json")
documents = SimpleDirectoryReader(
    input_dir=f"{dataset_path}/source_files"
).load_data()

index = VectorStoreIndex.from_documents(documents=documents)

query_engine1 = index.as_query_engine(similarity_top_k=1)

query_engine2 = index.as_query_engine(similarity_top_k=2)

```

from llama_index.core.llama_dataset import LabelledRagDataset from llama_index.core import SimpleDirectoryReader, VectorStoreIndex dataset_path = "./data/paul_graham" rag_dataset = LabelledRagDataset.from_json(f"{dataset_path}/rag_dataset.json") documents = SimpleDirectoryReader( input_dir=f"{dataset_path}/source_files" ).load_data() index = VectorStoreIndex.from_documents(documents=documents) query_engine1 = index.as_query_engine(similarity_top_k=1) query_engine2 = index.as_query_engine(similarity_top_k=2)
In [ ]:
Copied!
```
response1 = str(query_engine1.query(query))
response2 = str(query_engine2.query(query))

```

response1 = str(query_engine1.query(query)) response2 = str(query_engine2.query(query))
In [ ]:
Copied!
```
response1

```

response1
Out[ ]:
```
'The author mentions using the IBM 1401 computer for programming in his early experiences. The language he used was an early version of Fortran. One of the challenges he faced was the limited input options for programs, as the only form of input was data stored on punched cards, which he did not have access to. This limitation made it difficult for him to create programs that required specific input data.'
```

In [ ]:
Copied!
```
response2

```

response2
Out[ ]:
```
'The author mentions using the IBM 1401 computer for programming in his early experiences. The language he used was an early version of Fortran. One of the challenges he faced was the limited input options for programs, as the only form of input was data stored on punched cards, which he did not have access to. This limitation made it difficult for him to create programs that required specific input data, leading to a lack of meaningful programming experiences on the IBM 1401.'
```

In [ ]:
Copied!
```
ABS_SYSTEM_PROMPT = "You are a fair judge assistant tasked with providing clear, objective feedback based on specific criteria, ensuring each assessment reflects the absolute standards set for performance."
REL_SYSTEM_PROMPT = "You are a fair judge assistant assigned to deliver insightful feedback that compares individual performances, highlighting how each stands relative to others within the same cohort."

```

ABS_SYSTEM_PROMPT = "You are a fair judge assistant tasked with providing clear, objective feedback based on specific criteria, ensuring each assessment reflects the absolute standards set for performance." REL_SYSTEM_PROMPT = "You are a fair judge assistant assigned to deliver insightful feedback that compares individual performances, highlighting how each stands relative to others within the same cohort."
In [ ]:
Copied!
```
prometheus_pairwise_eval_prompt_template = """###Task Description:
An instruction (might include an Input inside it), a response to evaluate, and a score rubric representing a evaluation criteria are given.
1. Write a detailed feedback that assess the quality of two responses strictly based on the given score rubric, not evaluating in general.
2. After writing a feedback, choose a better response between Response A and Response B. You should refer to the score rubric.
3. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (A or B)"
4. Please do not generate any other opening, closing, and explanations.

###Instruction:
Your task is to compare response A and Response B and give Feedback and score [RESULT] based on Rubric for the following query.
{query}

###Response A:
{answer_1}

###Response B:
{answer_2}

###Score Rubric:
A: If Response A is better than Response B.
B: If Response B is better than Response A.

###Feedback: """

```

prometheus_pairwise_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a response to evaluate, and a score rubric representing a evaluation criteria are given. 1. Write a detailed feedback that assess the quality of two responses strictly based on the given score rubric, not evaluating in general. 2. After writing a feedback, choose a better response between Response A and Response B. You should refer to the score rubric. 3. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (A or B)" 4. Please do not generate any other opening, closing, and explanations. ###Instruction: Your task is to compare response A and Response B and give Feedback and score [RESULT] based on Rubric for the following query. {query} ###Response A: {answer_1} ###Response B: {answer_2} ###Score Rubric: A: If Response A is better than Response B. B: If Response B is better than Response A. ###Feedback: """
In [ ]:
Copied!
```
def parser_function(
    outputs: str,
) -> Tuple[Optional[bool], Optional[float], Optional[str]]:
    parts = outputs.split("[RESULT]")
    if len(parts) == 2:
        feedback, result = parts[0].strip(), parts[1].strip()
        if result == "A":
            return True, 0.0, feedback
        elif result == "B":
            return True, 1.0, feedback
    return None, None, None

```

def parser_function( outputs: str, ) -> Tuple[Optional[bool], Optional[float], Optional[str]]: parts = outputs.split("[RESULT]") if len(parts) == 2: feedback, result = parts[0].strip(), parts[1].strip() if result == "A": return True, 0.0, feedback elif result == "B": return True, 1.0, feedback return None, None, None
In [ ]:
Copied!
```
from llama_index.core.evaluation import PairwiseComparisonEvaluator

prometheus_pairwise_evaluator = PairwiseComparisonEvaluator(
    llm=prometheus_llm,
    parser_function=parser_function,
    enforce_consensus=False,
    eval_template=REL_SYSTEM_PROMPT
    + "\n\n"
    + prometheus_pairwise_eval_prompt_template,
)

```

from llama_index.core.evaluation import PairwiseComparisonEvaluator prometheus_pairwise_evaluator = PairwiseComparisonEvaluator( llm=prometheus_llm, parser_function=parser_function, enforce_consensus=False, eval_template=REL_SYSTEM_PROMPT + "\n\n" + prometheus_pairwise_eval_prompt_template, )
In [ ]:
Copied!
```
pairwise_result = await prometheus_pairwise_evaluator.aevaluate(
    query,
    response=response1,
    second_response=response2,
)

```

pairwise_result = await prometheus_pairwise_evaluator.aevaluate( query, response=response1, second_response=response2, )
In [ ]:
Copied!
```
pairwise_result

```

pairwise_result
Out[ ]:
```
EvaluationResult(query='In the essay, the author mentions his early experiences with programming. Describe the first computer he used for programming, the language he used, and the challenges he faced.', contexts=None, response="\nBoth responses accurately describe the first computer the author used for programming, the language he used, and the challenges he faced. However, Response B provides a more comprehensive understanding of the challenges faced by the author. It not only mentions the limited input options but also connects this limitation to the author's lack of meaningful programming experiences on the IBM 1401. This additional context in Response B enhances the reader's understanding of the author's experiences and the impact of the challenges he faced. Therefore, based on the score rubric, Response B is better than Response A as it offers a more detailed and insightful analysis of the author's early programming experiences. \n[RESULT] B", passing=True, feedback="\nBoth responses accurately describe the first computer the author used for programming, the language he used, and the challenges he faced. However, Response B provides a more comprehensive understanding of the challenges faced by the author. It not only mentions the limited input options but also connects this limitation to the author's lack of meaningful programming experiences on the IBM 1401. This additional context in Response B enhances the reader's understanding of the author's experiences and the impact of the challenges he faced. Therefore, based on the score rubric, Response B is better than Response A as it offers a more detailed and insightful analysis of the author's early programming experiences. \n[RESULT] B", score=1.0, pairwise_source='original', invalid_result=False, invalid_reason=None)
```

In [ ]:
Copied!
```
pairwise_result.score

```

pairwise_result.score
Out[ ]:
```
1.0
```

In [ ]:
Copied!
```
display(Markdown(f"<b>{pairwise_result.feedback}</b>"))

```

display(Markdown(f"**{pairwise_result.feedback}** "))
**Both responses accurately describe the first computer the author used for programming, the language he used, and the challenges he faced. However, Response B provides a more comprehensive understanding of the challenges faced by the author. It not only mentions the limited input options but also connects this limitation to the author's lack of meaningful programming experiences on the IBM 1401. This additional context in Response B enhances the reader's understanding of the author's experiences and the impact of the challenges he faced. Therefore, based on the score rubric, Response B is better than Response A as it offers a more detailed and insightful analysis of the author's early programming experiences. [RESULT] B**
#### Observation:¶
According to the feedback, the second response is preferred over the first response, with a score of 1.0 as per our parser function.
### Correctness Evaluation¶
In [ ]:
Copied!
```
prometheus_correctness_eval_prompt_template = """###Task Description:
An instruction (might include an Input inside it), a query, a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given.
1. Write a detailed feedback that assesses the quality of the response strictly based on the given score rubric, not evaluating in general.
2. After writing a feedback, write a score that is either 1 or 2 or 3 or 4 or 5. You should refer to the score rubric.
3. The output format should only look as follows: "Feedback: (write a feedback for criteria) [RESULT] (an integer number between 1 and 5)"
4. Please do not generate any other opening, closing, and explanations.
5. Only evaluate on common things between generated answer and reference answer. Don't evaluate on things which are present in reference answer but not in generated answer.

###Instruction:
Your task is to evaluate the generated answer and reference answer for the following query:
{query}

###Generate answer to evaluate:
{generated_answer}

###Reference Answer (Score 5):
{reference_answer}

###Score Rubrics:
Score 1: If the generated answer is not relevant to the user query and reference answer.
Score 2: If the generated answer is according to reference answer but not relevant to user query.
Score 3: If the generated answer is relevant to the user query and reference answer but contains mistakes.
Score 4: If the generated answer is relevant to the user query and has the exact same metrics as the reference answer, but it is not as concise.
Score 5: If the generated answer is relevant to the user query and fully correct according to the reference answer.

###Feedback:"""

```

prometheus_correctness_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query, a response to evaluate, a reference answer that gets a score of 5, and a score rubric representing a evaluation criteria are given. 1. Write a detailed feedback that assesses the quality of the response strictly based on the given score rubric, not evaluating in general. 2. After writing a feedback, write a score that is either 1 or 2 or 3 or 4 or 5. You should refer to the score rubric. 3. The output format should only look as follows: "Feedback: (write a feedback for criteria) [RESULT] (an integer number between 1 and 5)" 4. Please do not generate any other opening, closing, and explanations. 5. Only evaluate on common things between generated answer and reference answer. Don't evaluate on things which are present in reference answer but not in generated answer. ###Instruction: Your task is to evaluate the generated answer and reference answer for the following query: {query} ###Generate answer to evaluate: {generated_answer} ###Reference Answer (Score 5): {reference_answer} ###Score Rubrics: Score 1: If the generated answer is not relevant to the user query and reference answer. Score 2: If the generated answer is according to reference answer but not relevant to user query. Score 3: If the generated answer is relevant to the user query and reference answer but contains mistakes. Score 4: If the generated answer is relevant to the user query and has the exact same metrics as the reference answer, but it is not as concise. Score 5: If the generated answer is relevant to the user query and fully correct according to the reference answer. ###Feedback:"""
In [ ]:
Copied!
```
from typing import Tuple
import re


def parser_function(output_str: str) -> Tuple[float, str]:
    # Print result to backtrack
    display(Markdown(f"<b>{output_str}</b>"))

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

from typing import Tuple import re def parser_function(output_str: str) -> Tuple[float, str]: # Print result to backtrack display(Markdown(f"**{output_str}** ")) # Pattern to match the feedback and response # This pattern looks for any text ending with '[RESULT]' followed by a number pattern = r"(.+?) \\[RESULT\\] (\d)" # Using regex to find all matches matches = re.findall(pattern, output_str) # Check if any match is found if matches: # Assuming there's only one match in the text, extract feedback and response feedback, score = matches[0] score = float(score.strip()) if score is not None else score return score, feedback.strip() else: return None, None
In [ ]:
Copied!
```
from llama_index.core.evaluation import (
    CorrectnessEvaluator,
    FaithfulnessEvaluator,
    RelevancyEvaluator,
)
from llama_index.core.callbacks import CallbackManager, TokenCountingHandler


# CorrectnessEvaluator with Prometheus model
prometheus_correctness_evaluator = CorrectnessEvaluator(
    llm=prometheus_llm,
    parser_function=parser_function,
    eval_template=ABS_SYSTEM_PROMPT
    + "\n\n"
    + prometheus_correctness_eval_prompt_template,
)

```

from llama_index.core.evaluation import ( CorrectnessEvaluator, FaithfulnessEvaluator, RelevancyEvaluator, ) from llama_index.core.callbacks import CallbackManager, TokenCountingHandler # CorrectnessEvaluator with Prometheus model prometheus_correctness_evaluator = CorrectnessEvaluator( llm=prometheus_llm, parser_function=parser_function, eval_template=ABS_SYSTEM_PROMPT + "\n\n" + prometheus_correctness_eval_prompt_template, )
In [ ]:
Copied!
```
correctness_result = prometheus_correctness_evaluator.evaluate(
    query=query,
    response=response1,
    reference=reference,
)

```

correctness_result = prometheus_correctness_evaluator.evaluate( query=query, response=response1, reference=reference, )
**The generated answer is relevant to the user query and the reference answer, as it correctly identifies the IBM 1401 as the first computer used for programming, the early version of Fortran as the programming language, and the challenge of limited input options. However, the response lacks the depth and detail found in the reference answer. For instance, it does not mention the specific age of the author when he started using the IBM 1401, nor does it provide examples of the types of programs he could not create due to the lack of input data. These omissions make the response less comprehensive than the reference answer. Therefore, while the generated answer is accurate and relevant, it is not as thorough as the reference answer. So the score is 4. [RESULT] 4**
In [ ]:
Copied!
```
display(Markdown(f"<b>{correctness_result.score}</b>"))

```

display(Markdown(f"**{correctness_result.score}** "))
**4.0**
In [ ]:
Copied!
```
display(Markdown(f"<b>{correctness_result.passing}</b>"))

```

display(Markdown(f"**{correctness_result.passing}** "))
**True**
In [ ]:
Copied!
```
display(Markdown(f"<b>{correctness_result.feedback}</b>"))

```

display(Markdown(f"**{correctness_result.feedback}** "))
**The generated answer is relevant to the user query and the reference answer, as it correctly identifies the IBM 1401 as the first computer used for programming, the early version of Fortran as the programming language, and the challenge of limited input options. However, the response lacks the depth and detail found in the reference answer. For instance, it does not mention the specific age of the author when he started using the IBM 1401, nor does it provide examples of the types of programs he could not create due to the lack of input data. These omissions make the response less comprehensive than the reference answer. Therefore, while the generated answer is accurate and relevant, it is not as thorough as the reference answer. So the score is 4.**
#### Observation:¶
Based on the feedback, the generated answer is relevant to the user query and matches the metrics of the reference answer precisely. However, it is not as concise, resulting in a score of 4.0. Despite this, the answer passes as True based on the threshold.
### Faithfulness Evaluator¶
In [ ]:
Copied!
```
prometheus_faithfulness_eval_prompt_template = """###Task Description:
An instruction (might include an Input inside it), an information, a context, and a score rubric representing evaluation criteria are given.
1. You are provided with evaluation task with the help of information, context information to give result based on score rubrics.
2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general.
3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric.
4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)”
5. Please do not generate any other opening, closing, and explanations.

###The instruction to evaluate: Your task is to evaluate if the given piece of information is supported by context.

###Information:
{query_str}

###Context:
{context_str}

###Score Rubrics:
Score YES: If the given piece of information is supported by context.
Score NO: If the given piece of information is not supported by context

###Feedback:"""

prometheus_faithfulness_refine_prompt_template = """###Task Description:
An instruction (might include an Input inside it), a information, a context information, an existing answer, and a score rubric representing a evaluation criteria are given.
1. You are provided with evaluation task with the help of information, context information and an existing answer.
2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general.
3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric.
4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)"
5. Please do not generate any other opening, closing, and explanations.

###The instruction to evaluate: If the information is present in the context and also provided with an existing answer.

###Existing answer:
{existing_answer}

###Information:
{query_str}

###Context:
{context_msg}

###Score Rubrics:
Score YES: If the existing answer is already YES or If the Information is present in the context.
Score NO: If the existing answer is NO and If the Information is not present in the context.

###Feedback: """

```

prometheus_faithfulness_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), an information, a context, and a score rubric representing evaluation criteria are given. 1. You are provided with evaluation task with the help of information, context information to give result based on score rubrics. 2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)” 5. Please do not generate any other opening, closing, and explanations. ###The instruction to evaluate: Your task is to evaluate if the given piece of information is supported by context. ###Information: {query_str} ###Context: {context_str} ###Score Rubrics: Score YES: If the given piece of information is supported by context. Score NO: If the given piece of information is not supported by context ###Feedback:""" prometheus_faithfulness_refine_prompt_template = """###Task Description: An instruction (might include an Input inside it), a information, a context information, an existing answer, and a score rubric representing a evaluation criteria are given. 1. You are provided with evaluation task with the help of information, context information and an existing answer. 2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)" 5. Please do not generate any other opening, closing, and explanations. ###The instruction to evaluate: If the information is present in the context and also provided with an existing answer. ###Existing answer: {existing_answer} ###Information: {query_str} ###Context: {context_msg} ###Score Rubrics: Score YES: If the existing answer is already YES or If the Information is present in the context. Score NO: If the existing answer is NO and If the Information is not present in the context. ###Feedback: """
In [ ]:
Copied!
```
# FaithfulnessEvaluator with Prometheus model
prometheus_faithfulness_evaluator = FaithfulnessEvaluator(
    llm=prometheus_llm,
    eval_template=ABS_SYSTEM_PROMPT
    + "\n\n"
    + prometheus_faithfulness_eval_prompt_template,
    refine_template=ABS_SYSTEM_PROMPT
    + "\n\n"
    + prometheus_faithfulness_refine_prompt_template,
)

```

# FaithfulnessEvaluator with Prometheus model prometheus_faithfulness_evaluator = FaithfulnessEvaluator( llm=prometheus_llm, eval_template=ABS_SYSTEM_PROMPT + "\n\n" + prometheus_faithfulness_eval_prompt_template, refine_template=ABS_SYSTEM_PROMPT + "\n\n" + prometheus_faithfulness_refine_prompt_template, )
In [ ]:
Copied!
```
response_vector = query_engine1.query(query)

```

response_vector = query_engine1.query(query)
In [ ]:
Copied!
```
faithfulness_result = prometheus_faithfulness_evaluator.evaluate_response(
    response=response_vector
)

```

faithfulness_result = prometheus_faithfulness_evaluator.evaluate_response( response=response_vector )
In [ ]:
Copied!
```
faithfulness_result.score

```

faithfulness_result.score
Out[ ]:
```
1.0
```

In [ ]:
Copied!
```
faithfulness_result.passing

```

faithfulness_result.passing
Out[ ]:
```
True
```

#### Observation:¶
The score and passing denotes there is no hallucination observed.
### Relevancy Evaluator¶
In [ ]:
Copied!
```
prometheus_relevancy_eval_prompt_template = """###Task Description:
An instruction (might include an Input inside it), a query with response, context, and a score rubric representing evaluation criteria are given.
1. You are provided with evaluation task with the help of a query with response and context.
2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general.
3. After writing a feedback, write a score that is A or B. You should refer to the score rubric.
4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)”
5. Please do not generate any other opening, closing, and explanations.

###The instruction to evaluate: Your task is to evaluate if the response for the query is in line with the context information provided.

###Query and Response:
{query_str}

###Context:
{context_str}

###Score Rubrics:
Score YES: If the response for the query is in line with the context information provided.
Score NO: If the response for the query is not in line with the context information provided.

###Feedback: """

prometheus_relevancy_refine_prompt_template = """###Task Description:
An instruction (might include an Input inside it), a query with response, context, an existing answer, and a score rubric representing a evaluation criteria are given.
1. You are provided with evaluation task with the help of a query with response and context and an existing answer.
2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general.
3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric.
4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)"
5. Please do not generate any other opening, closing, and explanations.

###The instruction to evaluate: Your task is to evaluate if the response for the query is in line with the context information provided.

###Query and Response:
{query_str}

###Context:
{context_str}

###Score Rubrics:
Score YES: If the existing answer is already YES or If the response for the query is in line with the context information provided.
Score NO: If the existing answer is NO and If the response for the query is in line with the context information provided.

###Feedback: """

```

prometheus_relevancy_eval_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query with response, context, and a score rubric representing evaluation criteria are given. 1. You are provided with evaluation task with the help of a query with response and context. 2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 3. After writing a feedback, write a score that is A or B. You should refer to the score rubric. 4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)” 5. Please do not generate any other opening, closing, and explanations. ###The instruction to evaluate: Your task is to evaluate if the response for the query is in line with the context information provided. ###Query and Response: {query_str} ###Context: {context_str} ###Score Rubrics: Score YES: If the response for the query is in line with the context information provided. Score NO: If the response for the query is not in line with the context information provided. ###Feedback: """ prometheus_relevancy_refine_prompt_template = """###Task Description: An instruction (might include an Input inside it), a query with response, context, an existing answer, and a score rubric representing a evaluation criteria are given. 1. You are provided with evaluation task with the help of a query with response and context and an existing answer. 2. Write a detailed feedback based on evaluation task and the given score rubric, not evaluating in general. 3. After writing a feedback, write a score that is YES or NO. You should refer to the score rubric. 4. The output format should look as follows: "Feedback: (write a feedback for criteria) [RESULT] (YES or NO)" 5. Please do not generate any other opening, closing, and explanations. ###The instruction to evaluate: Your task is to evaluate if the response for the query is in line with the context information provided. ###Query and Response: {query_str} ###Context: {context_str} ###Score Rubrics: Score YES: If the existing answer is already YES or If the response for the query is in line with the context information provided. Score NO: If the existing answer is NO and If the response for the query is in line with the context information provided. ###Feedback: """
In [ ]:
Copied!
```
# RelevancyEvaluator with Prometheus model
prometheus_relevancy_evaluator = RelevancyEvaluator(
    llm=prometheus_llm,
    eval_template=ABS_SYSTEM_PROMPT
    + "\n\n"
    + prometheus_relevancy_eval_prompt_template,
    refine_template=ABS_SYSTEM_PROMPT
    + "\n\n"
    + prometheus_relevancy_refine_prompt_template,
)

```

# RelevancyEvaluator with Prometheus model prometheus_relevancy_evaluator = RelevancyEvaluator( llm=prometheus_llm, eval_template=ABS_SYSTEM_PROMPT + "\n\n" + prometheus_relevancy_eval_prompt_template, refine_template=ABS_SYSTEM_PROMPT + "\n\n" + prometheus_relevancy_refine_prompt_template, )
In [ ]:
Copied!
```
relevancy_result = prometheus_relevancy_evaluator.evaluate_response(
    query=query, response=response_vector
)

```

relevancy_result = prometheus_relevancy_evaluator.evaluate_response( query=query, response=response_vector )
In [ ]:
Copied!
```
relevancy_result.score

```

relevancy_result.score
Out[ ]:
```
1.0
```

In [ ]:
Copied!
```
relevancy_result.passing

```

relevancy_result.passing
Out[ ]:
```
True
```

In [ ]:
Copied!
```
display(Markdown(f"<b>{relevancy_result.feedback}</b>"))

```

display(Markdown(f"**{relevancy_result.feedback}** "))
**The response provided is in line with the context information given. It accurately describes the first computer used for programming, the language used, and the challenges faced by the author. The IBM 1401 computer is correctly identified as the first computer used for programming, and the early version of Fortran is mentioned as the language used. The challenges faced by the author, such as the limited input options and the difficulty of creating meaningful programs, are also accurately described. The response is concise and directly addresses the query, providing a clear and relevant answer. Therefore, based on the score rubric, the response is in line with the context information provided. [RESULT] YES**
#### Observation:¶
The feedback indicates that the response to the query aligns well with the provided context information, resulting in a score of 1.0 and passing status of True.
### Conclusion:¶
Exploring Prometheus-2 for OSS evaluation is interesting.
The feedback is in the expected format, making parsing and decision-making easier.
It's valuable to compare with GPT-4 for evaluation purposes and consider using Prometheus-2 in evaluations.
You can refer to our guide on comparing GPT-4 as an evaluator with the OSS evaluation model for experimentation.
