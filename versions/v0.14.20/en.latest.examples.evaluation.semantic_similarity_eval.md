![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Embedding Similarity Evaluator¶
This notebook shows the `SemanticSimilarityEvaluator`, which evaluates the quality of a question answering system via semantic similarity.
Concretely, it calculates the similarity score between embeddings of the generated answer and the reference answer.
If you're opening this Notebook on colab, you will probably need to install LlamaIndex 🦙.
In [ ]:
Copied!
```
!pip install llama-index

```

!pip install llama-index
In [ ]:
Copied!
```
from llama_index.core.evaluation import SemanticSimilarityEvaluator

evaluator = SemanticSimilarityEvaluator()

```

from llama_index.core.evaluation import SemanticSimilarityEvaluator evaluator = SemanticSimilarityEvaluator()
In [ ]:
Copied!
```
# This evaluator only uses `response` and `reference`, passing in query does not influence the evaluation
# query = 'What is the color of the sky'

response = "The sky is typically blue"
reference = """The color of the sky can vary depending on several factors, including time of day, weather conditions, and location.

During the day, when the sun is in the sky, the sky often appears blue. 
This is because of a phenomenon called Rayleigh scattering, where molecules and particles in the Earth's atmosphere scatter sunlight in all directions, and blue light is scattered more than other colors because it travels as shorter, smaller waves. 
This is why we perceive the sky as blue on a clear day.
"""

result = await evaluator.aevaluate(
    response=response,
    reference=reference,
)

```

# This evaluator only uses `response` and `reference`, passing in query does not influence the evaluation # query = 'What is the color of the sky' response = "The sky is typically blue" reference = """The color of the sky can vary depending on several factors, including time of day, weather conditions, and location. During the day, when the sun is in the sky, the sky often appears blue. This is because of a phenomenon called Rayleigh scattering, where molecules and particles in the Earth's atmosphere scatter sunlight in all directions, and blue light is scattered more than other colors because it travels as shorter, smaller waves. This is why we perceive the sky as blue on a clear day. """ result = await evaluator.aevaluate( response=response, reference=reference, )
In [ ]:
Copied!
```
print("Score: ", result.score)
print("Passing: ", result.passing)  # default similarity threshold is 0.8

```

print("Score: ", result.score) print("Passing: ", result.passing) # default similarity threshold is 0.8
```
Score:  0.874911773340899
Passing:  True

```

In [ ]:
Copied!
```
response = "Sorry, I do not have sufficient context to answer this question."
reference = """The color of the sky can vary depending on several factors, including time of day, weather conditions, and location.

During the day, when the sun is in the sky, the sky often appears blue. 
This is because of a phenomenon called Rayleigh scattering, where molecules and particles in the Earth's atmosphere scatter sunlight in all directions, and blue light is scattered more than other colors because it travels as shorter, smaller waves. 
This is why we perceive the sky as blue on a clear day.
"""

result = await evaluator.aevaluate(
    response=response,
    reference=reference,
)

```

response = "Sorry, I do not have sufficient context to answer this question." reference = """The color of the sky can vary depending on several factors, including time of day, weather conditions, and location. During the day, when the sun is in the sky, the sky often appears blue. This is because of a phenomenon called Rayleigh scattering, where molecules and particles in the Earth's atmosphere scatter sunlight in all directions, and blue light is scattered more than other colors because it travels as shorter, smaller waves. This is why we perceive the sky as blue on a clear day. """ result = await evaluator.aevaluate( response=response, reference=reference, )
In [ ]:
Copied!
```
print("Score: ", result.score)
print("Passing: ", result.passing)  # default similarity threshold is 0.8

```

print("Score: ", result.score) print("Passing: ", result.passing) # default similarity threshold is 0.8
```
Score:  0.7221738929165528
Passing:  False

```

### Customization¶
In [ ]:
Copied!
```
from llama_index.core.evaluation import SemanticSimilarityEvaluator
from llama_index.core.embeddings import SimilarityMode, resolve_embed_model

embed_model = resolve_embed_model("local")
evaluator = SemanticSimilarityEvaluator(
    embed_model=embed_model,
    similarity_mode=SimilarityMode.DEFAULT,
    similarity_threshold=0.6,
)

```

from llama_index.core.evaluation import SemanticSimilarityEvaluator from llama_index.core.embeddings import SimilarityMode, resolve_embed_model embed_model = resolve_embed_model("local") evaluator = SemanticSimilarityEvaluator( embed_model=embed_model, similarity_mode=SimilarityMode.DEFAULT, similarity_threshold=0.6, )
In [ ]:
Copied!
```
response = "The sky is yellow."
reference = "The sky is blue."

result = await evaluator.aevaluate(
    response=response,
    reference=reference,
)

```

response = "The sky is yellow." reference = "The sky is blue." result = await evaluator.aevaluate( response=response, reference=reference, )
In [ ]:
Copied!
```
print("Score: ", result.score)
print("Passing: ", result.passing)

```

print("Score: ", result.score) print("Passing: ", result.passing)
```
Score:  0.9178505509625874
Passing:  True

```

We note here that a high score does not imply the answer is always correct.
Embedding similarity primarily captures the notion of "relevancy". Since both the response and reference discuss "the sky" and colors, they are semantically similar.
