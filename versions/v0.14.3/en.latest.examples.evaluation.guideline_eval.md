![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Guideline Evaluator¶
This notebook shows how to use `GuidelineEvaluator` to evaluate a question answer system given user specified guidelines.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
%pip install llama-index-llms-openai

```

%pip install llama-index-llms-openai
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.core.evaluation import GuidelineEvaluator
from llama_index.llms.openai import OpenAI

# Needed for running async functions in Jupyter Notebook
import nest_asyncio

nest_asyncio.apply()

```

from llama_index.core.evaluation import GuidelineEvaluator from llama_index.llms.openai import OpenAI # Needed for running async functions in Jupyter Notebook import nest_asyncio nest_asyncio.apply()
In [ ]:
Copied!
```
GUIDELINES = [
    "The response should fully answer the query.",
    "The response should avoid being vague or ambiguous.",
    (
        "The response should be specific and use statistics or numbers when"
        " possible."
    ),
]

```

GUIDELINES = [ "The response should fully answer the query.", "The response should avoid being vague or ambiguous.", ( "The response should be specific and use statistics or numbers when" " possible." ), ]
In [ ]:
Copied!
```
llm = OpenAI(model="gpt-4")

evaluators = [
    GuidelineEvaluator(llm=llm, guidelines=guideline)
    for guideline in GUIDELINES
]

```

llm = OpenAI(model="gpt-4") evaluators = [ GuidelineEvaluator(llm=llm, guidelines=guideline) for guideline in GUIDELINES ]
In [ ]:
Copied!
```
sample_data = {
    "query": "Tell me about global warming.",
    "contexts": [
        (
            "Global warming refers to the long-term increase in Earth's"
            " average surface temperature due to human activities such as the"
            " burning of fossil fuels and deforestation."
        ),
        (
            "It is a major environmental issue with consequences such as"
            " rising sea levels, extreme weather events, and disruptions to"
            " ecosystems."
        ),
        (
            "Efforts to combat global warming include reducing carbon"
            " emissions, transitioning to renewable energy sources, and"
            " promoting sustainable practices."
        ),
    ],
    "response": (
        "Global warming is a critical environmental issue caused by human"
        " activities that lead to a rise in Earth's temperature. It has"
        " various adverse effects on the planet."
    ),
}

```

sample_data = { "query": "Tell me about global warming.", "contexts": [ ( "Global warming refers to the long-term increase in Earth's" " average surface temperature due to human activities such as the" " burning of fossil fuels and deforestation." ), ( "It is a major environmental issue with consequences such as" " rising sea levels, extreme weather events, and disruptions to" " ecosystems." ), ( "Efforts to combat global warming include reducing carbon" " emissions, transitioning to renewable energy sources, and" " promoting sustainable practices." ), ], "response": ( "Global warming is a critical environmental issue caused by human" " activities that lead to a rise in Earth's temperature. It has" " various adverse effects on the planet." ), }
In [ ]:
Copied!
```
for guideline, evaluator in zip(GUIDELINES, evaluators):
    eval_result = evaluator.evaluate(
        query=sample_data["query"],
        contexts=sample_data["contexts"],
        response=sample_data["response"],
    )
    print("=====")
    print(f"Guideline: {guideline}")
    print(f"Pass: {eval_result.passing}")
    print(f"Feedback: {eval_result.feedback}")

```

for guideline, evaluator in zip(GUIDELINES, evaluators): eval_result = evaluator.evaluate( query=sample_data["query"], contexts=sample_data["contexts"], response=sample_data["response"], ) print("=====") print(f"Guideline: {guideline}") print(f"Pass: {eval_result.passing}") print(f"Feedback: {eval_result.feedback}")
```
=====
Guideline: The response should fully answer the query.
Pass: False
Feedback: The response does not fully answer the query. While it does provide a brief overview of global warming, it does not delve into the specifics of the causes, effects, or potential solutions to the problem. The response should be more detailed and comprehensive to fully answer the query.
=====
Guideline: The response should avoid being vague or ambiguous.
Pass: False
Feedback: The response is too vague and does not provide specific details about global warming. It should include more information about the causes, effects, and potential solutions to global warming.
=====
Guideline: The response should be specific and use statistics or numbers when possible.
Pass: False
Feedback: The response is too general and lacks specific details or statistics about global warming. It would be more informative if it included data such as the rate at which the Earth's temperature is rising, the main human activities contributing to global warming, or the specific adverse effects on the planet.

```

