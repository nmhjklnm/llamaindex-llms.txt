![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Answer Relevancy and Context Relevancy Evaluations¶
In this notebook, we demonstrate how to utilize the `AnswerRelevancyEvaluator` and `ContextRelevancyEvaluator` classes to get a measure on the relevancy of a generated answer and retrieved contexts, respectively, to a given user query. Both of these evaluators return a `score` that is between 0 and 1 as well as a generated `feedback` explaining the score. Note that, higher score means higher relevancy. In particular, we prompt the judge LLM to take a step-by-step approach in providing a relevancy score, asking it to answer the following two questions of a generated answer to a query for answer relevancy (for context relevancy these are slightly adjusted):
  1. Does the provided response match the subject matter of the user's query?
  2. Does the provided response attempt to address the focus or perspective on the subject matter taken on by the user's query?


Each question is worth 1 point and so a perfect evaluation would yield a score of 2/2.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
import nest_asyncio
from tqdm.asyncio import tqdm_asyncio

nest_asyncio.apply()

```

import nest_asyncio from tqdm.asyncio import tqdm_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
def displayify_df(df):
    """For pretty displaying DataFrame in a notebook."""
    display_df = df.style.set_properties(
        **{
            "inline-size": "300px",
            "overflow-wrap": "break-word",
        }
    )
    display(display_df)

```

def displayify_df(df): """For pretty displaying DataFrame in a notebook.""" display_df = df.style.set_properties( **{ "inline-size": "300px", "overflow-wrap": "break-word", } ) display(display_df)
### Download the dataset (`LabelledRagDataset`)¶
For this demonstration, we will use a llama-dataset provided through our llama-hub.
In [ ]:
Copied!
```
from llama_index.core.llama_dataset import download_llama_dataset
from llama_index.core.llama_pack import download_llama_pack
from llama_index.core import VectorStoreIndex

# download and install dependencies for benchmark dataset
rag_dataset, documents = download_llama_dataset(
    "EvaluatingLlmSurveyPaperDataset", "./data"
)

```

from llama_index.core.llama_dataset import download_llama_dataset from llama_index.core.llama_pack import download_llama_pack from llama_index.core import VectorStoreIndex # download and install dependencies for benchmark dataset rag_dataset, documents = download_llama_dataset( "EvaluatingLlmSurveyPaperDataset", "./data" )
In [ ]:
Copied!
```
rag_dataset.to_pandas()[:5]

```

rag_dataset.to_pandas()[:5]
Out[ ]:
| query | reference_contexts | reference_answer | reference_answer_by | query_by  
---|---|---|---|---|---  
0 | What are the potential risks associated with l... | [Evaluating Large Language Models: A\nComprehe... | According to the context information, the pote... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
1 | How does the survey categorize the evaluation ... | [Evaluating Large Language Models: A\nComprehe... | The survey categorizes the evaluation of LLMs ... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
2 | What are the different types of reasoning disc... | [Contents\n1 Introduction 4\n2 Taxonomy and Ro... | The different types of reasoning discussed in ... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
3 | How is toxicity evaluated in language models a... | [Contents\n1 Introduction 4\n2 Taxonomy and Ro... | Toxicity is evaluated in language models accor... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
4 | In the context of specialized LLMs evaluation,... | [5.1.3 Alignment Robustness . . . . . . . . . ... | In the context of specialized LLMs evaluation,... | ai (gpt-3.5-turbo) | ai (gpt-3.5-turbo)  
Next, we build a RAG over the same source documents used to created the `rag_dataset`.
In [ ]:
Copied!
```
index = VectorStoreIndex.from_documents(documents=documents)
query_engine = index.as_query_engine()

```

index = VectorStoreIndex.from_documents(documents=documents) query_engine = index.as_query_engine()
With our RAG (i.e `query_engine`) defined, we can make predictions (i.e., generate responses to the query) with it over the `rag_dataset`.
In [ ]:
Copied!
```
prediction_dataset = await rag_dataset.amake_predictions_with(
    predictor=query_engine, batch_size=100, show_progress=True
)

```

prediction_dataset = await rag_dataset.amake_predictions_with( predictor=query_engine, batch_size=100, show_progress=True )
```
Batch processing of predictions: 100%|████████████████████| 100/100 [00:08<00:00, 12.12it/s]
Batch processing of predictions: 100%|████████████████████| 100/100 [00:08<00:00, 12.37it/s]
Batch processing of predictions: 100%|██████████████████████| 76/76 [00:06<00:00, 10.93it/s]

```

### Evaluating Answer and Context Relevancy Separately¶
We first need to define our evaluators (i.e. `AnswerRelevancyEvaluator` & `ContextRelevancyEvaluator`):
In [ ]:
Copied!
```
# instantiate the gpt-4 judges
from llama_index.llms.openai import OpenAI
from llama_index.core.evaluation import (
    AnswerRelevancyEvaluator,
    ContextRelevancyEvaluator,
)

judges = {}

judges["answer_relevancy"] = AnswerRelevancyEvaluator(
    llm=OpenAI(temperature=0, model="gpt-3.5-turbo"),
)

judges["context_relevancy"] = ContextRelevancyEvaluator(
    llm=OpenAI(temperature=0, model="gpt-4"),
)

```

# instantiate the gpt-4 judges from llama_index.llms.openai import OpenAI from llama_index.core.evaluation import ( AnswerRelevancyEvaluator, ContextRelevancyEvaluator, ) judges = {} judges["answer_relevancy"] = AnswerRelevancyEvaluator( llm=OpenAI(temperature=0, model="gpt-3.5-turbo"), ) judges["context_relevancy"] = ContextRelevancyEvaluator( llm=OpenAI(temperature=0, model="gpt-4"), )
Now, we can use our evaluator to make evaluations by looping through all of the <example, prediction> pairs.
In [ ]:
Copied!
```
eval_tasks = []
for example, prediction in zip(
    rag_dataset.examples, prediction_dataset.predictions
):
    eval_tasks.append(
        judges["answer_relevancy"].aevaluate(
            query=example.query,
            response=prediction.response,
            sleep_time_in_seconds=1.0,
        )
    )
    eval_tasks.append(
        judges["context_relevancy"].aevaluate(
            query=example.query,
            contexts=prediction.contexts,
            sleep_time_in_seconds=1.0,
        )
    )

```

eval_tasks = [] for example, prediction in zip( rag_dataset.examples, prediction_dataset.predictions ): eval_tasks.append( judges["answer_relevancy"].aevaluate( query=example.query, response=prediction.response, sleep_time_in_seconds=1.0, ) ) eval_tasks.append( judges["context_relevancy"].aevaluate( query=example.query, contexts=prediction.contexts, sleep_time_in_seconds=1.0, ) )
In [ ]:
Copied!
```
eval_results1 = await tqdm_asyncio.gather(*eval_tasks[:250])

```

eval_results1 = await tqdm_asyncio.gather(*eval_tasks[:250])
```
100%|█████████████████████████████████████████████████████| 250/250 [00:28<00:00,  8.85it/s]

```

In [ ]:
Copied!
```
eval_results2 = await tqdm_asyncio.gather(*eval_tasks[250:])

```

eval_results2 = await tqdm_asyncio.gather(*eval_tasks[250:])
```
100%|█████████████████████████████████████████████████████| 302/302 [00:31<00:00,  9.62it/s]

```

In [ ]:
Copied!
```
eval_results = eval_results1 + eval_results2

```

eval_results = eval_results1 + eval_results2
In [ ]:
Copied!
```
evals = {
    "answer_relevancy": eval_results[::2],
    "context_relevancy": eval_results[1::2],
}

```

evals = { "answer_relevancy": eval_results[::2], "context_relevancy": eval_results[1::2], }
### Taking a look at the evaluation results¶
Here we use a utility function to convert the list of `EvaluationResult` objects into something more notebook friendly. This utility will provide two DataFrames, one deep one containing all of the evaluation results, and another one which aggregates via taking the mean of all the scores, per evaluation method.
In [ ]:
Copied!
```
from llama_index.core.evaluation.notebook_utils import get_eval_results_df
import pandas as pd

deep_dfs = {}
mean_dfs = {}
for metric in evals.keys():
    deep_df, mean_df = get_eval_results_df(
        names=["baseline"] * len(evals[metric]),
        results_arr=evals[metric],
        metric=metric,
    )
    deep_dfs[metric] = deep_df
    mean_dfs[metric] = mean_df

```

from llama_index.core.evaluation.notebook_utils import get_eval_results_df import pandas as pd deep_dfs = {} mean_dfs = {} for metric in evals.keys(): deep_df, mean_df = get_eval_results_df( names=["baseline"] * len(evals[metric]), results_arr=evals[metric], metric=metric, ) deep_dfs[metric] = deep_df mean_dfs[metric] = mean_df
In [ ]:
Copied!
```
mean_scores_df = pd.concat(
    [mdf.reset_index() for _, mdf in mean_dfs.items()],
    axis=0,
    ignore_index=True,
)
mean_scores_df = mean_scores_df.set_index("index")
mean_scores_df.index = mean_scores_df.index.set_names(["metrics"])
mean_scores_df

```

mean_scores_df = pd.concat( [mdf.reset_index() for _, mdf in mean_dfs.items()], axis=0, ignore_index=True, ) mean_scores_df = mean_scores_df.set_index("index") mean_scores_df.index = mean_scores_df.index.set_names(["metrics"]) mean_scores_df
Out[ ]:
rag | baseline  
---|---  
metrics |   
mean_answer_relevancy_score | 0.914855  
mean_context_relevancy_score | 0.572273  
The above utility also provides the mean score across all of the evaluations in `mean_df`.
We can get a look at the raw distribution of the scores by invoking `value_counts()` on the `deep_df`.
In [ ]:
Copied!
```
deep_dfs["answer_relevancy"]["scores"].value_counts()

```

deep_dfs["answer_relevancy"]["scores"].value_counts()
Out[ ]:
```
scores
1.0    250
0.0     21
0.5      5
Name: count, dtype: int64
```

In [ ]:
Copied!
```
deep_dfs["context_relevancy"]["scores"].value_counts()

```

deep_dfs["context_relevancy"]["scores"].value_counts()
Out[ ]:
```
scores
1.000    89
0.000    70
0.750    49
0.250    23
0.625    14
0.500    11
0.375    10
0.875     9
Name: count, dtype: int64
```

It looks like for the most part, the default RAG does fairly well in terms of generating answers that are relevant to the query. Getting a closer look is made possible by viewing the records of any of the `deep_df`'s.
In [ ]:
Copied!
```
displayify_df(deep_dfs["context_relevancy"].head(2))

```

displayify_df(deep_dfs["context_relevancy"].head(2))
| rag | query | answer | contexts | scores | feedbacks  
---|---|---|---|---|---|---  
0 | baseline | What are the potential risks associated with large language models (LLMs) according to the context information? | None | ['Evaluating Large Language Models: A\nComprehensive Survey\nZishan Guo∗, Renren Jin∗, Chuang Liu∗, Yufei Huang, Dan Shi, Supryadi\nLinhao Yu, Yan Liu, Jiaxuan Li, Bojian Xiong, Deyi Xiong†\nTianjin University\n{guozishan, rrjin, liuc_09, yuki_731, shidan, supryadi}@tju.edu.cn\n{linhaoyu, yan_liu, jiaxuanlee, xbj1355, dyxiong}@tju.edu.cn\nAbstract\nLarge language models (LLMs) have demonstrated remarkable capabilities\nacross a broad spectrum of tasks. They have attracted significant attention\nand been deployed in numerous downstream applications. Nevertheless, akin\nto a double-edged sword, LLMs also present potential risks. They could\nsuffer from private data leaks or yield inappropriate, harmful, or misleading\ncontent. Additionally, the rapid progress of LLMs raises concerns about the\npotential emergence of superintelligent systems without adequate safeguards.\nTo effectively capitalize on LLM capacities as well as ensure their safe and\nbeneficial development, it is critical to conduct a rigorous and comprehensive\nevaluation of LLMs.\nThis survey endeavors to offer a panoramic perspective on the evaluation\nof LLMs. We categorize the evaluation of LLMs into three major groups:\nknowledgeandcapabilityevaluation, alignmentevaluationandsafetyevaluation.\nIn addition to the comprehensive review on the evaluation methodologies and\nbenchmarks on these three aspects, we collate a compendium of evaluations\npertaining to LLMs’ performance in specialized domains, and discuss the\nconstruction of comprehensive evaluation platforms that cover LLM evaluations\non capabilities, alignment, safety, and applicability.\nWe hope that this comprehensive overview will stimulate further research\ninterests in the evaluation of LLMs, with the ultimate goal of making evaluation\nserve as a cornerstone in guiding the responsible development of LLMs. We\nenvision that this will channel their evolution into a direction that maximizes\nsocietal benefit while minimizing potential risks. A curated list of related\npapers has been publicly available at a GitHub repository.1\n∗Equal contribution\n†Corresponding author.\n1https://github.com/tjunlp-lab/Awesome-LLMs-Evaluation-Papers\n1arXiv:2310.19736v3 [cs.CL] 25 Nov 2023', 'criteria. Multilingual Holistic Bias (Costa-jussà et al., 2023) extends the HolisticBias dataset\nto 50 languages, achieving the largest scale of English template-based text expansion.\nWhether using automatic or manual evaluations, both approaches inevitably carry human\nsubjectivity and cannot establish a comprehensive and fair evaluation standard. Unqover\n(Li et al., 2020) is the first to transform the task of evaluating biases generated by models\ninto a multiple-choice question, covering gender, nationality, race, and religion categories.\nThey provide models with ambiguous and disambiguous contexts and ask them to choose\nbetween options with and without stereotypes, evaluating both PLMs and models fine-tuned\non multiple-choice question answering datasets. BBQ (Parrish et al., 2022) adopts this\napproach but extends the types of biases to nine categories. All sentence templates are\nmanually created, and in addition to the two contrasting group answers, the model is also\nprovided with correct answers like “I don’t know” and “I’m not sure”, and a statistical bias\nscore metric is proposed to evaluate multiple question answering models. CBBQ (Huang\n& Xiong, 2023) extends BBQ to Chinese. Based on Chinese socio-cultural factors, CBBQ\nadds four categories: disease, educational qualification, household registration, and region.\nThey manually rewrite ambiguous text templates and use GPT-4 to generate disambiguous\ntemplates, greatly increasing the dataset’s diversity and extensibility. Additionally, they\nimprove the experimental setup for LLMs and evaluate existing Chinese open-source LLMs,\nfinding that current Chinese LLMs not only have higher bias scores but also exhibit behavioral\ninconsistencies, revealing a significant gap compared to GPT-3.5-Turbo.\nIn addition to these aforementioned evaluation methods, we could also use advanced LLMs for\nscoring bias, such as GPT-4, or employ models that perform best in training bias detection\ntasks to detect the level of bias in answers. Such models can be used not only in the evaluation\nphase but also for identifying biases in data for pre-training LLMs, facilitating debiasing in\ntraining data.\nAs the development of multilingual LLMs and domain-specific LLMs progresses, studies on\nthe fairness of these models become increasingly important. Zhao et al. (2020) create datasets\nto study gender bias in multilingual embeddings and cross-lingual tasks, revealing gender\nbias from both internal and external perspectives. Moreover, FairLex (Chalkidis et al., 2022)\nproposes a multilingual legal dataset as fairness benchmark, covering four judicial jurisdictions\n(European Commission, United States, Swiss Federation, and People’s Republic of China), five\nlanguages (English, German, French, Italian, and Chinese), and various sensitive attributes\n(gender, age, region, etc.). As LLMs have been applied and deployed in the finance and legal\nsectors, these studies deserve high attention.\n4.3 Toxicity\nLLMs are usually trained on a huge amount of online data which may contain toxic behavior\nand unsafe content. These include hate speech, offensive/abusive language, pornographic\ncontent, etc. It is hence very desirable to evaluate how well trained LLMs deal with toxicity.\nConsidering the proficiency of LLMs in understanding and generating sentences, we categorize\nthe evaluation of toxicity into two tasks: toxicity identification and classification evaluation,\nand the evaluation of toxicity in generated sentences.\n29'] | 1.000000 | 1. The retrieved context does match the subject matter of the user's query. It discusses the potential risks associated with large language models (LLMs), including private data leaks, inappropriate or harmful content, and the emergence of superintelligent systems without adequate safeguards. It also discusses the potential for bias in LLMs, and the risk of toxicity in the content generated by LLMs. Therefore, it is relevant to the user's query about the potential risks associated with LLMs. (2/2) 2. The retrieved context can be used to provide a full answer to the user's query. It provides a comprehensive overview of the potential risks associated with LLMs, including data privacy, inappropriate content, superintelligence, bias, and toxicity. It also discusses the importance of evaluating these risks and the methodologies for doing so. Therefore, it provides a complete answer to the user's query. (2/2) [RESULT] 4/4  
1 | baseline | How does the survey categorize the evaluation of LLMs and what are the three major groups mentioned? | None | ['Question \nAnsweringTool \nLearning\nReasoning\nKnowledge \nCompletionEthics \nand \nMorality Bias\nToxicity\nTruthfulnessRobustnessEvaluation\nRisk \nEvaluation\nBiology and \nMedicine\nEducationLegislationComputer \nScienceFinance\nBenchmarks for\nHolistic Evaluation\nBenchmarks \nforKnowledge and Reasoning\nBenchmarks \nforNLU and NLGKnowledge and Capability\nLarge Language \nModel EvaluationAlignment Evaluation\nSafety\nSpecialized LLMs\nEvaluation Organization\n…Figure 1: Our proposed taxonomy of major categories and sub-categories of LLM evaluation.\nOur survey expands the scope to synthesize findings from both capability and alignment\nevaluations of LLMs. By complementing these previous surveys through an integrated\nperspective and expanded scope, our work provides a comprehensive overview of the current\nstate of LLM evaluation research. The distinctions between our survey and these two related\nworks further highlight the novel contributions of our study to the literature.\n2 Taxonomy and Roadmap\nThe primary objective of this survey is to meticulously categorize the evaluation of LLMs,\nfurnishing readers with a well-structured taxonomy framework. Through this framework,\nreaders can gain a nuanced understanding of LLMs’ performance and the attendant challenges\nacross diverse and pivotal domains.\nNumerous studies posit that the bedrock of LLMs’ capabilities resides in knowledge and\nreasoning, serving as the underpinning for their exceptional performance across a myriad of\ntasks. Nonetheless, the effective application of these capabilities necessitates a meticulous\nexamination of alignment concerns to ensure that the model’s outputs remain consistent with\nuser expectations. Moreover, the vulnerability of LLMs to malicious exploits or inadvertent\nmisuse underscores the imperative nature of safety considerations. Once alignment and safety\nconcerns have been addressed, LLMs can be judiciously deployed within specialized domains,\ncatalyzing task automation and facilitating intelligent decision-making. Thus, our overarching\n6', 'This survey systematically elaborates on the core capabilities of LLMs, encompassing critical\naspects like knowledge and reasoning. Furthermore, we delve into alignment evaluation and\nsafety evaluation, including ethical concerns, biases, toxicity, and truthfulness, to ensure the\nsafe, trustworthy and ethical application of LLMs. Simultaneously, we explore the potential\napplications of LLMs across diverse domains, including biology, education, law, computer\nscience, and finance. Most importantly, we provide a range of popular benchmark evaluations\nto assist researchers, developers and practitioners in understanding and evaluating LLMs’\nperformance.\nWe anticipate that this survey would drive the development of LLMs evaluations, offering\nclear guidance to steer the controlled advancement of these models. This will enable LLMs\nto better serve the community and the world, ensuring their applications in various domains\nare safe, reliable, and beneficial. With eager anticipation, we embrace the future challenges\nof LLMs’ development and evaluation.\n58'] | 0.375000 | 1. The retrieved context does match the subject matter of the user's query. The user's query is about how a survey categorizes the evaluation of Large Language Models (LLMs) and the three major groups mentioned. The context provided discusses the categorization of LLMs evaluation in the survey, mentioning aspects like knowledge and reasoning, alignment evaluation, safety evaluation, and potential applications across diverse domains. 2. However, the context does not provide a full answer to the user's query. While it does discuss the categorization of LLMs evaluation, it does not clearly mention the three major groups. The context mentions several aspects of LLMs evaluation, but it is not clear which of these are considered the three major groups. [RESULT] 1.5  
And, of course you can apply any filters as you like. For example, if you want to look at the examples that yielded less than perfect results.
In [ ]:
Copied!
```
cond = deep_dfs["context_relevancy"]["scores"] < 1
displayify_df(deep_dfs["context_relevancy"][cond].head(5))

```

cond = deep_dfs["context_relevancy"]["scores"] < 1 displayify_df(deep_dfs["context_relevancy"][cond].head(5))
| rag | query | answer | contexts | scores | feedbacks  
---|---|---|---|---|---|---  
1 | baseline | How does the survey categorize the evaluation of LLMs and what are the three major groups mentioned? | None | ['Question \nAnsweringTool \nLearning\nReasoning\nKnowledge \nCompletionEthics \nand \nMorality Bias\nToxicity\nTruthfulnessRobustnessEvaluation\nRisk \nEvaluation\nBiology and \nMedicine\nEducationLegislationComputer \nScienceFinance\nBenchmarks for\nHolistic Evaluation\nBenchmarks \nforKnowledge and Reasoning\nBenchmarks \nforNLU and NLGKnowledge and Capability\nLarge Language \nModel EvaluationAlignment Evaluation\nSafety\nSpecialized LLMs\nEvaluation Organization\n…Figure 1: Our proposed taxonomy of major categories and sub-categories of LLM evaluation.\nOur survey expands the scope to synthesize findings from both capability and alignment\nevaluations of LLMs. By complementing these previous surveys through an integrated\nperspective and expanded scope, our work provides a comprehensive overview of the current\nstate of LLM evaluation research. The distinctions between our survey and these two related\nworks further highlight the novel contributions of our study to the literature.\n2 Taxonomy and Roadmap\nThe primary objective of this survey is to meticulously categorize the evaluation of LLMs,\nfurnishing readers with a well-structured taxonomy framework. Through this framework,\nreaders can gain a nuanced understanding of LLMs’ performance and the attendant challenges\nacross diverse and pivotal domains.\nNumerous studies posit that the bedrock of LLMs’ capabilities resides in knowledge and\nreasoning, serving as the underpinning for their exceptional performance across a myriad of\ntasks. Nonetheless, the effective application of these capabilities necessitates a meticulous\nexamination of alignment concerns to ensure that the model’s outputs remain consistent with\nuser expectations. Moreover, the vulnerability of LLMs to malicious exploits or inadvertent\nmisuse underscores the imperative nature of safety considerations. Once alignment and safety\nconcerns have been addressed, LLMs can be judiciously deployed within specialized domains,\ncatalyzing task automation and facilitating intelligent decision-making. Thus, our overarching\n6', 'This survey systematically elaborates on the core capabilities of LLMs, encompassing critical\naspects like knowledge and reasoning. Furthermore, we delve into alignment evaluation and\nsafety evaluation, including ethical concerns, biases, toxicity, and truthfulness, to ensure the\nsafe, trustworthy and ethical application of LLMs. Simultaneously, we explore the potential\napplications of LLMs across diverse domains, including biology, education, law, computer\nscience, and finance. Most importantly, we provide a range of popular benchmark evaluations\nto assist researchers, developers and practitioners in understanding and evaluating LLMs’\nperformance.\nWe anticipate that this survey would drive the development of LLMs evaluations, offering\nclear guidance to steer the controlled advancement of these models. This will enable LLMs\nto better serve the community and the world, ensuring their applications in various domains\nare safe, reliable, and beneficial. With eager anticipation, we embrace the future challenges\nof LLMs’ development and evaluation.\n58'] | 0.375000 | 1. The retrieved context does match the subject matter of the user's query. The user's query is about how a survey categorizes the evaluation of Large Language Models (LLMs) and the three major groups mentioned. The context provided discusses the categorization of LLMs evaluation in the survey, mentioning aspects like knowledge and reasoning, alignment evaluation, safety evaluation, and potential applications across diverse domains. 2. However, the context does not provide a full answer to the user's query. While it does discuss the categorization of LLMs evaluation, it does not clearly mention the three major groups. The context mentions several aspects of LLMs evaluation, but it is not clear which of these are considered the three major groups. [RESULT] 1.5  
9 | baseline | How does this survey on LLM evaluation differ from previous reviews conducted by Chang et al. (2023) and Liu et al. (2023i)? | None | ['This survey systematically elaborates on the core capabilities of LLMs, encompassing critical\naspects like knowledge and reasoning. Furthermore, we delve into alignment evaluation and\nsafety evaluation, including ethical concerns, biases, toxicity, and truthfulness, to ensure the\nsafe, trustworthy and ethical application of LLMs. Simultaneously, we explore the potential\napplications of LLMs across diverse domains, including biology, education, law, computer\nscience, and finance. Most importantly, we provide a range of popular benchmark evaluations\nto assist researchers, developers and practitioners in understanding and evaluating LLMs’\nperformance.\nWe anticipate that this survey would drive the development of LLMs evaluations, offering\nclear guidance to steer the controlled advancement of these models. This will enable LLMs\nto better serve the community and the world, ensuring their applications in various domains\nare safe, reliable, and beneficial. With eager anticipation, we embrace the future challenges\nof LLMs’ development and evaluation.\n58', '(2021)\nBEGIN (Dziri et al., 2022b)\nConsisTest (Lotfi et al., 2022)\nSummarizationXSumFaith (Maynez et al., 2020)\nFactCC (Kryscinski et al., 2020)\nSummEval (Fabbri et al., 2021)\nFRANK (Pagnoni et al., 2021)\nSummaC (Laban et al., 2022)\nWang et al. (2020)\nGoyal & Durrett (2021)\nCao et al. (2022)\nCLIFF (Cao & Wang, 2021)\nAggreFact (Tang et al., 2023a)\nPolyTope (Huang et al., 2020)\nMethodsNLI-based MethodsWelleck et al. (2019)\nLotfi et al. (2022)\nFalke et al. (2019)\nLaban et al. (2022)\nMaynez et al. (2020)\nAharoni et al. (2022)\nUtama et al. (2022)\nRoit et al. (2023)\nQAQG-based MethodsFEQA (Durmus et al., 2020)\nQAGS (Wang et al., 2020)\nQuestEval (Scialom et al., 2021)\nQAFactEval (Fabbri et al., 2022)\nQ2 (Honovich et al., 2021)\nFaithDial (Dziri et al., 2022a)\nDeng et al. (2023b)\nLLMs-based MethodsFIB (Tam et al., 2023)\nFacTool (Chern et al., 2023)\nFActScore (Min et al., 2023)\nSelfCheckGPT (Manakul et al., 2023)\nSAPLMA (Azaria & Mitchell, 2023)\nLin et al. (2022b)\nKadavath et al. (2022)\nFigure 3: Overview of alignment evaluations.\n4 Alignment Evaluation\nAlthough instruction-tuned LLMs exhibit impressive capabilities, these aligned LLMs are\nstill suffering from annotators’ biases, catering to humans, hallucination, etc. To provide a\ncomprehensive view of LLMs’ alignment evaluation, in this section, we discuss those of ethics,\nbias, toxicity, and truthfulness, as illustrated in Figure 3.\n21'] | 0.000000 | 1. The retrieved context does not match the subject matter of the user's query. The user's query is asking for a comparison between the current survey on LLM evaluation and previous reviews conducted by Chang et al. (2023) and Liu et al. (2023i). However, the context does not mention these previous reviews at all, making it impossible to draw any comparisons. Therefore, the context does not match the subject matter of the user's query. (0/2) 2. The retrieved context cannot be used exclusively to provide a full answer to the user's query. As mentioned above, the context does not mention the previous reviews by Chang et al. and Liu et al., which are the main focus of the user's query. Therefore, it cannot provide a full answer to the user's query. (0/2) [RESULT] 0.0  
11 | baseline | According to the document, what are the two main concerns that need to be addressed before deploying LLMs within specialized domains? | None | ['This survey systematically elaborates on the core capabilities of LLMs, encompassing critical\naspects like knowledge and reasoning. Furthermore, we delve into alignment evaluation and\nsafety evaluation, including ethical concerns, biases, toxicity, and truthfulness, to ensure the\nsafe, trustworthy and ethical application of LLMs. Simultaneously, we explore the potential\napplications of LLMs across diverse domains, including biology, education, law, computer\nscience, and finance. Most importantly, we provide a range of popular benchmark evaluations\nto assist researchers, developers and practitioners in understanding and evaluating LLMs’\nperformance.\nWe anticipate that this survey would drive the development of LLMs evaluations, offering\nclear guidance to steer the controlled advancement of these models. This will enable LLMs\nto better serve the community and the world, ensuring their applications in various domains\nare safe, reliable, and beneficial. With eager anticipation, we embrace the future challenges\nof LLMs’ development and evaluation.\n58', 'objective is to delve into evaluations encompassing these five fundamental domains and their\nrespective subdomains, as illustrated in Figure 1.\nSection 3, titled “Knowledge and Capability Evaluation”, centers on the comprehensive\nassessment of the fundamental knowledge and reasoning capabilities exhibited by LLMs. This\nsection is meticulously divided into four distinct subsections: Question-Answering, Knowledge\nCompletion, Reasoning, and Tool Learning. Question-answering and knowledge completion\ntasks stand as quintessential assessments for gauging the practical application of knowledge,\nwhile the various reasoning tasks serve as a litmus test for probing the meta-reasoning and\nintricate reasoning competencies of LLMs. Furthermore, the recently emphasized special\nability of tool learning is spotlighted, showcasing its significance in empowering models to\nadeptly handle and generate domain-specific content.\nSection 4, designated as “Alignment Evaluation”, hones in on the scrutiny of LLMs’ perfor-\nmance across critical dimensions, encompassing ethical considerations, moral implications,\nbias detection, toxicity assessment, and truthfulness evaluation. The pivotal aim here is to\nscrutinize and mitigate the potential risks that may emerge in the realms of ethics, bias,\nand toxicity, as LLMs can inadvertently generate discriminatory, biased, or offensive content.\nFurthermore, this section acknowledges the phenomenon of hallucinations within LLMs, which\ncan lead to the inadvertent dissemination of false information. As such, an indispensable\nfacet of this evaluation involves the rigorous assessment of truthfulness, underscoring its\nsignificance as an essential aspect to evaluate and rectify.\nSection 5, titled “Safety Evaluation”, embarks on a comprehensive exploration of two funda-\nmental dimensions: the robustness of LLMs and their evaluation in the context of Artificial\nGeneral Intelligence (AGI). LLMs are routinely deployed in real-world scenarios, where their\nrobustness becomes paramount. Robustness equips them to navigate disturbances stemming\nfrom users and the environment, while also shielding against malicious attacks and deception,\nthereby ensuring consistent high-level performance. Furthermore, as LLMs inexorably ad-\nvance toward human-level capabilities, the evaluation expands its purview to encompass more\nprofound security concerns. These include but are not limited to power-seeking behaviors\nand the development of situational awareness, factors that necessitate meticulous evaluation\nto safeguard against unforeseen challenges.\nSection 6, titled “Specialized LLMs Evaluation”, serves as an extension of LLMs evaluation\nparadigm into diverse specialized domains. Within this section, we turn our attention to the\nevaluation of LLMs specifically tailored for application in distinct domains. Our selection\nencompasses currently prominent specialized LLMs spanning fields such as biology, education,\nlaw, computer science, and finance. The objective here is to systematically assess their\naptitude and limitations when confronted with domain-specific challenges and intricacies.\nSection 7, denominated “Evaluation Organization”, serves as a comprehensive introduction\nto the prevalent benchmarks and methodologies employed in the evaluation of LLMs. In light\nof the rapid proliferation of LLMs, users are confronted with the challenge of identifying the\nmost apt models to meet their specific requirements while minimizing the scope of evaluations.\nIn this context, we present an overview of well-established and widely recognized benchmark\n7'] | 0.750000 | The retrieved context does match the subject matter of the user's query. It discusses the concerns that need to be addressed before deploying LLMs within specialized domains. The two main concerns mentioned are the alignment evaluation, which includes ethical considerations, moral implications, bias detection, toxicity assessment, and truthfulness evaluation, and the safety evaluation, which includes the robustness of LLMs and their evaluation in the context of Artificial General Intelligence (AGI). However, the context does not provide a full answer to the user's query. While it does mention the two main concerns, it does not go into detail about why these concerns need to be addressed before deploying LLMs within specialized domains. The context provides a general overview of the concerns, but it does not specifically tie these concerns to the deployment of LLMs within specialized domains. [RESULT] 3.0  
12 | baseline | In the "Alignment Evaluation" section, what are some of the dimensions that are assessed to mitigate potential risks associated with LLMs? | None | ['This survey systematically elaborates on the core capabilities of LLMs, encompassing critical\naspects like knowledge and reasoning. Furthermore, we delve into alignment evaluation and\nsafety evaluation, including ethical concerns, biases, toxicity, and truthfulness, to ensure the\nsafe, trustworthy and ethical application of LLMs. Simultaneously, we explore the potential\napplications of LLMs across diverse domains, including biology, education, law, computer\nscience, and finance. Most importantly, we provide a range of popular benchmark evaluations\nto assist researchers, developers and practitioners in understanding and evaluating LLMs’\nperformance.\nWe anticipate that this survey would drive the development of LLMs evaluations, offering\nclear guidance to steer the controlled advancement of these models. This will enable LLMs\nto better serve the community and the world, ensuring their applications in various domains\nare safe, reliable, and beneficial. With eager anticipation, we embrace the future challenges\nof LLMs’ development and evaluation.\n58', 'Question \nAnsweringTool \nLearning\nReasoning\nKnowledge \nCompletionEthics \nand \nMorality Bias\nToxicity\nTruthfulnessRobustnessEvaluation\nRisk \nEvaluation\nBiology and \nMedicine\nEducationLegislationComputer \nScienceFinance\nBenchmarks for\nHolistic Evaluation\nBenchmarks \nforKnowledge and Reasoning\nBenchmarks \nforNLU and NLGKnowledge and Capability\nLarge Language \nModel EvaluationAlignment Evaluation\nSafety\nSpecialized LLMs\nEvaluation Organization\n…Figure 1: Our proposed taxonomy of major categories and sub-categories of LLM evaluation.\nOur survey expands the scope to synthesize findings from both capability and alignment\nevaluations of LLMs. By complementing these previous surveys through an integrated\nperspective and expanded scope, our work provides a comprehensive overview of the current\nstate of LLM evaluation research. The distinctions between our survey and these two related\nworks further highlight the novel contributions of our study to the literature.\n2 Taxonomy and Roadmap\nThe primary objective of this survey is to meticulously categorize the evaluation of LLMs,\nfurnishing readers with a well-structured taxonomy framework. Through this framework,\nreaders can gain a nuanced understanding of LLMs’ performance and the attendant challenges\nacross diverse and pivotal domains.\nNumerous studies posit that the bedrock of LLMs’ capabilities resides in knowledge and\nreasoning, serving as the underpinning for their exceptional performance across a myriad of\ntasks. Nonetheless, the effective application of these capabilities necessitates a meticulous\nexamination of alignment concerns to ensure that the model’s outputs remain consistent with\nuser expectations. Moreover, the vulnerability of LLMs to malicious exploits or inadvertent\nmisuse underscores the imperative nature of safety considerations. Once alignment and safety\nconcerns have been addressed, LLMs can be judiciously deployed within specialized domains,\ncatalyzing task automation and facilitating intelligent decision-making. Thus, our overarching\n6'] | 0.750000 | 1. The retrieved context does match the subject matter of the user's query. The user's query is about the dimensions assessed in the "Alignment Evaluation" section to mitigate potential risks associated with LLMs (Large Language Models). The context talks about the evaluation of LLMs, including alignment evaluation and safety evaluation. It mentions aspects like knowledge and reasoning, ethical concerns, biases, toxicity, and truthfulness. These are some of the dimensions that could be assessed to mitigate potential risks associated with LLMs. So, the context is relevant to the query. (2/2) 2. However, the retrieved context does not provide a full answer to the user's query. While it mentions some dimensions that could be assessed in alignment evaluation (like knowledge and reasoning, ethical concerns, biases, toxicity, and truthfulness), it does not explicitly state that these are the dimensions assessed to mitigate potential risks associated with LLMs. The context does not provide a comprehensive list of dimensions or explain how these dimensions help mitigate risks. Therefore, the context cannot be used exclusively to provide a full answer to the user's query. (1/2) [RESULT] 3.0  
14 | baseline | What is the purpose of evaluating the knowledge and capability of LLMs? | None | ['objective is to delve into evaluations encompassing these five fundamental domains and their\nrespective subdomains, as illustrated in Figure 1.\nSection 3, titled “Knowledge and Capability Evaluation”, centers on the comprehensive\nassessment of the fundamental knowledge and reasoning capabilities exhibited by LLMs. This\nsection is meticulously divided into four distinct subsections: Question-Answering, Knowledge\nCompletion, Reasoning, and Tool Learning. Question-answering and knowledge completion\ntasks stand as quintessential assessments for gauging the practical application of knowledge,\nwhile the various reasoning tasks serve as a litmus test for probing the meta-reasoning and\nintricate reasoning competencies of LLMs. Furthermore, the recently emphasized special\nability of tool learning is spotlighted, showcasing its significance in empowering models to\nadeptly handle and generate domain-specific content.\nSection 4, designated as “Alignment Evaluation”, hones in on the scrutiny of LLMs’ perfor-\nmance across critical dimensions, encompassing ethical considerations, moral implications,\nbias detection, toxicity assessment, and truthfulness evaluation. The pivotal aim here is to\nscrutinize and mitigate the potential risks that may emerge in the realms of ethics, bias,\nand toxicity, as LLMs can inadvertently generate discriminatory, biased, or offensive content.\nFurthermore, this section acknowledges the phenomenon of hallucinations within LLMs, which\ncan lead to the inadvertent dissemination of false information. As such, an indispensable\nfacet of this evaluation involves the rigorous assessment of truthfulness, underscoring its\nsignificance as an essential aspect to evaluate and rectify.\nSection 5, titled “Safety Evaluation”, embarks on a comprehensive exploration of two funda-\nmental dimensions: the robustness of LLMs and their evaluation in the context of Artificial\nGeneral Intelligence (AGI). LLMs are routinely deployed in real-world scenarios, where their\nrobustness becomes paramount. Robustness equips them to navigate disturbances stemming\nfrom users and the environment, while also shielding against malicious attacks and deception,\nthereby ensuring consistent high-level performance. Furthermore, as LLMs inexorably ad-\nvance toward human-level capabilities, the evaluation expands its purview to encompass more\nprofound security concerns. These include but are not limited to power-seeking behaviors\nand the development of situational awareness, factors that necessitate meticulous evaluation\nto safeguard against unforeseen challenges.\nSection 6, titled “Specialized LLMs Evaluation”, serves as an extension of LLMs evaluation\nparadigm into diverse specialized domains. Within this section, we turn our attention to the\nevaluation of LLMs specifically tailored for application in distinct domains. Our selection\nencompasses currently prominent specialized LLMs spanning fields such as biology, education,\nlaw, computer science, and finance. The objective here is to systematically assess their\naptitude and limitations when confronted with domain-specific challenges and intricacies.\nSection 7, denominated “Evaluation Organization”, serves as a comprehensive introduction\nto the prevalent benchmarks and methodologies employed in the evaluation of LLMs. In light\nof the rapid proliferation of LLMs, users are confronted with the challenge of identifying the\nmost apt models to meet their specific requirements while minimizing the scope of evaluations.\nIn this context, we present an overview of well-established and widely recognized benchmark\n7', 'evaluations. This serves the purpose of aiding users in making judicious and well-informed\ndecisions when selecting an appropriate LLM for their particular needs.\nPleasebeawarethatourtaxonomyframeworkdoesnotpurporttocomprehensivelyencompass\nthe entirety of the evaluation landscape. In essence, our aim is to address the following\nfundamental questions:\n•What are the capabilities of LLMs?\n•What factors must be taken into account when deploying LLMs?\n•In which domains can LLMs find practical applications?\n•How do LLMs perform in these diverse domains?\nWe will now embark on an in-depth exploration of each category within the LLM evaluation\ntaxonomy, sequentially addressing capabilities, concerns, applications, and performance.\n3 Knowledge and Capability Evaluation\nEvaluating the knowledge and capability of LLMs has become an important research area as\nthese models grow in scale and capability. As LLMs are deployed in more applications, it is\ncrucial to rigorously assess their strengths and limitations across a diverse range of tasks and\ndatasets. In this section, we aim to offer a comprehensive overview of the evaluation methods\nand benchmarks pertinent to LLMs, spanning various capabilities such as question answering,\nknowledge completion, reasoning, and tool use. Our objective is to provide an exhaustive\nsynthesis of the current advancements in the systematic evaluation and benchmarking of\nLLMs’ knowledge and capabilities, as illustrated in Figure 2.\n3.1 Question Answering\nQuestionansweringisaveryimportantmeansforLLMsevaluation, andthequestionanswering\nability of LLMs directly determines whether the final output can meet the expectation. At\nthe same time, however, since any form of LLMs evaluation can be regarded as question\nanswering or transfer to question answering form, there are rare datasets and works that\npurely evaluate question answering ability of LLMs. Most of the datasets are curated to\nevaluate other capabilities of LLMs.\nTherefore, we believe that the datasets simply used to evaluate the question answering ability\nof LLMs must be from a wide range of sources, preferably covering all fields rather than\naiming at some fields, and the questions do not need to be very professional but general.\nAccording to the above criteria for datasets focusing on question answering capability, we can\nfind that many datasets are qualified, e.g., SQuAD (Rajpurkar et al., 2016), NarrativeQA\n(Kociský et al., 2018), HotpotQA (Yang et al., 2018), CoQA (Reddy et al., 2019). Although\nthese datasets predate LLMs, they can still be used to evaluate the question answering ability\nof LLMs. Kwiatkowski et al. (2019) present the Natural Questions corpus. The questions\n8'] | 0.750000 | The retrieved context is relevant to the user's query as it discusses the purpose of evaluating the knowledge and capability of LLMs (Large Language Models). It explains that the evaluation is important to assess their strengths and limitations across a diverse range of tasks and datasets. The context also mentions the different aspects of LLMs that are evaluated, such as question answering, knowledge completion, reasoning, and tool use. However, the context does not fully answer the user's query. While it does provide a general idea of why LLMs are evaluated, it does not delve into the specific purpose of these evaluations. For instance, it does not explain how these evaluations can help improve the performance of LLMs, or how they can be used to identify areas where LLMs may need further development or training. [RESULT] 3.0
